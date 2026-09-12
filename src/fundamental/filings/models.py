"""Extraction output — the shared envelope's item shape (§3.0, MP-4).

```
For every item you return:
  evidence_id    the id given in the item list below — never invent one
  value          exactly as the document states it, in the document's own units
  unit           the units, verbatim ("thousands of USD", "%", "shares")
  period         the period the figure covers, with start AND end where the
                 document gives both
  quote          a verbatim span from the document containing the value
  accession_id   the document the span came from
  offset         [start, end] character offsets of the quote within that document
```

★ **MP-4: every extraction has a stable `evidence_id`.** Rubric
`evidence_required` lists (RA-32) cite those ids and `evidence_coverage` (RA-65)
counts them — *an extraction with no id cannot be counted, so it cannot support
a rubric level.* That is **BS-26**'s whole argument for building this before the
scorecard: build rubrics against a system with no extraction and their
`evidence_required` lists will name **documents**, which is precisely RA-66's
defect — *"a 10-K that is present but from which the required number could not be
pulled is not evidence."*
"""

from __future__ import annotations

from dataclasses import dataclass

from src.fundamental.claims.models import EvidenceSpan

FOUND, NOT_FOUND = "found", "not_found"
STATUSES = (FOUND, NOT_FOUND)

#: ★ The scar tag. *"If the document gives a cumulative year-to-date figure where
#: a discrete quarterly figure was requested, return it tagged `cumulative_ytd`
#: with both period endpoints, and do NOT subtract to produce the discrete
#: quarter."* Cumulative-vs-discrete is **the single most expensive extraction
#: error this project has actually made** — ARM Q3 at 2.76×, MU's TTM at 71 %.
CUMULATIVE_YTD = "cumulative_ytd"


@dataclass(frozen=True, slots=True)
class Period:
    """The span a figure covers, **with start AND end where the document gives both**.

    ⚠ That is §5.1's whole argument arriving in the extraction layer: EDGAR wins
    for TTM *because its facts carry explicit period start and end, so a discrete
    quarter is distinguishable from a cumulative one by arithmetic*. An extractor
    that returns only an end date reintroduces FMP's guess inside D-01.
    """

    start: str | None
    end: str

    def __post_init__(self) -> None:
        if not self.end:
            raise ValueError("a period with no end covers nothing")

    @property
    def is_bounded(self) -> bool:
        return self.start is not None

    def to_json_obj(self) -> dict:
        return {"start": self.start, "end": self.end}


