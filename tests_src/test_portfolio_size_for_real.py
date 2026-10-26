"""F14 — the command on Victor's real holdings exports. AC-F14.18.

★ Skipped — loudly — wherever the files are absent (`DX-5`). A `--dry-run` only: no FMP
call, no policy needed for the capital to be read, nothing written.

Tier: reality probe.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import pytest

from tests_src.broker_fixtures import REAL

REPO = pathlib.Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    not (REAL / "Holdings_TFSA_2.csv").exists(),
    reason=f"needs Victor's real Holdings_TFSA_2.csv in {REAL} (never in git — RC-66, DX-5)")


def _dry(account):
    env = dict(os.environ, BMO_STATEMENTS_DIR=str(REAL), PYTHONDONTWRITEBYTECODE="1")
    env.pop("FMP_API_KEY", None)
    return subprocess.run(
        [sys.executable, "tools/size_for.py", "DELL", "--account", account, "--entry", "450",
         "--stop", "410", "--currency", "USD", "--dry-run"],
        cwd=REPO, env=env, capture_output=True, text=True, timeout=60)


def test_ac_f14_18_tfsa_2_reads_the_reported_capital_and_rate():
    """AC-F14.18."""
    out = _dry("TFSA_2")
    text = out.stdout.replace(",", "")
    assert "76805.55 CAD" in text and "2026-10-25" in text and "1.3999" in text


def test_ac_f14_18_tfsa_1_is_refused_by_name():
    """AC-F14.18 (RC-77)."""
    out = _dry("TFSA_1")
    assert out.returncode == 1
    assert "no holdings export for TFSA_1" in out.stdout + out.stderr
