"""CT-3.1 — HorizonSet v1, as approved 2026-08-16 (§5.6). Not an illustration.

★ **The arbitration block is the part that matters here** (QA-47): `h1m`
nominates, `h1w` may delay or veto and **never** nominates, `h1q` is research
only and **may not appear in a Nomination consumed by D-12 at all** (QA-120).
A HorizonSet without a stated arbitration rule is incomplete, and QA-1 forbids
leaving it implicit.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.quant.errors import HorizonUnpinnedError


@dataclass(frozen=True, slots=True)
class Horizon:
    id: str
    trading_days: int
    role: str            # selection | timing | research


@dataclass(frozen=True, slots=True)
class Arbitration:
    """QA-47 — explicit, and it lives in the HorizonSet rather than in a caller."""

    nominates: str
    may_delay_or_veto: tuple[str, ...]
    research_only: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HorizonSet:
    name: str
    version: int
    horizons: tuple[Horizon, ...]
    arbitration: Arbitration
    purge_days: int
    embargo_days: int
    ranked_quantity: str

    def horizon(self, horizon_id: str) -> Horizon:
        for h in self.horizons:
            if h.id == horizon_id:
                return h
        raise HorizonUnpinnedError(
            f"{horizon_id!r} is not in {self.name}@v{self.version}"
        )

    def __post_init__(self) -> None:
        longest = max(h.trading_days for h in self.horizons)
        if self.purge_days < longest:
            # QA-3 / QA-18 / AC-3.2 — purge is DERIVED from the longest horizon.
            # A shorter purge leaks the label window across the fold boundary.
            raise HorizonUnpinnedError(
                f"purge_days {self.purge_days} < longest horizon {longest}; a purge "
                f"shorter than the label window leaks it across folds (QA-18)"
            )


#: The approved production set. Values transcribed from CT-3.1 — this is the
#: contract, so the numbers are the contract's and not a local choice (CN-1).
PRODUCTION_V1 = HorizonSet(
    name="production",
    version=1,
    horizons=(
        Horizon("h1m", 21, "selection"),    # ★ the ONLY nominating horizon
        Horizon("h1w", 5, "timing"),        # may delay or veto, never nominate
        Horizon("h1q", 63, "research"),     # never reaches a human artifact
    ),
    arbitration=Arbitration(
        nominates="h1m",
        may_delay_or_veto=("h1w",),
        research_only=("h1q",),
    ),
    purge_days=63,
    embargo_days=5,
    ranked_quantity="denormalised_return",  # QA-58 — 'z_hat * sigma_hat * sqrt(h)'
)
