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

This is a design/strategy question — no code changes needed. Here's a structured analysis across the most impactful dimensions.

---

# Strategies to Improve Prediction Accuracy & Reliability

## 1. Feature Engineering

### Add Missing Features from the Spec
The current `MODEL_FEATURES` (14 features) is missing several from [rel1_document.md](cci:7://file:///home/victor_truong/ai-investment-pipeline-master/notebooks/rel1_document.md:0:0-0:0) Section 3.2:
- **ATR (Average True Range)** — better volatility proxy than realized vol, uses High/Low/Close
- **EMA(5), EMA(20)** — faster trend signals than SMA ratios
- **Trend slope** — linear regression slope over 10-20 days (captures acceleration, not just level)
- **Market regime features** — SPY rolling vol, VIX proxy (VIX or VVIX), market breadth (% of 30 stocks above their 20d SMA)

### Add Relative Strength vs Market
Each stock's return relative to the SPY ETF (which is already in the ticker universe as `VOO`). Cross-sectional alpha vs beta matters more than raw returns.

### Reduce Feature Noise
- **Winsorize** extreme return values (e.g. clip at ±20%) before training to prevent outlier-driven label corruption
- **Lag the cross-sectional ranks** — `rank_ret_5d` computed on the same 5d return used as label creates subtle look-ahead. Ensure ranks are computed on returns ending at `t`, not `t+5`.

---

## 2. Label Design

### Current Problem
`y_cls = 1 if fwd_ret_1w > 0 else 0` is highly noisy. ~50% of stocks will randomly be above zero even in noise. This makes the classifier learn near-random signal.

### Improvements
- **Use a threshold**: `y_cls = 1 if fwd_ret_1w > X%` where X is the median daily cost (spread + slippage + commission ≈ 16bps from [settings.yaml](cci:7://file:///home/victor_truong/ai-investment-pipeline-master/config/settings.yaml:0:0-0:0)). Only label as positive if the return is economically meaningful.
- **Tertile/quintile labels for ranker**: Instead of dense ranking, use quintile labels (0-4) which are less sensitive to return noise within a cohort and more robust to small restatements.
- **Neutral zone for classifier**: Consider a 3-class label (down / neutral / up) and only bet on high-confidence predictions. The `prob_hurdle=0.55` in config partly handles this, but a 3-class model is more expressive.

---

## 3. Model Training

### Walk-Forward Cross-Validation (Critical)
The current code uses a single `train_cutoff_date = "2023-01-01"` split. This means:
- The model is trained on 2015–2023 and tested on 2023–2026 — a single out-of-sample window
- No sense of whether performance is stable across different market regimes

**Fix:** Implement expanding-window (or rolling-window) cross-validation:
```
Fold 1: train 2015–2018, val 2018–2019
Fold 2: train 2015–2019, val 2019–2020
Fold 3: train 2015–2020, val 2020–2021
...
```
Average metrics across folds give a much more reliable estimate of live performance.

### Prevent Feature-Target Leakage
- `rank_ret_5d` and `rank_vol_20d` are cross-sectional features computed across the full universe at time `t`. This is fine for inference. But in the label builder, confirm that the group used for ranking at time `t` never includes future rows.
- `LabelBuilder.align()` should verify that the feature matrix index and the label index are aligned purely on `(date, ticker)` with no forward shift.

### LightGBM Hyperparameter Tuning
Current params are defaults (e.g. `num_leaves=31`). For 30 tickers × ~2000 trading days = ~60K rows, this is sufficient but not optimal. Suggestions:
- Use **Optuna** for Bayesian hyperparameter search with a walk-forward CV objective
- Tune `min_data_in_leaf` carefully — too small overfits to noise in small-cap cohorts
- Add `lambda_l1`, `lambda_l2` regularization to reduce overfitting on noisy financial labels

---

## 4. Ensemble & Model Architecture

### Use Predicted Scores More Carefully in SlotSelector
The current opportunity score is a linear combination:
```
score = c_rank * norm(rank_score) + c_ret * (pred_return * 10) + c_prob * (prob_up - 0.5)
```
The `* 10` scaling on `pred_return` is a manual calibration hack. Instead:
- **Normalize all three outputs to the same scale** (e.g. z-score within the daily cross-section) before combining
- Use the grid-searched coefficients from [optimize_coefficients()](cci:1://file:///home/victor_truong/ai-investment-pipeline-master/pipeline/policy/slot_selector.py:194:4-259:34) but validate them on a held-out period, not the same training data

### Add a Stacking Layer
Rather than a fixed linear combination, train a lightweight meta-model (e.g. logistic regression or a small MLP) that takes `[rank_score, pred_return, prob_up]` as inputs and predicts the binary label. This lets the combination weights be learned, not hand-tuned.

### Calibrate the Classifier
LightGBM's raw probability output is not well-calibrated by default. Use **Platt scaling** (`sklearn.calibration.CalibratedClassifierCV`) post-training so `prob_up=0.55` genuinely means 55% win rate. This makes the `prob_hurdle` threshold much more interpretable and reliable.

---

## 5. Regime Awareness

The 30-stock universe spans 2015–2026, which includes:
- Bull market (2015–2020 pre-COVID)
- COVID crash and recovery
- Tech bull (2020–2021)
- Rate-hike bear market (2022)
- Recovery (2023–2024)

A single model trained across all regimes will average out regime-specific signals. Approaches:
- **Regime feature** — add SPY 60d rolling vol as a feature, so the model can condition on regime
- **Separate models per regime** — train one model for low-vol regime, one for high-vol, use a regime classifier to switch at inference time
- **Time-weighted training** — use LightGBM's `weight` parameter to up-weight recent data

---

## 6. Signal Quality Checks at Inference

Before passing predictions to [SlotSelector](cci:2://file:///home/victor_truong/ai-investment-pipeline-master/pipeline/policy/slot_selector.py:54:0-399:78), add sanity checks in [main_inference.py](cci:7://file:///home/victor_truong/ai-investment-pipeline-master/pipeline/main_inference.py:0:0-0:0):
- **Model staleness check** — refuse to trade if the loaded model is older than N days (model version from [ModelManager](cci:2://file:///home/victor_truong/ai-investment-pipeline-master/pipeline/models/model_manager.py:12:0-131:37))
- **Feature distribution shift** — compare today's feature values against the training distribution (e.g. flag if any feature is >3σ from training mean). Extreme feature values often indicate bad data from `yfinance`, not genuine signals.
- **Prediction sanity check** — if `pred_return` range is unexpectedly large (e.g. >50% predicted weekly return), log a warning and fall back to CASH

---

## Priority Order

| Priority   | Strategy | Effort | Expected Impact |
|------------|-----------------------------------------------|--------|-----------------|
| 🔴 High   | Walk-forward cross-validation                 | Medium | High — current single-split is unreliable |
| 🔴 High   | Better classifier label (threshold, not zero) | Low    | High — fixes noisy 50/50 binary signal |
| 🔴 High   | Normalize inputs to SlotSelector consistently | Low    | Medium — removes manual `*10` hack |
| 🟡 Medium | Add ATR, EMA, market regime features          | Medium | Medium |
| 🟡 Medium | Calibrate classifier probabilities            | Low    | Medium — makes `prob_hurdle` reliable |
| 🟡 Medium | Optuna hyperparameter tuning with CV          | High   | Medium |
| 🟢 Low    | Stacking meta-model                           | High   | Medium — adds complexity |
| 🟢 Low    | Regime-specific models                        | High   | High but complex |



================================================================================================================


# Walk-Forward Backtest Changes

- main_train.py — Cleaned up
- Removed all CV code: _make_folds(), _evaluate_ranker/regressor/classifier(), walk_forward_cv()
- Removed unused imports: csv, numpy, sklearn.metrics, List/Dict/Any
- Reverted --mode choices back to ["price", "fundamental", "both"]
- Removed --cv-fold-years and --cv-val-years CLI args
- File is back to its original clean structure
- main_backtest.py — Walk-Forward Backtest added


### New function walk_forward_backtest() — per fold:

- Trains fresh Ranker + Regressor + Classifier on the expanding training window
- Optimises SlotSelector coefficients on that same training window (no look-ahead)
- Runs Backtester on the held-out test window
- Stitches the equity curve to the previous fold's endpoint (continuous compounding across regimes)


Equity curve stitching: each fold starts at $20K internally, but the reported curve scales each fold to continue from where the previous fold ended. This gives a realistic picture of total dollar growth over the full period.

### Output:

- Per-fold table in the log: Sharpe, CAGR, MaxDD, TotalReturn, HitRate
- FULL row: metrics computed on the single stitched equity curve
- logs/wf_backtest_results.csv saved automatically
- Full equity curve plot via BacktestReport (same as single-split)


================================================================================================================


# Changes to label_builder.py

### Classifier label (line 83)
Before: y_cls = 1 if fwd_ret_1w > 0
After: y_cls = 1 if fwd_ret_1w > 0.0016 (16bps = one-way cost)

With 30 stocks, ~50% of them randomly beat zero on any given week. Now the classifier only fires 1 when the return is large enough to actually profit after you pay to enter and exit the position. This shifts the class balance — roughly 35–40% of samples will be positive (stocks that genuinely outperform the cost hurdle) instead of 50%, giving the model a cleaner signal to learn from.

### Ranker label (line 88–90)
Before: pd.Series.rank(method="dense", ascending=False) — produces integer ranks 1 through N with ties resolved arbitrarily
After: pd.qcut(x, q=5, labels=False, duplicates="drop") — produces quintile labels 0–4

With 30 stocks, dense ranking produces 30 distinct labels. The difference between rank 14 and rank 15 is meaningless noise (near-zero return difference). Quintile labels bucket stocks into 5 equal groups per day — only the top 6 stocks get label 4, bottom 6 get label 0. LightGBM's lambdarank has much less noise to fit against.

settings.yaml — new key
yaml
costs:
  cls_threshold_bps: 16  # classifier positive label threshold
The threshold is now explicit and configurable. Change it here to tune how selective the positive label is without touching code.

One important consequence
After these changes, retrain is required — the saved models in trained_models/ were trained on the old labels. Run:

bash
python -m pipeline.main_train --mode price



================================================================================================================


# Changes to slot_selector.py

1. Z-score normalization replaces min-max (lines 149–158)
Before:

python
df["norm_rank"] = self._normalize(df["rank_score"])   # min-max 0..1
df["opportunity"] = (
    c_rank * df["norm_rank"] +
    c_ret  * (df["pred_return"] * 10) +   # ← manual hack
    c_prob * (df["prob_up"] - 0.5)        # ← manual centering
)
After:

python
df["z_rank"] = self._zscore(df["rank_score"])
df["z_ret"]  = self._zscore(df["pred_return"])
df["z_prob"] = self._zscore(df["prob_up"])
df["opportunity"] = c_rank * df["z_rank"] + c_ret * df["z_ret"] + c_prob * df["z_prob"]
All three signals now have mean=0, std=1 within each day's cross-section before combining. The coefficients c_rank + c_ret + c_prob = 1.0 now have genuine comparable units — no manual * 10 or - 0.5 adjustments needed.

2. _normalize() replaced by _zscore() (line 277)
The old min-max helper is gone. _zscore() handles the degenerate case (all stocks identical → returns zeros instead of crashing).

3. optimize_coefficients() now evaluates on a held-out tail (lines 43–48)
Before: _run_backtest_worker ran the backtest on the entire _GLOBAL_DF (the training data passed in). The best coefficients were the ones that best fit the training period — not necessarily the ones that generalise.

After: Each worker extracts the last 20% of dates from _GLOBAL_DF as a held-out validation slice, and evaluates Sharpe on that slice only. The first 80% is used by the models for training; the last 20% is the unseen evaluation window for coefficient selection.

This means: given df_train from 2015–2023, the grid search now picks coefficients that maximise Sharpe on 2021.4–2023, not on the full 2015–2023. The coefficients have to generalise across a period the backtester hasn't overfit to.

Downstream impact
Retrain + re-run RECOMPUTE_COEFFS is required to benefit from the new z-score normalisation:

bash
python -m pipeline.main_train --mode price      # retrain models
python -m pipeline.main_backtest                # recomputes coefficients on val tail

The saved policy_params.json coefficients were optimised under the old * 10 scaling, so they will produce incorrect scores until recalculated.
