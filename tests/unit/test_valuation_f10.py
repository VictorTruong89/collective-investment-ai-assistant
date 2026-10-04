"""`F10` — the valuation trail (D-02). One test per acceptance criterion, named.

★ The known answers are worked with plain `Decimal` arithmetic INSIDE the test,
independently of `valuation/`, so the code under test never grades itself.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, localcontext

import pandas as pd
import pytest

from src.shared.money import Money

USD = "USD"


def usd(major: int | str) -> Money:
    return Money.from_decimal_str(str(major), USD)


@pytest.fixture
def assumptions():
    from src.feature_engineer.valuation.assumptions import load_published
    return load_published("dcf_two_stage", 1)


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.1 — the mechanics, known answer
# ═══════════════════════════════════════════════════════════════════════════

def _hand_worked(base_minor: int, r: Decimal, g1: Decimal, gt: Decimal, n: int):
    """The textbook two-stage DCF, independently: each figure rounded half-up to
    minor units exactly once (`CT-F10.2` rounding rule)."""
    def q(x: Decimal) -> int:
        return int(x.quantize(Decimal(1), rounding=ROUND_HALF_UP))
    with localcontext() as ctx:
        ctx.prec = 50
        flows, pvs = [], []
        for t in range(1, n + 1):
            flow = q(Decimal(base_minor) * (1 + g1) ** t)
            df = Decimal(1) / (1 + r) ** t
            flows.append(flow)
            pvs.append(q(Decimal(flow) * df))
        tv_flow = q(Decimal(base_minor) * (1 + g1) ** n * (1 + gt))
        tv = q(Decimal(tv_flow) / (r - gt))
        tv_pv = q(Decimal(tv) / (1 + r) ** n)
    return flows, pvs, tv_flow, tv, tv_pv, sum(pvs) + tv_pv


def test_ac_f10_1_the_mechanics_match_a_hand_worked_two_stage_dcf():
    """AC-F10.1 — every flow, present value, terminal figure and EV."""
    from src.feature_engineer.valuation.dcf import discount

    r, g1, gt, n = Decimal("0.09"), Decimal("0.05"), Decimal("0.025"), 5
    trail = discount(usd(1000), discount_rate=r, stage1_growth=g1,
                     terminal_growth=gt, explicit_years=n)
    flows, pvs, tv_flow, tv, tv_pv, ev = _hand_worked(100_000, r, g1, gt, n)
    assert [f.fcff.amount_minor for f in trail.flows] == flows
    assert [f.present_value.amount_minor for f in trail.flows] == pvs
    assert trail.terminal_fcff.amount_minor == tv_flow
    assert trail.terminal_value.amount_minor == tv
    assert trail.terminal_present_value.amount_minor == tv_pv
    assert trail.enterprise_value.amount_minor == ev
    # ★ the trail adds up to the cent: EV is the exact sum of the rounded fields
    assert ev == sum(f.present_value.amount_minor for f in trail.flows) + tv_pv


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.2 — D-19 cannot recur
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(("ev", "net_debt", "shares"), [
    (16_000_000_000, 2_000_000_000, 100_000_000),
    (5_000_000_000, -1_500_000_000, 37_000_001),     # net CASH
    (1_234_567_891, 999_999_999, 7),
])
def test_ac_f10_2_value_per_share_subtracts_net_debt(ev, net_debt, shares):
    """AC-F10.2 — `(EV − net debt) ÷ shares`, and the gap to `EV ÷ shares` is net
    debt per share within one minor unit. ⚠ `D-19` divided EV by shares."""
    from src.feature_engineer.valuation.dcf import per_share

    ev_m, nd_m = Money(ev, USD), Money(net_debt, USD)
    equity, vps = per_share(ev_m, nd_m, shares)
    assert equity == ev_m - nd_m
    assert vps == (ev_m - nd_m).div_int(shares)
    gap = ev_m.div_int(shares).amount_minor - vps.amount_minor
    assert abs(gap - nd_m.div_int(shares).amount_minor) <= 1


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.3 — no finite answer refuses
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(("r", "gt"), [("0.025", "0.025"), ("0.02", "0.03")])
def test_ac_f10_3_discount_rate_not_above_terminal_growth_refuses(r, gt):
    from src.feature_engineer.errors import NoFiniteValueError
    from src.feature_engineer.valuation.dcf import discount

    with pytest.raises(NoFiniteValueError):
        discount(usd(1000), discount_rate=Decimal(r), stage1_growth=Decimal("0.02"),
                 terminal_growth=Decimal(gt), explicit_years=10)


@pytest.mark.parametrize("shares", [0, -5])
def test_ac_f10_3_non_positive_shares_refuses(shares):
    from src.feature_engineer.errors import NoFiniteValueError
    from src.feature_engineer.valuation.dcf import per_share

    with pytest.raises(NoFiniteValueError):
        per_share(usd(100), usd(10), shares)


# ═══════════════════════════════════════════════════════════════════════════
# The reported-basis fixture: CT-7.2-shaped rows, four discrete EDGAR quarters
# ═══════════════════════════════════════════════════════════════════════════

TAGS = {
    "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities",
    "interest_expense": "InterestExpense",
    "income_tax": "IncomeTaxExpenseBenefit",
    "pretax_income": "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    "capex": "PaymentsToAcquirePropertyPlantAndEquipment",
    "sbc": "ShareBasedCompensation",
    "cash": "CashAndCashEquivalentsAtCarryingValue",
    "long_term_debt": "LongTermDebtNoncurrent",
    "current_debt": "LongTermDebtCurrent",
    "diluted_shares": "WeightedAverageNumberOfDilutedSharesOutstanding",
    "marketable_securities_current": "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
    "marketable_securities_noncurrent": "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent",
    "finance_lease_current": "FinanceLeaseLiabilityCurrent",
    "finance_lease_noncurrent": "FinanceLeaseLiabilityNoncurrent",
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",       # D11
}
QUARTERS = [(date(2024, 8, 30), date(2024, 11, 28), date(2024, 12, 18)),
            (date(2024, 11, 29), date(2025, 2, 27), date(2025, 3, 21)),
            (date(2025, 2, 28), date(2025, 5, 29), date(2025, 6, 25)),
            (date(2025, 5, 30), date(2025, 8, 28), date(2025, 10, 3))]
AS_OF = date(2025, 10, 10)


def _row(start, end, filed, *, source="edgar", **items_major):
    row = {"ticker": "XYZ", "period_start": start, "period_end": end,
           "period_type": "quarterly", "filing_date": filed, "source": source,
           "accession_id": f"acc-{end.isoformat()}" if source == "edgar" else None}
    for item, major in items_major.items():
        tag = TAGS[item]
        row[f"{tag}_minor"] = int(major) if item == "diluted_shares" else int(major) * 100
        row[f"{tag}_currency"] = "" if item == "diluted_shares" else USD
    return row


def rows(over: dict | None = None):
    flow = dict(operating_cash_flow=3000, interest_expense=100, income_tax=250,
                pretax_income=1000, capex=2000, sbc=200, revenue=10_000)
    stock = dict(cash=5000, long_term_debt=8000, current_debt=1000, diluted_shares=1_000)
    out = []
    for i, (s, e, f) in enumerate(QUARTERS):
        items = dict(flow)
        if i == len(QUARTERS) - 1:
            items.update(stock)
        items.update((over or {}).get(i, {}))
        out.append(_row(s, e, f, **items))
    return pd.DataFrame(out)


class FakeEngine:
    """D-07's public surface, as `valuation()` uses it (`FE-23`)."""

    def __init__(self, fundamentals: pd.DataFrame, price_minor=4000, price_currency=USD,
                 price_date=date(2025, 10, 9)):
        self._f, self.calls = fundamentals, []
        self._price = (price_minor, price_currency, price_date)

    def get_fundamentals(self, ticker, as_of=None, period_type=None):
        self.calls.append(("get_fundamentals", ticker, as_of, period_type))
        f = self._f[self._f["filing_date"] <= as_of]
        return f[f["period_type"] == period_type].reset_index(drop=True) if period_type else f

    def get_prices(self, ticker, start, end, adj_as_of=object()):
        self.calls.append(("get_prices", ticker, start, end, adj_as_of))
        m, c, d = self._price
        frame = pd.DataFrame([{"date": d, "close_minor": m, "close_currency": c,
                               "adj_close_minor": m // 2, "adj_close_currency": c}])
        return frame[(frame["date"] >= start) & (frame["date"] <= end)]


def _value(engine, assumptions, as_of=AS_OF):
    from src.feature_engineer.valuation.service import valuation
    return valuation("XYZ", as_of, engine=engine, assumptions=assumptions)


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.17 — the D6 cash-flow formula
# ═══════════════════════════════════════════════════════════════════════════

def test_ac_f10_17_the_reported_basis_is_ocf_plus_after_tax_interest_minus_capex_minus_sbc():
    """AC-F10.17 — TTM: OCF 12,000 · interest 400 · tax 1,000 on pretax 4,000
    (t = 0.25) · capex 8,000 · SBC 800 ⇒ 12,000 + 400×0.75 − 8,000 − 800 = 3,500."""
    from src.feature_engineer.valuation.basis import reported_basis

    basis = reported_basis(rows(), as_of=AS_OF, ticker="XYZ")
    assert basis.base_fcff == usd(3500)
    assert basis.tax_rate == Decimal("0.25")
    assert basis.formula_id == "fcff.ocf_plus_after_tax_interest_minus_capex_minus_sbc.v2"
    assert basis.tax_rule == "effective"
    assert basis.origin == "reported"


@pytest.mark.parametrize(("pretax", "tax"), [(0, 10), (-100, -30)])
def test_ac_f10_17_a_loss_year_uses_a_zero_tax_rate(pretax, tax):
    """AC-F10.17 ✏ `DX-104` — pretax ≤ 0 ⇒ t = 0, recorded: interest added back in
    full ⇒ 12,000 + 400 − 8,000 − 800 = 3,600, whatever the tax line says."""
    import json

    from src.feature_engineer.valuation.basis import reported_basis

    loss = rows({i: {"pretax_income": pretax, "income_tax": tax} for i in range(4)})
    basis = reported_basis(loss, as_of=AS_OF, ticker="XYZ")
    assert basis.base_fcff == usd(3600) and basis.tax_rate == Decimal(0)
    assert basis.tax_rule == "loss_year_zero"
    assert json.loads(json.dumps(basis.to_json_obj(), default=str))["tax_rate"]["rule"] == \
        "loss_year_zero"


@pytest.mark.parametrize(("pretax", "tax"), [(1000, 1500), (1000, -50)])
def test_ac_f10_17_an_out_of_range_rate_on_a_profit_refuses_and_names_it(pretax, tax):
    """AC-F10.17 — never a substituted statutory rate (`P5`)."""
    from src.feature_engineer.errors import ValuationUnavailable
    from src.feature_engineer.valuation.basis import reported_basis

    bad = rows({i: {"pretax_income": pretax, "income_tax": tax} for i in range(4)})
    with pytest.raises(ValuationUnavailable) as exc:
        reported_basis(bad, as_of=AS_OF, ticker="XYZ")
    assert "tax_rate" in exc.value.missing


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.7 — trailing = four discrete quarters
# ═══════════════════════════════════════════════════════════════════════════

def test_ac_f10_7_the_trailing_basis_sums_four_discrete_contiguous_quarters():
    from src.feature_engineer.valuation.basis import reported_basis

    basis = reported_basis(rows(), as_of=AS_OF, ticker="XYZ")
    ocf = [i for i in basis.inputs if i["item"] == "operating_cash_flow"]
    assert len(ocf) == 4
    for i in ocf:
        assert 80 <= (i["period_end"] - i["period_start"]).days <= 100
        assert i["source"] == "edgar"


def test_ac_f10_7_a_cumulative_span_never_enters_as_a_quarter():
    """⚠ `fmp-api` trap 1 — a nine-month YTD figure labelled as a quarter."""
    from src.feature_engineer.errors import ValuationUnavailable
    from src.feature_engineer.valuation.basis import reported_basis

    frame = rows()
    frame.loc[2, "period_start"] = date(2024, 8, 30)          # a 272-day span
    with pytest.raises(ValuationUnavailable, match="discrete"):
        reported_basis(frame, as_of=AS_OF, ticker="XYZ")


def test_ac_f10_7_an_fmp_quarter_is_refused_where_edgar_quarters_exist():
    from src.feature_engineer.errors import ValuationUnavailable
    from src.feature_engineer.valuation.basis import reported_basis

    frame = rows()
    frame.loc[1, "source"] = "fmp"
    frame.loc[1, "accession_id"] = None
    with pytest.raises(ValuationUnavailable, match="EDGAR"):
        reported_basis(frame, as_of=AS_OF, ticker="XYZ")


def test_ac_f10_7_fewer_than_four_quarters_refuses():
    from src.feature_engineer.errors import ValuationUnavailable
    from src.feature_engineer.valuation.basis import reported_basis

    frame = rows().drop(index=1).reset_index(drop=True)
    with pytest.raises(ValuationUnavailable, match="only 3"):
        reported_basis(frame, as_of=AS_OF, ticker="XYZ")


def test_ac_f10_7_FOUR_quarters_with_a_hole_are_not_a_trailing_year():
    """⚠ Found by mutation: dropping a quarter tripped the COUNT check first, so
    contiguity was never tested. Here an older quarter keeps the count at four."""
    from src.feature_engineer.errors import ValuationUnavailable
    from src.feature_engineer.valuation.basis import reported_basis

    older = _row(date(2024, 5, 31), date(2024, 8, 29), date(2024, 9, 25),
                 operating_cash_flow=3000, interest_expense=100, income_tax=250,
                 pretax_income=1000, capex=2000, sbc=200)
    frame = pd.concat([pd.DataFrame([older]), rows().drop(index=1)]).reset_index(drop=True)
    with pytest.raises(ValuationUnavailable, match="not contiguous"):
        reported_basis(frame, as_of=AS_OF, ticker="XYZ")


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.8 — missing is not zero
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("item", ["operating_cash_flow", "capex", "sbc", "interest_expense"])
def test_ac_f10_8_a_missing_flow_item_names_itself(item, assumptions):
    from src.feature_engineer.errors import ValuationUnavailable

    frame = rows()
    frame.loc[3, f"{TAGS[item]}_minor"] = pd.NA
    with pytest.raises(ValuationUnavailable) as exc:
        _value(FakeEngine(frame), assumptions)
    assert exc.value.missing == [item]


@pytest.mark.parametrize("item", ["cash", "long_term_debt", "diluted_shares"])
def test_ac_f10_8_a_missing_balance_item_names_itself(item, assumptions):
    from src.feature_engineer.errors import ValuationUnavailable

    frame = rows()
    frame = frame.drop(columns=[f"{TAGS[item]}_minor"])
    with pytest.raises(ValuationUnavailable) as exc:
        _value(FakeEngine(frame), assumptions)
    assert item in exc.value.missing


def test_ac_f10_8_no_price_refuses(assumptions):
    from src.feature_engineer.errors import ValuationUnavailable

    with pytest.raises(ValuationUnavailable) as exc:
        _value(FakeEngine(rows(), price_date=date(2025, 11, 1)), assumptions)
    assert exc.value.missing == ["price"]


# ═══════════════════════════════════════════════════════════════════════════
# The full valuation — AC-F10.4, .5, .6, .9, .10, .11
# ═══════════════════════════════════════════════════════════════════════════

def test_ac_f10_4_recomputing_from_the_trail_alone_reproduces_everything(assumptions):
    """AC-F10.4 — the trail is complete: only fields of the serialised result."""
    from src.feature_engineer.valuation.dcf import discount, per_share
    from src.feature_engineer.valuation.implied import solve_implied

    res = _value(FakeEngine(rows()), assumptions)
    obj = json.loads(res.to_json())
    m = Money.from_json_obj
    a = res.assumptions_obj
    trail = discount(m(obj["basis"]["base_fcff"]), discount_rate=a.discount_rate,
                     stage1_growth=a.stage1_growth, terminal_growth=a.terminal_growth,
                     explicit_years=a.explicit_years)
    assert trail.enterprise_value == m(obj["enterprise_value"])
    _, vps = per_share(trail.enterprise_value, m(obj["net_debt"]["value"]),
                       obj["diluted_shares"])
    assert vps == m(obj["value_per_share"])
    for point in obj["band"]["grid"]:
        t = discount(m(obj["basis"]["base_fcff"]), discount_rate=Decimal(point["discount_rate"]),
                     stage1_growth=a.stage1_growth,
                     terminal_growth=Decimal(point["terminal_growth"]),
                     explicit_years=a.explicit_years)
        assert per_share(t.enterprise_value, m(obj["net_debt"]["value"]),
                         obj["diluted_shares"])[1] == m(point["value_per_share"])
    again = solve_implied(price=m(obj["price"]["value"]), base_fcff=m(obj["basis"]["base_fcff"]),
                          net_debt=m(obj["net_debt"]["value"]),
                          diluted_shares=obj["diluted_shares"], assumptions=a)
    assert again.to_json_obj() == obj["implied"]


def _monies(obj, path=""):
    if isinstance(obj, dict):
        if set(obj) == {"minor", "currency"}:
            yield path, obj
        for k, v in obj.items():
            yield from _monies(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _monies(v, f"{path}[{i}]")


def test_ac_f10_5_every_monetary_field_carries_one_currency(assumptions):
    res = _value(FakeEngine(rows()), assumptions)
    monies = list(_monies(json.loads(res.to_json())))
    assert len(monies) > 20
    assert {m["currency"] for _, m in monies} == {USD}


def test_ac_f10_5_a_second_currency_refuses(assumptions):
    """AC-F10.5 — a CAD price against a USD basis is not a comparison."""
    from src.shared.money import CurrencyMismatchError

    with pytest.raises(CurrencyMismatchError):
        _value(FakeEngine(rows(), price_currency="CAD"), assumptions)


def test_ac_f10_6_as_of_is_required(assumptions):
    from src.feature_engineer.errors import AsOfRequiredError
    from src.feature_engineer.valuation.service import valuation

    with pytest.raises(AsOfRequiredError):
        valuation("XYZ", engine=FakeEngine(rows()), assumptions=assumptions)
    with pytest.raises(AsOfRequiredError):
        valuation("XYZ", None, engine=FakeEngine(rows()), assumptions=assumptions)


def test_ac_f10_6_nothing_after_as_of_and_the_price_is_the_RAW_series(assumptions):
    engine = FakeEngine(rows(), price_minor=4000)
    res = _value(engine, assumptions)
    obj = json.loads(res.to_json())
    for i in obj["basis"]["inputs"]:
        assert date.fromisoformat(i["filing_date"]) <= AS_OF
    assert date.fromisoformat(obj["price"]["date"]) <= AS_OF
    assert obj["price"]["series"] == "raw" and obj["price"]["value"]["minor"] == 4000
    price_calls = [c for c in engine.calls if c[0] == "get_prices"]
    assert price_calls and all(c[4] is None for c in price_calls), "adj_as_of=None is RAW (DE-45)"
    fund = [c for c in engine.calls if c[0] == "get_fundamentals"]
    assert fund and all(c[2] == AS_OF for c in fund)


def test_ac_f10_6_a_filing_after_as_of_is_not_used(assumptions):
    """A quarter filed after `as_of` must not become the latest quarter."""
    from src.feature_engineer.errors import ValuationUnavailable

    with pytest.raises(ValuationUnavailable):
        _value(FakeEngine(rows()), assumptions, as_of=date(2025, 9, 1))


def test_ac_f10_9_the_band(assumptions):
    res = _value(FakeEngine(rows()), assumptions)
    grid = res.band.grid
    assert len(grid) == len(assumptions.band_discount) * len(assumptions.band_terminal)
    assert res.band.low <= res.value_per_share <= res.band.high
    for gt in assumptions.band_terminal:
        row = sorted((p for p in grid if p.terminal_growth == gt), key=lambda p: p.discount_rate)
        values = [p.value_per_share.amount_minor for p in row]
        assert values == sorted(values, reverse=True), "non-increasing in the discount rate"


def test_ac_f10_10_implied_growth_round_trips_to_the_price(assumptions):
    from src.feature_engineer.valuation.dcf import value_per_share_at

    res = _value(FakeEngine(rows()), assumptions)
    assert res.implied.status == "SOLVED"
    back = value_per_share_at(res.basis.base_fcff, res.net_debt, res.diluted_shares,
                              discount_rate=assumptions.discount_rate,
                              stage1_growth=res.implied.value,
                              terminal_growth=assumptions.terminal_growth,
                              explicit_years=assumptions.explicit_years)
    assert abs(back.amount_minor - res.price.amount_minor) <= 1


def test_ac_f10_10_a_price_outside_the_bracket_is_NO_ROOT_never_the_bracket_end(assumptions):
    res = _value(FakeEngine(rows(), price_minor=10**12), assumptions)
    assert res.implied.status == "NO_ROOT_IN_BRACKET"
    assert res.implied.value is None and res.implied.residual is None


def test_ac_f10_11_identical_inputs_serialise_byte_identically(assumptions):
    a = _value(FakeEngine(rows()), assumptions).to_json()
    b = _value(FakeEngine(rows()), assumptions).to_json()
    assert a == b


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.12 — assumptions are declared and versioned
# ═══════════════════════════════════════════════════════════════════════════

def test_ac_f10_12_the_published_set_is_D4(assumptions):
    """★ `D4`, as adopted — read from the config, asserted here once."""
    assert (assumptions.name, assumptions.version) == ("dcf_two_stage", 1)
    assert assumptions.discount_rate == Decimal("0.09")
    assert assumptions.terminal_growth == Decimal("0.025")
    assert assumptions.stage1_growth == Decimal("0.025")
    assert assumptions.explicit_years == 10
    assert assumptions.band_discount == tuple(Decimal(x) for x in ("0.08", "0.09", "0.10", "0.11"))
    assert assumptions.band_terminal == tuple(Decimal(x) for x in ("0.015", "0.025", "0.035"))
    assert (assumptions.implied_low, assumptions.implied_high, assumptions.implied_iterations) == (
        Decimal("-0.20"), Decimal("0.40"), 60)


def test_ac_f10_12_a_value_changed_without_a_version_change_refuses(tmp_path):
    import yaml

    from src.feature_engineer.errors import AssumptionsMutatedError
    from src.feature_engineer.valuation.assumptions import CONFIG_DIR, load

    doc = yaml.safe_load((CONFIG_DIR / "dcf_two_stage_v1.yaml").read_text())
    doc["discount_rate"]["value"] = "0.08"
    bad = tmp_path / "dcf_two_stage_v1.yaml"
    bad.write_text(yaml.safe_dump(doc))
    with pytest.raises(AssumptionsMutatedError):
        load(bad)


def test_ac_f10_12_a_grid_point_with_no_finite_value_refuses_at_load(tmp_path):
    import yaml

    from src.feature_engineer.errors import NoFiniteValueError
    from src.feature_engineer.valuation.assumptions import CONFIG_DIR, content_hash, load

    doc = yaml.safe_load((CONFIG_DIR / "dcf_two_stage_v1.yaml").read_text())
    doc["band"]["terminal_growth_steps"] = ["0.015", "0.09"]
    doc["content_hash"] = content_hash(doc)
    bad = tmp_path / "x.yaml"
    bad.write_text(yaml.safe_dump(doc))
    with pytest.raises(NoFiniteValueError):
        load(bad)


def test_ac_f10_12_no_assumption_value_is_a_literal_in_valuation_code(assumptions):
    import pathlib
    import re

    src = "\n".join(p.read_text() for p in
                    pathlib.Path("src/feature_engineer/valuation").glob("*.py"))
    code = re.sub(r'"""[\s\S]*?"""|#.*', "", src)        # docstrings/comments may explain
    for value in ("0.09", "0.025", "0.08", "0.11", "0.015", "0.035", "-0.20", "0.40"):
        assert value not in code, f"assumption literal {value} in valuation/ code"


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.13 — fv_model and fv_analyst never share a name
# ═══════════════════════════════════════════════════════════════════════════

PROVENANCE = {"block": "J-20", "prompt_version": "v1", "run_id": "run-x",
              "stage_commit_hash": "sha256:c", "bundle_hash": "sha256:b",
              "method": "cycle_average_margin",
              "window": {"start": "2016-01-01", "end": "2025-05-29"},
              "exclusions": [{"item": "inventory write-down", "evidence_id": "ap.change",
                              "quote": "…"}],
              "computed_by": "src.fundamental.valuation.normalise:v1"}


def test_ac_f10_13_a_judgement_basis_yields_fv_analyst_with_provenance(assumptions):
    from src.feature_engineer.valuation.service import value_on_basis
    from src.feature_engineer.valuation.types import (
        AnalystValuation,
        CashFlowBasis,
        ValuationResult,
    )

    basis = CashFlowBasis(label="normalised", base_fcff=usd(5000), origin="judgement",
                          provenance=PROVENANCE)
    out = value_on_basis("XYZ", AS_OF, basis=basis, engine=FakeEngine(rows()),
                         assumptions=assumptions)
    assert isinstance(out, AnalystValuation) and not isinstance(out, ValuationResult)
    assert out.kind == "fv_analyst"
    assert json.loads(out.to_json())["basis"]["provenance"] == PROVENANCE


@pytest.mark.parametrize("drop", ["method", "window", "computed_by", "stage_commit_hash"])
def test_ac_f10_13_incomplete_judgement_provenance_refuses(drop):
    from src.feature_engineer.valuation.types import CashFlowBasis

    with pytest.raises(ValueError, match=drop):
        CashFlowBasis(label="n", base_fcff=usd(1), origin="judgement",
                      provenance={k: v for k, v in PROVENANCE.items() if k != drop})


def test_ac_f10_13_valuation_never_returns_fv_analyst_and_render_refuses_it(assumptions):
    from src.feature_engineer.valuation.render import as_bundle_part
    from src.feature_engineer.valuation.service import valuation, value_on_basis
    from src.feature_engineer.valuation.types import CashFlowBasis, ValuationResult

    assert type(valuation("XYZ", AS_OF, engine=FakeEngine(rows()),
                          assumptions=assumptions)) is ValuationResult
    analyst = value_on_basis("XYZ", AS_OF, engine=FakeEngine(rows()), assumptions=assumptions,
                             basis=CashFlowBasis(label="n", base_fcff=usd(5000),
                                                 origin="judgement", provenance=PROVENANCE))
    with pytest.raises(TypeError, match="fv_model"):
        as_bundle_part(analyst)


def test_ac_f10_13_a_reported_basis_cannot_be_passed_off_through_value_on_basis(assumptions):
    """⚠ The judgement path must not become a second road to `fv_model`."""
    from src.feature_engineer.valuation.basis import reported_basis
    from src.feature_engineer.valuation.service import value_on_basis

    engine = FakeEngine(rows())
    with pytest.raises(ValueError, match="value_on_basis takes a judgement basis only"):
        value_on_basis("XYZ", AS_OF, engine=engine, assumptions=assumptions,
                       basis=reported_basis(rows(), as_of=AS_OF, ticker="XYZ"))
    assert engine.calls == [], "refused BEFORE fetching anything"


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.15 — staging
# ═══════════════════════════════════════════════════════════════════════════

def test_ac_f10_15_the_valuation_part_is_withheld_from_the_blind_view(assumptions):
    from src.feature_engineer.valuation.render import as_bundle_part
    from src.fundamental.bundle.models import BundlePart, EvidenceBundle

    spec = as_bundle_part(_value(FakeEngine(rows()), assumptions))
    part = BundlePart(**spec)
    filing = BundlePart("filing", {"accession_id": "acc"}, "Total revenue was $9,301 million.")
    full = EvidenceBundle(ticker="XYZ", as_of=AS_OF, parts=(filing, part))
    assert part in full.parts and part.kind == "computed"
    assert part.pins == {"contract_name": "valuation.dcf_two_stage", "contract_version": 1}
    assert "value_per_share" in part.content
    assert part not in full.redact().parts


def test_replace_is_imported_for_future_cases():
    """Keeps `replace` import meaningful for dataclass-override cases below."""
    from src.feature_engineer.valuation.types import CashFlowBasis
    b = CashFlowBasis(label="n", base_fcff=usd(1), origin="judgement", provenance=PROVENANCE)
    assert replace(b, label="m").label == "m"


# ═══════════════════════════════════════════════════════════════════════════
# DX-103 — real filers change concepts; the omissions follow the tag used
# ═══════════════════════════════════════════════════════════════════════════

def test_dx_103_a_filer_on_the_2023_taxonomy_is_valued_via_fallback_tags(assumptions):
    """⚠ Measured on MU: `InterestExpense` ends 2024, `LongTermDebt*` end 2013.
    The fallbacks resolve, the component records WHICH tag, and a lease-inclusive
    debt tag removes `finance_leases` from the declared omissions."""
    frame = rows()
    renames = {"InterestExpense_minor": "InterestExpenseNonoperating_minor",
               "InterestExpense_currency": "InterestExpenseNonoperating_currency",
               "LongTermDebtNoncurrent_minor": "LongTermDebtAndCapitalLeaseObligations_minor",
               "LongTermDebtNoncurrent_currency": "LongTermDebtAndCapitalLeaseObligations_currency",
               "LongTermDebtCurrent_minor": "DebtCurrent_minor",
               "LongTermDebtCurrent_currency": "DebtCurrent_currency"}
    res = _value(FakeEngine(frame.rename(columns=renames)), assumptions)
    obj = json.loads(res.to_json())
    tags = {c["item"]: c["tag"] for c in obj["net_debt"]["components"]}
    assert tags == {"cash": "CashAndCashEquivalentsAtCarryingValue",
                    "long_term_debt": "LongTermDebtAndCapitalLeaseObligations",
                    "current_debt": "DebtCurrent"}
    assert obj["net_debt"]["known_omissions"] == ["marketable_securities"]
    same = json.loads(_value(FakeEngine(rows()), assumptions).to_json())
    assert same["value_per_share"] == obj["value_per_share"], "same numbers, different tags"
    assert same["net_debt"]["known_omissions"] == [
        "marketable_securities", "finance_leases"]


def test_dx_103_CANONICAL_carries_the_fallbacks_AFTER_the_old_tags_and_the_contract_moved():
    """✏ `DX-103` (Victor, 2026-09-14): the fallbacks moved into `CANONICAL`, second in
    preference order, and the `fundamental` feature contract went to v3 (`FE-2`)."""
    from src.feature_engineer.contracts.sets.fundamental_v1 import FUNDAMENTAL_V1
    from src.feature_engineer.fundamental.items import CANONICAL

    assert CANONICAL["interest_expense"] == ("InterestExpense", "InterestExpenseNonoperating")
    assert CANONICAL["long_term_debt"] == ("LongTermDebtNoncurrent",
                                           "LongTermDebtAndCapitalLeaseObligations")
    assert CANONICAL["current_debt"] == ("LongTermDebtCurrent", "DebtCurrent")
    assert FUNDAMENTAL_V1.version >= 3      # ✏ v4 since F11 D4 (capex fallback), 2026-10-02


def _stock(**extra):
    """Rows whose latest quarter also carries `extra` balance items (major units)."""
    return rows({3: extra})


def test_ac_f10_20_net_debt_counts_securities_and_finance_leases(assumptions):
    """AC-F10.20 — debt 8,000 + 1,000 + leases 300 + 700 − cash 5,000 − securities
    600 + 1,400 ⇒ 3,000; each counted amount is a component with its tag."""
    from src.feature_engineer.valuation.basis import balance, known_omissions

    frame = _stock(marketable_securities_current=600, marketable_securities_noncurrent=1400,
                   finance_lease_current=300, finance_lease_noncurrent=700)
    net_debt, comps, _ = balance(frame, as_of=AS_OF, ticker="XYZ")
    assert net_debt == usd(3000)
    assert {c["item"]: c["tag"] for c in comps} == {
        "cash": TAGS["cash"], "long_term_debt": TAGS["long_term_debt"],
        "current_debt": TAGS["current_debt"],
        "marketable_securities_current": TAGS["marketable_securities_current"],
        "marketable_securities_noncurrent": TAGS["marketable_securities_noncurrent"],
        "finance_lease_current": TAGS["finance_lease_current"],
        "finance_lease_noncurrent": TAGS["finance_lease_noncurrent"]}
    assert known_omissions(comps) == ()
    out = json.loads(_value(FakeEngine(frame), assumptions).to_json())
    assert out["net_debt"]["value"] == usd(3000).to_json_obj()


def test_ac_f10_20_a_lease_inclusive_debt_tag_is_not_counted_twice():
    """⚠⚠ Measured on MU: `DebtCurrent` and `LongTermDebtAndCapitalLeaseObligations`
    already hold the finance leases. Per side: the inclusive side adds nothing, the
    other side adds its lease."""
    from src.feature_engineer.valuation.basis import balance, known_omissions

    frame = _stock(finance_lease_current=300, finance_lease_noncurrent=700).rename(columns={
        "LongTermDebtCurrent_minor": "DebtCurrent_minor",
        "LongTermDebtCurrent_currency": "DebtCurrent_currency"})
    net_debt, comps, _ = balance(frame, as_of=AS_OF, ticker="XYZ")
    assert net_debt == usd(8000 + 1000 + 700 - 5000)
    items = {c["item"] for c in comps}
    assert "finance_lease_current" not in items and "finance_lease_noncurrent" in items
    assert known_omissions(comps) == ("marketable_securities",)


@pytest.mark.parametrize(("extra", "omitted"), [
    ({}, ("marketable_securities", "finance_leases")),
    ({"marketable_securities_noncurrent": 50}, ("finance_leases",)),
    ({"finance_lease_current": 10}, ("marketable_securities", "finance_leases")),
])
def test_ac_f10_20_an_unreported_item_is_declared_never_zero(extra, omitted):
    """AC-F10.20 / `FE-14` — absent is named, not counted as 0; a lease on ONE
    non-inclusive side still leaves the other side's leases omitted."""
    from src.feature_engineer.valuation.basis import balance, known_omissions

    net_debt, comps, _ = balance(_stock(**extra), as_of=AS_OF, ticker="XYZ")
    assert known_omissions(comps) == omitted
    assert net_debt == usd(8000 + 1000 - 5000 - extra.get("marketable_securities_noncurrent", 0)
                           + extra.get("finance_lease_current", 0))


@pytest.mark.parametrize(("next_start", "ok"), [
    (date(2025, 5, 29), True),     # ★ gap 0 — how EDGAR-derived quarters abut (MU, measured)
    (date(2025, 5, 30), True),     # gap 1 — the "day after" convention
    (date(2025, 5, 20), False),    # overlap
    (date(2025, 6, 20), False),    # a hole of 22 days
])
def test_dx_103_quarters_that_start_ON_the_prior_end_are_contiguous(next_start, ok, assumptions):
    """⚠⚠ Found only on REAL data: Micron's derived quarters start on the prior
    quarter's end date, and a 1–7-day rule refused every trailing year."""
    from src.feature_engineer.errors import ValuationUnavailable
    from src.feature_engineer.valuation.basis import reported_basis

    frame = rows()
    frame.loc[3, "period_start"] = next_start
    if ok:
        reported_basis(frame, as_of=AS_OF, ticker="XYZ")
    else:
        with pytest.raises(ValuationUnavailable, match="contiguous|discrete"):
            reported_basis(frame, as_of=AS_OF, ticker="XYZ")


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.18 — one formula, any span (for D5's normaliser)
# ═══════════════════════════════════════════════════════════════════════════

def _annual(start, end, **items_major):
    row = _row(start, end, date(end.year, end.month, 28) if end.month < 12 else end, **items_major)
    row["period_type"] = "annual"
    return pd.Series(row)


def test_ac_f10_18_annual_basis_applies_D6_to_one_fiscal_year():
    """AC-F10.18 — OCF 12,000 · interest 400 · tax 1,000 / pretax 4,000 · capex 8,000 ·
    SBC 800 over one 364-day year ⇒ 3,500, the SAME figure as the trailing formula."""
    from src.feature_engineer.valuation.basis import annual_basis

    TAGS["revenue"] = "RevenueFromContractWithCustomerExcludingAssessedTax"
    row = _annual(date(2023, 9, 1), date(2024, 8, 29), operating_cash_flow=12000,
                  interest_expense=400, income_tax=1000, pretax_income=4000, capex=8000,
                  sbc=800, revenue=25000)
    year = annual_basis(row, ticker="XYZ", as_of=AS_OF)
    assert year.fcff == usd(3500) and year.revenue == usd(25000)
    assert year.tax_rate == Decimal("0.25") and year.fiscal_year_end == date(2024, 8, 29)


@pytest.mark.parametrize("days", [91, 272, 400])
def test_ac_f10_18_a_non_annual_span_refuses(days):
    from datetime import timedelta

    from src.feature_engineer.errors import ValuationUnavailable
    from src.feature_engineer.valuation.basis import annual_basis

    end = date(2024, 8, 29)
    row = _annual(end - timedelta(days=days), end, operating_cash_flow=1, interest_expense=1,
                  income_tax=1, pretax_income=4, capex=1, sbc=1)
    with pytest.raises(ValuationUnavailable, match="annual"):
        annual_basis(row, ticker="XYZ", as_of=AS_OF)


def test_ac_f10_18_trailing_total_sums_the_same_four_quarters():
    from src.feature_engineer.valuation.basis import reported_basis, trailing_total

    basis = reported_basis(rows(), as_of=AS_OF, ticker="XYZ")
    assert trailing_total(rows(), "capex", as_of=AS_OF, ticker="XYZ") == usd(8000)
    used = {str(i["period_end"]) for i in basis.inputs if i["item"] == "capex"}
    assert used == {str(e) for _, e, _ in QUARTERS}


def test_ac_f10_20_operating_leases_are_excluded_by_design_not_omitted(assumptions):
    """AC-F10.20 ✏ `DX-106` (Victor, 2026-09-14, ⓐ): `D6`'s operating cash flow already
    pays operating leases, so net debt leaves them out ON PURPOSE — declared with its
    reason, never listed as a gap, and no operating-lease amount moves net debt."""
    frame = _stock(marketable_securities_current=600, finance_lease_current=300,
                   finance_lease_noncurrent=700)
    frame["OperatingLeaseLiabilityNoncurrent_minor"] = 999_999 * 100
    frame["OperatingLeaseLiabilityNoncurrent_currency"] = USD
    obj = json.loads(_value(FakeEngine(frame), assumptions).to_json())
    assert "operating_leases" not in obj["net_debt"]["known_omissions"]
    assert "twice" in obj["net_debt"]["excluded_by_design"]["operating_leases"]
    assert obj["net_debt"]["value"] == usd(8000 + 1000 + 300 + 700 - 5000 - 600).to_json_obj()


def test_ac_f10_21_the_result_declares_what_it_cannot_compute(assumptions):
    """AC-F10.21 / `D9` (`DX-116`) — ★ the analysis found two capex questions; one is a real
    UNCOMPUTABLE limit and is declared, the other was already coherent and must NOT be listed.

    ⚠ `J-11` argued lease-funded equipment flatters FCFF. `D8` counts finance leases as DEBT
    ($3,107M on MU), so charging the additions to capex too would count them twice — `J-14`
    reached the same conclusion. A "limit" that is not one trains the reader to skip the list.
    """
    from src.feature_engineer.valuation.basis import KNOWN_LIMITS

    obj = json.loads(_value(FakeEngine(rows()), assumptions).to_json())
    assert obj["known_limits"] == list(KNOWN_LIMITS)
    (incentives,) = [limit for limit in obj["known_limits"] if "incentive" in limit]
    assert "no EDGAR fact carries them" in incentives and "DX-116" in incentives
    assert not any("lease" in limit for limit in obj["known_limits"]), (
        "finance leases are counted in net debt (D8); listing them as a limit would be false")


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.22 — the price requirement by duration, and market capitalisation (D10)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def assumptions_v2():
    from src.feature_engineer.valuation.assumptions import load_published
    return load_published("dcf_two_stage", 2)


def test_ac_f10_22_v2_is_v1_plus_the_duration_table_only(assumptions, assumptions_v2):
    """AC-F10.22 / D10 — the adopted periods, and nothing else moved."""
    assert assumptions_v2.duration_years == (5, 7, 10, 15)
    assert assumptions.duration_years == ()
    same = ("discount_rate", "explicit_years", "stage1_growth", "terminal_growth",
            "band_discount", "band_terminal", "implied_low", "implied_high", "implied_iterations")
    assert all(getattr(assumptions, f) == getattr(assumptions_v2, f) for f in same)


def test_ac_f10_22_one_row_per_period_and_the_own_period_equals_implied(assumptions_v2):
    """AC-F10.22 — each row is D7's solve with only explicit_years replaced."""
    from src.feature_engineer.valuation.dcf import value_per_share_at

    res = _value(FakeEngine(rows()), assumptions_v2)
    obj = json.loads(res.to_json())
    table = obj["implied_by_duration"]
    assert [r["explicit_years"] for r in table] == [5, 7, 10, 15]
    own = next(r for r in table if r["explicit_years"] == assumptions_v2.explicit_years)
    assert {k: own[k] for k in obj["implied"]} == obj["implied"]
    m = Money.from_json_obj
    a = assumptions_v2
    solved = [r for r in table if r["status"] == "SOLVED"]
    assert solved, "the fixture price must be reachable at some period"
    for r in table:
        if r["status"] == "NO_ROOT_IN_BRACKET":
            assert r["value"] is None and r["residual"] is None
            continue
        vps = value_per_share_at(m(obj["basis"]["base_fcff"]), m(obj["net_debt"]["value"]),
                                 obj["diluted_shares"], discount_rate=a.discount_rate,
                                 stage1_growth=Decimal(r["value"]),
                                 terminal_growth=a.terminal_growth,
                                 explicit_years=r["explicit_years"])
        assert abs((vps - m(obj["price"]["value"])).amount_minor) <= 1
    # ★ a shorter period needs growth FURTHER from terminal growth, in whichever direction
    #   the price points (here below the terminal-growth value, so the rates are negative)
    gaps = [abs(Decimal(r["value"]) - a.terminal_growth) for r in solved]
    assert gaps == sorted(gaps, reverse=True)


def test_ac_f10_22_a_price_above_value_needs_more_growth_the_shorter_the_period(assumptions_v2):
    """AC-F10.22 — the MU shape: price far above fv_model ⇒ positive, falling with N."""
    res = _value(FakeEngine(rows(), price_minor=40_000), assumptions_v2)
    table = json.loads(res.to_json())["implied_by_duration"]
    growths = [Decimal(r["value"]) for r in table if r["status"] == "SOLVED"]
    assert len(growths) >= 2 and all(g > assumptions_v2.terminal_growth for g in growths)
    assert growths == sorted(growths, reverse=True)


def test_ac_f10_22_market_cap_is_raw_price_times_diluted_shares(assumptions_v2, assumptions):
    for a in (assumptions, assumptions_v2):
        obj = json.loads(_value(FakeEngine(rows()), a).to_json())
        price = Money.from_json_obj(obj["price"]["value"])
        assert obj["market_capitalisation"] == Money(
            price.amount_minor * obj["diluted_shares"], price.currency).to_json_obj()


def test_ac_f10_22_a_set_with_no_table_carries_no_duration_key(assumptions):
    assert "implied_by_duration" not in json.loads(_value(FakeEngine(rows()), assumptions).to_json())


def test_ac_f10_22_a_v2_trail_recomputes_every_row_from_its_own_fields(assumptions_v2):
    """AC-F10.22 + AC-F10.4 — the table is part of the complete trail."""
    from dataclasses import replace as dc_replace

    from src.feature_engineer.valuation.implied import solve_implied

    obj = json.loads(_value(FakeEngine(rows()), assumptions_v2).to_json())
    m = Money.from_json_obj
    for r in obj["implied_by_duration"]:
        again = solve_implied(price=m(obj["price"]["value"]),
                              base_fcff=m(obj["basis"]["base_fcff"]),
                              net_debt=m(obj["net_debt"]["value"]),
                              diluted_shares=obj["diluted_shares"],
                              assumptions=dc_replace(assumptions_v2,
                                                     explicit_years=r["explicit_years"]))
        solve = {"explicit_years": r["explicit_years"], **again.to_json_obj()}
        assert {k: r[k] for k in solve} == solve        # the D11 fields: AC-F10.23's test


@pytest.mark.parametrize("bad", [[5, 5, 10], [0, 10], []])
def test_ac_f10_22_a_malformed_duration_table_refuses_at_load(tmp_path, bad):
    import yaml

    from src.feature_engineer.errors import NoFiniteValueError
    from src.feature_engineer.valuation.assumptions import CONFIG_DIR, content_hash, load

    doc = yaml.safe_load((CONFIG_DIR / "dcf_two_stage_v2.yaml").read_text())
    doc["duration_table"]["explicit_years"] = bad
    doc["content_hash"] = content_hash(doc)
    path = tmp_path / "x.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(NoFiniteValueError):
        load(path)


def test_ac_f10_22_the_duration_table_is_hashed(tmp_path):
    import yaml

    from src.feature_engineer.errors import AssumptionsMutatedError
    from src.feature_engineer.valuation.assumptions import CONFIG_DIR, load

    doc = yaml.safe_load((CONFIG_DIR / "dcf_two_stage_v2.yaml").read_text())
    doc["duration_table"]["explicit_years"] = [5, 10]
    path = tmp_path / "dcf_two_stage_v2.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(AssumptionsMutatedError):
        load(path)


# ═══════════════════════════════════════════════════════════════════════════
# AC-F10.23 — the required cash flow, in revenue terms (D11)
# ═══════════════════════════════════════════════════════════════════════════

def test_ac_f10_23_each_solved_row_states_its_final_year_fcff_and_its_share_of_revenue(
        assumptions_v2):
    """AC-F10.23 — the year-N flow of the SAME `discount` trail, ÷ trailing revenue."""
    from src.feature_engineer.valuation.dcf import discount

    obj = json.loads(_value(FakeEngine(rows(), price_minor=40_000), assumptions_v2).to_json())
    m = Money.from_json_obj
    revenue = m(obj["trailing_revenue"]["value"])
    assert revenue == usd(40_000)                              # four quarters × 10,000
    solved = [r for r in obj["implied_by_duration"] if r["status"] == "SOLVED"]
    assert solved
    for r in solved:
        trail = discount(m(obj["basis"]["base_fcff"]), discount_rate=assumptions_v2.discount_rate,
                         stage1_growth=Decimal(r["value"]),
                         terminal_growth=assumptions_v2.terminal_growth,
                         explicit_years=r["explicit_years"])
        final = trail.flows[-1].fcff
        assert m(r["required_final_year_fcff"]) == final
        with localcontext() as ctx:
            ctx.prec = 40
            expected = (Decimal(final.amount_minor) / Decimal(revenue.amount_minor)
                        ).quantize(Decimal("1e-6"))
        assert Decimal(r["share_of_trailing_revenue"]) == expected


def test_ac_f10_23_a_no_root_row_has_both_fields_null(assumptions_v2):
    obj = json.loads(_value(FakeEngine(rows(), price_minor=4_000_000), assumptions_v2).to_json())
    no_root = [r for r in obj["implied_by_duration"] if r["status"] == "NO_ROOT_IN_BRACKET"]
    assert no_root
    assert all(r["required_final_year_fcff"] is None and r["share_of_trailing_revenue"] is None
               for r in no_root)


def test_ac_f10_23_absent_revenue_refuses_naming_it(assumptions_v2):
    from src.feature_engineer.errors import ValuationUnavailable

    gap = rows()
    gap[f"{TAGS['revenue']}_minor"] = gap[f"{TAGS['revenue']}_minor"].astype("Int64")
    gap.loc[1, f"{TAGS['revenue']}_minor"] = pd.NA              # one trailing quarter missing
    with pytest.raises(ValuationUnavailable) as exc:
        _value(FakeEngine(gap), assumptions_v2)
    assert "revenue" in exc.value.missing


def test_ac_f10_23_a_v1_result_carries_neither_field(assumptions):
    obj = json.loads(_value(FakeEngine(rows()), assumptions).to_json())
    assert "trailing_revenue" not in obj and "implied_by_duration" not in obj
