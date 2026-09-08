#!/usr/bin/env python3
"""★ Review the golden-case harness adversarially — try to make it lie.

    python3 tools/review_golden_case.py            # the four verdicts
    python3 tools/review_golden_case.py --verbose  # + every file and payload

⚠⚠ **Why this exists as a file rather than a snippet to paste.** A multi-line
heredoc pasted into a terminal breaks silently if the closing marker picks up
leading whitespace: bash stops recognising it as the terminator and swallows
everything after it, including your attempts to quit. ★ A review instrument you
cannot reliably start is not a review instrument.

**What it is for.** The demo (`demo_golden_case.py`) shows the harness working.
⚠ But the same author wrote the harness *and* the demo — the constitution names
that trap in §5.1: *"the agent wrote both the code and the test, so of course
they agree."* These four checks attack it instead:

    A  identical response                 → must PASS   (verdict is computed, not printed)
    B  value changed                      → must FAIL   (catches the obvious break)
    C  value IDENTICAL, period.start gone → must FAIL   (★ catches the SUBTLE one)
    D  recording deleted                  → must RAISE  (silence is impossible)

★★ **C is the one worth trusting the harness for.** A prompt change that keeps
the headline number but drops the period start leaves every downstream figure
looking correct while the period becomes unbounded — which `Period`'s docstring
calls *"reintroducing FMP's guess inside D-01"*. A comparison that only looked
at `value` would pass it.

⚠ Everything here is fake and thrown away. It establishes nothing (`D2`).
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.evaluation.golden.models import GoldenCase  # noqa: E402
from src.evaluation.regression.replay import (  # noqa: E402
    UnresolvableCase,
    recorded_response,
)
from src.evaluation.regression.run import run_regression  # noqa: E402
from src.orchestration.trace.models import ExternalCall  # noqa: E402
from src.orchestration.trace.store import TraceStore  # noqa: E402
from tools.f2_payload_reader import f2_payload_reader  # noqa: E402

TRUTH = {
    "evidence_id": "seg.revenue",
    "value": "1,242",
    "unit": "millions of USD",
    "period": {"start": "2025-03-01", "end": "2025-05-29"},
    "status": "found",
    "tags": [],
}


def _record(root: pathlib.Path, response: dict) -> None:
    store = TraceStore(root, "r")
    store.append(ExternalCall(
        run_id="r", step_id="s", call_id="c", kind="llm",
        request={"prompt": "E-01"}, response=response,
        model_id="claude-opus-5", prompt_version="v1",
    ))
    store.close()


def _case() -> GoldenCase:
    return GoldenCase(
        case_id="c1", kind="extraction", input_ref="r/c", expected=TRUTH,
        source="10-Q (illustrative)", established_at="2026-09-05",
        established_by="Victor",
    )


def _check(tag, title, want, root, response, verbose, delete=False) -> bool:
    _record(root, response)
    payload = root / "r" / "trace" / "payloads" / "c.json"
    if delete:
        payload.unlink()

    if verbose:
        print("\n" + "=" * 74)
        print(f"  {tag} · {title}")
        print("=" * 74)
        print("\n-- files F2 wrote --")
        for p in sorted(root.rglob("*")):
            if p.is_file():
                print(f"   {p.relative_to(root)}  ({p.stat().st_size} B)")
        print("\n-- trace.jsonl --")
        for line in (root / "r" / "trace.jsonl").read_text().splitlines():
            print("   " + line)
        print("\n-- payload c.json (what replay_response resolves) --")
        if payload.exists():
            for line in payload.read_text().splitlines():
                print("   " + line)
        else:
            print("   ⛔ DELETED")
        print("\n-- regression --")

    try:
        report = run_regression([_case()], recorded_response(f2_payload_reader(root)))
        got = report.verdict
        if verbose:
            print(f"   verdict : {report.verdict}")
            print(f"   passed  : {report.passed}")
            for d in report.diverged:
                print(f"   DIVERGED case={d['case_id']} kind={d['kind']}")
                print(f"     expected : {json.dumps(d['expected'])}")
                print(f"     produced : {json.dumps(d['produced'])}")
                print(f"     by       : {d['established_by']}")
    except UnresolvableCase:
        got = "RAISED"
        if verbose:
            print("   ⛔ raised UnresolvableCase (correct — not a pass, not a skip):")
            for line in traceback.format_exc().strip().splitlines()[-3:]:
                print("     " + line)

    ok = got == want
    print(f"{'✅' if ok else '⛔'} {tag}  {title:<46} → {got:<6} (want {want})")
    return ok


def main() -> int:
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    print(__doc__.splitlines()[0])
    if not verbose:
        print("⚠ Re-run with --verbose to see every file, payload and traceback.\n")

    with tempfile.TemporaryDirectory() as tmp:
        t = pathlib.Path(tmp)
        results = [
            _check("A", "identical response", "PASS", t / "a", TRUTH, verbose),
            _check("B", "value changed 1,242 → 3,430", "FAIL", t / "b",
                   {**TRUTH, "value": "3,430"}, verbose),
            _check("C", "value IDENTICAL, only period.start dropped", "FAIL", t / "c",
                   {**TRUTH, "period": {"start": None, "end": "2025-05-29"}}, verbose),
            _check("D", "recording deleted", "RAISED", t / "d", TRUTH, verbose,
                   delete=True),
        ]

    if all(results):
        print("\n★ All four behaved. ⚠ This proves the HARNESS notices a changed")
        print("  reading. It does NOT prove today's extractor reads correctly —")
        print("  no LLM ran here. That question needs a real golden value (D2).")
        return 0
    print("\n⛔ A check misbehaved. Do not trust the golden suite until it is explained.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
