"""★ THE SEAM — the one place in `src/` that calls the LLM gateway (ST-5, RA-44).

```
D-01 IS THE ONLY DOMAIN PERMITTED TO IMPORT THE GATEWAY, AND WITHIN D-01
THIS IS THE ONLY FILE THAT DOES.

That is narrower than ST-5 requires, and deliberately so: ST-5 is checked by
a grep over twelve domains, and this makes the same rule checkable by
reading one file.
```

Four guards run before anything leaves, and each is an acceptance criterion:

| Guard | Rule | AC |
|---|---|---|
| a hashed bundle, or refuse | RA-1, RA-2 | **AC-1.1** |
| alignment, before any call | RA-13, INV-9 | **AC-1.10** |
| a fresh context, every time | RA-12 | **AC-1.11** |
| a degraded response is never analysis | RA-29, RA-110 | **AC-1.27** |

⚠ **RA-130 is the one that reads backwards.** AC-1.27 says a degraded call is
never persisted; RA-111 says the record must distinguish *"did not run"* from
*"ran and failed"*. **Record that it failed; never record what it produced.**
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone

from src.fundamental.bundle.models import EvidenceBundle
from src.fundamental.contracts.analysis_run import AnalysisRun, AnalysisRunLog
from src.fundamental.errors import (
    BundleNotPinnedError,
    ConversationalStateError,
    DegradedCallError,
)
from src.fundamental.prompts.envelope import compose_prompt
from src.fundamental.prompts.registry import PromptBlock, PromptRegistry
from src.shared.errors import LLMError
from src.shared.llm.gateway import Gateway, Tier

#: ★ INV-8 / §6: **both** of D-01's call kinds sit on the deep tier. Extraction
#: is nominally "extraction" but is low-frequency (the filing-aware cache) and
#: quality-critical — moat and profile feed the whole stack. **Tier is a property
#: of the call site, declared statically** (GW-4), so it is a constant here and
#: never chosen from data.
TIER = Tier.DEEP

#: GW-7a — `max_tokens` per call site, never one global value. ⚠ *A single global
#: value either starves the cheap calls or truncates the deep ones, and only the
#: second is fatal.* Values reused from `settings.yaml` (QI-4, closed).
#: ⚠⚠ Raised 8000 -> 20000 for extraction on 2026-09-07, from a MEASURED
#: truncation: E-01 over MU's 10-Q hit the 8000 cap and GW-23 correctly refused
#: the half answer. ★ With adaptive thinking the response budget is max_tokens
#: MINUS thinking (GW-7b), so a table of ~20 items each carrying a verbatim
#: quote does not fit what 8000 leaves. Judgement is unchanged — it was not
#: measured, and guessing a second number from one observation is how a limit
#: becomes folklore.
#:
#: ✏ Raised again 20000 -> 32000, then MEASURED FIVE TIMES on one bundle:
#:     14,165 · 16,000* · 16,000* · 13,243 · 32,000   (*a clamp, see below)
#:
#: ⚠⚠ Two separate causes were tangled here, and the first hid the second:
#:   1. `anthropic_transport` silently clamped `max_tokens` to 16,000, so the
#:      20,000 and 32,000 ceilings were never in force — and `GW-23` reported
#:      "hit max_tokens=32000", a number that was never sent. Fixed.
#:   2. ★ With the clamp gone, spend still ranged 13,243 -> 32,000 on the SAME
#:      input with no code change between runs. Adaptive thinking's cost is
#:      genuinely variable, and the tail is more than 2x the median.
#:
#: ⚠ So a ceiling chosen from one observation is a coin flip — but raising it
#: is not obviously the fix either, because thinking expands into the budget it
#: is given. The lever that actually bounds this is `llm.deep.effort`, not
#: max_tokens. ⬜ Unresolved: see L3 §2.5 and DX-27.
#:
#: ✏ **LOWERED 32000 -> 12000, 2026-09-08 (`DX-30`).** ⚠⚠ Not a performance
#: tweak — an economic one. Every truncation ever recorded returned a
#: **2-character payload**: adaptive thinking consumes the whole budget and the
#: tool call is never emitted, so a truncated run yields **zero items at full
#: price**. There is no partial answer to preserve by being generous.
#:
#: ★★ So the ceiling should sit just above the largest OBSERVED success, not at
#: a comfortable round number. Measured successes: MU 2,595 / 7,119 / 9,865 and
#: the AMD slice 7,401. 12,000 clears every one of them, and turns a failure
#: from ~$1.18 into ~$0.68.
#:
#: ⚠ The trade, stated: only **21 % headroom** over MU's largest success. A
#: filing needing 12,500 now fails where 32,000 would have served — but it would
#: have served at DOUBLE the price of the failure, and `GW-23` refuses the
#: half-answer either way. ★ Raise it only on evidence of a run that needed more
#: AND completed.
#:
#: ✏ **Raised 12,000 → 20,000 for extraction, 2026-09-11 (`DX-69`).** The
#: post-envelope `E-02` re-record hit 12,000 **exactly** and was refused.
#:
#: ⚠⚠ **The paragraph above is right and must not be read as overturned: a
#: larger cap makes a FAILURE more expensive, not a success.** A truncated run
#: produces the whole budget, so `E-02` failing now costs ~$0.87 instead of
#: ~$0.68. Output that is never produced is never billed, so a *successful*
#: call is unaffected — ★ but "an unused cap is free" is true only of the runs
#: that succeed, and it is the failures this number governs.
#:
#: ★★ What justifies it is the headroom census this constant had never had
#: (`DX-69`). The cap is shared per KIND while the margin is per BLOCK:
#: measured pre-envelope, MU `E-01` sat at 20.0 % headroom, AMD `E-01` at
#: 36.8 %, and **`E-02` at 12.4 %** — the tightest call in the project's
#: history, and the one nobody had looked at.
#:
#: ⚠⚠ **The retry did NOT need more than 12,000, and that is the finding.**
#: Same prompt, byte for byte — **76,195 input tokens on both runs** — and the
#: only variable changed was this constant:
#:
#:     cap 12,000 → 12,000 out, TRUNCATED, $0.6810 wasted
#:     cap 20,000 →  8,479 out, 38 items verified, $0.5929
#:
#: ★★★ So `E-02`'s requirement is **variable and straddles 12,000**, not fixed
#: above it. ⚠ Two samples with n=1 per arm and a stochastic generator: the
#: cap plausibly changes the adaptive-thinking split (the note at the top of
#: this comment), but **that mechanism is not established here** and the trace
#: does not record the thinking/response breakdown to settle it.
#:
#: ★ What IS established is enough to act on: a block whose draw sometimes
#: exceeds its ceiling fails ~$0.68 at a time and yields nothing, and a margin
#: of 12.4 % cannot absorb variance it was never measured against. **This cap
#: is raised against VARIANCE, not against a larger fixed requirement** — and
#: the rule above ("only on evidence of a run that needed more AND completed")
#: is not met by this change. Recorded as such so the precedent is not
#: mistaken for the rule.
MAX_TOKENS = {"extraction": 20000, "judgement": 16000}


@dataclass(frozen=True, slots=True)
class CallResult:
    """A SUCCESSFUL call. ★ Never constructed for a failed one.

    That is GW-22 expressed as a type: there is no `CallResult` carrying an
    error field, so a caller cannot forget to check one. **Both real incidents in
    this repo are a consumer treating a degraded result as usable.**
    """

    text: str
    parsed: object
    run: AnalysisRun


class AnalysisGateway:
    """D-01's call discipline, wrapped around D-00's transport.

    ⚠ **It is not a second gateway.** D-00 owns transport, retry, budget and the
    decoding controls (GW-1…GW-23); this owns the four guards above, which are
    D-01's because they are about *what may be asked*, and §1.2 forbids D-00 to
    hold any of them.
    """

    def __init__(self, gateway: Gateway, registry: PromptRegistry, *,
                 log: AnalysisRunLog | None = None, seed: int = 0) -> None:
        self._gateway = gateway
        self._registry = registry
        self.log = log or AnalysisRunLog()
        #: RA-17's permutation source. Seeded so a run is reproducible (INV-2)
        #: while the permutation still varies across calls within it — ⚠ *option
        #: order is randomised PER CALL, not per stage*: a stage-level
        #: permutation would correlate the position bias across the very
        #: dimensions RM-2 compares.
        self._rng = random.Random(seed)

    # -- the call ------------------------------------------------------------ #

    def call(self, *, prompt_name: str, prompt_version: str, bundle, run_id: str,
             step: str | None = None, schema=None, extra_context=None,
             evidence_rotation: int = 0) -> CallResult:
        """Send one prompt against one bundle. Raises rather than degrading.

        `extra_context` exists **only to be refused** — see `_refuse_ambient`.
        """
        block = self._require_pinned_and_aligned(prompt_name, prompt_version, bundle)
        self._refuse_ambient(extra_context)
        self._require_matching_view(block, bundle)

        permutation = self._permute(block)
        payload = self._compose(block, bundle, permutation,
                                evidence_rotation=evidence_rotation)
        started = datetime.now(timezone.utc)

        try:
            response = self._gateway.call(
                prompt_name=block.name, prompt_version=block.version, tier=TIER,
                payload=payload, max_tokens=MAX_TOKENS[block.kind], run_id=run_id,
                schema=schema, ticker=bundle.ticker,
            )
        except LLMError as exc:
            # ★ RA-130 — the FAILURE is recorded; the analysis is not.
            self.log.append(_failed_run(
                bundle=bundle, block=block, run_id=run_id, started=started,
                permutation=permutation, exc=exc, step=step,
                model_id=self._model_id(),
            ))
            raise DegradedCallError(block.name, _outcome_of(exc), str(exc)) from exc

        run = AnalysisRun(
            run_id=run_id, ticker=bundle.ticker, as_of=bundle.as_of,
            bundle_hash=bundle.bundle_hash, prompt_name=block.name,
            prompt_version=block.version, model_id=response.call.model_id,
            # ★ RA-129 — CT-0.1's object, transported WHOLE and byte-identical.
            # Flattening it here would reintroduce, one contract downstream,
            # exactly the defect CT-0.1 was reshaped to remove (GW-9).
            decoding=response.call.decoding.to_json_obj(),
            option_permutation=permutation,
            started_at=started, tokens_in=response.call.tokens_in,
            tokens_out=response.call.tokens_out, attempts=response.call.attempts,
            outcome=response.call.outcome, call_id=response.call.call_id, step=step,
        )
        self.log.append(run)          # RA-111 — before the next step begins
        return CallResult(text=response.text, parsed=response.parsed, run=run)

    # -- the four guards ------------------------------------------------------ #

    def _require_pinned_and_aligned(self, name: str, version: str,
                                    bundle) -> PromptBlock:
        """AC-1.1 + AC-1.10, in that order.

        ⚠ **Pinning is checked first.** An unpinned call that fails on alignment
        would look like a drift problem, and the reader would fix the prompt.
        """
        if not isinstance(bundle, EvidenceBundle):
            raise BundleNotPinnedError(
                f"call to {name!r} with {type(bundle).__name__} instead of an "
                f"EvidenceBundle"
            )
        if not bundle.bundle_hash.startswith("sha256:"):
            raise BundleNotPinnedError(f"call to {name!r} with an unhashed bundle")
        return self._registry.check(name, version)      # raises PromptDriftError

    @staticmethod
    def _refuse_ambient(extra_context) -> None:
        """AC-1.11 / RA-12 — no conversational state, no ambient retrieval.

        ★ The parameter exists **in order to be refused.** A seam with no such
        argument is silently satisfied by a caller who concatenates history into
        the payload instead; one that names and rejects it puts the rule where
        someone reaches for it — the same reasoning as D-05's `refuse_to_block`.
        """
        if extra_context:
            raise ConversationalStateError(
                f"extra_context of {len(extra_context)} item(s) was supplied "
                f"alongside the bundle"
            )

    @staticmethod
    def _require_matching_view(block: PromptBlock, bundle: EvidenceBundle) -> None:
        """RA-14 — a blind block gets a redacted bundle, and only that.

        ⚠ Checked both ways. A blind prompt handed the full bundle has lost the
        anchor-stripping; a full-view prompt handed a redacted one is reasoning
        about a valuation it cannot see and would say so confidently.
        """
        if block.view != bundle.view:
            raise BundleNotPinnedError(
                f"prompt {block.name!r} declares view={block.view!r} and was handed a "
                f"bundle with view={bundle.view!r}. RA-14's staging is a property of "
                f"the pair, not of either half"
            )

    # -- composition ---------------------------------------------------------- #

    def _permute(self, block: PromptBlock) -> tuple[str, ...]:
        """RA-17 — enumerated options are order-randomised per call, and recorded."""
        options = list(block.options)
        self._rng.shuffle(options)
        return tuple(options)

    @staticmethod
    def _compose(block: PromptBlock, bundle: EvidenceBundle,
                 permutation: tuple[str, ...], *,
                 evidence_rotation: int = 0) -> dict:
        """Build the payload — the bundle and nothing else (RA-1).

        ★ Rebuilt from scratch on every call. There is no accumulating context
        object to forget to clear, which is RA-12 made structural rather than
        procedural.

        ⚠ **`evidence_rotation` is RM-1's second perturbation, and it belongs
        HERE.** The bundle sorts its parts so RA-4's hash is order-independent,
        so rotating them on the bundle is undone before it is returned. Rotating
        the **payload** changes what the model reads while leaving `bundle_hash`
        identical — which is what makes the `k` runs comparable (RA-2).
        """
        obj = bundle.to_json_obj()
        parts = obj.get("parts") or []
        if evidence_rotation and parts:
            shift = evidence_rotation % len(parts)
            obj = {**obj, "parts": parts[shift:] + parts[:shift]}
        return {
            # ⚠⚠ `DX-67` — this sent `block.text` ALONE for every call this
            # project ever made. §3.0/§4.0 say the shared envelope
            # (`S-1`…`S-6`, plus `S-7` in Stage A) is *"composed into every
            # E-block / every J-block"*, and the composition did not exist.
            # ★ `S-3` is the evidence and citation contract — the rule that
            #   makes a factual claim checkable — so its absence is the part
            #   that mattered, not the missing words as such.
            "prompt": compose_prompt(block, stage_a=(block.view == "blind")),
            "options": list(permutation),
            "bundle": obj,
        }

    def _model_id(self) -> str:
        return str(self._gateway._cfg.get(f"llm.{TIER.value}.model_id"))


def _outcome_of(exc: LLMError) -> str:
    """Map a gateway error onto CT-0.1's outcome enum. ★ Never `partial`."""
    return {
        "DriftBlockedError": "drift_blocked",
        "TruncatedError": "truncated",
        "UnparseableError": "unparseable",
        "RefusedError": "refused",
        "TransportError": "transport_failed",
    }.get(type(exc).__name__, "transport_failed")


