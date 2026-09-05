"""CT-1.4 — the `GateVerdict` D-12 consumes (RA-47…RA-51a).

```
THE GATE STATUS IS A JUDGEMENT ABOUT THE THESIS'S OWN RELIABILITY —
WHICH IS D-01'S KNOWLEDGE, NOT D-12'S.

If D-12 derived the status it would need to know what agreement fraction
counts as unstable and what evidence coverage counts as thin. That is
ANALYTICAL POLICY, and D-12 is deterministic composition with no judgement.
```

★ **RA-51a is the field-level rule that keeps the card honest**: a
`stability_fraction` of 0.6 **cannot produce RA-20's *"BUY 3 / HOLD 2"*** — 0.6
is equally 3/5, 6/10 or 12/20. So `k` and `verdict_distribution` are required,
and `confidence` travels with its calibration status so **RA-21** can refuse to
print a bare number.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

PASS, FLAG, VETO, NO_THESIS = "PASS", "FLAG", "VETO", "NO_THESIS"

#: §11.2's statuses. `NO_THESIS` is here and is NOT a kind of PASS — D-12 DN-10:
#: the identity must not be reachable by omission.
STATUSES = (PASS, FLAG, VETO, NO_THESIS)

#: RA-52 — four dimensions, fixed, versioned and closed. Adding one invalidates
#: every §7.4 baseline, exactly as a rubric edit does.
SCORECARD_DIMENSIONS = ("moat_durability", "earnings_quality",
                        "balance_sheet_resilience", "capital_allocation")


@dataclass(frozen=True, slots=True)
class Grade:
    """The transported block (D-12 DN-25). ★ Absent is `None`, never invented.

    ⚠ **L3 BS-34.** A B3 stub has no `k` and no distribution because it never ran
    a model. The tempting fix — emit `k: 1, verdict_distribution: {"PASS": 1},
    stability_fraction: 1.0` — is *literally true and completely misleading*, and
    it is D-15's exact shape: a plausible value manufactured by a placeholder.
    So every graded field is nullable, and the renderer prints the absence.
    """

    verdict: str | None = None
    conviction: str | None = None
    stability_fraction: float | None = None
    k: int | None = None
    verdict_distribution: dict | None = None
    scorecard: dict | None = None
    confidence: dict | None = None

    def __post_init__(self) -> None:
        if self.scorecard is not None:
            unknown = set(self.scorecard) - set(SCORECARD_DIMENSIONS)
            if unknown:
                raise ValueError(
                    f"scorecard carries undeclared dimension(s) {sorted(unknown)}. The "
                    f"set is fixed, versioned and closed (RA-52)"
                )
        if self.k is not None and self.verdict_distribution is not None:
            total = sum(self.verdict_distribution.values())
            if total != self.k:
                raise ValueError(
                    f"verdict_distribution sums to {total} but k={self.k}. RA-20 "
                    f"renders 'BUY 3 / HOLD 2' from these two, and they must agree"
                )

    def to_json_obj(self) -> dict:
        return {"verdict": self.verdict, "conviction": self.conviction,
                "stability_fraction": self.stability_fraction, "k": self.k,
                "verdict_distribution": self.verdict_distribution,
                "scorecard": self.scorecard, "confidence": self.confidence}

    @property
    def keys(self) -> frozenset:
        """What D-12 DN-32's superset check compares against."""
        return frozenset(self.to_json_obj())


@dataclass(frozen=True, slots=True)
class GateVerdict:
    """CT-1.4. The decision-ready projection of a Thesis — never its replacement.

    **RA-47**: both are published. The projection replacing the thesis would make
    the falsifiers and the bear case unreachable.
    """

    gate_id: str
    ticker: str
    as_of: date
    status: str
    reason: str
    grade: Grade = field(default_factory=Grade)
    thesis_version: int | None = None
    thesis_as_of: date | None = None
    #: ★ L3 BS-34 / BS-27 — a stub says so, in the artifact AND in the manifest.
    produced_by_stub: str | None = None

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(
                f"status {self.status!r} is not one of {STATUSES}. RA-49 makes the "
                f"mapping total; an invented status is an unmapped state"
            )
        if not self.reason:
            raise ValueError(
                "a GateVerdict carries its reason. A status with no reason cannot be "
                "attributed on the card (D-12 DN-13)"
            )

    def to_json_obj(self) -> dict:
        return {
            "gate_id": self.gate_id, "ticker": self.ticker,
            "as_of": self.as_of.isoformat(), "status": self.status,
            "reason": self.reason,
            "thesis_version": self.thesis_version,
            "thesis_as_of": self.thesis_as_of.isoformat() if self.thesis_as_of else None,
            "grade": self.grade.to_json_obj(),
            "produced_by_stub": self.produced_by_stub,
        }
