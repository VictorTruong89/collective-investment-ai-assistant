"""D-11 CT-11.7 — the run artifact. ★ RC-59/60/61."""
import json

import pytest

from src.recording.artifacts.store import (
    INDEX_COLUMNS, RunArtifactStore, latest_thesis_for, rebuild_index,
    record_run,
)
from src.recording.errors import AppendOnlyViolation


def _run(root, run_id="r1", **over):
    payload = dict(
        run_id=run_id, root=root,
        manifest={"as_of": "2026-08-25", "job_graph_id": "daily_inference@v6"},
        outcome={"status": "SUCCESS"},
        recommendation={"candidate": {"ticker": "SNDK"},
                        "verdict": {"final": "BUY", "was_downgraded": False},
                        "actionable": False, "alerts_status": "UNCHECKED: x"},
        thesis={"bundle_hash": "sha256:abc", "verdict": "HOLD",
                "verdict_stability": {"agreement": 1.0}},
        renderings={"SNDK_2026-08-25.md": "# card"})
    payload.update(over)
    return record_run(**payload)


def test_ac_11_40_every_run_writes_the_five_parts(tmp_path):
    """RC-59 — ⚠ `ManifestStore` and `JournalStore` were both built and **neither
    was ever called**; every run's record evaporated at process exit."""
    _run(tmp_path)
    files = RunArtifactStore(tmp_path).read_run("r1")
    assert set(files) == {"manifest.json", "outcome.json", "recommendation.json",
                          "thesis.json", "SNDK_2026-08-25.md"}


def test_ac_11_40_a_blocked_run_is_recorded_too(tmp_path):
    """★ RC-33/OR-19 — *a failed run is a record, not an absence.* ⚠ An index of
    successes only makes every base rate measure the wrong population."""
    _run(tmp_path, run_id="blocked-1",
         outcome={"status": "BLOCKED_PRECONDITION"},
         recommendation=None, thesis=None, renderings=None)
    frame = rebuild_index(tmp_path)
    assert "BLOCKED_PRECONDITION" in frame["status"].tolist()


def test_ac_11_41_a_run_id_is_written_once(tmp_path):
    """RC-60 / OR-13 — ⚠ *overwriting would let a run's recorded inputs be
    adjusted to match its outputs*, and the temptation is highest on the record
    that says a verdict was wrong."""
    _run(tmp_path)
    with pytest.raises(AppendOnlyViolation):
        _run(tmp_path)


def test_ac_11_42_a_thesis_is_reused_for_an_unchanged_bundle(tmp_path):
    """★★ RC-61 — three Opus passes measured $1.34; an unchanged filing set
    would pay it again for evidence that did not move."""
    _run(tmp_path)
    assert latest_thesis_for("sha256:abc", root=tmp_path)["verdict"] == "HOLD"


def test_ac_11_42_a_changed_bundle_is_never_served_a_stale_thesis(tmp_path):
    """⚠ RA-2 — *two runs with DIFFERENT hashes are not comparable*, so a near
    miss must be a miss."""
    _run(tmp_path)
    assert latest_thesis_for("sha256:different", root=tmp_path) is None


def test_ac_11_42_the_newest_thesis_wins(tmp_path):
    """★ The cache is a lookup over an append-only history, not a single slot."""
    _run(tmp_path, run_id="a")
    _run(tmp_path, run_id="b",
         thesis={"bundle_hash": "sha256:abc", "verdict": "SELL"})
    assert latest_thesis_for("sha256:abc", root=tmp_path)["verdict"] == "SELL"


def test_ac_11_43_the_index_is_rebuildable_from_the_directories(tmp_path):
    """CT-11.7 — ★ *a convenience, never the record.* Deleting it costs nothing,
    which is what makes that claim checkable rather than asserted."""
    _run(tmp_path)
    (tmp_path / "runs.parquet").unlink()
    frame = rebuild_index(tmp_path)
    assert len(frame) == 1 and frame["ticker"].iloc[0] == "SNDK"


