"""XBRL period parsing — where §5.1's cumulative-vs-discrete question is DECIDED.

```
Only Q1 matches, because for Q1 year-to-date IS the quarter.

  ARM 6-K/20-F cumulative vs FMP discrete, verified row by row:
      Q1  1,053M  vs  1,053M   1.00x
      Q2  2,188M  vs  1,135M   1.93x
      Q3  3,430M  vs  1,242M   2.76x
      FY  4,920M  vs  1,490M   3.30x
```

★ **This is why EDGAR wins.** Its facts carry explicit period **start AND end**,
so a discrete quarter is distinguishable from a cumulative year-to-date one **by
arithmetic**. FMP exposes only the period end and must guess — and it guessed
wrong on MU by 71 %.

⚠ It is the same defect class as `_cumulative_fys`, which understated MU's TTM
revenue by 41.5 % and moved its fair value by $379/share — and which survived
because a docstring asserting the wrong rule had a passing test built on real
production numbers.
"""

from __future__ import annotations

from datetime import date

from src.data_engine.pit.models import ANNUAL, QUARTERLY

#: A discrete quarter is 3 months. Filers' quarters run 84-98 days (13-14 weeks
#: on a 52/53-week fiscal calendar), so the window is generous on both sides and
#: still cannot admit a half-year.
QUARTER_DAYS = (80, 100)
#: A fiscal year, likewise: 52-53 weeks plus the leap-week filers.
ANNUAL_DAYS = (350, 380)


def classify_span(period_start: date, period_end: date) -> str:
    """`annual` | `quarterly` | `cumulative` — from the span, not from a label.

    ★ **`cumulative` is a first-class answer and the whole point.** A six- or
    nine-month span is neither a quarter nor a year, and ingesting it as either
    is what injects 2-3x inflated revenue. Returning a guess would make the
    error invisible; returning `cumulative` makes the caller decide.
    """
    days = (period_end - period_start).days
    if ANNUAL_DAYS[0] <= days <= ANNUAL_DAYS[1]:
        return ANNUAL
    if QUARTER_DAYS[0] <= days <= QUARTER_DAYS[1]:
        return QUARTERLY
    return "cumulative"


def is_discrete_quarter(period_start: date, period_end: date) -> bool:
    return classify_span(period_start, period_end) == QUARTERLY


def discrete_from_cumulative(cumulative_by_end: dict, period_end: date,
                             prior_end: date) -> int | None:
    """Q_n = YTD_n − YTD_{n−1}. The arithmetic EDGAR's two dates make possible.

    Returns None when either side is missing — a subtraction with one operand
    absent is not zero, and DE-14 says missing is null (never 0, never "").
    """
    now, before = cumulative_by_end.get(period_end), cumulative_by_end.get(prior_end)
    if now is None or before is None:
        return None
    return int(now) - int(before)


def unit_currency(unit_key: str) -> str | None:
    """The currency of an XBRL unit key, or None when the unit is not monetary.

    `USD` is monetary; `shares` and `USD/shares` are not. Returning None for the
    non-monetary ones keeps `shares_outstanding` out of the Money path, where
    CT-M.1 would demand a currency it does not have.
    """
    if unit_key == "shares" or "/" in unit_key:
        return None
    return unit_key if len(unit_key) == 3 and unit_key.isalpha() else None
