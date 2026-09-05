## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

The Data Engine is the **foundation layer** of the AI Investment Pipeline.
It is responsible for acquiring, normalizing, validating, storing, and
serving all data consumed by every other domain in the system. Without
reliable data, every analysis, signal, recommendation, and risk assessment
built on top of it is worthless.

The Data Engine answers one question:

> **"Give me clean, validated, current data for any ticker in the
> system, in a standard format, as fast as possible, regardless of
> which external provider supplied it."**

Every other domain — Research, Quantitative, Portfolio, Risk, Reporting —
is a consumer of the Data Engine. No other domain fetches external data
directly. No other domain stores raw market or fundamental data. The Data
Engine owns the full lifecycle of data from external acquisition through
internal delivery.

## Scope

### In Scope

| Responsibility                         | Description                                           |
|----------------------------------------|-------------------------------------------------------|
| Market data acquisition                | OHLCV daily bars, quotes, index data                  |
| Fundamental data acquisition           | Income statements, balance sheets, cash flow           |
| News and sentiment acquisition         | News articles, sentiment scores                        |
| SEC filing acquisition                 | EDGAR filings (10-K, 10-Q, 8-K, Form 4)              |
| Company reference data                 | Profiles, sector, market cap, shares outstanding       |
| Provider management                    | Adapter layer, failover, rate limiting, health         |
| Data normalization                     | Canonical model translation, cents conversion, UTC     |
| Data validation                        | Schema checks, quality rules, anomaly detection        |
| Data storage                           | Persistence, upsert, retrieval, indexing               |
| Data caching                           | Cache-aside pattern, TTL management, invalidation      |
| Data freshness                         | Staleness tracking, auto-refresh, freshness reporting  |
| Watchlist management                   | Ticker list CRUD, watchlist-driven batch operations     |
| Ingestion scheduling                   | Scheduled jobs, batch processing, backfilling          |
| Trading calendar                       | NYSE holidays, trading day awareness                   |
| Data delivery                          | Typed service API for consuming domains                |

### Out of Scope

| Responsibility                         | Owned By                        |
|----------------------------------------|---------------------------------|
| Computing financial ratios             | Quantitative Analysis domain    |
| Technical indicator calculation        | Quantitative Analysis domain    |
| Interpreting or analyzing data         | Research Analysis domain        |
| Portfolio state management             | Portfolio Strategy domain       |
| Risk metric computation                | Risk Management domain          |
| LLM / AI agent operations             | Shared Infrastructure + Agents  |
| Report generation                      | Execution & Reporting domain    |
| Pipeline workflow orchestration        | Orchestration domain            |

### Boundary Rule

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   THE DATA ENGINE ACQUIRES, VALIDATES, AND SERVES DATA.         ║
║   IT DOES NOT INTERPRET, ANALYZE, OR COMPUTE DERIVED METRICS.   ║
║                                                                  ║
║   If a function computes something from raw data (e.g., P/E     ║
║   ratio, moving average, risk score), it belongs in another     ║
║   domain, not here.                                              ║
║                                                                  ║
║   Exception: The Data Engine may compute simple derived fields  ║
║   during normalization (e.g., gross_profit = revenue - COGS)    ║
║   when the source provider does not supply them and the         ║
║   computation is definitional, not analytical.                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 1. DOMAIN CONTEXT

## 1.1 Domain Position in System

```text
                 ┌──────────────────────────────────────┐
                 │         CONSUMING DOMAINS             │
                 │                                       │
                 │  Research   Quant   Portfolio   Risk  │
                 │    ▲         ▲         ▲         ▲   │
                 │    │         │         │         │   │
                 └────┼─────────┼─────────┼─────────┼───┘
                      │         │         │         │
                 ┌────┴─────────┴─────────┴─────────┴───┐
                 │                                       │
                 │          DATA ENGINE                  │
                 │         (This Domain)                 │
                 │                                       │
                 │  ┌───────────────────────────────┐   │
                 │  │       Delivery Layer           │   │
                 │  │    (Public Service API)        │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Storage + Cache Layer        │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Validation Layer             │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Ingestion + Transform Layer  │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Provider Adapter Layer       │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 └───────────────┼───────────────────────┘
                                 │
              ┌──────────────────┼──────────────────────┐
              │                  │                      │
              ▼                  ▼                      ▼
        ┌──────────┐      ┌──────────┐           ┌──────────┐
        │ FMP      │      │ tbc.     │           │ SEC      │
        │ API      │      │          │  . . .    │ EDGAR    │
        └──────────┘      └──────────┘           └──────────┘
```

## 1.2 Domain Consumers

| Consumer Domain        | What It Needs From Data Engine                            | Phase |
|------------------------|-----------------------------------------------------------|-------|
| Research Analysis      | Financial statements, company profiles, news, SEC filings | 2     |
| Quantitative Analysis  | OHLCV price history, volume data, fundamental metrics     | 3     |
| Portfolio Strategy     | Current prices, latest fundamentals, company profiles     | 4     |
| Risk Management        | Price history (for VaR), correlation data, current prices | 4     |
| Execution & Reporting  | Current prices, daily performance data                    | 5     |
| Orchestration          | Watchlist, freshness status, pipeline health              | 1     |

## 1.3 Domain Non-Consumers (Forbidden Dependencies)

No domain outside the Data Engine should:

- Import from `src/data_engine/providers/` (internal adapter layer)
- Import from `src/data_engine/storage/` (internal storage layer)
- Import from `src/data_engine/validation/` (internal validation layer)
- Import from `src/data_engine/ingestion/` (internal ingestion layer)
- Call any external data API directly

All access is through the **public service API** exported via
`src/data_engine/__init__.py`.

---

# 2. DOMAIN ENTITIES

## 2.1 Entity Catalog

```text
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ENGINE ENTITIES                          │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Market Data    │    │   Fundamental    │                  │
│  │                  │    │   Data           │                  │
│  │  • OHLCVBar      │    │                  │                  │
│  │  • Quote         │    │  • IncomeStmt    │                  │
│  │  • IndexBar      │    │  • BalanceSheet  │                  │
│  │                  │    │  • CashFlowStmt  │                  │
│  └──────────────────┘    │  • EarningsReport│                  │
│                          └──────────────────┘                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Reference      │    │   Alternative    │                  │
│  │   Data           │    │   Data           │                  │
│  │                  │    │                  │                  │
│  │  • CompanyProfile│    │  • NewsArticle   │                  │
│  │  • Watchlist     │    │  • SentimentScore│                  │
│  │  • WatchlistItem │    │  • SECFiling     │                  │
│  │  • TradingCalendar│   │  • InsiderTxn    │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Operational    │    │   Provider       │                  │
│  │   Entities       │    │   Entities       │                  │
│  │                  │    │                  │                  │
│  │  • IngestionRun  │    │  • ProviderStatus│                  │
│  │  • IngestionChkpt│    │  • RateLimitState│                  │
│  │  • QualityReport │    │  • HealthCheck   │                  │
│  │  • FreshnessReport│   │                  │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Core Entity Definitions

### OHLCVBar — The Primary Market Data Entity

```text
Entity:         OHLCVBar
Description:    A single trading period's price and volume data for a stock.
                The most fundamental data entity in the system.
