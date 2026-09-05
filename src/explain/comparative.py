"""F4 `T2` / `AC-4.13` — *"why this one and not that one?"* (`QR-16`).

★ The gap is named using each subject's **own published attribution**. D-13 does
not re-run either model to explain the difference — that would be recomputation
(`AC-4.3`) and, for the two analysts, a firewall crossing (`INV-014`).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.explain.models import Explanation


@dataclass(frozen=True, slots=True)
class DriverGap:
    name: str
    contribution_a: float
    contribution_b: float

    @property
    def gap(self) -> float:
        return self.contribution_a - self.contribution_b


@dataclass(frozen=True, slots=True)
class Comparison:
    subject_a: str
    subject_b: str
    as_of: str
    universe_id: str
    gaps: tuple[DriverGap, ...]
    #: ⚠ The weaker of the two statuses — a comparison is no more promotable
    #: than its least-promoted side (`PG-2`).
    subject_status: str

    @property
    def leading_driver(self) -> DriverGap | None:
        return max(self.gaps, key=lambda g: abs(g.gap), default=None)


def compare(a: Explanation, b: Explanation) -> Comparison:
    if (a.as_of, a.universe_id) != (b.as_of, b.universe_id):
        raise ValueError(
            "a comparison is peer-conditional: both subjects must share as_of and "
            "universe_id, or the gap is between two different questions (AC-4.9)")
    da = {d.name: d.contribution for at in a.attributions for d in at.drivers}
    db = {d.name: d.contribution for at in b.attributions for d in at.drivers}
    gaps = tuple(sorted(
        (DriverGap(n, da.get(n, 0.0), db.get(n, 0.0)) for n in set(da) | set(db)),
        key=lambda g: -abs(g.gap)))
    order = {"experimental": 0, "unpromoted": 1, "promoted": 2}
    status = min((a.subject_status, b.subject_status), key=lambda s: order[s])
    return Comparison(a.subject_id, b.subject_id, a.as_of, a.universe_id,
                      gaps, status)
