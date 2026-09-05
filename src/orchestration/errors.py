"""D-08 error family (L4 §5.3) — §13's catalogue.

★ **Every error here is a refusal to start or a refusal to continue.** D-08
computes nothing, so it has no wrong answers to give — only runs it should not
have allowed.
"""

from __future__ import annotations

from src.shared.errors import PipelineError


class OrchestrationError(PipelineError):
    code = "ORC.UNSPECIFIED"
    retryable = False


# --------------------------------------------------------------------------- #
# Preconditions — §5, §5A
# --------------------------------------------------------------------------- #

class PreconditionUnevaluableError(OrchestrationError):
    """OR-6 / AC-8.8 — ★ *it never defaults to "probably fine".*"""

    code = "ORC.PRECOND.UNEVALUABLE"

    def __init__(self, name: str, why: str) -> None:
        super().__init__(
            f"precondition {name!r} could not be evaluated: {why}. A "
            f"precondition that cannot be checked blocks the run (OR-6, P5)")


class StaleInputError(OrchestrationError):
    """OR-5(b) / AC-8.7 — inputs older than the freshness rule."""

    code = "ORC.PRECOND.STALE_INPUT"

    def __init__(self, artifacts, max_age_days: int) -> None:
        super().__init__(
            f"{sorted(artifacts)!r} are older than {max_age_days}d (OR-5)")


class OpenUnconfirmedError(OrchestrationError):
    """OR-33 / AC-8.31 — ★★ the day-T open is missing, unsettled or synthetic.

    ⚠ **Never substituted with the previous close.** That substitution is silent
    and *makes the decision a day stale while looking current.*
    """

    code = "ORC.PRECOND.OPEN_UNCONFIRMED"

    def __init__(self, as_of, ticker: str, why: str) -> None:
        where = f" for {ticker}" if ticker else ""
        super().__init__(
            f"day-T open{where} on {as_of} is unusable: {why}. The run blocks; "
            f"it never falls back to the previous close (OR-32, OR-33, P5)")


class CadenceClaimedError(OrchestrationError):
    """OR-46 / AC-8.37 — a completed run already claimed this window.

    ★ **INFO, not a failure**: *OR-42 deliberately prefers redundant firings
    with strict preconditions over an exactly-once timer.*
    """

    code = "ORC.PRECOND.CADENCE_CLAIMED"

    def __init__(self, cadence_key: str, run_id: str) -> None:
        super().__init__(
            f"cadence window {cadence_key!r} was already completed by run "
            f"{run_id!r}. A second firing inside one window is expected and "
            f"blocks rather than duplicating the run (OR-42, OR-46)")


class LockHeldError(OrchestrationError):
    """OR-24 / AC-8.25 — ★ the holder is named, because *a stuck lock must be
    diagnosable, not mysterious.*"""

    code = "ORC.LOCK.HELD"

    def __init__(self, job_graph_id: str, holder: str) -> None:
        super().__init__(
            f"{job_graph_id}: the lock is held by {holder!r} (OR-24)")


class UtcPinnedCadenceError(OrchestrationError):
    """OR-30 / AC-8.29 — ★ a schedule stored as a UTC constant.

    ⚠ *A cron pinned at 14:00 UTC runs at 09:00 ET all winter — thirty minutes
    before the market opens*, and the day-T open would not exist.
    """

    code = "ORC.CADENCE.UTC_PINNED"

    def __init__(self, job_graph_id: str) -> None:
        super().__init__(
            f"{job_graph_id}: the cadence is stored in UTC. It is "
            f"`(local_time, tz)` and is resolved per date — 10:00 ET is 14:00 "
            f"UTC in summer and 15:00 in winter (OR-30, OR-8, INV-007)")


class AnchorMismatchError(OrchestrationError):
    """OR-35 / AC-8.32 — the model was trained on a different anchor.

    ⚠ **A full session of drift on every single prediction, and invisible in
    backtest** because the backtest shares the training anchor.
    """

    code = "ORC.CADENCE.ANCHOR_MISMATCH"

    def __init__(self, manifest_anchor: str, trained_anchor: str) -> None:
        super().__init__(
            f"the run decides on the {manifest_anchor!r} anchor and the model "
            f"was trained on {trained_anchor!r} (OR-35, INV-4)")


class AnchorUndeclaredError(OrchestrationError):
    """OR-44 / AC-8.32a — ★★ a model artifact declaring no training anchor.

    ⚠ *"Trained on the same anchor"* and *"we do not know what it was trained
    on"* are **opposite findings**, and assuming the first is how INV-4's drift
    becomes undetectable (DE-35's shape).
    """

    code = "ORC.CADENCE.ANCHOR_UNDECLARED"

    def __init__(self, artifact_id: str) -> None:
        super().__init__(
            f"model {artifact_id!r} declares no `trained_anchor`. The run "
            f"blocks: an undeclared anchor is not a matching one (OR-44)")


