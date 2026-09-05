<!-- ARCHIVED — DO NOT CODE FROM THIS FILE -->

> **⚠️ ARCHIVED / HISTORICAL — NOT AUTHORITATIVE.** Frozen on 2026-08-08. This is a pre-SDD
> Release 1–5 document, kept as an immutable record of what was decided at the time. It does **not**
> describe the code today and it is **not** a set of instructions to execute. Paths inside predate the
> `notebooks/` → `sdd/` rename and are deliberately left unrewritten.
>
> **Authoritative sources:** `sdd/specs/vision.md` (what this project is) ·
> `sdd/specs/constitution.md` (the rules) · `sdd/specs/F<n>_<slug>/spec.md` (what a feature must do) ·
> `sdd/specs/F0_code_map/spec.md` (what the code currently looks like). See `sdd/archive/README.md`.

---

# Release 4 — Final Summary

> **Last updated:** 2026-06-01
>
> **Status**: Closing document for Release-4.
>
> **Audience**: a developer joining the project after release-4 ships. Assumes
> the rel1 / rel2 / rel3 documents have been read for ML-paradigm background.

---

## 1. Release-4 Introduction

Release-4 ships **two targets** on top of the existing ML paradigm without
touching it:

1. **`main_buffett` — a Warren-Buffett-style fundamental pipeline** that
   re-paradigms the project away from short-horizon ML return prediction
   (whose walk-forward Sharpe came in at −0.46 in rel-3) and toward
   quality + moat + DCF + safety-margin investing on a curated 30-ticker
   universe. Outputs are deterministic markdown reports plus a single
   composite ranking score per ticker.
2. **`buffett-api` — a FastAPI server served over Tailscale** that lets a
   Samsung phone trigger the pipeline's on-demand modes (`infer`,
   `synthesis-report`, `scorecard/full`, `backtest`) and read back mobile-
   optimised HTML cards or markdown reports. Single user, single worker, HTTP
   Basic auth behind the VPN.

Both targets share the same package (`pipeline/buffett/…`) and live alongside
the ML paradigm (`pipeline/ohlcv/`, `pipeline/training/`,
`pipeline/fundamental_analysis/`, `main_pipeline.py`) with a strict
no-back-import boundary.

### 1.1 What triggered the paradigm shift

The rel-3 ML/OHLCV paradigm was evaluated via walk-forward backtest (2018–
2026, 8 folds). Results:

| Metric | Value |
|---|---|
| WF Sharpe | −0.46 |
| Max Drawdown | −89.3% |
| Hit Rate | 47.6% |
| Feature Spearman ρ (1-week label) | ≈ 0.000 across all features |

Root cause: predicting 1-week returns for 30 stocks is near-pure noise. No
feature carries predictive signal at that horizon. The ML paradigm cannot
be fixed by tuning — the target variable is the problem.

The Buffett-paradigm solution treats fundamentals as the **primary**
investment signal (not a noisy ML input). A company with durable
competitive advantage, strong ROIC, and a clean balance sheet is worth
owning at the right price. OHLCV is used only to determine *when* to enter,
not *what* to own. The two paradigms **co-exist** in the codebase; neither
depends on the other.

Key principle the codebase enforces: **never buy a great company at a
terrible price, and never buy a mediocre company at any price.**

---

## 2. Target 1 — `main_buffett` fundamental pipeline

### 2.1 Investment framework (encoded in code)

```
Step 1: Quality Screen     — does this business deserve capital?
Step 2: Moat Analysis      — how durable is the competitive advantage?
Step 3: Management Signal  — is capital allocated honestly?
Step 4: Valuation          — what is fair intrinsic value?
Step 5: Safety Margin      — is price ≥ 25% below intrinsic value?
Step 6: Entry Timing       — is the technical setup favourable?
Step 7: Monitoring         — has the thesis changed? Time to sell?
```

Operating cadence: quarterly `analyze`+`screen` after 10-K/10-Q filings;
weekly `report`+`scorecard` for market context; daily `signals` on the
watchlist; on-demand `infer` and `synthesis-report` for single tickers.

### 2.2 CLI surface

`python -m pipeline.main_buffett --mode <MODE>` with:

| Mode | Steps | Typical use |
|---|---|---|
| `analyze` | filing fetch (EDGAR) → LLM extraction → `CompanyProfile` JSON | Quarterly |
| `screen` | quality gates + moat + DCF + safety → watchlist | After analyze |
| `signals` | entry timing (watchlist) + sell monitor (portfolio) | Daily |
| `report` | per-ticker enriched 12-section markdown | Weekly |
| `scorecard` | ranked universe markdown + data-quality report | Weekly |
| `infer` | cached fundamentals + fresh price + news + LLM materiality | On-demand |
| `synthesis-report` | archetype + cycle + supply-side + reconciled FV + ETF tripwires (Sonnet 4.6) | On-demand |
| `backtest` | historical IV validation (Methods 1+5 default, +2 optional) | Quarterly review |
| `full` | analyze → screen → signals → report → scorecard | End-to-end refresh |

Flags worth remembering: `--tickers` (override universe), `--year`
(target filing year for `analyze`), `--force-refresh` (bypass all per-step
caches), `--methods 1,5,2` and `--backtest-start YYYY-MM-DD` for the backtest
mode, `--output-json PATH` to dump the full result dict.

### 2.3 Composite ranking score

Every ticker in the universe is ranked by a single number in `[0, 100]`,
computed in `pipeline/buffett/report/universe_scorecard.py`:

```
composite = 0.40 × zone_pts        (Safety Margin)
          + 0.30 × moat_pts        (Moat)
          + 0.20 × quality_pts     (Quality Gates)
          + 0.10 × entry_pts       (Entry Signal)
```

The weighting encodes Buffett's *priority order* (see §6 for the academic
lineage); it is not a statistical optimisation. Component scoring:

- `zone_pts` = `{BUY: 100, HOLD: 67, REVIEW: 33, UNKNOWN: 0}` driven by the
  DCF margin-of-safety zone (`safety_margin.py`).
- `moat_pts = clamp(0, 10, 0.6×quant_score + 0.4×llm_score) × 10`
  (`moat_scorer.py`). `quant_score` = mean of gross-margin stability,
  ROIC vs WACC, revenue-growth consistency. `llm_score` = moat-type base
  − threat penalties − poor-management penalties.
- `quality_pts = (gates_passed / 4) × 100`. The four hard gates
  (`quality_checker.py`): ROIC > 10% in ≥3/5y, D/E < 1.5, FCF > 0 in ≥3/5y,
  current ratio > 1.5.
- `entry_pts` = `{BUY: 100, WATCH: 67, WAIT: 33}` from `entry_timer.py`.

Component formulas with code anchors:

- **Safety margin → zone → `zone_pts`**
  - `margin = (intrinsic_value − current_price) / intrinsic_value`
    (`safety_margin.py:64`).
  - `zone = "BUY" if margin ≥ 25% else "HOLD" if margin ≥ 10% else "REVIEW"`
    (`safety_margin.py:66-71`).
  - `intrinsic_value` is the weight-averaged 3-scenario DCF
    (`dcf_calculator.py:120-143`). When TTM revenue is available it
    replaces the most-recent annual EDGAR row as the projection base
    (`dcf_calculator.py:106-110`). The reverse-DCF helper
    `implied_growth_rate()` (lines 204-249) binary-searches the CAGR that
    equates DCF value with current price.

- **Moat → `moat_pts`**
  - `moat_score = 0.6 × quant_score + 0.4 × llm_score` (`moat_scorer.py:98`).
  - `quant_score = (gm_score + roic_score + rev_score) / 3`
    (`moat_scorer.py:176`):
    - `gm_score = max(0, 10 − stdev(gross_margins) × 200)` (`:141`)
    - `roic_score = clamp(0, 10, 5 + (avg_ROIC − WACC) × 50)` (`:163`)
    - `rev_score = (years_revenue_grew / total_years) × 10` (`:174`)
  - `llm_score = moat_type_base − threat_penalty − poor_mgmt_penalty`
    (`moat_scorer.py:180-191`). `moat_type_base`: network_effect=9.5,
    brand=9.0, switching_cost=8.5, cost_advantage=6.5, efficient_scale=6.0,
    none=2.0 (`:31-38`). Penalties capped at 0.5 per threat / poor-mgmt
    keyword.
  - `moat_pts = clamp(0, 10, moat_score) × 10` (`universe_scorecard.py:166`).

- **Quality gates → `quality_pts`** (`quality_checker.py:71-120`)
  - Gate 1: ROIC > 10% in ≥3 of last 5 years; `ROIC = Net_Income / (Equity + Debt − Cash)`.
  - Gate 2: D/E < 1.5 most recent year.
  - Gate 3: FCF > 0 in ≥3 of last 5 years.
  - Gate 4: Current Ratio > 1.5 most recent year.
  - `quality_pts = (gates_passed / 4) × 100` (`universe_scorecard.py:156-167`).

- **Entry signal → `entry_pts`** (`entry_timer.py:63-118`) — see §2.4 for
  the five filters. `entry_pts = {"BUY": 100, "WATCH": 67, "WAIT": 33}`
  (`universe_scorecard.py:49`).

#### 2.3.1 Worked example — MSFT on 2026-05-01

From `data/buffett/universe_scorecard_2026-05-01.md`:

| Field | Value |
|---|---|
| Price | $407.78 |
| IV/share | $432.08 |
| Margin | +5.6% |
| Zone | 🔴 REVIEW |
| Moat | 8.2 |
| Quality | ❌ (3/4) |
| Entry | WAIT |
| **Score** | **56.1** |

Calculation:

```
margin     = (432.08 − 407.78) / 432.08 = 5.6%   →  REVIEW
zone_pts   = 33        ⇒ 0.40 × 33 = 13.2
moat_pts   = 8.2 × 10 = 82    ⇒ 0.30 × 82 = 24.6
quality_pts = (3/4) × 100 = 75 ⇒ 0.20 × 75 = 15.0
entry_pts  = 33        ⇒ 0.10 × 33 = 3.3
                                       ─────
                                         56.1 ✓
```

How to read this: MSFT has the highest moat in the universe (8.2/10), but
the price already discounts that excellence — the DCF says you're paying
~$24 above fair value with no cushion for error. The signal is "monitor,
don't buy." For MSFT to enter HOLD zone (10% margin) price must drop to
~$389; for BUY zone (25% margin) ~$324. Alternatively, IV growth from
continued revenue + margin recovery can close the gap.

### 2.4 Five-filter entry gate (`entry_timer.py`)

ALL five must pass for `BUY`. Failing filter #1 → `WAIT`; passing #1 but
failing any technical → `WATCH`.

