## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This module is the **heartbeat of the entire system**. It is responsible
for acquiring daily OHLCV market data from external providers, translating
it into canonical format, validating it for quality, and persisting it for
consumption by every other domain.

Without this module functioning correctly and reliably, the system has
no price data, no return calculations, no technical indicators, no
portfolio values, and no risk metrics. It is the single most critical
module in Phase 1.

## Module Identity

| Attribute          | Value                                                   |
|--------------------|---------------------------------------------------------|
| Module Name        | Market Data Ingestion                                    |
| Domain             | Data Engine                                              |
| Phase              | 1                                                        |
| Priority           | CRITICAL — first module to build and deploy              |
| Location           | `src/data_engine/ingestion/`                             |
| Primary Service    | `IngestionService`                                       |
| Key Files          | `service.py`, `job_runner.py`, `backfill.py`, `checkpoint.py` |
| L1 Reference       | `specs/L1-domains/data-engine.md` Section 5.2, Item 1   |
| L4 References      | `coding-standards.md`, `data-pipeline-standards.md`, `financial-calculation-standards.md`, `testing-standards.md` |

---

# 1. MODULE OVERVIEW

## 1.1 Responsibilities

```text
THIS MODULE DOES:
  ✓ Orchestrate fetching of daily OHLCV data from external providers
  ✓ Select primary provider and fail over to fallback on failure
  ✓ Invoke canonical transformation (dollars → cents, timestamps → UTC)
  ✓ Invoke data validation pipeline before storage
  ✓ Persist validated data via the repository layer
  ✓ Track ingestion runs for monitoring and audit
  ✓ Support batch ingestion for the full watchlist
  ✓ Support single-ticker ingestion for on-demand refresh
  ✓ Support historical backfill for new tickers
  ✓ Emit domain events on completion, failure, and anomalies
  ✓ Handle idempotent re-runs via upsert semantics
  ✓ Resume interrupted batch runs via checkpointing

THIS MODULE DOES NOT:
  ✗ Store data directly (delegates to MarketDataRepository)
  ✗ Manage the cache (delegates to CachedMarketDataRepository)
  ✗ Call external APIs directly (delegates to Provider Adapters)
  ✗ Compute indicators, ratios, or derived metrics
  ✗ Decide which tickers to ingest (receives ticker list from caller)
  ✗ Manage the watchlist (WatchlistService is a separate module)
  ✗ Schedule itself (Scheduler is a separate infrastructure component)
```

## 1.2 Module Context Diagram

```text
                  ┌──────────────────────────────┐
                  │      CALLERS                  │
                  │                               │
                  │  ScheduledJob  ManualTrigger  │
                  │  BackfillReq   WatchlistEvent │
                  └───────────┬───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    MARKET DATA INGESTION MODULE                  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Ingestion    │  │ Job Runner   │  │ Backfill Service     │  │
│  │ Service      │  │              │  │                      │  │
│  │              │  │ Batch exec   │  │ Historical range     │  │
│  │ Single-ticker│  │ Concurrency  │  │ Chunking             │  │
│  │ orchestration│  │ Progress log │  │ Resume support       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │               │
│         └─────────────────┼──────────────────────┘               │
│                           │                                      │
│                    ┌──────▼───────┐                              │
│                    │ Checkpoint   │                              │
│                    │ Manager      │                              │
│                    └──────────────┘                              │
│                                                                  │
└───────┬────────────────┬───────────────────┬────────────────────┘
        │                │                   │
        ▼                ▼                   ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐
  │ Provider │    │ Validation   │    │ Repository   │
  │ Failover │    │ Pipeline     │    │ (Storage)    │
  │ Manager  │    │              │    │              │
  └──────────┘    └──────────────┘    └──────────────┘
        │                                    │
        ▼                                    ▼
  ┌──────────┐                        ┌──────────────┐
  │ Provider │                        │ Event Bus    │
  │ Adapters │                        │              │
  └──────────┘                        └──────────────┘
```

---

# 2. FUNCTIONAL REQUIREMENTS

## FR-001: Ingest Daily OHLCV for a Single Ticker

```text
ID:           FR-001
Title:        Ingest Daily OHLCV for a Single Ticker
Priority:     CRITICAL
Trigger:      Called by JobRunner, BackfillService, or manual trigger
```

### Description

Fetch the latest daily OHLCV bars for a single ticker from external
providers, validate, and store. This is the **atomic unit** of ingestion
that all higher-level operations (batch, backfill) decompose into.

### Preconditions

- Ticker is a valid, non-empty, uppercase string
- Target date is a trading day (or date range includes trading days)
- At least one provider is configured and healthy
- Database connection is available

### Input

```python
class IngestTickerRequest(BaseModel):
    """Input for single-ticker ingestion."""

    ticker: str = Field(
        ...,
        description="Uppercase ticker symbol",
        examples=["AAPL", "MSFT"],
    )
    start_date: date = Field(
        ...,
        description="First date to fetch (inclusive)",
    )
    end_date: date = Field(
        ...,
        description="Last date to fetch (inclusive)",
    )
    force_refresh: bool = Field(
        default=False,
        description="If True, fetch even if data already exists for this range",
    )
    correlation_id: str = Field(
        default="",
        description="Trace ID for pipeline correlation",
    )
```

### Processing Steps

```text
Step 1: VALIDATE INPUT
  1.1  Normalize ticker to uppercase, strip whitespace
  1.2  Validate ticker is non-empty and matches pattern [A-Z]{1,5}
  1.3  Validate start_date <= end_date
  1.4  Validate date range contains at least one trading day
  1.5  If force_refresh is False:
       Check if data already exists for full range
       If complete data exists and is fresh → return early (cache hit)

Step 2: DETERMINE FETCH RANGE
  2.1  Query repository for the latest stored date for this ticker
  2.2  If data exists and force_refresh is False:
       Adjust start_date to day after latest stored date
  2.3  If adjusted range is empty (all dates covered) → return early
  2.4  Log the effective fetch range

Step 3: FETCH FROM PROVIDER
  3.1  Call ProviderFailoverManager.fetch() with:
       - category: "market_data_daily"
       - method: "fetch_daily_bars"
       - ticker, start_date, end_date, adjusted=True
  3.2  Failover manager tries primary, then fallback(s)
  3.3  If ALL providers fail → return Failure with error details

Step 4: VALIDATE DATA
  4.1  Run each bar through the ValidationPipeline
  4.2  Classify each bar: ACCEPT, FLAG, or REJECT
  4.3  Collect accepted bars (including flagged with warnings)
  4.4  Log rejected bars with rule ID and details
  4.5  If ALL bars rejected → return Failure

Step 5: PERSIST DATA
  5.1  Call repository.store_bars(accepted_bars)
  5.2  Repository uses UPSERT semantics
  5.3  Cache invalidation triggered by repository write
  5.4  If write fails → return Failure

Step 6: EMIT EVENTS
  6.1  Publish "data.ingestion.ticker_completed" event with:
       - ticker, date range, bar count, source provider
  6.2  If any bars were flagged with anomalies:
       Publish "data.validation.anomaly_detected" for each
  6.3  Events include correlation_id for tracing

Step 7: RETURN RESULT
  7.1  Return Success with IngestionResult:
       - ticker, date range, bars_ingested count
       - bars_flagged count, bars_rejected count
       - source provider name, elapsed_ms
```

### Output

