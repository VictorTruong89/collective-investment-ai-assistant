# L3 — Build sequence

> **SDD role: `design/` tier — NON-AUTHORITATIVE.** Order of work and its rationale.
> **Binds nothing** — what binds is [`../../specs/constitution.md`](../../specs/constitution.md) and
> the governing spec. ⚠ But §6's **discrepancy log is a live record**, not a plan, and must be kept
> current during absorption.
> **Status:** DRAFT · **Opened:** 2026-08-30 · **Source:** rel1 S1–S5, `vision.md` §5
> **Companion to:** [`L4-target-structure.md`](L4-target-structure.md) (the target tree) ·
> [`../../questions.md`](../../questions.md) (why each decision was made)
> **ID family:** `M<n>` milestones · `DX-<n>` absorption discrepancies

---

# 1. What governs the order

| Rule | Effect on sequencing |
|---|---|
| ★★ **`PG-1`** | **No platform code until the inherited pipeline completes a verified end-to-end run.** This is why `M0` exists and why it is upstream work |
| **`PG-4`** | The evaluation harness is built **once, early, shared** — so it precedes both portfolio lanes, not one of them |
| **`PG-5.1`** | A capability graduates on its **Tier-A** measurement design → `F7a` precedes `F6b` |
| ★ **`PG-5.2` · `PG-9`** | Counterfactual arm, propensity, state-seen, decision id — **logged from the first run of any capability**. Near-free now, unrecoverable later → the trace (`M3`) precedes anything that alters an output |
| **`PG-8`** | The tree stays a superset → no module lands at a path that would need rewriting at absorption |
| **`QR-13`** | `src/evaluation/` is spec-governed → `F5` needs a spec before code |

★ **The through-line:** *instrument before capability.* Anything that changes an output is preceded by
the machinery that records what it changed.

---

# 2. ★ Progress — where the build actually is

> **This table is the progress tracker.** Update the Status column when a milestone's
> *"Done when"* is met — nowhere else records build state.
> **Statuses:** ⬜ not started · 🟡 in progress · ✅ done · 🚫 blocked

**Last reviewed: 2026-09-01.**

| # | Milestone | Seats | Specs | Gate to enter | **Status** |
|---|---|---|---|---|---|
| **M0** | ⬆ **Close the loop** *(upstream)* | all | — | — | 🟡 **in progress — the critical path** |
| **M1** | Platform substrate, standalone | D-00 | `F1` 🟡 | ★ `PG-1` satisfied | 🚫 blocked by M0 — ★ **spec drafted 2026-09-01** |
| **M2** | ★★ **The link** — first import from the pipeline | D-00 | — | M1 | ⬜ |
| **M3** | Observability | 7 | `F2` 🟡 | M2 | ⬜ — ★ **spec drafted 2026-09-01** |
| **M4** | Evaluation harness | 9 | `F5` 🟡 | M3 | ⬜ — ★ **spec drafted** |
| **M5** | Explainability | 6 + 2/3/4/5 | `F4` 🟡 | M4 | ⬜ — ★ **spec drafted** |
| **M6** | The earned agent + control surface | 8 · 7 · 2 | `F3` 🟡 `F8` `F9` `F6a` | M4 | ⬜ — ★ **`F3` drafted** |
| **M7** | Deliberation, measured | 7 · 9 | `F7a` 🟡 → `F6b` 🟡 → `F7b` 🟡 | M6 | ⬜ — ★ **all drafted** |
| **M8** | ★★ **Absorption** — copy in, retire the old repo | all | — | M0 + M6 | ⬜ |
| **M9** | Write-up, mirror, polish | — | — | M8 | ⬜ |

⚠ **`M7` is the first thing cut if `M0` or `M3`–`M4` overrun.** Said now, while it is cheap to say.

## 2.1 Current position

