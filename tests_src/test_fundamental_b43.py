"""D-01 B4.3 — AC-1.29, 1.30, 1.31, 1.34, 1.34a (the scorecard).

★ **L3 §3A.4's done-when:** *a rubric level whose required evidence was not
**extracted** is unavailable to the model; `evidence_coverage` **falls** when an
extraction fails.*

⚠ The second clause is what this slice found broken: as specified, coverage was
**identically 1.0** and could not fall at all (RA-134).

Tier: unit + data contract + invariant (constitution §4).
"""

from __future__ import annotations

import dataclasses

import pytest

from src.fundamental import (
    B43_RUBRICS, CONFIDENCE_FLOOR, CONFIDENCE_HOLD_CAP, DIMENSIONS, HOLD_CAPPED,
    INSUFFICIENT_DATA, LevelUnavailableError, Rubric, RubricLevel, RubricMutatedError,
    RubricRegistry, ScoreEmittedError, Selection, SelfReportedConfidenceError, UNCAPPED,
    assess_confidence, build_scorecard, coverage_report, derive_score,
    dimension_coverage, reject_self_reported,
)

MOAT = B43_RUBRICS[0]
ALL_EVIDENCE = frozenset().union(*(r.required_union for r in B43_RUBRICS))


def selection(rubric=MOAT, score=4, **kw):
    return Selection(dimension=kw.pop("dimension", rubric.dimension),
                     criterion=kw.pop("criterion", rubric.level(score).criterion),
                     boundary_observation=kw.pop("boundary", "Share loss to a new entrant."),
                     **kw)


def all_selections(score=2):
    return [selection(r, score) for r in B43_RUBRICS]


# --------------------------------------------------------------------------- #
# AC-1.29 — the model selects a criterion; the score is DERIVED
# --------------------------------------------------------------------------- #

def test_ac_1_29_the_score_is_derived_from_a_selected_criterion():
    """AC-1.29 — RA-31.

    ★ *The model selects a criterion, and the score is derived from the
    selection. It never emits a number directly — **a number invites
    interpolation, and interpolation is where dispersion enters**.*
    """
    got = derive_score(MOAT, selection(score=3), ALL_EVIDENCE)
    assert got.score == 3
    assert got.level.criterion == MOAT.level(3).criterion
    assert got.rubric_id == "moat_durability@v1"


def test_ac_1_29_a_criterion_matching_no_published_level_raises():
    """AC-1.29 — an invented level is not a rounding question.

    ⚠ A response carrying `score: 3` and nothing else is indistinguishable from
    an interpolation; the echoed criterion is what ties the answer to a written
    level.
    """
    with pytest.raises(ScoreEmittedError, match="invented level"):
        derive_score(MOAT, selection(criterion="The moat seems solid enough."),
                     ALL_EVIDENCE)


def test_ac_1_29_an_empty_criterion_is_a_score_emitted_directly():
    """RA-31 — checked at construction, so it cannot exist even briefly."""
    with pytest.raises(ScoreEmittedError, match="score emitted"):
        Selection(dimension="moat_durability", criterion="  ",
                  boundary_observation="x")


def test_the_boundary_observation_is_part_of_the_answer():
    """§4.0 — ★ *the cheapest de-biasing device in this file.*

    It forces the boundary of the judgement to be named at the moment it is made,
    and it is what makes RM-2's dispersion readable: *a dimension that moves two
    levels between identical runs, whose stated boundary observation is different
    each time, has an under-determined rubric (RA-34) — not a noisy model.*
    """
    with pytest.raises(ValueError, match="adjacent option"):
        Selection(dimension="moat_durability", criterion=MOAT.level(4).criterion,
                  boundary_observation="")


def test_criterion_matching_tolerates_whitespace_and_nothing_else():
    """A criterion is line-wrapped in the source and arrives on one line."""
    reflowed = " ".join(MOAT.level(3).criterion.split())
    assert derive_score(MOAT, selection(criterion=reflowed), ALL_EVIDENCE).score == 3
    assert "persist" in reflowed
    with pytest.raises(ScoreEmittedError):
        derive_score(MOAT, selection(criterion=reflowed.replace("persist", "hold")),
                     ALL_EVIDENCE)


