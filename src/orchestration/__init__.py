"""D-08 Orchestration — custody of the schedule. SEAT-5 · LEVEL 0.

⚠ **B3 SLICE: this is the walking-skeleton SHIM, not D-08** (L3 BS-12). It
supplies a declared job graph, a `RunManifest` and a `RunOutcome`. Retry
classification, time budgets, the DST-safe cadence, preconditions, locks and
checkpoints are **B6**, when D-08 replaces it (BS-16).

★ **No domain may import this package** (OR-3) — invocation is one-way, and it
is grep-checked in CI alongside ST-2/ST-5/ST-9.
"""

from src.orchestration.contracts.manifest import (
    BLOCKED_PRECONDITION, BUDGET_EXCEEDED, FAILED, INCOMPLETE, JobRun, RunManifest,
    RunOutcome, SUCCESS, Stub, config_hash, git_state, new_run_id,
)
from src.orchestration.errors import (
    AnchorMismatchError, AnchorUndeclaredError, BoundaryError,
    BudgetExceededError, CadenceClaimedError, LockHeldError, ManifestMissingError,
    OpenUnconfirmedError, OrchestrationError, PreconditionUnevaluableError,
    RetrainNonTradingDayError, RunIncompleteError, SemanticRetryError,
    StaleInputError, UnclassifiedRetryError, UngatedPromotionError,
    UtcPinnedCadenceError,
)
from src.orchestration.jobs.graph import (
    DAILY_INFERENCE, Job, JobGraph, TIMER_POLICY_MARKERS,
    assert_timer_has_no_policy,
)
from src.orchestration.jobs.runner import (
    FAILURE_NOTICE_FIELDS, Orchestrator, artifact_allowed, assert_artifact_allowed,
    assert_no_analysis, failure_notice, plan,
)
from src.orchestration.policy.budget import Budgets, DEFAULT_RUN_SECONDS
from src.orchestration.policy.retry import (
    RETRYABLE, RetryPolicy, SEMANTIC, SEMANTIC_CODES, TRANSPORT_CODES, classify,
    gateway_attempts,
)
from src.orchestration.schedule.cadence import (
    Cadence, DAILY_LOCAL_TIME, DECISION_ANCHOR, MARKET_TZ, first_trading_day,
    is_retrain_morning,
)
from src.orchestration.schedule.preconditions import (
    BlockedPrecondition, Precondition, assert_anchor, assert_cadence_unclaimed,
    assert_inputs_fresh, assert_lock, assert_open_confirmed, assert_trading_day,
)
from src.orchestration.state.locks import (
    AttemptLog, CadenceClaims, Checkpoints, RunLock,
)
from src.orchestration.jobs.skeleton import (
    JOB_GRAPH, JOB_GRAPH_ID, b3_stubs, build_manifest, finish, plan as skeleton_plan, topological_order,
)
from src.orchestration.state.manifest_store import ManifestImmutableError, ManifestStore

__all__ = [
    # the B3 walking skeleton (BS-16 replaces its runner, not its contracts)
    "BLOCKED_PRECONDITION", "BUDGET_EXCEEDED", "FAILED", "INCOMPLETE",
    "JOB_GRAPH", "JOB_GRAPH_ID", "JobRun", "ManifestImmutableError",
    "ManifestStore", "RunManifest", "RunOutcome", "SUCCESS", "Stub",
    "b3_stubs", "build_manifest", "config_hash", "finish", "git_state",
    "new_run_id", "skeleton_plan", "topological_order",
    # the real D-08 (B6)
    "AnchorMismatchError", "AnchorUndeclaredError", "AttemptLog",
    "BlockedPrecondition", "BoundaryError", "BudgetExceededError", "Budgets",
    "Cadence", "CadenceClaimedError", "CadenceClaims", "Checkpoints",
    "DAILY_INFERENCE", "DAILY_LOCAL_TIME", "DECISION_ANCHOR",
    "DEFAULT_RUN_SECONDS", "FAILURE_NOTICE_FIELDS", "Job", "JobGraph",
    "LockHeldError", "MARKET_TZ", "ManifestMissingError", "OpenUnconfirmedError",
    "Orchestrator", "OrchestrationError", "Precondition",
    "PreconditionUnevaluableError", "RETRYABLE", "RetrainNonTradingDayError",
    "RetryPolicy", "RunIncompleteError", "RunLock", "SEMANTIC", "SEMANTIC_CODES",
    "SemanticRetryError", "StaleInputError", "TIMER_POLICY_MARKERS",
    "TRANSPORT_CODES", "UnclassifiedRetryError", "UngatedPromotionError",
    "UtcPinnedCadenceError", "artifact_allowed", "assert_anchor",
    "assert_artifact_allowed", "assert_cadence_unclaimed", "assert_inputs_fresh",
    "assert_lock", "assert_no_analysis", "assert_open_confirmed",
    "assert_timer_has_no_policy", "assert_trading_day", "classify",
    "failure_notice", "first_trading_day", "gateway_attempts",
    "is_retrain_morning", "plan",
]
