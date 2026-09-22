"""Where the witness is pointed, and how its sources are judged.

The search is not restricted: the tool is left open so the witness can find
what the corpus never happened to favour, which is the only way it can tell
anyone anything they do not already have.

But the ledger has a source discipline of its own, and it is legible -- its 279
dated items carry 767 citations across 56 domains.  That list is derived from
the workbook here rather than written out by hand, named to the researcher as
preferred, and used afterwards to mark each finding's source as one the ledger
already relies on or one from beyond it.  The marking is done in code from the
finding's URL, never taken from the model's own account of where it looked.
"""

from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import openpyxl

from .ledger import DEFAULT_WORKBOOK

URL_PATTERN = re.compile(r"https?://[^\s'\")\,]+")

# Descriptive labels, not a ranking: they say where a finding's source sits
# relative to the ledger's existing citations, and nothing about its quality.
LEDGER_PREFERRED = "also cited by the ledger"
BEYOND_LEDGER = "not previously cited here"
UNSOURCED = "no usable url"


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except ValueError:
        return ""


@lru_cache(maxsize=4)
def cited_domains(workbook_path: str | None = None) -> tuple[tuple[str, int], ...]:
    """Every domain the ledger cites, with how often, most-cited first."""
    path = Path(workbook_path) if workbook_path else DEFAULT_WORKBOOK
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        counts: Counter[str] = Counter()
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if cell is None or "http" not in str(cell):
                        continue
                    for url in URL_PATTERN.findall(str(cell)):
                        domain = _domain(url)
                        if domain:
                            counts[domain] += 1
        return tuple(counts.most_common())
    finally:
        wb.close()


def preferred_set(workbook_path: str | None = None) -> set[str]:
    return {domain for domain, _ in cited_domains(workbook_path)}


def tier_for(url: str, workbook_path: str | None = None) -> str:
    """Judge one finding's source against the ledger's own.

    A subdomain of a cited domain counts as the same source: a citation of
    blog.google means google's own announcements are a source the ledger uses.
    """
    domain = _domain(url or "")
    if not domain:
        return UNSOURCED
    preferred = preferred_set(workbook_path)
    if domain in preferred:
        return LEDGER_PREFERRED
    if any(domain.endswith("." + known) for known in preferred):
        return LEDGER_PREFERRED
    return BEYOND_LEDGER


def preferred_block(workbook_path: str | None = None, top: int = 18) -> str:
    """The evidence policy given to the researcher.

    The ledger's own citations are no longer named as preferred.  A third of its
    positions rest on "a report was published that day", drawn overwhelmingly
    from one periodical archive that publishes every weekday -- which is true of
    almost any date in its range and so carries no information.  Naming those
    domains as preferred would have trained the witness to reproduce exactly
    that.
    """
    return """\
WHERE TO LOOK

Search openly. No publication is preferred over another, and a source is not
better for having been cited by this ledger before.

Prefer a primary record over reporting about it: a dated release, a filing, a
standards document, a court record, an archive holding the original. Prefer the
date a thing happened over the date it was written about, and where you have
both, say which is which.

Be wary of one kind of hit in particular. That a publication ran an article on a
given day is nearly always true of any day, and is not evidence that the day was
notable. Report an event because the event is dated, not because coverage of it
exists.
"""
