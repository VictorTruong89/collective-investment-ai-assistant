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


#: ⚠⚠ `DX-72` — **every declared version, discovered rather than listed.**
#: This guard checked `v2` and only `v2`. By 2026-09-11 the SHIPPED version was
#: `v3` — so the drift guard was pinning a version nothing sent, while the text
#: actually reaching the vendor was unchecked. ★ `v3` happened to match the doc,
#: so the gap cost nothing; it was still a guard watching the wrong object.
#: ⚠ A hardcoded version list would reproduce the defect at the next bump, so
#: the versions come from the module.
def _declared_e01_versions() -> dict:
    import src.fundamental.prompts.e_blocks as eb
    return {v: getattr(eb, f"E01_{v.upper()}_TEXT")
            for v in ("v2", "v3", "v4") if hasattr(eb, f"E01_{v.upper()}_TEXT")}


def test_ra_13_e01_prompt_text_is_byte_identical_to_the_spec():
    """⚠ If this reds, ONE of the two is a bug — decide which, then bump the
    version if the text is meant to change (`RA-13`).

    ★ `DX-72` — asserts EVERY declared version, not just the first one written.
    """
    declared = _declared_e01_versions()
    assert declared, "no E-01 version is declared — the guard would pass vacuously"
    for version, text in declared.items():
        assert _text_from_spec(version) == text, (
            f"E-01's {version} prompt text in e_blocks.py has drifted from "
            f"L1-fundamental-analysis-master-prompt.md §E-01 `{version}`"
        )


def test_ra_13_the_declared_hash_covers_that_text():
    """★ `block()` self-hashes at declaration — this pins that the hash the
    registry enforces is the hash of the text the spec published."""
    import src.fundamental.prompts.e_blocks as eb
    from src.fundamental.prompts.registry import content_hash
    for version in _declared_e01_versions():
        factory = getattr(eb, f"e01_{version}")
        assert factory().declared_hash == content_hash(_text_from_spec(version))


def test_dx_72_the_version_the_registry_ships_is_one_the_guard_checks():
    """★★★ `DX-72`'s actual lesson. A drift guard that checks a version nobody
    sends is a guard watching the wrong object — and it reads as coverage.

    ⚠ Same family as `DX-41`, `DX-63`, `DX-67`, `DX-70`: **a guard keeps
    checking exactly what it was written to check while the thing beside it
    goes unchecked.**
    """
    from src.fundamental.prompts.e_blocks import BLOCKS, E01_CURRENT_VERSION
    assert E01_CURRENT_VERSION in _declared_e01_versions()
    assert BLOCKS["E-01"][0]().version == E01_CURRENT_VERSION


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
    from src.fundamental.prompts.e_blocks import E01_V3_TEXT
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
    from src.fundamental.prompts.e_blocks import E01_V3_TEXT
    assert "presents only ONE basis" not in E01_V2_TEXT
    assert "presents only ONE basis" in E01_V3_TEXT
    assert "Do not search for figures the filing does not contain" in E01_V3_TEXT


