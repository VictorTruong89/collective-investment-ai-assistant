"""F8 `CT-8.1`–`CT-8.6` — the human control surface.

★★ **`QR-16`'s principle: a name the manager asks about gets the FULL analysis
path, at the same depth as the top-1.** Not a cheap tier, not a summary. The
constraint `INV-6` imposes is on **what is actionable**, not on what is analysed
— so depth is preserved and *designation* is what is rationed.

⚠ **`D5`: a designation is never amended.** A revocation is a second journal
entry. ★ Over a year the reversals are behavioural data about the manager's own
discipline, and amending in place deletes exactly the pattern worth seeing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DirectiveState = Literal["DRAFT", "ACTIVE", "EXPIRED", "REJECTED"]


@dataclass(frozen=True, slots=True)
class AnalysisRequest:
    """`CT-8.1` — ⚠ `D1`: a step INSIDE the day's run, not a run of its own.

    ★ `INV-6` — *one actionable recommendation per day* — is enforceable over
    **one** boundary. Separate runs would make "how many recommendations did
    today produce?" a question about how many processes started.
    """

    run_id: str
    ticker: str
    attempt: int
    requested_at: str
    rank_held: int | None = None

    def __post_init__(self) -> None:
        if self.attempt < 2:
            raise ValueError(
                "a drill-down is attempt >= 2 on the day's run (D1, F2 CT-2.7); "
                "attempt 1 is the scheduled analysis")

    @property
    def decision_id(self) -> str:
        return f"{self.run_id}:{self.ticker}:{self.attempt}"


@dataclass(frozen=True, slots=True)
class Designation:
    """`CT-8.2` — journaled to D-11. ⚠ Append-only (`D5`).

    `AC-8.3` — it records **what it displaced**: a designation that does not say
    what it replaced cannot be reviewed later.
    """

    run_id: str
    decision_id: str
    ticker: str
    displaced_decision_id: str | None
    displaced_ticker: str | None
    at: str
    revokes: str | None = None

    @property
    def is_revocation(self) -> bool:
        return self.revokes is not None


class ActionableLimitExceeded(Exception):
    """`AC-8.2` / `INV-6` — ⚠ one actionable recommendation per day."""


class DesignationJournal:
    """Append-only. ⚠ `D5` — a revocation is a SECOND entry, never an edit."""

    def __init__(self) -> None:
        self._entries: list[Designation] = []

    def append(self, d: Designation) -> None:
        if not d.is_revocation and self.actionable_for(d.run_id) is not None:
            raise ActionableLimitExceeded(
                f"{d.run_id} already has an actionable designation. ⚠ INV-6 is one "
                "per DAY, and D1 keeps a drill-down inside the day's run so the "
                "limit is enforceable over one boundary. Revoke first.")
        self._entries.append(d)

    @property
    def entries(self) -> tuple[Designation, ...]:
        return tuple(self._entries)

    def actionable_for(self, run_id: str) -> Designation | None:
        """The standing designation, after revocations."""
        live: dict[str, Designation] = {}
        for e in self._entries:
            if e.run_id != run_id:
                continue
            if e.is_revocation:
                live.pop(e.revokes, None)
            else:
                live[e.decision_id] = e
        return next(iter(live.values()), None)


def control_trace_records(*, run_id: str, request, designation=None,
                          suspended_at: str | None = None,
                          resumed_at: str | None = None) -> tuple[dict, ...]:
    """`AC-8.11` — ★ the request, the suspension, the resume and the
    designation, all joined on the run's `run_id` (`F2` `AC-2.1`).

    ⚠ **The ask is recorded regardless of outcome** (§4). A request that led to
    no designation still produces a record — ★ over a year that is behavioural
    data about the fund manager's own discipline, and `D5` keeps it append-only
    precisely so a reversal stays visible.

    ⚠ `decision_id` is **referenced, never minted here** (`CT-2.7`). A
    drill-down is `attempt >= 2` and mints its own at the start of the analysis;
    if the trace did not carry it, `F7b` could not join an outcome back to the
    analysis the manager actually asked for.
    """
    out = [{"type": "ControlRecord", "event": "request", "run_id": run_id,
            "decision_id": request.decision_id, "ticker": request.ticker,
            "rank_held": request.rank_held, "at": request.requested_at}]
    if suspended_at:
        out.append({"type": "ControlRecord", "event": "suspend",
                    "run_id": run_id, "decision_id": request.decision_id,
                    "at": suspended_at})
    if resumed_at:
        out.append({"type": "ControlRecord", "event": "resume",
                    "run_id": run_id, "decision_id": request.decision_id,
                    "at": resumed_at})
    if designation is not None:
        out.append({"type": "ControlRecord", "event": "designation",
                    "run_id": run_id, "decision_id": designation.decision_id,
                    # ★ `AC-8.3` — the substitution is the fact worth keeping.
                    "displaced_decision_id": designation.displaced_decision_id,
                    "displaced_ticker": designation.displaced_ticker,
                    "at": designation.at})
    return tuple(out)