```python
class IngestionResult(BaseModel):
    """Result of a single-ticker ingestion operation."""

    ticker: str
    start_date: date
    end_date: date
    bars_ingested: int
    bars_flagged: int
    bars_rejected: int
    source_provider: str
    was_cache_hit: bool = False       # True if data already existed
    elapsed_ms: int = 0
    quality_warnings: list[str] = Field(default_factory=list)
```

### Error Cases

| ID   | Condition                              | Error Code                          | Behavior                                          |
|------|----------------------------------------|-------------------------------------|----------------------------------------------------|
| E-01 | Empty or invalid ticker                | `DATA.INGESTION.INVALID_TICKER`     | Return Failure immediately, no provider call       |
| E-02 | start_date > end_date                  | `DATA.INGESTION.INVALID_DATE_RANGE` | Return Failure immediately                         |
| E-03 | No trading days in range               | `DATA.INGESTION.NO_TRADING_DAYS`    | Return Success with bars_ingested=0                |
| E-04 | Primary provider fails                 | (internal)                          | Log warning, try fallback provider                 |
| E-05 | All providers fail                     | `DATA.FAILOVER.ALL_FAILED`          | Return Failure with provider details               |
| E-06 | Provider rate limited                  | `DATA.PROVIDER.*.RATE_LIMITED`      | Wait and retry (handled by adapter)                |
| E-07 | All fetched bars fail validation       | `DATA.VALIDATION.ALL_REJECTED`      | Return Failure with rejection details              |
| E-08 | Database write fails                   | `DATA.STORAGE.WRITE_FAILED`         | Return Failure, do not emit events                 |
| E-09 | Provider returns empty result          | `DATA.INGESTION.NO_DATA_RETURNED`   | Return Success with bars_ingested=0, log warning   |
| E-10 | Provider returns fewer bars than expected | (no error)                       | Accept what was returned, log INFO with expected vs actual |

### Side Effects

| Side Effect                                   | Condition                     |
|-----------------------------------------------|-------------------------------|
| Bars written to database                      | At least 1 bar passes validation |
| Cache entries invalidated for this ticker     | Bars written to database      |
| Event `data.ingestion.ticker_completed`       | Ingestion succeeds            |
| Event `data.validation.anomaly_detected`      | Any bar flagged               |
| Log entries at INFO level                     | Always                        |
| Log entries at WARNING level                  | Provider failover or flagged bars |

### Performance Requirements

| Metric                     | Target      | Notes                               |
|----------------------------|-------------|--------------------------------------|
| Single ticker latency      | < 5s        | Including provider call              |
| Validation latency per bar | < 1ms       | Pure computation, no I/O             |
| Database write latency     | < 100ms     | For typical batch of 1-252 bars      |

---

## FR-002: Batch Ingest Watchlist

```text
ID:           FR-002
Title:        Batch Ingest Daily OHLCV for Entire Watchlist
Priority:     CRITICAL
Trigger:      Scheduled daily job (6:00 PM ET) or manual trigger
```

### Description

Execute FR-001 for every ticker on the active watchlist, with bounded
concurrency, error isolation per ticker, progress tracking, and aggregate
reporting.

### Preconditions

- Watchlist is non-empty
- WatchlistService is available
- At least one provider is healthy

### Input

```python
class BatchIngestionRequest(BaseModel):
    """Input for batch watchlist ingestion."""

    target_date: date = Field(
        ...,
        description="Date to ingest data for (typically today)",
    )
    tickers: list[str] | None = Field(
        default=None,
        description="Specific tickers to ingest. If None, uses full watchlist.",
    )
    max_concurrent: int = Field(
        default=10,
        description="Maximum concurrent ticker ingestions",
    )
    force_refresh: bool = Field(
        default=False,
        description="Force re-fetch even if data exists",
    )
    correlation_id: str = Field(
        default="",
        description="Pipeline trace ID",
    )
```

### Processing Steps

```text
Step 1: RESOLVE TICKER LIST
  1.1  If tickers provided → use provided list
  1.2  If tickers is None → load from WatchlistService.get_tickers()
  1.3  Filter to active tickers only
  1.4  Log ticker count

Step 2: CHECK TRADING DAY
  2.1  Verify target_date is a trading day via TradingCalendar
  2.2  If not a trading day → return early with status "SKIPPED_NON_TRADING_DAY"
  2.3  Log skip reason

Step 3: CREATE INGESTION RUN RECORD
  3.1  Generate run_id (UUID)
  3.2  Create IngestionRun record with status "running"
  3.3  Record: pipeline_name, started_at, tickers_total, trigger_type

Step 4: CHECK FOR EXISTING CHECKPOINT
  4.1  Look for incomplete checkpoint with same pipeline + target_date
  4.2  If found → determine which tickers remain
  4.3  Log resume information

Step 5: EXECUTE WITH BOUNDED CONCURRENCY
  5.1  Create asyncio.Semaphore(max_concurrent)
  5.2  For each ticker (remaining if resuming):
       5.2.1  Acquire semaphore
       5.2.2  Call IngestionService.ingest(ticker, target_date, target_date)
       5.2.3  Record result (success/failure/error code)
       5.2.4  Release semaphore
       5.2.5  Update checkpoint after each ticker
  5.3  Individual ticker failures do NOT stop the batch
  5.4  Per-ticker timeout enforced (configurable, default 30s)

Step 6: AGGREGATE RESULTS
  6.1  Count: succeeded, failed, skipped (cache hit)
  6.2  Collect: failed tickers with error codes
  6.3  Calculate: elapsed time, success rate

Step 7: UPDATE INGESTION RUN RECORD
  7.1  Set status to "completed" or "partial" (if any failures)
  7.2  Record: completed_at, tickers_succeeded, tickers_failed, elapsed_ms
  7.3  Store failed_tickers list with error codes

Step 8: EMIT BATCH COMPLETION EVENT
  8.1  Publish "data.ingestion.completed" with aggregate stats
  8.2  If failures > 0: include list of failed tickers

Step 9: RETURN BATCH RESULT
```

### Output

```python
class BatchIngestionResult(BaseModel):
    """Result of a batch ingestion operation."""

    run_id: str
    pipeline_name: str
    target_date: date
    trigger_type: str                          # "scheduled" | "manual" | "backfill"
    started_at: datetime
    completed_at: datetime
    elapsed_ms: int

    # Counts
    tickers_total: int
    tickers_succeeded: int
    tickers_failed: int
    tickers_skipped: int                       # Non-trading day or cache hit
    bars_total_ingested: int
    bars_total_flagged: int
    bars_total_rejected: int

    # Details
    success_rate_pct: float
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)
    status: str                                # "completed" | "partial" | "failed"
    was_resumed: bool = False
    correlation_id: str = ""


class FailedTickerDetail(BaseModel):
    """Details about a failed ticker ingestion."""

    ticker: str
    error_code: str
    error_message: str
```

### Error Cases

| ID   | Condition                               | Error Code                           | Behavior                                         |
|------|-----------------------------------------|--------------------------------------|---------------------------------------------------|
| E-11 | Watchlist is empty                      | `DATA.INGESTION.EMPTY_WATCHLIST`     | Return Success with tickers_total=0               |
| E-12 | Target date is not a trading day        | (no error)                           | Return Success with status "SKIPPED_NON_TRADING_DAY" |
| E-13 | All tickers fail                        | (aggregate)                          | Return BatchResult with status "failed"           |
| E-14 | Some tickers fail                       | (aggregate)                          | Return BatchResult with status "partial"          |
| E-15 | Single ticker times out                 | `DATA.INGESTION.TICKER_TIMEOUT`      | Record failure, continue with next ticker         |
| E-16 | Database connection lost mid-batch      | `DATA.STORAGE.CONNECTION_LOST`       | Checkpoint progress, halt batch, alert            |
| E-17 | Rate limit exhausted mid-batch          | `DATA.PROVIDER.*.RATE_LIMITED`       | Pause and wait, or switch to fallback provider    |

