"""`F8` `AC-8.16` — ⚠⚠ a directive's raw text never reaches a prompt.

★★ The AC is typed *invariant / property (structural)* and was enforced by a
**unit test on one object** (`DX-51`): `Directive.to_prompt_payload()` omits
`raw_text`, and a test asserted that. ⚠ Nothing stopped a different module
reading `.raw_text` and building a prompt of its own.

★★★ §2.1 states the harm plainly: *"Injecting it into an analysis prompt would
reintroduce exactly the unfalsifiable, untestable control `QR-17`'s analysis
rejected."* Put another way — a directive reaching a prompt is **an untyped
instruction channel into the analysis, with the fund manager as the injection
vector**, and `AC-8.15`'s confirm step would be approving typed effects while
unreviewed prose travelled beside them.
"""

from __future__ import annotations

from tools.check_no_raw_directive_in_prompt import RAW_FIELD, raw_text_leaks


def test_ac_8_16_no_prompt_building_module_touches_raw_text():
    """The live tree. ⚠ No skip, no tolerance list."""
    assert raw_text_leaks() == []


def test_ac_8_16_an_attribute_read_in_a_prompt_module_is_caught(tmp_path):
    """⚠ The check must be able to FAIL, or it is decoration."""
    root = tmp_path / "src" / "fundamental" / "prompts"
    root.mkdir(parents=True)
    (root / "build.py").write_text(
        "def build(directive):\n"
        "    return f'Consider: {directive.raw_text}'\n")
    hits = raw_text_leaks(tmp_path)
    assert len(hits) == 1 and "AC-8.16" in hits[0]


def test_ac_8_16_a_dict_key_lookup_is_caught_too(tmp_path):
    """★★ The realistic shape. A trace record read back from JSON is a **dict**,
    so `payload["raw_text"]` is how this actually arrives — an attribute-only
    check would miss the path most likely to be taken."""
    root = tmp_path / "src" / "shared" / "llm"
    root.mkdir(parents=True)
    (root / "gateway.py").write_text(
        "def send(payload):\n"
        "    return payload['raw_text']\n")
    hits = raw_text_leaks(tmp_path)
    assert len(hits) == 1


def test_ac_8_16_the_directives_module_itself_may_hold_it(tmp_path):
    """★ `CT-8.4` REQUIRES `raw_text` — it is recorded for the audit trail, and
    `CT-8.6`'s unmappable log exists to show it back to the manager
    (`AC-8.19`). ⚠ A check that banned the field outright would forbid the
    audit trail the same clause mandates."""
    root = tmp_path / "src" / "orchestration" / "control"
    root.mkdir(parents=True)
    (root / "directives.py").write_text("raw_text = 'kept for audit'\n")
    assert raw_text_leaks(tmp_path) == []


def test_ac_8_16_the_field_name_is_the_one_the_contract_uses():
    """⚠ A structural check keyed to the wrong field name passes forever."""
    from src.orchestration.control.directives import Directive
    assert RAW_FIELD in Directive.__dataclass_fields__
