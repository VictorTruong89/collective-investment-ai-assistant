"""D-11 §8a — the holdings export against EXTERNAL TRUTH. AC-11.61.

★ The numbers below were read off Victor's two real exports (2026-10-25) and checked by
hand: internally consistent to the cent, and in agreement with the refreshed transaction
histories (`RESP_1` to 2026-10-08, `TFSA_2` to 2026-10-15). They are worth asserting
**because they are real**, so they skip — loudly — wherever the files are absent
(`DX-5`: *fixture what is shape, skip what is truth*).

⚠ The account number on line 1 of each file is never read into anything (RC-78); nothing
here names it.

Tier: reality probe (F3 Tier 1).
"""

from __future__ import annotations

from datetime import date

import pytest

from src.recording.book.holdings import parse_holdings, reconcile_with_activity
from src.recording.orders.group import group_orders
from src.recording.reconcile.ingest import parse_export
from tests_src.broker_fixtures import REAL

requires_real_holdings = pytest.mark.skipif(
    not (REAL / "Holdings_RESP_1.csv").exists() or not (REAL / "Holdings_TFSA_2.csv").exists(),
    reason=(f"needs Victor's real BMO holdings exports (Holdings_RESP_1.csv, Holdings_TFSA_2.csv) "
            f"in {REAL} — real financial data, never in git (RC-66, DX-5). ★ This checks the "
            f"parser against EXTERNAL TRUTH; a synthetic version would assert invented data."),
)
pytestmark = requires_real_holdings

AS_OF = date(2026, 10, 25)


def real(account):
    return parse_holdings(REAL / f"Holdings_{account}.csv", account_id=account)


def test_ac_11_61_resp_1_matches_the_broker_to_the_cent():
    """AC-11.61 (RC-70…RC-75) — RESP_1, §8a.3."""
    s = real("RESP_1")
    assert s.as_of == AS_OF
    assert (s.cash_total, s.securities, s.balance) == (27.51, 13676.11, 13703.62)
    assert s.usd_cad is None
    assert [(c.currency, c.amount) for c in s.cash] == [("CAD", 27.51)]
    assert [(line.instrument_id, line.quantity, line.average_cost, line.price,
             line.market_value_cad) for line in s.lines] == [
        ("ENB|COMMON|CAD", 203, 66.04, 67.37, 13676.11)]
    book = s.to_book_state()
    assert book.capital_base == 13703.62 and book.account_type == "RESP"
    assert not book.in_fund                                    # RC-4


def test_ac_11_61_tfsa_2_matches_the_broker_to_the_cent():
    """AC-11.61 (RC-70…RC-75) — TFSA_2, §8a.3, including both FX traps."""
    s = real("TFSA_2")
    assert s.as_of == AS_OF
    assert (s.cash_total, s.securities, s.balance) == (105.24, 76700.31, 76805.55)
    assert s.usd_cad == 1.3999
    assert [(c.currency, c.amount, c.value_cad) for c in s.cash] == [
        ("CAD", 77.35, 77.35), ("USD", 19.92, 27.89)]
    assert {line.instrument_id: (line.quantity, line.market_value_cad) for line in s.lines} == {
        "GOOG|CDR|CAD": (200, 10080.00), "ARM|COMMON|USD": (36, 10599.87),
        "BMO|COMMON|CAD": (34, 8053.58), "BBD.B|COMMON|CAD": (53, 17307.68),
        "DELL|COMMON|USD": (21, 13422.20), "ENB|COMMON|CAD": (129, 8690.73),
        "MRK|CDR|CAD": (265, 8546.25)}
    arm = next(line for line in s.lines if line.symbol == "ARM:US")
    assert (arm.price, arm.price_currency, arm.fx_at_cost) == (210.33, "USD", 1.4231)
    book = s.to_book_state()
    assert book.capital_base == 76805.55 and book.fx_rate_used == {"USD": 1.3999}


@pytest.mark.parametrize("account", ["RESP_1", "TFSA_2"])
def test_ac_11_61_derived_and_reported_books_agree(account):
    """AC-11.61 (RC-76) — the transaction history and the holdings export agree."""
    rows = parse_export(REAL / f"TransactionHistory_{account}.csv", account_id=account)
    assert reconcile_with_activity(real(account), rows, group_orders(rows)) == ()
