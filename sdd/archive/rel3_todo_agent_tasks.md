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

# Release 3 — Agent TO-DO List

This file is intended for an AI agent to implement. Each task is self-contained with
full context, file paths, acceptance criteria, and implementation notes.
No prior conversation context is assumed.

---

## Implementation Plan — Execution Sequence for AI Agent

**Read this section first.** It defines the stage sequence, dependency constraints,
parallelism opportunities, and verification gates. Do not start a stage until all
verification commands from the previous stage pass. Each stage is self-contained:
if a stage fails its verification, fix it before proceeding — do not carry forward
a broken state into the next stage.

---

### Dependency graph

```
Stage 0 (Quick Wins, parallel-safe)
  TO-DO 1 — Remove ETF tickers          [no deps, config only]
  TO-DO 5 — Flat $10 fee revert         [no deps, backtester only]

Stage 1 (Foundation, must complete before Stages 2–6)
  TO-DO 7 — Simplify main_train modes   [no deps; enables 8, 9, 10, 11]
  TO-DO 3 — Point-in-time scores panel  [no deps; enables 4, 11]
  (7 and 3 are independent — develop in parallel, integrate separately)

Stage 2 (Validation Gates, after Stage 1 TO-DO 7)
  TO-DO 9 — Dataset quality validator   [needs 7]
  TO-DO 10 — Feature matrix validator   [needs 7; integrate after 9]
  (develop in parallel; integrate 9 first, then 10, to preserve pipeline order)

Stage 3 (Feature Selection, after Stage 2)
  TO-DO 8 — Feature selection pipeline  [needs 7, 9, 10; integrates after both]

Stage 4 (Overlay Optimization, after Stage 1 TO-DO 3)
  TO-DO 4 — Threshold optimizer         [needs 3]
  TO-DO 6 — Slot filling                [needs 4; do not implement before 4 stabilises overlay]

Stage 5 (Orchestration, after Stages 1–4)
  TO-DO 11 — main_pipeline.py           [needs 3, 7, 8, 9, 10; benefits from 5, 6]

Stage 6 (Documentation, after Stage 5)
  TO-DO 2 — PlantUML architecture       [most accurate after Stage 5 finalises architecture]
```

---

### Stage summary table

| Stage | TO-DOs | Parallelism | Blocking prerequisite | Key output |
|-------|--------|------------|----------------------|------------|
| 0 | 1, 5 | Both in parallel | None | Clean config + correct fee |
| 1 | 7, 3 | Both in parallel | None | Simplified modes + scores panel |
| 2 | 9, 10 | Develop parallel, integrate 9→10 | Stage 1 (7) | Validation gates in main_train |
| 3 | 8 | Sequential | Stage 2 (9, 10) | Feature selection + reports |
| 4 | 4→6 | Sequential (4 before 6) | Stage 1 (3) | Stable overlay + slot filling |
| 5 | 11 | Sequential | Stages 1–4 (3,7,8,9,10) | Full pipeline orchestrator |
| 6 | 2 | Independent | Stage 5 | Architecture diagram |

---

### Stage 0 — Quick Wins

**Goal:** Risk-free cleanup. Zero chance of breaking existing tests.
Both TO-DOs touch isolated files with no cross-module dependencies.

#### Step 0a — TO-DO 1: Remove ETF tickers
- File: `config/settings.yaml`
- Action: remove `VOO` and `ONEQ` from `pipeline.tickers`; insert two
  `# TODO: add replacement ticker here` comment placeholders
- Verification:
  ```bash
  python -c "import yaml; d=yaml.safe_load(open('config/settings.yaml')); \
    assert 'VOO' not in d['pipeline']['tickers'], 'VOO still present'; \
    assert 'ONEQ' not in d['pipeline']['tickers'], 'ONEQ still present'; \
    print('OK:', len(d['pipeline']['tickers']), 'tickers')"
  ```

#### Step 0b — TO-DO 5: Flat $10 fee
- Files: `pipeline/ohlcv/backtest/backtester.py`, `config/settings.yaml`
- Action: replace proportional bps cost model with `FLAT_TRADE_FEE_DOLLARS = 10.0`;
  write `tests/test_flat_trade_fee.py`
- Verification:
  ```bash
  pytest tests/test_flat_trade_fee.py -v
  pytest tests/ -x -q   # full suite — zero regressions
  ```

**Stage 0 passes when:** both verification commands exit 0.

---

### Stage 1 — Foundation

**Goal:** Establish the structural changes that all later stages build on.
TO-DO 7 and TO-DO 3 are independent and can be developed in parallel by two
agents, but both must pass verification before Stage 2 begins.

#### Step 1a — TO-DO 7: Simplify main_train.py modes

This is the most structurally impactful change. After this step, the modes
`fundamental_full` and `fundamental_scorer` no longer exist. Every subsequent
stage assumes the new three-mode structure (`price`, `fundamental`, `both`).

- Files: `pipeline/main_train.py`
- Actions:
  1. Update `parse_args()` choices to `["price", "fundamental", "both"]`
  2. Collapse dispatch in `main()` to the new execution map (see TO-DO 7 spec)
  3. Add `--skip-etl` flag
  4. Each dispatch function must accept `run_dir: Path` parameter (required by TO-DO 11)
  5. Each dispatch function must return a `TrainingArtifacts`-compatible dict
     (even if `TrainingArtifacts` dataclass does not yet exist — return a plain dict
     with keys `ranker`, `regressor`, `classifier`, `selector`, `selected_features`)
  6. Update any tests that reference removed mode names
- Verification:
  ```bash
  python -m pipeline.main_train --mode price --help          # must work
  python -m pipeline.main_train --mode fundamental_full 2>&1 | grep "invalid choice"
  python -m pipeline.main_train --mode fundamental_scorer 2>&1 | grep "invalid choice"
  pytest tests/ -x -q
  ```

#### Step 1b — TO-DO 3: Point-in-time scores panel

Independent of TO-DO 7. Extends `FundamentalScorer` without touching `main_train.py`.

- Files: `pipeline/fundamental_analysis/models/fundamental_scorer.py`,
  `pipeline/fundamental_analysis/integration/overlay.py`, `pipeline/main_backtest.py`
- Actions:
  1. Add `score_panel()` method to `FundamentalScorer`
  2. Forward-fill to daily frequency; write `fundamental_scores_panel.parquet`
  3. Update `load_fundamental_scores()` in overlay.py to accept `as_of_date`
  4. Update `main_backtest.py` to pass `as_of_date=fold_start` per fold
  5. Verify backward compatibility: JSON snapshot path still works when panel absent
- Verification:
  ```bash
  python -c "
  import pandas as pd
  df = pd.read_parquet('data/fundamentals/fundamental_scores_panel.parquet',
                       engine='fastparquet')
  assert 'as_of_date' in df.columns
  assert 'filing_date' in df.columns
  assert (df['filing_date'] <= df['as_of_date']).all(), 'look-ahead violation'
  print('Panel OK:', df.shape)
  "
  pytest tests/ -x -q
  ```

**Stage 1 passes when:** both 1a and 1b verification commands exit 0.

---

### Stage 2 — Validation Gates

**Goal:** Add the two validation classes that sit at the entry of the training pipeline.
These must integrate at the correct sequential positions inside `main_train.py`:

```
main_train (--mode fundamental)
  │
  ├── load combined_features.parquet
  ├── TO-DO 9: DataQualityValidator.validate()    ← first gate
  ├── feature engineering
  ├── TO-DO 10: FeatureMatrixValidator.validate() ← second gate
  ├── TO-DO 8: FeatureSelectionPipeline.run()     ← third gate (Stage 3)
  └── model training
```

Develop TO-DO 9 and TO-DO 10 in parallel. Integrate them in order (9 first, then 10)
because they occupy adjacent positions in the pipeline and an integration conflict in
the wrong order would be hard to untangle.

#### Step 2a — TO-DO 9: Dataset quality validator

- New file: `pipeline/ohlcv/dataset/data_quality_validator.py`
- New file: `docs/data_quality_guide.md`
- Modify: `pipeline/main_train.py` — call `DataQualityValidator.validate()` after
  loading combined_features, before feature engineering.
  Pass `run_dir / "data_quality"` as `report_dir`.
- Verification:
  ```bash
  python -m pipeline.main_train --mode fundamental --skip-etl
  # Must produce: reports/<ts>/data_quality/data_quality_summary.json
  # Must produce: reports/<ts>/data_quality/data_quality_report.md
  ls reports/$(ls -t reports/ | head -1)/data_quality/

  # Inject a FAIL-HARD condition and verify abort:
  python -c "
  import pandas as pd
  from pipeline.ohlcv.dataset.data_quality_validator import DataQualityValidator
  df = pd.read_parquet('data/fundamentals/combined_features_for_fundamental_training.parquet',
                       engine='fastparquet')
  # Inject OHLC violation
  df.loc[0, 'high'] = df.loc[0, 'close'] * 0.5
  validator = DataQualityValidator({})
  report = validator.validate(df, train_cutoff_date='2022-01-01',
                               report_dir='/tmp/dq_test')
  assert report['fail_hard_triggered'], 'FAIL-HARD did not trigger'
  print('FAIL-HARD injection test: OK')
  "
  pytest tests/ -x -q
  ```

#### Step 2b — TO-DO 10: Feature matrix validator

Implement AFTER Step 2a is integrated into `main_train.py`. This ensures the
integration order (9 before 10) is established before 10 is wired in.

