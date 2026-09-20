"""The edge set.

The ledger is not only a sequence of dates.  Each of the 399 BB keys names its
successors, with a stated gap, and those 701 edges make a directed graph whose
single root is -147.6 (the Altair position, 1974-12-01) and whose single sink is
212.4.  Positions 0.00 -- the epoch itself -- fans out to eighteen successors,
the widest branching in the ledger.

Two things are preserved rather than corrected.

A stated gap and the difference between the two keys disagree on five edges.
The parable records exactly this and says so: it preserved them and flagged
them, because interpreting every weight as elapsed time would require
clarification of what the weight means.  So an edge here carries both numbers
and a flag, and nothing silently rewrites the stated gap.

One edge runs backwards: 0.18 names 0.0 as a successor, which is earlier.  It
creates no cycle -- 0.0 never reaches 0.18 -- but it is not smoothed away either.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable

from .axis import DAYS_PER_UNIT, position_to_timestamp

GAP_TOLERANCE = 0.005


def parse_pairs(cell) -> list[tuple[float, float]]:
    """Read a ``[(key, gap), ...]`` successor cell back as numbers."""
    if cell is None:
        return []
    text = str(cell).strip()
    if not text or text in {"[]", "—"}:
        return []
    try:
        value = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return []
    pairs: list[tuple[float, float]] = []
    for record in value if isinstance(value, (list, tuple)) else []:
        if isinstance(record, (list, tuple)) and len(record) >= 2:
            try:
                pairs.append((float(record[0]), float(record[1])))
            except (TypeError, ValueError):
                continue
    return pairs


@dataclass(frozen=True)
class Edge:
    """One successor relation, with both readings of its gap.

    ``stated`` is False for an edge the workbook does not list but the default
    predecessor rule implies: every key's default predecessor is the key
    standing temporally just before it, so consecutive positions are joined
    whether or not the source spells the edge out.  Derived edges are marked
    everywhere they appear and are never counted as something the ledger said.
    """

    source: float
    target: float
    stated_gap: float
    stated: bool = True

    @property
    def implied_gap(self) -> float:
        """The gap the two positions actually imply."""
        return round(self.target - self.source, 6)

    @property
    def gap_agrees(self) -> bool:
        return abs(self.implied_gap - self.stated_gap) <= GAP_TOLERANCE

    @property
    def backward(self) -> bool:
        """True where the named successor sits at or before its source."""
        return self.target <= self.source

    @property
    def stated_days(self) -> float:
        """The stated gap read as elapsed time -- which is the disputed reading."""
        return self.stated_gap * DAYS_PER_UNIT

    @property
    def implied_days(self) -> float:
        return self.implied_gap * DAYS_PER_UNIT

    @property
    def source_date(self) -> datetime:
        return position_to_timestamp(self.source)

    @property
    def target_date(self) -> datetime:
        return position_to_timestamp(self.target)

    def describe(self) -> str:
        arrow = f"{self.source} → {self.target}"
        if not self.stated:
            return (
                f"{arrow}  gap {self.stated_gap}  "
                f"{self.implied_days:,.0f} days "
                f"({self.source_date.date()} → {self.target_date.date()})  "
                f"[implied by the default predecessor rule]"
            )
        span = (
            f"{self.implied_days:,.0f} days "
            f"({self.source_date.date()} → {self.target_date.date()})"
        )
        if self.gap_agrees:
            return f"{arrow}  gap {self.stated_gap}  {span}"
        return (
            f"{arrow}  gap stated {self.stated_gap}, positions imply "
            f"{self.implied_gap}  {span}  [gap disputed]"
        )


@dataclass
class KeyRecord:
    """One of the 399 BB keys: where the graph's vertices actually live."""

    key: float
    date: str
    analog: str
    chapter: str
    evidence_status: str
    carried_by: list[str] = field(default_factory=list)
    successors: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class IntegrityReport:
    keys: int
    edges: int
    roots: list[float]
    sinks: list[float]
    cycles: list[list[float]]
    dangling: list[Edge]
    backward: list[Edge]
    gap_disputed: list[Edge]
    max_out: tuple[float, int]
    max_in: tuple[float, int]
    backbone: int
    long_range: int
    stated_edges: int
    derived_edges: int

    @property
    def acyclic(self) -> bool:
        return not self.cycles

    @property
    def closed(self) -> bool:
        """True when every named successor is itself a key in the ledger."""
        return not self.dangling


