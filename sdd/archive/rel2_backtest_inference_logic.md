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

# Release 2 — Backtest & Inference Logic

> **Audience:** Humans and AI coding agents working on this codebase.
> **Last updated:** 2026-04-05

---

## 1. Overview

This document explains how the backtest and inference pipelines work, and how the Release-2 fundamental overlay integrates with each.

There are two runtime entry points:

| Entry Point | Purpose | Cadence |
|------------|---------|---------|
| `pipeline/main_inference.py` | Produce today's portfolio decisions | Daily |
| `pipeline/main_backtest.py` | Evaluate historical performance | Ad-hoc (development) |

Both share the same model stack (Ranker, Regressor, Classifier, SlotSelector) and now support an optional fundamental overlay that modifies BUY decisions based on pre-computed fundamental scores.

---

## 2. Inference Pipeline (`main_inference.py`)

### 2.1 Step-by-Step Flow

```
Step 1: Load config
    |
Step 2: Load latest raw price data (DataLoader)
    |  Fetches OHLCV bars for all tickers in the universe
    v
Step 3: Build features for today's date (OhlcvFeatureEngineer)
    |  Produces 14 price features (ret, SMA, vol, RSI, MACD, ranks)
    |  Filters to latest date only -> df_today
    v
Step 4: Load latest trained models (ModelManager)
    |  Ranker, Regressor, Classifier (LightGBM)
    v
Step 5: Predict signals for each ticker
    |  rank_score  = Ranker.predict(features)         cross-sectional rank
    |  pred_return = Regressor.predict(features)       expected 1-week return
    |  prob_up     = Classifier.predict_proba(features) probability of positive return
    v
Step 6: SlotSelector generates portfolio decisions
    |  Filters by prob_hurdle (>= 0.55)
    |  Computes opportunity = c_rank*z_rank + c_ret*z_ret + c_prob*z_prob
    |  Picks top 3 tickers -> BUY with equal weight (0.33 each)
    |  Remaining slots -> CASH / HOLD
    |  Output: List[Dict] with {ticker, action, weight}
    v
Step 7: Fundamental overlay (optional)
    |  Loads fundamental_scores.json (pre-computed quarterly)
    |  Calls apply_fundamental_overlay(decisions, scores, config)
    |  Maps each BUY to: STRONG_BUY / BUY / WARN / DOWNGRADE
    |  SELL and HOLD pass through unchanged
    |  Output: DataFrame with fundamental_action + score columns
    v
Step 8: Print decisions
    |  Shows base action -> fundamental_action with quality/trend scores
    v
Step 9: LLM analyst review (optional)
    |  Passes overlay-enhanced decisions to LLMAnalyst
    v
Step 10: Persist positions
    |  STRONG_BUY, BUY, WARN -> held in portfolio
    |  DOWNGRADE -> NOT held (treated as HOLD)
    |  SELL, HOLD -> NOT held
    |  Saved to data/current_positions.json
```

### 2.2 Fundamental Overlay Logic

The overlay is controlled by `config["fundamental"]["overlay"]["enabled"]` (default: `true`). When enabled:

1. Scores are loaded from `data/fundamentals/fundamental_scores.json`
2. Each ticker's BUY decision is classified using five rules:

| Rule | Condition | Result |
|------|-----------|--------|
| **R1** | BUY + quality >= 0.7 + value >= 0.6 + trend >= 0.5 | **STRONG_BUY** |
| **R2** | BUY + quality < 0.35 OR trend < 0.35 | **WARN** |
| **R3** | BUY + quality < 0.20 + trend < 0.25 | **DOWNGRADE** |
| **R3b** | BUY + piotroski_f < 3 + trend < 0.25 | **DOWNGRADE** |
| **R4** | SELL (any fundamentals) | **SELL** (never overridden) |
| **R5** | HOLD (any fundamentals) | **HOLD** (pass through) |

Rules are evaluated in priority order: R4 > R5 > R3 > R2 > R1 > default BUY.

3. The `fundamental_action` determines portfolio holding:
   - **STRONG_BUY**: Held. Highest conviction — price model and fundamentals agree.
   - **BUY**: Held. Normal price-model pick, fundamentals are neutral.
   - **WARN**: Held, but flagged. Price says BUY but fundamentals are weakening.
   - **DOWNGRADE**: **NOT held.** Fundamental risk is too high — BUY is converted to HOLD.
   - **SELL / HOLD**: Not held. Original price-model decision preserved.

### 2.3 Graceful Degradation

The overlay is wrapped in try/except at every level:
- If `fundamental_scores.json` does not exist -> skip overlay, use raw decisions
- If `load_fundamental_scores()` returns empty dict -> skip overlay
- If `apply_fundamental_overlay()` raises any exception -> log warning, use raw decisions
- If overlay is disabled in config -> skip entirely

The inference pipeline **never fails** due to missing fundamental data.

### 2.4 Position Persistence

Positions are saved to `data/current_positions.json` as `{ticker: weight}`. On the next inference run, these are loaded and passed to `selector.select()` so that hysteresis and turnover penalties can take effect across daily runs.

