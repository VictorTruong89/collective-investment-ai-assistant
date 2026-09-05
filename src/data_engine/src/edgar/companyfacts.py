"""companyfacts -> Facts (CT-7.3). The ingest boundary where DE-6.3 fires.

EDGAR's companyfacts payload is already close to the Fact ledger's shape — one
entry per (tag, unit, period, filing) — which is not a coincidence: §2.1's
Fact/FundamentalRow split was chosen *because* EDGAR is structured this way, and
CT-7.3 is what falls out of not flattening it.

⚠ **A fact with no `end`, no `accn` or no `filed` is dropped at ingest** and the
count is returned, never silently absorbed. `filed` in particular is DE-6.3: it
cannot be placed in time, so it could never be safely served.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from src.data_engine.pit.models import ANNUAL, Fact, QUARTERLY
from src.data_engine.src.edgar.xbrl import classify_span, unit_currency
from src.shared.money import Money


@dataclass(frozen=True, slots=True)
class ExtractResult:
    """What came out, and what did not. The second half is the point.

    ★ **P5**: a silent drop is the defect this system keeps paying for. Returning
    the rejected count and the reasons means an ingest that lost 40 % of its
    facts is visible in the run record rather than in a panel that "looks a bit
    thin".
    """

    facts: tuple[Fact, ...]
    rejected: int
    reasons: dict


def extract_facts(payload: dict, *, ticker: str, tags=None,
                  ingested_at: datetime | None = None) -> ExtractResult:
    """Every dated, filed, monetary Fact in a companyfacts response.

    `tags` restricts the extraction; None takes everything. Restricting is the
    normal case — companyfacts for a large filer runs to hundreds of concepts
    and MU's as-reported quarterly alone spans 536 distinct tags.
    """
    ingested_at = ingested_at or datetime.now(timezone.utc)
    ticker = ticker.upper()
    facts: list[Fact] = []
    reasons: dict[str, int] = {}

    for taxonomy in (payload.get("facts") or {}).values():
        for tag, body in taxonomy.items():
            if tags is not None and tag not in tags:
                continue
            for unit_key, entries in (body.get("units") or {}).items():
                currency = unit_currency(unit_key)
                for entry in entries:
                    fact = _one(entry, ticker, tag, unit_key, currency,
                                ingested_at, reasons)
                    if fact is not None:
                        facts.append(fact)
                # ★ The WHOLE series, not just what was rejected: the 90-day Q1
                #   is the anchor Q2 is differenced against, and it passes as a
                #   discrete quarter. Without it the chain starts at the
                #   six-month figure and Q2 can never be derived.
                facts.extend(derive_quarters(
                    entries, ticker=ticker, tag=tag, unit_key=unit_key,
                    currency=currency, ingested_at=ingested_at,
                    reported=facts, reasons=reasons))

    facts.sort(key=lambda f: (f.tag, f.period_end, f.period_type, f.filing_date,
                              f.accession_id))
    return ExtractResult(tuple(facts), sum(reasons.values()), dict(sorted(reasons.items())))


def _one(entry, ticker, tag, unit_key, currency, ingested_at, reasons) -> Fact | None:
    def reject(why: str):
        reasons[why] = reasons.get(why, 0) + 1
        return None

    if not entry.get("filed"):
        # DE-6.3 / AC-7.9 — the as-of filter runs on this axis; without it the
        # value can never be served, so it never enters.
        return reject("no filed date (DE-6.3)")
    if not entry.get("end"):
        return reject("no period end")
    if not entry.get("accn"):
        return reject("no accession id — restatements would be indistinguishable")
    if entry.get("val") is None:
        # DE-14: missing is null, never 0. A zero revenue and an unknown revenue
        # are different facts, so the unknown one is not stored as the known one.
        return reject("null value (DE-14 — not stored as zero)")

    end = date.fromisoformat(entry["end"])
    # An instant fact (a balance-sheet item) has no `start`. Its span is a point,
    # which classify_span would call "cumulative" — so instants are typed from
    # the filer's own `fp` rather than from arithmetic that does not apply.
    start = date.fromisoformat(entry["start"]) if entry.get("start") else end
    period_type = (classify_span(start, end) if entry.get("start")
                   else (ANNUAL if entry.get("fp") == "FY" else QUARTERLY))
    if period_type == "cumulative":
        # ★ §5.1's whole argument. A 6-K style year-to-date span is neither a
        # quarter nor a year; ingesting it as quarterly is what injects 2-3x
        # inflated revenue (ARM: 1.93x, 2.76x, 3.30x). It is derivable by
        # subtraction (xbrl.discrete_from_cumulative) and is NOT stored as-is.
        # ★★ Still not a discrete period, so still not emitted as one — but
        #   `derive_quarters` reads the same entries and differences them.
        return reject("cumulative span — differenced by derive_quarters (§5.1)")

    value = entry["val"]
    if currency is None:
        # Non-monetary (shares, per-share). CT-7.3 still needs a currency slot;
        # "" is used and is distinguishable from a real code by length.
        minor, code = int(value), ""
    else:
        minor, code = Money.from_float(float(value), currency).amount_minor, currency

    return Fact(
        ticker=ticker, accession_id=entry["accn"], tag=tag,
        period_start=start, period_end=end, period_type=period_type,
        value_minor=minor, value_currency=code, unit=unit_key,
        filing_date=date.fromisoformat(entry["filed"]), ingested_at=ingested_at,
    )


def derive_quarters(entries, *, ticker, tag, unit_key, currency,
                    ingested_at, reported, reasons) -> list:
    """★★ `Q_n = YTD_n − YTD_(n−1)` — **the arithmetic EDGAR is chosen for.**

    ⚠ *Found 2026-08-27 building D-02's 45 fundamental features.* `xbrl.py` has
    carried `discrete_from_cumulative` since B2 and **nothing ever called it**;
    `_one` rejected every cumulative span outright. The cost was invisible and
    large: NVDA's raw cash-flow facts carry **38 discrete quarters and 70
    year-to-date spans** (36 six-month, 34 nine-month), so **roughly two of every
    three quarters had no cash flow at all** — and every four-period rolling
    feature was null as a result, which reads as sparse data rather than as a
    dropped conversion.

    ★★ **This is the reason the project prefers EDGAR** (CLAUDE.md): *its facts
    carry explicit period start and end, so a discrete quarter is distinguishable
    from a cumulative YTD one by arithmetic, whereas FMP exposes only the period
    end and must guess — it guessed wrong on MU by 71 %.* Until now the
    distinguishing was done and the arithmetic was not.

    ⚠ **Only within one fiscal year, and only against the immediately preceding
    YTD of the same filing series.** Subtracting across a year boundary produces
    a number with no meaning, and subtracting a nine-month from a six-month one
    produces its negative.
    """
    from src.data_engine.src.edgar.xbrl import QUARTERLY

    if not entries:
        return []

    #: Spans already reported discretely — never re-derived over the top.
    have = {(f.period_start, f.period_end) for f in reported if f.tag == tag}

    by_start: dict = {}
    for entry in entries:
        try:
            start = date.fromisoformat(entry["start"])
            end = date.fromisoformat(entry["end"])
        except (KeyError, ValueError):
            continue
        if entry.get("val") is None:
            continue
        # ⚠ One (start, end) arrives from several accessions — the original
        #   filing and every later one that restates it. Differencing a span
        #   against ITSELF yields a zero-day, zero-value fact that looks like a
        #   quarter with no cash flow. Keyed on `end`, first wins.
        by_start.setdefault(start, {}).setdefault(end, entry)

    out = []
    for start, ends in by_start.items():
        series = sorted(ends.items())
        for index in range(1, len(series)):
            prior_end, prior = series[index - 1]
            end, entry = series[index]
            if (prior_end, end) in have:
                continue
            value = _quarter_value(entry, prior)
            if value is None:
                reasons["derived: one operand missing"] = \
                    reasons.get("derived: one operand missing", 0) + 1
                continue
            fact = _one({**entry, "start": prior_end.isoformat(), "val": value},
                        ticker, tag, unit_key, currency, ingested_at, reasons)
            # ⚠ `_one` re-classifies the shortened span; a stub that is still not
            #   a quarter (an odd 53-week year, a restated calendar) is dropped
            #   rather than forced into the enum.
            if fact is not None and fact.period_type == QUARTERLY:
                out.append(fact)
    return out


def _quarter_value(entry, prior):
    """`YTD_n − YTD_(n−1)`, or None. ⚠ A subtraction with one operand absent is
    **not zero** (DE-14)."""
    now, before = entry.get("val"), prior.get("val")
    if now is None or before is None:
        return None
    return now - before
