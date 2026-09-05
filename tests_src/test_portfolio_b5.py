"""D-06 B5 — AC-6.1…6.17, plus AC-6.9a…6.9m.

★★ **PS-8 is the rule the whole domain turns on: D-06 computes the risk-based
size; it does not propose it.** ⚠ §5.3's collision is why — `shares ∝ 1/σ` means
high-volatility names get small positions, the AI/semiconductor theme is
high-volatility, and **M-2 says concentration in it is a deliberate bet.**
Applied as a *recommendation*, the textbook rule would quietly implement the
diversification pressure M-2 rejects — **one trade at a time, with arithmetic as
the alibi.**

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

import math
from datetime import date

import pytest

from src.portfolio import (
    APPLIED, CONCENTRATION_THRESHOLD_PCT, Factor, MAX_POSITION_PCT,
    NOT_A_PROPOSAL, NoStopError, REALISED, REPORTED_ONLY, ReserveUnavailableError,
    RiskBudget, SizingAnswer, TAX_EVENT, TargetAllocationError, ThresholdCrossing,
    UNAPPLIED, UNMEASURED, UnavailableInputError, account_risk,
    assert_not_a_target_request, committed_risk, edge_factor, hold_alternative,
    implied_k, implied_risk, n_reserve, pyramid_check, risk_budget, risk_parity,
    scenario, size_for_stop, stop_distance,
)

AS_OF = date(2026, 8, 25)


def budget(**kw):
    return risk_budget(r_ceiling=kw.pop("r_ceiling", 0.02), **kw)


def size(**kw):
    base = dict(ticker="MU", account_id="TFSA_1", as_of=AS_OF, entry=100.0,
                stop=86.252, capital_base=100_000.0, budget=budget(),
                sigma=0.02, sigma_source="realised_20d",
                target_positions=8, current_positions=6)
    return size_for_stop(**{**base, **kw})


# --------------------------------------------------------------------------- #
# SIZING §5 — AC-6.1…6.9
# --------------------------------------------------------------------------- #

def test_ac_6_1_position_size_pct_is_absent_from_every_llm_schema_and_prompt():
    """AC-6.1 / PS-1, P2 — ★ *an LLM is doing the arithmetic today* (§1.4), and
    that is the defect this domain exists to remove."""
    import pathlib

    offenders = []
    for path in pathlib.Path("src").rglob("*.py"):
        if path.parts[1] == "portfolio":
            continue
        text = path.read_text(encoding="utf-8")
        if "position_size_pct" in text:
            offenders.append(str(path))
    for path in pathlib.Path("src/fundamental/prompts").rglob("*.md"):
        if "position_size_pct" in path.read_text(encoding="utf-8"):
            offenders.append(str(path))
    assert offenders == []


def test_ac_6_2_shares_are_risk_capital_over_stop_distance_with_no_conviction_term():
    """AC-6.2 / PS-2 — ★ **max-loss-at-stop is the basis.** *A size that varies
    with conviction is a conviction bet wearing a risk label.*"""
    answer = size()
    d = answer.arithmetic["stop_distance_per_share"]
    assert answer.arithmetic["shares"] == pytest.approx(
        answer.arithmetic["risk_capital"] / d)

    import inspect
    import src.portfolio.sizing.risk_based as module
    source = inspect.getsource(module.size_for_stop)
    assert "conviction" not in source and "rank_score" not in source


def test_the_same_risk_budget_gives_wildly_different_positions():
    """§5.1a — ★★ *"I risk 2% per trade" says NOTHING about how concentrated the
    book is.* **The stop width does all of it.**

    ⚠ Asserted on the *pre-cap* arithmetic, because INV-022 truncates the top of
    §5.1a's own table: a 2 % risk budget on a −2.2 % stop is a 90 %-of-account
    position, and PS-10 caps what the system proposes at 15 %. ★ Both facts are
    true and they are about different things — the arithmetic below, and the
    cap in `test_ac_6_8_...`.
    """
    risk_capital, entry = 2000.0, 100.0
    positions = {}
    for stop_pct in (2.2, 6.7, 13.3):
        d = entry * stop_pct / 100.0
        positions[stop_pct] = (risk_capital / d) * entry
    assert positions[2.2] == pytest.approx(90_909, abs=1)
    assert positions[6.7] == pytest.approx(29_850, abs=1)
    assert positions[13.3] == pytest.approx(15_037, abs=1)
    assert positions[2.2] > 6 * positions[13.3]      # same 2 %, six times the size


def test_ac_6_3_the_capital_base_comes_from_d11_point_in_time():
    """AC-6.3 / PS-3, RC-19 — never configured, never hard-coded."""
    answer = size(capital_base=250_000.0)
    assert answer.assumptions["capital_base"] == 250_000.0
    assert answer.assumptions["capital_base_as_of"] == AS_OF.isoformat()

    import inspect
    import src.portfolio.sizing.risk_based as module
    assert "20000" not in inspect.getsource(module)


def test_ac_6_4_sizing_with_no_stop_raises():
    """AC-6.4 / PS-5 — ★ *sizing without a stop is not conservative — it is
    undefined, and returning a number anyway invents the missing input.*"""
    with pytest.raises(NoStopError, match="knowable in advance"):
        size(stop=None)
    with pytest.raises(NoStopError, match="at or above entry"):
        size(stop=100.0)


def test_ac_6_5_every_answer_states_sigma_its_source_and_its_class():
    """AC-6.5 / PS-23 — ⚠ *realised vol is backward-looking and understates
    exactly when it matters — before an earnings gap.*

    Known-answer test for `stop_distance_vol_v1`: entry 100, σ 0.02, h 21,
    k 1.5 ⇒ d = 13.748…, and at risk_capital 2000 ⇒ 145 shares.
    """
    computed = stop_distance(entry=100.0, sigma=0.02, sigma_source="realised_20d",
                             sigma_class=REALISED, k=1.5, horizon_days=21)
    assert computed.per_share == pytest.approx(1.5 * 0.02 * math.sqrt(21) * 100.0)
    assert computed.per_share == pytest.approx(13.7477, abs=1e-4)
    assert 2000.0 / computed.per_share == pytest.approx(145.4786, abs=1e-3)

    answer = size()
    assert answer.arithmetic["sigma_class"] == REALISED
    assert answer.arithmetic["sigma_source"] == "realised_20d"
    with pytest.raises(ValueError, match="never called a forecast"):
        stop_distance(entry=100.0, sigma=0.02, sigma_source="x",
                      sigma_class="predicted")


def test_ac_6_6_a_user_supplied_stop_yields_the_implied_k():
    """AC-6.6 / PS-7 — ★ *a stop at 0.4σ and a stop at 3σ are different decisions
    and the number makes that visible.*"""
    tight = implied_k(entry=100.0, stop=96.0, sigma=0.02,
                      sigma_source="realised_20d")
    wide = implied_k(entry=100.0, stop=72.5, sigma=0.02,
                     sigma_source="realised_20d")
    assert tight.k == pytest.approx(0.4364, abs=1e-3)
    assert wide.k == pytest.approx(3.0, abs=0.01)


def test_ac_6_7_implied_risk_takes_the_humans_share_count():
    """AC-6.7 / PS-9 — ★ **the human's intended size is a first-class input**, and
    D-06 *never substitutes its own number for theirs* (INV-026)."""
    answer = implied_risk(ticker="MU", account_id="TFSA_1", as_of=AS_OF,
                          entry=100.0, stop=90.0, shares=500.0,
                          capital_base=100_000.0, sigma=0.02,
                          sigma_source="realised_20d")
    assert answer.arithmetic["shares"] == 500.0          # unchanged
    assert answer.arithmetic["risk_capital"] == pytest.approx(5000.0)
    assert answer.assumptions["risk_budget_pct"] == pytest.approx(5.0)
    assert answer.source == "human"


def test_ac_6_8_a_system_size_is_capped_and_labelled_a_human_size_never_is():
    """AC-6.8 / PS-10 — ★ **INV-022 caps only what the SYSTEM proposes.**

    ⚠ M-2 vs INV-022: capping the human's own size would be D-06 overruling the
    seat that holds the P&L.
    """
    huge = size(stop=99.5, target_positions=8, current_positions=0)
    assert huge.capped_by_inv022 is True
    assert huge.arithmetic["notional"] == pytest.approx(
        100_000.0 * MAX_POSITION_PCT / 100.0)

    human = implied_risk(ticker="MU", account_id="TFSA_1", as_of=AS_OF,
                         entry=100.0, stop=99.0, shares=900.0,
                         capital_base=100_000.0, sigma=0.02,
                         sigma_source="realised_20d")
    assert human.capped_by_inv022 is False
    assert human.arithmetic["notional"] == pytest.approx(90_000.0)
    with pytest.raises(ValueError, match="never capped"):
        SizingAnswer(ticker="MU", account_id="T", as_of=AS_OF, arithmetic={},
                     assumptions={}, risk_budget=budget(), account_risk={},
                     binding_constraint={}, consequences={},
                     capped_by_inv022=True, source="human")


def test_ac_6_9_cross_currency_sizing_with_no_fx_rate_is_unavailable():
    """AC-6.9 / PS-4, FX-3 — ★ **unavailable, not estimated.**"""
    with pytest.raises(UnavailableInputError, match="FX rate"):
        size(quote_currency="USD", currency="CAD", fx_rate=None)


# --------------------------------------------------------------------------- #
# RISK BUDGET §5.1a-c — AC-6.9a…6.9f
# --------------------------------------------------------------------------- #

def test_ac_6_9a_a_stop_above_entry_releases_the_whole_allocation():
    """AC-6.9a / PS-29 — ★ *a position whose stop has trailed above entry
    releases its budget **without being sold***.

    ⚠ The alternative — mark-to-market risk from the current price — **would
    keep a winner charged forever and quietly penalise holding**, which is the
    exact behaviour M-3 asks us to encourage.
    """
    trailing = [{"entry": 100.0, "stop": 112.0, "shares": 200.0}]
    at_risk = [{"entry": 100.0, "stop": 90.0, "shares": 200.0}]
    assert committed_risk(trailing) == 0.0
    assert committed_risk(at_risk) == pytest.approx(2000.0)


def test_ac_6_9b_allowance_committed_and_remaining_are_per_account():
    """AC-6.9b / PS-30 — ⚠ never netted: *registered accounts hold capital that
    cannot be moved between them.*"""
    a = account_risk(account_id="TFSA_1", as_of=AS_OF, capital_base=100_000.0,
                     r_ceiling=0.02,
                     open_positions=[{"entry": 100.0, "stop": 90.0,
                                      "shares": 100.0}])
    b = account_risk(account_id="RRSP_1", as_of=AS_OF, capital_base=50_000.0,
                     r_ceiling=0.02)
    assert a.allowance == 2000.0 and a.committed == 1000.0 and a.remaining == 1000.0
    assert b.allowance == 1000.0 and b.remaining == 1000.0
    assert a.to_json_obj()["account_id"] != b.to_json_obj()["account_id"]


def test_ac_6_9c_n_reserve_comes_from_the_stated_policy_never_from_cash():
    """AC-6.9c / PS-27, PS-43 — ⚠ *deriving it from cash is circular.*"""
    assert n_reserve(account_id="TFSA_1", target_positions=8,
                     current_positions=6) == 2

    import inspect
    import src.portfolio.sizing.risk_based as module
    assert "cash" not in inspect.getsource(module.n_reserve).split('"""')[2]


