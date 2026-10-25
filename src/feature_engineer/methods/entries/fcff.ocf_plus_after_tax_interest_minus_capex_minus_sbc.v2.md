# `fcff.ocf_plus_after_tax_interest_minus_capex_minus_sbc.v2` — the reported cash-flow basis

Code: src/feature_engineer/valuation/basis.py @ sha256:8442136b89e268c8
*(QA-25 / F12 AC-F12.22 — pinned 2026-10-05 as the baseline; re-pin only after re-reading this entry against the changed code.)*
*✏ Re-pinned 2026-10-21 after re-reading: F10 `D12` (`DX-176`, `DX-177`) added `_with_year_end_balance` — where net debt and the diluted count are READ after a 10-K. The FCFF formula this entry states is unchanged.*
*✏ Re-pinned 2026-10-23 after re-reading: F10 `D12` ✏ (`DX-189`, AC-F10.25) judges the year-end balance items per FACT (`_own_tags`) — again only where net debt is READ. The FCFF formula this entry states is unchanged.*

## Statement

Trailing-twelve-month free cash flow to the firm, from four discrete, contiguous
EDGAR quarters (`F10` `D6`):

    t         = income_tax_ttm ÷ pretax_income_ttm     when pretax_income_ttm > 0
    t         = 0                                      when pretax_income_ttm ≤ 0   (v2)
    base_fcff = OCF_ttm + interest_expense_ttm × (1 − t) − capex_ttm − SBC_ttm

## Symbols

| Symbol | Meaning |
|---|---|
| `OCF_ttm` | net cash provided by operating activities, summed over four quarters |
| `interest_expense_ttm` | interest expense, four quarters |
| `t` | effective tax rate over the same four quarters |
| `capex_ttm` | payments to acquire property, plant and equipment |
| `SBC_ttm` | share-based compensation (added back inside OCF as non-cash) |

## Reference

The operating-cash-flow route to FCFF (Damodaran, *Investment Valuation*, ch. 15:
`FCFF = CFO + interest × (1 − t) − capital expenditure`). ★ **HOUSE VARIANT** in one
respect: stock-based compensation is also subtracted (Victor Truong, 2026-09-13),
treating pay in shares as a cost owners bear through dilution.

## Assumptions

- US GAAP classifies interest PAID in operating cash flow — so after-tax interest
  is added back to reach a pre-financing flow that matches a firm discount rate
  (`D2`). ⚠ **Violated for IFRS filers**, who may classify interest paid in
  financing: adding it back there double-counts. Not handled; D-07 serves US
  EDGAR filers today.
- The effective tax rate over the trailing year approximates the marginal rate on
  interest. ⚠ **Yes, violated** where tax credits or losses distort it; on a POSITIVE
  pretax income a rate outside `[0, 1]` REFUSES rather than substituting a statutory rate.
- ✏ **v2 (2026-09-14, L3 `DX-104`): a loss year takes `t = 0`** — no taxable income, so
  interest shields nothing this year. ⚠ **Violated where losses carry forward**: the
  shield is deferred, not lost, so `v2` slightly overstates a loss year's FCFF. v1
  refused instead, which made every cycle window through a trough impossible.
- ⚠ Capex is total capital expenditure — maintenance is not separated from growth,
  so a company investing heavily at a cycle upswing (Micron, 2025) shows a low
  basis. That is the reported fact, and why a judgement basis (`fv_analyst`,
  `D1`) exists beside it.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **OCF − capex** | After interest, so discounting it at a firm rate counts debt twice — `D-19`'s shape |
| **EBIT × (1 − t) + D&A − capex − ΔNWC** | Coherent, but needs D&A and working-capital lines the canonical items lack: more items, more places to err |
| **Leave SBC in** | Overstates the cash available to owners |
| **Refuse a loss year (v1)** | A cycle average needs the troughs; dropping them biases it upward |
| **Statutory rate in a loss year** | A substituted default (`P5`); the filing's own position is "no tax" |

## Known-answer test

OCF 12,000 · interest 400 · tax 1,000 on pretax 4,000 (`t` = 0.25) · capex 8,000 ·
SBC 800 ⇒ `12,000 + 400 × 0.75 − 8,000 − 800 = 3,500`. Loss year (pretax ≤ 0) ⇒ `t = 0` ⇒
`12,000 + 400 − 8,000 − 800 = 3,600` (`tests/unit/test_valuation_f10.py::test_ac_f10_17_a_loss_year_uses_a_zero_tax_rate`).
`tests/unit/test_valuation_f10.py::test_ac_f10_17_the_reported_basis_is_ocf_plus_after_tax_interest_minus_capex_minus_sbc`
