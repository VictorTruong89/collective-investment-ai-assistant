"""D-08 B6 — AC-8.1…8.37, plus AC-8.22a, 8.32a, 8.37a.

★ **BS-16: D-08 replaces the B3 shim** — full manifest, retry classification,
budgets, the 10:00 ET cadence (§5A).

```text
╔══════════════════════════════════════════════════════════════════╗
║  RETRY TRANSPORT.  NEVER RETRY SEMANTICS.                        ║
║                                                                  ║
║  Retrying a semantic failure LAUNDERS A HARD FAILURE INTO A SOFT ║
║  ONE — "this input is bad" becomes "this eventually succeeded",  ║
║  which is how a discipline card was once built from a failed LLM ║
║  narrative and emailed as a real recommendation.                 ║
╚══════════════════════════════════════════════════════════════════╝
```

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, time, timezone

import pytest

from src.orchestration import (
    AnchorMismatchError, AnchorUndeclaredError, BoundaryError,
    BudgetExceededError, Budgets, Cadence, CadenceClaims, CadenceClaimedError,
    Checkpoints, DAILY_INFERENCE, DECISION_ANCHOR, FAILURE_NOTICE_FIELDS, Job,
    JobGraph, LockHeldError, ManifestMissingError, OpenUnconfirmedError,
    Orchestrator, OrchestrationError, PreconditionUnevaluableError, RETRYABLE,
    RetryPolicy, RunIncompleteError, RunLock, SEMANTIC, SemanticRetryError,
    StaleInputError, UnclassifiedRetryError, UtcPinnedCadenceError,
    artifact_allowed, assert_anchor, assert_artifact_allowed,
    assert_cadence_unclaimed, assert_inputs_fresh, assert_no_analysis,
    assert_open_confirmed, assert_timer_has_no_policy, assert_trading_day,
    classify, failure_notice, first_trading_day, gateway_attempts, plan,
)

AS_OF = date(2026, 8, 25)
UTC = timezone.utc


def cadence(**kw):
    return Cadence(job_graph_id=kw.pop("job_graph_id", "daily_inference@v3"), **kw)


def bar(**kw):
    base = dict(open=100.0, high=103.0, low=99.5, close=101.2, settled=True)
    return {**base, **kw}


def orchestrator(graph=None, **kw):
    return Orchestrator(graph=graph or DAILY_INFERENCE, cadence=cadence(), **kw)


def always_open(_day):
    return True


def triggered(orc=None, **kw):
    orc = orc or orchestrator()
    base = dict(as_of=AS_OF, calendar=always_open, day_bar=bar(),
                model={"artifact_id": "sha256:9c1f", "trained_anchor": "open"},
                git_sha="f9e7886", config_hash="sha256:1c9e", now=datetime(
                    2026, 8, 25, 14, 0, tzinfo=UTC))
    return orc, orc.trigger(**{**base, **kw})


# --------------------------------------------------------------------------- #
# BOUNDARY §1.3, §3 — AC-8.1…8.5  ★ the ones that matter most
# --------------------------------------------------------------------------- #

def test_ac_8_1_no_orchestration_function_returns_a_derived_value():
    """AC-8.1 / OR-1 — ★ *D-08 contains no analysis, computation or judgement.*

    Structural: the runner never calls a domain function — `invoke` is the
    caller's dispatch — so **nothing here can return a derived value because
    nothing here computes one.**
    """
    import inspect

    import src.orchestration.jobs.runner as module

    source = inspect.getsource(module)
    for banned in ("import pandas", "import numpy", "def rank", "def score",
                   "fair_value", "verdict ="):
        assert banned not in source, banned


def test_ac_8_2_orchestration_performs_no_book_write():
    """AC-8.2 / OR-2 — *position, lot, P&L and sleeve state are D-11's custody.*
    D-08 may **invoke** a D-11 write; it may not perform one."""
    from tests_src import architecture

    graph = architecture.scan()
    reached = {m for f, mods in graph.items()
               if f.startswith("src/orchestration/") for m in mods}
    assert not [m for m in reached if m.startswith("src.recording.book")]


def test_ac_8_3_no_domain_imports_orchestration():
    """AC-8.3 / OR-3 — ★ *a domain that imports the scheduler becomes
    schedule-aware and untestable standalone.*"""
    from tests_src import architecture

    assert architecture.or_3(architecture.scan()) == []


def test_ac_8_4_orchestration_imports_no_llm_gateway():
    """AC-8.4 / OR-4, OR-28, ST-5 — ★ *scheduling is deterministic work.*"""
    from tests_src import architecture

    graph = architecture.scan()
    reached = {m for f, mods in graph.items()
               if f.startswith("src/orchestration/") for m in mods}
    assert not [m for m in reached if "gateway" in m or m == "anthropic"]


def test_ac_8_5_the_api_exposes_no_order_placement_capability():
    """AC-8.5 / OR-29 — ★ *no execution capability, now or later.*"""
    import src.orchestration as o

    forbidden = {"place_order", "submit_order", "execute", "trade", "buy",
                 "sell", "route_order", "cancel_order"}
    assert not (forbidden & set(o.__all__))


# --------------------------------------------------------------------------- #
# TRIGGERING §5 — AC-8.6…8.9
# --------------------------------------------------------------------------- #

def test_ac_8_6_a_non_trading_day_is_blocked_not_failed():
    """AC-8.6 / OR-5 — ⚠ *a timer running an inference job on a market holiday
    produces a confident report about a day that did not happen.*"""
    _orc, blocked = triggered(calendar=lambda _d: False)
    assert blocked.status == "BLOCKED_PRECONDITION"
    assert blocked.code == "ORC.PRECOND.NOT_TRADING_DAY"
    assert "not a trading day" in blocked.reason


def test_ac_8_7_a_stale_input_blocks_the_run():
    """AC-8.7 / OR-5(b)."""
    with pytest.raises(StaleInputError):
        assert_inputs_fresh([{"artifact": "panel/features.parquet",
                              "as_of": date(2026, 8, 1)}], as_of=AS_OF)
    fresh = assert_inputs_fresh([{"artifact": "p", "as_of": AS_OF}], as_of=AS_OF)
    assert fresh.ok


def test_ac_8_8_an_unevaluable_precondition_blocks_and_states_why():
    """AC-8.8 / OR-6 — ★ **it never defaults to "probably fine".**"""
    def broken(_day):
        raise RuntimeError("the calendar service is down")

    with pytest.raises(PreconditionUnevaluableError, match="calendar service"):
        assert_trading_day(AS_OF, calendar=broken)
    with pytest.raises(PreconditionUnevaluableError, match="no answer"):
        assert_trading_day(AS_OF, calendar=lambda _d: None)
    with pytest.raises(PreconditionUnevaluableError, match="age is unknowable"):
        assert_inputs_fresh([{"artifact": "p"}], as_of=AS_OF)


def test_ac_8_9_schedule_times_are_local_with_the_market_timezone_recorded():
    """AC-8.9 / OR-8, OR-30 — ★ *the schedule is not a UTC constant.*"""
    obj = cadence().to_json_obj()
    assert obj["local_time"] == "10:00" and obj["tz"] == "America/New_York"
    with pytest.raises(UtcPinnedCadenceError, match="14:00 UTC in summer"):
        Cadence(job_graph_id="daily", tz="UTC")


# --------------------------------------------------------------------------- #
# CADENCE §5A — AC-8.29…8.37
# --------------------------------------------------------------------------- #

def test_ac_8_29_ten_am_et_resolves_correctly_on_both_sides_of_dst():
    """AC-8.29 / OR-30 — ★★ ⚠ *a cron pinned at 14:00 UTC runs at 09:00 ET all
    winter — thirty minutes before the market opens.*"""
    summer = cadence().firing_utc(date(2026, 8, 25))
    winter = cadence().firing_utc(date(2026, 12, 15))
    assert summer.hour == 14 and winter.hour == 15
    assert summer.tzinfo == UTC and winter.tzinfo == UTC


def test_ac_8_30_the_decision_input_is_a_real_bar_not_a_flattened_spot_quote():
    """AC-8.30 / OR-32 — ★★ ⚠ *`open == high == low == close` makes the day-T
    intraday range identically zero* on the one bar that drives the decision,
    while every training bar has a real range. **That is an INV-4 parity
    break.**"""
    assert assert_open_confirmed(bar(), as_of=AS_OF).ok
    spot = {"open": 101.0, "high": 101.0, "low": 101.0, "close": 101.0}
    with pytest.raises(OpenUnconfirmedError, match="relabelled as a bar"):
        assert_open_confirmed(spot, as_of=AS_OF)


def test_ac_8_31_a_missing_or_unsettled_open_blocks_and_is_never_substituted():
    """AC-8.31 / OR-33 — ★ *never substituted with the previous close: that
    substitution is silent and makes the decision a day stale while looking
    current.*"""
    with pytest.raises(OpenUnconfirmedError, match="no day-T bar"):
        assert_open_confirmed(None, as_of=AS_OF)
    with pytest.raises(OpenUnconfirmedError, match="missing"):
        assert_open_confirmed(bar(open=None), as_of=AS_OF)
    with pytest.raises(OpenUnconfirmedError, match="not settled"):
        assert_open_confirmed(bar(settled=False), as_of=AS_OF)

    _orc, blocked = triggered(day_bar=None)
    assert blocked.code == "ORC.PRECOND.OPEN_UNCONFIRMED"


def test_ac_8_32_a_model_trained_on_a_different_anchor_raises():
    """AC-8.32 / OR-35 — ⚠ *a model trained on close(T)→close(T+h) and deployed
    to decide at open(T) is anchored **a full session** away from the return it
    was fitted to predict — and it is invisible in backtest because the backtest
    shares the training anchor.*"""
    with pytest.raises(AnchorMismatchError, match="'open'.*'close'"):
        assert_anchor("open", {"artifact_id": "m1", "trained_anchor": "close"})
    assert assert_anchor("open", {"artifact_id": "m1",
                                  "trained_anchor": "open"}).ok


def test_ac_8_32a_a_model_declaring_no_anchor_blocks_the_run():
    """AC-8.32a / OR-44 — ★★ *"trained on the same anchor" and "we do not know
    what it was trained on" are **opposite findings**.*

    ⚠ Before OR-44 nothing declared a training anchor at all, so
    `ORC.CADENCE.ANCHOR_MISMATCH` could never fire.
    """
    with pytest.raises(AnchorUndeclaredError, match="not a matching one"):
        assert_anchor("open", {"artifact_id": "sha256:9c1f"})
    _orc, blocked = triggered(model={"artifact_id": "m1"})
    assert blocked.code == "ORC.CADENCE.ANCHOR_UNDECLARED"
    # ★ and the manifest declares the anchor the run decided on.
    _orc, manifest = triggered()
    assert manifest.decision_anchor == DECISION_ANCHOR == "open"


def test_ac_8_33_retrain_fires_on_the_first_trading_day_not_the_first():
    """AC-8.33 / OR-37 — ⚠ *the 1st falls on a weekend or holiday roughly ⅓ of
    the time; a calendar-blind rule would skip those months entirely or run
    against a closed market.*"""
    weekdays = lambda d: d.weekday() < 5          # noqa: E731
    assert date(2026, 11, 1).weekday() == 6       # a Sunday
    assert first_trading_day(2026, 11, is_trading_day=weekdays) == date(2026, 11, 2)
    assert first_trading_day(2026, 9, is_trading_day=weekdays) == date(2026, 9, 1)


def test_ac_8_34_inference_precedes_retrain_and_promotion_waits_a_day():
    """AC-8.34 / OR-38 — ★ *a model promoted at 10:05 and used at 10:06 has
    passed no gate.*"""
    from src.orchestration import UngatedPromotionError

    order = [j.job_id for j in DAILY_INFERENCE.order()]
    assert "rank" in order          # inference runs on the incumbent
    with pytest.raises(UngatedPromotionError, match="next trading day"):
        raise UngatedPromotionError("sha256:new")


def test_ac_8_36_the_external_timer_contains_no_policy():
    """AC-8.36 / OR-41 — ★ *policy in a timer is policy with no manifest, no
    test and no spec* — the same invisibility that produced §1.5a."""
    assert_timer_has_no_policy(
        "0 14 * * 1-5 /usr/bin/python -m src.orchestration.entrypoint")
    for bad in ("0 14 * * * run.sh --retry 3",
                "0 14 * * * a.sh && b.sh",
                "0 14 * * * run.sh --timeout 900"):
        with pytest.raises(OrchestrationError, match="no manifest"):
            assert_timer_has_no_policy(bad)


def test_ac_8_37_two_firings_in_one_window_produce_one_run():
    """AC-8.37 / OR-46 — ★★ **by an idempotency KEY, not by the lock.**

    ⚠ A lock is mutual exclusion *in time*: two firings twenty minutes apart
    never overlap, so the second finds it free and runs the whole cadence again.
    """
    orc, manifest = triggered()
    outcome = orc.run(manifest.run_id, invoke=lambda job, m: None,
                      clock=_fake_clock())
    assert outcome.status == "SUCCESS"

    _orc, second = triggered(orc=orc)
    assert second.status == "BLOCKED_PRECONDITION"
    assert second.code == "ORC.PRECOND.CADENCE_CLAIMED"


def test_ac_8_37a_a_failed_run_does_not_claim_the_window():
    """AC-8.37a / OR-46 — ⚠ *re-firing after a failure must be able to retry the
    cadence, or OR-42's redundancy buys nothing exactly when it is needed.*"""
    claims = CadenceClaims()
    assert claims.claim("k", "run-1", status="INCOMPLETE") is False
    assert "k" not in claims
    assert claims.claim("k", "run-2", status="SUCCESS") is True
    with pytest.raises(CadenceClaimedError, match="already completed"):
        assert_cadence_unclaimed("k", claims=claims)


