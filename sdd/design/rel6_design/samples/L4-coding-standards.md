## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines the coding conventions, patterns, and standards that
**all code** in the project must follow — whether written by a human
developer or an AI coding agent. Consistency is non-negotiable. An AI agent
reading this document alongside an L2 module spec must be able to produce
code that is indistinguishable in style from any other module in the system.

## Scope

This document covers general coding standards for the primary language
(Python). Companion documents cover domain-specific conventions:

| Topic                        | Document                                       |
|------------------------------|------------------------------------------------|
| Financial calculations       | `L4-conventions/financial-calculation-standards.md` |
| AI agent design patterns     | `L4-conventions/ai-agent-design-standards.md`  |
| Data pipeline patterns       | `L4-conventions/data-pipeline-standards.md`    |
| Testing patterns             | `L4-conventions/testing-standards.md`          |
| Error handling (deep dive)   | `L4-conventions/error-handling.md`             |

---

# 1. PROJECT STRUCTURE

## 1.1 Top-Level Repository Layout

```text
project-root/
│
├── src/                          # All application source code
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── config/                   # Configuration management
│   ├── shared/                   # Cross-cutting shared code
│   │   ├── types/                # Shared type definitions
│   │   ├── errors/               # Error class hierarchy
│   │   ├── utils/                # Pure utility functions
│   │   ├── constants/            # System-wide constants
│   │   └── interfaces/           # Abstract base classes / protocols
│   │
│   ├── infrastructure/           # External system adapters
│   │   ├── database/             # DB connection, migrations
│   │   ├── llm/                  # LLM provider gateway
│   │   ├── http_client/          # Shared HTTP client
│   │   ├── cache/                # Caching layer
│   │   ├── scheduler/            # Task scheduling
│   │   └── logging/              # Structured logging setup
│   │
│   ├── data_engine/              # Domain: Data Engine
│   │   ├── ingestion/
│   │   ├── storage/
│   │   ├── providers/            # External data provider adapters
│   │   └── validation/
│   │
│   ├── research/                 # Domain: Research Analysis
│   │   ├── screener/
│   │   ├── earnings/
│   │   ├── thesis/
│   │   └── agents/               # Research AI agents
│   │
│   ├── quantitative/             # Domain: Quantitative Analysis
│   │   ├── indicators/
│   │   ├── signals/
│   │   ├── scoring/
│   │   ├── backtesting/
│   │   └── agents/
│   │
│   ├── portfolio/                # Domain: Portfolio Strategy
│   │   ├── state/
│   │   ├── sizing/
│   │   ├── optimization/
│   │   └── agents/
│   │
│   ├── risk/                     # Domain: Risk Management
│   │   ├── analytics/
│   │   ├── stress_testing/
│   │   ├── guardrails/
│   │   └── agents/
│   │
│   ├── reporting/                # Domain: Execution & Reporting
│   │   ├── briefs/
│   │   ├── performance/
│   │   ├── dashboards/
│   │   └── trade_journal/
│   │
│   └── orchestration/            # Domain: Orchestration
│       ├── pipelines/
│       ├── workflows/
│       └── scheduling/
│
├── tests/                        # Mirror of src/ structure
│   ├── unit/
│   │   ├── data_engine/
│   │   ├── research/
│   │   ├── quantitative/
│   │   └── ...
│   ├── integration/
│   │   ├── data_engine/
│   │   └── ...
│   └── fixtures/                 # Shared test data
│       ├── market_data/
│       ├── financial_statements/
│       └── ...
│
├── specs/                        # SDD specification documents
│   └── (see L0 for structure)
│
├── scripts/                      # Dev/ops utility scripts
├── config/                       # Configuration files
│   ├── default.yaml
│   ├── development.yaml
│   ├── production.yaml
│   └── watchlist.json
│
├── migrations/                   # Database migrations
├── docs/                         # Additional documentation
├── .env.example                  # Environment variable template
├── pyproject.toml                # Project metadata and dependencies
├── Makefile                      # Common commands
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

## 1.2 Module Internal Structure

Every module within a domain follows this internal layout:

```text
# Example: src/data_engine/ingestion/

ingestion/
├── __init__.py                   # Public API exports only
├── service.py                    # Business logic (IngestionService)
├── repository.py                 # Data access (IngestionRepository)
├── models.py                     # Data models / schemas for this module
├── errors.py                     # Module-specific error classes
├── constants.py                  # Module-specific constants
├── types.py                      # Module-specific type aliases
├── interfaces.py                 # Abstract base classes / protocols
└── adapters/                     # External adapters (if applicable)
    ├── __init__.py
    ├── polygon_adapter.py
    └── alpha_vantage_adapter.py
```

**Rules:**
- Every module **must** have an `__init__.py` that explicitly exports the
  public API
- No external consumer may import from internal files directly — only
  through `__init__.py`
- If a file exceeds 300 lines, split it into smaller files within the
  same module
- If a module has more than 10 files, consider splitting into sub-modules

---

# 2. NAMING CONVENTIONS

## 2.1 File Naming

| Type               | Convention     | Example                           |
|--------------------|----------------|-----------------------------------|
| Python modules     | `snake_case`   | `market_data_service.py`          |
| Python packages    | `snake_case`   | `data_engine/`                    |
| Test files         | `test_` prefix | `test_market_data_service.py`     |
| Config files       | `snake_case`   | `default.yaml`                    |
| Spec documents     | `kebab-case`   | `market-data-ingestion.md`        |
| Migration files    | `NNN_description` | `001_create_ohlcv_table.sql`   |
| Script files       | `snake_case`   | `seed_watchlist.py`               |

## 2.2 Python Naming

| Type                | Convention      | Example                          |
|---------------------|-----------------|----------------------------------|
| Classes             | `PascalCase`    | `MarketDataService`              |
| Exceptions          | `PascalCase` + `Error` suffix | `DataFetchError`    |
| Functions/Methods   | `snake_case`    | `fetch_daily_ohlcv`             |
| Variables           | `snake_case`    | `closing_price`                  |
| Constants           | `UPPER_SNAKE`   | `MAX_RETRY_COUNT`                |
| Private members     | `_` prefix      | `_validate_ticker`               |
| Protected members   | `_` prefix      | `_connection_pool`               |
| Type aliases        | `PascalCase`    | `TickerSymbol = str`             |
| Protocols           | `PascalCase`    | `DataProvider`                   |
| Enums               | `PascalCase`    | `OrderStatus`                    |
| Enum members        | `UPPER_SNAKE`   | `OrderStatus.PENDING`            |

## 2.3 Domain-Specific Naming Rules

```python
# ── Ticker symbols: always uppercase string ──
ticker: str = "AAPL"  # ✓
ticker: str = "aapl"  # ✗

# ── Financial amounts: suffix with _cents for integer cents ──
price_cents: int = 15099       # $150.99  ✓
price: float = 150.99          # ✗ NEVER for stored/computed values

# ── Percentages: suffix with _pct for display, _ratio for math ──
growth_pct: float = 12.5       # Display: "12.5%"
growth_ratio: float = 0.125    # Computation: price * (1 + growth_ratio)

# ── Date/time: always use _at suffix for timestamps, _date for dates ──
created_at: datetime            # ✓ timestamp
earnings_date: date             # ✓ calendar date
created: datetime               # ✗ ambiguous

# ── Counts: suffix with _count ──
retry_count: int = 3            # ✓
retries: int = 3                # ✗ ambiguous (could be the retries themselves)

