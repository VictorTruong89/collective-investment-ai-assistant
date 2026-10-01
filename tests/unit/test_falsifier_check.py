"""`RM-13` — the falsifier checker, and the observable list it depends on (`DX-125`, `DX-126`).

★ What is pinned: the gathering is deterministic and complete, the READING is not claimed, and
a falsifier can only name a field the filer still reports.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.fundamental.monitor.falsifier_check import (
    DECIDABLE_BY_READER,
    NO_DATA,
    check,
    observations_since,
    summary,
)
from src.fundamental.thesis.models import BearCase, Falsifier, Thesis

AS_OF = date(2025, 6, 26)


def _rows(spec):
    """`[(period_end, filing_date, {tag: major})]` → CT-7.2-shaped rows."""
    out = []
    for period_end, filed, items in spec:
        row = {"period_end": period_end, "filing_date": filed, "period_type": "quarterly"}
        for tag, major in items.items():
            row[f"{tag}_minor"] = None if major is None else int(major * 100)
        out.append(row)
    return pd.DataFrame(out)


ROWS = _rows([
    (date(2025, 3, 1), date(2025, 4, 10), {"GrossProfit": 1_000}),        # before the thesis
    (date(2025, 8, 28), date(2025, 10, 2), {"GrossProfit": 5_054}),
    (date(2025, 11, 27), date(2026, 1, 8), {"GrossProfit": 7_646}),
    (date(2026, 2, 26), date(2026, 4, 2), {"GrossProfit": 17_755}),
])


def _thesis(*falsifiers) -> Thesis:
    # ⚠ `CT-1.1` requires 2-4 falsifiers, so a one-falsifier thesis cannot be built; the
    #   filler is a second, unrelated condition and the assertions read the first.
    if len(falsifiers) == 1:
        falsifiers = (*falsifiers, _falsifier(field="Assets", ordinal=9))
    return Thesis(
        ticker="MU", thesis_version=1, as_of=AS_OF, bundle_hash="sha256:b", run_id="r",
        verdict="SELL", conviction="Low", falsifiers=tuple(falsifiers),
        bear_case=BearCase(text="bear", falsification_condition="c", prompt_version="J-11@v1",
                           run_id="c1"),
        scorecard={}, confidence={"value": 0.5, "basis": "evidence_coverage"},
        falsifier_commit_hash="sha256:f")


def _falsifier(field="GrossProfit", ordinal=1, deadline=date(2026, 9, 30)) -> Falsifier:
    return Falsifier(ordinal=ordinal, condition=f"{field} rises in each reported quarter",
                     observable_field=field, source="D-07", deadline=deadline,
                     materiality="the thesis is wrong", about_business=True)


def test_only_periods_reported_AFTER_the_thesis_and_KNOWABLE_now_are_gathered():
    """⚠ Both halves: a period from before the thesis is not news, and one whose filing has not
    landed by the check date is not yet evidence."""
    seen = observations_since(ROWS, "GrossProfit", after=AS_OF, until=date(2026, 2, 1))
    assert [o.period_end for o in seen] == [date(2025, 8, 28), date(2025, 11, 27)]
    assert [o.value for o in seen] == [5_054.0, 7_646.0]
    later = observations_since(ROWS, "GrossProfit", after=AS_OF, until=date(2026, 9, 16))
    assert len(later) == 3


def test_the_evidence_is_gathered_and_the_READING_is_not_claimed():
    """★★ `RM-13` needs FIRED vs abandoned; parsing *"rises in each of four quarters"* out of
    prose is the plausible default `P5` forbids, so the status says who decides."""
    checks = check(_thesis(_falsifier()), ROWS, as_of=date(2026, 9, 16))
    one = checks[0]
    assert one.status == DECIDABLE_BY_READER
    assert [o.value for o in one.observations] == [5_054.0, 7_646.0, 17_755.0]
    assert "does not parse" in one.note
    assert summary(checks)["falsifiers"] == 2 and "FIRED" not in summary(checks)


def test_a_falsifier_whose_observable_never_reports_is_NO_DATA_not_HELD():
    """⛔ Measured on the MU thesis: `J-15` named `LongTermDebtNoncurrent`, which Micron stopped
    filing in 2013. ⚠ Silence is not the condition failing to fire — it is no evidence at all."""
    one = check(_thesis(_falsifier(field="LongTermDebtNoncurrent")), ROWS,
                as_of=date(2026, 9, 16))[0]
    assert one.status == NO_DATA and "no new period" in one.note


def test_a_deadline_that_has_passed_is_said_so_on_the_check():
    one = check(_thesis(_falsifier(deadline=date(2026, 6, 30))), ROWS,
                as_of=date(2026, 9, 16))[0]
    assert one.past_deadline and "past its 2026-06-30 deadline" in one.note
    assert one.to_json_obj()["checked_at"] == "2026-09-16"


def test_a_pandas_NA_value_is_MISSING_not_a_crash():
    """⚠⚠ CT-7.2's nullable columns hand out `pd.NA`, and `raw != raw` RAISES on it — the trap
    `for_ticker._missing` records, which bit this module on its first real run."""
    rows = _rows([(date(2025, 8, 28), date(2025, 10, 2), {"GrossProfit": 5_054})])
    rows["GrossProfit_minor"] = pd.array([pd.NA], dtype="Int64")
    (seen,) = observations_since(rows, "GrossProfit", after=AS_OF, until=date(2026, 9, 16))
    assert seen.value is None


def test_no_rows_at_all_is_NO_DATA_for_every_falsifier():
    checks = check(_thesis(_falsifier(), _falsifier(ordinal=2)), None, as_of=date(2026, 9, 16))
    assert {c.status for c in checks} == {NO_DATA}


# ═══════════════════════════════════════════════════════════════════════════
# `DX-126` — a falsifier may only name a field the filer STILL reports
# ═══════════════════════════════════════════════════════════════════════════

class _Engine:
    def __init__(self, rows):
        self._rows = rows

    def get_fundamentals(self, ticker, as_of=None, period_type=None):   # noqa: ARG002
        return self._rows


def test_dx_126_a_tag_the_filer_abandoned_is_no_longer_offered_as_an_observable():
    """⛔ Measured: the list offered `LongTermDebtNoncurrent` because a column exists and 2013
    rows carry values; `J-15` wrote a falsifier on it and it can never resolve (`RA-35`)."""
    from src.fundamental.bundle.for_ticker import observable_fields

    rows = _rows([
        (date(2013, 8, 29), date(2013, 10, 1), {"LongTermDebtNoncurrent": 3_267,
                                                "GrossProfit": None}),
        (date(2025, 8, 28), date(2025, 10, 2), {"LongTermDebtNoncurrent": None,
                                                "GrossProfit": 5_054}),
        (date(2025, 11, 27), date(2026, 1, 8), {"LongTermDebtNoncurrent": None,
                                                "GrossProfit": 7_646}),
        (date(2026, 2, 26), date(2026, 4, 2), {"LongTermDebtNoncurrent": None,
                                               "GrossProfit": 17_755}),
        (date(2026, 5, 28), date(2026, 7, 2), {"LongTermDebtNoncurrent": None,
                                               "GrossProfit": 35_056}),
    ])
    fields = observable_fields(_Engine(rows), "MU", date(2026, 9, 16), None)
    assert "GrossProfit" in fields
    assert "LongTermDebtNoncurrent" not in fields, "a tag unused for a decade is not checkable"


def test_dx_126_an_empty_observable_list_still_refuses_loudly():
    """★ `RA-145` — J-15 handed an empty list wrote four falsifiers naming no field at all."""
    from src.fundamental.bundle.for_ticker import observable_fields
    from src.fundamental.errors import BundleInconsistentError

    rows = _rows([(date(2026, 2, 26), date(2026, 4, 2), {"GrossProfit": None})])
    with pytest.raises(BundleInconsistentError, match="no observable fields"):
        observable_fields(_Engine(rows), "MU", date(2026, 9, 16), None)


# ═══════════════════════════════════════════════════════════════════════════
# `DX-128` — a STRUCTURED test decides, so `RM-13` needs no paid `J-15` re-run
# ═══════════════════════════════════════════════════════════════════════════

from src.fundamental.monitor.falsifier_check import (  # noqa: E402
    FIRED,
    HELD,
    evaluate_test,
    fields_in,
    series,
)

#: ⚠ DOLLARS, as the ledger carries them — the first draft of this fixture used millions and
#:   every threshold silently failed. Micron's real figures, to the million.
_M = 1_000_000
FLOWS = _rows([
    (date(2025, 8, 28), date(2025, 10, 2),
     {"OCF": 5_730 * _M, "Capex": 5_658 * _M, "GrossProfit": 5_054 * _M}),
    (date(2025, 11, 27), date(2026, 1, 8),
     {"OCF": 8_411 * _M, "Capex": 5_389 * _M, "GrossProfit": 7_646 * _M}),
    (date(2026, 2, 26), date(2026, 4, 2),
     {"OCF": 11_903 * _M, "Capex": 6_387 * _M, "GrossProfit": 17_755 * _M}),
    (date(2026, 5, 28), date(2026, 7, 2),
     {"OCF": 25_388 * _M, "Capex": 7_826 * _M, "GrossProfit": 35_056 * _M}),
])
FREE_CASH = [{"expr": [{"field": "OCF", "sign": 1}, {"field": "Capex", "sign": -1}],
              "op": ">", "value": 0}]


def _periods(rows=FLOWS, test=None):
    fields = fields_in(test) if test else ("OCF", "Capex", "GrossProfit")
    return series(rows, fields, after=AS_OF, until=date(2026, 9, 16))


def test_dx_128_the_mu_falsifier_1_fires_exactly_as_it_was_read_by_hand():
    """★★ The hand reading of 2026-09-15: OCF − capex positive in all four quarters, summing to
    $26.2bn against a $5bn threshold. ⚠ The point is that a script now reaches it."""
    test = {"window_periods": 4, "clauses": [
        {"mode": "each", "per_period": FREE_CASH},
        {"mode": "sum", "per_period": [{**FREE_CASH[0], "value": 5_000_000_000}]}]}
    status, why = evaluate_test(test, _periods(test=test))
    assert status == FIRED and "4 reported period(s)" in why


def test_dx_128_a_clause_that_does_not_hold_is_HELD_with_the_reason():
    test = {"window_periods": 4, "clauses": [
        {"mode": "each", "per_period": [{"expr": [{"field": "Capex", "sign": 1}],
                                         "op": "<", "value": 2_500_000_000}]}]}
    status, why = evaluate_test(test, _periods(test=test))
    assert status == HELD and "every period" in why


@pytest.mark.parametrize(("mode", "extra", "expected"), [
    ("rises_each", {}, FIRED),                                   # 5,054 → 35,056
    ("any", {"op": ">", "value": 30_000_000_000}, FIRED),        # the last quarter alone
    ("each", {"op": ">", "value": 30_000_000_000}, HELD),
    ("consecutive", {"op": ">", "value": 10_000_000_000, "consecutive": 2}, FIRED),
    ("consecutive", {"op": ">", "value": 30_000_000_000, "consecutive": 2}, HELD),
])
def test_dx_128_every_mode_in_the_declared_grammar_decides(mode, extra, expected):
    condition = {"expr": [{"field": "GrossProfit", "sign": 1}],
                 "op": extra.get("op", ">"), "value": extra.get("value", 0)}
    clause = {"mode": mode, "per_period": [condition]}
    if "consecutive" in extra:
        clause["consecutive"] = extra["consecutive"]
    test = {"window_periods": 4, "clauses": [clause]}
    assert evaluate_test(test, _periods(test=test))[0] == expected


def test_dx_128_two_conditions_in_one_clause_must_hold_in_the_SAME_period():
    """⚠ *"debt above X while cash below Y"* — satisfying each in a different quarter is not the
    condition. The grammar ANDs them within a period for exactly this reason."""
    rows = _rows([
        (date(2025, 8, 28), date(2025, 10, 2),
         {"Debt": 23_000 * _M, "Cash": 9_000 * _M}),                               # only debt
        (date(2025, 11, 27), date(2026, 1, 8),
         {"Debt": 10_000 * _M, "Cash": 5_000 * _M}),                               # only cash
    ])
    # ✏ 2026-10-01 `DX-139` — the window was 4 with only these 2 periods reported, so an `any`
    #   clause could still be satisfied later: HELD there was the partial-window defect. The
    #   window is now 2 (complete), which keeps this test about the SAME-period AND.
    test = {"window_periods": 2, "clauses": [{"mode": "any", "per_period": [
        {"expr": [{"field": "Debt", "sign": 1}], "op": ">", "value": 22_000_000_000},
        {"expr": [{"field": "Cash", "sign": 1}], "op": "<", "value": 6_000_000_000}]}]}
    assert evaluate_test(test, _periods(rows, test))[0] == HELD


def test_dx_128_a_field_that_never_reported_is_NO_DATA_not_HELD():
    """★ Silence is not the condition failing — `DX-126`'s lesson, now inside the evaluator."""
    test = {"window_periods": 4, "clauses": [{"mode": "any", "per_period": [
        {"expr": [{"field": "LongTermDebtNoncurrent", "sign": 1}], "op": ">", "value": 1}]}]}
    assert evaluate_test(test, _periods(test=test))[0] == NO_DATA


