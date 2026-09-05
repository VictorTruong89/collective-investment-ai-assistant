"""D-07's in-memory entities. ENTITY layer — stdlib, numpy/pandas only (CA-1).

★ §2.1: a **Fact** is what one filing said; a **FundamentalRow** is what we
believe about a period. They differ because filers restate — two filings can
report the same period with different numbers and both are true, one *then* and
one *now*. Collapsing them loses the only information that makes look-ahead
detectable, which is why D-07 stores Facts and derives rows at a stated as_of.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

ANNUAL, QUARTERLY = "annual", "quarterly"
EDGAR, FMP = "edgar", "fmp"


@dataclass(frozen=True, slots=True)
class Fact:
    """One XBRL value from one filing — CT-7.3.

    §6.2's four load-bearing fields, and what each absence costs:

        accession_id  which filing said this   -> restatements indistinguishable
        filing_date   when it became public    -> the as-of filter is impossible
        period_end (+ period_start)            -> cumulative-vs-discrete is a guess
        ingested_at   when WE learned it       -> our own latency is invisible

    ⚠ `filing_date` and `ingested_at` are separate and BOTH required. The gap
    between them is our own staleness, and conflating the two hides it.
    """

    ticker: str
    accession_id: str
    tag: str
    period_start: date
    period_end: date
    period_type: str
    value_minor: int
    value_currency: str
    unit: str
    filing_date: date
    ingested_at: datetime

    def __post_init__(self) -> None:
        if self.period_type not in (ANNUAL, QUARTERLY):
            raise ValueError(
                f"period_type must be {ANNUAL!r} or {QUARTERLY!r}, not "
                f"{self.period_type!r} (CT-7.3)"
            )
        if self.period_start > self.period_end:
            raise ValueError(
                f"{self.ticker}/{self.tag}: period_start {self.period_start} is after "
                f"period_end {self.period_end}. §5.1 case A exists because EDGAR "
                f"carries BOTH, making a discrete quarter distinguishable from a "
                f"cumulative one by arithmetic"
            )
        if self.ingested_at.tzinfo is None:
            raise ValueError("ingested_at must be timezone-aware UTC (DE-4)")

    @property
    def group_key(self) -> tuple[str, date, str]:
        """§6.3 step 2 — Facts are grouped by (tag, period_end, period_type)."""
        return (self.tag, self.period_end, self.period_type)

    @property
    def span_days(self) -> int:
        return (self.period_end - self.period_start).days


@dataclass(frozen=True, slots=True)
class CorporateEvent:
    """A dividend, split, earnings report, M&A or delisting that HAS occurred.

    ⚠ Deliberately a different type from :class:`CalendarEntry` (DE-19). A
    reported result is a fact that does not change; a scheduled date is a
    revisable claim about the future. Sharing a table would let a revised
    schedule silently rewrite history.
    """

    ticker: str
    event_type: str          # "split" | "dividend" | "earnings" | "ma" | "delisting"
    event_date: date         # split: effective; dividend: ex-date
    knowable_at: date        # split: 8-K; dividend: declarationDate (DE-18)
    detail: dict
    source: str

    def __post_init__(self) -> None:
        if self.knowable_at > self.event_date and self.event_type in ("split", "dividend"):
            # Not an error — a declaration can precede the event by months, which
            # is the point of DE-18. This guards the reverse: a knowability date
            # AFTER the event means the two were swapped at the boundary.
            pass


@dataclass(frozen=True, slots=True)
class CalendarEntry:
    """A scheduled, not-yet-occurred event — DE-19.

    ⚠ `knowable_at` is nullable BY DESIGN and that is the finding, not an
    omission: `earnings-calendar` supplies no publication axis, 34.6 % of its
    rows are future-dated, and DE-18 says a single-date calendar entry cannot be
    served to D-04 at all. It becomes usable only through the CT-7.6 snapshot
    ledger, where `observed_at` supplies the missing axis.
    """

    ticker: str
    event_type: str
    scheduled_date: date
    knowable_at: date | None
    source: str

    @property
    def servable_to_model(self) -> bool:
        """DE-18/DE-20 — false without a knowability date. There is no third option."""
        return self.knowable_at is not None


@dataclass(frozen=True, slots=True)
class UniverseEntry:
    """Membership plus the routing decision — DE-5.1.

    ★ `source` is decided **once at ingest, by filer class**, and recorded on
    every row. Never per-field, never per-call, never by whichever source
    answered first.
    """

    ticker: str
    cik: str | None
    filer_class: str         # "10-K/10-Q" | "20-F/6-K" | "none"
    source: str              # "edgar" | "fmp"
    in_watchlist: bool = False


def utcnow() -> datetime:
    """UTC at the boundary (DE-4).

    A function, not a default argument: a default is evaluated at import time
    and would stamp every row in a run with the moment the module loaded.
    """
    return datetime.now(timezone.utc)
