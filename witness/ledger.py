"""Reading the workbook.

`SFO_BB_analog_x_computing_events_enriched.xlsx` is the ledger this agent is
the witness to.  Nothing here interprets it -- this module only turns the sheets
into objects, keeping the workbook's own distinctions intact: the analog is the
supplied developmental framework, the evidence bands stay separate, and a cell
that was empty stays empty rather than becoming a zero.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import openpyxl

from .errata import Erratum, apply_to_keys, apply_to_nodes, load_errata
from .graph import Graph, KeyRecord, parse_pairs

NODES_SHEET = "Nodes · Analog+ · Events"
KEYS_SHEET = "BB analog index"
EVENTS_SHEET = "Timeline events"
LEDGER_SHEET = "Ledger dated items"
ACW_SHEET = "Agentic Computing War"

DEFAULT_WORKBOOK = Path(__file__).resolve().parent.parent / "data" / (
    "SFO_BB_analog_x_computing_events_enriched.xlsx"
)


def _as_datetime(value: Any) -> datetime | None:
    """Coerce a cell into an aware UTC datetime, or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int:
    parsed = _as_float(value)
    return int(parsed) if parsed is not None else 0


def parse_tuples(cell: Any) -> list[tuple[str, ...]]:
    """Read one of the workbook's tuple-of-tuples cells back as data.

    The workbook documents the format in its Method sheet: a literal tuple of
    tuples, one record per line, empty where nothing attaches.
    """
    if cell is None:
        return []
    text = str(cell).strip()
    if not text or text == "—":
        return []
    try:
        value = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return []
    if isinstance(value, tuple) and value and not isinstance(value[0], tuple):
        # A single record that lost its trailing comma.
        return [tuple(str(part) for part in value)]
    if isinstance(value, (tuple, list)):
        return [
            tuple(str(part) for part in record)
            for record in value
            if isinstance(record, (tuple, list))
        ]
    return []


@dataclass
class DatedItem:
    """One dated piece of evidence already standing in the ledger."""

    item_id: str
    date: str
    offset: str
    kind: str
    description: str
    url: str | None = None

    @classmethod
    def from_tuple(cls, record: tuple[str, ...]) -> "DatedItem":
        padded = list(record) + [""] * (6 - len(record))
        return cls(
            item_id=padded[0],
            date=padded[1],
            offset=padded[2],
            kind=padded[3],
            description=padded[4],
            url=padded[5] or None,
        )


@dataclass
class Node:
    """One SFO-BB node: a position, a date, and what the corpus says stands there."""

    node_id: str
    section: str
    position: float | None
    tnldy: int | None
    timestamp: datetime | None
    date: datetime | None
    analog: str | None
    analog_fallback: list[tuple[str, ...]]
    strands: int
    analog_key: float | None
    successors: list[tuple[float, float]]
    evidence_status: str | None
    chapter: list[tuple[str, ...]] = field(default_factory=list)
    parable_gloss: list[tuple[str, ...]] = field(default_factory=list)
    within_7d: list[DatedItem] = field(default_factory=list)
    context_8_30d: list[DatedItem] = field(default_factory=list)
    acw: list[tuple[str, ...]] = field(default_factory=list)
    exact_events: list[tuple[str, ...]] = field(default_factory=list)
    month_events: list[tuple[str, ...]] = field(default_factory=list)
    year_events: list[tuple[str, ...]] = field(default_factory=list)

    @property
    def iso_date(self) -> str:
        return self.date.date().isoformat() if self.date else ""

    @property
    def chapter_title(self) -> str:
        return self.chapter[0][0] if self.chapter and self.chapter[0] else ""

    @property
    def chapter_reading(self) -> str:
        if self.chapter and len(self.chapter[0]) >= 4:
            return self.chapter[0][3]
        return ""

    @property
    def analog_is_fallback(self) -> bool:
        """True when this key carries no attribute text of its own."""
        return not self.analog and bool(self.analog_fallback)

    @property
    def analog_text(self) -> str:
        """What the developmental framework says stands at this position.

        Some BB keys carry no attribute text at all.  Where that is so, the
        workbook names the last preceding key that does, with its distance in
        position -- the analog standing at this moment rather than one assigned
        to it.  That distinction is kept visible here rather than smoothed away.
        """
        if self.analog:
            return str(self.analog)
        if self.analog_fallback:
            record = list(self.analog_fallback[0]) + [""] * 4
            key, date, distance, text = record[0], record[1], record[2], record[3]
            return (
                f"{text} — carried over from key {key}"
                f"{f' ({date})' if date else ''}"
                f"{f', {distance}' if distance else ''}; this key carries no text of its own"
            )
        return "(no analog text on this key)"

    def is_future(self, now: datetime) -> bool:
        return bool(self.date and self.date.date() > now.date())

    def has_exact_event(self) -> bool:
        return bool(self.exact_events)

    def evidence_count(self) -> int:
        return len(self.within_7d) + len(self.context_8_30d) + len(self.exact_events)

    @property
    def successor_dates(self) -> list[tuple[float, float, str]]:
        """Each successor key with its gap and the date that gap lands on."""
        from .axis import position_to_timestamp

        return [
            (key, gap, position_to_timestamp(key).date().isoformat())
            for key, gap in self.successors
        ]


