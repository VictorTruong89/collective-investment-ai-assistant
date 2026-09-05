## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines how all code in the AI Investment Pipeline is tested.
Testing is not optional. Testing is not an afterthought. Testing is the
mechanism that makes spec-driven development trustworthy — the spec defines
what the code *should* do, the tests *prove* that it does.

In a financial system, the cost of undetected bugs is measured in real
capital losses, corrupted analyses, and eroded trust in the pipeline's
recommendations. The testing standards here are calibrated to that reality.

**Every developer and every AI coding agent** must follow these standards.
When an AI agent generates code, it must also generate the corresponding
tests. Code without tests is considered incomplete.

## Scope

| In Scope                                        | Out of Scope                          |
|-------------------------------------------------|---------------------------------------|
| Unit testing standards and patterns              | Production monitoring and alerting    |
| Integration testing standards                    | Chaos engineering                     |
| Financial calculation verification testing       | Performance benchmarking infrastructure|
| AI agent output validation testing               | Security penetration testing          |
| Data pipeline and ingestion testing              | UI/frontend testing                   |
| Test fixture and mock management                 | Load testing at scale                 |
| Coverage requirements and enforcement            |                                       |
| Regression testing strategy                      |                                       |

## Relationship to Other Standards

| Document                              | Relationship                                     |
|---------------------------------------|--------------------------------------------------|
| `L4-conventions/coding-standards.md`  | Test file naming, structure, and location         |
| `L4-conventions/financial-calculation-standards.md` | Elevated testing requirements for financial code (Section 14) |
| `L4-conventions/error-handling.md`    | How errors are surfaced and tested                |
| `guardrails/data-quality-guardrails.md` | Data quality rules that tests must verify       |
| `guardrails/ai-output-guardrails.md`  | AI output validation rules that tests must verify |

---

# 1. TESTING PHILOSOPHY

## 1.1 Core Principles

```text
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   PRINCIPLE 1: Tests are the executable specification.            ║
║   If the spec says a function does X, a test proves it does X.   ║
║                                                                   ║
║   PRINCIPLE 2: Tests run fast or they won't run.                 ║
║   Unit tests < 100ms each. Integration tests < 5s each.         ║
║                                                                   ║
║   PRINCIPLE 3: Tests are deterministic or they are worthless.    ║
║   A test that passes 99% of the time is a test that lies.       ║
║                                                                   ║
║   PRINCIPLE 4: Tests document intent.                            ║
║   A well-named test is better documentation than a comment.      ║
║                                                                   ║
║   PRINCIPLE 5: Tests catch regressions, not just bugs.           ║
║   Every bug fix includes a test that would have caught it.       ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

## 1.2 The Testing Pyramid for This Project

```text
                    ╱  ╲
                   ╱ E2E ╲                    Rare, expensive
                  ╱ Tests  ╲                  Pipeline workflows
                 ╱──────────╲                 (Phase 5+)
                ╱            ╲
               ╱ Integration  ╲               Moderate count
              ╱    Tests       ╲              DB, APIs, LLM
             ╱──────────────────╲
            ╱                    ╲
           ╱     Unit Tests       ╲           Large count,
          ╱                        ╲          fast, isolated
         ╱──────────────────────────╲
        ╱                            ╲
       ╱   Financial Verification     ╲       Cross-cutting,
      ╱        Tests                   ╲      high priority
     ╱──────────────────────────────────╲

     Target Distribution:
     ├── Unit Tests:                70% of test count
     ├── Financial Verification:    15% (cross-cutting, run as unit)
     ├── Integration Tests:         12%
     └── E2E / Pipeline Tests:       3%
```

## 1.3 What Gets Tested

| Component Type              | Testing Requirement                          | Level            |
|-----------------------------|----------------------------------------------|------------------|
| Financial calculations      | Mandatory, elevated standards (see Section 7) | Unit + Financial |
| Service layer (business logic) | Mandatory                                 | Unit             |
| Repository layer (data access) | Mandatory                                 | Integration      |
| Adapters (external providers)  | Mandatory                                 | Unit (mocked) + Integration (optional) |
| Pydantic models (validation)  | Mandatory                                  | Unit             |
| Error handling paths          | Mandatory                                   | Unit             |
| Configuration loading         | Mandatory                                   | Unit             |
| AI agent prompt → output      | Mandatory (Phase 2+)                        | Integration      |
| Pipeline orchestration        | Mandatory (Phase 5+)                        | E2E              |
| Utility / helper functions    | Mandatory                                   | Unit             |
| Constants and enums           | Not required (verified by type checker)     | —                |

---

# 2. TEST ORGANIZATION

## 2.1 Directory Structure

Tests mirror the `src/` structure exactly:

```text
tests/
├── conftest.py                          # Root-level shared fixtures
│
├── unit/                                # All unit tests
│   ├── conftest.py                      # Unit-level shared fixtures
│   ├── shared/
│   │   ├── utils/
│   │   │   ├── test_money.py
│   │   │   ├── test_returns.py
│   │   │   ├── test_risk_metrics.py
│   │   │   ├── test_ratios.py
│   │   │   ├── test_formatting.py
│   │   │   └── test_comparison.py
│   │   ├── errors/
│   │   │   └── test_error_hierarchy.py
│   │   └── types/
│   │       └── test_result.py
│   │
│   ├── data_engine/
│   │   ├── conftest.py                  # Domain-level fixtures
│   │   ├── ingestion/
│   │   │   ├── test_ingestion_service.py
│   │   │   ├── test_polygon_adapter.py
│   │   │   ├── test_alpha_vantage_adapter.py
│   │   │   └── test_ohlcv_validation.py
│   │   └── storage/
│   │       └── test_storage_service.py
│   │
│   ├── quantitative/
│   │   ├── indicators/
│   │   │   ├── test_moving_averages.py
│   │   │   ├── test_bollinger_bands.py
│   │   │   ├── test_rsi.py
│   │   │   └── test_macd.py
│   │   ├── signals/
│   │   │   └── test_signal_generation.py
│   │   └── scoring/
│   │       └── test_scoring_model.py
│   │
│   ├── portfolio/
│   │   ├── test_portfolio_return.py
│   │   ├── test_portfolio_volatility.py
│   │   └── test_position_sizing.py
│   │
│   ├── risk/
│   │   ├── test_var.py
│   │   ├── test_drawdown.py
│   │   └── test_correlation.py
│   │
│   └── research/
│       ├── test_screener.py
│       └── test_earnings_analyzer.py
│
├── integration/                         # Tests with real I/O
│   ├── conftest.py                      # Integration fixtures (DB, etc.)
│   ├── data_engine/
│   │   ├── test_ingestion_repository.py
│   │   ├── test_polygon_live.py         # Real API (rate-limited)
│   │   └── test_data_pipeline.py
│   ├── research/
│   │   └── test_research_agent.py       # Real LLM calls
│   └── infrastructure/
│       ├── test_database.py
│       └── test_cache.py
│
├── e2e/                                 # End-to-end pipeline tests
│   ├── test_daily_scan_pipeline.py
│   └── test_research_pipeline.py
│
├── fixtures/                            # Shared test data
│   ├── market_data/
│   │   ├── aapl_daily_2024.json
│   │   ├── msft_daily_2024.json
│   │   └── spy_daily_2024.json
│   ├── financial_statements/
│   │   ├── aapl_income_2024.json
│   │   └── aapl_balance_sheet_2024.json
│   ├── financial/                       # Financial calculation test vectors
│   │   ├── sma_test_vectors.py
│   │   ├── ema_test_vectors.py
│   │   ├── sharpe_test_vectors.py
│   │   └── var_test_vectors.py
│   ├── api_responses/                   # Recorded API responses
│   │   ├── polygon/
│   │   │   ├── daily_bars_aapl.json
│   │   │   └── error_rate_limited.json
│   │   └── alpha_vantage/
│   │       └── daily_bars_aapl.json
│   └── agent_outputs/                   # Reference AI agent outputs
│       ├── research_report_aapl.json
│       └── risk_report_portfolio.json
│
└── helpers/                             # Test utility functions
    ├── __init__.py
    ├── factories.py                     # Test object factories
    ├── assertions.py                    # Custom assertion helpers
    ├── generators.py                    # Random data generators
    └── time_helpers.py                  # Time manipulation utilities
```

## 2.2 File Mapping Rules

| Rule | Description |
|------|-------------|
| **TO-001** | Every `src/` module file has a corresponding `tests/unit/` test file |
| **TO-002** | Test file name = `test_` + source file name: `service.py` → `test_service.py` |
| **TO-003** | Test directory structure mirrors source directory structure exactly |
| **TO-004** | Each domain has its own `conftest.py` for domain-specific fixtures |
| **TO-005** | Shared fixtures live in `tests/conftest.py` or `tests/unit/conftest.py` |
| **TO-006** | Test data files live in `tests/fixtures/`, never inline in test files for large datasets |
| **TO-007** | Test helpers live in `tests/helpers/`, imported like any module |

---

# 3. TEST NAMING AND STRUCTURE

## 3.1 Test Naming Convention

Every test follows this pattern:

```python
def test_<what_is_being_tested>_<condition>_<expected_outcome>():
```

Or using the `should/when` pattern:

```python
def test_<method>_should_<expected>_when_<condition>():
```

```python
# ── GOOD test names — self-documenting ──

def test_simple_return_calculates_correctly_for_positive_move():
def test_simple_return_calculates_correctly_for_negative_move():
def test_simple_return_raises_value_error_for_single_price():
def test_simple_return_raises_value_error_for_zero_price():

def test_fetch_daily_ohlcv_should_return_bars_when_provider_succeeds():
def test_fetch_daily_ohlcv_should_use_fallback_when_primary_fails():
def test_fetch_daily_ohlcv_should_return_failure_when_all_providers_fail():
def test_fetch_daily_ohlcv_should_return_failure_when_ticker_invalid():

