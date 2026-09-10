"""`F6b` — the eight ACs `MS-7` left unbuilt, 2026-09-09.

⚠⚠ **Two of them are safety rules, not bookkeeping.**

- `AC-6b.6` — `P3` *"holds inside deliberation"*: a revision may make a verdict
  equal or more conservative, **never more aggressive**. ★ `deliberate()` did
  not check it, so the one place a verdict could be quietly *improved* by an
  agent was unguarded (`DX-48`).
- `AC-6b.10` — `ADVISORY_ONLY` **could not be expressed**: `Deliberation` had no
  `mode`, so `F7a`'s band table in §2.1 had nothing to bind to. ⚠ Including its
  `INSUFFICIENT` row, which exists precisely so that *absence of evidence
  defaults to the safe branch, not the convenient one*.
"""

from __future__ import annotations

import pytest

from src.orchestration.graph.deliberation import (
    ACTIVE,
    ADVISORY_ONLY,
    Message,
    VerdictEscalated,
    capability_delta,
    deliberate,
    speaking_order,
)

CONSERVATIVE = {"BUY": 0, "HOLD": 1, "SELL": 2}


def _challenge(metric_value=0.9, threshold=0.5):
    return Message("CHALLENGE", "risk", "fundamental", "concentration too high",
                   metric="risk_contribution", metric_value=metric_value,
                   threshold=threshold)


def _run(post, disposition="CONVERGED", pre="HOLD", **kw):
    return deliberate(decision_id="r:MU:1", pre=pre, challenge=_challenge(),
                      respond=lambda m, p: (post, disposition), **kw)


# ── AC-6b.6 — ★★ P3 holds INSIDE deliberation ─────────────────────────────
@pytest.mark.parametrize("pre,post", [("HOLD", "SELL"), ("BUY", "HOLD"),
                                      ("BUY", "SELL"), ("HOLD", "HOLD")])
def test_ac_6b_6_a_revision_may_soften_or_hold(pre, post):
    """★ Equal or more conservative is always allowed.

    ⚠ `mode=ACTIVE` is explicit here: the DEFAULT is `ADVISORY_ONLY`, which
    would leave `post == pre` and make this test pass for the wrong reason.
    """
    assert _run(post, pre=pre, mode=ACTIVE).post == post


@pytest.mark.parametrize("pre,post", [("HOLD", "BUY"), ("SELL", "HOLD"),
                                      ("SELL", "BUY")])
def test_ac_6b_6_a_revision_may_NEVER_make_a_verdict_more_aggressive(pre, post):
    """⚠⚠ `P3` — *verdicts gate, never upgrade*.

    ★★★ This is the single most consequential guard in `F6b`. Deliberation runs
    **before** D-12 (`D4`), so a verdict it escalated would arrive at
    composition looking like the seat's own honest output — and D-12 composes
    deterministically from whatever it is handed. ⚠ There is no downstream
    check that would catch it: `RP-7`/`DC-5` compare the *composed* verdict to
    the *nominated* one, and both would already carry the escalation.
    """
    with pytest.raises(VerdictEscalated, match="MORE AGGRESSIVE"):
        _run(post, pre=pre)


def test_ac_6b_6_a_non_verdict_payload_is_left_alone():
    """⚠ `pre`/`post` are not always verdicts — a seat may revise conviction or
    size. ★ The guard must not invent an ordering for values it cannot rank."""
    assert _run({"size": 0.03}, pre={"size": 0.05},
                mode=ACTIVE).post == {"size": 0.03}


# ── AC-6b.10 — ★ advisory mode cannot alter the verdict ───────────────────
def test_ac_6b_10_advisory_mode_leaves_the_verdict_untouched():
    """★ §2.1 — *transcript is rendered; the verdict is unaffected*."""
    d = _run("SELL", pre="HOLD", mode=ADVISORY_ONLY)
    assert d.post == d.pre == "HOLD"
    assert d.messages, "the transcript is STILL rendered — that is the point"


def test_ac_6b_10_advisory_mode_still_records_what_it_WOULD_have_done():
    """★★ `PG-5.2` — the counterfactual arm is the whole reason to run an
    advisory capability at all.

    ⚠ An advisory mode that discarded its own proposal would make the Tier-B
    study impossible for exactly the period the capability is unproven, which is
    when the evidence is most needed.
    """
    d = _run("SELL", pre="HOLD", mode=ADVISORY_ONLY)
    assert d.advisory_post == "SELL"
    assert d.changed is False, "the DECISION did not change, and that is what changed means"


def test_ac_6b_10_active_mode_does_alter_the_verdict():
    """⚠ The mode must actually distinguish, or the band table is decoration."""
    assert _run("SELL", pre="HOLD", mode=ACTIVE).post == "SELL"


def test_ac_6b_10_the_default_mode_is_the_SAFE_one():
    """⚠⚠ §2.1's `INSUFFICIENT` row: *absence of evidence defaults to the safe
    branch, not the convenient one.* ★ `F7a` has never run, so nothing has yet
    earned `ACTIVE` — and a default of `ACTIVE` would let an unmeasured
    capability alter verdicts from its first day."""
    assert _run("SELL", pre="HOLD").post == "HOLD"


# ── AC-6b.9 — order is randomised AND recorded ────────────────────────────
def test_ac_6b_9_the_speaking_order_is_drawn_from_a_recorded_seed():
    """★ `F7a`'s `T4` measures whether the outcome tracks order. ⚠ It can only
    do that if the order VARIES and the seed is recorded — an unrecorded
    randomisation is not reproducible, and `PG-9` requires replay."""
    a = speaking_order(("risk", "fundamental"), seed=7)
    assert a == speaking_order(("risk", "fundamental"), seed=7), "same seed, same order"
    seeds = {speaking_order(("risk", "fundamental", "quant"), seed=s)
             for s in range(30)}
    assert len(seeds) > 1, "the order must actually vary, or T4 measures nothing"


