"""D-11 §8a — the BMO holdings export, on tracked SYNTHETIC fixtures. AC-11.53…11.60.

★ `RC-70`: the holdings export is the book's OUTSIDE figure — the reported balance
`RC-51` needs and the CDR/TSX prices `RC-58` lacks. These tests assert its SHAPE
(layout, line identity, the two FX rates, the self-checks, the refusals), which is
faithfully reproducible on invented data. The numbers against Victor's real files are
`test_recording_holdings_real.py` (AC-11.61), skipped when absent — *fixture what is
shape, skip what is truth* (`broker_fixtures.py`).

⚠ **Every value here is invented**, including the account number on line 1
(`99887766`), which exists only so AC-11.57 can prove it never leaks.

Tier: unit (constitution §4).
"""

from __future__ import annotations

import shutil
from datetime import date

import pytest

from src.recording.book.holdings import (
    HoldingsStatement, load_book_wide, load_holdings, parse_holdings,
    reconcile_with_activity,
)
from src.recording.errors import (
    HoldingsMissingError, HoldingsSelfCheckError, HoldingsUnrecognisedError,
)
from src.recording.orders.group import group_orders
from src.recording.reconcile.ingest import parse_export
from tests_src.broker_fixtures import SYNTHETIC

HOLDINGS = SYNTHETIC / "holdings"
MARKER = "99887766"          # the invented line-1 account number (AC-11.57)


def statement(account: str) -> HoldingsStatement:
    return parse_holdings(HOLDINGS / f"Holdings_{account}.csv", account_id=account)


def activities(account: str):
    return parse_export(HOLDINGS / f"TransactionHistory_{account}.csv", account_id=account)


# --------------------------------------------------------------------------- #
# AC-11.53 — CAD only: read as reported, the book carries the reported balance
# --------------------------------------------------------------------------- #
def test_ac_11_53_a_cad_only_export_is_read_as_reported():
    """AC-11.53 (RC-70, RC-74, RC-75) — known answer on HLD_1."""
    s = statement("HLD_1")
    assert s.account_id == "HLD_1"
    assert s.as_of == date(2026, 6, 12)
    assert (s.cash_total, s.securities, s.balance) == (150.25, 1600.00, 1750.25)
    assert s.usd_cad is None
    assert [(c.currency, c.amount, c.value_cad) for c in s.cash] == [("CAD", 150.25, 150.25)]
    by_id = {line.instrument_id: line for line in s.lines}
    assert set(by_id) == {"FRC.B|COMMON|CAD", "FTC|CDR|CAD"}
    rail = by_id["FRC.B|COMMON|CAD"]
    assert (rail.quantity, rail.price, rail.price_currency, rail.market_value_cad) == (
        100, 11.50, "CAD", 1150.00)
    assert rail.sector == "Industrials"                  # trailing space stripped
    assert (rail.average_cost, rail.total_cost, rail.cost_currency) == (10.0995, 1009.95, "CAD")

    book = s.to_book_state(account_type="TFSA")
    assert book.account_id == "HLD_1" and book.date == date(2026, 6, 12)
    assert book.nav_base == book.capital_base == 1750.25
    assert book.cash_by_currency == {"CAD": 150.25}
    assert book.reconciled == "ok"
    assert book.source == "holdings_export"
    assert {p.instrument_id: p.market_value for p in book.positions} == {
        "FRC.B|COMMON|CAD": 1150.00, "FTC|CDR|CAD": 450.00}


# --------------------------------------------------------------------------- #
# AC-11.54 — two FX rates: the footer values, the line rate is cost only
# --------------------------------------------------------------------------- #
def test_ac_11_54_market_value_uses_the_footer_rate_never_the_purchase_rate():
    """AC-11.54 (RC-72) — FCC:US carries a purchase FX of 1.35; the footer is 1.40."""
    s = statement("HLD_2")
    assert s.usd_cad == 1.4000
    chip = next(line for line in s.lines if line.symbol == "FCC:US")
    assert chip.fx_at_cost == 1.3500
    assert chip.market_value_cad == 2240.00            # 10 × 160 × 1.40, not × 1.35
    book = s.to_book_state(account_type="TFSA")
    assert book.fx_rate_used == {"USD": 1.4000}
    pos = next(p for p in book.positions if p.instrument_id == "FCC|COMMON|USD")
    assert (pos.market_value, pos.currency) == (1600.00, "USD")
    assert book.cash_by_currency == {"CAD": 40.00, "USD": 10.00}
    assert book.nav_base == 6047.00
    assert book.nav_by_currency == {"CAD": 3793.00, "USD": 1610.00}
    assert book.reconciled == "ok"


