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

# Release 2 — Fundamental Analysis Architecture

> **Audience:** Humans and AI coding agents working on this codebase.
> **Last updated:** 2026-04-05

---

## 1. Executive Summary

The fundamental analysis layer is a **supportive overlay** on the primary OHLCV price model. It does **not** replace or combine with the price model's BUY/SELL ranking. Instead, it produces independent **quality, valuation, and trend scores** per ticker that confirm, warn, or downgrade the price model's signals.

**Current state:** SEC EDGAR Company Facts API pipeline is operational for 503 S&P 500 stocks with 16 XBRL concepts and 45 fundamental features. The ETL, feature engineering (ratio calculator, accruals, growth/trend, Piotroski F-Score, sector-relative Z-scores), standalone FundamentalScorer (quality/value/trend sub-models), and integration overlay are all implemented. The overlay is wired into `main_inference.py`.

**What is validated:** Steps 1-3 (universe, XBRL expansion, feature engineering) have been run end-to-end with real SEC data (21,238 snapshots, 503 tickers, 45 `f_` features, 28s runtime). All modules pass syntax and smoke tests.

**What is NOT validated:** The FundamentalScorer has never been trained on real data because no price data parquet exists on disk (needed for 6-month forward-return labels). The overlay has never executed in a real inference run. The backtester has zero fundamental integration.

**Remaining work for release closure:** See Section 10 (Acceptance Criteria).

---

## 2. Architecture Overview

```
                          PRICE PATH (primary)                     FUNDAMENTAL PATH (overlay)
                          ==================                     ============================

Data Source:              Alpha Vantage / yfinance               SEC EDGAR Company Facts API
                          Daily OHLCV bars                       Quarterly/Annual XBRL filings
                               |                                         |
                               v                                         v
Feature Eng:              OhlcvFeatureEngineer                   FundamentalsFeatureEngineer
                          14 features (ret, SMA,                 45 features (ratios, accruals,
                          vol, RSI, MACD, ranks)                 growth, Piotroski, sector Z)
                               |                                         |
                               v                                         v
Models:                   Ranker + Regressor +                   FundamentalScorer
                          Classifier (LightGBM)                  quality_score, value_score,
                          1-week horizon                         trend_score (3-6 month horizon)
                               |                                         |
                               v                                         v
Decisions:                SlotSelector                           Integration Layer
                          BUY / SELL / HOLD                      STRONG_BUY / WARN / DOWNGRADE
                          (3 slots, max_weight)                  overlay on price decisions
                               |                                         |
                               +------------------+------------------+
                                                  |
                                                  v
                                          Final Portfolio Action
                                          (main_inference.py)
```

### Key Design Principle

The price model operates on a **daily cadence with 1-week horizon** — it captures short-term momentum, mean-reversion, and cross-sectional ranking. The fundamental model operates on a **quarterly cadence with 3-6 month horizon** — it captures business quality, valuation, and earnings trajectory. These two signals are **complementary, not redundant**.

The fundamental layer should:
- **Confirm** a BUY when the stock has strong fundamentals (high quality + reasonable valuation + positive trend)
- **Warn** when price signals BUY but fundamentals are deteriorating (falling margins, rising leverage, negative earnings surprise)
- **Downgrade** a BUY to HOLD when fundamental risk is high (e.g., Piotroski F-score < 3, accruals in top decile)
- **Never override SELL** — if the price model says SELL, fundamental analysis should not contradict it

---

## 3. What Is Implemented Today

### 3.1 ETL Layer

| File | Purpose | Status |
|------|---------|--------|
| `pipeline/fundamental_analysis/etl/edgar_client.py` | SEC EDGAR HTTP client with CIK resolution, rate limiting, retry, local JSON caching | **Done** (479 lines) |
| `pipeline/fundamental_analysis/etl/companyfacts_extractor.py` | Extracts 16 canonical columns from XBRL companyfacts JSON | **Done** (411 lines) |
| `pipeline/fundamental_analysis/etl/universe_manager.py` | Ticker universe management with cascading fallback (override, config, file, S&P 500 default) | **Done** (195 lines) |
| `pipeline/fundamental_analysis/etl/xbrl_parser.py` | Raw XBRL/iXBRL parsing from SEC filing ZIPs (complete but not used — companyfacts API does this) | **Deprecated** (616 lines) |
| `pipeline/fundamental_analysis/etl/point_in_time.py` | Point-in-time snapshot builder: discover filings, download, parse, store, restatement scan | **Done** (704 lines) |
| `pipeline/fundamental_analysis/etl/restatement_tracker.py` | Detects filing amendments via 3-level heuristic, marks original snapshots as restated | **Done** (444 lines) |
| `pipeline/fundamental_analysis/etl/data_ingest_scheduler.py` | Full incremental ingestion loop: discover, download, parse, save JSON/Parquet, restatement scan | **Done** (565 lines) |
| `pipeline/fundamental_analysis/etl/etl_inspect.py` | Utility for inspecting stored fundamental data | **Done** (167 lines) |

> **Note:** The primary ETL path for fundamental data is `EdgarClient` + `companyfacts_extractor.py` (direct companyfacts API). The point-in-time, restatement tracker, and data ingest scheduler form an alternative ingestion pathway that downloads and parses raw SEC filings. Both paths are fully implemented.

**EdgarClient** (`edgar_client.py`):
- Endpoints: `COMPANY_SUBMISSIONS` (data.sec.gov/submissions/), `COMPANY_FACTS` (data.sec.gov/api/xbrl/companyfacts/)
- Caching: `data/fundamentals/edgar_cache/companyfacts_{TICKER}_{CIK}.json` (2-6 MB per company)
- Rate limiting: `min_request_interval` (default 0.15s, SEC allows 10 req/s)
- Config: `config["fundamental"]["edgar"]` — `user_agent_email`, `timeout`, `max_retries`

**CompanyFacts Extractor** (`companyfacts_extractor.py`):
- `CONCEPT_MAP`: 16 canonical columns mapped to multiple US-GAAP/DEI XBRL tag variants
- `IFRS_CONCEPT_MAP`: Parallel mapping for foreign filers (TSM, ASML via ifrs-full taxonomy)
- `VALID_FORMS`: 10-K, 10-Q, 10-K/A, 10-Q/A, 20-F, 20-F/A, 40-F, 6-K
- Point-in-time: uses `filed` date (not `period_end`) to avoid look-ahead bias
- Tag union strategy: collects entries from ALL matching tags (not first-match) to handle tag name changes over time

