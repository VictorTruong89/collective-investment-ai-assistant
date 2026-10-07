"""D-01 B4.4 — AC-1.6, 1.6a, 1.12, 1.13, 1.14, 1.15, 1.18, 1.32, 1.33.

★ **L3 §3A.4's done-when:** *D-12 receives a `GateVerdict` that **varies with the
thesis** — the B3 constant is gone, and every reachable thesis state maps to
exactly one status (RA-49).*

⚠ **BS-28 still binds.** B4.4 may be merged; its output may not be *delivered as
actionable* until B4.5's stability probe lands.

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

import dataclasses
from datetime import date

import pytest

from src.fundamental import (
    AuthoringRun, BUY, BearCase, BearCaseNotSeparateError, CommitLog, FLAG, FLAG_FLOOR,
    Falsifier, GateInputs, HOLD, INSUFFICIENT_DATA, NO_THESIS, NoFalsifierError,
    NullBearCaseError, PASS, PriorVerdictLeakError, SELL, STAGE_A, Thesis,
    UncheckableFalsifierError, UncommittedFalsifiersError, VETO, VETO_FLOOR,
    VerdictNotEnumError, assemble, assert_stage_view, bear_case_overlap,
    commit_falsifiers, computed, evaluate, filing, profile, supersede,
)

AS_OF = date(2026, 8, 23)
DEADLINE = date(2027, 3, 31)


def bundle(with_prior=False):
    parts = [filing("0000-1", "Gross margin was 55.4%."),
             computed("b3_minimal", 1, "fair_value_band=[380,445]"),
             profile(AS_OF, "Sector: IT")]
    if with_prior:
        from src.fundamental import prior_thesis
        parts.append(prior_thesis(3, "Previously BUY, conviction High."))
    return assemble(ticker="MU", as_of=AS_OF, parts=parts)


def falsifier(ordinal=1, **kw):
    base = dict(condition="Gross margin below 55% in two consecutive quarters.",
                observable_field="f_gross_margin", source="D-02", deadline=DEADLINE,
                materiality="The pricing-power premise fails.", about_business=True)
    return Falsifier(ordinal=ordinal, **{**base, **kw})


def falsifiers():
    return (falsifier(1),
            falsifier(2, condition="Net debt / EBITDA above 3.0x at any quarter-end.",
                      observable_field="f_net_debt_ebitda"))


def bear(**kw):
    return BearCase(text=kw.pop("text", "Capacity additions crush pricing by FY2028."),
                    falsification_condition=kw.pop(
                        "falsification_condition",
                        "Industry utilisation above 90% for three quarters."),
                    prompt_version=kw.pop("prompt_version", "J-11@v1"),
                    run_id=kw.pop("run_id", "call-bear"))


def thesis(**kw):
    run = AuthoringRun(ticker="MU", as_of=AS_OF)
    base = dict(bundle=bundle(), stage_a_payload={"moat_durability": 3},
                falsifiers=falsifiers(), verdict=BUY, conviction="Medium-High",
                bear_case=bear(), scorecard={"moat_durability": 3},
                confidence={"value": 0.62, "basis": "evidence_coverage"},
                bull_run_ids=("call-bull",), run_id="run-1")
    return run.author(**{**base, **kw})


# --------------------------------------------------------------------------- #
# AC-1.6 — bounded outputs
# --------------------------------------------------------------------------- #

def test_ac_1_6_verdict_and_conviction_are_enums():
    """AC-1.6 — RA-8. *Free prose is permitted only where nothing downstream
    branches on it* — and everything branches on the verdict."""
    assert thesis(verdict=SELL).verdict == SELL
    with pytest.raises(VerdictNotEnumError, match="enum with written criteria"):
        thesis(verdict="Cautiously Optimistic")
    with pytest.raises(VerdictNotEnumError, match="conviction"):
        thesis(conviction="quite sure")


def test_the_verdict_enum_has_four_values_not_three():
    """⚠ `INSUFFICIENT_DATA` is D-01's way of declining, and §11.2 maps it to VETO.

    It is **not** on D-12's lattice (`{BUY, HOLD, SELL}`): D-01 emits a *thesis*
    verdict and D-12 composes a *decision* one. §11.2 is the adapter.
    """
    from src.fundamental import VERDICTS
    from src.decision import CONSERVATISM

    assert set(VERDICTS) == {BUY, HOLD, SELL, INSUFFICIENT_DATA}
    assert INSUFFICIENT_DATA not in CONSERVATISM, "not a composable verdict"


# --------------------------------------------------------------------------- #
# AC-1.12 — anchor stripping
# --------------------------------------------------------------------------- #

def test_ac_1_12_stage_a_receives_a_bundle_with_price_and_valuation_withheld():
    """AC-1.12 — RA-14, MP-3.

    ★ *Stage membership is enforced by the bundle, not by the instruction.* A
    Stage-A prompt cannot see price because the bundle handed to it has no price
    field — **"do not consider valuation" is a request; an absent field is a
    guarantee.**
    """
    full = bundle()
    assert full.of_kind("computed"), "the full bundle carries the valuation"

    blind = full.redact()
    assert blind.of_kind("computed") == ()
    assert_stage_view(STAGE_A, blind)
    with pytest.raises(PriorVerdictLeakError, match="'blind' bundle"):
        assert_stage_view(STAGE_A, full)


def test_the_blind_bundle_is_derived_by_d01_not_supplied_by_the_caller():
    """RA-19 — *the evidence bundle is not curated by the same layer that judges.*

    ⚠ *If the judging layer could choose its evidence, confirmation bias would
    have a supply chain* — so `author()` redacts, and takes no blind view in.
    """
    import inspect
    sig = inspect.signature(AuthoringRun.author)
    assert "blind" not in sig.parameters and "blind_bundle" not in sig.parameters


# --------------------------------------------------------------------------- #
# The Stage-A freeze — §4A.2 step 5
# --------------------------------------------------------------------------- #

def test_the_stage_a_freeze_is_persisted_and_hashed():
    """★★ Step 5, *the load-bearing one*.

    ```
    Staging without a persisted commit lets Stage B silently revise Stage A
    once it has seen the price — AND THE ANCHOR-STRIPPING BOUGHT NOTHING.
    ```
    """
    t = thesis()
    assert t.stage_a_hash.startswith("sha256:")

    run = AuthoringRun(ticker="MU", as_of=AS_OF)
    first = run.freeze_stage_a(bundle=bundle().redact(), payload={"moat": 3})
    assert first.commit_hash.startswith("sha256:")
    # ⚠ RA-108 — nothing rewrites it, including a re-run of a later stage.
    with pytest.raises(UncommittedFalsifiersError, match="rewrite an earlier"):
        run.freeze_stage_a(bundle=bundle().redact(), payload={"moat": 4})


def test_an_uncommitted_stage_cannot_be_read():
    """RA-108 — *later stages READ it*, and there is nothing to read unless it
    was committed."""
    with pytest.raises(KeyError, match="reading a variable, not a commitment"):
        CommitLog().get(STAGE_A)


# --------------------------------------------------------------------------- #
# AC-1.14 — ★★ the falsifier commit
# --------------------------------------------------------------------------- #

def test_ac_1_14_the_falsifiers_are_persisted_before_the_verdict():
    """AC-1.14 — ★★ **RA-16 as amended**, the defect this slice found.

    ```
    It read "and is part of the same structured output" — which is the exact
    failure §4A.2 step 8 names: held in memory, the ordering is nominal and
    A SINGLE CALL COULD PRODUCE BOTH.
    ```

    ★ One call emitting `{falsifiers, verdict}` satisfied the old wording exactly
    and bought nothing: the falsifiers get **fitted to a verdict already
    reached**.
    """
    t = thesis()
    assert t.falsifier_commit_hash.startswith("sha256:")

    # ★ The ordering is enforced by the TYPE: a thesis cannot be constructed
    # without the commit hash, so a caller who skipped J-15's write is stuck.
    with pytest.raises(UncommittedFalsifiersError, match="strictly sequential"):
        Thesis(ticker="MU", thesis_version=1, as_of=AS_OF, bundle_hash="sha256:x",
               run_id="r", verdict=BUY, conviction="High", falsifiers=falsifiers(),
               bear_case=bear(), scorecard={}, confidence={},
               falsifier_commit_hash="")


def test_the_commit_hash_changes_with_the_falsifiers():
    """The commit is content-addressed, so a different set is a different commit."""
    log_a, log_b = CommitLog(), CommitLog()
    a = commit_falsifiers(log_a, bundle_hash="sha256:x", falsifiers=falsifiers())
    b = commit_falsifiers(log_b, bundle_hash="sha256:x",
                          falsifiers=(falsifier(1), falsifier(2, about_business=False,
                                                              condition="Price below $60.")))
    assert a.commit_hash != b.commit_hash


def test_falsifiers_render_before_the_verdict_in_the_record_too():
    """RA-16 — the commitment is first in the JSON a reader opens, not only in
    the call order."""
    keys = list(thesis().to_json_obj())
    assert keys.index("falsifiers") < keys.index("bear_case")
    assert "falsifier_commit_hash" in keys


# --------------------------------------------------------------------------- #
# AC-1.32 / AC-1.33 — falsifiers
# --------------------------------------------------------------------------- #

def test_ac_1_32_a_thesis_with_too_few_checkable_falsifiers_raises():
    """AC-1.32 — RA-35. *A thesis with no checkable breaking condition cannot be
    wrong, which means it cannot be right either.*"""
    with pytest.raises(NoFalsifierError):
        thesis(falsifiers=(falsifier(1),))
    with pytest.raises(NoFalsifierError, match="2-4 conditions"):
        thesis(falsifiers=tuple(falsifier(i) for i in range(1, 6)))


def test_ac_1_32_a_falsifier_set_of_only_price_levels_raises():
    """★ J-15 — *a falsifier set that consists only of price levels is a
    **stop-loss wearing a thesis's clothing**, and it will fire on volatility
    rather than on being wrong.*"""
    prices = (falsifier(1, about_business=False, condition="Price below $60.",
                        observable_field="close_minor"),
              falsifier(2, about_business=False, condition="Price below $50.",
                        observable_field="close_minor"))
    with pytest.raises(NoFalsifierError, match="stop-loss wearing"):
        thesis(falsifiers=prices)


def test_a_tautological_falsifier_is_refused():
    """J-15 — *you may not write "the thesis is invalidated if the investment case
    no longer holds" or any variant. That is a tautology and it fails the run.*"""
    for bad in ("The investment case no longer holds.",
                "The thesis is invalidated by events.",
                "The story changes materially."):
        with pytest.raises(UncheckableFalsifierError, match="tautology"):
            falsifier(1, condition=bad)


