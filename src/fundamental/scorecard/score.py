"""Criterion selection — the score is DERIVED, never emitted (RA-31, RA-32, RA-53).

```
You are selecting from written criteria, not producing a score. Read every
option before choosing. Choose the one whose criterion the evidence actually
satisfies — not the one nearest your overall impression. IF THE EVIDENCE FOR
AN OPTION'S STATED REQUIREMENTS IS MISSING FROM THE BUNDLE, THAT OPTION IS
UNAVAILABLE TO YOU no matter how well it describes the company.

You will also state, in one sentence, the single observation that would move
you to the adjacent option. That sentence is part of the answer.
```

★ **The last paragraph is the cheapest de-biasing device in the registry.** It
forces the boundary of the judgement to be named at the moment it is made, and
it is what makes **RM-2**'s dispersion readable: *a dimension that moves two
levels between identical runs, whose stated boundary observation is different
each time, has an under-determined rubric (RA-34) — not a noisy model.*
"""

from __future__ import annotations

from dataclasses import dataclass

from src.fundamental.errors import LevelUnavailableError, ScoreEmittedError
from src.fundamental.scorecard.coverage import (
    ConfidenceAssessment, CoverageReport, assess_confidence, coverage_report,
)
from src.fundamental.scorecard.models import DIMENSIONS, Rubric, RubricLevel


@dataclass(frozen=True, slots=True)
class Selection:
    """What the model returned for one dimension: a **criterion**, not a number.

    ⚠ `criterion` is the level's own text, echoed back. That is how RA-31 is
    checked rather than trusted: a response carrying `score: 3` and nothing else
    cannot be distinguished from an interpolation, and **the echo is what ties
    the answer to a written level.**
    """

    dimension: str
    criterion: str
    boundary_observation: str
    evidence_cited: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.dimension not in DIMENSIONS:
            raise ValueError(f"{self.dimension!r} is not one of {DIMENSIONS} (RA-52)")
        if not self.criterion.strip():
            raise ScoreEmittedError(
                f"{self.dimension}: a selection with no criterion is a score emitted "
                f"directly. A number invites interpolation, and interpolation is "
                f"where dispersion enters (RA-31)"
            )
        if not self.boundary_observation.strip():
            raise ValueError(
                f"{self.dimension}: the single observation that would move you to the "
                f"adjacent option is part of the answer, not an optional extra — it "
                f"is what makes RM-2's dispersion readable (§4.0, RA-34)"
            )


@dataclass(frozen=True, slots=True)
class DimensionScore:
    """A derived score, with the level it was derived from."""

    dimension: str
    score: int
    level: RubricLevel
    selection: Selection
    rubric_id: str

    def to_json_obj(self) -> dict:
        return {"dimension": self.dimension, "score": self.score,
                "rubric_id": self.rubric_id, "criterion": self.level.criterion,
                "boundary_observation": self.selection.boundary_observation,
                "evidence_required": list(self.level.evidence_required)}


@dataclass(frozen=True, slots=True)
class ScorecardResult:
    """§8's output for one `(ticker, as_of)` — four dimensions, and no total.

    ★★ **RA-53: the scorecard is transported, never summed. There is no composite
    score.** *A weighted sum would be a second verdict competing with the first,
    produced by weights nobody fitted* — and `L2` §5.0's argument against fitted
    weights applies with more force here, where `n` is smaller still.
    """

    ticker: str
    scores: tuple[DimensionScore, ...]
    coverage: CoverageReport
    confidence: ConfidenceAssessment

    def __post_init__(self) -> None:
        seen = sorted(s.dimension for s in self.scores)
        if seen != sorted(DIMENSIONS):
            raise ValueError(
                f"scorecard covers {seen}; the dimension set is closed and complete "
                f"(RA-52). ⚠ A missing dimension is indistinguishable from a "
                f"low-scoring one on the card"
            )

    def score_of(self, dimension: str) -> int:
        for s in self.scores:
            if s.dimension == dimension:
                return s.score
        raise KeyError(dimension)

    @property
    def as_grade_block(self) -> dict:
        """The `scorecard` mapping `CT-1.4`'s grade carries (D-12 DN-25)."""
        return {s.dimension: s.score for s in self.scores}

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker,
                "scorecard": self.as_grade_block,
                "detail": [s.to_json_obj() for s in self.scores],
                "evidence_coverage": self.coverage.to_json_obj(),
                "confidence": self.confidence.to_json_obj()}


def derive_score(rubric: Rubric, selection: Selection, extracted) -> DimensionScore:
    """RA-31 + RA-32 — resolve a criterion to its level, and check availability.

    ★ **The score is DERIVED from the criterion**, by matching the echoed text
    against the published rubric. A criterion that matches no level is not a
    near-miss to be rounded — it is a level the model invented.
    """
    if rubric.dimension != selection.dimension:
        raise ValueError(
            f"rubric {rubric.rubric_id} scored against a {selection.dimension!r} "
            f"selection"
        )
    matches = [lv for lv in rubric.levels
               if _normalise(lv.criterion) == _normalise(selection.criterion)]
    if not matches:
        raise ScoreEmittedError(
            f"{rubric.rubric_id}: the returned criterion matches no published level. "
            f"The score is derived from a SELECTION, so a criterion nothing published "
            f"is an invented level rather than a rounding question (RA-31, RA-33)"
        )
    level = matches[0]

    # ★ RA-32 / AC-1.30 — a failed selection, not a low-confidence one.
    if not level.is_available(extracted):
        raise LevelUnavailableError(
            rubric.rubric_id, level.score,
            set(level.evidence_required) - set(extracted),
        )
    return DimensionScore(dimension=rubric.dimension, score=level.score, level=level,
                          selection=selection, rubric_id=rubric.rubric_id)


def build_scorecard(*, ticker: str, rubrics, selections, extracted,
                    calibrated=None) -> ScorecardResult:
    """The whole §8 pass: derive four scores, measure coverage, apply the floors.

    ⚠ **Coverage is computed over the RUBRICS, not over the selected levels**
    (RA-134). Keyed on the selections it would be identically 1.0 — every
    selectable level has its evidence by construction — and RA-38's floors could
    never fire.
    """
    by_dimension = {r.dimension: r for r in rubrics}
    scores = tuple(
        derive_score(by_dimension[s.dimension], s, extracted)
        for s in sorted(selections, key=lambda s: s.dimension)
    )
    report = coverage_report(
        [by_dimension[d] for d in sorted(DIMENSIONS)], extracted)
    return ScorecardResult(ticker=ticker.upper(), scores=scores, coverage=report,
                           confidence=assess_confidence(report, calibrated=calibrated))


def _normalise(text: str) -> str:
    """Whitespace-insensitive criterion matching — and only whitespace.

    ⚠ A criterion is wrapped across lines in the rubric source and arrives from
    the API on one, so a run of spaces is a transport artifact. **A changed word
    is a different criterion**, which is the same line B4.2's span check draws.
    """
    return " ".join(text.split()).casefold()
