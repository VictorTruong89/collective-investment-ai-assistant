# L1: Domain Specification — Feature Engineering (D-02)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-02 · **Seat:** SEAT-5
> **Path:** `src/feature_engineer/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Depends on:** [`L1-data-engine.md`](L1-data-engine.md) (D-07) · [`L2-shared-money.md`](L2-shared-money.md) (D-00)
> **Prior art:** `pipeline/ohlcv/dataset/feature_schema.py`, `pipeline/fundamental_analysis/features/**`,
> `pipeline/buffett/analysis/**`, `pipeline/core/fundamental_engine.py`,
> `constitution.md` INV-1/INV-2/INV-3/INV-4, `F0` §12 **D-16**/**D-17**/**D-19**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.7.0 | 2026-08-27 | Victor | ⚠⚠ **`fundamental` → v2 — FE-2 was violated by this spec's own author.** Group C took membership from **45 to 47** and the version stayed at 1, so two feature sets shared one identity. ★ FE-2 says *"changing any `formula_id`, range, or membership produces a NEW version"*, and **`content_hash` existed to make that mechanical** — D-04's manifest simply did not carry it (**MT-51**). AC-2.46. |
| 0.6.0 | 2026-08-27 | Victor | ★★ **Group C built — §5.3's 61 features are complete.** `f_graham_number_ratio`, `f_moat_quant_score` and a real `f_market_to_book`, all priced on **`adj_open(t)`** rather than the legacy's close-at-filing (FE-28/QA-71). New **FE-38**: a share count was divided by 100 with the money, making market cap **100× too small**. New **FE-39**: the inherited moat stability term spanned 0.95–0.99 — *a 20 % weight on a near-constant*. ⚠ All three are **anchors** (RA-151). AC-2.45. |
| 0.5.0 | 2026-08-27 | Victor | ★★ **`fundamental@v1` — §5.3's 45 `f_*` features built.** With `price_ohlcv@v1` that is **59 of the declared 61**. ★★ **The order is the design**: per-filing first, as-of join second — the reverse silently nulls every multi-period feature, because a 120-day panel window holds **three** filings. ⚠ The join is `direction="backward"` on **`filing_date`**: `nearest` attaches a filing published *after* the date, and keying on `period_end` is worth **a quarter of hindsight on every row**. New **FE-37** — *null-ness correlates with sector* (NVDA 37/45, WMT 32, JPM 18). AC-2.38…2.44. |
| 0.4.0 | 2026-08-27 | Victor | ★★ **`price_ohlcv@v1` — §5.3's 14 price features built, on the FE-28 open anchor.** D-02 published two features where the spec declared 61. ⚠ **Not a verbatim port:** the legacy reads `adj_close(T)` and `volume(T)` — **neither knowable at the day-T open** — and uses `+1e-9` where FE-14 wants null. **L5 D-16 closed**: `rsi_14` is now Wilder's, `formula_id = rsi.wilder.v1`. New **FE-34** (scale invariance — the inherited `macd_hist` printed 2007 beside 3.1 on one day), **FE-35** (EWM warm-up, measured), **FE-36** (volume lags to T−1). ★ **FE-5 was never enforced anywhere** — `RangeViolationError` and AC-2.5 both existed and no code path evaluated a range; `assert_ranges` now runs at emit. AC-2.31…2.37. |
| 1.6.1 | 2026-08-25 | Victor | ⚠ **§6.4 claimed D-02 publishes "sector and theme mappings" to D-05 — it publishes SECTOR.** For D-02 to label a position's *theme* it must know the taxonomy, and **FE-21 forbids D-02 importing an analytical domain**; meanwhile D-05 **RK-6** makes the taxonomy a declared artifact of its own. ★ Both could not hold. **D-05 RK-37** resolves it in D-05's favour — theme membership is *a judgement call about what counts*, and a judgement belongs on a seat, not on neutral ground. |
| 0.3.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit — three seam defects.** **`CT-2.3` gains `decision_anchor`**: QA-72 calls the anchor *"a declared property of the label set, recorded in the label contract"* and **this is that contract; it was absent** (FE-31). ★★ **FE-32 states the Money→ratio boundary nobody had described** — MO-4 read literally forbids `ret_1d`, and the resolution is that **a same-currency ratio is dimensionless and leaves the Money type**. **FE-33** maps `CT-2.1.inputs` names to `CT-7.1` columns — **the two contracts used different names for the same column and neither said so.** |
| 0.2.0 | 2026-08-18 | Victor | **§5Z — the day-T feature row is anchored on the open** (FE-28…FE-30), following D-08 §5A and D-03 §5.9. Records that the `open` column **has never been adjusted in anger** and that the current live-price splice **flattens OHLC to a single value**. |
| 0.1.0 | 2026-08-16 | Victor | Initial draft. Closes **`L4` Q-10** (§6 — which outputs go to which consumer). Records four inherited defects (§8) rather than absorbing them silently. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

D-02 answers one question, and it must answer it identically for every asker:

> **"Give me the computed number — the same number, by the same formula, whoever is asking and
> whenever they ask."**

The weight is on **the same number**. Any domain can compute a margin; only D-02 can guarantee that
the margin the thesis quotes, the margin the model trains on, and the margin the backtest replays
are **one definition with one implementation**. That guarantee is what makes constitution **INV-4
(train/inference parity)** checkable rather than aspirational, and it is why the **feature
contract** (§5) is a first-class artifact here rather than a list someone maintains.

D-02 exists because the alternative already happened. Today the same concept is computed twice, in
two places, by two formulas — `moat_score` and `f_moat_quant_score` (§8.3) — and nothing says so.

## 1.2 Position

```text
   D-01 Fundamental          D-03 Quant  ·  D-04 Models          D-05 Risk
    (SEAT-2, LLM)              (SEAT-3, ML)                       (SEAT-4)
          ▲                          ▲                                ▲
          │  valuation, quality      │  the FEATURE CONTRACT          │
          │  moat, ratios            │  + labels                      │
          └────────────┬─────────────┴────────────────────────────────┘
                       │
          ┌────────────┴─────────────┐
          │  D-02 FEATURE ENGINEER   │  SEAT-5   ← this spec
          │  deterministic compute   │
          │  ★ NEUTRAL GROUND        │
          └────────────┬─────────────┘
                       ▲
          ┌────────────┴─────────────┐
          │    D-07 Data Engine      │  SEAT-5
          │  as_of · adj_as_of ·     │
          │  calendar check (§6A)    │
          └──────────────────────────┘
```

**D-02 is the only domain permitted to define a derived number.** A ratio computed inside D-01,
D-03 or D-04 is a defect, not a shortcut — it is a second definition, and the second definition is
always the one nobody tests.

## 1.3 Boundary

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-02 COMPUTES. IT DOES NOT FETCH, AND IT DOES NOT JUDGE.        ║
║                                                                  ║
║  Upstream line (D-07 | D-02):                                    ║
║    D-07 does DEFINITIONAL derivation — gross_profit =            ║
║    revenue - cogs when the filer omits it.                       ║
║    D-02 does ANALYTICAL derivation — margins, growth, scores.    ║
║    The test is D-07's: if two reasonable analysts could          ║
║    disagree about the formula, it belongs HERE.                  ║
║                                                                  ║
║  Downstream line (D-02 | D-01, D-03, D-04):                      ║
║    D-02 produces a NUMBER and the arithmetic behind it.          ║
║    What the number MEANS is the consumer's.                      ║
║    "fair_value = 412.80" is D-02.                                ║
║    "trading 34% below fair value, therefore BUY" is D-01.        ║
║    "rank 3 of 130" is D-03/D-04.                                 ║
║                                                                  ║
║  NO LLM PARTICIPATES IN ANY COMPUTATION HERE (AP-5, ST-5).       ║
║  D-02 may consume a value an LLM produced upstream — but see     ║
║  §8.3, because that is exactly how INV-014 leaks.                ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **FeatureRow** | ticker × date | `(ticker, date, contract_version)` | the panel row a model consumes |
| **FeatureContract** | a named, versioned feature set | `(name, version)` | **the artifact INV-4 asserts against** — §5 |
| **FeatureSpec** | one feature | `(contract, feature_name)` | formula id, dtype, range, inputs, PIT class |
| **Label** | ticker × date × horizon | `(ticker, date, horizon, label_def)` | forward-looking **by construction** — §7.4 |
| **ValuationResult** | ticker × as_of | `(ticker, as_of, method)` | fair value + the full arithmetic trail |
| **QualityResult** | ticker × as_of | `(ticker, as_of)` | gate outcomes + the inputs to each |
| **MoatResult** | ticker × as_of | `(ticker, as_of)` | durability score + components |

Every monetary field is a **`Money`** (`L2-shared-money.md` CT-M.1). A fair value without a currency
is a defect, not a number (**INV-001**).

> **`FeatureContract` is the entity that justifies this domain.** Without it, "the feature set" is
> whatever a training run happened to select, recorded nowhere and asserted against nothing —
> which is the state that produced **D-17**, where a model fitted on 61 features scored on 14 and
> the output was still called `rank_score`.

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── D-07 Data Engine   prices (raw + adj_as_of), fundamentals (as_of),
  │                      events, macro, sector — ALL through its public API
  └── D-00 shared        Money, errors, logging, ids

DEPENDED ON BY
  ├── D-01 Fundamental   valuation, quality, moat, ratios     (§6.2)
  ├── D-03 Quant         features + labels                    (§6.3)
  ├── D-04 Models        THE FEATURE CONTRACT + labels        (§6.3)
  └── D-05 Risk          exposure inputs, betas               (§6.4)

DOES NOT DEPEND ON
  ✗ any analytical domain (D-01, D-03, D-04, D-05, D-06)
      — D-02 is UPSTREAM of all of them. An input that came from
        an analyst is the INV-014 leak wearing a different hat
        (L0 §4.3). See §8.3 for the one live violation.
  ✗ the LLM gateway — D-02 never calls a model (AP-5, ST-5)
  ✗ D-08 Orchestration — the scheduler invokes D-02, never the reverse
  ✗ an external API — everything comes through D-07 (DE-1)
```

---

# 4. MODULE DECOMPOSITION

```text
src/feature_engineer/
├── contracts/          # ★ THE FEATURE CONTRACT — §5
│   ├── registry.py     #   named, versioned contracts
│   ├── spec.py         #   FeatureSpec: formula id, dtype, range, inputs, PIT class
│   └── sets/           #   versioned YAML, one file per contract version
├── valuation/
│   ├── dcf.py          #   owner-earnings DCF          ★ carries D-19 (§8.1)
│   ├── margin_of_safety.py
│   └── reconcile.py    #   multi-method reconciliation
├── quality/
│   ├── moat.py         #   ★ carries the duplicate-definition defect (§8.3)
│   ├── checks.py       #   ROIC / D-E / FCF / current-ratio gates
│   └── screen.py
├── fundamental/        #   ratios, margins, growth, accruals, Piotroski,
│   │                   #   sector-relative z-scores  (the 45 f_* features)
│   ├── ratios.py  ├── piotroski.py  ├── accruals.py
│   ├── trend.py   └── sector_relative.py
├── technical/          #   indicators, derived price series (the 14 price features)
│                       #   ★ carries D-16 (§8.2)
├── ml_features/        #   assembly of the panel against a contract
├── labels/             #   forward returns, cross-sectional bins — §7.4
└── validation/         #   range checks, coverage, contract conformance
```

---

# 5. THE FEATURE CONTRACT

## 5.1 What it is

A **FeatureContract** is a named, versioned, immutable declaration of exactly which features exist,
how each is computed, and what each is allowed to contain. It is published by D-02 and consumed by
D-04 as the thing parity asserts against.

Today's equivalent is `pipeline/ohlcv/dataset/feature_schema.py` — a Python module holding four
lists. It is the right idea and it is doing real work; what it lacks is **a version, a formula
identity per feature, and any statement of range or provenance.** Those three absences are what let
D-16, D-17 and §8.3 happen.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A FEATURE LIST SAYS WHICH COLUMNS EXIST.                        ║
║  A FEATURE CONTRACT SAYS WHAT EACH COLUMN MEANS.                 ║
║                                                                  ║
║  "rsi_14" in a list is a name. Two implementations can both      ║
║  satisfy it and disagree by 15 points (D-16 — ours uses a simple ║
║  rolling mean where every charting package uses Wilder           ║
║  smoothing, and nothing recorded the choice).                    ║
║                                                                  ║
║  In a contract, rsi_14 carries a FORMULA ID. Change the formula, ║
║  change the id, change the contract version — and every model    ║
║  trained on the old one fails parity LOUDLY instead of scoring   ║
║  on a silently different input.                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 5.2 What a FeatureSpec carries

| Field | Why |
|---|---|
| `name` | `rsi_14` |
| `formula_id` | `rsi.wilder.v1` \| `rsi.rolling_mean.v1` — **changing the maths changes this** |
| `dtype` | float64 / int / bool |
| `range` | `[0, 100]` — enforced, constitution **INV-3** |
| `inputs` | which D-07 fields and which other features it derives from |
| `pit_class` | A / B / C, inherited from `L1-data-engine.md` §5A.4 |
| `null_policy` | `allow` \| `forbid` — **never `fill_zero`** (§7.5) |
| `owner_module` | the one place it is computed |
| `since_version` / `deprecated_in` | lifecycle |

## 5.3 The contract today — 61 features

Inherited verbatim from `feature_schema.py`, restated so the spec and the code can be diffed.

| Group | Count | Prefix | Source |
|---|---|---|---|
| **Price / OHLCV** | **14** | none | `OhlcvFeatureEngineer` over D-07 prices |
| **Fundamental** | **45** | `f_` | `FundamentalsFeatureEngineer` over D-07 fundamentals |
| **Group C** (formula-only Buffett) | **2** | `f_` | `FundamentalEngine.compute_formula_features` |
| **Total (`ALL_FEATURES_V2`)** | **61** | — | 47 of them `f_*` |

**Price (14):** `ret_1d` `ret_5d` `ret_10d` `ret_20d` · `sma_5_ratio` `sma_20_ratio` `sma_50_ratio` ·
`vol_10d` `vol_20d` · `rsi_14` `macd_hist` · `vol_zscore_5d` · `rank_ret_5d` `rank_vol_20d`

**Fundamental (45):** profitability (11) · leverage (4) · liquidity (1) · efficiency & size (3) ·
valuation (1) · accruals (2) · Piotroski (4) · growth & trend (11) · margin-trend OLS (3) ·
sector-relative z (5)

**Group C (2):** `f_graham_number_ratio` · `f_moat_quant_score`

> **Two naming defects inherited, recorded rather than fixed in the move.**
> **(a)** `MODEL_FEATURES` is an alias for `PRICE_FEATURES` "for backward compatibility" — so a
> name that reads like *the model's features* means *14 of the 61*. `main_inference.py:595` falls
> back to it, which is one of the two paths D-17 travelled.
> **(b)** `f_f_net_margin_trend_4` and its two siblings carry a doubled prefix. Cosmetic, but it is
> evidence that the list is maintained by hand.

## 5.4 Rules

| ID | Rule |
|---|---|
| **FE-1** | A feature exists **only** if it has a `FeatureSpec` in a published contract. An unspecified column in the panel is a defect, not a bonus feature |
| **FE-2** | A contract version is **immutable once published**. Changing any `formula_id`, range, or membership produces a **new version** |
| **FE-3** | Every artifact D-02 emits records the **contract name and version** it was built against. A panel that cannot name its contract cannot be parity-checked |
| **FE-4** | **One feature, one owning module.** Two implementations of one concept is the defect this domain exists to remove (§8.3) |
| **FE-5** | A feature's declared `range` is **enforced at emit**, not documented (**INV-3**). Out of range raises |
| **FE-6** | Deprecation is by **tombstone**: a removed feature keeps its spec with `deprecated_in` set, so an old model's contract still resolves |
| **FE-34** | ★★ **A cross-sectional feature must be SCALE-INVARIANT, or it teaches the price level.** ⚠ *Found 2026-08-27 rebuilding §5.3's fourteen:* the inherited `macd_hist` is a price **difference**, and on 2026-08-26 it printed **2007** for `SNDK` (≈$1 499) beside **3.1** for `AAPL` (≈$313). ★ Every other price feature is a return, a ratio, a z-score or a percentile rank; **one dollar-denominated column is enough for a ranker to learn *"expensive stocks have big MACD"***, which is true and worthless. Normalised by its own slow EMA, and the `formula_id` says `_normalised` so an old model cannot silently parity-match the new arithmetic |
| **FE-35** | ★★ **A recursive feature declares a WARM-UP, and the warm-up BOUNDS the dependence rather than removing it.** ⚠ An EWM is recursive from whatever row it is handed, so `macd_hist` over a 200-day window and a 400-day window differ — INV-2, and invisible in a single run. ★ *Measured*: the first row's weight after `k` rows is `(1−2/27)^k` — `k=78 → 2.5e-3`, `k=156 → 6.1e-6`; at a 78-session warm-up, windows with 30/60/120/240 sessions of prior history agreed **exactly**. ⚠ **6× would be tighter and is refused**: the daily run fetches ~138 sessions, and a 156-session warm-up makes the column **entirely null in production** |
| **FE-36** | ★ **A feature whose input is not knowable at the day-T open is lagged, not merely approximated.** ⚠ `vol_zscore_5d` read `volume(T)`. A close-based feature is *partly* wrong at the open; **a volume-based one is wholly wrong** — the quantity does not exist until the session ends. Volume features end at **T−1** (FE-28) |
| **FE-37** | ★★ **Null-ness itself correlates with sector, and the consumer must be told.** ⚠ *Measured 2026-08-27 over a 120-day panel:* **NVDA 37 of 45 fundamental features present, WMT 32, JPM 18.** A bank has **no gross profit and no current/non-current split**; a REIT reports neither. ★ **These nulls are correct** — FE-14 forbids imputing them — but the *pattern* of nulls is a sector dummy arriving through the back door, and a model can learn *"the ones with holes are financials"* without ever seeing a sector column. ⚠ The remedy belongs to the consumer (**FE-15**: imputation is the consumer's decision, applied downstream and recorded); D-02's duty is to **declare the coverage** rather than to flatten it |
| **FE-38** | ★★ **A canonical item that is a COUNT must not be divided out of minor units.** ⚠ *Found 2026-08-27 building Group C:* `canonical_frame` divided **every** column by 100, and a share count went with the money — NVDA's real **24 285 000 000** diluted shares became **242 850 000**, so market capitalisation was **100× too small** and `f_market_to_book` with it. ★ The same class as **DE-52** one layer up: a non-monetary quantity carried through a monetary conversion, where DE-52 keeps per-share *ratios* out of the ingest and a share *count* has to stay in it. ⚠ **Declared, never inferred from an empty `<tag>_currency`** — an absent currency column and a genuinely non-monetary one look identical, and guessing would scale correctly right up until a currency went missing |
| **FE-39** | ★ **A component of a composite score must be shown to VARY before it is given a weight.** ⚠ The inherited `f_moat_quant_score` weighted stability at **20 %** and computed it as `clip(1 − std(ROA), 0, 1)`; quarterly ROA dispersion for a large filer runs 0.01–0.05, so the term spanned **0.95–0.99** — a fifth of the score that could not distinguish anything. ★ A **coefficient of variation** replaces it. ⚠ *A cross-sectional rank was tried first and abandoned: **no two filers share a fiscal calendar**, so grouping by `period_end` gave every group one member and nulled the column* |
| **FE-40** | ★★★ **A panel spanning many dates takes its fundamentals from a per-filing-date REPLAY, never from one read at the last date.** For each filing date F: `per_filing(rows as of F)`, keep the row the as-of join picks at F; the panel then joins those rows backward on F. Each `(ticker, date)` thereby carries exactly what a run on that date would have computed — growth, trend and Piotroski included, on the figures known then. ⚠ *Added 2026-10-07 (`DX-159`):* `growth.py`'s *"PIT visibility is already settled by `get_fundamentals`"* holds for one date; read once at today for a ten-year panel, every period sat at its latest re-filing and the training panel ran ~1 year stale |
| **FE-41** | ★★ **`sector_z` is NULL for a name whose sector is unknown — unknown names are never pooled into a bucket of their own.** ⚠ *Added 2026-10-07 (`DX-160`):* `build`'s docstring promised *"without [sectors] the five `*_sector_z` columns are null"*, but `sector_z` grouped with `dropna=False`, so with no map every name sat in one `None` group and the five features were **market-wide** z-scores under sector-relative names; the fitted model ranked `f_net_margin_sector_z` 2nd by gain. A z-score against an unknown peer group is not a z-score |
| **FE-42** | ★★ **`cross_sectional_gauss(labels)` — a TRAINING TARGET derived from CT-2.3 labels: within each date, the forward return's average-tie rank `r` among the `n` names becomes `ẑ = Φ⁻¹((r − ½) / n)`.** Same rows, same `available_at`, a new `label_def_id` (`<id>.xs_gauss`). A date with fewer than 3 names yields no target (a rank over two names is ±1). ★ Why Gaussian, not the raw percentile: D-04 inference publishes `ẑ · σ̂ · √h` (QA-58) — a centred score; a percentile in (0, 1) is all positive, and multiplying it by σ̂ would rank mostly by volatility. ⚠ It is a **target only**: realised IC, the simulation and every gate read the raw return. *Added 2026-10-08 (Victor; lecture L8 §7.2)* |

---

# 6. THE TWO CONSUMERS — closes `L4` Q-10

`L4-coding-standards.md` left open *which D-02 outputs are published to which consumer*. This is the
answer. It matters because the two consumers fail in different ways (L0 §1.6) and therefore need
different guarantees, not different data.

## 6.1 The principle

> **Both seats consume the same numbers. They do not consume the same *shape*.**
>
> D-01 asks about **one company at one as_of** and needs the arithmetic trail so it can cite.
> D-03/D-04 ask about **the whole universe across time** and need a dense, contract-bound panel.
> Serving one shape to both is how a valuation ends up in a training row (INV-014) or a panel
> column ends up quoted in a thesis without its derivation.

## 6.2 Published to D-01 Fundamental (SEAT-2)

**Shape: `ValuationResult` / `QualityResult` / `MoatResult` — per ticker, per as_of, with the full
arithmetic trail.** Not a panel row.

| Output | Contains |
|---|---|
| `valuation(ticker, as_of)` | fair value (`Money`), method, every assumption, every intermediate, the sensitivity band |
| `quality(ticker, as_of)` | each gate's pass/fail **and the input that decided it** |
| `moat(ticker, as_of)` | durability score + components |
| `ratios(ticker, as_of)` | the 45 `f_*` values **as named quantities**, each with its inputs |
| `peer_context(ticker, as_of)` | sector-relative position for the same metrics |

**Why the trail and not just the number:** AP-2 requires every claim to be traceable to a data
point. A thesis that says "ROIC of 24% comfortably exceeds cost of capital" must be able to name
the NOPAT and the invested capital it came from. A bare float cannot support a citation.

## 6.3 Published to D-03 Quant / D-04 Models (SEAT-3)

**Shape: a contract-bound panel — `(ticker, date)` × the declared feature set, plus labels.**

| Output | Contains |
|---|---|
| `panel(contract, tickers, start, end, as_of, adj_as_of)` | the FeatureRow matrix + the contract version stamped on it |
| `labels(definition, tickers, start, end)` | forward returns / cross-sectional bins — §7.4 |
| `contract(name, version)` | the FeatureSpec set, for parity assertion |
| `coverage(contract, tickers, as_of)` | **per-ticker usable-feature fraction, counting NaN-but-present as missing** |

**`coverage` is not a convenience.** It is the measurement F1 AC-1.15 needs and the one D-17 proved
was absent: a name can be *in* the panel with every `f_*` column present and every value NaN, and
nothing in a column-name check will notice.

## 6.4 Published to D-05 Risk (SEAT-4)

Betas, correlations' input series, **sector** mappings, and the size/exposure inputs. Same
deterministic guarantee, no separate machinery.

> ⚠ **This line said "sector and theme mappings" until 2026-08-25.** ★ **D-02 publishes no
> theme** (D-05 **RK-37**): theme membership is *a judgement call about what counts*, and for
> D-02 to label one it would have to know D-05's taxonomy — which **FE-21** forbids it to
> import. D-05 resolves theme from the sector published here plus its own `CT-5.3`.

## 6.5 What is published to nobody

| Not published | Why |
|---|---|
| Intermediate frames mid-computation | not a contract; would be depended on |
| A "latest" panel with no `as_of` | DE-6.4's defect, one layer out |
| Anything derived from an analyst's output | INV-014 — and see §8.3 |

---

# 7. DETERMINISM & POINT-IN-TIME OBLIGATIONS

D-02 inherits four constitution invariants and adds nothing to them except enforcement.

## 7.1 As-of is pass-through, never defaulted

| ID | Rule |
|---|---|
| **FE-7** | Every D-02 entry point takes `as_of` and **has no default**. It is passed to D-07 unchanged. D-02 never asks D-07 for "latest" on behalf of a caller who did not say so (**DE-6.4**, INV-1) |

## 7.2 Prices carry a second axis

`L1-data-engine.md` §5C.7 established that the adjusted price series is restated data.

| ID | Rule |
|---|---|
| **FE-8** | Price-derived features take **`adj_as_of` in addition to `as_of`**, and the panel records both. Two panels over the same dates with different `adj_as_of` are different data (**DE-30**) |
| **FE-9** | A feature that is **not scale-invariant** — any absolute price or volume threshold, any share count, the M-1 penny-stock screen — is computed on the **raw** series (**DE-29**). Returns, ratios, dollar volume and within-ticker z-scores are scale-invariant and may use the adjusted panel |

> **This is a live defect, not a hypothetical.** `OhlcvFeatureEngineer` builds all 14 price features
> from `adj_close` with no `adj_as_of` anywhere. Every one is a return or a ratio, so the *values*
> are scale-invariant and correct — but the panel is not reproducible across a future split, which
> is constitution **INV-2**. See §8.4.

## 7.3 The calendar check is a precondition

| ID | Rule |
|---|---|
| **FE-10** | D-02 does not build a panel for a window until D-07's **calendar check** (`L1-data-engine.md` §6A, **CT-7.7**) has returned `PROCEED` or `PROCEED_WITH_FLAGS` for that window. A `HALT` propagates; D-02 never computes "around" a blocking corporate action. ★ **CT-2.2's `calendar_check_id` is CT-7.7's `report_id`** — *named here from 2026-08-23, because citing a section rather than a contract is how this stamp came to reference a field D-07 had never declared* |

## 7.4 Labels are forward-looking on purpose, and that is the danger

A label is the one thing in this domain that legitimately looks forward. Everything else must not.

| ID | Rule |
|---|---|
| **FE-11** | Labels live in `labels/`, **never in `contracts/`**, and a label may never appear in a FeatureContract. The directory boundary is the guard: one module is allowed to see the future and it is not the one models take inputs from |
| **FE-12** | Every label declares its **horizon** and its **as-of-availability date** = `date + horizon`. A backtest may not train on a label whose availability date exceeds its as-of |
| **FE-13** | Cross-sectional label binning is computed **within a date group only** — never over the pooled sample, which leaks the future distribution into the past |

> FE-13 is inherited from a real defect: `_cross_section_rank` exists because a `pd.qcut` inside
> `groupby.transform` silently returned NaN for **77% of training rows**. The current code is
> correct; the rule exists so it stays correct.

## 7.5 Missingness

| ID | Rule |
|---|---|
| **FE-14** | Missing is `null`. **Never zero, never a mean, never forward-filled across a period boundary.** A zero margin and an unknown margin are different facts (DE-14) |
| **FE-15** | Any imputation is the **consumer's** decision, applied downstream and recorded. D-02 does not impute, because an imputed value is indistinguishable from a measured one once it is in the panel |

> Today `fillna_zero: false` in `config/settings.yaml` is correct and was arrived at the hard way:
> the earlier `true` zero-filled at train time but **not** at inference — a train/serve skew that
> also silently broke the CPCV protocol the production configs were tuned under.

## 7.6 Determinism

| ID | Rule |
|---|---|
| **FE-16** | Same inputs + same contract version + same `as_of` + same `adj_as_of` ⇒ **byte-identical output** (**INV-2**). No wall-clock, no `dict` iteration order, no unseeded randomness, no locale |
| **FE-17** | Every feature is **pure** with respect to its declared `inputs`. A feature reading anything not in its FeatureSpec is a defect the contract cannot see |

---

# 8. INHERITED DEFECTS — the honest register

D-02 receives ~5,450 LOC of working code that carries four known problems. **They are recorded here
so the migration cannot launder them into the new tree as clean code.** `L4` §1.4 classes most of
these files **VERBATIM** precisely so the move preserves blame and the fix is a separate, reviewable
commit.

## 8.1 D-19 — the DCF returns an enterprise value per share

**Status: 🔴 open, deliberately unfixed.**

`DCFCalculator.calculate` projects revenue × FCF margin (a firm-level cash flow), discounts at
**WACC** (a firm-level rate), correctly producing an **enterprise value** — the local variable is
even named `entity_value` — then does `per_share = entity_value / shares` **with no net-debt
subtraction**. The word *debt* appears nowhere in the file.

The error equals net debt per share, so **it scales with leverage**: CHTR measured at 455% of market
cap (IV/share $1,940 against a $157.69 price), ENB at 128% — and **ENB is on the practice
watchlist, the actionable path** (INV-6). MSFT ~3%, NVDA/MU ~0–1%.

| ID | Rule |
|---|---|
| **FE-18** | The DCF moves **VERBATIM**. D-19 is fixed only after the Tier-1 reality probe (F3 §4a) establishes *which* number is wrong — the open question is whether the projected flow is FCFF (fix = subtract net debt) or owner-earnings, which is already post-interest (fix = the discount rate). **WACC-on-FCFF and cost-of-equity-on-FCFE are two coherent designs and this code mixes their halves** |

`L1-data-engine.md` §5A.5 puts `enterprise-values` (which carries `minusCashAndCashEquivalents` +
`addTotalDebt`) and `owner-earnings` at priority 1 and 2 specifically to supply the probe's inputs.

## 8.2 D-16 — `rsi_14` is not Wilder's RSI

**Status: 🟡 frozen, not verified.**

`rsi_14` averages gains and losses with a **simple 14-day rolling mean**; essentially every charting
package and TA library uses **Wilder smoothing** (an EMA with α=1/14). The two diverge materially
after warm-up, so our `rsi_14` is **not comparable to an RSI read off a broker screen**.

This is a defensible variant, not a proven defect — as a model feature, consistency matters more
than convention, and it has been consistent since written. `tests/test_ohlcv_features_golden.py`
freezes it, but a characterization test asserts *"unchanged"*, never *"correct"*.

| ID | Rule |
|---|---|
| **FE-19** | `rsi_14` gets `formula_id = rsi.rolling_mean.v1` in the contract — **the variant is declared, not implied.** Changing to Wilder means a new `formula_id` and a new contract version, which invalidates every model trained on the old one. That is the correct cost and it should be paid deliberately |

Also unresolved and now declared: `rank_ret_5d` uses `ascending=False` while `rank_vol_20d` uses
`ascending=True`. Plausibly deliberate, never documented.

## 8.3 Two moat definitions — and one of them breaches INV-014

**Status: 🔴 open. Found 2026-08-16 while writing this spec.**

There are two moat computations in the codebase, with different formulas and different scales:

| | `MoatScorer.score()` | `FundamentalEngine._moat_quant()` |
|---|---|---|
| Path | `buffett/analysis/moat_scorer.py` | `core/fundamental_engine.py` |
| Scale | 0–10 | 0–1 |
| Formula | `0.7 × quant + 0.3 × llm_score` | panel-native profitability + stability + reinvestment |
| Used by | reports, `SignalEngine` | **training**, as `f_moat_quant_score` |
| In the contract? | no | **yes — Group C** |

Two problems, and the second is the serious one.

**(a) Duplicate definition.** A report can say "moat 7.4/10" while the model that ranked the same
name trained on a different number computed a different way. Neither is wrong; they are simply not
the same quantity, and nothing says so. **This is exactly what FE-4 forbids.**

**(b) `MoatScorer` consumes SEAT-2's output.** `_llm_score` is deterministic — it does *not* call a
model — but it reads `moat_type`, `moat_threats` and `management_signals` out of
`{TICKER}_profile.json`, **which an LLM in D-01 authored**. So a "D-02" number is 30% a function of
seat 2's judgement.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THIS IS THE INV-014 LEAK THE D-02/SEAT-5 DECISION WAS MEANT     ║
║  TO PREVENT — AND IT IS ALREADY IN THE CODE.                     ║
║                                                                  ║
║  L4 §1.2 argues D-02 under SEAT-5 keeps the analyst seats        ║
║  independent because neither consumes the other's output.        ║
║  That argument holds only if D-02 ITSELF consumes neither.       ║
║                                                                  ║
║  A deterministic function of an LLM's output is still the LLM's  ║
║  judgement. The determinism is in the transport, not the source. ║
║                                                                  ║
║  Today this does not reach the model — f_moat_quant_score is     ║
║  the panel-native one. But the two are named as if they were     ║
║  the same thing, and a future "let's use the better moat score"  ║
║  is one commit away from putting seat 2's narrative into         ║
║  seat 3's training set.                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **FE-20** | The **panel-native** moat is D-02's and keeps the name. The profile-derived blend is **not a D-02 feature** — it is a D-01 judgement that happens to be arithmetic, and it moves to `src/fundamental/` or is retired. **Whichever survives, exactly one may be called `moat`** (FE-4) |
| **FE-21** | **No D-02 feature may take an input produced by D-01, D-03, D-04, D-05 or D-06** — including a deterministic transform of one. A FeatureSpec's `inputs` are D-07 fields and other D-02 features, and nothing else. Grep-checkable, like ST-5 |

## 8.4 The price panel is not reproducible across a split

**Status: 🔴 open, systemic.**

All 14 price features derive from `adj_close`. Their *values* are scale-invariant, so nothing is
numerically wrong today. But the adjusted series is restated whenever a split occurs
(`L1-data-engine.md` §5C.7 — NVDA's 10:1 rescaled every prior price by 10 and every prior volume by
10 in the opposite direction), so **the same training run over the same dates produces different
inputs depending on when it is run.** That is constitution **INV-2**.

It also puts `tests/test_ohlcv_features_golden.py` in an impossible position: a live fixture reddens
on a future split for reasons unrelated to the code; a frozen fixture drifts from production.

| ID | Rule |
|---|---|
| **FE-22** | The golden fixture is a **frozen artifact with a recorded `adj_as_of`**, and the test asserts against the panel rebuilt at that same `adj_as_of`. A split then changes neither side |

---

---

# 5Z. ★ THE DAY-T FEATURE ROW IS ANCHORED ON THE OPEN — **2026-08-18**

D-08 §5A decides at the **day-T open**; D-03 §5.9 anchors labels there. D-02 builds the row the
decision is taken from, so the anchor binds here too.

| ID | Rule |
|---|---|
| **FE-28** | ★ The **day-T feature row uses data available at the day-T open**: everything through the T−1 close, plus the **settled day-T opening print**. Nothing from later in session T may enter it — that would be look-ahead against the system's own decision time (INV-1) |
| **FE-29** | ★ **No synthetic day-T bar.** `main_inference.py:250` currently splices a spot quote into `open`, `high`, `low`, `close` and `adj_close` **as one number**, making the day-T intraday range identically zero while every training bar has a real range. Any feature reading `high − low` or `open − close` is **degenerate on the one bar that matters** — an INV-4 parity break to be designed out, not carried over (D-08 §5A.2) |
| **FE-31** | ★ **`decision_anchor` is a field of the label set, not a convention** (CT-2.3, D-03 QA-72). A mixed-anchor panel is a defect; **QA-82's dual-anchor evaluation cycle is the one legal exception and is distinguished by the field, not by a filename** |
| **FE-32** | ★★ **Price inputs arrive as `Money` (`*_minor` + `*_currency`) and leave as dimensionless ratios.** ⚠ **`L2-shared-money.md` MO-4 says *"float never appears in a stored field"* — read literally that forbids `ret_1d`, which is a stored float feature.** It does not: **a ratio of two Money values of the same currency is dimensionless and is no longer money** (MO-8). The division is where the type is left, it happens **once**, in D-02, and **cross-currency ratios are forbidden** — a ratio only means something within one currency |
| **FE-33** | ★ **CT-2.1's `inputs:` names map to CT-7.1 columns explicitly.** `price.adj_close` **is** `adj_close_minor` + `adj_close_currency`; `price.adj_open` **is** `adj_open_minor` (**DE-42**). ⚠ **The two contracts used different names for the same column and neither said so** |
| **FE-30** | ★ **`open` must be split- and dividend-adjusted on the same basis as `adj_close`.** The current panel adjusts only the close; the `open` column **has never been consumed by any feature or label**, so its adjustment has never been exercised. Across NVDA's 10:1 this is a **10× error**, not a rounding one (D-03 QA-73, `L1-data-engine.md` §5C) |


# 9. CONTRACTS

> **ID-collision notice.** Per the convention this design tier uses, `AC-<n>.<k>` and `CT-<n>.<k>`
> key `n` on the **domain** — so D-02 issues `AC-2.k` / `CT-2.k`. **`sdd/specs/F2_portfolio_and_delivery/spec.md` *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))*
> already issues `AC-2.1`…`AC-2.8` against live code with passing tests.** This is the collision L0
> §16.4 records as knowingly accepted; unlike the D-07/F7 case it is **live, not latent**. Always
> qualify: "D-02 AC-2.3" or "F2 AC-2.3", never a bare `AC-2.3`.

## CT-2.1 — Feature contract (versioned YAML)

```yaml
name: all_features
version: 3            # immutable once published (FE-2)
created: 2026-08-16
features:
  - name: rsi_14
    formula_id: rsi.rolling_mean.v1     # NOT wilder — §8.2
    dtype: float64
    range: [0, 100]
    inputs: [price.adj_close]
    pit_class: C
    null_policy: allow
    owner_module: technical.oscillators
  - name: f_roic
    formula_id: roic.nopat_over_invested_capital.v1
    dtype: float64
    range: [-5.0, 5.0]
    inputs: [fundamentals.operating_income, fundamentals.tax_rate,
             fundamentals.total_assets, fundamentals.current_liabilities]
    pit_class: C
    null_policy: allow
    owner_module: fundamental.ratios
```

## CT-2.2 — Feature panel (parquet)

| Column | Type | Note |
|---|---|---|
| `ticker` | string | uppercase |
| `date` | date32 | |
| *(one column per FeatureSpec)* | per spec | names and dtypes **exactly** as the contract declares |
| `contract_name` · `contract_version` | string · int | **required** (FE-3) |
| `as_of` · `adj_as_of` | date32 | **both required** (FE-7, FE-8) |
| `calendar_check_id` | string | the D-07 report that cleared this window (FE-10) |

Constraints: no column outside the contract · every contract feature present (null allowed, absent
not) · every value inside its declared range · `(ticker, date)` unique.

## CT-2.3 — Label set (parquet)

`(ticker, date, horizon_days, label_def_id, ★ decision_anchor, value, available_at)`

★ **`decision_anchor ∈ {open, close, arrival}` is REQUIRED** — D-03 **QA-72** states the anchor is
*"a declared property of the label set, recorded in the label contract"*, and this contract is that
label contract. It was absent. **A label set whose anchor is not on the row cannot be compared with
one built on a different anchor, and nothing would notice** (D-03 §5.9.1).

`available_at = date + horizon_days`, materialised rather than computed, so FE-12 is checkable by
comparison rather than by trusting arithmetic at every call site.

## CT-2.4 — Coverage report (JSON)

Per ticker: `features_declared`, `features_usable` *(present **and** non-null)*, `coverage_fraction`,
`missing[]`. **NaN-but-present counts as missing** — the half a column-name check is structurally
blind to (D-17).

---

# 10. PUBLIC API SURFACE

Exported from `src/feature_engineer/__init__.py`. Nothing else is importable from outside (ST-3).

| Method | Returns | Note |
|---|---|---|
| `get_contract(name, version)` | `FeatureContract` | `version=None` ⇒ latest **published** |
| `build_panel(contract, tickers, start, end, as_of, adj_as_of)` | `FeaturePanel` | **all five arguments required** |
| `build_labels(label_def, tickers, start, end)` | `LabelSet` | separate call — labels are never in a panel (FE-11) |
| `coverage(contract, tickers, as_of)` | `CoverageReport` | NaN-aware (CT-2.4) |
| `valuation(ticker, as_of)` | `ValuationResult` | full arithmetic trail (§6.2) |
| `quality(ticker, as_of)` | `QualityResult` | per-gate inputs |
| `moat(ticker, as_of)` | `MoatResult` | panel-native only (FE-20) |
| `ratios(ticker, as_of)` | `dict[str, Quantity]` | named quantities, with inputs |
| `peer_context(ticker, as_of)` | `PeerContext` | sector-relative position |

---

# 11. BUSINESS RULES

| ID | Rule |
|---|---|
| **FE-1…FE-6** | The feature contract — §5.4 |
| **FE-7…FE-17** | Determinism & point-in-time — §7 |
| **FE-18…FE-22** | Inherited defects — §8 |
| **FE-23** | D-02 reaches D-07 **only** through its public API. No file reading, no path construction, no cache peeking |
| **FE-24** | Every computed monetary value is a `Money` (INV-001). A fair value without a currency does not compile |
| **FE-25** | A formula appears in **exactly one module**. If two callers need it, they import it — they do not reimplement it (FE-4) |
| **FE-26** | Sector-relative statistics are computed **within (sector, period)** groups only, never pooled across time. A pooled z-score leaks the future distribution |
| **FE-27** | A feature whose inputs are absent emits `null` and is **counted in the coverage report**. It never silently drops the row — that is DE-13's lesson one layer out |

---

# 12. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `FEAT.CONTRACT.UNKNOWN` | ERROR | no such contract name/version |
| `FEAT.CONTRACT.MUTATED` | ERROR | a published version's content changed (FE-2) |
| `FEAT.CONTRACT.UNDECLARED_COLUMN` | ERROR | panel contains a column with no FeatureSpec (FE-1) |
| `FEAT.CONTRACT.MISSING_FEATURE` | ERROR | a declared feature is absent from the panel |
| `FEAT.RANGE.VIOLATION` | ERROR | value outside the declared range (INV-3, FE-5) |
| `FEAT.PIT.AS_OF_REQUIRED` | ERROR | `as_of` or `adj_as_of` omitted (FE-7, FE-8) |
| `FEAT.PIT.CALENDAR_HALT` | ERROR | D-07's calendar check returned HALT (FE-10) |
| `FEAT.LABEL.IN_CONTRACT` | ERROR | a label appears in a FeatureContract (FE-11) |
| `FEAT.LABEL.NOT_AVAILABLE` | ERROR | label `available_at` exceeds the caller's as-of (FE-12) |
| `FEAT.INPUT.ANALYST_DERIVED` | ERROR | a FeatureSpec input traces to D-01/D-03/D-04/D-05/D-06 (FE-21, INV-014) |
| `FEAT.DUPLICATE_DEFINITION` | ERROR | two modules compute the same `formula_id` (FE-4, FE-25) |
| `FEAT.COVERAGE.DEGRADED` | WARNING | a ticker below the coverage floor — reported, never dropped (FE-27) |

---

# 13. ACCEPTANCE CRITERIA

```text
THE CONTRACT
□ AC-2.1   A column with no FeatureSpec fails panel validation
□ AC-2.2   A declared feature absent from the panel fails validation
□ AC-2.3   Republishing a version with different content raises (immutability)
□ AC-2.4   Every panel artifact records contract name + version
□ AC-2.5   A value outside its declared range raises (INV-3)
□ AC-2.6   Changing a formula without changing formula_id is caught
□ AC-2.7   A deprecated feature's spec still resolves for an old model's contract

POINT-IN-TIME & DETERMINISM
□ AC-2.8   Omitting as_of or adj_as_of raises — no default to today
□ AC-2.9   Same inputs + contract + as_of + adj_as_of => byte-identical (INV-2)
□ AC-2.10  Two panels over the same dates with different adj_as_of are not equal
□ AC-2.11  A non-scale-invariant feature reads the RAW price series (DE-29)
□ AC-2.12  A calendar-check HALT propagates; no panel is built (FE-10)
□ AC-2.13  No feature reads data with a knowability date after as_of (INV-1)

LABELS
□ AC-2.14  A label in a FeatureContract raises (FE-11)
□ AC-2.15  Every label carries horizon and materialised available_at
□ AC-2.16  Training on a label whose available_at exceeds the as-of raises
□ AC-2.17  Cross-sectional binning is within-date; a pooled bin is caught
□ AC-2.18  Label construction drops no row silently (the 77% regression)

MISSINGNESS & COVERAGE
□ AC-2.19  Missing is null; no zero-filling, no mean-filling, no cross-period ffill
□ AC-2.20  coverage() counts NaN-but-present as missing (D-17)
□ AC-2.21  A ticker with absent inputs is reported degraded, never dropped (FE-27)

INDEPENDENCE (INV-014)
□ AC-2.22  A FeatureSpec whose inputs trace to any analytical domain raises (FE-21)
□ AC-2.23  No module in src/feature_engineer imports the LLM gateway (AP-5, ST-5)
□ AC-2.24  No module in src/feature_engineer imports D-01/D-03/D-04/D-05/D-06
□ AC-2.25  Exactly one module computes each formula_id (FE-4, FE-25)

INHERITED DEFECTS
□ AC-2.26  The DCF moves byte-identically (R100) before any D-19 fix (FE-18)
□ AC-2.27  rsi_14 declares formula_id rsi.rolling_mean.v1, not a wilder id (FE-19)
□ AC-2.28  Exactly one feature is named `moat`; the profile-derived blend is not
           a D-02 feature (FE-20)
□ AC-2.29  The golden fixture records its adj_as_of and the test rebuilds at it (FE-22)

MONEY
□ AC-2.30  Every computed monetary value is a Money with explicit currency (INV-001)
□ AC-2.31 ★ the contract declares §5.3's fourteen and every one has a
           builder — FE-1 runs both ways
□ AC-2.32 ★★ no day-T feature changes when data after T changes; the
           volume z-score ends at T−1 (FE-28, FE-36, INV-1)
□ AC-2.33 ★★ rsi_14 is Wilder's, exactly 100 with no losses and null when
           flat — no epsilon (L5 D-16, FE-14)
□ AC-2.34 ★★ macd_hist is dimensionless and does not move with the
           caller's history window (FE-34, FE-35)
□ AC-2.35 ★ cross-sectional ranks are computed within a date only (FE-13)
□ AC-2.36 ★★ a declared range raises at emit; a null does not (FE-5, INV-3)
□ AC-2.37 ★ the same inputs yield a byte-identical panel (FE-16, INV-2)
□ AC-2.38 ★ the contract declares 45 f_* features, derived from the build
           tables, and keeps the inherited doubled prefix (FE-4, FE-6)
□ AC-2.39 ★★ no filing joins to a date before its filing_date, and the key
           is filing_date not period_end (INV-1)
□ AC-2.40 ★★ multi-period features survive a short panel window — computed
           per filing, joined afterwards
□ AC-2.41 ★ zero/negative denominators yield null, never inf or a sign flip
□ AC-2.42 ★★ an uncomputable Piotroski signal nulls the score rather than
           scoring zero (FE-14)
□ AC-2.43 ★ sector z is within (date, sector) and null below three names
□ AC-2.44 ★ an f_* contract with no fundamentals raises, never a null block
□ AC-2.45 ★★ a share count survives canonicalisation unscaled; Graham is
           null on a loss; the moat stability term varies; Group C is
           declared as anchors (FE-38, FE-39, RA-151)
□ AC-2.46 ★★ a membership change bumps the version and moves the content
           hash; the model manifest carries the hash and parity fails on a
           membership change under one version (FE-2, MT-51)
□ AC-2.47 ★★★ with a fundamentals history, every panel date carries the row a single read
           at that date would give — a period is visible from its FIRST filing, and an
           amended figure only from the amendment (FE-40, DE-75)
□ AC-2.48 ★★ sector_z is null for a row whose sector is missing — with no map at all,
           all five *_sector_z columns are null (FE-41)
□ AC-2.49 ★★ cross_sectional_gauss maps each date's returns to centred normal scores by rank
           (ties averaged), keeps available_at, renames the label, and drops dates with < 3
           names; it is invariant to any monotone transform of a date's returns (FE-42)
```

---

# 14. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QF-1** | Does the fair value D-02 computes enter the D-03/D-04 panel at all? | It is *permitted* — D-02 is neutral ground (L4 §1.2) — but `f_dcf_margin_of_safety` was deliberately excluded from Group C because the owner-earnings DCF is not historically PIT-reconstructable. That reason survives; revisit only if the DCF becomes PIT |
| **QF-2** | Where does the **quality gate** live — D-02 computes it, but "1 of 4 gates passed ⇒ block buy" is a verdict | The computation is D-02; the threshold and the action are the consumer's. The current `SignalEngine` coupling needs unpicking, and it touches `L0` §1.6 (Q-5) |
| **QF-3** | One contract or several? | Today `PRICE_FEATURES` / `ALL_FEATURES` / `ALL_FEATURES_V2` are three overlapping sets. Named contracts make that explicit — but a model trained on one and scored against another is the D-17 hazard, so the registry must forbid mixing |
| **QF-4** | Does D-02 cache, or recompute? | 130 tickers × 61 features × ~650 days is cheap to recompute and expensive to invalidate correctly. Leaning recompute, with the parquet as an artifact rather than a cache |
| **QF-5** | Who owns the **sector mapping**? | Sector-relative z-scores need it; it comes from D-07's `profile` (Class B, no as-of). A sector reclassification silently rewrites history — the same hazard as §8.4 |
| **QF-6** | Does `f_graham_number_ratio` survive? | It uses `price_at_filing`, which is PIT-correct, but the Graham number is a valuation opinion with a formula, sitting in a training set. Worth a deliberate keep-or-drop |

---

# 15. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-02, §1.5, **INV-014** | domain definition, why SEAT-5 owns it, the independence rule §8.3 breaches |
| `L1-data-engine.md` §5A.4a | which data serves which consumer — the input side of §6 |
| `L1-data-engine.md` §5C.7, DE-27…DE-30 | price adjustment as restatement — the basis for FE-8/FE-9/FE-22 |
| `L1-data-engine.md` §6A | the calendar check FE-10 depends on |
| `L2-shared-money.md` CT-M.1 | `Money` — FE-24 |
| `L4-coding-standards.md` §1.2, §1.5, ST-2/ST-3/ST-5 | path, the ~5,450 LOC inbound, import rules. **Closes its Q-10** |
| `sdd/specs/constitution.md` INV-1, INV-2, INV-3, INV-4, P2, P5 | the invariants this domain enforces |
| `sdd/specs/F0_code_map/spec.md` §12 **D-16**, **D-17**, **D-19** | the three recorded defects §8 inherits *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F1_disciplinary_report/spec.md` AC-1.15 | prior art for the coverage measurement §6.3 publishes *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F3_sdd_adoption/spec.md` §4a Tier 1, CT-3.2 | the reality probe D-19 needs before it is fixed *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
