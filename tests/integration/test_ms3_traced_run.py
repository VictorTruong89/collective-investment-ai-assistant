"""`MS-3`'s done-when: a full run is traced, and the trace replays. `AC-2.3`.

★★ **This is a REAL run of the REAL graph.** `DAILY_INFERENCE` — all 11 jobs (13 until 2026-10-05), in
dependency order — driven by the inherited `Orchestrator`, with its real cadence,
preconditions, budget, retry and checkpoint machinery. Nothing about D-08 is
simulated.

⚠ **What IS simulated: the dispatch.** `invoke(job, manifest)` returns fixtures
instead of calling vendors. That is not a shortcut around the test — it is the
architecture: D-08 *never* calls a domain function directly (`OR-1`), so dispatch
is a parameter, and substituting it is the same seam `AC-2.3`'s replay uses.
**A live run additionally exercises the vendors, the LLM and the money path; this
does not, and no claim here should be read as covering them** (`PG-10`).
"""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from src.orchestration.jobs.graph import DAILY_INFERENCE
from src.orchestration.jobs.runner import Orchestrator
from src.orchestration.schedule.cadence import Cadence
from src.orchestration.trace import (
    CapabilityDelta,
    DecisionRecord,
    StepRecord,
    TraceStore,
    mint_decision_id,
    replay,
    traced,
)

AS_OF = date(2026, 8, 25)


def _orchestrator() -> Orchestrator:
    return Orchestrator(graph=DAILY_INFERENCE,
                        cadence=Cadence(job_graph_id="daily_inference@v3"))


def _trigger(orc: Orchestrator):
    return orc.trigger(
        as_of=AS_OF, calendar=lambda _d: True,
        day_bar=dict(open=100.0, high=103.0, low=99.5, close=101.2, settled=True),
        model={"artifact_id": "sha256:9c1f", "trained_anchor": "open"},
        git_sha="f9e7886", config_hash="sha256:1c9e",
        now=datetime(2026, 8, 25, 14, 0, tzinfo=UTC))


def _fake_clock():
    t = iter(range(0, 10_000, 3))
    return lambda: float(next(t))


@pytest.fixture
def traced_run(tmp_path):
    """Run the real 13-job graph with the recorder attached."""
    orc = _orchestrator()
    manifest = _trigger(orc)
    store = TraceStore(tmp_path / "runs", run_id=manifest.run_id)

    outcome = orc.run(manifest.run_id,
                      invoke=traced(lambda job, m: {"job": job.job_id}, store),
                      clock=_fake_clock())
    store.close(status=outcome.status)
    return store, manifest, outcome


# --------------------------------------------------------------------------- #
# the done-when
# --------------------------------------------------------------------------- #
def test_ms3_a_full_run_of_the_real_graph_is_traced(traced_run):
    """★ Every job in `DAILY_INFERENCE` appears in the trace, in order."""
    store, manifest, outcome = traced_run
    assert outcome.status == "SUCCESS"

    steps = [r for r in store.read_all() if r["type"] == "StepRecord"]
    traced_ids = [s["job_id"] for s in steps]
    expected = [j.job_id for j in DAILY_INFERENCE.order()]
    assert traced_ids == expected, "every job, in dependency order"
    assert len(traced_ids) == 11    # ✏ 2026-10-05: observe + thesis removed
    assert all(s["run_id"] == manifest.run_id for s in steps)


def test_ms3_the_trace_joins_the_existing_run_record_and_adds_none(traced_run):
    """`AC-2.1` — F2 extends `RunManifest` downward; it writes no rival record."""
    store, manifest, _ = traced_run
    assert {p.name for p in store.run_dir.iterdir()} == {"trace.jsonl", "trace"}
    assert all(r["run_id"] == manifest.run_id for r in store.read_all())


def test_ms3_the_traced_run_replays(traced_run):
    """★★ `AC-2.3` — the done-when's second half."""
    store, _, _ = traced_run

    def re_execute(records, respond):
        orc = _orchestrator()
        manifest = _trigger(orc)
        out = TraceStore(store.run_dir.parent / "replayed", run_id=store.run_id)
        orc.run(manifest.run_id,
                invoke=traced(lambda job, m: {"job": job.job_id}, out),
                clock=_fake_clock())
        out.close(status="SUCCESS")
        return list(out.read_all())

    report = replay(store, re_execute)
    assert report.verdict == "REPRODUCED", report.first_divergence
    assert "given recorded external responses" in report.scope
    assert "started_at" in report.excluded_fields