The effective action for persistence uses `fundamental_action` when the overlay is active:

```python
hold_actions = {"SELL", "HOLD", "DOWNGRADE"}
# Only tickers NOT in hold_actions get saved as positions
```

---

## 3. Backtest Pipeline (`main_backtest.py`)

### 3.1 Two Backtest Modes

#### Single-Split Backtest (`--mode backtest`, default)

```
Load config + price data + features
    |
    v
Split: df_train = [start, train_cutoff)    # default cutoff: 2023-01-01
       df_test  = [train_cutoff, end]
    |
    v
Load latest saved models (Ranker, Regressor, Classifier)
    |
    v
Optimize SlotSelector coefficients on df_train (no look-ahead)
    |
    v
Run Backtester.run(df_test) with optional fundamental overlay
    |
    v
Generate report (CSV, PNG equity curve, metrics)
```

#### Walk-Forward Backtest (`--mode wf-backtest`)

```
Load config + price data + features
    |
    v
Build fold schedule (expanding window):
    Fold 1: train [2015, 2018),  test [2018, 2019)
    Fold 2: train [2015, 2019),  test [2019, 2020)    <- COVID crash
    Fold 3: train [2015, 2020),  test [2020, 2021)
    Fold 4: train [2015, 2021),  test [2021, 2022)    <- rate-hike bear
    ...
    Fold N: train [2015, 2024),  test [2024, 2025)
    |
    v
For each fold:
    1. Train fresh models on fold's training window
    2. Optimize SlotSelector coefficients on training window
    3. Run Backtester.run(df_test) with optional fundamental overlay
    4. Collect equity curve and metrics
    |
    v
Stitch per-fold equity curves into one continuous curve
    |
    v
Compute aggregate metrics (Sharpe, CAGR, MaxDD, etc.)
    |
    v
Save results to logs/wf_backtest_results[_with_overlay].csv
Generate report (CSV, PNG, metrics)
```

### 3.2 Backtester Daily Loop (Inside `Backtester.run()`)

The `Backtester` uses a **staggered-bucket** design to simulate a rolling portfolio with 5-day holding periods:

```
For each trading day i:
    1. Select active bucket = buckets[i % 5]       # round-robin across 5 buckets
    2. Predict signals for all tickers today:
       rank_score  = Ranker.predict(features)
       pred_return = Regressor.predict(features)
       prob_up     = Classifier.predict_proba(features)
    3. SlotSelector.select(df_day) -> shared_target (3 slots: BUY/CASH)
    4. [If fundamental overlay enabled]:
       apply_fundamental_overlay(shared_target, fund_scores)
       DOWNGRADE tickers removed from target_tickers
    5. Compute PnL for ALL buckets (mark-to-market on today's returns)
    6. Rebalance active bucket: reconcile positions to target_tickers
       - Fee charged for each new position entry and exit
    7. Update equity curve and daily returns
```

**Why staggered buckets?** The models predict 1-week (5-day) forward returns. By splitting capital into 5 buckets and rebalancing one bucket per day, the backtester:
- Avoids concentrating all trades on one day
- Simulates a rolling portfolio where 1/5 of capital is refreshed daily
- Each bucket holds its positions for exactly 5 days before rebalancing

### 3.3 Fundamental Overlay in Backtest

The `--fundamental-overlay` CLI flag enables the overlay for backtesting:

```bash
# Price-only backtest (baseline)
python -m pipeline.main_backtest --mode backtest

# Price + fundamental overlay
python -m pipeline.main_backtest --mode backtest --fundamental-overlay

# Walk-forward with overlay
python -m pipeline.main_backtest --mode wf-backtest --fundamental-overlay

# Custom scores path
python -m pipeline.main_backtest --fundamental-overlay --fundamental-scores-path path/to/scores.json
```

**How it works:**

1. `_load_overlay_scores()` loads `data/fundamentals/fundamental_scores.json`
2. The scores dict is passed to `Backtester.__init__(fundamental_scores=...)`
3. Inside `Backtester.run()`, on each trading day after `selector.select()`:
   - `apply_fundamental_overlay(shared_target, fund_scores, config)` is called
   - The overlay classifies each BUY as STRONG_BUY / BUY / WARN / DOWNGRADE
   - Only STRONG_BUY, BUY, and WARN tickers remain in `target_tickers`
   - DOWNGRADE tickers are removed — the bucket goes to cash for that slot

**Important assumptions:**
- Fundamental scores are **static** throughout the backtest (computed once from the latest quarterly data). In production, scores would be updated quarterly after each filing season.
- This is an approximation. A more accurate backtest would recompute scores per quarter, but the current approach is sufficient for measuring the overlay's directional impact on Sharpe ratio.

### 3.4 A/B Comparison Workflow

To measure whether the fundamental overlay improves risk-adjusted returns:

