<!-- ARCHIVED — DO NOT CODE FROM THIS FILE -->

> **⚠️ ARCHIVED / HISTORICAL — NOT AUTHORITATIVE.** Frozen on 2026-08-08. This is a pre-SDD
> Release 1–5 document, kept as an immutable record of what was decided at the time. It does **not**
> describe the code today and it is **not** a set of instructions to execute. Paths inside predate the
> `notebooks/` → `sdd/` rename and are deliberately left unrewritten.
>
> **Authoritative sources:** `sdd/specs/vision.md` (what this project is) ·
> `sdd/specs/constitution.md` (the rules) · `sdd/specs/F<n>_<slug>/spec.md` (what a feature must do) ·
> `sdd/specs/F0_code_map/spec.md` (what the code currently looks like). See `sdd/archive/README.md`.

---

# Feature 3-c — Per-Model Hyperparameter Tuning: Consolidated Evaluation Report

**Project:** AI Investment Pipeline (Release 5) · **Experiment:** Feature 3-c (per-model
hyperparameter tuning, Group A + Group B) · **Universe:** 123-name sector-balanced
S&P 500 panel · **Validation:** Combinatorial Purged Cross-Validation (CPCV).

| | |
|---|---|
| **Status** | ✅ Complete — 25 sweeps, 9 model families × 3 prediction roles, 0 open failures |
| **Group A (classical, CPU-tier)** | LightGBM, XGBoost, CatBoost, HistGB, RandomForest, Linear — run 2026-06-24 → 2026-06-27 |
| **Group B (deep-learning, GPU)** | FT-Transformer, TabM, LSTM — run 2026-06-28 → 2026-06-29 |
| **Production recommendation** | **RandomForest** (stock ranking) + **Linear/ElasticNet** (return sizing); classifier head shelved |
| **Headline finding** | A small but genuine edge exists (best RankIC ≈ 0.026); no model clears the 0.30 ICIR reliability gate; deep learning adds nothing for ~100× the compute |
| **Source of record** | **`reports/experiments/Rel5_Experiment/`** (committed to git) — all 25 sweep report dirs, the winners run, `tuned_winners.md`, and full console logs. Every figure below is cross-checked against those `tuning_report.json` files; if the archive is ever lost, this document IS the record. |

> **This document supersedes and consolidates four prior notes:** `groupA_combined_analysis.md`,
> `groupA_full_results_explained.md`, `groupB_and_crossmodel_analysis.md`, and
> `tuned_winners.md`. Where those notes carried minor rounding differences, the values
> here are taken directly from the experiment JSON (see §12, Data Provenance).

> **Terminology — "sweep" / "swept".** Throughout this report, a **sweep** is one
> complete tuning experiment for **one model family in one role**: every candidate
> hyperparameter configuration ("variant") of that family is trained and scored on
> all 15 CPCV splits, and the selection rule (§5.6) names one winner. "The **swept**
> role" means the role being tuned in that sweep. The 25 sweeps here = 6 Group-A
> families × 3 roles, plus FT-Transformer × 3, TabM × 3, and LSTM × 1 (ranker-only).

---

## Executive Summary

We evaluated **nine machine-learning model families** (each introduced individually in
§3), tuned and scored independently on three prediction tasks ("roles") — ranking stocks,
predicting return magnitude, and classifying up/down (why three, and how they combine
into one trading signal, is explained in §4) — under a rigorous, leak-resistant
cross-validation scheme. The goal
was to choose the model(s) that power the live pipeline's daily stock selection.

**Three conclusions:**

1. **The winners are simple, "averaging" models.** **RandomForest** is the best stock
   *ranker* (RankIC 0.0257) and **Linear/ElasticNet** is the best *return-magnitude*
   predictor (IC 0.0342, and astonishingly stable). Both are cheap, CPU-only, and robust.

2. **Complexity did not pay.** The two boosting models that use a specialised *ranking
   loss* (LightGBM, XGBoost) collapsed to near-zero skill, and all three **deep-learning**
   models (FT-Transformer, TabM, LSTM) were beaten by a plain random forest while costing
   ~100× more compute. The best deep model (FT-Transformer) only matched the *middle* of
   the classical pack.

3. **The edge is real but marginal.** The best models show a small, genuine predictive
   edge (RankIC ≈ 0.02–0.03 is meaningful in finance), but **no model cleared the 0.30
   "reliability gate"** (best consistency score ICIR ≈ 0.126). This is the honest verdict
   the cross-validation is designed to surface: deployable, but only at conservative size.

---

## 1. Background & Objective

The live pipeline must, each trading day, rank ~123 stocks and act on the strongest names.
Feature 3-c answers a focused question: **for each candidate model family, what is the
best hyperparameter configuration, and how do the tuned families compare head-to-head**
under honest validation? The output feeds the cross-model production decision (Feature 3-a)
and the daily-sleeve selection logic (Feature 3-b).

The experiment is deliberately structured so that *every* family is given a fair, equally
rigorous chance: the same data, the same validation, the same selection rule, the same
three roles.

---

## 2. Data & Universe

| Item | Value |
|---|---|
| Universe | **123 names**, sector-balanced across all 11 GICS sectors (IT capped at 18) |
| Price panel | `data/ohlcv/price_data.parquet` — 123 tickers, **349k rows**, 2015-01-02 → 2026-04-30 |
| Fundamentals panel | `combined_features_for_fundamental_training.parquet` — 123 tickers, **343k rows**, 96 columns |
| Feature set | `ALL_FEATURES` (≈59 numeric features: momentum, volatility, valuation, fundamentals) |
| Prediction horizon | 1 week forward return (`label_horizon: 1w`) |
| **Data-quality caveat** | **96.4 % of rows carry ≥1 NaN feature** (sparse fundamentals + rolling-window warm-up). This is central: it dictates which models even *run* (see §11, the `sklearn_gb` fix). |

**Why 123 names?** The earlier 30-name (mostly tech) universe starved the cross-sectional
statistics — each daily correlation was a 30-point estimate, far too noisy to be reliable.
Breadth is the binding constraint on reliability (the *fundamental law of active
management*, IR ≈ IC·√breadth). Expanding to 123 sector-balanced names lifted the
consistency score (ICIR) materially — though, as we will see, still short of the gate.

---

## 3. The nine model families — what they are and why we chose them

### 3.1 Orientation

The nine families were chosen to cover the full, recognised spectrum of learning
algorithms for tabular and time-series data: the simplest defensible baseline (a
regularised **linear** model), the two great decision-tree paradigms (**bagging**
and **boosting**, the latter in four flavours), and the three main **deep-learning**
archetypes for this kind of data (attention, ensembled MLPs, recurrence). Because
each family is the best-known representative of its *algorithm class*, the
head-to-head verdict generalises: when RandomForest beats FT-Transformer here, that
is evidence about *bagging vs deep attention on this problem*, not merely about two
libraries.

### 3.2 Model-by-model introduction

**Group A — classical models (CPU-tier)**

**1. Linear — ElasticNet (ranker/regressor) · Logistic Regression (classifier).**
The prediction is a weighted sum of the 59 features, with L1/L2 "shrinkage"
penalties that pull unimportant weights toward zero.
- *Pros:* trains in minutes; fully interpretable (the weights can be read and
  audited); extremely hard to overfit when strongly regularised — the honest
  scientific baseline every richer model must beat; the classic quant-finance
  workhorse for exactly this reason.
- *Cons:* cannot represent feature interactions or non-linear effects; sensitive to
  feature scaling and outliers; over-strong shrinkage can silently collapse the
  model to all-zero weights (several grid cells did exactly that — Appendix A).

**2. RandomForest — bagging (scikit-learn).**
Hundreds of decision trees, each trained on a random bootstrap sample using a
random subset of features; the forest's prediction is the *average* of the trees.
- *Pros:* averaging many decorrelated trees cancels noise — the ideal property for
  low signal-to-noise financial data; captures non-linearities and interactions;
  robust to outliers; few sensitive hyperparameters; tolerates NaN natively in
  modern scikit-learn.
- *Cons:* expensive to train at scale (12–14 h per role here — the single biggest
  compute item in Group A); large in memory; cannot extrapolate beyond the training
  range; usually loses to boosting on *strong-signal* problems.

**3. LightGBM — gradient boosting with a listwise ranking loss (`lambdarank`).**
Boosting builds trees *sequentially*, each new tree correcting the previous
ensemble's errors; LightGBM adds a purpose-built loss that directly optimises the
*ordering* of stocks.
- *Pros:* state-of-the-art accuracy on countless tabular benchmarks; extremely fast
  histogram-based training; NaN-native; the ranking loss is theoretically the
  "right" objective for a ranking task.
- *Cons:* the sequential error-chasing that makes boosting powerful makes it chase
  **noise** when the signal is weak; the ranking loss proved fragile on this broad,
  noisy panel (§6.3 — it collapsed to near-zero skill).

**4. XGBoost — gradient boosting with a pairwise ranking loss (`rank:pairwise`).**
The other industry-standard boosting library; its ranking mode optimises pairwise
"is A better than B?" comparisons.
- *Pros/Cons:* essentially as LightGBM — mature, fast, NaN-native, strong
  regularisation options; and it suffered the same ranking-loss collapse here.
  Keeping *both* LightGBM and XGBoost was deliberate: two independent
  implementations showing the same failure proves the problem is the objective
  *class*, not one library's bug.

**5. CatBoost — ordered gradient boosting (`YetiRank` ranking loss).**
A third boosting flavour whose "ordered boosting" trick reduces the subtle
target-leakage/overfitting that plagues standard boosting.
- *Pros:* excellent out-of-the-box defaults; measurably more overfit-resistant than
  the other two boosters (it kept a usable RankIC of 0.0192 where they collapsed);
  NaN-native.
- *Cons:* slower than LightGBM; still a booster on low-SNR data; middle of the pack
  on every role here.

**6. HistGB — scikit-learn `HistGradientBoosting` (pointwise objective).**
The same histogram-boosting machinery as LightGBM, but with a plain regression /
log-loss objective — it predicts a number per stock and we simply sort.
- *Pros:* NaN-native; very fast (<1 h per role); serves as the perfect *control*
  for the ranking-loss question — same algorithm family, different objective — and
  it ranked #3 overall, proving the objective was the culprit; strong classifier.
- *Cons:* fewer tuning knobs than the dedicated boosting libraries; no built-in
  ranking objective (which, here, turned out to be a feature).

**Group B — deep-learning models (GPU)**

