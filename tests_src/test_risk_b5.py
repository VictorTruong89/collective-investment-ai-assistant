"""D-05 B5 — AC-5.1…5.23, plus AC-5.6a, 5.13a, 5.19a.

★ **L3 BS-15a: build B5 against §4A, not against §5–§9's list of measures.** The
two load-bearing rules are **RK-29** (never compute on an unreconciled book — the
*last good book* fallback produces a correct-looking report about yesterday) and
**RK-30** (alerts emit only from a complete pass, because silence from a risk
desk is a claim).

⚠ **BS-15b**: `CT-11.4 BookState` was assigned to no milestone and is built at
the head of B5. These tests exercise it as D-05's input.

```
D-05 MEASURES AND SAYS. IT NEVER BLOCKS AND NEVER SIZES.
```

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

import dataclasses
from datetime import date, timedelta

import pytest

from src.recording.book.models import BookState, Break, Position
from src.recording.book.reconcile import (
    assert_reconciled, build_book, capital_base, compute_breaks,
)
from src.recording.errors import BookBreakError, CapitalBaseUnavailableError
from src.risk import (
    BlockAttemptedError, BookRisk, CONCENTRATION_THRESHOLD_PCT, Flag,
    FxUnavailableError, HoldingPeriods, NoBookError, NoTaxonomyError,
    REGISTERED_SHORT_HOLD_DAYS, REPORTED_ONLY, SECTOR_MAX_PCT, SEMI_2022,
    SuppressionAttemptedError, THEMES_V1, THEME_REPORT_THRESHOLD_PCT, Theme,
    ThemeTaxonomy, UNCLASSIFIED, UNMEASURED, Unmeasured,
    VarMethodUnstatedError, VarWithoutConcentrationError, acknowledge,
    daily_book_pass, drawdown, exposure, hypothetical_book, marginal_risk,
    premature_exit_flag, pyramiding_flag, refuse_to_block, short_hold_flags,
    stress, suppress, thresholds_crossed,
)

AS_OF = date(2026, 8, 25)


def pos(symbol="MU", value=1000.0, currency="CAD", account="TFSA_1",
        instrument=None, sector="Information Technology", **kw):
    return Position(instrument_id=instrument or f"{symbol}.{currency}",
                    analysis_symbol=symbol, quantity=10.0, market_value=value,
                    currency=currency, account_id=account, sector=sector, **kw)


def book(positions=None, *, account="TFSA_1", cash=0.0, nav=None,
         account_type="TFSA", fx=None, as_of=AS_OF):
    positions = positions if positions is not None else [pos()]
    by_ccy: dict = {}
    for p in positions:
        by_ccy[p.currency] = by_ccy.get(p.currency, 0.0) + p.market_value
    cash_map = {"CAD": cash} if not isinstance(cash, dict) else cash
    navs = nav if nav is not None else {
        c: by_ccy.get(c, 0.0) + cash_map.get(c, 0.0)
        for c in set(by_ccy) | set(cash_map)}
    return build_book(account_id=account, as_of=as_of, positions=positions,
                      cash_by_currency=cash_map, nav_by_currency=navs,
                      account_type=account_type, fx_rate_used=fx or {})


# --------------------------------------------------------------------------- #
# BS-15b — the book, B5's prerequisite. RC-10, RC-4, RC-19
# --------------------------------------------------------------------------- #

def test_the_book_reconciles_positions_plus_cash_against_nav():
    """RC-10 / INV-025 — the one check the whole book rests on."""
    b = book([pos(value=1000.0)], cash=250.0)
    assert b.reconciled == "ok" and b.breaks == ()
    assert b.nav_base == 1250.0


def test_a_break_raises_and_is_never_absorbed():
    """RC-10 — ⚠ *a break raises; it is never absorbed.*"""
    b = build_book(account_id="TFSA_1", as_of=AS_OF, positions=[pos(value=1000.0)],
                   cash_by_currency={"CAD": 0.0}, nav_by_currency={"CAD": 1100.0})
    assert b.reconciled == "break" and b.breaks[0].delta == -100.0
    with pytest.raises(BookBreakError, match="delta"):
        assert_reconciled(b)


def test_a_currency_missing_from_nav_is_a_break_not_a_currency_to_skip():
    """RC-10 — ★ the tempting `for ccy in nav_by_currency` loop passes a book
    that is missing a whole leg."""
    breaks = compute_breaks([pos(value=500.0, currency="USD")], {}, {"CAD": 0.0},
                            account_id="TFSA_1")
    assert [b.currency for b in breaks] == ["USD"]


def test_nav_base_is_null_without_an_fx_rate_never_a_guess():
    """FX-3 — ★ a single missing rate makes the whole aggregate unavailable."""
    b = build_book(account_id="TFSA_1", as_of=AS_OF,
                   positions=[pos(value=500.0, currency="USD")],
                   cash_by_currency={}, nav_by_currency={"USD": 500.0})
    assert b.nav_base is None
    with pytest.raises(CapitalBaseUnavailableError):
        capital_base(b)


def test_the_capital_base_is_read_from_the_book_never_configured():
    """RC-19 / BS-9 — ⚠ *every percentage cost figure is a function of a number
    that is currently the literal `20000.0` at `backtester.py:107`.*"""
    assert capital_base(book([pos(value=2000.0)])) == 2000.0


def test_an_unknown_account_type_raises_because_all_four_are_registered():
    """RC-25 / RK-16 — ★ M-4 has no exempt population."""
    with pytest.raises(ValueError, match="registered"):
        book(account_type="MARGIN")


def test_a_break_with_no_breaks_listed_raises():
    """RC-10 / P5 — a break that cannot say what broke has absorbed itself."""
    with pytest.raises(ValueError, match="absorbed itself"):
        BookState(account_id="X", date=AS_OF, positions=(), cash_by_currency={},
                  nav_by_currency={}, reconciled="break")


# --------------------------------------------------------------------------- #
# EXPOSURE §5 — AC-5.1…5.7, 5.6a
# --------------------------------------------------------------------------- #

def test_ac_5_1_exposure_is_reported_on_all_five_dimensions():
    """AC-5.1 / RK-1 — *any one alone understates a concentrated book.*"""
    view = exposure([book()], as_of=AS_OF, taxonomy=THEMES_V1)
    obj = view.to_json_obj()
    for dimension in ("by_name", "by_sector", "by_theme", "by_currency",
                      "by_account"):
        assert obj[dimension], dimension


def test_ac_5_2_every_threshold_crossing_is_reported_only():
    """AC-5.2 / RK-2, INV-026 — ★ *tracked, not blocked — concentration is
    intentional.*"""
    view = exposure([book([pos("MU", 900.0), pos("KO", 100.0, sector="Staples")])],
                    as_of=AS_OF, taxonomy=THEMES_V1)
    crossings = thresholds_crossed(view)
    assert crossings and all(c.effect == REPORTED_ONLY for c in crossings)
    assert all(c.alert_level == 2 for c in crossings)
    names = {c.name for c in crossings}
    assert {"CONCENTRATION_THRESHOLD_PCT", "SECTOR_MAX_PCT",
            "THEME_REPORT_THRESHOLD_PCT"} <= names


def test_a_threshold_that_claims_to_block_raises():
    """RK-2 / INV-026 — there is no other value for `effect`."""
    from src.risk import ThresholdCrossing

    with pytest.raises(BlockAttemptedError):
        ThresholdCrossing("SECTOR_MAX_PCT", 35.0, 74.0, effect="blocked")


def test_ac_5_3_a_cdr_and_its_underlying_are_one_exposure():
    """AC-5.3 / RK-5 — ★ *holding MU as a CDR in the RRSP and as the US stock in
    a TFSA is **one position in Micron**, and reporting them separately
    understates concentration by exactly the amount that matters.*"""
    cdr = pos("MU", 600.0, instrument="MU.NE.CAD", account="RRSP_1")
    us = pos("MU", 400.0, instrument="MU.US.CAD", account="TFSA_1")
    view = exposure([book([cdr], account="RRSP_1", account_type="RRSP"),
                     book([us], account="TFSA_1")],
                    as_of=AS_OF, taxonomy=THEMES_V1)
    assert view.by_name == {"MU": 100.0}          # one line, not two
    assert set(view.by_account) == {"RRSP_1", "TFSA_1"}


def test_ac_5_4_cross_currency_aggregation_with_no_rate_is_unavailable():
    """AC-5.4 / RK-3, FX-3 — ★ **unavailable, never estimated.**"""
    b = build_book(account_id="TFSA_1", as_of=AS_OF,
                   positions=[pos(value=500.0, currency="USD")],
                   cash_by_currency={}, nav_by_currency={"USD": 500.0})
    with pytest.raises(FxUnavailableError):
        exposure([b], as_of=AS_OF, taxonomy=THEMES_V1)


def test_ac_5_5_the_resp_exclusion_is_stated_not_assumed():
    """AC-5.5 / RC-4 — *an RESP is not the fund.*"""
    view = exposure([book(account="TFSA_1"),
                     book([pos("NVDA", 500.0)], account="RESP_1",
                          account_type="RESP")],
                    as_of=AS_OF, taxonomy=THEMES_V1)
    assert view.resp_excluded is True
    assert view.excluded_accounts == ("RESP_1",)
    assert "RESP_1" not in view.by_account
    assert view.to_json_obj()["resp_excluded"] is True


def test_ac_5_6_a_theme_threshold_with_no_taxonomy_raises():
    """AC-5.6 / RK-6 — ⚠ **a threshold on an undefined set is unenforceable**,
    and *the one threshold M-2 explicitly calls out is the one with no
    definition behind it.*"""
    with pytest.raises(NoTaxonomyError):
        exposure([book()], as_of=AS_OF, taxonomy=None)
    with pytest.raises(NoTaxonomyError, match="membership rule"):
        ThemeTaxonomy("themes.v9", "   ", (Theme("x"),))
    with pytest.raises(NoTaxonomyError, match="no version"):
        ThemeTaxonomy("", "a rule", (Theme("x"),))


def test_ac_5_6a_d05_resolves_theme_from_d02s_sector_and_d02_publishes_none():
    """AC-5.6a / RK-37, FE-21 — ★ *theme membership is a judgement call about
    what counts*, and a judgement belongs on a seat, not on neutral ground."""
    assert THEMES_V1.resolve(symbol="MU", sector="Information Technology") == \
        "ai_semiconductor"
    # ⚠ a Position carries `sector`; there is no `theme` field to supply.
    assert not hasattr(pos(), "theme")
    assert "theme" not in pos().to_json_obj()
    # and the taxonomy version travels with the aggregate.
    assert exposure([book()], as_of=AS_OF,
                    taxonomy=THEMES_V1).taxonomy_version == "themes.v1"


def test_ac_5_7_an_unclassifiable_theme_is_counted_never_dropped():
    """AC-5.7 / RK-7 — ⚠ dropping it *would understate the very concentration
    being tracked.*"""
    view = exposure([book([pos("MU", 600.0), pos("KO", 400.0, sector="Staples")])],
                    as_of=AS_OF, taxonomy=THEMES_V1)
    assert view.by_theme == {"ai_semiconductor": 60.0, UNCLASSIFIED: 40.0}
    assert sum(view.by_theme.values()) == pytest.approx(100.0)


def test_the_unclassified_residual_is_not_thresholded():
    """RK-7 — the residual is *visible*, not an alert about an unnamed set."""
    view = exposure([book([pos("KO", 1000.0, sector="Staples")])],
                    as_of=AS_OF, taxonomy=THEMES_V1)
    assert view.by_theme == {UNCLASSIFIED: 100.0}
    assert not [c for c in thresholds_crossed(view)
                if c.name == "THEME_REPORT_THRESHOLD_PCT"]


# --------------------------------------------------------------------------- #
# MEASUREMENT §6 — AC-5.8…5.11
# --------------------------------------------------------------------------- #

def risk_obj(**kw):
    view = exposure([book()], as_of=AS_OF, taxonomy=THEMES_V1)
    base = dict(as_of=AS_OF, base_currency="CAD", exposure=view,
                thresholds_crossed=thresholds_crossed(view),
                drawdown=drawdown([book(as_of=AS_OF - timedelta(days=1)), book()]),
                factors_for_d06={})
    return BookRisk(**{**base, **kw})


def test_ac_5_8_concentration_and_drawdown_are_present_whenever_risk_is_reported():
    """AC-5.8 / RK-8 — *direct, assumption-free, and they say what a correlated
    book actually risks.*"""
    obj = risk_obj().to_json_obj()
    assert obj["exposure"]["by_theme"] and obj["drawdown"]["depth_pct"] is not None


def test_ac_5_9_var_states_method_window_assumption_and_breadth():
    """AC-5.9 / RK-9 — ⚠ *a VaR without those is a number with borrowed
    authority.*"""
    with pytest.raises(VarMethodUnstatedError, match="effective_breadth"):
        risk_obj(var={"value": 4100.0, "method": "historical", "window": 250,
                      "assumption": "empirical"})
    ok = risk_obj(var={"value": 4100.0, "method": "historical", "window": 250,
                       "assumption": "empirical", "effective_breadth": 1.6})
    assert ok.var["effective_breadth"] == 1.6


def test_ac_5_10_var_without_concentration_fails():
    """AC-5.10 / RK-10 — ★★ **VaR is never the headline.**

    *"95% 1-day VaR is $4,100" and "you are 62% in one theme" are the same fact.
    The second is checkable, needs no distribution assumption, and cannot be
    quietly wrong.*
    """
    empty = dataclasses.replace(
        exposure([book()], as_of=AS_OF, taxonomy=THEMES_V1), by_theme={})
    with pytest.raises(VarWithoutConcentrationError):
        risk_obj(exposure=empty,
                 var={"value": 4100.0, "method": "historical", "window": 250,
                      "assumption": "empirical", "effective_breadth": 1.6})


def test_var_omitted_carries_its_reason():
    """RK-10 — ★ `var: null` with a stated reason is a legitimate outcome."""
    obj = risk_obj().to_json_obj()
    assert obj["var"] is None and "effective breadth" in obj["var_omitted_reason"]


def test_ac_5_11_correlation_is_reported_with_its_estimation_window():
    """AC-5.11 / RK-11 — ⚠ *correlations among semiconductor names in a drawdown
    converge toward 1; a matrix estimated in a calm window understates exactly
    when it matters.*"""
    with pytest.raises(ValueError, match="estimation window"):
        risk_obj(correlation={"mean": 0.81})
    assert risk_obj(correlation={"mean": 0.81, "window": 120}).correlation["window"] == 120


# --------------------------------------------------------------------------- #
# FLAGS §7 — AC-5.12…5.18, 5.13a
# --------------------------------------------------------------------------- #

def test_ac_5_12_a_buy_raising_average_cost_is_flagged_with_before_and_after():
    """AC-5.12 / RK-12, M-3, INV-028 — the mandate's stated behavioural problem."""
    flag = pyramiding_flag(ticker="MU", account="TFSA_1", as_of=AS_OF,
                           avg_cost_before=100.0, avg_cost_after=112.0,
                           added_value=2500.0)
    assert flag.kind == "pyramiding"
    assert flag.detail["avg_cost_before"] == 100.0
    assert flag.detail["avg_cost_after"] == 112.0
    assert pyramiding_flag(ticker="MU", account="TFSA_1", as_of=AS_OF,
                           avg_cost_before=100.0, avg_cost_after=94.0,
                           added_value=2500.0) is None