**Current CONCEPT_MAP (16 concepts):**

| Canonical Column | XBRL Tags Tried |
|-----------------|-----------------|
| `revenue` | Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, ...IncludingAssessedTax, SalesRevenueNet, SalesRevenueGoodsNet, SalesRevenueServicesNet |
| `net_income` | NetIncomeLoss, ProfitLoss, NetIncomeLossAvailableToCommonStockholdersBasic |
| `total_assets` | Assets |
| `total_liabilities` | Liabilities, LiabilitiesAndStockholdersEquity |
| `operating_cash_flow` | NetCashProvidedByUsedInOperatingActivities |
| `shares_outstanding` | EntityCommonStockSharesOutstanding, CommonStockSharesOutstanding, WeightedAverageNumberOfSharesOutstandingBasic |
| `stockholders_equity` | StockholdersEquity, StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest |
| `gross_profit` | GrossProfit |
| `operating_income` | OperatingIncomeLoss |
| `current_assets` | AssetsCurrent |
| `current_liabilities` | LiabilitiesCurrent |
| `capital_expenditures` | PaymentsToAcquirePropertyPlantAndEquipment, CapitalExpenditureDiscontinuedOperations |
| `rd_expense` | ResearchAndDevelopmentExpense |
| `interest_expense` | InterestExpense, InterestExpenseDebt |
| `dividends_paid` | PaymentsOfDividends, PaymentsOfDividendsCommonStock |
| `cost_of_revenue` | CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold |

### 3.2 Feature Engineering Layer

| File | Purpose | Status |
|------|---------|--------|
| `pipeline/fundamental_analysis/features/ratio_calculator.py` | Computes 20 financial ratios (6 unconditional + 14 conditional on data availability) | **Done** (257 lines) |
| `pipeline/fundamental_analysis/features/accruals.py` | Computes 2 accrual features (raw + z-scored) | **Done** (61 lines) |
| `pipeline/fundamental_analysis/features/trend_features.py` | Computes up to 14 growth/trend features (QoQ, YoY, rolling, OLS margin trends) | **Done** (132 lines) |
| `pipeline/fundamental_analysis/features/piotroski.py` | Computes 9-point Piotroski F-Score with 3 sub-scores (profitability, leverage, efficiency) | **Done** (242 lines) |
| `pipeline/fundamental_analysis/features/sector_relative.py` | Computes within-sector Z-scores for 5 key metrics | **Done** (124 lines) |
| `pipeline/fundamental_analysis/features/fundamental_feature_engineer.py` | Orchestrator: calls all feature modules, handles errors independently, temporal merge with OHLCV | **Done** (418 lines) |
| `pipeline/fundamental_analysis/features/feature_schema_fundamental.yaml` | YAML schema documenting all 45 fundamental features | **Done** (215 lines) |

**Current fundamental features (45, `f_` prefix):**

#### Basic Ratios (6 unconditional)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 1 | `f_net_margin` | net_income / revenue | ratio_calculator |
| 2 | `f_roa` | net_income / total_assets | ratio_calculator |
| 3 | `f_debt_to_assets` | total_liabilities / total_assets | ratio_calculator |
| 4 | `f_eps` | net_income / shares_outstanding | ratio_calculator |
| 5 | `f_ocf_to_assets` | operating_cash_flow / total_assets | ratio_calculator |
| 6 | `f_market_to_book` | market_cap / total_assets (conditional on market_cap) | ratio_calculator |

#### Expanded Ratios (14 conditional)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 7 | `f_roe` | net_income / stockholders_equity | ratio_calculator |
| 8 | `f_gross_margin` | gross_profit / revenue | ratio_calculator |
| 9 | `f_operating_margin` | operating_income / revenue | ratio_calculator |
| 10 | `f_roic` | operating_income / (total_assets - current_liabilities) | ratio_calculator |
| 11 | `f_rd_to_revenue` | rd_expense / revenue | ratio_calculator |
| 12 | `f_current_ratio` | current_assets / current_liabilities | ratio_calculator |
| 13 | `f_debt_to_equity` | total_liabilities / stockholders_equity | ratio_calculator |
| 14 | `f_interest_coverage` | operating_income / interest_expense | ratio_calculator |
| 15 | `f_equity_ratio` | stockholders_equity / total_assets | ratio_calculator |
| 16 | `f_fcf` | operating_cash_flow - capital_expenditures | ratio_calculator |
| 17 | `f_fcf_margin` | fcf / revenue | ratio_calculator |
| 18 | `f_ocf_to_net_income` | operating_cash_flow / net_income | ratio_calculator |
| 19 | `f_capex_to_revenue` | capital_expenditures / revenue | ratio_calculator |
| 20 | `f_size_log_assets` | log(total_assets) | ratio_calculator |

#### Accruals (2)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 21 | `f_accruals` | (net_income - operating_cash_flow) / lag(total_assets) | accruals |
| 22 | `f_accruals_std` | z-scored accruals within-ticker | accruals |

#### Growth — QoQ (7)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 23 | `f_revenue_chg_1` | QoQ revenue growth | trend_features |
| 24 | `f_net_income_chg_1` | QoQ net income growth | trend_features |
| 25 | `f_operating_income_chg_1` | QoQ operating income growth | trend_features |
| 26 | `f_gross_profit_chg_1` | QoQ gross profit growth | trend_features |
| 27 | `f_operating_cash_flow_chg_1` | QoQ operating cash flow growth | trend_features |
| 28 | `f_stockholders_equity_chg_1` | QoQ equity growth | trend_features |
| 29 | `f_total_assets_chg_1` | QoQ asset growth | trend_features |

#### Growth — YoY (3)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 30 | `f_revenue_chg_4` | YoY revenue growth (4-quarter) | trend_features |
| 31 | `f_net_income_chg_4` | YoY net income growth (4-quarter) | trend_features |
| 32 | `f_operating_income_chg_4` | YoY operating income growth (4-quarter) | trend_features |

#### Rolling Growth (1)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 33 | `f_revenue_rolling_chg_4` | 4-quarter rolling revenue growth | trend_features |