def _failed_run(*, bundle, block, run_id, started, permutation, exc, step,
                model_id) -> AnalysisRun:
    """RA-130's record. ⚠ It carries no output — only that a call was made."""
    return AnalysisRun(
        run_id=run_id, ticker=bundle.ticker, as_of=bundle.as_of,
        bundle_hash=bundle.bundle_hash, prompt_name=block.name,
        prompt_version=block.version, model_id=model_id,
        decoding={"control": "effort", "effort": None, "temperature": None,
                  "thinking_mode": None, "unresolved": True},
        option_permutation=permutation, started_at=started,
        tokens_in=0, tokens_out=0, attempts=getattr(exc, "attempts", 1),
        outcome=_outcome_of(exc), step=step, detail=type(exc).__name__,
    )


# --------------------------------------------------------------------------- #
# ★★ Constructing the gateway — **it lives HERE and nowhere else.**
#
# ⚠ *Added 2026-08-26.* Orchestration tried to build one so it could inject it,
# and nine architecture tests said no. The instinct was reasonable — the shim
# injects every other dependency — but **ST-5 is not about who owns the wiring,
# it is about who can reach the model**: a shim that can build a gateway can
# make a call. AC-1.38 then narrows it further, to exactly one file inside D-01,
# so that the rule is checkable by reading rather than by grepping twelve
# domains. That file is this one.
# --------------------------------------------------------------------------- #

