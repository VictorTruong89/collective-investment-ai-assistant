"""D-01 B4.2 — AC-1.3, 1.3a, 1.3b, 1.4, 1.5, 1.5a (extraction and the citation spine).

★ **L3 §3A.4's done-when:** *an extracted value absent from its cited span raises
**without an LLM being asked**; every factual claim carries a resolvable span.*

Tier: unit + data contract. ⚠ **Not one test here constructs a gateway for the
verification path** — that is the point of X-01/X-02 being deterministic, and
`test_x01_and_x02_ask_no_llm_anything` asserts it structurally.
"""

from __future__ import annotations

import ast
from datetime import date
from pathlib import Path

import pytest

from src.fundamental import (
    ASSUMPTION,
    E_BLOCK_IDS,
    FACT,
    INFERENCE,
    Claim,
    ClaimSet,
    EvidenceSpan,
    ExtractionKindError,
    ExtractionResult,
    PromptRegistry,
    SpanMismatchError,
    SpanUnresolvableError,
    UncitedClaimError,
    ValueNotInSpanError,
    assemble,
    assert_extraction_block,
    block,
    filing,
    item,
    not_found,
    profile,
    x01_verify_extraction,
    x02_verify_claims,
)

AS_OF = date(2026, 8, 23)

#: One filing, whose exact character offsets the tests index into. The quote at
#: [24, 62] is "Revenue was $1,234 thousand for the quarter".
DOC = ("MICRON TECHNOLOGY 10-Q. Revenue was $1,234 thousand for the quarter, "
       "against $1,100 thousand a year earlier. Cost of revenue was $740 thousand.")


def bundle():
    return assemble(ticker="MU", as_of=AS_OF,
                    parts=[filing("0000-1", DOC), profile(AS_OF, "Sector: IT")])


def span_of(text: str) -> tuple[int, int]:
    start = DOC.index(text)
    return start, start + len(text)


#: ⚠ A sentinel, because `kw.pop("offset", span_of(quote))` evaluates the default
#: eagerly — and a test that deliberately quotes text the document does NOT
#: contain would then fail inside the helper instead of inside the check.
_DERIVE = object()


def found(**kw):
    quote = kw.pop("quote", "Revenue was $1,234 thousand for the quarter")
    offset = kw.pop("offset", _DERIVE)
    return item(kw.pop("evidence_id", "seg.revenue"),
                value=kw.pop("value", "1,234"), unit=kw.pop("unit", "thousands of USD"),
                quote=quote, accession_id=kw.pop("accession_id", "0000-1"),
                offset=span_of(quote) if offset is _DERIVE else offset,
                period_start=kw.pop("period_start", "2026-03-01"),
                period_end=kw.pop("period_end", "2026-05-30"), **kw)


# --------------------------------------------------------------------------- #
# AC-1.3 / AC-1.3a — X-01
# --------------------------------------------------------------------------- #

def test_ac_1_3_a_value_absent_from_its_cited_span_raises():
    """AC-1.3 — RA-6. ★ B4.2's done-when, first clause."""
    good = x01_verify_extraction(bundle(), [found()])
    assert good.checked == 1

    with pytest.raises(ValueNotInSpanError, match="does not appear in its cited span"):
        x01_verify_extraction(bundle(), [found(value="9,999")])


def test_ac_1_3a_x01_resolves_the_offset_before_looking_for_the_value():
    """AC-1.3a — ★★ **RA-131, the defect this slice found.**

    ```
    THE OFFSET IS THE ONLY PART OF A CITATION THE MODEL CANNOT ALSO AUTHOR.
    ```

    A model that fabricates the quote **and** the value consistently passes a
    value-in-quote check — the citation is fiction with a character range
    attached. Here the quote is internally consistent with its value and
    disagrees with the document.
    """
    fabricated = found(
        quote="Revenue was $9,999 thousand for the quarter",
        value="9,999",
        offset=span_of("Revenue was $1,234 thousand for the quarter"),
    )
    with pytest.raises(SpanMismatchError, match="disagrees with the document"):
        x01_verify_extraction(bundle(), [fabricated])


def test_ac_1_3a_an_unresolvable_span_raises_rather_than_passing_quietly():
    """RA-131 — *an uncheckable citation is indistinguishable from a fabricated one.*"""
    with pytest.raises(SpanUnresolvableError, match="holds no filing"):
        x01_verify_extraction(bundle(), [found(accession_id="0000-9")])
    with pytest.raises(SpanUnresolvableError, match="past the end"):
        x01_verify_extraction(bundle(), [found(offset=(10, 99999))])


