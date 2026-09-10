"""F6b — typed deliberation. `MS-7.2`. ⚠ Gated on `F7a` (`PG-5.1`).

★★ **`D4`: deliberation runs BEFORE D-12 composes.** `PG-6` makes the verdict
algebra *"a bounded meet-semilattice… a structural guarantee, not a runtime
check"*, and agent-assisted combination is *"advisory alongside, never
replacing"*. Running after composition would revise a composed verdict — the
replacement `PG-6` forbids. ★ It also keeps `PG-5.2`'s arms clean: `pre` is the
seat's own output, `post` is its output after deliberation, and D-12 composes
deterministically from whichever it is handed.

★★ **`D5`: only Risk initiates.** `INV-014`/`ST-9` — D-01 and D-03 must not see
each other's in-progress work. Risk consumes both analysts' **published** outputs,
so a Risk challenge crosses nothing; a Research challenge to Quant would be a
firewall crossing, and `PG-7` says the same from the other side.

⛔ **`D3`: no `BLOCK`.** D-12's gate algebra already blocks (`P4`). A challenge
produces a **recorded objection**; if it should stop a recommendation, that is a
gate, and gates live in D-12.

⚠ **`QR-14`**: this is the ONLY directory permitted to import an orchestration
framework (`F2` `AC-2.10`). None is imported today.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

MessageKind = Literal["CHALLENGE", "RESPONSE", "OBJECTION_RECORDED"]

#: `D1` — one challenge, one response. ⚠ `max_turns=1` is request-response and
#: cannot show revision; unbounded makes `T7`'s cost unbounded and gives `PG-3`'s
#: deliberation theatre room to accumulate transcript without moving a position.
#: ★ `T6` is what raises this, not intuition.
TURN_BUDGET = 2

#: `D5` — the only seat that may initiate, and the firewall is why.
INITIATOR_DOMAIN = "risk"


class FirewallCrossing(Exception):
    """`D5` / `INV-014` — a seat challenged one it may not see in progress."""


class BlockAttempted(Exception):
    """⛔ `D3` — deliberation may not block. D-12's algebra gates (`P4`)."""


class VerdictEscalated(Exception):
    """`AC-6b.6` / `P3` — ⚠⚠ a revision made a verdict MORE AGGRESSIVE.

    ★★★ The most consequential guard in `F6b`, and the reason is the ordering.
    Deliberation runs **before** D-12 (`D4`), so an escalated verdict arrives at
    composition looking like the seat's own honest output — and D-12 composes
    deterministically from whatever it is handed. ⚠ Nothing downstream catches
    it: `RP-7`/`DC-5` compare the COMPOSED verdict to the NOMINATED one, and
    after an escalation here both already carry it.
    """


#: `AC-6b.10` / §2.1 — what `F7a`'s band permits this capability to do.
ACTIVE = "ACTIVE"
ADVISORY_ONLY = "ADVISORY_ONLY"

#: ⚠⚠ **The default is the SAFE branch.** §2.1's `INSUFFICIENT` row exists so
#: that *absence of evidence defaults to the safe branch, not the convenient
#: one* — and `F7a` has never run, so nothing has yet earned `ACTIVE`.
#: ★ A default of `ACTIVE` would let an unmeasured capability alter verdicts
#: from its first day, which is precisely what `PG-5.1` gates against.
DEFAULT_MODE = ADVISORY_ONLY

#: `P3`'s order, restated for the revision guard. ★ Same three strings D-12 and
#: D-09 use; a fourth copy would be `P4`, but importing `src/decision/` from
#: orchestration would invert the dependency the whole layering rests on.
_CONSERVATISM = {"BUY": 0, "HOLD": 1, "SELL": 2}


def speaking_order(domains: Sequence[str], *, seed: int) -> tuple[str, ...]:
    """`AC-6b.9` — a randomised order that is REPRODUCIBLE from its seed.

    ⚠ `F7a`'s `T4` asks whether the outcome tracks speaking order. It can only
    ask that if the order actually varies — and `PG-9` requires the run to
    replay, so an unrecorded randomisation is not admissible. ★ Seeded, and the
    seed travels on the `Deliberation`.
    """
    order = list(domains)
    random.Random(seed).shuffle(order)
    return tuple(order)


