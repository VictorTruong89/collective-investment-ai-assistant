"""The universe, its CIK map, and the routing decision — DE-13, DE-5.1 (AC-7.4/7.6).

⚠ **QD-5 is open**: "where does the universe list live — a config file or a D-07
artifact?" §5A.1 shows `stock-list`, `financial-statement-symbol-list` and
`actively-trading-list` are all available, and a D-07 artifact built from them
beats a hand-kept config.

**Implemented here as config-backed**, because B2 needs a universe and QD-5's
answer changes only where the list comes FROM, not what it is. The loader is one
function; swapping it for an FMP-derived artifact is a change to
:func:`load_universe` alone.

★ **DE-36 is why the watchlist is a flag on the entry rather than a separate
list.** The calendar check covers the universe, not the watchlist: a name
excluded from the actionable slate still participates in cross-sectional
normalisation, so its unhandled split contaminates every other name's rank. Two
lists would make "the universe" ambiguous at exactly the call site where it must
not be.
"""

from __future__ import annotations

from pathlib import Path

from src.data_engine.errors import NoCikError, NoFundamentalSourceError
from src.data_engine.pit.models import UniverseEntry
from src.data_engine.src.edgar.submissions import CASE_C, filer_class, route
from src.data_engine.store.atomic import read_json


def build_entry(ticker: str, *, cik: str | None, form_types) -> UniverseEntry:
    """Decide the source ONCE, from the filer class (DE-5.1, AC-7.1, AC-7.2).

    ⚠ Case B (20-F/6-K) needs no CIK because it routes to FMP, so the CIK check
    is deliberately *after* the classification rather than a precondition of it.
    Reversing the two would fail every foreign private issuer for lacking
    something it does not use.
    """
    ticker = ticker.upper()
    case = filer_class(form_types)
    if case == CASE_C:
        raise NoFundamentalSourceError(ticker, sorted({str(f) for f in form_types}))
    if case != CASE_C and cik is None and case == "10-K/10-Q":
        raise NoCikError(ticker)
    source = route(ticker, form_types, has_cik=cik is not None or case == "20-F/6-K")
    return UniverseEntry(ticker=ticker, cik=cik, filer_class=case, source=source)


class Universe:
    """The membership list plus its routing. Immutable once built."""

    def __init__(self, entries) -> None:
        self._entries = {e.ticker: e for e in entries}

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, ticker: str) -> bool:
        return ticker.upper() in self._entries

    @property
    def tickers(self) -> list[str]:
        return sorted(self._entries)

    @property
    def watchlist(self) -> list[str]:
        return sorted(t for t, e in self._entries.items() if e.in_watchlist)

    def entry(self, ticker: str) -> UniverseEntry:
        """DE-13 / AC-7.4 — a ticker with no source FAILS THE RUN, named.

        It is not dropped, and it does not become a row of NaNs. The incident
        behind this: a LEFT JOIN silently dropped 7 of the 13 watchlist names
        from the training panel and they were scored with all 47 fundamental
        features NaN, with nothing saying so.
        """
        hit = self._entries.get(ticker.upper())
        if hit is None:
            raise NoFundamentalSourceError(ticker.upper(), ["<not in universe>"])
        return hit

    def source_of(self, ticker: str) -> str:
        return self.entry(ticker).source

    def assert_source_stable(self, ticker: str, rows_source) -> None:
        """DE-5.3 / AC-7.6 — one source per ticker, across the whole series.

        A series that silently switches source mid-history has a discontinuity
        that **looks like a business event** — which is worse than a gap, because
        a gap is visible and a fake inflection is not.
        """
        seen = sorted({str(s) for s in rows_source})
        expected = self.source_of(ticker)
        if seen not in ([expected], []):
            raise NoFundamentalSourceError(
                ticker.upper(),
                [f"series mixes sources {seen}, expected only {expected!r} (DE-5.3)"],
            )


def load_universe(path: str | Path) -> Universe:
    """Read the universe from JSON: `[{ticker, cik, form_types, watchlist}]`.

    Fails on the first unroutable ticker rather than collecting them, because
    DE-13 makes it a run failure either way and a partial universe is not a
    thing this system has a use for.
    """
    payload = read_json(Path(path))
    entries = []
    for row in payload:
        entry = build_entry(row["ticker"], cik=row.get("cik"),
                            form_types=row.get("form_types", []))
        entries.append(UniverseEntry(entry.ticker, entry.cik, entry.filer_class,
                                     entry.source, bool(row.get("watchlist", False))))
    return Universe(entries)
