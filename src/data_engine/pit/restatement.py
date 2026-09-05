"""Restatement detection on the FMP side — DE-21, DE-23, DE-24 (AC-7.35/37/39).

```
FMP HAS NO RESTATEMENT HISTORY. IT SERVES ONE ANSWER: TODAY'S.
If a number changes, the old value is gone, and NOTHING IN THE RESPONSE
INDICATES THAT IT CHANGED.
```

EDGAR is different — every filing is immutable and separately addressable — so
§6.3 reconstructs any past date from the Fact ledger. For an FMP-routed ticker
there is no such reconstruction, and **the only detection available is to have
kept a dated earlier value and diff it**. That is what this module is.
"""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd

from src.data_engine.errors import WARNING_CODES

#: DE-21 / AC-7.35 — the placement order for an FMP fundamental row. `date` is
#: the PERIOD END and precedes knowability by a measured 20-57 days (MU, 40
#: quarters, median 28). It is not in this list and must never be.
FMP_KNOWABILITY_FIELDS = ("acceptedDate", "filingDate")

#: DE-23 / AC-7.37 — fields that LOOK like a knowability axis and are not.
#: `lastUpdated` is a batch reload stamp: 99 MSFT quarters share 8 distinct
#: values and the median row was "last updated" eleven years after it was
#: reported. Listed so a future reader does not rediscover it as a good idea.
FORBIDDEN_KNOWABILITY_FIELDS = ("lastUpdated", "date")


def knowability_date(row: dict, *, ticker: str, allow_missing: bool = False):
    """DE-21 — place an FMP fundamental row in time by acceptedDate, then filingDate.

    ⚠ Naively keying on `date` is look-ahead on **every fundamental feature, on
    average four weeks of it, every quarter**. The gap is not an edge case; it
    is the normal case.
    """
    for field in FMP_KNOWABILITY_FIELDS:
        value = row.get(field)
        if value:
            return _as_date(value)
    if allow_missing:
        return None
    from src.data_engine.errors import NoFilingDateError
    raise NoFilingDateError(ticker, row.get("tag", "<statement>"), row.get("date"))


def next_session_knowability(accepted_at: datetime, sessions) -> date:
    """§5C.5 — an acceptance at or after 16:00 ET is knowable the NEXT session.

    408 of 437 MSFT filings were accepted at or after the close. A same-day join
    is therefore a half-day leak on 93 % of filings, which is small per filing
    and systematic across all of them.

    `sessions` is the sorted trading calendar; the caller supplies it because
    D-07 does not own an exchange calendar and inventing one here would be a
    second definition of the trading day.
    """
    same_day = accepted_at.date()
    if accepted_at.hour < 16:
        return same_day
    for session in sessions:
        if session > same_day:
            return session
    raise ValueError(
        f"no trading session after {same_day} in the supplied calendar — the "
        f"knowability date of a filing accepted after the close cannot be resolved"
    )


def diff_against_stored(
    stored: pd.DataFrame, incoming: pd.DataFrame, *, key: list[str], value_col: str,
) -> pd.DataFrame:
    """DE-24 / AC-7.39 — what changed between two dated ingests.

    Returns one row per changed key with `stored`, `incoming` and the warning
    code, so the caller records a change event instead of overwriting silently.
    **This works only if we never overwrite**, which is why re-ingest goes
    through here rather than straight to the store.
    """
    if not len(stored):
        return pd.DataFrame(columns=key + ["stored", "incoming", "code"])
    merged = incoming.merge(
        stored[key + [value_col]], on=key, how="inner",
        suffixes=("_incoming", "_stored"), validate="one_to_one",
    )
    changed = merged[merged[f"{value_col}_incoming"] != merged[f"{value_col}_stored"]]
    out = changed[key].copy()
    out["stored"] = changed[f"{value_col}_stored"].to_numpy()
    out["incoming"] = changed[f"{value_col}_incoming"].to_numpy()
    out["code"] = WARNING_CODES["value_changed"]
    return out.reset_index(drop=True)


def market_cap_at(close_minor: int, shares_outstanding: int) -> int:
    """DE-25 / AC-7.40 — past market cap is close(d) x shares(as_of=d).

    ⚠ `historical-market-capitalization` is **not served to a PIT consumer**.
    Dividing its `marketCap` by `close` recovers the share count FMP used, and
    for MU that count **steps on the period-end date, 21-36 days before the
    filing that disclosed it**. Nobody knew MU's Q3 share count on 2024-05-30;
    it was published on 2024-06-27. Market cap feeds size, every EV and P/x
    multiple, and index weighting, so the leak propagates widely.

    On a split name it is worse: NVDA's series implies 24.578B shares in January
    2024 against a true 2.458B. The market-cap VALUE is invariant, so the number
    looks right — it is the share count recoverable from it that is off by the
    split factor (§5C.7).
    """
    if shares_outstanding <= 0:
        raise ValueError(
            f"share count {shares_outstanding} is not positive; a market cap "
            f"computed from it would be a plausible number with no meaning"
        )
    return int(close_minor) * int(shares_outstanding)


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value)
    return datetime.fromisoformat(text.replace("Z", "+00:00")).date() if "T" in text \
        else date.fromisoformat(text[:10])