#### Margin Trends (3, OLS slope)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 34 | `f_f_net_margin_trend_4` | 4-quarter OLS slope of net margin | trend_features |
| 35 | `f_f_gross_margin_trend_4` | 4-quarter OLS slope of gross margin | trend_features |
| 36 | `f_f_operating_margin_trend_4` | 4-quarter OLS slope of operating margin | trend_features |

#### Piotroski F-Score (4)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 37 | `f_piotroski_f` | Composite 9-point F-Score (sum of 3 sub-scores) | piotroski |
| 38 | `f_piotroski_profitability` | Sub-score (0-4): ROA, OCF, delta ROA, accrual quality | piotroski |
| 39 | `f_piotroski_leverage` | Sub-score (0-3): delta leverage, delta current ratio, no dilution | piotroski |
| 40 | `f_piotroski_efficiency` | Sub-score (0-2): delta gross margin, delta asset turnover | piotroski |

#### Sector-Relative Z-Scores (5)
| # | Feature | Formula | Module |
|---|---------|---------|--------|
| 41 | `f_roe_sector_z` | ROE z-scored within sector per quarter | sector_relative |
| 42 | `f_net_margin_sector_z` | Net margin z-scored within sector | sector_relative |
| 43 | `f_debt_to_assets_sector_z` | Debt-to-assets z-scored within sector | sector_relative |
| 44 | `f_revenue_chg_1_sector_z` | Revenue growth z-scored within sector | sector_relative |
| 45 | `f_accruals_sector_z` | Accruals z-scored within sector | sector_relative |

### 3.3 Temporal Merge (FeatureJoiner)

The `FeatureJoiner` class in `fundamental_feature_engineer.py` aligns daily OHLCV features with quarterly fundamental features using `pd.merge_asof(direction="backward")`. For each daily price row, it attaches the most recent fundamental snapshot filed on or before that date. This ensures point-in-time correctness.

### 3.4 Feature Schema

Two schemas exist:

1. **`pipeline/fundamental_analysis/features/feature_schema_fundamental.yaml`** — The authoritative schema for fundamental features. Documents all 45 `f_` features with categories, formulas, and source modules.

2. **`pipeline/ohlcv/dataset/feature_schema.py`** — Python-side feature registry used by the combined price+fundamental model. Currently lists only the original 11 fundamental features in `FUNDAMENTAL_FEATURES`. **This is stale** — it has not been updated to include the 34 features added in Steps 2-3. The standalone `FundamentalScorer` defines its own feature groups (QUALITY_FEATURES, VALUE_FEATURES, TREND_FEATURES) and does not depend on this file.

| Registry | Features | Used By |
|----------|----------|---------|
| `feature_schema.py` `FUNDAMENTAL_FEATURES` | 11 (original) | Combined price+fundamental model (`--mode fundamental_full`) |
| `feature_schema_fundamental.yaml` | 45 (complete) | Documentation, validation |
| `fundamental_scorer.py` feature groups | 40 (15 quality + 11 value + 14 trend) | Standalone FundamentalScorer (`--mode fundamental_scorer`) |

### 3.5 Models Layer

| File | Purpose | Status |
|------|---------|--------|
| `pipeline/fundamental_analysis/models/fundamental_scorer.py` | Standalone FundamentalScorer: LightGBM-based, 3 sub-models (quality/value/trend), scores in [0,1], JSON persistence | **Done** (458 lines) |
| `pipeline/fundamental_analysis/models/label_builder.py` | FundamentalLabelBuilder: 6-month forward return quintile labels via `merge_asof` | **Done** (334 lines) |

**FundamentalScorer** (`fundamental_scorer.py`):
- Main model + 3 sub-models: `quality_score`, `value_score`, `trend_score`
- Feature groups: QUALITY_FEATURES (15), VALUE_FEATURES (11), TREND_FEATURES (14)
- Uses `_rank_to_score()` for [0,1] normalization via percentile rank
- Persistence: `data/fundamentals/fundamental_scores.json` (loaded at inference time)
- Training: `python -m pipeline.main_train --mode fundamental_scorer`

**FundamentalLabelBuilder** (`label_builder.py`):
- Computes 6-month forward returns (126 trading days) from price data
- Cross-sectional quintile labels per filing quarter
- Uses `pd.merge_asof` for point-in-time price lookup
- **Critical dependency:** Requires price data at `data/processed/price_data.parquet` or `data/ohlcv/price_data.parquet`

> **Known issue:** Without price data on disk, `build_labels()` returns all-NaN labels, and the scorer cannot be trained. The code warns but does not error out clearly.

### 3.6 Integration Layer

| File | Purpose | Status |
|------|---------|--------|
| `pipeline/fundamental_analysis/integration/overlay.py` | Applies fundamental overlay to SlotSelector decisions: STRONG_BUY / WARN / DOWNGRADE rules | **Done** (258 lines) |

**Overlay rules** (implemented in `_classify_row()`):
1. BUY + high quality + high value + positive trend -> **STRONG_BUY** (keep, increase confidence)
2. BUY + low quality OR deteriorating trend -> **WARN** (keep BUY but flag risk)
3. BUY + very low quality (F-score < 3) + negative trend -> **DOWNGRADE** to HOLD
4. SELL -> always **SELL** (fundamentals never override)
5. HOLD + high quality + high value -> consider for BUY shortlist (queue for next cycle)

Thresholds are configurable via `config["fundamental"]["overlay"]` with defaults in `_DEFAULT_THRESHOLDS`.

**Integration in `main_inference.py`** (Step 7, after SlotSelector):
- Loads scores from `data/fundamentals/fundamental_scores.json`
- Calls `apply_fundamental_overlay(decisions, fund_scores, config)`
- Non-fatal: wrapped in try/except — if overlay fails or scores are absent, inference continues with unmodified decisions

### 3.7 Training Pipeline

`pipeline/main_train.py` supports multiple training modes:

| Mode | CLI Flag | What It Does |
|------|----------|--------------|
| `price` | `--mode price` | Price models only (Ranker + Regressor + Classifier) |
| `fundamental` | `--mode fundamental` | ETL/data prep only (fetch SEC data, save parquet) |
| `fundamental_full` | `--mode fundamental_full` | ETL + combined price+fundamental feature engineering + model training |
| `fundamental_scorer` | `--mode fundamental_scorer` | ETL + standalone scorer (quality/value/trend scores) |
| `both` | `--mode both` | price + fundamental_full |

