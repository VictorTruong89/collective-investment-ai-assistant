# FMP `/stable/` endpoint catalog — available on Starter

> ⚠ **Measured live 2026-08-15** against the real `FMP_API_KEY` — 156 `/stable/` endpoints, Starter
> tier. Status, row counts and field names come from the responses, **not from FMP's docs, which lag
> the API in both directions**. ★ Re-probe rather than remember.
>
> **Source:** upstream `sdd/design/rel6_design/L1-data-engine.md` §5A.1.
> **Traps and gates:** [`../SKILL.md`](../SKILL.md). **Live gate data:** `src/data_engine/src/fmp/gates.py`.

**PIT class** — **A** natively point-in-time · **B** snapshot with no history (⚠ must be captured into
an observation ledger, or the value is lost) · **C** restated series.
**Consumer** — D-01 fundamental · D-02 features · D-03 quant · D-05/D-06 risk & sizing · D-07 data
engine · D-08 orchestration · D-09 reporting · D-11 recording.

---

## Price & market state

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Daily OHLCV, split+div adjusted | `historical-price-eod/full` | ticker × day | C | D-02, D-03 |
| ★ Daily OHLCV, **unadjusted** | `historical-price-eod/non-split-adjusted` | ticker × day | **A** | D-02 — ⚠ **the only raw feed; fields are named `adj*`** |
| Daily OHLCV, dividend-adjusted only | `historical-price-eod/dividend-adjusted` | ticker × day | C | D-02 |
| Intraday bars (5m/15m/30m/1h/4h) | `historical-chart/{interval}` | ticker × bar | A | *(unused — daily batch)* |
| Live quote + 50/200-day avg + 52 w range | `quote` | ticker, now | **B** | D-09, D-05 |
| Pre/post-market bid-ask | `aftermarket-quote`, `aftermarket-trade` | ticker, now | B | D-09 |
| Trailing returns 1D…10Y, YTD | `stock-price-change` | ticker, now | B | D-02, D-09 |
| Market-cap history | `historical-market-capitalization` | ticker × day | C | D-02 — ⚠ leaks ~28 d per quarter |
| Exchange hours & holidays | `exchange-market-hours`, `holidays-by-exchange` | exchange | — | D-08 |

## Fundamentals & derived financials

⚠ **EDGAR wins wherever both have it** — see the quarter/cumulative trap in `SKILL.md`.

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Income / balance / cash-flow | `income-statement`, `balance-sheet-statement`, `cash-flow-statement` | ticker × period | C | D-02 — **EDGAR first** |
| Growth rates (3 statements + blended) | `*-growth`, `financial-growth` | ticker × period | C | D-02 |
| 60+ ratios | `ratios` | ticker × period | C | D-02 — ⚠ `period=quarter` is 402 |
| 45+ key metrics (ROIC, EV/EBITDA, Graham, cash-conversion) | `key-metrics` | ticker × period | C | D-02 — ⚠ `period=quarter` is 402 |
| TTM ratios / metrics | `ratios-ttm`, `key-metrics-ttm` | ticker, now | **B** | D-02 |
| Altman Z + Piotroski F | `financial-scores` | ticker, now | B | D-02 — *cross-check only; we compute Piotroski* |
| ★ Owner earnings + maintenance capex | `owner-earnings` | ticker × period | C | D-02 |
| ★ Enterprise value **with net-debt bridge** | `enterprise-values` | ticker × period | C | D-02 |
| Revenue by product / geography | `revenue-product-segmentation`, `revenue-geographic-segmentation` | ticker × period × segment | C | D-01, D-02 — ⚠ annual only |
| As-reported statements (raw XBRL shape) | `financial-statement-full-as-reported` | ticker × period | C | *(EDGAR is better)* |
| Report links (10-K/10-Q JSON & XLSX) | `financial-reports-dates` | ticker × period | A | D-01 |
| FMP's own DCF | `discounted-cash-flow`, `levered-discounted-cash-flow`, `custom-discounted-cash-flow` | ticker, now | B | ⚠ **cross-check only — never a published fair value** |

## Analyst consensus, estimates & ratings

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Forward estimates — rev/EBITDA/EBIT/NI/EPS, low·avg·high, analyst counts | `analyst-estimates` | ticker × forecast year | **B** ⚠ | D-01, D-02 — ⚠ `date` is the **target** period, not publication |
| Price-target consensus (high/low/median) | `price-target-consensus` | ticker, now | **B** | D-01, D-05 |
| Price-target counts & averages by window | `price-target-summary` | ticker, now | B | D-02 |
| ★ **Individual price-target changes** — analyst, firm, old→new | `price-target-news` | event | **A** | D-02, D-01 — ⚠ **max 100 rows per call**; `limit=1000` still returns 100 (newest first). Page with `page=0,1,…` to go back (MU: page 1 reached 2022-12-21). Measured 2026-10-01 |
| ★ **Individual rating actions** — firm, previous→new grade | `grades` | event | **A** | D-02, D-01 |
| Rating distribution history | `grades-historical` | ticker × month | A | D-02 |
| Current rating distribution + consensus | `grades-consensus` | ticker, now | B | D-09 |
| FMP quant rating + components | `ratings-snapshot` / `ratings-historical` | ticker, now / × date | B / A | cross-check |
| Rating-change news | `grades-news` | event | A | D-01 |

★ **`grades` and `price-target-news` are the event-stamped originals** behind the aggregated
snapshots — and the only PIT-safe way to build **revision momentum**, a well-known cross-sectional
signal. `grades` ignores date filters and returns its whole history: **MSFT came back with 967 actions
from 2012-03-16 across 82 firms** — fourteen years, at Starter price.