def test_ac_5_13_a_premature_exit_is_flagged_the_symmetric_case():
    """AC-5.13 / RK-14 — ⚠ **a domain that flags only scale-ins implements half
    the mandate and silently biases toward selling.**"""
    history = HoldingPeriods(days=(120, 200, 340, 410, 260))
    flag = premature_exit_flag(ticker="NVDA", account="TFSA_1", as_of=AS_OF,
                               held_days=30, unrealised_gain_pct=42.0,
                               history=history)
    assert flag.kind == "premature_exit"
    assert flag.detail["percentile_of_book"] == 0.0


def test_ac_5_13a_the_premature_exit_flag_uses_a_distribution_not_a_threshold():
    """AC-5.13a / RK-39 — ★ *a fixed "exited inside N days" repeats the
    fixed-percentage mistake D-06 QS-1 rejects*, **and the only artifact carrying
    an intended horizon is the thesis, which RK-28 forbids D-05 to import.**"""
    history = HoldingPeriods(days=(10, 20, 30, 40, 50))
    # 30 days is the MEDIAN of this book — unremarkable here, extreme above.
    assert premature_exit_flag(ticker="NVDA", account="TFSA_1", as_of=AS_OF,
                               held_days=30, unrealised_gain_pct=42.0,
                               history=history) is None
    flag = premature_exit_flag(ticker="NVDA", account="TFSA_1", as_of=AS_OF,
                               held_days=10, unrealised_gain_pct=42.0,
                               history=history)
    assert flag is not None and flag.detail["book_median_days"] == 30
    assert "no fixed threshold" in flag.detail["basis"]

    import inspect
    import src.risk.flags.behavioural as module
    assert "thesis" not in inspect.getsource(module.premature_exit_flag)