# ── Duration: suffix with _seconds, _minutes, _hours, _days ──
timeout_seconds: int = 30       # ✓
cache_ttl_hours: int = 24       # ✓
timeout: int = 30               # ✗ unclear unit

# ── Booleans: prefix with is_, has_, can_, should_, was_ ──
is_active: bool                 # ✓
has_earnings: bool              # ✓
can_trade: bool                 # ✓
active: bool                    # ✗ could be misread as non-boolean
```

## 2.4 Abbreviation Rules

| Approved Abbreviation | Meaning                     | Usage Context              |
|-----------------------|-----------------------------|----------------------------|
| `db`                  | Database                    | Variable names, not classes|
| `config` / `cfg`      | Configuration               | Variable names             |
| `msg`                 | Message                     | Variable names             |
| `ctx`                 | Context                     | Variable names             |
| `env`                 | Environment                 | Variable names             |
| `pct`                 | Percent                     | Suffixes                   |
| `avg`                 | Average                     | Variable/function names    |
| `std`                 | Standard deviation          | Variable/function names    |
| `vol`                 | Volume OR Volatility        | **MUST disambiguate** — use `trade_vol` vs `price_vol` |
| `qty`                 | Quantity                    | Variable names             |
| `txn`                 | Transaction                 | Variable names             |
| `df`                  | DataFrame                   | Only for pandas DataFrames |
| `ts`                  | Time series or Timestamp    | **MUST disambiguate** in context |

**Banned abbreviations** (always spell out):
- `ret` → use `returns` or `result`
- `val` → use `value` or `validation`
- `calc` → use `calculate` or `calculation`
- `proc` → use `process`
- `mgr` → use `manager`
- `num` → use `count` or the specific noun

---

# 3. TYPE SYSTEM

## 3.1 Type Hint Requirements

**Every function, every method, every class attribute must have type hints.**
No exceptions.

```python
# ✓ CORRECT — fully typed
def calculate_sma(
    prices: list[float],
    period: int,
) -> list[float | None]:
    ...

# ✗ WRONG — missing types
def calculate_sma(prices, period):
    ...
```

## 3.2 Type Hint Style

```python
# ── Use built-in generics (Python 3.10+ style) ──
items: list[str]                 # ✓
items: List[str]                 # ✗ (don't import from typing)

results: dict[str, int]         # ✓
results: Dict[str, int]         # ✗

maybe: str | None               # ✓
maybe: Optional[str]            # ✗

combo: str | int                # ✓
combo: Union[str, int]          # ✗

# ── Exception: use typing imports only when needed ──
from typing import TypeAlias, Protocol, TypeVar, Generic
from typing import Any           # Use sparingly, document why

# ── Use TypeAlias for domain types ──
TickerSymbol: TypeAlias = str
PriceCents: TypeAlias = int
Percentage: TypeAlias = float
DateStr: TypeAlias = str          # ISO 8601 date string "2025-01-15"
```

## 3.3 Data Models — Pydantic as Standard

All data structures that cross module boundaries **must** be Pydantic
models. Internal-only scratch data may use dataclasses.

```python
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


