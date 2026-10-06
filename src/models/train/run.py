"""★★ The training run — D-04's `fit()` had never been called in production.

Every piece existed: `TrainSpec`, `fit`, the zoo's `LightGBMRanker`, D-03's
`make_folds` and gates, `promote` and the `Registry`. **Nothing joined them**, so
`_incumbent_model()` returned `None` and the daily card was ranked by
`z(mom_21) × vol_21 × √21` — a two-feature formula, not a prediction.

```text
   universe -> prices -> EDGAR facts -> panel(price + fundamental)
            -> labels(1m, open anchor) -> folds -> fit
            -> gates -> promote | refuse
```

⚠⚠ **SURVIVORSHIP — INV-017, and it cannot be fully corrected here.**
`config/sp500_tickers.yaml` is **today's** index. Every name in a 2015-2026
sample drawn from it survived to 2026 *and* is still a constituent, so the
companies that went bankrupt, were taken under, or shrank out of the index are
absent. D-07 §5A.5 says it plainly — *"the universe is live-listed names only;
**nothing currently accounts for what left**"* — and **DE-35 makes index
membership `UNCHECKED` permanently**, so the historical constituent list cannot
be reconstructed from the sources this project has.

★ **What that means for the number:** a measured IC from this run is an **upper
bound**, not an estimate. It is still worth measuring — a signal that fails the
gate on a survivorship-flattered sample would fail harder on an honest one — but
a signal that *passes* has not yet been shown to work.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date, timedelta

#: HorizonSet v1's 1m leg. ⚠ `TrainSpec` refuses a SELECTION model at any other
#: horizon: *every currently deployed model is fitted against `fwd_ret_1w` and is
#: therefore fitted to a TIMING objective while being used for SELECTION* (MT-30).
SELECTION_HORIZON_DAYS = 21

#: ★ §5.3b's arithmetic: at `n = 130` the smallest IC detectable at `t > 3` is
#: **0.0479 at 1q** — a bar no realistic signal clears. *"~330 names reaches
#: t = 3 at 1q on existing history. That is a data task — an ETL re-run."*
BREADTH_FOR_1Q = 330

#: How far back to fetch. ⚠ An admitted choice: ten years spans two regimes and
#: is what the panel's MDE table (`n = 130, T = 1915`) was computed on.
DEFAULT_YEARS = 10


@dataclass
class TrainingInputs:
    """What a run was actually given — ★ every field reaches the manifest."""

    universe: tuple
    as_of: date
    start: date
    horizon_days: int = SELECTION_HORIZON_DAYS
    #: ⚠ Names that failed to resolve, kept rather than silently dropped: DE-13
    #: says *a missing name is not dropped and does not become a row of NaNs*.
    unresolved: dict = field(default_factory=dict)
    #: ★ INV-017. Recorded on every run so the number is never read as an
    #: unqualified estimate.
    survivorship: str = (
        "UNCORRECTED — the universe is today's index (INV-017). Index membership "
        "is UNCHECKED permanently (DE-35), so a measured IC is an UPPER BOUND."
    )


def load_sp500(path: str = "config/sp500_tickers.yaml") -> tuple:
    """The full S&P 500 list D-07 already routes by CIK.

    ★ Taking the index whole is a **declaration, not a selection** — which is
    what keeps QQ-11's *"by added breadth, not count"* caveat from becoming
    cherry-picking. ⚠ It does not answer QQ-11: breadth is about residual
    correlation (QA-43), and 500 correlated names are not 500 bets.
    """
    from src.data_engine.ingest.edgar_facts import load_cik_map

    return tuple(sorted(load_cik_map(path)))


def fetch_prices(client, universe, *, start: date, end: date,
                 on_error=None) -> tuple:
    """Raw OHLCV for the universe. Returns `(frames, unresolved)`.

    ⚠ **A name that fails is NAMED, never dropped quietly** (DE-13). The whole
    point of `assert_complete` one level up is that a shrinking universe is a
    finding, and a training set that quietly lost 40 names has a different
    cross-section from the one its manifest claims.
    """
    from src.data_engine.src.fmp import prices as fmp_prices

    frames, unresolved = {}, {}
    for ticker in universe:
        try:
            frames[ticker] = fmp_prices.raw_prices(client, ticker, start, end)
        except Exception as exc:               # noqa: BLE001 — recorded, not raised
            unresolved[ticker] = str(exc)[:160]
            if on_error is not None:
                on_error(ticker, exc)
    return frames, unresolved


def ingest_universe_facts(edgar, ledger, universe, *, cik_map,
                          on_error=None) -> dict:
    """EDGAR companyfacts for the universe. ★ Idempotent by key, so re-runnable.

    ⚠ Measured 2026-08-27: a `companyfacts` payload is ~4.5 MB and the whole
    universe takes minutes, not hours — the cost is not the reason this had never
    been run.
    """
    from src.data_engine.ingest.edgar_facts import ingest_facts

    failures = {}
    for ticker in universe:
        cik = cik_map.get(ticker)
        if cik is None:
            failures[ticker] = "no CIK in the routing map"
            continue
        try:
            ingest_facts(edgar, ledger, ticker=ticker, cik=cik)
        except Exception as exc:               # noqa: BLE001
            failures[ticker] = str(exc)[:160]
            if on_error is not None:
                on_error(ticker, exc)
    return failures


def build_training_panel(*, price_frames, engine, universe, as_of: date,
                         adj_as_of: date, calendar_report, sectors=None):
    """The CT-2.2 panel over both contracts — ★ 59 of §5.3's 61 features."""
    import pandas as pd

    from src.data_engine import build_price_panel
    from src.feature_engineer.contracts.sets.fundamental_v1 import FUNDAMENTAL_V1
    from src.feature_engineer.contracts.sets.price_ohlcv_v1 import PRICE_OHLCV_V1
    from src.feature_engineer.contracts.spec import FeatureContract
    from src.feature_engineer.ml_features.assemble import build_panel

    raw = pd.concat(price_frames.values(), ignore_index=True)
    prices = build_price_panel(raw, (), adj_as_of)

    # ★ One contract, so ONE `(name, version)` reaches the manifest. ⚠ Two
    #   panels merged after the fact would give the artifact two contracts to
    #   name and FE-3 only one field to name them in.
    # ★ The combined version tracks its MEMBERS, so adding a feature to either
    #   side cannot leave the joint identity unchanged (FE-2).
    combined = FeatureContract(
        name="price_and_fundamental",
        version=PRICE_OHLCV_V1.version * 100 + FUNDAMENTAL_V1.version,
        created=str(as_of),
        note=("price_ohlcv@v1 + fundamental@v1 — §5.3's 61 less the two Group-C "
              "formula features, which need a price D-02 does not hold."),
        features=PRICE_OHLCV_V1.features + FUNDAMENTAL_V1.features)

    rows_by_ticker = {t: engine.get_fundamentals(t, as_of=as_of)
                      for t in universe if t in price_frames}
    panel = build_panel(
        contract=combined, price_panel=prices, calendar_report=calendar_report,
        as_of=as_of, adj_as_of=adj_as_of,
        fundamentals={"rows_by_ticker": rows_by_ticker, "sectors": sectors})
    return panel, combined


