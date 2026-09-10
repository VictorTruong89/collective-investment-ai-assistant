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


#: `AC-7b.8` — ⚠⚠ **the wording is load-bearing.** `CT-7b.1` spells it out:
#: *"`NO_DIFFERENCE_DETECTED` is **not** `NO_DIFFERENCE`."*
#: ★★★ A null result on an underpowered study says *we could not see a
#: difference*, which is a statement about the INSTRUMENT. "No difference" is a
#: statement about the WORLD, and this study is nowhere near able to make it.
#: ⚠ These four are the only permitted values; nothing may render a synonym.
VERDICTS = ("INSUFFICIENT", "NO_DIFFERENCE_DETECTED", "IMPROVED", "DEGRADED")

#: ⚠ Phrases that overclaim a null. ★ Kept as data so `AC-7b.8` can assert
#: against them rather than trusting a reviewer to notice.
OVERCLAIMS = ("no difference", "no effect", "does not help", "did not help",
              "deliberation doesn't help", "no impact")


@dataclass(frozen=True, slots=True)
class TierBReport:
    lift: MetricResult
    n_changed: int
    n_unchanged: int
    scope: str = SCOPE
    tier: str = "B"
    #: `AC-7b.7` / `PG-7.2` — decisions where one seat configured another are a
    #: DISTINCT population. ⚠ Pooling them would let an echo count as evidence.
    influenced_bucket: bool = False

    @property
    def achieved_power(self) -> float:
        """`AC-7b.3` — ★ crude and honest, and it must never be omitted.

        ⚠ An `n` of 30 against an effect this small is not *nearly* powered; it
        is nowhere. Reporting the power as a number the reader can see is what
        stops a null being read as a negative.
        """
        n = self.n_changed
        return 0.0 if n <= 0 else min(1.0, n / 400.0)

    @property
    def detectable_effect_at_n(self) -> float | None:
        """`AC-7b.3` — ★★ **the honest headline** (`CT-7b.1`'s own words).

        The smallest lift this `n` could distinguish. ⚠ Reported *before* any
        difference, so a reader meets the instrument's resolution before they
        meet the number.
        """
        if self.n_changed <= 0:
            return None
        return round(2.8 / (self.n_changed ** 0.5), 4)

    @property
    def verdict(self) -> str:
        """`AC-7b.4` / `AC-7b.8` — ⚠ `INSUFFICIENT` is the DEFAULT and it is a
        **successful run**, not an error."""
        if not self.lift.is_sufficient or self.lift.value is None:
            return "INSUFFICIENT"
        detectable = self.detectable_effect_at_n or 0.0
        if abs(self.lift.value) < detectable:
            # ★ The measured lift is smaller than this n could resolve.
            return "NO_DIFFERENCE_DETECTED"
        return "IMPROVED" if self.lift.value > 0 else "DEGRADED"

    def to_report(self) -> str:
        """`AC-7b.3` — ★★ **power precedes the result, every time.**

        ⚠ The ordering is the requirement, not a formatting preference: a
        reader who meets the difference first has already formed a view by the
        time they reach the `n`.
        """
        lines = [
            "F7b — DELIBERATION OUTCOME STUDY (Tier B)",
            "=" * 52,
            "",
            "POWER  ★ read this before the result",
            "-" * 52,
            f"  n changed        : {self.n_changed}",
            f"  n unchanged      : {self.n_unchanged}   (retained — base rate)",
            f"  achieved power   : {self.achieved_power:.3f}",
            f"  detectable at n  : {self.detectable_effect_at_n}",
            "",
            "RESULT",
            "-" * 52,
            f"  verdict          : {self.verdict}",
            f"  lift             : {self.lift.value}",
            "",
            f"⚠ SCOPE: {self.scope}",
            "⚠ Tier B NEVER gates (PG-5.1). A powered disagreement with Tier A",
            "  is escalated to the fund manager as a finding, never applied (D4).",
        ]
        if self.influenced_bucket:
            lines.append("⚠ PG-7.2 — this bucket is CROSS-CONFIGURED and is not "
                         "pooled with independent decisions.")
        return "\n".join(lines)

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


def study(pairs: Sequence[Pair], *, inputs_ref: str,
          influenced_bucket: bool = False) -> TierBReport:
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
            n_changed=0, n_unchanged=len(unchanged),
            influenced_bucket=influenced_bucket)

    lift = sum(p.post_paper_return - p.pre_paper_return for p in changed) / len(changed)
    return TierBReport(measured("deliberation_lift", lift, len(changed), "B", inputs_ref),
                       n_changed=len(changed), n_unchanged=len(unchanged),
                       influenced_bucket=influenced_bucket)


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


def pairs_from_deltas(deltas, outcomes) -> tuple[Pair, ...]:
    """`AC-7b.1` — ★ the join this whole study rests on (`F2` `CT-2.6`).

    ⚠⚠ **Both arms are scored as PAPER returns** (`D2`), and that limit travels
    on every figure. The `pre` verdict was **never acted on**, so its realised
    outcome does not exist and cannot be recovered — so both arms are scored
    identically as *what each recommendation would have returned*.

    ★★★ The rejected alternative is the dangerous one: comparing the acted
    arm's REALISED outcome against the pre arm's PAPER one *looks* like using
    the best available data, and it is **asymmetric in deliberation's favour** —
    the acted arm carries execution and sizing effects the paper arm cannot.

    ⚠ The consequence must be stated wherever the figure appears: `F7b`
    measures whether deliberation improved **the recommendation**, ★ not
    whether it improved **the portfolio**. A reader will assume the second.

    ★ Unchanged deltas are retained (`AC-7b.2`) — they set the base rate, and
    dropping them leaves only the subset where the capability did something.
    """
    by_decision = {o["decision_id"]: o for o in outcomes}
    out = []
    for delta in deltas:
        if delta.get("type") != "CapabilityDelta":
            continue
        outcome = by_decision.get(delta.get("decision_id"))
        if outcome is None:
            # ⚠ Not yet resolved. ★ Absence here is the NORMAL state for most of
            #   this study's life — an outcome arrives weeks or months later —
            #   so it is skipped, never counted as a zero.
            continue
        out.append(Pair(
            decision_id=delta["decision_id"],
            changed=bool(delta.get("changed")),
            pre_paper_return=outcome.get("pre_paper_return"),
            post_paper_return=outcome.get("post_paper_return"),
        ))
    return tuple(out)
