"""`python -m src.data_engine.ingest` — the sweeps §6A assumes someone runs.

★ **This exists because `ingest/events.py` had no caller.** DE-56 fixed a gate
that reported `CHECKED` having fetched nothing; the maintainer that populates the
store was built in the same change and **nothing could invoke it**, which is the
same *built-but-never-called* shape it was fixing.

⚠ **A schedule is still not decided.** QD-16 rules out a per-run sweep — *"510
tickers × 8 classes is thousands of calls per run against a 300/min cap"* — so
§6A's design is an **incrementally maintained** store. This makes the maintenance
runnable; **how often it runs is Victor's call** (AB-14).

```text
   python -m src.data_engine.ingest events   --universe sp500 --years 10
   python -m src.data_engine.ingest facts    --universe sp500
   python -m src.data_engine.ingest symbols  --universe sp500   # §6B identity
   python -m src.data_engine.ingest status
```
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

EXIT_OK, EXIT_FAILED = 0, 1

#: ★ Classes computed AT CHECK TIME from data already held — they have no
#: ingest and need none. ⚠ Reporting them as *"no ingest built"* would put a
#: permanent to-do against something that is finished by construction.
DERIVED_AT_CHECK = {
    "price_adjustment_state": ("derived by `calendar.check.price_adjustment_status` "
                               "from the panel's own `adj_as_of` — nothing to "
                               "ingest, and it is CHECKED on every run"),
}

#: ⚠⚠ **Classes whose ingest EXISTS and which still cannot report coverage.**
#: ★ Without this state a built class reads as *"no ingest built"*, which
#: understates the work and hides the real reason it is `UNCHECKED` (DE-35 —
#: the two absences are different).
BUILT_BUT_UNCOVERED = {
    "restatement_silent": ("it diffs our OWN dated ingests (DE-24), so it needs "
                           "a SECOND snapshot per name — today every field set "
                           "holds exactly one"),
}


def _state(sub: str) -> Path:
    root = Path(os.environ.get("PIPELINE_STATE_DIR", ".state")) / sub
    root.mkdir(parents=True, exist_ok=True)
    return root


def _universe(name: str) -> tuple:
    """The name list, read from config — ★ **not imported from another domain.**

    ⚠ An earlier draft imported `load_universe` from `src.orchestration` and
    `load_sp500` from `src.models`. **ST-2's one-way import rule forbids both**,
    and D-05's architecture test caught it. ★ A universe is *data*: D-07 already
    owns `load_cik_map`, and a watchlist is a YAML key — neither needs a domain.
    """
    from src.data_engine.ingest.edgar_facts import load_cik_map

    if name == "sp500":
        return tuple(sorted(load_cik_map()))

    import yaml

    with open("config/settings.yaml", encoding="utf-8") as handle:
        settings = yaml.safe_load(handle) or {}
    return tuple((settings.get("pipeline") or {}).get("tickers") or ())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="src.data_engine.ingest",
        description="Maintain D-07's stores. ★ Separate from the daily run (P7).")
    sub = parser.add_subparsers(dest="what", required=True)

    for name, helptext in (
            ("events", "corporate actions into the EventStore (§6A's gate reads it)"),
            ("facts", "EDGAR companyfacts into the FactLedger"),
            ("symbols", "§6B — SEC ticker snapshot into the symbol history, and "
                        "ticker_change findings into the EventStore"),
            ("status", "what each store holds, and what it does NOT")):
        child = sub.add_parser(name, help=helptext)
        if name != "status":
            child.add_argument("--universe", choices=("sp500", "watchlist"),
                               default="sp500")
            child.add_argument("--as-of", type=date.fromisoformat, default=None)
        if name == "events":
            child.add_argument("--years", type=int, default=10)

    args = parser.parse_args(argv)
    if args.what == "status":
        return _status()

    as_of = args.as_of or datetime.now(timezone.utc).date()
    universe = _universe(args.universe)
    print(f"{args.what}: {len(universe)} names · as-of {as_of}")

    if args.what == "events":
        return _events(universe, as_of, years=args.years)
    if args.what == "symbols":
        return _symbols(universe, as_of)
    return _facts(universe)


def _symbols(universe, as_of: date) -> int:
    """§6B — snapshot SEC, diff on CIK, record the renames. **DE-62.**

    ★ **No vendor call and no web search**: the whole detection is a diff of two
    dated SEC files, and SEC's is free.

    ⚠⚠ Two results, kept apart. A `ticker_change` is a **finding**; a CIK that
    vanished is a **candidate for investigation** and never a delisting — *`XOM`
    vanished from the file on 2026-08-28 and Exxon Mobil priced normally that
    day* (DE-62, DE-35).
    """
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.edgar_facts import load_cik_map
    from src.data_engine.symbology.detect import (
        close_out, detect_changes, mappings_from, sec_snapshot)
    from src.data_engine.symbology.master import SymbolHistory
    from src.shared.secrets import Secret

    contact = os.environ.get("EDGAR_CONTACT") or os.environ.get("GMAIL_SMTP_USER")
    if not contact:
        print("BLOCKED: EDGAR_CONTACT is not set — SEC answers a User-Agent "
              "without a contact address with 403 (DE-8)", file=sys.stderr)
        return EXIT_FAILED

    held = {cik: ticker for ticker, cik in load_cik_map().items()
            if ticker in set(universe)}
    live = sec_snapshot(Secret("EDGAR_CONTACT", contact))
    findings, vanished = detect_changes(held, live, knowable_at=as_of)

    history = SymbolHistory(_state("symbology"))
    history.append(mappings_from(live, knowable_at=as_of))
    close_out(history, findings, on=as_of)

    store = EventStore(_state("events"))
    store.upsert(findings)
    # ★ The class covers exactly the names we asked about, so a later gate over
    #   a WIDER universe reports UNCHECKED rather than inheriting our coverage.
    store.record_refresh("ticker_change", as_of, as_of, covers_tickers=universe)

    print(f"  {len(history.read())} mappings · {len(findings)} ticker_change")
    for finding in findings:
        detail = finding.detail
        flag = "  ⚠ AMBIGUOUS" if detail.get("ambiguous") else ""
        print(f"    {detail['from']:6s} -> {detail['to']:6s} "
              f"cik {detail['cik']}{flag}")
    if vanished:
        print(f"  ⚠ {len(vanished)} CIK(s) absent from SEC's file — "
              f"CANDIDATES for investigation, NOT delistings:")
        for cik, ticker in sorted(vanished.items(), key=lambda kv: kv[1]):
            print(f"    {ticker:6s} cik {cik}  → see "
                  f".claude/skills/ticker-went-silent/")

    _report_contamination(store, findings, as_of)
    return EXIT_OK


def _restatements(store, universe, as_of: date, *, since: date) -> None:
    """Classes 4, 7 and 11 — ★ **one EDGAR pass, three classes.**

    ⚠⚠ *Measured 2026-08-28:* FMP's filing index returns **zero `10-K/A` across
    all filers** in three separate windows while `10-Q/A` fills a page; EDGAR
    holds five for TSLA alone. ★ Same precedence as TTM — EDGAR wins where FMP
    omits (DE-69).

    ⚠ **Separate call, separate credential, separate failure mode.** A missing
    `EDGAR_CONTACT` must not take the FMP classes down with it.
    """
    from src.data_engine.ingest.edgar_facts import load_cik_map
    from src.data_engine.ingest.submissions import (
        SUBMISSION_CLASSES, refresh_restatements)
    from src.data_engine.src.edgar.client import EdgarClient
    from src.shared.secrets import Secret

    contact = os.environ.get("EDGAR_CONTACT") or os.environ.get("GMAIL_SMTP_USER")
    if not contact:
        print("  ⚠ restatements SKIPPED — EDGAR_CONTACT is not set, so class 4 "
              "stays UNCHECKED and says so (DE-35)", file=sys.stderr)
        return

    out = refresh_restatements(
        EdgarClient(Secret("EDGAR_CONTACT", contact)), store,
        tickers=universe, cik_map=load_cik_map(), as_of=as_of, since=since,
        # ★★ Three classes from ONE submissions pass — fetching it three
        #    times would triple EDGAR's throttled cost for nothing.
        classes=SUBMISSION_CLASSES)
    print(f"  EDGAR filings: {out['findings']} "
          f"({out.get('amended', 0)} amended · "
          f"{out.get('non_reliance', 0)} non-reliance 8-K) · "
          f"by class {out.get('by_class', {})} · refreshed {out['refreshed']}")
    if out.get("why"):
        print(f"    {out['why']}", file=sys.stderr)


def _disclosures(client, store, universe, as_of: date, *, since: date) -> None:
    """Classes 13, 14, 15 — the **FLAG/NOTE tail**, per-ticker feeds.

    ⚠⚠ *Measured:* `grades` **ignores `limit`** — 1 791 rows for AAPL back to
    2012 whatever is asked. ★ The window is enforced client-side, or one NOTE
    class would put ~900 000 rows in the store.

    ⚠ **A NOTE that fails is not a reason to fail the sweep** — the gate cannot
    BLOCK on it. Each class reports the names it reached, and coverage excludes
    the rest (DE-58).
    """
    from src.data_engine.ingest.disclosures import (
        refresh_analyst_actions, refresh_beneficial_ownership, refresh_news)

    for label, fn in (("beneficial ownership", refresh_beneficial_ownership),
                      ("analyst actions", refresh_analyst_actions),
                      ("news", refresh_news)):
        try:
            out = fn(client, store, tickers=universe, as_of=as_of, since=since)
        except Exception as exc:                   # noqa: BLE001 — named
            print(f"  ⚠ {label} SKIPPED: {str(exc)[:110]}", file=sys.stderr)
            continue
        print(f"  {label}: {out['findings']} · "
              f"{len(out.get('reached', ()))} names · "
              f"refreshed {out['refreshed']}")
        if out.get("why"):
            print(f"    {out['why']}", file=sys.stderr)


def _macro(client, store, as_of: date, *, since: date) -> None:
    """Class 16 — ★ **the one class with no ticker.**

    ⚠⚠ *Measured:* `economic-calendar` truncates like `earnings-calendar`, and
    **non-monotonically** — asking for a year returned FEWER rows and less
    history than asking for a month. ★ The tell is the returned *span*.
    """
    from src.data_engine.ingest.macro import refresh_macro

    try:
        out = refresh_macro(client, store, as_of=as_of, since=since)
    except Exception as exc:                       # noqa: BLE001 — named
        print(f"  ⚠ macro SKIPPED: {str(exc)[:110]}", file=sys.stderr)
        return
    print(f"  macro: {out['findings']} releases · "
          f"reached {out.get('reached', 'nothing')} · "
          f"refreshed {out['refreshed']}")
    if out.get("why"):
        print(f"    {out['why']}", file=sys.stderr)


def _silent_restatements(store, universe, as_of: date) -> None:
    """Class 5 — DE-24. ★ **No vendor: the observation ledger diffs itself.**

    ⚠⚠ **This will report UNCHECKED until a SECOND dated ingest exists**, and
    that is the correct output, not a shortfall: FMP serves only today's answer,
    so the only detection available is to have kept a dated earlier value. ★ One
    snapshot cannot be diffed, and calling that *"no restatements"* is exactly
    the conflation DE-35 forbids.
    """
    from src.data_engine.ingest.silent import record, silent_changes
    from src.data_engine.observation.ledger import ObservationLedger
    from src.data_engine.observation.schedule import DEFAULT_SCHEDULE

    # ★ The schedule is keyed BY field set, so its keys are the names.
    field_sets = tuple(DEFAULT_SCHEDULE)
    ledger = ObservationLedger(_state("obs"))
    findings, status = silent_changes(ledger, field_sets=field_sets,
                                      tickers=universe, as_of=as_of)
    refreshed = record(store, findings, status, as_of=as_of)

    print(f"  silent restatements: {len(findings)} across "
          f"{len(status['comparable'])} comparable name(s) · "
          f"refreshed {refreshed}")
    if status.get("why"):
        print(f"    {status['why']}", file=sys.stderr)


def _report_contamination(store, findings, as_of: date) -> None:
    """DE-68 — ⚠⚠ **is a "delisted" name printing the successor's series?**

    ★★ **The one check the identity diff can never make.** `AVB` is invisible to
    it — its CIK never changed ticker — so no amount of SEC data surfaces it.
    The *prices* do: a retired name that has started printing another's series
    is visible from arithmetic. *Measured 2026-08-28: `AVB` → `VMRK`, 08-18.*

    ⚠ **This step DOES call the vendor**, unlike the diff above, which is why it
    is reported separately and kept to the smallest possible set: the names the
    store already calls `delisting`, against the successors the diff just named.
    ★ It degrades to a printed note rather than failing the sweep — a
    contamination check that cannot run is not a reason to lose the renames.
    """
    from src.data_engine.symbology.combination import contaminated_by

    successors = sorted({f.detail["to"] for f in findings})
    if not successors:
        return
    # ⚠ Not `delisted_names` — DE-67 now SUPPRESSES exactly the names we most
    #   need to test here. The suspects are the raw delisting rows.
    frame = store.read()
    suspects = sorted({str(r["ticker"]).upper() for r in frame.to_dict("records")
                       if r.get("event_class") == "delisting"}) if len(frame) else []
    if not suspects:
        return

    print(f"  contamination check: {len(suspects)} delisted × "
          f"{len(successors)} successor(s) — ⚠ this step calls the vendor")
    try:
        closes = _closes_for(sorted(set(suspects) | set(successors)), as_of)
        found = contaminated_by({t: closes[t] for t in suspects if t in closes},
                                {t: closes[t] for t in successors if t in closes})
    except Exception as exc:                              # noqa: BLE001 — named
        print(f"    note: contamination check did not run: {exc}", file=sys.stderr)
        return

    if not found:
        print("    ✓ no delisted name is printing a successor's series")
        return
    for suspect, hits in sorted(found.items()):
        for successor, when in hits:
            flag = "  ⚠ AMBIGUOUS" if len(hits) > 1 else ""
            print(f"    ⚠⚠ {suspect:6s} prints {successor}'s series from {when}"
                  f"{flag}")
    print("    ★ these bars are NOT that name's — every feature computed across "
          "the changeover carries a return that never happened (DE-61, DE-68)")
    print("    → confirm the cause with .claude/skills/ticker-went-silent/, "
          "then record it with symbology.combination.combination_findings()")


def _closes_for(tickers, as_of: date, *, days: int = 120) -> dict:
    """`{ticker: {date: close}}`. ⚠ The window must reach **before** any
    changeover — DE-68 raises rather than answering from too short a one."""
    from datetime import timedelta

    from src.data_engine.src.fmp import prices as fmp_prices
    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret

    client = FMPClient(Secret("FMP_API_KEY", os.environ["FMP_API_KEY"]))
    start = as_of - timedelta(days=days)
    out = {}
    for ticker in tickers:
        try:
            rows = fmp_prices.raw_prices(client, ticker, start, as_of)
        except Exception:                                 # noqa: BLE001
            continue                       # ⚠ a name we cannot price is silent
        if rows is None or not len(rows):
            continue
        # ★ `close_minor` — integers (CT-7.1), so the equality test is exact
        #   rather than dependent on the vendor's float rounding.
        out[ticker] = {d.date() if hasattr(d, "date") else d: c
                       for d, c in zip(rows["date"], rows["close_minor"])}
    return out


def _events(universe, as_of: date, *, years: int) -> int:
    """⚠ **Whole universe or no refresh recorded.** A partial sweep leaves the
    rest unchecked, and DE-36 says an unhandled split on an excluded name
    *contaminates every other name's rank*."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import refresh
    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret

    key = os.environ.get("FMP_API_KEY")
    if not key:
        print("BLOCKED: FMP_API_KEY is not set", file=sys.stderr)
        return EXIT_FAILED

    start = as_of - timedelta(days=365 * years)
    from src.data_engine.ingest.events import refresh_delistings

    client, store = FMPClient(Secret("FMP_API_KEY", key)), EventStore(_state("events"))
    outcome = refresh(client, store, tickers=universe, start=start, end=as_of)
    print(f"  {outcome['findings']} findings · refreshed {outcome['refreshed']}")

    # ★ Separate call, separate reachable window — see `refresh_delistings`.
    delisted = refresh_delistings(client, store, tickers=universe, as_of=as_of)
    print(f"  delistings: {delisted['findings']} in the universe · "
          f"reached {delisted.get('reached', 'nothing')}")
    if delisted.get("why"):
        print(f"    {delisted['why']}", file=sys.stderr)

    # ★★ The event that PRECEDES the silence — a combination is filed months
    #    before the ticker stops printing. ⚠⚠ But the pair is S-4
    #    filer/subject, NOT acquirer/target: measured, 4 of 6 universe matches
    #    were split-offs or divestitures where our name is the PARENT.
    from src.data_engine.ingest.events import refresh_ma_announcements

    _restatements(store, universe, as_of, since=start)
    _silent_restatements(store, universe, as_of)

    # ⚠⚠ Chunked on purpose — `earnings-calendar` caps at 4 000 rows and
    #    TRUNCATES SILENTLY, keeping the latest. Asking for 2026 returns
    #    November onward and says nothing (DE-58 a third time).
    from src.data_engine.ingest.earnings import refresh_earnings

    earn = refresh_earnings(client, store, tickers=universe, as_of=as_of,
                            since=start)
    print(f"  earnings: {earn['findings']} "
          f"({earn.get('reported', 0)} reported · "
          f"{earn.get('scheduled', 0)} scheduled) · "
          f"{earn.get('chunks', 0)} chunks · refreshed {earn['refreshed']}")
    if earn.get("why"):
        print(f"    {earn['why']}", file=sys.stderr)

    _disclosures(client, store, universe, as_of, since=start)
    _macro(client, store, as_of, since=start)

    mna = refresh_ma_announcements(client, store, tickers=universe, as_of=as_of,
                                   since=start)
    print(f"  M&A: {mna['findings']} in the universe "
          f"({mna.get('subjects', 0)} as S-4 SUBJECT — ⚠ a CANDIDATE to "
          f"investigate, NOT an acquisition) · "
          f"reached {mna.get('reached', 'nothing')}")
    if mna.get("why"):
        print(f"    {mna['why']}", file=sys.stderr)
    if outcome["failed"]:
        print(f"  ⚠ {len(outcome['failed'])} names failed: "
              f"{sorted(outcome['failed'])[:5]}", file=sys.stderr)
        print(f"  ⚠ {outcome['why']}", file=sys.stderr)
        return EXIT_FAILED
    return EXIT_OK


