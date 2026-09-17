"""What thin evidence may do to a verdict — `INV-012`, `INV-013`, `RA-38`, `RA-67`.

★★ **The decision this module implements** (Victor, 2026-09-15, L3 `DX-118`). The
alternative on the table was a HARD CAP: *forbid a directional verdict whenever the
consideration that governs it rests on a declared-absent input.* It was rejected, and the
reason is the domain's: **no investment judgement rests on complete evidence — the analyst
proceeds with the limitation and states it.** A rule keyed to "an input is absent" would,
on today's bundles, return `INSUFFICIENT_DATA` for every company forever: an off switch
wearing a filter's clothing, and it would starve the very measurements (`RM-1`, `RM-13`,
`F5`) that catch a wrong verdict.

★ **What replaces it is the ladder the house already specified and never wired up:**
`assess_confidence` over `coverage_report` (`INV-012` below 0.3 ⇒ decline; `INV-013` below
0.5 ⇒ capped at HOLD), plus a conviction cap when a GOVERNING consideration rests on an
input that was explicitly absent. ⚠ Both are **floors on what may be proposed**, never a
licence to be more aggressive (`P3`), and both are DECLARED on the artifact (`PG-10`).

⚠⚠ **"Capped at HOLD" is a MEET, not an assignment** (`L1-decision` §5.3 `DN-9`, §5.4):

```text
        SELL  ⊏  HOLD  ⊏  BUY            the verdict chain, conservative first
        cap(BUY,  HOLD) = HOLD           a thin-evidence BUY may not be proposed
        cap(SELL, HOLD) = SELL           ★ absorption — a cap cannot BLOCK AN EXIT
```

★ The asymmetry is deliberate and falls out of `P3`: *the discipline layer can stop you
buying; it cannot stop you selling.* A coverage cap that turned SELL into HOLD would hold a
position against its owner on the strength of a missing input.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.fundamental.scorecard.coverage import assess_confidence, coverage_report
from src.fundamental.thesis.models import BUY, CONVICTIONS, HOLD, INSUFFICIENT_DATA, SELL

#: The verdict chain, most conservative first (`L1-decision` §5.3). ⚠ `INSUFFICIENT_DATA`
#: is NOT on it — it is the decline, and it maps to a gate `VETO` downstream.
VERDICT_CHAIN = (SELL, HOLD, BUY)

#: The conviction a thesis may claim when a governing consideration rests on an input the
#: bundle declared absent. ★ Lowest of `CONVICTIONS`, never zero: the view still stands.
CAPPED_CONVICTION = CONVICTIONS[0]


def cap_verdict(verdict: str, assessment) -> tuple[str, str | None]:
    """`(verdict, why it moved)` under the coverage floors. ★ Never more aggressive."""
    if assessment.forces_insufficient_data:
        # `INV-012` — below the floor the system declines. ⚠ This is the ONE place a
        # verdict is replaced rather than met: a decline is not a point on the chain.
        if verdict != INSUFFICIENT_DATA:
            return INSUFFICIENT_DATA, (
                f"evidence coverage {assessment.value:.2f} is below the {0.3:.2f} floor, so "
                f"no directional verdict may be proposed (INV-012, RA-38)")
        return verdict, None
    if assessment.caps_at_hold and verdict in VERDICT_CHAIN:
        met = min(verdict, HOLD, key=VERDICT_CHAIN.index)
        if met != verdict:
            return met, (
                f"evidence coverage {assessment.value:.2f} is below {0.5:.2f}, so the verdict "
                f"is capped at HOLD (INV-013)")
    return verdict, None


#: How an ABSENT input announces itself in a committed answer, per block. ★ Derived in
#: CODE from what the blocks returned, not asked of the model: every extra required schema
#: field is one more way a paid call can fail (`DX-113`, measured on `J-11`).
def governing_inputs_absent(outputs: dict, stage_a: list) -> tuple[str, ...]:
    """The absent inputs that a GOVERNING consideration of `J-16` rests on.

    ⚠ Only the considerations `J-16` itself ranked as deciding are examined: an absent
    input the verdict did not turn on is a data gap (`J-17`), not a de-rating.
    """
    governing = " ".join(
        f"{c.get('from_call', '')} {c.get('consideration', '')}"
        for c in (outputs.get("D:J-16", {}).get("considerations") or ()))
    absent = []
    for block_id, label, present in _absences(outputs, stage_a):
        if present and block_id.lower() in governing.lower():
            absent.append(f"{block_id}: {label}")
    return tuple(absent)


def _absences(outputs: dict, stage_a: list):
    """`(block, what is absent, is it absent)` — one row per known absence signal."""
    by_block = {r["block_id"]: r.get("answer") or {} for r in stage_a}
    j08 = by_block.get("J-08", {})
    j09 = outputs.get("B:J-09", {})
    j10 = outputs.get("B:J-10", {})
    yield ("J-08", "supply_read is insufficient_evidence — no competitor capacity",
           j08.get("supply_read") == "insufficient_evidence")
    yield ("J-09", "no consensus position in the bundle",
           "insufficient" in str(j09.get("consensus_position", "")).lower())
    yield ("J-09", "a price requirement could not be set against Stage A",
           any(r.get("versus_stage_a") == "insufficient_evidence"
               for r in (j09.get("price_requirements") or ())))
    yield ("J-10", "no reference-class base rate in the bundle",
           any(not c.get("base_rate_in_bundle") for c in (j10.get("claims") or ())))


def cap_conviction(conviction: str, absent: tuple[str, ...]) -> tuple[str, str | None]:
    """`(conviction, why)` — a governing consideration on an absent input caps it low.

    ★ The verdict is untouched: the analyst proceeds (the domain has no complete
    evidence), and the artifact says how much of what the verdict needed was there.
    """
    if not absent or CONVICTIONS.index(conviction) <= CONVICTIONS.index(CAPPED_CONVICTION):
        return conviction, None
    return CAPPED_CONVICTION, (
        f"a governing consideration rests on {len(absent)} input(s) the bundle declared "
        f"absent, so conviction is capped at {CAPPED_CONVICTION} (RA-67)")


@dataclass(frozen=True, slots=True)
class Derating:
    """What the floors did, and everything a reader needs to re-derive it (`AP-2`)."""

    verdict: str
    conviction: str
    confidence: dict

    @classmethod
    def of(cls, *, verdict: str, conviction: str, rubrics, extracted, outputs: dict,
           stage_a: list) -> Derating:
        report = coverage_report(rubrics, extracted)
        assessment = assess_confidence(report)
        capped_verdict, verdict_reason = cap_verdict(verdict, assessment)
        absent = governing_inputs_absent(outputs, stage_a)
        capped_conviction, conviction_reason = cap_conviction(conviction, absent)
        return cls(
            verdict=capped_verdict, conviction=capped_conviction,
            confidence={
                **assessment.to_json_obj(),
                "coverage": report.to_json_obj(),
                "verdict_as_authored": verdict,
                "verdict_capped_by": verdict_reason,
                "conviction_as_authored": conviction,
                "conviction_capped_by": conviction_reason,
                "governing_inputs_absent": list(absent),
                # ★ `PG-10` on the artifact itself: the limitation travels with the claim.
                "note": ("Investment judgement never rests on complete evidence; this thesis "
                         "states what was missing rather than declining to hold a view. The "
                         "floors may only make a verdict more conservative (P3, INV-012/013)."),
            })
