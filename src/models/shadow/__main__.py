"""`python -m src.models.shadow {start,record,score,status}` — the shadow trial (MT-64…66).

★ Reuses the training run's own wiring (credentials, calendar check, event refresh,
contract assembly) — a second copy of any of it is where a shadow would drift from
the model it shadows.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta, timezone

EXIT_OK, EXIT_FAILED = 0, 1

#: Enough trading history for every price feature (50-session SMA, 20-session
#: volatility, the rule's 21-session z) — an admitted margin, not a tuned value.
PRICE_LOOKBACK_DAYS = 450


def _fmp_price_events(client, tickers, on_error=None) -> list:
    """Splits and dividends straight from FMP for the snapshot's names (MT-65).

    ★ Deliberately NOT through `ingest.events.refresh`: that records coverage as
    the requested names and window, OVERWRITING the store's full-universe record
    (DX-167) — a shadow snapshot must never narrow what training later sees as
    checked. FMP returns each name's full history, the same source the sweep uses.
    """
    from src.data_engine.src.fmp import prices as fmp_prices

    out = []
    for ticker in tickers:
        try:
            out += list(fmp_prices.splits(client, ticker))
            out += list(fmp_prices.dividends(client, ticker))
        except Exception as exc:               # noqa: BLE001 — named by the caller
            if on_error is not None:
                on_error(ticker, exc)
    return out


def _root():
    from src.models.train.__main__ import _state

    return _state("shadow")


def _store():
    from src.models.artifact.store import ArtifactStore
    from src.models.train.__main__ import _state

    return ArtifactStore(_state("models"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="src.models.shadow",
                                     description="Shadow-score a refused model live (MT-64…66).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_start = sub.add_parser("start", help="freeze an artifact and the criterion (once)")
    p_start.add_argument("artifact_id")
    p_rec = sub.add_parser("record", help="one snapshot (≥ 21 trading days apart)")
    p_rec.add_argument("--as-of", type=date.fromisoformat, default=None)
    p_rec.add_argument("--skip-facts", action="store_true",
                       help="reuse the fact ledger as it stands")
    p_rec.add_argument("--allow-unchecked-calendar", action="store_true")
    p_rec.add_argument("--limit", type=int, default=None,
                       help="⚠ trim the universe — a smoke run, not an observation")
    sub.add_parser("score", help="grade every matured snapshot")
    sub.add_parser("status", help="the trial, its snapshots and the verdict so far")
    args = parser.parse_args(argv)

    from src.models.shadow.trial import ShadowError

    try:
        if args.cmd == "start":
            return _start(args)
        if args.cmd == "status":
            return _status()
        from src.shared.progress import Heartbeat

        with Heartbeat(f"shadow {args.cmd}") as beat:
            return _record(args, beat) if args.cmd == "record" else _score(beat)
    except ShadowError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return EXIT_FAILED


def _start(args) -> int:
    from src.models.shadow.trial import start_trial

    store = _store()
    if store.load_estimator(args.artifact_id) is None:
        print(f"REFUSED: no fitted artifact {args.artifact_id} in {store.root}", file=sys.stderr)
        return EXIT_FAILED
    trial = start_trial(_root(), artifact_id=args.artifact_id, store=store)
    print(f"shadow trial started {trial['started']} · frozen {trial['artifact_id']}")
    print(f"  history: walk-forward IC {trial['history']['mean_ic']:.4f} over "
          f"{trial['history']['dates']} dates")
    print(f"  criterion (pre-registered): {trial['criterion']}")
    print("  next: `python -m src.models.shadow record` (records the latest completed trading day)")
    return EXIT_OK


def _record(args, beat) -> int:
    import pandas as pd

    from src.data_engine import build_price_panel
    from src.data_engine.errors import UnhandledBlockError
    from src.data_engine.ingest.edgar_facts import load_sector_map
    from src.data_engine.pit.adjustment import price_event_conflicts
    from src.feature_engineer.technical.momentum import mom_21, vol_21
    from src.models.shadow.record import (
        assert_contract,
        assert_out_of_sample,
        assert_spacing,
        rankings,
        snapshot_date,
        snapshots,
        write_snapshot,
    )
    from src.models.shadow.trial import ShadowError, load_trial
    from src.models.train import __main__ as train
    from src.models.train.run import (
        build_training_panel,
        fetch_prices,
        ingest_universe_facts,
        load_sp500,
    )

    root = _root()
    trial = load_trial(root)
    estimator = _store().load_estimator(trial["artifact_id"])
    if estimator is None:
        raise ShadowError(f"the frozen artifact {trial['artifact_id']} is missing")
    end = args.as_of or train.market_date()
    start = end - timedelta(days=PRICE_LOOKBACK_DAYS)
    universe = load_sp500()
    if args.limit:
        universe = universe[: args.limit]
        print(f"  ⚠ SMOKE: universe trimmed to {len(universe)} — not a trial observation")

    beat.stage("connecting")
    engine, ledger, client, edgar, cik_map = train._wire()
    if client is None:
        raise ShadowError("FMP_API_KEY is not set")
    # ★ Prices FIRST — the cheap checks (date, window, spacing) run before the
    #   3–4 minutes of fundamentals, so a refusal costs little.
    beat.stage("prices (FMP)")
    frames, unresolved = fetch_prices(client, universe, start=start, end=end)
    sessions = sorted({d.date() for f in frames.values() for d in pd.to_datetime(f["date"])})
    as_of = snapshot_date(sessions, args.as_of)
    print(f"  snapshot date {as_of}" + ("" if args.as_of else
                                       " (latest completed session in the EOD data)"))
    assert_out_of_sample(as_of, trial.get("returns_seen_through"))     # ★ MT-65
    previous = max((date.fromisoformat(s["as_of"]) for s in snapshots(root)), default=None)
    assert_spacing(previous, as_of, sessions)
    frames = {t: f[pd.to_datetime(f["date"]).dt.date <= as_of] for t, f in frames.items()}

    if not args.skip_facts and edgar is not None:
        beat.stage("fundamentals (EDGAR companyfacts)")
        failures = ingest_universe_facts(edgar, ledger, universe, cik_map=cik_map)
        print(f"  facts: {len(universe) - len(failures)} ingested, {len(failures)} failed")

    beat.stage("calendar check (read-only)")
    try:
        # ⚠ refresh_events=False — a shadow never writes the event store (DX-167).
        calendar = train._calendar_report(tuple(frames), start, as_of, refresh_events=False,
                                          client=client, run_id="shadow")
    except UnhandledBlockError as exc:
        raise ShadowError(f"the calendar check halted the window (DE-32) — {exc}") from exc
    status = getattr(calendar, "class_status", {}) or {}
    checked = sorted(k for k, v in status.items() if str(v) == "CHECKED")
    if not checked and not args.allow_unchecked_calendar:
        raise ShadowError("0 calendar classes CHECKED (MT-57) — run `python -m "
                          "src.data_engine.ingest events --universe sp500 --years 10` "
                          "the same day, or pass --allow-unchecked-calendar")

    beat.stage("splits & dividends (FMP, per name)")
    failed_events = {}
    events = _fmp_price_events(client, tuple(frames),
                               on_error=lambda t, e: failed_events.__setitem__(t, str(e)[:80]))
    for ticker in failed_events:                 # ⚠ unadjustable ⇒ left out, by name
        frames.pop(ticker, None)
    events = [e for e in events if e.event_date <= as_of and e.ticker.upper() in frames]
    conflicts = price_event_conflicts(pd.concat(frames.values(), ignore_index=True),
                                      events, as_of)
    for ticker in conflicts:
        frames.pop(ticker, None)
    events = [e for e in events if e.ticker.upper() not in conflicts]

    beat.stage("features panel (single date)")
    panel, contract = build_training_panel(
        price_frames=frames, engine=train._engine_for(engine, frames, cik_map),
        universe=tuple(frames), as_of=as_of, adj_as_of=as_of, calendar_report=calendar,
        events=events, sectors=load_sector_map(), single_date=True)
    assert_contract(contract.content_hash, trial["contract_hash"])

    # The rule's inputs, from the same adjusted prices (the card's own definition).
    prices = build_price_panel(pd.concat(frames.values(), ignore_index=True), events, as_of)
    prices = prices.sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)
    prices["mom_21"] = mom_21(prices).to_numpy()
    prices["vol_21"] = vol_21(prices).to_numpy()
    panel["date"] = pd.to_datetime(panel["date"])
    prices["date"] = pd.to_datetime(prices["date"])
    panel = panel.merge(prices[["ticker", "date", "mom_21", "vol_21"]],
                        on=["ticker", "date"], how="left")

    beat.stage("rank (frozen model + rule)")
    model, rule = rankings(panel, as_of=as_of, estimator=estimator,
                           feature_names=trial["features"])
    snapshot = {
        "as_of": as_of.isoformat(), "artifact_id": trial["artifact_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "universe_n": len(universe), "ranked_n": len(model),
        "smoke": bool(args.limit),
        "left_out": {**conflicts, **{t: str(w)[:120] for t, w in unresolved.items()},
                     **{t: f"splits/dividends unfetchable: {w}" for t, w in failed_events.items()}},
        "calendar": {"verdict": str(calendar.verdict), "report_id": calendar.report_id,
                     "checked": checked},
        "model": [{"ticker": r["ticker"], "z": r["z"], "rank": r["rank"]} for r in model],
        "rule": [{"ticker": r["ticker"], "z": r["z"], "rank": r["rank"]} for r in rule],
    }
    path = write_snapshot(root, snapshot)
    print(f"  snapshot {as_of}: {len(model)} names ranked · model #1 {model[0]['ticker']} · "
          f"rule #1 {rule[0]['ticker']} → {path}")
    print("  matures after 21 trading sessions; then `python -m src.models.shadow score`")
    return EXIT_OK


def _score(beat) -> int:
    import pandas as pd

    from src.data_engine import build_price_panel
    from src.data_engine.pit.adjustment import price_event_conflicts
    from src.models.shadow.record import snapshots
    from src.models.shadow.score import append_score, realised_returns, scored, snapshot_ic
    from src.models.shadow.trial import ShadowError, load_trial
    from src.models.train import __main__ as train
    from src.models.train.run import fetch_prices

    root = _root()
    load_trial(root)                       # refuses when no trial has been started
    done = {r["as_of"] for r in scored(root)}
    due = [s for s in snapshots(root) if s["as_of"] not in done]
    if not due:
        print("  nothing to score")
        return _status()
    today = train.market_date()
    first = min(date.fromisoformat(s["as_of"]) for s in due)
    tickers = sorted({r["ticker"] for s in due for r in s["model"]})

    beat.stage("connecting")
    _, _, client, _, _ = train._wire()
    if client is None:
        raise ShadowError("FMP_API_KEY is not set")
    beat.stage("prices (FMP)")
    frames, _ = fetch_prices(client, tickers, start=first - timedelta(days=7), end=today)
    beat.stage("splits & dividends (FMP, per name)")
    failed = {}
    events = _fmp_price_events(client, tuple(frames),
                               on_error=lambda t, e: failed.__setitem__(t, str(e)[:80]))
    for ticker in failed:
        frames.pop(ticker, None)
    events = [e for e in events if e.event_date <= today and e.ticker.upper() in frames]
    conflicts = price_event_conflicts(pd.concat(frames.values(), ignore_index=True),
                                      events, today)
    for ticker in conflicts:
        frames.pop(ticker, None)
    events = [e for e in events if e.ticker.upper() not in conflicts]
    prices = build_price_panel(pd.concat(frames.values(), ignore_index=True), events, today)

    beat.stage("grade")
    for snap in sorted(due, key=lambda s: s["as_of"]):
        realised = realised_returns(prices, date.fromisoformat(snap["as_of"]))
        if realised is None:
            print(f"  {snap['as_of']}: not matured yet")
            continue
        row = {"as_of": snap["as_of"], "scored_at": datetime.now(timezone.utc).isoformat(),
               "names": int(len(realised)),
               "model_ic": snapshot_ic(snap["model"], realised),
               "rule_ic": snapshot_ic(snap["rule"], realised),
               "left_out_at_scoring": sorted(conflicts)}
        append_score(root, row)
        print(f"  {snap['as_of']}: model IC {row['model_ic']:+.4f} · rule IC "
              f"{row['rule_ic']:+.4f} · {row['names']} names")
    return _status()


def _status() -> int:
    from src.models.shadow.record import snapshots
    from src.models.shadow.score import scored
    from src.models.shadow.trial import load_trial, pooled_verdict

    root = _root()
    trial = load_trial(root)
    snaps, rows = snapshots(root), scored(root)
    print(f"shadow trial · frozen {trial['artifact_id'][:19]}… since {trial['started']}")
    print(f"  snapshots {len(snaps)} · scored {len(rows)}"
          + (f" · last snapshot {snaps[-1]['as_of']}" if snaps else ""))
    model = [r["model_ic"] for r in rows]
    rule = [r["rule_ic"] for r in rows if r.get("rule_ic") is not None]
    verdict = pooled_verdict(trial["history"], model)
    if rule:
        print(f"  rule (comparator, not judged): live mean IC {sum(rule) / len(rule):+.4f} "
              f"over {len(rule)}")
    for key, value in verdict.items():
        print(f"  {key}: {value}")
    print("  ⚠ the bar does not promote — `python -m src.models.promote <id> --approve` (MT-52)")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
