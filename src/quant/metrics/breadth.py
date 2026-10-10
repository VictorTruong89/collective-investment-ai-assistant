"""Effective breadth — QA-43's residual-correlation measure. `breadth.residual_correlation.v1`

★ `breadth_gate` has declared this `formula_id` since B4 and **nothing computed
it**, so the gate reported `NOT_EVALUATED` on every run. With `cost_survival`
now live, this is **the only gate still refusing promotion**.

```text
   returns matrix (ticker x date)
     -> rho_raw       average pairwise correlation of the RETURNS   -> BREADTH
     -> rho_residual  the same after removing market and sector     -> diagnostic
     -> n_eff = n / (1 + (n-1)*rho_raw)
     -> BR    = n_eff * rebalances_per_year
```

⚠⚠ **The gate is fed `rho_raw`, and QA-43's literal words ask for the residual.
That divergence is deliberate, evidenced, and registered as an open question.**
Measured 2026-08-27 on synthetic panels with a *known* common correlation:

```text
   n     rho_true   rho_residual   -1/(n-1)      rho_raw
   12      0.00       -0.09090     -0.09091       0.0060
   12      0.35       -0.09088     -0.09091       0.3384
  500      0.00       -0.00200     -0.00200       0.0001
  500      0.35       -0.00200     -0.00200       0.3463
```

★★ **The residual correlation is identical at `rho_true = 0.00` and `0.35`** — it
returns `-1/(n-1)` and nothing else. Removing a factor built from the same names
removes the very correlation the measure exists to find, so **QA-43's procedure
as written cannot answer the question the gate asks.** The raw measure recovers
the truth to three decimals.

★ Both readings are legitimate and they ask different questions:
**residual** correlation asks *"is there structure left after the known
factors"*; **G&K breadth** asks *"how many independent bets does this book
hold"* — and a book of ten names all with β≈1 holds one bet however independent
their residuals are. The gate wants the second.

⚠⚠ **`n_eff` and `BR` are different quantities and the spec has been burned by
conflating them.** L1-quantitative-analysis v0.4.0 correction (c): *"`BR` was
conflated with `n` — **G&K breadth is bets per year**."* Grinold & Kahn's
`IR = IC·√BR` counts **independent decisions in a year**, so a 500-name universe
rebalanced monthly is not 500 bets and is not 12 either — it is
`n_eff × 12`. Both numbers are returned, named, and never interchanged.

⚠ **QA-43 forbids the shortcuts explicitly**: *"Neither `BR = n` nor the
equally-weighted-mean haircut is admissible as a default."* So an unmeasurable
breadth returns `None`, and the gate reads that as `NOT_EVALUATED` — never as
`n`, which would pass every universe by construction.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FORMULA_ID = "breadth.residual_correlation.v1"

#: ⚠ Below this many names a pairwise-correlation average is dominated by its own
#: sampling error. **An admitted floor** (CN-10) — nothing measured it; it exists
#: so the function declines rather than returning a confident number from four
#: observations.
MIN_NAMES = 10

#: ⚠ And below this many dates a correlation between two series is not a
#: correlation. 60 sessions ≈ one quarter.
MIN_DATES = 60

#: Trading days per year, for the `n_eff → BR` conversion.
TRADING_DAYS_PER_YEAR = 252


def residual_returns(returns: pd.DataFrame, sectors=None) -> pd.DataFrame:
    """Strip the market and sector factors by **regression**. ★ QA-43's *"residual"*.

    `returns` is `(date × ticker)`.

    ```text
    ╔══════════════════════════════════════════════════════════════════╗
    ║  ⚠⚠  NOT cross-sectional demeaning.  Subtracting the per-date     ║
    ║  mean removes exactly one degree of freedom, so the residuals     ║
    ║  are forced to sum to zero every date and their average pairwise  ║
    ║  correlation is MECHANICALLY -1/(n-1) — it measures n, not the    ║
    ║  market.                                                          ║
    ║                                                                  ║
    ║  Measured 2026-08-27 on twelve names: rho = -0.0884 against a     ║
    ║  forced -1/11 = -0.0909.  Clamped at zero that reports            ║
    ║  n_eff = n = 12 — which is the `BR = n` default QA-43 forbids,    ║
    ║  arrived at by a different route and looking like a measurement.  ║
    ╚══════════════════════════════════════════════════════════════════╝
    ```

    ★ Each name is regressed on the equal-weight market return and the residual
    kept — **`r_i − β_i·r_m`**, which leaves each name its own idiosyncratic
    variance and imposes no adding-up constraint across names.

    ⚠ **The sector step is skipped, not faked, when no sectors are supplied.**
    Reporting a market-only residual as sector-neutral would overstate breadth
    exactly where the mandate concentrates — L0 §12's *"370 more semiconductor
    names add little"* is the case that matters (QA-44).
    """
    residual = _regress_out(returns, returns.mean(axis=1))
    if not sectors:
        return residual

    groups: dict = {}
    for ticker in residual.columns:
        groups.setdefault(sectors.get(ticker, "?"), []).append(ticker)
    for _sector, members in groups.items():
        if len(members) < 2:
            continue                       # a one-name sector has no factor
        block = residual[members]
        residual[members] = _regress_out(block, block.mean(axis=1))
    return residual


def _regress_out(returns: pd.DataFrame, factor: pd.Series) -> pd.DataFrame:
    """`r_i − β_i·f` per name, β from the overlapping observations only.

    ⚠ A single β per name over the whole window — a rolling β would make the
    residual depend on a window nobody declared, and INV-2 would go with it.
    """
    out = returns.copy()
    aligned = factor.reindex(returns.index)
    variance = float(aligned.var(ddof=1))
    if not variance or np.isnan(variance):
        return out
    for ticker in returns.columns:
        series = returns[ticker]
        usable = series.notna() & aligned.notna()
        if usable.sum() < MIN_DATES:
            continue                       # ⚠ left raw, not zeroed
        beta = float(series[usable].cov(aligned[usable]) / variance)
        out[ticker] = series - beta * aligned
    return out


def average_pairwise_correlation(residual: pd.DataFrame) -> float | None:
    """Mean of the off-diagonal correlation matrix, or `None`.

    ⚠ **Pairwise-complete, then the off-diagonal mean.** Dropping every row with
    any null would empty a panel where names list and delist; a name-pair with
    too little overlap contributes `NaN` and is skipped rather than imputed.
    """
    if residual.shape[1] < MIN_NAMES or residual.shape[0] < MIN_DATES:
        return None
    matrix = residual.corr(min_periods=MIN_DATES).to_numpy()
    off_diagonal = matrix[~np.eye(matrix.shape[0], dtype=bool)]
    usable = off_diagonal[~np.isnan(off_diagonal)]
    return float(usable.mean()) if usable.size else None


def independent_names(n: int, rho: float) -> float:
    """`n / (1 + (n−1)·ρ)` — the effective number of independent names.

    ★ `ρ = 0` gives `n`; `ρ = 1` gives **1**, which is the honest answer for a
    book of one theme however many tickers it holds.

    ⚠ **A negative average correlation is clamped to zero**, because `n_eff > n`
    is not a meaningful answer — a book cannot hold more independent bets than
    positions. ★ With regression residuals a materially negative `ρ` is a
    finding rather than an artefact, so it is **reported before it is clamped**
    (see `effective_breadth`'s `rho` field).
    """
    if n <= 1:
        return float(n)
    rho = max(rho, 0.0)
    return n / (1.0 + (n - 1) * rho)


def held_book_breadth(rho: float, *, horizon_days: int, top_n: int | None = None) -> dict:
    """F12 `D10` — the held book's breadth, as a DIAGNOSTIC (never gated).

    ⚠ It uses the universe's average correlation for the top-N names — an
    approximation, stated: the names actually held differ by rebalance and their
    own correlation is not measured here.
    """
    if top_n is None:
        from src.quant.backtest.portfolio import TOP_N as top_n
    per_year = TRADING_DAYS_PER_YEAR / max(horizon_days, 1)
    n_eff = independent_names(top_n, rho)
    return {"names": top_n, "independent_names": round(n_eff, 4),
            "breadth": round(n_eff * per_year, 4),
            "note": ("held book: n_eff of the top-N at the UNIVERSE correlation x "
                     "rebalances per year — reported beside the gate, never gated (F12 D10)")}


def effective_breadth(returns: pd.DataFrame, *, horizon_days: int,
                      sectors=None) -> dict:
    """QA-43's measure. Returns `n`, `rho`, `n_eff` and `BR` — ★ **all four**.

    ⚠ **`BR` is bets per YEAR** (G&K), which is why `horizon_days` is required:
    the same universe rebalanced weekly and annually offers very different
    breadth from identical holdings. Reporting `n_eff` as `BR` is the v0.4.0
    correction (c) defect.
    """
    n = int(returns.shape[1])
    # ★★ The gate's input: the correlation of the RETURNS ACTUALLY TAKEN.
    rho = average_pairwise_correlation(returns)
    # ★ QA-43's literal measure, kept as a diagnostic — see the module docstring
    #   for why it is not the gate's input.
    residual = residual_returns(returns, sectors)
    rho_residual = average_pairwise_correlation(residual)
    if rho is None:
        return {
            "formula_id": FORMULA_ID, "names": n, "rho": None,
            "rho_residual": rho_residual,
            "independent_names": None, "breadth": None,
            "sector_neutral": bool(sectors),
            "why": (f"needs at least {MIN_NAMES} names and {MIN_DATES} dates with "
                    f"overlapping history; got {n} names and "
                    f"{residual.shape[0]} dates. ⚠ QA-43 forbids substituting n"),
        }

    n_eff = independent_names(n, rho)
    per_year = TRADING_DAYS_PER_YEAR / max(horizon_days, 1)
    return {
        "formula_id": FORMULA_ID,
        "names": n,
        "rho": round(rho, 6),
        # ⚠ Reported, never fed to the gate: it is `-1/(n-1)` by construction.
        "rho_residual": round(rho_residual, 6) if rho_residual is not None else None,
        "rho_residual_note": (
            f"≈ -1/(n-1) = {-1.0/(n-1):.6f} by construction — removing a factor "
            f"built from these names removes the correlation being measured "
            f"(QA-43 divergence, see the module docstring)") if n > 1 else "",
        "independent_names": round(n_eff, 4),
        # ★★ The gate's input. ⚠ NOT `n_eff` — see the module docstring.
        "breadth": round(n_eff * per_year, 4),
        "rebalances_per_year": round(per_year, 4),
        "sector_neutral": bool(sectors),
        # ★ F12 `D10` — the HELD book, reported beside the gate and never gated: the
        #   top-N names' independent count at the UNIVERSE correlation.
        "held_book": held_book_breadth(rho, horizon_days=horizon_days),
        "why": "",
    }


#: F12 `D12` — the residual correlation against factors priced OUTSIDE the panel.
FORMULA_EXTERNAL = "breadth.residual_correlation.external.v1"


def _ols_residual(y: pd.Series, factors: pd.DataFrame) -> pd.Series:
    """`y − (a + X·b)` on the rows where `y` and every factor exist; NaN elsewhere.

    ⚠ NaN, never the raw value, where the regression cannot run — a raw return left
    in a residual set would carry the market straight back into the average.
    """
    out = pd.Series(np.nan, index=y.index, dtype="float64")
    frame = pd.concat([y.rename("_y"), factors], axis=1).dropna()
    if len(frame) < MIN_DATES:
        return out
    x = np.column_stack([np.ones(len(frame)), frame[factors.columns].to_numpy(dtype="float64")])
    coef, *_ = np.linalg.lstsq(x, frame["_y"].to_numpy(dtype="float64"), rcond=None)
    out.loc[frame.index] = frame["_y"].to_numpy() - x @ coef
    return out


def _within_cross(residual: pd.DataFrame, sectors: dict) -> tuple:
    """Average residual correlation of same-sector pairs, and of cross-sector pairs."""
    if residual.shape[1] < MIN_NAMES or not sectors:
        return None, None
    matrix = residual.corr(min_periods=MIN_DATES).to_numpy()
    label = np.array([sectors.get(t) for t in residual.columns], dtype=object)
    same = (label[:, None] == label[None, :]) & (label[:, None] != None)  # noqa: E711
    off = ~np.eye(len(label), dtype=bool)
    within = matrix[same & off]
    cross = matrix[~same & off]
    within, cross = within[~np.isnan(within)], cross[~np.isnan(cross)]
    return (float(within.mean()) if within.size else None,
            float(cross.mean()) if cross.size else None)


def external_residual_correlation(returns: pd.DataFrame, *, market, sector_returns=None,
                                  sectors=None, horizon_days: int = 21) -> dict:
    """F12 `D12` / AC-F12.34 — residual ρ after EXTERNAL market and sector factors.

    `returns` is `(date × ticker)` on the same basis as the factors (the 21-day
    forward return, sampled daily). `market` is SPY's; `sector_returns` is
    `(date × sector)` from each GICS sector's SPDR; `sectors` maps ticker → sector.

    ★ Unlike `rho_residual` (AC-F12.28) the factors are priced outside the panel,
    so the answer is not forced to `−1/(n−1)`. ⚠ They are cap-weighted and hold
    these names — a mega-cap's own move is partly inside its factor (stated in
    F12 `D12`). **Reported beside the breadth gate, never gated** until ruled.
    """
    n = int(returns.shape[1])
    base = {"formula_id": FORMULA_EXTERNAL, "names": n, "rho_market": None,
            "rho_market_sector": None, "within_sector_market": None,
            "cross_sector_market": None, "within_sector_market_sector": None,
            "cross_sector_market_sector": None, "basis": None,
            "independent_names": None, "breadth": None,
            "note": "external factors (SPY + GICS sector SPDRs) — reported beside the "
                    "breadth gate, never gated (F12 D12)", "why": ""}
    if market is None or not len(market):
        return {**base, "why": "no external market factor supplied — not measured, "
                               "never substituted (QA-43)"}
    market = pd.Series(market).reindex(returns.index).rename("market")

    resid_m = pd.DataFrame({t: _ols_residual(returns[t], market.to_frame())
                            for t in returns.columns}, index=returns.index)
    rho_m = average_pairwise_correlation(resid_m)
    w_m, c_m = _within_cross(resid_m, sectors or {})
    out = {**base, "rho_market": None if rho_m is None else round(rho_m, 6),
           "within_sector_market": None if w_m is None else round(w_m, 6),
           "cross_sector_market": None if c_m is None else round(c_m, 6)}

    rho_used, basis = rho_m, "market"
    if sector_returns is not None and sectors:
        sector_returns = pd.DataFrame(sector_returns).reindex(returns.index)
        cols = {}
        for t in returns.columns:
            sector = sectors.get(t)
            if sector not in sector_returns.columns:
                continue                       # ⚠ no ETF for it: left out, not guessed
            factors = pd.concat([market, sector_returns[sector].rename("sector")], axis=1)
            cols[t] = _ols_residual(returns[t], factors)
        resid_ms = pd.DataFrame(cols, index=returns.index)
        rho_ms = average_pairwise_correlation(resid_ms)
        w_ms, c_ms = _within_cross(resid_ms, sectors)
        out.update(rho_market_sector=None if rho_ms is None else round(rho_ms, 6),
                   within_sector_market_sector=None if w_ms is None else round(w_ms, 6),
                   cross_sector_market_sector=None if c_ms is None else round(c_ms, 6))
        if rho_ms is not None:
            rho_used, basis = rho_ms, "market+sector"

    if rho_used is None:
        return {**out, "why": f"needs at least {MIN_NAMES} names and {MIN_DATES} dates"}
    n_eff = independent_names(n, rho_used)
    per_year = TRADING_DAYS_PER_YEAR / max(horizon_days, 1)
    out = {**out, "basis": basis, "independent_names": round(n_eff, 4),
           "breadth": round(n_eff * per_year, 4)}
    if rho_m is not None:
        # ★ F12 D13 — the GATED figure: market-only (the ranker is not sector-neutral).
        n_eff_m = independent_names(n, rho_m)
        out.update(independent_names_market=round(n_eff_m, 4),
                   breadth_market=round(n_eff_m * per_year, 4))
    return out


#: F12 `D13` — how the gate's basis is named in its `why`.
GATED_BASIS = "external market-only residual ρ (SPY; F12 D13)"


def gated_breadth(external: dict | None) -> tuple:
    """F12 `D13` / AC-F12.35 — `(BR, basis)` the breadth gate reads.

    ★ The market-only external residual: the shared market move is not a bet,
    but a sector tilt is — the ranker is not sector-neutral, so removing the
    sector factor would count five tech names as five independent bets.
    ⚠ Unmeasured ⇒ `None` (the gate is NOT_EVALUATED); never the raw ρ, never `n`.
    """
    br = (external or {}).get("breadth_market")
    return (float(br) if br is not None else None), GATED_BASIS


def from_predictions(predictions: pd.DataFrame, *, horizon_days: int,
                     sectors=None, label_column: str = "value") -> dict:
    """Measure breadth from the same frame the IC and the simulation read.

    ★ One source for all three, so a breadth figure cannot describe a different
    universe from the one that was scored. ⚠ The labels are **forward returns**,
    which is what the correlation should be computed on: the question is whether
    the *bets* are independent, not whether the prices are.
    """
    wide = predictions.pivot_table(index="date", columns="ticker",
                                   values=label_column, aggfunc="last")
    return effective_breadth(wide, horizon_days=horizon_days, sectors=sectors)
