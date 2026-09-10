"""`F8` `AC-8.1` · `AC-8.10` — ★★ a drill-down runs the FULL path.

⚠⚠ **`QR-16` is the governing decision and it is not the obvious one.** When the
fund manager asks about a name outside the top-1, the pipeline runs *"the full
analysis path — same depth, same rigour, same artifacts as the top-1. Not a stub,
not a comparative summary, not a downgraded card."*

> *"A ranked list the manager cannot interrogate is an oracle, not decision
> support."*

★★★ The tempting design is the cheap one: answer the question with a summary. It
would be faster, cheaper, and would quietly teach the manager that interrogating
the ranker yields something weaker than trusting it — which inverts the whole
point of the control surface.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.fundamental.scorecard.coverage import assess_confidence
from src.fundamental.source.adapters import ApiAdapter
from src.fundamental.source.errors import ClaimContradictsData, SpansMissing
from src.orchestration.control.models import AnalysisRequest


@dataclass(frozen=True)
class Claim:
    text: str
    is_factual: bool = True
    evidence_ref: str | None = "10-K p42"
    unbound_declared: bool = False


def _adapter(contradiction=lambda _c: None, coverage=0.8):
    """★ The SAME port both paths resolve — `F8` §4: T1 resolves `F9`'s
    `ThesisSourcePort` and produces the artifact the top-1 gets."""
    return ApiAdapter(
        author_fn=lambda t, a, c: {"claims": [Claim(f"{t} revenue rose")],
                                   "provenance": {"model_id": "claude-opus-5"}},
        assess_confidence=lambda raw: assess_confidence(coverage).to_json_obj(),
        contradiction_check=contradiction)


def _scheduled():
    return _adapter().author("NVDA", "2026-09-09", {})


def _drilldown(ticker="MU"):
    """A drill-down is `attempt >= 2` on the SAME run (`D1`)."""
    request = AnalysisRequest(run_id="run-1", ticker=ticker, attempt=2,
                              requested_at="2026-09-09T00:00:00Z", rank_held=7)
    assert request.decision_id == f"run-1:{ticker}:2"
    return _adapter().author(request.ticker, "2026-09-09", {})


def test_ac_8_1_the_drill_down_artifact_has_the_SAME_FIELDS_at_the_same_depth():
    """`AC-8.1` / `AC-F9.7` — ⚠ neither is a reduced form of the other."""
    top1, drill = _scheduled(), _drilldown()
    assert set(top1.__slots__) == set(drill.__slots__)
    for field in top1.__slots__:
        assert getattr(drill, field) is not None or getattr(top1, field) is None, (
            f"{field} is present on the top-1 artifact and missing on the "
            "drill-down — that is a downgraded card (QR-16)")


def test_ac_8_1_the_drill_down_uses_the_SAME_PROMPT_SPEC():
    """★ `D2` — one prompt, two transports; and one prompt, two entry points.
    ⚠ A leaner prompt for the drill-down would make the two incomparable, which
    is the same argument that keeps the API and relay adapters aligned."""
    assert _drilldown().prompt_spec == _scheduled().prompt_spec


def test_ac_8_1_the_drill_down_carries_provenance_like_any_other_thesis():
    """`AC-F9.5` — ★ provenance is not a property of *how it was asked for*."""
    assert _drilldown().provenance["port"] == "thesis_source"


# ── AC-8.10 — no verification bypass ──────────────────────────────────────
def test_ac_8_10_a_contradicting_claim_RAISES_on_the_drill_down_path_too():
    """⚠⚠ `AC-8.10` — *the same claim verification as the scheduled path*.

    ★★★ This is the AC most worth having. The drill-down is the path the manager
    asks for **because they already have a view** — which is exactly when a
    contradicting claim is most likely to be believed. ⚠ A verification bypass
    here would be invisible: the card looks identical (`AC-8.1` makes sure of
    it), so nothing on screen would say this one was checked less.
    """
    adapter = _adapter(contradiction=lambda c: "our own data says revenue fell")
    with pytest.raises(ClaimContradictsData):
        adapter.author("MU", "2026-09-09", {})


def test_ac_8_10_an_unbound_claim_is_refused_on_the_drill_down_path_too():
    """`C1` / `RA-9` — ⚠ a span or an explicit declaration, on every path."""
    adapter = ApiAdapter(
        author_fn=lambda t, a, c: {"claims": [Claim("x", evidence_ref=None)],
                                   "provenance": {}},
        assess_confidence=lambda raw: assess_confidence(0.8).to_json_obj())
    with pytest.raises(SpansMissing):
        adapter.author("MU", "2026-09-09", {})


@pytest.mark.parametrize("coverage", [0.0, 0.3, 0.5, 0.8, 1.0])
def test_ac_8_10_de_rating_is_identical_on_both_paths(coverage):
    """`AC-F9.4` reached through `F8` — ⚠ `AC-1.77`: the relay's whole safety
    case rests on `RA-67`'s de-rating firing **unchanged**, and a drill-down is
    just another caller."""
    direct = assess_confidence(coverage).to_json_obj()
    adapter = _adapter(coverage=coverage)
    assert adapter.author("MU", "2026-09-09", {}).confidence == direct


def test_ac_8_10_the_drill_down_mints_its_own_decision_id_not_the_top_1s():
    """⚠ `CT-2.7` — *a drill-down of the same ticker carries a DIFFERENT
    `decision_id`*. ★ Otherwise an outcome would join to two analyses and
    `F7b`'s Tier-B study would double-count it."""
    a = AnalysisRequest(run_id="run-1", ticker="MU", attempt=2,
                        requested_at="t", rank_held=7)
    b = AnalysisRequest(run_id="run-1", ticker="MU", attempt=3,
                        requested_at="t", rank_held=7)
    assert a.decision_id != b.decision_id


def test_ac_8_1_attempt_1_is_not_a_drill_down():
    """★ `D1` — attempt 1 IS the scheduled analysis; a drill-down starts at 2."""
    with pytest.raises(ValueError, match="attempt >= 2"):
        AnalysisRequest(run_id="run-1", ticker="MU", attempt=1, requested_at="t")
