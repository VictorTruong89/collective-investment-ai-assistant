"""D-08/D-09 RP-50…52, OR-50…52 — delivery is wired, and off unless asked."""
from datetime import date

import pytest

from src.orchestration.errors import OrchestrationError
from src.orchestration.jobs.wiring import RunContext, _deliver
from src.orchestration.schedule.preconditions import assert_inputs_fresh
from src.recording.artifacts.store import DELIVERY, record_run
from src.shared.secrets import Secret

AS_OF = date(2026, 8, 27)
RUN = "2026-08-27T02:00:00Z-daily_inference@v7-abc123"


class _Job:
    target = "src.reporting.deliver.email:send"


class _Manifest:
    run_id = RUN


def _card():
    """★ A REAL card through D-12 and D-09 — a stub card passed the first draft
    of these tests and hid the renderer entirely."""
    from src.decision import compose
    from src.fundamental import stub_gate_verdict
    from src.quant import Candidate, Nomination
    from src.reporting import build_card
    from src.risk import AlertSet, unchecked

    nomination = Nomination(
        as_of=AS_OF, run_id=RUN, decision_anchor="open",
        horizon_set=("production", 1), nominating_horizon="h1m",
        universe_n=510, model_artifact_id="sha256:85b75744",
        candidates=(Candidate("MNST", 1, 0.0263, 0.04),),
        contract_version="b3_minimal@v1", adj_as_of=date(2024, 8, 30),
        calendar_check_id="cal:test",
        excluded=({"ticker": "AVB", "reason": "delisted 2026-08-17"},))
    recommendation = compose(
        nomination=nomination,
        gate_verdicts=[stub_gate_verdict("MNST", AS_OF)],
        alert_set=AlertSet((), unchecked("no book (RK-29)")),
        run_id=RUN, as_of=AS_OF, gate_roster_declared=("thesis",),
        manifest_anchor="open", actionable=False,
        not_actionable_reason="no verdict stability",
        top_thesis_stability=None,
        stubs=({"domain": "D-01", "job": "thesis", "behaviour": "constant PASS",
                "replaced_at": "B4.4", "rule": "L3 BS-11"},))
    return build_card(recommendation, as_of=AS_OF)


class _Transport:
    """A hermetic SMTP — ★ nothing in this file sends real mail."""

    def __init__(self):
        self.sent = []

    def send_message(self, message):
        self.sent.append(message)


def _ctx(tmp_path, **kw):
    ctx = RunContext(as_of=AS_OF, adj_as_of=AS_OF, universe=("MNST",),
                     contract=None, artifact_root=tmp_path,
                     archive_root=tmp_path / "deliveries", **kw)
    ctx.outputs["render"] = _card()
    return ctx


#: ⚠ `src/reporting/__init__.py` re-exports the FUNCTION `deliver`, which
#: shadows the sub-package of the same name — so monkeypatch's dotted-string
#: form resolves to the function and fails. ★ The module object is fetched the
#: same way `resolve_target` fetches it, so both see one object.
def _email_module():
    import importlib

    return importlib.import_module("src.reporting.deliver.email")


def _patch_transport(monkeypatch, transport):
    """★ Inject the hermetic transport into D-09's own `deliver`, so the real
    archive → build_message → send path runs and only SMTP is replaced."""
    module = _email_module()
    real = module.deliver
    monkeypatch.setattr(module, "deliver",
                        lambda *a, **k: real(*a, **{**k, "transport": transport}))


@pytest.fixture()
def recorded(tmp_path):
    record_run(run_id=RUN, root=tmp_path, outcome={"status": "SUCCESS"})
    return tmp_path


# --------------------------------------------------------------------------- #
# ★★★ RP-50 — off by default, and it SAYS it did not send
# --------------------------------------------------------------------------- #

def test_without_the_flag_nothing_is_sent_and_the_job_says_so(recorded, monkeypatch):
    """AC-9.32 — ⚠ *Measured 2026-08-27:* this job reported **SUCCESS in
    0.000278 s having sent nothing**, which is worse than a failure — the
    outcome record asserted the artifact reached the human, and P6 is the
    constitutional claim it was falsifying."""
    sent = []
    monkeypatch.setattr(_email_module(), "send", lambda *a, **k: sent.append(a))

    result = _deliver(_Job(), _Manifest(), _ctx(recorded))

    assert result["sent"] is False and "--deliver" in result["why"]
    assert sent == []
    assert not (recorded / RUN / DELIVERY).exists()


