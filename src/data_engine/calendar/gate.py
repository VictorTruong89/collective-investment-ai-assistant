"""§6A's gate with the one handling QD-15 defines — **one implementation.**

★ Both callers need the same thing: run `calendar_check` over a window and
record that BLOCK-severity actions are handled by the price adjustment. D-08's
daily run had it inline; D-04's training run had a **stub asserting
`PROCEED_WITH_FLAGS` without checking anything** (AB-9). ⚠ Two copies of one
idea is FE-4's defect, and the second copy is where the drift starts.

```text
╔══════════════════════════════════════════════════════════════════╗
║  ⚠⚠  `handled` is built from what the STORE holds in the window,  ║
║  not from what this run happened to seed.                         ║
║                                                                  ║
║  The daily run seeds nothing (events=()), so building `handled`   ║
║  from the seeded events yields {} — and the moment the store is   ║
║  populated by `ingest/events.py`, every split in it is UNHANDLED  ║
║  and the run HALTS.  The handling is a property of HOW THE PANEL  ║
║  IS DERIVED, not of where the finding came from.                  ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **The handling is RECORDED, never assumed.** `calendar_check` accepts a BLOCK
as cleared only through an explicit string — *"a BLOCK may only be cleared by an
explicit, recorded handling — never by an empty dict entry and never by severity
downgrade."*
"""

from __future__ import annotations

from datetime import date


#: ★★ **The classes the price adjustment actually addresses — and only these.**
#:
#: ⚠ *Found 2026-08-27 the moment `delisting` was ingested:* this handling used
#: to clear **every BLOCK-severity finding**, and while the store held only
#: splits that read as correct. Adding delistings marked **AVB and EQR
#: `handled=True`** — and *re-deriving the panel at `adj_as_of` does nothing for
#: a delisted name.* It has no forward price, its label is undefined, and it
#: cannot be traded.
#:
#: ⚠ **`EQR` was never one of them** (Victor, 2026-08-28). The feed's call was
#: wrong: SEC shows its CIK listing `VMRK`, still trading — **DE-67**. The pair
#: above is kept as the *finding as it stood*; only `AVB` is a real delisting.
#:
#: ★ QD-15: *"a BLOCK may only be cleared by an explicit, recorded handling"* — a
#: blanket one is not explicit, it just looks like it.
ADJUSTMENT_HANDLES = ("split", "reverse_split")

#: ★★ DE-76 / QD-15 (Victor, 2026-10-07: *"PIT store"*) — handled ONLY for a caller
#: that derives fundamentals per filing date (DE-75, FE-40). ⚠ Opt-in, never
#: blanket: a caller that reads once and joins across dates would show the
#: amended figure from the amendment on and nothing true for the gap before it.
PIT_FUNDAMENTALS_HANDLES = ("restatement_amended",)