def test_sharpe_ratio_matches_known_value_from_textbook():
def test_sharpe_ratio_returns_none_for_zero_volatility():
def test_sharpe_ratio_is_negative_when_below_risk_free_rate():


# ── BAD test names — unclear intent ──

def test_calculate():           # ✗ What is being calculated?
def test_returns():             # ✗ What about returns?
def test_error():               # ✗ What error? When?
def test_1():                   # ✗ Meaningless
def test_sma_works():           # ✗ "Works" is not specific
```

## 3.2 Test Class Structure

Group tests by the unit under test, using classes:

```python
import pytest
import numpy as np
from src.shared.utils.returns import simple_returns


class TestSimpleReturns:
    """Tests for simple_returns() function.

    Reference: simple_returns computes (P1 - P0) / P0 for each
    consecutive pair in a price series.

    See: L4-conventions/financial-calculation-standards.md Section 2.2
    """

    # ── Happy Path Tests ──

    class TestHappyPath:
        """Standard cases that should succeed."""

        def test_positive_return(self):
            """Stock goes up: $100 → $110 = +10%."""
            prices = np.array([10000, 11000])  # cents
            result = simple_returns(prices)
            assert len(result) == 1
            assert result[0] == pytest.approx(0.10, abs=1e-10)

        def test_negative_return(self):
            """Stock goes down: $100 → $90 = -10%."""
            prices = np.array([10000, 9000])
            result = simple_returns(prices)
            assert result[0] == pytest.approx(-0.10, abs=1e-10)

        def test_zero_return(self):
            """Stock unchanged: $100 → $100 = 0%."""
            prices = np.array([10000, 10000])
            result = simple_returns(prices)
            assert result[0] == pytest.approx(0.0, abs=1e-10)

        def test_multiple_periods(self):
            """Multi-period series returns correct length and values."""
            prices = np.array([100, 110, 104.50, 115])
            result = simple_returns(prices)
            assert len(result) == 3
            assert result[0] == pytest.approx(0.10, abs=1e-6)
            assert result[1] == pytest.approx(-0.05, abs=1e-6)
            assert result[2] == pytest.approx(0.100478, abs=1e-4)

    # ── Edge Cases ──

    class TestEdgeCases:
        """Boundary and unusual inputs."""

        def test_very_small_price_change(self):
            """Penny change on a high-priced stock."""
            prices = np.array([100000, 100001])  # $1000.00 → $1000.01
            result = simple_returns(prices)
            assert result[0] == pytest.approx(0.00001, abs=1e-8)

        def test_large_price_change(self):
            """Stock doubles in one period."""
            prices = np.array([5000, 10000])
            result = simple_returns(prices)
            assert result[0] == pytest.approx(1.0, abs=1e-10)

        def test_minimum_valid_input(self):
            """Exactly 2 prices — minimum valid input."""
            prices = np.array([100, 200])
            result = simple_returns(prices)
            assert len(result) == 1

    # ── Error Cases ──

    class TestErrors:
        """Inputs that should raise exceptions."""

        def test_single_price_raises_value_error(self):
            """Cannot compute return from single price."""
            with pytest.raises(ValueError, match="at least 2 prices"):
                simple_returns(np.array([100]))

        def test_empty_array_raises_value_error(self):
            """Empty array is invalid."""
            with pytest.raises(ValueError, match="at least 2 prices"):
                simple_returns(np.array([]))

        def test_zero_price_raises_value_error(self):
            """Zero price causes division by zero — must reject."""
            with pytest.raises(ValueError, match="positive"):
                simple_returns(np.array([100, 0, 50]))

        def test_negative_price_raises_value_error(self):
            """Negative prices are invalid for equity markets."""
            with pytest.raises(ValueError, match="positive"):
                simple_returns(np.array([100, -50]))

    # ── Property Tests ──

    class TestProperties:
        """Mathematical properties that must hold."""

        def test_return_array_length_is_prices_minus_one(self):
            """Output is always one element shorter than input."""
            for n in [2, 5, 10, 100]:
                prices = np.random.uniform(50, 200, size=n)
                result = simple_returns(prices)
                assert len(result) == n - 1

        def test_round_trip_return_recovers_price(self):
            """Applying returns to start price recovers end price."""
            prices = np.array([100, 110, 104.50, 115.0])
            returns = simple_returns(prices)
            recovered = prices[0]
            for r in returns:
                recovered = recovered * (1 + r)
            assert recovered == pytest.approx(prices[-1], rel=1e-10)
```

## 3.3 Test Structure — Arrange, Act, Assert

Every test follows the AAA pattern with clear visual separation:

```python
def test_ingestion_service_stores_bars_after_successful_fetch(
    self,
    ingestion_service: IngestionService,
    mock_provider: MockMarketDataProvider,
    mock_repository: MockIngestionRepository,
):
    """Service stores validated bars after successful provider fetch."""

    # ── Arrange ──
    ticker = "AAPL"
    target_date = date(2025, 1, 15)
    expected_bars = [
        make_ohlcv_bar(ticker=ticker, date=target_date, close_cents=15099),
    ]
    mock_provider.set_response(ticker, Success(expected_bars))

    # ── Act ──
    result = await ingestion_service.ingest_daily_ohlcv(ticker, target_date)

    # ── Assert ──
    assert result.is_success
    assert result.value.bars_ingested == 1
    mock_repository.store_bars.assert_called_once_with(expected_bars)
```

## 3.4 Test Class Organization Rules

| Rule | Description |
|------|-------------|
| **TN-001** | One test class per public function or method under test |
| **TN-002** | Nest sub-classes for test categories: `TestHappyPath`, `TestEdgeCases`, `TestErrors`, `TestProperties` |
| **TN-003** | Test names must be readable as English sentences |
| **TN-004** | Every test class docstring references the relevant spec section |
| **TN-005** | Tests within a class ordered: happy path → edge cases → errors → properties |
| **TN-006** | Maximum 20 tests per class. Split into sub-classes or separate files if exceeded |
| **TN-007** | No test logic shared between test classes via inheritance. Use fixtures and helpers instead |

---

# 4. FIXTURES AND TEST DATA

## 4.1 Fixture Hierarchy

```python
# ── Root conftest.py — available to ALL tests ──
# tests/conftest.py

import pytest
from datetime import date, datetime, timezone


