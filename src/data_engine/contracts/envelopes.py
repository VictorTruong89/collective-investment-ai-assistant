"""CT-7.5 provenance envelope and CT-7.7 calendar-check report — the JSON shapes.

Both travel WITH an artifact rather than being stored beside it, because the
question each answers is only ever asked about a specific artifact: "where did
this number come from" and "what happened to its meaning inside the window".
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class Provenance:
    """CT-7.5 — every served artifact carries this (AC-7.18, AC-7.38).

    `pit_guarantee` is the field DE-23 forces into existence. The guarantee is
    **strictly weaker for FMP-routed tickers**: EDGAR filings are immutable and
    separately addressable so §6.3 reconstructs; FMP serves one answer, today's,
    and if a number changed the old value is gone with nothing in the response
    indicating it. A consumer computing a backtest is entitled to know which it
    has.

    `plan_gate_attempts` carries DE-46's count to the run record — the half of
    L4 EH-14 that the 402 classification probe has to answer.
    """

    source: str                     # "edgar" | "fmp"
    as_of: date
    fetched_at: datetime            # UTC
    pit_guarantee: str              # "reconstructed" | "best_effort"
    fx_rate_used: dict | None = None
    adj_as_of: date | None = None
    warnings: tuple[str, ...] = ()  # WARNING_CODES values that fired
    plan_gate_attempts: int = 0

    RECONSTRUCTED = "reconstructed"
    BEST_EFFORT = "best_effort"

    def __post_init__(self) -> None:
        if self.pit_guarantee not in (self.RECONSTRUCTED, self.BEST_EFFORT):
            raise ValueError(
                f"pit_guarantee must be {self.RECONSTRUCTED!r} or {self.BEST_EFFORT!r}, "
                f"not {self.pit_guarantee!r} — DE-23 requires the artifact to SAY "
                f"which guarantee it carries, and a third value says neither"
            )

    def to_json_obj(self) -> dict:
        obj = asdict(self)
        obj["as_of"] = self.as_of.isoformat()
        obj["fetched_at"] = self.fetched_at.isoformat()
        obj["adj_as_of"] = self.adj_as_of.isoformat() if self.adj_as_of else None
        obj["warnings"] = list(self.warnings)
        return obj


# --------------------------------------------------------------------------- #
# CT-7.7 — the calendar-check report
# --------------------------------------------------------------------------- #

#: The four severities of §6A.2. Distinct from DE-12's ACCEPT/FLAG/REJECT, which
#: classifies individual ROWS: a row can be perfectly valid and still sit inside
#: a window this gate blocks.
BLOCK, FLAG, NOTE, UNCHECKED = "BLOCK", "FLAG", "NOTE", "UNCHECKED"

#: CT-7.7 verdicts.
PROCEED, PROCEED_WITH_FLAGS, HALT = "PROCEED", "PROCEED_WITH_FLAGS", "HALT"


@dataclass(frozen=True, slots=True)
class Finding:
    """One corporate action inside the window.

    `knowable_at` is the knowability date and **not** the event date (DE-34). A
    split announced after `as_of` is absent from the report even though it is in
    today's `splits` response — the check is itself point-in-time.
    """

    ticker: str
    event_class: str
    severity: str
    event_date: date
    knowable_at: date
    detail: dict
    source: str
    handled: bool = False
    handling: str | None = None

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "class": self.event_class, "severity": self.severity,
            "event_date": self.event_date.isoformat(),
            "knowable_at": self.knowable_at.isoformat(),
            "detail": self.detail, "source": self.source,
            "handled": self.handled, "handling": self.handling,
        }


@dataclass(frozen=True, slots=True)
class CalendarCheckReport:
    """CT-7.7 — one report per run, referenced by every artifact it produces.

    ⚠ `class_status` must contain **every one of §6A.2's 17 classes**. A class
    missing from the map is a defect, not an implied pass — that is DE-35, and
    it is the rule this whole section exists for. Every other rule here fails
    safe by halting; DE-35 fails safe by *admitting ignorance*, and it is the
    one an implementation is tempted to skip because an empty list is so much
    easier to return than a tri-state.
    """

    run_id: str
    as_of: date
    adj_as_of: date | None
    window_start: date
    window_end: date
    universe_size: int
    class_status: dict          # class name -> "CHECKED" | "UNCHECKED: <why>"
    findings: tuple[Finding, ...] = ()
    checked_at: datetime | None = None
    probe: dict | None = field(default=None)

    @property
    def blocked(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == BLOCK and not f.handled)

    @property
    def verdict(self) -> str:
        if self.blocked:
            return HALT
        if any(f.severity == FLAG for f in self.findings):
            return PROCEED_WITH_FLAGS
        return PROCEED

    @property
    def report_id(self) -> str:
        """The handle FE-10's `calendar_check_id` refers to."""
        return f"{self.run_id}:{self.as_of.isoformat()}"

    def to_json_obj(self) -> dict:
        return {
            "run_id": self.run_id,
            "report_id": self.report_id,
            "as_of": self.as_of.isoformat(),
            "adj_as_of": self.adj_as_of.isoformat() if self.adj_as_of else None,
            "window": {"start": self.window_start.isoformat(),
                       "end": self.window_end.isoformat()},
            "universe_size": self.universe_size,
            "verdict": self.verdict,
            "class_status": dict(self.class_status),
            "findings": [f.to_json_obj() for f in self.findings],
            "blocked_tickers": sorted({f.ticker for f in self.blocked}),
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
            "probe": self.probe,
        }
