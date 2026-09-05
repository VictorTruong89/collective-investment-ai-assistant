"""Classes 13, 14, 15 — beneficial ownership, analyst actions, news.

★ The **FLAG and NOTE** tail of §6A's taxonomy: none of these can invalidate a
panel the way a split or a restatement can, and all three are per-ticker feeds.

```text
╔══════════════════════════════════════════════════════════════════╗
║  ⚠⚠ MEASURED 2026-08-28 — THE VOLUME HAZARD IS REAL.             ║
║                                                                  ║
║    `grades` IGNORES `limit` ENTIRELY.  limit=5, limit=50 and no   ║
║    limit all return the SAME 1 791 rows for AAPL, back to 2012.   ║
║    Across 510 names that is ~900 000 findings — more than 16x     ║
║    the ENTIRE event store — from one NOTE-severity class.        ║
║                                                                  ║
║  ★ SO THE WINDOW IS ENFORCED HERE, CLIENT-SIDE, NOT REQUESTED.    ║
║    A feed that ignores `limit` will ignore it silently.          ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **Severity governs how hard these try.** A NOTE that fails is not a reason to
fail the sweep — the gate cannot BLOCK on it — so a per-ticker error is
collected and reported, and the class simply records the names it reached.
"""

from __future__ import annotations

from datetime import date

#: ⚠⚠ A hard stop per ticker, because `grades` ignores `limit`. ★ An admitted
#: choice (CN-10): it bounds a NOTE class that could otherwise dominate the
#: store, and the window filter usually bites first.
MAX_ROWS_PER_TICKER = 500


def refresh_beneficial_ownership(client, store, *, tickers, as_of: date,
                                 since: date | None = None) -> dict:
    """Class 13 — **FLAG.** ★ `acceptedDate` is carried, so DE-34 is honoured.

    ⚠ A 13D/G tells you someone crossed 5 %; it does not tell you why, and the
    class is a FLAG for that reason — it is context for a reader, never a gate.
    """
    def rows_for(ticker):
        return client.get("acquisition-of-beneficial-ownership", symbol=ticker)

    def build(ticker, row):
        when = _as_date(row.get("filingDate"))
        # ★ acceptedDate is the knowability axis (DE-34); filingDate is the
        #   event. ⚠ They differ, and the accepted one is always the later.
        knowable = _as_date(row.get("acceptedDate")) or when
        return when, knowable, {
            "holder": _text(row.get("nameOfReportingPerson")),
            "cusip": _text(row.get("cusip")),
            "sole_voting": _num(row.get("soleVotingPower")),
            "shared_voting": _num(row.get("sharedVotingPower")),
        }

    return _per_ticker(client, store, "beneficial_ownership", tickers,
                       as_of=as_of, since=since, rows_for=rows_for, build=build,
                       source="fmp:acquisition-of-beneficial-ownership")


def refresh_analyst_actions(client, store, *, tickers, as_of: date,
                            since: date | None = None) -> dict:
    """Class 14 — **NOTE.** ⚠⚠ **The feed ignores `limit`; the window is ours.**

    ★ An upgrade/downgrade is recorded with **both** grades, because the level
    alone says nothing — *"Buy"* is a different event coming from *"Strong Buy"*
    than from *"Hold"*.
    """
    def rows_for(ticker):
        return client.get("grades", symbol=ticker)

    def build(ticker, row):
        when = _as_date(row.get("date"))
        return when, when, {
            "firm": _text(row.get("gradingCompany")),
            "action": _text(row.get("action")),
            "from_grade": _text(row.get("previousGrade")),
            "to_grade": _text(row.get("newGrade")),
        }

    return _per_ticker(client, store, "analyst_action", tickers,
                       as_of=as_of, since=since, rows_for=rows_for, build=build,
                       source="fmp:grades")


def refresh_news(client, store, *, tickers, as_of: date,
                 since: date | None = None) -> dict:
    """Class 15 — **NOTE.** ⚠ *Measured:* the feed returns ~20 recent items per
    name, so it is a **recent-window** source and cannot answer a historical
    question. ★ Recorded as such rather than presented as a news archive.
    """
    def rows_for(ticker):
        return client.get("news/stock", symbols=ticker)

    def build(ticker, row):
        when = _as_date(row.get("publishedDate"))
        return when, when, {
            "title": _text(row.get("title"))[:300],
            "publisher": _text(row.get("publisher") or row.get("site")),
            "url": _text(row.get("url")),
        }

    return _per_ticker(client, store, "news", tickers, as_of=as_of, since=since,
                       rows_for=rows_for, build=build, source="fmp:news/stock")


def _per_ticker(client, store, event_class: str, tickers, *, as_of: date,
                since: date | None, rows_for, build, source: str) -> dict:
    """The shape all three share: fetch per name, window, cap, record coverage.

    ⚠⚠ **The window is applied HERE, not requested.** *Measured:* `grades`
    returns its full history whatever `limit` says, so a caller that trusted the
    parameter would ingest 14 years per name and never be told.

    ⚠ **Coverage is the names actually reached** (DE-58). A name that errored is
    excluded, so a gate over the wider universe reports `UNCHECKED` rather than
    inheriting a claim this sweep cannot support.
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding

    severity = BY_NAME[event_class].severity
    findings, reached, failed, capped = [], [], {}, []

    for ticker in tickers:
        try:
            rows = rows_for(ticker) or []
        except Exception as exc:                   # noqa: BLE001 — named
            failed[ticker] = str(exc)[:120]
            continue
        reached.append(ticker)

        kept = 0
        for row in rows:
            when, knowable, detail = build(ticker, row)
            if when is None or knowable is None:
                continue
            if knowable > as_of:
                continue                   # ⚠ DE-34 — not knowable to this run
            if since is not None and when < since:
                continue
            if kept >= MAX_ROWS_PER_TICKER:
                # ⚠ Admitted, never silent: the name is truncated and said so.
                capped.append(ticker)
                break
            kept += 1
            findings.append(Finding(ticker, event_class, severity, when,
                                    knowable, detail, source))

    store.upsert(findings)
    if not reached:
        return {"findings": 0, "refreshed": [], "failed": failed,
                "why": f"no name could be fetched for {event_class}"}

    window_from = since or date(1900, 1, 1)
    store.record_refresh(event_class, window_from, as_of,
                         covers_tickers=tuple(reached))
    why = ""
    if failed:
        why = (f"⚠ {len(failed)} name(s) failed and are EXCLUDED from coverage, "
               f"so the class is CHECKED only for the {len(reached)} reached: "
               f"{sorted(failed)[:5]}")
    if capped:
        why += (f" ⚠⚠ {len(set(capped))} name(s) hit the "
                f"{MAX_ROWS_PER_TICKER}-row per-ticker cap — the feed ignores "
                f"`limit`, so the cap is ours and the excess is NOT stored")
    return {"findings": len(findings), "refreshed": [event_class],
            "reached": tuple(reached), "failed": failed,
            "capped": sorted(set(capped)), "why": why}


def _num(value):
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _text(value) -> str:
    return "" if value is None else str(value)


def _as_date(value):
    from datetime import date as _date

    try:
        return _date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None
