# Blueprint — D-04 Model Training & Inference

> **Governing spec:** [`../design/rel6_design/L1-model-training.md`](../design/rel6_design/L1-model-training.md)
> **Seat:** SEAT-3's machinery, not its judgement · **Path:** `src/models/`

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-10-20 | ★★ **D-04 is complete when it works, not when its model passes** | MT-68 / F12 `D16` (Victor, 2026-10-11, option Ⓐ): *"this D-04 ML model may never process any skills with my limited computing and news capacity, as well as the nature of predicting future stocks' ranking."* The gates keep measuring, unchanged | *Lowering the thresholds so fit 4 passes* (Ⓑ) — PG-2; the bar was fixed before the result; four fits on one decade are four draws |
| 2026-10-09 | ★★ **A refused model may rank the card — designated, labelled, revocable** | MT-67 / OR-58: the momentum rule measured walk-forward IC −0.008, fit 4 +0.030 on the same dates; `card_informational.json`, never `promotion.json` | *Keep the rule* — the worse ranking; *promote with an override* — MT-17 forbids it |
| 2026-10-09 | ★★★ **The shadow trial — scored on the future, never served** | MT-64…66: the only evidence that cannot be tuned. Frozen artifact, pre-registered criterion, write-once snapshots ≥ 21 sessions apart, never writes the event store (`DX-167`) | *Daily snapshots* — overlapping 21-day labels add ~nothing at 21× the cost |
| 2026-10-08 | ★★ **Fit on each day's return rank; grade on the raw return** | MT-59: raw returns spend the trees on the market's monthly swing, which a ranking cannot use. The card orders by ẑ, the ordering the gates measured (MT-60, `DX-165`) | *Percentile target* — inference needs a centred score |
| 2026-10-08 | ★★★ **Splits and dividends are applied to the panel and the labels** | MT-61 (`DX-166`): fits 1–3 read every split as a crash; NVDA had 42 labels below −50 %, after the fix 0 | — |
| 2026-10-07 | ★★★ **Fundamentals are replayed per filing date** | FE-40 (`DX-159`): one read at today made every training row's fundamentals ~1 year stale (13 % matched a true PIT read; after: 798/798) | — |
| 2026-10-06 | ★★ **Training holds for review; it never promotes itself** | MT-52: before, a passing run wrote `promotion.json` and the next card used it with no human step | — |
| 2026-08-26 *(zoo)* | ★★ **The required gate set has one owner, and it is D-03's** | **MT-50**, found by running the chain end to end. MT-19 already said the gates are D-03's — but neither spec **enumerated** them, so D-04 declared its own list with a `stability` gate D-03 never produces, and **promotion refused every artifact**. ★ **MT-18 caught it**, which is the rule working: a gate never run is indistinguishable from one that failed | *Adding `stability` to D-03* — it invents a gate to satisfy a list, which is the tail wagging the protocol |
| 2026-08-26 *(zoo)* | ★ **One family, with its reason recorded** | **MT-36**: retirement is the **default**; the legacy tree carries **nine families, 2,736 LOC across 18 files, for one production horizon and ~250k rows**. MT-37 keeps the neural branch in D-10 until it beats the GBDTs *at 1m on D-03's protocol* — a comparison nobody has run | *Porting the nine* — it is maintenance surface presented as optionality |
| 2026-08-26 *(zoo)* | ⚠ **Determinism is switched on explicitly** | LightGBM's defaults are **not** reproducible: without `deterministic`, `force_row_wise` and single-threading, repeated fits differ in the low bits. ★ INV-2 is a property of **the whole invocation** (D-08 OR-10), so a family that is *usually* reproducible fails it | *Trusting the seed alone* — it is necessary and not sufficient, and the failure is invisible until two artifact ids differ |
| 2026-08-26 *(zoo)* | ★ **The estimator refuses to reorder or narrow its columns** | An estimator that quietly fixes up a mismatched frame is **`_select_features` reappearing inside the zoo**. Column choice is the parity gate's business (MT-6), and the family must not be able to defend itself against D-17 — because doing so would hide it | *Reindexing to the fitted names* — convenient, and it silently restores the exact behaviour §6.1 exists to delete |
| 2026-08-25 | ★★ **Parity CHECKS; it never filters** | **MT-5…MT-11**, closing **D-17**. *Filtering answers "what can I score with?"; checking answers "am I allowed to score at all?"* — **the first always succeeds, so it cannot warn.** The legacy `_select_features` filtered, its empty-metadata branch scored on every remaining column, and `main_inference` fell back to 14 of 61 features under a name that read like the model's own | *Adding a check to the filter* — MT-5 says the fix is **deleting the second code path**, not guarding it |
| 2026-08-25 | ★★ **`nan_only` is a first-class field on the parity report** | **MT-7 / D-17's invisible half.** The `f_*` merge is `how="left"`, so an unmatched name keeps its row with **all 47 fundamental columns present and entirely NaN**. The columns exist, the filter passes, and the GBDTs consume NaNs natively and return an ordinary-looking score. **7 of 13 watchlist names, measured.** ★ It must be visible **without inference** | *Relying on the coverage fraction alone* — it aggregates, and the point is to name the columns |
| 2026-08-25 | ★★ **The estimator is injected** | MT-35 puts model families in the zoo, each needing a MethodEntry; the **protocol** is D-04's. ★ A two-line stand-in exercises every gate without a GBDT, which is what makes D-18's guards testable at all | *Importing LightGBM here* — it welds the protocol to one family and makes the gates untestable without it |
| 2026-08-25 | ★ **`artifact_id` excludes `evaluation_result_id` from its hash** | The id **is** the hash, and the evaluation is stamped *after* the model exists. Including it would change the id of a model that did not change | *Hashing the whole manifest* — it makes promotion mutate the artifact's identity |
| 2026-08-25 | ★ **Below-coverage tickers stay in the ranking** | **MT-11.** They cannot be the actionable pick (F1 AC-1.15, INV-6), but dropping them **changes the cross-section the ranking is computed over** — a different defect wearing a safety label. ⚠ If *every* curated name is excluded the run raises rather than picking one anyway | *Filtering them out* — quietly re-ranks the survivors |
| 2026-08-25 | ★ **`coverage()` treats an ABSENT column as missing** | ⚠ Found by a D-04 test: it indexed declared columns directly and raised a bare `KeyError`, losing the contract id. Same shape as D-07's `validate_fundamental_panel` (v0.8.0), same fix | *Catching it in parity* — the defect is in the coverage primitive, and every caller would need the same guard |