def test_ms3_a_changed_graph_diverges_and_is_located(traced_run):
    """`AC-2.4` — the same run, one job renamed, must be located not just detected."""
    store, _, _ = traced_run

    def re_execute(records, respond):
        out = []
        for r in records:
            r = dict(r)
            if r.get("job_id") == "rank":
                r["node"] = "rank_v2"
            out.append(r)
        return out

    report = replay(store, re_execute)
    assert report.verdict == "DIVERGED"
    assert report.first_divergence["field"] == "node"
    assert report.first_divergence["recorded"] == "rank"


# --------------------------------------------------------------------------- #
# PG-9 / PG-5.2 inside a real run
# --------------------------------------------------------------------------- #
def test_ms3_pg9_and_pg52_records_attach_to_a_real_run(traced_run):
    """★★ The fields that **cannot be backfilled**, written during a real run."""
    store, manifest, _ = traced_run
    did = mint_decision_id(manifest.run_id, "NVDA", 1)

    store.append(DecisionRecord(
        run_id=manifest.run_id, step_id="job:rank", decision_id=did,
        state={"realised_vol_60d": 0.51}, candidates=["1w", "1m"], action="1w",
        reason="realised_vol_60d > 0.45", propensity=1.0))
    store.append(CapabilityDelta(
        run_id=manifest.run_id, decision_id=did, capability="config_influence",
        pre={"horizon": "1m"}, post={"horizon": "1w"}, changed=True))

    by_did = [r for r in store.read_all() if r.get("decision_id") == did]
    assert {r["type"] for r in by_did} == {"DecisionRecord", "CapabilityDelta"}
    assert all(r["run_id"] == manifest.run_id for r in by_did)


def test_ms3_a_failing_job_is_recorded_as_failed_and_still_raises(tmp_path):
    """⚠ `P5` — the recorder never swallows, and never decides."""
    orc = _orchestrator()
    manifest = _trigger(orc)
    store = TraceStore(tmp_path / "runs", run_id=manifest.run_id)

    def boom(job, m):
        if job.job_id == "features":
            raise RuntimeError("vendor down")
        return {"job": job.job_id}

    outcome = orc.run(manifest.run_id, invoke=traced(boom, store), clock=_fake_clock())
    steps = {r["job_id"]: r["status"] for r in store.read_all()
             if r["type"] == "StepRecord"}
    assert steps["features"] == "FAILED"
    assert steps["calendar_check"] == "SUCCESS"

    # ⚠⚠ The half that matters: the ORCHESTRATOR must also see the failure.
    # Found by mutation — deleting the `raise` left the StepRecord saying FAILED
    # while the runner saw a successful return, so the TRACE AND THE RUN
    # DISAGREED and every assertion above still passed. A recorder that can
    # alter the run it records is not an observer.
    assert outcome.status != "SUCCESS", (
        "the recorder must re-raise: swallowing it hides the failure from D-08's "
        "retry and budget logic, and makes the trace disagree with the run"
    )
    failed_jobs = {r.job_id for r in outcome.jobs if r.status == "FAILED"}
    assert "features" in failed_jobs


def test_ms3_the_recorder_does_not_change_the_outcome_of_a_clean_run(tmp_path):
    """★ The observer must be invisible: same run, traced and untraced."""
    def run_once(store):
        orc = _orchestrator()
        manifest = _trigger(orc)
        def inv(job, m):
            return {"job": job.job_id}
        return orc.run(manifest.run_id,
                       invoke=traced(inv, store) if store else inv,
                       clock=_fake_clock())

    untraced = run_once(None)
    traced_out = run_once(TraceStore(tmp_path / "runs", run_id="run-observer"))
    assert untraced.status == traced_out.status
    assert [j.status for j in untraced.jobs] == [j.status for j in traced_out.jobs]


