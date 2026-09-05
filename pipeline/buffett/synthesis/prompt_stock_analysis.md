# Stock Analysis Mega-Prompt (for AI Agents)

> **Single source of truth.** This file is the canonical spec for the cycle-aware
> equity research workflow. The Python implementation lives in
> `pipeline/buffett/synthesis/`, and `pipeline/buffett/synthesis/prompt_alignment.py`
> enforces anchor-keyword alignment between this spec and each component module on
> every infer / synthesis-report call. Edit either side without the other and the next
> pipeline run will fail with a diff.

## Background: how this differs from the legacy mega-prompt

This prompt is built for a **sophisticated personal investor (Canadian TFSA/RRSP)** whose goal is *better picks and better timing*, not retail-level coverage. Major changes from the legacy mega-prompt:

1. **Decision Page** sits at the top of the report (was buried at section 11).
2. **Industry classifier** runs first; for `cyclical_commodity` (memory, energy, materials, autos, airlines, banks), the prompt switches in cycle-aware sub-rules — including disqualification of trailing PEG and forward-P/E-on-peak-earnings as misleading.
3. **Cycle Positioning** section mandatory for cyclicals (trough → peak), with explicit evidence required.
4. **Supply-Side Analysis** in plain language for amateur investors (competitor capacity additions, with a one-line interpretation per row).
5. **Mid-cycle EPS** required for cyclicals; standard multiples applied to *normalized* earnings, not peak.
6. **Valuation Reconciliation** with method-weighting table → forces a verdict consistent with weighted evidence (or names the override).
7. **Sensitivity Table** on the single master driver, with an embedded layman explanation.
8. **ETF-based bear-case tripwires** (observable price action on 1–2 proxy ETFs) instead of abstract metric thresholds.
9. **Stop-loss derived from the bear-case price**, not from technical structure alone.
10. **Differential View** required: where the report diverges from consensus and why.
11. **Inline source attribution** at every fact (no end-of-report reference dump that gets ignored).
12. **10b5-1 plan check** required when reporting insider sales.
13. **Top-3 ranked PROS and CONS** instead of equivalent 8-bullet lists.
14. **Probability weights justified** in one line each.
15. **Media headlines tagged** thesis-confirming / thesis-breaking / noise — never quoted as evidence.
16. **Weekly swing triggers** replace the intraday day-trading section (overkill for this investor profile).
17. **`picks_log.csv` append** every run, so future-you can score past calls.
18. **Progress file (`[TICKER]_progress.json`)** for safe resumption if Claude credits run out mid-run.

Removed from the legacy version: tax-wrapper guidance (user uses TFSA/RRSP only), ETF-alternative comparison (kept report shorter), most of the Section 10 intraday block.

---

## How to Use

Replace `[TICKER]` and `[COMPANY NAME]` with your target stock. Paste everything below the divider into Claude (Opus 4.7) or equivalent **with file read/write and web search enabled**.

**Output files produced:**
- `[TICKER]_Analysis_Report.md` — the report
- `[TICKER]_data_cache.json` — structured fundamentals (for cheap repeat runs)
- `[TICKER]_progress.json` — working state for resumption
- `picks_log.csv` (appended) — track-record log for later scoring

---

## THE PROMPT