def assert_not_escalated(pre: object, post: object) -> None:
    """`AC-6b.6` — ★ `P3` holds THROUGH revision.

    ⚠ Only ranks values it can rank. `pre`/`post` are not always verdicts — a
    seat may revise conviction or position size — and inventing an ordering for
    an unrankable value would either block legitimate revisions or, worse,
    silently approve one it did not understand.
    """
    # ⚠ `x in dict` RAISES TypeError on an unhashable value, and `pre`/`post`
    # are frequently dicts (a size or conviction payload). ★ Caught by
    # `test_ac_6b_6_a_non_verdict_payload_is_left_alone` — the guard against
    # escalation must never itself become a crash on a legitimate revision.
    if not (isinstance(pre, str) and isinstance(post, str)):
        return
    if (pre in _CONSERVATISM and post in _CONSERVATISM
            and _CONSERVATISM[post] < _CONSERVATISM[pre]):
        raise VerdictEscalated(
            f"deliberation revised {pre!r} to {post!r}, which is MORE "
            "AGGRESSIVE. ⚠ P3: verdicts gate, never upgrade. Deliberation "
            "runs before D-12 composes (D4), so this would reach the "
            "composer as the seat's own output and nothing downstream "
            "would catch it (AC-6b.6).")


@dataclass(frozen=True, slots=True)
class Message:
    kind: MessageKind
    from_domain: str
    to_domain: str
    text: str
    metric: str | None = None
    metric_value: float | None = None
    threshold: float | None = None

    def __post_init__(self) -> None:
        if self.kind == "CHALLENGE":
            if self.from_domain != INITIATOR_DOMAIN:
                raise FirewallCrossing(
                    f"{self.from_domain!r} may not challenge {self.to_domain!r}. "
                    "⚠ D5/INV-014: only Risk initiates, because it consumes both "
                    "analysts' PUBLISHED outputs and so crosses nothing. A "
                    "Research challenge to Quant would be a firewall crossing, and "
                    "their agreement would stop being independent evidence.")
            if self.metric is None or self.threshold is None:
                raise ValueError(
                    "D2 — a challenge states a DECLARED numeric trigger on a metric "
                    "the challenger owns. ⚠ Not a model judgement of materiality: "
                    "PG-9 requires a better answer than 'the model thought it "
                    "mattered', and a model deciding when to object is a model "
                    "deciding how often it speaks.")


@dataclass(frozen=True, slots=True)
class Deliberation:
    """The transcript plus the two `PG-5.2` arms."""

    decision_id: str
    messages: tuple[Message, ...]
    pre: object
    post: object
    turns_used: int
    terminated: Literal["CONVERGED", "BUDGET_EXHAUSTED", "ESCALATED", "INCOMPLETE"]
    #: `AC-6b.10` — what `F7a`'s band permits. ⚠ Defaults to the SAFE branch.
    mode: str = DEFAULT_MODE
    #: ★★ `PG-5.2` — what deliberation WOULD have produced, kept even when the
    #: mode forbids applying it. ⚠ An advisory capability that discarded its own
    #: proposal would make the Tier-B study impossible for exactly the period
    #: the capability is unproven, which is when the evidence is most needed.
    advisory_post: object = None
    #: `AC-6b.9` — recorded so `F7a`'s `T4` can ask whether order mattered.
    speaking_order: tuple[str, ...] = ()
    order_seed: int = 0
    #: `AC-6b.12` — ⚠ set when an agent failed. A truncated exchange must never
    #: read as a settled one.
    incomplete_reason: str | None = None

    @property
    def changed(self) -> bool:
        """⚠ Did the DECISION change — not *did the agent propose a change*.

        ★ In `ADVISORY_ONLY` the proposal is recorded in `advisory_post` and the
        decision is untouched, so `changed` is False. That is the honest answer
        for `T2`'s effect size: the capability altered nothing.
        """
        return self.pre != self.post


def is_material(value: float, threshold: float) -> bool:
    """`D2` — a declared threshold, evaluated deterministically."""
    return value > threshold


