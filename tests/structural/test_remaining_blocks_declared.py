"""`L3` §2.1p row 6 — the last undeclared prompt blocks (2026-10-04, Victor's scope).

★ A block is declared only when something CALLS it (`e_blocks.BLOCKS`: *"a registry entry
nothing calls is a claim, not a capability"*). So the deferred three are asserted ABSENT, each
with the reason, and the guard reds if one is declared without its workflow.
"""
import pytest

from src.fundamental.prompts.e_blocks import BLOCKS

#: Declared 2026-10-04, each with an input this repo holds and a runner path that calls it.
DECLARED_NOW = {"E-03": "v1", "E-05": "v1", "E-08": "v2", "E-11": "v1"}

#: ⊘ Deferred by Victor, 2026-10-04 — declared with the workflow that calls them.
DEFERRED = {
    "E-14": "the daily news gate — built at go-live with a news snapshot (FMP keeps ~92 days)",
    "J-18": "the pre-event brief — built with the event workflow in the daily run",
    "J-19": "industry-vs-company attribution — needs a D-02 peer-change computation first",
}


@pytest.mark.parametrize("block_id,version", sorted(DECLARED_NOW.items()))
def test_the_block_is_declared_at_its_version(block_id, version):
    factory, item_ids, declared = BLOCKS[block_id]
    assert declared == version and factory().version == version
    assert factory().kind == "extraction" and item_ids


@pytest.mark.parametrize("block_id", sorted(DEFERRED))
def test_a_deferred_block_is_NOT_declared_without_its_workflow(block_id):
    assert block_id not in BLOCKS, (
        f"{block_id} is declared, but its caller was deferred: {DEFERRED[block_id]}")


def test_each_item_id_is_the_blocks_own_item_list():
    """`MP-5` — the ids are parsed from the block's own text, never typed beside it."""
    import re
    for block_id in DECLARED_NOW:
        factory, item_ids, _v = BLOCKS[block_id]
        in_text = tuple(dict.fromkeys(re.findall(r"^  ([a-z]{2}\.[a-z_]+)", factory().text, re.M)))
        assert item_ids == in_text, block_id


def test_dx_148_e08_v2_asks_for_the_CODE_and_keeps_one_closed_label():
    """✏ `DX-148` ⓑ (Victor, 2026-10-04): `in.type` is the form's transaction code, verbatim —
    `X-01` ② checks it in its quote like any value; the label is MAPPED, never chosen.
    `in.plan_status` stays a declared closed set (`DX-122`)."""
    from src.fundamental.claims.classification import CLASSIFICATION_VALUES
    assert "in.type" not in CLASSIFICATION_VALUES
    assert CLASSIFICATION_VALUES["in.plan_status"] == ("10b5-1", "not_10b5-1", "not_stated")
    assert "the transaction code exactly as the form" in BLOCKS["E-08"][0]().text


@pytest.mark.parametrize("code,label", [
    ("S", "sale"), ("S(1)", "sale"), ("P", "purchase"), ("M(2)", "option exercise"),
    ("G", "gift"), ("A", "award"), ("F", "other"), ("X", "other"),
])
def test_dx_148_the_sec_code_maps_to_its_label(code, label):
    from src.fundamental.filings.form4 import transaction_label
    assert transaction_label(code) == label


@pytest.mark.parametrize("bad", ["", "sale", "(1)", "S M"])
def test_dx_148_a_value_that_is_not_a_code_RAISES(bad):
    from src.fundamental.filings.form4 import transaction_label
    with pytest.raises(ValueError):
        transaction_label(bad)
