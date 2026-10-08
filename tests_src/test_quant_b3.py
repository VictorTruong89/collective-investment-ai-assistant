"""D-03 — AC-3.1, 3.2, 3.14…3.21, 3.23 · CT-3.4's QA-119…QA-122.

Tier: unit + data contract, plus §8's **known-answer** tier (AC-3.16).
"""

from __future__ import annotations

import math
from datetime import date

import pandas as pd
import pytest

from src.quant import (
    Candidate, HorizonUnpinnedError, MethodMissingError, Nomination,
    NominationContractError, PRODUCTION_V1, RANK_FORMULA_ID, declared_formula_ids,
    formula_ids_referenced_in_src, method, missing_sections, rank_candidates, rule_id,
    within_ticker_z,
)
from src.quant.horizons.horizon_set import Arbitration, Horizon, HorizonSet

AS_OF = date(2024, 8, 30)


def nomination(**kw):
    base = dict(as_of=AS_OF, run_id="r", decision_anchor="open",
                horizon_set=("production", 1), nominating_horizon="h1m",
                universe_n=130, model_artifact_id="sha256:abc",
                candidates=(Candidate("NVDA", 1, 0.04, 2.6),),
                contract_version="b3_minimal@v1", adj_as_of=AS_OF,
                calendar_check_id="cal:abc")
    return Nomination(**{**base, **kw})


# --------------------------------------------------------------------------- #
# §5 — the horizon set
# --------------------------------------------------------------------------- #

def test_ac_3_1_the_horizon_set_is_named_and_versioned():
    """AC-F12.1 — AC-3.1 — QA-1. Every model/backtest declares its HorizonSet name and version."""
    assert (PRODUCTION_V1.name, PRODUCTION_V1.version) == ("production", 1)
    assert PRODUCTION_V1.ranked_quantity == "denormalised_return"
    with pytest.raises(HorizonUnpinnedError):
        PRODUCTION_V1.horizon("h1y")


def test_ac_3_2_purge_shorter_than_the_longest_horizon_raises():
    """AC-F12.2 — AC-3.2 — QA-3/QA-18. A short purge leaks the label window across a fold."""
    with pytest.raises(HorizonUnpinnedError, match="leaks it across folds"):
        HorizonSet("bad", 1, (Horizon("h1q", 63, "research"),),
                   Arbitration("h1m", (), ()), purge_days=5, embargo_days=5,
                   ranked_quantity="denormalised_return")


def test_qa_47_arbitration_is_explicit_and_lives_in_the_horizon_set():
    """QA-47 — ★ *A HorizonSet without a stated arbitration rule is incomplete.*"""
    arb = PRODUCTION_V1.arbitration
    assert arb.nominates == "h1m"
    assert arb.may_delay_or_veto == ("h1w",) and arb.research_only == ("h1q",)


# --------------------------------------------------------------------------- #
# §8 — mathematical provenance
# --------------------------------------------------------------------------- #

def test_ac_3_14_every_formula_id_in_src_resolves_to_a_methodentry():
    """AC-F12.17 — AC-3.14 — QA-20. ★ **A `formula_id` with no MethodEntry FAILS THE BUILD.**

    *A method with no stated provenance is a number with borrowed authority*, and
    `rsi_14` is the live proof: ours is a rolling mean where every charting
    package uses Wilder smoothing, and nothing recorded the choice.
    """
    undocumented = formula_ids_referenced_in_src() - declared_formula_ids()
    assert not undocumented, f"formula_id(s) with no MethodEntry: {sorted(undocumented)}"


def test_ac_3_15_every_methodentry_carries_the_six_required_fields():
    """AC-F12.18 — AC-3.15 — §8.2: statement, symbols, reference, assumptions, alternatives, KAT."""
    for formula_id in sorted(declared_formula_ids()):
        assert missing_sections(formula_id) == [], f"{formula_id} is incomplete"


def test_ac_3_17_a_house_variant_is_flagged_as_one():
    """AC-F12.20 — AC-3.17 — QA-22. A method with no external reference says so in words.

    Both of B3's non-standard choices are declared: the open-to-open volatility
    and the within-ticker `z`.
    """
    assert "HOUSE VARIANT" in method("volatility.realised_open_to_open_std.v1")
    assert "HOUSE VARIANT" in method(RANK_FORMULA_ID)


