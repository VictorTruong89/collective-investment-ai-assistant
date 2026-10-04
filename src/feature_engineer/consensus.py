"""The arithmetic over published sell-side consensus — one definition, D-02's.

`L3` §2.1p item 5 (2026-10-01). `src/fundamental/bundle/consensus.py` filters and
counts what analysts PUBLISHED as of a date; the two numbers it reports that are
computed rather than counted live here, because AC-1.40 / RA-45 forbid D-01 a
second definition of D-02's arithmetic.

⚠ FE-21 is not touched: the inputs are third-party market data from FMP (`grades`,
`price-target-news`, `earnings`), not the output of either analyst seat.
"""

from __future__ import annotations

import statistics


def target_spread(values) -> dict:
    """`n`, `median`, `low`, `high` of a set of price targets; all `None` when empty."""
    values = list(values)
    if not values:
        return {"n": 0, "median": None, "low": None, "high": None}
    return {"n": len(values), "median": statistics.median(values),
            "low": min(values), "high": max(values)}


def eps_surprise_pct(estimated, actual) -> float | None:
    """(actual − estimate) / |estimate| × 100, to 3 dp. `None` when either side is
    missing or the estimate is 0 — a surprise over a zero estimate is undefined, and
    a plausible-looking number in its place would be P5's invented value."""
    if estimated in (None, 0) or actual is None:
        return None
    return round((actual - estimated) / abs(estimated) * 100, 3)
