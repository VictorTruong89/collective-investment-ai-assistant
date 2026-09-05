"""D-06 §6 — scenario arithmetic. PS-11…PS-14, PS-12's forbidden shape.

★ **A scenario is the book after a stated hypothetical, computed from D-11's
actual book.** ⚠ *It is never a suggestion, and the artifact says so in words.*

⚠ **PS-12 restates L0 §4.3's forbidden dependency here because it is the thing
this domain would drift into**: no target allocation, no recommended book, no
drift-from-target.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date

from src.portfolio.errors import TargetAllocationError

#: PS-11 — ★ in words, on the artifact.
NOT_A_PROPOSAL = (
    "This is the book AFTER a stated hypothetical, computed from the actual "
    "book. It is not a suggestion and nothing here proposes a trade (PS-11)."
)

#: PS-12 — requests that are the forbidden dependency wearing a friendly name.
FORBIDDEN_REQUESTS = (
    "target_allocation", "recommended_book", "drift_from_target",
    "optimal_weights", "rebalance_to", "target_weights", "ideal_portfolio",
)


@dataclass(frozen=True, slots=True)
class Scenario:
    """CT-6.2 — `is_proposal` is a **constant**, present so the contract says so."""

    scenario_id: str
    as_of: date
    book_ref: str
    hypothetical: dict
    exposure_before: dict
    exposure_after: dict
    is_proposal: bool = False

    def __post_init__(self) -> None:
        if self.is_proposal:
            raise TargetAllocationError("a scenario marked is_proposal=True")

    @property
    def deltas(self) -> dict:
        keys = set(self.exposure_before) | set(self.exposure_after)
        return {k: round(self.exposure_after.get(k, 0.0)
                         - self.exposure_before.get(k, 0.0), 6)
                for k in sorted(keys)}

    def to_json_obj(self) -> dict:
        return {"scenario_id": self.scenario_id, "as_of": self.as_of.isoformat(),
                "book_ref": self.book_ref, "hypothetical": dict(self.hypothetical),
                "exposure_before": dict(self.exposure_before),
                "exposure_after": dict(self.exposure_after),
                "deltas": self.deltas, "is_proposal": False,
                "label": NOT_A_PROPOSAL}

    def fingerprint(self) -> str:
        """PS-13 / AC-6.12 — same book + hypothetical + as_of ⇒ byte-identical."""
        payload = json.dumps(self.to_json_obj(), sort_keys=True,
                             separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def assert_not_a_target_request(what: str) -> None:
    """PS-12 / AC-6.11 — ★ *reporting a number is a disclosure; optimising
    toward it is the target allocation PS-12 forbids.*"""
    if what.strip().casefold().replace(" ", "_") in FORBIDDEN_REQUESTS:
        raise TargetAllocationError(what)


def scenario(*, scenario_id: str, as_of: date, book_ref: str, hypothetical: dict,
             exposure_before: dict, exposure_after: dict) -> Scenario:
    assert_not_a_target_request(hypothetical.get("kind", ""))
    return Scenario(scenario_id=scenario_id, as_of=as_of, book_ref=book_ref,
                    hypothetical=hypothetical, exposure_before=exposure_before,
                    exposure_after=exposure_after)


@dataclass(frozen=True, slots=True)
class ParityComparison:
    """PS-31/PS-32 — ★ *"equal-risk would be 6 %; you hold 31 %"*.

    ⚠ **A comparison, never a target.** D-06 does not rank names by distance
    from risk parity, does not compute drift toward it, and does not order a
    slate by it — *M-2 rejects the pressure that would apply.*
    """

    account_id: str
    as_of: date
    equal_risk_weight_pct: float
    actual_weight_pct: dict
    is_target: bool = False

    def __post_init__(self) -> None:
        if self.is_target:
            raise TargetAllocationError("a risk-parity comparison marked is_target")

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "as_of": self.as_of.isoformat(),
                "equal_risk_weight_pct": round(self.equal_risk_weight_pct, 4),
                "actual_weight_pct": dict(self.actual_weight_pct),
                "is_target": False,
                "note": "reported beside the actual weight; nothing ranks, "
                        "sorts or tracks drift against it (PS-32)"}


def risk_parity(*, account_id: str, as_of: date, weights: dict) -> ParityComparison:
    """PS-31 — ★ *the honest counterweight to a concentrated book*, and INV-026
    makes reporting mandatory and blocking forbidden."""
    n = len(weights) or 1
    return ParityComparison(account_id=account_id, as_of=as_of,
                            equal_risk_weight_pct=100.0 / n,
                            actual_weight_pct=dict(weights))