def test_a_falsifier_naming_no_observable_field_is_refused():
    """RA-35 — ★ *a falsifier naming a field this system does not receive is not
    checkable, however precise it sounds.* The test J-15 states: **could a script
    decide it?**"""
    with pytest.raises(UncheckableFalsifierError, match="not checkable"):
        falsifier(1, observable_field="")
    with pytest.raises(UncheckableFalsifierError, match="materiality"):
        falsifier(1, materiality="  ")


def test_ac_1_33_superseding_is_the_only_path_and_a_thesis_is_frozen():
    """AC-1.33 — RA-36.

    ⚠ **Editing a falsifier after the fact is how a thesis becomes
    unfalsifiable** — the condition drifts toward whatever did not happen.
    """
    original = thesis()
    with pytest.raises(dataclasses.FrozenInstanceError):
        original.falsifiers = ()
    with pytest.raises(dataclasses.FrozenInstanceError):
        original.falsifiers[0].condition = "Something easier."

    newer = supersede(original, falsifiers=(falsifier(1), falsifier(
        2, condition="Inventory days above 140 for two quarters.",
        observable_field="f_inventory_days")))
    assert newer.thesis_version == original.thesis_version + 1
    assert original.falsifiers[1].condition != newer.falsifiers[1].condition
    assert original.thesis_version == 1, "the old thesis is intact"


