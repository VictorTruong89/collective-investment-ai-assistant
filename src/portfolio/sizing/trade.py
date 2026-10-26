"""D-06 §5.1b — THE sizing arithmetic, once. PS-10, PS-27, PS-28, PS-29. F14 AC-F14.19.

```
  risk_capital = min( capital · ceiling_rate ,                         ← r_ceiling × E·C·P·D
                      (capital · r_total − committed) / n_reserve )    ← only if both are known
  notional     = min( risk_capital / d · entry ,   cash ,   15 % · capital )
  shares       = floor(notional / entry)
```

★★ **`DX-191` — why this module exists.** `size_for_stop` computed its own version: it divided
the per-trade ceiling by `n_reserve` (no `r_total`), and when cash bound it LABELLED the answer
`cash` but returned the risk-sized shares — the `PS-28` table's 444 shares came back as 666. ⚠ Two
functions computing one formula drift; so both callers (`size_for_stop`, F14's
`size_on_demand`) now compute here and nowhere else (F14 `D12`).

Pure: no file, no network, no clock. Money is in the BASE currency (CAD) except the three
notionals and `deploy`, which are in the ENTRY currency (`fx` = base per unit of entry currency).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.portfolio.contracts.sizing import MAX_POSITION_PCT

RISK, CASH, CAP = "risk", "cash", "cap_15pct"
R_CEILING, RESERVE = "r_ceiling", "risk_remaining / n_reserve"


@dataclass(frozen=True, slots=True)
class TradeSize:
    risk_capital: float            # base — the most this trade may lose at the stop
    risk_binds: str                # R_CEILING | RESERVE
    allowance: float | None        # base — capital · r_total (PS-30)
    committed: float | None        # base — None = unmeasured, never 0 (PS-34's shape)
    remaining: float | None
    n_reserve: int
    notional_risk: float           # entry ccy — what risk alone allows, kept even when capped
    notional_cash: float | None    # entry ccy — None = cash not a constraint
    notional_cap: float            # entry ccy — MAX_POSITION_PCT of capital (PS-10)
    binding: str                   # RISK | CASH | CAP
    deploy: float                  # entry ccy — min of the three
    shares_exact: float
    shares: int                    # whole, floored (F14 D7)


def size_trade(*, capital_base: float, ceiling_rate: float, r_total: float | None,
               committed: float | None, n_reserve: int, entry: float,
               stop_per_share: float, cash_available: float | None = None,
               fx: float = 1.0) -> TradeSize:
    """§5.1b and PS-28 exactly as written. `stop_per_share` is `entry − stop` > 0."""
    if stop_per_share <= 0:
        raise ValueError(f"stop distance {stop_per_share} must be > 0 (PS-5)")
    if n_reserve <= 0:
        raise ValueError(f"n_reserve {n_reserve} must be > 0 (PS-43)")

    ceiling = capital_base * ceiling_rate
    allowance = capital_base * r_total if r_total is not None else None
    if allowance is None or committed is None:
        # ⚠ An unknown remaining is never guessed: only the ceiling can bind (F14 D4).
        remaining = None
        risk_capital, risk_binds = ceiling, R_CEILING
    else:
        remaining = max(0.0, allowance - committed)
        reserve = remaining / n_reserve
        risk_capital, risk_binds = ((ceiling, R_CEILING) if ceiling <= reserve
                                    else (reserve, RESERVE))

    notional_risk = risk_capital / (stop_per_share * fx) * entry
    notional_cap = capital_base * MAX_POSITION_PCT / 100.0 / fx
    candidates = [(notional_risk, RISK)]
    if cash_available is not None:
        candidates.append((max(0.0, cash_available) / fx, CASH))
    candidates.append((notional_cap, CAP))
    deploy, binding = min(candidates, key=lambda c: c[0])   # a tie names the first: risk, cash, cap
    shares_exact = deploy / entry
    return TradeSize(
        risk_capital=risk_capital, risk_binds=risk_binds, allowance=allowance,
        committed=committed, remaining=remaining, n_reserve=n_reserve,
        notional_risk=notional_risk,
        notional_cash=None if cash_available is None else max(0.0, cash_available) / fx,
        notional_cap=notional_cap, binding=binding, deploy=deploy,
        shares_exact=shares_exact, shares=math.floor(shares_exact + 1e-9))