Granularity:    One bar per ticker per trading day.
Source:         Market data providers (FMP, etc.)
Storage:        Time-series optimized table (primary key: ticker + date)
Immutability:   Immutable after validated ingestion. Updated only via re-ingestion.
Phase:          1

Attributes:
┌──────────────────┬──────────┬────────────────────────────────────────┐
│ Attribute        │ Type     │ Description                            │
├──────────────────┼──────────┼────────────────────────────────────────┤
│ ticker           │ str      │ Uppercase ticker symbol (e.g., "AAPL") │
│ date             │ date     │ Trading date                           │
│ open_cents       │ int      │ Opening price in USD cents             │
│ high_cents       │ int      │ Highest price in USD cents             │
│ low_cents        │ int      │ Lowest price in USD cents              │
│ close_cents      │ int      │ Closing price in USD cents             │
│ volume           │ int      │ Trading volume in shares               │
│ is_adjusted      │ bool     │ Split/dividend adjusted flag           │
│ source           │ str      │ Provider name                          │
│ fetched_at       │ datetime │ When data was fetched (UTC)            │
│ source_notes     │ str      │ Provider-specific notes                │
│ quality_warnings │ list[str]│ Validation warnings (if any)           │
└──────────────────┴──────────┴────────────────────────────────────────┘

Unique Key:     (ticker, date)
Indexes:        ticker, date, (ticker, date) composite

Validation Rules:
  - high_cents >= low_cents
  - high_cents >= open_cents, close_cents
  - low_cents <= open_cents, close_cents
  - volume >= 0
  - date must be a trading day (not weekend or holiday)
  - All prices > 0

Lifecycle:
  Created → Validated → Stored → Served
  (No update lifecycle — replaced via re-ingestion upsert)
```

### IncomeStatement — Quarterly/Annual Financial Data

```text
Entity:         IncomeStatement
Description:    A company's income statement for a fiscal period.
Granularity:    One record per ticker per fiscal period (quarterly or annual).
Source:         Fundamental data providers (FMP, SEC EDGAR)
Storage:        Relational table (primary key: ticker + period_end_date + period_type)
Immutability:   Updated only via re-ingestion (restated financials).
Phase:          2

Attributes:
┌─────────────────────────────┬──────────┬───────────────────────────────┐
│ Attribute                   │ Type     │ Description                   │
├─────────────────────────────┼──────────┼───────────────────────────────┤
│ ticker                      │ str      │ Uppercase ticker              │
│ period_end_date             │ date     │ End date of fiscal period     │
│ period_type                 │ str      │ "annual" or "quarterly"       │
│ fiscal_year                 │ int      │ Fiscal year number            │
│ fiscal_quarter              │ int|None │ Quarter (1-4) or None         │
│ revenue_cents               │ int      │ Total revenue                 │
│ cost_of_revenue_cents       │ int      │ Cost of goods sold            │
│ gross_profit_cents          │ int      │ Revenue - COGS                │
│ operating_expenses_cents    │ int      │ Total operating expenses      │
│ operating_income_cents      │ int      │ Operating income (EBIT)       │
│ net_income_cents            │ int      │ Net income                    │
│ ebitda_cents                │ int|None │ EBITDA                        │
│ eps_basic_cents             │ int|None │ Basic EPS in cents            │
│ eps_diluted_cents           │ int|None │ Diluted EPS in cents          │
│ shares_outstanding          │ int|None │ Basic shares outstanding      │
│ shares_diluted              │ int|None │ Diluted shares outstanding    │
│ research_development_cents  │ int|None │ R&D expenses                  │
│ selling_general_admin_cents │ int|None │ SG&A expenses                 │
│ interest_expense_cents      │ int|None │ Interest expense              │
│ income_before_tax_cents     │ int      │ Pre-tax income                │
│ income_tax_expense_cents    │ int      │ Tax expense                   │
│ depreciation_amort_cents    │ int|None │ D&A                           │
│ source                      │ str      │ Provider name                 │
│ fetched_at                  │ datetime │ When fetched (UTC)            │
│ filing_date                 │ date|None│ SEC filing date               │
│ quality_warnings            │ list[str]│ Validation warnings           │
└─────────────────────────────┴──────────┴───────────────────────────────┘

Unique Key:     (ticker, period_end_date, period_type)

Validation Rules:
  - gross_profit ≈ revenue - cost_of_revenue (within $1 tolerance)
  - revenue > 0 for our investable universe (FLAG if not)
  - All percentage margins computable from source fields
  - Period type must be "annual" or "quarterly"
```

### BalanceSheet

```text
Entity:         BalanceSheet
Description:    A company's balance sheet as of a fiscal period end.
Granularity:    One record per ticker per fiscal period.
Source:         Fundamental data providers
Phase:          2

Key Attributes:
  - total_assets_cents, total_liabilities_cents, total_shareholders_equity_cents
  - cash_and_equivalents_cents, total_current_assets_cents
  - long_term_debt_cents, total_current_liabilities_cents
  - total_debt_cents, retained_earnings_cents

Unique Key:     (ticker, period_end_date, period_type)

Validation Rules:
  - Assets = Liabilities + Equity (within $1 tolerance)
  - See L4 financial-calculation-standards.md Section 12.1
```

### CashFlowStatement

```text
Entity:         CashFlowStatement
Description:    A company's cash flow statement for a fiscal period.
Granularity:    One record per ticker per fiscal period.
Source:         Fundamental data providers
Phase:          2

Key Attributes:
  - operating_cash_flow_cents
  - capital_expenditures_cents
  - free_cash_flow_cents (operating - capex)
  - investing_cash_flow_cents
  - financing_cash_flow_cents
  - dividends_paid_cents
  - share_buyback_cents
  - net_change_in_cash_cents

Unique Key:     (ticker, period_end_date, period_type)

Validation Rules:
  - free_cash_flow = operating_cash_flow - capital_expenditures
  - OCF + ICF + FCF ≈ net_change_in_cash (within tolerance)
```

### CompanyProfile

```text
Entity:         CompanyProfile
Description:    Static and semi-static company reference data.
Granularity:    One record per ticker (updated periodically).
Source:         Data providers, SEC EDGAR
Phase:          1

Key Attributes:
  - ticker, company_name, description
  - sector (GICS), industry (GICS sub-industry)
  - market_cap_cents, enterprise_value_cents
  - shares_outstanding
  - exchange (NYSE, NASDAQ)
  - ipo_date
  - country, state, city
  - website_url
  - employees_count
  - ceo_name

Unique Key:     (ticker)
Update Frequency: Weekly or on-demand
```

### NewsArticle

```text
Entity:         NewsArticle
Description:    A news article relevant to a stock or the market.
Granularity:    One record per unique article.
Source:         News APIs (NewsAPI, Finnhub, etc.)
Phase:          2

