"""D-04 — artifact persistence and promotion. ★ `fit()` returned; nothing wrote."""
from datetime import date, datetime, timezone

import pytest

from src.models.artifact.store import ArtifactStore
from src.recording.errors import AppendOnlyViolation


class _Manifest:
    role, horizon_id = "selection", "h1m"
    horizon_set_version = 1

    class feature_contract:
        version = 1

    artifact_id = "sha256:test-artifact"

    def to_json_obj(self):
        return {"role": self.role, "horizon_id": self.horizon_id,
                "artifact_id": self.artifact_id}


class _Artifact:
    manifest = _Manifest()
    estimator = {"fitted": True}
    feature_names = ("a", "b")
    artifact_id = _Manifest.artifact_id

    def assert_loadable_for_production(self):
        return None


def test_the_artifact_is_written_even_when_the_gates_refuse(tmp_path):
    """★ **A refused model is a record** — and the most useful thing to hold
    when the next one passes. ⚠ MT-17 cuts both ways."""
    store = ArtifactStore(tmp_path)
    store.write(_Artifact(), evaluation={"ic": {"mean_ic": 0.02}})
    files = store.read(_Artifact.artifact_id)
    assert set(files) == {"manifest.json", "features.json", "evaluation.json"}


def test_the_manifest_is_never_rewritten(tmp_path):
    """★ `artifact_id` is derived from the manifest's own content, so a changed
    input yields a **new id** and cannot collide. ⚠ The manifest on disk is
    therefore written once and left alone — re-running an identical fit must not
    silently re-stamp it.
    """
    import json

    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    path = store.dir_for(_Artifact.artifact_id) / "manifest.json"
    before = path.read_text(encoding="utf-8")
    stamped = path.stat().st_mtime_ns

    store.write(_Artifact())
    assert path.read_text(encoding="utf-8") == before
    assert path.stat().st_mtime_ns == stamped, "the manifest was rewritten"
    assert json.loads(before)["artifact_id"] == _Artifact.artifact_id


def test_a_fitted_artifact_is_not_a_promoted_one(tmp_path):
    """★★ **MT-17 — promotion is the only path to production.** ⚠ Treating the
    presence of a model as licence to score with it is exactly what that rule
    exists to prevent, and `promoted()` reads `promotion.json`, whose **absence
    is the refusal**."""
    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    assert store.promoted(role="selection", horizon_id="h1m") is None


def test_a_promoted_artifact_is_found(tmp_path):
    """★ The positive path, so the negative one above is not vacuous."""
    from src.models.governance.promotion import PromotionRecord

    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    store.record_promotion(PromotionRecord(
        artifact_id=_Artifact.artifact_id, promoted_at=datetime.now(timezone.utc),
        promoted_by="test", backtest_result_id="bt-1",
        gate_outcomes={"ic_significance": "PASS"},
        horizon_set_version=1, contract_version=1))
    assert store.promoted(role="selection", horizon_id="h1m") \
        == _Artifact.artifact_id


def test_a_promotion_is_recorded_once(tmp_path):
    """CT-4.3 — ★ append-only. ⚠ *A rejected-name history that can be edited is
    the most tempting record in the system to edit* (RC-31's argument, one
    domain over)."""
    from src.models.governance.promotion import PromotionRecord

    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    record = PromotionRecord(
        artifact_id=_Artifact.artifact_id, promoted_at=datetime.now(timezone.utc),
        promoted_by="test", backtest_result_id="bt-1", gate_outcomes={},
        horizon_set_version=1, contract_version=1)
    store.record_promotion(record)
    with pytest.raises(AppendOnlyViolation):
        store.record_promotion(record)


# --------------------------------------------------------------------------- #
# The decision
# --------------------------------------------------------------------------- #

class _IC:
    status, mean_ic = "measured", 0.0203
    effective_n, corrected_se = 118.6, 0.0143
    formula_id, why = "rank_ic.spearman.v1", ""

    def mde(self, t_star=3.0):
        return t_star * self.corrected_se

    def to_json_obj(self):
        return {"mean_ic": self.mean_ic, "effective_n": self.effective_n}


def test_a_failing_gate_refuses_promotion_and_still_persists(tmp_path):
    """★★ The measured case, 2026-08-27: IC **0.0203** against an MDE of
    **0.0429** at this SE ⇒ `ic_significance` FAILs, and `cost_survival` cannot
    be evaluated at all."""
    from src.models.train.run import decide_promotion

    store = ArtifactStore(tmp_path)
    outcome = decide_promotion(_Artifact(), ic_result=_IC(), names=500,
                               store=store)
    assert outcome["promoted"] is False
    assert "ic_significance" in outcome["refused_gates"]
    assert store.read(_Artifact.artifact_id).get("manifest.json")


