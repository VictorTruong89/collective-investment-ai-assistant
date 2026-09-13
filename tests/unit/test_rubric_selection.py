"""⛔⛔ `DX-100` — a rubric is OFFERED as criteria and the score is DERIVED (`RA-31`).

Measured motivation: the first gated run (J-05 + J-06, 2026-09-13) returned 3 and
0 from an integer enum whose meaning the model was never shown.
"""

from __future__ import annotations

import pytest

from src.fundamental.errors import LevelUnavailableError, ScoreEmittedError
from src.fundamental.scorecard.rubrics.b43_v2 import CAPITAL_ALLOCATION_V2 as CAP
from src.fundamental.scorecard.selection import (
    INSUFFICIENT_EVIDENCE,
    RubricOffer,
    offer,
    resolve,
)

ALL = (4, 3, 2, 1, 0)
EVIDENCE = frozenset({"ca.capex", "cp.statement", "sc.diluted", "sc.sbc_expense"})


def _answer(criterion, boundary="a disclosed issuance to fund operations"):
    return {"criterion": criterion, "why": "…", "what_would_move_it_down": boundary}


def test_the_render_shows_EVERY_offered_criterion_and_NO_score():
    """★ `RA-31`: *a number invites interpolation*. The criteria are shown; the
    scores that would let the model reason by position are not."""
    o = offer(CAP, ALL, seed="s")
    text = o.render()
    for lv in CAP.levels:
        assert lv.criterion in text
        assert f", {lv.score}" not in text and f"score {lv.score}" not in text
    assert "level" not in text.casefold().replace("levels", "")
    assert INSUFFICIENT_EVIDENCE in text
    assert "evidence required: ca.capex" in text


def test_the_order_is_SEEDED_reproducible_and_varies_across_seeds():
    """★ `RA-17` — the same seed re-derives the recorded order; different seeds
    (blocks, runs) must not all show the same one, or position bias correlates."""
    assert offer(CAP, ALL, seed="x").permutation == offer(CAP, ALL, seed="x").permutation
    orders = {offer(CAP, ALL, seed=f"seed-{i}").permutation for i in range(20)}
    assert len(orders) > 5
    assert sorted(offer(CAP, ALL, seed="x").permutation) == sorted(ALL)


def test_the_criteria_enum_follows_the_SHOWN_order():
    o = offer(CAP, ALL, seed="y")
    assert o.criteria == tuple(CAP.level(s).criterion for s in o.permutation)


def test_an_echoed_criterion_DERIVES_its_score_whitespace_insensitively():
    lv = CAP.level(2)
    wrapped = lv.criterion.replace(" ", "\n  ", 3)
    score = resolve(offer(CAP, ALL, seed="z"), _answer(wrapped), EVIDENCE)
    assert (score.score, score.rubric_id) == (2, "capital_allocation@v2")
    assert score.selection.boundary_observation.startswith("a disclosed issuance")


def test_insufficient_evidence_is_NOT_a_score():
    """★★ `MP-7` — measured: without this exit J-06 used level 0 to mean
    *ungradable*, contradicting level 0's own criterion."""
    assert resolve(offer(CAP, ALL, seed="z"), _answer(INSUFFICIENT_EVIDENCE), EVIDENCE) is None


def test_an_INVENTED_criterion_refuses():
    with pytest.raises(ScoreEmittedError):
        resolve(offer(CAP, ALL, seed="z"), _answer("Management allocated capital well."), EVIDENCE)


def test_a_published_criterion_NOT_OFFERED_in_this_call_refuses():
    """⚠ The model may only choose what it was shown."""
    partial = offer(CAP, (2, 1, 0), seed="z")
    with pytest.raises(ScoreEmittedError, match="not among the 3 offered"):
        resolve(partial, _answer(CAP.level(4).criterion), EVIDENCE)


def test_a_level_whose_evidence_is_absent_refuses_through_derive_score():
    with pytest.raises(LevelUnavailableError):
        resolve(offer(CAP, ALL, seed="z"), _answer(CAP.level(4).criterion),
                frozenset({"ca.capex"}))


def test_an_offer_refuses_no_levels_and_a_criterion_colliding_with_the_exit():
    with pytest.raises(ValueError, match="no levels"):
        RubricOffer(rubric=CAP, ordered=(), seed="s")