Key Attributes:
  - external_id (provider's unique ID)
  - title, summary, url
  - source_name (publisher)
  - published_at (UTC)
  - tickers_mentioned (list of relevant tickers)
  - sentiment_score (if available from provider)
  - relevance_score (if available)

Unique Key:     (source, external_id)
Upsert Policy:  SKIP on conflict (published news is immutable)
```

### SECFiling

```text
Entity:         SECFiling
Description:    An SEC EDGAR filing for a company.
Granularity:    One record per filing (by accession number).
Source:         SEC EDGAR
Phase:          3

Key Attributes:
  - accession_number (SEC unique ID)
  - ticker, company_name, cik
  - filing_type (10-K, 10-Q, 8-K, Form 4, SC-13D)
  - filing_date, accepted_date
  - period_of_report
  - url (EDGAR URL)
  - parsed_content (structured extraction, if applicable)
  - raw_text_url

Unique Key:     (accession_number)
Upsert Policy:  UPDATE parsed fields (parsing may improve)
```

### Watchlist

```text
Entity:         Watchlist
Description:    A curated set of tickers actively monitored by the system.
Granularity:    One watchlist with multiple items (initially single default list).
Source:         User configuration
Phase:          1

Watchlist Attributes:
  - watchlist_id, name, description
  - created_at, updated_at

WatchlistItem Attributes:
  - watchlist_id, ticker
  - added_at
  - added_reason (e.g., "screener_hit", "manual", "portfolio_holding")
  - notes (free text from fund manager)
  - is_active (soft delete)

Unique Key:     (watchlist_id, ticker)
Max Size:       200 tickers (configurable via MAX_WATCHLIST_SIZE)
```

### IngestionRun

```text
Entity:         IngestionRun
Description:    A record of a batch ingestion execution.
                Used for operational monitoring and audit.
Granularity:    One record per pipeline execution.
Source:         Internal (created by scheduler/job runner)
Phase:          1

Key Attributes:
  - run_id (UUID)
  - pipeline_name (e.g., "daily_ohlcv_refresh")
  - started_at, completed_at
  - status ("running", "completed", "failed", "partial")
  - tickers_total, tickers_succeeded, tickers_failed
  - failed_tickers (list of {ticker, error_code})
  - trigger_type ("scheduled", "manual", "backfill")
  - elapsed_ms

Unique Key:     (run_id)
Retention:      90 days primary, 1 year archive
```

## 2.3 Entity Relationship Map

```text
┌─────────────────┐         ┌─────────────────┐
│   Watchlist      │ 1───M  │  WatchlistItem   │
│                  │─────────│                  │
│ • watchlist_id   │         │ • ticker         │
│ • name           │         │ • added_at       │
└─────────────────┘         └────────┬─────────┘
                                     │
                              ticker │ (logical, not FK)
                                     │
        ┌────────────────────────────┼─────────────────────────────┐
        │                            │                              │
        ▼                            ▼                              ▼
┌───────────────┐          ┌─────────────────┐           ┌─────────────────┐
│  OHLCVBar     │          │ IncomeStatement │           │  CompanyProfile │
│               │          │                 │           │                 │
│ PK: ticker,   │          │ PK: ticker,     │           │ PK: ticker      │
│     date      │          │ period_end_date,│           │                 │
│               │          │ period_type     │           │                 │
│ One per       │          │                 │           │ One per         │
│ trading day   │          │ One per fiscal  │           │ ticker          │
└───────────────┘          │ period          │           └─────────────────┘
                           └─────────────────┘
        │                            │
        │                            │
        │               ┌────────────┴──────────┐
        │               │                       │
        │               ▼                       ▼
        │     ┌─────────────────┐    ┌──────────────────┐
        │     │  BalanceSheet   │    │ CashFlowStatement│
        │     │                 │    │                  │
        │     │ PK: ticker,     │    │ PK: ticker,      │
        │     │ period_end_date,│    │ period_end_date, │
        │     │ period_type     │    │ period_type      │
        │     └─────────────────┘    └──────────────────┘
        │
        │              ┌─────────────────────────────────┐
        │              │                                  │
        ▼              ▼                                  ▼
┌───────────────┐ ┌───────────────┐            ┌─────────────────┐
│  NewsArticle  │ │  SECFiling    │            │  EarningsReport │
│               │ │               │            │                 │
│ PK: source,   │ │ PK: accession_│            │ PK: ticker,     │
│ external_id   │ │ number        │            │ report_date     │
│               │ │               │            │                 │
│ M:N tickers   │ │ One per filing│            │ One per         │
│ via mentions  │ │               │            │ earnings date   │
└───────────────┘ └───────────────┘            └─────────────────┘
```

---

# 3. DOMAIN EVENTS

## 3.1 Events Emitted by Data Engine

| Event Name                         | Trigger                                      | Payload                                          | Consumers                    |
|------------------------------------|----------------------------------------------|--------------------------------------------------|------------------------------|
| `data.ingestion.completed`         | Batch ingestion job finishes                 | {pipeline, tickers_count, succeeded, failed}     | Orchestration, Reporting     |
| `data.ingestion.ticker_completed`  | Single ticker ingestion succeeds             | {ticker, data_type, bar_count, source}           | Orchestration                |
| `data.ingestion.ticker_failed`     | Single ticker ingestion fails                | {ticker, data_type, error_code, provider}        | Orchestration, Reporting     |
| `data.validation.anomaly_detected` | Quality check flags unusual data             | {ticker, date, rule_id, severity, details}       | Reporting, Risk              |
| `data.freshness.stale_detected`    | Data exceeds staleness threshold             | {ticker, data_type, staleness_hours}             | Orchestration, Reporting     |
| `data.provider.health_changed`     | Provider becomes healthy or unhealthy        | {provider, is_healthy, last_check_at}            | Reporting                    |
| `data.provider.failover_triggered` | Primary failed, fallback used                | {primary, fallback, data_type, ticker}           | Reporting                    |
| `data.provider.rate_limit_warning` | Provider usage exceeds 80% of daily limit    | {provider, used, limit, pct}                     | Reporting                    |
| `data.watchlist.ticker_added`      | New ticker added to watchlist                | {ticker, watchlist, reason}                      | Orchestration (trigger backfill) |
| `data.watchlist.ticker_removed`    | Ticker removed from watchlist                | {ticker, watchlist}                              | Orchestration                |
| `data.backfill.completed`         | Historical backfill job finishes             | {ticker, data_type, start_date, end_date, count} | Orchestration                |

## 3.2 Events Consumed by Data Engine

| Event Name                         | Source Domain     | Data Engine Action                              |
|------------------------------------|-------------------|-------------------------------------------------|
| `orchestration.pipeline.trigger`   | Orchestration     | Start a scheduled or ad-hoc ingestion pipeline  |
| `portfolio.holdings.changed`       | Portfolio Strategy| Add/prioritize portfolio tickers for refresh    |

## 3.3 Event Rules

| Rule | Description |
|------|-------------|
| **EV-001** | All events include a `correlation_id` for tracing across pipeline stages |
| **EV-002** | Events use past tense verbs (`.completed`, `.detected`, `.triggered`) |
| **EV-003** | Events are informational — they do not carry commands |
| **EV-004** | Events include enough context to be useful without querying additional data |
| **EV-005** | Events are idempotent — receiving the same event twice is harmless |
| **EV-006** | Critical events (anomaly, failure, rate limit) include severity level |

---

# 4. DOMAIN DEPENDENCIES

## 4.1 Dependency Map

```text
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│  DATA ENGINE DEPENDENCIES                                    │
│                                                               │
│  DEPENDS ON (Infrastructure):                                │
│  ├── Database (PostgreSQL) — data persistence                │
│  ├── Cache (Redis or in-memory) — read performance           │
│  ├── HTTP Client — external API calls                        │
│  ├── Scheduler — triggering ingestion jobs                   │
│  ├── Event Bus — publishing domain events                    │
│  ├── Logger — structured logging                             │
│  └── Config — provider keys, rate limits, thresholds         │
│                                                               │
│  DEPENDS ON (External):                                      │
│  ├── Market Data APIs (FMP)                │
│  ├── Fundamental Data APIs (FMP)                    │
│  ├── News APIs (Phase 2)                                     │
│  ├── SEC EDGAR (Phase 3)                                     │
│  └── NYSE Trading Calendar                                   │
│                                                               │
│  DEPENDED ON BY (Domains):                                   │
│  ├── Research Analysis — all data types                      │
│  ├── Quantitative Analysis — price and fundamental data      │
│  ├── Portfolio Strategy — current prices and fundamentals    │
│  ├── Risk Management — price history and current prices      │
│  ├── Execution & Reporting — current prices and performance  │
│  └── Orchestration — watchlist, freshness, pipeline status   │
│                                                               │
│  DOES NOT DEPEND ON:                                         │
│  ✗ Research Analysis                                         │
│  ✗ Quantitative Analysis                                     │
│  ✗ Portfolio Strategy                                        │
│  ✗ Risk Management                                           │
│  ✗ LLM Gateway (Data Engine does not use AI)                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## 4.2 Dependency Rules

| Rule | Description |
|------|-------------|
| **DP-001** | Data Engine has ZERO dependencies on other business domains |
| **DP-002** | Data Engine depends ONLY on shared infrastructure (DB, cache, HTTP, events) |
| **DP-003** | Data Engine does NOT use the LLM Gateway — it is purely data infrastructure |
| **DP-004** | All external API dependencies are behind adapter interfaces for swapability |
| **DP-005** | Data Engine must remain functional if any single external provider fails (INV-033) |
| **DP-006** | Data Engine must remain functional if the cache is completely empty |

---

# 5. MODULE DECOMPOSITION

## 5.1 Module Map

```text
src/data_engine/
│
├── __init__.py                          # Public API exports
│
├── services/                            # Consumer-facing services
│   ├── __init__.py
│   ├── market_data.py                   # MarketDataService
│   ├── fundamental_data.py             # FundamentalDataService
│   ├── news_data.py                     # NewsDataService (Phase 2)
│   ├── filing_data.py                   # FilingDataService (Phase 3)
│   ├── company_data.py                  # CompanyDataService
│   └── watchlist.py                     # WatchlistService
│
├── ingestion/                           # Data acquisition orchestration
│   ├── __init__.py
│   ├── service.py                       # IngestionService
│   ├── backfill.py                      # BackfillService
│   ├── job_runner.py                    # IngestionJobRunner
│   └── checkpoint.py                    # IngestionCheckpoint
│
├── providers/                           # External provider adapters
│   ├── __init__.py
│   ├── base.py                          # BaseProviderAdapter
│   ├── interfaces.py                    # Provider protocol definitions
│   ├── registry.py                      # Provider registry
│   ├── failover.py                      # ProviderFailoverManager
│   ├── fmp/                             # FMP adapters
│   │   ├── __init__.py
│   │   ├── daily_bars.py
│   │   ├── income_statement.py
│   │   ├── balance_sheet.py
│   │   └── cash_flow.py
│   ├── newsapi/                         # News API adapter (Phase 2)
│   │   └── ...
│   └── sec_edgar/                       # SEC EDGAR adapter (Phase 3)
│       └── ...
│
├── validation/                          # Data quality validation
│   ├── __init__.py
│   ├── validator.py                     # ValidationPipeline
│   ├── quality_rules.py                 # Quality rule implementations
│   └── anomaly_detection.py             # Statistical anomaly detection
│
├── storage/                             # Persistence layer
│   ├── __init__.py
│   ├── interfaces.py                    # Repository protocols
│   ├── market_data_repo.py             # MarketDataRepository
│   ├── fundamental_data_repo.py        # FundamentalDataRepository
│   ├── news_repo.py                     # NewsRepository (Phase 2)
│   ├── filing_repo.py                   # FilingRepository (Phase 3)
│   ├── company_repo.py                  # CompanyRepository
│   ├── watchlist_repo.py               # WatchlistRepository
│   ├── ingestion_run_repo.py           # IngestionRunRepository
│   └── cached/                          # Cache-aside wrappers
│       ├── __init__.py
│       ├── cached_market_data.py
│       └── cached_company_data.py
│
├── freshness/                           # Data freshness tracking
│   ├── __init__.py
│   └── tracker.py                       # FreshnessTracker
│
├── calendar/                            # Trading calendar
│   ├── __init__.py
│   └── trading_calendar.py             # TradingCalendar
│
├── scheduling/                          # Ingestion scheduling
│   ├── __init__.py
│   └── config.py                        # IngestionSchedule configs
│
├── models/                              # Canonical data models
│   ├── __init__.py
│   ├── market_data.py                   # OHLCVBar, Quote, IndexBar
│   ├── fundamental_data.py             # IncomeStatement, BalanceSheet, etc.
│   ├── news.py                          # NewsArticle, SentimentScore
│   ├── filings.py                       # SECFiling, InsiderTransaction
│   ├── reference.py                     # CompanyProfile, WatchlistItem
│   └── operational.py                   # IngestionRun, QualityReport
│
├── errors.py                            # Domain error classes
│
└── constants.py                         # Domain constants
```

## 5.2 Module Specifications Required

Each module above requires a detailed L2 specification. The following
L2 specs should be written in this order (aligned with Phase 1 priority):

```text
PHASE 1 — L2 MODULE SPECS (Write First):
─────────────────────────────────────────
1. L2-modules/data-engine/market-data-ingestion.md
   → IngestionService, provider adapters, failover, rate limiting
   → The core data acquisition pipeline

2. L2-modules/data-engine/data-storage.md
   → MarketDataRepository, upsert logic, query patterns
   → The persistence layer

3. L2-modules/data-engine/data-validation.md
   → ValidationPipeline, quality rules, anomaly detection
   → The quality gate

4. L2-modules/data-engine/watchlist-management.md
   → WatchlistService, CRUD operations, backfill triggers
   → User-facing ticker management

5. L2-modules/data-engine/market-data-delivery.md
   → MarketDataService (consumer-facing), caching, freshness
   → The public API for price data

6. L2-modules/data-engine/company-data.md
   → CompanyDataService, CompanyProfile management
   → Reference data

7. L2-modules/data-engine/ingestion-scheduling.md
   → IngestionJobRunner, scheduling config, batch execution
   → Automated pipeline execution

PHASE 2 — L2 MODULE SPECS:
──────────────────────────
8.  L2-modules/data-engine/fundamental-data.md
9.  L2-modules/data-engine/news-sentiment-feed.md
10. L2-modules/data-engine/earnings-data.md

PHASE 3 — L2 MODULE SPECS:
──────────────────────────
11. L2-modules/data-engine/sec-filings-parser.md
12. L2-modules/data-engine/insider-transactions.md
```

---

# 6. BUSINESS RULES

## 6.1 Data Acquisition Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-001   | All external data is fetched through provider adapters, never directly.      |
| DE-002   | Every provider interaction respects the configured rate limit with safety buffer. |
| DE-003   | If the primary provider fails, the system automatically tries the fallback provider before returning an error. |
| DE-004   | Provider-specific data formats are translated to canonical models at the adapter boundary. All downstream code operates on canonical models only. |
| DE-005   | Dollar values from providers are converted to integer cents using `dollars_to_cents()` at the adapter boundary. |
| DE-006   | All timestamps from providers are converted to UTC at the adapter boundary. |
| DE-007   | All ticker symbols are normalized to uppercase at the adapter boundary.     |
| DE-008   | API keys and credentials are never logged, cached, or included in events.   |

## 6.2 Data Quality Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-010   | Every data point passes through the validation pipeline before storage.      |
| DE-011   | OHLCV bars must satisfy: high >= low, high >= open, high >= close, low <= open, low <= close. |
| DE-012   | OHLCV bars with non-trading-day dates (weekends, holidays) are REJECTED.    |
| DE-013   | OHLCV bars with zero volume on a trading day are FLAGGED (stored with warning). |
| DE-014   | Daily price moves exceeding 50% from prior close are FLAGGED (not rejected — could be real). |
| DE-015   | Balance sheets must satisfy: Assets = Liabilities + Equity (within $1 tolerance). |
| DE-016   | Income statements must satisfy: Gross Profit ≈ Revenue - COGS (within $1 tolerance). |
| DE-017   | Cash flow statements must satisfy: OCF + ICF + FCF ≈ Net Change in Cash (within $1 tolerance). |
| DE-018   | Missing data is stored as `None`, never as zero or empty string.            |
| DE-019   | Validation never modifies data — it classifies as ACCEPT, FLAG, or REJECT. |

## 6.3 Data Storage Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-020   | All write operations use UPSERT semantics (insert or update on conflict).   |
| DE-021   | Unique keys are enforced at the database level, not just application level. |
| DE-022   | Historical data is immutable after validated ingestion (INV-005). Updates occur only via re-ingestion upsert. |
| DE-023   | Retrieval queries always return data in ascending chronological order.       |
| DE-024   | Empty results are returned as empty lists, never `None`.                     |
| DE-025   | Repositories return canonical domain models, never raw database rows.       |

## 6.4 Data Freshness Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-030   | Every data point has a `fetched_at` timestamp recording when it was obtained.|
| DE-031   | Data freshness is checked before data is served to consuming domains.       |
| DE-032   | If data is stale and auto-refresh is enabled, a re-fetch is triggered transparently before the response. |
| DE-033   | Stale data is usable but must be flagged — it reduces agent confidence scores downstream. |
| DE-034   | Freshness thresholds: price = 15 min, daily OHLCV = 18 hours, fundamentals = 100 days, news = 24 hours, filings = 48 hours. |
| DE-035   | Freshness checks account for weekends and holidays — Friday data is not stale on Saturday. |

## 6.5 Watchlist Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-040   | Maximum watchlist size: 200 tickers (configurable via MAX_WATCHLIST_SIZE).  |
| DE-041   | Adding a ticker to the watchlist triggers a historical backfill job.        |
| DE-042   | Removing a ticker from the watchlist is a soft delete (data retained).      |
| DE-043   | Portfolio holdings are automatically included in the watchlist for monitoring. |
| DE-044   | Watchlist changes emit domain events for orchestration.                     |

## 6.6 Operational Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-050   | Every batch ingestion run is recorded as an IngestionRun for monitoring.    |
| DE-051   | Individual ticker failures within a batch do not stop the batch. The batch continues and reports aggregate results. |
| DE-052   | Ingestion pipelines are idempotent: re-running with the same parameters produces the same state. |
| DE-053   | Long-running pipelines use checkpointing for resume-after-failure.          |
| DE-054   | Market data ingestion is skipped on non-trading days (weekends, NYSE holidays). |
| DE-055   | Concurrent ticker processing is bounded to respect provider rate limits.    |
| DE-056   | Provider health is checked at system startup and every 15 minutes during operation. |

---

# 7. PUBLIC API SURFACE

## 7.1 Service API Catalog

These are the services exported by `src/data_engine/__init__.py` and
available to consuming domains:

### MarketDataService

```text
Service:    MarketDataService
Purpose:    Provides daily OHLCV price data and current prices.
Phase:      1

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_daily_bars(               │ Result[              │ Get OHLCV bars  │
│   ticker, start_date,         │   list[OHLCVBar],    │ for a ticker    │
│   end_date, auto_refresh)     │   DataError]         │ in date range   │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_latest_price_cents(       │ Result[int,          │ Most recent     │
│   ticker)                     │   DataError]         │ closing price   │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_latest_bar(               │ OHLCVBar | None      │ Most recent bar │
│   ticker)                     │                      │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_multiple_tickers_bars(    │ dict[str,            │ Batch retrieval │
│   tickers, start_date,        │   list[OHLCVBar]]    │ for watchlist   │
│   end_date)                   │                      │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_price_on_date(            │ Result[int,          │ Price on a      │
│   ticker, target_date)        │   DataError]         │ specific date   │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_freshness(                │ FreshnessStatus      │ Data freshness  │
│   ticker)                     │                      │ for a ticker    │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### FundamentalDataService

```text
Service:    FundamentalDataService
Purpose:    Provides financial statement data.
Phase:      2

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_income_statements(        │ Result[              │ Income stmts    │
│   ticker, period_type,        │   list[IncomeStmt],  │ annual or qtr   │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_balance_sheets(           │ Result[              │ Balance sheets  │
│   ticker, period_type,        │   list[BalanceSheet],│                 │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_cash_flow_statements(     │ Result[              │ Cash flow stmts │
│   ticker, period_type,        │   list[CashFlowStmt],│                │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_all_financials(           │ Result[              │ All three       │
│   ticker, period_type,        │   FinancialBundle,   │ statements      │
│   limit)                      │   DataError]         │ bundled         │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_latest_earnings(          │ Result[              │ Most recent     │
│   ticker)                     │   EarningsReport,    │ earnings data   │
│                               │   DataError]         │                 │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### CompanyDataService

```text
Service:    CompanyDataService
Purpose:    Provides company reference data.
Phase:      1

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_profile(ticker)           │ Result[              │ Company profile │
│                               │   CompanyProfile,    │                 │
│                               │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_profiles(tickers)         │ dict[str,            │ Batch profiles  │
│                               │   CompanyProfile|None]│                │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_sector(ticker)            │ str | None           │ GICS sector     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_market_cap_cents(ticker)  │ int | None           │ Latest mkt cap  │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### NewsDataService

```text
Service:    NewsDataService
Purpose:    Provides news articles and sentiment data.
Phase:      2

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_news(                     │ Result[              │ Recent news for │
│   ticker, from_date,          │   list[NewsArticle], │ a ticker        │
│   to_date, limit)             │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_market_news(              │ Result[              │ General market  │
│   from_date, to_date,         │   list[NewsArticle], │ news            │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_sentiment(ticker)         │ SentimentSummary     │ Aggregated      │
│                               │   | None             │ sentiment       │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### WatchlistService

```text
Service:    WatchlistService
Purpose:    Manages the active watchlist of monitored tickers.
Phase:      1

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_watchlist()               │ list[WatchlistItem]  │ All active items│
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_tickers()                 │ list[str]            │ Just the tickers│
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ add_ticker(                   │ Result[              │ Add a ticker    │
│   ticker, reason, notes)      │   WatchlistItem,     │ to watchlist    │
│                               │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ remove_ticker(ticker)         │ Result[None,         │ Soft-delete     │
│                               │   DataError]         │ from watchlist  │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ is_on_watchlist(ticker)       │ bool                 │ Membership check│
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_watchlist_freshness()     │ dict[str,            │ Freshness for   │
│                               │   FreshnessStatus]   │ all tickers     │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

## 7.2 Public API Rules

| Rule | Description |
|------|-------------|
| **API-001** | Only services listed in `src/data_engine/__init__.py` are accessible to other domains |
| **API-002** | Every public method returns typed results (Result, canonical models, or None) |
| **API-003** | No public method exposes internal implementation details (providers, cache, storage) |
| **API-004** | Public methods handle caching transparently — consumers never manage cache |
| **API-005** | Public methods handle freshness checks transparently — consumers optionally opt out via `auto_refresh=False` |
| **API-006** | Public methods are documented with full parameter descriptions and return types |
| **API-007** | Batch methods (multiple tickers) return dicts with empty values for missing data, never raise for individual failures |

---

# 8. DATA FLOW DIAGRAMS

## 8.1 Daily OHLCV Ingestion Flow (Phase 1 Core Flow)

```text
     ┌──────────────┐
     │  Scheduler   │ 6:00 PM ET (after market close)
     │  triggers    │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ JobRunner    │ Load tickers from WatchlistService
     │              │ Bounded concurrency (max 10)
     └──────┬───────┘
            │ for each ticker:
            ▼
     ┌──────────────┐
     │ Ingestion    │ Determine date range to fetch
     │ Service      │ (last stored date → today)
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐     fail     ┌──────────────┐
     │ Primary      │────────────→│ Fallback     │
     │ Provider     │             │ Provider     │
     │ (FMP)    │             │ (AlphaVant.) │
     └──────┬───────┘             └──────┬───────┘
            │ success                     │ success
            └──────────┬──────────────────┘
                       │
                       ▼
              ┌──────────────┐
              │ Canonical    │ dollars_to_cents()
              │ Transform    │ UTC timestamps
              │              │ Uppercase tickers
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Validation   │ Schema checks
              │ Pipeline     │ Quality rules
              │              │ Anomaly detection
              └──────┬───────┘
                     │
            ┌────────┼────────┐
            ▼        ▼        ▼
         ACCEPT    FLAG    REJECT
            │        │        │
            │        │        └──→ Log + Skip
            │        │
            ▼        ▼
     ┌──────────────────┐
     │ Repository       │ UPSERT into database
     │ (store_bars)     │ Invalidate cache
     └──────┬───────────┘
            │
            ▼
     ┌──────────────────┐
     │ Event Bus        │ Publish data.ingestion.ticker_completed
     └──────────────────┘
```

## 8.2 Consumer Data Retrieval Flow

```text
     ┌──────────────┐
     │  Consumer    │ e.g., Research Agent asks for AAPL prices
     │  (Research)  │
     └──────┬───────┘
            │ get_daily_bars("AAPL", start, end)
            ▼
     ┌──────────────┐
     │ MarketData   │
     │ Service      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐     hit     ┌──────────────┐
     │ Cache        │────────────→│ Return       │
     │ Lookup       │             │ cached data  │
     └──────┬───────┘             └──────────────┘
            │ miss
            ▼
     ┌──────────────┐
     │ Database     │ Query repository
     │ Query        │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Freshness    │ Is data current enough?
     │ Check        │
     └──────┬───────┘
            │
       ┌────┴────┐
       ▼         ▼
     FRESH     STALE
       │         │
       │         ▼
       │    ┌──────────────┐
       │    │ Auto-refresh │ Trigger ingestion
       │    │ from provider│ for stale range
       │    └──────┬───────┘
       │           │
       │           ▼
       │    ┌──────────────┐
       │    │ Re-query DB  │ Get updated data
       │    └──────┬───────┘
       │           │
       └─────┬─────┘
             │
             ▼
     ┌──────────────┐
     │ Populate     │ Cache results with TTL
     │ Cache        │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Return       │ list[OHLCVBar]
     │ to Consumer  │
     └──────────────┘
```

## 8.3 Watchlist Addition Flow

```text
     ┌──────────────┐
     │ Fund Manager │ Adds NVDA to watchlist
     └──────┬───────┘
            │ add_ticker("NVDA", reason="screener_hit")
            ▼
     ┌──────────────┐
     │ Watchlist    │ Validate ticker (exists, not penny stock)
     │ Service      │ Check watchlist size < MAX
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Store        │ Upsert WatchlistItem
     │ to DB        │
     └──────┬───────┘
            │
            ├───────────────────────────────────┐
            │                                   │
            ▼                                   ▼
     ┌──────────────┐                   ┌──────────────┐
     │ Emit Event   │                   │ Trigger      │
     │ watchlist.   │                   │ Backfill     │
     │ ticker_added │                   │ Job          │
     └──────────────┘                   └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ Fetch 1-5yr  │
                                        │ history from │
                                        │ providers    │
                                        └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ Validate +   │
                                        │ Store        │
                                        └──────────────┘
```

---

# 9. CONFIGURATION

## 9.1 Data Engine Configuration

```yaml
# config/data_engine.yaml (merged with default.yaml)

data_engine:
  # ── Provider Configuration ──
  providers:
    market_data:
      primary: "fmp"
    fundamental_data:
      primary: "fmp"
      fallback: null              # No fallback yet
    news:
      primary: "newsapi"
      fallback: "finnhub"
    filings:
      primary: "sec_edgar"
      fallback: null

  # ── Rate Limiting ──
  rate_limits:
    fmp:
      requests_per_minute: 5
      requests_per_day: null
      buffer_pct: 20

  # ── Freshness Thresholds ──
  freshness:
    price_hours: 0.25
    daily_ohlcv_hours: 18
    fundamentals_days: 100
    news_hours: 24
    filings_hours: 48

  # ── Cache TTLs ──
  cache:
    daily_bars_ttl_seconds: 300
    latest_quote_ttl_seconds: 60
    price_history_ttl_seconds: 3600
    income_statement_ttl_seconds: 86400
    company_profile_ttl_seconds: 86400

  # ── Validation Thresholds ──
  validation:
    max_daily_price_change_pct: 0.50
    min_reasonable_price_cents: 1
    max_reasonable_price_cents: 10000000
    volume_spike_multiplier: 50

  # ── Watchlist ──
  watchlist:
    max_size: 200
    default_backfill_years: 3

  # ── Ingestion ──
  ingestion:
    max_concurrent_tickers: 10
    per_ticker_timeout_seconds: 30
    batch_timeout_seconds: 600
    retry_max: 2
    backoff_base_seconds: 2

  # ── Health Checks ──
  health:
    check_interval_minutes: 15
    recovery_check_interval_minutes: 15

  # ── Retention ──
  retention:
    ohlcv_primary_days: 3650
    fundamentals_primary_days: 3650
    news_primary_days: 365
    pipeline_logs_primary_days: 90
```

## 9.2 Configuration Rules

| Rule | Description |
|------|-------------|
| **CF-001** | All Data Engine configuration in `config/data_engine.yaml` or environment variables |
| **CF-002** | API keys ONLY from environment variables, never config files |
| **CF-003** | Every threshold has a sensible default that works for Phase 1 |
| **CF-004** | Configuration loaded at startup and injected via DI |
| **CF-005** | Configuration changes do not require code changes |

---

# 10. PHASE MAPPING

## 10.1 Phase 1 — Foundation (Month 1-2)

```text
BUILD IN PHASE 1:
─────────────────
✓ Provider adapter layer (FMP for daily bars)
✓ Rate limiting infrastructure
✓ Provider failover manager
✓ Canonical data models (OHLCVBar, CompanyProfile)
✓ Data validation pipeline (OHLCV quality rules)
✓ Market data repository (PostgreSQL, upsert)
✓ Cache layer (cache-aside pattern)
✓ Freshness tracker
✓ MarketDataService (consumer-facing)
✓ CompanyDataService (basic profile)
✓ WatchlistService (CRUD, backfill trigger)
✓ Ingestion job runner (batch processing)
✓ Ingestion scheduling (daily after-close job)
✓ Trading calendar (NYSE holidays 2025)
✓ Backfill service (historical data loading)
✓ IngestionRun tracking
✓ Domain event publishing

PHASE 1 EXIT CRITERIA:
──────────────────────
□ Ingest daily OHLCV for 200+ tickers reliably (>99% success rate)
□ Provider failover tested (primary down → fallback succeeds)
□ Validation catches and rejects weekend bars
□ Validation flags extreme moves (>50%) with warning
□ Upsert verified: re-ingestion updates without duplicates
□ Cache hit rate measured and documented
□ Freshness tracker correctly identifies stale data
□ Backfill loads 3 years of history for a new ticker
□ Daily scheduled job runs unattended at 6 PM ET
□ All Phase 1 L2 module specs written and validated
□ Test coverage: repositories >75%, services >85%, validators >95%
```

## 10.2 Phase 2 — Research Data (Month 3-4)

```text
ADD IN PHASE 2:
───────────────
• Fundamental data models (IncomeStatement, BalanceSheet, CashFlowStatement)
• Fundamental data provider adapters (FMP financials)
• Fundamental data repository + validation
• FundamentalDataService (consumer-facing)
• Earnings data model and ingestion
• News article model and ingestion
• News API adapter
• NewsDataService (consumer-facing)
• Sentiment scoring (if provider supports it)
• Company profile enrichment (sector, industry, description)
• Financial statement cross-validation (A = L + E)
```

## 10.3 Phase 3 — SEC Data (Month 5-7)

```text
ADD IN PHASE 3:
───────────────
• SEC EDGAR adapter (filing retrieval)
• SEC filing parser (structured data extraction from 10-K, 10-Q, 8-K)
• Insider transaction parsing (Form 4)
• SECFiling model and repository
• InsiderTransaction model and repository
• FilingDataService (consumer-facing)
• Enhanced company profile from EDGAR (CIK mapping, SIC codes)
```

## 10.4 Phase 4+ — Enhancements

```text
FUTURE ENHANCEMENTS:
────────────────────
• Intraday data support (requires different storage pattern)
• Real-time quote streaming (WebSocket provider adapter)
• Alternative data integrations (social sentiment, web traffic)
• Index constituent tracking (S&P 500 membership changes)
• Dividend and split event tracking (corporate actions)
• Provider cost optimization (route to cheapest provider with sufficient data)
• Data lineage tracking (full audit trail of transformations)
```

---

# 11. ERROR CATALOG

## 11.1 Data Engine Error Hierarchy

```text
DomainError (from shared/errors)
└── DataError (base for all Data Engine errors)
    ├── DataFetchError
    │   ├── ProviderTimeoutError
    │   ├── ProviderRateLimitError
    │   └── ProviderConnectionError
    ├── DataValidationError
    │   ├── SchemaValidationError
    │   └── QualityRuleViolation
    ├── DataStorageError
    │   ├── WriteFailedError
    │   └── ConnectionLostError
    ├── DataNotFoundError
    │   ├── TickerNotFoundError
    │   └── DateRangeEmptyError
    ├── WatchlistError
    │   ├── WatchlistFullError
    │   └── TickerAlreadyExistsError
    └── DataFreshnessError
        └── StaleDataError
```

## 11.2 Error Code Catalog

| Error Code                               | Severity | Description                                        | Consumer Action                 |
|------------------------------------------|----------|----------------------------------------------------|---------------------------------|
| `DATA.PROVIDER.*.TIMEOUT`                | WARNING  | Provider API call timed out                        | Retry or use fallback           |
| `DATA.PROVIDER.*.RATE_LIMITED`           | WARNING  | Provider rate limit hit                            | Wait and retry                  |
| `DATA.PROVIDER.*.CONNECTION_ERROR`       | ERROR    | Cannot reach provider                              | Use fallback                    |
| `DATA.PROVIDER.*.CLIENT_ERROR`           | ERROR    | Provider returned 4xx (bad request)                | Check parameters, do not retry  |
| `DATA.PROVIDER.*.SERVER_ERROR`           | WARNING  | Provider returned 5xx                              | Retry with backoff              |
| `DATA.FAILOVER.ALL_FAILED`              | ERROR    | All providers failed for a request                 | Alert fund manager              |
| `DATA.FAILOVER.NO_PROVIDERS`            | ERROR    | No providers configured for data category          | Configuration error             |
| `DATA.VALIDATION.SCHEMA_INVALID`         | ERROR    | Data failed Pydantic schema validation             | Reject data, log details        |
| `DATA.VALIDATION.QUALITY_REJECT`         | WARNING  | Data failed a REJECT-severity quality rule         | Skip data point, log            |
| `DATA.VALIDATION.ANOMALY_DETECTED`       | INFO     | Data flagged by anomaly detection                  | Store with warning, log         |
| `DATA.STORAGE.WRITE_FAILED`             | ERROR    | Database write operation failed                    | Retry, then alert               |
| `DATA.STORAGE.CONNECTION_LOST`           | CRITICAL | Database connection lost                           | Immediate alert, retry connect  |
| `DATA.MARKET.NO_DATA`                    | WARNING  | No data found for ticker/date range                | Return empty to consumer        |
| `DATA.MARKET.TICKER_NOT_FOUND`           | WARNING  | Ticker not recognized by any provider              | Return error to consumer        |
| `DATA.WATCHLIST.FULL`                    | WARNING  | Watchlist at max capacity                          | Inform user, suggest removal    |
| `DATA.WATCHLIST.TICKER_EXISTS`           | INFO     | Ticker already on watchlist                        | No action needed (idempotent)   |
| `DATA.FRESHNESS.STALE`                   | WARNING  | Data exceeds staleness threshold                   | Trigger refresh, flag to agent  |
| `DATA.RATE_LIMIT.DAILY_EXCEEDED`         | ERROR    | Daily API call budget exhausted for a provider     | Use fallback or wait until reset|

---

# 12. QUALITY ATTRIBUTES

## 12.1 Performance Targets

| Operation                           | Target Latency | Notes                          |
|-------------------------------------|----------------|--------------------------------|
| Get daily bars (cache hit)          | < 50ms         | From in-memory cache           |
| Get daily bars (cache miss)         | < 200ms        | From PostgreSQL                 |
| Get daily bars (stale, auto-refresh)| < 5s           | Includes provider fetch        |
| Batch ingestion (200 tickers)       | < 10 minutes   | Bounded by rate limits         |
| Single ticker ingestion             | < 5s           | Provider fetch + validate + store |
| Watchlist operations                | < 100ms        | CRUD operations                |
| Freshness check (single ticker)     | < 10ms         | Metadata lookup                |
| Freshness check (full watchlist)    | < 500ms        | Batch metadata query           |

## 12.2 Reliability Targets

| Metric                              | Target         | Measurement                    |
|-------------------------------------|----------------|--------------------------------|
| Daily ingestion completion rate     | > 99%          | Tickers succeeded / total      |
| Provider failover success rate      | > 95%          | Fallback succeeds when primary fails |
| Data validation pass rate           | > 99.5%        | Bars accepted / total fetched  |
| Zero data corruption incidents      | 0 per quarter  | Manual audit of stored data    |
| System functional on cache clear    | 100%           | Functional test with empty cache |

## 12.3 Data Quality Targets

| Metric                              | Target         | Measurement                    |
|-------------------------------------|----------------|--------------------------------|
| Price accuracy vs source            | 100%           | Spot-check stored vs provider  |
| Cents conversion accuracy           | 100%           | Round-trip conversion tests    |
| Missing data rate                   | < 0.5%         | Null fields / total fields     |
| Duplicate data rate                 | 0%             | Upsert verification            |
| Staleness detection accuracy        | 100%           | Freshness tracker tests        |

---

# 13. SECURITY CONSIDERATIONS

| Concern                        | Mitigation                                        |
|--------------------------------|---------------------------------------------------|
| API key exposure               | Keys from env vars only. Sanitized from all logs. |
| SQL injection                  | Parameterized queries via repository layer.        |
| Data tampering                 | Append-only ingestion audit trail.                 |
| Provider impersonation         | HTTPS only. Certificate validation enabled.        |
| Rate limit abuse               | Rate limiter enforced on every external call.      |
| Cache poisoning                | Cache populated only from validated DB data.       |
| Credential in prompt/agent     | Data Engine has no LLM integration. No risk.       |

---

# 14. OPEN QUESTIONS AND FUTURE DECISIONS

These are decisions that do not need to be resolved for Phase 1 but
should be tracked for future phases:

| ID    | Question                                                          | Relevant Phase | Status   |
|-------|-------------------------------------------------------------------|----------------|----------|
| OQ-01 | Should we use TimescaleDB for OHLCV instead of plain PostgreSQL?  | 1              | DECIDE   |
| OQ-02 | Redis vs in-memory cache for Phase 1?                             | 1              | DECIDE   |
| OQ-03 | How to handle corporate actions (splits, dividends) retroactively?| 2              | DEFERRED |
| OQ-04 | Should fundamental data be stored in a document DB or relational? | 2              | DEFERRED |
| OQ-05 | How to handle delisted tickers in historical data?                | 3              | DEFERRED |
| OQ-06 | Real-time streaming architecture for intraday data?               | 6+             | DEFERRED |
| OQ-07 | Multi-provider cost optimization routing?                         | 4+             | DEFERRED |
| OQ-08 | Data lineage / full audit trail of transformations?               | 5              | DEFERRED |
| OQ-09 | Should the Data Engine expose a GraphQL API for flexible queries? | 5+             | DEFERRED |
| OQ-10 | Handling of different fiscal year ends across companies?          | 2              | DEFERRED |

---

# 15. CROSS-REFERENCES

| Document                                    | Location                                              |
|---------------------------------------------|-------------------------------------------------------|
| L0: System Vision                           | `specs/L0-system-vision.md`                           |
| L0: Data Architecture Principles            | `specs/L0-system-vision.md` Section 6                 |
| L0: Data Freshness Requirements             | `specs/L0-system-vision.md` Section 8 (authoritative) |
| L0: Data Quality Rules                      | `specs/L0-system-vision.md` Section 6.4               |
| L0: ID families & traceability              | `specs/L0-system-vision.md` Section 16               |
| L4: Coding Standards                        | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards         | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                       | `specs/L4-conventions/testing-standards.md`            |
| L4: Data Pipeline Standards                 | `specs/L4-conventions/data-pipeline-standards.md`     |
| L2: Market Data Ingestion (to be written)   | `specs/L2-modules/data-engine/market-data-ingestion.md` |
| L2: Data Storage (to be written)            | `specs/L2-modules/data-engine/data-storage.md`        |
| L2: Data Validation (to be written)         | `specs/L2-modules/data-engine/data-validation.md`     |
| L2: Watchlist Management (to be written)    | `specs/L2-modules/data-engine/watchlist-management.md` |
| L2: Market Data Delivery (to be written)    | `specs/L2-modules/data-engine/market-data-delivery.md` |
| L3: Market Data Schema (to be written)      | `specs/L3-interfaces/data-contracts/market-data-schema.md` |
| L3: Database Schema (to be written)         | `specs/L3-interfaces/database-schemas/schema.md`      |
| Guardrails: Data Quality (to be written)    | `specs/guardrails/data-quality-guardrails.md`         |

---
```