# --------------------------------------------------------------------------- #
# AC-1.30 — a level selected without its required evidence fails
# --------------------------------------------------------------------------- #

def test_ac_1_30_a_level_without_its_required_evidence_fails():
    """AC-1.30 — RA-32. ★ B4.2's done-when, first clause.

    *A level selected without that evidence present in the bundle is a **failed
    selection**, not a low-confidence one.*
    """
    thin = ALL_EVIDENCE - {"cmp.capacity_announcement"}
    assert MOAT.level(4).evidence_required[-1] == "cmp.capacity_announcement"

    with pytest.raises(LevelUnavailableError, match="failed selection"):
        derive_score(MOAT, selection(score=4), thin)
    assert derive_score(MOAT, selection(score=3), thin).score == 3, "…level 3 remains"


def test_ac_1_30_availability_counts_EXTRACTED_items_not_documents():
    """RA-66 — ★ *presence in the bundle is not extraction.*

    ⚠ *A 10-K that is present but from which the required number could not be
    pulled is not evidence*, and counting presence is how a coverage metric
    reports 100 % on a bundle nothing could be read from. The set passed in is
    B4.2's `evidence_ids`, which excludes every `not_found`.
    """
    assert MOAT.level(4).is_available(ALL_EVIDENCE)
    assert not MOAT.level(4).is_available(ALL_EVIDENCE - {"seg.revenue"})


def test_available_levels_are_returned_highest_first():
    """The judgement envelope asks the model to *read every option before
    choosing*, and the rubric presents them in a fixed order."""
    levels = MOAT.available_levels(ALL_EVIDENCE)
    assert [lv.score for lv in levels] == sorted((lv.score for lv in levels),
                                                 reverse=True)
    thin = frozenset({"seg.revenue"})
    assert [lv.score for lv in MOAT.available_levels(thin)] == [2, 1, 0]


def test_a_level_declaring_no_evidence_is_refused():
    """★ RA-134. It would be unconditionally available AND shrink coverage's
    denominator — *a level nothing can fail to support*."""
    with pytest.raises(ValueError, match="unconditionally available"):
        RubricLevel(3, "Looks fine.", ())


# --------------------------------------------------------------------------- #
# AC-1.31 — rubric immutability
# --------------------------------------------------------------------------- #

def test_ac_1_31_republishing_a_rubric_version_with_changed_content_raises():
    """AC-1.31 — RA-33. *A rubric edit invalidates every baseline in §7.4* (RM-4)."""
    reg = RubricRegistry(B43_RUBRICS)
    reg.publish(MOAT)                                  # idempotent, identical content

    edited = dataclasses.replace(
        MOAT, levels=tuple(
            dataclasses.replace(lv, criterion=lv.criterion + " Or thereabouts.")
            if lv.score == 4 else lv for lv in MOAT.levels))
    with pytest.raises(RubricMutatedError, match="needs a version bump"):
        reg.publish(edited)
    assert dataclasses.replace(edited, version=2).content_hash != MOAT.content_hash


def test_a_partial_rubric_set_is_refused():
    """RA-52 — ⚠ *a missing dimension is indistinguishable from a low-scoring one
    on the card.*"""
    reg = RubricRegistry(B43_RUBRICS[:3])
    with pytest.raises(KeyError, match="no rubric published"):
        reg.assert_complete()
    RubricRegistry(B43_RUBRICS).assert_complete()


def test_a_dimension_outside_the_closed_four_is_refused():
    """RA-52 — the set is fixed, versioned and closed."""
    with pytest.raises(ValueError, match="fixed, versioned and closed"):
        Rubric(dimension="management_quality", version=1,
               levels=(RubricLevel(4, "Good.", ("x",)),))


# --------------------------------------------------------------------------- #
# AC-1.34a — ★★ the defect this slice found
# --------------------------------------------------------------------------- #

