"""D-01 B4.5 — AC-1.8, 1.9, 1.16, 1.17, 1.19–1.26, 1.25a, 1.28, 1.28a, 1.72.

★ **L3 §3A.4's done-when:** *the monitor report contains **every** `RM-n` as a
value or an explicit `not_yet_calibrated`; **a verdict cannot render without its
stability figure**.*

★★ **And this is the slice BS-28 was waiting for** — *B4.4 may be merged; its
output may not be delivered until B4.5 lands.*

Tier: unit + invariant/property + integration (constitution §4).
"""

from __future__ import annotations

import pytest

from src.fundamental import (
    Baseline, CADENCE, FAIL, FORECAST_VOICE, K_STAB, LENGTH_CAPS, MonitorReport,
    MonitorResult, NOT_MEASURABLE, NOT_YET_CALIBRATED, OK, PERTURBATION, RM_IDS,
    SAMPLING, WARN, forecast_voice_violations, length_violations, not_measurable,
    not_yet_calibrated, rm1_perturbation_probe, rm1_result, rm1_sampling_probe,
    rm2_scorecard_dispersion, rm3_numeric_spread, rm4_regression, rm4_result,
    rm5_rebaseline_required, rm6_verdict_base_rate, rm7_dimension_dispersion,
    rm8_seat_disagreement, rm9_theme_skew, rm12_calibration_curve,
    rm13_falsifier_vs_abandonment, rm14_action_correlation, rm15_lint_and_uncited,
    rm16_thesis_error_correlation,
)


def full_report(**overrides):
    rows = {rm: not_yet_calibrated(rm) for rm in RM_IDS}
    rows.update(overrides)
    return MonitorReport(run_id="run-1", results=tuple(rows.values()))


# --------------------------------------------------------------------------- #
# AC-1.28 / AC-1.28a — the report is complete, and it can say "never"
# --------------------------------------------------------------------------- #

def test_ac_1_28_every_rm_appears_or_the_report_is_a_defect():
    """AC-1.28 — RA-30. ★ B4.5's done-when, first clause.

    ⚠ *A missing monitor reads as a passing one* — DE-35's defect applied to
    metrics.
    """
    report = full_report()
    assert len(report.results) == 16
    assert {r.rm_id for r in report.results} == set(RM_IDS)

    partial = tuple(not_yet_calibrated(rm) for rm in RM_IDS[:-1])
    with pytest.raises(ValueError, match="omits \\['RM-16'\\]"):
        MonitorReport(run_id="r", results=partial)


def test_ac_1_28a_not_measurable_is_distinct_from_not_yet_calibrated():
    """AC-1.28a — ★★ **RA-136**, the defect this slice found.

    ```
    "not yet calibrated (N=…)" PROMISES THE NUMBER IS COMING.

    RM-1's sampling half can NEVER be computed on this tier — claude-opus-5
    rejects temperature (GW-8a) — so reporting it that way tells a reader to
    wait for a number that will never arrive.
    ```
    """
    later = not_yet_calibrated("RM-12", n=3)
    never = rm1_sampling_probe()

    assert later.status == NOT_YET_CALIBRATED
    assert later.renders_as == "not yet calibrated (N=3)"
    assert never.status == NOT_MEASURABLE
    assert never.renders_as.startswith("not measurable — ")
    assert "temperature" in never.reason and "GW-10" in never.reason


def test_not_measurable_without_a_reason_is_refused():
    """RA-136 — ⚠ *without one it is indistinguishable from not_yet_calibrated,
    and the difference is whether a reader should ever expect a number.*"""
    with pytest.raises(ValueError, match="requires a reason"):
        not_measurable("RM-1", "")


def test_a_status_with_no_value_is_a_placeholder():
    """RA-30 — *never a placeholder value and never silence.*"""
    with pytest.raises(ValueError, match="placeholder"):
        MonitorResult("RM-6", OK, value=None)


def test_the_report_records_each_monitors_cadence():
    """§7.4 — so a reader can tell *"absent because it runs weekly"* from
    *"absent because nobody wired it"*."""
    assert set(CADENCE) == set(RM_IDS)
    assert full_report().get("RM-12").to_json_obj()["cadence"] == "monthly"


# --------------------------------------------------------------------------- #
# AC-1.8 / AC-1.19 — RM-1, the perturbation probe
# --------------------------------------------------------------------------- #

def test_ac_1_8_the_probe_requires_k_at_least_three():
    """AC-1.8 — RM-1. ★ *The actionable pick is never exempt, because it is the
    only output anyone trades on.*"""
    assert rm1_perturbation_probe(["BUY"] * K_STAB).k == K_STAB
    with pytest.raises(ValueError, match="never exempt"):
        rm1_perturbation_probe(["BUY", "BUY"])


