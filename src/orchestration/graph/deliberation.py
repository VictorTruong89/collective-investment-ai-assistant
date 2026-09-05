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

from collections.abc import Callable
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
    terminated: Literal["CONVERGED", "BUDGET_EXHAUSTED", "ESCALATED"]

    @property
    def changed(self) -> bool:
        return self.pre != self.post


def is_material(value: float, threshold: float) -> bool:
    """`D2` — a declared threshold, evaluated deterministically."""
    return value > threshold


def deliberate(*, decision_id: str, pre: object,
               challenge: Message,
               respond: Callable[[Message, object], tuple[object, str]],
               turn_budget: int = TURN_BUDGET) -> Deliberation:
    """Run one bounded exchange. ⚠ **Terminates by construction** (`T6`).

    `respond` returns `(revised_output, disposition)` where disposition is
    `"CONVERGED"` or `"ESCALATED"`. ⛔ It may not return `"BLOCK"` (`D3`).
    """
    if not is_material(challenge.metric_value or 0.0, challenge.threshold or 0.0):
        # ⚠ Below the declared trigger there is no deliberation at all — and the
        # PG-5.2 delta is still written by the caller, with changed=False.
        return Deliberation(decision_id, (), pre, pre, 0, "CONVERGED")

    post, disposition = respond(challenge, pre)
    if disposition == "BLOCK":
        raise BlockAttempted(
            "deliberation returned BLOCK. ⛔ D3/P4 — D-12's gate algebra already "
            "blocks; a second gating mechanism is two answers to one question. "
            "Record an objection instead.")
    if disposition not in ("CONVERGED", "ESCALATED"):
        raise ValueError(f"unknown disposition {disposition!r}")

    msgs = (challenge, Message("RESPONSE", challenge.to_domain,
                               challenge.from_domain, "responded"))
    turns = min(2, turn_budget)
    return Deliberation(decision_id, msgs, pre, post, turns, disposition)
