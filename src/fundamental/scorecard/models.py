"""The scorecard — bounded judgement (§8, RA-31…RA-34, RA-52…RA-54).

```
A SCORECARD CONVERTS AN OPEN-ENDED JUDGEMENT INTO A SELECTION FROM WRITTEN
CRITERIA, which is what makes it repeatable enough to measure.
```

★ **RA-31 is the shape of everything here: the model selects a CRITERION, and
the score is DERIVED from the selection.** It never emits a number directly —
*a number invites interpolation, and interpolation is where dispersion enters.*

⚠ **RA-134 (added building this slice): availability is per LEVEL, coverage is
per RUBRIC.** They answer different questions, and RA-65 had conflated them:
*"which levels may the model choose from?"* is a filter, and *"how much of what
this dimension needed did we pull?"* is a ratio whose denominator must be what a
complete assessment would require.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

#: RA-52 — four dimensions, **fixed, versioned and closed**. *Adding one
#: invalidates every §7.4 baseline*, exactly as a rubric edit does.
DIMENSIONS = ("moat_durability", "earnings_quality",
              "balance_sheet_resilience", "capital_allocation")

#: Every dimension is scored 0–4 by written criteria (RA-31).
MIN_SCORE, MAX_SCORE = 0, 4


@dataclass(frozen=True, slots=True)
class RubricLevel:
    """One written criterion and the evidence a reader would need to check it.

    ★ **RA-32: every level names the evidence required.** *A level selected
    without that evidence present in the bundle is a failed selection, not a
    low-confidence one.*
    """

    score: int
    criterion: str
    evidence_required: tuple[str, ...]

    def __post_init__(self) -> None:
        if not MIN_SCORE <= self.score <= MAX_SCORE:
            raise ValueError(
                f"level score {self.score} is outside [{MIN_SCORE}, {MAX_SCORE}] "
                f"(RA-31, §8.1)"
            )
        if not self.criterion.strip():
            raise ValueError(
                f"level {self.score} has no criterion. ★ The model selects a "
                f"CRITERION and the score is derived — a level with no written text "
                f"is a number wearing a rubric's shape (RA-31)"
            )
        if not self.evidence_required:
            # ⚠ RA-134. A level declaring nothing shrinks `evidence_coverage`'s
            # union denominator, which is the manufacturing RA-134 forbids —
            # and it also makes the level unconditionally available (RA-32),
            # so an evidence-free rubric has no floor at all.
            raise ValueError(
                f"level {self.score} declares no evidence_required. It would be "
                f"unconditionally available (RA-32) AND shrink coverage's "
                f"denominator (RA-65, RA-134) — an evidence-free level is a level "
                f"nothing can fail to support"
            )

    def is_available(self, extracted) -> bool:
        """RA-32 — every required item must have been **extracted**, not merely present.

        ⚠ **RA-66**: *a 10-K that is present but from which the required number
        could not be pulled is not evidence.* `extracted` is B4.2's
        `evidence_ids`, which counts only items whose X-01 check passed.
        """
        return set(self.evidence_required) <= set(extracted)

    def to_json_obj(self) -> dict:
        return {"score": self.score, "criterion": self.criterion,
                "evidence_required": list(self.evidence_required)}


@dataclass(frozen=True, slots=True)
class Rubric:
    """A versioned, immutable set of levels for one dimension (RA-33)."""

    dimension: str
    version: int
    levels: tuple[RubricLevel, ...]
    note: str = ""

    def __post_init__(self) -> None:
        if self.dimension not in DIMENSIONS:
            raise ValueError(
                f"dimension {self.dimension!r} is not one of {DIMENSIONS}. The set is "
                f"fixed, versioned and closed — adding one invalidates every §7.4 "
                f"baseline (RA-52)"
            )
        scores = [lv.score for lv in self.levels]
        if len(set(scores)) != len(scores):
            raise ValueError(f"{self.rubric_id}: duplicate level scores {sorted(scores)}")
        if not self.levels:
            raise ValueError(f"{self.dimension}: a rubric with no levels selects nothing")
        object.__setattr__(self, "levels",
                           tuple(sorted(self.levels, key=lambda lv: -lv.score)))

    @property
    def rubric_id(self) -> str:
        return f"{self.dimension}@v{self.version}"

    @property
    def required_union(self) -> frozenset:
        """★ **RA-65 as amended — `evidence_coverage`'s denominator.**

        ```
        AVAILABILITY IS PER LEVEL; COVERAGE IS PER RUBRIC.
        ```

        ⚠ The union, **not the selected level's list**. Keyed on the selected
        level, coverage is identically 1.0 — RA-32 makes an unsupported level
        unavailable, so anything selectable already has all its evidence, and
        **the floors RA-38 depends on could never fire** (RA-134).
        """
        return frozenset().union(*(set(lv.evidence_required) for lv in self.levels))

    def level(self, score: int) -> RubricLevel:
        for lv in self.levels:
            if lv.score == score:
                return lv
        raise KeyError(f"{self.rubric_id} has no level {score}")

    def available_levels(self, extracted) -> tuple[RubricLevel, ...]:
        """RA-32 — the levels the model may choose from, highest first.

        ★ *If the evidence for an option's stated requirements is missing from
        the bundle, that option is unavailable to you no matter how well it
        describes the company* (the judgement envelope).
        """
        return tuple(lv for lv in self.levels if lv.is_available(extracted))

    @property
    def content_hash(self) -> str:
        """RA-33's mechanism — immutability checked on CONTENT, exactly like FE-2.

        *A rubric edit invalidates every baseline in §7.4* (RM-4), so the version
        must be a fixed referent and a hash is what makes that mechanical.
        """
        payload = json.dumps(
            {"dimension": self.dimension, "version": self.version,
             "levels": [lv.to_json_obj() for lv in self.levels]},
            sort_keys=True, separators=(",", ":"),
        )
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_json_obj(self) -> dict:
        return {"rubric": self.dimension, "version": self.version,
                "levels": [lv.to_json_obj() for lv in self.levels],
                "content_hash": self.content_hash, "note": self.note}
