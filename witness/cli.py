"""Command line.

    python -m witness verify                 check the axis and read the ledger
    python -m witness nodes --horizon 400    what is still ahead
    python -m witness edges                  the successor graph and its anomalies
    python -m witness watch --dry-run        forward, without spending anything
    python -m witness backfill --limit 2     backward, into the silent nodes
    python -m witness feed --days 7          sideways, the world placed by date
    python -m witness render                 rewrite reports/WITNESS.md
    python -m witness build-web              rebuild the browser page

Every mode that calls the API accepts --dry-run first. Use it.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from .axis import verify
from .ledger import applied_errata, load_graph, load_nodes, upcoming
from .render import render_upcoming_table, write_witness
from .constants import MODEL
from .store import FindingStore


def _client(args):
    from .research import DryRunClient, WitnessClient

    if args.dry_run:
        print("[dry run] no API calls will be made.\n")
        return DryRunClient(), f"{args.model} (dry run)"
    return WitnessClient(model=args.model, effort=args.effort, max_uses=args.max_uses), args.model


def _now(args) -> datetime:
    if args.today:
        return datetime.fromisoformat(args.today).replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _report(result) -> None:
    print(f"\nrun {result.run_id} — mode {result.mode}")
    print(f"  nodes examined : {', '.join(result.examined) or 'none'}")
    print(f"  new findings   : {len(result.new_findings)}")
    for finding in result.new_findings:
        offset = (
            "same day" if finding.offset_days == 0
            else f"{finding.offset_days:+d}d" if finding.offset_days is not None
            else finding.date_precision
        )
        print(f"    [{finding.band:<14}] {finding.node_id} {finding.event_date} ({offset}) {finding.event_title}")
    if result.quiet_nodes:
        print(f"  quiet nodes    : {', '.join(result.quiet_nodes)}")
    for note in result.notes:
        print(f"  note           : {note}")


def main(argv: list[str] | None = None) -> int:
    # Shared options are attached to the top-level parser *and* to every
    # subcommand, so `witness --dry-run watch` and `witness watch --dry-run`
    # both work.  Defaults are filled in after parsing rather than declared
    # twice, so the subcommand copy cannot overwrite a flag given before it.
    common = argparse.ArgumentParser(add_help=False, argument_default=argparse.SUPPRESS)
    common.add_argument("--workbook", type=Path, help="path to the enriched xlsx")
    common.add_argument("--model", help=f"default: {MODEL}")
    common.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    common.add_argument("--max-uses", type=int, help="web searches per node (default 8)")
    common.add_argument("--dry-run", action="store_true", help="build the prompts, call nothing")
    common.add_argument("--today", help="stand at this date instead of now (ISO)")
    common.add_argument("--no-raw", action="store_true", help="do not keep raw research notes")

    parser = argparse.ArgumentParser(
        prog="witness",
        description="Behold what the whizz kids have wrought.",
        parents=[common],
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("verify", parents=[common], help="check the axis and report the ledger's shape")

    p_nodes = sub.add_parser("nodes", parents=[common], help="list node dates still ahead")
    p_nodes.add_argument("--horizon", type=int, default=400)

    p_edges = sub.add_parser("edges", parents=[common],
                             help="the successor graph over the 399 BB keys")
    p_edges.add_argument("--from", dest="from_key", type=float, default=None,
                         help="walk forward from this key")
    p_edges.add_argument("--depth", type=int, default=2, help="how far to walk")
    p_edges.add_argument("--chain", action="store_true",
                         help="follow one path to the sink, nearest successor each step")
    p_edges.add_argument("--stated-only", action="store_true",
                         help="the graph exactly as the workbook states it, without the"
                              " edges the default predecessor rule implies")

    p_watch = sub.add_parser("watch", parents=[common], help="forward: dates arriving or just passed")
    p_watch.add_argument("--horizon", type=int, default=120)
    p_watch.add_argument("--lookback", type=int, default=30)
    p_watch.add_argument("--limit", type=int, default=3)

    p_back = sub.add_parser("backfill", parents=[common], help="backward: the silent past nodes")
    p_back.add_argument("--limit", type=int, default=3)
    p_back.add_argument("--since", default=None)
    p_back.add_argument("--until", default=None)
    p_back.add_argument("--include-thin", action="store_true",
                        help="also take nodes with context but no exact-date event")

    p_feed = sub.add_parser("feed", parents=[common], help="sideways: recent world, placed by date")
    p_feed.add_argument("--days", type=int, default=7)

    sub.add_parser("render", parents=[common], help="rewrite reports/WITNESS.md")

    p_web = sub.add_parser("build-web", parents=[common], help="rebuild the single-file browser page")
    p_web.add_argument("--out", type=Path, default=None)

    args = parser.parse_args(argv)
    for name, value in {
        "workbook": None, "model": MODEL, "effort": "high", "max_uses": 8,
        "dry_run": False, "today": None, "no_raw": False,
    }.items():
        if not hasattr(args, name):
            setattr(args, name, value)

    now = _now(args)
    store = FindingStore()
    keep_raw = not args.no_raw

    if args.command == "verify":
        nodes = load_nodes(args.workbook) if args.workbook else load_nodes()
        check = verify(nodes)
        print(f"nodes            : {len(nodes)}")
        print(f"axis check       : {'ok — every timestamp reproduced' if check.ok else check.mismatches}")
        print(f"exact-date events: {sum(1 for n in nodes if n.has_exact_event())} nodes")
        print(f"no evidence      : {sum(1 for n in nodes if n.evidence_count() == 0)} nodes")
        print(f"future-dated     : {sum(1 for n in nodes if n.is_future(now))} nodes")
        print(f"findings on file : {len(store.all())}")
        graph = load_graph(args.workbook) if args.workbook else load_graph()
        report = graph.integrity()
        print(f"successor graph  : {report.edges} edges over {report.keys} keys, "
              f"{'acyclic' if report.acyclic else 'CYCLIC'}, "
              f"{len(report.gap_disputed)} gaps disputed  (see: witness edges)")
        corrections = applied_errata()
        if corrections:
            print(f"errata applied   : {len(corrections)} — "
                  + "; ".join(f"{e.id} ({e.summary})" for e in corrections))
        ahead = upcoming(nodes, now, 400)
        if ahead:
            print(f"next date        : {ahead[0].node_id} on {ahead[0].iso_date} — {ahead[0].analog_text}")
        return 0 if check.ok else 1

    if args.command == "edges":
        imply = not args.stated_only
        graph = load_graph(args.workbook, imply) if args.workbook else load_graph(
            imply_backbone=imply
        )
        if args.from_key is not None:
            record = graph.records.get(args.from_key)
            if record is None:
                print(f"no such key: {args.from_key}")
                return 1
            print(f"{record.key}  {record.date}  {record.analog[:70]}")
            print(f"  in {graph.in_degree(record.key)} / out {graph.out_degree(record.key)}")
            default = graph.default_edge(record.key)
            print(f"  default next: {default.describe() if default else 'none — this is the sink'}")
            for edge in graph.predecessors(record.key):
                print(f"  ← {edge.describe()}")
            if args.chain:
                print("  chain to the sink, nearest successor each step:")
                for edge in graph.chain_to_sink(record.key):
                    print(f"    {edge.describe()}")
            else:
                for level, edge in graph.walk(record.key, args.depth):
                    print(f"  {'  ' * level}→ {edge.describe()}")
            return 0

        report = graph.integrity()
        corrections = applied_errata()
        if corrections:
            print("errata applied to the workbook before this report:")
            for erratum in corrections:
                print(f"  {erratum.id}: {erratum.summary}")
                print(f"    {erratum.reason}")
                print(f"    reported by {erratum.reported_by}, {erratum.reported_on};"
                      f" declared in data/errata.json")
            print()
        rule_only = report.default_connections - report.default_also_stated
        print(f"keys             : {report.keys}")
        print(f"relations        : {report.edges}")
        print(f"  backbone       : {report.default_connections} — each key to the one immediately"
              " next to it")
        print(f"                   ({report.default_also_stated} also stated in the workbook,"
              f" {rule_only} by default alone)")
        print(f"  long-range     : {report.long_range} stated edges skipping over the backbone")
        print(f"acyclic          : {report.acyclic}")
        print(f"every successor is a key: {report.closed}")
        print(f"roots            : {report.roots}")
        print(f"sinks            : {report.sinks}")
        print(f"widest branching : {report.max_out[0]} with {report.max_out[1]} successors")
        print(f"most converged-on: {report.max_in[0]} with {report.max_in[1]} predecessors")
        if report.backward:
            print(f"backward edges   : {len(report.backward)} (successor at or before its source)")
            for edge in report.backward:
                print(f"  {edge.describe()}")
        if graph.derived_edges:
            print("backbone links the workbook does not write down:")
            for edge in graph.derived_edges:
                print(f"  {edge.source} → {edge.target}  gap {edge.stated_gap}"
                      f"  ({edge.source_date.date()} → {edge.target_date.date()})")
        if report.gap_disputed:
            print(f"gap disputed     : {len(report.gap_disputed)} — stated gap and the")
            print( "                   difference between the keys disagree. The parable")
            print( "                   preserved and flagged these rather than resolving")
            print( "                   them; so does this. Both numbers are kept.")
            for edge in report.gap_disputed:
                print(f"  {edge.describe()}")
        return 0

    if args.command == "nodes":
        nodes = load_nodes(args.workbook) if args.workbook else load_nodes()
        print(render_upcoming_table(nodes, now, args.horizon))
        return 0

    if args.command == "render":
        path = write_witness(workbook=args.workbook, store=store, now=now)
        print(f"wrote {path}")
        return 0

    if args.command == "build-web":
        from .web import build_page
        path = build_page(out=args.out, workbook=args.workbook, store=store, now=now)
        print(f"wrote {path}")
        return 0

    from . import modes

    client, model = _client(args)
    if args.command == "watch":
        result = modes.watch(client, model, now=now, horizon_days=args.horizon,
                             lookback_days=args.lookback, limit=args.limit,
                             workbook=args.workbook, store=store, keep_raw=keep_raw)
    elif args.command == "backfill":
        result = modes.backfill(client, model, now=now, limit=args.limit, since=args.since,
                                until=args.until, include_thin=args.include_thin,
                                workbook=args.workbook, store=store, keep_raw=keep_raw)
    else:
        result = modes.feed(client, model, now=now, days=args.days,
                            workbook=args.workbook, store=store, keep_raw=keep_raw)

    _report(result)
    if not args.dry_run:
        print(f"\nwrote {write_witness(workbook=args.workbook, store=store, now=now)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
