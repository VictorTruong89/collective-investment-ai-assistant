"""`F6a` `AC-6a.9` / `AC-6a.10` — `PG-7`'s second and third obligations.

⚠⚠ **`PG-7` has three parts and only the first was built.** `influenced_by` was
recorded (`AC-6a.5`), and then nothing consumed it:

  1. every cross-configuration is recorded on the nomination — ✅ `AC-6a.5`
  2. any decision where one seat configured the other is **bucketed separately
     in evaluation** — `AC-6a.9`, here
  3. ⚠ the combined verdict **may never claim "two independent views agree"**
     when one configured the other — `AC-6a.10`, here

★★ A recorded field that nothing reads is not a control. `PG-7`'s rationale is
that *"cross-configuration silently converts concurrence into an echo"* — and a
flag nobody partitions on leaves the echo in the headline number.
"""

from __future__ import annotations

import pytest

from src.evaluation.metrics.influence import (
    InfluenceBuckets,
    partition_by_influence,
)


def _d(step_id, influenced_by=None):
    return {"type": "DecisionRecord", "step_id": step_id,
            "decision_id": "run-1:MU:1", "influenced_by": influenced_by,
            "action": "deep", "reason": "r", "propensity": 1.0}


def test_ac_6a_9_influenced_decisions_form_their_own_bucket():
    """★ `PG-7.2` — reportable on its own, not merged into the total."""
    buckets = partition_by_influence([
        _d("a"), _d("b", "quant"), _d("c"), _d("d", "quant")])
    assert isinstance(buckets, InfluenceBuckets)
    assert [r["step_id"] for r in buckets.influenced] == ["b", "d"]
    assert [r["step_id"] for r in buckets.independent] == ["a", "c"]
    assert buckets.n_influenced == 2 and buckets.n_independent == 2


def test_ac_6a_9_the_buckets_partition_exactly_and_lose_nothing():
    """⚠ A partition that drops a record silently under-reports the echo."""
    records = [_d(str(i), "quant" if i % 3 == 0 else None) for i in range(20)]
    b = partition_by_influence(records)
    assert b.n_influenced + b.n_independent == len(records)
    assert not {r["step_id"] for r in b.influenced} & {r["step_id"] for r in b.independent}


def test_ac_6a_9_a_non_decision_record_is_ignored_not_counted():
    """⚠ A trace holds StepRecords and ExternalCalls too; counting them would
    inflate `n` on every figure `PG-7.2` produces (`AC-5.2` — `n` is never
    decoration)."""
    b = partition_by_influence([_d("a", "quant"),
                                {"type": "StepRecord", "step_id": "job:1"},
                                {"type": "ExternalCall", "call_id": "c1"}])
    assert b.n_influenced == 1 and b.n_independent == 0


def test_ac_6a_9_an_empty_trace_is_empty_buckets_not_an_error():
    b = partition_by_influence([])
    assert b.n_influenced == 0 and b.n_independent == 0
    assert b.any_influenced is False


def test_ac_6a_9_any_influenced_is_the_flag_ac_6a_10_consumes():
    """★ The join between `PG-7.2` and `PG-7.3`: the partition answers
    *'was anything cross-configured?'*, which is exactly what the agreement
    guard needs to know."""
    assert partition_by_influence([_d("a", "quant")]).any_influenced is True
    assert partition_by_influence([_d("a")]).any_influenced is False


# ── AC-6a.10 ──────────────────────────────────────────────────────────────
from src.evaluation.metrics.influence import (  # noqa: E402
    IndependenceClaimError,
    assert_may_claim_independent_agreement,
    concurrence_label,
)


def test_ac_6a_10_agreement_may_not_be_claimed_when_a_seat_was_configured():
    """⚠⚠ `PG-7.3` — the claim is REFUSED, not softened.

    ★ `D3` puts the enforcement at COMPOSITION: *"if the claim is never built,
    no renderer can emit it."* Guarding only the renderer leaves a true-looking
    `agreement=True` in the decision record for `F5`, `F7b` and every future
    consumer to read.
    """
    with pytest.raises(IndependenceClaimError, match="quant"):
        assert_may_claim_independent_agreement(influenced_by=["quant"])


def test_ac_6a_10_agreement_is_allowed_when_no_seat_was_configured():
    """★ The guard must not fire on the honest case, or callers route around it.

    ⚠ This assertion was written as a bare `... is None` expression, which
    tests NOTHING — ruff's `B015` caught it. ★ Exactly `DX-20`'s family: a check
    that passes without checking.
    """
    assert assert_may_claim_independent_agreement(influenced_by=[]) is None


@pytest.mark.parametrize("influenced,expected", [
    ([], "independent"),
    (["quant"], "cross-configured"),
])
def test_ac_6a_10_the_label_travels_with_the_verdict(influenced, expected):
    """★★ `PG-10`'s shape, and `F2` `D3`'s: **a claim carries its subject's
    status**, and the STATUS TRAVELS IN THE FIELD rather than in a caveat
    elsewhere. `IDENTICAL`→`REPRODUCED` was renamed for exactly this reason —
    *"the name is what gets copied."*
    """
    assert concurrence_label(influenced) == expected


def test_ac_6a_10_the_label_never_reads_as_agreement_when_configured():
    """⚠ The word a reader takes away. `PG-7.3` is about what the reader is
    TOLD, so the guard is on the rendered word, not only on a boolean."""
    label = concurrence_label(["quant"])
    assert "independent" not in label and "agree" not in label
