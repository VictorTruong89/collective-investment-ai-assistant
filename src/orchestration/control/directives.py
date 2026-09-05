"""F8 `CT-8.4`–`CT-8.6` — one line of human English, safely.

★★ **The safeguard is the CLOSED effect vocabulary plus a refusal path — not the
model tier** (`D2`). An unmapped directive applies **nothing** and is logged.

⚠ `D2` also settles the tier: mapping one line onto a bounded, known set is a
classification task, so the cheap tier is right. **A larger model guessing
plausibly at an ambiguous directive is MORE dangerous than a small one refusing**,
because its guess reads as competent.

⚠⚠ **`AC-8.16`: the raw text never reaches a prompt.** Only the typed effects do.
Otherwise a directive becomes an untyped instruction channel into the analysis —
prompt injection with the manager as the vector.

⏳ **`CT-8.5`'s initial vocabulary is deliberately EMPTY** (`D6`, `F8` `Q6`):
Victor deferred it to E2E validation so it describes effects the system actually
has. ⚠ `QR-23` made E2E a precondition for resuming trading, so this is on the
critical path — see `L3` §7.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from src.orchestration.control.models import DirectiveState


class UnregisteredEffect(Exception):
    """`AC-8.12` — ⚠ the interpreter may emit only REGISTERED effects."""


class NotConfirmed(Exception):
    """`AC-8.15` — nothing takes effect without confirmation."""


@dataclass(frozen=True, slots=True)
class EffectVocabulary:
    """`CT-8.5` — closed, registered, versioned.

    ⏳ Ships EMPTY by `D6`. ★ An empty closed set is not a stub: it means every
    directive is currently unmappable and applies nothing, which is the correct
    behaviour before the effects exist.
    """

    version: str
    effects: frozenset[str] = frozenset()

    def check(self, effect: str) -> None:
        if effect not in self.effects:
            raise UnregisteredEffect(
                f"{effect!r} is not in effect vocabulary {self.version} "
                f"({sorted(self.effects) or 'EMPTY — F8 Q6, defined at E2E'}). "
                "⚠ AC-8.12: the interpreter emits only registered effects.")


@dataclass(frozen=True, slots=True)
class Directive:
    """`CT-8.4` — typed, and **frozen at apply time** (`AC-8.13`)."""

    directive_id: str
    raw_text: str
    effects: tuple[tuple[str, object], ...]
    vocabulary_version: str
    state: DirectiveState
    window_from: str
    window_to: str
    interpreted_at: str

    def applies_on(self, day: str) -> bool:
        """`AC-8.18` — the window is honoured and expiry is automatic."""
        return self.state == "ACTIVE" and self.window_from <= day <= self.window_to

    def to_prompt_payload(self) -> dict:
        """⚠⚠ `AC-8.16` — typed effects ONLY. The raw text is not included.

        ★ Including it would turn a directive into an untyped instruction channel
        into the analysis: prompt injection with the manager as the vector.
        """
        return {"effects": dict(self.effects),
                "vocabulary_version": self.vocabulary_version}


@dataclass(frozen=True, slots=True)
class UnmappableDirective:
    """`CT-8.6` — append-only. ⚠ `AC-8.19`: reviewable, because the misses are
    how the vocabulary learns what it is missing."""

    directive_id: str
    raw_text: str
    at: str
    reason: str


def interpret(raw_text: str, *, vocabulary: EffectVocabulary,
              map_fn: Callable[[str], Mapping[str, object]],
              directive_id: str, at: str,
              window_from: str, window_to: str) -> Directive | UnmappableDirective:
    """Map one line onto the closed set, or refuse. ⚠ Returns a **DRAFT**."""
    try:
        proposed = dict(map_fn(raw_text))
    except Exception as exc:                                  # noqa: BLE001
        return UnmappableDirective(directive_id, raw_text, at, f"interpreter error: {exc}")
    if not proposed:
        return UnmappableDirective(directive_id, raw_text, at,
                                   "mapped to no registered effect")
    for name in proposed:
        try:
            vocabulary.check(name)
        except UnregisteredEffect as exc:
            # ⚠ AC-8.14 — an unmappable directive applies NOTHING. Not partially.
            return UnmappableDirective(directive_id, raw_text, at, str(exc))
    return Directive(directive_id=directive_id, raw_text=raw_text,
                     effects=tuple(sorted(proposed.items())),
                     vocabulary_version=vocabulary.version, state="DRAFT",
                     window_from=window_from, window_to=window_to,
                     interpreted_at=at)


def confirm(d: Directive) -> Directive:
    """`AC-8.15` — a DRAFT becomes ACTIVE only by explicit confirmation."""
    if d.state != "DRAFT":
        raise NotConfirmed(f"only a DRAFT may be confirmed; this is {d.state}")
    return Directive(**{**{f: getattr(d, f) for f in
                          ("directive_id", "raw_text", "effects",
                           "vocabulary_version", "window_from", "window_to",
                           "interpreted_at")}, "state": "ACTIVE"})


def effects_for_replay(d: Directive) -> tuple[tuple[str, object], ...]:
    """`AC-8.13` — ⚠⚠ replay uses the FROZEN effects; it never re-interprets.

    ★ Re-interpreting would make a replay depend on the interpreter's current
    behaviour, so a model change would silently alter history — and `F2`'s replay
    exists precisely to hold history fixed.
    """
    if d.state != "ACTIVE":
        raise NotConfirmed(f"only an ACTIVE directive has effects; this is {d.state}")
    return d.effects
