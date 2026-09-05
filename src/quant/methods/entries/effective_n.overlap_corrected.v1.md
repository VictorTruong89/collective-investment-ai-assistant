# `effective_n.overlap_corrected.v1` — independent observations under overlap

## Statement

    N_eff = T / h

★★ **Overlapping labels are the whole problem.** At horizon `h` with daily
observations, consecutive labels share `h−1` days of return, so `T` dates do not
supply `T` independent observations.

## Symbols

`T` = dates with a usable cross-section · `h` = horizon in trading days.

## Reference

`L1-quantitative-analysis.md` §5.3b: *"overlapping labels cut the independent
count to `T/h`"*. The correction is the same one Newey–West applies in the time
domain; here the overlap length is known exactly rather than estimated, so the
division is exact rather than a bandwidth choice.

## Assumptions

- ⚠ **The correction is exact only if the label windows tile.** Non-overlapping
  sampling would give `T/h` genuinely independent draws; daily sampling gives
  `T` correlated ones whose *effective* count is about `T/h`. This treats the
  two as equal, which is the standard approximation and is **conservative in the
  direction that matters** — it lowers the t-statistic.
- It ignores cross-sectional dependence, which **QA-43's effective breadth**
  handles separately and which this number does not claim to cover.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **`N = T`** | Inflates every t-statistic by `√h` — **4.6× at 1m** — and turns noise into a passing gate. This is the error QA-5 exists to prevent |
| **Newey–West with an estimated bandwidth** | Estimates a quantity we already know exactly; a bandwidth choice is a free parameter where none is needed |

## Known-answer test

`T = 1915`, `h = 21` ⇒ `N_eff = 91.2`.
`tests_src/test_quant_evaluation.py::test_effective_n_divides_by_the_horizon`
