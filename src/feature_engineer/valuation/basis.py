"""The reported basis — `D6`'s formula over four discrete EDGAR quarters (`AC-F10.7`, `.17`).

`base_fcff = OCF + interest × (1 − t) − capex − SBC`, `t = income_tax ÷ pretax_income`,
and `t = 0` when pretax income ≤ 0 (`DX-104`).

★ **Why each term (`D6`).** US GAAP operating cash flow is AFTER interest paid,
so after-tax interest is added back to make the flow pre-financing — matching
`D2`'s firm discount rate; without it, debt is counted twice (once in the flow,
once as net debt), which is `D-19`'s mistake in miniature. Stock-based
compensation is added back inside OCF as "non-cash", and subtracted here because
owners bear it through dilution.

⚠⚠ **Trailing means four DISCRETE, CONTIGUOUS quarters** (`fmp-api` trap 1: FMP
guessed Micron's quarter wrong by 71 %). D-07 classifies spans at ingest and
differences cumulative year-to-date facts into quarters; this module re-checks
the span and the contiguity rather than trusting a label, and refuses an FMP
quarter where EDGAR quarters exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pandas as pd

from src.feature_engineer.errors import ValuationUnavailable
from src.feature_engineer.fundamental.items import CANONICAL
from src.feature_engineer.valuation.types import CashFlowBasis
from src.shared.money import Money

#: ✏ `v2` (2026-09-14, `DX-104`): a loss year takes `t = 0` instead of refusing.
FORMULA_ID = "fcff.ocf_plus_after_tax_interest_minus_capex_minus_sbc.v2"

#: Flow items summed over the trailing four quarters, in `D6`'s order.
FLOW_ITEMS = ("operating_cash_flow", "interest_expense", "income_tax", "pretax_income",
              "capex", "sbc")
#: Balance items read from the latest quarter.
DEBT_ITEMS = ("long_term_debt", "current_debt")
CASH_ITEMS = ("cash",)
SHARES_ITEM = "diluted_shares"

#: A discrete quarter's span — the same window D-07 classifies by. ★ Filers on
#: 52/53-week calendars run 13–14 weeks, so 80–100 days, never a label.
_QUARTER_DAYS = (80, 100)
#: Consecutive quarters abut. ⚠⚠ **Measured on Micron's EDGAR facts, 2026-09-13:**
#: the next quarter starts ON the previous one's end date (gap 0) — the span D-07's
#: `derive_quarters` gives a quarter differenced from year-to-date facts. A first
#: version demanded 1–7 days (the textbook "day after") and refused real,
#: contiguous data; synthetic tests could not have shown it. A negative gap is an
#: overlap and still refuses; more than 7 days is a missing quarter.
_CONTIGUITY_DAYS = (0, 7)


def _day(value) -> date:
    return value if isinstance(value, date) and not isinstance(value, pd.Timestamp) \
        else pd.Timestamp(value).date()


#: ★ `D8` (2026-09-14, was `Q2`) — net-debt items that are NOT canonical line items.
#: Preference order per side; the first tag present wins, as in `CANONICAL`.
#: ⚠ Not in `CANONICAL`: no feature reads them, and a canonical item is a column in
#: every fundamentals frame (`FE-2`). ✗ `LongTermInvestments` is deliberately absent —
#: it includes equity-method stakes, which are not cash-like.
NET_DEBT_TAGS: dict[str, tuple[str, ...]] = {
    "marketable_securities_current": (
        "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
        "AvailableForSaleSecuritiesCurrent", "ShortTermInvestments"),
    "marketable_securities_noncurrent": (
        "MarketableSecuritiesNoncurrent", "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent",
        "AvailableForSaleSecuritiesNoncurrent"),
    "finance_lease_current": ("FinanceLeaseLiabilityCurrent",),
    "finance_lease_noncurrent": ("FinanceLeaseLiabilityNoncurrent",),
}
SECURITIES_ITEMS = ("marketable_securities_current", "marketable_securities_noncurrent")
#: debt item → the finance-lease item for the same side of the balance sheet.
LEASE_SIDE = {"current_debt": "finance_lease_current", "long_term_debt": "finance_lease_noncurrent"}

#: Debt tags whose amount ALREADY includes finance-lease obligations, so that side's
#: finance lease is not added again. ⚠⚠ **Measured on Micron, 2026-09-14:**
#: `DebtCurrent` = `FinanceLeaseLiabilityCurrent` exactly (538 = 538 at 2025-05-29; 582 = 582
#: at 2026-05-28) and ≥ it in every period since 2019; `LongTermDebtAndCapitalLeaseObligations`
#: 15,003 = `LongTermDebt` 12,434 + `FinanceLeaseLiabilityNoncurrent` 2,569. Adding the
#: lease tags on top would have counted ~$3.1B twice.
LEASE_INCLUSIVE_TAGS = frozenset({"LongTermDebtAndCapitalLeaseObligations", "DebtCurrent"})


def _tags(item: str) -> tuple[str, ...]:
    return CANONICAL[item] if item in CANONICAL else NET_DEBT_TAGS[item]


def _found(row, item: str):
    """`(tag, raw value)` for the first preference-ordered tag present, or None."""
    for tag in _tags(item):
        col = f"{tag}_minor"
        if col in row.index and not pd.isna(row[col]):
            return tag, row[col]
    return None


def _money(row, item: str) -> Money | None:
    """The first preference-ordered tag present for `item` (`CANONICAL`, `FE-25`)."""
    hit = _found(row, item)
    return None if hit is None else Money(int(hit[1]), str(row[f"{hit[0]}_currency"]))


def _count(row, item: str) -> int | None:
    hit = _found(row, item)
    return None if hit is None else int(hit[1])


def trailing_quarters(rows: pd.DataFrame, *, as_of: date, ticker: str) -> pd.DataFrame:
    """The latest four discrete, contiguous quarters knowable at `as_of`."""
    if rows is None or not len(rows):
        raise ValuationUnavailable(ticker, as_of, ["fundamentals"], "no filings at as_of")
    q = rows.copy()
    q["q_start"] = q["period_start"].map(_day)
    q["q_end"] = q["period_end"].map(_day)
    q["q_filed"] = q["filing_date"].map(_day)
    q = q[(q["q_filed"] <= as_of) & (q["q_end"] <= as_of)]
    if "period_type" in q.columns:
        q = q[q["period_type"] == "quarterly"]
    q = q.sort_values("q_end", kind="mergesort").tail(4).reset_index(drop=True)
    if len(q) < 4:
        raise ValuationUnavailable(ticker, as_of, ["four_quarters"],
                                   f"only {len(q)} quarterly filing(s) knowable")
    spans = [(r.q_end - r.q_start).days for r in q.itertuples()]
    if not all(_QUARTER_DAYS[0] <= d <= _QUARTER_DAYS[1] for d in spans):
        raise ValuationUnavailable(
            ticker, as_of, ["four_quarters"],
            f"spans {spans} days are not all discrete quarters — a cumulative year-to-date "
            f"value must never enter as a quarter (fmp-api trap 1)")
    for prev, nxt in zip(q.itertuples(), q.iloc[1:].itertuples(), strict=False):
        gap = (nxt.q_start - prev.q_end).days
        if not _CONTIGUITY_DAYS[0] <= gap <= _CONTIGUITY_DAYS[1]:
            raise ValuationUnavailable(
                ticker, as_of, ["four_quarters"],
                f"quarters ending {prev.q_end} and {nxt.q_end} are not contiguous "
                f"(gap {gap} days) — four quarters with a hole are not a trailing year")
    sources = set(q["source"])
    if len(sources) > 1:
        raise ValuationUnavailable(
            ticker, as_of, ["four_quarters"],
            f"trailing quarters mix sources {sorted(sources)}; EDGAR quarters exist, so an FMP "
            f"quarter is refused — EDGAR knows the quarter, FMP guesses it (fmp-api trap 1)")
    return q


def _input(row, item: str, value) -> dict:
    hit = _found(row, item)
    return {"item": item, "tag": None if hit is None else hit[0], "value": value,
            "source": row["source"],
            "accession_id": None if pd.isna(row.get("accession_id")) else row["accession_id"],
            "period_start": row["q_start"], "period_end": row["q_end"],
            "filing_date": row["q_filed"]}


@dataclass(frozen=True, slots=True)
class AnnualBasis:
    """`AC-F10.18` — `D6` applied to one fiscal year, for `D5`'s normaliser."""

    fiscal_year_end: date
    fcff: Money
    revenue: Money
    tax_rate: Decimal
    inputs: tuple
    tax_rule: str = "effective"