def test_ac_3_18_assumptions_name_the_ones_this_system_violates():
    """AC-F12.21 — AC-3.18 — QA-23. ⚠ And they point at the correction, not merely at the risk."""
    for formula_id in sorted(declared_formula_ids()):
        text = method(formula_id)
        section = text.split("## Assumptions", 1)[1].split("## ", 1)[0]
        assert "Yes" in section or "⚠" in section, (
            f"{formula_id} lists assumptions and admits violating none — "
            f"QA-23 wants the violated ones named"
        )


def test_a_missing_methodentry_raises():
    """The check FIRES, not merely passes (L4 IM-3's standard)."""
    with pytest.raises(MethodMissingError, match="borrowed authority"):
        method("nonexistent.formula.v1")


def test_method_known_answer_ranked_quantity():
    """AC-3.16 — `rank.denormalised_within_ticker_z.v1`'s known-answer test."""
    assert 2.0 * 0.02 * math.sqrt(21) == pytest.approx(0.183303, abs=1e-6)


def test_qa_58_the_higher_volatility_name_ranks_first_at_equal_z():
    """★ QA-58's whole point, as an observable difference from ranking on `z`.

    *Publishing only `z` would let a consumer rank on the normalised quantity*,
    which is a systematic low-volatility tilt.
    """
    panel = pd.DataFrame({
        "ticker": ["LOWVOL", "HIGHVOL"], "date": [pd.Timestamp(AS_OF)] * 2,
        "mom_21": [0.1, 0.1], "vol_21": [0.01, 0.05],
    })
    # Both have z = 1.0 by construction, so only sigma separates them.
    panel_with_z = panel.copy()
    ranked = _rank_with_fixed_z(panel_with_z, z=1.0)
    assert [c["ticker"] for c in ranked] == ["HIGHVOL", "LOWVOL"]


def _rank_with_fixed_z(panel, z):
    from src.quant.signals import rank as rank_mod
    original = rank_mod.within_ticker_z
    rank_mod.within_ticker_z = lambda s, t, **kw: pd.Series([z] * len(s), index=s.index)
    try:
        return rank_candidates(panel, as_of=AS_OF, horizon_days=21)
    finally:
        rank_mod.within_ticker_z = original


# --------------------------------------------------------------------------- #
# CT-3.4 — the Nomination
# --------------------------------------------------------------------------- #

def test_qa_120_only_h1m_may_nominate_and_h1q_is_rejected_not_ignored():
    """QA-120 — `h1q` is research_only and may not appear in a Nomination at all.

    ⚠ **Rejected, not ignored.** Silently dropping it would let it back in later.
    """
    with pytest.raises(NominationContractError, match="only 'h1m'"):
        nomination(nominating_horizon="h1w")
    with pytest.raises(NominationContractError, match="research_only"):
        nomination(vetoed_by=("h1q",))


def test_qa_121_universe_n_and_model_artifact_id_are_required():
    """QA-121 — ★ *A nomination that cannot be traced to what produced it cannot
    be re-run* (INV-2). Before D-04 the id is the ranking rule's content hash."""
    with pytest.raises(NominationContractError, match="content hash"):
        nomination(model_artifact_id="")
    with pytest.raises(NominationContractError, match="E\\[max z\\]"):
        nomination(universe_n=0)
    assert rule_id().startswith("sha256:")


def test_qa_122_candidates_is_a_dense_ordered_list():
    """QA-122 — ★ *A contract that emits only rank 1 makes `k_cov >= 2`
    unimplementable* (`L2` CB-19)."""
    ok = nomination(candidates=(Candidate("A", 1, 0.9, 2.0), Candidate("B", 2, 0.5, 1.0)))
    assert ok.top.ticker == "A"
    with pytest.raises(NominationContractError, match="dense list"):
        nomination(candidates=(Candidate("A", 2, 0.9, 2.0),))
    with pytest.raises(NominationContractError, match="no top pick"):
        nomination(candidates=()).top


def test_qa_119_z_travels_beside_the_ranked_quantity():
    """QA-119 — both are published, so a reader can see which was ranked on."""
    obj = nomination().to_json_obj()
    assert {"ranked_quantity", "z"} <= set(obj["candidates"][0])


# --------------------------------------------------------------------------- #
# Boundary
# --------------------------------------------------------------------------- #

