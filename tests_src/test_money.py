"""Money — L2-shared-money.md, AC-M.1 … AC-M.21.

Tier: unit (constitution §4). Coverage target for the module is 100% (AC-M.18):
it is ~200 lines, every domain imports it, and a gap here is a gap everywhere.

The exactness cases are not decoration. `pipeline/portfolio/money.py` exists
because two error sources compounded in the legacy code — binary representation
error in `float(rate)`, and the builtin `round()` being BANKER'S rounding where
money needs ROUND_HALF_UP — and the resulting cent errors were SYSTEMATICALLY
DOWNWARD, so they did not cancel. `1.00 x 1.365` returned 1.36 where money
arithmetic gives 1.37 (AC-M.19).
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import ROUND_DOWN, Decimal

import pytest

from src.shared.errors import (
    CurrencyMismatchError,
    FxDirectionError,
    InvalidAmountError,
    PrecisionLossError,
    UnsupportedCurrencyError,
)
from src.shared.money import BASE_CURRENCY, SUPPORTED_CURRENCIES, FxRate, Money, sum_money

USD, CAD = "USD", "CAD"


def rate(value="1.3742", pair="USDCAD"):
    return FxRate(pair=pair, rate=Decimal(value),
                  as_of=datetime(2026, 8, 14, 20, 0, tzinfo=timezone.utc), source="FMP")


# --------------------------------------------------------------------------- #
# Construction
# --------------------------------------------------------------------------- #

def test_constructs_from_minor_units():
    """AC-M.1 — Money(int, currency) constructs."""
    m = Money(1500, CAD)
    assert (m.amount_minor, m.currency) == (1500, CAD)


@pytest.mark.parametrize("bad", [15.0, "15", Decimal("15"), True, None])
def test_non_int_amount_rejected(bad):
    """AC-M.1 — a bare/!int amount is not a monetary value (INV-001, MO-1).

    `True` is included deliberately: bool subclasses int, so a naive isinstance
    check accepts Money(True, "CAD") as one cent.
    """
    with pytest.raises(InvalidAmountError):
        Money(bad, CAD)


def test_unsupported_currency_raises_and_never_defaults():
    """AC-M.2 — never silently defaults to base."""
    with pytest.raises(UnsupportedCurrencyError) as e:
        Money(100, "EUR")
    assert "EUR" in str(e.value)
    assert BASE_CURRENCY == CAD and set(SUPPORTED_CURRENCIES) == {CAD, USD}


def test_currency_must_be_uppercase_alpha3():
    """AC-M.2 — 'usd' is not a currency code; it is a typo that would default."""
    with pytest.raises(UnsupportedCurrencyError):
        Money(100, "usd")


@pytest.mark.parametrize("text,expected", [
    ("15.00", 1500), ("0.01", 1), ("-3.07", -307), ("0", 0), ("0.00", 0),
    ("150.99", 15099), ("1000000.00", 100_000_000),
])
def test_from_decimal_str_is_exact(text, expected):
    """AC-M.3 — exact for every 2-dp value; no float on the path."""
    assert Money.from_decimal_str(text, USD).amount_minor == expected


def test_from_decimal_str_rejects_non_numeric():
    """AC-M.3 — unparseable input raises rather than becoming zero."""
    with pytest.raises(InvalidAmountError):
        Money.from_decimal_str("fifteen", USD)


def test_sub_cent_input_raises_rather_than_rounding():
    """AC-M.4 — '15.005' into a 2-dp currency is a caller bug, not a rounding request."""
    with pytest.raises(PrecisionLossError) as e:
        Money.from_decimal_str("15.005", USD)
    assert "15.005" in str(e.value)


def test_from_float_is_available_and_exact_via_str():
    """AC-M.3 — from_float routes through Decimal(str(x)); FMP returns JSON floats."""
    assert Money.from_float(15.0, USD).amount_minor == 1500
    assert Money.from_float(150.99, USD).amount_minor == 15099


def test_zero_is_currency_bearing():
    """AC-M.8 — there is no universal zero."""
    assert Money.zero(USD) != Money.zero(CAD)
    assert Money.zero(USD) == Money(0, USD)


# --------------------------------------------------------------------------- #
# Arithmetic and exactness
# --------------------------------------------------------------------------- #

def test_addition_of_hundred_cents_is_exactly_one_dollar():
    """AC-M.19 — the float trap: sum of 100 x 0.01 is exactly 1.00."""
    total = sum_money([Money.from_decimal_str("0.01", USD)] * 100, USD)
    assert total == Money(100, USD)


def test_multiplication_by_int_is_exact():
    """AC-M.7 — 150.99 x 3 is exact (0.1+0.2 territory for floats)."""
    assert Money.from_decimal_str("150.99", USD) * 3 == Money(45297, USD)


def test_mul_rate_rounds_half_up_not_bankers():
    """AC-M.7, AC-M.19 — the recorded legacy defect: 1.00 x 1.365 -> 1.37, not 1.36."""
    assert Money.from_decimal_str("1.00", USD).mul_rate(Decimal("1.365")) == Money(137, USD)


def test_mul_rate_accepts_an_explicit_mode():
    """AC-M.7, MO-3 — every lossy operation may name its rounding."""
    m = Money.from_decimal_str("1.00", USD)
    assert m.mul_rate(Decimal("1.365"), rounding=ROUND_DOWN) == Money(136, USD)


def test_half_up_applies_symmetrically_to_negatives():
    """MO-3/MO-6 — negatives are legal and must not round toward zero by accident."""
    assert Money(-100, USD).mul_rate(Decimal("1.365")) == Money(-137, USD)


def test_negation_and_abs():
    """MO-6 — no operation silently clamps to zero."""
    assert -Money(-250, CAD) == Money(250, CAD)
    assert abs(Money(-250, CAD)) == Money(250, CAD)


def test_multi_step_computation_quantizes_once():
    """AC-M.16 — quantizing per step accumulates error; quantize at the boundary.

    weight x price x quantity, done stepwise, drifts from the single-quantize
    answer. The module must expose the §4.3 pattern, not merely permit it.
    """
    price = Money.from_decimal_str("100.05", USD)
    stepwise = price.mul_rate(Decimal("0.333")).mul_rate(Decimal("0.333")) * 7
    once = Money.from_minor_decimal(
        Decimal(price.amount_minor) * Decimal("0.333") * Decimal("0.333") * 7, USD
    )
    assert once == Money(7766, USD)    # 10005 x .333 x .333 x 7 = 7766.111115
    assert stepwise == Money(7770, USD)  # quantized 3 times: 3332 -> 1110 -> 7770
    assert stepwise != once            # the whole reason the rule exists


# --------------------------------------------------------------------------- #
# Currency boundaries
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("op", [
    lambda a, b: a + b, lambda a, b: a - b,
    lambda a, b: a < b, lambda a, b: a <= b,
    lambda a, b: a > b, lambda a, b: a >= b,
    lambda a, b: a / b,
])
def test_cross_currency_operations_raise(op):
    """AC-M.5 — no implicit conversion, no allow_mixed flag, ever (MO-2)."""
    with pytest.raises(CurrencyMismatchError):
        op(Money(100, USD), Money(100, CAD))


def test_equality_across_currencies_is_false_and_does_not_raise():
    """AC-M.6 — __eq__ must tolerate any object or `in`, dict and set break."""
    assert (Money(100, USD) == Money(100, CAD)) is False
    assert Money(100, USD) != Money(100, CAD)
    assert Money(100, USD) != "not money"
    assert Money(100, USD) in {Money(100, USD), Money(100, CAD)}


def test_same_currency_ratio_is_dimensionless_and_leaves_the_type():
    """AC-M.20, MO-8 — division is where the Money type is left."""
    ratio = Money(200, USD) / Money(100, USD)
    assert not isinstance(ratio, Money)
    assert ratio == Decimal("2")


def test_hash_is_stable_and_currency_aware():
    """FR-004 — hash over (amount_minor, currency)."""
    assert hash(Money(100, USD)) == hash(Money(100, USD))
    assert len({Money(100, USD), Money(100, CAD)}) == 2


# --------------------------------------------------------------------------- #
# FX — the only path across a currency boundary
# --------------------------------------------------------------------------- #

def test_convert_is_the_only_currency_changing_operation():
    """AC-M.9 — 100.00 USD at 1.3742 -> 137.42 CAD."""
    got = Money.from_decimal_str("100.00", USD).convert(rate())
    assert got == Money(13742, CAD)


def test_convert_in_the_wrong_direction_raises():
    """AC-M.9 — a CAD amount cannot be converted by a USDCAD rate."""
    with pytest.raises(FxDirectionError):
        Money(100, CAD).convert(rate())


def test_fx_rate_exposes_its_direction():
    r = rate()
    assert (r.from_currency, r.to_currency) == (USD, CAD)


def test_fx_rate_rejects_an_unsupported_target():
    """AC-M.9 — the target currency must be supported."""
    with pytest.raises(UnsupportedCurrencyError):
        Money(100, USD).convert(rate(pair="USDEUR"))


def test_fx_rate_is_decimal_not_float():
    """FR-005 — a float rate multiplies every converted amount in the book."""
    with pytest.raises(InvalidAmountError):
        FxRate(pair="USDCAD", rate=1.3742,
               as_of=datetime.now(timezone.utc), source="FMP")


# --------------------------------------------------------------------------- #
# sum_money
# --------------------------------------------------------------------------- #

def test_sum_money_requires_a_currency_and_answers_the_empty_case():
    """AC-M.12 — sum([]) returns 0, which has no currency (QM-1)."""
    assert sum_money([], USD) == Money.zero(USD)


def test_sum_money_rejects_a_mixed_list():
    """AC-M.12 — a mixed list is an immediate error, not a plausible total."""
    with pytest.raises(CurrencyMismatchError):
        sum_money([Money(1, USD), Money(1, CAD)], USD)


def test_sum_money_asserts_the_callers_expectation():
    """AC-M.12 — the currency argument also asserts what the caller believes."""
    with pytest.raises(CurrencyMismatchError):
        sum_money([Money(1, USD)], CAD)


# --------------------------------------------------------------------------- #
# On-disk representation
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("m", [
    Money(41900, USD), Money(0, CAD), Money(-1, USD), Money(-99999999, CAD),
])
def test_parquet_round_trip_is_identity(m):
    """AC-M.13 — CT-M.1, two columns: *_minor int64 + *_currency string."""
    fields = m.to_parquet_fields("price")
    assert set(fields) == {"price_minor", "price_currency"}
    assert isinstance(fields["price_minor"], int)
    assert Money.from_parquet_fields(fields, "price") == m


@pytest.mark.parametrize("m", [Money(41900, USD), Money(0, CAD), Money(-1, USD)])
def test_json_round_trip_is_identity(m):
    """AC-M.15 — CT-M.2, a nested object that a careless field selection cannot split."""
    obj = m.to_json_obj()
    assert obj == {"minor": m.amount_minor, "currency": m.currency}
    assert Money.from_json_obj(obj) == m


def test_fx_rate_serialises_its_rate_as_a_string():
    """AC-M.15 — a JSON float would not survive the round trip (CT-M.3)."""
    obj = rate().to_json_obj()
    assert obj["rate"] == "1.3742" and isinstance(obj["rate"], str)
    assert FxRate.from_json_obj(obj) == rate()


def test_converted_artifact_carries_its_rate():
    """AC-M.10 — FX-2: a converted number without its rate is not reproducible.

    Money supports the obligation; it cannot enforce it alone, because the
    artifact belongs to the calling domain. What is testable here is that the
    helper emits both halves together.
    """
    r = rate()
    obj = Money.from_decimal_str("100.00", USD).convert_with_record(r, "nav_base")
    assert obj["nav_base"] == {"minor": 13742, "currency": CAD}
    assert obj["fx_rate_used"]["pair"] == "USDCAD"
    assert obj["fx_rate_used"]["rate"] == "1.3742"


def test_no_rate_means_no_number():
    """AC-M.11 — FX-3: the rule most likely to be eroded under pressure.

    A missing NAV looks like a bug, so the temptation is yesterday's rate. A
    NAV that is quietly wrong is worse than one that is visibly absent.
    """
    with pytest.raises(TypeError):
        Money(100, USD).convert(None)


# --------------------------------------------------------------------------- #
# Properties
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("a,b", [(0, 0), (1, -1), (12345, 67890), (-5, -7)])
def test_algebraic_properties(a, b):
    """§7 Property — a + b - b == a; a + b == b + a; zero is the identity."""
    x, y = Money(a, USD), Money(b, USD)
    assert x + y - y == x
    assert x + y == y + x
    assert Money.zero(USD) + x == x


def test_module_imports_nothing_from_another_domain():
    """AC-M.17, SI-1 — enforced tree-wide by test_architecture, asserted here too."""
    from tests_src.architecture import imports_of
    from pathlib import Path

    src = Path(__file__).resolve().parents[1] / "src" / "shared" / "money.py"
    for mod in imports_of(src.read_text(encoding="utf-8")):
        assert not mod.startswith("src.") or mod.startswith("src.shared."), mod