The `fundamental_scorer` mode calls `train_fundamental_scorer()` (line 469), which:
1. Loads `data/fundamentals/fundamental_training_data.parquet`
2. Builds 45 features via `FundamentalsFeatureEngineer`
3. Loads price data via `DataLoader` (for forward-return labels)
4. Builds 6-month forward return labels via `FundamentalLabelBuilder`
5. Trains `FundamentalScorer` with walk-forward split
6. Scores all tickers, saves model + JSON scores

### 3.8 Test Results (503 S&P 500 Stocks)

- 503 tickers fetched (full S&P 500 universe from `config/sp500_tickers.yaml`)
- 21,238 fundamental snapshots across 2015-2026
- 45 `f_` features computed successfully
- Pipeline runtime: ~28 seconds (feature engineering only)
- Coverage: revenue 99%, net_income 100%, total_assets 100%, total_liabilities 100%, operating_cash_flow 86%, shares_outstanding 97%, R&D 32% (only applicable to tech/pharma), Piotroski 100%
- All 11 GICS sectors represented

---

## 4. Six-Step Roadmap

### Step 1: Scale to S&P 500 (~500 tickers) — DONE

**Why highest priority:** Cross-sectional models need breadth across sectors. 28 tech stocks cannot learn sector-relative patterns. With ~500 tickers x ~40 quarters = ~20,000-25,000 training rows.

**Implementation:**
1. Create `config/sp500_tickers.yaml` with the current S&P 500 constituents (obtain from Wikipedia or a static list)
2. Update `config/settings.yaml` to reference the S&P 500 list for fundamental training (keep original 30 tickers for price model)
3. Add `sector` and `industry` columns to the fundamental DataFrame (map via GICS from a static lookup or SEC SIC codes)
4. Run `build_fundamentals_from_edgar()` for all ~500 tickers — expect ~75 minutes at 0.15s/request with caching
5. Validate: ETF tickers will be skipped (no CIK), foreign filers should use IFRS path

**Files to modify:**
- `config/settings.yaml` — add `fundamental.tickers` list (separate from `pipeline.tickers`)
- `pipeline/fundamental_analysis/etl/companyfacts_extractor.py` — add `sector` column passthrough
- `pipeline/main_train.py` — `train_fundamental_models()` reads from `fundamental.tickers`

**Acceptance criteria:** >450 tickers with data, >15,000 fundamental snapshots, all 11 GICS sectors represented.

**Result:** 503 tickers, 21,238 snapshots, all 11 GICS sectors. PASSED.

---

### Step 2: Expand XBRL Extraction (~10 more concepts) — DONE

**Why:** The current 6 concepts are too thin for robust scoring. Key ratios like ROE, gross margin, current ratio, and FCF require additional balance sheet and cash flow items.

**New concepts to add to `CONCEPT_MAP`:**

| Canonical Column | XBRL Tags | Used For |
|-----------------|-----------|----------|
| `stockholders_equity` | StockholdersEquity, StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | ROE |
| `gross_profit` | GrossProfit | Gross margin |
| `operating_income` | OperatingIncomeLoss | Operating margin |
| `current_assets` | AssetsCurrent | Current ratio |
| `current_liabilities` | LiabilitiesCurrent | Current ratio |
| `capital_expenditures` | PaymentsToAcquirePropertyPlantAndEquipment, CapitalExpenditureDiscontinuedOperations | FCF |
| `rd_expense` | ResearchAndDevelopmentExpense | R&D intensity |
| `interest_expense` | InterestExpense, InterestExpenseDebt | Interest coverage |
| `dividends_paid` | PaymentsOfDividendsCommonStock, PaymentsOfDividends | Dividend payout |
| `inventory` | InventoryNet, InventoryFinishedGoods | Inventory days |
| `cost_of_revenue` | CostOfRevenue, CostOfGoodsAndServicesSold | Gross margin (alt) |

**Files to modify:**
- `pipeline/fundamental_analysis/etl/companyfacts_extractor.py` — expand `CONCEPT_MAP`, `IFRS_CONCEPT_MAP`
- Output DataFrame gains ~10 new columns

**Acceptance criteria:** >85% coverage for stockholders_equity, gross_profit, operating_income across S&P 500.

**Result:** 16 concepts implemented. Coverage >85% for stockholders_equity, gross_profit, operating_income. PASSED.

---

### Step 3: Expand Features from 11 to ~40-50 — DONE

**Why:** 11 features is too thin for gradient boosting to learn meaningful cross-sectional patterns. Target ~40-50 features covering profitability, leverage, liquidity, efficiency, valuation, quality, and growth.

**New features to add (grouped by category):**

#### Profitability (add ~5)
| Feature | Formula | Module |
|---------|---------|--------|
| `f_roe` | net_income / stockholders_equity | ratio_calculator |
| `f_gross_margin` | gross_profit / revenue | ratio_calculator |
| `f_operating_margin` | operating_income / revenue | ratio_calculator |
| `f_roic` | operating_income / (total_assets - current_liabilities) | ratio_calculator |
| `f_rd_to_revenue` | rd_expense / revenue | ratio_calculator |

#### Leverage & Liquidity (add ~4)
| Feature | Formula | Module |
|---------|---------|--------|
| `f_current_ratio` | current_assets / current_liabilities | ratio_calculator |
| `f_debt_to_equity` | total_liabilities / stockholders_equity | ratio_calculator |
| `f_interest_coverage` | operating_income / interest_expense | ratio_calculator |
| `f_equity_ratio` | stockholders_equity / total_assets | ratio_calculator |

#### Cash Flow & Quality (add ~4)
| Feature | Formula | Module |
|---------|---------|--------|
| `f_fcf` | operating_cash_flow - capital_expenditures | ratio_calculator |
| `f_fcf_margin` | fcf / revenue | ratio_calculator |
| `f_ocf_to_net_income` | operating_cash_flow / net_income | ratio_calculator |
| `f_capex_to_revenue` | capital_expenditures / revenue | ratio_calculator |

#### Composite Scores (add ~1, 2 deferred)
| Feature | Formula | Module | Status |
|---------|---------|--------|--------|
| `f_piotroski_f` | 9-point F-score (see below) | `piotroski.py` | **Done** |
| `f_altman_z` | Altman Z-score (5-factor) | `altman.py` | Deferred |
| `f_beneish_m` | Beneish M-score (earnings manipulation) | `beneish.py` | Deferred |

