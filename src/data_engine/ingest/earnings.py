"""Classes 9 & 10 — `earnings_reported` and `earnings_scheduled`. **FLAG.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  ⚠⚠ MEASURED 2026-08-28.  `earnings-calendar` IS CAPPED AT 4 000  ║
║     ROWS AND TRUNCATES SILENTLY — KEEPING THE LATEST, NOT THE     ║
║     EARLIEST:                                                    ║
║                                                                  ║
║       asked 2026-01-01..2026-12-31 -> got 2026-11-05..2026-12-31  ║
║       asked 2026-08-01..2026-09-30 -> got 2026-08-13..2026-09-30  ║
║                                                                  ║
║     Nothing in the response says a word about it.  A sweep that   ║
║     asked for a year and recorded a year would be claiming ten    ║
║     months it never saw — DE-56/DE-58/DE-60 A THIRD TIME.        ║
║                                                                  ║
║  ★ SO THE CAP IS DETECTED, NOT ASSUMED AWAY: a chunk that comes   ║
║    back at the cap is SPLIT AND REFETCHED until it fits.          ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠⚠ **`lastUpdated` is NOT a knowability date** (DE-23, AC-7.37) — and this feed
carries it, so the trap is live. *Measured:* **17 of AAPL's 20 quarters share
one stamp**, `2026-06-04`; it is a batch reload marker, not a publication date.
★ `date` is the **announcement** date (Apple's rows fall in late Jan/Apr/Jul/Oct,
not on period ends), and that is the axis used here.

★ **The two classes split on `epsActual`**: present ⇒ reported, absent ⇒ still
scheduled. ⚠ Their knowability differs and it is not cosmetic — see below.
"""

from __future__ import annotations

from datetime import date, timedelta

#: ⚠ The row cap the endpoint enforces without saying so. ★ A response AT the
#: cap is treated as truncated — it is indistinguishable from one that was.
ROW_CAP = 4000

#: ★ Chunk width. ⚠ Not tuned for speed: narrow enough that ordinary weeks stay
#: far under the cap, and peak earnings weeks still split rather than truncate.
CHUNK_DAYS = 7

#: ⚠ How many times a capped chunk may be halved before we admit defeat and
#: record only what was reached. ★ 7 days -> ~1.6 hours; long before that the
#: cap has stopped being about the window.
MAX_SPLIT_DEPTH = 6

#: ⚠⚠ DE-23 — fields that LOOK like a knowability axis on this feed and are not.
FORBIDDEN_KNOWABILITY = ("lastUpdated",)


