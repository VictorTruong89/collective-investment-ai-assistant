# L5: Inherited Defect Register — what `pipeline/` leaves behind

> **Tier:** `sdd/design/rel6_design/` — design tier.
> **Exists because of:** `L3-build-sequence.md` **BS-18** and L0 **G-7**.
> **Supersedes:** `sdd/specs/F0_code_map/spec.md` §12, deleted 2026-08-20.
> **Sibling:** [`L6-as-built-remaining.md`](L6-as-built-remaining.md) — ★ this file is what **`pipeline/`** left behind; L6 is what **Release 6 itself** leaves behind.

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-08-25 | Victor | ⚠⚠ **B7 readiness — the F0 defect log was deleted before it migrated.** **G-7**: *an F-spec is retired only when the code it governs is deleted, and **its acceptance criteria must migrate into the receiving L-spec first, or they are lost — the ACs are the only record of why the behaviour is what it is***. **BS-18** says the same and names the case: *"`F0`'s defect log — including the open `D-19` net-debt defect — must be carried over, not left to die with `pipeline/`."* ★ **F0 was deleted on 2026-08-20 (commit `e053786`) and nothing carried it over**, leaving **26 files pointing at a spec that does not exist** and the two open defects recorded nowhere authoritative. Recovered from git and re-homed here. |

---

# 1. Why this document exists

**B7 deletes `pipeline/`.** ★ *An F-spec is retired only when the code it governs
is deleted* (G-7) — and the F-tier was deleted **first**, on 2026-08-20, with the
departure recorded in L0 §17.5a but **the migration never performed**.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE DEFECT LOG IS THE ONLY RECORD OF WHY THE BEHAVIOUR IS       ║
║  WHAT IT IS.                                                     ║
║                                                                  ║
║  Two of these nineteen are OPEN. One of them — D-19 — changes    ║
║  every fair value in the system, is proportional to leverage,    ║
║  and reached the decision layer on a name in the actionable      ║
║  path. Losing it with the tree that contains it would erase the  ║
║  only written evidence that the number is wrong.                 ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **DF-1** | ★ **A defect is retired when the code carrying it is deleted AND its successor is shown not to carry it** — not when the file goes away. ⚠ `src/` is a rewrite, not a port, so *"the old code is gone"* is evidence about the old code only |
| **DF-2** | ★★ **An OPEN inherited defect is carried into the receiving domain's blueprint §10 before `pipeline/` is deleted.** D-19 and D-16 are already there (`D-09-reporting.md` `KNOWN_DEFECTS`, and `src/reporting/render/classes.py`), which is what makes their disclosure survive the cutover |
| **DF-3** | **A RESOLVED entry is kept, with its resolution date.** ⚠ *A register that lists only what is broken cannot tell a reader whether a class of defect was ever addressed* — and D-4, D-9 and D-13 are the reason `TTM_SOURCE_TOLERANCE` and the filing-aware cache exist |

---

# 2. ⚠ OPEN — these survive `pipeline/`

## D-19 — the DCF returns an enterprise value per share

**Where (legacy):** `analysis/dcf_calculator.py:204-214`, duplicated at
`buffett/backtest/iv_replay.py:202-212`.

★ **The DCF computes an ENTERPRISE value and divides it by share count, calling
the result `intrinsic_value_per_share`.** It projects revenue × FCF margin (a
firm-level cash flow) and discounts at **WACC** (a firm-level rate) — correctly
producing an enterprise value; the local variable is even named `entity_value` —
then does `per_share = entity_value / shares` with **no net-debt subtraction**.
The correct step is `equity = enterprise − net_debt`, *then* divide.

⚠ **The word *debt* appears nowhere in `dcf_calculator.py`**, `TTMFinancials`
carries no debt field, and neither `dcf_assumptions.yaml` nor F0 ever mentioned
the omission — **so it reads as intended.**

**The error equals net debt per share, so it scales with leverage** (measured
2026-08-11, net debt as % of market cap):

| Name | Net debt / mcap | Consequence |
|---|---|---|
| **CHTR** | **455 %** | IV/share **$1,940** against a **$157.69** price — ~12× |
| **ENB** | **128 %** | ⚠ **and ENB is on `practice_watchlist` — the actionable path (INV-6)** |
| MSFT | 3 % | negligible |
| NVDA · MU | 0–1 % | negligible, and slightly *understated* for net-cash names |

★ Found because a `--fundamental-overlay` run put CHTR at `zone=BUY
margin=+91.9%`; **it ended HOLD only because `SignalEngine` downgraded it**, so
the value *did* reach the decision layer.

| Status | 🔴 **OPEN — not fixed, deliberately.** It changes every fair value in the system |
|---|---|
| **Carried into** | `src/reporting/render/classes.py::KNOWN_DEFECTS["D-19"]`, disclosed on the artifact under **RP-5** |
| **Retired when** | D-01's valuation path subtracts net debt **and a known-answer test pins a levered name.** ⚠ Not when `pipeline/` is deleted (DF-1) |

