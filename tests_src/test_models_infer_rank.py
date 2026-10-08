"""D-04 inference — ranking by a promoted model, and the population check.

⚠ These live in `src/models/infer/`, not `src/quant/`: **QA-21 forbids D-03
importing from `src.models`**, and the first draft of this module sat in
`quant/signals/` and reached for `models.errors.ParityError`. ★ The rule
settles the ownership — scoring with a fitted artifact is D-04's.
"""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from src.quant.errors import QuantError
from src.models.infer.rank import (
    VOL_COLUMNS, assert_population_parity, rank_by_model,
)

AS_OF = date(2026, 8, 26)


class _Estimator:
    """Scores on the first feature, so the expected ranking is known."""

    @staticmethod
    def predict(frame):
        return frame.iloc[:, 0].to_numpy()


def _panel(names=("A", "B", "C"), *, vol_column="vol_20d", scores=(3.0, 1.0, 2.0)):
    return pd.DataFrame({
        "ticker": list(names),
        "date": [pd.Timestamp(AS_OF)] * len(names),
        "feat": list(scores),
        vol_column: [0.02] * len(names),
    })


def test_the_model_produces_the_ranking_not_the_rule():
    """★★ ⚠ *A model was promoted on 2026-08-27 and the card was still ranked by
    `z(mom_21) × vol_21 × √21`* — the artifact was loaded only so OR-44 could
    read its anchor, and nothing scored with it."""
    ranked = rank_by_model(_panel(), as_of=AS_OF, horizon_days=21,
                           estimator=_Estimator(), feature_names=("feat",))
    assert [c["ticker"] for c in ranked] == ["A", "C", "B"]
    assert ranked[0]["rank"] == 1


def test_a_missing_feature_raises_rather_than_narrowing():
    """★★★ **D-17.** ⚠ `[c for c in feature_names if c in df.columns]` is *one
    word away from correct*, and that word is the whole defect: a model never
    narrows to what is present."""
    with pytest.raises(QuantError, match="never narrows"):
        rank_by_model(_panel(), as_of=AS_OF, horizon_days=21,
                      estimator=_Estimator(),
                      feature_names=("feat", "absent_feature"))


def test_the_denormalisation_uses_the_contracts_own_volatility_column():
    """⚠ **`vol_21` belongs to `b3_minimal`; `vol_20d` to `price_ohlcv`.** A
    model fitted on the second and denormalised with the first's column failed
    with a `TypeError` deep inside pandas rather than saying so."""
    assert VOL_COLUMNS[0] == "vol_20d"
    ranked = rank_by_model(_panel(vol_column="vol_21"), as_of=AS_OF,
                           horizon_days=21, estimator=_Estimator(),
                           feature_names=("feat",))
    assert ranked, "either contract's volatility column resolves"


def test_no_volatility_column_raises_rather_than_publishing_the_raw_score():
    """★★ QA-58 — ⚠ a denormalisation that quietly drops σ̂ publishes the
    **normalised** score as though it were denormalised, which is exactly the
    low-vol tilt QA-58 exists to remove."""
    panel = _panel().drop(columns=["vol_20d"])
    with pytest.raises(QuantError, match="denormalis"):
        rank_by_model(panel, as_of=AS_OF, horizon_days=21,
                      estimator=_Estimator(), feature_names=("feat",))


def test_an_unrankable_name_is_skipped_never_scored_as_median():
    """FE-27 — ★ it is not dropped silently and not scored as the median; *it
    simply cannot be ranked today*."""
    panel = _panel()
    panel.loc[1, "vol_20d"] = np.nan
    ranked = rank_by_model(panel, as_of=AS_OF, horizon_days=21,
                           estimator=_Estimator(), feature_names=("feat",))
    assert [c["ticker"] for c in ranked] == ["A", "C"]


# --------------------------------------------------------------------------- #
# ★★ AB-4 — the population check a contract check cannot make
# --------------------------------------------------------------------------- #