def test_ac_6_9l_target_positions_is_required_and_a_full_account_is_unavailable():
    """AC-6.9l / PS-43, QS-7 — ★ **a number that DIVIDES the risk budget cannot
    have an invented default.**"""
    with pytest.raises(ReserveUnavailableError, match="was not supplied"):
        size(target_positions=None)
    with pytest.raises(ReserveUnavailableError, match="account is full"):
        size(target_positions=6, current_positions=6)
    assert size().assumptions["target_positions"] == 8
    assert size().assumptions["n_reserve"] == 2


def test_ac_6_9d_every_answer_states_which_constraint_binds_with_both_numbers():
    """AC-6.9d / PS-28 — ★ *"Cash binds: $40,000 deployable against $60,000 of
    risk capacity" is a different decision from the reverse, and the reader
    cannot infer it from the share count.*"""
    cash_bound = size(cash_available=1000.0)
    assert cash_bound.binding_constraint["binds"] == "cash"
    assert cash_bound.binding_constraint["cash_available"] == 1000.0
    assert cash_bound.binding_constraint["risk_capacity_notional"] > 1000.0

    risk_bound = size(cash_available=10_000_000.0)
    assert risk_bound.binding_constraint["binds"] == "risk_capacity"


def test_ac_6_9e_the_equal_risk_weight_is_reported_beside_the_actual():
    """AC-6.9e / PS-31 — ★ *the honest counterweight to a concentrated book.*"""
    comparison = risk_parity(account_id="TFSA_1", as_of=AS_OF,
                             weights={"MU": 31.0, "NVDA": 24.0, "AMD": 12.0})
    obj = comparison.to_json_obj()
    assert obj["equal_risk_weight_pct"] == pytest.approx(33.3333, abs=1e-3)
    assert obj["actual_weight_pct"]["MU"] == 31.0
    assert obj["is_target"] is False