def test_ac_3_20_and_3_21_stateless_and_no_forbidden_imports():
    """AC-F12.23 / AC-F12.24 — AC-3.20 / AC-3.21 — QA-28. No fitted parameters; no D-04, no D-01."""
    from tests_src.architecture import qa_21, scan, st_10
    graph = scan()
    assert qa_21(graph) == []
    assert st_10(graph) == [], "and D-03 does not import D-12 either (ST-10)"


def test_the_ranker_computes_no_feature_of_its_own():
    """D-02 §1.2 — *D-02 is the only domain permitted to define a derived number.*"""
    with pytest.raises(KeyError, match="computes none of its own"):
        rank_candidates(pd.DataFrame({"ticker": ["X"], "date": [pd.Timestamp(AS_OF)]}),
                        as_of=AS_OF, horizon_days=21)


def test_an_unrankable_name_is_skipped_not_scored_as_median():
    """PD-1 — a name with missing data is UNKNOWN, not "exactly average"."""
    panel = pd.DataFrame({
        "ticker": ["X"], "date": [pd.Timestamp(AS_OF)],
        "mom_21": [float("nan")], "vol_21": [0.02],
    })
    assert rank_candidates(panel, as_of=AS_OF, horizon_days=21) == []


def test_within_ticker_z_never_fills_a_flat_series_with_zero():
    """A zero trailing sd means the signal did not move: z is undefined, not 0.0."""
    s = pd.Series([1.0] * 30)
    z = within_ticker_z(s, pd.Series(["X"] * 30))
    assert z.tail(5).isna().all()


def test_ac_f12_6_the_horizon_set_records_its_mandate_justification():
    """AC-F12.6 (≡ AC-3.6, QA-2) — *the HorizonSet records its mandate justification.*
    ★ CT-3.1 carries `mandate_justification`, `approved_by` and `approved_on`; the code
    carried none of them, so v1's grounds lived only in prose (§5.6). A set without
    a justification is refused — QA-2: justified against the mandate, *not chosen
    for statistical convenience*."""
    assert "M-4" in PRODUCTION_V1.mandate_justification
    assert "L0 §12.1" in PRODUCTION_V1.mandate_justification
    assert (PRODUCTION_V1.approved_by, PRODUCTION_V1.approved_on) == ("victor", "2026-08-16")
    with pytest.raises(HorizonUnpinnedError, match="QA-2"):
        HorizonSet("unjustified", 1, (Horizon("h1m", 21, "selection"),),
                   Arbitration("h1m", (), ()), purge_days=21, embargo_days=5,
                   ranked_quantity="denormalised_return")


@pytest.mark.parametrize("missing", ["contract_version", "adj_as_of", "calendar_check_id"])
def test_ac_f12_26_a_nomination_records_its_provenance(missing):
    """AC-F12.26 (≡ AC-3.23, QA-30) — *every output records contract version, as_of,
    adj_as_of, calendar id.* ★ `BacktestSpec` pinned all four; the `Nomination` — the
    output D-12 actually consumes every day — carried `as_of` only. Each one absent
    is refused, never defaulted (P5)."""
    obj = nomination().to_json_obj()
    assert (obj["contract_version"], obj["adj_as_of"], obj["calendar_check_id"]) == \
        ("b3_minimal@v1", AS_OF.isoformat(), "cal:abc")
    empty = None if missing == "adj_as_of" else ""
    with pytest.raises(NominationContractError, match=missing):
        nomination(**{missing: empty})


def test_ac_f12_30_both_outputs_state_the_regime_limitation():
    """AC-F12.30 (F12 `D3`/`D7`, PG-10) — every Nomination and BacktestResult carries
    the fixed sentence, verbatim, so no single-regime result reads as regime-robust."""
    from src.quant.contracts.backtest import BacktestResult
    from src.quant.contracts.nomination import REGIME_LIMITATION

    assert REGIME_LIMITATION == (
        "Not regime-conditioned: one model is fitted across all market states; "
        "a result from one regime is not evidence for another.")
    assert nomination().to_json_obj()["limitation"] == REGIME_LIMITATION
    assert BacktestResult("bts:x", ()).to_json_obj()["limitation"] == REGIME_LIMITATION