def build_training_labels(prices, *, horizon_days: int, as_of: date):
    """CT-2.3 labels at the **open** anchor.

    ★ QA-71/FE-31: `open(T+h)/open(T) − 1`, both ends on the same field, because
    D-08 decides at the open. ⚠ `assert_no_lookahead` is called here rather than
    trusted: a label whose availability date exceeds the as-of is the one
    legitimate look-ahead in the system and the easiest to over-extend.
    """
    from src.feature_engineer.contracts.labels import (
        LabelDef,
        assert_no_lookahead,
        build_labels,
    )

    label_def = LabelDef(
        label_def_id=f"fwd_ret_{horizon_days}d_open",
        horizon_days=horizon_days, decision_anchor="open")
    labels = build_labels(label_def=label_def, price_panel=prices)
    return assert_no_lookahead(labels, as_of=as_of), label_def


def evaluate(result, *, horizon_id: str, names: int, effective_breadth=None,
             gross_return=None, net_return=None) -> dict:
    """D-03's gates. ★ **The required set is D-03's and is imported** (MT-50).

    ⚠ D-04 declaring its own list is how promotion came to demand a `stability`
    gate D-03 never produces, and every artifact was refused.
    """
    from src.quant.gates.metric_gate import (
        breadth_gate,
        cost_survival_gate,
        ic_significance_gate,
    )

    outcomes = {
        "ic_significance": ic_significance_gate(result, horizon_id=horizon_id),
        "breadth": breadth_gate(effective_breadth=effective_breadth,
                                names=names, horizon_id=horizon_id),
    }
    if gross_return is not None or net_return is not None:
        outcomes["cost_survival"] = cost_survival_gate(
            gross_return=gross_return, net_return=net_return)
    return outcomes