def test_ac_1_19_stability_renders_verbatim_including_when_unstable():
    """AC-1.19 — RA-20.

    ★ **The single most effective anti-overconfidence device available** —
    quantitative, honest, and impossible to skim past. *A reader who sees 3/5
    sizes the position differently, and should.*
    """
    assert rm1_perturbation_probe(["BUY"] * 5).renders_as == "stable 5/5"
    shaky = rm1_perturbation_probe(["BUY", "BUY", "BUY", "HOLD", "HOLD"])
    assert shaky.renders_as == "⚠ unstable: 3 BUY / 2 HOLD"
    assert shaky.agreement == pytest.approx(0.6) and shaky.modal == "BUY"


def test_the_distribution_is_what_renders_not_the_fraction():
    """RA-51a — ⚠ *0.6 is equally 3/5, 6/10 or 12/20*, so the ratio alone cannot
    produce "BUY 3 / HOLD 2"."""
    a = rm1_perturbation_probe(["BUY"] * 3 + ["HOLD"] * 2)
    b = rm1_perturbation_probe(["BUY"] * 6 + ["HOLD"] * 4)
    assert a.agreement == b.agreement
    assert a.renders_as != b.renders_as


def test_ra_61_the_probe_perturbs_the_input_and_names_what_it_varied():
    """RA-61/RA-62 — ★ *perturbing the INPUT measures robustness to things that
    should not matter*; resampling measures the decoder."""
    from src.fundamental import PERTURBATIONS

    probe = rm1_perturbation_probe(["BUY"] * 3)
    assert probe.probe == PERTURBATION
    assert probe.perturbations_applied == PERTURBATIONS
    assert set(PERTURBATIONS) == {"option_order", "evidence_order", "prompt_paraphrase"}


def test_rm1_colours_the_row_by_agreement():
    """The monitor row, not the card. RA-20 publishes the fraction verbatim
    either way."""
    assert rm1_result(rm1_perturbation_probe(["BUY"] * 5)).status == OK
    assert rm1_result(rm1_perturbation_probe(["BUY"] * 3 + ["HOLD"] * 2)).status == WARN

    # ⚠ Agreement is over the MODAL verdict, so a 2/3 split is still 0.6. Falling
    # below 0.5 requires genuine THREE-WAY disagreement — which is worth knowing:
    # on a two-verdict split, k=5 can never reach the FAIL band.
    assert rm1_perturbation_probe(["BUY"] * 2 + ["HOLD"] * 3).agreement == 0.6
    three_way = rm1_perturbation_probe(["BUY", "BUY", "HOLD", "HOLD", "SELL"])
    assert three_way.agreement == pytest.approx(0.4)
    assert rm1_result(three_way).status == FAIL


def test_rm2_flags_a_dimension_that_moves_two_levels():
    """RM-2 — ★ *a dimension that moves ≥2 levels between identical runs is not
    measuring anything*, and **RA-34 says the fix is in the RUBRIC**."""
    steady = rm2_scorecard_dispersion([{"moat_durability": 3}] * 3)
    assert steady.status == OK and steady.value == {"moat_durability": 0}

    wobbly = rm2_scorecard_dispersion([{"moat_durability": 1},
                                       {"moat_durability": 3},
                                       {"moat_durability": 2}])
    assert wobbly.status == FAIL and wobbly.value == {"moat_durability": 2}
    assert rm2_scorecard_dispersion([{"moat_durability": 3}]).status == NOT_YET_CALIBRATED


def test_rm3_reports_the_coefficient_of_variation():
    """RM-3 — ★ *wide spread ⇒ the numbers are decoration.*"""
    tight = rm3_numeric_spread({"stop": [100.0, 101.0, 99.0]})
    assert tight.status == OK
    assert rm3_numeric_spread({"stop": [50.0, 100.0, 150.0]}).status == WARN


# --------------------------------------------------------------------------- #
# AC-1.9 — RM-4's release gate
# --------------------------------------------------------------------------- #

def test_ac_1_9_a_prompt_change_without_a_regression_run_blocks_release():
    """AC-1.9 — RM-4. ★ *A wording change that flips 30 % of verdicts is a change
    of policy.*"""
    assert rm4_result(None).status == NOT_YET_CALIBRATED, "no run happened"

    before = Baseline("J-16", "v1", {"sha256:a": "BUY", "sha256:b": "HOLD",
                                     "sha256:c": "BUY", "sha256:d": "HOLD"})
    same = Baseline("J-16", "v2", dict(before.verdicts))
    assert not rm4_regression(before, same).blocks_release

    flipped = Baseline("J-16", "v2", {"sha256:a": "HOLD", "sha256:b": "HOLD",
                                      "sha256:c": "HOLD", "sha256:d": "HOLD"})
    result = rm4_regression(before, flipped)
    assert result.flip_rate == 0.5 and result.blocks_release
    assert rm4_result(result).status == FAIL


