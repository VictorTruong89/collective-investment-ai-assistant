## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines how data flows through the AI Investment Pipeline —
from external sources through ingestion, transformation, storage, caching,
and delivery to consuming domains. Data is the foundation upon which every
analysis, signal, recommendation, and risk assessment is built. If the data
pipeline is unreliable, inconsistent, or poorly structured, every downstream
component inherits those flaws.

The standards here ensure that data is:
- **Reliable:** Fetched consistently with provider failover and retry logic
- **Canonical:** Transformed into standard internal formats at the boundary
- **Validated:** Checked for quality before entering the system
- **Traceable:** Every data point has provenance (source, timestamp, freshness)
- **Efficient:** Cached appropriately to minimize API costs and latency
- **Idempotent:** Re-running pipelines produces the same result without duplication

**Every developer and every AI coding agent** building data ingestion,
transformation, or delivery components must follow these standards.

## Scope

| In Scope                                        | Out of Scope                           |
|-------------------------------------------------|----------------------------------------|
| Data ingestion patterns and pipeline structure   | Specific provider API documentation     |
| Provider adapter design                          | Database schema design (→ L3 specs)     |
| Data transformation and canonicalization         | LLM data preparation (→ AI agent standards) |
| Caching strategy and invalidation                | Dashboard/UI data delivery              |
| Rate limiting and API cost management            | Data warehouse / analytics architecture |
| Data quality validation                          | Machine learning feature engineering    |
| Idempotency and deduplication                    | Real-time streaming (future phase)      |
| Provider failover and health monitoring          |                                        |
| Scheduling and orchestration of data jobs        |                                        |
| Data retention and archival                      |                                        |

## Governing Principles

From L0-system-vision.md:

| ID      | Rule                                                         |
|---------|--------------------------------------------------------------|
| INV-001 | All monetary values stored as integer cents                  |
| INV-005 | Historical data is immutable once ingested and validated     |
| INV-007 | All timestamps in UTC; display conversion at presentation    |
| INV-030 | API keys and credentials never appear in logs                |
| INV-031 | No external API call without rate-limit compliance           |
| INV-033 | System must remain functional if any single external API fails |
| INV-034 | LLM provider failure must not halt non-LLM operations        |

From L0-system-vision.md Section 6 (Data Architecture Principles):

- All external data transformed into canonical internal formats at ingestion
- No downstream module works with provider-specific formats
- Provider switching must not require downstream changes

---

# 1. DATA PIPELINE ARCHITECTURE

## 1.1 Pipeline Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA PIPELINE FLOW                              │
│                                                                     │
│  EXTERNAL WORLD              BOUNDARY              INTERNAL SYSTEM  │
│                                                                     │
│  ┌──────────┐          ┌──────────────┐         ┌───────────────┐  │
│  │ Polygon  │────────→│              │        │               │  │
│  │ API      │          │   Provider   │        │   Canonical   │  │
│  └──────────┘          │   Adapter    │───────→│   Transform   │  │
│                        │   Layer      │        │               │  │
│  ┌──────────┐          │              │        └───────┬───────┘  │
│  │ Alpha    │────────→│  • Auth      │                │          │
│  │ Vantage  │          │  • Rate Limit│                ▼          │
│  └──────────┘          │  • Retry     │        ┌───────────────┐  │
│                        │  • Translate │        │   Validation  │  │
│  ┌──────────┐          │              │        │   Layer       │  │
│  │ SEC      │────────→│              │        │               │  │
│  │ EDGAR    │          └──────────────┘        │  • Schema     │  │
│  └──────────┘                                  │  • Quality    │  │
│                                                │  • Anomaly    │  │
│  ┌──────────┐                                  └───────┬───────┘  │
│  │ News     │────────→ (same pattern)                  │          │
│  │ APIs     │                                          ▼          │
│  └──────────┘                                  ┌───────────────┐  │
│                                                │   Storage     │  │
│                                                │   Layer       │  │
│                                                │               │  │
│                                                │  • Database   │  │
│                                                │  • Cache      │  │
│                                                │  • Audit Log  │  │
│                                                └───────┬───────┘  │
│                                                        │          │
│                                                        ▼          │
│                                                ┌───────────────┐  │
│                                                │   Delivery    │  │
│                                                │   Layer       │  │
│                                                │               │  │
│                                                │  Consumers:   │  │
│                                                │  • Research   │  │
│                                                │  • Quant      │  │
│                                                │  • Portfolio   │  │
│                                                │  • Risk       │  │
│                                                └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 1.2 Pipeline Layer Responsibilities

| Layer | Responsibility | Located In |
|-------|----------------|------------|
| **Provider Adapter** | Authentication, rate limiting, retry, raw API call, translation to canonical format | `src/data_engine/providers/` |
| **Canonical Transform** | Normalize raw data into standard internal models (cents, UTC, enums) | `src/data_engine/ingestion/` |
| **Validation** | Schema validation, data quality checks, anomaly detection | `src/data_engine/validation/` |
| **Storage** | Persist validated data to database and cache | `src/data_engine/storage/` |
| **Delivery** | Serve data to consuming domains via typed service interfaces | `src/data_engine/` (public API) |

## 1.3 Layer Rules

| Rule | Description |
|------|-------------|
| **PL-001** | Data flows in one direction: External → Adapter → Transform → Validate → Store → Deliver |
| **PL-002** | No layer may be skipped. Every data point passes through every layer. |
| **PL-003** | Provider-specific code exists ONLY in the adapter layer |
| **PL-004** | Canonical models exist ONLY in the transform and downstream layers |
| **PL-005** | Validation never modifies data — it accepts or rejects |
| **PL-006** | Storage is the system of record. Cache is ephemeral. |
| **PL-007** | Delivery layer returns only validated, canonical data — never raw or unvalidated |

---

# 2. PROVIDER ADAPTER STANDARDS

## 2.1 Provider Registry

```python
# src/data_engine/providers/registry.py

"""Provider registry — central catalog of all external data sources.

Every external data source used by the system is registered here.
The registry enables:
- Provider discovery by data type
- Health monitoring across all providers
- Centralized configuration
- Provider swapping without consumer changes
"""

from enum import Enum
from pydantic import BaseModel


class DataCategory(str, Enum):
    """Categories of data that providers can supply."""

    MARKET_DATA_DAILY = "market_data_daily"           # OHLCV daily bars
    MARKET_DATA_INTRADAY = "market_data_intraday"     # Intraday bars (future)
    MARKET_DATA_QUOTE = "market_data_quote"           # Real-time quotes
    FUNDAMENTAL_INCOME = "fundamental_income"          # Income statements
    FUNDAMENTAL_BALANCE = "fundamental_balance"        # Balance sheets
    FUNDAMENTAL_CASHFLOW = "fundamental_cashflow"      # Cash flow statements
    FUNDAMENTAL_RATIOS = "fundamental_ratios"          # Pre-computed ratios
    EARNINGS = "earnings"                              # Earnings dates/results
    NEWS = "news"                                      # News articles
    SENTIMENT = "sentiment"                            # Sentiment scores
    SEC_FILINGS = "sec_filings"                        # SEC EDGAR filings
    INSIDER_TRANSACTIONS = "insider_transactions"      # Form 4 / insider trades
    COMPANY_PROFILE = "company_profile"                # Company overview
    INDEX_CONSTITUENTS = "index_constituents"          # Index membership


class ProviderTier(str, Enum):
    """Provider priority tier."""

    PRIMARY = "primary"
    FALLBACK = "fallback"
    EMERGENCY = "emergency"


class ProviderRegistration(BaseModel):
    """Registration entry for a data provider."""

    provider_name: str
    categories: list[DataCategory]
    tier: ProviderTier
    rate_limit_per_minute: int
    rate_limit_per_day: int | None = None
    is_free_tier: bool = True
    max_history_years: int | None = None
    supports_adjusted_prices: bool = True
    notes: str = ""


# ── Provider catalog ──
PROVIDER_REGISTRY: list[ProviderRegistration] = [
    ProviderRegistration(
        provider_name="polygon",
        categories=[
            DataCategory.MARKET_DATA_DAILY,
            DataCategory.MARKET_DATA_QUOTE,
            DataCategory.COMPANY_PROFILE,
        ],
        tier=ProviderTier.PRIMARY,
        rate_limit_per_minute=5,       # Free tier
        rate_limit_per_day=None,
        is_free_tier=True,
        max_history_years=2,           # Free tier limit
        supports_adjusted_prices=True,
        notes="Free tier: 5 req/min, 2 years history",
    ),
    ProviderRegistration(
        provider_name="alpha_vantage",
        categories=[
            DataCategory.MARKET_DATA_DAILY,
            DataCategory.FUNDAMENTAL_INCOME,
            DataCategory.FUNDAMENTAL_BALANCE,
            DataCategory.FUNDAMENTAL_CASHFLOW,
            DataCategory.EARNINGS,
            DataCategory.COMPANY_PROFILE,
        ],
        tier=ProviderTier.FALLBACK,
        rate_limit_per_minute=5,
        rate_limit_per_day=500,
        is_free_tier=True,
        max_history_years=20,
        supports_adjusted_prices=True,
        notes="Free tier: 5 req/min, 500 req/day",
    ),
    # Add more providers as they are integrated
]
```

## 2.2 Provider Adapter Interface

Every provider adapter implements a category-specific protocol:

```python
# src/data_engine/providers/interfaces.py

"""Provider interfaces — protocols for each data category.

Each data category has its own protocol. A provider adapter may
implement multiple protocols if it supports multiple categories.

All protocols follow the same contract:
- Accept simple, typed parameters
- Return Result[CanonicalModel, DataError]
- Handle authentication internally
- Handle rate limiting internally
- Log all API calls
"""

from typing import Protocol
from datetime import date
from src.shared.types import Result
from src.data_engine.models import (
    OHLCVBar,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    CompanyProfile,
    NewsArticle,
    EarningsReport,
    SECFiling,
)
from src.data_engine.errors import DataFetchError


class DailyMarketDataProvider(Protocol):
    """Provider of daily OHLCV market data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_daily_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        adjusted: bool = True,
    ) -> Result[list[OHLCVBar], DataFetchError]: ...

    async def health_check(self) -> bool: ...


class FundamentalDataProvider(Protocol):
    """Provider of financial statement data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_income_statements(
        self,
        ticker: str,
        period: str = "annual",     # "annual" | "quarterly"
        limit: int = 5,
    ) -> Result[list[IncomeStatement], DataFetchError]: ...

    async def fetch_balance_sheets(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5,
    ) -> Result[list[BalanceSheet], DataFetchError]: ...

    async def fetch_cash_flow_statements(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5,
    ) -> Result[list[CashFlowStatement], DataFetchError]: ...

    async def health_check(self) -> bool: ...


class NewsDataProvider(Protocol):
    """Provider of news articles and sentiment data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_news(
        self,
        ticker: str,
        from_date: date,
        to_date: date,
        limit: int = 50,
    ) -> Result[list[NewsArticle], DataFetchError]: ...

    async def health_check(self) -> bool: ...


class SECFilingProvider(Protocol):
    """Provider of SEC EDGAR filing data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_filings(
        self,
        ticker: str,
        filing_types: list[str],     # ["10-K", "10-Q", "8-K"]
        from_date: date,
        to_date: date,
        limit: int = 20,
    ) -> Result[list[SECFiling], DataFetchError]: ...

    async def health_check(self) -> bool: ...
```

## 2.3 Provider Adapter Implementation Pattern

