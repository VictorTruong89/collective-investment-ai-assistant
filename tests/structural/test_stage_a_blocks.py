"""`DX-64` — Stage A is declared. ⚠ And two things about it are NOT true yet.

★★ `J-01`…`J-08` now have text in `src/`, pinned to the design doc by
`test_prompt_text_matches_spec.py`. These tests pin the claims that pinning does
NOT make true: that a block's emitted rubric exists, and that a declared block is
not mistaken for a callable one (`DX-80`, `DX-81`).
"""

from __future__ import annotations

import pathlib

import pytest

from src.fundamental.prompts.e_blocks import BLOCKS, EMITS_RUBRIC
from src.fundamental.scorecard.models import DIMENSIONS
from src.fundamental.scorecard.registry import RubricRegistry
from src.fundamental.scorecard.rubrics.b43_v1 import (
    BALANCE_SHEET_RESILIENCE,
    CAPITAL_ALLOCATION,
    EARNINGS_QUALITY,
    MOAT_DURABILITY,
)

STAGE_A = ("J-01", "J-02", "J-03", "J-04", "J-05", "J-06", "J-07", "J-08")


def _registry() -> RubricRegistry:
    """★ Every published version — the SAME list the judgement runner reads
    (`DX-99`), so the test cannot resolve a rubric the runner does not."""
    from src.fundamental.scorecard.rubrics.b43_v4 import PUBLISHED_RUBRICS   # ✏ DX-188

    return RubricRegistry(PUBLISHED_RUBRICS)


def test_dx_64_every_stage_a_block_is_declared():
    """★ `STAGE_BLOCKS` named `J-01`…`J-08` as Stage A for months while none but
    `J-01` had text. ⚠ A stage that cannot be constructed is not a stage."""
    missing = [b for b in STAGE_A if b not in BLOCKS]
    assert not missing, f"{missing} are named in Stage A but not declared in BLOCKS"


def test_every_stage_a_block_is_blind():
    """⚠⚠ `RA-14` / `MP-3` — Stage A reasons WITHOUT a valuation anchor, and the
    guarantee is physical: the redacted bundle has no price field at all.

    ★ One block declared `view="full"` by accident would be handed the whole
    bundle, and `call.py`'s pairing check would pass — because the pair would be
    consistent. The error is invisible at the seam and only visible here.
    """
    wrong = [b for b in STAGE_A if BLOCKS[b][0]().view != "blind"]
    assert not wrong, f"{wrong} are Stage A but not blind — RA-14"


def test_dx_80_every_emitted_rubric_RESOLVES_in_the_registry():
    """★★★ `DX-80` — the guard that was missing when the mismatch was written.

    ⚠⚠ The design doc's own headings say `J-03` emits `moat_durability@v2` and
    `J-05` emits `balance_sheet@v1`. **Neither resolves**: the registry publishes
    `moat_durability@v1` and the dimension is `balance_sheet_resilience`.
    ★ Nothing caught it because no rubric-emitting block had ever been declared —
    the two documents had simply never been asked to agree.
    """
    reg = _registry()
    for block_id, key in EMITS_RUBRIC.items():
        dimension, _, version = key.partition("@v")
        assert dimension in DIMENSIONS, (
            f"{block_id} emits {key!r} but {dimension!r} is not one of the four "
            f"RA-52 dimensions {DIMENSIONS}"
        )
        reg.get(dimension, int(version))     # raises if the version is absent


def test_dx_80_the_declared_rubrics_cover_every_scored_dimension():
    """`RA-52` — four dimensions or the scorecard is not a scorecard. ⚠ A reader
    cannot tell a dimension that scored low from one never assessed."""
    emitted = {k.partition("@v")[0] for k in EMITS_RUBRIC.values()}
    assert emitted == set(DIMENSIONS), (
        f"Stage A's scoring blocks emit {sorted(emitted)}; the scorecard needs "
        f"{sorted(DIMENSIONS)}"
    )


