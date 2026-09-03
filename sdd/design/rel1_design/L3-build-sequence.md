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
| ⊘ ~~`PG-1`~~ | ~~No platform code until a verified E2E run~~ — **RETIRED 2026-09-02.** ⚠ **`MS-0` no longer blocks `MS-1`**; they run in parallel. `MS-0`'s items are still needed, but as *work*, not as a *gate* |
| **`PG-4`** | The evaluation harness is built **once, early, shared** — so it precedes both portfolio lanes, not one of them |
| **`PG-5.1`** | A capability graduates on its **Tier-A** measurement design → `F7a` precedes `F6b` |
| ★ **`PG-5.2` · `PG-9`** | Counterfactual arm, propensity, state-seen, decision id — **logged from the first run of any capability**. Near-free now, unrecoverable later → the trace (`MS-3`) precedes anything that alters an output |
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
| **MS-0** | ⬆ **Close the loop** *(upstream)* | all | — | — | 🟡 **in progress — the critical path** |
| **MS-1** | Platform substrate, standalone | D-00 | `F1` 🟡 | ★ **`F1` approved 🟢** | ⬜ — ★ **unblocked 2026-09-02**; awaits spec approval only |
| **MS-2** | ★★ **The link** — first import from the pipeline | D-00 | — | MS-1 | ⬜ |
| **MS-3** | Observability | 7 | `F2` 🟡 | MS-2 | ⬜ — ★ **spec drafted 2026-09-01** |
| **MS-4** | Evaluation harness | 9 | `F5` 🟡 | MS-3 | ⬜ — ★ **spec drafted** |
| **MS-5** | Explainability | 6 + 2/3/4/5 | `F4` 🟡 | MS-4 | ⬜ — ★ **spec drafted** |
| **MS-6** | The earned agent + control surface | 8 · 7 · 2 | `F3` 🟡 `F8` `F9` `F6a` | MS-4 | ⬜ — ★ **`F3` drafted** |
| **MS-7** | Deliberation, measured | 7 · 9 | `F7a` 🟡 → `F6b` 🟡 → `F7b` 🟡 | MS-6 | ⬜ — ★ **all drafted** |
| **MS-8** | ★★ **Absorption** — copy in, retire the old repo | all | — | MS-0 + MS-6 | ⬜ |
| **MS-9** | Write-up, mirror, polish | — | — | MS-8 | ⬜ |

⚠ **`MS-7` is the first thing cut if `MS-0` or `MS-3`–`MS-4` overrun.** Said now, while it is cheap to say.

## 2.1 Current position

```text
   ┌─ PHASE 0 · SPEC WORK ─────────────── substantially COMPLETE ──┐
   │  vision · constitution (PG-2..9) · questions register         │
   │  build plan · target structure · LICENCE · lectures           │
   └───────────────────────────────────────────────────────────────┘
                              │
                              ▼
   ┌─ MS-0 · UPSTREAM ─────────────────────── IN PROGRESS ─────────┐
   │  ◐ 0.1 run completes SUCCESS · verification is MANUAL now     │
   │  ⚠ 0.2 QR-5 + QR-19         decided, NOT IMPLEMENTED          │
   │    0.3 QA-4 / MDE wording   not started                       │
   │    0.4 AB-3 CAD·CDR         not started                       │
   │    0.5 L0 §5.1 seat numbers not started                       │
   └───────────────────────────────────────────────────────────────┘
                              │  ★ NO GATE — MS-0 and MS-1 are PARALLEL
                              ▼
   ┌─ MS-1..MS-9 · THIS REPO ──────────── NO CODE, SPECS DRAFTED ──┐
   │  no src/ · no tests/                                          │
   │  ★ 11 specs 🟡 DRAFT · 137 ACs · 9 governed globs · gate LIVE │
   │  ⚠ none APPROVED — review sequence in §2.3                    │
   └───────────────────────────────────────────────────────────────┘
```

**What is done, and it is not nothing:** every question that blocked design is answered
([`../../questions.md`](../../questions.md) — 18 decided, 1 open, 2 withdrawn/superseded), the seat model and
capability set are fixed, and the absorption path is designed.

