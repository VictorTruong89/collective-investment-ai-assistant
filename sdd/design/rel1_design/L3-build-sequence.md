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
| **MS-1** | Platform substrate, standalone | D-00 | `F1` 🟢 | — | ✅ **COMPLETE** — 15 ACs mutation-verified; CI + ruff done 2026-09-04; ⚠ `AgentPort` deferred by decision |
| **MS-2** | ★★ **Absorptions** — `src/shared/` **and** `src/orchestration/` moved here (`QR-22`, `QR-23`) | D-00 · 7 | — | MS-1 | ✅ **COMPLETE 2026-09-04** — 4,588 lines, 187 tests, 3 specs absorbed; all `DX` closed |
| **MS-3** | Observability | 7 | `F2` 🟢 | MS-2 ✅ | ✅ **COMPLETE 2026-09-04** — **16/16 ACs green**, mutation-verified. The real 13-job graph is traced and **replays `REPRODUCED`** |
| **MS-4** | Evaluation harness | 9 | `F5` 🟢 | MS-3 ✅ | ✅ **BUILT 2026-09-04** — **16/16 ACs green**, 21 mutations all caught. ⚠ Golden set **empty** — `D2` makes it Victor's work |
| **MS-5** | Explainability | 6 + 2/3/4/5 | `F4` 🟢 | MS-4 ✅ | ✅ **BUILT 2026-09-04** — 13/15 ACs green, 16 mutations caught. ⏸ `AC-4.4`/`AC-4.6` moved to **upstream R7** (`D1`) |
| **MS-6** | The earned agent + control surface | 8 · 7 · 2 | `F3` `F8` `F9` `F6a` **all 🟢** | MS-4 ✅ | ✅ **BUILT 2026-09-04** — 4 specs, 17 decisions, **74 new tests**, 22 mutations all caught |
| **MS-7** | Deliberation, measured | 7 · 9 | `F7a` → `F6b` → `F7b`, **all 🟢** | MS-6 ✅ | 🟨 **BUILT 2026-09-04** — kill rule, Tier-A battery, deliberation, Tier-B study. 14 mutations all caught. ⏳ **`F7a` has not RUN** — that needs a live `F6b` |
| **MS-8** | **Absorption — the *remainder***, and retire the old repo ⚠ *(no longer the absorption event — `QR-22`)* | all | — | MS-0 + MS-6 | ⬜ |
| **MS-9** | Write-up, mirror, polish | — | — | MS-8 | ⬜ |

⚠ **`MS-7` is the first thing cut if `MS-0` or `MS-3`–`MS-4` overrun.** Said now, while it is cheap to say.

## 2.1 Current position — updated 2026-09-04

```text
   ┌─ PHASE 0 · SPEC WORK ─────────────── substantially COMPLETE ──┐
   │  vision · constitution (PG-2..10) · questions register (22)   │
   │  build plan · target structure · LICENCE · lectures           │
   └───────────────────────────────────────────────────────────────┘
                              │
   ┌─ MS-0 · UPSTREAM ─────────────────────── IN PROGRESS ─────────┐
   │  ◐ 0.1 run completes SUCCESS · verification is MANUAL now     │
   │  ⚠ 0.2 QR-5 + QR-19         decided, NOT IMPLEMENTED          │
   │    0.3 QA-4 · 0.4 AB-3 CAD·CDR · 0.5 L0 seat numbers          │
   └───────────────────────────────────────────────────────────────┘
                              │  ★ NO GATE — MS-0 and MS-1+ are PARALLEL
                              ▼
   ┌─ MS-1 · PLATFORM SUBSTRATE ───────────── BUILT 2026-09-03 ────┐
   │  ✅ F1 APPROVED 🟢 · 15 ACs · 16 mutations, all caught         │
   │  ✅ Registry · ports package · contract-suite harness          │
   │  ⚠ AgentPort deferred to MS-4 · ports/__all__ still EMPTY      │
   │  ⬜ CI · ruff  (item 1.1 — independent of everything)          │
   └───────────────────────────────────────────────────────────────┘
                              ▼
   ┌─ MS-2 · FIRST ABSORPTION ───────────── COMPLETE 2026-09-04 ───┐
   │  ✅ src/shared/ absorbed: 1,500 lines · 112 tests · 2 L2 specs │
   │  ✅ namespace package spans both repos · pin + drift tests     │
   │  ✅ rehearsal run · DX-1..DX-6 ALL RESOLVED                    │
   └───────────────────────────────────────────────────────────────┘
                              ▼
   ┌─ MS-3 · OBSERVABILITY ─────────────────── ⛔ BLOCKED ──────────┐
   │  ⛔ F2 is 🟡 DRAFT with SIX open questions (Q1..Q6)            │
   │  ⚠ needs src/orchestration/ absorbed first (QR-22)            │
   └───────────────────────────────────────────────────────────────┘
```

| | Tests | Note |
|---|---|---|
| this repo | **169 passed, 1 skipped** | 15 `F1` ACs · fences · pin · smoke |
| ⬆ upstream | **1068 passed, 4 skipped** | +12 from the `DX-5` fixtures |
| ⬆ upstream, **fresh clone** | **1027 passed, 45 skipped, 0 failed** | ★ was 30 **failed** before `DX-5` |

**What is done, and it is not nothing.** `F1` is approved and implemented with every AC
mutation-verified; the two repos import each other through one namespace package; the absorption has
been **rehearsed end-to-end**; and six discrepancies were found and closed — five of which only
surfaced *because code was written*, not because a document was reviewed.

