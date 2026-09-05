"""D-06 §5.1/§5.1b/§5.1d — sizing given a stop. PS-2…PS-10, PS-27…PS-35, PS-43.

```
        risk_capital  =  capital_base × risk_budget_pct     ← what you can LOSE
        shares        =  risk_capital / (entry − stop)
        notional      =  shares × entry                     ← what you DEPLOY
```

★★ **The single most confused idea in position sizing.** *"I risk 2 % per trade"
says NOTHING about how concentrated the book is* — the same 2 % produces a 15 %
position or a 90 % one, and **the stop width does all of it.**
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.portfolio.contracts.sizing import (
    APPLIED, MAX_POSITION_PCT, REPORTED_ONLY, UNAPPLIED, UNMEASURED, Factor,
    RiskBudget, SizingAnswer, ThresholdCrossing,
)
from src.portfolio.errors import (
    NoStopError, ReserveUnavailableError, UnavailableInputError,
)
from src.portfolio.sizing.stop_distance import implied_k

FORMULA_ID = "risk_budget_dynamic_v1"

#: L0 §8, one domain over — reporting thresholds, every one (INV-026).
CONCENTRATION_THRESHOLD_PCT = 25.0
SECTOR_MAX_PCT = 35.0
THEME_REPORT_THRESHOLD_PCT = 40.0


@dataclass(frozen=True, slots=True)
class RiskBudgetState:
    """PS-29/PS-30 — allowance · committed · remaining, **per account**."""

    account_id: str
    as_of: date
    allowance: float
    committed: float
    currency: str = "CAD"
    committed_basis: str = "max(0, entry-stop) x shares"

    @property
    def remaining(self) -> float:
        return max(0.0, self.allowance - self.committed)

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "as_of": self.as_of.isoformat(),
                "allowance": self.allowance, "committed": self.committed,
                "remaining": self.remaining, "currency": self.currency,
                "committed_basis": self.committed_basis}


def committed_risk(positions) -> float:
    """PS-29 — ★ `max(0, entry − stop) × shares`.

    *A position whose stop has trailed above entry **releases its budget without
    being sold*** (M-3). ⚠ The alternative convention — mark-to-market risk from
    the current price — **would keep a winner charged forever and quietly
    penalise holding**, which is the exact behaviour M-3 asks us to encourage.
    """
    return sum(max(0.0, p["entry"] - p["stop"]) * p["shares"] for p in positions)


def account_risk(*, account_id: str, as_of: date, capital_base: float,
                 r_ceiling: float, open_positions=(), currency: str = "CAD"
                 ) -> RiskBudgetState:
    """PS-30 — ⚠ **never netted across accounts.** Registered accounts hold
    capital that cannot be moved between them."""
    return RiskBudgetState(account_id=account_id, as_of=as_of,
                           allowance=capital_base * r_ceiling,
                           committed=committed_risk(open_positions),
                           currency=currency)


def n_reserve(*, account_id: str, target_positions: int | None,
              current_positions: int) -> int:
    """PS-27 / PS-43 / AC-6.9l — ★ the account's **open slots**, a stated policy.

    ⚠ **Never derived from free cash**: *deriving it from cash is circular —
    total deployable notional is `R × entry/d` independent of `n`.*
    """
    if target_positions is None:
        raise ReserveUnavailableError(
            account_id, "target_positions was not supplied")
    slots = target_positions - current_positions
    if slots <= 0:
        raise ReserveUnavailableError(
            account_id,
            f"n_reserve={slots} ({target_positions} target − {current_positions} "
            f"held): the account is full. ★ There is no open slot to size into, "
            f"and a budget computed anyway would be sizing a position the policy "
            f"says does not exist")
    return slots


def edge_factor(*, spread: float | None, mde: float | None,
                source: str = "D-03 rank_score") -> Factor:
    """PS-35 / AC-6.9j — ★ **the framework must be able to report that it cannot
    differentiate.**

    ⚠ *At IC ≈ 0.03 `E_i` may be statistically indistinguishable from 1 across
    the whole cross-section.* **Manufacturing differentiation from noise** is the
    failure this guard exists to prevent, so `E` applies only where the edge
    spread clears its own measurement error.
    """
    if spread is None or mde is None:
        return Factor("E_edge", 1.0, UNMEASURED,
                      why="no edge spread or no MDE published by D-03")
    if abs(spread) <= mde:
        return Factor("E_edge", 1.0, UNAPPLIED,
                      why=f"edge spread {spread:.4f} is inside its own MDE "
                          f"{mde:.4f} — indistinguishable from no edge",
                      source=source)
    return Factor("E_edge", min(1.0, abs(spread) / (abs(spread) + mde)), APPLIED,
                  source=source, method_id=FORMULA_ID)


def risk_budget(*, r_ceiling: float, edge=None, confidence=None, portfolio=None,
                drawdown=None) -> RiskBudget:
    """PS-33/PS-34 — ★ each factor **named, sourced and reported on the answer.**

    ⚠ `C_i` is unmeasurable until RM-1 is built; it shows as `unmeasured` so the
    budget is **visibly incomplete** rather than quietly wrong.
    """
    factors = (
        edge or Factor("E_edge", 1.0, UNMEASURED, why="no D-03 edge supplied"),
        confidence or Factor("C_confidence", 1.0, UNMEASURED,
                             why="RM-1 verdict stability not wired to sizing"),
        portfolio or Factor("P_portfolio", 1.0, UNMEASURED,
                            why="no D-05 marginal risk supplied"),
        drawdown or Factor("D_drawdown", 1.0, UNMEASURED,
                           why="no D-05 drawdown state supplied"),
    )
    return RiskBudget(r_ceiling=r_ceiling, factors=factors)


def size_for_stop(*, ticker: str, account_id: str, as_of: date, entry: float,
                  stop: float | None, capital_base: float, budget: RiskBudget,
                  sigma: float, sigma_source: str, sigma_class: str = "realised",
                  target_positions: int | None = None, current_positions: int = 0,
                  cash_available: float | None = None, book_weights=None,
                  currency: str = "CAD", fx_rate=None,
                  quote_currency: str | None = None) -> SizingAnswer:
    """PS-2…PS-10 — the size, its assumptions and what it does to the book.

    ⚠ **PS-8: this is a CONSEQUENCE of stated assumptions, not a proposal.**
    """
    if stop is None:
        raise NoStopError(ticker)
    if quote_currency and quote_currency != currency and fx_rate is None:
        # ★ PS-4/FX-3 — absent a rate the answer is unavailable, not estimated.
        raise UnavailableInputError(
            f"{ticker} sizing in {currency}",
            f"no FX rate for {quote_currency}->{currency}")

    slots = n_reserve(account_id=account_id, target_positions=target_positions,
                      current_positions=current_positions)
    state = account_risk(account_id=account_id, as_of=as_of,
                         capital_base=capital_base,
                         r_ceiling=budget.effective, currency=currency)
    # PS-27 — the per-trade budget is what remains, spread over the open slots.
    risk_capital = state.remaining / slots

    distance = implied_k(entry=entry, stop=stop, sigma=sigma,
                         sigma_source=sigma_source, sigma_class=sigma_class)
    if distance.per_share <= 0:
        raise NoStopError(ticker, f"stop {stop} is at or above entry {entry}")

    shares = risk_capital / distance.per_share
    notional = shares * entry

    # ── PS-10 / INV-022: cap what the SYSTEM proposes, and label the cap.
    capped = False
    ceiling = capital_base * MAX_POSITION_PCT / 100.0
    if notional > ceiling:
        capped = True
        shares = ceiling / entry
        notional = ceiling

    # ── PS-28: which constraint binds, with both numbers.
    risk_capacity_notional = notional
    if cash_available is not None and cash_available < notional:
        binds = {"binds": "cash", "risk_capacity_notional": risk_capacity_notional,
                 "cash_available": cash_available, "currency": currency}
    else:
        binds = {"binds": "risk_capacity",
                 "risk_capacity_notional": risk_capacity_notional,
                 "cash_available": cash_available, "currency": currency}

    consequences, crossings = _consequences(
        ticker=ticker, notional=notional, capital_base=capital_base,
        book_weights=book_weights or {})

    return SizingAnswer(
        ticker=ticker, account_id=account_id, as_of=as_of,
        arithmetic={"shares": shares, "notional": notional,
                    "risk_capital": risk_capital, **distance.to_json_obj()},
        assumptions={"risk_budget_pct": round(100.0 * budget.effective, 6),
                     "capital_base": capital_base,
                     "capital_base_as_of": as_of.isoformat(),
                     "horizon_days": distance.horizon_days,
                     "fx_rate_used": fx_rate, "n_reserve": slots,
                     "target_positions": target_positions,
                     "risk_source": "risk_remaining / n_reserve"},
        risk_budget=budget, account_risk=state.to_json_obj(),
        binding_constraint=binds, consequences=consequences,
        thresholds_crossed=crossings, capped_by_inv022=capped, source="system")


def implied_risk(*, ticker: str, account_id: str, as_of: date, entry: float,
                 stop: float | None, shares: float, capital_base: float,
                 sigma: float, sigma_source: str, sigma_class: str = "realised",
                 book_weights=None, currency: str = "CAD") -> SizingAnswer:
    """PS-9 / AC-6.7 — ★ **the human's intended size is a first-class input.**

    ⚠ *It never substitutes its own number for theirs* (INV-026 — D-06 does not
    overrule the seat that holds the P&L), and **the human's size is never
    capped** (PS-10).
    """
    if stop is None:
        raise NoStopError(ticker)
    distance = implied_k(entry=entry, stop=stop, sigma=sigma,
                         sigma_source=sigma_source, sigma_class=sigma_class)
    risk_capital = max(0.0, distance.per_share) * shares
    notional = shares * entry
    implied_pct = 100.0 * risk_capital / capital_base if capital_base else 0.0

    consequences, crossings = _consequences(
        ticker=ticker, notional=notional, capital_base=capital_base,
        book_weights=book_weights or {})
    return SizingAnswer(
        ticker=ticker, account_id=account_id, as_of=as_of,
        arithmetic={"shares": shares, "notional": notional,
                    "risk_capital": risk_capital, **distance.to_json_obj()},
        assumptions={"risk_budget_pct": round(implied_pct, 6),
                     "capital_base": capital_base,
                     "capital_base_as_of": as_of.isoformat(),
                     "horizon_days": distance.horizon_days,
                     "basis": "supplied share count; the budget is DERIVED "
                              "from it, not applied to it (PS-9)"},
        risk_budget=RiskBudget(r_ceiling=implied_pct / 100.0, factors=()),
        account_risk={}, binding_constraint={"binds": "human_supplied"},
        consequences=consequences, thresholds_crossed=crossings,
        capped_by_inv022=False, source="human")


def _consequences(*, ticker: str, notional: float, capital_base: float,
                  book_weights: dict):
    """§5.4's third block — *what it does to the book*, with thresholds as
    reports (INV-026)."""
    weight = 100.0 * notional / capital_base if capital_base else 0.0
    consequences = {
        "weight_account_pct": round(weight, 4),
        "sector_pct": round(book_weights.get("sector_pct", 0.0) + weight, 4),
        "theme_pct": round(book_weights.get("theme_pct", 0.0) + weight, 4),
        "weight_fund_pct": round(book_weights.get("fund_pct", weight), 4),
    }
    crossings = []
    if weight > CONCENTRATION_THRESHOLD_PCT:
        crossings.append(ThresholdCrossing(
            "CONCENTRATION_THRESHOLD_PCT", CONCENTRATION_THRESHOLD_PCT, weight))
    if consequences["sector_pct"] > SECTOR_MAX_PCT:
        crossings.append(ThresholdCrossing(
            "SECTOR_MAX_PCT", SECTOR_MAX_PCT, consequences["sector_pct"]))
    if consequences["theme_pct"] > THEME_REPORT_THRESHOLD_PCT:
        crossings.append(ThresholdCrossing(
            "THEME_REPORT_THRESHOLD_PCT", THEME_REPORT_THRESHOLD_PCT,
            consequences["theme_pct"]))
    return consequences, tuple(crossings)