**7. FT-Transformer — attention over feature embeddings.**
Each numeric feature is embedded as a token and a transformer applies self-attention
across the tokens — the strongest published deep architecture for tabular data.
- *Pros:* learns arbitrary feature interactions via attention; the best deep model
  here by far (#2 ranker, and the best ranker-consistency ICIR at 0.126); scales
  with data.
- *Cons:* by far the most expensive model (~12 h GPU *per role*, ~100× RandomForest
  for a slightly worse result); data-hungry — 343k rows is small by deep-learning
  standards; many sensitive hyperparameters; opaque.

**8. TabM — parameter-efficient ensemble of MLPs.**
A single network that internally simulates *k* parallel MLPs sharing most weights —
ensembling (variance reduction) at almost no extra cost.
- *Pros:* the cheap-ensembling idea mirrors what makes RandomForest work; fast on
  GPU (~0.6 h per sweep); the only Group-B sweep where tuning genuinely beat the
  default (>1σ, k=32 members).
- *Cons:* still data-hungry; weakest ranker among the serious contenders (RankIC
  0.0103); MLPs lack trees' built-in feature selection on noisy inputs.

**9. LSTM — recurrent network over daily price sequences.**
Reads each stock's recent history (20/60/120-day lookback) in order, one day at a
time, carrying a memory state — the canonical sequence model.
- *Pros:* the only family that models *temporal order* directly rather than through
  hand-built rolling features; cheap (~0.4 h); a necessary test of whether raw
  sequence modelling adds anything our engineered features miss.
- *Cons:* the sequence framing weakens cross-sectional comparability (each stock is
  scored from its own history); long lookbacks degraded sharply (120-day ≈ no
  skill); run as ranker only (sequence paradigm).

### 3.3 Why these nine — and why not others

Four selection criteria, applied deliberately:

1. **Cover the algorithm space, one strong representative per class.** Linear
   baseline → bagging → boosting (3 ranking-loss flavours + 1 pointwise control) →
   deep attention → deep ensemble-MLP → deep recurrence. Almost any model someone
   might propose is a member of one of these classes, so the experiment's verdict
   transfers to it.
2. **Proven track record on tabular/financial data.** GBDTs and RandomForest have
   dominated tabular ML benchmarks and quant practice for a decade; ElasticNet is
   the standard academic-finance baseline; FT-Transformer and TabM are the two
   strongest published deep-tabular architectures; LSTM is the canonical price-path
   sequence model.
3. **Fit to our data reality.** 343k rows with 96.4 % NaN-bearing rows and a
   consumer GPU: every family chosen either handles NaN natively or was fixable
   (the HistGB swap, §11), and trains within the CPCV budget.
4. **Mature, maintained open-source implementations** with reproducible seeds —
   a production pipeline cannot depend on research code.

**Considered and excluded:** SVM / kernel methods and Gaussian processes (training
scales quadratically-to-cubically with rows — infeasible at 343k); k-nearest-neighbours
(distance is nearly meaningless across 59 noisy dimensions; no NaN story); a plain
MLP (strictly dominated by TabM, which *is* an ensemble of MLPs); heavier
time-series transformers (e.g. Temporal Fusion Transformer — not justified until
*any* deep model demonstrates value here, which none did); and off-the-shelf AutoML
ensembles (opaque, and redundant with the explicit RF+Linear+HistGB ensemble we
recommend in §10).

---

## 4. Why each family trains three models — and how the three become one signal

### 4.1 Three heads, three different questions

A daily trading decision decomposes into three questions, and each wants a
different mathematical answer:

| Question | Head | ML task & loss | Output column |
|---|---|---|---|
| **Which** stock is most attractive today? | **Ranker** | learning-to-rank (or pointwise score + sort) | `rank_score` |
| **How much** do we expect it to move? | **Regressor** | regression on forward return | `pred_return` |
| **How likely** is it to go up at all? | **Classifier** | binary classification | `prob_up` |

A single multi-task model could attempt all three at once, but Release-5 testing
settled on the **"separate" paradigm**: three independent specialists per family.
The independence buys three concrete advantages: each head is trained and *measured*
on exactly the quantity it must deliver; tuning can proceed role-by-role
(coordinate descent, §5.4) and can train only the swept role (§5.8, a ~3× speed-up);
and errors diversify — three differently-trained models rarely fail the same way on
the same day.

### 4.2 The combination — the exact formula in the live pipeline

The blend is implemented in `SlotSelector.compute_opportunity` →
`SignalEngine.combined_score` → `SleeveSelector` (Feature 3-b). Step by step:

**Step 1 — normalise.** Each head's output is z-scored *across that day's 123
stocks*, putting the three heads on comparable units (standard deviations from the
day's average).

**Step 2 — weighted blend.** One "opportunity" score per stock:

```
opportunity = 0.55 · z(rank_score)  +  0.30 · z(pred_return)  +  0.15 · z(prob_up)
```

The weights live in `pipeline/ohlcv/policy/policy_params.json` (code defaults
0.60 / 0.30 / 0.10). They are **not hand-picked**: `SlotSelector` grid-searches
candidate weight triples and keeps the combination with the highest *backtest
Sharpe ratio* — i.e. the role weighting is itself an optimised hyperparameter.

**Step 3 — turnover penalty.** A small penalty is subtracted for names that would
require replacing a current holding (`adj_opportunity`), so the pipeline does not
churn positions for negligible expected gains.

**Step 4 — cross-signal soft blend.** `SignalEngine.combined_score` blends the
OHLCV opportunity with a *fundamental* composite and an optional *technical* score
(each z-scored, weights from `config.signal_engine.blend`, renormalised over
whatever is present). In the current configuration the OHLCV score carries full
weight, so `combined_score` ≈ the Step-3 output; the hook exists so fundamental
signals can be phased in without code changes.

**Step 5 — decision gates.** The sleeve policy considers only stocks with
**`prob_up ≥ 0.55`** (the classifier acts as a hard eligibility hurdle, not just a
15 % blend weight) whose score also beats a cash benchmark; it then takes the
**top-1** for today's sleeve, with hysteresis that keeps the incumbent holding
unless the challenger clearly beats it.

**Summary of each head's contribution to the final signal:**

| Head | Blend weight | Additional role in the decision |
|---|---|---|
| Ranker | **0.55** | primary driver of the daily pick |
| Regressor | **0.30** | magnitude information (and future position sizing) |
| Classifier | **0.15** | **plus** the hard `prob_up ≥ 0.55` eligibility hurdle |

### 4.3 What this experiment implies for the weighting

The weight ordering (ranker ≫ regressor > classifier) is vindicated by the measured
skill ordering: the ranker head carries genuine signal (best RankIC 0.0257), the
regressor adds independent, very stable magnitude information (best IC 0.0342), but
the classifier is barely better than a coin flip everywhere (AUC ≈ 0.51, §6). That
makes the classifier the weakest link *twice over* — its 0.15 blend weight adds
mostly noise, and its hard 0.55 hurdle filters candidates almost at random (a veto
with no skill can only cost opportunity). Hence the §9 recommendation to demote or
disable the classifier's influence until its label is reworked (§10, item 4).

---

## 5. Methodology

### 5.1 The prediction problem — three "roles" per model

Each model family is trained as three independent specialists ("separate" paradigm):

| Role | ML task | Output | Drives | Primary metric |
|---|---|---|---|---|
| **Ranker** | learning-to-rank | a score to *order* stocks | the daily top pick | **RankIC** |
| **Regressor** | regression | predicted % return | *position sizing* | **IC** of predicted return |
| **Classifier** | binary classification | P(up) | a yes/no filter | **AUC** |

The three heads are independent, which is what lets us tune each on its own metric
(coordinate descent, §5.4) and — for some models — train only the head being tuned (§5.8).

### 5.2 The nine model families at a glance (two compute groups)

Quick reference only — full introductions with pros/cons and selection rationale in §3.

| Group | Family | Type | Notes |
|---|---|---|---|
| **A** | **LightGBM** | gradient boosting + *ranking loss* (lambdarank / rank:pairwise) | NaN-native |
| **A** | **XGBoost** | gradient boosting + *ranking loss* | NaN-native |
| **A** | **CatBoost** | gradient boosting (YetiRank) | NaN-native |
| **A** | **HistGB** (`sklearn_gb`) | histogram gradient boosting, *pointwise* (regression/logloss) | NaN-native; replaced classic GB (§11) |
| **A** | **RandomForest** (`sklearn_rf`) | bagging (averaged deep trees) | NaN-tolerant in sklearn 1.7 |
| **A** | **Linear** | ElasticNet (reg/rank) / Logistic (cls) | heavy regularisation |
| **B** | **FT-Transformer** | attention/transformer for tabular | GPU, deepest model |
| **B** | **TabM** | parameter-efficient MLP ensemble | GPU |
| **B** | **LSTM** | recurrent sequence model | GPU; ranker-only (sequence paradigm) |

### 5.3 How each model's hyperparameter grid was chosen

Grids were not arbitrary — for each family we swept the **2–3 knobs that govern the
bias/variance trade-off** for that algorithm, around library-sensible defaults, biased
toward the *regularised* corner (shallow trees, stronger shrinkage) because finance data
is low signal-to-noise:

| Family | Knobs swept | Grid | Cells |
|---|---|---|---|
| LightGBM | `num_leaves` × `min_data_in_leaf` × `learning_rate` | 3×3×3 | 27 |
| XGBoost | `max_depth` × `learning_rate` × `min_child_weight` | 3×3×3 | 27 |
| CatBoost | `depth` × `learning_rate` × `l2_leaf_reg` | 3×3×3 | 27 |
| HistGB | `max_depth` × `learning_rate` × `max_leaf_nodes` | 3×3×3 | 27 |
| RandomForest | `max_features` × `min_samples_leaf` × `max_depth` | 3×3×3 | 27 |
| Linear (rank/reg) | `alpha` × `l1_ratio` (or learning-rate) | — | 12 |
| Linear (cls) | inverse-reg `C` | — | 4 |
| FT-Transformer | `d_token` × `n_layers` | 2×3 | 6 |
| TabM | `k_models` (ensemble width) × `hidden` | 3×2 | 6 |
| LSTM | `lookback` × `hidden` | 3×2 | 6 |

Grids are generated by `grid_gen.py` from a compact spec (`config/tuning/*.yaml`) so they
are reproducible and auditable — they are never hand-edited.

### 5.4 Search method — coordinate descent + full grid

- **Coordinate descent across roles:** each role is tuned on *its own* metric (ranker on
  RankIC, regressor on IC, classifier on AUC), rather than one global score. Cleaner and
  cheaper, because the heads are independent. In practice this means tuning one family
  = up to three *sweeps* — one self-contained tuning run per role.
- **Full grid within a sweep:** every cell in the small per-family grid above is evaluated
  (the generator also supports `random(N)` sampling, but every sweep here used exhaustive
  grids). Seeds are varied per cell to produce an honest spread.
- **Total:** 25 sweeps → **426 distinct (config × role) fits**, each evaluated over the
  full CPCV split set.

### 5.5 Validation — Combinatorial Purged Cross-Validation (CPCV)

Instead of a single train/test split we use CPCV (López de Prado):

- The timeline is cut into **N = 6 contiguous blocks**; we test on every combination of
  **k = 2** blocks → **C(6,2) = 15 train/test splits**.
- Each split applies **purge** (drop training rows whose label window overlaps the test
  window) and a **5-day embargo** (one label horizon) to eliminate look-ahead leakage.
- Recombining the splits yields **5 independent backtest "paths."** Every metric is
  reported as a **mean over the 5 paths with a path-σ (spread)**.

This is deliberately conservative — it makes a spurious edge *hard* to produce, which is
exactly what we want before risking capital.

### 5.6 Winner-selection rule (applied identically to every sweep)

1. **Gate:** require `RankICIR ≥ 0.30` (day-to-day consistency). *No sweep passed.*
2. **σ-adjusted ranking:** rank configs on `mean − 0.5 × path-σ` (penalise unstable wins).
3. **Simplicity tiebreak + "keep default":** if the best config beats the pre-declared
   default by **less than 1 path-σ**, keep the simpler default (a sub-1σ "win" on noisy
   data is almost certainly luck).

This is why most sweeps "recommend" their default config — tuning rarely beat noise (§6.4).

### 5.7 Metrics glossary

| Metric | Plain-language meaning | Reference points |
|---|---|---|
| **RankIC** | Spearman rank-correlation between predicted order of stocks and realised returns, averaged over days. A recommender-quality score. | 0 = no skill; **~0.02 is a real edge** in equities |
| **IC** | Pearson version, for the regressor's predicted returns | 0.02–0.03 is good here |
| **AUC** | P(model ranks a random up-day above a random down-day) | **0.50 = coin flip**; 0.52 ≈ negligible |
| **ICIR / RankICIR** | RankIC ÷ its day-to-day standard deviation = *consistency*. **The reliability gate.** | gate = **0.30**; best observed ≈ 0.126 |
| **path-σ** | spread of the metric across the 5 CPCV paths | smaller = more trustworthy |
| **mean/σ** | metric ÷ path-σ = signal-to-noise of the result itself | bigger = more reliable |
| **top-k Sharpe** | risk-adjusted return of actually holding the top-k picks (closest proxy to a live portfolio) | >1 good; here ~0.66–1.05 |

### 5.8 Compute, speed-ups & reproducibility

- **Group A** is CPU-bound classical training; total wall-clock ≈ **53 h**, dominated by
  **RandomForest** (12–14 h *per role* — 500 deep trees × 15 CPCV splits).
- **Group B** is GPU (telemetry-confirmed: 16–63 % utilisation, 1–2.8 GB VRAM). FT-Transformer
  cost **~12 h per role (~36 h total)**; TabM ~1.8 h; LSTM ~0.4 h.
- **`train_only_selected_role`** (opt-in): for the HistGB sweeps we trained only the head
  being tuned — bit-identical primary metric, ~3× faster. *Side-effect:* HistGB's
  *off-role* secondary metrics read 0.5 / 0.0 (those heads weren't trained), so HistGB is
  compared on its primary metric only. (FT/TabM/LSTM did **not** use this flag and trained
  all three heads — a known efficiency miss, see §10.)
- Seeds fixed per variant; library versions recorded in each `run_meta.json`
  (numpy 2.2.5, sklearn 1.7.2, lightgbm 4.6.0, xgboost 3.1.2, catboost 1.2.10,
  torch 2.11.0+cu129). Git commit `8320ff0`.

> **Telemetry caveat:** the `ran_on_gpu` flag in the JSON header is a VRAM-threshold proxy
> and reads `true` even for CPU-only sklearn families (idle desktop VRAM > 1 GB). Treat
> Group A as CPU-bound; only Group B is GPU-confirmed via utilisation.

---

## 6. Results

### 6.1 Master cross-model comparison matrix

Every model family, every key metric, in one place. Each value is the **best configuration
that family achieved for that role**, taken from its own role-sweep and cross-checked
against the JSON. **Bold = column winner.** Group B (deep) rows are marked 🟪.

| Model | Ranker RankIC ↑ | Ranker ICIR ↑ (gate 0.30) | Regressor IC ↑ | Regressor mean/σ ↑ | Classifier AUC ↑ | top-k Sharpe ↑ | Best-role train time |
|---|---|---|---|---|---|---|---|
| **RandomForest** | **0.0257** | 0.123 | 0.0268 | 5.4 | 0.5163 | 0.928 | 12–14 h (CPU) |
| HistGB | 0.0226 | 0.119 | 0.0234 | 4.9 | **0.5190** | 0.899 | ~0.9 h (CPU) |
| CatBoost | 0.0192 | 0.097 | 0.0137 | 2.5 | 0.5089 | **1.048** | ~1.4 h (CPU) |
| **Linear** | 0.0174 | 0.087 | **0.0342** | **52.6** | 0.5138 | 0.850 | ~0.5 h (CPU) |
| XGBoost | 0.0042 | 0.021 | 0.0158 | 2.8 | 0.5148 | 0.755 | ~1.9 h (CPU) |
| LightGBM | 0.0028 | 0.014 | 0.0131 | 3.0 | 0.5065 | 0.668 | ~1.2 h (CPU) |
| 🟪 FT-Transformer | 0.0232 | **0.126** | 0.0251 | 4.7 | 0.5114 | 0.905 | ~12 h (GPU) |
| 🟪 LSTM | 0.0112 | 0.081 | — *(ranker-only)* | — | — | 0.850 | ~0.4 h (GPU) |
| 🟪 TabM | 0.0103 | 0.072 | 0.0110 | 2.2 | 0.5123 | 0.662 | ~0.6 h (GPU) |

**How to read it:** the *ranker* columns decide the daily stock pick (most important); the
*regressor* columns decide bet sizing; *classifier AUC* near 0.50 means no directional
skill from anyone. The *top-k Sharpe* is the most portfolio-realistic single number.

### 6.2 Per-role leaderboards (sorted; full detail in Appendix A)

**Ranker — RankIC (drives the daily pick).** Higher is better; ICIR is the reliability gate.

| # | Model | RankIC | path-σ | ICIR | top-k Sharpe |
|---|---|---|---|---|---|
| 1 | **RandomForest** | **0.0257** | 0.0062 | 0.123 | 0.928 |
| 2 | FT-Transformer 🟪 | 0.0232 | 0.0062 | **0.126** | 0.905 |
| 3 | HistGB | 0.0226 | 0.0053 | 0.119 | 0.899 |
| 4 | CatBoost | 0.0192 | 0.0076 | 0.097 | 1.048 |
| 5 | Linear | 0.0174 | 0.0041 | 0.087 | 0.850 |
| 6 | LSTM 🟪 | 0.0112 | 0.0062 | 0.081 | 0.850 |
| 7 | TabM 🟪 | 0.0103 | 0.0016 | 0.072 | 0.662 |
| 8 | XGBoost | 0.0042 | 0.0007 | 0.021 | 0.755 |
| 9 | LightGBM | 0.0028 | 0.0014 | 0.014 | 0.668 |

**Regressor — IC of predicted return (drives sizing).**

| # | Model | IC | path-σ | mean/σ |
|---|---|---|---|---|
| 1 | **Linear** | **0.0342** | 0.0007 | **52.6** |
| 2 | RandomForest | 0.0268 | 0.0049 | 5.4 |
| 3 | FT-Transformer 🟪 | 0.0251 | 0.0053 | 4.7 |
| 4 | HistGB | 0.0234 | 0.0048 | 4.9 |
| 5 | XGBoost | 0.0158 | 0.0057 | 2.8 |
| 6 | CatBoost | 0.0137 | 0.0055 | 2.5 |
| 7 | LightGBM | 0.0131 | 0.0044 | 3.0 |
| 8 | TabM 🟪 | 0.0110 | 0.0050 | 2.2 |

**Classifier — AUC (up/down).** Everything is ~0.51; no real directional skill.

| # | Model | AUC | path-σ |
|---|---|---|---|
| 1 | HistGB | **0.5190** | 0.0023 |
| 2 | RandomForest | 0.5163 | 0.0017 |
| 3 | XGBoost | 0.5148 | 0.0026 |
| 4 | Linear | 0.5138 | 0.0021 |
| 5 | TabM 🟪 | 0.5123 | 0.0037 |
| 6 | FT-Transformer 🟪 | 0.5114 | 0.0031 |
| 7 | CatBoost | 0.5089 | 0.0022 |
| 8 | LightGBM | 0.5065 | 0.0033 |

### 6.3 The central story: bagging/pointwise beats ranking-loss boosting and deep nets

A clear pattern runs through every table:

> Models that score each stock **independently and then sort** — RandomForest (bagging),
> Linear, HistGB, CatBoost — *work*. The two that optimise a specialised **pairwise/listwise
> ranking objective** — LightGBM's `lambdarank` and XGBoost's `rank:pairwise` — *collapse*
> to near-zero (RankIC 0.0028 / 0.0042). The high-capacity **deep nets** land in the middle
> at best, never first.

This was investigated and is **not a bug**. The decisive evidence: **HistGB is the same
gradient-boosting family as LightGBM but uses a plain regression objective — and it ranks
#3 (0.0226).** So the culprit is the *ranking loss*, not boosting. On low signal-to-noise,
high-NaN, broad data, the fancy ranking objectives and the deep models have the capacity to
**fit noise**; "predict the number and sort" survives. (On the earlier 30-name tech-only
universe the ranking-loss models *looked* fine — that set had stronger, more learnable
patterns that masked the problem.)

### 6.4 Did tuning help? Barely — and that is the correct result

Across all 25 sweeps, the tuned best rarely beat the declared default by more than 1 path-σ,
so the selection rule (§5.6) **kept the simpler default** in the large majority of cases.
Where a config *did* win, it was consistently the **shallower / more-regularised** corner:

- RandomForest ranker: `max_features=sqrt, min_samples_leaf=20, max_depth=8` — the
  *shallow, regularised* corner beat the slow `max_depth=None` cells outright.
- Linear regressor: `alpha=0.01, l1_ratio=0.1` (stronger shrinkage) — the single most
  stable result in the entire experiment (IC 0.0342 at path-σ 0.0007, mean/σ ≈ 53).
- CatBoost / HistGB rankers: shallow depth (3–6), modest learning rate.

**Interpretation:** when the signal is this weak, most knob-twiddling fits noise. The
system correctly resists it. This validates the "cheap + regularised + stable" design bias.

### 6.5 The gate verdict

No model — classical or deep — reached the `RankICIR ≥ 0.30` reliability gate. The best
consistency scores cluster at **0.12–0.13** (FT-Transformer 0.126, RandomForest 0.123,
HistGB 0.119). Expanding the universe from 30 → 123 names *did* lift ICIR (e.g. CatBoost
0.078 → 0.097, Linear 0.075 → 0.087, and the new RF tops out at 0.123), confirming the
breadth thesis — but breadth alone was not enough to clear the bar.

---

## 7. Winning models — who wins, and why

| Role | Winner | Score | Why it wins |
|---|---|---|---|
| **Ranker** (daily pick) | **RandomForest** | RankIC 0.0257, ICIR 0.123 | Bagging averages out noise on a low-SNR, high-NaN, diverse panel; pointwise scoring avoids the ranking-loss overfitting trap; tolerant of missing values. |
| **Regressor** (sizing) | **Linear / ElasticNet** | IC 0.0342, mean/σ ≈ 53 | Heavy L2/L1 shrinkage is ideal for weak signal; by far the most *stable* result (path-σ 0.0007). Cheap and interpretable. |
| **Classifier** (filter) | *None usable* (HistGB nominal at AUC 0.519) | AUC ≈ 0.51 | No family shows real directional skill; do not gate trades on it. |

**Why not the deep models?** FT-Transformer is competitive (#2 ranker, #3 regressor, and
the single best ranker *ICIR* at 0.126) but never #1, and it costs **~100× more compute**
(12 h GPU/role vs minutes CPU). TabM and LSTM are cheap but the *weakest* rankers. There is
no deep model on the efficient frontier of skill-per-compute here. Deep learning needs more
data and stronger signal than this problem currently offers.

**Why not LightGBM/XGBoost?** Their ranking objectives collapse on this data (§6.3). If
retained at all, they must be switched to a plain regression objective — at which point
HistGB already fills that niche, faster.

---

## 8. Investment expectation from the recommended model

Taking the production stack — **RandomForest ranker + Linear regressor** — what should a
realistic investor expect? Stated honestly, with assumptions explicit.

- **The edge, sized.** RankIC ≈ 0.026 means the model's #1 pick out of 123 beats the
  average stock by a *small* margin, *on average, over many days*. Expect the daily pick to
  be "right" roughly **51–53 %** of the time — a thin edge repeated often, not a crystal ball.
- **Theoretical ceiling (diversified).** The fundamental law gives an annualised information
  ratio `IR ≈ ICIR_daily × √252 ≈ 0.12 × 15.9 ≈ 1.9` **gross of costs** — but only if you
  trade the *entire* 123-name book dollar-neutral every day. That is not the live strategy.
- **Realistic proxy (concentrated).** The live sleeve policy (1 stock/day) is far more
  concentrated and noisier. The measured **top-k Sharpe ≈ 0.85–0.93 (gross)** is the better
  guide; after transaction costs and concentration, expect an effective **Sharpe well under
  1 — plausibly 0.3–0.6**: positive expectancy, but with regular losing weeks and drawdowns.
- **Reliability flag.** Because the **0.30 ICIR gate was not met**, day-to-day consistency
  is low *by the project's own standard*. Cold streaks are expected, not anomalies.
- **No classifier edge.** AUC ≈ 0.51 — do not use the up/down head as a standalone trigger.

**Bottom line:** this is a **paper-trade / small-size** model, not a "bet the account"
model. The edge is genuine (the validation is built to *disprove* fake edges, and a small
one survived), but it is marginal and inconsistent. Use it as **one input**, keep sizing
conservative, and track live results for several months before scaling.

---

## 9. Recommended final AI pipeline (post-experiment architecture)

```
                ┌───────────────────────────────────────────────────────────┐
   Daily        │  Feature pipeline (ALL_FEATURES, ~59 cols, NaN-tolerant)  │
   123-name ───▶│  cross-sectional + fundamental features per stock        │
   panel        └───────────────┬───────────────────────────────────────────┘
                                │
                ┌───────────────┴────────────────┐
                ▼                                ▼
     ┌───────────────────────┐      ┌─────────────────────────────┐
     │  RANKER               │      │  REGRESSOR                  │
     │  RandomForest         │      │  Linear / ElasticNet        │
     │  (mf=sqrt, msl=20,    │      │  (alpha=0.01, l1_ratio=0.1) │
     │   max_depth=8, 500tr) │      │                             │
     │  → orders the stocks  │      │  → predicted return → size  │
     └──────────┬────────────┘      └───────────────┬─────────────┘
                │                                   │
                ▼                                   ▼
        top-1 / top-k pick   ───────────▶   position size (conservative)
                │
                ▼
     Feature 3-b sleeve policy (1 stock/day, 5 weekday sleeves)
     + risk overlay (size down in high-vol / negative-live-IC regimes)

     Classifier head: DISABLED (AUC ≈ 0.51, no skill) — revisit after label rework
     Deep models (FT/TabM/LSTM): SHELVED — screen cheaply before any future promotion
     LightGBM/XGBoost ranking objective: EXCLUDED (collapses); HistGB fills the GB niche
```

**Concretely, after this experiment the pipeline should:**

1. **Adopt RandomForest as the ranker and Linear/ElasticNet as the regressor**, with the
   exact tuned configs in Appendix B.
2. **Keep HistGB as a fast, NaN-native back-up / ensemble member** (strong #3 ranker, #1
   classifier, trains in <1 h).
3. **Disable the classifier head** as a trade gate until its label/inputs are reworked.
4. **Freeze the losers out of the routine sweep** (LightGBM/XGBoost ranking objectives;
   FT-Transformer/TabM/LSTM) to save days of compute per cycle.
5. **Cap risk:** conservative sizing, top-k (not top-1) holding, and a regime/turnover
   overlay — the gate is unmet, so reliability must come from portfolio construction.

---

## 10. Improvement roadmap

**A. Lift the signal (highest leverage — this is the real bottleneck).**
1. **More breadth.** 30 → 123 names already lifted ICIR ~0.078 → ~0.123. Push toward the
   full S&P 500 (curated in `config/sp500_tickers.yaml`). `IR ≈ IC·√breadth`: ~4× the names
   ≈ ~2× the IR for the same per-stock skill. Single highest-ROI change.
2. **Better features, not bigger models.** The ceiling is the features (deep nets couldn't
   beat a random forest). Add orthogonal signal: fundamentals momentum/estimate revisions,
   analyst-revision deltas, and especially **cross-sectional neutralisation** (sector-demean,
   de-trend) so the model learns *relative* edges.
3. **Ensemble the survivors.** RandomForest + Linear + HistGB are decorrelated pointwise
   models each clearing ~0.02 RankIC. A simple rank-average usually raises ICIR more than
   any single model — cheap and robust. Do this before any more deep-learning compute.
4. **Rework the classifier label** (e.g. wider dead-band: "clearly up" vs "clearly down",
   drop the mushy middle) — AUC 0.51 says the current target is too noisy.

**B. Improve investment reliability (turn a thin edge into a survivable strategy).**
5. **Diversify the daily bet** (top-3/top-5 instead of top-1) — keeps most of the edge,
   cuts variance; likely lifts realised Sharpe more than any model tweak.
6. **Model costs explicitly** — a daily-rotating top-1 has high turnover; add a hold-band so
   the model only trades when the new pick clearly beats the held one.
7. **Regime/risk overlay** — scale down or sit out when volatility is high or recent *live*
   IC turns negative.
8. **Walk-forward live tracking** — paper-trade RF+Linear for 3–6 months; confirm live
   RankIC matches the ~0.026 backtest before scaling.

**C. Pipeline efficiency.**
9. **Stop over-paying for deep models:** (a) set `train_only_selected_role: true` on the
   FT/TabM/LSTM configs (they currently train all 3 heads — ~3× waste); (b) **screen deep
   models on a cheap 2-fold walk-forward first**, promote to full CPCV only if they beat the
   RF baseline. Given these results, deep models can be deprioritised entirely for now.

---

## 11. Issues encountered & fixes (engineering log)

1. **`sklearn_gb` crashed on all 3 roles** — classic `GradientBoosting` rejects NaN, and
   96 % of rows have ≥1 NaN. **Fix:** swapped to **`HistGradientBoosting`** (NaN-native,
   ~10–100× faster). HistGB then ran in <1 h/role and became a top-3 ranker / top classifier.
2. **Hyperparameter "kwarg leak"** — non-swept roles inherited LightGBM-shaped defaults
   (e.g. `num_leaves`) that other estimators reject. **Fix:** `_filter_params()` filters
   kwargs to each estimator's constructor signature.
3. **LightGBM/XGBoost ranker collapse** — diagnosed as **ranking-objective overfitting, not
   a bug** (proved via a 2023+ holdout: RF 0.018 vs LightGBM 0.001 vs ElasticNet ~0.000, and
   HistGB — same boosting family, pointwise loss — ranks fine). See §6.3.
4. **Group A multi-day runtime** — RandomForest = ~75 % of the ~53 h (500 deep trees ×
   CPCV). **Fix:** `train_only_selected_role` (~3× lossless) + HistGB for GB; the slow
   `max_depth=None` RF cells lost to shallow ones anyway.
5. **GPU telemetry honesty** — utilisation sampler under-reported; `ran_on_gpu` now derived
   from VRAM. Side-effect: over-reports for CPU-only sklearn families (see §5.8 caveat).

---

## 12. Data provenance & cross-check

Every figure in §6–§7 was extracted directly from the per-sweep
`reports/experiments/<timestamp>/tuning_report.json` (the `metrics.primary` and
`metrics.secondary` blocks of the best-scoring variant per role), not copied from prior
prose notes. The earlier notes carried a few rounding differences now corrected here:

| Metric | Earlier note | JSON-verified (this report) |
|---|---|---|
| LightGBM ranker, best RankIC | 0.0026 | **0.0028** (0.0026 was the σ-adjusted *recommended* config) |
| CatBoost classifier, best AUC | 0.5087 | **0.5089** |
| LightGBM classifier, best AUC | 0.5061 | **0.5065** |
| HistGB regressor, best IC | 0.0233 | **0.0234** |

These differences arise because some prose tables reported the **σ-adjusted recommended**
config while the matrix here reports the **best raw configuration achieved** per family
(clearly the fairer "what is this model's ceiling" comparison). Recommended vs best-raw
configs are both shown per sweep in Appendix A.

The full sweep index (timestamp → family/role) is in Appendix C.

---

## 13. Runbook for future experiment campaigns (audience: AI agent)

Release 6+ will re-run this kind of campaign with more model families, more
features, and possibly new data pipelines. This section is everything a future
agent needs to (a) trust and reuse the release-5 numbers, (b) re-run the
release-5 protocol exactly, and (c) extend it without breaking comparability.

### 13.1 Where the raw evidence lives

`reports/experiments/Rel5_Experiment/` — **committed to git** (the one
exception carved out of the `reports/` gitignore; the negation block must stay
at the END of `.gitignore`):

```
Rel5_Experiment/
  Initial_Finetune_Experiement/
    reports/<timestamp>/     # all 25 Group-A/B sweeps (index: Appendix C)
    reports/tuned_winners.md # cross-model roll-up
    logs/pipeline_*.log      # full console logs of every sweep
  Winners_Model_Experiment/
    2026-07-01_21-51-01/     # production-combined validation run (§9 protocol)
    logs/
```

Each `<timestamp>/` dir is self-describing: `experiments_used.yaml` (verbatim
input config), `run_meta.json` (resolved per-variant hyperparameters incl.
injected seeds + library versions), `leaderboard.{csv,md}`,
`tuning_report.{md,json}` (the §3c.9 record this document is built from), and
`gpu_telemetry.csv`. **If the archive is lost, the key numbers survive in §6
(cross-model matrix), Appendix A (every variant), and §13.2 (winner configs).**

### 13.2 The winning configuration per family (the §5.6-recommended config)

These are the configs the selection rule *recommends* (best σ-adjusted, with
keep-default-within-1σ applied) — the fair starting point if a family is ever
revived. The production trio is in Appendix B; full grids in Appendix A.

| Family | Ranker | Classifier | Regressor |
|---|---|---|---|
| LightGBM | `num_leaves 15, min_data_in_leaf 20, lr 0.1` | `nl 31, mdil 20, lr 0.05` | `nl 31, mdil 20, lr 0.05` |
| XGBoost | `max_depth 6, lr 0.1, min_child_weight 20` | `md 6, lr 0.05, mcw 20` | `md 6, lr 0.05, mcw 20` |
| CatBoost | `depth 6, lr 0.05, l2_leaf_reg 3` | same | same |
| HistGB | `max_depth 3, lr 0.05, max_leaf_nodes 31` (+300 iter, msl 20, mf 0.9) | `md 5, lr 0.1, mln 31` | `md 3, lr 0.05, mln 31` |
| **RandomForest** | **`max_features sqrt, min_samples_leaf 20, max_depth 8` (500 trees)** | `mf 0.5, msl 20, md None` | `mf sqrt, msl 20, md 8` |
| **Linear** | `alpha 0.001, l1_ratio 0.5` | `C 1.0` | **`alpha 0.01, l1_ratio 0.1`** |
| FT-Transformer | `d_token 64, n_layers 3` (heads 8, ff 2, drop 0.1, lr 1e-3, wd 1e-5) | same | same |
| TabM | `k_models 32, hidden 128` (the one genuine >1σ tuning win) | `km 8, hidden 256` | `km 8, hidden 256` |
| LSTM | `lookback 60, hidden 64` (ranker-only) | — | — |

Bold = the production picks (wired into `config/settings.yaml`
`models.backend`/`hyperparameters`). Remember §5.6: *recommended* is sometimes
the simpler default rather than the raw best — Appendix A marks both.

### 13.3 Code map — the machinery that ran this campaign

| Module | Role |
|---|---|
| `pipeline/ohlcv/experiments/run_feature3c.py` | orchestrator: `--group A\|B\|prod` runs the `config/tuning/*.yaml` sweeps in sequence + roll-up |
| `pipeline/ohlcv/experiments/experiment_runner.py` | one sweep: panel→labels→per-variant train/score→report; walk-forward AND CPCV branches; per-variant seeds; `train_only_selected_role` |
| `pipeline/ohlcv/experiments/cpcv.py` | pure CPCV math: splits, purge/embargo, path reconstruction |
| `pipeline/ohlcv/experiments/grid_gen.py` | compact spec → sweep YAMLs (`grid`/`random(N)`) — regenerate, don't hand-edit |
| `pipeline/ohlcv/experiments/tuning_report.py` | §3c.9 tuning_report.{md,json}; `select_winner` (gate→σ-penalty→keep-default); `rollup_tuned_winners` |
| `pipeline/ohlcv/models/model_factory.py` | backend registry; per-role backend mapping (mixed bundles) |
| `pipeline/ohlcv/models/bundle_factory.py` + `model_bundle.py` | paradigm layer: separate/multihead/quantile/stacked/sequence — all emit `rank_score/pred_return/prob_up` |
| `pipeline/ohlcv/eval/prediction_metrics.py` | RankIC/IC/ICIR/NDCG@K/AUC/Brier — the metric definitions the rel5 numbers use |
| `config/tuning/*.yaml` | the 25 sweep definitions + `production_combined.yaml` |
| `config/experiments.yaml` | full hyperparameter reference block for every backend |

### 13.4 Reproduce release-5 exactly

```bash
# data: 123-ticker panel (config/settings.yaml pipeline.tickers), built by
#   python -m pipeline.main_pipeline --mode fundamental   (ETL + panel)
python -m pipeline.ohlcv.experiments.run_feature3c --group A     # ~2 days CPU
python -m pipeline.ohlcv.experiments.run_feature3c --group B     # ~1.5 days, GPU box
python -m pipeline.ohlcv.experiments.run_feature3c --group prod  # ~1 h
```

Determinism: seeds are `experiment.seed + variant_index`, injected with the
correct per-backend key (`seed`/`random_state`/`random_seed`); library
versions recorded in each `run_meta.json`. The 07-02 rerun reproduced the
07-01 single-split metrics byte-for-byte.

### 13.5 How to extend for a bigger campaign (new models / features / pipelines)

1. **New model family** = subclass `BaseModel` (`train/predict/predict_proba/
   feature_importance`; NaN handling mandatory — the panel is 96 % NaN-rows),
   register it lazily in `model_factory._register_backends()`, add its seed key
   to `experiment_runner._SEED_KEY`, write a compact grid spec through
   `grid_gen` (sweep only the 2-4 knobs that matter — Probst 2019), and give it
   a `config/tuning/<family>_<role>.yaml` per role. Deep models: keep torch
   imports lazy; set `train_only_selected_role: true` in role sweeps (~3×).
2. **New features** = extend `feature_schema.py` (new group, added to
   `ALL_FEATURES` or a new named set), rebuild the panel, point the sweep YAMLs'
   `features:` at the new set. The runner loads the panel ONCE per sweep so
   every variant sees identical data — keep it that way.
3. **New pipeline/data source** (beyond ohlcv+fundamentals) = merge new columns
   into `combined_features_for_fundamental_training.parquet` point-in-time
   (merge_asof on the real period-end — never calendar joins), then (2).
4. **Keep these invariants or the rel5 numbers stop being comparable:**
   CPCV N=6/k=2, embargo 5d, label horizon 1w; the §5.6 selection rule
   (gate RankICIR≥0.30, σ-penalty 0.5, keep-default-within-1σ); the §5.7
   metric definitions; a declared `default_variant` per sweep; frozen
   selector coefficients during sweeps. If any of these change, re-run at
   least RandomForest + Linear as bridges so old and new campaigns share
   anchor points.
5. **The reference numbers to beat** (123-name universe, CPCV): ranker RankIC
   **0.0257** / ICIR **0.123** (RandomForest); regressor IC **0.0342** (Linear);
   gate 0.30 unmet by everything. Walk-forward FULL Sharpe **0.871**
   (production combined, 2018→2026). A new campaign that can't beat these on
   the same protocol should keep the rel5 production stack.
6. **Read first:** §5 (methodology), §6.3 (why ranking losses and deep nets
   lost here — don't re-spend GPU-days rediscovering it), §10 (the improvement
   roadmap this was pointing at), and `rel5_document.md` Appendix D.4 (the
   never-built meta-label validator).

---

# Appendix A — Full per-variant performance records

Every configuration evaluated, one subsection per *sweep* (recall: a sweep = the tuning
run for one family in one role, §5.6 selecting its winner), sorted best→worst on the
role's primary metric. `**(rec)**` = the config the §5.6 selection rule recommends (kept-default or tuned);
`*(best)*` = the raw best when it differs from the recommendation. `RankICIR` is shown for
all roles (it is the gate metric; for HistGB's off-primary heads it reads 0 because only the
swept head was trained — see §5.8).

<!-- BEGIN APPENDIX TABLES -->
### LightGBM

**ranker** — sweep `2026-06-24_06-22-59` · metric `pred_rank_ic_mean` · 27/27 OK · 1.17 h
· selected/recommended: `lgbm_rk__nl15_mdil20_lr01` (best σ-adj: `lgbm_rk__nl15_mdil20_lr01`); >1σ over default: True

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `lgbm_rk__nl63_mdil50_lr002` | 0.0028 | 0.0014 | 0.0138 |
| `lgbm_rk__nl15_mdil100_lr005` | 0.0028 | 0.0013 | 0.0131 |
| `lgbm_rk__nl63_mdil100_lr01` | 0.0027 | 0.0016 | 0.0134 |
| `lgbm_rk__nl31_mdil20_lr01` | 0.0027 | 0.0016 | 0.0129 |
| `lgbm_rk__nl31_mdil100_lr005` | 0.0027 | 0.0014 | 0.0126 |
| `lgbm_rk__nl15_mdil100_lr01` | 0.0026 | 0.0013 | 0.0124 |
| `lgbm_rk__nl31_mdil50_lr005` | 0.0026 | 0.0009 | 0.0122 |
| `lgbm_rk__nl15_mdil20_lr01` **(rec)** | 0.0026 | 0.0005 | 0.0121 |
| `lgbm_rk__nl15_mdil100_lr002` | 0.0025 | 0.0009 | 0.0115 |
| `lgbm_rk__nl63_mdil20_lr005` | 0.0024 | 0.0014 | 0.0117 |
| `lgbm_rk__nl63_mdil20_lr002` | 0.0023 | 0.0032 | 0.0116 |
| `lgbm_rk__nl15_mdil50_lr005` | 0.0022 | 0.0007 | 0.0104 |
| `lgbm_rk__nl15_mdil50_lr01` | 0.0022 | 0.0009 | 0.0105 |
| `lgbm_rk__nl63_mdil20_lr01` | 0.0022 | 0.0012 | 0.0108 |
| `lgbm_rk__nl15_mdil50_lr002` | 0.0022 | 0.0007 | 0.0102 |
| `lgbm_rk__nl63_mdil50_lr005` | 0.0022 | 0.0014 | 0.0107 |
| `lgbm_rk__nl15_mdil20_lr005` | 0.0021 | 0.0012 | 0.0099 |
| `lgbm_rk__nl15_mdil20_lr002` | 0.0020 | 0.0008 | 0.0094 |
| `lgbm_rk__nl31_mdil100_lr01` | 0.0020 | 0.0008 | 0.0094 |
| `lgbm_rk__nl31_mdil100_lr002` | 0.0018 | 0.0016 | 0.0087 |
| `lgbm_rk__nl31_mdil50_lr002` | 0.0018 | 0.0014 | 0.0086 |
| `lgbm_rk__nl63_mdil50_lr01` | 0.0018 | 0.0006 | 0.0088 |
| `lgbm_rk__nl63_mdil100_lr002` | 0.0017 | 0.0015 | 0.0087 |
| `lgbm_rk__nl63_mdil100_lr005` | 0.0017 | 0.0015 | 0.0084 |
| `lgbm_rk__nl31_mdil50_lr01` | 0.0016 | 0.0015 | 0.0076 |
| `lgbm_rk__nl31_mdil20_lr005` | 0.0014 | 0.0012 | 0.0068 |
| `lgbm_rk__nl31_mdil20_lr002` | 0.0014 | 0.0016 | 0.0068 |

**classifier** — sweep `2026-06-24_07-32-58` · metric `pred_auc` · 27/27 OK · 1.16 h
· selected/recommended: `lgbm_cls__nl31_mdil20_lr005` (best σ-adj: `lgbm_cls__nl63_mdil20_lr005`); >1σ over default: False

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `lgbm_cls__nl63_mdil100_lr002` | 0.5065 | 0.0033 | 0.0078 |
| `lgbm_cls__nl63_mdil20_lr005` *(best)* | 0.5061 | 0.0024 | 0.0058 |
| `lgbm_cls__nl15_mdil50_lr005` | 0.5061 | 0.0028 | 0.0082 |
| `lgbm_cls__nl31_mdil100_lr01` | 0.5060 | 0.0040 | 0.0113 |
| `lgbm_cls__nl63_mdil50_lr002` | 0.5060 | 0.0041 | 0.0029 |
| `lgbm_cls__nl63_mdil20_lr002` | 0.5060 | 0.0046 | 0.0068 |
| `lgbm_cls__nl31_mdil20_lr002` | 0.5058 | 0.0032 | 0.0070 |
| `lgbm_cls__nl15_mdil20_lr002` | 0.5057 | 0.0021 | 0.0095 |
| `lgbm_cls__nl15_mdil20_lr005` | 0.5055 | 0.0031 | 0.0095 |
| `lgbm_cls__nl31_mdil50_lr005` | 0.5055 | 0.0035 | 0.0103 |
| `lgbm_cls__nl31_mdil100_lr002` | 0.5052 | 0.0040 | 0.0075 |
| `lgbm_cls__nl31_mdil50_lr002` | 0.5051 | 0.0038 | 0.0079 |
| `lgbm_cls__nl63_mdil20_lr01` | 0.5049 | 0.0046 | 0.0100 |
| `lgbm_cls__nl31_mdil20_lr01` | 0.5046 | 0.0046 | 0.0061 |
| `lgbm_cls__nl31_mdil20_lr005` **(rec)** | 0.5046 | 0.0031 | 0.0068 |
| `lgbm_cls__nl15_mdil100_lr005` | 0.5044 | 0.0032 | 0.0047 |
| `lgbm_cls__nl31_mdil100_lr005` | 0.5044 | 0.0025 | 0.0100 |
| `lgbm_cls__nl15_mdil100_lr002` | 0.5044 | 0.0013 | 0.0081 |
| `lgbm_cls__nl63_mdil100_lr005` | 0.5042 | 0.0036 | 0.0083 |
| `lgbm_cls__nl63_mdil100_lr01` | 0.5042 | 0.0043 | 0.0064 |
| `lgbm_cls__nl15_mdil20_lr01` | 0.5040 | 0.0016 | 0.0076 |
| `lgbm_cls__nl63_mdil50_lr005` | 0.5038 | 0.0046 | 0.0058 |
| `lgbm_cls__nl15_mdil50_lr01` | 0.5035 | 0.0042 | 0.0092 |
| `lgbm_cls__nl15_mdil100_lr01` | 0.5034 | 0.0033 | 0.0100 |
| `lgbm_cls__nl15_mdil50_lr002` | 0.5033 | 0.0019 | 0.0047 |
| `lgbm_cls__nl31_mdil50_lr01` | 0.5028 | 0.0017 | 0.0067 |
| `lgbm_cls__nl63_mdil50_lr01` | 0.5023 | 0.0030 | 0.0053 |

**regressor** — sweep `2026-06-24_08-42-41` · metric `pred_reg_ic_mean` · 27/27 OK · 1.16 h
· selected/recommended: `lgbm_reg__nl31_mdil20_lr005` (best σ-adj: `lgbm_reg__nl63_mdil20_lr01`); >1σ over default: False

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `lgbm_reg__nl63_mdil20_lr01` *(best)* | 0.0131 | 0.0044 | 0.0100 |
| `lgbm_reg__nl15_mdil100_lr002` | 0.0115 | 0.0065 | 0.0081 |
| `lgbm_reg__nl31_mdil100_lr002` | 0.0107 | 0.0043 | 0.0075 |
| `lgbm_reg__nl63_mdil50_lr002` | 0.0103 | 0.0041 | 0.0029 |
| `lgbm_reg__nl63_mdil20_lr005` | 0.0100 | 0.0039 | 0.0058 |
| `lgbm_reg__nl31_mdil50_lr002` | 0.0095 | 0.0043 | 0.0079 |
| `lgbm_reg__nl63_mdil50_lr005` | 0.0094 | 0.0036 | 0.0058 |
| `lgbm_reg__nl15_mdil100_lr005` | 0.0094 | 0.0058 | 0.0047 |
| `lgbm_reg__nl63_mdil20_lr002` | 0.0092 | 0.0027 | 0.0068 |
| `lgbm_reg__nl31_mdil100_lr005` | 0.0091 | 0.0045 | 0.0100 |
| `lgbm_reg__nl63_mdil100_lr002` | 0.0090 | 0.0048 | 0.0078 |
| `lgbm_reg__nl31_mdil20_lr005` **(rec)** | 0.0089 | 0.0038 | 0.0068 |
| `lgbm_reg__nl15_mdil50_lr01` | 0.0088 | 0.0044 | 0.0092 |
| `lgbm_reg__nl15_mdil50_lr002` | 0.0087 | 0.0071 | 0.0047 |
| `lgbm_reg__nl63_mdil100_lr01` | 0.0087 | 0.0044 | 0.0064 |
| `lgbm_reg__nl15_mdil50_lr005` | 0.0086 | 0.0060 | 0.0082 |
| `lgbm_reg__nl31_mdil20_lr002` | 0.0082 | 0.0045 | 0.0070 |
| `lgbm_reg__nl15_mdil20_lr01` | 0.0081 | 0.0040 | 0.0076 |
| `lgbm_reg__nl15_mdil20_lr005` | 0.0076 | 0.0023 | 0.0095 |
| `lgbm_reg__nl31_mdil100_lr01` | 0.0076 | 0.0036 | 0.0113 |
| `lgbm_reg__nl63_mdil100_lr005` | 0.0074 | 0.0052 | 0.0083 |
| `lgbm_reg__nl63_mdil50_lr01` | 0.0073 | 0.0049 | 0.0053 |
| `lgbm_reg__nl31_mdil50_lr01` | 0.0069 | 0.0052 | 0.0067 |
| `lgbm_reg__nl15_mdil20_lr002` | 0.0068 | 0.0066 | 0.0095 |
| `lgbm_reg__nl31_mdil20_lr01` | 0.0066 | 0.0058 | 0.0061 |
| `lgbm_reg__nl31_mdil50_lr005` | 0.0066 | 0.0044 | 0.0103 |
| `lgbm_reg__nl15_mdil100_lr01` | 0.0065 | 0.0078 | 0.0100 |


### XGBoost

**ranker** — sweep `2026-06-24_09-52-12` · metric `pred_rank_ic_mean` · 27/27 OK · 1.97 h
· selected/recommended: `xgb_rk__md6_lr01_mcw20` (best σ-adj: `xgb_rk__md6_lr01_mcw20`); >1σ over default: True

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `xgb_rk__md6_lr01_mcw20` **(rec)** | 0.0042 | 0.0007 | 0.0209 |
| `xgb_rk__md9_lr005_mcw20` | 0.0042 | 0.0011 | 0.0214 |
| `xgb_rk__md9_lr01_mcw1` | 0.0041 | 0.0014 | 0.0218 |
| `xgb_rk__md9_lr002_mcw20` | 0.0039 | 0.0024 | 0.0202 |
| `xgb_rk__md9_lr01_mcw50` | 0.0038 | 0.0011 | 0.0199 |
| `xgb_rk__md9_lr01_mcw20` | 0.0038 | 0.0012 | 0.0201 |
| `xgb_rk__md9_lr002_mcw1` | 0.0035 | 0.0010 | 0.0179 |
| `xgb_rk__md9_lr002_mcw50` | 0.0034 | 0.0018 | 0.0173 |
| `xgb_rk__md6_lr002_mcw20` | 0.0033 | 0.0008 | 0.0160 |
| `xgb_rk__md9_lr005_mcw50` | 0.0031 | 0.0010 | 0.0159 |
| `xgb_rk__md9_lr005_mcw1` | 0.0031 | 0.0019 | 0.0161 |
| `xgb_rk__md6_lr005_mcw1` | 0.0030 | 0.0022 | 0.0147 |
| `xgb_rk__md6_lr01_mcw1` | 0.0030 | 0.0008 | 0.0148 |
| `xgb_rk__md6_lr002_mcw50` | 0.0029 | 0.0012 | 0.0139 |
| `xgb_rk__md6_lr01_mcw50` | 0.0026 | 0.0008 | 0.0128 |
| `xgb_rk__md6_lr005_mcw20` | 0.0026 | 0.0018 | 0.0125 |
| `xgb_rk__md6_lr002_mcw1` | 0.0025 | 0.0013 | 0.0123 |
| `xgb_rk__md6_lr005_mcw50` | 0.0024 | 0.0020 | 0.0115 |
| `xgb_rk__md3_lr002_mcw20` | 0.0023 | 0.0010 | 0.0104 |
| `xgb_rk__md3_lr005_mcw20` | 0.0022 | 0.0008 | 0.0103 |
| `xgb_rk__md3_lr002_mcw50` | 0.0021 | 0.0005 | 0.0094 |
| `xgb_rk__md3_lr01_mcw1` | 0.0019 | 0.0010 | 0.0090 |
| `xgb_rk__md3_lr002_mcw1` | 0.0019 | 0.0008 | 0.0089 |
| `xgb_rk__md3_lr005_mcw50` | 0.0019 | 0.0008 | 0.0086 |
| `xgb_rk__md3_lr01_mcw20` | 0.0019 | 0.0015 | 0.0086 |
| `xgb_rk__md3_lr005_mcw1` | 0.0019 | 0.0006 | 0.0086 |
| `xgb_rk__md3_lr01_mcw50` | 0.0014 | 0.0012 | 0.0063 |

**classifier** — sweep `2026-06-24_11-50-18` · metric `pred_auc` · 27/27 OK · 1.75 h
· selected/recommended: `xgb_cls__md6_lr005_mcw20` (best σ-adj: `xgb_cls__md9_lr01_mcw50`); >1σ over default: False

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `xgb_cls__md9_lr01_mcw50` *(best)* | 0.5148 | 0.0026 | 0.0148 |
| `xgb_cls__md9_lr01_mcw20` | 0.5143 | 0.0022 | 0.0122 |
| `xgb_cls__md6_lr01_mcw20` | 0.5141 | 0.0021 | 0.0170 |
| `xgb_cls__md6_lr01_mcw1` | 0.5141 | 0.0022 | 0.0099 |
| `xgb_cls__md6_lr01_mcw50` | 0.5139 | 0.0025 | 0.0154 |
| `xgb_cls__md9_lr005_mcw50` | 0.5138 | 0.0024 | 0.0103 |
| `xgb_cls__md9_lr005_mcw20` | 0.5138 | 0.0026 | 0.0164 |
| `xgb_cls__md9_lr01_mcw1` | 0.5138 | 0.0023 | 0.0151 |
| `xgb_cls__md9_lr002_mcw20` | 0.5130 | 0.0039 | 0.0123 |
| `xgb_cls__md6_lr005_mcw50` | 0.5129 | 0.0032 | 0.0120 |
| `xgb_cls__md6_lr005_mcw20` **(rec)** | 0.5127 | 0.0034 | 0.0125 |
| `xgb_cls__md9_lr005_mcw1` | 0.5125 | 0.0026 | 0.0169 |
| `xgb_cls__md9_lr002_mcw1` | 0.5124 | 0.0034 | 0.0120 |
| `xgb_cls__md6_lr005_mcw1` | 0.5123 | 0.0030 | 0.0142 |
| `xgb_cls__md9_lr002_mcw50` | 0.5123 | 0.0035 | 0.0147 |
| `xgb_cls__md3_lr01_mcw50` | 0.5114 | 0.0036 | 0.0081 |
| `xgb_cls__md6_lr002_mcw20` | 0.5112 | 0.0038 | 0.0146 |
| `xgb_cls__md3_lr01_mcw20` | 0.5111 | 0.0034 | 0.0132 |
| `xgb_cls__md3_lr01_mcw1` | 0.5107 | 0.0038 | 0.0066 |
| `xgb_cls__md6_lr002_mcw1` | 0.5104 | 0.0038 | 0.0117 |
| `xgb_cls__md6_lr002_mcw50` | 0.5103 | 0.0032 | 0.0191 |
| `xgb_cls__md3_lr005_mcw50` | 0.5096 | 0.0038 | 0.0180 |
| `xgb_cls__md3_lr005_mcw20` | 0.5095 | 0.0038 | 0.0158 |
| `xgb_cls__md3_lr005_mcw1` | 0.5091 | 0.0036 | 0.0126 |
| `xgb_cls__md3_lr002_mcw50` | 0.5079 | 0.0038 | 0.0155 |
| `xgb_cls__md3_lr002_mcw20` | 0.5076 | 0.0039 | 0.0125 |
| `xgb_cls__md3_lr002_mcw1` | 0.5074 | 0.0045 | 0.0172 |

**regressor** — sweep `2026-06-24_13-35-15` · metric `pred_reg_ic_mean` · 27/27 OK · 1.74 h
· selected/recommended: `xgb_reg__md6_lr005_mcw20` (best σ-adj: `xgb_reg__md3_lr005_mcw50`); >1σ over default: False

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `xgb_reg__md3_lr005_mcw50` *(best)* | 0.0158 | 0.0057 | 0.0180 |
| `xgb_reg__md3_lr01_mcw1` | 0.0155 | 0.0058 | 0.0066 |
| `xgb_reg__md3_lr01_mcw50` | 0.0155 | 0.0058 | 0.0081 |
| `xgb_reg__md3_lr01_mcw20` | 0.0149 | 0.0054 | 0.0132 |
| `xgb_reg__md3_lr005_mcw20` | 0.0147 | 0.0053 | 0.0158 |
| `xgb_reg__md6_lr002_mcw50` | 0.0145 | 0.0055 | 0.0191 |
| `xgb_reg__md9_lr005_mcw1` | 0.0145 | 0.0044 | 0.0169 |
| `xgb_reg__md3_lr005_mcw1` | 0.0145 | 0.0052 | 0.0126 |
| `xgb_reg__md6_lr005_mcw20` **(rec)** | 0.0144 | 0.0048 | 0.0125 |
| `xgb_reg__md6_lr002_mcw1` | 0.0137 | 0.0035 | 0.0117 |
| `xgb_reg__md6_lr005_mcw50` | 0.0137 | 0.0033 | 0.0120 |
| `xgb_reg__md3_lr002_mcw20` | 0.0131 | 0.0047 | 0.0125 |
| `xgb_reg__md3_lr002_mcw50` | 0.0130 | 0.0048 | 0.0155 |
| `xgb_reg__md6_lr005_mcw1` | 0.0130 | 0.0055 | 0.0142 |
| `xgb_reg__md9_lr002_mcw20` | 0.0129 | 0.0059 | 0.0123 |
| `xgb_reg__md9_lr002_mcw50` | 0.0128 | 0.0058 | 0.0147 |
| `xgb_reg__md6_lr002_mcw20` | 0.0128 | 0.0051 | 0.0146 |
| `xgb_reg__md9_lr005_mcw20` | 0.0124 | 0.0039 | 0.0164 |
| `xgb_reg__md9_lr01_mcw20` | 0.0122 | 0.0066 | 0.0122 |
| `xgb_reg__md3_lr002_mcw1` | 0.0121 | 0.0048 | 0.0172 |
| `xgb_reg__md9_lr005_mcw50` | 0.0118 | 0.0057 | 0.0103 |
| `xgb_reg__md9_lr002_mcw1` | 0.0117 | 0.0045 | 0.0120 |
| `xgb_reg__md6_lr01_mcw50` | 0.0117 | 0.0039 | 0.0154 |
| `xgb_reg__md6_lr01_mcw1` | 0.0109 | 0.0047 | 0.0099 |
| `xgb_reg__md6_lr01_mcw20` | 0.0106 | 0.0046 | 0.0170 |
| `xgb_reg__md9_lr01_mcw50` | 0.0104 | 0.0068 | 0.0148 |
| `xgb_reg__md9_lr01_mcw1` | 0.0101 | 0.0041 | 0.0151 |


### CatBoost

**ranker** — sweep `2026-06-24_15-19-50` · metric `pred_rank_ic_mean` · 27/27 OK · 1.37 h
· selected/recommended: `cat_rk__dept6_lr005_llr3` (best σ-adj: `cat_rk__dept4_lr005_llr3`); >1σ over default: False

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `cat_rk__dept4_lr005_llr3` *(best)* | 0.0192 | 0.0076 | 0.0969 |
| `cat_rk__dept4_lr01_llr10` | 0.0189 | 0.0072 | 0.0954 |
| `cat_rk__dept4_lr01_llr3` | 0.0186 | 0.0069 | 0.0967 |
| `cat_rk__dept4_lr002_llr3` | 0.0183 | 0.0097 | 0.0912 |
| `cat_rk__dept4_lr01_llr1` | 0.0181 | 0.0070 | 0.0950 |
| `cat_rk__dept4_lr002_llr10` | 0.0178 | 0.0090 | 0.0908 |
| `cat_rk__dept6_lr005_llr3` **(rec)** | 0.0178 | 0.0086 | 0.0929 |
| `cat_rk__dept6_lr005_llr10` | 0.0177 | 0.0076 | 0.0914 |
| `cat_rk__dept6_lr002_llr10` | 0.0176 | 0.0105 | 0.0882 |
| `cat_rk__dept4_lr005_llr10` | 0.0175 | 0.0097 | 0.0881 |
| `cat_rk__dept6_lr005_llr1` | 0.0175 | 0.0072 | 0.0925 |
| `cat_rk__dept8_lr005_llr10` | 0.0174 | 0.0070 | 0.0985 |
| `cat_rk__dept4_lr005_llr1` | 0.0174 | 0.0080 | 0.0884 |
| `cat_rk__dept6_lr002_llr1` | 0.0172 | 0.0090 | 0.0894 |
| `cat_rk__dept6_lr01_llr3` | 0.0171 | 0.0084 | 0.0921 |
| `cat_rk__dept8_lr002_llr10` | 0.0171 | 0.0098 | 0.0946 |
| `cat_rk__dept6_lr01_llr10` | 0.0171 | 0.0094 | 0.0928 |
| `cat_rk__dept4_lr002_llr1` | 0.0168 | 0.0085 | 0.0865 |
| `cat_rk__dept8_lr005_llr1` | 0.0166 | 0.0066 | 0.0928 |
| `cat_rk__dept6_lr01_llr1` | 0.0160 | 0.0087 | 0.0873 |
| `cat_rk__dept8_lr01_llr3` | 0.0159 | 0.0082 | 0.0941 |
| `cat_rk__dept8_lr01_llr10` | 0.0156 | 0.0067 | 0.0863 |
| `cat_rk__dept6_lr002_llr3` | 0.0155 | 0.0080 | 0.0814 |
| `cat_rk__dept8_lr01_llr1` | 0.0152 | 0.0062 | 0.0909 |
| `cat_rk__dept8_lr002_llr3` | 0.0149 | 0.0078 | 0.0821 |
| `cat_rk__dept8_lr002_llr1` | 0.0133 | 0.0098 | 0.0751 |
| `cat_rk__dept8_lr005_llr3` | 0.0128 | 0.0048 | 0.0761 |

**classifier** — sweep `2026-06-24_16-41-57` · metric `pred_auc` · 27/27 OK · 1.39 h
· selected/recommended: `cat_cls__dept6_lr005_llr3` (best σ-adj: `cat_cls__dept8_lr01_llr3`); >1σ over default: False

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `cat_cls__dept8_lr002_llr3` | 0.5089 | 0.0022 | 0.0796 |
| `cat_cls__dept8_lr002_llr10` | 0.5089 | 0.0025 | 0.0977 |
| `cat_cls__dept8_lr01_llr3` *(best)* | 0.5087 | 0.0014 | 0.0845 |
| `cat_cls__dept8_lr002_llr1` | 0.5087 | 0.0021 | 0.0622 |
| `cat_cls__dept6_lr002_llr10` | 0.5086 | 0.0016 | 0.0887 |
| `cat_cls__dept6_lr005_llr3` **(rec)** | 0.5086 | 0.0015 | 0.0900 |
| `cat_cls__dept4_lr005_llr3` | 0.5084 | 0.0010 | 0.0864 |
| `cat_cls__dept6_lr002_llr3` | 0.5083 | 0.0013 | 0.0872 |
| `cat_cls__dept6_lr002_llr1` | 0.5083 | 0.0016 | 0.0860 |
| `cat_cls__dept8_lr005_llr1` | 0.5080 | 0.0022 | 0.0939 |
| `cat_cls__dept4_lr002_llr1` | 0.5078 | 0.0018 | 0.0926 |
| `cat_cls__dept6_lr005_llr10` | 0.5077 | 0.0028 | 0.0907 |
| `cat_cls__dept4_lr01_llr3` | 0.5074 | 0.0009 | 0.0926 |
| `cat_cls__dept8_lr005_llr3` | 0.5074 | 0.0028 | 0.0967 |
| `cat_cls__dept6_lr005_llr1` | 0.5074 | 0.0024 | 0.0918 |
| `cat_cls__dept8_lr005_llr10` | 0.5072 | 0.0046 | 0.0794 |
| `cat_cls__dept8_lr01_llr10` | 0.5071 | 0.0023 | 0.0809 |
| `cat_cls__dept4_lr002_llr3` | 0.5070 | 0.0034 | 0.0838 |
| `cat_cls__dept6_lr01_llr3` | 0.5068 | 0.0019 | 0.0879 |
| `cat_cls__dept4_lr005_llr1` | 0.5067 | 0.0019 | 0.0938 |
| `cat_cls__dept4_lr01_llr10` | 0.5065 | 0.0034 | 0.0798 |
| `cat_cls__dept4_lr005_llr10` | 0.5064 | 0.0026 | 0.0806 |
| `cat_cls__dept4_lr002_llr10` | 0.5062 | 0.0016 | 0.0875 |
| `cat_cls__dept8_lr01_llr1` | 0.5060 | 0.0022 | 0.0923 |
| `cat_cls__dept6_lr01_llr10` | 0.5056 | 0.0039 | 0.0885 |
| `cat_cls__dept6_lr01_llr1` | 0.5052 | 0.0039 | 0.0819 |
| `cat_cls__dept4_lr01_llr1` | 0.5050 | 0.0014 | 0.0985 |

**regressor** — sweep `2026-06-24_18-05-07` · metric `pred_reg_ic_mean` · 27/27 OK · 1.38 h
· selected/recommended: `cat_reg__dept6_lr005_llr3` (best σ-adj: `cat_reg__dept6_lr005_llr10`); >1σ over default: False

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `cat_reg__dept6_lr005_llr10` *(best)* | 0.0137 | 0.0055 | 0.0907 |
| `cat_reg__dept6_lr002_llr10` | 0.0136 | 0.0070 | 0.0887 |
| `cat_reg__dept6_lr002_llr1` | 0.0119 | 0.0063 | 0.0860 |
| `cat_reg__dept6_lr002_llr3` | 0.0115 | 0.0073 | 0.0872 |
| `cat_reg__dept4_lr005_llr1` | 0.0115 | 0.0063 | 0.0938 |
| `cat_reg__dept4_lr002_llr10` | 0.0114 | 0.0082 | 0.0875 |
| `cat_reg__dept6_lr005_llr3` **(rec)** | 0.0112 | 0.0051 | 0.0900 |
| `cat_reg__dept4_lr005_llr10` | 0.0111 | 0.0082 | 0.0806 |
| `cat_reg__dept8_lr01_llr3` | 0.0111 | 0.0049 | 0.0845 |
| `cat_reg__dept4_lr002_llr3` | 0.0109 | 0.0087 | 0.0838 |
| `cat_reg__dept4_lr005_llr3` | 0.0107 | 0.0053 | 0.0864 |
| `cat_reg__dept8_lr002_llr3` | 0.0107 | 0.0047 | 0.0796 |
| `cat_reg__dept6_lr01_llr1` | 0.0106 | 0.0063 | 0.0819 |
| `cat_reg__dept4_lr01_llr3` | 0.0105 | 0.0088 | 0.0926 |
| `cat_reg__dept8_lr002_llr10` | 0.0104 | 0.0067 | 0.0977 |
| `cat_reg__dept8_lr005_llr1` | 0.0104 | 0.0054 | 0.0939 |
| `cat_reg__dept4_lr002_llr1` | 0.0104 | 0.0073 | 0.0926 |
| `cat_reg__dept6_lr005_llr1` | 0.0104 | 0.0066 | 0.0918 |
| `cat_reg__dept8_lr002_llr1` | 0.0101 | 0.0053 | 0.0622 |
| `cat_reg__dept8_lr005_llr10` | 0.0096 | 0.0033 | 0.0794 |
| `cat_reg__dept4_lr01_llr1` | 0.0096 | 0.0087 | 0.0985 |
| `cat_reg__dept6_lr01_llr3` | 0.0090 | 0.0063 | 0.0879 |
| `cat_reg__dept8_lr01_llr10` | 0.0086 | 0.0059 | 0.0809 |
| `cat_reg__dept6_lr01_llr10` | 0.0083 | 0.0062 | 0.0885 |
| `cat_reg__dept4_lr01_llr10` | 0.0082 | 0.0070 | 0.0798 |
| `cat_reg__dept8_lr005_llr3` | 0.0079 | 0.0046 | 0.0967 |
| `cat_reg__dept8_lr01_llr1` | 0.0071 | 0.0048 | 0.0923 |


### HistGB (sklearn_gb)

**ranker** — sweep `2026-06-26_22-10-59` · metric `pred_rank_ic_mean` · 27/27 OK · 0.86 h
· selected/recommended: `skgb_rk__md3_lr005_mln31` (best σ-adj: `skgb_rk__md3_lr002_mln15`); >1σ over default: False

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `skgb_rk__md3_lr002_mln15` *(best)* | 0.0226 | 0.0053 | 0.1186 |
| `skgb_rk__md2_lr005_mln63` | 0.0222 | 0.0062 | 0.1193 |
| `skgb_rk__md5_lr002_mln15` | 0.0220 | 0.0045 | 0.1209 |
| `skgb_rk__md2_lr005_mln15` | 0.0218 | 0.0060 | 0.1150 |
| `skgb_rk__md5_lr002_mln31` | 0.0217 | 0.0044 | 0.1225 |
| `skgb_rk__md3_lr002_mln63` | 0.0217 | 0.0066 | 0.1146 |
| `skgb_rk__md3_lr005_mln31` **(rec)** | 0.0217 | 0.0047 | 0.1223 |
| `skgb_rk__md2_lr005_mln31` | 0.0216 | 0.0068 | 0.1160 |
| `skgb_rk__md5_lr002_mln63` | 0.0215 | 0.0044 | 0.1213 |
| `skgb_rk__md2_lr01_mln15` | 0.0215 | 0.0072 | 0.1217 |
| `skgb_rk__md3_lr002_mln31` | 0.0211 | 0.0050 | 0.1119 |
| `skgb_rk__md3_lr005_mln15` | 0.0209 | 0.0054 | 0.1185 |
| `skgb_rk__md5_lr01_mln15` | 0.0208 | 0.0030 | 0.1281 |
| `skgb_rk__md2_lr002_mln15` | 0.0205 | 0.0067 | 0.1051 |
| `skgb_rk__md2_lr002_mln63` | 0.0204 | 0.0060 | 0.1048 |
| `skgb_rk__md2_lr01_mln31` | 0.0202 | 0.0054 | 0.1143 |
| `skgb_rk__md5_lr005_mln31` | 0.0202 | 0.0046 | 0.1201 |
| `skgb_rk__md2_lr01_mln63` | 0.0201 | 0.0056 | 0.1143 |
| `skgb_rk__md5_lr005_mln15` | 0.0197 | 0.0031 | 0.1143 |
| `skgb_rk__md3_lr005_mln63` | 0.0196 | 0.0053 | 0.1113 |
| `skgb_rk__md5_lr005_mln63` | 0.0195 | 0.0045 | 0.1145 |
| `skgb_rk__md5_lr01_mln31` | 0.0194 | 0.0033 | 0.1194 |
| `skgb_rk__md2_lr002_mln31` | 0.0193 | 0.0068 | 0.0989 |
| `skgb_rk__md3_lr01_mln15` | 0.0184 | 0.0032 | 0.1106 |
| `skgb_rk__md3_lr01_mln63` | 0.0183 | 0.0037 | 0.1085 |
| `skgb_rk__md3_lr01_mln31` | 0.0176 | 0.0050 | 0.1062 |
| `skgb_rk__md5_lr01_mln63` | 0.0174 | 0.0044 | 0.1060 |

**classifier** — sweep `2026-06-26_23-02-34` · metric `pred_auc` · 27/27 OK · 1.00 h
· selected/recommended: `skgb_cls__md5_lr01_mln31` (best σ-adj: `skgb_cls__md5_lr01_mln31`); >1σ over default: True

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `skgb_cls__md5_lr01_mln31` **(rec)** | 0.5190 | 0.0023 | 0.0000 |
| `skgb_cls__md5_lr01_mln63` | 0.5183 | 0.0021 | 0.0000 |
| `skgb_cls__md3_lr01_mln15` | 0.5181 | 0.0024 | 0.0000 |
| `skgb_cls__md5_lr005_mln31` | 0.5180 | 0.0025 | 0.0000 |
| `skgb_cls__md3_lr01_mln31` | 0.5180 | 0.0028 | 0.0000 |
| `skgb_cls__md5_lr005_mln63` | 0.5179 | 0.0022 | 0.0000 |
| `skgb_cls__md3_lr01_mln63` | 0.5178 | 0.0028 | 0.0000 |
| `skgb_cls__md5_lr005_mln15` | 0.5174 | 0.0025 | 0.0000 |
| `skgb_cls__md5_lr01_mln15` | 0.5174 | 0.0020 | 0.0000 |
| `skgb_cls__md2_lr01_mln31` | 0.5161 | 0.0023 | 0.0000 |
| `skgb_cls__md2_lr01_mln63` | 0.5159 | 0.0016 | 0.0000 |
| `skgb_cls__md5_lr002_mln31` | 0.5159 | 0.0021 | 0.0000 |
| `skgb_cls__md3_lr005_mln15` | 0.5158 | 0.0021 | 0.0000 |
| `skgb_cls__md5_lr002_mln63` | 0.5158 | 0.0023 | 0.0000 |
| `skgb_cls__md3_lr005_mln63` | 0.5156 | 0.0030 | 0.0000 |
| `skgb_cls__md3_lr005_mln31` | 0.5154 | 0.0027 | 0.0000 |
| `skgb_cls__md2_lr01_mln15` | 0.5153 | 0.0026 | 0.0000 |
| `skgb_cls__md5_lr002_mln15` | 0.5150 | 0.0026 | 0.0000 |
| `skgb_cls__md2_lr005_mln15` | 0.5130 | 0.0017 | 0.0000 |
| `skgb_cls__md2_lr005_mln63` | 0.5130 | 0.0018 | 0.0000 |
| `skgb_cls__md2_lr005_mln31` | 0.5127 | 0.0025 | 0.0000 |
| `skgb_cls__md3_lr002_mln15` | 0.5126 | 0.0020 | 0.0000 |
| `skgb_cls__md3_lr002_mln31` | 0.5121 | 0.0021 | 0.0000 |
| `skgb_cls__md3_lr002_mln63` | 0.5121 | 0.0028 | 0.0000 |
| `skgb_cls__md2_lr002_mln31` | 0.5093 | 0.0026 | 0.0000 |
| `skgb_cls__md2_lr002_mln63` | 0.5087 | 0.0025 | 0.0000 |
| `skgb_cls__md2_lr002_mln15` | 0.5082 | 0.0026 | 0.0000 |

**regressor** — sweep `2026-06-27_00-02-28` · metric `pred_reg_ic_mean` · 27/27 OK · 0.83 h
· selected/recommended: `skgb_reg__md3_lr005_mln31` (best σ-adj: `skgb_reg__md2_lr002_mln31`); >1σ over default: False

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `skgb_reg__md2_lr002_mln15` | 0.0234 | 0.0048 | 0.0000 |
| `skgb_reg__md3_lr002_mln15` | 0.0233 | 0.0057 | 0.0000 |
| `skgb_reg__md3_lr002_mln63` | 0.0233 | 0.0049 | 0.0000 |
| `skgb_reg__md2_lr002_mln31` *(best)* | 0.0233 | 0.0042 | 0.0000 |
| `skgb_reg__md3_lr002_mln31` | 0.0228 | 0.0043 | 0.0000 |
| `skgb_reg__md2_lr005_mln31` | 0.0226 | 0.0046 | 0.0000 |
| `skgb_reg__md2_lr002_mln63` | 0.0226 | 0.0050 | 0.0000 |
| `skgb_reg__md2_lr005_mln15` | 0.0220 | 0.0051 | 0.0000 |
| `skgb_reg__md2_lr005_mln63` | 0.0219 | 0.0054 | 0.0000 |
| `skgb_reg__md3_lr005_mln31` **(rec)** | 0.0214 | 0.0048 | 0.0000 |
| `skgb_reg__md5_lr002_mln15` | 0.0210 | 0.0062 | 0.0000 |
| `skgb_reg__md2_lr01_mln15` | 0.0208 | 0.0059 | 0.0000 |
| `skgb_reg__md2_lr01_mln63` | 0.0199 | 0.0061 | 0.0000 |
| `skgb_reg__md2_lr01_mln31` | 0.0189 | 0.0053 | 0.0000 |
| `skgb_reg__md3_lr005_mln63` | 0.0188 | 0.0049 | 0.0000 |
| `skgb_reg__md5_lr002_mln31` | 0.0187 | 0.0035 | 0.0000 |
| `skgb_reg__md3_lr01_mln63` | 0.0180 | 0.0038 | 0.0000 |
| `skgb_reg__md3_lr005_mln15` | 0.0180 | 0.0049 | 0.0000 |
| `skgb_reg__md5_lr002_mln63` | 0.0177 | 0.0024 | 0.0000 |
| `skgb_reg__md3_lr01_mln15` | 0.0175 | 0.0050 | 0.0000 |
| `skgb_reg__md5_lr005_mln15` | 0.0170 | 0.0056 | 0.0000 |
| `skgb_reg__md5_lr005_mln31` | 0.0169 | 0.0039 | 0.0000 |
| `skgb_reg__md3_lr01_mln31` | 0.0163 | 0.0052 | 0.0000 |
| `skgb_reg__md5_lr01_mln63` | 0.0163 | 0.0037 | 0.0000 |
| `skgb_reg__md5_lr01_mln15` | 0.0155 | 0.0063 | 0.0000 |
| `skgb_reg__md5_lr005_mln63` | 0.0134 | 0.0030 | 0.0000 |
| `skgb_reg__md5_lr01_mln31` | 0.0129 | 0.0049 | 0.0000 |


### RandomForest

**ranker** — sweep `2026-06-24_19-32-47` · metric `pred_rank_ic_mean` · 27/27 OK · 12.27 h
· selected/recommended: `skrf_rk__mfsqrt_msl20_md8` (best σ-adj: `skrf_rk__mfsqrt_msl20_md8`); >1σ over default: False

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `skrf_rk__mfsqrt_msl20_md8` **(rec)** | 0.0257 | 0.0062 | 0.1234 |
| `skrf_rk__mfsqrt_msl50_md8` | 0.0251 | 0.0064 | 0.1206 |
| `skrf_rk__mfsqrt_msl5_md8` | 0.0248 | 0.0060 | 0.1201 |
| `skrf_rk__mf033_msl20_md8` | 0.0238 | 0.0059 | 0.1197 |
| `skrf_rk__mf033_msl50_md8` | 0.0234 | 0.0054 | 0.1167 |
| `skrf_rk__mf05_msl20_md8` | 0.0232 | 0.0051 | 0.1189 |
| `skrf_rk__mf05_msl5_md8` | 0.0232 | 0.0060 | 0.1196 |
| `skrf_rk__mf033_msl5_md8` | 0.0231 | 0.0060 | 0.1162 |
| `skrf_rk__mf05_msl50_md8` | 0.0230 | 0.0053 | 0.1176 |
| `skrf_rk__mfsqrt_msl50_md16` | 0.0222 | 0.0041 | 0.1143 |
| `skrf_rk__mfsqrt_msl5_md16` | 0.0211 | 0.0053 | 0.1100 |
| `skrf_rk__mfsqrt_msl20_md16` | 0.0204 | 0.0044 | 0.1052 |
| `skrf_rk__mf033_msl50_md16` | 0.0203 | 0.0036 | 0.1058 |
| `skrf_rk__mf033_msl20_md16` | 0.0200 | 0.0036 | 0.1045 |
| `skrf_rk__mf05_msl5_md16` | 0.0198 | 0.0030 | 0.1047 |
| `skrf_rk__mf033_msl5_md16` | 0.0197 | 0.0033 | 0.1039 |
| `skrf_rk__mf05_msl50_md16` | 0.0195 | 0.0036 | 0.1023 |
| `skrf_rk__mfsqrt_msl50_mdNone` | 0.0194 | 0.0034 | 0.1001 |
| `skrf_rk__mf05_msl20_md16` | 0.0192 | 0.0033 | 0.1011 |
| `skrf_rk__mfsqrt_msl20_mdNone` | 0.0176 | 0.0035 | 0.0907 |
| `skrf_rk__mf033_msl50_mdNone` | 0.0174 | 0.0034 | 0.0905 |
| `skrf_rk__mf05_msl50_mdNone` | 0.0170 | 0.0038 | 0.0887 |
| `skrf_rk__mfsqrt_msl5_mdNone` | 0.0163 | 0.0022 | 0.0835 |
| `skrf_rk__mf033_msl5_mdNone` | 0.0163 | 0.0026 | 0.0841 |
| `skrf_rk__mf033_msl20_mdNone` | 0.0162 | 0.0029 | 0.0834 |
| `skrf_rk__mf05_msl20_mdNone` | 0.0155 | 0.0031 | 0.0801 |
| `skrf_rk__mf05_msl5_mdNone` | 0.0154 | 0.0025 | 0.0799 |

**classifier** — sweep `2026-06-25_07-49-06` · metric `pred_auc` · 27/27 OK · 12.41 h
· selected/recommended: `skrf_cls__mf05_msl20_mdNone` (best σ-adj: `skrf_cls__mf05_msl20_mdNone`); >1σ over default: True

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `skrf_cls__mf05_msl20_mdNone` **(rec)** | 0.5163 | 0.0017 | 0.1211 |
| `skrf_cls__mf033_msl50_mdNone` | 0.5161 | 0.0023 | 0.1194 |
| `skrf_cls__mf05_msl50_mdNone` | 0.5161 | 0.0021 | 0.1205 |
| `skrf_cls__mf033_msl5_md16` | 0.5161 | 0.0023 | 0.1222 |
| `skrf_cls__mf033_msl5_mdNone` | 0.5161 | 0.0015 | 0.1224 |
| `skrf_cls__mf05_msl5_md16` | 0.5161 | 0.0022 | 0.1220 |
| `skrf_cls__mf05_msl5_mdNone` | 0.5160 | 0.0018 | 0.1215 |
| `skrf_cls__mf033_msl20_md16` | 0.5160 | 0.0024 | 0.1197 |
| `skrf_cls__mf033_msl50_md16` | 0.5160 | 0.0026 | 0.1206 |
| `skrf_cls__mf05_msl50_md16` | 0.5160 | 0.0024 | 0.1246 |
| `skrf_cls__mf033_msl20_mdNone` | 0.5159 | 0.0020 | 0.1223 |
| `skrf_cls__mf05_msl20_md16` | 0.5159 | 0.0024 | 0.1242 |
| `skrf_cls__mfsqrt_msl50_md16` | 0.5157 | 0.0027 | 0.1218 |
| `skrf_cls__mfsqrt_msl50_mdNone` | 0.5156 | 0.0023 | 0.1231 |
| `skrf_cls__mfsqrt_msl20_mdNone` | 0.5156 | 0.0017 | 0.1220 |
| `skrf_cls__mfsqrt_msl5_md16` | 0.5156 | 0.0021 | 0.1219 |
| `skrf_cls__mfsqrt_msl20_md16` | 0.5155 | 0.0027 | 0.1173 |
| `skrf_cls__mfsqrt_msl5_mdNone` | 0.5154 | 0.0019 | 0.1206 |
| `skrf_cls__mf033_msl5_md8` | 0.5126 | 0.0034 | 0.1231 |
| `skrf_cls__mf033_msl20_md8` | 0.5126 | 0.0037 | 0.1225 |
| `skrf_cls__mf05_msl5_md8` | 0.5125 | 0.0035 | 0.1214 |
| `skrf_cls__mfsqrt_msl20_md8` | 0.5125 | 0.0033 | 0.1234 |
| `skrf_cls__mf033_msl50_md8` | 0.5124 | 0.0034 | 0.1192 |
| `skrf_cls__mfsqrt_msl50_md8` | 0.5123 | 0.0033 | 0.1226 |
| `skrf_cls__mf05_msl50_md8` | 0.5123 | 0.0034 | 0.1218 |
| `skrf_cls__mf05_msl20_md8` | 0.5123 | 0.0038 | 0.1219 |
| `skrf_cls__mfsqrt_msl5_md8` | 0.5122 | 0.0036 | 0.1220 |

**regressor** — sweep `2026-06-25_20-13-42` · metric `pred_reg_ic_mean` · 27/27 OK · 14.10 h
· selected/recommended: `skrf_reg__mfsqrt_msl20_md8` (best σ-adj: `skrf_reg__mfsqrt_msl20_md8`); >1σ over default: False

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `skrf_reg__mfsqrt_msl20_md8` **(rec)** | 0.0268 | 0.0049 | 0.1234 |
| `skrf_reg__mfsqrt_msl50_md8` | 0.0267 | 0.0049 | 0.1226 |
| `skrf_reg__mfsqrt_msl5_md8` | 0.0260 | 0.0052 | 0.1220 |
| `skrf_reg__mfsqrt_msl50_md16` | 0.0245 | 0.0042 | 0.1218 |
| `skrf_reg__mfsqrt_msl5_md16` | 0.0245 | 0.0034 | 0.1219 |
| `skrf_reg__mfsqrt_msl20_md16` | 0.0239 | 0.0045 | 0.1173 |
| `skrf_reg__mf033_msl50_md8` | 0.0231 | 0.0051 | 0.1192 |
| `skrf_reg__mf033_msl20_md8` | 0.0223 | 0.0048 | 0.1225 |
| `skrf_reg__mf033_msl5_md8` | 0.0221 | 0.0054 | 0.1231 |
| `skrf_reg__mf05_msl20_md8` | 0.0220 | 0.0044 | 0.1219 |
| `skrf_reg__mf033_msl5_md16` | 0.0220 | 0.0038 | 0.1222 |
| `skrf_reg__mf05_msl50_md8` | 0.0218 | 0.0042 | 0.1218 |
| `skrf_reg__mf033_msl20_md16` | 0.0215 | 0.0035 | 0.1197 |
| `skrf_reg__mf033_msl50_md16` | 0.0213 | 0.0037 | 0.1206 |
| `skrf_reg__mf05_msl50_md16` | 0.0208 | 0.0029 | 0.1246 |
| `skrf_reg__mf05_msl5_md8` | 0.0208 | 0.0051 | 0.1214 |
| `skrf_reg__mf05_msl5_md16` | 0.0206 | 0.0039 | 0.1220 |
| `skrf_reg__mf05_msl20_md16` | 0.0204 | 0.0031 | 0.1242 |
| `skrf_reg__mfsqrt_msl50_mdNone` | 0.0203 | 0.0041 | 0.1231 |
| `skrf_reg__mfsqrt_msl20_mdNone` | 0.0196 | 0.0034 | 0.1220 |
| `skrf_reg__mfsqrt_msl5_mdNone` | 0.0192 | 0.0035 | 0.1206 |
| `skrf_reg__mf033_msl50_mdNone` | 0.0187 | 0.0033 | 0.1194 |
| `skrf_reg__mf05_msl50_mdNone` | 0.0181 | 0.0037 | 0.1205 |
| `skrf_reg__mf033_msl5_mdNone` | 0.0176 | 0.0031 | 0.1224 |
| `skrf_reg__mf033_msl20_mdNone` | 0.0173 | 0.0031 | 0.1223 |
| `skrf_reg__mf05_msl5_mdNone` | 0.0166 | 0.0031 | 0.1215 |
| `skrf_reg__mf05_msl20_mdNone` | 0.0163 | 0.0029 | 0.1211 |


### Linear

**ranker** — sweep `2026-06-26_10-19-42` · metric `pred_rank_ic_mean` · 12/12 OK · 0.41 h
· selected/recommended: `lin_rk__alph0001_lr05` (best σ-adj: `lin_rk__alph001_lr05`); >1σ over default: False

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `lin_rk__alph001_lr05` *(best)* | 0.0174 | 0.0041 | 0.0866 |
| `lin_rk__alph001_lr09` | 0.0162 | 0.0042 | 0.0781 |
| `lin_rk__alph01_lr01` | 0.0159 | 0.0043 | 0.0761 |
| `lin_rk__alph001_lr01` | 0.0154 | 0.0037 | 0.0813 |
| `lin_rk__alph0001_lr09` | 0.0150 | 0.0038 | 0.0792 |
| `lin_rk__alph0001_lr05` **(rec)** | 0.0143 | 0.0037 | 0.0763 |
| `lin_rk__alph0001_lr01` | 0.0138 | 0.0036 | 0.0745 |
| `lin_rk__alph00001_lr09` | 0.0137 | 0.0036 | 0.0743 |
| `lin_rk__alph00001_lr05` | 0.0137 | 0.0036 | 0.0743 |
| `lin_rk__alph00001_lr01` | 0.0137 | 0.0037 | 0.0743 |

**classifier** — sweep `2026-06-26_10-44-11` · metric `pred_auc` · 4/4 OK · 0.16 h
· selected/recommended: `lin_cls__C1` (best σ-adj: `lin_cls__C001`); >1σ over default: False

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `lin_cls__C001` *(best)* | 0.5138 | 0.0021 | 0.0763 |
| `lin_cls__C01` | 0.5137 | 0.0021 | 0.0763 |
| `lin_cls__C1` **(rec)** | 0.5137 | 0.0021 | 0.0763 |
| `lin_cls__C10` | 0.5137 | 0.0021 | 0.0763 |

**regressor** — sweep `2026-06-26_10-53-39` · metric `pred_reg_ic_mean` · 12/12 OK · 0.48 h
· selected/recommended: `lin_reg__alph001_lr01` (best σ-adj: `lin_reg__alph001_lr01`); >1σ over default: True

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `lin_reg__alph001_lr01` **(rec)** | 0.0342 | 0.0007 | 0.0763 |
| `lin_reg__alph0001_lr09` | 0.0337 | 0.0008 | 0.0763 |
| `lin_reg__alph0001_lr05` | 0.0296 | 0.0015 | 0.0763 |
| `lin_reg__alph0001_lr01` | 0.0193 | 0.0039 | 0.0763 |
| `lin_reg__alph00001_lr09` | 0.0189 | 0.0038 | 0.0763 |
| `lin_reg__alph00001_lr05` | 0.0179 | 0.0036 | 0.0763 |
| `lin_reg__alph00001_lr01` | 0.0163 | 0.0035 | 0.0763 |
| `lin_reg__alph001_lr05` | -0.0000 | 0.0000 | 0.0763 |
| `lin_reg__alph001_lr09` | -0.0000 | 0.0000 | 0.0763 |
| `lin_reg__alph01_lr01` | -0.0000 | 0.0000 | 0.0763 |
| `lin_reg__alph01_lr05` | -0.0000 | 0.0000 | 0.0763 |
| `lin_reg__alph01_lr09` | -0.0000 | 0.0000 | 0.0763 |


### FT-Transformer

**ranker** — sweep `2026-06-28_06-58-15` · metric `pred_rank_ic_mean` · 6/6 OK · 12.00 h
· selected/recommended: `ft_rk__dt64_nl3` (best σ-adj: `ft_rk__dt128_nl1`); >1σ over default: False

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `ft_rk__dt128_nl1` *(best)* | 0.0232 | 0.0062 | 0.1255 |
| `ft_rk__dt128_nl2` | 0.0222 | 0.0048 | 0.1161 |
| `ft_rk__dt128_nl3` | 0.0205 | 0.0041 | 0.1117 |
| `ft_rk__dt64_nl1` | 0.0195 | 0.0034 | 0.1060 |
| `ft_rk__dt64_nl3` **(rec)** | 0.0191 | 0.0052 | 0.1030 |
| `ft_rk__dt64_nl2` | 0.0190 | 0.0052 | 0.1019 |

**classifier** — sweep `2026-06-28_18-58-13` · metric `pred_auc` · 6/6 OK · 12.01 h
· selected/recommended: `ft_cls__dt64_nl3` (best σ-adj: `ft_cls__dt64_nl2`); >1σ over default: False

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `ft_cls__dt64_nl2` *(best)* | 0.5114 | 0.0031 | 0.0990 |
| `ft_cls__dt64_nl3` **(rec)** | 0.5099 | 0.0038 | 0.1030 |
| `ft_cls__dt128_nl3` | 0.5087 | 0.0028 | 0.1177 |
| `ft_cls__dt128_nl1` | 0.5074 | 0.0038 | 0.1140 |
| `ft_cls__dt64_nl1` | 0.5072 | 0.0030 | 0.1049 |
| `ft_cls__dt128_nl2` | 0.5065 | 0.0029 | 0.1050 |

**regressor** — sweep `2026-06-29_06-58-44` · metric `pred_reg_ic_mean` · 6/6 OK · 12.00 h
· selected/recommended: `ft_reg__dt64_nl3` (best σ-adj: `ft_reg__dt128_nl3`); >1σ over default: False

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `ft_reg__dt128_nl3` *(best)* | 0.0251 | 0.0053 | 0.1090 |
| `ft_reg__dt64_nl3` **(rec)** | 0.0237 | 0.0030 | 0.1033 |
| `ft_reg__dt64_nl2` | 0.0219 | 0.0052 | 0.1031 |
| `ft_reg__dt128_nl2` | 0.0219 | 0.0049 | 0.1018 |
| `ft_reg__dt64_nl1` | 0.0201 | 0.0021 | 0.1115 |
| `ft_reg__dt128_nl1` | 0.0146 | 0.0059 | 0.1112 |


### TabM

**ranker** — sweep `2026-06-29_18-58-38` · metric `pred_rank_ic_mean` · 6/6 OK · 0.60 h
· selected/recommended: `tabm_rk__km32_hidd128` (best σ-adj: `tabm_rk__km32_hidd128`); >1σ over default: True

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `tabm_rk__km32_hidd128` **(rec)** | 0.0103 | 0.0016 | 0.0719 |
| `tabm_rk__km8_hidd128` | 0.0089 | 0.0043 | 0.0648 |
| `tabm_rk__km1_hidd256` | 0.0089 | 0.0044 | 0.0610 |
| `tabm_rk__km1_hidd128` | 0.0088 | 0.0025 | 0.0591 |
| `tabm_rk__km32_hidd256` | 0.0077 | 0.0032 | 0.0553 |
| `tabm_rk__km8_hidd256` | 0.0067 | 0.0055 | 0.0465 |

**classifier** — sweep `2026-06-29_19-34-36` · metric `pred_auc` · 6/6 OK · 0.60 h
· selected/recommended: `tabm_cls__km8_hidd256` (best σ-adj: `tabm_cls__km8_hidd128`); >1σ over default: False

| variant | auc | path-σ | RankICIR |
|---|---|---|---|
| `tabm_cls__km8_hidd128` *(best)* | 0.5123 | 0.0037 | 0.0716 |
| `tabm_cls__km1_hidd128` | 0.5114 | 0.0026 | 0.0441 |
| `tabm_cls__km8_hidd256` **(rec)** | 0.5114 | 0.0033 | 0.0465 |
| `tabm_cls__km32_hidd128` | 0.5113 | 0.0020 | 0.0724 |
| `tabm_cls__km1_hidd256` | 0.5112 | 0.0031 | 0.0424 |
| `tabm_cls__km32_hidd256` | 0.5109 | 0.0020 | 0.0585 |

**regressor** — sweep `2026-06-29_20-10-23` · metric `pred_reg_ic_mean` · 6/6 OK · 0.59 h
· selected/recommended: `tabm_reg__km8_hidd256` (best σ-adj: `tabm_reg__km1_hidd128`); >1σ over default: False

| variant | reg_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `tabm_reg__km1_hidd128` *(best)* | 0.0110 | 0.0050 | 0.0528 |
| `tabm_reg__km1_hidd256` | 0.0085 | 0.0061 | 0.0424 |
| `tabm_reg__km8_hidd128` | 0.0078 | 0.0043 | 0.0713 |
| `tabm_reg__km8_hidd256` **(rec)** | 0.0068 | 0.0018 | 0.0465 |
| `tabm_reg__km32_hidd256` | 0.0064 | 0.0024 | 0.0601 |
| `tabm_reg__km32_hidd128` | 0.0045 | 0.0054 | 0.0681 |


### LSTM

**ranker** — sweep `2026-06-29_20-46-07` · metric `pred_rank_ic_mean` · 6/6 OK · 0.41 h
· selected/recommended: `lstm__look60_hidd64` (best σ-adj: `lstm__look20_hidd64`); >1σ over default: False

| variant | rank_ic_mean | path-σ | RankICIR |
|---|---|---|---|
| `lstm__look20_hidd64` *(best)* | 0.0112 | 0.0062 | 0.0810 |
| `lstm__look60_hidd64` **(rec)** | 0.0090 | 0.0043 | 0.0635 |
| `lstm__look60_hidd32` | 0.0040 | 0.0036 | 0.0297 |
| `lstm__look20_hidd32` | 0.0040 | 0.0015 | 0.0285 |
| `lstm__look120_hidd64` | 0.0036 | 0.0011 | 0.0260 |
| `lstm__look120_hidd32` | 0.0029 | 0.0054 | 0.0198 |

<!-- END APPENDIX TABLES -->

---

# Appendix B — Recommended production configurations (winning hyperparameters)

**RandomForest — ranker** (`skrf_rk__mfsqrt_msl20_md8`)
```json
{ "n_estimators": 500, "max_features": "sqrt", "min_samples_leaf": 20,
  "max_depth": 8, "n_jobs": -1, "random_state": 54 }
```

**RandomForest — regressor** (`skrf_reg__mfsqrt_msl20_md8`) — same shape
```json
{ "n_estimators": 500, "max_features": "sqrt", "min_samples_leaf": 20,
  "max_depth": 8, "n_jobs": -1, "random_state": 54 }
```

**Linear / ElasticNet — regressor** (`lin_reg__alph001_lr01`) — the most stable result
```json
{ "alpha": 0.01, "l1_ratio": 0.1, "random_state": 48 }
```
*Stability note:* the Linear regressor is sensitive — several higher-`alpha`/`lr` variants
collapsed to all-zero coefficients (IC ≈ 0). The winning config is the regularised but
non-degenerate corner.

**Linear / ElasticNet — ranker** (`lin_rk__alph001_lr05`)
```json
{ "alpha": 0.01, "l1_ratio": 0.5, "random_state": 49 }
```

**HistGB — ranker** (`skgb_rk__md3_lr002_mln15`) — recommended back-up / ensemble member
```json
{ "n_estimators": 300, "max_depth": 3, "learning_rate": 0.02,
  "max_leaf_nodes": 15, "min_samples_leaf": 20, "max_features": 0.9, "random_state": 51 }
```

**HistGB — classifier** (`skgb_cls__md5_lr01_mln31`) — best classifier (still ~0.52 AUC)
```json
{ "n_estimators": 300, "max_depth": 5, "learning_rate": 0.1,
  "max_leaf_nodes": 31, "min_samples_leaf": 20, "max_features": 0.9, "random_state": 67 }
```

---

# Appendix C — Sweep index (provenance)

| Family | Role | Run folder | Variants | OK | Wall-clock |
|---|---|---|---|---|---|
| LightGBM | ranker | `2026-06-24_06-22-59` | 27 | 27 | 1.17 h |
| LightGBM | classifier | `2026-06-24_07-32-58` | 27 | 27 | 1.16 h |
| LightGBM | regressor | `2026-06-24_08-42-41` | 27 | 27 | 1.16 h |
| XGBoost | ranker | `2026-06-24_09-52-12` | 27 | 27 | 1.97 h |
| XGBoost | classifier | `2026-06-24_11-50-18` | 27 | 27 | 1.75 h |
| XGBoost | regressor | `2026-06-24_13-35-15` | 27 | 27 | 1.74 h |
| CatBoost | ranker | `2026-06-24_15-19-50` | 27 | 27 | 1.37 h |
| CatBoost | classifier | `2026-06-24_16-41-57` | 27 | 27 | 1.39 h |
| CatBoost | regressor | `2026-06-24_18-05-07` | 27 | 27 | 1.38 h |
| RandomForest | ranker | `2026-06-24_19-32-47` | 27 | 27 | 12.27 h |
| RandomForest | classifier | `2026-06-25_07-49-06` | 27 | 27 | 12.41 h |
| RandomForest | regressor | `2026-06-25_20-13-42` | 27 | 27 | 14.10 h |
| Linear | ranker | `2026-06-26_10-19-42` | 12 | 12 | 0.41 h |
| Linear | classifier | `2026-06-26_10-44-11` | 4 | 4 | 0.16 h |
| Linear | regressor | `2026-06-26_10-53-39` | 12 | 12 | 0.48 h |
| HistGB | ranker | `2026-06-26_22-10-59` | 27 | 27 | 0.86 h |
| HistGB | classifier | `2026-06-26_23-02-34` | 27 | 27 | 1.00 h |
| HistGB | regressor | `2026-06-27_00-02-28` | 27 | 27 | 0.83 h |
| FT-Transformer | ranker | `2026-06-28_06-58-15` | 6 | 6 | 12.00 h |
| FT-Transformer | classifier | `2026-06-28_18-58-13` | 6 | 6 | 12.01 h |
| FT-Transformer | regressor | `2026-06-29_06-58-44` | 6 | 6 | 12.00 h |
| TabM | ranker | `2026-06-29_18-58-38` | 6 | 6 | 0.60 h |
| TabM | classifier | `2026-06-29_19-34-36` | 6 | 6 | 0.60 h |
| TabM | regressor | `2026-06-29_20-10-23` | 6 | 6 | 0.59 h |
| LSTM | ranker | `2026-06-29_20-46-07` | 6 | 6 | 0.41 h |

**Totals:** 25 sweeps · 426 (config × role) fits · 100 % OK after the HistGB fix ·
Group A ≈ 53 h CPU, Group B ≈ 38 h GPU.

*End of report.*
