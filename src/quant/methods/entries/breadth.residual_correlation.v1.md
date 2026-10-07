# `breadth.residual_correlation.v1` — effective breadth

Code: src/quant/metrics/breadth.py @ sha256:8dd2d1600e5c1fac
*(QA-25 / F12 AC-F12.22 — re-pinned 2026-10-06 after re-reading this entry against the change: the formula is unchanged; `held_book_breadth()` was added as a DIAGNOSTIC (F12 `D10`) and the gate now consumes `BR` through the implied IR `|IC|·√BR ≥ 0.5` — see the section below.)*

## ✏ 2026-10-06 — how the gate uses this number (F12 `D10`)

`breadth_gate` no longer tests `BR ≥ 3` (which could not fail at 1m: `ρ = 1` still gives `BR = 12`). It tests the
implied information ratio `|IC| · √BR ≥ IR* = 0.5` on the UNIVERSE `BR` measured here. `held_book` — the top-N's
`n_eff` at this same universe `ρ`, × rebalances per year — is reported beside it and never gated. Provisional.

## Statement

    rho     = mean off-diagonal correlation of the RETURNS  (pairwise-complete)
    n_eff   = n / (1 + (n-1) * rho)
    BR      = n_eff * (252 / horizon_days)

★ **`BR` is bets per YEAR**, not a name count — Grinold & Kahn's `IR = IC·√BR`
counts independent *decisions* in a year. L1-quantitative-analysis v0.4.0
correction (c) records that `BR` was once conflated with `n`; `n_eff` and `BR`
are both reported and never interchanged.

## Symbols

`n` = names in the cross-section · `rho` = average pairwise return correlation ·
`n_eff` = effective independent names · `horizon_days` = the rebalance interval.

## ⚠⚠ Divergence from QA-43 — stated, not silent

QA-43 asks for the average pairwise **residual** correlation *"after removing the
market and dominant sector factors."* **Measured 2026-08-27 on synthetic panels
with a known common correlation, that procedure returns `−1/(n−1)` and nothing
else:**

    n     rho_true   rho_residual   -1/(n-1)     rho_raw
    12      0.00       -0.09090     -0.09091      0.0060
    12      0.35       -0.09088     -0.09091      0.3384
   500      0.35       -0.00200     -0.00200      0.3463

★★ **Identical at `rho_true = 0.00` and `0.35`.** Removing a factor built from
the same names removes the correlation the measure exists to find. The raw
measure recovers the truth to three decimals.

★ Both readings are legitimate and ask different questions: *residual*
correlation asks **"is there structure left after the known factors"**; G&K's
`BR` asks **"how many independent bets does this book hold"** — and ten names all
with β≈1 are one bet however independent their residuals are. The gate wants the
second, so it is fed `rho_raw`; the residual figure is reported beside it.

⚠ **QA-43 is not amended.** Which statistic the gate should consume is **QQ-14,
open** — see **QA-124**.

## Reference

`L1-quantitative-analysis.md` QA-43, QA-44, QA-124, QQ-14 · Grinold, R. & Kahn,
R. (2000). *Active Portfolio Management*, 2nd ed., Ch. 6.

## Assumptions

- ⚠ **A negative `rho` is clamped to zero** — `n_eff > n` is not a meaningful
  answer, since a book cannot hold more independent bets than positions.
- ⚠ **Declines rather than guessing**: fewer than 10 names or 60 overlapping
  dates returns `None`, and the gate reads that as `NOT_EVALUATED`. QA-43:
  *neither `BR = n` nor the equally-weighted-mean haircut is admissible as a
  default* — substituting `n` would pass every universe by construction.
- ⚠ One correlation over the whole window; no regime split. A universe whose
  correlation rose in a crisis reports its average, not its worst.

## Demonstrates QA-44

At `rho = 0.35`, going from 12 names to 500 moves `n_eff` from **2.54 to 2.88** —
*488 extra names buy a third of a bet*, which is QA-44's *"370 more semiconductor
names add little"* measured rather than asserted.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **`BR = n`** | ⚠ QA-43 forbids it in terms. It passes every universe by construction, and a ten-name book inside one theme is closer to **1-2** |
| **The equally-weighted-mean haircut** | ⚠ Also named and forbidden by QA-43 — a fixed discount is an assumption wearing a measurement's clothes |
| **Residual correlation after cross-sectional demeaning** | ★★ Returns `−1/(n−1)` **identically at every true correlation** — see the divergence table above. It measures `n`, not the market |
| **Eigenvalue effective rank** `(Σλ)²/Σλ²` | A defensible alternative that answers the same question; not chosen because the pairwise form is the one QA-43 names and is readable without a spectral decomposition. ⚠ Would be the natural second opinion if QQ-14 reopens this |
| **Rolling / regime-split correlation** | Would report the worst regime rather than the average, which is arguably what a risk gate wants. ⚠ Not built — it needs a declared window, and an undeclared one is CN-10's defect |

## Known-answer test

`tests_src/test_quant_breadth.py` builds panels whose **true** common correlation
is known by construction and asserts the estimator recovers it:

    n=200, T=750, rho_true in {0.00, 0.10, 0.35, 0.60}
      -> measured rho within +/- 0.02 of the truth

    rho = 1.0, n = 500  ->  n_eff = 1.0     (one theme, one bet)
    rho = 0.0, n = 500  ->  n_eff = 500.0

★ And the negative control: the **residual** form returns `−1/(n−1)` at both
`rho_true = 0.00` and `0.35`, which is the assertion that keeps the divergence
above honest.

`tests_src/test_quant_breadth.py::test_the_raw_measure_recovers_a_known_correlation` ·
`tests_src/test_quant_breadth.py::test_the_residual_measure_returns_minus_one_over_n_minus_one_regardless`
*(✏ 2026-10-05, AC-F12.19: the section named the file only.)*
