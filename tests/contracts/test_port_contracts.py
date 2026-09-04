"""F1 — the concrete contract suites, plus the AC-1.9 meta-test."""

from __future__ import annotations

import pytest

from tests.contracts.harness import PortContractSuite, assert_no_state_leak
from tests.contracts.fixture_ports import LeakyGreeter, WarmupGreeter, build_registry


class TestGreeterContract(PortContractSuite):
    external_world_held_fixed = True  # pure in-memory adapters
    port = "greeter"
    primary_method = "greet"
    sample_inputs = ("Ada", "Grace")


class TestDoublerContract(PortContractSuite):
    external_world_held_fixed = True  # pure in-memory adapters
    port = "doubler"
    primary_method = "double"
    sample_inputs = (3, 7)


def test_ac_1_9_every_port_with_variants_has_a_contract_suite():
    """AC-1.9 — a port registered without a suite fails; the suite covers every variant."""
    suites = {c.port for c in PortContractSuite.__subclasses__()}
    registered = set(build_registry().ports())
    assert registered <= suites, f"ports registered with no contract suite: {registered - suites}"

    for cls in PortContractSuite.__subclasses__():
        covered = set(build_registry().variants(cls.port))
        assert covered, f"{cls.port} has a suite but no registered variants"


def test_ac_1_7_the_suite_actually_catches_a_leaky_adapter():
    """AC-1.7 (meta) — ⚠ prove the no-leakage CHECK has power, not just that the fixture leaks.

    Every adapter this repo registers today is stateless, so the suite would pass
    vacuously and tell us nothing. Running the real check against a deliberately
    leaky adapter is what proves it would catch one.
    """
    def leaky_registry():
        r = build_registry()
        r.register("greeter", "leaky", LeakyGreeter, version="0.0.1")
        return r

    with pytest.raises(AssertionError, match="state leaked"):
        assert_no_state_leak(leaky_registry, "greeter", "leaky", "greet", ("Ada", "Grace"))


def test_ac_1_7_the_fresh_instance_clause_is_load_bearing():
    """AC-1.7 (meta) — ⚠ a first-call-only leak is invisible without a FRESH instance.

    WarmupGreeter agrees with itself on every call after the first, so comparing two
    calls on one warm instance would pass. This is why the AC says "equals the result
    of calling B on a fresh instance" and not "twice on the same one".
    """
    def warm_registry():
        r = build_registry()
        r.register("greeter", "warmup", WarmupGreeter, version="0.0.1")
        return r

    with pytest.raises(AssertionError, match="state leaked"):
        assert_no_state_leak(warm_registry, "greeter", "warmup", "greet", ("Ada", "Grace"))


def test_ac_1_7_the_check_passes_a_well_behaved_adapter():
    """AC-1.7 (meta) — and does not fire on a correct one."""
    assert_no_state_leak(build_registry, "greeter", "polite", "greet", ("Ada", "Grace"))
