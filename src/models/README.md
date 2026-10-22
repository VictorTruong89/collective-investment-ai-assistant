# D-04 — the selection model (`src/models/`)

An operator's page: what D-04 is, the commands to run it, and the decisions that shape it. Not a spec — the rules
are in [`sdd/design/rel6_design/L1-model-training.md`](../../sdd/design/rel6_design/L1-model-training.md) (`MT-n`)
and [`sdd/specs/F12_quant_core/spec.md`](../../sdd/specs/F12_quant_core/spec.md). The cross-domain order of work
(statements → data → train → card → thesis) is the root [`README.md`](../../README.md) runbook; this page owns the
D-04 detail.

## 1 · What D-04 is

The selection model ranks the ~500 S&P 500 names by their expected return over the next **21 trading days**.
It **nominates, it never decides**: the top name goes to the card, where D-12 composes a verdict and the human decides.
It sits between D-02 (which builds the features and labels it reads) and D-03 (which grades it and owns the gates).

**Status (2026-10-11): functionally complete, skill unproven.** Every step below works end to end; no fit has passed
its gates. The best one, fit 4 (`sha256:8200ada7…`), ranks the card as a *refused* model, labelled as one.

---

## 2 · ★ Quick start — the default commands

Three steps, in this order, on the **same day** (the calendar check needs today's event sweep).

```bash
set -a; source .env; set +a                                           # every new terminal
```

**1 · Collect data** — the SEC ticker snapshot, then ten years of corporate actions for the S&P 500. ~70 min.

```bash
python -m src.data_engine.ingest symbols --universe sp500
python -m src.data_engine.ingest events  --universe sp500 --years 10
python -m src.data_engine.ingest status
```

**2 · Train — and backtest.** Fits the model, then runs the out-of-sample measurements, the portfolio simulation and
the three gates, and prints the artifact id. ~21 min.

```bash
python -m src.models.train
```

**3 · Read the report, then decide.** Shows the gate report saved by step 2; changes nothing.

```bash
python -m src.models.promote <artifact_id>
```

⚠ **Training and backtesting are ONE command.** `src.models.train` fits the model *and* grades it; there is no
separate backtest run. Step 3 is reading what step 2 measured — then, if you choose, `--approve` (only possible if every
gate passed) or `--card-informational` (a refused model ranks the card, labelled). See §4.

---

## 3 · What the run prints, and how to read it

Every 15 s it prints `⏱ train · … elapsed · now: <stage>` to stderr, each stage's duration as it ends, and the total.
The stages, in order:

| # | Stage | What it does |
|---|---|---|
| 1 | fundamentals (EDGAR) | ingests companyfacts for every name (skipped with `--skip-facts`) |
| 2 | prices (FMP) | raw daily bars; names that fail get one retry pass after 10 s (DE-80), then are named |
| 3 | calendar check | D-07's corporate-action gate over the window. A **HALT** (e.g. an unhandled delisting) stops the run, naming each event (MT-54). **0 classes checked** is refused (MT-57) |
| 4 | features panel | GICS sectors (today's map, DE-77); splits and dividends applied (DE-78 — the count printed is those **inside the window**); a name whose events contradict its prices is left out by name (KDP, DE-79); 61 features, fundamentals replayed per filing date (FE-40) |
| 5 | labels | the 21-day open-to-open return |
| 6 | fit | LightGBM on each day's return **rank** as a normal score (`xs_gauss`, MT-59) |
| 7 | out-of-sample · purged k-fold | trains on both sides of each test block. **Reported**; feeds only the simulation |
| 8 | out-of-sample · walk-forward | trains on the past only. **This is what the gates read** (F12 `D14`) |
| 9 | portfolio simulation | top-N book, held names drift, $0 commission (F12 `D6`, `D8`) |
| 10 | breadth | the universe's correlation, and the residual after SPY / sector SPDRs (12 FMP calls, F12 `D12`) |
| 11 | D-03 evaluation + gates | the three gates, then the artifact is written and **held for review** |

**The three gates** (F12 — the bars are fixed and do not move, `D16`):

| Gate | Passes when | Fit 4 |
|---|---|---|
| `ic_significance` | walk-forward `|mean IC| ≥ 3 × realised SE` (Newey-West) — `D9`, `D14` | ✗ IC 0.0296, t 2.51 (needs 0.0353) |
| `breadth` | implied IR `|IC| · √BR ≥ 0.5`, BR from the residual correlation after SPY — `D10`, `D13` | ✗ IR 0.421 |
| `cost_survival` | net simulated return > 0 | ✓ |

The run ends with `artifact: sha256:…`, the verdicts, and either `NOT PROMOTED — refused on [...]` or
`ALL GATES PASSED — HELD FOR REVIEW`. ⚠ A refused artifact is still written: it is a record.

⚠ **The simulated return is survivorship-biased** — the universe is today's index, which keeps the names that won.
Every backtest is stamped `BIASED`. **Do not quote it** (PG-10). The IC is the number that matters.

---

## 4 · Every argument

### `python -m src.models.train`

| Flag | Default | What it does | When to use it |
|---|---|---|---|
| `--as-of DATE` | today's **New York** date (MT-56) | the last day of the window | re-running a past day |
| `--years N` | `10` | window length | rarely — the record is on 10 |
| `--limit N` | all names | keep the first N names | **smoke run only** — not a fit |
| `--horizon-days N` | `21` | the label horizon | never — the selection model refuses any other |
| `--capital X` | `100000` | the book the cost gate is measured against | to measure at your real book size |
| `--refresh-events` | off | re-sweeps **only** splits, reverse splits and dividends inline | when step 1's sweep was not today; other classes then read unchecked |
| `--skip-facts` | off | reuse the stored fundamentals | a retrain the same week; saves ~5 min |
| `--prepare-only` | off | build panel and labels, then stop — no fit | the smoke test |
| `--target {xs_gauss,raw}` | `xs_gauss` | what the trees fit: each day's return rank, or the raw return | `raw` reproduces fits 1–2 |
| `--allow-unchecked-calendar` | off | train even when the calendar check covered nothing | avoid; the artifact then says it has no calendar guarantee |

### `python -m src.models.promote <artifact_id>`

| Flag | What it does |
|---|---|
| *(none)* | show the gate report; changes nothing |
| `--approve` | promote — **refused unless every gate passed**; there is no override (MT-17, MT-52) |
| `--card-informational` | let this **refused** model rank the card, labelled REFUSED with its failed gates (MT-67). Refused for a model that passed (promote it instead) |
| `--card-informational-off` | revoke the designation; the card falls back to the momentum rule |
| `--models DIR` | model store (default `$PIPELINE_STATE_DIR/models`, else `.state/models`) |

### `python -m src.models.shadow` — the live trial (MT-64…66)

| Sub-command | What it does |
|---|---|
| `start <artifact_id>` | once — freezes the model and the pre-registered criterion. A second start is refused |
| `record [--as-of D] [--skip-facts] [--allow-unchecked-calendar] [--limit N]` | one write-once snapshot of the latest **completed** session, ≥ 21 trading days after the last. ~15–20 min |
| `score` | grades every snapshot whose 21 trading days have passed |
| `status` | the snapshots, live ICs, pooled t and the leakage alarm |

### Worked examples

```bash
# a smoke run: 20 names, data + panel + labels, no fit (minutes)
python -m src.models.train --limit 20 --prepare-only

# a retrain that reuses this week's fundamentals
python -m src.models.train --skip-facts

# reproduce the old target (fits 1–2)
python -m src.models.train --target raw
```

---

## 5 · The decisions that shape D-04

| Decision | Date | Where |
|---|---|---|
| ★ **Done = functional, skill unproven.** The gates stay measurements, no threshold moves; lowering them was rejected | 2026-10-11 (Victor, option Ⓐ) | F12 `D16`, MT-68 |
| The gates: walk-forward t ≥ 3; IR ≥ 0.5 on market-only residual breadth; net return > 0 | 2026-10-06…08 | F12 `D9`, `D10`, `D13`, `D14` |
| Training never promotes itself; it holds for review, and `--approve` cannot override a failed gate | 2026-10-06 | MT-52, MT-17 |
| Retraining is manual — run by Victor, by hand | 2026-10-05 | L9 go-live checklist §5 |
| A refused model may rank the card, labelled; such a card is never actionable | 2026-10-09 | MT-67, OR-58, F12 `D15`, DN-41, RP-55 |
| The shadow trial: fit 4 frozen, scored live; pooled t ≥ 3 meets the bar, a leakage alarm from 6 observations. Meeting it does not promote | 2026-10-09 | MT-64…66 |
| **No more fits on 2016–2026** unless Victor asks — then ONE pre-registered attempt, counted as attempt 5. No retrain or re-designation during the trial without saying what it does to the record | 2026-10-11 | MT-68, lecture L8 §8.3 |
| Declared limitations: survivorship (today's index), today's GICS map over the whole window, one model across all regimes | 2026-10-05…07 | F12 `D3`, DE-77, AB-3 |

---

## 6 · Where things land

```text
.state/models/                                   ($PIPELINE_STATE_DIR/models if set)
├── <artifact_id>/
│   ├── manifest.json        what was fitted: contract, window, target, calendar report
│   ├── features.json        the feature contract the card must match (INV-4)
│   ├── evaluation.json      every number: both ICs, folds, simulation, breadth, gates
│   └── estimator.pkl        the fitted trees
└── card_informational.json  which refused model ranks the card (MT-67) — absent ⇒ the rule ranks
.state/shadow/
├── trial.json               the frozen model and the pre-registered criterion
├── snapshots/<date>.json    one per observation, write-once
└── scores.jsonl             one line per matured snapshot
```

---

## 7 · Pointers

- Rules: [`sdd/design/rel6_design/L1-model-training.md`](../../sdd/design/rel6_design/L1-model-training.md)
- Evaluation and gates: [`sdd/specs/F12_quant_core/spec.md`](../../sdd/specs/F12_quant_core/spec.md)
- How the code works: [`sdd/blueprints/D-04-model-training.md`](../../sdd/blueprints/D-04-model-training.md)
- The teaching version: [`docs/lectures/L8-the-selection-model.html`](../../docs/lectures/L8-the-selection-model.html)
- The cross-domain runbook: root [`README.md`](../../README.md) → *Operating it by hand*
