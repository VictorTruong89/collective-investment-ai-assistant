"""`python -m src.models.train` — the training run.

★ A separate entry point from `src.orchestration.entrypoint` on purpose:
constitution **P7** separates research from production, and a fit is not a daily
job. The daily run *consumes* an artifact; it never makes one.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

from src.models.train.run import (
    DEFAULT_YEARS,
    SELECTION_HORIZON_DAYS,
    TrainingInputs,
    build_training_labels,
    build_training_panel,
    default_window,
    elapsed,
    fetch_prices,
    ingest_universe_facts,
    load_sp500,
    summarise,
)

EXIT_OK, EXIT_FAILED = 0, 1


def _state(sub: str) -> Path:
    root = Path(os.environ.get("PIPELINE_STATE_DIR", ".state")) / sub
    root.mkdir(parents=True, exist_ok=True)
    return root


class _UncheckedReport:
    """⚠ The fallback when the event store has never been swept.

    ★ **Named, not hidden** — it reaches the run summary and the backtest spec's
    `calendar_check_id`, so an artifact fitted without a real check says so on
    its own manifest. FE-10 wants a real `PROCEED`; this is the honest stand-in
    until `--refresh-events` has run at least once (**AB-14**).
    """

    report_id = "TRAIN-CALENDAR-UNCHECKED"
    verdict = "PROCEED_WITH_FLAGS"
    window_start = window_end = None
    blocked = ()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="src.models.train",
        description="Fit a SELECTION model at the 1m horizon (P7: research).")
    parser.add_argument("--as-of", type=date.fromisoformat, default=None)
    parser.add_argument("--years", type=int, default=DEFAULT_YEARS)
    parser.add_argument("--limit", type=int, default=None,
                        help="⚠ Trim the universe — for a smoke run, not a fit.")
    parser.add_argument("--horizon-days", type=int, default=SELECTION_HORIZON_DAYS)
    parser.add_argument(
        "--capital", type=float, default=100_000.0,
        help="⚠ The book the cost gate is measured against. QA-48: a flat fee's "
             "drag is 1.20%%/yr at 1m on $100k and 0.12%% on $1M — the same "
             "strategy, a 10x spread. There is no 'realistic' default.")
    parser.add_argument(
        "--refresh-events", action="store_true",
        help="★ Sweep corporate actions into the event store before checking "
             "(AB-14). ⚠ ~2 calls per name — QD-16 rules out doing this every "
             "run, which is why it is a flag and not a default.")
    parser.add_argument("--skip-facts", action="store_true",
                        help="Reuse the fact ledger as it stands.")
    parser.add_argument("--prepare-only", action="store_true",
                        help="Build the panel and labels; do not fit.")
    args = parser.parse_args(argv)

    as_of = args.as_of or datetime.now(timezone.utc).date()
    started = time.time()

    universe = load_sp500()
    if args.limit:
        universe = universe[: args.limit]
    inputs = TrainingInputs(universe=universe, as_of=as_of,
                            start=default_window(as_of, years=args.years),
                            horizon_days=args.horizon_days)
    print(f"universe {len(universe)} · {inputs.start} → {as_of} · "
          f"h{args.horizon_days}d")
    print(f"⚠ survivorship: {inputs.survivorship}")

    engine, ledger, client, edgar, cik_map = _wire()
    if client is None:
        print("BLOCKED: FMP_API_KEY is not set", file=sys.stderr)
        return EXIT_FAILED

    if not args.skip_facts and edgar is not None:
        failures = ingest_universe_facts(edgar, ledger, universe, cik_map=cik_map)
        print(f"  facts: {len(universe) - len(failures)} ingested, "
              f"{len(failures)} failed  [{elapsed(started)}]")

    frames, unresolved = fetch_prices(client, universe, start=inputs.start,
                                      end=as_of)
    inputs.unresolved = unresolved
    print(f"  prices: {len(frames)} resolved, {len(unresolved)} unresolved  "
          f"[{elapsed(started)}]")
    if not frames:
        print("BLOCKED: no price history resolved", file=sys.stderr)
        return EXIT_FAILED

    # ★★ AB-9 — the real gate over the training window (FE-10).
    calendar = _calendar_report(tuple(frames), inputs.start, as_of,
                               refresh_events=args.refresh_events,
                               client=client, run_id="train")
    # ⚠ **`PROCEED` alone reads as "checked and clear".** An `UNCHECKED` class
    #   is not a blocker, so an unswept store yields PROCEED while nothing was
    #   examined — AB-14's hazard arriving in the training run. The counts say
    #   which it is.
    status = getattr(calendar, "class_status", {}) or {}
    checked = sorted(k for k, v in status.items() if str(v) == "CHECKED")
    print(f"  calendar: {calendar.verdict} · {calendar.report_id} · "
          f"{len(checked)}/{len(status)} classes CHECKED {checked}")
    if not checked:
        print("    ⚠ no class was checked — the event store has never been "
              "swept; re-run with --refresh-events (AB-14)", file=sys.stderr)

    panel, contract = build_training_panel(
        price_frames=frames, engine=_engine_for(engine, frames, cik_map),
        universe=tuple(frames), as_of=as_of, adj_as_of=as_of,
        calendar_report=calendar)
    print(f"  panel: {panel.shape} · contract {contract.name}@v{contract.version}"
          f"  [{elapsed(started)}]")

    import pandas as pd

    from src.data_engine import build_price_panel

    prices = build_price_panel(pd.concat(frames.values(), ignore_index=True),
                               (), as_of)
    labels, label_def = build_training_labels(
        prices, horizon_days=args.horizon_days, as_of=as_of)

    facts = summarise(inputs, panel, labels)
    for key, value in facts.items():
        print(f"    {key}: {value}")

    if args.prepare_only:
        print(f"PREPARED (no fit) [{elapsed(started)}]")
        return EXIT_OK

    from src.models.train.run import (
        feature_coverage,
        fit_selection_model,
        rank_ic,
    )

    coverage = feature_coverage(panel, contract.feature_names)
    print("  feature coverage:")
    for key, value in coverage.items():
        print(f"    {key}: {value}")

    artifact = fit_selection_model(
        panel=panel, labels=labels, contract=contract, label_def=label_def,
        as_of=as_of, adj_as_of=as_of, horizon_days=args.horizon_days)
    print(f"  fitted: {len(artifact.feature_names)} features  [{elapsed(started)}]")

    measured = rank_ic(artifact, panel, labels,
                       feature_names=artifact.feature_names)
    print("  IN-SAMPLE rank IC (⚠ not a validation result):")
    for key, value in measured.items():
        print(f"    {key}: {value}")
    from src.models.artifact.store import ArtifactStore
    from src.models.train.run import decide_promotion, walk_forward_ic

    print("  walk-forward (purged + embargoed) — ★ the number that can falsify:")
    ic_result, folds, scored = walk_forward_ic(
        panel=panel, labels=labels, contract=contract, label_def=label_def,
        as_of=as_of, adj_as_of=as_of, horizon_days=args.horizon_days)
    for key, value in ic_result.to_json_obj().items():
        print(f"    {key}: {value}")
    for fold in folds:
        print(f"    fold {fold['index']}: ic={fold.get('ic')} "
              f"test={fold.get('test_start')}..{fold.get('test_end')}")

    from src.quant.backtest.portfolio import simulate, turnover_note

    simulation = simulate(scored, horizon_days=args.horizon_days,
                          capital=args.capital)
    print("  portfolio simulation — ★ what `cost_survival` reads:")
    for key, value in simulation.items():
        print(f"    {key}: {value}")
    print(f"    {turnover_note(simulation)}")

    from src.models.train.run import measure_breadth

    breadth = measure_breadth(scored, horizon_days=args.horizon_days)
    print("  effective breadth — ★ QA-43, the last gate:")
    for key, value in breadth.items():
        print(f"    {key}: {value}")

    # ★★ MT-19 — D-03 grades it, and its `result_id` is the evidence promotion
    #   demands. D-04 computing its own verdict is the domain marking its own
    #   homework, which `promote()` refuses by asking for an id D-04 cannot mint.
    from src.models.train.run import d03_evaluate

    spec, backtest = d03_evaluate(
        universe=tuple(frames), scored=scored, simulation=simulation,
        breadth=breadth, horizon_days=args.horizon_days, as_of=as_of,
        start=inputs.start, capital=args.capital, contract=contract,
        calendar_check_id=calendar.report_id)
    print(f"  D-03 backtest: {backtest.result_id}")
    print(f"    spec {spec.spec_id} · survivorship_handled="
          f"{spec.survivorship_handled}  ⚠ QA-14: reported as BIASED")
    for gate_set in backtest.gate_sets:
        for gate in gate_set.gates:
            print(f"    {gate.gate_id}: {gate.verdict} — {gate.why}")

    store = ArtifactStore(_state("models"))
    outcome = decide_promotion(artifact, ic_result=ic_result,
                               names=facts["names"], store=store,
                               simulation=simulation, breadth=breadth,
                               backtest_result_id=backtest.result_id)
    print(f"  artifact: {outcome['artifact_id']}")
    print(f"  gates: {outcome['verdicts']}")
    if outcome["promoted"]:
        print("  ★ PROMOTED — every required gate passed")
    elif outcome.get("pending_review"):
        # ★ MT-52 — held for the fund manager's review; nothing scores with it yet.
        print("  ★ ALL GATES PASSED — HELD FOR REVIEW (MT-52). Nothing is promoted.")
        print(f"    review:  python -m src.models.promote {outcome['artifact_id']}")
        print(f"    approve: python -m src.models.promote {outcome['artifact_id']} --approve")
    else:
        print(f"  ⚠ NOT PROMOTED — refused on {outcome['refused_gates']}")
        print("    ★ The artifact is written anyway: a refused model is a record.")
    print(f"SUCCESS [{elapsed(started)}]")
    return EXIT_OK


def _calendar_report(universe, start, as_of, *, refresh_events, client, run_id):
    """D-07's §6A gate, sweeping first when asked.

    ⚠ **Falls back to a NAMED unchecked report rather than a fabricated PROCEED**
    when the store has never been swept — the id travels onto the backtest spec,
    so an artifact fitted without a real check carries that fact.
    """
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import refresh
    from src.models.train.run import training_calendar_check

    store = EventStore(_state("events"))
    if refresh_events and client is not None:
        outcome = refresh(client, store, tickers=universe, start=start, end=as_of)
        print(f"  events: {outcome['findings']} findings over "
              f"{outcome['tickers']} names · refreshed {outcome['refreshed']}")
        if outcome["why"]:
            print(f"    ⚠ {outcome['why']}", file=sys.stderr)
    try:
        return training_calendar_check(store=store, universe=universe,
                                       start=start, as_of=as_of, run_id=run_id)
    except Exception as exc:                   # noqa: BLE001 — named, not fatal
        print(f"  note: calendar check unavailable ({exc}); using the declared "
              f"UNCHECKED report (AB-14)", file=sys.stderr)
        return _UncheckedReport()


def _wire():
    """D-07's handles. ⚠ Built here, not imported into a domain."""
    from src.data_engine.ingest.edgar_facts import load_cik_map
    from src.data_engine.observation.ledger import ObservationLedger
    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.src.edgar.client import EdgarClient
    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret

    cik_map = load_cik_map()
    ledger = FactLedger(_state("facts"))
    key = os.environ.get("FMP_API_KEY")
    client = FMPClient(Secret("FMP_API_KEY", key)) if key else None
    contact = os.environ.get("EDGAR_CONTACT") or os.environ.get("GMAIL_SMTP_USER")
    edgar = EdgarClient(Secret("EDGAR_CONTACT", contact)) if contact else None
    return (ledger, ObservationLedger(_state("obs"))), ledger, client, edgar, cik_map


def _engine_for(handles, frames, cik_map):
    from src.data_engine.pit.models import UniverseEntry
    from src.data_engine.service import DataEngine
    from src.data_engine.universe.membership import Universe

    ledger, observations = handles
    entries = [UniverseEntry(ticker=t, cik=cik_map.get(t),
                             filer_class="10-K/10-Q" if cik_map.get(t) else "none",
                             source="edgar" if cik_map.get(t) else "fmp")
               for t in frames]
    return DataEngine(universe=Universe(entries), fact_ledger=ledger,
                      observation_ledger=observations, price_source=None)


if __name__ == "__main__":
    raise SystemExit(main())
