"""D-04 §10 — 1m nominates, 1w may delay or veto. MT-31, MT-32, QA-47, P3.

```text
  h1m  21d  SELECTION   ★ the only horizon that may nominate the daily pick
  h1w   5d  TIMING       may delay or veto — NEVER nominates
  h1q  63d  RESEARCH     D-10 only — never reaches a human-facing artifact
```

★★ **MT-32: the timing leg is a gate, so P3 binds it.** It may make an outcome
**equal or more conservative, never more aggressive.** *"Wait" is legal; "buy a
different name" is not* — QA-47's arbitration and P3's monotonicity are the same
rule seen from two domains.
"""

from __future__ import annotations

from dataclasses import dataclass

NOMINATE, DELAY, VETO = "nominate", "delay", "veto"


@dataclass(frozen=True, slots=True)
class ArbitrationResult:
    nominated: str | None
    outcome: str
    nominated_by: str
    delayed_by: str = ""
    vetoed_by: str = ""
    why: str = ""

    def to_json_obj(self) -> dict:
        return {"nominated": self.nominated, "outcome": self.outcome,
                "nominated_by": self.nominated_by, "delayed_by": self.delayed_by,
                "vetoed_by": self.vetoed_by, "why": self.why}


def arbitrate(selection: ScoreResult, timing=None, *,
              timing_threshold: float = 0.0) -> ArbitrationResult:
    """MT-31/MT-32 — ★ the timing leg **may never originate or substitute** a
    nomination.

    ⚠ The structural guarantee: this function reads `timing` only to decide
    between *the selection's pick* and *no pick*. There is no branch in which a
    name comes from `timing`.
    """
    from src.models.errors import HorizonRoleError

    ranked = selection.ranked()
    if not ranked:
        return ArbitrationResult(None, VETO, selection.artifact_id,
                                 why="the selection leg ranked nothing")
    eligible = [t for t, _ in ranked if t not in selection.excluded]
    if not eligible:
        # MT-11 — a ranking with no eligible pick does not pick one anyway.
        return ArbitrationResult(
            None, VETO, selection.artifact_id,
            why="every ranked name is below feature coverage (MT-11)")
    pick = eligible[0]

    if timing is None:
        return ArbitrationResult(pick, NOMINATE, selection.artifact_id)

    if pick not in timing.scores:
        raise HorizonRoleError(
            f"the timing leg scored no view on {pick!r}, the selection leg's "
            f"pick. ⚠ It cannot substitute a name it does prefer — that would "
            f"be the timing leg originating a nomination")
    view = timing.scores[pick]
    if view < timing_threshold:
        # ★ P3 — more conservative only. "Wait", never "buy something else".
        return ArbitrationResult(
            pick, DELAY, selection.artifact_id, delayed_by=timing.artifact_id,
            why=f"timing view {view:.4f} < {timing_threshold:.4f}")
    return ArbitrationResult(pick, NOMINATE, selection.artifact_id)
