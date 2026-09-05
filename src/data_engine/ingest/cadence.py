"""AB-14's other half — ★ **which classes are DUE, and which are merely old.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  QD-16 RULES OUT A PER-RUN SWEEP: 510 tickers x 18 classes is    ║
║  thousands of calls per run against a 300/min cap.  So the store  ║
║  is INCREMENTALLY MAINTAINED and the daily run is a READER.       ║
║                                                                  ║
║  ⚠ THIS DOES NOT DECIDE A CRON SCHEDULE.  It answers a different  ║
║    question — "what is stale RIGHT NOW" — which is the one a      ║
║    scheduler of any period needs, and the one a human needs when  ║
║    deciding whether today's run can be trusted.                  ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **Cadence follows severity, not convenience.** A `BLOCK` class going stale can
halt the run or, worse, let a real split through unhandled; a `NOTE` class going
stale costs a reader some context. ⚠ Giving them one interval would either
hammer the rate limit for news or leave splits unchecked for a week.

⚠⚠ **Staleness is measured from the refresh the store RECORDED**, never from
when the sweep was last *invoked*: a sweep that ran and covered nothing must not
reset the clock. That is DE-58's rule applied to time instead of to names.
"""

from __future__ import annotations

from datetime import date

#: ★ Maximum age in **days** before a class is DUE, by severity.
#: ⚠ Admitted choices (CN-10), and the ordering is the argument: a BLOCK class
#: is refetched an order of magnitude more often than a NOTE one.
MAX_AGE_BY_SEVERITY = {"BLOCK": 1, "FLAG": 7, "NOTE": 30}

#: ⚠ A class that has NEVER been refreshed is due, not merely old — and it is
#: reported separately, because *"never"* and *"stale"* need different fixes.
NEVER = "never refreshed"


def due(store, classes, *, as_of: date, max_age=None, derived=()) -> dict:
    """`{"due": [...], "never": [...], "fresh": [...], "exempt": [...]}`.

    `classes` is the `EVENT_CLASSES` sequence. ★ A class that cannot be swept —
    `permanently_unchecked` — is **exempt**, not perpetually due: reporting
    `index_membership` as overdue every day would train a reader to ignore the
    whole report.

    ⚠ `derived` names classes computed **at check time** from data already held.
    They have no refresh to be stale and must not be reported as *never
    refreshed* — that would contradict the class listing, which calls them
    finished by construction.

    ⚠ **This does not fetch and does not decide when to run.** It reports state,
    so a cron of any period, a human, or the daily run's own precondition can
    each ask the same question and get the same answer.
    """
    fresh_map = store.freshness() or {}
    out = {"due": [], "never": [], "fresh": [], "exempt": []}
    ages = max_age or MAX_AGE_BY_SEVERITY

    derived_names = set(derived)
    for spec in classes:
        if getattr(spec, "permanently_unchecked", False) or spec.name in derived_names:
            out["exempt"].append(spec.name)
            continue
        state = fresh_map.get(spec.name)
        if not state:
            out["never"].append(spec.name)
            continue
        when = _as_date(state.get("refreshed_at") or state.get("to"))
        limit = ages.get(spec.severity, 7)
        if when is None or (as_of - when).days > limit:
            out["due"].append(spec.name)
        else:
            out["fresh"].append(spec.name)
    return out


def report(state: dict) -> str:
    """One human line per group. ★ **What is missing leads**, not what is fine."""
    lines = []
    if state["never"]:
        lines.append(f"⚠⚠ {len(state['never'])} class(es) NEVER refreshed — "
                     f"a gate over them reports UNCHECKED: "
                     f"{', '.join(sorted(state['never']))}")
    if state["due"]:
        lines.append(f"⚠ {len(state['due'])} class(es) DUE: "
                     f"{', '.join(sorted(state['due']))}")
    if state["exempt"]:
        # ⚠ Two different reasons live here — no source at any price, and
        #   derived at check time. ★ Saying only the first would mislabel a
        #   finished class as an unobtainable one.
        lines.append(f"✗ {len(state['exempt'])} exempt (no source, or derived "
                     f"at check time): {', '.join(sorted(state['exempt']))}")
    lines.append(f"✓ {len(state['fresh'])} fresh")
    return "\n".join(lines)


def _as_date(value):
    from datetime import date as _date

    try:
        return _date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None