@pytest.fixture
def now_utc() -> datetime:
    """Current UTC time for tests that need a consistent timestamp."""
    return datetime(2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_ticker() -> str:
    """Standard ticker used across tests."""
    return "AAPL"


@pytest.fixture
def sample_date() -> date:
    """Standard date used across tests."""
    return date(2025, 1, 15)


# ── Domain conftest.py — available to domain tests only ──
# tests/unit/data_engine/conftest.py

import pytest
from unittest.mock import AsyncMock
from src.data_engine.ingestion.interfaces import MarketDataProvider
from src.data_engine.ingestion.repository import IngestionRepository
from src.data_engine.ingestion.service import IngestionService
from src.shared.interfaces import EventBus


@pytest.fixture
def mock_primary_provider() -> AsyncMock:
    """Mocked primary market data provider."""
    mock = AsyncMock(spec=MarketDataProvider)
    mock.provider_name = "mock_primary"
    return mock


@pytest.fixture
def mock_fallback_provider() -> AsyncMock:
    """Mocked fallback market data provider."""
    mock = AsyncMock(spec=MarketDataProvider)
    mock.provider_name = "mock_fallback"
    return mock


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Mocked ingestion repository."""
    return AsyncMock(spec=IngestionRepository)


@pytest.fixture
def mock_event_bus() -> AsyncMock:
    """Mocked event bus."""
    return AsyncMock(spec=EventBus)


@pytest.fixture
def ingestion_service(
    mock_primary_provider: AsyncMock,
    mock_fallback_provider: AsyncMock,
    mock_repository: AsyncMock,
    mock_event_bus: AsyncMock,
) -> IngestionService:
    """Fully wired IngestionService with all mocked dependencies."""
    return IngestionService(
        primary_provider=mock_primary_provider,
        fallback_provider=mock_fallback_provider,
        repository=mock_repository,
        event_bus=mock_event_bus,
    )
```

## 4.2 Test Object Factories

Use factory functions instead of constructing complex objects inline:

```python
# tests/helpers/factories.py

"""Test object factories.

These functions create valid test objects with sensible defaults.
Override only the fields relevant to your test — the factory
provides reasonable values for everything else.

Convention:
    - Factory function name: make_<model_name>
    - All parameters have defaults
    - Returns the actual domain model (not a mock)
"""

from datetime import date, datetime, timezone
from src.data_engine.ingestion.models import OHLCVBar


def make_ohlcv_bar(
    ticker: str = "AAPL",
    bar_date: date = date(2025, 1, 15),
    open_cents: int = 15000,
    high_cents: int = 15200,
    low_cents: int = 14900,
    close_cents: int = 15100,
    volume: int = 1_000_000,
    source: str = "test",
    fetched_at: datetime | None = None,
) -> OHLCVBar:
    """Create a valid OHLCVBar for testing.

    All values are internally consistent by default:
    low <= open, close <= high.
    """
    return OHLCVBar(
        ticker=ticker,
        date=bar_date,
        open_cents=open_cents,
        high_cents=high_cents,
        low_cents=low_cents,
        close_cents=close_cents,
        volume=volume,
        source=source,
        fetched_at=fetched_at or datetime.now(timezone.utc),
    )


def make_ohlcv_series(
    ticker: str = "AAPL",
    start_date: date = date(2025, 1, 2),
    num_bars: int = 20,
    start_price_cents: int = 15000,
    daily_return_pct: float = 0.001,
    volume: int = 1_000_000,
) -> list[OHLCVBar]:
    """Create a series of OHLCV bars with consistent price progression.

    Useful for testing indicators and time-series functions that
    need multi-bar input.

    Args:
        ticker: Stock ticker.
        start_date: Date of first bar.
        num_bars: Number of bars to generate.
        start_price_cents: Opening price of first bar.
        daily_return_pct: Daily return as decimal for price progression.
        volume: Constant volume for all bars.

    Returns:
        List of OHLCVBar objects in chronological order.
    """
    from tests.helpers.time_helpers import next_trading_day

    bars: list[OHLCVBar] = []
    current_price = float(start_price_cents)
    current_date = start_date

    for _ in range(num_bars):
        close_cents = round(current_price)
        open_cents = round(current_price * (1 - daily_return_pct * 0.3))
        high_cents = round(current_price * 1.005)
        low_cents = round(current_price * 0.995)

        bars.append(make_ohlcv_bar(
            ticker=ticker,
            bar_date=current_date,
            open_cents=open_cents,
            high_cents=max(high_cents, open_cents, close_cents),
            low_cents=min(low_cents, open_cents, close_cents),
            close_cents=close_cents,
            volume=volume,
        ))

        current_price *= (1 + daily_return_pct)
        current_date = next_trading_day(current_date)

    return bars


def make_financial_statement(
    ticker: str = "AAPL",
    period_end_date: date = date(2024, 12, 31),
    revenue_cents: int = 39_183_000_000_00,       # $391.83B
    cost_of_goods_sold_cents: int = 21_297_000_000_00,
    operating_income_cents: int = 11_896_000_000_00,
    net_income_cents: int = 9_680_000_000_00,
    total_assets_cents: int = 35_258_000_000_00,
    total_liabilities_cents: int = 27_454_000_000_00,
    shareholders_equity_cents: int = 7_804_000_000_00,
    total_debt_cents: int = 10_878_000_000_00,
    cash_cents: int = 3_009_000_000_00,
    ebitda_cents: int = 13_454_000_000_00,
    free_cash_flow_cents: int = 10_120_000_000_00,
    shares_outstanding: int = 15_408_095_000,
) -> dict:
    """Create a plausible financial statement for testing.

    Default values are loosely inspired by a large-cap tech company
    but are NOT real data. Use fixtures/financial_statements/ for
    actual verification data.

    Note: total_assets = total_liabilities + shareholders_equity
    is enforced by construction.
    """
    return {
        "ticker": ticker,
        "period_end_date": period_end_date,
        "revenue_cents": revenue_cents,
        "cost_of_goods_sold_cents": cost_of_goods_sold_cents,
        "operating_income_cents": operating_income_cents,
        "net_income_cents": net_income_cents,
        "total_assets_cents": total_assets_cents,
        "total_liabilities_cents": total_liabilities_cents,
        "shareholders_equity_cents": shareholders_equity_cents,
        "total_debt_cents": total_debt_cents,
        "cash_cents": cash_cents,
        "ebitda_cents": ebitda_cents,
        "free_cash_flow_cents": free_cash_flow_cents,
        "shares_outstanding": shares_outstanding,
    }
```

## 4.3 Test Data Files

```python
# ── Fixture data files — JSON for recorded API responses ──
# tests/fixtures/api_responses/polygon/daily_bars_aapl.json

# These are RECORDED real API responses used for adapter tests.
# They ensure our translation logic handles real provider quirks.
# Update periodically but do NOT use live API calls in unit tests.

# ── Loading fixture data ──
# tests/helpers/fixtures.py

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture(relative_path: str) -> dict:
    """Load a JSON fixture file.

    Args:
        relative_path: Path relative to tests/fixtures/ directory.

    Returns:
        Parsed JSON content.

    Raises:
        FileNotFoundError: If fixture file does not exist.

    Example:
        >>> data = load_fixture("api_responses/polygon/daily_bars_aapl.json")
    """
    fixture_path = FIXTURES_DIR / relative_path
    if not fixture_path.exists():
        raise FileNotFoundError(
            f"Fixture not found: {fixture_path}. "
            "Run `make update-fixtures` to refresh test data."
        )

    with open(fixture_path) as f:
        return json.load(f)


def load_price_series(relative_path: str) -> list[float]:
    """Load a price series from fixture file for indicator testing.

    Returns list of prices as floats (for indicator tests that
    work with raw prices rather than cent integers).
    """
    data = load_fixture(relative_path)
    return [bar["close"] for bar in data["bars"]]
```

## 4.4 Fixture Rules

| Rule | Description |
|------|-------------|
| **FX-001** | Fixtures build from bottom up: root → domain → test file. Never skip levels. |
| **FX-002** | Factory functions provide sensible defaults. Tests override only relevant fields. |
| **FX-003** | Fixture data files committed to git (they are part of the test specification). |
| **FX-004** | No fixture file larger than 1MB. Use generators for large datasets. |
| **FX-005** | Fixture data must be internally consistent (e.g., high ≥ open, close ≥ low). |
| **FX-006** | Fixtures never make network calls. Recorded responses stored in files. |
| **FX-007** | Factory functions return real domain objects, not mocks. |
| **FX-008** | Shared fixtures are documented with docstrings explaining their purpose. |

---

# 5. MOCKING STANDARDS

## 5.1 What to Mock

```text
┌─────────────────────────────────────────────────────────┐
│                 MOCKING DECISION MATRIX                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ALWAYS MOCK (in unit tests):                           │
│  ✓ External API calls (FMP, etc.)                       │
│  ✓ Database operations                                   │
│  ✓ File system I/O                                       │
│  ✓ LLM API calls                                        │
│  ✓ Event bus / message publishing                        │
│  ✓ Time/clock (use fixed timestamps)                     │
│  ✓ Random number generators (use fixed seeds)            │
│  ✓ Network requests                                      │
│                                                          │
│  NEVER MOCK:                                             │
│  ✗ The unit under test itself                            │
│  ✗ Pure functions (math, formatting, conversions)        │
│  ✗ Pydantic model validation                             │
│  ✗ Data structures (lists, dicts, numpy arrays)          │
│  ✗ Value objects and domain models                       │
│  ✗ Simple utility functions                              │
│                                                          │
│  USE REAL IN INTEGRATION TESTS:                          │
│  ◐ Database (use test database)                          │
│  ◐ Cache (use test cache instance)                       │
│  ◐ File system (use temp directories)                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 5.2 Mocking Patterns

```python
from unittest.mock import AsyncMock, MagicMock, patch
import pytest


# ── Pattern 1: Mock via dependency injection (PREFERRED) ──
# The service receives mocks through its constructor.
# This is the cleanest and most maintainable approach.

class TestIngestionServiceFetchWithFallback:
    """Test the fallback behavior when primary provider fails."""

    async def test_uses_fallback_when_primary_fails(
        self,
        ingestion_service: IngestionService,
        mock_primary_provider: AsyncMock,
        mock_fallback_provider: AsyncMock,
    ):
        # Arrange
        error = DataFetchError(code="TIMEOUT", message="Provider timeout")
        mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(error)

        expected_bars = [make_ohlcv_bar()]
        mock_fallback_provider.fetch_daily_ohlcv.return_value = Success(expected_bars)

        # Act
        result = await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

        # Assert
        assert result.is_success
        mock_primary_provider.fetch_daily_ohlcv.assert_called_once()
        mock_fallback_provider.fetch_daily_ohlcv.assert_called_once()


# ── Pattern 2: Mock via patch (USE SPARINGLY) ──
# Only when dependency injection is not feasible (e.g., module-level functions).

class TestSomethingWithCurrentTime:

    @patch("src.data_engine.ingestion.service.datetime")
    async def test_staleness_check_uses_current_time(
        self,
        mock_datetime: MagicMock,
    ):
        mock_datetime.now.return_value = datetime(
            2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc
        )
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)
        ...


# ── Pattern 3: Fake implementation (FOR COMPLEX INTERFACES) ──
# When the mock needs realistic behavior beyond simple return values.

class FakeMarketDataProvider:
    """In-memory market data provider for testing.

    Simulates a real provider with pre-loaded data, rate limiting,
    and configurable failure modes.
    """

    def __init__(self) -> None:
        self._data: dict[str, list[OHLCVBar]] = {}
        self._should_fail: bool = False
        self._call_count: int = 0

    @property
    def provider_name(self) -> str:
        return "fake"

    def load_data(self, ticker: str, bars: list[OHLCVBar]) -> None:
        """Pre-load data that will be returned for this ticker."""
        self._data[ticker] = bars

    def set_failure_mode(self, should_fail: bool) -> None:
        """Configure the provider to simulate failures."""
        self._should_fail = should_fail

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        self._call_count += 1

        if self._should_fail:
            return Failure(DataFetchError(
                code="FAKE_FAILURE",
                message="Simulated provider failure",
            ))

        bars = self._data.get(ticker, [])
        filtered = [
            b for b in bars
            if start_date <= b.date <= end_date
        ]
        return Success(filtered)

    async def health_check(self) -> bool:
        return not self._should_fail
```

## 5.3 Mock Verification Patterns

```python
# ── Verify a mock was called with specific arguments ──
mock_repository.store_bars.assert_called_once_with(expected_bars)

# ── Verify a mock was called N times ──
assert mock_provider.fetch_daily_ohlcv.call_count == 2

# ── Verify a mock was NOT called ──
mock_fallback_provider.fetch_daily_ohlcv.assert_not_called()

# ── Verify call arguments loosely ──
from unittest.mock import ANY
mock_event_bus.publish.assert_called_once_with(
    "data.ingestion.completed",
    {
        "ticker": "AAPL",
        "date": ANY,        # Don't care about exact date
        "bar_count": 5,
    },
)

# ── Verify call order ──
from unittest.mock import call
mock_logger.info.assert_has_calls([
    call("Starting operation", ticker="AAPL"),
    call("Operation completed", ticker="AAPL", bars_ingested=5),
], any_order=False)
```

## 5.4 Mocking Rules

| Rule | Description |
|------|-------------|
| **MK-001** | Prefer dependency injection over `@patch`. DI mocks are more readable and less fragile. |
| **MK-002** | Mock at the boundary, not the internals. Mock the interface (Protocol), not the implementation. |
| **MK-003** | Use `AsyncMock` for async methods, `MagicMock` for sync methods. |
| **MK-004** | Always use `spec=InterfaceClass` on mocks to catch interface changes. |
| **MK-005** | Mock return values must be realistic — use factory functions, not bare primitives. |
| **MK-006** | Every mock assertion should test behavior, not implementation. Verify *what* was called, not *how* the code arrived at calling it. |
| **MK-007** | If a mock setup exceeds 10 lines, extract it into a fixture or fake. |
| **MK-008** | Never mock the standard library (except `datetime.now` for fixed time). |
| **MK-009** | When using `@patch`, always patch where the target is *used*, not where it is *defined*. |

---

# 6. ASSERTION STANDARDS

## 6.1 Standard Assertions

```python
import pytest
import numpy as np

# ── Exact equality (for integers, strings, booleans) ──
assert result == 42
assert ticker == "AAPL"
assert is_valid is True  # explicit `is True`, not `assert is_valid`

# ── Approximate equality (for floats) — ALWAYS use pytest.approx ──
assert ratio == pytest.approx(15.23, abs=0.01)
assert returns[0] == pytest.approx(0.05, rel=1e-6)

# ── Never use bare == for float comparison ──
assert result == 0.1 + 0.2          # ✗ WILL FAIL
assert result == pytest.approx(0.3) # ✓ Correct

# ── NumPy array assertions ──
np.testing.assert_array_almost_equal(result, expected, decimal=6)
np.testing.assert_array_equal(result, expected)  # exact equality

# ── Collection assertions ──
assert len(result) == 5
assert "AAPL" in result
assert set(result) == {"AAPL", "MSFT", "GOOGL"}

# ── Result type assertions ──
assert result.is_success
assert result.is_failure
assert result.value == expected_value       # after confirming is_success
assert result.error.code == "INVALID_TICKER"  # after confirming is_failure

# ── Exception assertions ──
with pytest.raises(ValueError, match="at least 2 prices"):
    simple_returns(np.array([100]))

with pytest.raises(ValueError) as exc_info:
    some_function()
assert "specific message" in str(exc_info.value)

# ── None assertions ──
assert result is None       # ✓ Use `is None`
assert result is not None   # ✓ Use `is not None`
assert result == None        # ✗ Never use == for None
```

## 6.2 Custom Assertion Helpers

```python
# tests/helpers/assertions.py

"""Custom assertion helpers for domain-specific validations.

These helpers provide clear error messages when assertions fail,
making test failures easier to diagnose.
"""

import numpy as np
from src.shared.utils.comparison import EPSILON_WEIGHT


def assert_valid_ohlcv_bar(bar) -> None:
    """Assert that an OHLCV bar has internally consistent values.

    Checks:
    - High >= Low
    - High >= Open, Close
    - Low <= Open, Close
    - Volume >= 0
    - Ticker is non-empty uppercase
    """
    assert bar.high_cents >= bar.low_cents, (
        f"High ({bar.high_cents}) must be >= Low ({bar.low_cents}) "
        f"for {bar.ticker} on {bar.date}"
    )
    assert bar.high_cents >= bar.open_cents, (
        f"High ({bar.high_cents}) must be >= Open ({bar.open_cents})"
    )
    assert bar.high_cents >= bar.close_cents, (
        f"High ({bar.high_cents}) must be >= Close ({bar.close_cents})"
    )
    assert bar.low_cents <= bar.open_cents, (
        f"Low ({bar.low_cents}) must be <= Open ({bar.open_cents})"
    )
    assert bar.low_cents <= bar.close_cents, (
        f"Low ({bar.low_cents}) must be <= Close ({bar.close_cents})"
    )
    assert bar.volume >= 0, f"Volume must be >= 0, got {bar.volume}"
    assert bar.ticker == bar.ticker.upper(), (
        f"Ticker must be uppercase, got '{bar.ticker}'"
    )
    assert len(bar.ticker) > 0, "Ticker must not be empty"


def assert_weights_sum_to_one(weights: dict[str, float]) -> None:
    """Assert portfolio weights sum to 1.0 within tolerance."""
    total = sum(weights.values())
    assert abs(total - 1.0) <= EPSILON_WEIGHT, (
        f"Portfolio weights must sum to 1.0, got {total:.8f}. "
        f"Weights: {weights}"
    )


def assert_returns_series_valid(returns: np.ndarray) -> None:
    """Assert a returns series is valid for further computation."""
    assert len(returns) > 0, "Returns series is empty"
    assert not np.any(np.isnan(returns)), (
        f"Returns series contains {np.sum(np.isnan(returns))} NaN values"
    )
    assert not np.any(np.isinf(returns)), (
        f"Returns series contains infinite values"
    )
    # No single-period return should exceed ±100% (circuit breaker sanity)
    extreme = np.max(np.abs(returns))
    assert extreme <= 1.0, (
        f"Returns contain extreme value {extreme:.4f} (>{100}%). "
        "This may indicate a data error."
    )


def assert_chronological(dates: list) -> None:
    """Assert that a list of dates is in ascending chronological order."""
    for i in range(1, len(dates)):
        assert dates[i] >= dates[i - 1], (
            f"Dates not chronological: {dates[i-1]} followed by {dates[i]} "
            f"at index {i}"
        )


def assert_result_success(result, message: str = "") -> None:
    """Assert a Result is Success, with clear error message if not."""
    prefix = f"{message}: " if message else ""
    assert result.is_success, (
        f"{prefix}Expected Success but got Failure: "
        f"[{result.error.code}] {result.error.message}"
    )


def assert_result_failure(result, expected_code: str = "") -> None:
    """Assert a Result is Failure, optionally with a specific error code."""
    assert result.is_failure, (
        f"Expected Failure but got Success with value: {result.value}"
    )
    if expected_code:
        assert result.error.code == expected_code, (
            f"Expected error code '{expected_code}' but got '{result.error.code}'"
        )
```

## 6.3 Assertion Rules

| Rule | Description |
|------|-------------|
| **AS-001** | Always use `pytest.approx()` for float comparisons. Specify `abs` or `rel` tolerance explicitly. |
| **AS-002** | Always include a descriptive message for complex assertions (use f-strings in assert). |
| **AS-003** | One logical assertion per test. Multiple `assert` lines are fine if they verify one concept. |
| **AS-004** | Never use `assert True` or `assert False` alone — assert the actual condition. |
| **AS-005** | Use `is None` / `is not None`, never `== None`. |
| **AS-006** | Use `pytest.raises()` context manager for expected exceptions, always with `match=` pattern. |
| **AS-007** | Use custom assertion helpers from `tests/helpers/assertions.py` for domain-specific checks. |
| **AS-008** | Assertion failure messages should contain enough context to diagnose without looking at the test code. |

---

# 7. FINANCIAL CALCULATION TESTING

This section provides the testing standards for financial code as
required by `L4-conventions/financial-calculation-standards.md` Section 14.

## 7.1 Test Categories for Financial Functions

Every financial calculation function requires all of these test categories:

```python
@pytest.mark.financial
class TestSharpeRatio:
    """Tests for sharpe_ratio() function.

    Reference: Sharpe (1966), verified against numpy manual calculation.
    See: L4-conventions/financial-calculation-standards.md Section 4.2
    """

    # ── Category 1: Known-Value Tests ──
    # Compare against hand-calculated or textbook values.
    # Minimum 3 per function.

    class TestKnownValues:

        def test_textbook_example_positive_sharpe(self):
            """Verify against textbook example.

            Source: "Investments" by Bodie, Kane, Marcus (12th ed.), Ch. 6.
            Portfolio: 10% annual return, 15% annual volatility,
            Risk-free: 3%.
            Expected Sharpe: (0.10 - 0.03) / 0.15 = 0.4667
            """
            # Use daily returns that produce known annual values
            daily_returns = np.random.RandomState(42).normal(
                loc=0.10 / 252, scale=0.15 / np.sqrt(252), size=252
            )
            result = sharpe_ratio(daily_returns, risk_free_rate_annual=0.03)
            # Tolerance is wider here due to random sampling
            assert result == pytest.approx(0.47, abs=0.15)

        def test_zero_excess_return_gives_zero_sharpe(self):
            """If returns exactly match risk-free rate, Sharpe = 0."""
            # Create returns with mean matching risk-free rate
            rf_daily = (1.05) ** (1/252) - 1
            returns = np.full(252, rf_daily)
            result = sharpe_ratio(returns, risk_free_rate_annual=0.05)
            # Zero vol → None (can't divide by zero)
            assert result is None

        def test_manual_calculation_matches(self):
            """Step-by-step manual calculation verification."""
            returns = np.array([0.01, 0.02, -0.01, 0.015, -0.005])

            # Manual calculation
            mean_r = np.mean(returns)
            std_r = np.std(returns, ddof=1)
            rf_daily = (1.05) ** (1/252) - 1
            excess = mean_r - rf_daily
            daily_sharpe = excess / std_r
            annual_sharpe = daily_sharpe * np.sqrt(252)

            result = sharpe_ratio(
                returns, risk_free_rate_annual=0.05, periods_per_year=252
            )
            assert result == pytest.approx(annual_sharpe, rel=1e-6)

    # ── Category 2: Edge Cases ──

    class TestEdgeCases:

        def test_single_return_returns_none(self):
            """Cannot compute std dev from single observation."""
            result = sharpe_ratio(np.array([0.05]))
            assert result is None

        def test_two_returns_minimum_valid(self):
            """Two returns is the minimum for std dev."""
            result = sharpe_ratio(np.array([0.01, 0.02]))
            assert result is not None
            assert isinstance(result, float)

        def test_all_identical_returns_zero_vol(self):
            """All same returns → zero volatility → None."""
            result = sharpe_ratio(np.full(100, 0.001))
            assert result is None

        def test_very_small_returns(self):
            """Near-zero returns should not cause numerical issues."""
            returns = np.array([1e-10, 2e-10, -1e-10, 1e-10, 0])
            result = sharpe_ratio(returns)
            assert result is not None
            assert np.isfinite(result)

        def test_large_negative_returns(self):
            """Handles large drawdowns without error."""
            returns = np.array([-0.05, -0.10, -0.03, 0.02, -0.08])
            result = sharpe_ratio(returns)
            assert result is not None
            assert result < 0  # Should be negative Sharpe

    # ── Category 3: Precision Tests ──

    class TestPrecision:

        def test_result_has_sufficient_decimal_precision(self):
            """Result should have at least 4 significant figures."""
            returns = np.random.RandomState(42).normal(0.0005, 0.01, 252)
            result = sharpe_ratio(returns)
            # Verify it's not rounded to fewer than 4 significant figures
            result_str = f"{result:.10f}"
            assert len(result_str.replace("0", "").replace(".", "").replace("-", "")) >= 4

        def test_annualization_precision(self):
            """Verify annualization doesn't introduce precision loss."""
            returns = np.array([0.001] * 252)  # Constant daily return
            result_daily = sharpe_ratio(returns, periods_per_year=252)
            result_weekly = sharpe_ratio(
                returns[:52], periods_per_year=52
            )
            # Different periods should give similar annualized results
            # (not exact due to different sample sizes)
            if result_daily is not None and result_weekly is not None:
                assert abs(result_daily - result_weekly) < 2.0

    # ── Category 4: Reference Tests ──

    class TestReferenceImplementation:

        def test_matches_manual_numpy_calculation(self):
            """Compare against explicit numpy implementation."""
            returns = np.random.RandomState(99).normal(0.0004, 0.012, 500)
            rf_annual = 0.04

            # Manual numpy implementation
            rf_daily = (1 + rf_annual) ** (1/252) - 1
            excess_returns = returns - rf_daily
            manual_sharpe = (
                np.mean(excess_returns) / np.std(excess_returns, ddof=1)
            ) * np.sqrt(252)

            result = sharpe_ratio(
                returns,
                risk_free_rate_annual=rf_annual,
                periods_per_year=252,
            )
            assert result == pytest.approx(manual_sharpe, rel=1e-6)

    # ── Category 5: Property Tests ──

    class TestProperties:

        def test_higher_returns_higher_sharpe(self):
            """All else equal, higher mean return → higher Sharpe."""
            base = np.random.RandomState(42).normal(0.0, 0.01, 252)

            low_return = base + 0.0001
            high_return = base + 0.001

            sharpe_low = sharpe_ratio(low_return)
            sharpe_high = sharpe_ratio(high_return)

            assert sharpe_high > sharpe_low

        def test_higher_volatility_lower_sharpe(self):
            """All else equal, higher volatility → lower Sharpe."""
            mean = 0.0005
            low_vol = np.random.RandomState(42).normal(mean, 0.005, 252)
            high_vol = np.random.RandomState(42).normal(mean, 0.02, 252)

            sharpe_low_vol = sharpe_ratio(low_vol)
            sharpe_high_vol = sharpe_ratio(high_vol)

            if sharpe_low_vol is not None and sharpe_high_vol is not None:
                assert sharpe_low_vol > sharpe_high_vol
```

## 7.2 Financial Test Vectors

```python
# tests/fixtures/financial/sharpe_test_vectors.py

"""Known Sharpe ratio test vectors for verification.

Each vector includes source and expected result verified by
at least one alternative calculation method.
"""

SHARPE_TEST_VECTORS = [
    {
        "name": "Perfectly constant positive excess return",
        "returns": [0.001] * 252,
        "risk_free_rate_annual": 0.0,
        "periods_per_year": 252,
        "expected": None,  # Zero volatility → undefined
        "source": "Logical: zero std dev → division by zero",
    },
    {
        "name": "50/50 up and down with positive drift",
        "returns": [0.01, -0.005] * 126,
        "risk_free_rate_annual": 0.03,
        "periods_per_year": 252,
        "expected_range": (0.5, 3.0),  # Wide range due to pattern
        "source": "Hand-calculated bounds",
    },
]
```

## 7.3 Financial Testing Rules

| Rule | Description |
|------|-------------|
| **FT-001** | Every financial function has minimum 3 known-value tests with cited sources |
| **FT-002** | Every financial function is tested against at least one reference implementation |
| **FT-003** | All edge cases documented in the function's docstring have corresponding tests |
| **FT-004** | Monetary round-trip tests verify no precision loss: cents → compute → cents |
| **FT-005** | Property-based tests verify mathematical invariants (monotonicity, symmetry, etc.) |
| **FT-006** | All financial tests use the `@pytest.mark.financial` marker |
| **FT-007** | Financial test vectors are stored in `tests/fixtures/financial/` with sources |
| **FT-008** | When a financial calculation bug is found, the first fix is a failing test |

---

# 8. SERVICE LAYER TESTING

## 8.1 Service Test Pattern

```python
# tests/unit/data_engine/ingestion/test_ingestion_service.py

import pytest
from unittest.mock import AsyncMock
from datetime import date

from src.data_engine.ingestion.service import IngestionService
from src.data_engine.ingestion.errors import DataFetchError, DataValidationError
from src.shared.types import Success, Failure
from tests.helpers.factories import make_ohlcv_bar, make_ohlcv_series
from tests.helpers.assertions import assert_result_success, assert_result_failure


class TestIngestionServiceIngestDailyOHLCV:
    """Tests for IngestionService.ingest_daily_ohlcv().

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-001
    """

    class TestHappyPath:

        async def test_fetches_from_primary_provider(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_repository: AsyncMock,
        ):
            """Primary provider is used first."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            result = await ingestion_service.ingest_daily_ohlcv(
                "AAPL", date(2025, 1, 15)
            )

            assert_result_success(result, "Primary provider fetch")
            mock_primary_provider.fetch_daily_ohlcv.assert_called_once()

        async def test_stores_bars_after_successful_fetch(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_repository: AsyncMock,
        ):
            """Validated bars are persisted to repository."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

            mock_repository.store_bars.assert_called_once_with(bars)

        async def test_emits_completion_event(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_event_bus: AsyncMock,
        ):
            """Completion event published after successful ingestion."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

            mock_event_bus.publish.assert_called_once()
            call_args = mock_event_bus.publish.call_args
            assert call_args[0][0] == "data.ingestion.completed"
            assert call_args[0][1]["ticker"] == "AAPL"

    class TestFallbackBehavior:

        async def test_uses_fallback_when_primary_fails(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_fallback_provider: AsyncMock,
        ):
            """Falls back to secondary provider on primary failure."""
            mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(
                DataFetchError(code="TIMEOUT", message="Primary timeout")
            )
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_fallback_provider.fetch_daily_ohlcv.return_value = Success(bars)

            result = await ingestion_service.ingest_daily_ohlcv(
                "AAPL", date(2025, 1, 15)
            )

            assert_result_success(result, "Fallback provider")
            mock_primary_provider.fetch_daily_ohlcv.assert_called_once()
            mock_fallback_provider.fetch_daily_ohlcv.assert_called_once()

        async def test_returns_failure_when_all_providers_fail(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_fallback_provider: AsyncMock,
        ):
            """Returns Failure when both providers fail."""
            error = DataFetchError(code="TIMEOUT", message="timeout")
            mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(error)
            mock_fallback_provider.fetch_daily_ohlcv.return_value = Failure(error)

            result = await ingestion_service.ingest_daily_ohlcv(
                "AAPL", date(2025, 1, 15)
            )

            assert_result_failure(result, "ALL_PROVIDERS_FAILED")

        async def test_does_not_store_when_all_providers_fail(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_fallback_provider: AsyncMock,
            mock_repository: AsyncMock,
        ):
            """Repository is not called when no data is fetched."""
            error = DataFetchError(code="TIMEOUT", message="timeout")
            mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(error)
            mock_fallback_provider.fetch_daily_ohlcv.return_value = Failure(error)

            await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

            mock_repository.store_bars.assert_not_called()

    class TestValidation:

        async def test_normalizes_ticker_to_uppercase(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
        ):
            """Lowercase tickers are normalized before provider call."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            await ingestion_service.ingest_daily_ohlcv("aapl", date(2025, 1, 15))

            call_args = mock_primary_provider.fetch_daily_ohlcv.call_args
            assert call_args[0][0] == "AAPL"  # normalized

        async def test_rejects_empty_ticker(
            self,
            ingestion_service: IngestionService,
        ):
            """Empty ticker string returns Failure immediately."""
            result = await ingestion_service.ingest_daily_ohlcv(
                "", date(2025, 1, 15)
            )

            assert_result_failure(result, "INVALID_TICKER")
```

## 8.2 Service Test Coverage Requirements

For every service method, test:

```text
□ Happy path (normal successful execution)
□ Input validation (each validation rule)
□ Fallback behavior (if applicable)
□ All failure modes (each error case in the spec)
□ Side effects (events emitted, data stored)
□ Side effects NOT triggered on failure
□ Idempotency (if applicable)
□ Logging (key log points called with expected context)
```

---

# 9. ADAPTER TESTING

## 9.1 Adapter Unit Tests (Mocked HTTP)

```python
# tests/unit/data_engine/ingestion/test_polygon_adapter.py

import pytest
from unittest.mock import AsyncMock, patch
from datetime import date

from src.data_engine.ingestion.adapters.polygon_adapter import PolygonMarketDataAdapter
from tests.helpers.fixtures import load_fixture
from tests.helpers.assertions import assert_valid_ohlcv_bar


class TestPolygonAdapterTranslation:
    """Test Polygon API response translation to canonical format.

    These tests use RECORDED API responses from tests/fixtures/
    to verify that our translation logic handles real Polygon
    response formats correctly.
    """

    @pytest.fixture
    def adapter(self) -> PolygonMarketDataAdapter:
        return PolygonMarketDataAdapter(
            api_key="test-key-not-real",
            rate_limit_per_minute=100,
        )

    @pytest.fixture
    def polygon_daily_response(self) -> dict:
        """Real Polygon API response (recorded and sanitized)."""
        return load_fixture("api_responses/polygon/daily_bars_aapl.json")

    async def test_translates_polygon_response_to_ohlcv_bars(
        self, adapter, polygon_daily_response
    ):
        """Polygon response correctly translated to OHLCVBar objects."""
        with patch.object(adapter, "_make_request", return_value=polygon_daily_response):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 2), date(2025, 1, 10)
            )

        assert result.is_success
        bars = result.value
        assert len(bars) > 0

        for bar in bars:
            assert_valid_ohlcv_bar(bar)
            assert bar.ticker == "AAPL"
            assert bar.source == "polygon"

    async def test_converts_dollar_prices_to_cents(
        self, adapter
    ):
        """Polygon returns dollar floats — we convert to integer cents."""
        mock_response = {
            "results": [{
                "t": 1736899200000,   # Polygon timestamp (ms)
                "o": 150.25,
                "h": 152.10,
                "l": 149.80,
                "c": 151.50,
                "v": 5000000,
            }]
        }

        with patch.object(adapter, "_make_request", return_value=mock_response):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 15), date(2025, 1, 15)
            )

        bar = result.value[0]
        assert bar.open_cents == 15025
        assert bar.high_cents == 15210
        assert bar.low_cents == 14980
        assert bar.close_cents == 15150

    async def test_handles_null_volume_gracefully(
        self, adapter
    ):
        """Polygon sometimes returns null volume for pre-market."""
        mock_response = {
            "results": [{
                "t": 1736899200000,
                "o": 150.25,
                "h": 152.10,
                "l": 149.80,
                "c": 151.50,
                "v": None,            # null volume!
            }]
        }

        with patch.object(adapter, "_make_request", return_value=mock_response):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 15), date(2025, 1, 15)
            )

        assert result.is_success
        assert result.value[0].volume == 0  # Default to 0

    async def test_handles_rate_limit_response(self, adapter):
        """Polygon 429 response returns typed error."""
        rate_limit_response = load_fixture(
            "api_responses/polygon/error_rate_limited.json"
        )

        with patch.object(adapter, "_make_request", side_effect=Exception("429")):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 15), date(2025, 1, 15)
            )

        assert result.is_failure
        assert "RATE_LIMITED" in result.error.code or "TIMEOUT" in result.error.code