```bash
# Step 1: Run baseline (price-only)
python -m pipeline.main_backtest --mode wf-backtest
# -> logs/wf_backtest_results.csv

# Step 2: Run with overlay
python -m pipeline.main_backtest --mode wf-backtest --fundamental-overlay
# -> logs/wf_backtest_results_with_overlay.csv

# Step 3: Compare Sharpe ratios
# Look at the "FULL" row in each CSV:
#   wf_backtest_results.csv         -> Sharpe (baseline)
#   wf_backtest_results_with_overlay.csv -> Sharpe (with overlay)
#
# AC-8 acceptance: Sharpe delta > 0.05
```

---

## 4. Data Contracts

### 4.1 SlotSelector Output

`SlotSelector.select()` returns a `List[Dict]` with exactly `max_slots` (3) entries:

```python
[
    {"ticker": "AAPL", "action": "BUY",  "weight": 0.33},
    {"ticker": "MSFT", "action": "BUY",  "weight": 0.33},
    {"ticker": "CASH", "action": "HOLD", "weight": 0.0},
]
```

### 4.2 Overlay Output

`apply_fundamental_overlay()` returns a `pd.DataFrame` with the original columns plus:

| Column | Type | Description |
|--------|------|-------------|
| `fundamental_action` | str | STRONG_BUY / BUY / WARN / DOWNGRADE / HOLD / SELL |
| `fundamental_quality` | float | quality_score [0, 1] (NaN if no score) |
| `fundamental_value` | float | value_score [0, 1] |
| `fundamental_trend` | float | trend_score [0, 1] |
| `fundamental_composite` | float | composite_score [0, 1] |

### 4.3 Fundamental Scores JSON

`data/fundamentals/fundamental_scores.json` structure:

```json
{
    "AAPL": {
        "composite_score": 0.82,
        "quality_score": 0.91,
        "value_score": 0.73,
        "trend_score": 0.85,
        "filing_date": "2026-01-31",
        "piotroski_f": 7
    },
    ...
}
```

Produced by `FundamentalScorer.save_scores_json()` after training via `--mode fundamental_scorer`.

### 4.4 Backtester Results

`Backtester.run()` returns a dict:

```python
{
    "equity_curve":  [20000.0, 20050.0, ...],   # portfolio value per day
    "daily_returns": [0.0025, -0.001, ...],      # daily pct returns
    "metrics": {
        "sharpe": 1.23,
        "max_drawdown": -0.15,
        "cagr": 0.12,
        "volatility": 0.18,
        "calmar": 0.80,
        "hit_rate": 0.54,
        "avg_daily_return": 0.0005,
        "total_return": 0.35,
    },
    "debug_log": [...]  # per (date, ticker) entries
}
```

---

## 5. Overlay Threshold Reference

All thresholds are configurable via `config["fundamental"]["overlay"]`:

| Threshold | Default | Used By |
|-----------|---------|---------|
| `strong_buy_quality_min` | 0.70 | R1: quality >= threshold for STRONG_BUY |
| `strong_buy_value_min` | 0.60 | R1: value >= threshold for STRONG_BUY |
| `strong_buy_trend_min` | 0.50 | R1: trend >= threshold for STRONG_BUY |
| `warn_quality_max` | 0.35 | R2: quality < threshold triggers WARN |
| `warn_trend_max` | 0.35 | R2: trend < threshold triggers WARN |
| `downgrade_quality_max` | 0.20 | R3: quality < threshold triggers DOWNGRADE |
| `downgrade_piotroski_max` | 3 | R3b: piotroski_f < threshold triggers DOWNGRADE |
| `downgrade_trend_max` | 0.25 | R3: trend < threshold triggers DOWNGRADE |

---

## 6. File Reference

| File | Lines | Role |
|------|-------|------|
| `pipeline/main_inference.py` | 261 | Daily inference with fundamental overlay |
| `pipeline/main_backtest.py` | 528 | Backtest with `--fundamental-overlay` flag |
| `pipeline/ohlcv/backtest/backtester.py` | 193 | Staggered-bucket backtester with overlay support |
| `pipeline/ohlcv/policy/slot_selector.py` | ~250 | 3-slot BUY/SELL/HOLD policy |
| `pipeline/fundamental_analysis/integration/overlay.py` | 258 | Overlay classification logic |
| `pipeline/fundamental_analysis/models/fundamental_scorer.py` | 458 | Produces fundamental_scores.json |

---

## 7. Known Limitations

1. **Static fundamental scores in backtest.** The backtest uses a single snapshot of fundamental scores for all dates. In reality, scores change quarterly. This approximation overstates the overlay's effect if a ticker's fundamentals changed significantly during the backtest window.

2. **`current_positions={}` in backtester.** The backtester always passes empty positions to `selector.select()`, so hysteresis and turnover penalty logic in SlotSelector is effectively dead code during backtests.

3. **No SELL override.** The overlay never upgrades a SELL to a BUY, even if fundamentals are excellent. This is by design (Rule 4: price model SELL is final).

4. **3-slot constraint.** The backtester always picks exactly 3 stocks. If all 3 are DOWNGRADE'd by the overlay, the entire portfolio goes to cash for that rebalancing day.
