"""D-11 RC-62/63/64 — the run record names what produced it."""
import json

import pytest

from src.recording.artifacts.store import (
    DELIVERY, INDEX_COLUMNS, RECOMMENDATION, RunArtifactStore, rebuild_index,
    record_delivery, record_run,
)
from src.recording.errors import AppendOnlyViolation

RUN = "2026-08-27T02:00:00Z-daily_inference@v7-abc123"


class _Nomination:
    """Stands in for D-03's CT-3.4 — ★ it is passed as a CONTRACT OBJECT, so
    the test also pins that D-11 calls `to_json_obj()` and normalises nothing."""

    def to_json_obj(self):
        return {"universe_n": 510, "model_artifact_id": "sha256:85b75744",
                "candidates": [{"ticker": "MNST", "rank": 1}],
                "excluded": [{"ticker": "AVB", "reason": "delisted 2026-08-17"},
                             {"ticker": "EQR", "reason": "delisted 2026-08-18"}]}


def _record(tmp_path, **kw):
    record_run(run_id=RUN, root=tmp_path,
               manifest={"job_graph_id": "daily_inference@v7", "as_of": "2026-08-27"},
               outcome={"status": "SUCCESS"},
               recommendation={"candidate": {"ticker": "MNST"}, "verdict": "BUY",
                               "actionable": False},
               **kw)
    return json.loads((tmp_path / RUN / RECOMMENDATION).read_text())


# --------------------------------------------------------------------------- #
# ★★★ RC-62 — the nomination is folded into recommendation.json
# --------------------------------------------------------------------------- #

def test_recommendation_json_carries_the_nomination(tmp_path):
    """AC-11.44 — the ranked slate, excluded[] with reasons, universe_n and
    model_artifact_id all reach disk.

    ⚠ *Measured 2026-08-27 before this:* `grep` for the promoted model's hash
    across a complete run directory found **nothing** — the record could not
    answer *"what made this pick?"* (QA-121, INV-2)."""
    payload = _record(tmp_path, nomination=_Nomination())
    nomination = payload["nomination"]

    assert nomination["model_artifact_id"] == "sha256:85b75744"
    assert nomination["universe_n"] == 510
    assert [e["ticker"] for e in nomination["excluded"]] == ["AVB", "EQR"]
    assert "delisted 2026-08-17" in nomination["excluded"][0]["reason"]
    # ★ The recommendation's own fields are untouched beside it.
    assert payload["verdict"] == "BUY"


def test_the_model_is_greppable_from_the_run_directory(tmp_path):
    """AC-11.44 — ★ the regression stated as the user would check it."""
    _record(tmp_path, nomination=_Nomination())
    blob = "".join(p.read_text() for p in (tmp_path / RUN).iterdir())
    assert "85b75744" in blob


def test_a_nomination_without_a_recommendation_is_still_recorded(tmp_path):
    """RC-62 — ⚠ a run that ranked and did not decide is a real state; dropping
    the nomination would erase the only evidence the ranking happened."""
    record_run(run_id=RUN, root=tmp_path, outcome={"status": "INCOMPLETE"},
               nomination=_Nomination())
    payload = json.loads((tmp_path / RUN / RECOMMENDATION).read_text())
    assert payload["nomination"]["universe_n"] == 510


def test_no_nomination_leaves_the_recommendation_untouched(tmp_path):
    """RC-62 — the fold is additive; a run without one is unchanged."""
    assert "nomination" not in _record(tmp_path)


# --------------------------------------------------------------------------- #
# ★ RC-63 — delivery.json
# --------------------------------------------------------------------------- #

class _Delivery:
    def to_json_obj(self):
        return {"delivery_id": "abc123", "outcome": "SENT",
                "recipient_hash": "deadbeef"}


def test_a_delivery_writes_its_record_beside_the_run(tmp_path):
    """AC-11.45 — a delivered run writes delivery.json."""
    _record(tmp_path)
    record_delivery(RUN, root=tmp_path, delivery=_Delivery())
    assert json.loads((tmp_path / RUN / DELIVERY).read_text())["outcome"] == "SENT"


def test_a_run_that_did_not_deliver_writes_no_delivery_file(tmp_path):
    """AC-11.45 — ⚠ absence means NOT DELIVERED, never unknown (DE-35). An
    empty file or an `outcome: ""` placeholder would conflate the two."""
    _record(tmp_path)
    assert not (tmp_path / RUN / DELIVERY).exists()


def test_a_second_delivery_record_raises(tmp_path):
    """RC-60 — a re-send is a new delivery_id, never a rewritten record."""
    _record(tmp_path)
    record_delivery(RUN, root=tmp_path, delivery=_Delivery())
    with pytest.raises(AppendOnlyViolation):
        record_delivery(RUN, root=tmp_path, delivery=_Delivery())


def test_a_delivery_for_an_unrecorded_run_raises(tmp_path):
    """RC-63 — ★ `record` precedes `deliver` (OR-50); a delivery with no run
    directory means the ordering broke, and it is reported not created."""
    with pytest.raises(AppendOnlyViolation):
        record_delivery(RUN, root=tmp_path, delivery=_Delivery())


# --------------------------------------------------------------------------- #
# ★ RC-64 — the index
# --------------------------------------------------------------------------- #

def test_the_index_carries_the_new_columns(tmp_path):
    """AC-11.46 — runs.parquet carries excluded_n and model_artifact_id and is
    still rebuilt from the directories."""
    _record(tmp_path, nomination=_Nomination())
    record_delivery(RUN, root=tmp_path, delivery=_Delivery())
    row = rebuild_index(tmp_path).iloc[0]

    assert row["model_artifact_id"] == "sha256:85b75744"
    assert row["universe_n"] == 510
    assert row["excluded_n"] == 2
    assert row["delivery_status"] == "SENT"
    for column in ("universe_n", "excluded_n", "model_artifact_id",
                   "delivery_status"):
        assert column in INDEX_COLUMNS


def test_excluded_n_distinguishes_none_from_zero(tmp_path):
    """RC-64 — ⚠ `None` when there was no nomination, `0` when nothing was
    barred. *We did not rank* and *we barred nobody* are different facts."""
    _record(tmp_path)
    assert rebuild_index(tmp_path).iloc[0]["excluded_n"] is None


def test_delivery_status_is_blank_when_nothing_was_delivered(tmp_path):
    """RC-63/64 — the index reports not-delivered as such."""
    _record(tmp_path)
    assert rebuild_index(tmp_path).iloc[0]["delivery_status"] == ""
