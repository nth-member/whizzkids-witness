"""Taking research in by hand.

The two research phases do not have to be done by the agent.  The prompts are
just text: they can be run in any Claude session, and the answer brought back
here.  This module is that path, and it exists so the ledger can be worked
without an API key at all.

What it does not do is relax anything.  The bands are still computed in code
from two dates, the source tier is still judged from the URL, the store is still
append-only, and the record says plainly that the finding arrived this way --
``mode: ingest`` -- rather than from a run the agent made itself.

It deliberately imports nothing from the API layer, so it works on a machine
with neither credentials nor the anthropic package installed.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .axis import band_for, offset_days
from .decoy import shift_node
from .graph import Edge
from .ledger import Node, load_graph, load_nodes
from .sources import tier_for
from .store import Finding, FindingStore, IntervalFinding, IntervalStore, RunLog, RunRecord

PRECISIONS = {"day", "month", "year"}
CONFIDENCES = {"stated", "reported", "recalled — verify", "recalled - verify"}
SHAPES = {"both_ends", "one_end", "span_only", "neither"}

REQUIRED_FINDING = (
    "event_title", "event_date", "date_precision", "what_happened",
    "why_it_matters", "source_url", "source_name", "confidence", "caution",
)
REQUIRED_INTERVAL = ("development", "shape", "what_happened", "confidence", "caution")


class IngestError(ValueError):
    """Raised when the supplied records cannot be trusted as they stand."""


def _parse_date(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _check(record: dict[str, Any], required: tuple[str, ...], index: int) -> None:
    missing = [field for field in required if not str(record.get(field, "")).strip()]
    if missing:
        raise IngestError(f"record {index}: missing {', '.join(missing)}")


def read_records(path: Path | str) -> list[dict[str, Any]]:
    """Read a JSON file holding a list of records, or an object wrapping one."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("findings", [])
    if not isinstance(data, list):
        raise IngestError("expected a JSON list of records, or an object with 'findings'")
    return data


def ingest_node(
    node_id: str,
    records: list[dict[str, Any]],
    model: str,
    note: str = "",
    workbook=None,
    store: FindingStore | None = None,
    decoy: int | None = None,
) -> list[Finding]:
    """Take findings for one node, judging every band and tier here."""
    nodes = {n.node_id: n for n in (load_nodes(workbook) if workbook else load_nodes())}
    node: Node | None = nodes.get(node_id)
    if node is None:
        raise IngestError(f"no such node: {node_id}")

    if decoy:
        node = shift_node(node, decoy)

    store = store or FindingStore()
    run_id = RunRecord.new_id("decoy" if decoy else "ingest")
    prepared: list[Finding] = []

    for index, record in enumerate(records):
        _check(record, REQUIRED_FINDING, index)
        precision = str(record["date_precision"]).strip()
        if precision not in PRECISIONS:
            raise IngestError(f"record {index}: date_precision must be day, month or year")
        if str(record["confidence"]).strip() not in CONFIDENCES:
            raise IngestError(
                f"record {index}: confidence must be stated, reported, or 'recalled — verify'"
            )
        event_date = _parse_date(str(record["event_date"]))
        if event_date is None:
            raise IngestError(f"record {index}: event_date is not an ISO date")
        if precision == "day" and node.date:
            offset = offset_days(node.date, event_date)
            band = band_for(offset)
        else:
            offset, band = None, f"{precision}-precision"

        prepared.append(
            Finding(
                node_id=node.node_id,
                node_position=node.position,
                node_date=node.iso_date,
                mode="decoy" if decoy else "ingest",
                event_title=str(record["event_title"]),
                event_date=str(record["event_date"]),
                date_precision=precision,
                offset_days=offset,
                band=band,
                what_happened=str(record["what_happened"]),
                why_it_matters=str(record["why_it_matters"]),
                source_url=str(record["source_url"]),
                source_name=str(record["source_name"]),
                confidence=str(record["confidence"]).replace(" - ", " — "),
                caution=str(record["caution"]),
                source_tier=tier_for(str(record["source_url"])),
                decoy_offset=decoy,
                analog_at_node=node.analog_text,
                chapter=node.chapter_title,
                run_id=run_id,
                model=model,
            )
        )

    fresh = store.append(prepared)
    RunLog().append(
        RunRecord(
            run_id=run_id, mode="decoy" if decoy else "ingest",
            started_at=datetime.now(timezone.utc).isoformat(),
            model=model, nodes_examined=[node.node_id], findings_new=len(fresh),
            findings_total=len(store.all()), notes=note,
        )
    )
    return fresh


def ingest_interval(
    source: float,
    target: float,
    records: list[dict[str, Any]],
    model: str,
    note: str = "",
    workbook=None,
    store: IntervalStore | None = None,
) -> list[IntervalFinding]:
    """Take findings for one edge, judging each end here."""
    graph = load_graph(workbook) if workbook else load_graph()
    edge: Edge | None = next(
        (
            e
            for e in graph.out.get(source, [])
            if abs(e.target - target) < 1e-9
        ),
        None,
    )
    if edge is None:
        raise IngestError(f"no such edge: {source} → {target}")

    store = store or IntervalStore()
    run_id = RunRecord.new_id("ingest")
    prepared: list[IntervalFinding] = []

    for index, record in enumerate(records):
        _check(record, REQUIRED_INTERVAL, index)
        if str(record["shape"]).strip() not in SHAPES:
            raise IngestError(f"record {index}: shape must be one of {sorted(SHAPES)}")
        open_date = _parse_date(str(record.get("open_date", "")))
        close_date = _parse_date(str(record.get("close_date", "")))
        open_offset = offset_days(edge.source_date, open_date) if open_date else None
        close_offset = offset_days(edge.target_date, close_date) if close_date else None

        prepared.append(
            IntervalFinding(
                edge_source=edge.source, edge_target=edge.target,
                opens=edge.source_date.date().isoformat(),
                closes=edge.target_date.date().isoformat(),
                span_days=int(abs(edge.implied_days)), stated_gap=edge.stated_gap,
                gap_agrees=edge.gap_agrees, edge_stated=edge.stated, edge_default=edge.default,
                development=str(record["development"]), shape=str(record["shape"]),
                what_happened=str(record["what_happened"]),
                open_event=str(record.get("open_event", "")),
                open_date=str(record.get("open_date", "")),
                open_offset_days=open_offset,
                open_band=band_for(open_offset) if open_offset is not None else "",
                open_url=str(record.get("open_url", "")),
                open_source_tier=tier_for(str(record.get("open_url", ""))) if record.get("open_url") else "",
                close_event=str(record.get("close_event", "")),
                close_date=str(record.get("close_date", "")),
                close_offset_days=close_offset,
                close_band=band_for(close_offset) if close_offset is not None else "",
                close_url=str(record.get("close_url", "")),
                close_source_tier=tier_for(str(record.get("close_url", ""))) if record.get("close_url") else "",
                confidence=str(record["confidence"]).replace(" - ", " — "),
                caution=str(record["caution"]), run_id=run_id, model=model,
            )
        )

    fresh = store.append(prepared)
    RunLog().append(
        RunRecord(
            run_id=run_id, mode="ingest", started_at=datetime.now(timezone.utc).isoformat(),
            model=model, nodes_examined=[f"{source}→{target}"], findings_new=len(fresh),
            findings_total=len(store.all()), notes=note,
        )
    )
    return fresh