⚠ **What is NOT done: nothing is APPROVED.** All 11 specs are 🟡 draft, so no acceptance criterion
yet binds an implementer — and ~45 open questions inside them remain unanswered. **`§2.3` is the order
to fix that in.**

## 2.2 ★ The next deliverable

★ **`PG-1` is retired, so approval is now PER-SPEC, not corpus-wide.** `MS-1` needs exactly one
thing: **`F1` at 🟢**. Nothing else in the corpus gates it.

⚠ **That changes what "next" means.** Reviewing all eleven specs before writing any code was `PG-1`'s
logic, and `PG-1` is gone. `S4`–`S7` cover work that is months away and whose open questions will move
before it starts; reviewing them now spends attention early for value late.

| | Work | Where | Status |
|---|---|---|---|
| ✅ *2026-09-02* | ~~G1–G3 governance review~~ — 7 issues found, all resolved | this repo | done |
| ★★ **Next** | **`S1` — review `F1` + `F2`, answer `F1`'s `Q1` and `Q4`, approve `F1` 🟢** | this repo | ✅ unblocked |
| ★ **Then** | **Build `MS-1`** against the approved `F1`. ⚠ Do **not** wait for `S2`–`S7` | this repo | after `F1` 🟢 |
| ⇄ **In parallel** | Manual verification of run outcomes (`MS-0.1`) — the fund manager's own task | ⬆ pipeline | ongoing |
| ⇄ **In parallel** | `MS-0.2` — the `QR-5`/`QR-19` gate change. ⚠ Still governs every **performance claim** (`PG-10`) | ⬆ pipeline | not started |

### Why `S1` and not the whole corpus

| | |
|---|---|
| **It is the critical path** | `F1` 🟢 is the only thing between here and the first line of code |
| ★★ **It carries the irreversible content** | `PG-5.2`'s pre/post arms and `PG-9`'s propensity live in `F2`. Everything else can be retrofitted; **unlogged history cannot** |
| **It has the widest blast radius** | `CT-1.4` and `CT-2.4` are cited by 8 specs — a change here moves them all |
| ⚠ **It carries two live decisions** | `F1` `Q1` (what is a "run scope"?) and `Q4` (does `AgentPort` satisfy `A4` on day one, or does the AC move?) |

★ **Review the rest just-in-time** — `S2` before `MS-4`, `S5` before `MS-6`, and so on. A spec reviewed
months before it is built is reviewed twice.

## 2.3 ★ Review sequence — governance first, then specs

> **Nothing is approved.** All 11 specs are 🟡 draft and the governing documents have never been
> reviewed. This is the order to read them in and which to read **together**, derived from measured
> citation counts rather than guessed.
> **Review status:** ⬜ not started · 🟡 in review · 🔁 changes requested · ✅ approved

### Why this order — measured 2026-09-02

```text
   GOVERNANCE                                   cited by
     constitution.md   PG-2..PG-9 ………………………  114 citations
                       PG-5.1 · PG-5.2 ………  5 specs each
                       114 PG citations total
     questions.md      53 QR citations  (QR-16 ×10, QR-13 ×6, QR-3 ×6)
   SPECS
     F2 ←── 5 specs   ★ root      F1 ←── 3      F5 ←── 3
     F9 ←── F8, FOUR times        ★ tightest pair in the corpus

   ✅ 35 CT-* contracts defined, ZERO dangling references.
```

★★ **The constitution is cited 114 times — more than any spec is cited by anything.** A change to a
`PG` rule in review reschedules or reshapes all 11 specs. **It must be settled before a single spec is
read.**

### The sequence

