"""F3 `CT-3.1` — a corporate-action `Finding`.

★★ **`PG-3` justifies an agent here and almost nowhere else**: *the answer is on
the internet, not in the data.* A ticker stops printing; whether that is an
acquisition, a rename, a bankruptcy or a vendor gap is not derivable from the
price series — it is a fact about the world.

⚠ **`PG-3`'s corollary is the discipline:** search PRECEDES classification. A
model asked "what happened to XYZ?" with no evidence will produce a fluent,
plausible answer — and a plausible corporate action is worse than none, because
it will be acted on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Outcome = Literal["acquisition", "merger", "merger_of_equals", "ticker_change",
                  "spinoff", "bankruptcy", "halt", "vendor_gap", "undetermined"]
Confidence = Literal["corroborated", "single_source", "undetermined"]

#: `D5` — retried on `DE-72`'s severity clock, then terminal.
#: ⚠ `DE-72` treats `permanently_unchecked` as EXEMPT, not overdue — because
#: *"reporting an unresolvable class as overdue daily would train a reader to
#: ignore the whole report"* (`DE-35`).
MAX_RESOLUTION_ATTEMPTS = 3


@dataclass(frozen=True, slots=True)
class Evidence:
    url: str
    snippet: str

    def __post_init__(self) -> None:
        if not self.url or not self.snippet:
            raise ValueError("evidence needs a url AND the text it supports (AC-3.8)")


@dataclass(frozen=True, slots=True)
class Finding:
    """`CT-3.1` — one per SIDE of a combination (`AC-3.3`)."""

    ticker: str
    outcome: Outcome
    company: str = ""
    effective_date: str | None = None
    surviving_cik: str | None = None
    successor_symbol: str | None = None
    retired_side: bool = False
    #: ⚠ `AC-3.12` — the date from which a retired symbol's series is another
    #: company's. The finding RECORDS it; it never splices the series.
    series_contaminated_from: str | None = None
    sources: tuple[Evidence, ...] = ()
    confidence: Confidence = "undetermined"
    provenance: dict | None = None
    trace_ref: str | None = None
    attempts: int = 1

    def __post_init__(self) -> None:
        if self.outcome != "undetermined" and not self.sources:
            raise ValueError(
                f"{self.ticker}: a {self.outcome!r} finding with no sources is a "
                "guess (AC-3.8). ⚠ PG-3 justifies an agent here because the answer "
                "is on the internet — an unsourced answer did not come from there.")
        if self.outcome != "undetermined" and self.confidence == "undetermined":
            raise ValueError(
                f"{self.ticker}: a classified outcome must state its corroboration "
                "level (AC-3.2)")
        if self.confidence == "corroborated" and len({e.url for e in self.sources}) < 2:
            raise ValueError(
                f"{self.ticker}: 'corroborated' needs two INDEPENDENT sources; got "
                f"{len({e.url for e in self.sources})} (AC-3.2)")

    @property
    def is_terminal(self) -> bool:
        """`D5` — retried to a ceiling, then exempt rather than perpetually overdue."""
        return (self.outcome != "undetermined"
                or self.attempts >= MAX_RESOLUTION_ATTEMPTS)

    @property
    def state(self) -> str:
        if self.outcome != "undetermined":
            return "resolved"
        return "permanently_unchecked" if self.is_terminal else "retry_due"
