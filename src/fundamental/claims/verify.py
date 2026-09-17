"""★ X-01 and X-02 — DETERMINISTIC verification. No LLM is asked anything here.

```
FIVE OF SEVEN VERIFICATION STEPS ARE NOT PROMPTS. THAT IS THE POINT.

A checker built from the same stochastic process it is checking inherits its
blind spots; an LLM asked "does this number appear in this span" is strictly
worse than `in`.
```

★★ **RA-131 — X-01 has two halves, and only the second is usually implemented:**

```
   ①  the QUOTE must equal the document's own text at the cited offsets
   ②  the VALUE must appear in the QUOTE

   Checking only ② VERIFIES THE MODEL AGAINST ITSELF. A model that fabricates
   the quote and the value consistently passes, and the citation is fiction
   with a character range attached.

   THE OFFSET IS THE ONLY PART OF A CITATION THE MODEL CANNOT ALSO AUTHOR.
```

⚠ **RA-132 bounds ②.** "Arithmetically derivable" means **reformatting one
stated figure**, never combining two — the second is D-02's, and it is the
`_cumulative_fys` scar (ARM 2.76×, MU 71 %).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from src.fundamental.claims.models import ASSUMPTION, FACT, INFERENCE, Claim, ClaimSet
from src.fundamental.claims.classification import (
    assert_declared_value,
    is_classification,
)
from src.fundamental.errors import (
    SpanMismatchError,
    UncitedClaimError,
    ValueNotInSpanError,
)

#: Number-shaped tokens in a span: optional sign or parenthesis, digits with
#: separators, optional decimals, optional trailing percent.
_NUMBER = re.compile(r"\(?-?[\d][\d,  _]*(?:\.\d+)?\)?%?")

#: Characters that are FORMATTING, not value (RA-132). ⚠ Scale words —
#: "thousand", "million" — are deliberately absent: the envelope says the value
#: is returned *"in the document's own units"* with a separate `unit` field, so
#: rescaling here would let a value disagree with its own declared unit and pass.
_FORMAT_CHARS = str.maketrans(dict.fromkeys(",_\xa0\u202f$€£¥ %", ""))


@dataclass(frozen=True, slots=True)
class VerificationReport:
    """What X-01/X-02 found. ★ A count, not a boolean.

    **RM-10** is the *citation validity rate*, and it needs the denominator —
    "all claims passed" and "there was one claim and it passed" are different
    findings.
    """

    checked: int
    facts: int
    inferences: int
    assumptions: int
    not_found: int

    @property
    def all_passed(self) -> bool:
        """True by construction — the checks raise, so reaching here IS the pass.

        ⚠ Deliberate: a report carrying `passed: False` would let a caller forget
        one `if`, which is the return-value failure mode L4 §5.1 rejects outright.
        """
        return True

    def to_json_obj(self) -> dict:
        return {"checked": self.checked, "facts": self.facts,
                "inferences": self.inferences, "assumptions": self.assumptions,
                "not_found": self.not_found}


# --------------------------------------------------------------------------- #
# X-01 — extracted value present in cited span
# --------------------------------------------------------------------------- #

def x01_verify_extraction(bundle, items) -> VerificationReport:
    """★ AC-1.3 / AC-1.3a / AC-1.3b — RA-6, RA-131, RA-132.

    ⚠ **`not_found` is a correct answer** and is not verified: *"an item you
    cannot find is returned with status `not_found`… `not_found` is a correct
    answer"* (the extraction envelope, MP-7). Verifying it would demand a span
    for a value that does not exist.
    """
    checked = not_found = 0
    for item in items:
        if item.status == "not_found":
            not_found += 1
            continue
        _assert_quote_matches_document(bundle, item)      # ① RA-131
        # ✏ `DX-122` — ② asks the value to appear in its quote. For a CLASSIFICATION item
        #   (`cx.status`) the value is a label the document does not carry, so ② is replaced
        #   by its declared closed set. ⚠ ① is never relaxed.
        if is_classification(item.evidence_id):
            assert_declared_value(item.evidence_id, item.value)
        else:
            _assert_value_in_quote(item)                  # ② RA-6, RA-132
        checked += 1
    return VerificationReport(checked=checked, facts=checked, inferences=0,
                              assumptions=0, not_found=not_found)


def _assert_quote_matches_document(bundle, item) -> None:
    """★ X-01 ①. The half that makes the citation checkable at all."""
    actual = item.span.resolve(bundle)
    if _collapse_whitespace(actual) != _collapse_whitespace(item.quote):
        raise SpanMismatchError(item.evidence_id, item.quote, actual)


def _assert_value_in_quote(item) -> None:
    """★ X-01 ②, bounded by RA-132.

    Three chances, in order of strictness, and **no fourth**:
      1. the value appears literally in the quote;
      2. the value, normalised as a number, equals a number token in the quote;
      3. otherwise it raises.

    ⚠ There is deliberately no *"is it close?"* and no *"can it be derived?"*
    step. Read the other way, X-01 accepts anything a determined reader can
    construct, which is no check at all.
    """
    value = str(item.value)
    if value in item.quote:
        return
    # ⚠⚠ Typographic normalisation — added 2026-09-07 from a MEASURED failure,
    # and deliberately narrow. The model returned
    #     'Compute and Networking Business Unit ("CNBU")'
    # against a document reading `(“CNBU”)`. The value IS in the document; only
    # the quote characters differ.
    #
    # ★★ The curly quotes are an artefact of OUR OWN pipeline: the filing
    # fixture was converted from HTML and `&#8220;` was unescaped into `“`.
    # Failing an extraction over punctuation we introduced ourselves tests the
    # converter, not the model.
    #
    # ★ This is the same CATEGORY as `_assert_span_resolves`'s existing
    # whitespace collapse — rendering-level equivalence, not "is it close?".
    # ⚠ It adds no tolerance for a different WORD, a different NUMBER, or a
    # value assembled from two places; `test_x01_still_refuses_a_fabricated_
    # value_after_typographic_normalisation` pins that.
    if _normalise_typography(value) in _normalise_typography(item.quote):
        return
    wanted = _as_number(value)
    if wanted is not None:
        for token in _NUMBER.findall(item.quote):
            if _as_number(token) == wanted:
                return
    raise ValueNotInSpanError(item.evidence_id, value, item.quote)


#: Characters that differ only by RENDERING. ⚠ Nothing semantic belongs here.
_TYPOGRAPHY = str.maketrans({
    "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
    "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u00a0": " ",
})


def _normalise_typography(text: str) -> str:
    """Curly quotes, dashes and non-breaking spaces → their ASCII forms."""
    return text.translate(_TYPOGRAPHY)


def _as_number(text: str) -> Decimal | None:
    """Normalise ONE stated figure — RA-132's whole permitted set.

    `"1,234"` → `1234`; `"(500)"` → `-500`; `"12.5%"` → `12.5`. ⚠ **No scaling**:
    `"1,234"` with `unit="thousands of USD"` stays `1234`, because the envelope
    returns the value *in the document's own units* and the unit travels beside
    it. Rescaling here would let a value disagree with its own declared unit and
    still pass.
    """
    cleaned = text.strip().translate(_FORMAT_CHARS)
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()")
    if not cleaned:
        return None
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None
    return -value if negative else value


def _collapse_whitespace(text: str) -> str:
    """Whitespace-insensitive comparison — and ONLY whitespace.

    ⚠ A filing's text arrives through PDF and HTML extraction, so a run of
    spaces or a newline where the document had a line break is a transport
    artifact rather than a mis-citation. **Nothing else is normalised**: a
    changed digit, word or punctuation mark is a real disagreement.
    """
    return " ".join(text.split())


# --------------------------------------------------------------------------- #
# X-02 — every factual claim carries a span
# --------------------------------------------------------------------------- #

def x02_verify_claims(claim_set: ClaimSet, bundle=None) -> VerificationReport:
    """★ AC-1.5 / AC-1.5a — RA-9, RA-133, INV-004. A deterministic SCHEMA check.

    `bundle` is optional: supplied, every fact's span is also **resolved**, which
    turns *"carries a span"* into *"carries a span that points at something"*.
    ⚠ The done-when says **resolvable**, so a caller that omits the bundle has
    performed the weaker check and the report cannot tell them apart — which is
    why the parameter is named rather than inferred.
    """
    facts = inferences = assumptions = 0
    for claim in claim_set.claims:
        if claim.kind == FACT:
            if claim.span is None or not claim.quote:
                raise UncitedClaimError(claim.ordinal, claim.text)
            if bundle is not None:
                actual = claim.span.resolve(bundle)
                if _collapse_whitespace(actual) != _collapse_whitespace(claim.quote):
                    raise SpanMismatchError(
                        f"claim {claim.ordinal}", claim.quote, actual)
            facts += 1
        elif claim.kind == INFERENCE:
            _assert_rests_on_resolves(claim_set, claim)
            inferences += 1
        elif claim.kind == ASSUMPTION:
            assumptions += 1
    return VerificationReport(checked=len(claim_set.claims), facts=facts,
                              inferences=inferences, assumptions=assumptions,
                              not_found=0)


def _assert_rests_on_resolves(claim_set: ClaimSet, claim: Claim) -> None:
    """S-3 — *"carries the ordinals of the facts it rests on"*, and they must exist.

    ⚠ An inference citing an ordinal nothing carries is uncited by a longer
    route: the reader follows the reference, finds nothing, and has no way to
    tell that from a numbering slip.
    """
    for ordinal in claim.rests_on:
        try:
            claim_set.by_ordinal(ordinal)
        except KeyError:
            raise UncitedClaimError(
                claim.ordinal,
                f"{claim.text} — rests on ordinal {ordinal}, which no claim carries",
            ) from None
