# Behold what the whizz kids have wrought

*A witness to the SFO-BB ledger: what it claims, what the world actually did,*
*and where the days were quiet.*

Standing at **2026-09-20**.

## The ledger as it stands

- Nodes on the axis: **265**
- Axis check (timestamp = epoch + 100 days x position): **reproduces every timestamp**
- Nodes already carrying an exact-date event in the workbook: **9**
- Nodes carrying no evidence at all: **34**
- Nodes whose dates are still in the future: **31**

## Dates still to arrive

| Node | Position | Date | Stated analog |
|---|---|---|---|
| BB-235 | 42.0 | 2026-10-29 | LIGHT OF SEVEN DAYS — carried over from key 39.88 (2026-03-31), -2.12 in position (-212 da |
| BB-236 | 42.28 | 2026-11-26 | sanctuary cleansed (end) // land cleansed (end) |
| BB-237 | 43.2 | 2027-02-26 | Baby is now completely covered in Lanugo-Hair // land cleansed (end) |

## Against the control

**No control has been run.** Every finding below is at a date the ledger claims, and
nothing here says whether a date the ledger does *not* claim would have yielded as
much. Until that comparison exists, this is a list of coincidences without a
denominator. Run `witness prompt --node <id> --decoy` to start one.

## What the witness has found

**4 findings** across **3 nodes**.

| Band | Meaning | Findings |
|---|---|---|
| `exact` | same calendar day | 1 |
| `within_7d` | within seven days | 3 |

### BB-134 — 2019-08-05

*Stated analog:* 1T
  
*Design-story chapter:* 5. Perception becomes a developer platform

- **Cloudflare terminates service for 8chan** — 2019-08-05 (same day, `exact`)
  Cloudflare announced it was terminating 8chan as a customer, effective midnight Pacific that night, after the site's role in inspiring mass violence. The post is timestamped 2019-08-05T01:44:16Z.
  *Why it mattered:* An infrastructure provider, not a platform, decided what could remain reachable on the web, and said so publicly. It became a reference point for how far down the stack content decisions can be pushed.
  *Caution:* The date match is exact in UTC and the source is the company's own dated post, so the dating is as strong as it gets. The developmental fit is the weak part, and the strength of the date should not be allowed to carry it: this node sits in the chapter 'Perception becomes a developer platform', about machine senses being made available as reusable components, and an infrastructure provider withdrawing service from a website is not that. Exactly the case the ledger's own method warns about, where a date match is exact while its interpretation is weak.
  *Source:* [The Cloudflare Blog](https://blog.cloudflare.com/terminating-service-for-8chan/) — confidence: stated

- **Apple suspends the Siri grading programme** — 2019-08-02 (-3 days, `within_7d`)
  Apple suspended worldwide the practice of having contractors listen to and grade snippets of Siri recordings, after a Guardian report from a former grader described routinely hearing confidential material. Apple said it would review the programme and later let users opt in.
  *Why it mattered:* The human review behind machine perception became visible, and a vendor suspended a production quality-control pipeline over it. Google paused its Assistant reviews in the same period and Microsoft's Skype and Cortana review was reported days later.
  *Caution:* Three days before the node date, and it is secondary reporting of a statement Apple gave to press rather than a dated Apple release, so the day is the reporting day. Unlike the Cloudflare item this one does fit the chapter closely: speech perception offered as a platform feature, and the human labour underneath it. The pairing is worth noticing rather than hiding, since the item that fits the chapter is not the item that matches the date.
  *Source:* [Fast Company](https://www.fastcompany.com/90385310/apple-suspends-siri-grading-program-that-lets-contractor-listen-in-on-recordings) — confidence: reported

### BB-008 — 2004-06-26

*Stated analog:* 6.41048dysi...Pre-Adamites Tertiary-Stage Follices (Antral Phase 1)
  
*Design-story chapter:* 3. Social, mobile and cloud ecosystems

- **US-CERT advises abandoning Internet Explorer after the Download.Ject attack** — 2004-06-28 (+2 days, `within_7d`)
  After the Download.Ject (Scob) attack, in which compromised IIS servers silently installed a backdoor and keylogger on the machines of people merely viewing a web page, US-CERT took the unusual step of advising users to browse with something other than Internet Explorer, citing flaws in its zone security model, DHTML object model, MIME-type determination and ActiveX.
  *Why it mattered:* A national CERT telling the public to stop using the dominant browser made browser choice a security decision rather than a preference, and is commonly cited as part of what opened the ground for Firefox.
  *Caution:* This is the date the advice was reported, not necessarily the date CERT issued it; the underlying vulnerability note is the primary record and I have not read it directly. The attack itself ran roughly 21-25 June, so the episode straddles the node date rather than landing on it. Fit to the chapter is partial: it belongs squarely to 'privacy and control become design problems', but not to the 'social, mobile and cloud' half of the same chapter heading.
  *Source:* [The Register](https://www.theregister.com/2004/06/28/cert_ditch_explorer/) — confidence: reported

### BB-004 — 2002-07-07

*Stated analog:* 0.00dysi...=> SEVEN DAYS OF SEVEN DYSI COUNT
  
*Design-story chapter:* 2. The Internet becomes a shared Web

- **Apple acquires Emagic** — 2002-07-01 (-6 days, `within_7d`)
  Apple announced it had acquired Emagic, the German maker of the Logic professional music production software, which became a wholly owned division. Emagic's Windows product line was discontinued on 30 September 2002, moving Logic to the Macintosh alone.
  *Why it mattered:* It moved a professional creative application in-house and ended its cross-platform availability, the line of work that later produced GarageBand and Logic Pro. It is a platform-consolidation event rather than an internet one.
  *Caution:* Six days before the node date, so it is a proximity match, not a same-day one, and the press release is a US-dated corporate announcement against a UTC node timestamp. The developmental fit is weak and should not be talked up: this node sits in the chapter 'The Internet becomes a shared Web', about standards, linking and shared information environments, and an acquisition of music-production software is not that. Recorded because it is firmly dated and primary-sourced, not because it fits.
  *Source:* [Apple Newsroom](https://www.apple.com/newsroom/2002/07/01Apple-Acquires-Emagic/) — confidence: stated

## Where the days were quiet

Runs that looked and found nothing worth recording:

- `ingest-20260920T082605Z` (ingest): BB-004 2002-07-07: nothing on the day itself. One sourced item at -6d. A chronology entry claiming Microsoft home routers on 2002-07-11 was dropped: Microsoft's own newsroom dates that line to 2002-09-19.
- `ingest-20260920T082706Z` (ingest): BB-008 2004-06-26: nothing on the day; Download.Ject episode straddles it.
- `ingest-20260920T082707Z` (ingest): BB-134 2019-08-05: one exact-date item with weak fit, one close item with good fit.

## Standing cautions

These are the workbook's own, and they hold for everything above.

- The bands are a research convention of the parable and ledger, not a discovered
  property of SFO-BB. Same day, within seven days and 8–30 days are separate
  categories and are never merged here.
- Source event dates often use local calendars while SFO timestamps are UTC, so a
  same-day match does not establish an exact matching instant.
- Historical proximity and semantic fit are distinct: a date match can be exact
  while its developmental interpretation is weak.
- The stated analog is a supplied developmental and symbolic framework. Historical
  coincidence does not validate causation and does not predict superintelligence.
- An interval is not a dated correspondence. Its ends are judged separately, and the
  longer the span, the cheaper the coincidence: something always happened in the middle
  of a decade. Only the endpoints carry the claim.
- Findings below the heading above were written by a language model with web search.
  Each carries its own source and confidence. They are research notes, not a record.

*Last run: `ingest-20260920T082707Z` — ingest, 2 new findings, model claude-opus-5 (Claude Code session, WebSearch).*
