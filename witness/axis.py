"""The common time axis.

Every position-bearing source in this instance sits on one axis:

    timestamp = EPOCH + DAYS_PER_UNIT * position

Both constants are a *gauge*, not a property of SFO-BB.  The corpus carries
eleven named readings over the same positions at four scales (3500D, 2800D/23,
100D, yG), and this implementation traverses one of them.  Which one, and what
anchors it, is declared in ``data/instances/<name>.json`` and loaded here, so a
different slice is a different config rather than a different program.

The workbook's Method sheet records that recomputing the 265 node timestamps
from their positions reproduces every timestamp printed in REVOTT_Y_24PT50.md
exactly (0 mismatches).  `verify` below re-runs that check, because an agent
that appends to a ledger should be able to prove it is reading the same ledger.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

INSTANCES = Path(__file__).resolve().parent.parent / "data" / "instances"
DEFAULT_INSTANCE = os.environ.get("WITNESS_INSTANCE", "whizz-kids")


@dataclass(frozen=True)
class Instance:
    """One anchoring of the axis: which scale, and what fixes its zero."""

    name: str
    title: str
    epoch: datetime
    days_per_unit: float
    scale: str
    reading: str | None
    gauge: dict
    sampled: dict

    @property
    def formula(self) -> str:
        return f"timestamp = {self.epoch.isoformat()} + {self.days_per_unit:g} days x position"


def load_instance(name: str = DEFAULT_INSTANCE) -> Instance:
    raw = json.loads((INSTANCES / f"{name}.json").read_text(encoding="utf-8"))
    stamp = raw["epoch"].replace("Z", "+00:00")
    return Instance(
        name=raw["name"],
        title=raw.get("title", raw["name"]),
        epoch=datetime.fromisoformat(stamp),
        days_per_unit=float(raw["days_per_unit"]),
        scale=raw.get("scale", ""),
        reading=raw.get("reading"),
        gauge=raw.get("gauge", {}),
        sampled=raw.get("sampled", {}),
    )


ACTIVE = load_instance()

EPOCH = ACTIVE.epoch
DAYS_PER_UNIT = ACTIVE.days_per_unit

# The three bands the ledger keeps apart.  They are a research convention of the
# parable and ledger, not a discovered property of SFO-BB, and they must never
# be merged into a single "match" -- that collapse is what turns a dated record
# into an oracle.
EXACT = "exact"
WITHIN_7D = "within_7d"
CONTEXT_8_30D = "context_8_30d"
OUTSIDE = "outside"

BAND_LABELS = {
    EXACT: "same calendar day",
    WITHIN_7D: "within seven days",
    CONTEXT_8_30D: "wider context, 8-30 days",
    OUTSIDE: "outside the ledger's bands",
}


def position_to_timestamp(position: float) -> datetime:
    """Map an SFO-BB position onto the common axis."""
    return EPOCH + timedelta(days=DAYS_PER_UNIT * float(position))


def timestamp_to_position(ts: datetime) -> float:
    """Inverse of :func:`position_to_timestamp`."""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return (ts - EPOCH).total_seconds() / (DAYS_PER_UNIT * 86400.0)


def offset_days(node_date: datetime, event_date: datetime) -> int:
    """Signed distance in whole days: negative means the event precedes the node."""
    return (event_date.date() - node_date.date()).days


def band_for(offset: int) -> str:
    """Classify a signed day offset into the ledger's bands."""
    distance = abs(offset)
    if distance == 0:
        return EXACT
    if distance <= 7:
        return WITHIN_7D
    if distance <= 30:
        return CONTEXT_8_30D
    return OUTSIDE


@dataclass(frozen=True)
class AxisCheck:
    checked: int
    mismatches: list[tuple[str, str, str]]

    @property
    def ok(self) -> bool:
        return not self.mismatches


def verify(nodes) -> AxisCheck:
    """Recompute each node's timestamp from its position and compare.

    Tolerance is one second: the workbook prints timestamps to millisecond
    precision, and positions are stored as decimal text.
    """
    mismatches: list[tuple[str, str, str]] = []
    for node in nodes:
        if node.timestamp is None or node.position is None:
            continue
        recomputed = position_to_timestamp(node.position)
        drift = abs((recomputed - node.timestamp).total_seconds())
        if drift > 1.0:
            mismatches.append(
                (node.node_id, node.timestamp.isoformat(), recomputed.isoformat())
            )
    return AxisCheck(checked=len(nodes), mismatches=mismatches)
