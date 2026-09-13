"""✅ `DX-85`/`DX-86` — the `v2` rubrics, approved and published 2026-09-12.

★★ These pin what the approval rested on: `v2` changes ONLY the wiring, every id
it introduces is one an E-block actually emits, `v1` stays published beside it,
and the judgement path emits `v2`.
"""

from __future__ import annotations

import pathlib
import re

from src.fundamental.scorecard.rubrics import b43_v1 as v1
from src.fundamental.scorecard.rubrics import b43_v2 as v2

PAIRS = (
    (v1.MOAT_DURABILITY, v2.MOAT_DURABILITY_V2),
    (v1.EARNINGS_QUALITY, v2.EARNINGS_QUALITY_V2),
    (v1.BALANCE_SHEET_RESILIENCE, v2.BALANCE_SHEET_RESILIENCE_V2),
    (v1.CAPITAL_ALLOCATION, v2.CAPITAL_ALLOCATION_V2),
)
DOC = pathlib.Path(
    "sdd/design/rel6_design/L1-fundamental-analysis-master-prompt.md")


def _emitted_evidence_ids() -> set[str]:
    text = DOC.read_text(encoding="utf-8")
    ids: set[str] = set()
    for m in re.finditer(r"^## E-\d+ ·.*?\n+```text\n(.*?)```", text, re.S | re.M):
        ids.update(re.findall(r"([a-z]{2,4}\.[a-z_]+)", m.group(1)))
    return ids


def test_v2_is_PUBLISHED_alongside_v1_never_over_it():
    """★ `RA-52` — rubrics are *versioned*: a baseline recorded against `v1`
    must stay readable, so `v2` is added beside it and `v1` is not touched.

    ⚠ History: this test used to assert the OPPOSITE — that the draft was
    imported by nothing — because a draft that leaks into the registry is not a
    draft. It was rewritten on approval (Victor Truong, 2026-09-12).
    """
    from src.fundamental.scorecard.registry import RubricRegistry
    from src.fundamental.scorecard.rubrics.b43_v1 import B43_RUBRICS

    reg = RubricRegistry((*B43_RUBRICS, *v2.B43_V2_RUBRICS))
    for old, new in PAIRS:
        assert reg.get(old.dimension, 1) is old
        assert reg.get(new.dimension, 2) is new


def test_the_judgement_path_EMITS_v2_or_later():
    """✅ `DX-86` — no Stage-A scoring block emits `@v1`, whose ids resolve to
    no extractor. ✏ `DX-99` moved `J-04` on to `@v3`; the others stay `@v2`."""
    from src.fundamental.prompts.e_blocks import EMITS_RUBRIC

    assert EMITS_RUBRIC == {"J-03": "moat_durability@v2", "J-04": "earnings_quality@v3",
                            "J-05": "balance_sheet_resilience@v3",
                            "J-06": "capital_allocation@v3"}


def test_v2_changes_ONLY_the_wiring_not_a_single_criterion_or_score():
    """★★★ The property that makes the draft reviewable at a glance.

    ⚠ Correcting a wiring fault and revising analytical criteria are two
    different changes. Mixing them would make it impossible to tell which one
    moved a score afterwards — so this asserts the criteria are byte-identical.
    """
    for old, new in PAIRS:
        assert [(x.score, x.criterion) for x in old.levels] == \
               [(x.score, x.criterion) for x in new.levels], old.dimension
        assert new.version == old.version + 1
        assert new.dimension == old.dimension


def test_every_v2_evidence_id_is_one_an_E_BLOCK_ACTUALLY_EMITS():
    """★★★ The whole point of `DX-85`. `v1` required 13 ids and **3** matched.

    ⚠ `b43_v1.py`'s own comment predicted this: *"these must match what B4.2's
    extractors emit, or a level is unavailable for a NAMING reason rather than
    an evidential one — which would read as thin evidence and be a wiring bug."*
    """
    emitted = _emitted_evidence_ids()
    unknown = sorted({e for _o, n in PAIRS for lv in n.levels
                      for e in lv.evidence_required if e not in emitted})
    assert not unknown, f"v2 still cites ids no E-block emits: {unknown}"


def test_v1_is_measurably_broken_so_the_draft_has_a_reason_to_exist():
    """⚠ Asserts the CURRENT broken state deliberately — it fails the moment v1
    is repaired or retired, at which point this file's premise has changed."""
    emitted = _emitted_evidence_ids()
    broken = sorted({e for o, _n in PAIRS for lv in o.levels
                     for e in lv.evidence_required if e not in emitted})
    assert len(broken) == 9, broken


def test_two_E_entries_are_declared_but_CITED_BY_NO_LEVEL():
    """⚠ `guidance` (`gd.metric`) and `concentration` (`con.customer_pct`) sit
    in `E` and **no rubric level requires them**.

    ★ Worth stating because it changes the headline number: the dict is 13 wide
    and 3 resolve, but only **11** ids are load-bearing and **9** of those are
    broken. ⚠⚠ An unused entry is also the one place a wrong id costs nothing
    and so is never noticed — `con.customer_pct` has been wrong since it was
    written and could not have failed anything.
    """
    used = {e for _o, n in PAIRS for lv in n.levels for e in lv.evidence_required}
    unused = {k for k, val in v2.E2.items() if val not in used}
    assert unused == {"guidance", "concentration"}


def test_v2_unblocks_all_four_dimensions_once_the_E_BLOCKS_EXIST():
    """★★ What the fix buys, stated as a measurement rather than a claim.

    ⚠ It buys NOTHING today — with only `E-01`/`E-02` declared, v1 and v2 are
    identical, because the three ids that already matched are the three v2 does
    not change. ★ The gain appears the moment `E-04`…`E-13` land.
    """
    from src.fundamental.scorecard.availability import available_levels

    today = frozenset({"seg.revenue", "seg.op_income", "gd.metric"})
    for old, new in PAIRS:
        assert available_levels(old, today) == available_levels(new, today)

    later = today | {"ng.adjustment", "cc.customer", "dm.ladder", "dm.covenant",
                     "ca.capex", "ap.change", "sc.diluted", "sc.sbc_expense",
                     "cp.statement", "cx.capacity"}
    for old, new in PAIRS:
        assert available_levels(new, later) == (4, 3, 2, 1, 0), new.dimension
        if old.dimension != "moat_durability":
            assert available_levels(old, later) == (), (
                f"{old.dimension} v1 should still be unscoreable — that is the "
                f"defect v2 exists to fix")


def test_the_JUDGEMENT_entry_records_its_approved_resolution():
    """⚠⚠ `capital_actions` had no mechanical translation: `v1`'s `cap.action`
    was one generic slot and `E-07` emits eight specific ids. ★ Resolved as ⓐ
    (`ca.capex`) and approved 2026-09-12 — the header keeps the rejected
    alternatives, because this is where a wiring fix touched analysis."""
    header = pathlib.Path(
        "src/fundamental/scorecard/rubrics/b43_v2.py").read_text(encoding="utf-8")
    assert "THE ONE ENTRY THAT IS A JUDGEMENT" in header
    assert "approved 2026-09-12" in header
    assert v2.E2["capital_actions"] == "ca.capex"
