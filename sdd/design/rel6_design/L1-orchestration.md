# L1: Domain Specification — Orchestration (D-08)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-08 · **Seat:** SEAT-5
> **Path:** `src/orchestration/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Authority:** **LEVEL 0 AUTONOMOUS** — no agent, no LLM, no judgement (L0 §3.1, AP-5)
> **Depends on:** may **invoke** any domain · **computes nothing**
> **Prior art:** `pipeline/main_pipeline.py` (683) · `main_inference.py` (809) · `main_buffett.py` (300) ·
> `etl/data_ingest_scheduler.py` (565) — **1,792 LOC of entrypoint, ungoverned by any F-spec**
> **Binding:** **INV-032**, **INV-033**, **INV-034**, INV-005, INV-006, INV-007 ·
> constitution **INV-2** (determinism), **P5** (fail loud), **DC-3**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.16.0 | 2026-08-27 | Victor | ★★★ **OR-50…52 — the manifest's provenance was entirely empty and a precondition was passing vacuously.** ⚠ *Measured on a real run:* `git_sha: ""`, `config_hash: ""`, `inputs: []`, and **`inputs_fresh: true` over ZERO inputs** — ★★ DE-56's shape inside the orchestrator's own preconditions. `git_state()` existed and the daily path never called it. **OR-50** states delivery's consequence: a failed send ends the run `INCOMPLETE`, and the CT-11.7 record is already on disk because `record` precedes `deliver`. AC-8.38…8.40. |
| 0.10.0 | 2026-08-27 | Victor | ★★ **OR-49 — the daily universe now matches the training one (AB-13).** The run scored 130 names with a model fitted on 497; rank and sector-z features are population-defined and **the column names match exactly**, so no contract check could see it. ★ `--universe` defaults to `sp500`; `watchlist` stays reachable. ⚠ Measured 510 names in **3 m 44 s**, and **COHR/TTD entered the top three** — the narrow list was hiding names the model scores above ARM and INTC. |
| 0.9.0 | 2026-08-26 | Victor | ★ **OR-48 — invoke D-11, never import it.** AC-8.2's substring check rejected the sanctioned `invokes`-plus-`resolve` seam as well as a real import, leaving **no legal path from the graph to the book**. `daily_inference` gains a `book` job (`v3`→**`v4`**) that `risk` now depends on, so D-05 reports **why** a book is unavailable instead of the B3 skeleton's stale reason. |
| 0.8.0 | 2026-08-25 | Victor | ⚠ **`assert_open_confirmed` demanded four OHLC fields and at 10:00 only one exists.** The opening auction is final at 09:30; the bar is not final until 16:00 (D-07 **DE-47**), so the check as written **would have blocked every run forever.** ★ **OR-47**: the precondition requires the **open**; the collapsed-bar test fires when all four *are* present and equal — which is exactly `main_inference.py:250`'s output, and OR-32's real concern. AC-8.30a added. |
| 0.7.0 | 2026-08-25 | Victor | ⚠⚠ **B6 readiness — three defects, and one rule could never fire.** ★★ **OR-44**: **AC-8.32 raises when a model was trained on a different anchor, and nothing declares a training anchor** — the manifest has `decision_anchor`, D-03's nomination has a hashed id and no anchor, D-04 is unbuilt. A model now **declares `trained_anchor` or blocks**, because *matching* and *unknown* are opposite findings. ★★ **OR-45**: **OR-16 forbids a human-facing artifact from an INCOMPLETE run and OR-19 requires a failed run to reach the human** — read together they cancel, and resolving it the wrong way makes failure **silent**. The line is what the message CLAIMS: a report asserts an analysis, a failure notice carries none. ★★ **OR-46**: **AC-8.37 cites the lock and the lock cannot deliver it** — two firings twenty minutes apart never overlap. A `cadence_key` claims the window; ⚠ a FAILED run does not claim it. AC-8.22a/8.32a/8.37a added. |
| 0.6.0 | 2026-08-23 | Victor | ⚠ **B3 readiness: BS-27 was unimplementable against CT-8.1.** L3 **BS-27** requires the B3 constant-`PASS` gate to be *"written into the RunManifest rather than being silently true"*, and **the contract declared no field for it** — the fourth instance of a rule asserting against an undeclared field. ★ **New OR-43 + `stubs[]`**, with `[]` as the explicit production value: *a stub indistinguishable from a real implementation in the record is how a placeholder survives into production.* AC-8.14a added. |
| 0.5.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit: `CT-8.1` did not declare `decision_anchor`** — while **OR-35** says it is declared there, **MT-42** fails the run on `manifest.decision_anchor != run_manifest.decision_anchor`, and **DN-23** asserts the same. **Three specs checked against a field the contract never declared**, so the gate that catches a systematic, metric-invisible anchor mismatch was unimplementable. Same shape as `adj_open` (D-07 DE-42). |
| 0.4.0 | 2026-08-18 | Victor | **OR-14a — the retry exception is now declared from this side too.** LLM calls happen inside D-01, so a 429 never reaches orchestration; the gateway retries transport beneath the domain layer (GW-15), obeys the same EH-15 classification, and its attempt count reaches the RunManifest. **Something had been relying on this unwritten.** |
| 0.3.0 | 2026-08-18 | Victor | **QO-7 closed: the label anchor moves to the open.** Cascaded into D-03 §5.9, D-04 §6.3 + §8.1, D-02 §5Z. |
| 0.2.0 | 2026-08-18 | Victor | **QO-3 and QO-5 closed on Victor's authority.** New **§5A — the production cadence**: daily **10:00 ET** off the **day-T open**, retrain on the **first trading day of each month**, in-process job graph behind a thin external timer. §5A records three collisions the decision exposes — the schedule **cannot be pinned in UTC** (it would run before the open all winter), the live-price splice **does not fetch the open and flattens OHLC to a single number**, and an open-anchored decision requires an **open-anchored label** (INV-4). §1.5 reframed: the entrypoints are **rebuilt, not migrated**. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft. **§1.2 states the eight tasks and the expectation for each** — the thing D-08 is *for*. §1.5 records the inherited boundary violation: the existing entrypoints are orchestrators **stuffed with domain work**, including a model fit, a CV-fold split, and **direct mutation of the book**. §1.5a shows a real production defect that this boundary failure *caused*. §7 draws the line P5 needs — **retry transport, never retry semantics**. §8 records that time budgets, retry policy, and run manifests are **entirely unbuilt** despite being D-08's stated purpose. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"What should run, when, in what order — and what actually happened when it did?"**

D-08 is **custody of the schedule**, the fifth back-office duty alongside custody of data (D-07),
of derived data (D-02), of the record (D-11) and of the artifact (D-09).

## 1.2 ★ THE TASKS — what D-08 must do, and what "done" means

The user-facing definition of this domain. **Eight tasks, each with a stated expectation.** Nothing
outside this list belongs to D-08; nothing inside it belongs to anyone else.

| # | Task | Expectation — what "done" looks like |
|---|---|---|
| **T-1** | **Trigger** — decide *that* a pipeline runs | A run starts only when its **preconditions hold**: the calendar says it is a trading day (D-07 §6A), inputs are fresh, no conflicting run is live. **A schedule that fires blindly is not a trigger, it is a timer** |
| **T-2** | **Sequence** — decide the order | Job dependencies are **declared data**, not control flow buried in a `main()`. The graph is inspectable without running it |
| **T-3** | **Run identity** — name the run | Every run has a **RunManifest**: run id, git sha, config hash, data `as_of`, seed, input digests. ★ **Without this a run cannot be reproduced, and INV-2 is unenforceable at the only layer that can enforce it** |
| **T-4** | **State & checkpoint** | A run's progress is durable. A resumed run **recomputes nothing already proven complete**, and a resume is **never** a way to skip a step that failed |
| **T-5** | **Failure handling & retry** | ★ **Transport is retried; semantics never are** (§7). A retried run is marked as retried. **Partial success is a failure**, not a partial result (P5, DC-3) |
| **T-6** | **Time budget** | Every job declares a deadline. Breach ⇒ the run is **failed and incomplete** — ★ never "emit what we have" (§8) |
| **T-7** | **Concurrency & mutual exclusion** | Two runs never mutate the same state concurrently. Re-running a completed job is **idempotent** |
| **T-8** | **Report the outcome** | The run outcome goes to **D-11** (the record) and is available to **D-09** (the artifact). ★ **A failed run must be visible as a failure, not as silence** |

> **T-3, T-5, T-6 and T-8 are the ones with the most value and the least existing code.** §8 records
> that retry policy, time budgets and run manifests are **not implemented anywhere in the repo** —
> zero occurrences of `retry`, `backoff`, `timeout` or `deadline` across all four entrypoints.

## 1.3 ★ The one rule that defines the domain

```text
╔══════════════════════════════════════════════════════════════════╗
║  ORCHESTRATION INVOKES WORK. IT NEVER PERFORMS WORK.             ║
║                                                                  ║
║  No analysis. No computation. No judgement. No model fit, no     ║
║  fold split, no threshold search, no selection, no rendering,    ║
║  and above all NO WRITE TO THE BOOK.                             ║
║                                                                  ║
║  If a scheduled job computes something, that computation belongs ║
║  to the domain that owns it — and the ONLY correct fix is to     ║
║  move it there, never to bless it because it already runs.       ║
║                                                                  ║
║  The reason is not tidiness. A computation inside an entrypoint  ║
║  has NO SPEC, NO OWNER and NO ACCEPTANCE CRITERIA — it is        ║
║  invisible to the whole SDD process by construction. §1.5a is    ║
║  a production defect that existed for exactly that reason.       ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.4 Position