# --------------------------------------------------------------------------- #
# AC-11.55 — identity from description + currency, never the ticker
# --------------------------------------------------------------------------- #
def test_ac_11_55_line_identity_comes_from_description_and_currency():
    """AC-11.55 (RC-71) — CDR in CAD, `:US` in USD, bare TSX in CAD."""
    ids = {line.symbol: line.instrument_id for line in statement("HLD_2").lines}
    assert ids == {"FTC": "FTC|CDR|CAD", "FCC:US": "FCC|COMMON|USD",
                   "FBK": "FBK|COMMON|CAD"}
    chip = next(line for line in statement("HLD_2").lines if line.symbol == "FCC:US")
    assert chip.analysis_symbol == "FCC"


@pytest.mark.parametrize("account", ["BAD_9", "BAD_10"])
def test_ac_11_55_a_ticker_and_currency_that_disagree_raise(account):
    """AC-11.55 (RC-71) — `:US` in CAD (BAD_9), USD with no `:US` (BAD_10)."""
    with pytest.raises(HoldingsUnrecognisedError, match="RC-71"):
        statement(account)


# --------------------------------------------------------------------------- #
# AC-11.56 — one broken file per self-check, each refused with the check named
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("account, check", [
    ("BAD_1", "(a)"), ("BAD_2", "(b)"), ("BAD_3", "(c)"), ("BAD_4", "(d)"),
    ("BAD_5", "(f)"), ("BAD_11", "(g)"),
])
def test_ac_11_56_each_self_check_fires_and_names_itself(account, check):
    """AC-11.56 (RC-73)."""
    with pytest.raises(HoldingsSelfCheckError) as exc:
        statement(account)
    assert check in str(exc.value)
    assert "RC-73" in str(exc.value)


def test_ac_11_56_a_usd_line_with_no_footer_rate_raises():
    """AC-11.56 (RC-72, FX-3) — no rate, no number."""
    with pytest.raises(HoldingsUnrecognisedError, match="RC-72"):
        statement("BAD_6")


def test_ac_11_56_an_unrecognised_asset_class_raises():
    """AC-11.56 (RC-70) — `Fixed income` is not a line this parser knows."""
    with pytest.raises(HoldingsUnrecognisedError, match="Fixed income"):
        statement("BAD_7")


# --------------------------------------------------------------------------- #
# AC-11.57 — the line-1 account number is never persisted
# --------------------------------------------------------------------------- #
REFUSING = ["BAD_1", "BAD_2", "BAD_3", "BAD_4", "BAD_5", "BAD_6", "BAD_7", "BAD_8",
            "BAD_9", "BAD_10", "BAD_11"]


def test_ac_11_57_the_account_number_is_in_no_parsed_object():
    """AC-11.57 (RC-78) — not in the statement, its JSON, its repr, nor the book."""
    for account in ("HLD_1", "HLD_2"):
        s = statement(account)
        book = s.to_book_state(account_type="TFSA")
        for text in (repr(s), str(s.to_json_obj()), repr(book), str(book.to_json_obj())):
            assert MARKER not in text


@pytest.mark.parametrize("account", REFUSING)
def test_ac_11_57_the_account_number_is_in_no_error_message(account):
    """AC-11.57 (RC-78) — property over the whole refusal set of AC-11.56/11.58."""
    with pytest.raises(Exception) as exc:
        statement(account)
    assert MARKER not in str(exc.value)
    assert MARKER not in repr(exc.value)


# --------------------------------------------------------------------------- #
# AC-11.58 — an undated balance is not a balance
# --------------------------------------------------------------------------- #
def test_ac_11_58_a_missing_as_of_date_raises():
    """AC-11.58 (RC-74)."""
    with pytest.raises(HoldingsUnrecognisedError, match="RC-74"):
        statement("BAD_8")


