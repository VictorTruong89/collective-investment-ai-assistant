"""D-04 — model training and inference. MT-1…MT-49, CT-4.1…CT-4.4.

★ This domain exists to close two incidents, and every test here points at one:

- **D-17** — a model fitted on 61 features scored on 14, and the `f_*` left-join
  kept unmatched names with **all 47 fundamental columns present and entirely
  NaN**. The columns exist, the filter passes, the GBDTs consume the NaNs
  natively and return an ordinary-looking score. **7 of 13 watchlist names.**
- **D-18** — *a failure indistinguishable from a result*: every candidate
  raised, `best_sharpe` stayed `-inf`, **the untouched defaults were adopted and
  the phase reported PASS.**

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pandas as pd
import pytest

from src.feature_engineer.contracts.labels import (
    FWD_RETURN_5D_OPEN, FWD_RETURN_21D_OPEN, LabelDef, assert_no_lookahead,
    assert_single_anchor, build_labels,
)
from src.models import (
    AnchorMismatchError, DefaultSubstitutedError, HorizonRoleError,
    MIN_FEATURE_COVERAGE, ModelManifest, NOT_EVALUATED, NotEvaluatedError,
    ParityError, REQUIRED_GATES, Registry, RESEARCH_HORIZON, SELECTION, TIMING,
    TrainSpec, arbitrate, check_parity, drift, fit, promote, score, select_best,
)

AS_OF = date(2026, 6, 30)
TICKERS = ("NVDA", "MU", "AMD")


class _Estimator:
    """A two-line stand-in — ★ MT-35's families live in the zoo; the protocol
    is D-04's, and a test must be able to exercise it without a GBDT."""

    def __init__(self, weight: float = 1.0):
        self.weight = weight
        self.columns_seen = None

    def fit(self, x, y):
        self.columns_seen = tuple(x.columns)
        return self

    def predict(self, x):
        return (x.iloc[:, 0] * self.weight).to_numpy()


class _Contract:
    def __init__(self, name="all_features", version=3, features=("f_a", "f_b")):
        self.name, self.version = name, version
        self.feature_names = list(features)


def panel(nan_column: str | None = None, extra: str | None = None):
    days = pd.bdate_range("2026-01-01", periods=40)
    rows = []
    for i, ticker in enumerate(TICKERS):
        rows.append(pd.DataFrame({
            "ticker": ticker, "date": days,
            "f_a": [1.0 + i + j * 0.01 for j in range(len(days))],
            "f_b": [2.0 + i - j * 0.01 for j in range(len(days))],
            "adj_open_minor": [10000 + j * 50 for j in range(len(days))],
        }))
    frame = pd.concat(rows, ignore_index=True)
    if nan_column:
        frame[nan_column] = float("nan")
    if extra:
        frame[extra] = 1.0
    return frame


def labels(label_def=FWD_RETURN_21D_OPEN):
    return build_labels(label_def=label_def, price_panel=panel())


def spec(**kw):
    base = dict(contract_name="all_features", contract_version=3,
                label_def_id=FWD_RETURN_21D_OPEN.label_def_id,
                decision_anchor="open", horizon_id="h1m", horizon_days=21,
                protocol={"purge_days": 63}, seeds={"numpy": 42},
                framework={"name": "stub", "version": "0"}, code_version="git:test")
    return TrainSpec(**{**base, **kw})


def artifact(**kw):
    return fit(spec(**kw.pop("spec_kw", {})), panel=panel(), labels=labels(),
               estimator=_Estimator(), feature_names=("f_a", "f_b"),
               adj_as_of=AS_OF, as_of=AS_OF, **kw)


# --------------------------------------------------------------------------- #
# §5 — the artifact. MT-1…MT-4, MT-41
# --------------------------------------------------------------------------- #

