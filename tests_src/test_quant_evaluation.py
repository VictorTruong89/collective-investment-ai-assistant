"""D-03 §7 — the evaluation protocol. QA-4, QA-5, QA-11…QA-19, QA-43, QA-48, QA-50.

★★ **D-04 fits the models; D-03 decides whether they worked.** This is the thing
`promote()` demanded and could not previously be given.

⚠ **QA-17 has a live precedent.** F0 **D-18**: every candidate in the sleeve
optimiser failed, `best_sharpe` stayed at `-inf`, the untouched defaults were
adopted — and **`phase3b` still reported PASS, for over a month, across 8 of 8
folds.** ★ *A gate that cannot fail is decoration.*

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from src.quant import (
    BacktestResult, BacktestSpec, CostModel, FLAT_COMMISSION, GateSet,
    NOT_EVALUATED, PINNED_FIELDS, assert_comparable, assert_no_leakage,
    assert_not_pooled, assert_survivorship_stated, breadth_gate, corrected_se,
    cost_survival_gate, derive_protocol, effective_n, evaluate, folds_for,
    ic_significance_gate, make_folds, rank_ic,
)
from src.quant.errors import QuantError
from src.quant.horizons.horizon_set import PRODUCTION_V1

AS_OF = date(2026, 6, 30)


def predictions(*, dates: int = 200, names: int = 130, signal: float = 0.0,
                horizon_days: int = 21, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for day in pd.bdate_range("2020-01-01", periods=dates):
        for i in range(names):
            score = rng.normal()
            rows.append({"date": day.date(), "ticker": f"T{i}",
                         "horizon_days": horizon_days, "score": score,
                         "value": signal * score + rng.normal()})
    return pd.DataFrame(rows)


def spec(**kw):
    base = dict(universe=("NVDA", "MU"), start=date(2020, 1, 1),
                end=date(2026, 6, 30), horizon_set_name="production",
                horizon_set_version=1, initial_capital=100_000.0,
                contract_version=3, calendar_check_id="cal:1", as_of=AS_OF,
                adj_as_of=AS_OF, decision_anchor="open",
                survivorship_handled=True)
    return BacktestSpec(**{**base, **kw})


# --------------------------------------------------------------------------- #
# §5.3b — effective N and the corrected SE. QA-4, QA-5
# --------------------------------------------------------------------------- #

def test_mde_reproduces_the_specs_published_table():
    """★★ **The known-answer test for `mde.rank_ic.v1`.**

    §5.3b publishes, at `n = 130`, `T = 1915`: 1w → 0.0135, 1m → 0.0277,
    1q → 0.0479 at `t > 3`. ⚠ These are the bar, **computable before anything
    is measured**.
    """
    published = {5: 0.0135, 21: 0.0277, 63: 0.0479}
    for horizon, expected in published.items():
        mde = 3.0 * corrected_se(dates=1915, names_per_date=130,
                                 horizon_days=horizon)
        assert mde == pytest.approx(expected, abs=0.0002), horizon


def test_effective_n_divides_by_the_horizon():
    """★★ **Overlapping labels cut the independent count to `T/h`.**

    ⚠ Using `T` inflates every t-statistic by `√h` — **4.6× at 1m** — and turns
    noise into a passing gate. That is the error QA-5 exists to prevent.
    """
    assert effective_n(dates=1915, horizon_days=21) == pytest.approx(91.19, abs=0.01)
    naive_t = 0.01 / (corrected_se(dates=1915, names_per_date=130, horizon_days=1))
    corrected_t = 0.01 / corrected_se(dates=1915, names_per_date=130,
                                      horizon_days=21)
    assert naive_t / corrected_t == pytest.approx(21 ** 0.5, abs=0.01)


def test_rank_ic_is_one_when_the_ordering_is_perfect():
    """The known-answer test for `rank_ic.spearman.v1`."""
    rows = [{"date": date(2026, 1, 5), "ticker": f"T{i}", "horizon_days": 21,
             "score": i, "value": i * 2.0} for i in range(10)]
    assert rank_ic(pd.DataFrame(rows), horizon_days=21).mean_ic == pytest.approx(1.0)
    reversed_rows = [{**r, "value": -r["value"]} for r in rows]
    assert rank_ic(pd.DataFrame(reversed_rows),
                   horizon_days=21).mean_ic == pytest.approx(-1.0)


def test_qa17_an_uncomputable_statistic_is_not_evaluated_never_a_pass():
    """AC-F12.9 — ★★ QA-17 / **D-18's precedent** — *a gate that cannot fail is
    decoration.*"""
    single = pd.DataFrame([{"date": date(2026, 1, 5), "ticker": "MU",
                            "horizon_days": 21, "score": 1.0, "value": 0.1}])
    result = rank_ic(single, horizon_days=21)
    assert result.status == NOT_EVALUATED and result.mean_ic is None
    gate = ic_significance_gate(result, horizon_id="h1m")
    assert gate.verdict == NOT_EVALUATED
    assert gate.to_json_obj()["statistic"] is None


def test_qa5_horizons_are_never_compared_on_raw_metric_value():
    """QA-5 — ★ *a 1q RankIC of 0.03 and a 1w RankIC of 0.03 are not the same
    evidence, because their effective N differs by ~12×.*"""
    one_month = rank_ic(predictions(dates=60), horizon_days=21)
    one_week = rank_ic(predictions(dates=60, horizon_days=5), horizon_days=5)
    with pytest.raises(QuantError, match="raw value"):
        assert_comparable(one_month, one_week)


def test_qa4_every_statistic_carries_effective_n_and_a_corrected_se():
    """AC-F12.7 — QA-4 / AC-3.7 — ★ and the t-statistic is against the **corrected** SE."""
    result = rank_ic(predictions(dates=120), horizon_days=21)
    obj = result.to_json_obj()
    for key in ("effective_n", "corrected_se", "t_stat", "mde_t3", "formula_id"):
        assert obj[key] is not None, key
    assert result.t_stat == pytest.approx(result.mean_ic / result.corrected_se)


# --------------------------------------------------------------------------- #
# §7.3 — the CV protocol. QA-18, QA-19
# --------------------------------------------------------------------------- #

def test_purge_is_derived_from_the_longest_horizon():
    """★★ QA-18 — ⚠ *changing the horizon set changes them automatically, or
    they will be wrong the first time someone forgets.*

    HorizonSet v1 (`5`, `21`, `63`) ⇒ `purge_days = 63`, matching CT-3.1.
    """
    protocol = derive_protocol(PRODUCTION_V1)
    assert protocol.purge_days == 63 and protocol.embargo_days == 5
    assert protocol.horizon_set_version == 1


def test_purging_is_applied_on_both_sides_of_the_test_block():
    """★ *A training row **after** the test block whose label window reaches
    back into it is exactly as leaky as one before* — the overlap has no
    preferred direction, and purging only the past is the common
    half-implementation."""
    protocol = derive_protocol(PRODUCTION_V1, n_folds=3)
    days = [d.date() for d in pd.bdate_range("2024-01-01", periods=400)]
    folds = make_folds(days, protocol)
    assert len(folds) == 3
    middle = folds[1]
    assert middle.train_dates and middle.test_dates
    before = [d for d in middle.train_dates if d < middle.test_dates[0]]
    after = [d for d in middle.train_dates if d > middle.test_dates[-1]]
    assert before and after, "a middle fold trains on both sides"
    assert (middle.test_dates[0] - before[-1]).days >= protocol.purge_days
    assert (after[0] - middle.test_dates[-1]).days >= protocol.purge_days


def test_the_leakage_check_fires_when_the_gap_narrows():
    """★ The check exists because *"the construction handles it"* is not a
    guarantee — a later change to `make_folds` would silently narrow the gap."""
    from src.quant.backtest.protocol import Fold

    leaky = Fold(index=0, train_dates=(date(2026, 1, 1),),
                 test_dates=(date(2026, 1, 10), date(2026, 1, 20)),
                 purged=0, embargoed=5)
    with pytest.raises(QuantError, match="inside the 63d purge"):
        assert_no_leakage(leaky, purge_days=63)


def test_qa19_cv_groups_on_ticker_and_date():
    """AC-F12.3 — QA-19 — ★ **all copies of a row fall in the same fold**, or a row
    replicated across horizons trains on one copy and tests on another."""
    from src.quant.backtest.protocol import group_key

    assert group_key({"ticker": "MU", "date": date(2026, 1, 5), "horizon_days": 21}) \
        == group_key({"ticker": "MU", "date": date(2026, 1, 5), "horizon_days": 5})


# --------------------------------------------------------------------------- #
# §5.6a / §7.1 — costs. QA-48, QA-50
# --------------------------------------------------------------------------- #

def test_qa50_costs_are_charged_by_default():
    """QA-50 — ★ *a backtest accounts for whatever cost model exists*, and the
    result records **which components were charged**."""
    model = CostModel()
    assert model.charge_transaction_cost is True
    assert model.to_json_obj()["costs_charged"] == "commission_only"
    assert model.charge(notional=10_000, sides=2) == pytest.approx(2 * FLAT_COMMISSION)


def test_the_flat_fee_is_sourced_not_asserted():
    """★★ CN-2 — a world-fact constant carries its source and check date.

    ✏ 2026-10-05 (F12 `D8`, Victor): **BMO InvestorLine is now commission-free on
    buys and sells across all of his accounts**, so the fee is **0.00**. It was
    **9.95**, measured over 137 real orders to 2026-08-25 (D-11 RC-43) — which
    itself replaced the legacy `10.00` asserted at `backtester.py:14`.
    """
    assert FLAT_COMMISSION == 0.0
    source = CostModel().to_json_obj()["source"]
    assert "commission-free" in source and "2026-10-05" in source


def test_qa48_the_capital_base_changes_the_drag_by_ten_times():
    """★★ QA-48 — ⚠ *`settings.yaml:55` asserts "$20 round-trip immaterial at
    realistic capital" **without stating what realistic capital is**.*

    That is an undeclared convention doing load-bearing work, sitting in the
    line §5.6a's whole argument was built on.

    ✏ 2026-10-05 (F12 `D8`): the live fee is $0, so the mechanics are tested at
    the historical $9.95 — a zero fee would make the ratio 0/0 and prove nothing.
    """
    model = CostModel(flat_commission=9.95)
    small = model.annual_drag_pct(capital=100_000, trades_per_year=24,
                                  avg_notional=9_000)
    large = model.annual_drag_pct(capital=1_000_000, trades_per_year=24,
                                  avg_notional=9_000)
    assert small / large == pytest.approx(10.0, abs=0.01)
    with pytest.raises(QuantError, match="load-bearing work"):
        model.annual_drag_pct(capital=0, trades_per_year=24, avg_notional=9_000)


# --------------------------------------------------------------------------- #
# §7.1/§7.2 — the spec, the gates and the result. QA-11…QA-16, QA-43
# --------------------------------------------------------------------------- #

def test_qa11_an_unpinned_spec_is_inadmissible_as_evidence():
    """AC-F12.11 — ★★ QA-11 — *any unpinned input makes the result unreproducible and
    therefore **inadmissible as evidence**.*"""
    assert "initial_capital" in PINNED_FIELDS
    for field in ("initial_capital", "calendar_check_id", "decision_anchor",
                  "contract_version"):
        with pytest.raises(QuantError, match="INADMISSIBLE"):
            spec(**{field: None if field != "initial_capital" else 0.0})


def test_the_spec_id_is_a_content_hash():
    """INV-2 — two specs differing anywhere are different specs."""
    assert spec().spec_id == spec().spec_id
    assert spec(initial_capital=200_000.0).spec_id != spec().spec_id


def test_qa43_unmeasured_breadth_is_not_evaluated_never_n():
    """★★ QA-43 — ⚠ *neither `BR = n` nor the equally-weighted-mean haircut is
    admissible as a default.*

    ★ A ten-name book inside one theme is closer to **1–2**, not 10.
    """
    gate = breadth_gate(effective_breadth=None, names=130, horizon_id="h1m")
    assert gate.verdict == NOT_EVALUATED
    assert "forbids substituting n=130" in gate.why
    # ✏ 2026-10-06 (F12 D10): a MEASURED breadth is judged as IR = |IC|·√BR ≥ 0.5 —
    #   4.2 bets a year needs IC ≥ 0.244, so it fails at a realistic IC.
    assert breadth_gate(effective_breadth=4.2, mean_ic=0.03, names=130,
                        horizon_id="h1m").verdict == "FAIL"
    assert breadth_gate(effective_breadth=625.0, mean_ic=0.02, names=130,
                        horizon_id="h1m").verdict == "PASS"


def test_qa15_a_gate_declares_more_than_a_comparison():
    """QA-15 — ⚠ *a gate that reports only "0.031 ≥ 0.03 → PASS" is not a
    gate.*"""
    ic = rank_ic(predictions(dates=150, signal=0.4), horizon_days=21)
    obj = ic_significance_gate(ic, horizon_id="h1m").to_json_obj()
    for key in ("statistic", "threshold", "effective_n", "corrected_se",
                "t_stat", "formula_id"):
        assert obj[key] is not None, key


def test_qa16_gates_are_evaluated_per_horizon_and_never_pooled():
    """AC-F12.8 — QA-16 — one gate set per horizon."""
    with pytest.raises(QuantError, match="never pooled"):
        assert_not_pooled([GateSet("h1m"), GateSet("h1m")])


def test_a_noise_signal_fails_the_ic_gate_and_a_real_one_passes():
    """★ The gate must be able to do both, or it is decoration."""
    noise = ic_significance_gate(rank_ic(predictions(dates=150, signal=0.0),
                                         horizon_days=21), horizon_id="h1m")
    real = ic_significance_gate(rank_ic(predictions(dates=150, signal=0.8),
                                        horizon_days=21), horizon_id="h1m")
    assert noise.verdict == "FAIL" and real.verdict == "PASS"


def test_the_result_carries_its_label_and_its_formula_ids():
    """AC-F12.15 — QA-12/QA-13 — ★ *backtested returns are never presented as expected
    returns*, and the label travels with the number."""
    result = evaluate(spec(), predictions=predictions(dates=150, signal=0.8),
                      horizons=[h for h in PRODUCTION_V1.horizons
                                if h.trading_days == 21],
                      effective_breadth=4.0, gross_return=0.12, net_return=0.09)
    obj = result.to_json_obj()
    assert "not an expected return" in obj["label"]
    assert obj["costs_charged"] == "commission_only"
    assert "rank_ic.spearman.v1" in obj["formula_ids"]
    assert result.result_id.startswith("bt:")


def test_the_result_feeds_d04s_promotion_gate():
    """★★ **This is what `promote()` demanded and could not be given.**

    MT-17: production is reachable only through a record carrying a D-03
    `BacktestResult` id; MT-19: D-04 does not evaluate itself.
    """
    result = evaluate(spec(), predictions=predictions(dates=150, signal=0.8),
                      horizons=[h for h in PRODUCTION_V1.horizons
                                if h.trading_days == 21],
                      effective_breadth=4.0, gross_return=0.12, net_return=0.09)
    outcomes = result.gate_outcomes()
    assert set(outcomes) == {"ic_significance", "cost_survival", "breadth"}
    assert result.verdict == "PASS"
    assert all(v == "PASS" for v in outcomes.values())


def test_qa14_a_survivorship_blind_backtest_is_biased_not_a_result():
    """AC-F12.16 — QA-14 / INV-017 — ★ D-07's `delisted-companies` exists; using it is the
    spec's job to declare."""
    blind = spec(survivorship_handled=False)
    result = BacktestResult(spec_id=blind.spec_id, gate_sets=())
    with pytest.raises(QuantError, match="BIASED"):
        assert_survivorship_stated(result, blind)