```

---

# 10. PYDANTIC MODEL TESTING

## 10.1 Model Validation Tests

```python
# tests/unit/data_engine/ingestion/test_ohlcv_validation.py

import pytest
from datetime import date, datetime, timezone
from pydantic import ValidationError

from src.data_engine.ingestion.models import OHLCVBar


class TestOHLCVBarValidation:
    """Test Pydantic validation rules for OHLCVBar model.

    These tests verify that invalid data is rejected at the
    model boundary, preventing corrupt data from entering
    the system.
    """

    class TestValidConstruction:

        def test_valid_bar_is_accepted(self):
            """A bar with valid values constructs successfully."""
            bar = OHLCVBar(
                ticker="AAPL",
                date=date(2025, 1, 15),
                open_cents=15000,
                high_cents=15200,
                low_cents=14900,
                close_cents=15100,
                volume=1_000_000,
                source="polygon",
                fetched_at=datetime.now(timezone.utc),
            )
            assert bar.ticker == "AAPL"
            assert bar.close_cents == 15100

    class TestFieldValidation:

        def test_negative_price_rejected(self):
            """Negative prices are invalid."""
            with pytest.raises(ValidationError) as exc_info:
                OHLCVBar(
                    ticker="AAPL",
                    date=date(2025, 1, 15),
                    open_cents=-100,    # Invalid
                    high_cents=15200,
                    low_cents=14900,
                    close_cents=15100,
                    volume=1_000_000,
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )
            assert "open_cents" in str(exc_info.value)

        def test_negative_volume_rejected(self):
            """Negative volume is invalid."""
            with pytest.raises(ValidationError):
                OHLCVBar(
                    ticker="AAPL",
                    date=date(2025, 1, 15),
                    open_cents=15000,
                    high_cents=15200,
                    low_cents=14900,
                    close_cents=15100,
                    volume=-1,          # Invalid
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )

        def test_missing_required_field_rejected(self):
            """Missing required field raises ValidationError."""
            with pytest.raises(ValidationError):
                OHLCVBar(
                    # ticker missing!
                    date=date(2025, 1, 15),
                    open_cents=15000,
                    high_cents=15200,
                    low_cents=14900,
                    close_cents=15100,
                    volume=1_000_000,
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )

    class TestCrossFieldValidation:
        """Test cross-field validators (model_validator)."""

        def test_high_below_low_rejected(self):
            """High must be >= Low."""
            with pytest.raises(ValidationError, match="High.*Low"):
                OHLCVBarValidated(
                    ticker="AAPL",
                    date=date(2025, 1, 15),
                    open_cents=15000,
                    high_cents=14800,   # Below low!
                    low_cents=14900,
                    close_cents=15100,
                    volume=1_000_000,
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )

    class TestImmutability:

        def test_bar_is_frozen(self):
            """OHLCVBar instances should be immutable."""
            bar = OHLCVBar(
                ticker="AAPL",
                date=date(2025, 1, 15),
                open_cents=15000,
                high_cents=15200,
                low_cents=14900,
                close_cents=15100,
                volume=1_000_000,
                source="test",
                fetched_at=datetime.now(timezone.utc),
            )
            with pytest.raises(ValidationError):
                bar.close_cents = 99999  # Should fail if frozen
