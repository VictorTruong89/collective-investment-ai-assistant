## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This module is the **quality gate** of the data pipeline. Every data point
that enters the system — every OHLCV bar, every financial statement, every
company profile — passes through this module before it is stored. It is
the last line of defense between the external world's messy, inconsistent,
occasionally wrong data and the clean, validated internal dataset that
every analysis, signal, and recommendation depends on.

A single corrupt price bar that slips through validation can cascade into
wrong return calculations, wrong technical indicators, wrong risk metrics,
and ultimately wrong investment recommendations. This module exists to
prevent that.

## Module Identity

| Attribute          | Value                                                   |
|--------------------|---------------------------------------------------------|
| Module Name        | Data Validation                                          |
| Domain             | Data Engine                                              |
| Phase              | 1                                                        |
| Priority           | CRITICAL — no data enters the system without validation  |
| Location           | `src/data_engine/validation/`                            |
| Primary Service    | `ValidationPipeline`                                     |
| Key Files          | `pipeline.py`, `quality_rules.py`, `anomaly_detection.py`, `registry.py`, `models.py` |
| L1 Reference       | `specs/L1-domains/data-engine.md` Section 5.2, Item 3   |
| L2 Dependency      | Called by `L2-modules/data-engine/market-data-ingestion.md` FR-001 Step 4 |
| L4 References      | `data-pipeline-standards.md` Section 6, `financial-calculation-standards.md` Section 12, `testing-standards.md` |

---

# 1. MODULE OVERVIEW

## 1.1 Responsibilities

```text
THIS MODULE DOES:
  ✓ Define a composable pipeline of validation checks
  ✓ Run schema validation (Pydantic model validators)
  ✓ Run domain-specific quality rules (OHLCV, financials, etc.)
  ✓ Run statistical anomaly detection (unusual values, outliers)
  ✓ Classify each data point: ACCEPT, FLAG, or REJECT
  ✓ Attach quality warnings to flagged data points
  ✓ Report aggregate validation results (counts, rule IDs)
  ✓ Provide a registry of all active validation rules
  ✓ Allow new rules to be added without modifying existing rules
  ✓ Support configurable thresholds for rules
  ✓ Produce structured validation reports for monitoring

THIS MODULE DOES NOT:
  ✗ Modify data (validation is read-only, never transforms)
  ✗ Store or persist data (delegates to Repository)
  ✗ Fetch data from providers (receives data from IngestionService)
  ✗ Decide whether to retry or fallback (caller's responsibility)
  ✗ Compute financial metrics or indicators
  ✗ Make investment judgments about the data
  ✗ Cache anything (stateless)
```

## 1.2 Core Design Principle

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   VALIDATION NEVER MODIFIES DATA.                               ║
║                                                                  ║
║   Validation classifies data into three buckets:                ║
║                                                                  ║
║     ACCEPT  — Clean data. Store as-is.                          ║
║     FLAG    — Suspicious but plausible. Store with warnings.    ║
║     REJECT  — Invalid or corrupt. Do not store.                 ║
║                                                                  ║
║   If a data point is wrong, it is rejected.                     ║
║   If a data point is unusual but possibly correct, it is        ║
║   flagged — the downstream consumer can decide how to weight    ║
║   it in their analysis.                                          ║
║                                                                  ║
║   Validation does not "fix" data. Fixing data introduces        ║
║   assumptions that may be wrong. The system prefers honest       ║
║   gaps over silently fabricated fills.                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.3 Module Context Diagram

```text
                ┌──────────────────────────────────────────┐
                │       INGESTION SERVICE (Caller)          │
                │                                           │
                │  Receives raw bars from provider adapter  │
                │  Passes each bar through validation       │
                └───────────────────┬───────────────────────┘
                                    │
                                    │ list[OHLCVBar] (raw from provider)
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                    DATA VALIDATION MODULE                             │
│                                                                       │
│   ┌────────────────────────────────────────────────────────────┐     │
│   │                  ValidationPipeline                         │     │
│   │                                                             │     │
│   │  Orchestrates all validation checks in order:              │     │
│   │                                                             │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 1. Schema         │ ← Pydantic model validation         │     │
│   │  │    Validation     │   (type checks, field constraints)  │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 2. Quality Rules │ ← Domain-specific business rules    │     │
│   │  │    (Composable)  │   (high>=low, no weekends, etc.)    │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 3. Anomaly       │ ← Statistical outlier detection     │     │
│   │  │    Detection     │   (extreme moves, volume spikes)    │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 4. Cross-Record  │ ← Multi-bar consistency checks     │     │
│   │  │    Validation    │   (sequential dates, price gaps)    │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 5. Outcome       │ ← Classify: ACCEPT / FLAG / REJECT │     │
│   │  │    Determination │                                      │     │
│   │  └──────────────────┘                                      │     │
│   │                                                             │     │
│   └────────────────────────────────────────────────────────────┘     │
│                                                                       │
│   ┌────────────────────┐    ┌────────────────────┐                   │
│   │  Rule Registry     │    │  Threshold Config  │                   │
│   │                    │    │                    │                   │
│   │  Catalog of all    │    │  Configurable      │                   │
│   │  active rules      │    │  thresholds per    │                   │
│   │  with metadata     │    │  data type         │                   │
│   └────────────────────┘    └────────────────────┘                   │
│                                                                       │
└──────────────────────────────┬────────────────────────────────────────┘
                               │
                               │ ValidationBatchResult
                               ▼
                ┌──────────────────────────────────────────┐
                │       INGESTION SERVICE (Caller)          │
                │                                           │
                │  Receives classification for each bar:   │
                │  ACCEPT → store                          │
                │  FLAG   → store with warnings            │
                │  REJECT → skip, log                      │
                └──────────────────────────────────────────┘
```

---

# 2. DATA MODELS

## 2.1 Validation Input/Output Models

```python
# src/data_engine/validation/models.py

"""Data models for the validation module.

These models define the interface between the validation pipeline
and its callers (primarily IngestionService).
"""

from pydantic import BaseModel, Field
from datetime import date, datetime, timezone
from enum import Enum


# ── Severity Levels ──

class IssueSeverity(str, Enum):
    """Severity of a validation issue.

    Determines the outcome classification:
    - REJECT: Data point is invalid, do not store
    - FLAG: Data point is suspicious, store with warning
    - INFO: Noteworthy but not actionable, no impact on storage
    """

    REJECT = "REJECT"
    FLAG = "FLAG"
    INFO = "INFO"


# ── Outcome Classification ──

class ValidationOutcomeType(str, Enum):
    """Final classification of a validated data point."""

    ACCEPT = "ACCEPT"     # Clean data, store normally
    FLAG = "FLAG"         # Suspicious, store with quality_warnings
    REJECT = "REJECT"     # Invalid, do not store


# ── Individual Issue ──

class QualityIssue(BaseModel):
    """A single quality issue detected by a validation rule.

    Every issue is self-contained: it identifies what rule found it,
    how severe it is, which field it affects, what was expected vs
    actual, and a human-readable message.
    """

    rule_id: str = Field(
        ...,
        description="Unique identifier for the rule that detected this issue",
        examples=["DQ-OHLCV-001", "DQ-OHLCV-005", "DQ-FIN-BS-001"],
    )
    rule_name: str = Field(
        ...,
        description="Human-readable rule name",
        examples=["Price Consistency Check", "Weekend Date Rejection"],
    )
    severity: IssueSeverity = Field(
        ...,
        description="REJECT, FLAG, or INFO",
    )
    category: str = Field(
        ...,
        description="Rule category for grouping",
        examples=["schema", "quality", "anomaly", "cross_record"],
    )
    field: str = Field(
        ...,
        description="The data field that triggered the issue",
        examples=["close_cents", "volume", "date", "high_cents"],
    )
    message: str = Field(
        ...,
        description="Human-readable description of the issue",
    )
    actual_value: str = Field(
        default="",
        description="The actual value that caused the issue",
    )
    expected_range: str = Field(
        default="",
        description="What the value should be or the acceptable range",
    )
    context: dict = Field(
        default_factory=dict,
        description="Additional context for debugging",
    )


# ── Single Data Point Outcome ──

class ValidationOutcome(BaseModel):
    """Validation result for a single data point.

    Contains the final classification and all issues found.
    A data point can have multiple issues at different severities.
    The worst severity determines the outcome.
    """

    outcome: ValidationOutcomeType
    issues: list[QualityIssue] = Field(default_factory=list)

    @property
    def is_accepted(self) -> bool:
        """Data point should be stored (ACCEPT or FLAG)."""
        return self.outcome in (
            ValidationOutcomeType.ACCEPT,
            ValidationOutcomeType.FLAG,
        )

    @property
    def is_rejected(self) -> bool:
        """Data point should not be stored."""
        return self.outcome == ValidationOutcomeType.REJECT

    @property
    def reject_reasons(self) -> list[QualityIssue]:
        """Issues with REJECT severity."""
        return [i for i in self.issues if i.severity == IssueSeverity.REJECT]

    @property
    def flags(self) -> list[QualityIssue]:
        """Issues with FLAG severity."""
        return [i for i in self.issues if i.severity == IssueSeverity.FLAG]

    @property
    def info_items(self) -> list[QualityIssue]:
        """Issues with INFO severity."""
        return [i for i in self.issues if i.severity == IssueSeverity.INFO]

    @property
    def warning_messages(self) -> list[str]:
        """Extract warning messages for attaching to stored data."""
        return [
            f"[{i.rule_id}] {i.message}"
            for i in self.issues
            if i.severity in (IssueSeverity.REJECT, IssueSeverity.FLAG)
        ]


# ── Batch Result ──

class ValidationBatchResult(BaseModel):
    """Aggregate validation result for a batch of data points.

    Used by IngestionService to understand the overall quality
    of a provider's response.
    """

    total_count: int = 0
    accepted_count: int = 0
    flagged_count: int = 0
    rejected_count: int = 0

    # Issue breakdown
    issues_by_rule: dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues grouped by rule_id",
    )
    issues_by_severity: dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues grouped by severity",
    )

    # Individual outcomes
    outcomes: list[ValidationOutcome] = Field(
        default_factory=list,
        description="Per-data-point outcomes (parallel to input list)",
    )

    # Accepted data (convenience)
    accepted_indices: list[int] = Field(
        default_factory=list,
        description="Indices of accepted data points (ACCEPT + FLAG)",
    )
    rejected_indices: list[int] = Field(
        default_factory=list,
        description="Indices of rejected data points",
    )

    @property
    def acceptance_rate(self) -> float:
        """Percentage of data points accepted (ACCEPT + FLAG)."""
        if self.total_count == 0:
            return 1.0
        return (self.accepted_count + self.flagged_count) / self.total_count

    @property
    def rejection_rate(self) -> float:
        """Percentage of data points rejected."""
        if self.total_count == 0:
            return 0.0
        return self.rejected_count / self.total_count

    @property
    def has_rejections(self) -> bool:
        return self.rejected_count > 0

    @property
    def has_flags(self) -> bool:
        return self.flagged_count > 0


# ── Rule Metadata ──

class ValidationRuleInfo(BaseModel):
    """Metadata describing a validation rule.

    Used by the rule registry for documentation, monitoring,
    and configuration.
    """

    rule_id: str
    rule_name: str
    description: str
    category: str                                # "schema" | "quality" | "anomaly" | "cross_record"
    severity: IssueSeverity
    data_types: list[str]                        # Which data types this rule applies to
    is_configurable: bool = False                # Whether thresholds are configurable
    config_keys: list[str] = Field(default_factory=list)
    phase: int = 1                               # Which phase this rule was introduced
    enabled: bool = True
```

