"""F5 `CT-5.4` — Tier-A arm comparison, consumed by `F7a`.

★★ **`pre_registered_rule` must exist BEFORE the comparison runs** (`PG-5.1`,
`AC-5.14`). *"A threshold chosen after seeing the data is a rationalisation, not
a measurement."* The timestamp ordering is enforced, not trusted.

⚠ **Tier A only.** A Tier-A result answers *"does it behave like reasoning?"*,
never *"did it make better decisions?"* — mixing them is `AC-5.4`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


class PreRegistrationError(Exception):
    """`AC-5.14` — the kill rule was missing, empty, or written after the fact."""


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    arm_a: str
    arm_b: str
    metric: str
    value_a: float
    value_b: float
    n_a: int
    n_b: int
    pre_registered_rule: str
    pre_registered_at: str
    computed_at: str
    verdict: str                # PASS | FAIL | INSUFFICIENT
    tier: str = "A"

    def __post_init__(self) -> None:
        if not self.pre_registered_rule.strip():
            raise PreRegistrationError(
                "pre_registered_rule is required (PG-5.1, AC-5.14) — state the "
                "result that would DELETE the capability before running the test"
            )
        if _parse(self.pre_registered_at) >= _parse(self.computed_at):
            raise PreRegistrationError(
                f"the rule was registered at {self.pre_registered_at}, not before "
                f"the comparison at {self.computed_at}. ⚠ A threshold chosen after "
                "seeing the data is a rationalisation, not a measurement."
            )
        if self.tier != "A":
            raise ValueError("a ComparisonResult is Tier A (PG-5.1)")


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def compare(*, arm_a: str, arm_b: str, metric: str, value_a: float, value_b: float,
            n_a: int, n_b: int, pre_registered_rule: str, pre_registered_at: str,
            computed_at: str, minimum_n: int = 20) -> ComparisonResult:
    """⚠ INSUFFICIENT is a verdict, not a failure — and never a silent pass."""
    if min(n_a, n_b) < minimum_n:
        verdict = "INSUFFICIENT"
    else:
        verdict = "PASS" if value_b > value_a else "FAIL"
    return ComparisonResult(arm_a=arm_a, arm_b=arm_b, metric=metric,
                            value_a=value_a, value_b=value_b, n_a=n_a, n_b=n_b,
                            pre_registered_rule=pre_registered_rule,
                            pre_registered_at=pre_registered_at,
                            computed_at=computed_at, verdict=verdict)
