"""F9 — the two adapters. **One prompt, two transports** (`D2`).

★ `QR-20` framed the relay as *"a change of transport, not a new architecture"*.
`D2` holds the same line from the other side: the API adapter uses the **same**
1,952-line prompt spec. ⚠ Two prompts would confound every measured difference —
`F5`'s golden regression and `F7b`'s study both partition by variant, and if the
variants also differ in instruction, no experiment separates transport from
prompt.

⚠ **`AC-F9.2`: the relay is WRAPPED, never rebuilt.** `src/fundamental/relay/`
already does composition, rotation, schema validation, claim re-verification and
coverage de-rating. Re-implementing any of it here would produce a second answer
to a question that already has one (`P4`).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from src.fundamental.source.errors import (
    ClaimContradictsData,
    SpansMissing,
    UnresolvableTicker,
)

#: `D2` — both adapters name the SAME prompt spec. A divergence here is what
#: would make the two variants incomparable.
PROMPT_SPEC = "L1-fundamental-analysis-master-prompt.md"


@dataclass(frozen=True, slots=True)
class SourcedThesis:
    """`CT-9.2` — the existing `Thesis` shape plus what F9 adds."""

    ticker: str
    as_of: str
    claims: tuple
    confidence: dict
    provenance: dict
    source_variant: str
    prompt_spec: str = PROMPT_SPEC

    def __post_init__(self) -> None:
        if not self.provenance:
            raise ValueError("C4 — every thesis carries provenance (AC-F9.5)")
        if self.confidence.get("basis") == "adapter":
            raise ValueError(
                "C3 — confidence comes from the shared assess_confidence, never "
                "from the adapter (RA-67). An adapter that scores its own output "
                "is grading its own homework.")


def _check_claims(claims, *, contradiction_check: Callable[[Any], str | None]):
    """`C1` + `C2`. ⚠ Contradiction RAISES; it is never de-rated."""
    for c in claims:
        if (getattr(c, "is_factual", True)
                and getattr(c, "evidence_ref", None) is None
                and not getattr(c, "unbound_declared", False)):
            raise SpansMissing(
                f"claim {getattr(c, 'text', c)!r} has no span and is not "
                "declared unbound (C1, D1)")
        why = contradiction_check(c)
        if why:
            raise ClaimContradictsData(
                f"{getattr(c, 'text', c)!r} contradicts pipeline data: {why}. "
                "⚠ RA-118 — a claim contradicting our own data is WRONG, not "
                "low-confidence; it is never returned de-rated (C2)")


#: ⚠ NOT `slots=True` — deliberately. With slots, `ApiAdapter.variant` is a slot
#: DESCRIPTOR rather than the default value, so the class-level constant the
#: contract suite reads (`adapter_cls.variant`) disappears. ★ Second time slots
#: has bitten this codebase: F2's models hit the `super()` + slots interaction.
#: Slots buy memory on hot instances; these are constructed once per run.
@dataclass(frozen=True)
class _BaseAdapter:
    author_fn: Callable[[str, object, Mapping], dict]
    assess_confidence: Callable[[dict], dict]
    contradiction_check: Callable[[Any], str | None] = lambda _c: None
    variant: str = ""

    def author(self, ticker: str, as_of: object, context: Mapping) -> SourcedThesis:
        raw = self.author_fn(ticker, as_of, context)
        if not raw or not raw.get("claims"):
            raise UnresolvableTicker(
                ticker, "the source returned nothing to say")
        _check_claims(raw["claims"], contradiction_check=self.contradiction_check)
        return SourcedThesis(
            ticker=ticker, as_of=str(as_of), claims=tuple(raw["claims"]),
            confidence=self.assess_confidence(raw),      # C3 — shared, not ours
            provenance={"port": "thesis_source", "variant": self.variant,
                        **raw.get("provenance", {})},
            source_variant=self.variant)


@dataclass(frozen=True)
class ApiAdapter(_BaseAdapter):
    """★ The DEFAULT variant (`QR-20`, `AC-F9.8`)."""

    variant: str = "api"


@dataclass(frozen=True)
class RelayAdapter(_BaseAdapter):
    """⚠ WRAPS `src/fundamental/relay/`; reimplements none of it (`AC-F9.2`).

    ★ Its verification must propagate **unsoftened**: the relay raises on a
    contradicting claim, and this wrapper must not catch it.
    """

    variant: str = "relay"
