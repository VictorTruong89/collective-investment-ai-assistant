"""D-11 §7/§8 — `CT-11.4 BookState`, the book D-05 measures. RC-1…RC-10, RC-19.

★ **B5's prerequisite (BS-15b), and it was assigned to no milestone.** B1 built
*"enough of D-11 to hold"* the journal, calibration and counterfactual store;
BS-9 says the capital base *"lands with D-11's book, before B4"* while binding
only the SOURCE — so nobody owned the book and B4 shipped without it.

⚠ **RC-9: the book is DERIVED from activity and reconciled against the export,
never read from it.** ★ RC-10 is the whole of that reconciliation:
`sum(positions) + cash == NAV` per currency, per account, every day — **a break
raises; it is never absorbed.**
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

#: RC-10's outcomes. ⚠ There is no third value: a book is reconciled or it is a
#: break, and D-05's step 0 turns on exactly this field (RK-0, RK-29).
OK, BREAK = "ok", "break"
RECONCILED = (OK, BREAK)

#: D-11 §5.5 / RC-25 — **all four accounts are registered.** ★ M-4 therefore has
#: no exempt population, and any design routing tactical activity to a
#: "non-registered sleeve" is describing an account that does not exist.
REGISTERED_TYPES = ("TFSA", "RRSP", "RESP", "FHSA")

#: RC-4 — ★ **an RESP is not the fund.** It has a beneficiary and its own
#: mandate; it is recorded, and **excluded from the fund's performance and
#: exposure** unless Victor says otherwise (QC-1).
EXCLUDED_FROM_FUND = ("RESP",)

#: RC-10's tolerance. Money is exact (L2-shared-money), so this exists only for
#: callers passing floats; a Decimal book reconciles at zero.
RECONCILE_TOLERANCE = 0.005


@dataclass(frozen=True, slots=True)
class Position:
    """One lot in the book.

    ★ **RC-16/RC-28: analysis identity and settlement identity are separate
    fields.** `analysis_symbol` is the underlying US ticker — what D-02/D-03/D-04
    see; `instrument_id` is what the book holds. ⚠ **A CDR and its underlying are
    the same company and different lots**, and D-05 **RK-5** must aggregate them:
    holding `MU` as a CDR in the RRSP and as the US stock in a TFSA is *one
    position in Micron*, and reporting them separately understates concentration
    by exactly the amount that matters.
    """

    instrument_id: str            # (symbol, wrapper, venue_currency), rendered
    analysis_symbol: str          # the underlying US ticker
    quantity: float
    market_value: float           # in `currency`
    currency: str
    account_id: str
    sector: str = ""              # ★ from D-02 — sector, never theme (RK-37)
    average_cost: float | None = None
    opened_on: date | None = None

    def __post_init__(self) -> None:
        if not self.analysis_symbol:
            raise ValueError(
                f"{self.instrument_id!r} carries no analysis_symbol. ★ RC-28 "
                f"keeps the two identities separate precisely so a CDR can be "
                f"aggregated with its underlying (RC-16, D-05 RK-5)"
            )

    def to_json_obj(self) -> dict:
        return {"instrument_id": self.instrument_id,
                "analysis_symbol": self.analysis_symbol,
                "quantity": self.quantity, "market_value": self.market_value,
                "currency": self.currency, "account_id": self.account_id,
                "sector": self.sector, "average_cost": self.average_cost,
                "opened_on": self.opened_on.isoformat() if self.opened_on else None}


@dataclass(frozen=True, slots=True)
class Break:
    """One RC-10 failure, named. ⚠ *A break raises; it is never absorbed.*"""

    account_id: str
    currency: str
    computed: float
    reported: float

    @property
    def delta(self) -> float:
        return self.computed - self.reported

    def __str__(self) -> str:
        return (f"{self.account_id}/{self.currency}: positions+cash="
                f"{self.computed:.2f} vs NAV={self.reported:.2f} "
                f"(delta {self.delta:+.2f})")

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "currency": self.currency,
                "computed": self.computed, "reported": self.reported,
                "delta": self.delta}


@dataclass(frozen=True, slots=True)
class BookState:
    """CT-11.4 — one account, one day.

    ⚠ **`nav_base` is `null` when no FX rate is available — never a guess**
    (FX-3, inherited from `snapshot.py`). D-05 **RK-3** then reports the
    cross-currency aggregate as *unavailable*, not as zero.
    """

    account_id: str
    date: date
    positions: tuple[Position, ...]
    cash_by_currency: dict
    nav_by_currency: dict
    base_currency: str = "CAD"
    nav_base: float | None = None
    fx_rate_used: dict = field(default_factory=dict)
    capital_base: float | None = None
    reconciled: str = OK
    breaks: tuple[Break, ...] = ()
    account_type: str = "TFSA"
    #: RC-75 — where the figures came from: `derived` (transactions, RC-9) or
    #: `holdings_export` (BMO's reported values, RC-70).
    source: str = "derived"

    def __post_init__(self) -> None:
        if self.reconciled not in RECONCILED:
            raise ValueError(
                f"reconciled={self.reconciled!r} is not one of {RECONCILED}. "
                f"★ There is no third state, and D-05's step 0 turns on this "
                f"field alone (RC-10, RK-0)"
            )
        if self.account_type not in REGISTERED_TYPES:
            raise ValueError(
                f"account_type {self.account_type!r} is not one of "
                f"{REGISTERED_TYPES}. ★ All four accounts are registered "
                f"(RC-25) — M-4 has no exempt population"
            )
        if self.reconciled == BREAK and not self.breaks:
            raise ValueError(
                f"{self.account_id}: reconciled='break' with no breaks listed. "
                f"⚠ A break that cannot say what broke has absorbed itself "
                f"(RC-10, P5)"
            )

    @property
    def in_fund(self) -> bool:
        """RC-4 — ★ and the exclusion is **stated**, never assumed (AC-5.5)."""
        return self.account_type not in EXCLUDED_FROM_FUND

    def to_json_obj(self) -> dict:
        return {
            "account_id": self.account_id, "date": self.date.isoformat(),
            "account_type": self.account_type, "in_fund": self.in_fund,
            "positions": [p.to_json_obj() for p in self.positions],
            "cash_by_currency": dict(self.cash_by_currency),
            "nav_by_currency": dict(self.nav_by_currency),
            "base_currency": self.base_currency, "nav_base": self.nav_base,
            "fx_rate_used": dict(self.fx_rate_used),
            "capital_base": self.capital_base, "reconciled": self.reconciled,
            "breaks": [b.to_json_obj() for b in self.breaks],
            "source": self.source,
        }