---

# 3. FUNCTIONAL REQUIREMENTS

## FR-001: Validate a Batch of OHLCV Bars

```text
ID:           FR-001
Title:        Validate a Batch of OHLCV Bars
Priority:     CRITICAL
Trigger:      Called by IngestionService after provider adapter returns bars
```

### Description

Validate a list of OHLCV bars received from a provider adapter. Run all
applicable validation checks on each bar and produce a batch result that
classifies each bar as ACCEPT, FLAG, or REJECT.

### Input

```python
class ValidateOHLCVRequest(BaseModel):
    """Input to the OHLCV validation pipeline."""

    bars: list[OHLCVBar] = Field(
        ...,
        description="Bars to validate, in chronological order",
    )
    ticker: str = Field(
        ...,
        description="Ticker these bars belong to",
    )
    prior_bar: OHLCVBar | None = Field(
        default=None,
        description="The most recent stored bar before this batch. "
                    "Used for cross-record checks (e.g., daily change).",
    )
    historical_avg_volume: int | None = Field(
        default=None,
        description="Average daily volume for volume spike detection. "
                    "Typically 20-day average from stored history.",
    )
```

### Processing Steps

```text
Step 1: PREPARE CONTEXT
  1.1  Sort bars by date ascending (if not already sorted)
  1.2  Load applicable validation rules from the RuleRegistry
       for data_type="ohlcv"
  1.3  Load configurable thresholds from validation config
  1.4  Set prior_bar context:
       - If prior_bar provided → use it
       - Else → first bar has no prior context

Step 2: VALIDATE EACH BAR
  For each bar (in chronological order):

  2.1  Run SCHEMA VALIDATION:
       - Pydantic model validation already happened at creation time
       - Check additional schema constraints not in model:
         * ticker matches expected ticker
         * date is within a reasonable range (not future, not > 50 years ago)

  2.2  Run QUALITY RULES:
       - Each rule receives the bar + context (prior bar, avg volume)
       - Each rule returns: list[QualityIssue] (empty if passed)
       - Rules are independent — each runs regardless of others
       - Rules ordered by severity (REJECT rules first for efficiency)

  2.3  Run ANOMALY DETECTION:
       - Statistical checks that depend on context (history, averages)
       - Only run if historical_avg_volume is provided

  2.4  Run CROSS-RECORD VALIDATION:
       - Compare this bar against prior_bar (if available)
       - Check daily price change magnitude
       - Check date sequencing (no gaps that aren't weekends/holidays)

  2.5  COLLECT ALL ISSUES for this bar
       - Merge issues from all stages
       - Determine outcome: ACCEPT / FLAG / REJECT
       - Update prior_bar to current bar for next iteration

Step 3: AGGREGATE RESULTS
  3.1  Count: accepted, flagged, rejected
  3.2  Group issues by rule_id and severity
  3.3  Build accepted_indices and rejected_indices lists
  3.4  Construct ValidationBatchResult

Step 4: LOG RESULTS
  4.1  Log aggregate counts at INFO level
  4.2  Log individual rejections at WARNING level (with details)
  4.3  Log flagged anomalies at INFO level

Step 5: RETURN
  5.1  Return ValidationBatchResult
```

### Output

```python
# Returns ValidationBatchResult as defined in Section 2.1
```

### Error Cases

| ID   | Condition                          | Behavior                                               |
|------|------------------------------------|---------------------------------------------------------|
| E-01 | Empty bars list                    | Return ValidationBatchResult with total_count=0, all counts 0 |
| E-02 | Bar ticker doesn't match expected  | REJECT that bar with rule DQ-OHLCV-TICKER-MISMATCH     |
| E-03 | Bar date is in the future          | REJECT that bar with rule DQ-OHLCV-FUTURE-DATE         |
| E-04 | Validation rule throws exception   | Log ERROR, skip that rule for that bar, continue        |
| E-05 | All bars rejected                  | Return result with accepted_count=0 (caller handles)   |

### Important Constraints

```text
⚠  VALIDATION CONSTRAINTS:
  - Validation is STATELESS between calls — no persistent state
  - Validation is PURE — same input always produces same output
  - Validation is FAST — no I/O, no external calls, no DB queries
  - Validation NEVER modifies the input data
  - Validation rules are INDEPENDENT — one rule's result doesn't
    affect another rule's execution
  - Exception in one rule does NOT stop other rules from running
```

---

## FR-002: Validate Financial Statement Data

```text
ID:           FR-002
Title:        Validate Financial Statement Data
Priority:     HIGH
Trigger:      Called by FundamentalDataIngestion (Phase 2)
Phase:        2
```

### Description

Validate income statements, balance sheets, and cash flow statements
for internal consistency and plausibility.

### Processing Steps

```text
Step 1: RUN SCHEMA VALIDATION
  1.1  Pydantic model validation (types, required fields, constraints)

Step 2: RUN IDENTITY CHECKS (cross-field consistency)
  2.1  Income Statement:
       - gross_profit ≈ revenue - cost_of_revenue (±$1 tolerance)
  2.2  Balance Sheet:
       - total_assets ≈ total_liabilities + shareholders_equity (±$1)
  2.3  Cash Flow Statement:
       - operating + investing + financing ≈ net_change_in_cash (±$1)
       - free_cash_flow ≈ operating - capex (±$1)

Step 3: RUN PLAUSIBILITY CHECKS
  3.1  Revenue should be positive (FLAG if zero or negative)
  3.2  Period type must be "annual" or "quarterly"
  3.3  Fiscal year must be within reasonable range (1990-current+1)
  3.4  Filing date should be after period_end_date
  3.5  Quarterly data: fiscal_quarter must be 1-4

Step 4: RUN TEMPORAL CONSISTENCY (if prior periods available)
  4.1  Revenue change > 200% year-over-year → FLAG
  4.2  Margins swinging from positive to deeply negative → FLAG
  4.3  Total assets changing by > 100% → FLAG

Step 5: CLASSIFY AND RETURN
```

---

## FR-003: Register and Manage Validation Rules

```text
ID:           FR-003
Title:        Validation Rule Registry
Priority:     HIGH
Trigger:      System startup, rule introspection, monitoring
```

