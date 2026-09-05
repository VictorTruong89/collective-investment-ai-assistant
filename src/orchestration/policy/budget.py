"""D-08 §8 — time budgets. OR-20…OR-23.

⚠ **L0 §4.2 says D-08 "enforces time budgets", and a grep across all four
entrypoints returns zero matches for `retry`, `backoff`, `timeout`, `deadline`
or `time_budget`.** This module is that sentence, implemented.

★ **OR-21: a budget breach FAILS the run. It never truncates the work and emits
the remainder** — *"emit what we have" is the plausible-looking default P5
forbids, because a half-computed slate is more dangerous than no slate: it looks
complete.*
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.orchestration.errors import BudgetExceededError

#: OR-23 — ★ **config, not constants**, and their values are in the manifest.
DEFAULT_RUN_SECONDS = 1800.0


@dataclass(frozen=True, slots=True)
class Budgets:
    """OR-20 — every job declares one; the run declares an overall one."""

    run_seconds: float = DEFAULT_RUN_SECONDS
    per_job: dict = field(default_factory=dict)

    def for_job(self, job_id: str) -> float | None:
        return self.per_job.get(job_id)

    def check_job(self, job_id: str, elapsed_s: float) -> None:
        """OR-22 — ★ a breach records **which job, its budget and its elapsed
        time** — *enough to fix it without rerunning.*"""
        budget = self.for_job(job_id)
        if budget is not None and elapsed_s > budget:
            raise BudgetExceededError(job_id, budget, elapsed_s)

    def check_run(self, elapsed_s: float) -> None:
        if elapsed_s > self.run_seconds:
            raise BudgetExceededError("<run>", self.run_seconds, elapsed_s)

    def to_json_obj(self) -> dict:
        return {"run_seconds": self.run_seconds, "per_job": dict(self.per_job)}
