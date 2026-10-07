"""F12 `D9` / `D10` — the two gate rulings (Victor, 2026-10-06). AC-F12.31, AC-F12.32.

* **AC-F12.31 (`D9`, closes L6 `AB-12`)** — `ic_significance` decides on the REALISED standard error
  (Newey-West, Bartlett, `h − 1` lags) of the per-date ICs; the null `corrected_se` stays as the MDE.
* **AC-F12.32 (`D10`)** — `breadth` tests the implied information ratio `|IC| · √BR` on the UNIVERSE
  against `IR* = 0.5`; the held book is reported beside it, never gated. Provisional.

Pure arithmetic over synthetic numbers — no data, no network.
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from src.quant.gates.metric_gate import (
    FAIL,
    NOT_EVALUATED,
    PASS,
    breadth_gate,
    ic_significance_gate,
)
from src.quant.metrics.ic import ICResult, newey_west_se, rank_ic

# ── AC-F12.31 · D9 — the realised standard error ─────────────────────────────

def test_ac_f12_31_newey_west_known_answers():
    """Known answers, worked by hand. Series 1,-1,1,-1 (mean 0, γ0 = 1, γ1 = -0.75):
    lag 0 → √(1/4) = 0.5 · lag 1 (Bartlett w1 = 1/2) → √((1 + 2·½·(-0.75))/4) = 0.25."""
    series = [1.0, -1.0, 1.0, -1.0]
    assert newey_west_se(series, lags=0) == pytest.approx(0.5)
    assert newey_west_se(series, lags=1) == pytest.approx(0.25)


def test_ac_f12_31_too_few_dates_for_the_lag_window_is_none():
    """⚠ A window shorter than the lags cannot estimate the autocovariance — `None`, never a guess."""
    assert newey_west_se([0.1, 0.2, 0.3], lags=20) is None


def test_ac_f12_31_rank_ic_keeps_the_series_and_reports_both_errors():
    """The per-date ICs survive into the result; both SEs are reported (QA-4)."""
    import numpy as np

    rng = np.random.default_rng(7)
    rows = []
    for d in pd.bdate_range("2024-01-01", periods=120):
        for n in range(30):
            score = float(rng.normal())
            rows.append({"date": d, "ticker": f"T{n}", "score": score,
                         "value": 0.3 * score + float(rng.normal())})
    result = rank_ic(pd.DataFrame(rows), horizon_days=21)
    assert len(result.per_date) == result.dates == 120
    assert result.corrected_se is not None and result.realised_se is not None
    assert result.realised_se == pytest.approx(newey_west_se(result.per_date, lags=20))
    obj = result.to_json_obj()
    assert {"corrected_se", "realised_se", "t_stat_realised"} <= set(obj)


def _ic(mean, *, realised, corrected=0.004, dates=200):
    return ICResult(horizon_days=21, mean_ic=mean, dates=dates, names_per_date=500.0,
                    effective_n=dates / 21, corrected_se=corrected, realised_se=realised)


def test_ac_f12_31_the_august_case_passes_on_null_and_fails_on_realised():
    """★ L6 AB-12's measured case: mean IC 0.0203, null SE 0.00411 (t 4.94), realised
    SE 0.01433 (t 1.42). Under D9 the gate FAILS — and still reports the null MDE."""
    gate = ic_significance_gate(_ic(0.0203, realised=0.01433, corrected=0.00411),
                                horizon_id="h1m")
    assert gate.verdict == FAIL
    assert gate.corrected_se == pytest.approx(0.01433), "the gate's SE is the realised one"
    assert "realised" in gate.why and "MDE" in gate.why


def test_ac_f12_31_a_signal_that_clears_three_realised_ses_passes():
    gate = ic_significance_gate(_ic(0.05, realised=0.012), horizon_id="h1m")
    assert gate.verdict == PASS and gate.threshold == pytest.approx(0.036)


def test_ac_f12_31_no_realised_se_is_not_evaluated_never_pass():
    """QA-17 — a realised SE that could not be estimated is NOT_EVALUATED, even when the
    null SE alone would have passed."""
    gate = ic_significance_gate(_ic(0.05, realised=None, corrected=0.001), horizon_id="h1m")
    assert gate.verdict == NOT_EVALUATED


# ── AC-F12.32 · D10 — breadth as an implied information ratio ────────────────

def test_ac_f12_32_the_statistic_is_ic_times_root_breadth():
    gate = breadth_gate(effective_breadth=48.0, mean_ic=0.0203, names=500, horizon_id="h1m")
    assert gate.statistic == pytest.approx(0.0203 * math.sqrt(48.0), abs=1e-4)
    assert gate.threshold == 0.5 and gate.verdict == FAIL


def test_ac_f12_32_the_boundary_passes():
    """IR = 0.02 · √625 = 0.5 — the bar itself passes (≥)."""
    gate = breadth_gate(effective_breadth=625.0, mean_ic=0.02, names=500, horizon_id="h1m")
    assert gate.verdict == PASS


def test_ac_f12_32_the_gate_can_fail_at_one_month():
    """⚠ The old gate (BR ≥ 3) could not: at ρ = 1, n_eff = 1 and 12 rebalances still gave
    BR = 12. With IC 0.05 that is IR 0.17 — refused now."""
    gate = breadth_gate(effective_breadth=12.0, mean_ic=0.05, names=500, horizon_id="h1m")
    assert gate.verdict == FAIL


def test_ac_f12_32_a_negative_ic_is_judged_on_its_size():
    gate = breadth_gate(effective_breadth=625.0, mean_ic=-0.02, names=500, horizon_id="h1m")
    assert gate.statistic == pytest.approx(0.5) and gate.verdict == PASS


@pytest.mark.parametrize("br, ic", [(None, 0.02), (48.0, None)])
def test_ac_f12_32_an_unmeasured_input_is_not_evaluated(br, ic):
    gate = breadth_gate(effective_breadth=br, mean_ic=ic, names=500, horizon_id="h1m")
    assert gate.verdict == NOT_EVALUATED and gate.statistic is None


def test_ac_f12_32_the_held_book_is_reported_never_gated():
    """The held book's breadth rides on the measurement as a diagnostic: n_eff of the
    top-N at the universe correlation, × rebalances per year. It never enters the gate."""
    import numpy as np

    from src.quant.backtest.portfolio import TOP_N
    from src.quant.metrics.breadth import effective_breadth, independent_names

    rng = np.random.default_rng(11)
    common = rng.normal(size=300)
    returns = pd.DataFrame({f"T{i}": 0.6 * common + rng.normal(size=300) for i in range(40)})
    out = effective_breadth(returns, horizon_days=21)
    held = out["held_book"]
    assert held["names"] == TOP_N
    assert held["independent_names"] == pytest.approx(independent_names(TOP_N, out["rho"]),
                                                      abs=1e-4)
    assert held["breadth"] == pytest.approx(held["independent_names"] * 12.0, abs=1e-3)
    assert "never gated" in held["note"]
