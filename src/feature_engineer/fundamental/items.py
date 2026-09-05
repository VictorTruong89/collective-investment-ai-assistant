"""Canonical line items from CT-7.2, and the point-in-time join onto a daily panel.

★ **Two jobs, and the second is where the look-ahead lives.**

  1. **Canonicalise.** EDGAR does not have one tag per concept. Revenue arrives as
     `Revenues` *or* `RevenueFromContractWithCustomerExcludingAssessedTax`; cost
     of sales as `CostOfRevenue` *or* `CostOfGoodsAndServicesSold`. A feature
     that reads one tag is null for every filer that uses the other.

  2. **Join as-of.** Fundamentals are per fiscal period; the panel is per day. For
     each `(ticker, date)` the row must carry **the most recent filing whose
     `filing_date <= date`** — nothing later.

```text
╔══════════════════════════════════════════════════════════════════╗
║  merge_asof(direction="backward").  NEVER "nearest", and never    ║
║  "forward".  `nearest` will happily attach a filing published     ║
║  AFTER the date it is joined to whenever that one is closer —     ║
║  which is look-ahead that reads as a rounding choice.             ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **Coverage is not uniform and that is accounting, not a defect.** Measured
2026-08-27: `NVDA` reports 20 of 20 wanted tags, `WMT` 15, `XOM` 16, **`JPM` 9**
and **`PLD` 10**. A bank has no gross profit and no current/non-current split.
`f_gross_margin` is null for JPM *correctly* — and **FE-37** records what that
costs the consumer.
"""

from __future__ import annotations

import pandas as pd

#: canonical name → the EDGAR tags that may supply it, **in preference order**.
#:
#: ★ Order is the whole contract: the first tag present wins, per period, so a
#: filer that reports both gets a stable answer. ⚠ Preferring by *value* — say,
#: the larger — would let one company's series switch definition mid-history,
#: which is the discontinuity DE-5.3 refuses one level up.
CANONICAL: dict[str, tuple[str, ...]] = {
    "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"),
    "cost_of_revenue": ("CostOfRevenue", "CostOfGoodsAndServicesSold"),
    "gross_profit": ("GrossProfit",),
    "operating_income": ("OperatingIncomeLoss",),
    "net_income": ("NetIncomeLoss",),
    "total_assets": ("Assets",),
    "total_liabilities": ("Liabilities",),
    "stockholders_equity": ("StockholdersEquity",),
    "current_assets": ("AssetsCurrent",),
    "current_liabilities": ("LiabilitiesCurrent",),
    "cash": ("CashAndCashEquivalentsAtCarryingValue",),
    "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities",),
    "capex": ("PaymentsToAcquirePropertyPlantAndEquipment",),
    "rd_expense": ("ResearchAndDevelopmentExpense",),
    "interest_expense": ("InterestExpense",),
    "long_term_debt": ("LongTermDebtNoncurrent",),
    "current_debt": ("LongTermDebtCurrent",),
    "diluted_shares": ("WeightedAverageNumberOfDilutedSharesOutstanding",),
}

#: ★★ **Canonical items that are COUNTS, not money.** ⚠ *Found 2026-08-27:*
#: `canonical_frame` divided **every** column by 100 to leave minor units, and a
#: share count went with it — NVDA's real **24 285 000 000** diluted shares
#: became **242 850 000**, so market capitalisation came out **100× too small**
#: and `f_market_to_book` with it.
#:
#: ★ Same class as **DE-52**, one layer up: a non-monetary quantity carried
#: through a monetary conversion. DE-52 keeps per-share *ratios* out of the
#: ingest; a share *count* has to be in it (EPS and market cap both need one), so
#: the exemption is declared here instead.
#:
#: ⚠ Declared rather than inferred from an empty `<tag>_currency`: an absent
#: currency column and a genuinely non-monetary one look identical, and guessing
#: from that would scale correctly right up until a currency went missing.
NON_MONETARY = frozenset({"diluted_shares"})

#: CT-7.2 provenance columns carried through the join so a feature row can say
#: which filing it came from.
PROVENANCE = ("period_end", "period_type", "filing_date", "accession_id",
              "source", "restated")


def canonical_frame(rows: pd.DataFrame) -> pd.DataFrame:
    """CT-7.2's `<tag>_minor` columns reduced to canonical names, in **major units**.

    ★ **The division out of minor units happens once, here** — FE-32's boundary,
    the same place `mom_21` leaves the Money type. Every ratio downstream is
    dimensionless, so the unit stops mattering after this function.

    ⚠ Returns `null` where no tag in the preference list is present. That is
    FE-14 and it is load-bearing: *a zero margin and an unknown margin are
    different facts*, and for a bank the second is the true one.
    """
    if rows is None or not len(rows):
        return pd.DataFrame()

    out = pd.DataFrame({"ticker": rows["ticker"].to_numpy()})
    for column in PROVENANCE:
        if column in rows.columns:
            out[column] = rows[column].to_numpy()

    for canonical, tags in CANONICAL.items():
        series = pd.Series(pd.NA, index=rows.index, dtype="Float64")
        for tag in tags:                      # ★ preference order, first wins
            column = f"{tag}_minor"
            if column not in rows.columns:
                continue
            series = series.fillna(rows[column].astype("Float64"))
        scale = 1.0 if canonical in NON_MONETARY else 100.0
        out[canonical] = (series / scale).astype("Float64").to_numpy()
    return out


def as_of_join(panel: pd.DataFrame, canonical: pd.DataFrame) -> pd.DataFrame:
    """Attach each `(ticker, date)` its latest filing knowable at that date.

    ★★ **`direction="backward"` is the entire point.** ⚠ `nearest` attaches a
    filing published *after* the date whenever that one is closer — look-ahead
    that reads as a rounding choice and produces a panel whose backtest is
    unfalsifiably good.

    ⚠ **Keyed on `filing_date`, never `period_end`.** A quarter ending 31 March
    is not knowable on 31 March; it is knowable when it is filed, six to eight
    weeks later. Joining on the period end is the single most expensive
    look-ahead available in fundamentals — it is worth roughly one quarter of
    hindsight on every row.
    """
    if canonical is None or not len(canonical):
        return pd.DataFrame(index=panel.index)

    left = panel[["ticker", "date"]].copy()
    left["date"] = pd.to_datetime(left["date"])
    left["_row"] = range(len(left))

    right = canonical.copy()
    right["filing_date"] = pd.to_datetime(right["filing_date"])
    # ⚠ merge_asof requires both sides sorted on the join key, globally.
    right = right.sort_values(["filing_date", "ticker"], kind="mergesort")
    left_sorted = left.sort_values(["date", "ticker"], kind="mergesort")

    merged = pd.merge_asof(
        left_sorted, right, left_on="date", right_on="filing_date",
        by="ticker", direction="backward")

    return (merged.sort_values("_row", kind="mergesort")
                  .drop(columns=["_row", "ticker", "date"])
                  .set_index(panel.index))


def attach(panel: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    """`canonical_frame` then `as_of_join` — the one path features should use."""
    return as_of_join(panel, canonical_frame(rows))
