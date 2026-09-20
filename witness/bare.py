"""An instance instantiated without context.

The keys, dated on a given axis, and nothing else: no analog, no chapter, no
parable, no evidence, no findings.  Position and date are the whole content.

This exists because the axis is a gauge.  Re-anchoring it produces a different
instance over the same domain, and that instance has no design story attached to
it -- so it should not be rendered as though it had one.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from .axis import load_instance
from .ledger import load_keys

WEB = Path(__file__).resolve().parent.parent / "web"


def rows(instance_name: str):
    """Every key, dated on this instance's axis."""
    instance = load_instance(instance_name)
    keys = sorted(load_keys(), key=lambda r: r.key)
    out = []
    for record in keys:
        offset_days = instance.days_per_unit * record.key
        when = instance.epoch + timedelta(days=offset_days)
        out.append(
            {
                "key": record.key,
                "date": when.date().isoformat(),
                "stamp": when.isoformat().replace("+00:00", "Z"),
                "days": round(offset_days),
                "out": len(record.successors),
            }
        )
    return instance, out


def build_bare(instance_name: str, out_path: Path | str | None = None) -> Path:
    instance, data = rows(instance_name)
    first, last = data[0], data[-1]
    body = "\n".join(
        f'<tr><td class="k">{r["key"]}</td><td class="d">{r["date"]}</td>'
        f'<td class="o">{r["days"]:+,}</td><td class="s">{r["out"] or ""}</td></tr>'
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
.scroll{{overflow-x:auto;border-top:1px solid var(--rule)}}
table{{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:13px;
  font-variant-numeric:tabular-nums}}
th{{text-align:right;font-weight:500;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);padding:9px 10px;position:sticky;top:0;background:var(--ground)}}
th:nth-child(2){{text-align:left}}
td{{padding:6px 10px;border-bottom:1px solid var(--rule);text-align:right}}
.k{{color:var(--ink);font-weight:500}}
.d{{text-align:left;color:var(--ink-2)}}
.o{{color:var(--ink-3)}}
.s{{color:var(--accent);font-size:11.5px}}
tr.zero td{{background:var(--surface);border-bottom-color:var(--accent)}}
tr.zero .k{{color:var(--accent)}}
footer{{margin-top:26px;color:var(--ink-3);font-size:12px;line-height:1.6;max-width:64ch}}
</style>
<div class="wrap">
<h1>{instance.title}</h1>
<div class="sub">{len(data)} keys · scale {instance.scale} · axis only</div>

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

<input type="search" id="q" placeholder="filter by position or date…" autocomplete="off">
<div class="count" id="count"></div>
<div class="scroll">
<table>
<thead><tr><th>position</th><th>date</th><th>days from Ztp</th><th>succ</th></tr></thead>
<tbody id="rows">
{body}
</tbody>
</table>
</div>

<footer>
No analog, no chapter, no evidence and no correspondence is attached to these dates. This is the
key domain re-anchored on a different gauge, and nothing here claims that anything happened on any
of these days.
</footer>
</div>
<script>
(function(){{
  var rows = [].slice.call(document.querySelectorAll('#rows tr'));
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