def test_ac_6b_9_the_deliberation_carries_its_order_and_seed():
    d = _run("HOLD", order_seed=11)
    assert d.order_seed == 11
    assert set(d.speaking_order) == {"risk", "fundamental"}


# ── AC-6b.8 — pre/post recorded ALWAYS ────────────────────────────────────
def test_ac_6b_8_a_delta_is_produced_even_when_nothing_changed():
    """⚠⚠ `PG-5.2` / `F7a` `AC-7a.6` — *including when they are equal*. ★ The
    no-change cases are half the comparison; dropping them biases the study."""
    d = _run("HOLD", pre="HOLD")
    delta = capability_delta(d, is_valid=True)
    assert delta["changed"] is False
    assert delta["pre"] == {"verdict": "HOLD"} or delta["pre"] == "HOLD"
    assert delta["capability"] == "deliberation"


def test_ac_6b_8_the_delta_is_the_shape_f7a_reads():
    """★★ The join that makes `F7a` executable: `challenges_from_deltas()`
    consumes exactly this record."""
    from src.evaluation.studies.deliberation_tier_a import challenges_from_deltas

    d = _run("SELL", pre="HOLD", mode=ACTIVE)
    got = challenges_from_deltas([capability_delta(d, is_valid=True)])
    assert len(got) == 1
    assert got[0].revised is True
    assert got[0].softened is True, "HOLD -> SELL is a softening"


def test_ac_6b_8_an_unchallenged_subject_still_yields_a_delta():
    """⚠ Below the declared trigger there is no exchange — and `PG-5.2` still
    wants the arm. ★ Otherwise the denominator quietly excludes every case
    where deliberation declined to speak."""
    d = deliberate(decision_id="r:MU:1", pre="HOLD",
                   challenge=_challenge(metric_value=0.1, threshold=0.5),
                   respond=lambda m, p: ("SELL", "CONVERGED"))
    assert d.turns_used == 0
    assert capability_delta(d, is_valid=True)["changed"] is False


# ── AC-6b.12 — an agent error degrades, it does not crash ─────────────────
def test_ac_6b_12_an_agent_error_terminates_INCOMPLETE_not_settled():
    """⚠⚠ *never a silently shortened exchange presented as settled* (`P5`).

    ★ The dangerous outcome is not the crash — it is a truncated deliberation
    that reads as a converged one, because `F7a`'s `T6` would then count it as
    a convergence and the termination rate would be overstated.
    """
    def _boom(msg, pre):
        raise RuntimeError("the model timed out")

    d = deliberate(decision_id="r:MU:1", pre="HOLD", challenge=_challenge(),
                   respond=_boom)
    assert d.terminated == "INCOMPLETE"
    assert d.incomplete_reason and "timed out" in d.incomplete_reason
    assert d.post == d.pre, "an errored exchange revises nothing"


def test_ac_6b_12_an_incomplete_deliberation_is_not_counted_as_converged():
    """★ `T6` measures convergence; an INCOMPLETE run must not inflate it."""
    def _boom(msg, pre):
        raise RuntimeError("boom")

    d = deliberate(decision_id="r:MU:1", pre="HOLD", challenge=_challenge(),
                   respond=_boom)
    assert d.terminated != "CONVERGED"
    assert capability_delta(d, is_valid=True)["incomplete"] is True


def test_ac_6b_12_a_BLOCK_still_raises_and_is_not_swallowed_as_an_error():
    """⚠⚠ `D3`/`P4` — `BLOCK` is a CONTRACT breach, not a runtime failure.

    ★ The error path must not become a way to smuggle a forbidden disposition
    through as a degraded result: an agent that blocks is an agent that *acts*,
    and that is the line `F3` `D4` holds too.
    """
    from src.orchestration.graph.deliberation import BlockAttempted

    with pytest.raises(BlockAttempted):
        _run("HOLD", disposition="BLOCK")


# ── AC-6b.1 — termination is guaranteed ───────────────────────────────────
@pytest.mark.parametrize("disposition", ["CONVERGED", "ESCALATED"])
@pytest.mark.parametrize("budget", [0, 1, 2, 5])
def test_ac_6b_1_every_input_terminates_within_budget(disposition, budget):
    """★★ *no input produces an unbounded exchange* — halting by construction,
    not by a timeout."""
    d = _run("HOLD", disposition=disposition, turn_budget=budget)
    assert d.turns_used <= max(budget, 0)
    assert d.terminated in ("CONVERGED", "ESCALATED", "INCOMPLETE")


def test_ac_6b_11_a_sent_message_is_immutable():
    """`AC-6b.11` / `F2` `AC-2.8` — ⚠ a transcript that can be edited is not
    evidence."""
    from dataclasses import FrozenInstanceError

    msg = _challenge()
    # ⚠ NOT `pytest.raises(Exception)` — ruff's B017 caught that, and it is a
    # real weakness: a blind assert passes on a typo in the attribute name just
    # as happily as on the immutability it claims to test.
    with pytest.raises(FrozenInstanceError):
        msg.text = "rewritten"


def test_ac_6b_7_escalation_is_recorded_not_averaged():
    """★ `AC-6b.7` — ⚠ *never silently averaged*. Forcing convergence hides the
    disagreement most worth seeing."""
    d = _run("HOLD", disposition="ESCALATED")
    assert d.terminated == "ESCALATED"
    assert capability_delta(d, is_valid=True)["escalated"] is True
