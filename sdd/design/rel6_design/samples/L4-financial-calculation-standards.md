## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines the **mandatory standards** for all financial
calculations performed anywhere in the system. Financial software has
a unique category of bugs — calculations that are *almost* correct but
subtly wrong. These bugs compound silently over time, corrupt backtests,
distort risk assessments, and erode trust in the pipeline's recommendations.

This document exists to prevent those bugs categorically.

**Every developer and every AI coding agent** must read this document
before writing any code that touches prices, returns, ratios, percentages,
portfolio math, or financial time series.

## Scope

| In Scope                                    | Out of Scope                        |
|---------------------------------------------|-------------------------------------|
| Monetary arithmetic and precision           | Tax calculations (jurisdiction-specific) |
| Return calculations (simple, log, compound) | Accounting standards (GAAP/IFRS)    |
| Financial ratio formulas                    | Derivatives pricing (Black-Scholes) |
| Technical indicator calculations            | Options Greeks (Phase 6+)           |
| Portfolio math (weights, returns, risk)     | Fixed income math                   |
| Statistical measures (std, correlation)     | Cryptocurrency calculations         |
| Annualization and compounding               |                                     |
| Dividend and split adjustments              |                                     |
| Time-series alignment and cleaning          |                                     |

## Governing Invariants

