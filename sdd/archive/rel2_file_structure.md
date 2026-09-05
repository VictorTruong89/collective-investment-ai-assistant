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

### Actual directory tree (as-built, rel-2)

```
ai-investment-pipeline
├── config
│   ├── env.yaml
│   ├── settings.yaml
│   └── sp500_tickers.yaml
├── logs
│   ├── pipeline.log
│   └── wf_backtest_results.csv
├── notebooks
│   ├── rel1_document.md
│   ├── rel1_improvement_strategy.md
│   ├── rel2_backtest_inference_logic.md
│   ├── rel2_file_structure.md                   ← this file
│   ├── rel2_how_AI_analyze_fundamentals.md
│   └── rel2_IMPLEMENTATION_SUMMARY.md
├── reports
│   └── backtest_reports
│       ├── backtest_drawdown.png
│       ├── backtest_equity_curve.csv
│       ├── backtest_equity_curve.png
│       ├── backtest_metrics.csv
│       └── backtest_recommendations_debug.csv
└── pipeline
    ├── __init__.py
    ├── inspect_data.py
    ├── main_backtest.py
    ├── main_inference.py
    ├── main_train.py
    ├── fundamental_analysis
    │   ├── __init__.py
    │   ├── data_providers
    │   │   ├── __init__.py
    │   │   └── fmp_client.py
    │   ├── etl
    │   │   ├── __init__.py
    │   │   ├── companyfacts_extractor.py
    │   │   ├── data_ingest_scheduler.py
    │   │   ├── edgar_client.py
    │   │   ├── etl_inspect.py
    │   │   ├── point_in_time.py
    │   │   ├── restatement_tracker.py
    │   │   ├── universe_manager.py
    │   │   └── xbrl_parser.py
    │   ├── features
    │   │   ├── __init__.py
    │   │   ├── accruals.py
    │   │   ├── feature_schema_fundamental.yaml
    │   │   ├── fundamental_feature_engineer.py
    │   │   ├── piotroski.py
    │   │   ├── ratio_calculator.py
    │   │   ├── sector_relative.py
    │   │   └── trend_features.py
    │   ├── integration
    │   │   ├── __init__.py
    │   │   └── overlay.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   ├── fundamental_scorer.py
    │   │   └── label_builder.py
    │   └── tests
    │       └── test_xbrl_parser.py
    ├── llm
    │   ├── __init__.py
    │   └── llm_analyst.py
    ├── ohlcv
    │   ├── __init__.py
    │   ├── backtest
    │   │   ├── __init__.py
    │   │   ├── backtester.py
    │   │   ├── backtest_report.py
    │   │   └── metrics.py
    │   ├── dataset
    │   │   ├── __init__.py
    │   │   ├── data_loader.py
    │   │   ├── feature_schema.py
    │   │   ├── feature_selector.py
    │   │   ├── label_builder.py
    │   │   └── ohlcv_feature_engineer.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   ├── base_model.py
    │   │   ├── classifier_model.py
    │   │   ├── lightgbm_models.py
    │   │   ├── model_factory.py
    │   │   ├── model_manager.py
    │   │   ├── ranker_model.py
    │   │   ├── regressor_model.py
    │   │   ├── sklearn_models.py
    │   │   └── xgboost_models.py
    │   └── policy
    │       ├── __init__.py
    │       ├── policy_params.json
    │       └── slot_selector.py
    └── utils
        ├── __init__.py
        ├── logger.py
        └── utils.py
```

---

### What changed from the rel-2 design plan

| Planned | As-built | Note |
|---|---|---|
| `fundamental_analysis/sources/` | **Removed** | Replaced by `data_providers/` using FMP REST API |
| `fundamental_analysis/nlp/` | **Not implemented** | Deferred; LLM analysis handled by `pipeline/llm/` instead |
| `fundamental_analysis/scoring/` | **Merged into `features/`** | `piotroski.py` lives in `features/`; Altman-Z deferred |
| `fundamental_analysis/integration/feature_joiner.py` | `integration/overlay.py` | Scope narrowed to fundamental overlay on SlotSelector decisions |
| `main_fundamental_train.py` | **Removed** | Consolidated into `main_train.py --mode both` |
| `main_fundamental_inference.py` | **Removed** | Consolidated into `main_inference.py` |
| `feature_schema_fundamental.py` | `feature_schema_fundamental.yaml` | YAML format retained |
| `trend_features.yaml` | `trend_features.py` | Implemented as Python module |