# 1. What this domain does, in one paragraph

D-04 fits a model, proves it may be used, and scores with it. ★ **Everything is a
property of the artifact**, so the artifact carries a *versioned feature
contract*, a *decision anchor*, an *adjustment state* and the protocol it was
fitted under — enough to make those properties checkable rather than assumed.

# 2. The objects and how they flow

```text
   D-02 CT-2.1 contract ──┐
   D-02 CT-2.2 panel  ────┼──► fit() ──► ModelArtifact (CT-4.1)
   D-02 CT-2.3 labels ────┘              artifact_id = content hash
        (available_at, decision_anchor)         │
                                                ▼
   D-03 BacktestResult ──► promote() ──► PromotionRecord (CT-4.3) ──► Registry
                              every gate PASS                          │
                                                                       ▼
   D-08 CT-8.1 run_manifest.decision_anchor ──► check_parity ──► score()
                                                 (CT-4.2)          │
                                                  HALT ◄───────────┘
                                                                   ▼
                                              arbitrate: 1m nominates, 1w may
                                              delay or veto — never nominates
```

# 2a. ★ As-built — the training run *(2026-08-27)*

⚠ **`fit()` existed since B6 and had never been called in production.** Every
piece was built — `TrainSpec`, the zoo, D-03's folds and gates, `promote`, the
`Registry` — and **nothing joined them**, so `_incumbent_model()` returned `None`
and the daily card was ranked by a two-feature formula.