def test_mt1_the_manifest_carries_a_contract_NAME_AND_VERSION_not_a_column_list():
    """MT-1 — ★ *a name list can be satisfied by coincidence; a version cannot.*

    ⚠ *Today `model_manager.py:91` stores `feature_names` as a list of strings
    and nothing else — **the whole D-17 class follows from that one choice**.*

    ★★ **And a content hash, from 2026-08-27.** ⚠ A version cannot be satisfied
    by coincidence, but it *can* be left unchanged: two artifacts with **59** and
    **61** features both declared `price_and_fundamental@v1` after Group C
    landed, and `check_parity` compares name and version — so it waved the
    difference through. FE-2's own mechanism existed; the manifest did not carry
    it.
    """
    manifest = artifact().manifest
    assert manifest.feature_contract.to_json_obj() == {
        "name": "all_features", "version": 3, "content_hash": ""}
    assert "feature_names" not in manifest.to_json_obj()


def test_mt3_artifacts_are_immutable_and_content_addressed():
    """MT-3 — ★ retraining produces a **new** `artifact_id`; nothing updates."""
    one, two = artifact(), artifact()
    assert one.artifact_id == two.artifact_id           # same inputs, same id
    assert one.artifact_id.startswith("sha256:")
    different = fit(spec(), panel=panel(), labels=labels(),
                    estimator=_Estimator(), feature_names=("f_a", "f_b"),
                    adj_as_of=date(2026, 5, 31), as_of=AS_OF)
    assert different.artifact_id != one.artifact_id


def test_mt4_the_adjustment_state_is_part_of_the_model_identity():
    """MT-4 — ★ *two artifacts trained on "the same window" at different
    adjustment states are **different models**.* ⚠ Without it, a future split
    silently changes the training data."""
    assert "adj_as_of" in artifact().manifest.to_json_obj()


def test_mt41_a_manifest_with_no_decision_anchor_cannot_exist():
    """MT-41 — ★ a model **records the anchor it was fitted on.**"""
    from src.models import FeatureContractRef, ModelError

    with pytest.raises(ModelError, match="decision_anchor"):
        ModelManifest(role=SELECTION, horizon_set_name="production",
                      horizon_set_version=1, horizon_id="h1m",
                      feature_contract=FeatureContractRef("all_features", 3),
                      label_def_id="x", decision_anchor="",
                      training_start=AS_OF, training_end=AS_OF,
                      training_as_of=AS_OF, adj_as_of=AS_OF, protocol={},
                      framework={}, seeds={}, code_version="")


# --------------------------------------------------------------------------- #
# §6 — parity. ★★ the gate that closes D-17
# --------------------------------------------------------------------------- #

def test_mt7_present_but_entirely_nan_halts_the_run():
    """★★ **MT-7 / D-17 — the half a column-name check is structurally blind
    to.**

    ⚠ The `f_*` merge is `how="left"`, so an unmatched name **keeps its row with
    all 47 fundamental columns present and entirely NaN.** The columns exist.
    The filter passes. The GBDTs consume the NaNs natively and return an
    ordinary-looking score. **Measured 2026-08-10: 7 of 13 watchlist names.**
    """
    with pytest.raises(ParityError, match="entirely NaN"):
        check_parity(artifact(), panel(nan_column="f_b"), contract=_Contract(),
                     run_anchor="open")
    report = check_parity(artifact(), panel(nan_column="f_b"),
                          contract=_Contract(), run_anchor="open",
                          raise_on_halt=False)
    assert report.nan_only == ("f_b",)          # ★ a first-class field (CT-4.2)
    assert report.verdict == "HALT"


def test_mt6_parity_is_version_equality_not_subset_or_intersection():
    """MT-6 — ★ `artifact.contract_version == panel.contract_version`, **or the
    run halts.**"""
    with pytest.raises(ParityError, match="!="):
        check_parity(artifact(), panel(), contract=_Contract(version=4),
                     run_anchor="open")


def test_a_missing_feature_halts_rather_than_narrowing():
    """MT-9 — ★ *there is no fallback feature set.* ⚠ `_select_features`
    filtered here; **filtering always succeeds, so it cannot warn.**"""
    thin = panel().drop(columns=["f_b"])
    with pytest.raises(ParityError, match="missing"):
        check_parity(artifact(), thin, contract=_Contract(), run_anchor="open")


