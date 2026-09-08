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

from src.fundamental.prompts.e_blocks import E01_V1_TEXT, e01_v1

REPO = pathlib.Path(__file__).resolve().parents[2]
DOC = REPO / "sdd/design/rel6_design/L1-fundamental-analysis-master-prompt.md"
HEADING = "## E-01 · Segment revenue and operating income — `v1`"


def _text_from_spec() -> str:
    body = DOC.read_text(encoding="utf-8").split(HEADING, 1)[1]
    return body.split("```text", 1)[1].split("```", 1)[0].lstrip("\n")


def test_ra_13_e01_prompt_text_is_byte_identical_to_the_spec():
    """⚠ If this reds, ONE of the two is a bug — decide which, then bump the
    version if the text is meant to change (`RA-13`)."""
    assert _text_from_spec() == E01_V1_TEXT, (
        "E-01's prompt text in e_blocks.py has drifted from "
        "L1-fundamental-analysis-master-prompt.md §E-01"
    )


def test_ra_13_the_declared_hash_covers_that_text():
    """★ `block()` self-hashes at declaration — this pins that the hash the
    registry enforces is the hash of the text the spec published."""
    from src.fundamental.prompts.registry import content_hash
    assert e01_v1().declared_hash == content_hash(_text_from_spec())


def test_e01_is_declared_as_an_extraction_block():
    """`RA-5` — extraction and judgement are separate calls with separate
    prompts, and `assert_extraction_block` refuses the wrong kind."""
    assert e01_v1().kind == "extraction"


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
