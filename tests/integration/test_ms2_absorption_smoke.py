"""MS-2.4 — the absorbed domain works here, and the boundary holds both ways.

`MS-2`'s original wording was *"call one pipeline function from this repo, get
real data back"*, through a shim. There is no shim (`QR-22`): `src/shared/` was
absorbed, so those calls are now **plain intra-repo imports**. What still needs
proving is the part that is genuinely new — that an import edge **crossing the
two repos** resolves, in both directions, through the namespace package.

⚠ Deliberately no mocks. A smoke test that stubs the thing it is smoke-testing
proves the stub works.
"""

from __future__ import annotations

import pathlib
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.shared.errors import CurrencyMismatchError, PipelineError
from src.shared.money import BASE_CURRENCY, FxRate, Money, sum_money
from src.shared.registry import Registry

REPO = pathlib.Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# 1. the absorbed code is REALLY here — not resolving from somewhere else
# --------------------------------------------------------------------------- #
def test_absorbed_modules_load_from_this_repo():
    """⚠ The one assertion the rest depends on.

    If `src.shared.money` were still resolving out of the upstream tree, every
    test below would pass and prove nothing about the absorption.
    """
    import src.shared.money as m

    assert pathlib.Path(m.__file__).resolve().is_relative_to(REPO), (
        f"src.shared.money loaded from {m.__file__} — not this repo. The "
        "absorption did not take effect; check pyproject pythonpath order."
    )


def test_upstream_modules_load_from_the_sibling_repo():
    """The mirror: a NON-absorbed domain must still come from upstream."""
    import src.quant.errors as q

    assert not pathlib.Path(q.__file__).resolve().is_relative_to(REPO), (
        f"src.quant.errors loaded from {q.__file__} — inside this repo. Either it "
        "was absorbed without updating this test, or a stray copy exists (QR-22 "
        "forbids one domain living in two trees)."
    )


# --------------------------------------------------------------------------- #
# 2. real data, real arithmetic — the case that motivated the module
# --------------------------------------------------------------------------- #
def test_money_does_real_exact_arithmetic():
    """The defect `money.py` exists to prevent: 1.00 x 1.365 must be 1.37.

    `float` + banker's rounding gave 1.36, and the errors were systematically
    downward so they did not cancel (AC-M.19).
    """
    one_cad = Money.from_decimal_str("1.00", "CAD")
    rate = FxRate(pair="CADUSD", rate=Decimal("1.365"),
                  as_of=datetime(2026, 9, 4, tzinfo=timezone.utc), source="smoke-test")
    assert one_cad.convert(rate) == Money(137, "USD")


def test_money_refuses_to_mix_currencies():
    """`P5` — a degraded input raises rather than emitting a plausible default."""
    with pytest.raises(CurrencyMismatchError):
        Money(100, "CAD") + Money(100, "USD")


def test_sum_money_over_a_real_book():
    book = [Money.from_decimal_str(x, BASE_CURRENCY) for x in ("12.34", "0.66", "-3.00")]
    assert sum_money(book, BASE_CURRENCY) == Money(1000, "CAD")


# --------------------------------------------------------------------------- #
# 3. ★ the boundary itself — an UPSTREAM class inheriting an ABSORBED base
# --------------------------------------------------------------------------- #
def test_an_upstream_class_inherits_from_an_absorbed_base():
    """★★ The strongest available evidence that the link works.

    `src.quant.errors.QuantError` is defined upstream and subclasses
    `src.shared.errors.PipelineError`, which now lives HERE. The edge is resolved
    at class-definition time, in the direction upstream -> this repo. If the
    namespace package were broken, importing it would raise, not misbehave later.
    """
    from src.quant.errors import QuantError

    assert issubclass(QuantError, PipelineError)
    assert QuantError.__mro__[1].__module__ == "src.shared.errors"


def test_an_upstream_entrypoint_still_imports():
    """The whole daily run's import graph, exercised in one line."""
    from src.orchestration import entrypoint

    assert callable(entrypoint.main)


# --------------------------------------------------------------------------- #
# 4. absorbed code composes with the platform substrate (F1)
# --------------------------------------------------------------------------- #
def test_absorbed_code_resolves_through_the_f1_registry():
    """`MS-1` + `MS-2` together: the registry serves an absorbed implementation.

    This is what the milestone pair is actually for — a platform layer built here
    driving code that came from there, with provenance attached.
    """
    r = Registry()
    r.register("fx_rate", "fixed_cadusd",
               lambda: FxRate(pair="CADUSD", rate=Decimal("1.365"),
                              as_of=datetime(2026, 9, 4, tzinfo=timezone.utc),
                              source="smoke-test"),
               version="1.0.0")
    rate = r.resolve("fx_rate", "fixed_cadusd")
    assert Money.from_decimal_str("10.00", "CAD").convert(rate) == Money(1365, "USD")

    prov = r.provenance("fx_rate", "fixed_cadusd")
    assert (prov.port, prov.variant, prov.version) == ("fx_rate", "fixed_cadusd", "1.0.0")
    assert prov.experimental is False