```text
        ┌──────────────────────────────────────────────────────────┐
        │  D-08 ORCHESTRATION            SEAT-5 · LEVEL 0          │
        │  trigger · sequence · manifest · retry · budget · state  │
        └───┬──────────────────────────────────────────────────┬───┘
            │ invokes (one-way ↓)                              │
            ▼                                                  ▼
   D-07 · D-02 · D-01 · D-03 · D-04 · D-05 · D-06 · D-09 · D-11
            ▲                                                  │
            └── ✗ NO DOMAIN MAY IMPORT D-08 (OR-3) ────────────┘
                                                    outcome ──► D-11
```

## 1.5 ⚠ THE INHERITED VIOLATION — a rebuild inventory, not a migration plan

`main_pipeline.py` and `main_inference.py` are 1,492 lines of orchestrator that **do the work
themselves.** This is not a stylistic finding; every row below is a computation with no spec, no
owner and no AC.

> **Decided 2026-08-18 (Victor): L0 §4.3's rule stands unchanged, and both entrypoints are
> redesigned rather than repaired.** The table below is therefore a **rebuild inventory** — it says
> where each responsibility lands in `src/`, not how to refactor `pipeline/`. Nothing here is
> grandfathered: a rewrite that reproduces any of these rows in `src/orchestration/` has failed
> **OR-1**, and the rewrite is the moment when reproducing them is cheapest to avoid.

| Function | File:line | What it actually does | Belongs to |
|---|---|---|---|
| `_make_wf_folds` | `main_pipeline.py:542` | ★ **Walk-forward CV fold construction**, `fold_years=3, val_years=1` **hard-coded as defaults** | **D-04** (MT-*) / D-03 validation design |
| `_run_production_coefficient_fit` | `main_pipeline.py:482` | ★ **Fits the blend weights production runs on**, and persists them | **D-04** |
| `_run_threshold_optimization` | `main_pipeline.py:577` | Grid-search over overlay thresholds | **D-10** / D-03 |
| `run_phase3a/3b` | `main_pipeline.py:228,319` | Backtest execution and aggregation | **D-03** |
| `_build_inference_features`, `_feature_coverage` | `main_inference.py:346,299` | Feature construction and coverage checks | **D-02** |
| `_append_live_prices` | `main_inference.py:250` | Price fetch and splice into the panel | **D-07** |
| `_is_market_open_et` | `main_inference.py:236` | Market-calendar logic | **D-07** (§6A calendar check) |
| `_select_top_buffett_candidates` | `main_inference.py:508` | ★ **Selection — a judgement** | **D-01 / the combine point** |
| `_write_inference_report`, `_write_inference_markdown` | `main_inference.py:60,140` | Renders the human-facing artifact | **D-09** |
| ★ `_load_positions` / `_save_positions` / `_update_sleeves` / `_save_sleeves` | `main_inference.py:418–507` | ★★ **Reads and WRITES the position and sleeve state** | ★★ **D-11 — custody of the fact** |

> **The last row is the most serious.** The inference orchestrator **mutates the book**. D-11 is
> LEVEL 0 custody of what actually happened; an inference run writing `positions.json` means a
> *prediction* is editing the *record*. That is the same failure shape as ST-9 (a renderer upstream
> of the book) with a worse actor — and it is why **OR-2** exists.

## 1.5a ★ The defect this boundary failure caused — and it is documented in the code

`_run_production_coefficient_fit`'s own docstring records the incident (`F0` §12 **D-18(c)**):

```text
  The only caller with run_selector_optimization=True was the fold loop,
  so persist=True was UNREACHABLE and nothing could ever write
  policy_params.json.  Production therefore ran {rank 0.65, return 0.35,
  prob 0.00} — never fitted, and CONTRADICTED BY ALL 8 FOLDS, which
  independently chose rank 0.50–0.60, prob 0.10–0.20.
  "The backtest was measuring a policy production could not run."
```

