"""D-11 §8 — BMO InvestorLine ingestion. RC-9…RC-18, RC-41…RC-49.

★ **Every known answer here comes from the four REAL exports**, re-pulled
2026-08-25 from each account's inception (`From=2022-01-01`). `CT-3.2` is the
reason: *run the money path against external truth from outside this
repository.*

⚠ **The broker is BMO InvestorLine.** "CIBC" in this data is the CDR issuer and
belongs to the INSTRUMENT, never to the account (**RC-36**, §5.3 **H-0**).

★ **The longer history found five activity types the eight-month window did
not** — `Harmonized sales tax`, `Admin fee charged`, `Withdrawal`,
`Disbursement`, `Online banking` — each caught by RC-13 rather than absorbed.

Tier: unit + reality-probe (constitution §4, F3 Tier 1).
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path

import pytest

from src.recording.errors import (
    CommissionImplausibleError, ForeignAccountRowError, TruncatedWindowError,
    UnclassifiableActivityError,
)
from src.recording.orders.group import (
    BMO_FLAT_COMMISSION, derive_commission, group_orders, implied_orders,
)
from src.recording.reconcile.ingest import (
    KNOWN_ACTIVITIES, POSITION_MOVING_NON_TRADE, Activity, file_hash,
    parse_export,
)
from src.recording.reconcile.opening import derive_positions
from tests_src.broker_fixtures import requires_real_statements

# ⚠⚠ DX-5 — every test below reads the REAL BMO exports, which are NOT in git.
# They check derived numbers against EXTERNAL TRUTH (CT-3.2) — which is exactly
# what makes them worth having, and exactly why they cannot be synthesised: a
# synthetic external-truth check asserts a property of invented data while
# LOOKING like validation. So they skip loudly instead.
#
# ★ Structural parsing — column layouts, zero totals, dotted tickers, unknown
#   activities, foreign rows, CDR-vs-common — IS covered on any clone by
#   tests_src/test_recording_ingest_synthetic.py against tracked fixtures.
pytestmark = requires_real_statements



EXPORTS = Path("sdd/design/rel6_design/samples/bmo_investorline_transactions")
ACCOUNTS = ("TFSA_1", "TFSA_2", "RRSP_1", "RESP_1")

#: ⚠ RC-48 — `TFSA_2`'s export carries one row from a **Joint** account. Skipping
#: it is deliberate and must stay visible; `strict_accounts=True` elsewhere.
FOREIGN_ROW_ACCOUNT = ""   # ★ cleared 2026-08-25: Victor removed the Joint row


def export(account: str) -> Path:
    return EXPORTS / f"TransactionHistory_{account}.csv"


def activities(account: str):
    return parse_export(export(account), account_id=account,
                        strict_accounts=account != FOREIGN_ROW_ACCOUNT)


def orders(account: str, **kw):
    return group_orders(activities(account), **kw)


def every_order():
    return [o for a in ACCOUNTS for o in orders(a)]


def find(account: str, day: str, symbol: str):
    return [o for o in orders(account) if str(o.trade_date) == day
            and o.symbol == symbol]


# --------------------------------------------------------------------------- #
# The whole book parses and reconciles
# --------------------------------------------------------------------------- #

def test_all_four_accounts_parse_completely():
    """RC-1/RC-3 — every row attributed; a missing account is an incomplete
    book, not a smaller one."""
    counts = {a: len(activities(a)) for a in ACCOUNTS}
    assert counts == {"TFSA_1": 163, "TFSA_2": 149, "RRSP_1": 105, "RESP_1": 61}
    assert sum(counts.values()) == 478


def test_the_full_history_derives_a_book_with_no_negative_position():
    """★★ RC-45, the finding that sent the exports back — **now clear.**

    ⚠ The eight-month window produced `AVGO −1000`, `PLTR −520` and seven more:
    lots opened before the window, whose sells were in the file and whose buys
    were not. **The cash still balanced**, so nothing else would have noticed.
    From inception, every position is non-negative.
    """
    derived = derive_positions(every_order() + list(_non_trade_moves()))
    assert derived.origin == "activity_from_inception"
    assert len(derived.quantities) == 16
    assert all(q > 0 for q in derived.quantities.values())


def _non_trade_moves():
    return [a for account in ACCOUNTS for a in activities(account)
            if a.moves_position and not a.is_trade]


# --------------------------------------------------------------------------- #
# RC-13 — the fail-loud that keeps finding things
# --------------------------------------------------------------------------- #

def test_rc13_the_longer_history_contained_five_unknown_activity_types():
    """RC-13 — ★ *no neutral default, no silent drop.*

    ⚠ Eight months of history showed seven activity types; **four years showed
    twelve.** Every one of the five new ones stopped the run on first parse
    rather than vanishing from a book that has to balance.
    """
    for late in ("Harmonized sales tax", "Admin fee charged", "Withdrawal",
                 "Disbursement", "Online banking"):
        assert late in KNOWN_ACTIVITIES, late
    assert len(KNOWN_ACTIVITIES) == 13


def test_an_unknown_activity_raises_rather_than_being_dropped():
    """RC-13 — the planted violation (IM-3, BS-5)."""
    import tempfile

    rows = export("TFSA_1").read_text(encoding="utf-8-sig").splitlines()
    rows.append("2026-08-18,2026-08-19,Journalled Shares,SOMETHING,XYZ,1,1,CAD,-1,CAD")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        fh.write("\n".join(rows))
        path = fh.name
    with pytest.raises(UnclassifiableActivityError, match="Journalled Shares"):
        parse_export(path, account_id="TFSA_1")


def test_rc49_a_disbursement_moves_shares_and_carries_no_cash():
    """★★ RC-49 — ⚠ `PLTR 390 @ 0, total 0` in the RESP.

    Treating it as cash-only would **lose 390 shares** while the cash still
    balanced — RC-45's failure shape from a different cause. ★ The **sign is
    taken from the file, never inferred**: BMO signs dispositions negative
    throughout, and the book only reconciles with the positive reading.
    """
    assert POSITION_MOVING_NON_TRADE == {"Disbursement"}
    moves = list(_non_trade_moves())
    assert len(moves) == 1
    (move,) = moves
    assert (move.account_id, move.symbol, move.quantity) == ("RESP_1", "PLTR", 390.0)
    assert move.total_amount == 0.0 and move.price == 0.0
    assert move.moves_position and not move.is_trade


# --------------------------------------------------------------------------- #
# RC-41 / RC-48 — the file's own shape
# --------------------------------------------------------------------------- #

def test_rc41_both_column_layouts_parse_to_the_same_canonical_fields():
    """RC-41 — ★ `TFSA_2` carries **13 columns**; the others carry **10**.

    ⚠ A positional parser reads `Account name` where `Activity Description`
    belongs and **silently mis-books every row of that file.**
    """
    assert len(export("TFSA_2").read_text(encoding="utf-8-sig")
               .splitlines()[1].split(",")) == 13
    assert len(export("TFSA_1").read_text(encoding="utf-8-sig")
               .splitlines()[1].split(",")) == 10
    for row in list(activities("TFSA_2"))[:5] + list(activities("TFSA_1"))[:5]:
        assert isinstance(row, Activity)
        assert row.activity in KNOWN_ACTIVITIES and row.trade_date


def test_rc48_a_row_from_another_account_is_refused_never_absorbed():
    """★★ RC-48 — the guard that found a foreign row in a real export.

    ⚠ `TransactionHistory_TFSA_2.csv` was about account `23280100` and carried
    **one `Joint` row** (`23098925`) — a $0.50 transfer from 2022. Booking it
    into the TFSA attributes another account's cash to this one, **and the
    principle is RC-1's.** Victor removed the row on 2026-08-25, so the real
    exports are clean; the guard is exercised on a synthetic one, because *a
    check nobody can fire is a check nobody can trust*.
    """
    import tempfile

    lines = export("TFSA_2").read_text(encoding="utf-8-sig").splitlines()
    lines.append("2022-02-02,2022-02-02,SOMEONE ELSE,Joint,23098925,"
                 "Online banking,TF 2374,,0,0,,0.5,CAD")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        fh.write("\n".join(lines))
        path = fh.name
    with pytest.raises(ForeignAccountRowError, match="23098925"):
        parse_export(path, account_id="TFSA_2")
    # ★ Skipping it is possible, and must be deliberate.
    assert len(parse_export(path, account_id="TFSA_2",
                            strict_accounts=False)) == 149


def test_rc36_cibc_marks_the_instrument_never_the_account():
    """RC-36 / H-0 — ★ **the broker is BMO InvestorLine.**"""
    cdrs = [a for a in activities("RRSP_1") if a.is_cdr]
    assert cdrs
    for row in cdrs[:3]:
        assert row.instrument_id.endswith("|CDR|CAD")
        assert row.analysis_symbol == row.symbol.upper()
        assert "CIBC" not in row.account_id


def test_rc46_a_dotted_ticker_survives_the_instrument_id():
    """RC-46 — ★ `BBD.B` is a real holding, and `BBD.B.COMMON.CAD` cannot be
    split back into RC-16's `(symbol, wrapper, venue_currency)`."""
    dotted = [o for o in every_order() if "." in o.symbol]
    assert {o.symbol for o in dotted} == {"BBD.B"}
    symbol, wrapper, currency = dotted[0].instrument_id.split("|")
    assert symbol == "BBD.B" and wrapper in ("COMMON", "CDR") and currency


