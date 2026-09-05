"""CHARACTERIZATION — the inherited `Orchestrator.run` dispatch contract.

⚠⚠ **This test FREEZES behaviour. It does not claim the behaviour is correct.**
That distinction is the whole point of a characterization test: a frozen bug is
still a bug, and upstream records one (`_cumulative_fys`) that had a passing test
for two weeks.

★ **Why this contract and not another.** `F2`'s `traced()` (`src/orchestration/
trace/wire.py`) wraps `invoke` rather than editing `_run_one`, and that choice
rests on three inherited properties nobody wrote down:

  1. `run(run_id, *, invoke, clock)` calls `invoke(job, manifest)` **once per
     job**, in `graph.order()`;
  2. a job that raises is classified by the runner — the exception does **not**
     escape `run()`;
  3. `RunOutcome.jobs` carries one record per job in that same order.

⚠ If any of those changed, `traced()` would still import, still run, and silently
record a different history. **That is the failure this file exists to catch** —
constitution §5 item 3: *freeze inherited behaviour before building near it.*

⚠ `DX-11`: this is **one** characterization test, not an inventory. The other
inherited surfaces this repo consumes — `src/quant/metrics/`, the relay — remain
unfrozen, and that is recorded rather than closed.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from src.orchestration.jobs.graph import DAILY_INFERENCE
from src.orchestration.jobs.runner import Orchestrator
from src.orchestration.schedule.cadence import Cadence

AS_OF = date(2026, 8, 25)


def _orc() -> Orchestrator:
    return Orchestrator(graph=DAILY_INFERENCE,
                        cadence=Cadence(job_graph_id="daily_inference@v3"))


def _manifest(orc):
    return orc.trigger(
        as_of=AS_OF, calendar=lambda _d: True,
        day_bar=dict(open=100.0, high=103.0, low=99.5, close=101.2, settled=True),
        model={"artifact_id": "sha256:9c1f", "trained_anchor": "open"},
        git_sha="f9e7886", config_hash="sha256:1c9e",
        now=datetime(2026, 8, 25, 14, 0, tzinfo=UTC))


def _clock():
    t = iter(range(0, 10_000, 3))
    return lambda: float(next(t))


def test_characterization_invoke_is_called_once_per_job_in_graph_order():
    """FROZEN, not endorsed: one dispatch per job, in `graph.order()`."""
    orc = _orc()
    m = _manifest(orc)
    seen: list[str] = []
    orc.run(m.run_id, invoke=lambda job, _m: seen.append(job.job_id), clock=_clock())
    assert seen == [j.job_id for j in DAILY_INFERENCE.order()]
    assert len(seen) == len(set(seen)), "no job is dispatched twice"


def test_characterization_a_raising_job_does_not_escape_run():
    """FROZEN: the runner CLASSIFIES a failure; it does not propagate it.

    ⚠ `traced()` re-raises inside its `finally` on the assumption that `run()`
    catches. If that stopped being true, a traced run would crash where an
    untraced one completed — and the trace would be the cause.
    """
    orc = _orc()
    m = _manifest(orc)

    def boom(job, _m):
        if job.job_id == "features":
            raise RuntimeError("vendor down")

    outcome = orc.run(m.run_id, invoke=boom, clock=_clock())   # must not raise
    assert outcome.status != "SUCCESS"
    assert "features" in {j.job_id for j in outcome.jobs if j.status == "FAILED"}


def test_characterization_outcome_reports_one_record_per_job_in_order():
    """FROZEN: `RunOutcome.jobs` mirrors `graph.order()` one-for-one."""
    orc = _orc()
    m = _manifest(orc)
    outcome = orc.run(m.run_id, invoke=lambda job, _m: None, clock=_clock())
    assert [j.job_id for j in outcome.jobs] == [j.job_id for j in DAILY_INFERENCE.order()]


def test_characterization_dispatch_receives_the_manifest_it_was_triggered_with():
    """FROZEN: `invoke(job, manifest)` — the second argument is THE manifest.

    ⚠ `traced()` ignores it; `replayable_invoke()` relies on the arity.
    """
    orc = _orc()
    m = _manifest(orc)
    got: list[object] = []
    orc.run(m.run_id, invoke=lambda job, mf: got.append(mf), clock=_clock())
    assert got and all(x.run_id == m.run_id for x in got)
