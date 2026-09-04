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
| **MS-1** | Platform substrate, standalone | D-00 | `F1` 🟢 | — | 🟨 **built 2026-09-03** — registry, ports package, contract harness; ⚠ `AgentPort` + real ports deferred |
| **MS-2** | ★★ **First absorption** — `src/shared/` moved here *(rescoped by `QR-22`)* | D-00 | — | MS-1 | 🟨 **`2.1` `2.1a` `2.2a` `2.6` ✅ 2026-09-04** — 1,500 lines + 112 tests + 2 specs absorbed, counts conserved; ⬜ `2.3` pin revision, `2.4` smoke test, `2.5` rehearsal |
| **MS-3** | Observability | 7 | `F2` 🟡 | MS-2 | ⬜ — ★ **spec drafted 2026-09-01** |
| **MS-4** | Evaluation harness | 9 | `F5` 🟡 | MS-3 | ⬜ — ★ **spec drafted** |
| **MS-5** | Explainability | 6 + 2/3/4/5 | `F4` 🟡 | MS-4 | ⬜ — ★ **spec drafted** |
| **MS-6** | The earned agent + control surface | 8 · 7 · 2 | `F3` 🟡 `F8` `F9` `F6a` | MS-4 | ⬜ — ★ **`F3` drafted** |
| **MS-7** | Deliberation, measured | 7 · 9 | `F7a` 🟡 → `F6b` 🟡 → `F7b` 🟡 | MS-6 | ⬜ — ★ **all drafted** |
| **MS-8** | **Absorption — the *remainder***, and retire the old repo ⚠ *(no longer the absorption event — `QR-22`)* | all | — | MS-0 + MS-6 | ⬜ |
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
| ✅ *2026-09-03* | ~~`S1` — review `F1` + `F2`~~; `Q1`–`Q3` → `D1`–`D3`; **`F1` approved 🟢** | this repo | done |
| ✅ *2026-09-03* | ~~**Build `MS-1`**~~ — registry + ports + contract harness. 31 tests, **16 mutations all caught**; spec amended `A1` from 5 build-found defects | this repo | done |
| ✅ *2026-09-04* | ~~`MS-2.1` — the `src` collision~~ → `DX-1` ✅ fixed, `DX-2` ✅ decided (`QR-22`) | both repos | done |
| ✅ *2026-09-04* | ~~**`MS-2.2a` — absorb `src/shared/`**~~ — 1,500 lines, 112 tests, 2 L2 specs, 2 globs. **1197 tests before, 1197 after.** Surfaced `DX-3` | this repo ⬅ ⬆ | done |
| ★★ **Next** | `MS-2.3`–`2.5` — pin the upstream revision, smoke test, absorption rehearsal | this repo | ✅ unblocked |
| ✅ *2026-09-04* | ~~`DX-3`'s open half~~ — upstream's `architecture.py` is **multi-root**; one rule set spans both trees, verified by cross-repo planted violations | ⬆ upstream | done |
| ◐ **Anytime** | `MS-1.1` leftovers — CI, ruff. Independent of everything above | this repo | ⬜ |
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

| # | Item | Spec | Status |
|---|---|---|---|
| 1.1 | Repo scaffolding: `pyproject.toml`, CI, `LICENSE`, ruff/pytest config | — | 🟨 `pyproject.toml` + pytest ✅ · `LICENSE` ✅ · ⬜ CI, ruff |
| 1.2 | `src/shared/registry/` — `(port, variant) → factory`, versioning, `validate_coverage()` | `F1` | ✅ 2026-09-03 |
| 1.3 | `src/shared/agents/ports.py` — `AgentPort` as **one registered port among several** (`QR-8`) | `F1` | ⬜ **deferred to `MS-4`** — see note |
| 1.4 | ★ **Closed variant set** — every selectable variant registered at startup (`QR-7`) | `F1` | ✅ `AC-1.5` |
| 1.5 | ★ **Instance caching per `(port, variant)` within a run** | `F1` | ✅ `AC-1.6` — *run scope* = one `Registry` instance (`F1` `D1`) |
| 1.6 | ★★ **One contract-test suite, parameterised over every registered variant** | `F1` | ✅ `tests/contracts/` |

