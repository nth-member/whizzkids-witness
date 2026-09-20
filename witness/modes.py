"""The three ways the witness looks.

    watch     forward: nodes whose dates are arriving, and ones that just passed.
    backfill  backward: past nodes the ledger left silent.
    feed      sideways: what happened lately, placed against the ledger by date.

All three end in the same place -- findings appended to the store, each in its
band, each with a source.  The difference is only which dates they ask about.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .axis import band_for, offset_days
from .ledger import Node, load_nodes, nodes_by_date, recently_passed, upcoming
from .research import RawFinding, research_feed, research_node
from .store import Finding, FindingStore, RunLog, RunRecord


@dataclass
class ModeResult:
    mode: str
    run_id: str
    examined: list[str]
    new_findings: list[Finding]
    quiet_nodes: list[str]
    notes: list[str]


def _parse_event_date(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _to_finding(
    raw: RawFinding, node: Node, mode: str, run_id: str, model: str
) -> Finding:
    """Place one researched event against one node, in its band.

    The band is computed here, in code, from two dates -- never taken from the
    model's own sense of how close the match felt.  Month- and year-precision
    events get no day offset and no band: they are not day-level claims.
    """
    event_date = _parse_event_date(raw.event_date)
    if raw.date_precision == "day" and event_date and node.date:
        offset = offset_days(node.date, event_date)
        band = band_for(offset)
    else:
        offset = None
        band = f"{raw.date_precision}-precision"

    return Finding(
        node_id=node.node_id,
        node_position=node.position,
        node_date=node.iso_date,
        mode=mode,
        event_title=raw.event_title,
        event_date=raw.event_date,
        date_precision=raw.date_precision,
        offset_days=offset,
        band=band,
        what_happened=raw.what_happened,
        why_it_matters=raw.why_it_matters,
        source_url=raw.source_url,
        source_name=raw.source_name,
        confidence=raw.confidence,
        caution=raw.caution,
        analog_at_node=node.analog_text,
        chapter=node.chapter_title,
        run_id=run_id,
        model=model,
    )


def _run(
    mode: str,
    targets: list[Node],
    client,
    model: str,
    now: datetime,
    store: FindingStore,
    keep_raw: bool,
) -> ModeResult:
    run_id = RunRecord.new_id(mode)
    today = now.date().isoformat()
    examined: list[str] = []
    quiet: list[str] = []
    notes: list[str] = []
    collected: list[Finding] = []

    for node in targets:
        result = research_node(client, node, today, keep_raw=keep_raw)
        examined.append(node.node_id)
        if result.findings.quiet or not result.findings.findings:
            quiet.append(node.node_id)
            notes.append(f"{node.node_id} ({node.iso_date}): {result.findings.summary}")
            continue
        for raw in result.findings.findings:
            collected.append(_to_finding(raw, node, mode, run_id, model))

    new_findings = store.append(collected)
    if getattr(client, "dry", False):
        # A dry run looked at nothing; it does not belong in the record of looks.
        return ModeResult(mode, run_id, examined, new_findings, quiet, notes)
    RunLog().append(
        RunRecord(
            run_id=run_id,
            mode=mode,
            started_at=now.isoformat(),
            model=model,
            nodes_examined=examined,
            findings_new=len(new_findings),
            findings_total=len(store.all()),
            notes="; ".join(notes[:8]),
        )
    )
    return ModeResult(mode, run_id, examined, new_findings, quiet, notes)


def watch(
    client,
    model: str,
    now: datetime | None = None,
    horizon_days: int = 120,
    lookback_days: int = 30,
    limit: int = 3,
    workbook=None,
    store: FindingStore | None = None,
    keep_raw: bool = True,
) -> ModeResult:
    """Forward: the nodes whose dates are arriving or have just passed.

    A node whose date is still ahead cannot be witnessed -- nothing has happened
    there yet -- so the horizon is reported but only nodes at or behind today are
    researched.  Standing at 2026-09-20 the first open date is BB-235, 2026-10-29.
    """
    now = now or datetime.now(timezone.utc)
    nodes = load_nodes(workbook) if workbook else load_nodes()
    store = store or FindingStore()
    witnessed = store.witnessed_nodes()

    ahead = upcoming(nodes, now, horizon_days)
    passed = [n for n in recently_passed(nodes, now, lookback_days) if n.node_id not in witnessed]
    due_today = [n for n in ahead if n.date and n.date.date() == now.date()]

    targets = (due_today + passed)[:limit]
    result = _run("watch", targets, client, model, now, store, keep_raw)

    if ahead:
        horizon = ", ".join(f"{n.node_id} {n.iso_date}" for n in ahead[:5])
        result.notes.insert(0, f"Still ahead within {horizon_days} days: {horizon}")
    else:
        result.notes.insert(0, f"No node dates fall within the next {horizon_days} days.")
    return result


def backfill(
    client,
    model: str,
    now: datetime | None = None,
    limit: int = 3,
    since: str | None = None,
    until: str | None = None,
    include_thin: bool = False,
    workbook=None,
    store: FindingStore | None = None,
    keep_raw: bool = True,
) -> ModeResult:
    """Backward: the past nodes the ledger left silent.

    By default this takes only past nodes carrying no evidence at all.  There are
    just three: BB-004, BB-008 and BB-134.  (34 nodes are empty in the workbook,
    but 31 of those are future-dated and cannot hold evidence yet.)  With
    ``include_thin`` it also takes past nodes that have wider context but no
    exact-date event -- 225 of them, and the pool actually worth working.
    """
    now = now or datetime.now(timezone.utc)
    nodes = load_nodes(workbook) if workbook else load_nodes()
    store = store or FindingStore()
    witnessed = store.witnessed_nodes()

    def wanted(node: Node) -> bool:
        if not node.date or node.date.date() > now.date():
            return False
        if node.node_id in witnessed:
            return False
        if since and node.iso_date < since:
            return False
        if until and node.iso_date > until:
            return False
        if include_thin:
            return not node.has_exact_event()
        return node.evidence_count() == 0

    targets = sorted((n for n in nodes if wanted(n)), key=lambda n: n.date)[:limit]
    result = _run("backfill", targets, client, model, now, store, keep_raw)
    remaining = sum(1 for n in nodes if wanted(n))
    result.notes.insert(
        0, f"Silent nodes still unwitnessed after this run: {max(0, remaining - len(targets))}"
    )
    return result


def feed(
    client,
    model: str,
    now: datetime | None = None,
    days: int = 7,
    workbook=None,
    store: FindingStore | None = None,
    keep_raw: bool = True,
) -> ModeResult:
    """Sideways: what happened lately, then placed against the ledger by date.

    The search runs with no node in hand, so the world is read on its own terms.
    Placement happens afterwards, in code: an event is attached to a node only
    when their dates actually coincide.  Most days attach to nothing, and that is
    the expected result, not a failure.
    """
    now = now or datetime.now(timezone.utc)
    nodes = load_nodes(workbook) if workbook else load_nodes()
    store = store or FindingStore()
    run_id = RunRecord.new_id("feed")
    today = now.date().isoformat()
    since = (now - timedelta(days=days)).date().isoformat()

    result = research_feed(client, since, today, keep_raw=keep_raw)
    by_date = nodes_by_date(nodes)

    collected: list[Finding] = []
    notes: list[str] = [f"World read from {since} to {today}: {result.findings.summary}"]
    unplaced = 0

    for raw in result.findings.findings:
        event_date = _parse_event_date(raw.event_date)
        if raw.date_precision != "day" or event_date is None:
            unplaced += 1
            continue
        landed = by_date.get(event_date.date().isoformat(), [])
        if not landed:
            unplaced += 1
            continue
        for node in landed:
            collected.append(_to_finding(raw, node, "feed", run_id, model))

    new_findings = store.append(collected)
    notes.append(
        f"{len(result.findings.findings)} events read; {unplaced} landed on no node date."
    )
    if getattr(client, "dry", False):
        return ModeResult("feed", run_id, sorted({f.node_id for f in collected}),
                          new_findings, [], notes)
    RunLog().append(
        RunRecord(
            run_id=run_id,
            mode="feed",
            started_at=now.isoformat(),
            model=model,
            nodes_examined=sorted({f.node_id for f in collected}),
            findings_new=len(new_findings),
            findings_total=len(store.all()),
            notes=notes[-1],
        )
    )
    return ModeResult("feed", run_id, sorted({f.node_id for f in collected}), new_findings, [], notes)
