"""The Discipline Card — §6, §8Z (RP-6…RP-8, RP-13…RP-17, RP-43…RP-47).

★ **What D-09 renders is `CT-12.1 Recommendation`, and every field traces to it**
(§8Z). **RP-43: D-09 never re-derives any of it** — a card field computed inside
the renderer is a second, unowned computation.

⚠ **RP-13 and L3 BS-33.** A verdict on the *actionable* path with no stability is
`RPT.STABILITY.MISSING`. B3's card carries a stub gate and therefore no
stability, so it renders **`actionable: false`** and the check does not fire.
That is not a loophole — it is BS-28's boundary made operational: *the first
actionable card is B4.5's.*
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.reporting.errors import (
    BareConfidenceError,
    StabilityMissingError,
    VerdictEscalatedError,
)
from src.reporting.render.classes import (
    COMPUTATION,
    FACT,
    JUDGEMENT,
    RELAYED_JUDGEMENT,
    RenderUnit,
)
from src.reporting.render.lint import enforce

#: Ordering is an argument (**RP-15**): the falsifier renders ABOVE the verdict.
#: *What would prove this wrong, before what we think.*
#: ⚠ `thesis_source` sits IMMEDIATELY AFTER `analyst_verdict` (`F9` `AC-F9.6`).
#: ★ It qualifies that verdict and nothing else: how far the transport can be
#: trusted is unreadable once separated from the judgement it applies to. Placing
#: it lower — beside `confidence`, say — would let a reader take the analyst's
#: verdict at face value and meet its provenance a screen later.
FIELD_ORDER = ("falsifier", "verdict", "analyst_verdict", "thesis_source",
               "stability", "confidence",
               "rank", "ranked_quantity", "alerts", "deferral")

#: D-12's conservatism order, restated for the escalation check only. D-09 does
#: not compose — it verifies that what it was handed was not made *more*
#: aggressive in transit (RP-7, DC-5).
_CONSERVATISM = {"BUY": 0, "HOLD": 1, "SELL": 2}


@dataclass(frozen=True, slots=True)
class DisciplineCard:
    """CT-9.1 — the one-screen pre-commitment contract."""

    ticker: str
    as_of: date
    fields: tuple[RenderUnit, ...]
    falsifier: str
    data_gaps: tuple[str, ...]
    alerts_status: str
    actionable: bool
    not_actionable_reason: str | None
    degraded: bool = False
    stubs: tuple[dict, ...] = ()

    def field(self, name: str) -> RenderUnit:
        for f in self.fields:
            if f.field == name:
                return f
        raise KeyError(f"card has no field {name!r}")

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(f.field for f in self.fields)

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "as_of": self.as_of.isoformat(),
            "fields": {f.field: f.to_json_obj() for f in self.fields},
            "falsifier": self.falsifier, "data_gaps": list(self.data_gaps),
            "alerts_status": self.alerts_status,
            "actionable": self.actionable,
            "not_actionable_reason": self.not_actionable_reason,
            "degraded": self.degraded, "stubs": [dict(s) for s in self.stubs],
        }


def build_card(recommendation, *, as_of: date) -> DisciplineCard:
    """`CT-12.1` -> `CT-9.1`. Renders; re-derives nothing (RP-43)."""
    rec = recommendation
    grade = rec.grade
    units: list[RenderUnit] = []

    # RP-7 / DC-5 — may soften, never escalate. Checked rather than trusted: the
    # renderer is the last place a verdict could be quietly improved.
    if _CONSERVATISM[rec.verdict_final] < _CONSERVATISM[rec.verdict_nominated]:
        raise VerdictEscalatedError(
            f"rendering {rec.verdict_final!r} against a nominated "
            f"{rec.verdict_nominated!r} would make the verdict MORE aggressive "
            f"(RP-7, DC-5, P3)"
        )

    units.append(RenderUnit(
        field="verdict", value=rec.verdict_final, reliability=COMPUTATION,
        source="D-12", as_of=as_of,
        note=("composed, never originated (DN-1); softened from "
              f"{rec.verdict_nominated}" if rec.was_downgraded else "composed (DN-1)"),
    ))

    # ★ F9 AC-F9.6 — WHICH SOURCE produced the thesis, and how far to trust the
    # transport. ⚠ Read once here so the verdict unit below and the source unit
    # cannot disagree about it.
    thesis_variant = _thesis_variant(rec)
    analyst_class = (RELAYED_JUDGEMENT if thesis_variant != "api" and rec.thesis_ref
                     else JUDGEMENT)

    # ★ §8Z / RP-8 — the ANALYST's own verdict renders BESIDE the composed one,
    # never instead of it. Divergence is information, not a layout problem.
    if grade.get("verdict") is not None:
        units.append(RenderUnit(
            field="analyst_verdict", value=grade["verdict"],
            reliability=analyst_class,
            source="D-01", as_of=as_of,
            note="the analyst's own verdict, shown beside the composed one (RP-8)",
        ))

    # ★★ F9 `AC-F9.6` — the card states its source, on BOTH paths.
    # ⚠ A provenance field that appeared only on the relay path would teach a
    # reader that its ABSENCE means "fine", and then a missing provenance and an
    # API thesis look identical (`AP-2`, `DC-1`).
    if rec.thesis_ref:
        units.append(RenderUnit(
            field="thesis_source", value=thesis_variant,
            # ⚠ `source` names the producing DOMAIN, never a spec id. D-09's own
            # D-09's OWN `AC-9.6` (a different AC from F9's — DX-44)
            # asserts every field starts with `D-` (`RP-6`/`DC-1`:
            # *a field D-09 could compute itself is one it must not*), and the
            # thesis — whichever transport carried it — is D-01's.
            # ★ Caught by that existing test on the first run of this code.
            reliability=analyst_class, source="D-01", as_of=as_of,
            note=("relayed through a human transport: the evidence bundle does "
                  "not exist here and the numbers are mostly unverifiable "
                  "against data we hold (RP-48, RA-118)"
                  if analyst_class is RELAYED_JUDGEMENT else
                  "authored through the Anthropic API, the default source (QR-20)"),
        ))

    units.append(_stability_unit(grade, rec, as_of))
    units.append(_confidence_unit(grade, rec, as_of))

    units.append(RenderUnit(
        field="rank", value=rec.candidate["rank"], reliability=COMPUTATION,
        source="D-03", as_of=as_of))
    units.append(RenderUnit(
        field="ranked_quantity", value=rec.candidate["ranked_quantity"],
        reliability=COMPUTATION, source="D-03", as_of=as_of,
        note="denormalised 21-session return, z * sigma * sqrt(h) (QA-58)"))

    # RP-46 / RP-47 — alerts are never suppressed, and their STATUS renders.
    units.append(RenderUnit(
        field="alerts", value=[a["text"] for a in rec.alerts], reliability=FACT,
        source="D-05", as_of=as_of, note=rec.alerts_status))

    falsifier = _falsifier_text(rec)
    enforce({"falsifier": falsifier,
             **{f"reason:{g.gate_id}": g.reason for g in rec.gates}})

    return DisciplineCard(
        ticker=rec.candidate["ticker"], as_of=as_of,
        fields=tuple(sorted(units, key=lambda u: FIELD_ORDER.index(u.field))),
        falsifier=falsifier,
        data_gaps=_data_gaps(rec),
        alerts_status=rec.alerts_status,
        actionable=rec.actionable,
        not_actionable_reason=rec.not_actionable_reason,
        stubs=rec.stubs,
    )


def _stability_unit(grade, rec, as_of) -> RenderUnit:
    """RP-13 — verdict stability renders VERBATIM: "stable 5/5" or "BUY 3 / HOLD 2".

    ★ **The single most effective anti-overconfidence device available** (RA-20)
    — quantitative, honest, and impossible to skim past. ⚠ `stability_fraction`
    alone cannot produce it: 0.6 is equally 3/5, 6/10 or 12/20, which is why
    `k` and `verdict_distribution` are both required (RA-51a).
    """
    k, dist = grade.get("k"), grade.get("verdict_distribution")
    if k is None or dist is None:
        if rec.actionable:
            raise StabilityMissingError(
                "the actionable verdict carries no k-run stability. A verdict "
                "rendered without its stability figure is D-15 with better plumbing "
                "(RP-13, RA-20, L3 BS-28)"
            )
        # BS-33/BS-34 — absence rendered AS absence, never as a fabricated 1/1.
        return RenderUnit(
            field="stability", value="not applicable — no model was run",
            reliability=JUDGEMENT, source="D-01", as_of=as_of,
            note="stub gate (L3 BS-34): no k-run probe exists, so none is claimed")
    parts = " / ".join(f"{v} {n}" for n, v in sorted(dist.items()))
    modal = max(dist.items(), key=lambda kv: kv[1])
    text = (f"stable {modal[1]}/{k}" if modal[1] == k
            else f"⚠ unstable: {parts}")
    return RenderUnit(field="stability", value=text, reliability=JUDGEMENT,
                      source="D-01", as_of=as_of)


def _confidence_unit(grade, rec, as_of) -> RenderUnit:
    """RP-14 / RA-21 — with an empirical referent, or "not yet calibrated (N=…)".

    ⚠ **Never a bare number.** A confidence with nothing behind it is fabricated
    precision the reader cannot detect.
    """
    conf = grade.get("confidence")
    if conf is None:
        return RenderUnit(field="confidence", value="not applicable — no model was run",
                          reliability=JUDGEMENT, source="D-01", as_of=as_of,
                          note="stub gate (L3 BS-34)")
    calibration = conf.get("calibration") or {}
    if conf.get("basis") == "not_measured":
        # ⏸ AB-1 — ★ **a declination, not a number.** RA-30 gives a monitor one
        #   way to decline and RA-136 added `not_measurable` for the case where
        #   the figure is not merely late but uncomputed. ⚠ Rendering `0.0` here
        #   would be fabricated precision the reader cannot detect (RP-14).
        value = f"not measured — {conf.get('reason', 'no reason given')}"
    elif calibration.get("status") == "not_yet_calibrated":
        value = f"not yet calibrated (N={calibration.get('n', 0)})"
    elif conf.get("basis"):
        value = f"{conf['value']} (basis: {conf['basis']})"
    else:
        raise BareConfidenceError(
            f"confidence {conf.get('value')!r} has no empirical referent and no "
            f"'not yet calibrated' marker (RP-14, RA-21)"
        )
    return RenderUnit(field="confidence", value=value, reliability=JUDGEMENT,
                      source="D-01", as_of=as_of)


def _thesis_variant(rec) -> str:
    """`AC-F9.6` — which `thesis_source` variant authored this thesis.

    ⚠⚠ **`"unknown"`, never `"api"`, when provenance is absent.** The tempting
    default is `api`, because `QR-20` makes it the common case — and that would
    render an unprovenanced thesis as the **most** trustworthy source available.
    ★ A defaulting rule must fail toward the weaker claim (`P5`, `AP-2`), so an
    unknown source also renders at `RELAYED_JUDGEMENT`, the lowest assurance
    class (`ASSURANCE_ORDER`).
    """
    if not rec.thesis_ref:
        return "none"
    return (rec.thesis_ref.get("provenance") or {}).get("variant") or "unknown"


def _falsifier_text(rec) -> str:
    """RP-15 — what would prove this wrong, rendered above the verdict."""
    stub = [g for g in rec.gates if g.produced_by_stub]
    if stub:
        return (
            "No falsification condition exists: the thesis gate is a walking-skeleton "
            f"stub replaced at {stub[0].produced_by_stub} (L3 BS-11). "
            "This card states no thesis and can therefore be proven wrong by nothing "
            "— which is why it is not actionable."
        )
    return rec.thesis_ref.get("falsifier", "") if rec.thesis_ref else ""


def _data_gaps(rec) -> tuple[str, ...]:
    """RP-17 — the data-gap block is MANDATORY and non-collapsible.

    *What the analyst wanted and did not have is part of the finding.* At B3 the
    gaps are structural rather than analytical, and listing them is the point.
    """
    gaps = []
    for g in rec.gates:
        if g.produced_by_stub:
            gaps.append(f"gate {g.gate_id!r} is a stub — replaced at {g.produced_by_stub}")
    if rec.alerts_status != "COMPLETE":
        gaps.append(f"risk: {rec.alerts_status}")
    if rec.grade.get("k") is None:
        gaps.append("no k-run verdict stability (RA-20) — no model was run")
    return tuple(gaps)
