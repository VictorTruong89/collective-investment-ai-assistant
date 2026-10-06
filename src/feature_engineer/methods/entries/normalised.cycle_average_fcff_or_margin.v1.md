# `normalised.cycle_average_fcff_or_margin.v1` — cycle averages over a judgement's window

Code: src/feature_engineer/valuation/normalised.py @ sha256:9add9cba0f976e5d
*(QA-25 / F12 AC-F12.22 — pinned 2026-10-05 as the baseline; re-pin only after re-reading this entry against the changed code.)*

## Statement

Given a window of fiscal years `W = {first … last}` chosen by `J-20` (`F10` `D5`):

    cycle_average_fcff        = Σ_{y∈W} FCFF_y ÷ |W|
    cycle_average_fcff_margin = ( Σ_{y∈W} FCFF_y ÷ revenue_y ÷ |W| ) × revenue_ttm

`FCFF_y` is `fcff.ocf_plus_after_tax_interest_minus_capex_minus_sbc.v2` applied to one
fiscal year; `revenue_ttm` is the same four trailing quarters the reported basis uses.

## Symbols

| Symbol | Meaning |
|---|---|
| `W` | the window — at least three consecutive fiscal years, all present and computable |
| `FCFF_y`, `revenue_y` | fiscal-year free cash flow to the firm and revenue |
| `revenue_ttm` | trailing-twelve-month revenue |

## Reference

Normalised (mid-cycle) earnings by averaging over a full cycle — Graham & Dodd, *Security
Analysis*, on averaging earnings over a period long enough to span good and bad years;
Damodaran, *The Dark Side of Valuation*, on normalising cyclical companies by average margin
applied to current revenue. ★ **HOUSE VARIANT:** the window is chosen by a judgement block,
blind to price, and applied by this code — the choice and the arithmetic are separated.

## Assumptions

- The window spans a representative cycle. ⚠ **Yes, often violated**, and deliberately not
  checked here: whether a window is representative is `J-20`'s judgement, recorded with its
  named trough and peak years.
- ✏ Loss years are included: `D6` `v2` takes `t = 0` when pretax income ≤ 0 (L3 `DX-104`).
  A year that still cannot be computed (an absent item, a garbled rate on a profit) makes
  the window REFUSE, naming it.
- The margin method assumes margins, not levels, are what revert. ⚠ Violated by a business
  whose revenue base has changed structurally within the window.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **Average around unusable years** | Drops the troughs and biases the average upward — silently |
| **Median** | Discards the magnitude of the trough and peak the window was chosen to include |
| **Model-supplied figure** | Puts arithmetic in a prompt (`S-2`, `MP-6`) |

## Known-answer test

FCFF 3,000 · −100 · 2,000 · 2,800 · 500 · −400 over FY2019–FY2024 ⇒ mean 1,300.
`tests/unit/test_normalise_d5.py::test_ac_f10_19_the_averages_are_D02_functions_and_D01_holds_no_series_arithmetic`
