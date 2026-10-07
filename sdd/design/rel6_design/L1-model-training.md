# L1: Domain Specification — Model Training & Inference (D-04)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-04 · **Seat:** SEAT-3
> **Path:** `src/models/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Depends on:** [`L1-feature-engineering.md`](L1-feature-engineering.md) (D-02) ·
> [`L1-quantitative-analysis.md`](L1-quantitative-analysis.md) (D-03) ·
> [`L1-data-engine.md`](L1-data-engine.md) (D-07)
> **Prior art:** `pipeline/ohlcv/models/**` (2,736 LOC, 18 files), `pipeline/training/**`,
> `pipeline/ohlcv/policy/sleeve_selector.py`, `pipeline/main_inference.py`,
> `constitution.md` **INV-1/INV-2/INV-3/INV-4**, P5, P7, `F0` §12 **D-17**, **D-18**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.6.0 | 2026-08-27 | Victor | ★★★ **MT-51 — FE-2's immutability was defeated by the one field that could have caught it.** Two artifacts with **59** and **61** features both declared `price_and_fundamental@v1`; `check_parity` compares name and version and passed them. ★ `FeatureContractRef` now carries `content_hash`, `check_parity` compares it, and `fundamental` is bumped to **v2** because its membership changed 45 → 47. ⚠ An absent hash reports **unverifiable**, never a match. |
| 0.5.0 | 2026-08-26 | Victor | ★★ **§11's zoo built with ONE family** — `gbdt.lightgbm_rank.v1`, its MethodEntry, and **MT-36's stated reason for retention** (the legacy tree carries nine families, 2,736 LOC, for one production horizon). ⚠ **Determinism is not LightGBM's default**: `deterministic`/`force_row_wise`/single-thread are required or INV-2 fails silently. ★★ **The chain now closes** — D-02 panel and labels → D-04 fit and parity → **D-03 evaluates** → D-04 promotes on D-03's verdict. ⚠ **MT-50**, found by running it: D-04 had enumerated its own gate list including a `stability` gate D-03 never produces, so **promotion refused every artifact**. MT-18 caught it; the list now has one owner. |
| 0.4.0 | 2026-08-18 | Victor | ⚠ **Seam audit: D-04 named neither contract it depends on.** **MT-48** names **CT-2.3** (the label set — and its `available_at` is what INV-1 is checked against); **MT-49** names **CT-8.1** (the RunManifest `MT-42`'s parity gate asserts against). A gate specified against an unnamed contract is aspirational, not implementable. |
| 0.3.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit: `MT-41` says `decision_anchor` travels in the model manifest — and `CT-4.1` did not carry it.** Added. **MT-42's hard gate (`manifest.decision_anchor == run_manifest.decision_anchor`) had nothing to compare**, so the check that catches a systematic, metric-invisible anchor mismatch was unimplementable as contracted. |
| 0.2.0 | 2026-08-18 | Victor | **§6.3 — the decision anchor is a parity property** (MT-41…MT-44): the anchor travels in the manifest and is a **hard gate** at inference, and **a pre-change model cannot be relabelled, only retrained**. **§8.1 — the retrain cadence** (MT-45…MT-47): first trading day of the month, inference-before-retrain, promotion next day, and **a retrain may promote nothing**. |
| 0.1.0 | 2026-08-16 | Victor | Initial draft, organised around the two defect classes this domain owns: **§6** train/inference parity (the D-17 class — *a guard that filters is not a guard that checks*) and **§7** the promotion gate (the D-18 class — *a fallback indistinguishable from a result*). Implements **HorizonSet v1** (§10), decided 2026-08-16. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

D-04 fits models. That is not what it is *for*.

> **"Guarantee that the artifact which ships is the artifact that was measured."**

Every defect this domain has produced is one failure: **the deployed thing was not the evaluated
thing.**

- **D-17** — models fitted on 61 features scored on 14, or on 47 columns that were present and
  entirely `NaN`. The evaluation was honest. The deployment was not the same object.
- **D-18** — blend weights measured across 8 folds, deployed as the untouched hard-coded defaults,
  while the gate reported **PASS** for over a month.

Neither was a modelling error. Both were **artifact-integrity** errors, and both were invisible
because the output kept its name: it was still called `rank_score`.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A MODEL IS NOT THE DELIVERABLE. A REPRODUCIBLE, PARITY-CHECKED, ║
║  PROMOTION-GATED ARTIFACT IS.                                    ║
║                                                                  ║
║  D-03 decides what "works" means and measures it.                ║
║  D-04's job is to make sure the thing that gets deployed is      ║
║  the thing D-03 measured — and to FAIL LOUDLY when it is not.    ║
║                                                                  ║
║  The hardest part of this domain is not fitting. It is           ║
║  refusing to ship.                                               ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.2 Position

```text
                    ┌────────────────────────────┐
                    │  D-09 Reporting            │  the slate, the card
                    └─────────────▲──────────────┘
                                  │ rank_score + coverage + arbitration
                    ┌─────────────┴──────────────┐
                    │  D-04 MODEL TRAINING &     │  SEAT-3  ← this spec
                    │       INFERENCE            │
                    │  train · promote · infer   │
                    │  parity · drift            │
                    └──▲────────▲─────────▲──────┘
                       │        │         │
        ┌──────────────┘        │         └──────────────┐
┌───────┴────────┐   ┌──────────┴─────────┐   ┌──────────┴─────────┐
│ D-02 Feature   │   │ D-03 Quant         │   │ D-10 Experiments   │
│ contract +     │   │ HorizonSet v1 +    │   │ P7-exempt          │
│ panel + labels │   │ protocol + gates   │   │ one-way: D-10 may  │
│                │   │ ★ JUDGES D-04      │   │ import D-04, never │
└────────────────┘   └────────────────────┘   │ the reverse (ST-2) │
                                              └────────────────────┘

        ✗ D-01 thesis / verdict — FORBIDDEN INPUT (INV-014)
```

## 1.3 Boundary

```text
╔══════════════════════════════════════════════════════════════════╗
║  IF IT HAS LEARNED PARAMETERS, IT IS D-04's.                     ║
║                                                                  ║
║  D-04 owns: the ranker, the timing model, hyperparameters,       ║
║        the blend weights (fitted => D-04's, even though they     ║
║        look like config — D-03 §1.3), rank_score, the model      ║
║        artifact, parity, drift, promotion.                       ║
║                                                                  ║
║  D-04 does NOT own:                                              ║
║        the features or the contract      -> D-02                 ║
║        the labels                        -> D-02                 ║
║        the horizon set                   -> D-03 (HorizonSet v1) ║
║        the evaluation protocol or gates  -> D-03                 ║
║        whether the number is good        -> D-03                 ║
║        what to do about it               -> SEAT-1               ║
║                                                                  ║
║  D-04 MAY NOT grade its own homework. The metric gate that       ║
║  decides whether a model ships is D-03's, and D-03 must not      ║
║  import D-04 (D-03 §3).                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

**Authority: RECOMMEND (L0 §3.1).** `rank_score` orders the universe. It carries no verdict.

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **ModelArtifact** | one fitted model | `artifact_id` (content hash) | **§5** — the unit of everything here |
| **Bundle** | a set of artifacts serving one role | `bundle_id` | e.g. the 1m selection leg |
| **TrainingRun** | one fit | `run_id` | inputs, config, seeds, outcome — reproducible |
| **ParityReport** | artifact × panel | `(artifact_id, panel_id)` | **§6** — pass/fail, never advisory |
| **PromotionRecord** | artifact → production | `(artifact_id, promoted_at)` | **§7** — the only path to production |
| **DriftReport** | artifact × window | `(artifact_id, window)` | **§8** — input, output, performance |
| **InferenceRun** | one scoring pass | `run_id` | artifact ids, panel id, coverage, arbitration |
| **rank_score** | ticker × date | `(ticker, date)` | the cross-sectional output. **Not a verdict** |

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── D-02   the feature CONTRACT (name + version), the panel, the labels
  ├── D-03   HorizonSet v1, the evaluation protocol, the metric gates
  └── D-07   indirectly, via D-02 — never directly

DEPENDED ON BY
  ├── D-09   rank_score, the slate, coverage, arbitration outcome
  └── D-05   exposure of a candidate

DOES NOT DEPEND ON
  ✗ D-01 — thesis, verdict, conviction (INV-014); grep-checkable
  ✗ D-10 Experiments — one-way (ST-2). D-10 may import D-04
  ✗ the LLM gateway (AP-5, ST-5)
  ✗ D-07 directly — features come through D-02 or they are not features
```

---

# 4. MODULE DECOMPOSITION

```text
src/models/
├── artifact/           # ★ the ModelArtifact: content hash, manifest, load/save — §5
├── train/
│   ├── fit.py          #   one fit, one artifact, fully recorded
│   ├── selection.py    #   the 1m selection leg (HorizonSet v1)
│   └── timing.py       #   the 1w timing leg — triple-barrier (D-03 §5.6 QQ-2)
├── infer/
│   ├── score.py        #   scoring — calls D-02's panel builder, never its own
│   └── arbitrate.py    #   QA-47: 1m nominates, 1w may delay/veto (P3)
├── governance/
│   ├── parity.py       # ★ INV-4 as a GATE — §6
│   ├── promotion.py    # ★ the only path to production — §7
│   ├── drift.py        #   input · output · performance — §8
│   └── registry.py     #   what is in production, and why
└── zoo/                #   model families; each needs a MethodEntry (D-03 QA-20) — §11
```

---

# 5. THE MODEL ARTIFACT

Everything in this domain is a property of the artifact, so the artifact has to carry enough to make
those properties checkable.

## 5.1 What must travel with a model

| Field | Why — and what breaks without it |
|---|---|
| `artifact_id` | content hash. Two artifacts that differ anywhere are different artifacts |
| **`contract_name` + `contract_version`** | ★ **not a list of column names.** A name list can be satisfied by coincidence; a version cannot. This is the D-17 fix |
| `horizon_set_name` + `version` + `horizon_id` | which of HorizonSet v1's legs this serves |
| `label_def_id` | which label, at which horizon |
| `adj_as_of` | the price-adjustment state (D-02 FE-8). Without it, a future split silently changes the training data |
| `training_window` (start, end, `as_of`) | |
| `seeds`, framework + version, hyperparameters | reproducibility |
| `uniqueness_weighting`, `purge_days`, `embargo_days` | the protocol it was fitted under (D-03 QA-3, QA-37) |
| `evaluation_result_id` | the D-03 BacktestResult that measured it |
| `code_version` | the commit that produced it |

| ID | Rule |
|---|---|
| **MT-1** | An artifact records its **feature contract name and version**, never a bare column list. *(Today `model_manager.py:91` stores `feature_names` as a list of strings and nothing else — the whole D-17 class follows from that one choice)* |
| **MT-2** | An artifact that cannot state its contract version **cannot be loaded for inference**. There is no "assume the current contract" |
| **MT-3** | Artifacts are **immutable**. Retraining produces a new `artifact_id`; nothing is updated in place |
| **MT-4** | Every artifact records the **`adj_as_of`** its training panel was built at. Two artifacts trained on "the same window" at different adjustment states are **different models** (D-02 FE-8, D-07 §5C.7) |

---

# 6. TRAIN/INFERENCE PARITY — INV-4 as a gate

## 6.1 The defect this section exists to close

`ModelBundle._select_features` (`model_bundle.py:80–84`):

```python
def _select_features(self, df):
    if self.feature_names:
        cols = [c for c in self.feature_names if c in df.columns]   # ← FILTERS
        return df[cols]
    return df.drop(columns=[c for c in ("date","ticker") if c in df.columns])  # ← WORSE
```

Three failures in five lines:

1. **It filters where it must check.** A model fitted on 61 features silently scores on whatever
   subset happens to be present.
2. **The empty-`feature_names` branch scores on *every remaining column*** — a model with unreadable
   metadata does not fail, it scores on an arbitrary frame.
3. **`main_inference.py:595` falls back to `MODEL_FEATURES`**, which is an alias for
   `PRICE_FEATURES` — **14 of the 61**. The fallback is named as though it were the model's features.

And the half a column-name check cannot see: the `f_*` merge is `how="left"` on ticker, so an
unmatched name **keeps its row with all 47 fundamental columns present and entirely `NaN`**. The
columns exist. The filter passes. The GBDTs consume the NaNs natively and return an ordinary-looking
score. Measured 2026-08-10: **7 of the 13 `practice_watchlist` names** — the majority of the
actionable path (INV-6).

```text
╔══════════════════════════════════════════════════════════════════╗
║  A GUARD THAT FILTERS IS NOT A GUARD THAT CHECKS.                ║
║                                                                  ║
║  Filtering answers "what can I score with?"                      ║
║  Checking answers  "am I allowed to score at all?"               ║
║                                                                  ║
║  The first always succeeds. That is the entire problem —         ║
║  it cannot fail, so it cannot warn.                              ║
╚══════════════════════════════════════════════════════════════════╝
```

## 6.2 Parity done properly

| ID | Rule |
|---|---|
| **MT-5** | ★ **There is no inference-side feature builder.** Inference calls **D-02's `build_panel()`** with the artifact's recorded contract version. A second code path *is* the INV-4 violation, whether or not it currently agrees. *(`main_inference._build_inference_features` is that second path, and INV-4 names it as the reference implementation — the invariant currently points at its own violation)* |
| **MT-6** | Parity is **contract-version equality**, not subset and not intersection. `artifact.contract_version == panel.contract_version` or the run halts |
| **MT-7** | **NaN-but-present counts as missing.** Parity consumes D-02's `coverage()` (FE / CT-2.4), which is NaN-aware. This is the half §6.1's filter was structurally blind to |
| **MT-8** | Parity runs **once, before scoring, over the whole batch** — never per-row, never warn-and-continue |
| **MT-9** | ★ **There is no fallback feature set.** No `MODEL_FEATURES` default, no "score on what's there", no empty-metadata branch. **An artifact whose contract cannot be resolved does not score** (P5) |
| **MT-10** | Parity is checked **both ways**. Missing features halt. **Extra** features warn — and escalate to halt if the contract versions differ, because an extra column means the panel came from a different contract |
| **MT-11** | A ticker below `min_feature_coverage` **stays in the ranking and cannot be the actionable pick** (F1 AC-1.15, INV-6). If *every* curated name is excluded, the run **raises** rather than picking one anyway |

> **MT-5 is the structural fix and the others are belt to its braces.** The residual accepted in
> D-17 — *"`run_inference:526` and `_select_features:80-84` still narrow silently"* — is closed by
> deleting the second code path, not by adding a check to it.

---

## 6.3 ★ The decision anchor is a parity property — **DECIDED 2026-08-18**

D-08 §5A takes the decision at the **day-T open**; D-03 §5.9 moves the label to
`open(T+h)/open(T) − 1`. For D-04 this is not a labelling detail — it is **the parity check that
would otherwise pass while being wrong**.

| ID | Rule |
|---|---|
| **MT-41** | ★ **`decision_anchor` travels in the model manifest** (CT-4.1) alongside the feature contract hash. A model records the anchor it was fitted on |
| **MT-42** | ★ **Inference asserts `manifest.decision_anchor == run_manifest.decision_anchor`** and **fails the run** on mismatch (D-08 OR-35, `ORC.CADENCE.ANCHOR_MISMATCH`). This is a **hard gate, not a warning** — an anchor mismatch is silent, systematic, and invisible in every metric the system computes |
| **MT-48** | ★ **D-04 trains on `L1-feature-engineering.md` **CT-2.3 Label set** — `(ticker, date, horizon_days, label_def_id, decision_anchor, value, available_at)`.** ⚠ *Added by seam audit: this spec named `label_def_id` in its manifest and **never named the contract that emits it**.* ★ **`available_at` is the field INV-1 is checked against** — it is materialised, not computed (FE-12), so a look-ahead is caught by comparison rather than by trusting arithmetic at each call site |
| **MT-49** | ★ **`MT-42`'s parity gate asserts against `L1-orchestration.md` **CT-8.1 RunManifest**.** ⚠ *The gate was specified before the manifest declared `decision_anchor`; naming the contract is what makes the assertion implementable rather than aspirational.* The manifest also supplies `config_hash`, `seed` and the input digests a re-run needs (OR-9) |
| **MT-43** | ★ A model trained before the anchor change **cannot be promoted** into an open-anchored pipeline. There is no migration path for a fitted model: the anchor is baked into its weights, so **it must be retrained, not relabelled** |
| **MT-44** | The parity report (CT-4.2) includes the anchor. A parity check comparing feature vectors while ignoring the anchor **verifies the wrong half of the contract** — §6.1's defect in a new location |

# 7. THE PROMOTION GATE — research → production

## 7.1 The defect this section exists to close

**D-18**, four failures with one signature — *a failure indistinguishable from a result*:

| | What happened |
|---|---|
| **(a)** | Optimiser workers built a `Backtester` without `feature_names`, fell back to `MODEL_FEATURES` (14), while each fold's models were fitted on 16–61. **Every candidate raised.** 8 of 8 folds failed on two separate runs a month apart — 112 errors, then 98 |
| **(b)** | With every candidate failing, `best_sharpe` stayed `-inf`, **the untouched defaults were adopted, and `phase3b` reported PASS** |
| **(c)** | Even once fixed, the producing branch was **unreachable**: `persist = not is_fold`, and the only caller passed `fold_id=i`. Nothing could ever write `policy_params.json` |
| **(d)** | `TrainingPipeline.train` wrapped the optimiser in `except Exception → warning`, **downgrading a P5 raise** |

Production ran `{rank 0.65, prob 0.35, return 0.0}` — the hard-coded fallback — while all 8 folds
independently chose `rank 0.50–0.60, prob 0.10–0.20`. **Production gave the classifier zero weight
where every fold gave it non-zero.**

## 7.2 Rules

| ID | Rule |
|---|---|
| **MT-12** | ★ **A default is never substituted for a fitted value.** If a fit fails, **no artifact is produced**. A fallback that yields a plausible artifact is the defect, not the safety net |
| **MT-13** | ★ **A non-finite or absent optimisation result raises.** `-inf`, `NaN`, or an empty candidate set is a failure, never a selection |
| **MT-14** | **A partial failure reports its count and is treated as suspect.** A winner chosen from a thinned field is biased even when the winner is real |
| **MT-15** | ★ **Every producing code path must be reachable and must be executed by a test.** D-18(c) is the rule's origin: a branch that cannot run is not a fallback, it is **dead code impersonating a feature** |
| **MT-16** | **A broad `except` that logs and continues is a P5 violation wearing a `try` block.** Exception handling may narrow scope; it may never downgrade severity |
| **MT-52** | ★★ **A training run never promotes on its own — it HOLDS for the fund manager's review** *(Victor, 2026-10-06)*. Training writes the artifact, its `evaluation.json` (every gate with its statistic) and a `pending_review` marker; **`promotion.json` is written only by `python -m src.models.promote <artifact_id> --approve`**, an explicit human act that shows the gate report first and still refuses unless every required gate PASSes (MT-17 — no override). ⚠ Before this, a passing training run promoted itself and the next daily run scored with it |
| **MT-17** | Production is reachable **only** through a `PromotionRecord` carrying: `artifact_id`, contract version, horizon set version, the **D-03 `BacktestResult` id**, every gate outcome, the protocol id, and who promoted it when |
| **MT-18** | **A gate result of `NOT_EVALUATED` is not a pass** (D-03 QA-17). Promotion requires explicit `PASS` on every required gate |
| **MT-19** | **D-04 does not evaluate itself.** The gates are D-03's, run by D-03's code, against D-03's protocol (§1.3) |
| **MT-20** | Promotion of anything originating in **D-10 requires a spec** (P7). An experiment's output does not become production by being good |

---

# 8. DRIFT & RETRAINING

Three kinds, and they are observable on very different timescales — which matters more under
HorizonSet v1 than it did at 1w.

| Kind | What moves | Latency | Use |
|---|---|---|---|
| **Input drift** | feature distributions vs the training window | immediate | early warning |
| **Output drift** | `rank_score` distribution, rank turnover | immediate | early warning |
| **Performance drift** | realised IC decay vs the evaluation | **≥ 21 trading days at 1m** | confirmation |

| ID | Rule |
|---|---|
| **MT-21** | All three are computed; **input and output drift are the early warnings, performance drift is the confirmation.** A retrain triggered on performance alone reacts a horizon late |
| **MT-22** | Drift thresholds are **D-03's** (they are metric gates). D-04 computes and reports; it does not set the bar |
| **MT-23** | ★ **A retrain is a promotion and passes the full §7 gate.** "It is only a refresh" is how an unevaluated artifact reaches production |
| **MT-24** | ★ **The retrain window must not contain data the evaluation claimed not to see.** Retraining on the most recent data and then reporting the prior evaluation is look-ahead with a maintenance label (INV-1) |
| **MT-25** | Retraining cadence is **stated in the registry**, not implicit in a cron entry. A model whose retrain is overdue is **reported stale**, never silently trusted |

---

## 8.1 The retrain cadence — **DECIDED 2026-08-18**

**Retrain fires on the first *trading* day of each month** (D-08 §5A.4, OR-37).

| ID | Rule |
|---|---|
| **MT-45** | ★ **Inference runs first on the incumbent; retrain runs after; promotion takes effect the next trading day** (OR-38). A model promoted at 10:05 and used at 10:06 has passed no gate — §7 exists precisely so that cannot happen |
| **MT-46** | ★ **A retrain that fails, or fails its §7 gate, leaves the incumbent in place** and says so loudly (OR-39). **Never a fallback to an ungated model** |
| **MT-47** | ★ **A retrain is permitted to promote nothing.** With HorizonSet v1's 1-month horizon, each monthly retrain adds only ~one newly-labelled month — on a two-year panel, ~4 % new rows — so the fit will usually barely move. **The value is in the gate, not the retrain**, and a cadence that assumes every retrain ships a model turns §7 into a rubber stamp |

# 9. INFERENCE

| ID | Rule |
|---|---|
| **MT-26** | Inference is **deterministic** given `(artifact_id, panel_id, as_of, adj_as_of)` — byte-identical `rank_score` (INV-2) |
| **MT-27** | Every `InferenceRun` records artifact ids, contract version, panel id, `as_of`, `adj_as_of`, the D-07 calendar-check id, the coverage report and the arbitration outcome |
| **MT-28** | `rank_score` is an **ordering, not a verdict**. It carries no BUY/HOLD/SELL and no conviction (L0 §3.1, INV-014) |
| **MT-29** | Inference **halts** on: parity failure (§6), a D-07 calendar `HALT` (D-07 §6A), or an unresolvable contract. It does not degrade to a partial score |

---

# 10. HORIZONSET v1 IN PRACTICE

> **Decided by Victor 2026-08-16** (`L1-quantitative-analysis.md` §5.6). D-03 owns the decision;
> D-04 implements it. This section is the implementation contract, not a re-litigation.

```text
  h1m  21d  SELECTION   ★ the only horizon that may nominate the daily pick
  h1w   5d  TIMING       may delay or veto — NEVER nominates
  h1q  63d  RESEARCH     D-10 only — never reaches a human-facing artifact
```

| ID | Rule |
|---|---|
| **MT-30** | **The selection leg is fitted at 1m.** No production ranker is fitted against `fwd_ret_1w`. *(Every currently deployed model is — see §12)* |
| **MT-31** | **The timing leg never nominates.** It may **delay** or **veto** a nomination and may never originate or substitute one (QA-47) |
| **MT-32** | ★ **The timing leg is a gate, so P3 binds it**: it may make an outcome **equal or more conservative**, never more aggressive. "Wait" is legal; "buy a different name" is not. *(QA-47's arbitration and P3's monotonicity are the same rule seen from two domains)* |
| **MT-33** | A **1q artifact may not be loaded by production inference** — enforced at load, not by convention |
| **MT-34** | Under stacked multi-horizon fitting, the **per-horizon loss weighting is explicit** (QA-46). Uniqueness weighting alone implies ≈ 12.6 : 1 toward 1w — **the horizon that was deliberately retired** |

---

# 11. MODEL ZOO GOVERNANCE

`pipeline/ohlcv/models/` holds **nine families**: LightGBM · XGBoost · CatBoost · linear ·
sklearn · FT-Transformer · TabM · sequence · plus the bundle machinery. **2,736 LOC across 18
files, for one production horizon and ~250k rows.**

| ID | Rule |
|---|---|
| **MT-50** | ★★ **The required gate set is D-03's and D-04 IMPORTS it — it is never re-declared here.** ⚠ *Added 2026-08-26, found by running the chain end to end:* **MT-19 already says the gates are D-03's**, but neither spec **enumerated** them, so D-04 declared its own list — including a `stability` gate D-03 never produces — and **promotion refused every artifact.** ★ **MT-18 is what caught it**, which is the rule working exactly as intended: a gate that was never run is indistinguishable from one that failed. ⚠ Two lists for one idea drift **the moment the second exists**, and adding a gate in D-03 must reach promotion without an edit here |
| **MT-51** | ★★★ **`CT-4.1`'s contract ref carries the CONTENT HASH, not only the name and version.** ⚠ *Measured 2026-08-27:* two promoted artifacts — one fitted on **59** features, one on **61** — **both declared `price_and_fundamental@v1`**, because Group C was added to `fundamental` without a version bump. `check_parity` compares name and version, so it **waved the difference through**. ★★ **D-02's `FeatureContract.content_hash` already exists and says why in its own docstring** — *"hashing the CONTENT rather than trusting the version number is what makes the rule mechanical: republishing v3 with a changed `formula_id` produces a different hash and is refused, **whatever the file says**"* — and MT-1's ref did not carry it. ⚠ An **absent** hash is reported as *unverifiable*, never as a match: artifacts fitted before this field must not silently pass the check it exists to make |
| **MT-35** | A model family in `src/models/zoo/` requires a **MethodEntry** (D-03 QA-20) — statement, reference, assumptions, known-answer test. **A family with no MethodEntry cannot be promoted** |
| **MT-36** | An unretained family is **maintenance surface, not optionality**. Retirement is the default; retention needs a reason recorded in the registry |
| **MT-37** | The **neural branch stays in D-10** until it beats the GBDTs **at 1m** on D-03's protocol (D-03 §5.5). Tree ensembles still outperform deep learning on typical tabular data, and this data has far lower SNR than those benchmarks |

**On the three-head bundle** (D-03 §9): all three heads are deterministic functions of one variable,
so the bundle is **one target under three losses**, not an ensemble over three views. D-03's
recommendation stands — adopt **Option 1** (reframe and document honestly) now, build **Option 3**
(quantile heads) next, because it moves the Discipline Card's stop and target **from LLM judgement
to deterministic computation** (D-01 §7 argues that is the least reliable output class in the
system).

| ID | Rule |
|---|---|
| **MT-38** | If a deterministic model produces a stop or target, **D-01 narrates it and may not alter it** (D-03 QA-27, DC-1, DC-5) |

---

# 12. WHAT IS TRUE OF THE LIVE SYSTEM TODAY

Recorded so the migration cannot mistake the current state for a compliant one.

| Fact | Consequence |
|---|---|
| **Every deployed model is fitted against `fwd_ret_1w`** | Under HorizonSet v1 they are fitted to a *timing* objective while being used for *selection*. **A retrain is required before 1m ships** — the decision's consequence #1 |
| The fitted blend `{rank 0.5, return 0.3, prob 0.2}` was fitted at 5 days | Must be refitted at 1m; and the 25-sweep rel5 3-c tuning with it |
| `feature_names` is a bare list; there is no contract version | MT-1 is a **rebuild**, not a rename |
| `_select_features` filters, and its empty branch scores on all columns | MT-5/MT-9; the file is `L4` class **REVIEW**, not VERBATIM |
| `main_inference._build_inference_features` is the second feature path | MT-5 deletes it. **INV-4 currently names it as the reference implementation**, so the constitution's own reference must be repointed at D-02 when this lands |

---

# 13. CONTRACTS

> **ID-collision notice.** `AC-4.k` / `CT-4.k` key `n` on **D-04**.
> **`sdd/specs/F4_data_plane/spec.md` issues `AC-4.1`…`AC-4.8` and `CT-4.1`/`CT-4.2` against live *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))*
> code.** Fourth live collision under the accepted convention (L0 §16.4). Always qualify.

## CT-4.1 — Model artifact manifest (JSON, beside the model)

```json
{
  "artifact_id": "sha256:…",
  "role": "selection", "horizon_set": {"name": "production", "version": 1}, "horizon_id": "h1m",
  "feature_contract": {"name": "all_features", "version": 3},
  "label_def_id": "fwd_return_vol_norm_21d",
  "decision_anchor": "open",                    // ★ MT-41/42 — asserted == RunManifest at inference
  "training_window": {"start": "2019-01-02", "end": "2026-06-30", "as_of": "2026-06-30"},
  "adj_as_of": "2026-06-30",
  "protocol": {"purge_days": 63, "embargo_days": 5, "uniqueness_weighting": true},
  "framework": {"name": "lightgbm", "version": "4.3.0"}, "seeds": {"numpy": 42, "lgbm": 42},
  "evaluation_result_id": "bt:…", "code_version": "git:…"
}
```

**`feature_contract` is a name and a version.** A manifest carrying a column list instead does not
load (MT-1, MT-2).

## CT-4.2 — Parity report (JSON) — the gate, not a log

`(artifact_id, panel_id, contract_match: bool, missing[], extra[], nan_only[], coverage_by_ticker,
verdict ∈ {PASS, HALT})`. **`nan_only` is a first-class field** — present-but-all-NaN is the D-17
case and must be visible without inference (MT-7).

## CT-4.3 — Promotion record (JSON, append-only)

`(artifact_id, promoted_at, promoted_by, backtest_result_id, gate_outcomes{}, horizon_set_version,
contract_version, supersedes)`. **Every gate outcome is `PASS`** — `NOT_EVALUATED` is not a pass
(MT-18).

## CT-4.4 — Inference run (JSON)

`(run_id, artifact_ids[], panel_id, as_of, adj_as_of, calendar_check_id, coverage_report_id,
arbitration{nominated_by, delayed_by, vetoed_by}, excluded[])`.

---

# 14. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `train(spec)` | `ModelArtifact` | spec pins contract, horizon, protocol, seeds |
| `check_parity(artifact, panel)` | `ParityReport` | **raises on HALT** — never advisory (MT-8) |
| `promote(artifact, backtest_result)` | `PromotionRecord` | the **only** path to production (MT-17) |
| `production_artifact(role, horizon_id)` | `ModelArtifact` | from the registry; 1q raises (MT-33) |
| `score(artifacts, tickers, as_of, adj_as_of)` | `ScoreResult` | parity-checked; halts, never degrades (MT-29) |
| `arbitrate(selection, timing)` | `ArbitrationResult` | 1m nominates; 1w may delay/veto (MT-31, MT-32) |
| `drift(artifact, window)` | `DriftReport` | input · output · performance (MT-21) |

---

# 15. BUSINESS RULES

| ID | Rule |
|---|---|
| **MT-1…MT-4** | The model artifact — §5 |
| **MT-5…MT-11** | Train/inference parity — §6 |
| **MT-12…MT-20** | The promotion gate — §7 |
| **MT-21…MT-25** | Drift & retraining — §8 |
| **MT-26…MT-29** | Inference — §9 |
| **MT-30…MT-34** | HorizonSet v1 — §10 |
| **MT-35…MT-38** | Zoo governance — §11 |
| **MT-39** | D-04 imports **no** analytical domain: not D-01 (INV-014), not D-03 (it is judged by it), not D-10 (ST-2). Features come from D-02 or they are not features |
| **MT-40** | Every artifact and every score records the **D-02 contract version, `as_of`, `adj_as_of`, and the D-07 calendar-check id** it was produced under |

---

# 16. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `MDL.ARTIFACT.NO_CONTRACT` | ERROR | manifest carries no contract version — will not load (MT-2) |
| `MDL.ARTIFACT.COLUMN_LIST` | ERROR | manifest carries a bare column list instead of a version (MT-1) |
| `MDL.PARITY.CONTRACT_MISMATCH` | ERROR | artifact and panel contract versions differ — **halt** (MT-6) |
| `MDL.PARITY.MISSING_FEATURE` | ERROR | a trained feature absent from the panel (MT-6) |
| `MDL.PARITY.NAN_ONLY` | ERROR | feature present but entirely null — **the D-17 case** (MT-7) |
| `MDL.PARITY.EXTRA_FEATURE` | WARNING | escalates to ERROR if contract versions differ (MT-10) |
| `MDL.PARITY.NO_FALLBACK` | ERROR | something requested a default feature set (MT-9) |
| `MDL.TRAIN.FIT_FAILED` | ERROR | fit failed — **no artifact produced**, no default adopted (MT-12) |
| `MDL.TRAIN.NON_FINITE_SCORE` | ERROR | optimiser returned `-inf`/`NaN`/empty — **the D-18 case** (MT-13) |
| `MDL.TRAIN.THINNED_FIELD` | WARNING | partial candidate failure; count reported, winner suspect (MT-14) |
| `MDL.TRAIN.UNREACHABLE_PATH` | ERROR | a producing branch has no executing test (MT-15) |
| `MDL.PROMOTE.NO_RECORD` | ERROR | production reached without a PromotionRecord (MT-17) |
| `MDL.PROMOTE.GATE_NOT_EVALUATED` | ERROR | a required gate is `NOT_EVALUATED` (MT-18) |
| `MDL.PROMOTE.SELF_EVALUATED` | ERROR | gates run by D-04 rather than D-03 (MT-19) |
| `MDL.HORIZON.RESEARCH_IN_PRODUCTION` | ERROR | a 1q artifact requested for production (MT-33) |
| `MDL.HORIZON.TIMING_NOMINATED` | ERROR | the timing leg produced a nomination (MT-31) |
| `MDL.ARBITRATE.LESS_CONSERVATIVE` | ERROR | arbitration made an outcome more aggressive (MT-32, P3) |
| `MDL.RETRAIN.STALE` | WARNING | retrain overdue — reported, never silently trusted (MT-25) |
| `MDL.RETRAIN.WINDOW_OVERLAP` | ERROR | retrain window includes data the evaluation excluded (MT-24) |

---

# 17. ACCEPTANCE CRITERIA

```text
ARTIFACT  (§5)
□ AC-4.1   An artifact manifest carries a contract NAME + VERSION, not a column list
□ AC-4.2   An artifact with no resolvable contract version will not load
□ AC-4.3   Retraining produces a new artifact_id; nothing mutates in place
□ AC-4.4   adj_as_of is recorded; two artifacts differing only in it are not equal

PARITY  (§6 — the D-17 class)
□ AC-4.5   Inference calls D-02's panel builder; no second feature-building path
           exists in src/models (MT-5, grep-checkable)
□ AC-4.6   A contract-version mismatch halts the run
□ AC-4.7   A feature present but entirely NaN halts — NOT silently scored (D-17)
□ AC-4.8   No fallback feature set exists; an unreadable manifest fails, never
           defaults to MODEL_FEATURES or to "all remaining columns"
□ AC-4.9   Parity runs once, before scoring, over the whole batch
□ AC-4.10  Extra features warn; they halt when contract versions differ
□ AC-4.11  A ticker below the coverage floor stays ranked but cannot be the
           actionable pick; all-excluded raises (F1 AC-1.15, INV-6)

PROMOTION  (§7 — the D-18 class)
□ AC-4.12  A failed fit produces NO artifact; no default is adopted
□ AC-4.13  A non-finite or empty optimiser result raises (best_sharpe = -inf)
□ AC-4.14  A partial candidate failure reports its count and flags the winner
□ AC-4.15  Every producing branch is executed by a test (the persist=not is_fold
           regression: a branch no caller can reach)
□ AC-4.16  A broad except that downgrades a raise to a warning fails review
□ AC-4.17  Production is unreachable without a PromotionRecord
□ AC-4.18  A required gate at NOT_EVALUATED blocks promotion
□ AC-4.19  Gates are executed by D-03 code; D-04 self-evaluation raises

DRIFT & RETRAIN  (§8)
□ AC-4.20  Input, output and performance drift are all computed
□ AC-4.21  A retrain passes the full promotion gate
□ AC-4.22  A retrain window overlapping excluded evaluation data raises
□ AC-4.23  An overdue retrain is reported stale on the artifact

INFERENCE & HORIZONS  (§9, §10)
□ AC-4.24  Same artifact + panel + as_of + adj_as_of => byte-identical rank_score
□ AC-4.25  Inference halts on parity failure or a D-07 calendar HALT
□ AC-4.26  rank_score carries no verdict and no conviction
□ AC-4.27  No production ranker is fitted against fwd_ret_1w (MT-30)
□ AC-4.28  The timing leg cannot nominate; attempting to raises
□ AC-4.29  Arbitration may only make an outcome equal or more conservative (P3)
□ AC-4.30  A 1q artifact requested for production raises

BOUNDARY & ZOO
□ AC-4.31  src/models imports neither src/fundamental (D-01) nor src/experiments (D-10)
□ AC-4.32  Every zoo family has a MethodEntry; one without cannot be promoted
□ AC-4.33  A deterministic stop/target is not altered by any downstream layer
□ AC-4.34  ★★ A training run whose gates all PASS writes the artifact and a pending_review
           marker and NO promotion.json; `src.models.promote --approve` promotes it only
           if every required gate PASSed (MT-52, MT-17)
```

---

# 18. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QT-1** | **Which zoo families survive?** | Nine families, one production horizon, ~250k rows. D-03 QQ-8 asks the same. Retirement is the default (MT-36); each survivor needs a MethodEntry |
| **QT-2** | Retraining cadence for the 1m selection leg? | At 1m, performance drift needs ≥21 days to observe, so calendar-triggered retraining is likely the base with drift as an accelerator. Interacts with QT-3 |
| **QT-3** | Does the retrain window roll, or expand? | Rolling adapts to regime; expanding maximises the effective N that D-03 §5.3b shows is already tight at 1m. **Probably expanding, given the power constraint** |
| **QT-4** | Where does the timing leg's triple-barrier model live — here or D-03? | The **labels** are D-02, the **fit** is D-04, the **evaluation** is D-03. Unusual only because the timing leg is judged on hit-rate-conditional-on-entry rather than cross-sectional IC (D-03 §5.6) |
| **QT-5** | **INV-4's reference implementation names `main_inference._build_inference_features`**, which MT-5 deletes | The constitution's own reference must be repointed at D-02's panel builder. **A constitution amendment**, so it is Victor's (constitution §5.3) |
| **QT-6** | Does `rank_score` keep its name once quantile heads land (D-03 §9.3 Option 3)? | A calibrated band is not a score. Renaming is cheap now and expensive later |
| **QT-7** | What is the coverage floor at 1m? | `min_feature_coverage: 0.80` was set for the 1w panel. The fundamental features move quarterly, so coverage behaves differently at a 21-day horizon |

---

# 19. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-04, §1.6, §3.1, INV-014 | domain definition, seat independence, RECOMMEND authority |
| `L1-feature-engineering.md` §5, §6.3, **FE-8**, CT-2.2, CT-2.4 | the contract parity asserts against; the panel builder MT-5 mandates; NaN-aware coverage |
| `L1-quantitative-analysis.md` **§5.6**, §7, §9, QA-17, QA-27, QA-46, QA-47 | **HorizonSet v1 (the decision §10 implements)**, the evaluation protocol and gates, the arbitration rule, the three-head review |
| `L1-data-engine.md` §6A, §5C.7 | the calendar check inference halts on; the `adj_as_of` MT-4 records |
| `L1-fundamental-analysis.md` §7 | why moving stop/target to a deterministic model (MT-38) matters |
| `sdd/specs/constitution.md` **INV-1/2/3/4**, P3, P5, P7 | look-ahead, determinism, ranges, **parity**, gate monotonicity, fail-loud, research exemption |
| `sdd/specs/F0_code_map/spec.md` §12 **D-17**, **D-18** | the two defect classes §6 and §7 are built on *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F1_disciplinary_report/spec.md` AC-1.15 | the coverage gate MT-11 inherits *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
