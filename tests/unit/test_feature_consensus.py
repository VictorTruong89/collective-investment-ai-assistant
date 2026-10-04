"""`src/feature_engineer/consensus.py` — D-02's arithmetic over published consensus (AC-1.40)."""

import pytest

from src.feature_engineer.consensus import eps_surprise_pct, target_spread


def test_target_spread_is_median_low_high_and_empty_is_all_none():
    assert target_spread([170, 135, 150]) == {"n": 3, "median": 150, "low": 135, "high": 170}
    assert target_spread([140, 150]) == {"n": 2, "median": 145, "low": 140, "high": 150}
    assert target_spread(iter(())) == {"n": 0, "median": None, "low": None, "high": None}


def test_eps_surprise_is_relative_to_the_absolute_estimate():
    assert eps_surprise_pct(1.60, 1.91) == pytest.approx(19.375)
    assert eps_surprise_pct(-0.50, -0.25) == pytest.approx(50.0)   # a smaller loss beats


@pytest.mark.parametrize("est, act", [(None, 1.0), (0, 1.0), (1.0, None)])
def test_eps_surprise_is_none_when_undefined_never_a_default(est, act):
    assert eps_surprise_pct(est, act) is None
