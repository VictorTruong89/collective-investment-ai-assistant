"""D-01 §10B.5 — vintages and the industry term. RA-93, RA-93a, RA-94.

★★ **A comparison against a released series uses the print that existed on the
date, never the current revised value** (RA-93). ⚠ Comparing a dated assumption
against a revised figure is a look-ahead of exactly the class this project keeps
finding: `_cumulative_fys` 41.5 %, FMP TTM 71 %, `historical-market-capitalization`
~28 days.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.fundamental.errors import ResearchError

#: ★ RA-93 — **vintages are OBTAINABLE for the series that matter**, and the
#: rule must say so. ALFRED publishes as-first-released values via
#: `realtime_start`/`realtime_end`, free, over the FRED API. ⚠ *FMP's
#: `economic-indicators` is the vendor that cannot, not the world* — recording
#: it as universally unavailable would permanently downgrade a check that is
#: free for exactly the series that matter.
ALFRED_COVERED = frozenset({
    "CPIAUCSL", "CPILFESL", "PCEPI", "PCEPILFE", "INDPRO",
    "DGS2", "DGS10", "DGS30", "GDP", "PAYEMS", "UNRATE",
})

#: RA-93a — ★ **the primary macro variable needs no external vintage service at
#: all.** Hyperscaler capex guidance is *company disclosure*, so its vintage is
#: its filing date and D-07's `knowable_at` already carries it (DE-18); treasury
#: rates are market prices and are not revised. **The ALFRED dependency is
#: narrow — CPI, PCE, industrial production — and must not be allowed to gate
#: the capex work that does not need it.**
NO_VINTAGE_SERVICE_NEEDED = frozenset({"company_disclosure", "market_price"})

VINTAGE_CHECKED, REVISED_SERIES = "vintage_checked", "revised_series"
GRADE_UNCHECKED = "UNCHECKED"


@dataclass(frozen=True, slots=True)
class SeriesComparison:
    """One comparison of a dated assumption against a released series."""

    series_id: str
    comparison_date: date
    value_used: float
    kind: str = "released_series"      # or a `NO_VINTAGE_SERVICE_NEEDED` kind
    vintage_date: date | None = None   # ALFRED's `realtime_start`
    knowable_at: date | None = None    # DE-18, for company disclosure

    @property
    def basis(self) -> str:
        if self.kind in NO_VINTAGE_SERVICE_NEEDED:
            return VINTAGE_CHECKED
        return VINTAGE_CHECKED if self.vintage_date else REVISED_SERIES

    @property
    def grade(self) -> str:
        """RA-93 — `revised_series` is UNCHECKED-grade, never silently used."""
        return "" if self.basis == VINTAGE_CHECKED else GRADE_UNCHECKED

    def to_json_obj(self) -> dict:
        return {"series_id": self.series_id,
                "comparison_date": self.comparison_date.isoformat(),
                "value_used": self.value_used, "kind": self.kind,
                "basis": self.basis, "grade": self.grade,
                "vintage_date": self.vintage_date.isoformat()
                                if self.vintage_date else None,
                "knowable_at": self.knowable_at.isoformat()
                               if self.knowable_at else None}


def grade_comparison(comparison: SeriesComparison) -> SeriesComparison:
    """AC-1.60 / AC-1.65 — vintage-checked where ALFRED covers it, else UNCHECKED.

    ⚠ A covered series arriving with no vintage is an **error, not a
    downgrade**: the vintage is free for that series, and accepting
    `revised_series` there would permanently lower a check nobody had to lose.
    """
    if comparison.kind in NO_VINTAGE_SERVICE_NEEDED:
        if comparison.kind == "company_disclosure" and comparison.knowable_at is None:
            raise ResearchError(
                f"{comparison.series_id}: company disclosure with no "
                f"`knowable_at` — its vintage IS its filing date, and D-07 "
                f"already carries it (RA-93a, DE-18)"
            )
        return comparison
    if comparison.series_id in ALFRED_COVERED and comparison.vintage_date is None:
        raise ResearchError(
            f"{comparison.series_id}: ALFRED publishes an as-first-released "
            f"value for this series via realtime_start/realtime_end, free. "
            f"Grading it `revised_series` would permanently downgrade a check "
            f"that is obtainable (RA-93)"
        )
    return comparison


@dataclass(frozen=True, slots=True)
class PeerContext:
    """RA-94 — D-02's peer set, consumed with its arithmetic trail.

    ★ **D-01 does not assemble a peer set and does not choose one** — *a chosen
    peer set is a conclusion wearing a denominator.* There is deliberately no
    function in `src/fundamental/` that selects peers; this contract can only be
    received.
    """

    industry: str
    period: str
    members: tuple[str, ...]
    median: float
    trail_ref: str
    source: str = "D-02"

    def __post_init__(self) -> None:
        if self.source != "D-02":
            raise ResearchError(
                f"peer context sourced from {self.source!r} — the industry term "
                f"comes from D-02's `peer_context` at matching periods, with its "
                f"arithmetic trail (RA-94, RA-45, D-02 §6.2)"
            )
        if not self.trail_ref:
            raise ResearchError(
                f"peer context for {self.industry!r} carries no arithmetic "
                f"trail (RA-45)"
            )