def test_ac_6_9f_nothing_ranks_sorts_or_tracks_drift_against_risk_parity():
    """AC-6.9f / PS-32, PS-12 — ★ **reporting the number is a disclosure;
    optimising toward it is the target allocation PS-12 forbids.**"""
    for request in ("target_allocation", "drift from target", "optimal_weights",
                    "rebalance_to"):
        with pytest.raises(TargetAllocationError):
            assert_not_a_target_request(request)

    import importlib
    import inspect

    # ⚠ `src.portfolio.scenario` resolves to the FUNCTION, not the subpackage:
    #   §4's module tree names `scenario/` and §11's API names `scenario()`, so
    #   the collision is the spec's, not this code's. `import_module` is exact.
    module = importlib.import_module("src.portfolio.scenario.whatif")
    source = inspect.getsource(module)
    assert "def rank" not in source and "def drift" not in source


# --------------------------------------------------------------------------- #
# DYNAMIC RISK BUDGET §5.1d — AC-6.9g…6.9m
# --------------------------------------------------------------------------- #

def test_ac_6_9g_every_risk_budget_reports_its_factor_decomposition():
    """AC-6.9g / PS-33 — ★ *a budget the reader cannot decompose is a number
    with an author.*"""
    obj = budget().to_json_obj()
    assert set(obj) >= {"r_ceiling", "E_edge", "C_confidence", "P_portfolio",
                        "D_drawdown", "effective", "method_id"}
    assert obj["effective"] == pytest.approx(0.02)