# --------------------------------------------------------------------------- #
# RC-42 / RC-15 — grouping and the derived fee
# --------------------------------------------------------------------------- #

def test_rc42_nvda_two_tranches_group_to_one_order_at_exactly_9_95():
    """★★ **The known answer.**

    ```
    2026-04-29  Buy NVDA CDR  200 @ 47.68   total -9545.48   -> 9.48
    2026-04-29  Buy NVDA CDR   10 @ 47.69   total  -477.37   -> 0.47
                                              grouped        -> 9.95
    ```

    ⚠ Keyed on price these are two orders whose residuals are meaningless.
    **The grouping is what makes the fee derivable at all.**
    """
    (order,) = find("TFSA_2", "2026-04-29", "NVDA")
    assert (order.tranches, order.quantity) == (2, 210)
    assert order.commission == pytest.approx(BMO_FLAT_COMMISSION, abs=0.005)


def test_rc12_a_zero_total_amount_is_a_tranche_not_an_absence():
    """RC-12, H-1 — ★★ *a zero `Total Amount` is a **tranche**, not an absence.*

    ```
    2026-05-06  Buy MU CDR  250 @ 29.02   total -15967.95   <- all the cash
    2026-05-06  Buy MU CDR  300 @ 29.01   total       0     <- and 300 shares
    ```

    ⚠ Dropping the zero row loses **300 shares** while the cash still balances.
    """
    (order,) = find("RRSP_1", "2026-05-06", "MU")
    assert (order.tranches, order.quantity) == (2, 550)
    assert order.commission == pytest.approx(BMO_FLAT_COMMISSION, abs=0.005)


