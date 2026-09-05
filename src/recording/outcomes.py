"""Outcome marking — one basis for both arms (DN-20, RC-32, QA-71).

★ THE RULE THIS MODULE EXISTS FOR
---------------------------------
D-12 **DN-20**: vetoed candidates are marked to market on the **same horizon and
the same open-anchored basis** as acted-on ones, "or the two arms are not
comparable and §6.1 is uncomputable".

The gate's whole justification is a comparison between what was acted on and
what was vetoed. ⚠ If the two arms are marked differently, the difference is
mostly *basis* and it looks like skill — so the basis is a value that travels
with both, and mixing them raises rather than producing a number.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.recording.errors import OutcomeBasisMismatch


@dataclass(frozen=True, slots=True)
class Basis:
    """How a return was measured. Carried by BOTH arms or neither is comparable."""

    horizon: str          # "1w" | "1m" | "1q" — D-03's HorizonSet
    anchor: str           # "open" | "close" — QA-71 makes this open

    @staticmethod
    def assert_comparable(a: "Basis", b: "Basis") -> None:
        """Raise unless two measurements may be differenced (DN-20)."""
        if a.horizon != b.horizon:
            raise OutcomeBasisMismatch(
                f"horizon {a.horizon!r} vs {b.horizon!r} — a difference across "
                f"horizons is mostly horizon, and it would read as gate skill (DN-20)"
            )
        if a.anchor != b.anchor:
            raise OutcomeBasisMismatch(
                f"anchor {a.anchor!r} vs {b.anchor!r} — open-anchored and "
                f"close-anchored returns are different quantities (QA-71)"
            )


def mark_to_market(*, entry_px: float, exit_px: float, basis: Basis) -> float:
    """Realised simple return over `basis`.

    `basis` is a required keyword rather than a default, because a default
    horizon is how two arms end up on different ones without anyone choosing.
    """
    if not entry_px:
        raise ValueError(
            "entry price is zero or missing — a return that cannot be computed is "
            "a failure, never an infinity or a zero (P5)"
        )
    return (exit_px - entry_px) / entry_px