def adjustment_handling(findings, *, adj_as_of, fundamentals_pit: bool = False) -> dict:
    """`{(ticker, class, date): why}` for the BLOCKs the adjustment **covers**.

    ★ QD-15's only defined handling: the panel is derived at the run's
    `adj_as_of` (DE-28), so a split inside the window is already applied to the
    series the features are built from.

    ⚠ **It does not cover a split whose adjustment has not been applied.** That
    is what `adj_as_of` pins — two panels over the same dates at different
    adjustment states are different data (DE-30), and this string names which.

    ⚠⚠ **And it does not cover a delisting.** See `ADJUSTMENT_HANDLES`: a class
    outside that tuple stays unhandled and the gate HALTs, which for a delisting
    is the right outcome — *a name that stopped trading is something a human
    should look at*, not something a price adjustment absorbs.
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import BLOCK

    handled = {}
    for f in findings:
        if BY_NAME[f.event_class].severity != BLOCK:
            continue
        key = (f.ticker, f.event_class, f.event_date)
        if f.event_class in ADJUSTMENT_HANDLES:
            handled[key] = f"panel derived at the run's adj_as_of {adj_as_of} (DE-28, QD-15)"
        elif fundamentals_pit and f.event_class in PIT_FUNDAMENTALS_HANDLES:
            # ★ DE-76 — the replay shows the original before the amendment's
            #   filing date and the amended figure from it: no look-ahead, no gap.
            handled[key] = ("fundamentals point-in-time per filing date: as filed "
                            "before the amendment, amended after (DE-75, DE-76, QD-15)")
    return handled


#: DE-78 — the store classes the price adjustment applies, and the adjuster's
#: own `event_type` for each. ★ A reverse split IS a split (ratio below one).
PRICE_EVENT_TYPES = {"split": "split", "reverse_split": "split", "dividend": "dividend"}


def price_events(store, *, tickers, adj_as_of) -> list:
    """DE-78 / AC-7.96 — the store's splits and dividends as `CorporateEvent`s.

    ★★★ The ONE source of the price adjustment for every panel builder. ⚠ Until
    2026-10-08 (`DX-166`) training and the daily run both called
    `build_price_panel(raw, (), adj_as_of)` on RAW prices: no split was ever
    applied, while `adjustment_handling` recorded every split as handled by
    *"the panel derived at adj_as_of"*. With these events passed, that record is
    true by construction — the gate and the panel read one store.

    Every event of the asked names with `event_date ≤ adj_as_of` (an adjustment
    as of a date includes every action effective by then).
    """
    import json

    from src.data_engine.pit.models import CorporateEvent

    frame = store.read()
    if frame is None or not len(frame):
        return []
    wanted = {t.upper() for t in tickers}
    out = []
    for row in frame.to_dict("records"):
        kind = PRICE_EVENT_TYPES.get(row.get("event_class"))
        ticker = str(row.get("ticker", "")).upper()
        if kind is None or ticker not in wanted:
            continue
        when = _as_date(row.get("event_date"))
        if when is None or when > adj_as_of:
            continue
        detail = row.get("detail") or {}
        if isinstance(detail, str):
            detail = json.loads(detail)
        out.append(CorporateEvent(
            ticker=ticker, event_type=kind, event_date=when,
            knowable_at=_as_date(row.get("knowable_at")) or when,
            detail=detail, source=str(row.get("source", ""))))
    return out


def check_window(*, store, universe, start: date, end: date, as_of: date,
                 adj_as_of, run_id: str, max_age_days: int = 1,
                 fundamentals_pit: bool = False):
    """`calendar_check` over `[start, end]`, with the adjustment handling recorded.

    ★ **The handling is derived from the STORE**, so it covers every BLOCK the
    gate can see — including findings written by an earlier refresh that this run
    did not seed.
    """
    from src.data_engine.calendar.check import calendar_check
    from src.data_engine.calendar.store import CachedEventFeed

    handled = adjustment_handling(_blocks_in_window(store, start, end, as_of),
                                  adj_as_of=adj_as_of, fundamentals_pit=fundamentals_pit)
    return calendar_check(
        tickers=universe, start=start, end=end, as_of=as_of,
        adj_as_of=adj_as_of, feed=CachedEventFeed(store, max_age_days=max_age_days),
        run_id=run_id, handled=handled)


def _blocks_in_window(store, start: date, end: date, as_of: date):
    """Every finding the store holds inside the window and knowable by `as_of`.

    ⚠ **Knowability, not the event date** (DE-34): a split announced after
    `as_of` is absent even though it sits in today's feed — the check is itself
    point-in-time, and handling something the run could not have known about
    would be look-ahead in the guard.
    """
    from src.data_engine.contracts import Finding

    frame = store.read()
    if frame is None or not len(frame):
        return []

    out = []
    for row in frame.to_dict("records"):
        event_date = _as_date(row.get("event_date"))
        knowable = _as_date(row.get("knowable_at"))
        if event_date is None or not (start <= event_date <= end):
            continue
        if knowable is not None and knowable > as_of:
            continue                       # ⚠ DE-34 — not knowable yet
        out.append(Finding(
            row["ticker"], row["event_class"], row.get("severity", ""),
            event_date, knowable or event_date, row.get("detail"),
            row.get("source", "")))
    return out


def _as_date(value):
    import pandas as pd

    if value is None or (isinstance(value, float) and value != value):
        return None
    return pd.Timestamp(value).date()


def delisted_names(store, *, as_of: date, tickers=None) -> dict:
    """`{ticker: reason}` for names the store says have stopped trading.

    ★★ **A current-state read, deliberately outside `check_window`.** §6A's gate
    is window-scoped, and *"has this name stopped trading?"* is not a question
    about a window — which is why a three-week delisting feed reports `UNCHECKED`
    against every real 200-day window and the BLOCKs never surface (AB-15).

    ⚠ **Knowability still applies** (DE-34): a delisting announced after `as_of`
    is not yet knowable, and barring a name on it would be look-ahead — the run
    would be acting on news it could not have had.

    ★★ **DE-67 — a knowable `ticker_change` supersedes the delisting.** The feed
    sees a symbol go dark and **cannot tell a rebrand from an exit**; SEC's
    registrant index carries the fact explicitly. ⚠ *Measured 2026-08-28:* FMP
    called `EQR` a delisting on 2026-08-18 while CIK `0000906107` listed `VMRK`,
    which priced **41 bars through 2026-08-27** — barring it drops a live name.

    ⚠ **Un-barred is not declared fine.** The delisting row stays in the store
    and the `ticker_change` is still a **BLOCK** demanding DE-66's explicit
    handling. Clearing both here would be the severity downgrade QD-15 forbids.
    """
    frame = store.read()
    if frame is None or not len(frame):
        return {}

    wanted = {t.upper() for t in tickers} if tickers else None

    def knowable_of(row):
        """⚠ DE-34's axis — `knowable_at`, falling back to the event date."""
        return _as_date(row.get("knowable_at")) or _as_date(row.get("event_date"))

    records = frame.to_dict("records")

    # ★ DE-67 — collected FIRST, because a rename decides whether the delisting
    #   of the same ticker means anything. ⚠ Knowability cuts both ways: a
    #   rename the run could not have known must not retroactively un-bar a
    #   name, which would be look-ahead used to RELAX a guard.
    renamed = set()
    for row in records:
        if row.get("event_class") != "ticker_change":
            continue
        knowable = knowable_of(row)
        if knowable is not None and knowable <= as_of:
            renamed.add(str(row.get("ticker", "")).upper())

    out = {}
    for row in records:
        if row.get("event_class") != "delisting":
            continue
        ticker = str(row.get("ticker", "")).upper()
        if wanted is not None and ticker not in wanted:
            continue
        if ticker in renamed:
            continue                       # ★ DE-67 — identity beats the feed
        knowable = knowable_of(row)
        if knowable is None or knowable > as_of:
            continue                       # ⚠ DE-34 — not knowable yet
        when = _as_date(row.get("event_date"))
        detail = row.get("detail") or ""
        out[ticker] = (f"delisted {when} ({detail}) — a name that has stopped "
                       f"trading may not be nominated (QA-125)")
    return out