```python
# src/data_engine/providers/polygon/daily_bars.py

"""Polygon.io adapter for daily OHLCV market data.

Implements the DailyMarketDataProvider protocol.
All Polygon-specific API details are encapsulated here.

Provider documentation: https://polygon.io/docs/stocks
Rate limits: Free tier = 5 requests/minute
"""

import structlog
from datetime import date, datetime, timezone
from src.shared.types import Result, Success, Failure
from src.shared.utils.money import dollars_to_cents
from src.data_engine.providers.interfaces import DailyMarketDataProvider
from src.data_engine.providers.base import BaseProviderAdapter
from src.data_engine.models import OHLCVBar
from src.data_engine.errors import (
    DataFetchError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)


logger = structlog.get_logger(__name__)


class PolygonDailyBarsAdapter(BaseProviderAdapter):
    """Polygon adapter for daily OHLCV bar data.

    Responsibilities:
    - Construct Polygon API requests
    - Handle Polygon-specific authentication (API key in params)
    - Translate Polygon response format to canonical OHLCVBar
    - Handle Polygon-specific quirks:
      * Timestamps in milliseconds
      * Pre/post market bars mixed in
      * Occasional null volume
      * Adjusted/unadjusted price variants
    """

    PROVIDER_NAME: str = "polygon"
    BASE_URL: str = "https://api.polygon.io"

    def __init__(
        self,
        api_key: str,
        http_client: "HttpClient",
        rate_limiter: "RateLimiter",
    ) -> None:
        super().__init__(
            provider_name=self.PROVIDER_NAME,
            http_client=http_client,
            rate_limiter=rate_limiter,
        )
        self._api_key = api_key

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

    async def fetch_daily_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        adjusted: bool = True,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch daily bars from Polygon and translate to canonical format.

        Polygon endpoint: /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}
        """
        log = self._logger.bind(
            ticker=ticker,
            start_date=str(start_date),
            end_date=str(end_date),
        )

        # ── Rate limit check ──
        await self._rate_limiter.acquire(self.PROVIDER_NAME)

        # ── Construct request ──
        url = (
            f"{self.BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/"
            f"{start_date.isoformat()}/{end_date.isoformat()}"
        )
        params = {
            "apiKey": self._api_key,
            "adjusted": str(adjusted).lower(),
            "sort": "asc",
            "limit": "50000",
        }

        # ── Execute with standard error handling ──
        result = await self._make_request(
            method="GET",
            url=url,
            params=params,
            log=log,
        )

        if result.is_failure:
            return result

        # ── Translate to canonical format ──
        raw_response = result.value
        bars = self._translate_bars(raw_response, ticker, adjusted)

        log.info(
            "Bars fetched successfully",
            bar_count=len(bars),
        )

        return Success(bars)

    def _translate_bars(
        self,
        raw: dict,
        ticker: str,
        adjusted: bool,
    ) -> list[OHLCVBar]:
        """Translate Polygon response to canonical OHLCVBar list.

        This is the ONLY place where Polygon field names appear.
        All downstream code works exclusively with OHLCVBar.

        Polygon fields:
        - t: timestamp (Unix ms)
        - o: open
        - h: high
        - l: low
        - c: close
        - v: volume
        - vw: volume-weighted average price
        - n: number of transactions
        """
        bars: list[OHLCVBar] = []
        now = datetime.now(timezone.utc)

        for result in raw.get("results", []):
            # Handle null volume (Polygon quirk for some pre-market data)
            volume = result.get("v")
            volume = int(volume) if volume is not None else 0
            volume_was_null = result.get("v") is None

            bar = OHLCVBar(
                ticker=ticker,
                date=self._ms_timestamp_to_date(result["t"]),
                open_cents=dollars_to_cents(result["o"]),
                high_cents=dollars_to_cents(result["h"]),
                low_cents=dollars_to_cents(result["l"]),
                close_cents=dollars_to_cents(result["c"]),
                volume=volume,
                is_adjusted=adjusted,
                source=self.PROVIDER_NAME,
                fetched_at=now,
                source_notes="volume_was_null" if volume_was_null else "",
            )
            bars.append(bar)

        return bars

    @staticmethod
    def _ms_timestamp_to_date(timestamp_ms: int) -> date:
        """Convert Polygon millisecond timestamp to date.

        Polygon returns timestamps in UTC milliseconds.
        We convert to a calendar date (market date).
        """
        return datetime.fromtimestamp(
            timestamp_ms / 1000, tz=timezone.utc
        ).date()
```

## 2.4 Base Provider Adapter

```python
# src/data_engine/providers/base.py

"""Base adapter class for all data provider adapters.

Provides common infrastructure:
- HTTP request execution with timeout
- Standard error handling and translation
- Structured logging
- Request/response metrics
"""

import structlog
import time
from src.shared.types import Result, Success, Failure
from src.data_engine.errors import (
    DataFetchError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)


logger = structlog.get_logger(__name__)


class BaseProviderAdapter:
    """Base class for all provider adapters.

    Provides common request execution, error handling, and logging.
    Subclasses implement provider-specific request construction
    and response translation.
    """

    def __init__(
        self,
        provider_name: str,
        http_client: "HttpClient",
        rate_limiter: "RateLimiter",
        timeout_seconds: int = 30,
        max_retries: int = 2,
    ) -> None:
        self._provider_name = provider_name
        self._http_client = http_client
        self._rate_limiter = rate_limiter
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._logger = logger.bind(provider=provider_name)

    async def _make_request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        log: structlog.BoundLogger | None = None,
    ) -> Result[dict, DataFetchError]:
        """Execute an HTTP request with retry logic and error handling.

        Handles:
        - Timeout with configurable duration
        - Rate limit responses (HTTP 429) with retry-after
        - Server errors (5xx) with exponential backoff retry
        - Client errors (4xx) as immediate failure
        - Connection errors with retry

        Args:
            method: HTTP method (GET, POST).
            url: Full URL (without API key — added by adapter).
            params: Query parameters.
            headers: Additional headers.
            log: Bound logger with request context.

        Returns:
            Success(dict) with parsed JSON response, or
            Failure(DataFetchError) with error details.
        """
        _log = log or self._logger
        last_error: DataFetchError | None = None

        for attempt in range(self._max_retries + 1):
            start_time = time.monotonic()

            try:
                response = await self._http_client.request(
                    method=method,
                    url=url,
                    params=self._sanitize_params_for_request(params),
                    headers=headers,
                    timeout_seconds=self._timeout_seconds,
                )

                elapsed_ms = int((time.monotonic() - start_time) * 1000)

                # ── Log the request (sanitized) ──
                _log.debug(
                    "API request completed",
                    method=method,
                    url=self._sanitize_url_for_logging(url),
                    status_code=response.status_code,
                    elapsed_ms=elapsed_ms,
                    attempt=attempt + 1,
                )

                # ── Handle response by status code ──
                if 200 <= response.status_code < 300:
                    return Success(response.json())

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    _log.warning(
                        "Rate limited",
                        retry_after_seconds=retry_after,
                        attempt=attempt + 1,
                    )
                    last_error = ProviderRateLimitError(
                        code=f"DATA.PROVIDER.{self._provider_name.upper()}.RATE_LIMITED",
                        message=f"Rate limited by {self._provider_name}",
                        provider=self._provider_name,
                        retry_after_seconds=retry_after,
                    )
                    if attempt < self._max_retries:
                        await self._backoff(attempt, min_seconds=retry_after)
                        continue
                    return Failure(last_error)

                if response.status_code >= 500:
                    _log.warning(
                        "Server error, retrying",
                        status_code=response.status_code,
                        attempt=attempt + 1,
                    )
                    last_error = DataFetchError(
                        code=f"DATA.PROVIDER.{self._provider_name.upper()}.SERVER_ERROR",
                        message=f"Server error {response.status_code}",
                        provider=self._provider_name,
                    )
                    if attempt < self._max_retries:
                        await self._backoff(attempt)
                        continue
                    return Failure(last_error)

                # 4xx (client error) — do not retry
                return Failure(DataFetchError(
                    code=f"DATA.PROVIDER.{self._provider_name.upper()}.CLIENT_ERROR",
                    message=f"Client error {response.status_code}: {response.text[:200]}",
                    provider=self._provider_name,
                ))

            except TimeoutError:
                elapsed_ms = int((time.monotonic() - start_time) * 1000)
                _log.warning(
                    "Request timed out",
                    timeout_seconds=self._timeout_seconds,
                    elapsed_ms=elapsed_ms,
                    attempt=attempt + 1,
                )
                last_error = ProviderTimeoutError(
                    code=f"DATA.PROVIDER.{self._provider_name.upper()}.TIMEOUT",
                    message=f"Request timed out after {self._timeout_seconds}s",
                    provider=self._provider_name,
                )
                if attempt < self._max_retries:
                    await self._backoff(attempt)
                    continue

            except ConnectionError as exc:
                _log.warning(
                    "Connection error",
                    error=str(exc),
                    attempt=attempt + 1,
                )
                last_error = DataFetchError(
                    code=f"DATA.PROVIDER.{self._provider_name.upper()}.CONNECTION_ERROR",
                    message=f"Connection failed: {exc}",
                    provider=self._provider_name,
                )
                if attempt < self._max_retries:
                    await self._backoff(attempt)
                    continue

        return Failure(last_error or DataFetchError(
            code=f"DATA.PROVIDER.{self._provider_name.upper()}.UNKNOWN",
            message="Request failed after all retries",
            provider=self._provider_name,
        ))

    async def _backoff(
        self,
        attempt: int,
        min_seconds: int = 1,
    ) -> None:
        """Exponential backoff between retry attempts.

        Formula: wait = max(min_seconds, 2^attempt) seconds
        With jitter: ±20% randomization to avoid thundering herd.
        """
        import asyncio
        import random

        base_wait = max(min_seconds, 2 ** attempt)
        jitter = base_wait * 0.2 * (2 * random.random() - 1)
        wait = base_wait + jitter
        await asyncio.sleep(wait)

    def _sanitize_url_for_logging(self, url: str) -> str:
        """Remove API keys from URLs before logging."""
        import re
        return re.sub(r"apiKey=[^&]+", "apiKey=***", url)

    def _sanitize_params_for_request(
        self,
        params: dict | None,
    ) -> dict | None:
        """Ensure params are properly formatted for the HTTP client."""
        return params

    async def health_check(self) -> bool:
        """Check if the provider is reachable.

        Subclasses may override with a provider-specific
        lightweight endpoint.
        """
        try:
            # Default: ping a known lightweight endpoint
            result = await self._make_request(
                method="GET",
                url=self._get_health_check_url(),
                params=self._get_health_check_params(),
            )
            return result.is_success
        except Exception:
            return False

    def _get_health_check_url(self) -> str:
        """Override in subclass to provide a lightweight health check URL."""
        raise NotImplementedError

    def _get_health_check_params(self) -> dict:
        """Override in subclass to provide health check parameters."""
        return {}
```

## 2.5 Provider Adapter Rules

| Rule | Description |
|------|-------------|
| **PA-001** | One adapter file per provider per data category |
| **PA-002** | All adapters inherit from `BaseProviderAdapter` |
| **PA-003** | Provider-specific field names appear ONLY in the `_translate_*` methods |
| **PA-004** | Adapters translate dollars to cents using `dollars_to_cents()` at the boundary |
| **PA-005** | Adapters handle their own rate limiting via the injected `RateLimiter` |
| **PA-006** | Adapters log every API call at DEBUG level (sanitized: no API keys) |
| **PA-007** | Adapters return `Result` types, never raise exceptions for API failures |
| **PA-008** | Adding a new provider = new adapter files + registry entry, zero downstream changes |
| **PA-009** | Adapters document provider-specific quirks inline where they are handled |
| **PA-010** | Adapters never cache — caching is a separate layer's responsibility |

---

# 3. RATE LIMITING

## 3.1 Rate Limiter Design