# --------------------------------------------------------------------------- #
# AC-11.59 — no export → refused by name, never a fallback
# --------------------------------------------------------------------------- #
def _dir_with(tmp_path, holdings=(), transactions=()):
    for account in holdings:
        shutil.copy(HOLDINGS / f"Holdings_{account}.csv", tmp_path)
    for account in transactions:
        shutil.copy(HOLDINGS / f"TransactionHistory_{account}.csv", tmp_path)
    return tmp_path


def test_ac_11_59_an_account_with_no_holdings_export_is_refused_by_name(tmp_path):
    """AC-11.59 (RC-77) — a transaction history alone is never a fallback."""
    root = _dir_with(tmp_path, holdings=["HLD_2"], transactions=["HLD_1", "HLD_2"])
    with pytest.raises(HoldingsMissingError, match="no holdings export for HLD_1"):
        load_holdings("HLD_1", root=root)
    assert load_holdings("HLD_2", root=root).balance == 6047.00   # still answers


def test_ac_11_59_a_book_wide_request_over_a_partial_set_is_refused(tmp_path):
    """AC-11.59 (RC-77, RC-3, RK-5) — two of three is not the book."""
    root = _dir_with(tmp_path, holdings=["HLD_2"], transactions=["HLD_1", "HLD_2"])
    with pytest.raises(HoldingsMissingError) as exc:
        load_book_wide(root=root)
    assert exc.value.accounts == ("HLD_1",)
    assert "no holdings export for HLD_1" in str(exc.value)


def test_ac_11_59_a_complete_set_answers_book_wide(tmp_path):
    """AC-11.59 — every discovered account has an export → one statement each."""
    root = _dir_with(tmp_path, holdings=["HLD_1", "HLD_2"], transactions=["HLD_1", "HLD_2"])
    assert [s.account_id for s in load_book_wide(root=root)] == ["HLD_1", "HLD_2"]


# --------------------------------------------------------------------------- #
# AC-11.60 — RC-10 against something that can be wrong
# --------------------------------------------------------------------------- #
def _reconcile(account, rows=None):
    rows = activities(account) if rows is None else rows
    return reconcile_with_activity(statement(account), rows, group_orders(rows))


def test_ac_11_60_matching_books_reconcile_ok():
    """AC-11.60 (RC-76) — both synthetic pairs agree on every quantity and cash line."""
    assert _reconcile("HLD_1") == ()
    assert _reconcile("HLD_2") == ()


def test_ac_11_60_a_quantity_off_by_one_share_is_a_named_break_with_both_windows():
    """AC-11.60 (RC-76) — and neither side is adjusted."""
    from dataclasses import replace

    s = statement("HLD_2")
    s = replace(s, lines=tuple(replace(line, quantity=31) if line.symbol == "FBK" else line
                               for line in s.lines))
    rows = activities("HLD_2")
    breaks = reconcile_with_activity(s, rows, group_orders(rows))
    assert [b.item for b in breaks] == ["FBK|COMMON|CAD"]
    assert (breaks[0].derived, breaks[0].reported) == (30, 31)
    text = str(breaks[0])
    assert "derived 30" in text and "reported 31" in text
    assert "2026-10-15" in text and "2026-10-25" in text      # both windows


def test_ac_11_60_a_cash_line_off_by_a_cent_is_a_break():
    """AC-11.60 (RC-76) — to the cent."""
    from dataclasses import replace

    rows = activities("HLD_2")
    rows = tuple(replace(r, total_amount=5611.84) if r.activity == "Contribution" else r
                 for r in rows)
    assert [b.item for b in _reconcile("HLD_2", rows)] == ["cash CAD"]


def test_ac_11_60_a_line_on_one_side_only_is_a_break():
    """AC-11.60 (RC-76) — both directions: a holding the transactions never bought."""
    rows = tuple(r for r in activities("HLD_2") if r.symbol != "FBK")
    from dataclasses import replace

    # keep the cash identical so only the missing line breaks
    rows = rows + (replace(activities("HLD_2")[-1], activity="Withdrawal", symbol="",
                           quantity=None, price=None),)
    assert [b.item for b in _reconcile("HLD_2", rows)] == ["FBK|COMMON|CAD"]
