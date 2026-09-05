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

# Release 3 — Intended Features & Implementation Logic

> **Audience:** Humans and AI coding agents working on this codebase.
> **Created:** 2026-04-10
> **Updated:** 2026-04-13 — 4.1.5 FeatureJoiner fix confirmed: 44 f_* columns, 53839 rows with fundamentals. Per-run dated logs live. data_loader.py empty-ticker guard added.
> **Status:** In Progress — P0 + 4.1.5 complete. Next: 4.2.3 LabelBuilder dropout, then P1 validation.

---

## 1. Executive Summary

Release 3 hardens the existing Release 1 & 2 codebase, fixes critical correctness issues in the ML training and backtesting pipeline, adds proper test coverage, and then extends the system with a new **LLM-powered research report layer** by integrating the separately developed `AI_stock_analysis` project.

**Philosophy:** No new features until existing code is validated and correct. Concrete code before new capabilities.

**Release 3 goals (in priority order):**

1. **Fix critical correctness bugs** — validation split, transaction cost model, no-op stubs
2. **Add test coverage** — unit and integration tests for core pipeline logic
3. **Validate Release 2 end-to-end** — train FundamentalScorer on real data, run combined backtest
4. **Security hygiene** — remove hardcoded API keys from settings.yaml
5. **Performance** — vectorize ratio calculator, fix O(n^2) label builder lookup
6. **Integrate AI_stock_analysis** — park skills/prompts under this repo, auto-generate research reports for pipeline BUY picks

---

## 2. Background: AI_stock_analysis vs. ai-investment-pipeline

### 2.1 Context

During Release 2 development, a separate project (`AI_stock_analysis/`) was built to generate institutional-grade equity research reports using Claude Opus with live web data. The reports produced (PLTR: 658 lines, MSFT: 509 lines) were high quality — covering fundamentals, technicals, analyst consensus, intraday signals, scenario analysis, and final verdicts with specific entry/exit levels.

This raised the question: **does the ai-investment-pipeline need to continue, given that an LLM can produce high-quality stock analysis directly?**

### 2.2 Conclusion: Different Tools for Different Problems

After a comprehensive code review of all 10,607 lines of the pipeline, the conclusion is that these projects solve fundamentally different problems and are **complementary, not competing**.

| Dimension | AI_stock_analysis | ai-investment-pipeline |
|-----------|-------------------|----------------------|
| **Output** | Human-readable research report (Markdown) | Machine-actionable BUY/SELL/HOLD signals |
| **Scope** | 1 ticker per run, manually triggered | 30 tickers simultaneously, daily |
| **Decision maker** | Human reads report, decides | System decides, human executes |
| **Backtestable** | No (stateless, no historical memory) | Yes (walk-forward, multi-year, measurable) |
| **Learns from history** | No (LLM training cutoff only) | Yes (trained ML models on 10yr data) |
| **Cross-sectional** | No (evaluates one stock in isolation) | Yes (LambdaRank compares all stocks daily) |
| **Portfolio management** | No (no position sizing, turnover, cash) | Yes (SlotSelector, 3-slot portfolio, cash-as-virtual-stock) |
| **Cost to run** | ~$0.50-$8 in API tokens per report | Free after training (local LightGBM inference) |
| **Time per analysis** | 5-10 minutes per ticker (web scraping) | <1 second for full 30-stock universe |
| **Key question answered** | "What does the market say about PLTR today?" | "If I followed this strategy for 10 years, would I have made money?" |

### 2.3 The Synthesis: LLM-Augmented Quantitative Pipeline

Release 3 combines both by making the AI_stock_analysis prompt/skill an integrated component of the pipeline. When the pipeline recommends BUY on a stock, the system auto-generates a human-readable research report explaining *why* — providing the best of both worlds: machine decisions with human-readable justification.

---

## 3. Codebase Assessment (As of Release 2)

### 3.1 What Works (Validated)

- **SEC EDGAR ETL pipeline**: 503 S&P 500 tickers, 21,238 snapshots, 16 XBRL concepts, 45 fundamental features. Ran end-to-end with real data (28s runtime).
- **OHLCV feature engineering**: 14 price features (returns, SMAs, RSI, MACD, volume z-score, cross-sectional ranks). Runs daily via yfinance.
- **Model training**: LightGBM Ranker (LambdaRank) + Regressor + Classifier train successfully on price data.
- **Single-split backtest**: Runs to completion with equity curve, metrics, and debug CSV.
- **Walk-forward backtest**: Expanding-window folds with per-fold model retraining and coefficient optimization.
- **Model persistence**: Versioned .pkl files with JSON metadata sidecars tracking feature names and backend.
- **Multi-backend support**: LightGBM, XGBoost, sklearn GradientBoosting, sklearn RandomForest — all swappable via config.
- **LLM analyst**: Google Gemini integration for advisory review of BUY picks (advisory only, never overrides model).
- **Documentation**: 2,200+ lines of release notes across 5 markdown files.

### 3.2 What Does NOT Work (Unvalidated / Broken)

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| **Validation split** | **CRITICAL** | `lightgbm_models.py:112`, `fundamental_scorer.py:240` | `valid_sets=[train_data]` — training set used as validation set. Early stopping is meaningless; model selection is compromised. Affects all 4 models (ranker, regressor, classifier, fundamental scorer). |
| **Turnover penalty is a no-op** | **CRITICAL** | `slot_selector.py:236` | `_turnover_penalty()` returns `0.0` always. Config has `turnover_penalty_bps: 10` but it is never applied. Backtest results are overly optimistic. |
| **Hysteresis is a no-op** | **HIGH** | `slot_selector.py:224` | `_apply_hysteresis()` returns `selected` unchanged. Position persistence logic exists in `main_inference.py` but is never used in backtesting (`current_positions={}` always passed). |
| **Transaction costs wrong in backtest** | **HIGH** | `backtester.py:173` | Charges flat `$10` per trade regardless of position size. Config defines `spread_bps: 5`, `slippage_bps: 10`, `commission_bps: 1` (16 bps total) but these are only used for classifier label thresholds, never in PnL. |
| **FundamentalScorer never trained** | **HIGH** | `fundamental_scorer.py` | Code complete but never executed with real data. Requires price data parquet for 6-month forward-return labels. |
| **Fundamental overlay never tested E2E** | **HIGH** | `overlay.py` | Depends on `fundamental_scores.json` which doesn't exist without a trained scorer. |
| **Fundamental features stale in backtest** | **MEDIUM** | `backtester.py` | Uses single snapshot of fundamental scores, not time-varying quarterly updates. |
| **Feature schema stale** | **LOW** | `feature_schema.py` | Lists 11 fundamental features; actual count is 45. |
| **API keys hardcoded** | **MEDIUM** | `config/settings.yaml` | Google API key, Alpha Vantage key, News API key committed in plaintext. |
| **`RECOMPUTE_COEFFS = True` hardcoded** | **LOW** | `main_backtest.py:49` | Module-level flag forces coefficient re-optimization on every single-split backtest run. Should be a CLI arg. |
| **LSTM config unused** | **LOW** | `config/settings.yaml` | LSTM hyperparameters defined but no LSTM implementation exists anywhere. |

### 3.3 P0 Bug Fix Status (Updated 2026-04-13)

All four P0 bugs from section 3.2 were fixed in the initial implementation pass on 2026-04-13.

| Fix | File(s) | Status |
|-----|---------|--------|
| Validation split — all 4 models | `lightgbm_models.py`, `xgboost_models.py`, `fundamental_scorer.py` | ✅ DONE |
| Proportional transaction cost model | `backtester.py` | ✅ DONE |
| Turnover penalty (was always 0.0) | `slot_selector.py` | ✅ DONE |
| Hysteresis + thread `current_positions` | `slot_selector.py`, `backtester.py` | ✅ DONE |

First training run after the fixes (`python -m pipeline.main_train`, 2026-04-13 22:43) confirmed the validation split is working: each model now reports separate `val` metrics, and early stopping fires on held-out loss well before `num_boost_round=300`. However, the run exposed three new bugs documented in section 3.5 below.

---

### 3.4 Performance Issues

| Issue | Location | Impact |
|-------|----------|--------|
| `ratio_calculator.py` uses `.apply(lambda r: ...)` for all 20+ ratios | `ratio_calculator.py:66-230` | ~100x slower than vectorized pandas. Blocks S&P 500 scale. |
| `accruals.py` uses `.apply()` for accrual calculation | `accruals.py:51` | Same pattern, same fix. |
| `trend_features.py` margin trend uses manual sliding-window loop | `trend_features.py:103-128` | ~10x slower than vectorized approach. |
| `FundamentalLabelBuilder._asof_price_lookup()` has O(n^2) re-alignment | `label_builder.py:198-205` | Iterates merged rows with `.iloc[idx]`. Slow for 21K snapshots. |

### 3.5 Test Coverage (Current: Near Zero)

| File | Lines | What It Tests |
|------|-------|--------------|
| `pipeline/fundamental_analysis/tests/test_xbrl_parser.py` | 42 | XBRL parsing with synthetic XML |
| `test_merge_fix.py` | 144 | merge_asof sorting fix with synthetic data |
| `test_merge_groupby.py` | ~100 | Additional merge test |

