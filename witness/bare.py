"""An instance instantiated without real-world attachment.

The keys carry their own developmental framework -- the somite counts, the
Carnegie-stage markers, the follicular phases, the hidden-count and year
notations.  That is latent in the domain and travels with it, so it is here.

What does not travel is everything obtained by going and looking: the evidence
items, the source links, the computing design-story chapters, the parable
glosses, the findings.  Those belong to the instance that was sampled against
the record, not to the keys.  Re-anchoring the gauge produces a different dating
of the same framework, and nothing has been checked about it.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from .axis import load_instance
from .graph import Graph
from .ledger import load_keys

WEB = Path(__file__).resolve().parent.parent / "web"


def rows(instance_name: str):
    """Every key, dated on this instance's axis."""
    instance = load_instance(instance_name)
    records = load_keys()
    graph = Graph(records)
    keys = sorted(records, key=lambda r: r.key)
    out = []
    for record in keys:
        offset_days = instance.days_per_unit * record.key
        when = instance.epoch + timedelta(days=offset_days)
        # The analog is the latent framework the keys carry; the strands are how
        # it is written, several at once, separated by pipes.
        strands = [
            part.strip(" .")
            for part in str(record.analog or "").split("||")
            if part.strip(" .")
        ]
        default = graph.default_edge(record.key)
        out.append(
            {
                "key": record.key,
                "date": when.date().isoformat(),
                "stamp": when.isoformat().replace("+00:00", "Z"),
                "days": round(offset_days),
                "strands": strands,
                "out": len(record.successors),
                "next": default.target if default else None,
            }
        )
    return instance, out