def test_the_derived_fee_uses_per_tranche_notional_never_a_blended_price():
    """RC-42 — ★ `Σ|qᵢ|·pᵢ`, not `Q_total × p̄`."""
    assert derive_commission(notional=10012.90, total_amount=-10022.85) == \
        pytest.approx(9.95, abs=0.005)
    assert derive_commission(notional=8925.00, total_amount=8915.07) == \
        pytest.approx(9.93, abs=0.005)


def test_rc43_every_real_order_reconciles_to_a_multiple_of_the_flat_fee():
    """RC-43 — ★ measured over **all 225 orders** across four years."""
    every = every_order()
    assert len(every) == 231
    assert sum(1 for o in every
               if abs(o.commission - BMO_FLAT_COMMISSION) < 0.005) == 155
    for order in every:
        assert implied_orders(order.commission, quantity=order.quantity,
                              side=order.side) is not None


def test_rc43_a_multiple_of_the_flat_fee_reveals_a_same_day_merge():
    """RC-43 — ★ `SPCX 2026-06-16`, four tranches, residual `19.90` = **2 × 9.95**.

    ⚠ **The export carries no order id**, so the fee is the only evidence.
    """
    (order,) = find("RRSP_1", "2026-06-16", "SPCX")
    assert order.tranches == 4 and order.implied_order_count == 2
    assert order.commission == pytest.approx(2 * BMO_FLAT_COMMISSION, abs=0.05)


