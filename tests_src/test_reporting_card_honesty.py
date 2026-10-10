"""D-09 / D-12 / D-08 — the card says what it rests on. ✏ Written 2026-10-06 (L9 §10 C1–C4).

* AC-9.35 (RP-53) — with the placeholder thesis gate the verdict row reads NO VERDICT, never
  the nominated BUY, and the placeholder text names today's cause, not a passed milestone.
* AC-9.36 (RP-54) + AC-12.30 (DN-40) — the card names the rule or model that ranked the pick.
* AC-8.43 (OR-55) — the daily run's manifest declares the placeholder gate in `stubs[]`.
"""

from __future__ import annotations

from datetime import date

from src.reporting import build_card
from src.reporting.deliver.markdown import render_markdown
from tests_src.test_reporting_b3 import AS_OF, graded, recommendation


def _verdict(card):
    return card.field("verdict").value


def test_ac_9_35_a_placeholder_gate_renders_no_verdict_never_buy():
    """AC-9.35 — ⚠ the card read "Verdict: BUY": a fixed BUY nomination passed through a
    gate that always PASSes. Nothing analysed the name."""
    from src.quant import rule_id

    card = build_card(recommendation(model_artifact_id=rule_id()), as_of=AS_OF)
    value = _verdict(card)
    assert "BUY" not in value and value.startswith("no verdict")
    assert "ranked #1 by the rule" in value and "no thesis" in value
    assert "| verdict | no verdict" in render_markdown(card)


def test_ac_9_35_a_real_thesis_gate_still_renders_its_verdict():
    """AC-9.35 — the rule is about the PLACEHOLDER only; a graded gate renders as before."""
    from tests_src.test_reporting_b3 import STABILITY

    card = build_card(recommendation(gate=graded(), actionable=True,
                                     stability=STABILITY), as_of=AS_OF)
    assert _verdict(card) == "BUY"


def test_ac_9_35_the_placeholder_names_todays_cause_not_a_passed_milestone():
    """AC-9.35 / C2 — ⚠ it said *"D-01 is not built … replaced by the real gate at B4.4"*.
    D-01 is built; theses are authored on demand and the daily run writes none (DX-153)."""
    from src.fundamental import REPLACED_AT, STUB_REASON

    card = build_card(recommendation(), as_of=AS_OF)
    for text in (STUB_REASON, REPLACED_AT, card.falsifier, *card.data_gaps):
        assert "not built" not in text and "B4.4" not in text, text
    assert "on demand" in STUB_REASON and "on demand" in card.falsifier


def test_ac_12_30_the_recommendation_carries_what_ranked_the_pick():
    """AC-12.30 (DN-40) — byte-identical artifact id, named rule or model."""
    from src.quant import RANK_FORMULA_ID, rule_id

    by_rule = recommendation(model_artifact_id=rule_id()).candidate["ranked_by"]
    # ✏ 2026-10-09 — DN-41 / F12 D15 extend the record with the ranker's status.
    assert by_rule == {"artifact_id": rule_id(), "kind": "rule",
                       "formula_id": RANK_FORMULA_ID, "status": "rule", "refused_gates": []}
    by_model = recommendation(model_artifact_id="sha256:85b7").candidate["ranked_by"]
    assert by_model == {"artifact_id": "sha256:85b7", "kind": "model",
                        "formula_id": None, "status": "rule", "refused_gates": []}


def test_ac_9_36_the_card_names_the_rule_that_ranked_the_pick():
    """AC-9.36 (RP-54) — ★ PG-10 transparency: rule or model, on the card itself."""
    from src.quant import RANK_FORMULA_ID, rule_id

    card = build_card(recommendation(model_artifact_id=rule_id()), as_of=AS_OF)
    ranked_by = card.field("ranked_by")
    assert ranked_by.source == "D-03"
    assert "rule" in ranked_by.value and RANK_FORMULA_ID in ranked_by.value
    model = build_card(recommendation(model_artifact_id="sha256:85b7"), as_of=AS_OF)
    assert "model" in model.field("ranked_by").value
    assert "sha256:85b7" in model.field("ranked_by").value


def test_ac_8_43_the_daily_manifest_declares_the_placeholder_gate(monkeypatch):
    """AC-8.43 (OR-55) — ⚠ the daily entrypoint passed `stubs=()`, so the run record said
    `[]` while the thesis gate WAS the placeholder."""
    from src.fundamental import GATE_ID
    from src.orchestration import entrypoint
    from src.orchestration.schedule.preconditions import BlockedPrecondition

    seen = {}

    class _Orc:
        graph = None

        def trigger(self, **kw):
            seen.update(kw)
            return BlockedPrecondition(job_graph_id="g", as_of=kw["as_of"],
                                       code="TEST.STOP", reason="captured")

    monkeypatch.setattr(entrypoint, "build_orchestrator", lambda **k: _Orc())
    monkeypatch.setattr(entrypoint, "_day_bar", lambda *a, **k: None)
    monkeypatch.setattr(entrypoint, "_incumbent_model", lambda: None)
    entrypoint.main(["--as-of", "2026-08-25"])
    stubs = [s.to_json_obj() if hasattr(s, "to_json_obj") else s
             for s in seen.get("stubs", ())]
    assert any(s["domain"] == "D-01" and s["job"] == GATE_ID for s in stubs), stubs