def test_rm4_needs_a_pinned_bundle_set():
    """⚠ *A changed sample would read as a changed policy.*"""
    a = Baseline("J-16", "v1", {"sha256:a": "BUY"})
    b = Baseline("J-16", "v2", {"sha256:z": "BUY"})
    with pytest.raises(ValueError, match="share no bundle_hash"):
        rm4_regression(a, b)
    with pytest.raises(ValueError, match="against itself"):
        rm4_regression(a, Baseline("J-16", "v1", {"sha256:a": "HOLD"}))
    with pytest.raises(ValueError, match="one prompt across versions"):
        rm4_regression(a, Baseline("J-03", "v2", {"sha256:a": "BUY"}))


def test_rm5_fires_on_an_effort_change_not_only_a_tier_change():
    """★★ **GW-9b / RA-60a — the amendment's most consequential clause.**

    ⚠ RM-5 as written keys on an INV-8 **tier** change, and `high → xhigh` is not
    one — *it would move every deep-tier output with nothing firing*, which is
    **worse than the unset temperature GW-9 was written to fix**.
    """
    base = {"model_id": "claude-opus-5", "effort": "high", "thinking_mode": "adaptive"}
    assert rm5_rebaseline_required(base, base).status == OK

    effort = rm5_rebaseline_required(base, {**base, "effort": "xhigh"})
    assert effort.status == FAIL and effort.value["changed"] == ["effort"]

    model = rm5_rebaseline_required(base, {**base, "model_id": "claude-opus-6"})
    assert model.status == FAIL


# --------------------------------------------------------------------------- #
# AC-1.16 / AC-1.17 — the weekly bias set
# --------------------------------------------------------------------------- #

def test_ac_1_16_base_rate_dispersion_and_theme_skew_are_computed():
    """AC-1.16 — RM-6, RM-7, RM-9."""
    verdicts = ["BUY"] * 18 + ["HOLD"] * 4
    assert rm6_verdict_base_rate(verdicts).status == WARN, "an analyst that mostly BUYs"
    assert rm6_verdict_base_rate(["BUY"] * 8 + ["HOLD"] * 14).status == OK
    assert rm6_verdict_base_rate(["BUY"] * 5).status == NOT_YET_CALIBRATED

    degenerate = rm7_dimension_dispersion({"moat_durability": [3] * 25})
    assert degenerate.status == WARN
    assert degenerate.value["degenerate"] == ["moat_durability"]
    assert rm7_dimension_dispersion({"moat_durability": [1, 2, 3, 4] * 6}).status == OK

    skewed = rm9_theme_skew({"ai_semiconductor": ["BUY"] * 20,
                             "other": ["HOLD"] * 5}, universe_base_rate=0.4)
    assert skewed.status == WARN and skewed.value["ai_semiconductor"] > 0


def test_ac_1_17_seat_disagreement_reads_BACKWARDS():
    """AC-1.17 — ★★ RM-8, **the INV-014 health check**.

    ```
    INV-014 makes the two seats independent, so HEALTHY DISAGREEMENT IS
    EVIDENCE THE INDEPENDENCE IS REAL. Agreement drifting toward 100 % means
    either leakage or a shared bias.
    ```

    ⚠ **A low disagreement rate is a WARNING, not a success** — this diagnostic
    exists *because of* the architecture.
    """
    healthy = [("BUY", "BUY")] * 14 + [("BUY", "HOLD")] * 8
    assert rm8_seat_disagreement(healthy).status == OK

    lockstep = [("BUY", "BUY")] * 25
    assert rm8_seat_disagreement(lockstep).status == WARN, "★ leakage or shared bias"
    assert rm8_seat_disagreement([("BUY", "HOLD")] * 25).status == WARN, "inverted"


# --------------------------------------------------------------------------- #
# AC-1.72 — RM-16
# --------------------------------------------------------------------------- #

def test_ac_1_72_rho_is_not_yet_calibrated_until_outcomes_accrue():
    """AC-1.72 — RM-16, RA-30.

    ★ *`ρ` is currently an assumed parameter on both sides of an argument, and it
    is measurable.*
    """
    assert rm16_thesis_error_correlation({}).status == NOT_YET_CALIBRATED
    assert rm16_thesis_error_correlation({"MU": [0.1, 0.2, 0.3]}).status \
        == NOT_YET_CALIBRATED