**Missing tests (critical gaps):**
- No tests for label building (OHLCV or fundamental)
- No tests for feature engineering (ratio_calculator, piotroski, sector_relative)
- No tests for model training/prediction cycle
- No tests for SlotSelector logic (opportunity scoring, coefficient optimization)
- No tests for backtester (staggered bucket, PnL calculation, equity stitching)
- No tests for fundamental overlay rules (STRONG_BUY/WARN/DOWNGRADE classification)

### 3.6 Newly Discovered Issues (Post-P0 Training Run, 2026-04-13)

The first `main_train.py` run after the P0 fixes exposed three previously hidden bugs. These are documented fully in sections 4.1.5 and 4.2.3.

| Issue | Severity | Discovered | Location | Description |
|-------|----------|------------|----------|-------------|
| **FeatureJoiner: 0 fundamental rows merged** | **CRITICAL** | 2026-04-13 | `feature_joiner.py`, `ratio_calculator.py`, `accruals.py`, `trend_features.py` | `Rows with ≥1 fundamental feature: 0` — all 76,007 OHLCV rows had zero fundamental data. Root cause: `pd.NA` in `.apply()` lambdas produced `object` dtype columns, dropped as non-numeric. Secondary: `validate_merged_features` checked `canonical_*` prefix (never exists). **Fixed 2026-04-13. Confirmed: 44 f_* columns, 53839 rows with fundamentals.** |
| **LabelBuilder: 77% of training rows dropped** | **HIGH** | 2026-04-13 | `label_builder.py` (OHLCV) | 40,298 of 52,187 rows (77%) fail forward-return label assignment. For 30 tickers over 8 years of daily data only ~150 rows should be unlabelled (last 5 days per ticker). Root cause unknown — likely exact-date mismatch in the forward-price lookup rather than a genuine data gap. |
| **Regressor and Classifier quality near-random** | **HIGH** | 2026-04-13 | `lightgbm_models.py` | Regressor stops at iteration 3 (val rmse=0.0837). Classifier val binary_logloss=0.718 > ln(2)=0.693 (worse than random). Both are **symptoms** of the FeatureJoiner bug (no fundamental signal) and the LabelBuilder dropout (noisy/insufficient labels), not independent model bugs. Will re-evaluate after those two fixes. |

---

## 4. Release 3 Feature List (Priority Order)

### Priority Tiers

| Tier | Theme | Rationale | Status |
|------|-------|-----------|--------|
| **P0** | Fix critical correctness bugs | Pipeline produces incorrect results without these fixes | ✅ **DONE** (2026-04-13) |
| **P1** | Validate Release 2 end-to-end | 4,000+ lines of untested fundamental code | ✅ **DONE** (2026-04-17) — All 3 sub-items complete. See `reports/backtest_reports/backtest_comparison.md`. |
| **P2** | Test coverage | Prevent regressions, enable confident iteration | ✅ **DONE** (2026-04-17) — 25 integration tests pass. See `tests/`. |
| **P3** | Security & engineering hygiene | API keys, dead code, config cleanup | ✅ **DONE** (2026-04-18) — API keys moved to env vars, LSTM dead code removed, feature schema updated to 44 features, `RECOMPUTE_COEFFS` promoted to CLI flag. |
| **P4** | Performance optimization | Enable S&P 500 scale | ✅ **DONE** (2026-04-18) — All `.apply()` calls vectorized; O(n²) label lookup fixed. |
| **P5** | AI_stock_analysis integration | New capability: LLM research reports for BUY picks | ⬜ Pending |

---

### 4.1 P0 — Fix Critical Correctness Bugs

> **Status: ✅ DONE (2026-04-13).** Items 4.1.1–4.1.4 are implemented. See section 3.3 for verification evidence from the first training run. Item 4.1.5 was discovered during that run and is the current highest-priority work item.

#### 4.1.1 Fix LightGBM Validation Split

**Problem:** All 4 LightGBM models (ranker, regressor, classifier, fundamental scorer) use `valid_sets=[train_data]` — the training set as the validation set. This means:
- Early stopping optimizes against training loss (overfitting).
- Model selection within each walk-forward fold is compromised.
- You cannot know if models are overfitting because the "validation" metric always looks good.

**Fix:**
- In `LightGBMModel.train()` (`lightgbm_models.py`): Split incoming training data into train (80%) and validation (20%) using a time-based split (not random). Pass the validation portion as `valid_sets=[val_data]`.
- In `XGBoostModel.train()` (`xgboost_models.py`): Same pattern — `evals = [(dval, "val")]` instead of `[(dtrain, "train")]`.
- In `FundamentalScorer.fit()` (`fundamental_scorer.py`): Same fix for main model and all 3 sub-models.
- Make `early_stopping_rounds` default to a sensible value (e.g., 50) instead of `None`.

**Files to modify:**
- `pipeline/ohlcv/models/lightgbm_models.py` — `train()` method
- `pipeline/ohlcv/models/xgboost_models.py` — `train()` method
- `pipeline/fundamental_analysis/models/fundamental_scorer.py` — `fit()` and `_train_sub_model()` methods

**Acceptance criteria:** Training logs show separate train and validation loss. Early stopping triggers on validation loss. Walk-forward backtest Sharpe ratio may decrease (overfitting reduction).

> **✅ DONE (2026-04-13).** `_make_time_split()` helper added to `lightgbm_models.py` and `xgboost_models.py`. All four models split on unique dates (80/20), use `valid_sets=[val_data]` with `reference=train_data`. `early_stopping_rounds` defaults to 50. Confirmed in training log: ranker best_iter=38 (val ndcg@1=0.650), regressor best_iter=3 (val rmse=0.0837), classifier best_iter=10 (val binary_logloss=0.718).

---

#### 4.1.2 Implement Proportional Transaction Cost Model in Backtester

**Problem:** The backtester charges a flat `$10` per trade via `self.trade_fee`, regardless of position size. The config defines realistic proportional costs (`spread_bps: 5`, `slippage_bps: 10`, `commission_bps: 1` = 16 bps) but these are only used for the classifier label threshold, never in actual PnL computation.

**Fix:**
- In `Backtester._reconcile_bucket()` (`backtester.py`): Replace flat `$10` fee with proportional cost:
  ```
  total_cost_bps = config["costs"]["spread_bps"] + config["costs"]["slippage_bps"] + config["costs"]["commission_bps"]
  cost_per_trade = bucket.capital * weight * total_cost_bps / 10000.0
  ```
- Charge costs on both entry (new positions) and exit (closed positions).
- Remove the `trade_fee` constructor parameter (or keep as fallback).

**Files to modify:**
- `pipeline/ohlcv/backtest/backtester.py` — `__init__()` and `_reconcile_bucket()`

**Acceptance criteria:** Backtest PnL includes proportional transaction costs matching the config. Total return and Sharpe ratio will decrease (more realistic).

> **✅ DONE (2026-04-13).** `_reconcile_bucket()` in `backtester.py` now reads `config["costs"]` at `__init__` time. Exit cost = `bucket.capital × held_weight × total_bps / 10_000`. Entry cost = `bucket.capital × target_weight × total_bps / 10_000`. `trade_fee` parameter kept as `None` default for backward compatibility.

---

#### 4.1.3 Implement Turnover Penalty in SlotSelector

**Problem:** `_turnover_penalty()` returns `0.0` always. The opportunity score formula subtracts the turnover penalty, but since it's zero, there's no cost to churning positions daily.

**Fix:**
- In `SlotSelector._turnover_penalty()` (`slot_selector.py`): For tickers NOT in `current_positions`, apply a penalty proportional to `turnover_penalty_bps` from config. For tickers already held, penalty is zero (incentivize holding).
  ```python
  def _turnover_penalty(self, df, current_positions):
      penalty_bps = self.turnover_penalty_bps
      penalty = pd.Series(0.0, index=df.index)
      for idx, row in df.iterrows():
          if row["ticker"] not in current_positions:
              penalty.at[idx] = penalty_bps / 10000.0
      return penalty
  ```

**Files to modify:**
- `pipeline/ohlcv/policy/slot_selector.py` — `_turnover_penalty()`

**Acceptance criteria:** Stocks already held receive a preference bonus (zero penalty) vs. new positions. Position turnover rate decreases measurably in backtest.

> **✅ DONE (2026-04-13).** Vectorized implementation: `is_new = ~df["ticker"].isin(current_positions)`, penalty = `is_new * turnover_penalty_bps / 10_000`. Replaces the `for idx, row in df.iterrows()` loop suggested in the original spec.

---

#### 4.1.4 Implement Hysteresis in SlotSelector

**Problem:** `_apply_hysteresis()` returns the selected list unchanged. Without hysteresis, a stock that barely loses its #3 ranking gets immediately replaced, generating unnecessary turnover.

