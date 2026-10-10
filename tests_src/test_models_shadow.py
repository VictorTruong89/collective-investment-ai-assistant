"""D-04 shadow trial — MT-64 / AC-4.46 · MT-65 / AC-4.47 · MT-66 / AC-4.48. ✏ Written 2026-10-09.

★ A refused model is scored LIVE and never served: the only evidence about it that cannot be tuned.
Hermetic: tmp state, synthetic panels, a two-line estimator; no network.
"""

from __future__ import annotations

import json
import math
import pathlib
from datetime import date

import numpy as np
import pandas as pd
import pytest

ART = "sha256:" + "ab" * 32


class _Store:
    """The two ArtifactStore reads the trial needs."""

    def __init__(self, evaluation=None, manifest=None):
        self._files = {
            "evaluation.json": evaluation or {"walk_forward": {
                "mean_ic": 0.0296, "realised_se": 0.01178, "dates": 1994}},
            "manifest.json": manifest or {"feature_contract": {"content_hash": "sha256:cc"},
                                          "label_def_id": "fwd_ret_21d_open.xs_gauss"},
            "features.json": ["f1", "vol_20d"],
        }

    def read(self, artifact_id):
        if artifact_id != ART:
            raise KeyError(artifact_id)
        return self._files

    def is_retired(self, artifact_id):
        return False


# ── AC-4.46 · MT-64 — the trial ──────────────────────────────────────────────

def test_ac_4_46_start_freezes_the_artifact_and_the_criterion(tmp_path):
    from src.models.shadow.trial import CRITERION, load_trial, start_trial

    trial = start_trial(tmp_path, artifact_id=ART, store=_Store(), today=date(2026, 10, 9))
    assert trial["artifact_id"] == ART and trial["criterion"] == CRITERION
    assert trial["history"] == {"mean_ic": 0.0296, "realised_se": 0.01178, "dates": 1994}
    assert trial["comparator"].startswith("rule")
    assert load_trial(tmp_path) == trial


def test_ac_4_46_a_second_start_is_refused(tmp_path):
    from src.models.shadow.trial import ShadowError, start_trial

    start_trial(tmp_path, artifact_id=ART, store=_Store(), today=date(2026, 10, 9))
    with pytest.raises(ShadowError, match="already"):
        start_trial(tmp_path, artifact_id=ART, store=_Store(), today=date(2026, 10, 10))


def test_ac_4_46_an_artifact_without_a_walk_forward_cannot_start_a_trial(tmp_path):
    from src.models.shadow.trial import ShadowError, start_trial

    with pytest.raises(ShadowError, match="walk-forward"):
        start_trial(tmp_path, artifact_id=ART, store=_Store(evaluation={"ic": {}}),
                    today=date(2026, 10, 9))


def test_ac_4_46_no_card_side_domain_imports_the_shadow():
    root = pathlib.Path("src")
    for domain in ("orchestration", "reporting", "decision", "quant"):
        for path in (root / domain).rglob("*.py"):
            assert "models.shadow" not in path.read_text(encoding="utf-8"), path


# ── AC-4.47 · MT-65 — the snapshot ───────────────────────────────────────────

SESSIONS = tuple(d.date() for d in pd.bdate_range("2026-01-02", periods=80))


def test_ac_4_47_a_snapshot_within_21_sessions_of_the_last_is_refused():
    from src.models.shadow.record import assert_spacing
    from src.models.shadow.trial import ShadowError

    assert_spacing(None, SESSIONS[10], SESSIONS)                 # the first one
    assert_spacing(SESSIONS[10], SESSIONS[31], SESSIONS)         # exactly 21 later
    with pytest.raises(ShadowError, match="21"):
        assert_spacing(SESSIONS[10], SESSIONS[30], SESSIONS)


def test_ac_4_47_a_contract_mismatch_is_refused():
    from src.models.shadow.record import assert_contract
    from src.models.shadow.trial import ShadowError

    assert_contract("sha256:cc", "sha256:cc")
    with pytest.raises(ShadowError, match="INV-4"):
        assert_contract("sha256:dd", "sha256:cc")