| Module | What it is | ⚠ Open / known-limited |
|---|---|---|
| `src/models/train/run.py` | universe → prices → facts → panel → labels → folds → fit → gates | ⚠ **AB-9**: supplies a `_Report` stub asserting `PROCEED_WITH_FLAGS`; **FE-10 requires a real calendar check** and a ten-year window over 500 names is where an unhandled action hides |
| `src/models/train/__main__.py` | `python -m src.models.train` — ★ **separate from the daily run (P7)** | a fit is not a daily job; the daily run *consumes* an artifact and never makes one |
| `src/models/artifact/store.py` | `.state/models/<artifact_id>/`, append-only | ★ `promotion.json` is written **only** on a pass — **its absence is the refusal** (MT-17) |

# 2b. ★ As-built — the selection model, end to end *(2026-10-20)*

**Status: functionally complete, skill unproven** (MT-68). Operator's page: [`src/models/README.md`](../../src/models/README.md).
⚠ §2a and §10 below are the 2026-08 record; where they disagree with this section, this section is current.

```text
ingest events (D-07, by hand) ─► python -m src.models.train
  EDGAR facts ─► FMP prices (+1 retry pass, DE-80) ─► calendar check (HALT stops, MT-54; 0 checked refused, MT-57)
  ─► GICS sectors (DE-77) ─► splits/dividends applied (DE-78; conflicting names out by name, DE-79)
  ─► 61-feature panel, fundamentals replayed per filing date (FE-40) ─► 21-day open-to-open labels
  ─► LightGBM on xs_gauss (MT-59) ─► purged k-fold (reported) + walk-forward (gates, F12 D14)
  ─► simulation (cost_survival) ─► breadth: residual ρ after SPY (F12 D12/D13) ─► 3 gates
  ─► .state/models/<id>/ held for review (MT-52)
python -m src.models.promote <id> [--approve | --card-informational]   (MT-17, MT-67)
python -m src.orchestration.entrypoint  ─► ranker: promoted > designated refused > rule (OR-58)
python -m src.models.shadow {start,record,score,status}               (MT-64…66, frozen on fit 4)
```

| Module | What it is |
|---|---|
| `src/models/train/__main__.py` | the CLI and stage order (heartbeat, MT-53); prints every gate and the artifact id |
| `src/models/train/run.py` | prices, PIT fundamentals replay, panel, labels, both out-of-sample protocols, external breadth |
| `src/models/promote.py` | the review / `--approve` / `--card-informational` CLI |
| `src/models/infer/rank.py` | orders the card by ẑ (MT-60); `sigma_scaled` reported only |
| `src/models/shadow/` | the live trial: `trial.py` (start), `record.py`, `score.py` |

| Fit | Change | Walk-forward IC · t | Verdict |
|---|---|---|---|
| 1 `c30170a7` | baseline after the PIT fix | (k-fold 0.0227 · 2.16) | refused |
| 2 `26d118d2` | real GICS sectors | (k-fold 0.0250 · 2.32) | refused |
| 3 `fde8fb5e` | `xs_gauss` target | 0.0325 · 2.70 | refused (split bug present) |
| **4 `8200ada7`** | splits/dividends applied — the clean fit | **0.0296 · 2.51** | **refused** (`ic_significance`, `breadth` IR 0.421); designated card ranker |

## ⚠⚠ Open questions carried to `L6-as-built-remaining.md`

★★ **AB-12 — the IC gate's standard error.** `corrected_se` is `√(h/((n−1)·T))`,
the SE **under the null of no skill**. QA-4 promises *"an autocorrelation-corrected
standard error"* and the formula contains **no autocorrelation correction**. On
the 500-name run the same IC gives **t = 4.94 (PASS)** on the null SE and
**t = 1.42 (fail)** on the realised dispersion — **3.5× apart, and this is the gate
promotion turns on.**