```python
# src/infrastructure/rate_limiter.py

"""Rate limiter for external API calls.

Implements token bucket algorithm with per-provider limits.
Ensures the system stays within API rate limits while maximizing
throughput.

Rate limits are configured from the provider registry and include
a configurable safety buffer (default 20%) to stay well under
the provider's actual limits.
"""

import asyncio
import time
import structlog
from pydantic import BaseModel


logger = structlog.get_logger(__name__)


class RateLimitConfig(BaseModel):
    """Rate limit configuration for a single provider."""

    provider_name: str
    requests_per_minute: int
    requests_per_day: int | None = None
    buffer_pct: float = 20.0            # Stay 20% under the limit


class RateLimiter:
    """Token bucket rate limiter with per-provider tracking.

    Features:
    - Per-provider independent rate limiting
    - Configurable safety buffer below actual limits
    - Async-safe (uses asyncio.Lock)
    - Daily limit tracking with automatic reset
    - Logging of rate limit approaching / exceeded
    """

    def __init__(self, configs: list[RateLimitConfig]) -> None:
        self._configs = {c.provider_name: c for c in configs}
        self._buckets: dict[str, "_TokenBucket"] = {}
        self._daily_counts: dict[str, int] = {}
        self._daily_reset_date: str = ""
        self._lock = asyncio.Lock()
        self._logger = logger.bind(component="RateLimiter")

        for config in configs:
            effective_rpm = int(
                config.requests_per_minute * (1 - config.buffer_pct / 100)
            )
            self._buckets[config.provider_name] = _TokenBucket(
                max_tokens=effective_rpm,
                refill_rate=effective_rpm / 60.0,    # tokens per second
            )

    async def acquire(self, provider_name: str) -> None:
        """Acquire permission to make a request to the given provider.

        Blocks (async wait) until a request token is available.
        Raises if daily limit would be exceeded.

        Args:
            provider_name: Provider to rate limit.

        Raises:
            RateLimitExceededError: If daily limit is exhausted.
        """
        async with self._lock:
            self._maybe_reset_daily()

            config = self._configs.get(provider_name)
            if config is None:
                self._logger.warning(
                    "No rate limit config for provider",
                    provider=provider_name,
                )
                return

            # Check daily limit
            if config.requests_per_day is not None:
                daily_count = self._daily_counts.get(provider_name, 0)
                effective_daily = int(
                    config.requests_per_day * (1 - config.buffer_pct / 100)
                )
                if daily_count >= effective_daily:
                    self._logger.error(
                        "Daily rate limit exceeded",
                        provider=provider_name,
                        daily_count=daily_count,
                        daily_limit=effective_daily,
                    )
                    raise RateLimitExceededError(
                        f"Daily limit for {provider_name} exceeded: "
                        f"{daily_count}/{effective_daily}"
                    )

            # Acquire per-minute token
            bucket = self._buckets[provider_name]

        # Wait outside the lock (allows other providers to proceed)
        await bucket.acquire()

        # Track daily usage
        async with self._lock:
            self._daily_counts[provider_name] = (
                self._daily_counts.get(provider_name, 0) + 1
            )

    def get_usage_stats(self, provider_name: str) -> dict:
        """Get current usage statistics for a provider."""
        config = self._configs.get(provider_name)
        daily_count = self._daily_counts.get(provider_name, 0)
        return {
            "provider": provider_name,
            "daily_requests_used": daily_count,
            "daily_limit": config.requests_per_day if config else None,
            "daily_pct_used": (
                daily_count / config.requests_per_day * 100
                if config and config.requests_per_day
                else 0
            ),
        }

    def _maybe_reset_daily(self) -> None:
        """Reset daily counters if the date has changed."""
        from datetime import date
        today = str(date.today())
        if today != self._daily_reset_date:
            self._daily_counts.clear()
            self._daily_reset_date = today
            self._logger.info("Daily rate limit counters reset")
```

## 3.2 Rate Limiting Rules

| Rule | Description |
|------|-------------|
| **RL-001** | Every external API call must go through the `RateLimiter` |
| **RL-002** | Safety buffer of 20% applied to all provider limits (configurable) |
| **RL-003** | Rate limiter blocks (async wait), never fails silently |
| **RL-004** | Daily limits tracked and enforced when providers have them |
| **RL-005** | Rate limit approaching (>80% daily usage) triggers WARNING log |
| **RL-006** | Rate limit exceeded logs at ERROR level and halts requests to that provider |
| **RL-007** | Rate limiter statistics available for monitoring via `get_usage_stats()` |
| **RL-008** | Rate limits are per-provider, not global — hitting one provider's limit doesn't affect others |

---

# 4. PROVIDER FAILOVER

## 4.1 Failover Strategy

```python
# src/data_engine/providers/failover.py

"""Provider failover manager.

Manages primary/fallback provider selection for each data category.
Automatically switches to fallback providers when the primary is
unhealthy or rate-limited.
"""

import structlog
from src.shared.types import Result, Success, Failure
from src.data_engine.errors import DataFetchError


logger = structlog.get_logger(__name__)


class ProviderFailoverManager:
    """Manages failover between primary and fallback providers.

    For each data category, maintains an ordered list of providers
    (primary first, then fallbacks). If a provider fails, the next
    provider is tried. Provider health is tracked to avoid repeatedly
    calling known-unhealthy providers.

    Failover chain example:
        MARKET_DATA_DAILY: FMP → SED EDGAR → (error)

    Health recovery:
        Unhealthy providers are re-checked every `recovery_check_interval`
        minutes. If they pass a health check, they are restored to service.
    """

    def __init__(
        self,
        provider_chains: dict[str, list["DataProvider"]],
        recovery_check_interval_minutes: int = 15,
    ) -> None:
        self._chains = provider_chains
        self._health_status: dict[str, bool] = {}  # provider_name → healthy
        self._recovery_interval = recovery_check_interval_minutes
        self._logger = logger.bind(component="FailoverManager")

        # Initialize all as healthy
        for chain in provider_chains.values():
            for provider in chain:
                self._health_status[provider.provider_name] = True

    async def fetch(
        self,
        category: str,
        fetch_fn_name: str,
        **kwargs,
    ) -> Result:
        """Fetch data using the failover chain for the given category.

        Tries each provider in the chain until one succeeds.
        Skips known-unhealthy providers (unless all are unhealthy,
        in which case tries all).

        Args:
            category: Data category (e.g., "market_data_daily").
            fetch_fn_name: Method name to call on the provider.
            **kwargs: Arguments to pass to the fetch method.

        Returns:
            Success with data from the first successful provider, or
            Failure if all providers in the chain fail.
        """
        chain = self._chains.get(category, [])
        if not chain:
            return Failure(DataFetchError(
                code="DATA.FAILOVER.NO_PROVIDERS",
                message=f"No providers configured for category: {category}",
            ))

        # Separate healthy and unhealthy providers
        healthy = [p for p in chain if self._health_status.get(p.provider_name, True)]
        unhealthy = [p for p in chain if not self._health_status.get(p.provider_name, True)]

        # If all unhealthy, try all anyway (maybe they recovered)
        providers_to_try = healthy if healthy else chain

        last_error = None
        for provider in providers_to_try:
            fetch_method = getattr(provider, fetch_fn_name, None)
            if fetch_method is None:
                self._logger.warning(
                    "Provider does not support method",
                    provider=provider.provider_name,
                    method=fetch_fn_name,
                )
                continue

            result = await fetch_method(**kwargs)

            if result.is_success:
                # If this was a previously unhealthy provider, mark recovered
                if provider.provider_name in [p.provider_name for p in unhealthy]:
                    self._logger.info(
                        "Provider recovered",
                        provider=provider.provider_name,
                    )
                    self._health_status[provider.provider_name] = True
                return result

            # Mark as unhealthy
            self._health_status[provider.provider_name] = False
            last_error = result.error
            self._logger.warning(
                "Provider failed, trying next in chain",
                failed_provider=provider.provider_name,
                error_code=result.error.code,
                remaining_providers=len(providers_to_try) - providers_to_try.index(provider) - 1,
            )

        return Failure(DataFetchError(
            code="DATA.FAILOVER.ALL_FAILED",
            message=f"All providers failed for {category}",
            details={
                "category": category,
                "providers_attempted": [p.provider_name for p in providers_to_try],
                "last_error": str(last_error),
            },
        ))

    async def check_provider_health(self) -> dict[str, bool]:
        """Run health checks on all providers and update status."""
        results = {}
        for chain in self._chains.values():
            for provider in chain:
                if provider.provider_name not in results:
                    is_healthy = await provider.health_check()
                    results[provider.provider_name] = is_healthy
                    self._health_status[provider.provider_name] = is_healthy

                    if not is_healthy:
                        self._logger.warning(
                            "Provider health check failed",
                            provider=provider.provider_name,
                        )

        return results
```

## 4.2 Failover Rules

| Rule | Description |
|------|-------------|
| **FO-001** | Every data category must have at least one primary and one fallback provider |
| **FO-002** | Failover is automatic — consumers never know which provider served the data (they see only `source` field) |
| **FO-003** | Provider health tracked per-provider, not per-category |
| **FO-004** | Unhealthy providers are re-checked periodically (default: every 15 minutes) |
| **FO-005** | If all providers are unhealthy, try all anyway (may have recovered) |
| **FO-006** | Every failover event logged at WARNING level with provider names |
| **FO-007** | Consumer code must handle the case where all providers fail (Result type enforces this) |
| **FO-008** | Provider health check results available via monitoring endpoint |

---

# 5. DATA CANONICALIZATION

## 5.1 Canonical Model Standards

All data entering the system is transformed into canonical models at
the adapter boundary. Canonical models are the **single source of truth**
for data shape within the system.

```python
# src/data_engine/models/market_data.py

"""Canonical market data models.

These models define the internal representation of market data.
All provider adapters translate their responses into these models.
All consumers receive data in these formats.

No provider-specific field names, types, or conventions appear here.
"""

from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from enum import Enum


class OHLCVBar(BaseModel):
    """A single OHLCV price bar in canonical format.

    All prices are in integer cents (USD).
    All timestamps are UTC.
    All tickers are uppercase.
    """

    ticker: str = Field(
        ...,
        description="Uppercase ticker symbol",
        examples=["AAPL", "MSFT"],
    )
    date: date = Field(
        ...,
        description="Trading date (market date, not UTC date)",
    )
    open_cents: int = Field(
        ...,
        ge=0,
        description="Opening price in USD cents",
    )
    high_cents: int = Field(
        ...,
        ge=0,
        description="Highest price in USD cents",
    )
    low_cents: int = Field(
        ...,
        ge=0,
        description="Lowest price in USD cents",
    )
    close_cents: int = Field(
        ...,
        ge=0,
        description="Closing price in USD cents",
    )
    volume: int = Field(
        ...,
        ge=0,
        description="Trading volume in shares",
    )
    is_adjusted: bool = Field(
        default=True,
        description="Whether prices are adjusted for splits/dividends",
    )
    source: str = Field(
        ...,
        description="Provider that supplied this data",
    )
    fetched_at: datetime = Field(
        ...,
        description="When this data was fetched (UTC)",
    )
    source_notes: str = Field(
        default="",
        description="Provider-specific notes (e.g., 'volume_was_null')",
    )

    @model_validator(mode="after")
    def validate_price_consistency(self) -> "OHLCVBar":
        """Ensure OHLCV price relationships are valid."""
        if self.high_cents < self.low_cents:
            raise ValueError(
                f"High ({self.high_cents}) must be >= Low ({self.low_cents})"
            )
        if self.open_cents > self.high_cents:
            raise ValueError(
                f"Open ({self.open_cents}) cannot exceed High ({self.high_cents})"
            )
        if self.open_cents < self.low_cents:
            raise ValueError(
                f"Open ({self.open_cents}) cannot be below Low ({self.low_cents})"
            )
        if self.close_cents > self.high_cents:
            raise ValueError(
                f"Close ({self.close_cents}) cannot exceed High ({self.high_cents})"
            )
        if self.close_cents < self.low_cents:
            raise ValueError(
                f"Close ({self.close_cents}) cannot be below Low ({self.low_cents})"
            )
        return self

    class Config:
        frozen = True


class IncomeStatement(BaseModel):
    """Canonical income statement representation.

    All monetary values in integer cents (USD).
    Covers annual or quarterly periods.
    """

    ticker: str
    period_end_date: date
    period_type: str = Field(
        ...,
        description="'annual' or 'quarterly'",
    )
    fiscal_year: int
    fiscal_quarter: int | None = None   # None for annual

    # Revenue
    revenue_cents: int
    cost_of_revenue_cents: int
    gross_profit_cents: int

    # Operating
    research_development_cents: int | None = None
    selling_general_admin_cents: int | None = None
    operating_expenses_cents: int
    operating_income_cents: int

    # Below the line
    interest_expense_cents: int | None = None
    income_before_tax_cents: int
    income_tax_expense_cents: int
    net_income_cents: int

    # Per share
    eps_basic_cents: int | None = None
    eps_diluted_cents: int | None = None
    shares_outstanding: int | None = None
    shares_diluted: int | None = None

    # Supplemental
    ebitda_cents: int | None = None
    depreciation_amortization_cents: int | None = None

    # Provenance
    source: str
    fetched_at: datetime
    filing_date: date | None = None     # Date the filing was made

    class Config:
        frozen = True


class BalanceSheet(BaseModel):
    """Canonical balance sheet representation."""

    ticker: str
    period_end_date: date
    period_type: str
    fiscal_year: int
    fiscal_quarter: int | None = None

    # Assets
    cash_and_equivalents_cents: int
    short_term_investments_cents: int | None = None
    total_current_assets_cents: int
    total_non_current_assets_cents: int
    total_assets_cents: int

    # Liabilities
    total_current_liabilities_cents: int
    long_term_debt_cents: int | None = None
    total_non_current_liabilities_cents: int
    total_liabilities_cents: int

    # Equity
    total_shareholders_equity_cents: int
    retained_earnings_cents: int | None = None

    # Derived
    total_debt_cents: int | None = None  # Short + long term

    # Provenance
    source: str
    fetched_at: datetime

    @model_validator(mode="after")
    def validate_balance_sheet_identity(self) -> "BalanceSheet":
        """Verify A = L + E within rounding tolerance ($1.00 = 100 cents)."""
        expected = self.total_liabilities_cents + self.total_shareholders_equity_cents
        diff = abs(self.total_assets_cents - expected)
        if diff > 100:    # $1.00 tolerance
            raise ValueError(
                f"Balance sheet does not balance: "
                f"Assets ({self.total_assets_cents}) != "
                f"Liabilities ({self.total_liabilities_cents}) + "
                f"Equity ({self.total_shareholders_equity_cents}). "
                f"Difference: {diff} cents"
            )
        return self

    class Config:
        frozen = True
```

