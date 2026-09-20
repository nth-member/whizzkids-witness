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
INTERVAL_STORE = Path(__file__).resolve().parent.parent / "findings" / "intervals.jsonl"


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

    source_tier: str = ""
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


@dataclass
class IntervalFinding:
    """One development placed against one edge, judged end by end."""

    edge_source: float
    edge_target: float
    opens: str
    closes: str
    span_days: int
    stated_gap: float
    gap_agrees: bool
    edge_stated: bool
    edge_default: bool

    development: str
    shape: str                      # both_ends | one_end | span_only | neither
    what_happened: str

    open_event: str = ""
    open_date: str = ""
    open_offset_days: int | None = None
    open_band: str = ""
    open_url: str = ""
    open_source_tier: str = ""

    close_event: str = ""
    close_date: str = ""
    close_offset_days: int | None = None
    close_band: str = ""
    close_url: str = ""
    close_source_tier: str = ""

    confidence: str = ""
    caution: str = ""
    run_id: str = ""
    model: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finding_id: str = ""

    def __post_init__(self) -> None:
        if not self.finding_id:
            seed = (f"{self.edge_source}|{self.edge_target}|{self.development}"
                    f"|{self.open_date}|{self.close_date}")
            self.finding_id = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]

    @property
    def edge(self) -> str:
        return f"{self.edge_source} → {self.edge_target}"

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class IntervalStore:
    """Append-only, like the node findings, and kept in its own file.

    An interval claim has a different shape from a dated correspondence and is
    not mixed in with them.
    """

    def __init__(self, path: Path | str = INTERVAL_STORE) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def all(self) -> list[IntervalFinding]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    out.append(IntervalFinding(**json.loads(line)))
                except (json.JSONDecodeError, TypeError):
                    continue
        return out

    def witnessed_edges(self) -> set[tuple[float, float]]:
        return {(f.edge_source, f.edge_target) for f in self.all()}

    def append(self, findings: list[IntervalFinding]) -> list[IntervalFinding]:
        seen = {f.finding_id for f in self.all()}
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