⚠ **Two gates cannot be evaluated at all, and both are D-03's**: `cost_survival`
needs a backtest (**MT-19: D-04 does not evaluate itself**) and `breadth` needs
QA-43's residual-correlation measure (**QQ-11**). Until both land, **no artifact
can be promoted by construction** — the rule working, not a gap.

# 3. The sequence — what actually executes

`fit` → anchor agreement → **`assert_no_lookahead` against `available_at`** →
join → feature presence → estimator → `_assert_fitted_not_defaulted` → manifest.
`score` → `assert_loadable_for_production` (MT-33) → **`check_parity` once, over
the whole batch** → predict → mark below-coverage names excluded.

# 4. ★ The mathematics

There is almost none, and that is the design. The only arithmetic D-04 owns is
the **label**: `value = (P[t+h] − P[t]) / P[t]` at the declared anchor, and
`available_at` = the real trading date h sessions ahead — ⚠ **not
`date + horizon_days`**, which lands on weekends. Everything else is a gate.

# 5. The logic decisions

| Decision | Rule |
|---|---|
| Parity runs **once, before scoring** | MT-8 — a check inside the scoring loop has already let the first rows through |
| Extra columns **warn**, and halt when contracts differ | MT-10 — an extra column means the panel came from a different contract |
| Ties in the ranking break on ticker | INV-2 — a ranking whose ties depend on dict order is not deterministic |
| `arbitrate` reads `timing` only to choose between *the selection's pick* and *no pick* | ★ MT-31 made structural: **no branch takes a name from the timing leg** |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Changing it affects |
|---|---|---|---|
| `MIN_FEATURE_COVERAGE` | `src/models/governance/parity.py` | `0.80` | Which names may be the actionable pick (MT-11). ⚠ **ADMITTED GUESS** (CN-10) — the spec names the rule and no number |
| `REQUIRED_GATES` | `src/models/governance/promotion.py` | 4 gates | What promotion demands. ★ **Not config** — they are D-03's gates, and adding one is a spec change |
| `SELECTION_HORIZON_DAYS` | `src/models/train/fit.py` | `21` | HorizonSet v1's 1m leg. ⚠ **Not tunable** — MT-30 fixes it |
| `retrain_cadence` | `src/models/governance/promotion.py::Registry` | first trading day monthly | MT-25 — ★ stated **here**, never implicit in a cron entry |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | `CT-2.1` contract · `CT-2.2` panel | D-02 | version mismatch ⇒ `ParityError` |
| in | **`CT-2.3` labels** | D-02 | mixed anchors or look-ahead ⇒ raises |
| in | `CT-8.1.decision_anchor` | D-08 | mismatch ⇒ `AnchorMismatchError`, hard |
| in | `BacktestResult` id | **D-03** | absent ⇒ promotion refused (MT-19) |
| out | `CT-4.1` artifact · `CT-4.2` parity · `CT-4.3` promotion · `CT-4.4` score | D-03, D-08, D-12 | — |

# 8. Failure behaviour

★ **Every failure here is a refusal to score or a refusal to promote.** Missing
or all-NaN features halt; a contract that cannot be resolved does not score; an
anchor mismatch is a hard gate; a non-finite optimisation result raises; a gate
that was never run is not a pass. ⚠ **No path produces a degraded artifact** —
*a fallback that yields a plausible artifact is the defect, not the safety net.*

# 9. What this domain deliberately does NOT do

| Not done | Why |
|---|---|
| Build features at inference | ★ **MT-5** — a second code path *is* the INV-4 violation, whether or not it currently agrees |
| Evaluate itself | **MT-19** — the gates are D-03's, run by D-03's code |
| Emit a verdict | **MT-28** — `rank_score` is an ordering; no BUY/HOLD/SELL, no conviction |
| Let the timing leg nominate | **MT-31/MT-32** — *"wait" is legal; "buy a different name" is not* |
| Load a 1q artifact into production | **MT-33**, enforced at load |

# 10. ⚠ Known-wrong, approximations, and open defects

