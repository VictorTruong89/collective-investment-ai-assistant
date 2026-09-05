"""D-03 §7 — the portfolio simulation `cost_survival` reads."""
from datetime import date, timedelta

import pandas as pd
import pytest

from src.quant.backtest.costs import CostModel
from src.quant.backtest.portfolio import TOP_N, simulate, turnover_note
from src.quant.errors import QuantError


def _predictions(days=60, names=20, *, drift=0.01, seed=3):
    import numpy as np

    rng = np.random.default_rng(seed)
    rows = []
    for i in range(days):
        when = date(2025, 1, 1) + timedelta(days=i)
        for n in range(names):
            score = float(rng.normal())
            rows.append({"date": pd.Timestamp(when), "ticker": f"T{n:02d}",
                         "score": score,
                         # ★ label correlates with score, so the sim has signal
                         "value": score * drift + float(rng.normal()) * 0.005})
    return pd.DataFrame(rows)


def test_a_simulation_without_a_capital_base_raises():
    """★★ QA-48 — ⚠ `settings.yaml` asserts *"$20 round-trip immaterial at
    realistic capital"* **without stating what realistic capital is**: an
    undeclared convention doing load-bearing work. A flat fee's drag is
    **1.20 %/yr at 1m on $100k and 0.12 % on $1M** — a 10× spread on one
    strategy."""
    with pytest.raises(QuantError, match="capital"):
        simulate(_predictions(), horizon_days=21, capital=None)


def test_gross_and_net_differ_by_exactly_the_commission():
    """★ The whole point of the gate: a signal must survive its own trading."""
    result = simulate(_predictions(days=100), horizon_days=21, capital=100_000.0)
    assert result["gross_return"] > result["net_return"]
    drag = result["gross_return"] - result["net_return"]
    assert drag == pytest.approx(result["fees_paid"] / 100_000.0, rel=1e-9)


def test_a_held_name_is_not_charged_again():
    """⚠ **Commission is charged on TURNOVER, not on holdings** — which the
    legacy `_reconcile_bucket` docstring said and its code did not."""
    frame = _predictions(days=100)
    # ★ A constant score means the same names are picked every rebalance, so
    #   only the FIRST rebalance should trade.
    frame["score"] = frame["ticker"].str[1:].astype(float)
    result = simulate(frame, horizon_days=21, capital=100_000.0)
    assert result["trades"] == TOP_N, "only the opening basket should trade"


def test_rebalancing_is_at_the_horizon_not_daily():
    """⚠ Daily rebalancing on a 21-day label charges **21× the commission** for a
    signal that only changes monthly — the cost gate would then fail for an
    artefact of the simulation rather than a property of the strategy."""
    result = simulate(_predictions(days=105), horizon_days=21, capital=100_000.0)
    assert result["rebalances"] == pytest.approx(105 / 21, abs=1)


def test_returns_compound_rather_than_sum():
    """★ ⚠ Adding period returns overstates a series that alternates sign and
    understates one that trends; over 100 periods that is not a rounding
    error."""
    from src.quant.backtest.portfolio import _compound

    assert _compound([0.1, 0.1]) == pytest.approx(0.21)
    assert _compound([0.5, -0.5]) == pytest.approx(-0.25)


def test_a_thin_cross_section_is_unmeasured_never_padded():
    """QA-17 — ★ *a statistic that cannot be computed is NOT_EVALUATED, never a
    pass.* ⚠ Returning `0.0` here would read to the gate as a costless
    strategy."""
    result = simulate(_predictions(days=40, names=3), horizon_days=21,
                      capital=100_000.0)
    assert result["gross_return"] is None and result["net_return"] is None
    assert "thinner than the book" in result["why"]


def test_the_cost_gate_reads_what_the_simulation_measured():
    """★★ The join that did not exist: `engine.evaluate()` took `gross_return`
    and `net_return` as **arguments** and nothing produced them, so
    `cost_survival` reported `NOT_EVALUATED` on every run — and **no artifact
    could be promoted by construction** (MT-17)."""
    from src.models.train.run import gate_outcomes

    class _IC:
        status, mean_ic, effective_n, corrected_se = "measured", 0.05, 100.0, 0.01
        formula_id, why = "rank_ic.spearman.v1", ""

        def mde(self, t_star=3.0):
            return t_star * self.corrected_se

        def to_json_obj(self):
            return {}

    sim = simulate(_predictions(days=100), horizon_days=21, capital=100_000.0)
    outcomes = gate_outcomes(_IC(), horizon_id="h1m", names=20, simulation=sim)
    assert outcomes["cost_survival"] is not None
    assert outcomes["cost_survival"].verdict in ("PASS", "FAIL")


def test_the_turnover_note_says_costs_are_commission_only():
    """⚠ QA-49 — spread and slippage are **not modelled**, and §5.6a's ground (b)
    flips sign at 3-12 bps of proportional cost. The true drag is larger by an
    amount nobody has measured."""
    result = simulate(_predictions(days=100), horizon_days=21, capital=100_000.0)
    assert "commission only" in turnover_note(result)
    assert CostModel().proportional_bps == 0.0