---

### Purpose and intention of new folders and files

**`config/sp500_tickers.yaml`**
Static list of S&P 500 tickers used for universe expansion beyond the 30 core watchlist tickers in `settings.yaml`. Provides a reference universe for cross-sectional ranking.

---

**`pipeline/fundamental_analysis/data_providers/`**
Replaces the planned `sources/` folder. Provides a single pre-parsed REST API client instead of raw SEC EDGAR downloads, eliminating the need for in-pipeline XBRL parsing for the primary data path.

- **`fmp_client.py`**
  Thin caching wrapper around the Financial Modeling Prep (FMP) REST API. Fetches income statements, balance sheets, and cash-flow statements; merges them into the canonical `(ticker, filing_date, period_end, revenue, net_income, total_assets, total_liabilities, operating_cash_flow, shares_outstanding)` schema. Writes a local parquet cache (`data/fundamentals/fmp_cache/`) with a configurable TTL so the API is only hit on expiry. ETF tickers (VOO, ONEQ, etc.) are skipped automatically.

---

**`pipeline/fundamental_analysis/etl/`**
Retained as the SEC EDGAR fallback path and for point-in-time correctness tooling. Primary data flow now goes through `data_providers/fmp_client.py`; EDGAR tooling is used for validation, restatement tracking, and as a free alternative when FMP quota is exhausted.

- **`companyfacts_extractor.py`** *(new)*
  Pulls structured company facts directly from the SEC `data.sec.gov/api/xbrl/companyfacts/` endpoint. Provides a lighter alternative to full XBRL zip parsing for common GAAP tags (revenue, EPS, assets).

- **`etl_inspect.py`** *(new)*
  Developer utility for inspecting raw ETL outputs — prints snapshot counts, filing coverage, and NaN rates per ticker. Used during debugging and data-quality checks; not part of the production pipeline.

- **`edgar_client.py`** — Lightweight client for SEC EDGAR endpoints (CIK resolution, filing discovery, raw download). Handles rate-limiting, retries with exponential backoff, and local caching.

- **`xbrl_parser.py`** — Parses XBRL facts from downloaded filing zips into normalised tables (facts, contexts, units). Emits canonical numeric time series per ticker and accession.

- **`point_in_time.py`** — Builds and serves point-in-time snapshots keyed on `(ticker, filing_date, accession_id)` to prevent look-ahead bias in backtests.

- **`restatement_tracker.py`** — Detects and records restatements; links them to original filings and flags affected historical snapshots.

- **`data_ingest_scheduler.py`** — Orchestrates periodic pulls, incremental updates, and local caching; emits ingestion logs for lineage.

- **`universe_manager.py`** — Manages the set of tracked tickers; resolves CIK mappings and handles additions/removals.

---

**`pipeline/fundamental_analysis/features/`**
Computes all `f_*` fundamental features consumed by the combined training path in `main_train.py --mode both`.

- **`fundamental_feature_engineer.py`**
  Central orchestrator. `build_combined_features(price_data, fundamental_snapshots)` merges OHLCV features with quarterly fundamental snapshots via forward-filling, producing the combined feature DataFrame written to `data/fundamentals/combined_features_for_fundamental_training.parquet`.

- **`ratio_calculator.py`**
  Computes canonical financial ratios: `f_net_margin`, `f_roa`, `f_eps`, `f_ocf_to_assets`, `f_debt_to_assets`, `f_market_to_book`.

- **`accruals.py`**
  Implements accrual measures (`f_accruals`, `f_accruals_std`) and detects accounting-quality anomalies using the balance-sheet method.

- **`trend_features.py`**
  Generates QoQ/YoY growth and rolling momentum features: `f_revenue_chg_1`, `f_net_income_chg_1`, `f_revenue_rolling_chg_4`.

- **`piotroski.py`** *(moved from planned `scoring/`)*
  Deterministic Piotroski F-Score implementation (9 binary tests across profitability, leverage, and operating efficiency). Used as a fast screening signal and as a baseline for ML model validation.

