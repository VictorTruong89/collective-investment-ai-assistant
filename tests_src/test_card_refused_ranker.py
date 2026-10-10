"""Card option (b) — a REFUSED model ranks the informational card, and says so. ✏ 2026-10-09 (Victor).

F12 D15 / AC-F12.37 · MT-67 / AC-4.49 · OR-58 / AC-8.46 · DN-41 / AC-12.31 · RP-55 / AC-9.37.

★ Measured 2026-10-09 on the same walk-forward dates: the card's momentum rule IC −0.008, the refused
fit 4 +0.030. PG-10: an output from a model that has not passed its own gates must say so.
"""

from __future__ import annotations

import json

import pytest

from src.quant import Candidate, Nomination
from src.quant.errors import NominationContractError
from tests_src.test_decision_b3 import AS_OF, alerts, composed, nomination

GATES = ("ic_significance", "breadth")


def _refused_nomination():
    return nomination(model_artifact_id="sha256:8200", ranker_status="refused_informational",
                      refused_gates=GATES)


# ── AC-F12.37 · D15 — the nomination carries its ranker's status ─────────────

def test_ac_f12_37_the_status_and_gates_ride_on_the_nomination():
    nom = _refused_nomination()
    obj = nom.to_json_obj()
    assert obj["ranker_status"] == "refused_informational"
    assert obj["refused_gates"] == list(GATES)
    assert nomination().to_json_obj()["ranker_status"] == "rule"


@pytest.mark.parametrize("bad", [dict(ranker_status="experimental"),
                                 dict(ranker_status="refused_informational")])
def test_ac_f12_37_an_unknown_status_or_a_refusal_without_gates_is_refused(bad):
    with pytest.raises(NominationContractError):
        nomination(**bad)


# ── AC-4.49 · MT-67 — the designation is explicit, revocable, never promotion ─

def test_ac_4_49_a_refused_artifact_can_be_designated_and_revoked(tmp_path, monkeypatch, capsys):
    from src.models.promote import main
    from tests_src.test_models_promotion_review import _Artifact, _train

    store, _ = _train(tmp_path, monkeypatch, verdict="FAIL")
    root = str(store.root)
    assert main([_Artifact.artifact_id, "--models", root, "--card-informational"]) == 0
    pointer = store.card_informational(role="selection", horizon_id="h1m")
    assert pointer["artifact_id"] == _Artifact.artifact_id
    assert set(pointer["refused_gates"]) >= {"ic_significance"}
    assert "promotion.json" not in store.read(_Artifact.artifact_id)
    assert main([_Artifact.artifact_id, "--models", root, "--card-informational-off"]) == 0
    assert store.card_informational(role="selection", horizon_id="h1m") is None


def test_ac_4_49_a_model_that_passed_its_gates_is_promoted_not_shown_as_refused(
        tmp_path, monkeypatch, capsys):
    from src.models.promote import main
    from tests_src.test_models_promotion_review import _Artifact, _train

    store, _ = _train(tmp_path, monkeypatch, verdict="PASS")
    assert main([_Artifact.artifact_id, "--models", str(store.root),
                 "--card-informational"]) == 1
    assert "promote" in capsys.readouterr().err.lower()
    assert store.card_informational(role="selection", horizon_id="h1m") is None


# ── AC-8.46 · OR-58 — the daily ranker order ─────────────────────────────────

def test_ac_8_46_promoted_then_designated_then_rule(tmp_path, monkeypatch):
    from src.models.promote import main
    from src.orchestration import entrypoint
    from tests_src.test_models_promotion_review import _Artifact, _train

    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path / "state"))
    store, _ = _train(tmp_path / "state", monkeypatch, verdict="FAIL")
    assert entrypoint._incumbent_model() is None, "nothing designated ⇒ the rule ranks"
    main([_Artifact.artifact_id, "--models", str(store.root), "--card-informational"])
    inc = entrypoint._incumbent_model()
    assert inc["status"] == "refused_informational" and "ic_significance" in inc["refused_gates"]


def test_ac_8_46_the_rank_job_puts_the_status_on_the_nomination():
    import inspect

    from src.orchestration.jobs import wiring

    source = inspect.getsource(wiring)
    assert 'ranker_status=incumbent.get("status", "promoted")' in source
    assert "refused_gates=tuple(incumbent.get(\"refused_gates\") or ())" in source


# ── AC-12.31 · DN-41 — never actionable ──────────────────────────────────────

def test_ac_12_31_a_refused_ranking_can_never_be_actionable():
    from src.decision import Recommendation  # noqa: F401 — the module under test

    with pytest.raises(Exception, match="refused"):
        composed(nomination=_refused_nomination(), actionable=True)
    rec = composed(nomination=_refused_nomination(), actionable=False,
                   not_actionable_reason="ranked by a refused model",
                   alert_set=alerts())
    ranked_by = rec.candidate["ranked_by"]
    assert ranked_by["status"] == "refused_informational"
    assert ranked_by["refused_gates"] == list(GATES)


# ── AC-9.37 · RP-55 — the card says REFUSED, twice ───────────────────────────

def test_ac_9_37_the_card_names_the_refused_model_and_its_failed_gates():
    from src.fundamental import stub_gate_verdict
    from src.reporting import build_card
    from src.risk import AlertSet, unchecked
    from src.decision import compose

    rec = compose(
        nomination=_refused_nomination(),
        gate_verdicts=[stub_gate_verdict("NVDA", AS_OF)],
        alert_set=AlertSet((), unchecked("no book (RK-29)")),
        run_id="run-1", as_of=AS_OF, gate_roster_declared=("thesis",),
        manifest_anchor="open", actionable=False,
        not_actionable_reason="ranked by a refused model", top_thesis_stability=None,
        stubs=({"domain": "D-01", "job": "thesis", "behaviour": "constant PASS",
                "replaced_at": "B4.4", "rule": "L3 BS-11"},))
    card = build_card(rec, as_of=AS_OF)
    ranked = card.field("ranked_by").value
    assert "REFUSED" in ranked and "ic_significance" in ranked and "breadth" in ranked
    assert "informational" in ranked and "not promoted" in ranked
    assert "refused model" in card.field("verdict").value
    json.dumps(rec.candidate["ranked_by"])                   # serialisable
    assert Candidate and Nomination
