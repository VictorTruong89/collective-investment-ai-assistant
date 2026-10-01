"""RA-154 (`L1-fundamental-analysis` §11.2, 2026-10-01) — an unmeasured verdict FLAGS.

⚠ The defect: `gate.py` mapped `agreement is None` to PASS, so every thesis
authored once (k=1, `verdict_stability = null`) passed the stability check by
absence of evidence. RA-49: *"a state with no row is a defect, not a default to
PASS."* `L8` §8 lesson 8; `L3` §2.1p item 2.
"""

from __future__ import annotations

import dataclasses
from datetime import date

import pytest

from src.fundamental.contracts.gate import FLAG, PASS, VETO
from src.fundamental.thesis.gate import GateInputs, evaluate
from src.fundamental.thesis.models import BUY
from tests_src.test_fundamental_b44 import thesis

AS_OF = date(2025, 6, 26)


def _status(stability, **kw):
    t = dataclasses.replace(thesis(verdict=BUY), verdict_stability=stability)
    return evaluate(GateInputs(thesis=t, **kw), as_of=AS_OF, ticker="MU")


@pytest.mark.parametrize("stability", [
    None,                                                     # authored once: no RM-1 result
    {},                                                       # empty record
    {"k": 1, "agreement": 1.0, "distribution": {"BUY": 1}},   # one run "agrees" with itself
    {"k": 2, "agreement": 1.0, "distribution": {"BUY": 2}},   # below K_STAB
])
def test_ra_154_an_unmeasured_buy_flags_and_never_passes(stability):
    v = _status(stability)
    assert v.status == FLAG, v.reason
    assert "unmeasured" in v.reason


def test_ra_154_a_measured_stable_buy_still_passes():
    """The fix must not touch a real k=3 measurement."""
    v = _status({"k": 3, "agreement": 1.0, "distribution": {"BUY": 3}})
    assert v.status == PASS


def test_ra_154_unmeasured_never_softens_a_stronger_row():
    """RA-135 still holds: a fired falsifier VETOes an unmeasured BUY."""
    assert _status(None, falsifier_fired=True).status == VETO