## 5.2 Canonicalization Rules

| Rule | Description |
|------|-------------|
| **CN-001** | All monetary values converted to integer cents at the adapter boundary |
| **CN-002** | All timestamps converted to UTC at the adapter boundary |
| **CN-003** | All ticker symbols normalized to uppercase at the adapter boundary |
| **CN-004** | Canonical models are frozen (immutable after creation) |
| **CN-005** | Canonical models include Pydantic validators for cross-field consistency |
| **CN-006** | Every canonical model includes `source` and `fetched_at` provenance fields |
| **CN-007** | Optional fields use `None`, never zero or empty string as sentinel values |
| **CN-008** | Canonical models document units in field descriptions (`USD cents`, `shares`, etc.) |
| **CN-009** | Provider-specific notes preserved in `source_notes` field for debugging |
| **CN-010** | Canonical models are defined in `src/data_engine/models/`, not in provider adapters |

---

# 6. DATA VALIDATION

## 6.1 Validation Layer Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                 VALIDATION PIPELINE                      │
│                                                          │
│  Raw canonical     ┌─────────────────────┐              │
│  models from  ───→ │ Schema Validation   │              │
│  adapter           │ (Pydantic built-in) │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Quality Rules       │              │
│                    │ (domain-specific)   │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Anomaly Detection   │              │
│                    │ (statistical)       │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Freshness Check     │              │
│                    │ (staleness)         │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Accept / Flag /     │              │
│                    │ Reject              │              │
│                    └─────────────────────┘              │
│                                                          │
│  Outcomes:                                               │
│    ACCEPT:  Store as normal                              │
│    FLAG:    Store with quality_warning field set          │
│    REJECT:  Do not store. Log. Alert if critical.       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 6.2 Data Quality Rules

```python
# src/data_engine/validation/quality_rules.py

"""Data quality validation rules.

Each rule checks one aspect of data quality. Rules are
composable — the validation pipeline runs all applicable
rules for each data type.

Rules return:
- None if the check passes
- QualityIssue if a problem is detected
"""

import structlog
from datetime import date, timedelta
from pydantic import BaseModel


logger = structlog.get_logger(__name__)


class QualityIssue(BaseModel):
    """A detected data quality issue."""

    rule_id: str
    severity: str               # "REJECT" | "FLAG" | "INFO"
    field: str
    message: str
    actual_value: str = ""
    expected_range: str = ""


# ── OHLCV Quality Rules ──

class OHLCVQualityValidator:
    """Quality validation rules for OHLCV bar data.

    Reference: specs/guardrails/data-quality-guardrails.md
    """

    # Configurable thresholds
    MAX_DAILY_PRICE_CHANGE_PCT: float = 0.50    # 50% single-day move
    MIN_REASONABLE_PRICE_CENTS: int = 1          # $0.01
    MAX_REASONABLE_PRICE_CENTS: int = 100_000_00  # $100,000.00
    MIN_REASONABLE_VOLUME: int = 0
    VOLUME_SPIKE_MULTIPLIER: float = 50.0        # 50x average

    def validate_bar(
        self,
        bar: "OHLCVBar",
        prior_bar: "OHLCVBar | None" = None,
        avg_volume: int | None = None,
    ) -> list[QualityIssue]:
        """Run all quality checks on a single OHLCV bar.

        Args:
            bar: The bar to validate.
            prior_bar: Previous trading day's bar (for change checks).
            avg_volume: Average volume for comparison (e.g., 20-day average).

        Returns:
            List of quality issues found. Empty list means all checks pass.
        """
        issues: list[QualityIssue] = []

        # ── Rule DQ-001: Price sanity range ──
        for field_name in ["open_cents", "high_cents", "low_cents", "close_cents"]:
            price = getattr(bar, field_name)
            if price < self.MIN_REASONABLE_PRICE_CENTS:
                issues.append(QualityIssue(
                    rule_id="DQ-PRICE-TOO-LOW",
                    severity="FLAG",
                    field=field_name,
                    message=f"Price unusually low: {price} cents",
                    actual_value=str(price),
                    expected_range=f">= {self.MIN_REASONABLE_PRICE_CENTS}",
                ))
            if price > self.MAX_REASONABLE_PRICE_CENTS:
                issues.append(QualityIssue(
                    rule_id="DQ-PRICE-TOO-HIGH",
                    severity="FLAG",
                    field=field_name,
                    message=f"Price unusually high: {price} cents",
                    actual_value=str(price),
                    expected_range=f"<= {self.MAX_REASONABLE_PRICE_CENTS}",
                ))

        # ── Rule DQ-002: Extreme daily price change ──
        if prior_bar is not None and prior_bar.close_cents > 0:
            daily_change = abs(
                (bar.close_cents - prior_bar.close_cents) / prior_bar.close_cents
            )
            if daily_change > self.MAX_DAILY_PRICE_CHANGE_PCT:
                issues.append(QualityIssue(
                    rule_id="DQ-EXTREME-MOVE",
                    severity="FLAG",
                    field="close_cents",
                    message=(
                        f"Extreme daily move: {daily_change:.1%} "
                        f"(prior close: {prior_bar.close_cents}, "
                        f"current close: {bar.close_cents})"
                    ),
                    actual_value=f"{daily_change:.4f}",
                    expected_range=f"<= {self.MAX_DAILY_PRICE_CHANGE_PCT:.0%}",
                ))

        # ── Rule DQ-003: Zero volume on trading day ──
        if bar.volume == 0:
            issues.append(QualityIssue(
                rule_id="DQ-ZERO-VOLUME",
                severity="FLAG",
                field="volume",
                message="Zero volume on trading day — possible data issue",
                actual_value="0",
                expected_range="> 0",
            ))

        # ── Rule DQ-004: Volume spike ──
        if avg_volume is not None and avg_volume > 0:
            volume_ratio = bar.volume / avg_volume
            if volume_ratio > self.VOLUME_SPIKE_MULTIPLIER:
                issues.append(QualityIssue(
                    rule_id="DQ-VOLUME-SPIKE",
                    severity="INFO",
                    field="volume",
                    message=(
                        f"Volume spike: {volume_ratio:.1f}x average "
                        f"(volume: {bar.volume}, avg: {avg_volume})"
                    ),
                    actual_value=str(bar.volume),
                    expected_range=f"<= {avg_volume * self.VOLUME_SPIKE_MULTIPLIER:.0f}",
                ))

        # ── Rule DQ-005: Weekend/holiday date ──
        if bar.date.weekday() >= 5:   # Saturday = 5, Sunday = 6
            issues.append(QualityIssue(
                rule_id="DQ-WEEKEND-DATE",
                severity="REJECT",
                field="date",
                message=f"Bar has weekend date: {bar.date} ({bar.date.strftime('%A')})",
                actual_value=str(bar.date),
                expected_range="Monday-Friday",
            ))

        return issues


# ── Financial Statement Quality Rules ──

class FinancialStatementQualityValidator:
    """Quality validation for financial statement data."""

    def validate_income_statement(
        self,
        statement: "IncomeStatement",
    ) -> list[QualityIssue]:
        """Validate income statement internal consistency."""
        issues: list[QualityIssue] = []

        # ── Gross profit = Revenue - COGS ──
        expected_gross = statement.revenue_cents - statement.cost_of_revenue_cents
        if abs(statement.gross_profit_cents - expected_gross) > 100:
            issues.append(QualityIssue(
                rule_id="DQ-IS-GROSS-MISMATCH",
                severity="FLAG",
                field="gross_profit_cents",
                message=(
                    f"Gross profit ({statement.gross_profit_cents}) != "
                    f"Revenue ({statement.revenue_cents}) - "
                    f"COGS ({statement.cost_of_revenue_cents}) = {expected_gross}"
                ),
                actual_value=str(statement.gross_profit_cents),
                expected_range=str(expected_gross),
            ))

        # ── Revenue must be positive (for our equity universe) ──
        if statement.revenue_cents <= 0:
            issues.append(QualityIssue(
                rule_id="DQ-IS-NEGATIVE-REVENUE",
                severity="FLAG",
                field="revenue_cents",
                message=f"Non-positive revenue: {statement.revenue_cents}",
                actual_value=str(statement.revenue_cents),
                expected_range="> 0",
            ))

        return issues
```

## 6.3 Validation Outcome Handling

```python
# src/data_engine/validation/validator.py

"""Data validation orchestrator.

Runs all applicable quality rules and determines the final
outcome: ACCEPT, FLAG, or REJECT.
"""

import structlog
from src.data_engine.validation.quality_rules import QualityIssue

logger = structlog.get_logger(__name__)


class ValidationOutcome:
    """The result of running validation on a data point."""

    ACCEPT = "ACCEPT"       # Clean data, store normally
    FLAG = "FLAG"           # Store with quality warnings attached
    REJECT = "REJECT"       # Do not store, log the issue

    def __init__(
        self,
        outcome: str,
        issues: list[QualityIssue],
    ) -> None:
        self.outcome = outcome
        self.issues = issues
        self.reject_reasons = [i for i in issues if i.severity == "REJECT"]
        self.flags = [i for i in issues if i.severity == "FLAG"]
        self.info = [i for i in issues if i.severity == "INFO"]

    @property
    def is_accepted(self) -> bool:
        return self.outcome in (self.ACCEPT, self.FLAG)

    @property
    def is_rejected(self) -> bool:
        return self.outcome == self.REJECT


def determine_outcome(issues: list[QualityIssue]) -> ValidationOutcome:
    """Determine validation outcome from a list of quality issues.

    Logic:
    - Any REJECT issue → REJECT the data point
    - Any FLAG issue (no REJECT) → FLAG (store with warnings)
    - Only INFO issues or none → ACCEPT
    """
    if any(i.severity == "REJECT" for i in issues):
        return ValidationOutcome(ValidationOutcome.REJECT, issues)
    elif any(i.severity == "FLAG" for i in issues):
        return ValidationOutcome(ValidationOutcome.FLAG, issues)
    else:
        return ValidationOutcome(ValidationOutcome.ACCEPT, issues)
```

## 6.4 Validation Rules

