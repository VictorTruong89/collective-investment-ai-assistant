# `dcf.two_stage_fcff_firm_rate.v1` — two-stage DCF, FCFF at a firm rate, minus net debt

Code: src/feature_engineer/valuation/dcf.py @ sha256:9022eb6b62c8ab02
*(QA-25 / F12 AC-F12.22 — pinned 2026-10-05 as the baseline; re-pin only after re-reading this entry against the changed code.)*

## Statement

    fcff_y  = base × (1 + g₁)^y                         y = 1 … N
    PV_y    = fcff_y ÷ (1 + r)^y
    TV_N    = base × (1 + g₁)^N × (1 + g_T) ÷ (r − g_T)
    EV      = Σ PV_y + TV_N ÷ (1 + r)^N
    equity  = EV − net_debt
    value per share = equity ÷ diluted_shares

Each monetary term is rounded half-up to minor units exactly once, and `EV` is the
exact sum of the rounded present values (`F10` `CT-F10.2`).

## Symbols

| Symbol | Meaning |
|---|---|
| `base` | the cash-flow basis — reported (`fv_model`) or a judgement's (`fv_analyst`) |
| `r` | firm discount rate (a declared constant, `D4`) |
| `g₁`, `g_T` | stage-1 and terminal growth |
| `N` | explicit years |

## Reference

The two-stage discounted-cash-flow model with a Gordon-growth terminal value
(Damodaran, *Investment Valuation*, ch. 12, 15; Koller et al., *Valuation*). The
firm route — FCFF at a firm rate, then subtract net debt — is one of the two
coherent designs; the other (FCFE at the cost of equity) is rejected below.

## Assumptions

- `r > g_T`, or the terminal value has no finite answer — ⚠ enforced: it REFUSES.
- ⚠ **Yes, violated: `r` is one constant for every company** (`D4`), not a
  company-specific cost of capital. Deliberate for transparency; the sensitivity
  band (8–11 %) shows what it costs. CAPM is a future version.
- ⚠ **Net debt omits marketable securities and leases** until D-07 carries them
  (`F10` `Q2`). Every result declares this under `net_debt.known_omissions`.
- Growth is constant within each stage — a simplification that a cyclical
  violates; the judgement basis, not this formula, is where the cycle is handled.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **FCFE at the cost of equity** | Needs net borrowing per period and a beta the vendor serves only as a snapshot with no history |
| **EV ÷ shares with no net-debt step** | The inherited `D-19` defect — 455 % of market cap on CHTR |
| **Exit-multiple terminal value** | Imports a market price into a value meant to be compared with the market price |

## Known-answer test

Base 1,000 · `r` 9 % · `g₁` 5 % · `g_T` 2.5 % · `N` 5, each figure worked by hand
with independent `Decimal` arithmetic.
`tests/unit/test_valuation_f10.py::test_ac_f10_1_the_mechanics_match_a_hand_worked_two_stage_dcf`
