"""Export the ledger and the findings as one JSON payload.

The browser page is a single file with this payload baked in, so it opens from a
phone with no server, no network and no build step.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .axis import verify
from .ledger import load_nodes
from .store import FindingStore, RunLog


def build_payload(workbook=None, store: FindingStore | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    nodes = load_nodes(workbook) if workbook else load_nodes()
    store = store or FindingStore()
    findings = store.all()
    check = verify(nodes)

    def trim(text: str | None, limit: int = 400) -> str:
        text = (text or "").strip()
        return text if len(text) <= limit else text[: limit - 1] + "…"

    return {
        "generated": now.isoformat(),
        "axis": {
            "epoch": "2015-04-30T11:28:41.739Z",
            "days_per_unit": 100,
            "verified": check.ok,
            "checked": check.checked,
            "mismatches": len(check.mismatches),
        },
        "nodes": [
            {
                "id": n.node_id,
                "pos": n.position,
                "date": n.iso_date,
                "future": n.is_future(now),
                "analog": trim(n.analog_text, 220),
                "chapter": n.chapter_title,
                "reading": trim(n.chapter_reading, 320),
                "status": n.evidence_status or "",
                "exact": len(n.exact_events),
                "d7": len(n.within_7d),
                "d30": len(n.context_8_30d),
                "gloss": [list(g) for g in n.parable_gloss[:2]],
                "items": [
                    {"date": i.date, "off": i.offset, "kind": i.kind,
                     "text": trim(i.description, 260), "url": i.url}
                    for i in (n.within_7d + n.context_8_30d)[:8]
                ],
                "events": [list(e)[:5] for e in n.exact_events[:4]],
            }
            for n in nodes
        ],
        "findings": [
            {
                "id": f.finding_id, "node": f.node_id, "node_date": f.node_date,
                "title": f.event_title, "date": f.event_date, "precision": f.date_precision,
                "off": f.offset_days, "band": f.band, "what": f.what_happened,
                "why": f.why_it_matters, "caution": f.caution, "url": f.source_url,
                "source": f.source_name, "confidence": f.confidence, "mode": f.mode,
                "created": f.created_at, "model": f.model,
            }
            for f in findings
        ],
        "runs": [
            {"id": r.run_id, "mode": r.mode, "at": r.started_at,
             "new": r.findings_new, "total": r.findings_total, "notes": r.notes}
            for r in RunLog().all()[-25:]
        ],
    }


def write_payload(path: Path | str, **kwargs) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_payload(**kwargs), ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return path