| Rule | Description |
|------|-------------|
| **DV-001** | Every data point passes through the validation pipeline before storage |
| **DV-002** | Validation NEVER modifies data — it only classifies (ACCEPT / FLAG / REJECT) |
| **DV-003** | REJECT means the data is not stored. The rejection is logged with details. |
| **DV-004** | FLAG means the data is stored with `quality_warnings` metadata attached |
| **DV-005** | Quality issues include: rule_id, severity, field, message, actual vs expected |
| **DV-006** | Validation rules are configurable via thresholds (not hardcoded magic numbers) |
| **DV-007** | New validation rules can be added without modifying existing rules (composable) |
| **DV-008** | Validation outcome counts logged per ingestion run (N accepted, N flagged, N rejected) |
| **DV-009** | Flagged data points do NOT reduce confidence score — they inform it |
| **DV-010** | Rejected data points trigger re-fetch from fallback provider if available |

---

# 7. DATA STORAGE STANDARDS

## 7.1 Storage Layer Design

```python
# src/data_engine/storage/interfaces.py

"""Storage interfaces for the data engine.

Each data category has a repository interface. Implementations
may use different storage backends (PostgreSQL, TimescaleDB,
file system) but must conform to these interfaces.
"""

from typing import Protocol
from datetime import date


class MarketDataRepository(Protocol):
    """Interface for OHLCV bar storage and retrieval."""

    async def store_bars(
        self,
        bars: list["OHLCVBar"],
    ) -> int:
        """Store bars using upsert semantics (insert or update).

        Returns the count of bars stored.
        """
        ...

    async def get_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list["OHLCVBar"]:
        """Get bars for a ticker within a date range.

        Returns bars in ascending chronological order.
        Returns empty list if none found.
        """
        ...

    async def get_latest_bar(
        self,
        ticker: str,
    ) -> "OHLCVBar | None":
        """Get the most recent bar for a ticker."""
        ...

    async def get_latest_date(
        self,
        ticker: str,
    ) -> date | None:
        """Get the date of the most recent bar for freshness checking."""
        ...

    async def get_tickers_with_data(self) -> list[str]:
        """Get all tickers that have stored data."""
        ...

    async def get_bar_count(
        self,
        ticker: str,
    ) -> int:
        """Count stored bars for a ticker."""
        ...
```

## 7.2 Upsert Semantics

```python
# ── All data storage uses UPSERT (insert or update) ──
# This ensures idempotency: running the same ingestion twice
# produces the same result without duplication.

"""
Upsert strategy:

  OHLCV Bars:
    Unique key: (ticker, date)
    On conflict: UPDATE all fields except ticker and date
    Rationale: Re-ingesting should update with latest data from provider

  Financial Statements:
    Unique key: (ticker, period_end_date, period_type)
    On conflict: UPDATE if fetched_at is newer than existing
    Rationale: Later fetches may have restated/corrected values

  News Articles:
    Unique key: (source, external_id)
    On conflict: SKIP (don't update, news content doesn't change)
    Rationale: Published news is immutable

  SEC Filings:
    Unique key: (accession_number)
    On conflict: UPDATE parsed fields (re-parsing may improve)
    Rationale: Our parsing may improve over time

SQL pattern:
  INSERT INTO ohlcv_bars (ticker, date, open_cents, ...)
  VALUES ($1, $2, $3, ...)
  ON CONFLICT (ticker, date) DO UPDATE SET
    open_cents = EXCLUDED.open_cents,
    high_cents = EXCLUDED.high_cents,
    ...
    fetched_at = EXCLUDED.fetched_at
  WHERE ohlcv_bars.fetched_at < EXCLUDED.fetched_at;
"""
```

## 7.3 Storage Rules

| Rule | Description |
|------|-------------|
| **ST-001** | All data storage uses UPSERT semantics — no duplicate data from re-ingestion |
| **ST-002** | Unique keys defined per data type and enforced at the database level |
| **ST-003** | Historical data is immutable once validated (INV-005) — updates only via re-ingestion |
| **ST-004** | Storage repositories return canonical domain models, never raw database rows |
| **ST-005** | Empty results returned as empty lists, never `None` |
| **ST-006** | Queries always return data in chronological order (ascending date) |
| **ST-007** | Write operations return a count of affected rows |
| **ST-008** | All storage operations use parameterized queries (no SQL injection) |
| **ST-009** | Database connection pooling managed at the infrastructure level |
| **ST-010** | Storage errors return `Result` types, not exceptions |

---

# 8. CACHING STRATEGY

## 8.1 Cache Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                    CACHING STRATEGY                               │
│                                                                   │
│  ┌──────────┐   miss   ┌──────────┐   miss   ┌──────────────┐  │
│  │  Request │ ────────→ │  Cache   │ ────────→│  Database    │  │
│  │          │           │  Layer   │           │  (Storage)   │  │
│  │          │ ←──────── │          │ ←──────── │              │  │
│  │          │   hit     │          │   result  │              │  │
│  └──────────┘           └──────────┘           └──────────────┘  │
│                              │                                    │
│                      On miss: cache the                           │
│                      result with TTL                              │
│                                                                   │
│  Cache is NEVER the system of record.                            │
│  Cache can be cleared at any time without data loss.             │
│  Cache improves latency and reduces DB load.                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## 8.2 Cache TTL Policy

```python
# src/infrastructure/cache/config.py

"""Cache TTL configuration.

TTL values are calibrated to the update frequency of each data type.
Stale cache is acceptable because the database holds the source of
truth — cache is a performance optimization.

TTLs are conservative — better to re-fetch than serve stale data
for analytical purposes.
"""

from pydantic import BaseModel


class CacheTTLConfig(BaseModel):
    """Cache time-to-live settings by data type."""

    # ── Market Data ──
    daily_bars_ttl_seconds: int = 300            # 5 min — prices change frequently
    latest_quote_ttl_seconds: int = 60           # 1 min — near-real-time
    price_history_ttl_seconds: int = 3600        # 1 hr — historical doesn't change often

    # ── Fundamental Data ──
    income_statement_ttl_seconds: int = 86400    # 24 hrs — changes quarterly
    balance_sheet_ttl_seconds: int = 86400       # 24 hrs
    cash_flow_ttl_seconds: int = 86400           # 24 hrs
    company_profile_ttl_seconds: int = 86400     # 24 hrs — rarely changes

    # ── Computed Data ──
    technical_indicators_ttl_seconds: int = 300  # 5 min — depends on latest price
    financial_ratios_ttl_seconds: int = 3600     # 1 hr
    scoring_results_ttl_seconds: int = 3600      # 1 hr

    # ── Reference Data ──
    watchlist_ttl_seconds: int = 60              # 1 min — user may update frequently
    index_constituents_ttl_seconds: int = 86400  # 24 hrs

    # ── Never Cache ──
    # Agent outputs: NEVER cached (each analysis must be fresh)
    # Portfolio state: NEVER cached (must reflect real-time holdings)
    # Risk metrics: NEVER cached (must use latest data)
```

## 8.3 Cache Key Convention

```python
# ── Cache keys follow a consistent namespace convention ──

# Pattern: {domain}:{data_type}:{identifier}:{qualifier}

# Examples:
"market:daily_bars:AAPL:2025-01-15:2025-01-15"
"market:latest_quote:AAPL"
"market:price_history:MSFT:2024-01-01:2025-01-15"
"fundamental:income:AAPL:annual:5"
"fundamental:balance:AAPL:quarterly:4"
"quant:indicators:AAPL:sma:20"
"quant:scoring:AAPL:multi_factor"
"reference:watchlist:default"
"reference:index:SPY:constituents"


def build_cache_key(*parts: str) -> str:
    """Build a cache key from parts.

    Args:
        *parts: Key components to join with ':'.

    Returns:
        Cache key string.

    Example:
        >>> build_cache_key("market", "daily_bars", "AAPL", "2025-01-15")
        'market:daily_bars:AAPL:2025-01-15'
    """
    return ":".join(str(p) for p in parts)
```

## 8.4 Cache Service Interface

```python
# src/infrastructure/cache/interfaces.py

from typing import Protocol, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class CacheService(Protocol):
    """Interface for cache operations.

    Implementations may use Redis, in-memory dict, or file-based cache.
    All implementations must be async-safe.
    """

    async def get(self, key: str) -> str | None:
        """Get a value from cache. Returns None on miss."""
        ...

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int,
    ) -> None:
        """Set a value in cache with TTL."""
        ...

    async def delete(self, key: str) -> None:
        """Delete a specific key from cache."""
        ...

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern. Returns count deleted.

        Example: delete_pattern("market:daily_bars:AAPL:*")
        """
        ...

    async def clear(self) -> None:
        """Clear entire cache. Use sparingly."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        ...
```

## 8.5 Cache-Aside Pattern Implementation

```python
# src/data_engine/storage/cached_repository.py

"""Cached wrapper for data repositories.

Implements the cache-aside pattern:
1. Check cache first
2. On miss, query database
3. Populate cache with result
4. Return result

The cached repository wraps the actual repository and adds
caching transparently. Consumers don't know or care whether
data came from cache or database.
"""

import json
import structlog
from datetime import date
from src.infrastructure.cache.interfaces import CacheService
from src.data_engine.storage.interfaces import MarketDataRepository
from src.data_engine.models import OHLCVBar


logger = structlog.get_logger(__name__)


class CachedMarketDataRepository:
    """Cache-aside wrapper for MarketDataRepository.

    Delegates to the underlying repository on cache miss.
    Caches results with configured TTL.
    """

    def __init__(
        self,
        repository: MarketDataRepository,
        cache: CacheService,
        ttl_seconds: int = 300,
    ) -> None:
        self._repo = repository
        self._cache = cache
        self._ttl = ttl_seconds
        self._logger = logger.bind(component="CachedMarketDataRepo")

    async def get_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list[OHLCVBar]:
        """Get bars with cache-aside pattern."""

        cache_key = f"market:daily_bars:{ticker}:{start_date}:{end_date}"

        # ── Try cache ──
        cached = await self._cache.get(cache_key)
        if cached is not None:
            self._logger.debug("Cache hit", key=cache_key)
            return [OHLCVBar.model_validate_json(bar) for bar in json.loads(cached)]

        # ── Cache miss — query database ──
        self._logger.debug("Cache miss", key=cache_key)
        bars = await self._repo.get_bars(ticker, start_date, end_date)

        # ── Populate cache (only if we got data) ──
        if bars:
            serialized = json.dumps([bar.model_dump_json() for bar in bars])
            await self._cache.set(cache_key, serialized, self._ttl)

        return bars

    async def store_bars(self, bars: list[OHLCVBar]) -> int:
        """Store bars and invalidate related cache entries."""
        result = await self._repo.store_bars(bars)

        # Invalidate cache for affected tickers
        tickers = set(bar.ticker for bar in bars)
        for ticker in tickers:
            pattern = f"market:daily_bars:{ticker}:*"
            deleted = await self._cache.delete_pattern(pattern)
            if deleted > 0:
                self._logger.debug(
                    "Cache invalidated",
                    ticker=ticker,
                    keys_deleted=deleted,
                )

        return result
```

## 8.6 Caching Rules

| Rule | Description |
|------|-------------|
| **CA-001** | Cache is NEVER the system of record — database is authoritative |
| **CA-002** | Cache can be fully cleared at any time without data loss |
| **CA-003** | Cache TTLs set per data type based on update frequency |
| **CA-004** | Write operations MUST invalidate related cache entries |
| **CA-005** | Cache keys follow the namespace convention: `{domain}:{type}:{id}:{qualifier}` |
| **CA-006** | Agent outputs are NEVER cached — each analysis must be fresh |
| **CA-007** | Portfolio state is NEVER cached — must reflect current holdings |
| **CA-008** | Risk metrics are NEVER cached — must use latest data |
| **CA-009** | Cache misses logged at DEBUG level, not WARNING |
| **CA-010** | Cache hit rate tracked for performance monitoring |
| **CA-011** | Consumers never interact with cache directly — cache is transparent via repository wrappers |

---

# 9. IDEMPOTENCY

## 9.1 Idempotency Requirements

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   EVERY DATA PIPELINE OPERATION MUST BE IDEMPOTENT.             ║
║                                                                  ║
║   Running the same ingestion job twice with the same parameters ║
║   must produce the same system state as running it once.        ║
║                                                                  ║
║   This enables:                                                  ║
║   - Safe retry after failures                                    ║
║   - Safe re-run of daily jobs                                    ║
║   - Backfilling without corruption                               ║
║   - Recovery without manual cleanup                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 9.2 Idempotency Patterns