### Description

Maintain a registry of all validation rules with metadata enabling
discovery, configuration, documentation, and monitoring.

### Requirements

```text
The Rule Registry must:
  ✓ Catalog all active validation rules with metadata
  ✓ Group rules by data type (ohlcv, income_statement, etc.)
  ✓ Group rules by category (schema, quality, anomaly, cross_record)
  ✓ Allow enabling/disabling rules via configuration
  ✓ Provide rule introspection for monitoring dashboards
  ✓ Support adding new rules without modifying existing code
  ✓ Document each rule's purpose, severity, and thresholds
```

---

## FR-004: Generate Validation Report

```text
ID:           FR-004
Title:        Generate Validation Quality Report
Priority:     MEDIUM
Trigger:      After batch ingestion completion, or on-demand
```

### Description

Produce a structured report summarizing validation outcomes across
an ingestion run. Used for monitoring data quality trends and
detecting provider degradation.

### Output

```python
class ValidationReport(BaseModel):
    """Aggregate validation report for an ingestion run."""

    report_id: str
    generated_at: datetime
    ingestion_run_id: str

    # Scope
    data_type: str                              # "ohlcv", "income_statement", etc.
    ticker_count: int
    date_range_start: date | None = None
    date_range_end: date | None = None

    # Aggregate Counts
    total_data_points: int
    accepted_count: int
    flagged_count: int
    rejected_count: int

    acceptance_rate_pct: float
    rejection_rate_pct: float
    flag_rate_pct: float

    # Rule Breakdown
    issues_by_rule: list[RuleIssueSummary] = Field(default_factory=list)

    # Top Offenders
    most_rejected_tickers: list[TickerQualitySummary] = Field(default_factory=list)
    most_flagged_tickers: list[TickerQualitySummary] = Field(default_factory=list)

    # Trend
    quality_trend: str = "stable"               # "improving" | "stable" | "degrading"
    notes: list[str] = Field(default_factory=list)


class RuleIssueSummary(BaseModel):
    """Summary of issues for a single rule."""

    rule_id: str
    rule_name: str
    severity: str
    issue_count: int
    affected_tickers: int
    example_message: str = ""


class TickerQualitySummary(BaseModel):
    """Quality summary for a single ticker."""

    ticker: str
    rejected_count: int
    flagged_count: int
    top_issues: list[str] = Field(default_factory=list)
```

---

# 4. VALIDATION RULES CATALOG

## 4.1 OHLCV Validation Rules

### Category: Schema Validation

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-001  │ REJECT  │ Ticker is empty or does not match          │
│                    │         │ expected ticker for this ingestion batch.  │
│                    │         │ Check: bar.ticker == expected_ticker       │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-002  │ REJECT  │ Date is in the future.                    │
│                    │         │ Check: bar.date <= today                  │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-003  │ REJECT  │ Date is unreasonably far in the past.     │
│                    │         │ Check: bar.date >= 1970-01-01             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-004  │ REJECT  │ Any required field is null/missing.       │
│                    │         │ Check: all required fields non-null       │
│                    │         │ (Pydantic enforces this at model level)   │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Quality Rules (Price Consistency)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-001  │ REJECT  │ High < Low.                               │
│                    │         │ Check: high_cents >= low_cents             │
│                    │         │ This is physically impossible.             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-002  │ REJECT  │ Open outside High/Low range.              │
│                    │         │ Check: low_cents <= open_cents <= high_cents│
│                    │         │ Open must be between Low and High.        │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-003  │ REJECT  │ Close outside High/Low range.             │
│                    │         │ Check: low_cents <= close_cents <= high_cents│
│                    │         │ Close must be between Low and High.       │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-004  │ REJECT  │ Any price is negative.                    │
│                    │         │ Check: all *_cents >= 0                   │
│                    │         │ (Pydantic ge=0 enforces this)             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-005  │ REJECT  │ All four prices are zero.                 │
│                    │         │ Check: NOT (open==0 AND high==0 AND       │
│                    │         │ low==0 AND close==0)                      │
│                    │         │ A bar with all zeros is corrupt data.     │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-006  │ FLAG    │ Price is suspiciously low.                │
│                    │         │ Check: close_cents >= MIN_REASONABLE_PRICE │
│                    │         │ Threshold: $0.01 (1 cent)                │
│                    │         │ Could be a reverse split not yet adjusted.│
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-007  │ FLAG    │ Price is suspiciously high.               │
│                    │         │ Check: close_cents <= MAX_REASONABLE_PRICE │
│                    │         │ Threshold: $100,000 (10,000,000 cents)   │
│                    │         │ Could be a very high-priced stock (BRK.A).│
│                    │         │ FLAG, don't reject — some stocks are this │
│                    │         │ expensive.                                 │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-008  │ FLAG    │ High equals Low (flat bar).               │
│                    │         │ Check: high_cents == low_cents            │
│                    │         │ Unusual but possible (halt days, low      │
│                    │         │ liquidity). Flag for awareness.           │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Quality Rules (Volume)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-VOL-001  │ REJECT  │ Volume is negative.                       │
│                    │         │ Check: volume >= 0                        │
│                    │         │ (Pydantic ge=0 enforces this)             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-VOL-002  │ FLAG    │ Volume is zero on a trading day.          │
│                    │         │ Check: volume > 0 on trading days         │
│                    │         │ Could indicate: trading halt, data gap,   │
│                    │         │ or provider returning null volume.        │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-VOL-003  │ INFO    │ Volume spike.                             │
│                    │         │ Check: volume > avg_volume × SPIKE_MULT   │
│                    │         │ Threshold: 50x average                    │
│                    │         │ Informational — may indicate news event,  │
│                    │         │ earnings, or index rebalance.             │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Quality Rules (Calendar)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-CAL-001  │ REJECT  │ Bar has a weekend date.                   │
│                    │         │ Check: date.weekday() < 5                 │
│                    │         │ US equity markets are closed on weekends. │
│                    │         │ A bar with Saturday/Sunday date is         │
│                    │         │ definitely wrong data.                     │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-CAL-002  │ FLAG    │ Bar has a known NYSE holiday date.        │
│                    │         │ Check: date NOT in NYSE_HOLIDAYS          │
│                    │         │ FLAG rather than REJECT because our       │
│                    │         │ holiday list may be incomplete, and some  │
│                    │         │ providers include partial-day data.       │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Anomaly Detection (Context-Dependent)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-001  │ FLAG    │ Extreme daily price change.               │
│                    │         │ Check: |close - prior_close| / prior_close│
│                    │         │   > MAX_DAILY_CHANGE_PCT                  │
│                    │         │ Threshold: 50%                            │
│                    │         │ Requires: prior_bar provided.             │
│                    │         │ FLAG not REJECT: extreme moves do happen  │
│                    │         │ (earnings, M&A, circuit breakers).        │
│                    │         │ But they deserve investigation.           │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-002  │ FLAG    │ Extreme intraday range.                   │
│                    │         │ Check: (high - low) / low > 0.50          │
│                    │         │ Threshold: 50% intraday range             │
│                    │         │ Requires: none (single-bar check).        │
│                    │         │ FLAG: wide intraday swings are unusual    │
│                    │         │ for most stocks.                          │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-003  │ INFO    │ Volume significantly below average.       │
│                    │         │ Check: volume < avg_volume × 0.01         │
│                    │         │ Threshold: 1% of average volume           │
│                    │         │ Requires: historical_avg_volume provided. │
│                    │         │ INFO: Low volume may affect indicator     │
│                    │         │ reliability.                              │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-004  │ FLAG    │ Price gap from prior close.               │
│                    │         │ Check: |open - prior_close| / prior_close │
│                    │         │   > GAP_THRESHOLD                        │
│                    │         │ Threshold: 20%                            │
│                    │         │ Requires: prior_bar provided.             │
│                    │         │ FLAG: gaps are real but unusual. May      │
│                    │         │ indicate overnight news or data error.    │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Cross-Record Validation

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-001  │ FLAG    │ Non-sequential dates in batch.            │
│                    │         │ Check: each bar's date > prior bar's date │
│                    │         │ FLAG: could indicate missing data or      │
│                    │         │ duplicate dates (after dedup).            │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-002  │ REJECT  │ Duplicate date within same batch.         │
│                    │         │ Check: no two bars have same date         │
│                    │         │ REJECT the duplicate (keep the first one).│
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-003  │ FLAG    │ Large gap between consecutive bars.       │
│                    │         │ Check: calendar days between bars > 5     │
│                    │         │ AND gap is not explained by weekends/     │
│                    │         │ holidays alone.                           │
│                    │         │ Threshold: > 5 calendar days unexplained  │
│                    │         │ FLAG: may indicate trading halt or data   │
│                    │         │ gap from provider.                        │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-004  │ FLAG    │ Price moved but volume is zero.           │
│                    │         │ Check: close != prior_close AND volume==0 │
│                    │         │ FLAG: price change with zero volume is    │
│                    │         │ suspicious (may be adjusted close without │
│                    │         │ volume data).                             │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