### Side Effects

| Side Effect                                   | Condition                            |
|-----------------------------------------------|--------------------------------------|
| IngestionRun record created and updated        | Always                               |
| Checkpoint records created and updated         | During batch execution               |
| Multiple `data.ingestion.ticker_completed`     | For each successful ticker           |
| `data.ingestion.completed` event               | On batch completion                  |
| `data.ingestion.ticker_failed` events          | For each failed ticker               |

---

## FR-003: Backfill Historical Data

```text
ID:           FR-003
Title:        Backfill Historical OHLCV Data for a Ticker
Priority:     HIGH
Trigger:      New ticker added to watchlist, or manual backfill request
```

### Description

Fetch and store historical daily OHLCV data for a ticker spanning a
multi-year date range. Handles large date ranges by chunking into
manageable segments, respecting rate limits, and supporting resume
after interruption.

### Preconditions

- Ticker is valid
- Start date is a past date
- End date is today or earlier
- At least one provider is healthy

### Input

```python
class BackfillRequest(BaseModel):
    """Input for historical backfill."""

    ticker: str
    start_date: date
    end_date: date
    chunk_size_days: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Split range into chunks of this many calendar days",
    )
    delay_between_chunks_seconds: float = Field(
        default=2.0,
        ge=0,
        description="Rate-limit courtesy delay between chunks",
    )
    force_refresh: bool = False
    correlation_id: str = ""
```

### Processing Steps

```text
Step 1: VALIDATE AND PLAN
  1.1  Validate ticker and date range
  1.2  Split date range into chunks of chunk_size_days
       Example: 3 years = ~12 chunks of 90 days
  1.3  Calculate total expected trading days
  1.4  Log backfill plan: ticker, range, chunk count

Step 2: CHECK FOR EXISTING CHECKPOINT
  2.1  Look for incomplete backfill checkpoint for this ticker + range
  2.2  If found → determine which chunks remain
  2.3  Log resume information

Step 3: PROCESS EACH CHUNK
  3.1  For each chunk (remaining if resuming):
       3.1.1  Call IngestionService.ingest(ticker, chunk_start, chunk_end)
       3.1.2  Record chunk result
       3.1.3  Update checkpoint
       3.1.4  If delay configured → asyncio.sleep(delay)
  3.2  Chunk failure does NOT stop the backfill
       (skip chunk, record failure, continue)

Step 4: AGGREGATE AND REPORT
  4.1  Total bars ingested across all chunks
  4.2  Any chunks that failed (gaps in history)
  4.3  Date coverage: first bar date to last bar date

Step 5: EMIT BACKFILL COMPLETION EVENT
  5.1  Publish "data.backfill.completed" with:
       ticker, date range, total bars, any gaps
```

### Output

```python
class BackfillResult(BaseModel):
    """Result of a backfill operation."""

    ticker: str
    requested_start_date: date
    requested_end_date: date
    actual_first_bar_date: date | None
    actual_last_bar_date: date | None

    total_chunks: int
    chunks_succeeded: int
    chunks_failed: int
    total_bars_ingested: int
    total_bars_flagged: int
    total_bars_rejected: int

    elapsed_ms: int
    gaps: list[DateGap] = Field(default_factory=list)
    status: str                     # "completed" | "partial" | "failed"


class DateGap(BaseModel):
    """A gap in historical data coverage."""

    start_date: date
    end_date: date
    reason: str                     # e.g., "chunk_failed", "no_data_from_provider"
```

### Error Cases

| ID   | Condition                               | Error Code                         | Behavior                                |
|------|-----------------------------------------|------------------------------------|-----------------------------------------|
| E-20 | Date range too far in past for provider | `DATA.BACKFILL.RANGE_EXCEEDED`     | Fetch what's available, note the gap    |
| E-21 | All chunks fail for a ticker            | `DATA.BACKFILL.ALL_CHUNKS_FAILED`  | Return status "failed" with details     |
| E-22 | Provider has no history for this ticker | `DATA.BACKFILL.NO_HISTORY`         | Return status "completed" with 0 bars   |

---

## FR-004: Determine Optimal Fetch Range

```text
ID:           FR-004
Title:        Determine Optimal Fetch Range for Incremental Ingestion
Priority:     HIGH
Trigger:      Called internally by FR-001 before provider fetch
```

### Description

Determine the optimal date range to fetch from the provider by checking
what data already exists in storage. This minimizes unnecessary API calls
and data transfer.

### Processing Steps

```text
Step 1: QUERY LATEST STORED DATE
  1.1  Call repository.get_latest_date(ticker)
  1.2  If None → no data exists; fetch full requested range

Step 2: CALCULATE GAP
  2.1  If latest_stored_date >= end_date and not force_refresh:
       → Data is complete. Return None (no fetch needed).
  2.2  If latest_stored_date < start_date:
       → No overlap. Fetch full requested range.
  2.3  If latest_stored_date >= start_date and < end_date:
       → Partial overlap. Adjust start_date to latest_stored_date + 1 trading day.

Step 3: FILTER NON-TRADING DAYS
  3.1  Verify the adjusted range contains at least one trading day
  3.2  If no trading days in range → return None (no fetch needed)

Step 4: RETURN ADJUSTED RANGE
  4.1  Return (adjusted_start_date, end_date) or None
```

### Output

```python
class FetchRangeDetermination(BaseModel):
    """Result of fetch range analysis."""

    ticker: str
    original_start_date: date
    original_end_date: date
    effective_start_date: date | None     # None = no fetch needed
    effective_end_date: date | None       # None = no fetch needed
    latest_stored_date: date | None
    fetch_needed: bool
    reason: str                           # "no_data" | "gap" | "up_to_date" | "force"
    estimated_trading_days: int
```

---

## FR-005: Smart Refresh on Stale Data

```text
ID:           FR-005
Title:        Auto-Refresh Stale Data on Consumer Request
Priority:     HIGH
Trigger:      Called by MarketDataService when data is stale
```

### Description

When a consuming domain requests data and the freshness check indicates
staleness, trigger a targeted ingestion for just the stale date range
before returning data. This happens transparently to the consumer.

### Processing Steps

```text
Step 1: RECEIVE STALE DATA NOTIFICATION
  1.1  MarketDataService detects data is stale via FreshnessTracker
  1.2  Calls IngestionService.refresh(ticker, stale_from_date)

Step 2: DETERMINE REFRESH RANGE
  2.1  stale_from_date → today (or last trading day if today is not trading day)
  2.2  Typically a small range (1-5 days for daily refresh)

Step 3: EXECUTE INGESTION
  3.1  Call FR-001 with the refresh range
  3.2  Use shorter timeout (10s instead of 30s)
  3.3  If ingestion fails → return stale data with freshness warning
       (stale data is better than no data)

Step 4: RETURN
  4.1  If refresh succeeded → consumer gets fresh data
  4.2  If refresh failed → consumer gets stale data + warning flag
```

### Important Constraints

```text
⚠  AUTO-REFRESH CONSTRAINTS:
  - Max 1 concurrent refresh per ticker (deduplicate)
  - Refresh timeout: 10 seconds (shorter than normal ingestion)
  - If refresh fails, serve stale data — never block the consumer
  - Refresh does NOT retry on failure (consumer is waiting)
  - Log refresh attempts at INFO level for tracking
  - Do not auto-refresh if the last refresh attempt was < 5 minutes ago
    (prevent refresh storms)
```

