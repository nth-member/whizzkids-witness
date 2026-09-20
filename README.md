# Behold what the whizz kids have wrought

A witness to the SFO-BB ledger.

The ledger — `data/SFO_BB_analog_x_computing_events_enriched.xlsx` — places 265 positions on
a single time axis, from **1974-12-01** to **2081-05-13**, and attaches to each one a *stated
analog* (a supplied developmental and symbolic framework) and a chapter of computing's design
story: build a machine → connect machines → publish and find information → participate in
platforms → give software perceptual capabilities → converse with models → delegate actions.

234 of those dates have passed. **31 have not.** The next is **BB-235 on 2026-10-29**; the
framework's designated Super Intelligence position, 82.80, maps to **2037-12-30**.

This repository is the agent that stands at today's date and checks what the whizz kids
actually wrought — node by node, with sources — and writes down where it found nothing.

## The axis

    timestamp = 2015-04-30T11:28:41.739Z + 100 days × position

`python -m witness verify` recomputes all 265 timestamps from their positions and compares them
to the ones printed in the source corpus. It reproduces every one.

## What it does

    python -m witness watch      # forward: dates arriving, and ones that just passed
    python -m witness backfill   # backward: past nodes the ledger left silent
    python -m witness feed       # sideways: the recent world, placed against the ledger by date

All three end the same way: sourced findings appended to `findings/findings.jsonl`, each one
placed in a band, and `reports/WITNESS.md` rewritten.

**`watch`** researches nodes at or behind today's date. A node whose date is still ahead cannot
be witnessed — nothing has happened there yet — so the horizon is reported but not researched.

**`backfill`** takes the past nodes the ledger left silent, oldest first. Only **3** past nodes
carry no evidence at all — BB-004, BB-008 and BB-134. (34 nodes are empty in the workbook, but 31
of those are future-dated and cannot hold evidence yet.) The pool worth working is reached with
`--include-thin`: the **225** past nodes that have context but no exact-date event.

**`feed`** searches the recent world with no node in hand, so the world is read on its own terms;
placement happens afterwards, in code, by date. Most events land on no node, and that is the
expected result.

## The edge set

The positions are not only a sequence. Each of the **400** BB keys names its successors with a
stated gap. With the default predecessor rule below, that makes **704** edges in a directed graph:
one root, **−147.6** (the Altair position, 1974-12-01), one sink, **212.4**, and no cycles. The widest branching is
at **0.00** — the epoch itself, 2015-04-30 — which fans out to eighteen successors. The most
converged-on key is **24.41**, with seven predecessors.

The edge set splits into a **backbone** of **399** edges joining each key to the next in position
order, and **305 long-range edges** skipping over that spine. `witness edges` reports the split.

### The default predecessor rule

A key's immediate predecessor is, by default, the key standing temporally just before it. So
consecutive positions are joined whether or not the workbook spells the edge out, and the backbone
is complete by construction.

Three edges come from the rule rather than from the file, and all three sit in the epoch knot the
merged row damaged:

| Implied edge | Gap | Span |
|---|---|---|
| `−1.916 → −0.18` | 1.736 | 2014-10-20 → 2015-04-12 |
| `0.0 → 0.18` | 0.18 | 2015-04-30 → 2015-05-18 |
| `0.18 → 0.33` | 0.15 | 2015-05-18 → 2015-06-02 |

The first of those gives −0.18 its predecessor, so the graph has one root again rather than two.

Derived edges are never counted as something the ledger said: they carry `stated = False`, print
as *implied by the default predecessor rule*, and show dashed and marked *(implied)* in the page.
`witness edges --stated-only` drops them and reports the graph exactly as the workbook states it —
701 edges, a 396-edge backbone, two roots.

    python -m witness edges                      the graph and its anomalies
    python -m witness edges --from 0.0 --depth 1 walk forward from a key
    python -m witness edges --from -147.6 --chain follow one path to the sink

The graph runs over the **399 keys**, not the 265 nodes: a node is attached to the key standing at
its moment, and 212 keys are carried by a node. `Node.successors` gives the successors of the key
a node's analog is carried by — the distinction is kept rather than collapsed.

**Four disputed gaps are preserved, not corrected.** On four edges the stated gap and the
difference between the two keys disagree — including `23.41 → 29.528`, stated 3.6 against an
implied 6.118, which is the row the parable itself printed in its flagged-weights table. The
parable preserved and flagged these because reading every weight as elapsed time would need
clarification of what the weight means; this repository keeps both numbers and marks the edge
`gap disputed` rather than choosing one.

## Errata

The vendored workbook is never edited. It stays the source of record, and corrections to it are
declared in `data/errata.json` — each with its evidence, its cost and an `applied` flag — and
applied when the workbook is read. `witness edges` prints the ones in force.

**E-001-split-0.18.** One row carried two keys. Both **−0.18** (2015-04-12, eighteen days before
the epoch) and **0.18** (2015-05-18, eighteen days after it) exist in their appropriate positions;
the merged workbook collapsed them into a single row labelled 0.18, which then held both keys'
successor edges and sat in −0.18's place in the ordering.