| # | Review | Files | Size | ★ What to look for | Review status |
|---|---|---|---|---|---|
| **G1** | ★★ **The authority** | `specs/vision.md` + `specs/constitution.md` | 587 ln | ⚠ **Read together and first — everything below depends on them.** *Vision:* is this what you are building? The nine seats, `C1`–`C9`, and `PG-2`'s ordering of the two purposes. *Constitution:* **`PG-1` is cited by all 11 specs** — if the phase gate moves, the whole plan reschedules. `PG-5.1`/`PG-5.2` bind 5 specs each | ✅ **approved 2026-09-02** |
| **G2** | ★ **The reasoning** | `questions.md` (20 QRs) + `design/rel1_brainstorm.md` **decisions log only** | 812 ln + 97 ln | ★ **The one question that matters: does each entry record what you *actually* decided, and are the rejected options stated fairly?** ⚠ Check the three corrections especially — `QR-5` (rewritten after reading the upstream method registry), `QR-7` (my Layer-4 name-collision error), `QR-17` (withdrawn, then reframed). ⚠ **Skip the brainstorm's first 618 lines** — Session 1 evaluation of a since-deleted `prompt.md`, kept as history, binding nothing | ✅ **approved 2026-09-02** |
| **G3** | **The tree** | `design/rel1_design/L4-target-structure.md` | 213 ln | Does absorption stay a **merge, not a restructuring** (`PG-8`)? Every `ownership.yaml` glob derives from this layout, so a wrong path here is wrong in nine places | ✅ **approved 2026-09-02** |
| **S1** | ★★ **The foundation** | `F1` + `F2` | 24 ACs | ⚠ **Highest cost of being wrong.** `CT-1.4` and `CT-2.4` are cited by 8 specs. `PG-5.2`/`PG-9`'s fields are the **only irreversible items in the plan** — unlogged history cannot be reconstructed. Also `F2` `Q3`: does the replay wording overclaim? | ⬜ |
| **S2** | **The measurement substrate** | `F5` | 14 ACs | Does `MetricResult` carry everything its consumers need? `QR-13`'s metric-vs-study boundary (`Q1`). Is `AC-5.11`'s no-duplication rule actually enforceable? | ⬜ |
| **S3** | **The studies** | `F7a` + `F7b` | 21 ACs | ★ Read **immediately after `F5`** — `F7a` cites it 5 times. Does the `KillRule` analysis plan hold together? ⚠ **`F7b` `Q2` is the hardest problem in the corpus** — the pre-deliberation verdict was never acted on, so comparing arms reintroduces backtest assumptions | ⬜ |
| **S4** | **Interactive agents** | `F6a` + `F6b` | 23 ACs | These were **split from one feature** (`QR-9`) — check for a **gap or overlap**. Do `F6b`'s deployment bands (§2.1) line up with `F7a`'s four verdicts? | ⬜ |
| **S5** | **The human path** | `F8` + `F9` | 30 ACs | ★ **Tightest coupling in the corpus.** `QR-16`'s "full depth" is asserted from both sides (`AC-8.1`, `AC-9.7`) — **check they agree.** Largest session. Also the new directives design, and ⚠ `F8` `Q3` (auth), which must not slip past first deployment | ⬜ |
| **S6** | **The earned agent** | `F3` | 12 ACs | Self-contained leaf. The clearest `PG-3` case — is the classification-vs-detection boundary right? | ⬜ |
| **S7** | **Explainability** | `F4` | 13 ACs | Leaf, but ⚠ **`Q5` needs a `PG-2` decision**: wiring `AB-1` makes `CONFIDENCE_FLOOR` reachable, and names that previously scored become `INSUFFICIENT_DATA`. **That changes live output** | ⬜ |
| **H1** | Housekeeping | `CLAUDE.md` · `LICENSE` · the four tier `README`s | ~200 ln | Lowest stakes. ⚠ **One real item: `LICENSE` carries "Victor Truong" — inferred from the git user. A copyright notice needs your exact legal name** | ⬜ |

**Governance: ~1,700 lines. Specs: 137 ACs across 11 files.**

### ✅ G1–G3 closed 2026-09-02 — what the review found

Seven issues, all resolved. ⚠ **Three were substantive:**

| | Issue | Resolution |
|---|---|---|
| **1** | ★★ `PG-1` carried three disagreeing bars, its done-when was arguably already met, and **it blocked `F5` — the instrument that would answer its own rationale** | ⊘ **`PG-1` retired**; verification is now the fund manager's. ✅ **`PG-10`** adopted for the half that was never about blocking code |
| **2** | Seat 9 had authority "none" yet `F7a` gates `F6b` | Reworded — *its measurements **gate**, but never **decide*** |
| **3** | ⚠ Post-absorption glob ordering: `src/fundamental/**` would swallow `src/fundamental/source/**` and **F9 would never govern — silently** | `L4` §5.1 ordering rule + `MS-8.4a` assertion |

