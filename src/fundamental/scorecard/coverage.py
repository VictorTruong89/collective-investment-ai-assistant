"""`evidence_coverage` and the confidence floors — RA-65…RA-68, RA-38, RA-134.

```
RA-38's second clause matters. AP-1 asks the agent for a confidence score.
A MODEL ASKED TO GATE ITSELF WILL NOT GATE ITSELF.

Completeness and coverage are measurable from the bundle, so the floor is
computed from facts the model does not control.
```

★★ **RA-134 — availability is per LEVEL, coverage is per RUBRIC**, and this slice
found that RA-65 had conflated them. Keyed on the *selected* level the metric is
**identically 1.0**: RA-32 makes an unsupported level unavailable, so anything
selectable already has all its evidence. The floors below could never have fired.

★ **RA-67 makes RA-38 structural**: until calibration exists,
`confidence := evidence_coverage`, so there is **no model-produced confidence to
launder** — *"never self-reported"* stops being a rule someone enforces.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean

from src.fundamental.scorecard.models import DIMENSIONS, Rubric

#: INV-012 / INV-013, via RA-67. ⚠ **POLICY CHOICES, and they belong in config**
#: (L4 CN-1, RA-48: *both thresholds are declared config and appear in the
#: RunManifest*). Named here with their source because B4.3 has no manifest to
#: read them from yet — recorded in the blueprint as a known gap.
CONFIDENCE_FLOOR = 0.3        # below ⇒ INSUFFICIENT_DATA (INV-012)
CONFIDENCE_HOLD_CAP = 0.5     # below ⇒ verdict capped at HOLD (INV-013)

INSUFFICIENT_DATA, HOLD_CAPPED, UNCAPPED = "INSUFFICIENT_DATA", "HOLD", "none"


@dataclass(frozen=True, slots=True)
class DimensionCoverage:
    """One dimension's coverage, with the sets that produced it.

    ★ **The sets travel with the ratio.** RA-22 wants a computation the reader
    can trace, and `0.5` alone cannot say *which half was missing* — which is
    exactly the question a data-gap block has to answer (RA-25).
    """

    dimension: str
    required: frozenset
    extracted: frozenset

    @property
    def matched(self) -> frozenset:
        return self.required & self.extracted

    @property
    def missing(self) -> frozenset:
        return self.required - self.extracted

    @property
    def coverage(self) -> float:
        """`|extracted ∩ required| / |required|` — RA-65 as amended.

        ⚠ An empty `required` would be `0/0`. `RubricLevel` refuses a level with
        no `evidence_required`, so a published rubric cannot produce one — and
        this raises rather than returning a plausible 1.0 if one ever does.
        """
        if not self.required:
            raise ValueError(
                f"{self.dimension}: the rubric requires no evidence, so coverage is "
                f"0/0. An evidence-free rubric has no floor at all (RA-134)"
            )
        return len(self.matched) / len(self.required)

    def to_json_obj(self) -> dict:
        return {"dimension": self.dimension, "coverage": round(self.coverage, 6),
                "required": sorted(self.required), "matched": sorted(self.matched),
                "missing": sorted(self.missing)}


@dataclass(frozen=True, slots=True)
class CoverageReport:
    """The four dimensions and their mean — RA-65's aggregate (RA-52)."""

    dimensions: tuple[DimensionCoverage, ...]

    def __post_init__(self) -> None:
        seen = [d.dimension for d in self.dimensions]
        if sorted(seen) != sorted(DIMENSIONS):
            raise ValueError(
                f"coverage was computed over {sorted(seen)}; RA-65's aggregate is the "
                f"mean over the FOUR dimensions scored (RA-52). A mean over three "
                f"reports a number about a scorecard that does not exist"
            )

    @property
    def aggregate(self) -> float:
        return fmean(d.coverage for d in self.dimensions)

    def to_json_obj(self) -> dict:
        return {"aggregate": round(self.aggregate, 6),
                "by_dimension": [d.to_json_obj() for d in self.dimensions]}