def test_ac_1_72_rho_collapses_breadth_for_level_decisions():
    """★★ The box's asymmetry, as an assertion.

    ```
    LEVEL  effective breadth is n/(1+(n-1)ρ) — at n=13, ρ=0.6 that is 1.6.
    RANK   the shared error c CANCELS EXACTLY.
    ```
    """
    # Three names moving together — high ρ.
    together = rm16_thesis_error_correlation(
        {"MU": [0.1, 0.5, 0.9, 0.3], "NVDA": [0.12, 0.52, 0.88, 0.31],
         "INTC": [0.09, 0.48, 0.92, 0.29]})
    assert together.status == OK
    assert together.value["rho"] > 0.9
    assert together.value["effective_breadth_for_level_decisions"] < 1.2, \
        "★ three names, but barely more than one independent opinion"
    assert "rank decisions are unharmed" in together.value["note"]


def test_a_constant_error_series_gives_no_correlation_not_zero():
    """⚠ *A constant error series has UNDEFINED correlation, and reporting zero
    would claim independence that was never measured.*"""
    flat = rm16_thesis_error_correlation({"MU": [0.5] * 4, "NVDA": [0.5] * 4})
    assert flat.status == NOT_YET_CALIBRATED


def test_the_calibration_monitors_all_start_uncalibrated():
    """RM-12/13/14 — ⚠ **the monitors most likely to be silently skipped**,
    because none can return a number for years. RA-30 is why they still appear."""
    assert rm12_calibration_curve([]).status == NOT_YET_CALIBRATED
    assert rm14_action_correlation([]).status == NOT_YET_CALIBRATED
    curve = rm12_calibration_curve([("High", True)] * 15 + [("Low", False)] * 10)
    assert curve.status == OK and curve.value["High"] == 1.0


def test_rm13_flags_decorative_falsifiers():
    """RM-13 — ★ *a high abandonment rate means the falsifiers were decorative*,
    and **the fix is in J-15's prompt, not in the reader**."""
    assert rm13_falsifier_vs_abandonment(["falsifier_fired"] * 8
                                         + ["abandoned"] * 2).status == OK
    assert rm13_falsifier_vs_abandonment(["abandoned"] * 8
                                         + ["falsifier_fired"] * 2).status == WARN


def test_rm15_is_zero_or_it_fails_the_run():
    """RM-15 — ★ *should be zero. Non-zero is a REGRESSION, not a style question.*"""
    assert rm15_lint_and_uncited(0, 0).status == OK
    assert rm15_lint_and_uncited(1, 0).status == FAIL
    assert rm15_lint_and_uncited(0, 1).status == FAIL


# --------------------------------------------------------------------------- #
# AC-1.25 / AC-1.25a / AC-1.26 — the lint, and its ONE owner
# --------------------------------------------------------------------------- #

def test_ac_1_25a_the_wordlist_is_declared_once_and_d09_executes_it():
    """AC-1.25a — ★★ **RA-137**, the second defect this slice found.

    ⚠ *Two deterministic implementations of one wordlist is **FE-4's defect in
    another domain*** — and the two enforcement points differ in consequence:
    **X-03 fails the run**, **RP-18 blocks the render**. A list that drifts
    between them makes which one fires depend on which copy was edited.
    """
    import src.reporting.render.lint as d09
    import src.fundamental.monitor.lint as d01

    assert d09.FORECAST_VOICE is d01.FORECAST_VOICE, "one object, not two equal ones"
    assert d09.LENGTH_CAPS is d01.LENGTH_CAPS

    # ⚠ DX-9 — src/reporting/ is still upstream while this test now lives here.
    from tests_src.architecture import source_path
    source = source_path("src/reporting/render/lint.py").read_text()
    assert "FORECAST_VOICE = (" not in source, "D-09 must not restate the list"


def test_ac_1_25_forecast_voice_violations_are_found_deterministically():
    """AC-1.25 — RA-26, X-03. ★ *Deterministic wordlist — no LLM.*"""
    hits = forecast_voice_violations({"thesis": "Margins will clearly expand."})
    assert {h.phrase for h in hits} == {"will", "clearly"}
    assert forecast_voice_violations(
        {"thesis": "A willing buyer at clearance prices."}) == ()