def test_a_loss_making_exit_is_not_a_premature_exit():
    """RK-14 — *"sell less and let winners run"* is about **winners**."""
    history = HoldingPeriods(days=(120, 200, 340))
    assert premature_exit_flag(ticker="NVDA", account="TFSA_1", as_of=AS_OF,
                               held_days=5, unrealised_gain_pct=-12.0,
                               history=history) is None


def test_ac_5_14_a_round_trip_under_thirty_days_in_a_registered_account_is_flagged():
    """AC-5.14 / RK-15, M-4 — the sample data already trips this (D-11 §5.3 H-6)."""
    trips = [{"ticker": "MU", "account": "RRSP_1", "held_days": 1,
              "closed_on": AS_OF},
             {"ticker": "NVDA", "account": "TFSA_1", "held_days": 200,
              "closed_on": AS_OF}]
    flags = short_hold_flags(trips, as_of=AS_OF)
    assert [f.ticker for f in flags] == ["MU"]
    assert flags[0].detail["window_days"] == REGISTERED_SHORT_HOLD_DAYS


def test_ac_5_15_m4_has_no_exempt_account_population():
    """AC-5.15 / RK-16, RC-25 — ★ *any design routing tactical activity to a
    "non-registered sleeve" is describing an account that does not exist.*"""
    from src.recording.book.models import EXCLUDED_FROM_FUND, REGISTERED_TYPES

    assert set(REGISTERED_TYPES) == {"TFSA", "RRSP", "RESP", "FHSA"}
    trips = [{"ticker": "MU", "account": a, "held_days": 3, "closed_on": AS_OF}
             for a in ("TFSA_1", "RRSP_1", "RESP_1", "FHSA_1")]
    assert len(short_hold_flags(trips, as_of=AS_OF)) == 4
    # ⚠ the RESP is excluded from EXPOSURE (RC-4) and not from M-4.
    assert EXCLUDED_FROM_FUND == ("RESP",)


