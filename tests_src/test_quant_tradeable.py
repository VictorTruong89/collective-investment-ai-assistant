"""D-03 QA-125/126 — an untradeable name never reaches `candidates`."""
from datetime import date, timedelta

import pandas as pd
import pytest

from src.quant.errors import QuantError
from src.quant.signals.tradeable import (
    STALE_SESSIONS, apply_exclusions, assert_something_tradeable, untradeable,
)

AS_OF = date(2026, 8, 27)


def _panel(last_bar: dict, sessions: int = 10):
    """A panel where each name's last bar is where `last_bar` says it is."""
    days = [AS_OF - timedelta(days=i) for i in range(sessions)][::-1]
    rows = []
    for ticker, last in last_bar.items():
        for day in days:
            if day <= last:
                rows.append({"ticker": ticker, "date": pd.Timestamp(day),
                             "close": 100.0})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# ★★★ AC-3.32 — barred, and RECORDED
# --------------------------------------------------------------------------- #

def test_a_delisted_name_is_excluded_with_its_reason():
    """AC-3.32 — an untradeable name never reaches `candidates` and appears in
    `excluded[]` with its reason."""
    barred = untradeable(_panel({"NVDA": AS_OF, "AVB": AS_OF}), as_of=AS_OF,
                         delisted={"AVB": "delisted 2026-08-17"})
    kept, excluded = apply_exclusions(
        [{"ticker": "NVDA", "rank": 1}, {"ticker": "AVB", "rank": 2}], barred)

    assert [c["ticker"] for c in kept] == ["NVDA"]
    assert [e["ticker"] for e in excluded] == ["AVB"]
    assert "delisted 2026-08-17" in excluded[0]["reason"]


def test_a_barred_name_absent_from_candidates_is_still_recorded():
    """AC-3.32 — ★★ the regression this module exists for. ⚠ *Measured
    2026-08-27:* `AVB` and `EQR` are delisted **and absent from the day's
    cross-section**, so filtering the candidate list recorded NOTHING and a
    reader could not tell a name that was BEATEN from one that was BARRED.

    ★ The barred set is the authority, not the candidate list."""
    kept, excluded = apply_exclusions(
        [{"ticker": "NVDA", "rank": 1}],           # ⚠ AVB never got here
        {"AVB": "delisted 2026-08-17", "EQR": "delisted 2026-08-18"})

    assert [c["ticker"] for c in kept] == ["NVDA"]
    assert [e["ticker"] for e in excluded] == ["AVB", "EQR"]


def test_a_stale_name_is_excluded_even_though_it_still_prices():
    """AC-3.32 — a name with a stale last bar is excluded **even when it still
    prices**. ★ Nothing said it was delisted; it simply stopped printing."""
    stale = AS_OF - timedelta(days=STALE_SESSIONS + 3)
    barred = untradeable(_panel({"NVDA": AS_OF, "HALT": stale}), as_of=AS_OF)

    assert "HALT" in barred and "NVDA" not in barred
    assert "stopped printing" in barred["HALT"]


def test_a_one_session_gap_is_not_staleness():
    """QA-125 — ⚠ `STALE_SESSIONS` is not zero on purpose: a missing print is a
    halt or a late vendor file, not necessarily a delisting."""
    yesterday = AS_OF - timedelta(days=1)
    assert untradeable(_panel({"NVDA": AS_OF, "LATE": yesterday}),
                       as_of=AS_OF) == {}


def test_a_market_holiday_does_not_bar_the_whole_universe():
    """QA-125 — ⚠ staleness is measured against **the panel**, never a
    calendar: a holiday moves every name together."""
    shut = AS_OF - timedelta(days=4)
    assert untradeable(_panel({"NVDA": shut, "MSFT": shut}), as_of=AS_OF) == {}


def test_ranks_are_renumbered_over_what_survives():
    """QA-125 — ⚠ a gap where a barred name was would make `rank` and position
    disagree, and D-12 reads the top of this list as the nomination."""
    kept, _ = apply_exclusions(
        [{"ticker": "AVB", "rank": 1}, {"ticker": "NVDA", "rank": 2},
         {"ticker": "MSFT", "rank": 3}], {"AVB": "delisted"})
    assert [(c["ticker"], c["rank"]) for c in kept] == [("NVDA", 1), ("MSFT", 2)]


def test_the_supplied_reason_wins_over_the_derived_one():
    """QA-126 — tradeability is **supplied**; a delisted name keeps the store's
    reason rather than being relabelled as merely stale."""
    stale = AS_OF - timedelta(days=STALE_SESSIONS + 3)
    barred = untradeable(_panel({"NVDA": AS_OF, "AVB": stale}), as_of=AS_OF,
                         delisted={"AVB": "delisted 2026-08-17"})
    assert barred["AVB"] == "delisted 2026-08-17"


def test_an_empty_slate_raises_rather_than_nominating_nothing():
    """QA-125/P5 — ⚠ a nomination with no candidates would reach D-12 as *'no
    opportunity today'*, which is a judgement nobody made."""
    kept, excluded = apply_exclusions([{"ticker": "AVB", "rank": 1}],
                                      {"AVB": "delisted"})
    with pytest.raises(QuantError, match="no ranking to publish"):
        assert_something_tradeable(kept, excluded)