def _facts(universe) -> int:
    from src.data_engine.ingest.edgar_facts import ingest_facts, load_cik_map
    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.src.edgar.client import EdgarClient
    from src.shared.secrets import Secret

    contact = os.environ.get("GMAIL_SMTP_USER")
    if not contact:
        print("BLOCKED: GMAIL_SMTP_USER is not set (EDGAR needs a contact "
              "address in its User-Agent)", file=sys.stderr)
        return EXIT_FAILED

    client = EdgarClient(Secret("EDGAR_CONTACT", contact))
    ledger, cik_map = FactLedger(_state("facts")), load_cik_map()
    written = failed = 0
    for ticker in universe:
        cik = cik_map.get(ticker)
        if cik is None:
            continue
        try:
            written += ingest_facts(client, ledger, ticker=ticker, cik=cik)
        except Exception as exc:               # noqa: BLE001 — named, not fatal
            failed += 1
            print(f"  note: {ticker}: {str(exc)[:110]}", file=sys.stderr)
    print(f"  {written} new fact rows · {failed} names failed")
    return EXIT_OK


def _status() -> int:
    """★ **What each store does NOT hold, beside what it does.** ⚠ A status that
    lists only what is present reads as completeness (DE-35)."""
    from src.data_engine.calendar.classes import EVENT_CLASSES
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import SOURCED

    facts = sorted(_state("facts").glob("*.parquet"))
    print(f"facts      : {len(facts)} tickers")

    store = EventStore(_state("events"))
    fresh = store.freshness() or {}
    print(f"events     : {len(fresh)} of {len(EVENT_CLASSES)} classes refreshed")
    for spec in EVENT_CLASSES:
        state = fresh.get(spec.name)
        # ★ `permanently_unchecked` is the AUTHORITATIVE flag — ⚠ an earlier
        #   draft here labelled 13 classes *"no source in this project"* from a
        #   guess, when **only `index_membership` carries that flag**. The rest
        #   have declared sources (§5A.5) and simply have no ingest built.
        if spec.permanently_unchecked:
            mark, why = "✗", " — no source at any price, UNCHECKED permanently"
        elif state:
            covered = state.get("covers_tickers")
            mark = "✓"
            why = (f" — {len(covered)} names" if covered is not None
                   else " ⚠ coverage not recorded; reads as UNVERIFIABLE")
        elif spec.name in DERIVED_AT_CHECK:
            mark, why = "⊙", f" ★ DERIVED — {DERIVED_AT_CHECK[spec.name]}"
        elif spec.name in BUILT_BUT_UNCOVERED:
            # ⚠⚠ **Built and swept, and still not CHECKED** — a third state the
            #   marks above could not express. `restatement_silent` diffs our
            #   OWN dated ingests (DE-24), so with one snapshot per name there
            #   is no prior to compare and the honest answer is UNCHECKED.
            #   ★ Reporting it as "no ingest built" understates it; reporting it
            #   as swept would overstate it (DE-35).
            mark, why = "◐", f" ⚠ ingest BUILT — {BUILT_BUT_UNCOVERED[spec.name]}"
        elif spec.name in SOURCED:
            mark, why = "—", " ⚠ sourceable and never swept (AB-14)"
        else:
            mark, why = "·", " — source declared in §5A.5, no ingest built (AB-14)"
        print(f"    {mark} {spec.name}{why}")
    # ★ AB-14's other half: not "when did it run" but "what is stale NOW".
    from src.data_engine.calendar.classes import EVENT_CLASSES as _CLASSES
    from src.data_engine.ingest.cadence import due, report

    print("\ncadence — ⚠ what is stale RIGHT NOW (QD-16 rules out a per-run "
          "sweep, so the store is incrementally maintained):")
    today = datetime.now(timezone.utc).date()
    for line in report(due(store, _CLASSES, as_of=today,
                           derived=DERIVED_AT_CHECK)).splitlines():
        print(f"    {line}")

    print("\n✓ swept · ⊙ derived at check time · ◐ built, not yet coverable "
          "\n— sourceable, not swept · · declared source, no ingest "
          "\n✗ no source at all."
          "\n⚠ Only ✓ and ⊙ classes can reach CHECKED, and ✓ only for the "
          "names they covered.")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
