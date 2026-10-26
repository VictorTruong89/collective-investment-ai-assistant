"""F14 AC-F14.19 — one sizing path (`DX-191`, F14 `D12`).

★ The known answers are the design's OWN tables (`L1-portfolio-strategy` §5.1b, `PS-28`), not
numbers chosen here — so the test checks the code against the spec rather than against itself.

Tier: unit, known answer.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.portfolio import risk_budget, size_for_stop
from src.portfolio.on_demand.size_for import Policy, Sigma, size_on_demand
from src.portfolio.sizing.trade import size_trade
from src.recording.book.holdings import HoldingLine, HoldingsStatement

AS_OF = date(2026, 10, 25)


# --------------------------------------------------------------------------- #
# PS-28's table — "Cash binds: $40,000 deployable against $60,000 of risk capacity"
# --------------------------------------------------------------------------- #
def test_ac_f14_19_ps28_tight_stop_cash_binds_and_the_shares_are_reduced():
    """AC-F14.19 — risk 4,000 · entry 90 · d 6 → capacity 60,000; cash 40,000 → 444 shares."""
    t = size_trade(capital_base=400_000.0, ceiling_rate=0.01, r_total=None, committed=None,
                   n_reserve=1, entry=90.0, stop_per_share=6.0, cash_available=40_000.0)
    assert t.risk_capital == pytest.approx(4_000.0)
    assert t.notional_risk == pytest.approx(60_000.0)       # still reported (PS-28)
    assert t.binding == "cash"
    assert t.shares == 444                                   # ⚠ was 666 before DX-191
    assert t.deploy == pytest.approx(40_000.0)


def test_ac_f14_19_ps28_wide_stop_risk_binds():
    """AC-F14.19 — d 18 → capacity 20,000 < cash 40,000 → 222 shares."""
    t = size_trade(capital_base=400_000.0, ceiling_rate=0.01, r_total=None, committed=None,
                   n_reserve=1, entry=90.0, stop_per_share=18.0, cash_available=40_000.0)
    assert t.binding == "risk" and t.shares == 222
    assert t.notional_cash == pytest.approx(40_000.0)


# --------------------------------------------------------------------------- #
# §5.1b — per-trade risk = min(capital·r_ceiling, (capital·r_total − committed) / n_reserve)
# --------------------------------------------------------------------------- #
def test_ac_f14_19_5_1b_nothing_committed_the_ceiling_binds():
    """AC-F14.19 — min(1,000, 6,000 / 4) = 1,000 ⚠ (was 1,000 / 4 = 250 before DX-191)."""
    t = size_trade(capital_base=100_000.0, ceiling_rate=0.01, r_total=0.06, committed=0.0,
                   n_reserve=4, entry=50.0, stop_per_share=5.0)
    assert t.risk_capital == pytest.approx(1_000.0) and t.risk_binds == "r_ceiling"
    assert (t.allowance, t.remaining) == (pytest.approx(6_000.0), pytest.approx(6_000.0))


def test_ac_f14_19_5_1b_committed_risk_makes_the_reserve_term_bind():
    """AC-F14.19 — (6,000 − 3,000) / 4 = 750 < 1,000."""
    t = size_trade(capital_base=100_000.0, ceiling_rate=0.01, r_total=0.06, committed=3_000.0,
                   n_reserve=4, entry=50.0, stop_per_share=5.0)
    assert t.risk_capital == pytest.approx(750.0)
    assert t.risk_binds == "risk_remaining / n_reserve"


def test_ac_f14_19_with_committed_unmeasured_only_the_ceiling_binds():
    """AC-F14.19 / F14 D4 — remaining unknown → never a guessed reserve term."""
    t = size_trade(capital_base=100_000.0, ceiling_rate=0.01, r_total=0.06, committed=None,
                   n_reserve=4, entry=50.0, stop_per_share=5.0)
    assert t.remaining is None and t.risk_binds == "r_ceiling"


def test_ac_f14_19_the_uncapped_risk_notional_survives_the_cap():
    """AC-F14.19 / PS-10 — the cap binds; the number risk alone allowed is still there."""
    t = size_trade(capital_base=100_000.0, ceiling_rate=0.02, r_total=None, committed=None,
                   n_reserve=1, entry=100.0, stop_per_share=0.5)
    assert t.binding == "cap_15pct"
    assert t.notional_cap == pytest.approx(15_000.0)
    assert t.notional_risk == pytest.approx(400_000.0)


# --------------------------------------------------------------------------- #
# The two callers agree, because there is one function
# --------------------------------------------------------------------------- #
def _statement(n_lines: int, cash: float, balance: float) -> HoldingsStatement:
    lines = tuple(HoldingLine(
        instrument_id=f"H{i}|COMMON|CAD", symbol=f"H{i}", analysis_symbol=f"H{i}",
        description=f"HELD {i}", sector="", quantity=1, average_cost=1.0, total_cost=1.0,
        cost_currency="CAD", price=1.0, price_currency="CAD", market_value_cad=1.0,
        fx_at_cost=None) for i in range(n_lines))
    return HoldingsStatement(account_id="TFSA_8", as_of=AS_OF, cash_total=cash,
                             securities=float(n_lines), balance=balance, usd_cad=None,
                             cash=(), lines=lines, source_file="synthetic")


@pytest.mark.parametrize("entry, stop, cash", [
    (90.0, 84.0, 40_000.0),     # PS-28 tight → cash binds
    (90.0, 72.0, 40_000.0),     # PS-28 wide → risk binds
    (100.0, 99.5, 900_000.0),   # the cap binds
])
def test_ac_f14_19_size_for_stop_and_size_on_demand_agree(entry, stop, cash):
    """AC-F14.19 — same shares, same binding constraint, same risk capital."""
    capital, held, target = 400_000.0, 4, 8
    library = size_for_stop(
        ticker="NEWCO", account_id="TFSA_8", as_of=AS_OF, entry=entry, stop=stop,
        capital_base=capital, budget=risk_budget(r_ceiling=0.01), sigma=0.02,
        sigma_source="stated", target_positions=target, current_positions=held,
        cash_available=cash, r_total=0.06, open_positions=())
    on_demand = size_on_demand(
        ticker="NEWCO", account_id="TFSA_8", entry=entry, currency="CAD", stop=stop,
        statement=_statement(held, cash, capital),
        policy=Policy("TFSA_8", 0.06, 0.01, target, "test"), sigma=Sigma(0.02, "stated"),
        held_stops={f"H{i}": 1.0 for i in range(held)}).to_json_obj()
    assert library.arithmetic["shares"] == on_demand["shares"]
    assert library.binding_constraint["binds"] == on_demand["binding_constraint"]
    assert library.arithmetic["risk_capital"] == pytest.approx(on_demand["risk_capital"]["value"])