**Built 2026-09-03 — `31 passed, 1 skipped`, all 15 ACs mutation-verified (16 mutations, all caught).**

✏ **Amended the same day (`F1` `A1`).** The build raised **five spec defects that the `S1` review did
not find** — a contradiction between `CT-1.3` and `CT-1.4`, an unmechanised term in `AC-1.12`, a
residual false positive in `AC-1.7`, a missing `ports()` method, and untested `CT-1.1` rules. ★ Reading
a spec checks whether it is *coherent*; implementing it checks whether it is *executable*. **Treat the
first implementation as part of the review** for every spec after this one.

⚠ **Two deliberate gaps, both named rather than quietly closed:**

- **`1.3` `AgentPort` deferred.** Victor's call. `CT-1.5` declares it, but its only real consumer is
  `F6b`, which is unapproved and gated on `F7a`. Building it now would put a port in the tree whose
  contract suite has nothing to parameterise over.
- ⚠ **`src/shared/ports/__all__` ships EMPTY.** `F1` §2 makes the semantics of any particular port an
  explicit **non-goal** — `PricePort`, `ThesisSourcePort` (`F9`) and the rest arrive with their own
  specs. Declaring them here would be writing behaviour no approved AC covers (constitution §5.1). The
  *mechanism* is complete and proven against fixture ports in `tests/contracts/`.

**Done when:** ⚠ **partially met.** Two implementations of one port do both pass the same contract
suite, and a missing variant does fail at **startup** rather than at call time — but both
implementations are **fixtures**, not real adapters. The clause closes at `MS-2`/`MS-3`, when the first
real port lands. ★ Stated rather than marked green, because a fixture passing a suite is evidence about
the *harness*, not about *substitutability*.

## ★★ MS-2 — The first absorption *(was: "The link")*

✏ **Rewritten 2026-09-04 by `QR-22`.** This milestone used to build a shim so the two trees could be
imported together. ⚠ **They cannot be** — see §6.1. `MS-2` is now the **first per-domain absorption**,
and `src/shared/` is the natural first because it is the only domain *already* split across both repos.

| # | Item | Status |
|---|---|---|
| 2.1 | ✅ **Confirm the `src` package collision** — measured, not reasoned: 3 sys.path configurations from a neutral cwd | ✅ `DX-1` |
| 2.1a | ✅ Root `src/__init__.py` deleted in **both** repos; upstream `pyproject.toml` → `[tool.setuptools.packages.find]`, `namespaces = true`. Upstream re-run: **1166 passed, 4 skipped — identical to baseline** | ✅ 2026-09-04 |
| 2.2 | ~~Build one shim, `src/shared/upstream.py`~~ — ⛔ **struck.** A shim presumes simultaneous import (`QR-22`) | ⊘ |
| 2.2a | ★ **Absorb `src/shared/`** — ✅ **done 2026-09-04.** Moved: 6 modules + `llm/` (1,500 lines), their **3 dedicated test files** (112 tests), and **2 L2 specs**. `ownership.yaml` globs landed in the same change (`ST-8`) | ✅ |
| 2.2b | ⚠ **Restore the fences the move silently disabled** (`DX-3`) — `SI-1` re-implemented here **and** upstream's `architecture.py` made multi-root | ✅ **2026-09-04** |
| 2.3 | Pin the upstream revision. A moving dependency makes discrepancies unattributable | ⬜ |
| 2.4 | Smoke test: call one absorbed function from this repo, get real data back — ★ now a **plain intra-repo import**, no shim | ⬜ |
| 2.5 | ★★ **Absorption rehearsal** — see §5. ⚠ **Now doubly worth doing**, because `MS-2` *is* an absorption and every lesson transfers directly | ⬜ |
| 2.6 | ✅ **Discrepancy log opened** (§6) — `DX-1` ✅, `DX-2` ✅ | ✅ |

