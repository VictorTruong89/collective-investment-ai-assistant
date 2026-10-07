# `se.newey_west_bartlett.v1` — the realised standard error of the mean IC

## Statement

    e_t   = IC_t − mean(IC)                       (per-date rank IC, t = 1..T)
    γ_k   = (1/T) · Σ_{t>k} e_t · e_{t−k}
    w_k   = 1 − k / (L + 1)                       (Bartlett)
    Var   = (γ_0 + 2 · Σ_{k=1..L} w_k · γ_k) / T
    SE    = √Var        with  L = h − 1

★ **F12 `D9` (Victor, 2026-10-06; closes L6 `AB-12`)**: `ic_significance` passes only if
`|mean IC| ≥ 3 × SE`. The null `corrected_se` (`mde.rank_ic.v1`) stays as the planning figure.

## Symbols

`IC_t` = Spearman rank IC on date `t` · `T` = dates with a usable cross-section ·
`h` = label horizon in trading days · `L` = lag window.

## Reference

Newey & West (1987), *Econometrica* 55(3) — the heteroskedasticity- and autocorrelation-consistent
variance with Bartlett weights. The standard correction for the mean of overlapping-return statistics.

## Assumptions

- ⚠ **The lag window is FIXED at `h − 1`, not estimated** — consecutive `h`-day labels share exactly
  `h − 1` days, so the autocorrelation the overlap creates ends there. This is the same "known, not
  estimated" reasoning `effective_n.overlap_corrected.v1` used to reject a *data-chosen* bandwidth.
- It does **not** remove regime-level persistence beyond `h − 1` days (skill that is high for a year,
  then low): that variation is part of what the realised SE is meant to charge for, and a longer window
  would charge for more of it. Stated, not corrected (F12 `D3` — regime handling is a declared limitation).
- Fewer than `L + 2` dates, or a non-positive Bartlett variance on a tiny sample ⇒ `None`, never a guess.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **The null SE `√(h/((n−1)·T))`** as the acceptance test | The spread per-date IC would have *with no skill*; on the August 2026 fit it was 3.5× smaller than the realised spread (t 4.94 vs 1.42) — `D9` |
| **`sd(IC)/√(T/h)`** (L6 AB-12's quick realised form) | Right order of magnitude, but ignores the autocorrelation structure inside the window instead of weighting it |
| **A data-chosen bandwidth** | A free parameter where the overlap length is already known |

## Known-answer test

Series `1, −1, 1, −1`: `L = 0` ⇒ **0.5**; `L = 1` ⇒ **0.25** (worked by hand in the test).
`tests_src/test_quant_gates_d9_d10.py::test_ac_f12_31_newey_west_known_answers`