def test_an_unrunnable_gate_is_not_evaluated_never_a_pass(tmp_path):
    """★★ QA-17 / MT-19 — ⚠ **`cost_survival` needs a BACKTEST**, and *D-04 does
    not evaluate itself*. Scoring it PASS here would be D-04 marking its own
    homework; an ABSENT key and a `NOT_EVALUATED` one look identical to
    `promote`, so the entry is present and says why."""
    from src.models.train.run import COST_GATE_UNAVAILABLE, gate_outcomes

    outcomes = gate_outcomes(_IC(), horizon_id="h1m", names=500)
    assert "cost_survival" in outcomes and outcomes["cost_survival"] is None
    assert "MT-19" in COST_GATE_UNAVAILABLE


def test_survivorship_rides_on_the_evaluation_file(tmp_path):
    """★★ INV-017 — ⚠ a *passing* gate on today's index over ten years has not
    shown the signal works. The caveat is written into the record rather than
    left in a chat log."""
    from src.models.train.run import decide_promotion

    store = ArtifactStore(tmp_path)
    decide_promotion(_Artifact(), ic_result=_IC(), names=500, store=store)
    evaluation = store.read(_Artifact.artifact_id)["evaluation.json"]
    assert "INV-017" in evaluation["survivorship"]


def test_the_required_gates_are_d03s_not_d04s():
    """MT-50 — ⚠ D-04 declaring its own list is how promotion came to demand a
    `stability` gate D-03 never produced, and **every artifact was refused**."""
    from src.models.governance import promotion
    from src.quant.gates.metric_gate import REQUIRED_GATES

    assert promotion.REQUIRED_GATES is REQUIRED_GATES


def test_ab12_the_ic_gate_uses_the_null_standard_error():
    """★★★ **AB-12 — the gate promotion turns on, pinned so the choice is
    visible.**

    ⚠ `corrected_se` is `√(h/((n−1)·T))`: the standard error **under the null of
    no skill**. QA-4 promises *"an autocorrelation-corrected standard error"* and
    this contains no autocorrelation correction at all.

    ★ Measured 2026-08-27 on 500 names × 10 years, `mean IC = 0.0203`:
    the null SE gives **t = 4.94 (PASS)**; the realised SE, from an observed
    per-date dispersion of `0.156`, gives **t = 1.42 (fail)** — a **3.5×**
    difference on the same run.

    ⚠ This test does not assert which is correct. It asserts **which one the
    gate uses**, so that a change is deliberate rather than silent.
    """
    import math

    from src.quant.metrics.ic import corrected_se

    se = corrected_se(dates=2491, names_per_date=500.0, horizon_days=21)
    assert math.isclose(se, math.sqrt(21 / (499 * 2491)), rel_tol=1e-9)
    # ★ The null SE is ~3.5x smaller than the realised one on this run.
    realised = 0.1561 / math.sqrt(2491 / 21)
    assert realised / se > 3.0


# --------------------------------------------------------------------------- #
# ★★ Re-evaluation appends — the same fit graded twice
# --------------------------------------------------------------------------- #

def test_an_identical_refit_is_a_no_op_not_an_error(tmp_path):
    """★ `artifact_id` is derived from the manifest, so the *same* fit always
    yields the same id — and re-running one is what a reproducible pipeline
    should permit. ⚠ A **changed** manifest under an existing id cannot arise: a
    changed input changes the id."""
    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    store.write(_Artifact())                    # does not raise


def test_a_second_evaluation_appends_and_the_first_survives(tmp_path):
    """★★ ⚠ **Overwriting would let a refusal be replaced by a pass with nothing
    saying so.** The cost gate was wired *after* the first fit was graded — that
    is a second verdict on one model, and both belong in the record."""
    store = ArtifactStore(tmp_path)
    store.write(_Artifact(), evaluation={"gates": {"cost_survival": "NOT_EVALUATED"}})
    store.write(_Artifact(), evaluation={"gates": {"cost_survival": "PASS"}})

    files = store.read(_Artifact.artifact_id)
    assert "evaluation.json" in files and "evaluation-2.json" in files
    assert files["evaluation.json"]["gates"]["cost_survival"] == "NOT_EVALUATED"
    # ⚠ `sorted()` would put `evaluation-2.json` BEFORE `evaluation.json`
    #   (`-` sorts under `.`), returning the FIRST verdict — so a superseded
    #   refusal would read as the current one.
    assert store.latest_evaluation(_Artifact.artifact_id)["gates"][
        "cost_survival"] == "PASS"


def test_a_promotion_still_cannot_be_rewritten(tmp_path):
    """⚠ Evaluations append; **a promotion does not.** There is one moment a
    model entered production and it is not revisable (CT-4.3)."""
    from src.models.governance.promotion import PromotionRecord

    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    record = PromotionRecord(
        artifact_id=_Artifact.artifact_id, promoted_at=datetime.now(timezone.utc),
        promoted_by="t", backtest_result_id="b", gate_outcomes={},
        horizon_set_version=1, contract_version=1)
    store.record_promotion(record)
    with pytest.raises(AppendOnlyViolation):
        store.record_promotion(record)