```text
   ┌─ PHASE 0 · SPEC WORK ─────────────── substantially COMPLETE ─┐
   │  vision · constitution (PG-1..9) · questions register        │
   │  build plan · target structure · LICENCE · lectures          │
   └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
   ┌─ M0 · UPSTREAM ───────────────────────── IN PROGRESS ────────┐
   │  ⚠ 0.1 verified E2E run     NOT DONE  ← the PG-1 gate        │
   │  ⚠ 0.2 QR-5 + QR-19         decided, NOT IMPLEMENTED         │
   │    0.3 QA-4 / MDE wording   not started                      │
   │    0.4 AB-3 CAD·CDR         not started                      │
   │    0.5 L0 §5.1 seat numbers not started                      │
   └──────────────────────────────────────────────────────────────┘
                              │  ⛔ PG-1 blocks everything below
                              ▼
   ┌─ M1..M9 · THIS REPO ────────────────── NOT STARTED ──────────┐
   │  no src/ · no tests/ · no F-spec graduated                   │
   │  ownership.yaml empty → nothing spec-governed yet            │
   └──────────────────────────────────────────────────────────────┘
```

**What is done, and it is not nothing:** every question that blocked design is answered
([`../../questions.md`](../../questions.md) — 17 decided, 2 withdrawn, 1 open), the seat model and
capability set are fixed, and the absorption path is designed.

⚠ **What is NOT done:** **no `F<n>` spec has graduated.** `sdd/specs/` holds `vision.md`,
`constitution.md`, an empty `ownership.yaml` and a template — nothing else. There is no acceptance
criterion anywhere in the repo, so there is nothing an implementer could be held to.

## 2.2 ★ The next deliverable

**`PG-1` blocks code. It does not block specs** (constitution §2, `PG-1`). So there are exactly two
live workstreams, and they are independent:

| | Work | Where | Blocked? |
|---|---|---|---|
| ✅ *done 2026-09-01* | ~~Write `F1`'s spec~~ — [`F1_module_registry/spec.md`](../../specs/F1_module_registry/spec.md), 12 ACs, globs wired, gate live | this repo | — |
| ✅ *done 2026-09-01* | ~~Draft the spec corpus~~ — **all 11 specs 🟡 draft, 137 ACs, 9 governed globs** | this repo | — |
| ★ **Next here** | **Review all 11 and approve 🟡→🟢.** ⚠ Two need decisions that cannot wait for code: `F4` `Q5` (wiring `AB-1` changes live output — `PG-2` sign-off) and `F7b` `Q1`/`Q2` (what an outcome *is*, and the counterfactual arm) | this repo | ✅ **not blocked** |
| ★★ **Critical path** | `M0` — the verified E2E run and the `QR-5`/`QR-19` gate change | ⬆ `ai-investment-pipeline` | — |

**Why `F1` and not another spec.** `M1` is the only platform milestone with **no pipeline
dependency** — a registry and a protocol can be built and fully contract-tested in isolation. Its
scope is already settled by `QR-7` (closed variant set, layers 1–4, no hot reload) and `QR-8`
(module-scoped, not agent-scoped), so its ACs are writable **today**.

★ Writing it now means that the moment `M0` lands, `M1` starts against a finished spec instead of a
blank page.

⚠ **Housekeeping, unrelated to either:** the repo has **23 files and zero commits.** Everything is
untracked. Nothing here is recoverable if the directory is lost.

---

# 3. The milestones

## ⬆ M0 — Close the loop *(work in `ai-investment-pipeline`)*

**Nothing in this repo starts until this is done** (`PG-1`).

| # | Item | Note |
|---|---|---|
| 0.1 | A full daily run completes **end to end on real data** and delivers its report, unattended | The `PG-1` exit condition |
| 0.2 | ★ **Apply `QR-5` + `QR-19`** *(revised 2026-09-01)* — in `corrected_se`, replace the **null** variance `1/(n−1)` with the **realised** `sd(per-date IC)²`; ★ **keep `N_eff = T/h` untouched**. Report both SEs; gate on the realised; threshold `t > 2` with the selection count recorded | Touches `src/quant/gates/metric_gate.py`, `mde()`, §5.3b. ⚠ **Both in the same change** — moving the denominator alone silently tightens the bar 3.49× |
| 0.3 | Clarify QA-4's wording and the MDE-as-acceptance conflation | ⚠ **Narrowed 2026-09-01:** the `T/h` divisor **is** the autocorrelation correction, so AB-12's *"no correction at all"* is overstated. QA-4 needs clarifying, not the formula fixing |
| 0.4 | Decide upstream `AB-3` (CAD/CDR pricing) or scope it out | ⚠ Currently the single thing keeping the daily card non-actionable |
| 0.5 | Correct upstream `L0` §5.1's stale seat numbers | Cheap; prevents the error propagating |