- **`sector_relative.py`** *(new)*
  Computes sector-relative versions of fundamental ratios. Normalises each metric against the median of its GICS sector within the universe, producing cross-sectionally comparable signals.

- **`feature_schema_fundamental.yaml`**
  Single source of truth for all `f_*` feature names, units, and types. The 11 features defined here (`f_net_margin`, `f_roa`, `f_eps`, `f_ocf_to_assets`, `f_debt_to_assets`, `f_market_to_book`, `f_accruals`, `f_accruals_std`, `f_revenue_chg_1`, `f_net_income_chg_1`, `f_revenue_rolling_chg_4`) are the canonical fundamental feature set consumed by training.

---

**`pipeline/fundamental_analysis/integration/`**
Scope narrowed from the original design: no general feature joiner or dataset adapter. Focuses solely on the fundamental overlay applied at inference and backtest time.

- **`overlay.py`**
  `load_fundamental_scores(path)` — loads pre-computed per-ticker health scores from JSON.
  `apply_fundamental_overlay(decisions, scores, config)` — augments SlotSelector decisions with `STRONG_BUY / BUY / HOLD / WARN / DOWNGRADE` actions derived from the fundamental scorer. `DOWNGRADE` removes a ticker from that day's target positions without overriding the price-model ranking for all others.

---

**`pipeline/fundamental_analysis/models/`**

- **`fundamental_scorer.py`**
  Produces a composite health score per ticker from the `f_*` feature set. Combines Piotroski sub-scores with ratio-based signals into a single scalar used by `overlay.py`.

- **`label_builder.py`** *(new)*
  Builds forward-return labels aligned to quarterly filing dates for training fundamental models. Separate from `ohlcv/dataset/label_builder.py` because the time alignment (filing date → next-quarter return) differs from the daily OHLCV label logic.

---

**`pipeline/fundamental_analysis/tests/`**

- **`test_xbrl_parser.py`**
  Unit tests for XBRL parsing correctness, snapshot creation, and absence of look-ahead leakage.

---

**`pipeline/llm/`** *(new — not in original design)*
Advisory LLM layer added in rel-2. Provides qualitative commentary on quantitative BUY picks. Does not override model decisions.

- **`llm_analyst.py`**
  Wraps the Google Gemini API (`gemini-2.0-flash`). For each BUY ticker from SlotSelector, builds a prompt containing the model scores and last 4 quarters of financial data, then requests a 200-word analyst review (key risks, fundamental alignment, red flags, verdict). Falls back gracefully when the API key is missing or quota is exhausted (free-tier: ~1,500 requests/day). Toggle via `llm.enabled` in `settings.yaml`.

---

**`pipeline/ohlcv/dataset/feature_schema.py`** *(updated)*
Now defines three tiers:
- `PRICE_FEATURES` (14) — the original OHLCV "Golden List"
- `FUNDAMENTAL_FEATURES` (11) — all `f_*` features
- `ALL_FEATURES` (25) — union used by combined training
- `MODEL_FEATURES` — alias for `PRICE_FEATURES` for backward compatibility

**`pipeline/ohlcv/dataset/feature_selector.py`** *(new)*
Config-driven feature selection at training time. Supports `mode: all` (use all available features), `mode: price_only` (PRICE_FEATURES only), and `mode: importance` (two-pass training: first pass selects top-K features by LightGBM gain, second pass retrains on the refined set).

---

**`pipeline/ohlcv/models/`** *(significantly expanded)*
Refactored from three monolithic model files into a backend-agnostic hierarchy.

- **`base_model.py`** — Abstract `BaseModel` with `train()`, `predict()`, `predict_proba()`, `feature_importance()`, `save()`, `load()`. All concrete backends inherit from this.

- **`lightgbm_models.py`** — `LightGBMModel` subclass for ranker (LambdaRank), regressor (RMSE), and classifier (binary log-loss) roles. Matches the original hardcoded LightGBM parameters for backward compatibility.

- **`xgboost_models.py`** — `XGBoostModel` subclass. Drop-in alternative to LightGBM selected via `settings.yaml`.

- **`sklearn_models.py`** — `SklearnModel` subclass wrapping RandomForest and GradientBoosting. Useful for quick baseline comparisons without GPU.