def test_ac_1_34a_coverage_falls_when_an_extraction_fails():
    """AC-1.34a — ★★ **RA-65 as amended, RA-134.** B4.3's done-when, second clause.

    ```
    AS SPECIFIED, THE METRIC COULD NOT FALL.

    `required` read "the evidence_required list of the level BEING SELECTED",
    and RA-32 makes an unsupported level UNAVAILABLE — so every selectable
    level has all its evidence by construction and coverage is identically
    1.0. RA-38's 0.3/0.5 floors could never fire.
    ```
    """
    full = dimension_coverage(MOAT, ALL_EVIDENCE)
    assert full.coverage == 1.0

    thin = dimension_coverage(MOAT, {"seg.revenue"})
    assert thin.coverage == pytest.approx(1 / 3), "★ strictly between 0 and 1"
    assert thin.missing == {"seg.op_income", "cmp.capacity_announcement"}

    none = dimension_coverage(MOAT, frozenset())
    assert none.coverage == 0.0


def test_ac_1_34a_the_denominator_is_the_rubric_union_not_the_selected_level():
    """★ **RA-134 — availability is per LEVEL; coverage is per RUBRIC.**

    ⚠ Keyed on the selection, dropping to a low-demand level would *raise*
    coverage — which is RA-66's manufacturing arriving through the denominator.
    """
    thin = frozenset({"seg.revenue"})
    # Level 2 is available on this evidence and requires exactly what is present.
    assert MOAT.level(2).is_available(thin)
    assert set(MOAT.level(2).evidence_required) == thin

    # ⚠ RA-32 binds every dimension, so a scorecard needs each rubric's
    # lowest-level evidence before ANY level of it is selectable. That is the
    # rule working: a bottom score still has to be supported.
    floor_evidence = frozenset().union(
        *(set(r.level(0).evidence_required) for r in B43_RUBRICS))
    card = build_scorecard(ticker="MU", rubrics=B43_RUBRICS,
                           selections=[selection(r, 0) for r in B43_RUBRICS],
                           extracted=floor_evidence)

    # ★ Every dimension took its LOWEST-demand level, and coverage did NOT rise
    # to 1.0 — which is precisely what the pre-amendment formula would have done.
    # ★ (1/3 + 1/3 + 1/3 + 1/4) / 4 = 0.3125 — strictly between 0 and 1, and it
    # lands just ABOVE the 0.3 floor and firmly inside the HOLD cap. Under the
    # pre-amendment formula it would have been 1.0 and uncapped.
    assert card.coverage.aggregate == pytest.approx(0.3125)
    assert all(s.score == 0 for s in card.scores)
    assert card.confidence.cap == HOLD_CAPPED


def test_coverage_carries_the_sets_that_produced_it():
    """RA-22/RA-25 — `0.5` alone cannot say *which half was missing*, and that is
    exactly the question a data-gap block has to answer."""
    obj = dimension_coverage(MOAT, {"seg.revenue"}).to_json_obj()
    assert obj["matched"] == ["seg.revenue"]
    assert obj["missing"] == ["cmp.capacity_announcement", "seg.op_income"]


def test_the_aggregate_is_the_mean_over_all_four_dimensions():
    """RA-65 — ⚠ *a mean over three reports a number about a scorecard that does
    not exist.*"""
    report = coverage_report(B43_RUBRICS, ALL_EVIDENCE)
    assert report.aggregate == 1.0
    with pytest.raises(ValueError, match="FOUR dimensions"):
        coverage_report(B43_RUBRICS[:3], ALL_EVIDENCE)


# --------------------------------------------------------------------------- #
# AC-1.34 — the confidence floors
# --------------------------------------------------------------------------- #

def test_ac_1_34_the_floors_fire_on_coverage():
    """AC-1.34 — RA-38, RA-67, INV-012/INV-013.

    ★ **RA-67 makes RA-38 structural**: until calibration exists,
    `confidence := evidence_coverage`, so there is **no model-produced number to
    launder** and *"never self-reported"* stops being a rule someone enforces.
    """
    def confidence_at(extracted):
        return assess_confidence(coverage_report(B43_RUBRICS, extracted))

    top = confidence_at(ALL_EVIDENCE)
    assert top.value == 1.0 and top.cap == UNCAPPED
    assert top.basis == "evidence_coverage"
    assert top.calibration["status"] == "not_yet_calibrated"

    nothing = confidence_at(frozenset())
    assert nothing.value == 0.0
    assert nothing.cap == INSUFFICIENT_DATA and nothing.forces_insufficient_data

    # A coverage that lands between the two thresholds caps the verdict at HOLD.
    middling = assess_confidence(coverage_report(B43_RUBRICS, ALL_EVIDENCE),
                                 calibrated=0.4)
    assert middling.cap == HOLD_CAPPED and middling.caps_at_hold