def test_mt10_extra_features_warn_and_escalate_when_the_contract_differs():
    """MT-10 — ★ parity is checked **both ways**; an extra column means the
    panel came from a different contract."""
    report = check_parity(artifact(), panel(extra="f_zzz"), contract=_Contract(),
                          run_anchor="open", raise_on_halt=False)
    assert report.extra == ("f_zzz",) and report.verdict == "PASS"
    with pytest.raises(ParityError):
        check_parity(artifact(), panel(extra="f_zzz"),
                     contract=_Contract(version=9), run_anchor="open")


def test_mt42_an_anchor_mismatch_is_a_hard_gate_not_a_warning():
    """★★ MT-42 — ⚠ *silent, systematic, and invisible in every metric the
    system computes* — the backtest shares the training anchor, so it cannot see
    the drift it inherits."""
    with pytest.raises(AnchorMismatchError, match="must be RETRAINED"):
        check_parity(artifact(), panel(), contract=_Contract(),
                     run_anchor="close")


def test_mt11_a_ranking_with_no_eligible_pick_does_not_pick_one_anyway():
    """MT-11 — ★ a below-coverage name **stays in the ranking** and cannot be
    the actionable pick; if *every* curated name is excluded, the run raises."""
    from src.models import assert_some_name_is_actionable

    report = check_parity(artifact(), panel(), contract=_Contract(),
                          run_anchor="open", raise_on_halt=False)
    assert assert_some_name_is_actionable(report, TICKERS) == tuple(sorted(TICKERS))

    starved = check_parity(artifact(), panel(), contract=_Contract(),
                           run_anchor="open", raise_on_halt=False)
    object.__setattr__(starved, "coverage_by_ticker",
                       {t: {"coverage_fraction": 0.1} for t in TICKERS})
    with pytest.raises(ParityError, match="does not pick one"):
        assert_some_name_is_actionable(starved, TICKERS)


# --------------------------------------------------------------------------- #
# §7 — the fit and the promotion gate. ★★ D-18
# --------------------------------------------------------------------------- #

def test_mt12_a_fit_with_no_feature_names_produces_no_artifact():
    """MT-9/MT-12 — ⚠ *the empty-`feature_names` branch scored on **every
    remaining column***. There is no such branch."""
    with pytest.raises(DefaultSubstitutedError, match="MODEL_FEATURES"):
        fit(spec(), panel=panel(), labels=labels(), estimator=_Estimator(),
            feature_names=(), adj_as_of=AS_OF, as_of=AS_OF)


def test_mt13_a_non_finite_optimisation_result_raises():
    """★★ MT-13 / **D-18(b) exactly**: every candidate failed, `best_sharpe`
    stayed `-inf`, **the untouched defaults were adopted and the phase reported
    PASS.**"""
    class _Broken(_Estimator):
        best_score_ = float("-inf")

    with pytest.raises(DefaultSubstitutedError, match="D-18"):
        fit(spec(), panel=panel(), labels=labels(), estimator=_Broken(),
            feature_names=("f_a", "f_b"), adj_as_of=AS_OF, as_of=AS_OF)


def test_mt13_an_empty_candidate_set_is_a_failure_never_a_selection():
    """MT-13/MT-14 — ★ *a winner chosen from a thinned field is biased even when
    the winner is real*, so the count travels with it."""
    with pytest.raises(DefaultSubstitutedError, match="never a selection"):
        select_best([("a", float("-inf")), ("b", float("nan"))])
    name, value, counts = select_best([("a", 0.3), ("b", float("nan")), ("c", 0.5)])
    assert (name, value) == ("c", 0.5)
    assert counts == {"attempted": 3, "finite": 2, "thinned": 1}


def test_mt30_a_selection_model_must_be_fitted_at_one_month():
    """MT-30 — ⚠ *every currently deployed model is fitted against `fwd_ret_1w`*
    — a **timing** objective used for **selection**."""
    with pytest.raises(HorizonRoleError, match="TIMING objective"):
        spec(horizon_days=5, horizon_id="h1w")
    assert spec(role=TIMING, horizon_days=5, horizon_id="h1w").horizon_days == 5


