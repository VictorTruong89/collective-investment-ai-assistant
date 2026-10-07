"""D-08 — AC-8.22 (OR-19) delivered, not only composed. ✏ Written 2026-10-06 (L9 §9 O2).

⚠ The existing AC-8.22 test checks that `failure_notice` is COMPOSED. Nothing sent it: the
entrypoint printed it to stderr, while a successful `--deliver` run emails the card — so a
failed delivering run was silent on the channel the human watches. OR-19: *a failed run
reaches the human by the same channel a success would.* OR-45: the notice carries no
analytical content. Hermetic — a fake transport; no SMTP, no network.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from src.shared.secrets import Secret

T0 = datetime(2026, 10, 6, 14, 0, tzinfo=timezone.utc)


def _outcome():
    jobs = (SimpleNamespace(job_id="prices", status="SUCCESS", error_code=None),
            SimpleNamespace(job_id="rank", status="FAILED", error_code="SCHEMA_VIOLATION"))
    return SimpleNamespace(run_id="run-x", status="INCOMPLETE", jobs=jobs,
                           started_at=T0, ended_at=T0)


def _context(deliver=True, recipient="pm@example.invalid"):
    return SimpleNamespace(deliver=deliver, recipient=recipient,
                           smtp_user=Secret("GMAIL_SMTP_USER", "bot@example.invalid"),
                           smtp_password=Secret("GMAIL_APP_PASSWORD", "x"))


class _Transport:
    def __init__(self, fail=False):
        self.sent, self.fail = [], fail

    def send_message(self, message):
        if self.fail:
            raise OSError("smtp down")
        self.sent.append(message)


def test_ac_8_22_a_failed_delivering_run_emails_its_notice(capsys):
    """AC-8.22 / OR-19 — ★ same channel as a success: with `--deliver`, the notice is SENT."""
    from src.orchestration.entrypoint import _announce_failure

    transport = _Transport()
    _announce_failure(_outcome(), _context(), transport=transport)
    (message,) = transport.sent
    assert message["To"] == "pm@example.invalid"
    assert "INCOMPLETE" in message["Subject"] and "run-x" in message["Subject"]
    body = message.get_content()
    assert "rank" in body and "SCHEMA_VIOLATION" in body
    assert "INCOMPLETE run-x" in capsys.readouterr().err, "stderr still carries it"


def test_ac_8_22a_the_emailed_notice_carries_only_the_notice_fields():
    """AC-8.22a / OR-45 — no attachment, no card, no verdict: a notice, not a report."""
    from src.reporting.deliver.email import build_failure_message

    notice = {"run_id": "run-x", "status": "INCOMPLETE", "failed_jobs": ["rank"],
              "error_codes": ["SCHEMA_VIOLATION"], "started_at": T0.isoformat(),
              "ended_at": T0.isoformat()}
    message = build_failure_message(notice, sender="a@x.invalid", recipient="b@x.invalid")
    assert not list(message.iter_attachments())
    with pytest.raises(ValueError, match="OR-45"):
        build_failure_message({**notice, "verdict": "BUY"},
                              sender="a@x.invalid", recipient="b@x.invalid")


def test_ac_8_22_without_deliver_nothing_is_sent(capsys):
    """RP-50 — delivery is off unless asked: the notice goes to stderr only."""
    from src.orchestration.entrypoint import _announce_failure

    transport = _Transport()
    _announce_failure(_outcome(), _context(deliver=False), transport=transport)
    assert transport.sent == []
    assert "INCOMPLETE run-x" in capsys.readouterr().err


def test_ac_8_22_a_failed_notice_send_is_itself_loud(capsys):
    """P5 — if the failure email cannot be sent, that is said, never swallowed."""
    from src.orchestration.entrypoint import _announce_failure

    _announce_failure(_outcome(), _context(), transport=_Transport(fail=True))
    err = capsys.readouterr().err
    assert "failure notice could NOT be emailed" in err


def test_ac_8_22_no_recipient_is_loud_not_defaulted(capsys):
    """RP-51 — the recipient is never defaulted to the sending account."""
    from src.orchestration.entrypoint import _announce_failure

    transport = _Transport()
    _announce_failure(_outcome(), _context(recipient=""), transport=transport)
    assert transport.sent == []
    assert "REPORT_RECIPIENT" in capsys.readouterr().err


def test_ac_8_39_the_entrypoint_stamps_a_real_sha_and_config_hash(monkeypatch):
    """AC-8.39 / OR-51 — ★ the manifest's provenance is SUPPLIED, never the empty default.

    ✏ Written 2026-10-06 (L9 §9 O5). Captures what `main()` hands `trigger()` and stops
    the run there (a blocked precondition), so nothing is fetched or written.
    ⚠ **Partial by finding, not by omission:** AC-8.39 also names `inputs`, and the
    entrypoint passes NONE — the inputs are fetched after the manifest is written (OR-9),
    so `inputs` stays `[]` and OR-52 reports freshness NOT EVALUATED. Recorded in L9 §9
    (O8), not asserted away here.
    """
    from src.orchestration import entrypoint
    from src.orchestration.contracts.manifest import git_state
    from src.orchestration.schedule.preconditions import BlockedPrecondition

    seen = {}

    class _Orc:
        graph = None

        def trigger(self, **kw):
            seen.update(kw)
            return BlockedPrecondition(job_graph_id="g", as_of=kw["as_of"],
                                       code="TEST.STOP", reason="captured")

    monkeypatch.setattr(entrypoint, "build_orchestrator", lambda **k: _Orc())
    monkeypatch.setattr(entrypoint, "_day_bar", lambda *a, **k: None)
    monkeypatch.setattr(entrypoint, "_incumbent_model", lambda: None)
    assert entrypoint.main(["--as-of", "2026-08-25"]) == entrypoint.EXIT_BLOCKED

    sha, dirty = git_state()
    assert seen["git_sha"] and seen["git_sha"] == sha
    assert seen["dirty"] == dirty
    assert seen["config_hash"] and seen["config_hash"].startswith("sha256:")