```python
# ── Pattern 1: UPSERT for persistent data ──
# Already covered in Section 7.2.
# INSERT ON CONFLICT UPDATE ensures re-ingestion updates, not duplicates.


# ── Pattern 2: Ingestion checkpointing ──
# For multi-step pipelines, track progress to avoid re-processing.

class IngestionCheckpoint(BaseModel):
    """Tracks progress of an ingestion run.

    If a pipeline fails mid-way, the checkpoint tells us
    where to resume without re-processing completed items.
    """

    pipeline_name: str
    run_id: str
    started_at: datetime
    last_completed_ticker: str = ""
    tickers_completed: int = 0
    tickers_failed: int = 0
    tickers_total: int = 0
    status: str = "running"       # "running" | "completed" | "failed"


class CheckpointedIngestion:
    """Pipeline runner with checkpoint support."""

    async def ingest_watchlist(
        self,
        tickers: list[str],
        target_date: date,
        run_id: str,
    ) -> IngestionCheckpoint:
        """Ingest all watchlist tickers with checkpoint support.

        If a previous run with the same run_id exists and was
        incomplete, resume from where it left off.
        """
        # Check for existing checkpoint
        checkpoint = await self._load_checkpoint(run_id)

        if checkpoint and checkpoint.status == "completed":
            self._logger.info(
                "Ingestion already completed for this run_id",
                run_id=run_id,
            )
            return checkpoint

        # Determine which tickers still need processing
        if checkpoint:
            completed_index = tickers.index(checkpoint.last_completed_ticker) + 1
            remaining = tickers[completed_index:]
            self._logger.info(
                "Resuming from checkpoint",
                run_id=run_id,
                resuming_from=remaining[0] if remaining else "done",
                already_completed=checkpoint.tickers_completed,
            )
        else:
            remaining = tickers
            checkpoint = IngestionCheckpoint(
                pipeline_name="daily_ohlcv",
                run_id=run_id,
                started_at=datetime.now(timezone.utc),
                tickers_total=len(tickers),
            )

        # Process remaining tickers
        for ticker in remaining:
            result = await self._ingest_single(ticker, target_date)

            if result.is_success:
                checkpoint.tickers_completed += 1
            else:
                checkpoint.tickers_failed += 1

            checkpoint.last_completed_ticker = ticker
            await self._save_checkpoint(checkpoint)

        checkpoint.status = "completed"
        await self._save_checkpoint(checkpoint)
        return checkpoint


# ── Pattern 3: Idempotency keys for event publishing ──
# Prevent duplicate events when pipelines are re-run.

class IdempotentEventBus:
    """Event bus that deduplicates events by idempotency key."""

    async def publish(
        self,
        event_name: str,
        payload: dict,
        idempotency_key: str,
    ) -> bool:
        """Publish an event, skipping if the idempotency key was already seen.

        Args:
            event_name: Event identifier.
            payload: Event data.
            idempotency_key: Unique key for this event instance.
                Convention: f"{pipeline}:{ticker}:{date}:{event}"

        Returns:
            True if published, False if deduplicated (already sent).
        """
        if await self._was_already_published(idempotency_key):
            self._logger.debug(
                "Event deduplicated",
                event=event_name,
                idempotency_key=idempotency_key,
            )
            return False

        await self._publish_internal(event_name, payload)
        await self._record_published(idempotency_key)
        return True
```

## 9.3 Idempotency Rules

| Rule | Description |
|------|-------------|
| **ID-001** | All data write operations use UPSERT semantics |
| **ID-002** | Pipeline re-runs with same parameters produce same system state |
| **ID-003** | Long-running pipelines use checkpointing for resume-after-failure |
| **ID-004** | Events use idempotency keys to prevent duplicate emission |
| **ID-005** | Idempotency keys follow the pattern: `{pipeline}:{ticker}:{date}:{event}` |
| **ID-006** | Checkpoint state persisted to database, not in-memory |
| **ID-007** | Completed pipeline runs can be identified and skipped on re-run |

---

# 10. DATA FRESHNESS AND STALENESS

## 10.1 Freshness Tracking

```python
# src/data_engine/freshness/tracker.py

"""Data freshness tracking and alerting.

Monitors the age of data in the system and triggers alerts
when data exceeds staleness thresholds.

Freshness thresholds from L0-system-vision.md Section 8:
- Price data: 15 minutes (0.25 hours)
- Daily OHLCV: 18 hours
- Fundamentals: 100 days
- News: 24 hours
- SEC Filings: 48 hours
"""

import structlog
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class FreshnessStatus(BaseModel):
    """Freshness status for a data point or data set."""

    ticker: str
    data_type: str
    last_updated_at: datetime | None
    staleness_threshold_hours: float
    is_stale: bool
    staleness_hours: float | None       # How many hours past threshold
    status: str                         # "FRESH" | "WARNING" | "STALE" | "MISSING"


class FreshnessThresholds(BaseModel):
    """Configurable staleness thresholds."""

    price_hours: float = 0.25           # 15 minutes
    daily_ohlcv_hours: float = 18.0
    fundamentals_days: float = 100.0
    news_hours: float = 24.0
    filings_hours: float = 48.0
    scores_hours: float = 24.0


class FreshnessTracker:
    """Monitors data freshness across the system."""

    def __init__(
        self,
        thresholds: FreshnessThresholds = FreshnessThresholds(),
    ) -> None:
        self._thresholds = thresholds
        self._logger = logger.bind(component="FreshnessTracker")

    def check_freshness(
        self,
        data_type: str,
        ticker: str,
        last_updated_at: datetime | None,
    ) -> FreshnessStatus:
        """Check if a data point is fresh enough for use.

        Args:
            data_type: Type of data (e.g., "daily_ohlcv").
            ticker: Stock ticker.
            last_updated_at: When the data was last refreshed (UTC).

        Returns:
            FreshnessStatus with detailed freshness information.
        """
        threshold = self._get_threshold_hours(data_type)

        if last_updated_at is None:
            return FreshnessStatus(
                ticker=ticker,
                data_type=data_type,
                last_updated_at=None,
                staleness_threshold_hours=threshold,
                is_stale=True,
                staleness_hours=None,
                status="MISSING",
            )

        now = datetime.now(timezone.utc)
        age_hours = (now - last_updated_at).total_seconds() / 3600

        if age_hours > threshold:
            status = "STALE"
            is_stale = True
        elif age_hours > threshold * 0.8:   # Within 20% of threshold
            status = "WARNING"
            is_stale = False
        else:
            status = "FRESH"
            is_stale = False

        return FreshnessStatus(
            ticker=ticker,
            data_type=data_type,
            last_updated_at=last_updated_at,
            staleness_threshold_hours=threshold,
            is_stale=is_stale,
            staleness_hours=age_hours - threshold if is_stale else None,
            status=status,
        )

    def check_watchlist_freshness(
        self,
        data_type: str,
        freshness_map: dict[str, datetime | None],
    ) -> dict[str, FreshnessStatus]:
        """Check freshness for all tickers in a map.

        Args:
            data_type: Type of data.
            freshness_map: {ticker: last_updated_at} mapping.

        Returns:
            {ticker: FreshnessStatus} mapping.
        """
        results = {}
        stale_count = 0

        for ticker, last_updated in freshness_map.items():
            status = self.check_freshness(data_type, ticker, last_updated)
            results[ticker] = status
            if status.is_stale:
                stale_count += 1

        if stale_count > 0:
            self._logger.warning(
                "Stale data detected across watchlist",
                data_type=data_type,
                stale_count=stale_count,
                total_count=len(freshness_map),
                stale_pct=round(stale_count / len(freshness_map) * 100, 1),
            )

        return results

    def _get_threshold_hours(self, data_type: str) -> float:
        """Get the staleness threshold for a data type."""
        thresholds = {
            "price": self._thresholds.price_hours,
            "daily_ohlcv": self._thresholds.daily_ohlcv_hours,
            "fundamentals": self._thresholds.fundamentals_days * 24,
            "income_statement": self._thresholds.fundamentals_days * 24,
            "balance_sheet": self._thresholds.fundamentals_days * 24,
            "cash_flow": self._thresholds.fundamentals_days * 24,
            "news": self._thresholds.news_hours,
            "filings": self._thresholds.filings_hours,
            "scores": self._thresholds.scores_hours,
        }
        return thresholds.get(data_type, 24.0)   # Default 24 hours
```

## 10.2 Freshness Rules

| Rule | Description |
|------|-------------|
| **FR-001** | Every data point has a `fetched_at` timestamp recording when it was obtained |
| **FR-002** | Freshness checked before any data is used in analysis |
| **FR-003** | Stale data is usable but MUST be flagged in agent confidence calculation |
| **FR-004** | Missing data (never fetched) is distinct from stale data (fetched long ago) |
| **FR-005** | Freshness thresholds are configurable, not hardcoded |
| **FR-006** | Watchlist-wide freshness report generated before every pipeline run |
| **FR-007** | Stale data triggers a re-fetch attempt before analysis if within pipeline time budget |

---

# 11. INGESTION SCHEDULING

## 11.1 Schedule Configuration

```python
# src/data_engine/scheduling/config.py

"""Ingestion schedule configuration.

Defines when each data type should be refreshed.
Schedules are aligned with market hours and data availability.
"""

from pydantic import BaseModel


class IngestionSchedule(BaseModel):
    """Schedule for a single ingestion job."""

    job_name: str
    data_type: str
    cron_expression: str            # Standard cron syntax
    description: str
    tickers_source: str             # "watchlist" | "portfolio" | "all"
    enabled: bool = True
    timeout_seconds: int = 300
    max_concurrent: int = 10        # Concurrent ticker processing
    priority: int = 1               # Lower = higher priority


# ── Standard schedule ──
INGESTION_SCHEDULES: list[IngestionSchedule] = [
    IngestionSchedule(
        job_name="daily_ohlcv_refresh",
        data_type="daily_ohlcv",
        cron_expression="0 18 * * 1-5",    # 6:00 PM ET (after market close)
        description="Fetch daily OHLCV for all watchlist tickers after market close",
        tickers_source="watchlist",
        timeout_seconds=600,
        max_concurrent=10,
        priority=1,
    ),
    IngestionSchedule(
        job_name="pre_market_quote_refresh",
        data_type="quote",
        cron_expression="0 10 * * 1-5",    # 6:00 AM ET (pre-market)
        description="Fetch pre-market quotes for watchlist",
        tickers_source="watchlist",
        timeout_seconds=120,
        max_concurrent=20,
        priority=1,
    ),
    IngestionSchedule(
        job_name="fundamental_data_refresh",
        data_type="fundamentals",
        cron_expression="0 2 * * 6",        # 2:00 AM Saturday
        description="Weekly refresh of financial statements",
        tickers_source="watchlist",
        timeout_seconds=1800,
        max_concurrent=5,
        priority=3,
    ),
    IngestionSchedule(
        job_name="news_refresh",
        data_type="news",
        cron_expression="0 */4 * * 1-5",   # Every 4 hours, weekdays
        description="Refresh news articles for watchlist",
        tickers_source="watchlist",
        timeout_seconds=300,
        max_concurrent=5,
        priority=2,
    ),
    IngestionSchedule(
        job_name="portfolio_holdings_refresh",
        data_type="daily_ohlcv",
        cron_expression="*/15 9-16 * * 1-5",  # Every 15 min during market hours
        description="Frequent refresh for portfolio holdings",
        tickers_source="portfolio",
        timeout_seconds=120,
        max_concurrent=20,
        priority=1,
    ),
]
```

## 11.2 Job Execution Pattern