def test_ac_1_3b_a_reformatted_single_figure_passes():
    """AC-1.3b — RA-132's permitted half: **normalising ONE stated figure**."""
    b = bundle()
    for value in ("1,234", "1234", "$1,234"):
        assert x01_verify_extraction(b, [found(value=value)]).checked == 1


def test_ac_1_3b_a_value_combined_from_two_figures_fails():
    """AC-1.3b — ★ RA-132's forbidden half, and it is the scar.

    ⚠ *Cumulative-vs-discrete is the single most expensive extraction error this
    project has actually made* — ARM Q3 at 2.76×, MU's TTM at 71 %. `1234 − 1100
    = 134` is arithmetically derivable from the span and is **D-02's**, so X-01
    must refuse it.
    """
    quote = ("Revenue was $1,234 thousand for the quarter, against $1,100 thousand "
             "a year earlier")
    with pytest.raises(ValueNotInSpanError, match="assembled from two places"):
        x01_verify_extraction(bundle(), [found(value="134", quote=quote,
                                               offset=span_of(quote))])


def test_x01_does_not_rescale_a_value_against_its_own_unit():
    """RA-132 — ⚠ **no scaling.** The envelope returns the value *in the
    document's own units* with the unit beside it; rescaling here would let a
    value disagree with its declared unit and still pass."""
    with pytest.raises(ValueNotInSpanError):
        x01_verify_extraction(bundle(), [found(value="1234000", unit="USD")])


def test_x01_tolerates_whitespace_and_nothing_else():
    """⚠ A filing arrives through PDF/HTML extraction, so a run of spaces is a
    transport artifact. **A changed digit, word or punctuation mark is not.**"""
    b = bundle()
    quote = "Revenue was $1,234 thousand for the quarter"
    reflowed = found(quote="Revenue  was  $1,234\nthousand for the quarter",
                     offset=span_of(quote))
    assert x01_verify_extraction(b, [reflowed]).checked == 1

    with pytest.raises(SpanMismatchError):
        x01_verify_extraction(b, [found(quote="Revenue was $1,234 thousand for a quarter",
                                        offset=span_of(quote))])


def test_not_found_is_a_correct_answer_and_is_not_verified():
    """§3.0 / MP-7 — *`not_found` is a correct answer*, and verifying it would
    demand a span for a value that does not exist."""
    report = x01_verify_extraction(bundle(), [not_found("seg.assets",
                                                        note="no segment table in the 10-Q")])
    assert report.not_found == 1 and report.checked == 0


def test_a_bare_not_found_is_refused():
    """MP-7 — *an LLM with no stated way to say "I could not" will always find
    something to say*, and a bare not_found is indistinguishable from a step that
    never ran."""
    with pytest.raises(ValueError, match="where you looked"):
        not_found("seg.assets", note="")


def test_a_cumulative_ytd_figure_is_tagged_and_never_subtracted():
    """§3.0's scar paragraph — *do NOT subtract to produce the discrete quarter.
    That subtraction is arithmetic and belongs to D-02.*"""
    it = found(cumulative_ytd=True)
    assert it.is_cumulative_ytd
    assert x01_verify_extraction(bundle(), [it]).checked == 1, "tagged, still verified"


def test_a_period_carries_start_and_end_where_the_document_gives_both():
    """§5.1's argument in the extraction layer — *EDGAR wins for TTM because its
    facts carry explicit period start AND end, so a discrete quarter is
    distinguishable from a cumulative one by arithmetic.*"""
    assert found().period.is_bounded
    assert not found(period_start=None).period.is_bounded


# --------------------------------------------------------------------------- #
# AC-1.5 / AC-1.5a — X-02
# --------------------------------------------------------------------------- #

def fact_claim(**kw):
    quote = kw.pop("quote", "Revenue was $1,234 thousand for the quarter")
    span = kw.pop("span", _DERIVE)
    return Claim(ordinal=kw.pop("ordinal", 1), kind=FACT,
                 text=kw.pop("text", "Revenue was $1.234m."),
                 span=EvidenceSpan("0000-1", *span_of(quote)) if span is _DERIVE else span,
                 quote=quote)


def test_ac_1_5_a_factual_claim_with_no_evidence_span_raises():
    """AC-1.5 — RA-9, INV-004. ★ B4.2's done-when, second clause.

    *If you cannot quote it, it is not a fact. An uncited factual claim is a
    defect, not a style choice. It fails the run.*
    """
    with pytest.raises(UncitedClaimError, match="not a fact"):
        Claim(ordinal=1, kind=FACT, text="Revenue grew.")
    with pytest.raises(UncitedClaimError):
        Claim(ordinal=1, kind=FACT, text="Revenue grew.",
              span=EvidenceSpan("0000-1", 0, 5), quote="")


