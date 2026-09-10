"""`RA-13` / `DX-23` — a prompt's text in code must match the design doc.

⚠⚠ **Why this is structural, not a unit test.** `sdd/` is the source of truth
(`CLAUDE.md`: *"if code and spec ever disagree, one of them is a bug"*). E-01's
text was copied from `L1-fundamental-analysis-master-prompt.md` into
`e_blocks.py`, and a copy drifts silently: `block()` hashes the text at
declaration, so it catches a later edit to the FILE — it cannot catch the code
and the doc disagreeing, because it only ever sees one of them.

★ A prompt that has drifted from its spec makes every baseline recorded against
that version a statement about an unknown.
"""

from __future__ import annotations

import pathlib

from src.fundamental.prompts.e_blocks import E01_V2_TEXT, e01_v2

REPO = pathlib.Path(__file__).resolve().parents[2]
DOC = REPO / "sdd/design/rel6_design/L1-fundamental-analysis-master-prompt.md"
HEADING = "## E-01 · Segment revenue and operating income — `{v}`"


def _text_from_spec(version: str = "v2") -> str:
    body = DOC.read_text(encoding="utf-8").split(HEADING.format(v=version), 1)[1]
    return body.split("```text", 1)[1].split("```", 1)[0].lstrip("\n")


def test_ra_13_e01_prompt_text_is_byte_identical_to_the_spec():
    """⚠ If this reds, ONE of the two is a bug — decide which, then bump the
    version if the text is meant to change (`RA-13`)."""
    assert _text_from_spec() == E01_V2_TEXT, (
        "E-01's v2 prompt text in e_blocks.py has drifted from "
        "L1-fundamental-analysis-master-prompt.md §E-01"
    )


def test_ra_13_the_declared_hash_covers_that_text():
    """★ `block()` self-hashes at declaration — this pins that the hash the
    registry enforces is the hash of the text the spec published."""
    from src.fundamental.prompts.registry import content_hash
    assert e01_v2().declared_hash == content_hash(_text_from_spec())


def test_e01_is_declared_as_an_extraction_block():
    """`RA-5` — extraction and judgement are separate calls with separate
    prompts, and `assert_extraction_block` refuses the wrong kind."""
    assert e01_v2().kind == "extraction"


def test_mp_5_the_item_id_enum_matches_the_ids_named_in_the_prompt():
    """★★ MP-5 — the shape is enforced by the API, not by prose.

    ⚠ MEASURED: with `evidence_id` a free string whose *description* said
    "never invent one", the model returned all 56 items tagged `E-01` — the
    BLOCK id. The enum fixes that, and this test stops the enum drifting from
    the item list the prompt actually publishes.
    """
    from src.fundamental.prompts.e_blocks import E01_ITEM_IDS
    named = {ln.strip().split()[0] for ln in _text_from_spec().splitlines()
             if ln.startswith("  seg.")}
    assert set(E01_ITEM_IDS) == named, (
        "E01_ITEM_IDS and the ids listed in the E-01 prompt disagree"
    )


def test_mp_7_the_tool_schema_offers_a_stated_failure_output():
    """⚠⚠ MP-7 — *an LLM with no stated way to say "I could not" will always
    find something to say.* It did: a prose sentence in `value`, which X-01
    refused. The schema must carry `not_found`."""
    from src.fundamental.prompts.e_blocks import E01_ITEM_IDS
    from tools.anthropic_transport import extraction_tool
    props = (extraction_tool(E01_ITEM_IDS)["input_schema"]["properties"]
             ["items"]["items"]["properties"])
    assert props["status"]["enum"] == ["found", "not_found"]
    assert props["evidence_id"]["enum"] == list(E01_ITEM_IDS)


def test_ra_13_every_declared_version_matches_its_own_spec_section():
    """★★ A candidate prompt drifts as easily as a shipped one — more easily,
    because nothing runs it yet.

    ⚠ `v3` exists in code before it ships (`E01_CURRENT_VERSION` is still `v2`),
    so without this it could sit wrong for weeks and only be discovered by a
    live run that costs money.
    """
    from src.fundamental.prompts.e_blocks import E01_V2_TEXT, E01_V3_TEXT
    for version, text in (("v2", E01_V2_TEXT), ("v3", E01_V3_TEXT)):
        assert text == _text_from_spec(version), (
            f"E-01 {version} in e_blocks.py has drifted from the design doc"
        )


def test_v3_adds_a_reachable_exit_to_the_restatement_clause():
    """⚠⚠ `DX-31` — the defect `v3` exists to fix.

    `v2` demanded BOTH bases whenever a restatement was mentioned. AMD's filing
    states one and contains only the restated figures, so the demand was
    unsatisfiable and the model burned its whole budget producing nothing.
    ★★★ Every demand in a prompt needs a reachable exit.
    """
    from src.fundamental.prompts.e_blocks import E01_V2_TEXT, E01_V3_TEXT
    assert "presents only ONE basis" not in E01_V2_TEXT
    assert "presents only ONE basis" in E01_V3_TEXT
    assert "Do not search for figures the filing does not contain" in E01_V3_TEXT


#: ★ Each declared block and the heading its text lives under.
_BLOCK_HEADINGS = {
    "E-01": "## E-01 · Segment revenue and operating income — `{v}`",
    "E-02": "## E-02 · Guidance, and its revision — `{v}`",
}


def test_ra_13_every_DECLARED_block_matches_its_spec_section():
    """★★ The drift guard must grow with the registry, not lag it.

    ⚠ It covered `E-01` only. `E-02` was declared 2026-09-09, and a second
    block's text can drift from the design doc exactly as easily as the first —
    more easily while it has no cases and nothing runs it.
    """
    from src.fundamental.prompts.e_blocks import BLOCKS

    for block_id, (factory, _ids, version) in BLOCKS.items():
        heading = _BLOCK_HEADINGS[block_id].format(v=version)
        body = DOC.read_text(encoding="utf-8").split(heading, 1)[1]
        spec = body.split("```text", 1)[1].split("```", 1)[0].lstrip("\n")
        assert factory().text == spec, (
            f"{block_id} {version} in e_blocks.py has drifted from the design doc"
        )


def test_every_declared_block_is_covered_by_the_drift_guard():
    """⚠ A block added to BLOCKS but not to _BLOCK_HEADINGS would be declared
    and UNGUARDED — the guard would silently stop covering the registry."""
    from src.fundamental.prompts.e_blocks import BLOCKS
    assert set(BLOCKS) == set(_BLOCK_HEADINGS)