def dimension_coverage(rubric: Rubric, extracted) -> DimensionCoverage:
    """★ RA-65 / RA-134 — the denominator is the rubric's UNION, not the level's list."""
    return DimensionCoverage(dimension=rubric.dimension,
                             required=rubric.required_union,
                             extracted=frozenset(extracted))


def coverage_report(rubrics, extracted) -> CoverageReport:
    """Coverage over all four dimensions against one extraction pass."""
    return CoverageReport(tuple(dimension_coverage(r, extracted) for r in rubrics))


# --------------------------------------------------------------------------- #
# The floors — RA-38, RA-67
# --------------------------------------------------------------------------- #

@dataclass(frozen=True, slots=True)
class ConfidenceAssessment:
    """What the floors decided, and on what basis (RA-38, RA-67, RA-21).

    `basis` is **never `"self_reported"`** (CT-1.1's field rule). Until
    calibration lands it is `"evidence_coverage"`, and **RA-68** then splits the
    two again: *how much did we read* and *how often were we right* are different
    questions, and collapsing them would hide a well-evidenced thesis that is
    reliably wrong.
    """

    value: float
    basis: str
    cap: str
    calibration: dict

    @property
    def forces_insufficient_data(self) -> bool:
        return self.cap == INSUFFICIENT_DATA

    @property
    def caps_at_hold(self) -> bool:
        return self.cap in (HOLD_CAPPED, INSUFFICIENT_DATA)

    def to_json_obj(self) -> dict:
        return {"value": round(self.value, 6), "basis": self.basis, "cap": self.cap,
                "calibration": dict(self.calibration)}


def assess_confidence(report, *, calibrated=None,
                      floor: float = CONFIDENCE_FLOOR,
                      hold_cap: float = CONFIDENCE_HOLD_CAP) -> ConfidenceAssessment:
    """RA-38 / AC-1.34 — the floor on what may be **proposed**.

    ⚠ *These are floors on what may be proposed*, not on what is true. D-12 may
    make a verdict more conservative still (P3); nothing here may make one more
    aggressive.

    `calibrated` is RA-68's future state and is **not** built: passing one keeps
    `evidence_coverage` as a separate reported field rather than replacing it.

    ★★ **RA-144 — `report` is anything carrying an `aggregate`, or the float
    itself.** AC-1.77 says the floors fire *"unchanged"* on a relay report, and a
    relay has **claims, not rubric evidence**, so it can never build a
    `CoverageReport`. Requiring one left two options — fake the container, or
    write **a second copy of the floors** — and the second is FE-4's defect,
    the one RA-137 had just finished removing from the wordlist.

    ⚠ **The denominators stay different and must**: RA-65's is the rubric's
    `required_union`, the relay's is `claims_total`. *What is shared is the
    threshold, not the arithmetic that reaches it.*
    """
    coverage = getattr(report, "aggregate", report)
    coverage = float(coverage)
    if calibrated is None:
        # ★ RA-67 — no model-produced number exists to launder.
        value, basis = coverage, "evidence_coverage"
        calibration = {"n": 0, "status": "not_yet_calibrated"}
    else:
        value, basis = float(calibrated), "calibrated"
        calibration = {"n": -1, "status": "calibrated"}

    if value < floor:
        cap = INSUFFICIENT_DATA
    elif value < hold_cap:
        cap = HOLD_CAPPED
    else:
        cap = UNCAPPED
    return ConfidenceAssessment(value=value, basis=basis, cap=cap,
                                calibration=calibration)


def reject_self_reported(basis: str) -> str:
    """RA-38 — the method that exists in order to raise.

    ⚠ A confidence whose basis is the model's own claim lets the model raise its
    own ceiling, which is the one thing the floor exists to prevent.
    """
    from src.fundamental.errors import SelfReportedConfidenceError

    if basis in ("self_reported", "model", "stated"):
        raise SelfReportedConfidenceError(
            f"confidence basis {basis!r} is the model's own claim. A model asked to "
            f"gate itself will not gate itself — confidence is computed from data "
            f"completeness and evidence coverage (RA-38, RA-67)"
        )
    return basis
