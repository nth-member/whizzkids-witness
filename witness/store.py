"""The append-only findings store.

Every finding the agent makes is written once, as a line of JSON, and never
rewritten.  That is deliberate: a ledger whose past entries can be edited by the
thing that watches it is not evidence of anything.  Findings carry the run that
produced them and the model that wrote them, so a later reader can tell which
claims came from a machine and when.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_STORE = Path(__file__).resolve().parent.parent / "findings" / "findings.jsonl"


@dataclass
class Finding:
    """One real-world event, placed against one node, in one band."""

    node_id: str
    node_position: float | None
    node_date: str
    mode: str

    event_title: str
    event_date: str
    date_precision: str          # day | month | year
    offset_days: int | None
    band: str                    # exact | within_7d | context_8_30d | outside
    what_happened: str
    why_it_matters: str
    source_url: str
    source_name: str
    confidence: str              # stated | reported | recalled — verify
    caution: str

    analog_at_node: str = ""
    chapter: str = ""
    run_id: str = ""
    model: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finding_id: str = ""

    def __post_init__(self) -> None:
        if not self.finding_id:
            self.finding_id = self.compute_id()

    def compute_id(self) -> str:
        """Identity is node + event date + source, so the same claim never doubles."""
        seed = f"{self.node_id}|{self.event_date}|{self.source_url}|{self.event_title}"
        return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class FindingStore:
    def __init__(self, path: Path | str = DEFAULT_STORE) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def all(self) -> list[Finding]:
        if not self.path.exists():
            return []
        findings: list[Finding] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                findings.append(Finding(**json.loads(line)))
            except (json.JSONDecodeError, TypeError):
                continue
        return findings

    def known_ids(self) -> set[str]:
        return {f.finding_id for f in self.all()}

    def witnessed_nodes(self) -> set[str]:
        return {f.node_id for f in self.all()}

    def for_node(self, node_id: str) -> list[Finding]:
        return [f for f in self.all() if f.node_id == node_id]

    def append(self, findings: list[Finding]) -> list[Finding]:
        """Append findings that are not already on file.  Returns what was new."""
        seen = self.known_ids()
        fresh = []
        for finding in findings:
            if finding.finding_id in seen:
                continue
            seen.add(finding.finding_id)
            fresh.append(finding)
        if fresh:
            with self.path.open("a", encoding="utf-8") as handle:
                for finding in fresh:
                    handle.write(finding.to_json() + "\n")
        return fresh


@dataclass
class RunRecord:
    """One run of the witness, kept so a report can say when it last looked."""

    run_id: str
    mode: str
    started_at: str
    model: str
    nodes_examined: list[str]
    findings_new: int
    findings_total: int
    notes: str = ""

    @staticmethod
    def new_id(mode: str) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{mode}-{stamp}"


class RunLog:
    def __init__(self, path: Path | str | None = None) -> None:
        base = Path(__file__).resolve().parent.parent / "findings" / "runs.jsonl"
        self.path = Path(path) if path else base
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: RunRecord) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    def all(self) -> list[RunRecord]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    records.append(RunRecord(**json.loads(line)))
                except (json.JSONDecodeError, TypeError):
                    continue
        return records

    def last(self, mode: str | None = None) -> RunRecord | None:
        records = [r for r in self.all() if mode is None or r.mode == mode]
        return records[-1] if records else None