- New file: `pipeline/ohlcv/dataset/feature_matrix_validator.py`
- New file: `docs/feature_validation_guide.md`
- Modify: `pipeline/main_train.py` — call `FeatureMatrixValidator.validate()` after
  feature engineering, before feature selection.
  Pass `run_dir / "training" / "feature_validation"` as `report_dir`
  (use the nested path now to match TO-DO 11's folder structure).
- Verification:
  ```bash
  python -m pipeline.main_train --mode fundamental --skip-etl
  ls reports/$(ls -t reports/ | head -1)/training/feature_validation/

  # Inject leakage and verify abort:
  python -c "
  import pandas as pd, numpy as np
  from pipeline.ohlcv.dataset.feature_matrix_validator import FeatureMatrixValidator
  df = pd.read_parquet('data/fundamentals/combined_features_for_fundamental_training.parquet',
                       engine='fastparquet').dropna(subset=['rank_label_1w'])
  # Inject near-perfect label correlation
  df['leaked_feature'] = df['rank_label_1w'] + np.random.normal(0, 0.01, len(df))
  validator = FeatureMatrixValidator({})
  report = validator.validate(df, label_col='rank_label_1w',
                               report_dir='/tmp/fmv_test')
  assert report['fail_hard_triggered'], 'FAIL-HARD did not trigger on leakage'
  print('Leakage injection test: OK')
  "
  pytest tests/ -x -q
  ```

**Stage 2 passes when:** both verification sequences exit 0 and the pipeline order
in `main_train.py` is DataQualityValidator → feature engineering → FeatureMatrixValidator.

---

### Stage 3 — Feature Selection

**Goal:** Add the multi-stage feature selection pipeline between FeatureMatrixValidator
and model training. This stage produces the feature selection reports and a
`selected_features.json` that feeds the final model training.

#### Step 3a — TO-DO 8: Feature selection pipeline

- New file: `pipeline/ohlcv/dataset/feature_selection_pipeline.py`
  (contains `NaNVarianceFilter`, `CorrelationFilter`,
   `PermutationImportanceSelector`, `AnyModelUnionSelector`,
   `FeatureSelectionPipeline`)
- Modify: `pipeline/ohlcv/dataset/feature_selector.py` — add `mode: "pipeline"`
  that delegates to `FeatureSelectionPipeline`
- Modify: `pipeline/main_train.py` — call `FeatureSelectionPipeline.run()` after
  FeatureMatrixValidator, before model training.
  Pass `run_dir / "training" / "feature_selection"` as `report_dir`.
- Modify: `config/settings.yaml` — add `features.mode: "pipeline"` section
- Verification:
  ```bash
  python -m pipeline.main_train --mode fundamental --skip-etl
  # Must produce all feature selection report files:
  ls reports/$(ls -t reports/ | head -1)/training/feature_selection/
  # Verify selected_features.json:
  python -c "
  import json
  from pathlib import Path
  rdir = sorted(Path('reports').iterdir())[-1]
  sf = json.load(open(rdir / 'training/feature_selection/selected_features.json'))
  assert len(sf['selected_features']) > 0
  assert len(sf['selected_features']) <= 58
  # Verify none of the known-sparse features survived
  assert 'f_interest_coverage' not in sf['selected_features'] or \
    sf.get('dropped_stage1_nan') and 'f_interest_coverage' in sf['dropped_stage1_nan']
  print('Selected:', sf['n_selected'], 'features')
  "
  # Verify mode=default and mode=importance still work (backward compat):
  python -c "
  from pipeline.ohlcv.dataset.feature_selector import FeatureSelector
  sel = FeatureSelector({'features': {'mode': 'default'}})
  feats = sel.select()
  assert len(feats) == 14, f'Expected 14, got {len(feats)}'
  print('mode=default backward compat: OK')
  "
  pytest tests/ -x -q
  ```

**Stage 3 passes when:** `selected_features.json` is produced with a non-empty list,
known-sparse features are correctly dropped, backward-compatible modes still work,
and all existing tests pass.

---

### Stage 4 — Overlay Optimization

**Goal:** Empirically calibrate the fundamental overlay thresholds (TO-DO 4),
then implement the slot-filling logic that relies on a stable overlay (TO-DO 6).
These must be done in order: implementing slot filling before the overlay thresholds
are stable creates a moving-target integration problem.

#### Step 4a — TO-DO 4: Threshold optimizer

Prerequisite: Stage 1b (TO-DO 3) must be complete — the optimizer uses
`fundamental_scores_panel.parquet`.

- New file: `pipeline/fundamental_analysis/models/threshold_optimizer.py`
- Modify: `pipeline/main_train.py` — add `--mode optimize_thresholds` dispatch
- Modify: `pipeline/fundamental_analysis/integration/overlay.py` — update
  `_resolve_thresholds()` to load `optimal_thresholds.json` if it exists
- Ensure `ThresholdOptimizer` writes to `report_dir` passed by caller (not hardcoded)
- Verification:
  ```bash
  python -m pipeline.main_train --mode optimize_thresholds
  # Must produce:
  ls data/fundamentals/threshold_search_results.csv
  ls data/fundamentals/optimal_thresholds.json
  python -c "
  import json
  t = json.load(open('data/fundamentals/optimal_thresholds.json'))
  assert t['downgrade_quality_max'] < t.get('warn_quality_max', 1.0), \
    'Threshold ordering violated'
  print('Thresholds valid:', t)
  "
  pytest tests/ -x -q
  ```

#### Step 4b — TO-DO 6: Post-downgrade slot filling

Implement only after TO-DO 4 is verified and `optimal_thresholds.json` exists.

- Modify: `pipeline/ohlcv/backtest/backtester.py` — add `_fill_downgraded_slots()`
  and call it in `run()` after overlay block
- New file: `tests/test_fill_downgraded_slots.py`
- Verification:
  ```bash
  pytest tests/test_fill_downgraded_slots.py -v
  # Run backtest without overlay — result must be identical to pre-change baseline:
  python -m pipeline.main_backtest --backtest 2>&1 | tail -5
  pytest tests/ -x -q
  ```

**Stage 4 passes when:** `optimal_thresholds.json` exists and is valid, slot filling
unit tests pass, and backtest results without overlay are numerically unchanged.

---

### Stage 5 — Orchestration

**Goal:** Implement `main_pipeline.py` and extract `TrainingPipeline` class.
This is the integration stage — it wires together all previous stages.

**Prerequisites check before starting Stage 5:**
```bash
# Verify all prerequisite artifacts exist:
python -c "
from pathlib import Path
required = [
    'data/ohlcv_models/ranker.pkl',
    'data/ohlcv_models/regressor.pkl',
    'data/ohlcv_models/classifier.pkl',
    'data/ohlcv_models/policy_params.json',
    'data/ohlcv_models/selected_features.json',
    'data/fundamentals/fundamental_scores_panel.parquet',
    'data/fundamentals/optimal_thresholds.json',
]
for p in required:
    assert Path(p).exists(), f'Missing: {p}'
print('All prerequisites present')
"
```

If any artifact is missing, re-run the corresponding stage before proceeding.

#### Step 5a — TO-DO 11: TrainingPipeline class + main_pipeline.py

Implement in this internal order to keep each step verifiable:

**Sub-step 5a-i: Create `TrainingArtifacts` dataclass**
```
pipeline/ohlcv/training/training_pipeline.py
```
Define `TrainingArtifacts` dataclass and stub `TrainingPipeline.train()` that
raises `NotImplementedError`. Verify it imports without error.

**Sub-step 5a-ii: Migrate main_train.py logic into TrainingPipeline.train()**
Move the feature engineering → validation → selection → model training sequence
from `main_train.py`'s `train_fundamental_models_with_combined_features()` into
`TrainingPipeline.train()`. Have `main_train.py` call `TrainingPipeline.train()`
instead. Verify `main_train.py --mode fundamental --skip-etl` still works.

**Sub-step 5a-iii: Create `pipeline/main_pipeline.py`**
Implement Phase 1 (data quality), Phase 2 (full training via TrainingPipeline),
Phase 3a (single-split backtest), Phase 3b (walk-forward with Option B per-fold),
Phase 4 (report aggregation). Use the shared `run_dir` timestamp for all phases.

**Sub-step 5a-iv: Create `pipeline/ohlcv/reports/pipeline_reporter.py`**
Implement `PipelineReporter.generate()` to read phase JSON outputs and write
`pipeline_summary.json` + `pipeline_summary.md`.

- Verification:
  ```bash
  # End-to-end smoke test:
  python -m pipeline.main_pipeline \
    --mode fundamental \
    --fundamental-overlay \
    --fundamental-scores-path data/fundamentals/fundamental_scores_panel.parquet \
    --skip-etl

  # Verify folder structure:
  TS=$(ls -t reports/ | head -1)
  python -c "
  from pathlib import Path
  ts = '${TS}'
  base = Path('reports') / ts
  required_paths = [
    'data_quality/data_quality_summary.json',
    'training/feature_validation/feature_matrix_validation.json',
    'training/feature_selection/selected_features.json',
    'backtest_single_split/backtest_metrics.csv',
    'backtest_walk_forward/fold_0/feature_selection/selected_features.json',
    'backtest_walk_forward/aggregate/feature_stability_across_folds.csv',
    'pipeline_summary.json',
    'pipeline_summary.md',
  ]
  for p in required_paths:
    assert (base / p).exists(), f'Missing: {base / p}'
  print('All pipeline outputs present')
  "

  # Verify training pipeline used in both Phase 2 and Phase 3b:
  python -c "
  import json
  from pathlib import Path
  ts = sorted(Path('reports').iterdir())[-1].name
  # Phase 2 and fold_0 must both have selected_features (proves TrainingPipeline called both places)
  sf2 = json.load(open(f'reports/{ts}/training/feature_selection/selected_features.json'))
  sf3 = json.load(open(f'reports/{ts}/backtest_walk_forward/fold_0/feature_selection/selected_features.json'))
  assert sf2['n_selected'] > 0
  assert sf3['n_selected'] > 0
  print('Phase 2 features:', sf2['n_selected'], '| Fold 0 features:', sf3['n_selected'])
  "

  # Verify standalone main_train.py still works (backward compat):
  python -m pipeline.main_train --mode fundamental --skip-etl
  # Verify standalone main_backtest.py still works:
  python -m pipeline.main_backtest --backtest

  pytest tests/ -x -q
  ```

**Stage 5 passes when:** the end-to-end pipeline run completes, all required output
files exist, `feature_stability_across_folds.csv` is produced, and standalone
`main_train.py` / `main_backtest.py` still work independently.

---

### Stage 6 — Documentation

**Goal:** Produce the architecture diagram that reflects the fully-implemented system.
Written last so it accurately represents the final code, not a planning sketch.

#### Step 6a — TO-DO 2: PlantUML architecture diagram

- New file: `notebooks/rel3_training_architecture.puml`
- The diagram must reflect the architecture as implemented across Stages 0–5,
  including the `TrainingPipeline` class, `main_pipeline.py` phases, and the
  TO-DO 9/10/8 validation gates in sequence.
- Verification:
  ```bash
  # Check PlantUML syntax (requires plantuml jar or online renderer):
  grep "@startuml" notebooks/rel3_training_architecture.puml
  grep "@enduml"   notebooks/rel3_training_architecture.puml
  # Verify the two training tracks (A and B) are distinct in the diagram:
  grep -i "track\|fundamental\|ohlcv\|price" notebooks/rel3_training_architecture.puml | head -5
  ```

**Stage 6 passes when:** the `.puml` file is syntactically valid and renderable.

---

### Cross-stage integration invariants

These assertions must hold after EVERY stage. Run them after completing each stage,
not just at the end.

```bash
# 1. main_train.py --mode price still works (never broken by any stage)
python -m pipeline.main_train --mode price --help > /dev/null && echo "price mode: OK"

# 2. main_inference.py still works with existing fundamental_scores.json (TO-DO 3 backward compat)
python -c "
from pipeline.fundamental_analysis.integration.overlay import load_fundamental_scores
scores = load_fundamental_scores({})
assert len(scores) > 0, 'Scores empty — JSON fallback broken'
print('Inference backward compat: OK, scores for', len(scores), 'tickers')
"

# 3. All existing tests pass
pytest tests/ -x -q --tb=short

# 4. No hardcoded timestamp paths in new code
grep -r "reports/20[0-9][0-9]" pipeline/ && echo "FAIL: hardcoded timestamp found" || echo "No hardcoded timestamps: OK"
```

---

### Recommended implementation order for a single agent

If one agent implements all stages sequentially (no parallelism):

```
0a (TO-DO 1) → 0b (TO-DO 5) → 1a (TO-DO 7) → 1b (TO-DO 3)
→ 2a (TO-DO 9) → 2b (TO-DO 10) → 3a (TO-DO 8)
→ 4a (TO-DO 4) → 4b (TO-DO 6) → 5a (TO-DO 11) → 6a (TO-DO 2)
```

Total: 11 TO-DOs, approximately in that order.
Estimated implementation complexity (relative):
- Stage 0: Low (config + fee constant + tests)
- Stage 1: Medium (main_train refactor + FundamentalScorer extension)
- Stage 2: Medium-High (two new validator classes + integration)
- Stage 3: High (multi-stage feature selection with permutation importance)
- Stage 4: High (grid search + overlay integration + slot filling)
- Stage 5: High (full orchestrator + TrainingPipeline extraction)
- Stage 6: Low (diagram generation)

If two agents work in parallel, the fastest path is:
- Agent A: 0a → 0b → 1a → 2a → 2b → 3a → 5a
- Agent B: 1b → 4a → 4b
- Both complete before Stage 5 begins.

---

## TO-DO 1 — Remove ETF Tickers (VOO, ONEQ) from Pipeline Universe

### Background
The pipeline trains fundamental AI models on quarterly SEC filings (10-Q / 10-K).
Index ETFs such as VOO (Vanguard S&P 500 ETF) and ONEQ (Fidelity Nasdaq Composite ETF)
do not file earnings reports. They have no income statement, balance sheet, or cash flow
statement. As a result, every `f_*` fundamental feature column is `NaN` for these tickers
throughout `data/fundamentals/combined_features_for_fundamental_training.parquet`.

This was confirmed by inspecting the tail of that parquet file:
```
ticker       date  f_net_margin  f_roa  f_roe  f_piotroski_f
VOO    2026-04-17           NaN    NaN    NaN            NaN
```

### Task
Remove `VOO` and `ONEQ` from the tickers list in `config/settings.yaml`.
Replace them with `SNDK` (Sandisk) and `XOM` (Exxon Mobil).

### File to edit
`config/settings.yaml`, section `pipeline.tickers` (lines ~33–61).

Current list (28 operating companies + 2 ETFs):
```
GOOG, NVDA, MSFT, TSLA, MU, PLTR, AAPL, META, DELL, ONEQ,
AMZN, NFLX, CRM, ORCL, AMD, AVGO, QCOM, TXN, ASML, TSM,
INTC, SNOW, MDB, CRWD, SHOP, CSCO, VOO, TER, ROK, SYM
```

### Acceptance criteria
- `VOO` and `ONEQ` are removed from `pipeline.tickers`.
- Two `# TODO: add replacement ticker here` comment lines are inserted in their place
  so the owner can see exactly where to add new stocks.
- No other lines in `settings.yaml` are changed.
- The YAML file remains valid (parseable by `yaml.safe_load`).

---

## TO-DO 2 — Architecture Diagram of AI Model Training (PlantUML)

### Background
The training pipeline spans multiple modules and two distinct training tracks. There is
currently no visual documentation of how data flows from raw SEC filings and OHLCV prices
through feature engineering, labelling, model training, and artifact persistence.

### Task
Create a new file `notebooks/rel3_training_architecture.puml` containing a PlantUML
diagram that accurately maps the full training flow. The diagram must be renderable by
any standard PlantUML renderer.

### Diagram must cover

**Data sources (inputs):**
- SEC EDGAR Company Facts API → `data/fundamentals/fundamental_training_data.parquet`
- OHLCV price feeds → in-memory price DataFrame

**Feature engineering:**
- `OhlcvFeatureEngineer` → 14 price features
  (ret_1d, ret_5d, ret_10d, ret_20d, sma_5_ratio, sma_20_ratio, sma_50_ratio,
   vol_10d, vol_20d, rsi_14, macd_hist, vol_zscore_5d, rank_ret_5d, rank_vol_20d)
- `FundamentalsFeatureEngineer` → 44 fundamental features (all prefixed `f_`)
  Sub-components: ratio_calculator, accruals, trend_features, piotroski, sector_relative
- `FeatureJoiner.join()` → `pd.merge_asof(direction='backward')` temporal alignment
  → `data/fundamentals/combined_features_for_fundamental_training.parquet`

**Two parallel training tracks:**

Track A — Short-term OHLCV trading model:
- Labels: `LabelBuilder.build_1w_labels()` → 1-week forward cross-sectional rank
- Train/test split on `train_cutoff_date`
- Models: LightGBM ranker + regressor + classifier
- Artifacts: `data/ohlcv_models/ranker.pkl`, `regressor.pkl`, `classifier.pkl`
- Coefficient optimisation: `SlotSelector.optimize_coefficients()` → Sharpe maximisation
  → `pipeline/ohlcv/policy/policy_params.json`

Track B — Long-term fundamental scorer:
- Labels: `FundamentalLabelBuilder.build_labels()` → 6-month forward return quintile
- Time-based 80/20 split on unique `filing_date`s (prevents look-ahead bias)
- Models: LightGBM × 4 (composite, quality, value, trend sub-models)
- Scoring: `scorer.score_latest()` → percentile rank per ticker
- Artifacts: `data/fundamentals/fundamental_scorer.pkl`
  + `data/fundamentals/fundamental_scores.json`

**Inference / backtest consumption:**
- `main_inference.py`: loads OHLCV models + fundamental features → SlotSelector → overlay
- `main_backtest.py`: replays the same flow historically → equity curve + metrics

**Entry points:**
```
python -m pipeline.main_train --mode price              # Track A only
python -m pipeline.main_train --mode fundamental_full   # Track A + B combined features
python -m pipeline.main_train --mode fundamental_scorer # Track B scorer only
python -m pipeline.main_train --mode both               # All tracks
```

### Acceptance criteria
- The `.puml` file is syntactically valid PlantUML.
- It uses `@startuml` / `@enduml` wrappers.
- It uses `package`, `component`, `arrow` (`-->`) notation to separate layers clearly.
- The two training tracks (A and B) are visually distinct (e.g. separate packages or colours).
- File is saved as `notebooks/rel3_training_architecture.puml`.

---

## TO-DO 3 — Build a Point-in-Time Scores Panel (Replace Snapshot JSON)

### Background
The current `FundamentalScorer` computes scores once per training run and stores a flat
snapshot in `data/fundamentals/fundamental_scores.json`:
```json
{
  "AAPL": {"composite_score": 0.45, "quality_score": 0.72, ..., "filing_date": "2026-01-30"},
  ...
}
```

This is a **single-point snapshot** of the most recent filing per ticker. It has two problems:

1. **Backtesting look-ahead bias**: When replaying historical dates, the backtest loads
   the JSON and uses scores computed from filings that may not have existed yet on that
   replay date. For example, replaying 2025-06-01 but reading a score derived from a
   2026-01-30 filing is using future information.

2. **Stale cross-sectional ranks**: Scores are percentile ranks across the universe.
   When one ticker files new data, all relative ranks shift. A snapshot cannot capture
   this — the panel must re-rank the universe after every new filing.

### Task
Extend `FundamentalScorer` (file: `pipeline/fundamental_analysis/models/fundamental_scorer.py`)
to produce and persist a **time-series panel** of scores, and update all consumers to use it.

### Implementation specification

#### 3a. New method: `score_panel(df_fundamentals)`
Produce a row for every `(ticker, filing_date)` pair in the training data, not just
the most recent one. After computing raw LightGBM predictions for all rows, convert
them to **cross-sectional percentile ranks within each `filing_date` cohort** (i.e.
all tickers that filed in the same calendar quarter are ranked against each other).

Pseudocode:
```python
def score_panel(self, df):
    # df has columns: ticker, filing_date, f_* (44 fundamental features)
    raw_preds = self.model.predict(df[self.feature_names])
    df = df[['ticker', 'filing_date']].copy()
    df['raw_pred'] = raw_preds

    # Cross-sectional percentile rank within each filing cohort
    # Group by quarter (filing_date rounded to quarter) so tickers filing
    # in the same 3-month window are ranked together.
    df['filing_quarter'] = pd.to_datetime(df['filing_date']).dt.to_period('Q')
    df['composite_score'] = df.groupby('filing_quarter')['raw_pred'] \
                              .rank(pct=True)

    # Repeat for quality, value, trend sub-models...
    return df[['ticker', 'filing_date', 'composite_score',
               'quality_score', 'value_score', 'trend_score']]
```

#### 3b. Forward-fill to daily frequency
After building the quarterly panel, forward-fill each ticker's scores to daily
granularity using `pd.merge_asof(direction='backward')`, so that every calendar
date maps to the most recently available quarterly score as of that date.

The result: a parquet file `data/fundamentals/fundamental_scores_panel.parquet`
with schema:
```
ticker        | str   — ticker symbol
as_of_date    | date  — calendar date (daily)
filing_date   | date  — the filing that produced these scores
composite_score | float [0,1]
quality_score   | float [0,1]
value_score     | float [0,1]
trend_score     | float [0,1]
```

#### 3c. Update the overlay loader
In `pipeline/fundamental_analysis/integration/overlay.py`, update `load_fundamental_scores()`
to accept an optional `as_of_date` parameter. When the panel parquet exists, filter it to
the row matching `(ticker, as_of_date)` instead of reading the flat JSON. Preserve
backward compatibility: if the panel does not exist, fall back to the JSON snapshot.

#### 3d. Update `main_backtest.py`
When loading fundamental scores for a backtest fold covering dates [fold_start, fold_end],
pass `as_of_date=fold_start` to `load_fundamental_scores()` so that each fold only sees
scores that were computable on its start date.

#### 3e. Retain the JSON snapshot
Keep `fundamental_scores.json` as-is for real-time inference (`main_inference.py`), since
inference always wants the latest available scores. Only the backtest path needs the panel.

### Acceptance criteria
- `fundamental_scores_panel.parquet` is produced during `train_fundamental_scorer()`.
- The panel covers all historical filing dates present in `fundamental_training_data.parquet`.
- `as_of_date` filtering in `load_fundamental_scores()` passes a point-in-time correctness
  test: for any date `d`, no score derived from a `filing_date > d` is returned.
- `main_backtest.py` uses the panel; `main_inference.py` continues to use the JSON.
- All existing tests pass.

---

## TO-DO 4 — Backtested Threshold Search for Fundamental Overlay

### Background
The fundamental overlay (`pipeline/fundamental_analysis/integration/overlay.py`) uses
hardcoded thresholds to downgrade BUY signals to DOWNGRADE/WARN/HOLD:

```python
_DEFAULT_THRESHOLDS = {
    "downgrade_quality_max": 0.20,   # BUY → DOWNGRADE if quality < 0.20
    "downgrade_trend_max": 0.25,     # BUY → DOWNGRADE if trend < 0.25
    "warn_quality_max": 0.35,
    "warn_trend_max": 0.35,
    "strong_buy_quality_min": 0.7,
    "strong_buy_value_min": 0.6,
    "strong_buy_trend_min": 0.5,
    "downgrade_piotroski_max": 3,
}
```

These values were set by domain judgment, not by empirical optimisation. There is no
evidence they are optimal. The task is to implement a grid search over threshold
combinations and select the set that maximises risk-adjusted performance on a held-out
validation window.

### Task
Create a new module `pipeline/fundamental_analysis/models/threshold_optimizer.py`
containing a `ThresholdOptimizer` class. Integrate it into `main_train.py`.

### Implementation specification

#### 4a. `ThresholdOptimizer` class

```python
class ThresholdOptimizer:
    """
    Grid-searches fundamental overlay thresholds to maximise Sharpe ratio
    on a held-out validation window.

    Usage:
        optimizer = ThresholdOptimizer(config)
        best_thresholds = optimizer.optimize(
            df_features,           # combined_features parquet as DataFrame
            fundamental_scores_panel,  # panel parquet as DataFrame (from TO-DO 3)
            ranker, regressor, classifier,  # trained OHLCV models
            val_start_date,        # start of held-out validation window
            val_end_date,          # end of held-out validation window
        )
    """
```

#### 4b. Grid search space
Search the following thresholds independently (all scores are in [0, 1]):

```python
SEARCH_SPACE = {
    "downgrade_quality_max":  [0.10, 0.15, 0.20, 0.25, 0.30],
    "downgrade_trend_max":    [0.15, 0.20, 0.25, 0.30, 0.35],
    "warn_quality_max":       [0.25, 0.30, 0.35, 0.40, 0.45],
    "warn_trend_max":         [0.25, 0.30, 0.35, 0.40, 0.45],
    "strong_buy_quality_min": [0.60, 0.65, 0.70, 0.75, 0.80],
    "strong_buy_value_min":   [0.50, 0.55, 0.60, 0.65, 0.70],
    "strong_buy_trend_min":   [0.40, 0.45, 0.50, 0.55, 0.60],
}
```

Enforce validity constraints before evaluating any combination:
- `downgrade_quality_max < warn_quality_max < strong_buy_quality_min`
- `downgrade_trend_max < warn_trend_max < strong_buy_trend_min`

This reduces the search space by filtering out incoherent threshold orderings.

#### 4c. Objective function
For each valid threshold combination:
1. Run the full backtest on the validation window using `main_backtest.Backtester`.
2. Apply the fundamental overlay with those thresholds.
3. Record: `sharpe_ratio`, `max_drawdown`, `total_return`, `n_downgrades`, `n_strong_buys`.
4. Primary objective: **maximise Sharpe ratio**.
5. Secondary constraint: `n_downgrades >= 1` (the thresholds must actually fire at least
   once, otherwise we are just disabling the overlay).

#### 4d. Results output
Save two outputs:
- `data/fundamentals/threshold_search_results.csv` — one row per combination tested,
  columns: all 7 threshold values + sharpe + max_drawdown + total_return + n_downgrades.
- `data/fundamentals/optimal_thresholds.json` — the single best combination:
  ```json
  {
    "downgrade_quality_max": 0.20,
    "downgrade_trend_max": 0.20,
    "warn_quality_max": 0.35,
    ...
    "optimised_sharpe": 1.42,
    "optimised_on_window": ["2023-01-01", "2025-01-01"]
  }
  ```

#### 4e. Integration into `main_train.py`
Add a new training mode:
```
python -m pipeline.main_train --mode optimize_thresholds
```

When this mode is invoked:
1. Load the trained OHLCV models and fundamental scorer (must already exist).
2. Load `combined_features_for_fundamental_training.parquet`.
3. Load `fundamental_scores_panel.parquet` (requires TO-DO 3 to be complete).
4. Run `ThresholdOptimizer.optimize()` over the validation window
   (`train_cutoff_date` to end of data).
5. Save results to the two output files above.
6. Log a summary table of the top 10 combinations by Sharpe.

#### 4f. Update overlay default loading
In `overlay.py`, update `_resolve_thresholds()` to check for
`data/fundamentals/optimal_thresholds.json` and load it automatically if it exists,
falling back to `_DEFAULT_THRESHOLDS` if not. This means running
`--mode optimize_thresholds` once automatically improves all future inference runs.

### Acceptance criteria
- `ThresholdOptimizer` runs without error on the existing dataset.
- `threshold_search_results.csv` is produced with at least 50 rows (many combinations
  should be valid after constraint filtering).
- `optimal_thresholds.json` is produced and loadable by `_resolve_thresholds()`.
- Overlay behaviour in inference and backtest automatically uses optimal thresholds
  when the JSON file exists.
- Validity constraints (ordering) are enforced; no incoherent threshold sets are tested.
- All existing tests pass.

> **TO-DO 11 Integration Note**: `ThresholdOptimizer` is a candidate for an optional
> Phase 3c in `main_pipeline.py`, running after Phase 3b walk-forward backtest.
> When implementing, ensure `ThresholdOptimizer.optimize()` accepts a `report_dir: Path`
> parameter so its outputs (`threshold_search_results.csv`, `optimal_thresholds.json`)
> are written to `reports/<ts>/threshold_optimization/` — never to a hardcoded path.

---

## TO-DO 5 — Revert Transaction Fee to Flat $10 Per Trade

### Background
The rel3 P0 work replaced the flat $10-per-trade fee with a proportional bps-based
cost model (`spread_bps + slippage_bps + commission_bps`). This was done under the
assumption that proportional costs are more realistic at scale. However, the owner has
confirmed that **$10 flat per trade (entry or exit) is the actual broker fee** for this
account, regardless of trade size. The proportional model is economically incorrect for
this specific trading context and must be reverted.

The flat fee applies symmetrically:
- +$10 cost when ENTERING a new position (buying)
- +$10 cost when EXITING an existing position (selling)
- $0 for positions held unchanged (no trade, no fee)

### Files to change

**1. `pipeline/ohlcv/backtest/backtester.py`**

In `__init__`, remove the bps cost attributes and replace with a single constant:
```python
# BROKER REALITY: flat $10 per trade (entry or exit), regardless of size.
# DO NOT replace with proportional/bps-based fees — this is not a model assumption,
# it is the actual fee charged by the broker on this account.
FLAT_TRADE_FEE_DOLLARS = 10.0
```

In `_reconcile_bucket`, replace the two proportional cost lines with:
```python
# EXIT cost: flat $10 per position sold
for ticker in bucket.positions:
    if ticker not in target_tickers:
        total_fees += FLAT_TRADE_FEE_DOLLARS

# ENTRY cost: flat $10 per new position bought
for ticker in target_tickers:
    if ticker not in bucket.positions:
        total_fees += FLAT_TRADE_FEE_DOLLARS
```

Remove the `trade_fee` legacy parameter and the `self.trade_fee` attribute — they are
no longer needed now that the canonical fee is the flat constant above.

Remove the `# P0 Fix` comment block that described the proportional cost model, since
that model is being removed.

**2. `config/settings.yaml`**

Remove the `costs` section entirely (or retain it as documentation-only with a comment
that it is unused):
```yaml
# costs: section removed — broker charges flat $10/trade regardless of size.
# See FLAT_TRADE_FEE_DOLLARS in pipeline/ohlcv/backtest/backtester.py.
```

### New test to add

Create `tests/test_flat_trade_fee.py`:

```python
"""
Enforce that the backtester always uses the flat $10 broker fee.

This test exists to prevent well-intentioned "improvements" from silently
replacing the flat fee with a proportional/bps model. The $10 figure is
a broker reality for this account, not a modelling assumption.
"""
import pytest
from unittest.mock import MagicMock
from pipeline.ohlcv.backtest.backtester import Backtester, FLAT_TRADE_FEE_DOLLARS


def test_flat_fee_constant_is_ten_dollars():
    """FLAT_TRADE_FEE_DOLLARS must always be exactly $10."""
    assert FLAT_TRADE_FEE_DOLLARS == 10.0, (
        "Broker fee is $10 flat per trade. Do not change this value."
    )


def test_entry_fee_is_flat_regardless_of_capital(minimal_config):
    """Entry fee must be $10 regardless of bucket capital or weight."""
    bt = Backtester(minimal_config, ranker=None, regressor=None,
                    classifier=None, selector=None)
    from pipeline.ohlcv.backtest.backtester import PortfolioBucket

    small_bucket = PortfolioBucket(initial_capital=100.0)
    large_bucket = PortfolioBucket(initial_capital=1_000_000.0)
    target = {"AAPL": 0.33}

    fee_small = bt._reconcile_bucket(small_bucket, target)
    small_bucket.positions = {}        # reset

    # Rebuild large bucket — positions start empty
    fee_large = bt._reconcile_bucket(large_bucket, target)

    assert fee_small == FLAT_TRADE_FEE_DOLLARS, "Small bucket entry fee must be $10"
    assert fee_large == FLAT_TRADE_FEE_DOLLARS, "Large bucket entry fee must be $10"
    assert fee_small == fee_large,              "Fee must be size-independent"


def test_no_fee_for_held_positions(minimal_config):
    """Positions held unchanged between rebalances must incur zero fee."""
    bt = Backtester(minimal_config, ranker=None, regressor=None,
                    classifier=None, selector=None)
    from pipeline.ohlcv.backtest.backtester import PortfolioBucket

    bucket = PortfolioBucket(initial_capital=10_000.0)
    bucket.positions = {"AAPL": 0.33, "NVDA": 0.33}
    # Same target as current positions — no trades
    fee = bt._reconcile_bucket(bucket, {"AAPL": 0.33, "NVDA": 0.33})
    assert fee == 0.0, "No trade should incur zero fee"


@pytest.fixture
def minimal_config():
    return {"allocation": {}, "debug": False}
```

### Acceptance criteria
- `FLAT_TRADE_FEE_DOLLARS = 10.0` is a module-level constant in `backtester.py`.
- `_reconcile_bucket` charges exactly `$10 × number_of_new_trades`, never a fraction.
- The `costs` bps fields in `settings.yaml` are removed or commented out.
- All three tests in `test_flat_trade_fee.py` pass.
- No other test is broken by the revert.

---

## TO-DO 6 — Post-Downgrade Slot Filling: Replace CASH with Best Non-Downgraded Stock

### Background
When the fundamental overlay fires a DOWNGRADE on a stock that the SlotSelector chose,
the current code simply removes that ticker from `target_tickers` and leaves the slot
empty (implicit cash). There is no logic to ask: "Is there another stock already held
in this bucket, or ranked just below the selection threshold, that would be better than
holding cash?"

The current code in `backtester.py` (lines 136–141):
```python
target_tickers = {}
for _, row in overlay_df.iterrows():
    fa = row.get("fundamental_action", row["action"])
    if t != "CASH" and row["weight"] > 0 and fa != "DOWNGRADE":
        target_tickers[t] = row["weight"]
# Result: if TSLA was the 3rd pick and gets DOWNGRADED, only 2 stocks are held.
# The bucket is 66% invested. No logic asks: "should we hold the 4th-ranked stock instead?"
```

There are two separate sub-problems:

**Sub-problem A — No substitute candidate from SlotSelector**
SlotSelector already ranked all 30 stocks. The 4th, 5th, 6th ranked stocks are
available in `df_day` but were not selected. When a DOWNGRADE removes the 3rd pick,
the natural candidate is the 4th-ranked stock — IF it passes the `prob_hurdle` and
its `adj_opportunity > cash_benchmark_score`. Currently this candidate is never consulted.

**Sub-problem B — No preference for previously-held stocks**
When the bucket previously held stock X (from 5 days ago), and today's new selection
does not include X, the reconciliation sells X and goes to cash. If the overlay then
also removes the 3rd new pick, the bucket ends up with fewer stocks than optimal.
The hysteresis logic in `_apply_hysteresis()` partially addresses this for marginal
cases, but it runs BEFORE the overlay, so it cannot protect against post-overlay gaps.

### Task
Implement a `_fill_downgraded_slots()` method in `Backtester` and call it after the
overlay is applied.

### Implementation specification

```python
def _fill_downgraded_slots(
    self,
    df_day: pd.DataFrame,
    overlay_df: pd.DataFrame,
    target_tickers: dict,
    current_positions: dict,
    max_slots: int,
) -> dict:
    """
    After fundamental overlay removes DOWNGRADE tickers, attempt to fill
    empty slots using the next-best ranked candidates from df_day.

    Priority order for filling a vacant slot:
      1. A currently-held ticker not in the new target AND not DOWNGRADED
         (cheapest — no entry cost, already owned).
      2. The next-highest adj_opportunity ticker from df_day that:
         - is not already in target_tickers
         - did not receive DOWNGRADE from the overlay
         - passes prob_hurdle
         - has adj_opportunity > cash_benchmark_score

    If neither condition is met, the slot remains CASH.
    """
```

**Integration point** in `backtester.py` `run()` loop (after overlay block, lines ~140):
```python
if self.fundamental_scores:
    # ... existing overlay code ...
    # NEW: attempt to fill slots vacated by DOWNGRADE
    target_tickers = self._fill_downgraded_slots(
        df_day, overlay_df, target_tickers,
        current_positions=active_bucket.positions,
        max_slots=self.selector.max_slots,
    )
```

### Acceptance criteria
- When a DOWNGRADE removes a slot, `_fill_downgraded_slots()` is called.
- A currently-held ticker that is not DOWNGRADED is preferred over a new entry
  (avoids unnecessary sell + idle cash).
- A next-ranked candidate from `df_day` is considered only if it passes `prob_hurdle`
  and `adj_opportunity > cash_benchmark_score`.
- If no valid candidate exists, the slot is left as CASH — never forced.
- A unit test in `tests/test_fill_downgraded_slots.py` covers:
  (a) previously-held stock is reused when available,
  (b) next-ranked candidate is selected when no held stock is available,
  (c) slot stays CASH when no candidate passes the hurdle.
- Existing backtest results without `--fundamental-overlay` are numerically identical
  (this logic only activates when `self.fundamental_scores` is non-empty).

> **TO-DO 11 Integration Note**: `Backtester` is instantiated inside `main_pipeline.py`
> Phase 3a and Phase 3b. Its `run()` method must accept a `report_dir: Path` parameter
> so backtest artifacts land in the shared run folder:
> Phase 3a → `reports/<ts>/backtest_single_split/`
> Phase 3b fold n → `reports/<ts>/backtest_walk_forward/fold_{n}/backtest/`
> Do not hardcode report output paths inside `Backtester`.

---

## TO-DO 7 — Simplify `main_train.py` Modes: Collapse Partial Fundamental Modes

### Background
`main_train.py` currently exposes five `--mode` choices:

```
price              → OHLCV trading model only
fundamental        → SEC EDGAR ETL only (no model trained)
fundamental_full   → ETL + combined price+fundamental model (no scorer)
fundamental_scorer → ETL + standalone scorer (no combined model)
both               → price + ETL + combined model + scorer (everything)
```

The three middle modes all leave the system in a **partially-updated state**:
- `fundamental` fetches new data but trains nothing. The trading models are stale.
- `fundamental_full` updates the combined trading model but does not update the scorer.
  Inference runs with new trading signals but a stale overlay.
- `fundamental_scorer` updates the overlay scores but does not retrain the trading model.
  The overlay is ahead of the model — temporally misaligned.

Additionally, the `f_*` fundamental features are sparse in isolation (up to 60% NaN for
some columns). Building a daily-frequency trading model on fundamental features alone
produces a signal trained predominantly on stale, forward-filled quarterly data. There
is no valid use case for `fundamental_full` that does not also require `fundamental_scorer`,
and vice versa.

### Task
Collapse the five modes into three. All fundamental training steps must run together
as a single atomic operation.

### New mode set

```
price              → OHLCV trading model only (fast, runs daily/weekly)
fundamental        → ETL + combined features + combined trading model + scorer (quarterly)
both               → price + fundamental (complete quarterly refresh)
```

The existing `fundamental_full` and `fundamental_scorer` modes are removed. The existing
`fundamental` mode (which previously ran only ETL) is repurposed to run the complete
fundamental pipeline.

### Execution map (new dispatch in `main()`)

```python
if mode in ("price", "both"):
    train_price_models(config)

if mode in ("fundamental", "both"):
    train_fundamental_models(config)                          # ETL — SEC EDGAR fetch
    train_fundamental_models_with_combined_features(config)  # combined features + model
    train_fundamental_scorer(config)                         # scorer pkl + scores JSON
```

### Optional: `--skip-etl` flag
To allow retraining models on already-fetched data without re-hitting the SEC EDGAR API
(useful if ETL over 500 tickers takes a long time), add an optional flag:

```bash
python -m pipeline.main_train --mode fundamental --skip-etl
```

When `--skip-etl` is set, `train_fundamental_models()` (the SEC EDGAR fetch) is skipped.
The pipeline proceeds directly to `train_fundamental_models_with_combined_features()` and
`train_fundamental_scorer()`, using the existing `fundamental_training_data.parquet`.
If that file does not exist and `--skip-etl` is set, raise a clear error:
`"fundamental_training_data.parquet not found. Remove --skip-etl to fetch fresh data."`

### Files to change
- `pipeline/main_train.py`: update `parse_args()` choices, update `main()` dispatch,
  update all docstrings.
- Remove all references to `fundamental_full` and `fundamental_scorer` modes from:
  - `pipeline/main_train.py` (argparse choices, docstrings, dispatch)
  - `notebooks/rel3_todo_agent_tasks.md` Notes section (this file) if referenced
  - Any README or documentation that lists the mode names

### Acceptance criteria
- `--mode fundamental` runs ETL + combined model + scorer end-to-end with no partial state.
- `--mode fundamental_full` and `--mode fundamental_scorer` are removed and raise
  `argparse` errors if passed (argparse does this automatically via `choices=`).
- `--mode both` runs price + all fundamental steps in sequence.
- `--skip-etl` skips only the EDGAR fetch; all model training still runs.
- All existing tests that reference mode names are updated.
- Running `--mode fundamental --skip-etl` with a missing parquet file prints a clear
  error and exits non-zero.

> **TO-DO 11 Integration Note**: `main_train.py`'s dispatch functions
> (`train_price_models`, `train_fundamental_models_with_combined_features`,
> `train_fundamental_scorer`) will be wrapped by `TrainingPipeline.train_fold()`
> in TO-DO 11. When implementing TO-DO 7, ensure each function:
> (a) accepts a `run_dir: Path` parameter for all report output — never construct
>     an internal timestamp; the timestamp is owned by `main_pipeline.py`.
> (b) returns a `TrainingArtifacts` dataclass (model references + selected_features
>     + metadata) that the orchestrator can inspect and pass to Phase 3.

---

## TO-DO 8 — Multi-Stage, Multi-Model Feature Selection Pipeline

### Background and motivation

The pipeline currently uses 14 OHLCV price features + 44 fundamental features = 58 total.
The existing `FeatureSelector` (mode=`importance`) selects top-K features by LightGBM's
internal gain metric, computed from the ranker model only. This has three structural flaws:

1. **Single-model, single-metric bias**: Importance from the ranker's gain score silently
   drops features that only the regressor or classifier rely on.

2. **Gain importance is not marginal contribution**: Correlated features share gain —
   both survive the top-K cutoff even when one is fully redundant.
   Example: `f_piotroski_f` (composite) AND its three components
   (`f_piotroski_profitability`, `f_piotroski_leverage`, `f_piotroski_efficiency`)
   are all in FUNDAMENTAL_FEATURES — perfect multicollinearity.

3. **No pre-training data quality filters**: Features with 40–60% NaN are filled with 0
   before training. The model learns `feature == 0` as "no data available" — a
   data-quality artifact masquerading as a financial signal.

**Selection philosophy for this implementation:**
Keep a feature if ANY ONE of the three models (ranker, regressor, classifier) scores it
as having significant permutation importance. Do NOT require 2-of-3 consensus yet.
Rationale: the three models have different objectives. A feature useful to the ranker
only (e.g., cross-sectional rank momentum) does not overfit the regressor — the
regressor simply assigns it low weight. Starting inclusive and tightening later, guided
by the analysis report, is more rigorous than cutting blindly upfront.

The primary deliverable of this task is the **feature selection analysis report**
saved alongside every training run. This report gives the owner the data needed to
decide later whether to enforce 2-of-3 consensus (TO-DO 8b, deferred).

---

### New module: `pipeline/ohlcv/dataset/feature_selection_pipeline.py`

Contains three filter/analysis classes and one orchestrator. Extends — does not
replace — the existing `FeatureSelector`. The orchestrator's output feeds back into
`FeatureSelector` as an `include` list.

---

### Stage 1 — Pre-training filters (model-agnostic)

Run on the raw feature matrix before any model is trained.

#### Class: `NaNVarianceFilter`

```python
class NaNVarianceFilter:
    """Drop features too sparse or too flat to carry signal.

    Parameters (config["features"]["nan_variance_filter"])
    ----------
    max_nan_rate : float, default 0.40
        Drop features where > this fraction of rows are NaN.
        Measured BEFORE fillna — zero-filling must not hide sparsity.
        Applied to FUNDAMENTAL_FEATURES only; PRICE_FEATURES are never dropped.
    min_std : float, default 1e-4
        Drop features whose std (after fillna(0)) is below this threshold.
    """
```

**Expected drops (from observed NaN rates in combined_features parquet):**
```
f_fcf                  37.9% NaN → DROPPED
f_fcf_margin           37.9% NaN → DROPPED
f_accruals             37.3% NaN → DROPPED  (kept in FundamentalScorer unchanged)
f_accruals_std         37.3% NaN → DROPPED
f_interest_coverage    44.4% NaN → DROPPED
f_ocf_to_assets        36.4% NaN → DROPPED
f_ocf_to_net_income    36.4% NaN → DROPPED
```

After Stage 1a: ~51 features remain (14 price + ~37 fundamental).

#### Class: `CorrelationFilter`

```python
class CorrelationFilter:
    """Drop one feature from each highly-correlated pair.

    Parameters (config["features"]["correlation_filter"])
    ----------
    max_correlation : float, default 0.85
        Pearson |r| threshold for a pair to be considered redundant.
    label_col : str
        Target label column. Tiebreaker: keep the feature with higher
        Spearman rank-correlation with the label.
    """
```

**Algorithm:** Greedy, label-correlation-descending order. For each feature,
mark any remaining feature with |corr| > threshold as dropped. The "winner"
in each correlated cluster is always the feature with stronger direct label
correlation — not an arbitrary choice.

**Known redundant pairs to resolve:**
```
(ret_1d,  ret_5d)                    — correlated return lookbacks
(vol_10d, vol_20d)                   — correlated volatility windows
(sma_5_ratio, sma_20_ratio, sma_50_ratio) — correlated MA ratios
(f_net_margin, f_gross_margin, f_operating_margin) — correlated margins
(f_revenue_chg_1, f_revenue_chg_4, f_revenue_rolling_chg_4)
(f_piotroski_f, f_piotroski_profitability,
 f_piotroski_leverage, f_piotroski_efficiency)
```

After Stage 1b: ~36 features remain. The exact count depends on the
correlation structure observed in each training run.

---

### Stage 2 — Permutation importance (model-agnostic, post-training)

#### Class: `PermutationImportanceSelector`

```python
class PermutationImportanceSelector:
    """Compute permutation importance for any BaseModel on a held-out split.

    Algorithm: for each feature f, shuffle f's values across all rows in the
    validation set, re-run predict(), measure the drop in the validation metric.
    Importance = mean drop across n_repeats shuffles.

    Model-agnostic: only calls model.predict() / model.predict_proba(), which
    every BaseModel backend (LightGBM, XGBoost, sklearn) implements identically.

    Parameters (config["features"]["permutation_importance"])
    ----------
    n_repeats : int, default 5
        Shuffle repetitions per feature. Mean drop = importance. Std = stability.
    val_fraction : float, default 0.20
        Chronologically last fraction of training data used as validation.
        Never overlaps with the test split.
    metrics:
        ranker     → Spearman rank correlation (predicted score vs rank label)
        regressor  → negative RMSE          (higher = better)
        classifier → ROC-AUC               (higher = better)
    """
```

**Why permutation over gain/split importance:**
- Gain counts splits; correlated features share it — both look weak individually.
- Permutation measures: "how much does accuracy fall if this feature is destroyed?"
  This is true marginal contribution, measured on the validation set.
- Identical across all model backends — gain/split is LightGBM/XGBoost-specific.

**Output per model:**
```python
{
  "feature_name": {
    "mean_drop":  float,   # average metric degradation when shuffled
    "std_drop":   float,   # variance across n_repeats — flags instability
    "rank":       int,     # rank by mean_drop among all features (1 = most important)
    "significant": bool,   # True if mean_drop > 0 and one-sample t-test p < 0.10
  },
  ...
}
```

---

### Stage 3 — Any-model union selection (inclusive first pass)

#### Class: `AnyModelUnionSelector`

```python
class AnyModelUnionSelector:
    """Keep a feature if it has significant permutation importance in ANY model.

    A feature is "significant" for a model if:
      - mean_drop > 0  (shuffling it hurts the model)
      - one-sample t-test p-value across n_repeats < p_threshold (default 0.10)

    The union ensures that model-specialised features are retained:
      - A feature useful only to the ranker (cross-sectional rank signal) is kept.
      - A feature useful only to the regressor (return magnitude signal) is kept.
      - Neither model's specialised features overfit the other models — trees
        naturally assign near-zero weight to irrelevant features.

    Parameters (config["features"]["union_selector"])
    ----------
    p_threshold : float, default 0.10
        Significance threshold for the one-sample t-test on mean_drop.
    min_models : int, default 1
        Minimum number of models for which the feature must be significant.
        Default 1 = union (keep if ANY model finds it significant).
        Set to 2 or 3 later to tighten selection based on report analysis.
    """
```

**Selection outcome:** Features pass Stage 3 if they are significant in
`>= min_models` of the three models. With `min_models=1` (default), this is
the full union of all three models' significant features.

**The `min_models` parameter is the knob** the owner adjusts after reading the
feature selection report. Start at 1 (inclusive), move to 2 if the report shows
too many low-signal features surviving, move to 3 only if a very tight feature
set is needed and validated by backtest comparison.

---

### Orchestrator: `FeatureSelectionPipeline`

```python
class FeatureSelectionPipeline:
    """Run all three stages and return the final feature list + full audit state.

    Usage in main_train.py:
        pipeline = FeatureSelectionPipeline(config)
        result = pipeline.run(
            df_train,
            label_col="rank_label_1w",
            ranker=ranker,
            regressor=regressor,
            classifier=classifier,
            report_dir=run_dir / "feature_selection",  # same run_dir as backtest report
        )
        selected_features = result["selected_features"]
    """
```

**Full execution sequence:**
```
Stage 1a: NaNVarianceFilter            → drops high-NaN fundamental features (~7)
Stage 1b: CorrelationFilter            → drops one of each correlated pair (~8–15)
           Remaining after Stage 1: ~36–43 features

Stage 2:  Intermediate training pass
          Train ranker, regressor, classifier on Stage-1 filtered features
          PermutationImportanceSelector.compute(ranker,     df_val)
          PermutationImportanceSelector.compute(regressor,  df_val)
          PermutationImportanceSelector.compute(classifier, df_val)

Stage 3:  AnyModelUnionSelector.select(min_models=1)
          → selected_features = union of significant features across all 3 models
          → typically 25–40 of the ~36 Stage-1 survivors

Report:   FeatureSelectionReporter.generate(report_dir)
          → write all CSVs, summary table, and Markdown report

Output:   Save to data/feature_selection/selected_features.json
          Feed selected_features into FeatureSelector as mode="include" list
          Final training run uses selected_features (not the Stage-2 intermediate models)
```

Note: Stage 2 trains *intermediate* models for importance measurement only. The
final production models are retrained from scratch in `main_train.py` on the
`selected_features` output of Stage 3. This prevents the feature-selection pass
from leaking into the production model weights.

---

### Feature Selection Analysis Report

The report is the **primary deliverable** of this task. It is generated by
`FeatureSelectionReporter` and saved to the same timestamped run directory used by
the backtest report: `reports/<YYYY-MM-DD_HH-MM-SS>/feature_selection/`.

#### Report file structure

```
reports/<YYYY-MM-DD_HH-MM-SS>/
    feature_selection/
        feature_selection_summary.csv         ← master table, one row per feature
        feature_correlation_matrix.csv        ← full 58×58 Pearson matrix
        nan_variance_analysis.csv             ← NaN rate + std per feature
        permutation_importance_ranker.csv     ← mean_drop, std_drop, rank, significant
        permutation_importance_regressor.csv
        permutation_importance_classifier.csv
        gain_importance_ranker.csv            ← native model gain (for comparison)
        gain_importance_regressor.csv
        gain_importance_classifier.csv
        label_correlation.csv                 ← Spearman(feature, label) per feature
        feature_selection_report.md           ← human-readable summary with tables
        selected_features.json                ← final list + full audit trail
```

#### `feature_selection_summary.csv` schema (master table)

One row per feature. Every metric side-by-side for easy sorting and analysis.

| Column | Description |
|--------|-------------|
| `feature` | Feature name |
| `group` | `price` or `fundamental` |
| `nan_rate` | Fraction of NaN rows (training split) |
| `std` | Standard deviation (after fillna) |
| `spearman_label` | Spearman rank-correlation with 1-week rank label |
| `gain_ranker` | LightGBM gain importance (ranker) |
| `gain_regressor` | LightGBM gain importance (regressor) |
| `gain_classifier` | LightGBM gain importance (classifier) |
| `perm_ranker_mean` | Permutation importance mean_drop (ranker) |
| `perm_ranker_std` | Permutation importance std_drop (ranker) |
| `perm_ranker_rank` | Rank by perm importance among all features (ranker) |
| `perm_ranker_sig` | Boolean — significant in ranker (p < 0.10) |
| `perm_regressor_mean` | Same for regressor |
| `perm_regressor_std` | |
| `perm_regressor_rank` | |
| `perm_regressor_sig` | |
| `perm_classifier_mean` | Same for classifier |
| `perm_classifier_std` | |
| `perm_classifier_rank` | |
| `perm_classifier_sig` | |
| `n_models_significant` | Count of models (0–3) where feature is significant |
| `consensus_rank` | Mean of perm ranks across all 3 models (lower = more consistently important) |
| `stage1_dropped_nan` | Boolean — dropped by NaNVarianceFilter |
| `stage1_dropped_corr` | Boolean — dropped by CorrelationFilter |
| `corr_dropped_in_favor_of` | If dropped by CorrelationFilter: which feature it lost to |
| `stage3_selected` | Boolean — in final selected_features list |
| `selection_reason` | e.g. `"significant in ranker"`, `"significant in 2/3 models"`, `"dropped: nan_rate=44%"`, `"dropped: corr=0.91 with f_piotroski_f"` |

#### `feature_selection_report.md` content

The Markdown report must contain these five sections:

**Section 1 — Configuration used**
```
Run timestamp: 2026-04-21_14-33-10
NaN threshold: 0.40  |  Correlation threshold: 0.85  |  min_models: 1
Training rows: 58,420  |  Validation rows: 14,605
```

**Section 2 — Stage 1 drop summary**
Table of every dropped feature with the reason and the dropping metric value.
```
| Feature               | Drop reason       | Value  |
|-----------------------|-------------------|--------|
| f_fcf                 | nan_rate > 0.40   | 37.9%  |
| f_interest_coverage   | nan_rate > 0.40   | 44.4%  |
| f_piotroski_profitab. | corr with f_piotr | 0.93   |
```

**Section 3 — Permutation importance table (sorted by consensus_rank)**
All Stage-1 survivors, sorted by `consensus_rank`. Columns: feature,
perm_ranker_mean, perm_regressor_mean, perm_classifier_mean, n_models_significant.
This is the key table for deciding whether to tighten `min_models` later.

**Section 4 — Selection outcome**
```
Features entering Stage 1:    58
Dropped by NaNVarianceFilter:  7  (listed)
Dropped by CorrelationFilter: 12  (listed with which feature they lost to)
Remaining after Stage 1:      39
Selected (significant in ≥1 model): 31
Not selected (significant in 0 models): 8  (listed — candidates for future removal)
```

**Section 5 — Stability flags**
List of features where `perm_std_drop / perm_mean_drop > 0.5` in any model.
High ratio = the feature's contribution varies substantially across shuffle
repetitions, suggesting regime sensitivity. Flag these for the owner's attention.

#### `selected_features.json` schema

```json
{
  "selected_features": ["ret_5d", "rsi_14", "f_net_margin", ...],
  "n_selected": 31,
  "selection_config": {
    "min_models": 1,
    "nan_threshold": 0.40,
    "corr_threshold": 0.85,
    "p_threshold": 0.10
  },
  "dropped_stage1_nan":  ["f_fcf", "f_fcf_margin", ...],
  "dropped_stage1_corr": [
    {"feature": "f_piotroski_profitability", "kept": "f_piotroski_f", "corr": 0.93},
    ...
  ],
  "not_selected_stage3": ["ret_1d", "sma_5_ratio", ...],
  "consensus_ranks": {"ret_5d": 1.3, "rsi_14": 2.7, ...},
  "n_models_significant": {"ret_5d": 3, "rsi_14": 3, "ret_1d": 1, ...},
  "timestamp": "2026-04-21T14:33:10"
}
```

---

### Integration into `main_train.py`

The pipeline runs as part of `--mode fundamental` (after TO-DO 7) and writes its
report to the same `run_dir` as the backtest report. In `--mode price`, it does NOT
run — price-only training continues to use the 14 `PRICE_FEATURES` unchanged.

```python
# In train_fundamental_models_with_combined_features():

run_dir = PROJECT_ROOT / "reports" / "backtest_reports" / run_timestamp
fs_report_dir = run_dir / "feature_selection"

fs_pipeline = FeatureSelectionPipeline(config)
result = fs_pipeline.run(
    df_train,
    label_col="rank_label_1w",
    ranker=factory.create("ranker"),
    regressor=factory.create("regressor"),
    classifier=factory.create("classifier"),
    report_dir=fs_report_dir,
)
selected_features = result["selected_features"]
# selected_features feeds into the final production model training below
```

The existing `FeatureSelector` modes (`default`, `include`, `exclude`, `importance`)
are preserved. A new mode `pipeline` is added that delegates to `FeatureSelectionPipeline`:

```yaml
# settings.yaml
features:
  mode: "pipeline"
  nan_variance_filter:
    max_nan_rate: 0.40
    min_std: 1e-4
  correlation_filter:
    max_correlation: 0.85
  permutation_importance:
    n_repeats: 5
    val_fraction: 0.20
    p_threshold: 0.10
  union_selector:
    min_models: 1          # start inclusive — tighten to 2 after reading the report
```

---

### What this does NOT do (explicit scope boundary)

- Does **not** perform hyperparameter tuning (separate task)
- Does **not** create new features — only selects from the existing 58
- Does **not** change the `FundamentalScorer` — it uses all 44 `f_*` features on
  quarterly snapshot data; NaN is handled natively by LightGBM splits there
- Does **not** break `mode: "default"` or `mode: "importance"` — fully backward compatible
- Does **not** enforce 2-of-3 consensus yet — `min_models=1` is the starting point;
  tightening is deferred until the report is analysed (see TO-DO 8b, not yet written)

### Acceptance criteria
- `FeatureSelectionPipeline.run()` completes without error on the existing dataset.
- `feature_selection_summary.csv` is written with one row per feature (all 58).
- `feature_selection_report.md` contains all five sections described above.
- `selected_features.json` is written and loadable; `selected_features` list is
  non-empty and contains no feature from `dropped_stage1_nan` or `dropped_stage1_corr`.
- Features dropped by `NaNVarianceFilter` include the known-sparse columns
  (`f_fcf`, `f_interest_coverage`, etc.).
- `n_models_significant` column in summary CSV correctly counts 0, 1, 2, or 3 for each
  feature (verifiable by manual inspection of the permutation importance CSVs).
- Report artifacts are written to `reports/<timestamp>/feature_selection/` (same
  timestamped folder as backtest report artifacts).
- Production models (ranker/regressor/classifier) are retrained on `selected_features`
  — not on the Stage-2 intermediate models.
- Permutation importance is computed for all three roles regardless of backend
  (LightGBM, XGBoost, sklearn).
- All existing tests pass.
- `mode: "default"` and `mode: "importance"` in `FeatureSelector` are unchanged.

> **TO-DO 11 Integration Note**: `FeatureSelectionPipeline.run()` is called in two
> contexts by `main_pipeline.py`:
> (a) Once in Phase 2 (full training): `report_dir = run_dir / "training" / "feature_selection"`
> (b) Once per fold in Phase 3b walk-forward (Option B):
>     `report_dir = run_dir / "backtest_walk_forward" / f"fold_{n}" / "feature_selection"`
> The `report_dir` parameter passed by the orchestrator is the only path source.
> Never construct an internal timestamp inside `FeatureSelectionPipeline`.
> The per-fold reports feed `feature_stability_across_folds.csv` in Phase 4.

---

## TO-DO 9 — Dataset Quality Validation Gate Before Feature Engineering

### Background and motivation

The pipeline currently has no validation layer between the combined OHLCV +
Fundamental dataset and model training. Garbage-in-garbage-out risk is real:
silent data bugs (look-ahead bias from a wrong date, a split-unadjusted return
spike, revenue in wrong units) produce plausible-looking feature matrices that
train biased or unstable models.

The existing `RestatementTracker` and `PointInTimeManager` address ETL-level
concerns (are the filings correctly fetched and parsed?). This task addresses
dataset-level concerns (is the combined training dataset correct and sound?).

The validation framework has four layers plus an optional LLM interpretation step:

```
combined_features_for_fundamental_training.parquet
  │
  ├─ Layer 1: Schema & Invariant Checks  (FAIL-HARD  — abort training)
  ├─ Layer 2: Statistical Profiling       (WARN/FAIL  — configurable)
  ├─ Layer 3: Financial Domain Sanity    (SOFT CHECKS — warn only)
  └─ Layer 4: Temporal Integrity         (FAIL-HARD  — abort training)
  │
  └─ DataQualityReport → reports/<timestamp>/data_quality/
     ├─ data_quality_summary.json   (machine-readable, all check results)
     ├─ data_quality_report.md      (human-readable, full narrative)
     ├─ anomaly_rows.csv            (rows that triggered any check)
     └─ staleness_distribution.csv  (filing staleness per ticker)
```

**On LLM integration:** Do NOT feed raw dataset rows to an LLM. Feed the report
summary (~2–5 KB JSON) to an LLM via the existing `pipeline/llm/llm_analyst.py`.
The LLM reads structured statistics, not 76,937 rows. This is feasible within any
context window and produces meaningful interpretation. LLM step is optional and
controlled by `config["data_quality"]["llm_interpretation"]["enabled"]`.

---

### New module: `pipeline/ohlcv/dataset/data_quality_validator.py`

Single class `DataQualityValidator` with four `check_*` methods (one per layer)
and one `generate_report()` method. Invoked from
`train_fundamental_models_with_combined_features()` in `main_train.py` before
any feature selection or model training begins.

---

### Layer 1 — Schema & Invariant Checks (FAIL-HARD)

Physical impossibilities. Any violation aborts training immediately with a clear
error message that names the offending rows and tickers.

#### Checks

**1a. Required columns present**
```
Must exist: ticker, date, adj_close, close, high, low, open, volume
Must exist: ret_1d, ret_5d, rsi_14, filing_date
All PRICE_FEATURES and all FUNDAMENTAL_FEATURES from feature_schema.py
```

**1b. OHLC consistency — impossible price values**
```
close < 0        → impossible
high < low       → impossible
high < close     → impossible (close cannot exceed day's high)
low  > close     → impossible
open < 0         → impossible
volume < 0       → impossible
```

**1c. Duplicate (ticker, date) pairs**
```
df.groupby(['ticker', 'date']).size() > 1  → duplicate rows
```
Duplicates cause silent errors in merge_asof and label building.

**1d. Return magnitude sanity**
```
|ret_1d| > 0.50  → possible stock split artifact or data error
|ret_5d| > 1.00  → extremely suspicious
```
Flag these as potential split-unadjusted price contamination. Log the
ticker and date for every violation. Do not abort, but WARN clearly
because a small number of legitimate extreme moves may exist (e.g. NVDA
post-earnings 2023).

---

### Layer 2 — Statistical Profiling (WARN or configurable FAIL)

**2a. NaN rate per column vs. expected bands**

For each column, check that observed NaN rate falls within the expected range.
Expected rates are derived from the observed data in April 2026 and should be
updated each training run (self-calibrating over time).

```
Expected NaN rates (approximate, from observed data):
  PRICE_FEATURES:        0%  (guaranteed by OhlcvFeatureEngineer)
  f_net_margin:         ~25%  (accept up to 40%)
  f_roa:                ~25%  (accept up to 40%)
  f_piotroski_f:        ~25%  (accept up to 40%)
  f_fcf:                ~38%  (accept up to 55%)
  f_interest_coverage:  ~44%  (accept up to 60%)
  Any f_* column:        WARN if NaN rate > 70% (something structurally wrong)
  Any PRICE_FEATURE:     FAIL if NaN rate > 5%  (should never be NaN)
```

**2b. Return distribution check**
```
mean(ret_1d) should be in [-0.005, +0.015] for large-cap equities
std(ret_1d)  should be in [0.005, 0.050]
If mean(ret_1d) > 0.020 → likely survivorship bias or price data error
```

**2c. Feature outlier rate**
```
For each numeric feature, compute fraction of rows with |z-score| > 5.
Expected: < 0.5% for most features.
WARN if any feature exceeds 2% (suggests extreme values not clipped by feature engineering).
```
Store the top-10 most extreme rows per offending feature in `anomaly_rows.csv`.

**2d. Train/test distribution shift (Kolmogorov-Smirnov test)**
```
Split df at train_cutoff_date.
For each numeric feature, run KS test between train and test distributions.
WARN if KS statistic > 0.15 (moderate shift) for any feature.
WARN (stronger) if KS statistic > 0.30 (severe shift).
```
Severe shift means the test window looks unlike anything the model trained on —
a known risk for regime-change periods (COVID, rate-hike cycle).

**2e. Cross-sectional ticker coverage per date**
```
Compute: tickers_per_date = df.groupby('date')['ticker'].count()
WARN if any date has < 15 tickers (less than half the universe).
WARN if std(tickers_per_date) > 5 (highly variable coverage over time).
```
Low early-history coverage means cross-sectional rank labels are coarser for
early training data.

---

### Layer 3 — Financial Domain Sanity (SOFT CHECKS — warn only)

**3a. Balance sheet equation verification (sample-based)**
```
For a 10% random sample of rows where all three values are non-NaN:
  expected: |total_assets - (total_liabilities + stockholders_equity)| / total_assets < 0.01
  WARN if more than 5% of sampled rows violate this within 1% tolerance.
```
A violation indicates unit normalization error in the ETL (e.g., liabilities in
millions vs. assets in thousands).

**3b. Derived ratio cross-verification (sample-based)**
```
For a 10% random sample of rows:
  f_net_margin ≈ net_income / revenue          (tolerance: 2%)
  f_roa        ≈ net_income / total_assets     (tolerance: 2%)
  f_current_ratio ≈ current_assets / current_liabilities  (tolerance: 2%)
WARN if more than 5% of sampled rows disagree beyond tolerance.
```
This catches bugs where the ratio_calculator.py formula diverges from
the raw metrics stored alongside it.

**3c. Inverted ROE detection (negative equity)**
```
Rows where f_roe < -1.0 AND f_net_margin > 0.05:
  → Company is profitable but has negative equity (buyback-heavy).
  → ROE formula flips sign. Not a data error — a financial structure artifact.
  → LOG these tickers explicitly so the owner knows which f_roe values are
    structurally inverted (cannot be naively compared to positive-equity peers).
```

**3d. Sector z-score group size check**
```
For each sector in the training data, count distinct tickers.
WARN if any sector has fewer than 5 tickers.
  → z-scores computed from < 5 observations are statistically unreliable.
  → f_roe_sector_z, f_net_margin_sector_z etc. are not meaningful for small sectors.
```

**3e. Fundamental staleness distribution**
```
Compute staleness_days = (date - filing_date).days for every row.
Expected: median ~45 days, 95th percentile ~135 days (one quarter).
WARN if 5th percentile < 0      → some rows have filing_date AFTER date (look-ahead)
WARN if 95th percentile > 200   → fundamentals are stale for a large fraction
WARN if any row has staleness_days < 0  → direct look-ahead bias (ESCALATE to Layer 4)
```

---

### Layer 4 — Temporal Integrity (FAIL-HARD)

**4a. Point-in-time correctness**
```
For EVERY row in the combined dataset:
  filing_date <= date   MUST hold without exception.
FAIL-HARD if any violation found. Report:
  - Number of violations
  - Affected tickers and dates
  - The maximum look-ahead gap (max(filing_date - date) in days)
```
This is the single most critical check. A single row violating this means the
model was trained on future information. The `merge_asof(direction='backward')`
should prevent this, but timezone issues, date parsing bugs, or off-by-one errors
can silently introduce violations.

**4b. Label look-ahead check**
```
The 1-week forward return label requires prices 5 trading days ahead.
For the last 5 rows of each ticker, the label must be NaN (not zero).
WARN if any of the last 5 rows per ticker have a non-NaN label.
  → These rows have been incorrectly labeled (future prices leaked in).
```

**4c. Filing date plausibility**
```
No filing_date should be in the future relative to dataset end_date.
No filing_date should be before 2000-01-01 (SEC EDGAR XBRL coverage starts ~2009).
WARN if any filing_date > config["pipeline"]["end_date"].
WARN if any filing_date < 2009-01-01.
```

---

### Report artifacts

Saved to `reports/<YYYY-MM-DD_HH-MM-SS>/data_quality/` alongside
feature_selection and backtest reports.

#### `data_quality_summary.json` schema

```json
{
  "run_timestamp": "2026-04-21T14:33:10",
  "dataset_shape": {"rows": 76937, "columns": 91},
  "date_range": {"start": "2015-03-16", "end": "2026-04-17"},
  "tickers": ["AAPL", "AMD", ...],
  "overall_status": "PASS",   // "PASS", "WARN", "FAIL"
  "fail_hard_triggered": false,
  "checks": {
    "layer1_schema": {
      "status": "PASS",
      "ohlc_violations": 0,
      "duplicate_rows": 0,
      "extreme_returns": {"count": 3, "rows": [{"ticker": "NVDA", "date": "2023-05-25", "ret_1d": 0.241}]}
    },
    "layer2_statistical": {
      "status": "WARN",
      "nan_rates": {"f_interest_coverage": 0.444, "f_fcf": 0.379, ...},
      "nan_violations": [],
      "return_distribution": {"mean_ret1d": 0.00062, "std_ret1d": 0.023},
      "outlier_rates": {"f_roe": 0.0031, "f_debt_to_equity": 0.0044},
      "ks_shift": {"f_net_margin": 0.12, "f_revenue_chg_1": 0.18, ...},
      "ks_violations": ["f_revenue_chg_1"],
      "coverage_per_date": {"min": 28, "max": 30, "std": 0.8}
    },
    "layer3_domain": {
      "status": "WARN",
      "balance_sheet_violation_rate": 0.002,
      "ratio_verification_violation_rate": 0.008,
      "inverted_roe_tickers": ["AAPL", "MSFT"],
      "small_sector_groups": ["Energy"],
      "staleness_p50_days": 47,
      "staleness_p95_days": 131
    },
    "layer4_temporal": {
      "status": "PASS",
      "lookahead_violations": 0,
      "label_lookahead_violations": 0,
      "future_filing_dates": 0
    }
  },
  "warnings": ["f_revenue_chg_1 shows KS shift of 0.18 between train/test splits",
               "Sector 'Energy' has only 2 tickers — sector z-scores unreliable"],
  "blocking_errors": []
}
```

#### `data_quality_report.md` sections

1. **Executive summary** — one paragraph: overall status, count of checks passed/warned/failed
2. **Layer 1 results** — table of invariant checks with pass/fail and violation counts
3. **Layer 2 results** — NaN rate table, return distribution, top-5 KS-shifted features
4. **Layer 3 results** — balance sheet verification outcome, inverted ROE tickers,
   staleness distribution (median, p95, histogram summary)
5. **Layer 4 results** — temporal integrity outcome (critical section)
6. **Anomaly inventory** — table of the specific rows that triggered any check
7. **Recommendations** — auto-generated text:
   - "Consider removing ticker X: all f_* features are NaN (ETF or non-filer)"
   - "Feature f_revenue_chg_1 shows distribution shift. Monitor walk-forward performance on this feature."
   - "3 rows with |ret_1d| > 0.30 detected. Verify adj_close is split-adjusted for NVDA."

#### Optional LLM interpretation

If `config["data_quality"]["llm_interpretation"]["enabled"] = true`, after the
report is written, call `pipeline/llm/llm_analyst.py` with:
- Input: `data_quality_summary.json` (the ~3 KB structured report)
- Prompt template: "You are a quantitative data analyst reviewing a dataset
  quality report for an AI investment pipeline on 30 large-cap US equities,
  2015–2026. Identify: (1) surprising findings, (2) patterns suggesting
  systematic bugs, (3) tickers appearing most frequently in anomaly lists,
  (4) whether overall quality is sufficient for model training. Be specific
  and reference the numbers in the report."
- Output: append LLM response as a new section in `data_quality_report.md`

The LLM reads a 3 KB summary — never raw data rows.

#### 4. `docs/data_quality_guide.md`

A **static documentation file** in `docs/` (not timestamped, not under `reports/`)
that explains each validation layer and each check in plain English.
Written once; updated only when new checks are added.
Primary audience: someone who understands the business of investing and the
pipeline's purpose, but is not a mathematics expert.

Structure — one block per check, always four sub-fields:

```markdown
# Data Quality Validation Guide

## What is this document?
Plain-English explanation of why DataQualityValidator exists and what it protects
against. Include the "garbage-in-garbage-out" concept without jargon.

## Layer 1 — Physical Impossibility Checks

### OHLC Consistency
**What it is:** Every trading day has four price points: Open, High, Low, Close.
By definition, High must be the day's highest price and Low must be the lowest.
A "Close higher than the High" is physically impossible — it never happened in
reality and means the data feed delivered corrupted records.

**What we check:** For every row, Close ≤ High and Close ≥ Low and High ≥ Low.

**What a failure means:** The price data provider delivered bad records for
that ticker and date. Do not train on this data until the source file is corrected.

**Severity:** FAIL-HARD — training is blocked until fixed.

### Duplicate Rows
**What it is:** Each stock should have exactly one record per trading day.
Two records for the same stock on the same day cause silent calculation errors —
averages, returns, and ranks will be computed on duplicated data.

**What we check:** No (ticker, date) pair appears more than once.

**What a failure means:** A data pipeline step ran twice, or two data sources
were merged without deduplication. Fix the ETL before retraining.

**Severity:** FAIL-HARD — training is blocked until fixed.

## Layer 2 — Statistical Plausibility Checks

### NaN Rate per Feature
**What it is:** NaN means "no data available." Some missing data is expected
(quarterly earnings reports only come four times a year, so on most days a
stock has no new earnings figure). But if 90% of a feature's values are missing,
the feature carries almost no information.

**What we check:** Each feature's missing-data rate falls within expected bands.
Price features (calculated daily) should have zero missing data. Earnings features
should have 10–60% missing, not 90%.

**What a failure means:** Either the data fetch failed for many tickers, or a
feature column was not populated by the engineering step.

**Severity:** WARN (configurable to FAIL).

[... continue for return distribution, outlier rates, KS shift, coverage ...]

## Layer 3 — Financial Domain Sanity Checks

### Balance Sheet Equation
**What it is:** In accounting, total assets always equal total liabilities plus
shareholders' equity. This is not a theory — it is a mathematical identity that
every public company must satisfy in its SEC filing. A violation means the
numbers in our dataset are in different units (e.g., assets in millions,
liabilities in thousands) or were loaded from different filing rows.

**What we check:** For a random 10% sample of rows, assets ≈ liabilities + equity
within 1% tolerance.

**What a failure means:** A unit normalization bug in the ETL. The raw numbers
from SEC EDGAR are in different denominations and were not standardized before
being joined.

**Severity:** WARN — does not block training, but corrupts any ratio that divides
by assets or equity.

### Inverted ROE (Return on Equity)
**What it is:** ROE = net income ÷ shareholders' equity. Apple and Microsoft have
spent so many billions buying back their own shares that their shareholders' equity
is actually negative. When you divide a positive profit by a negative equity number,
the result is a negative ROE — even though the company is highly profitable. This
is not a data error; it is a real financial structure.

**What we check:** We flag tickers where ROE is deeply negative despite positive
net margins, so the model's owner knows which companies have this characteristic.

**What a failure means:** Not a failure — purely informational. These tickers need
special handling if ROE is used as a training feature, because their negative ROE
means something completely different from a company that is losing money.

**Severity:** LOG only — no action required unless the modeller chooses to adjust.

[... continue for sector z-score group size, filing staleness ...]

## Layer 4 — Time Integrity Checks

### Point-in-Time Correctness (Look-Ahead Bias)
**What it is:** The model is only allowed to learn from information that existed
on the day it would have made a decision. If Apple's earnings report from January
2026 is attached to a trading row dated December 2025, the model "knows the future"
during training. This is called look-ahead bias. A model with look-ahead bias will
appear to predict brilliantly in backtesting but fail completely in live trading —
because in live trading, future earnings reports do not exist yet.

**What we check:** For every row in the dataset, the filing date (the date the
earnings report was published to SEC EDGAR) must be on or before the trading date
of that row. No exceptions allowed.

**What a failure means:** The temporal alignment step (merge_asof) has a bug,
possibly a timezone mismatch or an off-by-one date error. This is the most critical
check in the entire validation pipeline. Do not train until it is fixed.

**Severity:** FAIL-HARD — training is blocked. A single violation is sufficient
to abort.
```

---

### Integration into `main_train.py`

```python
# In train_fundamental_models_with_combined_features(), after loading combined_features
# and BEFORE any feature selection or model training:

from pipeline.ohlcv.dataset.data_quality_validator import DataQualityValidator

validator = DataQualityValidator(config)
quality_report = validator.validate(
    df=combined_features,
    train_cutoff_date=train_cutoff,
    report_dir=run_dir / "data_quality",
)

if quality_report["fail_hard_triggered"]:
    logger.error("Dataset quality validation FAILED. Training aborted.")
    logger.error("Blocking errors: %s", quality_report["blocking_errors"])
    raise RuntimeError("Dataset quality gate failed — see data_quality_report.md")

if quality_report["overall_status"] == "WARN":
    logger.warning("Dataset quality warnings present. Review data_quality_report.md before relying on results.")
```

### New config section

```yaml
# settings.yaml
data_quality:
  enabled: true                    # set false to skip (not recommended)
  fail_on_warn: false              # set true to treat WARN as FAIL
  max_nan_rate_price_features: 0.05
  max_nan_rate_fundamental: 0.70
  max_outlier_rate: 0.02
  ks_shift_warn_threshold: 0.15
  ks_shift_fail_threshold: 0.30
  min_tickers_per_date: 15
  balance_sheet_tolerance: 0.01
  ratio_verification_tolerance: 0.02
  lookahead_tolerance_days: 0      # must be exactly 0 — any positive value is a bug
  llm_interpretation:
    enabled: false                 # requires pipeline/llm/llm_analyst.py configured
    model: "claude-haiku-4-5-20251001"
```

### Acceptance criteria
- `DataQualityValidator.validate()` runs without error on the existing dataset.
- `data_quality_summary.json` and `data_quality_report.md` are written to
  `reports/<timestamp>/data_quality/`.
- Layer 4 (temporal integrity) correctly identifies ZERO look-ahead violations
  on the current combined dataset (confirming merge_asof is correct).
- Layer 1 correctly detects a deliberately injected OHLC violation in a unit test
  (e.g., insert one row with `close > high` and verify FAIL-HARD triggers).
- Layer 3 correctly identifies AAPL and/or MSFT as "inverted ROE due to negative equity."
- Training proceeds normally when all checks pass.
- Training aborts with a clear error message when Layer 1 or Layer 4 fail-hard.
- All existing tests pass.
- When `llm_interpretation.enabled = false` (default), no LLM call is made.
- `docs/data_quality_guide.md` is written and covers all four validation layers
  in plain English. Each check has a What / Why / Failure meaning / Severity block.
  No mathematical notation in the guide body — prose and examples only.

> **TO-DO 11 Integration Note**: `DataQualityValidator.validate()` is called once
> in Phase 1 of `main_pipeline.py`. The orchestrator passes:
> `report_dir = run_dir / "data_quality"`
> The validator must use the passed `report_dir` exclusively — never construct its
> own timestamp or default output path. A FAIL-HARD from Phase 1 must abort the
> entire pipeline before Phase 2 (training) begins.

---

## TO-DO 10 — Feature Matrix Validator Before Feature Selection

### Background and motivation

After feature engineering transforms the combined dataset into a feature matrix,
there is no layer that verifies the engineering code produced correct output.
TO-DO 9 validates the source data. TO-DO 10 validates that the feature
engineering transformations were applied correctly.

The failure modes are distinct and non-overlapping:

| Layer | Source of failure | Example |
|-------|------------------|---------|
| TO-DO 9 | External data bug | `filing_date > date` in source parquet — look-ahead in merge |
| TO-DO 10 | Feature engineering code bug | `sma_5_ratio = close / sma_5` divides by near-zero producing value of 500.0 |
| TO-DO 8 | Signal quality decision | `ret_1d` and `ret_5d` are redundant — one should be dropped |

Feature selection (TO-DO 8) computes NaN rates, correlations, and permutation
importance on the feature matrix. If any feature values are wrong — wrong range,
wrong NaN pattern, wrong distribution — all selection decisions downstream are
corrupted. Validation must run before selection.

### Placement in the pipeline

```
combined_features.parquet
  │
  ├── TO-DO 9: DataQualityValidator          (source data layer)
  │
  ▼
Feature Engineering
(OhlcvFeatureEngineer + FundamentalsFeatureEngineer)
  │
  ├── TO-DO 10: FeatureMatrixValidator       ← this task
  │
  ▼
TO-DO 8: FeatureSelectionPipeline
  │
  ▼
Model Training
```

---

### New module: `pipeline/ohlcv/dataset/feature_matrix_validator.py`

Single class `FeatureMatrixValidator` with four check layers and a `validate()`
method. Invoked from `train_fundamental_models_with_combined_features()` in
`main_train.py` AFTER feature engineering and BEFORE feature selection.

---

### Layer 1 — Range Invariants

These are hard bounds derived from mathematical definitions. A value outside
these bounds is not a data quality issue — it is a code bug in the engineering step.

#### 1a. Hard bounds (FAIL-HARD if any row violates)

```
rsi_14                    → must be in [0, 100]
                            RSI is bounded [0, 100] by its formula definition.
rank_ret_5d               → must be in [0.0, 1.0]
rank_vol_20d              → must be in [0.0, 1.0]
                            Percentile rank is bounded [0, 1] by definition.
f_piotroski_f             → must be in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
                            Integer count of 9 binary criteria.
f_piotroski_profitability → must be in {0, 1, 2, 3, 4}
f_piotroski_leverage      → must be in {0, 1, 2, 3}
f_piotroski_efficiency    → must be in {0, 1, 2}
adj_close, close, open    → must be > 0
volume                    → must be >= 0
```

#### 1b. Soft bounds (WARN if > 1% of rows violate, for large-cap US universe)

```
sma_5_ratio, sma_20_ratio, sma_50_ratio → warn if outside [0.50, 2.00]
vol_10d, vol_20d                         → warn if > 1.0
                                           Daily vol > 100%/day is extraordinary.
macd_hist                                → warn if |value| > 50.0
                                           Suggests scale error in MACD computation.
ret_1d                                   → warn if |value| > 0.50
                                           Reinforces TO-DO 9 check, after engineering.
```

---

### Layer 2 — NaN Pattern Assertions

After feature engineering, certain features MUST have zero NaN. Others have
known NaN patterns from quarterly filing cadence.

#### 2a. Zero-NaN assertions (FAIL-HARD)

```
All 14 PRICE_FEATURES: NaN rate must be 0.0
  Rationale: OhlcvFeatureEngineer runs on raw OHLCV prices. These features are
  always computable. Any NaN means a rolling window was not handled or the
  feature engineering step silently failed on some rows.

rank_ret_5d, rank_vol_20d:
  For any date where >= 5 tickers are present, both rank features must be
  non-NaN for ALL tickers on that date.
  Rationale: percentile rank is undefined only when the universe is empty or
  has a single ticker — never for a 30-ticker universe.
```

#### 2b. Expected NaN bands for fundamental features (WARN if violated)

```
Any f_* feature:   FAIL if NaN rate == 0.0   (impossible for quarterly data — bug)
Any f_* feature:   FAIL if NaN rate > 0.90   (suggests column not populated at all)
f_net_margin:      warn if NaN rate outside [0.10, 0.60]
f_roa:             warn if NaN rate outside [0.10, 0.60]
f_piotroski_f:     warn if NaN rate outside [0.10, 0.60]
f_fcf:             warn if NaN rate outside [0.25, 0.70]
f_interest_coverage: warn if NaN rate outside [0.30, 0.70]
```

---

### Layer 3 — Cross-Sectional Distribution Checks

Cross-sectional rank features should produce approximately uniform distributions
across all rows. Systematic skew indicates a bug in the ranking computation.

#### 3a. Rank uniformity (KS test against Uniform[0,1])

```
For rank_ret_5d and rank_vol_20d:
  Run a one-sample KS test against Uniform(0, 1) on all non-NaN values.
  FAIL if KS statistic > 0.10 AND p-value < 0.001.
  WARN if KS statistic > 0.06 AND p-value < 0.05.

Expected: flat histogram, no spike at 0 or 1, no gap in the centre.
Bug example: off-by-one in groupby results in all values clustering near 0.
```

#### 3b. Cross-sectional coverage consistency

```
For each date, count tickers with non-NaN rank_ret_5d vs. total tickers that date.
WARN if any date has < 50% of tickers ranked.
  Indicates the ranking step ran on a partial universe for that date.
```

---

### Layer 4 — Target Leakage Screen

If any feature accidentally incorporates future price information, the model
will appear to predict brilliantly in training and fail completely in live
trading. This check is unique to the feature layer — TO-DO 9 cannot detect it
because it is a property of the relationship between a feature and the label,
not a property of the raw data.

#### 4a. Feature-label Spearman correlation screen

```
label_col: rank_label_1w  (1-week forward cross-sectional return rank)

For each feature in the feature matrix:
  corr = spearmanr(feature, label, nan_policy='omit')

FAIL-HARD if |corr| > 0.85 for any feature.
  A legitimate same-day feature cannot correlate this strongly with next week's
  outcome. This is almost certainly a look-ahead bug (future prices leaked in).

WARN if |corr| > 0.60 for any feature.
  Unusually high. Inspect manually.
  Known exception: rank_ret_5d has natural momentum correlation with
  rank_label_1w. Expect |corr| ~ 0.10–0.25 for momentum features. Values
  above 0.60 for this feature would still warrant investigation.
```

#### 4b. Cross-lag autocorrelation check on label

```
Verify rank_label_1w is not a shifted version of a known feature.
Compute: corr(rank_label_1w[t], rank_ret_5d[t+1])
  Should be near 0. High cross-lag correlation (> 0.50) suggests the label
  was built with the wrong date offset — i.e., today's return was labelled
  as next week's prediction.
```

---

### Four deliverables

#### 1. `feature_matrix_validation.json`

Machine-readable output of all check results. Saved to
`reports/<YYYY-MM-DD_HH-MM-SS>/feature_validation/`.

```json
{
  "run_timestamp": "2026-04-21T14:33:10",
  "feature_matrix_shape": {"rows": 73420, "columns": 60},
  "features_checked": 58,
  "overall_status": "PASS",
  "fail_hard_triggered": false,
  "checks": {
    "layer1_range_invariants": {
      "status": "PASS",
      "hard_bound_violations": 0,
      "soft_bound_warnings": [
        {"feature": "macd_hist", "violation_rate": 0.003,
         "range_observed": [-48.2, 61.4], "expected_max_abs": 50.0}
      ]
    },
    "layer2_nan_patterns": {
      "status": "PASS",
      "zero_nan_violations": [],
      "nan_band_violations": [],
      "nan_rates_observed": {
        "ret_1d": 0.0, "rsi_14": 0.0, "f_net_margin": 0.247, "f_fcf": 0.379
      }
    },
    "layer3_distributions": {
      "status": "PASS",
      "rank_uniformity": {
        "rank_ret_5d":  {"ks_stat": 0.04, "p_value": 0.12, "status": "PASS"},
        "rank_vol_20d": {"ks_stat": 0.03, "p_value": 0.41, "status": "PASS"}
      },
      "coverage_warnings": []
    },
    "layer4_leakage": {
      "status": "PASS",
      "fail_hard_leakage": [],
      "warn_leakage": [],
      "top_correlations": [
        {"feature": "rank_ret_5d", "spearman_with_label": 0.18},
        {"feature": "ret_5d",      "spearman_with_label": 0.14},
        {"feature": "ret_10d",     "spearman_with_label": 0.11}
      ],
      "cross_lag_corr_rank_ret5d_plus1": 0.02
    }
  },
  "warnings": [],
  "blocking_errors": []
}
```

#### 2. LLM interpretation prompt

If `config["feature_validation"]["llm_interpretation"]["enabled"] = true`,
after writing the JSON, call `pipeline/llm/llm_analyst.py` with:

- Input: `feature_matrix_validation.json` (~2–4 KB)
- Prompt template:
  ```
  You are a quantitative analyst reviewing a feature matrix validation report
  for an AI investment pipeline. The pipeline trains three models (ranker,
  regressor, classifier) on 58 engineered features from 30 large-cap US
  equities, 2015–2026. The features are derived from daily OHLCV price data
  and quarterly SEC fundamental filings.

  From the validation JSON provided, identify:
  1. Any checks that suggest a feature engineering bug — range violations, NaN
     patterns inconsistent with quarterly filing cadence, rank uniformity failures.
  2. Any potential target leakage risks — feature-label Spearman correlations
     above 0.60 that cannot be explained by known momentum effects.
  3. Features that show suspicious patterns not directly flagged as violations
     but that warrant manual inspection.
  4. Overall assessment: is this feature matrix safe to proceed with feature
     selection and model training?

  Be specific. Reference feature names and numbers from the report.
  Conclude with a single line: SAFE TO PROCEED or REQUIRES INVESTIGATION.
  ```

- Output: append LLM response as a "LLM Interpretation" section at the end of
  `feature_validation_report.md`.

#### 3. `feature_validation_report.md`

Human-readable report in `reports/<YYYY-MM-DD_HH-MM-SS>/feature_validation/`.

Five sections:

1. **Executive summary** — overall status, count of pass/warn/fail checks,
   one-sentence verdict on whether training may proceed.
2. **Layer 1 — Range invariants** — table of all features with observed min/max
   and status (PASS / WARN / FAIL).
3. **Layer 2 — NaN patterns** — observed NaN rate vs. expected band per feature,
   with a flag column.
4. **Layer 3 — Distribution checks** — KS statistics and p-values for rank
   features, cross-sectional coverage summary.
5. **Layer 4 — Leakage screen** — full feature-label correlation table sorted
   descending by |corr|, flagged features highlighted. Cross-lag check result.
6. **LLM Interpretation** — appended if enabled.
7. **Recommended actions** — auto-generated actionable text, e.g.:
   ```
   - macd_hist: 0.3% of rows exceed |50|. Consider clipping at ±50 in
     OhlcvFeatureEngineer. Not blocking.
   - rank_ret_5d Spearman with label = 0.18. Expected for momentum. OK.
   - No target leakage detected. Safe to proceed to feature selection.
   ```

#### 4. `docs/feature_validation_guide.md`

A **static documentation file** in `docs/` (not timestamped, not under `reports/`)
explaining every validation check in plain English.
Primary audience: someone who understands investing and the pipeline's purpose
but is not a mathematics expert.
Written once; updated only when new checks are added.

Structure — one block per check, always four sub-fields:

```markdown
# Feature Matrix Validation Guide

## What is this document?
This guide explains every check run by FeatureMatrixValidator before feature
selection. It describes what each check looks for, why it matters, and what
a failure means in practical terms. No formulas — plain English throughout.

## Why do we validate the feature matrix?
[Plain-English explanation: TO-DO 9 checked that the source data from SEC
EDGAR and price feeds was correct. This step checks that the code which
transformed that data into model inputs did its job correctly. Two clean
inputs can produce a broken output if the transformation code has a bug.
Give the sma_5_ratio ÷ near-zero example without math notation.]

## Layer 1 — Range Checks: "Is this value physically possible?"

### RSI (rsi_14)
**What it is:** RSI is a momentum indicator that measures whether a stock
has been bought or sold too aggressively recently. It was designed to always
produce a value between 0 and 100. An RSI of 110 is mathematically impossible
— the formula cannot produce it.

**What we check:** Every RSI value in the dataset must be between 0 and 100.

**What a failure means:** The RSI calculation in OhlcvFeatureEngineer has a
bug — likely a division where the denominator can become zero. The model must
not be trained until this is fixed.

**Severity:** FAIL-HARD — training stops.

### Piotroski F-Score (f_piotroski_f)
**What it is:** A financial quality score that counts how many of 9 specific
"yes/no" tests a company passes. The maximum possible score is 9 (passes all
tests); the minimum is 0 (passes none). It must be a whole number — there is
no such thing as a Piotroski score of 4.7.

**What we check:** Every Piotroski value is a whole number between 0 and 9.

**What a failure means:** The Piotroski calculator in FundamentalsFeatureEngineer
averaged something it should have summed, or a non-integer crept in through
a computation error.

**Severity:** FAIL-HARD — training stops.

### Rank Features (rank_ret_5d, rank_vol_20d)
**What it is:** These features express how a stock ranks among all 30 stocks
on a given day. The best-ranked stock gets 1.0, the worst gets 0.0 (or close
to it). By definition, a percentile rank cannot be above 1 or below 0.

**What we check:** Every value must be between 0.0 and 1.0.

**What a failure means:** The cross-sectional ranking code produced values
outside the valid range, which means the formula was applied incorrectly —
possibly using ordinal ranks (1 to 30) instead of percentile ranks (0 to 1).

**Severity:** FAIL-HARD — training stops.

## Layer 2 — NaN Pattern Checks: "Is missing data in the right places?"

### Price Features (ret_1d, rsi_14, sma_5_ratio, etc.)
**What it is:** These 14 features are computed from daily stock prices, which
we have for every single trading day. There is no reason any of them should
ever be missing.

**What we check:** None of the 14 price features have any missing values.

**What a failure means:** The feature engineering step failed silently for
some rows — perhaps a rolling-window calculation did not have enough history
at the start of the data, or an edge case was not handled.

**Severity:** FAIL-HARD — training stops.

### Fundamental Features (f_net_margin, f_roa, etc.)
**What it is:** These features come from quarterly earnings reports. Companies
report earnings four times a year, not every day. On days when no new report
has been filed, the feature carries forward the last known value. This means
missing data (NaN) is expected at the start of each ticker's history before
its first filing. A certain percentage of missing values is completely normal.

**What we check:** The fraction of missing values falls within an expected range.
Too low (near 0%) is suspicious — it suggests the forward-fill ran incorrectly
and invented data. Too high (above 90%) suggests the column was never populated.

**What a failure means:** Either the ETL did not fetch filings for most tickers,
or the forward-fill step in the feature engineering code was not applied.

**Severity:** WARN (configurable to FAIL).

## Layer 3 — Distribution Checks: "Is the shape of this data what we expect?"

### Rank Uniformity
**What it is:** When we rank 30 stocks each day, on average each rank position
(1st, 2nd, ..., 30th) should appear equally often across all days. This means
the distribution of rank values should look like a flat histogram — all bars
roughly the same height. We call this a "uniform distribution."

**What we check:** A statistical test (KS test) measures how far the observed
distribution of rank values departs from a perfect flat distribution. If the
departure is too large, the ranking code has a systematic bias.

**What a failure means:** The ranking calculation consistently favours certain
rank positions. For example, if the code used the wrong groupby key, all stocks
might get a rank near 0.5 regardless of their actual performance. This makes
the rank feature nearly useless as a signal.

**Severity:** FAIL if the departure is extreme; WARN if moderate.

## Layer 4 — Leakage Screen: "Did we accidentally use tomorrow's data today?"

**What it is:** The model is supposed to learn from today's data to predict
next week's stock performance. If any feature was accidentally built using
information that only exists in the future — for example, including next week's
closing price in today's moving average calculation — the model "cheats."
In training it appears to predict perfectly. In live trading it fails completely
because the future data does not yet exist.

**What we check:** We measure the statistical relationship (correlation) between
each feature and the future outcome (next week's return rank). A feature that is
genuinely computed from today's data should have only a modest relationship with
next week's outcome. A correlation above 0.85 is a red flag — only a feature
that accidentally contains next week's prices would show this level of connection.

**What a failure means:** One of the feature engineering formulas used a future
date when it should have used the current date. The most common cause is an
off-by-one error in a rolling window or a return calculation that accidentally
shifted forward by one row.

**Severity:** FAIL-HARD — training stops. Even one leaky feature destroys the
validity of all trained models.
```

---

### Integration into `main_train.py`

```python
# In train_fundamental_models_with_combined_features():
# AFTER feature engineering, BEFORE feature selection (TO-DO 8):

from pipeline.ohlcv.dataset.feature_matrix_validator import FeatureMatrixValidator

fmv = FeatureMatrixValidator(config)
fm_report = fmv.validate(
    df=feature_matrix,            # output of OhlcvFeatureEngineer + merge
    label_col="rank_label_1w",
    report_dir=run_dir / "feature_validation",
)

if fm_report["fail_hard_triggered"]:
    logger.error("Feature matrix validation FAILED. Training aborted.")
    logger.error("Blocking errors: %s", fm_report["blocking_errors"])
    raise RuntimeError(
        "Feature matrix validation gate failed — see feature_validation_report.md"
    )

if fm_report["overall_status"] == "WARN":
    logger.warning(
        "Feature matrix warnings present. "
        "Review feature_validation_report.md before relying on results."
    )
```

### New config section

```yaml
# settings.yaml
feature_validation:
  enabled: true
  fail_on_warn: false
  range_invariants:
    rsi_14_min: 0.0
    rsi_14_max: 100.0
    rank_min: 0.0
    rank_max: 1.0
    vol_max: 1.0
    macd_hist_soft_max: 50.0
    sma_ratio_soft_min: 0.50
    sma_ratio_soft_max: 2.00
    soft_violation_rate_threshold: 0.01   # warn if > 1% of rows violate soft bound
  nan_patterns:
    price_features_max_nan_rate: 0.0      # must be exactly 0
    fundamental_min_nan_rate: 0.05        # any f_* at 0% is impossible
    fundamental_max_nan_rate: 0.90        # any f_* above 90% was not populated
  distribution_checks:
    rank_uniformity_ks_threshold: 0.10
    rank_uniformity_p_threshold: 0.001
    min_coverage_fraction: 0.50
  leakage_screen:
    fail_threshold: 0.85
    warn_threshold: 0.60
    cross_lag_warn_threshold: 0.50
  llm_interpretation:
    enabled: false
    model: "claude-haiku-4-5-20251001"
```

### Acceptance criteria

- `FeatureMatrixValidator.validate()` runs without error on the existing dataset.
- Layer 1 hard-bound check: a unit test injects one row with `rsi_14 = 110` and
  verifies FAIL-HARD triggers.
- Layer 2 zero-NaN check: a unit test injects NaN into `ret_1d` and verifies
  FAIL-HARD triggers.
- Layer 3 rank uniformity: on the existing dataset, `rank_ret_5d` and
  `rank_vol_20d` pass the KS test (expected: roughly uniform on real data).
- Layer 4 leakage: a unit test injects a synthetic feature equal to
  `label + N(0, 0.01)` (corr ≈ 0.99) and verifies FAIL-HARD triggers.
- `feature_matrix_validation.json` is written to `reports/<timestamp>/feature_validation/`.
- `feature_validation_report.md` contains all five sections described above.
- `docs/feature_validation_guide.md` is written and covers every check with
  a What / Why / Failure meaning / Severity block. No mathematical notation —
  prose and examples only.
- Training proceeds normally when all checks pass.
- Training aborts with a clear error message when any FAIL-HARD triggers.
- `FeatureMatrixValidator` is read-only — it never modifies the feature matrix.
- Validation completes in < 60 seconds on the full 76,937-row dataset.
- All existing tests pass.
- When `llm_interpretation.enabled = false` (default), no LLM call is made.

> **TO-DO 11 Integration Note**: `FeatureMatrixValidator.validate()` is called in
> two contexts by `main_pipeline.py`:
> (a) Once in Phase 2 (full training): `report_dir = run_dir / "training" / "feature_validation"`
> (b) Once per fold in Phase 3b walk-forward (Option B):
>     `report_dir = run_dir / "backtest_walk_forward" / f"fold_{n}" / "feature_validation"`
> Same constraint as TO-DO 9: `report_dir` is always passed from outside.
> Never construct internal timestamps. A FAIL-HARD from Phase 2 or any fold in Phase 3b
> must abort that phase immediately and be recorded in `pipeline_summary.json`.

---

## TO-DO 11 — `main_pipeline.py`: End-to-End Training + Backtest Orchestrator

### Background and motivation

`main_train.py` and `main_backtest.py` (walk-forward mode) each implement their own
feature engineering, label building, and model training logic. Bugs fixed in one entry
point silently persist in the other. Running them separately also creates an audit gap:
a `ranker.pkl` saved Monday morning could be evaluated by a backtest run Thursday
afternoon after the code has changed, producing misleading metrics.

The orchestrator solves three problems simultaneously:

1. **Code-version discrepancy**: extract a `TrainingPipeline` class called by both
   entry points — one change propagates everywhere.
2. **Auditability**: all phases of one run share a single timestamp folder. Every
   report, model artifact pointer, and metric file is co-located and traceable.
3. **Option B walk-forward**: per-fold feature validation and selection are enforced
   by design, not left as an optional future improvement.

---

### New files

```
pipeline/
  main_pipeline.py                              ← orchestrator entry point
  ohlcv/
    training/
      training_pipeline.py                      ← TrainingPipeline + TrainingArtifacts
    reports/
      pipeline_reporter.py                      ← Phase 4 report aggregation
```

---

### `TrainingPipeline` class

Extract the shared training logic from both `main_train.py` and `main_backtest.py`
into a single class. Both entry points import and call it — neither reimplements
feature engineering, labelling, or model training independently.

```python
# pipeline/ohlcv/training/training_pipeline.py

@dataclass
class TrainingArtifacts:
    ranker:            BaseModel
    regressor:         BaseModel
    classifier:        BaseModel
    selector:          SlotSelector           # with optimised coefficients
    selected_features: List[str]
    report_dir:        Path                   # where this fold's reports were written
    fold_id:           Optional[int] = None   # None for the full-training Phase 2 pass


class TrainingPipeline:
    """
    Single source of truth for the full training pass.
    Called once by Phase 2 (full training) and once per fold by Phase 3b (walk-forward).
    All report paths are injected — this class never constructs timestamps.
    """

    def __init__(self, config: Dict):
        self.config = config

    def train(
        self,
        df: pd.DataFrame,
        label_col: str,
        report_dir: Path,
        fold_id: Optional[int] = None,
    ) -> TrainingArtifacts:
        """
        Full training pass in order:
          1. FeatureMatrixValidator     (TO-DO 10) — FAIL-HARD gates remainder
          2. FeatureSelectionPipeline   (TO-DO 8)  — selects features, writes report
          3. Train ranker, regressor, classifier on selected_features
          4. SlotSelector.optimize_coefficients()
        Returns TrainingArtifacts.
        """
```

**Why a dataclass return, not side-effects**: Phase 3b needs to receive the trained
models back from each fold's call to `train_fold()`. Returning a dataclass makes
the data flow explicit and testable, instead of relying on file paths being written
and re-read between folds.

---

### Phase 1 — Data Quality Validation

```python
def run_phase1(run_dir: Path, config: Dict) -> None:
    from pipeline.ohlcv.dataset.data_quality_validator import DataQualityValidator

    validator = DataQualityValidator(config)
    report = validator.validate(
        df=load_combined_features(config),
        train_cutoff_date=config["pipeline"]["train_cutoff_date"],
        report_dir=run_dir / "data_quality",
    )
    if report["fail_hard_triggered"]:
        raise RuntimeError(
            f"Phase 1 FAILED — data quality gate. "
            f"See {run_dir}/data_quality/data_quality_report.md"
        )
```

A FAIL-HARD in Phase 1 aborts the entire pipeline. Phases 2, 3a, 3b, and 4 do not run.

---

### Phase 2 — Full Training

```python
def run_phase2(run_dir: Path, config: Dict) -> TrainingArtifacts:
    pipeline = TrainingPipeline(config)
    artifacts = pipeline.train(
        df=load_combined_features(config),
        label_col="rank_label_1w",
        report_dir=run_dir / "training",
    )
    # Persist production model artifacts
    artifacts.ranker.save(MODEL_DIR / "ranker.pkl")
    artifacts.regressor.save(MODEL_DIR / "regressor.pkl")
    artifacts.classifier.save(MODEL_DIR / "classifier.pkl")
    save_policy_params(artifacts.selector, MODEL_DIR / "policy_params.json")
    save_selected_features(artifacts.selected_features, MODEL_DIR / "selected_features.json")
    return artifacts
```

Phase 2 is the only phase that writes production model artifacts to `data/ohlcv_models/`.
Phase 3b trains fold-specific models that are used and discarded within Phase 3b — they
are never written to `data/ohlcv_models/`.

---

### Phase 3a — Single-Split Backtest

Loads the production artifacts saved in Phase 2. Tests the specific trained model on
the held-out date range. This is model evaluation, not strategy evaluation.

```python
def run_phase3a(run_dir: Path, config: Dict, artifacts: TrainingArtifacts) -> None:
    backtester = Backtester(
        config,
        ranker=artifacts.ranker,
        regressor=artifacts.regressor,
        classifier=artifacts.classifier,
        selector=artifacts.selector,
        fundamental_scores=load_fundamental_scores(config),
        report_dir=run_dir / "backtest_single_split",
    )
    backtester.run(
        df=load_feature_matrix(config, features=artifacts.selected_features),
        start_date=config["pipeline"]["train_cutoff_date"],
        end_date=config["pipeline"]["end_date"],
    )
```

---

### Phase 3b — Walk-Forward Backtest (Option B)

Option B: every fold runs the full training pipeline including feature validation
(TO-DO 10) and feature selection (TO-DO 8). This is intentionally slower than Option A.
It produces per-fold feature selection reports, enabling `feature_stability_across_folds.csv`
in Phase 4.

```python
def run_phase3b(run_dir: Path, config: Dict) -> None:
    folds = make_wf_folds(config)           # same fold logic as current main_backtest.py
    wf_equity_curves = []
    all_fold_features = {}                  # fold_n → selected_features list

    for fold_n, (train_df, val_df) in enumerate(folds):
        fold_dir = run_dir / "backtest_walk_forward" / f"fold_{fold_n}"

        # Full training pass for this fold (Option B: validation + selection per fold)
        pipeline = TrainingPipeline(config)
        fold_artifacts = pipeline.train(
            df=train_df,
            label_col="rank_label_1w",
            report_dir=fold_dir,            # feature_validation/ and feature_selection/
            fold_id=fold_n,                 # stored in TrainingArtifacts for tracing
        )
        all_fold_features[fold_n] = fold_artifacts.selected_features

        # Run backtest on this fold's validation window using this fold's models
        backtester = Backtester(
            config,
            ranker=fold_artifacts.ranker,
            regressor=fold_artifacts.regressor,
            classifier=fold_artifacts.classifier,
            selector=fold_artifacts.selector,
            fundamental_scores=load_fundamental_scores_as_of(
                config, as_of_date=val_df["date"].min()   # point-in-time scores (TO-DO 3)
            ),
            report_dir=fold_dir / "backtest",
        )
        fold_equity = backtester.run(
            df=val_df[["date", "ticker"] + fold_artifacts.selected_features + ["rank_label_1w"]],
            start_date=val_df["date"].min(),
            end_date=val_df["date"].max(),
        )
        wf_equity_curves.append(fold_equity)

    # Stitch fold equity curves (rescaling, same as current wf logic)
    stitched_equity = stitch_equity_curves(wf_equity_curves)
    stitched_equity.to_csv(
        run_dir / "backtest_walk_forward" / "aggregate" / "wf_equity_curve.csv"
    )

    # Feature stability table
    save_feature_stability(
        all_fold_features,
        path=run_dir / "backtest_walk_forward" / "aggregate" / "feature_stability_across_folds.csv",
    )
```

---

### `feature_stability_across_folds.csv`

One row per feature, one column per fold. Shows which features were consistently
selected across all folds vs. which were selected only in some.

```
feature                  | fold_0 | fold_1 | fold_2 | fold_3 | fold_4 | fold_5 | fold_6 | n_folds_selected
-------------------------|--------|--------|--------|--------|--------|--------|--------|------------------
rank_ret_5d              |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |        7
rsi_14                   |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |        7
f_net_margin             |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✗    |   ✓    |        6
f_revenue_chg_1          |   ✓    |   ✗    |   ✓    |   ✗    |   ✓    |   ✗    |   ✓    |        4
f_accruals               |   ✗    |   ✓    |   ✗    |   ✗    |   ✗    |   ✗    |   ✗    |        1
```

This is the key deliverable of Option B. Features selected in 7/7 folds are
temporally stable — their signal is consistent across market regimes. Features
selected in 1/7 folds are regime-specific — useful context for deciding whether
to tighten `min_models` or `max_nan_rate` in TO-DO 8's configuration.

---

### Phase 4 — Report Aggregation

Reads the JSON outputs from all phases and assembles a one-page master report.
No computation — pure reading and formatting.

```python
def run_phase4(run_dir: Path) -> None:
    from pipeline.ohlcv.reports.pipeline_reporter import PipelineReporter
    reporter = PipelineReporter(run_dir)
    reporter.generate()
```

#### `pipeline_summary.json` schema

```json
{
  "run_timestamp": "2026-04-21T14:33:10",
  "mode": "fundamental",
  "flags": {
    "fundamental_overlay": true,
    "fundamental_scores_path": "data/fundamentals/fundamental_scores_panel.parquet",
    "skip_etl": false
  },
  "phase1_data_quality": {
    "status": "PASS",
    "warnings": 2,
    "report": "data_quality/data_quality_report.md"
  },
  "phase2_training": {
    "status": "PASS",
    "features_selected": 31,
    "selected_features": ["rank_ret_5d", "rsi_14", "f_net_margin", "..."],
    "report": "training/feature_selection/feature_selection_report.md"
  },
  "phase3a_single_split": {
    "status": "PASS",
    "sharpe": 1.18,
    "max_drawdown": -0.214,
    "total_return": 0.623,
    "report": "backtest_single_split/"
  },
  "phase3b_walk_forward": {
    "status": "PASS",
    "n_folds": 7,
    "aggregate_sharpe": 1.42,
    "aggregate_max_drawdown": -0.183,
    "aggregate_total_return": 1.471,
    "overlay_downgrades_total": 23,
    "feature_stability_report": "backtest_walk_forward/aggregate/feature_stability_across_folds.csv",
    "report": "backtest_walk_forward/aggregate/"
  },
  "overall_status": "PASS"
}
```

#### `pipeline_summary.md` content

```markdown
# Pipeline Run: 2026-04-21 14:33:10
## Configuration
Mode: fundamental | Overlay: ON | Scores: fundamental_scores_panel.parquet

## Phase 1 — Data Quality: PASS
2 warnings (see data_quality/data_quality_report.md for details)

## Phase 2 — Training: PASS
31 of 58 features selected
Top features: rank_ret_5d, rsi_14, f_net_margin, ret_5d, f_piotroski_f
Full feature report: training/feature_selection/feature_selection_report.md

## Phase 3a — Single-Split Backtest
Sharpe: 1.18 | Max Drawdown: -21.4% | Total Return: +62.3%
Tests: the specific ranker.pkl + regressor.pkl + classifier.pkl trained in Phase 2

## Phase 3b — Walk-Forward Backtest (7 folds, Option B per-fold selection)
Sharpe: 1.42 | Max Drawdown: -18.3% | Total Return: +147.1%
Overlay downgrades across all folds: 23
Stable features (selected in 7/7 folds): rank_ret_5d, rsi_14, ret_5d, f_net_margin
Unstable features (selected in ≤3/7 folds): f_accruals, f_revenue_rolling_chg_4
Feature stability detail: backtest_walk_forward/aggregate/feature_stability_across_folds.csv

## Artifacts
Production models: data/ohlcv_models/{ranker,regressor,classifier}.pkl
Policy params:     data/ohlcv_models/policy_params.json
Selected features: data/ohlcv_models/selected_features.json
```

---

### Folder structure

```
reports/
  2026-04-21_14-33-10/
    data_quality/                          ← Phase 1
      data_quality_summary.json
      data_quality_report.md
      anomaly_rows.csv
      staleness_distribution.csv
    training/                              ← Phase 2
      feature_validation/
        feature_matrix_validation.json
        feature_validation_report.md
      feature_selection/
        feature_selection_summary.csv
        feature_selection_report.md
        selected_features.json
    backtest_single_split/                 ← Phase 3a
      backtest_metrics.csv
      backtest_equity_curve.csv
      backtest_equity_curve.png
      backtest_drawdown.png
    backtest_walk_forward/                 ← Phase 3b
      fold_0/
        feature_validation/
          feature_matrix_validation.json
          feature_validation_report.md
        feature_selection/
          feature_selection_summary.csv
          feature_selection_report.md
          selected_features.json
        backtest/
          backtest_metrics.csv
          backtest_equity_curve.csv
      fold_1/ ... fold_6/  (same structure)
      aggregate/
        wf_equity_curve.csv
        wf_metrics.csv
        wf_backtest_results_with_overlay.csv
        feature_stability_across_folds.csv ← Option B deliverable
    pipeline_summary.json                  ← Phase 4
    pipeline_summary.md                    ← Phase 4
```

---

### Entry point and arguments

```bash
python -m pipeline.main_pipeline \
    --mode fundamental \
    --fundamental-overlay \
    --fundamental-scores-path data/fundamentals/fundamental_scores_panel.parquet \
    [--skip-etl]
```

| Argument | Type | Description |
|----------|------|-------------|
| `--mode` | choice: `price`, `fundamental`, `both` | Inherited from TO-DO 7. Controls what main_train's Phase 2 does. |
| `--fundamental-overlay` | flag | Enables overlay in Phase 3a and Phase 3b. No effect when absent. |
| `--fundamental-scores-path` | path | Path to scores panel (TO-DO 3). Ignored when `--fundamental-overlay` is absent. |
| `--skip-etl` | flag | Inherited from TO-DO 7. Skips SEC EDGAR fetch in Phase 2. |

Both Phase 3a (single-split) and Phase 3b (walk-forward) always run — they are not
controlled by separate flags. The pipeline always produces two backtest reports.

---

### Files to create

- `pipeline/main_pipeline.py` — entry point, `main()` with arg parsing and phase dispatch
- `pipeline/ohlcv/training/training_pipeline.py` — `TrainingPipeline` class + `TrainingArtifacts` dataclass
- `pipeline/ohlcv/reports/pipeline_reporter.py` — `PipelineReporter` class for Phase 4

### Files to refactor

- `pipeline/main_train.py` — dispatch functions must accept `run_dir: Path` and return `TrainingArtifacts`
- `pipeline/main_backtest.py` — walk-forward logic moves to `TrainingPipeline`; `Backtester` must accept `report_dir: Path`

---

### Prerequisites

Implement TO-DO 7, 8, 9, 10 before this task. All four must be complete because
`TrainingPipeline.train()` calls all of them internally. TO-DO 3 (scores panel)
must be complete for `load_fundamental_scores_as_of()` to work in Phase 3b.

---

### Acceptance criteria

- `python -m pipeline.main_pipeline --mode fundamental --fundamental-overlay` runs
  end-to-end without error on the existing dataset.
- All four phases execute in order. A FAIL-HARD in any phase aborts all subsequent phases.
- Phase 2 and Phase 3b both call `TrainingPipeline.train()` — the training code is
  not duplicated between `main_pipeline.py` and `main_backtest.py`.
- Phase 3a uses the model artifacts saved by Phase 2 (not retrained).
- Phase 3b retrains fresh models per fold via `TrainingPipeline.train()` (not the Phase 2 artifacts).
- All report files land under the same `reports/<ts>/` folder.
- `pipeline_summary.json` is written and contains valid Phase 1–3b metric fields.
- `pipeline_summary.md` is human-readable and contains the key metrics for all phases.
- `feature_stability_across_folds.csv` is produced with one row per feature and
  one boolean column per walk-forward fold.
- Stable features (selected in all folds) are correctly identified.
- Running `main_train.py` and `main_backtest.py` standalone (outside the orchestrator)
  still works — backward compatibility is preserved.
- All existing tests pass.

---

- **DO-NOT-BREAK rule**: `main_inference.py` and `main_backtest.py` must continue to
  work with the existing `fundamental_scores.json` if the new panel parquet does not
  yet exist. Every new component must degrade gracefully.
- **No test rewriting**: If existing tests pass before your changes, they must pass after.
- **No schema changes** to `combined_features_for_fundamental_training.parquet` or
  `fundamental_training_data.parquet`. Both files are inputs, not outputs of these tasks.
- TO-DO 3 is a **prerequisite** for TO-DO 4. Implement them in order.
- TO-DO 5 is independent and can be done at any time.
- TO-DO 6 depends on the overlay code being stable — implement after TO-DO 4 if possible.
- TO-DO 1 and TO-DO 2 are independent and can be done in any order.
- TO-DO 7, 8, 9, 10 are **prerequisites** for TO-DO 11. Implement them in order.