class _Est:
    def predict(self, x):
        return x["f1"].to_numpy()


def _panel(n=12, as_of=SESSIONS[-1]):
    rows = []
    for k, d in enumerate(SESSIONS):
        for i in range(n):
            rows.append({"ticker": f"T{i:02d}", "date": pd.Timestamp(d), "f1": float(i),
                         "vol_20d": 0.02, "mom_21": float((i * 7) % n) + 0.01 * k,
                         "vol_21": 0.02})
    return pd.DataFrame(rows)


def test_ac_4_47_rankings_cover_the_same_names_for_model_and_rule():
    from src.models.shadow.record import rankings

    model, rule = rankings(_panel(), as_of=SESSIONS[-1], estimator=_Est(),
                           feature_names=("f1", "vol_20d"), horizon_days=21)
    assert [r["ticker"] for r in model][:3] == ["T11", "T10", "T09"], "ordered by ẑ (MT-60)"
    assert {r["ticker"] for r in model} == {r["ticker"] for r in rule}
    assert all("rank" in r for r in model + rule)


def test_ac_4_47_a_snapshot_is_write_once(tmp_path):
    from src.models.shadow.record import write_snapshot
    from src.models.shadow.trial import ShadowError

    snap = {"as_of": "2026-10-09", "artifact_id": ART, "model": [], "rule": []}
    path = write_snapshot(tmp_path, snap)
    assert json.loads(path.read_text())["as_of"] == "2026-10-09"
    with pytest.raises(ShadowError, match="write-once"):
        write_snapshot(tmp_path, snap)


# ── AC-4.48 · MT-66 — scoring and the pre-registered verdict ─────────────────

def test_ac_4_48_a_snapshot_matures_after_21_sessions_and_is_scored_on_open_to_open():
    from src.models.shadow.score import realised_returns

    rows = []
    for k, d in enumerate(SESSIONS[:30]):
        for i in range(3):
            rows.append({"ticker": f"T{i}", "date": pd.Timestamp(d),
                         "adj_open_minor": 100 * (1 + i * 0.001 * k)})
    prices = pd.DataFrame(rows)
    assert realised_returns(prices, SESSIONS[10], horizon_days=21) is None, "not matured"
    got = realised_returns(prices, SESSIONS[5], horizon_days=21)
    assert got["T0"] == pytest.approx(0.0)
    assert got["T2"] == pytest.approx((1 + 0.002 * 26) / (1 + 0.002 * 5) - 1)


def test_ac_4_48_snapshot_ic_is_the_spearman_of_ranking_and_realised():
    from src.models.shadow.score import snapshot_ic

    ranking = [{"ticker": t, "rank": r} for r, t in enumerate(["A", "B", "C", "D"], start=1)]
    realised = pd.Series({"A": 0.04, "B": 0.03, "C": 0.02, "D": 0.01})
    assert snapshot_ic(ranking, realised) == pytest.approx(1.0)
    assert snapshot_ic(ranking, -realised) == pytest.approx(-1.0)


def test_ac_4_48_the_pooled_verdict_follows_the_pre_registered_formula():
    from src.models.shadow.trial import pooled_verdict

    history = {"mean_ic": 0.0296, "realised_se": 0.01178, "dates": 1994}
    n_h = 1994 / 21
    sd = 0.01178 * math.sqrt(n_h)
    live = [0.05] * 12
    v = pooled_verdict(history, live)
    mean = (n_h * 0.0296 + 12 * 0.05) / (n_h + 12)
    assert v["pooled_mean_ic"] == pytest.approx(mean, rel=1e-6)
    assert v["pooled_t"] == pytest.approx(mean / (sd / math.sqrt(n_h + 12)), rel=1e-6)
    assert v["bar_met"] is (v["pooled_t"] >= 3)
    assert v["leakage_alarm"] is False


