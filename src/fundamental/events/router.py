"""D-01 §10B.3 — the 8-K item-code router. RA-82, RA-83, RA-84, RA-138.

★ **8-K item numbers are semantically typed by the SEC**, so this is a lookup,
not a classification. ⚠ Asking a model to classify what the form declares is the
reverse of AP-5 — the answer is already in the filing header.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from src.fundamental.errors import EvidenceWithdrawnError

#: Severities, most severe first. `WITHDRAW` exists for exactly one item.
WITHDRAW, ESCALATE, POST_EVENT, TRIAGE, NOTE = (
    "withdraw", "escalate", "post_event", "cheap_triage", "note",
)
_ORDER = {WITHDRAW: 4, ESCALATE: 3, POST_EVENT: 2, TRIAGE: 1, NOTE: 0}


@dataclass(frozen=True, slots=True)
class Route:
    severity: str
    meaning: str
    note: str = ""
    #: RA-84 — only `7.01`/`8.01` and news reach a model at all.
    to_cheap_tier: bool = False
    #: Rows that escalate only when the thesis names the thing that changed.
    conditional_on: str = ""


#: §10B.3's table, verbatim. ★ Adding a row is a spec change, not a code change.
ITEM_ROUTES = {
    "4.02": Route(WITHDRAW, "non-reliance on previously issued financial statements",
                  "⛔ the highest severity in this system — RA-83"),
    "4.01": Route(ESCALATE, "change in certifying accountant",
                  "pair with E-09 `ap.auditor`"),
    "2.02": Route(POST_EVENT, "results of operations",
                  "→ the post-event read (§10A.4) — V-01/V-02 unchanged"),
    "1.01": Route(ESCALATE, "entry into a material agreement",
                  conditional_on="counterparty_or_contract"),
    "1.02": Route(ESCALATE, "termination of a material agreement",
                  conditional_on="counterparty_or_contract"),
    "2.01": Route(ESCALATE, "acquisition or disposition of assets"),
    "2.05": Route(ESCALATE, "costs associated with exit or disposal activities"),
    "2.06": Route(ESCALATE, "material impairment",
                  "★ management scoring its own capital allocation"),
    "3.01": Route(ESCALATE, "delisting notice / listing-rule failure"),
    "5.02": Route(ESCALATE, "departure or appointment of directors and officers",
                  conditional_on="capital_allocation_names_individual"),
    "1.05": Route(ESCALATE, "material cybersecurity incident"),
    "7.01": Route(TRIAGE, "Regulation FD disclosure", to_cheap_tier=True),
    "8.01": Route(TRIAGE, "other events",
                  "★ where the genuinely unexpected lands, unstructured by design",
                  to_cheap_tier=True),
}

#: An item the table does not know. ⚠ Not an error and not a silent drop: an
#: unknown code is triaged as unstructured text, which is what it is.
UNKNOWN_ROUTE = Route(NOTE, "item not in §10B.3's table", "logged, not escalated")


@dataclass(frozen=True, slots=True)
class Routing:
    """What the table said about one filing. No LLM was involved (RA-82)."""

    ref: str
    items: tuple[str, ...]
    routes: tuple[Route, ...]

    @property
    def severity(self) -> str:
        return max((r.severity for r in self.routes),
                   key=lambda s: _ORDER[s], default=NOTE)

    @property
    def withdraws_evidence(self) -> bool:
        return self.severity == WITHDRAW

    @property
    def to_cheap_tier(self) -> tuple[str, ...]:
        return tuple(i for i, r in zip(self.items, self.routes) if r.to_cheap_tier)

    def to_json_obj(self) -> dict:
        return {"ref": self.ref, "items": list(self.items),
                "severity": self.severity,
                "routes": [{"item": i, "severity": r.severity,
                            "meaning": r.meaning, "cheap_tier": r.to_cheap_tier}
                           for i, r in zip(self.items, self.routes)]}


def route_filing(ref: str, items) -> Routing:
    """RA-82 — a pure function of the item numbers. Deterministic, free, no call."""
    codes = tuple(str(i).strip() for i in items)
    return Routing(ref=ref, items=codes,
                   routes=tuple(ITEM_ROUTES.get(c, UNKNOWN_ROUTE) for c in codes))


# --------------------------------------------------------------------------- #
# RA-83 / RA-138 — item 4.02 withdraws the EXTRACTIONS, not merely the thesis
# --------------------------------------------------------------------------- #

def _overlaps(period, affected) -> bool:
    """Does an extracted item's period intersect a withdrawn range?

    ⚠ RA-138: **an item with NO period is withdrawn by any non-reliance
    filing.** An undated fact cannot be shown to lie outside the affected range,
    and RA-83's whole point is that the evidence was withdrawn.
    """
    if period is None:
        return True
    start = period.start or period.end
    for lo, hi in affected:
        if start <= hi and period.end >= lo:
            return True
    return False


def normalise_periods(affected) -> tuple[tuple[str, str], ...]:
    """`Period` objects or `(start, end)` pairs → sorted ISO ranges."""
    out = []
    for item in affected:
        if hasattr(item, "end"):
            out.append((item.start or item.end, item.end))
        else:
            lo, hi = item
            out.append((lo, hi))
    return tuple(sorted(out))


def withdraw_extractions(extraction, affected):
    """RA-138 — return the extraction with the affected periods removed.

    ★ **Withdrawal is by `(evidence_id, period)`**, so RA-65's arithmetic needs
    no special case: coverage recomputes over what survives. An item outside the
    affected range survives untouched — a restatement of FY2024 does not
    withdraw FY2022.
    """
    ranges = normalise_periods(affected)
    kept = tuple(i for i in extraction.items if not _overlaps(i.period, ranges))
    withdrawn = tuple(i for i in extraction.items if _overlaps(i.period, ranges))
    return replace(extraction, items=kept), withdrawn


def assert_scorecard_re_derived(ticker: str, scorecard_periods, affected,
                                *, dimensions=()) -> None:
    """RA-83 — every level that cited an affected period is unsupported.

    ⚠ It **must be re-derived, not adjusted**, and the verdict is
    `INSUFFICIENT_DATA` — never "HOLD pending review."
    """
    ranges = normalise_periods(affected)
    hit = {p for p in scorecard_periods if _overlaps(p, ranges)}
    if hit:
        raise EvidenceWithdrawnError(
            ticker, [f"{p.start or ''}..{p.end}" if hasattr(p, "end") else str(p)
                     for p in hit], dimensions)