def test_dx_81_a_block_with_no_answer_enum_declares_no_options():
    """⚠ `options` is the block's ANSWER set and `RA-17` order-randomises it.

    ★ Empty must mean *"this block does not answer with an enum"*, never *"the
    enum is not filled in yet"* — those are the same value and opposite
    meanings, so the distinction is asserted rather than commented.
    ⚠⚠ `J-08` CONTAINS a closed set (item 5's supply read) and still declares
    none: that enum belongs to a FIELD. Passing it would permute the wrong thing
    and record a permutation describing nothing.
    """
    enum_answering = {"J-01", "J-07"}
    for block_id in STAGE_A:
        options = BLOCKS[block_id][1]
        if block_id in enum_answering:
            assert options, f"{block_id} answers with an enum and must declare it"
            assert "insufficient_evidence" in options, (
                f"{block_id}: MP-7 — a block with no way to say 'I could not' "
                f"will always find something to say"
            )
        else:
            assert options == (), (
                f"{block_id} does not answer with an enum; `options` must be "
                f"empty so RA-17 permutes nothing (DX-81)"
            )


def test_the_registry_and_the_factory_agree_about_options():
    """⚠⚠ Found by mutation, and it is `DX-41`'s shape inside a test written to
    prevent `DX-41`'s shape.

    `BLOCKS[b]` carries an options tuple AND `BLOCKS[b][0]()` builds a block with
    its own. ★ Nothing made them equal. The first draft of
    `test_dx_81_a_block_with_no_answer_enum_declares_no_options` read the
    REGISTRY's copy, so a mutation that gave `J-08`'s factory a field enum —
    exactly the mistake that test exists to catch — **passed clean**.

    ⚠ Two places holding one fact is the defect; this asserts they hold the same
    one, and `RA-17` permutes whichever the caller reaches for.
    """
    for block_id, (factory, declared, _v) in BLOCKS.items():
        blk = factory()
        if blk.kind != "judgement":
            continue                      # extraction slot 2 is item ids, not options
        assert tuple(blk.options) == tuple(declared), (
            f"{block_id}: BLOCKS declares options={declared!r} but the factory "
            f"builds {blk.options!r} — two places, one fact, and they disagree"
        )


def test_dx_81_the_judgement_tool_serves_every_declared_shape():
    """★★★ This test previously asserted the OPPOSITE, on purpose.

    ⚠ Until 2026-09-11 it read `test_..._serves_only_the_enum_shape` and pinned
    that six of eight Stage-A blocks had no schema — written to **fail the
    moment someone widened the tool**, so the limit could not be widened
    silently and left undocumented. ★ It failed on the next commit, which is the
    design working: the limit was recorded where the person changing it had to
    read it.

    It now pins the three shapes that exist. ⚠ If a fourth is added, this fails
    again and must be rewritten again — that is the intended cost.
    """
    from tools.run_judgement_once import answer_shape

    shapes = {b: answer_shape(BLOCKS[b][0]()) for b in STAGE_A}
    assert shapes == {
        "J-01": "enum", "J-07": "enum",
        "J-03": "rubric", "J-04": "rubric", "J-05": "rubric", "J-06": "rubric",
        "J-02": "prose", "J-08": "prose",
    }
    # ⚠⚠ STILL NOT MODELLED, named so it is not assumed complete: `J-03`'s STEP 1
    #    mechanism table (5 mechanisms x present/absent/insufficient_evidence)
    #    and `J-08`'s per-competitor sentences are folded into `why`/`answer`.
    #    ★ They are real structured fields and this schema does not carry them.
    assert "intangible_assets" in BLOCKS["J-03"][0]().text
    assert "mechanism" not in str(_tool("J-03", criteria=CRITERIA)["input_schema"])


@pytest.mark.parametrize("block_id", STAGE_A)
def test_every_stage_a_block_hashes_its_own_text(block_id):
    """★ `block()` self-hashes at declaration (`RA-13`). A block whose hash does
    not cover its text cannot be pinned by anything downstream."""
    from src.fundamental.prompts.registry import content_hash

    blk = BLOCKS[block_id][0]()
    assert blk.declared_hash == content_hash(blk.text)
    assert blk.kind == "judgement"


