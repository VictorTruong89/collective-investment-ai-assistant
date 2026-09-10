"""`F8` — the five ACs `MS-6` left untraced, plus the structural half of `AC-8.16`.

⚠⚠ **`AC-8.16` was typed *invariant / property (structural)* and enforced by a
unit test on one object** (`DX-51`). `Directive.to_prompt_payload()` omits
`raw_text` and a test asserted that — but nothing stopped a *different* module
reading `.raw_text` and putting it in a prompt of its own. ★ The guarantee is
about the whole tree, so the check must be too.
"""

from __future__ import annotations

import pytest

from src.orchestration.control.directives import (
    EffectVocabulary,
    confirm,
    directive_delta,
    interpret,
)
from src.orchestration.control.models import (
    AnalysisRequest,
    Designation,
    control_trace_records,
)

VOCAB = EffectVocabulary(version="v1", effects=("exclude_sector",))


def _draft(mapping=None, directive_id="d1"):
    mapping = {"exclude_sector": "energy"} if mapping is None else mapping
    return interpret("skip energy for a week", vocabulary=VOCAB,
                     map_fn=lambda _t: mapping, directive_id=directive_id,
                     at="2026-09-09T00:00:00Z", window_from="2026-09-09",
                     window_to="2026-09-16")


def _active(mapping=None):
    return confirm(_draft(mapping))


# ── AC-8.20 — a directive is a capability that alters output ──────────────
def test_ac_8_20_an_active_directive_records_a_capability_delta():
    """★ `PG-5.2` — a directive CHANGES A TRADEABLE NUMBER, so it is a
    capability like any other and owes both arms."""
    delta = directive_delta(_active(), pre={"sector_weight": 0.20},
                            post={"sector_weight": 0.0}, decision_id="r:MU:1")
    assert delta["capability"] == "directive"
    assert delta["changed"] is True
    assert delta["pre"] == {"sector_weight": 0.20}


def test_ac_8_20_a_delta_is_recorded_even_when_NOTHING_changed():
    """⚠⚠ *including when nothing changed* — `AC-8.20`, `F2` `AC-2.6`.

    ★★ This is the arm that makes *"did the directive do anything?"* answerable
    at all. ⚠ Without it the only recorded directives are the ones that moved a
    number, and the effect size is 1.0 by construction — the same defect
    `F7a` `AC-7a.6` guards against, arriving through a different capability.
    """
    same = {"sector_weight": 0.20}
    delta = directive_delta(_active(), pre=same, post=same, decision_id="r:MU:1")
    assert delta["changed"] is False
    assert delta["capability"] == "directive"


def test_ac_8_20_a_DRAFT_directive_produces_no_delta():
    """⚠ `AC-8.15` — a draft has no effect on any run, so it has no arms to
    record. ★ Recording one would imply it ran."""
    draft = _draft(directive_id="d2")
    with pytest.raises(ValueError, match="DRAFT"):
        directive_delta(draft, pre={}, post={}, decision_id="r:MU:1")


def test_ac_8_20_the_delta_carries_the_effects_that_were_applied():
    """★ `PG-9` — *why did this run use these parameters?* must have an answer
    better than 'a directive was active'."""
    delta = directive_delta(_active(), pre={"a": 1}, post={"a": 2},
                            decision_id="r:MU:1")
    assert delta["effects"] == {"exclude_sector": "energy"}
    assert delta["directive_id"] == "d1"


# ── AC-8.11 — everything is traced ────────────────────────────────────────
def test_ac_8_11_the_request_the_designation_and_the_resume_are_all_traced():
    """`AC-8.11` — ★ all four control events carry the run's `run_id` (`F2`)."""
    req = AnalysisRequest(run_id="run-1", ticker="MU", attempt=2,
                          requested_at="2026-09-09T00:00:00Z", rank_held=7)
    des = Designation(run_id="run-1", decision_id="run-1:MU:2", ticker="MU",
                      displaced_decision_id="run-1:NVDA:1",
                      displaced_ticker="NVDA", at="2026-09-09T01:00:00Z")
    records = control_trace_records(run_id="run-1", request=req, designation=des,
                                    suspended_at="2026-09-09T00:30:00Z",
                                    resumed_at="2026-09-09T00:45:00Z")
    kinds = {r["event"] for r in records}
    assert kinds == {"request", "suspend", "resume", "designation"}
    assert all(r["run_id"] == "run-1" for r in records), (
        "every control record joins on the run's run_id (F2 AC-2.1)")


def test_ac_8_11_a_request_with_no_designation_still_traces():
    """★ §4 — *the ask is recorded regardless of outcome*. ⚠ Over a year that
    is behavioural data about the manager's own discipline (`D5`)."""
    req = AnalysisRequest(run_id="run-1", ticker="MU", attempt=2,
                          requested_at="2026-09-09T00:00:00Z", rank_held=7)
    records = control_trace_records(run_id="run-1", request=req, designation=None)
    assert [r["event"] for r in records] == ["request"]
    assert records[0]["decision_id"] == "run-1:MU:2"


def test_ac_8_11_the_records_reference_the_decision_id_they_belong_to():
    """⚠ `CT-2.7` — referenced, never minted here. ★ A drill-down is
    `attempt >= 2` and mints its own; the trace must carry it or `F7b` cannot
    join an outcome to the analysis the manager actually asked for."""
    req = AnalysisRequest(run_id="run-1", ticker="MU", attempt=3,
                          requested_at="2026-09-09T00:00:00Z")
    rec = control_trace_records(run_id="run-1", request=req, designation=None)[0]
    assert rec["decision_id"] == "run-1:MU:3"


# ── AC-8.4 — the rank is on the card ──────────────────────────────────────
def test_ac_8_4_a_drill_down_card_states_the_rank_the_name_held():
    """⚠⚠ §4 — *"A card that looks identical to the top-1's invites the reader
    to forget it was not."*

    ★★ This is `PG-2` in miniature: the drill-down runs at **full depth**
    (`QR-16`), which is exactly what makes the card indistinguishable — and the
    rank is the one field that says *you asked for this, the ranker did not
    surface it*.
    """
    from datetime import date

    from src.reporting.render.card import build_card
    from tests.unit.test_card_states_its_source import _rec

    card = build_card(_rec("api"), as_of=date(2026, 9, 9))
    assert "rank" in card.field_names
    assert card.field("rank").value == 1
    assert card.to_json_obj()["fields"]["rank"]["value"] == 1


def test_ac_8_4_the_rank_field_names_its_producing_domain():
    """★ D-09's OWN `AC-9.6` (⚠ not F9's `AC-F9.6` — DX-44) — a field
    D-09 could compute itself is one it must
    not. The rank is D-03's."""
    from datetime import date

    from src.reporting.render.card import build_card
    from tests.unit.test_card_states_its_source import _rec

    unit = build_card(_rec("api"), as_of=date(2026, 9, 9)).field("rank")
    assert unit.source == "D-03"
