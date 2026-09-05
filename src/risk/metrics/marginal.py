"""D-05 §8 — the `P` factor. RK-20, RK-22, RK-23, RK-31.

★★ **RK-20: `P` is a MARGINAL, not a standalone, measure.** *A sixth
semiconductor name adds far less diversification and far more concentration than
its own volatility suggests* — ⚠ **standalone vol would size it as though the
book were empty.**

★ **RK-31: WF-R2 uses the SAME code path as WF-R1, on a hypothetical book.** A
candidate evaluated by different code is a different measurement, and the two
would drift exactly where it matters — the comparison between *the book now* and
*the book with this position*. (INV-4's train/inference parity, applied to risk.)
"""

from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass
from datetime import date

from src.risk.metrics.drawdown import UNMEASURED


@dataclass(frozen=True, slots=True)
class MarginalRisk:
    """`P`, with its inputs — RK-22, so D-06 can read rather than trust it."""

    as_of: date
    ticker: str
    book_vol: float
    book_vol_with: float
    marginal_vol: float
    standalone_vol: float
    correlation_window: int
    status: str = "ok"

    @property
    def factor(self) -> float:
        """★ The ratio the marginal measure exists to expose.

        `marginal / standalone` is **near 1 for the sixth semiconductor and far
        below 1 for a genuinely diversifying name** — which is exactly the
        distinction RK-20 says standalone vol destroys. As the `P` in D-06's
        `r_ceiling × E × C × P × D`, a smaller number is a smaller budget.
        """
        if self.standalone_vol <= 0:
            return 1.0
        return min(1.0, self.marginal_vol / self.standalone_vol)

    def to_json_obj(self) -> dict:
        return {"as_of": self.as_of.isoformat(), "ticker": self.ticker,
                "book_vol": round(self.book_vol, 6),
                "book_vol_with": round(self.book_vol_with, 6),
                "marginal_vol": round(self.marginal_vol, 6),
                "standalone_vol": round(self.standalone_vol, 6),
                "correlation_window": self.correlation_window,
                "status": self.status, "factor": round(self.factor, 6)}


@dataclass(frozen=True, slots=True)
class Unmeasured:
    """RK-23 / AC-5.21 — ★ **a value, not a failure** (`RSK.FACTOR.UNMEASURED`)."""

    name: str
    why: str
    status: str = UNMEASURED

    def to_json_obj(self) -> dict:
        return {"name": self.name, "status": self.status, "why": self.why}


def _book_vol(weights, vols, correlations) -> float:
    """`sqrt(w' Σ w)` — the only arithmetic in this module."""
    total = 0.0
    names = list(weights)
    for i in names:
        for j in names:
            rho = 1.0 if i == j else correlations.get(
                (i, j), correlations.get((j, i)))
            if rho is None:
                raise KeyError((i, j))
            total += weights[i] * weights[j] * vols[i] * vols[j] * rho
    return math.sqrt(max(0.0, total))


def marginal_risk(*, ticker: str, weight: float, weights, vols, correlations,
                  as_of: date, window: int):
    """RK-20/RK-31 — the book with the candidate, minus the book without it.

    ⚠ Both sides run through `_book_vol`: **the same code path**, which is what
    makes the difference a measurement rather than two measurements.
    """
    missing = [n for n in list(weights) + [ticker] if n not in vols]
    if missing:
        return Unmeasured("P", f"no volatility for {sorted(missing)!r}")
    try:
        before = _book_vol(weights, vols, correlations)
        after_weights = _rescaled(weights, ticker, weight)
        after = _book_vol(after_weights, vols, correlations)
        contribution = _mctr(ticker, after_weights, vols, correlations, after)
    except KeyError as exc:
        # ⚠ RK-23 — unmeasured, never estimated. A missing correlation is not
        #   an excuse to assume zero, which would make the name look free.
        return Unmeasured("P", f"no correlation for {exc.args[0]!r} "
                               f"(window {window})")
    return MarginalRisk(as_of=as_of, ticker=ticker, book_vol=before,
                        book_vol_with=after, marginal_vol=contribution,
                        standalone_vol=vols[ticker] * after_weights[ticker],
                        correlation_window=window)


def _mctr(ticker, weights, vols, correlations, portfolio_vol: float) -> float:
    """`w_i × (Σw)_i / σ_p` — the marginal contribution to risk.

    ⚠ **The obvious implementation is wrong.** Differencing book volatility
    before and after — *"how much did adding it move σ_p"* — **clamps to zero
    for every name whose own vol is below the book's blend**, which includes
    both the diversifying name and the sixth semiconductor. The two then read
    identically, and RK-20's entire distinction is destroyed by the estimator
    rather than by the input.

    ★ MCTR is the measure that actually decomposes: it sums to `σ_p`, it is
    near `w_i·σ_i` for a name correlated with the book, and far below it for one
    that is not.
    """
    if portfolio_vol <= 0:
        return 0.0
    row = 0.0
    for other, w in weights.items():
        rho = 1.0 if other == ticker else correlations.get(
            (ticker, other), correlations.get((other, ticker)))
        if rho is None:
            raise KeyError((ticker, other))
        row += w * vols[ticker] * vols[other] * rho
    return weights[ticker] * row / portfolio_vol


def _rescaled(weights, ticker: str, weight: float) -> dict:
    """The book with the candidate added, weights renormalised to 1."""
    out = {k: v * (1.0 - weight) for k, v in weights.items()}
    out[ticker] = out.get(ticker, 0.0) + weight
    return out


def hypothetical_book(book, position):
    """RK-31 — ★ the same `BookState` shape, one position longer.

    ⚠ WF-R2 does not get its own book type. A candidate evaluated against a
    different structure is evaluated by different code eventually, however
    careful the first version is.
    """
    return dataclasses.replace(book, positions=book.positions + (position,))
