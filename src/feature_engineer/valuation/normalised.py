"""`AC-F10.19` — the cycle averages `J-20`'s choice parameterises (`F10` `D5`, `RA-45`).

★★ **Why this is D-02 and not D-01.** Given a method and a window of fiscal years,
averaging a series is judgement-free arithmetic — `RA-45`: *"D-01 performs no
arithmetic that D-02 could perform."* The first `D5` build put it in D-01 and the
structural guard refused it (`DX-105`). The JUDGEMENT — which method, which window —
stays in D-01 (`src/fundamental/valuation/normalise.py`); the arithmetic is here.

⚠⚠ **A window with an absent or unusable year REFUSES, naming every one.**
Measured on Micron 2026-09-13: FY2016 and FY2023 (the trough) had pretax losses,
so `D6`'s tax rate is undefined. Averaging the other years would drop exactly the
troughs and read high (`P5`; the formula question is L3 `DX-104`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext

import pandas as pd

from src.feature_engineer.errors import ValuationUnavailable
from src.feature_engineer.valuation.basis import annual_basis, trailing_total
from src.shared.money import Money

#: `AC-3.14` — the method this module implements has a MethodEntry.
FORMULA_ID = "normalised.cycle_average_fcff_or_margin.v1"


@dataclass(frozen=True, slots=True)
class AnnualYear:
    fiscal_year: int
    fiscal_year_end: date
    basis: object | None            # `AnnualBasis` when available
    margin: Decimal | None          # FCFF ÷ revenue — D-02's arithmetic, pre-computed
    unavailable: str | None         # the reason when not


def annual_history(annual_rows: pd.DataFrame, *, ticker: str, as_of: date
                   ) -> tuple[AnnualYear, ...]:
    """Every annual row knowable at `as_of`, resolved through `D6` or with its reason."""
    if annual_rows is None or not len(annual_rows):
        return ()
    out = []
    for _, row in annual_rows.sort_values("period_end", kind="mergesort").iterrows():
        end = pd.Timestamp(row["period_end"]).date()
        if pd.Timestamp(row["filing_date"]).date() > as_of:
            continue
        try:
            b = annual_basis(row, ticker=ticker, as_of=as_of)
        except ValuationUnavailable as exc:
            out.append(AnnualYear(end.year, end, None, None,
                                  f"missing {', '.join(exc.missing)}: {exc.reason}"))
            continue
        with localcontext() as ctx:
            ctx.prec = 40
            margin = Decimal(b.fcff.amount_minor) / Decimal(b.revenue.amount_minor)
        out.append(AnnualYear(end.year, end, b, margin, None))
    return tuple(out)


class WindowUnavailable(ValuationUnavailable):
    """A window that cannot be averaged — every absent or unusable year named."""


def _window(annual_rows, first: int, last: int, *, ticker: str, as_of: date):
    history = {y.fiscal_year: y for y in annual_history(annual_rows, ticker=ticker, as_of=as_of)}
    wanted = range(first, last + 1)
    absent = [f"FY{y}" for y in wanted if y not in history]
    unusable = [f"FY{y} ({history[y].unavailable})" for y in wanted
                if y in history and history[y].basis is None]
    if absent or unusable:
        raise WindowUnavailable(
            ticker, as_of, absent + [u.split(" ", 1)[0] for u in unusable],
            f"window FY{first}–FY{last} cannot be averaged — absent {absent}, unavailable "
            f"{unusable}. ⚠ Averaging around a gap would drop exactly the years that make "
            f"the cycle (F10 D5, P5)")
    years = [history[y] for y in wanted]
    currencies = {y.basis.fcff.currency for y in years}
    if len(currencies) != 1:
        raise WindowUnavailable(ticker, as_of, ["currency"],
                                f"window mixes currencies {sorted(currencies)}")
    return years, currencies.pop()


def cycle_average_fcff(annual_rows, first: int, last: int, *, ticker: str, as_of: date):
    """Mean annual `D6` FCFF over the window. Returns `(Money, years)`."""
    years, currency = _window(annual_rows, first, last, ticker=ticker, as_of=as_of)
    total = Money(sum(y.basis.fcff.amount_minor for y in years), currency)
    return total.div_int(len(years)), years


def cycle_average_fcff_margin(annual_rows, quarterly_rows, first: int, last: int, *,
                              ticker: str, as_of: date):
    """Mean FCFF margin over the window × trailing revenue. Returns
    `(Money, years, mean_margin, trailing_revenue)`."""
    years, _ = _window(annual_rows, first, last, ticker=ticker, as_of=as_of)
    with localcontext() as ctx:
        ctx.prec = 40
        mean = sum((y.margin for y in years), Decimal(0)) / Decimal(len(years))
    revenue = trailing_total(quarterly_rows, "revenue", as_of=as_of, ticker=ticker)
    return revenue.mul_rate(mean), years, mean, revenue
