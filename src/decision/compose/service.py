"""Composition — nomination + gates + alerts -> `CT-12.1` (§5, DN-1…DN-23, DN-38).

USE-CASE layer (**CA-2**): no transport, no filesystem, no vendor SDK. It
receives the three inputs and returns the artifact.

★ **D-12 originates nothing.** Every verdict it emits was emitted by someone else
first, and its only freedom is to make one *more conservative* (P3, DN-1). That
is checked here explicitly — not because the meet could produce an upgrade, but
because a check that can never fire is the only way to know the meet was used.
"""

from __future__ import annotations

from datetime import date

from src.decision.algebra.verdict import BUY, apply_gate, conservatism, meet
from src.decision.attribute.binding import attribute
from src.decision.concurrence import (
    assert_may_claim_independent_agreement,
    concurrence_label,
)
from src.decision.contracts.recommendation import GateOutcome, Recommendation
from src.decision.errors import (
    AbsentTreatedAsPassError,
    AnchorMismatchError,
    GateMissingError,
    MultipleActionableError,
    SellNotHeldError,
    VerdictOriginatedError,
    VerdictUpgradeError,
)

#: What D-03 nominating a top candidate means as a verdict. ★ D-03 never emits a
#: verdict (QA-29) — it ranks. The nomination of a rank-1 name is the proposal
#: `BUY`, and naming that here keeps the translation in one visible place rather
#: than implied at a call site.
NOMINATED_VERDICT = BUY


def compose(
    *, nomination, gate_verdicts, alert_set, run_id: str, as_of: date,
    gate_roster_declared, manifest_anchor: str, held_tickers=(),
    actionable: bool, not_actionable_reason: str | None = None, stubs=(),
    top_thesis_stability: dict | None = None,
    influenced_by: tuple[str, ...] = (),
    claim_independent_agreement: bool = False,
    thesis_ref: dict | None = None,
) -> Recommendation:
    """Pure, total on declared inputs (§8's API surface).

    `gate_roster_declared` is passed in rather than inferred — **DN-11**:
    *inferring the roster from responders makes a silently-absent gate
    structurally undetectable.*
    """
    declared = tuple(sorted(gate_roster_declared))
    reported = tuple(sorted(g.gate_id for g in gate_verdicts))

    missing = set(declared) - set(reported)
    if missing:
        # DN-11 first, then DN-10's named error for the specific gate. Both exist
        # because "the roster disagrees" and "this gate would have composed as the
        # identity" are different diagnoses.
        for gate_id in sorted(missing):
            raise AbsentTreatedAsPassError(gate_id) if len(missing) == 1 \
                else GateMissingError(missing, declared)

    if nomination.decision_anchor != manifest_anchor:
        raise AnchorMismatchError(nomination.decision_anchor, manifest_anchor)

    # ★★★ DN-41 / AC-12.31 — a ranking from a REFUSED model is never actionable.
    #   Refused here, not trusted to the caller: PG-10's guarantee cannot rest on
    #   every caller remembering it.
    if actionable and getattr(nomination, "ranker_status", "rule") == "refused_informational":
        from src.decision.errors import RefusedRankerActionableError

        raise RefusedRankerActionableError(nomination.refused_gates)

    top = nomination.top
    verdict = NOMINATED_VERDICT
    outcomes: list[GateOutcome] = []
    for gv in sorted(gate_verdicts, key=lambda g: g.gate_id):
        status = _algebra_status(gv.status)
        verdict_after = apply_gate(NOMINATED_VERDICT, status)
        outcomes.append(GateOutcome(
            gate_id=gv.gate_id, status=gv.status, verdict_after=verdict_after,
            reason=gv.reason, produced_by_stub=gv.produced_by_stub,
        ))

    final = meet(NOMINATED_VERDICT, *(o.verdict_after for o in outcomes))

    # DN-1 / AC-12.11 — traceable to an input verdict.
    inputs = [NOMINATED_VERDICT, *(o.verdict_after for o in outcomes)]
    if final not in inputs:
        raise VerdictOriginatedError(final, inputs)
    # AC-12.2 / DEC.VERDICT.UPGRADE — algebraically impossible, so firing means
    # the meet was bypassed. The check is the evidence that it was not.
    for v in inputs:
        if conservatism(final) < conservatism(v):
            raise VerdictUpgradeError(
                f"composed {final!r} is more aggressive than input {v!r}; the meet "
                f"was bypassed (DN-5)"
            )
    if final == "SELL" and top.ticker.upper() not in {t.upper() for t in held_tickers}:
        raise SellNotHeldError(top.ticker)

    # ★★ DN-39 — `actionable: true` requires a COMPLETE risk pass AND a
    #   stability figure. ⚠ This is NOT D-05 blocking (INV-026 stands): it is
    #   D-12 declining to call something actionable when a declared input never
    #   ran, which is DN-11's absent-gate rule applied to the alert channel.
    if actionable:
        assert_actionable_inputs(alert_set, top_thesis_stability)

    # ⚠⚠ `PG-7.3` / `AC-6a.10` — refuse to BUILD the claim, do not soften it.
    # ★ `F6a` `D3`: *"if the claim is never built, no renderer can emit it."*
    #   Guarding only D-09 would leave a true-looking agreement in the decision
    #   record for `F5`, `F7b` and every future consumer to read.
    if claim_independent_agreement:
        assert_may_claim_independent_agreement(influenced_by=influenced_by)

    return Recommendation(
        as_of=as_of, run_id=run_id, decision_anchor=nomination.decision_anchor,
        candidate={"ticker": top.ticker, "rank": top.rank,
                   "ranked_quantity": top.ranked_quantity,
                   "horizon": nomination.nominating_horizon,
                   "ranked_by": _ranked_by(nomination)},
        verdict_final=final, verdict_nominated=NOMINATED_VERDICT,
        gates=tuple(outcomes), attribution=attribute(NOMINATED_VERDICT, outcomes),
        grade=_transport_grade(nomination, top, gate_verdicts),
        alerts=tuple(a.to_json_obj() for a in alert_set.alerts),
        alerts_status=alert_set.status,
        gate_roster_declared=declared, gate_roster_reported=reported,
        actionable=actionable, not_actionable_reason=not_actionable_reason,
        stubs=tuple(stubs),
        # ★ The status travels with the verdict, always — including when it is
        #   `"independent"`, because a field present only on the bad case is a
        #   field readers learn to ignore.
        concurrence=concurrence_label(influenced_by),
        # ★ DN-42 — the nominee's thesis reference, carried verbatim; nothing above reads it.
        thesis_ref=dict(thesis_ref) if thesis_ref else None,
    )