⚠ **What is NOT done.** **Ten of eleven specs are still 🟡 draft**, so only `F1`'s ACs bind an
implementer. `MS-3` cannot start until `F2` is approved — and `F2` has **six** open questions, more
than `F1` had.

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
| ✅ *2026-09-04* | ~~`MS-2.3` — pin the upstream revision~~ — pin + 11 drift tests + refresh tool; 5 drift modes each verified by planting them | this repo | done |
| ✅ *2026-09-04* | ~~`MS-2.4` smoke test · `MS-2.5` absorption rehearsal~~ — **`MS-2` complete**. Rehearsal surfaced `DX-4`/`DX-5`/`DX-6` and answered `QR-15` | this repo | done |
| ✅ *2026-09-04* | ~~`DX-5`~~ — synthetic broker fixtures + loud skips; **upstream is runnable from a fresh clone for the first time** | ⬆ upstream | done |
| ✅ *2026-09-04* | ~~**`S2` — approve `F2`**~~ — `D1`–`D6` adopted, 16 ACs, 0 open questions | this repo | done |
| ✅ *2026-09-04* | ~~**`MS-3`** — trace substrate built~~ — 14/16 ACs green, mutation-verified; `DX-7` found and fixed | this repo | done |
| ✅ *2026-09-04* | ~~**`MS-3` completion**~~ — real 13-job graph traced and replayed; `AC-2.7`/`AC-2.11` closed. **16/16 ACs** | this repo | done |
| ✅ *2026-09-04* | ~~Approve `F5` `D1`–`D5`~~ — adopted; `D2` confirmed *"fund manager decides what is right"* | this repo | done |
| ✅ *2026-09-04* | ~~**`MS-4`** — evaluation harness built~~ — **16/16 ACs**, 21 mutations all caught first pass | this repo | done |
| ⚠ **Victor** | **Establish the first golden cases** (`D2`, `AC-5.1`). ⚠ The harness refuses a circular value and the regression reds correctly — but **the golden set is empty, so it currently has nothing to red about** | — | ⏳ **needs Victor** |
| ✅ *2026-09-04* | ~~**`MS-5`** — explainability~~ — `F4` approved, 13/15 ACs; ⚠ `D1` **moved two ACs to upstream R7** and corrected §1's *"wire it"* framing | this repo | done |
| ★★ **Next** | **Approve `MS-6`'s four specs.** ⏳ All **17 questions** worked up 2026-09-04 with rejected options: `F3` `D1`–`D5` · `F6a` `D1`–`D3` · `F9` `D1`–`D3` · `F8` `D1`–`D6`. ⚠⚠ **`F8` `D3` (authentication) needs real attention**; ⏳ `F8` `Q6` stays open by design | this repo | ⏳ **needs Victor** |
| ✅ *2026-09-04* | ~~Approve `MS-7`'s three specs~~ — 14 decisions adopted; ★★ **all 11 specs 🟢** | this repo | done |
| ✅ *2026-09-04* | ~~**`MS-7`** built~~ — kill rule, `T1`–`T7`, deliberation, Tier-B study | this repo | done |
| ⚠ **Victor** | **Run `F7a`** — needs hand-written false challenges and a live `F6b`. `D1`: ~23/arm for KEEP, ~99 for DELETE | — | ⏳ |
| ⚠ **Victor** | **Add repository secret `UPSTREAM_REPO_TOKEN`** (read access to `ai-investment-pipeline`) — CI cannot check out the private sibling without it, and ⚠ **the namespace packages span both repos** | — | ⏳ |
| ★★ **Next** | `MS-8` (absorption remainder — 9 domains still upstream) or `MS-9` | this repo | ✅ unblocked |
| ~~superseded~~ | ~~Approve `MS-7`'s three specs~~ — 14 decisions worked up. ⚠⚠ Two need real attention: **`F7a` `D1`** (the kill rule's cheap verdict is KEEP and its expensive one is DELETE — wrong way round for a gate) and **`F7b` `D2`** (both arms are PAPER outcomes; the study measures the *recommendation*, not the *portfolio*) | this repo | ⏳ **needs Victor** |
| ◐ **Anytime** | `MS-1.1` — CI + ruff. ★ **Eight** hand-verified guarantees now depend on it | this repo | ⬜ |
| ★ **Also ready** | **Wrap the LLM gateway** so `ExternalCall` records come from real runs, not direct writes — the one gap `MS-3` leaves | this repo | ✅ unblocked |
| ◐ **Anytime** | `MS-1.1` — CI + ruff. ★ **Now four** hand-verified guarantees depend on it | this repo | ⬜ |
| ~~superseded~~ | ~~`S2` — approve `F2`~~ ⏳ All six questions now have worked proposals with rejected options (`F2` §7 `D1`–`D6`). ★ `Q5` was **answered by measuring** the inherited code: `seed` covers the RNG, **43 wall-clock call sites** are the real gap | this repo | ⏳ **needs Victor's approval only** |
| ★ **Then** | **`MS-2.7` — absorb `src/orchestration/`** (`QR-22`) — ⚠ the 74-line `__init__.py` with 11 re-exports. Do it *before* `MS-3` writes `src/orchestration/trace/`. ★ `D6` depends on it: boundary instrumentation becomes an intra-repo change | this repo ⬅ ⬆ | after `F2` 🟢 |
| ◐ **Anytime** | `MS-1.1` — CI + ruff. ★ Now more valuable than it looks: **CI is what makes the fresh-clone guarantee `DX-5` just bought actually hold** | this repo | ⬜ |
| ✅ *2026-09-04* | ~~**`DX-5`**~~ — fixed with **A + B split by kind**: 12 structural tests on tracked synthetic fixtures, 41 external-truth tests skip loudly. Fresh clone: 30 failed → **0 failed** | ⬆ upstream | done |
| ★★ **Next** | **`MS-3` — observability** (`F2`). ⚠ First absorb `src/orchestration/` (74-line `__init__`, 11 re-exports) per `QR-22` | this repo | ✅ unblocked |
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

## 2.2b ✅ `MS-2.7` — D-08 absorbed, 2026-09-04

**Unblocked by `QR-23`:** Victor suspended the daily run until this repo is complete, upstream retired,
and **E2E validation** done. The only objection to absorbing D-08 was that it would make this repo
load-bearing for that run. ★ There is no run to break.

| | Before | After | Δ |
|---|---|---|---|
| this repo | 169 | ✅ **244 passed, 1 skipped** | +75 |
| ⬆ upstream | 1068 | ✅ **1006 passed, 4 skipped** | −62 |
| **sum** | **1237** | **1237** | ★ **0 — conserved** |

⬆ **fresh clone: 965 passed, 45 skipped, 0 failed.**

**Moved:** `src/orchestration/**` (20 modules, 3,088 lines — contracts, entrypoint, jobs, policy,
schedule, state) · `test_orchestration_b3.py`, `_b6.py` · `L1-orchestration.md` · one
`ownership.yaml` entry. ⚠ The three cross-domain integration tests (`deliver`, `wiring`,
`b3_skeleton`) **stayed upstream** — they exercise the whole pipeline, not this domain, and resolve
`src.orchestration` through the namespace package.

### ⚠⚠ The hazard `L4` §5.1 predicted arrived HERE, not at `MS-8`

`src/orchestration/**` **contains four platform paths already governed by their own specs**:

```text
   src/orchestration/trace/**          -> F2      ← must be matched FIRST
   src/orchestration/policy/routing.py -> F6a
   src/orchestration/control/**        -> F8
   src/orchestration/graph/**          -> F6b
   src/orchestration/**                -> L1-orchestration   ← the container, LAST
```

★★ **Why it needed a test rather than a careful comment.** Ordered wrongly, the inherited L1 spec
would govern platform code — and **the gate would still fire**, the edit would still be permitted
after reading *a* spec, and **nothing would look broken**. That is the same invisible-failure class as
`ST-8`'s stale glob and `DX-3`'s vacuous fence: the third instance in four days.

**So `MS-8` item 8.4a was built now** — `tests/structural/test_ownership_ordering.py`, 13 tests,
covering ordering, spec-file existence, stale globs (`ST-8`) and the resolution of all nine boundary
paths. ⚠ Verified by **planting both failure modes**: reordering the broad glob to the front → 5
failures; renaming a glob so it matches nothing → 2 failures.