## 4.2 Financial Statement Validation Rules (Phase 2)

### Category: Balance Sheet Identity

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-BS-001     │ FLAG    │ Balance sheet does not balance.            │
│                    │         │ Check: |assets - (liabilities + equity)|  │
│                    │         │   <= TOLERANCE_CENTS                      │
│                    │         │ Threshold: 100 cents ($1.00)              │
│                    │         │ FLAG not REJECT: rounding differences     │
│                    │         │ are common between provider's stated      │
│                    │         │ values. But large discrepancies indicate  │
│                    │         │ data quality problems.                    │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-BS-002     │ REJECT  │ Balance sheet imbalance exceeds 1%.       │
│                    │         │ Check: |assets - (liabilities + equity)|  │
│                    │         │   / assets > 0.01                        │
│                    │         │ REJECT: a > 1% imbalance is not rounding —│
│                    │         │ it is corrupt data.                       │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-BS-003     │ FLAG    │ Negative shareholders equity.             │
│                    │         │ Check: shareholders_equity_cents < 0      │
│                    │         │ FLAG: technically possible (accumulated   │
│                    │         │ deficit exceeds paid-in capital) but      │
│                    │         │ unusual and warrants attention.           │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Income Statement Consistency

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-001     │ FLAG    │ Gross profit ≠ revenue - COGS.            │
│                    │         │ Check: |gross_profit -                    │
│                    │         │   (revenue - cost_of_revenue)| <= 100    │
│                    │         │ Threshold: 100 cents ($1.00)              │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-002     │ FLAG    │ Non-positive revenue.                     │
│                    │         │ Check: revenue_cents > 0                  │
│                    │         │ FLAG: unusual for operating companies     │
│                    │         │ in our universe, but possible for         │
│                    │         │ pre-revenue or turnaround companies.      │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-003     │ FLAG    │ Gross margin outside -100% to +100%.      │
│                    │         │ Check: -1.0 <= gross_margin <= 1.0        │
│                    │         │ FLAG: technically possible but warrants   │
│                    │         │ investigation.                            │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-004     │ FLAG    │ Year-over-year revenue change > 200%.     │
│                    │         │ Check: |(rev_current - rev_prior) /       │
│                    │         │   rev_prior| > 2.0                       │
│                    │         │ Requires: prior period data.              │
│                    │         │ FLAG: may indicate M&A, spin-off, or     │
│                    │         │ data error.                               │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Cash Flow Statement Consistency

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-CF-001     │ FLAG    │ Cash flow components don't reconcile.     │
│                    │         │ Check: |OCF + ICF + FCF - net_change|    │
│                    │         │   <= TOLERANCE_CENTS                      │
│                    │         │ Threshold: 100 cents ($1.00)              │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-CF-002     │ FLAG    │ Free cash flow ≠ operating - capex.       │
│                    │         │ Check: |FCF - (OCF - capex)| <= 100      │
│                    │         │ FLAG: different definitions of FCF exist. │
│                    │         │ Provider may use a different formula.      │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

## 4.3 Rule Summary Matrix

```text
PHASE 1 RULES (OHLCV):
───────────────────────────────────────────────────
Total: 19 rules
  REJECT:  8 (hard failures — data is invalid)
  FLAG:   10 (suspicious — store with warning)
  INFO:    1 (noteworthy — informational only)

Schema:    4 rules
Quality:   7 rules (price: 5, volume: 2)
Calendar:  2 rules
Anomaly:   4 rules
X-Record:  4 rules (NEW in this spec, not in data-pipeline-standards)

PHASE 2 RULES (Financial Statements):
───────────────────────────────────────────────────
Total: 9 rules
  REJECT:  1
  FLAG:    8
  INFO:    0
```

---

# 5. VALIDATION PIPELINE ARCHITECTURE

## 5.1 Pipeline Implementation

```python
# src/data_engine/validation/pipeline.py

"""Validation pipeline — orchestrates all validation checks.

The pipeline is the single entry point for data validation.
It loads applicable rules, runs them against each data point,
and produces structured results.
"""

import structlog
import time
from src.data_engine.validation.models import (
    ValidationOutcome,
    ValidationOutcomeType,
    ValidationBatchResult,
    QualityIssue,
    IssueSeverity,
)
from src.data_engine.validation.registry import RuleRegistry
from src.data_engine.validation.interfaces import ValidationRule
from src.data_engine.models import OHLCVBar


logger = structlog.get_logger(__name__)


class ValidationPipeline:
    """Orchestrates data validation across all registered rules.

    The pipeline:
    1. Loads applicable rules for the data type
    2. Runs each rule against each data point
    3. Collects all issues
    4. Determines the outcome (ACCEPT/FLAG/REJECT)
    5. Aggregates results for the batch

    Thread-safe and stateless — safe to call concurrently.

    Dependencies:
        - rule_registry: RuleRegistry (provides active rules)
        - config: ValidationConfig (thresholds)
    """

    def __init__(
        self,
        rule_registry: RuleRegistry,
        config: "ValidationConfig",
    ) -> None:
        self._registry = rule_registry
        self._config = config
        self._logger = logger.bind(component="ValidationPipeline")

    def validate_ohlcv_batch(
        self,
        bars: list[OHLCVBar],
        ticker: str,
        prior_bar: OHLCVBar | None = None,
        historical_avg_volume: int | None = None,
    ) -> ValidationBatchResult:
        """Validate a batch of OHLCV bars.

        Implements FR-001.

        Args:
            bars: Bars to validate, in chronological order.
            ticker: Expected ticker symbol.
            prior_bar: Most recent stored bar for context.
            historical_avg_volume: Average volume for spike detection.

        Returns:
            ValidationBatchResult with per-bar outcomes.
        """
        start_time = time.monotonic()

        if not bars:
            return ValidationBatchResult(total_count=0)

        # Load applicable rules
        rules = self._registry.get_rules_for_data_type("ohlcv")

        # Build context
        context = ValidationContext(
            ticker=ticker,
            prior_bar=prior_bar,
            historical_avg_volume=historical_avg_volume,
            trading_calendar=self._config.trading_calendar,
            thresholds=self._config.ohlcv_thresholds,
        )

        # Validate each bar
        outcomes: list[ValidationOutcome] = []
        accepted_indices: list[int] = []
        rejected_indices: list[int] = []

        seen_dates: set = set()

        for i, bar in enumerate(bars):
            # Cross-record: duplicate date detection
            if bar.date in seen_dates:
                outcome = ValidationOutcome(
                    outcome=ValidationOutcomeType.REJECT,
                    issues=[QualityIssue(
                        rule_id="DQ-OHLCV-XRC-002",
                        rule_name="Duplicate Date Detection",
                        severity=IssueSeverity.REJECT,
                        category="cross_record",
                        field="date",
                        message=f"Duplicate date {bar.date} in batch",
                        actual_value=str(bar.date),
                    )],
                )
                outcomes.append(outcome)
                rejected_indices.append(i)
                continue

            seen_dates.add(bar.date)

            # Run all rules
            issues = self._run_rules(rules, bar, context)
            outcome = self._determine_outcome(issues)
            outcomes.append(outcome)

            if outcome.is_accepted:
                accepted_indices.append(i)
            else:
                rejected_indices.append(i)

            # Update context for next bar
            context.prior_bar = bar

        # Aggregate
        result = self._aggregate_results(
            outcomes, accepted_indices, rejected_indices
        )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        self._logger.info(
            "OHLCV batch validation completed",
            ticker=ticker,
            total=result.total_count,
            accepted=result.accepted_count,
            flagged=result.flagged_count,
            rejected=result.rejected_count,
            elapsed_ms=elapsed_ms,
        )

        if result.has_rejections:
            self._logger.warning(
                "Bars rejected during validation",
                ticker=ticker,
                rejected_count=result.rejected_count,
                rejection_rules=list(result.issues_by_rule.keys()),
            )

        return result

    def _run_rules(
        self,
        rules: list[ValidationRule],
        bar: OHLCVBar,
        context: "ValidationContext",
    ) -> list[QualityIssue]:
        """Run all validation rules against a single bar.

        Rules are independent — one rule's failure does not
        prevent other rules from running.

        If a rule raises an unexpected exception, it is logged
        and skipped (other rules still run).
        """
        all_issues: list[QualityIssue] = []

        for rule in rules:
            if not rule.is_enabled:
                continue

            try:
                issues = rule.check(bar, context)
                all_issues.extend(issues)
            except Exception as exc:
                self._logger.error(
                    "Validation rule threw unexpected exception",
                    rule_id=rule.rule_id,
                    ticker=bar.ticker,
                    date=str(bar.date),
                    error=str(exc),
                    exc_info=True,
                )
                # Skip this rule, continue with others

        return all_issues

    @staticmethod
    def _determine_outcome(
        issues: list[QualityIssue],
    ) -> ValidationOutcome:
        """Determine the final outcome from a list of issues.

        Logic:
        - Any REJECT issue → REJECT
        - Any FLAG issue (no REJECT) → FLAG
        - Only INFO issues or no issues → ACCEPT
        """
        if any(i.severity == IssueSeverity.REJECT for i in issues):
            return ValidationOutcome(
                outcome=ValidationOutcomeType.REJECT,
                issues=issues,
            )
        elif any(i.severity == IssueSeverity.FLAG for i in issues):
            return ValidationOutcome(
                outcome=ValidationOutcomeType.FLAG,
                issues=issues,
            )
        else:
            return ValidationOutcome(
                outcome=ValidationOutcomeType.ACCEPT,
                issues=issues,
            )

    def _aggregate_results(
        self,
        outcomes: list[ValidationOutcome],
        accepted_indices: list[int],
        rejected_indices: list[int],
    ) -> ValidationBatchResult:
        """Aggregate per-bar outcomes into a batch result."""
        accepted = sum(
            1 for o in outcomes
            if o.outcome == ValidationOutcomeType.ACCEPT
        )
        flagged = sum(
            1 for o in outcomes
            if o.outcome == ValidationOutcomeType.FLAG
        )
        rejected = sum(
            1 for o in outcomes
            if o.outcome == ValidationOutcomeType.REJECT
        )

        issues_by_rule: dict[str, int] = {}
        issues_by_severity: dict[str, int] = {}
        for outcome in outcomes:
            for issue in outcome.issues:
                issues_by_rule[issue.rule_id] = (
                    issues_by_rule.get(issue.rule_id, 0) + 1
                )
                issues_by_severity[issue.severity.value] = (
                    issues_by_severity.get(issue.severity.value, 0) + 1
                )

        return ValidationBatchResult(
            total_count=len(outcomes),
            accepted_count=accepted,
            flagged_count=flagged,
            rejected_count=rejected,
            issues_by_rule=issues_by_rule,
            issues_by_severity=issues_by_severity,
            outcomes=outcomes,
            accepted_indices=accepted_indices,
            rejected_indices=rejected_indices,
        )
```