**Done when:** 0.1 passes and 0.2 is merged upstream.

> ⚠ Expect the gate to start **refusing models it previously passed**. That is the mechanism working,
> and it will look like a regression on the first run that hits it.

## M1 — Platform substrate, standalone

**No pipeline dependency.** This is why it is first — it is the only platform work that can be built
and fully tested in isolation.

| # | Item | Spec |
|---|---|---|
| 1.1 | Repo scaffolding: `pyproject.toml`, CI, `LICENSE`, ruff/pytest config | — |
| 1.2 | `src/shared/registry/` — `(port, variant) → factory`, versioning, `validate_coverage()` | `F1` |
| 1.3 | `src/shared/agents/ports.py` — `AgentPort` as **one registered port among several** (`QR-8`) | `F1` |
| 1.4 | ★ **Closed variant set** — every selectable variant registered at startup (`QR-7`) | `F1` |
| 1.5 | ★ **Instance caching per `(port, variant)` within a run** — or per-ticker selection reloads a model 500 times | `F1` |
| 1.6 | ★★ **One contract-test suite, parameterised over every registered variant** | `F1` |

**Done when:** two real implementations of one port both pass the same contract suite, and a missing
variant fails at **startup**, not at call time.

## ★★ M2 — The link

**This is the step where this repo first imports code from `ai-investment-pipeline`.**

| # | Item |
|---|---|
| 2.1 | ⚠ Confirm the **`src` package collision**: both repos root their packages at `src`, so a plain `pip install -e ../ai-investment-pipeline` will not work (`L4` §4) |
| 2.2 | ★ Build **one** shim — `src/shared/upstream.py`. Every reach into the pipeline goes through it |
| 2.3 | Pin the upstream revision. A moving dependency makes discrepancies unattributable |
| 2.4 | Smoke test: call one pipeline function from this repo, get real data back |
| 2.5 | ★★ **Absorption rehearsal** — see §5. Dry-run the copy into a scratch branch, record every `DX-n` it surfaces, then **throw the branch away** |
| 2.6 | ⚠ **Open the discrepancy log** (§6) |

**Done when:** 2.4 passes and 2.5's findings are recorded in §6.

> ★ **Why one shim and not many.** At `M8` the shim is deleted and the imports it wrapped become plain
> intra-repo imports. **One file to delete** is the whole design. Reaching into the pipeline from
> twenty call sites turns absorption into a refactor.

## M3 — Observability

Everything after this alters an output, so the recorder comes first.

| # | Item | Spec |
|---|---|---|
| 3.1 | `src/orchestration/trace/` — `TraceRecord`, `AgentTurn`, `GraphSnapshot` | `F2` |
| 3.2 | ★★ **`PG-5.2` fields designed in from record #1** — the pre-capability value beside the post | `F2` |
| 3.3 | ★★ **`PG-9` fields** — state the policy saw, action taken, **propensity** (`1.0` while deterministic), stable decision id linking to the realised outcome | `F2` |
| 3.4 | Replay: re-execute against **recorded** tool responses, not live ones | `F2` |
| 3.5 | Framework decision + ⚠ **CI grep** confining it to `src/orchestration/graph/` (`QR-14`) | `F2` |

**Done when:** a full pipeline run is traced, and replaying the trace reproduces it.

> ⚠ **3.2 and 3.3 are the ones that cannot be added later.** Everything else in this plan can be
> retrofitted; unlogged history cannot be reconstructed.

## M4 — Evaluation harness

`PG-4` — built once, shared by both lanes. Spec-governed per `QR-13`.

| # | Item | Spec |
|---|---|---|
| 4.1 | Write `F5`'s spec **first** — `QR-13` made this spec-governed precisely because a measurement instrument nobody verified is how you get confidently wrong numbers | `F5` |
| 4.2 | `src/evaluation/golden/` — known-correct fixtures | `F5` |
| 4.3 | `metrics/` — citation and grounding rate, calibration (reliability, ECE, Brier), faithfulness | `F5` |
| 4.4 | `regression/` — fails when a **prompt** changes behaviour | `F5` |
| 4.5 | ⚠ Draw the boundary flagged in `QR-13`: metric implementations spec'd; one-off studies `P7`-exempt | `F5` |