Four mechanical: dangling `F7` → `F7a`/`F7b` · retired `Q4`/`Q2` IDs → `QR-4`/`QR-2` · undefined
"Phase 0–4" vocabulary → `MS-n` · stale register tally.

⚠ **`AB-3` was decided in the same pass** — `QR-21`, scope out and declare coverage.

> ⚠ **Caveat on "approved".** G1's `constitution.md` changed **materially after** the read that
> approved it: §1 rebuilt with eleven previously-missing ID families, `M<n>`→`MS-n` renamed across
> 118 references, `PG-1` retired, `PG-10` added. ★ **A re-skim of `constitution.md` alone is worth
> the ten minutes** — the rest of G1–G3 is unchanged in substance.

### ⚠ Three things only visible when reading a pair together

Reading these one at a time will not surface them:

| Check | Spans | Why it hides |
|---|---|---|
| **Does "full depth" mean the same on both sides?** | `AC-8.1` ↔ `AC-9.7` | Each asserts it independently; only together does a mismatch show |
| **Did the `F6a`/`F6b` split leave a gap?** | `F6a` ↔ `F6b` | They were one feature. A behaviour could belong to neither |
| **Do `F6b`'s bands match `F7a`'s verdicts?** | `F6b` §2.1 ↔ `F7a` `CT-7a.2` | Four verdicts, four modes — an off-by-one silently changes what ships |

### ★ Decisions that should not wait for their review slot

- ⚠ **`F4` `Q5`** *(would otherwise be read last)* — the coverage floor firing is a `PG-2` change to
  **live output**.
- ⚠ **`F7b` `Q1`/`Q2`** — what an "outcome" *is*, and how an un-acted-on arm is compared. Determines
  what that study can **ever** conclude.
- ⚠ **`F7a` `Q1`** — δ and the bands. Cheap to answer, and **nothing in `S3` can be finalised without
  it** because pre-registration is void once data exists.

---

# 3. The milestones

## ⬆ MS-0 — Close the loop *(work in `ai-investment-pipeline`)*

⚠ **No longer a gate.** `PG-1` was retired 2026-09-02 — these items are still needed, and `0.2` still
governs every performance claim, but they **do not block `MS-1`**.

| # | Item | Note |
|---|---|---|
| 0.1 | ◐ **Runs already complete** — `SUCCESS`, 13/13 jobs, rendered report (2026-08-28). ★ **What remains is *verification*, now the fund manager's own task** | was the `PG-1` exit; now a manual review |
| 0.2 | ★ **Apply `QR-5` + `QR-19`** *(revised 2026-09-01)* — in `corrected_se`, replace the **null** variance `1/(n−1)` with the **realised** `sd(per-date IC)²`; ★ **keep `N_eff = T/h` untouched**. Report both SEs; gate on the realised; threshold `t > 2` with the selection count recorded | Touches `src/quant/gates/metric_gate.py`, `mde()`, §5.3b. ⚠ **Both in the same change** — moving the denominator alone silently tightens the bar 3.49× |
| 0.3 | Clarify QA-4's wording and the MDE-as-acceptance conflation | ⚠ **Narrowed 2026-09-01:** the `T/h` divisor **is** the autocorrelation correction, so AB-12's *"no correction at all"* is overstated. QA-4 needs clarifying, not the formula fixing |
| 0.4 | ✅ **`AB-3` decided — `QR-21`: scope out.** Exclude unpriceable CAD/CDR positions from exposure, **declare the coverage on the card**, keep it actionable | ⬆ Upstream amendment to `DN-39`/`RC-58`. ⚠ Needs the excluded-fraction ceiling (`QR-21` `Q1`) |
| 0.5 | Correct upstream `L0` §5.1's stale seat numbers | Cheap; prevents the error propagating |

**Done when:** the fund manager has verified a run's outputs in depth, and 0.2 is merged upstream.