def build_bare(instance_name: str, out_path: Path | str | None = None) -> Path:
    instance, data = rows(instance_name)
    first, last = data[0], data[-1]
    def esc(text: str) -> str:
        return (
            str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

    body = "\n".join(
        '<article class="row">'
        f'<div class="rail"><span class="k">{r["key"]}</span>'
        f'<span class="d">{r["date"]}</span>'
        f'<span class="o">{r["days"]:+,}d</span></div>'
        '<div class="body">'
        + (
            "".join(f'<span class="strand">{esc(s)}</span>' for s in r["strands"])
            or '<span class="none">no text on this key</span>'
        )
        + (
            f'<span class="succ">→ {r["next"]}'
            + (f' · {r["out"]} stated' if r["out"] else "")
            + "</span>"
            if r["next"] is not None
            else '<span class="succ">sink</span>'
        )
        + "</div></article>"
        for r in data
    )
    gauge = instance.gauge
    html = f"""<title>{instance.title} Axis</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>
:root{{--ground:#f4f4f2;--surface:#fff;--ink:#16181a;--ink-2:#565d63;--ink-3:#868d93;
  --rule:#dcdedd;--accent:#7a4bd6;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  --sans:'IBM Plex Sans',system-ui,sans-serif;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --ground:#0f1113;--surface:#15181b;--ink:#e8eaec;--ink-2:#a2abb2;--ink-3:#727b82;
  --rule:#262b2f;--accent:#b79dfa;}}}}
:root[data-theme="dark"]{{--ground:#0f1113;--surface:#15181b;--ink:#e8eaec;--ink-2:#a2abb2;
  --ink-3:#727b82;--rule:#262b2f;--accent:#b79dfa;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:15px}}
.wrap{{max-width:780px;margin:0 auto;padding-inline:16px;padding-block:36px 64px}}
h1{{font-family:var(--mono);font-size:clamp(20px,5vw,30px);font-weight:500;letter-spacing:-.01em;
  margin:0 0 6px}}
.sub{{color:var(--ink-3);font-family:var(--mono);font-size:12px;letter-spacing:.04em;
  text-transform:uppercase;margin-bottom:22px}}
.gauge{{background:var(--surface);border:1px solid var(--rule);border-radius:4px;padding:13px 14px;
  font-family:var(--mono);font-size:11.5px;color:var(--ink-2);overflow-x:auto;line-height:1.7}}
.gauge b{{color:var(--accent);font-weight:500}}
.gauge .exp{{white-space:nowrap;display:block;margin-bottom:8px;color:var(--ink)}}
.facts{{display:flex;flex-wrap:wrap;gap:0;margin:18px 0 0;border:1px solid var(--rule);
  border-radius:4px;background:var(--surface);overflow:hidden}}
.fact{{flex:1 1 120px;padding:11px 13px;border-right:1px solid var(--rule)}}
.fact:last-child{{border-right:0}}
.fact b{{display:block;font-family:var(--mono);font-size:17px;font-weight:500;
  font-variant-numeric:tabular-nums}}
.fact span{{font-size:11px;color:var(--ink-3)}}
input{{width:100%;margin-top:22px;font-family:var(--mono);font-size:14px;color:var(--ink);
  background:var(--surface);border:1px solid var(--rule);border-radius:3px;padding:9px 11px}}
input:focus-visible{{outline:2px solid var(--accent);outline-offset:1px}}
.count{{font-family:var(--mono);font-size:11.5px;color:var(--ink-3);margin:10px 0 4px}}
.rows{{border-top:1px solid var(--rule)}}
.row{{display:grid;grid-template-columns:96px 1fr;gap:0;border-bottom:1px solid var(--rule)}}
.rail{{padding:10px 12px 10px 0;text-align:right;font-family:var(--mono);font-size:11.5px;
  font-variant-numeric:tabular-nums;line-height:1.5}}
.rail .k{{display:block;color:var(--ink);font-weight:500;font-size:12.5px}}
.rail .d{{display:block;color:var(--ink-2)}}
.rail .o{{display:block;color:var(--ink-3);font-size:10.5px}}
.row .body{{padding:10px 0 10px 14px;border-left:1px solid var(--rule);min-width:0}}
.strand{{display:block;font-size:13.5px;color:var(--ink);line-height:1.5}}
.strand + .strand{{color:var(--ink-2);margin-top:2px}}
.none{{display:block;font-size:13px;color:var(--ink-3);font-style:italic}}
.succ{{display:block;font-family:var(--mono);font-size:10.5px;color:var(--accent);margin-top:5px;
  letter-spacing:.03em}}
.row.zero{{background:var(--surface)}}
.row.zero .rail .k{{color:var(--accent)}}
footer{{margin-top:26px;color:var(--ink-3);font-size:12px;line-height:1.6;max-width:64ch}}
</style>
<div class="wrap">
<h1>{instance.title}</h1>
<div class="sub">{len(data)} keys · scale {instance.scale} · framework only, nothing checked</div>

<div class="gauge">
  <span class="exp">{gauge.get("expression", "")}</span>
  Ztp = <b>{gauge.get("value", "")}</b> = <b>{gauge.get("decimal", "")}</b><br>
  timestamp = {instance.epoch.isoformat().replace("+00:00", "Z")} + {instance.days_per_unit:g} days × position
</div>

<div class="facts">
  <div class="fact"><b>{len(data)}</b><span>keys</span></div>
  <div class="fact"><b>{first["date"][:4]}</b><span>first, {first["key"]}</span></div>
  <div class="fact"><b>{last["date"][:4]}</b><span>last, {last["key"]}</span></div>
  <div class="fact"><b>{(last["days"] - first["days"]):,}</b><span>days spanned</span></div>
</div>

<input type="search" id="q" placeholder="filter by position, date or framework text…" autocomplete="off">
<div class="count" id="count"></div>
<div class="rows" id="rows">
{body}
</div>

<footer>
The text on each key is the developmental framework the domain carries — somite counts and
Carnegie-stage markers, follicular phases, the hidden-count and year notations — written in
several strands at once. It travels with the keys and is here unchanged.<br><br>
What is not here is anything obtained by going and looking: no evidence, no sources, no design-story
chapter, no correspondence. Nothing on this page claims that anything happened on any of these
days. It is an independent slice of REVOTT, anchored by its own Ztp, carrying the same framework
from its own zero.
</footer>
</div>
<script>
(function(){{
  var rows = [].slice.call(document.querySelectorAll('#rows .row'));
  rows.forEach(function(r){{ if (r.querySelector('.k').textContent.trim() === '0.0')
    r.classList.add('zero'); }});
  var count = document.getElementById('count');
  function tally(n){{ count.textContent = n + ' of ' + rows.length + ' keys'; }}
  tally(rows.length);
  document.getElementById('q').addEventListener('input', function(){{
    var q = this.value.trim().toLowerCase(), shown = 0;
    rows.forEach(function(r){{
      var hit = !q || r.textContent.toLowerCase().indexOf(q) !== -1;
      r.hidden = !hit; if (hit) shown++;
    }});
    tally(shown);
  }});
}})();
</script>
"""
    path = Path(out_path) if out_path else WEB / f"{instance.name}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path
