"""D-05 error family — §13's catalog (L4 §5.3)."""

from __future__ import annotations

from src.shared.errors import PipelineError


class RiskError(PipelineError):
    code = "RSK.UNSPECIFIED"
    retryable = False


class NoBookError(RiskError):
    """RSK.EXPOSURE.NO_BOOK — no reconciled book at `as_of` (RK-0, RK-29).

    ```
    D-05 NEVER COMPUTES ON AN UNRECONCILED BOOK. IT REFUSES, LOUDLY.

    The tempting alternative — compute on the last good book — is worse: it
    produces a correct-looking risk report ABOUT YESTERDAY, and nothing on
    the artifact would say so.
    ```
    """

    code = "RSK.EXPOSURE.NO_BOOK"

    def __init__(self, as_of, why: str) -> None:
        super().__init__(
            f"no reconciled book at {as_of}: {why}. Exposure measured on an "
            f"unreconciled book reports a number about a book that does not exist "
            f"(RK-0, RK-29)"
        )


class BlockAttemptedError(RiskError):
    """RSK.BLOCK.ATTEMPTED — a caller asked D-05 to veto, refuse or downgrade.

    ★ **INV-026.** D-05 holds zero authority: it measures, it flags, it never
    blocks. A caller reaching for a pass/fail here has misread the domain, and
    **RK-34 says the absence of a gate step is deliberate** — stating that it
    does not exist is cheaper than having someone add it.
    """

    code = "RSK.BLOCK.ATTEMPTED"

    def __init__(self, what: str) -> None:
        super().__init__(
            f"{what} asked D-05 to block. D-05 has zero blocking authority — "
            f"concentration IS the bet (M-2), and a risk function that could veto it "
            f"would be overruling the mandate on the strength of a statistic (INV-026)"
        )


class SuppressionAttemptedError(RiskError):
    """RSK.FLAG.SUPPRESSION_ATTEMPTED — INV-021, RK-18.

    ⚠ Including by severity filtering, pagination, or a "show more" that defaults
    to collapsed. **A flag that can be turned off is a flag that will be off when
    it matters.**
    """

    code = "RSK.FLAG.SUPPRESSION_ATTEMPTED"


# --------------------------------------------------------------------------- #
# B5 — the full WF-R1 ladder (§4A.2)
# --------------------------------------------------------------------------- #

class NoTaxonomyError(RiskError):
    """RK-6 / AC-5.6 — a theme threshold evaluated with no declared taxonomy.

    ⚠ **A threshold on an undefined set is unenforceable**, and *the one
    threshold M-2 explicitly calls out is the one with no definition behind it*.
    """

    code = "RSK.THEME.NO_TAXONOMY"

    def __init__(self, detail: str) -> None:
        super().__init__(f"{detail} (RK-6, CT-5.3)")


class FxUnavailableError(RiskError):
    """RK-3 / FX-3 / AC-5.4 — a cross-currency aggregate with no rate.

    ★ **Unavailable, never estimated.** ⚠ A partial sum across currencies is not
    a smaller exposure, it is a wrong one.
    """

    code = "RSK.EXPOSURE.FX_UNAVAILABLE"

    def __init__(self, account_id: str, currency: str) -> None:
        super().__init__(
            f"{account_id}: no FX rate for {currency}, so the base-currency "
            f"aggregate is unavailable rather than estimated (RK-3, FX-3)"
        )


class NotAggregatedError(RiskError):
    """RK-5 / AC-5.3 — a CDR and its underlying counted as two exposures.

    ★ Holding `MU` as a CDR in the RRSP and as the US stock in a TFSA is **one
    position in Micron**, and reporting them separately **understates
    concentration by exactly the amount that matters.**
    """

    code = "RSK.CDR.NOT_AGGREGATED"

    def __init__(self, symbol: str, instruments) -> None:
        super().__init__(
            f"{symbol}: {sorted(instruments)!r} were counted separately. A CDR "
            f"and its underlying are one exposure (RK-5, RC-28)"
        )


class VarMethodUnstatedError(RiskError):
    """RK-9 / AC-5.9 — VaR without method, window, assumption and breadth.

    ⚠ **A VaR without those is a number with borrowed authority** — and on a
    ten-name single-theme book it is *the classic way a concentrated book is
    made to look risk-managed.*
    """

    code = "RSK.VAR.UNSTATED_METHOD"

    def __init__(self, missing) -> None:
        super().__init__(
            f"VaR reported without {sorted(missing)!r}. It states its method, "
            f"window, distributional assumption and effective breadth, or it is "
            f"not reported (RK-9, QA-20, QA-43)"
        )


class VarWithoutConcentrationError(RiskError):
    """RK-10 / AC-5.10 — an artifact reporting VaR and not concentration.

    ★ **VaR is never the headline.** *A book that reports VaR and not theme
    weight is reporting the derived number and hiding the direct one* — and when
    correlation across the book is near 1, the two are the same fact in
    different units.
    """

    code = "RSK.VAR.UNSTATED_METHOD"

    def __init__(self) -> None:
        super().__init__(
            "VaR is present and concentration is not. VaR may appear BESIDE "
            "concentration; it may not stand in for it (RK-10)"
        )
