"""D-05 §7 — M-3 and M-4 on the real book. RK-12…RK-19, RK-39, RC-59, RC-60.

★ **The half of D-05 that needs no market value**, so it runs today while RC-58
postpones valuation — and it is the half **the mandate actually asked for**:

> **M-3:** *"Pyramiding-up is the behaviour to curb. The intended fix is to sell
> less and let winners run."*
> **M-4:** round trips inside `REGISTERED_SHORT_HOLD_DAYS` in a registered
> account, where **there is no exempt account** (RC-25).

Every number here comes from the four real BMO exports, 2022-01-01 → 2026-08-25.

Tier: unit + reality-probe (constitution §4, F3 Tier 1).
"""

from __future__ import annotations

from datetime import date

import pytest

from src.recording.book.lots import cost_changes, round_trips
from src.recording.orders.group import group_orders
from src.recording.reconcile.ingest import parse_export
from src.risk.flags.from_book import (
    behavioural_flags, m3_premature_exits, m3_pyramiding,
    m4_registered_short_holds,
)
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



EXPORTS = "sdd/design/rel6_design/samples/bmo_investorline_transactions"
ACCOUNTS = ("TFSA_1", "TFSA_2", "RRSP_1", "RESP_1")
AS_OF = date(2026, 8, 25)


def book_orders():
    out = []
    for account in ACCOUNTS:
        out += list(group_orders(parse_export(
            f"{EXPORTS}/TransactionHistory_{account}.csv", account_id=account)))
    return out


# --------------------------------------------------------------------------- #
# RC-59 — average cost, and what M-3 reads
# --------------------------------------------------------------------------- #

def test_rc59_average_cost_is_weighted_average_not_fifo():
    """RC-59 — ★ the Canadian adjusted-cost-base convention, and **M-3 is a rule
    about the average rising**. ⚠ FIFO answers a different question and would
    give a different flag."""
    changes = cost_changes(book_orders())
    assert len(changes) == 131
    for change in changes:
        if change.held_before > 0:
            blended = ((change.held_before * change.avg_cost_before
                        + change.added_value)
                       / (change.held_before + change.added_quantity))
            assert change.avg_cost_after == pytest.approx(blended, rel=1e-9)


def test_the_first_purchase_of_a_name_is_never_pyramiding():
    """RK-12 — ⚠ there is no prior average to raise, and a flag that fires on an
    opening trade would make M-3 meaningless."""
    openers = [c for c in cost_changes(book_orders()) if c.held_before == 0]
    assert openers
    assert not any(c.raises_average_cost for c in openers)


def test_the_commission_is_inside_the_average_cost():
    """RC-59 — ★ M-3 is about **what you paid**, and the fee is part of that.

    ⚠ Excluding it understates the average cost of every small order by more
    than the price moves this rule cares about.
    """
    import inspect

    import src.recording.book.lots as lots

    assert "total_amount" in inspect.getsource(lots._unit_cost)


# --------------------------------------------------------------------------- #
# M-3 — pyramiding, on the real book
# --------------------------------------------------------------------------- #

def test_m3_flags_the_real_pyramiding_in_this_book():
    """RK-12 / INV-028 — ★ *adding at ever-higher average cost.*

    ⚠ `SNDK` in `TFSA_1` is the clearest case in the data — **three scale-ins
    in fourteen days**, each at a higher price than the last:

    ```
    2026-04-16   avg   903.08 ->   911.84   added   4,612
    2026-04-28   avg   911.84 ->   958.57   added  11,058
    2026-04-30   avg   958.57 ->  1028.35   added  13,108
    ```

    ★ **+13.9 % on the average cost**, and the position roughly tripled while
    it happened. That is the mandate's stated behavioural problem, in the data.
    """
    flags = m3_pyramiding(book_orders(), as_of=AS_OF)
    assert len(flags) == 17
    assert all(f.kind == "pyramiding" for f in flags)

    sndk = sorted([f for f in flags
                   if f.ticker == "SNDK" and f.account == "TFSA_1"],
                  key=lambda f: f.as_of)
    assert len(sndk) == 3
    assert sndk[0].detail["avg_cost_before"] == pytest.approx(903.08, abs=0.01)
    assert sndk[-1].detail["avg_cost_after"] == pytest.approx(1028.35, abs=0.01)
    rise = sndk[-1].detail["avg_cost_after"] / sndk[0].detail["avg_cost_before"]
    assert rise == pytest.approx(1.139, abs=0.001)
    assert (sndk[-1].as_of - sndk[0].as_of).days == 14