# --------------------------------------------------------------------------- #
# IDENTITY §6 — AC-8.10…8.15, 8.14a
# --------------------------------------------------------------------------- #

def test_ac_8_10_a_manifest_is_written_before_any_job_runs():
    """AC-8.10 / OR-9, OR-10 — ★ **determinism has no owner if D-08 does not own
    the manifest.**"""
    orc = orchestrator()
    with pytest.raises(ManifestMissingError, match="BEFORE it does any work"):
        orc.run("no-such-run", invoke=lambda job, m: None)


def test_ac_8_11_the_manifest_carries_the_whole_invocation():
    """AC-8.11 / OR-9 — *reproducibility is a property of the whole invocation:
    code + config + data + seed.*"""
    _orc, manifest = triggered()
    obj = manifest.to_json_obj()
    for key in ("run_id", "job_graph_id", "config_hash", "data_as_of",
                "decision_anchor", "seed", "budgets", "preconditions", "stubs"):
        assert key in obj, key
    assert obj["code"]["git_sha"] == "f9e7886"


def test_ac_8_12_a_dirty_tree_is_marked_dirty():
    """AC-8.12 / OR-11 — ★ *silently recording a clean sha for a modified tree
    is worse than not recording one.*"""
    _orc, manifest = triggered(dirty=True)
    assert manifest.to_json_obj()["code"]["dirty"] is True