def test_ac_4_48_the_leakage_alarm_needs_six_observations_and_a_real_shortfall():
    from src.models.shadow.trial import pooled_verdict

    history = {"mean_ic": 0.0296, "realised_se": 0.01178, "dates": 1994}
    assert pooled_verdict(history, [-0.2] * 5)["leakage_alarm"] is None, "too few to judge"
    assert pooled_verdict(history, [-0.2] * 6)["leakage_alarm"] is True
    assert pooled_verdict(history, list(np.full(6, 0.02)))["leakage_alarm"] is False


def test_ac_4_46_the_command_starts_once_and_reports_status(tmp_path, monkeypatch, capsys):
    from src.models.shadow import __main__ as shadow

    class _S(_Store):
        root = tmp_path / "models"

        def load_estimator(self, artifact_id):
            return _Est() if artifact_id == ART else None

    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path))
    monkeypatch.setattr(shadow, "_store", lambda: _S())
    assert shadow.main(["start", ART]) == shadow.EXIT_OK
    assert "pre-registered" in capsys.readouterr().out
    assert shadow.main(["start", ART]) == shadow.EXIT_FAILED          # once only
    assert "already" in capsys.readouterr().err
    assert shadow.main(["status"]) == shadow.EXIT_OK
    out = capsys.readouterr().out
    assert "snapshots 0" in out and "pooled_t" in out and "does not promote" in out


def test_ac_4_47_a_shadow_never_writes_the_event_store():
    """DX-167 — `refresh` would overwrite the store's full-universe coverage record."""
    import inspect

    from src.models.shadow import __main__ as shadow

    source = inspect.getsource(shadow)
    assert "refresh_events=False" in source
    assert "record_refresh" not in source and "ingest.events import refresh" not in source


def test_ac_4_47_a_snapshot_inside_the_models_training_window_is_refused():
    """★ Found smoke-testing 2026-10-09: a snapshot dated 2026-08-04 scored IC +0.35 —
    fit 4 had seen returns through its training as_of (2026-10-08): its own homework.
    A snapshot dated T predicts open(T)→open(T+21); it is clean only if T ≥ that as_of."""
    from src.models.shadow.record import assert_out_of_sample
    from src.models.shadow.trial import ShadowError

    assert_out_of_sample(date(2026, 10, 8), "2026-10-08")
    assert_out_of_sample(date(2026, 11, 9), "2026-10-08")
    for inside in (date(2026, 8, 4), date(2026, 10, 7)):
        with pytest.raises(ShadowError, match="training window"):
            assert_out_of_sample(inside, "2026-10-08")


def test_ac_4_46_the_trial_records_what_the_model_has_seen(tmp_path):
    from src.models.shadow.trial import start_trial

    store = _Store(manifest={"feature_contract": {"content_hash": "sha256:cc"},
                             "label_def_id": "x",
                             "training_window": {"as_of": "2026-10-08",
                                                 "end": "2026-09-09T00:00:00"}})
    trial = start_trial(tmp_path, artifact_id=ART, store=store, today=date(2026, 10, 9))
    assert trial["returns_seen_through"] == "2026-10-08"


def test_ac_4_47_the_snapshot_date_defaults_to_the_latest_completed_session():
    """✏ 2026-10-09 (Victor's first `record`): FMP's EOD history posts a day's bar only after
    that day ends, so 'today' was refused. Default to the latest session in the data; a
    requested date that is not there yet is refused with the right reason."""
    from src.models.shadow.record import snapshot_date
    from src.models.shadow.trial import ShadowError

    sessions = [date(2026, 10, 7), date(2026, 10, 8)]
    assert snapshot_date(sessions, None) == date(2026, 10, 8)
    assert snapshot_date(sessions, date(2026, 10, 7)) == date(2026, 10, 7)
    with pytest.raises(ShadowError, match="after the close"):
        snapshot_date(sessions, date(2026, 10, 9))
