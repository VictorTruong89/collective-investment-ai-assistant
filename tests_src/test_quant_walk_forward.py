"""F12 `D11` / AC-F12.33 — a true expanding-window walk-forward (`DX-162`). ✏ Written 2026-10-08.

⚠ The console's "walk-forward" was purged k-fold: block 0 (2016–18) was tested by a model trained on
2018–26. These folds train only on the past. Pure date arithmetic — no data.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.quant.backtest.protocol import (
    CVProtocol,
    make_folds,
    make_walk_forward_folds,
)

DATES = tuple(d.date() for d in pd.bdate_range("2016-01-04", periods=500))
PROTOCOL = CVProtocol(purge_days=63, embargo_days=5, horizon_set_name="production",
                      horizon_set_version=1, n_folds=5)


def test_ac_f12_33_every_training_date_precedes_every_test_date():
    for fold in make_walk_forward_folds(DATES, PROTOCOL):
        assert max(fold.train_dates) < min(fold.test_dates)


def test_ac_f12_33_block_zero_is_never_tested_and_blocks_match_the_k_fold():
    walk = make_walk_forward_folds(DATES, PROTOCOL)
    kfold = make_folds(DATES, PROTOCOL)
    assert [f.index for f in walk] == [1, 2, 3, 4]
    for w in walk:
        assert w.test_dates == kfold[w.index].test_dates


def test_ac_f12_33_the_purge_is_in_trading_days_not_calendar_days():
    for fold in make_walk_forward_folds(DATES, PROTOCOL):
        position = {d: i for i, d in enumerate(DATES)}
        gap = position[fold.test_dates[0]] - position[fold.train_dates[-1]]
        assert gap == PROTOCOL.purge_days + 1, "exactly purge_days trading days skipped"
        # ⚠ 63 calendar days would be ~43 trading days — the DX-161 shape.
        assert (fold.test_dates[0] - fold.train_dates[-1]).days > 63


def test_ac_f12_33_a_fold_with_no_past_after_the_purge_is_dropped():
    short = DATES[:150]              # blocks of 30 dates; block 1's past is 30 < 63 purge
    walk = make_walk_forward_folds(short, PROTOCOL)
    assert all(len(f.train_dates) > 0 for f in walk)
    assert 1 not in [f.index for f in walk]


def test_ac_f12_33_empty_dates_make_no_folds():
    assert make_walk_forward_folds((), PROTOCOL) == ()
    assert isinstance(DATES[0], date)
