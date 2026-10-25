"""D-05 RK-40 / CT-5.4 — the behavioural-flag pass, complete on its own. AC-5.24…5.27.

★ Victor, 2026-10-21 (L9 §6.5 option ⓐ): the flags read the trade history only (RK-33),
so a flags-only pass is a complete measurement of what it measures — published beside an
`UNCHECKED` exposure, never blended into it.

Tier: unit, on tiny exports written per test (invented values; the shape is BMO's, RC-41).
"""

from __future__ import annotations

import shutil
from datetime import date, timedelta

import pytest

from src.risk.flags.behavioural import KINDS, Flag
from src.risk.flags.from_book import RECENT_WINDOW_DAYS, flag_pass, summarise
from tests_src.broker_fixtures import SYNTHETIC

HEADER = ("Transaction Date,Settlement Date,Activity Description,Description,Symbol,"
          "Quantity,Price,Price Currency,Total Amount,Total Currency")
AS_OF = date(2026, 10, 21)


def _row(day, activity, symbol, qty, price):
    # ⚠ BMO signs the QUANTITY of a sell (RC-41): `-30` shares, a positive total.
    total = -qty * price if activity == "Buy" else qty * price
    signed = qty if activity == "Buy" else -qty
    return f"{day},{day},{activity},FICTIONAL {symbol},{symbol},{signed},{price},USD,{total:.2f},USD"


def _write(root, account, rows):
    root.mkdir(parents=True, exist_ok=True)
    (root / f"TransactionHistory_{account}.csv").write_text(
        "\n".join([HEADER, "2026-01-02,2026-01-02,Contribution,CONTRIBUTION,,0,0,USD,100000.00,USD",
                   *rows]) + "\n", encoding="utf-8")


def _book(root):
    # TFSA_1: a pyramid (second buy above the first's cost) and a 2-day round trip.
    _write(root, "TFSA_1", [
        _row("2026-02-02", "Buy", "AAA", 10, 10.0),
        _row("2026-03-02", "Buy", "AAA", 10, 20.0),
        _row("2026-09-28", "Buy", "BBB", 10, 10.0),
        _row("2026-09-30", "Sell", "BBB", 10, 12.0),
    ])
    # RRSP_1: one long hold, closed last.
    _write(root, "RRSP_1", [
        _row("2026-01-05", "Buy", "CCC", 5, 10.0),
        _row("2026-10-02", "Sell", "CCC", 5, 11.0),
    ])


# ── AC-5.24 ─────────────────────────────────────────────────────────────────

def test_ac_5_24_complete_when_every_account_was_read(tmp_path):
    """AC-5.24 (RK-40) — the trade history alone completes it; no price, no book."""
    _book(tmp_path)
    fp = flag_pass(as_of=AS_OF, root=str(tmp_path))
    assert fp.status == "COMPLETE"
    assert fp.accounts == ("RRSP_1", "TFSA_1")
    assert {f.kind for f in fp.flags} >= {"pyramiding", "registered_short_hold"}


def test_ac_5_24_one_unreadable_account_withholds_all(tmp_path):
    """AC-5.24 (RK-40, RK-5) — M-4's trailing count over part of the book would
    understate the pattern, so one bad export means no flags at all, said why."""
    _book(tmp_path)
    shutil.copy(SYNTHETIC / "TransactionHistory_FIX_4.csv", tmp_path)   # RC-13: unknown activity
    fp = flag_pass(as_of=AS_OF, root=str(tmp_path))
    assert fp.status.startswith("UNCHECKED: ") and "FIX_4" in fp.status
    assert fp.flags == () and fp.counts == {}


def test_ac_5_24_no_exports_is_unchecked_not_empty(tmp_path):
    """AC-5.24 — no accounts is a missing input, never "no flags" (RK-36)."""
    fp = flag_pass(as_of=AS_OF, root=str(tmp_path / "absent"))
    assert fp.status.startswith("UNCHECKED: ") and fp.flags == ()


# ── AC-5.26 ─────────────────────────────────────────────────────────────────

def _flag(i, kind, event, *, round_trip=True):
    detail = {"closed_on": event.isoformat()} if round_trip else {}
    return Flag(flag_id=f"f{i}", kind=kind, ticker="X", account="TFSA_1",
                as_of=AS_OF if round_trip else event, detail=detail)


@pytest.mark.parametrize("offset", [0, 1, 29, 30, 31, 400])
def test_ac_5_26_recent_is_exactly_the_window_ending_history_through(offset):
    """AC-5.26 (RK-40, RK-18) — every kind counted; `recent` = event in the 30 days
    ENDING history_through (an event exactly 30 days earlier is outside)."""
    through = date(2026, 10, 2)
    event = through - timedelta(days=offset)
    flags = (_flag(1, "registered_short_hold", event),
             _flag(2, "pyramiding", event, round_trip=False))
    s = summarise(flags, history_through=through)
    assert set(s["counts"]) == set(KINDS)
    assert sum(s["counts"].values()) == len(flags)
    assert s["recent"] == (["f1", "f2"] if offset < RECENT_WINDOW_DAYS else [])


def test_ac_5_26_counts_match_the_list_on_a_real_shape(tmp_path):
    """AC-5.26 — nothing is dropped between the list and its counts."""
    _book(tmp_path)
    fp = flag_pass(as_of=AS_OF, root=str(tmp_path))
    assert sum(fp.counts.values()) == len(fp.flags)
    assert set(fp.recent) <= {f.flag_id for f in fp.flags}


# ── AC-5.27 ─────────────────────────────────────────────────────────────────

def test_ac_5_27_the_pass_states_how_far_the_history_runs(tmp_path):
    """AC-5.27 (RK-40) — a stale export must read as stale, never as "nothing recent"."""
    _book(tmp_path)
    fp = flag_pass(as_of=AS_OF, root=str(tmp_path))
    assert fp.history_through == date(2026, 10, 2)
    obj = fp.to_json_obj()
    assert obj["history_through"] == "2026-10-02" and obj["as_of"] == "2026-10-21"
    assert obj["recent_window_days"] == RECENT_WINDOW_DAYS
    assert "trade history only" in obj["source"]
    assert len(obj["flags"]) == len(fp.flags)
