"""D-03 §5.6a / §7.1 — the cost model. QA-12, QA-48, QA-49, QA-50.

★★ **QA-50: `charge_transaction_cost` MUST default to `true`.** A backtest
accounts for whatever cost model exists, and the result records **which
components were charged**.

⚠ **QA-49 stays open: spread and slippage are unmodelled.** So the honest label
is `commission_only`, and it travels on every result — *a gross-of-cost result
may be shown beside a net one, never instead* (QA-12).

★★ **The flat fee is `9.95`, MEASURED — not the `10.00` the legacy constant
asserts.** `backtester.py:14-18` reads *"BROKER REALITY: flat $10 per trade"*,
and 137 real BMO orders (2022-01-01 → 2026-08-25) put it at **9.95 exactly on
100 of them, in CAD and USD alike** (D-11 RC-43). ⚠ The 0.5 % error is trivial
per trade and is **not** trivial in the place §5.6a uses it: the horizon
argument turns on a cost *differential*, and an unsourced constant doing
load-bearing work is exactly what **QA-48** exists to catch.
"""

from __future__ import annotations

from dataclasses import dataclass

COMMISSION_ONLY, FULL = "commission_only", "full"

#: L4 **CN-2** — a world-fact constant carries its source and check date.
#: **BMO InvestorLine flat equity commission, CAD and USD. Measured over 137
#: real orders, checked 2026-08-25** (D-11 RC-43). ⚠ Supersedes the legacy
#: `10.00` at `backtester.py:14`, which was asserted rather than measured.
FLAT_COMMISSION = 9.95

#: ⚠ **QA-48**: `settings.yaml:55` asserts *"$20 round-trip immaterial at
#: realistic capital"* **without stating what realistic capital is** — an
#: undeclared convention doing load-bearing work. There is no default here.
NO_DEFAULT_CAPITAL = None


@dataclass(frozen=True, slots=True)
class CostModel:
    """★ QA-50 — charging is **on** unless someone turns it off in writing."""

    flat_commission: float = FLAT_COMMISSION
    charge_transaction_cost: bool = True
    #: ⚠ QA-49 — until spread and slippage are modelled, this is the truth.
    components: str = COMMISSION_ONLY
    #: §5.6a: ground (b) flips sign at 3–12 bps of proportional cost, so the
    #: field exists to make that testable — it is **0.0 and stated**, not absent.
    proportional_bps: float = 0.0

    def charge(self, *, notional: float, sides: int = 1) -> float:
        """`sides=2` for a round trip. ⚠ Held positions incur no fee — which the
        legacy `_reconcile_bucket` docstring said and its code did not."""
        if not self.charge_transaction_cost:
            return 0.0
        return (self.flat_commission * sides
                + notional * self.proportional_bps / 10_000.0 * sides)

    def annual_drag_pct(self, *, capital: float, trades_per_year: float,
                        avg_notional: float) -> float:
        """★★ §7.1's reason `initial_capital` is pinned.

        ⚠ *A flat per-trade fee's drag in percentage terms depends entirely on
        the book*: **1.20 %/yr at 1m on $100 k, 0.12 % on $1 M — a 10× spread on
        the same strategy.** Two backtests that differ only in an unstated
        capital base are not comparable.
        """
        from src.quant.errors import QuantError

        if not capital:
            raise QuantError(
                "annual drag needs the capital base. ★ QA-48: an undeclared "
                "'realistic capital' is a convention doing load-bearing work")
        return 100.0 * self.charge(notional=avg_notional,
                                   sides=2) * trades_per_year / capital

    def to_json_obj(self) -> dict:
        return {"flat_commission": self.flat_commission,
                "charge_transaction_cost": self.charge_transaction_cost,
                "costs_charged": self.components,
                "proportional_bps": self.proportional_bps,
                "source": ("BMO InvestorLine, measured over 137 real orders, "
                           "2026-08-25 (D-11 RC-43) — CN-2")}