def test_dx_128_the_drafted_MU_tests_parse_state_their_gaps_and_name_their_thesis():
    """⚠ Each translation is a READING of a sentence; a draft with no stated gap is the one to
    distrust. ★ And the file names the thesis it belongs to, so it cannot decide another."""
    import json as _json
    import pathlib

    path = pathlib.Path(__file__).resolve().parents[2] / "config/falsifiers/mu-2025-06-26.json"
    drafted = _json.loads(path.read_text(encoding="utf-8"))
    assert drafted["_thesis_run_id"] == "run-2026-09-15T042754-mu-thesis"
    tests = {k: v for k, v in drafted.items() if not k.startswith("_")}
    assert set(tests) == {"1", "2", "3", "4"}
    for ordinal, test in tests.items():
        assert fields_in(test), f"{ordinal} reads no field"
        assert test["clauses"] and test.get("source")
    assert "_gap" in tests["4"] and "DX-126" in tests["4"]["_gap"], (
        "falsifier 4 substitutes the tag Micron actually files; that must be declared")


def test_dx_128_a_series_that_dips_once_does_NOT_fire_a_rises_each_clause():
    """⚠ Found by mutation: nothing tested a FAILING `rises_each`, so an evaluator that always
    said FIRED would have passed. One dip is the whole point of the condition."""
    rows = _rows([
        (date(2025, 8, 28), date(2025, 10, 2), {"GrossProfit": 5_054 * _M}),
        (date(2025, 11, 27), date(2026, 1, 8), {"GrossProfit": 4_000 * _M}),      # the dip
        (date(2026, 2, 26), date(2026, 4, 2), {"GrossProfit": 17_755 * _M}),
    ])
    test = {"window_periods": 4, "clauses": [
        {"mode": "rises_each", "per_period": [{"expr": [{"field": "GrossProfit", "sign": 1}],
                                               "op": ">", "value": 0}]}]}
    status, why = evaluate_test(test, _periods(rows, test))
    assert status == HELD and "does not rise in every period" in why


def test_dx_128_a_sum_below_its_threshold_is_HELD_with_the_total_named():
    """⚠ The other mutation survivor: a `sum` clause that always passed. ★ The message carries
    the total, because "the sum failed" without the number cannot be checked by a reader."""
    test = {"window_periods": 4, "clauses": [
        {"mode": "sum", "per_period": [{"expr": [{"field": "GrossProfit", "sign": 1}],
                                        "op": ">", "value": 999_000_000_000}]}]}
    status, why = evaluate_test(test, _periods(test=test))
    assert status == HELD and "65,511,000,000" in why.replace(" ", "")
