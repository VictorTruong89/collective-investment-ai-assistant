# `risk_budget_dynamic_v1` — the dynamic per-trade risk budget

## Statement

    risk_budget_i = r_ceiling × E_i × C_i × P_i × D_i        each factor ∈ (0, 1]

The most that may be **lost** on the trade if the stop is hit, expressed as a
fraction of account equity. ⚠ **Not the capital deployed** — the two are related
by `entry / stop_distance` and nothing else.

## Symbols

| Symbol | Meaning | Source |
|---|---|---|
| `r_ceiling` | the **maximum**, not the target (INV-022) | configuration |
| `E_i` | edge — signal strength against the cross-section | D-03 `rank_score` |
| `C_i` | confidence — RM-1 verdict stability, calibration, coverage | D-01, D-04 |
| `P_i` | marginal contribution to book risk, **not standalone** | D-05 |
| `D_i` | drawdown state | D-05, from D-11's book |

## Reference

Grossman & Zhou (1993) for the drawdown-control form of `D`; the marginal
contribution to risk (`MCTR`) is the institutional standard for `P`.

## Assumptions

- Each factor is independently measurable and bounded in `(0, 1]`.
- ★ Bounding at 1 makes **INV-022 structural**: the product can never exceed
  `r_ceiling`, so *"the system's own recommendation may never exceed
  MAX_POSITION_PCT"* holds **by construction rather than by a clamp bolted on
  afterwards**.
- Multiplicative combination assumes the factors are roughly independent. ⚠ They
  are not: a deep drawdown and low confidence often co-occur, so the product is
  **more conservative than either alone** — which is the safe direction, and is
  stated rather than corrected.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **A fixed percentage** | Wrong *in kind*, not imprecise: blind to edge, correlation, drawdown state, estimation confidence and the opportunity set (§5.1d) |
| **Fractional Kelly** | Produces the right edge×(1/vol) shape but is **savage under parameter uncertainty**; at IC ≈ 0.03 the input is mostly noise |
| **Additive factors** | Cannot make INV-022 structural — a sum has no natural ceiling, so the cap returns as a clamp |

## Known-answer test

With `r_ceiling = 0.02` and every factor `1.0` (all unmeasured), the budget is
exactly `0.02` — ★ **an unmeasured framework degrades to the fixed percentage it
replaces, visibly**, rather than to a smaller number that looks like caution.
`tests_src/test_portfolio_b5.py::test_ac_6_9i_the_product_never_exceeds_r_ceiling`