def test_ac_6_9h_an_unmeasurable_factor_is_one_point_zero_and_says_so():
    """AC-6.9h / PS-34 — ★ *never estimated, never quietly omitted.* The budget
    is **visibly incomplete** rather than quietly wrong."""
    obj = budget().to_json_obj()
    assert obj["C_confidence"]["status"] == UNMEASURED
    assert obj["C_confidence"]["value"] == 1.0
    assert "RM-1" in obj["C_confidence"]["why"]
    with pytest.raises(ValueError, match="estimate wearing a disclaimer"):
        Factor("C_confidence", 0.7, UNMEASURED)


def test_ac_6_9i_the_product_never_exceeds_r_ceiling():
    """AC-6.9i / INV-022 — ★ **structural, not a clamp bolted on afterwards.**

    Known-answer test for `risk_budget_dynamic_v1`: every factor 1.0 ⇒ the
    budget is exactly `r_ceiling` — ★ an unmeasured framework degrades to the
    fixed percentage it replaces, **visibly**.
    """
    assert budget(r_ceiling=0.02).effective == pytest.approx(0.02)
    applied = budget(
        r_ceiling=0.02,
        portfolio=Factor("P_portfolio", 0.70, APPLIED, source="D-05 marginal"),
        drawdown=Factor("D_drawdown", 0.85, APPLIED, source="D-11 book"))
    assert applied.effective == pytest.approx(0.02 * 0.7 * 0.85)
    assert applied.effective < 0.02
    with pytest.raises(ValueError, match="BY CONSTRUCTION"):
        Factor("E_edge", 1.4, APPLIED, source="D-03")