> ⚠ Expect the gate to start **refusing models it previously passed**. That is the mechanism working,
> and it will look like a regression on the first run that hits it.

## MS-1 — Platform substrate, standalone

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

## ★★ MS-2 — The link

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

> ★ **Why one shim and not many.** At `MS-8` the shim is deleted and the imports it wrapped become plain
> intra-repo imports. **One file to delete** is the whole design. Reaching into the pipeline from
> twenty call sites turns absorption into a refactor.

## MS-3 — Observability

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

## MS-4 — Evaluation harness

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

## MS-5 — Explainability

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

## MS-6 — The earned agent and the control surface

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

## MS-7 — Deliberation, measured

⚠ **Strict order. `F7a` is a gate, not a follow-up** (`PG-5.1`).

| # | Item | Spec |
|---|---|---|
| 7.1 | ★★ **`F7a` design + pre-registered kill rule** — stated *before* the test runs | `F7a` |
| 7.2 | `F6b` — typed messages, turn budget, guaranteed termination, escalation as a first-class outcome | `F6b` |
| 7.3 | Run `F7a`: capitulation on false vs valid challenges, effect size, direction, order-dependence, information content, termination, cost | `F7a` |
| 7.4 | `F7b` accrues outcome data — **never gates** | `F7b` |

**Done when:** `F7a` has run and its result is published — ★ **including if the result is that
deliberation does not help**, which satisfies `PG-5` and is the stronger portfolio artifact.

## ★★ MS-8 — Absorption

**Entry:** `MS-0` complete (the pipeline is stable) **and** `MS-6` complete (the platform works against it).

| # | Item |
|---|---|
| 8.1 | `git status` clean in both repos; tag both |
| 8.2 | Copy `src/**`, `tests/**`, `tests_src/**`, `config/**`, `tools/**` — ★ **zero content changes**. A move commit changes no bytes |
| 8.3 | Copy the upstream `sdd/design/rel6_design/**` L-specs |
| 8.4 | Merge `ownership.yaml` — ⚠ **`ST-8`: every glob moves in the same commit as its code.** A stale glob matches nothing and the gate then **fails open, silently** |
| 8.4a | ★★ **Assert glob ordering** — for every pair where one glob is a prefix of another, the **more specific must come first** (`L4` §5.1). ⚠ Four platform paths sit inside inherited domains; if an inherited glob is written above them the wrong spec governs, the gate still fires, and **nothing looks broken** |
| 8.5 | ★ **Delete `src/shared/upstream.py`.** Its wrapped imports become plain intra-repo imports |
| 8.6 | Run the **whole** suite — 1,192 upstream tests plus the platform's |
| 8.7 | Reconcile ID families: upstream's `P/INV/AP/ST/CA/DR/DE/RA/QA/...` now live beside `PG/QR/F/M/DX` |
| 8.8 | Record every discrepancy in §6 **before fixing any of them** |
| 8.9 | Retire `ai-investment-pipeline` — archive read-only, do not delete |

**Done when:** the full suite is green in one repo and the shim is gone.

> ★★ **The test of whether `L4`'s structure was right:** absorption deletes one shim, moves ~294 files
> with zero content changes, and merges one YAML. **Anything more means `PG-8` was violated somewhere
> earlier** — and that is a finding about the plan, not about the merge.

## MS-9 — Write-up, mirror, polish

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
| 2 Fundamental Analyst | D-01 | MS-5 (`AB-2`) · MS-6 (`F9`) |
| 3 Quantitative Analyst | D-03 · D-04 | MS-0 (`QR-5`) · MS-5 (attribution) |
| 4 Risk Management | D-05 | MS-5 (attribution) |
| 5 Portfolio Strategy | D-06 | MS-5 (attribution) |
| 6 Decision Mediator | D-12 · **D-13** | MS-5 |
| 7 Orchestrator | D-08 | MS-3 · MS-6 · MS-7 |
| 8 Back Office | D-07 · D-02 · D-09 · D-11 | MS-6 |
| 9 Experiments | D-10 · **D-14** | MS-4 |
| — cross-cutting | D-00 | **MS-1** |