@dataclass
class TimelineEvent:
    """One entry from the computing timeline, as the workbook resolved it."""

    event_id: str
    source_article: str
    date_as_given: str
    given_precision: str
    pinpointed_date: str
    resolved_to: str
    basis: str
    event: str
    notes: str | None


def _header_index(header_row: Iterable[Any]) -> dict[str, int]:
    return {str(name).strip(): i for i, name in enumerate(header_row) if name}


def load_nodes(workbook_path: Path | str = DEFAULT_WORKBOOK) -> list[Node]:
    """Load the 265 nodes with their analog, enrichment and matched events."""
    wb = openpyxl.load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        ws = wb[NODES_SHEET]
        rows = ws.iter_rows(values_only=True)
        index = _header_index(next(rows))

        def cell(row: tuple[Any, ...], name: str) -> Any:
            position = index.get(name)
            return row[position] if position is not None and position < len(row) else None

        nodes: list[Node] = []
        for row in rows:
            if not row or not row[0]:
                continue
            nodes.append(
                Node(
                    node_id=str(cell(row, "Node ID")),
                    section=str(cell(row, "Section") or ""),
                    position=_as_float(cell(row, "Position")),
                    tnldy=_as_int(cell(row, "TNLDY")) or None,
                    timestamp=_as_datetime(cell(row, "Timestamp (UTC)")),
                    date=_as_datetime(cell(row, "Node UTC date")),
                    analog=cell(row, "Stated analog — design-story context"),
                    analog_fallback=parse_tuples(
                        cell(row, "Analog fallback — last BB key carrying text (tuple)")
                    ),
                    strands=_as_int(cell(row, "Strands")),
                    analog_key=_as_float(cell(row, "Analog BB key")),
                    # The successors belong to the BB key this node's analog is
                    # carried by, not to the node: the graph lives on the 399
                    # keys, and 265 nodes draw on them.
                    successors=parse_pairs(cell(row, "BB successors (key, gap)")),
                    evidence_status=cell(row, "Ledger evidence status"),
                    chapter=parse_tuples(
                        cell(row, "Design-story chapter (parable §, span, reading)")
                    ),
                    parable_gloss=parse_tuples(
                        cell(row, "Parable position gloss (tuple)")
                    ),
                    within_7d=[
                        DatedItem.from_tuple(t)
                        for t in parse_tuples(
                            cell(row, "Ledger — same day / within 7 days (tuple)")
                        )
                    ],
                    context_8_30d=[
                        DatedItem.from_tuple(t)
                        for t in parse_tuples(
                            cell(row, "Ledger — wider context 8–30 days (tuple)")
                        )
                    ],
                    acw=parse_tuples(cell(row, "Agentic Computing War — PDF (tuple)")),
                    exact_events=parse_tuples(
                        cell(row, "Corresponding events — exact date (tuple)")
                    ),
                    month_events=parse_tuples(cell(row, "Same-month events (tuple)")),
                    year_events=parse_tuples(cell(row, "Same-year events (tuple)")),
                )
            )
        apply_to_nodes(nodes, load_errata())
        return nodes
    finally:
        wb.close()


