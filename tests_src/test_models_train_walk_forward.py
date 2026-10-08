"""D-04 — MT-58 / AC-4.40: both out-of-sample protocols, each named. ✏ Written 2026-10-08 (`DX-162`).

Hermetic: a synthetic panel, a two-line estimator stand-in is not needed — LightGBM fits 40 names ×
300 days in well under a second.
"""

from __future__ import annotations

import inspect
from datetime import date

import numpy as np
import pandas as pd
import pytest


def _panel_and_labels(days=640, names=30, seed=3):
    from src.feature_engineer.contracts.labels import LabelDef

    rng = np.random.default_rng(seed)
    rows, labels = [], []
    for d in pd.bdate_range("2020-01-01", periods=days):
        for n in range(names):
            x = float(rng.normal())
            rows.append({"ticker": f"T{n}", "date": d, "f1": x})
            labels.append({"ticker": f"T{n}", "date": d, "value": 0.02 * x + float(rng.normal(0, .05)),
                           "available_at": d + pd.Timedelta(days=30), "decision_anchor": "open",
                           "label_def_id": "fwd_ret_21d_open", "horizon_days": 21})
    label_def = LabelDef(label_def_id="fwd_ret_21d_open", horizon_days=21, decision_anchor="open")
    return pd.DataFrame(rows), pd.DataFrame(labels), label_def


class _Contract:
    name, version, content_hash = "test", 1, ""
    feature_names = ("f1",)


@pytest.mark.parametrize("scheme", ["purged_kfold", "walk_forward"])
def test_ac_4_40_each_scheme_runs_and_is_recorded(scheme):
    from src.models.train.run import walk_forward_ic

    panel, labels, label_def = _panel_and_labels()
    result, folds, scored = walk_forward_ic(
        panel=panel, labels=labels, contract=_Contract(), label_def=label_def,
        as_of=date(2026, 10, 8), adj_as_of=date(2026, 10, 8), horizon_days=21, scheme=scheme)
    assert result.mean_ic is not None and result.mean_ic > 0
    assert all(f["scheme"] == scheme for f in folds)
    if scheme == "walk_forward":
        assert [f["index"] for f in folds if f.get("ic") is not None] == [1, 2, 3, 4]
        assert scored["date"].min() > panel["date"].min(), "block 0 is never tested"


def test_ac_4_40_an_unknown_scheme_raises():
    from src.models.train.run import walk_forward_ic

    panel, labels, label_def = _panel_and_labels(days=60, names=5)
    with pytest.raises(ValueError, match="scheme"):
        walk_forward_ic(panel=panel, labels=labels, contract=_Contract(), label_def=label_def,
                        as_of=date(2026, 10, 8), adj_as_of=date(2026, 10, 8), horizon_days=21,
                        scheme="rolling")


def test_ac_4_40_training_runs_both_and_persists_the_walk_forward():
    from src.models.train import __main__ as train
    from src.models.train.run import decide_promotion

    body = inspect.getsource(train._train)
    assert 'scheme="walk_forward"' in body and "purged k-fold" in body
    assert "walk_forward=" in body
    assert "walk_forward" in inspect.signature(decide_promotion).parameters
