"""F14 — size one trade in one account against D-11's REPORTED balance. AC-F14.1…F14.17.

```
  risk_capital = min( capital · r_ceiling · E·C·P·D ,            ← the ceiling (PS-33)
                      (capital · r_total − committed) / n_reserve )  ← only when committed is measured
  deploy       = min( risk_capital / d · entry ,  cash ,  15 % of capital )      (PS-28, PS-10)
  shares       = floor(deploy / entry)                                          (F14 D7)
```

★★ **PS-8: a consequence of stated inputs, never a proposal.** Every input on the answer
carries where it came from and, for the holdings export, the date it is as of.

★ **One sizing path** (`DX-191`, F14 `D12`): the arithmetic is `sizing/trade.py::size_trade`,
which the library's `size_for_stop` also calls. This module only gathers and labels the inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from src.portfolio.contracts.sizing import ThresholdCrossing
from src.portfolio.errors import (
    NoStopError, PolicyMissingError, UnavailableInputError,
)
from src.portfolio.pyramid.scale import pyramid_check
from src.portfolio.sizing.risk_based import (
    CONCENTRATION_THRESHOLD_PCT, committed_risk, n_reserve, risk_budget,
)
from src.portfolio.sizing.trade import size_trade
from src.portfolio.sizing.stop_distance import (
    DEFAULT_HORIZON_DAYS, DEFAULT_K, implied_k, stop_distance,
)

POLICY_PATH = "config/portfolio_policy.yaml"

#: PS-23 — the realised window, in returns; it needs one close more.
SIGMA_WINDOW = 21

#: RC-4 / PS-20 — the account type the fund excludes.
EXCLUDED_FROM_FUND = ("RESP",)

HOLDINGS = "holdings_export"


@dataclass(frozen=True, slots=True)
class Policy:
    """CT-F14.2 — Victor's stated numbers for one account (PS-43, D6)."""

    account_id: str
    r_total: float
    r_ceiling: float
    target_positions: int
    source: str


def load_policy(account_id: str, path=POLICY_PATH) -> Policy:
    """PS-43 — no default for any value; a gap raises naming it."""
    import yaml

    path = Path(path)
    if not path.exists():
        raise PolicyMissingError(account_id, path, "no policy file")
    accounts = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("accounts") or {}
    entry = accounts.get(account_id)
    if not entry:
        raise PolicyMissingError(account_id, path, f"no policy for {account_id}")
    for key in ("r_total", "r_ceiling", "target_positions"):
        if entry.get(key) is None:
            raise PolicyMissingError(account_id, path, f"`{key}` is not stated")
    r_total, r_ceiling = float(entry["r_total"]), float(entry["r_ceiling"])
    target = entry["target_positions"]
    if not 0 < r_total <= 1:
        raise PolicyMissingError(account_id, path, f"`r_total` {r_total} is not in (0, 1]")
    if not 0 < r_ceiling <= r_total:
        raise PolicyMissingError(account_id, path,
                                 f"`r_ceiling` {r_ceiling} is not in (0, r_total={r_total}]")
    if not isinstance(target, int) or target < 1:
        raise PolicyMissingError(account_id, path,
                                 f"`target_positions` {target!r} is not an integer ≥ 1")
    return Policy(account_id, r_total, r_ceiling, target, str(path))


@dataclass(frozen=True, slots=True)
class Sigma:
    """σ and its label (PS-23): `realised · …`, `stated`, or `unavailable: why`."""

    value: float | None
    source: str


def realised_sigma(closes, *, source: str, window: int = SIGMA_WINDOW) -> Sigma:
    """PS-23 — the sample sd of the last `window` daily log returns of the closes.

    ⚠ Fewer than `window + 1` closes is `unavailable` — never a shorter window, which would
    be indistinguishable in the output from a real one (PD-9's rule, one domain over).
    """
    closes = sorted(closes)
    if len(closes) < window + 1:
        return Sigma(None, f"unavailable: {len(closes)} closes, {window + 1} needed")
    tail = closes[-(window + 1):]
    if any(c <= 0 for _d, c in tail):
        return Sigma(None, "unavailable: a non-positive close in the window")
    rets = [math.log(b / a) for (_da, a), (_db, b) in zip(tail, tail[1:])]
    mean = sum(rets) / len(rets)
    sd = math.sqrt(sum((r - mean) ** 2 for r in rets) / (len(rets) - 1))
    return Sigma(sd, f"realised · {source} · {window} sessions to {tail[-1][0].isoformat()}")


