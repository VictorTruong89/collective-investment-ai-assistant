"""D-09 — AC-9.1…9.9, 9.15…9.29 (reliability classes, the card, anti-overconfidence).

Tier: data contract + golden/characterisation (deterministic bytes) + unit.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.decision import compose
from src.fundamental import GateVerdict, Grade, stub_gate_verdict
from src.quant import Candidate, Nomination
from src.reporting import (
    ArchiveMismatchError, BareConfidenceError, CLASSES, COMPUTATION,
    DeliveryFailedError, ExternalRefError, FACT, ForecastVoiceError,
    FreshnessUnstatedError, JUDGEMENT, KNOWN_DEFECTS, NoProducerError, RenderUnit,
    RenderingsDivergedError, ScriptPresentError, StabilityMissingError,
    UntaggedClassError, archive, assert_content_equivalent, assert_self_contained,
    build_card, build_message, deliver, delivery_id, digest, enforce, lint,
    render_html, render_markdown, send,
)
from src.risk import AlertSet, COMPLETE, Alert, unchecked
from src.shared.secrets import Secret

AS_OF = date(2026, 8, 23)


#: ★ DN-39 — the only shape an actionable card is now allowed to have.
STABILITY = {"k": 5, "modal": "BUY", "agreement": 0.6}


def recommendation(*, gate=None, actionable=False, alerts=None, reason="B3 stub",
                   stability=None):
    nom = Nomination(as_of=AS_OF, run_id="r", decision_anchor="open",
                     horizon_set=("production", 1), nominating_horizon="h1m",
                     universe_n=1, model_artifact_id="sha256:abc",
                     candidates=(Candidate("NVDA", 1, 0.1115, 0.425),),
                     contract_version="b3_minimal@v1", adj_as_of=AS_OF,
                     calendar_check_id="cal:test")
    return compose(
        nomination=nom, gate_verdicts=[gate or stub_gate_verdict("NVDA", AS_OF)],
        # ★ DN-39 — an actionable card requires a COMPLETE pass, so the
        #   actionable default differs from the informational one.
        alert_set=(alerts if alerts is not None
                   else AlertSet((), COMPLETE) if actionable
                   else AlertSet((), unchecked("no book (RK-29)"))),
        run_id="r", as_of=AS_OF, gate_roster_declared=("thesis",),
        manifest_anchor="open", actionable=actionable,
        not_actionable_reason=None if actionable else reason,
        top_thesis_stability=(stability if stability is not None
                              else STABILITY if actionable else None),
        stubs=({"domain": "D-01", "job": "thesis", "behaviour": "constant PASS",
                "replaced_at": "B4.4", "rule": "L3 BS-11"},),
    )


def graded(**kw):
    base = dict(verdict="BUY", conviction="Medium-High", stability_fraction=0.6, k=5,
                verdict_distribution={"BUY": 3, "HOLD": 2},
                confidence={"value": 0.62, "basis": "evidence_coverage",
                            "calibration": {"n": 40, "status": "calibrated"}})
    return GateVerdict("thesis", "NVDA", AS_OF, "PASS", "supported",
                       Grade(**{**base, **kw}))


# --------------------------------------------------------------------------- #
# §5 — reliability classes
# --------------------------------------------------------------------------- #

def test_ac_9_1_every_rendered_value_carries_a_class():
    """AC-9.1 — RP-1.

    ```
    "Position: 220 sh @ $91.40"  is a RECONCILED FACT.
    "Fair value: $412.80"        is a COMPUTATION with a live open defect.
    "Conviction: Medium-High"    is one draw from a stochastic process.

    A reader who cannot tell them apart will size the position off the least
    reliable one, because it is the one written in prose.
    ```
    """
    card = build_card(recommendation(), as_of=AS_OF)
    assert card.fields and all(f.reliability in CLASSES for f in card.fields)
    with pytest.raises(UntaggedClassError):
        RenderUnit("x", 1, "vibes", "D-03", AS_OF)


def test_ac_9_2_and_9_24d_class_is_never_signalled_by_colour_alone():
    """AC-9.2 / AC-9.24d — QP-1's surviving constraint.

    Colour inverts in dark mode and is invisible to a share of readers, so the
    **glyph and the text label** carry the class in every medium.
    """
    card = build_card(recommendation(), as_of=AS_OF)
    md, html = render_markdown(card), render_html(card)
    for unit in card.fields:
        assert unit.marker in md
        assert f"{unit.reliability}\">" in html or unit.marker.split()[0] in html


def test_ac_9_3_every_component_states_its_own_as_of():
    """AC-9.3 — RP-2. ★ Freshness is per component, never per card."""
    card = build_card(recommendation(), as_of=AS_OF)
    assert all(f.as_of is not None for f in card.fields)
    with pytest.raises(FreshnessUnstatedError):
        RenderUnit("x", 1, FACT, "D-11", None)


def test_ac_9_6_every_card_field_names_a_producing_domain():
    """AC-9.6 — RP-6/DC-1. ★ *A field D-09 could compute itself is one it must not.*"""
    card = build_card(recommendation(), as_of=AS_OF)
    assert all(f.source.startswith("D-") for f in card.fields)
    with pytest.raises(NoProducerError):
        RenderUnit("x", 1, COMPUTATION, "", AS_OF)


def test_ac_9_5_the_known_defect_register_is_available_for_disclosure():
    """AC-9.5 — RP-5. ⚠ Uncomfortable and correct.

    *The alternative is a card that prints a fair value the project's own defect
    log says is overstated in proportion to leverage.* B3 renders no fair value,
    so the register is asserted rather than exercised — and it is asserted so
    the disclosure path exists before the first fair value does.
    """
    assert "D-19" in KNOWN_DEFECTS and "net-debt" in KNOWN_DEFECTS["D-19"]
    unit = RenderUnit("fair_value", [380, 445], COMPUTATION, "D-02", AS_OF,
                      known_defects=("D-19",))
    assert unit.known_defects == ("D-19",)
    with pytest.raises(ValueError, match="unknown defect"):
        RenderUnit("x", 1, COMPUTATION, "D-02", AS_OF, known_defects=("D-99",))


# --------------------------------------------------------------------------- #
# §6/§7 — the card, and fail loud
# --------------------------------------------------------------------------- #

def test_ac_9_7_rendering_may_soften_and_never_escalate():
    """AC-9.7 — RP-7/DC-5/P3. Checked, because the renderer is the last chance."""
    from src.reporting.errors import VerdictEscalatedError
    rec = recommendation()
    bad = rec.__class__(**{**{f: getattr(rec, f) for f in rec.__slots__},
                           "verdict_final": "BUY", "verdict_nominated": "SELL"})
    with pytest.raises(VerdictEscalatedError, match="MORE aggressive"):
        build_card(bad, as_of=AS_OF)


def test_ac_9_15_verdict_stability_renders_verbatim():
    """AC-9.15 — RP-13/RA-20. ★ *The single most effective anti-overconfidence
    device available* — and `stability_fraction` alone cannot produce it."""
    card = build_card(recommendation(gate=graded(), actionable=True), as_of=AS_OF)
    assert card.field("stability").value == "⚠ unstable: 3 BUY / 2 HOLD"

    stable = build_card(recommendation(gate=graded(k=5, verdict_distribution={"BUY": 5},
                                                   stability_fraction=1.0),
                                       actionable=True), as_of=AS_OF)
    assert stable.field("stability").value == "stable 5/5"


def test_ac_9_15_an_actionable_verdict_with_no_stability_raises():
    """RP-13 / `RPT.STABILITY.MISSING` — and ★ **L3 BS-28 is what it enforces.**

    *A verdict rendered without its stability figure is D-15 with better
    plumbing.* The B3 card escapes only by being non-actionable (BS-33).
    """
    # ★ Hand-built, because DN-39 makes D-12 refuse this pairing first. The
    #   subject here is **D-09's own backstop**: a card that reached the
    #   renderer actionable-but-unmeasured is still refused, so the check does
    #   not depend on D-12 having caught it upstream.
    import dataclasses

    unmeasured = dataclasses.replace(recommendation(actionable=False),
                                     actionable=True, not_actionable_reason=None)
    with pytest.raises(StabilityMissingError, match="better plumbing"):
        build_card(unmeasured, as_of=AS_OF)

    card = build_card(recommendation(actionable=False), as_of=AS_OF)
    assert card.field("stability").value == "not applicable — no model was run"


def test_ac_9_16_confidence_renders_with_a_referent_or_not_yet_calibrated():
    """AC-9.16 — RP-14/RA-21. ⚠ Never a bare number."""
    uncal = graded(confidence={"value": 0.62, "basis": "evidence_coverage",
                               "calibration": {"n": 3, "status": "not_yet_calibrated"}})
    card = build_card(recommendation(gate=uncal, actionable=True), as_of=AS_OF)
    assert card.field("confidence").value == "not yet calibrated (N=3)"

    bare = graded(confidence={"value": 0.62})
    with pytest.raises(BareConfidenceError, match="empirical referent"):
        build_card(recommendation(gate=bare, actionable=True), as_of=AS_OF)


def test_ac_9_17_the_falsifier_renders_above_the_verdict():
    """AC-9.17 — RP-15. ★ *Ordering is an argument.*"""
    card = build_card(recommendation(), as_of=AS_OF)
    md = render_markdown(card)
    assert md.index("What would prove this wrong") < md.index("| verdict |")


def test_ac_9_19_the_data_gap_block_is_present_and_non_collapsible():
    """AC-9.19 — RP-17. *What the analyst wanted and did not have is part of the
    finding.*"""
    card = build_card(recommendation(), as_of=AS_OF)
    assert card.data_gaps
    assert "## Data gaps" in render_markdown(card)
    assert "Data gaps" in render_html(card)


def test_ac_9_20_forecast_voice_blocks_the_render():
    """AC-9.20 — RP-18/RA-26. Deterministic, cheap, and it blocks."""
    assert lint({"thesis": "margins will clearly expand"}).blocking
    with pytest.raises(ForecastVoiceError, match="assert certainty"):
        enforce({"thesis": "the cycle is set to turn"})
    assert not lint({"thesis": "margins may expand if the cycle turns"}).blocking


def test_ac_9_21_narrative_sections_respect_their_length_caps():
    """AC-9.21 — RP-19. ⚠ WARNING, not blocking: length is a soft signal."""
    report = lint({"thesis": "x" * 5000})
    assert report.over_length and not report.blocking


# --------------------------------------------------------------------------- #
# §9 — delivery
# --------------------------------------------------------------------------- #

def test_ac_9_24a_the_html_fetches_nothing():
    """AC-9.24a — RP-31, asserted on the EMITTED BYTES, not on intent.

    ★ *An artifact that needs a live server is not viewable later, and later is
    exactly when a decision gets audited* (P6).
    """
    html = render_html(build_card(recommendation(), as_of=AS_OF))
    assert_self_contained(html)
    for bad in ('<img src="https://x/y.png">', "<style>@import url(http://x)</style>",
                '<link href="//cdn/x.css">'):
        with pytest.raises(ExternalRefError):
            assert_self_contained(bad)


def test_ac_9_24b_the_html_contains_no_script():
    """AC-9.24b — RP-34. Inline handlers count."""
    with pytest.raises(ScriptPresentError):
        assert_self_contained("<script>alert(1)</script>")
    with pytest.raises(ScriptPresentError):
        assert_self_contained('<div onclick="x()">')


def test_ac_9_24c_html_and_markdown_carry_the_same_class_tagged_fields():
    """AC-9.24c — RP-32. *A value present in one rendering and absent in another
    is a defect*, as is a value that differs."""
    card = build_card(recommendation(), as_of=AS_OF)
    html, md = render_html(card), render_markdown(card)
    assert_content_equivalent(html, md)
    with pytest.raises(RenderingsDivergedError):
        assert_content_equivalent(html, md.replace("| verdict | BUY |",
                                                   "| verdict | SELL |"))


def test_ac_9_27_rendering_is_deterministic():
    """AC-9.27 — RP-28. Without it there is no golden test and no evidence of
    what was seen."""
    card = build_card(recommendation(), as_of=AS_OF)
    assert render_html(card) == render_html(card)
    assert render_markdown(card) == render_markdown(card)


def test_ac_9_24_archived_bytes_equal_delivered_bytes(tmp_path):
    """AC-9.24 — RP-24. *If they can differ, the archive is not evidence.*"""
    card = build_card(recommendation(), as_of=AS_OF)
    renderings = {"a.html": render_html(card).encode(),
                  "a.md": render_markdown(card).encode()}
    paths = archive(renderings, tmp_path, "d1")
    for name, payload in renderings.items():
        assert paths[name].read_bytes() == payload


def test_ac_9_25_a_delivery_failure_raises(tmp_path):
    """AC-9.25 — RP-23. ★ *An email that did not arrive is indistinguishable from
    a run that never happened.*"""
    class Exploding:
        def send_message(self, msg):
            raise OSError("smtp refused")

    card = build_card(recommendation(), as_of=AS_OF)
    with pytest.raises(DeliveryFailedError, match="never happened"):
        deliver(card, {"a.md": b"x"}, sender="a@b.c", recipient="d@e.f",
                user=Secret("GMAIL_SMTP_USER", "a@b.c"),
                password=Secret("GMAIL_APP_PASSWORD", "pw"),
                archive_root=tmp_path, transport=Exploding())


def test_ac_9_22_delivery_is_idempotent_and_recorded(tmp_path):
    """RP-22 — *a silent duplicate is how a stale card gets acted on twice.*"""
    class Recorder:
        def __init__(self): self.sent = []
        def send_message(self, msg): self.sent.append(msg)

    card = build_card(recommendation(), as_of=AS_OF)
    renderings = {"a.md": render_markdown(card).encode()}
    t = Recorder()
    kw = dict(sender="a@b.c", recipient="d@e.f",
              user=Secret("GMAIL_SMTP_USER", "a@b.c"),
              password=Secret("GMAIL_APP_PASSWORD", "pw"),
              archive_root=tmp_path, transport=t)
    first = deliver(card, renderings, **kw)
    second = deliver(card, renderings, **kw)
    assert first.delivery_id == second.delivery_id, "identical content, identical id"
    assert first.outcome == "SENT" and len(t.sent) == 2


def test_the_password_never_reaches_an_error_message(tmp_path):
    """DE-8's rule applied to SMTP — enforced by the Secret wrapper."""
    class Exploding:
        def send_message(self, msg):
            raise OSError("smtp refused")

    card = build_card(recommendation(), as_of=AS_OF)
    with pytest.raises(DeliveryFailedError) as exc:
        deliver(card, {"a.md": b"x"}, sender="a@b.c", recipient="d@e.f",
                user=Secret("GMAIL_SMTP_USER", "a@b.c"),
                password=Secret("GMAIL_APP_PASSWORD", "hunter2"),
                archive_root=tmp_path, transport=Exploding())
    assert "hunter2" not in str(exc.value)
    with pytest.raises(TypeError, match="Secret-wrapped"):
        send(build_message(card, {}, sender="a@b.c", recipient="d@e.f"),
             user="a@b.c", password="pw")


