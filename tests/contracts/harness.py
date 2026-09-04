"""F1 — the contract-suite base (AC-1.7, AC-1.9).

⚠ Lives OUTSIDE conftest.py on purpose. pytest loads conftest under its own
module name, so a class defined there is a DIFFERENT object from the one a test
module imports — and `issubclass` silently returns False, which disables the
parameterisation without failing anything. Exactly the quiet failure the
constitution warns about in §4.
"""

from __future__ import annotations

from tests.contracts.fixture_ports import build_registry


class PortContractSuite:
    """Base for every port's contract suite.

    Subclasses declare:
      port            — the port name as registered
      primary_method  — AC-1.7: "the port's primary method, as named in its own contract"
      sample_inputs   — (A, B), two DIFFERENT inputs to the primary method
    """

    port: str
    primary_method: str
    sample_inputs: tuple[object, object]

    @staticmethod
    def registry():
        return build_registry()

    def test_ac_1_7_no_state_leaks_between_calls(self, variant):
        """AC-1.7 — call A then B on one instance; B must equal B on a fresh instance."""
        assert_no_state_leak(
            self.registry, self.port, variant, self.primary_method, self.sample_inputs
        )


def assert_no_state_leak(registry_factory, port, variant, primary_method, sample_inputs):
    """AC-1.7's actual check, extracted so a meta-test can prove it has POWER.

    ⚠ Deliberately NOT idempotence. "Same input twice → same output" would fail a
    correct adapter that reads a moving external world — a PricePort hitting a live
    vendor legitimately returns different results if the data moved. What AC-1.6's
    instance caching requires is that no CALLER-VISIBLE STATE carries between calls,
    which is what the A-then-B form tests.
    """
    a, b = sample_inputs
    shared = registry_factory().resolve(port, variant)
    getattr(shared, primary_method)(a)
    after_a = getattr(shared, primary_method)(b)

    fresh = registry_factory().resolve(port, variant)
    alone = getattr(fresh, primary_method)(b)
    assert after_a == alone, f"{port}/{variant}: state leaked from the previous call"
