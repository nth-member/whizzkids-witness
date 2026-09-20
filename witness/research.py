"""The Claude layer: search the world, then structure what came back.

Two phases on purpose.

  Phase one  searches with the server-side web_search tool and produces prose
             with citations.  The raw text is kept on disk as the working note
             behind every finding, so a claim can always be traced back.
  Phase two  converts that note into validated records with no tools and no
             search, which keeps the extraction from quietly inventing an event
             that the search never actually found.

Splitting them also avoids mixing search citations with a constrained output
format in a single request.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .ledger import Node
from .prompts import DISCIPLINE, EXTRACTION_INSTRUCTION, feed_task, research_task

from .constants import MODEL, SEARCH_TOOL
RAW_DIR = Path(__file__).resolve().parent.parent / "runs" / "raw"


class RawFinding(BaseModel):
    """One sourced event, as the extraction phase returns it."""

    event_title: str = Field(description="Short title for what happened")
    event_date: str = Field(description="ISO date: YYYY-MM-DD, YYYY-MM or YYYY")
    date_precision: Literal["day", "month", "year"]
    what_happened: str = Field(description="Two or three sentences, factual")
    why_it_matters: str = Field(description="Why this event mattered in computing")
    source_url: str
    source_name: str
    confidence: Literal["stated", "reported", "recalled — verify"]
    caution: str = Field(
        description="What would make this correspondence weak, or 'none noted'"
    )


class FindingSet(BaseModel):
    summary: str = Field(description="One paragraph on what the search established")
    quiet: bool = Field(description="True if the days held nothing worth recording")
    findings: list[RawFinding]


@dataclass
class ResearchResult:
    node_id: str
    raw_text: str
    findings: FindingSet
    raw_path: Path | None
    searched: int


class DryRunClient:
    """Stands in for the API so a run can be inspected before it costs anything."""

    dry = True

    def research(self, task: str, label: str) -> tuple[str, int]:
        return (
            "[dry run] no search performed.\n\n--- task given to the model ---\n"
            + task,
            0,
        )

    def extract(self, raw_text: str, label: str) -> FindingSet:
        return FindingSet(
            summary="[dry run] nothing extracted; no API call was made.",
            quiet=True,
            findings=[],
        )


class WitnessClient:
    """Wraps the Messages API for the two phases."""

    def __init__(self, model: str = MODEL, effort: str = "high", max_uses: int = 8):
        import anthropic  # imported here so --dry-run works without the SDK

        self.anthropic = anthropic
        self.client = anthropic.Anthropic()
        self.model = model
        self.effort = effort
        self.search_tool = {**SEARCH_TOOL, "max_uses": max_uses}

    def research(self, task: str, label: str) -> tuple[str, int]:
        """Phase one: search the world.  Streamed -- search turns run long."""
        searched = 0
        with self.client.messages.stream(
            model=self.model,
            max_tokens=32000,
            system=[{"type": "text", "text": DISCIPLINE, "cache_control": {"type": "ephemeral"}}],
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            tools=[self.search_tool],
            messages=[{"role": "user", "content": task}],
        ) as stream:
            message = stream.get_final_message()

        if message.stop_reason == "refusal":
            detail = getattr(message, "stop_details", None)
            raise RuntimeError(
                f"{label}: the model declined this request "
                f"({getattr(detail, 'category', 'unknown')})"
            )

        chunks: list[str] = []
        for block in message.content:
            if block.type == "text":
                chunks.append(block.text)
            elif block.type == "web_search_tool_result":
                # An error arrives as an object, a success as a list of results.
                content = getattr(block, "content", None)
                if isinstance(content, list):
                    searched += len(content)
        return "\n".join(chunks).strip(), searched

    def extract(self, raw_text: str, label: str) -> FindingSet:
        """Phase two: structure the note.  No tools, no search, no invention."""
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=16000,
            system=DISCIPLINE,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            messages=[
                {
                    "role": "user",
                    "content": f"{EXTRACTION_INSTRUCTION}\n\n--- research notes ---\n{raw_text}",
                }
            ],
            output_format=FindingSet,
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(f"{label}: the model declined to structure these notes")
        return response.parsed_output


def _write_raw(label: str, text: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RAW_DIR / f"{label}-{stamp}.md"
    path.write_text(text, encoding="utf-8")
    return path


def research_node(client, node: Node, today: str, keep_raw: bool = True) -> ResearchResult:
    """Search around one node's date, then structure what came back."""
    task = research_task(node, today)
    raw_text, searched = client.research(task, node.node_id)
    raw_path = _write_raw(node.node_id, raw_text) if keep_raw and raw_text else None
    findings = client.extract(raw_text, node.node_id)
    return ResearchResult(
        node_id=node.node_id,
        raw_text=raw_text,
        findings=findings,
        raw_path=raw_path,
        searched=searched,
    )


def research_feed(client, since: str, today: str, keep_raw: bool = True) -> ResearchResult:
    """Search the recent world with no node in hand.  Real world first."""
    task = feed_task(since, today)
    raw_text, searched = client.research(task, "feed")
    raw_path = _write_raw("feed", raw_text) if keep_raw and raw_text else None
    findings = client.extract(raw_text, "feed")
    return ResearchResult(
        node_id="—",
        raw_text=raw_text,
        findings=findings,
        raw_path=raw_path,
        searched=searched,
    )