#### Growth & Trend (add ~14)
| Feature | Formula | Module |
|---------|---------|--------|
| `f_operating_income_chg_1` | QoQ operating income growth | trend_features |
| `f_gross_profit_chg_1` | QoQ gross profit growth | trend_features |
| `f_operating_cash_flow_chg_1` | QoQ operating cash flow growth | trend_features |
| `f_stockholders_equity_chg_1` | QoQ equity growth | trend_features |
| `f_total_assets_chg_1` | QoQ asset growth | trend_features |
| `f_revenue_chg_4` | YoY revenue growth (4-quarter) | trend_features |
| `f_net_income_chg_4` | YoY net income growth (4-quarter) | trend_features |
| `f_operating_income_chg_4` | YoY operating income growth (4-quarter) | trend_features |
| `f_revenue_rolling_chg_4` | 4-quarter rolling revenue growth | trend_features |
| `f_f_net_margin_trend_4` | 4-quarter OLS slope of net margin | trend_features |
| `f_f_gross_margin_trend_4` | 4-quarter OLS slope of gross margin | trend_features |
| `f_f_operating_margin_trend_4` | 4-quarter OLS slope of operating margin | trend_features |

#### Cross-Sectional (add ~6)
| Feature | Formula | Module |
|---------|---------|--------|
| `f_roe_sector_z` | ROE z-scored within sector | sector_relative |
| `f_margin_sector_z` | Net margin z-scored within sector | sector_relative |
| `f_leverage_sector_z` | Debt-to-assets z-scored within sector | sector_relative |
| `f_growth_sector_z` | Revenue growth z-scored within sector | sector_relative |
| `f_quality_sector_z` | Accruals z-scored within sector | sector_relative |
| `f_size_log_assets` | log(total_assets) — size factor | ratio_calculator |

#### Piotroski F-Score Components (9 binary signals)
1. Positive ROA
2. Positive operating cash flow
3. ROA increasing YoY
4. Cash flow > net income (accrual quality)
5. Leverage decreasing YoY
6. Current ratio increasing YoY
7. No dilution (shares_outstanding not increasing)
8. Gross margin increasing YoY
9. Asset turnover increasing YoY

**Files created:**
- `pipeline/fundamental_analysis/features/piotroski.py` — **Done** (242 lines)
- `pipeline/fundamental_analysis/features/sector_relative.py` — **Done** (124 lines)

**Files not created (deferred):**
- `pipeline/fundamental_analysis/features/altman.py` — Altman Z-score
- `pipeline/fundamental_analysis/features/beneish.py` — Beneish M-score

**Files modified:**
- `pipeline/fundamental_analysis/features/ratio_calculator.py` — 14 new ratios added (20 total)
- `pipeline/fundamental_analysis/features/trend_features.py` — margin trend via OLS slope added
- `pipeline/fundamental_analysis/features/fundamental_feature_engineer.py` — wired all modules
- `pipeline/fundamental_analysis/features/feature_schema_fundamental.yaml` — 45 features documented

**Acceptance criteria:** feature_schema lists 40+ features; >80% non-null rate for core features across S&P 500.

**Result:** 45 features documented in YAML, >80% non-null for core features, 100% for Piotroski. PASSED. (`feature_schema.py` Python-side list is stale at 11 — does not block standalone scorer.)

---

### Step 4: Redesign Fundamental Model as Standalone Scorer — CODE DONE, NOT VALIDATED

**Why:** The current approach trains Ranker/Regressor/Classifier on combined price+fundamental features with a 1-week horizon. This is wrong for fundamentals — quarterly data with 1-week labels is mostly noise. The fundamental model should predict **3-6 month forward returns** and output **interpretable scores**.

**Design:**

```python
class FundamentalScorer:
    """
    Standalone fundamental scoring model.

    Inputs: ~40-50 fundamental features per (ticker, filing_date)
    Outputs: three scores per ticker (updated quarterly)
        quality_score:   float [0, 1]  — business quality (profitability, cash flow, Piotroski)
        value_score:     float [0, 1]  — valuation attractiveness (relative to sector peers)
        trend_score:     float [0, 1]  — earnings/margin trajectory direction

    Training:
        - Label: 6-month forward return quintile (cross-sectional)
        - Model: LightGBM classifier (5-class ordinal) or gradient boosting regressor
        - Retraining cadence: quarterly (after filing season: Feb, May, Aug, Nov)
        - Walk-forward validation with 2-year expanding window
    """
```

**Label construction:**
1. For each (ticker, filing_date), compute the 6-month forward return from `filing_date` to `filing_date + 126 trading days`
2. Cross-sectionally rank into quintiles (1=worst, 5=best) per filing quarter
3. Train classifier to predict quintile from fundamental features only (no price features)

**Score decomposition:**
- `quality_score`: weighted combination of Piotroski F-score, accrual quality, OCF/NI ratio, margin stability
- `value_score`: sector-relative valuation (ROE vs. market-to-book, FCF yield vs. peers)
- `trend_score`: direction of margin, revenue growth, and earnings trajectory over last 4 quarters

**Files created:**
- `pipeline/fundamental_analysis/models/fundamental_scorer.py` — **Done** (458 lines)
- `pipeline/fundamental_analysis/models/label_builder.py` — **Done** (334 lines)

**Files modified:**
- `pipeline/main_train.py` — `train_fundamental_scorer()` added, `--mode fundamental_scorer` CLI option

**Acceptance criteria:** FundamentalScorer produces quality/value/trend scores for all S&P 500 tickers; walk-forward IC (information coefficient) > 0.05 on held-out quarters.

**Result:** Code implemented and syntax-verified. **NOT VALIDATED** — requires price data on disk to build labels and train. Walk-forward IC not yet measured.

---

### Step 5: Build Integration Layer — CODE DONE, NOT VALIDATED

**Why:** Connect fundamental scores to the existing SlotSelector decisions in `main_inference.py`.

**Design:**