def test_ac_6_9j_edge_applies_only_when_the_spread_clears_its_own_mde():
    """AC-6.9j / PS-35 — ★ **the framework must be able to report that it cannot
    differentiate.** ⚠ *Manufacturing differentiation from noise* is the failure.
    """
    noise = edge_factor(spread=0.01, mde=0.04)
    assert noise.status == UNAPPLIED and noise.value == 1.0
    assert "inside its own MDE" in noise.why

    real = edge_factor(spread=0.20, mde=0.04)
    assert real.status == APPLIED and real.value < 1.0

    absent = edge_factor(spread=None, mde=None)
    assert absent.status == UNMEASURED and absent.value == 1.0


def test_ac_6_9k_every_applied_factor_resolves_to_a_method_entry():
    """AC-6.9k / PS-36, QA-20 — statement, symbols, reference, assumptions,
    alternatives-rejected and a known-answer test, before it multiplies a real
    position."""
    from src.quant.methods.registry import method, missing_sections

    for formula_id in ("risk_budget_dynamic_v1", "stop_distance_vol_v1"):
        assert missing_sections(formula_id) == []
        assert method(formula_id)

    applied = edge_factor(spread=0.20, mde=0.04)
    assert missing_sections(applied.method_id) == []


def test_ac_6_9m_d06s_entries_live_in_d06_and_it_imports_nothing_from_d03():
    """AC-6.9m / PS-44 — ★ **QA-20 owns the STANDARD, not the storage.**

    ⚠ Filing SEAT-4's entries in SEAT-3's tree, or importing `src.quant`, would
    create an edge **the graph cannot distinguish from consuming a nomination**
    (FE-21's shape, one seat over). The register's check is a *filesystem scan*.
    """
    import pathlib

    from tests_src import architecture

    here = pathlib.Path("src/portfolio/methods/entries")
    assert {p.stem for p in here.glob("*.md")} == {
        "risk_budget_dynamic_v1", "stop_distance_vol_v1"}

    graph = architecture.scan()
    reached = {m for f, mods in graph.items() if f.startswith("src/portfolio/")
               for m in mods}
    assert not [m for m in reached if m.startswith("src.quant")]
    assert not [m for m in reached if m.startswith("src.fundamental")]
    assert not [m for m in reached if "gateway" in m or m == "anthropic"]


# --------------------------------------------------------------------------- #
# CONSEQUENCES §6 — AC-6.10…6.13
# --------------------------------------------------------------------------- #

def test_ac_6_10_every_threshold_crossing_is_reported_only():
    """AC-6.10 / INV-026 — there is no other value."""
    answer = size(stop=86.252, book_weights={"sector_pct": 34.0,
                                             "theme_pct": 58.0})
    assert answer.thresholds_crossed
    assert all(t.effect == REPORTED_ONLY for t in answer.thresholds_crossed)
    with pytest.raises(TargetAllocationError):
        ThresholdCrossing("SECTOR_MAX_PCT", 35.0, 44.0, effect="blocked")


def test_ac_6_11_a_request_for_a_target_allocation_raises():
    """AC-6.11 / PS-12 — ⚠ **the forbidden dependency in L0 §4.3**, restated here
    *because it is the thing this domain would drift into.*"""
    with pytest.raises(TargetAllocationError, match="CONSEQUENCES, not proposals"):
        scenario(scenario_id="s1", as_of=AS_OF, book_ref="b",
                 hypothetical={"kind": "target_allocation"},
                 exposure_before={}, exposure_after={})


def test_ac_6_12_the_same_book_and_hypothetical_give_a_byte_identical_scenario():
    """AC-6.12 / PS-13, INV-2."""
    def make():
        return scenario(scenario_id="s1", as_of=AS_OF, book_ref="book@1",
                        hypothetical={"kind": "buy", "ticker": "MU",
                                      "shares": 100},
                        exposure_before={"MU": 20.0},
                        exposure_after={"MU": 27.5})
    a, b = make(), make()
    assert a.fingerprint() == b.fingerprint()
    assert a.deltas == {"MU": 7.5}


