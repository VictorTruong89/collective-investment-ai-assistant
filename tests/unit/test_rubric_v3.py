"""`DX-99` — `earnings_quality@v3`: absence as a SEARCHED requirement.

★★ Measured motivation: `E-04` on MU returned every item `not_found` (no non-GAAP
measure presented), and `v2` — which requires `ng.adjustment` FOUND at every level
— refused `J-04` for the company permanently, contradicting its own note that
*"its ABSENCE is itself the finding"*.
"""

from __future__ import annotations

import pytest

from src.fundamental.scorecard.availability import (
    NoAvailableLevel,
    PartialRubricEvidence,
    require_levels,
)
from src.fundamental.scorecard.rubrics.b43_v2 import EARNINGS_QUALITY_V2
from src.fundamental.scorecard.rubrics.b43_v3 import (
    EARNINGS_QUALITY_V3,
    PUBLISHED_RUBRICS,
    V3_SEARCHED,
)

#: MU, E-01 + E-04 + a completed E-09 that found no policy change: the shape
#: measured 2026-09-12 for E-04, with E-09 as a successful run would return it.
MU_SEARCHED = frozenset({
    "seg.revenue", "seg.op_income",
    "searched:ng.measure", "searched:ng.gaap_start", "searched:ng.adjustment",
    "searched:ng.recurrence_note", "searched:ng.nongaap_end",
    "searched:ap.change",
})


def test_v3_changes_ONLY_the_evidence_form_not_a_criterion_or_a_score():
    """★★★ `DX-86`'s discipline: an evidence-form change and a criteria change
    are never mixed, or a later score move cannot be attributed."""
    assert [(lv.score, lv.criterion) for lv in EARNINGS_QUALITY_V3.levels] == \
           [(lv.score, lv.criterion) for lv in EARNINGS_QUALITY_V2.levels]
    for old, new in zip(EARNINGS_QUALITY_V2.levels, EARNINGS_QUALITY_V3.levels, strict=True):
        assert new.evidence_required == tuple(V3_SEARCHED.get(e, e) for e in old.evidence_required)
    assert V3_SEARCHED == {"ng.adjustment": "searched:ng.adjustment",
                           "ap.change": "searched:ap.change"}
    assert "seg.op_income" in EARNINGS_QUALITY_V3.level(4).evidence_required


def test_v3_is_PUBLISHED_alongside_v1_and_v2():
    from src.fundamental.scorecard.registry import RubricRegistry

    reg = RubricRegistry(PUBLISHED_RUBRICS)
    assert reg.get("earnings_quality", 2) is EARNINGS_QUALITY_V2
    assert reg.get("earnings_quality", 3) is EARNINGS_QUALITY_V3
    assert reg.get("earnings_quality", 1).version == 1


def test_every_v3_requirement_names_an_id_a_DECLARED_block_emits():
    """★ Against the code's registry (`DX-85`ⓑ's test, extended to `searched:`)."""
    from src.fundamental.prompts.e_blocks import BLOCKS
    from src.fundamental.scorecard.availability import SEARCHED

    declared = {i for f, ids, _v in BLOCKS.values() if f().kind == "extraction" for i in ids}
    cited = {e.removeprefix(SEARCHED) for lv in EARNINGS_QUALITY_V3.levels
             for e in lv.evidence_required}
    assert cited <= declared, sorted(cited - declared)


def test_dx_99_MU_with_no_non_GAAP_measures_is_SCOREABLE_under_v3_and_refused_under_v2():
    """★★★ The finding, as a before/after on the same evidence."""
    with pytest.raises(NoAvailableLevel):
        require_levels(EARNINGS_QUALITY_V2, MU_SEARCHED)
    assert require_levels(EARNINGS_QUALITY_V3, MU_SEARCHED) == (4, 3, 2, 1, 0)


def test_dx_99_without_E09_the_rubric_is_still_PARTIAL_and_refused():
    """⚠ `DX-98` still binds: `searched:` does not waive a block that never ran.
    MU's E-09 was truncated twice — so J-04 must still refuse until it succeeds."""
    no_e09 = MU_SEARCHED - {"searched:ap.change"}
    with pytest.raises(PartialRubricEvidence, match="searched:ap.change"):
        require_levels(EARNINGS_QUALITY_V3, no_e09)


def test_dx_99_a_FOUND_id_does_not_satisfy_its_searched_form_by_accident():
    """⚠ The two id families are distinct strings; a found `ng.adjustment` alone
    (no `searched:` pin) must not open v3. `extractions()` always writes both, so
    this guards a hand-built bundle rather than a real one."""
    found_only = frozenset({"seg.op_income", "ng.adjustment", "ap.change"})
    with pytest.raises(NoAvailableLevel):
        require_levels(EARNINGS_QUALITY_V3, found_only)


# ═══════════════════════════════════════════════════════════════════════════
# `DX-101` — two criteria whose WORDING decided the first criterion-selected scores
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(("old_name", "new_name", "changed"), [
    ("BALANCE_SHEET_RESILIENCE_V2", "BALANCE_SHEET_RESILIENCE_V3", {3, 1}),
    ("CAPITAL_ALLOCATION_V2", "CAPITAL_ALLOCATION_V3", {4}),
])
def test_dx_101_ONLY_the_named_criteria_change(old_name, new_name, changed):
    """★★★ `DX-86`'s discipline: scores and evidence byte-identical; every level
    outside the named ones byte-identical; the named ones actually differ."""
    from src.fundamental.scorecard.rubrics import b43_v2, b43_v3

    old, new = getattr(b43_v2, old_name), getattr(b43_v3, new_name)
    assert (new.dimension, new.version) == (old.dimension, 3)
    for a, b in zip(old.levels, new.levels, strict=True):
        assert (a.score, a.evidence_required) == (b.score, b.evidence_required)
        assert (a.criterion != b.criterion) is (a.score in changed), a.score


def test_dx_101_undisclosed_headroom_is_no_longer_ABSENT():
    """① The measured ambiguity: *absent* read as *not disclosed* scored a sound
    balance sheet at 1. Level 1 is now adverse only; non-disclosure is level 3."""
    from src.fundamental.scorecard.rubrics.b43_v3 import BALANCE_SHEET_RESILIENCE_V3 as B

    assert "absent" not in B.level(1).criterion
    assert "exhausted or breached" in B.level(1).criterion
    assert "or not disclosed" in B.level(3).criterion
    assert "headroom disclosed," in B.level(4).criterion, "level 4 still needs disclosure"


def test_dx_101_a_window_with_no_buybacks_is_STATED_not_assumed():
    """② The measured assumption is now the criterion's own words."""
    from src.fundamental.scorecard.rubrics.b43_v3 import CAPITAL_ALLOCATION_V3 as C

    assert "a window with no buybacks meets this condition" in C.level(4).criterion


def test_dx_101_every_published_rubric_resolves_and_versions_are_unique():
    from src.fundamental.prompts.e_blocks import EMITS_RUBRIC
    from src.fundamental.scorecard.registry import RubricRegistry

    reg = RubricRegistry(PUBLISHED_RUBRICS)
    for key in EMITS_RUBRIC.values():
        dim, _, ver = key.partition("@v")
        reg.get(dim, int(ver))
    ids = [r.rubric_id for r in PUBLISHED_RUBRICS]
    assert len(ids) == len(set(ids))
