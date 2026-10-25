"""`DX-188` — `balance_sheet_resilience@v4`: the maturity ladder as a SEARCHED requirement.

⛔ Measured 2026-10-22 (SNDK as of 2026-10-20, a free dry Stage A): Sandisk repaid its term
loan in full on 2026-03-04 and its revolver is undrawn, so `E-06` returned `dm.ladder`
`not_found` — correctly. Every `@v3` level requires `dm.ladder` FOUND, so `J-05` refused at
EVERY level (`RA-32`), level 0 "does not disclose the maturity ladder" included. `DX-99`'s
shape; Victor, 2026-10-22: "Rubric v4, searched:".
"""
from __future__ import annotations


def test_v4_changes_ONLY_dm_ladder_to_its_searched_form():
    """★★★ `DX-86` — no criterion and no score moves; every other id is byte-identical."""
    from src.fundamental.scorecard.rubrics.b43_v3 import BALANCE_SHEET_RESILIENCE_V3 as V3
    from src.fundamental.scorecard.rubrics.b43_v4 import BALANCE_SHEET_RESILIENCE_V4 as V4

    assert (V4.dimension, V4.version) == ("balance_sheet_resilience", 4)
    assert [(lv.score, lv.criterion) for lv in V4.levels] == \
        [(lv.score, lv.criterion) for lv in V3.levels]
    for old, new in zip(V3.levels, V4.levels):
        assert new.evidence_required == tuple(
            "searched:dm.ladder" if e == "dm.ladder" else e for e in old.evidence_required)
        assert "dm.ladder" not in new.evidence_required


def test_v4_is_PUBLISHED_alongside_every_earlier_version_and_J05_emits_it():
    """`RA-52` — versioned, never over v3; the judgement path emits `@v4`."""
    from src.fundamental.prompts.e_blocks import EMITS_RUBRIC
    from src.fundamental.scorecard.registry import RubricRegistry
    from src.fundamental.scorecard.rubrics.b43_v4 import PUBLISHED_RUBRICS

    reg = RubricRegistry(PUBLISHED_RUBRICS)
    for version in (1, 2, 3, 4):
        reg.get("balance_sheet_resilience", version)
    assert EMITS_RUBRIC["J-05"] == "balance_sheet_resilience@v4"
    for key in EMITS_RUBRIC.values():
        dim, _, ver = key.partition("@v")
        reg.get(dim, int(ver))


def test_dx_188_a_company_with_no_debt_is_SCOREABLE_under_v4_and_refused_under_v3():
    """★★★ The finding, as a before/after on SNDK's evidence ids (E-06 · E-10)."""
    import pytest

    from src.fundamental.scorecard.availability import NoAvailableLevel, require_levels
    from src.fundamental.scorecard.rubrics.b43_v3 import BALANCE_SHEET_RESILIENCE_V3 as V3
    from src.fundamental.scorecard.rubrics.b43_v4 import BALANCE_SHEET_RESILIENCE_V4 as V4

    ids = frozenset({"dm.covenant", "dm.instrument", "dm.revolver", "sc.diluted",
                     "searched:dm.ladder", "searched:dm.covenant", "searched:sc.diluted"})
    with pytest.raises(NoAvailableLevel):
        require_levels(V3, ids)
    assert set(require_levels(V4, ids)) == {4, 3, 2, 1, 0}


def test_dx_188_without_E06_the_rubric_still_refuses():
    """⚠ `DX-98` still binds: `searched:` does not waive a block that never ran."""
    import pytest

    from src.fundamental.scorecard.availability import NoAvailableLevel, require_levels
    from src.fundamental.scorecard.rubrics.b43_v4 import BALANCE_SHEET_RESILIENCE_V4 as V4

    with pytest.raises(NoAvailableLevel):
        require_levels(V4, frozenset({"sc.diluted"}))