# ═══════════════════════════════════════════════════════════════════════════
# `DX-81` — the answer SCHEMA, widened from one shape to three.
# ═══════════════════════════════════════════════════════════════════════════

RUBRIC_BLOCKS = ("J-03", "J-04", "J-05", "J-06")
#: Two stand-in criteria for schema-shape tests (the real ones come from an offer).
CRITERIA = ("criterion alpha", "criterion beta")
ENUM_BLOCKS = ("J-01", "J-07")
PROSE_BLOCKS = ("J-02", "J-08")


def _tool(block_id, **kw):
    from tools.run_judgement_once import judgement_tool
    return judgement_tool(BLOCKS[block_id][0](), **kw)


def test_dx_81_every_stage_a_block_now_has_a_schema():
    """★★ The gap `DX-81` named: six of eight blocks were declared and had no
    answer shape. ⚠ A declared block nothing can call is `DX-23`'s state."""
    for block_id in STAGE_A:
        kw = {"criteria": CRITERIA} if block_id in RUBRIC_BLOCKS else {}
        schema = _tool(block_id, **kw)
        assert schema["input_schema"]["required"], block_id


def test_dx_81_j01_field_name_is_UNCHANGED_because_a_signed_case_grades_it():
    """★★★ The constraint that shaped the design.

    ⚠⚠ `thesis.yaml::mu-fy2025q3-j01-archetype` asserts
    `expected: {archetype: cyclical_commodity}` against a recorded call, signed
    by the fund manager. Renaming this field to a neutral `answer` while
    generalising would have broken established `D2` work that cannot be
    regenerated — the tidy refactor is the destructive one.
    """
    import yaml

    schema = _tool("J-01")
    assert schema["name"] == "classify_archetype"
    assert "archetype" in schema["input_schema"]["properties"]

    case = yaml.safe_load(
        pathlib.Path("tests_src/fixtures/golden/thesis.yaml").read_text())["cases"][0]
    assert set(case["expected"]) <= set(schema["input_schema"]["properties"]), (
        "the signed thesis case asserts a field the J-01 schema no longer emits"
    )


def test_dx_81_a_rubric_block_REFUSES_a_default_level_set():
    """★★★ `RA-32` — a level whose `evidence_required` is absent from the bundle
    is UNAVAILABLE, so the enum is a property of THIS CALL, not of the rubric.

    ⚠ Defaulting to the full 0-4 would silently re-offer levels the evidence
    cannot support, which is the rubric's entire discipline discarded in one
    default argument. ★ `P5` — it raises instead.
    """
    for block_id in RUBRIC_BLOCKS:
        with pytest.raises(ValueError, match="RA-32"):
            _tool(block_id)


def test_dx_100_a_rubric_answer_is_a_CRITERION_never_a_number():
    """⛔⛔ `DX-100` — REWRITTEN. This test used to assert the opposite
    (`test_dx_81_a_rubric_level_is_an_INTEGER_enum`), and in doing so pinned
    the defect: an integer enum whose meaning the model was never shown.
    ★ `RA-31`: the answer is the criterion text, the score is derived; and
    `MP-7`: `insufficient_evidence` is a stated exit, not the floor."""
    from src.fundamental.scorecard.selection import INSUFFICIENT_EVIDENCE

    props = _tool("J-04", criteria=CRITERIA)["input_schema"]["properties"]
    assert "level" not in props and "score" not in props
    assert props["criterion"]["type"] == "string"
    assert props["criterion"]["enum"] == [*CRITERIA, INSUFFICIENT_EVIDENCE]


def test_dx_81_the_rubric_tool_is_named_for_the_dimension_it_scores():
    """★ A tool called `score_moat_durability` cannot be mistaken at the trace
    for one scoring a different dimension — `DX-80` is what ambiguity here
    costs."""
    from src.fundamental.prompts.e_blocks import EMITS_RUBRIC

    for block_id in RUBRIC_BLOCKS:
        dimension = EMITS_RUBRIC[block_id].partition("@v")[0]
        assert _tool(block_id, criteria=CRITERIA)["name"] == f"score_{dimension}"


