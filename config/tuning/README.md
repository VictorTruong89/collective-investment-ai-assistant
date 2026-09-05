# Feature 3-c — per-model tuning sweeps

Per-model hyperparameter tuning (rel5_features.md §3c). Each YAML here is **one
model, one role** sweep (coordinate descent, §3c.4) run through the existing
experiment entrypoint:

```bash
python -m pipeline.main_pipeline --mode experiment --experiments config/tuning/<file>.yaml
```

Every run writes to `reports/experiments/<ts>/`:

| file | what |
|---|---|
| `leaderboard.csv` / `.md` | every variant ranked, full metric set |
| `tuning_report.md` | the mandatory §3c.9 record: provenance, search space, validation setup, per-unit leaderboard, **selection trace**, winner-vs-default verdict, diagnostics |
| `tuning_report.json` | machine-readable mirror (drives the cross-model roll-up) |
| `experiments_used.yaml` / `run_meta.json` | verbatim configs + seeds + lib versions |

## Two-stage workflow (§3c.8)

1. **Screen** (cheap) — `validation.scheme: walk_forward`, `max_folds: 2`.
   Cheap models run a full coarse grid; deep models random-sample ~12 cells.
   Deep grids **must run on the `tf_gpu` box**.
2. **Validate** (full budget) — promote the top ~3 survivors to
   `validation.scheme: cpcv` (N=6, k=2 → 15 splits / 5 paths, purge + embargo).
   Selection reads the **path distribution** (mean − 0.5·path-σ), gated on ICIR.

`lgbm_ranker.yaml` shows the CPCV (Stage-2) form; `ft_transformer_ranker.yaml`
shows the walk-forward (Stage-1) screen for a deep model.

## Selection rule (§3c.1) — per role

| role swept | `selection.metric` | `selection.gate` |
|---|---|---|
| ranker | `pred_rank_ic_mean` | `pred_rank_ic_ir` ≥ 0.3 |
| classifier | `pred_auc` | — (add `pred_brier` as a min-secondary) |
| regressor | `pred_reg_ic_mean` | — |

## Generating / editing a grid

These files are produced by `grid_gen.expand_grid` from a compact spec — edit the
spec and regenerate rather than hand-editing the expanded `variants:` blocks:

```python
from pipeline.ohlcv.experiments.grid_gen import expand_to_yaml_block
print(expand_to_yaml_block({
    "base": {"backend": "lightgbm", "paradigm": "separate", "role": "ranker",
             "fixed": {"num_boost_round": 500, "early_stopping_rounds": 50}},
    "id_prefix": "lgbm_rk", "search": "grid",   # or "random(12)"
    "grid": {"num_leaves": [15, 31, 63],
             "min_data_in_leaf": [20, 50, 100],
             "learning_rate": [0.02, 0.05, 0.10]},
}))
```

## Cross-model roll-up (§3c.7 P3)

After several sweeps, concatenate each one's recommended winner into one table:

```python
from pathlib import Path
from pipeline.ohlcv.experiments import rollup_tuned_winners
rollup_tuned_winners(sorted(Path("reports/experiments").glob("*/tuning_report.json")),
                     Path("reports/experiments/tuned_winners.md"))
```
