"""The eighteen event classes — the enumeration DE-35 is checked against.

★ §6A.2's seventeen, plus §6B's **`ticker_change`** (class 18): a rename is a
corporate action like any other, and *from the price feed it is indistinguishable
from a delisting* — `BK`→`BNY` and `SATS`→`ECHO` both still trade.

★ WHY A TABLE AND NOT EIGHTEEN `if` BRANCHES.
`CT-7.7` requires **every one of them** to appear in `class_status` as
`CHECKED` or `UNCHECKED:<reason>`, and a class missing from the map is a defect
rather than an implied pass. Eighteen branches make an omission invisible; one
table makes it a length check.

```
DE-35 IS THE RULE THIS SECTION EXISTS FOR.

Every other rule here fails safe by HALTING. DE-35 fails safe by ADMITTING
IGNORANCE — and it is the one an implementation is tempted to skip, because
an empty list is so much easier to return than a tri-state.
```
"""

from __future__ import annotations

from dataclasses import dataclass

from src.data_engine.contracts.envelopes import BLOCK, FLAG, NOTE


@dataclass(frozen=True, slots=True)
class EventClass:
    """One row of §6A.2."""

    name: str
    number: int
    source: str
    knowability: str
    severity: str
    note: str = ""
    permanently_unchecked: bool = False
    universe_wide: bool = False


#: The eighteen — §6A.2's seventeen plus §6B's `ticker_change`, in spec order.
#: The `number` is carried so a reader can put a finding back against the spec
#: table without counting rows.
EVENT_CLASSES: tuple[EventClass, ...] = (
    EventClass("price_adjustment_state", 1, "derived: splits + dividends at as_of", "—",
               BLOCK, "BLOCK if the panel's adj_as_of differs from the run's (DE-28/DE-30)"),
    EventClass("split", 2, "fmp:splits", "8-K announcement; `date` is EFFECTIVE", BLOCK),
    EventClass("reverse_split", 3, "fmp:splits (denominator > numerator)",
               "8-K announcement", BLOCK,
               "also an M-1 penny-stock screening hazard — a $0.50 stock looks like $10"),
    # ⚠⚠ **Source corrected 2026-08-28 — the declared one does not carry the
    #    data.** Measured: FMP's filing index returns ZERO `10-K/A` across all
    #    filers in 2024, 2025 H1 and 2026 YTD, while `10-Q/A` fills a page over
    #    the same windows; EDGAR holds five for TSLA alone. ★ Same precedence
    #    as TTM — EDGAR wins where FMP omits. ⚠ And `formType ~ /A` was the
    #    wrong TEST as well: it matches `SC 13G/A` and `4/A`, which restate no
    #    financial statements (63 of them for AAPL alone). See DE-69.
    EventClass("restatement_amended", 4,
               "edgar:submissions (10-K/A, 10-Q/A, 20-F/A, 40-F/A; 8-K item 4.02)",
               "acceptanceDateTime", BLOCK,
               "BLOCK only if it amends a period inside the window"),
    EventClass("restatement_silent", 5, "our own diff across dated ingests (DE-24)",
               "ingest date", BLOCK,
               "the only restatement detection available on the FMP side"),
    EventClass("delisting", 6, "fmp:delisted-companies", "delistedDate", BLOCK,
               "survivorship — INV-017"),
    EventClass("filing_mid_window", 7, "statements' acceptedDate (§5C.1)", "acceptedDate",
               FLAG, "what was knowable changes INSIDE the window"),
    EventClass("dividend", 8, "fmp:dividends", "declarationDate — NOT `date` (the ex-date)",
               FLAG, "MSFT declares a median ~72 days before ex (K-4)"),
    EventClass("earnings_reported", 9, "fmp:earnings", "report date", FLAG),
    EventClass("earnings_scheduled", 10, "fmp:earnings-calendar",
               "none — 34.6% of rows are forward-dated", FLAG,
               "UNCHECKED unless snapshotted into CT-7.6 (QD-11)"),
    EventClass("material_event_8k", 11, "fmp:sec-filings-search/form-type=8-K",
               "acceptedDate", FLAG),
    EventClass("ma_announcement", 12, "fmp:mergers-acquisitions-latest", "acceptedDate", FLAG),
    EventClass("beneficial_ownership", 13, "fmp:acquisition-of-beneficial-ownership",
               "filingDate", FLAG, "activist or strategic stake-building"),
    EventClass("analyst_action", 14, "fmp:grades, fmp:price-target-news", "publishedDate",
               NOTE, "sentiment-affecting"),
    EventClass("news", 15, "fmp:news/stock", "publishedDate", NOTE,
               "UNCHECKED beyond ~92 days — K-8"),
    EventClass("macro_release", 16, "fmp:economic-calendar", "release date", NOTE,
               "universe-wide, not per ticker", universe_wide=True),
    EventClass("index_membership", 17, "(no source)", "—", NOTE,
               "UNCHECKED permanently — record the gap", permanently_unchecked=True),
    # ── §6B ──────────────────────────────────────────────────────────────────
    # ★★ A ticker is a LABEL WITH A VALIDITY INTERVAL, not an identity.
    #    ⚠ `BK`→`BNY` and `SATS`→`ECHO` were REBRANDS — both still trade — and
    #    from the price feed a rename and a delisting are indistinguishable.
    #    ★ BLOCK, because a universe still naming the retired symbol fetches a
    #    TRUNCATED series (BK stops at the changeover, BNY carries all 164 bars)
    #    and loses the name to staleness while `universe_n` still counts it.
    EventClass("ticker_change", 18,
               "derived: diff of dated sec:company_tickers.json snapshots on CIK",
               "the snapshot date the new symbol first appears", BLOCK,
               "cleared only by an explicit handling — the panel was fetched "
               "under the resolved current symbol (DE-63, DE-66, QD-15)"),
)

BY_NAME: dict[str, EventClass] = {c.name: c for c in EVENT_CLASSES}

#: DE-35's tri-state, spelled once. `UNCHECKED` always carries a reason: the
#: whole point is that "we could not look" and "we looked and found nothing" are
#: different results, and a bare `UNCHECKED` collapses them again.
CHECKED = "CHECKED"


def unchecked(reason: str) -> str:
    if not reason:
        raise ValueError(
            "UNCHECKED requires a reason. Absence of evidence and evidence of "
            "absence are different results, and a reasonless UNCHECKED is the "
            "first back into conflating them (DE-35)"
        )
    return f"UNCHECKED: {reason}"


#: §5C.4 — `news/stock` returns ~92 days regardless of paging depth, measured on
#: three tickers (K-8). Beyond it the class is UNCHECKED and never "no events".
NEWS_DEPTH_DAYS = 92
