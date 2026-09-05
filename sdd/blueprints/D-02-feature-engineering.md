# Blueprint — D-02 Feature Engineering *(B3 slice)*

> **Code:** `src/feature_engineer/` · **Spec:** `sdd/design/rel6_design/L1-feature-engineering.md` · **Seat:** SEAT-5
> **Status:** written 2026-08-23 at **B3** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠ **PARTIAL DOMAIN.** B3 builds the **feature contract mechanism** and two price features.
> Valuation (the DCF, D-19), quality, moat, the 45 `f_*` fundamentals, labels and sector-relative
> z-scores are **B4 and later** — §9 lists what is deliberately absent.

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-27 | ★★ **`fundamental@v1` — the 45 `f_*` features** | With `price_ohlcv@v1` that is **59 of §5.3's 61**. ★★ **Per-filing first, as-of join second** — the reverse silently nulls every multi-period feature because a 120-day window holds **three** filings, and the failure looks exactly like sparse data. ⚠ The join is `backward` on **`filing_date`**: `nearest` attaches a filing published *after* the date, and keying on `period_end` is worth **a quarter of hindsight per row**. New **FE-37** — *null-ness correlates with sector* (NVDA 37/45, WMT 32, **JPM 18**: a bank has no gross profit and no current/non-current split) | *Computing after the join* — 45 columns of null that validate, train, and read as a filer reporting nothing |
| 2026-08-27 | ★★ **`price_ohlcv@v1` — §5.3's 14 price features, and four legacy defects not carried** | D-02 published **two** features where the spec declared **61**; this closes the price third. ⚠ **Not a port:** the legacy reads `adj_close(T)` and `volume(T)` — neither knowable at the day-T open (FE-28) — and uses `+1e-9` where FE-14 wants null. **L5 D-16 closed** (Wilder's RSI). ★ **FE-34**: the inherited `macd_hist` printed **2007** for SNDK beside **3.1** for AAPL on one day, so a cross-sectional ranker would learn the price level; it is normalised now. ★★ **FE-5 had never been enforced** — `RangeViolationError` and AC-2.5 both existed and no code path evaluated a range | *Porting verbatim* — every value would look plausible and four of them would be wrong |
| 2026-08-23 | **Two features, not the "one feature" L3's B3 text names** | D-03's `ranked_quantity` is the **denormalised** return `z·σ·√h` (QA-58/QA-119), which needs a volatility estimate — and **a volatility computed inside D-03 would be a derived number outside D-02** (§1.2, FE-4). So it is a feature | Ranking on `z` alone — installs the low-vol tilt QA-58 exists to remove, and it is a seam that gets *more* expensive to move once a model depends on it |
| 2026-08-23 | The contract set is **Python, not `contracts/sets/*.yaml`** | FE-2's immutability is enforced on a **content hash**; a Python literal is diffed by git and typed by the dataclass, where YAML adds a parser and a schema between the declaration and the check | YAML per §5.1 — earns its keep past a handful of features, and at two would only add a way to be wrong |
| 2026-08-23 | **`vol_21` declares a range; `mom_21` does not** | A standard deviation is non-negative by construction and 5.0/day is far outside any listed equity, so the bound catches a **units error** rather than a market. A 21-session return has no honest upper bound | Declaring `mom_21 ∈ [−1, 5]` — an invented threshold that fires on a real 6× move. **CN-10: an admitted absence beats a fabricated bound** |
| 2026-08-23 | `mom_21` is **open-to-open**, both ends on the same field | D-08 §5A decides at the open, and a `close→open` ratio carries a systematic intraday drift the model will fit (QA-71's argument, applied to a feature) | `close(t)/close(t−21)` — one full session of drift on every prediction, and **invisible in backtest because the backtest shares the anchor** |
| 2026-08-23 | The label machinery is **not built**, but FE-11's guard is | B3 has no D-04 to consume labels, so `build_labels` would be scope with no consumer. **The guard costs one regex and closes the directory boundary from the other side** | Building both — B4 scope in a B3 milestone. Building neither — leaves FE-11 as prose until B4 |

---

# 1. What this domain does, in one paragraph

D-02 answers *"give me the computed number — the same number, by the same formula, whoever is
asking and whenever they ask."* The B3 slice builds the machinery that makes that checkable: a
**named, versioned, immutable FeatureContract** with a `formula_id` per feature, and a panel that is
validated against it at the boundary. It computes two price features. It is responsible for being
right about **definition**, not about value.

# 2. The objects and how they flow

```text
   CT-7.1 price panel (D-07)
        │
        ▼
   BUILDERS[name](panel) ──► one Series per FeatureSpec
        │                         ▲
        │                    FeatureContract (CT-2.1)
        ▼                    name · version · content_hash
   build_panel ──► validate_panel ──► CT-2.2 panel ──► D-03
        ▲                                 │
   calendar_report (CT-7.7)          coverage() ──► CT-2.4
   FE-10 gate: PROCEED | HALT
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| `FeatureSpec` | `src/feature_engineer/contracts/spec.py::FeatureSpec` | the contract set | `validate_panel` | forever — immutable |
| `FeatureContract` | `src/feature_engineer/contracts/spec.py::FeatureContract` | `src/feature_engineer/contracts/sets/b3_minimal_v1.py` | D-03, D-04 | forever — FE-2 |
| CT-2.2 panel | `src/feature_engineer/contracts/panel.py` | `src/feature_engineer/ml_features/assemble.py::build_panel` | D-03 | per `(window, as_of, adj_as_of)` |

★ **The object that surprised me: `content_hash`.** A version number is what a reader trusts; the
hash is what the registry actually checks. Republishing `v1` with a changed `formula_id` is refused
by arithmetic, not by anyone remembering FE-2.

# 2a. ★ As-built — modules added after the B3 slice *(2026-08-27)*

§5.3 declares **61** features; the B3 slice published **two**. These modules close
**all 61** — the price 14, the fundamental 45 and Group C's 2.

| Module | What it is | ⚠ Open / known-limited |
|---|---|---|
| `src/feature_engineer/technical/price.py` | §5.3's 14 price features on the **FE-28 open anchor** | ★ **Not a port.** The legacy reads `adj_close(T)` and `volume(T)`, neither knowable at the day-T open. **L5 D-16 closed** — `rsi_14` is Wilder's |
| `src/feature_engineer/contracts/sets/price_ohlcv_v1.py` | the 14, declared | `macd_hist` carries a **78-session warm-up**; the EWM dependence is *bounded, not removed* (**FE-35**) |
| `src/feature_engineer/fundamental/items.py` | canonical line items + the **PIT as-of join** | ⚠ `direction="backward"` on **`filing_date`** — `nearest` attaches a filing published *after* the date; `period_end` is worth a quarter of hindsight |
| `src/feature_engineer/fundamental/ratios.py` | profitability, leverage, liquidity, efficiency, valuation, accruals | ⚠ **`f_roic` is PRE-TAX** — the tax tag is not ingested and a flat 21 % would be a fabricated input (CN-10) |
| `src/feature_engineer/fundamental/growth.py` | growth, margin trend, Piotroski, sector-z | ⚠ **Piotroski is 7 signals scored out of 7**, not 9 — two need inputs a bank never reports. *7/7 and 7/9 are different claims* |
| `src/feature_engineer/fundamental/build.py` | the orchestrator | ★★ **Per filing first, as-of join second.** The reverse silently nulls every multi-period feature: a 120-day window holds **three** filings |
| `src/feature_engineer/contracts/sets/fundamental_v1.py` | the 45 **+ Group C's 2**, declared from `build.FEATURE_NAMES` | ⚠ **Coverage is filer-dependent** — NVDA 37/45, WMT 32, **JPM 18** (**FE-37**) |
| `src/feature_engineer/fundamental/group_c.py` | `f_graham_number_ratio`, `f_moat_quant_score`, market cap | ★★ **FE-38**: a share count was divided by 100 with the money → market cap **100× too small**. **FE-39**: the inherited moat stability term spanned **0.95–0.99**, a 20 % weight on a near-constant |

## ⚠⚠ Open question carried to `L6-as-built-remaining.md`

**FE-37 — null-ness correlates with sector.** A bank has no gross profit and no
current/non-current split, so those nulls are *correct* (FE-14 forbids imputing
them) — but the **pattern** of nulls is a sector dummy arriving through the back
door. **FE-15 assigns the remedy to the consumer**; D-02's duty is to declare the
coverage, which `feature_coverage()` now does.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | require both PIT axes | `src/feature_engineer/ml_features/assemble.py::build_panel` | **FE-7/FE-8 before any work.** They fail differently — `as_of` is INV-1, `adj_as_of` is INV-2 | `AsOfRequiredError` |
| 1 | gate on the calendar check | `src/feature_engineer/ml_features/assemble.py::_require_cleared_window` | ★ **FE-10.** A window whose units changed partway through is not fixable downstream | `CalendarHaltError` |
| 2 | build each declared feature | `BUILDERS[name]` | One name, one builder — FE-4 has nowhere to hide a second definition | `KeyError` naming the spec |
| 3 | stamp the envelope | `src/feature_engineer/ml_features/assemble.py::build_panel` | FE-3 + FE-10: a panel that cannot name its contract or its clearing check is unauditable | contract validation |
| 4 | validate | `src/feature_engineer/contracts/panel.py::validate_panel` | ★ **After construction, not during.** Range and membership are properties of the finished frame | `Undeclared`/`Missing`/`RangeViolation` |

⚠ **Step 1 before step 2 is the ordering a rewrite would get wrong**, because building first and
checking after "works" — and produces a panel for a window the gate would have blocked.

# 4. ★ The mathematics

### `mom_21` — 21-session open-to-open return

| | |
|---|---|
| **Implemented in** | `src/feature_engineer/technical/momentum.py::mom_21` |
| **Formula** | ```python\nout = (now / then) - 1.0\nout[then <= 0] = pd.NA\n``` where `now = adj_open_minor`, `then = groupby("ticker").shift(21)` |
| **Units** | minor units ÷ minor units → **dimensionless** (FE-32, MO-8). ★ This is where the Money type is left, and it happens once |
| **Domain / range** | `then > 0`; otherwise `NA`. Unbounded above; bounded below at −1 only if a price can reach zero |
| **Why this form** | Both ends on `adj_open`: D-08 §5A decides at the open, and mixed anchors carry a drift the model fits |
| **Alternatives rejected** | See `src/quant/methods/entries/momentum.open_to_open_ratio.v1.md` — close-anchored, mixed-anchor and log-return forms, each with its reason |
| **Sensitivity** | Entirely the `adj_factor` (D-07). A missing split is a **10× error**, not a rounding one |
| **★ Worked example** | `adj_open(t−21) = 10000` ($100.00), `adj_open(t) = 11000` ($110.00) → `11000/10000 − 1 = 0.10` **exactly**. With 21 rows or fewer: `NaN`, never `0.0` |
| **Known-wrong** | ⚠ 21 **sessions**, not 21 calendar days. On a panel with gaps the lookback is a session count and the elapsed time varies |

### `vol_21` — realised daily volatility

| | |
|---|---|
| **Implemented in** | `src/feature_engineer/technical/momentum.py::vol_21` |
| **Formula** | ```python\nlog_ret = np.log(px / prev)\nout = log_ret.groupby(...).rolling(window, min_periods=window).std(ddof=1)\n``` |
| **Units** | log-return standard deviation, **per day** |
| **Domain / range** | `[0, 5)` declared. `min_periods=window` ⇒ `NaN` for the first 21 rows |
| **Why this form** | ⚠ **`min_periods` is the load-bearing argument** (PD-9). The pandas default emits a value from fewer observations, and a 21-day sd built from 3 days is indistinguishable in the output |
| **Alternatives rejected** | Yang-Zhang (QA-35) is the right answer and needs `adj_high`/`adj_low`, which **CT-7.1 does not carry** — deferred to B4 and recorded so the deferral is visible; EWMA/GARCH is a forecast, and forecasts are D-04's |
| **Sensitivity** | `SE(sd) ≈ sd/√(2(n−1)) ≈ 16 %` at n=21. **The ranking inherits that noise**, and §10.2 records it |
| **★ Worked example** | A constant-growth series has identical log returns every day ⇒ sd is **exactly 0.0** — a *measured* zero, distinguishable from the `NaN` of insufficient history |
| **Known-wrong** | Open-to-open, not close-to-close. Measured ratio 1.0006 over 130 tickers × 371,840 rows (D-03 §5.9.1c), so the substitution is near-free — but it is a HOUSE VARIANT and is declared as one |

# 5. The logic decisions

| Decision | Where | What it does | Why this way | What it would take to change it |
|---|---|---|---|---|
| Label detection is by **name prefix/suffix** | `src/feature_engineer/contracts/spec.py::LABEL_MARKERS` | rejects `fwd_*`, `label_*`, `target_*`, `*_ahead` | The directory boundary cannot see a spec hand-written in the wrong file; the name is what a reader would also use | one tuple — but a label that evades all four markers evades the guard (§10.1) |
| Input namespaces are **allow-listed** | `src/feature_engineer/contracts/spec.py::ALLOWED_INPUT_NAMESPACES` | six namespaces; anything else raises | FE-21 is a trust decision, so widening it should require reading the comment above it | one tuple; the analyst list is named separately so the error can say *which* seat leaked |
| `validate_panel` **returns** the frame | `src/feature_engineer/contracts/panel.py` | `df = validate_panel(df, c)` | Makes the check impossible to leave out by accident at a call site | — |
| A range of `None` means **unbounded**, not unchecked | `src/feature_engineer/contracts/panel.py` | skips the range check | INV-3 enforces *declared* ranges; an undeclared one is an admitted absence (CN-10) | — |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Who reads it | Changing it affects |
|---|---|---|---|---|
| `LOOKBACK_SESSIONS` | `src/feature_engineer/technical/momentum.py` | 21 | `mom_21` | ⚠ a **policy choice in code** (CN-3) — matched to HorizonSet v1's `h1m`, and it should move to config when D-08 supplies a manifest |
| `VOL_WINDOW_SESSIONS` | same | 21 | `vol_21` | as above |
| the contract in force | `src/feature_engineer/contracts/sets/b3_minimal_v1.py` | `b3_minimal@v1` | every consumer | the whole panel; a version bump invalidates every model trained on the old one |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | **CT-7.1** price panel | D-07 | `KeyError` naming the missing CT-7.1 columns |
| in | **CT-7.7** calendar report | D-07 | `CalendarHaltError` — and `None` is a halt, not a skip |
| out | **CT-2.2** panel | D-03 | `validate_panel` raises |
| out | **CT-2.4** coverage | D-03, D-09 | ★ NaN-but-present counts as missing |

# 8. Failure behaviour

| Failure | Detected where | Behaviour |
|---|---|---|
| `as_of` / `adj_as_of` omitted | `build_panel` | `AsOfRequiredError` |
| calendar HALT, or no report | `_require_cleared_window` | `CalendarHaltError` — propagates, never worked around |
| undeclared or missing column | `validate_panel` | raises; **never filters** (PD-18) |
| value outside a declared range | `validate_panel` | `RangeViolationError` |
| a label name in a contract | `FeatureSpec.__post_init__` | `LabelInContractError` |
| an analyst-derived input | `FeatureSpec.__post_init__` | `AnalystDerivedInputError` |
| insufficient history | the builders | **`NaN`**, counted in coverage — never 0.0, never imputed |

# 9. What this domain deliberately does NOT do — and what B3 leaves unbuilt

| Not in the B3 slice | When |
|---|---|
| the DCF, margin of safety, reconciliation — ★ **carrying D-19** | B4 (FE-18: it moves VERBATIM, and D-19 is fixed only after the reality probe) |
| moat, quality gates — ★ **and the FE-20 duplicate-definition decision** | B4 |
| the 45 `f_*` fundamentals, Piotroski, accruals, sector-relative z | B4 |
| `rsi_14` and the other 12 price features — **carrying D-16** | B4 |
| `build_labels` / CT-2.3 | B4, with D-04. FE-11's **guard** is here; the machinery is not |
| caching (QF-4) | leaning recompute; the parquet is an artifact, not a cache |
| judging anything | ✗ never — *"trading 34 % below fair value, therefore BUY" is D-01* |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — label detection is nominal** | ⚠ medium | A forward-looking feature named `momentum_next_month` passes every guard. **The directory boundary (FE-11) is the real defence and B3 has only one directory** | new — no ID |
| **10.2 — `vol_21` at n=21 is a noisy estimate** | ⚠ medium | `SE(sd) ≈ 16 %`, and it multiplies the ranked quantity directly. **The ranking is noisier than a reader of a 6-decimal figure would assume** | QA-58's own caveat |
| **10.3 — the lookback is a policy choice in code** | low | CN-3. It reaches no RunManifest because D-08 does not exist | CN-3, OR-9 |
| **10.4 — no `coverage` floor is enforced** | low | `coverage()` measures; nothing refuses on it. F1 AC-1.15's gate is D-09's and D-03's, and B3 has one name at 100 % | FE-27, RP-12 |
| **10.5 — `pit_class: C` is declared and unchecked** | ⚠ medium | The FeatureSpec says the inputs are restated data; nothing verifies the panel it was handed actually carries an `adj_as_of`. **The two contracts agree by convention here, not by assertion** | new — no ID |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_feature_engineer_b3.py` — 21 cases, each docstring naming its `AC-2.n` |
| 2 | ★ **Break it and confirm red** | In `src/feature_engineer/contracts/panel.py`, change the `missing` check to filter instead of raise. `test_ac_2_2_a_declared_feature_absent_from_the_panel_fails` must fail — **that one word is the whole of D-17** |
| 3 | The worked example (§4) reproduces | `test_method_known_answer_mom_21` and `test_method_known_answer_vol_21_constant_growth_is_exactly_zero` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **Partly.** The features are checked against *arithmetic* known answers, not against a market. Their inputs (`adj_open`) **are** checked against live FMP by D-07's §6A.4 probe, so the input is externally verified and the formula is not |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-feature-engineering.md` | FE-1…FE-33, CT-2.1…2.4, §8's four inherited defects |
| `sdd/design/rel6_design/L1-data-engine.md` | CT-7.1 (`adj_open_minor`, DE-42), CT-7.7 (`report_id`), §6A |
| `sdd/design/rel6_design/L1-quantitative-analysis.md` | **QA-58/QA-119** — why `vol_21` exists at all; QA-71's anchor |
| `sdd/design/rel6_design/L3-build-sequence.md` | B3's scope, **BS-10** |
| `sdd/specs/constitution.md` | INV-1, INV-2, **INV-3** (the ranges), INV-4 |