```python
# In main_inference.py, after Step 6 (SlotSelector produces decisions):

def apply_fundamental_overlay(decisions, fundamental_scores, config):
    """
    Modify BUY/SELL/HOLD decisions based on fundamental scores.

    Rules:
    1. BUY + high quality + high value + positive trend → STRONG BUY (keep, increase confidence)
    2. BUY + low quality OR deteriorating trend → WARN (keep BUY but flag risk)
    3. BUY + very low quality (F-score < 3) + negative trend → DOWNGRADE to HOLD
    4. SELL → always SELL (fundamentals never override)
    5. HOLD + high quality + high value → consider for BUY shortlist (queue for next cycle)

    Thresholds are configurable in config["fundamental"]["overlay"].
    """
```

**Integration points:**
- `main_inference.py` — Step 7 (fundamental overlay) after Step 6 (SlotSelector)
- `config/settings.yaml` — `fundamental.overlay` section with thresholds
- Fundamental scores loaded from a persisted file (updated quarterly by `train_fundamental_scorer()`)

**Score persistence:**
- `data/fundamentals/fundamental_scores.json` — latest scores per ticker
- Updated after each quarterly model retraining
- Loaded at inference time as a static lookup

**Files created:**
- `pipeline/fundamental_analysis/integration/overlay.py` — **Done** (258 lines)

**Files modified:**
- `pipeline/main_inference.py` — Step 7 wired with try/except fallback

**Acceptance criteria:** inference pipeline runs end-to-end with overlay; decisions annotated with STRONG_BUY/WARN/DOWNGRADE.

**Result:** Code implemented, dead-code bug fixed, and smoke-tested (BUY->STRONG_BUY, BUY->DOWNGRADE, BUY->WARN, SELL->SELL all correct). Overlay result is now used for printing, position persistence, and LLM analyst. **NOT VALIDATED** end-to-end — requires `fundamental_scores.json` from a trained scorer.

---

### Step 6: Backtest Combined System — CODE DONE, NOT VALIDATED

**Why:** Validate that the fundamental overlay actually improves risk-adjusted returns vs. price-only.

**Methodology:**
1. Run existing walk-forward backtest with price-only model (baseline)
2. Run same backtest with fundamental overlay applied to decisions
3. Compare: Sharpe ratio, max drawdown, win rate, turnover, sector concentration

**Expected improvements (realistic):**
- 5-15% drawdown reduction (fundamental filter avoids buying into deteriorating businesses)
- 2-5% improvement in risk-adjusted returns
- Reduced turnover (fundamental filter adds stability to BUY decisions)
- Better sector diversification (S&P 500 universe + sector-relative features)

**Files modified:**
- `pipeline/main_backtest.py` — added `--fundamental-overlay` and `--fundamental-scores-path` flags, `_load_overlay_scores()` helper
- `pipeline/ohlcv/backtest/backtester.py` — added `fundamental_scores` and `fundamental_config` parameters; overlay applied after daily `selector.select()`

**Acceptance criteria:** Sharpe ratio improves by >0.05 with fundamental overlay vs. price-only on 2023-2026 walk-forward test.

**Result:** Code implemented and integration-tested. `--fundamental-overlay` flag works in both `backtest` and `wf-backtest` modes. DOWNGRADE correctly removes tickers from target positions. **NOT VALIDATED** — requires `fundamental_scores.json` from a trained scorer, which requires price data (AC-4).

**See also:** `notebooks/rel2_backtest_inference_logic.md` for detailed data flow and A/B comparison workflow.

---

## 5. Data Flow (End-to-End)

```
SEC EDGAR Company Facts API (free, no API key)
    |
    v
EdgarClient.get_company_facts(ticker)
    |  HTTP GET → data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
    |  Cached locally: data/fundamentals/edgar_cache/companyfacts_{TICKER}_{CIK}.json
    v
companyfacts_extractor.extract_fundamentals_for_ticker()
    |  CONCEPT_MAP → 16 canonical columns
    |  Filters: VALID_FORMS only, dedup on (filed, end)
    |  Point-in-time: uses 'filed' date for filing_date
    v
Raw fundamental DataFrame:
    [ticker, filing_date, period_end, form, fiscal_year, fiscal_period,
     revenue, net_income, total_assets, total_liabilities,
     operating_cash_flow, shares_outstanding, stockholders_equity,
     gross_profit, operating_income, current_assets, current_liabilities,
     capital_expenditures, rd_expense, interest_expense, dividends_paid,
     cost_of_revenue, ...]
    |
    v
FundamentalsFeatureEngineer.build_fundamental_features()
    |
    ├── ratio_calculator.compute_ratio_panel()
    |       → 20 ratio features (f_net_margin, f_roa, f_roe, f_gross_margin,
    |         f_operating_margin, f_roic, f_current_ratio, f_debt_to_equity, ...)
    |
    ├── accruals.compute_accruals()
    |       → f_accruals, f_accruals_std
    |
    ├── trend_features.compute_growth_features()
    |       → f_revenue_chg_1, f_net_income_chg_1, f_operating_income_chg_1, ...
    |
    ├── trend_features.compute_rolling_growth()
    |       → f_revenue_rolling_chg_4
    |
    ├── trend_features.compute_margin_trend()
    |       → f_f_net_margin_trend_4, f_f_gross_margin_trend_4, f_f_operating_margin_trend_4
    |
    ├── piotroski.compute_piotroski_f_score()
    |       → f_piotroski_f, f_piotroski_profitability, f_piotroski_leverage, f_piotroski_efficiency
    |
    ├── sector_relative.compute_sector_z_scores()
    |       → f_roe_sector_z, f_net_margin_sector_z, f_debt_to_assets_sector_z, ...
    |
    v
Fundamental feature DataFrame (quarterly, 45 columns)
    |
    +---[FOR COMBINED TRAINING]---→ FeatureJoiner.join(method="asof")
    |                                  merge_asof(backward) with daily OHLCV features
    |                                  → combined training DataFrame (25+ features per daily row)
    |
    +---[FOR STANDALONE SCORER]---→ FundamentalScorer.fit()
                                       → quality_score, value_score, trend_score per ticker
                                       → saved to data/fundamentals/fundamental_scores.json
                                       → loaded by main_inference.py as overlay
```

---

## 6. File Reference (for AI Coding Agents)