def test_a_materially_different_cross_section_raises():
    """★★★ **AB-4.** ⚠ `rank_ret_5d`, `rank_vol_20d` and every `*_sector_z` are
    **defined by the population they are computed in** — *a percentile among 497
    names is not a percentile among 130*. The column names match exactly, so a
    contract check cannot see it."""
    from src.models.errors import ParityError

    panel = _panel(names=tuple(f"T{i}" for i in range(130)),
                   scores=tuple(range(130)))
    with pytest.raises(ParityError, match="fitted on 497"):
        assert_population_parity({"training_names": 497}, panel)


def test_a_matching_cross_section_passes():
    """★ The positive case, so the negative one is not vacuous."""
    panel = _panel(names=tuple(f"T{i}" for i in range(480)),
                   scores=tuple(range(480)))
    assert assert_population_parity({"training_names": 497}, panel).startswith("OK")


def test_an_artifact_that_cannot_be_checked_says_so():
    """⚠⚠ **Returned, never swallowed.** An artifact fitted before
    `training_names` existed cannot have this checked — and *"could not check"*
    must not read like *"checked and fine"*."""
    note = assert_population_parity({}, _panel())
    assert note.startswith("UNCHECKED")
    assert "AB-4" in note


def test_the_manifest_records_the_training_population():
    """★ Without the field the mismatch is undetectable: the column names match
    exactly."""
    from src.models.artifact.manifest import ModelManifest

    assert "training_names" in ModelManifest.__dataclass_fields__


# --------------------------------------------------------------------------- #
# ★★ AB-13 closed by construction — one universe on both sides
# --------------------------------------------------------------------------- #

def test_the_daily_run_defaults_to_the_training_universe():
    """★★ **AB-13's structural fix.** ⚠ The daily run scored **130** names with a
    model fitted on **497**, and rank/sector-z features are *defined by the
    population they are computed in* — a percentile among 497 is not a
    percentile among 130, and the column names match exactly.

    ★ Aligning the two closes it by construction rather than by a check.
    """
    import argparse
    import inspect

    from src.orchestration import entrypoint

    source = inspect.getsource(entrypoint.main)
    assert '"--universe", choices=("sp500", "watchlist"), default="sp500"' in source
    del argparse


def test_both_universes_come_from_one_source_each():
    """★ ⚠ Two lists that *should* match will drift the moment they are
    maintained separately — the training universe and the daily default are the
    same call, not two copies."""
    import inspect

    from src.orchestration import entrypoint

    assert "from src.models.train.run import load_sp500" in inspect.getsource(
        entrypoint._sp500_universe)


def test_widening_the_universe_does_not_widen_what_may_be_bought():
    """★ DE-36 — *a name excluded from the actionable slate still participates in
    cross-sectional normalisation.* ⚠ The universe normalises; the watchlist is
    what may be nominated, and INV-6 still permits exactly one actionable pick."""
    from src.orchestration.entrypoint import load_universe

    watchlist = load_universe()
    assert len(watchlist) > 0, "the watchlist survives as its own list"


# --------------------------------------------------------------------------- #
# ★★ MT-60 / AC-4.42 (DX-165) — the card ranks what the gates measured
# --------------------------------------------------------------------------- #

def test_ac_4_42_the_order_follows_the_score_not_the_volatility_scaled_value():
    """A calm name with a larger score beats a volatile one with a smaller score.
    ⚠ Before 2026-10-08 the order was ẑ·σ̂·√h, so B (ẑ 1.0, σ 0.05 → 0.229) beat
    A (ẑ 2.0, σ 0.01 → 0.092) — the gates had measured the ẑ order."""
    panel = _panel(names=("A", "B"), scores=(2.0, 1.0))
    panel["vol_20d"] = [0.01, 0.05]
    ranked = rank_by_model(panel, as_of=AS_OF, horizon_days=21,
                           estimator=_Estimator(), feature_names=("feat",))
    assert [c["ticker"] for c in ranked] == ["A", "B"]
    assert [c["ranked_quantity"] for c in ranked] == [c["z"] for c in ranked]
    assert ranked[1]["sigma_scaled"] == pytest.approx(1.0 * 0.05 * 21 ** 0.5)
    assert ranked[1]["sigma_scaled"] > ranked[0]["sigma_scaled"], "reported, not ordering"
