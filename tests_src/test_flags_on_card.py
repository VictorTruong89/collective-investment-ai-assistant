"""RK-40 on the daily path — D-05's flag pass → D-12 → D-09 (Victor 2026-10-21, L9 §6.5 ⓐ).

AC-5.25 · AC-12.32 (DN-43) · AC-9.38 (RP-57) · AC-8.50 (OR-63).

★ The flag pass is labelled apart from the risk pass and never blended into it: it changes
neither `alerts_status` nor `actionable`, and the card shows it under its own heading.

Tier: unit (compose, card) · integration (the graph).
"""

from __future__ import annotations

from datetime import date

import pytest

from src.risk import unchecked
from tests_src.test_decision_b3 import alerts, composed, gate

THROUGH = date(2026, 10, 2)


def _pass(status="COMPLETE"):
    """A CT-5.4 FlagPass as D-05 publishes it: 3 flags, 2 of them recent."""
    from src.risk.flags.behavioural import Flag
    from src.risk.flags.from_book import FlagPass

    if status != "COMPLETE":
        return FlagPass(status=status, as_of=date(2026, 10, 21), history_through=None,
                        accounts=(), flags=(), counts={},
                        short_hold_trailing_frequency=None, recent=())
    flags = (
        Flag("M4:MU:RRSP_1:2026-09-23", "registered_short_hold", "MU", "RRSP_1",
             date(2026, 10, 21), {"held_days": 1, "closed_on": "2026-09-23",
                                  "trailing_frequency": 0.5664}, trailing_count=81),
        Flag("M3:AAA:TFSA_1:2026-03-02", "pyramiding", "AAA", "TFSA_1",
             date(2026, 3, 2), {"avg_cost_before": 10.0, "avg_cost_after": 15.0}),
        Flag("PX:ARM:TFSA_1:2026-09-29", "premature_exit", "ARM", "TFSA_1",
             date(2026, 9, 29), {"held_days": 5}),
    )
    return FlagPass(status="COMPLETE", as_of=date(2026, 10, 21), history_through=THROUGH,
                    accounts=("RRSP_1", "TFSA_1"), flags=flags,
                    counts={"pyramiding": 1, "premature_exit": 1, "registered_short_hold": 1},
                    short_hold_trailing_frequency=0.5664,
                    recent=("M4:MU:RRSP_1:2026-09-23", "PX:ARM:TFSA_1:2026-09-29"))


# ── AC-12.32 / AC-5.25 — carried, never blended ────────────────────────────────

def test_ac_12_32_the_flag_pass_is_carried_verbatim():
    """AC-12.32 (DN-43) — D-12 reads nothing in it; the JSON is D-05's, byte for byte."""
    fp = _pass().to_json_obj()
    rec = composed(alert_set=alerts(unchecked("no book (RK-29)")), actionable=False,
                   top_thesis_stability=None, behavioural_flags=fp)
    assert rec.behavioural_flags == fp
    assert rec.to_json_obj()["behavioural_flags"] == fp


def test_ac_5_25_a_complete_flag_pass_leaves_the_risk_status_unchecked():
    """AC-5.25 (RK-40, RK-30) — the flags' COMPLETE is not the risk pass's."""
    fp = _pass().to_json_obj()
    without = composed(alert_set=alerts(unchecked("no book (RK-29)")), actionable=False,
                       top_thesis_stability=None)
    with_flags = composed(alert_set=alerts(unchecked("no book (RK-29)")), actionable=False,
                          top_thesis_stability=None, behavioural_flags=fp)
    assert with_flags.alerts_status == without.alerts_status
    assert with_flags.alerts_status.startswith("UNCHECKED")
    assert with_flags.verdict_final == without.verdict_final
    assert with_flags.alerts == without.alerts


def test_ac_5_25_a_complete_flag_pass_never_makes_a_card_actionable():
    """AC-5.25 (DN-39) — actionable still needs the FULL pass."""
    from src.decision.errors import DecisionError

    with pytest.raises(DecisionError):
        composed(alert_set=alerts(unchecked("no book (RK-29)")), actionable=True,
                 behavioural_flags=_pass().to_json_obj())


# ── AC-9.38 — the card ─────────────────────────────────────────────────────────

def _card(fp):
    from src.reporting import build_card
    from tests_src.test_decision_b3 import AS_OF

    rec = composed(gate_verdicts=[gate()], alert_set=alerts(unchecked("no book (RK-29)")),
                   actionable=False, top_thesis_stability=None,
                   behavioural_flags=fp.to_json_obj() if fp else None)
    return build_card(rec, as_of=AS_OF)


