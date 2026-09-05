"""F4 — the explanation contract, composition, comparison, counterfactuals."""

from __future__ import annotations

import pytest

from src.explain.comparative import compare
from src.explain.counterfactual import NoCounterfactual, Observable, search
from src.explain.models import Attribution, Change, Counterfactual, Driver, Explanation
from src.explain.service import SelfExplanationRejected, explain


def _attr(domain="quant", method="treeshap", status="unpromoted", **kw):
    return Attribution(domain=domain, method=method, subject_status=status,
                       drivers=(Driver("gross_margin", 0.4, "up"),
                                Driver("revenue_growth", 0.2, "up")), **kw)


def _cf():
    return Counterfactual(statement="if gross margin falls to 0.38, verdict becomes HOLD",
                          changes=(Change("gross_margin", 0.42, 0.38),),
                          flips_to="HOLD", as_of="2026-09-04", universe_id="sp500")


# --------------------------------------------------------------------------- #
# AC-4.1 / AC-4.3 / AC-4.15 — attribution comes from the domain, unchanged
# --------------------------------------------------------------------------- #
def test_ac_4_1_an_explanation_without_attribution_explains_nothing():
    with pytest.raises(ValueError, match="explains nothing"):
        Explanation(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                    attributions=())


def test_ac_4_3_attributions_are_used_exactly_as_published():
    """★ D-13 composes; it never recomputes (QR-10)."""
    published = _attr()
    e = explain(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                published_attributions=[published])
    assert e.attributions[0] is published


def test_ac_4_15_the_method_is_always_named():
    """D2 — F4 commits to no method, but an unnamed one cannot be partitioned."""
    with pytest.raises(ValueError, match="method is required"):
        Attribution(domain="quant", method="")


def test_ac_4_15_an_intrinsic_method_is_equally_valid():
    """★ If the EBM challenger wins, only the recorded name changes."""
    assert Attribution(domain="quant", method="ebm_intrinsic").method == "ebm_intrinsic"


# --------------------------------------------------------------------------- #
# AC-4.11 / D3 — stability
# --------------------------------------------------------------------------- #
def test_ac_4_11_stability_may_be_a_number_or_explicitly_absent():
    assert _attr(stability=0.9).stability == 0.9
    assert _attr().stability is None


def test_ac_4_11_zero_is_a_measurement_not_an_absence():
    """⚠ 0 reads as *measured and perfectly unstable*; None means *not measured*."""
    assert _attr(stability=0.0).stability == 0.0
    assert _attr(stability=0.0).stability is not None


def test_ac_4_11_stability_outside_zero_to_one_is_refused():
    with pytest.raises(ValueError, match="agreement fraction"):
        _attr(stability=1.4)


# --------------------------------------------------------------------------- #
# AC-4.12 — status travels, and the WEAKEST wins
# --------------------------------------------------------------------------- #
def test_ac_4_12_an_explanation_is_only_as_promotable_as_its_weakest_input():
    """★★ PG-2 — a composed artifact must not launder an unpromoted model's authority.

    ⚠ The ranker sits at walk-forward IC 0.0203, t = 1.42.
    """
    e = Explanation(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                    attributions=(_attr(domain="fundamental", status="promoted"),
                                  _attr(domain="quant", status="unpromoted")))
    assert e.subject_status == "unpromoted"


def test_ac_4_12_experimental_dominates_everything():
    e = Explanation(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                    attributions=(_attr(status="promoted"),
                                  _attr(status="experimental")))
    assert e.subject_status == "experimental"


# --------------------------------------------------------------------------- #
# AC-4.8 / AC-4.9 — counterfactuals are observable and peer-scoped
# --------------------------------------------------------------------------- #
def test_ac_4_9_a_counterfactual_without_a_universe_is_refused():
    """⚠ A rank counterfactual is conditional on the peer set."""
    with pytest.raises(ValueError, match="as_of and universe_id"):
        Counterfactual(statement="x", changes=(Change("rank", 3, 1),),
                       flips_to="BUY", as_of="2026-09-04", universe_id="")


def test_ac_4_9_a_counterfactual_from_another_universe_is_refused():
    other = Counterfactual(statement="x", changes=(Change("rank", 3, 1),),
                           flips_to="BUY", as_of="2026-09-04", universe_id="tsx60")
    with pytest.raises(ValueError, match="different universe"):
        Explanation(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                    attributions=(_attr(),), counterfactual=other)


def test_ac_4_14_an_empty_counterfactual_cannot_be_constructed():
    with pytest.raises(ValueError, match="not a counterfactual"):
        Counterfactual(statement="x", changes=(), flips_to="HOLD",
                       as_of="2026-09-04", universe_id="sp500")


# --------------------------------------------------------------------------- #
# AC-4.14 / D4 — the search returns the SPARSEST flip, or refuses honestly
# --------------------------------------------------------------------------- #
def _verdict(state):
    return "BUY" if state["gross_margin"] >= 0.40 and state["rank"] <= 5 else "HOLD"