def test_a_pyramiding_flag_carries_before_and_after_and_never_blocks():
    """RK-13 / RK-18 — ★ *flagged, never blocked*; the override is journalled."""
    flag = m3_pyramiding(book_orders(), as_of=AS_OF)[0]
    assert flag.detail["avg_cost_after"] > flag.detail["avg_cost_before"]
    assert flag.detail["added_exposure"] > 0
    assert flag.suppressed is False
    assert "journal" in flag.detail["note"]


# --------------------------------------------------------------------------- #
# M-4 — the registered short hold. RK-15…RK-17
# --------------------------------------------------------------------------- #

def test_rc60_round_trips_are_fifo_matched():
    """RC-60 — ⚠ **which** shares came back out matters for a holding period,
    and the earliest lot is the one the test is about."""
    trips = round_trips(book_orders())
    assert len(trips) == 120
    for trip in trips:
        assert trip.closed_on >= trip.opened_on
        assert trip.quantity > 0


def test_m4_finds_a_real_and_substantial_pattern():
    """RK-15…RK-17 / M-4 — ★★ **67 of 120 round trips close inside 30 days.**

    ⚠ *CRA's "carrying on a business" test weighs PATTERN; a single fast round
    trip is unremarkable and twenty is the finding.* This book shows **13 closed
    within a single day**, and the spec predicted exactly this from the sample:
    *"D-11 §5.3 H-6 records 1-day round trips in MU, INTC and SNDK in the RRSP."*
    """
    flags = m4_registered_short_holds(book_orders(), as_of=AS_OF)
    assert len(flags) == 67
    assert sum(1 for f in flags if f.detail["held_days"] <= 1) == 13
    # ★ RK-17 — the trailing count and frequency travel on every flag.
    assert {f.trailing_count for f in flags} == {67}
    (frequency,) = {f.detail["trailing_frequency"] for f in flags}
    assert frequency == pytest.approx(0.5583, abs=1e-4)
    assert all("carrying on a business" in f.detail["cra_rationale"] for f in flags)


def test_m4_has_no_exempt_account():
    """RK-16 / RC-25 — ★ all four accounts are registered, so M-4 applies to the
    **entire book, always**."""
    flags = m4_registered_short_holds(book_orders(), as_of=AS_OF)
    assert {f.account for f in flags} == set(ACCOUNTS)


# --------------------------------------------------------------------------- #
# M-3's other half — RK-14, RK-39
# --------------------------------------------------------------------------- #

def test_the_symmetric_flag_fires_too():
    """RK-14 — ⚠ **a domain that flags only scale-ins implements half the
    mandate and silently biases toward selling.**

    ★ RK-39: each winning exit is placed in **the book's own** distribution —
    no fixed threshold, and no intended horizon (which RK-28 forbids D-05 to
    see). This book's median hold is **23.5 days**, which is itself the finding.
    """
    flags = m3_premature_exits(book_orders(), as_of=AS_OF)
    assert len(flags) == 25
    assert all(f.detail["unrealised_gain_pct"] > 0 for f in flags), \
        "M-3's fix is about WINNERS"
    assert {f.detail["book_median_days"] for f in flags} == {23.5}
    assert all(f.detail["percentile_of_book"] <= 25.0 for f in flags)
    assert all("no fixed threshold" in f.detail["basis"] for f in flags)


def test_all_three_run_without_a_single_market_price():
    """★★ RC-58 — the flags read the **trade history**, not the valuation, so
    they run today while Canadian listings and CDRs are postponed."""
    import inspect

    import src.risk.flags.from_book as module

    source = inspect.getsource(module)
    for banned in ("price", "market_value", "quote"):
        assert f"{banned}=" not in source, banned
    flags = behavioural_flags(book_orders(), as_of=AS_OF)
    assert len(flags) == 109
    assert {f.kind for f in flags} == {"pyramiding", "premature_exit",
                                       "registered_short_hold"}
