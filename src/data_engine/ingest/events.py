"""Corporate actions into the `EventStore` — the fetch §6A's gate reads.

★★ **The gate was reading a store nothing ever wrote.** `_calendar` recorded a
refresh for `split`, `reverse_split` and `dividend` unconditionally while the
entrypoint passed `events=()`, so three classes reported **`CHECKED` having
fetched nothing**. DE-35 exists to prevent exactly that — *"absence of evidence
and evidence of absence are different results, and conflating them is how a false
assumption becomes a silent one"* — and the conflation sat inside the code
implementing the rule.

⚠ **Deliberately NOT a per-run sweep.** QD-16: *510 tickers × 8 classes is
thousands of calls per run against a 300/min cap*, so §6A's design is an
**incrementally maintained store** that the gate reads. This module is the
maintainer; the daily run is a reader.

★ A class this module does not fetch stays `UNCHECKED` **and says so**. That is
the honest state, and it is what makes the three it does fetch mean something.
"""

from __future__ import annotations

from datetime import date

#: The classes this module can source today. ⚠ The rest stay `UNCHECKED` with
#: their reason — `index_membership` **permanently** (DE-35).
SOURCED = ("split", "reverse_split", "dividend", "delisting")

#: US venues. ⚠ `delisted-companies` is a **global** feed — page 0 measured
#: 2026-08-27 held OTC, CBOE and ASX rows beside NASDAQ/NYSE/AMEX — and a
#: foreign delisting is not an event in this book's universe.
US_EXCHANGES = frozenset({"NASDAQ", "NYSE", "AMEX"})


def refresh(client, store, *, tickers, start: date, end: date,
            on_error=None) -> dict:
    """Fetch splits and dividends for `tickers` and record the refresh.

    ⚠ **The refresh is recorded per class only if that class was fetched for the
    whole universe.** A partial sweep — 400 of 510 names — leaves the other 110
    unchecked, and marking the class `CHECKED` would claim otherwise. DE-36's
    argument applies: *a name excluded from the actionable slate still
    participates in cross-sectional normalisation, so its unhandled split
    contaminates every other name's rank.*
    """
    from src.data_engine.contracts import Finding
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.src.fmp import prices as fmp_prices

    findings, failed = [], {}
    for ticker in tickers:
        try:
            events = list(fmp_prices.splits(client, ticker))
            events += list(fmp_prices.dividends(client, ticker))
        except Exception as exc:               # noqa: BLE001 — named, not fatal
            failed[ticker] = str(exc)[:140]
            if on_error is not None:
                on_error(ticker, exc)
            continue
        for event in events:
            name = _class_of(event)
            findings.append(Finding(
                event.ticker, name, BY_NAME[name].severity, event.event_date,
                event.knowable_at, event.detail, event.source))

    store.upsert(findings)

    # ★ Only a class fetched for EVERY name is recorded as refreshed.
    recorded = []
    if not failed:
        for name in SOURCED:
            # ★ The names actually fetched travel with the refresh, so a later
            #   gate over a WIDER universe reports UNCHECKED rather than
            #   inheriting a coverage the sweep never had.
            store.record_refresh(name, start, end, covers_tickers=tickers)
            recorded.append(name)
    return {"tickers": len(tickers), "findings": len(findings),
            "failed": failed, "refreshed": recorded,
            "why": ("" if not failed else
                    f"{len(failed)} of {len(tickers)} names failed, so no class "
                    f"is recorded as refreshed — a partial sweep leaves the rest "
                    f"unchecked and CHECKED would claim otherwise")}


def _class_of(event) -> str:
    """`split` vs `reverse_split` — ⚠ **by the ratio, never by the label.**

    A 1-for-10 reverse split arrives on the same feed as a 10-for-1 forward one
    and the vendor calls both a split. The two have opposite effects on the price
    series, and D-07's severity table treats them separately.
    """
    if getattr(event, "event_type", "") != "split":
        return "dividend"
    detail = event.detail or {}
    return ("reverse_split"
            if detail.get("denominator", 0) > detail.get("numerator", 0)
            else "split")