**Done when:** citation rate and a calibration curve compute over real pipeline output, and a
deliberate prompt change reds the regression suite.

## M5 — Explainability

| # | Item | Seat | Spec |
|---|---|---|---|
| 5.1 | **Attribution obligations** on each analytical domain's own output contract (`QR-10`) | 2·3·4·5 | `F4` |
| 5.2 | Monotonic constraints on the ranker — a config change, structural guarantee | 3 | `F4` |
| 5.3 | ★★ **Close upstream `AB-2`** — claim→span binding on the judgement narrative. Machinery is built, tested, exported and **never called** | 2 | `F4` |
| 5.4 | `src/explain/` — cross-view explanation, counterfactuals in **observables** | 6 | `F4` |
| 5.5 | SHAP + ALE + attribution-stability diagnostic | 3 | `F4` |
| 5.6 | EBM challenger under the same gates | 9 | — |

**Done when:** a recommendation carries per-domain attribution, every factual claim in its narrative is
bound to a verified span or marked unbound, and a counterfactual is stated in observable terms.

⚠ **`AB-1` trap:** once `evidence_coverage` becomes a real number the `CONFIDENCE_FLOOR` becomes
*reachable* and starts firing. **That is the mechanism working, not a regression.**

## M6 — The earned agent and the control surface

| # | Item | Seat | Spec |
|---|---|---|---|
| 6.1 | `src/data_engine/corporate_actions/` — the one agent that clearly earns its place under `PG-3` | 8 | `F3` |
| 6.2 | `ThesisSourcePort` with `ApiAdapter` (**default**, `QR-20`) and `RelayAdapter`, `provenance` on the output | 2 | `F9` |
| 6.3 | ★ **Pull the actual API bill** and revisit `QR-20` with a number | — | — |
| 6.4 | Human control surface — the API and its buttons | 7 | `F8` |
| 6.5 | ★ **Suspend / resume** — a run that pauses for external work and resumes: resume token, idempotency, expiry, stale-input guard | 7 | `F8` |
| 6.6 | ★ **`QR-16` — the full analysis path for any requested name**, same depth as the top-1; the manager designates which analysis is the day's actionable one; the designation is journaled | 8 · 11 | `F8` |
| 6.7 | `F6a` config-influence routing — pure function returning variant **+ reason + `influenced_by`** (`PG-7`) | 7 | `F6a` |

**Done when:** the manager can request any name and receive a full-depth analysis, and the request,
the rank it held, and any designation are recorded.

## M7 — Deliberation, measured

⚠ **Strict order. `F7a` is a gate, not a follow-up** (`PG-5.1`).

| # | Item | Spec |
|---|---|---|
| 7.1 | ★★ **`F7a` design + pre-registered kill rule** — stated *before* the test runs | `F7a` |
| 7.2 | `F6b` — typed messages, turn budget, guaranteed termination, escalation as a first-class outcome | `F6b` |
| 7.3 | Run `F7a`: capitulation on false vs valid challenges, effect size, direction, order-dependence, information content, termination, cost | `F7a` |
| 7.4 | `F7b` accrues outcome data — **never gates** | `F7b` |

**Done when:** `F7a` has run and its result is published — ★ **including if the result is that
deliberation does not help**, which satisfies `PG-5` and is the stronger portfolio artifact.

## ★★ M8 — Absorption

**Entry:** `M0` complete (the pipeline is stable) **and** `M6` complete (the platform works against it).

| # | Item |
|---|---|
| 8.1 | `git status` clean in both repos; tag both |
| 8.2 | Copy `src/**`, `tests/**`, `tests_src/**`, `config/**`, `tools/**` — ★ **zero content changes**. A move commit changes no bytes |
| 8.3 | Copy the upstream `sdd/design/rel6_design/**` L-specs |
| 8.4 | Merge `ownership.yaml` — ⚠ **`ST-8`: every glob moves in the same commit as its code.** A stale glob matches nothing and the gate then **fails open, silently** |
| 8.5 | ★ **Delete `src/shared/upstream.py`.** Its wrapped imports become plain intra-repo imports |
| 8.6 | Run the **whole** suite — 1,192 upstream tests plus the platform's |
| 8.7 | Reconcile ID families: upstream's `P/INV/AP/ST/CA/DR/DE/RA/QA/...` now live beside `PG/QR/F/M/DX` |
| 8.8 | Record every discrepancy in §6 **before fixing any of them** |
| 8.9 | Retire `ai-investment-pipeline` — archive read-only, do not delete |

