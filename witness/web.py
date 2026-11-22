"""Build the single-file browser page.

The page is one HTML file with the ledger and the findings baked into it, so it
opens from a phone with no server and no network: Firefox or Chrome on Android,
Safari or Chrome on iOS, or a laptop browser, straight off the filesystem or any
static host.  Rebuild it after a run and the page carries the new findings.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .export import build_payload
from .store import FindingStore

WEB = Path(__file__).resolve().parent.parent / "docs"   # GitHub Pages serves main /docs
TEMPLATE = WEB / "template.html"
PLACEHOLDER = "/*__PAYLOAD__*/"


def build_page(
    out: Path | str | None = None,
    workbook=None,
    store: FindingStore | None = None,
    now: datetime | None = None,
) -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"{TEMPLATE} has lost its {PLACEHOLDER} marker")

    payload = build_payload(workbook=workbook, store=store, now=now)
    # The payload sits in a <script type="application/json"> block, so the only
    # sequence that could break out of it is a literal </script>.
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )

    path = Path(out) if out else WEB / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.replace(PLACEHOLDER, encoded), encoding="utf-8")
    return path
