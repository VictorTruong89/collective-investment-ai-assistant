## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines how all AI agents in the investment pipeline are
designed, built, tested, and operated. An "agent" in this system is a
software component that uses a Large Language Model (LLM) to perform
analytical tasks that require judgment, synthesis, or natural language
understanding — tasks that cannot be solved with deterministic code alone.

AI agents are the most powerful and most dangerous components in the system.
Powerful because they can synthesize information and generate insights at
a speed no human can match. Dangerous because they can hallucinate,
produce plausible-sounding nonsense, and generate false confidence in
wrong conclusions. Every standard in this document exists to **maximize
the power and minimize the danger**.

**Every developer and every AI coding agent** building agent components
must follow these standards. No agent may be deployed to production
without conforming to every applicable section.

## Scope

| In Scope                                        | Out of Scope                        |
|-------------------------------------------------|-------------------------------------|
| Agent architectural patterns                     | Specific agent behaviors (→ L5 specs)|
| Prompt engineering standards                     | LLM model selection and evaluation  |
| LLM gateway design                              | LLM fine-tuning methodology         |
| Agent I/O contracts and validation               | Embedding model selection            |
| Agent versioning and reproducibility             | Vector database schema design        |
| Output validation pipeline                       | RAG architecture details             |
| Confidence and citation standards                | Specific prompt content (→ L5 specs) |
| Multi-agent coordination patterns                |                                     |
| Token management and cost controls               |                                     |
| Agent observability and monitoring               |                                     |
| Graceful degradation and fallback patterns        |                                     |

## Governing Principles

Restated from L0-system-vision.md Section 5.2 for emphasis. **IDs are `AP-n`** — `P1`–`P7` are taken by the project constitution and mean different things.

| Principle | Summary |
|-----------|---------|
| AP-1: Transparency Over Confidence | Every output includes confidence, completeness, data gaps, and assumptions |
| AP-2: Cited Claims Only | Every factual assertion traceable to a data point |
| AP-3: Mandatory Adversarial Thinking | Every directional recommendation includes counter-argument |
| AP-4: Graceful Degradation | Missing data → partial report marked INCOMPLETE, never fabricated data |
| AP-5: Deterministic When Possible | Use code for math, LLMs for judgment and synthesis |
| AP-6: Versioned and Reproducible | Every output records agent version, prompt version, model, inputs |

---

# 1. AGENT ARCHITECTURE

## 1.1 The Fundamental Rule

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   AN AGENT IS NOT A PROMPT.                                     ║
║   AN AGENT IS A SOFTWARE COMPONENT THAT USES PROMPTS.           ║
║                                                                  ║
║   The LLM is a reasoning engine called by the agent.            ║
║   The agent owns: data gathering, validation, orchestration,    ║
║   output verification, error handling, and guardrail            ║
║   enforcement.                                                   ║
║                                                                  ║
║   The LLM owns: synthesis, interpretation, and narrative        ║
║   generation from structured data it receives.                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.2 Agent Component Architecture

Every agent in the system is composed of these components:

```text
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT BOUNDARY                           │
│                                                                  │
│  ┌────────────────┐                                             │
│  │  Input Handler │ ← Receives request, validates, enriches    │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Data Gatherer │ ← Fetches all data needed for analysis     │
│  │                │   from internal services (NOT external APIs) │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Pre-Processor │ ← Transforms raw data into LLM-ready       │
│  │                │   context (tables, summaries, structured)    │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐    ┌──────────────┐                        │
│  │  Prompt        │───→│  LLM Gateway │← The ONLY component    │
│  │  Assembler     │    │  (API call)  │  that calls the LLM    │
│  └────────────────┘    └──────┬───────┘                        │
│                               ▼                                  │
│  ┌────────────────┐                                             │
│  │  Output Parser │ ← Extracts structured data from LLM text   │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Validator     │ ← Schema validation, guardrail checks,     │
│  │                │   citation verification, anomaly detection   │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Post-Processor│ ← Enriches output with computed fields,     │
│  │                │   metadata, confidence scores                │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Output        │ ← Returns validated, typed agent output    │
│  └────────────────┘                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 1.3 Agent Base Class

All agents inherit from a common base that enforces the component pipeline:

```python
# src/shared/agents/base_agent.py

"""Base agent class for all AI agents in the system.

Every agent inherits from this base class, which enforces:
- Consistent lifecycle (gather → prepare → reason → validate → output)
- Mandatory guardrail checking
- Structured logging and observability
- Version tracking and reproducibility metadata
- Token usage tracking
"""

import structlog
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TypeVar, Generic

from pydantic import BaseModel
from src.shared.types import Result, Success, Failure
from src.shared.agents.models import (
    AgentExecutionMetadata,
    AgentError,
    GuardrailViolation,
)
from src.infrastructure.llm.gateway import LLMGateway


logger = structlog.get_logger(__name__)

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """Abstract base class for all AI agents.

    Subclasses implement the abstract methods for each stage of the
    agent pipeline. The base class orchestrates the flow and enforces
    guardrails.

    Type Parameters:
        TInput: The Pydantic model for agent input.
        TOutput: The Pydantic model for agent output.
    """

    def __init__(
        self,
        llm_gateway: LLMGateway,
        agent_name: str,
        agent_version: str,
        prompt_version: str,
        max_retries: int = 2,
    ) -> None:
        self._llm = llm_gateway
        self._agent_name = agent_name
        self._agent_version = agent_version
        self._prompt_version = prompt_version
        self._max_retries = max_retries
        self._logger = logger.bind(
            agent=agent_name,
            agent_version=agent_version,
        )

    async def execute(
        self,
        input_data: TInput,
        correlation_id: str = "",
    ) -> Result[TOutput, AgentError]:
        """Execute the full agent pipeline.

        This is the ONLY public method. It orchestrates all stages
        in order, enforces guardrails, and handles failures.

        Args:
            input_data: Validated input conforming to TInput schema.
            correlation_id: Trace ID for linking related operations.

        Returns:
            Success(TOutput) with validated agent output, or
            Failure(AgentError) with structured error details.
        """
        start_time = time.monotonic()
        log = self._logger.bind(
            correlation_id=correlation_id,
            operation="execute",
        )

        log.info("Agent execution started", input_summary=self._summarize_input(input_data))

        try:
            # ── Stage 1: Gather data ──
            log.debug("Gathering data")
            context = await self._gather_data(input_data)
            if context.is_failure:
                return self._handle_stage_failure("gather_data", context.error, log)

            # ── Stage 2: Pre-process into LLM context ──
            log.debug("Pre-processing context")
            prepared_context = self._prepare_context(context.value, input_data)

            # ── Stage 3: Assemble prompt ──
            prompt = self._assemble_prompt(prepared_context)

            # ── Stage 4: Call LLM (with retries) ──
            log.debug("Calling LLM")
            raw_output = await self._call_llm_with_retry(prompt, log)
            if raw_output.is_failure:
                return self._handle_stage_failure("llm_call", raw_output.error, log)

            # ── Stage 5: Parse output ──
            log.debug("Parsing output")
            parsed = self._parse_output(raw_output.value)
            if parsed.is_failure:
                return self._handle_stage_failure("parse_output", parsed.error, log)

            # ── Stage 6: Validate (schema + guardrails) ──
            log.debug("Validating output")
            validated = self._validate_output(parsed.value, input_data, context.value)
            if validated.is_failure:
                return self._handle_stage_failure("validation", validated.error, log)

            # ── Stage 7: Post-process (enrich with metadata) ──
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            output = self._post_process(
                validated.value,
                metadata=self._build_metadata(
                    input_data=input_data,
                    llm_response=raw_output.value,
                    elapsed_ms=elapsed_ms,
                    correlation_id=correlation_id,
                ),
            )

            log.info(
                "Agent execution completed",
                elapsed_ms=elapsed_ms,
                confidence=getattr(output, "confidence_score", None),
                tokens_used=raw_output.value.token_usage.total if hasattr(raw_output.value, "token_usage") else 0,
            )

            return Success(output)

        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            log.error(
                "Agent execution failed with unexpected error",
                error=str(exc),
                elapsed_ms=elapsed_ms,
                exc_info=True,
            )
            return Failure(AgentError(
                code=f"AGENT.{self._agent_name.upper()}.UNEXPECTED",
                message=f"Unexpected error: {exc}",
                stage="unknown",
            ))

    # ── Abstract methods (implement in each agent) ──

    @abstractmethod
    async def _gather_data(self, input_data: TInput) -> Result:
        """Fetch all data needed for analysis from internal services.

        This method calls other services (DataEngine, etc.) to
        assemble the raw data the agent needs. It does NOT call
        external APIs directly.

        Returns:
            Success with gathered data context, or
            Failure if critical data is unavailable.
        """
        ...

    @abstractmethod
    def _prepare_context(self, raw_data: dict, input_data: TInput) -> dict:
        """Transform raw data into LLM-ready context.

        This is where data is formatted into tables, summaries,
        and structured text that the LLM can reason about effectively.
        Keep context focused — include only what the LLM needs.

        Returns:
            Dictionary of prepared context sections.
        """
        ...

    @abstractmethod
    def _assemble_prompt(self, context: dict) -> list[dict]:
        """Assemble the complete prompt (system + user messages).

        Returns:
            List of message dicts: [{"role": "...", "content": "..."}]
        """
        ...

    @abstractmethod
    def _parse_output(self, llm_response: "LLMResponse") -> Result:
        """Parse the raw LLM text into structured data.

        Returns:
            Success with parsed data, or
            Failure if the output cannot be parsed.
        """
        ...

    @abstractmethod
    def _validate_output(self, parsed: dict, input_data: TInput, context: dict) -> Result:
        """Validate parsed output against schema and guardrails.

        Returns:
            Success with validated output, or
            Failure with specific validation errors.
        """
        ...

    @abstractmethod
    def _post_process(self, validated: TOutput, metadata: AgentExecutionMetadata) -> TOutput:
        """Enrich validated output with metadata and computed fields.

        Returns:
            Final output with all metadata attached.
        """
        ...

    # ── Provided methods (common infrastructure) ──

    async def _call_llm_with_retry(
        self,
        messages: list[dict],
        log: structlog.BoundLogger,
    ) -> Result:
        """Call LLM with retry logic. See Section 3 for details."""
        ...

    def _build_metadata(self, **kwargs) -> AgentExecutionMetadata:
        """Build standardized execution metadata. See Section 6."""
        ...

    def _handle_stage_failure(self, stage: str, error: any, log) -> Failure:
        """Log and wrap a stage failure. See Section 10."""
        ...

    def _summarize_input(self, input_data: TInput) -> dict:
        """Create a log-safe summary of input (no sensitive data)."""
        ...
