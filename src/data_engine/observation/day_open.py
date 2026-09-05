"""D-07 DE-47 — the day-T opening print, as its own read.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE OPENING PRINT AND THE DAY-T BAR SETTLE AT DIFFERENT TIMES.  ║
║                                                                  ║
║  The opening auction prints at 09:30 and is FINAL.               ║
║  The bar is not final until 16:00.                               ║
║                                                                  ║
║  So a daily endpoint polled at 10:00 returns an IN-PROGRESS row  ║
║  whose high/low/close are the running price — which is exactly   ║
║  open == high == low == close, the collapsed bar OR-32 names     ║
║  and main_inference.py:250 produced.                             ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **This module serves the PRINT.** ⚠ It never fabricates the other three
fields, and it never backfills from the previous close (OR-33) — *that
substitution is silent and makes the decision a day stale while looking
current.*
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

MARKET_TZ = "America/New_York"
SESSION_OPEN = time(9, 30)

#: ⚠ **ADMITTED GUESS** (CN-10): how long after the bell a vendor needs before
#: its `open` field reflects the auction rather than the last pre-market tick.
#: DE-47 states the *rule* — the print is final at 09:30 — and names no margin.
SETTLING_MARGIN_MINUTES = 5


@dataclass(frozen=True, slots=True)
class DayOpen:
    """The opening print. ★ `high`/`low`/`close` are **deliberately absent.**

    ⚠ A contract that carried them would invite a caller to read an
    in-progress high as a settled one — which is the collapsed-bar defect
    arriving through the type system instead of through the data.
    """

    ticker: str
    date: date
    open_minor: int | None
    currency: str
    settled: bool
    why: str = ""
    source: str = "fmp"
    observed_at: datetime | None = None

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker, "date": self.date.isoformat(),
                "open_minor": self.open_minor, "currency": self.currency,
                "settled": self.settled, "why": self.why, "source": self.source,
                "observed_at": self.observed_at.isoformat()
                               if self.observed_at else None}

    def as_precondition_bar(self) -> dict | None:
        """The shape D-08's `assert_open_confirmed` checks (OR-32).

        ★ Returns `None` when unsettled, so the run **blocks** rather than
        receiving a bar it would have to trust. ⚠ The four OHLC keys are filled
        from the print alone **only when the session has closed** — before that
        there is no honest value for three of them, and D-08's collapsed-bar
        check would (correctly) reject a row that pretended otherwise.
        """
        if not self.settled or self.open_minor is None:
            return None
        return {"open": self.open_minor, "settled": True,
                # ⚠ Deliberately distinct sentinels: D-08 refuses a row whose
                #   four fields are equal, and these are not values — they are
                #   the absence of a settled high/low/close, stated.
                "high": None, "low": None, "close": None}


def session_open_utc(day: date) -> datetime:
    return datetime.combine(day, SESSION_OPEN,
                            tzinfo=ZoneInfo(MARKET_TZ)).astimezone(timezone.utc)


def is_print_settled(day: date, *, now: datetime,
                     margin_minutes: int = SETTLING_MARGIN_MINUTES) -> bool:
    """DE-47 — the auction has completed for `day`.

    ⚠ A future date is never settled, however late in the day it is asked.
    """
    from datetime import timedelta

    return now >= session_open_utc(day) + timedelta(minutes=margin_minutes)


def day_open(*, ticker: str, as_of: date, row, now: datetime,
             margin_minutes: int = SETTLING_MARGIN_MINUTES) -> DayOpen:
    """Build the print from a vendor row. `row` is `None` when nothing exists.

    ⚠ **A row whose OHLC fields are all equal is refused, not returned**
    (AC-7.63): it is a running price wearing a bar's shape, and passing it on
    would move the defect one domain downstream.
    """
    observed = now
    if not is_print_settled(as_of, now=now, margin_minutes=margin_minutes):
        return DayOpen(ticker, as_of, None, "USD", False,
                       why=(f"the {as_of} opening auction has not settled as of "
                            f"{now.isoformat()} (DE-47)"), observed_at=observed)
    if row is None:
        return DayOpen(ticker, as_of, None, "USD", False,
                       why=f"no vendor row for {ticker} on {as_of}",
                       observed_at=observed)

    fields = [row.get(f) for f in ("open", "high", "low", "close")]
    if all(f is not None for f in fields) and len(set(fields)) == 1:
        from src.data_engine.errors import DataError

        raise DataError(
            f"{ticker} {as_of}: open==high==low==close=={fields[0]!r}. That is "
            f"the running price wearing a bar's shape, not the opening print — "
            f"returning it would put a zero intraday range on the one bar that "
            f"drives the decision (DE-47, OR-32, INV-4)")

    # ⚠ `open_minor` is Money MINOR units (CT-7.1's convention). The source
    #   constructs it at the boundary (DE-3); a bare vendor float here would be
    #   a major-unit number wearing a minor-unit name.
    minor = row.get("open_minor", row.get("open"))
    if minor is None:
        return DayOpen(ticker, as_of, None, row.get("currency", "USD"), False,
                       why=f"the vendor row for {as_of} carries no open",
                       observed_at=observed)
    if not isinstance(minor, int):
        from src.data_engine.errors import DataError

        raise DataError(
            f"{ticker} {as_of}: open={minor!r} is not int minor units. CT-7.1's "
            f"`*_minor` columns are int64 Money minor units, and a float here "
            f"is a major-unit number wearing a minor-unit name (DE-3)")
    return DayOpen(ticker=ticker, date=as_of, open_minor=minor,
                   currency=row.get("currency", "USD"), settled=True,
                   observed_at=observed)