def test_dx_81_j02_item_5_is_a_REQUIRED_FIELD_not_a_sentence():
    """★★ `MP-5` applied to a rule that was only prose. `J-02` says item 5 *"is
    mandatory and may not be 'nothing'"*. ⚠ `E-01` is the measured warning: a
    free string whose description said *"never invent one"* returned all 56
    items tagged with the block id. A description asks; a schema declares."""
    required = _tool("J-02")["input_schema"]["required"]
    assert "what_i_do_not_understand" in required


def test_dx_81_j08s_supply_read_is_a_closed_FIELD_enum():
    """⚠ `J-08` answers in prose AND carries one closed set for item 5. ★ It is
    a field enum, not the block's answer — `options` stays empty so `RA-17`
    permutes nothing, and the schema still declares the closed set."""
    from src.fundamental.prompts.e_blocks import J08_SUPPLY_OPTIONS

    schema = _tool("J-08")
    assert schema["input_schema"]["properties"]["supply_read"]["enum"] == list(
        J08_SUPPLY_OPTIONS)
    assert "supply_read" in schema["input_schema"]["required"]
    assert BLOCKS["J-08"][1] == ()


@pytest.mark.parametrize("block_id", ENUM_BLOCKS + PROSE_BLOCKS[1:])
def test_every_declared_enum_appears_VERBATIM_in_the_prompt_text(block_id):
    """★★★ The guard that keeps the schema and the prose from disagreeing.

    ⚠⚠ `MP-5` says a closed set is DECLARED rather than described — but if the
    declaration and the description name different values, the model is asked
    one thing and constrained to another, and the mismatch is invisible in both
    files. ★ Every option must be findable in the block's own text.
    """
    from src.fundamental.prompts.e_blocks import FIELD_ENUMS

    blk = BLOCKS[block_id][0]()
    values = list(blk.options) + [
        v for enum in FIELD_ENUMS.get(block_id, {}).values() for v in enum]
    assert values, f"{block_id} declares no closed set to check"
    missing = [v for v in values if v not in blk.text]
    assert not missing, (
        f"{block_id} declares {missing} in its schema but never names them in "
        f"its prompt text — the model is asked one thing and constrained to "
        f"another"
    )


# ═══════════════════════════════════════════════════════════════════════════
# `DX-84` — the judgement path bypasses the Gateway, so GW-23 never ran.
# ═══════════════════════════════════════════════════════════════════════════

def test_dx_84_the_judgement_runner_uses_the_declared_judgement_budget():
    """★★★ `MAX_OUT` was a THIRD output budget — 4,000 — smaller than either of
    the two already declared, sitting in a runner nobody diffed against them.

    ⚠⚠ Measured 2026-09-11: it truncated **7 of 8** Stage-A calls, and every one
    printed ✅. `J-01` came back missing its required `why` and still parsed as
    JSON, so the run reported "8/8 block(s)" on $3.22 of unusable output.
    ★ One fact, one place: the runner now takes `call.py`'s judgement budget.
    """
    from src.fundamental.prompts.call import MAX_TOKENS
    from tools.run_judgement_once import MAX_OUT

    assert MAX_TOKENS["judgement"] == MAX_OUT
    assert MAX_OUT > 4_000, "the budget that truncated Stage A must not return"


def test_dx_84_a_truncated_judgement_is_refused_not_reported_as_an_answer():
    """★★★ `GW-23` — *a truncated response is a failure, not a short answer.*

    ⚠⚠ The extraction path gets this from `Gateway.call`. This runner wires
    `anthropic_transport` STRAIGHT into `traced_transport`, so it never reaches
    the Gateway and the check simply did not exist on the judgement side.
    ★ The source is asserted rather than the behaviour because the check guards
    a LIVE call: a test that exercised it would have to spend money.
    """
    import pathlib as _p

    src = _p.Path("tools/run_judgement_once.py").read_text(encoding="utf-8")
    assert 'stop == "max_tokens"' in src, (
        "the judgement runner no longer refuses a truncated response — GW-23"
    )
    assert "a truncated response is a failure" in src