```

## 1.4 Agent Component Rules

| Rule | Description |
|------|-------------|
| **AC-001** | Every agent inherits from `BaseAgent` — no standalone agent implementations |
| **AC-002** | The LLM is called in exactly ONE stage (`_call_llm_with_retry`). No other stage calls the LLM. |
| **AC-003** | Data gathering calls internal services only, never external APIs directly |
| **AC-004** | Pre-processing is deterministic — same raw data always produces same context |
| **AC-005** | Output validation is mandatory and cannot be skipped |
| **AC-006** | Post-processing adds metadata but never changes analytical content |
| **AC-007** | Each stage returns a `Result` type for explicit error handling |
| **AC-008** | The base class handles all logging, timing, and error wrapping |

---

# 2. PROMPT ENGINEERING STANDARDS

## 2.1 Prompt Architecture

Every agent uses a three-part prompt structure:

```text
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM PROMPT (Identity + Rules + Output Format)           │
│                                                              │
│  "You are a Senior Equity Research Analyst..."               │
│  - Role definition                                           │
│  - Analytical framework (step-by-step)                       │
│  - Guardrails and prohibitions                               │
│  - Output schema (JSON structure)                            │
│  - Citation requirements                                     │
│                                                              │
│  Changes: RARELY (tied to agent version)                     │
├─────────────────────────────────────────────────────────────┤
│  CONTEXT INJECTION (Data + Prior Knowledge)                  │
│                                                              │
│  "Here is the data for your analysis:"                       │
│  - Financial statements (formatted tables)                   │
│  - Price history summary                                     │
│  - Recent news (summarized)                                  │
│  - Existing thesis (if any)                                  │
│  - Peer comparison data                                      │
│                                                              │
│  Changes: EVERY CALL (dynamic data)                          │
├─────────────────────────────────────────────────────────────┤
│  TASK INSTRUCTION (Specific Request)                         │
│                                                              │
│  "Analyze {ticker} and produce a research report..."         │
│  - Specific task description                                 │
│  - Any special focus areas                                   │
│  - Time horizon                                              │
│  - Output reminder                                           │
│                                                              │
│  Changes: EVERY CALL (task-specific)                         │
└─────────────────────────────────────────────────────────────┘
```

## 2.2 System Prompt Standards

```python
# src/agents/research/prompts/system.py

"""System prompt for the Research Analyst Agent.

Version: 1.0.0
Last Updated: [DATE]
Changes: Initial version

This file contains ONLY the system prompt text. It is loaded by
the agent's _assemble_prompt() method. The prompt version is
tracked alongside the agent version for reproducibility.
"""

RESEARCH_ANALYST_SYSTEM_PROMPT = """
You are a Senior Equity Research Analyst working for an investment fund
focused on US equities. Your role is to analyze companies and produce
structured, data-driven research reports that support investment decisions.

## YOUR ANALYTICAL FRAMEWORK

Follow these steps in order for every analysis:

1. SITUATE: What does this company do? What sector? What is its competitive
   position? What stage of business lifecycle?

2. FINANCIALS: Analyze revenue trends, profit margins, cash flow generation,
   and balance sheet health over the available history. Identify improving
   or deteriorating trends.

3. VALUATION: Compare current valuation multiples (P/E, P/S, EV/EBITDA)
   against historical averages and peer group. Determine if the stock
   appears cheap, fairly valued, or expensive.

4. CATALYSTS: Identify specific upcoming events or trends that could drive
   the stock price higher within the analysis time horizon.

5. RISKS: Identify specific threats that could drive the stock price lower.
   Be thorough — risks are as important as catalysts.

6. SYNTHESIZE: Construct bull, base, and bear cases with estimated
   probability weights that sum to 100%.

7. RECOMMEND: Issue a recommendation with a confidence score based on
   your data completeness and analytical certainty.

8. CITE: Every factual claim must reference a specific data point from
   the provided context. If you cannot cite it, do not state it.

## YOUR RULES

- NEVER fabricate financial numbers. Use ONLY the data provided.
- NEVER claim certainty. Use probabilistic language.
- NEVER omit the bear case, even for your strongest convictions.
- NEVER provide a price target without showing methodology.
- ALWAYS disclose when data is limited or missing.
- ALWAYS note when a metric is an outlier relative to peers or history.
- If you lack sufficient data for a confident analysis, say so explicitly
  and reduce your confidence score accordingly.

## YOUR OUTPUT FORMAT

Respond with a JSON object matching this exact structure:
{output_schema}

Do not include any text outside the JSON object. Do not wrap in markdown
code blocks. Output raw JSON only.
"""
```

## 2.3 Context Injection Standards

```python
# src/agents/research/context_builder.py

"""Context builder for Research Analyst Agent.

Transforms raw data from internal services into LLM-ready text.
The goal is to present data in a format that is:
1. Easy for the LLM to parse and reference
2. Compact (minimizes token usage)
3. Labeled (every piece of data has a clear identifier for citation)
4. Honest (missing data is explicitly noted, not omitted)
"""

from datetime import date


class ResearchContextBuilder:
    """Builds structured context for the Research Analyst Agent.

    Each method produces a labeled section that the LLM can reference.
    The output is plain text with clear headers and table formatting.
    """

    def build_financial_context(
        self,
        income_statements: list[dict],
        balance_sheets: list[dict],
        cash_flow_statements: list[dict],
    ) -> str:
        """Format financial statements as text tables for LLM context.

        Example output:
        === INCOME STATEMENT (Annual, USD Millions) ===
        [DATA-FIN-IS]
        | Metric          | FY2024  | FY2023  | FY2022  | FY2021  |
        |-----------------|---------|---------|---------|---------|
        | Revenue         | 391,830 | 383,285 | 394,328 | 365,817 |
        | Gross Profit    | 180,683 | 169,148 | 170,782 | 152,836 |
        | Operating Inc.  | 118,960 | 114,301 | 119,437 | 108,949 |
        | Net Income      |  96,800 |  96,995 |  99,803 |  94,680 |
        ...

        [DATA-FIN-MARGINS]
        | Margin          | FY2024  | FY2023  | FY2022  | FY2021  |
        | Gross Margin    |  46.1%  |  44.1%  |  43.3%  |  41.8%  |
        ...

        Note: Data labeled [DATA-FIN-IS] can be cited by the agent as
        source "DATA-FIN-IS" in its citations.
        """
        ...

    def build_price_context(
        self,
        current_price_cents: int,
        price_history_summary: dict,
    ) -> str:
        """Format price and technical summary.

        Example output:
        === PRICE DATA ===
        [DATA-PRICE-CURRENT]
        Current Price: $185.92 (as of 2025-01-15 16:00 ET)
        52-Week High: $199.62 (2024-12-26)
        52-Week Low: $164.08 (2024-04-19)
        Distance from High: -6.9%
        Distance from Low: +13.3%

        [DATA-PRICE-PERFORMANCE]
        | Period  | Return  | vs SPY  |
        |---------|---------|---------|
        | 1 Month | +3.2%   | +1.1%   |
        | 3 Month | -2.1%   | -5.3%   |
        | 6 Month | +8.7%   | +2.4%   |
        | 1 Year  | +24.1%  | +6.8%   |
        """
        ...

    def build_missing_data_disclosure(
        self,
        available: list[str],
        requested: list[str],
    ) -> str:
        """Explicitly list what data is available and what is missing.

        This section ensures the LLM knows what it doesn't know.

        Example output:
        === DATA AVAILABILITY ===
        [DATA-AVAILABILITY]
        ✓ Available: Income Statement (4 years), Balance Sheet (4 years),
          Price History (1 year), Current Quote
        ✗ Missing: Cash Flow Statement, Analyst Estimates,
          Insider Transactions, News (last 30 days)

        Data Completeness: 6 of 10 requested data sets available (60%)
        """
        available_str = ", ".join(available) if available else "None"
        missing = [r for r in requested if r not in available]
        missing_str = ", ".join(missing) if missing else "None"
        completeness = len(available) / len(requested) if requested else 0

        return (
            "=== DATA AVAILABILITY ===\n"
            "[DATA-AVAILABILITY]\n"
            f"✓ Available: {available_str}\n"
            f"✗ Missing: {missing_str}\n"
            f"\nData Completeness: {len(available)} of {len(requested)} "
            f"requested data sets available ({completeness:.0%})\n"
        )
