"""D-11 — RC-67 (the check command) and RC-68 (the ingest log). AC-11.49 … AC-11.51.

✏ Written 2026-10-06 (L9 §11 K1/K2). Hermetic: synthetic exports in a tmp directory, written
here — never the real statements in `.state/broker/` (DX-5). Nothing touches the network.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

HEADER = ("Transaction Date,Settlement Date,Activity Description,Description,Symbol,"
          "Quantity,Price,Price Currency,Total Amount,Total Currency")
ROWS = [
    "2026-01-05,2026-01-07,Contribution,CONTRIBUTION,,0,0,CAD,5000.00,CAD",
    "2026-01-08,2026-01-10,Buy,FICTIONAL RAIL CO,FRC.B,100,10.00,CAD,-1009.95,CAD",
    "2026-02-02,2026-02-04,Buy,FICTIONAL TECH CORP,FTC,60,20.00,USD,-2009.95,USD",
    "2026-02-02,2026-02-04,Buy,FICTIONAL TECH CORP,FTC,40,20.00,USD,0.00,USD",
    "2026-05-05,2026-05-07,Sell,FICTIONAL RAIL CO,FRC.B,-40,12.00,CAD,470.05,CAD",
]


def _write(root: Path, account: str, rows) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"TransactionHistory_{account}.csv"
    path.write_text("\n".join([HEADER, *rows]) + "\n", encoding="utf-8")
    return path


def _report(root, log):
    from src.recording.check import check_exports

    return {a["account_id"]: a for a in check_exports(root=str(root), log_path=log)["accounts"]}


# ── RC-67 · AC-11.49 — the check command ────────────────────────────────────

def test_ac_11_49_every_account_is_reported_with_positions_and_cash(tmp_path):
    root = tmp_path / "exports"
    _write(root, "TFSA_1", ROWS)
    _write(root, "RRSP_1", ROWS[:2])
    acc = _report(root, tmp_path / "log.jsonl")
    tfsa = acc["TFSA_1"]
    assert tfsa["refusal"] is None
    assert tfsa["window"] == ["2026-01-05", "2026-05-05"] and tfsa["rows"] == 5
    assert tfsa["orders"] == 3, "the two FTC tranches are ONE order (RC-14)"
    assert tfsa["positions"] == {"FRC.B|COMMON|CAD": 60.0, "FTC|COMMON|USD": 100.0}
    assert tfsa["cash"] == {"CAD": 4460.1, "USD": -2009.95}
    assert set(acc) == {"TFSA_1", "RRSP_1"}, "discovered, not listed (RC-65)"


def test_ac_11_49_a_bad_file_is_named_and_the_others_still_report(tmp_path):
    root = tmp_path / "exports"
    _write(root, "TFSA_1", ROWS)
    # ⚠ the sell's buy is outside the window → a negative position (RC-45)
    _write(root, "TFSA_2", [ROWS[-1]])
    acc = _report(root, tmp_path / "log.jsonl")
    assert acc["TFSA_1"]["refusal"] is None
    assert "RC-45" in acc["TFSA_2"]["refusal"]


def test_ac_11_49_check_writes_nothing_and_exits_nonzero_on_refusal(tmp_path, capsys):
    from src.recording.check import main

    root = tmp_path / "exports"
    _write(root, "TFSA_1", ROWS)
    _write(root, "TFSA_2", [ROWS[-1]])
    log = tmp_path / "log.jsonl"
    before = sorted(p.name for p in tmp_path.rglob("*"))
    assert main(["--root", str(root), "--log", str(log)]) == 1
    assert sorted(p.name for p in tmp_path.rglob("*")) == before, "read-only"
    out = capsys.readouterr().out
    assert "TFSA_1" in out and "TFSA_2" in out and "REFUSED" in out


# ── RC-68 · AC-11.50 / AC-11.51 — the ingest log ─────────────────────────────

def _record(root, log):
    from src.recording.check import main

    return main(["--root", str(root), "--log", str(log), "--record"])


def test_ac_11_50_an_identical_file_is_a_no_op(tmp_path):
    root, log = tmp_path / "exports", tmp_path / "log.jsonl"
    _write(root, "TFSA_1", ROWS)
    assert _record(root, log) == 0
    assert _report(root, log)["TFSA_1"]["log"]["status"] == "unchanged"


def test_ac_11_50_a_changed_past_row_is_a_restatement(tmp_path):
    root, log = tmp_path / "exports", tmp_path / "log.jsonl"
    _write(root, "TFSA_1", ROWS)
    _record(root, log)
    changed = [*ROWS]
    changed[1] = changed[1].replace("-1009.95", "-1019.95")     # a silent correction
    _write(root, "TFSA_1", changed)
    entry = _report(root, log)["TFSA_1"]["log"]
    assert entry["status"] == "restatement"
    assert any("-1009.95" in r for r in entry["removed"])
    assert any("-1019.95" in r for r in entry["added"])


def test_ac_11_50_rows_after_the_window_are_new_activity_not_restatement(tmp_path):
    root, log = tmp_path / "exports", tmp_path / "log.jsonl"
    _write(root, "TFSA_1", ROWS)
    _record(root, log)
    _write(root, "TFSA_1", [*ROWS, "2026-09-01,2026-09-03,Dividend,FICTIONAL RAIL CO,"
                                   "FRC.B,0,0,CAD,7.20,CAD"])
    entry = _report(root, log)["TFSA_1"]["log"]
    assert entry["status"] == "new_activity" and entry["new_rows"] == 1
    assert entry["removed"] == [] and entry["added"] == []


def test_ac_11_50_a_window_that_starts_later_is_reported(tmp_path):
    root, log = tmp_path / "exports", tmp_path / "log.jsonl"
    _write(root, "TFSA_1", ROWS)
    _record(root, log)
    _write(root, "TFSA_1", ROWS[1:])
    entry = _report(root, log)["TFSA_1"]["log"]
    assert entry["window_starts_later"] is True


def test_ac_11_51_record_appends_and_never_rewrites(tmp_path):
    root, log = tmp_path / "exports", tmp_path / "log.jsonl"
    _write(root, "TFSA_1", ROWS)
    _record(root, log)
    first = log.read_text(encoding="utf-8")
    changed = [*ROWS]
    changed[1] = changed[1].replace("-1009.95", "-1019.95")
    _write(root, "TFSA_1", changed)
    _record(root, log)
    text = log.read_text(encoding="utf-8")
    assert text.startswith(first), "an earlier line is never rewritten"
    lines = [json.loads(x) for x in text.splitlines()]
    assert len(lines) == 2 and lines[1]["comparison"]["status"] == "restatement"


def test_ac_11_51_a_refused_account_is_not_recorded(tmp_path):
    root, log = tmp_path / "exports", tmp_path / "log.jsonl"
    _write(root, "TFSA_2", [ROWS[-1]])
    assert _record(root, log) == 1
    assert not log.exists() or log.read_text(encoding="utf-8") == ""


def test_ac_11_49_an_empty_export_directory_is_said_plainly(tmp_path, capsys):
    """RC-65 / AC-11.48 — no statements → exit 1 with the reason, never a traceback."""
    from src.recording.check import main

    (tmp_path / "exports").mkdir()
    assert main(["--root", str(tmp_path / "exports"), "--log", str(tmp_path / "l")]) == 1
    assert "no broker exports found" in capsys.readouterr().err


def test_the_default_log_lives_beside_the_exports_under_state():
    """RC-66 / RC-68 — `.state/broker/ingest_log.jsonl`, git-ignored with the exports."""
    from src.recording.check import DEFAULT_LOG

    assert Path(DEFAULT_LOG) == Path(".state/broker/ingest_log.jsonl")


@pytest.fixture(autouse=True)
def _no_real_statements(monkeypatch):
    """⚠ DX-5 — never let these tests fall back to the real statements."""
    monkeypatch.delenv("BMO_STATEMENTS_DIR", raising=False)
