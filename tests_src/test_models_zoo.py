"""D-04 §11 — the model zoo, and the whole chain end to end. MT-26, MT-35…MT-37.

★★ **This file's last test is the first time every domain runs together**:
D-02 builds the panel and the labels, D-04 fits and scores, **D-03 evaluates**,
and D-04 promotes only on D-03's verdict. Until D-03's protocol existed,
`promote()` was correct and unreachable.

Tier: unit + integration (constitution §4).
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
import pytest

from src.feature_engineer.contracts.labels import LabelDef, build_labels
from src.models import (
    ModelError, Registry, REQUIRED_GATES, TrainSpec, check_parity, fit, promote,
    score,
)
from src.models.zoo.family import Family, Zoo
from src.models.zoo.gbdt import DETERMINISM, FORMULA_ID, LIGHTGBM, LightGBMRanker
from src.quant import BacktestSpec, derive_protocol, evaluate
from src.quant.horizons.horizon_set import PRODUCTION_V1

LABEL = LabelDef("fwd_return_21d_open", 21, "open")
AS_OF, ADJ = date(2026, 12, 31), date(2026, 6, 30)


class _Contract:
    name, version = "zoo_demo", 1
    feature_names = ["f_mom", "f_vol"]


def synthetic(*, names: int = 40, dates: int = 300, signal: float = 0.0006,
              seed: int = 7) -> pd.DataFrame:
    """A panel with a **known** latent: `f_mom` carries it, `f_vol` does not."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2024-01-01", periods=dates)
    rows = []
    for i in range(names):
        drift, price = rng.normal(0, 0.4), 10_000.0
        for day in days:
            price *= 1 + (signal * drift + rng.normal(0, 0.012))
            rows.append({"ticker": f"T{i}", "date": day,
                         "adj_open_minor": price,
                         "f_mom": drift + rng.normal(0, 0.25),
                         "f_vol": abs(rng.normal(1, 0.2))})
    return pd.DataFrame(rows)


def train(panel=None, estimator=None):
    panel = synthetic() if panel is None else panel
    labels = build_labels(label_def=LABEL, price_panel=panel)
    spec = TrainSpec(
        contract_name="zoo_demo", contract_version=1,
        label_def_id=LABEL.label_def_id, decision_anchor="open",
        horizon_id="h1m", horizon_days=21,
        protocol=derive_protocol(PRODUCTION_V1).to_json_obj(),
        seeds={"lgbm": 42}, framework=LightGBMRanker().framework(),
        code_version="git:test")
    return fit(spec, panel=panel, labels=labels,
               estimator=estimator or LightGBMRanker(),
               feature_names=("f_mom", "f_vol"), adj_as_of=ADJ, as_of=AS_OF), panel


# --------------------------------------------------------------------------- #
# MT-35 / MT-36 — zoo governance
# --------------------------------------------------------------------------- #

def test_mt35_a_family_with_no_method_entry_cannot_be_registered():
    """MT-35 — ★ *a family with no MethodEntry cannot be promoted*, and the
    check is a filesystem scan, so it costs nothing and cannot be argued with."""
    Zoo().register(LIGHTGBM)                    # the real one has an entry
    with pytest.raises(ModelError, match="no MethodEntry"):
        Zoo().register(Family(family_id="ghost", formula_id="not.a.formula.v1",
                              retained_because="testing", library="none"))


def test_mt36_retention_needs_a_stated_reason():
    """MT-36 — ★ **retirement is the DEFAULT.** ⚠ *An unretained family is
    maintenance surface, not optionality* — the legacy tree carries **nine
    families, 2,736 LOC across 18 files, for one production horizon.**"""
    with pytest.raises(ModelError, match="retirement is the DEFAULT"):
        Family(family_id="x", formula_id=FORMULA_ID, retained_because="  ",
               library="lightgbm")
    assert "MT-37" in LIGHTGBM.retained_because


def test_mt37_only_one_family_is_retained_today():
    """MT-37 — ★ the neural branch stays in D-10 *until it beats the GBDTs at
    1m on D-03's protocol*, and that comparison has not been run."""
    zoo = Zoo()
    zoo.register(LIGHTGBM)
    assert len(zoo.to_json_obj()["families"]) == 1


# --------------------------------------------------------------------------- #
# MT-26 — determinism, which LightGBM does not give by default
# --------------------------------------------------------------------------- #

def test_two_fits_with_the_same_seed_are_identical():
    """★★ MT-26 / INV-2 — ⚠ **determinism is not the default.**

    `deterministic`, `force_row_wise` and single-threading are required, or
    repeated fits differ in the low bits — and INV-2 is a property of **the
    whole invocation** (D-08 OR-10), not an aspiration.
    """
    assert DETERMINISM["deterministic"] is True
    assert DETERMINISM["num_threads"] == 1
    panel = synthetic(names=15, dates=120)
    one, _ = train(panel)
    two, _ = train(panel)
    assert one.artifact_id == two.artifact_id
    frame = panel[["f_mom", "f_vol"]].head(50)
    assert np.array_equal(one.estimator.predict(frame),
                          two.estimator.predict(frame))


def test_the_family_recovers_a_monotone_signal():
    """The known-answer test for `gbdt.lightgbm_rank.v1`."""
    frame = pd.DataFrame({"f_mom": np.linspace(-3, 3, 300),
                          "f_vol": np.ones(300)})
    model = LightGBMRanker().fit(frame, frame["f_mom"] * 2.0)
    predicted = model.predict(frame)
    assert pd.Series(predicted).corr(frame["f_mom"], method="spearman") > 0.99


