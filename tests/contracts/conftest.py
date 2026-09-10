"""F1 — contract-suite parameterisation (AC-F1.9).

★ This is the mechanism F1 §4 calls "one contract suite per port, parameterised
over every registered variant": a newly registered variant is picked up WITHOUT
anyone remembering to add it to a list.
"""

from __future__ import annotations

from tests.contracts.fixture_ports import build_registry
from tests.contracts.harness import PortContractSuite


def pytest_generate_tests(metafunc):
    """AC-F1.9 — run each suite once per REGISTERED variant of its port."""
    cls = getattr(metafunc, "cls", None)
    if cls is not None and issubclass(cls, PortContractSuite) and "variant" in metafunc.fixturenames:
        metafunc.parametrize("variant", build_registry().variants(cls.port))
