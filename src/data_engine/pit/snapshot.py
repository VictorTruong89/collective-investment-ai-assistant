"""§6.3 as-of resolution — the domain's reason to exist (DE-6.1, DE-6.4, DE-6.6).

```
A POINT-IN-TIME QUERY RETURNS WHAT WAS KNOWABLE, NOT WHAT IS TRUE.
as_of(2024-03-01) returns the numbers a person could have READ on 2024-03-01,
including the ones later restated. It does NOT return today's corrections.
```

★ STEP 3 IS THE SUBTLE ONE. "Knowable on D" is not "the first thing filed" — if
a restatement landed on or before D, it *was* knowable on D. **The filter is on
publication, not on originality.** Getting this backwards produces a ledger that
is defensibly conservative and quietly wrong in the other direction.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.data_engine.contracts.envelopes import Provenance
from src.data_engine.contracts.ledgers import FACT_LEDGER
from src.data_engine.contracts.panels import FUNDAMENTAL_PANEL, validate_fundamental_panel
from src.data_engine.errors import AsOfRequiredError, DerivedNoFilingDateError
from src.data_engine.pit.models import EDGAR, utcnow

#: Sentinel for "the caller did not pass as_of at all", distinct from None.
#: DE-6.4 forbids a default; a plain ``as_of=None`` default would BE one, just
#: spelled differently, and every call site would keep working.
_UNSET = object()


def require_as_of(as_of, method: str) -> date:
    """DE-6.4 / AC-7.10 — no default, ever, not even to today.

    ⚠ The rule most likely to be eroded, because ``as_of=None -> today`` is
    silently CORRECT in production, where today is the as-of. It is silently
    wrong in every backtest and every training run, and the numbers look right
    in both cases.
    """
    if as_of is _UNSET or as_of is None:
        raise AsOfRequiredError(method)
    if not isinstance(as_of, date):
        raise AsOfRequiredError(f"{method} (got {type(as_of).__name__})")
    return as_of


def facts_as_of(ledger_df: pd.DataFrame, as_of=_UNSET) -> pd.DataFrame:
    """§6.3 steps 1-3: the Facts knowable at `as_of`, one per group.

    Deterministic by construction (DE-6.6 / AC-7.11): the sort is explicit and
    stable, so the "latest filing" tie-break resolves the same way every time.
    An unstable tie-break would make the whole panel irreproducible while
    looking deterministic (PD-20).
    """
    as_of = require_as_of(as_of, "facts_as_of")
    if not len(ledger_df):
        return FACT_LEDGER.empty()

    cutoff = pd.Timestamp(as_of)
    knowable = ledger_df[ledger_df["filing_date"] <= cutoff]        # step 1
    if not len(knowable):
        return FACT_LEDGER.empty()

    ordered = knowable.sort_values(                                  # step 3
        ["ticker", "tag", "period_end", "period_type", "filing_date", "accession_id"],
        kind="mergesort",
    )
    latest = ordered.groupby(
        ["ticker", "tag", "period_end", "period_type"], sort=True, as_index=False
    ).tail(1)
    return latest.sort_values(list(FACT_LEDGER.key), kind="mergesort").reset_index(drop=True)


def restatement_flags(ledger_df: pd.DataFrame, as_of=_UNSET) -> pd.DataFrame:
    """Which (tag, period) groups had more than one filing on or before `as_of`.

    DE-6.5 / AC-7.13: restatements are **surfaced, not smoothed**. This is the
    half that reaches the consumer — `facts_as_of` picks the right value, this
    says that a choice was made at all.
    """
    as_of = require_as_of(as_of, "restatement_flags")
    if not len(ledger_df):
        return pd.DataFrame(columns=["ticker", "tag", "period_end", "period_type", "filings"])
    knowable = ledger_df[ledger_df["filing_date"] <= pd.Timestamp(as_of)]
    counts = (knowable.groupby(["ticker", "tag", "period_end", "period_type"], sort=True)
                      ["accession_id"].nunique().reset_index(name="filings"))
    return counts


def assemble_rows(
    ledger_df: pd.DataFrame,
    as_of=_UNSET,
    *,
    source: str = EDGAR,
    shares_tag: str = "CommonStockSharesOutstanding",
) -> pd.DataFrame:
    """§6.3 steps 4-5 — CT-7.2, derived from CT-7.3 at an as_of (AC-7.17).

    One row per `(ticker, period_end, period_type)`, one `<tag>_minor` /
    `<tag>_currency` pair per line item, plus the provenance §6.3 step 5
    requires: `accession_id` and `filing_date` per row.

    ⚠ `pit_guarantee` is filled from `source` and not inferred from the data
    (DE-23, AC-7.38). An EDGAR-routed ticker is *reconstructed*; an FMP-routed
    one is *best_effort*, because FMP serves one answer — today's — and if a
    number changed, the old value is gone with nothing indicating it did.
    """
    as_of = require_as_of(as_of, "assemble_rows")
    ledger_df, scale_refused = _refuse_share_scale(ledger_df, as_of)
    facts = facts_as_of(ledger_df, as_of)
    if not len(facts):
        return FUNDAMENTAL_PANEL.empty()

    flags = restatement_flags(ledger_df, as_of)
    # Tuple keys, not joined strings. `Series.astype(str)` renders a midnight
    # Timestamp as "2024-03-31" while `str(Timestamp)` renders
    # "2024-03-31 00:00:00", so a string join silently never matched — a
    # difference invisible in both the flags frame and the panel.
    restated = {
        (r.ticker, pd.Timestamp(r.period_end), r.period_type)
        for r in flags[flags["filings"] > 1].itertuples()
    }

    rows = []
    grouped = facts.groupby(["ticker", "period_end", "period_type"], sort=True)
    for (ticker, period_end, period_type), grp in grouped:
        newest = grp.sort_values("filing_date", kind="mergesort").iloc[-1]
        row = {
            "ticker": ticker,
            "period_start": grp["period_start"].min(),
            "period_end": period_end,
            "period_type": period_type,
            "shares_outstanding": _shares(grp, shares_tag),
            "source": source,
            "accession_id": newest["accession_id"] if source == EDGAR else None,
            "filing_date": newest["filing_date"],
            "ingested_at": pd.Timestamp(utcnow()),
            "pit_guarantee": (Provenance.RECONSTRUCTED if source == EDGAR
                              else Provenance.BEST_EFFORT),
            "restated": (ticker, pd.Timestamp(period_end), period_type) in restated,
            "quality_flags": ("share_scale_refused (DE-86)"
                              if (ticker, pd.Timestamp(period_end), period_type) in scale_refused
                              else ""),
        }
        for _, fact in grp.iterrows():
            row[f"{fact['tag']}_minor"] = int(fact["value_minor"])
            row[f"{fact['tag']}_currency"] = fact["value_currency"]
        rows.append(row)

    df = pd.DataFrame(rows)
    # A line item absent from one period leaves a NaN, which widens the int
    # column to float. DE-14: missing is null, never 0 — so the column is left
    # nullable-int rather than zero-filled (PD-1: no imputation, ever).
    for col in [c for c in df.columns if c.endswith("_minor")]:
        df[col] = df[col].astype("Int64")
    df["shares_outstanding"] = df["shares_outstanding"].astype("Int64")
    df["restated"] = df["restated"].astype(bool)
    return validate_fundamental_panel(df.reset_index(drop=True))


#: DE-86 — how far from the name's own median a share count may sit before it is refused.
SHARE_SCALE_FACTOR = 100


def _refuse_share_scale(ledger_df: pd.DataFrame, as_of):
    """★★ DE-86 (`DX-179`) — a `shares` fact filed at the wrong SCALE is not served.

    ⚠ Measured: GRMN filed 193,597 (thousands) beside 192,885,000; MCD 720 (millions)
    beside 965,500,000. The reference is the median of the same name's same tag over
    the facts KNOWABLE at `as_of` — no look-ahead in the guard. Refused, never rescaled:
    a guessed factor would be a fabricated figure. Returns the ledger without them and
    the `(ticker, period_end, period_type)` keys they belonged to, for the flag.
    """
    if not len(ledger_df) or "unit" not in ledger_df.columns:
        return ledger_df, set()
    knowable = ledger_df["filing_date"] <= pd.Timestamp(as_of)
    shares = knowable & (ledger_df["unit"] == "shares")
    if not shares.any():
        return ledger_df, set()
    median = ledger_df[shares].groupby(["ticker", "tag"])["value_minor"].transform("median")
    value = ledger_df.loc[shares, "value_minor"].astype("float64")
    off = (value * SHARE_SCALE_FACTOR < median) | (value > median * SHARE_SCALE_FACTOR)
    refused = ledger_df.loc[off[off].index]
    keys = {(r.ticker, pd.Timestamp(r.period_end), r.period_type) for r in refused.itertuples()}
    return ledger_df.drop(index=refused.index), keys


def _shares(grp: pd.DataFrame, tag: str):
    hit = grp[grp["tag"] == tag]
    return int(hit.iloc[-1]["value_minor"]) if len(hit) else None


def inherit_filing_date(derived_period, statement_index: dict, kind: str):
    """DE-22 / AC-7.36 — a derived periodic borrows its statement's acceptedDate.

    `key-metrics`, `ratios`, `enterprise-values`, `financial-growth`,
    `owner-earnings` and the `*-growth` series carry **only the period end** —
    no `filingDate`, no `acceptedDate`. So they inherit from the statement for
    the same `(ticker, period_end, period_type)`.

    ⚠ With no matching statement the row is **not served to a PIT consumer**. It
    cannot be placed in time, and an unplaceable row is DE-6.3's rule applied
    one layer out — so this raises rather than falling back to the period end,
    which is the 20-to-57-day look-ahead DE-21 exists to stop.
    """
    ticker, period_end, period_type = derived_period
    hit = statement_index.get((ticker, period_end, period_type))
    if hit is None:
        raise DerivedNoFilingDateError(ticker, period_end, period_type, kind)
    return hit