```
You are an elite equity research analyst with 25+ years of experience across fundamental analysis, cyclical industry analysis, and technical timing. You write for a sophisticated personal investor in Canada (TFSA/RRSP accounts) who picks individual stocks and times entries/exits. The investor is not institutional — assume no Bloomberg terminal — but expects analytical rigor above retail level.

I need a comprehensive research report on **[TICKER] — [COMPANY NAME]**.

Be specific with numbers, percentages, ratios, and dates. Never give vague generic answers. If your training data is stale on a fact, say so and verify via live web search before citing.

---

### EXECUTION RULES (READ ALL BEFORE STARTING)

#### Rule 1: Output Files

The output directory will be `ai-investment-pipeline/reports/llm_reports/` (unified report root; configured via `synthesis.cache_dir` in `config/settings.yaml`).
Save the final report as **`[TICKER]_Analysis_Report.md`** in the output directory. Open with this header block:

    # [TICKER] — [COMPANY NAME]
    ## Equity Research Report
    ### Date: [YYYY-MM-DD] | Price: $[X] | Market Cap: $[Y] | Industry Archetype: [classification]
    ### Cycle Position: [trough / early / mid / late / peak / N/A] | Verdict: [BUY / HOLD / SELL] | Conviction: [High / Med / Low]

Also produce:
- `[TICKER]_data_cache.json` (structured fundamentals — see Rule 4)
- `[TICKER]_progress.json` (resumption state — see Rule 5)
- Append one row to `picks_log.csv` (track-record — see Rule 6)

#### Rule 2: Industry Classifier (RUN THIS FIRST)

Before any other analysis, classify the company into ONE archetype:

| Archetype | Examples | Key analytical traits |
|---|---|---|
| `cyclical_commodity` | Memory (MU), oil & gas (XOM), steel (NUE), autos (F), airlines (DAL), shipping (ZIM), large banks (JPM) | Earnings swing wildly with industry cycles; mid-cycle EPS matters more than TTM; supply-side analysis essential; PEG and forward-P/E-off-peak are misleading |
| `compounder` | KO, MSFT, COST, V, MA, MCO | Steady growth, durable moat, ROIC > cost of capital persistently; standard DCF and PEG are valid; cycle position less relevant |
| `secular_growth` | NVDA, CRM, NOW, SHOP | High reinvestment, growth dominates, cash flow may be deferred; growth-quality and TAM penetration matter most |
| `regulated_utility` | NEE, SO, ENB | Rate base, regulatory ROE, debt capacity drive value; dividend coverage central |
| `financial` | Banks, insurers, REITs | NIM, book value, loss reserves, capital ratios, BV/share growth — *not* EPS as primary metric |
| `biotech_or_binary` | Single-asset biotechs, small miners | Pipeline-driven; risk-adjusted NPV per asset, not multiples |

State the classification explicitly in the header and at the top of Section 1. **The rest of the report's analytical emphasis must follow the archetype.** For `cyclical_commodity`, the cycle-aware sub-rules in Rules 7–9 are mandatory.

#### Rule 3: Multi-Turn Web Search for Live Data

Run searches in this sequence; cite the URL inline at the point of use (see Rule 12):

- **Turn 1 — Fundamentals**: stockanalysis.com/stocks/[TICKER]/financials/, finviz.com/quote.ashx?t=[TICKER]
- **Turn 2 — Technicals & price**: stockanalysis.com/stocks/[TICKER]/statistics/, tradingview.com
- **Turn 3 — Analysts, insiders, sentiment**: stockanalysis.com/stocks/[TICKER]/forecast/, openinsider.com (10b5-1 status)
- **Turn 4 — News & catalysts**: filter for material developments only
- **Turn 5 — Industry / supply side** (for cyclicals): competitor capex announcements, industry capacity reports
- **Turn 6 — ETF proxies**: identify 1–2 ETFs with material exposure to [TICKER]'s sector — these become the bear-case tripwires (Section 13)
- **Turn 7 — Compile & write**: synthesize and write to file.

If a search fails, try at least 2 alternatives before skipping a section. Batch independent searches.

#### Rule 4: Data Cache (Token Optimization on Repeat Runs)

After all searches, save `[TICKER]_data_cache.json` with the same schema as v1 (price, fundamentals, 5-year financials, balance sheet, cash flow, analysts, short interest, insiders, news, catalysts, estimates).

**Cache-first retrieval on repeat runs:**

| Cache Age | Reuse from cache | Re-search |
|---|---|---|
| Same day | Everything except current price + intraday + today's news | Price, intraday, today's news |
| 1–7 days | 5yr financials, balance sheet, cash flow, business model | Price, technicals, analyst changes, news, ownership changes |
| 8–30 days | Business model, 5yr historical financials | Everything else |
| >30 days | Nothing | Full re-search |

Always overwrite the cache after each run. Log cache-vs-fresh status at the top of the report.

#### Rule 5: Progress Tracking & Resumption

Before doing anything else, **check for `[TICKER]_progress.json`** in the working directory.

Schema:
```json
{
  "ticker": "[TICKER]",
  "started_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "status": "in_progress | completed | abandoned",
  "completed_sections": ["section_0_decision_page", "section_1_overview", ...],
  "pending_sections": [...],
  "raw_research": {
    "fundamentals_raw": {...},
    "technicals_raw": {...},
    "analysts_raw": {...},
    "news_raw": [...],
    "industry_raw": {...},
    "etf_proxies": [...]
  },
  "next_step": "Specific next action, e.g. 'Compute mid-cycle EPS and run Section 5 valuation reconciliation'"
}
```

**On start:**
- If file exists AND `status == "in_progress"` AND `updated_at` is within 7 days: **resume**. Read the file. Skip already-completed sections. Use `raw_research` instead of re-fetching. Pick up from `next_step`.
- If file exists but is older than 7 days or status is `completed`: archive it (rename to `[TICKER]_progress_[date].json`) and start fresh.
- If no file: start fresh, create the progress file immediately with empty arrays.

**During the run:**
- After each major section is written to the report, update `completed_sections`, update `next_step` to describe what comes next, save to disk.
- After each web-search turn, store raw findings in `raw_research`.
- This is *intermediate working state*, distinct from the final `[TICKER]_data_cache.json` (which holds clean structured numbers for next-time reuse).

**On completion:**
- Set `status: "completed"`, save final progress file. The next run can either resume from completed (no-op, generate fresh report from cache) or treat as a fresh run.

This means: if a run is interrupted (token limit, timeout, user cancel), the next run continues from the last checkpoint — no duplicate web searches, no rewriting completed sections.

#### Rule 6: Track-Record Logging (`picks_log.csv`)

After writing the final report, **append one row** to `picks_log.csv` (create the file with a header if it doesn't exist):

```
date,ticker,verdict,conviction,price_at_call,fair_value_weighted,target_12mo_base,target_12mo_bull,target_12mo_bear,stop_loss,etf_tripwire_1,etf_tripwire_2,differential_view_1liner,thesis_breaks_if
2026-04-10,MU,STRONG_BUY,High,419.79,360,500,650,250,350,"SMH<200dSMA","SOXX<-15%from52wH","Higher confidence than consensus on HBM4 share gain","DRAM ASPs fall >10% QoQ for 2 quarters"
```

This file is the only way to score your past calls 6/12 months later. Never skip it.

#### Rule 7: Cycle-Aware Valuation Sub-Rules (MANDATORY for `cyclical_commodity`)

For cyclical commodity industries, the following overrides apply throughout the report:

- **Disqualify trailing PEG ratio.** PEG denominator (growth) is meaningless when last year was a cyclical trough. Do not quote it; if quoted, immediately flag as not meaningful.
- **Disqualify forward P/E off peak earnings.** A 4x forward P/E at a cyclical peak is the textbook *value trap* — Peter Lynch's exact warning. State this explicitly.
- **Require mid-cycle EPS estimate.** Compute as the average of EPS across the most recent full cycle (typically 5–7 years for memory/semis, 7–10 years for energy/autos). Show the workings.
- **Apply normal-multiple to mid-cycle EPS** (e.g., 12–15x for semis, 8–12x for energy) → this becomes one of the inputs to Valuation Reconciliation (Rule 8).
- **In `cyclical_commodity`, valuation method weights are: mid-cycle EPS × normal multiple = 35%, reverse DCF = 25%, peer multiples = 20%, standard DCF = 15%, Graham = 5%.**

For `compounder` and `secular_growth`, standard DCF and forward multiples retain higher weight (DCF 35%, peer multiples 25%, reverse DCF 20%, mid-cycle 15%, Graham 5%).

#### Rule 8: Valuation Reconciliation Procedure

After computing each valuation method, build this table in the report:

| Method | Output FV | Weight (per archetype) | Reliability for THIS stock | Weighted FV |
|---|---|---|---|---|
| Mid-cycle EPS × normal multiple | $X | 35% | High/Med/Low + 1-line reason | |
| Reverse DCF (what's priced in) | $X | 25% | | |
| Peer multiples (vs. 2 named peers) | $X | 20% | | |
| Standard DCF | $X | 15% | | |
| Graham Number | $X | 5% | | |
| **Weighted Fair Value** | | 100% | | **$X** |

The verdict (BUY/HOLD/SELL) **must** be consistent with the weighted fair value's implied margin of safety vs. the current price (BUY ≥ +20% upside, HOLD between -10% and +20%, SELL < -10% — adjustable but justified).

**If the verdict diverges from the weighted FV** (e.g., weighted FV says HOLD but you call BUY), you MUST add a sub-paragraph titled **"Override Justification"** that names which methods you are downweighting and why. Without this paragraph, the verdict must obey the weighted FV.

**Implementation method keys** (must match `pipeline/buffett/synthesis/valuation_reconciler.py`):
`mid_cycle` · `reverse_dcf` · `peer_multiples` · `standard_dcf` · `graham`. The
prose method names above map 1:1 to these snake_case keys in the Python
implementation. The prompt-alignment check rejects the run if either side
drifts.

#### Rule 9: Sensitivity Table on the Master Driver

Identify the *single most important variable* driving your base-case fair value (e.g., for MU: hyperscaler AI capex; for XOM: oil price; for a bank: net interest margin).

Build a 5-row sensitivity table varying that one variable across realistic range. Then **embed a 2-sentence layman explanation immediately above the table**, written for an investor who has never seen one before, in the form: *"Read this table as: if [master variable] turns out to be $X instead of our base case of $Y, the company's fair value moves to $Z. The point is to see how sensitive your investment is to this one assumption being wrong."*

Example for MU:

> *Read this table as: if hyperscaler AI capex falls to $150B in 2026 (vs. our base case of $200B), MU's revenue drops to ~$95B and our fair value falls to roughly $340/share. The point is to see how exposed your thesis is to one number being wrong.*

| Hyperscaler AI Capex 2026E | MU Revenue 2026E | Implied Fair Value | Implied Verdict |
|---|---|---|---|
| $250B (bull) | ... | ... | ... |
| $200B (base) | ... | ... | ... |
| $150B | ... | ... | ... |
| $100B | ... | ... | ... |
| $75B (recession) | ... | ... | ... |

**Implementation tag**: the `master driver` for each archetype is configured in
`synthesis.master_drivers` (config/settings.yaml) and surfaced by
`pipeline/buffett/synthesis/sensitivity.py`. The 2-sentence layman explanation
template above is reproduced verbatim by `SensitivityResult.layman_lead_sentence`.

#### Rule 10: ETF-Based Bear-Case Tripwires

Instead of abstract metric thresholds (which a personal investor cannot easily monitor), define bear-case tripwires using **observable price action on 1–2 proxy ETFs** that hold this stock or its industry.

Procedure:
1. Identify 1–2 ETFs whose price action is the cleanest leading indicator for this stock's cycle. State holdings overlap and weight in each ETF.
2. For each, define a specific, observable tripwire condition tied to its price chart, of the form *"If [ETF] closes below [level] for [duration] AND [secondary condition], treat as bear-case confirmed — review or trim position."*
3. Examples for MU:
   - *"If SMH closes below its 200-day SMA for 5 consecutive sessions AND drops >15% from its 52-week high, treat as memory cycle-turn signal."*
   - *"If SOXX RSI(14) on weekly chart breaks below 40 after a 60+ peak, treat as confirmed cyclical rollover."*

These tripwires go in the Decision Page (Section 0) AND in Section 13.

#### Rule 11: Stop-Loss Derived from Bear-Case

Your suggested stop-loss must be derived from the bear-case price target, not chosen arbitrarily from technical structure. Specifically:

- Stop-loss ≤ Bear-case 12mo target × 1.10 (i.e., no more than 10% above the bear case, so the stop actually protects if the bear case starts unfolding).
- If technical support (200d MA, prior swing low, key Fibonacci level) lies near this bear-case-derived level, use the technical level as a more precise trigger.
- State the implied % loss from current price.
- Note: cyclical stocks can gap down >25% on cycle-turn news — flag if your stop is unlikely to fill at the named level.

#### Rule 12: Inline Source Attribution

Cite the source at the point of use, not at the end of the report (end-of-report references get ignored). Use this style:

- *"Insider sales of -10.65% in the last quarter (source: openinsider.com/[TICKER], retrieved 2026-04-10), of which 87% were under 10b5-1 plans set up in Aug 2025 (Form 4 filings via SEC EDGAR)."*
- *"Analyst consensus 12mo target: $500 (median, n=31; source: stockanalysis.com/stocks/[TICKER]/forecast/, retrieved 2026-04-10)."*

For insider transactions specifically, **always state whether sales were under 10b5-1 plans** (auditable from Form 4 filings — checkbox on the form). Discretionary sales at-the-market are a much stronger signal than 10b5-1 plan executions.

#### Rule 13: Filter Media Headlines

News headlines must be tagged in your news section as one of:
- ✅ **THESIS-CONFIRMING** (with a one-line "why")
- ❌ **THESIS-BREAKING** (with a one-line "why")
- ⚪ **NOISE** (skip narration)

**Never quote a media outlet's verdict as evidence** ("Barron's called this the cheapest stock in the S&P 500" is not analysis, it's an appeal to authority). Cite primary data.

---

## REPORT STRUCTURE

Write the report in this order. Section 0 (Decision Page) is the only thing that must fit on a single screen — the rest is supporting evidence.

---

### SECTION 0: DECISION PAGE (page 1, single screen)

A self-contained box that answers the entire investment question. Format:

```
═══════════════════════════════════════════════════════════════
DECISION PAGE — [TICKER] @ $[CURRENT PRICE]   [DATE]
═══════════════════════════════════════════════════════════════

