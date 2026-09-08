"""D-04 §7 — one fit, one artifact, fully recorded. MT-12…MT-16, MT-30.

⚠ **D-18, four failures with one signature — *a failure indistinguishable from
a result*.** Optimiser workers fell back to 14 features while folds were fitted
on 16–61; **every candidate raised**; `best_sharpe` stayed `-inf`; **the
untouched defaults were adopted and `phase3b` reported PASS.** Production ran
`{rank 0.65, prob 0.35, return 0.0}` while all 8 folds chose
`rank 0.50–0.60, prob 0.10–0.20` — *the classifier got zero weight where every
fold gave it non-zero.*
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.models.artifact.manifest import (
    SELECTION,
    FeatureContractRef,
    ModelArtifact,
    ModelManifest,
)
from src.models.errors import DefaultSubstitutedError

#: MT-30 — ★ **the selection leg is fitted at 1m.** *No production ranker is
#: fitted against `fwd_ret_1w`* — and §12 records that every currently deployed
#: model is, which is why a retrain is required before 1m ships.
SELECTION_HORIZON_DAYS = 21


@dataclass(frozen=True, slots=True)
class TrainSpec:
    """What a fit is pinned to. ★ Every field ends up in the manifest."""

    contract_name: str
    contract_version: int
    label_def_id: str
    decision_anchor: str
    horizon_id: str
    horizon_days: int
    role: str = SELECTION
    horizon_set_name: str = "production"
    horizon_set_version: int = 1
    protocol: dict = None
    seeds: dict = None
    framework: dict = None
    code_version: str = ""
    #: ★ FE-2's mechanical check, carried onto the manifest. ⚠ Empty means
    #: *unverifiable*, never *matching*.
    contract_hash: str = ""

    def __post_init__(self) -> None:
        from src.models.errors import HorizonRoleError

        if self.role == SELECTION and self.horizon_days != SELECTION_HORIZON_DAYS:
            raise HorizonRoleError(
                f"a SELECTION model must be fitted at {SELECTION_HORIZON_DAYS}d "
                f"(HorizonSet v1's 1m leg), not {self.horizon_days}d. ⚠ Every "
                f"currently deployed model is fitted against fwd_ret_1w and is "
                f"therefore fitted to a TIMING objective while being used for "
                f"SELECTION (MT-30, §12)")


def fit(spec: TrainSpec, *, panel: pd.DataFrame, labels: pd.DataFrame,
        estimator, feature_names, adj_as_of: date, as_of: date):
    """MT-12…MT-16 — ★ **if the fit fails, NO ARTIFACT IS PRODUCED.**

    `estimator` is injected: D-04 owns the protocol, the zoo owns the family
    (MT-35), and a test can fit a two-line stand-in without a GBDT.
    """
    from src.feature_engineer.contracts.labels import (
        assert_no_lookahead,
        assert_single_anchor,
    )

    features = tuple(feature_names)
    if not features:
        # ★ MT-9 — the empty-metadata branch is the one §6.1 scored an
        #   arbitrary frame on. There is no such branch here.
        raise DefaultSubstitutedError(
            "fit", "no feature names supplied. There is no 'score on what's "
                   "there' path and no MODEL_FEATURES default")

    anchor = assert_single_anchor(labels)
    if anchor != spec.decision_anchor:
        from src.models.errors import AnchorMismatchError

        raise AnchorMismatchError(spec.decision_anchor, anchor)
    # ⚠ INV-1 — checked by COMPARISON against `available_at` (FE-12), not by
    #   re-deriving a date at this call site.
    assert_no_lookahead(labels, as_of=as_of)

    frame = panel.merge(labels[["ticker", "date", "value"]],
                        on=["ticker", "date"], how="inner")
    if frame.empty:
        raise DefaultSubstitutedError(
            "fit", "no rows survived the panel/label join. An empty training "
                   "set does not yield an untrained artifact")

    missing = [c for c in features if c not in frame.columns]
    if missing:
        raise DefaultSubstitutedError(
            "fit", f"the panel lacks {missing!r}. A fit never narrows to what "
                   f"is present — that is D-17's filter, one domain earlier")

    x = frame[list(features)]
    y = frame["value"]
    estimator.fit(x, y)
    _assert_fitted_not_defaulted(estimator, rows=len(frame))

    manifest = ModelManifest(
        role=spec.role, horizon_set_name=spec.horizon_set_name,
        horizon_set_version=spec.horizon_set_version, horizon_id=spec.horizon_id,
        feature_contract=FeatureContractRef(spec.contract_name,
                                            spec.contract_version,
                                            spec.contract_hash),
        label_def_id=spec.label_def_id, decision_anchor=spec.decision_anchor,
        training_start=frame["date"].min(), training_end=frame["date"].max(),
        # ★ AB-4 — the population, recorded so inference can check it.
        training_names=int(frame["ticker"].nunique()),
        training_as_of=as_of, adj_as_of=adj_as_of,
        protocol=dict(spec.protocol or {}), framework=dict(spec.framework or {}),
        seeds=dict(spec.seeds or {}), code_version=spec.code_version)
    return ModelArtifact(manifest=manifest, estimator=estimator,
                         feature_names=features)


def _assert_fitted_not_defaulted(estimator, *, rows: int) -> None:
    """MT-13 — ★ *`-inf`, `NaN`, or an empty candidate set is a failure, never a
    selection.*"""
    for name in ("best_score_", "score_", "best_sharpe"):
        value = getattr(estimator, name, None)
        if value is None:
            continue
        if isinstance(value, (int, float)) and not math.isfinite(value):
            raise DefaultSubstitutedError(
                type(estimator).__name__,
                f"{name}={value!r} after {rows} rows. ⚠ This is D-18(b) "
                f"exactly: every candidate failed, the score stayed -inf, and "
                f"the untouched defaults were adopted while the phase "
                f"reported PASS")


def select_best(candidates) -> tuple:
    """MT-13/MT-14 — ★ a winner chosen from a thinned field is **biased even
    when the winner is real**, so the count travels with it."""
    scored = [(name, score) for name, score in candidates
              if isinstance(score, (int, float)) and math.isfinite(score)]
    if not scored:
        raise DefaultSubstitutedError(
            "select_best",
            f"no finite candidate among {len(list(candidates))}. An empty "
            f"candidate set is a failure, never a selection")
    best = max(scored, key=lambda kv: kv[1])
    attempted = len(list(candidates))
    return best[0], best[1], {"attempted": attempted, "finite": len(scored),
                              "thinned": attempted - len(scored)}
