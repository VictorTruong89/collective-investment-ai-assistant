# L4: Coding Standards — §1 Structure · §5 Errors · §10 Imports · §14 Constants · §17 Pandas · §18 Clean Architecture

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> Nothing here governs code until this file is promoted into `sdd/specs/` and its paths are
> registered in `sdd/specs/ownership.yaml`. Until then `pipeline/**` remains the live system and
> its existing specs (F0–F9) remain the governing ones.
>
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** — domains `D-00`…`D-11`
> (§16.2), seats `SEAT-2`…`SEAT-5` (§1.5), tier & promotion rules `G-1`…`G-7` (§17).
> **Format reference:** `samples/L4-coding-standards.md` (structure and tone only — its technology
> choices are superseded, see §1.8).

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.18.0 | 2026-08-23 | Victor | ⚠ **B2 readiness cascade — two stale spots in the D-07 layout, plus one rule conflict.** ★ **EH-14 vs D-07 DE-15/AC-7.32**: one forbids a domain to retry, the other requires D-07's client to retry a 402 before reporting it. Carve-out recorded on EH-14, resolved in **DE-46**. §1.1's tree predates `L1-data-engine.md` §5A.4 and §6A and omitted **`observation/`** (the Class-B snapshot ledger, CT-7.6) and **`calendar/`** (the pre-run corporate-action gate) — both are B2 deliverables, and neither had a home in the layout the parallel build executes against. ★ **§1.3 called the same directory `data_engine/sources/` that §1.1 and §1.5 call `data_engine/src/`** — one directory, two names, in one document. `src/` binds (Victor, 2026-08-23); §1.3 corrected. |
| 0.17.0 | 2026-08-18 | Victor | **Q-5 closed** — the combine point is `D-12`, and the ~420 LOC it blocked now has a destination: `signal_engine.py` → `src/quant/`, `gate.py` → `src/decision/`. |
| 0.16.0 | 2026-08-18 | Victor | **Q-3 closed** by `L3-build-sequence.md` §7 — a non-question, since **ST-2 takes D-10 off the critical path** rather than placing it on either end of it. Parent → L0 v0.20.0. |
| 0.15.0 | 2026-08-18 | Victor | ⚠ **DOC-1 was violated by the document that defines it.** §10.1's grep table bolded its IDs, so five `ST-*` rules parsed as double definitions — and **`OR-3` appeared bold here while being owned by `L1-orchestration.md`**, reading as though L4 defined another spec's rule. De-bolded as index rows. |
| 0.14.0 | 2026-08-18 | Victor | **DOC-1** — a rule is defined once in a **bold** ID cell; roll-up and grep tables are **index rows and are not bold**. Makes D-03 QA-116's one-binding-definition rule mechanically checkable instead of a reading exercise. Parent claim corrected to L0 v0.18.0. |
| 0.13.0 | 2026-08-18 | Victor | ⚠ **Audit finding D: `CA-1…CA-9` were referenced by no L1 spec.** New **CA-0** binds every L1 module decomposition to §18 **without restating it** — an L1 names its modules, §18 governs their internal layering, and a tree drawn before §18 existed is not exempt. Stated once so eleven copies cannot drift. |
| 0.12.0 | 2026-08-18 | Victor | §1.5 migration table records that **`backtester.py`'s hard-coded `initial_capital` is deliberately left unpatched** — the capital base is read from D-11 in the rebuilt `quant/backtest/` only (D-03 QA-114/115). |
| 0.11.0 | 2026-08-18 | Victor | **§18 Clean Architecture added** (CA-1…CA-9), implementing L0 §4.4. Circles are drawn **per module**, not above the tree. §18.4 states the position that matters: **the panel IS the domain model**, so what crosses a boundary is a **contract-bound DataFrame**, not a DTO. §18.6's honest gap: CA-1/CA-2 have **no automated check**, unlike §10.1's horizontal edges — and by IM-3's own standard that makes them comments. |
| 0.10.0 | 2026-08-18 | Victor | **`src/decision/` (D-12) added** to §1.1 and §1.2. New **ST-10** — neither analyst seat may import D-12; the composition edge is one-way, and it joins §10.1's checked edges. |
| 0.9.0 | 2026-08-18 | Victor | **Four sections added — §5 Errors, §10 Imports, §14 Constants, §17 Pandas** (EH-1…15, IM-1…9, CN-1…11, PD-1…20). §5 **replaces** the sample's `Result[T,E]` with **raise** per §1.8/P5, and adds `Unmeasured` as a declared type. §14 and §17 record **live violations**: float FX arithmetic in `book_state.py:116` / `reconcile.py:140` (**INV-001**), and `fillna(0.0)` on a z-score in `signal_engine.py:213`. |
| 0.8.0 | 2026-08-18 | Victor | §1.2 records that **D-10 is deliberately unspecified** (L0 §4.2) and that **ST-2 is consequently load-bearing**, not stylistic. |
| 0.7.0 | 2026-08-18 | Victor | [`L1-portfolio-strategy.md`](L1-portfolio-strategy.md) added — `src/portfolio/` gains `pyramid/` (M-3's scale-in flag **and** its hold alternative). ⚠ **`position_size_pct` must be deleted from `report_writer.py`'s LLM schema and prompt** (PS-1, P2/AP-5) — an LLM is currently doing risk arithmetic under a contract that says it is computed. |
| 0.6.0 | 2026-08-18 | Victor | [`L1-reporting.md`](L1-reporting.md) added — `src/reporting/render/` gains **`classes.py`** (reliability-class tagging) and **`lint.py`** (forecast-voice, length, uncited claims). **D-09 has an agent but must never import the LLM gateway** — it renders text D-01 authored (ST-5), and that is grep-checkable. |
| 0.5.0 | 2026-08-18 | Victor | [`L1-recording.md`](L1-recording.md) added — `src/recording/` gains `ingest/`, `orders/`, `instruments/`, `capital/` and `arrival/`. ⚠ **The broker is BMO InvestorLine, not CIBC** — `pipeline/portfolio/ingest.py`'s docstring and error message both misname it, so that file is **REVIEW, not VERBATIM**. |
| 0.4.4 | 2026-08-16 | Victor | [`L1-model-training.md`](L1-model-training.md) added — `src/models/` gains `artifact/` and `governance/{parity,promotion,drift,registry}`. Its **MT-5 deletes the inference-side feature builder**, so `main_inference._build_inference_features` is **not migrated**; and `ohlcv/models/model_bundle.py` is **REVIEW, not VERBATIM** (`_select_features` filters where it must check). |
| 0.4.3 | 2026-08-16 | Victor | [`L1-quantitative-analysis.md`](L1-quantitative-analysis.md) added — `src/quant/` gains `horizons/`, `gates/` and **`methods/`** (the method register). Its **§8 mathematical-provenance requirement binds D-02…D-06 and belongs in §§2–13 of this document** — recorded as its QQ-7. |
| 0.4.2 | 2026-08-16 | Victor | [`L1-fundamental-analysis.md`](L1-fundamental-analysis.md) added — `src/fundamental/` gains `bundle/`, `claims/` and `monitor/`, and its **QR-5** flags that anchor-stripping (RA-14) requires splitting `prompt_stock_analysis.md`, whose sections INV-9's alignment manifest tracks individually. |
| 0.4.1 | 2026-08-16 | Victor | **Q-10 closed** by [`L1-feature-engineering.md`](L1-feature-engineering.md) §6 — D-01 gets per-ticker results with the arithmetic trail, D-03/D-04 get a contract-bound panel plus labels. That spec also records a **live INV-014 breach** in `moat_scorer.py` (§8.3), which changes where that file lands. |
| 0.4.0 | 2026-08-15 | Victor | **D-09 split (L0 v0.10.0).** `src/reporting/` narrows to D-09 Reporting (render · deliver · online_api · contracts); new **`src/recording/` = D-11** (book · reconcile · trades · journal · attribution · contracts). §1.1 tree, §1.2 map and the §1.5 migration table updated; `pipeline/portfolio/**` and `discipline/journal.py` re-routed to D-11. New **ST-9** — Recording must not import Reporting. |
| 0.3.1 | 2026-08-15 | Victor | **L0 v0.9.0 caught up with this file.** D-02 = Feature Engineering / SEAT-5 and D-10 = Experiments / SEAT-3 are now declared in L0 §16.2, so §1.2 is no longer ahead of its parent. **Q-8 closed** — L0 INV-014 reworded. No layout or migration-table change. |
| 0.3.0 | 2026-08-14 | Victor | **D-02 assigned to SEAT-5** (closes Q-7). This also resolves the INV-014 collision structurally: a neutral third-party computation layer means neither analyst seat consumes the other's output. Q-8 downgraded from blocker to wording fix; per-consumer output contracts deferred as Q-10. |
| 0.2.0 | 2026-08-14 | Victor | Layout refined: `data_engine/src/{edgar,fmp}`; `research/`→**`fundamental/`** with new **`scorecard/`**; `valuation/`→**`feature_engineer/`**, widened to own *all* deterministic computation (valuation + fundamental + technical + ML features + labels) feeding **both** analyst seats; new **`src/experiments/` (D-10)** replacing `research_lab/`; `reporting/api/`→`reporting/online_api/`. Cascaded through §1.2, §1.5, ST-2, ST-5. Two consequences raised as **Q-7** (D-02's owning seat) and **Q-8** (INV-014 wording). |
| 0.1.0 | 2026-08-14 | Victor | §1 only — target layout, domain→path map, and the full current→target migration table. §§2–20 (naming, typing, errors, logging, conventions) not yet drafted. |

## Scope — and why the section numbers have gaps

**Five sections are drafted; the numbering follows the full outline, so the gaps are deliberate.**
§§2–4, 6–9, 11–13, 15–16, 18–25 (naming, types, function standards, service/adapter patterns, DI,
async, logging, config, repository, events, comments, git, tooling) are **not written and may never
need to be** — most of that is generic style `ruff` and `black` settle without a document.

The five that are written are the ones that **make an invariant mechanical instead of aspirational**:

| § | What it holds up |
|---|---|
| **§1 Structure** | where every file lives — a file with no home means L0 §4's domain model is wrong |
| **§5 Errors** | ★ **P5 fail-loud.** Decides whether a degraded input can return a plausible number at all |
| **§10 Imports** | ★ ST-1/2/5/9 and OR-3 — the only place four structural invariants are actually enforced |
| **§14 Constants** | ★ INV-001 money, and the fact/choice/math split that decides what a manifest records |
| **§17 Pandas** | ★ where nearly every correctness defect in this repo actually lives |
| **§18 Clean Arch** | ★ the **vertical** dependency rule — policy never imports mechanism (L0 §4.4) |

§1 answers one question: **where does every file live, and how does today's code get there.**

It is drafted first because it is the artifact the parallel build executes against, and because a
file with no obvious home is evidence that the domain model in L0 §4 is wrong — better discovered
now, on paper, than after three weeks of moves.

**This is a parallel build.** `src/` is created alongside `pipeline/`; the legacy tree keeps
running and its tests keep passing until each domain is cut over. See §1.7 for the rules that keep
that from becoming a permanent fork.

---

# 1. PROJECT STRUCTURE

## 1.1 Target repository layout

```text
ai-investment-pipeline/
├── src/                         # the new tree — one directory per domain
│   ├── shared/                  # D-00  cross-cutting, owned by no seat
│   │   ├── money.py             #       Money(amount_minor: int, currency: str) — INV-001
│   │   ├── errors.py            #       error hierarchy
│   │   ├── ids.py               #       ticker / period / run identifiers
│   │   ├── logging.py
│   │   └── llm/                 #       LLM gateway — the only place a model is called
│   │
│   ├── data_engine/             # D-07  SEAT-5   acquire · validate · store · serve
│   │   ├── src/edgar/           #       EDGAR client, companyfacts, XBRL parsing
│   │   ├── src/fmp/             #       FMP client, fundamentals, prices, news
│   │   ├── pit/                 #       point-in-time enforcement + restatement tracking
│   │   ├── observation/         #       ★ Class-B snapshot ledger — CT-7.6, L1-DE §5A.4
│   │   ├── calendar/            #       ★ pre-run corporate-action gate — L1-DE §6A
│   │   ├── validation/          #       quality rules, ACCEPT / FLAG / REJECT
│   │   ├── contracts/           #       parquet & JSON schemas (authoritative shapes)
│   │   ├── store/               #       read/write parquet + JSON, atomic writes
│   │   └── universe/            #       ticker universe & watchlist membership
│   │
│   ├── feature_engineer/        # D-02  the deterministic computation layer
│   │   │                        #       consumes D-07 · feeds BOTH D-01 and D-03/D-04
│   │   ├── valuation/           #       DCF, fair value, margin of safety
│   │   ├── quality/             #       moat, quality scoring
│   │   ├── fundamental/         #       ratios, margins, growth, accruals, Piotroski
│   │   ├── technical/           #       indicators, derived price series
│   │   ├── ml_features/         #       the feature contract — train AND inference
│   │   ├── labels/              #       label construction
│   │   └── contracts/           #       feature-set schemas + versioning
│   │
│   ├── fundamental/             # D-01  SEAT-2   qualitative, LLM-bearing
│   │   ├── bundle/              #       ★ pinned, hashed evidence set — L1-RA §5
│   │   ├── scorecard/           #       ★ scorecard templates — bounded, rubric-driven
│   │   │                        #         LLM scoring for deterministic, explainable output
│   │   ├── prompts/             #       system prompts, versioned; alignment-checked (INV-9)
│   │   ├── thesis/              #       authoring + falsification condition
│   │   ├── invalidation/        #       monitoring against new filings & news
│   │   ├── filings/             #       filing interpretation
│   │   ├── claims/              #       ★ claim extraction + evidence-span binding
│   │   └── monitor/             #       ★ RM-1…RM-15 — variance, base rates, calibration
│   │
│   ├── quant/                   # D-03  SEAT-3   stateless calculation
│   │   ├── horizons/            #       ★ the HorizonSet — 1w/1m/1q contract
│   │   ├── screens/             #       52w position, gaps, volume, momentum rank
│   │   ├── signals/
│   │   ├── backtest/            #       engine, costs, purge/embargo protocol
│   │   ├── metrics/             #       RankIC, ICIR, Sharpe — with effective-N
│   │   ├── gates/               #       threshold + statistic + distribution
│   │   └── methods/             #       ★ METHOD REGISTER — maths + citations
│   │
│   ├── models/                  # D-04  SEAT-3   ML lifecycle
│   │   ├── artifact/            #       ★ manifest: contract VERSION, not a column list
│   │   ├── train/               #       selection (1m) · timing (1w)
│   │   ├── infer/               #       score · arbitrate (1m nominates, 1w may veto)
│   │   ├── governance/          #       ★ parity · promotion · drift · registry
│   │   └── zoo/                 #       model families; each needs a MethodEntry
│   │
│   ├── risk/                    # D-05  SEAT-4
│   │   ├── exposure/
│   │   ├── metrics/             #       VaR, CVaR, correlation, drawdown
│   │   ├── stress/
│   │   └── flags/               #       pyramiding, registered short-hold — M-3 / M-4
│   │
│   ├── portfolio/               # D-06  SEAT-4   arithmetic only, never an allocation
│   │   ├── sizing/              #       size given a stop (+ stop_distance from vol)
│   │   ├── scenario/            #       what-if impact of a candidate position
│   │   ├── pyramid/             #       ★ M-3: scale-in flag AND the hold alternative
│   │   └── contracts/
│   │
│   ├── orchestration/           # D-08  SEAT-5
│   │   ├── jobs/                #       job definitions
│   │   ├── schedule/
│   │   └── state/               #       run records, checkpoints
│   │
│   ├── decision/                # D-12  SEAT-5   custody of the COMPOSITION
│   │   │                        #       LEVEL 1 RECOMMEND · deterministic, NO agent
│   │   ├── algebra/             #       ★ the verdict meet-semilattice (P3 by type)
│   │   ├── compose/
│   │   ├── attribute/           #       every binding gate, not the first
│   │   ├── counterfactual/      #       ★ vetoed candidates — the measurable arm
│   │   └── contracts/
│   │
│   ├── reporting/               # D-09  SEAT-5   custody of the ARTIFACT
│   │   │                        #       LEVEL 1 RECOMMEND · the only seat-5 domain with an agent
│   │   ├── render/              #       card · slate · brief
│   │   │   ├── classes.py       #       ★ reliability-class tagging (fact/computation/judgement)
│   │   │   └── lint.py          #       ★ forecast-voice · length · uncited-claim checks
│   │   ├── deliver/             #       email + self-contained archive (P6)
│   │   ├── online_api/          #       local + phone READ-ONLY surface
│   │   └── contracts/           #       report/brief/card schemas
│   │
│   ├── recording/               # D-11  SEAT-5   custody of the FACT
│   │   │                        #       LEVEL 0 AUTONOMOUS · no agent, no LLM, no rendering
│   │   ├── ingest/              #       broker export → RawActivity, verbatim + hashed
│   │   ├── orders/              #       ★ tranche grouping (partial fills)
│   │   ├── instruments/         #       ★ CDR vs underlying — same ticker, 2 instruments
│   │   ├── book/                #       positions, book state, P&L, NAV snapshot
│   │   ├── capital/             #       ★ the capital base — QA-63
│   │   ├── reconcile/           #       export ↔ computed book, break detection
│   │   ├── trades/              #       retrospective log
│   │   ├── arrival/             #       ★ forward log — arrival quotes (QA-69)
│   │   ├── journal/             #       decision journal
│   │   ├── attribution/         #       performance attribution
│   │   └── contracts/           #       portfolio_state / book_state / trade-log schemas
│   │
│   └── experiments/             # D-10  P7-EXEMPT · SEAT-5 · serves ALL analyst seats
│       ├── sweeps/              #       hyperparameter search  ← ohlcv/experiments (reuse)
│       ├── tuning/              #       grid/random generation ← grid_gen.py
│       ├── evaluate/            #       CPCV, walk-forward     ← cpcv.py
│       ├── leaderboard/         #       cross-variant AND cross-domain comparison
│       ├── registry/            #  ★    variant registration + resolution
│       ├── store/               #  ★    run records, variant hashes, results
│       ├── promote/             #  ★    the P7 promotion gate — baseline ← variant
│       └── variants/            #  ★★   ALL variant code lives HERE, not in the domains
│           ├── fundamental/     #       rubric / prompt / extraction variants
│           ├── quant/           #       feature, screen, horizon variants
│           ├── models/          #       architecture, backend, hyperparameter variants
│           ├── risk/            #       formula, limit, scenario variants
│           └── decision/        #       composition-rule variants
│
├── pipeline/                    # LEGACY — frozen, shrinking, deleted at the end
├── tests/                       # legacy tests (import pipeline.*)
├── tests_src/                   # new tests (import src.*) — merged into tests/ at cutover
├── config/
├── data/
└── sdd/
```

### Three naming notes

- **`online_api/`, not `online-api/`.** A hyphen is not a legal Python identifier — `import
  reporting.online-api` is a syntax error, so a hyphenated directory can never be a package. The
  intent is preserved with an underscore, which is also the convention everywhere else in the tree.
- **`data_engine/src/` means *data source*, not *source code*.** It is a deliberate choice and it
  reads ambiguously next to the top-level `src/`. If that bothers you later, `sources/` or
  `providers/` says the same thing without the collision — flagged as **Q-6**, not changed.
- **`experiments/` is inside `src/`** rather than a sibling `research_lab/`. That makes the
  P7 boundary an import rule rather than a directory rule — see **ST-2**.
- ★★ **`variants/` lives under `experiments/`, NOT under the domain it varies.** A variant under
  `src/fundamental/variants/` was the intuitive placement and it breaks two things at once:
  `src/fundamental/**` is a **governed glob**, so the `sdd_gate` hook would demand spec-reading for
  work P7 exempts; and production code could import it as an ordinary intra-domain import, which
  **ST-2's CI grep cannot see** — it greps for the *name* `experiments` outside `src/experiments/`.
  ⚠ **Locality would have created a leak path the one-way rule is blind to.** See
  [`L1-experiments-intent.md`](L1-experiments-intent.md) §9A.

## 1.2 Domain → path map

Authoritative binding of L0 §16.2 to directories. **A file's directory determines its domain,
its domain determines its owning seat, and its seat determines its authority.**

| ID | Domain | Seat | Path | LLM? |
|---|---|---|---|---|
| **D-00** | Shared Infrastructure | — | `src/shared/` | gateway only |
| **D-01** | Fundamental Analysis | SEAT-2 | `src/fundamental/` | **yes** |
| **D-02** | **Feature Engineering** | **SEAT-5** | `src/feature_engineer/` | **no** |
| **D-03** | Quantitative Analysis | SEAT-3 | `src/quant/` | **no** |
| **D-04** | Model Training & Inference | SEAT-3 | `src/models/` | **no** |
| **D-05** | Risk Management | SEAT-4 | `src/risk/` | **no** |
| **D-06** | Portfolio Strategy | SEAT-4 | `src/portfolio/` | **no** |
| **D-07** | Data Engine | SEAT-5 | `src/data_engine/` | **no** |
| **D-08** | Orchestration | SEAT-5 | `src/orchestration/` | **no** |
| **D-09** | **Reporting** | SEAT-5 | `src/reporting/` | rendering only |
| **D-10** | **Experiments** *(P7-exempt)* | SEAT-5 | `src/experiments/` | **no** |

> ★ **D-10 has no L1 spec by decision** (L0 §4.2, 2026-08-18) — what to experiment on is not knowable until the other ten domains run end-to-end. **`ST-2` is therefore not a tidiness rule for D-10; it is the only thing holding it.** An unspecified domain that nothing may import cannot leak into production; an unspecified domain that anything may import is an unspecified production dependency.

| **D-11** | **Recording** | SEAT-5 | `src/recording/` | **no** |
| **D-12** | **Decision** | SEAT-5 | `src/decision/` | **no** |

> Only **D-01** performs LLM reasoning. **D-00** owns the gateway that makes the call; **D-09** may
> render LLM-produced text it did not author (DC-1). Every other domain is deterministic — this is
> **AP-5**, and it is checkable by grepping for gateway imports outside `src/fundamental/`.

### D-02 belongs to SEAT-5 — and that is what keeps INV-014 intact

**Decided 2026-08-14 (closes Q-7).** D-02 is owned by **SEAT-5**, alongside D-07. The reasoning is
that D-02 is derived-data custody: it consumes D-07, computes deterministically, and serves whoever
asks. That is the same duty as the Data Engine, one step downstream — not analysis.

This is not merely a filing decision. **Placing D-02 under SEAT-5 is what stops it colliding with
INV-014.**

INV-014 forbids each analyst seat from consuming *the other seat's* analytical output, and names
fair value in that list. Had D-02 stayed under SEAT-2, a fair value flowing into D-03/D-04 would
have been SEAT-3 consuming SEAT-2's output — a violation on the face of it. Under SEAT-5 it is
neither seat's output. **Both analyst seats consume a neutral third party, and neither inherits the
other's conclusion.** Independence is preserved by ownership rather than by exception.

```text
                    ┌──────────────────────┐
                    │  D-07 Data Engine    │  SEAT-5
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │ D-02 Feature Engineer│  SEAT-5   ← neutral ground
                    │ deterministic compute│
                    └─────┬──────────┬─────┘
                          │          │
             ┌────────────┘          └────────────┐
             ▼                                    ▼
   ┌──────────────────┐                 ┌──────────────────┐
   │ D-01 Fundamental │  SEAT-2         │ D-03 / D-04      │  SEAT-3
   │ thesis, verdict  │                 │ signals, rank    │
   └──────────────────┘                 └──────────────────┘
             └────────── never cross (INV-014) ───────────┘
```

**What still needs specifying, later.** Which D-02 outputs are published to which consumer is a
D-02 contract question, deliberately left open. It does not threaten INV-014 — every D-02 output is
SEAT-5's regardless of who reads it — so it can be settled when the D-02 L1 spec is written rather
than now.

~~**Residual wording nit (Q-8, downgraded).**~~ **CLOSED 2026-08-15 in L0 v0.9.0.** INV-014 now
forbids "the thesis's reading of a fair value" rather than a bare "fair value", and states
explicitly that both seats may consume the same D-02 number without either inheriting the other's
conclusion.

## 1.3 Module internal structure

Every leaf module follows one shape:

```text
src/<domain>/<module>/
├── __init__.py        # public API — the ONLY thing outsiders may import
├── service.py         # the operation; orchestrates the module's own pieces
├── models.py          # typed data shapes for this module
├── contracts.py       # authoritative on-disk shapes (CT-n.k), where the module owns one
├── errors.py          # module error classes
├── store.py           # parquet/JSON read+write, if the module persists anything
└── <domain-specific>/ # e.g. rules/, prompts/, adapters/
```

Notes on the deltas from the sample:

- **`store.py`, not `repository.py`.** There is no database (L0 §6.2). A store reads and writes
  files; calling it a repository imports assumptions — connection pooling, transactions,
  migrations — that do not apply and would be cargo-culted into the code.
- **No `interfaces.py` by default.** Add a Protocol when there is a second implementation, not in
  anticipation of one. Two sources (EDGAR, FMP) justify one in `data_engine/src/`; almost
  nothing else does. ⚠ **Corrected 2026-08-23** — this line said `data_engine/sources/` while §1.1
  and §1.5 said `data_engine/src/`. One directory, two names, in one document; `src/` binds.
- **`contracts.py` is new** and has no analogue in the sample. It exists because the on-disk shapes
  are now the integration surface between domains, and a Parquet file with no declared schema is
  the file-based equivalent of an untyped API.

## 1.4 The three migration classes

Every legacy file is exactly one of these. The class determines the commit shape.

| Class | Meaning | Commit shape |
|---|---|---|
| **VERBATIM** | Moves unchanged. Content is correct and battle-tested; only its address changes. | `git mv` (pure, R100) → **separate commit** for the re-export shim. Any edit waits for a third commit. |
| **REVIEW** | Moves, then is deliberately rewritten against a written AC. | `git mv` first, rewrite in a **later** commit. Never both at once. |
| **REBUILD** | Written fresh in `src/`. No history to preserve. | plain `git add`. Legacy file deleted at cutover. |
| **EXCLUDE** | Not migrated. | Left in `pipeline/` until deleted, or its disposition is an open question. |

> **The rule that protects history:** a move commit changes *zero bytes of content*. Git stores no
> renames — it detects them by similarity at diff time — so a combined move+rewrite is recorded as
> delete+add and `git log --follow` stops dead there. Verify each move with
> `git show --stat -M --find-renames=100% HEAD` and expect `R100` on every line.
> **Never squash a move commit into a rewrite commit.**

## 1.5 Migration table

Legacy inventory: **38,669 LOC** across 35 packages. Classified below.

### D-07 Data Engine — `src/data_engine/`

The spine of the parallel build, and the largest verbatim inheritance.

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `fundamental_analysis/etl/point_in_time.py` | 703 | `data_engine/pit/point_in_time.py` | **VERBATIM** | ★ PIT enforcement. Move untouched; write its contract before refactoring. F0 records it as once un-importable — you will want the blame. |
| `fundamental_analysis/etl/restatement_tracker.py` | 444 | `data_engine/pit/restatement.py` | **VERBATIM** | PIT-adjacent; moves with it |
| `fundamental_analysis/etl/xbrl_parser.py` | 616 | `data_engine/src/edgar/xbrl.py` | **VERBATIM** | |
| `fundamental_analysis/etl/companyfacts_extractor.py` | 593 | `data_engine/src/edgar/companyfacts.py` | **VERBATIM** | governed today by F9 — glob must move with it |
| `fundamental_analysis/etl/edgar_client.py` | 496 | `data_engine/src/edgar/client.py` | **VERBATIM** | |
| `fundamental_analysis/etl/fmp_fundamentals.py` | 213 | `data_engine/src/fmp/fundamentals.py` | **VERBATIM** | governed today by F9 |
| `data_providers/fmp_provider.py` | 641 | `data_engine/src/fmp/client.py` | **REVIEW** | ★ carries the EDGAR-over-FMP TTM precedence. Move verbatim, then split client from precedence policy |
| `data_providers/base.py` + `market_data.py` | 164 | `data_engine/src/base.py` | **REVIEW** | collapse into one source Protocol |
| `fundamental_analysis/etl/ingest_validator.py` | 265 | `data_engine/validation/` | **REVIEW** | rewrite as composable rules (L0 §6.4 DQ-nnn) |
| `fundamental_analysis/etl/universe_manager.py` | 194 | `data_engine/universe/` | **REVIEW** | |
| `buffett/etl/**` | 2,493 | `data_engine/validation/` + `src/` | **REVIEW** | enricher + cross-source validator; expect real shrinkage |
| `buffett/screening/watchlist_manager.py` | ~130 | `data_engine/universe/watchlist.py` | **REVIEW** | membership is data, not analysis |
| `fundamental_analysis/data_providers/**` | 223 | — | **REBUILD** | duplicates `data_providers/`; resolve to one |
| `fundamental_analysis/etl/data_ingest_scheduler.py` | 565 | `orchestration/` | **REBUILD** | scheduling is D-08, not D-07 |
| `fundamental_analysis/etl/etl_inspect.py` | 167 | `experiments/` | **REVIEW** | dev tool → D-10 |
| *(new)* | — | `data_engine/contracts/` | **REBUILD** | parquet/JSON schemas — no legacy equivalent exists |
| *(new)* | — | `data_engine/store/` | **REBUILD** | atomic write-temp-rename; the property a DB gave free |

**Verbatim subtotal: 3,065 LOC** inherited with history intact.

### D-01 Fundamental Analysis — `src/fundamental/`

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `buffett/synthesis/prompt_alignment.py` | 358 | `fundamental/prompts/alignment.py` | **VERBATIM** | enforces INV-9; do not touch during the move |
| `buffett/synthesis/report_writer.py` | 1,108 | **split** → `fundamental/prompts/` + `reporting/render/` | **REVIEW** | ★ largest file in the repo and doing two jobs. Prompt assembly is D-01; markdown rendering is D-09 |
| `buffett/analysis/news_analyst.py` | 473 | `fundamental/invalidation/news.py` | **REVIEW** | thesis-aware news check |
| `buffett/analysis/llm_filing_parser.py` | 242 | `fundamental/filings/parser.py` | **REVIEW** | |
| `buffett/synthesis/archetype_classifier.py` | 221 | `fundamental/prompts/` | **REVIEW** | prompts reused **with careful review** |
| `buffett/synthesis/supply_side.py` | 176 | `fundamental/prompts/` | **REVIEW** | |
| `buffett/synthesis/etf_tripwire.py` | 175 | `fundamental/prompts/` | **REVIEW** | |
| `buffett/synthesis/sensitivity.py` | 173 | `fundamental/prompts/` | **REVIEW** | |
| `buffett/synthesis/cycle_position.py` | 165 | `fundamental/prompts/` | **REVIEW** | |
| `buffett/report/company_report.py` | 817 | `reporting/render/` | **REVIEW** | rendering, not research |

### D-02 Feature Engineering — `src/feature_engineer/`

**The largest structural change from v0.1.0.** D-02 was Valuation under SEAT-2; it is now the
shared deterministic computation layer, absorbing the feature work that v0.1.0 had split between
D-03 (`quant/indicators/`) and D-04 (`models/features/`). One layer computes; two analyst seats
consume.

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `buffett/analysis/dcf_calculator.py` | 440 | `feature_engineer/valuation/dcf.py` | **VERBATIM** | ★ |
| `buffett/analysis/moat_scorer.py` | 191 | **split** → `feature_engineer/quality/moat.py` + `fundamental/` | **REVIEW** | ⚠ **not VERBATIM any more.** `_llm_score` reads `moat_type` / `moat_threats` / `management_signals` out of D-01's LLM-authored profile, so 30% of this score is seat-2 judgement inside a SEAT-5 domain — an **INV-014 breach**. The panel-native moat (`core/fundamental_engine._moat_quant`) is the D-02 one. See `L1-feature-engineering.md` §8.3, FE-20 |
| `buffett/analysis/quality_checker.py` | 154 | `feature_engineer/quality/checks.py` | **VERBATIM** | |
| `buffett/analysis/safety_margin.py` | 82 | `feature_engineer/valuation/margin_of_safety.py` | **VERBATIM** | |
| `buffett/analysis/technical_analyzer.py` | 181 | `feature_engineer/technical/` | **VERBATIM** | *(was D-03 in v0.1.0)* |
| `buffett/synthesis/valuation_reconciler.py` | 236 | `feature_engineer/valuation/reconcile.py` | **REVIEW** | |
| `buffett/screening/quality_screener.py` | ~128 | `feature_engineer/quality/screen.py` | **REVIEW** | |
| `fundamental_analysis/features/**` | 1,140 | `feature_engineer/fundamental/` | **REVIEW** | ratios, margins, accruals, Piotroski, trend, sector-relative *(was D-04)* |
| `ohlcv/dataset/ohlcv_feature_engineer.py` | ~400 | `feature_engineer/technical/` | **REVIEW** | *(was split D-03/D-04 — now one home)* |
| `ohlcv/dataset/**` *(rest)* | ~2,120 | `feature_engineer/ml_features/` + `labels/` + `contracts/` | **REVIEW** | ★ owns the feature contract — the artifact INV-4 parity asserts against *(was D-04)* |
| `core/feature_builder.py` | 79 | `feature_engineer/ml_features/` | **REVIEW** | *(was D-04)* |
| `fundamental_analysis/models/label_builder.py` | ~300 | `feature_engineer/labels/` | **REVIEW** | *(was D-04)* |
| *(new)* | — | `feature_engineer/contracts/` | **REBUILD** | feature-set schema + version, consumed by D-01, D-03, D-04 |

**Verbatim subtotal: 1,048 LOC.** Total inbound ≈ **5,450 LOC** — D-02 becomes the second-largest
domain after D-04.

> **Why this grouping earns its keep:** every one of these is deterministic arithmetic over
> D-07 data, and all of it was previously scattered across `buffett/analysis/`,
> `fundamental_analysis/features/`, `ohlcv/dataset/` and `core/`. Consolidating it puts every
> number that feeds an analyst behind one contract and one set of tests.
>
> **The risk to watch:** D-02 is now on the critical path of both analyst seats, so a defect here
> is a defect in both views *simultaneously* — the two views stop being independent evidence
> without INV-014 being violated on paper. Its test bar should be the highest in the tree.

### D-03 Quantitative Analysis — `src/quant/`

Narrowed by the D-02 change: D-03 no longer computes features, it *consumes* them.

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `ohlcv/backtest/**` | 487 | `quant/backtest/` | **REVIEW** | consumes D-02 features. ⚠ **`backtester.py:107`'s hard-coded `initial_capital = 20000.0` is NOT patched in place** — the capital base is read from D-11 in the rebuilt version only (D-03 **QA-114/115**) |
| `buffett/signals/**` | 354 | `quant/signals/` | **REVIEW** | |
| *(new)* | — | `quant/screens/` | **REBUILD** | 52w position, gaps, volume, momentum rank — cross-sectional screens over D-02 output |

### D-04 Model Training & Inference — `src/models/`

Narrowed by the D-02 change: D-04 trains and infers; it no longer owns feature construction.

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `ohlcv/models/**` | 2,736 | `models/train/` + `models/infer/` | **REVIEW** | 18 files; ranker/regressor/classifier bundle |
| `fundamental_analysis/models/**` *(less label_builder)* | ~1,074 | `models/` | **REVIEW** | fundamental scorer, threshold optimizer |
| `training/**` | 631 | `models/train/` | **REVIEW** | |
| `ohlcv/policy/sleeve_selector.py` | 405 | `models/infer/` | **REVIEW** | |
| `ohlcv/eval/**` | 195 | `models/governance/` | **REVIEW** | |
| `ohlcv/training/**` | 189 | `models/train/` | **REVIEW** | |
| `core/fundamental_engine.py` | 139 | `models/` | **REVIEW** | |
| *(new)* | — | `models/governance/parity.py` | **REBUILD** | INV-4 parity as an explicit gate against the D-02 feature contract, not an implicit convention |


### D-05 Risk / D-06 Portfolio Strategy — `src/risk/`, `src/portfolio/`

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `discipline/risk.py` | ~250 | `risk/metrics/` | **REVIEW** | |
| `discipline/flags.py` | ~200 | `risk/flags/` | **REVIEW** | pyramiding + registered short-hold (M-3, M-4) |
| `discipline/context.py` | ~200 | `risk/exposure/` | **REVIEW** | |
| `discipline/gate.py` | ~200 | **deferred** | **REVIEW** | see §1.6 |
| *(new)* | — | `portfolio/sizing/` | **REBUILD** | size-given-a-stop; today embedded in report code |
| *(new)* | — | `portfolio/scenario/` | **REBUILD** | what-if arithmetic; no legacy equivalent |
| *(new)* | — | `risk/stress/` | **REBUILD** | |

### D-08 Orchestration — `src/orchestration/`

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `main_pipeline.py` · `main_inference.py` · `main_buffett.py` | 1,792 | `orchestration/jobs/` | **REBUILD** | entry points become thin job definitions; the logic in them belongs to owning domains |

### D-11 Recording — `src/recording/` *(new domain, v0.4.0)*

`pipeline/portfolio/**` splits across three modules rather than landing in one. It is a small
package doing three separable jobs, and the split is what the D-09 cut was for.

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `portfolio/reconcile.py` | 329 | `recording/reconcile/` | **REVIEW** | broker export ↔ book, break detection — governed today by F4 |
| `portfolio/ingest.py` | 270 | `recording/reconcile/ingest.py` | **REVIEW** | ⚠ **BMO InvestorLine** CSV/XLSX parse — the file's own docstring misnames the broker as CIBC (`L1-recording.md` §5.3 H-2a); fix on move. **Boundary call:** it is ingestion, but of *our own book*, not of market data — it stays out of D-07, which owns external market sources (L1 §1.2). Recorded as **Q-11** |
| `portfolio/book_state.py` | 162 | `recording/book/` | **REVIEW** | |
| `portfolio/snapshot.py` | 101 | `recording/book/snapshot.py` | **REVIEW** | ★ carries the FX-3 `nav_base = None` behaviour `L2-shared-money.md` cites as prior art. Do not "fix" the None |
| `portfolio/trade_log.py` | 129 | `recording/trades/` | **REVIEW** | |
| `discipline/journal.py` | 195 | `recording/journal/` | **REVIEW** | governed today by F2 — the one D-11 file that does **not** come from `portfolio/` |
| *(new)* | — | `recording/attribution/` | **REBUILD** | performance attribution; no legacy equivalent. Reserved desk **F8** |
| *(new)* | — | `recording/contracts/` | **REBUILD** | `portfolio_state` / `book_state` / trade-log schemas — F4 CT-4.1/CT-4.2 made explicit |

**Inbound ≈ 1,186 LOC.** Every row is deterministic; **no file here may import the LLM gateway or
a renderer** (ST-5, ST-9).

### D-09 Reporting — `src/reporting/`

Narrowed by the split: D-09 renders and delivers, and keeps no book.

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `report/**` *(less `schemas.py`)* | 1,618 | `reporting/render/` | **REVIEW** | brief, slate, renderer, Discipline Card, your-move — governed today by F1 |
| `report/schemas.py` | 494 | `reporting/contracts/` | **REVIEW** | F1's report + card schemas; they are contracts, not renderers |
| `api/**` | 2,224 | `reporting/online_api/` | **REVIEW** | |
| `buffett/report/**` | 1,216 | `reporting/render/` | **REVIEW** | |
| `ohlcv/reports/**` | 449 | `reporting/render/` | **REVIEW** | |
| `delivery/**` | 177 | `reporting/deliver/` | **VERBATIM** | governed today by F2 |

### D-00 Shared — `src/shared/`

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `utils/**` | 383 | `shared/` | **REVIEW** | |
| `llm/llm_client.py` | 247 | `shared/llm/client.py` | **VERBATIM** | the gateway — D-00, not D-01 |

### D-10 Experiments — `src/experiments/` *(P7-exempt)*

| Current | LOC | → Target | Class | Note |
|---|---|---|---|---|
| `ohlcv/experiments/**` | 1,978 | `experiments/{sweeps,tuning,evaluate,leaderboard}/` | **REVIEW** | ✅ **Reuse decided 2026-08-22** (QX-5). The "experiment feature" — hyperparameter search, CPCV, grid generation, blend attribution. ★ `_deep_merge(base, override)` is already the baseline+variant overlay; `VariantSpec.backend` is already a named registry. **Move first, generalise second — never both in one commit** |
| `buffett/backtest/**` | 2,030 | `experiments/evaluate/` — ★ **by harvest, not by move** | **REBUILD** | ✅ **Q-9 closed 2026-08-22: harvested into D-10.** 2,030 LOC, **0 tests** — ⚠ nothing is `git mv`-ed, or untested code that moves becomes untested code that ships. ★ **`iv_replay.py` is the prize**: a point-in-time *fundamental* backtest, which is the evaluation protocol the reused quant-shaped runner lacks. Required reading list and the rel4 measured results in [`L1-experiments-intent.md`](L1-experiments-intent.md) §9C |
| `fundamental_analysis/etl/etl_inspect.py` | 167 | `experiments/` | **REVIEW** | dev inspection tool |

> **D-10 is inside `src/` but exempt from spec rigor (P7).** The boundary is therefore an *import
> rule*, not a directory rule: **`src/experiments/` may import any other domain; no other domain may
> import `src/experiments/`** (ST-2). Promotion of an experiment's output into a governed domain
> requires a spec.
>
> The one-way rule is what keeps the exemption honest. Without it, "exempt from spec rigor" leaks
> into production by import rather than by decision.

## 1.6 Files with no home yet

Two items cannot be placed, and inventing a home for either would silently decide something L0
leaves open. Both are recorded rather than resolved.

| Item | LOC | Why it is blocked |
|---|---|---|
| `core/signal_engine.py` | 221 | **This is the combine point.** It merges the quant ranking with the thesis verdict — precisely the question L0 §1.6 defers. It belongs to D-03, D-05, or a domain that does not exist yet, depending on how seats 3 and 3 combine. **Do not move it until §1.6 resolves.** |
| `discipline/gate.py` | ~200 | Implements the gate `signal_engine` applies. The monotonicity rule survives (constitution P3), but which domain owns the gate follows from §1.6. |

Everything else in the migration table is independent of that decision — which is the useful
finding. **The deferral blocks ~420 LOC, not the restructure.**

## 1.7 Structural rules

| Rule | Statement |
|---|---|
| **ST-1** | **`src/` MUST NOT import `pipeline/`.** Ever, including temporarily. The legacy tree depends on the new one via shims; the reverse makes `pipeline/` undeletable and the parallel build becomes a permanent fork. |
| **ST-2** | **No domain may import `src/experiments/` (D-10).** The reverse is allowed — D-10 may import anything. P7 exempts experiments from spec rigor, and this one-way rule is what stops that exemption leaking into production by import rather than by decision. |
| **ST-3** | Cross-domain imports go through the domain's `__init__.py` public API. Reaching into `src/<domain>/<module>/service.py` from another domain is a defect. |
| **ST-4** | A domain's directory determines its seat and therefore its authority (§1.2). Placing a file is an authority decision, not a filing decision. |
| **ST-5** | **The LLM gateway is imported only by `src/fundamental/`.** Any other domain importing it violates AP-5 and is grep-checkable in CI. |
| **ST-6** | Every move commit changes zero bytes. Verified by `R100` (§1.4). |
| **ST-7** | **The test suite is green at every commit.** A move commit that reddens it means the shim is wrong — which is exactly what the shim exists to reveal. |
| **ST-8** | When a governed path moves, its glob in `sdd/specs/ownership.yaml` moves **in the same commit**. A stale glob matches nothing and the `sdd_gate` hook **fails open silently**. This is the highest-risk step in the whole migration. |
| **ST-9** | **`src/recording/` (D-11) MUST NOT import `src/reporting/` (D-09).** The reverse is allowed and expected. Recording is LEVEL 0 custody of fact; Reporting is LEVEL 1 and is read as advice. An import in the forbidden direction puts a renderer upstream of the book, which is how a printed number ends up rewriting the record it claimed to describe. Grep-checkable in CI, like ST-2 and ST-5. |
| **ST-10** | ★ **`src/fundamental/` (D-01) and `src/quant/` (D-03) MUST NOT import `src/decision/` (D-12).** Composition flows one way. A composed verdict returning to either analyst seat is **INV-014 laundered through a third party and a time lag** (`L1-decision.md` DN-3). Grep-checkable in CI, like ST-2, ST-5 and ST-9. |

## 1.8 Superseded by L0 — do not copy from the sample

`samples/L4-coding-standards.md` is the format reference. These of its decisions do not apply:

| Sample says | Here | Why |
|---|---|---|
| `async` for all I/O | **sync** | Daily batch, no server. 2 `async def` in 38.7k lines today |
| `Result[T, E]` for expected failures | **raise** | Constitution **P5 fail loud**. A `Failure` that a caller forgets to check is the silent degradation P5 exists to prevent |
| Pydantic for everything crossing a boundary | **dataclass by default**, Pydantic where input is untrusted | 47 dataclass vs 16 Pydantic files today; validation belongs at the ingest boundary, not on every internal hop |
| `repository.py` + PostgreSQL | **`store.py`** + parquet/JSON | L0 §6.2 |
| bare `int` cents | **`Money(amount_minor, currency)`** | INV-001 — a bare int is the untagged value the invariant forbids |
| Polygon + AlphaVantage adapters | **EDGAR + FMP** | L0 §2.2 |

---

## Open questions

| ID | Question | Blocks |
|---|---|---|
| ~~Q-1~~ | ~~Concrete shape of `Money`~~ | **CLOSED 2026-08-14** — see [`L2-shared-money.md`](L2-shared-money.md) |
| **Q-2** | Does `data_engine/store/` expose typed accessors per artifact, or a generic reader keyed by contract? | D-07 L1 |
| ~~**Q-3**~~ | ~~Does D-10 move first or last?~~ | ✅ **CLOSED — [`L3-build-sequence.md`](L3-build-sequence.md) §7.** ★ **Neither: a non-question.** D-10's content is unknowable before M3, and **ST-2's one-way rule means no domain can be blocked by it** — the question presupposed a critical path the import rule already removes it from |
| **Q-4** | `tests_src/` merged into `tests/` at cutover, or kept split permanently? | test layout |
| ~~**Q-5**~~ | ~~L0 §1.6 — how seats 3 and 3 combine~~ | ✅ **CLOSED — `L2-signal-combination.md` + `D-12`.** The ~420 LOC is no longer blocked: `signal_engine.py` → `src/quant/`, `gate.py` → `src/decision/` |
| **Q-6** | `data_engine/src/` vs `sources/` vs `providers/` — the nested-`src` ambiguity | cosmetic; decide before the first move |
| ~~Q-7~~ | ~~Which seat owns D-02?~~ | **CLOSED 2026-08-14 — SEAT-5** (§1.2) |
| ~~Q-8~~ | ~~INV-014 lists "fair value" as a seat-2 output~~ | **CLOSED 2026-08-15** — L0 v0.9.0 §7.2 |
| ~~Q-10~~ | ~~Which D-02 outputs are published to D-01 vs D-03/D-04?~~ | **CLOSED 2026-08-16** — `L1-feature-engineering.md` §6 |
| **Q-11** | Does `portfolio/ingest.py` (broker-export parse) belong to **D-11 Recording** or **D-07 Data Engine**? Placed in D-11 for now — it ingests *our own book*, not market data, and D-07's boundary is external market sources | D-11 L1 · D-07 L1 §8 |
| ~~**Q-9**~~ | ~~`buffett/backtest/` (2,030 LOC, 0 tests) — join D-10 or drop?~~ | ✅ **CLOSED 2026-08-22 — neither: HARVESTED.** Class `EXCLUDE` → `REBUILD`; designs and recorded results carry across, the files do not. See `L1-experiments-intent.md` §9C |

---

**Next sections of this document, not yet drafted:** §2 naming · §3 typing · §4 functions ·
§5 errors · §6 logging · §7 configuration · §8 pandas/parquet conventions · §9 imports ·
§10 comments · §11 git conventions · §12 tooling · §13 AI-agent checklist.

---
---

# 5. ERROR HANDLING — raise, never return

> ⚠ **The sample's §5 is titled "RESULT TYPE — the core error handling pattern". It does not apply
> here** (§1.8). `Result[T, E]` makes failure a *return value*, and a return value can be ignored by
> forgetting one `if`. Constitution **P5** requires the opposite: a degraded input must **stop the
> program**, not travel onward wearing a type. This section is the replacement, not the adaptation.

## 5.1 The rule

```text
╔══════════════════════════════════════════════════════════════════╗
║  A FUNCTION THAT CANNOT DO ITS JOB RAISES.                       ║
║                                                                  ║
║  It does not return None.  It does not return 0.0, 0.5, an       ║
║  empty DataFrame, or a "default". It does not log a warning and  ║
║  continue.  It raises, and the raise carries enough to fix the   ║
║  problem without rerunning.                                      ║
║                                                                  ║
║  This repo has TWO REAL INCIDENTS from the other choice: a       ║
║  discipline card built out of a failed LLM narrative and emailed ║
║  as a genuine recommendation, with no stop and no targets.       ║
║  Nothing crashed. That was the problem.                          ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **EH-1** | ★ **A failure raises.** No `Result`, no `Optional` used as an error channel, no sentinel return |
| **EH-2** | ★ `Optional[T]` means **"this value is legitimately absent"** — never "this failed". `None` for *no position held* is correct; `None` for *the price lookup failed* is a defect |
| **EH-3** | ★ **`except Exception: pass` and bare `except:` are defects**, always. `except Exception: <fallback value>` is the same defect with extra steps |
| **EH-4** | An exception carries: **what was being attempted, the identifying key** (ticker, date, `as_of`, `run_id`), **and the value that failed the check**. `"invalid input"` is not an error message |
| **EH-5** | Catch **narrowly and locally**. A `try` block spanning more than the one call that can fail hides which call failed |
| **EH-6** | ★ **Re-raise or wrap — never swallow.** Wrapping is `raise DomainError(...) from exc`; the `from` is mandatory, because a lost `__cause__` is a lost diagnosis |

## 5.2 The one legitimate exception: declared unavailability

Fail-loud does not mean *everything is fatal*. Several specs need **"this quantity could not be
computed"** as a **first-class value** — D-06 `PS-34`, D-05 `RK-23`, D-07 `DE-35`.

| ID | Rule |
|---|---|
| **EH-7** | ★ **`Unmeasured` is a declared type, not a `None` and not a `NaN`.** It carries **why**, and it is **impossible to arithmetic with** — any operation on it raises. That is the whole point: an absent input must not silently become a number downstream |
| **EH-8** | ★ **A renderer must be able to display `Unmeasured`, and must never substitute for it** (DC-3). "—" is a correct rendering; `0.0` is a lie |
| **EH-9** | The distinction is: **`raise`** when the caller asked for something the system should have been able to do; **`Unmeasured`** when the answer is legitimately "we do not know", and not knowing is a reportable state |

## 5.3 Exception hierarchy

```python
PipelineError                      # base — nothing raises this directly
├── DataError                      # D-07 · ingest, contract, freshness, PIT
│   ├── SourceUnavailableError     # INV-033: degrade scope, report the absence
│   ├── ContractViolationError     # schema/dtype/units
│   └── PointInTimeError           # ★ INV-1 — a look-ahead was detected
├── FeatureError                   # D-02 · formula_id, parity, coverage
├── ModelError                     # D-04 · artifact, parity, promotion
│   └── ParityError                # ★ INV-4 — train/inference disagreement
├── BookError                      # D-11 · reconciliation, lots, FX
├── OrchestrationError             # D-08 · precondition, budget, retry
└── InvariantViolation             # ★ any INV-* breached in flight
```

| ID | Rule |
|---|---|
| **EH-10** | Every raise site uses the **narrowest class that fits**. `raise PipelineError` is never correct |
| **EH-11** | ★ **`InvariantViolation` is never caught.** It propagates to the top and fails the run. An invariant a caller can recover from is not an invariant |
| **EH-12** | ★ `PointInTimeError` and `ParityError` exist as **their own classes** because INV-1 and INV-4 are the two failures that are *invisible in every metric the system computes*. They must be impossible to catch by accident inside a broad `except DataError` |
| **EH-13** | Error **codes** (`ORC.BUDGET.EXCEEDED`, `RSK.THEME.NO_TAXONOMY`, …) live on the exception, not only in the message. The L1 error catalogs are the registry |

## 5.4 Retry — the D-08 boundary

| ID | Rule |
|---|---|
| **EH-14** | ★ **Only `src/orchestration/` retries.** A domain that retries internally hides transport failures from the layer that owns the retry policy (D-08 §7), and its retry count never reaches the RunManifest. ⚠ **One carve-out, 2026-08-23: `L1-data-engine.md` **DE-46**** — a 402 must be re-sent to be *classified* at all (§5A.2 gives it three indistinguishable causes), so that probe is not recovery. The attempt count is carried to the manifest, which is what this rule was protecting |
| **EH-15** | ★ Exception classes are tagged **retryable / not retryable**, and the default for an untagged class is **not retryable** (OR-14). `SourceUnavailableError` from a 429 is retryable; `ContractViolationError` never is |

---
---

# 10. IMPORT STANDARDS — where the architecture is actually enforced

> ★ **This is the shortest section with the most load on it.** Four of L0's structural invariants
> are *only* enforceable as import rules. Prose in a spec persuades; a CI grep decides.

## 10.1 The five checked edges

> *(Index rows — **DOC-1**: not bold, because each of these is **defined** elsewhere. `ST-*` in §1.7;
> **`OR-3` in [`L1-orchestration.md`](L1-orchestration.md)**, which is another spec's rule and must
> not appear here as though this document owned it.)*

| # | Rule | Grep |
|---|---|---|
| ST-1 | `src/` must not import `pipeline/` | `grep -rn "^from pipeline\|^import pipeline" src/` |
| ST-2 | ★ no domain imports `src/experiments/` (D-10) | `grep -rn "experiments" src/ --include=*.py \| grep -v "^src/experiments/"` |
| ST-5 | ★ the LLM gateway is imported only by `src/fundamental/` | `grep -rn "llm" src/ \| grep -v "^src/fundamental/\|^src/shared/llm/"` |
| ST-9 | `src/recording/` must not import `src/reporting/` | `grep -rn "reporting" src/recording/` |
| ST-10 | ★ neither analyst seat imports `src/decision/` | `grep -rn "decision" src/fundamental/ src/quant/` |
| OR-3 | ★ no domain imports `src/orchestration/` | `grep -rn "orchestration" src/ \| grep -v "^src/orchestration/"` |

| ID | Rule |
|---|---|
| **IM-1** | ★ **All five run in CI and fail the build.** A rule that is only in a document is a rule that is already broken somewhere |
| **IM-2** | ★ **The greps are anchored to line starts and exclude the owning directory**, or they match their own definition and pass vacuously. A structural check that cannot fail is worse than no check — it reports safety it never verified |
| **IM-3** | ★ Each check has a **test that deliberately violates it** and asserts the check fires. This is the only way to know the grep is live (the `sdd_gate` stale-glob hazard, ST-8, is the same failure shape: **fails open silently**) |

## 10.2 Ordinary import hygiene

| ID | Rule |
|---|---|
| **IM-4** | Order: **stdlib · third-party · `src/`**, one blank line between groups. `ruff` enforces it; nobody argues about it |
| **IM-5** | ★ **Absolute imports only.** `from ..models import x` obscures which domain is being crossed, which is precisely the fact §10.1 exists to make visible |
| **IM-6** | Cross-domain imports go through the domain package's `__init__.py` (**ST-3**). Reaching into `src/quant/horizons/service.py` from another domain is a defect even though Python allows it |
| **IM-7** | ★ **No import-time side effects.** No config read, no file open, no network call, no logger configuration at module scope. An import that does work makes test isolation impossible and makes `--help` hit the network |
| **IM-8** | ★ **Function-local imports are permitted only to break a genuine cycle, and must carry a comment saying which cycle.** A cycle broken by a hidden local import is an architecture defect that has been made invisible — `_append_live_prices` imports `MarketData` inside the function body today, and that is the orchestrator reaching into D-07 where §10.1 would have caught it at module scope |
| **IM-9** | `TYPE_CHECKING` imports for annotations only, never for runtime behaviour |

---
---

# 14. CONSTANTS & MAGIC NUMBERS — the difference between a fact and a choice

## 14.1 The classification that matters

```text
╔══════════════════════════════════════════════════════════════════╗
║  A LITERAL IS ONE OF THREE THINGS, AND THEY LIVE IN THREE        ║
║  DIFFERENT PLACES:                                               ║
║                                                                  ║
║  BROKER / WORLD FACT  → a named module constant, with the        ║
║      source and the date it was checked.  $9.95 is not a         ║
║      modelling choice; it is what BMO charges.                   ║
║                                                                  ║
║  POLICY CHOICE        → config/*.yaml.  Thresholds, horizons,    ║
║      budgets, ceilings, cadences. Anything a human might tune    ║
║      is config BY DEFINITION, and anything in config appears in  ║
║      the RunManifest (OR-9/OR-23).                               ║
║                                                                  ║
║  MATHEMATICAL CONSTANT → inline is fine.  252 trading days, 2    ║
║      for a square, 100 for a percent.  Name it if the READER     ║
║      would otherwise have to derive it.                          ║
║                                                                  ║
║  ★ THE FAILURE MODE IS PUTTING A POLICY CHOICE IN CODE, WHERE    ║
║    NO MANIFEST RECORDS IT AND NO REVIEW EVER SEES IT CHANGE.     ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **CN-1** | ★ **Every literal is classified before it is written.** Fact → named constant with provenance; choice → config; math → inline, named if non-obvious |
| **CN-2** | ★ **A world-fact constant carries its source and check date** in a comment: `FLAT_TRADE_FEE = Money(995, "CAD")  # BMO InvestorLine equity commission, checked 2026-08-18`. Without the date, nobody can tell a stale fact from a current one |
| **CN-3** | ★ **A policy choice hard-coded in a function body is a defect**, however obvious it looks. Three live examples: `backtester.py:107` `initial_capital = 20000.0`; `main_pipeline.py:542` `fold_years=3, val_years=1`; `sleeve_selector.py:121`'s `incumbency_delta` sharing a value with `penalty_z` by coincidence rather than by declaration |
| **CN-4** | Config values are **read once at the edge and passed down** — never re-read deep in a call stack, where the same key can resolve differently in one run |
| **CN-5** | ★ Every config value used by a run appears in the **RunManifest** (OR-9). A tuned number that no manifest records makes the run irreproducible while looking deterministic |

## 14.2 Money and units

| ID | Rule |
|---|---|
| **CN-6** | ★ **A monetary constant is a `Money`, never a bare number** — `Money(995, "CAD")`, not `9.95` and not `995`. See [`L2-shared-money.md`](L2-shared-money.md) **MO-1**; **INV-001** |
| **CN-7** | ★ **`float` is forbidden for money at rest and in any intermediate that feeds a stored field** (MO-4). ⚠ **Live violations today:** `portfolio/book_state.py:116` `cash_base += amount * float(fx["rate"])` and `portfolio/reconcile.py:140` `round(amount * float(rate), 2)` — FX conversion done in binary floating point and rounded to 2dp, which is the exact arithmetic MO-3/MO-5 exist to replace |
| **CN-8** | ★ **A number carries its unit in its name.** `THEME_REPORT_THRESHOLD_PCT` (percent) vs a bare `0.40` (fraction) is a 100× error waiting for a careless reader — and a `_BPS` / `_PCT` mix-up has already produced a **3.2× error** in this repo's cost arithmetic (D-03 QA-60) |
| **CN-9** | Percent-vs-fraction is fixed **per contract field**, stated in the contract, and never converted implicitly at a boundary |

## 14.3 Thresholds are declared, not discovered

| ID | Rule |
|---|---|
| **CN-10** | ★ A threshold that gates behaviour states **who set it, when, and on what basis** — a fitted value, a mandate number (`REGISTERED_SHORT_HOLD_DAYS = 30` is CRA-derived), or an admitted guess. **"Admitted guess" is an acceptable answer; silence is not** |
| **CN-11** | ★ **A threshold on an undefined set is unenforceable.** `THEME_REPORT_THRESHOLD_PCT = 40` with no theme taxonomy anywhere in the repo (D-05 **QK-2**) is a constant that cannot fire — the most dangerous kind, because it reads as protection |

---
---

# 17. PANDAS & DATAFRAME CONVENTIONS

> ★ **This is the highest-yield section in the document for this repo.** Almost every correctness
> defect found across the L1 specs is a pandas defect: an imputation, a misaligned index, a
> cumulative-vs-discrete period, a filter where a check belonged. 71 `sort_values`, 60 `groupby`,
> 58 `.loc[`, 31 `fillna`, 28 `iterrows` in `pipeline/` today.

## 17.1 ★ `fillna` is the P5 violation with a friendly name

```python
# core/signal_engine.py:213
return ((s - s.mean()) / std).fillna(0.0)
```

```text
╔══════════════════════════════════════════════════════════════════╗
║  A Z-SCORE FILLED WITH 0.0 SAYS "EXACTLY AVERAGE".               ║
║                                                                  ║
║  A name with missing data is not average. It is UNKNOWN. This    ║
║  line silently scores every data-poor name as perfectly median   ║
║  and lets it compete for a slot on that basis.                   ║
║                                                                  ║
║  core/fundamental_engine.py:125 does the same with .fillna(0.5)  ║
║  on a 0–1 growth score; :124's .fillna(stab.min()) is worse      ║
║  still — it imputes from the same cross-section, so one name's   ║
║  score depends on the others present that day.                   ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **PD-1** | ★ **`fillna` on a feature, score or label is a defect.** Missing is a state: **drop the row, or carry it as `Unmeasured` (EH-7)**. Never impute to a plausible middle |
| **PD-2** | ★ **Cross-sectional imputation is forbidden outright** — `fillna(mean)`, `fillna(median)`, `fillna(s.min())`. It makes one name's value depend on which other names happened to be present, which is leakage across the very axis D-03 ranks on |
| **PD-3** | `fillna` is permitted for **cosmetics only** (a display string, a report cell) and never on anything that reaches a model, a score or a stored artifact |
| **PD-4** | ★ **NaN rate is measured and reported before any handling**, not after. `feature_selection_pipeline.py:58` already gets this right and says so in a comment — that is the standard |

## 17.2 ★ Time, shifting, and INV-1

| ID | Rule |
|---|---|
| **PD-5** | ★ **Every `shift`, `rolling` and `resample` is preceded by an explicit `sort_values(["ticker","date"])` on the same frame.** Pandas will happily shift an unsorted group and produce a plausible, wrong series. There is no error and no warning |
| **PD-6** | ★ **A `shift` that crosses tickers is a look-ahead defect.** Always `groupby("ticker")[col].shift(...)`, never a bare `.shift()` on a stacked panel — the first rows of each ticker would inherit the previous ticker's tail |
| **PD-7** | ★ **Negative shifts are forward-looking by construction and are permitted only in label construction**, never in a feature. `label_builder.py:86`'s `shift(-5)` is correct *because it is a label*; the identical line in a feature module is an **INV-1 breach** |
| **PD-8** | ★ **Every feature states the last timestamp it may see**, and the day-T row sees through the T−1 close plus the day-T open (D-02 **FE-28**). A rolling window that includes the current bar's close in a decision taken at the open is look-ahead |
| **PD-9** | `rolling(n)` requires **`min_periods=n`** unless a shorter window is deliberate and stated. The default silently emits a value computed from fewer observations — a 60-day mean built from 3 days, indistinguishable in the output |

## 17.3 Alignment, joins and the silent row loss

| ID | Rule |
|---|---|
| **PD-10** | ★ **Every `merge` names `how=` and `on=` explicitly** and **asserts the row count afterwards**. A default inner join that drops 40 % of the panel produces a smaller, cleaner, entirely wrong dataset with no error |
| **PD-11** | ★ **`validate=` is mandatory on merge** (`"one_to_one"`, `"many_to_one"`). An unnoticed duplicate key silently multiplies rows, and the resulting panel still looks like a panel |
| **PD-12** | ★ **Never rely on positional alignment.** No `df[col] = some_series.values`, no `reset_index(drop=True)` immediately before an assignment "to make it line up". `.values` discards the index — which is the only thing that made the assignment correct |
| **PD-13** | Concatenating frames with different columns is explicit about the union, and the result's schema is **re-validated against the contract** (D-02) |

## 17.4 Mutation, copies, and dtypes

| ID | Rule |
|---|---|
| **PD-14** | ★ **A function never mutates a caller's DataFrame.** Copy at entry or return a new frame. This is the single most common source of "it works alone but not in the pipeline" |
| **PD-15** | ★ **No chained assignment** (`df[df.x > 0]["y"] = z`). Use `.loc[mask, col]`. Chained assignment is a no-op on a copy in some pandas versions and a write in others — the worst possible kind of bug |
| **PD-16** | `inplace=True` is not used. It saves nothing, returns nothing, and makes the mutation invisible at the call site |
| **PD-17** | ★ **Dtypes are asserted at contract boundaries, not assumed.** An `object`-dtype price column arithmetically "works" and produces garbage; a datetime silently parsed as string sorts lexically, which is correct for ISO dates and wrong for everything else |
| **PD-18** | ★ **A column that must exist is checked, not filtered.** `model_bundle.py:80` does `[c for c in self.feature_names if c in df.columns]` — a **missing feature therefore produces a smaller, silently different model input** rather than an error. That is the D-17 defect, and it is one word (`if` → `assert`) away from correct |

## 17.5 Iteration and scale

| ID | Rule |
|---|---|
| **PD-19** | `iterrows` is permitted where clarity beats speed — a 130-name book is not a performance problem, and 28 uses today are mostly fine. **But `iterrows` returns a Series with a unified dtype**, so an int column comes back as float; never use it where dtype matters |
| **PD-20** | ★ **Determinism (INV-2): every operation whose output order can vary is explicitly ordered.** `groupby(..., sort=True)`, an explicit `sort_values` before any head/tail/rank, and a stable `kind="mergesort"` where ties matter. **A ranking system with an unstable tie-break is not reproducible**, and D-03's whole product is a ranking |

---

---
---

# 18. CLEAN ARCHITECTURE — the Dependency Rule in a numerical pipeline

> **Requirement set by [`L0-system-vision.md`](L0-system-vision.md) §4.4.** L0 states *what* is
> adopted and, just as importantly, what is not. This section is *how*.
> **Reference:** Martin, *Clean Architecture* (2017), ch. 22 "The Clean Architecture"; ch. 11 DIP.

## 18.1 The rule, and the honest starting position

```text
╔══════════════════════════════════════════════════════════════════╗
║  POLICY NEVER IMPORTS MECHANISM.                                 ║
║                                                                  ║
║  A valuation formula must not know that prices arrive over       ║
║  HTTPS from FMP, that filings are XBRL, that the panel is        ║
║  Parquet, or that delivery is SMTP. It states WHAT it needs;     ║
║  something outward provides it.                                  ║
║                                                                  ║
║  The payoff is concrete and already needed: yfinance was ripped  ║
║  out and EDGAR/FMP precedence was reversed on a measured TTM     ║
║  defect (MU, 71%). Every such change SHOULD touch one adapter    ║
║  and zero analytical domains.                                    ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **The target tree is already largely compliant, and by accident of good instinct rather than by
rule.** §1.1's vertical slices, §1.3's `store.py`/`contracts.py` split, and the one-way import edges
ST-1/2/5/9/10 are all Dependency-Rule-shaped. §18 names what was implicit and closes the gaps.

## 18.2 The layer, inside a module

Clean Architecture's circles are drawn **per module**, not above the tree (L0 §4.4):

```text
   src/<domain>/<module>/
   │
   │   ◄──────────── dependencies point INWARD only ────────────
   │
   ├── models.py      ── ENTITY layer.  Types and invariants. Imports:
   │                     stdlib, numpy/pandas, other models. NOTHING else.
   ├── service.py     ── USE-CASE layer. The operation. Imports models and
   │                     PORTS. ★ Never an SDK, never a URL, never a path.
   ├── ports.py       ── the boundary Protocols this module needs (18.3)
   ├── contracts.py   ── the on-disk shapes it owns (CT-n.k)
   ├── store.py       ── ADAPTER. Parquet/JSON. Implements a port.
   ├── adapters/      ── ADAPTER. Vendor SDKs, HTTP, SMTP.
   └── errors.py      ── may be imported by any layer
```

| ID | Rule |
|---|---|
| **CA-1** | ★ **`models.py` imports no I/O, no vendor SDK, no config, no logger.** stdlib, numpy/pandas and other `models` only. It is the innermost circle and the easiest to keep clean — and the first to be quietly polluted by "just one" config read |
| **CA-2** | ★ **`service.py` imports no transport, no filesystem path and no vendor SDK.** It receives what it needs. A `service.py` containing a URL, an API key lookup, an `open()` or a `requests` import has inverted the rule |
| **CA-3** | ★ **Adapters may import inward; nothing inward may import an adapter.** `store.py` and `adapters/` are the outermost circle and are imported only by composition roots (§18.5) |
| **CA-4** | **`errors.py` is exempt from the layering** — exceptions cross every boundary by nature (§5.3). It must still import nothing outward |

## 18.3 Dependency inversion — where, and deliberately not everywhere

`L4` §1.3 says: *"No `interfaces.py` by default. Add a Protocol when there is a second
implementation, not in anticipation of one."* **That judgement stands** and is not overridden here.

| ID | Rule |
|---|---|
| **CA-5** | ★ **A port is required where a boundary is crossed that the system has already changed once, or contractually promises to change.** Not speculation — history. **Qualifying today: price/fundamental sources** (yfinance removed; EDGAR/FMP precedence reversed on measured evidence), **the LLM gateway** (INV-8 tiering, provider swaps), **delivery** (SMTP today, a read surface tomorrow — P6) |
| **CA-6** | ★ **The Protocol is declared by the CONSUMER, in the inner layer, and named for what the consumer needs** — `PriceHistory`, not `FMPClientInterface`. A port named after its implementation has inverted nothing; it has renamed the coupling |
| **CA-7** | Everything else stays concrete until a second implementation exists. **Indirection with one implementation and no reader is cost without benefit**, and it hides the dependency graph the §10.1 greps rely on |

## 18.4 ★ Where the DataFrame sits — the one that needs stating

Strict Clean Architecture would call `pandas` a framework detail and forbid it crossing a boundary.
**That reading is rejected here** (L0 §4.4).

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE PANEL IS THE DOMAIN MODEL, NOT A FRAMEWORK DETAIL.          ║
║                                                                  ║
║  A 130 x N cross-sectional panel with a (ticker, date) index IS  ║
║  the business object of a quant pipeline. Decomposing it into    ║
║  row entities to satisfy a diagram would cost orders of          ║
║  magnitude in speed, destroy the vectorised expression of every  ║
║  formula, and buy no safety whatsoever.                          ║
║                                                                  ║
║  What DOES cross boundaries is therefore a CONTRACT-BOUND        ║
║  DataFrame — schema, dtypes and units declared in contracts.py   ║
║  and validated at the boundary. That is the discipline the       ║
║  layering was asking for; the object type was never the point.   ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **CA-8** | ★ **A DataFrame crossing a domain boundary is contract-bound**: declared schema, dtypes and units in `contracts.py`, **validated at the boundary, not assumed** (L4 PD-17). An unvalidated DataFrame crossing a boundary is the file-based equivalent of an untyped API |

## 18.5 The composition root

| ID | Rule |
|---|---|
| **DOC-1** | ★ **A rule is DEFINED exactly once, in a bold ID cell; every other appearance is an index row and is NOT bold.** §12-style roll-ups and §10.1-style grep tables are indexes. ⚠ **This is what makes "one binding definition per ID" (D-03 QA-116) mechanically checkable** rather than a matter of reading carefully — the audit of 2026-08-18 found four rules defined two or three times with nothing saying which bound |
| **CA-0** | ★ **Every L1 module decomposition is subject to CA-1…CA-9 without restating them.** An L1 spec names its *modules* (what the domain is made of); **§18 governs their internal layering** (`models.py` / `service.py` / adapters / `ports.py`). ⚠ **An L1 tree drawn before §18 existed is not thereby exempt** — the audit of 2026-08-18 confirmed none of them conflict, and CA-0 is what keeps that true without eleven copies of the same rule to drift apart |
| **CA-9** | ★ **Adapters are wired in exactly one place per entry point** — the composition root — and passed inward as ports. ⚠ **For this system the composition root is `src/orchestration/` (D-08), which creates a tension worth naming: D-08 must construct adapters while computing nothing (OR-1).** Construction is not computation, so the two rules are compatible — but a "composition root" that starts making choices about *which* adapter based on data has become a decision layer, and D-12 is the only domain allowed to be one |

## 18.6 Honest gap assessment against the current target tree

| Gap | Severity | Note |
|---|---|---|
| No `ports.py` anywhere; D-07's sources are concrete | **medium** | CA-5 names three qualifying boundaries. The **price/fundamental source port is the one with a track record** of change |
| `service.py` layering is stated but unenforced | **medium** | Unlike ST-1/2/5/9/10 there is no grep for it. **An AST check for SDK/transport imports inside `service.py` and `models.py` would make CA-1/CA-2 as real as ST-2** |
| Legacy `pipeline/` violates CA-1/CA-2 broadly | **low** | Out of scope by design — `pipeline/` is being replaced, not repaired (`L1-orchestration.md` §1.5) |
| No layer distinction in `contracts.py` vs `models.py` | **low** | They differ in *authority* (on-disk vs in-memory), not in layer. Fine as is; noted so it is not mistaken for an omission |

> ★ **The one worth building is the AST check.** §10.1's greps are what make the horizontal rules
> real; CA-1/CA-2 are the vertical rules and currently have nothing equivalent. **A structural rule
> with no automated check is a comment** — and this document's own §10.1 IM-3 says exactly that.

---