## 5.2 Validation Context

```python
# src/data_engine/validation/context.py

"""Validation context — shared state across rule checks for a single bar.

The context provides rules with additional information needed for
context-dependent checks (e.g., prior bar for daily change calculation,
average volume for spike detection).
"""

from dataclasses import dataclass, field
from src.data_engine.models import OHLCVBar
from src.data_engine.calendar.trading_calendar import TradingCalendar


@dataclass
class OHLCVValidationThresholds:
    """Configurable thresholds for OHLCV validation rules.

    All thresholds have defaults from L0/L4 standards but can
    be overridden via configuration.
    """

    # Price range
    min_reasonable_price_cents: int = 1                     # $0.01
    max_reasonable_price_cents: int = 10_000_000            # $100,000

    # Daily change
    max_daily_price_change_pct: float = 0.50                # 50%

    # Intraday range
    max_intraday_range_pct: float = 0.50                    # 50%

    # Volume
    volume_spike_multiplier: float = 50.0                   # 50x average
    low_volume_threshold_pct: float = 0.01                  # 1% of average

    # Gaps
    gap_threshold_pct: float = 0.20                         # 20% gap from prior close
    max_unexplained_gap_days: int = 5                       # Calendar days

    # Date range
    min_valid_date_year: int = 1970
    max_future_days: int = 0                                # 0 = today is max


@dataclass
class FinancialStatementValidationThresholds:
    """Configurable thresholds for financial statement validation."""

    balance_sheet_tolerance_cents: int = 100                 # $1.00
    balance_sheet_reject_pct: float = 0.01                  # 1% imbalance → REJECT
    income_statement_tolerance_cents: int = 100
    cash_flow_tolerance_cents: int = 100
    max_yoy_revenue_change_pct: float = 2.0                 # 200%


@dataclass
class ValidationContext:
    """Context passed to validation rules for a single data point.

    Mutable: prior_bar is updated after each bar is validated,
    so the next bar receives the correct prior context.
    """

    ticker: str = ""
    prior_bar: OHLCVBar | None = None
    historical_avg_volume: int | None = None
    trading_calendar: TradingCalendar | None = None
    thresholds: OHLCVValidationThresholds = field(
        default_factory=OHLCVValidationThresholds
    )
```

---

# 6. VALIDATION RULE INTERFACE AND IMPLEMENTATION

## 6.1 Rule Interface

```python
# src/data_engine/validation/interfaces.py

"""Validation rule interface.

Every validation rule implements this protocol. This enables:
- Composability: rules are plugged into the pipeline independently
- Testability: each rule is tested in isolation
- Extensibility: new rules added without modifying existing code
"""

from typing import Protocol
from src.data_engine.validation.models import QualityIssue, ValidationRuleInfo
from src.data_engine.models import OHLCVBar
from src.data_engine.validation.context import ValidationContext


class ValidationRule(Protocol):
    """Protocol for a single validation rule.

    Every rule:
    - Has a unique rule_id
    - Has metadata (name, description, category, severity)
    - Receives a data point + context
    - Returns a list of QualityIssue (empty = passed)
    - Is pure: no side effects, no I/O, no state mutation
    - Handles its own edge cases (never raises)
    """

    @property
    def rule_id(self) -> str:
        """Unique rule identifier (e.g., 'DQ-OHLCV-PRC-001')."""
        ...

    @property
    def info(self) -> ValidationRuleInfo:
        """Rule metadata for registry and documentation."""
        ...

    @property
    def is_enabled(self) -> bool:
        """Whether this rule is currently active."""
        ...

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        """Run this validation check against a single bar.

        Args:
            bar: The OHLCV bar to validate.
            context: Validation context (prior bar, thresholds, etc.)

        Returns:
            List of quality issues found. Empty list = passed.
            A single rule can return multiple issues.
        """
        ...
```

## 6.2 Rule Implementations