def test_folds_for_runs_the_leakage_check_on_every_fold():
    """★ The engine wires the check, so a caller cannot forget it."""
    days = [d.date() for d in pd.bdate_range("2024-01-01", periods=400)]
    protocol = derive_protocol(PRODUCTION_V1, n_folds=3)
    assert len(folds_for(spec(), days, protocol)) == 3


def test_ac_f12_10_a_gate_set_where_every_gate_failed_cannot_pass():
    """AC-F12.10 (≡ AC-3.10, QA-17, F0 D-18) — *a gate where every candidate failed
    cannot report PASS.* ★ Invariant, checked EXHAUSTIVELY over every combination of
    up to three gate verdicts: the set is PASS iff it is non-empty and every gate
    PASSED — so no mix of FAIL and NOT_EVALUATED, and no empty set, rounds up."""
    from itertools import product

    from src.quant.gates.metric_gate import (
        FAIL,
        NOT_EVALUATED,
        PASS,
        GateResult,
        GateSet,
    )

    def gate(i, verdict):
        stat = None if verdict == NOT_EVALUATED else 0.1
        return GateResult(f"g{i}", "h1m", stat, 0.0, None, None, "f.v1", verdict)

    assert GateSet("h1m", ()).verdict == NOT_EVALUATED
    for n in (1, 2, 3):
        for verdicts in product((PASS, FAIL, NOT_EVALUATED), repeat=n):
            gs = GateSet("h1m", tuple(gate(i, v) for i, v in enumerate(verdicts)))
            assert (gs.verdict == PASS) == all(v == PASS for v in verdicts), verdicts


def test_ac_f12_10_a_pass_with_no_statistic_is_vacuous_and_raises():
    """AC-F12.10 — `QNT.GATE.VACUOUS` (§13): *a gate that cannot fail.* ★ D-18's shape
    is a PASS over nothing — every candidate errored, the default was adopted, and the
    gate still passed. A PASS with no statistic behind it is refused at construction,
    as is a verdict outside the three."""
    from src.quant.errors import GateVacuousError
    from src.quant.gates.metric_gate import PASS, GateResult

    with pytest.raises(GateVacuousError, match="QA-17"):
        GateResult("ic_significance", "h1m", None, 0.03, None, None, "f.v1", PASS)
    with pytest.raises(GateVacuousError, match="verdict"):
        GateResult("ic_significance", "h1m", 0.1, 0.03, None, None, "f.v1", "OK")
