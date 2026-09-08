"""D-06 CT-6.1 — `SizingAnswer`. PS-8, PS-10, PS-28, PS-33, PS-34.

★★ **PS-8: D-06 computes the risk-based size; it does not propose it.** The
output is *"at a 2 % risk budget and a 1.5σ stop this is 340 shares"* — **a
consequence of stated assumptions**, not an answer to *"what should I do".*

⚠ **§5.3's collision, and why the distinction is load-bearing.** `shares ∝ 1/σ`
means high-volatility names get small positions; **the AI/semiconductor theme is
high-volatility and M-2 says concentration in it is a DELIBERATE BET.** Applied
as a *recommendation*, the textbook rule would quietly implement the
diversification pressure M-2 rejects — **one trade at a time, with arithmetic as
the alibi.**
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: L0 §config — INV-022. ★ Caps what the system PROPOSES, never what may be held.
MAX_POSITION_PCT = 15.0

#: RK-2/INV-026, one domain over. There is no other value.
REPORTED_ONLY = "reported_only"

#: PS-34's statuses. ★ `unapplied` and `unmeasured` are different findings:
#: *we measured and it did not differentiate* vs *we could not measure*.
APPLIED, UNAPPLIED, UNMEASURED = "applied", "unapplied", "unmeasured"


@dataclass(frozen=True, slots=True)
class Factor:
    """One term of `r_ceiling × E × C × P × D` (PS-33, PS-34).

    ⚠ **A factor that cannot be measured is 1.0 and says so** — never estimated,
    never quietly omitted. ★ Setting it to 1 keeps the budget *visibly
    incomplete* rather than quietly smaller.
    """

    name: str
    value: float
    status: str
    why: str = ""
    source: str = ""
    method_id: str = ""

    def __post_init__(self) -> None:
        if self.status not in (APPLIED, UNAPPLIED, UNMEASURED):
            raise ValueError(f"factor status {self.status!r} is not one of "
                             f"{(APPLIED, UNAPPLIED, UNMEASURED)} (PS-34)")
        if not 0.0 < self.value <= 1.0:
            # ★ INV-022 made structural: the product cannot exceed r_ceiling.
            raise ValueError(
                f"factor {self.name!r}={self.value}: every factor is bounded in "
                f"(0, 1], which is what makes INV-022 hold BY CONSTRUCTION "
                f"rather than by a clamp bolted on afterwards (PS-33)")
        if self.status != APPLIED and self.value != 1.0:
            raise ValueError(
                f"factor {self.name!r} is {self.status!r} with value "
                f"{self.value}. ⚠ An unapplied factor is 1.0 — anything else is "
                f"an estimate wearing a disclaimer (PS-34)")
        if self.status != UNMEASURED and not (self.source or self.method_id):
            raise ValueError(
                f"factor {self.name!r} is {self.status!r} and names neither a "
                f"source nor a MethodEntry (PS-33, PS-36)")

    def to_json_obj(self) -> dict:
        return {"name": self.name, "value": round(self.value, 6),
                "status": self.status, "why": self.why, "source": self.source,
                "method_id": self.method_id}


@dataclass(frozen=True, slots=True)
class RiskBudget:
    """PS-33 — ★ **computed per trade, not configured.**

    *A budget the reader cannot decompose is a number with an author.*
    """

    r_ceiling: float
    factors: tuple[Factor, ...]
    method_id: str = "risk_budget_dynamic_v1"

    @property
    def effective(self) -> float:
        value = self.r_ceiling
        for factor in self.factors:
            value *= factor.value
        return value

    def to_json_obj(self) -> dict:
        obj = {"r_ceiling": self.r_ceiling, "method_id": self.method_id,
               "effective": round(self.effective, 8)}
        for factor in self.factors:
            obj[factor.name] = factor.to_json_obj()
        return obj


@dataclass(frozen=True, slots=True)
class ThresholdCrossing:
    name: str
    limit: float
    value: float
    effect: str = REPORTED_ONLY

    def __post_init__(self) -> None:
        if self.effect != REPORTED_ONLY:
            from src.portfolio.errors import TargetAllocationError
            raise TargetAllocationError(
                f"threshold {self.name!r} with effect={self.effect!r}")

    def to_json_obj(self) -> dict:
        return {"name": self.name, "limit": self.limit, "value": self.value,
                "effect": self.effect}


@dataclass(frozen=True, slots=True)
class SizingAnswer:
    """CT-6.1 — ★ *not a number. A number, its assumptions, and what it does to
    the book.*"""

    ticker: str
    account_id: str
    as_of: date
    arithmetic: dict
    assumptions: dict
    risk_budget: RiskBudget
    account_risk: dict
    binding_constraint: dict
    consequences: dict
    thresholds_crossed: tuple[ThresholdCrossing, ...] = ()
    risk_parity: dict | None = None
    pyramid: dict | None = None
    #: PS-10 / AC-6.8 — ★ applies **only** to a system-computed size.
    capped_by_inv022: bool = False
    #: PS-9 — the human's number in, the implied budget out.
    source: str = "system"
    unavailable: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.source != "system" and self.capped_by_inv022:
            raise ValueError(
                "a human-supplied size was marked capped. ★ INV-022 caps only "
                "what the SYSTEM proposes; the human's own size is reported "
                "with its consequences, never capped (PS-10, INV-026, M-2)")

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "account_id": self.account_id,
            "as_of": self.as_of.isoformat(), "arithmetic": dict(self.arithmetic),
            "assumptions": dict(self.assumptions),
            "risk_budget_factors": self.risk_budget.to_json_obj(),
            "account_risk": dict(self.account_risk),
            "binding_constraint": dict(self.binding_constraint),
            "consequences": dict(self.consequences),
            "thresholds_crossed": [t.to_json_obj() for t in self.thresholds_crossed],
            "risk_parity": self.risk_parity, "pyramid": self.pyramid,
            "capped_by_inv022": self.capped_by_inv022, "source": self.source,
            "unavailable": list(self.unavailable),
        }