```python
# src/data_engine/scheduling/job_runner.py

"""Ingestion job runner.

Executes scheduled ingestion jobs with:
- Bounded concurrency
- Per-ticker error isolation
- Progress logging
- Completion summary
"""

import asyncio
import structlog
import time
from datetime import date

logger = structlog.get_logger(__name__)


class IngestionJobRunner:
    """Runs an ingestion job for a list of tickers."""

    def __init__(
        self,
        ingestion_service: "IngestionService",
        max_concurrent: int = 10,
        timeout_seconds: int = 300,
    ) -> None:
        self._service = ingestion_service
        self._max_concurrent = max_concurrent
        self._timeout_seconds = timeout_seconds
        self._logger = logger.bind(component="JobRunner")

    async def run(
        self,
        job_name: str,
        tickers: list[str],
        target_date: date,
    ) -> "JobResult":
        """Run ingestion for all tickers with bounded concurrency.

        Individual ticker failures do NOT stop the job.
        The job completes all tickers and reports aggregate results.

        Args:
            job_name: Identifier for this job run.
            tickers: Tickers to ingest.
            target_date: Date to ingest data for.

        Returns:
            JobResult with aggregate success/failure statistics.
        """
        start_time = time.monotonic()
        self._logger.info(
            "Job started",
            job_name=job_name,
            ticker_count=len(tickers),
            target_date=str(target_date),
            max_concurrent=self._max_concurrent,
        )

        semaphore = asyncio.Semaphore(self._max_concurrent)
        results: list[tuple[str, bool, str]] = []   # (ticker, success, error_msg)

        async def _ingest_one(ticker: str) -> None:
            async with semaphore:
                try:
                    result = await asyncio.wait_for(
                        self._service.ingest_daily_ohlcv(ticker, target_date),
                        timeout=self._timeout_seconds / len(tickers) * 2,
                    )
                    if result.is_success:
                        results.append((ticker, True, ""))
                    else:
                        results.append((ticker, False, result.error.code))
                        self._logger.warning(
                            "Ticker ingestion failed",
                            job_name=job_name,
                            ticker=ticker,
                            error=result.error.code,
                        )
                except asyncio.TimeoutError:
                    results.append((ticker, False, "TIMEOUT"))
                    self._logger.warning(
                        "Ticker ingestion timed out",
                        job_name=job_name,
                        ticker=ticker,
                    )
                except Exception as exc:
                    results.append((ticker, False, str(exc)))
                    self._logger.error(
                        "Ticker ingestion unexpected error",
                        job_name=job_name,
                        ticker=ticker,
                        error=str(exc),
                    )

        # Run all with bounded concurrency
        tasks = [_ingest_one(ticker) for ticker in tickers]
        await asyncio.gather(*tasks)

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        succeeded = [r for r in results if r[1]]
        failed = [r for r in results if not r[1]]

        job_result = JobResult(
            job_name=job_name,
            target_date=target_date,
            total=len(tickers),
            succeeded=len(succeeded),
            failed=len(failed),
            failed_tickers=[(r[0], r[2]) for r in failed],
            elapsed_ms=elapsed_ms,
        )

        self._logger.info(
            "Job completed",
            job_name=job_name,
            total=job_result.total,
            succeeded=job_result.succeeded,
            failed=job_result.failed,
            elapsed_ms=elapsed_ms,
            success_rate=f"{job_result.succeeded / job_result.total * 100:.1f}%",
        )

        return job_result
```

## 11.3 Scheduling Rules

| Rule | Description |
|------|-------------|
| **SC-001** | Ingestion schedules aligned with market hours and data availability windows |
| **SC-002** | Portfolio holdings refreshed more frequently than watchlist |
| **SC-003** | Individual ticker failures do not stop the batch job |
| **SC-004** | Job-level timeout enforced to prevent runaway ingestion runs |
| **SC-005** | Concurrent ticker processing bounded by `max_concurrent` to respect rate limits |
| **SC-006** | Job completion summary logged with success/failure counts |
| **SC-007** | Weekend/holiday awareness: skip market data ingestion on non-trading days |
| **SC-008** | Schedules configurable via config file, not hardcoded |
| **SC-009** | Manual trigger available for any scheduled job (for ad-hoc refresh) |

---

# 12. DATA BACKFILLING

## 12.1 Backfill Pattern

```python
# src/data_engine/ingestion/backfill.py

"""Data backfill utilities.

Backfilling fills historical data gaps. Used when:
- A new ticker is added to the watchlist
- A new data type is integrated
- Historical data needs to be refreshed
- Data gaps are discovered

Backfills are idempotent (upsert) and respect rate limits.
"""

import structlog
from datetime import date, timedelta
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class BackfillRequest(BaseModel):
    """Configuration for a backfill operation."""

    tickers: list[str]
    data_type: str
    start_date: date
    end_date: date
    chunk_size_days: int = 30       # Split large ranges into chunks
    delay_between_tickers_seconds: float = 1.0   # Rate limit courtesy
    priority: str = "low"           # "low" | "normal" | "high"


class BackfillService:
    """Manages historical data backfilling."""

    async def backfill(
        self,
        request: BackfillRequest,
    ) -> "BackfillResult":
        """Execute a backfill operation.

        Splits the date range into chunks to manage memory and
        rate limits. Processes one ticker at a time with configurable
        delays between tickers.

        Backfills are:
        - Idempotent (safe to re-run)
        - Resumable (tracks progress via checkpoints)
        - Rate-limit aware (respects provider limits)
        - Chunked (handles large date ranges)
        """
        self._logger.info(
            "Backfill started",
            tickers=len(request.tickers),
            date_range=f"{request.start_date} to {request.end_date}",
            data_type=request.data_type,
        )

        # Split date range into chunks
        chunks = self._split_date_range(
            request.start_date,
            request.end_date,
            request.chunk_size_days,
        )

        for ticker in request.tickers:
            for chunk_start, chunk_end in chunks:
                await self._ingest_chunk(
                    ticker, request.data_type, chunk_start, chunk_end
                )

            # Courtesy delay between tickers
            if request.delay_between_tickers_seconds > 0:
                await asyncio.sleep(request.delay_between_tickers_seconds)

        ...

    def _split_date_range(
        self,
        start: date,
        end: date,
        chunk_days: int,
    ) -> list[tuple[date, date]]:
        """Split a date range into chunks of chunk_days each."""
        chunks = []
        current = start
        while current <= end:
            chunk_end = min(current + timedelta(days=chunk_days - 1), end)
            chunks.append((current, chunk_end))
            current = chunk_end + timedelta(days=1)
        return chunks
```

## 12.2 Backfill Rules

| Rule | Description |
|------|-------------|
| **BF-001** | All backfills use UPSERT — safe to re-run without duplication |
| **BF-002** | Large date ranges split into chunks (default: 30 days) |
| **BF-003** | Rate limit delays between tickers during backfill |
| **BF-004** | Backfill progress trackable via checkpoints |
| **BF-005** | Backfill jobs run at lower priority than real-time ingestion |
| **BF-006** | Backfill logs include: ticker, date range, chunk progress, rows ingested |
| **BF-007** | New watchlist additions trigger automatic backfill of configured history depth |

---

# 13. DATA DELIVERY (PUBLIC API)

## 13.1 Data Engine Public API

The Data Engine domain exposes a clean public API to all consuming domains.
Consumers never interact with providers, cache, or storage directly.

```python
# src/data_engine/__init__.py

"""Data Engine — Public API.

This is the ONLY interface through which other domains
access market data, fundamental data, and reference data.

All methods return canonical models or Result types.
All methods handle caching transparently.
All methods check freshness and trigger refresh if needed.
"""

from src.data_engine.services.market_data import MarketDataService
from src.data_engine.services.fundamental_data import FundamentalDataService
from src.data_engine.services.news_data import NewsDataService
from src.data_engine.services.watchlist import WatchlistService
from src.data_engine.models import (
    OHLCVBar,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    CompanyProfile,
    NewsArticle,
)

__all__ = [
    "MarketDataService",
    "FundamentalDataService",
    "NewsDataService",
    "WatchlistService",
    "OHLCVBar",
    "IncomeStatement",
    "BalanceSheet",
    "CashFlowStatement",
    "CompanyProfile",
    "NewsArticle",
]
```

```python
# src/data_engine/services/market_data.py

"""Market Data Service — primary consumer-facing interface.

This service provides market data to all consuming domains.
It orchestrates: cache check → freshness check → fetch if needed → return.
"""

import structlog
from datetime import date
from src.shared.types import Result, Success, Failure
from src.data_engine.models import OHLCVBar
from src.data_engine.errors import DataError


logger = structlog.get_logger(__name__)


class MarketDataService:
    """Consumer-facing market data service.

    Provides a clean API for retrieving market data.
    Handles caching, freshness, and provider failover transparently.
    Consumers never need to think about data infrastructure.

    See: specs/L2-modules/data-engine/market-data-ingestion.md
    """

    def __init__(
        self,
        cached_repository: "CachedMarketDataRepository",
        ingestion_service: "IngestionService",
        freshness_tracker: "FreshnessTracker",
    ) -> None:
        self._repo = cached_repository
        self._ingestion = ingestion_service
        self._freshness = freshness_tracker
        self._logger = logger.bind(service="MarketDataService")

    async def get_daily_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        auto_refresh: bool = True,
    ) -> Result[list[OHLCVBar], DataError]:
        """Get daily OHLCV bars for a ticker.

        Transparently handles:
        1. Cache lookup (fast path)
        2. Database query (if cache miss)
        3. Freshness check (is the data current enough?)
        4. Auto-refresh from provider (if stale and auto_refresh=True)

        Args:
            ticker: Uppercase ticker symbol.
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            auto_refresh: If True and data is stale, trigger refresh
                before returning. If False, return whatever we have.

        Returns:
            Success with list of bars in chronological order, or
            Failure if data cannot be retrieved.
        """
        ticker = ticker.strip().upper()

        # Get from cache/database
        bars = await self._repo.get_bars(ticker, start_date, end_date)

        # Check freshness
        if bars and auto_refresh:
            latest_date = bars[-1].date
            freshness = self._freshness.check_freshness(
                "daily_ohlcv", ticker, bars[-1].fetched_at
            )

            if freshness.is_stale:
                self._logger.info(
                    "Data stale, triggering refresh",
                    ticker=ticker,
                    last_fetched=str(bars[-1].fetched_at),
                    staleness_status=freshness.status,
                )
                refresh_result = await self._ingestion.ingest_daily_ohlcv(
                    ticker, end_date
                )
                if refresh_result.is_success:
                    bars = await self._repo.get_bars(ticker, start_date, end_date)

        if not bars:
            return Failure(DataError(
                code="DATA.MARKET.NO_DATA",
                message=f"No daily bars found for {ticker} "
                        f"between {start_date} and {end_date}",
            ))

        return Success(bars)

    async def get_latest_price_cents(
        self,
        ticker: str,
    ) -> Result[int, DataError]:
        """Get the most recent closing price in cents.

        Convenience method for consumers that just need the current price.
        """
        bar = await self._repo.get_latest_bar(ticker)
        if bar is None:
            return Failure(DataError(
                code="DATA.MARKET.NO_DATA",
                message=f"No data available for {ticker}",
            ))
        return Success(bar.close_cents)

    async def get_multiple_tickers_bars(
        self,
        tickers: list[str],
        start_date: date,
        end_date: date,
    ) -> dict[str, list[OHLCVBar]]:
        """Get daily bars for multiple tickers.

        Returns a dictionary mapping each ticker to its bars.
        Tickers with no data are mapped to empty lists.
        """
        results = {}
        for ticker in tickers:
            result = await self.get_daily_bars(
                ticker, start_date, end_date, auto_refresh=False
            )
            results[ticker] = result.value if result.is_success else []
        return results
```

## 13.2 Delivery Rules

| Rule | Description |
|------|-------------|
| **DL-001** | Consuming domains access data ONLY through the Data Engine's public API |
| **DL-002** | Public API methods return canonical models, never raw database rows or provider responses |
| **DL-003** | Public API transparently handles caching — consumers never manage cache |
| **DL-004** | Freshness checks and auto-refresh are transparent to consumers |
| **DL-005** | Multi-ticker queries return a dict with empty lists for missing tickers, never errors |
| **DL-006** | Public API methods document their freshness behavior (auto-refresh or return-as-is) |
| **DL-007** | No consuming domain may import from `src/data_engine/providers/` or `src/data_engine/storage/` |