```text
╔══════════════════════════════════════════════════════════════════╗
║  A MODEL FIT LIVED IN AN ENTRYPOINT, SO NO SPEC COVERED IT, SO   ║
║  NO ACCEPTANCE CRITERION ASKED WHETHER IT EVER RAN — AND IT      ║
║  NEVER DID.  PRODUCTION SHIPPED HAND-TYPED COEFFICIENTS THAT     ║
║  EVERY FOLD DISAGREED WITH.                                      ║
║                                                                  ║
║  This is the argument for OR-1 in a single incident. The rule    ║
║  is not aesthetic. Work with no owner is work nobody checks.     ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.6 What D-08 must never do

| | |
|---|---|
| ✗ **Compute anything** | L0 §4.3 forbidden edge — analysis, computation or judgement |
| ✗ **Write the book** | D-11's custody (§1.5, OR-2) |
| ✗ **Call the LLM gateway** | AP-5, ST-5 — the gateway is imported only by `src/fundamental/` |
| ✗ **Emit or alter a verdict** | DC-5. A scheduler has no opinion |
| ✗ **Be imported by a domain** | OR-3 — invocation is one-way |
| ✗ **★ Invoke an experiment** | ★ **ST-2 + `L1-experiments-intent.md` XP-33.** D-10 is P7-exempt and **manually triggered only** — no cron, no daily-path step, no post-pipeline hook. ⚠ ST-2 stops an experiment leaking into production *by import*; this stops it leaking *by execution*, which is a different failure mode and was previously unaddressed |
| ✗ **★ Place an order** | L0 §1.5 / §3.1 LEVEL 3. **There is no brokerage API and no execution path.** An automated schedule that could trade is the single most dangerous thing this domain could become, and it must be structurally impossible rather than merely absent |

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **Job** | one unit of invokable work | `job_id` | declares its domain, deps, budget, retry policy. **Declared data** (T-2) |
| **Schedule** | a trigger rule | `schedule_id` | cadence + **preconditions**, not a bare timer |
| **JobRun** | one execution | `(job_id, run_id)` | status, timings, attempt number |
| **RunManifest** | one pipeline run | `run_id` | ★ git sha, config hash, data `as_of`, seed, input digests (T-3) |
| **Checkpoint** | job × run | `(run_id, job_id)` | what is durably complete |
| **RetryPolicy** | per job | `job_id` | ★ **transport-only** (§7) |
| **TimeBudget** | per job and per run | `job_id` | deadline + breach behaviour (§8) |
| **RunOutcome** | one run | `run_id` | terminal state → D-11, visible to D-09 (T-8) |

---

# 3. DEPENDENCIES

```text
ALLOWED
  D-08 ──► may INVOKE any domain's pipeline (L0 §4.3, invokes only)
  D-08 ──► D-11   run outcome, written as a record (T-8)

FORBIDDEN
  ✗ ANY domain ──► D-08          (OR-3; L0 states the D-05 case explicitly)
  ✗ D-08 ──► the LLM gateway     (AP-5, ST-5)
  ✗ D-08 ──► any execution path  (§1.6; none exists — keep it that way)
```

| ID | Rule |
|---|---|
| **OR-1** | ★ **D-08 contains no analysis, computation or judgement** (L0 §4.3). Enforced by review of every function in `src/orchestration/`: a function that returns a number derived from data is a defect |
| **OR-2** | ★ **D-08 never writes the book.** Position, lot, P&L and sleeve state are D-11's custody. D-08 may invoke a D-11 write; it may not perform one |
| **OR-3** | ★ **No domain may import `src/orchestration/`.** Invocation is one-way — the mirror of ST-2. A domain that imports the scheduler becomes schedule-aware, untestable standalone, and impossible to invoke from anywhere else. Grep-checkable in CI, like ST-2/ST-5/ST-9 |
| **OR-4** | D-08 imports no LLM gateway (AP-5, ST-5) and originates no verdict (DC-5) |

---

# 4. MODULE DECOMPOSITION

```text
src/orchestration/
├── jobs/           # job definitions — declared, inspectable, no logic
├── schedule/       # cadence + preconditions (calendar, freshness, locks)
├── state/          # run records, manifests, checkpoints
├── policy/         # ★ retry classification + time budgets
└── contracts/      # RunManifest, JobRun, RunOutcome schemas
```

---

# 5. TRIGGERING — a schedule is not a timer

| ID | Rule |
|---|---|
| **OR-5** | ★ A trigger evaluates **preconditions** before starting: (a) **trading-day / calendar check** (D-07 §6A), (b) **input freshness**, (c) **no conflicting run holds the lock**. A cadence that fires regardless of state is a timer, and a timer running an inference job on a market holiday produces a confident report about a day that did not happen |
| **OR-6** | A precondition that **cannot be evaluated** blocks the run and reports why (P5). It never defaults to "probably fine" |
| **OR-7** | The **calendar check belongs to D-07**, not here. D-08 asks; D-07 answers. `_is_market_open_et` currently lives in the inference entrypoint (§1.5) and must move |
| **OR-8** | All schedule times are **UTC** with the market timezone recorded separately (INV-007). A cadence expressed in local time silently shifts twice a year |

---

# 5A. ★ THE PRODUCTION CADENCE — QO-3 CLOSED

**Decided 2026-08-18 (Victor).**

| | Decision |
|---|---|
| **Daily** | **10:00 ET**, consuming the **day-T open price** as the decision input |
| **Retrain** | **The 1st of every month** |
| **Mechanism** | **In-process job graph, invoked by a thin external timer** (QO-5) |

This is the first stated cadence in the whole spec set, and it settles more than the schedule — it
fixes the **decision anchor**, which propagates into D-02, D-03 and D-04. Three collisions follow.

## 5A.1 ⚠ The schedule cannot be pinned in UTC

`10:00 ET` is **14:00 UTC** in summer and **15:00 UTC** in winter.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A CRON PINNED AT 14:00 UTC RUNS AT 09:00 ET ALL WINTER —        ║
║  THIRTY MINUTES BEFORE THE MARKET OPENS.                         ║
║                                                                  ║
║  The day-T open would not exist, and every run from November to  ║
║  March would either block or silently decide off a stale bar.    ║
║  This is OR-8 with a concrete failure attached.                  ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **OR-30** | ★ The cadence is stored as **`(local_time, tz)` = `(10:00, America/New_York)`** and resolved to UTC **per date**. Timestamps in the manifest and the record remain UTC (INV-007); the *schedule* is not a UTC constant |
| **OR-31** | The resolved UTC firing time for the run is written into the **RunManifest** (OR-9), so a DST-shifted run is visible rather than inferred |

## 5A.2 ⚠ "The open price" is not what the code fetches today

`main_inference.py:250` `_append_live_prices` runs whenever the market is open — including 10:00 —
and does this:

```python
price = md.get_quote(ticker).get("price")   # ← the SPOT quote at run time (10:00),
                                            #   not the 09:30 open
for c in ("open", "high", "low", "close", "adj_close"):
    new[c] = price                          # ★ all five OHLC fields set to ONE number