★ **D-00 first and seat 1 never** — the two ends of the same principle.

---

# 5. ★ The absorption rehearsal (MS-2.5)

**The problem:** absorption is at `MS-8`, but discrepancies discovered there are discovered *late* —
after months of platform code has been written against assumptions the merge may invalidate.

**The fix, and it is cheap:** at `MS-2`, dry-run the whole thing.

```text
   git checkout -b absorption-rehearsal
   copy the pipeline tree in
   run both test suites
   ── record every DX-n in §6 ──
   git branch -D absorption-rehearsal      ← throw it away
```

★ **The branch is discarded; the findings are kept.** You buy early discovery without early commitment,
and `MS-8` becomes a merge you have already performed once.

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

*(empty — opens at `MS-2`)*

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
| **E1** | ★★ **The initial effect vocabulary** for directives (`F8` `CT-8.5`) | `F8` · seat 7 | `MS-6` E2E validation | ✅ Victor, 2026-09-01: *"defined after codes written, during E2E validation."* ⚠ Until then `CT-8.5` is **empty and every directive is unmappable** — which is `AC-8.14` working, not a bug. **The unmappable log is what seeds the vocabulary** |
| **E2** | Confirm the interpreter's tier (cheap vs deep) — `F8` `Q7` | `F8` | `MS-6` E2E validation | Needs observed misinterpretation rate. The confirm step (`AC-8.15`) is what makes the cheap tier defensible |
| **E3** | ★ **Register `F7a`'s `KillRule`** — δ, bands, α, power ⇒ `min_n_per_arm` | `F7a` · seat 9 | ⚠ **before `T2` of the suite runs**, not after | Pre-registration is void if it post-dates the data (`AC-7a.4`). ★ The *plan* is specifiable now; only δ and the bands need Victor |
| **E4** | Exercise `AC-7a.11` — confirm an underpowered run returns `INSUFFICIENT`, never `DELETE` | `F7a` | `MS-7` validation | The failure-to-reject asymmetry is the easiest thing to get wrong in the whole study |
| **E5** | Confirm `AC-8.13` — a replayed run with an `ACTIVE` directive **does not invoke the interpreter** | `F8` | `MS-6` E2E validation | ★ This is what keeps `PG-9` intact once an LLM is in the input path |
| **E6** | Confirm `AC-8.16` — `raw_text` reaches no downstream prompt | `F8` | `MS-6` E2E validation | ⚠ The regression that would silently reintroduce unfalsifiable control |
| **E7** | `F2` `Q5` — is *all* randomness seeded? | `F2` | `MS-2` link step | Answerable only against the inherited code |
| **E8** | `F9` `Q1` — does the relay envelope carry source spans? | `F9` | `MS-6` | Determines whether `QR-16`'s "earn the confidence back" path is open |
| **E9** | `QR-20` — pull the actual API bill and revisit the default | `F9` | `MS-6` | Ten minutes; either validates the concern or removes it |

★ **E1, E3 and E5 are the three that change what the system *is*.** The rest are confirmations.

---

# 8. Risks

| Risk | Mitigation |
|---|---|
| ⚠ **`MS-0` slips** | ★ **No longer blocking** since `PG-1` was retired — `MS-1` proceeds in parallel. ⚠ But `0.2` (`QR-5`/`QR-19`) still gates every *performance claim* |
| **`MS-7` gets squeezed** | Already designated first-to-cut. ★ `MS-1`+`MS-3`+`MS-6` is a coherent, honest release on its own |
| ⚠ **`PG-5.2`/`PG-9` fields skipped under time pressure at `MS-3`** | ★★ **The one irreversible failure in this plan.** Everything else can be retrofitted; unlogged history cannot |
| **Absorption is worse than a merge** | The `MS-2.5` rehearsal converts this from a surprise into a schedule item |
| **The API bill makes `QR-20` moot either way** | 6.3 is ten minutes; do it early in `MS-6` |
| ⚠ **`QR-5` makes the gate refuse everything** | Expected. `QR-19` set `t > 2` precisely so the bar tightens 2.33× rather than 3.49×. If nothing passes for two quarters, revisit `QR-19` — **not** by loosening quietly |