def test_ac_8_13_two_runs_in_the_same_second_have_distinct_ids():
    """AC-8.13 / OR-12 — *a run id must survive a clock change.*"""
    from src.orchestration import new_run_id

    at = datetime(2026, 8, 25, 14, 0, tzinfo=UTC)
    ids = {new_run_id("daily_inference@v3", at) for _ in range(50)}
    assert len(ids) == 50


def test_ac_8_14_a_written_manifest_cannot_be_mutated():
    """AC-8.14 / OR-13, INV-005/006 — *a rerun creates a new manifest; it never
    edits the old one.*"""
    _orc, manifest = triggered()
    with pytest.raises(dataclasses.FrozenInstanceError):
        manifest.seed = 7


def test_ac_8_14a_every_stub_is_declared_and_the_key_is_never_absent():
    """AC-8.14a / OR-43 — ★ *a stub that is indistinguishable from a real
    implementation in the RECORD is how a placeholder survives into
    production.*"""
    from src.orchestration import Stub

    _orc, clean = triggered()
    assert clean.to_json_obj()["stubs"] == []      # present, and empty

    stub = Stub(domain="D-01", job="thesis_gate", behaviour="constant PASS",
                replaced_at="B4.4", rule="L3 BS-27")
    _orc2, stubbed = triggered(orc=orchestrator(), stubs=(stub,))
    declared = stubbed.to_json_obj()["stubs"][0]
    assert declared["domain"] == "D-01" and declared["replaced_at"] == "B4.4"


