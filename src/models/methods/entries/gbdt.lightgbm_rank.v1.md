# `gbdt.lightgbm_rank.v1` — gradient-boosted trees for the 1m selection leg

Code: src/models/zoo/gbdt.py @ sha256:870c5de7f888d4f8
*(QA-25 / F12 AC-F12.22 — pinned 2026-10-05 as the baseline; re-pin only after re-reading this entry against the changed code.)*

## Statement

A LightGBM regressor fitted on the volatility-normalised forward return at the
21-day horizon, producing a **score used only as an ordering** (MT-28).

    score_i = sum_k f_k(x_i)          f_k a regression tree, boosted on L2 loss

★ The output is **not** a return forecast and is never rendered as one. D-03
de-normalises it into `ranked_quantity` for the nomination (QA-58, QA-119).

## Symbols

| Symbol | Meaning |
|---|---|
| `x_i` | the feature vector for name `i`, from D-02's pinned contract |
| `f_k` | the k-th boosted regression tree |
| `num_leaves`, `learning_rate`, `n_estimators` | capacity and step size |

## Reference

Ke et al. (2017), *LightGBM: A Highly Efficient Gradient Boosting Decision
Tree*, NeurIPS. Chosen over the neural branch per **MT-37**: tree ensembles
still outperform deep learning on typical tabular data, and this data has **far
lower SNR** than those benchmarks.

## Assumptions

- ⚠ **Determinism is not the default.** `deterministic=True`, `force_row_wise=True`
  and `num_threads=1` are required or repeated fits differ in the low bits —
  and **INV-2 is a property of the whole invocation**, not an aspiration.
- Missing values are consumed **natively**, which is precisely how D-17's
  all-NaN columns produced an ordinary-looking score. ★ That is why parity
  (MT-7) must reject them *before* this estimator ever sees the frame — the
  family cannot defend itself here.
- L2 loss on a normalised target is a **proxy** for rank quality. The metric
  that decides is rank IC (D-03), not the training loss.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **A neural branch (FT-Transformer, TabM)** | **MT-37** keeps it in D-10 until it beats the GBDTs *at 1m* on D-03's protocol |
| **`LGBMRanker` (LambdaRank)** | Optimises NDCG at a cut-off; the decision needs the **whole cross-section ordered**, and D-01 covers the top `k_cov` rather than a single winner (RA-55, QA-122) |
| **Nine families, as the legacy tree carries** | **MT-36** — an unretained family is *maintenance surface, not optionality*. 2,736 LOC across 18 files for one production horizon |

## Known-answer test

On a monotone synthetic signal the fitted model reproduces the ordering
(rank IC = 1.0), and two fits with the same seed are byte-identical.
`tests_src/test_models_zoo.py::test_the_family_recovers_a_monotone_signal`
`tests_src/test_models_zoo.py::test_two_fits_with_the_same_seed_are_identical`
