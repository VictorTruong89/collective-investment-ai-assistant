"""Class 5 `restatement_silent` — DE-24. ★ **No vendor: we diff ourselves.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  FMP HAS NO RESTATEMENT HISTORY.  IT SERVES ONE ANSWER: TODAY'S. ║
║  If a number changes, the old value is GONE, and nothing in the  ║
║  response indicates that it changed.                             ║
║                                                                  ║
║  ★ So the only detection available is TO HAVE KEPT A DATED       ║
║    EARLIER VALUE AND DIFF IT.  That is this module.              ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠⚠ **Measured 2026-08-28: this class can find NOTHING today, and that is the
finding.** Every one of the four observation field sets holds **exactly one
snapshot per ticker** — 191 rows, 0 tickers with a prior. ★ A diff needs two
observations, so the honest report is **UNCHECKED with its reason**, never
*"no restatements found"*. DE-35: *absence of evidence and evidence of absence
are different results, and conflating them is how a false assumption becomes a
silent one.*

⚠ **And a second limit, structural rather than temporal.** None of the four
field sets carries a period key — they are TTM and current-state snapshots. So
a changed value is **ambiguous by construction**: it may be a silent revision,
or simply a new quarter rolling into the trailing window. ★ The finding says
which, and never claims a restatement it cannot distinguish.
"""

from __future__ import annotations

from datetime import date

#: ★ Field sets whose payload is keyed to a reporting period. ⚠ Empty today —
#: all four observation sets are TTM/current-state, so every change they show
#: is ambiguous. A periodic set added later belongs here and its changes become
#: unambiguous restatements.
PERIOD_KEYED = frozenset()

#: ⚠ **Relative tolerance on numeric comparison** — an admitted choice (CN-10),
#: and not zero: a vendor re-serialising `0.1 + 0.2` is not a restatement. ★ It
#: is small enough that any real revision clears it by orders of magnitude.
REL_TOLERANCE = 1e-9

#: ⚠ Keys that move on their own and restate nothing — a changed price or
#: market cap is the market, not the accounts.
VOLATILE_KEYS = frozenset({"price", "marketCap", "lastDividend", "range",
                           "changePercentage", "change", "volume",
                           "averageVolume", "beta"})


def silent_changes(ledger, *, field_sets, tickers, as_of: date):
    """`(findings, status)` — ★ **and the status is the point.**

    Diffs the two most recent snapshots of each `(ticker, field_set)` and emits
    a `restatement_silent` finding per changed field.

    ⚠⚠ **A ticker with fewer than two snapshots is NOT clean — it is
    UNCHECKED.** It is counted in `status["no_prior"]` and deliberately kept
    out of the covered set, so the class cannot report `CHECKED` over names it
    could never have examined (DE-58's rule, DE-35's distinction).
    """
    import json

    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding

    severity = BY_NAME["restatement_silent"].severity
    wanted = [t.upper() for t in tickers]
    findings, comparable, no_prior, absent = [], [], [], []

    for field_set in field_sets:
        try:
            frame = ledger.read(field_set)
        except Exception:                          # noqa: BLE001
            continue
        if frame is None or not len(frame):
            absent.append(field_set)
            continue

        ambiguous = field_set not in PERIOD_KEYED
        for ticker in wanted:
            mine = frame[frame["ticker"] == ticker]
            if len(mine) < 2:
                no_prior.append((ticker, field_set))
                continue
            mine = mine.sort_values("observed_at", kind="mergesort")
            previous, latest = mine.iloc[-2], mine.iloc[-1]
            when = _as_date(latest["observed_at"])
            if when is None or when > as_of:
                continue                   # ⚠ DE-34 — not knowable to this run
            comparable.append((ticker, field_set))

            was = _payload(json.loads, previous["payload"])
            now = _payload(json.loads, latest["payload"])
            for key, old, new in _changed(was, now):
                findings.append(Finding(
                    ticker, "restatement_silent", severity, when, when,
                    {"field_set": field_set, "field": key,
                     "was": _plain(old), "now": _plain(new),
                     "prior_observed_at": str(previous["observed_at"])[:19],
                     # ⚠⚠ Without a period key a change may simply be a new
                     #   quarter entering the trailing window. ★ Said, never
                     #   silently resolved either way.
                     "ambiguous": ambiguous,
                     "why_ambiguous": (
                         "the field set carries no period key, so a new period "
                         "rolling into a TTM window is indistinguishable from a "
                         "revision of an already-reported one" if ambiguous else "")},
                    "derived:observation-ledger-diff"))

    status = {
        "comparable": sorted({t for t, _ in comparable}),
        "no_prior": sorted({t for t, _ in no_prior}),
        "absent_field_sets": absent,
        "why": "",
    }
    if not comparable:
        status["why"] = (
            f"⚠ UNCHECKED — {len(status['no_prior'])} name(s) hold fewer than "
            f"two snapshots, so there is no prior value to diff against. ★ This "
            f"is NOT 'no restatements found': the class becomes checkable only "
            f"after a SECOND dated ingest (DE-24, DE-35)")
    return findings, status


def record(store, findings, status, *, as_of: date) -> list:
    """Upsert and record the refresh — ★ **over the comparable names only.**

    ⚠ Recording the whole universe would claim a coverage the diff never had,
    which is DE-58's defect. With no comparable name, **nothing is recorded**
    and the class stays `UNCHECKED` with its reason.
    """
    store.upsert(findings)
    covered = status.get("comparable") or []
    if not covered:
        return []
    store.record_refresh("restatement_silent", as_of, as_of,
                         covers_tickers=tuple(covered))
    return ["restatement_silent"]


def _changed(was: dict, now: dict):
    """Field-level differences. ⚠ A key that APPEARS is not a restatement."""
    if not isinstance(was, dict) or not isinstance(now, dict):
        return
    for key in sorted(set(was) & set(now)):
        if key in VOLATILE_KEYS:
            continue
        old, new = was[key], now[key]
        if _same(old, new):
            continue
        yield key, old, new


def _same(old, new) -> bool:
    if old is None and new is None:
        return True
    if isinstance(old, bool) or isinstance(new, bool):
        return old == new
    if isinstance(old, (int, float)) and isinstance(new, (int, float)):
        scale = max(abs(float(old)), abs(float(new)), 1.0)
        return abs(float(old) - float(new)) <= REL_TOLERANCE * scale
    return old == new


def _payload(loads, raw):
    try:
        return loads(raw)
    except (TypeError, ValueError):
        return {}


def _plain(value):
    """⚠ Findings are stored as JSON — a numpy scalar would not round-trip."""
    if isinstance(value, (str, bool)) or value is None:
        return value
    if isinstance(value, (int, float)):
        return float(value) if isinstance(value, float) else int(value)
    return str(value)


def _as_date(value):
    from datetime import date as _date

    try:
        return _date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None