def _algebra_status(status: str) -> str:
    """Map a `CT-1.4` status onto the algebra's `S` (§5.3).

    ★ `NO_THESIS` composes as `VETO`, and that is DN-10 honoured rather than
    bypassed: the absence of a thesis is **not** the identity, so it must move the
    verdict. It keeps its own name in the artifact so the reader can tell "the
    analyst said no" from "there was no analyst".
    """
    return "VETO" if status == "NO_THESIS" else status


def _ranked_by(nomination) -> dict:
    """DN-40 / AC-12.30 — what ranked the pick, carried byte-identical (DN-26).

    ★ `kind` is an IDENTITY check against D-03's declared rule id, not a
    computation: QA-121 makes the rule's content hash the nomination's
    `model_artifact_id` whenever no promoted model ranked.
    """
    from src.quant import RANK_FORMULA_ID, rule_id

    artifact = nomination.model_artifact_id
    is_rule = artifact == rule_id()
    return {"artifact_id": artifact, "kind": "rule" if is_rule else "model",
            "formula_id": RANK_FORMULA_ID if is_rule else None,
            # ★ DN-41 / F12 D15 — carried byte-identical from the nomination.
            "status": getattr(nomination, "ranker_status", "rule"),
            "refused_gates": list(getattr(nomination, "refused_gates", ()) or ())}


def _transport_grade(nomination, top, gate_verdicts) -> dict:
    """DN-25 / DN-32 — a SUPERSET of the producer's grade keys, byte-identical.

    ⚠ **DN-26**: pass-through fields are never recomputed, rescaled or rounded in
    transit. A transported number that differs from its origin is a second,
    unowned computation.
    """
    out = {"ranked_quantity": top.ranked_quantity, "rank": top.rank, "z": top.z}
    for gv in gate_verdicts:
        if gv.gate_id == "thesis":
            out.update(gv.grade.to_json_obj())     # complete, not selective
    return out


def enforce_inv6(recommendations) -> None:
    """DN-22 / AC-12.20 — exactly one ACTIONABLE recommendation per run.

    ★ Informational output is permitted and explicitly marked non-actionable
    (INV-6 as amended). The invariant constrains the count of actionable
    recommendations, not the number of artifacts.
    """
    n = sum(1 for r in recommendations if r.actionable)
    if n > 1:
        raise MultipleActionableError(
            f"{n} actionable recommendations in one run; INV-6 permits exactly one "
            f"(DN-22). Discovery output must be marked actionable=false"
        )


def veto_rate(recommendations) -> float:
    """DN-17 / AC-12.19 — monitored and reported every run.

    ★ **Reading it needs no statistical power.** A rate near 0 % or 100 % is a
    STRUCTURAL finding — decoration, or a ranker and an analyst that
    systematically disagree — which is why DN-16 forbids tuning the gate on P&L
    while DN-17 still requires this number on every run.
    """
    recommendations = list(recommendations)
    if not recommendations:
        raise ValueError(
            "veto_rate over an empty window is undefined, not 0.0. A rate of zero "
            "means the gate never fired; no data means nobody looked (DN-17)"
        )
    vetoed = sum(1 for r in recommendations
                 if any(g.status in ("VETO", "NO_THESIS") for g in r.gates))
    return vetoed / len(recommendations)


def assert_actionable_inputs(alert_set, verdict_stability) -> None:
    """DN-39 / AC-12.29 — ★ **both, or the card is informational.**

    ⚠ *A partial run that emits three of five alerts has told the reader the
    other two categories are clear* (D-05 RK-30), and *a verdict may not reach a
    human as actionable before its stability figure exists* (RA-20, BS-28).
    """
    from src.decision.errors import DecisionError

    status = getattr(alert_set, "status", None)
    if status is None or not str(status).startswith("COMPLETE"):
        raise DecisionError(
            f"actionable=true with alerts_status={status!r}. ★ D-05 holds zero "
            f"authority and is not blocking this — D-12 is declining to call a "
            f"recommendation actionable when the risk desk never ran, because "
            f"silence from it reads as an all-clear (DN-39, RK-30, INV-026)")
    if not verdict_stability:
        raise DecisionError(
            "actionable=true with verdict_stability=null. ★ AC-1.8: the "
            "actionable pick carries a k>=3 stability result, and a verdict may "
            "not reach a human as actionable before that field exists "
            "(DN-39, RA-20, BS-28)")
