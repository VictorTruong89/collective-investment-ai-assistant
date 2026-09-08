"""★ The rendering contract — three reliability classes on one screen (§5, RP-1…RP-5).

```
RENDERING IS LOSSY BY CONSTRUCTION.

It takes a reconciled fact, a measured computation and a stochastic
judgement, and prints them in the same font, on the same screen, to the same
number of decimal places.

Every rule in this module exists to stop that flattening. D-09 is not a
formatting concern; it is the last safety boundary before capital moves.
```
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

FACT, COMPUTATION, JUDGEMENT = "fact", "computation", "judgement"
#: ★★ RP-1's fourth class (RP-48, D-01 RA-116) — *added 2026-08-25*. D-01
#: declared it and RP-1 listed three; **AC-1.79 requires it in every medium.**
RELAYED_JUDGEMENT = "relayed_judgement"
CLASSES = (FACT, COMPUTATION, JUDGEMENT, RELAYED_JUDGEMENT)

#: ★ RP-48 — the four in order of assurance, most to least. A renderer that
#: needs to know *"is this weaker than that"* asks this, not a string compare.
ASSURANCE_ORDER = (FACT, COMPUTATION, JUDGEMENT, RELAYED_JUDGEMENT)

#: ★ **RP-1 residual (QP-1): class is NEVER signalled by colour alone.** Colour
#: inverts in dark mode and is invisible to a share of readers, so the glyph and
#: the text label carry it and colour may only reinforce.
GLYPH = {FACT: "◆", COMPUTATION: "▣", JUDGEMENT: "◌", RELAYED_JUDGEMENT: "◌⇄"}
LABEL = {FACT: "FACT", COMPUTATION: "COMPUTATION", JUDGEMENT: "JUDGEMENT",
         # ⚠ RP-48 — **more** provisional than JUDGEMENT, never a footnote on
         #   it. A relay report is a judgement whose bundle does not exist
         #   (D-01 §4B.2) and whose numbers are mostly unverifiable against data
         #   we hold (RA-118). The label says so in every medium.
         RELAYED_JUDGEMENT: "RELAYED JUDGEMENT (unverified transport)"}


def is_weaker_than(a: str, b: str) -> bool:
    """RP-48 — assurance ordering, for a renderer that must not invert it."""
    return ASSURANCE_ORDER.index(a) > ASSURANCE_ORDER.index(b)

#: RP-5 — a known open defect in a producing domain is disclosed on the artifact
#: that uses it. ⚠ Uncomfortable and correct: the alternative is a card printing
#: a fair value the project's own defect log says is overstated in proportion to
#: leverage, with nothing on the page to say so.
KNOWN_DEFECTS = {
    "D-19": ("the DCF returns an enterprise value per share with no net-debt "
             "subtraction, so the error scales with leverage (L5-inherited-defects §2)"),
    "D-16": ("rsi_14 uses a simple rolling mean, not Wilder smoothing — not "
             "comparable to an RSI read off a broker screen (L5-inherited-defects §2)"),
}


@dataclass(frozen=True, slots=True)
class RenderUnit:
    """One field on one artifact — carrying its class and its OWN as_of (RP-1, RP-2)."""

    field: str
    value: object
    reliability: str
    source: str                 # the producing domain, e.g. "D-03" (RP-6)
    as_of: date
    trail_ref: str | None = None
    known_defects: tuple[str, ...] = ()
    stale: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        from src.reporting.errors import (
            FreshnessUnstatedError,
            NoProducerError,
            UntaggedClassError,
        )
        if self.reliability not in CLASSES:
            raise UntaggedClassError(
                f"field {self.field!r} has reliability {self.reliability!r}; every "
                f"rendered value carries one of {CLASSES} (RP-1)"
            )
        if not self.source:
            raise NoProducerError(
                f"field {self.field!r} names no producing domain. A field D-09 could "
                f"compute itself is a field D-09 must not compute (RP-6, DC-1)"
            )
        if self.as_of is None:
            raise FreshnessUnstatedError(
                f"field {self.field!r} states no as_of. Freshness is per component, "
                f"never per card (RP-2)"
            )
        for code in self.known_defects:
            if code not in KNOWN_DEFECTS:
                raise ValueError(f"unknown defect code {code!r}")

    @property
    def marker(self) -> str:
        """Glyph + text label. ★ Never colour alone (QP-1 residual, AC-9.24d)."""
        return f"{GLYPH[self.reliability]} {LABEL[self.reliability]}"

    def to_json_obj(self) -> dict:
        return {"value": self.value, "class": self.reliability, "source": self.source,
                "as_of": self.as_of.isoformat(), "trail_ref": self.trail_ref,
                "known_defects": list(self.known_defects), "stale": self.stale,
                "note": self.note}
