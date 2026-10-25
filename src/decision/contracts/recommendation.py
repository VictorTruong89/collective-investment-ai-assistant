"""CT-12.1 — the Recommendation, D-12's single artifact-ready output.

★ **The meet is lossy, so D-12 must TRANSPORT what it does not consume**
(§5.8, DN-25, DN-32). A meet discards everything except the ordering — D-03's
rank magnitude, D-01's conviction, RM-1's k-run stability, the scorecard.
Discarding them for the *verdict* is correct; discarding them from the *artifact*
would kill the graded information here, because §1.5 forbids `D-12 -> D-06`.

⚠ **DN-32: transport is COMPLETE, not selective.** *A field dropped in transport
is indistinguishable downstream from a field the producer never emitted* — and
this contract had silently dropped `k`, `verdict_distribution` and `confidence`,
each of which RA-20 or RA-21 requires the artifact to render.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.decision.algebra.verdict import CONSERVATISM


@dataclass(frozen=True, slots=True)
class GateOutcome:
    """One gate's contribution, and the verdict standing after it."""

    gate_id: str
    status: str
    verdict_after: str
    reason: str
    produced_by_stub: str | None = None


@dataclass(frozen=True, slots=True)
class Attribution:
    """★ EVERY gate at the binding level, not the first (DN-13).

    With a meet, several gates can be simultaneously binding. Reporting one of
    three makes the other two invisible, and the reader fixes a third of the
    problem believing they fixed it.
    """

    binding: tuple[str, ...]
    binding_level: str


@dataclass(frozen=True, slots=True)
class Recommendation:
    """CT-12.1."""

    as_of: date
    run_id: str
    decision_anchor: str
    candidate: dict                       # ticker, rank, ranked_quantity, horizon
    verdict_final: str
    verdict_nominated: str
    gates: tuple[GateOutcome, ...]
    attribution: Attribution
    grade: dict                           # ★ DN-25 — consumed_by_algebra: false
    alerts: tuple[dict, ...]
    alerts_status: str                    # ★ DN-38 — COMPLETE | UNCHECKED: <why>
    gate_roster_declared: tuple[str, ...]
    gate_roster_reported: tuple[str, ...]
    actionable: bool
    not_actionable_reason: str | None = None
    thesis_ref: dict | None = None
    #: ★ DN-43 — D-05's FlagPass (CT-5.4), carried verbatim; nothing in D-12 reads it.
    behavioural_flags: dict | None = None
    deferral: dict | None = None
    stubs: tuple[dict, ...] = field(default_factory=tuple)
    #: ★ `PG-7.3` / `F6a` `AC-6a.10` — `"independent"` | `"cross-configured"`.
    #: ⚠⚠ The STATUS TRAVELS IN THE FIELD, not in a caveat elsewhere. `F2` `D3`
    #: renamed `IDENTICAL` → `REPRODUCED` for exactly this reason: *"the name is
    #: what gets copied"*, and a caveat that does not travel beside the value it
    #: qualifies is decoration. A reader of the stored JSON can therefore never
    #: mistake an echo for concurrence between independent views.
    concurrence: str = "independent"

    @property
    def was_downgraded(self) -> bool:
        return CONSERVATISM[self.verdict_final] > CONSERVATISM[self.verdict_nominated]

    def to_json_obj(self) -> dict:
        return {
            "as_of": self.as_of.isoformat(), "run_id": self.run_id,
            "decision_anchor": self.decision_anchor,
            "candidate": dict(self.candidate),
            "verdict": {"final": self.verdict_final,
                        "nominated": self.verdict_nominated,
                        "was_downgraded": self.was_downgraded},
            "gates": [{"gate_id": g.gate_id, "status": g.status,
                       "verdict_after": g.verdict_after, "reason": g.reason,
                       "produced_by_stub": g.produced_by_stub} for g in self.gates],
            "attribution": {"binding": list(self.attribution.binding),
                            "binding_level": self.attribution.binding_level},
            "thesis_ref": self.thesis_ref,
            "behavioural_flags": self.behavioural_flags,
            "alerts": [dict(a) for a in self.alerts],
            "alerts_status": self.alerts_status,
            # ★ DN-25 — the flag is ON the block, so a reader of the stored JSON
            # cannot mistake a transported number for one the algebra used.
            "grade": {"consumed_by_algebra": False, **self.grade},
            "concurrence": self.concurrence,
            "deferral": self.deferral,
            "actionable": self.actionable,
            "not_actionable_reason": self.not_actionable_reason,
            "gate_roster_declared": list(self.gate_roster_declared),
            "gate_roster_reported": list(self.gate_roster_reported),
            "stubs": [dict(s) for s in self.stubs],
        }
