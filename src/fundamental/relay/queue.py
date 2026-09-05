"""D-01 §4B.5/§4B.5a — the relay queue. RA-121, RA-126, RA-127, RA-128.

★ **RA-121 is the split that puts this feature in D-01 rather than SEAT-5:**
*the queue mechanics are deterministic; the priority is D-01's judgement.*
Rotation, coverage and overdue tracking are arithmetic. **What makes a ticker
urgent is a judgement** — so `urgent` arrives as an argument here, and the
arithmetic around it does not know why.

> ✅ **Victor, 2026-08-22:** *"Overdue names go stale. It is my responsibility to
> remember and run it later."*

★ That needs **no new mechanism**: it is RA-120's event-relative staleness doing
its job, with the queue kept honest about the consequence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: Why a name is on today's slice. ★ `rotation` is the default and the reason
#: coverage is even by construction; the rest are RA-121's judgement overrides.
ROTATION = "rotation"
OVERRIDE_REASONS = (
    "event_landed", "falsifier_approaching", "unexplained_residual",
    "8k_escalation", "sector_file_moved",
)


@dataclass(frozen=True, slots=True)
class QueueEntry:
    """One name on the relay queue, with its age.

    ⚠ **RA-126: an overdue relay is not a backlog item — it is a thesis going
    stale.** A queued name that is not run ages until its thesis crosses RA-71's
    test, at which point the thesis is marked stale on the card exactly as any
    other stale thesis is. ★ **The queue never absorbs the consequence on the
    thesis's behalf** — *a name sitting in a queue is not a name that has been
    analysed.*
    """

    ticker: str
    last_relayed_on: date | None
    queued_since: date
    reason: str = ROTATION
    #: ⚠ Recorded, and **deliberately not an input to any ordering** (RA-127).
    times_skipped: int = 0

    def age_days(self, as_of: date) -> int:
        return (as_of - self.queued_since).days

    def to_json_obj(self, as_of: date) -> dict:
        return {"ticker": self.ticker, "reason": self.reason,
                "queued_since": self.queued_since.isoformat(),
                "age_days": self.age_days(as_of),
                "last_relayed_on": self.last_relayed_on.isoformat()
                                   if self.last_relayed_on else None,
                "times_skipped": self.times_skipped}


@dataclass(frozen=True, slots=True)
class QueueReport:
    """★ RA-128 / AC-1.82 — `overdue` and `stale` are **separate counts**.

    ⚠ *Not yet run* and *no longer trusted* are different states, and
    **collapsing them hides the moment one became the other.**
    """

    as_of: date
    today: tuple[QueueEntry, ...]
    returned: tuple[str, ...]
    overdue: tuple[QueueEntry, ...]
    stale: tuple[str, ...]
    #: Everything still queued. ★ RA-128 — an overdue entry **ages in place and
    #: is never silently dropped to make room.**
    carried: tuple[QueueEntry, ...] = ()

    def to_json_obj(self) -> dict:
        return {
            "as_of": self.as_of.isoformat(),
            "queued": [e.to_json_obj(self.as_of) for e in self.today],
            "returned": list(self.returned),
            "overdue": [e.to_json_obj(self.as_of) for e in self.overdue],
            "stale": list(self.stale),
            "counts": {"queued": len(self.today), "returned": len(self.returned),
                       "overdue": len(self.overdue), "stale": len(self.stale)},
            # ★ RA-127 — the system reports; it does not chase.
            "chases": False,
        }


def _rotation_key(entry: QueueEntry):
    """Oldest-first over names with a live thesis, so coverage is even.

    ⚠ **RA-127: `times_skipped` is absent from this key, deliberately.** *No
    re-prioritising a name because it was skipped* — skipping is a decision
    SEAT-1 is entitled to make, and a queue that pesters is a system asserting
    authority it does not hold.
    """
    return (entry.last_relayed_on or date.min, entry.queued_since, entry.ticker)


def derive_queue(entries, *, as_of: date, per_day: int = 3, urgent=(),
                 overdue_after_days: int = 7, stale_tickers=()) -> QueueReport:
    """★ **The queue is re-derived every run, not consumed** (§4B.5).

    *A ticker that becomes urgent overtakes; nothing is "already scheduled" in a
    way that resists new evidence.* `urgent` is D-01's judgement, applied here as
    a set — this function never decides what is urgent, only what that means for
    the ordering.
    """
    urgent = set(urgent)
    pool = tuple(entries)
    ordered = sorted(
        pool, key=lambda e: (0 if e.ticker in urgent else 1, *_rotation_key(e)))

    today = tuple(ordered[:per_day])
    overdue = tuple(e for e in pool if e.age_days(as_of) >= overdue_after_days)
    stale = tuple(sorted({t for t in stale_tickers
                          if t in {e.ticker for e in pool}}))
    return QueueReport(as_of=as_of, today=today, returned=(), overdue=overdue,
                       stale=stale, carried=pool)


def relay_staleness(thesis, as_of: date, *, events=(), last_relayed_on=None,
                    depends_on=()):
    """RA-120 / AC-1.81 — ★ relay staleness is **event-relative**.

    *A relay report is stale when a scheduled event it depends on has occurred,
    not when a timer expires.* ★ This is the half Victor described as *"D-01
    just needs to search, re-evaluate and update if the report is too old"* —
    **and it already exists**: `calendar/staleness.py`, unchanged.
    """
    from datetime import datetime, time, timezone

    from src.fundamental.calendar.staleness import staleness

    last_check = (datetime.combine(last_relayed_on, time.min, tzinfo=timezone.utc)
                  if last_relayed_on else None)
    return staleness(thesis, as_of, events=events, last_check_at=last_check,
                     depends_on=depends_on)