def test_ac_1_5_every_factual_claim_carries_a_RESOLVABLE_span():
    """★ The done-when says **resolvable**, not merely present — so the bundle is
    passed and every fact's span is resolved against it."""
    ok = ClaimSet((fact_claim(),))
    assert x02_verify_claims(ok, bundle()).facts == 1

    mis = ClaimSet((fact_claim(quote="Revenue was $9,999 thousand for the quarter",
                               span=EvidenceSpan("0000-1", *span_of(
                                   "Revenue was $1,234 thousand for the quarter"))),))
    with pytest.raises(SpanMismatchError):
        x02_verify_claims(mis, bundle())


def test_ac_1_5a_an_assumption_is_a_claim_with_an_ordinal():
    """AC-1.5a — ★★ **RA-9 amended, RA-133**, the second defect this slice found.

    ⚠ The enum admitted `{fact, inference}` while **S-3 instructs the model that
    there are exactly THREE kinds** and names ASSUMPTION as the third. The prompt
    asked for a shape the contract could not hold.
    """
    from src.fundamental import KINDS
    assert KINDS == (FACT, INFERENCE, ASSUMPTION)

    claims = ClaimSet((
        fact_claim(ordinal=1),
        Claim(ordinal=2, kind=ASSUMPTION, text="Cycle trough passed in FY2025."),
        Claim(ordinal=3, kind=INFERENCE, text="Margins should recover.", rests_on=(1, 2)),
    ))
    report = x02_verify_claims(claims, bundle())
    assert (report.facts, report.assumptions, report.inferences) == (1, 1, 1)

    # ★ RA-133 — assumptions[] is a PROJECTION, and the ordinal survives.
    assert claims.assumptions[0].ordinal == 2
    assert claims.to_json_obj()["assumptions"] == [
        {"ordinal": 2, "text": "Cycle trough passed in FY2025."}]


def test_an_assumption_carrying_a_span_is_refused():
    """S-3 — *an assumption is something the bundle does not contain*; with a span
    it is a fact."""
    with pytest.raises(ValueError, match="it is a fact"):
        Claim(ordinal=1, kind=ASSUMPTION, text="Cycle turned.",
              span=EvidenceSpan("0000-1", 0, 5), quote="MICRON")


def test_an_inference_resting_on_nothing_is_refused():
    """S-3 — *an inference resting on nothing is an ASSUMPTION; label it as one.*

    ⚠ Mislabelling hides a supplied belief inside a derived one.
    """
    with pytest.raises(ValueError, match="label it as one"):
        Claim(ordinal=2, kind=INFERENCE, text="Margins recover.")


def test_an_inference_citing_a_missing_ordinal_is_uncited_by_a_longer_route():
    """S-3 — *carries the ordinals of the facts it rests on*, and they must exist."""
    claims = ClaimSet((fact_claim(ordinal=1),
                       Claim(ordinal=2, kind=INFERENCE, text="…", rests_on=(1, 9))))
    with pytest.raises(UncitedClaimError, match="which no claim carries"):
        x02_verify_claims(claims, bundle())


def test_duplicate_claim_ordinals_are_refused():
    """S-3's inferences cite ordinals, so a duplicate makes `rests_on` ambiguous."""
    with pytest.raises(ValueError, match="duplicate claim ordinals"):
        ClaimSet((fact_claim(ordinal=1), fact_claim(ordinal=1)))


# --------------------------------------------------------------------------- #
# AC-1.4 — extraction and judgement are separate
# --------------------------------------------------------------------------- #

def test_ac_1_4_a_judgement_block_cannot_be_run_as_an_extraction():
    """AC-1.4 — RA-5.

    ★ *A prompt that asks "summarise the filing and tell me if it's a good
    business" makes the verifiable half unverifiable.* Checked on the declared
    `kind`, not on the id: `E-` is a naming convention and `kind` is the fact.
    """
    assert_extraction_block(block("E-01", "v1", "extraction", "Extract segments."))
    with pytest.raises(ExtractionKindError, match="separate calls"):
        assert_extraction_block(block("E-99", "v1", "judgement", "Is it a good business?"))


def test_ac_1_4_an_extraction_block_reads_the_full_bundle():
    """§1.1 — every E-block is `view: full`. ⚠ A blind extraction would read a
    document with its numbers withheld."""
    with pytest.raises(ExtractionKindError, match="full bundle"):
        assert_extraction_block(
            block("E-01", "v1", "extraction", "Extract segments.", view="blind"))