#: `DX-104` — how `t` was set, recorded on the basis.
TAX_EFFECTIVE, TAX_LOSS_YEAR_ZERO = "effective", "loss_year_zero"


def _d6(totals: dict, *, ticker: str, as_of: date) -> tuple[Money, Decimal, str]:
    """★ THE `D6` formula — the one place it is written (`FE-25`).

    `OCF + interest × (1 − t) − capex − SBC`, `t = income_tax ÷ pretax_income`.

    ✏ **`DX-104` (Victor, 2026-09-14): pretax income ≤ 0 ⇒ `t = 0`.** A loss year
    pays no tax, so interest shields nothing. The first version refused, and that
    made every cycle window through a trough impossible — Micron's FY2016 and
    FY2023. ⚠ Still NOT a statutory substitute: a POSITIVE pretax income with a
    rate outside `[0, 1]` refuses, because there the filing's own rate is garbled.
    """
    pretax, tax = totals["pretax_income"], totals["income_tax"]
    if pretax.amount_minor <= 0:
        rate, rule = Decimal(0), TAX_LOSS_YEAR_ZERO
    else:
        rate, rule = Decimal(tax.amount_minor) / Decimal(pretax.amount_minor), TAX_EFFECTIVE
    if not Decimal(0) <= rate <= Decimal(1):
        raise ValuationUnavailable(ticker, as_of, ["tax_rate"],
                                   f"effective tax rate {rate} is outside [0, 1]")
    base = (totals["operating_cash_flow"]
            + totals["interest_expense"].mul_rate(Decimal(1) - rate)
            - totals["capex"]
            - totals["sbc"])
    return base, rate, rule