def test_ac_1_34_the_thresholds_are_inv_012_and_inv_013s():
    """RA-67 — 0.3 → INSUFFICIENT_DATA, 0.3–0.5 → cap at HOLD."""
    assert (CONFIDENCE_FLOOR, CONFIDENCE_HOLD_CAP) == (0.3, 0.5)
    for value, expected in ((0.29, INSUFFICIENT_DATA), (0.30, HOLD_CAPPED),
                            (0.49, HOLD_CAPPED), (0.50, UNCAPPED)):
        got = assess_confidence(coverage_report(B43_RUBRICS, ALL_EVIDENCE),
                                calibrated=value)
        assert got.cap == expected, f"{value} -> {got.cap}"


def test_ac_1_34_a_self_reported_confidence_is_refused():
    """RA-38 — ★ *a model asked to gate itself will not gate itself.*"""
    for bad in ("self_reported", "model", "stated"):
        with pytest.raises(SelfReportedConfidenceError, match="own claim"):
            reject_self_reported(bad)
    assert reject_self_reported("evidence_coverage") == "evidence_coverage"


def test_ra_68_calibration_does_not_absorb_coverage():
    """RA-68 — after calibration, coverage stays a SEPARATE reported field.

    ⚠ *How much did we read* and *how often were we right* are different
    questions, and collapsing them would hide **a well-evidenced thesis that is
    reliably wrong**.
    """
    report = coverage_report(B43_RUBRICS, {"seg.revenue"})
    calibrated = assess_confidence(report, calibrated=0.9)
    assert calibrated.value == 0.9 and calibrated.basis == "calibrated"
    assert report.aggregate < 0.9, "coverage survives beside it, unchanged"


# --------------------------------------------------------------------------- #
# RA-53 — no composite score
# --------------------------------------------------------------------------- #

def test_ra_53_the_scorecard_is_transported_never_summed():
    """★★ RA-53 — *there is no composite score.*

    *A weighted sum would be a second verdict competing with the first, produced
    by weights nobody fitted* — and `L2` §5.0's argument against fitted weights
    applies with more force here, where `n` is smaller still.
    """
    card = build_scorecard(ticker="mu", rubrics=B43_RUBRICS,
                           selections=all_selections(2), extracted=ALL_EVIDENCE)
    obj = card.to_json_obj()
    assert set(obj["scorecard"]) == set(DIMENSIONS)
    for forbidden in ("total", "composite", "overall", "weighted", "sum", "score"):
        assert forbidden not in obj, f"a {forbidden!r} field is a second verdict"
    assert not hasattr(card, "total")


def test_the_scorecard_matches_ct_1_4s_grade_block():
    """§8.1 — the four keys `CT-1.4.grade.scorecard` carries (D-12 DN-25)."""
    from src.fundamental import Grade

    card = build_scorecard(ticker="MU", rubrics=B43_RUBRICS,
                           selections=all_selections(3), extracted=ALL_EVIDENCE)
    grade = Grade(scorecard=card.as_grade_block)      # accepted by CT-1.4
    assert set(grade.scorecard) == set(DIMENSIONS)
    assert all(v == 3 for v in grade.scorecard.values())


def test_a_scorecard_missing_a_dimension_is_refused():
    """RA-52 — ⚠ a missing dimension is indistinguishable from a low-scoring one."""
    with pytest.raises(ValueError, match="closed and complete"):
        build_scorecard(ticker="MU", rubrics=B43_RUBRICS,
                        selections=all_selections(2)[:3], extracted=ALL_EVIDENCE)


def test_every_published_rubric_declares_evidence_at_every_level():
    """★ RA-134 — a level declaring none would silently shrink the denominator."""
    for rubric in B43_RUBRICS:
        for level in rubric.levels:
            assert level.evidence_required, f"{rubric.rubric_id} level {level.score}"
        assert rubric.required_union, rubric.rubric_id
