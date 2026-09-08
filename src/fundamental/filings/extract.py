"""The E-block runner — extraction, kept separate from judgement (RA-5, AC-1.4).

```
                    EXTRACTION              JUDGEMENT
   Question    what does this document say?  is this a good business?
   Ground truth       EXISTS — in the document      does not exist
   Verifiable         YES — the answer is in the bundle    no
   Right guard   ASSERT AGAINST THE SOURCE   measure variance, bound, disclose
   Failure mode  hallucination — a fact not in the source   inconsistency, bias
```

★ **RA-5 is what makes hallucination a *detectable class* rather than a general
anxiety.** *A prompt that asks "summarise the filing and tell me if it's a good
business" makes the verifiable half unverifiable.*

⚠ **RA-7: judgement calls consume EXTRACTION OUTPUTS, never raw documents.**
Reversed, the verifiable half becomes unverifiable — which is why §4A.2 puts
step 2 before step 4 and step 3 between them.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.fundamental.claims.models import EvidenceSpan
from src.fundamental.claims.verify import VerificationReport, x01_verify_extraction
from src.fundamental.errors import ExtractionKindError
from src.fundamental.filings.models import (
    CUMULATIVE_YTD,
    FOUND,
    NOT_FOUND,
    ExtractedItem,
    ExtractionResult,
    Period,
)
from src.fundamental.prompts.registry import PromptBlock

#: §1.1's registry. ★ **Every E-block is `view: full` and `tier: deep`** — and
#: the second is not an oversight: extraction is nominally "extraction" but is
#: *low-frequency (the filing-aware cache) and quality-critical*, so INV-8's
#: cost-and-value test puts it on the deep tier alongside judgement.
#:
#: ⚠ E-14 and E-15 are the two cheap-tier exceptions (news triage, sector-file
#: ingest) and are **not** part of WF-1's step 2.
E_BLOCK_IDS = tuple(f"E-{n:02d}" for n in range(1, 14))
CHEAP_E_BLOCKS = ("E-14", "E-15")


@dataclass(frozen=True, slots=True)
class ExtractionPass:
    """Step 2 + step 3 of §4A.2, which are inseparable in practice.

    ★ **Step 3 is a deterministic ABORT.** *An unverified fact entering a
    judgement is a hallucination with a scorecard built on it* — so verification
    is not a later stage that a caller might skip, it is the same call.
    """

    results: tuple[ExtractionResult, ...]
    report: VerificationReport

    @property
    def evidence_ids(self) -> frozenset:
        """The union a rubric level's `evidence_required` may cite (RA-32, RA-65)."""
        return frozenset().union(*(r.evidence_ids for r in self.results)) \
            if self.results else frozenset()

    def to_json_obj(self) -> dict:
        return {"results": [r.to_json_obj() for r in self.results],
                "verification": self.report.to_json_obj()}


def assert_extraction_block(block: PromptBlock) -> PromptBlock:
    """RA-5 / AC-1.4 — an E-block is an extraction block, and the registry knows.

    ★ Checked at the call site rather than trusted from the id: `E-` is a naming
    convention, and `kind` is the declared fact. A block named `E-99` that
    declares `judgement` would otherwise be run through the extraction path and
    verified with X-01, which measures nothing about a judgement.
    """
    if block.kind != "extraction":
        raise ExtractionKindError(
            f"block {block.name!r} declares kind={block.kind!r} and was run as an "
            f"extraction. Extraction and judgement are separate calls with separate "
            f"prompts — mixing them makes the verifiable half unverifiable (RA-5)"
        )
    if block.view != "full":
        raise ExtractionKindError(
            f"block {block.name!r} declares view={block.view!r}; every E-block reads "
            f"the full bundle (§1.1). A blind extraction would read a document with "
            f"its numbers withheld"
        )
    return block


def run_extraction(seam, *, block_ids, bundle, run_id: str,
                   parse) -> ExtractionPass:
    """Run the E-blocks over one bundle, then verify — steps 2 and 3.

    `parse` maps a raw response to `list[ExtractedItem]`; it is injected because
    **the response shape is the API's contract, not this module's** (MP-5:
    *output shape is enforced by the API, not by prose* — extraction calls use
    tool use with `strict: true`).

    ⚠ **RA-107: calls within a stage may run in any order or concurrently.** This
    runs them in the order given, which is a valid schedule — *"no conversational
    state" makes every call in a stage independent by construction*, so nothing
    here depends on the ordering and a concurrent runner is a drop-in.
    """
    results = []
    for block_id, version in block_ids:
        block = assert_extraction_block(seam._registry.get(block_id, version))
        call = seam.call(prompt_name=block.name, prompt_version=block.version,
                         bundle=bundle, run_id=run_id, step=f"extract:{block.name}")
        results.append(ExtractionResult(
            block_id=block.name, bundle_hash=bundle.bundle_hash,
            items=tuple(parse(call)),
        ))

    # ★ Step 3 — deterministic, and it ABORTS. No LLM is asked anything.
    report = x01_verify_extraction(bundle, [i for r in results for i in r.items])
    return ExtractionPass(results=tuple(results), report=report)


# --------------------------------------------------------------------------- #
# Item construction — the envelope's shape, checked at the boundary
# --------------------------------------------------------------------------- #

def item(evidence_id: str, *, value: str, unit: str, quote: str,
         accession_id: str, offset, period_end: str | None = None,
         period_start: str | None = None, cumulative_ytd: bool = False,
         note: str = "", qualifier: str = "") -> ExtractedItem:
    """Build a found item from the envelope's seven fields.

    ★ `qualifier` (`MP-18`) names WHICH ROW when one `evidence_id` legitimately
    yields several — the segment for `E-01`. ⚠ It is not part of the id.
    """
    start, end = offset
    return ExtractedItem(
        evidence_id=evidence_id, value=value, unit=unit,
        period=Period(period_start, period_end) if period_end else None,
        quote=quote, span=EvidenceSpan(accession_id, int(start), int(end)),
        status=FOUND, tags=(CUMULATIVE_YTD,) if cumulative_ytd else (), note=note,
        qualifier=qualifier,
    )


def not_found(evidence_id: str, *, note: str) -> ExtractedItem:
    """★ *`not_found` is a correct answer* (§3.0, MP-7).

    ⚠ *A value that is "roughly" in the document, or that you assembled from two
    places, is not.* The note is required: a bare `not_found` is
    indistinguishable from a step that never ran.
    """
    return ExtractedItem(evidence_id=evidence_id, value="", unit="", period=None,
                         quote="", span=None, status=NOT_FOUND, note=note)