def test_ac_6_13_a_scenario_says_in_words_that_it_is_not_a_proposal():
    """AC-6.13 / PS-11, PS-14 — ★ *it is never a suggestion, and the artifact
    says so in words.*"""
    obj = scenario(scenario_id="s1", as_of=AS_OF, book_ref="b",
                   hypothetical={"kind": "buy"}, exposure_before={},
                   exposure_after={}).to_json_obj()
    assert obj["is_proposal"] is False
    assert obj["label"] == NOT_A_PROPOSAL
    assert "not a suggestion" in obj["label"]


# --------------------------------------------------------------------------- #
# M-3 §7 — AC-6.14…6.17
# --------------------------------------------------------------------------- #

def test_ac_6_14_a_buy_raising_the_average_cost_is_flagged_with_before_and_after():
    """AC-6.14 / PS-15 — the mandate's stated behavioural problem."""
    check = pyramid_check(ticker="MU", account_id="TFSA_1", as_of=AS_OF,
                          held_shares=100.0, held_avg_cost=84.10,
                          add_qty=50.0, price=100.0)
    assert check.is_scale_in is True
    assert check.avg_cost_before == 84.10
    assert check.avg_cost_after == pytest.approx(89.4, abs=0.05)
    assert check.added_exposure == pytest.approx(5000.0)


def test_a_buy_lowering_the_average_cost_is_not_a_scale_in():
    """PS-15 — M-3 is about pyramiding *up*."""
    assert pyramid_check(ticker="MU", account_id="TFSA_1", as_of=AS_OF,
                         held_shares=100.0, held_avg_cost=100.0,
                         add_qty=50.0, price=80.0).is_scale_in is False


def test_ac_6_15_a_pyramiding_flag_never_blocks():
    """AC-6.15 / PS-16, INV-028 — *an override is logged and visible, never
    prevented.*"""
    check = pyramid_check(ticker="MU", account_id="TFSA_1", as_of=AS_OF,
                          held_shares=100.0, held_avg_cost=84.10,
                          add_qty=50.0, price=100.0)
    assert check.blocks is False
    assert "journal" in check.to_json_obj()["override"]
    with pytest.raises(TargetAllocationError):
        pyramid_check(ticker="MU", account_id="T", as_of=AS_OF, held_shares=1.0,
                      held_avg_cost=1.0, add_qty=1.0,
                      price=2.0).__class__(ticker="MU", account_id="T",
                                           as_of=AS_OF, is_scale_in=True,
                                           avg_cost_before=1.0,
                                           avg_cost_after=2.0,
                                           added_exposure=2.0, blocks=True)


def test_ac_6_16_hold_is_a_first_class_computed_alternative():
    """AC-6.16 / PS-17 — ★ **holding is a first-class computed alternative, not
    the absence of an action.**

    ⚠ Most systems compute only the trim, which makes holding the thing that
    happens when no button is pressed.
    """
    alternative = hold_alternative(ticker="MU", account_id="TFSA_1", as_of=AS_OF,
                                   shares=200.0, price=110.0, avg_cost=84.10,
                                   trim_shares=50.0,
                                   remaining_size_check={"shares": 150.0})
    obj = alternative.to_json_obj()
    assert obj["hold"]["exposure"] == pytest.approx(22_000.0)
    assert obj["hold"]["unrealised"] == pytest.approx(5180.0)
    assert obj["hold"]["optionality_note"]
    assert obj["trim"]["cash_freed"] == pytest.approx(5500.0)
    # ★ PS-18 — "should I trim" and "is what remains correctly sized", together.
    assert obj["trim"]["remaining_size_check"] == {"shares": 150.0}


def test_ac_6_17_a_trim_reports_no_tax_event():
    """AC-6.17 / PS-21 — ★ **no tax-lot reasoning is needed, and that is a
    FINDING, not an omission.**

    All four accounts are registered, so the usual *"tax cost of trimming"* term
    is **identically zero here** — which *strengthens* M-3's "trim rather than
    exit" rather than weakening it.
    """
    obj = hold_alternative(ticker="MU", account_id="TFSA_1", as_of=AS_OF,
                           shares=200.0, price=110.0, avg_cost=84.10,
                           trim_shares=50.0).to_json_obj()
    assert obj["trim"]["tax_event"] is False and TAX_EVENT is False
    assert "registered" in obj["trim"]["tax_note"]