def summarise(inputs: TrainingInputs, panel, labels) -> dict:
    """What the run saw. ★ Printed and put on the manifest, never only printed."""
    names = int(panel["ticker"].nunique()) if len(panel) else 0
    return {
        "names": names,
        "rows": int(len(panel)),
        "dates": int(panel["date"].nunique()) if len(panel) else 0,
        "labels": int(len(labels)),
        "unresolved": len(inputs.unresolved),
        "horizon_days": inputs.horizon_days,
        # ⚠ Carried on the artifact, not merely logged (INV-017).
        "survivorship": inputs.survivorship,
        "breadth_note": (
            f"n={names}. §5.3b: ~{BREADTH_FOR_1Q} names reaches t=3 at 1q; "
            f"1m clears the bar on the current panel (t=3.25 at IC=0.03). "
            f"⚠ Count is not breadth — QA-43's residual correlation decides "
            f"(QQ-11, open)."),
    }


def elapsed(since: float) -> str:
    return f"{time.time() - since:.0f}s"


def default_window(as_of: date, *, years: int = DEFAULT_YEARS) -> date:
    return as_of - timedelta(days=365 * years)


def fit_selection_model(*, panel, labels, contract, label_def, as_of: date,
                        adj_as_of: date, horizon_days: int, seed: int = 42):
    """Fit the SELECTION model and return `(artifact, frame)`.

    ★ **The estimator is injected** (MT-35): D-04 owns the protocol, the zoo owns
    the family, and `fit` never chooses columns — *an estimator that can narrow
    its own inputs is `_select_features` reappearing inside the zoo* (MT-6).

    ⚠ **Rows with a null feature are dropped here, and the count is returned.**
    LightGBM tolerates NaN and would train happily on a panel where a bank
    contributes only the columns a bank reports — which is **FE-37 arriving as a
    fitted parameter**. Dropping is the consumer decision FE-15 assigns to this
    layer, and it is reported rather than performed silently.
    """
    from src.models.train.fit import TrainSpec, fit
    from src.models.zoo.gbdt import LightGBMRanker

    features = tuple(contract.feature_names)
    spec = TrainSpec(
        contract_name=contract.name, contract_version=contract.version,
        label_def_id=label_def.label_def_id, decision_anchor="open",
        horizon_id="h1m", horizon_days=horizon_days,
        protocol={"kind": "time_series_holdout"},
        seeds={"estimator": seed},
        framework={"lightgbm": _lightgbm_version()},
        code_version="rel6",
        # ★ FE-2 — the membership fingerprint travels with the artifact.
        contract_hash=contract.content_hash)

    artifact = fit(spec, panel=panel, labels=labels,
                   estimator=LightGBMRanker(seed=seed), feature_names=features,
                   adj_as_of=adj_as_of, as_of=as_of)
    return artifact


def _lightgbm_version() -> str:
    try:
        import lightgbm

        return str(lightgbm.__version__)
    except Exception:                          # noqa: BLE001 — recorded as absent
        return "unavailable"


