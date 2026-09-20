"""Reports.

WITNESS.md is the standing document: what the ledger claims, what the agent
found, and -- kept just as visible -- where it found nothing.  A witness that
only reports hits is not a witness.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .axis import BAND_LABELS, verify
from .ledger import Node, load_nodes, upcoming
from .store import FindingStore, RunLog

REPORTS = Path(__file__).resolve().parent.parent / "reports"
TITLE = "Behold what the whizz kids have wrought"

BAND_ORDER = ["exact", "within_7d", "context_8_30d", "outside"]


def _band_rank(band: str) -> int:
    return BAND_ORDER.index(band) if band in BAND_ORDER else len(BAND_ORDER)


def render_witness(
    workbook=None, store: FindingStore | None = None, now: datetime | None = None
) -> str:
    now = now or datetime.now(timezone.utc)
    nodes = load_nodes(workbook) if workbook else load_nodes()
    store = store or FindingStore()
    findings = store.all()
    by_node = {n.node_id: n for n in nodes}
    check = verify(nodes)
    runs = RunLog().all()

    lines: list[str] = [
        f"# {TITLE}",
        "",
        "*A witness to the SFO-BB ledger: what it claims, what the world actually did,*",
        "*and where the days were quiet.*",
        "",
        f"Standing at **{now.date().isoformat()}**.",
        "",
        "## The ledger as it stands",
        "",
        f"- Nodes on the axis: **{len(nodes)}**",
        f"- Axis check (timestamp = epoch + 100 days x position): "
        f"**{'reproduces every timestamp' if check.ok else str(len(check.mismatches)) + ' mismatches'}**",
        f"- Nodes already carrying an exact-date event in the workbook: "
        f"**{sum(1 for n in nodes if n.has_exact_event())}**",
        f"- Nodes carrying no evidence at all: "
        f"**{sum(1 for n in nodes if n.evidence_count() == 0)}**",
        f"- Nodes whose dates are still in the future: "
        f"**{sum(1 for n in nodes if n.is_future(now))}**",
        "",
    ]

    ahead = upcoming(nodes, now, 400)
    if ahead:
        lines += ["## Dates still to arrive", "", "| Node | Position | Date | Stated analog |", "|---|---|---|---|"]
        for node in ahead[:12]:
            analog = (node.analog_text or "").replace("|", "/")[:90]
            lines.append(f"| {node.node_id} | {node.position} | {node.iso_date} | {analog} |")
        lines.append("")

    lines += ["## What the witness has found", ""]
    if not findings:
        lines += [
            "Nothing yet. No run has appended a finding.",
            "",
            "That is the honest state of this file until the agent has actually looked.",
            "",
        ]
    else:
        bands = Counter(f.band for f in findings)
        lines.append(f"**{len(findings)} findings** across **{len({f.node_id for f in findings})} nodes**.")
        lines.append("")
        lines.append("| Band | Meaning | Findings |")
        lines.append("|---|---|---|")
        for band, count in sorted(bands.items(), key=lambda kv: _band_rank(kv[0])):
            lines.append(f"| `{band}` | {BAND_LABELS.get(band, 'precision below day level')} | {count} |")
        lines.append("")

        grouped: dict[str, list] = {}
        for finding in findings:
            grouped.setdefault(finding.node_id, []).append(finding)

        for node_id in sorted(grouped, key=lambda nid: by_node[nid].date if nid in by_node and by_node[nid].date else now, reverse=True):
            node = by_node.get(node_id)
            lines.append(f"### {node_id} — {node.iso_date if node else '?'}")
            lines.append("")
            if node:
                lines.append(f"*Stated analog:* {node.analog_text}")
                if node.chapter_title:
                    lines.append(f"  ")
                    lines.append(f"*Design-story chapter:* {node.chapter_title}")
                lines.append("")
            for finding in sorted(grouped[node_id], key=lambda f: _band_rank(f.band)):
                offset = "same day" if finding.offset_days == 0 else (
                    f"{finding.offset_days:+d} days" if finding.offset_days is not None
                    else f"{finding.date_precision}-precision"
                )
                lines += [
                    f"- **{finding.event_title}** — {finding.event_date} ({offset}, `{finding.band}`)",
                    f"  {finding.what_happened}",
                    f"  *Why it mattered:* {finding.why_it_matters}",
                    f"  *Caution:* {finding.caution}",
                    f"  *Source:* [{finding.source_name}]({finding.source_url}) — confidence: {finding.confidence}",
                    "",
                ]

    quiet_notes = [r for r in runs if r.notes]
    if quiet_notes:
        lines += ["## Where the days were quiet", "", "Runs that looked and found nothing worth recording:", ""]
        for record in quiet_notes[-10:]:
            lines.append(f"- `{record.run_id}` ({record.mode}): {record.notes}")
        lines.append("")

    lines += [
        "## Standing cautions",
        "",
        "These are the workbook's own, and they hold for everything above.",
        "",
        "- The bands are a research convention of the parable and ledger, not a discovered",
        "  property of SFO-BB. Same day, within seven days and 8–30 days are separate",
        "  categories and are never merged here.",
        "- Source event dates often use local calendars while SFO timestamps are UTC, so a",
        "  same-day match does not establish an exact matching instant.",
        "- Historical proximity and semantic fit are distinct: a date match can be exact",
        "  while its developmental interpretation is weak.",
        "- The stated analog is a supplied developmental and symbolic framework. Historical",
        "  coincidence does not validate causation and does not predict superintelligence.",
        "- Findings below the heading above were written by a language model with web search.",
        "  Each carries its own source and confidence. They are research notes, not a record.",
        "",
    ]
    if runs:
        last = runs[-1]
        lines.append(f"*Last run: `{last.run_id}` — {last.mode}, {last.findings_new} new findings, model {last.model}.*")
    return "\n".join(lines) + "\n"


def write_witness(**kwargs) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / "WITNESS.md"
    path.write_text(render_witness(**kwargs), encoding="utf-8")
    return path


def render_upcoming_table(nodes: list[Node], now: datetime, horizon: int = 400) -> str:
    rows = upcoming(nodes, now, horizon)
    if not rows:
        return "No node dates within the horizon."
    width = max(len(n.analog_text or "") for n in rows)
    out = [f"{'Node':<9} {'Pos':>8}  {'Date':<12} Stated analog"]
    for node in rows:
        out.append(
            f"{node.node_id:<9} {node.position:>8}  {node.iso_date:<12} "
            f"{(node.analog_text or '')[:min(width, 70)]}"
        )
    return "\n".join(out)
