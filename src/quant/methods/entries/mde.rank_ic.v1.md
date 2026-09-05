# `mde.rank_ic.v1` — the smallest detectable rank IC

## Statement

    SE(mean IC) = sqrt( h / ((n-1) * T) )
    MDE(t*)     = t* * SE(mean IC)

★ **MDE is computable BEFORE anything is measured — it is the bar, not a
prediction.**

## Symbols

`n` = names per cross-section · `T` = dates · `h` = horizon in trading days ·
`t*` = the t-threshold, **3.0** for multiple testing.

## Reference

`L1-quantitative-analysis.md` §5.3b. Under the null, `ρ_t` has variance
≈ `1/(n−1)`; averaging over `T/h` independent dates divides by that count.

## Assumptions

- Null variance `1/(n−1)` is the large-`n` Spearman approximation.
- ⚠ `t* = 3` is the multiple-testing threshold the spec's own table uses; at
  `t* = 2` the bar is a third lower and **more strategies pass than should**.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **A fixed IC threshold (e.g. 0.03)** | It means completely different things at different `n`, `T` and `h`. §5.3b's table shows the same 0.03 is undetectable at 1q and comfortable at 1w |

## Known-answer test

`n = 130`, `T = 1915`, `h = 21`, `t* = 3` ⇒ **0.0277**, matching §5.3b's
published table to four decimal places.
`tests_src/test_quant_evaluation.py::test_mde_reproduces_the_specs_published_table`
