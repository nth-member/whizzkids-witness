# Handover

Written 2026-09-20, for whoever picks this up next — including a future session with no memory of
building it. `README.md` documents the method; this file is state, history, and the reasoning
behind decisions that would otherwise look arbitrary.

---

## 1. What exists

Two things, in two places.

**`~/whizzkids-witness`** — a repository, pushed to `https://github.com/nth-member/whizzkids-witness`
(private). It is a witness to **one slice** of REVOTT: the one anchored at Y = 24.50, sampled at
the 265 positions that have reachable real-world targets. It researches what actually happened at
those dates, with sources, and records where it found nothing.

**`~/revott`** — a plain tree, not a repository, holding other slices instantiated across the whole
400-key domain with no real-world attachment:

    ~/revott/
    ├── instances/  again-born.json  circumspection.json
    └── web/        again-born.html  circumspection.html

The generator  ---  e.g. (((((100)×((85.32)+(0)))+(100×((32.68)+(0÷35)))+(((14160))+(0÷7)))×(48.3÷17640))+5849+(391÷420)−3880)  --- for those slices currently lives inside `whizzkids-witness` (`witness/bare.py`,
`witness/axis.py`'s instance loader, `data/revott_readings.json`). That is a known structural wart
— machinery belonging to all slices owned by one slice's project. Splitting it into a `revott`
package was offered and deferred until a third slice justified it. There are now three.



---

## 2. The corpus, and what was learned about it today

Source files live in `~/pdp-causal-agent/claude_code_outputs/nth_agent_instances/`. The workbook is
vendored into the repo at `data/SFO_BB_analog_x_computing_events_enriched.xlsx` and **is never
edited** — corrections go in `data/errata.json`.

**The domain is 400 keys, not 265 nodes.** The 265 are where this slice was sampled. The code said
otherwise for most of today; `verify` now prints `sampled: 265 positions of 400 keys`.

**The axis is a gauge, not a law.**

    timestamp = epoch + days_per_unit × position

Both constants are a choice. The corpus carries **eleven named readings** over the same positions
at four scales — 3500D, 2800D/23, 100D, yG — extracted to `data/revott_readings.json`, complete on
all 265 positions. This implementation traverses the 100D scale on the raw position.

**What fixes a slice's zero is its Ztp**, given by the REVOTT gauge expression with a parameter Y:

    (((((100)×(Y))+(100×0)+(14160))×(48.3÷17640))+5849+(391÷420)−3880)

`48.3/17640` reduces to `23/8400`. The year unit implied throughout is `8400/23 = 365.2174` days.
Three slices are declared:

| slice | Y | Ztp | epoch | keys |
|---|---|---|---|---|
| whizz-kids | 24.50 | 112863/56 = 2015.4107… | 2015-04-30T11:28:41.739Z | 265 sampled of 400 |
| again-born | 82.80 | 853177/420 = 2031.3738… | 2031-04-16T11:28:41.739Z | 400 |
| circumspection | 85.32 | 2133667/1050 = 2032.0638… | 2031-12-24T11:28:41.739Z | 400 |
| exe-tpdp | 34.918 | 84767057/42000 = 2018.2633… | 2018-03-07T06:40:41.739Z | 400 |

Separations between slices are exact, the 23s cancelling: whizz-kids→again-born 5830 days,
whizz-kids→circumspection 6082 days, again-born→circumspection 252 days.

**None of these is a child of another.** They are siblings, each anchored by its own gauge.
whizz-kids is not the reference frame; it is simply the slice with evidenceable targets. An earlier
version of the instance files framed again-born as derived, and that was wrong.

**Y need not be a key.** 24.50 and 85.32 are not members of the 400-key domain; 82.80 and 34.918
are. 85.32 is a node position in the whizz-kids sampling (BB-259, attached to key 82.80).

**A separation need not be a whole number of days.** The exe-tpdp slice sits 1041.8 days from the
24.50 slice because Y = 34.918 carries three decimals. Under the borrowed instant that fraction
shifts its time of day to 06:40:41.739Z. This is the sharpest place the missing year-to-instant
convention bites.

**The successor graph.** 400 keys, 704 relations: a **backbone** of 399 — each key to the one
immediately next to it in time, which holds by default whether or not the workbook writes it down
— and **305 long-range** stated edges skipping over it. One root (−147.6), one sink (212.4),
acyclic. Widest branching at 0.00 with 19 successors; most converged-on is 24.41 with 7.
Three backbone links are not written down: `−1.916 → −0.18`, `0.0 → 0.18`, `0.18 → 0.33`.
`witness edges --stated-only` shows the workbook alone: 701 edges, 396-link backbone, two roots.

**Four disputed gaps** remain preserved, not corrected — the stated gap and the difference between
the keys disagree, including `23.41 → 29.528` (stated 3.6, implied 6.118), which the parable itself
printed in its flagged-weights table.

**One erratum is in force.** `E-001-split-0.18`: one workbook row carried two keys. Both **−0.18**
(2015-04-12) and **0.18** (2015-05-18) exist, eighteen days either side of the epoch; the merge
collapsed them into a single row labelled 0.18 which held both keys' successor edges and sat in
−0.18's place in the ordering. Separated, every gap reconciles and the graph's only backward edge
and only ordering violation both disappear. Declared in `data/errata.json` with its evidence;
setting `applied: false` returns every view to the file as it stands, which is tested.

---

## 3. Findings so far

Four, all researched in a Claude Code session with web search and ingested — **no API key has ever
been used**. All three previously silent past nodes are now witnessed.

| node | node date | found | offset | band | source tier |
|---|---|---|---|---|---|
| BB-004 | 2002-07-07 | Apple acquires Emagic | −6d | `within_7d` | in the ledger's own sources |
| BB-008 | 2004-06-26 | US-CERT advises abandoning Internet Explorer | +2d | `within_7d` | beyond |
| BB-134 | 2019-08-05 | **Cloudflare terminates 8chan** | same day | `exact` | beyond |
| BB-134 | 2019-08-05 | Apple suspends Siri grading | −3d | `within_7d` | beyond |

**BB-134 is the instructive one and must not be tidied.** The exact match — Cloudflare's own
timestamped post — has the *weakest* developmental fit (that chapter is "Perception becomes a
developer platform"). The item that fits the chapter closely is three days off. Both are recorded
with that stated plainly. This is the case the workbook's own method warns about.

**One claim was dropped rather than recorded:** a chronology dating Microsoft's home routers to
2002-07-11, which Microsoft's own newsroom puts at 2002-09-19.

**No intervals witnessed.** 290 closed long-range edges are unresearched.

**No control has been run.** `reports/WITNESS.md` says so in place of the comparison table.

---

## 4. The three copies, and what updates what

| | role | updates |
|---|---|---|
| `~/whizzkids-witness` | working copy | `witness ingest` rewrites findings, `reports/WITNESS.md` and `docs/index.html` |
| GitHub, private | the record: history and backup | manual `git push` |
| claude.ai artifacts | the view, readable on a phone | only a Claude session can republish |

| page | file | artifact |
|---|---|---|
| Whizz Kids Witness | `~/whizzkids-witness/docs/index.html` | https://nth-member.github.io/whizzkids-witness/ (and https://claude.ai/artifact/LcaxFfw5pepitte1YW4gfs) |
| AGAIN_BORN Axis | `~/revott/web/again-born.html` | https://claude.ai/artifact/XSJgeBToKMAQqTZ6FCysxr |
| CIRCUMSPECTION | `~/revott/web/circumspection.html` | https://claude.ai/artifact/Qxayq7szBAdAwjGXoBFEjS |
| EXE_TPDP | `~/revott/web/exe-tpdp.html` | https://claude.ai/artifact/U5NY8yA1p2RoGzZB4G3Ngm |

Republish by calling the Artifact tool on the file **with that URL**; publishing without it makes a
second, separate artifact. A republish needs `favicon` passed again if the tool cannot read the
current one.

**Anything in a page's embedded payload is readable by anyone the link is shared with**, via
view-source. The page is the corpus, in JSON. Share accordingly.

---

## 5. Identity and exposure

- All commits authored `nth-member <nth-member@users.noreply.github.com>`. Scoped with
  `git config --local`; the global config and every other repository are untouched.
- No real name, email or home path in any tracked file, and none in either published page. Verified.
- The org `nth-member` is owned by `okeyegonu`, whose membership is set Private.
- **The repo is private and should stay that way until after the viva.** The vocabulary here —
  `SFO-BB`, `TNLDY`, `dysi`, REVOTT, the parable — is unique and will appear in a named
  dissertation. Going public would undo the pseudonym by correlation, not by metadata, and public
  repos are announced through GitHub's event firehose rather than discovered.
- GitHub Pages on a private repo needs a paid plan, and a Pages site built from a private repo is
  itself public. The artifact links are the sharable surface.

---

## 6. The working loop, with no API key

    python -m witness prompt --node BB-xxx --rules       # print the prompt and the rules
    # research it — web search, honouring the rules that printed with it
    python -m witness ingest --node BB-xxx --json f.json --by "..." --note "..."
    git add -A && git commit -m "witness: BB-xxx" && git push
    # then ask a session to republish the artifact

`--edge SOURCE TARGET` for an interval. `--decoy N` files against a displaced date.

The JSON is a list of records with nine required fields: `event_title`, `event_date`,
`date_precision`, `what_happened`, `why_it_matters`, `source_url`, `source_name`, `confidence`,
`caution`. Missing any and the whole file is refused.

**Read-only commands, no key and no `anthropic` package needed:**

    python -m witness verify                          # axis, counts, graph, errata, next date
    python -m witness nodes --horizon 500             # dates still ahead
    python -m witness edges                           # the graph and its anomalies
    python -m witness edges --from 0.0 --depth 1      # walk out from a key
    python -m witness edges --from -147.6 --chain     # one path to the sink
    python -m witness edges --stated-only             # the workbook unaided
    python -m witness render                          # rewrite reports/WITNESS.md
    python -m witness build-web                       # rebuild the witness page
    python -m witness build-bare --instance <name>    # instantiate a slice into ~/revott

`WITNESS_INSTANCE=<name>` switches which slice the whole pipeline reads. `REVOTT_ROOT` moves the
slice tree.

**With a key** (`ANTHROPIC_API_KEY`, or `ant auth login`): `watch`, `backfill`, `feed`, `intervals`,
each taking `--dry-run` first. Measured cost is recorded per run from the API's own usage figures.
Estimated ~$0.36 a node, ~$0.58 an interval; weekly `watch` is near zero because only three node
dates arrive in the next twelve months.

---

## 7. What must not be relaxed

These are the reason the thing is worth anything.

1. **Bands are computed in code**, from two dates, in `modes.py` and `ingest.py`. Never taken from
   the model's sense of how close a match felt.
2. **Source tier is judged from the URL**, in `sources.py`. Never from the model's account of where
   it looked.
3. **Nothing found is a valid result.** A quiet run that appends nothing is a successful run. The
   failure mode of this agent is not being wrong, it is being agreeable.
4. **Append-only.** Findings are never rewritten. Corrections go in `data/errata.json` with their
   evidence. The workbook file is never edited.
5. **The exact / ±7d / 8–30d bands stay separate.** A wider band is not a weaker exact match.
6. **For an interval, the endpoints carry the claim, not the middle.** Over a gap of years
   something always happened in between; that is arithmetic, not correspondence.
7. **Say where the fit is weak.** BB-134 is the model: the strongest date has the weakest meaning,
   and the record says so.
8. **Unwritten is never presented as stated.** Backbone links the workbook omits are marked
   everywhere they appear, and `--stated-only` exists so the workbook can always be read unaided.
9. **No slice is the reference frame.** Each is anchored by its own Ztp. Relations between them are
   recorded as relations, never as derivations.

---

## 8. The next thing to do

**Run the control.** Nothing here can currently say whether a finding at a ledger date is worth
more than a finding at any date, because something notable happened within seven days of almost any
date since 1974. Without the comparison the findings are coincidences with no denominator, and
adding more makes it worse rather than better.

    python -m witness prompt --node BB-004 --decoy      # prints a displaced date and the offset
    python -m witness ingest --node BB-004 --decoy 170 --json f.json

Twenty ledger dates and twenty decoys, researched identically, is the smallest thing that can
produce a result. `WITNESS.md` prints the comparison once both populations exist. It costs nothing
through the ingest path. **If the two rates do not separate, that is the answer, and it is worth
having.**

This matters more now that the machinery can be re-anchored, not less. A structure this generative
will produce striking correspondences under almost any anchoring; the control is what distinguishes
that from a finding. Point it at deliberately wrong slices too.

---

## 9. Open and unresolved

- **The year-to-instant convention.** The gauge fixes Ztp as a decimal year, not an instant.
  REVOTT's own convention is not in the files read here, so `again-born` and `circumspection`
  epochs, and their time of day, were calibrated against the whizz-kids Ztp/instant pair. Declared
  under `unresolved` in each instance file. Supply the native convention and each epoch follows
  from its own Ztp alone.
- **Whether the named readings are slices.** The corpus carries `END_IE_PURPOSE_CIRCUMSPECTION.100D`
  and ten others over the same positions. Whether a named reading and a gauge-anchored slice of the
  same name are the same object is not established and is not assumed anywhere.
- **The live API path is unexercised.** Nothing has ever run against the Anthropic API. The request
  shapes in `witness/research.py` are written from documentation, not from a response.
- **Splitting the REVOTT machinery** out of `whizzkids-witness` into its own package.
- **Chains.** The strongest claim in the corpus is not a date or an edge but a sequence: the close
  of one edge as the open of the next. `graph.chain_to_sink` exists and nothing uses it.
- **The dedupe key includes the event title**, so the same event re-reported under a different
  title would file twice.

---

## 10. File map

    witness/axis.py       the axis, the instance loader, the band rules
    witness/ledger.py     reading the workbook into objects
    witness/graph.py      edges, degrees, cycles, walks, backbone, integrity
    witness/errata.py     declared corrections, applied at load
    witness/sources.py    the ledger's own cited domains; source tiering
    witness/prompts.py    what the witness is told, and forbidden to do
    witness/research.py   the two-phase Claude layer (unexercised)
    witness/modes.py      watch / backfill / feed / intervals
    witness/ingest.py     taking research in by hand, no API layer imported
    witness/decoy.py      the control
    witness/usage.py      measured cost
    witness/store.py      append-only findings, intervals, run log
    witness/render.py     reports/WITNESS.md
    witness/web.py        the witness page
    witness/bare.py       a slice instantiated into ~/revott
    witness/cli.py        every command

    data/SFO_BB_analog_x_computing_events_enriched.xlsx   the ledger, never edited
    data/errata.json                                      declared corrections
    data/revott_readings.json                             11 named readings × 265 positions
    data/instances/*.json                                 slice declarations
    findings/findings.jsonl                               node findings, append-only
    findings/intervals.jsonl                              interval findings, append-only
    findings/runs.jsonl                                   run log with measured cost
    reports/WITNESS.md                                    the standing document