def test_ms3_an_uncdlosed_run_is_unreplayable(tmp_path):
    """`AC-2.12` — a crashed run must not read as whole."""
    orc = _orchestrator()
    manifest = _trigger(orc)
    store = TraceStore(tmp_path / "runs", run_id=manifest.run_id)
    orc.run(manifest.run_id, invoke=traced(lambda j, m: None, store),
            clock=_fake_clock())
    # deliberately not closed
    assert replay(store, lambda r, s: r).verdict == "UNREPLAYABLE"


# --------------------------------------------------------------------------- #
# AC-2.7 / AC-2.11 — the join key, and provenance
# --------------------------------------------------------------------------- #
def test_ac_2_7_an_outcome_links_to_a_past_decision_without_re_deriving_the_id(
        traced_run, tmp_path):
    """`AC-2.7` — ★ this is what makes `F7b` possible years later.

    ⚠ The link is keyed by `decision_id` ALONE. Re-deriving it from run contents
    would tie the join to internals that change.
    """
    from src.orchestration.trace import OutcomeStore

    store, manifest, _ = traced_run
    did = mint_decision_id(manifest.run_id, "NVDA", 1)
    store.append(DecisionRecord(
        run_id=manifest.run_id, step_id="job:decide", decision_id=did,
        state={"v": 1}, candidates=["BUY", "HOLD"], action="BUY",
        reason="rank_1", propensity=1.0))

    outcomes = OutcomeStore(tmp_path / "outcomes")          # a DIFFERENT store
    outcomes.link(did, resolved_at="2026-12-01T00:00:00Z",
                  outcome={"return_1m": 0.031})

    # ⚠ A SECOND decision, so `for_decision` must actually match on the id.
    # Found by mutation: with one row, returning "the first" passed.
    other = mint_decision_id(manifest.run_id, "AMD", 1)
    outcomes.link(other, resolved_at="2026-12-01T00:00:00Z",
                  outcome={"return_1m": -0.014})

    linked = outcomes.for_decision(did)
    assert linked["decision_id"] == did
    assert linked["outcome"]["return_1m"] == 0.031
    assert outcomes.for_decision(other)["outcome"]["return_1m"] == -0.014
    assert outcomes.for_decision("run:NOPE:1") is None
    decision = [r for r in store.read_all() if r.get("decision_id") == did][0]
    assert decision["decision_id"] == linked["decision_id"], "joined by the id alone"


def test_ac_2_7_an_outcome_may_not_be_silently_revised(tmp_path):
    """⚠ Append-only: an unfavourable outcome must not be editable after the fact."""
    from src.orchestration.trace import OutcomeStore, TraceImmutableError

    outcomes = OutcomeStore(tmp_path / "outcomes")
    outcomes.link("run:NVDA:1", "2026-12-01T00:00:00Z", {"return_1m": -0.08})
    with pytest.raises(TraceImmutableError):
        outcomes.link("run:NVDA:1", "2026-12-02T00:00:00Z", {"return_1m": 0.08})
    assert outcomes.for_decision("run:NVDA:1")["outcome"]["return_1m"] == -0.08


def test_ac_2_11_a_step_that_resolved_a_variant_carries_provenance(tmp_path):
    """`AC-2.11` — `F1` `CT-1.4` on the step that resolved it (`AP-6`, `C8`).

    ⚠ Provenance is entry-derived (`AC-1.8`), so the record answers *"which
    implementation produced this?"* even if the object lies about itself.
    """
    from dataclasses import asdict

    from src.shared.registry import Registry

    reg = Registry()
    reg.register("ranking_model", "lightgbm", lambda: object(), version="2.1.0")
    prov = reg.provenance("ranking_model", "lightgbm")

    store = TraceStore(tmp_path / "runs", run_id="run-prov")
    store.append(StepRecord(run_id="run-prov", job_id="rank", step_id="job:rank",
                            node="rank", started_at="t", ended_at="t",
                            status="SUCCESS", provenance=asdict(prov)))

    rec = [r for r in store.read_all() if r["step_id"] == "job:rank"][0]
    assert rec["provenance"] == {"port": "ranking_model", "variant": "lightgbm",
                                 "version": "2.1.0", "experimental": False}