**Done when:** `src/shared/` exists in exactly **one** repo, both suites are green, and `ownership.yaml`
says who governs the moved files.

### ✅ `MS-2.2a` — the first absorption, 2026-09-04

**Test counts are exactly conserved — that is the check that nothing was lost or double-counted:**

| | Before | After | Δ |
|---|---|---|---|
| this repo | 31 passed, 1 skipped | ✅ **150 passed, 1 skipped** | +119 *(112 absorbed + 7 new `DX-3` fence tests)* |
| ⬆ upstream (tf_gpu 3.10) | 1166 passed, 4 skipped | ✅ **1054 passed, 4 skipped** | −112 |
| **sum of the two** | **1197** | **1197** | ★ **0 — conserved** |

**What moved.** `config.py` `errors.py` `logging.py` `money.py` `secrets.py` `llm/` (~1,500 lines) ·
`tests_src/{test_money,test_gateway,test_shared_infra}.py` + `conftest.py` ·
`sdd/design/rel6_design/L2-shared-{infrastructure,money}.md` · 2 `ownership.yaml` entries.

⚠ **`tests_src/` was used here deliberately** — the same path upstream uses — so `MS-8` merges rather
than moves (`PG-8`). ★ And **`conftest.py` travelled with the tests**: it is an autouse guard that
redirects `PIPELINE_STATE` to a tmp dir, and upstream's own comment records that a test once became *"a
FULL LIVE DAILY RUN… 44 phantom records"* without it. **A safety net left behind is a safety net
removed.**

**Verified in both directions**, not just ours: upstream's `entrypoint` still imports, and
`src.shared.money` resolves *from this repo* through the namespace package.

⚠ **The upstream path is now load-bearing.** Upstream's `pytest.ini` carries
`pythonpath = . ../collective-investment-ai-assistant`, and this repo's `pyproject.toml` carries the
mirror. **Neither repo may regain a root `src/__init__.py`** (`DX-1`).

> ★★ **What this milestone actually taught.** The plan said absorption moves *code*. It moves **four
> things** — code, tests, `ownership.yaml` globs, and the architecture rules that scan the path — and
> `DX-3` is what the fourth looks like when you forget it: **upstream's `SI-1` went from policing a
> directory to scanning zero files, and reported `14 passed`.** ⚠ Nothing failed. The only reason it
> was caught is that a violation was **planted on purpose**. See §6.3 — that check is now mandatory
> before any future absorption is called done.

> ⚠⚠ **`ST-8` applies from this milestone onward, per domain.** Every glob moves in the *same* change as
> its code — a glob matching nothing makes the gate **fail open, silently**. This used to be an `MS-8`
> concern; per-domain absorption makes it a **recurring** one.

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

## ★★ MS-8 — Absorption *(the remainder)*

✏ **Rescoped 2026-09-04 by `QR-22`.** ⚠ **`MS-8` is no longer the absorption event** — it is whatever is
**left over**. The domains this repo needs (`shared`, `orchestration`, `data_engine`, `fundamental`) are
absorbed earlier and individually, each with its own test run. ★ That converts the plan's largest
single-step risk into instalments that fail small.

**Entry:** `MS-0` complete (the pipeline is stable) **and** `MS-6` complete (the platform works against it).