```

---

# 11. AI AGENT OUTPUT TESTING (Phase 2+)

## 11.1 Agent Output Schema Validation

```python
# tests/integration/research/test_research_agent.py

import pytest
from pydantic import ValidationError

from src.research.agents.research_analyst import ResearchAnalystAgent
from src.research.agents.models import ResearchReport


@pytest.mark.integration
@pytest.mark.agent
class TestResearchAgentOutput:
    """Test that the Research Analyst Agent produces valid, compliant output.

    These tests verify structural compliance and guardrail adherence.
    They do NOT evaluate the quality of the analysis (that's human review).

    See: specs/L5-agents/research-analyst-agent.md
    """

    class TestSchemaCompliance:

        async def test_output_matches_research_report_schema(
            self, research_agent, mock_data_for_aapl
        ):
            """Agent output must parse as a valid ResearchReport."""
            raw_output = await research_agent.analyze("AAPL")

            # Must not raise ValidationError
            report = ResearchReport.model_validate(raw_output)
            assert report.metadata.ticker == "AAPL"

        async def test_all_required_fields_present(
            self, research_agent, mock_data_for_aapl
        ):
            """Every required field in ResearchReport is populated."""
            report = await research_agent.analyze("AAPL")

            assert report.metadata.ticker is not None
            assert report.metadata.generated_at is not None
            assert report.metadata.confidence_score is not None
            assert report.summary.recommendation is not None
            assert report.summary.key_risks is not None
            assert report.summary.key_catalysts is not None
            assert report.thesis.bull_case is not None
            assert report.thesis.base_case is not None
            assert report.thesis.bear_case is not None

    class TestGuardrailCompliance:

        async def test_confidence_score_in_valid_range(
            self, research_agent, mock_data_for_aapl
        ):
            """Confidence score must be between 0.0 and 1.0."""
            report = await research_agent.analyze("AAPL")
            assert 0.0 <= report.metadata.confidence_score <= 1.0

        async def test_bear_case_always_present(
            self, research_agent, mock_data_for_aapl
        ):
            """Even for STRONG_BUY, a bear case must exist.

            Guardrail: INV-011 from L0-system-vision.md
            """
            report = await research_agent.analyze("AAPL")
            assert report.thesis.bear_case is not None
            assert len(report.thesis.bear_case.narrative) > 50  # Substantive

        async def test_all_claims_have_citations(
            self, research_agent, mock_data_for_aapl
        ):
            """Every data claim in the report must have a citation.

            Guardrail: Agent Design Principle P2 (Cited Claims Only)
            """
            report = await research_agent.analyze("AAPL")
            assert len(report.evidence.supporting_data_points) > 0

            for data_point in report.evidence.supporting_data_points:
                assert data_point.source is not None
                assert len(data_point.source) > 0

        async def test_no_forbidden_language(
            self, research_agent, mock_data_for_aapl
        ):
            """Agent must not use certainty language.

            Guardrail: MUST NOT use "guaranteed", "certain", "risk-free"
            """
            report = await research_agent.analyze("AAPL")

            forbidden_phrases = [
                "guaranteed",
                "risk-free",
                "certain to",
                "will definitely",
                "cannot fail",
                "sure thing",
                "no risk",
            ]

            full_text = report.model_dump_json().lower()
            for phrase in forbidden_phrases:
                assert phrase not in full_text, (
                    f"Report contains forbidden phrase: '{phrase}'"
                )

        async def test_low_confidence_caps_recommendation(
            self, research_agent, mock_data_with_minimal_info
        ):
            """When data is sparse, confidence should be low and
            recommendation capped.

            Guardrail: INV-012, INV-013
            """
            report = await research_agent.analyze("OBSCURE_TICKER")

            if report.metadata.confidence_score < 0.3:
                assert report.summary.recommendation == "INSUFFICIENT_DATA"
            elif report.metadata.confidence_score < 0.5:
                assert report.summary.recommendation in ("HOLD", "INSUFFICIENT_DATA")

    class TestDataIntegrity:

        async def test_financial_numbers_traceable_to_source(
            self, research_agent, mock_data_for_aapl
        ):
            """Key financial figures in report should match input data."""
            report = await research_agent.analyze("AAPL")

            # Verify at least some figures match what we provided
            # (specific checks depend on what data was mocked)
            assert report.metadata.data_completeness_score > 0

        async def test_stale_data_flagged(
            self, research_agent, mock_data_stale
        ):
            """When input data is stale, report flags it."""
            report = await research_agent.analyze("AAPL")

            assert report.metadata.data_completeness_score < 1.0
            assert len(report.evidence.data_gaps) > 0