@pytest.mark.parametrize("horizon", [1, 5, 21])
def test_ac_f12_4_a_label_reads_only_prices_inside_its_horizon(horizon):
    """AC-F12.4 (≡ AC-3.4, INV-1) — *labels for a horizon use only prices within that
    horizon.* ★ Invariant, checked by PERTURBATION: for every labelled row `i`, moving
    any price other than the two anchors (`i` and `i+h`) leaves its label unchanged,
    and `available_at` is the date `h` sessions on. The labels are D-02's
    (`build_labels`); this test reads them and changes nothing there."""
    import numpy as np

    from src.feature_engineer.contracts.labels import LabelDef, build_labels

    n = horizon + 8
    dates = pd.bdate_range("2025-01-02", periods=n).date
    prices = 100.0 + np.arange(n, dtype=float) * 1.5
    label_def = LabelDef(f"t{horizon}", horizon, "open")

    def labels(p):
        panel = pd.DataFrame({"ticker": "X", "date": dates, "adj_open_minor": p})
        return build_labels(label_def=label_def, price_panel=panel)

    base = labels(prices)
    assert len(base) == n - horizon
    for i in range(n - horizon):
        assert base["value"][i] == pytest.approx(prices[i + horizon] / prices[i] - 1)
        assert pd.Timestamp(base["available_at"][i]) == pd.Timestamp(dates[i + horizon])
        for j in set(range(n)) - {i, i + horizon}:
            moved = prices.copy()
            moved[j] *= 3.0
            assert labels(moved)["value"][i] == pytest.approx(base["value"][i]), (i, j)


def test_ac_f12_19_every_methodentry_names_a_known_answer_test_that_exists():
    """AC-F12.19 (≡ AC-3.16) — *every MethodEntry's known-answer test executes and
    passes.* ★ Each entry's `## Known-answer test` section must name at least one
    `path.py::test_name` that resolves to a real test function; the suite then runs
    it, so a resolvable link is an executed one. ⚠ An entry naming no test, a file
    that is gone, or a function that was renamed is reported — the link is the
    thing that rots."""
    from src.quant.methods.registry import unresolved_known_answer_tests

    assert unresolved_known_answer_tests() == {}


def test_ac_f12_19_a_dangling_known_answer_link_is_reported(tmp_path):
    """AC-F12.19 — the check FIRES (IM-3): a renamed test function is caught."""
    from src.quant.methods.registry import unresolved_known_answer_tests

    (tmp_path / "entries").mkdir()
    (tmp_path / "entries" / "x.v1.md").write_text(
        "## Known-answer test\n\n`tests_src/test_quant_b3.py::test_no_such_function`\n")
    found = unresolved_known_answer_tests(entry_dirs=(tmp_path / "entries",))
    assert "x.v1" in found and "test_no_such_function" in found["x.v1"]


def test_ac_f12_22_every_located_formula_is_pinned_to_its_code():
    """AC-F12.22 (≡ AC-3.19, QA-25) — *changing a formula without amending its
    MethodEntry in the same commit fails CI.* ★ Each entry whose formula_id is
    declared by a `FORMULA_ID = "..."` assignment pins the sha256 of that file
    (`Code: <path> @ sha256:<hex>`); a mismatch is a stale entry. ⚠ Entries with no
    assignment have no code to pin — they are a FIXED list, so it cannot grow
    silently."""
    from src.quant.methods.registry import UNLOCATED_FORMULAS, stale_entries

    assert stale_entries() == {}
    expected = frozenset({
        "cv.purge_embargo.derived.v1", "effective_n.overlap_corrected.v1",
        "mde.rank_ic.v1", "rank_ic.spearman.v1",
        "volatility.realised_open_to_open_std.v1",
        "se.newey_west_bartlett.v1",       # ✏ 2026-10-06 — F12 D9
        "cv.walk_forward.expanding.v1"})   # ✏ 2026-10-08 — F12 D11
    assert frozenset(UNLOCATED_FORMULAS) == expected


def test_ac_f12_22_a_code_change_without_its_entry_is_stale(tmp_path):
    """AC-F12.22 — the check FIRES: edit the code, leave the entry, and it is stale."""
    from src.quant.methods.registry import code_digest, stale_entries

    src = tmp_path / "src" / "dom"
    (src / "methods" / "entries").mkdir(parents=True)
    code = src / "f.py"
    code.write_text('FORMULA_ID = "f.v1"\n\ndef f(x):\n    return x + 1\n')
    entry = src / "methods" / "entries" / "f.v1.md"
    entry.write_text(f"Code: src/dom/f.py @ sha256:{code_digest(code)}\n")
    assert stale_entries(repo=tmp_path) == {}
    code.write_text('FORMULA_ID = "f.v1"\n\ndef f(x):\n    return x + 2\n')
    assert "f.v1" in stale_entries(repo=tmp_path)