These invariants are inherited from L0-system-vision.md and are
restated here for emphasis:

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-001 | **A monetary value is an integer amount in minor units PLUS an explicit currency code — inseparably.** A bare integer is not a monetary value. No arithmetic combines currencies without an explicit FX step. *(Amended in L0 v0.6.0; this document's §1 still shows currency-free `int` cents throughout and needs a pass.)* |
| INV-002 | All percentages calculated to minimum 4 decimal precision     |
| INV-003 | No floating-point equality comparisons (use epsilon tolerance)|
| INV-015 | No analysis may use future data (look-ahead bias prevention)  |
| INV-016 | Backtest results must account for transaction costs            |
| INV-017 | Survivorship bias must be addressed in any historical analysis|

---

# 1. MONETARY ARITHMETIC

## 1.1 The Cardinal Rule: Integer Cents

```python
# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   ALL MONETARY VALUES ARE STORED AND COMPUTED AS             ║
# ║   INTEGER CENTS (int64). NEVER AS FLOATING-POINT DOLLARS.   ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

# ✗ CATASTROPHICALLY WRONG — floating-point dollars
price = 150.99
total = price * 3          # = 452.96999999999997 (NOT 452.97)

# ✓ CORRECT — integer cents
price_cents: int = 15099
total_cents: int = price_cents * 3  # = 45297 (exactly $452.97)
```

## 1.2 Why This Matters — The Evidence

```python
# Floating-point arithmetic is fundamentally broken for money:

>>> 0.1 + 0.2
0.30000000000000004

>>> 0.1 + 0.2 == 0.3
False

>>> sum([0.01] * 100)
1.0000000000000007

>>> 150.99 * 3
452.96999999999997

# Over thousands of positions and millions of calculations,
# these errors compound into material discrepancies.
# A $0.01 rounding error per trade × 10,000 trades = $100 unexplained.
```

## 1.3 Conversion Functions

```python
# src/shared/utils/money.py

"""Monetary conversion utilities.

These are the ONLY functions that convert between dollar floats
(from external APIs) and integer cents (internal representation).
All external data enters the system through these functions.
"""

import math
from decimal import Decimal, ROUND_HALF_UP


def dollars_to_cents(dollars: float) -> int:
    """Convert a dollar amount (float) to integer cents.

    Uses Decimal for precise conversion to avoid floating-point
    rounding errors.

    Args:
        dollars: Dollar amount as float (e.g., 150.99).

    Returns:
        Integer cents (e.g., 15099).

    Examples:
        >>> dollars_to_cents(150.99)
        15099
        >>> dollars_to_cents(0.1 + 0.2)
        30  # Correct, despite float input being 0.30000000000000004
        >>> dollars_to_cents(10.005)
        1001  # Rounds half up
    """
    return int(Decimal(str(dollars)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    ) * 100)


def cents_to_dollars(cents: int) -> float:
    """Convert integer cents to dollar float for display only.

    ⚠️  WARNING: Use this ONLY for human-readable display output.
    Never use the returned float for further calculations.

    Args:
        cents: Integer cents (e.g., 15099).

    Returns:
        Dollar float (e.g., 150.99). FOR DISPLAY ONLY.
    """
    return cents / 100


def format_usd(cents: int) -> str:
    """Format integer cents as a USD display string.

    Args:
        cents: Integer cents. Can be negative.

    Returns:
        Formatted string like "$1,500.99" or "-$42.10".

    Examples:
        >>> format_usd(150099)
        '$1,500.99'
        >>> format_usd(-4210)
        '-$42.10'
        >>> format_usd(0)
        '$0.00'
    """
    if cents < 0:
        return f"-${abs(cents) / 100:,.2f}"
    return f"${cents / 100:,.2f}"
```

## 1.4 Monetary Arithmetic Operations

```python
# ── Addition / Subtraction: straightforward with int ──
total_cents = price_a_cents + price_b_cents       # ✓ Exact

# ── Multiplication by integer quantity: straightforward ──
line_total_cents = unit_price_cents * quantity     # ✓ Exact

# ── Percentage of a monetary amount: round explicitly ──
# Example: 7.5% tax on $150.99
tax_cents = round(15099 * 0.075)                  # = 1132 ($11.32)

# ── Division producing money: always round explicitly ──
split_cents = round(total_cents / num_people)     # ✓ Explicitly rounded

# ── Weighted amounts: use Decimal for multi-step calculations ──
from decimal import Decimal, ROUND_HALF_UP

def calculate_weighted_price(
    price_cents: int,
    weight: float,
) -> int:
    """Calculate a weighted monetary amount with precise rounding.

    Used for portfolio-weighted calculations where intermediate
    precision matters.
    """
    result = Decimal(str(price_cents)) * Decimal(str(weight))
    return int(result.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

## 1.5 Monetary Comparison

```python
# ── Equality: integers compare exactly ──
if total_cents == expected_cents:    # ✓ Safe with integers
    ...

# ── Never compare dollar floats ──
if total_dollars == 150.99:          # ✗ NEVER — floating-point trap
    ...
```

## 1.6 When Float Dollars Are Acceptable

```text
Float dollar values are acceptable ONLY in these contexts:

1. Display output strings (via format_usd() or cents_to_dollars())
2. Charting / visualization data points (presentation layer only)
3. Intermediate values in return/ratio calculations (Section 2)
   where the result is a ratio, not a dollar amount

Float dollar values are NEVER acceptable for:

1. Storage (database, file, cache)
2. Monetary arithmetic (addition, subtraction, line totals)
3. Comparison operations
4. Portfolio value calculations
5. P&L calculations
6. Transaction amounts
```

---

# 2. RETURN CALCULATIONS

## 2.1 Return Type Taxonomy

The system uses three types of returns. Every function that calculates
or consumes returns must document which type it uses.

```python
# ── Simple Return (Arithmetic Return) ──
# Most common. Used for single-period returns.
# Formula: R = (P1 - P0) / P0
# Example: Stock goes from $100 to $105 → R = 0.05 (5%)

# ── Log Return (Continuously Compounded Return) ──
# Used when returns need to be time-additive.
# Formula: r = ln(P1 / P0)
# Example: Stock goes from $100 to $105 → r = 0.04879 (4.879%)

# ── Total Return ──
# Includes dividends/distributions.
# Formula: R_total = (P1 + D - P0) / P0
# Where D = dividends received during period
```

## 2.2 Standard Return Functions

```python
# src/shared/utils/returns.py

"""Return calculation utilities.

All return calculation functions in the system. Functions are
pure (no side effects) and operate on numpy arrays for performance.

Convention:
- Returns are always expressed as decimals (0.05 = 5%), not percentages
- Functions document which return type they compute
- NaN is used for undefined returns (e.g., division by zero)
"""

import numpy as np
import pandas as pd


def simple_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate simple (arithmetic) returns from a price series.

    Formula: R_t = (P_t - P_{t-1}) / P_{t-1}

    Args:
        prices: Array of prices in chronological order (oldest first).
            Must have at least 2 elements. Prices must be positive.

    Returns:
        Array of simple returns. Length = len(prices) - 1.
        Returns are decimals: 0.05 means +5%.

    Raises:
        ValueError: If prices has fewer than 2 elements.
        ValueError: If any price is <= 0.

    Example:
        >>> simple_returns(np.array([100, 105, 103]))
        array([0.05, -0.01904762])
    """
    prices = np.asarray(prices, dtype=np.float64)

    if len(prices) < 2:
        raise ValueError(
            f"Need at least 2 prices, got {len(prices)}"
        )

    if np.any(prices <= 0):
        raise ValueError(
            "All prices must be positive. Found non-positive price."
        )

    return np.diff(prices) / prices[:-1]


def log_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate log (continuously compounded) returns from a price series.

    Formula: r_t = ln(P_t / P_{t-1})

    Log returns are time-additive: the log return over multiple periods
    equals the sum of individual period log returns.

    Args:
        prices: Array of prices in chronological order (oldest first).
            Must have at least 2 elements. Prices must be positive.

    Returns:
        Array of log returns. Length = len(prices) - 1.

    Raises:
        ValueError: If prices has fewer than 2 elements.
        ValueError: If any price is <= 0.

    Note:
        For small returns (< ~10%), simple and log returns are
        approximately equal. They diverge for larger moves.
    """
    prices = np.asarray(prices, dtype=np.float64)

    if len(prices) < 2:
        raise ValueError(
            f"Need at least 2 prices, got {len(prices)}"
        )

    if np.any(prices <= 0):
        raise ValueError(
            "All prices must be positive. Found non-positive price."
        )

    return np.log(prices[1:] / prices[:-1])


def total_return(
    price_start_cents: int,
    price_end_cents: int,
    dividends_cents: int = 0,
) -> float:
    """Calculate total return including dividends for a single period.

    Formula: R = (P_end + D - P_start) / P_start

    Args:
        price_start_cents: Starting price in cents.
        price_end_cents: Ending price in cents.
        dividends_cents: Total dividends received during period, in cents.

    Returns:
        Total return as decimal. 0.05 means +5%.

    Raises:
        ValueError: If price_start_cents is <= 0.

    Example:
        >>> total_return(10000, 10500, 200)
        0.07  # Stock up 5% + 2% dividend = 7% total return
    """
    if price_start_cents <= 0:
        raise ValueError(
            f"Start price must be positive, got {price_start_cents}"
        )

    return (price_end_cents + dividends_cents - price_start_cents) / price_start_cents
```

## 2.3 Cumulative and Compound Returns

```python
def cumulative_simple_return(simple_returns: np.ndarray) -> np.ndarray:
    """Calculate cumulative return series from simple returns.

    Formula: (1 + R_1)(1 + R_2)...(1 + R_t) - 1

    Args:
        simple_returns: Array of simple period returns as decimals.

    Returns:
        Array of cumulative returns (same length as input).
        cumulative[i] = total return from start through period i.

    Example:
        >>> cumulative_simple_return(np.array([0.10, -0.05, 0.08]))
        array([0.10, 0.045, 0.1286])
        # $100 → $110 → $104.50 → $112.86 → total return 12.86%
    """
    return np.cumprod(1 + simple_returns) - 1


def compound_annual_growth_rate(
    total_return: float,
    years: float,
) -> float:
    """Calculate CAGR from total return and holding period.

    Formula: CAGR = (1 + R_total)^(1/years) - 1

    Args:
        total_return: Total return as decimal (e.g., 0.50 for +50%).
        years: Number of years (can be fractional, e.g., 2.5).

    Returns:
        CAGR as decimal.

    Raises:
        ValueError: If years <= 0.
        ValueError: If total_return < -1.0 (lost more than 100%).

    Example:
        >>> compound_annual_growth_rate(0.50, 3.0)
        0.14471  # ~14.5% annualized for 50% over 3 years
    """
    if years <= 0:
        raise ValueError(f"Years must be positive, got {years}")

    if total_return < -1.0:
        raise ValueError(
            f"Total return cannot be less than -100%, got {total_return}"
        )

    return (1 + total_return) ** (1 / years) - 1
```

## 2.4 Return Calculation Rules

| Rule | Description |
|------|-------------|
| **RC-001** | Returns are always decimals (0.05), never percentages (5.0), in computation. Conversion to percentage happens only at display. |
| **RC-002** | Always specify return type (simple, log, total) in function names and docstrings |
| **RC-003** | Use simple returns for single-period and portfolio return calculations |
| **RC-004** | Use log returns for time-series aggregation and statistical analysis |
| **RC-005** | Never compound simple returns by summing them (multiply: ∏(1+R_i) - 1) |
| **RC-006** | Never compute log returns by summing simple returns |
| **RC-007** | Return arrays are one element shorter than price arrays |
| **RC-008** | Handle division by zero explicitly (return NaN, not raise) for batch operations |
| **RC-009** | Price inputs to return functions must be in chronological order (oldest first) |
| **RC-010** | Always document whether prices are adjusted or unadjusted for splits/dividends |

---

# 3. ANNUALIZATION

## 3.1 Annualization Constants

```python
# src/shared/constants/financial.py

"""Financial calculation constants.

These are standard financial conventions, not tunable parameters.
Changes to these values would mean changing industry standards.
"""

# Trading periods per year — used for annualization
TRADING_DAYS_PER_YEAR: int = 252
TRADING_WEEKS_PER_YEAR: int = 52
TRADING_MONTHS_PER_YEAR: int = 12

# Square roots — pre-computed for common annualization
SQRT_TRADING_DAYS: float = 252 ** 0.5       # ≈ 15.8745
SQRT_TRADING_WEEKS: float = 52 ** 0.5       # ≈ 7.2111
SQRT_TRADING_MONTHS: float = 12 ** 0.5      # ≈ 3.4641
```

## 3.2 Annualization Functions

```python
# src/shared/utils/annualization.py

"""Annualization utilities for returns and volatility.

The annualization formulas differ for returns vs. volatility:
- Returns annualize by compounding: (1+R)^N - 1
- Volatility annualizes by √N scaling: σ_annual = σ_period × √N

These functions enforce the correct formula for each case.
"""

import numpy as np
from src.shared.constants.financial import TRADING_DAYS_PER_YEAR


def annualize_return(
    periodic_return: float,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Annualize a mean periodic return by compounding.

    Formula: R_annual = (1 + R_period)^periods_per_year - 1

    Args:
        periodic_return: Mean return for one period (e.g., mean daily return).
        periods_per_year: Number of periods in a year (252 for daily).

    Returns:
        Annualized return as decimal.

    Example:
        >>> annualize_return(0.0004, 252)  # Mean daily return of 0.04%
        0.1061  # ≈ 10.61% annualized
    """
    return (1 + periodic_return) ** periods_per_year - 1


def annualize_volatility(
    periodic_volatility: float,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Annualize periodic volatility using square-root-of-time rule.

    Formula: σ_annual = σ_period × √(periods_per_year)

    This assumes returns are IID (independent and identically distributed).
    In practice, financial returns exhibit serial correlation and
    clustering, so this is an approximation.

    Args:
        periodic_volatility: Standard deviation of periodic returns.
        periods_per_year: Number of periods in a year (252 for daily).

    Returns:
        Annualized volatility as decimal.

    Example:
        >>> annualize_volatility(0.01, 252)  # Daily vol of 1%
        0.1587  # ≈ 15.87% annualized volatility
    """
    return periodic_volatility * np.sqrt(periods_per_year)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  CRITICAL: Never annualize volatility by compounding.           ║
# ║  Never annualize returns by √N scaling.                         ║
# ║                                                                  ║
# ║  Returns compound:    R_annual = (1 + R_daily)^252 - 1          ║
# ║  Volatility scales:   σ_annual = σ_daily × √252                 ║
# ║                                                                  ║
# ║  Mixing these formulas is a common and serious error.           ║
# ╚══════════════════════════════════════════════════════════════════╝
```

## 3.3 Period Detection

```python
def infer_frequency(dates: pd.DatetimeIndex) -> int:
    """Infer the observation frequency and return periods_per_year.

    Examines the median gap between observations to determine
    whether data is daily, weekly, or monthly.

    Args:
        dates: DatetimeIndex of observation dates. Must be sorted ascending.

    Returns:
        Estimated number of periods per year:
        - Daily data: 252
        - Weekly data: 52
        - Monthly data: 12

    Raises:
        ValueError: If fewer than 3 dates provided.
        ValueError: If frequency cannot be determined.

    Note:
        This is a heuristic. When possible, specify frequency
        explicitly rather than relying on inference.
    """
    if len(dates) < 3:
        raise ValueError(
            f"Need at least 3 dates to infer frequency, got {len(dates)}"
        )

    median_gap_days = np.median(np.diff(dates).astype("timedelta64[D]").astype(int))

    if 0 < median_gap_days <= 3:
        return TRADING_DAYS_PER_YEAR    # Daily
    elif 3 < median_gap_days <= 10:
        return TRADING_WEEKS_PER_YEAR   # Weekly
    elif 10 < median_gap_days <= 45:
        return TRADING_MONTHS_PER_YEAR  # Monthly
    else:
        raise ValueError(
            f"Cannot infer frequency from median gap of {median_gap_days} days. "
            "Specify periods_per_year explicitly."
        )
```

---

# 4. RISK AND STATISTICAL MEASURES

## 4.1 Volatility

```python
# src/shared/utils/risk_metrics.py

"""Risk metric calculation utilities.

All risk metrics follow the same contract:
- Input: array of returns (specify simple or log)
- Output: scalar or array metric
- NaN handling: documented per function
- Annualization: optional, explicit parameter
"""

import numpy as np
from src.shared.constants.financial import TRADING_DAYS_PER_YEAR


def volatility(
    returns: np.ndarray,
    annualize: bool = True,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
    ddof: int = 1,
) -> float:
    """Calculate volatility (standard deviation of returns).

    Args:
        returns: Array of periodic returns (simple or log).
        annualize: If True, annualize using √N scaling.
        periods_per_year: Periods per year for annualization.
        ddof: Delta degrees of freedom. Use 1 for sample std dev
            (default, appropriate for estimating from sample),
            0 for population std dev.

    Returns:
        Volatility as decimal. NaN if fewer than 2 returns.

    Note:
        Uses sample standard deviation (ddof=1) by default,
        which is the appropriate estimator when computing from
        a sample of returns rather than the full population.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 2:
        return float("nan")

    vol = np.std(returns, ddof=ddof)

    if annualize:
        vol = vol * np.sqrt(periods_per_year)

    return float(vol)
```

## 4.2 Sharpe Ratio

```python
def sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate_annual: float = 0.05,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float | None:
    """Calculate annualized Sharpe ratio.

    Formula: Sharpe = (R_p_annual - R_f) / σ_p_annual

    Where:
        R_p_annual = annualized portfolio return
        R_f = annual risk-free rate
        σ_p_annual = annualized portfolio volatility

    Args:
        returns: Array of periodic simple returns.
        risk_free_rate_annual: Annual risk-free rate as decimal (e.g., 0.05 for 5%).
        periods_per_year: Trading periods per year.

    Returns:
        Annualized Sharpe ratio, or None if calculation is not possible
        (fewer than 2 returns or zero volatility).

    Reference:
        Sharpe, W.F. (1966). "Mutual Fund Performance."
        Journal of Business, 39(1), 119-138.

    Note:
        A Sharpe ratio > 1.0 is generally considered good.
        > 2.0 is very good. > 3.0 is excellent.
        Negative Sharpe means underperforming risk-free rate.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 2:
        return None

    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)

    if std_return == 0:
        return None

    # Convert risk-free rate to per-period
    risk_free_per_period = (1 + risk_free_rate_annual) ** (1 / periods_per_year) - 1

    # Annualize excess return and volatility
    excess_return_annual = annualize_return(
        mean_return - risk_free_per_period, periods_per_year
    )
    vol_annual = annualize_volatility(std_return, periods_per_year)

    return float(excess_return_annual / vol_annual)
```

## 4.3 Sortino Ratio

```python
def sortino_ratio(
    returns: np.ndarray,
    risk_free_rate_annual: float = 0.05,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
    mar: float | None = None,
) -> float | None:
    """Calculate annualized Sortino ratio.

    Like Sharpe, but uses downside deviation instead of total volatility.
    Only penalizes downside risk, not upside volatility.

    Formula: Sortino = (R_p_annual - MAR) / σ_downside_annual

    Args:
        returns: Array of periodic simple returns.
        risk_free_rate_annual: Annual risk-free rate as decimal.
        periods_per_year: Trading periods per year.
        mar: Minimum Acceptable Return (per period). If None, uses
            the per-period risk-free rate.

    Returns:
        Annualized Sortino ratio, or None if not calculable.

    Note:
        Sortino > Sharpe indicates positive skew (more upside
        volatility than downside). Sortino < Sharpe indicates
        negative skew (more downside volatility).
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 2:
        return None

    if mar is None:
        mar = (1 + risk_free_rate_annual) ** (1 / periods_per_year) - 1

    # Downside deviation: std of returns below MAR
    downside_returns = returns[returns < mar] - mar
    if len(downside_returns) == 0:
        return None  # No downside observations

    downside_dev = np.sqrt(np.mean(downside_returns ** 2))

    if downside_dev == 0:
        return None

    mean_return = np.mean(returns)
    excess_return_annual = annualize_return(
        mean_return - mar, periods_per_year
    )
    downside_dev_annual = annualize_volatility(downside_dev, periods_per_year)

    return float(excess_return_annual / downside_dev_annual)
```

## 4.4 Maximum Drawdown

```python
def maximum_drawdown(prices: np.ndarray) -> dict[str, float | int]:
    """Calculate maximum drawdown from a price series.

    Maximum drawdown is the largest peak-to-trough decline observed.

    Args:
        prices: Array of prices (or portfolio values) in chronological order.
            Must have at least 2 elements.

    Returns:
        Dictionary with:
            - max_drawdown: Maximum drawdown as negative decimal
                (e.g., -0.25 for a 25% drawdown)
            - peak_index: Index of the peak before the max drawdown
            - trough_index: Index of the trough of the max drawdown
            - recovery_index: Index where price recovers to peak level,
                or -1 if not yet recovered

    Raises:
        ValueError: If fewer than 2 prices provided.

    Example:
        >>> prices = np.array([100, 110, 95, 85, 90, 105, 115])
        >>> maximum_drawdown(prices)
        {
            'max_drawdown': -0.2273,  # -22.73% from peak of 110 to trough of 85
            'peak_index': 1,
            'trough_index': 3,
            'recovery_index': 5
        }
    """
    prices = np.asarray(prices, dtype=np.float64)

    if len(prices) < 2:
        raise ValueError(
            f"Need at least 2 prices, got {len(prices)}"
        )

    # Running maximum
    running_max = np.maximum.accumulate(prices)

    # Drawdown at each point
    drawdowns = (prices - running_max) / running_max

    # Maximum drawdown
    trough_index = int(np.argmin(drawdowns))
    max_dd = float(drawdowns[trough_index])

    # Peak before trough
    peak_index = int(np.argmax(prices[:trough_index + 1]))

    # Recovery after trough
    recovery_index = -1
    peak_price = prices[peak_index]
    for i in range(trough_index + 1, len(prices)):
        if prices[i] >= peak_price:
            recovery_index = i
            break

    return {
        "max_drawdown": round(max_dd, 6),
        "peak_index": peak_index,
        "trough_index": trough_index,
        "recovery_index": recovery_index,
    }
```

## 4.5 Value at Risk (VaR)

```python
def value_at_risk_historical(
    returns: np.ndarray,
    confidence_level: float = 0.95,
    portfolio_value_cents: int | None = None,
) -> dict[str, float]:
    """Calculate historical Value at Risk (VaR).

    Historical VaR uses the empirical distribution of past returns
    to estimate the maximum expected loss at a given confidence level.

    Args:
        returns: Array of periodic simple returns.
        confidence_level: Confidence level (e.g., 0.95 for 95% VaR).
            Must be between 0 and 1.
        portfolio_value_cents: If provided, VaR is also expressed in cents.

    Returns:
        Dictionary with:
            - var_pct: VaR as a positive percentage (e.g., 0.025 = 2.5% loss)
            - var_cents: VaR in cents (if portfolio_value provided), else None
            - confidence_level: The confidence level used
            - observation_count: Number of returns used
            - worst_return: The worst observed return

    Note:
        Historical VaR assumes that the past return distribution
        is representative of future risk. This assumption breaks
        during regime changes and tail events.

    Reference:
        Jorion, P. (2006). "Value at Risk", 3rd edition.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 30:
        raise ValueError(
            f"Need at least 30 observations for meaningful VaR, "
            f"got {len(returns)}"
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            f"Confidence level must be between 0 and 1, got {confidence_level}"
        )

    # VaR is the return at the (1 - confidence) percentile
    var_pct = abs(float(np.percentile(returns, (1 - confidence_level) * 100)))

    var_cents = None
    if portfolio_value_cents is not None:
        var_cents = round(portfolio_value_cents * var_pct)

    return {
        "var_pct": round(var_pct, 6),
        "var_cents": var_cents,
        "confidence_level": confidence_level,
        "observation_count": len(returns),
        "worst_return": float(np.min(returns)),
    }


def conditional_var(
    returns: np.ndarray,
    confidence_level: float = 0.95,
) -> float:
    """Calculate Conditional VaR (Expected Shortfall / CVaR).

    CVaR is the expected loss given that the loss exceeds VaR.
    It answers: "When things are bad (beyond VaR), how bad on average?"

    CVaR is always >= VaR and captures tail risk better.

    Args:
        returns: Array of periodic simple returns.
        confidence_level: Confidence level (e.g., 0.95).

    Returns:
        CVaR as a positive percentage (e.g., 0.04 = expected 4% loss
        in worst scenarios).

    Raises:
        ValueError: If fewer than 30 observations.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 30:
        raise ValueError(
            f"Need at least 30 observations, got {len(returns)}"
        )

    cutoff = np.percentile(returns, (1 - confidence_level) * 100)
    tail_returns = returns[returns <= cutoff]

    if len(tail_returns) == 0:
        return 0.0

    return abs(float(np.mean(tail_returns)))
```

## 4.6 Correlation

```python
def rolling_correlation(
    returns_a: np.ndarray,
    returns_b: np.ndarray,
    window: int = 60,
) -> np.ndarray:
    """Calculate rolling Pearson correlation between two return series.

    Args:
        returns_a: First return series.
        returns_b: Second return series. Must be same length as returns_a.
        window: Rolling window in periods (default 60 ≈ 3 months daily).

    Returns:
        Array of rolling correlations. First (window-1) values are NaN.
        Values range from -1.0 to +1.0.

    Raises:
        ValueError: If series lengths don't match.
        ValueError: If window < 3 or window > len(returns_a).

    Note:
        Correlations are unstable with small windows and during
        regime changes. Always visualize the rolling series rather
        than relying on a single point estimate.
    """
    if len(returns_a) != len(returns_b):
        raise ValueError(
            f"Series must be same length: {len(returns_a)} vs {len(returns_b)}"
        )

    if window < 3:
        raise ValueError(f"Window must be >= 3, got {window}")

    if window > len(returns_a):
        raise ValueError(
            f"Window ({window}) exceeds data length ({len(returns_a)})"
        )

    a = pd.Series(returns_a)
    b = pd.Series(returns_b)

    return a.rolling(window=window).corr(b).to_numpy()
```

## 4.7 Risk Metric Rules

| Rule | Description |
|------|-------------|
| **RM-001** | All risk metrics return `float \| None` or `dict` — never raise for insufficient data, return None/NaN |
| **RM-002** | Minimum observation counts are enforced: VaR ≥ 30, correlation ≥ window size, volatility ≥ 2 |
| **RM-003** | Always specify ddof (degrees of freedom) explicitly for std dev calculations |
| **RM-004** | Rolling calculations fill insufficient-window positions with NaN, never zero |
| **RM-005** | Correlation matrices must be validated as positive semi-definite |
| **RM-006** | All risk metrics must document their assumptions and limitations |
| **RM-007** | VaR/CVaR are point-in-time estimates — document the observation window used |

---

# 5. FINANCIAL RATIOS

## 5.1 Ratio Calculation Standards

```python
# src/shared/utils/ratios.py

"""Financial ratio calculations.

All ratios follow a consistent contract:
- Inputs are raw financial statement values (in cents where monetary)
- Division by zero returns None (not infinity, not zero)
- Negative values that are meaningless for the ratio return None
- Each function documents its formula and data source
"""


def price_to_earnings(
    market_price_cents: int,
    earnings_per_share_cents: int,
) -> float | None:
    """Calculate Price-to-Earnings (P/E) ratio.

    Formula: P/E = Price / EPS

    Args:
        market_price_cents: Current market price per share in cents.
        earnings_per_share_cents: Trailing 12-month EPS in cents.

    Returns:
        P/E ratio as float, or None if EPS is zero or negative
        (negative P/E is meaningless).

    Note:
        - Trailing P/E uses last 12 months of actual earnings.
        - Forward P/E uses estimated future earnings (separate function).
        - Negative earnings → None (use P/S ratio instead).
    """
    if earnings_per_share_cents <= 0:
        return None

    return market_price_cents / earnings_per_share_cents


def price_to_sales(
    market_cap_cents: int,
    revenue_ttm_cents: int,
) -> float | None:
    """Calculate Price-to-Sales (P/S) ratio.

    Formula: P/S = Market Cap / Revenue (TTM)

    Args:
        market_cap_cents: Total market capitalization in cents.
        revenue_ttm_cents: Trailing 12-month revenue in cents.

    Returns:
        P/S ratio as float, or None if revenue is zero or negative.
    """
    if revenue_ttm_cents <= 0:
        return None

    return market_cap_cents / revenue_ttm_cents


def enterprise_value_to_ebitda(
    market_cap_cents: int,
    total_debt_cents: int,
    cash_cents: int,
    ebitda_ttm_cents: int,
) -> float | None:
    """Calculate Enterprise Value to EBITDA (EV/EBITDA).

    Formula: EV/EBITDA = (Market Cap + Debt - Cash) / EBITDA

    Args:
        market_cap_cents: Total market capitalization in cents.
        total_debt_cents: Total debt (short-term + long-term) in cents.
        cash_cents: Cash and cash equivalents in cents.
        ebitda_ttm_cents: Trailing 12-month EBITDA in cents.

    Returns:
        EV/EBITDA ratio as float, or None if EBITDA is zero or negative.

    Note:
        EV/EBITDA is often preferred over P/E because it is:
        - Capital structure neutral (includes debt)
        - Less affected by accounting differences (depreciation)
        - Comparable across companies with different leverage
    """
    if ebitda_ttm_cents <= 0:
        return None

    enterprise_value_cents = market_cap_cents + total_debt_cents - cash_cents

    return enterprise_value_cents / ebitda_ttm_cents


def return_on_equity(
    net_income_cents: int,
    shareholders_equity_cents: int,
) -> float | None:
    """Calculate Return on Equity (ROE).

    Formula: ROE = Net Income / Shareholders' Equity

    Args:
        net_income_cents: Trailing 12-month net income in cents.
        shareholders_equity_cents: Total shareholders' equity in cents.

    Returns:
        ROE as decimal (0.15 = 15%), or None if equity is zero or negative.

    Note:
        Very high ROE (> 40%) may indicate high leverage rather than
        operational excellence. Cross-reference with D/E ratio.
    """
    if shareholders_equity_cents <= 0:
        return None

    return net_income_cents / shareholders_equity_cents


def debt_to_equity(
    total_debt_cents: int,
    shareholders_equity_cents: int,
) -> float | None:
    """Calculate Debt-to-Equity (D/E) ratio.

    Formula: D/E = Total Debt / Shareholders' Equity

    Args:
        total_debt_cents: Total debt (short + long term) in cents.
        shareholders_equity_cents: Total shareholders' equity in cents.

    Returns:
        D/E ratio as float, or None if equity is zero or negative.

    Note:
        D/E interpretation is sector-dependent:
        - Utilities/REITs: D/E > 1.5 is normal
        - Tech: D/E > 0.5 may warrant scrutiny
        - Financials: Not meaningful (use different leverage metrics)
    """
    if shareholders_equity_cents <= 0:
        return None

    return total_debt_cents / shareholders_equity_cents


def free_cash_flow_yield(
    free_cash_flow_cents: int,
    market_cap_cents: int,
) -> float | None:
    """Calculate Free Cash Flow Yield.

    Formula: FCF Yield = Free Cash Flow / Market Cap

    Args:
        free_cash_flow_cents: TTM free cash flow in cents.
            Can be negative (cash burn).
        market_cap_cents: Market capitalization in cents.

    Returns:
        FCF Yield as decimal (0.05 = 5%), or None if market cap is zero.

    Note:
        - Positive FCF yield means the company generates cash
        - Negative FCF yield means the company burns cash
        - High FCF yield (> 8%) may indicate undervaluation or
          business decline — context is required
    """
    if market_cap_cents <= 0:
        return None

    return free_cash_flow_cents / market_cap_cents
```

## 5.2 Margin Calculations

```python
def gross_margin(
    revenue_cents: int,
    cost_of_goods_sold_cents: int,
) -> float | None:
    """Calculate Gross Margin.

    Formula: Gross Margin = (Revenue - COGS) / Revenue

    Returns:
        Gross margin as decimal (0.65 = 65%), or None if revenue is zero.
    """
    if revenue_cents <= 0:
        return None

    return (revenue_cents - cost_of_goods_sold_cents) / revenue_cents


def operating_margin(
    operating_income_cents: int,
    revenue_cents: int,
) -> float | None:
    """Calculate Operating Margin.

    Formula: Operating Margin = Operating Income / Revenue

    Returns:
        Operating margin as decimal. Can be negative (operating loss).
        None if revenue is zero.
    """
    if revenue_cents <= 0:
        return None

    return operating_income_cents / revenue_cents


def net_profit_margin(
    net_income_cents: int,
    revenue_cents: int,
) -> float | None:
    """Calculate Net Profit Margin.

    Formula: Net Margin = Net Income / Revenue

    Returns:
        Net margin as decimal. Can be negative. None if revenue is zero.
    """
    if revenue_cents <= 0:
        return None

    return net_income_cents / revenue_cents
```

## 5.3 Ratio Calculation Rules

| Rule | Description |
|------|-------------|
| **FR-001** | Division by zero → return None (never Infinity, never raise) |
| **FR-002** | Meaningless negative ratios → return None with documentation explaining why |
| **FR-003** | All monetary inputs are in cents; all ratio outputs are dimensionless floats |
| **FR-004** | TTM (trailing twelve months) is the default period unless specified |
| **FR-005** | Every ratio function documents its formula, data source fields, and interpretation notes |
| **FR-006** | Sector-dependent interpretation must be noted in docstring |
| **FR-007** | Cross-check recommendations noted (e.g., high ROE → also check D/E) |

---

# 6. TECHNICAL INDICATOR STANDARDS

## 6.1 Indicator Function Contract

All technical indicators follow a uniform interface:

```python
# src/quantitative/indicators/interfaces.py

from typing import Protocol
import numpy as np


class TechnicalIndicator(Protocol):
    """Standard interface for all technical indicators.

    All indicators:
    - Accept price/volume data as numpy arrays
    - Return numpy arrays of the same length as input
    - Use NaN for positions where the indicator is undefined
      (e.g., first N-1 values for an N-period moving average)
    - Are pure functions (no side effects, no state)
    - Document their formula and standard interpretation
    """

    @property
    def name(self) -> str:
        """Human-readable indicator name."""
        ...

    @property
    def min_periods(self) -> int:
        """Minimum number of data points needed to produce first valid value."""
        ...

    def calculate(self, **kwargs: np.ndarray) -> np.ndarray:
        """Calculate the indicator values."""
        ...
```

## 6.2 Example: Moving Averages

```python
# src/quantitative/indicators/moving_averages.py

"""Moving average indicators.

All moving averages follow the TechnicalIndicator contract:
- Input: numpy array of prices (typically close prices)
- Output: numpy array of same length, NaN-padded at the start
- Pure functions, no side effects
"""

import numpy as np


def simple_moving_average(
    prices: np.ndarray,
    period: int,
) -> np.ndarray:
    """Calculate Simple Moving Average (SMA).

    Formula: SMA_t = (1/N) × Σ(P_{t-i}) for i = 0 to N-1

    The SMA gives equal weight to all observations in the window.

    Args:
        prices: Array of prices in chronological order.
        period: Lookback period (number of bars to average).

    Returns:
        Array of SMA values. Same length as prices.
        First (period - 1) values are NaN.

    Raises:
        ValueError: If period < 1 or period > len(prices).

    Interpretation:
        - Price > SMA: bullish (price above average)
        - Price < SMA: bearish (price below average)
        - Common periods: 20 (short-term), 50 (medium), 200 (long-term)
    """
    _validate_indicator_inputs(prices, period)

    result = np.full(len(prices), np.nan)
    cumsum = np.cumsum(prices)

    result[period - 1] = cumsum[period - 1] / period
    result[period:] = (cumsum[period:] - cumsum[:-period]) / period

    return result


def exponential_moving_average(
    prices: np.ndarray,
    period: int,
) -> np.ndarray:
    """Calculate Exponential Moving Average (EMA).

    Formula: EMA_t = α × P_t + (1 - α) × EMA_{t-1}
    Where:  α = 2 / (period + 1)

    The EMA gives more weight to recent observations, making it
    more responsive to new information than the SMA.

    Args:
        prices: Array of prices in chronological order.
        period: Lookback period (used to calculate smoothing factor).

    Returns:
        Array of EMA values. Same length as prices.
        First (period - 1) values are NaN.
        The EMA is initialized with the SMA of the first 'period' values.

    Raises:
        ValueError: If period < 1 or period > len(prices).

    Interpretation:
        - EMA responds faster to price changes than SMA
        - Commonly used in MACD (12, 26 period EMAs)
        - Crossover of fast/slow EMA is a common signal
    """
    _validate_indicator_inputs(prices, period)

    result = np.full(len(prices), np.nan)
    alpha = 2.0 / (period + 1)

    # Initialize with SMA
    result[period - 1] = np.mean(prices[:period])

    # Calculate EMA
    for i in range(period, len(prices)):
        result[i] = alpha * prices[i] + (1 - alpha) * result[i - 1]

    return result


def _validate_indicator_inputs(
    prices: np.ndarray,
    period: int,
) -> None:
    """Validate common indicator inputs.

    Raises:
        ValueError: If period is invalid or prices too short.
    """
    if period < 1:
        raise ValueError(f"Period must be >= 1, got {period}")

    if period > len(prices):
        raise ValueError(
            f"Period ({period}) exceeds data length ({len(prices)})"
        )

    if np.any(np.isnan(prices)):
        raise ValueError(
            "Price array contains NaN values. Clean data before "
            "computing indicators."
        )
```

## 6.3 Indicator Output Rules

| Rule | Description |
|------|-------------|
| **TI-001** | Output array length MUST equal input array length |
| **TI-002** | Undefined positions filled with NaN, never zero |
| **TI-003** | Input prices must not contain NaN (validate and reject) |
| **TI-004** | Indicators are pure functions — no internal state between calls |
| **TI-005** | Every indicator documents: formula, standard interpretation, common parameters |
| **TI-006** | Every indicator has a `min_periods` property documenting minimum required data |
| **TI-007** | Multi-value indicators (e.g., Bollinger Bands) return a named dict of arrays |
| **TI-008** | Performance-critical indicators use numpy vectorized operations, not Python loops |

## 6.4 Multi-Value Indicator Example

```python
def bollinger_bands(
    prices: np.ndarray,
    period: int = 20,
    num_std: float = 2.0,
) -> dict[str, np.ndarray]:
    """Calculate Bollinger Bands.

    Components:
        - Middle Band: SMA(period)
        - Upper Band: SMA + (num_std × σ)
        - Lower Band: SMA - (num_std × σ)
        - %B: (Price - Lower) / (Upper - Lower)
        - Bandwidth: (Upper - Lower) / Middle

    Args:
        prices: Array of prices (typically close prices).
        period: SMA period (default 20).
        num_std: Number of standard deviations (default 2.0).

    Returns:
        Dictionary with keys:
            'middle': SMA values
            'upper': Upper band values
            'lower': Lower band values
            'pct_b': %B values (0 = at lower, 1 = at upper)
            'bandwidth': Bandwidth values

    Interpretation:
        - Price near upper band: potentially overbought
        - Price near lower band: potentially oversold
        - Narrow bandwidth: low volatility, potential breakout
        - Wide bandwidth: high volatility
    """
    _validate_indicator_inputs(prices, period)

    middle = simple_moving_average(prices, period)

    # Rolling standard deviation
    rolling_std = np.full(len(prices), np.nan)
    for i in range(period - 1, len(prices)):
        rolling_std[i] = np.std(prices[i - period + 1:i + 1], ddof=0)

    upper = middle + (num_std * rolling_std)
    lower = middle - (num_std * rolling_std)

    # %B calculation
    band_width_raw = upper - lower
    pct_b = np.where(
        band_width_raw > 0,
        (prices - lower) / band_width_raw,
        np.nan,
    )

    # Bandwidth
    bandwidth = np.where(
        middle > 0,
        band_width_raw / middle,
        np.nan,
    )

    return {
        "middle": middle,
        "upper": upper,
        "lower": lower,
        "pct_b": pct_b,
        "bandwidth": bandwidth,
    }
```

---

# 7. PORTFOLIO MATH

## 7.1 Portfolio Return

```python
def portfolio_return(
    weights: np.ndarray,
    returns: np.ndarray,
) -> float:
    """Calculate portfolio return as weighted sum of asset returns.

    Formula: R_portfolio = Σ(w_i × R_i)

    Args:
        weights: Array of portfolio weights. Must sum to 1.0
            (within tolerance of 1e-6).
        returns: Array of asset returns for the same period.
            Must be same length as weights.

    Returns:
        Portfolio return as decimal.

    Raises:
        ValueError: If weights and returns have different lengths.
        ValueError: If weights do not sum to 1.0 (±1e-6).
    """
    weights = np.asarray(weights, dtype=np.float64)
    returns = np.asarray(returns, dtype=np.float64)

    if len(weights) != len(returns):
        raise ValueError(
            f"Weights length ({len(weights)}) must match "
            f"returns length ({len(returns)})"
        )

    weight_sum = np.sum(weights)
    if abs(weight_sum - 1.0) > 1e-6:
        raise ValueError(
            f"Weights must sum to 1.0, got {weight_sum:.8f}"
        )

    return float(np.dot(weights, returns))
```

## 7.2 Portfolio Volatility

```python
def portfolio_volatility(
    weights: np.ndarray,
    covariance_matrix: np.ndarray,
    annualize: bool = True,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Calculate portfolio volatility from weights and covariance matrix.

    Formula: σ_portfolio = √(w^T × Σ × w)

    Where:
        w = weight vector
        Σ = covariance matrix of asset returns

    Args:
        weights: Array of portfolio weights (must sum to 1.0).
        covariance_matrix: NxN covariance matrix of periodic returns.
            Must be symmetric and positive semi-definite.
        annualize: Whether to annualize the result.
        periods_per_year: Periods per year for annualization.

    Returns:
        Portfolio volatility as decimal.

    Raises:
        ValueError: If dimensions don't match.
        ValueError: If covariance matrix is not square.
        ValueError: If covariance matrix is not symmetric (within tolerance).
    """
    weights = np.asarray(weights, dtype=np.float64)
    cov = np.asarray(covariance_matrix, dtype=np.float64)

    n = len(weights)

    if cov.shape != (n, n):
        raise ValueError(
            f"Covariance matrix shape {cov.shape} doesn't match "
            f"number of assets {n}"
        )

    # Verify symmetry
    if not np.allclose(cov, cov.T, atol=1e-10):
        raise ValueError("Covariance matrix is not symmetric")

    portfolio_var = float(weights @ cov @ weights)

    if portfolio_var < 0:
        raise ValueError(
            "Portfolio variance is negative — covariance matrix "
            "may not be positive semi-definite"
        )

    vol = np.sqrt(portfolio_var)

    if annualize:
        vol = vol * np.sqrt(periods_per_year)

    return float(vol)
```

## 7.3 Position Sizing

```python
def kelly_criterion(
    win_probability: float,
    win_loss_ratio: float,
    fraction: float = 0.5,
) -> float:
    """Calculate Kelly Criterion for optimal position sizing.

    Formula: f* = (bp - q) / b

    Where:
        f* = fraction of capital to allocate
        b  = win/loss ratio (average win / average loss)
        p  = probability of winning
        q  = probability of losing (1 - p)

    In practice, we use fractional Kelly (typically half-Kelly)
    to reduce variance.

    Args:
        win_probability: Estimated probability of a winning trade (0-1).
        win_loss_ratio: Ratio of average win to average loss.
            Must be positive.
        fraction: Kelly fraction to use (default 0.5 = half-Kelly).
            Full Kelly is theoretically optimal but very aggressive.

    Returns:
        Recommended position size as fraction of capital (0-1).
        Returns 0.0 if Kelly suggests no bet (negative edge).

    Raises:
        ValueError: If win_probability not in (0, 1).
        ValueError: If win_loss_ratio not positive.
        ValueError: If fraction not in (0, 1].

    Note:
        Kelly Criterion assumes:
        - Known, stable probabilities (rarely true in markets)
        - Binary outcomes (markets have continuous outcomes)
        - No transaction costs
        Always use fractional Kelly and cap with MAX_POSITION_PCT.
    """
    if not 0 < win_probability < 1:
        raise ValueError(
            f"Win probability must be in (0,1), got {win_probability}"
        )

    if win_loss_ratio <= 0:
        raise ValueError(
            f"Win/loss ratio must be positive, got {win_loss_ratio}"
        )

    if not 0 < fraction <= 1:
        raise ValueError(
            f"Fraction must be in (0,1], got {fraction}"
        )

    q = 1 - win_probability
    kelly_full = (win_loss_ratio * win_probability - q) / win_loss_ratio

    if kelly_full <= 0:
        return 0.0

    return kelly_full * fraction


def volatility_based_position_size(
    portfolio_value_cents: int,
    risk_per_trade_pct: float,
    entry_price_cents: int,
    stop_loss_price_cents: int,
) -> int:
    """Calculate position size based on volatility / stop-loss distance.

    This sizes a position so that if the stop-loss is hit, the
    portfolio loses exactly risk_per_trade_pct.

    Formula: Shares = (Portfolio × Risk%) / (Entry - StopLoss)

    Args:
        portfolio_value_cents: Total portfolio value in cents.
        risk_per_trade_pct: Maximum risk per trade as decimal
            (e.g., 0.01 = 1% of portfolio).
        entry_price_cents: Expected entry price in cents.
        stop_loss_price_cents: Stop-loss price in cents.
            Must be below entry price for long positions.

    Returns:
        Number of shares to purchase (rounded down to whole shares).

    Raises:
        ValueError: If stop loss is >= entry price.
        ValueError: If risk_per_trade_pct not in (0, 1).
    """
    if stop_loss_price_cents >= entry_price_cents:
        raise ValueError(
            f"Stop loss ({stop_loss_price_cents}) must be below "
            f"entry price ({entry_price_cents}) for long positions"
        )

    if not 0 < risk_per_trade_pct < 1:
        raise ValueError(
            f"Risk per trade must be in (0,1), got {risk_per_trade_pct}"
        )

    risk_amount_cents = int(portfolio_value_cents * risk_per_trade_pct)
    risk_per_share_cents = entry_price_cents - stop_loss_price_cents

    # Floor division — never round up on position sizing
    shares = risk_amount_cents // risk_per_share_cents

    return shares
```

## 7.4 Portfolio Math Rules

| Rule | Description |
|------|-------------|
| **PM-001** | Portfolio weights must sum to 1.0 (tolerance: ±1e-6). Validate on every operation. |
| **PM-002** | Portfolio weights stored with 6 decimal precision minimum |
| **PM-003** | Position size calculations always round DOWN (floor), never up |
| **PM-004** | Covariance matrices must be validated as symmetric and positive semi-definite |
| **PM-005** | All position sizing must be capped by MAX_POSITION_PCT from guardrails config |
| **PM-006** | Cash position = 1.0 - sum(equity_weights). Cash is an explicit position. |
| **PM-007** | Short positions have negative weights. System is long-only initially (Phase 1-5), so negative weights should raise errors until Phase 6. |

---

# 8. TIME-SERIES DATA HANDLING

## 8.1 Date and Time Standards

```python
# ── All timestamps in UTC ──
from datetime import datetime, timezone, date

# ✓ CORRECT — always timezone-aware
now = datetime.now(timezone.utc)

# ✗ WRONG — naive datetime (no timezone)
now = datetime.now()

# ── Calendar dates use date, not datetime ──
# For "which trading day", use date
trading_date: date = date(2025, 1, 15)

# For "when exactly did we fetch this", use datetime with tz
fetched_at: datetime = datetime(2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

# ── Trading calendar awareness ──
# The system must be aware that markets are closed on:
# - Weekends (Saturday, Sunday)
# - US market holidays (NYSE calendar)
# Use a trading calendar library, never assume all calendar days are trading days
```

## 8.2 Time-Series Alignment

```python
def align_time_series(
    series_a: pd.DataFrame,
    series_b: pd.DataFrame,
    date_column: str = "date",
    method: str = "inner",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Align two time series to common dates.

    When comparing or computing relationships between two time series
    (e.g., correlation between two stocks), they must be aligned to
    the same dates. Missing dates (due to halts, different listing
    dates, etc.) must be handled explicitly.

    Args:
        series_a: First time series with a date column.
        series_b: Second time series with a date column.
        date_column: Name of the date column.
        method: Alignment method:
            - 'inner': Only dates present in BOTH series (default, safest)
            - 'outer': All dates from either series (NaN-fills gaps)

    Returns:
        Tuple of (aligned_a, aligned_b) DataFrames with matching dates.

    Raises:
        ValueError: If no overlapping dates exist.
        ValueError: If method is not 'inner' or 'outer'.

    Warning:
        Using 'outer' join introduces NaN values that must be handled
        before any calculation. Prefer 'inner' unless you have a
        specific reason to include non-overlapping dates.
    """
    if method not in ("inner", "outer"):
        raise ValueError(f"Method must be 'inner' or 'outer', got '{method}'")

    merged = pd.merge(
        series_a, series_b,
        on=date_column,
        how=method,
        suffixes=("_a", "_b"),
    )

    if len(merged) == 0:
        raise ValueError(
            "No overlapping dates between the two series. "
            f"Series A: {series_a[date_column].min()} to {series_a[date_column].max()}, "
            f"Series B: {series_b[date_column].min()} to {series_b[date_column].max()}"
        )

    # Re-split into separate aligned DataFrames
    a_cols = [c for c in merged.columns if c.endswith("_a") or c == date_column]
    b_cols = [c for c in merged.columns if c.endswith("_b") or c == date_column]

    aligned_a = merged[a_cols].rename(
        columns={c: c.removesuffix("_a") for c in a_cols}
    )
    aligned_b = merged[b_cols].rename(
        columns={c: c.removesuffix("_b") for c in b_cols}
    )

    return aligned_a, aligned_b
```

## 8.3 Missing Data Handling

```python
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MISSING DATA POLICY                                            ║
# ║                                                                  ║
# ║  Missing data is NEVER silently filled.                         ║
# ║  Missing data is NEVER silently dropped.                        ║
# ║  The handling strategy must be explicit and documented.         ║
# ╚══════════════════════════════════════════════════════════════════╝
```

| Strategy | When to Use | Implementation |
|----------|-------------|----------------|
| **Reject** | Indicator inputs, ratio denominators | Raise ValueError if NaN present |
| **NaN Propagate** | Indicator outputs for insufficient history | NaN fills propagate naturally |
| **Forward Fill** | Portfolio weights between rebalance dates | `df.ffill()` with explicit max gap |
| **Drop** | Return calculations excluding halted days | `.dropna()` with count logging |
| **Flag** | Data completeness scoring for agent confidence | Set completeness_score < 1.0 |
| **Interpolate** | Never for financial data | Not permitted in this system |

```python
# ── Missing data logging requirement ──
# Whenever data is dropped or filled, log the count and context:

log.info(
    "Missing data handled",
    ticker=ticker,
    strategy="drop",
    rows_affected=missing_count,
    total_rows=total_count,
    date_range=f"{start_date} to {end_date}",
    pct_missing=round(missing_count / total_count, 4),
)

# If missing data exceeds threshold, flag the analysis:
MISSING_DATA_WARN_PCT: float = 0.05   # 5% missing → warning
MISSING_DATA_REJECT_PCT: float = 0.15  # 15% missing → reject analysis
```

## 8.4 Adjusted vs Unadjusted Prices

```python
# ╔══════════════════════════════════════════════════════════════════╗
# ║  SPLIT AND DIVIDEND ADJUSTMENT POLICY                           ║
# ║                                                                  ║
# ║  All historical price data used for return calculations,        ║
# ║  technical indicators, and backtesting MUST be split-adjusted   ║
# ║  and (for total return calculations) dividend-adjusted.         ║
# ║                                                                  ║
# ║  Unadjusted prices are stored alongside adjusted prices but    ║
# ║  are used ONLY for display of actual historical prices.         ║
# ╚══════════════════════════════════════════════════════════════════╝

class AdjustedOHLCV(BaseModel):
    """Price bar with explicit adjustment tracking.

    Both raw and adjusted prices are stored. Computations
    always use adjusted prices. Display may use either.
    """

    ticker: str
    date: date

    # Raw (unadjusted) prices — for display only
    raw_open_cents: int
    raw_high_cents: int
    raw_low_cents: int
    raw_close_cents: int

    # Adjusted prices — for all computations
    adj_open_cents: int
    adj_high_cents: int
    adj_low_cents: int
    adj_close_cents: int

    volume: int

    # Adjustment metadata
    adjustment_factor: float = 1.0   # cumulative split adjustment
    dividend_adjustment: float = 0.0  # cumulative dividend adjustment
    is_adjusted: bool = True

    # Provenance
    source: str
    fetched_at: datetime
```

## 8.5 Time-Series Rules

| Rule | Description |
|------|-------------|
| **TS-001** | Time series must be sorted chronologically (oldest first) before any computation |
| **TS-002** | Never assume consecutive calendar days = consecutive trading days |
| **TS-003** | Always use adjusted prices for return and indicator calculations |
| **TS-004** | Store both adjusted and unadjusted prices; document which is used where |
| **TS-005** | All date ranges are inclusive on both ends: [start_date, end_date] |
| **TS-006** | Missing data handling must be explicit, logged, and documented |
| **TS-007** | Forward-looking data must never be accessible during backtesting (look-ahead bias) |
| **TS-008** | When two time series have different lengths, align before computing (inner join default) |

---

# 9. BACKTESTING STANDARDS

## 9.1 Backtesting Bias Prevention

```python
# ╔══════════════════════════════════════════════════════════════════╗
# ║  BACKTESTING BIAS CHECKLIST                                     ║
# ║                                                                  ║
# ║  Every backtest result MUST include a bias disclosure section   ║
# ║  confirming that these biases have been addressed or           ║
# ║  acknowledged:                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝
```

| Bias | Description | Mitigation |
|------|-------------|------------|
| **Look-Ahead Bias** | Using information not available at the time of the simulated decision | All data access through a point-in-time API that filters by `as_of_date` |
| **Survivorship Bias** | Only backtesting stocks that exist today, ignoring delisted companies | Include delisted stocks in the universe; document if not possible |
| **Selection Bias** | Cherry-picking the strategy that worked best in backtesting | Use out-of-sample testing; split data into train/test periods |
| **Overfitting** | Tuning too many parameters to fit historical data perfectly | Limit free parameters; use walk-forward analysis |
| **Transaction Cost Bias** | Ignoring commissions, slippage, and market impact | Always include configurable commission and slippage (see L0 Section 8) |
| **Execution Bias** | Assuming trades execute at exact signal prices | Use next-bar open price for execution, not signal-bar close |
| **Dividend Bias** | Not accounting for dividends in total return | Use dividend-adjusted prices for return calculations |

## 9.2 Backtest Output Schema

```python
class BacktestResult(BaseModel):
    """Standardized backtest result output.

    Every backtest in the system produces this structure,
    ensuring consistent comparison across strategies.
    """

    # Metadata
    strategy_name: str
    strategy_version: str
    backtest_run_id: str
    run_timestamp: datetime

    # Period
    start_date: date
    end_date: date
    total_trading_days: int
    total_calendar_days: int

    # Returns
    total_return_pct: float         # Total return as decimal
    cagr_pct: float                 # Compound annual growth rate
    benchmark_total_return_pct: float
    benchmark_cagr_pct: float
    alpha_pct: float                # Return above benchmark (annualized)

    # Risk
    annualized_volatility_pct: float
    max_drawdown_pct: float
    max_drawdown_duration_days: int
    sharpe_ratio: float | None
    sortino_ratio: float | None
    calmar_ratio: float | None      # CAGR / Max Drawdown
    var_95_pct: float | None
    cvar_95_pct: float | None

    # Trading
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    average_win_pct: float
    average_loss_pct: float
    profit_factor: float | None     # gross profit / gross loss
    average_holding_period_days: float

    # Costs
    total_commission_cents: int
    total_slippage_cents: int
    commission_bps: float           # Config used
    slippage_bps: float             # Config used

    # Bias Disclosure
    bias_disclosure: BiasDisclosure

    # Raw Data
    equity_curve_cents: list[int]   # Daily portfolio value
    monthly_returns: list[float]    # Monthly returns for tearsheet


class BiasDisclosure(BaseModel):
    """Mandatory bias disclosure for every backtest."""

    survivorship_bias_addressed: bool
    survivorship_bias_notes: str

    look_ahead_bias_addressed: bool
    look_ahead_bias_notes: str

    transaction_costs_included: bool
    commission_bps_used: float
    slippage_bps_used: float

    execution_price_assumption: str   # e.g., "next_bar_open"
    price_adjustment: str             # e.g., "split_and_dividend_adjusted"

    out_of_sample_tested: bool
    train_period: str                 # e.g., "2015-01-01 to 2019-12-31"
    test_period: str                  # e.g., "2020-01-01 to 2024-12-31"

    free_parameter_count: int         # Number of tunable parameters
    overfitting_risk: str             # "LOW" | "MEDIUM" | "HIGH"
    overfitting_risk_rationale: str
```

## 9.3 Backtest Execution Rules

| Rule | Description |
|------|-------------|
| **BT-001** | Simulated trades execute at next bar's open price, never at the signal bar's close |
| **BT-002** | Commission and slippage are always applied (configurable, never zero) |
| **BT-003** | Position sizes rounded down to whole shares |
| **BT-004** | Cash earns the risk-free rate (configurable, default 0) |
| **BT-005** | Results must include a bias disclosure section (BiasDisclosure schema) |
| **BT-006** | Minimum backtest period: 3 years (per L0 config MIN_BACKTEST_YEARS) |
| **BT-007** | Results compared against benchmark (default: SPY) |
| **BT-008** | Walk-forward analysis preferred over single train/test split |
| **BT-009** | Monthly and annual return breakdowns included in results |
| **BT-010** | Equity curve stored for visualization and drawdown analysis |

---

# 10. FLOATING-POINT COMPARISON

## 10.1 Epsilon Comparison Utilities

```python
# src/shared/utils/comparison.py

"""Floating-point comparison utilities.

Financial calculations frequently produce floating-point values
that need to be compared. Direct equality comparison (==) is
unreliable with floats. These utilities provide safe alternatives.
"""

import math
import numpy as np


# Default tolerances by use case
EPSILON_WEIGHT: float = 1e-6     # Portfolio weight comparisons
EPSILON_RETURN: float = 1e-8     # Return comparisons
EPSILON_RATIO: float = 1e-4      # Financial ratio comparisons
EPSILON_PRICE: float = 0.0       # Price comparisons (use exact int cents)


def float_equals(
    a: float,
    b: float,
    epsilon: float = EPSILON_RETURN,
) -> bool:
    """Check if two floats are equal within tolerance.

    Args:
        a: First value.
        b: Second value.
        epsilon: Maximum allowed difference.

    Returns:
        True if |a - b| <= epsilon.
    """
    return abs(a - b) <= epsilon


def float_greater_than(
    a: float,
    b: float,
    epsilon: float = EPSILON_RETURN,
) -> bool:
    """Check if a is meaningfully greater than b (not just floating-point noise).

    Returns True only if a exceeds b by more than epsilon.
    """
    return a - b > epsilon


def float_less_than(
    a: float,
    b: float,
    epsilon: float = EPSILON_RETURN,
) -> bool:
    """Check if a is meaningfully less than b."""
    return b - a > epsilon


def weights_sum_to_one(weights: np.ndarray) -> bool:
    """Check if portfolio weights sum to 1.0 within tolerance."""
    return float_equals(float(np.sum(weights)), 1.0, EPSILON_WEIGHT)


def is_valid_probability(value: float) -> bool:
    """Check if a value is a valid probability [0.0, 1.0]."""
    return -EPSILON_RETURN <= value <= 1.0 + EPSILON_RETURN
```

## 10.2 Floating-Point Rules

| Rule | Description |
|------|-------------|
| **FP-001** | Never use `==` to compare two float values. Use `float_equals()` with appropriate epsilon. |
| **FP-002** | Never use `float` for monetary amounts. Use `int` cents. |
| **FP-003** | Use `math.isnan()` or `np.isnan()` to check for NaN, never `x == float('nan')` (which is always False). |
| **FP-004** | Use `math.isinf()` or `np.isinf()` to check for infinity. |
| **FP-005** | When summing many small floats, use `math.fsum()` or `np.sum()` instead of Python's built-in `sum()` for better precision. |
| **FP-006** | Document the epsilon value and rationale when it differs from the default. |

---

# 11. DISPLAY AND FORMATTING

## 11.1 Standard Display Formats

All formatting happens in the **presentation layer only**. Internal
computations always use raw numeric types.

```python
# src/shared/utils/formatting.py

"""Display formatting utilities.

These functions convert internal numeric representations to
human-readable strings. They are used ONLY in the presentation
layer (reports, dashboard, CLI output).

NEVER use the output of these functions for further computation.
"""


def format_return(value: float, decimals: int = 2) -> str:
    """Format a return value as a percentage string.

    Args:
        value: Return as decimal (e.g., 0.0523).
        decimals: Number of decimal places (default 2).

    Returns:
        Formatted string like "+5.23%" or "-3.10%".

    Examples:
        >>> format_return(0.0523)
        '+5.23%'
        >>> format_return(-0.031)
        '-3.10%'
        >>> format_return(0.0)
        '0.00%'
    """
    pct = value * 100
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.{decimals}f}%"


def format_ratio(value: float | None, decimals: int = 2) -> str:
    """Format a financial ratio for display.

    Args:
        value: Ratio value, or None if not calculable.
        decimals: Decimal places.

    Returns:
        Formatted string like "15.23" or "N/A" for None.
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_large_number(cents: int) -> str:
    """Format large monetary values with K/M/B suffixes.

    Args:
        cents: Value in cents.

    Returns:
        Human-readable string like "$1.5B" or "$423.2M" or "$85.0K".

    Examples:
        >>> format_large_number(150_000_000_000)  # $1.5B
        '$1.50B'
        >>> format_large_number(42_320_000_00)    # $423.2M
        '$423.20M'
    """
    dollars = abs(cents) / 100
    sign = "-" if cents < 0 else ""

    if dollars >= 1_000_000_000:
        return f"{sign}${dollars / 1_000_000_000:.2f}B"
    elif dollars >= 1_000_000:
        return f"{sign}${dollars / 1_000_000:.2f}M"
    elif dollars >= 1_000:
        return f"{sign}${dollars / 1_000:.2f}K"
    else:
        return f"{sign}${dollars:.2f}"


def format_sharpe(value: float | None) -> str:
    """Format Sharpe/Sortino ratio for display.

    Includes qualitative assessment.

    Returns:
        String like "1.85 (Good)" or "0.42 (Poor)".
    """
    if value is None:
        return "N/A"

    if value >= 3.0:
        quality = "Excellent"
    elif value >= 2.0:
        quality = "Very Good"
    elif value >= 1.0:
        quality = "Good"
    elif value >= 0.5:
        quality = "Adequate"
    elif value >= 0:
        quality = "Poor"
    else:
        quality = "Negative"

    return f"{value:.2f} ({quality})"
```

## 11.2 Display Formatting Rules

| Rule | Description |
|------|-------------|
| **DF-001** | Formatting functions live in `src/shared/utils/formatting.py` only |
| **DF-002** | Formatting is the last step — never format then compute |
| **DF-003** | Returns displayed as percentages with sign: "+5.23%", "-3.10%" |
| **DF-004** | Monetary values displayed as USD: "$1,500.99", "-$42.10" |
| **DF-005** | Large numbers use suffixes: "$1.5B", "$423M", "$85K" |
| **DF-006** | Ratios that are None display as "N/A", never "0" or blank |
| **DF-007** | All formatted output includes units or context (%, $, x, bps) |

---

# 12. CALCULATION VERIFICATION STANDARDS

## 12.1 Cross-Check Requirements

Every financial calculation module must include verification logic:

```python
# ── Balance sheet identity ──
def verify_balance_sheet(
    total_assets_cents: int,
    total_liabilities_cents: int,
    shareholders_equity_cents: int,
    tolerance_cents: int = 100,  # $1.00 tolerance for rounding
) -> bool:
    """Verify A = L + E within tolerance.

    If this fails, the source data is suspect and should be flagged.
    """
    expected = total_liabilities_cents + shareholders_equity_cents
    return abs(total_assets_cents - expected) <= tolerance_cents


# ── Cash flow reconciliation ──
def verify_cash_flow_statement(
    operating_cf_cents: int,
    investing_cf_cents: int,
    financing_cf_cents: int,
    net_change_in_cash_cents: int,
    tolerance_cents: int = 100,
) -> bool:
    """Verify OCF + ICF + FCF = Net change in cash."""
    calculated = operating_cf_cents + investing_cf_cents + financing_cf_cents
    return abs(calculated - net_change_in_cash_cents) <= tolerance_cents


# ── Portfolio weight verification ──
def verify_portfolio_weights(
    weights: dict[str, float],
    include_cash: bool = True,
) -> bool:
    """Verify portfolio weights sum to 1.0."""
    total = sum(weights.values())
    return float_equals(total, 1.0, EPSILON_WEIGHT)
```

## 12.2 Anomaly Detection in Calculations

```python
# ── Flag results that seem implausible ──
RATIO_ANOMALY_THRESHOLDS: dict[str, tuple[float, float]] = {
    # ratio_name: (min_reasonable, max_reasonable)
    "pe_ratio": (0.0, 500.0),
    "ps_ratio": (0.0, 100.0),
    "ev_ebitda": (0.0, 200.0),
    "roe": (-2.0, 2.0),           # -200% to +200%
    "debt_to_equity": (0.0, 20.0),
    "gross_margin": (-1.0, 1.0),
    "net_margin": (-5.0, 1.0),    # Can be deeply negative
    "fcf_yield": (-1.0, 1.0),
}


def check_ratio_anomaly(
    ratio_name: str,
    value: float,
) -> bool:
    """Check if a computed ratio falls outside reasonable bounds.

    Returns True if the value is anomalous (outside expected range).
    Anomalous values are not necessarily wrong — they should be
    flagged for review, not discarded.

    Note:
        These thresholds are heuristics. Some legitimate companies
        have extreme ratios (early-stage growth, turnarounds, etc.).
        The flag means "double-check this", not "this is wrong".
    """
    if ratio_name not in RATIO_ANOMALY_THRESHOLDS:
        return False

    min_val, max_val = RATIO_ANOMALY_THRESHOLDS[ratio_name]
    return value < min_val or value > max_val
```

## 12.3 Verification Rules

| Rule | Description |
|------|-------------|
| **VR-001** | Balance sheet identity (A = L + E) verified on every financial statement ingestion |
| **VR-002** | Cash flow statement reconciled on every ingestion |
| **VR-003** | Portfolio weights verified to sum to 1.0 after every modification |
| **VR-004** | Computed ratios checked against anomaly thresholds; anomalies logged and flagged |
| **VR-005** | Return calculations spot-checked: manual verification of first and last values against source data |
| **VR-006** | Technical indicators verified against a reference implementation for at least 3 test cases per indicator |
| **VR-007** | Backtest results verified: total return matches equity curve endpoint |

---

# 13. REFERENCE FORMULAS

Quick reference for all financial formulas used in the system.
Each entry links to the function that implements it.

```text
RETURN CALCULATIONS
─────────────────────────────────────────────────────────────
Simple Return:       R = (P₁ - P₀) / P₀
Log Return:          r = ln(P₁ / P₀)
Total Return:        R = (P₁ + D - P₀) / P₀
Cumulative Return:   ∏(1 + Rᵢ) - 1
CAGR:                (1 + R_total)^(1/years) - 1

ANNUALIZATION
─────────────────────────────────────────────────────────────
Return:              R_annual = (1 + R_period)^N - 1
Volatility:          σ_annual = σ_period × √N
(N = periods per year; 252 daily, 52 weekly, 12 monthly)

RISK METRICS
─────────────────────────────────────────────────────────────
Volatility:          σ = std(returns, ddof=1)
Sharpe Ratio:        (R_p - R_f) / σ_p  (annualized)
Sortino Ratio:       (R_p - MAR) / σ_downside  (annualized)
Max Drawdown:        max((peak - trough) / peak)
VaR (Historical):    percentile(returns, (1 - confidence) × 100)
CVaR:                mean(returns | returns ≤ VaR)
Calmar Ratio:        CAGR / |Max Drawdown|

PORTFOLIO MATH
─────────────────────────────────────────────────────────────
Portfolio Return:    R_p = Σ(wᵢ × Rᵢ)
Portfolio Variance:  σ²_p = w^T × Σ × w
Portfolio Vol:       σ_p = √(w^T × Σ × w)
Kelly Criterion:     f* = (bp - q) / b  (use half-Kelly)

VALUATION RATIOS
─────────────────────────────────────────────────────────────
P/E:                 Price / EPS
P/S:                 Market Cap / Revenue
EV/EBITDA:           (Market Cap + Debt - Cash) / EBITDA
ROE:                 Net Income / Equity
D/E:                 Total Debt / Equity
FCF Yield:           FCF / Market Cap
Gross Margin:        (Revenue - COGS) / Revenue
Operating Margin:    Operating Income / Revenue
Net Margin:          Net Income / Revenue

TECHNICAL INDICATORS
─────────────────────────────────────────────────────────────
SMA:                 (1/N) × Σ(Pᵢ)  for i in window
EMA:                 α × P_t + (1-α) × EMA_{t-1}  where α = 2/(N+1)
Bollinger Upper:     SMA + (k × σ_rolling)
Bollinger Lower:     SMA - (k × σ_rolling)
RSI:                 100 - 100/(1 + avg_gain/avg_loss)
```

---

# 14. TESTING REQUIREMENTS FOR FINANCIAL CODE

Financial calculation code has **elevated testing requirements** beyond
the general testing standards (see `L4-conventions/testing-standards.md`).

## 14.1 Mandatory Test Categories

| Category | Description | Requirement |
|----------|-------------|-------------|
| **Known-Value Tests** | Compare output against hand-calculated or textbook values | Every formula must have at least 3 known-value test cases |
| **Edge Case Tests** | Zero inputs, single element, negative values, NaN | Every function must handle all edge cases documented in its docstring |
| **Boundary Tests** | Values at exact thresholds (e.g., confidence = 0.0, 1.0) | Every threshold boundary tested |
| **Precision Tests** | Verify output precision meets documented standards | Monetary: exact to the cent. Ratios: 4+ decimals. |
| **Reference Tests** | Compare against trusted external library (numpy, scipy, ta-lib) | Every indicator verified against at least one reference |
| **Symmetry Tests** | Properties that must hold (e.g., correlation(A,B) = correlation(B,A)) | All symmetric operations tested |
| **Monotonicity Tests** | Properties like "longer SMA period → smoother output" | Where applicable |
| **Round-Trip Tests** | Convert to cents → compute → convert back; verify no loss | All monetary conversion paths |

## 14.2 Test Data Requirements

```python
# ── Known test vectors for verification ──
# Every indicator / metric must have reference test data in:
# tests/fixtures/financial/

# Example: tests/fixtures/financial/sma_test_vectors.py
SMA_TEST_VECTORS = [
    {
        "name": "Basic 3-period SMA",
        "prices": [10, 20, 30, 40, 50],
        "period": 3,
        "expected": [None, None, 20.0, 30.0, 40.0],
        "source": "Hand-calculated",
    },
    {
        "name": "SMA matches Yahoo Finance for AAPL 2024-01-02 to 2024-01-10",
        "prices": [18529, 18472, 18160, 18226, 18506],  # cents
        "period": 5,
        "expected": [None, None, None, None, 18378.6],  # cents
        "source": "Yahoo Finance SMA(5) verified 2024-01-15",
    },
]
```

## 14.3 Financial Test Markers

```python
# ── All financial calculation tests use the @pytest.mark.financial marker ──

import pytest

@pytest.mark.financial
class TestSharpeRatio:
    """Tests for Sharpe ratio calculation.

    Reference: Sharpe (1966), verified against QuantLib and numpy.
    """

    def test_known_value_positive_sharpe(self):
        """Verify Sharpe ratio against hand-calculated example."""
        ...

    def test_known_value_negative_sharpe(self):
        """Negative Sharpe when returns below risk-free rate."""
        ...

    def test_zero_volatility_returns_none(self):
        """If all returns are identical, volatility is zero → None."""
        ...

    def test_single_return_returns_none(self):
        """Cannot compute std dev from single observation."""
        ...

    def test_matches_reference_implementation(self):
        """Compare against numpy-based manual calculation."""
        ...

    def test_annualization_daily(self):
        """Verify daily → annual annualization is correct."""
        ...

    def test_annualization_monthly(self):
        """Verify monthly → annual annualization is correct."""
        ...
```

---

# 15. CROSS-REFERENCES

| Document                             | Location                                              |
|--------------------------------------|-------------------------------------------------------|
| L0: System Vision                    | `specs/L0-system-vision.md`                           |
| L0: Configurable Parameters          | `specs/L0-system-vision.md` Section 8                 |
| L4: Coding Standards                 | `specs/L4-conventions/coding-standards.md`             |
| L4: Testing Standards                | `specs/L4-conventions/testing-standards.md`            |
| Guardrails: Financial                | `specs/guardrails/financial-guardrails.md`             |
| Guardrails: Data Quality             | `specs/guardrails/data-quality-guardrails.md`          |
| L2: Technical Indicators Module      | `specs/L2-modules/quantitative/technical-indicators.md`|
| L2: Backtesting Engine Module        | `specs/L2-modules/quantitative/backtesting-engine.md`  |
| L2: Risk Analytics Module            | `specs/L2-modules/risk/risk-analytics.md`             |

---
```
