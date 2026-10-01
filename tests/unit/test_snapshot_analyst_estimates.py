"""`tools/snapshot_analyst_estimates.py` — we create the publication axis FMP lacks."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from tools.snapshot_analyst_estimates import snapshot

NOW = datetime(2026, 10, 1, 19, 30, tzinfo=timezone.utc)


class FakeClient:
    def __init__(self, rows):
        self.rows, self.calls = rows, []

    def get(self, endpoint, **params):
        self.calls.append((endpoint, params))
        return self.rows


def test_a_snapshot_is_stamped_with_when_we_observed_it(tmp_path):
    c = FakeClient([{"symbol": "MU", "date": "2027-08-31", "epsAvg": 40.0}])
    out = snapshot("mu", c, root=tmp_path, now=NOW)
    body = json.loads(out.read_text())
    assert out.name == "2026-10-01T193000Z.json" and body["observed_at"].startswith("2026-10-01")
    assert body["rows"][0]["date"] == "2027-08-31", "the target period is kept, and named as such"


def test_the_call_stays_inside_the_plan_gate(tmp_path):
    """`analyst-estimates` is 402 for period=quarter or limit >= 20."""
    c = FakeClient([{"x": 1}])
    snapshot("MU", c, root=tmp_path, now=NOW)
    (endpoint, params), = c.calls
    assert endpoint == "analyst-estimates" and params["period"] == "annual" and params["limit"] < 20


def test_a_snapshot_is_never_overwritten(tmp_path):
    snapshot("MU", FakeClient([{"x": 1}]), root=tmp_path, now=NOW)
    with pytest.raises(FileExistsError):
        snapshot("MU", FakeClient([{"x": 2}]), root=tmp_path, now=NOW)


def test_an_empty_answer_records_nothing(tmp_path):
    with pytest.raises(RuntimeError, match="nothing recorded"):
        snapshot("MU", FakeClient([]), root=tmp_path, now=NOW)
    assert not any(tmp_path.rglob("*.json"))