```

Two defects, both inherited and both fixed by building the new path correctly:

1. **It is the spot quote, not the open.** At 10:00 it is a 30-minute-old market, not the opening print.
2. ★ **It flattens the bar.** `open == high == low == close` makes the day-T **intraday range
   identically zero**. Any feature reading high−low, or open-vs-close, gets a degenerate value on
   the one bar that drives the decision — while every training bar has a real range. That is an
   **INV-4 train/inference parity break**, and it is the same class of defect the function's own
   docstring already documents for the off-hours case (`ret_1d = 0 for every name`).

| ID | Rule |
|---|---|
| **OR-32** | ★ The daily run consumes the **settled day-T opening print**, obtained as a real OHLC field from D-07 — **never a spot quote relabelled as an open**, and never a synthetic bar with collapsed OHLC |
| **OR-33** | ★ **A missing or unconfirmed day-T open blocks the run** (`BLOCKED_PRECONDITION`). It is **never** substituted with the previous close: that substitution is silent and makes the decision a day stale while looking current — the plausible-looking default **P5** forbids |
| **OR-34** | Half-days and late vendor prints are **preconditions, not exceptions**. If the open is not confirmed by the firing time, the run blocks and reports; it does not wait indefinitely inside a time budget (§8) |

## 5A.3 ★ An open-anchored decision requires an open-anchored label — INV-4

Today the label is **close-anchored**:

```python
# ohlcv/dataset/label_builder.py:86-87
df["fwd_ret_1w"] = df.groupby("ticker")["adj_close"].shift(-5)
df["fwd_ret_1w"] = (df["fwd_ret_1w"] - df["adj_close"]) / df["adj_close"]
```

The `open` field is **never read by any feature or label** in the current dataset code — it appears
only in the quality validator's non-negativity check.

```text
╔══════════════════════════════════════════════════════════════════╗
║  IF THE DECISION IS TAKEN AT THE DAY-T OPEN, THE LABEL MUST BE   ║
║  ANCHORED AT THE DAY-T OPEN.                                     ║
║                                                                  ║
║  A model trained on close(T) → close(T+h) and deployed to decide ║
║  at open(T) is anchored one session away from the return it was  ║
║  fitted to predict. The mismatch is a FULL SESSION of drift on   ║
║  every single prediction, and it is invisible in backtest        ║
║  because the backtest shares the training anchor.                ║
║                                                                  ║
║  This is not orchestration's decision to make — it is D-03's     ║
║  and D-04's. It IS orchestration's job to state that the         ║
║  cadence forces it.                                              ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **OR-35** | ★ **The decision anchor is part of the cadence and is declared in the RunManifest** (`decision_anchor: "open"`). D-02, D-03 and D-04 build features and labels against **that** anchor — **QO-7** raises the change with D-03/D-04, which own it |
| **OR-36** | The **30-minute gap** between the 09:30 open and the 10:00 run, plus the human's own latency, means **decision price ≠ fill price**. This is not look-ahead — the open is settled and in the past (INV-1 is intact) — but it is **implementation shortfall that nothing currently measures**. D-11 §7 already records that execution cost is unmeasured; this cadence gives that gap a fixed, known lower bound |
| **OR-47** | ★★ **The precondition requires the OPEN. `high`/`low`/`close` are checked only if present.** ⚠ *Added 2026-08-25 wiring the feed: **`assert_open_confirmed` demanded all four OHLC fields, and at 10:00 only one of them exists.*** The auction is final at 09:30; the bar is not final until 16:00 (**D-07 DE-47**) — so a check that insists on a settled close at decision time **blocks every single day, forever.** ★ OR-32's actual concern is narrower and survives intact: *never a spot quote relabelled as an open, and never a synthetic bar with collapsed OHLC* — so **the collapsed-bar test fires when all four ARE present and equal**, which is precisely `main_inference.py:250`'s output. ⚠ An explicit `None` for the other three is **the absence of a settled value, stated** — not a missing field |
| **OR-48** | ★ **Orchestration may INVOKE a D-11 entrypoint by dotted name; it may never `import` one.** ⚠ *Added 2026-08-26 wiring the book into the daily graph.* **AC-8.2**'s test was a bare substring check for `src.recording` over the whole shim — which also rejected the **sanctioned** seam, a `Job` whose `invokes` string names a D-11 callable that `resolve()` imports at run time. ★ That left orchestration with **no legal way to reach D-11 at all**, the opposite of what OR-2 intends: OR-2 forbids *an inference run editing the record*, not *naming the record's reader*. The check now matches `^(from\|import) src.recording` |
| **OR-49** | ★★ **The daily run's universe is the one the model was FITTED on.** ⚠ *Changed 2026-08-27 (AB-13):* the run scored **130** names — Release 5's sector-balanced list, which *nothing analytical picked* — with a model fitted on **497**. ★★ `rank_ret_5d`, `rank_vol_20d` and every `*_sector_z` are **defined by the population they are computed in**, so *a percentile among 497 is not a percentile among 130* — and **the column names match exactly, so `check_parity` cannot see it** (INV-4). ★ Aligning the two closes it **by construction** rather than by a check, and both sides now read **one** list. ⚠ **DE-36 is why this costs nothing in mandate terms**: the universe is what *normalises* the cross-section, the watchlist is what may be *bought*, and INV-6 still permits exactly one actionable pick. Measured: 130 names 57 s, 510 names **3 m 44 s** — and the ranking below #1 changed, because `COHR` and `TTD` were not in the narrow list at all |
| **OR-50** | ★★ **A failed delivery FAILS the run — and the record already exists.** RP-23 makes the failure loud; this states the consequence: the run ends `INCOMPLETE`, not `SUCCESS`. ★ **`record` depends on `render` and runs BEFORE `deliver` deliberately** (CT-11.7's job order), so the CT-11.7 artifact is on disk *before* the send is attempted — **a record written after a successful send is missing exactly when the send failed, which is when it is wanted most** |
| **OR-51** | ★★ **The manifest's provenance fields are SUPPLIED, not defaulted.** ⚠ *Measured 2026-08-27 on a real run:* `git_sha: ""`, `config_hash: ""`, `inputs: []` — every one the empty default of `trigger()`, because the entrypoint passed none of them. ★ `git_state()` **already existed and was never called from the daily path**; OR-11's *"a dirty tree is permitted and marked"* was recording neither the sha nor the dirt |
| **OR-52** | ★★ **`inputs_fresh` may not report `true` over an empty input list.** ⚠ *Measured:* the precondition returned `Precondition("inputs_fresh", True)* having examined **zero inputs** — it asserted freshness having checked nothing. ★★ **This is DE-56's shape inside the preconditions**: *absence of evidence and evidence of absence are different results, and conflating them is how a false assumption becomes a silent one* (DE-35). A run declaring no inputs reports the precondition as **not evaluated**, never as passed |
| **OR-55** | ★ **The daily run declares its stubs in the RunManifest** (OR-43 applied to the entrypoint). ⚠ *Added 2026-10-06 (Victor, L9 §10 C3):* the daily entrypoint passed `stubs=()`, so the manifest said `[]` while the thesis gate IS the placeholder — the record contradicted the card |
| **OR-56** | ★ **The daily run's `*_sector_z` inputs come from D-07's sector map (DE-77) — the same source training uses.** ⚠ *Added 2026-10-07 (`DX-160`):* `_sectors_for` read FMP `profile` from the observation ledger, which is empty on this machine, so the daily panel had no sectors; a model fitted with sectors would then be scored on null sector features — train/serve skew. One map, both paths |
| **OR-54** | ★ **One state root, one name: `PIPELINE_STATE_DIR`** (default `.state`), read identically by the daily run, the training run and the ingest run. ⚠ *Added 2026-10-06 (`DX-154`, Victor):* the daily run read `PIPELINE_STATE` while training and ingest read `PIPELINE_STATE_DIR`, so setting one put a model or a swept event store where the daily run never looks. The retired name is **refused when set**, never silently ignored (P5) |
| **OR-53** | ★ **The daily run SUPPLIES D-05's declared theme taxonomy** (`CT-5.3`, `THEMES_V1`) to the `risk` job. ⚠ *Added 2026-10-06 (Victor, L9 §6 R2):* `RunContext.taxonomy` was never set, so `_risk` fell back to the B3 refusal even for a valued book — a refusal for a reason (no taxonomy) that no longer existed. Supplied as declared data, chosen by nobody at run time (OR-1) |
| **OR-44** | ★★ **A model artifact presented to a run DECLARES the anchor it was trained on, and one that declares none BLOCKS the run.** ⚠ *Added 2026-08-25 building B6: **AC-8.32 says "a run whose model was trained on a different anchor raises" and nothing declares a training anchor.** The manifest carries `decision_anchor` (OR-35); D-03's nomination carries a hashed `model_artifact_id` (QA-121) and **no anchor**; D-04 is unbuilt. So `ORC.CADENCE.ANCHOR_MISMATCH` **could never fire** — the rule with the loudest failure mode in §5A was structurally undetectable.* ★ **Blocking on an undeclared anchor rather than assuming a match is the whole point**: *"trained on the same anchor"* and *"we do not know what it was trained on"* are opposite findings, and INV-4's drift is **a full session on every prediction and invisible in backtest**, because the backtest shares the training anchor |

## 5A.4 Monthly retrain

| ID | Rule |
|---|---|
| **OR-37** | ★ Retrain fires on the **first *trading* day of the month**, not the 1st. The 1st falls on a weekend or holiday roughly **⅓ of the time**; a calendar-blind rule would skip those months entirely or run against a closed market |
| **OR-38** | ★ **Ordering on a retrain morning: inference first, on the incumbent model; retrain after; promotion takes effect on the next trading day.** A model promoted at 10:05 and used at 10:06 has passed no gate — D-04 §7's promotion criteria need to actually run. This also makes the mutual-exclusion lock (OR-24) trivially safe, since the two jobs never contend |
| **OR-39** | A retrain that **fails or fails its gate leaves the incumbent in place**, and the failure is loud (OR-19). **Never** a fallback to an ungated model |

> ★ **A note on information gain, not an objection to the cadence.** With HorizonSet v1's **1-month
> production horizon**, the newest fully-labelled row at retrain time is already ~1 month old. Each
> monthly retrain therefore adds roughly **one new labelled month** — on a two-year panel, ~4 % new
> rows. The fitted model will usually barely move. That is fine, and drift protection plus
> operational rhythm justify the cadence on their own — but it means **the value sits in the
> promotion gate, not in the retrain**, and a retrain that changes nothing must be allowed to
> promote nothing (OR-39, D-04 §7).

## 5A.5 In-process job graph — QO-5 CLOSED

| ID | Rule |
|---|---|
| **OR-40** | ★ The job graph, manifest, retry policy, budgets and checkpoints are **in-process Python inside `src/orchestration/`**, invoked by a **thin external timer** (cron/systemd) whose entire responsibility is *"call the entrypoint at this time"* |
| **OR-41** | ★ **The external timer holds no policy.** No retry, no dependency order, no budget, no conditional logic lives in crontab. Policy in a timer is policy with no manifest, no test and no spec — the same invisibility that produced §1.5a |
| **OR-42** | The timer may fire **more often than the cadence**; preconditions (OR-5) decide whether work happens. An over-firing timer is safe by construction; a missed firing is not, so **prefer redundant firings with strict preconditions over an exactly-once timer** |
| **OR-46** | ★★ **One run per cadence WINDOW is enforced by an idempotency key, not by the lock.** ⚠ *Added 2026-08-25 building B6: **AC-8.37 cites OR-42 and OR-24, and OR-24's lock cannot deliver it.** A lock is **mutual exclusion in time** — it stops two runs overlapping. Two firings twenty minutes apart do not overlap: the first completes, **releases the lock**, and the second finds it free, passes every precondition and runs the whole cadence again.* ★ So the window is keyed: `(job_graph_id, cadence_date, local_time)` resolves to one **`cadence_key`**, a completed run claims it, and a second firing against a claimed key is `BLOCKED_PRECONDITION` — *not* a failure, because **OR-42 deliberately prefers redundant firings**. ⚠ **A FAILED run does not claim the key**: re-firing after a failure must be able to retry the cadence, or OR-42's redundancy buys nothing exactly when it is needed |

---

# 6. ★ RUN IDENTITY AND REPRODUCIBILITY — the largest gap

**Today the entire run identity is a wall-clock string:**

```python
# main_pipeline.py:605
run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
```

No manifest, no code version, no config hash, no data `as_of`, no run-level seed. Model seeds exist
(`random_state: 42`, three places in `settings.yaml`), but **nothing records what the run as a whole
was made of.**

| ID | Rule |
|---|---|
| **OR-9** | ★ **Every run emits a RunManifest before it does any work**, containing: `run_id`, **git sha (and dirty flag)**, config hash, data `as_of`, **run seed**, and a digest of every input artifact |
| **OR-10** | ★ **D-08 is the only layer that can enforce constitution INV-2 (determinism).** A domain can be deterministic in isolation and the pipeline still irreproducible, because reproducibility is a property of *the whole invocation* — code + config + data + seed. **Determinism has no owner if D-08 does not own the manifest** |
| **OR-11** | A run against a **dirty working tree** is permitted but **marked dirty in the manifest and in everything downstream**. Silently recording a clean sha for a modified tree is worse than not recording one |
| **OR-12** | `run_id` is **not** a wall-clock timestamp alone. Two runs launched in the same second must be distinguishable, and a run id must survive a clock change |
| **OR-43** | ★★ **A stubbed domain is DECLARED IN THE MANIFEST, and the declaration is not optional.** ⚠ *Added 2026-08-23.* `L3` **BS-27** requires that the B3 constant-`PASS` gate *"is written into the RunManifest rather than being silently true"* — and **CT-8.1 declared no field for it**, so the rule was unimplementable against its own contract. ★ **The reason it is a manifest field and not a code comment: a stub that is indistinguishable from a real implementation in the RECORD is how a placeholder survives into production.** `stubs: []` is the production value and must be written explicitly — an absent key is not an empty list |
| **OR-13** | The manifest is **append-only and immutable once written** (INV-005, INV-006). A rerun creates a new manifest; it never edits the old one |

---

# 7. ★ FAILURE AND RETRY — where P5 and "retry" have to be reconciled

P5 says **fail loud, never silent.** Retry looks like the opposite. The line that reconciles them:

```text
╔══════════════════════════════════════════════════════════════════╗
║  RETRY TRANSPORT.  NEVER RETRY SEMANTICS.                        ║
║                                                                  ║
║  RETRYABLE — the request did not get a real answer:              ║
║      timeout · connection reset · HTTP 429 · 5xx · rate limit     ║
║                                                                  ║
║  NOT RETRYABLE — the system got an answer it did not like:       ║
║      data-quality failure · schema violation · validation breach ║
║      · a missing ticker · an LLM returning unusable output       ║
║      · HTTP 402 (FMP entitlement — L1-data-engine §5A: it means  ║
║        "not on your plan", and retrying it forever is a bill,    ║
║        not a fix)                                                ║
║                                                                  ║
║  Retrying a semantic failure LAUNDERS A HARD FAILURE INTO A SOFT ║
║  ONE.  It converts "this input is bad" into "this eventually     ║
║  succeeded", which is exactly the silent degradation P5 exists   ║
║  to prevent — and how a discipline card was once built from a    ║
║  failed LLM narrative and emailed as a real recommendation.      ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **OR-14** | ★ **Retry classification is explicit per error, never a blanket `except: retry`.** An unclassified error is **not retryable** — the safe default is to stop |
| **OR-14a** | ★ **Declared exception: the LLM gateway retries transport beneath the domain layer** ([`L2-shared-infrastructure.md`](L2-shared-infrastructure.md) **GW-15**). D-08 owns retry for *jobs*; the gateway owns it for *calls*, because a 429 inside a D-01 call never reaches orchestration. ⚠ **Both obey the same classification (EH-15) and the gateway's attempt count reaches the RunManifest** (GW-16) — an exception that hid its retries would make a flaky run look clean |
| **OR-15** | Retries are **bounded, backed off, and recorded**. The attempt count appears in the JobRun and in anything downstream |
| **OR-16** | ★ **Partial success is failure.** A run where some jobs succeeded and some failed is `INCOMPLETE`, and **INCOMPLETE never produces a human-facing artifact** (DC-3, P5). The two real incidents in this repo both came from a downstream consumer treating a degraded upstream as usable |
| **OR-17** | **INV-032** — a failure must not corrupt data. Writes are atomic or transactional: a killed run leaves either the old state or the new one, never a half-written panel |
| **OR-18** | **INV-033 / INV-034** — a single external API failure, or an LLM-provider failure, **degrades scope, not the system**. The non-LLM path continues and **the absence is reported**, not filled |
| **OR-19** | ★ **A failed run is loud.** Silence is not an acceptable failure mode: if the nightly run dies, that fact reaches the human by the same channel the success would have (T-8). **A pipeline that fails quietly is indistinguishable from one that was never scheduled** |
| **OR-45** | ★★ **A failure notification is NOT a human-facing artifact, and OR-16 does not suppress it.** ⚠ *Added 2026-08-25 building B6: **OR-16 says `INCOMPLETE` never produces a human-facing artifact; OR-19 says a failed run must reach the human by the same channel a success would.** Read together and unqualified, the first forbids the second — and an implementer resolving it that way makes a failed run **silent**, which is precisely what OR-19 exists to prevent.* ★ **The line is what the message CLAIMS**: a report asserts *"here is the analysis"* and must never be emitted from a partial run; a failure notice asserts *"the run did not complete, here is why"* and **carries no analytical content at all**. ⚠ A failure notice that quotes a partial result has become a report and is forbidden |

---

# 8. ★ TIME BUDGETS — stated in L0, implemented nowhere

L0 §4.2 says D-08 *"enforces time budgets."* **Grep across all four entrypoints returns zero matches
for `retry`, `backoff`, `timeout`, `deadline` or `time_budget`.** The only hit is a comment in
`data_ingest_scheduler.py` describing backoff as a future hook.

| ID | Rule |
|---|---|
| **OR-20** | Every job declares a **time budget**; the run declares an overall one |
| **OR-21** | ★ **Budget breach fails the run. It never truncates the work and emits the remainder.** "Emit what we have" is the plausible-looking default P5 forbids — a half-computed slate is more dangerous than no slate, because it looks complete |
| **OR-22** | A breach records **which job**, **its budget**, and **its elapsed time** — enough to fix it without rerunning |
| **OR-23** | Budgets are **config, not constants**, and their values are in the RunManifest (OR-9) |

---

# 9. CONCURRENCY, IDEMPOTENCE AND STATE

| ID | Rule |
|---|---|
| **OR-24** | ★ **Mutual exclusion on written state.** Two runs never mutate the same artifact concurrently. The lock is explicit and its holder is inspectable — a stuck lock must be diagnosable, not mysterious |
| **OR-25** | Re-running a completed job is **idempotent**: same manifest inputs ⇒ same outputs, no duplicated records (pairs with D-11's idempotent ingestion) |
| **OR-26** | ★ A **resume** skips only work with a **durable checkpoint proving completion**. It never skips a step that failed, and never skips a step whose inputs changed |
| **OR-27** | Run state is **append-only** (INV-006). A retry appends an attempt; it does not overwrite the first one |

---

# 10. CONTRACTS

> **ID-collision notice.** `AC-8.k` / `CT-8.k` key `n` on **D-08**. **`F8` is reserved** in
> `vision.md` §4 (*performance attribution & review*) — latent, like D-05/F5 and D-07/F7
> (L0 §16.4). Qualify the tier when citing.

## CT-8.1 — RunManifest (JSON, written **before** work begins, immutable)

```json
{
  "run_id": "2026-08-18T09:30:00Z-inference-7f3a91",
  "job_graph_id": "daily_inference@v3",
  "code": {"git_sha": "f9e7886", "dirty": false},
  "config_hash": "sha256:1c9e…",
  "data_as_of": "2026-08-15",
  "decision_anchor": "open",              // ★ OR-35. MT-42 and DN-23 assert against this field
  "seed": 42,
  "inputs": [{"artifact": "panel/features.parquet", "digest": "sha256:aa41…"}],
  "budgets": {"run_seconds": 1800, "per_job": {"features": 300}},
  "preconditions": {"trading_day": true, "inputs_fresh": true, "lock_acquired": true,
                    "open_confirmed": true, "cadence_unclaimed": true},
  "cadence_key": "daily_inference@v3:2026-08-18:10:00",   // ★ OR-46 — one run per window
  "model": {"artifact_id": "sha256:9c1f…", "trained_anchor": "open"},  // ★ OR-44
  "stubs": [                              // ★ OR-43. Empty in production; NOT optional
    {"domain": "D-01", "job": "thesis_gate", "behaviour": "constant PASS",
     "replaced_at": "B4.4", "rule": "L3 BS-27"}
  ]
}
```

## CT-8.2 — RunOutcome (JSON, append-only → D-11)

`(run_id, status ∈ {SUCCESS, FAILED, INCOMPLETE, BUDGET_EXCEEDED, BLOCKED_PRECONDITION},
jobs[{job_id, status, attempts, elapsed_s, error_code}], started_at, ended_at, artifacts[])`

★ **`INCOMPLETE` is a first-class terminal status, not a variant of success** (OR-16), and no
human-facing artifact may be produced under it.

---

# 11. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `plan(job_graph_id)` | `JobGraph` | ★ inspectable **without executing** (T-2) |
| `trigger(job_graph_id, as_of)` | `RunManifest \| BlockedPrecondition` | evaluates OR-5 first |
| `run(run_id)` | `RunOutcome` | invokes only |
| `resume(run_id)` | `RunOutcome` | honours OR-26 |
| `status(run_id)` | `JobRun[]` | live state |
| `history(window)` | `RunOutcome[]` | for D-09 and D-11 |

★ **No method on this surface returns an analytical value.** If one ever does, OR-1 has been broken.

---

# 12. BUSINESS RULES

| ID | Rule |
|---|---|
| **OR-1…OR-4** | Boundary — invokes, never computes; never writes the book; one-way import — §3 |
| **OR-5…OR-8** | Triggering and preconditions — §5 |
| **OR-9…OR-13** | Run identity, manifest, determinism — §6 |
| **OR-14…OR-19** | Failure and retry — §7 |
| **OR-20…OR-23** | Time budgets — §8 |
| **OR-24…OR-27** | Concurrency, idempotence, state — §9 |
| **OR-30…OR-42** | ★ **The production cadence** — DST-safe schedule, the open as decision input, open-anchored labels, monthly retrain ordering, in-process graph — §5A |
| **OR-28** | ★ D-08 has **no agent and no LLM** (L0 §5.1). Scheduling is deterministic work |
| **OR-29** | ★ **D-08 exposes no execution or order-placement capability**, now or later (§1.6, L0 §1.5) |

---

# 13. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `ORC.PRECOND.NOT_TRADING_DAY` | INFO | run does not start; recorded as `BLOCKED_PRECONDITION`, **not** as a failure |
| `ORC.PRECOND.STALE_INPUT` | ERROR | inputs older than the freshness rule (OR-5) |
| `ORC.PRECOND.UNEVALUABLE` | ERROR | a precondition could not be checked — blocks (OR-6) |
| `ORC.LOCK.HELD` | ERROR | a conflicting run holds the lock; holder is named (OR-24) |
| `ORC.MANIFEST.MISSING` | ERROR | work attempted before a manifest was written (OR-9) |
| `ORC.MANIFEST.DIRTY_TREE` | WARNING | run proceeds, **marked dirty everywhere downstream** (OR-11) |
| `ORC.RETRY.UNCLASSIFIED` | ERROR | an error with no retry classification — **not retried** (OR-14) |
| `ORC.RETRY.SEMANTIC_ATTEMPTED` | ERROR | ★ retry attempted on a non-transport failure (OR-14) |
| `ORC.RUN.INCOMPLETE` | ERROR | some jobs failed — **no human-facing artifact** (OR-16) |
| `ORC.BUDGET.EXCEEDED` | ERROR | deadline breached; job, budget and elapsed recorded (OR-21) |
| `ORC.PRECOND.OPEN_UNCONFIRMED` | ERROR | ★ day-T opening print missing or unsettled — **blocks; never falls back to the previous close** (OR-33) |
| `ORC.CADENCE.UTC_PINNED` | ERROR | ★ a schedule stored as a UTC constant instead of `(local_time, tz)` (OR-30) |
| `ORC.CADENCE.ANCHOR_MISMATCH` | ERROR | ★ manifest `decision_anchor` disagrees with the anchor the model was trained on (OR-35, INV-4) |
| `ORC.CADENCE.ANCHOR_UNDECLARED` | ERROR | ★★ a model artifact that declares no training anchor — **blocks; *matching* and *unknown* are opposite findings** (OR-44) |
| `ORC.PRECOND.CADENCE_CLAIMED` | INFO | ★ a completed run already claimed this cadence window; recorded as `BLOCKED_PRECONDITION`, **not** a failure (OR-46, OR-42) |
| `ORC.RETRAIN.NON_TRADING_DAY` | ERROR | retrain scheduled on a date the calendar says is closed (OR-37) |
| `ORC.RETRAIN.UNGATED_PROMOTION` | ERROR | ★ a model promoted and used inside the same run (OR-38) |
| `ORC.TIMER.POLICY_PRESENT` | ERROR | ★ retry, ordering or budget logic found in the external timer (OR-41) |
| `ORC.BOUNDARY.COMPUTATION` | ERROR | ★ orchestration code returned a derived value (OR-1) |
| `ORC.BOUNDARY.BOOK_WRITE` | ERROR | ★ orchestration attempted to write position/P&L state (OR-2) |
| `ORC.BOUNDARY.IMPORTED` | ERROR | a domain imported `src/orchestration/` (OR-3) |

---

# 14. ACCEPTANCE CRITERIA

```text
BOUNDARY  (§1.3, §3)  ★ the ones that matter most
□ AC-8.1   No function in src/orchestration/ returns a value derived from market
           or fundamental data (OR-1)
□ AC-8.2   src/orchestration/ performs no write to position, lot, P&L or sleeve
           state — it may only invoke D-11 (OR-2)
□ AC-8.3   No domain imports src/orchestration/ — grep-checkable in CI (OR-3)
□ AC-8.4   src/orchestration/ imports no LLM gateway (OR-4, ST-5)
□ AC-8.5   The public API exposes no order-placement capability (OR-29)

TRIGGERING  (§5)
□ AC-8.6   A run on a non-trading day is BLOCKED_PRECONDITION, not a failure
□ AC-8.7   A stale input blocks the run (OR-5)
□ AC-8.8   An unevaluable precondition blocks and states why (OR-6)
□ AC-8.9   Schedule times are UTC with the market timezone recorded (OR-8)

IDENTITY  (§6)
□ AC-8.10  A manifest is written BEFORE any job runs; work without one raises
□ AC-8.11  The manifest carries git sha, dirty flag, config hash, data as_of,
           seed, and input digests (OR-9)
□ AC-8.12  A dirty tree is marked dirty in the manifest and downstream (OR-11)
□ AC-8.13  Two runs started in the same second have distinct run_ids (OR-12)
□ AC-8.14  A written manifest cannot be mutated (OR-13, INV-005/006)
□ AC-8.14a ★ Every stubbed domain appears in manifest.stubs with its behaviour
           and the milestone that replaces it; the key is present even when
           empty (OR-43, L3 BS-27)
□ AC-8.15  ★ Two runs with identical manifests produce identical outputs
           (constitution INV-2, enforced here — OR-10)

FAILURE  (§7)
□ AC-8.16  A transport error (timeout/429/5xx) is retried, bounded and recorded
□ AC-8.17  ★ A semantic error (schema, validation, data-quality, HTTP 402) is
           NEVER retried (OR-14)
□ AC-8.18  An unclassified error is not retried (OR-14)
□ AC-8.19  ★ A run with any failed job is INCOMPLETE and produces no
           human-facing artifact (OR-16, DC-3)
□ AC-8.20  A killed run leaves old or new state, never half-written (INV-032)
□ AC-8.21  An external-API or LLM-provider failure degrades scope and REPORTS
           the absence (INV-033/034, OR-18)
□ AC-8.22  ★ A failed run reaches the human by the same channel a success would
           (OR-19)
□ AC-8.22a ★ The failure notice carries NO analytical content; OR-16 suppresses
           reports, never the notification that the run failed (OR-45)

CADENCE  (§5A)  ★ QO-3 / QO-5
□ AC-8.29  The daily schedule resolves 10:00 America/New_York to the correct UTC
           instant on BOTH sides of a DST boundary (OR-30)
□ AC-8.30  ★ The decision input is the settled day-T OPENING PRINT — not a spot
           quote, and not a bar whose OHLC fields are all equal (OR-32)
□ AC-8.30a ★ The precondition needs only the OPEN; high/low/close are absent at
           10:00 by construction, and demanding them blocks every day (OR-47, DE-47)
□ AC-8.31  ★ A missing or unconfirmed day-T open BLOCKS the run and is never
           substituted with the previous close (OR-33)
□ AC-8.32  ★ The manifest records decision_anchor, and a run whose model was
           trained on a different anchor raises (OR-35, INV-4)
□ AC-8.33  Retrain fires on the first TRADING day of the month (OR-37)
□ AC-8.34  ★ On a retrain morning, inference completes on the incumbent model
           before retrain starts; promotion takes effect the next trading day
           (OR-38)
□ AC-8.35  A failed or gate-failing retrain leaves the incumbent in place, loudly
           (OR-39)
□ AC-8.36  ★ The external timer contains no retry, ordering or budget policy
           (OR-41)
□ AC-8.37  Two timer firings inside one cadence window produce one run, not two
           (OR-42, OR-46) — by an idempotency KEY, not by the lock
□ AC-8.37a ★ A FAILED run does not claim the window; a re-firing may retry it
           (OR-46, OR-42)
□ AC-8.32a ★ A model artifact declaring no training anchor BLOCKS the run —
           matching and unknown are opposite findings (OR-44, DE-35)
□ AC-8.38  ★★ A failed delivery fails the run, and the CT-11.7 record is on
           disk regardless because record precedes deliver (OR-50, RP-23)
□ AC-8.39  ★ The manifest carries a real git_sha, config_hash and inputs — no
           field is the empty default (OR-51, OR-11)
□ AC-8.40  ★★ inputs_fresh over an empty list reports NOT EVALUATED, never
           true (OR-52, DE-35)
□ AC-8.41  ★ The daily run's context carries D-05's declared taxonomy (THEMES_V1);
           the risk job never refuses for want of one (OR-53, CT-5.3)
□ AC-8.42  ★ Every state-root read in src/ uses PIPELINE_STATE_DIR; the retired
           PIPELINE_STATE, if set, raises rather than being ignored (OR-54, DX-154)
□ AC-8.43  ★ The daily run's manifest declares the placeholder thesis gate in
           stubs[] (OR-55, OR-43)
□ AC-8.44  ★ The daily run's sectors come from D-07's sector map — the same as
           training's (OR-56, DE-77)

BUDGET & STATE  (§8, §9)
□ AC-8.23  Budget breach fails the run; it never truncates and emits (OR-21)
□ AC-8.24  A breach names the job, its budget and its elapsed time (OR-22)
□ AC-8.25  Concurrent runs cannot mutate the same artifact; the lock holder is
           inspectable (OR-24)
□ AC-8.26  Re-running a completed job duplicates no records (OR-25)
□ AC-8.27  Resume skips only checkpointed-complete work, never a failed step
           and never a step whose inputs changed (OR-26)
□ AC-8.28  A retry appends an attempt; it never overwrites the first (OR-27)
```

---

# 15. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QO-1** | ★ **What is the migration order for the ten misplaced functions in §1.5?** | They cannot move at once. `_load_positions`/`_save_positions`/`_update_sleeves` → D-11 is the **highest-risk and highest-value** move (it is a prediction editing the record); `_is_market_open_et` → D-07 is the cheapest. **The book-write move should go first** |
| **QO-2** | Where does **`_make_wf_folds`** land — D-04 or D-03? | It is CV methodology. D-04 owns training; D-03 owns validation design (QA-*). It has been an **orchestrator default (`fold_years=3, val_years=1`) that nothing reviews**, which is the actual problem regardless of destination |
| **QO-3** | ~~What is the schedule?~~ | ✅ **CLOSED 2026-08-18 (Victor).** Daily **10:00 ET** off the **day-T open**; retrain the **1st of every month**. See **§5A** — and note the decision closed one question and opened three (§5A.1–5A.3) |
| **QO-4** | Does **D-08 own the run cadence for retraining**, or does D-04? | D-04 §7 owns promotion; `F10` (*model governance — retrain cadence*) is **reserved** in `vision.md`. Overlaps **QQ-15** (INV-6 cadence, constitution-level) |
| **QO-5** | ~~In-process or external orchestration?~~ | ✅ **CLOSED 2026-08-18 (Victor).** **In-process job graph behind a thin external timer** — OR-40…OR-42 |
| **QO-6** | Should a `BLOCKED_PRECONDITION` run **notify**? | It is not a failure, but a week of silent holiday-blocks is indistinguishable from a broken scheduler (OR-19's concern in reverse). Probably: notify on **state change**, not on every occurrence |
| **QO-7** | ~~Does the label anchor move from close to open?~~ | ✅ **CLOSED 2026-08-18 (Victor). It moves.** Labels become `open(T+h)/open(T) − 1` — **D-03 §5.9** (QA-71…QA-75), **D-04 §6.3/§8.1** (MT-41…MT-47), **D-02 §5Z** (FE-28…FE-30). The riskiest part is that the `open` column **has never been split-adjusted in anger**; the costliest is that **every historical IC, fold and tuning number becomes non-comparable** |
| **QO-8** | Does a **10:00 run** leave enough of the session to act? | The run consumes the 09:30 open, finishes some minutes later, and Victor acts after that. **OR-36** makes the gap explicit but nothing measures it. Ties **QQ-20** and D-11 §7 (execution cost unmeasured) |

---

# 16. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-08, **§4.3** (invokes only; Risk ✗→ Orchestration), §3.1 LEVEL 0, **§1.5** (no execution path), INV-032/033/034, INV-005/006/007 | the boundary rule, the authority level, the failure invariants |
| `L4-coding-standards.md` §1.1 `src/orchestration/`, **ST-2, ST-3, ST-5, ST-9**, migration table (`data_ingest_scheduler.py` → REBUILD) | the target tree; the one-way-import pattern OR-3 mirrors |
| `sdd/specs/constitution.md` **P5** (fail loud), **INV-2** (determinism), **DC-3** | §7's retry line and §6's manifest exist to make these enforceable |
| `L1-data-engine.md` **§6A** calendar check, §5A (HTTP 402's three meanings) | OR-5's precondition; OR-14's canonical non-retryable error |
| `L1-recording.md` RC-* (idempotent ingestion, append-only journal) | OR-2's custody boundary; OR-25's idempotence |
| `L1-quantitative-analysis.md` HorizonSet v1 (§5), **QQ-20** | the 1m production horizon §5A.4's information-gain note reasons from; the arrival-price gap OR-36 names |
| `L1-model-training.md` **§7** promotion, MT-* | where `_run_production_coefficient_fit` and `_make_wf_folds` belong (QO-2) |
| `L1-reporting.md` **DC-3**, freshness per component | why `INCOMPLETE` must never render (OR-16) |
| `sdd/specs/F0_code_map/spec.md` §12 **D-18(c)** | the documented incident in §1.5a *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