---

## FR-006: Ingestion Run Tracking

```text
ID:           FR-006
Title:        Track and Record Ingestion Run Metadata
Priority:     MEDIUM
Trigger:      Every batch ingestion (FR-002) creates and updates a run record
```

### Description

Create and maintain a record for every batch ingestion execution,
enabling operational monitoring, success rate tracking, and debugging
of failed runs.

### Data Model

```python
class IngestionRun(BaseModel):
    """Record of a batch ingestion execution."""

    run_id: str = Field(
        ...,
        description="UUID v4 unique identifier",
    )
    pipeline_name: str = Field(
        ...,
        description="Identifier for the pipeline type",
        examples=["daily_ohlcv_refresh", "fundamental_refresh"],
    )
    trigger_type: str = Field(
        ...,
        description="What triggered this run",
        examples=["scheduled", "manual", "backfill", "auto_refresh"],
    )

    # Timing
    started_at: datetime
    completed_at: datetime | None = None
    elapsed_ms: int | None = None

    # Status
    status: str = Field(
        default="running",
        description="'running' | 'completed' | 'partial' | 'failed' | 'cancelled'",
    )

    # Metrics
    tickers_total: int = 0
    tickers_succeeded: int = 0
    tickers_failed: int = 0
    tickers_skipped: int = 0
    bars_ingested: int = 0
    bars_flagged: int = 0
    bars_rejected: int = 0

    # Failure details
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)

    # Context
    target_date: date | None = None
    correlation_id: str = ""
    notes: str = ""
```

### Lifecycle

```text
  CREATED (status: "running")
      │
      ├── tickers processing...
      │   (tickers_succeeded/failed incrementing)
      │
      ├── On normal completion ──→ status: "completed"
      ├── On partial failure ────→ status: "partial"
      ├── On total failure ──────→ status: "failed"
      └── On cancellation ───────→ status: "cancelled"
```

---

## FR-007: Ingestion Checkpoint Management

```text
ID:           FR-007
Title:        Checkpoint Management for Resumable Ingestion
Priority:     MEDIUM
Trigger:      During batch (FR-002) and backfill (FR-003) execution
```

### Description

Maintain checkpoints during long-running ingestion operations to enable
resume-after-failure without re-processing already-completed items.

### Data Model

```python
class IngestionCheckpoint(BaseModel):
    """Checkpoint state for a resumable ingestion operation."""

    checkpoint_id: str                     # UUID
    pipeline_name: str
    run_id: str
    target_date: date | None = None

    # Progress
    tickers_total: int
    tickers_processed: int = 0             # completed + failed
    tickers_completed: int = 0
    tickers_failed: int = 0
    last_processed_ticker: str = ""

    # State
    status: str = "active"                 # "active" | "completed" | "abandoned"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # The full ticker list (for determining remaining)
    all_tickers: list[str] = Field(default_factory=list)
```

### Processing Logic

```text
CREATE checkpoint at batch/backfill start:
  - Record all_tickers, tickers_total
  - Set status = "active"

UPDATE checkpoint after each ticker completes:
  - Increment tickers_processed, tickers_completed or tickers_failed
  - Set last_processed_ticker
  - Update updated_at

ON RESUME:
  - Find active checkpoint for (pipeline_name, target_date)
  - Calculate remaining_tickers = all_tickers[processed_index+1:]
  - Log resume with remaining count
  - Continue processing remaining tickers
  - On completion, set status = "completed"

ON ABANDON (manual or timeout):
  - Set status = "abandoned"
  - Log final state
```

---

# 3. SERVICE INTERFACE

## 3.1 IngestionService — Full Interface

```python
# src/data_engine/ingestion/service.py

class IngestionService:
    """Orchestrates market data ingestion from external providers.

    This is the primary entry point for all data ingestion operations.
    It coordinates provider calls, validation, storage, and event emission.

    Dependencies (injected via constructor):
        - failover_manager: ProviderFailoverManager
        - validation_pipeline: ValidationPipeline
        - repository: MarketDataRepository
        - event_bus: EventBus
        - freshness_tracker: FreshnessTracker
        - trading_calendar: TradingCalendar

    See: specs/L2-modules/data-engine/market-data-ingestion.md
    """

    def __init__(
        self,
        failover_manager: ProviderFailoverManager,
        validation_pipeline: ValidationPipeline,
        repository: MarketDataRepository,
        event_bus: EventBus,
        freshness_tracker: FreshnessTracker,
        trading_calendar: TradingCalendar,
    ) -> None:
        ...

    async def ingest(
        self,
        request: IngestTickerRequest,
    ) -> Result[IngestionResult, DataError]:
        """Ingest daily OHLCV data for a single ticker.

        Implements FR-001. This is the atomic unit of ingestion.
        All higher-level operations decompose into calls to this method.

        See: FR-001 processing steps for detailed flow.
        """
        ...

    async def refresh(
        self,
        ticker: str,
        from_date: date | None = None,
    ) -> Result[IngestionResult, DataError]:
        """Refresh stale data for a ticker.

        Implements FR-005. Called by MarketDataService when
        auto-refresh is triggered.

        Uses shorter timeout and does not retry on failure.
        """
        ...

    def determine_fetch_range(
        self,
        ticker: str,
        requested_start: date,
        requested_end: date,
        force_refresh: bool = False,
    ) -> FetchRangeDetermination:
        """Determine optimal date range to fetch.

        Implements FR-004. Checks existing data to minimize
        redundant API calls.
        """
        ...
```

## 3.2 IngestionJobRunner — Full Interface

```python
# src/data_engine/ingestion/job_runner.py

class IngestionJobRunner:
    """Executes batch ingestion jobs with bounded concurrency.

    Runs ingestion for multiple tickers with:
    - Configurable concurrency limit
    - Per-ticker error isolation
    - Progress checkpointing
    - Aggregate result reporting

    Dependencies:
        - ingestion_service: IngestionService
        - watchlist_service: WatchlistService
        - checkpoint_manager: CheckpointManager
        - run_repository: IngestionRunRepository

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-002
    """

    def __init__(
        self,
        ingestion_service: IngestionService,
        watchlist_service: WatchlistService,
        checkpoint_manager: CheckpointManager,
        run_repository: IngestionRunRepository,
        trading_calendar: TradingCalendar,
        event_bus: EventBus,
    ) -> None:
        ...

    async def run_batch(
        self,
        request: BatchIngestionRequest,
    ) -> Result[BatchIngestionResult, DataError]:
        """Execute batch ingestion for watchlist.

        Implements FR-002. Orchestrates parallel ingestion with
        bounded concurrency and error isolation.
        """
        ...

    async def resume_batch(
        self,
        checkpoint_id: str,
    ) -> Result[BatchIngestionResult, DataError]:
        """Resume an interrupted batch ingestion from checkpoint.

        Finds the checkpoint, determines remaining tickers,
        and continues processing.
        """
        ...
```

## 3.3 BackfillService — Full Interface

