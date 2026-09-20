# Handover

For whoever picks this up next, including a future session with no memory of building it.

## What this is

A witness to the SFO-BB ledger. The ledger (`data/SFO_BB_analog_x_computing_events_enriched.xlsx`)
places 265 positions on one time axis and attaches to each a stated developmental analog and a
chapter of computing's design story. This repository researches what actually happened at those
dates, with sources, and records where it found nothing.

Read `README.md` for the method. This file is only about state and the working loop.

## Where things stand — 2026-09-20

- **Pushed** to `https://github.com/nth-member/whizzkids-witness`, private, 8 commits.
- **Identity**: all commits authored `nth-member <nth-member@users.noreply.github.com>`. The
  pseudonym is scoped to this repo only — `git config --local`, global config untouched. No real
  name, email or home path in any tracked file. Keep it that way.
- **Findings**: 4, from the 3 previously silent past nodes.
  - BB-004 (2002-07-07) — Apple acquires Emagic, −6d, `within_7d`. Fit to the chapter is weak and
    the record says so.
  - BB-008 (2004-06-26) — US-CERT advises abandoning Internet Explorer, +2d, `within_7d`.
  - BB-134 (2019-08-05) — Cloudflare terminates 8chan, **exact** to the day in UTC, and the weakest
    fit of the four. Apple suspends Siri grading, −3d, fits the chapter closely and does not match
    the date. That pairing is deliberate evidence, not an untidiness.
- **Intervals**: none witnessed. 290 closed long-range edges are unresearched.
- **Control**: none run. `WITNESS.md` says so in place of the comparison table. This is the most
  important open item — see below.
- **No API key** has ever been used. Nothing here has run against the live Anthropic API; the
  request shapes in `witness/research.py` are unexercised.

## The three copies

| | role | updates |
|---|---|---|
| `~/whizzkids-witness` | working copy | `witness ingest` rewrites findings, `reports/WITNESS.md` and `web/index.html` |
| GitHub, private | the record: history and backup | manual `git push` |
| claude.ai artifact | the view, readable on a phone | only a Claude session can republish it |

Artifact: https://claude.ai/artifact/LcaxFfw5pepitte1YW4gfs — republish by calling the Artifact
tool on `web/index.html` with that URL. Do not publish without the URL; that would make a second,
separate artifact.

Anything in the page's embedded payload is readable by anyone the link is shared with, via
view-source. The page is the corpus, in JSON. Share accordingly.

## The working loop, with no API key

    python -m witness prompt --node BB-xxx --rules     # print the prompt
    # research it — web search, honouring the rules that printed with it
    python -m witness ingest --node BB-xxx --json f.json --by "..." --note "..."
    git add -A && git commit -m "witness: BB-xxx" && git push
    # then republish the artifact

`--edge SOURCE TARGET` does the interval form. `--decoy N` files against a displaced date.

The JSON is a list of records with nine required fields: `event_title`, `event_date`,
`date_precision`, `what_happened`, `why_it_matters`, `source_url`, `source_name`, `confidence`,
`caution`. Missing any and the whole file is refused.

## What must not be relaxed

These are the reason the thing is worth anything. Do not let convenience erode them.

1. **Bands are computed in code**, from two dates, in `modes.py` and `ingest.py`. Never take a
   band from the model's sense of how close a match felt.
2. **Source tier is judged from the URL**, in `sources.py`. Never from the model's account of
   where it looked.
3. **Nothing found is a valid result.** A quiet run that appends nothing is a successful run. The
   failure mode of this agent is not being wrong, it is being agreeable.
4. **Append-only.** Findings are never rewritten. Corrections go in `data/errata.json` with their
   evidence, and the workbook file is never edited.
5. **The exact / ±7d / 8–30d bands stay separate.** A wider band is not a weaker exact match.
6. **Say where the fit is weak.** BB-134 is the model for this: the strongest date has the
   weakest meaning, and the record says so plainly.

## The next thing to do

**Run the control.** Nothing in this repository can currently say whether a finding at a ledger
date is worth more than a finding at any date, because something notable happened within seven
days of almost any date since 1974. Without the comparison, the findings are coincidences with no
denominator, and adding more of them makes the situation worse rather than better.

    python -m witness prompt --node BB-004 --decoy    # prints a displaced date and the offset
    python -m witness ingest --node BB-004 --decoy 170 --json f.json

Twenty ledger dates and twenty decoys, researched identically, is the smallest thing that can
produce a result. `WITNESS.md` prints the comparison once both populations exist.

If the two rates do not separate, that is the answer, and it is worth having.

## Open decisions

- **Public or private.** Currently private. Going public exposes the whole corpus permanently and,
  because the vocabulary here (`SFO-BB`, `TNLDY`, `dysi`, REVOTT, the parable) is unique and will
  appear in the author's named dissertation, would undo the pseudonym by correlation. The viva
  should decide this, not the convenience of a link.
- **Whether to get an API key at all.** The ingest path works without one. A key buys the
  unattended weekly run and speed, at roughly $0.36 a node and $0.58 an interval.
- **Chains.** The strongest claim in the corpus is not a date or an edge but a sequence: the close
  of one edge as the open of the next. `graph.chain_to_sink` exists and nothing uses it.
