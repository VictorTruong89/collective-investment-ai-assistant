"""`DX-139` — a test may not be decided on a window that has not finished reporting.

⚠ Found by the first live `J-15 v2` call (2026-10-01): falsifier #3 asked for
operating income above $1bn in EACH of the next EIGHT quarters, only four had been
reported, and `evaluate_test` said FIRED "over 4 reported period(s)". A partial
window was treated as a complete one.

★ The rule is asymmetric, because some answers are final early and some are not:
one failing quarter settles an `each` clause as HELD, one satisfying quarter
settles an `any` clause as FIRED; anything else waits, as `PENDING`.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.fundamental.monitor.falsifier_check import FIRED, HELD, PENDING, evaluate_test


def _periods(*values):
    return [{"period_end": date(2025, 8, 28), "values": {"X": v}} for v in values]


def _test(mode, value, window, **extra):
    return {"window_periods": window, "clauses": [{"mode": mode, **extra, "per_period": [
        {"expr": [{"field": "X", "sign": 1}], "op": ">", "value": value}]}]}


@pytest.mark.parametrize("test,periods,expected", [
    (_test("each", 0, 8), _periods(1, 2, 3, 4), PENDING),      # the J-15 v2 #3 case
    (_test("each", 0, 8), _periods(1, -1, 3, 4), HELD),        # one failure is final
    (_test("rises_each", 0, 8), _periods(1, 2, 3, 4), PENDING),
    (_test("rises_each", 0, 8), _periods(1, 3, 2, 4), HELD),
    (_test("any", 3, 8), _periods(1, 2, 4, 1), FIRED),         # one hit is final
    (_test("any", 9, 8), _periods(1, 2, 4, 1), PENDING),
    (_test("consecutive", 0, 8, consecutive=2), _periods(1, 2, -1, -1), FIRED),
    (_test("consecutive", 0, 8, consecutive=3), _periods(1, -1, 2, -1), PENDING),
    (_test("sum", 100, 8), _periods(1, 2, 3, 4), PENDING),     # a sum can still go either way
])
def test_dx_139_a_partial_window_is_decided_only_when_the_answer_is_already_final(
        test, periods, expected):
    status, why = evaluate_test(test, periods)
    assert status == expected, why
    if status == PENDING:
        assert "4 of 8" in why


def test_dx_139_a_complete_window_decides_exactly_as_before():
    assert evaluate_test(_test("each", 0, 4), _periods(1, 2, 3, 4))[0] == FIRED
    assert evaluate_test(_test("sum", 100, 4), _periods(1, 2, 3, 4))[0] == HELD


def test_dx_139_one_held_clause_settles_the_test_even_while_another_waits():
    """All clauses must hold to FIRE, so one final failure is a final HELD."""
    test = {"window_periods": 8, "clauses": [
        _test("sum", 0, 8)["clauses"][0], _test("each", 0, 8)["clauses"][0]]}
    assert evaluate_test(test, _periods(1, -1, 3, 4))[0] == HELD