def reported_basis(rows: pd.DataFrame, *, as_of: date, ticker: str) -> CashFlowBasis:
    """`AC-F10.17` — `D6`'s judgement-free basis for `fv_model`."""
    q = trailing_quarters(rows, as_of=as_of, ticker=ticker)
    totals: dict[str, Money] = {}
    inputs, missing = [], []
    for item in FLOW_ITEMS:
        values = [_money(r, item) for _, r in q.iterrows()]
        if any(v is None for v in values):
            missing.append(item)
            continue
        total = values[0]
        for v in values[1:]:
            total = total + v
        totals[item] = total
        inputs.extend(_input(r, item, v) for (_, r), v in zip(q.iterrows(), values, strict=True))
    if missing:
        raise ValuationUnavailable(ticker, as_of, missing,
                                   "a trailing flow item is absent in one or more quarters")
    base, rate, rule = _d6(totals, ticker=ticker, as_of=as_of)
    return CashFlowBasis(label="reported_ttm_fcff", base_fcff=base, origin="reported",
                         formula_id=FORMULA_ID, tax_rate=rate, tax_rule=rule,
                         tax_inputs={"income_tax": totals["income_tax"],
                                     "pretax_income": totals["pretax_income"]},
                         inputs=tuple(inputs))


def trailing_total(rows: pd.DataFrame, item: str, *, as_of: date, ticker: str) -> Money:
    """`AC-F10.18` — one canonical item over the SAME four trailing quarters."""
    q = trailing_quarters(rows, as_of=as_of, ticker=ticker)
    values = [_money(r, item) for _, r in q.iterrows()]
    if any(v is None for v in values):
        raise ValuationUnavailable(ticker, as_of, [item], "absent in a trailing quarter")
    total = values[0]
    for v in values[1:]:
        total = total + v
    return total


#: A fiscal year's span. ★ 52/53-week filers run 364 or 371 days.
_ANNUAL_DAYS = (350, 380)


