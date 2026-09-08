"""F5 `CT-5.2` / `D2` — golden cases, and who is allowed to establish one.

⚠⚠ **`D2`: the fund manager establishes every golden value. Never the system.**

The tempting alternative — seeding the golden set from the pipeline's own best
output — produces *more cases* and a *permanently green suite*, while certifying
the system against itself. Any regression then becomes the new gold, silently.
★ It is rejected here in code, not merely in prose, because it is the option that
looks better.

⚠ For `kind == "thesis"` the correct answer is a **judgement**, not ground truth.
The case records **whose judgement it was**; it does not pretend to objectivity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Kind = Literal["extraction", "thesis", "ranking"]

#: `D2` — names that may NOT appear in `established_by`. A golden value traceable
#: to the pipeline is circular no matter how it is worded.
FORBIDDEN_ESTABLISHERS = (
    "pipeline", "system", "model", "llm", "claude", "gpt", "agent",
    "src.", "auto", "generated", "gateway",
)

#: ⚠ `thesis` answers are judgements. Stated so a reader cannot mistake the
#: golden set for ground truth on the most expensive output in the system.
JUDGEMENT_KINDS = ("thesis",)


class CircularGoldenValue(Exception):
    """`D2` — a golden value the system itself produced.

    ⚠ This is the failure mode that produces a green suite forever: the harness
    certifies the system against its own past output, so a regression becomes the
    new expected value and nothing ever reds.
    """


@dataclass(frozen=True, slots=True)
class GoldenCase:
    """`CT-5.2`. ⚠ `source` is required — an unrecorded derivation gets trusted
    for the wrong reason eventually."""

    case_id: str
    kind: Kind
    input_ref: str
    expected: object
    source: str
    established_at: str
    established_by: str

    def __post_init__(self) -> None:
        if not self.case_id or not self.input_ref:
            raise ValueError("case_id and input_ref are required")
        if not self.source.strip():
            raise ValueError(
                f"{self.case_id}: `source` is required (CT-5.2) — a golden value "
                "whose derivation is unrecorded cannot be re-checked, and will "
                "eventually be trusted for the wrong reason"
            )
        if not self.established_by.strip():
            raise ValueError(f"{self.case_id}: established_by is required (D2)")
        if self.expected is None:
            # ⚠⚠ DX-20. An `expected` left empty is a case the fund manager has
            # not finished establishing — the state every case passes through
            # while the filing is still open on the desk. It did not merely
            # load: `run_regression` compares with `==`, so any run producing
            # nothing (extraction NOT_FOUND, a stub, a failed call) matched
            # `None` and the case reported **PASS**.
            # ★ Every other check here guards a value that is WRONG. This one
            #   guards a value that was never established at all — and it is the
            #   only one whose failure mode is GREEN.
            raise ValueError(
                f"{self.case_id}: `expected` is empty (CT-5.2, DX-20) — an "
                "unestablished case must not load: it would PASS whenever the "
                "system produces nothing. ★ If the document genuinely does not "
                "state the figure, say so explicitly (e.g. "
                "`expected: {status: NOT_FOUND}`) — 'the document does not say' "
                "is a finding; 'I have not looked yet' is not."
            )
        low = f"{self.established_by} {self.source}".lower()
        for bad in FORBIDDEN_ESTABLISHERS:
            if bad in low:
                raise CircularGoldenValue(
                    f"{self.case_id}: established_by/source names {bad!r}. ⚠ D2 — the "
                    "fund manager establishes golden values; a value the system "
                    "produced would certify the system against itself, and every "
                    "regression would become the new gold."
                )

    @property
    def is_judgement(self) -> bool:
        """⚠ True for `thesis` — the expected value is an opinion, recorded as one."""
        return self.kind in JUDGEMENT_KINDS
