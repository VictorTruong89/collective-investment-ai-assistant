"""D-04 §11 — the LightGBM family. `gbdt.lightgbm_rank.v1`, MT-26, MT-37.

★ **MT-37**: tree ensembles still outperform deep learning on typical tabular
data, and **this data has far lower SNR than those benchmarks** — so the neural
branch stays in D-10 until it beats the GBDTs *at 1m* on D-03's protocol.

⚠ **Determinism is not LightGBM's default.** `deterministic`, `force_row_wise`
and single-threading are required, or repeated fits differ in the low bits —
and **INV-2 is a property of the whole invocation** (D-08 OR-10), not an
aspiration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.models.zoo.family import Family

FORMULA_ID = "gbdt.lightgbm_rank.v1"
FAMILY_ID = "lightgbm_gbdt"

#: The one family retained today, with its reason (MT-36).
LIGHTGBM = Family(
    family_id=FAMILY_ID, formula_id=FORMULA_ID,
    retained_because=("MT-37: tree ensembles outperform deep learning on "
                      "tabular data at this SNR, and D-03's protocol has not "
                      "yet been run against any alternative"),
    library="lightgbm")

#: ⚠ **ADMITTED GUESSES** (CN-10) — sensible small-data defaults, **not tuned**.
#: Tuning is D-03's protocol (§7.3), and a hyperparameter chosen here without a
#: fold structure behind it is the D-18(c) shape: a value nothing reviewed.
DEFAULTS = {
    "objective": "regression",
    "n_estimators": 300,
    "learning_rate": 0.03,
    "num_leaves": 15,
    "min_child_samples": 50,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.8,
    "reg_lambda": 1.0,
    "verbose": -1,
}

#: ★ What makes a fit reproducible. Without these, INV-2 fails silently.
DETERMINISM = {"deterministic": True, "force_row_wise": True, "num_threads": 1,
               "seed": 42, "bagging_seed": 42, "feature_fraction_seed": 42}


@dataclass
class LightGBMRanker:
    """The estimator D-04's `fit()` injects. ★ `fit`/`predict`, nothing else.

    ⚠ It deliberately exposes **no feature selection**: choosing columns is the
    parity gate's business (MT-6), and an estimator that can narrow its own
    inputs is `_select_features` reappearing inside the zoo.
    """

    params: dict = field(default_factory=dict)
    seed: int = 42
    _model: object = field(default=None, init=False, repr=False)
    feature_names_: tuple = field(default=(), init=False)

    def resolved_params(self) -> dict:
        merged = {**DEFAULTS, **DETERMINISM, **self.params}
        merged.update({"seed": self.seed, "bagging_seed": self.seed,
                       "feature_fraction_seed": self.seed,
                       "random_state": self.seed})
        return merged

    def fit(self, x, y):
        import lightgbm as lgb

        self.feature_names_ = tuple(x.columns)
        self._model = lgb.LGBMRegressor(**self.resolved_params())
        self._model.fit(x, y)
        return self

    def predict(self, x):
        from src.models.errors import ModelError

        if self._model is None:
            raise ModelError(
                "the estimator has not been fitted. ⚠ There is no 'predict on "
                "an unfitted model' path — an untrained model scoring is D-18's "
                "default-substituted defect wearing another hat")
        if tuple(x.columns) != self.feature_names_:
            raise ModelError(
                f"the scoring frame's columns differ from the fitted ones. "
                f"★ The estimator does not reorder or narrow — that is the "
                f"parity gate's job, and an estimator that fixes it up quietly "
                f"is `_select_features` reappearing (MT-6, D-17)")
        return self._model.predict(x)

    def framework(self) -> dict:
        import lightgbm

        return {"name": "lightgbm", "version": lightgbm.__version__}
