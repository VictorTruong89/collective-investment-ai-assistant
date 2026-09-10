"""F6a — config-influence routing. `MS-6.7`."""

from __future__ import annotations

import pytest

from src.orchestration.policy.routing import (
    PHASE_ORDER,
    VOL_THRESHOLD,
    PhaseOrderViolation,
    Routing,
    UnknownPort,
    assert_forward,
    select,
)


def test_ac_6a_1_identical_inputs_give_an_equal_routing():
    """PG-9 — ⚠ a stochastic control plane destroys F7a/F7b's ability to
    attribute an outcome difference to deliberation."""
    f = {"realised_vol_60d": 0.51}
    assert select("ranking_model", f) == select("ranking_model", f)


def test_ac_6a_2_select_performs_no_io(monkeypatch):
    """AC-6a.2 — pure. No clock, no file, no network."""
    import builtins
    real = builtins.open
    monkeypatch.setattr(builtins, "open",
                        lambda *a, **k: pytest.fail("select() opened a file"))
    try:
        select("ranking_model", {"realised_vol_60d": 0.51})
    finally:
        monkeypatch.setattr(builtins, "open", real)


def test_ac_6a_3_the_reason_is_specific_not_boilerplate():
    r = select("ranking_model", {"realised_vol_60d": 0.51})
    assert r.reason == f"realised_vol_60d > {VOL_THRESHOLD}"
    assert r.variant == "1w"


def test_ac_6a_3_an_empty_reason_cannot_be_constructed():
    with pytest.raises(ValueError, match="reason is never empty"):
        Routing("p", "a", "", ("a",))


def test_ac_6a_4_a_routing_may_only_name_a_registered_candidate():
    """F1 AC-1.5 — the variant set is closed; routing cannot invent one."""
    with pytest.raises(ValueError, match="not among"):
        Routing("ranking_model", "gpt5", "because", ("1m", "1w"))


def test_ac_6a_5_cross_configuration_is_recorded():
    """★ PG-7 — concurrence between INDEPENDENT views is informative;
    cross-configuration silently turns concurrence into an echo.

    ⚠ Note the DIRECTION: quant's volatility shapes how deep the FUNDAMENTAL
    analysis goes. Found while writing this test — the spec's worked example
    routed `ranking_model`, a quant port in the FIRST phase, which nothing may
    legitimately configure. `assert_forward` refused it, correctly.
    """
    r = select("thesis_depth", {},
               peer={"realised_vol_60d": 0.9, "seat_domain": "quant"})
    assert r.variant == "deep"
    assert r.influenced_by == "quant", "the shaping seat must be named"


def test_ac_6a_5_nothing_may_configure_the_first_phase():
    """★★ AC-6a.7 at the select() boundary, not just the helper."""
    with pytest.raises(PhaseOrderViolation, match="forward"):
        select("ranking_model", {}, peer={"realised_vol_60d": 0.9,
                                          "seat_domain": "fundamental"})


def test_ac_6a_5_an_uninfluenced_selection_records_none():
    assert select("ranking_model", {"realised_vol_60d": 0.9}).influenced_by is None


def test_ac_6a_7_influence_flows_forward_only():
    """★★ AC-6a.7 / D1 — the order is DERIVED from coverage economics."""
    assert PHASE_ORDER == ("quant", "fundamental", "risk", "decision")
    assert_forward("quant", "fundamental")            # forward: fine


@pytest.mark.parametrize("a,b", [("risk", "quant"), ("decision", "fundamental"),
                                 ("quant", "quant")])
def test_ac_6a_7_backward_or_same_phase_influence_is_refused(a, b):
    """⚠ A cycle makes two seats configure each other, and neither output is
    independent of the other — the firewall's whole premise."""
    with pytest.raises(PhaseOrderViolation, match="forward"):
        assert_forward(a, b)


def test_ac_6a_7_an_unknown_domain_is_refused():
    with pytest.raises(PhaseOrderViolation, match="not in the declared phase order"):
        assert_forward("astrology", "quant")


@pytest.mark.parametrize("features", [{}, {"realised_vol_60d": None},
                                      {"realised_vol_60d": "n/a"},
                                      {"unrelated": 1}])
def test_ac_6a_11_select_is_total_and_falls_back_to_the_default(features):
    """AC-6a.11 — every input yields a Routing, including degenerate ones."""
    r = select("ranking_model", features)
    assert r.reason == "default" and r.variant == "1m"


