"""F2 `CT-2.6` / `T6` — linking a decision to what actually happened.

★★ **This is what makes a Tier-B study (`F7b`) possible years after the
decision.** An outcome resolves weeks or months later, in a different process,
long after the run directory stopped being interesting — so the link is keyed by
`decision_id` alone and **never re-derives the id from run contents**
(`AC-2.7`). Re-deriving would tie the join to a run's internals, which change.

⚠ **Append-only, like every other trace record.** An outcome that can be edited
after the fact is exactly the record an unfavourable result would get edited out
of. `PG-5.2`'s counterfactual arm is only worth something if nobody can adjust it.

★ Stored **outside** the run directory, because `D2` expires run payloads while
outcomes must outlive them by years.
"""

from __future__ import annotations

import json
import pathlib
from collections.abc import Iterator
from typing import Any

from src.orchestration.trace.errors import TraceImmutableError


class OutcomeStore:
    """Append-only `decision_id → realised outcome`. One file, all runs."""

    def __init__(self, root: str | pathlib.Path) -> None:
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "outcomes.jsonl"

    def link(self, decision_id: str, resolved_at: str, outcome: Any) -> None:
        """`T6` — attach a realised outcome to a past decision.

        ⚠ Raises on a second link for the same `decision_id`: a decision has one
        realised outcome, and a second write is either a bug or a correction —
        both of which must be visible rather than silently applied.
        """
        if not decision_id:
            raise ValueError("an outcome link needs a decision_id (CT-2.6, AC-2.7)")
        if not resolved_at:
            raise ValueError("resolved_at is required — an undated outcome cannot be studied")
        if decision_id in {r["decision_id"] for r in self.read_all()}:
            raise TraceImmutableError(f"outcome:{decision_id}")
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"decision_id": decision_id,
                                 "resolved_at": resolved_at,
                                 "outcome": outcome}, default=str) + "\n")

    def read_all(self) -> Iterator[dict]:
        if not self.path.exists():
            return iter(())
        return iter([json.loads(line) for line
                     in self.path.read_text(encoding="utf-8").splitlines()
                     if line.strip()])

    def for_decision(self, decision_id: str) -> dict | None:
        return next((r for r in self.read_all() if r["decision_id"] == decision_id), None)