```python
# src/data_engine/ingestion/backfill.py

class BackfillService:
    """Manages historical data backfilling.

    Handles large date ranges by chunking, with rate limit awareness,
    progress tracking, and resume support.

    Dependencies:
        - ingestion_service: IngestionService
        - checkpoint_manager: CheckpointManager

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-003
    """

    def __init__(
        self,
        ingestion_service: IngestionService,
        checkpoint_manager: CheckpointManager,
        event_bus: EventBus,
    ) -> None:
        ...

    async def backfill(
        self,
        request: BackfillRequest,
    ) -> Result[BackfillResult, DataError]:
        """Execute historical data backfill.

        Implements FR-003. Splits the date range into chunks,
        processes each chunk via IngestionService, and tracks
        progress for resume capability.
        """
        ...

    def plan_chunks(
        self,
        start_date: date,
        end_date: date,
        chunk_size_days: int,
    ) -> list[tuple[date, date]]:
        """Split a date range into processing chunks.

        Returns list of (chunk_start, chunk_end) tuples.
        """
        ...
```

## 3.4 CheckpointManager — Full Interface

```python
# src/data_engine/ingestion/checkpoint.py

class CheckpointManager:
    """Manages ingestion checkpoints for resume capability.

    Dependencies:
        - repository: CheckpointRepository (DB persistence)

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-007
    """

    def __init__(
        self,
        repository: CheckpointRepository,
    ) -> None:
        ...

    async def create_checkpoint(
        self,
        pipeline_name: str,
        run_id: str,
        all_tickers: list[str],
        target_date: date | None = None,
    ) -> IngestionCheckpoint:
        """Create a new checkpoint at the start of a batch operation."""
        ...

    async def update_checkpoint(
        self,
        checkpoint_id: str,
        ticker: str,
        succeeded: bool,
    ) -> None:
        """Update checkpoint after processing a ticker."""
        ...

    async def find_active_checkpoint(
        self,
        pipeline_name: str,
        target_date: date | None = None,
    ) -> IngestionCheckpoint | None:
        """Find an active (incomplete) checkpoint for resuming."""
        ...

    async def complete_checkpoint(
        self,
        checkpoint_id: str,
    ) -> None:
        """Mark a checkpoint as completed."""
        ...

    async def abandon_checkpoint(
        self,
        checkpoint_id: str,
        reason: str = "",
    ) -> None:
        """Mark a checkpoint as abandoned."""
        ...

    def get_remaining_tickers(
        self,
        checkpoint: IngestionCheckpoint,
    ) -> list[str]:
        """Calculate which tickers haven't been processed yet."""
        ...
```

---

# 4. INTERNAL DEPENDENCIES

## 4.1 Dependency Map

```text
┌───────────────────────────────────────────────────────────────────┐
│                  MARKET DATA INGESTION MODULE                     │
│                                                                   │
│   ┌─────────────────┐        ┌─────────────────────┐            │
│   │ IngestionJobRunner│──────→│ IngestionService     │            │
│   └────────┬─────────┘        └────────┬────────────┘            │
│            │                           │                          │
│   ┌────────▼─────────┐        ┌───────▼────────────┐            │
│   │ CheckpointManager│        │ BackfillService    │            │
│   └──────────────────┘        └────────────────────┘            │
│                                                                   │
│   DEPENDS ON (from other modules within Data Engine):            │
│   ├── ProviderFailoverManager (data_engine/providers/failover)   │
│   ├── ValidationPipeline (data_engine/validation/validator)       │
│   ├── MarketDataRepository (data_engine/storage/market_data_repo)│
│   ├── IngestionRunRepository (data_engine/storage/ingestion_run) │
│   ├── CheckpointRepository (data_engine/storage/checkpoint)      │
│   ├── WatchlistService (data_engine/services/watchlist)           │
│   ├── FreshnessTracker (data_engine/freshness/tracker)           │
│   └── TradingCalendar (data_engine/calendar/trading_calendar)    │
│                                                                   │
│   DEPENDS ON (from shared infrastructure):                       │
│   ├── EventBus (shared/interfaces)                               │
│   ├── Logger (structlog)                                         │
│   └── Config (data_engine configuration)                         │
│                                                                   │
│   DEPENDED ON BY:                                                │
│   ├── MarketDataService (for auto-refresh, FR-005)               │
│   ├── Scheduler (for daily scheduled jobs)                       │
│   └── WatchlistService (triggers backfill on new ticker)         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## 4.2 Dependency Rules

| Rule | Description |
|------|-------------|
| **DEP-001** | Ingestion module never calls provider adapters directly — always through FailoverManager |
| **DEP-002** | Ingestion module never writes to database directly — always through Repository |
| **DEP-003** | Ingestion module never manages cache — cache invalidation is Repository's responsibility |
| **DEP-004** | Ingestion module never accesses configuration directly — values injected via constructor |
| **DEP-005** | All dependencies injected via constructor, never created internally |

---

# 5. DATA MODELS (Module-Scoped)

All data models used internally within this module:

```python
# src/data_engine/ingestion/models.py

"""Data models for the Market Data Ingestion module.

These models are used internally within the ingestion pipeline.
External consumers interact with canonical models from
src/data_engine/models/.
"""

from pydantic import BaseModel, Field
from datetime import date, datetime, timezone


# ── Request Models ──
# (Defined above in FR-001, FR-002, FR-003)
# IngestTickerRequest
# BatchIngestionRequest
# BackfillRequest


# ── Result Models ──

class IngestionResult(BaseModel):
    """Result of a single-ticker ingestion."""

    ticker: str
    start_date: date
    end_date: date
    bars_ingested: int
    bars_flagged: int
    bars_rejected: int
    source_provider: str
    was_cache_hit: bool = False
    elapsed_ms: int = 0
    quality_warnings: list[str] = Field(default_factory=list)


class BatchIngestionResult(BaseModel):
    """Result of a batch ingestion."""

    run_id: str
    pipeline_name: str
    target_date: date
    trigger_type: str
    started_at: datetime
    completed_at: datetime
    elapsed_ms: int

    tickers_total: int
    tickers_succeeded: int
    tickers_failed: int
    tickers_skipped: int
    bars_total_ingested: int
    bars_total_flagged: int
    bars_total_rejected: int

    success_rate_pct: float
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)
    status: str
    was_resumed: bool = False
    correlation_id: str = ""


class BackfillResult(BaseModel):
    """Result of a historical backfill."""

    ticker: str
    requested_start_date: date
    requested_end_date: date
    actual_first_bar_date: date | None
    actual_last_bar_date: date | None

    total_chunks: int
    chunks_succeeded: int
    chunks_failed: int
    total_bars_ingested: int
    total_bars_flagged: int
    total_bars_rejected: int

    elapsed_ms: int
    gaps: list[DateGap] = Field(default_factory=list)
    status: str


class FailedTickerDetail(BaseModel):
    """Details about a single ticker's ingestion failure."""

    ticker: str
    error_code: str
    error_message: str


class DateGap(BaseModel):
    """A gap in date coverage during backfill."""

    start_date: date
    end_date: date
    reason: str


class FetchRangeDetermination(BaseModel):
    """Result of fetch range analysis."""

    ticker: str
    original_start_date: date
    original_end_date: date
    effective_start_date: date | None
    effective_end_date: date | None
    latest_stored_date: date | None
    fetch_needed: bool
    reason: str
    estimated_trading_days: int


# ── Operational Models ──

class IngestionRun(BaseModel):
    """Record of a batch ingestion execution."""

    run_id: str
    pipeline_name: str
    trigger_type: str
    started_at: datetime
    completed_at: datetime | None = None
    elapsed_ms: int | None = None
    status: str = "running"

    tickers_total: int = 0
    tickers_succeeded: int = 0
    tickers_failed: int = 0
    tickers_skipped: int = 0
    bars_ingested: int = 0
    bars_flagged: int = 0
    bars_rejected: int = 0

    target_date: date | None = None
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)
    correlation_id: str = ""
    notes: str = ""