def rank_ic(artifact, panel, labels, *, feature_names) -> dict:
    """Spearman rank IC of the fitted scores against realised returns.

    ★ **Per date, then averaged** — that is what a cross-sectional IC is. ⚠ A
    pooled correlation over every `(ticker, date)` row measures *"do high scores
    go with high returns anywhere in the sample"*, which a common market factor
    satisfies without the model ranking anything within a day.
    """
    import numpy as np
    import pandas as pd

    frame = panel.merge(labels[["ticker", "date", "value"]],
                        on=["ticker", "date"], how="inner")
    # ⚠ **Drop on the LABEL only.** Requiring all 59 features non-null removes
    #   every row — `f_market_to_book` needs a market cap and the five
    #   `*_sector_z` need a sector, and neither is supplied by default. ★ That is
    #   FE-37 arriving as an empty measurement rather than as a warning, and the
    #   fix is to report the coverage (see `feature_coverage`) instead of
    #   silently intersecting it away.
    frame = frame.dropna(subset=["value"])
    if frame.empty:
        return {"mean_ic": None, "dates": 0, "t_stat": None,
                "why": "no rows survived the join and the null drop"}

    frame["_score"] = artifact.estimator.predict(frame[list(feature_names)])
    per_date = []
    for _day, group in frame.groupby("date", sort=True):
        if len(group) < 3:                     # a rank over two names is ±1
            continue
        per_date.append(group["_score"].corr(group["value"], method="spearman"))

    values = pd.Series(per_date, dtype="float64").dropna()
    if values.empty:
        return {"mean_ic": None, "dates": 0, "t_stat": None,
                "why": "no date had three rankable names"}

    mean = float(values.mean())
    # ⚠ Overlapping labels: a 21-day horizon makes consecutive dates share 20 of
    #   21 days, so the independent count is dates/h — §5.3b's own correction.
    independent = max(len(values) / 21.0, 1.0)
    t_stat = mean / (values.std(ddof=1) / np.sqrt(independent)) \
        if values.std(ddof=1) > 0 else None
    return {"mean_ic": mean, "dates": int(len(values)),
            "t_stat": float(t_stat) if t_stat is not None else None,
            "rows": int(len(frame))}


def feature_coverage(panel, feature_names) -> dict:
    """Per-feature non-null share — ★ **FE-37 made visible.**

    ⚠ A column that is 100 % null is not a feature; it is a promise. LightGBM
    accepts it without complaint and the manifest still claims it, so the
    artifact's declared input count and its *effective* one diverge silently.
    """
    rows = len(panel)
    if not rows:
        return {}
    share = {name: float(panel[name].notna().mean())
             for name in feature_names if name in panel.columns}
    empty = sorted(n for n, v in share.items() if v == 0.0)
    thin = sorted(n for n, v in share.items() if 0.0 < v < 0.25)
    return {
        "declared": len(feature_names),
        "all_null": empty,
        "under_25pct": thin,
        "effective": len(share) - len(empty),
        "mean_coverage": round(sum(share.values()) / max(len(share), 1), 3),
    }


