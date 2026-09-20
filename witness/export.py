"""Export the ledger and the findings as one JSON payload.

The browser page is a single file with this payload baked in, so it opens from a
phone with no server, no network and no build step.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .axis import ACTIVE, verify
from .ledger import applied_errata, load_graph, load_nodes
from .sources import cited_domains
from .store import FindingStore, IntervalStore, RunLog


def build_payload(workbook=None, store: FindingStore | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    nodes = load_nodes(workbook) if workbook else load_nodes()
    graph = load_graph(workbook) if workbook else load_graph()
    store = store or FindingStore()
    findings = store.all()
    check = verify(nodes)
    report = graph.integrity()

    # Which node, if any, carries each BB key -- so a successor in the page can
    # be followed to the position that draws on it.
    key_nodes: dict[str, str] = {}
    for node in nodes:
        if node.analog_key is not None:
            key_nodes.setdefault(f"{node.analog_key:g}", node.node_id)

    def trim(text: str | None, limit: int = 400) -> str:
        text = (text or "").strip()
        return text if len(text) <= limit else text[: limit - 1] + "…"

    return {
        "generated": now.isoformat(),
        "axis": {
            "instance": ACTIVE.name,
            "title": ACTIVE.title,
            "scale": ACTIVE.scale,
            "epoch": ACTIVE.epoch.isoformat().replace("+00:00", "Z"),
            "days_per_unit": ACTIVE.days_per_unit,
            "gauge": ACTIVE.gauge.get("expression", ""),
            "gauge_value": ACTIVE.gauge.get("decimal"),
            "verified": check.ok,
            "checked": check.checked,
            "mismatches": len(check.mismatches),
        },
        "graph": {
            "keys": report.keys,
            "edges": report.edges,
            "acyclic": report.acyclic,
            "closed": report.closed,
            "roots": report.roots,
            "sinks": report.sinks,
            "max_out": list(report.max_out),
            "max_in": list(report.max_in),
            "backbone": report.backbone,
            "long_range": report.long_range,
            "stated_edges": report.stated_edges,
            "derived_edges": report.derived_edges,
            "default_connections": report.default_connections,
            "default_also_stated": report.default_also_stated,
            "derived": [
                {"from": e.source, "to": e.target, "gap": e.stated_gap,
                 "from_date": e.source_date.date().isoformat(),
                 "to_date": e.target_date.date().isoformat()}
                for e in graph.derived_edges
            ],
            "backward": [
                {"from": e.source, "to": e.target, "gap": e.stated_gap,
                 "implied": e.implied_gap, "days": e.implied_days}
                for e in report.backward
            ],
            "disputed": [
                {"from": e.source, "to": e.target, "gap": e.stated_gap,
                 "implied": e.implied_gap, "days": e.implied_days,
                 "from_date": e.source_date.date().isoformat(),
                 "to_date": e.target_date.date().isoformat()}
                for e in report.gap_disputed
            ],
        },
        "key_nodes": key_nodes,
        "errata": [
            {"id": e.id, "summary": e.summary, "reason": e.reason,
             "by": e.reported_by, "on": e.reported_on, "cost": e.cost}
            for e in applied_errata()
        ],
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
                "key": n.analog_key,
                "succ": [
                    {"key": k, "gap": g, "date": d,
                     "disputed": abs((k - (n.analog_key or k)) - g) > 0.005}
                    for k, g, d in n.successor_dates[:8]
                ],
                # The default connection out of this node's key: to the key
                # standing immediately next in time, whether or not a successor
                # cell records it.
                "dflt": (
                    lambda e: e and {
                        "key": e.target, "gap": e.stated_gap,
                        "date": e.target_date.date().isoformat(),
                        "stated": e.stated,
                    }
                )(graph.default_edge(n.analog_key) if n.analog_key is not None else None),
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
             "tier": f.source_tier,
                "created": f.created_at, "model": f.model,
            }
            for f in findings
        ],
        "intervals": [
            {"src": f.edge_source, "tgt": f.edge_target, "opens": f.opens,
             "closes": f.closes, "span": f.span_days, "dev": f.development,
             "shape": f.shape, "what": f.what_happened,
             "open_event": f.open_event, "open_date": f.open_date,
             "open_band": f.open_band, "open_url": f.open_url,
             "close_event": f.close_event, "close_date": f.close_date,
             "close_band": f.close_band, "close_url": f.close_url,
             "caution": f.caution, "confidence": f.confidence}
            for f in IntervalStore().all()
        ],
        "sources": {
            "policy": "open search, the ledger's own domains preferred",
            "domains": [d for d, _ in cited_domains()][:24],
            "cited": sum(c for _, c in cited_domains()),
        },
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
