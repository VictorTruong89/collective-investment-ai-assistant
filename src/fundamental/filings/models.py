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
        }


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """One E-block's output over one bundle."""

    block_id: str
    bundle_hash: str
    items: tuple[ExtractedItem, ...]

    def __post_init__(self) -> None:
        ids = [i.evidence_id for i in self.items]
        if len(set(ids)) != len(ids):
            raise ValueError(
                f"{self.block_id}: duplicate evidence_id(s) in one extraction. "
                f"`evidence_coverage` counts ids, so a duplicate double-counts a "
                f"rubric level's support (MP-4, RA-65)"
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