```

## 11.2 Agent Testing Rules

| Rule | Description |
|------|-------------|
| **AG-001** | Agent output MUST validate against its Pydantic schema (100% of the time) |
| **AG-002** | Guardrail tests run on every agent output, even in development |
| **AG-003** | Forbidden language checks use a configurable blocklist |
| **AG-004** | Agent tests use the `@pytest.mark.agent` marker |
| **AG-005** | Agent integration tests are allowed to make real LLM calls (marked slow) |
| **AG-006** | Agent unit tests mock the LLM and test the surrounding logic |
| **AG-007** | Agent output tests verify structure, not analytical quality (quality is human-reviewed) |
| **AG-008** | Confidence calibration is tested: low-data scenarios must produce low confidence |

---

# 12. INTEGRATION TESTING

## 12.1 Database Integration Tests

```python
# tests/integration/conftest.py

import pytest
import asyncio
from src.infrastructure.database import Database


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all async integration tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> Database:
    """Create and configure a test database.

    Uses a separate test database that is created before the
    test session and destroyed after.
    """
    db = Database(
        host="localhost",
        port=5432,
        name="investment_pipeline_test",
        pool_size_min=1,
        pool_size_max=5,
    )
    await db.connect()
    await db.run_migrations()
    yield db
    await db.drop_all_tables()
    await db.disconnect()


