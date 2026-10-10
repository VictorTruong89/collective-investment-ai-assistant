"""D-12 error family — §10's catalog (L4 §5.3)."""

from __future__ import annotations

from src.shared.errors import PipelineError


class DecisionError(PipelineError):
    code = "DEC.UNSPECIFIED"
    retryable = False


class GateMissingError(DecisionError):
    """DEC.GATE.MISSING — a declared gate did not report (DN-11)."""

    code = "DEC.GATE.MISSING"

    def __init__(self, missing, declared) -> None:
        super().__init__(
            f"declared gate(s) {sorted(missing)} did not report; roster was "
            f"{sorted(declared)}. The roster is declared BEFORE the run — inferring "
            f"it from what answered makes a silently-absent gate structurally "
            f"undetectable (DN-11)"
        )


class AbsentTreatedAsPassError(DecisionError):
    """DEC.GATE.ABSENT_TREATED_AS_PASS — ★ the identity reached by omission.

    ```
    THE IDENTITY ELEMENT MUST NOT BE REACHABLE BY OMISSION.

    If a missing gate input is treated as PASS, the meet is unchanged and the
    recommendation goes out ungated — looking exactly like one that passed.

    Both real incidents in this repo are this bug: a discipline card built
    from a FAILED and from an ABSENT LLM narrative, emailed as genuine
    recommendations with no stop and no targets.
    ```
    """

    code = "DEC.GATE.ABSENT_TREATED_AS_PASS"

    def __init__(self, gate_id: str) -> None:
        super().__init__(
            f"gate {gate_id!r} supplied no status and would have composed as the "
            f"identity (BUY), leaving the recommendation ungated and indistinguishable "
            f"from one that passed (DN-10, §5.5)"
        )


class GateUnavailableError(DecisionError):
    """DEC.GATE.UNAVAILABLE — a gate errored; no actionable recommendation (DN-12)."""

    code = "DEC.GATE.UNAVAILABLE"


class VerdictOriginatedError(DecisionError):
    """DEC.VERDICT.ORIGINATED — a verdict traceable to no input (DN-1).

    ★ D-12's only freedom is to make a verdict *more conservative*. A composed
    verdict that appears in no input means the composition was bypassed.
    """

    code = "DEC.VERDICT.ORIGINATED"

    def __init__(self, final: str, inputs) -> None:
        super().__init__(
            f"composed verdict {final!r} appears in no input {sorted(set(inputs))}. "
            f"D-12 originates nothing — every verdict it emits was emitted by someone "
            f"else first (DN-1)"
        )


class VerdictUpgradeError(DecisionError):
    """DEC.VERDICT.UPGRADE — ★ algebraically impossible; firing means the meet was bypassed."""

    code = "DEC.VERDICT.UPGRADE"


class AttributionIncompleteError(DecisionError):
    """DEC.ATTRIBUTION.INCOMPLETE — binding gates omitted (DN-13).

    ⚠ Reporting one of three binding gates makes the other two invisible, and
    the reader fixes a third of the problem believing they fixed it.
    """

    code = "DEC.ATTRIBUTION.INCOMPLETE"


class AnchorMismatchError(DecisionError):
    """DEC.ANCHOR.MISMATCH — anchor disagrees with the RunManifest (DN-23, OR-35)."""

    code = "DEC.ANCHOR.MISMATCH"

    def __init__(self, recommendation: str, manifest: str) -> None:
        super().__init__(
            f"decision_anchor {recommendation!r} disagrees with the RunManifest's "
            f"{manifest!r}. A model trained on one anchor and deployed on another is "
            f"a full session of drift on every prediction, invisible in backtest "
            f"(OR-35, INV-4)"
        )


class MultipleActionableError(DecisionError):
    """DEC.INV6.MULTIPLE_ACTIONABLE — more than one actionable recommendation (DN-22)."""

    code = "DEC.INV6.MULTIPLE_ACTIONABLE"


class RefusedRankerActionableError(DecisionError):
    """DN-41 / AC-12.31 — a ranking from a REFUSED model may not be actionable."""

    code = "DEC.ACTIONABLE.REFUSED_RANKER"

    def __init__(self, refused_gates) -> None:
        super().__init__(
            f"the nomination was ranked by a refused model "
            f"({', '.join(refused_gates)} failed) — it may be shown as informational, "
            f"never actionable (DN-41, PG-10)")


class SellNotHeldError(DecisionError):
    """DEC.SELL.NOT_HELD — ★ outside the chain's precondition (DN-24).

    `c(BUY) < c(HOLD) < c(SELL)` is an ordering **only for a name currently
    held**. On an unheld name a SELL is a *short* — more aggressive than HOLD —
    and §5's ordering inverts. Here the precondition is guaranteed rather than
    assumed: all four accounts are registered, and CRA rules prohibit short
    selling in a registered account.
    """

    code = "DEC.SELL.NOT_HELD"

    def __init__(self, ticker: str) -> None:
        super().__init__(
            f"SELL emitted for {ticker!r}, which is not held. The conservatism chain "
            f"presumes a long-only book: on an unheld name SELL is a short, which is "
            f"an ESCALATION and not a downgrade (DN-24)"
        )
