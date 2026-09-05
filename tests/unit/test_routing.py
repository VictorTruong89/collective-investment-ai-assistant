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
