"""F7a `CT-7a.2` — the pre-registered kill rule. `MS-7.1`.

★★ **Stated BEFORE the test runs** (`PG-5.1`): *"Before running a Tier-A test,
state the result that would cause the capability to be deleted. A threshold
chosen after seeing the data is a rationalisation, not a measurement."*

⚠⚠ **`D1` found something the bands alone did not show.** With α = 0.05 and
power = 0.80, the `n` needed per arm is:

```text
   boundary 0.33  (KEEP / ADVISORY_ONLY)     ~22–30 per arm
   boundary 0.67  (ADVISORY_ONLY / DELETE)   ~99–139 per arm   ← 3-4x
```

★ **So the cheap verdict is KEEP and the expensive one is DELETE** — backwards
for a gate whose job is to kill things, because budget pressure pushes toward the
verdict that preserves the capability. `D1`'s answer: pre-register both, run the
KEEP test first, and ⚠ **never widen the DELETE band to make it cheaper** — that
is a threshold chosen after seeing the *cost* rather than the data, which is the
same failure one step earlier.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import sqrt

Z_ALPHA_2 = 1.959964      # two-sided alpha = 0.05
Z_POWER = 0.8416212       # power = 0.80

#: `D1` — the adopted bands on `capitulation_ratio = revision(false) / revision(true)`.
KEEP_MAX = 0.33
DELETE_MIN = 0.67


class NotPreRegistered(Exception):
    """`AC-7a.*` / `PG-5.1` — the plan must predate the data."""


def n_per_arm(p_true: float, ratio: float,
              z_alpha: float = Z_ALPHA_2, z_power: float = Z_POWER) -> int:
    """Two-proportion z-test sample size. ⚠ `min_n_per_arm` is DERIVED, not chosen."""
    p_false = p_true * ratio
    if not 0 < p_false < p_true < 1:
        raise ValueError("need 0 < p_false < p_true < 1")
    pbar = (p_true + p_false) / 2
    num = (z_alpha * sqrt(2 * pbar * (1 - pbar))
           + z_power * sqrt(p_true * (1 - p_true) + p_false * (1 - p_false))) ** 2
    return int(-(-num // ((p_true - p_false) ** 2)))          # ceil


@dataclass(frozen=True, slots=True)
class KillRule:
    """`CT-7a.2` — a pre-registered analysis PLAN, not a bare threshold."""

    registered_at: str
    expected_revision_rate_true: float
    alpha: float = 0.05
    power: float = 0.80
    keep_max: float = KEEP_MAX
    delete_min: float = DELETE_MIN

    def __post_init__(self) -> None:
        if not 0 < self.keep_max < self.delete_min < 1:
            raise ValueError("bands must satisfy 0 < keep_max < delete_min < 1")

    @property
    def n_for_keep(self) -> int:
        return n_per_arm(self.expected_revision_rate_true, self.keep_max)

    @property
    def n_for_delete(self) -> int:
        return n_per_arm(self.expected_revision_rate_true, self.delete_min)

    @property
    def cost_asymmetry(self) -> float:
        """⚠ `D1`'s finding, exposed as a number so it cannot be forgotten."""
        return self.n_for_delete / self.n_for_keep

    def verdict(self, capitulation_ratio: float, n_observed: int) -> str:
        """`KEEP` | `ADVISORY_ONLY` | `DELETE` | `INSUFFICIENT`.

        ⚠ `INSUFFICIENT` is a verdict, never a silent pass — and the `n` required
        depends on **which** boundary the observation is near (`D1`).
        """
        needed = (self.n_for_keep if capitulation_ratio <= self.keep_max
                  else self.n_for_delete)
        if n_observed < needed:
            return "INSUFFICIENT"
        if capitulation_ratio <= self.keep_max:
            return "KEEP"
        if capitulation_ratio >= self.delete_min:
            return "DELETE"
        return "ADVISORY_ONLY"


def assert_pre_registered(rule: KillRule, computed_at: str) -> None:
    """`PG-5.1` — ⚠ the plan must predate the data it judges."""
    if _t(rule.registered_at) >= _t(computed_at):
        raise NotPreRegistered(
            f"the kill rule was registered at {rule.registered_at}, not before the "
            f"test at {computed_at}. ⚠ A threshold chosen after seeing the data is "
            "a rationalisation, not a measurement (PG-5.1).")


def _t(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