★ **A note on the `KNOWN_UNBUILT` allowlist.** Globs for unwritten code legitimately match nothing, so
`ST-8` cannot simply fail on them. The list of tolerated ones is explicit, and a second test asserts
**every entry still fails to match** — so the allowlist cannot outlive its entries and quietly
re-permit a genuinely stale glob.

## 2.2a ⚠ Re-evaluated 2026-09-04 — the queue is not as serial as it looks

**Two assumptions in `§2.2` were wrong, and correcting them changes what to do while `F2` waits.**

★ **1. Absorbing `src/orchestration/` does NOT depend on `F2`.** It was listed *after* `F2` 🟢 because
`MS-3` needs both. But the absorption moves a domain between repos — it has nothing to do with what
`F2` says. ⚠ It is also the **hardest absorption so far** (74-line `__init__.py`, 11 re-exports,
against `src/shared/`'s two docstrings). Doing it while `F2` is in review converts waiting into
de-risking, and `MS-3` then starts on ground that is already proven.

> ⚠⚠ **But it carries a consequence that must be a decision, not a side effect.** Absorbing D-08 makes
> **this repo load-bearing for the daily run** — the orchestrator itself would live here. Today only
> `src/shared/` does. ★ `MS-0` is still in flight and is the critical path for real money, so the
> question *"is it acceptable for the daily run to depend on the platform repo while `MS-0` is
> unfinished?"* is **Victor's**, not the plan's. **Recorded rather than assumed.**

★ **2. `MS-1.1` (CI + ruff) is worth more than its position suggests.** It was parked as tidying. But
`DX-5` just bought a **fresh-clone guarantee** — upstream went from 30 failures to 0 on a clean
checkout — and **that guarantee currently holds because it was tested once, by hand.** Nothing stops it
regressing. ★ CI is what converts it from an observation into a property. It needs no approval and
blocks nothing.

**So the queue, re-ordered by what is actually blocked:**

| | Work | Needs | Why now |
|---|---|---|---|
| ★★ **1** | **`MS-1.1` — CI + ruff** | nothing | ⚠ **Four** guarantees now hold only because they were tested by hand: the fresh-clone run (`DX-5`), the architecture fences (`DX-3`), glob ordering (`MS-2.8`), and framework confinement (`AC-2.10`) |
| ⏳ **2** | **Approve `F2` `D1`–`D6`** | ⏳ **Victor** | The only true blocker on `MS-3` |
| ✅ **3** | ~~`MS-2.7` — absorb `src/orchestration/`~~ | ✅ `QR-23` voided the objection | **Done 2026-09-04** — 3,088 lines; surfaced the `L4` §5.1 hazard early (§2.2b) |
| **4** | **`MS-3`** — observability | **only 2 now** | ★ D-08 is ours, so `D6`'s boundary instrumentation is an intra-repo change |

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
| 1.1 | Repo scaffolding: `pyproject.toml`, CI, `LICENSE`, ruff/pytest config | — | ✅ **2026-09-04** — ruff clean, `.github/workflows/ci.yml`, `tools/check_all.py` |
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
| 2.3 | ✅ **Pin the upstream revision** — `config/upstream_pin.json` + `tests/structural/test_upstream_pin.py` (11 tests) + `tools/refresh_upstream_pin.py`. Pinned `6925c22` on `rel6_discipline` | ✅ **2026-09-04** |
| 2.4 | ✅ **Smoke test** — `tests/integration/test_ms2_absorption_smoke.py`, 8 tests, no mocks. Real `Decimal` FX arithmetic; ★ **`src.quant.errors.QuantError` (upstream) subclasses `src.shared.errors.PipelineError` (here)** — the boundary resolved at class-definition time; absorbed code served through the `F1` registry with provenance | ✅ **2026-09-04** |
| 2.5 | ✅ **Absorption rehearsal** — §5.1. `42 failed, 1183 passed` merged; **1 file collision**, 0 import conflicts. Surfaced `DX-4` ✅ `DX-5` ⛔ `DX-6` ✅, and answered `QR-15` | ✅ **2026-09-04** |
| 2.6 | ✅ **Discrepancy log opened** (§6) — `DX-1` ✅, `DX-2` ✅ | ✅ |

| 2.7 | ✅ **Absorb `src/orchestration/` (D-08)** — 20 modules, **3,088 lines**, 2 dedicated tests, `L1-orchestration.md`, 1 `ownership.yaml` entry. ⚠ The load-bearing objection was **voided by `QR-23`** (daily run suspended) | ✅ **2026-09-04** |
| 2.8 | ★ **`L4` §5.1 glob-ordering assertion built** — `tests/structural/test_ownership_ordering.py`, 13 tests. ⚠ Was `MS-8` item 8.4a; the hazard arrived **here** instead | ✅ **2026-09-04** |

**Done when:** `src/shared/` exists in exactly **one** repo, both suites are green, and `ownership.yaml`
says who governs the moved files. *(2.7 is scoped here but gated separately — see §2.2a.)*

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

### ✅ `MS-1.1` — CI and ruff, 2026-09-04

**The nine guarantees stop depending on my memory.** `tools/check_all.py` runs them in one command
locally; `.github/workflows/ci.yml` runs the same script on every push.

**ruff.** Config matches upstream's `line-length = 100`, `target-version = "py310"` **exactly** — a
lint that disagreed would reformat half the tree on the first run after `MS-8`, and `PG-8` says the
absorption is a move, not a rewrite. 93 findings on our code; **all fixed, 0 suppressed by blanket
rule**. The five `zip()` findings were worth the pass on their own: each now states whether truncation
is intended, and `replay.py`'s says why `strict=False` is deliberate — a length difference there is a
**reportable divergence**, and raising would turn `DIVERGED` into a crash.

⚠⚠ **Absorbed code is EXCLUDED from the strict set and is NOT exempt.** Upstream *declared* a ruff
config and never ran it (ruff is not installed there); its tree carries ~164 findings under its own
declared rules. Linting it strictly would either stop the build or force a mass reformat of inherited
code. ★ Paths **this repo authored inside those trees** — `data_engine/corporate_actions/`,
`fundamental/source/` — are **not** excluded.

> ⚠⚠ **Two self-inflicted findings during this milestone, both the same shape as `DX-9`.**
>
> **1.** ruff reformatted `src/orchestration/__init__.py` — **inherited code** — because the exclusion
> list named `src/orchestration/jobs/` and friends but **not the package's own `__init__.py`**.
> ★ *An exclusion list that covers `pkg/` but not `pkg/__init__.py` looks complete and is not.*
> Restored byte-for-byte from upstream's committed copy, and every absorbed file was then diffed
> against `HEAD` to confirm nothing else had drifted.
>
> **2.** `check_all.py --skip-upstream` printed a warning and then said **"ALL CHECKS PASSED"**.
> ⚠ That is `DX-9` in prose: a narrowed run reporting success. It now **exits 2** unless
> `--allow-narrowed` is passed. *Writing the warning is not the same as refusing to pass.*

**CI's hard part is the sibling checkout**, and the workflow says so at length: `src` and `tests_src`
are namespace packages spanning **both** repos, so CI must check out both **as siblings** or the other
repo's domains vanish — and ⚠ absence-asserting scans then pass **vacuously**.
`test_the_graph_is_not_vacuous` is the guard, and the workflow warns against "fixing" a failure there
by relaxing it. A pre-flight step also fails if either repo regains a root `src/__init__.py` (`DX-1`).

⏳ **Needs Victor:** repository secret **`UPSTREAM_REPO_TOKEN`** with read access to the private
`ai-investment-pipeline`.

### ✅ `MS-2.3` — the upstream revision is pinned, 2026-09-04

**Why it needed more than a version string.** Absorption is per-domain, so this repo imports
`src.quant.*`, `src.orchestration.*` straight out of a **sibling working tree** — not a released
package. Nothing was version-controlled from this side: someone could `git pull` upstream and this
repo's tests would keep passing against different code, silently. ⚠ That is `DX-3`'s shape again — a
check that stops checking without saying so.

| Piece | Role |
|---|---|
| `config/upstream_pin.json` | commit, branch, **the suite results observed against them**, and the expected uncommitted delta |
| `tests/structural/test_upstream_pin.py` | 11 tests — fails loud on drift |
| `tools/refresh_upstream_pin.py` | the *legitimate* way to move the pin, so it is not hand-edited |

★ **The design point is `expected_uncommitted`.** Upstream is legitimately dirty right now — `MS-2.2a`
and `MS-2.2b` were made there and await review. A pin that ignored that would be a lie; one that simply
failed would be noise nobody reads. So the pin **lists the expected delta and fails only on the
unexpected**, which is what *"attributable"* actually means. ⚠ Wildcards are rejected, and the list must
shrink to empty once the absorption is committed.

**Drift modes verified by planting each one:** upstream moved · different branch · sibling repo missing ·
unexpected upstream edit · wildcard blanket allowance. All five fail; all five pass again on restore.

> ⚠⚠ **A defect this milestone found in its own tooling — worth keeping.** `_git()` used
> `stdout.strip()`, which eats the **leading space of the first `git status --porcelain` line**: ` M
> pyproject.toml` became `M pyproject.toml`, and slicing from index 3 produced **`yproject.toml`**. The
> pin generator had the *identical* bug, so the two agreed with each other and **every test passed**.
> ★ It was caught only by reading the tool's printed output, not by any assertion.
> **A bug shared by a value and its checker is invisible to comparison** — which is why the porcelain
> parsing now has its own table-driven regression test instead of being trusted because the suite is
> green.

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
| 3.1 | ✅ `src/orchestration/trace/` — `StepRecord`, `ExternalCall`, `DecisionRecord`, `CapabilityDelta`, `TraceStore`, `replay`, `redact` | `F2` |
| 3.2 | ✅ ★★ **`PG-5.2`** — `CapabilityDelta` carries `pre`/`post`, and is **refused without a `decision_id`**; written even when `changed` is false | `F2` |
| 3.3 | ✅ ★★ **`PG-9`** — `DecisionRecord` **raises** if any of `state`/`candidates`/`action`/`reason`/`propensity` is null (5 parametrised cases) | `F2` |
| 3.4 | ✅ Replay serves every external call from the recording; `respond()` is the only door. Verdict **`REPRODUCED`** (`D3`), never `IDENTICAL` | `F2` |
| 3.8 | ✅ **`traced()` wraps `invoke`** — job-boundary recording with **zero edits to the inherited runner** (`D6`, `AC-2.1`) | `F2` |
| 3.9 | ✅ **`OutcomeStore`** — the `decision_id` join that makes `F7b` possible years later (`AC-2.7`, `CT-2.6`) | `F2` |
| 3.5 | ✅ **`QR-14` confinement** — `tools/check_framework_confinement.py` + 13 tests. ⚠ **AST, not grep**: `L4` §10.1's grep form fails on a *docstring* mentioning a framework | `F2` |

| 3.6 | ⏳ **`D1` layout** — `trace.jsonl` + `trace/payloads/` per run. ⚠ Payload separation is what makes `D2`'s expiry possible **without breaking append-only** | `F2` |
| 3.7 | ⏳ **`D5` clock allowlist** — record the run's clock origin; excluded wall-clock fields are **printed in the `ReplayReport`**, never silently skipped | `F2` |

**Done when:** a full pipeline run is traced, and replaying the trace **reproduces its control flow**
(`D3` — ⚠ *not* "reproduces it", which over-claims what replay can establish).

### ✅ `MS-3` — COMPLETE 2026-09-04

**301 passed, 1 skipped** here (was 244). **16/16 `F2` ACs green.**

★★ **The done-when is met.** `tests/integration/test_ms3_traced_run.py` runs the **real
`DAILY_INFERENCE` graph — all 13 jobs, in dependency order** — through the inherited `Orchestrator`
with its real cadence, preconditions, budget, retry and checkpoints, with the recorder attached; then
replays it to `REPRODUCED`, and proves a changed graph reports `DIVERGED` **located** at the right job
and field.

⚠ **What is simulated, stated plainly: the dispatch.** `invoke(job, manifest)` returns fixtures rather
than calling vendors. That is not a shortcut around the test — it *is* the architecture (`OR-1`:
D-08 never calls a domain function directly, so dispatch is a parameter). ★ But **a live run also
exercises the vendors, the LLM and the money path, and this does not** — `PG-10` forbids reading more
into it than that.

**The integration needed ZERO changes to the inherited runner** — `traced()` wraps `invoke`. Editing
`_run_one` would have put F2 inside D-08's retry path, where a trace bug could change whether a job is
retried. ⚠ A recorder that can alter the run it records is not an observer.

### ⚠⚠ Four mutations survived the first pass — and one was serious

| Survivor | What it exposed |
|---|---|
| `redact_secrets` removed from the **log** path | The only secret under test lived in an `ExternalCall` *payload*, redacted on a **different** path. A credential in `DecisionRecord.state` would have been written verbatim |
| the recorder **swallows** the exception | ⚠⚠ The `StepRecord` still said `FAILED` while the runner saw a clean return — **the trace and the run disagreed**, and every assertion passed. Exactly the "not an observer" failure the design claims to avoid, untested |
| `for_decision` returns the **first** row | With one outcome in the store, ignoring the id was indistinguishable from matching it |
| `AC-2.9`'s value-scrubbing | A secret-shaped value under a harmless key |

★ Each was a case of **one test being credited with covering two paths**. All four closed.

### ✏ `AC-2.7` had been deferred to `MS-4` — wrongly

**290 passed, 1 skipped** here (was 244); upstream unchanged at 1006. **12 mutations run against the
new ACs; 11 caught on the first pass.**

⚠⚠ **The twelfth is the finding worth keeping.** Removing `redact_secrets` from the **log** write path
left **every test passing**. The only secret under test lived in an `ExternalCall` *payload* — redacted
on a **different code path** — so a credential in a `DecisionRecord.state` would have been written
verbatim and nothing would have noticed. ★ *Two code paths were being credited to one test.* Two tests
added; both paths now fail when broken.

Re-reading `F2` settled it: **`T6` names `trace/outcomes.py::link` and `CT-2.6` defines the record**,
so the outcome *link* is F2's — only *metrics over* outcomes are `F5`'s (§2 non-goals). ★ The spec had
the answer all along; the deferral came from reading the **milestone plan** instead of the **spec**.
⚠ `AC-2.11` likewise needed only a variant resolved through `F1` — a fixture variant *is* one, and the
AC is about F2 recording provenance faithfully, not about the port being production code.

**Also built:** `trace/outcomes.py` — `OutcomeStore`, keyed by `decision_id` **alone** (never
re-derived from run contents), stored **outside** the run directory because `D2` expires payloads while
outcomes must outlive them by years, and append-only because ⚠ *an unfavourable outcome must not be
editable after the fact.*

⚠ **Still open, and it is not an AC:** `ExternalCall` records are not yet emitted by a real run —
`traced()` gives **job** granularity, and call granularity needs the LLM gateway and HTTP client
wrapped. `AC-2.2` is exercised by direct writes. **Recorded in `wire.py`'s docstring so the gap is
visible in the code, not discovered later.**

> ⚠ **3.2 and 3.3 are the ones that cannot be added later.** Everything else in this plan can be
> retrofitted; unlogged history cannot be reconstructed.

## MS-4 — Evaluation harness

`PG-4` — built once, shared by both lanes. Spec-governed per `QR-13`.

| # | Item | Spec |
|---|---|---|
| 4.0 | ✅ **`CT-5.1` `MetricResult`** — `n` required, tier required, value ⊻ insufficiency, `experimental`, `recomputable` | `F5` |
| 4.1 | ✅ **`F5` approved 🟢 2026-09-04** — `Q1`–`Q5` → `D1`–`D5`, 16 ACs | `F5` |
| 4.2 | 🟨 `src/evaluation/golden/` — `GoldenCase` **refuses a circular value** (`D2`); ⚠ **the set itself is empty**, and filling it is Victor's | `F5` |
| 4.3 | ✅ `metrics/` — grounding rate, calibration (bins, ECE, Brier + decomposition), `evidence_coverage` **kept separate** (`AC-5.5`), deletion curve | `F5` |
| 4.4 | ✅ `regression/` — reds on a behaviour change and **names the diverging cases and who established each expectation**; replays `F2` (`D5`), never calls live | `F5` |
| 4.5 | ✅ **`D1` boundary drawn and ENFORCED** — `tools/check_evaluation_boundaries.py` checks all three import rules (`AC-5.11`, `AC-5.12`, `AC-5.15`) | `F5` |

**Done when:** citation rate and a calibration curve compute over real pipeline output, and a
deliberate prompt change reds the regression suite.

### 🟨 `MS-4` — built 2026-09-04; the machinery is done, the inputs are not

**347 passed, 1 skipped** here (was 301). **16/16 `F5` ACs green — 21 mutations, all caught on the
first pass**, the first milestone where none survived.

**Three decisions show up as code rather than prose:**

- **`D2`** — `GoldenCase` **raises `CircularGoldenValue`** if `established_by` or `source` names a
  pipeline component. ⚠⚠ The rejected option produces *more cases and a permanently green suite* while
  certifying the system against itself, so it is refused **in code**, not just discouraged in a comment.
- **`D3`** — `MINIMUM_N` per metric, each with a `CN-10` note saying who set it and that it is an
  **admitted guess**. Below the floor, `measured()` returns an insufficiency naming the shortfall.
- **`D1`** — the metric/study boundary is a **grep**, not a judgement: `AC-5.15` fails if anything
  imports `src/evaluation/studies/**`.

⚠⚠ **The "done when" is NOT met, and the gap is not code.** *"Citation rate and a calibration curve
compute over real pipeline output"* — they compute correctly over fixtures, but **the golden set is
empty**. `D2` makes filling it the fund manager's work, and the harness cannot honestly measure
anything until it has expectations to measure against.

> ★ **That is the right kind of incomplete.** The alternative — seeding the set automatically — was
> available, cheap, and would have made this milestone *look* finished. `D2` exists to refuse it.

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
| 6.1 | ✅ `corporate_actions/` — search **precedes** classification; one source is a lead, two are a finding; a combination yields **two** findings | 8 | `F3` |
| 6.2 | ✅ `ThesisSourcePort` — **both adapters through ONE contract suite** (`F1` `AC-1.9` on a real port); `D2` one prompt, two transports | 2 | `F9` |
| 6.3 | ★ **Pull the actual API bill** and revisit `QR-20` with a number | — | — |
| 6.4 | ✅ Control surface — designation journal, ⚠ `D5` revocation is a **second entry**, `INV-6` enforced over one boundary | 7 | `F8` |
| 6.5 | ✅ **Suspend / resume** — on disk (survives restart), idempotent, `RA-126` expiry, and `D4`'s `data_as_of` stale-input guard | 7 | `F8` |
| 6.6 | ★ **`QR-16` — the full analysis path for any requested name**, same depth as the top-1; the manager designates which analysis is the day's actionable one; the designation is journaled | 8 · 11 | `F8` |
| 6.7 | ✅ `F6a` routing — pure, total, records `influenced_by`; ★ `D1`'s derived phase order **caught an incoherent worked example** | 7 | `F6a` |

**Done when:** the manager can request any name and receive a full-depth analysis, and the request,
the rank it held, and any designation are recorded.

### ✅ `MS-6` — built 2026-09-04

**934 passed, 4 skipped** here (was 385). **All 22 mutations caught on the first pass.**

**Two absorptions came first** (`QR-22`): `src/data_engine/` (62 modules, 8,511 lines) and
`src/fundamental/` (64 modules, 8,527 lines) — ★ the 290-line `__init__.py` with 45 re-exports that
`DX-2` singled out as the hardest. **Test conservation exact: 1,396 before, 1,396 after.**

⚠ **Two new discrepancies, and the second is the instructive one** — see §6.5.
`DX-8`: an absorption must also carry the domain's **`config/`** — the "four things" rule was
incomplete. `DX-9`: ⚠⚠ **`DX-3`'s multi-root fix covered the import graph and NOT filesystem-scanning
tests.** Upstream's yfinance ban silently stopped covering two whole domains, because it asserts
**absence** and a shrinking tree satisfies that trivially. ★ Its sibling test in the same file failed
loudly — but only because it happened to assert *presence*. Same bug, one silent instance and one loud
one, and only the loud one would ever have been noticed. Both fixed; a shared `source_path()` resolver
now spans roots so this stops needing a bespoke fix each time.

> ★★ **`F6a`'s phase order refused an incoherent test before it could ship.** `D1` derived
> `quant → fundamental → risk` from upstream's coverage economics, and `assert_forward` then rejected
> the spec's own worked example — which routed `ranking_model`, a **quant** port in the **first**
> phase, from a peer. **Nothing may configure the first phase.** The real cross-configuration case is
> quant's volatility shaping how deep the *fundamental* analysis goes. ★ A derived rule caught a
> hand-written example; that is the rule earning its place.

⏳ **`F8` `Q6` stays open by design** (`D6`): the effect vocabulary ships **empty**, so every directive
is currently unmappable and applies nothing — which is correct before the effects exist. ⚠ `QR-23` puts
its definition on the path to resuming trading (§7).

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

### 🟨 `MS-7` — built 2026-09-04. ⏳ The instrument exists; the experiment has not run.

**960 passed, 4 skipped** here (was 934). **14 mutations, all caught first pass.**
★★ **All 11 specs are now 🟢.**

⚠⚠ **The "done when" is NOT met, and the gap is not code.** `F7a` requires running real
deliberations against a live `F6b` and a set of hand-written false challenges — ★ `D1` says
**~23 per arm** for a `KEEP` verdict, **~99** for `DELETE`. What exists is the *instrument*:
pre-registered kill rule, the `T1`–`T7` battery, a bounded deliberation loop, and the Tier-B study
that accrues beside it.

**Three decisions are enforced in code rather than described:**

- **`F6b` `D5`** — a `Message` with `from_domain != "risk"` **raises `FirewallCrossing`**. `INV-014`
  is a type error, not a guideline.
- **`F6b` `D3`** — a `respond()` returning `"BLOCK"` **raises**. D-12's algebra gates (`P4`); a second
  gating mechanism is two answers to one question.
- **`F7b` `D2`** — `SCOPE` states *"measures the RECOMMENDATION, not the portfolio"* on every figure,
  and `TierBReport.gate()` exists **only to raise** — `PG-5.1` in executable form.

> ★★ **`D1`'s cost asymmetry showed up as behaviour, not as a table.** A test fixture at
> `0.2 / 0.6 = 0.333` — a hair above the `0.33` band — returned `INSUFFICIENT` where I expected
> `KEEP`, because being marginally outside the cheap band jumps the requirement from **23 to 99 per
> arm**. ⚠ That is exactly the moment budget pressure argues for the verdict that preserves the
> capability, and it is now a named test rather than a paragraph.

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
| 8.2a | ✅ **`DX-5` resolved** — structural parsing runs on tracked synthetic fixtures; the external-truth tests skip loudly. ⚠ At `MS-8`, carry `tests_src/fixtures/broker_statements/` and `tests_src/broker_fixtures.py` **with** the recording domain, and re-confirm `.gitignore` still excludes the real exports (item 8.1a) |
| 8.3 | ⚠ **Copy `sdd/**` WITH the code, not after it — it is a TEST INPUT, not documentation** (`DX-4`). Upstream tests parse `L1-data-engine.md` and `L6-as-built-remaining.md` at runtime to check the code agrees with its spec; copying `src/` without `sdd/` fails 3 tests immediately |
| 8.4 | Merge `ownership.yaml` — ⚠ **`ST-8`: every glob moves in the same commit as its code.** A stale glob matches nothing and the gate then **fails open, silently** |
| 8.4a | ✅ **DONE at `MS-2.7`** — `tests/structural/test_ownership_ordering.py`. Originally: ★★ **assert glob ordering** — for every pair where one glob is a prefix of another, the **more specific must come first** (`L4` §5.1). ⚠ Four platform paths sit inside inherited domains; if an inherited glob is written above them the wrong spec governs, the gate still fires, and **nothing looks broken** |
| 8.5 | ~~Delete `src/shared/upstream.py`~~ — ⊘ **no shim was ever built** (`QR-22`). Instead: ⚠ **verify no domain remains split across both repos** |
| 8.5a | ★ **Retire the upstream pin** (`DX-6`) — delete `config/upstream_pin.json`, `tests/structural/test_upstream_pin.py`, `tools/refresh_upstream_pin.py`. There is no upstream left to pin |
| 8.5b | ★ **Invert `test_ms2_absorption_smoke.py::test_upstream_modules_load_from_the_sibling_repo`** (`DX-6`) — it asserts `src.quant` loads from OUTSIDE this repo, which the merge makes false. ⚠ It is **correct today**; do not weaken it early |
| 8.5c | **De-duplicate `tests_src/conftest.py`** — the rehearsal's ONLY file collision, a deliberate `MS-2.2a` duplicate. Confirm the two are still identical before deleting either |
| 8.5d | ⚠ **Set `pythonpath` back to `.` alone** in `pyproject.toml` and `pytest.ini`, and drop `_SIBLING_REPOS` from `tests_src/architecture.py` — the sibling is gone. `test_the_graph_is_not_vacuous` is what catches this if forgotten |
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

## ✅ 5.1 The rehearsal was run — 2026-09-04

⚠ **Not on a branch.** A branch carries only *committed* state, and every line of `MS-1`/`MS-2` is
still uncommitted pending review — so a branch would have rehearsed a tree that does not exist. The
rehearsal used a **filesystem copy of the live working trees** instead, which is what the merge will
actually see. ★ *The recipe was written before the situation existed; follow its intent, not its
`git checkout`.*

**Result: `42 failed, 1183 passed, 5 skipped`** in the merged tree — against `1056 + 161 = 1217`
passing in the two repos separately. ★ **Every one of the 42 is explained, and none is a merge
conflict in the code.**

| Cause | Fails | Finding | Status |
|---|---|---|---|
| upstream tests read **untracked** BMO statements | **30** | `DX-5` | ✅ **resolved** — fixtures + loud skips (§6.4) |
| upstream tests parse spec files from `sdd/`, not in the copy list | 3 | `DX-4` | ✅ item 8.3 rewritten |
| platform tests that correctly encode the **pre**-merge world | 5 | `DX-6` | ✅ items 8.5a/8.5b |
| ⚠ **file collisions between the two trees** | — | `tests_src/conftest.py` **only** | ✅ item 8.5c |

**What the rehearsal checked, against §5's own list:**

| Class | Result |
|---|---|
| Package collision | ✅ none left — `QR-22` settled it at `MS-2.2a`; the merged tree has one `src/` |
| Path assumptions | ⚠ **3 hits** — all `sdd/`-relative spec reads (`DX-4`), none from `parents[n]` drift |
| Config | ✅ **34 upstream files, 0 collisions** — this **answered `QR-15`**, which had been open since `L4` S-3 |
| Test collection | ✅ no duplicate basenames; **1** genuine same-path file (`tests_src/conftest.py`) |
| `ownership.yaml` | ◐ **not exercised** — the rehearsal ran pytest, not the gate. ⚠ Item 8.4a stays unverified |
| ID collisions | ✅ none surfaced |
| Dependency versions | ✅ one `pyproject.toml`, one `pytest.ini` — no competing pins |
| Entry points | ✅ one `entrypoint.py`; this repo has none to compete |
| `__init__.py` exports | ✅ survived — 296 `src/` files overlaid with no loss |

> ★★ **The headline is what did NOT happen.** ~294 files merged into a tree that already held platform
> code and produced **one** filename collision and **zero** import conflicts. That is `PG-8` — *"the
> tree is a superset, always"* — paying off: absorption really is a move, not a restructuring.
>
> ⚠ **And the headline finding is one nobody was looking for.** §5's checklist anticipated package
> collisions, path assumptions and config merges. The blocker it found instead — **a third of a
> domain's tests depend on data git can never carry** — was on nobody's list, and is *pre-existing*:
> upstream's suite has never been runnable from a fresh clone. ★ It took looking from **outside** the
> machine to see it, which is the entire argument for rehearsing early.

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
| **DX-4** | 2026-09-04 | MS-2.5 | `MS-8` item 8.2's copy list (`src/**`, `tests/**`, `tests_src/**`, `config/**`, `tools/**`) is what the absorption must move | ⚠ **Incomplete — upstream tests read SPEC FILES from `sdd/` at runtime.** 3 failures on `sdd/design/rel6_design/L1-data-engine.md` and `L6-as-built-remaining.md`: tests parse the spec to check code agrees with it. `sdd/` was in item **8.3** as *"the L-specs"*, which reads like documentation and is actually a **test dependency** | `tests_src/test_data_source_precedence.py`, `test_as_built_ab1.py` · `L3` `MS-8` items 8.2/8.3 | ⚠ material | ✅ **resolved 2026-09-04** | `MS-8` item 8.3 rewritten: `sdd/` is a **test input**, copied with `src/`, not documentation copied afterwards |
| **DX-5** | 2026-09-04 | MS-2.5 | Absorption is a `git mv` — everything a test needs travels with it | ⛔⛔ **~30 upstream tests depend on data git CANNOT carry.** `tests_src/test_recording_ingest.py` (21) and `test_risk_flags_from_book.py` (9) read `sdd/design/rel6_design/samples/bmo_investorline_transactions/` — **4 files on disk, 0 tracked**, because they are real BMO broker statements and both repos' `.gitignore` excludes them **correctly**. ⚠ **A fresh clone of upstream cannot run its own suite today** — this is pre-existing, not caused by the absorption; the rehearsal is simply the first thing to look | upstream `.gitignore:48` · `tests_src/test_recording_ingest.py`, `test_risk_flags_from_book.py` | ⛔ blocker for `MS-8` | ✅ **resolved 2026-09-04** | **Option A + B, split by KIND** (§6.4). ★ 12 new structural tests on **tracked synthetic fixtures** (`tests_src/fixtures/broker_statements/`, every value invented) — parsing is now verifiable on any clone. ⚠ The 41 **external-truth** tests keep the real data and **skip loudly** without it. Fresh-clone simulation: **12 passed, 41 skipped, 0 failed** (was 30 failed). Upstream 1056 → **1068 passed** |
| **DX-6** | 2026-09-04 | MS-2.5 | The platform's own tests survive the merge | ⚠ **5 of them encode the PRE-merge world and must fail after it** — correctly. `test_upstream_pin.py` (4) checks a sibling repo that will no longer exist; `test_ms2_absorption_smoke.py::test_upstream_modules_load_from_the_sibling_repo` (1) asserts `src.quant` loads from **outside** this repo, which stops being true the moment it is inside | `tests/structural/test_upstream_pin.py` · `tests/integration/test_ms2_absorption_smoke.py` | ◐ cosmetic | ✅ **resolved 2026-09-04** | ★ **Not weakened now** — they are correct today and weakening them would defeat `MS-2.3`. Retirement is scheduled as `MS-8` items 8.5a/8.5b instead |
| **DX-7** | 2026-09-04 | MS-3 | `DX-1`/`DX-2` settled the namespace rule for `src/` and `tests_src/`; other shared top-level directories follow | ⚠ **It recurs at `tools/` — the THIRD instance.** This repo's `tools/` has no `__init__.py` (namespace); upstream's has an **empty** one, making it a *regular* package that **ends the import scan**. So `import tools.check_framework_confinement` resolved to upstream's `tools/`, which does not contain it, and failed with `ModuleNotFoundError` naming the submodule — ⚠ **exactly the misleading error `DX-1` documented.** ★ It passed under `python3 -c` (only one root on the path) and failed under pytest (both roots) — so it looked like a pytest problem | `tools/__init__.py` (upstream, 0 lines) · this repo's `tools/` | ⚠ material | ✅ **resolved 2026-09-04** | Deleted upstream's empty `tools/__init__.py`. ★★ **It was UNTRACKED** — hidden by upstream's blanket `__init__.py` gitignore rule, which this repo's own `.gitignore` calls *"a real defect"* and deliberately refused to inherit. **So a file git could not see was silently breaking imports across the repo boundary.** Nothing upstream imports `tools.*`; blast radius zero. `tools` is now a namespace spanning both, like `src` and `tests_src`. ★ **The rule generalises: EVERY shared top-level directory must be a namespace package**, now stated in `L4` §4 rather than rediscovered per directory |
| **DX-8** | 2026-09-04 | MS-6 | An absorption moves code, tests, globs and architecture rules (`DX-3`'s "four things") | ⚠ **There is a FIFTH: `config/`.** Absorbing `src/data_engine/` broke 2 tests here with `FileNotFoundError: config/sp500_tickers.yaml` — the domain's tests read config files that stayed upstream. ★ `QR-15` measured that `config/` **merges** cleanly; it never asked whether a domain's config must **travel** with it | `config/sp500_tickers.yaml` · `tests_src/test_data_engine_ingest.py` | ⚠ material | ✅ **resolved 2026-09-04** | The absorbed domain's config files copied with it. ★ **The rule is now FIVE things: code · tests · `ownership.yaml` globs · architecture rules · CONFIG** |
| **DX-9** | 2026-09-04 | MS-6 | `DX-3`'s multi-root fix made the architecture rules span both trees | ⚠⚠ **It fixed the IMPORT-graph rules only. Tests that scan the FILESYSTEM narrowed silently.** `tests_src/test_data_source_precedence.py` sets `SCANNED = (Path("src"), Path("tools"))` — upstream's own tree — and asserts **absence** (`assert offenders == []`, the yfinance ban). ★★ **An absence assertion over a shrinking tree passes trivially**, so the ban stopped covering the absorbed domains **and nothing failed.** ⚠ One sibling test in the same file failed loudly only because it asserted *presence* (`assert "period" in seen`) — **that was luck, not design** | upstream `tests_src/test_data_source_precedence.py` | ⚠ material | ✅ **resolved 2026-09-04** | `SCANNED` now derives from `architecture.SRC_ROOTS`, so it spans both trees like the import rules; the EDGAR path test resolves its directory across roots. ★ **The generalised rule is in §6.5** |

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

## 6.5 ⚠⚠ `DX-8`/`DX-9` — the absorption checklist was incomplete, twice

★ `DX-3` produced a rule: *an absorption moves **four** things — code, tests, `ownership.yaml` globs,
and the architecture rules that scan its path.* **Two more absorptions found two more things.**

| Found at | Missing | Symptom |
|---|---|---|
| `MS-2.7` (`DX-3`) | architecture rules | `SI-1` scanned 0 files and reported `14 passed` |
| `MS-6` (`DX-8`) | **`config/`** | `FileNotFoundError: config/sp500_tickers.yaml` — loud, at least |
| `MS-6` (`DX-9`) | **filesystem-scanning tests** | ⚠⚠ **silent** — an absence assertion over a shrinking tree |

### ★★ The rule, restated — an absorption moves FIVE things

> **code · its tests · its `ownership.yaml` globs · the rules that scan its path · its `config/`**

### ⚠ And the sharper lesson from `DX-9`

`DX-3` was fixed by making the **import graph** multi-root. That felt like a complete fix and was not:
**any test that resolves a path relative to the repo root has the same defect**, and the import graph
was merely the instance that had been noticed.

> ⚠⚠ **A test that asserts something is ABSENT gets *more* likely to pass as the tree it scans gets
> smaller.** `DX-9`'s yfinance ban stopped covering two whole domains and stayed green. The sibling
> test that failed did so only because it happened to assert **presence** — ★ *the same bug produced a
> loud failure and a silent one in the same file, and only the loud one would ever have been noticed.*

**Check at every future absorption:** `grep -rn 'Path("src\|Path("config\|Path("tools' tests*/` in
**both** repos, and confirm each hit still resolves to the tree it means.

## 6.4 ⛔ `DX-5` — tests that depend on data git cannot carry

**The finding.** `tests_src/test_recording_ingest.py` (21 tests) and `test_risk_flags_from_book.py`
(9) read **real BMO InvestorLine transaction statements**. There are **4 files on disk and 0 tracked** —
both repos' `.gitignore` excludes that directory, and ★ **correctly so**: it is real personal financial
data, and this repo's own `.gitignore` calls it *"the sharpest item in this file."*

⚠ **This is pre-existing, not caused by the absorption.** Upstream's suite reports `1056 passed` on
*this machine* because the files happen to be here. **On a fresh clone, ~30 tests fail.** The rehearsal
is simply the first thing that ever looked from outside.

★ **Why it is nevertheless an `MS-8` blocker:** `MS-8` says *"the full suite is green in one repo."*
That criterion is unmeetable while a third of the recording domain's tests need files no clone will ever
have — so either the data becomes portable, or the criterion has to say what it actually means.

### Options

| | Option | Assessment |
|---|---|---|
| ⛔ | **Track the CSVs** | **Not an option.** Real broker statements in git history, unremovable. The `.gitignore` rule exists precisely to prevent this |
| ★★ **A** | **Synthesise a redacted fixture set** — same shape and edge cases, invented names and amounts — and point the tests at it; keep the real files as an optional override | **Recommended.** ⚠ The tests' value is in the *edge cases* (`RC-55` mixed column widths, a CDR and its common share held together, blank activity rows carrying cash) — **those are shape, not identity**, so a fixture reproduces them faithfully. Cost: real work, ~30 tests, and each edge case must be re-derived from the real file before it can be faked |
| **B** | **Skip loudly when the data is absent** | ◐ Cheap and honest — a fresh clone reports *"skipped: needs local broker data"* rather than failing. ⚠ But `PG-5`'s spirit is that an unmeasured thing is unproven, and a permanently-skipped test is an unenforced one. Acceptable as an **interim beside A**, not instead of it |
| **C** | **Move the data outside the repo** and reference it by env var | ⚠ Same skip problem, plus a new configuration surface. No better than B |
| **D** | **Declare the recording domain's tests machine-local** | ✗ Gives up on the merged suite being meaningful — and `MS-8`'s done-when is exactly that |

★ **Recommendation: A, with B as the interim** — land the loud skip now so a clone is honest, then
build the fixture set when the recording domain is next touched. ⚠ Both are **upstream test surgery on
~30 tests**, so neither was done unilaterally.

### ✅ Resolved 2026-09-04 — and the recommendation changed on contact

**Implementing A revealed that "these ~40 tests" are two different kinds of test, and the fix differs
for each.** The original recommendation treated them as one population; that was wrong.

| Kind | Example | Fix | Why |
|---|---|---|---|
| ★ **Structural** | RC-55 two column widths in one file · RC-12 a zero total is a tranche · RC-46 `BBD.B` · RC-13 unknown activity raises · RC-48 foreign row refused · RK-5 common **and** CDR | **A — synthetic fixture** | These assert **shape**, and shape is faithfully reproducible. They should pass on any clone |
| ⚠ **External truth** | RC-57 *derived cash matches the broker balance to the cent* · *225 orders over four years* · *67 of 120 round trips close inside 30 days* | **B — skip loudly** | ⚠ Their value **is** that the data is real. A synthetic version asserts a property of invented data **while looking like validation** — strictly worse than not running |

> ★★ **The rule this produced: fixture what is SHAPE, skip what is TRUTH.**
> A synthetic external-truth check is not a weaker test — it is a **false** one. ⚠ Had option A been
> applied to the whole population as first recommended, `RC-57` would have become a test that
> "verifies" cash against a balance chosen to make it pass. That is the single most dangerous outcome
> available here, and it would have looked like the *most* thorough one.

**Built:** `tests_src/broker_fixtures.py` (resolver + `requires_real_statements`, with
`$BMO_STATEMENTS_DIR` override) · `tests_src/fixtures/broker_statements/` — 5 tracked CSVs, **every
value invented**, reproducing the real files' structure (one header, per-row width detection, wide
block then narrow block as in `TFSA_2`) · `tests_src/test_recording_ingest_synthetic.py` — 12 tests.

| | Real data present | Fresh clone |
|---|---|---|
| before | 41 passed | ⛔ **30 failed** |
| after | 41 passed **+ 12 new** | ✅ **12 passed, 41 skipped, 0 failed** |

⚠ **Four fixture bugs were caught by the domain code itself** while building this — an implausible
negative commission (a zero-total tranche means its sibling carries the **full** order amount), a
repeated mid-file header, `None` quantities on a dividend row, and a wrong assumption about the
position key shape. ★ Each was the *parser* refusing invented data that a real broker would never
emit — good evidence the fixtures are now shaped like the real thing rather than merely parseable.

⚠ **Still true, and deliberately not papered over:** the external-truth tests do not run on any machine
but the fund manager's. That is a real coverage limit, now **stated by every skip** rather than
discovered by a failure.

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

> ⚠⚠ **`QR-23` changed this section's status.** E2E validation is now a **precondition for resuming
> real trading**, not a milestone tick. Anything parked "until E2E" is on the critical path.
>
> ⏳ **`F8` `Q6` — the initial effect vocabulary (`CT-8.5`)** is parked here by Victor's decision
> (`F8` `D6`): it should describe effects the system actually has, so it is defined **during** this
> validation. ★ Recorded here so it is found by the person doing E2E rather than remembered.

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
