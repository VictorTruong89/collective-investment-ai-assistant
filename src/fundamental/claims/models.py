"""The citation spine — `Claim`, `EvidenceSpan` (RA-9, RA-133, S-3, INV-004).

```
Every sentence you write is one of exactly three kinds, and you tag each one:

  FACT       Stated in the bundle. Carries `evidence_id` and a verbatim quote
             of the supporting text. If you cannot quote it, it is not a fact.
  INFERENCE  Follows from one or more FACTs you have already stated. Carries
             the ordinals of the facts it rests on. An inference resting on
             nothing is an assumption; label it as one.
  ASSUMPTION Something you supplied that the bundle does not contain and does
             not imply. Permitted, and must be listed as an assumption so the
             reader can reject it independently of everything else.

An uncited factual claim is a defect, not a style choice. It fails the run.
```

★ **RA-9 was amended for this slice.** The enum read `{fact, inference}` while
S-3 instructs the model that there are exactly **three** kinds — so the prompt
asked for a shape the contract could not hold, and an ingest had to reject valid
output or coerce an assumption into an inference *that rests on stated facts,
which an assumption by definition does not*.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FACT, INFERENCE, ASSUMPTION = "fact", "inference", "assumption"
KINDS = (FACT, INFERENCE, ASSUMPTION)


@dataclass(frozen=True, slots=True)
class EvidenceSpan:
    """A resolvable pointer into one bundle document — `(accession_id, [start, end])`.

    ★ **RA-131: the offset is the only part of a citation the model cannot also
    author.** A `quote` is the model's *claim* about what the document says; the
    offset is a claim that can be checked against the document itself.
    """

    accession_id: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValueError(
                f"span [{self.start}, {self.end}] on {self.accession_id!r} is not a "
                f"range. An unresolvable offset makes the citation uncheckable, which "
                f"is the state RA-131 exists to prevent"
            )
        if not self.accession_id:
            raise ValueError(
                "a span with no accession_id points at no document — it is a quote "
                "wearing a citation's shape (RA-9)"
            )

    def resolve(self, bundle) -> str:
        """The document's OWN text at these offsets. Raises if it cannot be resolved.

        ⚠ Resolution failure is not a soft miss: an offset that indexes past the
        end of the document, or names a filing the bundle does not hold, is a
        citation that was never checkable.
        """
        from src.fundamental.errors import SpanUnresolvableError

        for part in bundle.of_kind("filing"):
            if part.pins.get("accession_id") == self.accession_id:
                if self.end > len(part.content):
                    raise SpanUnresolvableError(
                        f"span [{self.start}, {self.end}] runs past the end of "
                        f"{self.accession_id} ({len(part.content)} chars)"
                    )
                return part.content[self.start:self.end]
        raise SpanUnresolvableError(
            f"the bundle holds no filing {self.accession_id!r}; it has "
            f"{[p.pins.get('accession_id') for p in bundle.of_kind('filing')]}"
        )

    def to_json_obj(self) -> dict:
        return {"accession_id": self.accession_id, "offset": [self.start, self.end]}


@dataclass(frozen=True, slots=True)
class Claim:
    """One assertion, with what it rests on (§2, RA-9).

    `rests_on` carries **ordinals**, per S-3 — *"an inference … carries the
    ordinals of the facts it rests on"*. ★ That is also why an assumption needs
    an ordinal of its own (**RA-133**): the bare string list `CT-1.1` used to
    carry destroyed it, so an inference could not point at the assumption it
    depended on.
    """

    ordinal: int
    kind: str
    text: str
    span: EvidenceSpan | None = None
    quote: str = ""
    rests_on: tuple[int, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        from src.fundamental.errors import UncitedClaimError

        if self.kind not in KINDS:
            raise ValueError(
                f"claim kind {self.kind!r} is not one of {KINDS}. S-3 gives the model "
                f"exactly three, and a fourth is a shape nothing downstream can render "
                f"(RA-9, RA-22)"
            )
        if not self.text.strip():
            raise ValueError(f"claim {self.ordinal} has no text")
        if self.kind == FACT and (self.span is None or not self.quote):
            # AC-1.5 / INV-004 — X-02's rule, enforced at construction so an
            # uncited fact cannot exist even briefly.
            raise UncitedClaimError(self.ordinal, self.text)
        if self.kind == INFERENCE and not self.rests_on:
            raise ValueError(
                f"claim {self.ordinal} is an inference resting on nothing. S-3: "
                f"\"an inference resting on nothing is an ASSUMPTION; label it as "
                f"one\" — and mislabelling it hides a supplied belief inside a "
                f"derived one"
            )
        if self.kind == ASSUMPTION and self.span is not None:
            raise ValueError(
                f"claim {self.ordinal} is tagged an assumption and carries a span. "
                f"An assumption is *"
                f"something the bundle does not contain*; if it has a span it is a "
                f"fact (S-3)"
            )

    def to_json_obj(self) -> dict:
        return {"ordinal": self.ordinal, "kind": self.kind, "text": self.text,
                "evidence_span": self.span.to_json_obj() if self.span else None,
                "quote": self.quote, "rests_on": list(self.rests_on)}


@dataclass(frozen=True, slots=True)
class ClaimSet:
    """Every claim from one analysis, ordinal-indexed."""

    claims: tuple[Claim, ...]

    def __post_init__(self) -> None:
        ordinals = [c.ordinal for c in self.claims]
        if len(set(ordinals)) != len(ordinals):
            raise ValueError(
                f"duplicate claim ordinals {sorted(ordinals)} — S-3's inferences cite "
                f"ordinals, so a duplicate makes 'rests_on' ambiguous"
            )
        object.__setattr__(self, "claims", tuple(sorted(self.claims, key=lambda c: c.ordinal)))

    def of_kind(self, kind: str) -> tuple[Claim, ...]:
        return tuple(c for c in self.claims if c.kind == kind)

    @property
    def assumptions(self) -> tuple[Claim, ...]:
        """★ RA-133 — `CT-1.1.assumptions[]` is THIS, not a parallel list.

        ⚠ Two stores for one idea is how the same prose ends up under two
        contracts and the rendered one is whichever was written last (DN-33's
        shape). The projection keeps each ordinal, so an inference can point at
        the assumption it rests on.
        """
        return self.of_kind(ASSUMPTION)

    def by_ordinal(self, ordinal: int) -> Claim:
        for c in self.claims:
            if c.ordinal == ordinal:
                return c
        raise KeyError(f"no claim with ordinal {ordinal}")

    def to_json_obj(self) -> dict:
        return {"claims": [c.to_json_obj() for c in self.claims],
                "assumptions": [{"ordinal": a.ordinal, "text": a.text}
                                for a in self.assumptions]}