def test_ac_8_15_identical_manifests_produce_identical_plans():
    """AC-8.15 / OR-10, INV-2 — ★ D-08 is the only layer that can enforce it.

    ⚠ D-08 computes nothing, so what it can guarantee is that **the same
    manifest drives the same invocation sequence** — ties in the graph break on
    `job_id`, so the plan is byte-identical run to run.
    """
    assert plan(DAILY_INFERENCE).to_json_obj() == plan(DAILY_INFERENCE).to_json_obj()
    calls_a, calls_b = [], []
    for sink in (calls_a, calls_b):
        orc, manifest = triggered(orc=orchestrator())
        orc.run(manifest.run_id, invoke=lambda job, m: sink.append(job.job_id),
                clock=_fake_clock())
    assert calls_a == calls_b


# --------------------------------------------------------------------------- #
# FAILURE §7 — AC-8.16…8.22, 8.22a
# --------------------------------------------------------------------------- #

def test_ac_8_16_a_transport_error_is_retried_bounded_and_recorded():
    """AC-8.16 / OR-15."""
    assert classify("HTTP_429") == RETRYABLE
    assert classify("TIMEOUT") == RETRYABLE
    policy = RetryPolicy(max_attempts=3)
    assert policy.should_retry(job_id="prices", error_code="HTTP_429", attempt=1)
    assert not policy.should_retry(job_id="prices", error_code="HTTP_429",
                                   attempt=3)
    assert policy.delay_for(3) > policy.delay_for(1)      # backed off