**Fix:**
- In `SlotSelector._apply_hysteresis()` (`slot_selector.py`): If a currently-held ticker was ranked just below the cutoff (e.g., position #4 or #5), keep it instead of swapping. Require a minimum improvement margin (`swap_buffer`) for a new ticker to displace an existing position.
  ```python
  def _apply_hysteresis(self, selected, df, current_positions):
      if not current_positions:
          return selected
      # For each slot, if current holder is close to the cutoff, keep them
      final = list(selected)
      held_tickers = set(current_positions.keys())
      for i, ticker in enumerate(final):
          if ticker == "CASH" or ticker in held_tickers:
              continue
          # Check if there's a held ticker that was displaced by a small margin
          displaced_held = held_tickers - set(final)
          for held in displaced_held:
              held_opp = df[df["ticker"] == held]["adj_opportunity"].values
              new_opp = df[df["ticker"] == ticker]["adj_opportunity"].values
              if len(held_opp) > 0 and len(new_opp) > 0:
                  if new_opp[0] - held_opp[0] < self.swap_buffer:
                      final[i] = held
                      break
      return final
  ```

**Files to modify:**
- `pipeline/ohlcv/policy/slot_selector.py` — `_apply_hysteresis()`
- `pipeline/ohlcv/backtest/backtester.py` — pass `current_positions` from previous day (not `{}`)

**Acceptance criteria:** Position turnover rate decreases. Positions are held for multiple days when ranking differences are small. Backtest debug log shows hysteresis in action.

> **✅ DONE (2026-04-13).** `_apply_hysteresis()` now checks `margin = new_opp - held_opp`; keeps held ticker when `margin < self.swap_buffer (0.005)`. `backtester.run()` changed from `current_positions={}` to `current_positions=active_bucket.positions`.

---

#### 4.1.5 Fix FeatureJoiner — Fundamental Features Not Merging *(Discovered 2026-04-13)*

> **✅ DONE (2026-04-13).** Root cause identified and fixed. Confirmed: 44 `f_*` columns, 53,839 rows with ≥1 fundamental feature.

**Problem (resolved):** The `FeatureJoiner` produced zero rows with fundamental data:

```
Rows with ≥1 fundamental feature: 0
Rows with only price features: 76007
```

The merged DataFrame has 93 columns (14 OHLCV + 79 others), but all 37 fundamental `f_*` columns arrive as `object` dtype (entirely `NaN`). They are immediately dropped by the `main_train.py` non-numeric filter, so the three models trained on 2026-04-13 use only 21 OHLCV features — the entire Release 2 fundamental pipeline contributes nothing.

**Why this matters:**
- All trained models (ranker, regressor, classifier) saved after this run are OHLCV-only despite the metadata claiming 21 combined features.
- The poor regressor (stops at iter 3) and classifier (logloss > random) results are direct consequences of missing fundamental signal and are expected to improve once this is fixed.
- 4.2.1 (FundamentalScorer training) and 4.2.2 (combined backtest) cannot be meaningfully attempted until fundamental features are present in the feature matrix.

**Root cause candidates (investigate in order):**

1. **Ticker format mismatch.** The OHLCV pipeline tracks 30 tickers (`AAPL`, `MSFT`, etc.). The fundamental pipeline covers 503 tickers. If the ticker strings differ in any way (exchange suffix, case, whitespace), `merge_asof` will find no key matches. Check:
   ```python
   price_tickers = set(df_price["ticker"].unique())
   fund_tickers = set(df_fund["ticker"].unique())
   print(price_tickers & fund_tickers)  # should be non-empty
   ```

2. **Date ordering or key mismatch in `merge_asof`.** `merge_asof` requires both DataFrames to be sorted ascending by the join key before the call. If `df_fund` is sorted descending or has `NaT` dates, the asof join silently produces all-NaN matches. Check the sort order and `NaT` counts in `filing_date`.

3. **`left_by` / `right_by` (ticker grouping) misconfigured.** `pd.merge_asof(..., by="ticker")` requires exact string equality in the `by` column. A single extra space or encoding difference in a ticker causes it to match nothing. Verify the actual bytes: `df_fund["ticker"].str.encode("utf-8").unique()[:5]`.

4. **Column dtype mismatch causing silent NaN propagation.** If `filing_date` in the fundamental DataFrame is `object` dtype rather than `datetime64`, the asof join may run without error but produce no temporal overlap. Check `df_fund.dtypes["filing_date"]`.

**Files to investigate:**
- `pipeline/fundamental_analysis/integration/feature_joiner.py` (or equivalent) — the `merge_asof` call
- `pipeline/main_train.py` — `train_fundamental_models_with_combined_features()`, step 3

**Acceptance criteria (met):** Confirmed output from `main_train.py --mode fundamental_full` (2026-04-13 23:27 run):
```
f_* fundamental columns found: 44
Rows with ≥1 fundamental feature: 53839
Rows with only price features: 19197
```
Also fixed: `data_loader.py` now guards against empty yfinance responses (e.g. NVDA `KeyError: 'date'`).

---

### 4.2 P1 — Validate Release 2 End-to-End

> **Status: ✅ DONE (2026-04-17).** All 3 items complete. LabelBuilder dropout fixed (145/50K dropped vs. 40K before). FundamentalScorer trained on 503 S&P 500 tickers. Walk-forward A/B comparison produced — overlay improves MaxDD (-62.12% → -58.55%) at a modest Sharpe cost (0.791 → 0.750). Full comparison in `reports/backtest_reports/backtest_comparison.md`.

#### 4.2.1 Train FundamentalScorer on Real Data

**Problem:** The FundamentalScorer (458 lines, quality/value/trend sub-models) has never been trained on real data. It requires:
1. Fundamental training data parquet (exists: 21,238 snapshots from SEC EDGAR)
2. Price data parquet (needs to exist on disk for 6-month forward-return labels)

**Steps:**
1. Ensure price data is persisted as parquet by DataLoader (may need `df_prices.to_parquet()`).
2. Run `python -m pipeline.main_train --mode both` (includes scorer as of 2026-04-17).
3. Verify `data/fundamentals/fundamental_scorer.pkl` and `data/fundamentals/fundamental_scores.json` are produced.
4. Check that composite/quality/value/trend scores are in [0,1] range with reasonable distributions.

**Files modified (2026-04-16):**
- `pipeline/ohlcv/dataset/data_loader.py` — `load_price_data()` now persists price data to `data/ohlcv/price_data.parquet` on first load, matching `FundamentalLabelBuilder._PRICE_DATA_SEARCH_PATHS`. Note: `train_fundamental_scorer` in main_train.py also passes `price_data` directly to `FundamentalLabelBuilder`, so it works without disk persistence too.

**Action required:** Run `python -m pipeline.main_train --mode both`

> **Note (2026-04-17):** `--mode both` now runs all four training stages in sequence:
> price models → EDGAR ETL → combined feature models → fundamental scorer.
> There is no longer a need to run `--mode fundamental_scorer` separately.

**Acceptance criteria:** FundamentalScorer trained. Scores JSON at `data/fundamentals/fundamental_scores.json` contains entries for 400+ tickers. Score distributions are not degenerate (not all 0.5).

---

#### 4.2.2 Run Combined Backtest (Price + Fundamental Overlay)

**Status (2026-04-16):** Baseline run complete. The `--fundamental-overlay` run on 2026-04-16 completed but was a no-op — `fundamental_scores.json` did not exist, so `load_fundamental_scores()` returned `{}` and the overlay warning fired. Results are identical to price-only. Baseline results saved to `logs/wf_backtest_results.csv`.

**Baseline (price-only) results:**

| Metric | Value |
|--------|-------|
| Sharpe (full stitched) | 0.791 |
| CAGR | 24.00% |
| Max Drawdown | -62.12% |
| Total Return | 446.28% |
| HitRate | 53.52% |

Notable folds: COVID recovery 2020 (+150%), 2023 bull (+67%); rate-hike bear 2021 (-18%), 2022 (-15%).

**Remaining steps (completed 2026-04-17):**
1. ✅ Train FundamentalScorer — `python -m pipeline.main_train --mode both` (scorer now included)
2. ✅ Re-run overlay backtest — `python -m pipeline.main_backtest --mode wf-backtest --fundamental-overlay`
3. ✅ Compare to `logs/wf_backtest_results.csv` baseline
4. ✅ Full A/B table in `reports/backtest_reports/backtest_comparison.md`

**Acceptance criteria:** Walk-forward backtest completes with overlay enabled. Debug CSV shows `fundamental_action` column. A/B comparison table produced in `backtest_comparison.md`.

---

#### 4.2.3 Investigate and Fix LabelBuilder 77% Row Dropout *(Discovered 2026-04-13)*

> **✅ FIXED (2026-04-16).** Root cause identified and fixed. New `_cross_section_rank()` helper replaces the broken qcut-in-transform pattern.

**Problem:** The OHLCV `LabelBuilder` drops 77% of training rows when computing 1-week forward returns:

```
Rows before dropping NaN labels: 52187
Rows after dropping NaN labels: 11889   (40,298 rows dropped)
```

For 30 tickers with roughly 8 years of daily training data (~2,016 rows each), the expected dropout is at most ~150 rows (the last 5 trading days per ticker where no forward price exists). Losing 40,298 rows (77%) indicates the forward-price lookup is failing for the vast majority of rows.

**Why this matters:**
- With only 11,889 labeled samples from a possible 52,187, the training dataset is ~4× smaller than it should be. This directly degrades model quality (more noise, less signal).
- Combined with the FeatureJoiner bug (no fundamental features), this is a second independent cause of the poor regressor/classifier metrics observed.

**Root cause (confirmed 2026-04-16):**

`pd.qcut(x, q=5, labels=False, duplicates="drop")` called inside `groupby("date").transform()` returns a `Categorical` (or nullable Integer) dtype. `transform` cannot broadcast a `Categorical` back to a `float64` column — it silently fills NaN for **every row in every date group**, not just the 5 expected per-ticker boundary rows. This caused 77% dropout via the subsequent `dropna(subset=["rank_label_1w"])`.

The `fwd_ret_1w` computation via `df.groupby("ticker")["adj_close"].shift(-5)` was already correct (per-ticker).

**Fix applied:** New `_cross_section_rank(x, n_bins=5)` helper function in `label_builder.py`:
1. Drops NaN from each date group before calling `pd.qcut`
2. Explicitly casts result to `float64` and reindexes to original group index
3. Handles groups with fewer than `n_bins` valid values → all NaN (correct behavior)

**Acceptance criteria (met):** Expected dropout after fix: <0.3% (~150 rows / ~52K from last 5 rows per ticker). Training dataset should grow from ~11K to ~50K+ samples.

---

### 4.3 P2 — Test Coverage

> **Status: ✅ DONE (2026-04-17).** 4.3.1 unit tests skipped per release scope. 4.3.2 integration tests implemented — 25 tests across 3 files, all passing in 1.5s. Run with `pytest tests/ -v`.

#### 4.3.1 Unit Tests for Core Components (Skipped all Unit Test at this release-3)

Add tests under `pipeline/tests/` (or `tests/` at project root) covering:

| Component | Test File | What to Test |
|-----------|-----------|-------------|
| `ratio_calculator` | `test_ratio_calculator.py` | All 20 ratios with synthetic data. Division by zero. Missing columns. |
| `piotroski` | `test_piotroski.py` | All 9 signals. Edge cases (first row, NaN values). Known F-score for hand-calculated input. |
| `sector_relative` | `test_sector_relative.py` | Z-score correctness. Min sector size enforcement. |
| `accruals` | `test_accruals.py` | Accrual formula correctness. Z-scoring. |
| `trend_features` | `test_trend_features.py` | QoQ growth. Rolling growth. OLS margin trend slope. |
| `LabelBuilder` (OHLCV) | `test_label_builder_ohlcv.py` | 1-week forward return calculation. Classifier threshold (16 bps). |
| `FundamentalLabelBuilder` | `test_label_builder_fundamental.py` | 6-month forward return. Quintile assignment per quarter. |
| `SlotSelector` | `test_slot_selector.py` | Opportunity scoring formula. Prob hurdle filtering. Cash fallback. Turnover penalty (after fix). Hysteresis (after fix). |
| `overlay` | `test_overlay.py` | STRONG_BUY / WARN / DOWNGRADE rules. Threshold edge cases. SELL never overridden. |
| `BacktestMetrics` | `test_metrics.py` | Sharpe, CAGR, max drawdown, hit rate with known equity curves. |

#### 4.3.2 Integration Tests

| Test | What It Covers |
|------|---------------|
| `test_train_predict_cycle.py` | Train LightGBM ranker/regressor/classifier on synthetic data, predict, verify output shapes and ranges. |
| `test_backtest_e2e.py` | Run a mini backtest (50 days, 5 tickers) and verify equity curve length, metric ranges, debug log structure. |
| `test_feature_joiner.py` | merge_asof alignment with synthetic daily + quarterly data. Verify no look-ahead leakage. |

**Acceptance criteria:** `pytest` passes with >80% line coverage on core modules. All P0 fixes have corresponding regression tests.

#### How to Run the Tests

From the project root (`ai-investment-pipeline/`):

```bash
# Run the full suite (25 tests, ~1.2s)
pytest tests/ -v

# Run a single test file
pytest tests/test_train_predict_cycle.py -v
pytest tests/test_backtest_e2e.py -v
pytest tests/test_feature_joiner.py -v

# Run a single test by name
pytest tests/test_feature_joiner.py::test_no_lookahead_leakage -v

# Run with short traceback on failure
pytest tests/ -v --tb=short

# Stop on first failure
pytest tests/ -v -x
```

Expected output:
```
25 passed in ~1.2s
```

> **✅ DONE (2026-04-17).** Three integration test files created under `tests/`:
> - `test_train_predict_cycle.py` (7 tests) — ModelFactory, LightGBM ranker/regressor/classifier train + predict shapes, probability ranges
> - `test_backtest_e2e.py` (12 tests) — 30-day mini backtest: equity curve length, metric ranges, debug log columns, initial capital
> - `test_feature_joiner.py` (6 tests) — merge_asof row count, no-lookahead leakage, no ticker_x/ticker_y, NaN for missing tickers, backward fill between filings
>
> Infrastructure: `pytest.ini` (`testpaths = tests`, `pythonpath = .`), `tests/conftest.py` (session-scoped `cfg`, `price_df`, `trained_models`, `price_df_factory` fixtures).

---

### 4.4 P3 — Security & Engineering Hygiene

> **Status: ✅ DONE (2026-04-18).** Both items complete. See detailed completion notes below.

#### 4.4.1 Move API Keys to Environment Variables

**Problem:** `config/settings.yaml` contained hardcoded API keys:
- `alpha_vantage.api_key: "FIBYWSSS2U4G7PG4"`
- `google_api.key: "AIzaSyDqVRrl3BkDG6MO8Hg_3mlk-YXUdciICw4"`
- `news_api.key: "70f34d278c81483182ba5a8064085657"`

**Fix:**
- Replace with `${ENV_VAR_NAME}` placeholders in settings.yaml.
- Add a `config/env.example` file documenting required environment variables.
- Update `utils.py` `load_config()` to resolve `${...}` patterns from `os.environ`.
- Add `.env` to `.gitignore`.
- Rotate all exposed keys immediately.

**Files to modify:**
- `config/settings.yaml` — replace key values with `${ALPHA_VANTAGE_API_KEY}` etc.
- `pipeline/utils/utils.py` — add env var resolution in `load_config()`
- `.gitignore` — add `.env`
- New file: `config/env.example`

> **✅ DONE (2026-04-18).** All four files changed:
> - `config/settings.yaml`: three keys replaced with `${ALPHA_VANTAGE_API_KEY}`, `${GOOGLE_API_KEY}`, `${NEWS_API_KEY}`
> - `pipeline/utils/utils.py`: `_resolve_env_vars()` helper added; `load_config()` reads the full YAML as a string, substitutes all `${VAR}` patterns via regex before `yaml.safe_load()`. If a var is unset, the placeholder is left as-is and a warning is printed to stderr — the process does not crash, allowing the pipeline to run in environments where not all APIs are needed.
> - `.gitignore`: `.env` and `.env.*` added (with `!.env.example` exception).
> - `config/env.example`: new file with copy-paste instructions and signup URLs for all three keys.
>
> **Usage:**
> ```bash
> cp config/env.example .env
> # fill in .env with real keys
> source .env
> python -m pipeline.main_inference
> ```

---

#### 4.4.2 Clean Up Dead Code and Stale Config

- Remove LSTM config block from `settings.yaml` (no implementation exists).
- Update `feature_schema.py` to list all 44 fundamental features (was 11).
- Move `RECOMPUTE_COEFFS` from module-level constant to CLI flag in `main_backtest.py`.
- Remove `ASK_USER_INPUT` flag (interactive input is not compatible with automated backtesting).

> **✅ DONE (2026-04-18).**
>
> **LSTM block removed** (`config/settings.yaml`): The `model.lstm` block (8 lines: `seq_len`, `hidden_size`, `num_layers`, `dropout`, `lr`, `batch_size`, `epochs`, `early_stop_patience`) had no corresponding implementation anywhere in the codebase. Removed entirely to eliminate config drift.
>
> **`feature_schema.py` updated** (`pipeline/ohlcv/dataset/feature_schema.py`): `FUNDAMENTAL_FEATURES` expanded from 11 → 44 entries, matching the actual columns produced by `FundamentalsFeatureEngineer`. The full set covers: 11 profitability ratios, 4 leverage/solvency ratios, 1 liquidity ratio, 4 efficiency/size metrics, 1 valuation ratio, 2 accruals features, 4 Piotroski sub-scores, 13 growth/trend features (QoQ, YoY, rolling, OLS margin slope), and 5 sector-relative z-scores. `ALL_FEATURES` count updated from 25 → 58.
>
> **`RECOMPUTE_COEFFS` promoted to CLI flag** (`pipeline/main_backtest.py`): Module-level constants `RECOMPUTE_COEFFS = True` and `ASK_USER_INPUT = False` removed. Replaced by `--no-recompute-coeffs` argparse flag (default: recompute). The `elif ASK_USER_INPUT` branch is removed entirely. Usage:
> ```bash
> # Default — recompute coefficients (same as before)
> python -m pipeline.main_backtest --mode wf-backtest
>
> # Fast mode — skip coefficient optimisation
> python -m pipeline.main_backtest --mode wf-backtest --no-recompute-coeffs
> ```

---

### 4.5 P4 — Performance Optimization

#### 4.5.1 Vectorize ratio_calculator.py

**Problem:** Every ratio uses `.apply(lambda r: ...)` which is ~100x slower than vectorized pandas.

**Fix:** Replace all `.apply()` calls with vectorized operations. The `piotroski.py` file already uses `np.where()` correctly — follow that pattern:

```python
# Before (slow):
out["f_net_margin"] = out.apply(
    lambda r: (r.net_income / r.revenue) if pd.notnull(r.revenue) and r.revenue != 0 else pd.NA,
    axis=1,
)

# After (fast):
out["f_net_margin"] = np.where(
    out["revenue"].notna() & (out["revenue"] != 0),
    out["net_income"] / out["revenue"],
    pd.NA,
)
```

Apply this pattern to all 20+ ratios.

**Files to modify:**
- `pipeline/fundamental_analysis/features/ratio_calculator.py` — all `.apply()` calls
- `pipeline/fundamental_analysis/features/accruals.py` — `_accrual` function
- `pipeline/fundamental_analysis/features/trend_features.py` — `_pct_change` lambdas

---

#### 4.5.2 Vectorize FundamentalLabelBuilder._asof_price_lookup()

**Problem:** The re-alignment loop iterates every row of the merged DataFrame with `.iloc[idx]`. This is O(n^2) for 21K snapshots.

**Fix:** Use vectorized index assignment:
```python
# Instead of iterating:
result = merged.set_index("_row_idx")["adj_close"].reindex(range(len(lookup)))
```

**Files to modify:**
- `pipeline/fundamental_analysis/models/label_builder.py` — `_asof_price_lookup()`

---

#### ✅ P4 Completion Notes (2026-04-18)

All four performance targets implemented:

**4.5.1 — ratio_calculator.py (fully rewritten)**
- Added `_safe_div(numerator, denominator)` helper: `numerator / denominator.replace(0, np.nan)`
- All 20+ `.apply(lambda r: ..., axis=1)` calls replaced with vectorized pandas/numpy operations
- `f_size_log_assets`: `np.log(out["total_assets"].where(out["total_assets"] > 0))`
- `f_roic`: `out["operating_income"] / (out["total_assets"] - out["current_liabilities"]).replace(0, np.nan)`
- `f_fcf`: `out["operating_cash_flow"] - out["capital_expenditures"]`

**4.5.1 (continued) — accruals.py**
- Removed `_accrual(row)` row function
- Replaced with: `lag = out["_lag_total_assets"].replace(0, np.nan)` then vectorized division

**4.5.1 (continued) — trend_features.py**
- `compute_growth_features`: removed `_pct_change(row)` lambda; replaced with `lag = out[shift_name].replace(0, np.nan)` + `(out[col] - lag) / lag`
- `compute_rolling_growth`: removed inline `lambda r: ...` in `.apply()`; same vectorized pattern
- `compute_margin_trend._rolling_slope`: replaced Python `for i in range(n)` loop with `pd.Series.rolling(window).apply(_slope, raw=True)` — pre-computes `x_centered` and `ss_x` once outside the closure

**4.5.2 — label_builder.py `_asof_price_lookup()`**
- Removed O(n²) `for _, row in merged.iterrows()` loop
- Replaced with O(n) vectorized pattern:
  ```python
  price_by_idx = merged.dropna(subset=["adj_close"]).set_index("_row_idx")["adj_close"]
  result = price_by_idx.reindex(range(len(lookup)))
  result.index = lookup.index
  ```

---

### 4.6 P5 — AI_stock_analysis Integration

#### 4.6.1 Overview

Park the AI_stock_analysis skill, prompt, and report generation logic under `ai-investment-pipeline/` so that the pipeline can auto-generate institutional-grade research reports for its top BUY recommendations.

**Integration flow:**
```
main_inference.py
    |
    v
SlotSelector produces BUY decisions (top 1-3 tickers)
    |
    v
[NEW] ReportGenerator triggered for top-3 BUY tickers
    |
    v
Uses prompt_stock_analysis.md template + live web data
    |
    v
Generates [TICKER]_Analysis_Report.md in reports/ directory
    |
    v
Report provides human-readable justification for the machine decision
```

#### 4.6.2 Files to Migrate

Copy from `AI_stock_analysis/` into `ai-investment-pipeline/`:

| Source | Destination | Purpose |
|--------|------------|---------|
| `.cognition/skills/stock-analysis/SKILL.md` | `ai-investment-pipeline/.cognition/skills/stock-analysis/SKILL.md` | Devin CLI skill definition (with path adjustments) |
| `prompt_stock_analysis.md` | `ai-investment-pipeline/pipeline/llm/prompt_stock_analysis.md` | 562-line mega-prompt template |
| `README.md` (relevant sections) | Merge into main README.md | Usage docs |

#### 4.6.3 New Module: `pipeline/llm/report_generator.py`

Create a new module that orchestrates report generation:

```python
class ReportGenerator:
    """Generate institutional-grade research reports for pipeline BUY picks.

    Uses the prompt_stock_analysis.md template with live web data via
    the Devin CLI skill or direct LLM API call (Google Gemini / Claude).

    This replaces the simple LLMAnalyst (200-word advisory) with a full
    11-section research report (500-700 lines per ticker).
    """

    def __init__(self, config: dict):
        self.config = config
        self.prompt_template = self._load_prompt_template()
        self.output_dir = PROJECT_ROOT / "reports" / "stock_analysis"

    def generate_for_picks(self, decisions: list, top_n: int = 3):
        """Generate reports for the top N BUY picks."""
        buy_picks = [d for d in decisions if d["action"] == "BUY"]
        for pick in buy_picks[:top_n]:
            ticker = pick["ticker"]
            self._generate_report(ticker)

    def _generate_report(self, ticker: str):
        """Generate a single report using the skill/prompt."""
        # Option A: Invoke Devin skill via subprocess
        # Option B: Use Google Gemini API with the prompt template
        # Option C: Write ticker to a queue file for manual skill invocation
        pass

    def _load_prompt_template(self) -> str:
        """Load the stock analysis mega-prompt template."""
        prompt_path = Path(__file__).parent / "prompt_stock_analysis.md"
        return prompt_path.read_text()
```

#### 4.6.4 Skill Definition Adjustments

The migrated `SKILL.md` needs path adjustments:

```yaml
---
name: stock-analysis
description: Generate institutional-grade stock research reports for pipeline BUY picks
argument-hint: "<TICKER> [COMPANY NAME]"
permissions:
  allow:
    - Write(reports/stock_analysis/*_Analysis_Report.md)
    - Write(reports/stock_analysis/*_data_cache.json)
---
```

Output directory changes from the AI_stock_analysis repo root to `reports/stock_analysis/` under the pipeline.

#### 4.6.5 Integration with main_inference.py

Add report generation as an optional step after the LLM analyst review:

```python
# After step 9 (LLM analyst review):
# Step 10: Generate full research reports for top BUY picks
report_enabled = config.get("report_generator", {}).get("enabled", False)
if report_enabled:
    from pipeline.llm.report_generator import ReportGenerator
    reporter = ReportGenerator(config)
    reporter.generate_for_picks(llm_decisions, top_n=3)
```

#### 4.6.6 Config Additions

Add to `config/settings.yaml`:
```yaml
report_generator:
  enabled: false          # set true to auto-generate reports on inference
  top_n: 3                # number of BUY picks to generate reports for
  output_dir: "reports/stock_analysis"
  cache_dir: "reports/stock_analysis"  # data cache for token optimization
  method: "skill"         # "skill" (Devin CLI) or "api" (direct Gemini/Claude)
```

#### 4.6.7 Intended Behavior

1. **Daily inference** (`python -m pipeline.main_inference`):
   - Pipeline runs as normal: loads data, predicts, selects 1-3 stocks.
   - If `report_generator.enabled: true` and the top BUY picks have no same-day cached report, trigger report generation for the top 3 tickers.
   - Reports are saved under `reports/stock_analysis/[TICKER]_Analysis_Report.md`.
   - Data caches (`[TICKER]_data_cache.json`) enable token optimization on repeat runs (same-day: 70% savings, 1-7 days: 35% savings).

2. **Manual invocation** via Devin CLI:
   ```bash
   /stock-analysis PLTR "Palantir Technologies"
   ```
   Works exactly as before but outputs to the pipeline's report directory.

3. **Backtest mode**: Report generation is **disabled** during backtests (too slow, too expensive).

---

## 5. Future Considerations (Post-Release 3)

These items are **not in scope** for Release 3 but are documented for planning:

### 5.1 Structured LLM Signal (Release 4 candidate)

Instead of free-text advisory analysis (current LLMAnalyst) or full research reports (Release 3), create a **structured JSON signal** that feeds directly into the SlotSelector:

```json
{
  "ticker": "PLTR",
  "llm_sentiment_score": 0.72,
  "risk_flags": ["earnings_in_5_days", "sector_rotation_headwind"],
  "catalyst_proximity": 0.85,
  "fundamental_alignment": "AGREE"
}
```

This would make the LLM component quantitative and backtestable — a 4th signal alongside rank_score, pred_return, and prob_up.

### 5.2 Feature Engineering Expansion

From `rel1_improvement_strategy.md` (still unimplemented):
- ATR (Average True Range)
- EMA(5), EMA(20) crossovers
- Trend slope (linear regression over 10-20 days)
- Market regime features (SPY rolling vol, VIX proxy, market breadth)
- Relative strength vs. SPY

### 5.3 NLP / Earnings Transcript Features

Deferred from Release 2. Use NLP on SEC filings' MD&A and Risk Factors text (already extracted by `xbrl_parser.py`) to generate sentiment features.

### 5.4 Altman Z-Score and Beneish M-Score

Deferred from Release 2. Both are feasible with the existing XBRL data.

### 5.5 SHAP Explainability

Feature-level attribution for model decisions. Useful for debugging and reporting.

---

## 6. AI Agent Development Instructions

This section provides step-by-step implementation guidance for AI coding agents working on Release 3.

### 6.1 General Rules

1. **Read before writing.** Always read the file you're about to modify. Understand surrounding code, imports, and patterns before making changes.
2. **Match existing style.** This codebase uses:
   - Type annotations (Python 3.10+ style and `# type:` comments)
   - `get_logger()` for all logging
   - Docstrings in Google/numpy hybrid style
   - `config: dict` passed to every component's constructor
   - `PROJECT_ROOT` from `pipeline/utils/utils.py` for path resolution
3. **Run tests after every change.** If no tests exist for the module you changed, write one first.
4. **Do not break existing interfaces.** The `main_train.py`, `main_inference.py`, and `main_backtest.py` CLIs must continue to work with existing arguments.
5. **Commit atomically.** Each P0/P1/P2 item is one logical commit. Do not mix correctness fixes with performance optimization.

### 6.2 Current Session State (Updated 2026-04-13)

Before starting work, read this summary of what has been completed and what is blocked:

**Completed:**
- ✅ 4.1.1 Validation split fix — all 4 LightGBM/XGBoost models, `_make_time_split()` helper added
- ✅ 4.1.2 Proportional transaction costs — `backtester.py` reads `config["costs"]` bps
- ✅ 4.1.3 Turnover penalty — vectorized implementation in `slot_selector.py`
- ✅ 4.1.4 Hysteresis + `current_positions` threading — `slot_selector.py` + `backtester.py`

**Current blocker:**
- ✅ 4.1.5 — FIXED. `FeatureJoiner` now produces 44 `f_*` columns and 53,839 rows with fundamentals. Root cause: `pd.NA` → `object` dtype in feature lambdas + wrong `canonical_*` prefix in validation. Also fixed `data_loader.py` empty-ticker guard.

**Parallel investigation:**
- 🟡 4.2.3 — `LabelBuilder` 77% row dropout. Can be debugged independently while 4.1.5 is being fixed.

### 6.3 Diagnosing 4.1.5 — FeatureJoiner Fundamental Merge

When an AI agent picks up this task, execute these diagnostic steps in order before writing any code:

**Step 1 — Verify ticker overlap:**
```python
# In a notebook or quick script
import pandas as pd
from pipeline.utils.utils import PROJECT_ROOT

df_price = pd.read_parquet(PROJECT_ROOT / "data" / "ohlcv" / "features.parquet")
df_fund = pd.read_parquet(PROJECT_ROOT / "data" / "fundamentals" / "features.parquet")

price_tickers = set(df_price["ticker"].unique())
fund_tickers = set(df_fund["ticker"].unique())
print("Price tickers:", sorted(price_tickers)[:10])
print("Fund tickers:", sorted(fund_tickers)[:10])
print("Overlap:", sorted(price_tickers & fund_tickers))
```
If the overlap is empty → ticker format mismatch (root cause 1 in 4.1.5). Fix the ticker normalisation in the ETL or the join key.

**Step 2 — Verify date types:**
```python
print(df_fund["filing_date"].dtype)   # must be datetime64[ns], not object
print(df_fund["filing_date"].isna().sum())
print(df_price["date"].dtype)         # must be datetime64[ns]
```
If `filing_date` is `object` dtype → cast it: `df_fund["filing_date"] = pd.to_datetime(df_fund["filing_date"])`.

**Step 3 — Run a minimal manual merge_asof:**
```python
one_ticker_price = df_price[df_price["ticker"] == "AAPL"].sort_values("date")
one_ticker_fund = df_fund[df_fund["ticker"] == "AAPL"].sort_values("filing_date")

merged = pd.merge_asof(
    one_ticker_price,
    one_ticker_fund,
    left_on="date",
    right_on="filing_date",
    by="ticker",
)
print(merged.shape, merged["f_roa"].notna().sum())
```
This isolates whether the join logic works for one ticker before debugging the full pipeline.

**Step 4 — Fix the root cause in `feature_joiner.py`**, then re-run `python -m pipeline.main_train` and verify the log shows `Rows with ≥1 fundamental feature: N` where N > 0.

### 6.4 Diagnosing 4.2.3 — LabelBuilder 77% Dropout

**Step 1 — Check per-ticker dropout:**
```python
# In label_builder.py or a debug script, after label assignment:
per_ticker = df_train.groupby("ticker")["fwd_return_1w"].apply(
    lambda s: s.isna().sum()
)
print(per_ticker.sort_values(ascending=False))
```
If dropout is concentrated in a few tickers → data availability issue for those tickers.
If dropout is uniform across all tickers → systematic bug in the forward-price lookup.

**Step 2 — Verify the forward-return computation pattern:**
Look for `shift(-5)` in `label_builder.py`. It must be called within a `groupby("ticker")`, not on the full DataFrame:
```python
# WRONG — shifts across ticker boundaries:
df["fwd_return"] = df["adj_close"].shift(-5)

# CORRECT — shifts within each ticker's time series:
df["fwd_return"] = df.groupby("ticker")["adj_close"].shift(-5)
```

**Step 3 — Check the train/test split boundary.** If the `LabelBuilder` is called on a slice that ends before the last 5 trading days of the full dataset, those rows correctly have NaN labels. But if the training window ends months before the available price data, a larger block will be unlabelled.

### 6.5 Implementation Order (Updated 2026-04-13)

```
Phase 1: Correctness (P0) — COMPLETE ✅
  1. ✅ Fix validation split (lightgbm_models.py, xgboost_models.py, fundamental_scorer.py)
  2. ✅ Implement proportional transaction costs (backtester.py)
  3. ✅ Implement turnover penalty (slot_selector.py)
  4. ✅ Implement hysteresis + thread current_positions (slot_selector.py, backtester.py)
  5. ⬜ Write regression tests for all 4 fixes (deferred to P2, not blocking)

Phase 1b: Newly Discovered Blockers (P0 continuation) — DONE ✅
  6. ✅ Fix FeatureJoiner — fundamental merge produces 0 rows (4.1.5) ← DONE
  7. ✅ Fix LabelBuilder 77% row dropout (4.2.3) ← DONE (2026-04-16)

Phase 2: Validation (P1) — ✅ DONE (2026-04-17)
  8. ✅ Price data persisted to data/ohlcv/price_data.parquet (DataLoader fix)
  9. ✅ FundamentalScorer trained — 503 tickers, non-degenerate scores, data/fundamentals/fundamental_scores.json
  10. ✅ Combined models retrained with 50,077 samples (LabelBuilder fix + ticker collision fix)
  11. ✅ Walk-forward A/B comparison complete — logs/wf_backtest_results_with_overlay.csv
  12. ✅ Full A/B analysis in reports/backtest_reports/backtest_comparison.md

Phase 3: Testing (P2) — ✅ DONE (2026-04-17)
  13. ✅ Create test infrastructure (pytest.ini, tests/conftest.py, session-scoped fixtures)
  14. ⬜ Unit tests skipped (deferred per release scope)
  15. ⬜ Unit tests skipped (deferred per release scope)
  16. ✅ Integration tests: test_train_predict_cycle.py, test_backtest_e2e.py, test_feature_joiner.py
  17. ✅ All 25 tests pass — `pytest tests/ -v`

Phase 4: Hygiene (P3) — ✅ DONE (2026-04-18)
  18. ✅ Move API keys to env vars — settings.yaml placeholders, load_config() resolver, .env.example, .gitignore
  19. ✅ Clean up dead code — LSTM config removed, feature_schema.py updated to 44 f_* features, RECOMPUTE_COEFFS → --no-recompute-coeffs CLI flag

Phase 5: Performance (P4)
  20. Vectorize ratio_calculator.py (follow piotroski.py pattern)
  21. Vectorize accruals.py and trend_features.py
  22. Fix O(n^2) label builder lookup

Phase 6: Integration (P5)
  23. Copy AI_stock_analysis files into pipeline structure
  24. Create report_generator.py module
  25. Wire into main_inference.py (behind config flag)
  26. Test end-to-end: inference -> report generation for top 3 picks
  27. Update README.md with integrated usage instructions
```

### 6.6 Testing Guidance

**Synthetic data pattern** (use for all unit tests):

```python
import pandas as pd
import numpy as np

def make_synthetic_fundamentals(n_tickers=10, n_quarters=8):
    """Generate synthetic fundamental data for testing."""
    tickers = [f"TICK{i}" for i in range(n_tickers)]
    rows = []
    for t in tickers:
        for q in range(n_quarters):
            rows.append({
                "ticker": t,
                "filing_date": pd.Timestamp("2022-01-01") + pd.DateOffset(months=3*q),
                "revenue": np.random.uniform(1e9, 50e9),
                "net_income": np.random.uniform(1e8, 10e9),
                "total_assets": np.random.uniform(10e9, 200e9),
                "total_liabilities": np.random.uniform(5e9, 100e9),
                "operating_cash_flow": np.random.uniform(5e8, 15e9),
                "shares_outstanding": np.random.uniform(1e9, 10e9),
                "current_assets": np.random.uniform(5e9, 50e9),
                "current_liabilities": np.random.uniform(2e9, 30e9),
                "stockholders_equity": np.random.uniform(5e9, 100e9),
                "gross_profit": np.random.uniform(5e8, 30e9),
                "operating_income": np.random.uniform(2e8, 12e9),
                "capital_expenditures": np.random.uniform(1e8, 5e9),
                "sector": np.random.choice(["Technology", "Healthcare", "Financials"]),
            })
    return pd.DataFrame(rows)
```

### 6.7 Verification Commands

After each phase, run:

```bash
# Phase 1: Verify fixes don't break training
cd /home/victor_truong/sandbox/ai-investment-pipeline
python -m pipeline.main_train --mode price

# Phase 2: Full training (price + combined features + fundamental scorer)
# Note: --mode both now includes fundamental_scorer as of 2026-04-17
python -m pipeline.main_train --mode both
python -m pipeline.main_backtest --mode wf-backtest --fundamental-overlay

# Phase 3: Run integration tests
pytest tests/ -v --tb=short

# Phase 4: Verify config still loads
python -c "from pipeline.utils.utils import load_config; c = load_config(); print('OK')"

# Phase 5: Benchmark feature engineering speed
python -c "
import time
import pandas as pd
from pipeline.fundamental_analysis.features.ratio_calculator import compute_ratio_panel
df = pd.read_parquet('data/fundamentals/fundamental_training_data.parquet')
start = time.time()
compute_ratio_panel(df)
print(f'Ratio computation: {time.time()-start:.2f}s for {len(df)} rows')
"
```

---

## 7. Integration Test Suite Reference (P2)

> Added 2026-04-17. Covers the three integration test files created under `tests/` as part of P2. Unit tests (4.3.1) are deferred to a future release.

### 7.1 How to Run

```bash
# Full suite (all 25 tests, verbose)
cd /home/victor/Workspace/ai-investment-pipeline
pytest tests/ -v

# Short summary only (no per-test lines)
pytest tests/ -q

# Single file
pytest tests/test_train_predict_cycle.py -v
pytest tests/test_backtest_e2e.py -v
pytest tests/test_feature_joiner.py -v

# Stop on first failure
pytest tests/ -x -v

# Show captured log output (useful for debugging model training noise)
pytest tests/ -v -s

# Run with coverage report (requires pytest-cov)
pytest tests/ --cov=pipeline --cov-report=term-missing
```

Expected baseline output:
```
25 passed in ~1.5s
```

All tests use synthetic data generated in-process. No real data files, no network access, no model artifacts on disk are required.

---

### 7.2 Test Infrastructure (`tests/conftest.py`)

The `conftest.py` defines session-scoped fixtures shared by all three test files.

| Fixture | Scope | What It Provides |
|---------|-------|-----------------|
| `cfg` | session | Minimal pipeline config dict. LightGBM backend, `num_boost_round=30`, 14-bps cost model, 3-slot allocation. |
| `price_df` | session | 5 tickers × 100 business days of synthetic OHLCV feature data. All 14 `MODEL_FEATURES` columns plus `ticker`, `date`, `adj_close`. |
| `trained_models` | session | Pre-trained LightGBM ranker, regressor, and classifier. Trained once and reused across all tests that need prediction. Avoids repeating 3× model training per test. |
| `price_df_factory` | session | Returns the `make_price_df(n_tickers, n_days, seed)` helper function itself. Use this in tests that need custom-shaped data (e.g. 30-day mini backtest). |

**Why session scope?** Model training is the slowest step (~0.5s per model). Session scope trains once per `pytest` invocation and shares the result across all 25 tests, keeping the full suite under 2s.

**Synthetic data design:** `make_price_df()` generates a random-walk `adj_close` starting at $100, and independently sampled values for all 14 features. The values are within realistic ranges (e.g. RSI in [30, 70], SMA ratios near 1.0, returns in ±2% daily). Labels used for training are random integers in [0, 4] — sufficient to verify that models train and predict correctly; they do not need to be meaningful for the tests to be valid.

---

### 7.3 `tests/test_train_predict_cycle.py` — 7 Tests

**Purpose:** Verify that all three model roles (ranker, regressor, classifier) can be constructed via `ModelFactory`, trained on synthetic data, and produce predictions with correct shapes and value ranges. These tests catch: wrong feature list, broken `train()` or `predict()` signatures, factory configuration errors, and dtype issues in output arrays.

| Test | What It Validates | Expected Result |
|------|-------------------|----------------|
| `test_factory_creates_all_three_roles` | `ModelFactory(cfg).create(role)` returns a non-None object for `"ranker"`, `"regressor"`, `"classifier"` | All three return non-None without error |
| `test_ranker_trains_and_predicts_correct_shape` | `ranker.train(X, y_rank)` then `ranker.predict(X_feat)` | Output array has shape `(n_rows,)` |
| `test_ranker_predictions_are_finite` | Same as above, check no NaN/Inf in output | `np.all(np.isfinite(preds)) == True` |
| `test_regressor_trains_and_predicts_floats` | Regressor trained on continuous `ret_5d` targets; `predict()` returns floats | Shape `(n_rows,)`, all finite |
| `test_classifier_predict_proba_shape_and_range` | Classifier trained on binary labels; `predict_proba()` returns probabilities | Shape `(n_rows,)`, all values in `[0.0, 1.0]` |
| `test_trained_models_fixture_all_present` | Smoke-test the session fixture | All three model objects are non-None |
| `test_trained_models_predict_on_new_data` | Session-trained models called with a fresh 20-row DataFrame | All three produce `(20,)` output; classifier probabilities still in `[0, 1]` |

**Regression value:** If LightGBM's `train()` or `predict()` API changes, or if `_clean_X()` incorrectly drops required feature columns, these tests will fail immediately.

---

### 7.4 `tests/test_backtest_e2e.py` — 12 Tests

**Purpose:** Verify that the `Backtester` runs end-to-end on a small synthetic dataset and produces structurally correct outputs. This is a regression test for the entire daily simulation loop: feature prediction → `SlotSelector` → position reconciliation → equity update → metrics computation. These tests catch: broken backtester loop, wrong equity curve accumulation, missing metric keys, debug log column regressions.

The module-level `backtest_results` fixture runs a single 30-day, 5-ticker backtest once and shares the `results` dict across all 12 tests in the file.

**Setup parameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_tickers` | 5 | Enough for SlotSelector to have real choices vs. CASH |
| `n_days` | 30 business days | Fast to simulate; enough to exercise all 5 bucket slots (horizon=5) |
| `horizon_days` | 5 | Matches production default (5 staggered buckets) |
| `initial_capital` | $20,000 | Matches `Backtester.initial_capital` hardcoded value |

| Test | What It Validates | Expected Result |
|------|-------------------|----------------|
| `test_backtest_returns_all_keys` | `results` dict has `equity_curve`, `daily_returns`, `metrics`, `debug_log` | All 4 keys present |
| `test_equity_curve_length` | Equity curve has exactly `n_days` entries | `len(equity_curve) == 30` (1 initial + 29 simulated days) |
| `test_initial_capital_is_correct` | First entry of equity curve equals hardcoded initial capital | `equity_curve[0] == 20_000.0` |
| `test_daily_returns_count_matches_equity_steps` | One daily return per equity step after the initial | `len(daily_returns) == len(equity_curve) - 1` |
| `test_metrics_keys_all_present` | All five required metric keys exist | `sharpe`, `max_drawdown`, `cagr`, `hit_rate`, `total_return` all present |
| `test_sharpe_in_plausible_range` | Sharpe ratio is mathematically possible | `−15 ≤ sharpe ≤ 15` |
| `test_max_drawdown_is_non_positive` | Max drawdown is a non-positive fraction | `−1.0 ≤ max_drawdown ≤ 0.0` |
| `test_hit_rate_is_a_valid_probability` | Hit rate is a valid probability | `0.0 ≤ hit_rate ≤ 1.0` |
| `test_total_return_bounded_by_capital_floor` | Portfolio can't lose more than 100% | `total_return > −1.0` |
| `test_debug_log_not_empty` | Backtest produced at least one debug entry | `len(debug_log) > 0` |
| `test_debug_log_has_required_columns` | Each debug entry has all expected columns | `{"date", "ticker", "rank_score", "pred_return", "prob_up", "actual_next_ret", "weight_assigned", "is_selected"}` all present |
| `test_debug_log_covers_all_test_tickers` | Every ticker appears in the debug log | `{"TICK0", …, "TICK4"}` found in log |

**Key invariant: equity curve length.** The backtester calls `df = df[df["date"] < last_date]` before the loop, dropping the final date (no forward return available). With `n_days=30` input dates, 29 dates are simulated. `equity_curve` starts as `[20_000.0]` and appends one value per date → 30 total entries.

---

### 7.5 `tests/test_feature_joiner.py` — 6 Tests

**Purpose:** Verify the temporal merge logic inside `FeatureJoiner.join()` (the P0 bug fix site). These tests are regression tests for two critical past bugs: the ticker-column duplication (`ticker_x`/`ticker_y`) that caused 77% label dropout, and look-ahead leakage (using future filings at prediction time).

**Synthetic data setup:** `_price_df()` generates 60 daily rows per ticker. `_fund_df()` generates 4 quarterly filings per ticker starting at `start`. Tests that verify specific temporal behavior use hand-crafted DataFrames with known sentinel values.

| Test | What It Validates | Expected Result |
|------|-------------------|----------------|
| `test_join_preserves_price_row_count` | `join()` output has same number of rows as price input | `len(result) == len(price)` — no rows added or dropped |
| `test_no_lookahead_leakage` | On each price date, only filings at or before that date are visible | Rows with `date < filing_date` have `NaN` for the filing's column; rows with `date ≥ filing_date` have the correct value (999.0 sentinel) |
| `test_ticker_column_not_duplicated` | `ticker` appears exactly once in output columns | `"ticker"` present; `"ticker_x"` and `"ticker_y"` absent — **regression test for the P0 ticker-collision fix** |
| `test_ticker_missing_from_fundamentals_produces_nan_not_crash` | A ticker present in price but absent in fundamentals is handled gracefully | `len(result) == len(price)` and fundamental columns are `NaN` for the missing ticker |
| `test_backward_fill_between_two_filings` | Price rows between two filing dates carry the earlier filing's data, not the later one | All rows with `2022-01-10 ≤ date < 2022-03-10` have `f_val == 1.0`; no bleed-forward from the `2022-03-10` filing |
| `test_all_tickers_present_in_output` | All tickers from the price DataFrame appear in output, even those without fundamental data | `set(result["ticker"].unique()) == set(price["ticker"].unique())` |

**Why look-ahead leakage matters here.** The pipeline uses `direction="backward"` in `merge_asof`, meaning for each price date it picks the most recent filing at-or-before that date. A bug that switched to `direction="forward"` would silently cause the model to see future quarterly earnings data during training — inflating backtest Sharpe dramatically with information that would not be available in live trading. The sentinel test (`f_sentinel = 999.0`) catches this class of bug directly.

---

## 8. Reference: AI_stock_analysis Project Summary

### 7.1 Project Structure

```
AI_stock_analysis/
├── .cognition/skills/stock-analysis/
│   └── SKILL.md                    # Devin CLI skill (169 lines)
├── prompt_stock_analysis.md        # Full mega-prompt (562 lines, 11 sections)
├── PLTR_Analysis_Report.md         # Generated report (658 lines)
├── MSFT_Analysis_Report.md         # Generated report (509 lines)
├── README.md                       # Usage documentation (96 lines)
└── .gitignore
```

### 7.2 Report Sections (11 total)

| # | Section | Content |
|---|---------|---------|
| 1 | Company Overview & Business Model | Segments, moat, competitors, TAM, management |
| 2 | Fundamental Analysis | Income statement (5yr), balance sheet, cash flow, valuation multiples, DCF |
| 3 | Technical Analysis & Price Action | Trend, MAs, RSI/MACD, volume, support/resistance, key levels table |
| 4 | Analyst Consensus & Sentiment | Ratings breakdown, price targets, upgrades/downgrades, short interest |
| 5 | Recent News, Catalysts & Risks | Last 90 days, upcoming events, risk assessment (company/sector/macro/ESG) |
| 6 | Sector & Macro Context | Sector performance, tailwinds/headwinds, business cycle |
| 7 | Dividend & Income Analysis | Yield, payout, safety, growth (or N/A) |
| 8 | Ownership & Insider Activity | Top holders, insider buys/sells with amounts |
| 9 | Scenario Analysis | Bull/base/bear table with probability-weighted expected value |
| 10 | Intraday & Short-Term Trading Signals | VWAP, intraday technicals, volume/flow, trade setups (entry/stop/target) |
| 11 | Final Verdict & Recommendation | Rating, conviction, PROS/CONS, position sizing, entry strategy |

### 7.3 Skill Definition (SKILL.md Summary)

The Devin CLI skill provides:
- **Data caching** with staleness tiers (same-day: 70% savings, 1-7 days: 35%, 8-30 days: 15%)
- **Multi-turn web search** across 5 data batches (fundamentals, technicals, analysts, news, intraday)
- **Configurable report format** with metadata header and data freshness logging
- **Reference sources**: stockanalysis.com (primary), finviz.com (fallback), barchart.com (intraday)

### 7.4 Sample Reports Generated

- **PLTR (2026-04-10)**: 658 lines, rated BUY with High conviction. Included 4 specific trade setups, 30-day price table, Fibonacci retracement levels, intraday hammer candlestick analysis.
- **MSFT (2026-04-10)**: 509 lines, rated BUY with High conviction. DCF fair value ~$286/share (conservative), analyst consensus Strong Buy with avg PT $596.81 (+59.9% upside), 12.1% institutional outflow flagged as concern.

### 7.5 Key Design Decisions

1. **Reports are stateless**: Each run performs live web searches. No ML learning between runs.
2. **Cache reduces token cost**: JSON data cache enables incremental updates instead of full re-search.
3. **Advisory only**: Reports are for human consumption. They do not produce machine-actionable signals (this is what Release 3 P5 integration changes).
4. **Model-agnostic**: The prompt works with Claude, GPT-4, Gemini, or any LLM with web access.

---

## 8. Appendix: File Inventory (Release 2 As-Built)

For AI agents needing to navigate the codebase:

```
ai-investment-pipeline/                          # 10,607 lines Python
├── config/
│   ├── env.yaml                                 # Conda environment spec
│   ├── settings.yaml                (142 lines) # Main config (API keys, tickers, model params)
│   └── sp500_tickers.yaml          (1515 lines) # 503 S&P 500 tickers with CIK + GICS sectors
├── pipeline/
│   ├── __init__.py
│   ├── inspect_data.py               (92 lines) # Data debugging utility
│   ├── main_train.py                (686 lines) # Training orchestrator (5 modes)
│   ├── main_inference.py            (288 lines) # Daily inference pipeline
│   ├── main_backtest.py             (562 lines) # Backtesting (single-split + walk-forward)
│   ├── fundamental_analysis/
│   │   ├── data_providers/
│   │   │   └── fmp_client.py        (246 lines) # Financial Modeling Prep API client
│   │   ├── etl/
│   │   │   ├── companyfacts_extractor.py (411 lines) # XBRL canonical metric extraction
│   │   │   ├── data_ingest_scheduler.py  (565 lines) # Incremental ETL orchestration
│   │   │   ├── edgar_client.py           (479 lines) # SEC EDGAR API client
│   │   │   ├── etl_inspect.py                        # ETL debugging
│   │   │   ├── point_in_time.py          (704 lines) # Point-in-time snapshot manager
│   │   │   ├── restatement_tracker.py    (444 lines) # Filing amendment detection
│   │   │   ├── universe_manager.py       (195 lines) # Ticker universe resolution
│   │   │   └── xbrl_parser.py            (616 lines) # Full XBRL/iXBRL parser
│   │   ├── features/
│   │   │   ├── accruals.py                (61 lines) # Accrual anomaly features
│   │   │   ├── feature_schema_fundamental.yaml       # Feature registry
│   │   │   ├── fundamental_feature_engineer.py (418 lines) # Master orchestrator
│   │   │   ├── piotroski.py              (242 lines) # Piotroski F-Score (9 signals)
│   │   │   ├── ratio_calculator.py       (257 lines) # 20+ financial ratios
│   │   │   ├── sector_relative.py        (124 lines) # Within-sector z-scores
│   │   │   └── trend_features.py         (132 lines) # Growth + margin trend (OLS)
│   │   ├── integration/
│   │   │   └── overlay.py                (258 lines) # Fundamental overlay rules
│   │   ├── models/
│   │   │   ├── fundamental_scorer.py     (458 lines) # Quality/value/trend scorer
│   │   │   └── label_builder.py          (334 lines) # 6-month forward return labels
│   │   └── tests/
│   │       └── test_xbrl_parser.py        (42 lines) # XBRL unit test
│   ├── llm/
│   │   └── llm_analyst.py               (251 lines) # Google Gemini LLM analyst
│   ├── ohlcv/
│   │   ├── backtest/
│   │   │   ├── backtester.py             (193 lines) # Staggered-bucket backtester
│   │   │   ├── backtest_report.py         (94 lines) # Equity curve + drawdown plots
│   │   │   └── metrics.py                 (43 lines) # Sharpe, CAGR, max DD, Calmar
│   │   ├── dataset/
│   │   │   ├── data_loader.py            (204 lines) # Multi-source OHLCV loader
│   │   │   ├── feature_schema.py          (65 lines) # Feature registry (STALE)
│   │   │   ├── feature_selector.py       (165 lines) # Config-driven feature selection
│   │   │   ├── label_builder.py           (73 lines) # 1-week forward return labels
│   │   │   └── ohlcv_feature_engineer.py  (97 lines) # 14 price features
│   │   ├── models/
│   │   │   ├── base_model.py             (142 lines) # Abstract base class
│   │   │   ├── classifier_model.py                   # Legacy wrapper
│   │   │   ├── lightgbm_models.py        (143 lines) # LightGBM backend
│   │   │   ├── model_factory.py          (107 lines) # Config-driven factory
│   │   │   ├── model_manager.py          (158 lines) # Versioned model persistence
│   │   │   ├── ranker_model.py            (49 lines) # Legacy wrapper
│   │   │   ├── regressor_model.py                    # Legacy wrapper
│   │   │   ├── sklearn_models.py         (173 lines) # GradientBoosting + RF backends
│   │   │   └── xgboost_models.py         (141 lines) # XGBoost backend
│   │   └── policy/
│   │       ├── policy_params.json                    # Saved coefficients
│   │       └── slot_selector.py          (236 lines) # Portfolio allocation policy
│   └── utils/
│       ├── logger.py                     (100 lines) # Dual-output logging
│       └── utils.py                       (52 lines) # Config loading, path helpers
├── test_merge_fix.py                     (144 lines) # merge_asof integration test
├── test_merge_groupby.py                             # Additional merge test
└── .gitignore
```