def test_the_registry_can_hold_both_kinds_and_tell_them_apart():
    """RA-5 at the registry level — the split is declared, not inferred."""
    reg = PromptRegistry([
        block("E-01", "v1", "extraction", "Extract segments."),
        block("J-03", "v1", "judgement", "Assess the moat.", view="blind"),
    ])
    assert reg.get("E-01", "v1").kind == "extraction"
    assert reg.get("J-03", "v1").kind == "judgement"


# --------------------------------------------------------------------------- #
# The done-when's load-bearing clause
# --------------------------------------------------------------------------- #

def test_x01_and_x02_ask_no_llm_anything():
    """★★ B4.2's done-when: *"without an LLM being asked"*.

    ```
    FIVE OF SEVEN VERIFICATION STEPS ARE NOT PROMPTS. THAT IS THE POINT.

    A checker built from the same stochastic process it is checking inherits
    its blind spots; an LLM asked "does this number appear in this span" is
    strictly worse than `in`.
    ```

    Checked structurally: the verification module imports nothing that could
    reach a model, and every test above ran without constructing a gateway.
    """
    source = Path("src/fundamental/claims/verify.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
    assert not any("llm" in m or "gateway" in m or "anthropic" in m for m in imported), \
        f"X-01/X-02 reached for a model: {sorted(imported)}"
    assert "prompts" not in " ".join(imported), "and it composes no prompt either"


def test_evidence_ids_count_extracted_items_not_documents():
    """★ **BS-26's whole argument, and RA-66's defect.**

    *A 10-K that is present but from which the required number could not be
    pulled is not evidence.* ⚠ Build rubrics before extraction and their
    `evidence_required` lists name **documents** — which is why B4.2 ships
    before B4.3.
    """
    result = ExtractionResult(
        block_id="E-01", bundle_hash="sha256:x",
        items=(found(evidence_id="seg.revenue"),
               not_found("seg.assets", note="no segment table")),
    )
    assert result.evidence_ids == frozenset({"seg.revenue"})
    assert "seg.assets" not in result.evidence_ids, "presence is not extraction (RA-66)"


def test_two_items_with_one_identity_are_ambiguous_evidence():
    """MP-18 (was: MP-4 / RA-65 "double-count").

    ✏ Renamed 2026-09-07. The BEHAVIOUR is unchanged — two items sharing an
    identity still raise — but the old name asserted a reason that is not what
    the code does. ⚠ `evidence_ids` is a frozenset and `coverage()` is
    `len(matched)/len(required)` over frozensets, so a duplicate CANNOT
    double-count. ★ The real hazard is ambiguity: nothing says which of the two
    a rubric level cites.
    """
    with pytest.raises(ValueError, match="ambiguous"):
        ExtractionResult(block_id="E-01", bundle_hash="sha256:x",
                         items=(found(), found()))


def test_mp_18_one_evidence_id_per_segment_is_legal_and_distinguished():
    """★★ MP-18 — the case that forced the rule. E-01 returns ONE ITEM PER
    SEGMENT and every one is legitimately `seg.revenue`.

    ⚠ Under the old rule E-01 could not emit a segment table at all.
    """
    r = ExtractionResult(block_id="E-01", bundle_hash="sha256:x", items=(
        found(value="5,069", qualifier="CNBU"),
        found(value="1,451", qualifier="SBU"),
        found(value="1,551", qualifier="MBU"),
    ))
    assert len(r.items) == 3
    # ★ The rubric still matches on the BARE id — b43_v1 maps segments ->
    #   "seg.revenue", and score.py does set membership. A suffix would break it.
    assert r.evidence_ids == frozenset({"seg.revenue"})


def test_mp_18_the_qualifier_may_not_be_smuggled_into_the_evidence_id():
    """⚠ `seg.revenue.CNBU` makes the rubric level unavailable for a NAMING
    reason rather than an evidential one — the wiring bug b43_v1's own comment
    warns about."""
    from src.fundamental.scorecard.rubrics.b43_v1 import E
    r = ExtractionResult(block_id="E-01", bundle_hash="sha256:x", items=(
        found(evidence_id="seg.revenue.CNBU", qualifier=""),
    ))
    assert E["segments"] not in r.evidence_ids, (
        "a suffixed id no longer matches the published rubric dimension"
    )


def test_the_thirteen_deep_e_blocks_are_declared():
    """§1.1 — E-01…E-13 on the deep tier; E-14/E-15 are the cheap exceptions."""
    assert tuple(f"E-{n:02d}" for n in range(1, 14)) == E_BLOCK_IDS
    from src.fundamental import CHEAP_E_BLOCKS
    assert set(CHEAP_E_BLOCKS).isdisjoint(E_BLOCK_IDS)


def test_mp_18_same_id_same_qualifier_different_period_is_the_discrete_vs_ytd_pair():
    """★★ MP-18's `period` component, and why it is load-bearing.

    F5 golden cases 1 and 2 pin the SAME segment row from the two adjacent
    columns of MU's FY2025 Q3 segment table: the discrete quarter and the
    nine-month cumulative. They share `evidence_id` AND `qualifier` and differ
    only by `period`.

    ⚠⚠ Under the pre-MP-18 rule (bare `evidence_id`) this pair was impossible.
    Under a `(evidence_id, qualifier)` identity it is STILL impossible. If
    someone ever "simplifies" identity by dropping `period`, this test is what
    says so — and the cumulative-vs-discrete pair is the project's most
    expensive measured error class (ARM Q3 2.76x, MU TTM 71%).
    """
    discrete = found(value="5,069", qualifier="CNBU",
                     period_start="2025-02-28", period_end="2025-05-29")
    cumulative = found(value="14,028", qualifier="CNBU", cumulative_ytd=True,
                       period_start="2024-08-30", period_end="2025-05-29")

    result = ExtractionResult(block_id="E-01", bundle_hash="sha256:x",
                              items=(discrete, cumulative))
    assert len(result.items) == 2

    # ★ A rubric still sees ONE bare id — b43_v1 maps segments -> "seg.revenue".
    assert result.evidence_ids == frozenset({"seg.revenue"})

    # ⚠ The tag drives "do not subtract" (D-02 owns that arithmetic, not E-01).
    assert not discrete.is_cumulative_ytd
    assert cumulative.is_cumulative_ytd

    # ⚠⚠ The two differ ONLY by period — drop it from identity and they collide.
    assert discrete.identity != cumulative.identity
    assert (discrete.evidence_id, discrete.qualifier) == \
           (cumulative.evidence_id, cumulative.qualifier), (
        "if these ever differ by id or qualifier the test has drifted off the "
        "case it was written for, and stops guarding the period component"
    )


def test_mp_18_the_qualifier_survives_serialisation():
    """⚠⚠ MP-18 — identity that does not survive `to_json_obj()` is not identity.

    The recorded payload a golden case replays against (F2 CT-2.2) is the
    SERIALISED form. If `qualifier` is missing there, two segment rows are
    indistinguishable on the wire and F5 cases 1 and 2 cannot be told apart —
    however correct the in-memory dataclass is.
    """
    cnbu = found(value="5,069", qualifier="CNBU").to_json_obj()
    sbu = found(value="1,451", qualifier="SBU").to_json_obj()
    assert cnbu["qualifier"] == "CNBU"
    assert cnbu != sbu
    assert set(found().to_json_obj()) >= {
        "evidence_id", "value", "unit", "period", "quote", "span",
        "status", "tags", "note", "qualifier",
    }, "a golden case's `expected` is written against this exact key set"


def test_x01_accepts_a_value_differing_only_by_curly_quotes():
    """⚠ MEASURED 2026-09-07 — the model returned straight quotes against a
    fixture whose curly quotes came from OUR OWN html.unescape. Failing that
    tests the converter, not the model."""
    from src.fundamental.claims.verify import _assert_value_in_quote
    quote = 'Compute and Networking Business Unit (“CNBU”): Includes memory'
    _assert_value_in_quote(found(
        value='Compute and Networking Business Unit ("CNBU")', quote=quote,
        offset=(0, len(quote)),
    ))  # must not raise


def test_x01_still_refuses_a_fabricated_value_after_typographic_normalisation():
    """★★ The guard must keep its teeth. ⚠ Normalising punctuation must not
    become "is it close?" — a different word, a different number, or a value
    assembled from two places still raises."""
    from src.fundamental.errors import ValueNotInSpanError
    from src.fundamental.claims.verify import _assert_value_in_quote
    quote = 'Compute and Networking Business Unit (“CNBU”): Includes memory'
    for bogus in ['Storage Business Unit ("SBU")',
                  'Compute and Networking Business Unit ("CNBU") and Storage',
                  '9,999']:
        with pytest.raises(ValueNotInSpanError):
            _assert_value_in_quote(found(value=bogus, quote=quote,
                                         offset=(0, len(quote))))
