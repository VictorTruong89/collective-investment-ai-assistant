"""D-01 §10 — what an invalidation check produces.

★ **`InvalidationEvent`, not a verdict** (RA-41). D-01 reports that a *stated
condition occurred*; whether that changes the position is SEAT-1's (L0 §3.1).
The distinction is structural here: this contract has no field a verdict could
travel in, and `assert_no_verdict` refuses one that tries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

#: RA-42 — invalidation is cheap-tier and high-frequency (INV-8, Haiku 4.5).
#: Deep tier is reached only when triage flags something.
TIER_CHEAP = "cheap"
TIER_DEEP = "deep"

#: The keys a verdict would arrive under if RA-41 were ever violated.
_VERDICT_KEYS = frozenset({
    "verdict", "recommendation", "action", "rating", "conviction", "target",
})


@dataclass(frozen=True, slots=True)
class NewEvidenceItem:
    """One piece of post-thesis evidence — a filing or a news item.

    ⚠ `knowable_at` is the load-bearing field, not the publication date. RA-40
    filters on it, and D-07's DE-18 two-date rule is what makes it trustworthy.
    """

    kind: str                  # "filing" | "news"
    ref: str                   # accession number, url — the handle, not the text
    knowable_at: datetime
    item_code: str = ""        # 8-K item number where the form has one
    text: str = ""

    def __post_init__(self) -> None:
        if self.kind not in ("filing", "news"):
            raise ValueError(f"unknown evidence kind {self.kind!r}")
        if not self.ref:
            raise ValueError("evidence with no ref cannot be cited")


@dataclass(frozen=True, slots=True)
class Triage:
    """The cheap-tier read of one item against one thesis (RA-42).

    ★ Shallow by design. It answers *does this bear on a stated condition?* —
    never *what should we do about it*.
    """

    flagged: bool
    falsifier_ordinal: int | None = None
    rationale: str = ""
    escalate: bool = False     # → deep tier, V-02


@dataclass(frozen=True, slots=True)
class InvalidationEvent:
    """RA-41 — a stated condition occurred. That is the whole claim.

    ⚠ There is deliberately **no verdict, no recommendation and no conviction**
    on this object. A monitoring channel that emitted one would be a second
    decision channel, and the constitution permits exactly one (INV-6).
    """

    ticker: str
    thesis_version: int
    falsifier_ordinal: int
    condition: str
    materiality: str
    occurred_at: datetime
    evidence_ref: str
    tier: str = TIER_CHEAP

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "thesis_version": self.thesis_version,
            "falsifier_ordinal": self.falsifier_ordinal,
            "condition": self.condition, "materiality": self.materiality,
            "occurred_at": self.occurred_at.isoformat(),
            "evidence_ref": self.evidence_ref, "tier": self.tier,
        }


@dataclass(frozen=True, slots=True)
class InvalidationCheck:
    """One run of the check — what it read, what it refused to read, what fired."""

    ticker: str
    thesis_version: int
    as_of: date
    events: tuple[InvalidationEvent, ...]
    considered: tuple[str, ...]
    #: ★ RA-40's discards, named. *Re-reading old evidence produces drift, not
    #: information* — and a silent filter is indistinguishable from a bug.
    skipped_already_known: tuple[str, ...]
    escalated: tuple[str, ...] = ()

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "thesis_version": self.thesis_version,
            "as_of": self.as_of.isoformat(),
            "events": [e.to_json_obj() for e in self.events],
            "considered": list(self.considered),
            "skipped_already_known": list(self.skipped_already_known),
            "escalated": list(self.escalated),
        }


def assert_no_verdict(obj: dict, *, where: str) -> None:
    """RA-41 / RA-87 — a monitoring output may not carry a decision."""
    from src.fundamental.errors import ResearchError

    leaked = sorted(_VERDICT_KEYS & set(obj))
    if leaked:
        raise ResearchError(
            f"{where} carries {leaked!r} — monitoring reports that a condition "
            f"occurred; it never decides (RA-41, RA-87, INV-6)"
        )
