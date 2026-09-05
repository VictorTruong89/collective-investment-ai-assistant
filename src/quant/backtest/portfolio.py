"""Turn scored predictions into held positions and a return — CT-3.2's missing half.

★ `engine.evaluate()` has always taken `gross_return` and `net_return` as
**arguments**, and nothing produced them. So `cost_survival_gate` reported
`NOT_EVALUATED` on every run, and **no artifact could be promoted by
construction** (MT-17 requires every required gate to PASS).

```text
   scored predictions -> pick top-N per rebalance date
                      -> hold for the horizon
                      -> gross  = mean realised label return
                      -> net    = gross - commission on the turnover
```

⚠⚠ **This measures a PORTFOLIO, not the daily card.** INV-6 permits exactly one
actionable recommendation per day; a backtest of a one-name book measures the
luck of one name. ★ The gate asks *"does this signal survive costs"*, which is a
question about the **signal**, and answering it needs enough positions for the
answer to be about ranking rather than about a single pick. The two live at
different levels and **`TOP_N` is not a position-sizing decision** — D-06 owns
that (PS-43).

⚠ **Commission is charged on the TURNOVER, not on the holdings.** A name held
through a rebalance incurs no fee — which the legacy `_reconcile_bucket`
docstring said and its code did not (QA-50's neighbouring defect).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.quant.backtest.costs import CostModel

#: ★ How many names the simulated book holds. ⚠ **An admitted choice** (CN-10):
#: nothing measured it. It is stated here because §7.1 shows a flat fee's drag
#: depends entirely on the book — *1.20 %/yr at 1m on $100 k, 0.12 % on $1 M* —
#: so N, capital and horizon together decide whether the cost gate can pass at
#: all, and a buried literal would hide that.
TOP_N = 10

#: ⚠ **No default.** QA-48: `settings.yaml` asserts *"$20 round-trip immaterial
#: at realistic capital"* **without stating what realistic capital is** — an
#: undeclared convention doing load-bearing work.
NO_DEFAULT_CAPITAL = None


def simulate(predictions: pd.DataFrame, *, horizon_days: int, capital: float,
             cost_model: CostModel | None = None, top_n: int = TOP_N,
             score_column: str = "score", label_column: str = "value") -> dict:
    """Hold the top `top_n` names each rebalance, and report gross and net.

    `predictions` carries `(date, ticker, score, value)` where `value` is the
    **realised forward return over `horizon_days`** — the label, so the
    simulation never needs a price series of its own and cannot disagree with
    the one the labels were built from.

    ⚠ **Rebalances every `horizon_days`, not every day.** Daily rebalancing on a
    21-day label would charge 21× the commission for a signal that only changes
    monthly, and the cost gate would fail for a reason that is an artefact of the
    simulation rather than a property of the strategy.
    """
    from src.quant.errors import QuantError

    if capital is NO_DEFAULT_CAPITAL or not capital:
        raise QuantError(
            "a simulation needs its capital base. ★ QA-48: a flat per-trade fee's "
            "drag in percentage terms depends entirely on the book — 1.20 %/yr "
            "at 1m on $100k against 0.12 % on $1M, a 10x spread on one strategy. "
            "Two backtests that differ only in an unstated capital base are not "
            "comparable")

    costs = cost_model or CostModel()
    frame = predictions.dropna(subset=[score_column, label_column])
    if frame.empty:
        return _unmeasured("no scored rows carried a realised label")

    dates = sorted(pd.to_datetime(frame["date"]).dt.date.unique())
    rebalances = dates[::horizon_days]          # ⚠ see the docstring
    if not rebalances:
        return _unmeasured("no rebalance dates in the window")

    day = pd.to_datetime(frame["date"]).dt.date
    held: set = set()
    periods, turnovers, benchmark = [], [], []

    for when in rebalances:
        book = frame[day == when]
        if len(book) < top_n:
            continue                            # ⚠ a thin cross-section is skipped, not padded
        picked = book.nlargest(top_n, score_column)
        names = set(picked["ticker"])
        # ★★ **The equal-weight universe on the SAME dates** — without it,
        #   "24.9 % annualised" is a number with nothing to be compared to, and
        #   a survivorship-flattered sample makes any absolute return look good.
        benchmark.append(float(book[label_column].mean()))

        # ★ Equal weight. ⚠ Not a sizing decision — D-06 owns sizing (PS-43);
        #   this is the neutral choice that makes the number about the RANKING.
        periods.append(float(picked[label_column].mean()))
        turnovers.append(len(names - held) + len(held - names))
        held = names

    if not periods:
        return _unmeasured(
            f"no rebalance date carried {top_n} rankable names — the "
            f"cross-section is thinner than the book")

    gross = _compound(periods)
    per_name = capital / top_n
    fees = sum(costs.charge(notional=per_name) for _ in range(sum(turnovers)))
    net = gross - (fees / capital)

    years = max(len(periods) * horizon_days / 252.0, 1e-9)
    bench = _compound(benchmark)
    return {
        "gross_return": gross,
        # ★★ The equal-weight universe over the same dates. ⚠ **Not a market
        #   index** — it is *this* universe, which on today's S&P 500 over ten
        #   years is itself survivorship-flattered (INV-017). It answers the
        #   narrower question the data can answer: *did the RANKING add anything
        #   over holding everything?*
        "benchmark_return": bench,
        "annualised_benchmark": _annualise(bench, years),
        "excess_annualised": (_annualise(gross, years) - _annualise(bench, years)),
        "net_return": net,
        "annualised_gross": _annualise(gross, years),
        "annualised_net": _annualise(net, years),
        "periods": len(periods),
        "rebalances": len(periods),
        "trades": int(sum(turnovers)),
        "fees_paid": round(fees, 2),
        "cost_drag_pct": round(100.0 * fees / capital, 4),
        "capital": capital,
        "top_n": top_n,
        "years": round(years, 2),
        "costs_charged": costs.components,
    }


def _compound(period_returns) -> float:
    """★ Compounded, not summed. ⚠ Adding period returns overstates a series
    that alternates sign and understates one that trends — and over 100 periods
    the difference is not a rounding error."""
    total = 1.0
    for value in period_returns:
        total *= (1.0 + value)
    return total - 1.0


def _annualise(total_return: float, years: float) -> float:
    """⚠ Null rather than a complex number when the book lost more than 100 %."""
    base = 1.0 + total_return
    if base <= 0:
        return float("nan")
    return base ** (1.0 / years) - 1.0


def _unmeasured(why: str) -> dict:
    """QA-17 — ★ *a statistic that cannot be computed is NOT_EVALUATED, never a
    pass.* `None` returns keep `cost_survival_gate` from reading a gap as zero."""
    return {"gross_return": None, "net_return": None, "annualised_gross": None,
            "annualised_net": None, "periods": 0, "rebalances": 0, "trades": 0,
            "fees_paid": 0.0, "cost_drag_pct": None, "why": why}


def turnover_note(result: dict) -> str:
    """★ §5.6a's sign-flip ground, made readable on the artifact.

    ⚠ *Ground (b) flips sign at 3-12 bps of proportional cost*, and
    `proportional_bps` is **0.0 and stated** — so this number is the commission
    drag only, and the true drag is larger by an amount nobody has measured.
    """
    drag = result.get("cost_drag_pct")
    if drag is None:
        return "cost drag not measured"
    return (f"{result['trades']} trades over {result['years']}y cost "
            f"{drag:.4f}% of capital — ⚠ commission only; spread and slippage "
            f"are not modelled (QA-49)")