```

## 2.4 Context Injection Rules

| Rule | Description |
|------|-------------|
| **CI-001** | Every data block has a citation label (e.g., `[DATA-FIN-IS]`) that the LLM must reference |
| **CI-002** | Missing data is ALWAYS explicitly disclosed in the context, never silently omitted |
| **CI-003** | Numerical data is pre-formatted (tables, aligned columns) for LLM readability |
| **CI-004** | Context uses consistent units with labels (USD Millions, cents, percentages) |
| **CI-005** | Data freshness dates included: "as of [DATE]" on every data section |
| **CI-006** | Context sections ordered by importance (most critical data first) |
| **CI-007** | Total context size monitored and logged (token count). See Section 5 for limits. |
| **CI-008** | Raw data NEVER injected directly — always transformed by context builder |

## 2.5 Prompt File Management

```text
src/agents/
├── research/
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system.py          # System prompt text (versioned)
│   │   ├── task_templates.py  # Task instruction templates
│   │   └── output_schema.py   # JSON schema for output format
│   ├── context_builder.py     # Data → LLM context transformer
│   ├── output_parser.py       # LLM text → structured data
│   ├── validator.py           # Guardrail enforcement
│   ├── agent.py               # Main agent class (extends BaseAgent)
│   └── models.py              # Agent-specific Pydantic models
```

## 2.6 Prompt Engineering Rules

| Rule | Description |
|------|-------------|
| **PE-001** | System prompts stored in dedicated Python files, not inline strings |
| **PE-002** | Every system prompt file has a version number and changelog in its docstring |
| **PE-003** | System prompt changes require a new prompt version, logged alongside agent version |
| **PE-004** | Prompts NEVER contain real financial data — data is injected via context |
| **PE-005** | Output format specified as JSON schema in the system prompt, not free text |
| **PE-006** | Chain-of-thought reasoning is requested explicitly in the analytical framework |
| **PE-007** | Guardrails stated as explicit rules in the system prompt ("NEVER", "ALWAYS") |
| **PE-008** | Prompts tested with multiple LLM providers to avoid provider-specific assumptions |
| **PE-009** | No prompt relies on the LLM "knowing" current events — all data is injected |
| **PE-010** | Prompt templates use named placeholders (`{ticker}`, `{output_schema}`), never positional |

---

# 3. LLM GATEWAY

## 3.1 Gateway Architecture

All LLM communication flows through a single gateway. No agent, service,
or module calls an LLM provider API directly.

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Research    │    │  Quant       │    │  Risk        │
│  Agent       │    │  Agent       │    │  Agent       │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼───────┐
                    │  LLM Gateway │
                    │              │
                    │ • Rate limit │
                    │ • Retry      │
                    │ • Fallback   │
                    │ • Logging    │
                    │ • Token track│
                    │ • Sanitize   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Primary  │ │ Fallback │ │ Fallback │
        │ Provider │ │ Provider │ │ Provider │
        │ (e.g.,   │ │ (e.g.,   │ │ (e.g.,   │
        │ Claude)  │ │ GPT-4o)  │ │ Local)   │
        └──────────┘ └──────────┘ └──────────┘
```

## 3.2 Gateway Interface

```python
# src/infrastructure/llm/gateway.py

"""LLM Gateway — single point of access for all LLM calls.

All LLM interactions in the system go through this gateway.
It handles provider abstraction, retry logic, rate limiting,
input sanitization, token tracking, and structured logging.
"""

import structlog
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)


class LLMRequest(BaseModel):
    """Standardized LLM request."""

    messages: list[dict[str, str]]
    model: str = ""                       # Empty = use default
    temperature: float = 0.2             # Low for analytical tasks
    max_output_tokens: int = 4096
    response_format: str = "json"        # "json" or "text"
    timeout_seconds: int = 120

    # Metadata (not sent to provider)
    agent_name: str = ""
    agent_version: str = ""
    prompt_version: str = ""
    correlation_id: str = ""


class TokenUsage(BaseModel):
    """Token usage tracking."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_cents: int = 0         # Estimated cost in USD cents


class LLMResponse(BaseModel):
    """Standardized LLM response."""

    content: str                          # Raw response text
    model_used: str                       # Actual model that responded
    provider_used: str                    # Which provider handled it
    token_usage: TokenUsage
    latency_ms: int
    finish_reason: str                    # "stop", "length", "error"
    request_id: str                       # Provider's request ID
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class LLMGateway:
    """Central LLM access gateway.

    Features:
    - Provider abstraction (swap providers without agent changes)
    - Automatic retry with exponential backoff
    - Provider fallback chain
    - Input sanitization (remove potential credential leaks)
    - Token usage tracking and budgeting
    - Structured logging of all LLM interactions
    - Rate limiting per provider
    """

    def __init__(
        self,
        primary_provider: "LLMProvider",
        fallback_providers: list["LLMProvider"] | None = None,
        max_retries: int = 2,
        token_budget_daily: int | None = None,
    ) -> None:
        self._primary = primary_provider
        self._fallbacks = fallback_providers or []
        self._max_retries = max_retries
        self._token_budget_daily = token_budget_daily
        self._daily_tokens_used: int = 0
        self._logger = logger.bind(component="LLMGateway")

    async def complete(
        self,
        request: LLMRequest,
    ) -> Result[LLMResponse, AgentError]:
        """Send a completion request to the LLM.

        This is the ONLY method that external code calls to
        interact with an LLM.

        Flow:
        1. Sanitize input (remove potential secrets)
        2. Check token budget
        3. Try primary provider
        4. On failure, try fallback providers
        5. Log everything
        6. Track token usage

        Args:
            request: Standardized LLM request.

        Returns:
            Success(LLMResponse) or Failure(AgentError).
        """
        # Step 1: Sanitize
        sanitized_request = self._sanitize_input(request)

        # Step 2: Budget check
        if self._token_budget_daily and self._daily_tokens_used >= self._token_budget_daily:
            return Failure(AgentError(
                code="LLM.BUDGET_EXCEEDED",
                message=f"Daily token budget ({self._token_budget_daily}) exceeded",
                stage="llm_call",
            ))

        # Step 3-4: Try providers
        providers = [self._primary] + self._fallbacks
        last_error = None

        for provider in providers:
            result = await self._try_provider(provider, sanitized_request)
            if result.is_success:
                self._daily_tokens_used += result.value.token_usage.total_tokens
                return result
            last_error = result.error
            self._logger.warning(
                "Provider failed, trying next",
                provider=provider.name,
                error=str(last_error),
            )

        return Failure(AgentError(
            code="LLM.ALL_PROVIDERS_FAILED",
            message="All LLM providers failed",
            stage="llm_call",
            details={"last_error": str(last_error)},
        ))

    def _sanitize_input(self, request: LLMRequest) -> LLMRequest:
        """Remove potential secrets from messages before sending to LLM.

        Scans all message content for patterns that look like:
        - API keys
        - Passwords
        - Connection strings
        - JWT tokens

        See: guardrails/operational-guardrails.md
        """
        ...

    async def _try_provider(
        self,
        provider: "LLMProvider",
        request: LLMRequest,
    ) -> Result[LLMResponse, AgentError]:
        """Try a single provider with retry logic."""
        ...
```

## 3.3 LLM Provider Interface

```python
# src/infrastructure/llm/interfaces.py

from typing import Protocol


class LLMProvider(Protocol):
    """Interface for LLM provider adapters.

    Each provider (OpenAI, Anthropic, local, etc.) implements
    this protocol. The gateway selects which provider to use.
    """

    @property
    def name(self) -> str:
        """Provider identifier (e.g., 'anthropic', 'openai')."""
        ...

    @property
    def default_model(self) -> str:
        """Default model for this provider."""
        ...

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a completion request to this provider.

        Must translate from the standardized LLMRequest format
        to the provider's native API format, and translate the
        response back.

        Raises:
            LLMProviderError: On API call failure.
            LLMRateLimitError: On rate limiting.
            LLMTimeoutError: On timeout.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the provider is reachable."""
        ...
```

## 3.4 Gateway Rules

| Rule | Description |
|------|-------------|
| **GW-001** | All LLM calls go through LLMGateway. No direct provider API calls anywhere. |
| **GW-002** | Every LLM call is logged with: agent name, prompt version, model, token usage, latency |
| **GW-003** | Input sanitization runs on every request before sending to any provider |
| **GW-004** | Response `finish_reason == "length"` is treated as a warning — output may be truncated |
| **GW-005** | Token usage tracked per agent, per day, with configurable daily budget |
| **GW-006** | Default temperature is 0.2 for analytical tasks (low creativity, high consistency) |
| **GW-007** | Provider adapters handle their own rate limiting internally |
| **GW-008** | Gateway never caches LLM responses — each analysis must be fresh |

---

# 4. OUTPUT PARSING AND VALIDATION

## 4.1 Output Parsing Strategy

LLM output is text. It must be parsed into structured data reliably.