#: INV-8 puts thesis authoring in the **deep tier**. ⚠ Opus 5 caps thinking and
#: response together under `max_tokens`, so the transport owns that headroom —
#: a call that truncates mid-answer loses the verdict, not just the prose.
THESIS_MODEL = "claude-opus-5"

#: ★ A per-RUN ceiling, not per-call. Three authoring passes over a real bundle
#: measured $1.09 on 2026-08-25; this sits well above a genuine run so nothing
#: is truncated, and far below anything that could surprise.
BUDGET_USD = 8.00

_PRICING = {"input_per_mtok": 15.0, "output_per_mtok": 75.0}


def build_gateway(*, model: str = THESIS_MODEL, budget_usd: float = BUDGET_USD):
    """An `AnalysisGateway` on the deep tier, or raise if no key is configured.

    ⚠ Raises rather than returning `None`: *"no API key"* and *"the model
    declined"* are different states, and a caller that cannot tell them apart
    reports a missing credential as an absent thesis (P5).
    """
    import os

    from src.fundamental.errors import ResearchError
    from src.fundamental.prompts.blocks.j_blocks import production_registry
    from src.shared.llm.anthropic_transport import MappingConfig, make_transport
    from src.shared.llm.claude_code_transport import (
        CLAUDE_CODE,
        make_claude_code_transport,
        selected_transport,
    )
    from src.shared.llm.gateway import Gateway
    from src.shared.secrets import Secret

    # ★ GW-24 — `claude_code` (subscription) unless CIA_LLM_TRANSPORT=anthropic_api.
    #   The API key is reserved for the real daily runs (`CLAUDE.md`, 2026-10-01).
    on_subscription = selected_transport() == CLAUDE_CODE
    key = None if on_subscription else os.environ.get("ANTHROPIC_API_KEY")
    if not on_subscription and not key:
        raise ResearchError(
            "ANTHROPIC_API_KEY is not set, so D-01 cannot author. ★ This is a "
            "configuration fault and it is reported as one — an absent thesis "
            "would read as a model that declined to reach a verdict (P5)")

    # ★ GW-27 — a subscription call costs $0 of API money, so it is priced at
    #   0 and the budget counts API dollars only; the CLI's list price is kept
    #   on each response as `notional_usd`.
    price = 0.0 if on_subscription else 1.0
    config = MappingConfig({
        "llm.deep.model_id": model,
        "llm.deep.effort": "medium",
        "llm.deep.thinking_mode": "adaptive",
        "llm.budget.usd_per_run": budget_usd,
        f"llm.pricing.{model}.input_per_mtok": _PRICING["input_per_mtok"] * price,
        f"llm.pricing.{model}.output_per_mtok": _PRICING["output_per_mtok"] * price,
    })
    transport = (make_claude_code_transport() if on_subscription
                 else make_transport(Secret("ANTHROPIC_API_KEY", key)))
    return AnalysisGateway(Gateway(config, transport=transport),
                           production_registry())