**Done when:** the full suite is green in one repo and the shim is gone.

> ★★ **The test of whether `L4`'s structure was right:** absorption deletes one shim, moves ~294 files
> with zero content changes, and merges one YAML. **Anything more means `PG-8` was violated somewhere
> earlier** — and that is a finding about the plan, not about the merge.

## M9 — Write-up, mirror, polish

| # | Item |
|---|---|
| 9.1 | The curated public mirror (`QR-12`) — platform only, synthetic fixtures, no history |
| 9.2 | `LICENSE` + README §Licence on the mirror |
| 9.3 | ⚠ Dependency-licence audit before first publish |
| 9.4 | The demo |
| 9.5 | ★ Architecture essay — *why* the decisions were made. The `questions.md` register is most of the raw material |

---

# 4. What each seat gets, and when

| Seat | Domain | First touched |
|---|---|---|
| 1 Fund PM & Trader | — *(no module, ever)* | — |
| 2 Fundamental Analyst | D-01 | M5 (`AB-2`) · M6 (`F9`) |
| 3 Quantitative Analyst | D-03 · D-04 | M0 (`QR-5`) · M5 (attribution) |
| 4 Risk Management | D-05 | M5 (attribution) |
| 5 Portfolio Strategy | D-06 | M5 (attribution) |
| 6 Decision Mediator | D-12 · **D-13** | M5 |
| 7 Orchestrator | D-08 | M3 · M6 · M7 |
| 8 Back Office | D-07 · D-02 · D-09 · D-11 | M6 |
| 9 Experiments | D-10 · **D-14** | M4 |
| — cross-cutting | D-00 | **M1** |

★ **D-00 first and seat 1 never** — the two ends of the same principle.

---

# 5. ★ The absorption rehearsal (M2.5)

**The problem:** absorption is at `M8`, but discrepancies discovered there are discovered *late* —
after months of platform code has been written against assumptions the merge may invalidate.

**The fix, and it is cheap:** at `M2`, dry-run the whole thing.

```text
   git checkout -b absorption-rehearsal
   copy the pipeline tree in
   run both test suites
   ── record every DX-n in §6 ──
   git branch -D absorption-rehearsal      ← throw it away
```

★ **The branch is discarded; the findings are kept.** You buy early discovery without early commitment,
and `M8` becomes a merge you have already performed once.

**What the rehearsal is looking for** — the classes most likely to bite:

| Class | What to check |
|---|---|
| **Package collision** | Two `src` roots. ⚠ The known one |
| **Path assumptions** | Hard-coded absolute paths, `Path(__file__).parents[n]` counts that shift |
| **Config** | Does `config/` merge, or do platform settings need their own namespace? (`QR-15`) |
| **Test collection** | Duplicate module basenames across `tests/` and the platform's tests |
| **`ownership.yaml`** | Glob overlaps; ⚠ any glob matching nothing (`ST-8` fails **open**) |
| **ID collisions** | A platform ID that duplicates a reserved upstream family |
| **Dependency versions** | Two pins that disagree |
| **Entry points** | Two `entrypoint.py`, two CLI surfaces |
| ★ **`__init__.py` exports** | Upstream `.gitignore` once excluded these and it was a real defect — confirm they survive the copy |

---

# 6. ⚠⚠ Discrepancy log — `DX-n`

> ★★ **THE RULE: record the discrepancy BEFORE attempting a solution.**
>
> A discrepancy found and fixed in one motion leaves no trace of what was wrong, why it was wrong, or
> what else might share the cause. Write the row first. Then solve it. **The row is not overhead — it
> is the only artifact that survives the fix.**

**Fields.** `DX-n` · date · milestone · what was **expected** · what was **found** · where · severity ·
status · resolution *(filled in later, never at the same time as the row)*.

