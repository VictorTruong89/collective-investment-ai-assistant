# `rank_ic.spearman.v1` — cross-sectional rank information coefficient

## Statement

For each date `t`, the Spearman rank correlation between the score and the
realised forward label across the names present on that date; the reported
statistic is the **mean over dates**.

    IC_t = spearman( score_{i,t} , label_{i,t} )        over i on date t
    IC   = mean_t( IC_t )

⚠ **Per date, then averaged — never pooled.** A pooled correlation mixes the
cross-section with the time series and answers a question nobody asked.

## Symbols

| Symbol | Meaning |
|---|---|
| `n` | names in the cross-section on date `t` |
| `T` | number of dates with a usable cross-section |
| `h` | horizon in trading days |

## Reference

Spearman rank correlation. The cross-sectional-then-average construction is the
standard IC definition in the factor literature (Grinold & Kahn, *Active
Portfolio Management*).

## Assumptions

- A date needs **at least two names** to have a cross-section; fewer is
  `NOT_EVALUATED`, not zero (QA-17).
- Zero variance on either side makes the correlation undefined — ⚠ that date is
  **dropped, not counted as 0.0**, which would bias the mean toward no signal.
- Rank correlation is robust to the score's scale, which is why the ranker may
  emit any monotone transform without changing this number.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **Pearson IC** | Sensitive to outliers, and the score is used only as an *ordering* (MT-28) — a rank statistic matches the use |
| **Pooled correlation over all (i,t)** | Confounds cross-sectional skill with time-series drift, and its N is wrong by a factor of `T` |

## Known-answer test

Perfectly rank-ordered scores give `IC = 1.0`; reversed give `-1.0`.
`tests_src/test_quant_evaluation.py::test_rank_ic_is_one_when_the_ordering_is_perfect`