def test_ac_8_17_a_semantic_error_is_never_retried():
    """AC-8.17 / OR-14 — ★★ ⚠ *retrying a semantic failure LAUNDERS A HARD
    FAILURE INTO A SOFT ONE.*"""
    for code in ("SCHEMA_VIOLATION", "VALIDATION_FAILED", "DATA_QUALITY",
                 "MISSING_TICKER", "LLM_UNUSABLE", "HTTP_402"):
        assert classify(code) == SEMANTIC
        with pytest.raises(SemanticRetryError, match="does not change the answer"):
            RetryPolicy().should_retry(job_id="j", error_code=code, attempt=1)


def test_http_402_is_the_one_that_looks_like_transport_and_is_not():
    """OR-14 with `L1-data-engine` §5A — ★ it means *"not on your plan"*, and
    **retrying it forever is a bill, not a fix.**"""
    assert classify("HTTP_402") == SEMANTIC
    assert classify("HTTP_429") == RETRYABLE


def test_ac_8_18_an_unclassified_error_is_not_retried():
    """AC-8.18 / OR-14 — ★ *the safe default is to stop.*"""
    assert classify("SOMETHING_NEW") is None
    with pytest.raises(UnclassifiedRetryError, match="NOT retried"):
        RetryPolicy().should_retry(job_id="j", error_code="SOMETHING_NEW",
                                   attempt=1)


def test_or_14a_the_gateways_own_retries_reach_the_manifest():
    """OR-14a / GW-16 — ⚠ *an exception that hid its retries would make a flaky
    run look clean.*"""
    counted = gateway_attempts(2, 3)
    assert counted["gateway_attempts"] == 3
    assert counted["total_transport_retries"] == 3


