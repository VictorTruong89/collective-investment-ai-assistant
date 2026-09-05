"""The source ports — declared by the consumer, named for what it needs (CA-5, CA-6).

**CA-5** requires a port where a boundary has already changed once. This one
qualifies twice over: yfinance was removed outright, and EDGAR/FMP precedence
was *reversed* on a measured TTM defect (MU, 71 %). Both should have touched one
adapter and zero analytical domains.

★ The Protocols are named `PriceHistory` and `FundamentalFacts`, not
`FMPClientInterface`. A port named after its implementation has inverted
nothing — it has renamed the coupling.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

import pandas as pd


class Transport(Protocol):
    """The HTTP boundary, injected so every test is hermetic by construction.

    Returns `(status, body)`. The status is not raised on here because §5A.2's
    three meanings of `402` are decided by the caller with the parameters in
    hand, and a transport that raised would throw that context away.
    """

    def get(self, url: str, params: dict, headers: dict, timeout: float) -> tuple[int, str]:
        ...


class PriceHistory(Protocol):
    """Raw OHLCV plus the events needed to adjust it (DE-27)."""

    def raw_prices(self, ticker: str, start: date, end: date) -> pd.DataFrame: ...

    def splits(self, ticker: str) -> list: ...

    def dividends(self, ticker: str) -> list: ...


class FundamentalFacts(Protocol):
    """Period-level financials with their knowability dates (DE-21)."""

    def facts(self, ticker: str, period_type: str) -> list: ...


class FilerClassifier(Protocol):
    """§5.1 — which case a ticker is, decided once at ingest by filer class."""

    def filer_class(self, ticker: str) -> str: ...