## Corporate events & calendar

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Earnings actual vs estimate (+ revenue) | `earnings` | ticker × report | **A** | D-02 (surprise), D-01 — ⚠ rows carry `lastUpdated` AFTER the report (MU 2025-06-25 row: 2025-09-25), so a past `epsEstimated` may have been revised; and rows dated in the future hold TODAY's forward estimate (look-ahead). Measured 2026-10-01 |
| Upcoming earnings, whole market | `earnings-calendar` | date range | A | D-05 (event risk), D-09 |
| Dividends — declaration/record/payment/ex | `dividends` | event | **A** | D-02, D-11 |
| Dividend calendar | `dividends-calendar` | date range | A | D-09 |
| Splits (+ calendar) | `splits`, `splits-calendar` | event | **A** | D-07 (adjustment), D-02 |
| ★ M&A announcements | `mergers-acquisitions-latest` | event | A | D-01 — thesis-invalidation trigger |
| IPO calendar / disclosures / prospectuses | `ipos-calendar`, `ipos-disclosure`, `ipos-prospectus` | event | A | *(low priority)* |
| ★ Delistings | `delisted-companies` | event | A | **D-07 — survivorship** ⚠ only ~3 weeks deep; page 2+ is 402 |

## SEC filings

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| ★ All SEC filings by symbol / CIK / form type | `sec-filings-search/{symbol,cik,form-type}` | filing | **A** | D-07 cache invalidation, D-01 |
| Filings that carry financials | `sec-filings-financials` | filing | A | D-07 |
| SEC registrant profile (SIC, incorporation, FY end) | `sec-profile` | ticker | B | D-07, D-01 |

## Insider, institutional & political

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| ★ Form 4 insider transactions | `insider-trading/search` | transaction | **A** | D-02, D-01 |
| Insider buy/sell aggregates | `insider-trading/statistics` | ticker × quarter | A | D-02 |
| Market-wide latest Form 4s | `insider-trading/latest` | transaction | A | D-03 screens |
| ★ SC 13D/G — 5 %+ beneficial ownership | `acquisition-of-beneficial-ownership` | filing | **A** | D-01 — activist / stake-building |
| Congressional trading | `senate-trades`, `house-trades`, `*-latest` | disclosure | A | D-01 *(novelty; weak signal)* |

⛔ **13F institutional ownership is 402 — the biggest single gap.**

## Sector, industry & macro

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Sector / industry daily performance | `sector-performance-snapshot`, `industry-performance-snapshot` | date × sector | A | D-02, D-05 |
| Sector / industry performance history | `historical-sector-performance`, `historical-industry-performance` | date × sector | A | D-02 |
| ★ Sector / industry P/E | `sector-pe-snapshot`, `industry-pe-snapshot` | date × sector | A | D-02 — relative-valuation denominator |
| Gainers / losers / most active | `biggest-gainers`, `biggest-losers`, `most-actives` | day | A | D-03 screens |
| ★ **Treasury curve, 1M–30Y** | `treasury-rates` | date | **A** | D-02 — *the risk-free rate the DCF hard-codes* |
| Fed funds, CPI, unemployment, … | `economic-indicators?name=…` | date × series | A | D-02 |
| Economic calendar | `economic-calendar` | event | A | D-05 — ⚠ span ≤ 180 d |
| ★ Equity risk premium by country | `market-risk-premium` | country | B | D-02 — *the other DCF input* |

## Company reference & universe

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Profile — sector, industry, beta, CEO, CIK, ISIN | `profile` | ticker | B | D-07, D-01 |
| ★ Float, free float, shares outstanding | `shares-float` | ticker | B | D-02, D-05 |
| Employee count (+ history) | `employee-count`, `historical-employee-count` | ticker × filing | A | D-02 |
| Executives + compensation | `key-executives`, `governance-executive-compensation` | ticker | B / A | D-01 — ⚠ per-company 402s |
| Company notes / issued debt | `company-notes` | ticker | B | D-01 |
| ★ Universe lists | `stock-list`, `etf-list`, `actively-trading-list`, `financial-statement-symbol-list`, `cik-list` | market | — | **D-07 universe** |
| Sector / industry / exchange vocabularies | `available-sectors`, `available-industries`, `available-exchanges` | market | — | D-07 validation |

## News

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Per-ticker news (title, publisher, full `text`, url) | `news/stock` | article | **A** | D-01 — ⚠ **any `from`/`to` is 402**; page instead. Only ~92 d deep |
| Market-wide latest | `news/stock-latest`, `news/general-latest` | article | A | D-01 |
| FMP editorial with tickers | `fmp-articles` | article | A | *(low value)* |

## FX

| Data | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| ★ USDCAD spot + history | `quote`, `historical-price-eod/full` on `USDCAD` | pair × day | A | **D-00 `FxRate`** |
| Pair list | `forex-list` | — | — | D-07 |

---

## ⛔ Not available — see [`../SKILL.md`](../SKILL.md) for the full list

**Gated (402):** 13F institutional ownership (5 endpoints) · `*-statement-ttm` ·
`latest-financial-statements` · `news/press-releases*` · all ESG · `etf/holdings` ·
`batch-quote-short` · `mergers-acquisitions-search` · `executive-compensation-benchmark` · `*-bulk`.

**Absent (404 — no plan buys these):** earnings-call transcripts ★ · short interest ·
all sentiment products · fail-to-deliver · commitment-of-traders · `all-shares-float`.

**Forbidden by our own rule:** `technical-indicators/*` — ⛔ never ingested at any tier.