| # | What | Severity | Detail | ID |
|---|---|---|---|---|
| 10.1 | ✅ *closed 2026-08-26 — `gbdt.lightgbm_rank.v1`* **No model family exists** | ⚠ **expected** | `src/models/zoo/` is empty and the estimator is injected. ★ **MT-35 requires a MethodEntry per family before promotion**, so a family cannot be added quietly — but nothing can be fitted for production until one is | MT-35 |
| 10.2 | ✅ *closed — D-03's backtest and gates run inside every training run (§2b)* **Promotion is unreachable — D-03 has no `BacktestResult`** | ⚠ **medium, and structural** | `promote()` demands a D-03 evaluation id and **D-03's evaluation protocol is not built** (`src/quant/` has horizons, methods, rank, nomination — no backtest). ★ The gate is correct and currently **cannot pass**, which is the honest state: MT-19 forbids D-04 evaluating itself | MT-17, MT-19 |
| 10.3 | ✅ *closed — purged k-fold + walk-forward, both in trading days since 2026-10-20 (F12 `D11`, `D17`)* **`fit` is single-fold** | ⚠ expected | No CPCV, no purging, no embargo — the protocol fields are *recorded* in the manifest and **not enforced by this code**, because the protocol is D-03's (QA-3, QA-37). ⚠ A manifest can therefore claim `purge_days: 63` that nothing applied | MT-17 |
| 10.4 | **Drift's input/output tests are crude** | low | A 50 % mean shift and a one-sd move. ⚠ **ADMITTED GUESSES** — MT-22 says the thresholds are D-03's, and D-03 has not set them, so these are placeholders that **report** rather than judge | MT-22 |
| 10.5 | **`select_best` is not wired into `fit`** | low | MT-13/MT-14's guards exist and are tested; **no optimisation loop calls them yet**, because tuning is D-03's protocol | MT-14 |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_models_b4.py` — 27 cases, each naming its `MT-n` |
| 2 | ★ **Break it and confirm red** | **(a)** In `src/models/governance/parity.py`, delete the `nan_only` computation. `test_mt7_present_but_entirely_nan_halts_the_run` must fail — ★★ **that is D-17**, and the columns exist so nothing else notices. **(b)** In `check_parity`, change contract equality to `<=` (subset). `test_mt6_parity_is_version_equality_not_subset_or_intersection` must fail — **subset is exactly what filtering does**. **(c)** In `src/models/train/fit.py`, delete `_assert_fitted_not_defaulted`. `test_mt13_a_non_finite_optimisation_result_raises` must fail — ⚠ **that is D-18(b)**: `-inf` adopted as a result while the phase reports PASS |
| 3 | The worked example (§4) reproduces | `test_mt48_available_at_is_materialised_not_computed` — 21 sessions is more than 21 calendar days |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ✏ *2026-10-20: four real fits on 510 names × 10 years (§2b), and a live shadow trial — the only external check that cannot be tuned.* ⚠ *(2026-08 text:)* **No, and it cannot be yet.** Every test fits a stand-in estimator on a synthetic panel. **Nothing has been fitted on the real universe**, because the panel builder needs D-07 prices for the full universe and promotion needs D-03's evaluation. ★ What *is* externally checked is the **label arithmetic** — `available_at` lands on real trading dates |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-model-training.md` | **§6** parity as a gate, **§7** the promotion gate, §10 HorizonSet v1; MT-1…MT-49 |
| `sdd/design/rel6_design/L1-feature-engineering.md` | **CT-2.1/2.2/2.3/2.4** — the contract, panel, labels and NaN-aware coverage |
| `sdd/design/rel6_design/L1-quantitative-analysis.md` | **QA-20** MethodEntry, QA-47 arbitration, the protocol D-04 records and D-03 owns |
| `sdd/design/rel6_design/L1-orchestration.md` | **CT-8.1** — the `decision_anchor` MT-42 asserts against |
| `sdd/design/rel6_design/L5-inherited-defects.md` | **D-17** and **D-18**, the two incidents this domain closes |
