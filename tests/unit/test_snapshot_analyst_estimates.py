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


# ── L3 §2.1q decision 3 (Victor, 2026-10-02): a tracked home and a daily timer ──

def test_snapshots_live_in_a_version_controlled_path_never_under_state():
    """`DX-12`'s shape, fifth sighting: history under gitignored `.state/` dies with the laptop."""
    import subprocess

    from tools.snapshot_analyst_estimates import REPO, ROOT
    probe = ROOT / "MU" / "probe.json"
    ignored = subprocess.run(["git", "check-ignore", "-q", str(probe.relative_to(REPO))],
                             cwd=REPO).returncode == 0
    assert not ignored, f"{ROOT} is gitignored — snapshots there are not durable"
    assert ".state" not in ROOT.parts


def test_with_no_arguments_the_tickers_come_from_config():
    from tools.snapshot_analyst_estimates import configured_tickers
    assert configured_tickers() == ["MU", "AMD"]


def test_one_failing_ticker_does_not_stop_the_others_and_the_run_fails_loud(tmp_path, monkeypatch):
    import tools.snapshot_analyst_estimates as mod

    class Client:
        def get(self, endpoint, **params):
            if params["symbol"] == "MU":
                raise RuntimeError("HTTP 500")
            return [{"x": 1}]

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.run(["MU", "AMD"], Client()) == 1
    assert [p.parent.name for p in tmp_path.rglob("*.json")] == ["AMD"]


def test_the_timer_example_runs_weekdays_after_the_new_york_close_and_catches_up():
    from tools.snapshot_analyst_estimates import REPO
    timer = (REPO / "deploy/snapshot-analyst-estimates.timer.example").read_text()
    assert "OnCalendar=Mon..Fri 18:30 America/New_York" in timer
    assert "Persistent=true" in timer
    service = (REPO / "deploy/snapshot-analyst-estimates.service.example").read_text()
    assert "tools/snapshot_analyst_estimates.py" in service and "FMP_API_KEY=" not in service