def test_ac_5_16_the_flag_reports_trailing_count_and_frequency():
    """AC-5.16 / RK-17 — ★ *CRA's "carrying on a business" test weighs PATTERN;
    a single fast round trip is unremarkable and twenty is the finding.*"""
    trips = [{"ticker": "MU", "account": "RRSP_1", "held_days": d,
              "closed_on": AS_OF} for d in (1, 2, 3, 400)]
    flags = short_hold_flags(trips, as_of=AS_OF)
    assert all(f.trailing_count == 3 for f in flags)
    assert flags[0].detail["trailing_frequency"] == 0.75


def test_ac_5_17_any_attempt_to_suppress_a_flag_raises():
    """AC-5.17 / RK-18, INV-021 — ★ **a flag that can be turned off is a flag
    that will be off when it matters.**"""
    with pytest.raises(SuppressionAttemptedError):
        suppress("M4:MU:RRSP_1:2026-08-25")
    with pytest.raises(SuppressionAttemptedError, match="no other value"):
        Flag(flag_id="f", kind="pyramiding", ticker="MU", account="TFSA_1",
             as_of=AS_OF, detail={}, suppressed=True)


def test_ac_5_18_acknowledging_records_and_does_not_stop_it_rendering():
    """AC-5.18 / RK-19 — ★ **acknowledged is not suppressed.**"""
    flag = pyramiding_flag(ticker="MU", account="TFSA_1", as_of=AS_OF,
                           avg_cost_before=100.0, avg_cost_after=112.0,
                           added_value=2500.0)
    seen = acknowledge(flag, at="2026-08-25T20:00:00Z")
    assert seen.acknowledged_at == "2026-08-25T20:00:00Z"
    assert seen.suppressed is False
    assert seen.to_json_obj()["suppressed"] is False


