"""Corrections applied to the workbook at load time.

The vendored .xlsx is never edited.  It stays the source of record, and any
correction to it is declared in ``data/errata.json`` with the evidence on both
sides and applied on the way in, so the corrected value is what the agent, the
report and the page all see -- while what the file actually says, and why it was
overridden, remain readable.

This is the same discipline the ledger already keeps for its disputed gaps:
preserve, declare, and never silently rewrite.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_ERRATA = Path(__file__).resolve().parent.parent / "data" / "errata.json"
TOLERANCE = 1e-9


@dataclass
class Erratum:
    id: str
    applied: bool
    target: str
    reason: str
    change: dict[str, Any]
    reported_by: str = ""
    reported_on: str = ""
    evidence_for: list[str] | None = None
    evidence_against: list[str] | None = None
    reconciliation: str = ""
    cost: str = ""
    preserves: str = ""
    hits: int = 0

    @property
    def summary(self) -> str:
        change = self.change
        if change.get("type") == "key_split":
            parts = ", ".join(str(part["key"]) for part in change.get("into", []))
            return f"row {change['row_key']} split into {parts}"
        return str(change)


def load_errata(path: Path | str = DEFAULT_ERRATA) -> list[Erratum]:
    path = Path(path)
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for record in raw.get("errata", []):
        fields = {k: v for k, v in record.items() if k in Erratum.__dataclass_fields__}
        out.append(Erratum(**fields))
    return out


def _same(a: float | None, b: float) -> bool:
    return a is not None and abs(float(a) - float(b)) < TOLERANCE


def apply_to_keys(records: list, errata: list[Erratum]) -> list[Erratum]:
    """Split a row that carries more than one key back into its keys.

    Each resulting key takes only the successor edges that belong to it.  The
    chapter and evidence status are inherited, because the workbook records
    those per position and the split does not divide them.
    """
    from .axis import position_to_timestamp
    from .graph import KeyRecord

    active = [e for e in errata if e.applied and e.change.get("type") == "key_split"]
    for erratum in active:
        row_key = float(erratum.change["row_key"])
        parts = erratum.change.get("into", [])
        index = next(
            (i for i, r in enumerate(records) if _same(r.key, row_key)), None
        )
        if index is None:
            continue  # already split, or the workbook no longer carries that row
        original = records[index]
        replacements = [
            KeyRecord(
                key=float(part["key"]),
                date=position_to_timestamp(float(part["key"])).date().isoformat(),
                analog=part.get("analog", original.analog),
                chapter=original.chapter,
                evidence_status=original.evidence_status,
                carried_by=list(original.carried_by),
                successors=[(float(t), float(g)) for t, g in part.get("successors", [])],
            )
            for part in parts
        ]
        records[index:index + 1] = replacements
        erratum.hits += len(replacements)
    records.sort(key=lambda r: r.key)
    return active


def apply_to_nodes(nodes, errata: list[Erratum]) -> list[Erratum]:
    """Nodes need no rewriting under a split.

    No node is attached to the split key, and the one inbound edge that names it
    -- -1.916 -> 0.18 -- belongs to the half that keeps the recorded value. This
    is checked rather than assumed: anything unexpected is counted and reported.
    """
    active = [e for e in errata if e.applied and e.change.get("type") == "key_split"]
    for erratum in active:
        row_key = float(erratum.change["row_key"])
        keeps = {float(p["key"]) for p in erratum.change.get("into", [])}
        if row_key in keeps:
            continue  # the recorded value survives the split; nothing to rewrite
        for node in nodes:
            if _same(node.analog_key, row_key):
                erratum.hits += 1
            for target, _gap in node.successors:
                if _same(target, row_key):
                    erratum.hits += 1
    return active
