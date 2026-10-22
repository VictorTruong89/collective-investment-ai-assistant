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


def market_date(now: datetime | None = None) -> date:
    """MT-56 / AC-4.38 (DX-163a) — today's date in NEW YORK, the market's calendar.

    ⚠ Until 2026-10-08 the default was the UTC date: a run started at 23:27 EDT
    dated itself tomorrow, one day past every source's coverage.
    """
    from zoneinfo import ZoneInfo

    now = now or datetime.now(timezone.utc)
    return now.astimezone(ZoneInfo("America/New_York")).date()


def price_events_line(events, *, start: date, as_of: date) -> str:
    """AC-4.50 (MT-61 ✏ 2026-10-20) — count the events that adjust a bar in the window.

    An event dated on or before `start` adjusts only bars before the window. ⚠ The
    line printed "1785 splits applied", counting every stored split ≤ `as_of`.
    """
    inside = [e for e in events if start < e.event_date <= as_of]
    n_split = sum(1 for e in events if e.event_type == "split")
    in_split = sum(1 for e in inside if e.event_type == "split")
    return (f"  price events: {in_split} splits · {len(inside) - in_split} dividends "
            f"in the window (of {n_split} · {len(events) - n_split} supplied) (DE-78)")


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
    parser.add_argument(
        "--target", choices=("xs_gauss", "raw"), default="xs_gauss",
        help="★ What the trees are fitted on (MT-59): xs_gauss = each day's return "
             "rank as a centred normal score (default); raw = the 21-day return. "
             "Evaluation always reads the raw return.")
    parser.add_argument(
        "--allow-unchecked-calendar", action="store_true",
        help="⚠ Proceed even when the calendar check CHECKED no class (MT-57). "
             "The run then carries no calendar guarantee, and says so.")
    args = parser.parse_args(argv)

    # ★ MT-53 / AC-4.35 — a long run shows it is alive (elapsed + stage, to stderr).
    from src.shared.progress import Heartbeat

    with Heartbeat("train") as beat:
        return _train(args, beat)


