"""D-01 §7.1 — RM-1's k-run probe against a real authoring path.

★★ **§12's API said `k > 1` runs the stability probe, and nothing ran it.** The
probe machinery measured verdicts a caller produced by hand; the authoring path
produced one. This wires them.

⚠ **Two defects only a live run could find**, both recorded as RA-145/RA-146:
J-15 tells the model to choose a field *"from the supplied list of available
observables"* and **nothing supplied one**; and once the list existed, the
**blind view withheld it**, because it began as a `computed` part.

Tier: unit + integration (constitution §4).
"""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from src.fundamental import (
    AuthoringRun, ResearchError, assemble, computed, filing, profile,
)
from src.fundamental.bundle.assemble import observables
from src.fundamental.bundle.models import BLIND_WITHHELD_KINDS, PIN_FIELDS
from src.fundamental.prompts.blocks.j_blocks import (
    ALL_BLOCKS, J11, J15, J16, production_registry,
)
from src.fundamental.prompts.call import AnalysisGateway
from src.fundamental.thesis.probe import (
    APPLIED_PERTURBATIONS, assert_publishable, author_thesis, evidence_rotation,
    perturb_bundle,
)
from src.fundamental.thesis.run import ParsedVerdict, author_once, parse_falsifiers

AS_OF = date(2026, 8, 25)
OBSERVABLES = ("f_gross_margin", "f_net_debt_ebitda", "mom_21", "vol_21")
DECODING = {"control": "effort", "value": "high", "thinking_mode": "adaptive"}


def bundle():
    return assemble(ticker="MU", as_of=AS_OF, parts=[
        filing("0000-1", "Micron FQ3 2026: gross margin 55.4%, up from 51.2%."),
        computed("b3_minimal", 1, "f_gross_margin=0.554 price=182.40"),
        profile(AS_OF, "Micron. Memory semiconductors. Cyclical commodity."),
        observables(OBSERVABLES)])


class FakeGateway:
    """Records what each prompt was shown — ★ the thing the perturbation moves."""

    def __init__(self, verdicts=("BUY", "BUY", "BUY")):
        self.verdicts = list(verdicts)
        self.seen: list = []

    def call(self, *, prompt_name, prompt_version, tier, payload, max_tokens,
             run_id, schema=None, ticker=None):
        self.seen.append((prompt_name,
                          tuple(p["kind"] for p in payload["bundle"]["parts"])))
        if prompt_name == "J-16":
            verdict = self.verdicts[
                min(len([s for s in self.seen if s[0] == "J-16"]) - 1,
                    len(self.verdicts) - 1)]
            text = f"Verdict: {verdict}. Conviction: Medium-High."
        elif prompt_name == "J-15":
            text = ("Gross margin below 55% for two consecutive quarters — "
                    "f_gross_margin — the pricing-power premise fails.\n"
                    "Net debt to EBITDA above 3.0x at any quarter-end — "
                    "f_net_debt_ebitda — the balance-sheet premise fails.")
        else:
            text = ("Capacity additions crush DRAM pricing by FY2028.\n"
                    "Industry utilisation above 90% for three quarters confirms it.")
        call = SimpleNamespace(
            model_id="stub",
            decoding=SimpleNamespace(to_json_obj=lambda: dict(DECODING)),
            tokens_in=900, tokens_out=300, attempts=1, outcome="ok",
            call_id=f"c-{prompt_name}-{len(self.seen)}")
        return SimpleNamespace(text=text, parsed=None, call=call)


def probe(k=3, verdicts=("BUY", "BUY", "BUY")):
    fake = FakeGateway(verdicts)
    gateway = AnalysisGateway(fake, production_registry())
    source = bundle()

    def author(b, i):
        return author_once(bundle=b, gateway=gateway,
                           run=AuthoringRun(ticker="MU", as_of=AS_OF), index=i,
                           observables=OBSERVABLES, deadline=date(2027, 3, 31),
                           run_id=f"probe-{i}")

    return author_thesis(source, author=author, k=k), fake, source