| # | Item |
|---|---|
| 8.1 | `git status` clean in both repos; tag both |
| 8.1a | ⚠⚠ **Verify `.gitignore` covers the incoming tree BEFORE copying.** ★ Especially `sdd/design/rel6_design/samples/bmo_investorline_transactions/` — **real BMO broker transaction CSVs.** Also `.state/` `data/` `logs/` `trained_models/` `reports/*` `*.pkl` `*.joblib` `*.model`. **`git rm --cached` after the fact does not remove anything from history** |
| 8.2 | Copy `src/**`, `tests/**`, `tests_src/**`, `config/**`, `tools/**` — ★ **zero content changes**. A move commit changes no bytes |
| 8.3 | Copy the upstream `sdd/design/rel6_design/**` L-specs |
| 8.4 | Merge `ownership.yaml` — ⚠ **`ST-8`: every glob moves in the same commit as its code.** A stale glob matches nothing and the gate then **fails open, silently** |
| 8.4a | ★★ **Assert glob ordering** — for every pair where one glob is a prefix of another, the **more specific must come first** (`L4` §5.1). ⚠ Four platform paths sit inside inherited domains; if an inherited glob is written above them the wrong spec governs, the gate still fires, and **nothing looks broken** |
| 8.5 | ~~Delete `src/shared/upstream.py`~~ — ⊘ **no shim was ever built** (`QR-22`). Instead: ⚠ **verify no domain remains split across both repos** |
| 8.6 | Run the **whole** suite — 1,192 upstream tests plus the platform's |
| 8.7 | Reconcile ID families: upstream's `P/INV/AP/ST/CA/DR/DE/RA/QA/...` now live beside `PG/QR/F/M/DX` |
| 8.8 | Record every discrepancy in §6 **before fixing any of them** |
| 8.9 | Retire `ai-investment-pipeline` — archive read-only, do not delete |

**Done when:** the full suite is green in one repo and the shim is gone.