#: ★ Each declared block and the heading its text lives under.
_BLOCK_HEADINGS = {
    "E-01": "## E-01 · Segment revenue and operating income — `{v}`",
    "E-02": "## E-02 · Guidance, and its revision — `{v}`",
    # ⚠ `J-01` is a JUDGEMENT block and its section sits one level deeper
    #   (`###`) in the design doc. ★ Declared 2026-09-10 (`DX-64`) — the first
    #   J-block with text in `src/`, after `STAGE_BLOCKS` had named J-01…J-17
    #   for months with none of them constructible.
    "J-01": "### J-01 · Industry archetype — `{v}`",
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


# ═══════════════════════════════════════════════════════════════════════════
# `DX-67` — the SHARED ENVELOPE. ⚠⚠ The guard above pinned BLOCK text and
# passed throughout, while §3.0/§4.0's composition rule went unimplemented for
# every call this project ever made. ★ A guard keeps checking exactly what it
# was written to check; the thing beside it goes unchecked.
# ═══════════════════════════════════════════════════════════════════════════

def test_dx67_every_envelope_section_matches_its_spec_section():
    """`RA-13` for `S-1`…`S-9`, the same discipline block text already had."""
    from src.fundamental.prompts.envelope import ALL_SECTIONS

    doc = DOC.read_text(encoding="utf-8")
    for name, text in ALL_SECTIONS.items():
        n = name.split("-")[1]
        body = doc.split(f"## S-{n} · ", 1)[1]
        spec = body.split("```text", 1)[1].split("```", 1)[0].strip("\n")
        assert text.strip("\n") == spec, f"{name} has drifted from the design doc"


def test_dx67_the_guard_covers_every_section_the_doc_declares():
    """⚠ A section added to the doc but not to `ALL_SECTIONS` would be
    unguarded — and one never composed at all is exactly `DX-67`."""
    import re

    doc = DOC.read_text(encoding="utf-8")
    declared = set(re.findall(r"^## (S-\d) · ", doc, re.M))
    from src.fundamental.prompts.envelope import ALL_SECTIONS
    assert declared == set(ALL_SECTIONS), (
        f"doc declares {sorted(declared)}, envelope.py carries "
        f"{sorted(ALL_SECTIONS)}")


def test_dx67_an_EXTRACTION_block_composes_S1_to_S6_and_the_preamble():
    """§3.0 — *"Composed into every E-block: S-1 · S-2 · S-3 · S-4 · S-5 · S-6."*"""
    from src.fundamental.prompts.e_blocks import e01_v3
    from src.fundamental.prompts.envelope import (
        EXTRACTION_PREAMBLE,
        EXTRACTION_SECTIONS,
        compose_prompt,
    )

    out = compose_prompt(e01_v3())
    assert out.startswith(EXTRACTION_PREAMBLE.strip("\n"))
    for sec in EXTRACTION_SECTIONS:
        assert sec.strip("\n") in out
    # ★ the block is LAST: the envelope states the rules, the block asks the
    #   question, and a question answered before its rules are read is the
    #   ordering this composition exists to prevent.
    assert out.rstrip().endswith(e01_v3().text.strip())


def test_dx67_a_JUDGEMENT_block_gets_the_judgement_preamble_not_the_extraction_one():
    """★ `RA-5` — extraction and judgement are told different things about what
    their answer is worth. ⚠ Handing a judgement block the extraction preamble
    (*"no part of your answer may be an opinion"*) would forbid the task."""
    from src.fundamental.prompts.e_blocks import j01_v1
    from src.fundamental.prompts.envelope import (
        EXTRACTION_PREAMBLE,
        JUDGEMENT_PREAMBLE,
        compose_prompt,
    )

    out = compose_prompt(j01_v1(), stage_a=True)
    assert JUDGEMENT_PREAMBLE.strip("\n") in out
    assert EXTRACTION_PREAMBLE.strip("\n") not in out


def test_dx67_S7_is_STAGE_A_ONLY():
    """⚠⚠ §4.0 — `S-7` is the anti-anchoring notice and applies to Stage A
    alone. ★ `MP-3` makes the staging physical (the blind bundle carries no
    price); `S-7` is the half that says so in words. A Stage-B block receiving
    it would be told not to anchor on a price it may legitimately see."""
    from src.fundamental.prompts.e_blocks import j01_v1
    from src.fundamental.prompts.envelope import STAGE_A_SECTION, compose_prompt

    assert STAGE_A_SECTION.strip("\n") in compose_prompt(j01_v1(), stage_a=True)
    assert STAGE_A_SECTION.strip("\n") not in compose_prompt(j01_v1(), stage_a=False)


def test_dx67_S3_the_citation_contract_reaches_every_block():
    """★★★ The section whose absence actually mattered.

    *"An uncited factual claim is a defect, not a style choice. It fails the
    run."* ⚠ Extraction partly escaped because `X-01` enforces the same rule in
    code; judgement had no backstop, and `J-01`'s pre-envelope output carried no
    FACT/INFERENCE/ASSUMPTION tags because nothing asked for them.
    """
    from src.fundamental.prompts.e_blocks import e01_v3, e02_v2, j01_v1
    from src.fundamental.prompts.envelope import S3, compose_prompt

    for blk, kw in ((e01_v3(), {}), (e02_v2(), {}), (j01_v1(), {"stage_a": True})):
        assert S3.strip("\n") in compose_prompt(blk, **kw), f"{blk.name} lacks S-3"
