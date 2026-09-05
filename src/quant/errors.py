"""D-03 error family — §13's catalog (L4 §5.3, EH-13)."""

from __future__ import annotations

from src.shared.errors import PipelineError


class QuantError(PipelineError):
    code = "QNT.UNSPECIFIED"
    retryable = False


class HorizonUnpinnedError(QuantError):
    """QA-1 / AC-3.1 — a model or backtest without a declared HorizonSet version."""

    code = "QNT.HORIZON.UNPINNED"


class MethodMissingError(QuantError):
    """QA-20 / AC-3.14 — a `formula_id` with no MethodEntry.

    ★ **This fails the BUILD, not the run.** §8's argument is that a quant method
    without stated provenance is a number with borrowed authority: the reader
    cannot tell a standard estimator from a house variant, and `rsi_14` is the
    live example — ours is a rolling mean where every charting package uses
    Wilder smoothing, and *nothing recorded the choice*.
    """

    code = "QNT.METHOD.MISSING"

    def __init__(self, formula_id: str, searched) -> None:
        super().__init__(
            f"formula_id {formula_id!r} has no MethodEntry under {searched}. A method "
            f"with no provenance is a number with borrowed authority (QA-20, CT-3.3)"
        )


class AdjustedLevelError(QuantError):
    """QA-10 / AC-3.22 — a price-LEVEL comparison computed on the adjusted panel.

    ⚠ Mandate-compliance, not merely modelling: on an adjusted history a reverse
    split makes a stock that traded at $0.50 look like $10 retroactively, so the
    **M-1 penny-stock screen silently admits names that were penny stocks at the
    time** (D-07 DE-29).
    """

    code = "QNT.SIGNAL.ADJUSTED_LEVEL"

    def __init__(self, screen: str) -> None:
        super().__init__(
            f"screen {screen!r} compares a price LEVEL and was handed the adjusted "
            f"panel. Levels read the RAW series (QA-10, DE-29)"
        )


class NominationContractError(QuantError):
    """CT-3.4 — the nomination D-12 consumes is malformed."""

    code = "QNT.NOMINATION.INVALID"
