"""`T1` — base rates for one subject, as of one date (`CT-F11.2`).

★ **Inputs come through D-07** (`FE-23`): the caller reads each member's annual rows from
the fact ledger and passes them through `F10`'s `annual_history` — the subject's own `D6`
formula and point-in-time filter (`AC-F11.2`, `AC-F11.3`). This module only selects years
and counts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from src.feature_engineer.base_rates.stats import (
    margin_reach,
    positive_runs,
    published_bracket,
    revenue_cagr_reach,
)
from src.feature_engineer.valuation.normalised import annual_history


def _filed(year) -> date | None:
    stamps = [i.get("filing_date") for i in (year.basis.inputs or ()) if i.get("filing_date")]
    return max(stamps) if stamps else None


def member_years(history: dict, *, as_of: date, ranges: dict) -> tuple[dict, list]:
    """`(used, excluded)` — usable years per member inside its declared range, and every
    year that could not be used, named with its reason (never zero, `FE-14`).

    ⚠ One fiscal year can arrive as several annual rows (a 0-day or quarter-length span
    labelled annual); a usable one wins, and the year is excluded only if none is usable.
    """
    used, excluded = {}, []
    for member, years in history.items():
        low, high = ranges.get(member, (None, None))
        usable, reasons = {}, {}
        for y in years:
            if (low is not None and y.fiscal_year < low) or (high is not None and
                                                             y.fiscal_year > high):
                continue
            if y.basis is None:
                reasons.setdefault(y.fiscal_year, y.unavailable)
                continue
            filed = _filed(y)
            if filed is not None and filed > as_of:              # `AC-F11.2` — belt and braces
                continue
            usable[y.fiscal_year] = y
        used[member] = [usable[k] for k in sorted(usable)]
        excluded += [{"member": member, "fiscal_year": fy, "reason": why}
                     for fy, why in sorted(reasons.items()) if fy not in usable]
    return used, excluded


def history_from_rows(rows_by_member: dict, *, as_of: date) -> dict:
    """D-07 annual rows per member → `F10` `annual_history` (the ONE formula, `FE-25`)."""
    return {m: annual_history(rows, ticker=m, as_of=as_of) for m, rows in rows_by_member.items()}


def thresholds_from(trail: dict) -> dict:
    """`AC-F11.5` — every threshold is a value from the subject's `implied_by_duration`."""
    rows = trail.get("implied_by_duration")
    if not rows:
        raise ValueError("base rates need the subject's F10 implied_by_duration (a set with a "
                         "duration table, D10) — none in this trail")
    solved = [r for r in rows if r.get("status") == "SOLVED"]
    return {"margin": [(int(r["explicit_years"]), Decimal(r["share_of_trailing_revenue"]))
                       for r in solved if r.get("share_of_trailing_revenue") is not None],
            "growth": [(int(r["explicit_years"]), Decimal(r["value"])) for r in solved],
            "runs": [int(r["explicit_years"]) for r in rows]}


@dataclass(frozen=True, slots=True)
class BaseRates:
    reference_class: dict
    as_of: date
    subject: str
    member_years: list
    excluded_years: list
    margin_reach: list
    positive_runs: list
    revenue_cagr_reach: list
    published: dict | None = None
    members: list = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "class": self.reference_class, "as_of": self.as_of.isoformat(),
            "subject": self.subject, "members": self.members,
            "member_years": self.member_years, "excluded_years": self.excluded_years,
            "margin_reach": self.margin_reach, "positive_runs": self.positive_runs,
            "revenue_cagr_reach": self.revenue_cagr_reach, "published": self.published},
            sort_keys=True, separators=(",", ":"), default=str)


def compute(*, reference_class, history: dict, subject: str, as_of: date, trail: dict,
            published=None, ranges: dict | None = None) -> BaseRates:
    t = thresholds_from(trail)
    used, excluded = member_years(history, as_of=as_of,
                                  ranges=reference_class.ranges() if ranges is None else ranges)
    pub = None
    if published is not None:
        pub = {"source": published.source, "measure": published.measure,
               "reference_class": published.reference_class,
               "rows": [{"periods": p, "required_growth": str(g),
                         "bracket": published_bracket(published, p, g),
                         "pages": next(({"observations": h["page"], "rates": h["rates_page"]}
                                        for h in published.horizons
                                        if int(h["years"]) == p), None)}
                        for p, g in t["growth"]]}
    return BaseRates(
        reference_class=(reference_class.cite() if hasattr(reference_class, "cite") else
                         {"name": reference_class.name, "version": reference_class.version,
                          "content_hash": reference_class.content_hash}),
        as_of=as_of, subject=subject,
        members=[{"label": m.label, "name": m.name, "role": m.role, "why": m.why}
                 for m in getattr(reference_class, "members", ())],
        member_years=[{"member": m, "fiscal_year": y.fiscal_year,
                       "fcff": y.basis.fcff.to_json_obj(),
                       "revenue": y.basis.revenue.to_json_obj(),
                       "fcff_margin": str(y.margin), "filing_date": _filed(y),
                       # `AC-F11.9` — every figure traces to the filings it came from
                       "accession_ids": sorted({i["accession_id"] for i in y.basis.inputs
                                                if i.get("accession_id")})}
                      for m, years in used.items() for y in years],
        excluded_years=excluded,
        margin_reach=margin_reach(used, t["margin"], subject=subject),
        positive_runs=positive_runs(used, t["runs"], subject=subject),
        revenue_cagr_reach=revenue_cagr_reach(used, t["growth"], subject=subject),
        published=pub)