def annual_basis(row, *, ticker: str, as_of: date) -> AnnualBasis:
    """`AC-F10.18` — `D6` on ONE annual row; a non-annual span refuses."""
    start, end = _day(row["period_start"]), _day(row["period_end"])
    days = (end - start).days
    if not _ANNUAL_DAYS[0] <= days <= _ANNUAL_DAYS[1]:
        raise ValuationUnavailable(ticker, as_of, ["annual_span"],
                                   f"a {days}-day span is not an annual period")
    frame = row.copy()
    frame["q_start"], frame["q_end"], frame["q_filed"] = start, end, _day(row["filing_date"])
    totals, missing = {}, []
    for item in FLOW_ITEMS + ("revenue",):
        value = _money(frame, item)
        if value is None:
            missing.append(item)
        totals[item] = value
    if missing:
        raise ValuationUnavailable(ticker, as_of, missing,
                                   f"absent for the fiscal year ending {end}")
    base, rate, rule = _d6(totals, ticker=ticker, as_of=as_of)
    inputs = tuple(_input(frame, item, totals[item]) for item in FLOW_ITEMS + ("revenue",))
    return AnnualBasis(fiscal_year_end=end, fcff=base, revenue=totals["revenue"],
                       tax_rate=rate, inputs=inputs, tax_rule=rule)


def _with_year_end_balance(rows: pd.DataFrame, latest, *, as_of: date, facts=None):
    """`D12` (`DX-176`) — a Q4 derived from a 10-K, with the 10-K's year-end balance sheet.

    ⚠ A 10-K reports no fourth quarter: D-07 differences Q4's FLOWS from the year, and an
    instant item has nothing to difference, so it sits only on the ANNUAL row. ★ Filled
    only from the annual row of the SAME period end AND the SAME accession — the same
    balance sheet, on the same date, in the same filing; never another filing's figure.
    """
    # ✏ `DX-177` — the diluted count too: a 10-K tags it for the YEAR only, and DE-84 no
    #   longer derives a Q4 average by subtraction. The year's weighted average is used.
    balance_items = (CASH_ITEMS + DEBT_ITEMS + SECURITIES_ITEMS + tuple(LEASE_SIDE.values())
                     + (SHARES_ITEM,))
    if "period_type" not in rows.columns or all(
            _found(latest, item) is not None for item in CASH_ITEMS + DEBT_ITEMS + (SHARES_ITEM,)):
        return latest
    dated = rows[(rows["period_type"] == "annual")
                 & (rows["period_end"].map(_day) == latest["q_end"])
                 & (rows["filing_date"].map(_day) <= as_of)]
    same = dated[dated["accession_id"] == latest.get("accession_id")]
    own = None                                    # None: the whole row is the filing's own
    if not len(same):
        # ✏ `DX-189` (`AC-F10.25`) — D-07 labels a row with the newest filing that tagged ANY
        #   fact for the date, so a proxy's one `NetIncomeLoss` relabelled SNDK's year-end
        #   row. ★ Judged per FACT: a tag counts only if its newest knowable fact is THIS
        #   filing's; an amendment that re-tagged it is still another filing's figure.
        if not len(dated) or facts is None:
            return latest
        same, own = dated, _own_tags(facts(), latest)
    annual, merged = same.iloc[-1], latest.copy()
    for item in balance_items:
        hit = _found(annual, item)
        if hit is not None and own is not None and hit[0] not in own:
            continue
        if _found(merged, item) is None and hit is not None:
            merged[f"{hit[0]}_minor"] = hit[1]
            merged[f"{hit[0]}_currency"] = annual[f"{hit[0]}_currency"]
    return merged


def _own_tags(facts: pd.DataFrame, latest) -> set[str]:
    """The annual tags at the latest quarter's end whose NEWEST knowable fact is its filing."""
    at = facts[(facts["period_type"] == "annual")
               & (facts["period_end"].map(_day) == latest["q_end"])]
    return set(at.loc[at["accession_id"] == latest.get("accession_id"), "tag"])


