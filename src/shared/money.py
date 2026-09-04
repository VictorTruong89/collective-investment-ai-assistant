"""Money — an exact amount inseparable from its currency.

Spec: `sdd/design/rel6_design/L2-shared-money.md` (INV-001, M-5, constitution INV-5).

WHY A TYPE AND NOT A CONVENTION
-------------------------------
The semantics are not new: constitution INV-5 has required explicit currency
since before this redesign, and `portfolio_state.json` already records
`fx_rate_used`. What never existed is a *type* — currency travelled as a sibling
string next to a float, by convention, in each place that remembered.

`pipeline/portfolio/money.py` is the prior art (P4) and it is a **function
library over floats**: `quantize`, `convert`, `add` all return `Optional[float]`
and none of them knows a currency. What carries across is its exactness
discipline, not its API — see AC-M.19's recorded defect: `1.00 x 1.365` returned
1.36 where money arithmetic gives 1.37, because `float(rate)` carries binary
representation error and the builtin `round()` is BANKER'S rounding. Those
errors were systematically DOWNWARD, so they did not cancel across many
conversions the way symmetric noise would.

⚠ SPEC DISCREPANCY, recorded rather than silently resolved (constitution §5):
`FR-002` says a same-currency ratio returns **Decimal**; `MO-8` says "a plain
float". This module returns **Decimal**, because FR-002 is the functional
contract and `AC-M.20` says only "dimensionless and leaves the Money type" —
which Decimal satisfies exactly, and without reintroducing the float MO-4 exists
to keep away. MO-8's point is that division is where the type is left, not that
the result must be binary. Flagged for the spec to settle.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Iterable

from src.shared.errors import (
    CurrencyMismatchError,
    FxDirectionError,
    InvalidAmountError,
    PrecisionLossError,
    UnsupportedCurrencyError,
)

#: code → minor-unit exponent. A TABLE, not the constant 2: a zero-decimal
#: currency (JPY) or three-decimal one (KWD) would otherwise be silently wrong
#: by a factor of 100 the day one is added.
SUPPORTED_CURRENCIES: dict[str, int] = {"CAD": 2, "USD": 2}

#: M-5. The base the book is reported in — never a fallback for an untagged
#: amount, which is a defect (INV-001).
BASE_CURRENCY: str = "CAD"

_ONE = Decimal(1)


def _check_currency(code: object) -> str:
    if not isinstance(code, str) or code not in SUPPORTED_CURRENCIES:
        raise UnsupportedCurrencyError(code, SUPPORTED_CURRENCIES)
    return code


def _quantize_to_int(value: Decimal, rounding: str = ROUND_HALF_UP) -> int:
    """The single place a Decimal becomes stored minor units (MO-5)."""
    return int(value.quantize(_ONE, rounding=rounding))


@dataclass(frozen=True, slots=True)
class Money:
    """An exact monetary amount, inseparable from its currency (INV-001).

    amount_minor: signed integer in the currency's minor unit. Negative is
                  legal — a debit, a loss, or a short cash balance (MO-6).
    currency:     ISO-4217 alpha-3, uppercase, in SUPPORTED_CURRENCIES.

    Frozen because a value that can be mutated in place can be mutated by one
    holder and observed by another. Every operation returns a new Money.
    """

    amount_minor: int
    currency: str

    def __post_init__(self) -> None:
        # `type(...) is not int` and not isinstance: bool subclasses int, so
        # isinstance would accept Money(True, "CAD") as one cent.
        if type(self.amount_minor) is not int:
            raise InvalidAmountError(
                f"amount_minor must be an int of minor units, got "
                f"{type(self.amount_minor).__name__} {self.amount_minor!r} — "
                f"a bare value is not a monetary value (MO-1, INV-001)"
            )
        _check_currency(self.currency)

    # ---- construction (FR-001) -------------------------------------------- #

    @classmethod
    def zero(cls, currency: str) -> "Money":
        """An explicit zero IN a currency. There is no currency-free zero (§4.4)."""
        return cls(0, _check_currency(currency))

    @classmethod
    def from_decimal_str(cls, text: str, currency: str) -> "Money":
        """The preferred boundary constructor — exact, and no float ever exists."""
        _check_currency(currency)
        exponent = SUPPORTED_CURRENCIES[currency]
        try:
            value = Decimal(str(text))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise InvalidAmountError(f"cannot parse {text!r} as a decimal amount") from exc
        if value != value:  # NaN compares unequal to itself
            raise InvalidAmountError(f"{text!r} is not a finite amount")
        if -value.as_tuple().exponent > exponent:
            raise PrecisionLossError(str(text), currency, exponent)
        return cls(_quantize_to_int(value.scaleb(exponent)), currency)

    @classmethod
    def from_float(cls, value: float, currency: str) -> "Money":
        """External data that is already a float — FMP returns JSON floats.

        Deliberately named so it stays greppable (QM-2). Routes through
        `Decimal(str(x))` so the float's binary error is not carried inward.
        """
        return cls.from_decimal_str(str(value), currency)

    @classmethod
    def from_minor_decimal(
        cls, value: Decimal, currency: str, rounding: str = ROUND_HALF_UP
    ) -> "Money":
        """Quantize a multi-step Decimal computation ONCE, at the boundary (§4.3, AC-M.16).

        Carry Decimal through `weight × price × quantity × fx` and call this at
        the end. Quantizing at each step accumulates error.
        """
        _check_currency(currency)
        if not isinstance(value, Decimal):
            raise InvalidAmountError(f"expected Decimal, got {type(value).__name__}")
        return cls(_quantize_to_int(value, rounding), currency)

    # ---- arithmetic (FR-002, FR-003) --------------------------------------- #

    def _same_currency(self, other: "Money", operation: str) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(self.currency, other.currency, operation)

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other, "add")
        return Money(self.amount_minor + other.amount_minor, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other, "subtract")
        return Money(self.amount_minor - other.amount_minor, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount_minor, self.currency)

    def __abs__(self) -> "Money":
        return Money(abs(self.amount_minor), self.currency)

    def __mul__(self, n: int) -> "Money":
        """Exact: share counts, periods. A rate goes through `mul_rate` (FR-003)."""
        if type(n) is not int:
            return NotImplemented
        return Money(self.amount_minor * n, self.currency)

    __rmul__ = __mul__

    def __truediv__(self, other):
        """`/ int` → Money (rounded); `/ Money` → Decimal ratio (MO-8, AC-M.20)."""
        if isinstance(other, Money):
            self._same_currency(other, "take a ratio of")
            return Decimal(self.amount_minor) / Decimal(other.amount_minor)
        if type(other) is int:
            return self.div_int(other)
        return NotImplemented

    def div_int(self, n: int, rounding: str = ROUND_HALF_UP) -> "Money":
        """Divide by a count, naming the rounding mode (MO-3)."""
        return Money(
            _quantize_to_int(Decimal(self.amount_minor) / Decimal(n), rounding), self.currency
        )

    def mul_rate(self, rate: Decimal, rounding: str = ROUND_HALF_UP) -> "Money":
        """Multiply by a rate or weight — lossy, so the mode is named (FR-003, MO-3).

        Separate from `*` because `* int` is exact and `* rate` is not; sharing
        one operator would let a lossy operation look identical to an exact one
        at the call site.
        """
        if not isinstance(rate, Decimal):
            raise InvalidAmountError(
                f"rate must be Decimal, got {type(rate).__name__} — a float rate "
                f"carries binary representation error into every converted amount"
            )
        return Money(
            _quantize_to_int(Decimal(self.amount_minor) * rate, rounding), self.currency
        )

    # ---- comparison (FR-004) ----------------------------------------------- #
    #
    # The asymmetry is deliberate. Python requires __eq__ to tolerate any object
    # — raising would break `in`, dict, set and every assertEqual. Ordering
    # carries no such requirement, and "is this USD amount bigger than that CAD
    # amount" has no answer, so it fails loudly.
    #
    # __eq__ and __hash__ come from the frozen dataclass: they compare and hash
    # (amount_minor, currency), which already returns False across currencies
    # without raising.

    def _compare(self, other: "Money", op: str):
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other, f"order ({op})")
        return None

    def __lt__(self, other: "Money"):
        r = self._compare(other, "<")
        return r if r is NotImplemented else self.amount_minor < other.amount_minor

    def __le__(self, other: "Money"):
        r = self._compare(other, "<=")
        return r if r is NotImplemented else self.amount_minor <= other.amount_minor

    def __gt__(self, other: "Money"):
        r = self._compare(other, ">")
        return r if r is NotImplemented else self.amount_minor > other.amount_minor

    def __ge__(self, other: "Money"):
        r = self._compare(other, ">=")
        return r if r is NotImplemented else self.amount_minor >= other.amount_minor

    # ---- FX (FR-005) -------------------------------------------------------- #

    def convert(self, rate: "FxRate") -> "Money":
        """The ONLY way a Money changes currency (FX-1, MO-7).

        FX-3 — no rate means no number — is the caller's obligation: this raises
        rather than accepting `None`, so a missing rate cannot become a quietly
        wrong NAV. A NAV that is visibly absent beats one that is quietly wrong.
        """
        if not isinstance(rate, FxRate):
            raise TypeError(
                f"convert() requires an FxRate, got {type(rate).__name__} — "
                f"with no rate the dependent value is UNAVAILABLE, never computed "
                f"from a stale or assumed rate (FX-3)"
            )
        if rate.from_currency != self.currency:
            raise FxDirectionError(self.currency, rate.pair)
        _check_currency(rate.to_currency)
        return Money(
            _quantize_to_int(Decimal(self.amount_minor) * rate.rate), rate.to_currency
        )

    def convert_with_record(self, rate: "FxRate", field: str) -> dict:
        """Convert AND emit the rate beside it (FX-2, CT-M.3, AC-M.10).

        A converted number without its rate is not reproducible, and
        reproducibility is the point (AP-6). The obligation belongs to the
        artifact's owning domain; this emits both halves together so the two
        cannot be separated by accident.
        """
        return {field: self.convert(rate).to_json_obj(), "fx_rate_used": rate.to_json_obj()}

    # ---- on-disk (CT-M.1, CT-M.2) ------------------------------------------ #

    def to_parquet_fields(self, name: str) -> dict:
        """Two columns, not a struct: filterable and groupable without unnesting."""
        return {f"{name}_minor": self.amount_minor, f"{name}_currency": self.currency}

    @classmethod
    def from_parquet_fields(cls, fields: dict, name: str) -> "Money":
        try:
            return cls(int(fields[f"{name}_minor"]), fields[f"{name}_currency"])
        except KeyError as exc:
            raise InvalidAmountError(
                f"{name}_minor without its {name}_currency sibling is a schema "
                f"violation, not a default-to-base (CT-M.1)"
            ) from exc

    def to_json_obj(self) -> dict:
        """A nested object, so a careless field selection cannot split the pair."""
        return {"minor": self.amount_minor, "currency": self.currency}

    @classmethod
    def from_json_obj(cls, obj: dict) -> "Money":
        return cls(int(obj["minor"]), obj["currency"])


@dataclass(frozen=True, slots=True)
class FxRate:
    """An observed rate. `rate` is Decimal because it multiplies every converted
    amount in the book, so a float's representation error is applied at scale."""

    pair: str            # "USDCAD" — converts FROM the first code TO the second
    rate: Decimal        # units of `to` per 1 unit of `from`
    as_of: datetime      # UTC, when observed
    source: str          # e.g. "FMP"

    def __post_init__(self) -> None:
        if not isinstance(self.rate, Decimal):
            raise InvalidAmountError(
                f"FxRate.rate must be Decimal, got {type(self.rate).__name__} — a "
                f"float rate multiplies every converted amount in the book"
            )
        if not isinstance(self.pair, str) or len(self.pair) != 6:
            raise InvalidAmountError(f"pair must be six characters, got {self.pair!r}")

    @property
    def from_currency(self) -> str:
        return self.pair[:3]

    @property
    def to_currency(self) -> str:
        return self.pair[3:]

    def to_json_obj(self) -> dict:
        """`rate` serialises as a STRING — a JSON float would not round-trip (CT-M.3)."""
        return {
            "pair": self.pair,
            "rate": str(self.rate),
            "as_of": self.as_of.isoformat(),
            "source": self.source,
        }

    @classmethod
    def from_json_obj(cls, obj: dict) -> "FxRate":
        return cls(
            pair=obj["pair"],
            rate=Decimal(obj["rate"]),
            as_of=datetime.fromisoformat(obj["as_of"]),
            source=obj["source"],
        )


def sum_money(items: Iterable[Money], currency: str) -> Money:
    """Sum same-currency amounts. `currency` is REQUIRED (FR-006, AC-M.12).

    It is the answer for an empty iterable — `sum([])` returns `0`, which has no
    currency and is exactly the untagged value INV-001 forbids — and for a
    non-empty one it asserts the caller's expectation, turning a mixed list into
    an immediate error rather than a plausible total.
    """
    _check_currency(currency)
    total = 0
    for item in items:
        if not isinstance(item, Money):
            raise InvalidAmountError(f"sum_money expects Money, got {type(item).__name__}")
        if item.currency != currency:
            raise CurrencyMismatchError(currency, item.currency, "sum")
        total += item.amount_minor
    return Money(total, currency)