# --------------------------------------------------------------------------- #
# AC-1.13 / AC-1.18 — the bear case
# --------------------------------------------------------------------------- #

def test_ac_1_13_the_bear_case_comes_from_a_separate_call():
    """AC-1.13 — RA-15.

    ⚠ *A bear case written in the same breath is a **rhetorical concession**, not
    an analysis.* Checked on the **call id**, because prose cannot show which
    call produced it.
    """
    thesis()                                              # separate ids — fine
    with pytest.raises(BearCaseNotSeparateError, match="separateness is the analysis"):
        thesis(bear_case=bear(run_id="call-bull"), bull_run_ids=("call-bull",))


def test_ac_1_18_a_bear_case_naming_no_falsifiable_condition_fails_the_run():
    """AC-1.18 — RM-11. ★ *A bear case that nothing could disprove is a mood.*"""
    with pytest.raises(NullBearCaseError, match="is a mood"):
        bear(falsification_condition="")


def test_x05_measures_bear_bull_overlap_deterministically():
    """RM-11's other half — ⚠ **the threshold is an ADMITTED GUESS.**

    RM-11 says *"shares > X % of its tokens with the bull case"* and **never
    declares X**. 0.6 is a level at which two texts are plainly the same
    argument; it has never been measured (CN-10).
    """
    from src.fundamental import BEAR_OVERLAP_CAP

    bull = "Capacity discipline holds and pricing recovers through FY2028."
    assert bear_case_overlap(bull, bull) == 1.0
    assert bear_case_overlap("Capacity additions crush pricing by FY2028.", bull) \
        < BEAR_OVERLAP_CAP
    assert 0.0 < BEAR_OVERLAP_CAP < 1.0


