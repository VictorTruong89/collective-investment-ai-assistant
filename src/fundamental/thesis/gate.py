"""★ §11.2 — the real gate. Replaces the B3 stub (L3 BS-27, BS-34).

```
THE GATE STATUS IS A JUDGEMENT ABOUT THE THESIS'S OWN RELIABILITY — WHICH IS
D-01'S KNOWLEDGE, NOT D-12'S.

If D-12 derived the status it would need to know what agreement fraction
counts as unstable and what evidence coverage counts as thin. That is
ANALYTICAL POLICY, and D-12 is deterministic composition with no judgement.
Deriving it there would also be D-12 ORIGINATING a verdict, which DN-1 forbids.
```

★★ **RA-135 (added building this slice): the rows OVERLAP, so the status is the
MOST CONSERVATIVE match** — `VETO ⊐ FLAG ⊐ PASS`. RA-49 demands *"exactly one
status"* and the table is a **list of conditions, not a total function**: a
stable, confident BUY that is also **stale** matches both `PASS` and `FLAG`.
⚠ *First match wins* would make the answer depend on the order the rows happen
to be written in.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.fundamental.contracts.gate import FLAG, NO_THESIS, PASS, VETO, GateVerdict, Grade
from src.fundamental.errors import GateMappingError
from src.fundamental.monitor.variance import K_STAB
from src.fundamental.thesis.models import BUY, HOLD, INSUFFICIENT_DATA, SELL, Thesis

#: The S chain (D-12 §5.3). ★ Meeting on it is P3 applied INSIDE D-01: a gate may
#: only become more conservative as more conditions match.
SEVERITY = {PASS: 0, FLAG: 1, VETO: 2}

#: RA-48's two thresholds. ⚠ **Declared config that appears in the RunManifest**
#: (L4 CN-1) — module constants here only because B4.4 has no manifest to read
#: from, which is the same gap B4.3's confidence floors carry.
VETO_FLOOR = 0.5      # agreement below this ⇒ the model cannot reproduce itself
FLAG_FLOOR = 0.8      # agreement below this but at or above VETO_FLOOR ⇒ annotate

GATE_ID = "thesis"


@dataclass(frozen=True, slots=True)
class GateInputs:
    """Everything §11.2's table reads. ★ All of it is D-01's own knowledge.

    ⚠ `nominated_verdict` is deliberately **absent**. The gate answers *"D-03
    nominated a BUY; does the thesis support acting on it?"* — and the answer
    does not depend on which name D-03 picked, only on what the thesis says.
    Passing it in would let the gate tune itself to the nomination.
    """

    thesis: Thesis | None
    stale: bool = False
    falsifier_fired: bool = False
    #: RA-38's cap, from B4.3's `assess_confidence`. INSUFFICIENT_DATA has
    #: already been applied to the verdict by then; this is carried for the reason.
    confidence_cap: str = "none"


@dataclass(frozen=True, slots=True)
class Match:
    """One row of §11.2 that fired, with the reason it did."""

    status: str
    reason: str


def evaluate(inputs: GateInputs, *, as_of: date, ticker: str = "") -> GateVerdict:
    """★ The mapping. Total, deterministic, and identical theses map identically.

    L3 §3A.4's done-when for this slice: **D-12 receives a `GateVerdict` that
    varies with the thesis** — the B3 constant is gone.
    """
    thesis = inputs.thesis

    # ⚠ NO_THESIS is not on the S chain — it is a distinct state (DN-10) and
    # short-circuits. *The identity must not be reachable by omission.*
    if thesis is None:
        return GateVerdict(
            gate_id=GATE_ID, ticker=ticker.upper(), as_of=as_of, status=NO_THESIS,
            reason="no thesis exists for this name at this as_of. NO_THESIS is a "
                   "distinct state, never a PASS (§11.2, D-12 DN-10)",
            grade=Grade(),
        )

    matches = _matching_rows(inputs)
    if not matches:
        # RA-49 — *a state with no row is a defect, not a default to PASS.*
        raise GateMappingError(
            f"verdict={thesis.verdict!r} stability={thesis.verdict_stability!r} "
            f"stale={inputs.stale} falsifier_fired={inputs.falsifier_fired}"
        )

    # ★★ RA-135 — the most conservative match wins.
    binding = max(matches, key=lambda m: SEVERITY[m.status])
    also = [m.reason for m in matches if m is not binding]
    reason = binding.reason + (f" (also matched: {'; '.join(also)})" if also else "")

    return GateVerdict(
        gate_id=GATE_ID, ticker=(ticker or thesis.ticker).upper(), as_of=as_of,
        status=binding.status, reason=reason,
        thesis_version=thesis.thesis_version, thesis_as_of=thesis.as_of,
        grade=_grade_of(thesis),
    )


def _matching_rows(inputs: GateInputs) -> list[Match]:
    """Every row of §11.2 that fires. ⚠ Several can, which is RA-135's point."""
    thesis = inputs.thesis
    out: list[Match] = []
    agreement = _agreement(thesis)

    if thesis.verdict == BUY:
        if agreement is None:
            # ★★ RA-154 (2026-10-01) — UNMEASURED is neither stable nor unstable. This
            #   branch used to PASS, so every k=1 thesis passed the stability check by
            #   absence of evidence: the default RA-49 forbids.
            out.append(Match(
                FLAG, f"verdict stability is unmeasured: no RM-1 result with k >= "
                      f"{K_STAB} (RA-154) — not shown unstable, never shown stable"))
        elif agreement >= FLAG_FLOOR:
            out.append(Match(PASS, "the thesis independently supports the buy"))
        elif agreement >= VETO_FLOOR:
            # RA-48's middle — *annotate*, which is QR-2's answer.
            out.append(Match(
                FLAG, f"verdict agreement {agreement:.2f} is below the stability "
                      f"floor {FLAG_FLOOR} but above {VETO_FLOOR}"))
        else:
            out.append(Match(
                VETO, f"verdict agreement {agreement:.2f} is below {VETO_FLOOR} — "
                      f"the model does not reproduce its own answer"))
    elif thesis.verdict == HOLD:
        out.append(Match(VETO, "the thesis does not support a buy (verdict HOLD)"))
    elif thesis.verdict == SELL:
        # ⚠ *and ONLY to HOLD* — D-12 DN-9 forbids a gate originating a sell, and
        # §5.4 makes the veto inert on a SELL anyway. RA-50: a thesis that wants
        # an exit says so through an InvalidationEvent, never through the gate.
        out.append(Match(VETO, "the thesis verdict is SELL; the gate withholds "
                               "support for a buy and cannot cause a sell (RA-50)"))
    elif thesis.verdict == INSUFFICIENT_DATA:
        out.append(Match(VETO, "INSUFFICIENT_DATA — the absence of a thesis, not a "
                               "weak one (RA-38's floor)"))

    if inputs.stale:
        # RA-43/RA-71 — reported, not silently trusted.
        out.append(Match(FLAG, "the thesis is stale: an event of a class it depends "
                               "on occurred and was not read (RA-71)"))
    if inputs.falsifier_fired:
        out.append(Match(VETO, "a stated falsifier has fired — the thesis's own "
                               "breaking condition occurred (RA-41)"))
    return out