def test_ac_4_14_the_search_returns_the_sparsest_flip():
    got = search({"gross_margin": 0.42, "rank": 3},
                 [Observable("gross_margin", (0.38, 0.30)), Observable("rank", (9,))],
                 _verdict, as_of="2026-09-04", universe_id="sp500")
    assert isinstance(got, Counterfactual)
    assert got.sparsity == 1, "one change suffices, so two must not be returned"
    assert got.flips_to == "HOLD"


def test_ac_4_8_every_change_names_an_observable_not_a_feature_id():
    got = search({"gross_margin": 0.42, "rank": 3},
                 [Observable("gross_margin", (0.30,))], _verdict,
                 as_of="2026-09-04", universe_id="sp500")
    for c in got.changes:
        assert not c.observable.startswith("f_"), "⚠ never a raw feature id"
        assert c.observable[-1] != "z", "⚠ never a z-score"


def test_ac_4_14_nothing_flipping_it_is_reported_not_returned_empty():
    """⚠ Silence would read as 'no counterfactual was looked for'."""
    got = search({"gross_margin": 0.42, "rank": 3},
                 [Observable("gross_margin", (0.41,))], _verdict,
                 as_of="2026-09-04", universe_id="sp500")
    assert isinstance(got, NoCounterfactual)
    assert got.searched == 1 and "finding" in got.reason


def test_ac_4_14_a_pair_is_found_when_no_single_change_works():
    def both_needed(state):
        return "BUY" if state["a"] and state["b"] else "HOLD"
    got = search({"a": True, "b": True},
                 [Observable("a", (False,)), Observable("b", (False,))],
                 lambda s: "HOLD" if not (s["a"] and s["b"]) else "BUY",
                 as_of="2026-09-04", universe_id="sp500")
    assert isinstance(got, Counterfactual) and got.sparsity == 1


# --------------------------------------------------------------------------- #
# AC-4.10 — ⚠ no self-explanation
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("key", ["reasoning", "chain_of_thought", "rationale",
                                 "model_explanation", "thought_process"])
def test_ac_4_10_model_self_reported_reasoning_is_rejected(key):
    """⚠⚠ Chain-of-thought is demonstrably unfaithful — models shift answers under
    biasing cues while their stated reasoning never mentions the cue."""
    with pytest.raises(SelfExplanationRejected):
        explain(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                published_attributions=[_attr()],
                gate_binding={"gates": ["ic"], key: "I weighed the evidence"})


def test_ac_4_10_self_report_is_caught_when_nested():
    with pytest.raises(SelfExplanationRejected):
        explain(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                published_attributions=[_attr()],
                gate_binding={"detail": [{"cot": "first I considered..."}]})


def test_ac_4_10_ordinary_gate_binding_passes():
    e = explain(subject_id="NVDA", as_of="2026-09-04", universe_id="sp500",
                published_attributions=[_attr()],
                gate_binding={"gates": ["ic_significance"], "bound_by": "breadth"})
    assert e.gate_binding["bound_by"] == "breadth"


# --------------------------------------------------------------------------- #
# AC-4.13 — "why this and not that"
# --------------------------------------------------------------------------- #
def test_ac_4_13_comparison_names_the_driver_of_the_gap():
    a = Explanation("NVDA", "2026-09-04", "sp500", (_attr(),))
    b = Explanation("AMD", "2026-09-04", "sp500",
                    (Attribution("quant", "treeshap",
                                 drivers=(Driver("gross_margin", 0.1, "up"),
                                          Driver("revenue_growth", 0.25, "up"))),))
    cmp = compare(a, b)
    assert cmp.leading_driver.name == "gross_margin"
    assert cmp.leading_driver.gap == pytest.approx(0.3)


def test_ac_4_13_a_cross_universe_comparison_is_refused():
    a = Explanation("NVDA", "2026-09-04", "sp500", (_attr(),))
    b = Explanation("SHOP", "2026-09-04", "tsx60", (_attr(),))
    with pytest.raises(ValueError, match="peer-conditional"):
        compare(a, b)


def test_ac_4_13_a_comparison_carries_the_weaker_status():
    a = Explanation("NVDA", "2026-09-04", "sp500", (_attr(status="promoted"),))
    b = Explanation("AMD", "2026-09-04", "sp500", (_attr(status="experimental"),))
    assert compare(a, b).subject_status == "experimental"


# --------------------------------------------------------------------------- #
# D1 — the honest current state of AB-1 / AB-2
# --------------------------------------------------------------------------- #
def test_d1_grounding_and_confidence_default_to_the_truth_today():
    """⚠ AB-1/AB-2 are upstream R7. Until they land, an Explanation says so."""
    e = Explanation("NVDA", "2026-09-04", "sp500", (_attr(),))
    assert e.grounding == {"claims_total": 0, "claims_bound": 0, "unbound": []}
    assert e.confidence == {"basis": "not_measured"}
