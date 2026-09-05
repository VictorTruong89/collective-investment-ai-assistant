"""CT-1.1 — the Thesis, its falsifiers and its bear case (§9, RA-35…RA-38).

```
A thesis is NOT VALID without at least one falsifier that is observable,
dated, and checkable WITHOUT A FURTHER JUDGEMENT CALL.

"Competition intensifies" is not a falsifier.
"Gross margin below 55% in any two consecutive quarters" is.
```

★ **RA-36: falsifiers are written at authoring time, versioned with the thesis,
and NEVER edited — only superseded by a new thesis version.** *Editing a
falsifier after the fact is how a thesis becomes unfalsifiable.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

#: J-16's closed set. ⚠ **Four, not three** — `INSUFFICIENT_DATA` is D-01's way
#: of declining, and §11.2 maps it to `VETO`. It is **not** on D-12's verdict
#: lattice (`{BUY, HOLD, SELL}`): D-01 emits a *thesis* verdict and D-12 composes
#: a *decision* one, and §11.2 is the adapter between them.
BUY, HOLD, SELL, INSUFFICIENT_DATA = "BUY", "HOLD", "SELL", "INSUFFICIENT_DATA"
VERDICTS = (BUY, HOLD, SELL, INSUFFICIENT_DATA)

#: J-16's conviction enum. **RA-8: enums with written criteria, never free-form.**
CONVICTIONS = ("Low", "Medium", "Medium-High", "High")

#: J-15 — two to four conditions, and the bounds are the prompt's.
MIN_FALSIFIERS, MAX_FALSIFIERS = 2, 4

#: ⚠ J-15: *"You may not write 'the thesis is invalidated if the investment case
#: no longer holds' or any variant. That is a tautology and it fails the run."*
_TAUTOLOGY_MARKERS = ("investment case no longer holds", "thesis is invalidated",
                      "no longer attractive", "story changes", "fundamentals deteriorate")


@dataclass(frozen=True, slots=True)
class Falsifier:
    """One stated breaking condition — RA-35's four properties, all required.

    ★ **`observable_field` is the load-bearing one.** *A falsifier naming a field
    this system does not receive is not checkable, however precise it sounds* —
    so the field is validated against the observables D-02/D-07 actually publish,
    not against how specific the sentence reads.
    """

    ordinal: int
    condition: str
    observable_field: str          # the metric or field the check reads
    source: str                    # "D-02" | "D-07"
    deadline: date                 # RA-35's "dated" — not "eventually"
    materiality: str               # what it would mean if it fired
    about_business: bool = True    # False ⇒ a price level

    @classmethod
    def from_json_obj(cls, payload: dict) -> "Falsifier":
        """★ Rehydrate. ⚠ `deadline` is a DATE — a string here would compare
        against `as_of` as text and RA-35's *"dated, not eventually"* would be
        satisfied by a value nothing can evaluate."""
        return cls(
            ordinal=int(payload["ordinal"]), condition=payload["condition"],
            # ⚠ The serialised key is `observable`, the field is
            #   `observable_field`. ★ Asymmetric names are exactly why a
            #   round-trip test earns its place — the mismatch raised on the
            #   first real rehydration rather than producing a silent miss.
            observable_field=payload["observable"],
            source=payload["source"],
            deadline=date.fromisoformat(str(payload["deadline"])[:10]),
            materiality=payload["materiality"],
            about_business=bool(payload.get("about_business", True)))

    def __post_init__(self) -> None:
        from src.fundamental.errors import UncheckableFalsifierError

        text = self.condition.strip()
        if not text:
            raise UncheckableFalsifierError(self.ordinal, "no condition text")
        low = text.casefold()
        if any(m in low for m in _TAUTOLOGY_MARKERS):
            raise UncheckableFalsifierError(
                self.ordinal,
                f"{text[:70]!r} is a tautology — it restates the thesis failing "
                f"rather than naming an observation (J-15)",
            )
        if not self.observable_field:
            raise UncheckableFalsifierError(
                self.ordinal,
                "names no observable field. ★ A falsifier naming a field this "
                "system does not receive is not checkable, however precise it "
                "sounds (J-15, RA-35)",
            )
        if not self.materiality.strip():
            raise UncheckableFalsifierError(
                self.ordinal,
                "states no materiality. RA-35 requires that firing means the thesis "
                "is WRONG, not merely dented",
            )

    def to_json_obj(self) -> dict:
        return {"ordinal": self.ordinal, "condition": self.condition,
                "observable": self.observable_field, "source": self.source,
                "deadline": self.deadline.isoformat(),
                "materiality": self.materiality,
                "about_business": self.about_business, "checkable": True}


@dataclass(frozen=True, slots=True)
class BearCase:
    """J-11's output — a separate call against the same bundle (RA-15).

    ⚠ *A bear case written in the same breath is a **rhetorical concession**, not
    an analysis* (AP-3, INV-011). The separateness is checked at the seam, not
    trusted from the prose.
    """

    text: str
    falsification_condition: str        # ★ J-11 item 4 — the bear case's OWN
    prompt_version: str
    run_id: str

    @classmethod
    def from_json_obj(cls, payload: dict) -> "BearCase":
        return cls(text=payload["text"],
                   falsification_condition=payload["falsification_condition"],
                   prompt_version=payload["prompt_version"],
                   run_id=payload["run_id"])

    def __post_init__(self) -> None:
        from src.fundamental.errors import NullBearCaseError

        if not self.falsification_condition.strip():
            # RM-11 / AC-1.18. ★ *A bear case that nothing could disprove is a mood.*
            raise NullBearCaseError(
                "the bear case names no falsifiable condition of its own (J-11 item "
                "4). A bear case that nothing could disprove is a mood, and it is "
                "measurable without judgement (RM-11)"
            )
        if not self.text.strip():
            raise NullBearCaseError("the bear case has no text")

    def to_json_obj(self) -> dict:
        return {"text": self.text,
                "falsification_condition": self.falsification_condition,
                "prompt_version": self.prompt_version, "run_id": self.run_id}


@dataclass(frozen=True, slots=True)
class Thesis:
    """CT-1.1. ★ Falsifiers first, and they were committed in an earlier call."""

    ticker: str
    thesis_version: int
    as_of: date
    bundle_hash: str
    run_id: str
    verdict: str
    conviction: str
    falsifiers: tuple[Falsifier, ...]
    bear_case: BearCase
    scorecard: dict
    confidence: dict
    verdict_stability: dict | None = None
    claims: tuple = ()
    data_gaps: tuple[str, ...] = ()
    assumptions: tuple[dict, ...] = field(default_factory=tuple)
    #: ★ RA-16 — the hash of the persisted J-15 output, written BEFORE J-16 ran.
    #: Its presence is what distinguishes "the falsifiers were committed first"
    #: from "one call produced both and we wrote them in that order".
    falsifier_commit_hash: str = ""
    #: RA-14/RA-108 — the Stage-A freeze this thesis was built on.
    stage_a_hash: str = ""
    #: ★ RA-142 — the sector files this thesis rested on, **declared**. The
    #: pins are already inside `bundle_hash` (RA-102), which proves they did not
    #: change; ⚠ it does not say *what they were* to a reader who no longer
    #: holds the bundle. RA-102 asks for both.
    sector_files: tuple[dict, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        from src.fundamental.errors import (
            NoFalsifierError, UncommittedFalsifiersError, VerdictNotEnumError,
        )

        if self.verdict not in VERDICTS:
            raise VerdictNotEnumError("verdict", self.verdict, VERDICTS)
        if self.conviction not in CONVICTIONS:
            raise VerdictNotEnumError("conviction", self.conviction, CONVICTIONS)
        if len(self.falsifiers) < MIN_FALSIFIERS:
            raise NoFalsifierError(self.ticker, len(self.falsifiers))
        if len(self.falsifiers) > MAX_FALSIFIERS:
            raise NoFalsifierError(
                self.ticker, len(self.falsifiers),
                detail=f"J-15 asks for {MIN_FALSIFIERS}-{MAX_FALSIFIERS} conditions",
            )
        if not any(f.about_business for f in self.falsifiers):
            # ★ J-15: *a falsifier set that consists only of price levels is a
            # stop-loss wearing a thesis's clothing, and it will fire on
            # volatility rather than on being wrong.*
            raise NoFalsifierError(
                self.ticker, len(self.falsifiers),
                detail="every falsifier is a price level — that is a stop-loss "
                       "wearing a thesis's clothing (J-15)",
            )
        if not self.falsifier_commit_hash:
            raise UncommittedFalsifiersError(self.ticker)
        if self.confidence.get("basis") == "self_reported":
            from src.fundamental.errors import SelfReportedConfidenceError
            raise SelfReportedConfidenceError(
                "a thesis carrying a self-reported confidence lets the model raise "
                "its own ceiling (RA-38, CT-1.1's field rule)"
            )

    @classmethod
    def from_json_obj(cls, payload: dict) -> "Thesis":
        """★★ **Rehydration exists so RC-61's reuse is real.**

        ⚠ *Written 2026-08-26:* the cache was built first and every lookup
        silently missed, because `Thesis` had no way back from JSON and the
        lookup swallowed the failure. **A cache that can only miss is
        decorative**, and it would have cost $1.34 a day while appearing to work.

        ★ `__post_init__` runs on the way back in, so a stored thesis that no
        longer satisfies CT-1.1 — too few falsifiers, an unknown verdict, an
        uncommitted falsifier set — **raises rather than being served**. A record
        written under an older contract is not silently trusted.
        """
        return cls(
            ticker=payload["ticker"],
            thesis_version=int(payload["thesis_version"]),
            as_of=date.fromisoformat(str(payload["as_of"])[:10]),
            bundle_hash=payload["bundle_hash"], run_id=payload["run_id"],
            verdict=payload["verdict"], conviction=payload["conviction"],
            falsifiers=tuple(Falsifier.from_json_obj(f)
                             for f in payload.get("falsifiers", ())),
            bear_case=BearCase.from_json_obj(payload["bear_case"]),
            scorecard=dict(payload.get("scorecard") or {}),
            confidence=dict(payload.get("confidence") or {}),
            verdict_stability=payload.get("verdict_stability"),
            data_gaps=tuple(payload.get("data_gaps") or ()),
            assumptions=tuple(dict(a) for a in payload.get("assumptions") or ()),
            falsifier_commit_hash=payload.get("falsifier_commit_hash", ""),
            stage_a_hash=payload.get("stage_a_hash", ""),
            sector_files=tuple(dict(s) for s in payload.get("sector_files") or ()),
        )

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "thesis_version": self.thesis_version,
            "as_of": self.as_of.isoformat(), "bundle_hash": self.bundle_hash,
            "run_id": self.run_id, "verdict": self.verdict,
            "sector_files": [dict(s) for s in self.sector_files],
            "conviction": self.conviction,
            "verdict_stability": self.verdict_stability,
            # ★ RA-16 — falsifiers precede the verdict in the record as well as
            # in the call order, so a reader of the JSON sees the commitment first.
            "falsifiers": [f.to_json_obj() for f in self.falsifiers],
            "falsifier_commit_hash": self.falsifier_commit_hash,
            "stage_a_hash": self.stage_a_hash,
            "bear_case": self.bear_case.to_json_obj(),
            "scorecard": dict(self.scorecard),
            "confidence": dict(self.confidence),
            "claims": [c.to_json_obj() for c in self.claims],
            "data_gaps": list(self.data_gaps),
            "assumptions": [dict(a) for a in self.assumptions],
        }
