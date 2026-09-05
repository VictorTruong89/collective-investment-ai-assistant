"""CT-1.2 — the AnalysisRun (AP-6, RA-11, RA-64, RA-111, RA-129, RA-130).

> **`AnalysisRun` is not bookkeeping.** It is what makes an output
> reproducible-in-principle and comparable across runs. **Without it the variance
> measurement in §7.1 has nothing to key on.**

★ **RA-129 (amended 2026-08-23): `decoding` is `CT-0.1`'s OBJECT, transported
whole.** This contract used to carry a flat `temperature` — the exact shape
CT-0.1 was reshaped away from, because *a flat `temperature: null` cannot
distinguish "this model has no such parameter" from "nobody set it"* (GW-9). And
it carried no `effort` at all, while **`effort` is the only decoding control D-01
has**: §6 puts both call kinds on the deep tier, and `claude-opus-5` rejects
`temperature` with a 400 (GW-8a).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

#: CT-0.1's outcome enum, mirrored. ★ **There is no `partial`** (GW-22) — both
#: real card incidents came from treating one as a success.
OK = "ok"
FAILING_OUTCOMES = ("transport_failed", "refused", "truncated", "unparseable",
                    "drift_blocked")
OUTCOMES = (OK, *FAILING_OUTCOMES)


@dataclass(frozen=True, slots=True)
class AnalysisRun:
    """One execution of one step. Written **before the next step begins** (RA-111).

    ⚠ *Records written at the end of a run cannot distinguish "did not run" from
    "ran and failed" — and that distinction is the whole of P5.*
    """

    run_id: str
    ticker: str
    as_of: date
    bundle_hash: str
    prompt_name: str
    prompt_version: str
    model_id: str
    #: ★ RA-129 — CT-0.1's object, byte-identical. Never flattened, never reshaped.
    decoding: dict
    #: RA-17 — enumerated options are order-randomised **per call**, and the
    #: permutation is recorded here. ⚠ D-01's own field, not transported: the
    #: gateway composes no prompt (GW-2), so it cannot know the option order.
    option_permutation: tuple[str, ...]
    started_at: datetime
    tokens_in: int
    tokens_out: int
    attempts: int
    outcome: str
    call_id: str | None = None
    step: str | None = None
    detail: str = ""

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(
                f"outcome {self.outcome!r} is not one of {OUTCOMES}. ★ There is "
                f"deliberately no 'partial' — both card incidents came from treating "
                f"one as a success (GW-22, RA-64)"
            )
        if not isinstance(self.decoding, dict) or "control" not in self.decoding:
            raise ValueError(
                "decoding must be CT-0.1's object carrying its `control` key. A flat "
                "temperature cannot say whether null means 'not settable' or "
                "'forgotten', and those are different facts (RA-129, GW-9)"
            )
        if not self.bundle_hash:
            raise ValueError(
                "an AnalysisRun with no bundle_hash records a run nothing can be "
                "compared against (RA-2)"
            )

    @property
    def succeeded(self) -> bool:
        return self.outcome == OK

    @property
    def effort(self) -> str | None:
        """The deep tier's only decoding control (GW-8a, RA-60a).

        ⚠ **RM-5 does not fire on an effort change today** — it re-baselines on an
        INV-8 *tier* change, and `high → xhigh` is not one. Exposing it here is
        what makes RA-60a's hazard diagnosable at all: a run whose effort cannot
        be read is a run whose output distribution cannot be attributed.
        """
        return self.decoding.get("effort")

    def to_json_obj(self) -> dict:
        return {
            "run_id": self.run_id, "ticker": self.ticker,
            "as_of": self.as_of.isoformat(), "bundle_hash": self.bundle_hash,
            "prompt_name": self.prompt_name, "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "decoding": dict(self.decoding),
            "option_permutation": list(self.option_permutation),
            "started_at": self.started_at.isoformat(),
            "tokens_in": self.tokens_in, "tokens_out": self.tokens_out,
            "attempts": self.attempts, "outcome": self.outcome,
            "call_id": self.call_id, "step": self.step, "detail": self.detail,
        }


class AnalysisRunLog:
    """Append-only, in-order. ★ **RA-130's store.**

    ```
    RECORD THAT IT FAILED; NEVER RECORD WHAT IT PRODUCED.
    ```

    ⚠ A reader of AC-1.27 alone (*"a degraded call is never persisted"*) would
    suppress the failure record and destroy exactly what RA-111 exists for. The
    two are different artifacts: D-15 persisted a **Narrative** built from
    dataclass defaults and rendered it; this persists only that a call was made
    and how it ended.
    """

    def __init__(self) -> None:
        self._runs: list[AnalysisRun] = []

    def append(self, run: AnalysisRun) -> AnalysisRun:
        self._runs.append(run)
        return run

    @property
    def runs(self) -> tuple[AnalysisRun, ...]:
        return tuple(self._runs)

    @property
    def failures(self) -> tuple[AnalysisRun, ...]:
        return tuple(r for r in self._runs if not r.succeeded)

    def for_bundle(self, bundle_hash: str) -> tuple[AnalysisRun, ...]:
        """Every run keyed on one bundle — ★ what RM-1's k-run probe compares.

        *Two runs with the same `bundle_hash` are comparable; two with different
        hashes are not* (RA-2), so this is the only legitimate grouping.
        """
        return tuple(r for r in self._runs if r.bundle_hash == bundle_hash)

    def to_json_obj(self) -> list[dict]:
        return [r.to_json_obj() for r in self._runs]