```python
# src/shared/agents/output_parser.py

"""LLM output parsing utilities.

The LLM is instructed to return JSON, but it may:
- Wrap it in markdown code blocks (```json ... ```)
- Include preamble text before the JSON
- Include trailing commentary after the JSON
- Return invalid JSON (missing commas, trailing commas, etc.)
- Return partial JSON (if truncated by token limit)

This module handles all these cases.
"""

import json
import re
from src.shared.types import Result, Success, Failure
from src.shared.agents.models import AgentError


def parse_json_output(
    raw_text: str,
    agent_name: str = "",
) -> Result[dict, AgentError]:
    """Parse LLM text output into a JSON dictionary.

    Attempts multiple strategies to extract valid JSON:
    1. Direct JSON parse
    2. Extract from markdown code block
    3. Extract first JSON object from mixed text
    4. Attempt repair of common JSON errors

    Args:
        raw_text: Raw text from LLM response.
        agent_name: Agent name for error context.

    Returns:
        Success(dict) with parsed JSON, or
        Failure(AgentError) with parse error details.
    """
    if not raw_text or not raw_text.strip():
        return Failure(AgentError(
            code=f"AGENT.{agent_name}.EMPTY_OUTPUT",
            message="LLM returned empty output",
            stage="parse_output",
        ))

    # Strategy 1: Direct parse
    try:
        return Success(json.loads(raw_text))
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code block
    code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
    code_match = re.search(code_block_pattern, raw_text, re.DOTALL)
    if code_match:
        try:
            return Success(json.loads(code_match.group(1)))
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find first { ... } block
    brace_start = raw_text.find("{")
    brace_end = raw_text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        try:
            return Success(json.loads(raw_text[brace_start:brace_end + 1]))
        except json.JSONDecodeError:
            pass

    # Strategy 4: Attempt common JSON repairs
    repaired = _attempt_json_repair(raw_text)
    if repaired is not None:
        return Success(repaired)

    # All strategies failed
    return Failure(AgentError(
        code=f"AGENT.{agent_name}.PARSE_FAILED",
        message="Could not parse LLM output as JSON after all strategies",
        stage="parse_output",
        details={
            "raw_text_preview": raw_text[:500],
            "raw_text_length": len(raw_text),
        },
    ))


def _attempt_json_repair(text: str) -> dict | None:
    """Attempt to repair common JSON formatting errors.

    Handles:
    - Trailing commas before closing braces/brackets
    - Single quotes instead of double quotes
    - Missing quotes on keys
    - JavaScript-style comments

    Returns:
        Parsed dict if repair succeeded, None otherwise.
    """
    # Remove JavaScript-style comments
    cleaned = re.sub(r"//.*?\n", "\n", text)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)

    # Remove trailing commas
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    # Try to find and parse JSON object
    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start != -1 and brace_end != -1:
        try:
            return json.loads(cleaned[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    return None
```

## 4.2 Output Validation Pipeline

After parsing, every agent output passes through a validation pipeline:

```python
# src/shared/agents/validator.py

"""Agent output validation pipeline.

Every agent output must pass through this pipeline before being
returned to the caller. The pipeline enforces:
1. Schema compliance (Pydantic model validation)
2. Guardrail compliance (invariants from L0)
3. Citation verification (every claim has a source)
4. Anomaly detection (flagging implausible values)
5. Confidence calibration (data completeness → confidence bounds)
"""

import structlog
from pydantic import ValidationError
from src.shared.types import Result, Success, Failure
from src.shared.agents.models import AgentError, GuardrailViolation


logger = structlog.get_logger(__name__)


class AgentOutputValidator:
    """Validates agent output against schema and guardrails.

    This validator is agent-agnostic. Agent-specific validation
    rules are passed in via configuration.
    """

    def __init__(
        self,
        output_model: type,
        guardrails: list["GuardrailCheck"],
        citation_required: bool = True,
    ) -> None:
        self._output_model = output_model
        self._guardrails = guardrails
        self._citation_required = citation_required
        self._logger = logger.bind(component="AgentOutputValidator")

    def validate(
        self,
        parsed_output: dict,
        input_context: dict,
    ) -> Result[BaseModel, AgentError]:
        """Run full validation pipeline on parsed agent output.

        Args:
            parsed_output: Dict parsed from LLM JSON output.
            input_context: The data context that was provided to the LLM
                (used for citation verification).

        Returns:
            Success with validated Pydantic model, or
            Failure with validation errors.
        """
        violations: list[GuardrailViolation] = []

        # ── Check 1: Schema compliance ──
        try:
            validated_model = self._output_model.model_validate(parsed_output)
        except ValidationError as exc:
            return Failure(AgentError(
                code="AGENT.VALIDATION.SCHEMA_INVALID",
                message=f"Output does not match schema: {exc.error_count()} errors",
                stage="validation",
                details={"errors": exc.errors()},
            ))

        # ── Check 2: Guardrail compliance ──
        for guardrail in self._guardrails:
            result = guardrail.check(validated_model)
            if result is not None:
                violations.append(result)

        # ── Check 3: Citation verification ──
        if self._citation_required:
            citation_violations = self._verify_citations(
                validated_model, input_context
            )
            violations.extend(citation_violations)

        # ── Check 4: Evaluate violations ──
        critical_violations = [v for v in violations if v.severity == "CRITICAL"]
        warning_violations = [v for v in violations if v.severity == "WARNING"]

        if critical_violations:
            self._logger.error(
                "Critical guardrail violations detected",
                violations=[v.code for v in critical_violations],
            )
            return Failure(AgentError(
                code="AGENT.VALIDATION.GUARDRAIL_VIOLATION",
                message=f"{len(critical_violations)} critical guardrail violations",
                stage="validation",
                details={
                    "violations": [v.model_dump() for v in critical_violations]
                },
            ))

        if warning_violations:
            self._logger.warning(
                "Non-critical guardrail warnings",
                violations=[v.code for v in warning_violations],
            )
            # Warnings are attached to output metadata but don't block

        return Success(validated_model)

    def _verify_citations(
        self,
        output: BaseModel,
        context: dict,
    ) -> list[GuardrailViolation]:
        """Verify that cited data sources exist in the provided context.

        Checks that [DATA-*] citation labels in the agent's evidence
        section match labels that were present in the context injection.
        """
        ...
```

## 4.3 Standard Guardrail Checks

```python
# src/shared/agents/guardrails.py

"""Standard guardrail checks for agent output validation.

Each guardrail is a standalone check that examines one aspect
of the agent's output. Guardrails return None if passed, or a
GuardrailViolation if failed.
"""

from src.shared.agents.models import GuardrailViolation


class ForbiddenLanguageGuardrail:
    """Check for language that implies certainty or makes promises.

    Reference: L0-system-vision.md INV-011
    """

    FORBIDDEN_PHRASES: list[str] = [
        "guaranteed",
        "risk-free",
        "certain to",
        "will definitely",
        "cannot fail",
        "sure thing",
        "no risk",
        "100% chance",
        "impossible to lose",
        "always profitable",
    ]

    def check(self, output: BaseModel) -> GuardrailViolation | None:
        full_text = output.model_dump_json().lower()
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in full_text:
                return GuardrailViolation(
                    code="GUARDRAIL.FORBIDDEN_LANGUAGE",
                    severity="CRITICAL",
                    message=f"Output contains forbidden phrase: '{phrase}'",
                    field_path="*",
                )
        return None


class BearCaseRequiredGuardrail:
    """Verify that a bear case is present for directional recommendations.

    Reference: L0-system-vision.md INV-011, Agent Principle P3
    """

    def check(self, output: BaseModel) -> GuardrailViolation | None:
        thesis = getattr(output, "thesis", None)
        if thesis is None:
            return None

        bear_case = getattr(thesis, "bear_case", None)
        if bear_case is None:
            return GuardrailViolation(
                code="GUARDRAIL.MISSING_BEAR_CASE",
                severity="CRITICAL",
                message="Output missing bear case thesis",
                field_path="thesis.bear_case",
            )

        narrative = getattr(bear_case, "narrative", "")
        if len(narrative) < 50:
            return GuardrailViolation(
                code="GUARDRAIL.INSUFFICIENT_BEAR_CASE",
                severity="WARNING",
                message=f"Bear case narrative too short ({len(narrative)} chars)",
                field_path="thesis.bear_case.narrative",
            )

        return None


class ConfidenceCalibrationGuardrail:
    """Enforce confidence → recommendation mapping.

    Reference: L0-system-vision.md INV-012, INV-013
    """

    CONFIDENCE_FLOOR: float = 0.3
    CONFIDENCE_HOLD_CAP: float = 0.5

    DIRECTIONAL_RECOMMENDATIONS: set[str] = {
        "STRONG_BUY", "BUY", "SELL", "STRONG_SELL"
    }

    def check(self, output: BaseModel) -> GuardrailViolation | None:
        confidence = getattr(
            getattr(output, "metadata", None), "confidence_score", None
        )
        recommendation = getattr(
            getattr(output, "summary", None), "recommendation", None
        )

        if confidence is None or recommendation is None:
            return None

        if confidence < self.CONFIDENCE_FLOOR:
            if recommendation != "INSUFFICIENT_DATA":
                return GuardrailViolation(
                    code="GUARDRAIL.CONFIDENCE_FLOOR_BREACH",
                    severity="CRITICAL",
                    message=(
                        f"Confidence {confidence:.2f} < {self.CONFIDENCE_FLOOR} "
                        f"but recommendation is '{recommendation}' "
                        f"(must be 'INSUFFICIENT_DATA')"
                    ),
                    field_path="summary.recommendation",
                )

        elif confidence < self.CONFIDENCE_HOLD_CAP:
            if recommendation in self.DIRECTIONAL_RECOMMENDATIONS:
                return GuardrailViolation(
                    code="GUARDRAIL.CONFIDENCE_HOLD_CAP",
                    severity="CRITICAL",
                    message=(
                        f"Confidence {confidence:.2f} < {self.CONFIDENCE_HOLD_CAP} "
                        f"but recommendation is '{recommendation}' "
                        f"(must be 'HOLD' or 'INSUFFICIENT_DATA')"
                    ),
                    field_path="summary.recommendation",
                )

        return None


class NumericalPlausibilityGuardrail:
    """Check that key financial figures in the output are plausible.

    Cross-references agent-cited figures against the input context
    to detect potential hallucinations.
    """

    def check(self, output: BaseModel, context: dict) -> GuardrailViolation | None:
        """Compare cited figures against source data."""
        ...
```