def test_ac_1_26_length_caps_are_declared_per_section():
    """AC-1.26 — RA-27. *Length is a free confidence signal; capping removes it
    and costs nothing analytical.*"""
    assert length_violations({"thesis": "x" * 100}) == ()
    over = length_violations({"thesis": "x" * 5000})
    assert over[0][0] == "thesis" and over[0][2] == LENGTH_CAPS["thesis"]
    assert "business_model" in LENGTH_CAPS, "J-02's 400-word cap"


# --------------------------------------------------------------------------- #
# ★★ BS-28 — the boundary this slice lifts
# --------------------------------------------------------------------------- #

def test_bs28_a_verdict_can_now_render_with_its_stability_figure():
    """★★ B4.5's done-when, second clause, and **BS-28's whole point**.

    *A verdict may not reach a human before RA-20/RA-21's fields exist — a
    verdict rendered without its stability figure and with a bare confidence
    number is D-15 with better plumbing.*

    Before this slice the gate returned `None` for agreement and RP-13 refused
    the actionable path. RM-1 now supplies the figure.
    """
    import dataclasses
    from datetime import date

    from src.decision import compose
    from src.fundamental import GateInputs, evaluate
    from src.quant import Candidate, Nomination
    from src.reporting import build_card
    from src.risk import AlertSet, COMPLETE
    from tests_src.test_fundamental_b44 import thesis

    as_of = date(2026, 8, 23)
    probe = rm1_perturbation_probe(["BUY", "BUY", "BUY", "HOLD", "HOLD"])
    t = dataclasses.replace(thesis(), verdict_stability=probe.to_json_obj())

    gate_verdict = evaluate(GateInputs(thesis=t), as_of=as_of, ticker="MU")
    nomination = Nomination(as_of=as_of, run_id="r", decision_anchor="open",
                            horizon_set=("production", 1), nominating_horizon="h1m",
                            universe_n=130, model_artifact_id="sha256:abc",
                            candidates=(Candidate("MU", 1, 0.04, 2.6),),
                     contract_version="b3_minimal@v1", adj_as_of=as_of,
                     calendar_check_id="cal:test")
    rec = compose(nomination=nomination, gate_verdicts=[gate_verdict],
                  alert_set=AlertSet((), COMPLETE), run_id="r", as_of=as_of,
                  gate_roster_declared=("thesis",), manifest_anchor="open",
                  actionable=True,
                  # ★ DN-39 — D-12 now requires the figure it is about to let a
                  #   human act on, rather than trusting D-09 to catch its absence.
                  top_thesis_stability=t.verdict_stability)

    # ★ It renders on the ACTIONABLE path — which B4.4's output could not do.
    card = build_card(rec, as_of=as_of)
    assert card.actionable is True
    assert card.field("stability").value == "⚠ unstable: 3 BUY / 2 HOLD"
    assert card.field("confidence").value.startswith("0.62 (basis: evidence_coverage)")


def test_bs28_an_unmeasured_stability_still_refuses_the_actionable_path():
    """⚠ The boundary lifts only when the probe actually ran.

    **`None` is not 1.0**, and RP-13 still fires — which is what stops B4.5 from
    becoming a licence rather than a measurement.
    """
    from datetime import date

    from src.decision import compose
    from src.fundamental import GateInputs, evaluate
    from src.quant import Candidate, Nomination
    from src.reporting import StabilityMissingError, build_card
    from src.risk import AlertSet, COMPLETE
    from tests_src.test_fundamental_b44 import thesis

    as_of = date(2026, 8, 23)
    gate_verdict = evaluate(GateInputs(thesis=thesis()), as_of=as_of, ticker="MU")
    nomination = Nomination(as_of=as_of, run_id="r", decision_anchor="open",
                            horizon_set=("production", 1), nominating_horizon="h1m",
                            universe_n=130, model_artifact_id="sha256:abc",
                            candidates=(Candidate("MU", 1, 0.04, 2.6),),
                     contract_version="b3_minimal@v1", adj_as_of=as_of,
                     calendar_check_id="cal:test")
    # ⚠ Hand-built past D-12: DN-39 now refuses this pairing upstream, and the
    #   subject of THIS test is that **D-09 refuses it too** — the boundary must
    #   not depend on the layer above having held.
    import dataclasses

    rec = compose(nomination=nomination, gate_verdicts=[gate_verdict],
                  alert_set=AlertSet((), COMPLETE), run_id="r", as_of=as_of,
                  gate_roster_declared=("thesis",), manifest_anchor="open",
                  actionable=False, not_actionable_reason="no stability (DN-39)")
    rec = dataclasses.replace(rec, actionable=True, not_actionable_reason=None)
    with pytest.raises(StabilityMissingError, match="better plumbing"):
        build_card(rec, as_of=as_of)
