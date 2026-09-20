"""The control.

Something notable happened within seven days of almost any date in computing
history since 1974.  So a finding at a ledger date means nothing on its own --
only the difference between the ledger's dates and dates that are not the
ledger's carries information.  Without that comparison the report is a list of
coincidences with no denominator, and the more of it there is, the less any one
entry is worth.

A decoy is the same position researched under the same rules at a displaced
date.  Findings made against one are recorded with the displacement on them, so
the two populations can never be confused and can always be compared.
"""

from __future__ import annotations

import copy
import random
from datetime import timedelta

from .graph import Edge
from .ledger import Node

# Far enough that the windows cannot overlap (the widest band is 30 days), near
# enough to stay in the same technological era.
MIN_SHIFT = 120
MAX_SHIFT = 900


def pick_offset(seed: str, rng: random.Random | None = None) -> int:
    """A displacement, positive or negative, stable for a given seed."""
    rng = rng or random.Random(seed)
    return rng.choice([-1, 1]) * rng.randint(MIN_SHIFT, MAX_SHIFT)


def shift_node(node: Node, days: int) -> Node:
    """The same position, asked about a date that is not its own."""
    moved = copy.copy(node)
    if node.date:
        moved.date = node.date + timedelta(days=days)
    if node.timestamp:
        moved.timestamp = node.timestamp + timedelta(days=days)
    # The evidence already on file belongs to the real date, not this one.
    moved.within_7d = []
    moved.context_8_30d = []
    moved.exact_events = []
    moved.month_events = []
    moved.year_events = []
    moved.evidence_status = "decoy date — the ledger says nothing about this day"
    return moved


def shift_edge(edge: Edge, days: int) -> Edge:
    """The same span, moved wholesale, so its length is preserved exactly."""
    return Edge(
        source=edge.source + days / 100.0,
        target=edge.target + days / 100.0,
        stated_gap=edge.stated_gap,
        stated=edge.stated,
        default=edge.default,
    )
