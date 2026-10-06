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
    """AC-F12.11 — ★★ QA-48 — ⚠ `settings.yaml` asserts *"$20 round-trip immaterial at
    realistic capital"* **without stating what realistic capital is**: an
    undeclared convention doing load-bearing work. A flat fee's drag is
    **1.20 %/yr at 1m on $100k and 0.12 % on $1M** — a 10× spread on one
    strategy."""
    with pytest.raises(QuantError, match="capital"):
        simulate(_predictions(), horizon_days=21, capital=None)


def test_gross_and_net_differ_by_exactly_the_commission():
    """★ The whole point of the gate: a signal must survive its own trading.
    ✏ 2026-10-05 (F12 `D8`): tested at the historical $9.95 — the live fee is $0,
    and gross == net would hide a broken charge."""
    result = simulate(_predictions(days=100), horizon_days=21, capital=100_000.0,
                      cost_model=CostModel(flat_commission=9.95))
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


def test_ac_f12_14_a_held_name_keeps_its_drifted_weight():
    """AC-F12.14 (≡ AC-3.11c, QA-61; F12 `D6`) — ★ held names DRIFT; only entries and
    exits trade. ⚠ The simulator used to score each period as the MEAN of the picked
    labels, which silently re-equalised every held name at every rebalance and
    charged $0 — a trade QA-61 says must be charged, and one the fund would not make.

    A doubles in period 1 and B is flat, so A enters period 2 at 2/3 of the book:
    period 2 returns 1/3 x 10 % = 3.33 %, not the equal-weight 5 %.
    """
    rows = []
    for day, (a, b) in enumerate([(1.00, 0.00), (0.00, 0.10)]):
        when = pd.Timestamp(date(2025, 1, 1) + timedelta(days=day))
        rows += [{"date": when, "ticker": "A", "score": 3.0, "value": a},
                 {"date": when, "ticker": "B", "score": 2.0, "value": b},
                 {"date": when, "ticker": "C", "score": 1.0, "value": 0.0}]
    result = simulate(pd.DataFrame(rows), horizon_days=1, capital=100_000.0, top_n=2)
    assert result["gross_return"] == pytest.approx(1.5 * (1 + 0.10 / 3) - 1, abs=1e-12)
    assert result["gross_return"] != pytest.approx(1.5 * 1.05 - 1, abs=1e-6), \
        "equal-weight re-balancing of held names is back"
    assert result["trades"] == 2, "only the opening basket trades — no re-weight trade"


def test_ac_f12_14_an_entry_takes_the_exits_proceeds():
    """AC-F12.14 / `D6` — ★ the exit is sold and its proceeds buy the entry, so a
    held winner keeps its larger weight across a rotation of the other slot."""
    rows = []
    for day, vals in enumerate([{"A": 1.00, "B": 0.00, "C": 0.0},
                                {"A": 0.00, "B": 0.0, "C": 0.30}]):
        when = pd.Timestamp(date(2025, 1, 1) + timedelta(days=day))
        scores = {"A": 3.0, "B": 2.0, "C": 1.0} if day == 0 else {"A": 3.0, "B": 1.0, "C": 2.0}
        rows += [{"date": when, "ticker": t, "score": scores[t], "value": vals[t]}
                 for t in "ABC"]
    result = simulate(pd.DataFrame(rows), horizon_days=1, capital=100_000.0, top_n=2)
    # period 2: A at 2/3 (held, drifted), C at 1/3 (B's proceeds) -> 1/3 x 30 % = 10 %
    assert result["gross_return"] == pytest.approx(1.5 * 1.10 - 1, abs=1e-12)
    assert result["trades"] == 4, "2 opening + 1 exit + 1 entry"


def test_ac_f12_12_costs_charged_is_one_of_three_and_says_none_when_off():
    """AC-F12.12 (≡ AC-3.11a, QA-12/QA-50) — *a backtest result states costs_charged
    in {none, commission_only, full}.* ⚠ With charging switched off the label used to
    read `commission_only` beside a $0 fee — a result claiming costs it never charged."""
    from src.quant.backtest.costs import COSTS_CHARGED

    assert COSTS_CHARGED == ("none", "commission_only", "full")
    on = simulate(_predictions(days=100), horizon_days=21, capital=100_000.0)
    off = simulate(_predictions(days=100), horizon_days=21, capital=100_000.0,
                   cost_model=CostModel(charge_transaction_cost=False))
    assert on["costs_charged"] == "commission_only"
    assert off["costs_charged"] == "none" and off["fees_paid"] == 0.0
    assert CostModel(charge_transaction_cost=False).to_json_obj()["costs_charged"] == "none"
    with pytest.raises(ValueError, match="costs_charged"):
        CostModel(components="gross")


def test_ac_f12_13_a_round_trip_costs_exactly_two_commissions():
    """AC-F12.13 (≡ AC-3.11b as amended by F12 `D8`, QA-62) — the known-answer test.
    The simulator charges **exactly one flat commission per trade**, so a buy-then-
    sell round trip costs exactly 2 x the fee: **$0.00 at today's commission-free
    BMO** (`D8`, Victor 2026-10-05), and exactly $19.90 at the old measured $9.95 —
    the mechanics are pinned at a non-zero fee so a zero cannot hide a broken charge.

    One-name book: A is bought on day 0 and sold on day 1 when B outranks it (the
    round trip), and B is bought (a third trade)."""
    rows = []
    for day, (sa, sb) in enumerate([(2.0, 1.0), (1.0, 2.0), (1.0, 2.0)]):
        when = pd.Timestamp(date(2025, 1, 1) + timedelta(days=day))
        rows += [{"date": when, "ticker": "A", "score": sa, "value": 0.01},
                 {"date": when, "ticker": "B", "score": sb, "value": 0.01}]
    frame = pd.DataFrame(rows)

    free = simulate(frame, horizon_days=1, capital=10_000.0, top_n=1)
    assert free["trades"] == 3 and free["fees_paid"] == 0.0
    assert free["net_return"] == free["gross_return"]

    old = simulate(frame, horizon_days=1, capital=10_000.0, top_n=1,
                   cost_model=CostModel(flat_commission=9.95))
    assert old["fees_paid"] == pytest.approx(3 * 9.95, abs=1e-9)
    assert CostModel(flat_commission=9.95).charge(notional=1.0, sides=2) == \
        pytest.approx(19.90, abs=1e-12)