def load_events(workbook_path: Path | str = DEFAULT_WORKBOOK) -> list[TimelineEvent]:
    """Load the timeline of computing events the workbook matched against."""
    wb = openpyxl.load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        ws = wb[EVENTS_SHEET]
        rows = ws.iter_rows(values_only=True)
        index = _header_index(next(rows))

        def cell(row: tuple[Any, ...], name: str) -> Any:
            position = index.get(name)
            return row[position] if position is not None and position < len(row) else None

        events: list[TimelineEvent] = []
        for row in rows:
            if not row or not row[0]:
                continue
            events.append(
                TimelineEvent(
                    event_id=str(cell(row, "Event ID")),
                    source_article=str(cell(row, "Source article") or ""),
                    date_as_given=str(cell(row, "Date as given") or ""),
                    given_precision=str(cell(row, "Given precision") or ""),
                    pinpointed_date=str(cell(row, "Pinpointed date") or ""),
                    resolved_to=str(cell(row, "Resolved to") or ""),
                    basis=str(cell(row, "Basis") or ""),
                    event=str(cell(row, "Event (from timeline)") or ""),
                    notes=cell(row, "Notes / corrections"),
                )
            )
        return events
    finally:
        wb.close()


def upcoming(nodes: list[Node], now: datetime, horizon_days: int) -> list[Node]:
    """Nodes whose dates fall from today out to the horizon."""
    return sorted(
        (
            node
            for node in nodes
            if node.date
            and 0 <= (node.date.date() - now.date()).days <= horizon_days
        ),
        key=lambda n: n.date,
    )


def recently_passed(nodes: list[Node], now: datetime, lookback_days: int) -> list[Node]:
    """Nodes whose dates have just gone by, and so can now be witnessed."""
    return sorted(
        (
            node
            for node in nodes
            if node.date
            and 0 < (now.date() - node.date.date()).days <= lookback_days
        ),
        key=lambda n: n.date,
        reverse=True,
    )


def nodes_by_date(nodes: list[Node]) -> dict[str, list[Node]]:
    """Index nodes by ISO date, for mapping a real event back onto the ledger."""
    index: dict[str, list[Node]] = {}
    for node in nodes:
        if node.date:
            index.setdefault(node.iso_date, []).append(node)
    return index


def load_keys(workbook_path: Path | str = DEFAULT_WORKBOOK) -> list[KeyRecord]:
    """Load all 399 BB keys -- the vertices the successor graph runs over."""
    wb = openpyxl.load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        ws = wb[KEYS_SHEET]
        rows = ws.iter_rows(values_only=True)
        index = _header_index(next(rows))

        def cell(row: tuple[Any, ...], name: str) -> Any:
            position = index.get(name)
            return row[position] if position is not None and position < len(row) else None

        records: list[KeyRecord] = []
        for row in rows:
            if not row or row[index.get("SFO_BB_key", 1)] is None:
                continue
            key = _as_float(cell(row, "SFO_BB_key"))
            if key is None:
                continue
            carried = str(cell(row, "Carried by nodes") or "").strip()
            records.append(
                KeyRecord(
                    key=key,
                    date=str(cell(row, "BB UTC date") or "")[:10],
                    analog=str(cell(row, "Stated analog — design-story context") or ""),
                    chapter=str(cell(row, "Design-story chapter (ledger)") or ""),
                    evidence_status=str(cell(row, "Ledger evidence status") or ""),
                    carried_by=[c.strip() for c in carried.split(",") if c.strip()],
                    successors=parse_pairs(cell(row, "Successors (key, gap)")),
                )
            )
        apply_to_keys(records, load_errata())
        return records
    finally:
        wb.close()


def load_graph(
    workbook_path: Path | str = DEFAULT_WORKBOOK, imply_backbone: bool = True
) -> Graph:
    """The successor relation over the keys, with declared errata applied.

    ``imply_backbone=False`` gives the graph exactly as the workbook states it,
    without the edges the default predecessor rule implies.
    """
    return Graph(load_keys(workbook_path), imply_backbone=imply_backbone)


def applied_errata() -> list[Erratum]:
    """The corrections in force, for anything that reports on the ledger."""
    return [e for e in load_errata() if e.applied]
