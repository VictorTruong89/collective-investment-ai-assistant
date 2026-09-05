"""D-08 §9 — mutual exclusion, cadence claims and checkpoints. OR-24…OR-27, OR-46.

★ **OR-24: the lock's holder is inspectable** — *a stuck lock must be
diagnosable, not mysterious.*

⚠ **A lock is not idempotence.** It stops two runs *overlapping*; it does
nothing about two firings twenty minutes apart. That is OR-46's `cadence_key`,
and the two mechanisms are kept visibly separate here for exactly that reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RunLock:
    """OR-24 — in-process mutual exclusion over written state."""

    _holder: str | None = None
    _since: datetime | None = None

    def holder(self) -> str | None:
        return self._holder

    def acquire(self, run_id: str, *, at: datetime) -> None:
        from src.orchestration.errors import LockHeldError

        if self._holder is not None:
            raise LockHeldError(run_id, f"{self._holder} since {self._since}")
        self._holder, self._since = run_id, at

    def release(self, run_id: str) -> None:
        if self._holder == run_id:
            self._holder, self._since = None, None


@dataclass
class CadenceClaims:
    """★ OR-46 — the window register.

    ⚠ **Only a SUCCESSFUL run claims a window.** A failed one leaves it open, so
    a re-firing can retry the cadence — *or OR-42's redundancy buys nothing
    exactly when it is needed.*
    """

    _claims: dict = field(default_factory=dict)

    def __contains__(self, key: str) -> bool:
        return key in self._claims

    def __getitem__(self, key: str) -> str:
        return self._claims[key]

    def claim(self, key: str, run_id: str, *, status: str) -> bool:
        if status != "SUCCESS":
            return False
        self._claims[key] = run_id
        return True

    def to_json_obj(self) -> dict:
        return dict(self._claims)


@dataclass
class Checkpoints:
    """OR-26 — ★ a resume skips only work with a **durable checkpoint proving
    completion**.

    ⚠ *It never skips a step that failed, and never skips a step whose inputs
    changed* — so the checkpoint records the input digest, not merely the fact.
    """

    _done: dict = field(default_factory=dict)

    def record(self, job_id: str, *, inputs_digest: str) -> None:
        self._done[job_id] = inputs_digest

    def can_skip(self, job_id: str, *, inputs_digest: str) -> bool:
        return self._done.get(job_id) == inputs_digest

    def to_json_obj(self) -> dict:
        return dict(self._done)


@dataclass
class AttemptLog:
    """OR-27 / AC-8.28 — ★ **append-only.** *A retry appends an attempt; it does
    not overwrite the first one.*"""

    _attempts: list = field(default_factory=list)

    def append(self, *, job_id: str, attempt: int, status: str,
               error_code: str | None, elapsed_s: float) -> None:
        self._attempts.append({"job_id": job_id, "attempt": attempt,
                               "status": status, "error_code": error_code,
                               "elapsed_s": elapsed_s})

    def for_job(self, job_id: str) -> tuple:
        return tuple(a for a in self._attempts if a["job_id"] == job_id)

    def to_json_obj(self) -> list:
        return list(self._attempts)