Separated, everything reconciles. `−0.18 → 0.0` states a gap of 0.18 and implies 0.18;
`0.18 → 1.62` states 1.44 and implies 1.44; the inbound `−1.916 → 0.18` states 2.096 and implies
2.096. The two strands divide along the same line as the edges: *Lens Vesicle, Nasal Pit, Hand
Plate* appears only on that row and on 0.00, so it ends at 0.00 — the `−0.18 → 0.0` edge; *Nasal
Pits move ventrally, Auricular Hillocks, Foot Plate* continues on 0.33, 0.8 and 1.62 — the
`0.18 → 1.62` edge.

The graph's only backward edge and its only ordering violation both came from the collapse, and
both disappear. One consequence is recorded rather than hidden: the inbound edge belongs to 0.18,
so the source states no edge into −0.18. The default predecessor rule supplies one,
`−1.916 → −0.18`, and the graph keeps its single root; `--stated-only` shows the two-root form.

The edges reach the agent as context, never as a target: a node's brief names what the ledger says
comes next, explicitly marked as not a prediction to confirm and not something to search for. The
research is still about one date.

## The bands

A finding's band is computed in code from two dates — never taken from the model's sense of how
close the match felt.

| Band | Meaning |
|---|---|
| `exact` | the event's own date is the node's date, to the day |
| `within_7d` | one to seven days apart |
| `context_8_30d` | eight to thirty days apart, wider context only |
| `outside` | further than thirty days, marked as such |
| `month-precision`, `year-precision` | the source gave no day; no offset is claimed |

These are separate categories and are never merged. A wider band is not a weaker version of an
exact match — it is a different kind of claim.

## What it is told it may not do

`witness/prompts.py` carries the ledger's own cautions as standing instructions. The short form:
every finding needs a date and a source URL; state the precision you actually have; a same-day
match across timezones is not a same instant; proximity is not meaning; **nothing found is a
valid result**; and report what happened, not what it portends.

The agent's failure mode is not being wrong — it is being agreeable. A quiet run that appends
nothing is a successful run.

## The browser page

Published, and openable on a phone: **https://claude.ai/artifact/LcaxFfw5pepitte1YW4gfs**
(private to the account that published it until shared).

`web/index.html` is one self-contained file with the ledger and the findings baked in. It opens
in Firefox or Chrome on Android, Safari or Chrome on iOS, or any desktop browser — from the
filesystem, off a USB stick, or any static host. No server, no network, no build step.

    python -m witness build-web     # rebuild it after a run

The spine is the axis itself: positions on the rail, a *you are here* marker at today's date,
past above and still-ahead below. Tap a position for its analog, its chapter, the evidence
already on file and what the witness found. Search and filter by witnessed / silent / still
ahead / exact-date. A position's successors are listed under it and can be followed — tapping one
jumps to the position that carries that key.

## Running it

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...

    python -m witness verify              # no API key needed
    python -m witness nodes --horizon 400 # no API key needed
    python -m witness watch --dry-run     # builds the prompts, calls nothing
    python -m witness watch --limit 2     # this one spends money

Reading the ledger — `verify`, `nodes`, `render`, `build-web` — never calls the API and does not
need the `anthropic` package installed.

Every researching mode accepts `--dry-run` first. Use it. Each node costs two calls to
`claude-opus-5`: one search pass with the server-side `web_search` tool, one extraction pass with
no tools that turns the notes into validated records. Raw research notes are kept under
`runs/raw/` so any finding can be traced back to the text it came from.

`--today YYYY-MM-DD` stands the witness at another date, which is how you test `watch` against a
node date that has not arrived yet.

## On a schedule

`.github/workflows/witness.yml` runs `watch` weekly, rebuilds the report and the page, and
commits anything new. It needs an `ANTHROPIC_API_KEY` repository secret and is set to
`workflow_dispatch` as well, so the first run can be a manual one you watch.

## Layout

    witness/axis.py      the time axis, and the band rules
    witness/graph.py     the successor edges, their integrity and their anomalies
    witness/ledger.py    reading the workbook into objects
    witness/prompts.py   what the witness is told, and forbidden to do
    witness/research.py  the two-phase Claude layer: search, then structure
    witness/modes.py     watch / backfill / feed
    witness/store.py     append-only findings, never rewritten
    witness/render.py    reports/WITNESS.md
    witness/web.py       the single-file browser page
    findings/            findings.jsonl and runs.jsonl — the record
    reports/WITNESS.md   the standing document

## Standing cautions

Carried from the workbook's own Method sheet, and they hold for everything this agent produces:

- The bands are a research convention of the parable and ledger, not a discovered property of
  SFO-BB.
- Source event dates often use local calendars while SFO timestamps are UTC, so a same-day match
  does not establish an exact matching instant.
- Historical proximity and semantic fit are distinct: a date match can be exact while its
  developmental interpretation is weak.
- The stated analog is the supplied developmental framework. Historical coincidence does not
  validate causation and does not predict superintelligence.
- Everything in `findings/` was written by a language model with web search. Each finding carries
  its own source and confidence. They are research notes, not a record.