def walk_forward_ic(*, panel, labels, contract, label_def, as_of: date,
                    adj_as_of: date, horizon_days: int, n_folds: int = 5,
                    seed: int = 42):
    """★★ **Out-of-sample predictions across purged, embargoed folds → D-03's IC.**

    ⚠ *An in-sample IC is not a weak result, it is not a result.* Measured
    2026-08-27 on 500 names over ten years: **in-sample 0.112, walk-forward
    0.0203**. The gap is the whole reason this exists.

    ★★ **The statistic is D-03's, not D-04's.** `quant.metrics.ic.rank_ic`
    returns a `CT-3.x ICResult` carrying `effective_n` and an
    autocorrelation-corrected SE, and `ic_significance_gate` reads exactly that.
    ⚠ A hand-rolled mean-and-t here would be **two implementations of one
    statistic** — and the one that matters most, since it is what promotion turns
    on. *(This function did roll its own until 2026-08-27; the gate could not
    consume it.)*

    ★ D-03 also owns the split (**QA-18**): `purge_days` is the **longest**
    horizon in the set, not the one being evaluated, and the purge runs on
    **both sides** — a training row *after* the test block whose label window
    reaches back into it is exactly as leaky as one before.
    """
    import pandas as pd

    from src.models.train.fit import TrainSpec, fit
    from src.models.zoo.gbdt import LightGBMRanker
    from src.quant.backtest.protocol import (
        assert_no_leakage,
        derive_protocol,
        make_folds,
    )
    from src.quant.horizons.horizon_set import PRODUCTION_V1
    from src.quant.metrics.ic import rank_ic

    protocol = derive_protocol(PRODUCTION_V1, n_folds=n_folds)
    frame = panel.merge(labels[["ticker", "date", "value"]],
                        on=["ticker", "date"], how="inner").dropna(subset=["value"])
    dates = tuple(sorted(pd.to_datetime(frame["date"]).dt.date.unique()))
    folds = make_folds(dates, protocol)

    features = tuple(contract.feature_names)
    day = pd.to_datetime(frame["date"]).dt.date
    predictions, per_fold = [], []

    for fold in folds:
        assert_no_leakage(fold, purge_days=protocol.purge_days)
        train = frame[day.isin(set(fold.train_dates))]
        test = frame[day.isin(set(fold.test_dates))]
        if train.empty or test.empty:
            per_fold.append({**fold.to_json_obj(), "ic": None,
                             "why": "empty split"})
            continue

        spec = TrainSpec(
            contract_name=contract.name, contract_version=contract.version,
            label_def_id=label_def.label_def_id, decision_anchor="open",
            horizon_id="h1m", horizon_days=horizon_days,
            protocol={"purge_days": protocol.purge_days,
                      "embargo_days": protocol.embargo_days,
                      "n_folds": n_folds, "fold": fold.index},
            seeds={"estimator": seed}, code_version="rel6")
        artifact = fit(spec, panel=train.drop(columns=["value"]), labels=labels,
                       estimator=LightGBMRanker(seed=seed),
                       feature_names=features, adj_as_of=adj_as_of, as_of=as_of)

        scored = test[["ticker", "date", "value"]].copy()
        scored["score"] = artifact.estimator.predict(test[list(features)])
        predictions.append(scored)
        # ★ Per fold, through the same D-03 function — never a second formula.
        fold_ic = rank_ic(scored, horizon_days=horizon_days)
        per_fold.append({**fold.to_json_obj(), "ic": fold_ic.mean_ic,
                         "test_rows": int(len(test))})

    if not predictions:
        from src.quant.metrics.ic import NOT_EVALUATED, ICResult

        return (ICResult(horizon_days=horizon_days, mean_ic=None, dates=0,
                         names_per_date=0.0, effective_n=None,
                         corrected_se=None, status=NOT_EVALUATED,
                         why="no fold produced a usable test split"),
                per_fold, pd.DataFrame())

    scored = pd.concat(predictions, ignore_index=True)
    # ★ The out-of-sample predictions are returned as well as the statistic:
    #   `cost_survival` needs a SIMULATION over them, and re-scoring to get it
    #   would be a second inference path that could disagree with this one.
    return rank_ic(scored, horizon_days=horizon_days), per_fold, scored


#: ★ The one gate D-03 cannot answer from a fit alone. ⚠ `cost_survival` needs a
#: BACKTEST — gross and net returns after QA-123's commission ($0 since F12 D8, 2026-10-05; was 9.95) — and D-04
#: does not run one (**MT-19: D-04 does not evaluate itself**). Reporting it as
#: `NOT_EVALUATED` is what makes promotion refuse; scoring it PASS here would be
#: D-04 marking its own homework.
COST_GATE_UNAVAILABLE = (
    "no backtest was run, so gross/net returns do not exist. MT-19 puts "
    "evaluation in D-03; a fit cannot answer a cost question about itself"
)