```python
# src/data_engine/validation/rules/ohlcv_price_rules.py

"""OHLCV price consistency validation rules.

Each class implements one validation rule following the
ValidationRule protocol.
"""

from src.data_engine.validation.interfaces import ValidationRule
from src.data_engine.validation.models import (
    QualityIssue,
    IssueSeverity,
    ValidationRuleInfo,
)
from src.data_engine.validation.context import ValidationContext
from src.data_engine.models import OHLCVBar


class HighLowConsistencyRule:
    """DQ-OHLCV-PRC-001: High must be >= Low."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-PRC-001"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="High/Low Consistency",
            description="High price must be greater than or equal to Low price. "
                        "A bar where High < Low is physically impossible and "
                        "indicates corrupt data.",
            category="quality",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if bar.high_cents < bar.low_cents:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="High/Low Consistency",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="high_cents",
                message=(
                    f"High ({bar.high_cents}) is less than "
                    f"Low ({bar.low_cents})"
                ),
                actual_value=f"high={bar.high_cents}, low={bar.low_cents}",
                expected_range="high >= low",
            )]
        return []


class OpenInRangeRule:
    """DQ-OHLCV-PRC-002: Open must be between Low and High."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-PRC-002"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Open Within Range",
            description="Open price must be between Low and High.",
            category="quality",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []

        if bar.open_cents > bar.high_cents:
            issues.append(QualityIssue(
                rule_id=self.rule_id,
                rule_name="Open Within Range",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="open_cents",
                message=(
                    f"Open ({bar.open_cents}) exceeds "
                    f"High ({bar.high_cents})"
                ),
                actual_value=str(bar.open_cents),
                expected_range=f"<= {bar.high_cents}",
            ))

        if bar.open_cents < bar.low_cents:
            issues.append(QualityIssue(
                rule_id=self.rule_id,
                rule_name="Open Within Range",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="open_cents",
                message=(
                    f"Open ({bar.open_cents}) is below "
                    f"Low ({bar.low_cents})"
                ),
                actual_value=str(bar.open_cents),
                expected_range=f">= {bar.low_cents}",
            ))

        return issues


class AllPricesZeroRule:
    """DQ-OHLCV-PRC-005: All four prices zero indicates corrupt data."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-PRC-005"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="All Prices Zero",
            description="A bar where open, high, low, and close are all zero "
                        "is corrupt data, not a real trading period.",
            category="quality",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if (
            bar.open_cents == 0
            and bar.high_cents == 0
            and bar.low_cents == 0
            and bar.close_cents == 0
        ):
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="All Prices Zero",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="close_cents",
                message="All four prices (OHLC) are zero — corrupt data",
                actual_value="O=0, H=0, L=0, C=0",
                expected_range="> 0 for at least one price",
            )]
        return []


class ExtremeDailyChangeRule:
    """DQ-OHLCV-ANO-001: Flag extreme daily price changes."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-ANO-001"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Extreme Daily Price Change",
            description=(
                "Daily close-to-close change exceeds threshold. "
                "Flagged for review — extreme moves are rare but real. "
                "May indicate earnings, M&A, or data error."
            ),
            category="anomaly",
            severity=IssueSeverity.FLAG,
            data_types=["ohlcv"],
            is_configurable=True,
            config_keys=["max_daily_price_change_pct"],
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if context.prior_bar is None:
            return []  # Cannot check without prior bar

        if context.prior_bar.close_cents <= 0:
            return []  # Cannot compute change from zero

        daily_change = abs(
            (bar.close_cents - context.prior_bar.close_cents)
            / context.prior_bar.close_cents
        )
        threshold = context.thresholds.max_daily_price_change_pct

        if daily_change > threshold:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Extreme Daily Price Change",
                severity=IssueSeverity.FLAG,
                category="anomaly",
                field="close_cents",
                message=(
                    f"Daily price change of {daily_change:.1%} exceeds "
                    f"threshold of {threshold:.0%}. "
                    f"Prior close: {context.prior_bar.close_cents}, "
                    f"Current close: {bar.close_cents}"
                ),
                actual_value=f"{daily_change:.4f}",
                expected_range=f"<= {threshold}",
                context={
                    "prior_close_cents": context.prior_bar.close_cents,
                    "prior_date": str(context.prior_bar.date),
                },
            )]
        return []


class WeekendDateRule:
    """DQ-OHLCV-CAL-001: Reject bars with weekend dates."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-CAL-001"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Weekend Date Rejection",
            description=(
                "US equity markets are closed on Saturday and Sunday. "
                "A bar with a weekend date is incorrect data from the provider."
            ),
            category="calendar",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if bar.date.weekday() >= 5:
            day_name = bar.date.strftime("%A")
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Weekend Date Rejection",
                severity=IssueSeverity.REJECT,
                category="calendar",
                field="date",
                message=f"Bar has weekend date: {bar.date} ({day_name})",
                actual_value=f"{bar.date} ({day_name})",
                expected_range="Monday through Friday",
            )]
        return []


class ZeroVolumeRule:
    """DQ-OHLCV-VOL-002: Flag zero volume on trading days."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-VOL-002"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Zero Volume Warning",
            description=(
                "Zero volume on a trading day may indicate a trading halt, "
                "data gap, or provider returning null volume. "
                "Flagged for awareness — downstream indicators that depend on "
                "volume may be unreliable for this bar."
            ),
            category="quality",
            severity=IssueSeverity.FLAG,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if bar.volume == 0:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Zero Volume Warning",
                severity=IssueSeverity.FLAG,
                category="quality",
                field="volume",
                message=(
                    f"Zero volume on trading day {bar.date}. "
                    "May indicate halt, data gap, or provider issue."
                ),
                actual_value="0",
                expected_range="> 0",
            )]
        return []


class VolumeSpikeRule:
    """DQ-OHLCV-VOL-003: Note extreme volume spikes."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-VOL-003"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Volume Spike Detection",
            description=(
                "Volume exceeds historical average by a large multiple. "
                "Informational — may indicate earnings, news, index rebalance, "
                "or options expiration."
            ),
            category="anomaly",
            severity=IssueSeverity.INFO,
            data_types=["ohlcv"],
            is_configurable=True,
            config_keys=["volume_spike_multiplier"],
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if context.historical_avg_volume is None:
            return []  # Cannot check without average

        if context.historical_avg_volume <= 0:
            return []  # Cannot compute ratio

        volume_ratio = bar.volume / context.historical_avg_volume
        threshold = context.thresholds.volume_spike_multiplier

        if volume_ratio > threshold:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Volume Spike Detection",
                severity=IssueSeverity.INFO,
                category="anomaly",
                field="volume",
                message=(
                    f"Volume spike: {volume_ratio:.1f}x average. "
                    f"Volume: {bar.volume:,}, "
                    f"Avg: {context.historical_avg_volume:,}"
                ),
                actual_value=str(bar.volume),
                expected_range=f"<= {int(context.historical_avg_volume * threshold):,}",
            )]
        return []
```

## 6.3 Rule File Organization

```text
src/data_engine/validation/
├── __init__.py
├── pipeline.py                       # ValidationPipeline
├── interfaces.py                     # ValidationRule protocol
├── models.py                         # QualityIssue, ValidationOutcome, etc.
├── context.py                        # ValidationContext, Thresholds
├── registry.py                       # RuleRegistry
├── report_generator.py               # ValidationReport generation
│
└── rules/                            # Individual rule implementations
    ├── __init__.py
    ├── ohlcv_schema_rules.py         # DQ-OHLCV-SCH-*
    ├── ohlcv_price_rules.py          # DQ-OHLCV-PRC-*
    ├── ohlcv_volume_rules.py         # DQ-OHLCV-VOL-*
    ├── ohlcv_calendar_rules.py       # DQ-OHLCV-CAL-*
    ├── ohlcv_anomaly_rules.py        # DQ-OHLCV-ANO-*
    ├── ohlcv_cross_record_rules.py   # DQ-OHLCV-XRC-*
    ├── financial_balance_sheet.py    # DQ-FIN-BS-* (Phase 2)
    ├── financial_income_stmt.py      # DQ-FIN-IS-* (Phase 2)
    └── financial_cash_flow.py        # DQ-FIN-CF-* (Phase 2)
```

---

# 7. RULE REGISTRY

## 7.1 Registry Implementation

```python
# src/data_engine/validation/registry.py

"""Validation rule registry.

Central catalog of all validation rules. Provides:
- Discovery: which rules apply to which data types
- Configuration: enable/disable rules
- Introspection: rule metadata for dashboards
- Registration: new rules registered at startup
"""

import structlog
from src.data_engine.validation.interfaces import ValidationRule
from src.data_engine.validation.models import ValidationRuleInfo


logger = structlog.get_logger(__name__)


class RuleRegistry:
    """Central registry of all validation rules.

    Rules are registered at application startup.
    The registry is immutable after initialization.
    """

    def __init__(self) -> None:
        self._rules: dict[str, ValidationRule] = {}
        self._rules_by_data_type: dict[str, list[ValidationRule]] = {}
        self._logger = logger.bind(component="RuleRegistry")

    def register(self, rule: ValidationRule) -> None:
        """Register a validation rule.

        Args:
            rule: Rule instance to register.

        Raises:
            ValueError: If a rule with the same ID is already registered.
        """
        if rule.rule_id in self._rules:
            raise ValueError(
                f"Rule '{rule.rule_id}' is already registered"
            )

        self._rules[rule.rule_id] = rule

        for data_type in rule.info.data_types:
            if data_type not in self._rules_by_data_type:
                self._rules_by_data_type[data_type] = []
            self._rules_by_data_type[data_type].append(rule)

        self._logger.debug(
            "Rule registered",
            rule_id=rule.rule_id,
            data_types=rule.info.data_types,
            severity=rule.info.severity.value,
        )

    def get_rules_for_data_type(
        self,
        data_type: str,
    ) -> list[ValidationRule]:
        """Get all registered rules for a data type.

        Returns rules ordered: REJECT rules first, then FLAG, then INFO.
        This ordering allows short-circuit optimization if desired.
        """
        rules = self._rules_by_data_type.get(data_type, [])

        severity_order = {
            "REJECT": 0,
            "FLAG": 1,
            "INFO": 2,
        }

        return sorted(
            rules,
            key=lambda r: severity_order.get(r.info.severity.value, 3),
        )

    def get_rule(self, rule_id: str) -> ValidationRule | None:
        """Get a specific rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rule_info(self) -> list[ValidationRuleInfo]:
        """Get metadata for all registered rules."""
        return [rule.info for rule in self._rules.values()]

    def get_rule_count(self) -> dict[str, int]:
        """Count rules by data type."""
        return {
            data_type: len(rules)
            for data_type, rules in self._rules_by_data_type.items()
        }

    @property
    def total_rules(self) -> int:
        return len(self._rules)


def create_default_registry() -> RuleRegistry:
    """Create and populate the default rule registry.

    Called at application startup. Registers all Phase 1 rules.
    Phase 2+ rules are registered when those phases are activated.
    """
    from src.data_engine.validation.rules.ohlcv_price_rules import (
        HighLowConsistencyRule,
        OpenInRangeRule,
        CloseInRangeRule,
        AllPricesZeroRule,
        SuspiciouslyLowPriceRule,
        SuspiciouslyHighPriceRule,
        FlatBarRule,
    )
    from src.data_engine.validation.rules.ohlcv_volume_rules import (
        ZeroVolumeRule,
        VolumeSpikeRule,
    )
    from src.data_engine.validation.rules.ohlcv_calendar_rules import (
        WeekendDateRule,
        HolidayDateRule,
    )
    from src.data_engine.validation.rules.ohlcv_schema_rules import (
        TickerMismatchRule,
        FutureDateRule,
        AncientDateRule,
    )
    from src.data_engine.validation.rules.ohlcv_anomaly_rules import (
        ExtremeDailyChangeRule,
        ExtremeIntradayRangeRule,
        LowVolumeRule,
        PriceGapRule,
    )
    from src.data_engine.validation.rules.ohlcv_cross_record_rules import (
        NonSequentialDateRule,
        LargeGapBetweenBarsRule,
        PriceChangeWithZeroVolumeRule,
    )
    # Note: DQ-OHLCV-XRC-002 (duplicate date) is handled directly
    # in the pipeline loop, not as a pluggable rule, because it
    # requires batch-level state (seen_dates set).

    registry = RuleRegistry()

    # Schema rules
    registry.register(TickerMismatchRule())
    registry.register(FutureDateRule())
    registry.register(AncientDateRule())

    # Price consistency rules
    registry.register(HighLowConsistencyRule())
    registry.register(OpenInRangeRule())
    registry.register(CloseInRangeRule())
    registry.register(AllPricesZeroRule())
    registry.register(SuspiciouslyLowPriceRule())
    registry.register(SuspiciouslyHighPriceRule())
    registry.register(FlatBarRule())

    # Volume rules
    registry.register(ZeroVolumeRule())
    registry.register(VolumeSpikeRule())

    # Calendar rules
    registry.register(WeekendDateRule())
    registry.register(HolidayDateRule())

    # Anomaly rules
    registry.register(ExtremeDailyChangeRule())
    registry.register(ExtremeIntradayRangeRule())
    registry.register(LowVolumeRule())
    registry.register(PriceGapRule())

    # Cross-record rules
    registry.register(NonSequentialDateRule())
    registry.register(LargeGapBetweenBarsRule())
    registry.register(PriceChangeWithZeroVolumeRule())

    logger.info(
        "Validation rule registry initialized",
        total_rules=registry.total_rules,
        rules_by_type=registry.get_rule_count(),
    )

    return registry
```