def test_mt18_not_evaluated_is_not_a_pass():
    """★★ MT-18 — ⚠ absence is not consent, and treating silence as consent is
    **D-18(b)'s shape**."""
    gates = {g: "PASS" for g in REQUIRED_GATES}
    record = promote(artifact(), backtest_result_id="bt:1", gate_outcomes=gates,
                     promoted_by="victor", at=datetime.now(timezone.utc))
    assert record.backtest_result_id == "bt:1"

    for missing in (dict(gates, breadth=NOT_EVALUATED), dict(gates, breadth="FAIL")):
        with pytest.raises(NotEvaluatedError, match="breadth"):
            promote(artifact(), backtest_result_id="bt:1", gate_outcomes=missing,
                    promoted_by="victor", at=datetime.now(timezone.utc))


def test_mt19_promotion_requires_a_d03_evaluation_d04_cannot_supply():
    """MT-19 — ★ **D-04 does not evaluate itself.** The gates are D-03's, run by
    D-03's code, against D-03's protocol."""
    from src.models import ModelError

    with pytest.raises(ModelError, match="does not evaluate itself"):
        promote(artifact(), backtest_result_id="",
                gate_outcomes={g: "PASS" for g in REQUIRED_GATES},
                promoted_by="victor", at=datetime.now(timezone.utc))


def test_mt33_a_research_horizon_artifact_cannot_reach_production():
    """MT-33 — ★ enforced **at load**, not by convention."""
    research = fit(spec(role="research", horizon_id=RESEARCH_HORIZON,
                        horizon_days=21),
                   panel=panel(), labels=labels(), estimator=_Estimator(),
                   feature_names=("f_a", "f_b"), adj_as_of=AS_OF, as_of=AS_OF)
    with pytest.raises(HorizonRoleError, match="RESEARCH horizon"):
        research.assert_loadable_for_production()


def test_mt46_a_failed_retrain_leaves_the_incumbent_in_place():
    """MT-46 — ★ **never a fallback to an ungated model.**"""
    registry = Registry()
    incumbent = artifact()
    registry.install(incumbent, promote(
        incumbent, backtest_result_id="bt:1",
        gate_outcomes={g: "PASS" for g in REQUIRED_GATES},
        promoted_by="victor", at=datetime.now(timezone.utc)))
    assert registry.incumbent_survives(SELECTION, "h1m")
    with pytest.raises(NotEvaluatedError):
        promote(artifact(), backtest_result_id="bt:2",
                gate_outcomes={g: NOT_EVALUATED for g in REQUIRED_GATES},
                promoted_by="victor", at=datetime.now(timezone.utc))
    assert registry.production_artifact(SELECTION, "h1m") is incumbent


# --------------------------------------------------------------------------- #
# §9/§10 — inference and arbitration. MT-26…MT-32
# --------------------------------------------------------------------------- #

def scored(**kw):
    return score(artifact(), panel(), contract=_Contract(), as_of=AS_OF,
                 adj_as_of=AS_OF, run_anchor="open", **kw)


def test_mt26_inference_is_deterministic_and_ties_break_on_ticker():
    """MT-26 / INV-2 — ⚠ a ranking whose ties depend on dict order is not
    deterministic, however stable it looks in practice."""
    assert scored().ranked() == scored().ranked()
    assert scored().to_json_obj() == scored().to_json_obj()


def test_mt28_rank_score_carries_no_verdict():
    """MT-28 — ★ *an ordering, not a verdict* (L0 §3.1, INV-014)."""
    obj = scored().to_json_obj()
    # ⚠ `parity_verdict` is the PARITY gate's outcome, not a trading verdict —
    #   the distinction is the point, so the check is on trading vocabulary.
    blob = str({k: v for k, v in obj.items() if k != "parity_verdict"})
    for banned in ("BUY", "HOLD", "SELL", "conviction", "target", "stop"):
        assert banned not in blob, banned
    assert set(obj["ranked"][0]) == {"ticker", "rank_score"}


def test_mt29_inference_halts_on_parity_failure_and_never_degrades():
    """MT-29 — ★ *it does not degrade to a partial score.*"""
    with pytest.raises(ParityError):
        score(artifact(), panel(nan_column="f_b"), contract=_Contract(),
              as_of=AS_OF, adj_as_of=AS_OF, run_anchor="open")


