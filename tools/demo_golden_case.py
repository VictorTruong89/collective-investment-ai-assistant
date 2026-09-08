#!/usr/bin/env python3
"""★ Watch a golden case work. `python3 tools/demo_golden_case.py`

⚠⚠ **Everything here is FAKE and thrown away.** It records a pretend extraction
into a temp directory so the mechanism can be *seen*. It establishes nothing,
touches no real trace, and writes nothing into the repo. `D2` still means the
fund manager establishes every real golden value.

It shows the one thing prose kept failing to convey: **what a golden case
actually catches, and when.**
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

# ★ Runnable from anywhere — this is a thing to be *shown*, so it must not
#   depend on the reader's working directory.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.evaluation.golden.models import GoldenCase  # noqa: E402
from src.evaluation.regression.replay import recorded_response  # noqa: E402
from src.evaluation.regression.run import run_regression  # noqa: E402
from src.orchestration.trace.models import ExternalCall  # noqa: E402
from src.orchestration.trace.store import TraceStore  # noqa: E402
from tools.f2_payload_reader import f2_payload_reader  # noqa: E402

RUN_ID, CALL_ID = "run-2026-09-05-demo", "extract-E-01-seg-revenue"

#: ⚠ The two figures are ARM's, from the `fmp-api` skill's measured table
#: (Q3: 1,242 discrete vs 3,430 cumulative, 2.76×). They are used here as an
#: ILLUSTRATIVE SHAPE — the period dates are invented and no filing was read.
#: ★ Named honestly because a demo that pairs one company's label with another
#: company's numbers is the exact quiet wrongness this project exists to catch.
#:
#: What the extractor returned the day the case was established. ★ This is the
#: `ExtractedItem` shape: `value` is a STRING in the document's own units.
TRUTHFUL = {
    "evidence_id": "seg.revenue",
    "value": "1,242",
    "unit": "millions of USD",
    "period": {"start": "2025-03-01", "end": "2025-05-29"},
    "status": "found",
    "tags": [],
}

#: ⚠ The SAME filing, read by a changed prompt: it returned the nine-month
#: column instead of the three-month one, and dropped the period start.
#: ★ Nothing about this is malformed. It validates. It is simply WRONG.
DRIFTED = {
    "evidence_id": "seg.revenue",
    "value": "3,430",
    "unit": "millions of USD",
    "period": {"start": None, "end": "2025-05-29"},
    "status": "found",
    "tags": [],
}


def _record(root: pathlib.Path, response: dict) -> None:
    """Record one pretend extraction call, exactly as F2 would."""
    store = TraceStore(root, RUN_ID)
    store.append(ExternalCall(
        run_id=RUN_ID, step_id="extract:E-01", call_id=CALL_ID, kind="llm",
        request={"prompt": "E-01", "bundle": "ARM_FY2025Q3_20F  # illustrative"},
        response=response, model_id="claude-opus-5", prompt_version="v1",
    ))
    store.close()


def _run(label: str, root: pathlib.Path, response: dict, case: GoldenCase) -> None:
    _record(root, response)
    report = run_regression([case], recorded_response(f2_payload_reader(root)))
    mark = "✅" if report.ok else "🔴"
    print(f"\n{mark} {label}  →  {report.verdict}")
    for d in report.diverged:
        print(f"     case      : {d['case_id']}")
        print(f"     expected  : {d['expected']['value']} "
              f"(period {d['expected']['period']})")
        print(f"     produced  : {d['produced']['value']} "
              f"(period {d['produced']['period']})")
        print(f"     ⚠ established by {d['established_by']} — ask them, not the code")


def main() -> None:
    # The case Victor established, months ago, by reading the filing.
    case = GoldenCase(
        case_id="arm-fy2025q3-seg-revenue", kind="extraction",
        input_ref=f"{RUN_ID}/{CALL_ID}", expected=TRUTHFUL,
        source="ARM 20-F, segment table, THREE months ended column (illustrative)",
        established_at="2026-09-05", established_by="Victor Truong",
    )

    print(__doc__.split("\n\n")[0])
    print("\nA golden case pins ONE reading of ONE document, so that a change to")
    print("the prompt or the model that alters that reading cannot pass quietly.")

    with tempfile.TemporaryDirectory() as tmp:
        _run("Today: the extractor still reads the filing the same way",
             pathlib.Path(tmp) / "a", TRUTHFUL, case)
        _run("Later: E-01 v2 ships, and quietly reads the YTD column instead",
             pathlib.Path(tmp) / "b", DRIFTED, case)

    print("\n★ The second run is the entire point. Nothing crashed, nothing was")
    print("  malformed, and `x01_verify_extraction` would still PASS it — the")
    print("  quote really is in the document. Only the golden case knows the")
    print("  system used to read it differently.")
    print("\n⚠ Without the case, that change ships silently and every downstream")
    print("  scorecard, thesis and valuation is built on 3,430 instead of 1,242.")


if __name__ == "__main__":
    main()