---

# 8. CONFIGURATION

## 8.1 Module Configuration

```yaml
# Extracted from config/data_engine.yaml

data_engine:
  validation:
    # ── OHLCV Thresholds ──
    ohlcv:
      min_reasonable_price_cents: 1            # $0.01
      max_reasonable_price_cents: 10000000     # $100,000
      max_daily_price_change_pct: 0.50         # 50%
      max_intraday_range_pct: 0.50             # 50%
      volume_spike_multiplier: 50.0            # 50x average
      low_volume_threshold_pct: 0.01           # 1% of average
      gap_threshold_pct: 0.20                  # 20% open-to-prior-close
      max_unexplained_gap_days: 5

    # ── Financial Statement Thresholds (Phase 2) ──
    financial:
      balance_sheet_tolerance_cents: 100       # $1.00
      balance_sheet_reject_pct: 0.01           # 1%
      income_statement_tolerance_cents: 100
      cash_flow_tolerance_cents: 100
      max_yoy_revenue_change_pct: 2.0          # 200%

    # ── Rule Overrides ──
    disabled_rules: []                          # List of rule_ids to disable
    # Example: ["DQ-OHLCV-ANO-003"]            # Disable low volume info

    # ── Monitoring ──
    rejection_rate_alert_threshold: 0.05       # Alert if >5% rejected
```

---

# 9. TESTING REQUIREMENTS

## 9.1 Test Coverage Matrix

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    TEST COVERAGE REQUIREMENTS                           │
├────────────────────────────────────────┬─────────┬──────────────────────┤
│ Test Case                              │ Type    │ Priority             │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ PIPELINE TESTS                                                          │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ Empty batch → result with count 0      │ Unit    │ HIGH                 │
│ All bars valid → all ACCEPT            │ Unit    │ CRITICAL             │
│ Mixed valid/invalid → correct counts   │ Unit    │ CRITICAL             │
│ All bars invalid → all REJECT          │ Unit    │ HIGH                 │
│ FLAG bars included in accepted indices │ Unit    │ HIGH                 │
│ Rule exception → skip rule, continue   │ Unit    │ HIGH                 │
│ Issues aggregated by rule and severity │ Unit    │ MEDIUM               │
│ Prior bar updated between bars         │ Unit    │ HIGH                 │
│ Duplicate date → second bar rejected   │ Unit    │ HIGH                 │
│ Bars sorted chronologically before val.│ Unit    │ MEDIUM               │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ INDIVIDUAL RULE TESTS (per rule)                                        │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ DQ-OHLCV-PRC-001: high < low → REJECT │ Unit    │ CRITICAL             │
│ DQ-OHLCV-PRC-001: high == low → pass  │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-001: high > low → pass   │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-002: open > high → REJECT│ Unit    │ CRITICAL             │
│ DQ-OHLCV-PRC-002: open < low → REJECT │ Unit    │ CRITICAL             │
│ DQ-OHLCV-PRC-002: open in range → pass│ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-005: all zero → REJECT   │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-005: one non-zero → pass │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-006: penny price → FLAG  │ Unit    │ MEDIUM               │
│ DQ-OHLCV-PRC-008: flat bar → FLAG     │ Unit    │ MEDIUM               │
│ DQ-OHLCV-VOL-002: zero vol → FLAG     │ Unit    │ HIGH                 │
│ DQ-OHLCV-VOL-003: spike → INFO        │ Unit    │ MEDIUM               │
│ DQ-OHLCV-VOL-003: no avg vol → skip   │ Unit    │ MEDIUM               │
│ DQ-OHLCV-CAL-001: Saturday → REJECT   │ Unit    │ CRITICAL             │
│ DQ-OHLCV-CAL-001: Sunday → REJECT     │ Unit    │ CRITICAL             │
│ DQ-OHLCV-CAL-001: Monday → pass       │ Unit    │ HIGH                 │
│ DQ-OHLCV-CAL-002: holiday → FLAG      │ Unit    │ HIGH                 │
│ DQ-OHLCV-ANO-001: 60% move → FLAG     │ Unit    │ HIGH                 │
│ DQ-OHLCV-ANO-001: 10% move → pass     │ Unit    │ HIGH                 │
│ DQ-OHLCV-ANO-001: no prior → skip     │ Unit    │ MEDIUM               │
│ DQ-OHLCV-ANO-004: 25% gap → FLAG      │ Unit    │ MEDIUM               │
│ DQ-OHLCV-XRC-001: non-sequential → FL │ Unit    │ MEDIUM               │
│ DQ-OHLCV-XRC-003: >5 day gap → FLAG   │ Unit    │ MEDIUM               │
│ DQ-OHLCV-XRC-004: price+0vol → FLAG   │ Unit    │ MEDIUM               │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ REGISTRY TESTS                                                          │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ All Phase 1 rules registered           │ Unit    │ HIGH                 │
│ Duplicate rule ID → ValueError         │ Unit    │ HIGH                 │
│ Rules ordered: REJECT → FLAG → INFO    │ Unit    │ MEDIUM               │
│ Rules filterable by data type          │ Unit    │ MEDIUM               │
│ Rule metadata complete for all rules   │ Unit    │ LOW                  │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ OUTCOME DETERMINATION                                                   │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ No issues → ACCEPT                     │ Unit    │ CRITICAL             │
│ Only INFO → ACCEPT                     │ Unit    │ HIGH                 │
│ FLAG + INFO → FLAG                     │ Unit    │ HIGH                 │
│ REJECT + FLAG + INFO → REJECT          │ Unit    │ CRITICAL             │
│ Multiple REJECT → REJECT (all listed)  │ Unit    │ HIGH                 │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ INTEGRATION TESTS                                                       │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ Real AAPL bars pass validation         │ Integ.  │ HIGH                 │
│ Synthetically corrupted bars rejected  │ Integ.  │ HIGH                 │
│ Full pipeline: ingest → validate →     │ Integ.  │ HIGH                 │
│   store only accepted bars             │         │                      │
│ Recorded provider response validated   │ Integ.  │ MEDIUM               │
│   correctly                            │         │                      │
└────────────────────────────────────────┴─────────┴──────────────────────┘
```

## 9.2 Key Test Patterns

### Pattern: Testing a Single Rule

```python
@pytest.mark.unit
class TestHighLowConsistencyRule:
    """Tests for DQ-OHLCV-PRC-001: High must be >= Low."""

    @pytest.fixture
    def rule(self) -> HighLowConsistencyRule:
        return HighLowConsistencyRule()

    @pytest.fixture
    def default_context(self) -> ValidationContext:
        return ValidationContext(ticker="AAPL")

    def test_high_less_than_low_produces_reject(
        self, rule, default_context
    ):
        """High < Low is physically impossible → REJECT."""
        bar = make_ohlcv_bar(high_cents=14000, low_cents=15000)

        issues = rule.check(bar, default_context)

        assert len(issues) == 1
        assert issues[0].rule_id == "DQ-OHLCV-PRC-001"
        assert issues[0].severity == IssueSeverity.REJECT
        assert issues[0].field == "high_cents"
        assert "14000" in issues[0].actual_value
        assert "15000" in issues[0].actual_value

    def test_high_equals_low_passes(self, rule, default_context):
        """High == Low is valid (flat bar, possible during halt)."""
        bar = make_ohlcv_bar(
            open_cents=15000, high_cents=15000,
            low_cents=15000, close_cents=15000,
        )

        issues = rule.check(bar, default_context)

        assert len(issues) == 0

    def test_high_greater_than_low_passes(self, rule, default_context):
        """Normal bar with High > Low passes."""
        bar = make_ohlcv_bar(high_cents=15200, low_cents=14800)

        issues = rule.check(bar, default_context)

        assert len(issues) == 0

    def test_rule_metadata_correct(self, rule):
        """Rule metadata is complete and accurate."""
        info = rule.info
        assert info.rule_id == "DQ-OHLCV-PRC-001"
        assert info.severity == IssueSeverity.REJECT
        assert info.category == "quality"
        assert "ohlcv" in info.data_types
        assert rule.is_enabled is True