class RetrainNonTradingDayError(OrchestrationError):
    """OR-37 / AC-8.33 — no trading day found for the retrain month."""

    code = "ORC.RETRAIN.NON_TRADING_DAY"

    def __init__(self, year: int, month: int) -> None:
        super().__init__(
            f"no trading day found in {year}-{month:02d} within 15 days of the "
            f"1st — the calendar is unusable, and a calendar-blind rule would "
            f"skip the month or run against a closed market (OR-37)")


class UngatedPromotionError(OrchestrationError):
    """OR-38 / AC-8.34 — ★ a model promoted and used inside the same run.

    *A model promoted at 10:05 and used at 10:06 has passed no gate.*
    """

    code = "ORC.RETRAIN.UNGATED_PROMOTION"

    def __init__(self, artifact_id: str) -> None:
        super().__init__(
            f"model {artifact_id!r} was promoted and used in the same run. "
            f"Inference runs on the INCUMBENT; promotion takes effect on the "
            f"next trading day (OR-38, D-04 §7)")


# --------------------------------------------------------------------------- #
# Identity, retry, budget — §6, §7, §8
# --------------------------------------------------------------------------- #

class ManifestMissingError(OrchestrationError):
    """OR-9 / AC-8.10 — work attempted before a manifest was written.

    ★ **D-08 is the only layer that can enforce INV-2**: a domain can be
    deterministic in isolation and the pipeline still irreproducible, because
    reproducibility is a property of *the whole invocation*.
    """

    code = "ORC.MANIFEST.MISSING"

    def __init__(self, job_id: str) -> None:
        super().__init__(
            f"job {job_id!r} was started with no RunManifest. Every run emits "
            f"one BEFORE it does any work — determinism has no owner if D-08 "
            f"does not own the manifest (OR-9, OR-10)")


class SemanticRetryError(OrchestrationError):
    """OR-14 / AC-8.17 — ★★ retry attempted on a non-transport failure.

    ```
    RETRY TRANSPORT.  NEVER RETRY SEMANTICS.
    ```
    ⚠ *Retrying a semantic failure LAUNDERS A HARD FAILURE INTO A SOFT ONE* — it
    converts *"this input is bad"* into *"this eventually succeeded"*, which is
    how a discipline card was once built from a failed LLM narrative and emailed
    as a real recommendation.
    """

    code = "ORC.RETRY.SEMANTIC_ATTEMPTED"

    def __init__(self, job_id: str, error_code: str) -> None:
        super().__init__(
            f"{job_id}: {error_code} is a semantic failure and was retried. The "
            f"system got an answer it did not like; asking again does not "
            f"change the answer (OR-14, P5)")


class UnclassifiedRetryError(OrchestrationError):
    """OR-14 / AC-8.18 — ★ *the safe default is to stop.*"""

    code = "ORC.RETRY.UNCLASSIFIED"

    def __init__(self, job_id: str, error_code: str) -> None:
        super().__init__(
            f"{job_id}: {error_code!r} has no retry classification, so it is "
            f"NOT retried. An unclassified error is not retryable (OR-14)")


class RunIncompleteError(OrchestrationError):
    """OR-16 / AC-8.19 — ★★ **partial success is failure.**

    ⚠ *The two real incidents in this repo both came from a downstream consumer
    treating a degraded upstream as usable.*
    """

    code = "ORC.RUN.INCOMPLETE"

    def __init__(self, run_id: str, failed) -> None:
        super().__init__(
            f"run {run_id!r} is INCOMPLETE ({sorted(failed)!r} failed) and may "
            f"produce no human-facing artifact (OR-16, DC-3, P5)")


class BudgetExceededError(OrchestrationError):
    """OR-21/OR-22 / AC-8.23, AC-8.24 — ★ **it never truncates and emits.**

    ⚠ *"Emit what we have" is the plausible-looking default P5 forbids — a
    half-computed slate is more dangerous than no slate, because it looks
    complete.*
    """

    code = "ORC.BUDGET.EXCEEDED"

    def __init__(self, job_id: str, budget_s: float, elapsed_s: float) -> None:
        super().__init__(
            f"{job_id}: {elapsed_s:.1f}s against a {budget_s:.1f}s budget. The "
            f"run fails; it does not emit the remainder (OR-21, OR-22)")


class BoundaryError(OrchestrationError):
    """OR-1/OR-2 / AC-8.1, AC-8.2 — orchestration computed or wrote the book."""

    code = "ORC.BOUNDARY.COMPUTATION"

    def __init__(self, what: str) -> None:
        super().__init__(
            f"{what}. D-08 invokes; it never computes, never writes the book "
            f"and never originates a verdict (OR-1, OR-2, OR-4)")