- **`model_factory.py`** — `ModelFactory(config)` reads `models.backend` from `settings.yaml` and returns the correct backend instance for a given role. Centralises the backend selection so training scripts need no `if/else` logic.

- **`model_manager.py`** *(updated)* — Now writes a `.meta.json` sidecar alongside each `.pkl` recording `backend`, `feature_names`, and training timestamp. `get_feature_names(model_type)` is used by `main_backtest.py` and `main_inference.py` to reconstruct the exact feature set without hard-coding it.

- **`ranker_model.py`, `regressor_model.py`, `classifier_model.py`** — Legacy wrappers retained for backward compatibility; delegate to `LightGBMModel` internally.

---

**`pipeline/main_train.py`** *(consolidated)*
Single entry point for all training modes:
- `--mode price` — trains price-only models on `PRICE_FEATURES` (14 features)
- `--mode fundamental` — fetches FMP data, builds fundamental snapshots, writes `data/fundamentals/fundamental_training_data.parquet`
- `--mode both` — runs price training first, then combined price+fundamental training; the combined models (21 features) overwrite the price-only versions as the latest saved model

**`pipeline/main_backtest.py`** *(updated)*
Detects whether the latest saved model was trained on fundamental features (by inspecting `.meta.json`). If so, loads `data/fundamentals/combined_features_for_fundamental_training.parquet` and left-joins the `f_*` columns into the test DataFrame before prediction. Prevents the 21-vs-14 feature mismatch at backtest time.

**`pipeline/main_inference.py`** *(updated)*
Same fundamental feature merge as `main_backtest.py`. For daily inference, uses the most recent row per ticker from the combined features parquet (quarterly fundamental data forward-fills validly to daily frequency).

---

### Data files written at runtime

```
data/
├── current_positions.json         ← persisted portfolio positions (main_inference.py)
├── fundamentals/
│   ├── fmp_cache/
│   │   └── fmp_fundamentals.parquet       ← raw FMP fetch cache (TTL: 7 days)
│   ├── fundamental_training_data.parquet  ← canonical snapshots (main_train --mode fundamental)
│   ├── combined_features_for_fundamental_training.parquet  ← OHLCV + f_* merged
│   └── fundamental_scores.json            ← per-ticker health scores (FundamentalScorer)
trained_models/
│   ├── version_registry.json
│   ├── ranker/
│   │   ├── ranker_YYYY-MM-DD.pkl
│   │   └── ranker_YYYY-MM-DD.meta.json    ← feature_names + backend recorded here
│   ├── regressor/
│   └── classifier/
reports/
└── backtest_reports/
    ├── backtest_equity_curve.csv / .png
    ├── backtest_drawdown.png
    ├── backtest_metrics.csv
    └── backtest_recommendations_debug.csv
```

---

### How the pipeline components integrate end-to-end

```
DataLoader ──► OhlcvFeatureEngineer ──────────────────────────────┐
                                                                   │
FMPClient ──► FundamentalsFeatureEngineer.build_combined_features ─┤
                                                                   ▼
                                               combined_features DataFrame
                                                        │
                                              FeatureSelector.select()
                                                        │
                                              ModelFactory → LightGBMModel
                                                        │
                                           ModelManager.save_new_version()
                                              (writes .pkl + .meta.json)

───────────────────── inference / backtest ─────────────────────────

ModelManager.load_latest() + get_feature_names()
        │
        ├── if f_* features required → merge combined_features parquet
        │
        ▼
ranker.predict() / regressor.predict() / classifier.predict_proba()
        │
SlotSelector.select()
        │
apply_fundamental_overlay()   ← overlay.py (DOWNGRADE removes position)
        │
LLMAnalyst.analyze_picks()    ← advisory commentary only
        │
output: decisions + annotations
```

---

### Not yet implemented (deferred from rel-2 design)

- `fundamental_analysis/sources/` — FRED macro client, price proxy (not needed; FMP covers these)
- `fundamental_analysis/nlp/` — earnings transcript scraper, MD&A extractor, FinBERT adapter
- `fundamental_analysis/scoring/altman_z.py` and `composite_health_score.py`
- `fundamental_analysis/docs/README.md`
- Altman Z-Score and multi-signal composite health scoring
- Restatement-aware backtest re-runs
- SHAP explainability output alongside model artifacts