def gate_outcomes(ic_result, *, horizon_id: str, names: int,
                  effective_breadth=None, simulation=None) -> dict:
    """D-03's gates over the walk-forward result. ★ **The required set is D-03's.**

    ⚠ MT-50: D-04 declaring its own list is how promotion came to demand a
    `stability` gate D-03 never produced, and every artifact was refused.
    """
    from src.quant.backtest.costs import CostModel
    from src.quant.gates.metric_gate import (
        REQUIRED_GATES,
        breadth_gate,
        cost_survival_gate,
        ic_significance_gate,
    )

    outcomes = {
        "ic_significance": ic_significance_gate(ic_result, horizon_id=horizon_id),
        "breadth": breadth_gate(effective_breadth=effective_breadth,
                                names=names, horizon_id=horizon_id),
    }
    if simulation:
        # ★ The gate reads what the simulation MEASURED. ⚠ `None` returns from
        #   `simulate` stay `None`: QA-17 says an uncomputable statistic is
        #   NOT_EVALUATED, and passing 0.0 would read as a costless strategy.
        outcomes["cost_survival"] = cost_survival_gate(
            gross_return=simulation.get("gross_return"),
            net_return=simulation.get("net_return"),
            horizon_id=horizon_id,
            costs_charged=simulation.get("costs_charged",
                                         CostModel().components))
    # ⚠ Every required gate gets an entry, even the one that cannot be run — an
    #   ABSENT key and a NOT_EVALUATED one are the same to `promote`, and the
    #   second says why.
    for gate_id in REQUIRED_GATES:
        outcomes.setdefault(gate_id, None)
    return outcomes


def measure_breadth(scored, *, horizon_days: int, sectors=None) -> dict:
    """QA-43 from the same predictions the IC and the simulation read.

    ★ One source for all three, so a breadth figure cannot describe a different
    universe from the one that was scored.
    """
    from src.quant.metrics.breadth import from_predictions

    if scored is None or not len(scored):
        return {"breadth": None, "why": "no scored predictions"}
    return from_predictions(scored, horizon_days=horizon_days, sectors=sectors)


def decide_promotion(artifact, *, ic_result, names: int, store,
                     backtest_result_id: str = "", promoted_by: str = "training-run",
                     effective_breadth=None, simulation=None, breadth=None) -> dict:
    """Persist the artifact, then promote **only if every required gate passes**.

    ★ **The artifact is written either way.** A refused model is a record, and it
    is the most useful thing to hold when the next one passes.

    ⚠⚠ **Survivorship rides on the decision** (INV-017). The sample is today's
    index over ten years, so a *passing* gate has not shown the signal works —
    only that it cleared a bar on a flattered sample. The reason is written into
    the evaluation file rather than left in a chat log.
    """
    from datetime import datetime, timezone

    from src.models.governance.promotion import PASS, promote
    from src.quant.gates.metric_gate import REQUIRED_GATES

    outcomes = gate_outcomes(
        ic_result, horizon_id=artifact.manifest.horizon_id, names=names,
        effective_breadth=(effective_breadth if effective_breadth is not None
                           else (breadth or {}).get("breadth")),
        simulation=simulation)
    verdicts = {gate_id: (getattr(result, "verdict", None) or "NOT_EVALUATED")
                for gate_id, result in outcomes.items()}

    evaluation = {
        "ic": ic_result.to_json_obj(),
        "gates": {gate_id: (result.to_json_obj()
                            if hasattr(result, "to_json_obj")
                            else {"verdict": "NOT_EVALUATED",
                                  "why": COST_GATE_UNAVAILABLE})
                  for gate_id, result in outcomes.items()},
        "survivorship": TrainingInputs.__dataclass_fields__[
            "survivorship"].default,
        "simulation": dict(simulation) if simulation else None,
        "breadth": dict(breadth) if breadth else None,
        "required_gates": list(REQUIRED_GATES),
    }
    store.write(artifact, evaluation=evaluation)

    refused = [g for g in REQUIRED_GATES if verdicts.get(g) != PASS]
    if refused:
        return {"promoted": False, "refused_gates": refused,
                "verdicts": verdicts, "artifact_id": artifact.artifact_id}

    record = promote(artifact, backtest_result_id=backtest_result_id,
                     gate_outcomes=verdicts, promoted_by=promoted_by,
                     at=datetime.now(timezone.utc))
    store.record_promotion(record)
    return {"promoted": True, "verdicts": verdicts,
            "artifact_id": artifact.artifact_id}