@dataclass(frozen=True, slots=True)
class SizingOnDemand:
    """CT-F14.1 — not a number: the number, every input with its source, and the book."""

    ticker: str
    account_id: str
    as_of: date
    inputs: dict
    risk_budget: dict
    account_risk: dict
    risk_capital: dict
    notional: dict
    binding_constraint: str
    shares: int
    shares_exact: float
    deploy_notional: float
    consequences: dict
    thresholds_crossed: tuple = ()
    pyramid: dict | None = None
    book_wide: str = ""
    unavailable: tuple = ()
    assumptions: tuple = field(default_factory=tuple)

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "account_id": self.account_id,
            "as_of": self.as_of.isoformat(), "inputs": self.inputs,
            "risk_budget_factors": self.risk_budget, "account_risk": self.account_risk,
            "risk_capital": self.risk_capital, "notional": self.notional,
            "binding_constraint": self.binding_constraint, "shares": self.shares,
            "shares_exact": self.shares_exact, "deploy_notional": self.deploy_notional,
            "consequences": self.consequences,
            "thresholds_crossed": [t.to_json_obj() for t in self.thresholds_crossed],
            "pyramid": self.pyramid, "book_wide": self.book_wide,
            "unavailable": list(self.unavailable), "assumptions": list(self.assumptions),
            "statement": "a consequence of the stated inputs, not a recommendation (PS-8)",
        }

    def render(self, *, today: date | None = None) -> str:
        today = today or date.today()
        i, n, ccy = self.inputs, self.notional, self.notional["currency"]
        age = (today - self.as_of).days
        k = i["k"]
        lines = [
            f"{self.ticker} in {self.account_id} — {self.shares} shares "
            f"({self.shares_exact:.4f} exact), deploy {self.deploy_notional:,.2f} {ccy}",
            f"  binds: {self.binding_constraint}   ·   risk {n['risk']:,.2f} · cash "
            f"{n['cash']:,.2f} · 15 % cap {n['cap_15pct']:,.2f} {ccy}",
            "",
            f"  capital  {i['capital_base']['value']:,.2f} CAD  (holdings export as of "
            f"{self.as_of.isoformat()}, {age} days old)",
            f"  cash     {i['cash_available']['value']:,.2f} CAD  (holdings export; a USD buy "
            f"assumes BMO's auto-FX from CAD cash)",
            f"  entry    {i['entry']['value']} {i['entry']['currency']}  (stated)",
            f"  stop     {i['stop']['value']:.4f} {i['entry']['currency']}  ({i['stop']['source']})",
            f"  σ        {_fmt(i['sigma']['value'])}  ({i['sigma']['source']})",
            f"  k        {_fmt(k['value'])}  ({k['source']})",
        ]
        if i.get("fx_usd_cad", {}).get("value") is not None:
            lines.append(f"  USD→CAD  {i['fx_usd_cad']['value']}  (holdings export footer)")
        rb = self.risk_budget
        lines += [
            f"  policy   r_total {i['r_total']['value']} · r_ceiling {i['r_ceiling']['value']} · "
            f"target_positions {i['target_positions']['value']}  ({i['r_ceiling']['source']})",
            f"  budget   {rb['effective']:.4%} — budget = ceiling, because E, C, P, D are not "
            f"measured yet (PS-34)",
            f"  risk     {self.risk_capital['value']:,.2f} CAD at the stop  "
            f"(binds: {self.risk_capital['binds']})",
        ]
        ar = self.account_risk
        if ar["committed_status"] == "measured":
            lines.append(f"  account  allowance {ar['allowance']:,.2f} · committed "
                         f"{ar['committed']:,.2f} · remaining {ar['remaining']:,.2f} CAD · "
                         f"n_reserve {ar['n_reserve']}")
        else:
            lines.append(f"  account  allowance {ar['allowance']:,.2f} CAD · committed "
                         f"UNMEASURED (no held stop for {', '.join(i['held_stops']['missing'])}) "
                         f"· n_reserve {ar['n_reserve']} — only r_ceiling binds")
        c = self.consequences
        lines.append(f"  weight   {c['weight_account_pct']:.2f} % of the account · fund: "
                     f"{c['weight_fund_pct']}")
        for t in self.thresholds_crossed:
            lines.append(f"  ⚠ {t.name} {t.value:.2f} > {t.limit} (reported only)")
        if self.pyramid:
            p = self.pyramid
            lines.append(f"  M-3      held: average cost {p['avg_cost_before']:.4f} → "
                         f"{p['avg_cost_after']:.4f}" + ("  ⚠ scale-in (flagged, never blocked)"
                                                         if p["is_scale_in"] else ""))
        lines.append(f"  book     {self.book_wide}")
        for u in self.unavailable:
            lines.append(f"  ∅ {u}")
        lines.append("  ★ a consequence of the stated inputs, not a recommendation (PS-8)")
        return "\n".join(lines)