## 4.4 Validation Rules

| Rule | Description |
|------|-------------|
| **VA-001** | Every agent output must pass schema validation (Pydantic model_validate) |
| **VA-002** | Every agent output must pass all registered guardrail checks |
| **VA-003** | Critical guardrail violations block the output from being returned |
| **VA-004** | Warning-level violations are attached as metadata but do not block |
| **VA-005** | Citation verification checks that [DATA-*] labels exist in context |
| **VA-006** | If validation fails after all retries, agent returns structured Failure, not raw error |
| **VA-007** | Validation failures are logged with full details for debugging |
| **VA-008** | Validation pipeline is configurable per agent (different agents may have different guardrails) |

---

# 5. TOKEN MANAGEMENT AND COST CONTROL

## 5.1 Token Budget Architecture

```python
# src/infrastructure/llm/token_manager.py

"""Token usage tracking and budget management.

Tracks token consumption per agent, per day, and enforces
configurable budgets to prevent runaway costs.
"""

from pydantic import BaseModel
from datetime import date


class TokenBudgetConfig(BaseModel):
    """Token budget configuration."""

    daily_total_limit: int = 1_000_000          # Total tokens per day
    per_agent_daily_limits: dict[str, int] = {
        "research_analyst": 300_000,
        "quant_analyst": 200_000,
        "risk_manager": 200_000,
        "portfolio_strategist": 200_000,
        "report_writer": 100_000,
    }
    per_request_max_input_tokens: int = 100_000  # Max context per call
    per_request_max_output_tokens: int = 8_000   # Max response per call
    cost_alert_threshold_cents: int = 5000       # $50/day alert


class TokenUsageTracker:
    """Track and enforce token budgets.

    Records all token usage and provides budget enforcement.
    Resets daily at midnight UTC.
    """

    def check_budget(
        self,
        agent_name: str,
        estimated_tokens: int,
    ) -> bool:
        """Check if a request is within budget before sending.

        Returns True if the request can proceed, False if it
        would exceed the budget.
        """
        ...

    def record_usage(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        model: str,
        estimated_cost_cents: int,
    ) -> None:
        """Record token usage after a successful LLM call."""
        ...

    def get_daily_summary(self) -> dict:
        """Get today's usage summary by agent."""
        ...
```

## 5.2 Context Size Management

```python
# src/shared/agents/context_manager.py

"""Context size management for LLM calls.

Manages the context window by prioritizing information when
the total context exceeds the model's limit.
"""


class ContextManager:
    """Manages context size within token limits.

    When all available data exceeds the context window, this
    manager prioritizes sections based on configured importance.
    """

    def __init__(
        self,
        max_context_tokens: int = 100_000,
        token_counter: "TokenCounter" | None = None,
    ) -> None:
        self._max_tokens = max_context_tokens
        self._counter = token_counter or ApproximateTokenCounter()

    def fit_context(
        self,
        sections: list["ContextSection"],
    ) -> list["ContextSection"]:
        """Select and trim context sections to fit within token budget.

        Sections are included in priority order (highest first).
        The last section that fits may be truncated.
        Sections that don't fit are listed in the data availability
        disclosure as "excluded due to context limits".

        Args:
            sections: List of context sections ordered by priority.

        Returns:
            Sections that fit within the token budget.
            Excluded sections are noted in the metadata.
        """
        ...


class ContextSection(BaseModel):
    """A single section of context to inject into the prompt."""

    label: str                  # e.g., "DATA-FIN-IS"
    content: str                # The formatted text
    priority: int               # 1 = highest, 10 = lowest
    is_required: bool = False   # If True, failure if it doesn't fit
    estimated_tokens: int = 0   # Pre-calculated token count


# ── Context priority order (standard) ──
CONTEXT_PRIORITY = {
    "task_instruction": 1,       # What the agent should do
    "financial_statements": 2,   # Core financial data
    "price_data": 3,             # Current price and history
    "valuation_metrics": 4,      # Pre-computed ratios
    "existing_thesis": 5,        # Prior analysis to update
    "peer_comparison": 6,        # Competitive context
    "news_summary": 7,           # Recent news
    "sector_context": 8,         # Sector/macro backdrop
    "analyst_estimates": 9,      # Consensus estimates
    "insider_transactions": 10,  # Insider trading data
}
```

## 5.3 Token Management Rules