def d03_evaluate(*, universe, scored, simulation, breadth, horizon_days: int,
                 as_of: date, start: date, capital: float, contract,
                 calendar_check_id: str) -> object:
    """★★ **D-03 grades the model; D-04 consumes the verdict.**

    ⚠ *Found 2026-08-27 by the rule itself:* all three gates passed and promotion
    **still refused** — `promote()` demands a D-03 `BacktestResult` id and none
    existed, because the training run had been computing gate outcomes **inside
    D-04**. That is the domain marking its own homework, and **MT-19 forbids it
    in exactly those words**: *"D-04 does not evaluate itself; a promotion with
    no evaluation is the gate skipped, not passed."*

    ★ So the same numbers now travel through `quant.backtest.engine.evaluate`,
    which builds the `GateSet` per horizon (QA-16) and returns a
    `CT-3.2 BacktestResult` carrying a `result_id`. **The id is the evidence** —
    a promotion that cannot name one is a promotion with no evaluation behind it.

    ⚠ `survivorship_handled=False` is passed **explicitly**. QA-14: *a backtest
    over currently-listed names only is reported as **biased**, not as a result*
    — and INV-017 says it cannot be corrected from these sources.
    """
    from src.quant.backtest.costs import CostModel
    from src.quant.backtest.engine import evaluate
    from src.quant.contracts.backtest import BacktestSpec
    from src.quant.horizons.horizon_set import PRODUCTION_V1

    horizons = [h for h in PRODUCTION_V1.horizons
                if h.trading_days == horizon_days]
    frame = scored.copy()
    frame["horizon_days"] = horizon_days

    spec = BacktestSpec(
        universe=tuple(universe), start=start, end=as_of,
        horizon_set_name=PRODUCTION_V1.name,
        horizon_set_version=PRODUCTION_V1.version,
        initial_capital=capital, contract_version=contract.version,
        calendar_check_id=calendar_check_id, as_of=as_of, adj_as_of=as_of,
        decision_anchor="open",
        protocol={"kind": "purged_embargoed_walk_forward"},
        cost_model=CostModel().to_json_obj(),
        rebalance=f"every {horizon_days}d",
        # ⚠ Explicit, not defaulted — see the docstring.
        survivorship_handled=False)

    return spec, evaluate(
        spec, predictions=frame, horizons=horizons,
        effective_breadth=(breadth or {}).get("breadth"),
        gross_return=(simulation or {}).get("gross_return"),
        net_return=(simulation or {}).get("net_return"))


def training_calendar_check(*, store, universe, start: date, as_of: date,
                            run_id: str):
    """§6A's gate over the **training window** — ★ AB-9's stub, replaced.

    ⚠ *Until 2026-08-27 the training run supplied a `_Report` asserting
    `PROCEED_WITH_FLAGS` without checking anything.* **FE-10 says D-02 builds no
    panel until D-07's check clears the window**, and a ten-year window over 500
    names is precisely where an unhandled corporate action hides.

    ★ Uses D-07's `check_window`, the same call the daily run makes — one gate,
    one handling (FE-4).

    ⚠ **`max_age_days` is generous here on purpose.** The daily gate wants a
    fresh store; a ten-year training sweep is refreshed deliberately, not on a
    cadence, and demanding day-old data would make every fit refuse until
    somebody re-swept.
    """
    from src.data_engine.calendar.gate import check_window

    return check_window(
        store=store, universe=universe, start=start, end=as_of, as_of=as_of,
        adj_as_of=as_of, run_id=run_id, max_age_days=365 * 20)
