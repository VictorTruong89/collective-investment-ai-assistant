"""FE-42 / AC-2.49 · MT-59 / AC-4.41 — the within-day Gaussian-rank training target. ✏ 2026-10-08.

★ A ranking model fitted on raw 21-day returns spends its trees on the market's swing, which every
stock shares. The target becomes each date's rank, mapped to a centred normal score; evaluation stays
on the raw return.
"""

from __future__ import annotations

import inspect
from datetime import date
from statistics import NormalDist

import numpy as np
import pandas as pd
import pytest


def _labels(values_by_date):
    rows = []
    for d, values in values_by_date.items():
        for i, v in enumerate(values):
            rows.append({"ticker": f"T{i}", "date": pd.Timestamp(d), "horizon_days": 21,
                         "label_def_id": "fwd_ret_21d_open", "decision_anchor": "open",
                         "value": v, "available_at": pd.Timestamp(d) + pd.Timedelta(days=30)})
    return pd.DataFrame(rows)


# ── AC-2.49 · FE-42 ──────────────────────────────────────────────────────────

def test_ac_2_49_known_answer_four_names():
    from src.feature_engineer.contracts.labels import cross_sectional_gauss

    out = cross_sectional_gauss(_labels({"2024-01-02": [0.05, -0.02, 0.10, 0.00]}))
    inv = NormalDist().inv_cdf
    expected = [inv(2.5 / 4), inv(0.5 / 4), inv(3.5 / 4), inv(1.5 / 4)]
    assert out["value"].tolist() == pytest.approx(expected)
    assert out["value"].sum() == pytest.approx(0.0, abs=1e-12), "centred"
    assert set(out["label_def_id"]) == {"fwd_ret_21d_open.xs_gauss"}
    assert (out["available_at"] == pd.Timestamp("2024-02-01")).all()


def test_ac_2_49_ties_are_averaged():
    from src.feature_engineer.contracts.labels import cross_sectional_gauss

    out = cross_sectional_gauss(_labels({"2024-01-02": [0.01, 0.01, 0.02]}))
    assert out["value"].iloc[0] == pytest.approx(out["value"].iloc[1])


def test_ac_2_49_a_market_wide_move_changes_nothing():
    """★ The point: adding the same 8 % to every name (a market month) moves no target."""
    from src.feature_engineer.contracts.labels import cross_sectional_gauss

    base = [0.03, -0.01, 0.07, 0.02, -0.04]
    a = cross_sectional_gauss(_labels({"2024-01-02": base}))
    b = cross_sectional_gauss(_labels({"2024-01-02": [np.exp(v + 0.08) for v in base]}))
    assert a["value"].tolist() == pytest.approx(b["value"].tolist())


def test_ac_2_49_a_date_with_fewer_than_three_names_yields_no_target():
    from src.feature_engineer.contracts.labels import cross_sectional_gauss

    out = cross_sectional_gauss(_labels({"2024-01-02": [0.1, 0.2],
                                         "2024-01-03": [0.1, 0.2, 0.3]}))
    assert set(out["date"]) == {pd.Timestamp("2024-01-03")}


# ── AC-4.41 · MT-59 ──────────────────────────────────────────────────────────

def test_ac_4_41_the_default_target_is_xs_gauss_and_raw_is_selectable():
    from src.models.train.__main__ import main

    source = inspect.getsource(main)
    assert '"--target"' in source and 'default="xs_gauss"' in source


def test_ac_4_41_the_artifact_names_its_target_and_evaluation_reads_raw():
    from src.models.train.run import fit_selection_model, walk_forward_ic
    from tests_src.test_models_train_walk_forward import _Contract, _panel_and_labels

    panel, labels, label_def = _panel_and_labels()
    artifact = fit_selection_model(panel=panel, labels=labels, contract=_Contract(),
                                   label_def=label_def, as_of=date(2026, 10, 8),
                                   adj_as_of=date(2026, 10, 8), horizon_days=21,
                                   target="xs_gauss")
    assert artifact.manifest.label_def_id == "fwd_ret_21d_open.xs_gauss"

    _, _, scored = walk_forward_ic(panel=panel, labels=labels, contract=_Contract(),
                                   label_def=label_def, as_of=date(2026, 10, 8),
                                   adj_as_of=date(2026, 10, 8), horizon_days=21,
                                   target="xs_gauss")
    raw = labels.set_index(["ticker", "date"])["value"]
    joined = scored.set_index(["ticker", "date"])["value"]
    assert joined.equals(raw.loc[joined.index]), "the simulation reads the RAW return"