def deliberate(*, decision_id: str, pre: object,
               challenge: Message,
               respond: Callable[[Message, object], tuple[object, str]],
               turn_budget: int = TURN_BUDGET,
               mode: str = DEFAULT_MODE,
               order_seed: int = 0) -> Deliberation:
    """Run one bounded exchange. ⚠ **Terminates by construction** (`AC-6b.1`).

    `respond` returns `(revised_output, disposition)` where disposition is
    `"CONVERGED"` or `"ESCALATED"`. ⛔ It may not return `"BLOCK"` (`D3`).
    """
    order = speaking_order((challenge.from_domain, challenge.to_domain),
                           seed=order_seed)
    base = {"decision_id": decision_id, "mode": mode,
            "speaking_order": order, "order_seed": order_seed}

    if not is_material(challenge.metric_value or 0.0, challenge.threshold or 0.0):
        # ⚠ Below the declared trigger there is no deliberation at all — and
        # `PG-5.2`'s arm is STILL produced (`capability_delta`), because a
        # denominator that quietly excluded every case where deliberation
        # declined to speak would overstate its effect size.
        return Deliberation(messages=(), pre=pre, post=pre, turns_used=0,
                            terminated="CONVERGED", advisory_post=pre, **base)

    try:
        post, disposition = respond(challenge, pre)
    except BlockAttempted:
        raise
    except Exception as exc:
        # ⚠⚠ `AC-6b.12` — degrade, do not crash, and do not read as settled.
        # ★ The dangerous outcome is not the failure: it is a TRUNCATED exchange
        #   presented as a converged one, because `T6` would then count it as a
        #   convergence and the termination rate would be overstated.
        return Deliberation(
            messages=(challenge,), pre=pre, post=pre, turns_used=1,
            terminated="INCOMPLETE", advisory_post=pre,
            incomplete_reason=f"{type(exc).__name__}: {exc}", **base)

    if disposition == "BLOCK":
        raise BlockAttempted(
            "deliberation returned BLOCK. ⛔ D3/P4 — D-12's gate algebra already "
            "blocks; a second gating mechanism is two answers to one question. "
            "Record an objection instead.")
    if disposition not in ("CONVERGED", "ESCALATED"):
        raise ValueError(f"unknown disposition {disposition!r}")

    # ★★ `AC-6b.6` / `P3` — checked on what the agent PROPOSED, before the mode
    #    decides whether to apply it. ⚠ Checking only the applied value would
    #    let an escalation pass unnoticed in ADVISORY_ONLY and then arrive the
    #    day the band is promoted to ACTIVE.
    assert_not_escalated(pre, post)

    # `AC-6b.10` — ★ advisory mode renders the transcript and changes nothing.
    applied = post if mode == ACTIVE else pre

    msgs = (challenge, Message("RESPONSE", challenge.to_domain,
                               challenge.from_domain, "responded"))
    return Deliberation(messages=msgs, pre=pre, post=applied,
                        turns_used=min(2, turn_budget), terminated=disposition,
                        advisory_post=post, **base)


def capability_delta(d: Deliberation, *, is_valid: bool,
                     tokens: int = 0, span_bound: bool = False) -> dict:
    """`AC-6b.8` — the `CT-2.4` record, **always** (`PG-5.2`).

    ★★ This is the join that makes `F7a` executable: it is exactly the shape
    `challenges_from_deltas()` reads. ⚠ Written *including when `changed` is
    false* — the no-change cases are half the comparison, and dropping them
    biases the study invisibly (`F2` `AC-2.6`, `F7a` `AC-7a.6`).

    ⚠ `is_valid` says which of `T1`'s two arms this belongs to — a **valid**
    challenge or a deliberately false one. It is the caller's to declare
    because only the experiment knows, and `challenges_from_deltas` refuses a
    delta without it rather than defaulting.
    """
    return {
        "type": "CapabilityDelta",
        "decision_id": d.decision_id,
        "capability": "deliberation",
        "pre": {"verdict": d.pre} if isinstance(d.pre, str) else d.pre,
        "post": {"verdict": d.post} if isinstance(d.post, str) else d.post,
        "changed": d.changed,
        "is_valid": is_valid,
        "escalated": d.terminated == "ESCALATED",
        "incomplete": d.terminated == "INCOMPLETE",
        "turns_used": d.turns_used,
        # ⚠⚠ `DX-56` — what the capability COST. The first real `F7a` run
        # reported `T7 tokens/deliberation = 0.000` with n=46, reading as
        # *"deliberation is free"*, because nothing populated this field. The
        # true figure was $0.0177 per deliberation, known from the billing.
        # ★ `CT-7a.1`'s `T7` measures *"tokens and dollars per deliberation vs
        #   single-pass"* — it cannot, unless the delta carries them.
        "tokens": int(tokens),
        # ★ `D4` — `T5`'s denominator is SPAN-BOUND claims only, and it reports
        #   what fraction of challenges that covers. ⚠ `AB-2` is upstream `R7`,
        #   so today this is usually False and `T5` correctly declines.
        "span_bound": bool(span_bound),
        "order_index": (d.speaking_order.index(INITIATOR_DOMAIN)
                        if INITIATOR_DOMAIN in d.speaking_order else 0),
    }