1. `safety_margin ≥ 25%`
2. `price > 50-day SMA` (medium-term trend confirmation)
3. `RSI-14 < 65` (not overbought; tighter than Wilder's classic 70)
4. `volume z-score (5d) < 2.0` (no news-driven blow-off day)
5. `not within ±5 calendar days of an earnings announcement`

The signal `WATCH` is the most actionable state — fundamentals say own, you're
waiting for a better entry.

### 2.5 Three-scenario DCF (`dcf_calculator.py`)

```
Entity = Σ_{t=1..10}  base_revenue × (1+CAGR)^t × FCF_margin_t / (1+WACC)^t
       + terminal_FCF × (1+TGR) / (WACC − TGR) / (1+WACC)^10
IV/share = Σ_i (weight_i × Entity_i / shares)   for i ∈ {bull, base, bear}
```

When TTM revenue is available it replaces the most-recent annual EDGAR row
as the projection base. A reverse-DCF helper binary-searches the CAGR that
equates DCF value to current price — surfaced in the per-ticker report as
"market-implied growth."

All DCF inputs are read from `config/dcf_assumptions.yaml`. Resolution order:
`ticker_overrides → sector_overrides → defaults`. Per-sector overrides exist
for Technology, Energy, Consumer Staples, Healthcare, and Financials.

### 2.6 Cross-source data validation (TO-DO 1)

Before any DCF math runs, `pipeline/buffett/etl/data_validator.py` cross-
checks every yfinance-sourced input (price, shares, sector, four TTM line
items) against an independent free source (Stooq EOD for price, EDGAR XBRL
for everything else). Tolerance bands live in
`config/dcf_assumptions.yaml: data_validation:` and produce three severities:

- `OK` — proceed silently.
- `WARN` — proceed with DCF; log warning; surface in report.
- `BLOCKED` — skip DCF (IV = `None`); scorecard row keeps moat/quality but
  shows `—` for IV-derived columns.

Side-by-side comparisons for every ticker land in
`data/buffett/data_quality_report_<YYYY-MM-DD>.md`, written at the end of
every `scorecard`/`full` run. Secondary-source unreachability degrades to
`UNAVAILABLE` and never blocks the pipeline. 12-unit-test suite in
`tests/test_data_validator.py`.

### 2.7 Backtest validation (TO-DO 2)

`pipeline/buffett/backtest/` validates the Intrinsic Value signal — *not* a trading
strategy. Three methods, two phases:

| Method | Question | Pass criterion |
|---|---|---|
| 1 — Forward returns by quintile | Do cheap stocks beat expensive ones over 1/3/5y? | Q1−Q5 3y spread ≥ 5%/yr, t ≥ 2.0 |
| 5 — Mean-reversion half-life | Does the IV-price gap actually close? | Median half-life ≤ 1500 trading days, uncensored ≥ 50% |
| 2 — Long-short Q1/Q5 portfolio | Could a tradable strategy earn a real Sharpe? | Sharpe ≥ 0.5 |

Invariants enforced everywhere: point-in-time financials (filing date, never
period-end), originally-filed precedence (no restatement leakage), TTM and
data-validator paths disabled (neither is PIT), and the production
`DCFCalculator._dcf_value()` is *reused* (not re-derived) so backtest math
stays lockstep with production. `BacktestMetrics.compute()` from
`pipeline.ohlcv.backtest.metrics` is the single concrete cross-paradigm
import — used unchanged for Method 2's Sharpe / Sortino / MaxDD.

Output: `reports/backtest_reports/<run-timestamp>/buffett_iv_backtest/iv_backtest_<date>.md`
— the same root that `main_pipeline` writes to, so timestamped fundamental
and ohlcv backtests interleave naturally. CLI:

```bash
python -m pipeline.main_buffett --mode backtest                  # default 1,5
python -m pipeline.main_buffett --mode backtest --methods 1,5,2  # add long-short
python -m pipeline.main_buffett --mode backtest --backtest-force-recompute
```

Cold run ~60min (EDGAR throttling); cached re-runs under 5min via
`data/buffett/backtest/observations.parquet`. The 2026-05-26 run reported
Method 1 PASS (+31.6%/yr Q1−Q5 spread, t=5.38), Method 5 FAIL (cheap-side
gaps largely don't close inside the 8-year window).

### 2.8 Synthesis layer — `--mode synthesis-report`

Layered on top of the deterministic pipeline, the synthesis layer adds
cycle-aware analytical sections the deterministic pipeline can't infer from
filings alone. Built in three phases — phases 1 and 2 are wired through the
CLI; phase 3 surfaces them on the phone.

Phase 1 (pure Python, no LLM cost): `ValuationReconciler` combines five
valuation methods (mid-cycle, reverse DCF, peer multiples, standard DCF,
Graham) with per-archetype weights into a single weighted FV + verdict
(`BUY/HOLD/SELL`). `SensitivityAnalyzer` produces a 5-row delta table on the
per-archetype master driver (e.g. "Industry pricing / contract ASPs" for
cyclicals). Both write straight into the existing `--mode report` markdown
as Section 0 (Decision Box), 5b (Reconciliation), 5c (Sensitivity).

Phase 2 (LLM + Claude native web search):
`pipeline/buffett/synthesis/` modules use Claude's `web_search_20250305`
tool through a thin wrapper (`etl/web_search_provider.py`, 24h disk cache).
Components:

- `archetype_classifier.py` — one cheap call, 90-day cache, sector-string
  fallback if the LLM is unreachable.
- `cycle_position.py` — web-search-augmented; returns cycle phase, evidence,
  mid-cycle EPS estimate, recommended normal multiple. Cyclicals only.
- `supply_side.py` — web-search-augmented competitor-capacity table with
  one-line interpretations. Cyclicals only.
- `etf_tripwire.py` — web-search-augmented; 1–2 proxy ETFs with observable
  trigger conditions phrased as `"If [ETF] [condition] → [action]"`.
- `report_writer.py` — orchestrator. Runs all data + synthesis steps, then
  makes ONE Sonnet 4.6 narrative call via structured tool-use to produce
  verdict + conviction + top-3 pros/cons + differential view + thesis
  tripwires + entry zone + stop-loss + 3 targets + position size.
- `prompt_alignment.py` — single-source-of-truth enforcer. Every infer and
  synthesis-report call validates the master spec at
  `AI_stock_analysis/prompt_stock_analysis.md` against the component prompts
  before any LLM work happens, raising `PromptAlignmentError` with a diff if
  they have drifted. mtime-cached so post-first-call cost is sub-millisecond.

Outputs land at `reports/llm_reports/<TICKER>_report.md` (markdown) +
`<TICKER>_synthesis.json` (structured) + `<TICKER>_archetype.json` (90-day
cache). Cost ≈ $0.25/report cold, $0.04 with cache; latency 60–120s cold,
<500ms cached.

### 2.9 Infer mode — `--mode infer`

The fastest path to a single-ticker call: it trusts the cached `screen`
result (moat, quality gates, IV) and only refreshes the two things that
change daily: **price/technicals** and **news**.

```
infer = cached screen result
      + fresh price & technicals       (yfinance, ~15min delay)
      + fresh multi-source news        (4 news APIs, 2–3h freshness)
      + LLM materiality judgment       (claude-sonnet-4-6, ~$0.013/call)
      → concise signal card (JSON + HTML)
```

News aggregation (`etl/news_aggregator.py`) hits Finnhub + Yahoo RSS +
Marketaux + NewsData.io concurrently (`ThreadPoolExecutor(max_workers=5)`,
<5s budget), plus Alpha Vantage as a bonus for pre-computed sentiment
(saves 30–50% LLM input tokens when AV's 25/day quota is available). Each
source is wrapped in try/except — failures degrade gracefully (Yahoo RSS is
key-less and rate-limit-free so a result is always returned).

The LLM analyst (`analysis/news_analyst.py`) can never produce `BUY` if
the quantitative signal is `WAIT`; the only escalation allowed is
`WAIT → WATCH/AVOID`. Both `quantitative_signal` and `modified_signal`
are shown side by side — the pipeline never silently overrides the
deterministic algorithm.

Cache strategy is **filing-aware** (rel-4 evolution beyond the original
30-min TTL design): the cache stays valid until `FilingMonitor` reports a
new periodic filing date on EDGAR (10-K/10-Q/20-F). A 7-day TTL is the
safety net. `force_refresh=True` bypasses both gates.

### 2.10 Data flow (four stages)

The pipeline executes in four logical stages. The CLI modes from §2.2
(`analyze`, `screen`, `report`, `scorecard`, `signals`, `full`) are
sub-selections over these stages, not a parallel hierarchy.

```
┌─────────────────────────────────────────────────────────────────┐
│                  STAGE 1 — Data Ingestion (analyze)             │
└─────────────────────────────────────────────────────────────────┘
  EDGAR (10-K full-text)               Anthropic API
         │                              (claude-sonnet-4-6)
         ▼                                    │
  filing_fetcher.py  → fetch HTML, extract Items 1, 1A, 7, 8,
                       truncate to 8K tok/sec, cache under
                       data/buffett/filings/
         │ section text                       │
         ▼                                    │
  llm_filing_parser.py  ───────────────► llm_client.py
                                         (prompt caching, tool-use)
         │
         ▼
  data/buffett/analysis/<TICKER>_profile.json
   { business_description, moat_type, moat_threats,
     management_signals, key_risks, revenue_drivers,
     competitive_position }

┌─────────────────────────────────────────────────────────────────┐
│              STAGE 2 — Analysis & Screening (screen)            │
└─────────────────────────────────────────────────────────────────┘
  CompanyProfile JSON   financials_provider.py   dcf_assumptions.yaml
        │              (FMP + EDGAR XBRL)              │
        ▼                       │                      │
  moat_scorer.py         quality_checker.py            │
  0.6 × quant +          4 hard gates                  │
  0.4 × LLM qual         (see §2.11.2)                 │
        └───────────┬───────────┘                      │
                    ▼                                  ▼
             quality_screener.py ────────────► dcf_calculator.py
                    │                          (owner-earnings DCF,
                    │                           3 scenarios + Gordon,
                    │                           reverse DCF)
                    ▼                                  │
             safety_margin.py  ◄────────── intrinsic_value
                    │ (margin = (IV − P) / IV)
                    ▼
             watchlist_manager.py
             data/buffett/watchlist.json

┌─────────────────────────────────────────────────────────────────┐
│         STAGE 3 — Market Enrichment (report / scorecard)        │
└─────────────────────────────────────────────────────────────────┘
  yfinance extended methods           yfinance OHLCV
  (free, 24h disk cache)                   │
         │                                 ▼
         ▼                          technical_analyzer.py
  market_data_enricher.py           (SMA-50/200, Golden/Death,
  (TTM income + cashflow,            RSI-14, 52w range + drawdown,
   analyst targets, upgrades/         beta, vol z-score, key
   downgrades, insider, top-5         support/resistance)
   institutional, news 90d,
   dividends)
         │
         ▼  TTM passed back into dcf_calculator → IV uses live revenue
            reverse DCF → market-implied growth rate at current price

┌─────────────────────────────────────────────────────────────────┐
│             STAGE 4 — Signals & Output (signals/report)         │
└─────────────────────────────────────────────────────────────────┘
  watchlist.json     OhlcvFeatureEngineer   portfolio.json
       │             (shared with ML)            │
       ▼                    ▼                    ▼
  entry_timer.py       (technicals)        sell_monitor.py
  (5 filters, see §2.4)                    (margin < -20%, moat < 5,
       │                                    or quality fail)
       ▼
  company_report.py     universe_scorecard.py
  (12 sections)         (ranked table)
       │                       │
       └───────────┬───────────┘
                   ▼
         buffett_pipeline.py  →  main_buffett.py (CLI)
```

Notes on cross-paradigm sharing: `entry_timer.py` reuses
`OhlcvFeatureEngineer` from `pipeline/ohlcv/dataset/` to compute SMA-50,
RSI, and volume z-score (see §4.1). No model weights cross the boundary.

### 2.11 Configs and thresholds reference

The consolidated index of every tunable knob that shapes a ticker's
composite score. Use as a lookup when tuning or diagnosing; the academic
lineage for each threshold lives in §6.

#### 2.11.1 `config/dcf_assumptions.yaml` — drives the **safety margin (40%)** component

```yaml
defaults:
  wacc: 0.09                          # discount rate
  terminal_growth_rate: 0.03          # Gordon perpetuity growth
  projection_years: 10                # explicit-period length
  margin_of_safety_threshold: 0.25    # ≥ 25% → BUY zone
  hold_zone_threshold: 0.10           # 10–25% → HOLD; <10% → REVIEW
  owner_earnings:
    maintenance_capex_pct_of_revenue: 0.03
    da_pct_of_revenue: 0.04
  dcf_scenarios:
    bull:  { revenue_cagr: 0.15, fcf_margin: 0.20, weight: 0.25 }
    base:  { revenue_cagr: 0.10, fcf_margin: 0.15, weight: 0.50 }
    bear:  { revenue_cagr: 0.04, fcf_margin: 0.10, weight: 0.25 }

sector_overrides:
  Technology:                          # ← used for AAPL, MSFT, NVDA, GOOG, …
    wacc: 0.10
    terminal_growth_rate: 0.04
    dcf_scenarios:
      bull: { revenue_cagr: 0.18, fcf_margin_trajectory: [0.25,0.27,0.30,0.32,0.35],
              terminal_fcf_margin: 0.35, weight: 0.30 }
      base: { revenue_cagr: 0.13, fcf_margin_trajectory: [0.25,0.26,0.28,0.30,0.32],
              terminal_fcf_margin: 0.30, weight: 0.50 }
      bear: { revenue_cagr: 0.07, fcf_margin_trajectory: [0.22,0.22,0.23,0.24,0.25],
              terminal_fcf_margin: 0.25, weight: 0.20 }
  Energy:           { wacc: 0.10, terminal_growth_rate: 0.02,
                      maintenance_capex_pct_of_revenue: 0.08 }
  Consumer Staples: { wacc: 0.08, terminal_growth_rate: 0.025 }
  Healthcare:       { wacc: 0.09, terminal_growth_rate: 0.035 }
  Financials:       { wacc: 0.10, terminal_growth_rate: 0.025 }

ticker_overrides: {}                   # per-ticker manual overrides
```

Resolution order (highest priority first): `ticker_overrides` →
`sector_overrides[<sector>]` → `defaults`. The `fcf_margin_trajectory`
block is honoured year-by-year (year-N entries beyond list length reuse
the final entry). Sectors without a trajectory use the flat `fcf_margin`
field. A separate `data_validation:` block in the same file holds the
TO-DO 1 tolerance bands (§2.6).

#### 2.11.2 Quality gates — `pipeline/buffett/analysis/quality_checker.py`

```python
ROIC_THRESHOLD          = 0.10    # > 10%
DE_THRESHOLD            = 1.5     # Debt/Equity < 1.5
CURRENT_RATIO_THRESHOLD = 1.5     # > 1.5
YEARS_LOOKBACK          = 5
MIN_PASSING_YEARS       = 3       # ROIC and FCF gates require 3 of 5 years
```

The **20% quality component** is purely `(passed / 4) × 100`.

#### 2.11.3 Moat scoring — `pipeline/buffett/analysis/moat_scorer.py`

```python
QUANT_WEIGHT          = 0.6      # quantitative sub-score weight
LLM_WEIGHT            = 0.4      # LLM qualitative sub-score weight
MOAT_SCORE_THRESHOLD  = 6.0      # in quality_screener.py — required for watchlist
THREAT_PENALTY        = 0.5      # per-threat reduction in LLM sub-score
POOR_SIGNAL_PENALTY   = 0.5      # per poor-mgmt keyword
YEARS_LOOKBACK        = 5
```

Plus the moat-type base table (`_MOAT_TYPE_BASE`) and `_POOR_MGMT_KEYWORDS`
set in the same file.

#### 2.11.4 Safety-margin zoning — `pipeline/buffett/analysis/safety_margin.py`

Thresholds read from `dcf_assumptions.yaml.defaults`. Mapping:

```
margin ≥ 25%          → BUY     → zone_pts = 100
10% ≤ margin < 25%    → HOLD    → zone_pts =  67
margin < 10%          → REVIEW  → zone_pts =  33
margin = None         → UNKNOWN → zone_pts =   0
```

#### 2.11.5 Entry timing — `pipeline/buffett/signals/entry_timer.py`

```python
RSI_THRESHOLD          = 65.0    # not overbought
VOL_ZSCORE_THRESHOLD   = 2.0     # 5-day volume z-score < 2.0
EARNINGS_BUFFER_DAYS   = 5       # avoid ±5 days around earnings
OHLCV_LOOKBACK_DAYS    = 120     # warm-up window for SMA-50 + RSI(14)
```

Plus the structural filter `price > 50-day SMA` (no separate constant).
All five must pass for `signal = "BUY"`.

#### 2.11.6 Sell monitor — `pipeline/buffett/signals/sell_monitor.py`

```python
_MOAT_FLOOR        = 5.0          # moat dropping below 5 → REDUCE
_OVERVALUED_MARGIN = -0.20        # price > 120% of IV → SELL
```

Quality-gate failures also trigger REDUCE. The asymmetry between BUY (25%
margin required) and SELL (-20% margin required to trigger) is intentional:
discourages churn (see §6.2).

#### 2.11.7 Composite weights — `pipeline/buffett/report/universe_scorecard.py`

```python
_ZONE_SCORE  = {"BUY": 100, "HOLD": 67, "REVIEW": 33, "UNKNOWN": 0, "ERROR": 0}
_ENTRY_SCORE = {"BUY": 100, "WATCH": 67, "WAIT": 33}

composite = 0.40 × zone_pts + 0.30 × moat_pts + 0.20 × quality_pts + 0.10 × entry_pts
```

#### 2.11.8 Universe and LLM — `config/settings.yaml: buffett:`

```yaml
buffett:
  universe:                      # 30 tickers — fixed, hand-curated
    - GOOG, NVDA, MSFT, TSLA, MU, PLTR, AAPL, META, DELL, SNDK
    - AMZN, NFLX, CRM, ORCL, AMD, AVGO, QCOM, TXN, ASML, TSM
    - INTC, SNOW, MDB, CRWD, SHOP, CSCO, XOM, TER, ROK, SYM
  llm:
    model: "claude-sonnet-4-6"
    max_tokens: 4096
    cache_filing_sections: true
  filings:
    cache_dir: "data/buffett/filings"
    max_tokens_per_section: 8000
    years_lookback: 3
  analysis:
    cache_dir: "data/buffett/analysis"
  watchlist_path: "data/buffett/watchlist.json"
  portfolio_path: "data/buffett/portfolio.json"
```

### 2.12 Expected outputs and runtime estimates

#### 2.12.1 Per-ticker report — `data/buffett/reports/<TICKER>_report.md`

```
# {TICKER} — Buffett Investment Report
Generated: YYYY-MM-DD | Sector: {sector}

## Zone: {emoji} {ZONE}  |  Entry: {emoji} {SIGNAL}

## 1. Business Summary             ← LLM extraction from 10-K
## 2. Moat Analysis                ← quant + LLM hybrid score, components shown
## 3. Financial Quality            ← 4-gate scorecard (ROIC / D-E / FCF / Cur-Ratio)
## 4. DCF Valuation                ← bull/base/bear table, base-revenue source label,
                                     reverse DCF (implied CAGR)
## 5. Safety Margin                ← margin %, BUY/HOLD/REVIEW classification
## 6. Market Context               ← 52w range, drawdown, MA flags, MA trend
                                     (Golden/Death cross), beta, 20d avg volume,
                                     key support/resistance
## 7. Analyst Consensus            ← mean/median/high/low targets, implied upside,
                                     last 5 upgrades/downgrades
## 8. Insider & Institutional      ← net 6m direction, last 8 transactions,
                                     top-5 institutional holders
## 9. Recent News & Catalysts      ← 10 headlines (yfinance, last 90d)
## 10. Dividend Analysis           ← annual dividend, yield, payout ratio, ex-date
## 11. Entry Timing                ← 5-filter status + SMA-200 reference (display only)
## 12. Investment Thesis           ← LLM streaming narrative
```

Sections 6–10 are populated from `EnrichedMarketData` and `TechnicalContext`
— no LLM calls. The synthesis-layer report (`reports/llm_reports/<T>_report.md`,
§2.8) adds Section 0 (Decision Box), 5b (Reconciliation), 5c (Sensitivity)
on top of this base structure.

#### 2.12.2 Cross-universe scorecard — `data/buffett/universe_scorecard_<date>.md`

```markdown
# Buffett Universe Scorecard — 2026-05-01
*30 tickers | Ranked by composite score (safety 40% + moat 30% + quality 20% + entry 10%)*

| Rank | Ticker | Price | IV/Share | Margin | Zone | Moat | Quality | Entry | Analyst Mean | Analyst Upside | Score |
|------|--------|-------|----------|--------|------|------|---------|-------|--------------|----------------|-------|
| 1    | …      | …     | …        | …      | …    | …    | …       | …     | …            | …              | …     |
| 30   | …      | …     | …        | …      | …    | …    | …       | …     | …            | …              | …     |

## Zone Summary
| Zone      | Count | Tickers |
|-----------|-------|---------|
| 🟢 BUY    | n     | …       |
| 🟡 HOLD   | n     | …       |
| 🔴 REVIEW | n     | …       |

## Quality Screen Summary
| Status            | Count |
|-------------------|-------|
| Pass (4/4 gates)  | n     |
| Near-pass (3/4)   | n     |
| Fail (≤2/4)       | n     |
```

From 2026-05-22 onwards the scorecard also carries a `Data Q` column
(OK / ⚠ WARN / 🚫 BLOCKED) from the cross-source validator (§2.6).

#### 2.12.3 Persistent state files

| File | Purpose | Refreshed on |
|---|---|---|
| `data/buffett/filings/<TICKER>_<YEAR>_10K.json` | Cached 10-K section text | `analyze` (or when missing) |
| `data/buffett/analysis/<TICKER>_profile.json` | LLM-extracted CompanyProfile | `analyze` |
| `data/buffett/market_data/<TICKER>_enriched.json` | yfinance enrichment (24h TTL) | `report` / `scorecard` |
| `data/buffett/watchlist.json` | Tickers passing quality + moat ≥ 6 | `screen` |
| `data/buffett/portfolio.json` | Held positions w/ cost basis | Manual |
| `data/buffett/reports/<TICKER>_report.md` | 12-section markdown | `report` / `full` |
| `data/buffett/universe_scorecard_<date>.md` | Ranked universe table | `scorecard` / `full` |
| `data/buffett/data_quality_report_<date>.md` | Cross-source comparison (§2.6) | `scorecard` / `full` |
| `data/buffett/infer/<TICKER>_infer.json` | Filing-aware infer cache (§2.9) | `infer` |
| `data/buffett/filing_monitor/<TICKER>.json` | Latest periodic-filing marker | infer / synthesis cache invalidation |
| `data/buffett/backtest/observations.parquet` | PIT quintile observations (§2.7) | `backtest` |
| `reports/backtest_reports/<ts>/buffett_iv_backtest/iv_backtest_<date>.md` | IV validation report (§2.7) | `backtest` |
| `reports/llm_reports/<TICKER>_report.md` | Synthesis-layer markdown report (§2.8) | `synthesis-report` |
| `reports/llm_reports/<TICKER>_synthesis.json` | Synthesis structured cache | `synthesis-report` |
| `reports/llm_reports/<TICKER>_archetype.json` | Archetype (90-day cache) | `synthesis-report` |

See §5.3 for the full cache-TTL companion table.

#### 2.12.4 Runtime estimates (30-ticker universe)

| Mode | Approximate runtime | API cost |
|---|---|---|
| `analyze` (cold cache, all 30) | 25–40 min | ~$0.30 / ticker (LLM, w/ prompt caching) |
| `screen` (cached) | ~2 min | $0 |
| `signals` | ~3 min | $0 |
| `report` (single ticker, w/ LLM thesis) | 35–50 sec | ~$0.05 (LLM thesis only) |
| `report` (all 30) | ~25 min | ~$1.50 |
| `scorecard` (all 30) | ~7 min | $0 |
| `synthesis-report` (single ticker, cold) | 60–120 sec | ~$0.25 |
| `synthesis-report` (24h cache hit) | <500 ms | $0 |
| `backtest` (cold, all 30, methods 1+5) | ~60 min | $0 (no LLM) |
| `backtest` (cached observations) | <5 min | $0 |
| `infer` (single ticker, cache miss) | 15–35 sec | ~$0.013 |
| `infer` (filing-cache hit) | sub-second | $0 |
| `full` (all 30) | ~60 min | ~$10 first run, ~$2 cached |

### 2.13 Key data sources

| Source | Used by | Notes |
|---|---|---|
| SEC EDGAR full-text 10-K | `filing_fetcher.py` | Free; SEC requires `User-Agent` header |
| SEC EDGAR XBRL Company Facts | `financials_provider.py` (via `edgar_client.py`) | Free; structured annual financials |
| SEC EDGAR submissions JSON | `filing_monitor.py` | Free; latest periodic-filing date for cache invalidation |
| Anthropic API (claude-sonnet-4-6) | `llm_client.py` | Paid; prompt caching ≈ 90% savings on re-runs |
| Anthropic native web search tool | `web_search_provider.py` | Paid; 24h disk cache; used by synthesis layer (§2.8) |
| yfinance — basic | `entry_timer.py`, `technical_analyzer.py` | Free; OHLCV + `.info` |
| yfinance — extended | `market_data_enricher.py` | Free; `ttm_income_stmt`, `ttm_cashflow`, `analyst_price_targets`, `upgrades_downgrades`, `insider_transactions`, `institutional_holders`, `news`, `calendar` |
| Financial Modeling Prep (FMP) | `financials_provider.py`, `consensus_fetcher.py` | Paid free-tier; primary financials source |
| Stooq EOD CSV | `data_validator.py` (TO-DO 1) | Free; price cross-check |
| Finnhub | `news_aggregator.py` (infer) | Free; 60 req/min company news |
| Yahoo Finance RSS | `news_aggregator.py` | Free; `feedparser`, no key required |
| Marketaux | `news_aggregator.py` | Free; 100 req/day |
| NewsData.io | `news_aggregator.py` | Free; 200 credits/day |
| Alpha Vantage | `news_aggregator.py` (bonus sentiment) | Free; 25 req/day; pre-computed `overall_sentiment_label` |
| NewsAPI | `news_fetcher.py` (legacy) | Free; superseded by the 4-source aggregator + yfinance news |

Release-5 will consolidate **all** of the above into a single paid News API
as the canonical source of truth — see §8.1 for the deprecation list that
follows.

---

## 3. Target 2 — `buffett-api` (FastAPI on Tailscale)

### 3.1 Architecture

```
Samsung phone (Chrome/Samsung Internet)
  │ HTTP over Tailscale (encrypted, private, no port forwarding)
  │ URL: http://100.x.x.x:8000/
  ▼
FastAPI app (pipeline/api/app.py, single uvicorn worker)
  │ HTTP Basic auth (username/password from env)
  │ Long pipeline calls go through asyncio run_in_executor so the
  │ event loop stays responsive (the spinner loads immediately)
  ▼
BuffettPipeline.run_infer_one() / run_synthesis_report_one() /
run_backtest_one() / run_full_one()
```

No app install on the phone — Chrome opens the Tailscale IP, can be saved as
a homescreen PWA shortcut for full-screen behaviour. Auth is HTTP Basic
behind the VPN (browser caches credentials after first prompt).

### 3.2 Endpoints

```
GET  /                                  — HTML index form (mobile)
POST /infer                             — runs infer pipeline (returns HTML card)
GET  /infer/{ticker}                    — same via URL (bookmarkable)
GET  /api/infer/{ticker}                — JSON response (curl/debug)

GET  /synthesis/{T}/decision            — mobile Decision Page card (cache read)
GET  /synthesis/{T}/full                — full markdown rendered as HTML
POST /synthesis/{T}/refresh             — async synthesis job; returns {job_id}
GET  /synthesis/jobs/{job_id}           — poll job status
GET  /synthesis/jobs                    — recent 20 jobs
GET  /api/synthesis/{T}                 — full synthesis JSON

POST /backtest/run                      — async backtest job; returns {job_id}
GET  /backtest/jobs/{job_id}            — poll
GET  /backtest/report/latest            — latest markdown report (text/markdown)
GET  /api/backtest/latest               — latest report metadata (JSON)

POST /scorecard/run                     — async `--mode full` job (same-day idempotent)
GET  /scorecard/jobs/{job_id}           — poll
GET  /scorecard                         — HTML fragment for index-page injection
GET  /scorecard/page                    — standalone bookmarkable page
GET  /api/scorecard/latest              — latest scorecard metadata

GET  /health                            — {"status":"ok"} (systemd liveness)
GET  /static/style.css, /static/manifest.json
```

Async jobs are coordinated by `pipeline/api/async_jobs.py` (`AsyncJobRunner`,
in-memory dict with TTL eviction by a background sweeper). Each long
endpoint type owns its own runner (synthesis: default 1h TTL, scorecard:
4h TTL because `--mode full` can take 30–60min cold and the user may resume
the page later). The phone polls `/jobs/{id}` every 3s; on completion the
page reloads, the Decision Page / scorecard renders fresh.

Sentinel `ticker=FULL` from the index form is detected in JS and routed to
`POST /scorecard/run` instead of `/infer` — `_is_valid_ticker()` rejects
the literal string so the infer endpoint never sees it.

### 3.3 Renderers

- `pipeline/api/renderer.py` — index form, infer result card, scorecard
  fragment + standalone page, scorecard-pending placeholder. All f-string
  HTML; no Jinja2 dependency.
- `pipeline/api/synthesis_renderer.py` — Decision Page card, full-report
  markdown-to-HTML, pending page with built-in JS that POSTs `/refresh`
  and polls.
- `pipeline/api/static/style.css` — ~100-line mobile-first stylesheet, no
  CDN, works offline on LAN.

Signal badge colours match the design spec: BUY = green `#16a34a`, WATCH =
amber `#d97706`, WAIT = red-orange `#dc2626`, AVOID = deep red `#7f1d1d`.
Synthesis verdict: BUY green, HOLD blue `#0ea5e9`, SELL red.

### 3.4 Deploy & ops

#### 3.4.1 Python dependencies (conda env `tf_gpu`)

**Environment:** use the Anaconda `tf_gpu` conda environment — no separate
`.venv` needed. The pipeline is always run inside `tf_gpu`; install all API
deps there too so only one environment activation is required.

```bash
# Activate the conda environment (tf_gpu is already used for all pipeline work)
conda activate tf_gpu

# Install all API + news deps into tf_gpu conda environment
pip install fastapi>=0.115
pip install uvicorn[standard]>=0.34
pip install feedparser>=6.0
pip install finnhub-python>=2.4
pip install python-multipart>=0.0.9    # required by FastAPI for HTML form submission (POST /infer)
pip install aiofiles>=23.0             # required by Starlette StaticFiles to serve style.css / manifest.json
```

`requirements-api.txt` (separate from core pipeline deps so the pipeline still runs without the API server):
```
fastapi>=0.115
uvicorn[standard]>=0.34
feedparser>=6.0
finnhub-python>=2.4
python-multipart>=0.0.9    # required by FastAPI for HTML form submission (POST /infer)
aiofiles>=23.0             # required by Starlette StaticFiles to serve style.css / manifest.json
```

**Note:** `python-multipart` and `aiofiles` are not optional — FastAPI 0.115+
raises a `RuntimeError` at startup if either is missing.

After installing, confirm uvicorn landed in the conda env:
```bash
which uvicorn
# → /home/victor/anaconda3/envs/tf_gpu/bin/uvicorn
```

#### 3.4.2 systemd service (runs FastAPI on server boot)

The `ExecStart` path must point to uvicorn **inside the `tf_gpu` conda env**,
not a project-local `.venv` (which was removed in favour of the conda env).

The service file lives at `deploy/buffett-api.service` in the repo and is
excluded from git (`.gitignore`) because it contains secret keys. Copy it to
systemd and enable:

```bash
sudo cp deploy/buffett-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now buffett-api
sudo systemctl status buffett-api     # confirm it's running
```

Reference content of `deploy/buffett-api.service`:

```ini
[Unit]
Description=Buffett Inference API (FastAPI + Uvicorn, served over Tailscale)
After=network.target tailscaled.service

[Service]
Type=simple
User=victor
WorkingDirectory=/home/victor/Workspace/ai-investment-pipeline
ExecStart=/home/victor/anaconda3/envs/tf_gpu/bin/uvicorn \
    pipeline.api.app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1
Restart=on-failure
RestartSec=5
Environment=PYTHONPATH=/home/victor/Workspace/ai-investment-pipeline
Environment=FAST_API_PASSWORD=...       # the HTTP Basic Auth password you chose
Environment=ANTHROPIC_API_KEY=...       # sk-ant-...
Environment=FINNHUB_API_KEY=...
Environment=MARKETAUX_API_TOKEN=...
Environment=NEWSDATA_API_KEY=...
Environment=ALPHA_VANTAGE_API_KEY=...

[Install]
WantedBy=multi-user.target
```

Verify from the server itself:
```bash
curl -u victor:YOUR_FAST_API_PASSWORD http://localhost:8000/health
# → {"status":"ok"}
```

#### 3.4.3 Phone setup (human reader guide — Victor)

**One-time setup — 5 minutes:**

**Step 1: Find your server's Tailscale IP**
```bash
# Run on the Linux server
tailscale ip -4
# → something like 100.x.x.x — note this down
```

**Step 2: Confirm Tailscale is active on your Samsung phone**
- Open the Tailscale app on your phone
- Check that your Linux machine appears as "Connected" in the device list
- If it does not appear: on the Linux server run `sudo tailscale up` and re-check

**Step 3: Open the web UI in Chrome**
- Open Chrome on your Samsung phone
- Navigate to: `http://100.x.x.x:8000` (replace with your actual Tailscale IP)
- A password prompt appears → enter username `victor` and your chosen password
- Chrome saves the credentials — you will never be prompted again

**Step 4: Add to homescreen (makes it feel like a native app)**
- In Chrome, tap the **three-dot menu** (⋮) in the top-right corner
- Tap **"Add to Home screen"**
- Rename to `Buffett Infer` (or leave as-is) → tap **Add**
- An icon now appears on your homescreen
- Tapping it opens the app full-screen (no browser address bar)

**Step 5: Test it**
- Tap the homescreen icon
- Type `MSFT` in the ticker box → tap the arrow button
- Wait 15-35 seconds (spinner shows)
- Result card appears with signal, gates, news, and LLM judgment

**Tip:** The Tailscale IP `100.x.x.x` is static — it never changes even if
your server's home IP changes. You do not need to update the bookmark.

#### 3.4.4 Bringing the server back up after a machine restart

The systemd service is configured with `WantedBy=multi-user.target` and
installed with `systemctl enable`, so **it starts automatically on every
boot — no manual action needed**.

To confirm it came up after a reboot:
```bash
sudo systemctl status buffett-api
# Active: active (running) ...
```

If for any reason the service did not auto-start (e.g. it was manually
stopped, or the service file was re-copied without re-enabling):

```bash
# Start it now (one-off, no reboot)
sudo systemctl start buffett-api

# Re-enable auto-start if it was disabled
sudo systemctl enable buffett-api

# Check it is running and port 8000 is open
sudo systemctl status buffett-api
ss -tlnp | grep 8000

# Quick health check from the server
curl -u victor:YOUR_FAST_API_PASSWORD http://localhost:8000/health
# → {"status":"ok"}
```

If the service fails to start, read the last 50 lines of the journal for
the exact error:
```bash
journalctl -u buffett-api -n 50 --no-pager
```

**Common causes of startup failure:**

| Symptom | Cause | Fix |
|---|---|---|
| `203/EXEC` | uvicorn binary not found at `ExecStart` path | Check conda env path with `which uvicorn` and update service file |
| `1/FAILURE` | Python crash at startup | Check `journalctl` — usually a missing package or wrong env var |
| `Active: active` but phone can't connect | UFW firewall blocking port 8000 | `sudo ufw allow in on tailscale0 to any port 8000` |
| Tailscale not connected | `tailscaled` service not running | `sudo tailscale up` |

---

## 4. File structure (Release-4 surface)

The ML paradigm (`pipeline/main_pipeline.py`, `pipeline/ohlcv/`,
`pipeline/training/`, `pipeline/fundamental_analysis/`) is **frozen and
untouched**. Release-4 added these directories:

```
pipeline/
  main_buffett.py                      # CLI entrypoint (all modes)
  buffett/
    buffett_pipeline.py                # Orchestrator + InferResult dataclass
    etl/
      filing_fetcher.py                # 10-K section extraction from EDGAR
      financials_provider.py           # FMP + EDGAR XBRL annual financials
      market_data_enricher.py          # yfinance: TTM, analysts, insiders, news
      news_aggregator.py               # NEW REL4: 4-source news + AV bonus
      news_fetcher.py                  # NewsAPI (optional/legacy)
      consensus_fetcher.py             # FMP analyst estimates (optional)
      data_validator.py                # REL4 TO-DO 1: cross-source validation
      filing_monitor.py                # REL4: filing-aware infer cache invalidation
      web_search_provider.py           # REL4 synthesis: Claude native web search
    analysis/
      llm_filing_parser.py             # LLM → CompanyProfile JSON
      quality_checker.py               # 4 hard pass/fail gates
      moat_scorer.py                   # Hybrid moat score [0..10]
      dcf_calculator.py                # 3-scenario DCF + reverse DCF + Graham
      safety_margin.py                 # BUY / HOLD / REVIEW zones
      technical_analyzer.py            # SMA, RSI, 52w range, beta, drawdown
      news_analyst.py                  # REL4: NewsAnalysisResult + LLM materiality
    screening/
      quality_screener.py              # quality+moat+DCF+safety+watchlist
      watchlist_manager.py             # data/buffett/watchlist.json upsert
    signals/
      entry_timer.py                   # 5-filter BUY/WATCH/WAIT signal
      sell_monitor.py                  # Thesis-break detection
    report/
      company_report.py                # 12-section per-ticker markdown report
      universe_scorecard.py            # Ranked cross-universe table
      data_quality_report.py           # REL4 TO-DO 1: side-by-side comparisons
    backtest/                          # REL4 TO-DO 2: IV validation
      pit_data.py                      # Point-in-time EDGAR + price assembly
      iv_replay.py                     # Replay DCF on quarterly grid
      method1_forward_returns.py       # Quintile spread + t-stat
      method5_mean_reversion.py        # Kaplan-Meier half-life
      method2_long_short.py            # Quarterly Q1−Q5 portfolio
      report.py                        # Composite markdown writer
      runner.py                        # IVBacktestRunner orchestrator
    synthesis/                         # REL5-prep (shipped in REL4)
      archetype_classifier.py
      cycle_position.py
      supply_side.py
      etf_tripwire.py
      valuation_reconciler.py
      sensitivity.py
      report_writer.py                 # Sonnet 4.6 orchestrator + markdown
      prompt_alignment.py              # Single-source-of-truth enforcer

  api/                                 # REL4: FastAPI mobile UI
    app.py                             # Endpoint routing + run_in_executor
    auth.py                            # HTTP Basic auth dependency
    renderer.py                        # Infer/index/scorecard HTML rendering
    synthesis_renderer.py              # Decision Page + full + pending
    async_jobs.py                      # AsyncJobRunner (TTL evict)
    templates/, static/                # index.html, style.css, manifest.json

config/
  settings.yaml                        # SHARED — added `buffett:`, `news_apis:`,
                                       #   `infer:`, `synthesis:`, `web_search:`,
                                       #   `api:` blocks
  dcf_assumptions.yaml                 # DCF defaults + sector/ticker overrides
                                       #   + `data_validation:` tolerance bands

data/buffett/
  filings/{TICKER}_{YEAR}_10K.json     # cached 10-K sections (cold-cache only)
  analysis/{TICKER}_profile.json       # CompanyProfile (LLM)
  market_data/{TICKER}_enriched.json   # yfinance enrichment (24h TTL)
  reports/{TICKER}_report.md           # 12-section markdown
  universe_scorecard_{YYYY-MM-DD}.md
  data_quality_report_{YYYY-MM-DD}.md  # REL4 cross-source comparisons
  watchlist.json, portfolio.json
  infer/{TICKER}_infer.json            # REL4 filing-aware infer cache
  filing_monitor/{TICKER}.json         # REL4 latest periodic-filing marker
  backtest/observations.parquet        # REL4 PIT quintile observations
  backtest/method2_nav.parquet         # REL4 long-short NAV series
  web_search_cache/{sha256}.json       # REL4 24h web search cache
reports/
  backtest_reports/<ts>/buffett_iv_backtest/iv_backtest_<date>.md
  llm_reports/{TICKER}_report.md       # REL4 synthesis-layer reports
  llm_reports/{TICKER}_synthesis.json
  llm_reports/{TICKER}_archetype.json
  llm_reports/picks_log.csv            # Append-only track-record log

deploy/
  buffett-api.service                  # systemd unit (gitignored — has secrets)

AI_stock_analysis/                     # Master prompt + skill spec
  prompt_stock_analysis.md             # Single source of truth for synthesis
  prompt_portfolio_rebalancing.md
  README.md
```

### 4.1 Shared dependencies across paradigms

Strict isolation: nothing in `pipeline/buffett/` imports from
`pipeline/ohlcv/models.py`, `pipeline/training/`, or `main_pipeline.py`.

| Shared module | Used by |
|---|---|
| `pipeline/utils/logger.py` | Both |
| `pipeline/utils/utils.py` (`load_config`, `PROJECT_ROOT`) | Both |
| `pipeline/fundamental_analysis/etl/edgar_client.py` | Both (XBRL financials) |
| `pipeline/ohlcv/dataset/ohlcv_feature_engineer.py` | ML training + Buffett `entry_timer.py` |
| `pipeline/ohlcv/backtest/metrics.py` (`BacktestMetrics`) | ML backtest + Buffett `method2_long_short.py` |
| `config/settings.yaml` | Both |
| `reports/backtest_reports/<ts>/...` directory layout | Both — paves the way for a rel-5 unified reporter |

---

## 5. Code-related knowledge for developers

### 5.1 Configuration resolution & secrets

`config/settings.yaml` is the single config file. Secrets are referenced as
`"${ENV_VAR}"` and resolved by `load_config()` from the environment — never
commit raw keys. The `api.password` field reads `FAST_API_PASSWORD`. News
keys read `FINNHUB_API_KEY` / `MARKETAUX_API_TOKEN` / `NEWSDATA_API_KEY` /
`ALPHA_VANTAGE_API_KEY`. DCF resolution order is `ticker_overrides` →
`sector_overrides[<sector>]` → `defaults` (see
`dcf_calculator.py: _wacc/_terminal_growth/_scenarios_cfg`).

### 5.2 Coexistence rules

The two paradigms share `config/settings.yaml`, `utils/`,
`edgar_client.py`, `OhlcvFeatureEngineer`, and `BacktestMetrics`. Nothing
else. When extending the Buffett pipeline:

- **Do not import** from `pipeline/training/*` or `pipeline/ohlcv/models.py`.
- **Do reuse** `BacktestMetrics.compute()` for any Sharpe/Sortino/MaxDD you
  add — keeps numbers comparable across paradigms.
- **Do honour** the `reports/backtest_reports/<timestamp>/...` layout so a
  future rel-5 aggregator can fold both pipelines into one report index.

### 5.3 Caching layers (always check the right one when debugging)

| Cache | TTL | Path |
|---|---|---|
| Filing sections (LLM input) | until manual refresh | `data/buffett/filings/` |
| CompanyProfile (LLM output) | until `--mode analyze` runs | `data/buffett/analysis/` |
| Market enrichment (yfinance) | 24h | `data/buffett/market_data/` |
| Infer result | filing-aware + 7d safety | `data/buffett/infer/` |
| Filing marker (EDGAR submissions) | thin disk cache | `data/buffett/filing_monitor/` |
| Data-validator secondary sources | 6h | `data/buffett/data_validation_cache/` |
| Web search (Claude native tool) | 24h | `data/buffett/web_search_cache/` |
| Synthesis report (full output) | 24h | `reports/llm_reports/` |
| Archetype classifier | 90d | `reports/llm_reports/<T>_archetype.json` |
| Backtest IV observations | until `--backtest-force-recompute` | `data/buffett/backtest/` |
| Per-ticker EOD prices (backtest) | until manual delete | `data/buffett/backtest/prices/` |

`--force-refresh` bypasses all per-step caches in CLI modes; the `/refresh`
endpoints in the FastAPI surface set `force_refresh=True` for their
respective layer.

### 5.4 LLM call pattern

`pipeline/llm/llm_client.py` (shared, untouched in rel-4) wraps the
Anthropic SDK with: (a) server-side prompt caching enabled by default,
(b) automatic retry with exponential backoff, (c) structured tool-use for
JSON-schema responses, (d) usage metadata captured per call. Every new
LLM call in rel-4 (`news_analyst.py`, `archetype_classifier.py`,
`cycle_position.py`, `supply_side.py`, `etf_tripwire.py`,
`report_writer.py`) goes through it. Model defaults to
`claude-sonnet-4-6` per `settings.yaml`.

### 5.5 Prompt-alignment invariant

`pipeline/buffett/synthesis/prompt_alignment.py` is the contract enforcer
between `AI_stock_analysis/prompt_stock_analysis.md` (the canonical spec)
and the component prompts under `pipeline/buffett/synthesis/`. A manifest
declares, per component, which master section it implements and a list of
anchor keywords that must appear in both files. Every infer and
synthesis-report call validates this before spending LLM tokens; the CLI
exits non-zero on drift, and the FastAPI endpoints return HTTP 409 with the
diff so the phone sees exactly what changed. Per-process mtime-keyed cache
keeps re-runs sub-millisecond.

### 5.6 Async jobs gotcha

`AsyncJobRunner` is **in-memory** — restarting the FastAPI process loses
in-flight jobs. The sweeper evicts completed/failed jobs after the runner's
TTL (1h default, 4h for the scorecard runner). Submitting an already-queued
ticker creates a second job; if you want dedupe, build it on top.

### 5.7 Single-user assumption

The whole FastAPI surface is built for one user, one worker. No request-
scoped state, no per-tenant caching, no rate limiting beyond what each
external API enforces. Don't bolt on multi-tenant features without
revisiting the AsyncJobRunner and the file-cache layout.

### 5.8 Test footprint

`tests/test_data_validator.py` (12 tests) covers WARN/BLOCKED bands,
`UNAVAILABLE` degradation, sector-string compare, disabled-config short-
circuit, TTM-from-quarterly arithmetic (4-quarter sum, amended-filing
precedence, annual-form filtering), and a renderer smoke test. The wider
suite (`python -m pytest tests/`) passes 65/65 as of 2026-05-21. No live
yfinance / EDGAR / Stooq calls happen in tests — the validator is exercised
via a `_secondary_override` shim.

---

## 6. Financial knowledge and discussions

> Distilled from `rel4_buffett_educational_discussions.md`. References to
> academic sources are kept inline so future readers can follow the lineage
> without re-deriving the rationale.

### 6.1 Why the composite is 40/30/20/10

Encodes Buffett's stated priority order, not a statistical optimisation
(which would overfit on 30 tickers × 8 years of history).

| Weight | Component | Justification | Primary source |
|---|---|---|---|
| 40% | Safety margin | "Even a perfect business at the wrong price destroys returns." | Graham, *The Intelligent Investor* (1949), Ch. 20 |
| 30% | Moat | Wide moat compounds at high ROIC for decades; without one ROIC mean-reverts to WACC. | Buffett 1995 letter; Dorsey, *The Little Book That Builds Wealth* (2008) |
| 20% | Quality gates | Eliminates "value traps" that look cheap but are deteriorating. | Greenblatt, *Magic Formula* (2005); Piotroski F-Score (2000) |
| 10% | Entry signal | Timing is a small nudge — never override fundamentals. | Jegadeesh & Titman (1993) |

### 6.2 Thresholds and lineage

- **Margin of safety ≥ 25%** — Graham's 33% rule (book-based) loosened by
  Buffett to "at least 25%" when the yardstick became DCF intrinsic value
  (Berkshire letters 1992, 1996). 25% sits at the lower end of consensus
  (Graham/Klarman/Greenblatt/Pabrai), defensible for the rel-4 high-quality
  large-cap universe. Sector-tunable in `dcf_assumptions.yaml`.
- **Quality gate cuts (ROIC > 10%, D/E < 1.5, FCF > 0, current ratio > 1.5)** —
  Piotroski F-Score and Greenblatt's Magic Formula heritage. The "≥3 of last
  5 years" structure tolerates one bad year without disqualifying the
  company.
- **Moat 0.6 quant + 0.4 LLM** — quant side measures realised moat outcomes
  (margin stability, ROIC vs WACC, revenue consistency); LLM side classifies
  *type* (network effect / brand / switching cost / cost advantage /
  efficient scale / none) from the 10-K. Watchlist threshold = 6.0 ≈ the
  Morningstar "narrow vs wide moat" boundary. Sources: Dorsey 2008,
  Greenwald 2005, Porter 1980.
- **Entry filter values** — SMA-50 (Edwards-Magee 1948; Faber 2007;
  Jegadeesh-Titman 1993); RSI-14 < 65 (deliberate tightening of Wilder
  1978's 70 because the universe skews high-momentum tech); volume z-score
  < 2.0 (Gaussian 95% convention; informed-trading microstructure —
  Easley & O'Hara 1992; Lehmann 1990); ±5 day earnings buffer (Bernard &
  Thomas 1989 PEAD; Ball & Brown 1968).
- **Sell triggers** — `_OVERVALUED_MARGIN = -0.20` (price > 120% of IV) and
  `_MOAT_FLOOR = 5.0`. The 25%-required-to-buy vs −20%-required-to-sell
  asymmetry is intentional: discourages churn, holds great businesses
  through fair value.

Empirical fragility ranking (tune in this order if backtested):
RSI=65 > vol z=2 > SMA=50 > earnings=5d > margin=25%.

### 6.3 Technical analysis — what's in and what's deliberately out

In (chosen from families A, B, D only): SMA-50/SMA-200, Golden/Death cross
flag, RSI-14, 5-day volume z-score, 20-day average volume, 52-week range &
drawdown, beta, earnings-date proximity.

Out (chart patterns, Fibonacci retracements, Elliott waves, MACD/Bollinger/
ADX/Stochastic overlap with what's used, multi-timeframe confirmations,
sentiment / on-chain / short-interest, microstructure breadth) — all
omitted to avoid parameter sprawl and false precision. SMA-200 is computed
and displayed but **deliberately not gated**, since Buffett-style holding
periods make a 50-day filter already generous.

### 6.4 Reading the entry signal output

- **BUY** — all 5 pass. Rare, high-conviction.
- **WATCH** — safety margin passes but a technical fails. *Most actionable
  state* — fundamentals say own; you're waiting for a better entry.
- **WAIT** — safety margin fails. Don't bother with the technicals.

Worked examples in the original educational notebook covered MSFT (price-
driven WAIT, 4/5 technicals green), INTC (broken-and-overbought — RSI 86.6),
NVDA (-96% margin — technicals irrelevant), and AAPL (17% margin, HOLD-zone
new-capital question).

### 6.5 Portfolio construction & risk (the 11-stock case)

Captured for reference — **no code changes proposed here**. The investor
operates 4 tax-sheltered accounts (1+2+4+4 = 11 names, individual stocks
only, weekly–monthly trading cadence). Two decisions face this setup:
allocation (how to size 11 positions) and risk management (what to do when
things go wrong).

The reasoned-out stack is *not* MVO / Black-Litterman / put-hedging
(wrong inputs or wrong scale). Instead, the chosen combination is:

| Layer | Method | Trigger frequency |
|---|---|---|
| 1 | Tiered concentration ceilings (70%/85% absolute floor) | rare |
| 2 | Sector trailing stop on SOXX (regime-change circuit breaker) | once-per-cycle |
| 3 | Pyramid-out on cost-basis milestones (100/300/700% per position) | 1–2× per position lifetime |
| 4 | Volatility-regime concentration cap (tightens when sector vol spikes) | slow-moving |
| Backbone | Claude prompt orchestrator (`/portfolio-review`) | 2–3× per week |

Persistent state lives in **Google Sheets** (mobile-editable from Android,
GOOGLEFINANCE for live prices). The Claude prompt is stateless; the sheet's
"Claude Input Export" tab produces a single-cell pasteable string. This
workflow (TO-DOs 3 and 4 in the educational notebook) is documented as a
plan, not yet implemented in code — see §8 below.

Key behavioural rules adopted:
- Trade only on signal flips, sell-monitor alerts, or composite-score
  changes ≥10 points. Else hold (Barber & Odean 2000: over-trading is the
  dominant cause of retail under-performance).
- Drawdown protocol at the *portfolio* level: −15% triggers a written
  re-justification of every position; −30% halts new buys for 2 weeks.
  Price drops *alone* never trigger sells.
- For the forced-concentration P1 (1 stock): at −30% with fundamentals
  intact, the *correct* action is to **add** capital, not sell.

### 6.6 The honest meta-observation

The biggest improvement is not adding more indicators — it's
**measuring whether the current 5 filters actually help**. Method 1 of the
rel-4 backtest produced strong evidence the IV signal has predictive power
(+31.6%/yr Q1−Q5 spread, t=5.38 over 2018–2025), but Method 5 shows IV
gaps don't reliably close — meaning returns may be momentum-driven rather
than value-driven. Resolving this disagreement is open work.

---

## 7. Rel-4 Acceptance Criteria

> Initialized with my (assistant) reading of the three rel-4 notebooks plus
> the current codebase. Victor will add personal acceptance criteria below.

### 7.1 Pipeline (Target 1)

- [x] **AC-P1**: `python -m pipeline.main_buffett --mode analyze --tickers AAPL`
  produces `data/buffett/analysis/AAPL_profile.json` with the documented
  `CompanyProfile` schema (business_description, moat_type, moat_threats,
  management_signals, key_risks, revenue_drivers, competitive_position).
- [x] **AC-P2**: `--mode screen` walks the 30-ticker universe and emits a
  `watchlist.json` containing every ticker that passes all four quality
  gates and has `moat_score ≥ 6.0`.
- [x] **AC-P3**: `--mode signals` emits a per-watchlist `BUY/WATCH/WAIT`
  using the five-filter `entry_timer.py` and a per-portfolio
  `HOLD/REDUCE/SELL` from `sell_monitor.py`. Confirmed by `_run_signals`
  returning `confirmed_buys` and `sell_alerts` arrays.
- [x] **AC-P4**: `--mode report` produces a 12-section markdown per ticker
  (`data/buffett/reports/<T>_report.md`) covering business summary, moat,
  financial quality, DCF valuation, safety margin, market context, analyst
  consensus, insider & institutional, news, dividends, entry timing,
  investment thesis.
- [x] **AC-P5**: `--mode scorecard` produces
  `data/buffett/universe_scorecard_<YYYY-MM-DD>.md` ranking the universe
  by the 0.4/0.3/0.2/0.1 composite. The file is observed in the repo on
  2026-05-01, 2026-05-06, 2026-05-22, 2026-05-27, 2026-05-28.
- [x] **AC-P6**: `--mode full` chains analyze → screen → signals → report →
  scorecard and produces the data-quality report alongside the scorecard
  in the same run.
- [x] **AC-P7** (TO-DO 1): cross-source data validation runs inside
  `DCFCalculator.calculate()`; tolerance bands live in
  `config/dcf_assumptions.yaml: data_validation:`; BLOCKED tickers skip
  the DCF math and surface in `data_quality_report_<date>.md`;
  secondary-source unreachability degrades to `UNAVAILABLE`. 12 unit tests
  pass.
- [x] **AC-P8** (TO-DO 2): `--mode backtest --methods 1,5` completes on
  cached observations under 5 minutes; cold run under 60 minutes; output at
  `reports/backtest_reports/<ts>/buffett_iv_backtest/iv_backtest_<date>.md`;
  honours `--backtest-force-recompute`. `--methods 1,5,2` adds the long-
  short Method 2 with `BacktestMetrics`-computed Sharpe/Sortino/MaxDD.
- [x] **AC-P9**: `--mode synthesis-report` produces both the 14-section
  markdown report and the structured JSON cache under `reports/llm_reports/`.
  Cost ≈ $0.25 cold, $0.04 cached; latency 60–120s cold, <500ms cached.
- [x] **AC-P10** (rel-4 evolution): infer cache is *filing-aware* — a new
  10-K/10-Q on EDGAR invalidates the cache regardless of wall-clock age,
  while a 7-day TTL acts as a safety net.
- [x] **AC-P11**: `PromptAlignmentChecker.enforce_alignment()` is invoked
  before any LLM work in `run_infer_one()` and `run_synthesis_report_one()`;
  master spec at `AI_stock_analysis/prompt_stock_analysis.md` and component
  files are mtime-cached so the check is sub-millisecond after the first
  call.

### 7.2 API (Target 2)

- [x] **AC-A1**: `pipeline/api/app.py` exposes the full endpoint surface
  documented in §3.2 (infer × 3, synthesis × 6, backtest × 4, scorecard ×
  5, health, static). All non-health endpoints are gated by
  `make_auth_dependency(config)`.
- [x] **AC-A2**: long pipeline calls are dispatched via
  `asyncio.run_in_executor` so the single uvicorn worker remains responsive
  during the 15–35s infer window and the 60–120s synthesis window.
- [x] **AC-A3**: `AsyncJobRunner` provides three independent runners
  (synthesis 1h TTL, backtest 1h TTL, scorecard 4h TTL) with a background
  sweeper started at app boot.
- [x] **AC-A4**: `_is_valid_ticker()` rejects the literal `FULL` sentinel
  so the index form's `ticker=FULL` shortcut routes to `/scorecard/run`
  rather than producing a generic infer failure.
- [x] **AC-A5**: prompt-alignment drift surfaces as HTTP 409 with the diff
  rendered to a mobile-readable page (see `_render_alignment_failure_html`).
- [x] **AC-A6**: systemd unit at `deploy/buffett-api.service` runs uvicorn
  out of the `tf_gpu` conda env with 1 worker, restarts on failure, and
  passes all secrets through environment variables. The file is gitignored.
- [x] **AC-A7**: phone PWA flow works end-to-end — Chrome → Tailscale IP →
  HTTP Basic prompt → "Add to Home Screen" → tap launches full-screen,
  submit a ticker, see a result card in 15–35s.

### 7.3 Cross-paradigm

- [x] **AC-X1**: nothing in `pipeline/buffett/` imports from
  `pipeline/ohlcv/models.py`, `pipeline/training/`, or `main_pipeline.py`.
- [x] **AC-X2**: the ML paradigm runs unchanged: `python -m pipeline.main_pipeline …`
  produces the same artefacts and metrics as before rel-4.
- [x] **AC-X3**: the rel-4 backtest reuses `BacktestMetrics.compute()` from
  the ML paradigm unchanged, and writes its reports under the same
  `reports/backtest_reports/<ts>/` root layout.

### 7.4 Documentation

- [x] **AC-D1**: this `rel4_document.md` exists and supersedes the three
  working notebooks.

---

## 8. Rel-4 Remainings (re-evaluated against Release-5 plans)

Release-5 will consolidate **all** raw inputs — fundamentals, ratios, OHLCV,
and news — behind a **single paid News API** acting as the canonical source
of truth, eliminating yfinance/EDGAR/Stooq/FMP/Finnhub/Marketaux/NewsData/
Alpha-Vantage as parallel providers. Several rel-4 remainings collapse under
that decision; the rest are sorted below into "deprecated by rel-5",
"deferred until rel-5 data lands", "carried-over TO-DOs (kept verbatim)", and
"still actionable now".

### 8.1 Deprecated by the Release-5 single-source data revamp

These items will dissolve naturally when the paid News API becomes the
canonical source — no separate work order needed in rel-5:

- **The `DataValidator` cross-source check (rel-4 TO-DO 1) will be removed.**
  With one authoritative source, there is nothing to cross-check; the
  `data_validator.py` module, `data_validation:` config block,
  `data_quality_report_*.md` artifact, and `data_validation_cache/` disk
  cache all retire together. Keep the module in tree until the rel-5 data
  layer is wired, then delete in one commit.
- **Wide tolerance bands** on the validator's TTM fields (3–15%) — moot once
  the validator is gone.
- **Sector taken from the `yfinance.info.sector` snapshot** — replaced by
  whatever the new provider exposes as the canonical sector field.
- **The `Filing-aware infer cache` will still be valid**, but the EDGAR
  submissions probe inside `FilingMonitor` likely becomes a provider call
  instead. The cache invariant (cache survives until the latest periodic
  filing date changes) is unchanged.

### 8.2 Deferred behind the rel-5 data upgrade

These are real rel-4 issues, but the answers depend on having the new data
source in place. Re-open after rel-5 data lands; do not invest in patching
rel-4-era data first.

- **Backtest credibility (Method 5 FAIL).** The 2026-05-26 run showed
  Method 1 PASS (+31.6%/yr Q1−Q5 spread, t=5.38, N=1584) but Method 5 FAIL
  (cheap-side gaps largely don't close: 9% uncensored over 364 triggers).
  Possible explanations include (a) returns are momentum-driven and IV is
  mis-centered, (b) the 8-year window is too short, (c) the underlying
  EDGAR-XBRL + yfinance data has subtle PIT errors that distort the
  half-life walk. (a) and (b) are real signals; (c) is a data artefact.
  Cleanly disambiguating between them requires the rel-5 data source —
  re-run the backtest first thing once that lands, *then* decide whether
  to swap the IV anchor (EPV, Monte-Carlo DCF).
- **Survivorship bias** in the backtest universe (current 30 tickers
  applied historically). A historical S&P-100 membership table is the
  right fix; sourcing it should be folded into the rel-5 data work.
- **Method 2 ignores transaction costs and short-borrow costs.** Worth
  modelling, but do it on the rel-5 data so the cost calibration matches
  the new return series rather than the soon-to-be-retired one.
- **The commit message for the initial backtest acknowledged "backtest
  logic is not solid" (e9de98f).** Deeper review of the IV-replay path
  (look-ahead, restatement leakage, dividend handling) is warranted, but
  do it against the rel-5 dataset — debugging a PIT pipeline twice is
  wasteful.

### 8.3 Carried-over TO-DOs (not top priority for Release-5, kept here in full)

The two TO-DOs below were specced in
`rel4_buffett_educational_discussions.md` and remain unimplemented. They
are not Release-5 blockers, but losing the full spec would make them hard
to pick up later — the bodies are reproduced verbatim so this document
stays self-contained after the original notebook is deleted.

#### 8.3.1 TO-DO 3 — Portfolio review prompt as a Claude Code slash command (Android-accessible)

**Motivation**: §6.5 selected a 4-method concentration management stack
(A + B + C + E) orchestrated by a single Claude prompt run 2–3× per week.
The prompt itself is drafted (see conversation transcript or §6.5 reference)
but needs to be installable as a repeatable, mobile-accessible workflow.
Goal of this task: zero-friction invocation from desktop terminal AND from
Android phone.

**Goal**: install the portfolio-review prompt as a Claude Code slash command
at the project level so the investor can invoke it with a single command,
paste portfolio holdings, and receive structured analysis. Provide
documented Android access paths so the workflow runs from a phone in under
60 seconds end-to-end.

##### Files to create

1. **`.claude/commands/portfolio-review.md`** — Claude Code slash command
   file.
   - Format: standard Claude Code slash-command markdown. The file body
     becomes the prompt that is sent to Claude when the user types
     `/portfolio-review` in Claude Code.
   - Body content: the complete prompt drafted in §6.5 conversation
     (Methods A/B/C/E orchestration, holdings input format, output
     structure).
   - The command should accept the holdings table either inline (pasted
     after the slash command) or via a `$ARGUMENTS` variable so the user
     can pass content directly.

2. **`prompts/portfolio_review_template.md`** — canonical copy of the prompt
   for non-Claude-Code use cases (web Claude, mobile Claude.ai). Same
   content as the slash command body. Investor can copy-paste this into any
   Claude interface.

3. **`prompts/README.md`** — short index documenting the prompts directory
   and how each is intended to be invoked.

##### Slash command structure

The `.claude/commands/portfolio-review.md` file should follow this skeleton:

```markdown
---
description: Run the 2-3x/week portfolio concentration review (Methods A/B/C/E)
argument-hint: [paste holdings table as multi-line string, or leave blank to be prompted]
---

[full prompt body from §6.5 — context, methods, inputs, tasks, output format, edge cases]

## Investor's holdings for this review

$ARGUMENTS
```

Notes for the implementing agent:
- If `$ARGUMENTS` is empty, the prompt should explicitly ask the investor
  to paste the holdings table.
- The prompt body should be self-contained — do not depend on any other
  CLAUDE.md content. It must work even if invoked in a fresh Claude Code
  session.
- Date/time reference: use the system's current date implicitly; do not
  hard-code.

##### Android access — three documented paths

The TO-DO must produce documentation (in `prompts/README.md`) covering all
three:

| Path | Setup | Trade-off |
|---|---|---|
| **A. Termux + Claude Code** | Install Termux, install Node.js, install `@anthropic-ai/claude-code` npm package, authenticate. Then `cd` to the project and run `claude` to enter Claude Code; type `/portfolio-review` and paste. | Fully native; requires one-time Termux setup; uses phone compute. |
| **B. SSH from Android to a desktop running Claude Code** | Use Termux SSH client or any Android SSH app (JuiceSSH, Termius). Connect to the desktop, `cd` to project, run `claude`, invoke command. | Best UX once SSH is configured; requires desktop to be on. |
| **C. Claude.ai web (mobile browser)** | Open claude.ai in mobile browser. Paste the contents of `prompts/portfolio_review_template.md` followed by the holdings table. | No setup; loses Claude Code's project context (web Claude can't access local files), but the prompt is self-contained so this is fine. |

The README must explicitly note: **paths A and B run inside this repo and
have access to the data/ folder** (so future enhancements could read
holdings from local JSON if the investor opts for that). **Path C is fully
standalone** — no local file access — and is the recommended fallback when
the desktop is off.

##### Optional convenience wrapper (nice-to-have, not required)

A small shell script `scripts/portfolio_review.sh`:
```bash
#!/usr/bin/env bash
# Convenience wrapper: launches Claude Code with the portfolio-review command pre-staged.
# Usage: ./scripts/portfolio_review.sh
exec claude --command portfolio-review
```

Skip this if Claude Code's native slash-command discovery already makes
invocation trivial.

##### What NOT to build in this task

- **No Anthropic API direct integration.** The investor explicitly chose
  Claude Code (interactive, terminal-based) over API calls. Do not write
  Python that calls `anthropic.Anthropic().messages.create(...)`. Future
  work might add an API-based scheduled run, but that is out of scope here.
- **No automatic execution of recommended trades.** The prompt produces
  recommendations only. Trade execution remains manual.
- **No persistent state inside the prompt.** Pyramid-tier counters live in
  the Google Sheet (TO-DO 4), not in code. The slash command is stateless
  by design.

##### Acceptance criteria

1. Typing `/portfolio-review` in Claude Code (this project's directory)
   loads the portfolio-review prompt and prompts the investor for holdings
   input.
2. Pasting a sample holdings table (provided in `prompts/sample_holdings.txt`
   for testing) produces a structured response with all six required output
   sections (Summary, Concentration snapshot, Method status, Recommended
   actions, Side notes, Methodology footnote).
3. The same prompt body, copy-pasted into claude.ai web, produces equivalent
   output (validates self-containment).
4. `prompts/README.md` documents all three Android access paths with the
   exact setup commands for path A (Termux).
5. No new Python dependencies introduced. No Anthropic API key required for
   this workflow.

##### Edge cases the agent must handle in the prompt body

These are content requirements for the slash command body, not
implementation tasks:
- Missing SOXX data → fall back to SMH; if both fail, suspend Methods B/E
  with a clear note.
- Missing avg-cost on a position → skip Method C for that position; flag in
  side notes.
- Single-stock portfolio (P1) treated correctly — concentration in P1 is
  structural, not actionable at the account level.
- A ticker held in multiple sub-portfolios → aggregated for concentration,
  but trades recommended per sub-portfolio.

#### 8.3.2 TO-DO 4 — Google Sheets template for holdings & rebalancing ledger

**Motivation**: §6.5 designated Google Sheets as the persistent holdings
ledger feeding the Claude prompt. The Sheet does not yet exist; this task
defines the template structure, formulas, and one-time setup.

**Goal**: a public, copy-able Google Sheets template that an investor can
clone in 30 seconds, populate with holdings, and immediately use as the
input source for the portfolio-review prompt (TO-DO 3). Tab structure must
support 4 sub-portfolios (RRSP, RESP, TFSA-*), currently holding tickers,
pyramid-tier tracking, live price refresh, and a one-cell "export for
Claude" view. All formulas are draggable and Google Sheets-compatible.

##### Tab structure

The template must add exactly these five tabs in this order:

###### Tab 1 — `Holdings`
The single source of truth. Columns:

| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| Portfolio | Ticker | Shares | Avg Cost | Live Price | Current Value | Unrealized Gain (Loss) | Unrealized Return % | Sector | AI Capex Cluster (Y/N) | Pyramid Tiers Taken (0-3) |

- Column B (Ticker) is dynamically updated from the 4 tabs "RRSP", "RESP",
  "TFSA-Thang", "TFSA-Thao", displaying only tickers with the latest
  "Cum Qty" (Column M) larger than 0. If a ticker is sold out
  ("Cum Qty"=0), it should not be shown in the table any more.
- Column E (Live Price) formula: `=IFERROR(GOOGLEFINANCE(B2, "price"), "N/A")`
- Column F: `=C2*E2`
- Column H: `=IF(D2>0, (E2-D2)/D2, "")` formatted as percentage
- Column K: integer 0–3 (manually updated when pyramid-out trims are
  executed)
- Conditional formatting on columns G & H: green if > 100%, brighter green
  > 300%, brightest > 700% — visual cue that a pyramid-out tier is due.

###### Tab 2 — `Concentration`
Summary view. Three blocks:

**Block A — By portfolio (sub-portfolio NAV)**:
| Portfolio | NAV | % of total |
|---|---|---|
| P1_RRSP | `=SUMIF(Holdings!A:A, "P1_RRSP", Holdings!F:F)` | … |
| P2_TFSA | … | … |
| P3 | … | … |
| P4 | … | … |
| **TOTAL** | … | 100% |

**Block B — By GICS sector**:
| Sector | NAV | % of total |
|---|---|---|
| Technology | `=SUMIF(Holdings!H:H, "Technology", Holdings!F:F)` | … |
| (etc.) | … | … |

Conditional formatting on % column: green < 40%, yellow 40–55%, orange
55–70%, red > 70%.

**Block C — AI Capex cluster**:
| Cluster | NAV | % of total |
|---|---|---|
| AI capex (col I = "Y") | `=SUMIF(Holdings!I:I, "Y", Holdings!F:F)` | … |
| Non-cluster | … | … |

Same conditional formatting as sectors.

###### Tab 3 — `Pyramid Tracker`
For each holding, automatically flag tier-due status.

| Ticker | Total Return % | Tiers Taken | Tier 1 (≥100%) | Tier 2 (≥300%) | Tier 3 (≥700%) | Action Due? |
|---|---|---|---|---|---|---|
| (one row per holding via ARRAYFORMULA from Holdings tab) | | | | | | |

Logic for "Action Due?":
- If `Total Return ≥ 100%` AND `Tiers Taken < 1` → "TIER 1 DUE"
- If `Total Return ≥ 300%` AND `Tiers Taken < 2` → "TIER 2 DUE"
- If `Total Return ≥ 700%` AND `Tiers Taken < 3` → "TIER 3 DUE"
- Otherwise → "—"

Conditional formatting: highlight any "DUE" cell in red.

###### Tab 4 — `Trade Log` (append-only)

| Date | Portfolio | Ticker | Action (BUY/SELL) | Shares | Price | Method that triggered | Notes |
|---|---|---|---|---|---|---|---|

This is purely manual. Used to:
- Audit decisions over time.
- Reconstruct cost basis if Holdings tab is corrupted.
- Update pyramid tier counts on Holdings tab manually after a SELL.

Realized P&L can be computed at the bottom of this tab via SUMPRODUCT if
desired.

###### Tab 5 — `Claude Input Export`

A single cell (e.g., `B2`) that uses a `TEXTJOIN` / `ARRAYFORMULA`
combination to produce the exact pipe-delimited holdings string expected by
the portfolio-review prompt:

```
=TEXTJOIN(CHAR(10), TRUE,
  "PORTFOLIO_NAME | TICKER | SHARES | AVG_COST_USD | SECTOR | PYRAMID_TIERS_TAKEN",
  ARRAYFORMULA(
    IF(Holdings!B2:B="", "",
       Holdings!A2:A & " | " & Holdings!B2:B & " | " & Holdings!C2:C & " | " &
       Holdings!D2:D & " | " & Holdings!I2:I & " | " & Holdings!K2:K)
  )
)
```

The investor:
1. Opens this tab on phone or desktop.
2. Selects cell B2.
3. Copies (mobile: tap-and-hold, copy).
4. Pastes into the Claude prompt's `$ARGUMENTS` slot.

Single copy-paste action — the design constraint of §6.5 is satisfied.

##### Template creation — deliverable

Two artifacts:

1. **A Google Sheets template URL** that anyone can copy via
   `File > Make a copy`. The implementing agent creates the template in a
   shareable Google account, sets sharing to "anyone with the link can
   view" (not edit), and records the URL.

2. **`prompts/google_sheets_setup.md`** — written instructions for an
   investor who wants to recreate the template manually rather than
   copying. Step-by-step formula list per tab, in the order above.

##### GOOGLEFINANCE caveats to document

The README must explicitly state:
- `GOOGLEFINANCE` refreshes ~every 20 minutes; it is not real-time. For a
  2–3×/week review cadence, this is acceptable.
- It occasionally returns `#N/A` or stale data for newly-listed tickers,
  ETFs with low volume, or after market hours. The Holdings sheet uses
  `IFERROR(...)` to degrade gracefully.
- It does not work for OTC tickers or some foreign listings (workaround:
  use the US-listed ADR symbol where available).
- For pyramid-tier accuracy during outages, the investor can override Live
  Price by manually typing a value in column E — the formula is recomputed
  on next refresh.

##### Manual update workflow

Documented in the README:

| Event | Investor action |
|---|---|
| Buy more shares | Append row to Trade Log; recompute weighted Avg Cost on Holdings tab; update Shares |
| Sell shares (pyramid trim) | Append row to Trade Log; reduce Shares on Holdings tab; **increment Pyramid Tiers Taken (col K)** |
| Sell entire position | Delete row from Holdings tab; row remains in Trade Log for history |
| Add new ticker | Append row to Holdings tab with full data |
| Switch portfolio assignment | Edit Portfolio column on Holdings tab |

Pyramid Tiers Taken (column K) is the most-error-prone field — emphasize in
the README that this **must** be incremented when a pyramid-out trim is
executed, otherwise the prompt will keep recommending the same trim
repeatedly.

##### Acceptance criteria

1. The Google Sheets template URL produces a fully-functional copy with all
   5 tabs in the specified order.
2. Populating the Holdings tab with 5 sample positions causes:
   - Live Price to populate via GOOGLEFINANCE within ~30 seconds.
   - Concentration tab to update with correct sector/cluster percentages.
   - Pyramid Tracker tab to flag any due tiers.
   - Claude Input Export tab to produce a valid pipe-delimited string ready
     for the prompt.
3. The Claude Input Export string, copied and pasted into the
   portfolio-review prompt, produces a valid analysis on first run
   (validates the contract between TO-DO 3 and TO-DO 4).
4. `prompts/google_sheets_setup.md` describes the template completely
   enough that an investor without access to the original URL can rebuild
   it from scratch in under 30 minutes.
5. No paid Google Workspace features are required — must work on a free
   Google account.

##### What NOT to build

- **No two-way Sheets ↔ pipeline integration via Google API.** The
  investor's workflow is copy-paste; programmatic Sheets access adds OAuth
  complexity for negligible benefit at this scale.
- **No automated trade execution.** Trade Log is a manual ledger.
- **No backfill from existing positions.** Investor populates the template
  once, manually, with current holdings.

### 8.4 Functional gaps still actionable independent of rel-5 data

These items do not depend on the rel-5 data revamp; they can be picked up
opportunistically whenever there is budget.

- **Watchlist Decision strip endpoint** (`GET /synthesis/watchlist`) — a
  single-page grid of every watchlist ticker's verdict + margin. Useful
  when reviewing 20+ tickers on the phone.
- **ETF-tripwire monitoring background job** — would compare the latest
  ETF close to each ticker's tripwire condition on every run and push a
  notification when any fire. Today the user must read the synthesis report
  and check ETF prices manually.
- **Re-run scheduling** — cron / systemd-timer that fires
  `--mode synthesis-report` on the watchlist after each FOMC meeting / CPI
  release / earnings event. Today the user must manually trigger refresh
  via CLI or the `/refresh` endpoint.

### 8.5 Engineering / robustness

- **AsyncJobRunner is in-memory.** A FastAPI process restart loses
  in-flight synthesis/backtest/scorecard jobs. The phone polling logic
  handles a `404` gracefully but the work is silently dropped. Persisting
  job state (SQLite, or even a JSON sidecar) would let restarts resume
  safely.
- **No automated regression of the composite ranker.** A "for each ticker,
  snapshot today's composite + its 4 components" test would catch
  accidental drift when a threshold or weight is tweaked.
- **No request-rate guard on the FastAPI surface.** Single-user is the
  design assumption, but a misconfigured PWA shortcut could repeatedly POST
  `/infer` and drain news-API quotas before noticing. A per-endpoint
  debounce or per-day call cap would be cheap insurance — and becomes more
  important after rel-5 consolidates onto one paid provider whose quota
  matters more.
- **No CI runs the rel-4 test suite.** The 65 unit tests pass locally —
  pipe them through GitHub Actions (or pre-commit) so they actually run on
  every change.

### 8.6 Synthesis layer roadmap — rel-5 evolution notes (reminder only)

> **Status framing.** This sub-section preserves the original 3-phase design
> intent for the cycle-aware synthesis layer, lifted from the soon-to-be-
> deleted `rel4_infer_remote_design.md`. The bulk of it was actually shipped
> in rel-4 — see §2.8 (synthesis layer) and §3.2 (synthesis API endpoints).
> The content below is kept here as a **reference for future Release-5
> evolution** — items not yet wired stay open, items already shipped are
> tagged ✅ so a future reader can tell what's new work versus what's
> historical record.

#### 8.6.1 Why a synthesis layer

The deterministic Buffett pipeline already produces moat, quality, DCF,
safety margin, technicals, and entry signal. The synthesis layer adds the
analytical capabilities the master prompt mandates and the deterministic
pipeline cannot infer from filings alone:

| synthesis capability missing in the pipeline | Added by | Status |
|---|---|---|
| Industry archetype classification | `synthesis/archetype_classifier.py` | ✅ |
| Cycle positioning (trough → peak) | `synthesis/cycle_position.py` | ✅ |
| Supply-side competitor capacity table | `synthesis/supply_side.py` | ✅ |
| ETF-based bear-case tripwires | `synthesis/etf_tripwire.py` | ✅ |
| Method-weighted Valuation Reconciliation | `synthesis/valuation_reconciler.py` | ✅ |
| Sensitivity table on master driver | `synthesis/sensitivity.py` | ✅ |
| Full 14-section synthesis markdown report | `synthesis/report_writer.py` | ✅ |
| Web search for supply / cycle / ETF facts | `etl/web_search_provider.py` (Claude native tool) | ✅ |

#### 8.6.2 Phase 1 — Pure-Python additions (no LLM cost) ✅

Shipped. New files: `pipeline/buffett/synthesis/__init__.py`,
`valuation_reconciler.py`, `sensitivity.py`. Modified:
`pipeline/buffett/report/company_report.py` (adds Section 0 Decision Box,
Section 5b Valuation Reconciliation, Section 5c Sensitivity to the
existing `<TICKER>_report.md`). `config/settings.yaml` gained
`synthesis:` and `web_search:` blocks.

`ValuationReconciler.reconcile()` combines 5 valuation methods (mid-cycle,
reverse DCF, peer multiples, standard DCF, Graham) with per-archetype
weights into a single weighted fair value, then derives a verdict:

```
margin ≥ +20%                → BUY
margin between -10% and +20% → HOLD
margin ≤ -10%                → SELL
```

Missing methods (e.g. `mid_cycle = None` in Phase 1) are skipped and
their weight is redistributed proportionally so the total always sums to
1.0. An explicit `override_verdict` is only honoured when
`override_justification` is also supplied — enforcing the master prompt's
"Rule 8" discipline.

`SensitivityAnalyzer.analyze()` builds a 5-row table varying the
per-archetype master driver (e.g. "Industry pricing / contract ASPs" for
cyclicals) across `[+30%, +10%, 0%, -15%, -35%]` deltas. EPS moves linearly
with the driver via a caller-supplied `passthrough_multiplier` (1.2× for
compounders, 1.5× for cyclicals — the operating-leverage assumption). The
result embeds a fixed-template `layman_lead_sentence` above the table.

Cost: zero. Latency: <100ms per ticker.

**Smoke-test results (2026-05-11)**:
- SNDK @ $1,542.87 with cyclical inputs → weighted FV $295.80, margin
  −80.8%, verdict SELL.
- KO @ $70 with compounder inputs → weighted FV $80, margin +14.3%,
  verdict HOLD.

#### 8.6.3 Phase 2 — LLM synthesis layer (Sonnet 4.6 + native web search) ✅

Shipped. New files:
- `pipeline/buffett/etl/web_search_provider.py` — thin wrapper around
  Claude's built-in `web_search_20250305` tool. 24h disk cache keyed on
  SHA-256 of `(query|instruction|schema)`.
- `pipeline/buffett/synthesis/archetype_classifier.py` — one cheap LLM
  call; result cached 90 days under
  `reports/llm_reports/<TICKER>_archetype.json`. Falls back to a sector-
  string heuristic if the LLM is unreachable.
- `pipeline/buffett/synthesis/cycle_position.py` — web-search-augmented
  LLM call. Returns `cycle_phase`, evidence bullets, mid-cycle EPS
  estimate, and a recommended normal multiple. Cyclicals only;
  non-cyclicals skip.
- `pipeline/buffett/synthesis/supply_side.py` — web-search-augmented LLM
  call. Returns a plain-language competitor capacity table with a 1-line
  interpretation per row + a net supply/demand classification
  (`supply_growing_faster | in_line | demand_growing_faster`). Cyclicals
  only.
- `pipeline/buffett/synthesis/etf_tripwire.py` — web-search-augmented LLM
  call. Returns 1–2 proxy ETFs with stock weight and an *observable*
  tripwire condition (SMA crossings, drawdowns, RSI) phrased as
  `"If [ETF] [condition] → [action]"`.
- `pipeline/buffett/synthesis/report_writer.py` — orchestrator. Runs all
  data-layer + synthesis-layer steps, then makes ONE Sonnet 4.6 narrative
  call via tool-use to produce verdict + conviction + top-3 ranked
  pros/cons + differential view + thesis tripwires + entry zone +
  stop-loss + 3 targets + position size. Composes the final 14-section
  markdown.

Modified: `pipeline/buffett/buffett_pipeline.py` (adds
`_run_synthesis_report()` and public `run_synthesis_report_one()`),
`pipeline/main_buffett.py` (adds `synthesis-report` to `--mode` choices
plus summary printer).

**Web-search provider usage** (preserved as a code reference for future
extension):

```python
ws = WebSearchProvider(config)
result = ws.search_and_extract(
    query="What new NAND capacity is coming online in 2026-2027?",
    instruction="Return a supply-side table...",
    schema=SUPPLY_SCHEMA,
    tool_name="supply_side_analysis",
)
# result.structured = {"competitor_rows": [...], "net_read": "...", ...}
# result.citations  = [{"url": ..., "title": ..., "cited_text": ...}, ...]
```

The provider always succeeds — on any failure (no API key, network error,
LLM exception) it returns `WebSearchResult(error="...")` so the synthesis
pipeline can degrade gracefully (the section is marked unavailable rather
than aborting the whole report).

**Per-archetype valuation weighting** (config-driven, defaults in
`config/settings.yaml`):

| Method | cyclical | compounder | secular_growth | utility | financial | biotech |
|---|---|---|---|---|---|---|
| mid_cycle | **35%** | 15% | 15% | 20% | 20% | 5% |
| reverse_dcf | 25% | 20% | **30%** | 10% | 15% | **40%** |
| peer_multiples | 20% | 25% | 20% | 25% | **30%** | 20% |
| standard_dcf | 15% | **35%** | **30%** | **40%** | 25% | 30% |
| graham | 5% | 5% | 5% | 5% | 10% | 5% |

**Narrative LLM contract**: one structured tool call returning all
narrative fields (`verdict`, `conviction`, `top_3_pros`, `top_3_cons`,
`differential_view`, `thesis_tripwires`, `entry_zone_low/high`,
`stop_loss`, `target_{bull,base,bear}`, `position_size_pct`). The schema
enforces shape (e.g. exactly 3 pros and 3 cons), preventing free-form
drift.

**Cost per synthesis report** (Sonnet 4.6, 3–4 web searches typical):

| Component | Tokens / searches | Approx cost |
|---|---|---|
| Archetype classifier | ~600 in + 50 out, 0 search | $0.0019 |
| Cycle position | ~4K in + 1K out, 2 searches | $0.027 + $0.020 = $0.047 |
| Supply side | ~4K in + 1.2K out, 2–3 searches | $0.030 + $0.030 = $0.060 |
| ETF tripwires | ~3K in + 800 out, 1–2 searches | $0.021 + $0.020 = $0.041 |
| Narrative composition | ~5K in + 1.5K out, 0 search | $0.038 |
| **Total per full report** | | **~$0.19 + search ~$0.07 ≈ $0.25** |

Repeat runs within 24h hit the WebSearchProvider cache and the
report_writer cache, cutting cost to roughly the narrative call (~$0.04).

**Outputs**:
- `reports/llm_reports/<TICKER>_report.md` — full 14-section markdown
- `reports/llm_reports/<TICKER>_synthesis.json` — structured cache
- `reports/llm_reports/<TICKER>_archetype.json` — archetype (90-day cache)
- `data/buffett/web_search_cache/<sha256>.json` — web search results (24h)

#### 8.6.4 Phase 3 — Phone API + async job + mobile Decision Page ✅

Shipped. New files:
- `pipeline/api/async_jobs.py` — `AsyncJobRunner` in-memory async job dict
  with TTL eviction. Single-user; jobs >1h old evicted by a background
  sweeper.
- `pipeline/api/synthesis_renderer.py` — three mobile views:
  - `render_decision_html(synthesis)` — Decision Page card
  - `render_full_html(markdown, ticker)` — full markdown rendered as HTML
  - `render_pending_page(ticker)` — "no synthesis report yet — generate
    one?" page with built-in JS to POST `/refresh` and poll `/jobs/{id}`.

Modified: `pipeline/api/app.py` — adds six new endpoints under
`/synthesis/...`, wires `AsyncJobRunner`, starts the sweeper task at
app boot. Full endpoint map already in §3.2.

**Phone request flow**:

```
1. User opens PWA shortcut → /synthesis/SNDK/decision
   - If cache exists → Decision Page renders instantly (< 200ms)
   - If no cache → render_pending_page with "Generate" button

2. User taps "↻ Refresh"
   → POST /synthesis/SNDK/refresh
   → {job_id: "a1b2c3...", status: "queued"}

3. JavaScript polls GET /synthesis/jobs/{job_id} every 3s
   - "queued" → "running" → "completed" (60-120s typical)
   - On completion → window.location.reload() → Decision Page renders fresh

4. User taps "📄 Full report" → /synthesis/SNDK/full
   → Full 14-section markdown rendered as mobile-readable HTML
```

Concurrency: Decision Page and Full report endpoints are pure cache reads
(milliseconds, never block). Only `/refresh` triggers a long-running job,
and that job runs in `run_in_executor` (same pattern as the existing infer
mode). The single FastAPI worker stays responsive.

#### 8.6.5 Mobile Decision Page layout — visual spec ✅

Designed for a 375px-wide Samsung Galaxy screen, deliberately fits on one
scroll:

```
┌─────────────────────────────────────┐
│  📊 Synthesis Decision · SNDK              │   ← topbar
│                                     │
│  ┌───────────────────────────────┐  │
│  │  SNDK                $1,542.87 │ │   ← header
│  │  Archetype: cyclical_commodity │ │
│  │  Cycle: late · 2026-05-11      │ │
│  │                                │ │
│  │   ╔════════════════╗           │ │
│  │   ║  S E L L       ║  med-high │ │   ← verdict badge
│  │   ╚════════════════╝  conv     │ │
│  │  Weighted FV decoupled from    │ │   ← one-liner
│  │  price; cycle-aware FV ~$300   │ │
│  │                                │ │
│  │  Weighted FV         $295.80   │ │   ← FV block
│  │  Margin vs price     -80.8%    │ │
│  │  Stop-loss           $880.00   │ │
│  │  Entry zone   $700.00 – $850.00│ │
│  │  Bull/Base/Bear $1,800/900/400 │ │
│  │                                │ │
│  │  TOP 3 PROS                    │ │   ← green
│  │  1. NAND in genuine shortage…  │ │
│  │  2. FQ3 beat (rev +97% QoQ)…   │ │
│  │  3. Industry capex restrained… │ │
│  │                                │ │
│  │  TOP 3 CONS                    │ │   ← red
│  │  1. Forward P/E 17x on peak…   │ │
│  │  2. Stock +2,500% in 12mo…     │ │
│  │  3. Premium to all NAND peers… │ │
│  │                                │ │
│  │  DIFFERENTIAL VIEW             │ │   ← yellow border
│  │  More bearish than consensus   │ │
│  │  on multiple durability…       │ │
│  │                                │ │
│  │  THESIS BREAKS IF              │ │
│  │  • NAND ASP +30% QoQ FY27 +    │ │
│  │    GM >70% for 4+ quarters     │ │
│  │                                │ │
│  │  BEAR-CASE TRIPWIRES (ETF)     │ │
│  │  DRAM · Roundhill Memory ETF   │ │
│  │  If DRAM < 50d SMA for 5       │ │
│  │  sess AND >25% from ATH →      │ │
│  │  trim hard.                    │ │
│  │  SMH · VanEck Semiconductor    │ │
│  │  If SMH < 200d SMA AND…        │ │
│  │                                │ │
│  │  [📄 Full report] [↻ Refresh]  │ │   ← actions
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

Verdict colours: `BUY` green `#16a34a`, `HOLD` blue `#0ea5e9`,
`SELL` red `#dc2626`.

#### 8.6.6 Cost & latency summary (one-line table — already in §2.12.4)

Cross-referenced for completeness; canonical version lives in §2.12.4:

| Operation | Cost | Latency |
|---|---|---|
| `--mode report` (Phase 1 additions) | $0 | +100ms vs original |
| `--mode synthesis-report` (full Phase 2 run) | ~$0.25 | 60–120s |
| `--mode synthesis-report` (24h cache hit) | $0 | <500ms |
| `GET /synthesis/<T>/decision` (cache hit) | $0 | <200ms |
| `GET /synthesis/<T>/full` (cache hit) | $0 | <500ms |
| `POST /synthesis/<T>/refresh` then completion | ~$0.25 | 60–120s (async; UI polls) |

Daily watchlist of 20 tickers regenerated weekly ≈ 20 × $0.25 = **$5/week**.
Cache hits dominate when re-checking during the day.

#### 8.6.7 Open follow-ups (not implemented in rel-4)

Items below were called out in the original Part 7 §7.8 as "open follow-ups
the rel-4 ship did not cover." Three of the four are already mirrored in
§8.4; only the first item is truly new to this sub-section:

- **Per-ticker mid-cycle EPS overrides in `dcf_assumptions.yaml`.** Phase 2
  populates mid-cycle EPS from the cycle estimator; a config override would
  let the user pin a specific value when they disagree with the LLM.
  *(Net-new — not listed elsewhere.)*
- **"Watchlist Decision strip" endpoint (`GET /synthesis/watchlist`)** —
  single page listing every watchlist ticker's verdict + margin in a
  compact grid. *(See §8.4.)*
- **ETF-tripwire monitoring background job** — compares the latest ETF
  close to each tripwire condition on every run and pushes a notification
  if any fire. *(See §8.4.)*
- **Re-run scheduling** — cron / systemd-timer that fires
  `--mode synthesis-report` on the watchlist after each FOMC meeting / CPI
  release / earnings event. *(See §8.4.)*