---

# 14. DATA RETENTION AND ARCHIVAL

## 14.1 Retention Policy

```python
# src/data_engine/retention/config.py

"""Data retention policy configuration.

Defines how long different data types are retained in
primary storage vs. archived to cold storage.
"""

from pydantic import BaseModel


class RetentionPolicy(BaseModel):
    """Retention configuration for a data type."""

    data_type: str
    primary_retention_days: int          # Keep in fast-access database
    archive_retention_days: int | None   # Keep in cold storage (None = forever)
    description: str


RETENTION_POLICIES: list[RetentionPolicy] = [
    RetentionPolicy(
        data_type="daily_ohlcv",
        primary_retention_days=3650,       # 10 years
        archive_retention_days=None,       # Forever
        description="Price history essential for backtesting and analysis",
    ),
    RetentionPolicy(
        data_type="income_statement",
        primary_retention_days=3650,       # 10 years
        archive_retention_days=None,
        description="Financial history for trend analysis",
    ),
    RetentionPolicy(
        data_type="balance_sheet",
        primary_retention_days=3650,
        archive_retention_days=None,
        description="Balance sheet history",
    ),
    RetentionPolicy(
        data_type="cash_flow",
        primary_retention_days=3650,
        archive_retention_days=None,
        description="Cash flow history",
    ),
    RetentionPolicy(
        data_type="news_articles",
        primary_retention_days=365,        # 1 year
        archive_retention_days=1825,       # 5 years
        description="News useful for recent context, archived for research",
    ),
    RetentionPolicy(
        data_type="agent_outputs",
        primary_retention_days=730,        # 2 years
        archive_retention_days=None,       # Forever (audit trail)
        description="Agent analysis history for audit and learning",
    ),
    RetentionPolicy(
        data_type="pipeline_logs",
        primary_retention_days=90,         # 3 months
        archive_retention_days=365,        # 1 year
        description="Operational logs for debugging",
    ),
    RetentionPolicy(
        data_type="cache_entries",
        primary_retention_days=1,          # Ephemeral
        archive_retention_days=None,       # Never archived
        description="Cache is ephemeral, no retention needed",
    ),
]
```

## 14.2 Retention Rules

| Rule | Description |
|------|-------------|
| **RT-001** | Price and financial data retained for minimum 10 years (backtesting requirement) |
| **RT-002** | Agent outputs retained indefinitely (audit trail requirement from L0 INV-006) |
| **RT-003** | News articles archived after 1 year to cold storage |
| **RT-004** | Pipeline operational logs retained 90 days, archived 1 year |
| **RT-005** | Cache has no retention — it is ephemeral by design |
| **RT-006** | Retention enforcement automated via scheduled cleanup job |
| **RT-007** | Archival moves data to cold storage, never deletes analytical data |

---

# 15. MONITORING AND OBSERVABILITY

## 15.1 Pipeline Metrics

| Metric | Granularity | Purpose |
|--------|-------------|---------|
| Ingestion success rate | Per job, per ticker, per day | Pipeline reliability |
| Ingestion latency (p50, p95) | Per provider, per data type | Performance |
| API call count | Per provider, per day | Cost tracking / rate limit proximity |
| API error rate | Per provider | Provider health |
| Data freshness score | Per ticker, per data type | Data currency |
| Stale data count | Per data type, per watchlist scan | Freshness monitoring |
| Cache hit rate | Per data type | Cache effectiveness |
| Storage growth | Per data type, per month | Capacity planning |
| Provider failover count | Per provider pair, per day | Failover frequency |
| Validation rejection rate | Per data type | Data quality trend |
| Rate limit events | Per provider, per day | API budget tracking |
| Backfill progress | Per backfill job | Backfill monitoring |

## 15.2 Pipeline Health Dashboard Data

```python
class PipelineHealthReport(BaseModel):
    """Daily pipeline health report."""

    report_date: date
    report_generated_at: datetime

    # Ingestion summary
    total_tickers_in_watchlist: int
    tickers_with_fresh_data: int
    tickers_with_stale_data: int
    tickers_with_no_data: int

    # Provider health
    provider_statuses: dict[str, bool]     # provider → healthy
    provider_api_calls_today: dict[str, int]
    provider_errors_today: dict[str, int]
    provider_failovers_today: int

    # Data quality
    bars_ingested_today: int
    bars_flagged_today: int
    bars_rejected_today: int
    validation_pass_rate: float

    # Cache performance
    cache_hit_rate: float
    cache_entries_count: int

    # Freshness by type
    freshness_summary: dict[str, dict[str, int]]   # data_type → {fresh, warning, stale, missing}
```

## 15.3 Observability Rules

| Rule | Description |
|------|-------------|
| **OB-001** | Every pipeline run logs a completion summary with success/failure counts |
| **OB-002** | Provider API calls counted and logged daily |
| **OB-003** | Rate limit proximity (>80%) triggers WARNING log |
| **OB-004** | Provider health checked at startup and periodically (every 15 minutes) |
| **OB-005** | Validation rejection rate tracked — spikes indicate provider issues |
| **OB-006** | Pipeline health report generated daily and stored for trend analysis |
| **OB-007** | Cache hit rate below 50% triggers review of TTL configuration |

---

# 16. TRADING CALENDAR

## 16.1 Market Calendar Integration

```python
# src/data_engine/calendar/trading_calendar.py

"""Trading calendar for US equity markets.

Provides awareness of:
- Trading days (Monday-Friday, excluding holidays)
- Market hours (9:30 AM - 4:00 PM ET)
- Pre-market hours (4:00 AM - 9:30 AM ET)
- After-hours (4:00 PM - 8:00 PM ET)
- Early close days (some holidays close at 1:00 PM ET)
- NYSE holiday schedule

This is used by:
- Scheduler: Skip ingestion on non-trading days
- Validation: Reject bars with weekend dates
- Backtester: Count trading days correctly
- Freshness: Adjust staleness thresholds for weekends/holidays
"""

from datetime import date, timedelta


class TradingCalendar:
    """US equity market trading calendar."""

    # NYSE holidays (update annually)
    # Source: https://www.nyse.com/markets/hours-calendars
    NYSE_HOLIDAYS_2025: set[date] = {
        date(2025, 1, 1),    # New Year's Day
        date(2025, 1, 20),   # MLK Day
        date(2025, 2, 17),   # Presidents' Day
        date(2025, 4, 18),   # Good Friday
        date(2025, 5, 26),   # Memorial Day
        date(2025, 6, 19),   # Juneteenth
        date(2025, 7, 4),    # Independence Day
        date(2025, 9, 1),    # Labor Day
        date(2025, 11, 27),  # Thanksgiving
        date(2025, 12, 25),  # Christmas
    }

    def is_trading_day(self, d: date) -> bool:
        """Check if a date is a trading day.

        A trading day is a weekday that is not an NYSE holiday.
        """
        if d.weekday() >= 5:   # Saturday = 5, Sunday = 6
            return False
        if d in self._get_holidays(d.year):
            return False
        return True

    def next_trading_day(self, d: date) -> date:
        """Get the next trading day after the given date."""
        candidate = d + timedelta(days=1)
        while not self.is_trading_day(candidate):
            candidate += timedelta(days=1)
        return candidate

    def previous_trading_day(self, d: date) -> date:
        """Get the most recent trading day before the given date."""
        candidate = d - timedelta(days=1)
        while not self.is_trading_day(candidate):
            candidate -= timedelta(days=1)
        return candidate

    def trading_days_between(
        self,
        start: date,
        end: date,
    ) -> list[date]:
        """List all trading days between start and end (inclusive)."""
        days = []
        current = start
        while current <= end:
            if self.is_trading_day(current):
                days.append(current)
            current += timedelta(days=1)
        return days

    def count_trading_days(
        self,
        start: date,
        end: date,
    ) -> int:
        """Count trading days between two dates (inclusive)."""
        return len(self.trading_days_between(start, end))

    def _get_holidays(self, year: int) -> set[date]:
        """Get holidays for a year. Extend as needed."""
        holidays_by_year = {
            2025: self.NYSE_HOLIDAYS_2025,
            # Add future years as they are published
        }
        return holidays_by_year.get(year, set())
```

## 16.2 Calendar Rules

| Rule | Description |
|------|-------------|
| **TC-001** | Market data ingestion skipped on non-trading days |
| **TC-002** | Data validation rejects bars with non-trading-day dates |
| **TC-003** | Freshness thresholds adjusted over weekends (Friday data not stale on Saturday) |
| **TC-004** | Trading day count used for annualization (252 days/year standard) |
| **TC-005** | Holiday calendar updated annually before year-start |
| **TC-006** | Backtesting uses the trading calendar for accurate day counts |

---

# 17. TESTING CHECKLIST FOR DATA PIPELINES

When building or modifying data pipeline components, verify:

```text
PROVIDER ADAPTER:
─────────────────
□ Inherits from BaseProviderAdapter
□ Implements category-specific Protocol
□ Translates to canonical models (dollars_to_cents, UTC, uppercase tickers)
□ Rate limiting handled via injected RateLimiter
□ Retry logic with exponential backoff
□ Provider-specific quirks documented and handled
□ API keys never appear in logs
□ Health check endpoint implemented
□ Recorded API responses stored in test fixtures

VALIDATION:
───────────
□ Schema validation via Pydantic model validators
□ Domain quality rules implemented and composable
□ REJECT / FLAG / ACCEPT outcomes clearly defined
□ Rejection reasons logged with specific rule IDs
□ Weekend/holiday dates rejected
□ Cross-field consistency checked (e.g., high >= low)

STORAGE:
────────
□ UPSERT semantics (idempotent writes)
□ Unique keys enforced at database level
□ Repository returns canonical models, not raw rows
□ Empty results return empty lists, not None
□ Results always in chronological order

CACHING:
────────
□ Cache-aside pattern (read: cache → DB, write: DB → invalidate cache)
□ Write operations invalidate related cache keys
□ TTL set per data type based on update frequency
□ Cache hit/miss logged at DEBUG level
□ System functional with empty/cleared cache

IDEMPOTENCY:
────────────
□ Running the same ingestion twice produces identical state
□ No duplicate rows from re-ingestion
□ Events deduplicated with idempotency keys
□ Long pipelines use checkpointing for resume

FRESHNESS:
──────────
□ fetched_at tracked on every data point
□ Freshness checked before analysis uses data
□ Stale data flagged but usable (affects confidence score)
□ Auto-refresh triggered transparently when stale

SCHEDULING:
───────────
□ Schedule aligned with market hours
□ Trading calendar consulted (skip weekends/holidays)
□ Individual ticker failures don't stop the batch
□ Batch completion summary logged
□ Bounded concurrency respects rate limits

GENERAL:
────────
□ All monetary values in integer cents
□ All timestamps in UTC
□ All tickers uppercase
□ Logging follows L4 coding standards
□ Error handling uses Result types
□ Tests cover happy path, failures, edge cases
□ Integration tests use recorded API responses
```

---

# 18. CROSS-REFERENCES

| Document                              | Location                                              |
|---------------------------------------|-------------------------------------------------------|
| L0: System Vision                     | `specs/L0-system-vision.md`                           |
| L0: Data Architecture Principles      | `specs/L0-system-vision.md` Section 6                 |
| L0: Data Freshness Requirements       | `specs/L0-system-vision.md` Section 8 (authoritative) |
| L0: Configurable Parameters           | `specs/L0-system-vision.md` Section 8                 |
| L4: Coding Standards                  | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards   | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                 | `specs/L4-conventions/testing-standards.md`            |
| L4: AI Agent Design Standards         | `specs/L4-conventions/ai-agent-design-standards.md`   |
| L1: Data Engine Domain                | `specs/L1-domains/data-engine.md`                     |
| L2: Market Data Ingestion Module      | `specs/L2-modules/data-engine/market-data-ingestion.md` |
| L2: Data Storage Module              | `specs/L2-modules/data-engine/data-storage.md`        |
| Guardrails: Data Quality              | `specs/guardrails/data-quality-guardrails.md`         |
| Guardrails: Operational               | `specs/guardrails/operational-guardrails.md`           |

---
```