def _agreement(thesis: Thesis) -> float | None:
    """RM-1's agreement fraction, or `None` when no k-run probe was run.

    ⚠ **`None` is not 1.0.** A thesis with no stability result is not stable; it
    is unmeasured — and **RP-13 refuses to render it on the actionable path**
    (`RPT.STABILITY.MISSING`). That is BS-28's boundary, and it is why B4.4's
    output stays non-actionable until B4.5 supplies the probe.
    """
    stability = thesis.verdict_stability
    if not stability or stability.get("agreement") is None:
        return None
    # ★ RA-154 — a single run "agrees" with itself; below K_STAB the fraction
    #   measures nothing (`variance.py`), so it is unmeasured, not 1.0.
    if int(stability.get("k") or 0) < K_STAB:
        return None
    return float(stability["agreement"])


def _grade_of(thesis: Thesis) -> Grade:
    """RA-51 — the grade block is **byte-identical to the Thesis fields it
    mirrors** (D-12 DN-26). A transport copy, never a recomputation."""
    stability = thesis.verdict_stability or {}
    return Grade(
        verdict=thesis.verdict,
        conviction=thesis.conviction,
        stability_fraction=stability.get("agreement"),
        k=stability.get("k"),
        verdict_distribution=stability.get("distribution"),
        scorecard=_by_dimension(thesis.scorecard) if thesis.scorecard else None,
        confidence=dict(thesis.confidence) if thesis.confidence else None,
    )


def _by_dimension(scorecard: dict) -> dict:
    """`DX-178` — a `thesis_for` thesis keys its scorecard by BLOCK (`J-03` …), and CT-1.4's
    `Grade` by DIMENSION. ★ Re-keyed from each entry's own `rubric_id` (`moat_durability@v2`),
    the entry itself copied unchanged (DN-26); a key that is already a dimension stays.
    """
    out = {}
    for key, entry in scorecard.items():
        rubric = (entry or {}).get("rubric_id") if isinstance(entry, dict) else None
        out[rubric.split("@", 1)[0] if key.startswith("J-") and rubric else key] = entry
    return out