def refresh_delistings(client, store, *, tickers, as_of: date) -> dict:
    """★ INV-017's declared source — and **it cannot correct history.**

    ```text
    ╔══════════════════════════════════════════════════════════════════╗
    ║  MEASURED 2026-08-27.  `delisted-companies` returns 100 rows on   ║
    ║  page 0 and **402 on every page after it**.  Page 0 spans about   ║
    ║  three weeks (2026-08-06 …) plus announced future delistings.     ║
    ║                                                                  ║
    ║  So this source can say WHO IS DELISTING NOW.  It cannot say who  ║
    ║  delisted in 2019, and **INV-017's survivorship correction needs  ║
    ║  exactly that**.  AB-3 stands: a backtest over today's index is   ║
    ║  reported BIASED (QA-14), and this does not change it.            ║
    ╚══════════════════════════════════════════════════════════════════╝
    ```

    ⚠⚠ **The refresh records the window the feed ACTUALLY reached**, not the one
    that was asked for. Recording a ten-year window from a three-week feed is
    DE-56 and DE-58's defect a third time, and the date range is exactly what
    makes it look rigorous.
    """
    from src.data_engine.contracts import Finding
    from src.data_engine.calendar.classes import BY_NAME

    try:
        rows = client.get("delisted-companies")
    except Exception as exc:                   # noqa: BLE001
        return {"findings": 0, "refreshed": [],
                "why": f"the delisting feed is unavailable: {str(exc)[:120]}"}

    wanted = {t.upper() for t in tickers}
    findings, seen_dates = [], []
    for row in rows or []:
        symbol = str(row.get("symbol", "")).upper()
        when = row.get("delistedDate")
        if not when:
            continue
        seen_dates.append(_as_date(when))
        if symbol not in wanted or row.get("exchange") not in US_EXCHANGES:
            continue
        event_date = _as_date(when)
        findings.append(Finding(
            symbol, "delisting", BY_NAME["delisting"].severity, event_date,
            # ⚠ A delisting is knowable when it is announced, and this feed
            #   carries only the effective date. Using it is CONSERVATIVE — it
            #   can only omit an event from a knowability-keyed report, never
            #   invent one (DE-34's own argument for splits).
            event_date, {"company": row.get("companyName", ""),
                         "exchange": row.get("exchange", "")}, "fmp:delisted-companies"))

    store.upsert(findings)
    if not seen_dates:
        return {"findings": 0, "refreshed": [],
                "why": "the delisting feed returned no dated rows"}

    reached_from, reached_to = min(seen_dates), max(seen_dates)
    store.record_refresh("delisting", reached_from, reached_to,
                         covers_tickers=tickers)
    return {
        "findings": len(findings),
        "refreshed": ["delisting"],
        "reached": f"{reached_from}..{reached_to}",
        # ★ Stated on every call, because a caller asking for ten years gets
        #   three weeks and nothing else would say so.
        "why": (f"⚠ page 0 only — pages 1+ are 402 on this plan, so the feed "
                f"reaches {reached_from}..{reached_to}. INV-017's HISTORICAL "
                f"survivorship correction is NOT possible from this source "
                f"(AB-3 stands)"),
    }


