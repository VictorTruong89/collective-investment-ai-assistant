"""D-06 error family (L4 §5.3). §5, §6, §7."""

from __future__ import annotations

from src.shared.errors import PipelineError


class PortfolioError(PipelineError):
    code = "PRT.UNSPECIFIED"
    retryable = False


class NoStopError(PortfolioError):
    """PS-5 / AC-6.4 — a candidate with no stop gets no size.

    ★ **Sizing without a stop is not conservative — it is undefined**, and
    returning a number anyway invents the missing input.
    """

    code = "PRT.SIZING.NO_STOP"

    def __init__(self, ticker: str, detail: str = "no stop supplied") -> None:
        super().__init__(
            f"{ticker}: {detail}. Max-loss-at-stop is the ONE quantity a stop "
            f"makes knowable in advance, and without it there is nothing to "
            f"size against (PS-5, PS-2)"
        )


class TargetAllocationError(PortfolioError):
    """PS-12 / AC-6.11 — a target allocation, recommended book or drift measure.

    ⚠ **The forbidden dependency in L0 §4.3**, restated here because it is *the
    thing this domain would drift into.* ★ Reporting the risk-parity number is a
    disclosure; **optimising toward it is the target allocation PS-12 forbids.**
    """

    code = "PRT.TARGET.REQUESTED"

    def __init__(self, what: str) -> None:
        super().__init__(
            f"{what!r} was requested. D-06 computes CONSEQUENCES, not proposals: "
            f"no target allocation, no recommended book, no drift-from-target "
            f"(PS-12, L0 §4.3)"
        )


class UnavailableInputError(PortfolioError):
    """PS-24 / AC-6.9 — ★ **unavailable, not estimated** (P5, FX-3's shape)."""

    code = "PRT.INPUT.UNAVAILABLE"

    def __init__(self, what: str, why: str) -> None:
        super().__init__(f"{what} is unavailable: {why} (PS-24, FX-3)")


class ReserveUnavailableError(PortfolioError):
    """PS-43 / AC-6.9l — `n_reserve <= 0`, or `target_positions` not supplied.

    ⚠ **A number that DIVIDES the risk budget cannot have an invented default**,
    and PS-27's *"never derived from free cash"* rules out the tempting
    inference — *deriving it from cash is circular*.
    """

    code = "PRT.RESERVE.UNAVAILABLE"

    def __init__(self, account_id: str, detail: str) -> None:
        super().__init__(
            f"{account_id}: {detail}. `target_positions` is a STATED POLICY "
            f"(PS-27, PS-43, QS-7) — supplied per account, never inferred"
        )
