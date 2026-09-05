"""D-08 §7 — retry classification. OR-14, OR-14a, OR-15.

```text
╔══════════════════════════════════════════════════════════════════╗
║  RETRY TRANSPORT.  NEVER RETRY SEMANTICS.                        ║
║                                                                  ║
║  RETRYABLE — the request did not get a real answer:              ║
║      timeout · connection reset · HTTP 429 · 5xx · rate limit     ║
║                                                                  ║
║  NOT RETRYABLE — the system got an answer it did not like:       ║
║      data-quality · schema · validation · a missing ticker       ║
║      · an LLM returning unusable output · HTTP 402               ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **HTTP 402 is the one that looks transport and is not.** `L1-data-engine` §5A:
it means *"not on your plan"*, and **retrying it forever is a bill, not a fix.**
"""

from __future__ import annotations

from dataclasses import dataclass

from src.orchestration.errors import SemanticRetryError, UnclassifiedRetryError

RETRYABLE, SEMANTIC = "retryable", "semantic"

#: ★ The classification is EXPLICIT per error, never a blanket `except: retry`.
TRANSPORT_CODES = frozenset({
    "HTTP_429", "HTTP_500", "HTTP_502", "HTTP_503", "HTTP_504",
    "TIMEOUT", "CONNECTION_RESET", "RATE_LIMIT", "DNS_FAILURE",
})

#: ⚠ Answers the system did not like. Asking again does not change the answer.
SEMANTIC_CODES = frozenset({
    "HTTP_400", "HTTP_401", "HTTP_403", "HTTP_404",
    #: ★ The entitlement code. It reads like a payment hiccup and is a plan
    #: boundary — see `L1-data-engine` §5A and DE-46's classification probe.
    "HTTP_402",
    "SCHEMA_VIOLATION", "VALIDATION_FAILED", "DATA_QUALITY", "MISSING_TICKER",
    "LLM_UNUSABLE", "RES.LLM.DEGRADED", "PRECISION_LOSS",
})

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BACKOFF_S = 2.0


def classify(error_code: str) -> str | None:
    """★ OR-14 — an **unclassified** error returns `None`, and `None` means stop."""
    if error_code in TRANSPORT_CODES:
        return RETRYABLE
    if error_code in SEMANTIC_CODES:
        return SEMANTIC
    return None


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """OR-15 — bounded, backed off, and **recorded**."""

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    backoff_s: float = DEFAULT_BACKOFF_S

    def should_retry(self, *, job_id: str, error_code: str, attempt: int) -> bool:
        """Raises rather than returning False for the two cases that are defects.

        ⚠ A `False` return and a raise are different findings: *this failed and
        we stopped trying* is normal; *someone asked to retry a validation
        breach* is a defect in the caller.
        """
        kind = classify(error_code)
        if kind is None:
            raise UnclassifiedRetryError(job_id, error_code)
        if kind == SEMANTIC:
            raise SemanticRetryError(job_id, error_code)
        return attempt < self.max_attempts

    def delay_for(self, attempt: int) -> float:
        return self.backoff_s * (2 ** max(0, attempt - 1))

    def to_json_obj(self) -> dict:
        return {"max_attempts": self.max_attempts, "backoff_s": self.backoff_s}


def gateway_attempts(job_attempts: int, gateway_attempts_: int) -> dict:
    """OR-14a / GW-16 — ★ the gateway's own retries reach the RunManifest.

    ⚠ *An exception that hid its retries would make a flaky run look clean.*
    D-08 owns retry for **jobs**; the gateway owns it for **calls**, because a
    429 inside a D-01 call never reaches orchestration — and **both obey the
    same classification** (EH-15).
    """
    return {"job_attempts": job_attempts, "gateway_attempts": gateway_attempts_,
            "total_transport_retries": max(0, job_attempts - 1) + max(0, gateway_attempts_ - 1)}
