"""`PG-7`'s unbuilt two-thirds — `F6a` `AC-6a.9` and `AC-6a.10`.

⚠⚠ **`PG-7` has three obligations and only the first was implemented.**
`F6a` recorded `influenced_by` on every `Routing` and every `DecisionRecord`
(`AC-6a.5`), and then **nothing read it**:

  1. every cross-configuration is recorded on the nomination — ✅ `AC-6a.5`
  2. any decision where one seat configured the other is **bucketed separately
     in evaluation** — `AC-6a.9`, here
  3. ⚠ the combined verdict **may never claim "two independent views agree"**
     when one configured the other — `AC-6a.10`, here

★★ **A recorded field that nothing consumes is not a control, it is a note.**
`PG-7`'s rationale is that *"choosing a model horizon **is** an analytical
choice … cross-configuration silently converts concurrence into an echo"* — and
a flag nobody partitions on leaves the echo inside the headline number, which is
the exact harm the rule was written against.

★ **Why this lives in `src/evaluation/` rather than in `F6a`.** `F6a` §2:
*"✗ Recording. F6a returns the reason; F2 persists it."* — and it computes no
metrics either. `PG-7.2` is a statement about **evaluation**, and `ST-2` says the
harness imports domains while nothing imports the harness, so the consumer is
the right place for it.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

# ★★ `ST-2` / `AC-5.12` — the harness imports domains; nothing imports the
# harness. `PG-7.3`'s guard belongs with the code that CONSTRUCTS the claim
# (D-12, per `F6a` `D3`), so it is imported from there and re-exported for the
# convenience of readers who come looking for all of `PG-7` in one place.
# ⚠ Defining it here instead would have forced `src/decision/` to import
# `src/evaluation/`, which `AC-5.12` fails the build over.
from src.decision.concurrence import (  # noqa: F401
    IndependenceClaimError,
    assert_may_claim_independent_agreement,
    concurrence_label,
)

#: ⚠ Only `CT-2.3` records carry `influenced_by`. A trace also holds
#: `StepRecord`s and `ExternalCall`s, and counting those would inflate `n` on
#: every figure this produces — `AC-5.2` says `n` is never decoration.
DECISION_TYPE = "DecisionRecord"


@dataclass(frozen=True, slots=True)
class InfluenceBuckets:
    """`AC-6a.9` — the two buckets `PG-7.2` requires, reportable separately."""

    influenced: tuple[dict, ...] = field(default_factory=tuple)
    independent: tuple[dict, ...] = field(default_factory=tuple)

    @property
    def n_influenced(self) -> int:
        return len(self.influenced)

    @property
    def n_independent(self) -> int:
        return len(self.independent)

    @property
    def any_influenced(self) -> bool:
        """★ The join between `PG-7.2` and `PG-7.3` — the partition answers
        *"was anything cross-configured?"*, which is precisely what the
        agreement guard needs to know."""
        return bool(self.influenced)

    @property
    def seats(self) -> tuple[str, ...]:
        """Which seats did the configuring — named, because `PG-7.1` says the
        cross-configuration is recorded, and a bucket that cannot say *by whom*
        is not much of a record."""
        return tuple(sorted({str(r.get("influenced_by")) for r in self.influenced}))


def partition_by_influence(records: Iterable[dict]) -> InfluenceBuckets:
    """`AC-6a.9` — split decisions into cross-configured and independent.

    ⚠ **Exhaustive over decisions, and silent about everything else.** Every
    `DecisionRecord` lands in exactly one bucket; a record of any other type is
    ignored rather than counted, because `n` travels with every figure `F5`
    emits and an inflated `n` misstates the very comparison this enables.
    """
    influenced, independent = [], []
    for record in records:
        if record.get("type") != DECISION_TYPE:
            continue
        (influenced if record.get("influenced_by") else independent).append(record)
    return InfluenceBuckets(tuple(influenced), tuple(independent))