def balance(rows: pd.DataFrame, *, as_of: date, ticker: str, facts=None):
    """Net debt and diluted shares from the latest trailing quarter (`CT-F10.2`, `D8`).

    `net debt = debt + finance leases not inside a debt tag − cash − marketable securities`.
    ★ Securities and finance leases are counted WHEN REPORTED; an unreported one is
    named by `known_omissions`, never counted as zero (`AC-F10.20`, `FE-14`).
    ★ Operating leases are not counted, by design (`D8`, `DX-106`): `D6`'s operating
    cash flow already pays them, so the liability would count them twice.
    """
    q = trailing_quarters(rows, as_of=as_of, ticker=ticker)
    latest = _with_year_end_balance(rows, q.iloc[-1], as_of=as_of, facts=facts)
    missing, parts = [], {}
    for item in CASH_ITEMS + DEBT_ITEMS:
        value = _money(latest, item)
        if value is None:
            missing.append(item)
        parts[item] = value
    shares = _count(latest, SHARES_ITEM)
    if shares is None:
        missing.append(SHARES_ITEM)
    if missing:
        raise ValuationUnavailable(ticker, as_of, missing,
                                   "a balance item is absent in the latest quarter")
    net_debt = parts["long_term_debt"] + parts["current_debt"] - parts["cash"]
    counted = list(CASH_ITEMS + DEBT_ITEMS)
    for item in SECURITIES_ITEMS:
        value = _money(latest, item)
        if value is not None:
            net_debt, parts[item] = net_debt - value, value
            counted.append(item)
    for debt_item, lease_item in LEASE_SIDE.items():
        if _found(latest, debt_item)[0] in LEASE_INCLUSIVE_TAGS:
            continue                               # ★ already inside the debt figure
        value = _money(latest, lease_item)
        if value is not None:
            net_debt, parts[lease_item] = net_debt + value, value
            counted.append(lease_item)
    components = tuple(_input(latest, item, parts[item]) for item in counted)
    return net_debt, components, shares


#: ★ `D9` / `AC-F10.21` (`DX-116`) — figures `D6` CANNOT compute from D-07's facts, declared on
#: every result (`PG-10`). ⚠ A limit belongs here only when it is REAL and UNCOMPUTABLE:
#: ✗ lease-funded equipment is NOT here — `D8` already counts finance leases as debt, so charging
#:   the additions to capex too would count the same equipment twice (measured on MU: $3,107M of
#:   finance leases in net debt against $1,394M of trailing ROU additions).
#: ⚠ Government-incentive proceeds ARE here: no tagged fact exists anywhere in `companyfacts`
#:   (`GovernmentAssistance*` carries balances, not the cash line), so a trailing figure cannot be
#:   computed at all. Measured on MU: $1,294M over 9M FY2025 against a $1,349M trailing base —
#:   material enough that valuing silently would misstate the flow.
KNOWN_LIMITS: tuple[str, ...] = (
    "capex is charged GROSS: government-incentive proceeds are not credited against it, because no "
    "EDGAR fact carries them (the figure appears only in filing prose) — D6 cannot compute it "
    "(F10 D9, DX-116)",
)


def known_omissions(components) -> tuple[str, ...]:
    """`CT-F10.2` — what net debt does NOT count, derived from the components USED.

    ★ Never a fixed list: declaring an item omitted when it was counted would be a
    false statement on the result, and so would the reverse.
    """
    by_item = {c.get("item"): c.get("tag") for c in components}
    omitted = []
    if not any(item in by_item for item in SECURITIES_ITEMS):
        omitted.append("marketable_securities")
    if any(by_item.get(debt) not in LEASE_INCLUSIVE_TAGS and lease not in by_item
           for debt, lease in LEASE_SIDE.items()):
        omitted.append("finance_leases")
    return tuple(omitted)


#: `CT-F10.2` — what net debt leaves out ON PURPOSE, with the reason (`D8`, `DX-106`).
#: ★ Kept apart from `known_omissions`: a choice and a gap are different facts, and
#: one list for both would let a reader mistake either for the other (`PG-10`).
EXCLUDED_BY_DESIGN = {
    "operating_leases": ("paid inside operating cash flow, which the D6 cash-flow basis already "
                         "subtracts — counting the liability too would count the lease twice"),
}