# --------------------------------------------------------------------------- #
# ★★★ MT-19 — D-04 does not evaluate itself
# --------------------------------------------------------------------------- #

def test_promotion_refuses_without_a_d03_backtest_id():
    """★★★ **The rule caught a real design error, 2026-08-27.**

    All three gates passed and promotion **still refused**: the training run had
    been computing gate outcomes *inside D-04*, which is the domain marking its
    own homework. ⚠ MT-19 says it in those words — *"D-04 does not evaluate
    itself; a promotion with no evaluation is the gate skipped, not passed"* —
    and `promote()` enforces it by demanding an id D-04 cannot mint.
    """
    from src.models.errors import ModelError
    from src.models.governance.promotion import promote

    with pytest.raises(ModelError, match="BacktestResult"):
        promote(_Artifact(), backtest_result_id="",
                gate_outcomes={g: "PASS" for g in
                               ("ic_significance", "cost_survival", "breadth")},
                promoted_by="t", at=datetime.now(timezone.utc))


def test_the_backtest_spec_declares_survivorship_explicitly():
    """★★ QA-14 — ⚠ *a backtest over currently-listed names only is reported as
    **biased**, not as a result*, and INV-017 says it cannot be corrected from
    these sources. The field is passed explicitly rather than defaulted."""
    import inspect

    from src.models.train.run import d03_evaluate

    source = inspect.getsource(d03_evaluate)
    assert "survivorship_handled=False" in source
    assert "QA-14" in source


def test_an_unpinned_backtest_spec_is_inadmissible():
    """QA-11 — ★ *an unpinned input makes the result unreproducible and therefore
    **inadmissible as evidence***."""
    from datetime import date as _date

    from src.quant.contracts.backtest import BacktestSpec
    from src.quant.errors import QuantError

    with pytest.raises(QuantError, match="INADMISSIBLE"):
        BacktestSpec(universe=("A",), start=_date(2020, 1, 1),
                     end=_date(2026, 1, 1), horizon_set_name="production",
                     horizon_set_version=1, initial_capital=100_000.0,
                     contract_version=1,
                     calendar_check_id="",          # ⚠ the unpinned field
                     as_of=_date(2026, 1, 1), adj_as_of=_date(2026, 1, 1),
                     decision_anchor="open")


# --------------------------------------------------------------------------- #
# ★★ Retirement is a tombstone, not a deletion
# --------------------------------------------------------------------------- #

def test_retirement_keeps_the_record_and_removes_it_from_service(tmp_path):
    """★★ ⚠ The obvious move is `rm -rf` the directory. **CT-4.3, RC-60 and
    OR-13 all forbid it for one reason** — *a record that can be removed after
    the outcome is known is not evidence* — and a superseded model is exactly
    what you want when the next one misbehaves."""
    from src.models.governance.promotion import PromotionRecord

    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    store.record_promotion(PromotionRecord(
        artifact_id=_Artifact.artifact_id, promoted_at=datetime.now(timezone.utc),
        promoted_by="t", backtest_result_id="b", gate_outcomes={},
        horizon_set_version=1, contract_version=1))
    assert store.promoted(role="selection", horizon_id="h1m") is not None

    store.retire(_Artifact.artifact_id, reason="superseded by a 61-feature fit")

    # ★ Out of service…
    assert store.promoted(role="selection", horizon_id="h1m") is None
    # …⚠ but the record — including the promotion that really happened — stays.
    files = store.read(_Artifact.artifact_id)
    assert "manifest.json" in files and "promotion.json" in files
    assert files["retirement.json"]["reason"]


def test_retirement_requires_a_stated_reason(tmp_path):
    """MT-36's argument one level down — ⚠ *a model stood down for no recorded
    cause is indistinguishable from one stood down by accident*."""
    from src.models.errors import ModelError

    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    with pytest.raises(ModelError, match="stated reason"):
        store.retire(_Artifact.artifact_id, reason="   ")


def test_a_retirement_cannot_be_rewritten(tmp_path):
    """★ Append-only, like the promotion it stands down."""
    store = ArtifactStore(tmp_path)
    store.write(_Artifact())
    store.retire(_Artifact.artifact_id, reason="superseded")
    with pytest.raises(AppendOnlyViolation):
        store.retire(_Artifact.artifact_id, reason="superseded again")


def test_retiring_something_that_does_not_exist_raises(tmp_path):
    """⚠ A retirement that silently no-ops would report a model as stood down
    when nothing was."""
    from src.models.errors import ModelError

    with pytest.raises(ModelError, match="no artifact"):
        ArtifactStore(tmp_path).retire("sha256:absent", reason="x")
