"""Class-B capture — FMP snapshots into the `ObservationLedger`. **DE-6.8/6.10.**

★★ **`ObservationLedger.snapshot()` existed and nothing ever called it.** The
same shape as the fact ledger and the two run stores: a correct writer with no
caller, so `get()` answered `None` truthfully forever and D-01's `_profile_part`
returned `None` on every run.

⚠ The consequence was not cosmetic. The bundle NVDA and SNDK were judged on
carried **five EDGAR line items and nothing else** — no sector, no business
description, no ratios — and all three authoring passes returned
`INSUFFICIENT_DATA`. **The model was not being cautious; it was right.**

★ `snapshot()` already does DE-6.10 change detection, so a capture that changed
nothing appends no row: *the ledger records changes, so its size tracks
information rather than uptime.*
"""

from __future__ import annotations

from datetime import date

from src.data_engine.observation.schedule import DEFAULT_SCHEDULE

#: The field sets a thesis bundle draws on. ⚠ Deliberately **not** the whole of
#: `DEFAULT_SCHEDULE`: `analyst_estimates`, `price_target_consensus` and
#: `grades_consensus` are other people's opinions, and **RA-12/RA-19 keep the
#: judging layer away from them** — a thesis that reads the consensus before
#: forming a view is measuring agreement, not the business.
THESIS_FIELD_SETS = ("profile", "ratios_ttm", "key_metrics_ttm",
                     "financial_scores")


def capture(client, ledger, *, ticker: str, as_of: date,
            field_sets=THESIS_FIELD_SETS) -> dict:
    """Capture the due field sets for one ticker. Returns `{field_set: written}`.

    ⚠ **Cadence is respected, not ignored** — `DEFAULT_SCHEDULE`'s intervals are
    *admitted guesses* (CN-10) and are used as declared rather than replaced
    with better-sounding ones this module has no evidence for.

    ★ A fetch failure is recorded as `False` and does not abort the sweep: one
    unavailable endpoint must not cost the other three, and the caller can see
    which fell out.
    """
    written = {}
    for field_set in field_sets:
        plan = DEFAULT_SCHEDULE.get(field_set)
        if plan is None:
            written[field_set] = False
            continue
        endpoint, cadence_days, _why = plan
        if not is_due(ledger, ticker=ticker, field_set=field_set, as_of=as_of,
                      cadence_days=cadence_days):
            written[field_set] = False
            continue
        try:
            payload = client.get(endpoint, symbol=ticker.upper())
        except Exception:                      # noqa: BLE001 — see the docstring
            written[field_set] = False
            continue
        # ⚠ FMP answers these as a ONE-ELEMENT LIST. Storing the list would make
        #   every consumer index into it, and a day the vendor returns two
        #   elements would silently change meaning.
        if isinstance(payload, list):
            payload = payload[0] if payload else None
        if not payload:
            written[field_set] = False
            continue
        written[field_set] = ledger.snapshot(
            ticker=ticker, field_set=field_set, payload=payload,
            source_endpoint=f"fmp:{endpoint}")
    return written


def is_due(ledger, *, ticker: str, field_set: str, as_of: date,
           cadence_days: int) -> bool:
    """Has this field set gone un-captured for longer than its cadence?

    ★ `consumer="display"` on the read: **DE-6.9 denies a Class-B live read to a
    PIT consumer**, and asking *"when did we last look?"* is not a PIT read — it
    is scheduling. ⚠ Using a PIT consumer name here would make the scheduler
    raise on exactly the field sets it exists to schedule.
    """
    latest = ledger.get(ticker=ticker, field_set=field_set, consumer="display")
    if latest is None:
        return True
    observed = latest["observed_at"].date()
    return (as_of - observed).days >= cadence_days