def test_ac_9_38_markdown_shows_the_pass_under_its_own_label():
    """AC-9.38 (RP-57) — counts per kind, the recent flags in full, the rest counted."""
    from src.reporting.deliver.markdown import render_markdown

    md = render_markdown(_card(_pass()))
    risk = md[md.index("## Risk"):]
    assert "status: UNCHECKED" in risk                      # the risk pass, untouched
    assert "Behavioural flags" in risk and "trade history through 2026-10-02" in risk
    assert "not part of the exposure pass" in risk
    for line in ("registered_short_hold: 1", "pyramiding: 1", "premature_exit: 1"):
        assert line in risk
    assert "0.5664" in risk                                 # RK-17 trailing frequency
    assert "MU" in risk and "ARM" in risk                   # recent, listed
    assert "AAA" not in risk                                # older: counted, not listed
    assert "1 older flag(s) counted, not listed" in risk


def test_ac_9_38_html_and_email_say_the_same():
    """AC-9.38 — every medium (RP-57)."""
    from src.reporting.deliver.email import build_message
    from src.reporting.deliver.html import render_html

    card = _card(_pass())
    html = render_html(card)
    assert "Behavioural flags" in html and "2026-10-02" in html and "ARM" in html
    body = build_message(card, {}, sender="a@x", recipient="b@x").get_body().get_content()
    assert "Behavioural flags" in body and "registered_short_hold: 1" in body


def test_ac_9_38_an_unchecked_pass_renders_its_reason_and_no_counts():
    """AC-9.38 (RP-57, RK-36) — never zero flags where none were read."""
    from src.reporting.deliver.markdown import render_markdown

    md = render_markdown(_card(_pass("UNCHECKED: TFSA_1: unreadable")))
    risk = md[md.index("## Risk"):]
    assert "Behavioural flags: UNCHECKED: TFSA_1: unreadable" in risk
    assert "registered_short_hold:" not in risk


def test_ac_9_38_no_pass_at_all_says_so():
    """AC-9.38 — a run without the job (an older graph) is absence, not all-clear."""
    from src.reporting.deliver.markdown import render_markdown

    md = render_markdown(_card(None))
    assert "Behavioural flags: not run" in md


# ── AC-8.50 — the graph ────────────────────────────────────────────────────────

def test_ac_8_50_the_graph_runs_the_flag_pass_by_dotted_name():
    """AC-8.50 (OR-63) — its own optional job; `risk` and `decide` read it."""
    from src.orchestration import DAILY_INFERENCE

    jobs = {j.job_id: j for j in DAILY_INFERENCE.jobs}
    assert jobs["flags"].invokes == "src.risk.flags.from_book:flag_pass"
    assert jobs["flags"].optional is True
    assert "flags" in jobs["risk"].depends_on and "flags" in jobs["decide"].depends_on


def test_ac_8_50_the_pass_reaches_the_recommendation(tmp_path):
    """AC-8.50 — end to end, on exports in a test directory."""
    from tests_src.test_orchestration_wiring import context, orchestrator, triggered
    from tests_src.test_risk_flag_pass import _book
    from src.orchestration.jobs.wiring import make_dispatch

    _book(tmp_path)
    orc, ctx = orchestrator(), context()
    ctx.broker_root = str(tmp_path)
    outcome = orc.run(triggered(orc, ctx).run_id, invoke=make_dispatch(ctx))
    assert outcome.status == "SUCCESS"
    fp = ctx.outputs["decide"].behavioural_flags
    assert fp["status"] == "COMPLETE" and fp["history_through"] == "2026-10-02"
    assert ctx.outputs["decide"].alerts_status.startswith("UNCHECKED")


def test_ac_8_50_a_failing_pass_is_unchecked_never_empty_complete(tmp_path, monkeypatch):
    """AC-8.50 (OR-63, P5) — an exception inside D-05 becomes UNCHECKED with its reason."""
    import src.risk.flags.from_book as fb
    from src.orchestration.jobs.wiring import make_dispatch
    from tests_src.test_orchestration_wiring import context, orchestrator, triggered

    def boom(**_k):
        raise RuntimeError("parser exploded")

    monkeypatch.setattr(fb, "flag_pass", boom)
    orc, ctx = orchestrator(), context()
    ctx.broker_root = str(tmp_path)
    orc.run(triggered(orc, ctx).run_id, invoke=make_dispatch(ctx))
    fp = ctx.outputs["decide"].behavioural_flags
    assert fp["status"].startswith("UNCHECKED: ") and "parser exploded" in fp["status"]
    assert fp["flags"] == []
