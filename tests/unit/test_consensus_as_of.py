"""`src/fundamental/bundle/consensus.py` — what the market's analysts had published, as of a date.

`L3` §2.1p item 5 (Victor, 2026-10-01). Decisions it encodes:
  1b — an item counts when published ON OR BEFORE the as-of date's MARKET CLOSE
       (16:00 New York), the same moment as the raw close price the thesis uses.
       ⚠ A row with a date but no time cannot be shown to precede the close, so a
       same-day date-only row is EXCLUDED.
  2a — past earnings estimates are included WITH a caveat: FMP edits these rows
       after the report (`lastUpdated`), so a past estimate may have been revised.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.fundamental.bundle import consensus as cs

AS_OF = date(2025, 6, 26)


def _grade(day, firm, new, action="maintain"):
    return {"symbol": "MU", "date": day, "gradingCompany": firm, "previousGrade": new,
            "newGrade": new, "action": action}


def _target(ts, firm, target, posted=127.0):
    return {"symbol": "MU", "publishedDate": ts, "analystCompany": firm,
            "priceTarget": target, "priceWhenPosted": posted}


def _earn(day, est, act, rev_est=1.0, rev_act=1.0, updated="2025-09-25"):
    return {"symbol": "MU", "date": day, "epsEstimated": est, "epsActual": act,
            "revenueEstimated": rev_est, "revenueActual": rev_act, "lastUpdated": updated}


# ── decision 1b: the as-of boundary ─────────────────────────────────────────

def test_1b_a_timestamped_item_before_the_close_counts_and_after_it_does_not():
    """16:00 New York on 2025-06-26 is 20:00 UTC (EDT)."""
    targets = [_target("2025-06-26T19:59:00.000Z", "A", 150),
               _target("2025-06-26T20:01:00.000Z", "B", 999)]
    s = cs.consensus_as_of(grades=[], targets=targets, earnings=[], as_of=AS_OF)
    assert [t["firm"] for t in s["price_targets"]["items"]] == ["A"]


def test_1b_a_same_day_date_only_row_is_excluded_it_cannot_be_shown_to_precede_the_close():
    grades = [_grade("2025-06-25", "Early", "Buy"), _grade("2025-06-26", "SameDay", "Sell")]
    s = cs.consensus_as_of(grades=grades, targets=[], earnings=[], as_of=AS_OF)
    assert set(s["ratings"]["latest_by_firm"]) == {"Early"}


def test_nothing_published_after_the_as_of_reaches_the_summary():
    s = cs.consensus_as_of(
        grades=[_grade("2026-01-01", "Late", "Sell")],
        targets=[_target("2026-01-01T12:00:00.000Z", "Late", 2000)],
        earnings=[_earn("2025-09-23", 2.0, 2.5), _earn("2026-12-23", 37.0, None)],
        as_of=AS_OF)
    assert s["ratings"]["latest_by_firm"] == {}
    assert s["price_targets"]["items"] == []
    assert s["earnings"]["reports"] == []


# ── ratings ─────────────────────────────────────────────────────────────────

def test_the_latest_rating_per_firm_within_twelve_months_is_counted_once():
    grades = [_grade("2024-01-01", "Old", "Sell"),                 # outside 12 months
              _grade("2024-09-01", "MS", "Equal Weight"),
              _grade("2025-05-01", "MS", "Overweight", "upgrade"),  # supersedes
              _grade("2025-05-02", "Citi", "Buy")]
    r = cs.consensus_as_of(grades=grades, targets=[], earnings=[], as_of=AS_OF)["ratings"]
    assert r["latest_by_firm"] == {"MS": "Overweight", "Citi": "Buy"}
    assert r["by_bucket"] == {"buy": 2, "hold": 0, "sell": 0}
    assert r["actions"] == {"maintain": 2, "upgrade": 1}       # every action in the window


def test_an_unknown_grade_is_listed_as_unmapped_never_guessed_into_a_bucket():
    """P5 — a bucket chosen for an unfamiliar label is a plausible default."""
    r = cs.consensus_as_of(grades=[_grade("2025-05-01", "X", "Speculative Accumulate")],
                           targets=[], earnings=[], as_of=AS_OF)["ratings"]
    assert r["by_bucket"] == {"buy": 0, "hold": 0, "sell": 0}
    assert r["unmapped"] == {"X": "Speculative Accumulate"}


# ── price targets ───────────────────────────────────────────────────────────

def test_price_targets_are_the_ninety_days_before_with_median_low_high():
    targets = [_target("2025-03-01T12:00:00.000Z", "Old", 50),           # outside 90 days
               _target("2025-05-01T12:00:00.000Z", "A", 135),
               _target("2025-06-01T12:00:00.000Z", "B", 150),
               _target("2025-06-20T12:00:00.000Z", "C", 170)]
    p = cs.consensus_as_of(grades=[], targets=targets, earnings=[], as_of=AS_OF)["price_targets"]
    assert (p["n"], p["median"], p["low"], p["high"]) == (3, 150, 135, 170)


# ── decision 2a: earnings estimates, with the caveat ───────────────────────

def test_2a_the_last_four_reports_carry_estimate_actual_surprise_and_the_caveat():
    earnings = [_earn(d, 1.0, 1.1) for d in
                ("2024-06-26", "2024-09-25", "2024-12-18", "2025-03-20")] + [
                _earn("2025-06-25", 1.60, 1.91, 8.86e9, 9.301e9)]
    e = cs.consensus_as_of(grades=[], targets=[], earnings=earnings, as_of=AS_OF)["earnings"]
    assert [r["date"] for r in e["reports"]] == ["2024-09-25", "2024-12-18", "2025-03-20",
                                                 "2025-06-25"]
    last = e["reports"][-1]
    assert last["eps_surprise_pct"] == pytest.approx(19.375)
    assert last["last_updated"] == "2025-09-25" and "revised" in e["caveat"]


# ── the bundle part ─────────────────────────────────────────────────────────

def test_the_part_is_computed_so_the_blind_stage_a_view_never_sees_it():
    """RA-14 — analysts' opinions are exactly the anchors the blind view strips."""
    part = cs.consensus_part(cs.consensus_as_of(
        grades=[_grade("2025-05-01", "Citi", "Buy")],
        targets=[_target("2025-06-01T12:00:00.000Z", "B", 150)],
        earnings=[_earn("2025-06-25", 1.6, 1.91)], as_of=AS_OF))
    assert part.kind == "computed"
    assert part.content.startswith("CONSENSUS AS OF 2025-06-26")
    for must in ("Citi", "median 150", "forward", "revised"):
        assert must in part.content