def test_mt31_the_timing_leg_never_nominates():
    """★★ MT-31/MT-32 — ⚠ *"Wait" is legal; "buy a different name" is not.*

    P3's monotonicity and QA-47's arbitration are the same rule seen from two
    domains, and the structural guarantee is that **no branch takes a name from
    the timing leg.**
    """
    selection = scored()
    pick = selection.ranked()[0][0]

    timing = score(artifact(spec_kw={"role": TIMING, "horizon_id": "h1w",
                                     "horizon_days": 5,
                                     "label_def_id": FWD_RETURN_5D_OPEN.label_def_id}),
                   panel(), contract=_Contract(), as_of=AS_OF, adj_as_of=AS_OF,
                   run_anchor="open")

    assert arbitrate(selection).nominated == pick
    object.__setattr__(timing, "scores", {pick: -1.0})
    delayed = arbitrate(selection, timing)
    assert delayed.outcome == "delay" and delayed.nominated == pick

    # ⚠ It cannot substitute a name it prefers.
    object.__setattr__(timing, "scores", {"SOMEONE_ELSE": 9.9})
    with pytest.raises(HorizonRoleError, match="originating a nomination"):
        arbitrate(selection, timing)


# --------------------------------------------------------------------------- #
# §8 — drift. MT-21, MT-22
# --------------------------------------------------------------------------- #

def test_mt21_performance_drift_is_unmeasured_not_zero_before_a_horizon():
    """MT-21 — ★ *a retrain triggered on performance alone reacts a horizon
    late*, and ⚠ **unmeasured is not "no drift"**."""
    report = drift(artifact(), window_days=21)
    assert report.performance_drift["status"] == "unmeasured"
    assert "not 'no drift'" in report.performance_drift["why"]


def test_mt22_drift_reports_and_does_not_judge():
    """MT-22 — ★ the thresholds are **D-03's**; D-04 computes and reports."""
    report = drift(artifact(), window_days=21,
                   training_scores=[0.1, 0.2, 0.3], live_scores=[5.0, 5.1, 5.2])
    assert report.output_drift["status"] == "moved"
    assert report.to_json_obj()["verdict"] == "reported_not_judged"
    assert "output" in report.early_warnings


# --------------------------------------------------------------------------- #
# CT-2.3 — the label set D-04 trains on. MT-48
# --------------------------------------------------------------------------- #

def test_mt48_available_at_is_materialised_not_computed():
    """MT-48 / FE-12 — ★ *so INV-1 is checkable by **comparison** rather than by
    trusting arithmetic at every call site.*

    ⚠ It is the real trading date h sessions ahead — **not** `date +
    horizon_days`, which would land on weekends.
    """
    frame = labels()
    assert list(frame.columns) == ["ticker", "date", "horizon_days",
                                   "label_def_id", "decision_anchor", "value",
                                   "available_at"]
    gap = (frame["available_at"].iloc[0] - frame["date"].iloc[0]).days
    assert gap > 21, "21 sessions is more than 21 calendar days"
    assert_no_lookahead(frame, as_of=date(2026, 12, 31))
    with pytest.raises(Exception, match="not knowable"):
        assert_no_lookahead(frame, as_of=date(2026, 1, 15))


def test_fe31_a_label_set_declares_its_anchor_and_may_not_mix_anchors():
    """FE-31 / QA-72 — ⚠ *a label set whose anchor is not on the row cannot be
    compared with one built on a different anchor, and nothing would notice.*"""
    assert assert_single_anchor(labels()) == "open"
    mixed = pd.concat([labels(), labels().assign(decision_anchor="close")])
    with pytest.raises(Exception, match="mixes anchors"):
        assert_single_anchor(mixed)


def test_the_anchor_selects_the_price_column():
    """FE-31 — ⚠ an `open`-anchored label built from `close` is **D-08 OR-35's
    full-session drift, introduced one domain earlier** — and invisible in
    backtest, because the backtest shares it."""
    with pytest.raises(Exception, match="full session of drift"):
        build_labels(label_def=LabelDef("x", 21, "close"), price_panel=panel())
