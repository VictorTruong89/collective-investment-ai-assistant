"""CT-7.6 — the axis Class-B data does not carry (§5A.4, DE-6.7…DE-6.10).

```
CLASS B IS THE ONE THAT WILL BITE.

analyst-estimates has a `date` field. It is the FORECAST target period —
FY2027 — not the day the estimate was made. Joining it to a 2024 training
row gives the model a 2026 opinion about 2027 and calls it a 2024 feature.

DE-6.4 says as_of is never defaulted to today. Class B data defaults to
today STRUCTURALLY — it has no other value to offer.
```

★ **There is no retrofit.** History not captured is gone, which is what makes
this a B2 deliverable rather than something to add when a feature needs it. The
same is true of news (§5C.4): FMP serves ~92 days and there is no backfill at
any price, so a news-derived feature's training window begins at first capture.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from src.data_engine.contracts.ledgers import (
    CLASS_B_FIELD_SETS, OBSERVATION_LEDGER, PIT_CONSUMERS,
)
from src.data_engine.contracts.schema import as_utc_timestamp
from src.data_engine.errors import LiveReadDeniedError
from src.data_engine.pit.models import utcnow
from src.data_engine.pit.snapshot import require_as_of
from src.data_engine.store.atomic import read_parquet, write_parquet


def canonical_payload(payload) -> str:
    """The response, canonicalised — DE-6.10's `content_hash` depends on it.

    `sort_keys` is what makes "unchanged" mean unchanged: a vendor that returns
    the same values with the keys in a different order must hash the same, or
    the ledger would grow one row per fetch and its size would track uptime
    rather than information.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(payload) -> str:
    return hashlib.sha256(canonical_payload(payload).encode("utf-8")).hexdigest()


class ObservationLedger:
    """Append-only snapshot store, one parquet per field set."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def path(self, field_set: str) -> Path:
        return self.root / f"{field_set}.parquet"

    def read(self, field_set: str) -> pd.DataFrame:
        p = self.path(field_set)
        return read_parquet(p) if p.is_file() else OBSERVATION_LEDGER.empty()

    # -- write -------------------------------------------------------------- #

    def snapshot(
        self, *, ticker: str, field_set: str, payload, source_endpoint: str,
        observed_at: datetime | None = None,
    ) -> bool:
        """Append one observation. Returns False when nothing was written.

        ⚠ `observed_at` defaults to now and that is **not** a DE-6.4 violation —
        it is DE-6.8. The stamp is OURS: the moment we asked. Taking it from a
        vendor field would claim a publication date that does not exist, which
        is the exact fiction this ledger exists to avoid.

        DE-6.10 / AC-7.28: an unchanged snapshot appends **no row**. The ledger
        records *changes*, so its size tracks information rather than uptime.
        """
        ticker = ticker.upper()
        digest = content_hash(payload)
        existing = self.read(field_set)

        if len(existing):
            mine = existing[existing["ticker"] == ticker]
            if len(mine):
                newest = mine.sort_values("observed_at", kind="mergesort").iloc[-1]
                if newest["content_hash"] == digest:
                    return False

        row = pd.DataFrame([{
            "ticker": ticker,
            "field_set": field_set,
            "observed_at": observed_at or utcnow(),
            "source_endpoint": source_endpoint,
            "payload": canonical_payload(payload),
            "content_hash": digest,
        }])
        row["observed_at"] = as_utc_timestamp(row["observed_at"])
        out = pd.concat([existing, row], ignore_index=True) if len(existing) else row
        out = out.sort_values(["ticker", "observed_at"], kind="mergesort").reset_index(drop=True)
        OBSERVATION_LEDGER.validate(out)
        write_parquet(out, self.path(field_set))
        return True

    # -- read --------------------------------------------------------------- #

    def get(self, *, ticker: str, field_set: str, as_of=None, consumer: str = "display"):
        """DE-6.9 / AC-7.26 — the ONLY Class-B read path for a PIT consumer.

        Returns the most recent observation with ``observed_at <= as_of``, or
        None when nothing had been observed by then. `None` here means
        *legitimately absent*, not *failed* (EH-2): before first capture there
        genuinely was no observation, and inventing one is the whole hazard.
        """
        if consumer in PIT_CONSUMERS:
            as_of = require_as_of(as_of, f"get({field_set!r}, consumer={consumer!r})")
        df = self.read(field_set)
        if not len(df):
            return None
        mine = df[df["ticker"] == ticker.upper()]
        if as_of is not None:
            mine = mine[mine["observed_at"] < end_of_day_utc(as_of)]
        if not len(mine):
            return None
        newest = mine.sort_values("observed_at", kind="mergesort").iloc[-1]
        return {
            "ticker": newest["ticker"], "field_set": newest["field_set"],
            "observed_at": newest["observed_at"].to_pydatetime(),
            "source_endpoint": newest["source_endpoint"],
            "payload": json.loads(newest["payload"]),
            "content_hash": newest["content_hash"],
        }

    def first_capture(self, field_set: str, ticker: str) -> date | None:
        """DE-26 / AC-7.42 — when this series starts, so a backtest cannot precede it.

        ⚠ There is no historical backfill for news at any price, and none for any
        Class-B family. A feature built on either has a usable training window
        that BEGINS here, and a backtest that quietly extends before it is
        training on data that did not exist.
        """
        df = self.read(field_set)
        mine = df[df["ticker"] == ticker.upper()] if len(df) else df
        if not len(mine):
            return None
        return mine["observed_at"].min().date()


def end_of_day_utc(as_of) -> "pd.Timestamp":
    """The instant the `as_of` **trading day** ends, in UTC. ★★ DE-53.

    ⚠ *Found 2026-08-26 capturing Class-B observations:* the cutoff was
    `Timestamp(as_of, tz="UTC") + 1 day`, and **`as_of` is an ET trading date
    everywhere in this system** — the calendar, the open anchor and
    `is_trading_day` all are. A UTC-midnight cutoff therefore ends the business
    day at **19:00 or 20:00 ET**, so every observation captured in the evening
    of day T was invisible to a run dated T.

    ★★ **The failure was silent and self-inflicted:** a run captured a profile
    at 22:50 ET, wrote it to the ledger, then read back `None` and assembled the
    bundle without it — *"nothing was captured"* and *"it was captured four
    hours ago"* were indistinguishable.

    ⚠ Never fixed by back-dating `observed_at`: **DE-6.8 says the stamp is
    ours** — the moment we asked — and moving it would claim we asked earlier
    than we did.
    """
    from zoneinfo import ZoneInfo

    #: The market's timezone, as `observation/day_open.py` and
    #: `orchestration/schedule/cadence.py` already define it.
    market_midnight = pd.Timestamp(as_of, tz=ZoneInfo("America/New_York"))
    return (market_midnight + pd.Timedelta(days=1)).tz_convert("UTC")


def deny_live_read(field_set: str, consumer: str) -> None:
    """Raise when a PIT consumer reaches for Class-B data outside the ledger.

    ★ Written per-CONSUMER rather than per-field on purpose (DE-6.9). Live
    consensus is genuinely useful on a report today and genuinely poison in a
    training row; both are true, so the field cannot decide it.
    """
    if consumer in PIT_CONSUMERS and field_set in CLASS_B_FIELD_SETS:
        raise LiveReadDeniedError(field_set, consumer)