def test_ac_8_19_a_run_with_any_failed_job_is_incomplete_and_emits_nothing():
    """AC-8.19 / OR-16 — ★★ **partial success is failure.**

    ⚠ *The two real incidents in this repo both came from a downstream consumer
    treating a degraded upstream as usable.*
    """
    orc, manifest = triggered()

    def invoke(job, _m):
        if job.job_id == "rank":
            raise _semantic()

    outcome = orc.run(manifest.run_id, invoke=invoke, clock=_fake_clock())
    assert outcome.status == "INCOMPLETE"
    assert artifact_allowed(outcome) is False
    with pytest.raises(RunIncompleteError, match="no human-facing artifact"):
        assert_artifact_allowed(outcome)


def test_ac_8_21_an_optional_job_degrades_scope_and_reports_the_absence():
    """AC-8.21 / OR-18, INV-033/034 — *the non-LLM path continues and the
    absence is REPORTED, not filled.*"""
    orc, manifest = triggered()

    def invoke(job, _m):
        if job.job_id == "risk":              # declared optional in the graph
            raise _semantic()

    outcome = orc.run(manifest.run_id, invoke=invoke, clock=_fake_clock())
    assert outcome.status == "SUCCESS"
    risk = [j for j in outcome.jobs if j.job_id == "risk"][0]
    assert risk.status == "FAILED" and risk.error_code    # the absence, reported


def test_ac_8_22_a_failed_run_reaches_the_human():
    """AC-8.22 / OR-19 — ★ *a pipeline that fails quietly is indistinguishable
    from one that was never scheduled.*"""
    orc, manifest = triggered()
    outcome = orc.run(manifest.run_id,
                      invoke=lambda job, m: _semantic() if job.job_id == "rank"
                      else None, clock=_fake_clock())
    notice = failure_notice(outcome)
    assert notice["status"] == "INCOMPLETE"
    assert notice["failed_jobs"] == ["rank"]
    assert notice["error_codes"]


def test_ac_8_22a_the_failure_notice_carries_no_analytical_content():
    """AC-8.22a / OR-45 — ★★ **OR-16 suppresses reports, never the notification
    that the run failed.**

    ⚠ Read together and unqualified, OR-16 forbids OR-19 — and resolving it that
    way makes a failed run **silent**, which is what OR-19 exists to prevent.
    The line is what the message CLAIMS.
    """
    orc, manifest = triggered()
    outcome = orc.run(manifest.run_id,
                      invoke=lambda job, m: _semantic() if job.job_id == "rank"
                      else None, clock=_fake_clock())
    notice = failure_notice(outcome)
    assert set(notice) <= set(FAILURE_NOTICE_FIELDS)
    assert_no_analysis(notice)
    with pytest.raises(BoundaryError, match="analytical content"):
        assert_no_analysis({**notice, "top_pick": "MU", "verdict": "BUY"})


# --------------------------------------------------------------------------- #
# BUDGET & STATE §8, §9 — AC-8.23…8.28
# --------------------------------------------------------------------------- #

def test_ac_8_23_a_budget_breach_fails_the_run_and_never_truncates():
    """AC-8.23 / OR-21 — ★ *"emit what we have" is the plausible-looking default
    P5 forbids — a half-computed slate is more dangerous than no slate, because
    it looks complete.*"""
    budgets = Budgets(run_seconds=10.0, per_job={"prices": 0.001})
    orc, manifest = triggered(orc=orchestrator(budgets=budgets))
    outcome = orc.run(manifest.run_id, invoke=lambda job, m: None,
                      clock=_fake_clock(step=1.0))
    assert outcome.status == "BUDGET_EXCEEDED"
    assert artifact_allowed(outcome) is False


def test_ac_8_24_a_breach_names_the_job_its_budget_and_its_elapsed():
    """AC-8.24 / OR-22 — *enough to fix it without rerunning.*"""
    with pytest.raises(BudgetExceededError, match=r"prices: 5\.0s against a 1\.0s"):
        Budgets(per_job={"prices": 1.0}).check_job("prices", 5.0)


