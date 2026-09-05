"""D-11 ingestion — the STRUCTURAL rules, on tracked synthetic fixtures.

`DX-5`. Its sibling `test_recording_ingest.py` checks derived numbers against
**external truth** — the real broker exports — and rightly skips when they are
absent. But *"the parser handles both column widths interleaved"* is a claim
about **shape**, not about anyone's money, and a clone should be able to check
it. This file is what makes the parser's edge cases verifiable on any machine.

⚠ **Every value here is invented.** No real name, amount, symbol or account
number appears. That is what makes the file committable — and it is also the
limit of what it can prove: nothing here validates the money path against
reality. `test_recording_ingest.py` does that, and cannot be replaced by this.
"""

from __future__ import annotations

import pytest

from src.recording.errors import ForeignAccountRowError, UnclassifiableActivityError
from src.recording.orders.group import group_orders
from src.recording.reconcile.ingest import (
    KNOWN_ACTIVITIES, POSITION_MOVING_NON_TRADE, parse_export,
)
from src.recording.reconcile.opening import derive_positions
from tests_src.broker_fixtures import synthetic


def acts(account: str, **kw):
    return parse_export(synthetic(account), account_id=account, **kw)


# --------------------------------------------------------------------------- #
# RC-41 / RC-55 — column layouts
# --------------------------------------------------------------------------- #
def test_rc41_the_narrow_layout_parses():
    rows = acts("FIX_1")
    assert len(rows) == 7
    assert {r.activity for r in rows} <= KNOWN_ACTIVITIES


def test_rc55_both_widths_interleaved_in_one_file_parse():
    """★★ RC-55 — reading the header ONCE put `Quantity` where `Activity` belongs.

    The first symptom upstream was an activity literally called `'1000'`. This
    fixture interleaves 10- and 13-column rows deliberately.
    """
    rows = acts("FIX_2")
    assert len(rows) == 4
    assert {r.activity for r in rows} <= KNOWN_ACTIVITIES, (
        "a mis-read header shows up as a nonsense activity name"
    )
    assert [r.symbol for r in rows if r.symbol] == ["FEL", "FEL", "FEL"]


def test_rc41_both_layouts_reach_the_same_canonical_shape():
    """A wide row and a narrow row must be indistinguishable once parsed."""
    wide = [r for r in acts("FIX_2") if r.activity == "Buy"][0]
    narrow = [r for r in acts("FIX_1") if r.activity == "Buy"][0]
    assert type(wide) is type(narrow)
    assert wide.account_id == "FIX_2" and narrow.account_id == "FIX_1"
    for field in ("trade_date", "settlement_date", "symbol", "quantity", "price"):
        assert getattr(wide, field) is not None and getattr(narrow, field) is not None


# --------------------------------------------------------------------------- #
# RC-46 / RC-12 / RC-49 — values that look like absences and are not
# --------------------------------------------------------------------------- #
def test_rc46_a_dotted_ticker_survives():
    """`FRC.B` — a dot is part of the symbol, not a delimiter."""
    assert any(r.symbol == "FRC.B" for r in acts("FIX_1"))


def test_rc12_a_zero_total_amount_is_a_tranche_not_an_absence():
    """★★ RC-12 — the second tranche of a filled order can settle at 0."""
    zero = [r for r in acts("FIX_1") if r.symbol == "FTC" and r.total_amount == 0]
    assert len(zero) == 1
    assert zero[0].quantity == 40, "a zero total must not discard the quantity"


def test_rc49_a_disbursement_moves_shares_and_carries_no_cash():
    """RC-49 — quantity moves, cash does not. Dropping it loses 25 shares."""
    d = [r for r in acts("FIX_2") if r.activity in POSITION_MOVING_NON_TRADE]
    assert len(d) == 1 and d[0].quantity == 25 and d[0].total_amount == 0


def test_rc56_a_blank_activity_carrying_cash_is_never_skipped():
    """RC-56 — a grant row whose description is prose still moves money."""
    grants = [r for r in acts("FIX_3") if r.activity == "Grant"]
    assert len(grants) == 1 and grants[0].total_amount == 500


# --------------------------------------------------------------------------- #
# RC-13 / RC-48 — the planted violations (BS-5: a rule needs a failing case)
# --------------------------------------------------------------------------- #
def test_rc13_an_unknown_activity_raises_rather_than_being_dropped():
    """★ No neutral default, no silent drop (P5)."""
    with pytest.raises(UnclassifiableActivityError):
        acts("FIX_4")


def test_rc48_a_row_from_another_account_is_refused():
    """RC-48 — the guard that found a foreign row in a real export."""
    with pytest.raises(ForeignAccountRowError):
        acts("FIX_5", strict_accounts=True)


# --------------------------------------------------------------------------- #
# RK-5 — a company held as BOTH common and CDR
# --------------------------------------------------------------------------- #
def test_rk5_one_company_may_be_held_as_common_and_as_cdr():
    """RK-5 — two instruments, ONE economic exposure. They must not merge.

    ★ The risk this encodes: a book that silently collapses `FTC` and its CDR
    `FTC.NE` into one line understates concentration in that company.
    """
    derived = derive_positions(group_orders(acts("FIX_1")))
    ftc = sorted(inst for _, inst in derived.quantities if inst.startswith("FTC"))
    assert ftc == ["FTC.NE|CDR|CAD", "FTC|COMMON|USD"], (
        f"common and CDR must stay separate instruments, got {ftc}"
    )
    assert len({i.split("|")[1] for i in ftc}) == 2, "the instrument id carries the form"


def test_positions_derive_to_the_expected_quantities():
    """The whole path — parse, group, derive — on data with a known answer."""
    derived = derive_positions(group_orders(acts("FIX_1")))
    by_symbol = {inst.split("|")[0]: q for (_, inst), q in derived.quantities.items()}
    assert by_symbol == {"FRC.B": 60.0, "FTC": 100.0, "FTC.NE": 50.0}, by_symbol
    assert all(q > 0 for q in derived.quantities.values()), "no negative positions"


# --------------------------------------------------------------------------- #
# order grouping still works on invented data
# --------------------------------------------------------------------------- #
def test_two_same_day_tranches_group_to_one_order():
    """RC-42 — two fills of one instruction are one order, not two."""
    ftc = [o for o in group_orders(acts("FIX_1")) if getattr(o, "symbol", None) == "FTC"]
    assert len(ftc) == 1, f"expected one grouped order, got {len(ftc)}"