# --------------------------------------------------------------------------- #
# RA-16 — the ordering the whole thing turns on
# --------------------------------------------------------------------------- #

def test_ra16_the_falsifiers_are_written_before_the_verdict():
    """★★ RA-16 — ⚠ *one call emitting both satisfies the old wording and buys
    nothing: **the falsifiers get fitted to a verdict already reached.***"""
    _, fake, _ = probe(k=1)
    names = [prompt for prompt, _ in fake.seen]
    assert names == ["J-11", "J-15", "J-16"]
    assert names.index("J-15") < names.index("J-16")


def test_ra15_the_bear_case_is_a_separate_call():
    """RA-15 — ★ so it cannot be written by the pass that argued the bull."""
    _, fake, _ = probe(k=1)
    assert [p for p, _ in fake.seen].count("J-11") == 1


def test_ra14_stage_c_and_d_calls_read_the_full_bundle_per_stage_view():
    """RA-14 / MP-3 — ✏ `DX-110` (2026-09-15). ⚠ This asserted J-11 and J-15 ran BLIND,
    pinning the old path's contradiction of the master prompt and `author.STAGE_VIEW`
    (Stages C and D are `view:full`). ★ The blind view is Stage A's, and the Stage-A
    freeze is still made over `bundle.redact()` inside `run.author`."""
    from src.fundamental.thesis.author import STAGE_C, STAGE_D, STAGE_VIEW

    assert STAGE_VIEW[STAGE_C] == STAGE_VIEW[STAGE_D] == "full"
    _, fake, _ = probe(k=1)
    for prompt, kinds in fake.seen:
        assert "computed" in kinds, f"{prompt} is Stage C/D and reads the full bundle"


# --------------------------------------------------------------------------- #
# RA-145 / RA-146 — what the live run found
# --------------------------------------------------------------------------- #

def test_ra146_the_observables_list_survives_the_blind_view():
    """★★ RA-146 — ⚠ the list began as a `computed` part and **the blind view
    stripped it**, so J-11 and J-15 — *the two calls that run blind* — were
    exactly the ones that could not see it.

    ★ **RA-14 withholds ANCHORS, not vocabulary**: `f_gross_margin` says what is
    checkable, never what it is worth.
    """
    assert "observables" in PIN_FIELDS
    assert "observables" not in BLIND_WITHHELD_KINDS
    _, fake, _ = probe(k=1)
    for prompt, kinds in fake.seen:
        assert "observables" in kinds, prompt


def test_ra145_a_falsifier_naming_no_field_is_refused():
    """★★ RA-145 / RA-35 — ⚠ *a falsifier naming a field this system does not
    receive is not checkable, however precise it sounds* — and one naming **no**
    field is worse.

    This is verbatim what the live model produced before the list existed:
    well-formed prose, no field, `NoFalsifierError`.
    """
    fieldless = ("Reported gross margin prints below 51.2% in any quarter "
                 "reported on or before the FQ2 2027 filing.\n"
                 "The HBM sell-out disclosure disappears from two filings.")
    assert parse_falsifiers(fieldless, deadline=date(2027, 3, 31),
                            observables=OBSERVABLES) == ()

    named = ("Gross margin below 55% for two quarters — f_gross_margin — "
             "the pricing-power premise fails.")
    (falsifier,) = parse_falsifiers(named, deadline=date(2027, 3, 31),
                                    observables=OBSERVABLES)
    assert falsifier.observable_field == "f_gross_margin"


# --------------------------------------------------------------------------- #
# RM-1 — the probe itself
# --------------------------------------------------------------------------- #