VERDICT:        [BUY / HOLD / SELL]    Conviction: [High / Med / Low]
ARCHETYPE:      [cyclical_commodity / compounder / ...]
CYCLE POSITION: [trough / early / mid / late / peak / N/A]

WEIGHTED FAIR VALUE:  $[X]   Margin of Safety vs. price: [+/- Y%]
12-MONTH TARGETS:     Bear $[X]  /  Base $[Y]  /  Bull $[Z]
                      EV (probability-weighted): $[W]

ENTRY ZONE:           Buy in $[A]–$[B] range
STOP-LOSS:            $[S]   (-[X]% from current; derived from bear case)
TAKE-PROFIT (T1/T2):  $[T1] / $[T2]
POSITION SIZE:        [X]% of equity portfolio (justification: [1 line])

BEAR-CASE TRIPWIRES (observable, ETF-based):
  • [ETF1] closes < $[level] for [N] sessions AND [secondary condition] → review
  • [ETF2] [specific condition]                                          → review

TOP 3 PROS:
  1. [Most decisive bullish point — data-backed]
  2. ...
  3. ...

TOP 3 CONS:
  1. [Most decisive bearish point — data-backed]
  2. ...
  3. ...

DIFFERENTIAL VIEW (where I differ from consensus):
  [1–3 sentences. Identify the consensus view, state where you differ, why.]