## D-16 — `rsi_14` is not Wilder's RSI

**Where (legacy):** `OhlcvFeatureEngineer.ohlcv_build_features`.

It averages gains and losses with a **simple 14-day rolling mean**
(`x.rolling(14).mean()`); Wilder's RSI — the definition used by essentially every
charting package and TA library — uses **Wilder smoothing** (an EMA with
α = 1/14). ★ The two diverge materially after warm-up, so **our `rsi_14` is not
comparable to an RSI read off a broker screen.**

⚠ **This is a defensible variant, not a proven defect**: as a model feature its
absolute level matters less than its consistency, and it has been consistent
since it was written. ★ **Also pinned, and never documented:** `rank_ret_5d` uses
`ascending=False` while `rank_vol_20d` uses `ascending=True` — plausibly
deliberate, recorded nowhere.

| Status | 🟡 **OPEN — frozen, not verified.** `tests/test_ohlcv_features_golden.py` (2026-08-10) freezes the current values |
|---|---|
| **Carried into** | `src/reporting/render/classes.py::KNOWN_DEFECTS["D-16"]` |
| **Retired when** | D-02 either implements Wilder smoothing or **declares the variant in a MethodEntry** (QA-20) — *ours is a simple rolling mean where every charting package uses Wilder smoothing, and **nothing anywhere recorded the choice*** |

---

# 3. RESOLVED — kept, per DF-3

| ID | Where | What | Resolved |
|---|---|---|---|
| **D-4** | `FMPProvider._cumulative_fys` | mis-detected discrete quarters as cumulative-YTD for MU/SNDK, **understating TTM revenue by 41.5 %** | 2026-08-02 — the partial-FY guess deleted; detection is evidence-only |
| **D-9** | root cause behind D-4 | the heuristic was **an artifact of a missing companyfacts TTL**, not real FMP behaviour | 2026-08-01 — `EdgarClient.COMPANYFACTS_TTL_HOURS` |
| **D-8** | `FundamentalTrainer._run_etl` | **no validator on the raw ingest** | 2026-08-05 — `FundamentalIngestValidator` between fetch and write |
| **D-10** | `SleeveSelector` ↔ Phase 3b | **backtest-fitted blend coefficients leaked into production** | 2026-08-05 — `persist`/`audit_dir` |
| **D-13** | `refresh_policy` ↔ `SynthesisReportWriter` | UPDATE mode was **a label with no implementation** | 2026-08-05 |
| **D-14** | `pipeline/**` docstrings | **eight mentions of a superseded deep-tier model** in production code | 2026-08-05 |
| **D-15** | `SynthesisReportWriter.generate` | ★★ **a degraded narrative was cached and rendered as though it were real** — the incident **BS-34**, **DC-3** and D-01 **RA-130** all exist to prevent | 2026-08-05 — `_finish` refuses to persist a degraded bundle |
| **D-17** | `main_inference._build_inference_features` | **INV-4 implemented as a filter that silently accepts a subset** | 2026-08-10 — workers score with the models' recorded feature names |
| **D-18** | `SleeveSelector._run_backtest_worker` | **the sleeve blend weights had never once been fitted** | 2026-08-10 |
| **D-12** | `report/slate.py` | failed loud on a missing ticker column and **silent on a missing score column** | 2026-08-05 |
| **D-5** | `discipline/context.py` | Layer D omitted entirely for unheld tickers | 2026-08-05 |
| **D-11** | `report/daily_brief.py:183` | **the Haiku invalidation check never ran** | 2026-08-05 |
| **D-6** | `main_pipeline.main()` | Phase 1 read the parquet Phase 2 writes — **the gate graded nothing on run #1** | 2026-08-02 |
| **D-7** | F0 §12 D-6 as first written | the claimed residual **was false**; the gate simply had no test | 2026-08-02 |
| **D-1** | `F1/spec.md` | named the pre-amendment deep-tier model | 2026-08-02 |
| **D-2 · D-3** | F1 §7/§8 | 🟡 open *questions*, not drift — and **F1 is deleted**, so they lapse with it |

---

# 4. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L3-build-sequence.md` | **BS-18** — the rule that required this document |
| `sdd/design/rel6_design/L0-system-vision.md` §17.5a · **G-7** | the F-tier deletion, and the rule it departed from |
| `sdd/design/rel6_design/L1-reporting.md` **RP-5** | how an open defect reaches the artifact that uses it |
| `sdd/blueprints/D-09-reporting.md` | `KNOWN_DEFECTS` — where D-19 and D-16 are carried in code |

---

# 5. ★ Carried-forward contracts — the load-bearing half of G-7