def test_the_perturbation_moves_what_the_model_reads_not_the_bundle():
    """★★ ⚠ **`evidence_order` was a no-op for its first hour.**

    The obvious implementation rotates `bundle.parts` — and
    `EvidenceBundle.__post_init__` **sorts them**, because RA-4 makes the hash
    independent of arrival order. The rotation was undone before the bundle
    was returned, and the probe **reported a perturbation it never applied.**

    ★ The order must move where it reaches the model — the composed payload —
    which leaves `bundle_hash` identical, and that is what makes the k runs
    comparable at all (RA-2).
    """
    source = bundle()
    assert perturb_bundle(source, 2) is source, "the bundle is NOT perturbed"
    assert evidence_rotation(source, 1) != evidence_rotation(source, 2)

    _, fake, used = probe(k=3)
    orders = [kinds for prompt, kinds in fake.seen if prompt == "J-16"]
    assert len(set(orders)) == 3, "three runs, three payload orderings"
    assert used.bundle_hash == bundle().bundle_hash, "the bundle never changed"


def test_prompt_paraphrase_is_declared_absent_not_silently_skipped():
    """★ RA-13 hashes the prompt, so a paraphrase is a **new version**, not a
    perturbation of one. ⚠ *Declaring a robustness you did not test is worse
    than testing neither.*"""
    assert APPLIED_PERTURBATIONS == ("option_order", "evidence_order")
    probed, _, _ = probe(k=3)
    assert "prompt_paraphrase" not in probed.stability.perturbations_applied


def test_ra17_the_verdict_options_are_permuted_per_call():
    """RA-17 — ★ enumerated options are order-randomised and **recorded**."""
    assert set(J16.options) == {"BUY", "HOLD", "SELL", "INSUFFICIENT_DATA"}
    probed, _, _ = probe(k=3)
    permutations = {r.option_permutation for r in probed.runs}
    assert all(set(p) == set(J16.options) for p in permutations)


def test_ac_1_8_k_below_three_is_not_actionable():
    """★★ AC-1.8 / RA-20 / BS-28 — ⚠ *`k=1` is not a failure* — it is a
    legitimate cheap run whose output is **not actionable**. What is forbidden
    is publishing one as though it were."""
    single, _, _ = probe(k=1)
    # ★ `None`, not a weak result — `StabilityResult` refuses to exist below
    #   K_STAB, and `CT-1.1.verdict_stability` is `null` for exactly this case.
    assert single.stability is None and single.actionable is False
    assert single.to_json_obj()["verdict_stability"] is None
    assert single.thesis.verdict_stability is None
    with pytest.raises(ResearchError, match="may not be the one thing INV-6"):
        assert_publishable(single)

    three, _, _ = probe(k=3)
    assert three.actionable is True
    assert_publishable(three)


def test_a_split_verdict_lowers_agreement_and_stays_publishable():
    """RA-20 — ★ *the fraction is published verbatim*; the probe measures, it
    does not judge. A 2/3 split is a real result, not a failure."""
    probed, _, _ = probe(k=3, verdicts=("BUY", "BUY", "HOLD"))
    assert probed.stability.modal == "BUY"
    assert probed.stability.agreement == pytest.approx(2 / 3)
    assert probed.thesis.verdict_stability["agreement"] == pytest.approx(2 / 3)


def test_the_published_thesis_is_the_first_run_not_a_vote():
    """★ *A modal verdict assembled from k runs is a thesis nobody wrote*, and
    its falsifiers would belong to a different pass than its verdict (RA-16)."""
    probed, _, _ = probe(k=3, verdicts=("HOLD", "BUY", "BUY"))
    assert probed.thesis.verdict == "HOLD" == probed.runs[0].verdict
    assert probed.stability.modal == "BUY" != probed.thesis.verdict


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


def test_an_unparseable_verdict_raises_rather_than_defaulting():
    """P5 — ★ the model was given a bounded option list; a response that names
    none of them is a failure, **never `INSUFFICIENT_DATA` by default**."""
    from src.fundamental import VerdictNotEnumError

    assert ParsedVerdict.parse("Verdict: SELL. Conviction: Low.").verdict == "SELL"
    with pytest.raises(VerdictNotEnumError):
        ParsedVerdict.parse("I would need more information to say.")