def test_rc44_the_unexplained_usd_sell_excess_is_reported_not_absorbed():
    """RC-44 — ⚠ *a plausible reason attached to an unexplained residual is
    strictly worse than the honest gap* (D-01 **RA-79**, applied to fees)."""
    flagged = [o for o in every_order() if o.residual_unexplained > 0]
    assert len(flagged) == 19
    assert all(o.currency == "USD" and o.side == "Sell" for o in flagged), \
        "if a CAD order ever carries one, RC-44's reasoning needs revisiting"


def test_bmo_charges_nothing_on_its_own_etfs():
    """RC-43 — ★ a zero fee is a real fee. `ZCN` and `ZSP` are BMO's own."""
    free = {o.symbol for o in every_order() if abs(o.commission) < 0.06}
    assert free == {"ZCN", "ZSP"}


def test_an_implausible_residual_raises():
    """RC-15 — the planted violation (IM-3, BS-5)."""
    from src.recording.orders.group import assert_plausible

    with pytest.raises(CommissionImplausibleError, match="NEGATIVE"):
        assert_plausible("x", -5.0, tranches=1, quantity=100)
    with pytest.raises(CommissionImplausibleError, match="multiple"):
        assert_plausible("x", 4.10, tranches=1, quantity=10)


def test_rc11_ingestion_is_idempotent_and_content_keyed():
    """RC-11 — ★ *a changed hash for a covered window is a **restatement**.*"""
    assert file_hash(export("TFSA_1")) == file_hash(export("TFSA_1"))
    assert file_hash(export("TFSA_1")) != file_hash(export("TFSA_2"))
    assert activities("TFSA_1") == activities("TFSA_1")


# --------------------------------------------------------------------------- #
# RC-45 / RC-47 — the guards, on synthetic input now that the real data is whole
# --------------------------------------------------------------------------- #

def test_rc45_a_truncated_window_still_blocks():
    """RC-45 — ⚠ **the cash balances, so nothing else would notice.**

    The real exports no longer trip this. The guard is exercised on a deliberate
    truncation, because a check nobody can fire is a check nobody can trust.
    """
    truncated = [o for o in orders("TFSA_2")
                 if o.trade_date >= _date(2026, 1, 1)]
    with pytest.raises(TruncatedWindowError, match="went negative"):
        derive_positions(truncated)


def test_rc47_a_snapshot_may_origin_the_book_and_must_name_its_statement():
    """RC-47 — ★ the snapshot changes **where the derivation starts**, not
    whether it is checked. ⚠ It is **evidence**, so it names its source."""
    from src.recording.reconcile.opening import (
        FROM_INCEPTION, FROM_SNAPSHOT, OpeningPosition,
    )

    truncated = [o for o in orders("TFSA_2")
                 if o.trade_date >= _date(2026, 1, 1)]
    opening = [OpeningPosition(a, s, w, c, q, _date(2025, 12, 31),
                               source="BMO statement 2025-12")
               for a, s, w, c, q in (("TFSA_2", "AVGO", "CDR", "CAD", 1000.0),
                                     ("TFSA_2", "GOOG", "COMMON", "USD", 30.0),
                                     ("TFSA_2", "NVDA", "COMMON", "USD", 62.0))]
    derived = derive_positions(truncated, opening=opening)
    assert derived.origin == FROM_SNAPSHOT != FROM_INCEPTION
    assert all(q > -1e-9 for q in derived.quantities.values())

    with pytest.raises(ValueError, match="not evidence"):
        OpeningPosition("TFSA_1", "ENB", "COMMON", "USD", 220.0,
                        _date(2025, 12, 31), source="")
    with pytest.raises(ValueError, match="mandate holds none"):
        OpeningPosition("TFSA_1", "ENB", "COMMON", "USD", -5.0,
                        _date(2025, 12, 31), source="statement")


def test_rk5_the_real_book_holds_one_company_as_both_common_and_cdr():
    """D-05 **RK-5**, exercised by real data — ★ *holding a name as a CDR and as
    the US stock is **one position**.*"""
    lots: dict = {}
    for order in every_order():
        lots.setdefault(order.analysis_symbol, set()).add(
            order.instrument_id.split("|")[1])
    both = {sym for sym, kinds in lots.items() if len(kinds) > 1}
    assert both, "at least one name is held as both COMMON and CDR"


