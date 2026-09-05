"""D-06 §7 — M-3, and the half that is usually forgotten. PS-15…PS-18, PS-21.

> **M-3:** *"Pyramiding-up is the behaviour to curb. The intended fix is to
> **sell less and let winners run**, not to scale in at ever-higher average cost.
> Features must serve **holding winners**, not only exiting."*

★ **PS-17: holding is a FIRST-CLASS computed alternative, not the absence of an
action.** ⚠ Most systems compute only the trim, which makes holding the thing
that happens when no button is pressed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: PS-21 — ★ **all four accounts are registered, so a trim triggers no
#: capital-gains event.** *No tax-lot reasoning is needed, and that is a
#: FINDING, not an omission*: the usual "tax cost of trimming" term is
#: identically zero here, which **strengthens M-3's "trim rather than exit"**
#: rather than weakening it.
TAX_EVENT = False


@dataclass(frozen=True, slots=True)
class PyramidCheck:
    """PS-15/PS-16 — ★ **flagged, never blocked** (INV-028, INV-026)."""

    ticker: str
    account_id: str
    as_of: date
    is_scale_in: bool
    avg_cost_before: float
    avg_cost_after: float
    added_exposure: float
    blocks: bool = False

    def __post_init__(self) -> None:
        if self.blocks:
            from src.portfolio.errors import TargetAllocationError
            raise TargetAllocationError("a pyramid check that blocks")

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker, "account_id": self.account_id,
                "as_of": self.as_of.isoformat(), "is_scale_in": self.is_scale_in,
                "avg_cost_before": round(self.avg_cost_before, 6),
                "avg_cost_after": round(self.avg_cost_after, 6),
                "added_exposure": round(self.added_exposure, 6),
                "blocks": False,
                "override": "a fund-manager override is logged and visible in "
                            "D-11's journal (RC-24), never prevented (PS-16)"}


def pyramid_check(*, ticker: str, account_id: str, as_of: date,
                  held_shares: float, held_avg_cost: float, add_qty: float,
                  price: float) -> PyramidCheck:
    """PS-15 — the resulting average cost, and whether it rose."""
    total = held_shares + add_qty
    after = ((held_shares * held_avg_cost + add_qty * price) / total
             if total else price)
    return PyramidCheck(
        ticker=ticker, account_id=account_id, as_of=as_of,
        is_scale_in=after > held_avg_cost, avg_cost_before=held_avg_cost,
        avg_cost_after=after, added_exposure=add_qty * price)


@dataclass(frozen=True, slots=True)
class HoldAlternative:
    """CT-6.3 — ★ what holding preserves, against what trimming realises."""

    ticker: str
    account_id: str
    as_of: date
    hold: dict
    trim: dict

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker, "account_id": self.account_id,
                "as_of": self.as_of.isoformat(), "hold": dict(self.hold),
                "trim": dict(self.trim)}


def hold_alternative(*, ticker: str, account_id: str, as_of: date,
                     shares: float, price: float, avg_cost: float,
                     trim_shares: float, remaining_size_check=None
                     ) -> HoldAlternative:
    """PS-17/PS-18 / AC-6.16, AC-6.17 — both sides, computed together.

    ⚠ **PS-18**: the trim block carries *the remaining position's* risk-based
    size, so *"should I trim"* and *"is what remains correctly sized"* are
    answered **together rather than sequentially**.
    """
    exposure = shares * price
    unrealised = (price - avg_cost) * shares
    return HoldAlternative(
        ticker=ticker, account_id=account_id, as_of=as_of,
        hold={"exposure": round(exposure, 6),
              "unrealised": round(unrealised, 6),
              "optionality_note": (
                  "M-3's stated fix is to sell less and let winners run; "
                  "holding is computed here as an alternative, not assumed as "
                  "the default (PS-17)")},
        trim={"cash_freed": round(trim_shares * price, 6),
              "exposure_after": round((shares - trim_shares) * price, 6),
              # ★ PS-21 — identically zero, and that is the finding.
              "tax_event": TAX_EVENT,
              "tax_note": ("all four accounts are registered (D-11 §5.5), so a "
                           "trim triggers no capital-gains event — the usual "
                           "'tax cost of trimming' term is identically zero"),
              "remaining_size_check": remaining_size_check})
