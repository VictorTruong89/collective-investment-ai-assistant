"""`DX-76` — the shared prompt envelope has a recordable identity.

⚠⚠ `DX-67` composed `S-1`…`S-6` in front of every call this project makes and
bumped **no version**, so `F2`'s `prompt_version` — which names the BLOCK — left
a pre-envelope and a post-envelope recording indistinguishable in the trace.
★ These tests pin the half that was missing.
"""

from __future__ import annotations

# ── DX-76 · the envelope has an identity, and it is the one that was SENT ────

def test_dx_76_the_hash_covers_exactly_the_bytes_prepended_to_the_block():
    """★★★ The property that makes the hash worth recording: it is a hash of
    what the VENDOR SAW, not of a parallel list that happens to look similar.

    ⚠ A hash assembled from its own copy of the section order would drift from
    `compose_prompt` silently — and a hash of something never sent is worse
    than no hash, because it reads as evidence.
    """
    from src.fundamental.prompts.e_blocks import e01_v4
    from src.fundamental.prompts.envelope import compose_prompt, envelope_hash
    from src.fundamental.prompts.registry import content_hash

    block = e01_v4()
    sent = compose_prompt(block)
    prefix = sent[: len(sent) - len(block.text.strip("\n"))].rstrip("\n")
    assert content_hash(prefix) == envelope_hash("extraction")


def test_dx_76_a_different_envelope_is_a_different_hash():
    """⚠ `S-7` is Stage-A only (`MP-3` — *an absent field is a guarantee*), so
    a Stage-A judgement and a later-stage one are NOT the same prompt regime
    and must not record the same identity."""
    from src.fundamental.prompts.envelope import envelope_hash

    plain = envelope_hash("judgement")
    stage_a = envelope_hash("judgement", stage_a=True)
    fresh = envelope_hash("judgement", fresh=True)
    assert len({plain, stage_a, fresh}) == 3
    assert envelope_hash("extraction") != plain


def test_dx_76_an_unknown_kind_raises_rather_than_hashing_nothing():
    """`P5` — a kind with no envelope must not quietly hash the empty string
    and report a confident identity for a call nothing composed."""
    import pytest

    from src.fundamental.prompts.envelope import envelope_hash

    with pytest.raises(ValueError, match="RA-5"):
        envelope_hash("ranking")
