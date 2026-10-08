"""D-04 — MT-53 / AC-4.35: the training run shows it is alive. ✏ Written 2026-10-07 (Victor).

Hermetic: no FMP key, so the run stops at its first network step — and the heartbeat must
still report the stage and the total on the way out.
"""

from __future__ import annotations

import inspect


def test_ac_4_35_training_runs_inside_a_heartbeat_and_names_its_stages():
    from src.models.train import __main__ as train

    assert "Heartbeat(" in inspect.getsource(train.main)
    body = inspect.getsource(train._train)
    for stage in ("fundamentals", "prices", "calendar check", "features panel",
                  "fit", "walk-forward", "portfolio simulation", "breadth",
                  "D-03 evaluation"):
        assert f'beat.stage("{stage}' in body, stage


def test_ac_4_35_an_early_stop_still_reports_the_total(monkeypatch, tmp_path, capsys):
    from src.models.train.__main__ import main

    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path / "state"))
    assert main(["--limit", "2", "--prepare-only"]) == 1        # BLOCKED: no FMP key
    err = capsys.readouterr().err
    assert "BLOCKED: FMP_API_KEY is not set" in err
    assert "⏱ train · done in" in err
