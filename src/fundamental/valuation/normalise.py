"""`J-20`'s choice → a `CashFlowBasis(origin="judgement")` (`F10` `D5`).

★★ **The model CHOSE; D-02 CALCULATES.** `J-20` returns a method from a closed set
and a window of fiscal years. This module only VALIDATES that choice and records
its provenance; every figure comes from D-02 (`valuation/normalised.py`,
`AC-F10.19`). ⚠ It holds no series arithmetic and imports no pandas: `RA-45` —
*"D-01 performs no arithmetic that D-02 could perform"* — refused the first build,
which averaged here (`DX-105`).

⚠ Exclusions are RECORDED in the provenance and NOT applied (`J-20` `v1`): the
basis is cash flow, a non-cash write-down barely moves it, and quantifying one
would put a figure in the model's hands.
"""

from __future__ import annotations

from datetime import date

from src.feature_engineer.errors import ValuationUnavailable
from src.feature_engineer.valuation.basis import reported_basis
from src.feature_engineer.valuation.normalised import (
    FORMULA_ID,
    cycle_average_fcff,
    cycle_average_fcff_margin,
)
from src.feature_engineer.valuation.types import CashFlowBasis

#: `J-20`'s window rule — asserted equal to the prompt's own words by a structural test.
MIN_WINDOW_YEARS = 3
COMPUTED_BY = f"src.feature_engineer.valuation.normalised:{FORMULA_ID}"
BLOCK = "J-20"
METHODS = ("reported_ttm", "cycle_average_fcff", "cycle_average_fcff_margin",
           "insufficient_evidence")


class NoNormalisedBasis(Exception):
    """The judgement produced no usable basis — `insufficient_evidence`, or a
    choice the history cannot support. ⚠ Never a default basis (`P5`)."""


def assert_exclusions_quoted(choice: dict, bundle) -> None:
    """`L3` `DX-108`(1) — every exclusion's quote must be IN the bundle the block read.

    ★ `X-01`'s comparison rule, applied to a quote with no offsets: whitespace and
    typography are transport artifacts, nothing else is normalised. ⚠ Found on the
    first live `J-20` (2026-09-14): three quotes were verbatim, but only a HAND check
    said so — and an exclusion travels into the frozen Stage-A commit as evidence.
    """
    from src.fundamental.claims.verify import _collapse_whitespace, _normalise_typography

    def norm(text: str) -> str:
        return _collapse_whitespace(_normalise_typography(text))

    corpus = norm("\n".join(p.content for p in bundle.parts))
    for n, exclusion in enumerate(choice.get("exclusions") or (), start=1):
        quote = norm(str(exclusion.get("quote", "")))
        if not quote or quote not in corpus:
            raise NoNormalisedBasis(
                f"exclusion {n} ({str(exclusion.get('item', ''))[:60]!r}) quotes text that is "
                f"not in the bundle: {quote[:80]!r} — an unverifiable quote is not evidence "
                f"(X-01, S-3)")


def normalise(choice: dict, *, quarterly_rows, annual_rows, ticker: str, as_of: date,
              provenance: dict, bundle) -> CashFlowBasis:
    """Validate `J-20`'s choice and have D-02 compute it.

    ★ `bundle` is REQUIRED: the exclusions' quotes are verified against it before any
    basis exists (`assert_exclusions_quoted`).
    """
    method = choice.get("method")
    if method not in METHODS:
        raise NoNormalisedBasis(f"method {method!r} is not one of {METHODS} (MP-5)")
    if method == "insufficient_evidence":
        raise NoNormalisedBasis("J-20 answered insufficient_evidence — no normalised basis")
    assert_exclusions_quoted(choice, bundle)

    prov = {**provenance, "block": BLOCK, "method": method, "computed_by": COMPUTED_BY,
            "exclusions": [dict(e) for e in (choice.get("exclusions") or [])],
            "exclusions_applied": False,
            "trough_year": choice.get("trough_year"), "peak_year": choice.get("peak_year")}

    if method == "reported_ttm":
        prov["window"] = {"start": "trailing_four_quarters", "end": as_of.isoformat()}
        return CashFlowBasis(label="normalised.reported_ttm",
                             base_fcff=reported_basis(quarterly_rows, as_of=as_of,
                                                      ticker=ticker).base_fcff,
                             origin="judgement", provenance=prov)

    first, last = choice.get("first_fiscal_year"), choice.get("last_fiscal_year")
    if not isinstance(first, int) or not isinstance(last, int) or first > last:
        raise NoNormalisedBasis(f"window {first!r}–{last!r} is not a range of fiscal years")
    if last - first + 1 < MIN_WINDOW_YEARS:
        raise NoNormalisedBasis(f"window FY{first}–FY{last} spans {last - first + 1} years; "
                                f"J-20 requires at least {MIN_WINDOW_YEARS}")
    for label in ("trough_year", "peak_year"):
        year = choice.get(label)
        if not isinstance(year, int) or not first <= year <= last:
            raise NoNormalisedBasis(f"{label} {year!r} is not inside FY{first}–FY{last}")

    try:
        if method == "cycle_average_fcff":
            base, years = cycle_average_fcff(annual_rows, first, last, ticker=ticker, as_of=as_of)
        else:
            base, years, mean, revenue = cycle_average_fcff_margin(
                annual_rows, quarterly_rows, first, last, ticker=ticker, as_of=as_of)
            prov["mean_margin"] = str(mean)
            prov["trailing_revenue"] = revenue.to_json_obj()
    except ValuationUnavailable as exc:
        raise NoNormalisedBasis(exc.reason) from exc
    prov["window"] = {"start": f"FY{first}", "end": f"FY{last}",
                      "fiscal_year_ends": [y.fiscal_year_end.isoformat() for y in years]}
    return CashFlowBasis(label=f"normalised.{method}", base_fcff=base, origin="judgement",
                         provenance=prov)
