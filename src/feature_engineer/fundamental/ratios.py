"""Profitability, leverage, liquidity, efficiency, valuation and accruals.

★ Every function here takes the **canonical, as-of-joined** frame from `items.py`
— one row per panel row, carrying the latest filing knowable at that date — and
returns one aligned Series.

⚠ **`_ratio` is the only division in this module.** A bare `a / b` returns `inf`
when `b == 0` and pandas will carry it into a model without complaint;
`_ratio` returns **null** instead, because *a margin computed on zero revenue is
not enormous, it is undefined* (FE-14).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: ⚠ **Denominators that may legitimately be negative**, where the sign carries
#: meaning and the ratio does not. Book equity goes negative after large
#: buybacks (MCD, HD, SBUX all have); `net_income / equity` then reports a
#: *positive* ROE for a profitable company with negative book value, which is
#: arithmetically true and reads as the opposite of the truth.
SIGNED_DENOMINATORS = ("stockholders_equity", "net_income", "invested_capital")


def _ratio(numerator, denominator, *, allow_negative: bool = False) -> pd.Series:
    """`numerator / denominator`, with **null** wherever the answer is undefined.

    ★ `allow_negative=False` also nulls a negative denominator (see
    `SIGNED_DENOMINATORS`) rather than emitting a sign-flipped ratio that looks
    like a value.
    """
    num = pd.to_numeric(numerator, errors="coerce").astype("float64")
    den = pd.to_numeric(denominator, errors="coerce").astype("float64")
    out = num / den
    bad = den.isna() | (den == 0)
    if not allow_negative:
        bad = bad | (den < 0)
    out[bad] = np.nan
    return out.replace([np.inf, -np.inf], np.nan)


def _col(frame: pd.DataFrame, name: str) -> pd.Series:
    """A canonical column, or an all-null Series when the filer never reports it.

    ⚠ **Absent is null, not an error.** A bank has no `gross_profit` and a REIT
    no `current_assets`; raising would make an accounting fact look like a
    pipeline fault (FE-14, and the coverage table in `edgar_facts.FEATURE_TAGS`).
    """
    if name in frame.columns:
        return pd.to_numeric(frame[name], errors="coerce").astype("float64")
    return pd.Series(np.nan, index=frame.index, dtype="float64")


# --------------------------------------------------------------------------- #
# Profitability (11)
# --------------------------------------------------------------------------- #

def gross_profit(frame: pd.DataFrame) -> pd.Series:
    """`GrossProfit` when reported, else `revenue − cost_of_revenue`.

    ★ **The subtraction is legitimate HERE and forbidden in D-01.** RA-132 says
    combining two figures *"is arithmetic, and it is D-02's"* — this is D-02.
    """
    reported = _col(frame, "gross_profit")
    derived = _col(frame, "revenue") - _col(frame, "cost_of_revenue")
    return reported.fillna(derived)


def net_margin(f):        return _ratio(_col(f, "net_income"), _col(f, "revenue"))
def gross_margin(f):      return _ratio(gross_profit(f), _col(f, "revenue"))
def operating_margin(f):  return _ratio(_col(f, "operating_income"), _col(f, "revenue"))
def roa(f):               return _ratio(_col(f, "net_income"), _col(f, "total_assets"))
def roe(f):               return _ratio(_col(f, "net_income"), _col(f, "stockholders_equity"))


def invested_capital(frame: pd.DataFrame) -> pd.Series:
    """Equity + interest-bearing debt − cash. ⚠ An approximation, said to be one."""
    return (_col(frame, "stockholders_equity")
            + _col(frame, "long_term_debt").fillna(0.0)
            + _col(frame, "current_debt").fillna(0.0)
            - _col(frame, "cash").fillna(0.0))


def roic(frame: pd.DataFrame) -> pd.Series:
    """`operating_income ÷ invested_capital` — ⚠ **pre-tax, and that is a choice.**

    ★ Textbook ROIC uses **NOPAT**, operating income after tax. The effective tax
    rate needs a tax-expense tag this ingest does not carry, and **applying a
    flat 21 % would be a fabricated input, not a simplification** (CN-10: an
    admitted absence beats an invented number). Pre-tax ROIC is monotone in the
    same quantity and is comparable across names in the same tax regime; it is
    **not** comparable across regimes, and that limitation is real.
    """
    return _ratio(_col(frame, "operating_income"), invested_capital(frame))


def eps(f):               return _ratio(_col(f, "net_income"), _col(f, "diluted_shares"))
def ocf_to_assets(f):     return _ratio(_col(f, "operating_cash_flow"), _col(f, "total_assets"))


def ocf_to_net_income(frame: pd.DataFrame) -> pd.Series:
    """Cash conversion. ★ `allow_negative=True`: a loss-making quarter is exactly
    where this ratio is interesting, and nulling it would hide the cases the
    feature exists to flag."""
    return _ratio(_col(frame, "operating_cash_flow"), _col(frame, "net_income"),
                  allow_negative=True)


def fcf(frame: pd.DataFrame) -> pd.Series:
    """`operating_cash_flow − capex`, in **major currency units**.

    ⚠⚠ **NOT scale-invariant — this is a LEVEL feature, and FE-34 permits it
    only because it is declared as one.** A $10bn FCF says *large*, not *good*;
    `f_fcf_margin` is the scale-invariant sibling and is the one a
    cross-sectional ranker should prefer. ★ Kept because §5.3 declares it and a
    size factor is a legitimate thing to have — `f_size_log_assets` is one on
    purpose — but a consumer must choose it knowingly.
    """
    return _col(frame, "operating_cash_flow") - _col(frame, "capex").fillna(0.0)


def fcf_margin(f):        return _ratio(fcf(f), _col(f, "revenue"))


# --------------------------------------------------------------------------- #
# Leverage (4) · Liquidity (1)
# --------------------------------------------------------------------------- #

def debt_to_assets(f):    return _ratio(_col(f, "total_liabilities"), _col(f, "total_assets"))
def debt_to_equity(f):    return _ratio(_col(f, "total_liabilities"), _col(f, "stockholders_equity"))
def equity_ratio(f):      return _ratio(_col(f, "stockholders_equity"), _col(f, "total_assets"))


def interest_coverage(frame: pd.DataFrame) -> pd.Series:
    """`operating_income ÷ interest_expense`.

    ⚠ Null when interest expense is zero — **a debt-free company has undefined
    coverage, not infinite coverage**. The distinction matters because `inf`
    ranks first in any sort, so a company with no debt would top a "safest"
    ranking through a division by zero rather than through its balance sheet.
    """
    return _ratio(_col(frame, "operating_income"), _col(frame, "interest_expense"))


def current_ratio(f):     return _ratio(_col(f, "current_assets"), _col(f, "current_liabilities"))


# --------------------------------------------------------------------------- #
# Efficiency & size (3) · Valuation (1)
# --------------------------------------------------------------------------- #

def capex_to_revenue(f):  return _ratio(_col(f, "capex"), _col(f, "revenue"))
def rd_to_revenue(f):     return _ratio(_col(f, "rd_expense"), _col(f, "revenue"))


def size_log_assets(frame: pd.DataFrame) -> pd.Series:
    """`ln(total_assets)` — ★ **a size factor, deliberately.**

    ⚠ Not an accidental level carrier like `macd_hist` was: the size premium is
    a documented cross-sectional effect and this is the standard way to express
    it. Null for non-positive assets, which is not a real balance sheet.
    """
    assets = _col(frame, "total_assets")
    out = np.log(assets.where(assets > 0))
    return out.replace([np.inf, -np.inf], np.nan)


def market_to_book(frame: pd.DataFrame, *, market_cap=None) -> pd.Series:
    """`market_cap ÷ stockholders_equity`.

    ⚠⚠ **A VALUATION MULTIPLE, and D-01 may never see it in a blind pass.** It
    carries the price by construction — RA-14/RA-151. It is a legitimate model
    feature and an anchor for a narrative, which is exactly why the two domains
    consume D-02 through different published sets (§6.2 vs §6.3).

    Returns all-null when no market cap is supplied: **book value alone cannot
    produce it**, and inventing a price here would be the substitution D-11's
    CDR banner refuses in another domain.
    """
    if market_cap is None:
        return pd.Series(np.nan, index=frame.index, dtype="float64")
    return _ratio(market_cap, _col(frame, "stockholders_equity"))


# --------------------------------------------------------------------------- #
# Accruals (2)
# --------------------------------------------------------------------------- #

def accruals(frame: pd.DataFrame) -> pd.Series:
    """Sloan accruals — `(net_income − operating_cash_flow) ÷ total_assets`.

    ★ Scale-invariant by construction, and high values are the classic warning:
    earnings the cash flow does not support.
    """
    return _ratio(_col(frame, "net_income") - _col(frame, "operating_cash_flow"),
                  _col(frame, "total_assets"))


def accruals_std(frame: pd.DataFrame, *, periods: int = 4) -> pd.Series:
    """Rolling sd of `accruals` over the last `periods` **filings**, per ticker.

    ⚠ **Over filings, not over days.** The as-of joined frame repeats one
    filing's values across every day until the next filing lands, so a
    day-window rolling sd would be ~0 for most of a quarter and then jump — a
    measurement of the filing calendar rather than of the company.
    """
    values = accruals(frame)
    if "accession_id" not in frame.columns or "ticker" not in frame.columns:
        return pd.Series(np.nan, index=frame.index, dtype="float64")
    return _per_filing_rolling(frame, values, periods=periods, how="std")


def _per_filing_rolling(frame: pd.DataFrame, values: pd.Series, *, periods: int,
                        how: str) -> pd.Series:
    """Roll a statistic over distinct FILINGS, then broadcast back to the days.

    ★ The de-duplication is the whole trick: collapse to one row per
    `(ticker, accession_id)`, roll there, then map the answer back onto every
    day that filing covers.
    """
    work = pd.DataFrame({
        "ticker": frame["ticker"] if "ticker" in frame.columns else "",
        "accession_id": frame["accession_id"],
        "filing_date": frame.get("filing_date"),
        "_v": values,
    })
    distinct = (work.dropna(subset=["accession_id"])
                    .drop_duplicates(subset=["ticker", "accession_id"])
                    .sort_values(["ticker", "filing_date"], kind="mergesort"))
    rolled = (distinct.groupby("ticker", sort=True)["_v"]
                      .rolling(periods, min_periods=periods))
    distinct["_r"] = (rolled.std(ddof=1) if how == "std" else rolled.mean()
                      ).reset_index(level=0, drop=True)
    lookup = distinct.set_index(["ticker", "accession_id"])["_r"]
    keys = pd.MultiIndex.from_arrays([work["ticker"], work["accession_id"]])
    return pd.Series(lookup.reindex(keys).to_numpy(), index=frame.index,
                     dtype="float64")
