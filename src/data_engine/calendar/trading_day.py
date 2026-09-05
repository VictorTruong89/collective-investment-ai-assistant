"""D-07 DE-48 — is this date a US equity trading day?

★ **OR-7's migration, finally performed.** *"The calendar check belongs to D-07,
not here. `_is_market_open_et` currently lives in the inference entrypoint
(§1.5) and must move."* **QO-1 called it the cheapest of the ten misplaced
functions**, and it is what D-08's step 0 asks.

⚠ **It is a rebuild, not a port.** The legacy predicate was:

```python
if now.weekday() >= 5: return False
return (9*60+30) <= minutes <= (16*60)
```

★ **Weekday-only — no holiday calendar of any kind.** It returns `True` on
Christmas Day whenever Christmas falls on a Tuesday, and it answers *"is the
market open right now"* when D-08 needs *"was this DATE a session"*.
"""

from __future__ import annotations

from datetime import date

#: NYSE full closures. ⚠ **ADMITTED LIST** (CN-10): hand-entered from the
#: exchange calendar, not fetched. ★ It is strictly better than the legacy
#: weekday-only rule and strictly worse than asking the vendor — **DE-48 says
#: which**, and `unknown_beyond` below refuses to answer past its coverage
#: rather than guessing, because a silent wrong `True` runs the pipeline
#: against a market that never opened.
NYSE_HOLIDAYS = frozenset({
    # 2025
    date(2025, 1, 1), date(2025, 1, 20), date(2025, 2, 17), date(2025, 4, 18),
    date(2025, 5, 26), date(2025, 6, 19), date(2025, 7, 4), date(2025, 9, 1),
    date(2025, 11, 27), date(2025, 12, 25),
    # 2026
    date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3),
    date(2026, 5, 25), date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7),
    date(2026, 11, 26), date(2026, 12, 25),
    # 2027
    date(2027, 1, 1), date(2027, 1, 18), date(2027, 2, 15), date(2027, 3, 26),
    date(2027, 5, 31), date(2027, 6, 18), date(2027, 7, 5), date(2027, 9, 6),
    date(2027, 11, 25), date(2027, 12, 24),
})

#: The span `NYSE_HOLIDAYS` actually covers. ★ Outside it the answer is
#: **unknown**, not `True` — DE-35's shape: *"no holidays found"* and *"we did
#: not look"* are opposite findings.
COVERED_FROM, COVERED_TO = date(2025, 1, 1), date(2027, 12, 31)


def is_trading_day(day: date) -> bool | None:
    """★ `None` means **unknowable**, and D-08's OR-6 blocks on it.

    ⚠ *A precondition that cannot be evaluated blocks the run and reports why.
    It never defaults to "probably fine."*
    """
    if not COVERED_FROM <= day <= COVERED_TO:
        return None
    if day.weekday() >= 5:
        return False
    return day not in NYSE_HOLIDAYS


def previous_trading_day(day: date) -> date | None:
    """The session before `day`, or `None` if it falls outside coverage."""
    from datetime import timedelta

    probe = day - timedelta(days=1)
    for _ in range(10):
        answer = is_trading_day(probe)
        if answer is None:
            return None
        if answer:
            return probe
        probe -= timedelta(days=1)
    return None