```

### Pattern: Testing the Pipeline

```python
@pytest.mark.unit
class TestValidationPipeline:
    """Tests for the ValidationPipeline orchestration."""

    @pytest.fixture
    def pipeline(self) -> ValidationPipeline:
        registry = create_default_registry()
        config = ValidationConfig(
            ohlcv_thresholds=OHLCVValidationThresholds(),
        )
        return ValidationPipeline(
            rule_registry=registry,
            config=config,
        )

    def test_valid_bars_all_accepted(self, pipeline):
        """All valid bars produce ACCEPT outcomes."""
        bars = make_ohlcv_series(ticker="AAPL", num_bars=5)

        result = pipeline.validate_ohlcv_batch(
            bars=bars,
            ticker="AAPL",
        )

        assert result.total_count == 5
        assert result.accepted_count == 5
        assert result.flagged_count == 0
        assert result.rejected_count == 0
        assert result.acceptance_rate == 1.0

    def test_corrupt_bar_rejected_others_accepted(self, pipeline):
        """One corrupt bar is rejected; valid bars pass."""
        valid_bars = make_ohlcv_series(ticker="AAPL", num_bars=3)
        corrupt_bar = make_ohlcv_bar(
            ticker="AAPL",
            bar_date=date(2025, 1, 18),  # Saturday!
        )
        all_bars = valid_bars + [corrupt_bar]

        result = pipeline.validate_ohlcv_batch(
            bars=all_bars,
            ticker="AAPL",
        )

        assert result.accepted_count == 3
        assert result.rejected_count == 1
        assert "DQ-OHLCV-CAL-001" in result.issues_by_rule

    def test_extreme_move_flagged_not_rejected(self, pipeline):
        """A 60% daily move is flagged but not rejected."""
        prior = make_ohlcv_bar(
            ticker="AAPL", bar_date=date(2025, 1, 14),
            close_cents=10000,
        )
        current = make_ohlcv_bar(
            ticker="AAPL", bar_date=date(2025, 1, 15),
            open_cents=16000, high_cents=16500,
            low_cents=15800, close_cents=16200,
        )

        result = pipeline.validate_ohlcv_batch(
            bars=[current],
            ticker="AAPL",
            prior_bar=prior,
        )

        assert result.accepted_count == 1  # Flagged but accepted
        assert result.flagged_count == 1
        assert result.rejected_count == 0
        assert "DQ-OHLCV-ANO-001" in result.issues_by_rule

    def test_rule_exception_does_not_crash_pipeline(self, pipeline):
        """If a rule throws, pipeline skips it and continues."""
        # This test uses a mock registry with a broken rule
        class BrokenRule:
            rule_id = "DQ-BROKEN"
            info = ValidationRuleInfo(
                rule_id="DQ-BROKEN",
                rule_name="Broken",
                description="",
                category="quality",
                severity=IssueSeverity.REJECT,
                data_types=["ohlcv"],
            )
            is_enabled = True
            def check(self, bar, context):
                raise RuntimeError("Rule crashed!")

        registry = RuleRegistry()
        registry.register(BrokenRule())
        config = ValidationConfig(
            ohlcv_thresholds=OHLCVValidationThresholds(),
        )
        pipeline_with_broken = ValidationPipeline(registry, config)

        bars = [make_ohlcv_bar(ticker="AAPL")]

        # Should not raise
        result = pipeline_with_broken.validate_ohlcv_batch(
            bars=bars, ticker="AAPL"
        )

        # Broken rule is skipped, bar still evaluated by other rules
        assert result.total_count == 1
```

---

# 10. PERFORMANCE REQUIREMENTS

| Operation                              | Target        | Notes                           |
|----------------------------------------|---------------|---------------------------------|
| Validate single OHLCV bar (all rules)  | < 1ms         | Pure computation, no I/O        |
| Validate batch of 252 bars (1 year)    | < 50ms        | All rules, all bars             |
| Validate batch of 5000 bars (backfill) | < 500ms       | All rules, all bars             |
| Rule registry lookup                   | < 0.1ms       | Dictionary access               |
| Outcome determination                  | < 0.01ms      | Simple severity scan            |

---

# 11. ACCEPTANCE CRITERIA

```text
ACCEPTANCE CRITERIA — DATA VALIDATION MODULE
═════════════════════════════════════════════

FUNCTIONAL — PIPELINE:
□ AC-01: Empty batch returns result with count 0 (no error)
□ AC-02: Valid bars produce ACCEPT outcomes with no issues
□ AC-03: Mixed valid/invalid bars produce correct per-bar outcomes
□ AC-04: Worst severity determines outcome (REJECT > FLAG > INFO)
□ AC-05: Flagged bars are included in accepted_indices
□ AC-06: Rejected bars are excluded from accepted_indices
□ AC-07: Rule exceptions do not crash the pipeline
□ AC-08: Issues aggregated correctly by rule_id and severity
□ AC-09: Duplicate dates within batch detected and second rejected
□ AC-10: Prior bar context updated between bars in batch

FUNCTIONAL — RULES:
□ AC-11: High < Low → REJECT (DQ-OHLCV-PRC-001)
□ AC-12: Open outside High/Low → REJECT (DQ-OHLCV-PRC-002)
□ AC-13: Close outside High/Low → REJECT (DQ-OHLCV-PRC-003)
□ AC-14: All prices zero → REJECT (DQ-OHLCV-PRC-005)
□ AC-15: Weekend date → REJECT (DQ-OHLCV-CAL-001)
□ AC-16: Zero volume → FLAG (DQ-OHLCV-VOL-002)
□ AC-17: Extreme daily move (>50%) → FLAG (DQ-OHLCV-ANO-001)
□ AC-18: Volume spike (>50x) → INFO (DQ-OHLCV-VOL-003)
□ AC-19: All 19 Phase 1 rules registered in default registry
□ AC-20: Each rule tested with pass case, fail case, and edge case

FUNCTIONAL — REGISTRY:
□ AC-21: All rules discoverable by data type
□ AC-22: Rules returned in severity order (REJECT first)
□ AC-23: Duplicate rule_id raises ValueError
□ AC-24: Rule metadata complete (id, name, description, severity)

NON-FUNCTIONAL:
□ AC-25: Validation of 252 bars completes in < 50ms
□ AC-26: Validation is stateless — no side effects, no I/O
□ AC-27: Validation never modifies input data
□ AC-28: All thresholds configurable via config file

TESTING:
□ AC-29: Unit test coverage > 95% for this module
□ AC-30: Every rule has at least 3 test cases (pass, fail, edge)
□ AC-31: Pipeline tested with real recorded provider data
```

---

# 12. CROSS-REFERENCES

| Document                                    | Location                                              |
|---------------------------------------------|-------------------------------------------------------|
| L0: System Vision                           | `specs/L0-system-vision.md`                           |
| L0: Data Quality Rules                      | `specs/L0-system-vision.md` Section 6.4               |
| L1: Data Engine Domain                      | `specs/L1-domains/data-engine.md`                     |
| L1: Data Engine Business Rules              | `specs/L1-domains/data-engine.md` Section 6.2         |
| L2: Market Data Ingestion                   | `specs/L2-modules/data-engine/market-data-ingestion.md` |
| L4: Coding Standards                        | `specs/L4-conventions/coding-standards.md`             |
| L4: Data Pipeline Standards                 | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Data Pipeline Standards — Validation    | `specs/L4-conventions/data-pipeline-standards.md` §6  |
| L4: Financial Calculation Standards — Verify| `specs/L4-conventions/financial-calculation-standards.md` §12 |
| L4: Testing Standards                       | `specs/L4-conventions/testing-standards.md`            |
| Guardrails: Data Quality (to be written)    | `specs/guardrails/data-quality-guardrails.md`         |

---
```