def test_ac_11_43_the_index_unpacks_the_verdict_object(tmp_path):
    """⚠ `verdict` is `{final, nominated, was_downgraded}` — D-12 records the
    gate's EFFECT, not just its result. ★ `was_downgraded` is what DN-17's veto
    rate counts, so the index must not flatten it away."""
    _run(tmp_path, recommendation={
        "candidate": {"ticker": "MU"},
        "verdict": {"final": "HOLD", "nominated": "BUY", "was_downgraded": True},
        "actionable": False})
    row = rebuild_index(tmp_path).iloc[0]
    assert row["verdict"] == "HOLD" and bool(row["was_downgraded"]) is True


def test_ac_11_43_an_unknown_actionable_is_not_reported_as_a_decided_no(tmp_path):
    """⚠ `bool(None)` is `False`. A run that recorded no recommendation has an
    UNKNOWN actionability, and reporting it as a decided "no" would be a claim
    the record never made."""
    _run(tmp_path, recommendation=None, thesis=None, renderings=None)
    assert rebuild_index(tmp_path)["actionable"].iloc[0] is None


def test_the_index_columns_answer_questions_the_specs_already_ask():
    """★ Every column has a named consumer — DN-17, RM-1, DN-38, DN-29."""
    for column in ("verdict", "was_downgraded", "agreement", "alerts_status",
                   "status", "bundle_hash"):
        assert column in INDEX_COLUMNS


def test_run_ids_are_chronological_by_lexical_order(tmp_path):
    """CT-8.1 — `run_id` begins with an ISO timestamp, which is what lets the
    thesis lookup walk history backwards without parsing anything."""
    _run(tmp_path, run_id="2026-08-25T01:00:00Z-g-aaa")
    _run(tmp_path, run_id="2026-08-26T01:00:00Z-g-bbb")
    assert RunArtifactStore(tmp_path).run_ids() == [
        "2026-08-25T01:00:00Z-g-aaa", "2026-08-26T01:00:00Z-g-bbb"]


def test_a_thesis_survives_a_json_round_trip_exactly(tmp_path):
    """★★ RC-61 — ⚠ **the cache was built before `Thesis.from_json_obj` existed
    and every lookup silently missed**: the lookup swallowed the failure, so it
    could only ever miss. *A cache that can only miss is decorative* — and it
    would have cost $1.34 a day while appearing to work."""
    from src.fundamental.thesis.models import Thesis
    from tests_src.test_fundamental_b44 import thesis

    original = thesis()
    assert Thesis.from_json_obj(original.to_json_obj()).to_json_obj() \
        == original.to_json_obj()


def test_a_rehydrated_falsifier_deadline_is_a_date_not_a_string():
    """RA-35 — ⚠ *"dated, not eventually"*. A string deadline would compare
    against `as_of` as TEXT and satisfy the rule with a value nothing can
    evaluate."""
    from datetime import date

    from src.fundamental.thesis.models import Thesis
    from tests_src.test_fundamental_b44 import thesis

    back = Thesis.from_json_obj(thesis().to_json_obj())
    assert isinstance(back.falsifiers[0].deadline, date)


def test_a_cached_thesis_carries_no_invented_runs(tmp_path):
    """★ RM-1's figure travels on the thesis (`verdict_stability`). ⚠ A
    fabricated run list would let a monitor count evidence that never
    happened."""
    from src.fundamental.thesis.author_for import _cached
    from tests_src.test_fundamental_b44 import thesis

    original = thesis()
    record_run(run_id="r1", root=tmp_path, thesis=original)
    hit = _cached(original.bundle_hash, tmp_path)
    assert hit is not None and hit.runs == ()


def test_a_stored_thesis_that_no_longer_meets_ct_1_1_is_not_served(tmp_path):
    """★ `__post_init__` runs on the way back in — a record written under an
    older contract raises rather than being silently trusted."""
    from src.fundamental.thesis.models import Thesis
    from tests_src.test_fundamental_b44 import thesis

    broken = thesis().to_json_obj()
    broken["falsifiers"] = []                  # CT-1.1 requires a minimum
    with pytest.raises(Exception):
        Thesis.from_json_obj(broken)