### ETL Layer
| File | Key Exports | Notes |
|------|-------------|-------|
| `pipeline/fundamental_analysis/etl/__init__.py` | `EdgarClient`, `build_fundamentals_from_edgar`, `extract_fundamentals_for_ticker`, `CONCEPT_MAP` | Re-exports |
| `pipeline/fundamental_analysis/etl/edgar_client.py` | `EdgarClient` class | `get_company_facts()`, `list_filings()`, `get_cik_for_ticker()` |
| `pipeline/fundamental_analysis/etl/companyfacts_extractor.py` | `CONCEPT_MAP`, `IFRS_CONCEPT_MAP`, `VALID_FORMS`, `extract_fundamentals_for_ticker()`, `build_fundamentals_from_edgar()` | The core extraction logic |
| `pipeline/fundamental_analysis/etl/universe_manager.py` | `UniverseManager` class | `get_sp500()`, `get_test_universe()`, `from_config()`, `from_file()`, `resolve_universe()` |
| `pipeline/fundamental_analysis/etl/xbrl_parser.py` | `XBRLParser` class | Deprecated — `parse()`, zip/iXBRL extraction, canonical metric building |
| `pipeline/fundamental_analysis/etl/point_in_time.py` | `PointInTimeManager` class | `ensure_snapshots()`, `list_snapshots()`, `get_snapshot()` |
| `pipeline/fundamental_analysis/etl/restatement_tracker.py` | `RestatementTracker` class | `scan_and_mark()`, 3-level heuristic detection |
| `pipeline/fundamental_analysis/etl/data_ingest_scheduler.py` | `DataIngestScheduler` class | `run_incremental_ingest()`, `fetch_price_proxies()`, `get_last_run_info()` |
| `pipeline/fundamental_analysis/etl/etl_inspect.py` | Utility functions | Data inspection and validation |

### Feature Engineering Layer
| File | Key Exports | Notes |
|------|-------------|-------|
| `pipeline/fundamental_analysis/features/__init__.py` | Re-exports | |
| `pipeline/fundamental_analysis/features/ratio_calculator.py` | `compute_basic_ratios()`, `compute_ratio_panel()` | 20 ratio features |
| `pipeline/fundamental_analysis/features/accruals.py` | `compute_accruals()` | 2 accrual features |
| `pipeline/fundamental_analysis/features/trend_features.py` | `compute_growth_features()`, `compute_rolling_growth()`, `compute_margin_trend()` | Up to 14 growth/trend features |
| `pipeline/fundamental_analysis/features/piotroski.py` | `compute_piotroski_f_score()` | 4 Piotroski features (composite + 3 sub-scores) |
| `pipeline/fundamental_analysis/features/sector_relative.py` | `compute_sector_z_scores()` | 5 sector-relative Z-score features |
| `pipeline/fundamental_analysis/features/fundamental_feature_engineer.py` | `FundamentalsFeatureEngineer`, `FeatureJoiner` | Orchestrates all feature modules |
| `pipeline/fundamental_analysis/features/feature_schema_fundamental.yaml` | (YAML) | Authoritative schema for all 45 features |

### Models Layer
| File | Key Exports | Notes |
|------|-------------|-------|
| `pipeline/fundamental_analysis/models/__init__.py` | Re-exports | |
| `pipeline/fundamental_analysis/models/fundamental_scorer.py` | `FundamentalScorer`, `QUALITY_FEATURES`, `VALUE_FEATURES`, `TREND_FEATURES` | LightGBM-based scorer with 3 sub-models |
| `pipeline/fundamental_analysis/models/label_builder.py` | `FundamentalLabelBuilder` | 6-month forward return quintile labels |

### Integration Layer
| File | Key Exports | Notes |
|------|-------------|-------|
| `pipeline/fundamental_analysis/integration/__init__.py` | Re-exports | |
| `pipeline/fundamental_analysis/integration/overlay.py` | `apply_fundamental_overlay()`, `load_fundamental_scores()` | STRONG_BUY / WARN / DOWNGRADE overlay rules |

### Data Providers
| File | Key Exports | Notes |
|------|-------------|-------|
| `pipeline/fundamental_analysis/data_providers/fmp_client.py` | `FMPClient` class | Alternative data provider (Financial Modeling Prep API) |

### Price Model Layer (for context)
| File | Key Exports | Notes |
|------|-------------|-------|
| `pipeline/ohlcv/dataset/feature_schema.py` | `PRICE_FEATURES`, `FUNDAMENTAL_FEATURES`, `ALL_FEATURES`, `MODEL_FEATURES` | Central feature registry (FUNDAMENTAL_FEATURES is stale at 11) |
| `pipeline/ohlcv/dataset/ohlcv_feature_engineer.py` | `OhlcvFeatureEngineer` | 14 price features |
| `pipeline/ohlcv/models/model_factory.py` | `ModelFactory` | Config-driven model creation (LightGBM, XGBoost, sklearn) |
| `pipeline/ohlcv/models/base_model.py` | `BaseModel` ABC | `train()`, `predict()`, `predict_proba()`, `feature_importance()` |
| `pipeline/ohlcv/models/model_manager.py` | `ModelManager` | Save/load with `.meta.json` sidecar |
| `pipeline/ohlcv/policy/slot_selector.py` | `SlotSelector` | 3-slot BUY/SELL/HOLD with opportunity scoring |

### Tests
| File | Key Tests | Notes |
|------|-----------|-------|
| `pipeline/fundamental_analysis/tests/test_xbrl_parser.py` | `test_parse_simple_xbrl` | 42 lines, 1 test — minimal coverage |

### Entry Points
| File | Key Functions | Notes |
|------|---------------|-------|
| `pipeline/main_train.py` | `train_price_models()`, `train_fundamental_models()`, `train_fundamental_scorer()` | `--mode price\|fundamental\|fundamental_full\|fundamental_scorer\|both` |
| `pipeline/main_inference.py` | `main()` | Daily inference pipeline (Step 7 = fundamental overlay) |
| `pipeline/main_backtest.py` | Walk-forward backtesting | **No fundamental integration yet** |

### Config
| File | Relevant Sections | Notes |
|------|-------------------|-------|
| `config/settings.yaml` | `fundamental.edgar.*`, `fundamental.store_root`, `pipeline.tickers`, `models.*`, `features.*` | All config |
| `config/sp500_tickers.yaml` | 503 tickers with sector and CIK | Universe definition |

---

## 7. Configuration Reference