class IngestionCheckpoint(BaseModel):
    """Checkpoint for resumable ingestion operations."""

    checkpoint_id: str
    pipeline_name: str
    run_id: str
    target_date: date | None = None

    tickers_total: int
    tickers_processed: int = 0
    tickers_completed: int = 0
    tickers_failed: int = 0
    last_processed_ticker: str = ""

    status: str = "active"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    all_tickers: list[str] = Field(default_factory=list)
```

---

# 6. ERROR HANDLING

## 6.1 Module Error Classes

```python
# src/data_engine/ingestion/errors.py

"""Ingestion-specific error classes.

Inherits from DataError (Data Engine domain base error).
"""

from dataclasses import dataclass
from src.data_engine.errors import DataError


@dataclass(frozen=True)
class IngestionError(DataError):
    """Base error for ingestion operations."""
    ticker: str = ""
    pipeline_name: str = ""


@dataclass(frozen=True)
class InvalidTickerError(IngestionError):
    """Ticker symbol is invalid or empty."""
    pass


@dataclass(frozen=True)
class InvalidDateRangeError(IngestionError):
    """Date range is invalid (start > end, no trading days, etc.)."""
    start_date: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class AllProvidersFailedError(IngestionError):
    """All configured providers failed for this request."""
    providers_attempted: list[str] | None = None
    last_error_code: str = ""


@dataclass(frozen=True)
class AllBarsRejectedError(IngestionError):
    """All fetched bars failed validation."""
    rejection_count: int = 0
    rejection_reasons: list[str] | None = None


@dataclass(frozen=True)
class TickerTimeoutError(IngestionError):
    """Single ticker ingestion exceeded timeout."""
    timeout_seconds: int = 0


@dataclass(frozen=True)
class BatchAbortedError(IngestionError):
    """Batch ingestion was aborted (e.g., DB connection lost)."""
    tickers_completed_before_abort: int = 0
    reason: str = ""
```

## 6.2 Error Handling Decision Matrix

```text
┌──────────────────────────────┬────────────────────┬───────────────────────┐
│ Error Condition              │ Within Single      │ Within Batch          │
│                              │ Ticker (FR-001)    │ (FR-002)              │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Invalid ticker               │ Return Failure     │ Skip ticker, record   │
│                              │ immediately        │ as failed             │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Primary provider fails       │ Try fallback       │ Same (per-ticker)     │
│                              │ automatically      │                       │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ All providers fail           │ Return Failure     │ Record ticker as      │
│                              │                    │ failed, continue batch│
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Provider rate limited        │ Wait (via adapter) │ Same, affects all     │
│                              │ then retry         │ subsequent tickers    │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Some bars fail validation    │ Store valid bars,  │ Same (per-ticker)     │
│                              │ reject invalid     │                       │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ All bars fail validation     │ Return Failure     │ Record ticker as      │
│                              │ (no data to store) │ failed, continue batch│
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Database write fails         │ Return Failure     │ Checkpoint, halt if   │
│                              │                    │ persistent (DB down)  │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Ticker ingestion timeout     │ Return Failure     │ Record as failed,     │
│                              │                    │ continue with next    │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Provider returns empty data  │ Return Success     │ Record as success     │
│                              │ (0 bars, warning)  │ (0 bars, not failure) │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ DB connection lost           │ Return Failure     │ Checkpoint progress,  │
│                              │                    │ halt batch, ALERT     │
└──────────────────────────────┴────────────────────┴───────────────────────┘
```

---

# 7. LOGGING SPECIFICATION

## 7.1 Mandatory Log Points

```python
# ── FR-001: Single Ticker Ingestion ──

# Entry
logger.info("Ticker ingestion started",
    ticker=ticker, start_date=start_date, end_date=end_date,
    force_refresh=force_refresh, correlation_id=correlation_id)

# Fetch range determination
logger.info("Fetch range determined",
    ticker=ticker, fetch_needed=True, effective_start=start,
    effective_end=end, latest_stored=stored_date, reason=reason)

# Provider selection
logger.debug("Attempting provider",
    ticker=ticker, provider=provider_name, attempt=1)

# Provider failover (WARNING)
logger.warning("Primary provider failed, using fallback",
    ticker=ticker, failed_provider=primary, fallback_provider=fallback,
    error_code=error.code)

# Validation results
logger.info("Validation completed",
    ticker=ticker, accepted=accepted_count, flagged=flagged_count,
    rejected=rejected_count)

# Anomaly detected (WARNING)
logger.warning("Data anomaly detected",
    ticker=ticker, date=bar_date, rule_id=rule_id,
    severity=severity, details=details)

# Completion
logger.info("Ticker ingestion completed",
    ticker=ticker, bars_ingested=count, source=provider,
    elapsed_ms=elapsed, correlation_id=correlation_id)

# Failure
logger.error("Ticker ingestion failed",
    ticker=ticker, error_code=error.code, error_message=error.message,
    stage=stage, correlation_id=correlation_id)


# ── FR-002: Batch Ingestion ──

# Batch start
logger.info("Batch ingestion started",
    pipeline=pipeline_name, run_id=run_id, ticker_count=count,
    target_date=target_date, max_concurrent=max_concurrent,
    trigger_type=trigger_type, correlation_id=correlation_id)

# Non-trading day skip
logger.info("Batch skipped — non-trading day",
    target_date=target_date, day_of_week=day_name)

# Resume from checkpoint
logger.info("Resuming from checkpoint",
    run_id=run_id, checkpoint_id=checkpoint_id,
    tickers_remaining=remaining_count,
    tickers_already_completed=completed_count)

# Batch progress (every 10% or every 20 tickers, whichever is more frequent)
logger.info("Batch progress",
    run_id=run_id, processed=processed, total=total,
    pct_complete=f"{processed/total*100:.0f}%",
    succeeded=succeeded, failed=failed)

# Batch completion
logger.info("Batch ingestion completed",
    pipeline=pipeline_name, run_id=run_id,
    tickers_total=total, succeeded=succeeded, failed=failed,
    skipped=skipped, bars_ingested=total_bars,
    elapsed_ms=elapsed, success_rate=f"{rate:.1f}%",
    status=status, correlation_id=correlation_id)

# Failed tickers summary (if any)
logger.warning("Failed tickers in batch",
    run_id=run_id, failed_count=len(failed),
    tickers=[{t: code} for t, code in failed_tickers])


# ── FR-003: Backfill ──

# Backfill start
logger.info("Backfill started",
    ticker=ticker, start_date=start, end_date=end,
    total_chunks=chunk_count, chunk_size_days=chunk_size)

# Chunk progress
logger.info("Backfill chunk completed",
    ticker=ticker, chunk=f"{i+1}/{total}",
    chunk_range=f"{chunk_start} to {chunk_end}",
    bars_ingested=count)

# Backfill completion
logger.info("Backfill completed",
    ticker=ticker, total_bars=total, chunks_succeeded=ok,
    chunks_failed=fail, gaps=len(gaps), elapsed_ms=elapsed)
```

---

# 8. CONFIGURATION

## 8.1 Module-Specific Configuration

```yaml
# Extracted from config/data_engine.yaml
# These values are injected into module services via DI.

