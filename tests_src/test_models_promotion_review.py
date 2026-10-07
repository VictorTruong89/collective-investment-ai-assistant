"""D-04 — MT-52 / AC-4.34: a training run HOLDS promotion for the fund manager's review.

✏ Written 2026-10-06 (Victor: *"training should hold promotion until I've reviewed it"*).
⚠ Before, `decide_promotion` wrote `promotion.json` the moment every gate passed, and the next
daily run scored the card with that model — no human step in between. Now training writes the
artifact and its evaluation marked `pending`; `python -m src.models.promote <id> --approve`
promotes, and still refuses unless every required gate PASSed (MT-17 — no override).
Hermetic: a tmp store, fake gate results; no data, no fit.
"""

from __future__ import annotations

import pytest

from src.models.artifact.store import ArtifactStore
from tests_src.test_models_artifact_store import _IC, _Artifact


def _gates(verdict="PASS"):
    from src.quant.gates.metric_gate import REQUIRED_GATES, GateResult

    stat = None if verdict == "NOT_EVALUATED" else 0.6
    return {g: GateResult(g, "h1m", stat, 0.5, None, None, "f.v1", verdict, f"{g} {verdict}")
            for g in REQUIRED_GATES}


def _train(tmp_path, monkeypatch, verdict="PASS"):
    import src.models.train.run as run

    monkeypatch.setattr(run, "gate_outcomes", lambda *a, **k: _gates(verdict))
    store = ArtifactStore(tmp_path / "models")
    outcome = run.decide_promotion(_Artifact(), ic_result=_IC(), names=500, store=store,
                                   backtest_result_id="bt:abc")
    return store, outcome


def test_ac_4_34_all_gates_passing_is_held_not_promoted(tmp_path, monkeypatch):
    store, outcome = _train(tmp_path, monkeypatch)
    assert outcome["promoted"] is False and outcome["pending_review"] is True
    files = store.read(_Artifact.artifact_id)
    assert "promotion.json" not in files, "MT-52: training never writes promotion.json"
    evaluation = files["evaluation.json"]
    assert evaluation["review"]["status"] == "pending"
    assert evaluation["backtest_result_id"] == "bt:abc"
    assert store.promoted(role="selection", horizon_id="h1m") is None


def test_ac_4_34_a_refused_model_is_marked_refused_not_pending(tmp_path, monkeypatch):
    store, outcome = _train(tmp_path, monkeypatch, verdict="FAIL")
    assert outcome["promoted"] is False and not outcome.get("pending_review")
    assert store.read(_Artifact.artifact_id)["evaluation.json"]["review"]["status"] == "refused"


def test_ac_4_34_promote_without_approve_only_shows_the_report(tmp_path, monkeypatch, capsys):
    from src.models.promote import main

    store, _ = _train(tmp_path, monkeypatch)
    assert main([_Artifact.artifact_id, "--models", str(store.root)]) == 0
    out = capsys.readouterr().out
    assert "ic_significance" in out and "pending" in out and "--approve" in out
    assert "promotion.json" not in store.read(_Artifact.artifact_id)


def test_ac_4_34_approve_promotes_a_model_whose_gates_all_passed(tmp_path, monkeypatch):
    from src.models.promote import main

    store, _ = _train(tmp_path, monkeypatch)
    assert main([_Artifact.artifact_id, "--models", str(store.root), "--approve"]) == 0
    record = store.read(_Artifact.artifact_id)["promotion.json"]
    assert record["backtest_result_id"] == "bt:abc"
    assert "review" in record["promoted_by"]
    assert store.promoted(role="selection", horizon_id="h1m") == _Artifact.artifact_id


def test_ac_4_34_approve_refuses_a_model_with_a_failed_gate(tmp_path, monkeypatch, capsys):
    """MT-17 — ★ no override: approval cannot promote past a gate."""
    from src.models.promote import main

    store, _ = _train(tmp_path, monkeypatch, verdict="FAIL")
    assert main([_Artifact.artifact_id, "--models", str(store.root), "--approve"]) == 1
    assert "promotion.json" not in store.read(_Artifact.artifact_id)
    assert "refused" in capsys.readouterr().err.lower()


def test_ac_4_34_an_unknown_artifact_is_said_plainly(tmp_path, capsys):
    from src.models.promote import main

    assert main(["sha256:nope", "--models", str(tmp_path / "models"), "--approve"]) == 1
    assert "no artifact" in capsys.readouterr().err.lower()


@pytest.fixture(autouse=True)
def _isolated(monkeypatch, tmp_path):
    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path / "state"))
