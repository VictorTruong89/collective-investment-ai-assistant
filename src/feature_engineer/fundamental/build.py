"""§5.3's 45 `f_*` features — computed per filing, joined once, sector-z last.

★★ **The order is the design**, and it was arrived at by measurement:

```text
   1. canonical_frame(rows)     one row per reported period, FULL history
   2. per-filing features       ratios, growth, trend, Piotroski
   3. as_of_join(panel, ...)    backward only — the latest filing knowable
   4. sector_z(...)             needs the cross-section AT A DATE
```

⚠ **Steps 2 and 3 in the other order silently produce nulls.** A 120-day panel
window contains **three** distinct NVDA filings, so a four-filing lag computed
after the join is null on every row — not because the history is missing, but
because the join discarded it first. The failure looks exactly like sparse data.
"""

from __future__ import annotations

import pandas as pd

from src.feature_engineer.fundamental import group_c, growth, items, ratios

#: Pointwise ratios: canonical column → the function that builds it.
POINTWISE = {
    "f_net_margin": ratios.net_margin,
    "f_gross_margin": ratios.gross_margin,
    "f_operating_margin": ratios.operating_margin,
    "f_roa": ratios.roa,
    "f_roe": ratios.roe,
    "f_roic": ratios.roic,
    "f_eps": ratios.eps,
    "f_ocf_to_assets": ratios.ocf_to_assets,
    "f_ocf_to_net_income": ratios.ocf_to_net_income,
    "f_fcf": ratios.fcf,
    "f_fcf_margin": ratios.fcf_margin,
    "f_debt_to_assets": ratios.debt_to_assets,
    "f_debt_to_equity": ratios.debt_to_equity,
    "f_equity_ratio": ratios.equity_ratio,
    "f_interest_coverage": ratios.interest_coverage,
    "f_current_ratio": ratios.current_ratio,
    "f_capex_to_revenue": ratios.capex_to_revenue,
    "f_rd_to_revenue": ratios.rd_to_revenue,
    "f_size_log_assets": ratios.size_log_assets,
    "f_accruals": ratios.accruals,
    "f_accruals_std": ratios.accruals_std,
}

#: `(feature, canonical_item, lag)` — one filing back, or four.
CHANGES = (
    ("f_revenue_chg_1", "revenue", 1),
    ("f_revenue_chg_4", "revenue", 4),
    ("f_net_income_chg_1", "net_income", 1),
    ("f_net_income_chg_4", "net_income", 4),
    ("f_gross_profit_chg_1", "gross_profit", 1),
    ("f_operating_income_chg_1", "operating_income", 1),
    ("f_operating_income_chg_4", "operating_income", 4),
    ("f_operating_cash_flow_chg_1", "operating_cash_flow", 1),
    ("f_stockholders_equity_chg_1", "stockholders_equity", 1),
    ("f_total_assets_chg_1", "total_assets", 1),
)

#: ⚠ The **doubled `f_f_` prefix is inherited and kept** — §5.3 records it as a
#: naming defect *"recorded rather than fixed in the move"*. ★ Renaming it here
#: would silently break every model whose contract names the old column, and
#: FE-6 says a rename is a **tombstone plus a new version**, not an edit.
TRENDS = (
    ("f_f_net_margin_trend_4", "net"),
    ("f_f_gross_margin_trend_4", "gross"),
    ("f_f_operating_margin_trend_4", "operating"),
)

#: ★ §5.3's **Group C** — the two that need a price, plus the valuation multiple
#: they share a hazard with. ⚠⚠ **All three are ANCHORS** (RA-14/RA-151): D-01's
#: blind passes may never see them, which is why §6.2 and §6.3 publish different
#: sets to the two seats.
PRICED = ("f_graham_number_ratio", "f_market_to_book")

#: `(feature, source feature)` — z-scored within `(date, sector)` after the join.
SECTOR_Z = (
    ("f_net_margin_sector_z", "f_net_margin"),
    ("f_roe_sector_z", "f_roe"),
    ("f_debt_to_assets_sector_z", "f_debt_to_assets"),
    ("f_revenue_chg_1_sector_z", "f_revenue_chg_1"),
    ("f_accruals_sector_z", "f_accruals"),
)

FEATURE_NAMES = (
    tuple(POINTWISE) + tuple(n for n, _, _ in CHANGES)
    + ("f_revenue_rolling_chg_4",)
    + ("f_piotroski_f", "f_piotroski_profitability", "f_piotroski_leverage",
       "f_piotroski_efficiency")
    + tuple(n for n, _ in TRENDS)
    + ("f_moat_quant_score", "f_graham_number_ratio", "f_market_to_book")
    + tuple(n for n, _ in SECTOR_Z)
)


def per_filing(rows: pd.DataFrame) -> pd.DataFrame:
    """Everything computable from one filer's history, one row per period."""
    canonical = items.canonical_frame(rows)
    if not len(canonical):
        return canonical

    out = canonical.copy()
    for name, build in POINTWISE.items():
        out[name] = build(canonical).to_numpy()
    for name, item, lag in CHANGES:
        out[name] = growth.change(canonical, item, lag=lag).to_numpy()
    out["f_revenue_rolling_chg_4"] = growth.rolling_change(
        canonical, "revenue", periods=4).to_numpy()
    for name, which in TRENDS:
        out[name] = growth.margin_trend(canonical, which).to_numpy()
    for name, series in growth.piotroski(canonical).items():
        out[name] = series.to_numpy()
    # ★ Per filing, because it rolls over eight of them; the price half is
    #   applied after the join, where the day's own open is available.
    out["f_moat_quant_score"] = group_c.moat_quant_score(canonical).to_numpy()
    return out


def build(panel: pd.DataFrame, *, rows_by_ticker: dict, sectors=None,
          market_caps=None) -> pd.DataFrame:
    """The 45, aligned to `panel`'s `(ticker, date)` rows.

    `rows_by_ticker` is `{TICKER: CT-7.2 frame}` from D-07, already PIT-filtered.
    `sectors` is `{TICKER: sector}` from D-07's Class-B profile; without it the
    five `*_sector_z` columns are null — **which is the honest answer, because a
    z-score against an unknown peer group is not a z-score.**
    """
    pieces = []
    for ticker, sub in panel.groupby("ticker", sort=True):
        enriched = per_filing(rows_by_ticker.get(ticker))
        joined = items.as_of_join(sub, enriched)
        joined.index = sub.index
        pieces.append(joined)
    out = pd.concat(pieces).reindex(panel.index)

    # ★★ The priced features, after the join: `adj_open(t)` is the day's own
    #   open (FE-28) and the shares come from the as-of joined filing.
    caps = _aligned(panel, market_caps) if market_caps \
        else group_c.market_cap(panel, out)
    out["f_market_to_book"] = ratios.market_to_book(
        out, market_cap=caps).to_numpy()
    out["f_graham_number_ratio"] = group_c.graham_number_ratio(
        panel, out).to_numpy()

    sector_series = _aligned(panel, sectors, default=None)
    for name, source in SECTOR_Z:
        out[name] = growth.sector_z(panel, out.get(source), sector_series).to_numpy()

    return out[list(FEATURE_NAMES)]


def _aligned(panel: pd.DataFrame, mapping, default=float("nan")):
    """A per-ticker dict broadcast onto the panel's rows."""
    if not mapping:
        return pd.Series(default, index=panel.index)
    return panel["ticker"].map(mapping)
