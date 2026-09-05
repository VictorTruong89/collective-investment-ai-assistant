"""D-04 error family (L4 §5.3) — §16's catalogue.

★ **Every error here is a refusal to score or a refusal to promote.** D-17 and
D-18 are the two incidents this domain exists to prevent, and both were
*failures indistinguishable from results*.
"""

from __future__ import annotations

from src.shared.errors import PipelineError


class ModelError(PipelineError):
    code = "MDL.UNSPECIFIED"
    retryable = False


class ContractUnresolvableError(ModelError):
    """MT-2 / MT-9 — an artifact that cannot state its contract version.

    ★ **There is no "assume the current contract"**, and no fallback feature
    set. ⚠ *`main_inference.py:595` falls back to `MODEL_FEATURES`, which is an
    alias for `PRICE_FEATURES` — **14 of the 61** — and the fallback is named as
    though it were the model's features.*
    """

    code = "MDL.CONTRACT.UNRESOLVABLE"

    def __init__(self, artifact_id: str, detail: str) -> None:
        super().__init__(
            f"{artifact_id}: {detail}. An artifact whose contract cannot be "
            f"resolved does not score — there is no fallback feature set "
            f"(MT-2, MT-9, P5)")


class ParityError(ModelError):
    """MT-6 / MT-8 / MT-10 — the gate, not a log.

    ```
    A GUARD THAT FILTERS IS NOT A GUARD THAT CHECKS.

    Filtering answers "what can I score with?"
    Checking answers  "am I allowed to score at all?"

    The first always succeeds. That is the entire problem —
    it cannot fail, so it cannot warn.
    ```
    """

    code = "MDL.PARITY.FAILED"

    def __init__(self, artifact_id: str, detail: str) -> None:
        super().__init__(f"{artifact_id}: {detail} (INV-4, MT-6)")


class AnchorMismatchError(ModelError):
    """MT-42 — ★ **a hard gate, not a warning.**

    ⚠ *An anchor mismatch is silent, systematic, and invisible in every metric
    the system computes* — the backtest shares the training anchor, so it cannot
    see the drift it inherits.
    """

    code = "MDL.ANCHOR.MISMATCH"

    def __init__(self, artifact_anchor: str, run_anchor: str) -> None:
        super().__init__(
            f"the model was fitted on the {artifact_anchor!r} anchor and the run "
            f"decides on {run_anchor!r}. A fitted model cannot be relabelled — "
            f"the anchor is baked into its weights, so it must be RETRAINED "
            f"(MT-42, MT-43, D-08 OR-35)")


class DefaultSubstitutedError(ModelError):
    """MT-12 / MT-13 — ★ *a default is never substituted for a fitted value.*

    ⚠ **D-18**: with every candidate failing, `best_sharpe` stayed `-inf`, **the
    untouched defaults were adopted, and `phase3b` reported PASS.** Production
    ran `{rank 0.65, prob 0.35, return 0.0}` while all 8 folds independently
    chose `rank 0.50-0.60, prob 0.10-0.20` — *the classifier got zero weight
    where every fold gave it non-zero.*
    """

    code = "MDL.FIT.DEFAULT_SUBSTITUTED"

    def __init__(self, what: str, detail: str) -> None:
        super().__init__(
            f"{what}: {detail}. If a fit fails, NO ARTIFACT IS PRODUCED — a "
            f"fallback that yields a plausible artifact is the defect, not the "
            f"safety net (MT-12, MT-13)")


class NotEvaluatedError(ModelError):
    """MT-18 — ★ **`NOT_EVALUATED` is not a pass.**"""

    code = "MDL.PROMOTION.NOT_EVALUATED"

    def __init__(self, artifact_id: str, gates) -> None:
        super().__init__(
            f"{artifact_id}: gate(s) {sorted(gates)!r} are not PASS. Promotion "
            f"requires an explicit PASS on every required gate; absence is not "
            f"consent (MT-18, D-03 QA-17)")


class HorizonRoleError(ModelError):
    """MT-31 / MT-32 / MT-33 — the horizon a model may act in.

    ★ *The timing leg may **delay** or **veto** a nomination and may never
    originate or substitute one* — P3's monotonicity and QA-47's arbitration are
    the same rule seen from two domains.
    """

    code = "MDL.HORIZON.ROLE"

    def __init__(self, detail: str) -> None:
        super().__init__(f"{detail} (MT-31, MT-32, MT-33)")