def test_ac_6a_11_an_undeclared_port_raises_rather_than_guessing():
    """⚠ P5 — routing cannot invent a candidate set."""
    with pytest.raises(UnknownPort, match="closed"):
        select("no_such_port", {})


def test_d2_exactly_one_predicate_ships_at_ms6():
    """D2 — ⚠ every unexercised branch is a control-plane path PG-9's replay
    has never covered."""
    import src.orchestration.policy.routing as m
    reasons = {select("ranking_model", {"realised_vol_60d": v}).reason
               for v in (0.0, 0.44, 0.46, 9.9)}
    assert reasons == {"default", f"realised_vol_60d > {m.VOL_THRESHOLD}"}


# ═══════════════════════════════════════════════════════════════════════════
# AC-6a.8 · AC-6a.9 · AC-6a.10 — the three ACs `MS-6` left untraced.
#
# ⚠⚠ A spec-vs-spec disagreement found while writing these (`DX-40`):
#    F2 §4 says *"a decision record is written by the routing function
#    itself"*; F6a §2 non-goals says *"✗ Recording. F6a returns the reason;
#    F2 persists it."* ★ Resolved in F6a's favour — `routing.py` imports
#    nothing from `trace/`, and the seam lives in F2's `wire.py`, where the
#    other record-writing seams already live.
# ═══════════════════════════════════════════════════════════════════════════


def test_ac_6a_8_a_selection_is_recorded_with_propensity_one(tmp_path):
    """`AC-6a.8` — ★ every routing choice leaves a `DecisionRecord`.

    ⚠ `propensity == 1.0` *while the control plane is deterministic* (`PG-9`).
    F2 §4: the field exists NOW so off-policy evaluation is possible later —
    **it is not a placeholder to add when needed, because by then the history
    is gone.**
    """
    from src.orchestration.trace.models import mint_decision_id
    from src.orchestration.trace.store import TraceStore
    from src.orchestration.trace.wire import record_routing

    store = TraceStore(tmp_path, "run-1")
    decision_id = mint_decision_id("run-1", "MU")
    routing = select("thesis_depth", {"realised_vol_60d": 0.60})
    record_routing(store, routing, step_id="route:thesis_depth",
                   decision_id=decision_id, state={"realised_vol_60d": 0.60})
    store.close()

    rec = next(r for r in store.read_all() if r.get("type") == "DecisionRecord")
    assert rec["action"] == "deep"
    assert rec["reason"] == f"realised_vol_60d > {VOL_THRESHOLD}"
    assert rec["candidates"] == ["standard", "deep"]
    assert rec["propensity"] == 1.0
    assert rec["decision_id"] == decision_id
    assert rec["state"] == {"realised_vol_60d": 0.60}


def test_ac_6a_8_the_decision_id_is_referenced_never_minted_here(tmp_path):
    """⚠⚠ `CT-2.7` — *"a routing choice is part of a decision, not the
    decision."* Its own identity is `step_id`.

    ★ If `record_routing` minted an id, every routing choice would become its
    own decision and `F7b`'s join to outcomes would fan out — the Tier-B study
    rests on exactly this key.
    """
    import inspect

    from src.orchestration.trace import wire
    src = inspect.getsource(wire.record_routing)
    assert "mint_decision_id" not in src, (
        "record_routing must REFERENCE a decision_id, never mint one (CT-2.7)")
    with pytest.raises(TypeError):
        wire.record_routing(object(), select("thesis_depth", {}),
                            step_id="s")  # decision_id is required


def test_ac_6a_8_an_influenced_selection_carries_the_seat_into_the_record(tmp_path):
    """★ `PG-7.1` and `PG-9`'s reason are the SAME field, recorded once (F2 §4)."""
    from src.orchestration.trace.store import TraceStore
    from src.orchestration.trace.wire import record_routing

    store = TraceStore(tmp_path, "run-1")
    routing = select("thesis_depth", {}, peer={"seat_domain": "quant",
                                               "realised_vol_60d": 0.9})
    record_routing(store, routing, step_id="route:1", decision_id="run-1:MU:1",
                   state={"realised_vol_60d": 0.9})
    store.close()
    rec = next(r for r in store.read_all() if r.get("type") == "DecisionRecord")
    assert rec["influenced_by"] == "quant"
