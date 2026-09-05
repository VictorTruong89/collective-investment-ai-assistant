"""D-01 §10A — the scheduled calendar, as D-01 sees it.

★ **A scheduled event is evidence about the FUTURE** (RA-69). D-07 already
models it as an entity distinct from an occurred `CorporateEvent` (DE-19) and
carries its two dates (DE-18); this module is D-01's consumption of that, and
the one thing it adds is the rule that **none of it may become a fact**.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime

#: RA-70 — a confirmed date and a vendor-estimated date are different fields.
#: ⚠ D-07 measured it: **34.6 % of `earnings-calendar` rows are future-dated**,
#: and most vendor dates are estimates until the company announces.
CONFIRMED = "confirmed"
ESTIMATED = "vendor_estimated"
DATE_STATUSES = (CONFIRMED, ESTIMATED)

#: RA-77 — macro and FOMC events are book-level; everything else is per name.
SCOPE_TICKER = "ticker"
SCOPE_BOOK = "book"

#: The event classes that are never written per ticker (RA-77).
BOOK_LEVEL_CLASSES = frozenset({"fomc", "cpi", "pce", "payrolls", "macro"})

#: RA-74 — the three states an outcome may leave a falsifier in. There is no
#: fourth, and in particular there is no "confirms the thesis".
FIRES, CLEARS, UNDETERMINED = "fires", "clears", "undetermined"
FALSIFIER_STATES = (FIRES, CLEARS, UNDETERMINED)


@dataclass(frozen=True, slots=True)
class CalendarEvent:
    """D-07's `CalendarEntry`, consumed. Never a `Claim`'s evidence (RA-69)."""

    event_class: str            # "earnings" | "fomc" | "cpi" | …
    scheduled_date: date
    knowable_at: datetime       # DE-18's second date — when we learned of it
    date_status: str = ESTIMATED
    ticker: str = ""
    entry_ref: str = ""

    def __post_init__(self) -> None:
        if self.date_status not in DATE_STATUSES:
            raise ValueError(
                f"date_status {self.date_status!r} is neither {CONFIRMED!r} nor "
                f"{ESTIMATED!r} — RA-70 requires the two be distinguishable"
            )
        if self.scope == SCOPE_TICKER and not self.ticker:
            raise ValueError(f"{self.event_class!r} is per-name and names no ticker")

    @property
    def scope(self) -> str:
        return SCOPE_BOOK if self.event_class in BOOK_LEVEL_CLASSES else SCOPE_TICKER

    @property
    def is_confirmed(self) -> bool:
        return self.date_status == CONFIRMED

    def render_date(self) -> str:
        """RA-70 — the two render differently, and that is the point.

        ⚠ *An estimated date presented as confirmed produces a pre-event brief
        written for the wrong week.*
        """
        if self.is_confirmed:
            return self.scheduled_date.isoformat()
        return f"~{self.scheduled_date.isoformat()} (estimated)"

    def to_json_obj(self) -> dict:
        return {"event_class": self.event_class, "ticker": self.ticker,
                "scheduled_date": self.scheduled_date.isoformat(),
                "knowable_at": self.knowable_at.isoformat(),
                "date_status": self.date_status, "scope": self.scope,
                "entry_ref": self.entry_ref, "rendered_date": self.render_date()}


@dataclass(frozen=True, slots=True)
class StalenessState:
    """RA-71/RA-72 — the two markings the card carries, and why each fired.

    ★ `stale` and `pre_event` are **not opposites and not exclusive**: a thesis
    can be stale for a read event and provisional against the next one.
    """

    stale: bool
    basis: str                  # "event" | "clock" | "fresh"
    reason: str = ""
    driving_event: CalendarEvent | None = None
    pre_event: bool = False
    pre_event_date: date | None = None
    pre_event_class: str = ""

    def to_json_obj(self) -> dict:
        return {
            "stale": self.stale, "basis": self.basis, "reason": self.reason,
            "pre_event": self.pre_event,
            "pre_event_date": self.pre_event_date.isoformat()
                              if self.pre_event_date else None,
            "pre_event_class": self.pre_event_class,
            "driving_event": self.driving_event.to_json_obj()
                             if self.driving_event else None,
        }


@dataclass(frozen=True, slots=True)
class OutcomeMapping:
    """RA-74 — one *outcome → falsifier state* row. The brief is made of these."""

    outcome: str                # an observable result, not a prediction of one
    falsifier_ordinal: int
    falsifier_state: str

    def __post_init__(self) -> None:
        if self.falsifier_state not in FALSIFIER_STATES:
            raise ValueError(
                f"falsifier_state {self.falsifier_state!r} is not one of "
                f"{FALSIFIER_STATES} — a brief maps outcomes to states (RA-74)"
            )

    def to_json_obj(self) -> dict:
        return {"outcome": self.outcome,
                "falsifier_ordinal": self.falsifier_ordinal,
                "falsifier_state": self.falsifier_state}


@dataclass(frozen=True, slots=True)
class PreEventBrief:
    """RA-73…RA-75 — written before the event, hashed, immutable after it.

    ★ *J-15's falsifier machinery aimed at a known date.* It converts a
    scheduled release into a test the thesis can fail — and **its entire value
    is the possibility of being wrong in public** (RA-73).
    """

    brief_id: str
    event: CalendarEvent
    authored_at: datetime
    thesis_version: int
    outcome_map: tuple[OutcomeMapping, ...]
    #: RA-75 — mandatory. *A quarterly result is over-read by default, and the
    #: only moment at which naming the limit is free is before the number exists.*
    will_not_tell_you: tuple[str, ...] = ()
    ticker: str = ""
    scope: str = SCOPE_TICKER
    brief_hash: str = field(default="", compare=False)

    def to_json_obj(self) -> dict:
        return {
            "brief_id": self.brief_id, "ticker": self.ticker,
            "scope": self.scope, "thesis_version": self.thesis_version,
            "event": self.event.to_json_obj(),
            "authored_at": self.authored_at.isoformat(),
            "outcome_map": [o.to_json_obj() for o in self.outcome_map],
            "will_not_tell_you": list(self.will_not_tell_you),
        }

    def compute_hash(self) -> str:
        """RA-73 — the pre-commitment, hashed before the event (RA-36's rule)."""
        payload = json.dumps(self.to_json_obj(), sort_keys=True,
                             separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def assert_not_cited_as_fact(claim, calendar_refs) -> None:
    """RA-69 / AC-1.41 — a `Claim` may not rest on a scheduled event.

    ★ *"Earnings are on the 24th"* is not a reason for anything. A scheduled
    event is evidence about the **future**; it travels in its own `calendar`
    block carrying `knowable_at`, and a claim of kind `fact` or `inference`
    that cites one has treated a revisable schedule as a filing.
    """
    from src.fundamental.errors import CalendarCitedAsFactError

    # ★ Only `fact` and `inference` can reach here at all: S-3 already forbids an
    # `assumption` from carrying a span, so **two independent rules close this**.
    refs = {r for r in calendar_refs if r}
    doc = getattr(claim.span, "accession_id", "") if claim.span else ""
    if doc and doc in refs:
        raise CalendarCitedAsFactError(f"#{claim.ordinal}", doc)