class Graph:
    """The successor relation over BB keys.

    With ``imply_backbone`` (the default), the graph also carries the edges the
    default predecessor rule implies: where two consecutive positions have no
    stated edge between them, one is derived, marked ``stated=False``, and its
    gap is the difference between the two keys.
    """

    def __init__(self, records: Iterable[KeyRecord], imply_backbone: bool = True):
        self.records: dict[float, KeyRecord] = {r.key: r for r in records}
        self.edges: list[Edge] = []
        self.out: dict[float, list[Edge]] = defaultdict(list)
        self.into: dict[float, list[Edge]] = defaultdict(list)
        for record in self.records.values():
            for target, gap in record.successors:
                self._add(Edge(record.key, target, gap))
        if imply_backbone:
            self._imply_backbone()

    def _add(self, edge: Edge) -> None:
        self.edges.append(edge)
        self.out[edge.source].append(edge)
        self.into[edge.target].append(edge)

    def _imply_backbone(self) -> list[Edge]:
        """Join each key to the one standing temporally just before it."""
        order = sorted(self.records)
        derived: list[Edge] = []
        for earlier, later in zip(order, order[1:]):
            if any(abs(e.target - later) < 1e-9 for e in self.out.get(earlier, [])):
                continue
            edge = Edge(earlier, later, round(later - earlier, 6), stated=False)
            self._add(edge)
            derived.append(edge)
        return derived

    @property
    def stated_edges(self) -> list[Edge]:
        return [e for e in self.edges if e.stated]

    @property
    def derived_edges(self) -> list[Edge]:
        return [e for e in self.edges if not e.stated]

    def __len__(self) -> int:
        return len(self.records)

    def successors(self, key: float) -> list[Edge]:
        return self.out.get(key, [])

    def predecessors(self, key: float) -> list[Edge]:
        return self.into.get(key, [])

    def out_degree(self, key: float) -> int:
        return len(self.out.get(key, []))

    def in_degree(self, key: float) -> int:
        return len(self.into.get(key, []))

    def roots(self) -> list[float]:
        return sorted(k for k in self.records if not self.into.get(k))

    def sinks(self) -> list[float]:
        return sorted(k for k in self.records if not self.out.get(k))

    def cycles(self) -> list[list[float]]:
        """Depth-first cycle search, iterative so deep chains cannot blow the stack."""
        WHITE, GREY, BLACK = 0, 1, 2
        color: dict[float, int] = {k: WHITE for k in self.records}
        found: list[list[float]] = []

        for start in list(self.records):
            if color[start] != WHITE:
                continue
            stack: list[tuple[float, int]] = [(start, 0)]
            path: list[float] = []
            color[start] = GREY
            path.append(start)
            while stack:
                node, index = stack[-1]
                edges = self.out.get(node, [])
                if index < len(edges):
                    stack[-1] = (node, index + 1)
                    nxt = edges[index].target
                    if nxt not in color:
                        continue  # dangling: not a key in this ledger
                    if color[nxt] == GREY:
                        found.append(path[path.index(nxt):] + [nxt])
                    elif color[nxt] == WHITE:
                        color[nxt] = GREY
                        path.append(nxt)
                        stack.append((nxt, 0))
                else:
                    color[node] = BLACK
                    stack.pop()
                    if path:
                        path.pop()
        return found

    def walk(self, key: float, depth: int = 3) -> list[tuple[int, Edge]]:
        """Follow the chain forward, breadth-first, to a given depth."""
        seen: set[float] = {key}
        frontier = [key]
        out: list[tuple[int, Edge]] = []
        for level in range(1, depth + 1):
            nxt: list[float] = []
            for node in frontier:
                for edge in self.out.get(node, []):
                    out.append((level, edge))
                    if edge.target not in seen:
                        seen.add(edge.target)
                        nxt.append(edge.target)
            frontier = nxt
            if not frontier:
                break
        return out

    def chain_to_sink(self, key: float, limit: int = 60) -> list[Edge]:
        """One forward path, always taking the nearest successor."""
        chain: list[Edge] = []
        seen = {key}
        current = key
        while len(chain) < limit:
            edges = [e for e in self.out.get(current, []) if e.target not in seen]
            if not edges:
                break
            edge = min(edges, key=lambda e: e.target)
            chain.append(edge)
            seen.add(edge.target)
            current = edge.target
        return chain

    def backbone_split(self) -> tuple[list[Edge], list[Edge]]:
        """Separate the spine from the skips.

        Taking the nearest successor at every step walks all 399 keys from the
        root to the sink, so the edge set is a backbone joining each key to the
        next one in position order, plus long-range edges that jump over it.
        """
        order = sorted(self.records)
        following = {key: order[i + 1] for i, key in enumerate(order[:-1])}
        backbone, long_range = [], []
        for edge in self.edges:
            (backbone if following.get(edge.source) == edge.target else long_range).append(edge)
        return backbone, long_range

    def integrity(self) -> IntegrityReport:
        dangling = [e for e in self.edges if e.target not in self.records]
        backbone, long_range = self.backbone_split()
        out_deg = {k: len(v) for k, v in self.out.items()}
        in_deg = {k: len(v) for k, v in self.into.items()}
        return IntegrityReport(
            keys=len(self.records),
            edges=len(self.edges),
            roots=self.roots(),
            sinks=self.sinks(),
            cycles=self.cycles(),
            dangling=dangling,
            backward=[e for e in self.edges if e.backward],
            gap_disputed=[e for e in self.edges if not e.gap_agrees],
            max_out=max(out_deg.items(), key=lambda kv: kv[1]) if out_deg else (0.0, 0),
            max_in=max(in_deg.items(), key=lambda kv: kv[1]) if in_deg else (0.0, 0),
            backbone=len(backbone),
            long_range=len(long_range),
            stated_edges=len(self.stated_edges),
            derived_edges=len(self.derived_edges),
        )