def test_with_the_flag_the_card_is_sent_and_recorded(recorded, monkeypatch):
    """AC-9.32 — ★ end to end: D-09 sends, D-11 records, D-08 wires."""
    transport = _Transport()
    _patch_transport(monkeypatch, transport)

    result = _deliver(_Job(), _Manifest(), _ctx(
        recorded, deliver=True, recipient="someone@example.com",
        smtp_user=Secret("GMAIL_SMTP_USER", "sender@example.com"),
        smtp_password=Secret("GMAIL_APP_PASSWORD", "app-password")))

    assert result["sent"] is True
    assert len(transport.sent) == 1
    assert (recorded / RUN / DELIVERY).is_file()


def test_a_not_actionable_card_is_delivered_like_any_other(recorded, monkeypatch):
    """AC-9.34 / RP-52 — ⚠ a NOT ACTIONABLE day is information, and delivering
    only on action would make silence ambiguous between *nothing to do* and
    *the run did not happen* (DN-29)."""
    transport = _Transport()
    _patch_transport(monkeypatch, transport)

    _deliver(_Job(), _Manifest(), _ctx(
        recorded, deliver=True, recipient="someone@example.com",
        smtp_user=Secret("GMAIL_SMTP_USER", "sender@example.com"),
        smtp_password=Secret("GMAIL_APP_PASSWORD", "app-password")))

    assert "[NOT ACTIONABLE]" in transport.sent[0]["Subject"]


def test_a_missing_recipient_raises_rather_than_defaulting(recorded):
    """AC-9.33 / RP-51 — ⚠ it never falls back to the SMTP user: mail to the
    wrong address is not recoverable."""
    with pytest.raises(OrchestrationError, match="REPORT_RECIPIENT"):
        _deliver(_Job(), _Manifest(), _ctx(
            recorded, deliver=True, recipient="",
            smtp_user=Secret("GMAIL_SMTP_USER", "sender@example.com"),
            smtp_password=Secret("GMAIL_APP_PASSWORD", "app-password")))


def test_a_failed_send_propagates_and_the_record_survives(recorded, monkeypatch):
    """AC-8.38 / OR-50 — a failed delivery fails the run, ★ and the CT-11.7
    record is already on disk because `record` precedes `deliver`."""
    from src.reporting.errors import DeliveryFailedError

    monkeypatch.setattr(_email_module(), "deliver",
                        lambda *a, **k: (_ for _ in ()).throw(
                            DeliveryFailedError("smtp refused")))

    with pytest.raises(DeliveryFailedError):
        _deliver(_Job(), _Manifest(), _ctx(
            recorded, deliver=True, recipient="someone@example.com",
            smtp_user=Secret("GMAIL_SMTP_USER", "sender@example.com"),
            smtp_password=Secret("GMAIL_APP_PASSWORD", "app-password")))

    assert (recorded / RUN / "outcome.json").is_file()
    assert not (recorded / RUN / DELIVERY).exists()


# --------------------------------------------------------------------------- #
# ★★ OR-52 — the precondition that was passing vacuously
# --------------------------------------------------------------------------- #

def test_inputs_fresh_over_an_empty_list_is_not_evaluated():
    """AC-8.40 — ⚠ *Measured:* every real run recorded `inputs_fresh: true`
    having examined **zero inputs**. ★★ DE-56's shape inside the orchestrator's
    own guards: absence of evidence and evidence of absence are different."""
    check = assert_inputs_fresh([], as_of=AS_OF)
    assert check.ok is None
    assert "NOT EVALUATED" in check.detail
    assert check.to_json_obj()["ok"] is None


def test_inputs_fresh_still_passes_when_it_actually_checked_something():
    """OR-52 — the not-evaluated state replaces the vacuous pass, not the
    real one."""
    assert assert_inputs_fresh([{"artifact": "p", "as_of": AS_OF}],
                               as_of=AS_OF).ok is True
