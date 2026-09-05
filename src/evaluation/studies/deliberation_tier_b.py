"""F7b — the Tier-B outcome study. `MS-7.4`. ⚠⚠ **It never gates** (`PG-5.1`).

★★ **`D2` is the decision that bounds what this study may CLAIM.**

The `pre` verdict was never acted on, so its realised outcome does not exist and
cannot be recovered. Both arms are therefore scored as **paper** forward returns —
what each arm's recommendation *would* have returned — regardless of which was
acted on. **Symmetric treatment is what makes the comparison valid.**

⚠⚠ **The consequence travels with every figure:** `F7b` measures whether
deliberation improved **the recommendation**, ★ *not* whether it improved **the
portfolio**. Those are different claims, and the second is the one a reader will
assume — so `PG-10` requires the artifact to say which it is.

⚠ The rejected alternative is the dangerous one: comparing the acted arm's
*realised* outcome against the unacted arm's *paper* outcome **flatters
deliberation**, because the acted arm carries sizing and execution effects the
paper arm cannot. It looks like using the best available data.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from src.evaluation.metrics.models import MetricResult, insufficient, measured

#: `D2` — stated on every figure this module emits.
SCOPE = ("paper forward return at the model's own horizon, for BOTH arms; "
         "measures the RECOMMENDATION, not the portfolio")

#: `D3` — annual while insufficient, quarterly once the floor is met.
REPORT_MONTHS_INSUFFICIENT = 12
REPORT_MONTHS_SUFFICIENT = 3


class TierBCannotGate(Exception):
    """⚠⚠ `PG-5.1` — *"Tier B accrues from day one and never gates."*"""


@dataclass(frozen=True, slots=True)
class Pair:
    """One `CapabilityDelta`, joined to outcomes by `decision_id` (`F2` `CT-2.6`)."""

    decision_id: str
    changed: bool
    pre_paper_return: float | None
    post_paper_return: float | None


@dataclass(frozen=True, slots=True)
class TierBReport:
    lift: MetricResult
    n_changed: int
    n_unchanged: int
    scope: str = SCOPE
    tier: str = "B"

    def gate(self) -> None:
        """⚠ Calling this is always an error. Present so the refusal is explicit."""
        raise TierBCannotGate(
            "a Tier-B result may not gate a capability (PG-5.1). At ~250 decisions "
            "a year against a signal at IC 0.0203 / t = 1.42, this is a "
            "second-order measurement on an unestablished first-order one — and "
            "⚠ more time does not fix it, because noise grows with the sample.")

    @property
    def next_report_months(self) -> int:
        """`D3` — the accrual IS the information while insufficient."""
        return (REPORT_MONTHS_SUFFICIENT if self.lift.is_sufficient
                else REPORT_MONTHS_INSUFFICIENT)


def study(pairs: Sequence[Pair], *, inputs_ref: str) -> TierBReport:
    """⚠ `AC-7b.2` — unchanged decisions are RETAINED, never silently dropped.

    ★ They are half the comparison; dropping them leaves exactly the subset where
    the capability did something, which biases the result invisibly.
    """
    usable = [p for p in pairs
              if p.pre_paper_return is not None and p.post_paper_return is not None]
    changed = [p for p in usable if p.changed]
    unchanged = [p for p in usable if not p.changed]

    if not changed:
        return TierBReport(
            insufficient("deliberation_lift", 0, "B", inputs_ref, minimum=1),
            n_changed=0, n_unchanged=len(unchanged))

    lift = sum(p.post_paper_return - p.pre_paper_return for p in changed) / len(changed)
    return TierBReport(measured("deliberation_lift", lift, len(changed), "B", inputs_ref),
                       n_changed=len(changed), n_unchanged=len(unchanged))


def reconcile(tier_a_verdict: str, tier_b: TierBReport) -> str:
    """`D4` — ⛔ Tier B never supersedes Tier A; a disagreement ESCALATES.

    ★ It never silently overrides, and it is never silently discarded either.
    """
    if not tier_b.lift.is_sufficient:
        return tier_a_verdict
    disagrees = (tier_a_verdict == "KEEP" and tier_b.lift.value is not None
                 and tier_b.lift.value < 0)
    if disagrees:
        return "ESCALATE_TO_FUND_MANAGER"
    return tier_a_verdict
