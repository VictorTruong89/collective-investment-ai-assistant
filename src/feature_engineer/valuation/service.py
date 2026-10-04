"""`T1` / `T2` — `valuation()` (`fv_model`) and `value_on_basis()` (`fv_analyst`).

★ **Inputs come only through D-07's public API** (`FE-23`): `get_fundamentals`
for line items, `get_prices(adj_as_of=None)` for the RAW price (`FE-9`, DE-45 —
a per-share value compares with what a person actually saw, not a restated
series). ⚠ `as_of` is required and never defaulted (`FE-7`, `INV-1`).
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from src.feature_engineer.errors import AsOfRequiredError, ValuationUnavailable
from src.feature_engineer.valuation.assumptions import Assumptions
from src.feature_engineer.valuation.band import band
from src.feature_engineer.valuation.basis import balance, reported_basis, trailing_total
from src.feature_engineer.valuation.dcf import discount, per_share
from src.feature_engineer.valuation.implied import implied_by_duration, solve_implied
from src.feature_engineer.valuation.types import (
    AnalystValuation,
    CashFlowBasis,
    ValuationResult,
)
from src.shared.money import Money

_UNSET = object()
#: How far back the price lookup reaches for the last trading day ≤ as_of.
#: ★ A holiday cluster, never a stale quote: longer than any market closure.
_PRICE_LOOKBACK_DAYS = 10


def _raw_price(engine, ticker: str, as_of: date) -> tuple[Money, date]:
    frame = engine.get_prices(ticker, as_of - timedelta(days=_PRICE_LOOKBACK_DAYS), as_of,
                              adj_as_of=None)
    if frame is None or not len(frame):
        raise ValuationUnavailable(ticker, as_of, ["price"], "no raw close knowable at as_of")
    frame = frame.assign(_d=frame["date"].map(lambda d: pd.Timestamp(d).date()))
    frame = frame[frame["_d"] <= as_of].sort_values("_d", kind="mergesort")
    if not len(frame):
        raise ValuationUnavailable(ticker, as_of, ["price"], "no raw close knowable at as_of")
    last = frame.iloc[-1]
    return Money(int(last["close_minor"]), str(last["close_currency"])), last["_d"]


def _require_as_of(as_of, method: str) -> date:
    if as_of is _UNSET or as_of is None:
        raise AsOfRequiredError(method, "as_of")
    return as_of


def _assemble(cls, ticker: str, as_of: date, basis: CashFlowBasis, *, engine,
              assumptions: Assumptions, rows: pd.DataFrame):
    net_debt, components, shares = balance(rows, as_of=as_of, ticker=ticker)
    price, price_date = _raw_price(engine, ticker, as_of)
    trail = discount(basis.base_fcff, discount_rate=assumptions.discount_rate,
                     stage1_growth=assumptions.stage1_growth,
                     terminal_growth=assumptions.terminal_growth,
                     explicit_years=assumptions.explicit_years)
    equity, vps = per_share(trail.enterprise_value, net_debt, shares)
    solve_inputs = dict(price=price, base_fcff=basis.base_fcff, net_debt=net_debt,
                        diluted_shares=shares, assumptions=assumptions)
    # ✏ `D11` — only a set that declares a duration table needs revenue; ⚠ absent revenue
    #   raises `ValuationUnavailable` naming it, never a share over a substitute (P5).
    revenue = (trailing_total(rows, "revenue", as_of=as_of, ticker=ticker)
               if assumptions.declares_duration_table else None)
    return cls(
        ticker=ticker.upper(), as_of=as_of, assumptions_obj=assumptions, basis=basis,
        trail=trail, net_debt=net_debt, net_debt_components=components, equity_value=equity,
        diluted_shares=shares, value_per_share=vps, price=price, price_date=price_date,
        band=band(basis.base_fcff, net_debt, shares, assumptions=assumptions),
        implied=solve_implied(**solve_inputs),
        # ✏ `D10` — raw price × diluted shares, so no prompt multiplies it (`RA-45`).
        market_capitalisation=Money(price.amount_minor * shares, price.currency),
        implied_by_duration=implied_by_duration(**solve_inputs, trailing_revenue=revenue),
        trailing_revenue=revenue,
    )


def valuation(ticker: str, as_of=_UNSET, *, engine, assumptions: Assumptions
              ) -> ValuationResult:
    """`fv_model` — the mechanics on `D6`'s judgement-free reported basis."""
    as_of = _require_as_of(as_of, "valuation")
    rows = engine.get_fundamentals(ticker, as_of, period_type="quarterly")
    basis = reported_basis(rows, as_of=as_of, ticker=ticker)
    return _assemble(ValuationResult, ticker, as_of, basis, engine=engine,
                     assumptions=assumptions, rows=rows)


def value_on_basis(ticker: str, as_of=_UNSET, *, basis: CashFlowBasis, engine,
                   assumptions: Assumptions) -> AnalystValuation:
    """`fv_analyst` — the SAME mechanics on a judgement's basis (`D1`, `VS-4`).

    ⚠ Refuses a reported basis: this must not become a second road to `fv_model`.
    """
    as_of = _require_as_of(as_of, "value_on_basis")
    if basis.origin != "judgement":
        raise ValueError(
            "value_on_basis takes a judgement basis only — a reported basis is valued by "
            "valuation() and is fv_model (F10 VS-1, AC-F10.13)")
    rows = engine.get_fundamentals(ticker, as_of, period_type="quarterly")
    return _assemble(AnalystValuation, ticker, as_of, basis, engine=engine,
                     assumptions=assumptions, rows=rows)
