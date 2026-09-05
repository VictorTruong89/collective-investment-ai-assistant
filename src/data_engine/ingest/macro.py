"""Class 16 `macro_release` — **NOTE.** ★ The one class with no ticker.

```text
╔══════════════════════════════════════════════════════════════════╗
║  ⚠⚠ MEASURED 2026-08-28.  `economic-calendar` TRUNCATES THE SAME  ║
║     WAY `earnings-calendar` DOES — and worse, NON-MONOTONICALLY:  ║
║                                                                  ║
║       asked 2026-08-01..2026-08-28  -> 2 313 rows, FULL span      ║
║       asked 2026-01-01..2026-12-31  -> 1 407 rows, ONLY Oct-Dec   ║
║                                                                  ║
║     ★ A WIDER REQUEST RETURNED FEWER ROWS AND LESS HISTORY.       ║
║     Nothing in the response says so.  DE-70 again, on a second    ║
║     endpoint — so the guard is reused, not reinvented.           ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **This class has no ticker**, and every other class in §6A does. A macro
release is an event for the *whole book*, so it is stored under a reserved
sentinel rather than fabricating a per-name row — ★ writing 510 identical
findings for one CPI print would make the store's size a function of universe
width rather than of information.
"""

from __future__ import annotations

from datetime import date, timedelta

#: ★ The ticker a class with no ticker uses. ⚠ Deliberately not a real symbol
#: and not blank: a blank would silently join to everything.
MARKET_WIDE = "*MACRO*"

#: ⚠ Only releases that can move a whole book. ★ The feed's own `impact`
#: field; a "Low" impact print is noise at NOTE severity and there are
#: thousands of them.
KEPT_IMPACT = frozenset({"High", "Medium"})

#: ★ The book is USD/CAD (INV-5), so these are the economies that matter.
KEPT_COUNTRIES = frozenset({"US", "CA"})

#: ⚠ Chunk width, for the same reason as DE-70: narrow enough that the silent
#: truncation never bites. *Measured:* a 28-day window returned its full span;
#: a 365-day window dropped nine months.
CHUNK_DAYS = 30

#: ⚠ A missing head smaller than this is a **quiet calendar**, not truncation.
#: ★ An admitted choice (CN-10) — without it the detector fires on every
#: holiday week and the real signal drowns.
_MIN_GAP_DAYS = 7


def refresh_macro(client, store, *, as_of: date, since: date,
                  chunk_days: int = CHUNK_DAYS) -> dict:
    """Class 16 into the store, chunked so the silent truncation cannot bite.

    ⚠⚠ **A response whose span does not reach the requested `from` is
    truncated**, and this is the only way to detect it — the endpoint returns
    HTTP 200 either way. ★ Unlike `earnings-calendar` there is no row cap to
    watch; the tell is the *span*, so that is what is checked.
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding

    severity = BY_NAME["macro_release"].severity
    findings, seen, short = [], [], []
    cursor = since
    horizon = as_of + timedelta(days=90)      # ★ scheduled releases are useful

    while cursor <= horizon:
        stop = min(cursor + timedelta(days=chunk_days - 1), horizon)
        try:
            rows = client.get("economic-calendar", **{"from": cursor.isoformat(),
                                                      "to": stop.isoformat()}) or []
        except Exception as exc:                   # noqa: BLE001 — named
            short.append({"span": f"{cursor}..{stop}", "cause": "refused",
                          "detail": str(exc)[:90]})
            cursor = stop + timedelta(days=1)
            continue

        dates = [d for d in (_as_date(r.get("date")) for r in rows) if d]
        missing = (min(dates) - cursor).days if dates else 0
        # ⚠⚠ The tell is a LARGE missing head, not any gap at all.
        #   ★ A calendar legitimately has quiet stretches — and a window in the
        #   FUTURE is sparse by nature, because releases are only scheduled so
        #   far ahead. A first cut flagged `2026-11-21..26 returned from the
        #   23rd` as truncation; that was two quiet days, not a dropped span.
        #   The measured truncation was NINE MONTHS missing from a year.
        if cursor <= as_of and missing > max(_MIN_GAP_DAYS, chunk_days // 3):
            short.append({"span": f"{cursor}..{stop}", "cause": "truncated",
                          "detail": f"returned from {min(dates)}, not {cursor} "
                                    f"— {missing} days missing from the head"})

        for row in rows:
            when = _as_date(row.get("date"))
            if when is None:
                continue
            if str(row.get("country") or "").upper() not in KEPT_COUNTRIES:
                continue
            if str(row.get("impact") or "") not in KEPT_IMPACT:
                continue
            seen.append(when)
            # ⚠ A macro release is knowable ON its date — the calendar is
            #   published ahead, but the NUMBER is not.
            findings.append(Finding(
                MARKET_WIDE, "macro_release", severity, when, when,
                {"event": _text(row.get("event"))[:200],
                 "country": _text(row.get("country")),
                 "impact": _text(row.get("impact")),
                 "actual": _num(row.get("actual")),
                 "estimate": _num(row.get("estimate")),
                 "previous": _num(row.get("previous")),
                 "unit": _text(row.get("unit"))},
                "fmp:economic-calendar"))
        cursor = stop + timedelta(days=1)

    store.upsert(findings)
    if not seen:
        return {"findings": 0, "refreshed": [], "short": short,
                "why": "the economic calendar returned no kept rows"}

    reached_from, reached_to = min(seen), max(seen)
    if short:
        # ⚠ NOT recorded — an unreached span means releases we never saw.
        return {"findings": len(findings), "refreshed": [], "short": short,
                "reached": f"{reached_from}..{reached_to}",
                "why": (f"⚠⚠ {len(short)} chunk(s) did not cover their window "
                        f"({short[0]['span']}, {short[0]['cause']}) — the class "
                        f"is NOT recorded as refreshed (DE-58, DE-70)")}

    store.record_refresh("macro_release", reached_from, reached_to,
                         covers_tickers=(MARKET_WIDE,))
    return {"findings": len(findings), "refreshed": ["macro_release"],
            "short": [], "reached": f"{reached_from}..{reached_to}",
            "why": (f"★ stored under {MARKET_WIDE} — ⚠ a macro release is not a "
                    f"per-ticker event, and 510 copies of one CPI print would "
                    f"make the store's size a function of universe width")}


def _num(value):
    try:
        return None if value in (None, "") else float(value)
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