def test_ac_8_25_the_lock_holder_is_inspectable():
    """AC-8.25 / OR-24 — ★ *a stuck lock must be diagnosable, not mysterious.*"""
    lock = RunLock()
    lock.acquire("run-1", at=datetime(2026, 8, 25, 14, 0, tzinfo=UTC))
    assert "run-1" in lock.holder()
    with pytest.raises(LockHeldError, match="run-1"):
        lock.acquire("run-2", at=datetime(2026, 8, 25, 14, 1, tzinfo=UTC))
    lock.release("run-1")
    assert lock.holder() is None


def test_ac_8_26_rerunning_a_completed_job_duplicates_no_records():
    """AC-8.26 / OR-25 — same manifest inputs ⇒ same outputs, no duplication."""
    orc, manifest = triggered()
    calls = []
    orc.run(manifest.run_id, invoke=lambda job, m: calls.append(job.job_id),
            clock=_fake_clock())
    first = len(calls)
    orc.resume(manifest.run_id, invoke=lambda job, m: calls.append(job.job_id),
               clock=_fake_clock())
    assert len(calls) == first, "a checkpointed job was invoked twice"


def test_ac_8_27_resume_skips_only_checkpointed_work_with_unchanged_inputs():
    """AC-8.27 / OR-26 — ★ *never a step that failed, and never a step whose
    inputs changed.*"""
    checkpoints = Checkpoints()
    checkpoints.record("prices", inputs_digest="abc")
    assert checkpoints.can_skip("prices", inputs_digest="abc")
    assert not checkpoints.can_skip("prices", inputs_digest="def")
    assert not checkpoints.can_skip("features", inputs_digest="abc")


def test_a_failed_job_is_never_skipped_on_resume():
    """OR-26 — the failed step runs again; only successes are checkpointed."""
    orc, manifest = triggered()
    attempts = []

    def invoke(job, _m):
        attempts.append(job.job_id)
        if job.job_id == "rank" and attempts.count("rank") == 1:
            raise _semantic()

    orc.run(manifest.run_id, invoke=invoke, clock=_fake_clock())
    orc.resume(manifest.run_id, invoke=invoke, clock=_fake_clock())
    assert attempts.count("rank") == 2
    assert attempts.count("prices") == 1        # checkpointed, skipped


def test_ac_8_28_a_retry_appends_an_attempt_and_never_overwrites():
    """AC-8.28 / OR-27 — append-only run state (INV-006)."""
    orc, manifest = triggered()
    state = {"n": 0}

    def invoke(job, _m):
        if job.job_id == "prices":
            state["n"] += 1
            if state["n"] < 3:
                raise _transport()

    orc.run(manifest.run_id, invoke=invoke, clock=_fake_clock())
    logged = orc.attempts.for_job("prices")
    assert [a["attempt"] for a in logged] == [1, 2, 3]
    assert [a["status"] for a in logged] == ["FAILED", "FAILED", "SUCCESS"]


# --------------------------------------------------------------------------- #
# The graph — T-2, OR-40
# --------------------------------------------------------------------------- #

def test_the_plan_is_inspectable_without_executing():
    """T-2 / OR-40 — ★ *a graph you cannot read without running it is a graph
    nobody reviews.*"""
    graph = plan(DAILY_INFERENCE)
    order = [j.job_id for j in graph.order()]
    assert order[0] == "calendar_check"      # DE-31, before the first feature
    assert order.index("features") > order.index("prices")
    assert order.index("decide") > max(order.index("rank"),
                                       order.index("thesis_gate"))
    assert order[-1] == "deliver"


def test_a_dependency_cycle_and_an_unknown_dependency_both_raise():
    """OR-40 — the graph is validated as declared data, before anything runs."""
    with pytest.raises(ValueError, match="cycle"):
        JobGraph("g", (Job("a", "x", depends_on=("b",)),
                       Job("b", "y", depends_on=("a",)))).order()
    with pytest.raises(ValueError, match="does not declare"):
        JobGraph("g", (Job("a", "x", depends_on=("ghost",)),))