⚠ **Four of the 29 dangling citations were not prior art.** They were live
definitional dependencies: code in `src/` already built against a contract that
existed only in a deleted file. ★ **`CT-3.2` is the sharpest** — D-07 §6A.4's
FMP reality probe, built at B2 and run by `pytest -m live`, rests on it.

## CT-3.2 — the reality-probe record *(from F3 §4b, verbatim)*

★ **Tier 1 of F3's three-tier test model.** *Run the money path against external
truth from outside this repository.* When it was applied to the legacy tree it
**found ~6 of the 13 bugs.**

A probe MUST record:

| Field | Requirement |
|---|---|
| **entry point** | the module and entry point exercised |
| **ground truth** | the **external** truth used — filing URL/accession, broker statement, hand calculation |
| **every intermediate** | ★ *not only the final output* — ⚠ **FMP's TTM was wrong while the DCF still produced a plausible number** |
| **the verdict** | and if the two disagreed, **which was wrong and how that was established** |

> ★ **The third row is the one that earns its keep.** A probe that compares only
> the final number passes whenever two errors cancel, and this project has
> already seen a wrong TTM produce a plausible fair value.

**Where it is honoured:** `sdd/design/rel6_design/L1-data-engine.md` §6A.4
(K-1…K-5), `tests_src/test_data_engine_probe.py`.

## The three test tiers *(from F3 §4)*

| Tier | What it is | ⚠ What it must not claim |
|---|---|---|
| **1 — Reality probe** | run the money path against **external** truth | — |
| **2 — Characterization** | freeze behaviour you depend on but cannot verify | ★ *"this has not changed"*, **never** *"this is correct"* — **the distinction is the whole point** (constitution §5.2) |
| **3 — Spec-on-touch** | write the spec when you are about to change the code | ⚠ **Never write a spec for code you do not intend to modify** |

## CT-3.3 — the `ownership.yaml` rule *(from F3 §4b)*

A spec that governs code MUST appear in `sdd/specs/ownership.yaml` **in the same
change as the spec.** ⚠ *A spec with no globs is unenforced: the `PreToolUse`
gate falls back to `always` (constitution only), which is weaker than intended.*
★ This is **ST-8's other half**, and the file documents it in its own header.

---

# 6. ★ Tombstones — the six retired F-specs

★ **All six are recoverable from one commit:** `e0537860d6c1^`
(*"Delete sdd specs file since before rel6 new pipeline design"*, 2026-08-20).
⚠ **Recoverability is not migration** — G-7 requires the content to land in a
live spec, and a citation that resolves only through `git show` is a citation a
reader cannot follow.

| Spec | Governed | Retired | Content carried to |
|---|---|---|---|
| **F0** `code_map` | the as-is map of `pipeline/**`, incl. the **D-nn defect log** | 2026-08-20 | ★ **§2/§3 of this document** — the two OPEN defects and all resolutions |
| **F1** `disciplinary_report` | the daily card — Layers A–C, `CT-1.1`, `AC-1.15` | 2026-08-20 | **prior art only.** The behaviour is re-specified in `L1-reporting.md` §8 and `L1-fundamental-analysis.md`; ⚠ its `AC-1.n` family is the **live ID collision** those specs warn about |
| **F2** `portfolio_and_delivery` | `discipline/{risk,flags,context}.py`, delivery, `CT-2.3` | 2026-08-20 | **prior art only** — re-specified in `L1-risk-management.md` (8/8 ACs were green) and `L1-reporting.md` §9 |
| **F3** `sdd_adoption` | the SDD process itself — the three tiers, `CT-3.1/3.2/3.3` | 2026-08-20 | ★ **§5 of this document.** ⚠ **This is the one with a live dependency**, not merely prior art |
| **F4** `data_plane` | ⚠ **BMO InvestorLine** export → `portfolio_state` → `book_state`; currency-per-leg, `fx_rate_used`. *(Corrected 2026-08-25: this row said "CIBC export" — the exact drift **RC-36** and §5.3 **H-0** exist to stop. **The broker is BMO InvestorLine**; "CIBC" is the CDR issuer and belongs to the INSTRUMENT, never to the account.)* | 2026-08-20 | **prior art only** — re-specified as `L1-recording.md` **CT-11.4** and built at B5 (`src/recording/book/`) |
| **F9** `universe_and_fundamental_sources` | source routing, 6-K cumulative evidence, coverage | 2026-08-20 | **prior art only** — re-specified in `L1-data-engine.md` §5A and `L1-feature-engineering.md` §6.3 |

| ID | Rule |
|---|---|
| **DF-4** | ★ **A citation to a retired spec must say on its own line that the target is deleted.** ⚠ *A citation that looks live and resolves to nothing is worse than no citation* — the reader cannot tell a missing file from a moved one, and `tools/sdd_audit.py::check_spec_pointers` treats an unmarked one as a failure for exactly that reason |
