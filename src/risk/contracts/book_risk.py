"""D-05 CT-5.1 — `BookRisk`. RK-8…RK-11, RK-30, RK-36.

★★ **RK-10: VaR is never the headline.** *A book that reports VaR and not theme
weight is reporting the derived number and hiding the direct one* — and when
correlation across this book is near 1, **"95% 1-day VaR is $4,100" and "you are
62% in one theme" are the same fact**, except that the second is checkable,
needs no distribution assumption, and cannot be quietly wrong.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.risk.errors import VarMethodUnstatedError, VarWithoutConcentrationError

#: RK-9 — what a VaR must state, or it is not reported (QA-20, QA-43).
VAR_REQUIRED_FIELDS = ("method", "window", "assumption", "effective_breadth")

#: RK-10's default, and the honest one for this book's shape.
VAR_OMITTED_REASON = (
    "effective breadth ~1-2 on a ten-name single-theme book; concentration is "
    "the direct measure and VaR would restate it with borrowed authority (RK-10)"
)


@dataclass(frozen=True, slots=True)
class BookRisk:
    """CT-5.1 — published only from a COMPLETE pass (RK-30, RK-35)."""

    as_of: date
    base_currency: str
    exposure: object
    thresholds_crossed: tuple
    drawdown: object
    factors_for_d06: dict
    var: dict | None = None
    var_omitted_reason: str = VAR_OMITTED_REASON
    correlation: dict | None = None
    flags: tuple = ()
    status: str = "COMPLETE"

    def __post_init__(self) -> None:
        if self.var is not None:
            missing = [f for f in VAR_REQUIRED_FIELDS if not self.var.get(f)]
            if missing:
                raise VarMethodUnstatedError(missing)
            # ★ RK-10 / AC-5.10 — VaR may appear BESIDE concentration; it may
            #   not stand in for it.
            if not getattr(self.exposure, "by_theme", None):
                raise VarWithoutConcentrationError()
        if self.correlation is not None and not self.correlation.get("window"):
            # RK-11 — ⚠ correlations among semiconductor names converge toward 1
            # in a drawdown; a matrix estimated in a calm window understates
            # exactly when it matters, so the window travels with the number.
            raise ValueError(
                "correlation reported without its estimation window (RK-11)")

    def to_json_obj(self) -> dict:
        return {
            "as_of": self.as_of.isoformat(), "base_currency": self.base_currency,
            "exposure": self.exposure.to_json_obj(),
            "thresholds_crossed": [t.to_json_obj() for t in self.thresholds_crossed],
            "drawdown": self.drawdown.to_json_obj(),
            "var": self.var, "var_omitted_reason": self.var_omitted_reason,
            "correlation": self.correlation,
            "factors_for_d06": dict(self.factors_for_d06),
            "flags": [f.to_json_obj() for f in self.flags],
            "status": self.status,
        }