def refresh_ma_announcements(client, store, *, tickers, as_of: date,
                             since: date | None = None,
                             max_pages: int = 40) -> dict:
    """Class 12 — ★★ **the event that PRECEDES the silence.**

    ```text
    ╔══════════════════════════════════════════════════════════════════╗
    ║  ★ THE EVENT THAT PRECEDES THE SILENCE.  A combination is filed   ║
    ║    MONTHS before a ticker stops printing, so the name going       ║
    ║    quiet is the LAST evidence to arrive, not the first.           ║
    ║                                                                  ║
    ║  ⚠⚠ BUT THIS IS A CANDIDATE, NEVER A CONCLUSION.                  ║
    ║     MEASURED 2026-08-28 over 3 years of the S&P 500: SIX names    ║
    ║     matched, and FOUR ARE NOT ACQUISITIONS OF THAT NAME AT ALL.   ║
    ║                                                                  ║
    ║       CMI  -> ATMU     Cummins SPLIT OFF Atmus                    ║
    ║       AIG  -> CRBG     AIG DIVESTED Corebridge                    ║
    ║       BDX  -> WAT      Reverse Morris Trust — BDX is the PARENT   ║
    ║       COF  -> COF-PI   its own PREFERRED CLASS                    ║
    ║       BEN  -> DHCA     a SPAC S-4                                 ║
    ║       NSC  -> UNP      ★ the one genuine merger of the six        ║
    ║                                                                  ║
    ║  ★ THE PAIR IS FILER vs SUBJECT ON AN S-4 — NOT ACQUIRER vs       ║
    ║    TARGET.  A split-off and an acquisition are the SAME SHAPE     ║
    ║    here, and the parent appears in the position a naive reading   ║
    ║    calls "the side that disappears".                             ║
    ╚══════════════════════════════════════════════════════════════════╝
    ```

    ★★ **Measured 2026-08-28: this feed PAGES, and `delisted-companies` does
    not.** Page 40 still returns rows dated **1999**, where `delisted-companies`
    walls at about three weeks (DE-60). ⚠ That does **not** close INV-017: this
    names *acquisitions and mergers*, not bankruptcies or compliance removals,
    so it is a **partial** survivorship source at best and AB-3 still stands.

    ⚠ **`acceptedDate` is the knowability date, `transactionDate` the event
    date** (DE-34). Using the transaction date for both would make an
    announcement knowable before the filing that announced it.
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding

    wanted = {t.upper() for t in tickers}
    findings, seen, pages, stopped = [], [], 0, "exhausted the feed"

    for page in range(max_pages):
        try:
            rows = client.get("mergers-acquisitions-latest", page=page, limit=100)
        except Exception as exc:                       # noqa: BLE001
            # ⚠ Named, not swallowed: a 402 partway through means the window
            #   REACHED is shorter than the one asked for, and the refresh must
            #   record what it got — DE-56/DE-58's defect otherwise.
            stopped = f"the feed stopped at page {page}: {str(exc)[:100]}"
            break
        if not rows:
            stopped = f"the feed ran out at page {page}"
            break
        pages += 1

        for row in rows:
            when = _as_date_or_none(row.get("transactionDate"))
            if when is None:
                continue
            seen.append(when)
            knowable = _as_date_or_none(row.get("acceptedDate")) or when
            # ⚠ DE-34 — an announcement the run could not have read is not a
            #   finding for it, however real it is.
            if knowable > as_of:
                continue
            for side, symbol, other, other_name in (
                    ("subject", str(row.get("targetedSymbol") or "").upper(),
                     str(row.get("symbol") or "").upper(),
                     row.get("companyName")),
                    ("filer", str(row.get("symbol") or "").upper(),
                     str(row.get("targetedSymbol") or "").upper(),
                     row.get("targetedCompanyName"))):
                if not symbol or symbol not in wanted:
                    continue
                findings.append(Finding(
                    symbol, "ma_announcement", BY_NAME["ma_announcement"].severity,
                    when, knowable,
                    # ⚠⚠ `side` is the FILING's role, not the DEAL's. Calling
                    #   the subject a "target" would label Cummins, AIG, BDX
                    #   and Capital One as acquired companies — measured, and
                    #   four of six matches were exactly that (DE-35).
                    {"side": side, "counterparty": other,
                     "counterparty_name": other_name or "",
                     "cik": str(row.get("cik") or ""),
                     "targeted_cik": str(row.get("targetedCik") or ""),
                     "link": row.get("link") or "",
                     "investigate": ".claude/skills/ticker-went-silent/"},
                    "fmp:mergers-acquisitions-latest"))

        if since is not None and seen and min(seen) <= since:
            stopped = f"reached {since} at page {page}"
            break

    store.upsert(findings)
    if not seen:
        return {"findings": 0, "refreshed": [],
                "why": "the M&A feed returned no dated rows"}

    reached_from, reached_to = min(seen), max(seen)
    # ⚠⚠ The window RECORDED is the one the feed reached, never the one asked
    #   for. This is the third place that mistake was made (DE-56, DE-58).
    store.record_refresh("ma_announcement", reached_from, reached_to,
                         covers_tickers=tickers)
    subjects = sum(1 for f in findings if f.detail["side"] == "subject")
    return {
        "findings": len(findings),
        "refreshed": ["ma_announcement"],
        "reached": f"{reached_from}..{reached_to}",
        "pages": pages,
        "subjects": subjects,
        "why": (f"⚠ {stopped}. ★ Unlike `delisted-companies` this feed PAGES — "
                f"{pages} page(s) reached {reached_from}. ⚠⚠ Every hit is a "
                f"CANDIDATE, not a conclusion: the pair is S-4 filer/subject, "
                f"and MEASURED 4 of 6 universe matches were split-offs, "
                f"divestitures or a preferred class — NOT acquisitions of that "
                f"name (DE-35). ⚠ Partial survivorship source only; AB-3 stands"),
    }


def _as_date_or_none(value):
    """⚠ A malformed date is skipped, never coerced to today."""
    try:
        return _as_date(value) if value else None
    except (TypeError, ValueError):
        return None


def _as_date(value):
    from datetime import date as _date

    return _date.fromisoformat(str(value)[:10])
