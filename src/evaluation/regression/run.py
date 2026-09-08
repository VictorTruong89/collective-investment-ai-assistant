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


def _matches(produced: object, expected: object) -> bool:
    """Does `produced` satisfy everything `expected` ASSERTS?

    ⚠⚠ `expected` is a **subset**, not a snapshot. A golden case states what the
    fund manager established — `value`, `unit`, `period`, `tags` — and says
    nothing about the rest of the item. ★ The keys it omits are not "don't
    care": they are things **`D2` did not let anyone establish**, because they
    come from the system (`quote`, `span`, `note`).

    ★★ Snapshot equality would have made the case circular in the exact way
    `D2` forbids: to write `expected` you would first run the system, copy its
    `quote` and character offsets, and thereafter be asserting that the system
    still produces what the system produced. **The subset rule is what keeps a
    golden value a claim about the DOCUMENT.**

    ⚠ It also keeps the case honest across a fixture re-render: character
    offsets move, the reading does not (`C13` moved every offset in this repo).

    Nested dicts recurse, so `period: {start, end}` is compared as a whole
    without asserting the keys beside it.
    """
    if isinstance(expected, dict) and isinstance(produced, dict):
        return all(k in produced and _matches(produced[k], v)
                   for k, v in expected.items())
    return produced == expected


def run_regression(cases: list[GoldenCase],
                   replay_response: Callable[[str], object]) -> RegressionReport:
    """Run every golden case against recorded responses.

    `replay_response(case.input_ref)` serves the recording. ⚠ It is the only door;
    a callable that reaches a vendor is a `D5` violation, not a slow test.

    ★ Comparison is **subset**, not equality — see `_matches`. A case asserts
    what was established and stays silent about what only the system knows.
    """
    passed: list[str] = []
    diverged: list[dict] = []
    for case in cases:
        produced = replay_response(case.input_ref)
        if _matches(produced, case.expected):
            passed.append(case.case_id)
        else:
            diverged.append({"case_id": case.case_id, "kind": case.kind,
                             "expected": case.expected, "produced": produced,
                             "established_by": case.established_by})
    return RegressionReport(tuple(passed), tuple(diverged),
                            "PASS" if not diverged else "FAIL")