# --------------------------------------------------------------------------- #
# FACTORS §8 — AC-5.19, 5.19a, 5.20, 5.21
# --------------------------------------------------------------------------- #

def series(navs):
    return [book([pos(value=v)], as_of=AS_OF - timedelta(days=len(navs) - i - 1))
            for i, v in enumerate(navs)]


def test_ac_5_19_drawdown_is_computable_from_the_book_alone():
    """AC-5.19 / RK-21 — ★ *`D` waits on nothing*, and **a risk budget that
    shrinks in a drawdown is already meaningfully better than a constant.**"""
    state = drawdown(series([100.0, 120.0, 105.6]))
    assert state.peak == 120.0 and state.current == 105.6
    assert state.depth_pct == pytest.approx(12.0)
    assert state.duration_days == 1
    assert state.factor == pytest.approx(0.88)

    import inspect
    import src.risk.metrics.drawdown as module
    source = inspect.getsource(module)
    assert "feature_engineer" not in source and "src.models" not in source


def test_ac_5_19a_an_incomplete_series_is_unmeasured_never_zero_drawdown():
    """AC-5.19a / RK-38, RK-36 — ★ **a book whose history begins today is at its
    peak by construction**, and *"no drawdown"* is the most misleading possible
    reading of it."""
    state = drawdown(series([100.0]))
    assert state.status == UNMEASURED
    assert state.depth_pct is None and state.factor is None
    assert "at its peak by construction" in state.why