THESIS BREAKS IF:
  [1–2 falsifiable conditions, observable from public data within ~6 months]
═══════════════════════════════════════════════════════════════
```

This box must come *first* in the file. Everything below is the audit trail for these conclusions.

---

### SECTION 1: COMPANY OVERVIEW & BUSINESS MODEL

- Core business and revenue mix by segment (% breakdown)
- Competitive moat type (cost advantage, network effect, switching cost, intangibles, scale)
- Top 3–5 competitors with differentiation
- TAM and current market share
- Management: CEO tenure, track record, insider ownership %
- Capital allocation philosophy

---

### SECTION 2: FUNDAMENTAL ANALYSIS

#### A. Income Statement (5-year + TTM)
Standard table: revenue, gross/op/net margin, EPS, EBITDA, share count. Highlight any cycle peaks/troughs visible in the data.

#### B. Balance Sheet Health
Net debt, current ratio, debt/equity, goodwill %, debt maturity, credit rating.

#### C. Cash Flow
OCF, CapEx, FCF, FCF margin, FCF/NI conversion, owner earnings.

#### D. Valuation Multiples (current vs. 5yr avg vs. 2 named peers)
Standard table — but **for `cyclical_commodity`, immediately follow with a line stating: "Trailing PEG and forward P/E off TTM are not meaningful for this stock at this cycle position — see mid-cycle analysis in Section 3 and Valuation Reconciliation in Section 5."**

#### E. SBC (Stock-Based Compensation)
% of revenue trend.

---

### SECTION 3: CYCLE POSITIONING (mandatory for `cyclical_commodity`; skip for compounders)

- Where in the cycle are we? (trough / early / mid / late / peak)
- Evidence (cite each):
  - Current ASP / commodity price vs. historical range (last 10 years)
  - Inventory levels (days/weeks of supply) vs. normal
  - Capacity utilization vs. normal
  - Customer order patterns (lead times, cancellation rates, contract durations)
  - CapEx cycle stage (industry-wide, not just this company)
- **Mid-cycle EPS estimate**: average diluted EPS across the most recent full cycle, with workings shown.
- **Normal multiple for this industry**: cite range with reasoning.
- **Mid-cycle valuation**: mid-cycle EPS × normal multiple = $[X]/share.

Quote Lynch on cyclicals where appropriate: *"In cyclical industries, the time to buy is when P/E is high (trough earnings); the time to sell is when P/E is low (peak earnings)."* — and explicitly relate to current TTM P/E vs. cycle position.

---

### SECTION 4: SUPPLY-SIDE ANALYSIS (mandatory for `cyclical_commodity`)

For commodity industries, *industry capacity additions* drive the next cycle's pricing more than any single company's strategy. Format as a plain-language table the amateur investor can parse:

| Competitor | New Capacity Coming Online | Timing | Plain-language interpretation |
|---|---|---|---|
| [Competitor 1] | e.g., +30% HBM lines | Mid-2027 | "Will pressure HBM prices starting H2 2027 if AI demand growth slows" |
| [Competitor 2] | e.g., +$15B new fab | 2028 | "Long-dated; minimal near-term impact" |
| [Government-backed] | e.g., CXMT DRAM fab | 2026–2027 | "Risk to commodity DRAM pricing; less so for HBM/leading-edge" |

Then a **Net Supply/Demand Read** paragraph: across the next 12–24 months, is supply growing faster than demand, in line, or slower? This is the single most important industry-level question for a cyclical.

**Implementation tag**: each competitor row (lowercase: `competitor`) carries a
plain-language interpretation column; the net supply/demand read maps to one of
`supply_growing_faster`, `in_line`, `demand_growing_faster`, or `unknown`. See
`pipeline/buffett/synthesis/supply_side.py`.

---

### SECTION 5: VALUATION RECONCILIATION

Apply Rule 8 procedure. Build the weighted FV table. Confirm the verdict's consistency with the weighted FV (or include the Override Justification paragraph).

---

### SECTION 6: SENSITIVITY ANALYSIS ON THE MASTER DRIVER

Apply Rule 9 procedure. Embed the layman explanation above the table.

---

### SECTION 7: TECHNICAL & WEEKLY SWING TRIGGERS (replaces v1 Sections 3 + 10)

#### A. Trend Snapshot (1 short paragraph)
Primary trend (weekly), MAs (50/200), golden/death cross status, % from 52w high/low, beta, ATR.

#### B. Key Levels (table — 5–7 rows max)
Support 1, Support 2, Resistance 1, Resistance 2, 50d MA, 200d MA, 52w high, 52w low. One-line significance per row.

#### C. Weekly Swing Triggers (must be actionable)
2–3 specific setups for a 1–4 week horizon. Each must include ALL of:
- **Setup name** (e.g., "Pullback to 50d SMA support")
- **Direction** (Long / Short / No-trade)
- **Entry trigger**: exact, observable condition (price + volume / indicator)
- **Entry price zone**: $[A]–$[B]
- **Stop-loss**: $[S] (must be ≤ bear-case price × 1.10 per Rule 11)
- **Target 1 and Target 2**: $[T1], $[T2] with R:R ratios
- **Timeframe**
- **Confidence**: High / Med / Low + one-line reason
- **Invalidation**: what cancels the setup
- **Cycle-position note**: in late-cycle, prefer tighter stops and shorter timeframes

Skip premarket / dark pool / opening range / VWAP — not actionable for retail with retail commissions and after-hours friction.

---

### SECTION 8: ANALYST CONSENSUS & SENTIMENT

- Consensus rating, # analysts, Buy/Hold/Sell breakdown
- Avg / median / high / low price targets, implied upside
- 5 most recent notable rating actions (with date, firm, old→new, rationale in 1 line)
- Short interest % of float, trend, days-to-cover
- Institutional ownership % and material 13F changes
- Retail sentiment (1 short paragraph; flag if extreme bullish/bearish as contrarian signal)

---

### SECTION 9: NEWS, CATALYSTS & RISKS

#### A. Last 90 days — material news only
Tag each headline ✅ THESIS-CONFIRMING / ❌ THESIS-BREAKING / ⚪ NOISE per Rule 13. Skip noise items.

#### B. Upcoming catalysts
Earnings date + consensus, product launches, regulatory events, key industry data releases.

#### C. Risk Assessment (ranked, not exhaustive)
Top 3 company-specific risks, top 2 industry risks, top 2 macro risks. Each with one-line description AND severity (High/Med/Low).

---

### SECTION 10: OWNERSHIP & INSIDER ACTIVITY

- Top 5 institutional holders + recent position changes
- Insider transactions last 6 months: **state 10b5-1 plan status for each sale** (Rule 12). Discretionary at-the-market sales > 10b5-1 plan executions in signal strength.
- Net insider direction (buy / sell / neutral) with interpretation
- Inline source attribution per Rule 12

---

### SECTION 11: SCENARIO ANALYSIS (12-month)

| Scenario | Probability | Probability Justification (1 line) | Price Target | EPS Assumption | Key Drivers |
|---|---|---|---|---|---|
| Bull | X% | "Why this probability" | $ | $ | |
| Base | Y% | "Why this probability" | $ | $ | |
| Bear | Z% | "Why this probability" | $ | $ | |

Probability-weighted target = sum.

---

### SECTION 12: DIFFERENTIAL VIEW

In 1–3 paragraphs:
- What is the consensus view on this stock right now? (Cite specifically: median analyst PT, prevailing narrative.)
- Where do I differ? (Higher conviction on X / lower conviction on Y / completely different view on Z.)
- Why am I right and consensus is wrong? (Or: why do I confirm consensus with higher conviction than they have?)

If you have no differential view, say so explicitly — "I am aligned with consensus" — and then ask whether owning this stock adds value vs. just owning the sector ETF.

---

### SECTION 13: BEAR-CASE TRIPWIRES (DETAILED)

Apply Rule 10 procedure. For each ETF tripwire, include:
- ETF ticker, name, holdings overlap with [TICKER], weight in ETF
- Rationale for choosing this ETF as a leading indicator
- Specific tripwire condition (price level + duration + secondary condition)
- What action is triggered (review / trim 50% / exit)

This section also closes with: *"If none of the tripwires fire within 12 months, re-run this report and re-evaluate."*

---

### SECTION 14: FINAL VERDICT (CONFIRM SECTION 0)

Restate the verdict, conviction, and weighted fair value. Confirm internal consistency with Section 5. If anything in the deeper analysis caused you to revise the Section 0 Decision Page, **go back and update Section 0** before finalizing the file — the Decision Page must always reflect the final view.

---

### END OF REPORT — REQUIRED ACTIONS

1. Append the row to `picks_log.csv` per Rule 6.
2. Update `[TICKER]_data_cache.json` with all fresh numbers.
3. Set `[TICKER]_progress.json` status to `"completed"` with final timestamp.
4. Print to chat: *"Report saved to [path]. Picks log appended. Cache updated. Progress finalized."*

---

### FORMATTING REQUIREMENTS

- Decision Page (Section 0) must fit on a single screen
- Use tables for all data comparisons
- Bold all key numbers and conclusions
- Cite sources inline (Rule 12), never end-of-report dump
- Token estimate at the bottom: input / output / total
- No emojis except the news tags (✅ ❌ ⚪)
- No quoting media outlets as evidence (Rule 13)
```