@pytest.fixture(autouse=True)
async def clean_tables(test_db: Database):
    """Truncate all tables before each test for isolation.

    This runs before every integration test to ensure clean state.
    Uses TRUNCATE CASCADE for speed.
    """
    await test_db.truncate_all_tables()
    yield


# ── Integration test example ──
# tests/integration/data_engine/test_ingestion_repository.py

@pytest.mark.integration
class TestIngestionRepositoryStoreAndRetrieve:
    """Test IngestionRepository against a real database."""

    async def test_store_and_retrieve_bars(
        self, test_db: Database
    ):
        """Bars stored in DB can be retrieved exactly."""
        repo = IngestionRepository(db=test_db)
        bars = [
            make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15)),
            make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 16)),
        ]

        stored_count = await repo.store_bars(bars)
        assert stored_count == 2

        retrieved = await repo.get_bars(
            "AAPL", date(2025, 1, 15), date(2025, 1, 16)
        )
        assert len(retrieved) == 2
        assert retrieved[0].date == date(2025, 1, 15)
        assert retrieved[1].date == date(2025, 1, 16)
        assert retrieved[0].close_cents == bars[0].close_cents

    async def test_upsert_updates_existing_bar(
        self, test_db: Database
    ):
        """Storing a bar for the same ticker+date updates, not duplicates."""
        repo = IngestionRepository(db=test_db)

        bar_v1 = make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15), close_cents=15000)
        bar_v2 = make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15), close_cents=15100)

        await repo.store_bars([bar_v1])
        await repo.store_bars([bar_v2])

        retrieved = await repo.get_bars("AAPL", date(2025, 1, 15), date(2025, 1, 15))
        assert len(retrieved) == 1
        assert retrieved[0].close_cents == 15100  # Updated value

    async def test_get_bars_returns_empty_for_unknown_ticker(
        self, test_db: Database
    ):
        """Unknown ticker returns empty list, not None or error."""
        repo = IngestionRepository(db=test_db)

        retrieved = await repo.get_bars(
            "ZZZZ", date(2025, 1, 15), date(2025, 1, 16)
        )
        assert retrieved == []
```

## 12.2 Integration Test Rules

| Rule | Description |
|------|-------------|
| **IT-001** | Integration tests use real infrastructure (database, cache) but fake external APIs |
| **IT-002** | Each test starts with clean state (tables truncated) |
| **IT-003** | Integration tests marked with `@pytest.mark.integration` |
| **IT-004** | Integration tests may take up to 5 seconds each |
| **IT-005** | Test database is separate from dev/prod databases |
| **IT-006** | Integration tests run in CI but can be skipped locally with `pytest -m "not integration"` |
| **IT-007** | External API integration tests (real network) marked `@pytest.mark.slow` and `@pytest.mark.external` |

---

# 13. ASYNC TESTING

## 13.1 Async Test Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```python
# ── Async tests — just use `async def` ──
# With asyncio_mode = "auto", pytest-asyncio handles the event loop

class TestAsyncService:

    async def test_async_operation(self, service):
        """Async test — no decorator needed with asyncio_mode='auto'."""
        result = await service.fetch_data("AAPL")
        assert result.is_success

    async def test_concurrent_operations(self, service):
        """Test concurrent execution behavior."""
        import asyncio
        results = await asyncio.gather(
            service.fetch_data("AAPL"),
            service.fetch_data("MSFT"),
            service.fetch_data("GOOGL"),
        )
        assert all(r.is_success for r in results)
```

## 13.2 Async Mock Patterns

```python
from unittest.mock import AsyncMock

# ── AsyncMock for async methods ──
mock_provider = AsyncMock(spec=MarketDataProvider)
mock_provider.fetch_daily_ohlcv.return_value = Success([make_ohlcv_bar()])

# ── AsyncMock with side_effect for sequential calls ──
mock_provider.fetch_daily_ohlcv.side_effect = [
    Failure(DataFetchError(code="TIMEOUT", message="First call fails")),
    Success([make_ohlcv_bar()]),  # Second call succeeds (retry)
]

# ── AsyncMock with side_effect for exceptions ──
mock_provider.fetch_daily_ohlcv.side_effect = ConnectionError("Network down")

# ── Verify async mock was awaited ──
mock_provider.fetch_daily_ohlcv.assert_awaited_once_with("AAPL", date(2025, 1, 15), date(2025, 1, 15))
```

---

# 14. COVERAGE REQUIREMENTS

## 14.1 Coverage Targets

| Code Category                     | Minimum Coverage | Rationale                              |
|-----------------------------------|------------------|----------------------------------------|
| Financial calculations (`shared/utils/`) | 95%        | Highest risk — errors cost real money  |
| Technical indicators (`quantitative/indicators/`) | 95% | Direct impact on trading signals |
| Risk metrics (`risk/analytics/`)  | 95%              | Guardrail enforcement                 |
| Service layer (all `*_service.py`)| 85%              | Core business logic                   |
| Repository layer                  | 75%              | Data access (partly integration-tested)|
| Adapters                          | 80%              | External boundary translation          |
| Pydantic models                   | 80%              | Validation rules                       |
| Infrastructure                    | 70%              | Boilerplate and wiring                 |
| Agent prompts/logic               | 70%              | Hard to unit test; integration covers  |
| **Overall project minimum**       | **80%**          | Enforced in CI                         |

## 14.2 Coverage Configuration

```toml
# pyproject.toml

[tool.coverage.run]
source = ["src"]
omit = [
    "src/main.py",          # Entry point — not unit-testable
    "src/config/*",         # Configuration loading
    "src/**/migrations/*",  # Database migrations
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@overload",
]
```

## 14.3 Coverage Rules

| Rule | Description |
|------|-------------|
| **CV-001** | Coverage threshold is enforced in CI — build fails if below target |
| **CV-002** | `# pragma: no cover` requires a comment explaining why coverage is not feasible |
| **CV-003** | Coverage must not decrease on any PR (ratchet policy) |
| **CV-004** | New files must meet the category-specific target, not just the global average |
| **CV-005** | Coverage measures line coverage AND branch coverage |
| **CV-006** | 100% coverage does not mean correct code — coverage is necessary but not sufficient |

---

# 15. TEST PERFORMANCE

## 15.1 Speed Requirements

| Test Category  | Max Duration Per Test | Max Suite Duration |
|----------------|-----------------------|--------------------|
| Unit tests     | 100ms                 | 60 seconds total   |
| Financial      | 200ms                 | 30 seconds total   |
| Integration    | 5 seconds             | 120 seconds total  |
| Agent          | 30 seconds            | 300 seconds total  |
| E2E            | 60 seconds            | 300 seconds total  |

## 15.2 Speed Enforcement

```python
# ── Mark slow tests ──
@pytest.mark.slow
async def test_full_research_pipeline():
    """This test makes real LLM calls and takes ~20 seconds."""
    ...


# ── Run only fast tests during development ──
# pytest -m "not slow and not integration"

# ── Run everything in CI ──
# pytest --timeout=60
```

## 15.3 Speed Optimization Rules

| Rule | Description |
|------|-------------|
| **SP-001** | Unit tests must not do any I/O (network, disk, database) |
| **SP-002** | Use `pytest-timeout` to enforce per-test time limits |
| **SP-003** | Session-scoped fixtures for expensive setup (DB connection) |
| **SP-004** | Function-scoped fixtures for test isolation (table truncation) |
| **SP-005** | Large fixture files loaded once per session, not per test |
| **SP-006** | Prefer numpy vectorized operations in test data generation |
| **SP-007** | Profile test suite periodically; investigate any single test > 500ms |

---

# 16. REGRESSION TESTING

## 16.1 Bug Fix Protocol

