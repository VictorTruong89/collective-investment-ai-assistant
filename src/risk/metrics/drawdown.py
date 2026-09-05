"""D-05 §8 — the `D` factor. RK-21, RK-23, RK-38.

★★ **RK-21 is the practical recommendation of the whole spec.** *`D` waits on
nothing* — no volatility forecast, no correlation matrix, no D-05 machinery
beyond a peak — and **a risk budget that shrinks in a drawdown is already
meaningfully better than a constant.**

⚠ **RK-38: the peak is DERIVED from the series, never stored.** `CT-11.4` is one
account on one day, and **RK-27 forbids D-05 writing anything except its own
alert and flag records** — so the history is the accumulation of the contract
already declared, read afresh each run.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.risk.exposure.aggregate import UNCHECKED

#: ★ RK-38 — a peak needs something to be a peak *of*. One observation is at its
#: own peak by construction, and reporting that as "no drawdown" would be the
#: most misleading possible reading of a book whose history has just begun.
MIN_SERIES = 2

UNMEASURED = "unmeasured"


@dataclass(frozen=True, slots=True)
class DrawdownState:
    """`CT-5.1.drawdown` — depth and duration against the peak."""

    as_of: date
    peak: float | None
    current: float | None
    depth_pct: float | None
    duration_days: int | None
    status: str = "ok"
    why: str = ""
    peak_on: date | None = None

    @property
    def factor(self) -> float | None:
        """The `D` in D-06's `r_ceiling × E × C × P × D` (§8).

        ★ Deeper drawdown ⇒ smaller budget. `1 - depth` is the simplest form
        that is monotone and bounded in `(0, 1]`, and it is **reported with its
        inputs** (RK-22) so D-06's decomposition can be *read rather than
        trusted*.
        """
        if self.depth_pct is None:
            return None
        return max(0.0, 1.0 - self.depth_pct / 100.0)

    def to_json_obj(self) -> dict:
        return {"as_of": self.as_of.isoformat(), "peak": self.peak,
                "current": self.current, "depth_pct": self.depth_pct,
                "duration_days": self.duration_days, "status": self.status,
                "why": self.why,
                "peak_on": self.peak_on.isoformat() if self.peak_on else None,
                "factor": self.factor}


def drawdown(series, *, as_of: date | None = None) -> DrawdownState:
    """RK-21 / AC-5.19 / AC-5.19a — from D-11's books alone, and nothing else.

    `series` is the reconciled `BookState`s in date order (or any order — they
    are sorted here). ⚠ **An unreconciled state is not a risk input** (RK-0), so
    it is excluded and, if that leaves too little, the result is `unmeasured`
    rather than a flattering zero.
    """
    usable = sorted((b for b in series
                     if b.reconciled == "ok" and b.nav_base is not None),
                    key=lambda b: b.date)
    when = as_of or (usable[-1].date if usable else date.today())

    if len(usable) < MIN_SERIES:
        return DrawdownState(
            as_of=when, peak=None, current=None, depth_pct=None,
            duration_days=None, status=UNMEASURED,
            why=(f"{len(usable)} usable reconciled state(s); a peak needs at "
                 f"least {MIN_SERIES}. ★ A book whose history begins today is "
                 f"at its peak by construction, and reporting that as 'no "
                 f"drawdown' would be the most misleading possible reading "
                 f"(RK-38, RK-36)"))

    peak, peak_on = usable[0].nav_base, usable[0].date
    for state in usable:
        if state.nav_base > peak:
            peak, peak_on = state.nav_base, state.date
    current = usable[-1].nav_base
    depth = 0.0 if peak <= 0 else max(0.0, 100.0 * (peak - current) / peak)
    return DrawdownState(as_of=when, peak=peak, current=current,
                         depth_pct=round(depth, 4),
                         duration_days=(usable[-1].date - peak_on).days,
                         peak_on=peak_on)


def unmeasured_factor(name: str, why: str) -> dict:
    """RK-23 / PS-34 / AC-5.21 — ★ **`unmeasured`, never estimated.**

    ⚠ D-06 sets an unmeasured factor to 1 and reports it as unmeasured, so the
    budget is **visibly incomplete** rather than quietly wrong.
    """
    return {"status": UNMEASURED, "why": why, "name": name,
            "unchecked": UNCHECKED}