def test_an_unreconciled_state_is_excluded_from_the_drawdown_series():
    """RK-0 — *a `BookState` with `reconciled: "break"` is not a risk input.*"""
    broken = build_book(account_id="TFSA_1", as_of=AS_OF,
                        positions=[pos(value=1000.0)],
                        cash_by_currency={"CAD": 0.0},
                        nav_by_currency={"CAD": 5000.0})
    assert drawdown([broken] + series([100.0])).status == UNMEASURED


def test_ac_5_20_marginal_risk_is_marginal_not_standalone():
    """AC-5.20 / RK-20 — ★ *a sixth semiconductor name adds far less
    diversification and far more concentration than its own volatility
    suggests.* ⚠ **Standalone vol would size it as though the book were empty.**
    """
    vols = {"MU": 0.40, "NVDA": 0.45, "AMD": 0.42}
    correlated = {("MU", "NVDA"): 0.9, ("MU", "AMD"): 0.9, ("NVDA", "AMD"): 0.9}
    diversifying = {k: 0.05 for k in correlated}

    weights = {"MU": 0.5, "NVDA": 0.5}
    tight = marginal_risk(ticker="AMD", weight=0.2, weights=weights, vols=vols,
                          correlations=correlated, as_of=AS_OF, window=120)
    loose = marginal_risk(ticker="AMD", weight=0.2, weights=weights, vols=vols,
                          correlations=diversifying, as_of=AS_OF, window=120)
    # ★ the same standalone vol, a very different marginal contribution.
    assert tight.standalone_vol == loose.standalone_vol
    assert tight.marginal_vol > loose.marginal_vol
    assert tight.to_json_obj()["correlation_window"] == 120


def test_ac_5_21_an_uncomputable_factor_returns_unmeasured_never_an_estimate():
    """AC-5.21 / RK-23, PS-34 — ★ *a value, not a failure.*

    ⚠ A missing correlation is not an excuse to assume zero, which would make
    the name look free.
    """
    result = marginal_risk(ticker="AMD", weight=0.2, weights={"MU": 1.0},
                           vols={"MU": 0.4, "AMD": 0.42}, correlations={},
                           as_of=AS_OF, window=120)
    assert isinstance(result, Unmeasured)
    assert result.status == UNMEASURED and "correlation" in result.why

    novol = marginal_risk(ticker="AMD", weight=0.2, weights={"MU": 1.0},
                          vols={"MU": 0.4}, correlations={}, as_of=AS_OF,
                          window=120)
    assert isinstance(novol, Unmeasured) and "volatility" in novol.why


def test_rk31_a_candidate_is_measured_on_the_same_book_shape():
    """RK-31 — ★ *a candidate evaluated by different code is a different
    measurement.* (INV-4's train/inference parity, applied to risk.)"""
    b = book()
    hypothetical = hypothetical_book(b, pos("NVDA", 500.0))
    assert type(hypothetical) is type(b)
    assert len(hypothetical.positions) == len(b.positions) + 1
    assert b.positions == book().positions          # the original is untouched


# --------------------------------------------------------------------------- #
# WF-R1 §4A.2 — the ladder. RK-29, RK-30, RK-34, RK-35
# --------------------------------------------------------------------------- #