```text
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   EVERY BUG FIX MUST INCLUDE A REGRESSION TEST                  ║
║                                                                   ║
║   1. Write a test that FAILS with the bug present               ║
║   2. Fix the bug                                                 ║
║   3. Verify the test now PASSES                                  ║
║   4. The test stays in the suite forever                         ║
║                                                                   ║
║   This ensures the same bug never returns.                       ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

```python
class TestRegressions:
    """Regression tests for previously discovered bugs.

    Each test documents the bug it prevents. Do not delete
    regression tests even if they seem redundant — they are
    the project's institutional memory.
    """

    def test_regression_issue_42_polygon_null_volume(self):
        """Bug: Polygon sometimes returns null volume for pre-market bars.
        Previously caused a ValidationError crash in ingestion.

        Fix: Default to volume=0 and flag the bar.
        Issue: #42
        Date: 2025-01-15
        """
        mock_response = {
            "results": [{
                "t": 1736899200000,
                "o": 150.25,
                "h": 152.10,
                "l": 149.80,
                "c": 151.50,
                "v": None,  # The null volume that caused the crash
            }]
        }
        # Should not raise — should handle gracefully
        bars = adapter._translate_response(mock_response, "AAPL")
        assert bars[0].volume == 0

    def test_regression_issue_57_float_dollar_precision_loss(self):
        """Bug: Converting $150.99 to cents produced 15098 instead of 15099
        due to floating-point representation.

        Fix: Use Decimal for conversion in dollars_to_cents().
        Issue: #57
        Date: 2025-02-03
        """
        assert dollars_to_cents(150.99) == 15099
        assert dollars_to_cents(0.1 + 0.2) == 30  # Classic float trap
        assert dollars_to_cents(10.005) == 1001    # Banker's rounding edge
```

---

# 17. TEST ANTI-PATTERNS

## 17.1 What NOT to Do

```python
# ── ANTI-PATTERN 1: Testing implementation, not behavior ──

# ✗ WRONG — tests internal method names
def test_service_calls_private_validate_method():
    service._validate_ticker("AAPL")  # Reaching into internals!

# ✓ CORRECT — tests the public behavior
def test_service_rejects_invalid_ticker():
    result = await service.ingest("", date.today())
    assert result.is_failure


# ── ANTI-PATTERN 2: Test that tests nothing ──

# ✗ WRONG — no assertion
def test_something():
    result = calculate_sma(prices, 20)
    # forgot to assert!

# ✓ CORRECT
def test_sma_produces_correct_value():
    result = calculate_sma(prices, 20)
    assert result[-1] == pytest.approx(expected_value)


# ── ANTI-PATTERN 3: Overly broad try/except in tests ──

# ✗ WRONG — swallows the actual error
def test_something_doesnt_crash():
    try:
        result = some_function()
    except Exception:
        pytest.fail("Function raised an exception")

# ✓ CORRECT — let unexpected exceptions propagate naturally
def test_something_produces_valid_result():
    result = some_function()  # If it raises, pytest reports it clearly
    assert result is not None


# ── ANTI-PATTERN 4: Tests dependent on execution order ──

# ✗ WRONG — test_b depends on side effects of test_a
class TestOrdered:
    shared_state = {}

    def test_a_creates_record(self):
        self.shared_state["id"] = create_record()

    def test_b_reads_record(self):
        record = get_record(self.shared_state["id"])  # Depends on test_a!

# ✓ CORRECT — each test sets up its own state
class TestIndependent:
    def test_create_and_read_record(self):
        record_id = create_record()
        record = get_record(record_id)
        assert record is not None


# ── ANTI-PATTERN 5: Sleeping in tests ──

# ✗ WRONG
async def test_retry_behavior():
    await service.start()
    await asyncio.sleep(5)  # Waiting for something to happen
    assert service.is_ready

# ✓ CORRECT — use polling or mock the clock
async def test_retry_behavior():
    with mock_clock() as clock:
        await service.start()
        clock.advance(seconds=5)
        assert service.is_ready


# ── ANTI-PATTERN 6: Magic numbers in assertions ──

# ✗ WRONG — where did 15099 come from?
def test_price_conversion():
    assert convert(150.99) == 15099

# ✓ CORRECT — explain the expected value
def test_price_conversion():
    input_dollars = 150.99
    expected_cents = 15099  # $150.99 × 100 = 15099 cents
    assert dollars_to_cents(input_dollars) == expected_cents


# ── ANTI-PATTERN 7: Testing framework code (e.g., Pydantic itself) ──

# ✗ WRONG — testing that Pydantic works
def test_pydantic_validates_types():
    with pytest.raises(ValidationError):
        OHLCVBar(ticker=12345, ...)  # Testing Pydantic's type checking

# ✓ CORRECT — testing YOUR validation rules
def test_high_below_low_is_rejected():
    with pytest.raises(ValidationError, match="High.*Low"):
        OHLCVBarValidated(high_cents=100, low_cents=200, ...)


# ── ANTI-PATTERN 8: Hardcoded dates that will become stale ──

# ✗ WRONG — breaks after 2025-12-31
def test_data_is_not_stale():
    data = fetch_data("AAPL")
    assert data.date >= date(2025, 1, 1)

# ✓ CORRECT — relative to test execution
def test_data_is_not_stale():
    data = fetch_data("AAPL")
    max_staleness = timedelta(days=7)
    assert (date.today() - data.date) <= max_staleness
```

## 17.2 Anti-Pattern Checklist

| Anti-Pattern | Detection | Prevention |
|-------------|-----------|------------|
| No assertions in test | Linting rule (`pytest --strict-markers`) | Code review |
| Test order dependency | Run tests with `pytest -p randomly` | Each test self-contained |
| Sleep in tests | Search for `asyncio.sleep` in tests | Mock time instead |
| Testing internals | Search for `._` in test files | Test public API only |
| Excessive mocking | > 5 mocks per test | Simplify design or use fakes |
| Flaky tests | CI tracking of intermittent failures | Fix or quarantine immediately |
| Large test functions | > 30 lines per test | Split into focused tests |
| Shared mutable state | Class-level variables in test classes | Use fixtures |

---

# 18. CI INTEGRATION

## 18.1 CI Test Stages

```yaml
# CI Pipeline Test Stages

stages:
  - name: "Lint & Type Check"
    commands:
      - ruff check src/ tests/
      - mypy src/
    max_duration: 60s

  - name: "Unit Tests"
    commands:
      - pytest tests/unit -v --timeout=10 --cov=src
    max_duration: 120s
    required: true    # Blocks merge

  - name: "Financial Verification Tests"
    commands:
      - pytest tests/unit -m financial -v --timeout=10
    max_duration: 60s
    required: true    # Blocks merge

  - name: "Integration Tests"
    commands:
      - pytest tests/integration -v --timeout=30
    max_duration: 300s
    required: true    # Blocks merge
    needs: [test-database]

  - name: "Agent Tests"
    commands:
      - pytest tests/integration -m agent -v --timeout=60
    max_duration: 600s
    required: false   # Advisory (LLM calls may be flaky)
    needs: [llm-api-key]

  - name: "Coverage Report"
    commands:
      - pytest tests/unit tests/integration --cov=src --cov-report=html --cov-fail-under=80
    required: true    # Blocks merge if coverage drops
```

## 18.2 CI Rules

| Rule | Description |
|------|-------------|
| **CI-001** | All unit and integration tests must pass before merge to main |
| **CI-002** | Coverage must not decrease (ratchet: new code must meet target) |
| **CI-003** | Type checking (mypy strict) must pass |
| **CI-004** | Linting (ruff) must pass with zero warnings |
| **CI-005** | Financial tests (`@pytest.mark.financial`) run as a separate visible stage |
| **CI-006** | Test duration tracked per-commit to detect performance regressions |
| **CI-007** | Flaky test detected (passes then fails in same commit) → must be fixed within 24 hours or quarantined |

---

# 19. TESTING CHECKLIST FOR AI CODING AGENTS

When an AI agent generates code, it must also generate tests that satisfy:

```text
UNIT TEST CHECKLIST (per public function/method):
─────────────────────────────────────────────────
□ Happy path test (normal successful case)
□ All input validation rules have tests
□ All error cases in docstring have tests
□ Edge cases tested (empty input, single element, boundaries)
□ Return type verified (Success/Failure, None, empty list)
□ Side effects verified (events emitted, data stored)
□ Side effects NOT triggered on failure path

FINANCIAL FUNCTION ADDITIONAL CHECKLIST:
────────────────────────────────────────
□ Minimum 3 known-value tests with cited sources
□ Reference implementation comparison test
□ Precision test (decimal places, round-trip)
□ Edge cases: zero, negative, very large, very small values
□ Property/invariant tests (mathematical properties)
□ Marked with @pytest.mark.financial

SERVICE METHOD ADDITIONAL CHECKLIST:
─────────────────────────────────────
□ Dependencies mocked via constructor injection
□ Fallback behavior tested (if applicable)
□ Concurrent execution tested (if applicable)
□ Logging verified for key operations

MODEL VALIDATION ADDITIONAL CHECKLIST:
──────────────────────────────────────
□ Valid construction succeeds
□ Each required field missing → ValidationError
□ Invalid field values → ValidationError
□ Cross-field validation tested
□ Immutability tested (if frozen)

GENERAL QUALITY:
────────────────
□ Test names are self-documenting English sentences
□ Arrange-Act-Assert structure with visual separation
□ No magic numbers in assertions (expected values explained)
□ pytest.approx used for ALL float comparisons
□ Custom assertion helpers used for domain checks
□ No test exceeds 30 lines
□ All tests pass: ruff, mypy, pytest
```

---

# 20. CROSS-REFERENCES

| Document                              | Location                                              |
|---------------------------------------|-------------------------------------------------------|
| L0: System Vision                     | `specs/L0-system-vision.md`                           |
| L4: Coding Standards                  | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards   | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: AI Agent Design Standards         | `specs/L4-conventions/ai-agent-design-standards.md`   |
| L4: Data Pipeline Standards           | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Error Handling                    | `specs/L4-conventions/error-handling.md`               |
| L5: Research Analyst Agent            | `specs/L5-agents/research-analyst-agent.md`           |
| Guardrails: Data Quality              | `specs/guardrails/data-quality-guardrails.md`         |
| Guardrails: AI Output                 | `specs/guardrails/ai-output-guardrails.md`            |

---
```
