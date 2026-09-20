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
    python -m witness intervals  # along the edges: what began at one end and closed at the other

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

The positions are not only a sequence, they are a directed graph. Two kinds of relation run over
the **400** BB keys:

- a **backbone** of **399** connections, each key to the one immediately next to it in time. This
  holds by default for every key, whether or not a successor cell records it; 396 are also written
  down in the workbook, 3 are not.
- **305 long-range** stated edges, which skip over the backbone.

**704** relations in total: one root, **−147.6** (the Altair position, 1974-12-01), one sink,
**212.4**, and no cycles. The widest branching is at **0.00** — the epoch itself, 2015-04-30 —
with nineteen successors. The most converged-on key is **24.41**, with seven predecessors.

    python -m witness edges                       the graph, its backbone and its anomalies
    python -m witness edges --from 0.0 --depth 1  walk forward from a key
    python -m witness edges --from -147.6 --chain follow one path to the sink
    python -m witness edges --stated-only         only what the workbook writes down

The three backbone links the workbook does not write down are `−1.916 → −0.18` (gap 1.736),
`0.0 → 0.18` (0.18) and `0.18 → 0.33` (0.15) — all three in the epoch knot that the merged row
below damaged. They are marked wherever they appear, so nothing unwritten is passed off as stated.
`--stated-only` drops them: 701 edges, a 396-link backbone, and −0.18 without a predecessor.

The graph runs over the **400 keys**, not the 265 nodes: a node is attached to the key standing at
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

## Along the edges

An edge is not a date, it is a claim about a span: that one position leads to another across a
stated gap. `witness intervals` tests it by looking for a single development that **began** at or
near the opening date and **concluded** at or near the closing date.

The same-day / ±7d / 8–30d bands do not apply to a span, so intervals have their own rules, and
they are stricter in one specific way: **the endpoints carry the claim, not the middle.** Over a
gap of years something always happened in between — that is arithmetic, not correspondence. Each
end is judged separately, by offset, in code.

| Shape | Meaning |
|---|---|
| `both_ends` | a development that starts at one end and finishes at the other |
| `one_end` | only the opening or only the closing is anchored |
| `span_only` | the duration matches, the endpoints do not align |
| `neither` | two dated events with no thread between them |

Long-range edges are tested first, because those are the ledger's own non-obvious claims — it is
asserting a relation between positions that are *not* adjacent. Backbone links only join
consecutive positions, so they assert much less; `--backbone` tests them anyway.

Candidates are ordered **shortest span first**: a coincidence across four days is expensive to
find, one across a decade is not. Of 305 long-range edges, 290 have closed and are unwitnessed;
the shortest are `−5.7342 → −5.7145` (2 days) and `24.41 → 24.447` (4 days). An edge whose closing
date is still in the future is never researched.

Interval findings live in `findings/intervals.jsonl`, separate from the dated correspondences,
because they are a different kind of claim and are not mixed in with them.

## Sources

The search is **not restricted**. The tool is left open so the witness can find what the corpus
never happened to favour — a witness that can only read what the ledger already reads cannot tell
you anything new.

But the ledger has a legible source discipline of its own: **1,074 citations across 56 domains**,
led by wired.com (the archive spine, queried by dated sitemap), then the primary announcements of
the organisations themselves — openai.com, deepmind.google, apple.com, arxiv.org, news.microsoft.com,
anthropic.com — and a few computing-history archives. That list is derived from the workbook at
run time, not hardcoded, and named to the researcher as preferred.

Every finding is then marked in code, from its URL, as resting **in the ledger's own sources** or
**beyond the ledger's sources**. As with the bands, that judgement is arithmetic on data, never
the model's account of where it looked.

Where the searches physically run is Anthropic's infrastructure: `web_search_20260209` is a
server-side tool, and which index sits behind it is not visible from here. `allowed_domains` /
`blocked_domains` are available on that tool if you later want the policy enforced rather than
preferred.

## Working it without an API key

The research is two prompts and a structured answer, so it does not have to be the agent that
does it. Print the prompt, run it in any Claude session, bring the answer back:

    python -m witness prompt --node BB-004 --rules      # the prompt, and the rules of evidence
    python -m witness ingest --node BB-004 --json f.json # take the answer in

Nothing is relaxed on the way in. The bands are still computed here from two dates, the source
tier is still judged from the URL, the store is still append-only, and the record says the finding
arrived this way — `mode: ingest`, with the session named — rather than from a run the agent made
itself. `witness ingest` imports nothing from the API layer, so it works on a machine with neither
credentials nor the `anthropic` package.

Edges work the same way: `--edge -5.7342 -5.7145`.

## The control

Something notable happened within seven days of almost any date since 1974. A finding at a ledger
date therefore means nothing on its own, and a report full of them means less, not more — the more
you look, the less you see. Only the difference between the ledger's dates and dates that are not
the ledger's carries information.

    python -m witness prompt --node BB-004 --decoy       # a stable displaced date
    python -m witness ingest --node BB-004 --decoy 170 --json f.json

A decoy is the same position researched under the same rules at a date displaced 120–900 days —
far enough that the 30-day window cannot overlap, near enough to stay in the same technological
era. The evidence already on file is stripped, because it belongs to the real date. Findings carry
their displacement, so the two populations can never be confused, and `WITNESS.md` prints the
comparison. Until a control exists, the report says so in place of the table.

## What a run costs

Runs record the API's own usage figures and what they cost at the rates in `witness/usage.py` —
tokens in and out, cache reads and writes, and searches at $10 per 1,000. Each run's measured
cost is printed when it finishes and stored on its `RunRecord`, so the numbers in any estimate can
be checked against what actually happened.

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
