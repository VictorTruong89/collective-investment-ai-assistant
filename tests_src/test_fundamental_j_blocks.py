"""D-01 — the J-block registry `build_gateway` registers (`j_blocks.py`). MP-12, RA-13.

✏ 2026-10-05: moved out of `test_fundamental_probe.py` when the old three-call thesis
path (`thesis/run.py`, `probe.py`, `author_for.py`) was removed (L3 §2.1s). `j_blocks.py`
and `build_gateway` were KEPT — AC-1.38 needs `prompts/call.py` to remain D-01's one
gateway builder — so the hashing guard over the blocks stays.
"""

from __future__ import annotations

import pytest

from src.fundamental.prompts.blocks.j_blocks import (
    ALL_BLOCKS,
    J11,
    J15,
    J16,
    production_registry,
)


def test_the_j_blocks_are_the_master_prompts_text_and_are_hashed():
    """MP-12 / RA-13 — ★ a text edit without a version bump raises."""
    registry = production_registry()
    registry.check_all()
    assert {b.name for b in ALL_BLOCKS} == {"J-11", "J-15", "J-16"}
    assert (J11.view, J15.view, J16.view) == ("full", "full", "full")      # ✏ DX-110
    import src.fundamental.prompts.e_blocks as eb
    for blk in (J11, J15, J16):                  # ★ one text per name and version
        # ✏ 2026-10-01 — compare against the factory for THIS block's version: `J-15` is
        #   `v1` here (prose path) and `v2` in the Stage B–D runner, so the current
        #   registry entry is not the right reference for every block any more.
        factory = getattr(eb, f"{blk.name.lower().replace('-', '')}_{blk.version}")
        assert blk.text == factory().text
    object.__setattr__(J15, "text", J15.text + " edited")
    from src.fundamental import PromptDriftError
    with pytest.raises(PromptDriftError):
        J15.check()
    object.__setattr__(J15, "text", J15.text[: -len(" edited")])


# ✏ 2026-10-05 — the two `build_gateway` tests below came from the deleted
#   `test_fundamental_author_for.py`; `build_gateway` was KEPT, so its tests stay.

def test_a_missing_api_key_is_reported_as_configuration_not_as_no_thesis(monkeypatch):
    """P5 — ⚠ *"no API key"* and *"the model declined"* are different states, and
    a caller that cannot tell them apart reports a config fault as a verdict."""
    from src.fundamental.errors import ResearchError
    from src.fundamental.prompts.call import build_gateway

    monkeypatch.setenv("CIA_LLM_TRANSPORT", "anthropic_api")   # this test covers the API path (GW-24)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ResearchError, match="ANTHROPIC_API_KEY"):
        build_gateway()


def test_the_deep_tier_model_is_opus(monkeypatch):
    """INV-8 — thesis authoring is quality-critical and low-frequency."""
    from src.fundamental.prompts.call import THESIS_MODEL

    assert THESIS_MODEL == "claude-opus-5"