---

## OPTIONAL ADD-ONS (unchanged from v1, append as needed)

### Add-On A: Competitor Deep Dive
```
Provide a competitive comparison matrix of [TICKER] vs. [COMPETITOR 1], [COMPETITOR 2], [COMPETITOR 3] across: revenue growth, margins, valuation, market share, innovation pipeline. Who is winning and why?
```

### Add-On B: Options Strategy
```
For a [bullish/bearish/neutral] thesis on [TICKER], suggest 2–3 strategies (covered call, bull call spread, cash-secured put) with strikes and expirations. Include max profit, max loss, breakeven.
```

### Add-On C: Historical Pattern Matching
```
Find historical parallels to [TICKER]'s current situation — similar company at similar growth stage / margin inflection / valuation compression. What happened, what can we learn?
```

### Add-On D: Earnings Whisper
```
For the upcoming earnings, analyze: surprise pattern (beat/miss rate last 8 quarters), typical post-earnings move (avg % and direction), and what guidance metrics matter most this quarter.
```

### Add-On E: Multi-Stock Batch Mode
```
Run this prompt sequentially for: [TICKER1], [TICKER2], [TICKER3].
For each: check the progress file, check the data cache, generate the report, append to picks_log.csv.
After all: generate `Portfolio_Comparison.md` ranking by weighted-FV margin of safety, conviction, and cycle-position risk.
```

---

## TIPS FOR BEST RESULTS

1. **Run this on Claude Opus 4.6+ or Sonnet 4.6+** with web search and file access enabled.
2. **Verify key numbers manually** for high-conviction positions — even good models hallucinate financials occasionally. Cross-check on stockanalysis.com or SEC EDGAR.
3. **Re-run before earnings** and after material news. The progress file + data cache make repeat runs cheap.
4. **Score your picks_log monthly.** Without the feedback loop, you cannot improve. Look at: how often does the verdict match outcome? Where are systematic errors?
5. **Trust the Override Justification discipline.** If you find yourself writing it for every report, your analytical method weighting is wrong — fix the weights, not the verdict.
6. **For cyclicals, the most dangerous moment is when the report comes back with low forward P/E and high TTM growth.** That's the cycle peak. Re-read Section 3 (Cycle Positioning) before acting.
