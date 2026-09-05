"""D-01 §4A.2 — one authoring pass, end to end. RA-14, RA-15, RA-16, RA-19.

```text
  1  BLIND VIEW      bundle.redact()      RA-14 — price WITHHELD, physically
  2  STAGE-A FREEZE  hashed               RA-108 — before anything sees price
  3  J-11 BEAR CASE  separate call        RA-15 — not the pass that argued bull
  4  J-15 FALSIFIERS separate call        RA-16 — BEFORE the verdict
  5  PERSIST         commit hash          ★ the write that makes 4 provable
  6  J-16 VERDICT    full bundle          the reconciliation stage
```

★★ **Step 5 is the one that is easy to skip and impossible to fake.** *One call
emitting both satisfies the old wording and buys nothing: the falsifiers get
fitted to a verdict already reached.* The commit hash is what distinguishes
*"the falsifiers were committed first"* from *"one call produced both and we
wrote them in that order"*.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from src.fundamental.thesis.models import BearCase, Falsifier
from src.fundamental.thesis.probe import ProbeRun

VERDICT_PATTERN = re.compile(
    r"\b(BUY|HOLD|SELL|INSUFFICIENT[_ ]DATA)\b", re.I)
CONVICTION_PATTERN = re.compile(
    r"\b(Medium-High|Low|Medium|High)\b", re.I)


@dataclass(frozen=True, slots=True)
class ParsedVerdict:
    """What J-16 returned, read from the text. ⚠ **Parsed, never inferred.**

    ★ A verdict this parser cannot find is `INSUFFICIENT_DATA` **only if J-16
    said so** — an unparseable response raises, because *a plausible default is
    exactly what P5 forbids* and the model was given a bounded option list.
    """

    verdict: str
    conviction: str
    text: str

    @classmethod
    def parse(cls, text: str) -> "ParsedVerdict":
        from src.fundamental.errors import VerdictNotEnumError

        found = VERDICT_PATTERN.search(text or "")
        if not found:
            raise VerdictNotEnumError(
                "verdict", (text or "")[:80],
                ("BUY", "HOLD", "SELL", "INSUFFICIENT_DATA"))
        verdict = found.group(1).upper().replace(" ", "_")
        conviction = CONVICTION_PATTERN.search(text or "")
        return cls(verdict=verdict,
                   conviction=(conviction.group(1) if conviction else "Medium"),
                   text=text)


def parse_falsifiers(text: str, *, deadline: date, observables) -> tuple:
    """J-15's output, as `Falsifier` objects.

    ⚠ **The `Falsifier` contract does the validating, not this parser** — it
    already refuses a tautology, an unnamed observable and a missing
    materiality (RA-35). A parser that pre-filtered would hide what the model
    actually wrote, and RM-13's *"were the falsifiers decorative?"* question
    needs the real output.
    """
    out, ordinal = [], 0
    for line in (text or "").splitlines():
        stripped = line.strip(" -*\t")
        if not stripped or len(stripped) < 25:
            continue
        # ⚠ The field must be NAMED. RA-35: *a falsifier naming a field this
        #   system does not receive is not checkable, however precise it
        #   sounds* — and one naming no field at all is worse. The bundle now
        #   carries the available list (`observables()`), so a model that names
        #   none had the list and declined to use it.
        field = next((o for o in observables if o.lower() in stripped.lower()), "")
        if not field:
            continue
        ordinal += 1
        out.append(Falsifier(
            ordinal=ordinal, condition=stripped[:400], observable_field=field,
            source="D-02", deadline=deadline,
            materiality=f"stated with condition {ordinal}", about_business=True))
        if ordinal >= 4:
            break
    return tuple(out)


#: ★★ **Confidence is DECLARED UNMEASURED, not reported as `0.0`.**
#:
#: ⏸ **POSTPONED to the next release — Victor, 2026-08-27.** Wiring B4.2's
#: extraction and B4.3's scorecard into authoring needs mathematical and
#: algorithmic reconsideration plus experiment; it is not a plumbing job. See
#: `L6-as-built-remaining.md` **AB-1**.
#:
#: ⚠ **The value it replaces was a lie by shape.** `{"value": 0.0, "basis":
#: "evidence_coverage"}` says *coverage was measured and came out zero*. The
#: truth is that coverage was **never computed** — `scorecard/`, `claims/` and
#: `filings/` are built and tested and this path calls none of them. ★ A reader
#: cannot tell a company with no evidence from a pipeline that never looked, and
#: **RA-30 already gives a monitor the vocabulary to decline** rather than
#: invent a number (RA-136 added `not_measurable` for exactly this shape).
#:
#: ★ **This is why `CONFIDENCE_FLOOR` needs no change.** RA-38 computes the
#: floor *from* coverage; with no coverage the floor is **unreachable, not
#: disabled** — so the constant stays at `0.3` and keeps doing its live work in
#: the relay path (`relay/ingest.py`, AC-1.77), where the floors are the only
#: thing de-rating a pasted chat report.
UNMEASURED_CONFIDENCE = {
    "value": None,
    "basis": "not_measured",
    "reason": "B4.2 extraction and B4.3 scorecard are not wired into authoring, "
              "so evidence_coverage was never computed (AB-1, RA-67)",
}


def author_once(*, bundle, gateway, run: "AuthoringRun", index: int,
                observables, deadline: date, run_id: str):
    """One full pass. ★ Returns `(ProbeRun, Thesis)` for `author_thesis`.

    ⚠ Every call goes through `AnalysisGateway`, so the four guards run on each:
    **pinned → aligned → no ambient context → view match** (RA-13, RA-14, RA-12).
    """
    from src.fundamental.thesis.probe import evidence_rotation

    blind = bundle.redact()                     # RA-14 — physical, not asked for
    # ★ RM-1's second perturbation, applied where it reaches the model. The
    #   bundle — and therefore `bundle_hash` — is identical across the k runs.
    rotation = evidence_rotation(bundle, index)

    bear_call = gateway.call(prompt_name="J-11", prompt_version="v1",
                             bundle=blind, run_id=run_id, step="bear_case",
                             evidence_rotation=rotation)
    bear = BearCase(text=bear_call.text[:4000],
                    falsification_condition=_first_condition(bear_call.text),
                    prompt_version="J-11@v1", run_id=bear_call.run.call_id)

    # ★ RA-16 — J-15 runs BEFORE the verdict, as its own call.
    falsifier_call = gateway.call(prompt_name="J-15", prompt_version="v1",
                                  bundle=blind, run_id=run_id, step="falsifiers",
                                  evidence_rotation=rotation)
    falsifiers = parse_falsifiers(falsifier_call.text, deadline=deadline,
                                  observables=observables)

    # ── step 6 — the verdict, on the FULL bundle (the reconciliation stage).
    verdict_call = gateway.call(prompt_name="J-16", prompt_version="v1",
                                bundle=bundle, run_id=run_id, step="verdict",
                                evidence_rotation=rotation)
    parsed = ParsedVerdict.parse(verdict_call.text)

    thesis = run.author(
        bundle=bundle, stage_a_payload={"bear_case_seen": True},
        falsifiers=falsifiers, verdict=parsed.verdict,
        conviction=parsed.conviction, bear_case=bear,
        scorecard={}, confidence=UNMEASURED_CONFIDENCE,
        bull_run_ids=(verdict_call.run.call_id,), run_id=run_id,
        thesis_version=1)

    calls = (bear_call, falsifier_call, verdict_call)
    return ProbeRun(
        index=index, verdict=parsed.verdict, conviction=parsed.conviction,
        # ★ What the MODEL saw, which is the thing being perturbed.
        evidence_order=tuple(
            (list(p.kind for p in bundle.parts)[rotation:]
             + list(p.kind for p in bundle.parts)[:rotation])),
        option_permutation=verdict_call.run.option_permutation,
        run_ids=tuple(c.run.call_id for c in calls),
        tokens_in=sum(c.run.tokens_in or 0 for c in calls),
        tokens_out=sum(c.run.tokens_out or 0 for c in calls),
    ), thesis


def _first_condition(text: str) -> str:
    """RA-15's *"name the single condition that would confirm it"*."""
    for line in (text or "").splitlines():
        stripped = line.strip(" -*\t")
        if len(stripped) > 30:
            return stripped[:300]
    return "the bear case stated no confirming condition"
