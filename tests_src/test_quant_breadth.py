"""D-03 QA-43 — effective breadth, `breadth.residual_correlation.v1`."""
import numpy as np
import pandas as pd
import pytest

from src.quant.metrics.breadth import (
    FORMULA_ID, average_pairwise_correlation, effective_breadth,
    independent_names, residual_returns,
)


def _panel(n, dates, rho_true, seed=11):
    """`n` names with a **known** common-factor correlation."""
    rng = np.random.default_rng(seed)
    common = rng.normal(size=(dates, 1))
    idio = rng.normal(size=(dates, n))
    data = np.sqrt(rho_true) * common + np.sqrt(1 - rho_true) * idio
    return pd.DataFrame(data, columns=[f"T{i:03d}" for i in range(n)])


# --------------------------------------------------------------------------- #
# ★★★ The estimator, against known truth
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("rho_true", [0.0, 0.10, 0.35, 0.60])
def test_the_raw_measure_recovers_a_known_correlation(rho_true):
    """AC-F12.28 — ★★ The gate's input is validated against a panel whose true common
    correlation is known by construction — not against intuition."""
    measured = average_pairwise_correlation(_panel(200, 750, rho_true))
    assert measured == pytest.approx(rho_true, abs=0.02)


@pytest.mark.parametrize("n", [12, 50, 200, 500])
def test_the_residual_measure_returns_minus_one_over_n_minus_one_regardless(n):
    """AC-F12.28 — ★★★ **The reason the gate is not fed QA-43's literal measure.**

    ⚠ Removing a factor built from the same names removes the very correlation
    being measured. Measured 2026-08-27: the residual correlation is **identical
    at `rho_true = 0.00` and `0.35`** — it carries no information at all.
    """
    flat = average_pairwise_correlation(residual_returns(_panel(n, 750, 0.0)))
    correlated = average_pairwise_correlation(residual_returns(_panel(n, 750, 0.35)))
    assert flat == pytest.approx(-1.0 / (n - 1), abs=0.005)
    assert correlated == pytest.approx(-1.0 / (n - 1), abs=0.005)
    assert flat == pytest.approx(correlated, abs=0.005), \
        "a measure that cannot tell 0.00 from 0.35 measures nothing"


def test_adding_names_inside_one_factor_buys_almost_no_breadth():
    """★★ **QA-44 demonstrated**: *"370 more semiconductor names add little."*

    At `rho = 0.35`, going from 12 names to 500 moves the independent count from
    ~2.5 to ~2.9 — **488 extra names buy a third of a bet.**
    """
    small = effective_breadth(_panel(12, 750, 0.35), horizon_days=21)
    large = effective_breadth(_panel(500, 750, 0.35), horizon_days=21)
    assert large["independent_names"] - small["independent_names"] < 1.0
    assert large["names"] / small["names"] > 40


def test_independent_names_collapses_to_one_for_a_single_theme():
    """★ `ρ = 1` gives **1** — the honest answer for a book of one theme however
    many tickers it holds, and the case `breadth_gate`'s own docstring names."""
    assert independent_names(500, 1.0) == pytest.approx(1.0)
    assert independent_names(500, 0.0) == pytest.approx(500.0)


# --------------------------------------------------------------------------- #
# BR is bets per year, not a name count
# --------------------------------------------------------------------------- #

def test_breadth_is_bets_per_year_not_a_name_count():
    """★★ L1-quant v0.4.0 correction (c): *"`BR` was conflated with `n` — G&K
    breadth is bets **per year**."* ⚠ The same universe rebalanced weekly and
    annually offers very different breadth from identical holdings."""
    monthly = effective_breadth(_panel(200, 750, 0.3), horizon_days=21)
    weekly = effective_breadth(_panel(200, 750, 0.3), horizon_days=5)
    assert monthly["independent_names"] == pytest.approx(
        weekly["independent_names"], rel=1e-6), "the same holdings"
    assert weekly["breadth"] > monthly["breadth"] * 3, "more decisions per year"


def test_an_unmeasurable_breadth_is_none_never_the_name_count():
    """AC-F12.28 — ★★ QA-43 — ⚠ *Neither `BR = n` nor the equally-weighted-mean haircut is
    admissible as a default.* Substituting `n` would pass every universe by
    construction."""
    result = effective_breadth(_panel(4, 750, 0.3), horizon_days=21)
    assert result["breadth"] is None and result["independent_names"] is None
    assert "forbids substituting n" in result["why"]


def test_a_short_history_declines_rather_than_guessing():
    """⚠ A correlation between two series over 20 dates is not a correlation."""
    assert effective_breadth(_panel(50, 20, 0.3), horizon_days=21)["breadth"] is None


def test_the_formula_id_matches_the_gate():
    """FE-2's rule, one domain over — ★ the maths IS the id, and the gate names
    it."""
    from src.quant.gates.metric_gate import breadth_gate

    result = breadth_gate(effective_breadth=None, names=10, horizon_id="h1m")
    assert result.formula_id == FORMULA_ID


def test_the_gate_reads_what_the_measure_produced():
    """★ The join that did not exist: `breadth_gate` declared this `formula_id`
    since B4 and **nothing computed it**."""
    from src.quant.gates.metric_gate import breadth_gate

    measured = effective_breadth(_panel(200, 750, 0.3), horizon_days=21)
    # ✏ 2026-10-06 (F12 D10): the gate's statistic is the implied IR |IC|·√BR, so the
    #   measured BR reaches it together with an IC.
    result = breadth_gate(effective_breadth=measured["breadth"], mean_ic=0.03,
                          names=measured["names"], horizon_id="h1m")
    assert result.verdict in ("PASS", "FAIL")
    assert result.statistic == pytest.approx(0.03 * measured["breadth"] ** 0.5, abs=1e-4)