def _fmt(v):
    return "unavailable" if v is None else f"{v:.6g}"


def size_on_demand(*, ticker: str, account_id: str, entry: float, currency: str,
                   stop: float | None, statement, policy: Policy, sigma: Sigma,
                   held_stops: dict, discovered_accounts=(), accounts_with_holdings=None,
                   k: float = DEFAULT_K) -> SizingOnDemand:
    """F14 §4 steps 3–9. `statement` is D-11's `HoldingsStatement` (RC-70…RC-75)."""
    ticker = ticker.upper()
    as_of = statement.as_of
    capital = statement.balance
    unavailable = []

    # ── step 7, FX (PS-4, FX-3) — a USD entry needs the footer rate, or nothing.
    if currency == "CAD":
        fx = 1.0
    elif currency == "USD":
        if statement.usd_cad is None:
            raise UnavailableInputError(
                f"{ticker} sizing in {account_id}",
                f"the entry is USD and {statement.source_file} carries no `1 USD = r CAD` rate")
        fx = statement.usd_cad
    else:
        raise UnavailableInputError(f"{ticker}", f"currency {currency!r} is not CAD or USD")

    # ── step 4, committed risk (PS-29, D4) — from the REPORTED average cost.
    held = {line.analysis_symbol: line for line in statement.lines}
    unknown = sorted(set(held_stops) - set(held))
    if unknown:
        raise UnavailableInputError(
            f"--held-stop {', '.join(unknown)}", f"{account_id} holds no such line "
            f"(it holds {', '.join(sorted(held)) or 'nothing'})")
    missing_stops = sorted(set(held) - set(held_stops))
    if missing_stops:
        committed = None
        status = "unmeasured"
    else:
        committed = sum(committed_risk([{
            "entry": line.average_cost, "stop": held_stops[sym], "shares": line.quantity}])
            * (statement.usd_cad if line.cost_currency == "USD" else 1.0)
            for sym, line in held.items())
        status = "measured"

    # ── PS-27/PS-43 — a held ticker is sized into its OWN slot (AC-F14.16).
    is_held = ticker in held
    slots = n_reserve(account_id=account_id, target_positions=policy.target_positions,
                      current_positions=len(held) - (1 if is_held else 0))

    # ── step 3, the budget (PS-33, PS-34, D3) — four factors, all unmeasured.
    budget = risk_budget(r_ceiling=policy.r_ceiling)

    # ── step 6, the stop (PS-5, PS-6, PS-7, D5).
    if stop is None:
        if sigma.value is None:
            raise NoStopError(ticker, f"no stop stated and no σ ({sigma.source}) for a "
                                      f"volatility stop")
        distance = stop_distance(entry=entry, sigma=sigma.value, sigma_source=sigma.source,
                                 k=k)
        stop_value, stop_source = entry - distance.per_share, "volatility_stop"
        k_input = {"value": k, "source": "default (QS-2 open)" if k == DEFAULT_K else "stated"}
    else:
        stop_value, stop_source = float(stop), "stated"
        if sigma.value is not None:
            k_input = {"value": implied_k(entry=entry, stop=stop_value, sigma=sigma.value,
                                          sigma_source=sigma.source).k,
                       "source": "implied by the stated stop"}
        else:
            k_input = {"value": None, "source": "implied by the stated stop"}
            unavailable.append(f"implied_k: σ {sigma.source}")
    per_share = entry - stop_value
    if per_share <= 0:
        raise NoStopError(ticker, f"stop {stop_value} is at or above entry {entry}")

    # ── step 8 — ★ the ONE sizing path (DX-191, F14 D12): §5.1b and PS-28 in `size_trade`.
    trade = size_trade(capital_base=capital, ceiling_rate=budget.effective,
                       r_total=policy.r_total, committed=committed, n_reserve=slots,
                       entry=entry, stop_per_share=per_share,
                       cash_available=statement.cash_total, fx=fx)
    shares = trade.shares

    # ── step 9, consequences (thresholds report, never veto — INV-026).
    held_cad = held[ticker].market_value_cad if is_held else 0.0
    weight = 100.0 * (held_cad + shares * entry * fx) / capital
    crossings = ((ThresholdCrossing("CONCENTRATION_THRESHOLD_PCT",
                                    CONCENTRATION_THRESHOLD_PCT, weight),)
                 if weight > CONCENTRATION_THRESHOLD_PCT else ())
    account_type = account_id.rsplit("_", 1)[0]
    with_holdings = set(accounts_with_holdings or (account_id,))
    lacking = sorted(set(discovered_accounts) - with_holdings)
    if account_type in EXCLUDED_FROM_FUND:
        fund = "excluded (RC-4)"
    elif lacking:
        fund = f"UNCHECKED — no holdings export for {', '.join(lacking)} (RC-77)"
    else:
        fund = "not computed — F14 sizes per account (PS-19)"
    book_wide = (f"UNCHECKED — no holdings export for {', '.join(lacking)} (RC-77, RK-5)"
                 if lacking else "every discovered account has a holdings export; F14 "
                                 "computes no book-wide figure (PS-19)")
    unavailable += ["sector / theme exposure: no D-05 pass on a valued book"]

    pyramid = None
    if is_held:
        line = held[ticker]
        pyramid = pyramid_check(ticker=ticker, account_id=account_id, as_of=as_of,
                                held_shares=line.quantity, held_avg_cost=line.average_cost,
                                add_qty=shares, price=entry).to_json_obj()

    holdings = {"source": HOLDINGS, "as_of": as_of.isoformat()}
    inputs = {
        "capital_base": {"value": capital, "currency": "CAD", **holdings},
        "cash_available": {"value": statement.cash_total, "currency": "CAD", **holdings},
        "entry": {"value": entry, "currency": currency, "source": "stated"},
        "stop": {"value": stop_value, "currency": currency, "source": stop_source},
        "sigma": {"value": sigma.value, "source": sigma.source},
        "k": k_input,
        "r_total": {"value": policy.r_total, "source": policy.source},
        "r_ceiling": {"value": policy.r_ceiling, "source": policy.source},
        "target_positions": {"value": policy.target_positions, "source": policy.source},
        "held_stops": {"value": dict(held_stops), "source": "stated", "missing": missing_stops},
    }
    if currency == "USD":
        inputs["fx_usd_cad"] = {"value": fx, **holdings}

    return SizingOnDemand(
        ticker=ticker, account_id=account_id, as_of=as_of, inputs=inputs,
        risk_budget=budget.to_json_obj(),
        account_risk={"allowance": trade.allowance, "committed": trade.committed,
                      "committed_status": status, "remaining": trade.remaining,
                      "n_reserve": slots, "currency": "CAD",
                      "committed_basis": "max(0, average cost − held stop) × shares"},
        risk_capital={"value": trade.risk_capital, "currency": "CAD",
                      "binds": trade.risk_binds},
        notional={"risk": trade.notional_risk, "cash": trade.notional_cash,
                  "cap_15pct": trade.notional_cap, "currency": currency},
        binding_constraint=trade.binding, shares=trade.shares,
        shares_exact=trade.shares_exact, deploy_notional=trade.deploy,
        consequences={"weight_account_pct": round(weight, 4), "weight_fund_pct": fund},
        thresholds_crossed=crossings, pyramid=pyramid, book_wide=book_wide,
        unavailable=tuple(unavailable),
        assumptions=("a USD buy is funded from the account's total cash via BMO's auto-FX "
                     "(F14 D9)", f"holding horizon {DEFAULT_HORIZON_DAYS} sessions (PS-6)"))
