"""Filing index -> filer class. §5.1's routing decision, made once (DE-5.1).

★ **The classification is per TICKER, by filer class, decided once at ingest and
recorded on every row.** Never per-field, never per-call, never by whichever
source answered first. That is DE-5.1, and it is the rule that stops a series
from silently switching source mid-history — a discontinuity that looks like a
business event.

K-5: **ARM files 20-F and 6-K; no 10-K, no 10-Q.** That is case B, backed by
primary evidence in `data/fmp_dump/sec_filings_search_symbol__ARM.csv` rather
than by an assertion inherited from F9.
"""

from __future__ import annotations

from src.data_engine.errors import NoFundamentalSourceError
from src.data_engine.pit.models import EDGAR, FMP

CASE_A, CASE_B, CASE_C = "10-K/10-Q", "20-F/6-K", "none"

DOMESTIC_FORMS = frozenset({"10-K", "10-Q"})
FOREIGN_FORMS = frozenset({"20-F", "6-K", "40-F"})


def filer_class(form_types) -> str:
    """§5.1's three cases, from the set of forms a filer actually files.

    ⚠ Case A wins where both appear. A filer that has filed a 10-K at any point
    has discrete quarters available, and DE-5.3 forbids mixing sources within one
    ticker's series — so the better source takes the whole history rather than
    the recent part of it.
    """
    forms = {str(f).upper() for f in form_types}
    if forms & DOMESTIC_FORMS:
        return CASE_A
    if forms & FOREIGN_FORMS:
        return CASE_B
    return CASE_C


def route(ticker: str, form_types, *, has_cik: bool) -> str:
    """`edgar` | `fmp`, or raise (§5.1 case C, DE-13, AC-7.1/7.2/7.4).

    Case B routes to FMP **because 6-K interim reports are cumulative
    year-to-date, not discrete quarters** — ingesting them as quarterly injects
    2-3x inflated revenue, measured on ARM row by row.
    """
    if not has_cik:
        raise NoFundamentalSourceError(ticker, ["edgar (no CIK)"])
    case = filer_class(form_types)
    if case == CASE_A:
        return EDGAR
    if case == CASE_B:
        return FMP
    raise NoFundamentalSourceError(ticker, sorted({str(f) for f in form_types}) or ["<none>"])


def forms_from_submissions(payload: dict) -> list[str]:
    """The distinct form types in an EDGAR submissions response."""
    recent = ((payload.get("filings") or {}).get("recent") or {})
    return sorted(set(recent.get("form") or []))
