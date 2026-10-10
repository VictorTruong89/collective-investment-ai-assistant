"""D-04 — the training run. ★ `fit()` had never been called in production."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from src.models.train import run


def test_the_selection_horizon_is_one_month():
    """⚠ MT-30 — *every currently deployed model is fitted against `fwd_ret_1w`
    and is therefore fitted to a TIMING objective while being used for
    SELECTION.* `TrainSpec` refuses any other horizon for this role."""
    from src.models.errors import HorizonRoleError
    from src.models.train.fit import TrainSpec

    assert run.SELECTION_HORIZON_DAYS == 21
    with pytest.raises(HorizonRoleError):
        TrainSpec(contract_name="c", contract_version=1, label_def_id="l",
                  decision_anchor="open", horizon_id="h1w", horizon_days=5)


def test_the_universe_is_the_whole_index_not_a_selection():
    """★ QQ-11's caveat — *by added breadth, not count*. Taking the index whole
    is a **declaration**, which is what keeps it from being cherry-picking. ⚠ It
    does not answer QQ-11: 500 correlated names are not 500 bets (QA-43)."""
    universe = run.load_sp500()
    assert len(universe) > run.BREADTH_FOR_1Q
    assert universe == tuple(sorted(universe)), "declared order, not curated"


def test_survivorship_is_recorded_on_every_run():
    """★★ **INV-017**, and it cannot be corrected from these sources. ⚠ D-07
    §5A.5: *the universe is live-listed names only; nothing currently accounts
    for what left*, and **DE-35 makes index membership UNCHECKED permanently**.
    A measured IC is an UPPER BOUND, and the artifact must say so."""
    inputs = run.TrainingInputs(universe=("A",), as_of=date(2026, 8, 26),
                                start=date(2016, 8, 26))
    assert "INV-017" in inputs.survivorship
    assert "UPPER BOUND" in inputs.survivorship
    assert "survivorship" in run.summarise(
        inputs, pd.DataFrame({"ticker": [], "date": []}), pd.DataFrame())


def test_an_unresolved_name_is_named_never_dropped_silently():
    """DE-13 — ⚠ *a missing name is not dropped and does not become a row of
    NaNs.* A training set that quietly lost 40 names has a different
    cross-section from the one its manifest claims."""
    class _Client:
        pass

    def _boom(client, ticker, start, end):
        raise RuntimeError("no data")

    import src.data_engine.src.fmp.prices as prices_module

    original = prices_module.raw_prices
    prices_module.raw_prices = _boom
    try:
        frames, unresolved = run.fetch_prices(
            _Client(), ("AAA", "BBB"), start=date(2024, 1, 1), end=date(2024, 2, 1))
    finally:
        prices_module.raw_prices = original
    assert frames == {} and set(unresolved) == {"AAA", "BBB"}


# --------------------------------------------------------------------------- #
# ★★ FE-37 made visible
# --------------------------------------------------------------------------- #

def test_feature_coverage_names_the_all_null_columns():
    """★★ ⚠ **A column that is 100 % null is not a feature; it is a promise.**
    LightGBM accepts it without complaint and the manifest still claims it, so
    the declared input count and the effective one diverge silently."""
    panel = pd.DataFrame({"a": [1.0, 2.0], "b": [np.nan, np.nan],
                          "c": [1.0, np.nan]})
    coverage = run.feature_coverage(panel, ("a", "b", "c"))
    assert coverage["all_null"] == ["b"]
    assert coverage["declared"] == 3 and coverage["effective"] == 2


# --------------------------------------------------------------------------- #
# ★★★ In-sample is not a result
# --------------------------------------------------------------------------- #

def _panel_and_labels(days=120, names=("A", "B", "C", "D")):
    rows, labels = [], []
    rng = np.random.default_rng(7)
    for i in range(days):
        day = pd.Timestamp(date(2025, 1, 1)) + pd.Timedelta(days=i)
        for t in names:
            x = float(rng.normal())
            rows.append({"ticker": t, "date": day, "feat": x})
            labels.append({"ticker": t, "date": day, "value": float(rng.normal())})
    return pd.DataFrame(rows), pd.DataFrame(labels)


def test_rank_ic_is_computed_per_date_then_averaged():
    """★★ ⚠ A pooled correlation over every `(ticker, date)` row measures *"do
    high scores go with high returns anywhere in the sample"* — which a common
    market factor satisfies without the model ranking anything within a day."""
    panel, labels = _panel_and_labels()

    class _Artifact:
        class estimator:
            @staticmethod
            def predict(x):
                return x["feat"].to_numpy()

    measured = run.rank_ic(_Artifact(), panel, labels, feature_names=("feat",))
    assert measured["dates"] > 100
    # ★ Random features against random labels: an IC indistinguishable from zero.
    assert abs(measured["mean_ic"]) < 0.2


def test_rank_ic_drops_on_the_label_not_on_every_feature():
    """⚠ Requiring all 59 features non-null removes **every row** —
    `f_market_to_book` needs a market cap and the five `*_sector_z` need a
    sector. ★ That is FE-37 arriving as an empty measurement rather than a
    warning."""
    panel, labels = _panel_and_labels(days=30)
    panel["always_null"] = np.nan

    class _Artifact:
        class estimator:
            @staticmethod
            def predict(x):
                return x["feat"].to_numpy()

    measured = run.rank_ic(_Artifact(), panel, labels,
                           feature_names=("feat", "always_null"))
    assert measured["dates"] > 0, "an all-null column must not empty the measure"


def test_the_walk_forward_purge_uses_the_longest_horizon():
    """★★ QA-18 — ⚠ *not the horizon being evaluated: the **longest** one.* A
    fold purged for 21 days while a 63-day label is in the set leaks 42 days of
    overlap into every boundary."""
    from src.quant.backtest.protocol import derive_protocol
    from src.quant.horizons.horizon_set import PRODUCTION_V1

    protocol = derive_protocol(PRODUCTION_V1, n_folds=5)
    longest = max(h.trading_days for h in PRODUCTION_V1.horizons)
    assert protocol.purge_days == longest


@pytest.fixture(autouse=True)
def _no_retry_pause(monkeypatch):
    """DE-80's retry pause is real in production; these tests fail fetches on purpose."""
    monkeypatch.setattr("src.data_engine.universe.prices.RETRY_PAUSE_SECONDS", 0.0)
    monkeypatch.setattr("src.models.train.run.PRICE_RETRY_PAUSE_SECONDS", 0.0)