# --------------------------------------------------------------------------- #
# AC-1.15 — the prior verdict
# --------------------------------------------------------------------------- #

def test_ac_1_15_fresh_authoring_never_sees_the_prior_verdict():
    """AC-1.15 — RA-18, and ⚠ **invalidation is the deliberate exception** (RA-39).

    *Re-deciding and re-checking are different tasks*, and the distinction lives
    in which entry point was called — which is why RA-106 makes the workflows
    separate functions rather than one `analyse(mode=…)`.
    """
    thesis()                                              # no prior part — fine
    with pytest.raises(PriorVerdictLeakError, match="re-deciding is not re-checking"):
        thesis(bundle=bundle(with_prior=True))

    # RA-39: the part kind exists precisely so an invalidation bundle CAN carry it.
    assert bundle(with_prior=True).of_kind("prior_thesis")


# --------------------------------------------------------------------------- #
# ★ The real gate — §11.2, and B4.4's done-when
# --------------------------------------------------------------------------- #

def gate(**kw):
    """⚠ `thesis_obj` is tested for PRESENCE, not truthiness — passing `None`
    explicitly means *there is no thesis*, which is the case §11.2 maps to
    `NO_THESIS`. A `kw.pop("thesis_obj", None)` cannot tell that from "not
    specified", which is the same conflation DN-10 is about."""
    stability = kw.pop("stability", {"k": 5, "agreement": 1.0,
                                     "distribution": {"BUY": 5}})
    if "thesis_obj" in kw:
        subject = kw.pop("thesis_obj")
    else:
        subject = dataclasses.replace(thesis(verdict=kw.pop("verdict", BUY)),
                                      verdict_stability=stability)
    return evaluate(GateInputs(thesis=subject, **kw), as_of=AS_OF, ticker="MU")


def test_the_done_when_the_gate_varies_with_the_thesis():
    """★★ L3 §3A.4 — *D-12 receives a `GateVerdict` that varies with the thesis;
    **the B3 constant is gone**.*"""
    statuses = {
        gate(verdict=BUY).status,
        gate(verdict=HOLD).status,
        gate(verdict=BUY, stability={"k": 5, "agreement": 0.6,
                                     "distribution": {"BUY": 3, "HOLD": 2}}).status,
        gate(thesis_obj=None).status,
    }
    assert statuses == {PASS, VETO, FLAG, NO_THESIS}, statuses


def test_ac_1_6a_the_most_conservative_matching_row_wins():
    """AC-1.6a — ★★ **RA-135**, the second defect this slice found.

    ⚠ §11.2's rows **overlap**: a stable, confident BUY that is also **stale**
    matches row 1 (`PASS`) and row 7 (`FLAG`). RA-49 demands *"exactly one
    status"*, and **first match wins would make the answer depend on the order
    the rows happen to be written in**.
    """
    assert gate(verdict=BUY).status == PASS
    stale = gate(verdict=BUY, stale=True)
    assert stale.status == FLAG, "PASS and FLAG both matched; FLAG is conservative"
    assert "also matched" in stale.reason, "and the other match is still reported"

    both = gate(verdict=HOLD, stale=True)
    assert both.status == VETO, "VETO beats FLAG"