```yaml
# config/settings.yaml — fundamental section

fundamental:
  store_root: "data/fundamentals"          # root for all fundamental data
  edgar:
    user_agent_email: "you@example.com"    # required by SEC
    min_request_interval: 0.15             # seconds between requests (SEC allows 10/s)
    timeout: 30                            # HTTP timeout
    max_retries: 3                         # retry on 429/503
  tickers: "config/sp500_tickers.yaml"     # path to S&P 500 universe list
  overlay:
    enabled: true                          # enable/disable fundamental overlay in inference
    quality_threshold: 0.4                 # below this → WARN
    downgrade_threshold: 0.2              # below this → DOWNGRADE BUY to HOLD
    piotroski_min: 3                       # F-score floor for BUY confirmation
  scheduler:
    lookback_days: 3650                    # ~10 years of history
    fetch_price_proxies: false
```

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| XBRL tag inconsistency across companies | Missing data, broken ratios | Multi-tag lookup (CONCEPT_MAP), IFRS fallback, >85% coverage threshold |
| SEC rate limiting (429 errors) | Slow/blocked ETL | 0.15s interval, exponential backoff, local JSON cache |
| Foreign filers (TSM, ASML) use IFRS | Missing from US-GAAP extraction | IFRS_CONCEPT_MAP with ifrs-full taxonomy |
| Quarterly data lag (filings arrive 30-60 days after period end) | Stale signals | Use `filed` date for point-in-time; accept lag as feature |
| Overfitting on 11 features with 1,034 rows | Poor generalization | Scale to S&P 500 (25,000+ rows) before expanding model complexity |
| Fundamental overlay too aggressive | Kills good price trades | Start conservative (WARN only, no DOWNGRADE); tune thresholds with backtest |
| Survivorship bias in S&P 500 constituent list | Inflated backtests | Use point-in-time constituent lists if available; document this limitation |
| FundamentalScorer trained without price data | All-NaN labels, useless model | Ensure price data parquet exists before running `--mode fundamental_scorer` |

---

## 9. What to Deprioritize

These were mentioned in the original research document but should be deferred:

- **Altman Z-score and Beneish M-score** — mentioned in Step 3 but not blocking. Can be added later as additional composite features.
- **Transfer learning on filing text / MD&A NLP** — requires LLM infrastructure, marginal value vs. structured features
- **Synthetic data (GANs/VAEs)** — premature before we have real cross-sectional breadth
- **Earnings surprise prediction** — needs analyst consensus estimates (paid data)
- **FRED macro features** — useful but orthogonal to the fundamental scoring design; add later as enrichment

---

## 10. Release-2 Acceptance Criteria

### Must-Have (blocking release closure)

| # | Criterion | Metric | Status |
|---|-----------|--------|--------|
| **AC-1** | S&P 500 universe ingestion | >450 tickers with data, >15,000 snapshots, all 11 GICS sectors | **PASSED** (503 tickers, 21,238 snapshots) |
| **AC-2** | XBRL concept expansion | >85% coverage for stockholders_equity, gross_profit, operating_income | **PASSED** (16 concepts implemented) |
| **AC-3** | Feature breadth | 40+ fundamental features with >80% non-null rate for core features | **PASSED** (45 features, Piotroski at 100%) |
| **AC-4** | Price data available | `data/processed/price_data.parquet` exists for all S&P 500 tickers | **NOT DONE** — required for AC-5 and AC-7 |
| **AC-5** | FundamentalScorer trained | `fundamental_scores.json` produced with quality/value/trend scores for >450 tickers | **NOT DONE** — blocked by AC-4 |
| **AC-6** | Walk-forward IC | Information coefficient > 0.05 on held-out quarters | **NOT MEASURED** — blocked by AC-5 |
| **AC-7** | Backtest integration | `main_backtest.py` supports `--fundamental-overlay` flag; runs with/without overlay | **DONE** — code implemented, integration-tested |
| **AC-8** | Sharpe improvement | Sharpe ratio improves by >0.05 with overlay vs. price-only on 2023-2026 walk-forward | **NOT MEASURED** — blocked by AC-7 |

### Should-Have (quality / correctness, not blocking)

| # | Criterion | Status |
|---|-----------|--------|
| **SH-1** | Sync `feature_schema.py` FUNDAMENTAL_FEATURES list from 11 to 45 | **NOT DONE** — only affects `--mode fundamental_full`, not standalone scorer |
| **SH-2** | Overlay runs end-to-end in `main_inference.py` with real scores | **CODE DONE** — dead-code bug fixed, overlay result now used for printing, position persistence, and LLM. Needs real `fundamental_scores.json` to validate end-to-end. |
| **SH-3** | `config/settings.yaml` overlay section uncommented | **NOT DONE** — thresholds exist as code defaults in `overlay.py` |

### Nice-to-Have (completeness, explicitly deferred)

| # | Criterion | Status |
|---|-----------|--------|
| **NH-1** | Altman Z-score module (`altman.py`) | Deferred |
| **NH-2** | Beneish M-score module (`beneish.py`) | Deferred |
| **NH-3** | Test coverage for feature modules | 1 test file (42 lines) across 25 modules |
| **NH-4** | `universe_manager.py` full 503-ticker hardcoded list | Currently ~100 hardcoded; full list in `config/sp500_tickers.yaml` |

### Critical Path to Closure

```
AC-4 (price data) → AC-5 (train scorer) → AC-6 (measure IC)
                                        ↘
AC-7 (backtest code) ---- DONE --------→ AC-8 (measure Sharpe, blocked by AC-5)
```

**AC-4 is the single blocking dependency.** Once price data is on disk:
1. Run `--mode fundamental_scorer` to train and produce scores (AC-5)
2. Measure walk-forward IC from the scorer output (AC-6)
3. Run `--mode wf-backtest --fundamental-overlay` to compare Sharpe (AC-8) — code is ready

### File Inventory Summary

| Layer | Files | Total Lines | Status |
|-------|-------|-------------|--------|
| ETL | 8 Python files | ~3,581 | All implemented |
| Features | 6 Python files + 1 YAML | ~1,234 + 215 | All implemented |
| Models | 2 Python files | ~792 | Code done, not validated |
| Integration | 1 Python file | ~258 | Code done, not validated |
| Tests | 1 Python file | ~42 | Minimal |
| **Total** | **18 Python + 1 YAML** | **~6,122** | |
