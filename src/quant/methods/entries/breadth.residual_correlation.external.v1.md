# `breadth.residual_correlation.external.v1` — residual correlation against EXTERNAL factors

## Statement

    for each name i:  r_i,t = a_i + b_i·M_t                  + e_i,t      (market)
                      r_i,t = a_i + b_i·M_t + c_i·S_sector(i),t + u_i,t   (market + sector)
    rho_market        = mean over pairs i≠j of corr(e_i, e_j)
    rho_market_sector = mean over pairs i≠j of corr(u_i, u_j)
    n_eff = n / (1 + (n−1)·rho)     BR = n_eff × 252 / h

## Symbols

`r` = the 21-day forward return sampled daily (the label) · `M` = SPY's return on the same basis · `S` = the
GICS sector SPDR's (XLK, XLF, XLV, XLY, XLP, XLE, XLI, XLB, XLU, XLRE, XLC) · one OLS per name, with intercept,
over the rows where the name and its factors all exist.

## Reference

Grinold & Kahn, *Active Portfolio Management* (2nd ed., 2000), ch. 6 (breadth as independent ACTIVE bets);
an information ratio is defined on active (residual) return, so the correlation that limits breadth is the
residual one. F12 `D12` records why the factors must be external.

## Assumptions

- ⚠ **The ETFs are cap-weighted and HOLD these names**: a mega-cap's own move is partly inside its factor, which
  pushes its residual correlation with the rest slightly down — small for the market, larger in thin sectors
  (Real Estate, Materials). Reported, not corrected.
- ⚠ XLC begins 2018-06-18; a Communication Services name has no sector residual before it.
- ⚠ The sector map is today's GICS, applied to the whole window (DE-77).
- One β per name over the whole window (a rolling β would add an undeclared window).

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **Equal-weight factor from the panel (`v1`'s residual)** | Forced to `−1/(n−1)` (AC-F12.28) |
| **PCA factors from the panel** | Built from the same names — the same trap, more subtly |
| **Raw correlation (the gate today)** | Counts the market's swing as a bet; an IR on active return holds no market bet |

## Known-answer test

Synthetic panel `r = M + 0.7·S + h·H + ε` with external `M`, `S`: residual ρ = `h²/(h²+1)` is recovered to ±0.02
for `h ∈ {0, 0.333, 0.5}`, while `v1`'s residual reads `−1/(n−1)` on the same panel.
`tests_src/test_quant_breadth_external.py::test_ac_f12_34_recovers_a_known_residual_correlation`