def test_ac_9_29_and_rp_47_an_unchecked_risk_pass_renders_as_itself():
    """AC-9.29 — ★ RP-47/DN-38, added building B3.

    ⚠ **An empty alert list is never rendered as a clean bill of health.**
    D-05's silence is a claim (RK-30), and a card that cannot distinguish
    *"nothing found"* from *"nobody looked"* makes it on the risk desk's behalf.
    """
    card = build_card(recommendation(), as_of=AS_OF)
    assert card.alerts_status.startswith("UNCHECKED: ")
    for text in (render_markdown(card), render_html(card)):
        assert "UNCHECKED" in text
    assert any("risk:" in g for g in card.data_gaps)

    clean = build_card(
        recommendation(gate=graded(), actionable=True,
                       alerts=AlertSet((Alert("D-05", 2, "theme 61.7%", AS_OF),),
                                       COMPLETE)),
        as_of=AS_OF)
    assert clean.alerts_status == COMPLETE
    assert "theme 61.7%" in render_markdown(clean), "RP-46 — never suppressed"


def test_ac_9_28_reporting_imports_no_gateway_and_writes_to_nothing():
    """AC-9.28 — RP-29/RP-30, ST-5/ST-9. Structural, not stylistic."""
    from tests_src.architecture import rp_30, scan, st_5
    graph = scan()
    assert st_5(graph) == [] and rp_30(graph) == []


def test_the_b3_card_says_not_actionable_above_everything_else():
    """★ L3 BS-33 — the skeleton walks without claiming to be a recommendation.

    The reason is asserted from the composition root's own constant, so the
    card cannot drift from the rule it is standing on.
    """
    from src.orchestration.jobs.b3_run import NOT_ACTIONABLE_REASON

    card = build_card(recommendation(reason=NOT_ACTIONABLE_REASON), as_of=AS_OF)
    md = render_markdown(card)
    assert card.actionable is False
    assert md.index("NOT ACTIONABLE") < md.index("What would prove this wrong")
    # ⚠ No longer `"B4.5" in md` — see test_b3_skeleton.py. The card must name
    #   the rule and the missing inputs, not a milestone that has passed.
    assert "BS-28/BS-33" in md and "stability" in md
