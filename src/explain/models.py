"""F4 `CT-4.1`–`CT-4.3` — the explanation contract.

★★ **The distinction this whole module turns on:**

```text
   PLAUSIBLE   the explanation reads well and satisfies a human
   FAITHFUL    the explanation describes the computation that actually ran

   ⚠ THESE ARE INDEPENDENT. A plausible-but-unfaithful explanation is
     WORSE THAN NONE — it manufactures confidence while conveying nothing.
```

⚠ **D-13 composes; it never computes.** Only the module that performed a
computation can attribute it (`QR-10`) — SHAP needs the fitted model,
claim-binding needs the extraction pipeline. Seat 6 assembles **already
published** attributions, which is what keeps it on the legal side of the
analyst firewall (`INV-014`/`ST-9`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Direction = Literal["up", "down"]
SubjectStatus = Literal["promoted", "unpromoted", "experimental"]


@dataclass(frozen=True, slots=True)
class Driver:
    """⚠ `name` is an OBSERVABLE, never a feature id (`AC-4.8`'s spirit)."""

    name: str
    contribution: float
    direction: Direction

    def __post_init__(self) -> None:
        if self.direction not in ("up", "down"):
            raise ValueError(f"direction is up|down; got {self.direction!r}")


@dataclass(frozen=True, slots=True)
class Attribution:
    """`CT-4.1` — a field on **each analytical domain's own output**, not D-13's."""

    domain: str
    method: str
    drivers: tuple[Driver, ...] = ()
    baseline: float | None = None
    #: ⚠ `AC-4.11` / `D3` — a number, or explicitly None. **Never 0**, which reads
    #: as *measured and perfectly unstable* rather than *not measured*.
    stability: float | None = None
    subject_status: SubjectStatus = "unpromoted"

    def __post_init__(self) -> None:
        if not self.domain:
            raise ValueError("an attribution names the domain that produced it (QR-10)")
        if not self.method:
            raise ValueError(
                "method is required (AC-4.15, D2) — F4 commits to no method, but an "
                "unnamed one cannot be partitioned by later comparison"
            )
        if self.subject_status not in ("promoted", "unpromoted", "experimental"):
            raise ValueError(f"unknown subject_status {self.subject_status!r}")
        if self.stability is not None and not 0.0 <= self.stability <= 1.0:
            raise ValueError("stability is an agreement fraction in [0, 1]")


@dataclass(frozen=True, slots=True)
class Change:
    observable: str
    from_value: object
    to_value: object


@dataclass(frozen=True, slots=True)
class Counterfactual:
    """`CT-4.3` — stated in **observables**, never in feature space.

    ★ *"Gross margin holds above 42 % for two more quarters"* is monitorable;
    `f_gross_margin_z + 0.4σ` is not.

    ⚠ A **rank** counterfactual is conditional on the peer set, so `as_of` and
    `universe_id` are required (`AC-4.9`).
    """

    statement: str
    changes: tuple[Change, ...]
    flips_to: str
    as_of: str
    universe_id: str

    def __post_init__(self) -> None:
        if not self.changes:
            raise ValueError(
                "a Counterfactual with no changes is not a counterfactual — report "
                "'no single-observable change flips this' instead (AC-4.14)"
            )
        if not (self.as_of and self.universe_id):
            raise ValueError(
                "as_of and universe_id are required (AC-4.9) — a rank counterfactual "
                "is conditional on the peer set it was computed against"
            )

    @property
    def sparsity(self) -> int:
        return len(self.changes)


@dataclass(frozen=True, slots=True)
class Explanation:
    """`CT-4.2` — D-13's output. **Assembled, never recomputed** (`AC-4.3`)."""

    subject_id: str
    as_of: str
    universe_id: str
    attributions: tuple[Attribution, ...]
    gate_binding: dict | None = None
    counterfactual: Counterfactual | None = None
    #: ⚠ Until upstream R7 lands `AB-2`, `claims_total` is 0 and `unbound` empty —
    #: the honest current state (`D1`), not a placeholder pretending otherwise.
    grounding: dict = field(default_factory=lambda: {"claims_total": 0,
                                                     "claims_bound": 0,
                                                     "unbound": []})
    #: ⚠ Coverage, NOT calibration (`F5` `AC-5.5`, upstream `AB-1`).
    confidence: dict = field(default_factory=lambda: {"basis": "not_measured"})

    def __post_init__(self) -> None:
        if not self.attributions:
            raise ValueError(
                "an Explanation with no attribution explains nothing (AC-4.1)")
        if self.counterfactual is not None:
            cf = self.counterfactual
            if (cf.as_of, cf.universe_id) != (self.as_of, self.universe_id):
                raise ValueError(
                    "the counterfactual's as_of/universe_id must match the "
                    "explanation's — a peer-conditional claim scoped to a "
                    "different universe is not about this subject (AC-4.9)")

    @property
    def subject_status(self) -> SubjectStatus:
        """⚠ `AC-4.12` — the WEAKEST status wins.

        ★ An explanation is only as promotable as its least-promoted input; a
        composed artifact must not launder an unpromoted model's authority
        (`PG-2`). The ranker sits at walk-forward IC 0.0203, *t* = 1.42.
        """
        order = {"experimental": 0, "unpromoted": 1, "promoted": 2}
        return min((a.subject_status for a in self.attributions),
                   key=lambda s: order[s])
