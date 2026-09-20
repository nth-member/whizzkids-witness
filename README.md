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
ahead / exact-date.

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
