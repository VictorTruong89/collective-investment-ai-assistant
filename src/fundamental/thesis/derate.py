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
from decimal import Decimal

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
def governing_inputs_absent(outputs: dict, stage_a: list, *,
                            price_requirement: dict | None = None) -> tuple[str, ...]:
    """The absent inputs that a GOVERNING consideration of `J-16` rests on.

    ⚠ Only the considerations `J-16` itself ranked as deciding are examined: an absent
    input the verdict did not turn on is a data gap (`J-17`), not a de-rating.
    """
    governing = " ".join(
        f"{c.get('from_call', '')} {c.get('consideration', '')}"
        for c in (outputs.get("D:J-16", {}).get("considerations") or ()))
    absent = []
    for block_id, label, present in _absences(outputs, stage_a, price_requirement):
        if present and block_id.lower() in governing.lower():
            absent.append(f"{block_id}: {label}")
    return tuple(absent)


def _absences(outputs: dict, stage_a: list, price_requirement: dict | None = None):
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
           any(r.get("versus_stage_a") == "insufficient_evidence" and not _rests_on_known_limit(r)
               for r in (j09.get("price_requirements") or ())))
    yield ("J-10", "no reference-class base rate in the bundle",
           any(not c.get("base_rate_in_bundle") and _counts_for_j10(c, price_requirement)
               for c in (j10.get("claims") or ())))


#: ✏ `DX-140` (Victor, 2026-10-02). How a requirement shows it rests on a limit D-02 DECLARES
#: it cannot compute (`F10` `D9`, `CT-F10.2` `known_limits`): it cites the trail's field, or
#: quotes the limit's own opening words. ⚠ Matched on the text the answer already carries —
#: a new schema field would be one more way a call can fail (`DX-113`).
KNOWN_LIMITS_FIELD = "known_limits"
_LIMIT_QUOTE_CHARS = 40


def _declared_limits() -> tuple[str, ...]:
    from src.feature_engineer.valuation.basis import KNOWN_LIMITS
    return KNOWN_LIMITS


def _rests_on_known_limit(row: dict) -> bool:
    text = f"{row.get('requirement', '')} {row.get('if_it_holds', '')}"
    return KNOWN_LIMITS_FIELD in text or any(
        limit[:_LIMIT_QUOTE_CHARS] in text for limit in _declared_limits())


_NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
                 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 15: "fifteen",
                 20: "twenty"}


def _is_price_requirement_claim(claim: dict, req: dict) -> bool:
    """✏ `DX-146` — a `J-10` claim about what the PRICE requires: it states one of the subject's
    required growth rates (at 0, 1 or 2 dp, as a percent) or one of its duration periods as a
    span of years. ★ Matched on the subject's own `F10` numbers, never a list of phrases."""
    import re
    text = str(claim.get("claim") or "").lower()
    for g in req.get("growth", ()):
        pct = Decimal(g) * 100
        for dp in (2, 1, 0):
            shown = f"{pct:.{dp}f}"
            if re.search(rf"(?<![\d.]){re.escape(shown)}\s*%", text):
                return True
    for n in req.get("periods", ()):
        words = [str(n)] + ([_NUMBER_WORDS[n]] if n in _NUMBER_WORDS else [])
        if any(re.search(rf"\b{w}[- ](?:consecutive |explicit )?years?\b", text) for w in words):
            return True
    return False


def _counts_for_j10(claim: dict, req: dict | None) -> bool:
    """Without the subject's price requirement, every unsupported claim counts (the stricter
    rule, unchanged). With it, only price-requirement claims cap; the rest are STATED."""
    return True if req is None else _is_price_requirement_claim(claim, req)


def stated_limitations(outputs: dict, *, price_requirement: dict | None = None
                       ) -> tuple[str, ...]:
    """`DX-140` — requirements left unset ONLY by a declared known limit. ★ Stated on the
    thesis (`PG-10`) and NOT counted as a governing absence: no input the system can obtain
    would cure them, so a cap keyed to them would be a constant, not a signal."""
    rows = (outputs.get("B:J-09", {}).get("price_requirements") or ())
    stated = [f"J-09: {r.get('requirement', '').strip()}" for r in rows
              if r.get("versus_stage_a") == "insufficient_evidence"
              and _rests_on_known_limit(r)]
    # ✏ `DX-146` — J-10 claims the verdict's price requirement does not rest on.
    if price_requirement is not None:
        stated += [f"J-10: no base rate for — {str(c.get('claim', '')).strip()}"
                   for c in (outputs.get("B:J-10", {}).get("claims") or ())
                   if not c.get("base_rate_in_bundle")
                   and not _is_price_requirement_claim(c, price_requirement)]
    return tuple(stated)


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
           stage_a: list, price_requirement: dict | None = None) -> Derating:
        report = coverage_report(rubrics, extracted)
        assessment = assess_confidence(report)
        capped_verdict, verdict_reason = cap_verdict(verdict, assessment)
        absent = governing_inputs_absent(outputs, stage_a, price_requirement=price_requirement)
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
                "limitations_stated": list(stated_limitations(
                    outputs, price_requirement=price_requirement)),
                # ★ `PG-10` on the artifact itself: the limitation travels with the claim.
                "note": ("Investment judgement never rests on complete evidence; this thesis "
                         "states what was missing rather than declining to hold a view. The "
                         "floors may only make a verdict more conservative (P3, INV-012/013)."),
            })