def test_dx_84_a_parsed_but_incomplete_answer_is_refused():
    """⚠ `J-01`'s truncated run dropped `why` and still parsed as valid JSON.

    ★ *"It parsed"* is not *"it is complete"* — the same mistake `DX-68` taught
    about *"it parses now"*. The runner checks the schema's own required list.
    """
    import pathlib as _p

    src = _p.Path("tools/run_judgement_once.py").read_text(encoding="utf-8")
    assert "missing required field(s)" in src


def test_dx_84_no_output_budget_is_declared_in_more_than_one_place():
    """⚠⚠ Three budgets existed: `call.py`'s 20,000/16,000, the runner's 4,000,
    and `anthropic_transport`'s model ceiling. ★ The first two must agree, and
    a fourth literal appearing in a runner is how the third one got written."""
    import pathlib as _p
    import re

    src = _p.Path("tools/run_judgement_once.py").read_text(encoding="utf-8")
    literals = re.findall(r"MAX_OUT\s*=\s*([0-9_]+)", src)
    assert not literals, (
        f"MAX_OUT is assigned a literal {literals} — it must come from "
        f"call.py::MAX_TOKENS so the judgement budget has one definition"
    )


def test_dx_82_the_runner_APPLIES_the_RA_32_gate_and_does_not_merely_compute_it():
    """★★★ Found by mutation: every test covered the pure function and none
    covered the CALLER, so `if False and gate_error:` passed clean.

    ⚠⚠ That is the `DX-41` shape again — a guard checking the thing beside the
    thing. A gate that is computed and then ignored is worse than no gate: it
    produces a reassuring log line and sends the call anyway.
    ★ Source-asserted because the path it guards is a LIVE call; exercising it
    would cost money.
    """
    import pathlib as _p

    src = _p.Path("tools/run_judgement_once.py").read_text(encoding="utf-8")
    assert "require_levels" in src, "the runner no longer applies RA-32"
    assert "if gate_error:" in src, (
        "the RA-32 refusal is computed but not acted on — a gate that is "
        "ignored is worse than none, because it logs reassuringly"
    )
    # ⚠ The refusal must happen BEFORE the request is built and sent.
    assert src.index("if gate_error:") < src.index("result = transport(request)")


def test_dx_82_no_rubric_block_is_billable_from_a_bare_filing_bundle():
    """★ The measurable consequence: `RA-32` makes the four rubric blocks
    unsendable today, so the ~$2.6 the ungated run spent on them cannot be
    spent again by accident."""
    from src.fundamental.scorecard.availability import available_levels
    for rubric in (MOAT_DURABILITY, EARNINGS_QUALITY,
                   BALANCE_SHEET_RESILIENCE, CAPITAL_ALLOCATION):
        assert available_levels(rubric, frozenset()) == ()


def test_dx_88_the_extraction_runner_offers_only_extraction_blocks_and_real_versions():
    """⚠ `DX-88` — once Stage A was declared, `run_extraction_once --block`
    offered `J-01`…`J-08`, and `--prompt-version` was pinned to `v2|v3` while
    `E-01` ships `v4`. ★ `RA-5`: an extraction runner must not accept a
    judgement block; `DX-72`: a version list must not be hardcoded."""
    import subprocess
    import sys

    out = subprocess.run([sys.executable, "tools/run_extraction_once.py", "--help"],
                         capture_output=True, text=True,
                         env={"PYTHONPATH": ".", "PATH": ""}).stdout
    block_line = next(line for line in out.splitlines() if "--block {" in line)
    assert "J-0" not in block_line, block_line
    assert "v4" in out, "E-01's shipped version is not selectable"