> ★★ **The test of whether `L4`'s structure was right** *(restated for per-domain absorption)*: **every**
> absorption — `MS-2`'s and this one — moves files with **zero content changes** and merges globs into
> `ownership.yaml`. **Anything more means `PG-8` was violated somewhere earlier** — a finding about the
> plan, not about the merge. ★ And now it is tested repeatedly instead of once, at the end.

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
| **DX-1** | 2026-09-03 | MS-2 | `L4` §4 option B — *"keep the upstream repo importable under its own distribution name"* — lets this repo reach `src.quant…` through one shim | ⛔ **Option B cannot work as written.** The clash is on the **import** name, not the distribution name. Both repos root at `src` **and both ship `src/__init__.py`**, making `src` a *regular* package in each. ⚠ **A regular package found anywhere on `sys.path` ends the scan** — so whichever root is found first wins outright and the other's domains are simply invisible. Installing upstream under any distribution name changes nothing | `src/__init__.py` (both repos) · `L4` §4 option B · upstream `pyproject.toml` `packages = ["src"]` | ⛔ blocker | ✅ **resolved 2026-09-04** | **Root `src/__init__.py` deleted in BOTH repos; upstream `pyproject.toml` switched to `[tool.setuptools.packages.find]` with `namespaces = true`** (authorised by Victor). Verified: upstream **1166 passed, 4 skipped — identical to baseline**; this repo 31 passed. ⚠ Resolves the ROOT level only — see `DX-2` |
| **DX-2** | 2026-09-04 | MS-3 | With `DX-1` fixed, this repo can add a subpackage under any upstream domain and import both trees at once | ⛔ **The same rule bites again one level down, and there it cannot be fixed the same way.** `src/shared/` exists in BOTH repos as a *regular* package, so `src.shared` resolves to one repo and the other's modules are invisible. Deleting both `src/shared/__init__.py` **does** work — measured, both trees import simultaneously — ⚠ **but it breaks upstream's `tests_src/test_architecture.py::test_every_domain_directory_is_a_package`**, which enforces upstream `L4` §1.1 | `src/shared/` (both repos) · upstream `L4` §1.1 · `tests_src/test_architecture.py` | ⛔ blocker | ✅ **decided 2026-09-04** | **Option B — absorb per-domain, early; the two trees never coexist for any domain** (`QR-22`). ⚠ Upstream `L4` §1.1 and its test are **left intact** — the chosen option needs no upstream rule change, which is why it beat option A |
| **DX-3** | 2026-09-04 | MS-2 | Absorbing a domain moves its code, its tests and the rules that police it | ⚠⚠ **The architecture fences that scanned the absorbed directory became silently VACUOUS.** Upstream's `SI-1` (*"`src/shared/` imports no `src/<domain>/`"*) uses `importer_prefixes=("src/shared/",)` against upstream's own tree — now **empty**. **Measured: SI-1 scans 0 files** (`ST-5` still scans 285, so it stayed meaningful for upstream *importers* but is blind to this repo's). ★ Caught by **planting a violation**: upstream still reported `14 passed` | upstream `tests_src/architecture.py` `SRC = REPO / "src"` · rules `SI-1`, `ST-5` | ⚠ material | ✅ **resolved 2026-09-04** | **Upstream's `tests_src/architecture.py` is now MULTI-ROOT** — `SRC_ROOTS` spans both trees, so **one rule set** governs both. `SI-1` went from **0 files scanned back to 14**; graph 285 → 299. ★ Proven by planting `SI-1` and `ST-5` violations *in this repo* and watching **upstream's** suite fail. Plus two new guards: `test_the_graph_is_not_vacuous` (fires if any domain prefix matches nothing) and a `scan()` **raise** if one domain appears in both trees (`QR-22`). This repo's `test_shared_fences.py` stays as defence in depth |

> **Measured 2026-09-03**, not inferred. Three configurations, from a neutral cwd:
>
> | Both roots have `__init__.py` | ours only | **neither** |
> |---|---|---|
> | ⛔ `src.quant` invisible | ⛔ `src.quant` invisible | ✅ `src.__path__` spans **both** trees; `src.shared` and `src.quant` both import |
>
> ★ **Deleting *our* `src/__init__.py` alone does nothing** — that is the counter-intuitive half, and the
> reason this row exists. The scan stops at the first *regular* package, so a single `__init__.py` left
> anywhere on the path re-breaks it silently, with a `ModuleNotFoundError` that names the submodule and
> gives no hint that a packaging decision two directories up caused it.
>
> ⚠ **The candidate fix needs an upstream change**, and `CLAUDE.md` is explicit that inherited code is
> changed *there*, not here — so it is Victor's call, not this repo's. Upstream's root `src/__init__.py`
> is **docstring-only**, and `L4` `ST-3`'s *"`__init__.py` is the domain's public API"* is about
> `src/<domain>/__init__.py`, **not** the root — so the blast radius looks small. ⚠ *Looks* small: it also
> touches upstream's `pyproject.toml`, which declares `packages = ["src"]` under setuptools.
>
> ★ **Why this is worth the trouble rather than a workaround:** if `src` becomes one namespace package
> spanning both trees, the absorption is *already rehearsed* — the two trees merge into one directory
> and **not a single import statement changes**, which is exactly the test `L4` §4 sets for itself
> (*"delete one shim, move ~294 files with zero content changes"*). A workaround that fakes the import
> path would pass `MS-2` and fail that test at `MS-8`.

> ⚠ **Do not delete a resolved row.** Strike the status, keep the finding. The shape of a discrepancy
> recurs; the fix does not.
>
> ★ **If a `DX` turns out to be a spec-versus-code disagreement rather than a merge artifact, it is not
> a discrepancy — it is a defect,** and it goes to the owning spec under the constitution's change
> process. Say which it is in the row.

---

## 6.1 ⚠⚠ `DX-2` in full — the collision is recursive, and it gets worse

**The rule, stated once:** *a **regular** package (one with `__init__.py`) found anywhere on `sys.path`
**ends the import scan***. Namespace portions from other roots are discarded. So **every directory that
both repos populate must be a namespace package**, all the way down — not just `src/`.

⚠ **`src/shared/` was the easy case.** Both `__init__.py` were docstring-only, so deleting them costs
nothing but two docstrings. **The next three are not.**

| Directory | Upstream `__init__.py` | Needed by | Verdict |
|---|---|---|---|
| `src/shared/` | **0** non-blank lines | `F1` — ★ *already built* | ◐ deletable, but see the test below |
| `src/orchestration/` | **74** lines, **11** re-export imports | `F2` `MS-3`, `F6a`, `F6b`, `F8` | ⛔ **not deletable** |
| `src/data_engine/` | **62** lines, **8** re-exports | `F3` | ⛔ **not deletable** |
| `src/fundamental/` | ⚠ **290** lines, **45** re-exports | `F9` | ⛔⛔ **not deletable** |
| `src/evaluation/`, `src/explain/` | *absent upstream* | `F5`, `F4` | ✅ no collision, ever |

⚠⚠ **Those `__init__.py` files ARE the public API** — upstream `L4` `ST-3` says so, upstream's own code
imports through them (`from src.orchestration.errors import …`), and upstream has **a test that enforces
it**. ★ **That test's docstring is the punchline:** it exists *"because the failure mode is confusing:
imports resolve via namespace packages until one does not, and the error names the wrong file."*
**Upstream already knew about this trap and wrote a guard against it** — and this plan walks into it.

### The options, none free

| | Option | Cost |
|---|---|---|
| **A** | **Amend upstream `L4` §1.1** to exempt directories that are namespace-by-design, and relax its test | ⚠ Weakens a rule upstream wrote *deliberately*, and the confusing failure mode it guards returns |
| **B** | **Absorb per-domain, early** — when this repo first needs `src/orchestration/`, absorb upstream's whole `src/orchestration/` then, instead of coexisting | ★ No shim for that domain, and `PG-8` is satisfied by construction. ⚠ Turns `MS-8` from one event into a sequence, and pulls absorption risk forward |
| **C** | **`pkgutil.extend_path`** in this repo's colliding `__init__.py` — a regular package that appends upstream's directory to its own `__path__` | ⚠ Our `__init__.py` runs and upstream's does **not**, so its 45 re-exports vanish. Would have to be re-created and kept in sync — a second copy of the API surface |
| **D** | **Process boundary** — reach upstream through its CLI (`orchestration/entrypoint.py::main`) and exchange artifacts, never importing it | ★ Sidesteps the collision entirely and matches upstream's actual shape (a CLI). ⚠ `F2` wants *step-level* trace from inside a run, which an artifact boundary does not give |
| **E** | **Keep this repo's new code out of upstream-named domains until `MS-8`** | ✗ Breaks `PG-8` — absorption becomes a restructuring, the exact thing `PG-8` exists to prevent |

★ **`F1`/`MS-1` is unaffected** — already built and green, and `src/shared/` is only a problem the day
something imports *both* repos' `shared`. Nothing does.

## 6.3 ⚠⚠ `DX-3` — absorption silently un-enforces the rules that policed the domain

★★ **This is the general hazard of per-domain absorption, and it will recur at every one.** It is
`ST-8`'s failure shape — *"a stale glob matches nothing and the gate fails open, silently"* — but for
**architecture tests** rather than ownership globs, so `ST-8`'s own wording does not cover it.

**What happened.** Upstream's `SI-1` scans `src/shared/**` in *upstream's* tree. Absorbing the domain
emptied that directory, so the rule examines **zero files** and passes unconditionally. Nothing failed,
nothing warned. ⚠ A green suite reported a rule satisfied when it was no longer being checked at all.

**How it was caught, and the lesson.** By **planting a violation** and observing that upstream still
reported `14 passed`. ★ *A rule that cannot fail is indistinguishable from a rule that passes — the only
way to tell them apart is to make it fail on purpose.* This is the same instrument that caught `AC-1.7`'s
vacuous contract suite during `MS-1` two days earlier, and it is now **twice** the thing that found a
defect nothing else did.

**What survived by luck, and what did not.** `money.py` carries its *own* per-module assertion
(`test_module_imports_nothing_from_another_domain`) which travelled with the code and **did** catch the
planted violation. `config.py`, `errors.py`, `logging.py`, `secrets.py` and `llm/` carry no such test —
for those, enforcement simply stopped. ⚠ **Do not read the surviving case as evidence the move was
safe;** it was one module's belt-and-braces, not a property of the process.

### ★★ The rule to apply at every future absorption

> **An absorption moves FOUR things, not one: the code, its tests, its `ownership.yaml` globs, and the
> architecture rules that scan its path.** Forgetting the fourth is invisible — the suite stays green.
> ⚠ **Before declaring an absorption done, plant a violation of each rule that used to cover the moved
> directory and confirm something still fails.**

### ✅ Closed 2026-09-04 — one rule set now spans both trees

`tests_src/architecture.py` (upstream) is **multi-root**. `SRC_ROOTS` = this repo's `src/` **plus** each
absorbed sibling's, discovered by name and overridable via `ARCHITECTURE_SRC_ROOTS`. ★ **One enforcement
point**, not two copies that would eventually disagree.

**The one non-obvious mechanic:** `scan()` used to key files by `path.relative_to(REPO)`, which *throws*
for a sibling's file. Keys now come from **each root's own parent**, so an absorbed file keys as
`src/shared/money.py` exactly as it did before the move — and **every existing prefix rule keeps working
unchanged**. No rule needed rewriting; that is the test of whether the abstraction was right.

| Verification | Result |
|---|---|
| `SI-1` files scanned | **0 → 14** ✅ |
| import graph | 285 → **299 files** |
| `SI-1` violation planted **in this repo** | ⬆ **upstream suite fails** ✅ |
| `ST-5` violation planted **in this repo** | ⬆ **upstream suite fails** ✅ |
| sibling root missing | `test_the_graph_is_not_vacuous` **fails** ✅ — cannot go silent again |
| one domain in **both** trees | `scan()` **raises** ✅ — enforces `QR-22`'s one-owner invariant |
| upstream suite | 1054 → **1056 passed, 4 skipped** (the 2 new guards) |

⚠ **`ARCHITECTURE_SRC_ROOTS` and the two `pythonpath` entries are now load-bearing.** A CI checkout that
does not place the repos as siblings must set it, or the rules narrow — and `test_the_graph_is_not_vacuous`
is what turns that from silent into loud.

## 6.2 ✅ Resolved — option B, and what it changes

**Decision `QR-22` (2026-09-04): absorb per-domain, early.** The full rationale and the four rejected
options live in [`questions.md`](../../questions.md) `QR-22` — ★ **read it before proposing a shim**,
because options A and D are attractive and were rejected for specific measured reasons.

**The rule, operationally:** *when this repo first needs to add code under a domain upstream owns, that
domain is absorbed **at that moment*** — upstream's directory moves here, its globs arrive in
`ownership.yaml` pointing at the upstream `L`-spec, and upstream stops being the source of truth for it.
⚠ **The two trees never both contain the same domain.** The collision only exists while both copies are
live, so the fix is to never have both.

| Domain | Owner today | Absorbed at |
|---|---|---|
| `src/shared/` | ⚠ **split** — `registry`, `ports` here; `config`, `errors`, `llm`, `money`, `secrets` upstream | `MS-2` — ★ **first, because it is the only one already split** |
| `src/orchestration/` | upstream | `MS-3` (`F2` needs it) |
| `src/data_engine/` | upstream | `MS-3`/`MS-5` (`F3`) |
| `src/fundamental/` | upstream | when `F9` is built — ⚠ **the 290-line one; do it last and alone** |
| `src/evaluation/`, `src/explain/` | ★ this repo, from scratch | never absorbed — no upstream counterpart |
| everything else | upstream | `MS-8`, as the remainder |

⚠ **`MS-8` is now the *remainder*, not the event.** It absorbs whatever is left; the risky domains are
absorbed earlier, individually, each with its own test run. ★ That is the argument *for* B rather than a
cost of it: `MS-8` was the largest single-step risk in the plan, and this converts it into instalments
that fail small.

⚠⚠ **The maintenance rule now has an exception that must stay legible.** `CLAUDE.md` and vision §2 say
inherited logic changes *upstream*. That remains true **only for domains not yet absorbed.** Once a
domain is here, it changes here. **`ownership.yaml` is the authority on which is which** — check it
before editing anything under `src/`, not memory.

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
