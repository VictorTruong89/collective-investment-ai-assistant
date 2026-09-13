"""F2 `CT-2.1`–`CT-2.4`, `CT-2.7` — the trace record shapes.

★ **These EXTEND the existing run record downward.** `RunManifest` / `RunOutcome`
(`src/orchestration/contracts/manifest.py`, `OR-13`) answer *which jobs ran*.
F2 answers *what happened inside a job* — and joins to them by `run_id`,
never duplicating them (`AC-2.1`, `P4`, `PG-8`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Status = Literal["SUCCESS", "FAILED", "INCOMPLETE"]


def mint_decision_id(run_id: str, ticker: str, attempt: int = 1) -> str:
    """`CT-2.7` — minted once per `(run_id, ticker, attempt)`.

    ★ Minted at the START of a ticker's analysis, before any routing or verdict
    exists, because routing (`F6a`) runs *before* D-12 composes a verdict — an id
    minted at verdict time could not be referenced by the records preceding it.

    ⚠ `attempt` 2+ is a drill-down (`QR-16`): a SEPARATE analysis of the same
    ticker, which mints its own id rather than reusing the scheduled one.
    """
    if not run_id or not ticker:
        raise ValueError("decision_id needs a run_id and a ticker (CT-2.7)")
    if attempt < 1:
        raise ValueError(f"attempt starts at 1, got {attempt}")
    return f"{run_id}:{ticker}:{attempt}"


@dataclass(frozen=True, slots=True)
class TraceRecord:
    """Base: everything joins to the existing run by `run_id`.

    ⚠ Subclasses call `TraceRecord.validate(self)` explicitly rather than
    `super().validate()`. `@dataclass(slots=True)` **builds a new class object**
    and the zero-argument `super()` closes over the ORIGINAL one, so `super()`
    inside a slotted dataclass subclass raises
    `TypeError: obj is not an instance or subtype of type`. The explicit call is
    the fix; it is not a style choice.
    """

    run_id: str

    #: Discriminator written into the JSONL line — `D1`'s one-file layout.
    @property
    def type(self) -> str:
        return type(self).__name__

    def to_json_obj(self) -> dict[str, Any]:
        return {"type": self.type, **asdict(self)}

    def validate(self) -> None:
        if not self.run_id:
            raise ValueError("every trace record carries a run_id (AC-2.1)")

    @property
    def record_key(self) -> str:
        """Identity for append-only enforcement (`AC-2.8`)."""
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class StepRecord(TraceRecord):
    """`CT-2.1` — one per step, beneath an existing `JobRun`."""

    job_id: str = ""
    step_id: str = ""
    node: str = ""
    started_at: str = ""
    ended_at: str | None = None
    status: Status = "INCOMPLETE"
    parent_step_id: str | None = None
    #: ⚠ Nullable — null for run-scoped steps not about one ticker (`CT-2.7`).
    decision_id: str | None = None
    #: ⚠ Nullable — vision §3 gives cross-cutting D-00 work no seat.
    seat: int | None = None
    provenance: dict | None = None

    def validate(self) -> None:
        TraceRecord.validate(self)
        if not self.step_id:
            raise ValueError("step_id is required and unique within the run")
        if self.seat is not None and not 1 <= self.seat <= 9:
            raise ValueError(f"seat must be 1..9 or null, got {self.seat}")

    @property
    def record_key(self) -> str:
        return f"step:{self.step_id}"


@dataclass(frozen=True, slots=True)
class ExternalCall(TraceRecord):
    """`CT-2.2` — ⭐ the replay substrate.

    ⚠ `request` and `response` are stored BESIDE the log (`D1`), referenced by
    `call_id`, so `D2` can expire them by deleting a directory rather than
    rewriting an append-only file.
    """

    step_id: str = ""
    call_id: str = ""
    kind: Literal["llm", "tool", "http"] = "tool"
    request: Any = None
    response: Any = None
    model_id: str | None = None
    prompt_version: str | None = None
    #: ★★★ `DX-76` — WHICH SHARED ENVELOPE was composed in front of the prompt.
    #: ⚠⚠ `prompt_version` names the BLOCK's version and nothing else. `DX-67`
    #: prepended `S-1`…`S-6` to every call and bumped no version — `E-02` is
    #: `v2` before and after — so a pre-envelope and a post-envelope recording
    #: were **indistinguishable in the trace**, and the drift guard written to
    #: catch a retired prompt was structurally blind to the largest prompt
    #: change the project has made. ★ `None` = pre-`DX-76`, i.e. unknown; it is
    #: deliberately not "none", which means *an envelope was composed and it
    #: was empty*.
    envelope_hash: str | None = None
    #: ★★ `DX-95` (`CT-2.2` `A6`) — WHICH EVIDENCE BUNDLE the call read.
    #: `prompt_version` + `envelope_hash` name the prompt; this names the
    #: evidence (`RA-2`). ⚠ Load-bearing since `DX-85`ⓒ: Stage-A bundles differ
    #: by which extraction runs were loaded. `None` = unknown, pre-`DX-95`.
    bundle_hash: str | None = None
    tokens: dict = field(default_factory=dict)
    cost_usd: float | None = None
    latency_ms: int = 0
    error: str | None = None

    def validate(self) -> None:
        TraceRecord.validate(self)
        if not self.call_id:
            raise ValueError("call_id is required")
        if self.request is None:
            raise ValueError("request is required — a call without it cannot be replayed")
        if self.response is None and not self.error:
            raise ValueError(
                "a call needs a response or an explicit error (AC-2.2) — a request "
                "without either cannot be replayed and must not read as complete"
            )

    @property
    def record_key(self) -> str:
        return f"call:{self.call_id}"


@dataclass(frozen=True, slots=True)
class DecisionRecord(TraceRecord):
    """`CT-2.3` — ⭐ `PG-9`. ⚠ `decision_id` is a REFERENCE to `CT-2.7`, not owned here."""

    step_id: str = ""
    decision_id: str = ""
    state: dict | None = None
    candidates: list | None = None
    action: str | None = None
    reason: str | None = None
    propensity: float | None = None
    influenced_by: str | None = None

    def validate(self) -> None:
        TraceRecord.validate(self)
        for f_ in ("state", "candidates", "action", "reason", "propensity"):
            if getattr(self, f_) is None:
                raise ValueError(
                    f"{f_} is required (AC-2.5, PG-9) — a control-plane decision "
                    "that cannot say why it was taken is not explainable"
                )

    @property
    def record_key(self) -> str:
        return f"decision:{self.step_id}"


@dataclass(frozen=True, slots=True)
class CapabilityDelta(TraceRecord):
    """`CT-2.4` — ⭐ `PG-5.2`. Written whenever the capability runs.

    ⚠ Including when `changed` is false: the no-change cases are half the
    comparison, and dropping them biases the Tier-B study invisibly — the
    surviving sample is exactly the subset where the capability did something.
    """

    decision_id: str = ""
    capability: str = ""
    pre: Any = None
    post: Any = None
    changed: bool = False

    def validate(self) -> None:
        TraceRecord.validate(self)
        if not self.decision_id:
            raise ValueError("CapabilityDelta requires a decision_id (CT-2.4, PG-5.2)")
        if not self.capability:
            raise ValueError("capability is required")

    @property
    def record_key(self) -> str:
        return f"delta:{self.decision_id}:{self.capability}"