def test_a_fired_falsifier_vetoes_whatever_else_matched():
    """RA-41 — *the stated breaking condition occurred.*"""
    assert gate(verdict=BUY, falsifier_fired=True).status == VETO


def test_ra_48s_two_thresholds_split_unstable_into_flag_and_veto():
    """RA-48 — ✅ QR-2 closed: *an unstable verdict FLAGS above `VETO_FLOOR` and
    VETOES below it.* The question presupposed a binary."""
    def at(agreement):
        return gate(verdict=BUY, stability={"k": 5, "agreement": agreement,
                                            "distribution": {"BUY": 3, "HOLD": 2}}).status

    assert at(FLAG_FLOOR) == PASS
    assert at(FLAG_FLOOR - 0.01) == FLAG
    assert at(VETO_FLOOR) == FLAG
    assert at(VETO_FLOOR - 0.01) == VETO


def test_no_thesis_short_circuits_and_is_never_a_pass():
    """DN-10 / §11.2 — ⚠ **NO_THESIS is not on the S chain.**

    *The identity must not be reachable by omission.*
    """
    v = gate(thesis_obj=None)
    assert v.status == NO_THESIS and v.status != PASS
    assert v.grade.k is None, "no thesis, nothing graded"


def test_a_sell_thesis_vetoes_and_cannot_cause_a_sell():
    """RA-50 — ⚠ *`VETO` on a SELL thesis is inert by construction* (D-12 §5.4).

    *D-01 must not expect a SELL thesis to CAUSE a sell; it withholds support for
    a buy. A thesis that wants an exit says so through an `InvalidationEvent`.*
    """
    from src.decision import apply_gate

    v = gate(verdict=SELL)
    assert v.status == VETO and "cannot cause a sell" in v.reason
    assert apply_gate("SELL", VETO) == "SELL", "inert, per D-12 §5.4"


def test_insufficient_data_vetoes_as_an_absence_not_a_weak_thesis():
    """§11.2 — *the absence of a thesis, not a weak one* (RA-38's floor)."""
    v = gate(verdict=INSUFFICIENT_DATA)
    assert v.status == VETO and "absence of a thesis" in v.reason


def test_the_grade_block_is_a_transport_copy_of_the_thesis():
    """RA-51 — *byte-identical to the Thesis fields it mirrors* (DN-26)."""
    t = dataclasses.replace(thesis(), verdict_stability={
        "k": 5, "agreement": 0.6, "distribution": {"BUY": 3, "HOLD": 2}})
    g = evaluate(GateInputs(thesis=t), as_of=AS_OF).grade
    assert (g.verdict, g.conviction) == (t.verdict, t.conviction)
    assert g.k == 5 and g.verdict_distribution == {"BUY": 3, "HOLD": 2}
    assert g.stability_fraction == 0.6


def test_an_unmeasured_stability_is_none_and_never_a_fabricated_one():
    """★ BS-28's boundary in code.

    ⚠ **`None` is not 1.0.** A thesis with no stability result is not stable; it
    is *unmeasured* — and RP-13 refuses to render it on the actionable path. That
    is why B4.4's output stays non-actionable until B4.5 supplies the probe.
    """
    g = evaluate(GateInputs(thesis=thesis()), as_of=AS_OF).grade
    assert g.k is None and g.stability_fraction is None
    assert g.verdict_distribution is None


def test_the_mapping_is_deterministic():
    """RA-49 — *identical theses map identically* (INV-2)."""
    t = dataclasses.replace(thesis(), verdict_stability={"k": 3, "agreement": 0.67,
                                                         "distribution": {"BUY": 2, "HOLD": 1}})
    a = evaluate(GateInputs(thesis=t, stale=True), as_of=AS_OF)
    b = evaluate(GateInputs(thesis=t, stale=True), as_of=AS_OF)
    assert a.to_json_obj() == b.to_json_obj()


def test_the_real_gate_is_not_the_stub():
    """L3 BS-27 — *the B3 stub is replaced in B4.4 and not before.*"""
    from src.fundamental import stub_gate_verdict

    real = gate(verdict=BUY)
    stub = stub_gate_verdict("MU", AS_OF)
    assert real.produced_by_stub is None
    from src.fundamental import REPLACED_AT     # ✏ 2026-10-06: was "B4.4"
    assert stub.produced_by_stub == REPLACED_AT
    assert real.thesis_version is not None and stub.thesis_version is None