def refresh_earnings(client, store, *, tickers, as_of: date,
                     since: date, chunk_days: int = CHUNK_DAYS) -> dict:
    """Both earnings classes into the store, over `since..as_of` plus the
    forward schedule.

    ⚠⚠ **Knowability differs between the two classes, and conflating them would
    be look-ahead:**

    * `earnings_reported` — the announcement **is** the knowability date. A
      result announced on the 29th was not knowable on the 28th.
    * `earnings_scheduled` — the *event* is in the future; what is knowable is
      **that we saw this schedule today**, so `knowable_at = as_of`. ⚠ A
      scheduled date **moves**, so using today's calendar to answer *"what was
      scheduled as of 2024-03-01"* is look-ahead of exactly DE-65's kind. This
      class is honest about the CURRENT schedule only.
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding

    wanted = {t.upper() for t in tickers}
    reported_sev = BY_NAME["earnings_reported"].severity
    scheduled_sev = BY_NAME["earnings_scheduled"].severity

    rows, spans, truncated = [], [], []
    cursor = since
    # ★ Forward to the end of the visible schedule, not merely to as_of: a
    #   scheduled date is the one piece of this feed that is USEFUL ahead.
    horizon = as_of + timedelta(days=120)
    while cursor <= horizon:
        stop = min(cursor + timedelta(days=chunk_days - 1), horizon)
        got, spans_here, cut = _fetch_span(client, cursor, stop, depth=0)
        rows.extend(got)
        spans.extend(spans_here)
        truncated.extend(cut)
        cursor = stop + timedelta(days=1)

    findings, seen = [], []
    for row in rows:
        symbol = str(row.get("symbol") or "").upper()
        if symbol not in wanted:
            continue
        when = _as_date(row.get("date"))
        if when is None:
            continue
        seen.append(when)
        actual = row.get("epsActual")
        if actual is not None:
            # ★ Reported: announced on the day, knowable that day.
            if when > as_of:
                continue
            findings.append(Finding(
                symbol, "earnings_reported", reported_sev, when, when,
                {"eps_actual": _num(actual),
                 "eps_estimated": _num(row.get("epsEstimated")),
                 "revenue_actual": _num(row.get("revenueActual")),
                 "revenue_estimated": _num(row.get("revenueEstimated")),
                 "surprise": _surprise(actual, row.get("epsEstimated"))},
                "fmp:earnings-calendar"))
        elif when >= as_of:
            # ⚠ Scheduled: knowable BECAUSE WE LOOKED TODAY, not on the date.
            findings.append(Finding(
                symbol, "earnings_scheduled", scheduled_sev, when, as_of,
                {"eps_estimated": _num(row.get("epsEstimated")),
                 "revenue_estimated": _num(row.get("revenueEstimated")),
                 "observed_as_of": as_of.isoformat(),
                 # ⚠⚠ A scheduled date moves. Said, so a PIT consumer cannot
                 #   mistake today's calendar for a historical one (DE-65).
                 "caveat": "the CURRENT schedule only — a scheduled date moves, "
                           "and this feed keeps no history of what it once said"},
                "fmp:earnings-calendar"))

    store.upsert(findings)
    if not seen:
        return {"findings": 0, "refreshed": [], "truncated": truncated,
                "why": "the earnings calendar returned no dated rows"}

    reached_from, reached_to = min(seen), max(seen)
    recorded = []
    if truncated:
        # ⚠⚠ NOT recorded. An uncovered chunk means unseen names inside the
        #   window, and CHECKED would claim them (DE-58).
        capped = [t for t in truncated if t["cause"] == "capped"]
        refused = [t for t in truncated if t["cause"] == "refused"]
        parts = []
        if capped:
            parts.append(f"{len(capped)} chunk(s) still AT the {ROW_CAP}-row cap "
                         f"after splitting ({capped[0]['span']})")
        if refused:
            parts.append(f"{len(refused)} chunk(s) REFUSED by the feed "
                         f"({refused[0]['span']}) — ★ measured 2026-08-28, this "
                         f"plan answers 402 beyond about one year back, so the "
                         f"reachable history is a ROLLING WINDOW, not the range "
                         f"asked for")
        why = ("⚠⚠ the window is NOT fully covered, so neither class is recorded "
               "as refreshed: " + "; ".join(parts))
    else:
        for name in ("earnings_reported", "earnings_scheduled"):
            store.record_refresh(name, reached_from, reached_to,
                                 covers_tickers=tuple(sorted(wanted)))
            recorded.append(name)
        why = (f"★ {len(spans)} chunk(s), none at the cap — the window is "
               f"covered. ⚠ `earnings_scheduled` reflects the CURRENT schedule "
               f"only; a scheduled date moves and this feed keeps no history")

    return {"findings": len(findings), "refreshed": recorded,
            "reached": f"{reached_from}..{reached_to}",
            "chunks": len(spans), "truncated": truncated,
            "reported": sum(1 for f in findings
                            if f.event_class == "earnings_reported"),
            "scheduled": sum(1 for f in findings
                             if f.event_class == "earnings_scheduled"),
            "why": why}


def _fetch_span(client, start: date, end: date, *, depth: int):
    """Rows for `start..end`, ★ **halving the window when it hits the cap.**

    ⚠ A response *at* the cap is indistinguishable from one that was truncated,
    so it is treated as truncated. Returns `(rows, spans, truncated)`.
    """
    try:
        rows = client.get("earnings-calendar", **{"from": start.isoformat(),
                                                  "to": end.isoformat()}) or []
    except Exception as exc:                       # noqa: BLE001 — named
        # ⚠ A REFUSAL, not a cap — measured 2026-08-28, this plan answers 402
        #   beyond about one year back. ★ Both leave the window uncovered, but
        #   saying "the cap" of a 402 would send a reader to the wrong fix.
        return [], [], [{"span": f"{start}..{end}", "cause": "refused",
                         "detail": str(exc)[:90]}]

    if len(rows) < ROW_CAP:
        return rows, [(start, end)], []
    if depth >= MAX_SPLIT_DEPTH or start >= end:
        # ⚠ Admitted, never hidden: this window could not be covered.
        return rows, [(start, end)], [{"span": f"{start}..{end}",
                                       "cause": "capped",
                                       "detail": f"still {len(rows)} rows at "
                                                 f"depth {depth}"}]

    middle = start + (end - start) / 2
    left = _fetch_span(client, start, middle, depth=depth + 1)
    right = _fetch_span(client, middle + timedelta(days=1), end, depth=depth + 1)
    return (left[0] + right[0], left[1] + right[1], left[2] + right[2])


def _surprise(actual, estimated):
    """★ The FLAG-worthy content: actual against expectation, not the level."""
    a, e = _num(actual), _num(estimated)
    if a is None or e is None or e == 0:
        return None
    return round((a - e) / abs(e), 6)


def _num(value):
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _as_date(value):
    from datetime import date as _date

    try:
        return _date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None
