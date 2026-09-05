"""F2 failure modes. Every one is loud (`P5`)."""

from __future__ import annotations


class TraceError(Exception):
    """Base for every trace failure."""


class TraceImmutableError(TraceError):
    """`AC-2.8` — a written record may not be rewritten.

    ⚠ Inherits `OR-13`'s rule verbatim in spirit: *editing it would let a run's
    recorded inputs be adjusted to match its outputs.* **A trace that can be
    edited is not evidence.**
    """

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(
            f"{key} is already recorded; a trace is append-only (AC-2.8, OR-13). "
            "The original is unchanged."
        )


class IncompleteTrace(TraceError):
    """`AC-2.12` — the log is truncated or the run never closed.

    ⚠ A partial trace that reads as whole is worse than none.
    """


class PayloadsExpired(TraceError):
    """`AC-2.15` / `D2` — payloads were deleted by retention, not lost.

    ★ A run that cannot be replayed *because we deleted something* must say so;
    silence here reads as corruption.
    """

    def __init__(self, run_id: str, expired_at: str) -> None:
        self.run_id, self.expired_at = run_id, expired_at
        super().__init__(
            f"payloads for {run_id} expired {expired_at} (F2 D2 retention). "
            "Decision records and deltas are retained permanently; the raw "
            "request/response bodies replay needs are gone."
        )
