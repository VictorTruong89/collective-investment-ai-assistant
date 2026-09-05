"""Composable quality rules — DE-12, ACCEPT / FLAG / REJECT (AC-7.60).

```
VALIDATION CLASSIFIES. IT NEVER MODIFIES.

A FLAG is stored WITH the row.
A REJECT is not stored at all, and is logged with its rule id.
Nothing is repaired, clipped, filled or coerced on the way through.
```

★ **The "never modifies" half is the load-bearing half**, and it is the one an
implementation erodes first — clipping an out-of-range value is one line and
looks like robustness. It is the same move as `fillna(0.0)` on a z-score
(**PD-1**): the row stops being wrong and starts being *plausibly* wrong, which
is strictly worse because nothing downstream can tell.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

ACCEPT, FLAG, REJECT = "ACCEPT", "FLAG", "REJECT"


@dataclass(frozen=True, slots=True)
class Rule:
    """One check. `predicate` returns a boolean Series: True means the rule FIRED.

    Phrased as "fired" rather than "passed" so a reader of a rule body cannot
    get the polarity backwards — `df["close_minor"] <= 0` reads as the problem
    it names, not as its negation.
    """

    rule_id: str                # "DQ-001"
    severity: str               # FLAG | REJECT
    description: str
    predicate: Callable[[pd.DataFrame], pd.Series]

    def __post_init__(self) -> None:
        if self.severity not in (FLAG, REJECT):
            raise ValueError(
                f"rule severity must be {FLAG} or {REJECT}, not {self.severity!r}. "
                f"ACCEPT is the absence of a firing rule, not a rule of its own"
            )


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """What validation decided. The INPUT frame is never among the outputs.

    `accepted` carries the FLAG findings in `quality_flags`; `rejected` carries
    the rows that were not stored, so a caller can count and log them. **Neither
    contains a value that validation changed** — there is no such value.
    """

    accepted: pd.DataFrame
    rejected: pd.DataFrame
    findings: pd.DataFrame

    @property
    def verdict(self) -> str:
        if len(self.rejected):
            return REJECT
        if len(self.findings):
            return FLAG
        return ACCEPT


class RuleRegistry:
    """The composable set L4 §1.5 asks `ingest_validator.py` to become."""

    def __init__(self, rules=()) -> None:
        self._rules: list[Rule] = list(rules)

    def add(self, rule: Rule) -> "RuleRegistry":
        if any(r.rule_id == rule.rule_id for r in self._rules):
            raise ValueError(
                f"rule id {rule.rule_id!r} is already registered. Two rules under one "
                f"id makes a finding untraceable to the check that produced it"
            )
        self._rules.append(rule)
        return self

    @property
    def rules(self) -> tuple[Rule, ...]:
        # Sorted so the findings frame is deterministic regardless of the order
        # rules were registered in (INV-2, PD-20).
        return tuple(sorted(self._rules, key=lambda r: r.rule_id))