**Severity.** ⛔ blocker — absorption cannot proceed · ⚠ material — affects a number or a contract ·
◐ cosmetic — naming, layout, docs.

| ID | Date | M | Expected | Found | Where | Sev | Status | Resolution |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

*(empty — opens at `M2`)*

> ⚠ **Do not delete a resolved row.** Strike the status, keep the finding. The shape of a discrepancy
> recurs; the fix does not.
>
> ★ **If a `DX` turns out to be a spec-versus-code disagreement rather than a merge artifact, it is not
> a discrepancy — it is a defect,** and it goes to the owning spec under the constitution's change
> process. Say which it is in the row.

---

# 7. ⏳ E2E validation checklist

> ★ **Things deliberately deferred to end-to-end validation** — decisions that cannot honestly be made
> before real behaviour exists, recorded here so they are not forgotten when it does.
> ⚠ **This is a live list.** An item leaves it only when its answer lands in a spec or the register.

| # | Deferred item | Owner | Decided during | Why it waits |
|---|---|---|---|---|
| **E1** | ★★ **The initial effect vocabulary** for directives (`F8` `CT-8.5`) | `F8` · seat 7 | `M6` E2E validation | ✅ Victor, 2026-09-01: *"defined after codes written, during E2E validation."* ⚠ Until then `CT-8.5` is **empty and every directive is unmappable** — which is `AC-8.14` working, not a bug. **The unmappable log is what seeds the vocabulary** |
| **E2** | Confirm the interpreter's tier (cheap vs deep) — `F8` `Q7` | `F8` | `M6` E2E validation | Needs observed misinterpretation rate. The confirm step (`AC-8.15`) is what makes the cheap tier defensible |
| **E3** | ★ **Register `F7a`'s `KillRule`** — δ, bands, α, power ⇒ `min_n_per_arm` | `F7a` · seat 9 | ⚠ **before `T2` of the suite runs**, not after | Pre-registration is void if it post-dates the data (`AC-7a.4`). ★ The *plan* is specifiable now; only δ and the bands need Victor |
| **E4** | Exercise `AC-7a.11` — confirm an underpowered run returns `INSUFFICIENT`, never `DELETE` | `F7a` | `M7` validation | The failure-to-reject asymmetry is the easiest thing to get wrong in the whole study |
| **E5** | Confirm `AC-8.13` — a replayed run with an `ACTIVE` directive **does not invoke the interpreter** | `F8` | `M6` E2E validation | ★ This is what keeps `PG-9` intact once an LLM is in the input path |
| **E6** | Confirm `AC-8.16` — `raw_text` reaches no downstream prompt | `F8` | `M6` E2E validation | ⚠ The regression that would silently reintroduce unfalsifiable control |
| **E7** | `F2` `Q5` — is *all* randomness seeded? | `F2` | `M2` link step | Answerable only against the inherited code |
| **E8** | `F9` `Q1` — does the relay envelope carry source spans? | `F9` | `M6` | Determines whether `QR-16`'s "earn the confidence back" path is open |
| **E9** | `QR-20` — pull the actual API bill and revisit the default | `F9` | `M6` | Ten minutes; either validates the concern or removes it |

★ **E1, E3 and E5 are the three that change what the system *is*.** The rest are confirmations.

---

# 8. Risks

| Risk | Mitigation |
|---|---|
| ⚠⚠ **`M0` slips** — everything is behind it | It is upstream work that was needed anyway. ★ Spec-writing continues throughout; `PG-1` blocks code, not thinking |
| **`M7` gets squeezed** | Already designated first-to-cut. ★ `M1`+`M3`+`M6` is a coherent, honest release on its own |
| ⚠ **`PG-5.2`/`PG-9` fields skipped under time pressure at `M3`** | ★★ **The one irreversible failure in this plan.** Everything else can be retrofitted; unlogged history cannot |
| **Absorption is worse than a merge** | The `M2.5` rehearsal converts this from a surprise into a schedule item |
| **The API bill makes `QR-20` moot either way** | 6.3 is ten minutes; do it early in `M6` |
| ⚠ **`QR-5` makes the gate refuse everything** | Expected. `QR-19` set `t > 2` precisely so the bar tightens 2.33× rather than 3.49×. If nothing passes for two quarters, revisit `QR-19` — **not** by loosening quietly |