data_engine:
  ingestion:
    # ── Concurrency ──
    max_concurrent_tickers: 10          # Max parallel ticker ingestions
    per_ticker_timeout_seconds: 30      # Timeout for single ticker
    batch_timeout_seconds: 600          # Total batch timeout (10 min)

    # ── Retry ──
    retry_max: 2                        # Max retries per provider
    backoff_base_seconds: 2             # Exponential backoff base

    # ── Auto-Refresh ──
    refresh_timeout_seconds: 10         # Shorter timeout for auto-refresh
    refresh_cooldown_seconds: 300       # Min time between refresh attempts
    refresh_max_concurrent: 3           # Max concurrent refresh operations

    # ── Backfill ──
    default_backfill_years: 3           # History depth for new tickers
    backfill_chunk_size_days: 90        # Chunk size for backfill
    backfill_delay_between_chunks: 2.0  # Seconds between chunks
    backfill_delay_between_tickers: 1.0 # Seconds between tickers

    # ── Checkpointing ──
    checkpoint_enabled: true
    checkpoint_abandon_after_hours: 24  # Abandon old checkpoints

    # ── Progress Logging ──
    batch_progress_log_interval: 20     # Log progress every N tickers
```

---

# 9. TESTING REQUIREMENTS

## 9.1 Test Coverage Matrix

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    TEST COVERAGE REQUIREMENTS                           │
├───────────────────────────────────┬─────────┬───────────────────────────┤
│ Test Case                         │ Type    │ Priority                  │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-001: SINGLE TICKER INGESTION                                        │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Happy path: fetch + validate +    │ Unit    │ CRITICAL                  │
│   store + event                   │         │                           │
│ Invalid ticker returns Failure    │ Unit    │ CRITICAL                  │
│ Invalid date range returns Failure│ Unit    │ CRITICAL                  │
│ No trading days → Success (0 bars)│ Unit    │ HIGH                      │
│ Primary fails → fallback used     │ Unit    │ CRITICAL                  │
│ All providers fail → Failure      │ Unit    │ CRITICAL                  │
│ Some bars rejected → partial store│ Unit    │ HIGH                      │
│ All bars rejected → Failure       │ Unit    │ HIGH                      │
│ DB write fails → Failure, no event│ Unit    │ HIGH                      │
│ Empty result from provider → 0 bars│ Unit   │ MEDIUM                    │
│ Force refresh bypasses cache check│ Unit    │ MEDIUM                    │
│ Event emitted on success          │ Unit    │ HIGH                      │
│ Event NOT emitted on failure      │ Unit    │ HIGH                      │
│ Anomaly event on flagged bars     │ Unit    │ MEDIUM                    │
│ Correct provider call args        │ Unit    │ HIGH                      │
│ Logging at all mandatory points   │ Unit    │ MEDIUM                    │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-002: BATCH INGESTION                                                │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Happy path: all tickers succeed   │ Unit    │ CRITICAL                  │
│ Some tickers fail → partial status│ Unit    │ CRITICAL                  │
│ All tickers fail → failed status  │ Unit    │ HIGH                      │
│ Non-trading day → skip            │ Unit    │ HIGH                      │
│ Empty watchlist → Success (0)     │ Unit    │ MEDIUM                    │
│ Concurrency bounded by semaphore  │ Unit    │ HIGH                      │
│ Single ticker timeout doesn't     │ Unit    │ CRITICAL                  │
│   stop batch                      │         │                           │
│ IngestionRun created and updated  │ Unit    │ HIGH                      │
│ Checkpoint created and updated    │ Unit    │ HIGH                      │
│ Resume from checkpoint works      │ Unit    │ HIGH                      │
│ Batch completion event emitted    │ Unit    │ MEDIUM                    │
│ Progress logging at intervals     │ Unit    │ LOW                       │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-003: BACKFILL                                                       │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Happy path: all chunks succeed    │ Unit    │ HIGH                      │
│ Date range split into correct     │ Unit    │ HIGH                      │
│   chunks                          │         │                           │
│ Chunk failure → continue, gap     │ Unit    │ HIGH                      │
│   recorded                        │         │                           │
│ Resume from checkpoint works      │ Unit    │ MEDIUM                    │
│ Delay between chunks respected    │ Unit    │ MEDIUM                    │
│ Backfill event emitted            │ Unit    │ LOW                       │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-004: FETCH RANGE DETERMINATION                                      │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ No existing data → full range     │ Unit    │ HIGH                      │
│ Partial data → adjusted range     │ Unit    │ HIGH                      │
│ Complete data → no fetch needed   │ Unit    │ HIGH                      │
│ Force refresh → full range always │ Unit    │ HIGH                      │
│ Weekend adjustment correct        │ Unit    │ MEDIUM                    │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-005: AUTO-REFRESH                                                   │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Stale data triggers refresh       │ Unit    │ HIGH                      │
│ Refresh failure → serve stale data│ Unit    │ CRITICAL                  │
│ Cooldown prevents refresh storms  │ Unit    │ HIGH                      │
│ Shorter timeout enforced          │ Unit    │ MEDIUM                    │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ INTEGRATION TESTS                                                      │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Full pipeline: provider → validate│ Integ.  │ CRITICAL                  │
│   → store → retrieve              │         │                           │
│ Upsert: re-ingestion updates not  │ Integ.  │ CRITICAL                  │
│   duplicates                      │         │                           │
│ Backfill stores multi-year data   │ Integ.  │ HIGH                      │
│ Checkpoint persists to DB and     │ Integ.  │ HIGH                      │
│   resume works                    │         │                           │
│ Provider adapter with recorded    │ Integ.  │ HIGH                      │
│   API response                    │         │                           │
└───────────────────────────────────┴─────────┴───────────────────────────┘
```

## 9.2 Key Test Scenarios

### Scenario 1: Happy Path — Daily Ingestion

```python
@pytest.mark.unit
class TestIngestionServiceHappyPath:
    """FR-001: Standard successful single-ticker ingestion."""

    async def test_fetches_validates_stores_and_emits(
        self,
        ingestion_service: IngestionService,
        mock_failover_manager: AsyncMock,
        mock_validation_pipeline: MagicMock,
        mock_repository: AsyncMock,
        mock_event_bus: AsyncMock,
    ):
        """Complete happy path: fetch → validate → store → event."""

        # Arrange
        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
        )
        expected_bars = [make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15))]

        mock_failover_manager.fetch.return_value = Success(expected_bars)
        mock_validation_pipeline.validate.return_value = ValidationOutcome(
            outcome="ACCEPT", issues=[]
        )
        mock_repository.get_latest_date.return_value = date(2025, 1, 14)
        mock_repository.store_bars.return_value = 1

        # Act
        result = await ingestion_service.ingest(request)

        # Assert
        assert_result_success(result, "Happy path ingestion")
        assert result.value.ticker == "AAPL"
        assert result.value.bars_ingested == 1
        assert result.value.source_provider != ""

        mock_failover_manager.fetch.assert_called_once()
        mock_repository.store_bars.assert_called_once_with(expected_bars)
        mock_event_bus.publish.assert_called_once()
```

### Scenario 2: Provider Failover