@dataclass(frozen=True, slots=True)
class ExtractedItem:
    """One item from one E-block. ★ Verified by X-01 before anything judges on it."""

    evidence_id: str
    value: str
    unit: str
    period: Period | None
    quote: str
    span: EvidenceSpan | None
    status: str = FOUND
    tags: tuple[str, ...] = ()
    note: str = ""
    #: `MP-18` — which ROW this item is, when one `evidence_id` legitimately
    #: yields several: the segment name for `E-01`, and `""` everywhere else.
    #: ⚠ It does NOT go in the `evidence_id`: `b43_v1.py` maps the published
    #: rubric dimension `segments → "seg.revenue"` and `score.py` matches by set
    #: membership on bare ids, so `seg.revenue.CNBU` would make the level
    #: unavailable for a *naming* reason rather than an evidential one.
    qualifier: str = ""

    @property
    def is_figure(self) -> bool:
        """Is this item's value a stated NUMBER?

        ⚠ Deliberately simpler than `verify._as_number`, which converts to
        `Decimal` for comparison. Here only the question *"is this a
        measurement or a narrative?"* is being asked, and duplicating the
        conversion would give two places to disagree about what a number is.
        """
        cleaned = self.value.strip().strip("()").replace(",", "").rstrip("%")
        cleaned = cleaned.lstrip("$£€¥").replace(".", "", 1).lstrip("-")
        return cleaned.isdigit()

    @property
    def identity(self) -> tuple:
        """`MP-18` — what must be unique within one `ExtractionResult`.

        ★ Mirrors `withdraw_extractions`, which already keys on
        `(evidence_id, period)` (`RA-138`).

        ⚠⚠ **`C14`, 2026-09-07 — a narrative item also carries its SPAN.**
        `MP-18` was derived from `seg.revenue` — numeric, per-segment,
        per-period — and over-fitted it. `E-01` also asks for *"**any**
        statement that the segmentation changed"*, and a real filing gave
        **three**, all `('seg.basis_note', '', period)`:

            "Business units reorganized effective Q4 2025…"
            "The changes will require us to recast our segment reporting…"
            "Certain reclassifications have been made to prior-period amounts…"

        ★ They are not duplicates. A rubric citing `seg.basis_note` wants them
        all, and `evidence_coverage` counts the id **once** either way — so
        there is no ambiguity to guard against, and refusing them lost real
        evidence.

        ⚠ **The guard is unchanged where it matters.** For a FIGURE the span is
        excluded, so two values claiming one `(id, qualifier, period)` still
        collide — *"nothing then says which one a rubric cites"* is exactly the
        numeric case, and it is still refused. Narrative items are
        distinguished by **where they were found**, which is the only thing
        that does distinguish them.
        """
        # ⚠ A TUPLE, not `period.to_json_obj()` — that returns a dict, which is
        # unhashable, and `__post_init__` puts these in a set.
        #
        # ⚠⚠ **`DX-68`, 2026-09-11 — `cumulative_ytd` joined the identity.**
        # The first run under the shared envelope (`DX-67`) returned
        # `period_start = None` on **65 of 65** items, so every quarterly row
        # collapsed onto its YTD twin: 20 duplicate identities, and the whole
        # result was refused.
        #
        # ★★★ The model was not misbehaving — it was obeying `S-2` item 3,
        # *"Do not compute … do not derive it yourself."* A segment table
        # states the period **END** (*"Thirteen weeks ended May 29, 2025"*);
        # the START has to be derived. **Every earlier recording carried a
        # `period_start` only because nothing had told the model not to compute
        # one**, and that derived field was masking a gap in this identity.
        #
        # ★★ `cumulative_ytd` is the fact the model RECORDS rather than
        # derives, and it separates the two rows exactly — 5,069 (quarter) from
        # 14,028 (YTD), same id, same qualifier, same end date. `AP-5`: a
        # derived quantity does not belong in an identity.
        base = (self.evidence_id, self.qualifier,
                (self.period.start, self.period.end) if self.period else None,
                bool(self.is_cumulative_ytd))
        if self.is_figure or self.span is None:
            return base
        return (*base, (self.span.accession_id, self.span.start, self.span.end))

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"status {self.status!r} is not one of {STATUSES}")
        if not self.evidence_id:
            raise ValueError(
                "an item with no evidence_id cannot be counted by evidence_coverage, "
                "so it cannot support a rubric level (MP-4, RA-65)"
            )
        if self.status == NOT_FOUND:
            # MP-7 / P5 — the stated failure output. *An LLM with no stated way to
            # say "I could not" will always find something to say.*
            if not self.note:
                raise ValueError(
                    f"{self.evidence_id}: not_found requires a one-line note on where "
                    f"you looked. A bare not_found is indistinguishable from a step "
                    f"that never ran (MP-7)"
                )
            return
        if self.span is None or not self.quote:
            raise ValueError(
                f"{self.evidence_id}: a found item needs a quote and a resolvable "
                f"span, or X-01 has nothing to check it against (RA-6, RA-131)"
            )

    @property
    def is_cumulative_ytd(self) -> bool:
        """⚠ True ⇒ **do not subtract**. The discrete quarter is D-02's arithmetic."""
        return CUMULATIVE_YTD in self.tags

    def to_json_obj(self) -> dict:
        return {
            "evidence_id": self.evidence_id, "value": self.value, "unit": self.unit,
            "period": self.period.to_json_obj() if self.period else None,
            "quote": self.quote,
            "span": self.span.to_json_obj() if self.span else None,
            "status": self.status, "tags": list(self.tags), "note": self.note,
            # ⚠⚠ MP-18. Omitting this made the discriminator invisible on the
            # WIRE: `qualifier` lived on the dataclass but never reached the
            # recorded payload, so two segment rows serialised identically and
            # a replayed golden case could not tell CNBU from SBU. ★ Identity
            # that does not survive serialisation is not identity.
            "qualifier": self.qualifier,
        }


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """One E-block's output over one bundle."""

    block_id: str
    bundle_hash: str
    items: tuple[ExtractedItem, ...]

    def __post_init__(self) -> None:
        # ✏ `MP-18` (2026-09-07) — identity is `(evidence_id, qualifier, period)`.
        # ⚠⚠ The previous rule banned a repeated `evidence_id` outright, and
        # `E-01` **cannot satisfy it**: it returns one item per reportable
        # segment and every one is legitimately `seg.revenue`.
        #
        # ⚠ Its stated reason was also wrong. It claimed a duplicate
        # "double-counts a rubric level's support", but `evidence_ids` is a
        # frozenset and `coverage()` is `len(matched) / len(required)` over
        # frozensets — duplicates collapse and cannot double-count. ★ The real
        # hazard is AMBIGUITY: two items claiming one identity with different
        # values, where nothing says which one a rubric cites. That is what is
        # banned below, and it is why `qualifier` distinguishes rather than
        # suppresses.
        seen = [i.identity for i in self.items]
        if len(set(seen)) != len(seen):
            raise ValueError(
                f"{self.block_id}: two items share one identity "
                f"(evidence_id, qualifier, period). ⚠ Nothing then says which "
                f"one a rubric level cites, so the evidence is ambiguous. If "
                f"these are different rows of one table (e.g. per-segment), set "
                f"`qualifier` — do NOT suffix the evidence_id (MP-18, MP-4)"
            )

    @property
    def found(self) -> tuple[ExtractedItem, ...]:
        return tuple(i for i in self.items if i.status == FOUND)

    @property
    def evidence_ids(self) -> frozenset:
        """★ What a rubric level's `evidence_required` cites, and what
        `evidence_coverage` counts — **successfully extracted items only**.

        ⚠ RA-66: *presence in the bundle is not extraction.* A `not_found` item
        is deliberately absent from this set, which is the whole difference
        between counting documents and counting pulled facts.
        """
        return frozenset(i.evidence_id for i in self.found)

    def to_json_obj(self) -> dict:
        return {"block_id": self.block_id, "bundle_hash": self.bundle_hash,
                "items": [i.to_json_obj() for i in self.items]}
