"""F12 `D12` / AC-F12.34 — residual correlation against EXTERNAL factors. ✏ Written 2026-10-08.

★ `rho_residual` regresses on an equal-weight factor built from the same names and is pinned at
−1/(n−1) whatever the truth (AC-F12.28). Here the factors are supplied from outside — on a synthetic
panel with a planted hidden factor, so the true residual correlation is known in advance.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

N_PER_SECTOR, SECTORS, T = 15, ("Tech", "Energy", "Health", "Utilities"), 2000


def _panel(hidden_loading: float, seed: int = 5):
    """r_i = 1.0·market + 0.7·sector + h·hidden + ε_i,  var(ε)=1.

    The residual after removing market AND sector is h·hidden + ε, so its pairwise
    correlation is h² / (h² + 1) — the known answer.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2016-01-01", periods=T)
    market = rng.normal(size=T)
    hidden = rng.normal(size=T)
    sector_f = {s: rng.normal(size=T) for s in SECTORS}
    cols, sectors = {}, {}
    for s in SECTORS:
        for k in range(N_PER_SECTOR):
            t = f"{s[:3].upper()}{k}"
            cols[t] = market + 0.7 * sector_f[s] + hidden_loading * hidden + rng.normal(size=T)
            sectors[t] = s
    returns = pd.DataFrame(cols, index=dates)
    # ★ The "ETFs": exogenous series, priced outside the panel.
    etfs = pd.DataFrame({s: market + 0.7 * sector_f[s] for s in SECTORS}, index=dates)
    return returns, pd.Series(market, index=dates), etfs, sectors


@pytest.mark.parametrize("h", [0.0, 0.333, 0.5])
def test_ac_f12_34_recovers_a_known_residual_correlation(h):
    from src.quant.metrics.breadth import external_residual_correlation

    returns, market, etfs, sectors = _panel(h)
    out = external_residual_correlation(returns, market=market, sector_returns=etfs,
                                        sectors=sectors)
    truth = h * h / (h * h + 1)
    assert out["rho_market_sector"] == pytest.approx(truth, abs=0.02)
    # market-only leaves the sector structure in: within-sector pairs stay correlated
    assert out["rho_market"] > out["rho_market_sector"]


def test_ac_f12_34_is_not_pinned_at_minus_one_over_n_minus_one():
    from src.quant.metrics.breadth import external_residual_correlation, residual_returns
    from src.quant.metrics.breadth import average_pairwise_correlation

    returns, market, etfs, sectors = _panel(0.5)
    internal = average_pairwise_correlation(residual_returns(returns, sectors))
    external = external_residual_correlation(returns, market=market, sector_returns=etfs,
                                             sectors=sectors)["rho_market_sector"]
    n = returns.shape[1]
    assert internal == pytest.approx(-1 / (n - 1), abs=0.01), "the AC-F12.28 trap"
    assert external == pytest.approx(0.2, abs=0.02), "the truth: 0.25 / 1.25"


def test_ac_f12_34_reports_within_and_cross_sector_and_the_breadth_it_implies():
    from src.quant.metrics.breadth import external_residual_correlation

    returns, market, etfs, sectors = _panel(0.0)
    out = external_residual_correlation(returns, market=market, sector_returns=None,
                                        sectors=sectors, horizon_days=21)
    # market only: within-sector pairs share the sector factor (0.49 / 1.49 ≈ 0.33)
    assert out["within_sector_market"] == pytest.approx(0.49 / 1.49, abs=0.03)
    assert out["cross_sector_market"] == pytest.approx(0.0, abs=0.02)
    assert out["rho_market_sector"] is None, "no sector factors ⇒ not measured, never guessed"
    assert out["independent_names"] is not None and out["breadth"] is not None
    assert "never gated" in out["note"]


def test_ac_f12_34_a_missing_market_factor_is_not_measured():
    from src.quant.metrics.breadth import external_residual_correlation

    returns, _, etfs, sectors = _panel(0.0)
    out = external_residual_correlation(returns, market=None, sector_returns=etfs,
                                        sectors=sectors)
    assert out["rho_market"] is None and out["why"]


# ── AC-F12.35 · D13 — the gate's BR is the external MARKET-ONLY one ──────────

def test_ac_f12_35_the_gate_reads_breadth_from_the_market_only_residual():
    from src.quant.gates.metric_gate import breadth_gate
    from src.quant.metrics.breadth import (
        external_residual_correlation,
        gated_breadth,
        independent_names,
    )

    returns, market, etfs, sectors = _panel(0.333)
    ext = external_residual_correlation(returns, market=market, sector_returns=etfs,
                                        sectors=sectors, horizon_days=21)
    br, basis = gated_breadth(ext)
    n = returns.shape[1]
    assert br == pytest.approx(independent_names(n, ext["rho_market"]) * 12, rel=1e-3)
    assert br != pytest.approx(ext["breadth"]), "not the market+sector figure"
    gate = breadth_gate(effective_breadth=br, mean_ic=0.03, names=n, horizon_id="h1m",
                        basis=basis)
    assert "market-only" in gate.why and "D13" in gate.why


def test_ac_f12_35_no_external_market_factor_is_not_evaluated():
    from src.quant.gates.metric_gate import NOT_EVALUATED, breadth_gate
    from src.quant.metrics.breadth import external_residual_correlation, gated_breadth

    returns, _, etfs, sectors = _panel(0.0)
    br, basis = gated_breadth(external_residual_correlation(
        returns, market=None, sector_returns=etfs, sectors=sectors))
    assert br is None
    gate = breadth_gate(effective_breadth=br, mean_ic=0.03, names=60, horizon_id="h1m",
                        basis=basis)
    assert gate.verdict == NOT_EVALUATED


def test_ac_f12_35_training_gates_on_the_external_market_only_breadth():
    import inspect

    from src.models.train import __main__ as train

    body = inspect.getsource(train._train)
    assert "gated_breadth(external)" in body
    assert body.count("breadth=gate_breadth") == 2, "both routes into the gate"
