"""D-08 §5A — the production cadence. OR-8, OR-30…OR-34, OR-37, OR-42, OR-46.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A CRON PINNED AT 14:00 UTC RUNS AT 09:00 ET ALL WINTER —        ║
║  THIRTY MINUTES BEFORE THE MARKET OPENS.                         ║
║                                                                  ║
║  The day-T open would not exist, and every run from November to  ║
║  March would either block or silently decide off a stale bar.    ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **OR-30: the cadence is `(local_time, tz)` and is resolved to UTC per date.**
Timestamps in the manifest stay UTC (INV-007); **the schedule is not a UTC
constant.**
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

#: QO-3, decided 2026-08-18 — 10:00 ET, consuming the day-T open.
MARKET_TZ = "America/New_York"
DAILY_LOCAL_TIME = time(10, 0)

#: OR-35 — the decision anchor, declared in the manifest and propagated to
#: D-02/D-03/D-04. ★ *If the decision is taken at the day-T open, the label must
#: be anchored at the day-T open* — the mismatch is **a full session of drift on
#: every prediction, invisible in backtest because the backtest shares the
#: training anchor.**
DECISION_ANCHOR = "open"


@dataclass(frozen=True, slots=True)
class Cadence:
    """OR-30 — ★ stored local, resolved per date, **never pinned in UTC**."""

    job_graph_id: str
    local_time: time = DAILY_LOCAL_TIME
    tz: str = MARKET_TZ

    def __post_init__(self) -> None:
        if self.tz.upper() in ("UTC", "GMT", "Z"):
            from src.orchestration.errors import UtcPinnedCadenceError
            raise UtcPinnedCadenceError(self.job_graph_id)

    def firing_utc(self, on: date) -> datetime:
        """OR-30/OR-31 — the resolved instant, written into the manifest so a
        DST-shifted run is **visible rather than inferred**."""
        local = datetime.combine(on, self.local_time, tzinfo=ZoneInfo(self.tz))
        return local.astimezone(timezone.utc)

    def cadence_key(self, on: date) -> str:
        """★ OR-46 — the window's identity.

        ⚠ **A lock is mutual exclusion in time and cannot deliver AC-8.37**: two
        firings twenty minutes apart never overlap, so the second finds the lock
        free and runs the whole cadence again. The key is what a completed run
        claims.
        """
        return (f"{self.job_graph_id}:{on.isoformat()}:"
                f"{self.local_time.strftime('%H:%M')}")

    def to_json_obj(self) -> dict:
        return {"job_graph_id": self.job_graph_id,
                "local_time": self.local_time.strftime("%H:%M"), "tz": self.tz}


def first_trading_day(year: int, month: int, *, is_trading_day) -> date:
    """OR-37 — ★ the first **trading** day of the month, not the 1st.

    ⚠ *The 1st falls on a weekend or holiday roughly ⅓ of the time; a
    calendar-blind rule would skip those months entirely or run against a closed
    market.*
    """
    day = date(year, month, 1)
    from datetime import timedelta
    for _ in range(15):
        if is_trading_day(day):
            return day
        day += timedelta(days=1)
    from src.orchestration.errors import RetrainNonTradingDayError
    raise RetrainNonTradingDayError(year, month)


def is_retrain_morning(on: date, *, is_trading_day) -> bool:
    return on == first_trading_day(on.year, on.month, is_trading_day=is_trading_day)