# ── Enums for constrained values ──
class Recommendation(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ── Pydantic model for structured data ──
class OHLCVBar(BaseModel):
    """A single OHLCV price bar."""

    ticker: str = Field(..., description="Uppercase ticker symbol")
    date: date = Field(..., description="Trading date")
    open_cents: int = Field(..., ge=0, description="Open price in cents")
    high_cents: int = Field(..., ge=0, description="High price in cents")
    low_cents: int = Field(..., ge=0, description="Low price in cents")
    close_cents: int = Field(..., ge=0, description="Close price in cents")
    volume: int = Field(..., ge=0, description="Trading volume in shares")
    source: str = Field(..., description="Data provider name")
    fetched_at: datetime = Field(..., description="When data was fetched (UTC)")

    class Config:
        frozen = True  # Immutable after creation


# ── Use model_validator for cross-field validation ──
from pydantic import model_validator

class OHLCVBarValidated(OHLCVBar):

    @model_validator(mode="after")
    def validate_price_relationships(self) -> "OHLCVBarValidated":
        if self.high_cents < self.low_cents:
            raise ValueError(
                f"High ({self.high_cents}) must be >= Low ({self.low_cents})"
            )
        if self.open_cents > self.high_cents or self.open_cents < self.low_cents:
            raise ValueError("Open must be between Low and High")
        if self.close_cents > self.high_cents or self.close_cents < self.low_cents:
            raise ValueError("Close must be between Low and High")
        return self
```

## 3.4 When to Use What

| Structure          | Use When                                            |
|--------------------|-----------------------------------------------------|
| Pydantic `BaseModel` | Data crossing module boundaries, API I/O, agent I/O, anything persisted, anything validated |
| `dataclass`        | Internal-only ephemeral data, simple value holders  |
| `TypedDict`        | Typed dictionary structures for JSON-like data      |
| `NamedTuple`       | Lightweight immutable records (e.g., coordinate pairs) |
| Plain `dict`       | **Never** for structured data — always type it      |

---

# 4. FUNCTION & METHOD STANDARDS

## 4.1 Function Rules

```python
# ── Max 40 lines per function ──
# If a function exceeds 40 lines, split it into helper functions.

# ── Max 4 parameters ──
# If more than 4 parameters, use a config/options object.

# ✓ CORRECT — options object
class ScreenerOptions(BaseModel):
    min_market_cap_cents: int | None = None
    max_pe_ratio: float | None = None
    sectors: list[str] | None = None
    min_volume: int | None = None
    limit: int = 50

def screen_stocks(options: ScreenerOptions) -> list[ScreenerResult]:
    ...

# ✗ WRONG — too many parameters
def screen_stocks(
    min_market_cap, max_pe, sectors, min_volume, limit, sort_by, order
):
    ...
```

## 4.2 Function Documentation

Every public function **must** have a docstring following Google style:

```python
def calculate_sharpe_ratio(
    returns: list[float],
    risk_free_rate_annual: float = 0.05,
    periods_per_year: int = 252,
) -> float | None:
    """Calculate the annualized Sharpe ratio for a series of returns.

    Uses the standard formula: (mean_return - risk_free_rate) / std_return,
    annualized by multiplying by sqrt(periods_per_year).

    Args:
        returns: List of periodic (e.g., daily) simple returns as decimals.
            Example: [0.01, -0.005, 0.003] for +1%, -0.5%, +0.3%.
        risk_free_rate_annual: Annual risk-free rate as decimal.
            Default 0.05 (5%). Will be converted to per-period rate internally.
        periods_per_year: Number of periods in a year. Use 252 for daily
            trading returns, 12 for monthly, 52 for weekly.

    Returns:
        Annualized Sharpe ratio as float, or None if calculation is not
        possible (e.g., fewer than 2 returns or zero standard deviation).

    Raises:
        ValueError: If periods_per_year is not positive.
        ValueError: If risk_free_rate_annual is negative.

    Example:
        >>> daily_returns = [0.001, 0.002, -0.001, 0.003, -0.002]
        >>> calculate_sharpe_ratio(daily_returns, risk_free_rate_annual=0.05)
        1.234  # (illustrative)

    Note:
        This uses simple returns, not log returns. Ensure consistency
        with the return type used throughout the system.

    See Also:
        L4-conventions/financial-calculation-standards.md Section 3.2
    """
    ...
```

## 4.3 Private Function Documentation

Private functions need a brief docstring (one-liner is acceptable if the
function is straightforward):

```python
def _normalize_ticker(raw_ticker: str) -> str:
    """Strip whitespace and convert ticker to uppercase."""
    return raw_ticker.strip().upper()
```

## 4.4 Return Type Patterns

```python
from src.shared.types import Result, Error

# ── For operations that can fail: use Result pattern ──
# (Never raise exceptions for expected business failures)

def find_company(ticker: str) -> Result[CompanyProfile, DataError]:
    """Look up company profile by ticker.

    Returns:
        Success(CompanyProfile) if found.
        Failure(DataError) if ticker not found or data unavailable.
    """
    ...

# ── For collections that may be empty: return empty collection, never None ──
def get_signals(ticker: str) -> list[Signal]:
    """Returns signals for ticker. Empty list if none found."""
    ...

# ── For single items that may not exist: use None ──
def get_latest_thesis(ticker: str) -> Thesis | None:
    """Returns the most recent thesis, or None if no thesis exists."""
    ...

# ── Never return ambiguous types ──
def get_price(ticker: str) -> int | None:      # ✓ Clear: price_cents or missing
    ...

def get_price(ticker: str) -> int:              # ✗ What does 0 mean? Missing? Free?
    ...
```

---

# 5. RESULT TYPE — THE CORE ERROR HANDLING PATTERN

## 5.1 Result Type Definition

The project uses a `Result` type for operations that can fail in expected
ways. This is the **primary** error handling mechanism.

```python
# src/shared/types/result.py

from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Success(Generic[T]):
    """Represents a successful operation result."""
    value: T

    @property
    def is_success(self) -> bool:
        return True

    @property
    def is_failure(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class Failure(Generic[E]):
    """Represents a failed operation result."""
    error: E

    @property
    def is_success(self) -> bool:
        return False

    @property
    def is_failure(self) -> bool:
        return True


Result = Success[T] | Failure[E]
```

## 5.2 Result Usage Pattern

```python
from src.shared.types import Result, Success, Failure
from src.data_engine.ingestion.errors import DataFetchError, DataValidationError


class MarketDataService:

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch daily OHLCV data for a ticker within date range."""

        # Validate inputs
        if not self._is_valid_ticker(ticker):
            return Failure(DataFetchError(
                code="INVALID_TICKER",
                message=f"Invalid ticker symbol: {ticker}",
            ))

        # Attempt primary provider
        result = await self._provider.fetch(ticker, start_date, end_date)

        if result.is_failure:
            # Attempt fallback provider
            self._logger.warning(
                "Primary provider failed, attempting fallback",
                ticker=ticker,
                error=result.error,
            )
            result = await self._fallback_provider.fetch(
                ticker, start_date, end_date
            )

        if result.is_failure:
            return Failure(DataFetchError(
                code="ALL_PROVIDERS_FAILED",
                message=f"All data providers failed for {ticker}",
                details={"ticker": ticker, "providers_attempted": 2},
            ))

        # Validate data quality
        validated = self._validate_bars(result.value)
        if validated.is_failure:
            return Failure(validated.error)

        return Success(validated.value)


# ── Consumer side ──
async def handle_request(ticker: str) -> None:
    result = await market_data_service.fetch_daily_ohlcv(
        ticker=ticker,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )

    match result:
        case Success(value=bars):
            process_bars(bars)
        case Failure(error=err) if err.code == "INVALID_TICKER":
            logger.error("Bad ticker", ticker=ticker)
        case Failure(error=err):
            logger.error("Data fetch failed", error=err)
            alert_fund_manager(err)
```

## 5.3 When to Use Result vs Exceptions

```text
┌─────────────────────────────┬───────────────────────────────────────┐
│ USE RESULT TYPE             │ USE EXCEPTIONS                        │
├─────────────────────────────┼───────────────────────────────────────┤
│ Business logic failures     │ Programming errors (bugs)             │
│ Expected error conditions   │ Truly unexpected conditions           │
│ Data validation failures    │ Infrastructure failures (DB down)     │
│ External API failures       │ Assertion violations                  │
│ "Not found" scenarios       │ Out of memory, stack overflow         │
│ Permission/auth failures    │ Unrecoverable state corruption        │
│                             │                                       │
│ Caller should handle this   │ Caller should NOT handle this —       │
│ as part of normal flow      │ let it propagate to global handler    │
└─────────────────────────────┴───────────────────────────────────────┘
```

---

# 6. ERROR CLASS HIERARCHY

## 6.1 Base Error Classes

```python
# src/shared/errors/base.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DomainError:
    """Base class for all domain errors in the system.

    All domain-specific errors inherit from this. Used with the
    Result type for expected failure cases.
    """

    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


# ── Domain-specific error base classes ──
# Each domain defines its own error hierarchy inheriting from DomainError

@dataclass(frozen=True)
class DataError(DomainError):
    """Base error for Data Engine domain."""
    pass


@dataclass(frozen=True)
class ResearchError(DomainError):
    """Base error for Research Analysis domain."""
    pass


@dataclass(frozen=True)
class QuantError(DomainError):
    """Base error for Quantitative Analysis domain."""
    pass


@dataclass(frozen=True)
class PortfolioError(DomainError):
    """Base error for Portfolio Strategy domain."""
    pass


@dataclass(frozen=True)
class RiskError(DomainError):
    """Base error for Risk Management domain."""
    pass
```

## 6.2 Module-Level Error Example

```python
# src/data_engine/ingestion/errors.py

from dataclasses import dataclass
from src.shared.errors import DataError


@dataclass(frozen=True)
class DataFetchError(DataError):
    """Failed to fetch data from an external provider."""
    provider: str = ""
    ticker: str = ""


@dataclass(frozen=True)
class DataValidationError(DataError):
    """Fetched data failed quality validation."""
    field_name: str = ""
    expected: str = ""
    actual: str = ""


@dataclass(frozen=True)
class ProviderRateLimitError(DataError):
    """External provider rate limit exceeded."""
    provider: str = ""
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class StaleDataError(DataError):
    """Data exceeds acceptable staleness threshold."""
    data_type: str = ""
    last_updated_at: str = ""
    max_staleness_hours: float = 0.0
```

## 6.3 Error Code Convention

Error codes follow the pattern: `DOMAIN.MODULE.SPECIFIC_ERROR`

```python
# ── Error code examples ──
"DATA.INGESTION.PROVIDER_TIMEOUT"
"DATA.INGESTION.INVALID_TICKER"
"DATA.INGESTION.RATE_LIMITED"
"DATA.VALIDATION.PRICE_NEGATIVE"
"DATA.VALIDATION.MISSING_FIELD"
"DATA.STORAGE.WRITE_FAILED"
"RESEARCH.THESIS.INSUFFICIENT_DATA"
"RESEARCH.EARNINGS.PARSE_FAILED"
"QUANT.INDICATOR.INSUFFICIENT_HISTORY"
"QUANT.BACKTEST.LOOK_AHEAD_DETECTED"
"PORTFOLIO.SIZING.EXCEEDS_MAX_POSITION"
"RISK.GUARDRAIL.CONCENTRATION_BREACH"
"RISK.GUARDRAIL.DRAWDOWN_THRESHOLD"
```

---

# 7. SERVICE PATTERN — The Core Architectural Unit

## 7.1 Standard Service Structure

Every module's business logic lives in a `Service` class that follows
this exact structure:

```python
# src/data_engine/ingestion/service.py

import structlog
from src.shared.types import Result, Success, Failure
from src.shared.interfaces import EventBus
from src.data_engine.ingestion.interfaces import MarketDataProvider
from src.data_engine.ingestion.repository import IngestionRepository
from src.data_engine.ingestion.models import OHLCVBar, IngestionResult
from src.data_engine.ingestion.errors import DataFetchError, DataValidationError


logger = structlog.get_logger(__name__)


class IngestionService:
    """Orchestrates market data ingestion from external providers.

    Responsibilities:
        - Fetch data from primary provider with fallback
        - Validate data quality
        - Store validated data
        - Emit ingestion events

    See: specs/L2-modules/data-engine/market-data-ingestion.md
    """

    def __init__(
        self,
        primary_provider: MarketDataProvider,
        fallback_provider: MarketDataProvider,
        repository: IngestionRepository,
        event_bus: EventBus,
    ) -> None:
        self._primary_provider = primary_provider
        self._fallback_provider = fallback_provider
        self._repository = repository
        self._event_bus = event_bus
        self._logger = logger.bind(service="IngestionService")

    async def ingest_daily_ohlcv(
        self,
        ticker: str,
        target_date: date,
    ) -> Result[IngestionResult, DataFetchError | DataValidationError]:
        """Ingest daily OHLCV data for a single ticker.

        Follows the standard service method flow:
        1. Validate inputs
        2. Execute business logic
        3. Persist results
        4. Emit events
        5. Return result
        """
        # ── Step 1: Validate ──
        ticker = ticker.strip().upper()
        validation = self._validate_request(ticker, target_date)
        if validation.is_failure:
            return validation

        self._logger.info(
            "Ingesting daily OHLCV",
            ticker=ticker,
            target_date=str(target_date),
        )

        # ── Step 2: Execute ──
        bars = await self._fetch_with_fallback(ticker, target_date)
        if bars.is_failure:
            return bars

        quality_result = self._validate_data_quality(bars.value)
        if quality_result.is_failure:
            return quality_result

        # ── Step 3: Persist ──
        await self._repository.store_bars(quality_result.value)

        # ── Step 4: Emit events ──
        await self._event_bus.publish(
            "data.ingestion.completed",
            {
                "ticker": ticker,
                "date": str(target_date),
                "bar_count": len(quality_result.value),
            },
        )

        # ── Step 5: Return ──
        ingestion_result = IngestionResult(
            ticker=ticker,
            date=target_date,
            bars_ingested=len(quality_result.value),
            source=quality_result.value[0].source if quality_result.value else "",
        )

        self._logger.info(
            "Ingestion completed",
            ticker=ticker,
            bars_ingested=ingestion_result.bars_ingested,
        )

        return Success(ingestion_result)

    # ── Private methods below ──

    def _validate_request(
        self,
        ticker: str,
        target_date: date,
    ) -> Result[None, DataFetchError]:
        ...

    async def _fetch_with_fallback(
        self,
        ticker: str,
        target_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        ...

    def _validate_data_quality(
        self,
        bars: list[OHLCVBar],
    ) -> Result[list[OHLCVBar], DataValidationError]:
        ...
```

## 7.2 Service Method Flow — Mandatory Steps

Every public service method follows these steps in order:

```text
┌─────────────────────────────────────────────────┐
│           SERVICE METHOD FLOW                    │
│                                                  │
│  1. VALIDATE    → Check inputs, return early     │
│                   on invalid                     │
│  2. LOG ENTRY   → Log the operation starting     │
│  3. EXECUTE     → Run business logic             │
│  4. PERSIST     → Save results to storage        │
│  5. EMIT EVENT  → Publish domain event           │
│  6. LOG EXIT    → Log success with key metrics   │
│  7. RETURN      → Return Result type             │
│                                                  │
│  Steps 4-5 may be skipped for read-only queries  │
└─────────────────────────────────────────────────┘
```

---

# 8. ADAPTER PATTERN — External System Integration

## 8.1 Interface Definition

Every external system interaction is defined by a Protocol (interface):

```python
# src/data_engine/ingestion/interfaces.py

from typing import Protocol
from datetime import date
from src.shared.types import Result
from src.data_engine.ingestion.models import OHLCVBar
from src.data_engine.ingestion.errors import DataFetchError


class MarketDataProvider(Protocol):
    """Interface for market data providers.

    All market data providers must implement this protocol.
    Adapters for specific providers (FMP, etc.)
    implement this interface.
    """

    @property
    def provider_name(self) -> str:
        """Unique identifier for this provider."""
        ...

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch daily OHLCV bars for a ticker.

        Must return data in canonical OHLCVBar format regardless
        of the provider's native format.

        Args:
            ticker: Uppercase ticker symbol.
            start_date: First date (inclusive).
            end_date: Last date (inclusive).

        Returns:
            Success with list of bars, or Failure with error details.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the provider is currently reachable."""
        ...
```

## 8.2 Adapter Implementation

```python
# src/data_engine/ingestion/adapters/polygon_adapter.py

import structlog
from datetime import date
from src.shared.types import Result, Success, Failure
from src.data_engine.ingestion.interfaces import MarketDataProvider
from src.data_engine.ingestion.models import OHLCVBar
from src.data_engine.ingestion.errors import DataFetchError


logger = structlog.get_logger(__name__)


class PolygonMarketDataAdapter:
    """Polygon.io adapter implementing MarketDataProvider protocol.

    Translates Polygon's API responses into canonical OHLCVBar format.
    Handles rate limiting, pagination, and Polygon-specific quirks.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.polygon.io",
        rate_limit_per_minute: int = 5,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._rate_limit_per_minute = rate_limit_per_minute
        self._logger = logger.bind(provider="polygon")

    @property
    def provider_name(self) -> str:
        return "polygon"

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch from Polygon and translate to canonical format."""
        try:
            raw_response = await self._make_request(ticker, start_date, end_date)
            bars = self._translate_response(raw_response, ticker)
            return Success(bars)

        except ConnectionError as exc:
            return Failure(DataFetchError(
                code="DATA.INGESTION.PROVIDER_TIMEOUT",
                message=f"Polygon API connection failed: {exc}",
                provider=self.provider_name,
                ticker=ticker,
            ))

    def _translate_response(
        self,
        raw: dict,
        ticker: str,
    ) -> list[OHLCVBar]:
        """Translate Polygon-specific response to canonical OHLCVBar.

        This is the ONLY place where Polygon's field names appear.
        All downstream code works with OHLCVBar only.
        """
        bars: list[OHLCVBar] = []
        for result in raw.get("results", []):
            bars.append(OHLCVBar(
                ticker=ticker,
                date=self._timestamp_to_date(result["t"]),
                open_cents=self._dollars_to_cents(result["o"]),
                high_cents=self._dollars_to_cents(result["h"]),
                low_cents=self._dollars_to_cents(result["l"]),
                close_cents=self._dollars_to_cents(result["c"]),
                volume=int(result["v"]),
                source=self.provider_name,
                fetched_at=datetime.now(timezone.utc),
            ))
        return bars

    @staticmethod
    def _dollars_to_cents(dollars: float) -> int:
        """Convert dollar float to integer cents.

        Uses round() to handle floating point precision issues.
        See: L4-conventions/financial-calculation-standards.md
        """
        return round(dollars * 100)

    ...
```

## 8.3 Adapter Rules

| Rule | Description |
|------|-------------|
| **AD-001** | Provider-specific code lives ONLY in adapter files |
| **AD-002** | Adapters translate to canonical models at the boundary |
| **AD-003** | No provider-specific types leak into service code |
| **AD-004** | Each adapter handles its own rate limiting |
| **AD-005** | Each adapter handles its own retry logic (max 2 retries) |
| **AD-006** | Each adapter implements `health_check()` |
| **AD-007** | Adding a new provider = one new adapter file, zero changes elsewhere |

---

# 9. DEPENDENCY INJECTION

## 9.1 Constructor Injection (Mandatory)

All dependencies are injected through the constructor. No service creates
its own dependencies.

```python
# ✓ CORRECT — dependencies injected
class ResearchService:
    def __init__(
        self,
        data_service: MarketDataService,
        thesis_repository: ThesisRepository,
        llm_gateway: LLMGateway,
        event_bus: EventBus,
    ) -> None:
        self._data_service = data_service
        self._thesis_repository = thesis_repository
        self._llm_gateway = llm_gateway
        self._event_bus = event_bus

# ✗ WRONG — service creates its own dependencies
class ResearchService:
    def __init__(self) -> None:
        self._data_service = MarketDataService()
        self._thesis_repository = ThesisRepository(get_db_connection())
```

## 9.2 Composition Root

All dependency wiring happens in a single place — the composition root:

```python
# src/main.py (or src/container.py)

def create_application() -> Application:
    """Composition root — wire all dependencies here.

    This is the ONLY place where concrete implementations are
    instantiated and connected. All other code works with
    interfaces/protocols.
    """
    config = load_config()

    # ── Infrastructure ──
    db = create_database(config.database)
    event_bus = InMemoryEventBus()
    http_client = create_http_client(config.http)

    # ── Data Engine ──
    fmp_adapter = FmpAdapter(
        api_key=config.fmp_api_key,
    )
    ingestion_repository = IngestionRepository(db=db)
    ingestion_service = IngestionService(
        primary_provider=fmp_adapter,
        fallback_provider=edgar_adapter,
        repository=ingestion_repository,
        event_bus=event_bus,
    )

    # ── Continue for all services ──
    ...

    return Application(
        ingestion_service=ingestion_service,
        ...
    )
```

---

# 10. IMPORT STANDARDS

## 10.1 Import Order

Imports are organized into **five groups**, separated by blank lines:

```python
# Group 1: Standard library
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import TypeAlias, Protocol

# Group 2: Third-party packages
import structlog
import pandas as pd
from pydantic import BaseModel, Field

# Group 3: Project infrastructure and shared
from src.shared.types import Result, Success, Failure
from src.shared.errors import DomainError
from src.shared.interfaces import EventBus

# Group 4: Same-domain imports (other modules in same domain)
from src.data_engine.storage.repository import StorageRepository

# Group 5: Current module relative imports
from .models import OHLCVBar, IngestionResult
from .errors import DataFetchError
from .interfaces import MarketDataProvider
```

## 10.2 Import Rules

| Rule | Description |
|------|-------------|
| **IM-001** | Always use absolute imports from `src.` root |
| **IM-002** | Relative imports (`.`) allowed ONLY within same module |
| **IM-003** | Never use wildcard imports (`from module import *`) |
| **IM-004** | Never import a private member (`_name`) from another module |
| **IM-005** | Import specific names, not entire modules (unless the module IS the interface, e.g., `import pandas as pd`) |
| **IM-006** | Cross-domain imports must go through the domain's `__init__.py` public API |

## 10.3 Cross-Domain Import Example

```python
# ✓ CORRECT — imports through public API
from src.data_engine import MarketDataService, OHLCVBar

# ✗ WRONG — reaches into internal module structure
from src.data_engine.ingestion.service import IngestionService
from src.data_engine.ingestion.models import OHLCVBar

# The domain's __init__.py controls what is public:
# src/data_engine/__init__.py
from src.data_engine.ingestion.service import IngestionService as MarketDataService
from src.data_engine.ingestion.models import OHLCVBar

__all__ = ["MarketDataService", "OHLCVBar"]
```

---

# 11. ASYNC STANDARDS

## 11.1 Async Rules

```python
# ── Default to async for I/O operations ──
# All functions that perform I/O (network, disk, database) must be async.

# ── CPU-bound work stays synchronous ──
# Technical indicator calculations, financial math = sync functions.

# ── Never mix sync and async I/O ──
# Don't call synchronous blocking I/O inside an async function.

# ✓ CORRECT
async def fetch_and_store(ticker: str) -> Result[int, DataError]:
    data = await self._provider.fetch(ticker)       # async I/O
    score = calculate_momentum_score(data.value)     # sync CPU
    await self._repository.store(ticker, score)      # async I/O
    return Success(score)

# ✗ WRONG — blocking I/O in async context
async def fetch_and_store(ticker: str):
    data = requests.get(f"https://api.example.com/{ticker}")  # BLOCKING!
    ...
```

## 11.2 Concurrency Patterns

```python
import asyncio

# ── Batch concurrent operations with controlled concurrency ──
async def ingest_watchlist(
    tickers: list[str],
    max_concurrent: int = 10,
) -> list[Result[IngestionResult, DataFetchError]]:
    """Ingest data for all watchlist tickers with bounded concurrency."""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def _limited_ingest(ticker: str):
        async with semaphore:
            return await self.ingest_daily_ohlcv(ticker, date.today())

    tasks = [_limited_ingest(ticker) for ticker in tickers]
    return await asyncio.gather(*tasks)
```

---

# 12. LOGGING STANDARDS

## 12.1 Logger Setup

The project uses `structlog` for structured, JSON-compatible logging.

```python
import structlog

# ── One logger per module ──
logger = structlog.get_logger(__name__)

# ── Bind context at the service level ──
class SomeService:
    def __init__(self, ...) -> None:
        self._logger = logger.bind(service="SomeService")

    async def some_method(self, ticker: str) -> ...:
        # Bind per-operation context
        log = self._logger.bind(ticker=ticker, operation="some_method")
        log.info("Operation started")
        ...
        log.info("Operation completed", duration_ms=elapsed)
```

## 12.2 Log Levels

| Level      | Use For                                         | Example                              |
|------------|-------------------------------------------------|--------------------------------------|
| `DEBUG`    | Detailed internal state, data dumps             | Raw API response body                |
| `INFO`     | Normal operations, milestones                   | "Ingested 200 bars for AAPL"         |
| `WARNING`  | Recoverable issues, fallbacks triggered         | "Primary provider failed, using fallback" |
| `ERROR`    | Operation failed, requires attention            | "All providers failed for TSLA"      |
| `CRITICAL` | System-level failure, pipeline halted           | "Database connection lost"           |

## 12.3 Mandatory Log Points

Every service method must log:

```python
async def process_something(self, input: InputType) -> Result:
    log = self._logger.bind(operation="process_something", **key_context)

    # ── ALWAYS log entry ──
    log.info("Starting operation")

    # ── ALWAYS log the outcome ──
    if result.is_success:
        log.info("Operation succeeded", **outcome_metrics)
    else:
        log.error("Operation failed", error_code=result.error.code)

    # ── ALWAYS log duration for operations > trivial ──
    log.info("Operation completed", duration_ms=elapsed_ms)
```

## 12.4 Logging Prohibitions

| Rule | Description |
|------|-------------|
| **LG-001** | NEVER log API keys, tokens, passwords, or credentials |
| **LG-002** | NEVER log full API response bodies at INFO level (use DEBUG) |
| **LG-003** | NEVER use `print()` — always use structlog |
| **LG-004** | NEVER log at ERROR level for expected business failures (use WARNING) |
| **LG-005** | NEVER log personally identifiable information |
| **LG-006** | ALWAYS include `ticker` in log context when operating on a specific stock |

---

# 13. CONFIGURATION MANAGEMENT

## 13.1 Configuration Hierarchy

```text
Precedence (highest to lowest):
1. Environment variables         (secrets, deployment-specific)
2. Config file (environment)     (config/production.yaml)
3. Config file (default)         (config/default.yaml)
4. Code defaults                 (hardcoded fallback — last resort)
```

## 13.2 Configuration Model

```python
# src/config/models.py

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "investment_pipeline"
    pool_size_min: int = 2
    pool_size_max: int = 10


class DataProviderConfig(BaseModel):
    primary: str = "polygon"
    fallback: str = "alpha_vantage"
    rate_limit_buffer_pct: float = 20.0


class GuardrailConfig(BaseModel):
    max_position_pct: float = 15.0
    concentration_threshold_pct: float = 25.0
    sector_max_pct: float = 35.0
    drawdown_alert_pct: float = 10.0
    drawdown_critical_pct: float = 20.0
    correlation_alert: float = 0.85


class AgentConfig(BaseModel):
    confidence_floor: float = 0.3
    confidence_hold_cap: float = 0.5
    max_latency_seconds: int = 180
    retry_max: int = 2


class AppConfig(BaseSettings):
    """Root configuration — assembled from files + environment.

    Environment variables override file values using the prefix
    INVEST_ (e.g., INVEST_DATABASE__HOST=myhost).
    """

    database: DatabaseConfig = DatabaseConfig()
    data_provider: DataProviderConfig = DataProviderConfig()
    guardrails: GuardrailConfig = GuardrailConfig()
    agents: AgentConfig = AgentConfig()

    # Secrets — only from environment variables
    fmp_api_key: str = Field(default="", description="FMP.io API key")
    llm_api_key: str = Field(default="", description="LLM provider API key")

    class Config:
        env_prefix = "INVEST_"
        env_nested_delimiter = "__"
```

## 13.3 Configuration Rules

| Rule | Description |
|------|-------------|
| **CF-001** | Secrets (API keys, passwords) ONLY from environment variables, never in config files |
| **CF-002** | Every configurable value must have a sensible default |
| **CF-003** | Configuration is loaded ONCE at startup and injected via DI |
| **CF-004** | Modules never read config directly — they receive values through constructor |
| **CF-005** | `.env` files are gitignored; `.env.example` is committed with placeholder values |
| **CF-006** | Guardrail configuration changes must be logged to audit trail |

---

# 14. CONSTANTS & MAGIC NUMBERS

## 14.1 No Magic Numbers Rule

```python
# ✗ WRONG — magic numbers
if position_pct > 15.0:
    alert()
if len(history) < 252:
    return None

# ✓ CORRECT — named constants from config or module constants
from src.config import AppConfig

if position_pct > config.guardrails.max_position_pct:
    alert()

# Or from module constants for domain-specific values:
TRADING_DAYS_PER_YEAR: int = 252
MINIMUM_HISTORY_DAYS: int = TRADING_DAYS_PER_YEAR  # 1 year minimum

if len(history) < MINIMUM_HISTORY_DAYS:
    return None
```

## 14.2 System-Wide Constants

```python
# src/shared/constants/markets.py

"""Constants related to US equity markets.

These values are facts, not configuration. They change only when
market structure changes (extremely rarely). If a value might need
tuning, it belongs in configuration, not here.
"""

TRADING_DAYS_PER_YEAR: int = 252
TRADING_HOURS_START_ET: str = "09:30"
TRADING_HOURS_END_ET: str = "16:00"
PRE_MARKET_START_ET: str = "04:00"
AFTER_HOURS_END_ET: str = "20:00"

# Standard index tickers
INDEX_SP500: str = "SPY"
INDEX_NASDAQ: str = "QQQ"
INDEX_RUSSELL2000: str = "IWM"
INDEX_VIX: str = "VIX"

# Penny stock threshold (per L0 exclusion rules)
PENNY_STOCK_PRICE_CENTS: int = 500        # $5.00
PENNY_STOCK_MARKET_CAP_CENTS: int = 50_000_000_000  # $500M in cents

# GICS Sector codes
GICS_SECTORS: dict[str, str] = {
    "10": "Energy",
    "15": "Materials",
    "20": "Industrials",
    "25": "Consumer Discretionary",
    "30": "Consumer Staples",
    "35": "Health Care",
    "40": "Financials",
    "45": "Information Technology",
    "50": "Communication Services",
    "55": "Utilities",
    "60": "Real Estate",
}
```

---

# 15. REPOSITORY PATTERN — Data Access

## 15.1 Standard Repository Structure

```python
# src/data_engine/ingestion/repository.py

import structlog
from datetime import date
from src.infrastructure.database import Database


logger = structlog.get_logger(__name__)


class IngestionRepository:
    """Data access layer for OHLCV market data storage.

    Responsibilities:
        - Read/write OHLCV bars to persistent storage
        - Handle query construction and parameter binding
        - Map between database rows and domain models

    Does NOT contain:
        - Business logic
        - Validation logic
        - External API calls
    """

    def __init__(self, db: Database) -> None:
        self._db = db
        self._logger = logger.bind(repository="IngestionRepository")

    async def store_bars(self, bars: list[OHLCVBar]) -> int:
        """Store OHLCV bars. Returns count of bars stored.

        Uses upsert semantics — existing bars for the same
        ticker+date are updated, not duplicated.
        """
        ...

    async def get_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list[OHLCVBar]:
        """Retrieve stored OHLCV bars for a ticker and date range.

        Returns empty list if no bars found. Never returns None.
        Bars are returned in chronological order (ascending date).
        """
        ...

    async def get_latest_bar(self, ticker: str) -> OHLCVBar | None:
        """Get the most recent bar for a ticker, or None if no data."""
        ...

    async def get_last_ingestion_date(self, ticker: str) -> date | None:
        """Get the date of the most recent ingestion for staleness checking."""
        ...
```

## 15.2 Repository Rules

| Rule | Description |
|------|-------------|
| **RP-001** | Repositories handle ONLY data access — no business logic |
| **RP-002** | One repository per aggregate root / primary entity |
| **RP-003** | Repositories return domain models, not raw dicts or DB rows |
| **RP-004** | Collections return empty list (not None) when nothing found |
| **RP-005** | Single items return `T | None` when item may not exist |
| **RP-006** | All queries must use parameterized inputs (no SQL injection) |
| **RP-007** | Repository methods are named: `get_`, `find_`, `store_`, `delete_`, `exists_`, `count_` |

---

# 16. EVENT SYSTEM

## 16.1 Event Naming Convention

Events follow the pattern: `domain.module.action_past_tense`

```python
# ── Event name examples ──
"data.ingestion.completed"
"data.ingestion.failed"
"data.validation.anomaly_detected"
"research.thesis.created"
"research.thesis.updated"
"research.report.generated"
"quant.signal.buy_triggered"
"quant.signal.sell_triggered"
"quant.scoring.completed"
"portfolio.position.opened"
"portfolio.position.closed"
"portfolio.rebalance.recommended"
"risk.guardrail.breached"
"risk.drawdown.threshold_hit"
"orchestration.pipeline.started"
"orchestration.pipeline.completed"
"orchestration.pipeline.failed"
```

## 16.2 Event Payload Structure

```python
# src/shared/interfaces/events.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DomainEvent(BaseModel):
    """Base event structure for all domain events."""

    event_name: str = Field(..., description="Dot-separated event identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    source_module: str = Field(..., description="Module that emitted event")
    correlation_id: str = Field(
        default="",
        description="ID to trace related events across a pipeline run",
    )
    payload: dict = Field(
        default_factory=dict,
        description="Event-specific data",
    )

    class Config:
        frozen = True
```

---

# 17. PANDAS & DATAFRAME CONVENTIONS

Given the financial data nature of this project, pandas DataFrames are
used extensively. These conventions prevent common mistakes.

## 17.1 DataFrame Rules

```python
import pandas as pd
import numpy as np

# ── Always use explicit dtypes ──
# ✓ CORRECT
df = pd.DataFrame({
    "ticker": pd.array(["AAPL", "MSFT"], dtype="string"),
    "close_cents": pd.array([15099, 42050], dtype="int64"),
    "volume": pd.array([1000000, 2000000], dtype="int64"),
    "date": pd.to_datetime(["2025-01-14", "2025-01-14"]),
})

# ✗ WRONG — implicit dtypes
df = pd.DataFrame({
    "ticker": ["AAPL", "MSFT"],
    "close": [150.99, 420.50],   # float dollars! BAD!
})


# ── Never modify DataFrames in place (use .copy()) ──
# ✓ CORRECT
filtered_df = df[df["volume"] > 500000].copy()
filtered_df["avg_price_cents"] = (
    (filtered_df["high_cents"] + filtered_df["low_cents"]) // 2
)

# ✗ WRONG — modifying a view (SettingWithCopyWarning)
filtered_df = df[df["volume"] > 500000]
filtered_df["avg_price_cents"] = ...


# ── Always sort and reset index after filtering ──
result_df = (
    df[df["volume"] > min_volume]
    .sort_values("date", ascending=True)
    .reset_index(drop=True)
)


# ── Use .loc / .iloc, never chained indexing ──
# ✓ CORRECT
value = df.loc[df["ticker"] == "AAPL", "close_cents"].iloc[0]

# ✗ WRONG — chained indexing
value = df[df["ticker"] == "AAPL"]["close_cents"][0]
```

## 17.2 DataFrame Naming

```python
# ── Variable naming for DataFrames ──
ohlcv_df: pd.DataFrame          # suffix with _df
returns_series: pd.Series       # suffix with _series
prices_index: pd.Index          # suffix with _index

# ── Column naming in DataFrames: snake_case, same as Python variables ──
# Required columns in OHLCV DataFrames:
OHLCV_COLUMNS: list[str] = [
    "ticker",
    "date",
    "open_cents",
    "high_cents",
    "low_cents",
    "close_cents",
    "volume",
]
```

## 17.3 DataFrame Function Signatures

```python
def calculate_moving_average(
    prices_df: pd.DataFrame,
    column: str,
    window: int,
) -> pd.Series:
    """Calculate simple moving average for a column.

    Args:
        prices_df: DataFrame with at least the specified column.
            Must be sorted by date ascending.
        column: Name of the column to average.
        window: Lookback period in rows (typically trading days).

    Returns:
        Series of same length as input with MA values.
        First (window - 1) values will be NaN.

    Raises:
        KeyError: If column not in DataFrame.
        ValueError: If window < 1 or window > len(prices_df).
    """
    if column not in prices_df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    if window < 1 or window > len(prices_df):
        raise ValueError(
            f"Window must be between 1 and {len(prices_df)}, got {window}"
        )

    return prices_df[column].rolling(window=window).mean()
```

---

# 18. CODE ORGANIZATION RULES

## 18.1 File Length Limits

| File Type                  | Soft Limit | Hard Limit | Action at Hard Limit       |
|----------------------------|------------|------------|----------------------------|
| Service class              | 200 lines  | 300 lines  | Split into sub-services    |
| Repository class           | 150 lines  | 250 lines  | Split by entity/query type |
| Model definitions          | 200 lines  | 400 lines  | Split into sub-model files |
| Adapter                    | 150 lines  | 250 lines  | Extract shared utilities   |
| Test file                  | 300 lines  | 500 lines  | Split by test category     |
| Utility/helper file        | 100 lines  | 200 lines  | Split by function group    |
| Constants file             | 100 lines  | 200 lines  | Split by category          |

## 18.2 Class Rules

| Rule | Description |
|------|-------------|
| **CL-001** | One primary class per file (helper/private classes in same file OK) |
| **CL-002** | Class name matches file name: `MarketDataService` → `market_data_service.py` |
| **CL-003** | Max 10 public methods per class |
| **CL-004** | Max 6 constructor parameters (use config objects for more) |
| **CL-005** | All instance attributes set in `__init__` (no lazy attributes) |
| **CL-006** | Private methods prefixed with `_`, placed below public methods |
| **CL-007** | No inheritance deeper than 2 levels; prefer composition |
| **CL-008** | No `@staticmethod` that needs instance state — use regular method |

## 18.3 Method Ordering Within a Class

```python
class SomeService:
    # 1. __init__
    def __init__(self, ...) -> None: ...

    # 2. Public methods (in order of importance / usage frequency)
    async def primary_operation(self, ...) -> ...: ...
    async def secondary_operation(self, ...) -> ...: ...
    def query_method(self, ...) -> ...: ...

    # 3. Properties
    @property
    def is_healthy(self) -> bool: ...

    # 4. Private methods (in call order from public methods)
    def _validate_input(self, ...) -> ...: ...
    async def _execute_step_one(self, ...) -> ...: ...
    async def _execute_step_two(self, ...) -> ...: ...

    # 5. Static/class methods
    @staticmethod
    def _helper_function(...) -> ...: ...

    # 6. Dunder methods (other than __init__)
    def __repr__(self) -> str: ...
```

---

# 19. COMMENTING STANDARDS

## 19.1 When to Comment

```python
# ── ALWAYS comment: ──

# Business rule justification
# Orders older than 30 days cannot be modified (BR-003)
if (datetime.now(timezone.utc) - order.created_at).days > 30:
    return Failure(OrderError(code="ORDER_TOO_OLD", ...))

# Non-obvious "why" (the code shows "what", the comment explains "why")
# We use T+2 settlement, so the effective date is 2 business days ahead
effective_date = next_business_day(next_business_day(trade_date))

# Financial formula source
# Sharpe Ratio = (Rp - Rf) / σp
# Annualized by multiplying by √(periods_per_year)
# Source: "Investments" by Bodie, Kane, Marcus, Ch. 6

# Workarounds with ticket/issue reference
# WORKAROUND: Polygon API returns timestamps in ms, not seconds
# See: https://github.com/your-repo/issues/42
timestamp = raw_timestamp / 1000

# Performance-critical decisions
# Using numpy vectorized operations instead of loop for 10x speedup
# on watchlists > 100 tickers
returns = np.diff(prices) / prices[:-1]


# ── NEVER comment: ──

# Restating the code
count = count + 1  # increment count by 1  ← USELESS

# Commented-out code (delete it, git has history)
# old_method()  ← DELETE THIS

# TODO without a ticket reference
# TODO: fix this later  ← USELESS, will be forgotten
# TODO(ISSUE-123): Handle edge case for delisted tickers  ← OK
```

## 19.2 Comment Style

```python
# ── Single-line comments: space after # ──
# This is correct.
#This is wrong.

# ── Block comments for sections within long functions ──
# ── Step 1: Validate inputs ──
...

# ── Step 2: Fetch data ──
...

# ── Multi-line comments for complex explanations ──
# The Kelly Criterion suggests optimal bet sizing as:
# f* = (bp - q) / b
# where b = odds, p = win probability, q = 1 - p
# We use a half-Kelly (f*/2) to be more conservative.
```

---

# 20. GIT CONVENTIONS

## 20.1 Branch Naming

```text
feature/PHASE-N/short-description     feature/PHASE-1/market-data-ingestion
bugfix/short-description               bugfix/polygon-rate-limit-handling
refactor/short-description             refactor/extract-adapter-base-class
spec/spec-name                         spec/L2-market-data-ingestion
chore/short-description                chore/update-dependencies
```

## 20.2 Commit Message Format

```text
type(scope): short description (max 72 chars)

Longer description if needed. Wrap at 80 characters.
Explain WHAT changed and WHY, not HOW (the diff shows HOW).

Refs: ISSUE-123
Spec: L2-modules/data-engine/market-data-ingestion.md
Breaking: description of breaking change (if any)
```

**Types:**
| Type       | Use For                                    |
|------------|--------------------------------------------|
| `feat`     | New feature or capability                  |
| `fix`      | Bug fix                                    |
| `refactor` | Code restructuring (no behavior change)    |
| `test`     | Adding or updating tests                   |
| `spec`     | Adding or updating specification documents |
| `docs`     | Documentation updates                      |
| `chore`    | Dependencies, config, build tooling        |
| `perf`     | Performance improvement                    |

**Examples:**
```text
feat(data-engine): add Polygon adapter for daily OHLCV ingestion

Implements the MarketDataProvider protocol for Polygon.io API.
Handles rate limiting (5 req/min on free tier), pagination,
and translation to canonical OHLCVBar format.

Spec: L2-modules/data-engine/market-data-ingestion.md
Refs: ISSUE-15

---

fix(data-engine): handle Polygon API returning null volume for pre-market

Polygon occasionally returns null for volume on pre-market bars.
Previously this caused a ValidationError. Now we default to 0
and flag the bar with source_note="volume_missing".

Refs: ISSUE-42
```

## 20.3 Gitignore Essentials

```text
# ── Always ignore ──
.env
*.pyc
__pycache__/
.venv/
venv/
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
coverage/
htmlcov/
.coverage

# ── Project-specific ──
config/local.yaml
data/                     # Local data files (large)
*.db                      # SQLite files
logs/
```

---

# 21. TOOL CONFIGURATION

## 21.1 Required Tools

| Tool         | Purpose              | Configuration File     |
|--------------|----------------------|------------------------|
| `ruff`       | Linting + formatting | `pyproject.toml`       |
| `mypy`       | Type checking        | `pyproject.toml`       |
| `pytest`     | Testing              | `pyproject.toml`       |
| `pre-commit` | Git hook automation  | `.pre-commit-config.yaml` |

## 21.2 Ruff Configuration

```toml
# pyproject.toml

[tool.ruff]
target-version = "py311"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort (import sorting)
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # Ruff-specific rules
    "PT",   # flake8-pytest-style
    "RET",  # flake8-return
    "ARG",  # flake8-unused-arguments
    "C4",   # flake8-comprehensions
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["src"]
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## 21.3 Mypy Configuration

```toml
# pyproject.toml

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_unreachable = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

## 21.4 Pytest Configuration

```toml
# pyproject.toml

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-fail-under=70",
]
markers = [
    "unit: Unit tests (no external dependencies)",
    "integration: Integration tests (may use DB/network)",
    "slow: Tests that take > 5 seconds",
    "financial: Tests verifying financial calculations",
]
```

---

# 22. PRE-COMMIT CHECKS

All code must pass these checks before commit:

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: ruff-lint
        name: Ruff Lint
        entry: ruff check --fix
        language: system
        types: [python]

      - id: ruff-format
        name: Ruff Format
        entry: ruff format
        language: system
        types: [python]

      - id: mypy
        name: Mypy Type Check
        entry: mypy
        language: system
        types: [python]
        pass_filenames: false

      - id: pytest-unit
        name: Unit Tests
        entry: pytest tests/unit -x --no-header -q
        language: system
        pass_filenames: false
        stages: [pre-push]

      - id: no-secrets
        name: Check for Secrets
        entry: grep -rn "api_key\s*=\s*['\"][^'\"]*['\"]" --include="*.py"
        language: system
        types: [python]
        pass_filenames: false
```

---

# 23. MAKEFILE — Standard Commands

```makefile
# Makefile

.PHONY: help install lint format typecheck test test-unit test-integration run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e ".[dev]"
	pre-commit install

lint: ## Run linter
	ruff check src/ tests/

format: ## Format code
	ruff format src/ tests/

typecheck: ## Run type checker
	mypy src/

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit -v

test-integration: ## Run integration tests only
	pytest tests/integration -v

test-financial: ## Run financial calculation tests
	pytest -m financial -v

run: ## Start the application
	python -m src.main

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info/

check: lint typecheck test-unit ## Run all checks (pre-commit equivalent)
```

---

# 24. CHECKLIST FOR AI CODING AGENTS

When an AI agent is generating code for this project, it must verify:

```text
□ File is in the correct location per project structure (Section 1)
□ File name follows snake_case convention (Section 2.1)
□ All names follow naming conventions (Section 2)
□ All functions have complete type hints (Section 3.1)
□ All data models use Pydantic BaseModel (Section 3.3)
□ All monetary values use integer cents (Section 2.3)
□ No function exceeds 40 lines (Section 4.1)
□ No function has > 4 parameters without options object (Section 4.1)
□ All public functions have Google-style docstrings (Section 4.2)
□ Service methods follow the 7-step flow (Section 7.2)
□ Result type used for fallible operations (Section 5)
□ Error classes follow hierarchy and code convention (Section 6)
□ External systems accessed only through adapter pattern (Section 8)
□ Dependencies injected via constructor (Section 9)
□ Imports follow 5-group ordering (Section 10)
□ I/O operations are async (Section 11)
□ Logging uses structlog with proper levels (Section 12)
□ No magic numbers (Section 14)
□ Repository methods return domain models not dicts (Section 15)
□ DataFrames follow pandas conventions (Section 17)
□ No file exceeds hard line limit (Section 18.1)
□ Comments explain "why", not "what" (Section 19)
□ Code passes ruff, mypy, and pytest (Section 21-22)
```

---

# 25. CROSS-REFERENCES

| Document                                | Location                                              |
|-----------------------------------------|-------------------------------------------------------|
| L0: System Vision                       | `specs/L0-system-vision.md`                           |
| L4: Financial Calculation Standards     | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: AI Agent Design Standards           | `specs/L4-conventions/ai-agent-design-standards.md`   |
| L4: Data Pipeline Standards             | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Testing Standards                   | `specs/L4-conventions/testing-standards.md`           |
| L4: Error Handling (deep dive)          | `specs/L4-conventions/error-handling.md`              |
| Guardrails: Financial                   | `specs/guardrails/financial-guardrails.md`            |
| Guardrails: Data Quality                | `specs/guardrails/data-quality-guardrails.md`         |

---
```
