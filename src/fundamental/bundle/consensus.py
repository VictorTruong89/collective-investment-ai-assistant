"""What the market's analysts had PUBLISHED about a name, as of a date — a Stage B–D input.

`L3` §2.1p item 5 (Victor, 2026-10-01). ★ Fills `J-09`'s *"consensus position"*, the
input whose absence capped every thesis at Low conviction (`DX-118`). Deterministic:
it filters and counts what was published; it never estimates what was not.
The two computed numbers (target median/low/high, EPS surprise) are D-02's:
`src/feature_engineer/consensus.py` (AC-1.40).

Sources: FMP `grades` (rating actions), `price-target-news` (target changes) and
`earnings` (estimate vs actual per report), each event-stamped (Class A,
`fmp-api` trap 5) and stored as version-controlled fixtures.

| Rule | Decided |
|---|---|
| **1b** | an item counts when published ON OR BEFORE the as-of date's **market close** (16:00 New York), the same moment as the raw close the thesis is priced at. ⚠ A date-only row on the as-of date cannot be shown to precede the close, so it is excluded |
| **2a** | past earnings estimates are included **with a caveat**: FMP edits these rows after the report (`lastUpdated`), so a past estimate may have been revised |

⚠ **Not supplied, and declared absent:** a FORWARD consensus (next-quarter / next-year
EPS and revenue). FMP's `analyst-estimates` holds only today's values, with no
publication date, so for a past as-of it would be look-ahead (`DX-109`).
⚠ The part is `computed`, so the blind Stage-A view never sees it (`RA-14`): analysts'
opinions are exactly the anchors that view strips.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from src.feature_engineer.consensus import eps_surprise_pct, target_spread
from src.fundamental.bundle.models import BundlePart

RATINGS_WINDOW_DAYS = 365
TARGETS_WINDOW_DAYS = 90
EARNINGS_REPORTS = 4
MARKET_CLOSE = time(16, 0)
NEW_YORK = ZoneInfo("America/New_York")

#: Grade label → bucket. ⚠ Closed on purpose: a label not listed is reported as
#: `unmapped`, never guessed into a bucket (P5).
BUCKET = {
    **dict.fromkeys(("buy", "strong buy", "outperform", "overweight", "positive", "accumulate",
                     "sector outperform", "market outperform", "top pick", "conviction buy",
                     "add"), "buy"),
    **dict.fromkeys(("hold", "neutral", "equal weight", "equal-weight", "market perform",
                     "sector perform", "peer perform", "in-line", "sector weight", "mixed",
                     "perform"), "hold"),
    **dict.fromkeys(("sell", "strong sell", "underperform", "underweight", "negative",
                     "reduce", "sector underperform", "market underperform"), "sell"),
}

EARNINGS_CAVEAT = ("FMP edits these rows after the report (each carries `lastUpdated`), so a "
                   "past estimate may have been revised since it was the live consensus")
FORWARD_ABSENT = ("no forward consensus (next-period EPS or revenue) is supplied: FMP holds only "
                  "today's estimates, with no publication date, so for this as-of they would be "
                  "look-ahead")


def market_close_utc(as_of: date) -> datetime:
    """16:00 New York on `as_of`, in UTC (DST handled by the zone, not by a constant)."""
    return datetime.combine(as_of, MARKET_CLOSE, tzinfo=NEW_YORK).astimezone(timezone.utc)


def _known_by_close(stamp: str, as_of: date) -> bool:
    """Decision 1b. A full timestamp is compared with the close; a bare date counts only
    if it is BEFORE the as-of date, since a same-day bare date cannot be placed."""
    text = str(stamp or "")
    if len(text) <= 10:
        return date.fromisoformat(text[:10]) < as_of
    moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment <= market_close_utc(as_of)


def _day(stamp: str) -> date:
    return date.fromisoformat(str(stamp)[:10])


def consensus_as_of(*, grades, targets, earnings, as_of: date) -> dict:
    """The consensus a reader could have known at the as-of close. Pure; no I/O."""
    # ── ratings: the latest action per firm, in the 12 months before ────────
    since = as_of - timedelta(days=RATINGS_WINDOW_DAYS)
    window = sorted((g for g in grades
                     if _known_by_close(g["date"], as_of) and _day(g["date"]) > since),
                    key=lambda g: g["date"])
    latest = {}
    for g in window:
        latest[g["gradingCompany"]] = g["newGrade"]
    buckets = {"buy": 0, "hold": 0, "sell": 0}
    unmapped = {}
    for firm, grade in latest.items():
        bucket = BUCKET.get(str(grade).strip().lower())
        if bucket is None:
            unmapped[firm] = grade
        else:
            buckets[bucket] += 1
    ratings = {"window_days": RATINGS_WINDOW_DAYS, "latest_by_firm": latest,
               "by_bucket": buckets, "unmapped": unmapped,
               "actions": dict(Counter(g.get("action") for g in window))}

    # ── price targets: the 90 days before ────────────────────────────────────
    since = as_of - timedelta(days=TARGETS_WINDOW_DAYS)
    items = sorted(({"published": t["publishedDate"], "firm": t.get("analystCompany") or "",
                     "target": t["priceTarget"], "price_when_posted": t.get("priceWhenPosted")}
                    for t in targets
                    if t.get("priceTarget") is not None
                    and _known_by_close(t["publishedDate"], as_of)
                    and _day(t["publishedDate"]) > since),
                   key=lambda t: t["published"])
    price_targets = {"window_days": TARGETS_WINDOW_DAYS, "items": items,
                     **target_spread(t["target"] for t in items)}

    # ── earnings: the last reports, estimate vs actual (decision 2a) ─────────
    reported = sorted((e for e in earnings
                       if e.get("epsActual") is not None and _known_by_close(e["date"], as_of)),
                      key=lambda e: e["date"])[-EARNINGS_REPORTS:]
    reports = []
    for e in reported:
        est, act = e.get("epsEstimated"), e.get("epsActual")
        reports.append({
            "date": e["date"][:10], "eps_estimated": est, "eps_actual": act,
            "eps_surprise_pct": eps_surprise_pct(est, act),
            "revenue_estimated": e.get("revenueEstimated"),
            "revenue_actual": e.get("revenueActual"),
            "last_updated": e.get("lastUpdated")})
    return {"as_of": as_of.isoformat(), "boundary": market_close_utc(as_of).isoformat(),
            "ratings": ratings, "price_targets": price_targets,
            "earnings": {"reports": reports, "caveat": EARNINGS_CAVEAT},
            "forward_estimates": FORWARD_ABSENT}


def _money(x) -> str:
    return "—" if x is None else f"{x:,.2f}".rstrip("0").rstrip(".")


def consensus_part(summary: dict, *, version: int = 1) -> BundlePart:
    """The summary as a `computed` bundle part — plain lines, the reader's units."""
    r, p, e = summary["ratings"], summary["price_targets"], summary["earnings"]
    lines = [f"CONSENSUS AS OF {summary['as_of']} (published by market close, "
             f"{summary['boundary']}) — analysts' published actions only.",
             "These are OTHER PEOPLE'S views, supplied so a differential view can be stated. "
             "They are not evidence about the business.",
             "",
             f"RATINGS — latest per firm, {r['window_days']} days before: "
             f"buy {r['by_bucket']['buy']} · hold {r['by_bucket']['hold']} · "
             f"sell {r['by_bucket']['sell']} ({len(r['latest_by_firm'])} firms)"]
    lines += [f"- {firm}: {grade}" for firm, grade in sorted(r["latest_by_firm"].items())]
    if r["unmapped"]:
        lines.append(f"  unmapped grade labels (not counted): {r['unmapped']}")
    lines.append(f"  actions in the window: {r['actions']}")
    lines += ["", f"PRICE TARGETS — {p['window_days']} days before: n {p['n']}"
                  + (f" · median {_money(p['median'])} · low {_money(p['low'])} · "
                     f"high {_money(p['high'])}" if p["n"] else "")]
    lines += [f"- {t['published'][:10]} {t['firm']}: target {_money(t['target'])} "
              f"(price when posted {_money(t['price_when_posted'])})" for t in p["items"]]
    lines += ["", f"EARNINGS — last {len(e['reports'])} reports, consensus estimate vs actual "
                  f"(⚠ {e['caveat']}):"]
    lines += [f"- {x['date']}: EPS est {_money(x['eps_estimated'])} · actual "
              f"{_money(x['eps_actual'])} · surprise {x['eps_surprise_pct']}% · revenue est "
              f"{_money(x['revenue_estimated'])} · actual {_money(x['revenue_actual'])} "
              f"(row last updated {x['last_updated']})" for x in e["reports"]]
    lines += ["", f"NOT SUPPLIED: {summary['forward_estimates']}"]
    return BundlePart("computed", {"contract_name": "consensus.as_of",
                                   "contract_version": int(version)}, "\n".join(lines))
