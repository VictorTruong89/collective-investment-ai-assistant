"""Fixture ports for the F1 contract harness.

⚠ These live in tests/ ON PURPOSE. F1 §2 makes the semantics of any particular
port a NON-GOAL — real ports (PricePort, ThesisSourcePort, ...) arrive with
their own specs. What F1 owns is the MECHANISM, and a fixture port exercises
the mechanism completely.
"""

from __future__ import annotations

from typing import Mapping, Protocol, runtime_checkable

from src.shared.registry import Registry


@runtime_checkable
class GreeterPort(Protocol):
    def greet(self, name: str) -> str: ...


@runtime_checkable
class DoublerPort(Protocol):
    def double(self, value: int) -> int: ...


class PoliteGreeter:
    def greet(self, name: str) -> str:
        return f"Good day, {name}"


class TerseGreeter:
    def greet(self, name: str) -> str:
        return name


class LeakyGreeter:
    """⚠ Deliberately violates AC-1.7 — used to prove the suite CATCHES it."""

    def __init__(self) -> None:
        self._last = ""

    def greet(self, name: str) -> str:
        out = f"{self._last}{name}"
        self._last = name
        return out


class WarmupGreeter:
    """⚠ Leaks only on the FIRST call — the class AC-1.7's fresh-instance clause exists for.

    A check that compared two calls on the SAME warm instance would see agreement
    and pass. Only comparing against a genuinely fresh instance exposes it.
    """

    def __init__(self) -> None:
        self._warm = False

    def greet(self, name: str) -> str:
        if not self._warm:
            self._warm = True
            return "<cold>"
        return name


class IntDoubler:
    def double(self, value: int) -> int:
        return value * 2


class ShiftDoubler:
    def double(self, value: int) -> int:
        return value << 1


def build_registry() -> Registry:
    r = Registry()
    r.register("greeter", "polite", PoliteGreeter, version="1.0.0")
    r.register("greeter", "terse", TerseGreeter, version="0.2.0", experimental=True)
    r.register("doubler", "mul", IntDoubler, version="1.0.0")
    r.register("doubler", "shift", ShiftDoubler, version="1.1.0")
    return r


PORT_TYPES: Mapping[str, type] = {"greeter": GreeterPort, "doubler": DoublerPort}
