"""The LLM gateway — a transport with guards (L2-shared-infrastructure §4, §5).

```
╔══════════════════════════════════════════════════════════════════╗
║  IT COMPOSES NO PROMPT AND INTERPRETS NO OUTPUT.                 ║
║                                                                  ║
║  GW-2 — it receives a prompt with a name and version and sends   ║
║         it. Authoring is D-01's.                                 ║
║  GW-3 — it parses to the declared schema and raises on failure;  ║
║         what the content MEANS is D-01's.                        ║
║                                                                  ║
║  GW-1/ST-5 — imported ONLY by src/fundamental/. Enforced tree-   ║
║  wide by tests_src/test_architecture.py, not by good intentions. ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **The guard this file exists for is GW-22**: the gateway never returns a
partial, truncated or default response as a successful one. **Both real
incidents in this repo are that defect** — a discipline card built from a
*failed* LLM narrative and one built from an *absent* narrative, each emailed as
a genuine recommendation with no stop and no targets. **The gateway is the last
place either could have been caught**, which is why `Outcome` has no `partial`
member: the shape makes the mistake unrepresentable rather than discouraged.

⚠ **One provider, deliberately no port.** QI-5 closed: Anthropic only. So there
is no `Protocol` here (L4 CA-7 forbids speculative abstractions) — `transport`
is a plain injected callable, which is what makes the suite hermetic. INV-8's
Haiku↔Opus tiering is a MODEL swap, not a provider swap.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping

from src.shared.errors import (
    BudgetExceededError,
    DecodingControlError,
    DriftBlockedError,
    RefusedError,
    SemanticRetryError,
    TransportError,
    TruncatedError,
    UnparseableError,
)


class Tier(str, Enum):
    """INV-8. A property of the CALL SITE, declared statically (GW-4).

    Never chosen at runtime from data: a gateway that picks a model based on its
    input is making a cost/quality judgement, which §1.2 forbids it to hold.
    """

    CHEAP = "cheap"
    DEEP = "deep"


class Outcome(str, Enum):
    """CT-0.1. ★ There is NO `partial` — that absence is GW-22 made structural."""

    OK = "ok"
    TRANSPORT_FAILED = "transport_failed"
    REFUSED = "refused"
    TRUNCATED = "truncated"
    UNPARSEABLE = "unparseable"
    DRIFT_BLOCKED = "drift_blocked"


@dataclass(frozen=True, slots=True)
class Decoding:
    """CT-0.1's `decoding` object (GW-9).

    ★ An object rather than a flat `temperature` field, and that is the
    load-bearing choice: a flat `temperature: null` cannot distinguish *"this
    model has no such parameter"* from *"nobody set it"* — and the second is the
    defect GW-9 exists to prevent, so a record conflating them defeats its own
    check.
    """

    control: str                      # "effort" (deep) | "temperature" (cheap)
    effort: str | None = None
    temperature: float | None = None
    thinking_mode: str | None = None

    def fingerprint(self) -> str:
        """The value a baseline keys on (GW-9b).

        ⚠ RM-5 today re-baselines on an INV-8 *tier* change, and `high → xhigh`
        is not one. This makes the decoding settings comparable across runs so
        that check can be written; **the check itself lives in D-01 and does not
        exist yet** — AC-0.4c is partial by construction, not by omission.
        """
        return f"{self.control}:{self.effort or self.temperature}:{self.thinking_mode}"

    def to_json_obj(self) -> dict:
        return {
            "control": self.control,
            "effort": self.effort,
            "temperature": self.temperature,
            "thinking_mode": self.thinking_mode,
        }


def decoding_for(tier: Tier, cfg: Mapping[str, Any]) -> Decoding:
    """Build the decoding controls the tier's model actually accepts (§5.2a).

    ★ The two tiers take MUTUALLY EXCLUSIVE controls:
        cheap (`claude-haiku-4-5`)  temperature settable, effort errors
        deep  (`claude-opus-5`)     temperature REJECTED with a 400, effort valid
    """
    if tier is Tier.DEEP:
        effort = cfg.get_optional("llm.deep.effort")
        if not effort:
            raise DecodingControlError(
                "deep-tier calls must set `effort` explicitly (GW-9a) — omitting it "
                "takes the provider default, which is a baseline nobody controls"
            )
        if cfg.get_optional("llm.deep.temperature") is not None:
            raise DecodingControlError(
                "deep tier must not set `temperature`: claude-opus-5 REJECTS the "
                "parameter with a 400 (GW-8a). Use `effort` — and see L2 §5.2a"
            )
        thinking = cfg.get_optional("llm.deep.thinking_mode") or "adaptive"
        if thinking == "disabled":
            raise DecodingControlError(
                "thinking must not be disabled on the deep tier (GW-9c): Opus 5 can "
                "then write a tool call into VISIBLE TEXT — the turn succeeds, the "
                "call never runs, and D-01's extraction presents as a document that "
                "said nothing"
            )
        return Decoding(control="effort", effort=effort, thinking_mode=thinking)

    temperature = cfg.get_optional("llm.cheap.temperature")
    if temperature is None:
        raise DecodingControlError(
            "cheap-tier calls must set `temperature` explicitly (GW-8) — an unset "
            "temperature runs at the provider default, the maximum available "
            "variance, chosen by omission"
        )
    return Decoding(control="temperature", temperature=float(temperature))


@dataclass(frozen=True, slots=True)
class LLMCall:
    """CT-0.1 — one record per gateway invocation."""

    call_id: str
    run_id: str
    prompt_name: str
    prompt_version: str
    tier: str
    model_id: str
    decoding: Decoding
    max_tokens: int
    alignment_ok: bool
    attempts: int
    retry_reasons: tuple[str, ...]
    tokens_in: int
    tokens_out: int
    elapsed_ms: int
    outcome: str
    ticker: str | None = None
    probe: str | None = None
    cost_usd: float = 0.0

    def to_json_obj(self) -> dict:
        return {
            "call_id": self.call_id, "run_id": self.run_id, "ticker": self.ticker,
            "prompt_name": self.prompt_name, "prompt_version": self.prompt_version,
            "tier": self.tier, "model_id": self.model_id,
            "decoding": self.decoding.to_json_obj(),
            "max_tokens": self.max_tokens, "alignment_ok": self.alignment_ok,
            "attempts": self.attempts, "retry_reasons": list(self.retry_reasons),
            "tokens_in": self.tokens_in, "tokens_out": self.tokens_out,
            "elapsed_ms": self.elapsed_ms, "outcome": self.outcome,
            "probe": self.probe, "cost_usd": round(self.cost_usd, 6),
        }


@dataclass(frozen=True, slots=True)
class Response:
    """What a successful call returns. Never constructed for a failed one."""

    text: str
    parsed: Any
    call: LLMCall


@dataclass
class _Budget:
    """GW-20. A budget that can be exceeded silently is not a budget."""

    cap_usd: float
    spent_usd: float = 0.0
    calls: list[LLMCall] = field(default_factory=list)

    def charge(self, call: LLMCall) -> None:
        if self.spent_usd + call.cost_usd > self.cap_usd:
            raise BudgetExceededError(
                f"run budget ${self.cap_usd:.2f} exceeded: ${self.spent_usd:.4f} spent, "
                f"this call ${call.cost_usd:.4f}. ⚠ At k_cov x k_stab the call count "
                f"multiplies, so overspend arrives faster than intuition suggests"
            )
        self.spent_usd += call.cost_usd
        self.calls.append(call)


#: Transport-failure markers the provider surfaces. Everything absent from this
#: list is NOT retried — EH-14's default for an unclassified error (GW-17).
_RETRYABLE_HINTS = ("429", "500", "502", "503", "504", "timeout", "connection")


class Gateway:
    """The one chokepoint every LLM call passes through.

    `transport` is injected so the suite is hermetic — no test in this repo
    makes a live API call. The production transport lives in `transport.py`.
    """

    def __init__(
        self,
        config: Mapping[str, Any],
        *,
        transport: Callable[[dict], dict],
        alignment: Callable[[str, str], bool] | None = None,
        log=None,
        max_attempts: int = 3,
    ) -> None:
        self._cfg = config
        self._transport = transport
        self._alignment = alignment
        self._log = log
        self._max_attempts = max_attempts
        self._budget = _Budget(cap_usd=float(config.get("llm.budget.usd_per_run")))

    # -- accounting (GW-18, GW-19) ------------------------------------------ #

    @property
    def spent_usd(self) -> float:
        return self._budget.spent_usd

    @property
    def calls(self) -> list[LLMCall]:
        """Every call this run made — the input to D-08's RunManifest (GW-16)."""
        return list(self._budget.calls)

    def _cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        cfg = self._cfg
        return (
            tokens_in / 1_000_000 * float(cfg.get(f"llm.pricing.{model}.input_per_mtok"))
            + tokens_out / 1_000_000 * float(cfg.get(f"llm.pricing.{model}.output_per_mtok"))
        )

    # -- the call ------------------------------------------------------------ #

    def call(
        self,
        *,
        prompt_name: str,
        prompt_version: str,
        tier: Tier,
        payload: dict,
        max_tokens: int,
        run_id: str,
        schema: Callable[[str], Any] | None = None,
        ticker: str | None = None,
        probe: str | None = None,
    ) -> Response:
        """Send one prompt and return a CHECKED response.

        Raises on drift, truncation, refusal, schema failure and budget. Never
        returns a partial (GW-22).
        """
        if not prompt_name or not prompt_version:
            raise ValueError("prompt_name and prompt_version are required — there is "
                             "no unversioned call path (GW-14)")

        model_id = self._cfg.get(f"llm.{tier.value}.model_id")   # GW-5
        decoding = decoding_for(tier, self._cfg)                 # GW-8a/9a/9c
        call_id = uuid.uuid4().hex[:12]

        def record(outcome: Outcome, *, attempts=1, reasons=(), tin=0, tout=0,
                   elapsed=0, aligned=True, cost=0.0) -> LLMCall:
            return LLMCall(
                call_id=call_id, run_id=run_id, prompt_name=prompt_name,
                prompt_version=prompt_version, tier=tier.value, model_id=model_id,
                decoding=decoding, max_tokens=max_tokens, alignment_ok=aligned,
                attempts=attempts, retry_reasons=tuple(reasons), tokens_in=tin,
                tokens_out=tout, elapsed_ms=elapsed, outcome=outcome.value,
                ticker=ticker, probe=probe, cost_usd=cost,
            )

        # GW-12/13 — alignment BEFORE any call. Checking after would check nothing.
        if self._alignment is not None and not self._alignment(prompt_name, prompt_version):
            self._emit(record(Outcome.DRIFT_BLOCKED, aligned=False))
            raise DriftBlockedError(
                f"prompt {prompt_name}@{prompt_version} has drifted from its spec — "
                f"no call was made (INV-9, GW-12). A drifted prompt is an unversioned "
                f"change to the analytical method"
            )

        request = {
            "model": model_id, "max_tokens": max_tokens, "payload": payload,
            **({"effort": decoding.effort, "thinking": decoding.thinking_mode}
               if decoding.control == "effort" else {"temperature": decoding.temperature}),
        }

        attempts, reasons, started = 0, [], time.monotonic()
        while True:
            attempts += 1
            try:
                raw = self._transport(request)
                break
            except TransportError as exc:
                reasons.append(type(exc).__name__ + ":" + str(exc)[:60])
                retryable = exc.retryable and any(
                    h in str(exc).lower() for h in _RETRYABLE_HINTS
                )
                if not retryable or attempts >= self._max_attempts:
                    self._emit(record(Outcome.TRANSPORT_FAILED, attempts=attempts,
                                      reasons=reasons))
                    raise
                time.sleep(0)          # bounded + backed off (GW-17); 0 in tests
            except (TruncatedError, RefusedError, UnparseableError, DriftBlockedError) as exc:
                # GW-15 / EH-15: retry the request that got no real answer, never
                # the answer you disliked. Reaching here is the gateway's own bug.
                raise SemanticRetryError(
                    f"{type(exc).__name__} reached the retry loop — semantic failures "
                    f"are never retried (GW-15)"
                ) from exc

        elapsed = int((time.monotonic() - started) * 1000)
        tin, tout = int(raw.get("tokens_in", 0)), int(raw.get("tokens_out", 0))
        cost = self._cost(model_id, tin, tout)
        stop = raw.get("stop_reason")

        # GW-23 — a truncation is a FAILURE, not a short answer.
        if stop == "max_tokens":
            self._emit(record(Outcome.TRUNCATED, attempts=attempts, reasons=reasons,
                              tin=tin, tout=tout, elapsed=elapsed, cost=cost))
            raise TruncatedError(
                f"{prompt_name}@{prompt_version} hit max_tokens={max_tokens} — a "
                f"truncated response is a failure, not a short answer (GW-23). With "
                f"adaptive thinking the response budget is max_tokens MINUS thinking, "
                f"so this is caught rather than predicted (GW-7b)"
            )
        if stop == "refusal":
            self._emit(record(Outcome.REFUSED, attempts=attempts, reasons=reasons,
                              tin=tin, tout=tout, elapsed=elapsed, cost=cost))
            raise RefusedError(f"{prompt_name}@{prompt_version} was refused by the model")

        text = raw.get("text")
        if not text:
            # GW-22 — an empty body is the ABSENT narrative that produced incident two.
            self._emit(record(Outcome.UNPARSEABLE, attempts=attempts, reasons=reasons,
                              tin=tin, tout=tout, elapsed=elapsed, cost=cost))
            raise UnparseableError(
                f"{prompt_name}@{prompt_version} returned an empty response — an "
                f"absent narrative is a failure, never a default (GW-22)"
            )

        parsed = text
        if schema is not None:
            try:
                parsed = schema(text)
            except Exception as exc:
                self._emit(record(Outcome.UNPARSEABLE, attempts=attempts, reasons=reasons,
                                  tin=tin, tout=tout, elapsed=elapsed, cost=cost))
                raise UnparseableError(
                    f"{prompt_name}@{prompt_version} did not match its declared schema "
                    f"({exc}) — the gateway parses and raises; what the content MEANS "
                    f"is D-01's (GW-3)"
                ) from exc

        call = record(Outcome.OK, attempts=attempts, reasons=reasons, tin=tin,
                      tout=tout, elapsed=elapsed, cost=cost)
        self._budget.charge(call)                                  # GW-20
        self._emit(call)
        return Response(text=text, parsed=parsed, call=call)

    def _emit(self, call: LLMCall) -> None:
        if self._log is not None:
            self._log.info("llm_call", **call.to_json_obj())
