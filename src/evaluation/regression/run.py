"""F5 `AC-5.7` / `D5` — the golden-set regression, on RECORDED responses.

★★ **CI replays `F2`'s recordings; it makes no live call.** Both halves already
existed when `D5` was decided: `F2` `CT-2.2` records every request and response,
and upstream already ships `pytest.mark.live` for the opt-in direction.

⚠ Live calls in CI were rejected: cost, flakiness, and **a suite that fails when
a vendor is down teaches people to ignore red** — which destroys it permanently.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.evaluation.golden.models import GoldenCase


class LiveCallInRegression(Exception):
    """⚠ `D5` — the regression reached the network. It must not."""


@dataclass(frozen=True, slots=True)
class RegressionReport:
    passed: tuple[str, ...]
    diverged: tuple[dict, ...]
    verdict: str                # PASS | FAIL

    @property
    def ok(self) -> bool:
        return self.verdict == "PASS"


def run_regression(cases: list[GoldenCase],
                   replay_response: Callable[[str], object]) -> RegressionReport:
    """Run every golden case against recorded responses.

    `replay_response(case.input_ref)` serves the recording. ⚠ It is the only door;
    a callable that reaches a vendor is a `D5` violation, not a slow test.
    """
    passed: list[str] = []
    diverged: list[dict] = []
    for case in cases:
        produced = replay_response(case.input_ref)
        if produced == case.expected:
            passed.append(case.case_id)
        else:
            diverged.append({"case_id": case.case_id, "kind": case.kind,
                             "expected": case.expected, "produced": produced,
                             "established_by": case.established_by})
    return RegressionReport(tuple(passed), tuple(diverged),
                            "PASS" if not diverged else "FAIL")