# --------------------------------------------------------------------------- #
# RC-57 — ★★ the first external check of any number in this system
# --------------------------------------------------------------------------- #

#: The balances BMO shows, supplied by Victor 2026-08-25. ★ **This is the
#: external truth** `CT-3.2` asks for — outside the repository, outside the
#: vendor, and not derivable from the rows being checked.
STATED_CASH = {
    "TFSA_1": {"CAD": 25.30, "USD": 832.81},
    "TFSA_2": {"CAD": 30.86, "USD": 151.22},
    "RRSP_1": {"CAD": 18.83, "USD": 0.00},
    "RESP_1": {"CAD": 45.43, "USD": 0.00},
}


def test_rc57_derived_cash_matches_the_broker_balance_to_the_cent():
    """★★ **RC-57 / RC-10 checked against EXTERNAL TRUTH.**

    ⚠ RC-51: derive positions, cash and NAV from the same rows and the check
    passes by construction. **These four balances come from outside the file**,
    so the arithmetic finally has something to be wrong against.

    ★ It validates the whole chain at once — the per-row layout mapping
    (RC-55), thirteen activity classifications, order grouping (RC-42), the
    derived commission (RC-15) and the cash accumulation. Two defects had to be
    fixed before it passed, and **each was found by exactly this check**.
    """
    from src.recording.book.from_activity import derive_cash

    for account, stated in STATED_CASH.items():
        cash = derive_cash(activities(account))
        for currency, expected in stated.items():
            assert cash.get(currency, 0.0) == pytest.approx(expected, abs=0.005), \
                f"{account}/{currency}: derived {cash.get(currency)} vs {expected}"


def test_rc56_a_blank_activity_carrying_cash_is_never_skipped():
    """★★ RC-56 — ⚠ three RESP rows read `BENE: 01 … GRANT REC` with **no
    activity type and $500 each**. Skipping them lost **exactly $1,500**, which
    is precisely what RESP_1 was short.

    ★ The description mapping is **declared data**, not inference — and a blank
    activity the table does not claim **raises**.
    """
    from src.recording.reconcile.ingest import BLANK_ACTIVITY_BY_DESCRIPTION

    grants = [a for a in activities("RESP_1") if a.activity == "Grant"]
    assert len(grants) == 3
    assert sum(g.total_amount for g in grants) == pytest.approx(1500.0)
    assert BLANK_ACTIVITY_BY_DESCRIPTION == (("GRANT REC", "Grant"),)


def test_rc55_a_file_may_mix_column_layouts_row_by_row():
    """★★ RC-55 — `TFSA_2` carries **both widths, interleaved**.

    ⚠ Reading the header once put `Quantity` where `Activity Description`
    belongs; the first symptom was an activity called `'1000'`.
    """
    import csv

    widths = {len(r) for r in csv.reader(
        export("TFSA_2").read_text(encoding="utf-8-sig").splitlines()[3:]) if len(r) > 1}
    assert widths == {10, 13}
    assert len(activities("TFSA_2")) == 149


def test_rc58_canadian_listings_and_cdrs_are_postponed_not_guessed():
    """⏸ RC-58 — ★ positions are derived; **only market value waits.**

    ⚠ *A CDR is a separate stock that tracks a US underlying; its price is NOT
    the underlying's price* — so nothing substitutes one for the other.
    """
    from src.recording.book.valuation import (
        UNPRICEABLE_NOT_ON_PLAN, UNPRICEABLE_WRONG_VENUE, value_direct,
    )

    unpriced = value_direct(instrument_id="BBD.B|COMMON|CAD", quantity=53,
                            price=None, currency="CAD")
    assert not unpriced.priced and unpriced.method == UNPRICEABLE_NOT_ON_PLAN

    # ⚠ RC-53 — a same-named US listing is refused, never converted.
    wrong_venue = value_direct(instrument_id="BMO|COMMON|CAD", quantity=34,
                               price=175.0, currency="CAD", quote_currency="USD")
    assert not wrong_venue.priced
    assert wrong_venue.method == UNPRICEABLE_WRONG_VENUE