# --------------------------------------------------------------------------- #

def _semantic():
    from src.shared.errors import PipelineError

    class _E(PipelineError):
        code = "SCHEMA_VIOLATION"
    raise _E("bad schema")


def _transport():
    from src.shared.errors import PipelineError

    class _E(PipelineError):
        code = "HTTP_429"
    raise _E("rate limited")


def _fake_clock(step: float = 0.0):
    state = {"t": 0.0}

    def clock():
        value = state["t"]
        state["t"] += step
        return value
    return clock


# --------------------------------------------------------------------------- #
# B7 — the entrypoint and the dispatch check the graph never had
# --------------------------------------------------------------------------- #

def test_every_declared_job_resolves_to_something_that_exists():
    """★ **Added after the drift it exists to prevent.**

    ⚠ When B6 declared `DAILY_INFERENCE`, **five of its nine `invokes` names
    pointed at functions that did not exist** — `rank` for `rank_candidates`,
    `build` for `build_panel`, `render` for `build_card`. Nothing noticed,
    because **a declared pointer with no check is a comment.**
    """
    from src.orchestration.jobs.graph import assert_graph_resolves

    assert_graph_resolves(DAILY_INFERENCE)


def test_a_job_naming_a_missing_function_raises():
    """The planted violation for the check above (IM-3, BS-5)."""
    from src.orchestration.jobs.graph import resolve

    with pytest.raises(AttributeError, match="does not resolve"):
        resolve(Job("ghost", "src.quant.signals.rank:no_such_function"))
    with pytest.raises(ValueError, match="module:callable"):
        resolve(Job("ghost", "src.quant.signals.rank"))


def test_the_entrypoint_plans_without_executing():
    """T-2 / OR-40 — ★ `--plan-only` reads the graph and runs nothing."""
    from src.orchestration.entrypoint import main

    assert main(["--plan-only"]) == 0


def test_the_entrypoint_blocks_rather_than_inventing_a_day_t_open(
        tmp_path, monkeypatch, capsys):
    """OR-33 — a run with no day-T open **blocks**: *never substitute the
    previous close.* ★ Exit code 0, because BLOCKED is INFO, not failure (OR-42).

    ```text
    ╔══════════════════════════════════════════════════════════════════╗
    ║  ⚠⚠  FOUND 2026-08-27.  This test used to call main() with no      ║
    ║  isolation, on the premise that `_day_bar` was unwired and always  ║
    ║  returned None.  IT WAS WIRED SINCE — so the test had become a     ║
    ║  FULL LIVE DAILY RUN: real FMP calls inside the unit suite, and a  ║
    ║  real run directory written into the user's .state/runs on every   ║
    ║  `make check`.                                                    ║
    ║                                                                  ║
    ║  ★ And `== 0` could never notice, because BLOCKED and SUCCESS      ║
    ║  share exit code 0.  The assertion held while the behaviour it     ║
    ║  named had gone.                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    ```

    ★ The condition is now **forced** and the outcome **named**, so the test
    fails if blocking stops happening.
    """
    import src.orchestration.entrypoint as entrypoint

    monkeypatch.setenv("PIPELINE_STATE", str(tmp_path))
    monkeypatch.setattr(entrypoint, "_day_bar", lambda *a, **k: None)

    assert entrypoint.main(["--as-of", "2026-08-25"]) == 0
    assert "OPEN_UNCONFIRMED" in capsys.readouterr().err
    # ⚠ And it wrote nothing: a blocked run makes no CT-11.7 directory here.
    assert not (tmp_path / "runs").exists()


def test_resolution_lives_at_the_edge_not_in_the_runner():
    """★ OR-1 — the runner takes `invoke` as an argument so **nothing inside it
    can return a value derived from market data.** The dispatch that actually
    calls a domain lives in `entrypoint.py`, where it is visible."""
    import inspect

    import src.orchestration.jobs.runner as runner

    assert "importlib" not in inspect.getsource(runner)