def test_rk29_the_pass_refuses_on_an_unreconciled_book():
    """★★ RK-29 — ⚠ *the tempting alternative, compute on the last good book, is
    worse: it produces a correct-looking risk report **about yesterday**, and
    nothing on the artifact would say so.*"""
    broken = build_book(account_id="TFSA_1", as_of=AS_OF,
                        positions=[pos(value=1000.0)],
                        cash_by_currency={"CAD": 0.0},
                        nav_by_currency={"CAD": 1100.0})
    with pytest.raises(NoBookError, match="unreconciled"):
        daily_book_pass(as_of=AS_OF, books=[broken], taxonomy=THEMES_V1)
    with pytest.raises(NoBookError, match="no book states"):
        daily_book_pass(as_of=AS_OF, books=[], taxonomy=THEMES_V1)


def test_rk30_alerts_are_emitted_only_from_a_complete_pass():
    """★★ RK-30 — ⚠ *because this domain's whole value is that silence means
    "nothing found", a partial run that emits three of five alerts has told the
    reader the other two categories are clear.*"""
    risk, alerts = daily_book_pass(
        as_of=AS_OF, books=[book([pos("MU", 900.0),
                                  pos("KO", 100.0, sector="Staples")])],
        taxonomy=THEMES_V1,
        history=series([100.0, 120.0, 105.6]))
    assert alerts.status == "COMPLETE"
    assert alerts.alerts and all(a.level == 2 for a in alerts.alerts)
    assert all(not a.blocking and not a.suppressible for a in alerts.alerts)


def test_the_pass_publishes_a_complete_book_risk():
    """RK-35 / §4A.2 step 7 — *contracts are published complete.*"""
    risk, _ = daily_book_pass(as_of=AS_OF, books=[book()], taxonomy=THEMES_V1,
                              history=series([100.0, 120.0, 105.6]))
    obj = risk.to_json_obj()
    assert obj["exposure"]["by_theme"] and obj["drawdown"]["status"] == "ok"
    assert obj["factors_for_d06"]["D"]["factor"] == pytest.approx(0.88)
    assert obj["factors_for_d06"]["P"]["status"] == UNMEASURED


def test_ac_5_22_a_request_to_veto_or_downgrade_raises():
    """AC-5.22 / RK-27, RK-34, INV-026 — ★ *there is no gate step, and its
    absence is deliberate.* **Stating that it does not exist is cheaper than
    having someone add it.**"""
    with pytest.raises(BlockAttemptedError):
        refuse_to_block("D-12")
    import src.risk as risk_pkg
    assert not [n for n in dir(risk_pkg)
                if n in ("block", "veto", "gate", "approve", "reject")]


def test_ac_5_23_src_risk_imports_no_gateway_no_d01_and_not_d08():
    """AC-5.23 / RK-28, AP-5, ST-5 — the seat that sees everything and decides
    nothing does not need any of them."""
    from tests_src import architecture

    graph = architecture.scan()
    reached = {m for f, mods in graph.items() if f.startswith("src/risk/")
               for m in mods}
    assert not {m for m in reached
                if m.startswith(("src.fundamental", "src.orchestration"))}
    assert not [m for m in reached if "gateway" in m or m == "anthropic"]


# --------------------------------------------------------------------------- #
# STRESS §9 — RK-24, RK-25, RK-26
# --------------------------------------------------------------------------- #

def test_rk24_a_scenario_states_its_source_or_its_assumption():
    """RK-24 — ★ a scenario that states neither is a number with an author and
    no provenance."""
    from src.risk import Scenario

    with pytest.raises(ValueError, match="neither"):
        Scenario("bad", {"ai_semiconductor": -0.4})
    assert SEMI_2022.historical_source


def test_rk26_the_informative_stress_is_a_single_theme_shock():
    """RK-26 — ⚠ *a broad-market scenario mostly restates beta.*"""
    view = exposure([book([pos("MU", 600.0), pos("KO", 400.0, sector="Staples")])],
                    as_of=AS_OF, taxonomy=THEMES_V1)
    result = stress(view, SEMI_2022, as_of=AS_OF)
    assert result.impact_by_theme == {"ai_semiconductor": -27.0}
    assert "NOT A PREDICTION" in result.label


def test_rk25_stress_is_deterministic():
    """RK-25 / INV-2 — reproducible given the book and the scenario definition."""
    view = exposure([book()], as_of=AS_OF, taxonomy=THEMES_V1)
    a = stress(view, SEMI_2022, as_of=AS_OF).to_json_obj()
    b = stress(view, SEMI_2022, as_of=AS_OF).to_json_obj()
    assert a == b
