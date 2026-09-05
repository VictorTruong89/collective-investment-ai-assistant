"""The rubric registry — published, versioned, immutable (RA-33, AC-1.31)."""

from __future__ import annotations

from src.fundamental.errors import RubricMutatedError
from src.fundamental.scorecard.models import DIMENSIONS, Rubric


class RubricRegistry:
    """Keyed on `(dimension, version)`. ★ There is no "the moat rubric".

    The same argument as D-02's `ContractRegistry`: a model scored against a
    rubric that cannot be named at a version cannot be compared with anything.
    """

    def __init__(self, rubrics=()) -> None:
        self._by_key: dict[tuple[str, int], Rubric] = {}
        for rubric in rubrics:
            self.publish(rubric)

    def publish(self, rubric: Rubric) -> Rubric:
        key = (rubric.dimension, rubric.version)
        existing = self._by_key.get(key)
        if existing is not None:
            if existing.content_hash != rubric.content_hash:
                raise RubricMutatedError(rubric.rubric_id, existing.content_hash,
                                         rubric.content_hash)
            return existing                    # idempotent republish
        self._by_key[key] = rubric
        return rubric

    def get(self, dimension: str, version: int) -> Rubric:
        hit = self._by_key.get((dimension, version))
        if hit is None:
            raise KeyError(
                f"no rubric {dimension}@v{version}; published: "
                f"{sorted(f'{d}@v{v}' for d, v in self._by_key)}"
            )
        return hit

    def assert_complete(self) -> None:
        """★ RA-52 — all four dimensions, or the scorecard is not a scorecard.

        ⚠ A partial scorecard would still render, and a reader has no way to tell
        a dimension that scored low from one that was never assessed — the same
        shape as D-07 **DE-35** and D-05 **RK-36**.
        """
        missing = [d for d in DIMENSIONS if not any(k[0] == d for k in self._by_key)]
        if missing:
            raise KeyError(
                f"no rubric published for {missing}. The dimension set is closed and "
                f"complete (RA-52); a missing dimension is indistinguishable from a "
                f"low-scoring one on the card"
            )

    @property
    def published(self) -> list[str]:
        return sorted(f"{d}@v{v}" for d, v in self._by_key)
