"""Broker-statement test data — `DX-5` (collective-investment-ai-assistant `L3` §6.4).

THE PROBLEM
-----------
`test_recording_ingest.py`, `test_risk_flags_from_book.py` and
`test_recording_book_load.py` read **real BMO InvestorLine statements** from
`sdd/design/rel6_design/samples/bmo_investorline_transactions/`. That directory
is `.gitignore`d — correctly, it is real personal financial data — so it holds
**4 files on disk and 0 tracked**. ⚠ A fresh clone therefore **cannot run ~40 of
this repo's own tests**, and nobody noticed until the absorption rehearsal looked
from outside this machine.

THE SPLIT THAT MATTERS
----------------------
Those tests are not one kind of thing, and the fix is different for each:

★ **Structural** — RC-41/RC-55 column layouts, RC-12 zero totals, RC-46 dotted
  tickers, RC-13 unknown activities, RC-48 foreign rows, RC-49 disbursements,
  RK-5 a common share and its CDR. These assert **shape**, and shape is
  faithfully reproducible. They belong on the SYNTHETIC fixtures below and must
  pass on any clone.

⚠ **External truth** — *"derived cash matches the broker balance to the cent"*
  (RC-57), *"225 orders across four years"*, *"67 of 120 round trips close inside
  30 days"*. These are worth having **precisely because the data is real**.
  Rebuilding them on invented data would assert a property of fiction while
  looking like validation — strictly worse than not running them. They stay on
  the real exports and **skip loudly** when it is absent.

> ★★ The rule: **fixture what is shape, skip what is truth.** A synthetic
> external-truth check is not a weaker test, it is a false one.
"""

from __future__ import annotations

import os
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Tracked, synthetic, safe to publish. Every value is invented.
SYNTHETIC = REPO / "tests_src" / "fixtures" / "broker_statements"

#: The real exports. Untracked by design; present only on the fund manager's machine.
REAL = REPO / "sdd" / "design" / "rel6_design" / "samples" / "bmo_investorline_transactions"


def real_statements_dir() -> pathlib.Path | None:
    """The real exports, or None. Override with `BMO_STATEMENTS_DIR`."""
    override = os.environ.get("BMO_STATEMENTS_DIR")
    if override:
        p = pathlib.Path(override)
        return p if p.is_dir() else None
    return REAL if REAL.is_dir() else None


#: ⚠ Skips LOUDLY — the reason names what is missing and why it is not in git,
#: so a green-with-skips run is honest rather than mysterious (P5 in spirit:
#: an absent check announces itself).
requires_real_statements = pytest.mark.skipif(
    real_statements_dir() is None,
    reason=(
        "needs the real BMO InvestorLine exports, which are NOT in git (real "
        f"financial data; see .gitignore). Expected at {REAL} or $BMO_STATEMENTS_DIR. "
        "★ This test checks derived numbers against EXTERNAL TRUTH — a synthetic "
        "version would assert a property of invented data (DX-5, option A/B split). "
        "Structural parsing IS covered on any clone by test_recording_ingest_synthetic.py."
    ),
)


def synthetic(account: str) -> pathlib.Path:
    return SYNTHETIC / f"TransactionHistory_{account}.csv"
