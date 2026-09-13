"""`DX-100` — offering a rubric to the model as CRITERIA, and deriving the score.

⛔⛔ **The defect this closes, measured 2026-09-13.** The judgement runner's rubric
schema offered `level: integer enum [4,3,2,1,0]`, and the criterion text reached
the model NOWHERE — not the prompt, not the schema. The first gated run returned
J-05 = 3 and J-06 = 0, and J-05 said so itself: *"the enumerated criteria text
was not supplied to me, so this mapping is mine"*. ★ `RA-31` already forbade it —
*"the model selects a CRITERION and the score is derived"* — and `score.py` held
the contract (`Selection`, `derive_score`, `ScoreEmittedError`); nothing on the
live path called it.

★ **Four parts, one per failure:**
  1. the offered levels' criterion text is RENDERED into the payload — never
     their scores: *a number invites interpolation* (`RA-31`);
  2. in a SEEDED, RECORDED order (`RA-17`, `P-1`) — position bias is measurable
     only if the order that was shown is on file;
  3. the answer is the criterion TEXT, and the score is DERIVED by
     `derive_score`, so `ScoreEmittedError`/`LevelUnavailableError` guard it;
  4. `insufficient_evidence` is an explicit exit (`MP-7`) — measured: with no way
     to say *"I cannot grade this"*, J-06 used the FLOOR to mean it, contradicting
     level 0's own criterion (*"the bundle does not disclose capital-allocation
     actions"*) in the same answer that listed the actions.

★ Pure: no I/O, no model. The runner composes; this decides what is shown and
what the answer means (`AP-5`).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.fundamental.errors import ScoreEmittedError
from src.fundamental.scorecard.models import Rubric, RubricLevel
from src.fundamental.scorecard.score import DimensionScore, Selection, derive_score

#: `MP-7` — the stated way to say *"the bundle does not let me decide"*.
#: ⚠ NOT a level and NOT a score: it resolves to `None`, never to 0.
INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True, slots=True)
class RubricOffer:
    """The levels shown to the model for one call, in the order shown."""

    rubric: Rubric
    ordered: tuple[RubricLevel, ...]
    seed: str

    def __post_init__(self) -> None:
        if not self.ordered:
            raise ValueError(f"{self.rubric.rubric_id}: an offer of no levels selects nothing")
        texts = [lv.criterion for lv in self.ordered]
        if INSUFFICIENT_EVIDENCE in texts or len(set(texts)) != len(texts):
            raise ValueError(f"{self.rubric.rubric_id}: criteria must be distinct, and "
                             f"none may collide with {INSUFFICIENT_EVIDENCE!r}")

    @property
    def criteria(self) -> tuple[str, ...]:
        """The answer enum, in presentation order, WITHOUT the exit."""
        return tuple(lv.criterion for lv in self.ordered)

    @property
    def permutation(self) -> tuple[int, ...]:
        """★ `RA-17` — the scores in the order their criteria were SHOWN. Recorded
        with the call so `P-1` can ask whether position moved the answer."""
        return tuple(lv.score for lv in self.ordered)

    def render(self) -> str:
        """The rubric as the model reads it — criteria and evidence, no numbers."""
        lines = [
            f'<rubric id="{self.rubric.rubric_id}">',
            "Choose ONE option below and copy its criterion text EXACTLY into",
            "`criterion`. The options are shown in a randomised order and carry no",
            "score: select the criterion the evidence satisfies, not a position.",
            f"If the bundle does not let you decide between them, answer "
            f"`{INSUFFICIENT_EVIDENCE}` —",
            "that is NOT the lowest option and is never recorded as a score.",
            "",
        ]
        for lv in self.ordered:
            lines.append(f"OPTION: {lv.criterion}")
            lines.append(f"  evidence required: {', '.join(lv.evidence_required)}")
        lines.append("</rubric>")
        return "\n".join(lines)


def offer(rubric: Rubric, scores, *, seed: str) -> RubricOffer:
    """Offer `scores`' levels in a seeded order.

    ★ Seeded by a STRING (`random.Random` hashes it with SHA-512, stable across
    processes), so the same `(run seed, block)` always shows the same order and a
    recording can be re-derived — while different blocks and runs vary, which is
    what keeps position bias from correlating across a stage.
    """
    levels = [rubric.level(s) for s in scores]
    random.Random(seed).shuffle(levels)
    return RubricOffer(rubric=rubric, ordered=tuple(levels), seed=seed)


def resolve(an_offer: RubricOffer, answer: dict, extracted) -> DimensionScore | None:
    """The model's answer → a DERIVED score, or `None` for `insufficient_evidence`.

    ⚠ Through `derive_score`, never around it: an invented criterion raises
    `ScoreEmittedError`, a level whose evidence is absent raises
    `LevelUnavailableError`. ★ A criterion that was published but NOT offered in
    this call is refused too — the model may only choose what it was shown.
    """
    criterion = answer["criterion"]
    if criterion == INSUFFICIENT_EVIDENCE:
        return None
    shown = {" ".join(c.split()).casefold() for c in an_offer.criteria}
    if " ".join(criterion.split()).casefold() not in shown:
        raise ScoreEmittedError(
            f"{an_offer.rubric.rubric_id}: the returned criterion was not among the "
            f"{len(shown)} offered in this call (RA-31, RA-32)")
    selection = Selection(dimension=an_offer.rubric.dimension, criterion=criterion,
                          boundary_observation=answer["what_would_move_it_down"])
    return derive_score(an_offer.rubric, selection, extracted)