| Rule | Description |
|------|-------------|
| **TM-001** | Daily token budget is enforced — requests rejected when budget exceeded |
| **TM-002** | Per-agent daily limits prevent one agent from consuming the entire budget |
| **TM-003** | Token usage logged per request: agent, model, input tokens, output tokens, cost |
| **TM-004** | Context size estimated before sending; oversized contexts are trimmed by priority |
| **TM-005** | Requests that would exceed per-request limits are rejected, not truncated silently |
| **TM-006** | Daily cost tracked and alerts triggered at configurable threshold |
| **TM-007** | Token usage reports available for cost optimization analysis |
| **TM-008** | System prompt tokens counted once and cached (they don't change per request) |

---

# 6. VERSIONING AND REPRODUCIBILITY

## 6.1 Agent Execution Metadata

Every agent output includes complete metadata for reproducibility:

```python
# src/shared/agents/models.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class AgentExecutionMetadata(BaseModel):
    """Metadata attached to every agent output.

    This metadata enables:
    - Audit trail: who/what produced this analysis
    - Reproducibility: approximate recreation of the analysis
    - Debugging: understanding what went wrong
    - Performance tracking: latency and cost trends
    """

    # ── Agent identity ──
    agent_name: str
    agent_version: str                  # Semantic version: "1.2.3"
    prompt_version: str                 # Semantic version: "1.0.0"

    # ── LLM details ──
    model_used: str                     # e.g., "claude-3-5-sonnet-20241022"
    model_provider: str                 # e.g., "anthropic"
    temperature: float                  # Temperature used
    max_output_tokens: int              # Token limit used

    # ── Execution details ──
    executed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    execution_latency_ms: int
    correlation_id: str = ""

    # ── Token usage ──
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_cents: int

    # ── Data provenance ──
    data_snapshot_id: str = ""          # Hash of input data
    data_as_of: datetime | None = None  # Freshest data timestamp
    data_sources_used: list[str] = Field(default_factory=list)
    data_sources_missing: list[str] = Field(default_factory=list)
    data_completeness_score: float = 0.0

    # ── Validation results ──
    guardrail_warnings: list[str] = Field(default_factory=list)
    validation_passed: bool = True

    # ── Retry information ──
    retry_count: int = 0
    provider_fallback_used: bool = False


class AgentError(BaseModel):
    """Structured error from agent execution."""

    code: str
    message: str
    stage: str                          # Which pipeline stage failed
    details: dict = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    retryable: bool = False


class GuardrailViolation(BaseModel):
    """A single guardrail check failure."""

    code: str                           # e.g., "GUARDRAIL.FORBIDDEN_LANGUAGE"
    severity: str                       # "CRITICAL" | "WARNING"
    message: str
    field_path: str                     # JSON path to the offending field
```

## 6.2 Data Snapshot Hashing

```python
# src/shared/agents/snapshot.py

"""Data snapshot hashing for reproducibility.

Creates a deterministic hash of all input data provided to an agent.
This hash is stored with the output, enabling verification that
the same input data produces consistent output (within LLM variance).
"""

import hashlib
import json


def compute_data_snapshot_id(data: dict) -> str:
    """Compute a deterministic hash of the data provided to an agent.

    The hash covers all data fields that influence the analysis.
    It does NOT include timestamps, request metadata, or other
    non-analytical fields.

    Args:
        data: Dictionary of all data context provided to the agent.

    Returns:
        SHA-256 hex digest (first 16 characters for readability).

    Note:
        This hash enables approximate reproducibility. Re-running
        the agent with the same data snapshot should produce a
        similar (but not identical, due to LLM non-determinism)
        analysis.
    """
    # Sort keys for determinism
    serialized = json.dumps(data, sort_keys=True, default=str)
    full_hash = hashlib.sha256(serialized.encode()).hexdigest()
    return full_hash[:16]
```

## 6.3 Version Change Policy

```text
AGENT VERSION (agent_version):
  Increment when agent CODE changes.
  Major: Breaking output schema change
  Minor: New capability or guardrail
  Patch: Bug fix, refactor

PROMPT VERSION (prompt_version):
  Increment when prompt TEXT changes.
  Major: Significant analytical framework change
  Minor: New instruction or rule added
  Patch: Wording refinement, typo fix

EXAMPLES:
  Agent v1.0.0, Prompt v1.0.0 → Initial release
  Agent v1.0.0, Prompt v1.1.0 → Added "check insider transactions" instruction
  Agent v1.1.0, Prompt v1.1.0 → Added peer comparison to context builder
  Agent v2.0.0, Prompt v2.0.0 → Changed output schema (breaking)
```

## 6.4 Reproducibility Rules

| Rule | Description |
|------|-------------|
| **VR-001** | Every output includes full AgentExecutionMetadata |
| **VR-002** | Agent version and prompt version tracked independently |
| **VR-003** | Data snapshot hash computed for every execution |
| **VR-004** | Model identifier includes the full version string, not just "gpt-4" |
| **VR-005** | Temperature and token limits recorded in metadata |
| **VR-006** | Version changes documented in agent spec (L5) and prompt file docstrings |
| **VR-007** | Breaking schema changes increment major version |
| **VR-008** | Old agent outputs must remain parseable by the current system (backward compatibility) |

---

# 7. CONFIDENCE SCORING

## 7.1 Confidence Score Framework

Confidence is NOT the agent's subjective feeling. It is a **computed score**
based on measurable factors.

```python
# src/shared/agents/confidence.py

"""Confidence score computation for agent outputs.

Confidence score is a 0.0–1.0 value computed from measurable
factors, NOT from the LLM's self-assessment. The LLM may
contribute a qualitative assessment, but the final score is
computed deterministically from data.

Score interpretation:
  0.0 – 0.3: INSUFFICIENT_DATA — not enough information
  0.3 – 0.5: LOW — analysis possible but limited
  0.5 – 0.7: MODERATE — reasonable analysis, some gaps
  0.7 – 0.9: HIGH — comprehensive analysis
  0.9 – 1.0: VERY HIGH — exceptional data coverage

Reference: L0-system-vision.md INV-012, INV-013
"""

from pydantic import BaseModel


class ConfidenceFactors(BaseModel):
    """Measurable factors that contribute to confidence score."""

    data_completeness: float = 0.0       # 0–1: fraction of requested data available
    data_freshness: float = 0.0          # 0–1: how current is the data
    history_depth: float = 0.0           # 0–1: how much history is available
    source_diversity: float = 0.0        # 0–1: multiple data sources agree
    analytical_coverage: float = 0.0     # 0–1: how many analytical steps completed
    contradiction_level: float = 0.0     # 0–1: 0 = no contradictions, 1 = severe


class ConfidenceWeights(BaseModel):
    """Weights for confidence factors. Must sum to 1.0."""

    data_completeness: float = 0.30
    data_freshness: float = 0.15
    history_depth: float = 0.15
    source_diversity: float = 0.10
    analytical_coverage: float = 0.20
    contradiction_level: float = 0.10


def compute_confidence_score(
    factors: ConfidenceFactors,
    weights: ConfidenceWeights = ConfidenceWeights(),
) -> float:
    """Compute confidence score from measurable factors.

    Formula: score = Σ(factor_i × weight_i) × (1 - contradiction_penalty)

    The contradiction_level factor is treated specially — it acts as
    a penalty that reduces the overall score rather than contributing
    positively.

    Args:
        factors: Measured confidence factors.
        weights: Relative importance of each factor.

    Returns:
        Confidence score between 0.0 and 1.0.
    """
    base_score = (
        factors.data_completeness * weights.data_completeness +
        factors.data_freshness * weights.data_freshness +
        factors.history_depth * weights.history_depth +
        factors.source_diversity * weights.source_diversity +
        factors.analytical_coverage * weights.analytical_coverage
    )

    # Contradiction penalty (reduces score, doesn't add to it)
    contradiction_penalty = factors.contradiction_level * weights.contradiction_level
    score = base_score * (1 - contradiction_penalty)

    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, score))


def compute_data_completeness(
    available_sources: list[str],
    required_sources: list[str],
    optional_sources: list[str],
) -> float:
    """Compute data completeness score.

    Required sources are weighted 2x relative to optional sources.

    Args:
        available_sources: Sources that were successfully fetched.
        required_sources: Sources that are essential for analysis.
        optional_sources: Sources that enhance analysis but aren't critical.

    Returns:
        Completeness score between 0.0 and 1.0.
    """
    if not required_sources and not optional_sources:
        return 1.0

    required_available = sum(
        1 for s in required_sources if s in available_sources
    )
    optional_available = sum(
        1 for s in optional_sources if s in available_sources
    )

    required_weight = 2.0
    optional_weight = 1.0

    total_weight = (
        len(required_sources) * required_weight +
        len(optional_sources) * optional_weight
    )

    achieved_weight = (
        required_available * required_weight +
        optional_available * optional_weight
    )

    return achieved_weight / total_weight if total_weight > 0 else 0.0
```

## 7.2 Confidence Rules

| Rule | Description |
|------|-------------|
| **CF-001** | Confidence score is COMPUTED from factors, not self-assessed by the LLM |
| **CF-002** | The LLM may contribute a qualitative assessment, but the final score is deterministic |
| **CF-003** | Confidence < 0.3 forces recommendation to INSUFFICIENT_DATA (INV-012) |
| **CF-004** | Confidence 0.3–0.5 caps recommendation at HOLD (INV-013) |
| **CF-005** | Confidence factors and their values are included in output metadata |
| **CF-006** | Data completeness is the highest-weighted factor (30%) |
| **CF-007** | Contradictions in data REDUCE confidence, they do not increase it |
| **CF-008** | Confidence score must be recalculated if any input data changes |

---

# 8. MULTI-AGENT COORDINATION

## 8.1 Agent Independence Principle

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   AGENTS DO NOT CALL OTHER AGENTS DIRECTLY.                     ║
║                                                                  ║
║   Agent coordination happens ONLY through the Orchestration     ║
║   layer. Agents receive data and produce output. They do not    ║
║   know about or depend on other agents' existence.              ║
║                                                                  ║
║   This ensures:                                                  ║
║   1. Agents can be tested independently                         ║
║   2. Agent failures don't cascade                               ║
║   3. New agents can be added without changing existing ones     ║
║   4. Research and Quant agents remain analytically independent  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 8.2 Coordination Patterns

```text
PATTERN 1: SEQUENTIAL PIPELINE
────────────────────────────────
Data Engine → Research Agent → Portfolio Strategist Agent

Use when: Later agent needs output of earlier agent as input.
Implementation: Orchestration layer calls agents in sequence,
passing output of A as input to B.

PATTERN 2: PARALLEL INDEPENDENT
────────────────────────────────
           ┌─→ Research Agent ──────┐
Data ──────┤                        ├──→ Synthesis
           └─→ Quant Agent ─────────┘

Use when: Agents analyze the same data independently (preferred for
Research + Quant to avoid confirmation bias).
Implementation: Orchestration layer calls agents concurrently,
collects all outputs for synthesis.

PATTERN 3: FAN-OUT / FAN-IN
────────────────────────────
                ┌─→ Analyze AAPL ──┐
Watchlist ──────┼─→ Analyze MSFT ──┼──→ Rank & Filter
                └─→ Analyze GOOGL ─┘

Use when: Same agent applied to many inputs.
Implementation: Orchestration layer distributes work with
bounded concurrency.

PATTERN 4: CONDITIONAL
──────────────────────
Research Agent → [If recommendation != HOLD] → Risk Check Agent

Use when: Downstream agent only needed under certain conditions.
Implementation: Orchestration layer checks conditions between stages.
```

## 8.3 Agent Communication Contract

Agents communicate through the orchestration layer using typed I/O schemas:

```python
# ── Agents NEVER share state directly ──
# ── Agents communicate through typed schemas ──

# The orchestration layer transforms outputs into inputs:
class OrchestrationStep:
    """A single step in a multi-agent pipeline."""

    async def execute(
        self,
        agent: BaseAgent,
        input_data: BaseModel,
        prior_outputs: dict[str, BaseModel] | None = None,
    ) -> Result[BaseModel, AgentError]:
        """Execute an agent step, optionally with prior outputs.

        Args:
            agent: The agent to execute.
            input_data: Primary input for this agent.
            prior_outputs: Outputs from previous pipeline steps,
                keyed by agent name. The orchestration layer decides
                which prior outputs to include.

        Returns:
            Agent output or error.
        """
        # If prior outputs should be included as context, merge them
        if prior_outputs:
            enriched_input = self._merge_prior_outputs(
                input_data, prior_outputs
            )
        else:
            enriched_input = input_data

        return await agent.execute(enriched_input)
```

## 8.4 Coordination Rules

| Rule | Description |
|------|-------------|
| **MC-001** | Agents never import or call other agents directly |
| **MC-002** | All agent coordination managed by the Orchestration domain |
| **MC-003** | Research and Quant agents MUST run independently (never feed into each other) |
| **MC-004** | Agent outputs are immutable once produced — downstream agents receive copies |
| **MC-005** | Pipeline failures in one agent do not halt others (graceful degradation) |
| **MC-006** | Pipeline timeout enforced at the orchestration level (default: 5 minutes total) |
| **MC-007** | Concurrent agent execution bounded by configurable concurrency limit |
| **MC-008** | Every pipeline run has a correlation_id shared across all agent executions |

---

# 9. DETERMINISTIC VS LLM BOUNDARY

## 9.1 The Decision Framework

```text
┌─────────────────────────────────────────────────────────────────┐
│              DETERMINISTIC vs LLM DECISION MATRIX               │
├─────────────────────────────┬───────────────────────────────────┤
│  USE DETERMINISTIC CODE     │  USE LLM                          │
├─────────────────────────────┼───────────────────────────────────┤
│ Calculate P/E ratio         │ Interpret what P/E means in       │
│                             │ context of this company's stage   │
├─────────────────────────────┼───────────────────────────────────┤
│ Compute SMA, EMA, RSI       │ Interpret indicator confluence    │
│                             │ and what it suggests              │
├─────────────────────────────┼───────────────────────────────────┤
│ Calculate portfolio VaR     │ Explain what VaR means for the    │
│                             │ current portfolio in plain English│
├─────────────────────────────┼───────────────────────────────────┤
│ Parse SEC filing structure  │ Interpret management tone in      │
│ (extract tables, numbers)   │ earnings call transcript          │
├─────────────────────────────┼───────────────────────────────────┤
│ Rank stocks by score        │ Explain why top-ranked stocks     │
│                             │ deserve attention                 │
├─────────────────────────────┼───────────────────────────────────┤
│ Detect price anomalies      │ Assess potential causes and       │
│ (gap, volume spike)         │ investment implications           │
├─────────────────────────────┼───────────────────────────────────┤
│ Compare current vs target   │ Write thesis narrative            │
│ portfolio weights           │ supporting rebalance case         │
├─────────────────────────────┼───────────────────────────────────┤
│ Sum portfolio exposure      │ Assess whether exposure           │
│ by sector                   │ is appropriate given macro outlook│
└─────────────────────────────┴───────────────────────────────────┘

RULE OF THUMB:
  If the answer is a NUMBER → deterministic code
  If the answer is a JUDGMENT → LLM
  If the answer is BOTH → compute the number, send it to the LLM for interpretation
```

## 9.2 Implementation Pattern

```python
class ResearchAnalystAgent(BaseAgent[ResearchInput, ResearchReport]):
    """Research Analyst Agent implementation.

    Demonstrates the deterministic/LLM split:
    - Pre-processing: deterministic (compute ratios, format tables)
    - LLM call: synthesis and narrative generation
    - Post-processing: deterministic (confidence score, validation)
    """

    def _prepare_context(self, raw_data: dict, input_data: ResearchInput) -> dict:
        """Pre-process: ALL computation happens here, not in the LLM.

        The LLM receives pre-computed numbers and interprets them.
        The LLM does NOT compute numbers.
        """
        # ── Deterministic computation ──
        income = raw_data["income_statements"]
        balance = raw_data["balance_sheets"]
        prices = raw_data["price_history"]

        # Compute all ratios BEFORE sending to LLM
        pe_ratio = price_to_earnings(
            prices[-1].close_cents,
            income[-1].eps_cents,
        )
        revenue_growth = [
            (income[i].revenue_cents - income[i-1].revenue_cents)
            / income[i-1].revenue_cents
            for i in range(1, len(income))
        ]
        gross_margin = [
            (s.revenue_cents - s.cogs_cents) / s.revenue_cents
            for s in income
        ]

        # Format for LLM consumption
        context = {
            "financial_tables": self._context_builder.build_financial_context(
                income, balance, raw_data.get("cash_flows", [])
            ),
            "computed_ratios": self._context_builder.build_ratio_context(
                pe_ratio=pe_ratio,
                revenue_growth=revenue_growth,
                gross_margins=gross_margin,
                # ... more pre-computed metrics
            ),
            "price_data": self._context_builder.build_price_context(
                prices[-1].close_cents,
                raw_data["price_summary"],
            ),
            "data_availability": self._context_builder.build_missing_data_disclosure(
                available=list(raw_data.keys()),
                requested=self.REQUIRED_DATA_SOURCES + self.OPTIONAL_DATA_SOURCES,
            ),
        }

        return context

    def _post_process(
        self,
        validated: ResearchReport,
        metadata: AgentExecutionMetadata,
    ) -> ResearchReport:
        """Post-process: deterministic enrichment of LLM output.

        The LLM has produced the narrative. Now we:
        1. Compute confidence score (deterministic)
        2. Attach execution metadata
        3. Add computed fields the LLM shouldn't generate
        """
        # ── Compute confidence (deterministic, not LLM-assessed) ──
        factors = ConfidenceFactors(
            data_completeness=metadata.data_completeness_score,
            data_freshness=self._compute_freshness(metadata.data_as_of),
            history_depth=self._compute_history_depth(metadata),
            source_diversity=self._compute_source_diversity(metadata),
            analytical_coverage=self._compute_analytical_coverage(validated),
            contradiction_level=self._compute_contradiction_level(validated),
        )
        confidence = compute_confidence_score(factors)

        # Override LLM's self-assessed confidence with computed confidence
        validated.metadata.confidence_score = confidence
        validated.metadata.agent_name = metadata.agent_name
        validated.metadata.agent_version = metadata.agent_version
        validated.metadata.generated_at = metadata.executed_at

        # Enforce confidence → recommendation guardrails
        validated = self._apply_confidence_caps(validated, confidence)

        return validated
```

## 9.3 Boundary Rules

| Rule | Description |
|------|-------------|
| **DB-001** | All arithmetic, financial ratios, and metrics computed by deterministic code |
| **DB-002** | LLM receives pre-computed numbers, it does not compute them |
| **DB-003** | Confidence score computed deterministically in post-processing, not by LLM |
| **DB-004** | Technical indicators computed deterministically, LLM interprets results |
| **DB-005** | Risk metrics computed deterministically, LLM contextualizes them |
| **DB-006** | Data quality checks are deterministic, never delegated to LLM |
| **DB-007** | If the LLM produces a number that disagrees with the pre-computed value, the pre-computed value wins |
| **DB-008** | LLM output is treated as a draft that must pass deterministic validation |

---

# 10. GRACEFUL DEGRADATION AND ERROR HANDLING

## 10.1 Degradation Hierarchy

```text
LEVEL 0: FULL SUCCESS
  All data available, LLM responds correctly, all guardrails pass.
  → Return complete output with high confidence.

LEVEL 1: PARTIAL DATA
  Some data sources unavailable but critical data present.
  → Return analysis with reduced confidence and explicit data gaps.
  → Data completeness score reflects what's missing.

LEVEL 2: LLM OUTPUT INVALID
  LLM returns unparseable or schema-invalid output.
  → Retry with same prompt (up to max_retries).
  → If retries exhausted: try fallback provider.
  → If all providers fail: return structured INCOMPLETE output.

LEVEL 3: LLM PROVIDER UNAVAILABLE
  All LLM providers are down.
  → Return pre-computed metrics only (no narrative analysis).
  → Flag output as "COMPUTATIONAL_ONLY — no AI synthesis".
  → Confidence score set to minimum (0.1).

LEVEL 4: CRITICAL DATA UNAVAILABLE
  Core required data (e.g., price data) cannot be fetched.
  → Return error with specific data failure details.
  → Do not attempt analysis with insufficient foundation.
  → Log and alert.

LEVEL 5: SYSTEM ERROR
  Unexpected exception in agent pipeline.
  → Return structured AgentError.
  → Log full stack trace.
  → Alert fund manager.
  → Never crash the calling pipeline.
```

## 10.2 Fallback Output Pattern

```python
# src/shared/agents/fallback.py

"""Fallback output generation for degraded agent operation.

When the full agent pipeline cannot complete (LLM unavailable,
too many parse failures, etc.), produce a structured output
with only the deterministically-computable fields filled in.
"""


def generate_fallback_research_output(
    ticker: str,
    computed_metrics: dict,
    available_data: list[str],
    failure_reason: str,
) -> ResearchReport:
    """Generate a minimal research report without LLM synthesis.

    Fills in all fields that can be computed deterministically:
    - Financial ratios
    - Price performance
    - Technical indicator values
    - Data availability status

    Leaves narrative fields as explicit placeholders:
    - thesis: "AI synthesis unavailable — see computed metrics"
    - risks/catalysts: empty (not fabricated)

    Sets confidence to 0.1 and recommendation to INSUFFICIENT_DATA.
    """
    return ResearchReport(
        metadata=ReportMetadata(
            ticker=ticker,
            confidence_score=0.1,
            data_completeness_score=compute_data_completeness(
                available_data, REQUIRED_SOURCES, OPTIONAL_SOURCES
            ),
            agent_version="fallback",
            generated_at=datetime.now(timezone.utc),
        ),
        summary=ReportSummary(
            one_liner=f"[FALLBACK] Computational analysis only for {ticker}",
            recommendation="INSUFFICIENT_DATA",
            key_risks=["AI synthesis unavailable — manual review required"],
            key_catalysts=[],
        ),
        fundamentals=computed_metrics.get("fundamentals", {}),
        thesis=ThesisSection(
            bull_case=ThesisCase(
                narrative="AI synthesis unavailable. See computed metrics.",
                probability=0.0,
            ),
            base_case=ThesisCase(
                narrative="AI synthesis unavailable. See computed metrics.",
                probability=0.0,
            ),
            bear_case=ThesisCase(
                narrative="AI synthesis unavailable. See computed metrics.",
                probability=0.0,
            ),
        ),
        evidence=EvidenceSection(
            supporting_data_points=[],
            contradictory_signals=[],
            data_gaps=[failure_reason] + [
                s for s in REQUIRED_SOURCES if s not in available_data
            ],
        ),
    )
```

## 10.3 Error Handling Rules

| Rule | Description |
|------|-------------|
| **EH-001** | Agent errors never crash the calling pipeline — always return structured Result |
| **EH-002** | LLM parse failures trigger retries before failing |
| **EH-003** | All retry attempts logged with attempt number and error details |
| **EH-004** | Fallback outputs are clearly marked as degraded (not disguised as full analysis) |
| **EH-005** | Fallback outputs NEVER fabricate narrative — they contain only computed values |
| **EH-006** | LLM provider failures trigger fallback to next provider, then to computational-only mode |
| **EH-007** | Agent timeouts enforced: default 180 seconds, configurable per agent |
| **EH-008** | Every error state has a defined degradation path (no undefined behavior) |

---

# 11. AGENT OBSERVABILITY

## 11.1 Logging Standards for Agents

```python
# ── Every agent execution logs these events ──

# 1. Execution start
logger.info(
    "Agent execution started",
    agent=agent_name,
    agent_version=agent_version,
    ticker=ticker,
    correlation_id=correlation_id,
)

# 2. Data gathering result
logger.info(
    "Data gathering complete",
    agent=agent_name,
    sources_available=["income_statement", "balance_sheet", "prices"],
    sources_missing=["news", "insider_transactions"],
    data_completeness=0.6,
)

# 3. Context size
logger.info(
    "Context assembled",
    agent=agent_name,
    context_tokens=45_230,
    sections_included=8,
    sections_excluded=2,
    excluded_sections=["insider_transactions", "analyst_estimates"],
)

# 4. LLM call result
logger.info(
    "LLM call completed",
    agent=agent_name,
    provider=provider_name,
    model=model_name,
    input_tokens=45_230,
    output_tokens=3_847,
    latency_ms=8_432,
    finish_reason="stop",
    retry_count=0,
)

# 5. Validation result
logger.info(
    "Output validation completed",
    agent=agent_name,
    schema_valid=True,
    guardrail_violations=0,
    guardrail_warnings=1,
    warnings=["GUARDRAIL.INSUFFICIENT_BEAR_CASE"],
)

# 6. Execution complete
logger.info(
    "Agent execution completed",
    agent=agent_name,
    total_latency_ms=12_450,
    confidence_score=0.72,
    recommendation="BUY",
    total_tokens=49_077,
    estimated_cost_cents=15,
)
```

## 11.2 Metrics to Track

| Metric | Granularity | Purpose |
|--------|-------------|---------|
| Execution count | Per agent, per day | Usage patterns |
| Execution latency (p50, p95, p99) | Per agent | Performance monitoring |
| Token usage (input, output, total) | Per agent, per call | Cost tracking |
| Estimated cost | Per agent, per day | Budget monitoring |
| Success rate | Per agent | Reliability |
| Retry rate | Per agent | LLM quality signal |
| Provider fallback rate | Per provider | Provider health |
| Schema validation failure rate | Per agent | Prompt quality signal |
| Guardrail violation rate | Per guardrail | Guardrail calibration |
| Confidence score distribution | Per agent | Calibration monitoring |
| Data completeness distribution | Per agent | Data pipeline health |
| Parse failure rate | Per agent | Output format compliance |

## 11.3 Observability Rules

| Rule | Description |
|------|-------------|
| **OB-001** | All 6 log events (Section 11.1) are mandatory for every agent execution |
| **OB-002** | Token usage logged on every LLM call, not just aggregated |
| **OB-003** | Latency breakdown logged: data gathering, context building, LLM call, validation |
| **OB-004** | Provider fallbacks logged as warnings |
| **OB-005** | Guardrail violations logged with the specific violation code and field |
| **OB-006** | Agent metrics exportable for analysis (JSON or time-series DB) |
| **OB-007** | Daily summary report of agent usage, cost, and health generated automatically |

---

# 12. SECURITY STANDARDS FOR AGENTS

## 12.1 Data Handling in LLM Context

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   NEVER INCLUDE IN LLM PROMPTS:                                ║
║                                                                  ║
║   ✗ API keys, tokens, or credentials                            ║
║   ✗ Database connection strings                                  ║
║   ✗ Internal system architecture details                        ║
║   ✗ Other users' data (N/A for single-user, but future-proof)  ║
║   ✗ Full raw API responses from external providers              ║
║   ✗ Internal IP addresses or service endpoints                   ║
║   ✗ The system prompt of other agents                           ║
║                                                                  ║
║   ALWAYS INCLUDE IN LLM PROMPTS:                                ║
║                                                                  ║
║   ✓ Pre-processed, formatted financial data                     ║
║   ✓ Public market information                                    ║
║   ✓ Clearly labeled data sections with citation labels          ║
║   ✓ Explicit analytical instructions                             ║
║   ✓ Output format specification                                  ║
║   ✓ Guardrail rules                                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 12.2 LLM Output Security

```python
# ── LLM outputs must be sanitized before storage or display ──

def sanitize_agent_output(output: str) -> str:
    """Sanitize LLM output to prevent stored XSS or injection.

    Even though this is a single-user system, sanitizing output
    prevents potential issues if output is displayed in a web
    dashboard or included in generated reports.
    """
    # Remove potential HTML/script injection
    # Remove potential SQL fragments
    # Remove potential file path references
    ...
```

## 12.3 Agent Security Rules

| Rule | Description |
|------|-------------|
| **SE-001** | LLM prompts sanitized by gateway before sending (no credentials) |
| **SE-002** | LLM outputs sanitized before storage or display |
| **SE-003** | Agent cannot access external APIs directly — only through internal services |
| **SE-004** | Agent cannot modify its own configuration, guardrails, or prompts at runtime |
| **SE-005** | Agent cannot access other agents' prompts or internal state |
| **SE-006** | Full LLM prompts logged at DEBUG level only, never at INFO or above |
| **SE-007** | Agent output stored in append-only format for audit trail |

---

# 13. TESTING CHECKLIST FOR AGENTS

When building or modifying any agent, verify:

```text
AGENT STRUCTURE:
────────────────
□ Inherits from BaseAgent
□ Implements all abstract methods
□ Uses LLMGateway, never calls LLM directly
□ Data gathering calls internal services only
□ Pre-processing is deterministic (no LLM calls)
□ Post-processing computes confidence deterministically

PROMPT:
───────
□ System prompt stored in dedicated file with version
□ Output schema specified as JSON in system prompt
□ Guardrails stated as explicit rules
□ Citation labels defined for all data sections
□ Missing data disclosure included in context
□ No secrets or internal details in prompt

OUTPUT:
───────
□ Output schema defined as Pydantic model
□ Schema validation runs on every output
□ All guardrail checks registered and active
□ Citation verification enabled
□ Confidence score computed from factors, not LLM self-assessment
□ Confidence → recommendation mapping enforced
□ Forbidden language check active

METADATA:
─────────
□ AgentExecutionMetadata attached to every output
□ Agent version and prompt version tracked
□ Data snapshot hash computed
□ Token usage recorded
□ Latency recorded

ERROR HANDLING:
───────────────
□ LLM parse failures trigger retry (up to max)
□ Provider failures trigger fallback
□ All-provider-failure produces fallback output, not crash
□ Missing data produces partial output, not error
□ Agent timeout enforced
□ All errors return structured AgentError, not raw exceptions

TESTING:
────────
□ Schema compliance test (output validates against Pydantic model)
□ All guardrails tested individually
□ Forbidden language check tested
□ Confidence calibration tested (low data → low confidence)
□ Fallback output tested (LLM unavailable scenario)
□ Parse failure recovery tested
□ Missing data scenario tested
□ Full happy path integration test
```

---

# 14. CROSS-REFERENCES

| Document                              | Location                                              |
|---------------------------------------|-------------------------------------------------------|
| L0: System Vision                     | `specs/L0-system-vision.md`                           |
| L0: Decision Authority Framework      | `specs/L0-system-vision.md` Section 3                 |
| L0: AI Agent Architecture             | `specs/L0-system-vision.md` Section 5                 |
| L0: LLM Usage Policy                  | `specs/L0-system-vision.md` Section 5.3               |
| L4: Coding Standards                  | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards   | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                 | `specs/L4-conventions/testing-standards.md`            |
| L5: Research Analyst Agent            | `specs/L5-agents/research-analyst-agent.md`           |
| L5: Quant Analyst Agent              | `specs/L5-agents/quant-analyst-agent.md`              |
| L5: Risk Manager Agent              | `specs/L5-agents/risk-manager-agent.md`               |
| L5: Portfolio Strategist Agent       | `specs/L5-agents/portfolio-strategist-agent.md`       |
| Guardrails: AI Output                | `specs/guardrails/ai-output-guardrails.md`            |
| Guardrails: Financial                | `specs/guardrails/financial-guardrails.md`             |
| Guardrails: Operational              | `specs/guardrails/operational-guardrails.md`           |

---
```
