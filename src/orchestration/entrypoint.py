"""D-08 §5A.5 — the entrypoint a thin external timer calls. OR-40, OR-41, OR-42.

```
python -m src.orchestration.entrypoint --as-of 2026-08-25
```

★ **OR-41: the timer holds NO policy.** Its entire responsibility is *"call this
at this time"* — no retry, no dependency order, no budget, no conditional logic.
*Policy in a timer is policy with no manifest, no test and no spec.*

★ **OR-42: the timer may fire MORE OFTEN than the cadence.** Preconditions decide
whether work happens, so **an over-firing timer is safe by construction** and a
missed firing is not — prefer redundant firings with strict preconditions over
an exactly-once timer. A second firing inside one window exits `BLOCKED`, which
is **INFO, not failure** (OR-46).

⚠ **This module resolves and dispatches; the runner still does not.** `invoke`
stays an argument to `Orchestrator.run`, so **nothing inside `src/orchestration/`
can return a value derived from market data** (OR-1) — the resolution lives here,
at the edge, where it is visible.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timezone

_TODAY = date.today()

from src.orchestration.contracts.manifest import config_hash, git_state
from src.orchestration.jobs.graph import DAILY_INFERENCE, resolve
from src.orchestration.jobs.runner import (
    Orchestrator, artifact_allowed, assert_no_analysis, failure_notice,
)
from src.orchestration.policy.budget import Budgets
from src.orchestration.schedule.cadence import Cadence

#: Exit codes the timer can act on without parsing output.
EXIT_OK, EXIT_BLOCKED, EXIT_FAILED = 0, 0, 1


def build_orchestrator(*, job_graph=DAILY_INFERENCE) -> Orchestrator:
    """Assemble the run. ★ Nothing here computes; it wires."""
    budgets = Budgets(run_seconds=1800.0,
                      per_job={j.job_id: j.budget_s for j in job_graph.jobs
                               if j.budget_s is not None})
    return Orchestrator(graph=job_graph,
                        cadence=Cadence(job_graph_id=job_graph.job_graph_id),
                        budgets=budgets)


def dispatch_for(context):
    """The caller's dispatch — ★ **the one place a domain is actually called.**

    ⚠ It lives outside the runner deliberately (OR-1): `src/orchestration/` may
    invoke, never compute, and keeping the domain calls at the edge is what
    makes that boundary greppable rather than reviewed.

    ★ `src/orchestration/jobs/wiring.py` holds one adapter per job. Each reads
    what its job needs from `context` and hands it to the domain; **an adapter
    that derived a value would break OR-1**, and `test_no_adapter_computes`
    is the guard.
    """
    from src.orchestration.jobs.wiring import make_dispatch

    return make_dispatch(context)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="src.orchestration.entrypoint",
        description="D-08 daily run. The timer calls this and holds no policy "
                    "of its own (OR-41).")
    parser.add_argument("--as-of", type=date.fromisoformat, default=None)
    parser.add_argument(
        "--thesis", action="store_true",
        help="★ Author a k=3 probed thesis for the top-ranked name (D-01 WF-1). "
             "⚠ COSTS MONEY — three live Opus passes, roughly $1 per run, which "
             "is why the daily run does not do it silently. Without it the "
             "thesis gate stays the declared stub and DN-39 keeps the card "
             "informational.")
    parser.add_argument(
        "--reauthor", action="store_true",
        help="⚠ Author a fresh thesis even if one exists for this exact bundle "
             "(RC-61). Costs another ~$1.34; the default reuses.")
    parser.add_argument(
        "--universe", choices=("sp500", "watchlist"), default="sp500",
        help="★ DEFAULT `sp500` — the same ~510 the model trains on, so rank and "
             "sector-z features mean the same thing on both sides (AB-13). "
             "`watchlist` is config/settings.yaml's 130-name rel5 list, kept "
             "reachable for comparison. ⚠ DE-36: the universe is what NORMALISES "
             "the cross-section; the watchlist is what may be bought, and "
             "widening the first does not widen the second.")
    parser.add_argument(
        "--deliver", action="store_true",
        help="★★ RP-50 — SEND the card by email. ⚠ OUTWARD-FACING and OFF by "
             "default: the recipient comes from REPORT_RECIPIENT and a missing "
             "one raises rather than falling back to the SMTP user (RP-51). "
             "The card is sent whether or not it is actionable (RP-52), and a "
             "failed send fails the run — the CT-11.7 record is already on "
             "disk because `record` precedes `deliver` (OR-50).")
    parser.add_argument("--plan-only", action="store_true",
                        help="★ T-2 — print the graph without executing it")
    args = parser.parse_args(argv)
    as_of = args.as_of or datetime.now(timezone.utc).date()

    orc = build_orchestrator()

    if args.plan_only:
        # ★ T-2: inspectable WITHOUT executing. A graph you cannot read without
        #   running it is a graph nobody reviews.
        for job in orc.graph.order():
            deps = ", ".join(job.depends_on) or "-"
            print(f"{job.job_id:15s} <- {deps:35s} {job.invokes}")
        return EXIT_OK

    from src.orchestration.schedule.preconditions import BlockedPrecondition

    # ★★ OR-51 — the provenance is SUPPLIED. ⚠ Until 2026-08-27 every run
    #   recorded `git_sha: ""`, `config_hash: ""` and `inputs: []`, each the
    #   empty default of `trigger()`. `git_state()` existed and this path never
    #   called it, so OR-11's "a dirty tree is permitted and marked" was
    #   recording neither the sha nor the dirt.
    sha, dirty = git_state()
    triggered = orc.trigger(as_of=as_of, calendar=_calendar, day_bar=_day_bar(as_of),
                            model=_incumbent_model(),
                            git_sha=sha, dirty=dirty,
                            config_hash=config_hash(_run_config(args)))
    if isinstance(triggered, BlockedPrecondition):
        # ⚠ Blocked is not failure. A non-trading day and an already-claimed
        #   cadence window are both INFO (OR-42, OR-46).
        print(f"BLOCKED {triggered.code}: {triggered.reason}", file=sys.stderr)
        return EXIT_BLOCKED

    context = _context_for(triggered, as_of, want_thesis=args.thesis,
                           reauthor=args.reauthor,
                           universe_name=args.universe,
                           deliver=args.deliver)
    if context is None:
        print("BLOCKED: no market data supplied — D-07's universe fetch is not "
              "wired into this entrypoint yet", file=sys.stderr)
        return EXIT_BLOCKED
    outcome = orc.run(triggered.run_id, invoke=dispatch_for(context))
    _record_outcome(outcome, context)
    if artifact_allowed(outcome):
        print(f"SUCCESS {outcome.run_id}")
        _summarise(context)
        return EXIT_OK

    # ★ OR-19 + OR-45 — a failed run is LOUD, and the notice carries no
    #   analytical content. *A pipeline that fails quietly is indistinguishable
    #   from one that was never scheduled.*
    notice = failure_notice(outcome)
    assert_no_analysis(notice)
    print(f"{notice['status']} {notice['run_id']}: "
          f"{notice['failed_jobs']} {notice['error_codes']}", file=sys.stderr)
    return EXIT_FAILED


#: The universe the cross-section is computed over. ⚠ **DE-36: the UNIVERSE,
#: not the watchlist** — *a name excluded from the actionable slate still
#: participates in cross-sectional normalisation.*
UNIVERSE_CONFIG = "config/settings.yaml"

#: How much history the trailing features need. ⚠ `b3_minimal_v1`'s `mom_21`
#: and `vol_21` need 21 sessions; 200 calendar days leaves room for holidays
#: and is the window the live probe uses.
LOOKBACK_DAYS = 200


def load_universe(path: str = UNIVERSE_CONFIG) -> tuple[str, ...]:
    """The declared universe. ★ **DE-49**: a name the plan does not cover does
    not belong here, and discovering that at fetch time is too late."""
    import yaml

    with open(path, encoding="utf-8") as handle:
        settings = yaml.safe_load(handle)
    return tuple((settings.get("pipeline") or {}).get("tickers") or ())


def _run_config(args) -> dict:
    """★ OR-9/CN-5 — every config value the run used, hashed into the manifest.

    ⚠ **The switches belong in it.** `--universe` changes what the
    cross-section normalises over (DE-36) and `--thesis` changes whether the
    card can be actionable at all: two runs on the same day with different
    flags are different runs, and an identical `config_hash` would say they
    were not.
    """
    return {"universe": args.universe, "thesis": args.thesis,
            "reauthor": args.reauthor, "deliver": args.deliver,
            "universe_config": UNIVERSE_CONFIG}


def _delivery_credentials(deliver: bool):
    """`(recipient, user, password)` for RP-50/RP-51, or blanks when off.

    ⚠ **Never hardcoded and never defaulted.** A recipient that falls back to
    the SMTP user delivers to whoever holds the sending account, and mail to
    the wrong address is not recoverable.
    """
    from src.shared.secrets import Secret

    if not deliver:
        return "", None, None
    user, password = (os.environ.get("GMAIL_SMTP_USER"),
                      os.environ.get("GMAIL_APP_PASSWORD"))
    if not user or not password:
        raise SystemExit(
            "delivery was requested and GMAIL_SMTP_USER/GMAIL_APP_PASSWORD are "
            "not both set. ★ Source .env first (RP-23, SC-3)")
    return (os.environ.get("REPORT_RECIPIENT", ""),
            Secret("GMAIL_SMTP_USER", user),
            Secret("GMAIL_APP_PASSWORD", password))


def _context_for(manifest, as_of: date, *, want_thesis: bool = False,
                 reauthor: bool = False, universe_name: str = "watchlist",
                 deliver: bool = False):
    """Assemble the run's inputs — ★ **one CT-7.1 panel over the whole
    universe** (D-07 `assemble_universe_panel`).

    ⚠ **DE-13 is the spine**: a ticker that does not resolve **fails the run**,
    is not dropped, and does not become a row of NaNs. A partial panel is the
    defect MT-11 and RK-36 both refuse, so there is no path here that proceeds
    on one.
    """
    from datetime import timedelta

    import pandas as pd

    from src.data_engine.src.fmp import prices as fmp_prices
    from src.data_engine.src.fmp.client import FMPClient
    from src.data_engine.universe.prices import assert_complete, fetch_universe
    from src.orchestration.jobs.wiring import RunContext
    from src.feature_engineer.contracts.sets.b3_minimal_v1 import B3_MINIMAL_V1
    from src.shared.secrets import Secret

    # ★ DE-36 — the UNIVERSE is what normalises the cross-section; the
    #   watchlist is what may be bought. Widening the first does not widen the
    #   second, and AB-13 is about the first.
    # ★★ **The training universe by default** (AB-13). ⚠ The 130-name list was
    #   inherited from Release 5 and *nothing analytical picked it* — the spec's
    #   own arithmetic asks for ~330 (§5.3b), and scoring 130 with a model fitted
    #   on 497 feeds rank and sector-z features a differently-scaled input under
    #   identical column names, which a contract check cannot see.
    universe = (load_universe() if universe_name == "watchlist"
                else _sp500_universe())
    if not universe:
        return None

    key = os.environ.get("FMP_API_KEY")
    if not key:
        return None
    client = FMPClient(Secret("FMP_API_KEY", key))
    start = as_of - timedelta(days=LOOKBACK_DAYS)

    frames, report = fetch_universe(
        None, universe, start=start, end=as_of,
        fetch=lambda symbol: fmp_prices.raw_prices(client, symbol, start, as_of),
        # ★★ §6B/DE-63 — a renamed name is fetched under its CURRENT symbol.
        #   ⚠ `BK` returns 122 bars stopping at the changeover; `BNY` returns
        #   164 covering the same period. Without this the name silently leaves
        #   the cross-section while `universe_n` still counts it.
        symbol_for=_symbol_resolver(as_of))
    assert_complete(report)                    # ⛔ DE-13 — loud, not partial
    if report.fetched_as:
        print(f"  §6B: {len(report.fetched_as)} name(s) fetched under a resolved "
              f"symbol: " + ", ".join(f"{k}->{v}"
                                      for k, v in sorted(report.fetched_as.items())),
              file=sys.stderr)

    # ★★ **The contract the PROMOTED MODEL declares**, not a constant. ⚠ The
    #   model needs `price_and_fundamental@v1`'s 59 features and the B3 default
    #   carries 2; building the wrong one and scoring anyway is D-17.
    incumbent = _incumbent_model()
    contract = _contract_for(incumbent)
    # ★ Only when the contract asks for them — a run on the B3 contract needs
    #   no fundamentals and should not pay for the ledger reads.
    fundamentals = (_fundamentals_for(universe, as_of)
                    if any(f.name.startswith("f_") for f in contract.features)
                    else None)

    recipient, smtp_user, smtp_password = _delivery_credentials(deliver)
    return RunContext(
        as_of=as_of, adj_as_of=as_of, universe=universe,
        contract=contract, incumbent=incumbent, fundamentals=fundamentals,
        delisted=_delisted_for(universe, as_of),
        raw_prices=pd.concat(frames.values(), ignore_index=True),
        book_prices=_book_prices(frames),
        artifact_root=_state_dir() / "runs",
        # ★ RP-50/RP-51 — supplied, so the adapter decides nothing (OR-1).
        deliver=deliver, recipient=recipient,
        smtp_user=smtp_user, smtp_password=smtp_password,
        archive_root=_state_dir() / "deliveries",
        author_thesis=want_thesis, reauthor=reauthor,
        engine=_data_engine(universe, as_of=as_of) if want_thesis else None,
        observation_ledger=_observation_ledger() if want_thesis else None,
        fmp_client=_fmp_client() if want_thesis else None,
        price_fetch=_price_fetch(client, start, as_of),
        events=(), event_store_root=str(_state_dir() / "events"))


#: ★★ **The one thing standing between this pipeline and an actionable card,
#: on the D-01 side.** `author_thesis(bundle, author=..., k=3)` works — it was
#: run live against MU on 2026-08-25 (3 orderings, $1.09 of an $8.00 cap). What
#: does not exist is an **assembler that builds an `EvidenceBundle` for an
#: arbitrary ticker from D-07's data**; the live probe composed one by hand.
#:
#: ⚠ Until that lands, `RunContext.probed_thesis` stays `None`, `_thesis_gate`
#: falls back to the declared stub, and DN-39 keeps the card informational —
#: which is the correct outcome, not a workaround.
THESIS_ASSEMBLER_MISSING = (
    "D-01 has no ticker -> EvidenceBundle assembler; the k=3 probe is built and "
    "proven but has nothing to feed it in an unattended run (RA-4, BS-11)"
)


def _ingested_today(ledger, ticker: str) -> bool:
    """Has this ticker's ledger already been refreshed today?

    ★ `ingest_facts` is idempotent, so re-fetching is *correct* — it is merely
    **130 companyfacts payloads per run**, which measured at three of the five
    minutes a `--thesis` run took. ⚠ Daily granularity is the right coarseness:
    a filing that lands today is picked up tomorrow at the latest, and EDGAR
    publishes on a filing-date axis rather than continuously.
    """
    from datetime import datetime, timezone

    path = ledger.path(ticker)
    if not path.is_file():
        return False
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return modified.date() == datetime.now(timezone.utc).date()


def _record_outcome(outcome, context) -> None:
    """CT-8.2 into the run's CT-11.7 directory — ★ **including a failed one.**

    ⚠ **The outcome cannot be a graph job**: it is only known once every job has
    finished, so the `record` job writes everything else and this writes the one
    field that does not exist yet.

    ★ **D-08's own store writes D-08's own contract**, into the directory D-11
    owns. That is not a way around AC-8.2 — orchestration still imports nothing
    from `src.recording`; RC-33 asks that the record hold the RunOutcome, and it
    does. ⚠ `write_outcome` only, never `write`: the manifest is already there
    and RC-60 would refuse the second write, correctly.
    """
    from src.orchestration.state.manifest_store import ManifestStore

    root = getattr(context, "artifact_root", None)
    if root is None:
        return
    try:
        ManifestStore(root).write_outcome(outcome)
        # ★ The index is DERIVED (CT-11.7), and the outcome is the last write —
        #   so it is rebuilt here or `status` is blank for the newest run, which
        #   is precisely the run a reader is looking at. ⚠ Invoked by dotted
        #   name, never imported (OR-2, OR-48).
        from src.orchestration.jobs.graph import resolve_target

        resolve_target("src.recording.artifacts.store:rebuild_index")(root)
    except Exception as exc:                   # noqa: BLE001 — named, not fatal
        print(f"  note: could not record the run outcome: {exc}", file=sys.stderr)


def _data_engine(universe, *, as_of: date, ingest: bool = True):
    """D-07 for D-01's reads — ★ **ingesting EDGAR facts first**.

    ⚠ `DataEngine` reads ledgers and **nothing had ever written one**, so
    `get_fundamentals` answered correctly from an empty store and the assembler
    had no evidence to assemble. `ingest_facts` is idempotent by key, so this is
    safe on every run rather than something to guard with state.
    """
    from src.data_engine.ingest.edgar_facts import ingest_facts, load_cik_map
    from src.data_engine.ingest.observations import capture
    from src.data_engine.observation.ledger import ObservationLedger
    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.pit.models import UniverseEntry
    from src.data_engine.service import DataEngine
    from src.data_engine.src.edgar.client import EdgarClient
    from src.data_engine.universe.membership import Universe
    from src.shared.secrets import Secret

    cik_map = load_cik_map()
    entries = [UniverseEntry(ticker=t, cik=cik_map.get(t),
                             filer_class="10-K/10-Q" if cik_map.get(t) else "none",
                             source="edgar" if cik_map.get(t) else "fmp")
               for t in universe]
    root = _state_dir() / "facts"
    root.mkdir(parents=True, exist_ok=True)
    ledger = FactLedger(root)

    contact = os.environ.get("GMAIL_SMTP_USER") if ingest else None
    if contact:
        client = EdgarClient(Secret("EDGAR_CONTACT", contact))
        for entry in entries:
            if entry.cik is None or _ingested_today(ledger, entry.ticker):
                continue
            try:
                ingest_facts(client, ledger, ticker=entry.ticker, cik=entry.cik)
            except Exception as exc:           # noqa: BLE001 — named, not fatal
                print(f"  note: EDGAR ingest failed for {entry.ticker}: {exc}",
                      file=sys.stderr)

    observations = ObservationLedger(_state_dir() / "obs")

    # ★ Class-B capture — sector, business description and TTM ratios. ⚠ Only
    #   for names the BOOK or the top of the RANK will reach: `DEFAULT_SCHEDULE`
    #   caps the request rate by cadence, not the universe size, and 130 names
    #   × 4 field sets on every run is 520 calls for evidence that changes
    #   monthly. The cadence check inside `capture` still gates each one.
    # ★ Held names only. ⚠ The pre-run sweep used to cover the top 40 of the
    #   universe *hoping* to catch the nominee — and **SNDK, rank #1, sits at
    #   #124 of 130**; it was covered only because Victor holds it. The `observe`
    #   job now captures the nominated name after `rank`, by name, so this sweep
    #   no longer guesses. What is held is worth having regardless: D-05 reads
    #   the same ledger.
    fmp = _fmp_client() if ingest else None
    if fmp is not None:
        for ticker in _observation_targets():
            capture(fmp, observations, ticker=ticker, as_of=as_of)

    return DataEngine(universe=Universe(entries), fact_ledger=ledger,
                      observation_ledger=observations, price_source=None)


def _observation_targets() -> tuple:
    """The names in the book. ★ **Not a guess at the nominee.**

    ⚠ The nominated name is not known until `rank` has run, which is after this
    — so the `observe` job captures it there, by name. Guessing here covered
    rank #1 only by luck.
    """
    # ⚠ Invoked by dotted name, never imported — OR-2/OR-48. ★ This is the
    #   third time the shim has reached for `src.recording` by import and the
    #   third time the rule has caught it; the resolver exists so the reach is
    #   legal rather than merely tempting.
    from src.orchestration.jobs.graph import resolve_target

    try:
        held = {i.split("|")[0]
                for i in resolve_target(
                    "src.recording.book.load:held_instruments")()}
    except Exception:                          # noqa: BLE001 — a thinner sweep
        held = set()
    return tuple(sorted(held))


def _price_fetch(client, start, end):
    """`fetch(symbol) -> (price, currency) | None` — ★ **D-07's half of D-11's
    valuation.** The shim supplies HOW to price; the book decides WHAT.

    ⚠ Returns `None` rather than raising, because one unquotable holding is a
    fact D-11 reports by name (RC-10), not an orchestration failure.
    """
    from src.data_engine.src.fmp import prices as fmp_prices

    def fetch(symbol: str):
        try:
            frame = fmp_prices.raw_prices(client, symbol, start, end)
        except Exception as exc:               # noqa: BLE001 — reported, not raised
            print(f"  note: no quote for held name {symbol}: {exc}",
                  file=sys.stderr)
            return None
        if frame is None or len(frame) == 0:
            return None
        row = frame.iloc[-1]
        return int(row["close_minor"]) / 100.0, str(row["currency"])

    return fetch


def _book_prices(frames) -> dict:
    """`{instrument_id: (price, currency)}` for what D-07 actually quoted.

    ⚠ **Only US common stock.** A CDR is a separate security whose price is not
    its underlying's (RC-52), so `NVDA|CDR|CAD` is deliberately absent even
    though `NVDA` was fetched — substituting one for the other is the exact
    error D-11's valuation banner exists to forbid.
    """
    prices = {}
    for ticker, frame in frames.items():
        if frame is None or len(frame) == 0:
            continue
        row = frame.iloc[-1]
        # ⚠ `close_minor` is MINOR UNITS (DC-2). Dividing here is the one place
        #   it becomes a display float, and it goes straight into a market value
        #   that is reconciled against a broker balance — never into arithmetic
        #   that accumulates.
        currency = str(row["currency"])
        prices[f"{ticker}|COMMON|{currency}"] = (
            int(row["close_minor"]) / 100.0, currency)
    return prices


def _summarise(context) -> None:
    """★ What the run produced, in the terminal. ⚠ **`ranked_quantity`, not
    `z`** — QA-119: *publishing only `z` would let a consumer rank on the wrong
    quantity*, and the two orderings genuinely differ.
    """
    nomination = context.outputs.get("rank")
    if nomination is not None:
        print(f"  universe {nomination.universe_n} · horizon "
              f"{nomination.nominating_horizon}")
        for candidate in nomination.candidates[:5]:
            print(f"   #{candidate.rank} {candidate.ticker:<6} "
                  f"ranked_quantity {candidate.ranked_quantity:+.4f}  "
                  f"z {candidate.z:+.2f}")
    card = context.outputs.get("render")
    if card is not None:
        rec = context.outputs["decide"]
        print(f"  card: {card.ticker} (actionable={rec.actionable})")
        # ★★ DN-39 — when the card is informational, say WHY here, every run.
        #   ⚠ *"Not actionable"* with the reason buried on the artifact is the
        #   shape RA-30 refuses: a reader cannot tell a deliberate hold from a
        #   broken pipeline without opening something else.
        if not rec.actionable and rec.not_actionable_reason:
            print(f"        why: {rec.not_actionable_reason}")


def _state_dir():
    import pathlib

    root = pathlib.Path(os.environ.get("PIPELINE_STATE", ".state"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _calendar(day: date):
    """OR-7 — ★ **the calendar check belongs to D-07.** D-08 asks; D-07 answers."""
    from src.data_engine.calendar.trading_day import is_trading_day

    return is_trading_day(day)


#: ★ The precondition asks *"has the session's opening auction settled?"* — a
#: market-wide fact — so **one liquid reference answers it**. ⚠ The decision
#: input is every name's open, and that arrives in the panel; conflating the two
#: would make the run depend on one ticker's data quality.
OPEN_REFERENCE = "SPY"


def _sp500_universe() -> tuple:
    """The same list the training run declares — ★ **one source, so train and
    infer cannot drift apart** (AB-13)."""
    from src.models.train.run import load_sp500

    return load_sp500()


def _fundamentals_for(universe, as_of: date):
    """D-07's PIT fundamentals and sectors for the `f_*` block.

    ★ **Reads the ledgers; it does not ingest.** Ingest is the training run's
    job (`--thesis` refreshes what a thesis needs) — a daily inference run that
    silently fetched 500 companyfacts payloads would be doing D-07's write path
    on a schedule nobody declared.
    """
    engine = _data_engine(universe, as_of=as_of, ingest=False)
    rows = {}
    for ticker in universe:
        try:
            rows[ticker] = engine.get_fundamentals(ticker, as_of=as_of)
        except Exception:                      # noqa: BLE001 — absent, not fatal
            continue
    return {"rows_by_ticker": rows, "sectors": _sectors_for(engine, universe, as_of)}


def _sectors_for(engine, universe, as_of: date) -> dict:
    """`{TICKER: sector}` from D-07's Class-B profile, for the `*_sector_z` five.

    ⚠ A name with no captured profile is simply absent — `sector_z` then nulls
    that cell rather than assigning it to a bucket it was never observed in.
    """
    from src.feature_engineer.fundamental.build import SECTOR_Z

    del SECTOR_Z
    out = {}
    for ticker in universe:
        try:
            observation = engine.get_observation(ticker, "profile", as_of=as_of,
                                                 consumer="thesis")
        except Exception:                      # noqa: BLE001
            continue
        payload = (observation or {}).get("payload") or {}
        sector = payload.get("sector")
        if sector:
            out[ticker] = sector
    return out


def _symbol_resolver(as_of: date):
    """§6B — `ticker -> the symbol to request`, ★ **invoked by dotted name**.

    ⚠ Returns the identity map when the symbol history is empty or unreadable:
    an unpopulated store must behave exactly as before, never block the run.
    ★ Run `python -m src.data_engine.ingest symbols` to populate it.
    """
    from src.orchestration.jobs.graph import resolve_target

    try:
        history = resolve_target("src.data_engine.symbology.master:SymbolHistory")(
            _state_dir() / "symbology")
        if not len(history.read()):
            return None
        fetch_symbol_for = resolve_target(
            "src.data_engine.symbology.master:fetch_symbol_for")
        return lambda ticker: fetch_symbol_for(history, ticker, as_of=as_of)
    except Exception as exc:                   # noqa: BLE001 — named, not fatal
        print(f"  note: symbol history unavailable: {exc}", file=sys.stderr)
        return None


def _delisted_for(universe, as_of: date) -> dict:
    """D-07's current-state answer, ★ **invoked by dotted name** (OR-2/OR-48).

    ⚠ Returns `{}` on any failure rather than raising: a store that cannot be
    read is a reason to nominate carefully, not a reason to stop the run — and
    the emptiness is visible in the nomination's `excluded[]`, which stays empty.
    """
    from src.orchestration.jobs.graph import resolve_target

    try:
        store = resolve_target("src.data_engine.calendar.store:EventStore")(
            _state_dir() / "events")
        return resolve_target("src.data_engine.calendar.gate:delisted_names")(
            store, as_of=as_of, tickers=universe)
    except Exception as exc:               # noqa: BLE001 — named, not fatal
        print(f"  note: could not read delistings: {exc}", file=sys.stderr)
        return {}


def _contract_for(incumbent):
    """The feature contract this run must build.

    ★ Read from the promoted artifact's manifest, so **the panel and the model
    cannot disagree by construction**. ⚠ With no model the B3 contract stands —
    the rule-based ranker needs `mom_21` and `vol_21` and nothing else.
    """
    from src.feature_engineer.contracts.sets.b3_minimal_v1 import B3_MINIMAL_V1

    if not incumbent:
        return B3_MINIMAL_V1

    from src.feature_engineer.contracts.sets.fundamental_v1 import FUNDAMENTAL_V1
    from src.feature_engineer.contracts.sets.price_ohlcv_v1 import PRICE_OHLCV_V1
    from src.feature_engineer.contracts.spec import FeatureContract

    ref = (incumbent.get("contract") or {})
    if ref.get("name") != "price_and_fundamental":
        return B3_MINIMAL_V1
    return FeatureContract(
        name="price_and_fundamental", version=int(ref.get("version", 1)),
        created=str(_TODAY), note="rebuilt at inference from the model's manifest",
        features=PRICE_OHLCV_V1.features + FUNDAMENTAL_V1.features)


def _observation_ledger():
    from src.data_engine.observation.ledger import ObservationLedger

    return ObservationLedger(_state_dir() / "obs")


def _fmp_client():
    """DE-1 — ★ **all external access goes through D-07**, and the key never
    leaves the `Secret` wrapper (DE-8)."""
    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret

    key = os.environ.get("FMP_API_KEY")
    return FMPClient(Secret("FMP_API_KEY", key)) if key else None


def _day_bar(as_of: date, *, ticker: str = OPEN_REFERENCE, row=None):
    """OR-32/OR-33/OR-47 — the settled day-T **opening print**, from D-07.

    ★ **The print, not the bar** (D-07 **DE-47**): the auction is final at 09:30,
    the bar not until 16:00, so `high`/`low`/`close` come back explicitly `None`
    — *the absence of a settled value, stated*, which OR-47 accepts and the
    collapsed-bar test still rejects when all four arrive equal.

    ⚠ `row` is the vendor row and is `None` until the FMP open feed is wired, so
    this returns `None` and the run **blocks** — which is correct, not a stub:
    OR-33 forbids substituting the previous close.
    """
    from src.data_engine.observation.day_open import day_open
    from src.data_engine.src.fmp import prices as fmp_prices

    if row is None:
        client = _fmp_client()
        if client is not None:
            try:
                row = fmp_prices.open_row(client, ticker, as_of)
            except Exception:                               # noqa: BLE001
                row = None            # ⇒ unsettled ⇒ the run blocks (OR-33)
    now = datetime.now(timezone.utc)
    print_ = day_open(ticker=ticker, as_of=as_of, row=row, now=now)
    return print_.as_precondition_bar()


def _incumbent_model():
    """OR-44 — the **promoted** artifact for this role and horizon, or `None`.

    ★★ **Promoted, not merely fitted.** `ArtifactStore.promoted()` reads
    `promotion.json`, whose absence *is* the refusal — MT-17 makes promotion the
    only path to production, and treating the presence of a model as licence to
    score with it is exactly what that rule exists to prevent.

    ⚠ `None` is the ordinary state today: the first fit measured a walk-forward
    IC of **0.0203 against an MDE of 0.0123 but a realised t of 1.42**, so
    `ic_significance_gate` refused it — and `cost_survival` cannot even be
    evaluated without a D-03 backtest (MT-19). `assert_anchor` reads `None` as
    *no model in this run*, which is true.
    """
    from src.orchestration.jobs.graph import resolve_target

    try:
        store = resolve_target("src.models.artifact.store:ArtifactStore")(
            _state_dir() / "models")
        artifact_id = store.promoted(role=SELECTION_ROLE, horizon_id="h1m")
    except Exception as exc:                   # noqa: BLE001 — named, not fatal
        print(f"  note: could not read the model registry: {exc}",
              file=sys.stderr)
        return None
    if artifact_id is None:
        return None
    files = store.read(artifact_id)
    manifest = files.get("manifest.json") or {}
    return {
        "artifact_id": artifact_id,
        "estimator": store.load_estimator(artifact_id),
        "features": files.get("features.json") or [],
        # ★★ OR-44 — **read from the manifest, never defaulted.** A model that
        #   cannot say which anchor it was trained on may not score against one:
        #   `open` and `close` differ by a full session's drift (OR-35), and the
        #   mismatch is INV-4 and **invisible in backtest, because the backtest
        #   shares it**. A `.get(..., "open")` here would manufacture the
        #   declaration the rule exists to demand.
        "trained_anchor": manifest.get("decision_anchor"),
        "contract": manifest.get("feature_contract"),
        "training_names": manifest.get("training_names"),
    }


#: D-04's role name for the daily selection model (MT-30's 1m leg).
SELECTION_ROLE = "selection"


if __name__ == "__main__":       # pragma: no cover - the timer's target
    raise SystemExit(main())
