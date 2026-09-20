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

LEDGER_PREFERRED = "in the ledger's own sources"
BEYOND_LEDGER = "beyond the ledger's sources"
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
    """The preferred-sources paragraph given to the researcher."""
    domains = cited_domains(workbook_path)
    if not domains:
        return ""
    total = sum(count for _, count in domains)
    listed = ", ".join(domain for domain, _ in domains[:top])
    return f"""\
WHERE TO LOOK

The ledger cites {total} sources across {len(domains)} domains. In order of how
much it relies on them, the most used are:

  {listed}

That is one periodical archive carrying contemporary reporting, the primary
announcements of the organisations themselves, and a few computing-history
archives. Prefer those sources: a finding that rests on one of them sits on the
same footing as the evidence already in the ledger.

You are not restricted to them. Where the better source for a date lies
somewhere else -- a national archive, a standards body, a court record, a
regional publication, the original paper -- go there and cite it. A witness that
can only read what the ledger already reads cannot tell anyone anything new.

Prefer a primary source over reporting about it, and the date a thing happened
over the date it was written about. Where you have both, say which is which.
"""
