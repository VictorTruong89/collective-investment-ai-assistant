"""QA-125 — D-03 never nominates a name that cannot be traded.

★★ **This exists because the exclusion was working by accident.** `AVB` and
`EQR` delisted on 17 and 18 August 2026 and left the ranking **only because they
print no bar on the as-of date** — `rank_by_model` selects `panel[date ==
as_of]`. A name that delisted *today* and still printed a bar would have ranked
normally, and nothing would have said so.

```text
╔══════════════════════════════════════════════════════════════════╗
║  §6A's calendar gate CANNOT cover this, and no ingest fixes it.  ║
║                                                                  ║
║  "Has any name stopped trading?" is a CURRENT-STATE question.    ║
║  The calendar gate is WINDOW-SCOPED by construction, so a         ║
║  three-week delisting feed reports UNCHECKED against every real   ║
║  200-day window — honestly, and uselessly (AB-15, DE-60).         ║
║                                                                  ║
║  So the check belongs where the ranking is made.                  ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **Excluded, never silently dropped.** DE-13's rule one domain over: *a missing
name is not dropped and does not become a row of NaNs*. An untradeable name
leaves `candidates` and appears in `excluded[]` **with its reason**, so a reader
can tell a name that was beaten from a name that was barred.

★ **Tradeability is SUPPLIED, not fetched** (QA-126). D-03 ranks D-02's numbers
and computes none of its own; reaching into D-07's event store here would make
the ranking layer a data client.
"""

from __future__ import annotations

from datetime import date

#: ★ How many sessions a name may go without a bar before it is untradeable.
#:
#: ⚠ **An admitted choice** (CN-10), and it is not zero on purpose: a name can
#: miss the as-of date for reasons that are not delisting — a trading halt, a
#: late vendor file, an exchange holiday the calendar disagrees about. ★ Two
#: sessions distinguishes *"no print today"* from *"stopped printing"*.
STALE_SESSIONS = 2


def untradeable(panel, *, as_of: date, delisted=None,
                stale_sessions: int = STALE_SESSIONS) -> dict:
    """`{ticker: reason}` for every name that must not be nominated.

    `delisted` is `{ticker: reason}` supplied by the caller from D-07's event
    store — ★ **supplied, not fetched** (QA-126).

    Two independent grounds, and the second is the one that catches what the
    calendar gate cannot:

    * **Delisted** — the store says the name stopped trading.
    * **Stale** — its last bar is more than `stale_sessions` behind the panel's
      own latest date. ⚠ Measured against **the panel**, not against a calendar:
      a market holiday moves every name together and must not mark the whole
      universe untradeable.
    """
    import pandas as pd

    out = {str(k).upper(): str(v) for k, v in (delisted or {}).items()}
    if panel is None or not len(panel):
        return out

    dates = pd.to_datetime(panel["date"])
    latest = dates.max()
    if pd.isna(latest):
        return out

    # ★ Sessions the PANEL has, not days on a calendar.
    sessions = sorted(dates.dt.date.unique())
    cutoff = sessions[max(len(sessions) - 1 - stale_sessions, 0)]

    last_bar = panel.assign(_d=dates.dt.date).groupby("ticker")["_d"].max()
    for ticker, seen in last_bar.items():
        name = str(ticker).upper()
        if name in out:
            continue                      # already barred, and the reason stands
        if seen < cutoff:
            out[name] = (f"last bar {seen} is more than {stale_sessions} "
                         f"sessions behind the panel's {sessions[-1]} — the name "
                         f"has stopped printing (QA-125)")
    return out


def apply_exclusions(candidates, barred: dict) -> tuple:
    """Return `(kept, excluded)` — ★ **both**, and the second carries reasons.

    ⚠⚠ **`excluded` is built from EVERY barred name, not from the candidates
    that happened to be barred.** *Measured 2026-08-27:* `AVB` and `EQR` are
    delisted **and absent from the day's cross-section**, because they print no
    bar on the as-of date — so filtering the candidate list recorded **nothing**,
    and a reader still could not tell they had been barred. That is the same
    silent drop this function exists to prevent.

    ★ The barred set is the authority; the candidate list is only where the
    filtering happens to bite.

    ⚠ Ranks are **renumbered** over what survives. Leaving a gap where a barred
    name was would make `rank` and position disagree, and D-12 reads the top of
    this list as the nomination.
    """
    kept = [dict(c) for c in candidates
            if str(c.get("ticker", "")).upper() not in barred]
    for position, candidate in enumerate(kept, start=1):
        candidate["rank"] = position

    excluded = tuple({"ticker": ticker, "reason": reason}
                     for ticker, reason in sorted(barred.items()))
    return tuple(kept), excluded


def assert_something_tradeable(kept, excluded) -> None:
    """⚠ **An empty slate is a failure, never a quiet nomination of nothing.**

    ★ P5 — if every name in the universe is barred, the run must say so. A
    nomination with no candidates would reach D-12 as *"no opportunity today"*,
    which is a judgement nobody made.
    """
    from src.quant.errors import QuantError

    if kept:
        return
    raise QuantError(
        f"every candidate is untradeable ({len(excluded)} excluded) — there is "
        f"no ranking to publish. ★ An empty slate reaching D-12 would read as "
        f"'no opportunity today', which is a judgement nobody made (QA-125, P5)")