def test_the_estimator_refuses_to_reorder_or_narrow_its_inputs():
    """★ MT-6 — *an estimator that fixes it up quietly is `_select_features`
    reappearing.* Choosing columns is the parity gate's business."""
    model, panel = train()
    with pytest.raises(ModelError, match="parity gate's job"):
        model.estimator.predict(panel[["f_vol", "f_mom"]].head(5))
    with pytest.raises(ModelError, match="not been fitted"):
        LightGBMRanker().predict(panel[["f_mom", "f_vol"]].head(5))


# --------------------------------------------------------------------------- #
# ★★ The chain — D-02 → D-04 → D-03 → D-04
# --------------------------------------------------------------------------- #

def test_the_required_gate_set_has_exactly_one_owner():
    """★★ **Found by running the chain end to end.**

    ⚠ D-04 had enumerated its own gate list including a `stability` gate **D-03
    never produces**, so promotion refused every artifact. Neither spec
    enumerated the set. ★ **MT-19 puts the gates in D-03**, so D-04 imports
    them — and MT-18 is what caught the disagreement.
    """
    from src.models.governance import promotion
    from src.quant.gates import metric_gate

    assert promotion.REQUIRED_GATES is metric_gate.REQUIRED_GATES
    assert REQUIRED_GATES == ("ic_significance", "cost_survival", "breadth")


def test_the_whole_chain_runs_and_promotion_rests_on_d03s_verdict():
    """★★ **Every domain, once.** D-02 builds the panel and labels, D-04 fits
    and scores through the parity gate, **D-03 evaluates**, and D-04 promotes
    only on D-03's outcomes (MT-17, MT-19).

    ⚠ Until D-03's protocol existed, `promote()` was **correct and
    unreachable** — it demanded a `BacktestResult` nothing could produce.
    """
    artifact, panel = train()
    labels = build_labels(label_def=LABEL, price_panel=panel)

    parity = check_parity(artifact, panel, contract=_Contract(),
                          run_anchor="open", raise_on_halt=False)
    assert parity.verdict == "PASS" and not parity.nan_only

    result = score(artifact, panel, contract=_Contract(), as_of=AS_OF,
                   adj_as_of=ADJ, run_anchor="open", panel_id="p1")
    assert len(result.ranked()) == 40

    merged = panel.merge(labels[["ticker", "date", "value"]],
                         on=["ticker", "date"])
    merged["score"] = artifact.estimator.predict(merged[["f_mom", "f_vol"]])
    merged["horizon_days"] = 21
    backtest = evaluate(
        BacktestSpec(universe=tuple(f"T{i}" for i in range(40)),
                     start=date(2024, 1, 1), end=ADJ,
                     horizon_set_name="production", horizon_set_version=1,
                     initial_capital=100_000.0, contract_version=1,
                     calendar_check_id="cal:1", as_of=AS_OF, adj_as_of=ADJ,
                     decision_anchor="open", survivorship_handled=True),
        predictions=merged,
        horizons=[h for h in PRODUCTION_V1.horizons if h.trading_days == 21],
        effective_breadth=5.0, gross_return=0.14, net_return=0.11)

    gate = backtest.gate_sets[0].gates[0]
    assert gate.verdict == "PASS" and gate.t_stat > 3.0
    assert gate.effective_n < 20, "N_eff is T/h, not T"

    record = promote(artifact, backtest_result_id=backtest.result_id,
                     gate_outcomes=backtest.gate_outcomes(),
                     promoted_by="victor", at=datetime.now(timezone.utc))
    registry = Registry()
    registry.install(artifact, record)
    assert registry.production_artifact("selection", "h1m") is artifact
    assert record.backtest_result_id.startswith("bt:")


def test_a_model_with_no_signal_does_not_reach_production():
    """★ The chain must be able to say **no**, or it is decoration (QA-17's
    precedent, D-18)."""
    from src.models import NotEvaluatedError

    panel = synthetic(signal=0.0, seed=11)
    artifact, _ = train(panel)
    labels = build_labels(label_def=LABEL, price_panel=panel)
    merged = panel.merge(labels[["ticker", "date", "value"]],
                         on=["ticker", "date"])
    merged["score"] = artifact.estimator.predict(merged[["f_mom", "f_vol"]])
    merged["horizon_days"] = 21
    backtest = evaluate(
        BacktestSpec(universe=("T0",), start=date(2024, 1, 1), end=ADJ,
                     horizon_set_name="production", horizon_set_version=1,
                     initial_capital=100_000.0, contract_version=1,
                     calendar_check_id="cal:1", as_of=AS_OF, adj_as_of=ADJ,
                     decision_anchor="open", survivorship_handled=True),
        predictions=merged,
        horizons=[h for h in PRODUCTION_V1.horizons if h.trading_days == 21],
        effective_breadth=5.0, gross_return=0.02, net_return=-0.01)
    assert backtest.verdict == "FAIL"
    with pytest.raises(NotEvaluatedError):
        promote(artifact, backtest_result_id=backtest.result_id,
                gate_outcomes=backtest.gate_outcomes(), promoted_by="victor",
                at=datetime.now(timezone.utc))