```python
class TestIngestionServiceFailover:
    """FR-001: Provider failover behavior."""

    async def test_uses_fallback_when_primary_fails(
        self,
        ingestion_service: IngestionService,
        mock_failover_manager: AsyncMock,
    ):
        """Failover manager handles primary→fallback transparently."""

        # Arrange — failover manager returns success from fallback
        bars = [make_ohlcv_bar(ticker="AAPL", source="alpha_vantage")]
        mock_failover_manager.fetch.return_value = Success(bars)

        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
        )

        # Act
        result = await ingestion_service.ingest(request)

        # Assert — ingestion succeeds regardless of which provider was used
        assert_result_success(result)
        assert result.value.source_provider == "alpha_vantage"

    async def test_returns_failure_when_all_providers_fail(
        self,
        ingestion_service: IngestionService,
        mock_failover_manager: AsyncMock,
    ):
        """When failover manager exhausts all providers → Failure."""

        mock_failover_manager.fetch.return_value = Failure(
            AllProvidersFailedError(
                code="DATA.FAILOVER.ALL_FAILED",
                message="All providers failed for AAPL",
                providers_attempted=["polygon", "alpha_vantage"],
            )
        )

        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
        )

        result = await ingestion_service.ingest(request)

        assert_result_failure(result, "DATA.FAILOVER.ALL_FAILED")
```

### Scenario 3: Batch Error Isolation

```python
class TestBatchIngestionErrorIsolation:
    """FR-002: Individual ticker failures do not stop the batch."""

    async def test_batch_continues_after_ticker_failure(
        self,
        job_runner: IngestionJobRunner,
        mock_ingestion_service: AsyncMock,
    ):
        """One ticker fails, others succeed. Batch reports 'partial'."""

        # Arrange — AAPL succeeds, BADTICKER fails, MSFT succeeds
        async def mock_ingest(request):
            if request.ticker == "BADTICKER":
                return Failure(AllProvidersFailedError(
                    code="DATA.FAILOVER.ALL_FAILED",
                    message="No data for BADTICKER",
                    ticker="BADTICKER",
                ))
            return Success(IngestionResult(
                ticker=request.ticker,
                start_date=request.start_date,
                end_date=request.end_date,
                bars_ingested=1,
                bars_flagged=0,
                bars_rejected=0,
                source_provider="polygon",
            ))

        mock_ingestion_service.ingest.side_effect = mock_ingest

        request = BatchIngestionRequest(
            target_date=date(2025, 1, 15),
            tickers=["AAPL", "BADTICKER", "MSFT"],
            max_concurrent=10,
        )

        # Act
        result = await job_runner.run_batch(request)

        # Assert
        assert_result_success(result)
        assert result.value.tickers_total == 3
        assert result.value.tickers_succeeded == 2
        assert result.value.tickers_failed == 1
        assert result.value.status == "partial"
        assert len(result.value.failed_tickers) == 1
        assert result.value.failed_tickers[0].ticker == "BADTICKER"

        # Verify ALL tickers were attempted (batch didn't stop)
        assert mock_ingestion_service.ingest.call_count == 3
```

### Scenario 4: Idempotent Re-Ingestion

```python
@pytest.mark.integration
class TestIngestionIdempotency:
    """Verify that re-running ingestion produces identical state."""

    async def test_double_ingestion_no_duplicates(
        self,
        ingestion_service: IngestionService,
        test_db: Database,
    ):
        """Running ingestion twice for same ticker+date → same result."""

        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
            force_refresh=True,
        )

        # First ingestion
        result1 = await ingestion_service.ingest(request)
        assert_result_success(result1)

        # Second ingestion (same parameters)
        result2 = await ingestion_service.ingest(request)
        assert_result_success(result2)

        # Verify no duplicates
        repo = MarketDataRepository(db=test_db)
        bars = await repo.get_bars("AAPL", date(2025, 1, 15), date(2025, 1, 15))
        assert len(bars) == 1  # Not 2
```

---

# 10. PERFORMANCE REQUIREMENTS

| Operation                              | Target        | Measurement                    |
|----------------------------------------|---------------|--------------------------------|
| Single ticker ingestion (end-to-end)   | < 5s          | Request to completion          |
| Single ticker ingestion (validation)   | < 10ms        | Validation pipeline only       |
| Single ticker ingestion (DB write)     | < 100ms       | Repository store_bars          |
| Batch ingestion (200 tickers)          | < 10 min      | Total batch duration           |
| Backfill (1 ticker, 3 years)           | < 5 min       | Total backfill duration        |
| Fetch range determination              | < 50ms        | DB query + computation         |
| Checkpoint update                      | < 20ms        | Single checkpoint write        |
| Auto-refresh (stale data)              | < 10s         | Including provider call        |

---

# 11. ACCEPTANCE CRITERIA

These criteria must all pass before this module is considered complete:

```text
ACCEPTANCE CRITERIA — MARKET DATA INGESTION MODULE
═══════════════════════════════════════════════════

FUNCTIONAL:
□ AC-01: System ingests daily OHLCV for a single ticker from FMP successfully
□ AC-02: System fails over to SEC EDGAR when FMP is unavailable
□ AC-03: System returns structured Failure when all providers fail
□ AC-04: Batch ingestion processes 200 tickers with >99% success rate
□ AC-05: Individual ticker failure does not stop the batch
□ AC-06: Non-trading day batch is skipped with appropriate status
□ AC-07: Backfill loads 3 years of history for a newly added ticker
□ AC-08: Backfill resumes from checkpoint after interruption
□ AC-09: Re-ingesting same ticker+date updates, does not duplicate
□ AC-10: Auto-refresh triggers transparently when data is stale
□ AC-11: Auto-refresh failure serves stale data (does not error)
□ AC-12: All OHLCV bars pass validation (high >= low, etc.)
□ AC-13: Bars with >50% daily move are flagged but stored
□ AC-14: Bars with weekend dates are rejected
□ AC-15: Domain events emitted for completion, failure, and anomalies

DATA INTEGRITY:
□ AC-16: All prices stored as integer cents (verified by round-trip test)
□ AC-17: All timestamps stored in UTC
□ AC-18: All tickers normalized to uppercase
□ AC-19: Zero duplicate bars in database after repeated ingestion

OPERATIONAL:
□ AC-20: IngestionRun record created for every batch
□ AC-21: Checkpoint enables resume within 24 hours
□ AC-22: Rate limits respected (never hit provider 429)
□ AC-23: API keys never appear in logs or events
□ AC-24: All mandatory log points present and correct

PERFORMANCE:
□ AC-25: Single ticker ingestion < 5 seconds
□ AC-26: 200-ticker batch < 10 minutes
□ AC-27: 3-year backfill < 5 minutes per ticker

TESTING:
□ AC-28: Unit test coverage > 85% for this module
□ AC-29: All CRITICAL test cases passing
□ AC-30: Integration test with recorded API responses passing
```

---

# 12. CROSS-REFERENCES

| Document                                    | Location                                              |
|---------------------------------------------|-------------------------------------------------------|
| L0: System Vision                           | `specs/L0-system-vision.md`                           |
| L1: Data Engine Domain                      | `specs/L1-domains/data-engine.md`                     |
| L4: Coding Standards                        | `specs/L4-conventions/coding-standards.md`             |
| L4: Data Pipeline Standards                 | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Financial Calculation Standards         | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                       | `specs/L4-conventions/testing-standards.md`            |
| L2: Data Storage (to be written)            | `specs/L2-modules/data-engine/data-storage.md`        |
| L2: Data Validation (to be written)         | `specs/L2-modules/data-engine/data-validation.md`     |
| L2: Market Data Delivery (to be written)    | `specs/L2-modules/data-engine/market-data-delivery.md` |
| L2: Watchlist Management (to be written)    | `specs/L2-modules/data-engine/watchlist-management.md` |
| L3: Market Data Schema (to be written)      | `specs/L3-interfaces/data-contracts/market-data-schema.md` |
| L3: Database Schema (to be written)         | `specs/L3-interfaces/database-schemas/schema.md`      |

---
```