def _train(args, beat) -> int:
    as_of = args.as_of or market_date()                 # ★ MT-56 — New York, not UTC
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

    beat.stage("connecting")
    engine, ledger, client, edgar, cik_map = _wire()
    if client is None:
        print("BLOCKED: FMP_API_KEY is not set", file=sys.stderr)
        return EXIT_FAILED

    if not args.skip_facts and edgar is not None:
        beat.stage("fundamentals (EDGAR companyfacts)")
        failures = ingest_universe_facts(edgar, ledger, universe, cik_map=cik_map)
        print(f"  facts: {len(universe) - len(failures)} ingested, "
              f"{len(failures)} failed  [{elapsed(started)}]")

    beat.stage("prices (FMP)")
    frames, unresolved = fetch_prices(client, universe, start=inputs.start,
                                      end=as_of)
    inputs.unresolved = unresolved
    print(f"  prices: {len(frames)} resolved, {len(unresolved)} unresolved  "
          f"[{elapsed(started)}]")
    if not frames:
        print("BLOCKED: no price history resolved", file=sys.stderr)
        return EXIT_FAILED

    # ★★ AB-9 — the real gate over the training window (FE-10).
    beat.stage("calendar check")
    from src.data_engine.errors import UnhandledBlockError

    try:
        calendar = _calendar_report(tuple(frames), inputs.start, as_of,
                                   refresh_events=args.refresh_events,
                                   client=client, run_id="train")
    except UnhandledBlockError as exc:
        # ★★ MT-54 / AC-4.36 (DX-158) — a HALT ends the run, naming every event.
        #   ⚠ Until 2026-10-07 this was caught as "calendar check unavailable" and
        #   replaced by a stand-in PROCEED_WITH_FLAGS — five BLOCKs went unseen.
        print(f"HALT: the calendar check refused the training window (DE-32) — {exc}",
              file=sys.stderr)
        print("  no panel is built over an unhandled BLOCK; each event needs a recorded "
              "handling (D-07 §6A) before this window can be trained on", file=sys.stderr)
        return EXIT_FAILED
    # ⚠ **`PROCEED` alone reads as "checked and clear".** An `UNCHECKED` class
    #   is not a blocker, so an unswept store yields PROCEED while nothing was
    #   examined — AB-14's hazard arriving in the training run. The counts say
    #   which it is.
    status = getattr(calendar, "class_status", {}) or {}
    checked = sorted(k for k, v in status.items() if str(v) == "CHECKED")
    print(f"  calendar: {calendar.verdict} · {calendar.report_id} · "
          f"{len(checked)}/{len(status)} classes CHECKED {checked}")
    if not checked:
        # ★★ MT-57 / AC-4.39 (DX-163b) — nothing checked is REFUSED, not noted.
        print(f"    ⚠ 0/{len(status)} calendar classes CHECKED — the window has no "
              f"calendar guarantee:", file=sys.stderr)
        for name, why in sorted(status.items()):
            print(f"      {name}: {why}", file=sys.stderr)
        if not args.allow_unchecked_calendar:
            print("REFUSED: sweep the event store first (`python -m "
                  "src.data_engine.ingest events`, or --refresh-events), or pass "
                  "--allow-unchecked-calendar to train without a calendar check "
                  "(MT-57)", file=sys.stderr)
            return EXIT_FAILED
        print("  ⚠ UNCHECKED CALENDAR — proceeding on --allow-unchecked-calendar "
              "(MT-57); this artifact carries no calendar guarantee", file=sys.stderr)

    beat.stage("features panel")
    # ★ MT-55 / DE-77 (DX-160) — the GICS map, so the five *_sector_z are
    #   sector-relative. ⚠ Until 2026-10-07 none was passed and they were
    #   market-wide z-scores under sector names.
    from src.data_engine.ingest.edgar_facts import load_sector_map

    sectors = load_sector_map()
    covered = sum(1 for t in frames if t in sectors)
    print(f"  sectors: {covered}/{len(frames)} names (GICS, config/sp500_tickers.yaml) "
          f"⚠ today's classification applied to the whole window (DE-77)")
    # ★★★ MT-61 / DE-78 (DX-166) — splits and dividends, from the event store
    #   the calendar check just read; the panel AND the labels use them.
    from src.data_engine.calendar.gate import price_events
    from src.data_engine.calendar.store import EventStore

    events = price_events(EventStore(_state("events")), tickers=tuple(frames),
                          adj_as_of=as_of)
    # ★ MT-63 / DE-79 — a name whose events contradict its own prices is left
    #   out BY NAME (DE-13), never adjusted with a guessed factor.
    import pandas as pd

    from src.data_engine.pit.adjustment import price_event_conflicts

    conflicts = price_event_conflicts(pd.concat(frames.values(), ignore_index=True),
                                      events, as_of)
    for ticker, why in sorted(conflicts.items()):
        print(f"  ⚠ {ticker} left out: {why}", file=sys.stderr)
        frames.pop(ticker, None)
        inputs.unresolved[ticker] = f"price events inconsistent: {why}"
    events = [e for e in events if e.ticker.upper() not in conflicts]
    print(price_events_line(events, start=inputs.start, as_of=as_of))
    panel, contract = build_training_panel(
        price_frames=frames, engine=_engine_for(engine, frames, cik_map),
        universe=tuple(frames), as_of=as_of, adj_as_of=as_of,
        calendar_report=calendar, events=events, sectors=sectors)
    print(f"  panel: {panel.shape} · contract {contract.name}@v{contract.version}"
          f"  [{elapsed(started)}]")

    import pandas as pd

    from src.data_engine import build_price_panel

    beat.stage("labels")
    prices = build_price_panel(pd.concat(frames.values(), ignore_index=True),
                               events, as_of)              # ★ MT-61 — same events
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

    beat.stage("fit")
    print(f"  target: {args.target} (MT-59) — the trees fit this; IC, simulation and "
          f"gates read the raw {args.horizon_days}-day return")
    artifact = fit_selection_model(
        panel=panel, labels=labels, contract=contract, label_def=label_def,
        as_of=as_of, adj_as_of=as_of, horizon_days=args.horizon_days,
        target=args.target)
    print(f"  fitted: {len(artifact.feature_names)} features  [{elapsed(started)}]")

    measured = rank_ic(artifact, panel, labels,
                       feature_names=artifact.feature_names)
    print("  IN-SAMPLE rank IC (⚠ not a validation result):")
    for key, value in measured.items():
        print(f"    {key}: {value}")
    from src.models.artifact.store import ArtifactStore
    from src.models.train.run import decide_promotion, walk_forward_ic

    # ★ MT-58 (DX-162) — two protocols, each named for what it is. ⚠ Until
    #   2026-10-08 the k-fold below was printed as "walk-forward".
    print("  out-of-sample · purged k-fold (trains on BOTH sides of each test block; "
          "reported, not gated — F12 D14; feeds only the simulation):")
    beat.stage("out-of-sample IC (purged k-fold)")
    ic_result, folds, scored = walk_forward_ic(
        panel=panel, labels=labels, contract=contract, label_def=label_def,
        as_of=as_of, adj_as_of=as_of, horizon_days=args.horizon_days,
        scheme="purged_kfold", target=args.target)
    for key, value in ic_result.to_json_obj().items():
        print(f"    {key}: {value}")
    for fold in folds:
        print(f"    fold {fold['index']}: ic={fold.get('ic')} "
              f"test={fold.get('test_start')}..{fold.get('test_end')}")

    print("  out-of-sample · walk-forward (expanding window, trains on the PAST only) — "
          "★ GATES significance and breadth (F12 D14):")
    beat.stage("walk-forward IC (expanding window)")
    wf_result, wf_folds, wf_scored = walk_forward_ic(
        panel=panel, labels=labels, contract=contract, label_def=label_def,
        as_of=as_of, adj_as_of=as_of, horizon_days=args.horizon_days,
        scheme="walk_forward", target=args.target)
    wf = wf_result.to_json_obj()
    print(f"    mean_ic: {wf.get('mean_ic')} · realised_se: {wf.get('realised_se')} · "
          f"t_stat_realised: {wf.get('t_stat_realised')} · dates: {wf.get('dates')}")
    for fold in wf_folds:
        print(f"    fold {fold['index']}: ic={fold.get('ic')} train_to={fold.get('n_train')} "
              f"dates · test={fold.get('test_start')}..{fold.get('test_end')}")
    walk_forward = {**wf, "folds": wf_folds}

    from src.quant.backtest.portfolio import simulate, turnover_note

    beat.stage("portfolio simulation")
    simulation = simulate(scored, horizon_days=args.horizon_days,
                          capital=args.capital)
    print("  portfolio simulation — ★ what `cost_survival` reads:")
    for key, value in simulation.items():
        print(f"    {key}: {value}")
    print(f"    {turnover_note(simulation)}")

    from src.models.train.run import measure_breadth

    beat.stage("breadth")
    breadth = measure_breadth(scored, horizon_days=args.horizon_days)
    print("  effective breadth — ★ QA-43, the last gate:")
    for key, value in breadth.items():
        print(f"    {key}: {value}")

    # ★ MT-62 / F12 D12 — the residual correlation against EXTERNAL factors
    #   (SPY + the GICS sector SPDRs), reported beside the gate, never gating.
    from src.models.train.run import external_factor_returns
    from src.quant.metrics.breadth import external_residual_correlation

    beat.stage("external breadth (SPY + sector SPDRs)")
    missing = []
    market, sector_returns = external_factor_returns(
        client, start=inputs.start, as_of=as_of, horizon_days=args.horizon_days,
        on_error=lambda symbol, exc: missing.append(f"{symbol} ({str(exc)[:60]})"))
    wide = scored.pivot_table(index="date", columns="ticker", values="value",
                              aggfunc="last")
    wide.index = pd.to_datetime(wide.index)
    external = external_residual_correlation(
        wide, market=market, sector_returns=sector_returns, sectors=sectors,
        horizon_days=args.horizon_days)
    if external.get("breadth_market") and wf_result.mean_ic is not None:
        # ★ F12 D13/D14 — the gated pair: market-only BR × the walk-forward IC.
        external["implied_ir_gated"] = round(
            abs(wf_result.mean_ic) * external["breadth_market"] ** 0.5, 4)
    external["factors_missing"] = missing
    print("  external residual correlation — ★ F12 D12 (its market-only BR is what the gate reads, D13):")
    for key, value in external.items():
        print(f"    {key}: {value}")

    # ★★ F12 D13 — the breadth gate reads BR from the EXTERNAL MARKET-ONLY residual ρ.
    #   The raw-ρ figure above stays reported (`raw_breadth`); unmeasured ⇒ NOT_EVALUATED.
    from src.quant.metrics.breadth import gated_breadth

    gated_br, gated_basis = gated_breadth(external)
    gate_breadth = {**breadth, "raw_breadth": breadth.get("breadth"),
                    "breadth": gated_br, "breadth_basis": gated_basis}
    print(f"  breadth gate input: BR {gated_br} from {gated_basis} "
          f"(raw-ρ BR {breadth.get('breadth')} reported, not gated)")

    # ★★ MT-19 — D-03 grades it, and its `result_id` is the evidence promotion
    #   demands. D-04 computing its own verdict is the domain marking its own
    #   homework, which `promote()` refuses by asking for an id D-04 cannot mint.
    from src.models.train.run import d03_evaluate, gating_predictions

    beat.stage("D-03 evaluation + gates")
    spec, backtest = d03_evaluate(
        # ★★ F12 D14 — the IC-reading gates judge the WALK-FORWARD predictions;
        #   the simulation (cost_survival) keeps the k-fold's five blocks.
        universe=tuple(frames),
        scored=gating_predictions(kfold=scored, walk_forward=wf_scored),
        simulation=simulation,
        breadth=gate_breadth, horizon_days=args.horizon_days, as_of=as_of,
        start=inputs.start, capital=args.capital, contract=contract,
        calendar_check_id=calendar.report_id)
    print(f"  D-03 backtest: {backtest.result_id}")
    print(f"    spec {spec.spec_id} · survivorship_handled="
          f"{spec.survivorship_handled}  ⚠ QA-14: reported as BIASED")
    for gate_set in backtest.gate_sets:
        for gate in gate_set.gates:
            print(f"    {gate.gate_id}: {gate.verdict} — {gate.why}")

    store = ArtifactStore(_state("models"))
    outcome = decide_promotion(artifact, ic_result=wf_result,       # ★ F12 D14
                               names=facts["names"], store=store,
                               simulation=simulation, breadth=gate_breadth,
                               backtest_result_id=backtest.result_id,
                               walk_forward=walk_forward,
                               external_breadth=external)
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

    ★★ **MT-54 — nothing is caught here.** A never-swept store already yields D-07's
    real report with every class `UNCHECKED` (named on the run summary and on the
    backtest spec's `calendar_check_id`); an unhandled BLOCK raises
    `UnhandledBlockError` and the caller ends the run. ⚠ *Until 2026-10-07 (DX-158)*
    a broad `except` replaced ANY failure — a HALT included — with a stand-in
    `PROCEED_WITH_FLAGS` report: MT-16's defect.
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
    return training_calendar_check(store=store, universe=universe,
                                   start=start, as_of=as_of, run_id=run_id)


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
