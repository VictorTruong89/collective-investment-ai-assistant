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

**Last reviewed: 2026-10-01.** ⓘ Every row below still holds as written. The live state since MS-9 is in §2.1, and the newest dated entry is §2.1o.

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
| **MS-8** | **Absorption — the remainder** | all | — | MS-6 ✅ | 🟨 **DONE 2026-09-04** — 9 domains, one tree, **1,524 passing**. ⚠ `8.9` (retire upstream) NOT done — outward-facing; `DX-12` open |
| **MS-9** | Write-up, mirror, polish | — | — | MS-8 ✅ | 🟨 **2026-09-04** — essay, README, audit, mirror builder all built. ⊘ `9.4` demo descoped to 2027; ⛔ publishing is Victor's and is **not urgent** |

⚠ **`MS-7` is the first thing cut if `MS-0` or `MS-3`–`MS-4` overrun.** Said now, while it is cheap to say.

## 2.1 Current position — ★★★ platform COMPLETE · FIRST THESIS (MU SELL — 2 of 4 falsifiers FIRED, computed) · ★★ scorecard coverage **1.000** (E-09 solved) · analysis 77 % declared · 69 % working · ★ dev calls on the subscription (§2.1o) · ⊘ golden programme CLOSED (§2.1p) · ★ consensus + duration in the bundle (§2.1q) · updated 2026-10-03

```text
   ┌─ PHASE 0 · SPECS ────────────────────────────────── COMPLETE ──┐
   │  ★★ 13 of 13 specs 🟢 APPROVED · 180 ACs (F10 23 · F11 9)      │
   └────────────────────────────────────────────────────────────────┘
                              ▼
   ┌─ MS-1 … MS-7 · THE PLATFORM ─────────── ★★★ 148/148 ACs ───────┐
   │  F1 15 · F2 16 · F3 12 · F4 13 · F5 18 · F6a 11 · F9 10        │
   │  F7a 12 · F6b 12 · F8 20 · F7b 9                               │
   │  ⛔ 1 red: J-07 golden (re-established) · 2,494 pass           │
   └────────────────────────────────────────────────────────────────┘
                              ▼
   ┌─ MS-8/9 · ABSORPTION + WRITE-UP ─────────────── ONE TREE ──────┐
   │  ✅ 15 domains · ~40,000 lines · upstream src/ is GONE         │
   │  ⛔ 8.9 retire the old repo · publishing — both Victor's       │
   └────────────────────────────────────────────────────────────────┘
                              ▼
   ┌─ ★★★ THE ANALYSIS LAYER — 35 prompt blocks (+J-20) ────────────┐
   │  declared 27 (77 %) · working 24 (69 %) · graded 7 (20 %)      │
   │  E 9/15 declared · ★ 9 working — E-09 solved at effort low     │
   │  J 18/20 declared · ★ 18 working — J-04 scored, none absent    │
   │  ★★ FIRST CT-1.1 THESIS: MU SELL · Medium · 4 falsifiers · 9 gaps│
   │  ⛔ falsifiers #1 #2 FIRED on later filings — thesis WRONG      │
   │  ★★ COMPLETE: moat=2 eq=4 bs=3 cap=4 · coverage 1.000          │
   │  ⚠ conviction still Low — 3 governing inputs absent (DX-118)   │
   │  ★ first DERIVED rubric scores: bs@v3=3·3·3  cap@v3=4·4·4     │
   │  ✅ bundle: extraction parts · subject guard · no repo header  │
   └────────────────────────────────────────────────────────────────┘
                              ▼
   ┌─ THE GOLDEN SET ──────────────────── ⊘ CLOSED 2026-10-01 (L8 §9) ─┐
   │  53 LIVE, kept & maintained: 48 extraction · 5 thesis           │
   │  52 pass · J-07 RED on purpose · 14/35 blocks · NO new cases    │
   │  10 thesis drafts FROZEN unsigned · judgement → falsifiers +    │
   │  rule checks                                                    │
   └─────────────────────────────────────────────────────────────────┘
                              ▼
   ┌─ ⬜ NEXT — in dependency order (§2.1p) ──────────────────────────┐
   │   ✅ 2026-10-01: dev LLM calls → subscription (§2.1o, GW-24…29)  │
   │   ✅ DX-131 · DX-135 · DX-137 closed · 22 extraction signed      │
   │   1. ✅ RULE CHECKS built — 45 calls, 4 known (DX-138 new)     │
   │   2. ✅ k=1 gate: unmeasured BUY now FLAGS (RA-154)            │
   │   3. ✅ FALSIFIER LOOP: J-15 v2 live on MU — 4/4 valid tests,  │
   │        decided automatically · DX-139 (partial window) fixed    │
   │        · ✅ 4 MU readings reviewed by Victor (DX-128)          │
   │   4. ✅ AGREEMENT PROBE · live: MU J-16 SELL 3/3, conv. SPLIT  │
   │   5. ◐ ✅ CONSENSUS (FMP, PIT) · ✅ DURATION TABLE (F10 D10)   │
   │        ✅ J-09 re-run: consensus STATED · ✅ DX-140 ruled       │
   │        ⏳ thesis resume J-10…J-17 (§2.1q)                       │
   │        ✅ F10 D11 margin share · ✅ F11 base rates (memory@v1)  │
   │        ✅ 3rd thesis: SELL; caps lifted (DX-146) · DX-144 refuses│
   │        ✅ J-15 v3 + DX-147 · 4th thesis SELL/Medium-High,  │
   │           uncapped — falsifiers #3 #4 FIRED, #1 #2 pending    │
   │   then: 8 undeclared blocks · DX-76 · AMD thesis · quant ~70 %  │
   │  open: DX-57 60 61 78 79 87 89-92 134 · partial 44 71 80        │
   └─────────────────────────────────────────────────────────────────┘
```

| | Result |
|---|---|
| tests | **2,494 pass · 6 skip · ⛔ 1 fail — J-07 re-established by Victor, a measured disagreement** (J-07 parked to pending, 2026-09-13) |
| guarantees | **12**, `tools/check_all.py` → ⛔ **2 FAILED** — and both are the SAME fact, not two: *the test suite* and *the suite from a fresh clone* (`DX-5`) each carry `test_ac_5_7_the_golden_set_replays_green`, red since 2026-09-13 because Victor RE-ESTABLISHED the `J-07` value against the recording. ⚠ The other 10 pass. ★ This row read `ALL CHECKS PASSED` until 2026-09-17 and was **stale from the day J-07 went red** — a summary line that outlives its measurement is exactly the defect this table exists to prevent |
| findings | **140 `DX` logged — 130 closed** (✏ 2026-10-02: `DX-140` logged and closed) (+`DX-138` detected, `DX-139` closed) (✏ 2026-10-01: `DX-131`…`DX-137` added; `DX-131` `DX-132` `DX-133` `DX-135` `DX-136` `DX-137` closed) · ⬜ open since: `DX-134` · ⬜ open: `DX-57` `DX-60` `DX-61` `DX-78` `DX-79` `DX-87` `DX-89` `DX-90` `DX-91` `DX-92` `DX-108`(3,4) · ◐ `DX-116` (measured) · `DX-117` (source list) · ✅ `DX-96` closed by `DX-129` (E-09 ran) · ◐ partial: `DX-44` `DX-71` `DX-80` |
| golden set | ⊘ **CLOSED 2026-10-01 (`L8` §9): 53 live, kept and maintained, no new cases; 10 thesis drafts frozen.** ✏ *History below is as of 2026-09-17:* **33 live** (28 extraction · 5 thesis: J-01 ✅ · J-05 ✅ `balance_sheet_resilience@v3` L3 · J-06 ✅ `capital_allocation@v3` L4 · J-08 ✅ · ⛔ J-07 `late` vs recorded `mid` — parked and RE-ESTABLISHED 2026-09-13 by Victor's decision, red on purpose) · every value established by the fund manager. Graded blocks: `E-01` `E-02` `J-01` only. ★ Eight cases were withdrawn and re-established on 2026-09-11 rather than rebaselined |
| recordings | graded: `run-2026-09-11T082002-mu-e01` (E-01 v4) · `…T082118-amd-e01` (E-01 v4) · `…T115548-mu-e02` · `run-2026-09-12T024848-mu-stage-a` (J-01…J-08, complete, envelope-hashed). ⚠ `run-2026-09-12T021719-mu-stage-a` is the TRUNCATED Stage A (`DX-84`) — not promoted, and `spend_report.py` still labels its calls `SUCCESS` because it reports the RUN's close status, not the call's `stop_reason` |
| spend | ★ **measured from traces** (`tools/spend_report.py`): floor **$72.41 over 105 calls** all-time · **$1.17 on 2026-09-17** (`E-09` at effort low $0.4171 — the block that had never completed — then `J-04` $0.7485, the last unscored rubric ⇒ coverage 1.000) · **$3.31 on 2026-09-15/16** (industry evidence: $1.88 on three failed `E-13` attempts, then `J-03` $0.61 + `J-08` $0.81 — the `E-13` itself was REPLAYED free, `DX-123`) · **$16.93 on 2026-09-15** (the first thesis, 4 runs: $2.54 · $2.79 · $6.73 · $4.87 — $5.33 of it lost to three failed calls) · **$0.50 on 2026-09-14** (J-20) · ⚠ one FMP call 2026-09-14 (subscription quota, not in this figure) · **$6.44 on 2026-09-11 · $13.28 on 2026-09-12 · $12.57 on 2026-09-13** (`DX-96` $4.39 incl. E-09 v2 + summarized-thinking diagnostic · J-05+J-06 blind-criteria run $1.72, VOID · criterion-selected re-run $1.69 · k=3 under v3 $4.77) (incl. the seven E-block runs, **$4.74**, of which `DX-96`'s three truncations **$2.64**). ⚠ 3 calls reached the vendor with no tokens recorded, so the console is authoritative. ⚠ A running figure of "$17.16 this session" quoted on 09-12 was **wrong by ~$2.20** — it carried a mis-added base forward; the trace-derived number replaces it. ★ Largest avoidable costs: `DX-84` truncated Stage A **$3.68** · `DX-69` truncated `E-02` **$0.68** · `DX-78` refused `E-02` **$0.67** |
| lint | ruff clean on all code this repo authored |

⚠⚠ **What "148/148" does and does not mean.** Every acceptance criterion has a passing test in the
right tier and every structural AC has a real check. ★ It does **not** mean the system has been run
end to end. ✏ *Updated 2026-10-01:* one `CT-9.2` thesis now exists (MU, k=1 only, so `CT-9.2`'s k=3 is
still unmet), 18 of 20 J-blocks are declared, the golden set grades 7 of 35 blocks, and `F7a`'s one real run returned `INSUFFICIENT` on a test that
`F7a` §8.1 now records as unable to measure what it claims. **The instruments are built and four of
them have now been fired.**

> ★★★ **What 2026-09-11 actually established, and it is not what the day set out to do.** The plan
> was to re-record four calls under the shared envelope and re-point the golden set — understood as
> a mechanical edit. It was not. Of 28 extraction cases only **11 passed as written**, and chasing
> why produced `DX-68` through `DX-75`: an identity resting on a derived date, a promoter that read
> its ticker from a module default, a drift guard pinned to a retired version, a selector weaker
> than the identity it claims to mirror, and a cap nobody had measured the headroom of.
>
> ⚠⚠ **The single most important result is the one that cost nothing:** two AMD runs of the same
> prompt family, 82 minutes apart, differed in whether `qualifier` existed at all (`DX-74`). ⇒
> **run-to-run variance in these blocks is large**, so a single re-record cannot tell a prompt
> regression from noise — and `DX-75`'s 25 % `E-02` drop therefore stays **unattributed**, because
> attributing it would be exactly the unmeasured confident claim this log keeps catching.
> ★ That is a premise the golden set's design had been assuming, and it is now known to be false.

## 2.1b ★★★ 2026-09-11 — the day the golden set was pointed at itself

> **One sentence:** a plan to re-record four calls and re-point the golden set — believed mechanical —
> produced **twelve findings (`DX-68`…`DX-79`)**, cost **$8.61**, and ended with 29 live cases where
> only 11 of 28 had passed at the midpoint. **Not one established value was overwritten by the system.**

### What was actually being done

`DX-67` (2026-09-11, earlier) found that the shared prompt envelope — `S-1`…`S-6`, declared in the
design doc as *"composed into every E-block"* — **had never been implemented**. Every call the project
had ever made went out without it. The envelope was implemented and four calls re-recorded. This
section is what happened when the golden set was asked to accept the new recordings.

### ⓘ The four-line summary of the mechanism

| | |
|---|---|
| what broke | the envelope's `S-2` says **"Do not compute"**, correctly |
| what that suppressed | any value the model would have had to **derive** — and some it only *looked* like it would |
| why it cascaded | `MP-18`'s identity, `F5`'s selector and 17 case selectors all rested on a **derived** field |
| why it was survivable | `D2` had kept the fund manager's values out of the system's reach, so nothing could be quietly rebaselined |

### The findings, and why each was fixed the way it was

| | finding | fix | why NOT the obvious alternative |
|---|---|---|---|
| `DX-68` | `period_start` vanished ⇒ **20 duplicate identities**, result refused | add `cumulative_ytd` to `MP-18`'s identity | reverting the envelope discards `S-3`, the reason for `DX-67`. ★ `AP-5`: **a derived quantity does not belong in an identity** |
| `DX-69` | `E-02` truncated at `max_tokens`, $0.68 wasted | cap 12,000 → 20,000 | ⚠ the retry produced **8,479 — below the cap that truncated it**. So the cap was raised against **variance**, not a larger requirement, and the constant says so rather than claiming evidence it does not have |
| `DX-70` | `promote_recording` wrote `filing.json → MU` for the **AMD** run | derive the ticker from the **recorded bundle** | reading a module global was the bug; a different global would repeat it. ★ Evidence over convention |
| `DX-71` | only **11 of 28** cases passed; re-pointing would rebaseline two regressions | **HELD the re-point**, reported | re-pointing 11 splits the set across two prompt regimes — `DX-67`'s own rejected option |
| `DX-72` | the prompt drift guard pinned **`v2`**, retired since 09-08 | discover every declared version | a hardcoded list reproduces the defect at the next bump |
| `DX-73` | 6 YTD cases assert a start **the filing never states** | `E-01 v4` + fund manager re-established with `start: null` | pushing the prompt harder would train the model to do the arithmetic the envelope exists to stop |
| `DX-74` | `qualifier` **vanished** between two runs 82 min apart ⇒ 4 notes on one selector | teach the selector the **span** `identity` already carried | the docstring claimed *"the selector IS `MP-18`'s identity"* and that was **false** for non-figures |
| `DX-75` | `E-02` lost 25 % of its items | **3 more runs, $2.02** | ⛔ the tidy story (*`S-2` suppressed it*) was **unsupported** — a refusing model records a gap and this one recorded none |
| `DX-76` | the envelope is **unversioned** ⇒ the drift guard is blind to it | `envelope_hash` on `CT-2.2` | `prompt_version` names the block; the envelope is per-block-**independent** |
| `DX-77` | 2 cases pin a **quote boundary** the model chooses | assert the **span**, not the value | ★ the span was identical in **4 of 4** runs; the value text varied |
| `DX-78` | `X-01` refused a whole run over **one capital letter** | recorded, **not fixed** | case-insensitivity weakens the guard everywhere to fix a first-character artefact |
| `DX-79` | which run gets promoted can decide whether a case passes | named, not fixed | ⚠ the pre-registered rule protected against **me** choosing — a different hazard — and left this untouched |

### ★★★ The three that are one finding

`DX-73` (a period start the filing never states) · `DX-74` (a qualifier the model invents) ·
`DX-77` (a quote boundary the model chooses).

> **The golden set kept asserting things the MODEL authors rather than things the DOCUMENT fixes.**
> Those assertions cannot be stable, because nothing external holds them still.

★ `F5` §4's subset rule was already the answer; what these three establish is that it must apply to
**`value` itself**, not only to `quote`/`span`/`note`. ⚠ `DX-79` is the same finding wearing a
different hat: under value-pinning, a case's pass/fail was partly a **coin flip on which run got
promoted** — measured 3-in-4 on one reading.

### ⚠⚠ What went wrong in the WORK, recorded because the log is not a press release

1. **I read "it parses now" as "the problem is solved."** `DX-68`ⓐ was necessary and **not
   sufficient**; 10 cases still failed on a value the fund manager had established, and I moved on
   to re-recording before checking.
2. **I called re-pointing mechanical** and proposed it as a one-line step. It was not: 17 of 28
   cases needed a judgement, and 8 needed the fund manager.
3. **I estimated `DX-71`'s blast radius at "17 case selectors"** from case names. Measured, it was
   **6**. ★ The habit that caught it is the one that keeps working: *measure before specifying.*
4. **I parked 2 cases without re-pointing them**, so a later signature passed against the
   **pre-envelope** recording and settled nothing. Caught only by building `DX-76`'s guard.
5. **I quoted `$1.20` and spent `$2.02`** on `DX-75` — a refused run was still billed.
6. **My own `source` prose was refused by `D2`** for the phrase *"the model's"*. ★ Correctly: the
   guard fired on my writing, not on the fund manager's.

### ★★ What this says about the instrument

**The golden set did the job it exists to do, and the evidence is that it was inconvenient.** It
refused to rebaseline two regressions (`DX-71`), forced eight signed cases back to the fund manager
rather than letting the system edit them (`D2`), and exonerated the envelope on a third
(`DX-75`) — which is the outcome that was *least* convenient to the story I had already half-written.

⚠ It also nearly failed silently in three places, each closed here: a guard pinned to a retired
version (`DX-72`), a selector weaker than the identity it claimed to mirror (`DX-74`), and a prompt
change no version number could name (`DX-76`). ★ **Fourth, fifth and sixth instances of one shape** —
after `DX-41`, `DX-63`, `DX-67`: *a guard keeps checking exactly what it was written to check while
the thing beside it goes unchecked.*

## 2.1c ★★★ WHERE THE BUILD ACTUALLY IS — the block census, 2026-09-11

⚠⚠ **"148/148 ACs" and "all 11 specs complete" are true and they are the wrong number to quote.**
They measure the **platform** — the machinery that runs, records, replays and grades prompts. They say
nothing about how much of the **analytical content** exists, and that is where the remaining work is.

### The measurement

> ✏ **Re-measured 2026-09-13** from `BLOCKS`, every recorded run and both golden files — not from a
> summary. ★ Three columns, because the three moved apart this week: a block can be declared and never
> produce a usable answer.

| | in the design doc | declared in `src/` | **working** — a valid live answer at the shipped version | **graded** — ≥1 golden case |
|---|---|---|---|---|
| **E-blocks** | **15** | **9** (60 %) | **7** (47 %) — `E-01` `E-02` `E-04` `E-06` `E-07` `E-10` `E-12` · ✗ `E-09` truncates (`DX-96`) · ✗ `E-13` wrong subject (`DX-97`) | **2** (13 %) — `E-01` (20 cases) · `E-02` (8) |
| **J-blocks** | **19** | **8** (42 %) | **6** (32 %) — `J-01` `J-02` `J-05` `J-06` `J-07` `J-08` · ✗ `J-03` (needs real E-13) · ✗ `J-04` (needs E-09) | **5** (26 %) — `J-01` `J-05` `J-06` `J-08` ✅ · `J-07` ⛔ disagrees |
| **total** | **34** | **17 — 50 %** | **13 — 38 %** | **7 — 21 %** · 33 live cases, 32 pass |
| ★ **the `CT-9.2` thesis path** (`E-01`…`E-13` + `J-01`…`J-17`) | **30** | 17 — **57 %** | 13 — **43 %** | 7 — **23 %** |

⚠ `J-03`/`J-04` DID answer on 2026-09-12 — but ungated and from a blind integer enum (`DX-85`, `DX-100`), so
those answers are void and are not counted as working.

★ **Declared · schema'd · RUN** are three different things, and the census above measures only the
first. As of 2026-09-12: **17 declared**, **17 schema'd**, **9 run live at least once** (`E-01`,
`E-02`, `J-01`…`J-08` — the last eight in one Stage-A run), **3 covered by golden cases**.

> ✅ **Updated 2026-09-12 — `DX-85`ⓑ closed.** `E-04` `E-06` `E-07` `E-09` `E-10` `E-12` `E-13` declared
> `v1`, text generated from the doc (never retyped), pinned by the drift guard. A new structural test
> asserts **every id a `v2` rubric level cites is emitted by a block declared in `src/`** — against the
> code's registry, not the doc. `MP-5`'s enum check now covers every E-block. **8 mutations, 8 caught**
> after one guard was added (`BLOCKS` version ≠ factory version survived the first pass). All seven
> dry-run; **$0 spent**. ⚠ Pre-flight findings recorded as `DX-89`…`DX-93`; the surviving mutation as `DX-94`. ⛔ `J-03`…`J-06` still
> refuse — `DX-85`ⓒ is now the only structural blocker.

> ✅ **Updated 2026-09-11 — Stage A is complete.** `J-02`…`J-08` declared, verbatim, pinned to the
> design doc by `RA-13`'s drift guard, 15 new structural tests, **4 of 4 mutations caught**.
> ✅ **And now callable** — `DX-81` closed the same day: `judgement_tool` serves all three shapes
> (`enum` · `rubric` · `prose`), `--block` selects any of the eight, and every one dry-runs.
> ⬜ `DX-82`: `RA-32`'s evidence-gating of rubric levels is deliberately still open and **warns out
> loud** on every rubric call rather than defaulting quietly.

★★★ **The single most important fact for planning: every one of the 34 already has its prompt text
written in `L1-fundamental-analysis-master-prompt.md`.** The remaining work is **transcription,
wiring and verification** — not authoring, not design. ⚠ This corrects `DX-64`'s framing, which read
as though the J-blocks needed to be invented.

### What one block costs, measured on the three that exist

Per block: the text constant (verbatim) · an item-id enum or option list · a factory · a `BLOCKS`
entry · a drift test pinning it to its doc section · and — only if it is to be **graded** — a live
recording (~$0.55-0.70) plus golden cases the fund manager establishes.

⚠ `e_blocks.py` is **325 lines for 3 blocks**, but most of that is `DX` commentary, not mechanism.

### ⚠ Two honest qualifications

- **`STAGE_BLOCKS` names J-01…J-17; the doc defines J-01…J-19.** Not a defect: `J-18` (pre-event
  brief) and `J-19` (industry-vs-company attribution) were added for the **event and attribution
  workflows**, not for the `CT-9.2` thesis pipeline. ★ They are real work, outside the thesis.
- **Declaring a block is not the same as covering it.** The golden set grades **3 of 34** blocks.
  Coverage is the expensive half, because it needs a live call **and** the fund manager's time.

### ⬜ The order this should be built in, and why

1. ✅ **`J-02`…`J-08` DECLARED and ✅ SCHEMA'D — 2026-09-11.** Seven blocks verbatim under the drift
   guard, plus three answer shapes in `judgement_tool` (`enum` · `rubric` · `prose`) and a `--block`
   flag. **All 8 Stage-A blocks dry-run.** ⬜ Not yet RUN live, and `DX-82` (`RA-32` level gating)
   is open.
   ★ **Next concrete step: run Stage A once, on MU.** 8 blocks × 1 run ≈ **$3.1** at the measured
   $0.39/call — the first time this project would hold a complete Stage A rather than one block of
   it. ⚠ `K_RUNS`=3 makes it ~$9.4; **k=1 first** is the cheap-test-before-the-expensive-one habit
   that has paid off four times (`DX-31`, `DX-55`, `DX-57`, `DX-75`).
2. ✅ **DECLARED 2026-09-12 (`DX-85`ⓑ).** ⚠⚠ **CORRECTED 2026-09-12 (twice) — `E-04` · `E-06` · `E-07` · `E-09` · `E-10` · `E-12` · `E-13`
   come BEFORE Stages B-D.** `DX-85` measured that `J-03`…`J-06` cannot be scored at all until the
   evidence their `v2` levels cite exists: `ng.adjustment` (`E-04`), `dm.ladder`/`dm.covenant` (`E-06`),
   `ca.capex` (`E-07`), `ap.change` (`E-09`), `sc.diluted`/`sc.sbc_expense` (`E-10`), `cp.statement`
   (`E-12`), `cx.capacity` (`E-13`). ⚠ The first version of this line named `E-05` (cited by no level)
   and missed `E-09`/`E-10`/`E-12` — it was written from the `E` dict, not from what the LEVELS cite. ★ Declaring more J-blocks first would add more blocks that cannot be answered — the
   earlier plan had this backwards, and only wiring `RA-32` revealed it.
3. **`J-09`…`J-17`** — Stages B-D. Completes a `CT-9.2` thesis: **17 blocks × `K_RUNS`=3 = 51 calls**,
   which is also what finally prices `QR-20` (`DX-60`).
4. **the remaining `E-blocks`** — `E-03`, `E-05`, `E-08`, `E-11`, `E-14`, `E-15`. ★ Cheapest per block and
   lowest risk: the pattern is proven twice and `X-01` already backstops them in code.
5. **`J-18`, `J-19`** — only when the event/attribution workflows are being built.

⚠⚠ **Do not grade every block.** 34 blocks × a live recording × the fund manager establishing cases
is the most expensive thing in this plan, and `D2` makes his time the binding constraint, not money.
★ The `DX-77`ⓒ lesson applies directly: assert what the **document** fixes, and a case survives
re-recording instead of needing re-establishment each time.

## 2.1d ★★ 2026-09-11/12 — Stage A declared, schema'd, and run

### What exists now that did not this morning

| | |
|---|---|
| `J-02`…`J-08` | declared verbatim, pinned to the design doc by `RA-13`'s drift guard |
| `judgement_tool` | **three** answer shapes (`enum` · `rubric` · `prose`), was one |
| `--stage-a` | runs all 8 Stage-A blocks into **one** `run_id` and trace |
| `GW-23` on judgement | a truncated response is now refused on a path that never reaches the Gateway |

### ⚠⚠ The expensive lesson: `DX-84`

**The first Stage-A run reported `8/8 block(s)` and 7 of the 8 were truncated.** $3.68 spent,
$3.22 of it unusable. Two causes, both real:

1. **The judgement path never reaches `Gateway.call`**, so `GW-23` — the check that had caught
   `DX-69` on the extraction side **three hours earlier the same day** — did not exist here at all.
2. **`MAX_OUT = 4_000`** was a THIRD output budget, *smaller than either already declared*
   (`call.py`: 20,000 / 16,000), living in a runner nobody had diffed against them.

★★★ **The re-run measured what 4,000 was actually costing.** Untruncated, the rubric blocks want
**9,322 – 13,516** output tokens:

| | `J-01` | `J-02` | `J-03` | `J-04` | `J-05` | `J-06` |
|---|---|---|---|---|---|---|
| out (untruncated) | 5,416 | 3,224 | 11,272 | 10,681 | 13,516 | 9,322 |
| under the old cap | 4,000 ⛔ | 3,391 ✅ | 4,000 ⛔ | 4,000 ⛔ | 4,000 ⛔ | 4,000 ⛔ |

⇒ the rubric blocks were being cut off at roughly **a third of their answer**. ⚠ And the cost
estimate for a Stage A was wrong in the same direction: **~$4.7, not ~$3.7**, because the $0.46/call
figure came from measuring *truncated* calls. ★ A price measured on a broken run is a broken price.

### ★★ Why it was not caught by anything

`J-02` — the one block that fit in 4,000 — returned cleanly, so the run had a plausible-looking
member. The other seven returned **valid JSON that parsed**: `J-01` parsed and was simply *missing
its required `why`*. ⚠⚠ **"It parsed" is not "it is complete"** — the same mistake `DX-68` taught
about *"it parses now"*, recurring nine hours later on a different path.

⚠ It reached a **signed golden case**: the thesis case had been re-pointed onto
`run-2026-09-11T111240-mu-j01`, which is also truncated. It passed throughout, because `F5` §4's
subset rule means it asserts only `archetype`. ★ That is the subset rule earning its keep — and not
a reason to keep grading a degraded call. Re-pointed back to the only complete `J-01` recording.

### ✅ The re-run — the first complete Stage A this project has produced

`run-2026-09-12T024848-mu-stage-a` · **8/8 `tool_use`, no truncation, every required field present** ·
**$4.8646**

| block | shape | answer | out |
|---|---|---|---|
| `J-01` | enum | `archetype = cyclical_commodity` | 5,416 |
| `J-02` | prose | 3,907 chars + `what_i_do_not_understand` | 3,224 |
| `J-03` | rubric | `moat_durability = 1` — *"the moat is a story about a moat"* | 11,272 |
| `J-04` | rubric | `earnings_quality = 3` | 10,681 |
| `J-05` | rubric | `balance_sheet_resilience = 3` | 13,516 |
| `J-06` | rubric | `capital_allocation = 0` — *"the bundle does not disclose capital-allocation actions"* | 9,322 |
| `J-07` | enum | `cycle_position = mid` | 12,092 |
| `J-08` | prose | `supply_read = insufficient_evidence` | 13,291 |

★ `J-01` agrees with all three prior runs and with the fund manager's own view.
★ `J-06 = 0` and `J-08 = insufficient_evidence` are the floors **used as designed** — `MP-7`/`S-4`,
a block that can say *"I could not"* rather than inventing something.

> ⚠⚠⚠ **`PG-10` — NONE OF THESE FIGURES IS VERIFIED, and none may be quoted as a finding about
> Micron.** Zero golden cases grade `J-02`…`J-08`; `D2` reserves establishing them to the fund
> manager. ★ `J-06 = 0` is the one to distrust first: the MU 10-Q **does** disclose a declared
> dividend and buyback activity, so a floor score there is a claim worth checking before it is
> believed. ⚠ And `RA-32` is ungated (`DX-82`) — every level was selectable regardless of whether
> its `evidence_required` was present.

★ `J-01` from this run is complete, post-envelope and hashed, so the **thesis golden case moved onto
it** — resolving `DX-84`'s forced choice between a complete pre-envelope answer and a truncated
post-envelope one. The established value is unchanged; only the artefact moved.

### ⬜ What Stage A still is NOT

- **Not covered.** Eight blocks have run; **zero** have golden cases. A run is evidence that the
  pipe works, not that the answer is right — and `D2` reserves the second to the fund manager.
- ⛔ **Not SCOREABLE at all** (`DX-82` closed → `DX-85` opened). `RA-32` is now applied, and it
  **refuses all four rubric blocks**: zero levels are available from a bare-filing bundle. ★ The four
  scores the 2026-09-12 run produced (`moat=1 · earnings=3 · balance=3 · capital=0`) rest on nothing
  structural and may not be quoted (`PG-10`).
- **Not k=3.** `K_RUNS`=3 is what `CT-9.2` requires; this is k=1.
- **Not a thesis.** Stage A is 8 of 17 blocks. Stages B-D (`J-09`…`J-17`) are undeclared.

## 2.1q ★★ 2026-10-01/02 — `J-09`'s governing inputs: consensus and duration supplied, one cap ruled out

> **$0 API** (subscription). FMP calls standing-approved (fixed-rate). Detail in §2.1p item 5.

### What exists now

| | |
|---|---|
| consensus | FMP `grades` + `price-target-news` + `earnings`, version-controlled fixtures with provenance; a `consensus.as_of` bundle part cut at the as-of **market close** (1b), past estimates with a revision caveat (2a); its arithmetic in D-02 (`src/feature_engineer/consensus.py`, `AC-1.40`). Daily `analyst-estimates` snapshot tool built — ⚠ writes to gitignored `.state/` and is not scheduled |
| price requirement | **F10 amended** (`D10`, `AC-F10.22`): `dcf_two_stage@v2` = `v1` + a 5 / 7 / 10 / 15-year duration table + market capitalisation. MU: no root at 5 y · 39.0 % at 7 · 28.3 % at 10 · 20.5 % at 15; market cap $141.75bn |
| runner | `--stop-after BLOCK`; absences dropped per bundle only when the part really supplies them |
| `J-09` | re-asked (`run-2026-10-01T225847`): consensus position **stated**, duration requirement **decided** (`required_more_than_evidenced`), still `insufficient` on gross capex (a declared limit) and implied margin (curable) |
| `DX-140` | ✅ ruled ⓑ: a requirement unset only by a DECLARED known limit is stated on the thesis (`limitations_stated`), not counted toward the cap |
| thesis | ⏳ `--resume-from run-2026-10-01T225847-mu-thesis` → `run-2026-10-02T113055-mu-thesis`: J-10…J-14 committed (9 calls, ~1.6M input tokens), then ⚠ **the subscription session limit stopped J-15** (`TransportError`, no partial commit — `P5`). Resumed after the reset from `…113055` (10 commits carried, hashes verified) → J-15…J-17 only |
| ★★ result | **`run-2026-10-02T173511-mu-thesis`: HOLD · Low** (authored HOLD / Medium; capped by 2 governing absences — `J-08` competitor capacity, `J-09` implied margin). `limitations_stated`: the gross-capex base (`DX-140`). 4 falsifiers (J-15 v2, tests model-authored), 12 data gaps. $0 API (notional ≈$13.5 over 13 calls) |

### ★★ The second MU thesis: SELL → HOLD, and what its own falsifiers say

| | 2026-09-15 (no consensus, no duration) | 2026-10-02 |
|---|---|---|
| verdict | **SELL** · Medium → Low | **HOLD** · Medium → Low |
| why | price needs 28.3 %/10 y, unmatched by the record | same requirement, but the base is understated by a DECLARED limit (gross capex), so the $15.96-vs-$126 gap is *"a data gap rather than a measured mispricing"*; supply unmeasured, so it *"cannot assert the upcycle ends sooner than consensus assumes"*; earnings quality and balance sheet defeat the exit case |
| falsifiers, checked on later EDGAR quarters | #1 #2 **FIRED** · #3 #4 HELD → wrong | #1 HELD (final, past deadline — revenue grew, so the "margin without growth" test cannot fire) · **#2 FIRED** (OCF − gross capex summed far above $8bn at the full capex pace: *"the base figure the whole price argument turns on is wrong by roughly six times"*) · #3 #4 **PENDING** (4 of 8 and 4 of 6 quarters reported, every one so far on the firing side) |

★ **Less wrong, not right.** HOLD did not sell into the rally the SELL missed, but its own #2 says its
bear-leaning reasoning rested on the wrong base, and #3/#4 are on course to fire. ⚠ **k=1, and the
change is not yet attributed:** the old bundle's SELL repeated 3/3 (item 4), so a move to HOLD on the
new bundle is *probably* the new inputs and not noise — but `agreement_probe` on the new `J-16` (2 calls)
is what would show it (`MOVED` needs both arms unanimous).
✅ **Probed 2026-10-02** (`run-2026-10-02T193942-agreement-j16`, noise floor, k=3, 2 new calls on the
subscription, requests byte-identical to the recorded one): **verdict SPLIT — HOLD 2 · SELL 1**;
conviction Medium 3/3 (before the cap); considerations 3/3. ⇒ Against the old bundle's SELL 3/3, the new
inputs moved the verdict **onto the SELL/HOLD boundary**, not cleanly to HOLD. By the pre-registered rule
this is not a `MOVED` (that needs both sides unanimous), and the thesis's HOLD is the modal answer of an
unstable call. ⚠ The probe printed "~106,044 input tokens each" — its pre-send ESTIMATE; measured was
242,520 and 487,622 (two CLI turns), so nothing was dropped.
⚠ Rule checks over the three runs: **`DX-141`** — `J-11` quoted *"Construction in progress | 4,937 |
3,444"*, dropping the footnote marker `(2)` it quoted verbatim elsewhere (content-faithful, not
verbatim; not registered in `rule_checks.KNOWN`, which covers promoted recordings only) · the J-15 call
the session limit killed is flagged `incomplete-call` (correct; nothing was committed from it).

### ★★ The third MU thesis (2026-10-03): consensus + duration + D11 + F11 base rates — SELL again

`run-2026-10-03T002642-mu-thesis` (stopped by the session limit at `J-13:operating_margin`, 5 commits) →
resumed as `run-2026-10-03T125303-mu-thesis` (5 carried, hashes verified; 8 sent). $0 API, subscription.

| | 2026-09-15 | 2026-10-02 | **2026-10-03** |
|---|---|---|---|
| inputs added | — | consensus · duration table | + D11 margin share · **F11 base rates** · longer MU history |
| verdict (authored) | SELL / Medium | HOLD / Medium | **SELL / Medium-High** |
| conviction (capped) | Low (3 absent) | Low (J-08, J-09) | **Low — 1 absent: `J-10`** |
| J-09 price requirements | 1 decided of 3 | 3 of 4 | ★ **4 of 4 `required_more_than_evidenced`** |
| J-10 | INSUFFICIENT | INSUFFICIENT | ★ **cites the base rates**: 0/21 member-years at the required margin, 0/6 runs ≥ 7 y, 0/2,886 in the book |

★ **What the base rates changed.** J-16's first consideration is now *"every duration the price can be solved
at requires an FCFF margin … that no member-year in the reference class reaches — 0/21"*, and J-10 adds its
own honest qualifier: *"the zeros are weaker than they look … they establish absence of precedent, not
impossibility."* ⚠ The 2026-10-02 HOLD rested on the gross-capex limit making the gap "a data gap"; this run
answers it directly — *"even a doubled base leaves the 7-year requirement above every observed member-year."*

⚠⚠ **Its falsifiers, checked on later EDGAR quarters — and a checker reading that is wrong (`DX-144`).** As
written, `check_falsifiers` reports #1 #2 #3 **HELD** and #4 PENDING. But each condition says *"in each of
four (eight) CONSECUTIVE reported quarters"* with deadlines in 2027, and the model's structured tests use
mode `each` over the FIRST window instead of `consecutive` — so one weak first quarter "settles" a test the
deadline has not reached. Read as the sentences say:

| # | Condition | Later quarters | As the sentence reads |
|---|---|---|---|
| 1 | OCF − capex > $1.5bn, 4 consecutive quarters | 0.07 · 3.0 · 5.5 · 17.6 ($bn) | **PENDING — 3 consecutive; one more quarter fires it** |
| 2 | gross profit > COGS, 4 consecutive | GP < COGS in Q1, then 7.6/6.0 · 17.8/6.1 · 35.1/6.4 | **PENDING — 3 consecutive; one more fires it** |
| 3 | capex < $2bn with OCF > $4bn, 4 consecutive | capex 5.7 · 5.4 · 6.4 · 7.8 | not firing |
| 4 | net income > $2.5bn, 8 consecutive | 3.2 · 5.2 · 13.8 · 28.2 | **PENDING — 4 of 8, all firing** |

⇒ ★ **This SELL is on course to be falsified by its own conditions, like the first one.** Three runs, three
verdicts (SELL → HOLD → SELL) over materially the same evidence plus added inputs, and every verdict's
falsifiers point the same way: the cash generation the price required arrived.

⚠ Rule checks over both runs (after a checker fix below): the session-killed call (correct) · **`DX-145`**
J-13 (`return_on_equity`, `operating_margin`) quoted NAND as *"plus low-50%"* — the filing says *"plus
low-30%"* — **the `DX-138` misquote again, in two more answers** · J-13 `non_gaap_eps` quoted 2 of a 4-column
table row (`DX-141`'s class). ✅ Checker fixed: the computed sections F11 and the consensus part add
(`MARGIN REACH`, `REFERENCE-CLASS`, `PUBLISHED`, `CONSENSUS`…) were being checked against the FILING; now
exempt like D-02's (7 new tests).

✅ **2026-10-03 — `DX-144` ⓐ, `DX-145` ⓐ, `DX-146` ⓑ ruled and built** (details in §6). ⚠ Was: **The remaining cap is `J-10`'s, and it is `DX-140`'s shape again (`DX-146`).** `derate` flags J-10 when ANY
claim lacks a base rate. The price-requirement claims now have them; three secondary claims do not —
terminal growth in perpetuity, J-07's "mid" cycle read, and FY2025 capex guidance — and no reference class
this system can build answers "perpetuity survival". ⬜ **Victor's ruling.**

### ⛔ 2026-10-04 — the J-15 re-ask: refused by `DX-144`, as predicted

`--resume-from run-2026-10-03T125303-mu-thesis --resend-from J-15` → `run-2026-10-04T024042-mu-thesis`.
J-09…J-14 carried (10 commits, every hash re-verified against today's bundle); J-15 sent once on the
subscription ($0 API). ⚠⚠ **`RES.THESIS.NO_FALSIFIER`** — falsifier 1: `window_periods 4 ends before the
deadline 2027-07-01: ~7 quarters will have reported by then`. J-16 and J-17 NOT issued (`RA-16`); no thesis (`P5`).

| # | Condition (new authoring) | Deadline | Test as written |
|---|---|---|---|
| 1 | OCF − capex > $2.0bn, 4 consecutive quarters | 2027-07-01 | `each`, window 4, stray `consecutive: 4` |
| 2 | gross profit ≥ $3.5bn and revenue ≥ $9.3bn, 4 consecutive | 2027-07-01 | same shape |
| 3 | capex < $2.5bn with OCF > $4.0bn, 4 consecutive | 2027-07-01 | same shape |
| 4 | net income ≥ $1.5bn, 8 consecutive | 2028-01-31 | `each`, window 8 (≈9–10 due) |

★ The conditions are sharper than the 2026-10-03 set (thresholds moved up), and the model clearly MEANT
*consecutive*: it wrote the count into each clause. ⚠ But it used mode `each` (where that count is never read,
`DX-147`) over a window that stops a year before the deadline. ⇒ Exactly the case §6 `DX-144` predicted: the
prompt does not state the window rule, so the authoring cannot satisfy it except by luck.
Rule checks on the J-15 call: **0 violations**. Runner: `--resend-from BLOCK` added (carries only the commits
BEFORE the block; 1 test, mutation caught). ✅ `DX-147` ⓐ built the same day. Suite 2,496 pass / 1 deliberate red (`J-07`).
✅ **Victor approved J-15 v3 the same night** (two sentences: the window must reach the deadline; a run of quarters
is mode `consecutive`). Built in the L1 master prompt (0.5.0) and `e_blocks.py` (drift guard green); the
tests file now records the version that wrote it.

### ★★ The fourth MU thesis (2026-10-04): J-15 v3 — SELL / Medium-High, the first uncapped, and already falsified

`--resume-from run-2026-10-03T125303-mu-thesis --resend-from J-15` → **`run-2026-10-04T031717-mu-thesis`**.
J-09…J-14 carried (verified); J-15 v3 → J-16 → J-17 sent ($0 API; notional ≈$5.38).

| | |
|---|---|
| verdict | **SELL** · authored SELL / Medium-High · **conviction Medium-High** — coverage 1.00, governing absences **0** (first MU thesis with no cap) |
| why (J-16) | *"SELL at $126.00, on price rather than on business quality"* — earnings quality clean; the price needs FCFF at 40.1–65.3 % of revenue vs a best year of 28.5 %, 0/21 member-years in the class; the whole 12-cell grid ($10.76–$22.50) is ~⅕ of price. Medium-High, not High: HBM economics, net-of-incentive capex and peer figures absent |
| `limitations_stated` | 3, all `DX-146` ⓑ: J-10 has no base rate for terminal growth in perpetuity · J-07's "mid" cycle read · FY2025 capex ≈ $14bn net of incentives |
| falsifier tests | all four mode `consecutive`, windows 8 / 10 / 6 / 8 reaching their deadlines — ★ `DX-144` and `DX-147` both satisfied on the first v3 authoring |
| rule checks | the 3 new calls: **0 violations** (the 4 on the carried runs are the known 2026-10-03 ones) |

⚠⚠ **Falsifiers, checked 2026-10-03 on later EDGAR quarters: 2 FIRED, 2 PENDING on course to fire.**

| # | Condition | Deadline | Status |
|---|---|---|---|
| 1 | OCF − capex ≥ $3.0bn, 6 consecutive quarters | 2027-07-01 | PENDING — 0.07 · 3.02 · 5.5 · 17.6 ($bn): 3 consecutive so far |
| 2 | OCF > capex, 8 consecutive quarters | 2028-02-01 | PENDING — 4 of 4 so far |
| 3 | gross profit ≥ COGS, 3 consecutive quarters | 2027-01-15 | **FIRED** |
| 4 | revenue ≥ $14.0bn and operating income ≥ $5.0bn, 2 consecutive | 2027-07-01 | **FIRED** — revenue $23.9bn, $41.5bn |

⇒ ★★ **Four theses, four verdicts falsified or on course (SELL → HOLD → SELL → SELL).** The v3 falsifiers are
sharper and correctly windowed, and the checker now decides them as their sentences read — and they say the
thesis is wrong: the scale the price required arrived within a year. ⚠ The most confident MU thesis so far
(Medium-High, uncapped) is the most clearly falsified one. k=1. ★ This is the measurement `L8` §9 exists for:
conviction rose with evidence coverage, and correctness did not.
⚠ J-16 reports a frozen-record inconsistency it found itself: Stage B/C answers say *"nine usable years"* where
the annual-history block gives 13, and *"five sign changes"* matches neither window. **Unverified** — worth a
look before it is registered.

### ★★ Retrospective, 2026-10-03 — the falsifier loop after three theses

1. ★★ **Falsifiers are the instrument that keeps being right.** Three MU theses (SELL → HOLD → SELL)
   over a growing bundle; each one's own conditions point the same way on Micron's later filings — the
   cash generation the price required arrived. Stability (3/3 SELL, then a split) and a full scorecard
   never said so; falsifiers did.
2. ⚠⚠ **Sentence ↔ test fidelity cannot be checked by eye.** It held on 2026-10-01 and failed on the next
   authoring (`DX-144`): *"consecutive"* written, `each` over the first window tested. It is now a
   validation rule, not a reading.
3. ★ **Every cap rule written so far became a constant within one iteration** (`DX-140` J-09, `DX-146`
   J-10). The pattern: an "any row/claim lacks X" rule meets a row no input can cure. ⇒ A new cap rule
   should state, when written, which absences it can be cured by.
4. ⚠ **Paraphrase-from-memory errors recur on the same sentence** (`DX-138` → `DX-145`): two adjacent ranges
   sharing "low-50%". Caught every time by the rule check; accepted as caught.
5. ★ **The subscription session limit is a real pace constraint** — two of three theses were stopped
   mid-run; `--resume-from` made both stops free. Plan theses as two sittings.
6. ★ **Reference classes are as wide as their tags** (`DX-143`): 4 members gave 21 usable member-years
   only after a revenue fallback; old SanDisk stays out. Every rendered rate carries its `n`.

### ★ Retrospective — what this stretch taught

1. ⚠⚠ **The usage limit hit with the suite red, and the interim commit captured it.** The `AC-1.40`
   failure (`.median()` in D-01) was found by the last suite run before the cutoff and committed
   unfixed. ⇒ Run the whole suite **before** reporting a sub-step done, not after the next one starts.
2. ⚠ **My first answer to item 5 misnamed the gap.** I said `J-09` lacked market cap and multiples; the
   recorded answer showed the binding row was **duration**. Reading the answer cost one command and
   redirected the F10 amendment. ⇒ Read the recorded output before proposing what would fix it.
3. ★ **The spec-first rule held under time pressure.** F10 had no AC for a duration figure, so the
   amendment came first and Victor chose the periods; the traceability guard (169 → 170) failed exactly
   as designed when the AC was added. 5 of 5 mutations caught.
4. ★★ **`DX-140`: an absence rule must know whether the absence is curable.** A cap keyed to
   *"any row insufficient"* became a constant for MU, because one row rests on a limit F10 already
   declares uncomputable. The fix states it on the thesis instead of counting it.
5. ⚠ **The subscription's usage limit is now the pace constraint, measured:** one Stage B–D thesis is
   ~13 calls of 170–300k input each; on the Pro plan it did not fit in one session window. `--resume-from`
   made the stop free (nothing re-sent). ⇒ Plan theses as two sittings, or `--stop-after` at a natural break.
6. ⚠ **`DX-12`'s shape, fifth sighting:** the analyst-estimates snapshot writes under gitignored
   `.state/`. Forward-consensus history not kept somewhere durable is unrecoverable.
7. ★ **Stability is not correctness** (item 4): MU's SELL repeats 3/3 and is falsified by its own
   #1/#2. Falsifiers stay the primary instrument (`L8` §9).

### ⬜ What next — in order

| # | Work | Who | Cost |
|---|---|---|---|
| **a** | ✅ Read the resumed thesis (above). ✅ J-16 probe: verdict SPLIT HOLD 2 / SELL 1 — the move is to the boundary | agent | done |
| **b** | ✅ **`J-10` base rate — `F11` approved and BUILT** (2026-10-02): `memory@v1` (MU · SanDisk pre-2016 + 2025 · WDC FY2017–2025), capex fallback `PaymentsToAcquireProductiveAssets` (`fundamental` → v4), *The Base Rate Book* (2016) Exhibit 4 + appendix transcribed by script with pages, overlapping windows labelled. 9/9 ACs, 9/9 mutations caught; members ingested from EDGAR and promoted to `tests_src/fixtures/edgar/reference_class/memory_v1/`. ★ **MU as of 2025-06-26:** FCFF margin ≥ the required 40–65 % in **0/17** member-years (0/8 without MU); a positive-FCFF run of ≥ 7 years **0/3**; the book: ≥ 25 % real sales CAGR over 10 years in **0/2,886** for starting sales > $25bn. ⚠ **`DX-143`** — the class is thinner than its members | done | — |
| **c** | ✅ **Implied margin — `F10` `D11` built** (2026-10-02): required final-year FCFF and its share of trailing revenue per duration row; MU needs **40.1 % / 48.1 % / 65.3 %** at 7 / 10 / 15 y against a best year of 28.5 %. `implied_margin` no longer declared absent. 4 tests, 4/4 mutations caught | done | — |
| **d** | ✅ **Snapshot** (2026-10-02): tracked `snapshots/analyst-estimates/`, tickers in `config/snapshots/`, systemd user timer weekdays 18:30 New York (`Persistent=true`), examples in `deploy/`; first timer run wrote MU + AMD. ⚠ `Linger=no`: runs only while Victor is logged in; a missed day catches up at next login | done | — |
| **d′** | ✅ Re-asked (3rd thesis 2026-10-03; J-15…J-17 again under v3 → 4th thesis `run-2026-10-04T031717`, SELL / Medium-High, #3 #4 FIRED) | agent | done |
| **e** | Then §2.1p's table rows **6–10**: 8 undeclared blocks · `DX-76` envelope versioning · AMD thesis end to end · quant ~30 % → done · go-live (`MS-0`) | agent, with Victor's reviews | ~15–25 sessions |

## 2.1p ★★ 2026-10-01 — the golden-case programme is CLOSED; what replaces it, and what is left

> **Decision by Victor** (`L8` §9): no golden case is developed from today. Extraction is finished at the
> 48 signed cases (9 of 15 E-blocks), thesis cases are frozen (5 signed live, 10 drafts kept unsigned),
> and **judgement quality moves to falsifiers and rule checks.** Nothing is deleted.

### Why, in one line each

The replay grades stored answers, so it cannot judge a prompt change. Every thesis is k=1, so a red
case cannot separate a worse prompt from a different draw. A judgement case measures agreement with one
reader (`J-07`). And the one failure that mattered (the MU thesis falsified by its own conditions) was
invisible to every golden case. Full reasoning: `L8` §9.

### What replaces it

| Instrument | Answers | Exists today | To build |
|---|---|---|---|
| **Falsifiers** (`RM-13`) | *was the thesis wrong by its own stated conditions?* | ✅ `tools/check_falsifiers.py --tests`, hand-written tests for MU (`config/falsifiers/mu-2025-06-26.json`): #1 #2 FIRED | ⬜ `J-15 v2` emits the structured test itself, so every thesis is checkable without hand translation; ⬜ a runner that re-checks open theses when new filings land |
| **Rule checks** (invariant tier, constitution §4) | *does every call obey the rules, whatever it answers?* | ◐ in pieces: `X-01` quote checks, `DX-131` date guard, truncation refusal (`DX-133`), drift guard | ⬜ one suite over EVERY recording: no leaked tool syntax (`DX-134`), refuse on a declared-absent input (`J-09`/`J-10` shape), every cited figure resolves, every required field present |
| **Agreement across runs** | *did a prompt change move the answer, or was that noise?* | ⛔ `thesis/gate.py::_agreement` returns `None` at k=1 and the gate then PASSES (`L8` §8.8) | ⬜ the gate FLAGS at k=1; ⬜ a k=3 probe run on the subscription for any prompt change |

### ★ Remaining work — the whole build, re-estimated 2026-10-01

API dollars are no longer the unit (development is on the subscription, `GW-24`). The units are
**sessions** of agent work, **hours** of the fund manager's time, and **subscription usage**.

| # | Work | Agent | Victor | Subscription |
|---|---|---|---|---|
| **1** | Rule-check suite over all recordings + `DX-134` guard | ~1 session | — | none |
| **2** | k=1 gate flags instead of passing | <1 session | — | none |
| **3** | Falsifier loop: `J-15 v2` structured tests, auto-check | ~1–2 sessions | ~1 h (check the 4 MU readings, then each new set) | 1 thesis re-run (~13 calls) |
| **4** | k=3 agreement probe | <1 session | — | ~26 calls per probe |
| **5** | ★ `J-09`/`J-10` governing inputs (consensus, price requirement, base rate): the only thing that can lift Low conviction | 2–4 sessions | ✅ source decided 2026-10-01 (FMP `grades` + `price-target-news` + `earnings`; published base-rate study first). ⬜ name the reference class | small |
| **6** | 8 undeclared blocks (`E-03` `E-05` `E-08` `E-11` `E-14` `E-15` `J-18` `J-19`) + `J-13`'s 6th metric | 2–3 sessions | review | ~10 calls |
| **7** | `DX-76` envelope versioning + the "both period endpoints" wording | <1 session | — | re-record of affected blocks |
| **8** | Second ticker end to end (AMD thesis), judged by rule checks and falsifiers | 1–2 sessions | ~2 h | ~25 calls |
| **9** | Quant domain, ~30 % → done: factor construction, retrain cadence, regime handling, nomination pipeline, `DX-62`, `AB-16` | ⚠ the largest block: ~8–15 sessions | design decisions | none |
| **10** | Go-live (`MS-0`): API spot-check of the 53 live cases, transport switch, budget, `MS-8.9` retire upstream | 1–2 sessions | the switch, the budget, retiring the old repo | ⚠ the first paid API calls since 2026-09-17 |

⇒ **Roughly 18–30 agent sessions**, with quant ~half of it, and **~5–10 h** of the fund manager's time,
most of it decisions rather than reading. ⚠ Ranges, not commitments: the last estimate this file made
for the golden programme was revised twice inside one day.

### ✏ Same day — item 1 BUILT: `tools/rule_checks.py` ($0)

Four rules over every recorded call: **leaked tool syntax** (`DX-134`), **incomplete call** (truncated or
empty, `DX-133`), **quote not in source** (every `FACT [...] "…"` attributed to the filing must be in it,
compared on letters and digits so layout does not count, with `...` abridgement allowed and non-filing
sources exempt), and **absent input not refused** (`J-09` must answer `INSUFFICIENT_EVIDENCE` while
consensus is declared absent; a `J-10` base rate must be declared absent or cite a `FACT`, so the
company's own history is allowed and an invented rate is not). Absences are read from the run's own
bundle (`DECLARED ABSENT INPUTS`), falling back to `STAGE_B_ABSENCES` for promoted recordings, which
elide the bundle.

★ **First run: 45 calls, 4 violations, all now explained in `rule_checks.KNOWN`**: `DX-84` (the old
truncated `J-01`), `DX-134` (`J-11`'s leaked tag), and **`DX-138`, new**: `J-03` quoted a NAND price
range with a changed number. ⚠ A first draft of the `J-10` rule was itself wrong (it flagged Micron's
own history used as a base rate) and was corrected before anything was recorded. Wired into
`check_all.py` as guarantee 13. Tests: 14 unit (each rule fires and stays quiet) + 2 structural (the
recordings hold exactly `KNOWN`, and a fixed violation must be removed). Suite 2,354 pass · 1 deliberate
red (`J-07`).

### ✏ Same day — item 2 BUILT: an unmeasured verdict FLAGS (`RA-154`, $0)

⚠ **A spec-vs-code defect, not only a code one.** `L1-fundamental-analysis` §11.2's PASS row already
required a **stable** verdict, and RA-49 says *"a state with no row is a defect, not a default to
PASS"*, yet `thesis/gate.py` mapped `agreement is None` to PASS. Every k=1 thesis therefore passed the
stability check by absence of evidence. ★ Spec amended first (v0.26.0, **RA-154** and a new §11.2 row),
then the code: no RM-1 result, or `k < K_STAB`, is **unmeasured** and FLAGs. It does not VETO, since
RA-48 reserves that for a verdict shown not to reproduce. A fired falsifier still VETOes over it
(RA-135). ⓘ The downstream backstop (`assert_actionable_inputs`, RP-13) already refused an
unmeasured verdict on the actionable path; what changes is that the gate's own record no longer says PASS.

⚠ **One inherited test changed, and why:** `test_ac_1_84_a_stale_relay_sourced_thesis_flags_at_the_gate`
used *"fresh relay thesis → PASS"* as its control. A relay thesis carries no stability by RA-115, so it
is unmeasured and now FLAGs. RA-115 already says the relay *"can inform, gate and populate the card"*
but never be the actionable pick, so FLAG is consistent with it. The control now asserts what AC-1.84
is about: the **stale** reason is present when stale and absent when fresh. Tests: 6 new
(`tests/unit/test_gate_unmeasured_stability.py`). Suite 2,360 pass · 1 deliberate red (`J-07`).
⓪ MU is unaffected: its thesis is SELL, which VETOes on its own row.

### ✏ Same day — item 4 BUILT: `tools/agreement_probe.py`, did a prompt change MOVE the answer? ($0)

Re-sends ONE recorded call k times per arm. Arm A is the prompt as recorded (the recording counts as one
of k); arm B swaps the block's old text for its new text, exactly once, with bundle, model, effort and
`max_tokens` identical. It compares **decision fields only**: enums, booleans, numbers and list lengths,
never prose. `--noise-floor` runs arm A alone, to measure one prompt's own spread.

★ **The rule, fixed before any run:** `SAME` if the modal answers agree; **`MOVED` only if both arms are
unanimous and differ**, the only move k=3 can support; otherwise `UNCLEAR`, including any arm with
fewer than k usable answers (a truncation is reported, never counted). Single arm: `STABLE` · `SPLIT` ·
`UNCLEAR`. Scope: Stage B–D blocks, whose schema `thesis_tool` rebuilds; J-15's arms answer through
their own version's schema (`thesis_tool(..., j15_version=)`). ⚠ It is SAMPLING, not RM-1's
perturbation probe (`RA-61`/`RA-62`), so a `STABLE` here does not supply `verdict_stability` and cannot
lift `RA-154`'s FLAG by itself. 13 tests, all with fake transports. Dry runs on real MU recordings:
J-16 noise floor = 2 new calls of ~183k tokens; J-15 v1→v2 = 5 new calls of ~182k.

✅ **Live, 2026-10-01 (approved by Victor): MU `J-16` noise floor, k=3**, `run-2026-10-01T144904-agreement-j16`.
2 new calls on the subscription, ~59 s and ~203.6k input tokens each, notional $2.14 each, **$0 API**;
no truncation; rule checks clean. ⚠ The second call got no prompt-cache benefit (961 tokens read), so
each probe call costs a full bundle.

| Decision field | 3 answers | Result |
|---|---|---|
| `verdict` | SELL · SELL · SELL | **STABLE** |
| `conviction` (as authored, before `DX-118`'s cap) | Medium · Medium · Medium-High | **SPLIT** |
| considerations count | 3 · 3 · 3 | STABLE |

★ **What it says.** The SELL is not a lucky draw: the verdict call repeats it 3/3 on identical input,
and all three name the same counterweight (capex taken gross, with no maintenance/growth split). The
conviction is the soft part (2 Medium, 1 Medium-High), which `DX-118` caps at Low regardless. ⚠⚠ **And
the verdict this measures as stable is the one its own falsifiers #1 and #2 have since shown wrong.**
Stability is not correctness; this is `L8` §9's argument made concrete, and why falsifiers stay the
primary instrument. ⚠ Sampling, not RM-1's perturbation probe: this does not supply `verdict_stability`
and does not lift `RA-154`'s FLAG.

### ✏ Same day — item 5, CONSENSUS half BUILT: FMP published actions as of a date ($0)

Victor approved (2026-10-01): FMP `grades` + `price-target-news` + `earnings` for past as-of dates, a daily
`analyst-estimates` snapshot for future ones, no paid vendor; FMP calls standing-approved (fixed-rate).
Two rulings: **1b** — an item counts when published on or before the as-of **market close** (16:00 New
York, the moment of the raw close the thesis is priced at; a date-only row on the as-of day is excluded,
since it cannot be placed before the close) · **2a** — past earnings estimates are included **with a
caveat**, because FMP edits those rows after the report (`lastUpdated`).

| Piece | What |
|---|---|
| fixtures | `tests_src/fixtures/consensus/MU_{grades,price_target_news,earnings}.json` + `MU.meta.json` (946 · 200 paged · 166 rows; fetched 2026-10-01T19:07Z; hazards listed) — via `tools/fetch_consensus.py` |
| section | `src/fundamental/bundle/consensus.py`: latest rating per firm over 365 days, targets over 90 days, last 4 reports estimate vs actual; a `computed` part (`consensus.as_of` v1), so the blind Stage-A view never sees it (`RA-14`). Unmapped grade labels are reported, never bucketed by guess |
| arithmetic | ✏ **moved to D-02 after the first suite run failed `AC-1.40`** (`.median()` in D-01): `src/feature_engineer/consensus.py` (`target_spread`, `eps_surprise_pct`; a zero or missing estimate gives `None`, not a number) |
| runner | `run_thesis_once.consensus_for` adds the part when a fixture exists and drops `consensus_rating_and_price_target_actions` from the declared absences. ⚠ `consensus_forward_estimates` **stays declared absent** for a past as-of (`DX-109`: look-ahead) |
| snapshot | `tools/snapshot_analyst_estimates.py MU AMD` — first snapshots taken 2026-10-01. ⚠ written under `.state/snapshots/`, which is **gitignored** (`DX-12`'s shape): history not captured, or lost with the laptop, is gone. ⬜ Victor: schedule it, and decide where snapshots are kept |
| tests | `test_consensus_as_of.py` (8) · `test_consensus_in_the_bundle.py` · `test_snapshot_analyst_estimates.py` · `test_feature_consensus.py` (5). Suite **2,425 pass · 1 deliberate red (`J-07`)** |

**What MU's analysts had published by the 2025-06-26 close:** ratings **buy 19 · hold 3 · sell 1**
(23 firms); 6 price targets in 90 days, **median $147.5** (low $135, high $170) against a $126 raw
close; 4 straight EPS beats, the last **$1.91 vs $1.60** (+19.4 %). ⇒ the SELL was a strongly
contrarian call, which is exactly what `J-09`'s differential view exists to state — and it never saw this.

### ✏ Same day — item 5, PRICE-REQUIREMENT half BUILT: `F10 D10` ($0)

What actually capped `J-09` was its THIRD price requirement (*"10 years at 28.3 %, then 2.5 %"*) marked
`insufficient_evidence`, citing `implied_duration` as declared absent; market cap and multiples were
absent too but did not bind. F10 had no AC for it, so **the spec was amended first** (constitution
§5.1): Victor chose a duration table at **5 / 7 / 10 / 15 years** (`D10`, `AC-F10.22`), published as
`dcf_two_stage@v2` (`v1` + `duration_table`, every other value identical; `v1` untouched). Market
capitalisation joins the trail. The runner moved to `v2`, and drops `implied_duration` +
`market_capitalisation` from the declared absences **only when the rendered part carries the table**
(an unavailable valuation keeps them declared). `STAGE_B_ABSENCES` itself is unchanged — it is also
`rule_checks`' record of what older bundles declared. `--stop-after BLOCK` added to the runner.
Tests: 8 new F10 tests (5/5 mutations caught) + 1 runner; traceability guard 169 → 170. Suite
**2,436 pass · 1 deliberate red (`J-07`)**.

| MU, 2025-06-26, $126 raw | 5 y | 7 y | 10 y | 15 y |
|---|---|---|---|---|
| stage-1 FCFF growth the price requires | **no root** (> 40 %/yr, the bracket top) | 39.0 % | 28.3 % | 20.5 % |

Market cap **$141.75bn** (1,125M diluted shares). ⚠ Still declared absent: `implied_margin`,
`valuation_multiples` (F10 non-goals).

### ✏ Same day — `J-09` re-asked with both halves in its bundle ($0 API)

`run-2026-10-01T225847-mu-thesis`, `--stop-after J-09`, subscription: 169,943 in / 7,544 out, notional
$1.04. Schema-valid; rule checks 0 violations. ⇒ finish with `--resume-from` (J-10…J-17, ~12 calls).

| `J-09` field | 2026-09-15 (no consensus, no table) | 2026-10-01 |
|---|---|---|
| `consensus_position` | `INSUFFICIENT_EVIDENCE` | ★ **stated**: 19 buy · 3 hold · 1 sell, 90-day targets $135–$170 (median $147.5), four beats ending +19.4 % |
| `differential_view` | "I cannot state a differential view" | ★ no differential on DIRECTION (Stage A's supply read is insufficient); differs on BASIS — consensus anchors on quarterly EPS, the price needs a FCFF level no FY2016–FY2024 year delivered |
| duration requirement | `insufficient_evidence` (`implied_duration` absent) | ★ **`required_more_than_evidenced`** — no root at 5 y, ≥ 7 years of 28–39 % needed |
| still `insufficient_evidence` | — | ⓐ the gross-capex base (`D9` known limit: incentive proceeds uncomputable from D-07) · ⓑ implied margin (still declared absent, F10 non-goal) |

⚠⚠ **So the `DX-118` cap's `J-09` half still fires, and the reason is structural.** `derate._absences`
flags the price requirement when ANY row is `insufficient_evidence`. Row ⓐ rests on a limit F10 `D9`
DECLARES uncomputable, so it will fire on every MU thesis whatever data is added; row ⓑ needs another
F10 amendment. ✅ **`DX-140` ruled 2026-10-02 (Victor): a requirement left unset only by a DECLARED
known limit is STATED on the thesis, not counted toward the cap.** Implied margin (curable) still counts, and
`J-10`'s base rate still caps on its own.
⚠ Minor: `consensus_position` set the targets against **$127.25** (the analysts' "price when posted")
rather than the thesis's $126.00 raw close — the section shows both; not a rule violation.

⬜ **Not yet done.** ⓐ `J-09` ✅ re-asked (above) — was: has not been re-asked with the section in its bundle, so the
`DX-118` cap (`derate.py` reads `J-09`'s `consensus_position`) is **still on** — a re-run of J-09
(and, for the verdict to use it, J-16) on the subscription. ⓑ The `J-09` price-requirement half is free
D-02 code (market cap and multiples from the raw close × filed shares). ⓒ The `J-10` base rate: the
published study's table entered with source and page, ⚠ **after Victor names the reference class**.

### ✏ Same day — item 3 BUILT in code: `J-15 v2` writes each falsifier's structured TEST ($0)

| Piece | What |
|---|---|
| spec | `L1-fundamental-analysis-master-prompt` v0.4.0: **§J-15 `v2`** = v1 plus one paragraph, *write each condition's TEST in the grammar the answer schema declares, or rewrite the condition until it can be* |
| prompt | `e_blocks.J15_V2_TEXT`, byte-identical to the spec (drift guard green); `BLOCKS["J-15"]` → `v2` |
| schema | each falsifier now REQUIRES `test`: window, clauses (`each` `any` `consecutive` `sum` `rises_each`), per-period comparisons whose every field is an `enum` of the published observables, so a test over a field the system does not receive cannot be written |
| validation | `falsifier_check.validate_test` names every undecidable shape (unknown field, mode or op; `consecutive` < 2; a one-series mode with two conditions; a window outside 1..12). ★ **Your 4 hand-written MU tests are valid in it.** A J-15 answer with an invalid test raises `UncheckableFalsifierError`, so **J-16 is never issued** (RA-16) |
| runner | writes `falsifier_tests.json` beside `thesis.json`, stamped with the run id; a `--resume-from` run that carries J-15 carries its tests too |
| checker | `check_falsifiers.py` finds that file with no `--tests`; `--all` checks every recorded thesis. On real data, MU with the hand tests reproduces **#1 #2 FIRED, #3 #4 HELD** exactly |

⚠ **Two J-15 paths exist, and only one moved.** The Stage B–D runner ships `v2`. The **orchestrated**
job (`src/fundamental/thesis/run.py`, J-11 → J-15 → J-16) parses falsifiers out of PROSE with no
schema, so `v2`'s *"the grammar the answer schema declares"* has nothing to point at there. It stays on
`v1` **on purpose**, with a test saying so. ⬜ **Go-live (item 10) must move the daily path onto the
structured Stage B–D calls**, or daily theses keep producing falsifiers only a reader can decide.

⚠ One inherited test (`test_the_j_blocks_are_the_master_prompts_text_and_are_hashed`) compared each
block with the current registry entry by NAME; with J-15 legitimately at two versions it now compares
by name AND version, which is what its own comment said it checked. Tests: 19 new (18 structural + 1
runner integration). Suite 2,379 pass · 1 deliberate red (`J-07`).

✅ **The live `J-15 v2` call, 2026-10-01** (approved by Victor): the recorded MU J-15 request with ONLY the
v1 → v2 text and schema changed, through the subscription. `run-2026-10-01T143722-mu-j15v2-probe` (in
`.state/runs`, not promoted). 124 s; ~210k input tokens written to cache then read once (6 CLI turns for
the structured output); 10,328 out; notional $2.46, **$0 API**.

| | J-15 v2 (model, decided automatically) | Victor-approved readings of the v1 thesis |
|---|---|---|
| #1 | OCF − capex > **$1.5bn** in each of the next 4 quarters → **HELD** (Q1 after the thesis was $0.07bn) | > $0 each and sum > $5bn → **FIRED** |
| #2 | gross profit rises in each of the next 4 AND exceeds $3.5bn in each → **FIRED** | rises each quarter → **FIRED** |
| #3 | operating income > $1bn in each of the next **8** quarters → **PENDING** (4 of 8 reported) | capex < $2.5bn for 2 quarters with GP ≥ $3,508M → **HELD** |
| #4 | finance-lease liability (current + noncurrent) stays below $3,107M in each of the next 4 → **FIRED** | debt > $22bn while cash < $6bn → **HELD** |

★ **What it shows.** ⓐ **4 of 4 tests schema-valid, grammar-valid, over published fields only, and each
decides exactly the sentence beside it** (read one by one). ⓑ **No hand translation was needed.**
ⓒ The rule checks pass on the call (no misquote, no leaked markup). ⓓ ⚠ It is NOT the same falsifier
set: v2 authored fresh conditions rather than restating v1's, so the two columns are not a fidelity
comparison. The fidelity comparison is sentence ↔ test **within** each column, and both pass.
ⓔ ⚠ It surfaced `DX-139` (#3 was first reported FIRED on half its window). ⚠ k=1: one call says the
mechanism works, not that v2's falsifiers are reliably well-chosen.

### ⬜ What next

**1 → 2 → 3**, all free or nearly so, in that order (✅ all three done 2026-10-01): rule checks first because they cover every block
at once and immediately re-check the 53 live recordings; then the k=1 gate, a one-function defect; then
the falsifier loop, which turns the only instrument that has caught a wrong thesis into one that runs by
itself. ⚠ **Item 5 is the first substantive decision that is the fund manager's** and should be taken
before item 3 finishes, because without those inputs every thesis stays capped at Low.

## 2.1o ★★ 2026-10-01 — development LLM calls move to the subscription (GW-24…GW-29)

> **$0 API.** Victor's rule (`CLAUDE.md` house rules): golden cases, test runs, debugging and re-records
> go through **headless Claude Code on his subscription**. The Anthropic API key is reserved for the
> real daily runs. `DX-136`.

### What exists now

| | |
|---|---|
| spec | `L2-shared-infrastructure` **v0.4.0 §5.7**: `GW-24`…`GW-29`, `AC-0.21`…`AC-0.26` |
| transport | `src/shared/llm/claude_code_transport.py`: `claude -p --output-format json`, no tools, no saved session, run in an empty temp directory (so it never loads this repo's `CLAUDE.md` or hooks), structured output via `--json-schema` built from the same tool schema the API path uses |
| selection | `CIA_LLM_TRANSPORT`, **default `claude_code`**, or `anthropic_api`. Any other value raises. `tools/llm_transport.py` is the one switch the five `run_*` tools use; `build_gateway` reads the same variable |
| guards | API credentials are stripped from the subprocess, and the CLI must report `authMethod: claude.ai` before the first call (`GW-25`). `temperature` is refused (`GW-28`). The CLI's output-cap error becomes `stop_reason: max_tokens` (`GW-29`) |
| accounting | every response carries `transport` (`GW-26`). A subscription call is priced at $0 and keeps `notional_usd`, the CLI's list price. `spend_report.py` lists those calls apart and **never adds them to the floor** (still $72.41) |
| tests | 28 new (`tests/unit/test_claude_code_transport.py`). Suite **2,327 pass · 6 skip · 1 fail** (`J-07`, deliberate) |
| live check | one ~2k-token call with the real `extraction_tool` schema and model id `claude-opus-5`: `stop_reason: tool_use`, valid structured items, notional $0.022, $0 API |

### ⚠ What it changes about every number after today

- **The paid lines in `L8` §6 become usage, not dollars.** The ≈$111 estimate for all three golden
  levels now costs subscription quota. ⚠ The account is **Pro**. A full thesis is ~13 calls of ~90k
  tokens, so usage limits, not dollars, are now the constraint on pace.
- ★★ **A `claude_code` recording is not an API recording.** The envelope differs (CLI system prompt,
  `--json-schema` instead of a strict tool, no `temperature`, output capped by environment variable).
  A golden case signed on one grades the **prompt**, not the production transport. ⇒ Before the daily
  runs go live, re-run a sample of signed cases through the API (paid, approved per call) and compare.
  ⬜ This is now a precondition of `MS-0`.
- `--thinking-display` (`DX-96`) has no effect on the subscription path, since the CLI shows no thinking.

### ✏ Same day — `DX-131` and `DX-135` ruled and built ($0)

Victor took both recommendations. **`DX-131`**: any period date the document does not state is cleared
in the parse, for every block, never computed. **`DX-135`**: an absent item keeps its qualifier. ★ The
fix was measured before it was made, so its blast radius was known: `DX-131` moves exactly 5 pending
cases and no signed one; `DX-135` moves 1 pending case and **2 signed ones, which were withdrawn into
`extraction.pending.yaml` rather than edited** (`D2`), one of them splitting in two. All 48 extraction
cases (26 live, 22 pending) resolve to exactly one item and match. Live set **33 → 31**; pending
**29 → 32**, all signable. Suite 2,338 pass · 1 deliberate red (`J-07`).

### ⬜ What next

⊘ Superseded the same day by §2.1p (golden programme closed). Originally: unchanged in substance from the 2026-10-01 review. ⚠ **Victor's rulings on `DX-135` and `DX-131` come
first, because both decide the identity of cases that are already drafted.** Then the free defects:
the k=1 gate passing by absence (`L8` §8 lesson 8), the `DX-134` leaked-tag guard, a cross-block check
for `DX-131`'s class, and `DX-76` envelope versioning.

## 2.1n ★★★ 2026-09-17 — the scorecard is COMPLETE: `E-09` solved, `J-04` scored, coverage 1.000

> **$1.17 in two calls** ($0.4171 `E-09` + $0.7485 `J-04`), both approved individually. `DX-129`
> and `DX-130`. ★ `STAGE_A_ABSENT` is now **empty for the first time** — every declared Stage-A
> block has an answer on disk.

### The two calls

| Call | Run | Result | Cost |
|---|---|---|---|
| `E-09` at **`--effort low`** | `run-2026-09-17T071619-mu-e09` | 9 items verified, `ap.change` FOUND twice, 1,639 out **against five prior truncations at 20,000** | **$0.4171** |
| `J-04` (rubric, blind) | `run-2026-09-17T113226-mu-j04` | **`earnings_quality@v3` = 4**, 12,635 out, rubric hash `sha256:ba08f3636…` | **$0.7485** |

★ The order matters and was forced: `RA-32`/`DX-98` gate `earnings_quality@v3` on `searched:ap.change`,
which only `E-09` emits. Four days of `J-04` being "unscoreable" were really `E-09` being unattempted.

### What `J-04` actually reasoned — and why it is a 4, not a 5

The cash test, done the way the criterion asks: operating cash flow exceeded net income in **every**
period the bundle reports — **$11,795M vs $5,338M** (FY25 9M), and **$5,102M of cash inflow against a
$(109)M reported LOSS** (FY24 9M). ★ It then did the part that separates a real answer from a
plausible one: it attributed the gap to **D&A of $6,203M**, not to a working-capital release, and
showed the working-capital lines were in aggregate a **drag** (receivables −123, other current assets
−206, other current liabilities −681). ⇒ conversion explained by capital intensity, not accrual timing.

⚠ **Not a 5, by its own declaration:** the model emitted a `DATA GAP` — the accounting-policy-change
question can be answered only over the bundle's window, not over the full history the criterion
implies. `MP-7`/`S-4` again: the floor and the ceiling both get used honestly.

### The complete scorecard, re-derated free

```
coverage   1.000   moat 1.00 · earnings quality 1.00 · balance sheet 1.00 · capital allocation 1.00
scorecard  J-03 = 2  ·  J-04 = 4  ·  J-05 = 3  ·  J-06 = 4
verdict    SELL       (unchanged — J-16 is NOT re-asked)
conviction Low        (three governing inputs still absent)
```

### ★★ The finding: coverage 1.000 did NOT raise the conviction

This is `DX-118` working as designed, and it is the thing to remember from this session. Coverage
measures **evidence gathered**; the conviction cap measures **governing inputs absent**. The three
that cap Micron — `J-09`'s consensus position, `J-09`'s price requirement, `J-10`'s reference-class
base rate — are Stage-B/C inputs the bundle never contained. ⇒ **No quantity of Stage-A extraction can
lift them**, and a full-coverage scorecard sitting beside a Low conviction is not a contradiction.

⚠ A reader who reads 1.000 as *"fully informed"* will over-trust this thesis. The cap is the
counterweight, and it is the reason `RA-67` defines confidence as coverage rather than as belief.

★ And the verdict this all decorates is still **wrong by its own conditions** — falsifiers #1 and #2
FIRED (`DX-128`). A complete scorecard on a falsified thesis is exactly the state the measuring
apparatus exists to make visible.

## 2.1m ★★ 2026-09-16 — bypassing the paid work: a free re-deration and a decided `RM-13`

> **$0.** Victor: *"no paid run, too expensive, find a way to bypass this."* ⇒ `DX-128`, and a
> temporary hand-off file, `_TEMP_for_victor_2026-09-16.md`, for what could NOT be bypassed.

### Already done before the instruction — and not re-run

`E-13` (industry, replayed free), `J-03` (**moat = 2**, $0.61) and `J-08` (`insufficient_evidence`,
$0.81) had all completed earlier in the session. ★ Nothing was re-run; **$0 spent after the instruction**.

### Two bypasses that worked

| Paid thing | Bypass | Result |
|---|---|---|
| Re-authoring the thesis (~$11.38) to see the new coverage | `tools/rederate_thesis.py` — recompute only what is ARITHMETIC over evidence | coverage → **0.917**, conviction **Medium → Low**, verdict **unchanged**; the record states in its own `limitation` field that `J-09`…`J-17` never saw the new evidence |
| A `J-15` re-run to get machine-checkable conditions | `DX-128` — the structured test is written by HAND beside the prose, in a declared grammar | **#1 #2 FIRED · #3 #4 HELD**, reproducing the hand analysis exactly, deterministically, free |

### ⛔ What could NOT be bypassed, and why (detail in the temp file)

**`E-09`** — `earnings_quality@v3` needs `searched:ap.change`. No other block emits it; the marker
cannot be synthesised (`DX-85`ⓒ: evidence by assertion); and it cannot be REPLAYED because all five
attempts TRUNCATED, so no complete call exists on disk — `DX-123`'s guard refuses them, correctly.
⇒ It needs one live call (~$0.50–0.90) at `--effort low`, the lever never tried on that block.

★ **The replay path has a shape worth noting:** it recovers a defect in OUR code, never a failure of
the model. `E-09` is the case that proves the distinction — nothing to recover.

## 2.1l ★★ 2026-09-16 — `DX-116` answered, and two instruments built free

> **$0.** `DX-116` closed (half solved, half declared), `DX-125`…`DX-127` built. 2,287 tests pass.

### `DX-116` — attempted, and it splits cleanly in two

| Half | Outcome |
|---|---|
| `J-11`: lease-funded equipment escapes capex | ✅ **No change needed.** `D8` counts finance leases as DEBT ($3,107M on MU at 2025-05-29). Charging the $1,394M of trailing ROU additions to capex as well would count the same equipment twice — once as debt subtracted from equity value, once as investment reducing the flow. ★ `J-14` said so first, when it contradicted `J-11` |
| `J-09`: capex is gross of government incentives | ⚠ **Unsolvable from D-07, so DECLARED.** A namespace-wide scan of Micron's `companyfacts` finds no tagged incentive-PROCEEDS fact at all; the $1,294M exists only in filing prose. Every result now carries it in `known_limits` (`F10` `D9`, AC-F10.21) — material, since crediting 9M alone would roughly double the $1,349M base |

★ The rule that falls out: **a limit is declared only when it is real AND uncomputable.** Listing the
lease half would have been false, and a limits list with a false entry trains the reader to skip it.

### The two instruments

- **`RM-13`'s falsifier checker** (`tools/check_falsifiers.py`) — deterministic gathering of every
  reported period since a thesis, with deadline state. ⚠ It does NOT decide a prose condition:
  `DECIDABLE_BY_READER` is an honest status, and automatic firing needs a structured `test` in a future
  `J-15` (`DX-125`). ★ On its first run it found `DX-126`.
- **`DX-126`** — falsifier #4 of the Micron thesis names `LongTermDebtNoncurrent`, a tag Micron **last
  filed in 2013**. The observable list offered it because the COLUMN exists. ⚠ Its silence looks
  identical to a condition holding, so the thesis carried an unfalsifiable falsifier through every
  check. Fixed: only tags non-null in the latest 4 reported periods are offered (31 → 25 for MU).
- **`DX-127`** — prompt caching: the ~140k-token base bundle is now one `cache_control` block shared by
  all 13 Stage B–D calls. **$17.57 → $11.38** per thesis, arithmetic until a live run reports a non-zero
  `cache_read`. ⚠ The model now reads evidence → commits → instructions; `--no-cache` restores the old
  order exactly.

### ⬜ What next

1. ⛔ **`E-09`** — the last evidence gap (earnings quality 0.67, the only dimension short). Five
   truncations; the untried lever is `--effort low` with a raised cap, the one that fixed `J-13`/`J-14`.
2. 💲 **Re-author the thesis** on 0.92 coverage with caching (**≈$11.38**) — it would also validate
   `DX-127` against the vendor and re-run `J-15` with the corrected observable list (`DX-126`).
3. **Victor:** a structured `test` on `J-15` (`DX-125`) · `E-13 v2` so `cx.status` quotes the sentence it
   is read from (`DX-122`) · sign the pending `J-20`/`J-09` cases and consider one for `J-03`.
4. **Free, smaller:** `J-13`'s `book_value` metric for financials; declaring `E-03`/`E-05`/`E-08`/`E-11`.

## 2.1k ★★★ 2026-09-16 — the industry file: `DX-117` unblocked, and the first moat score

> **$3.31** (⚠ $1.88 of it on three failed `E-13` attempts) plus free fetching. `DX-119`…`DX-124`.
> ★ Scorecard coverage **0.583 → 0.917**; `J-03` scored for the first time in this project's history.

### What exists now

- **A versioned source list** — `config/sector/memory_v1.yaml` (`memory.v1`): **Sandisk** (EDGAR CIK
  0002023554, also the declared reporter for the Kioxia joint-venture fabs), **SK hynix**, **Samsung**
  (peer set: Victor, *"relative size and similar product lines"*). Kioxia, YMTC/CXMT and the paid trade
  trackers are EXCLUDED with their reasons ON the file, so announced supply here is a declared LOWER BOUND.
- **Three real documents**, fetched 2026-09-16 with Victor's authorisation, each with a `.meta.json`
  sidecar carrying url, published date, WHERE THE DATE CAME FROM, and a content hash: Sandisk's 10-Q
  (filed 2025-05-12), SK hynix's 1Q25 release (2025-04-24), Samsung's 1Q25 IR deck (2025-04-30). All three
  predate the bundle's `as_of`; a later document is omitted WITH ITS REASON rather than dropped (`INV-1`).
- **`tools/ingest_sector_file.py`** visits every source and cannot skip one silently;
  **`run_extraction_once --sector`** renders the file as one pinned `sector_file` part;
  **`tools/reverify_recording.py`** replays a COMPLETE recorded call under fixed verification code.
- **Live results:** `E-13` over the industry file returned **10 verified items** — Kioxia's Kitakami
  K1/Y7/K2 fabs (through Sandisk's own facility agreements), Samsung's *"Ramp up enhanced HBM3E 12H"*,
  SK hynix's *"when demand ramps up"*. `J-03` then scored **moat_durability@v2 = 2**: *"A mechanism is
  described in the filings and the outcome tests are inconclusive on the bundle's periods."* `J-08`'s
  supply read stays **`insufficient_evidence`**, and its own sentence is the finding: *"the aggregate
  supply decision is precisely the quantity this bundle does not disclose."*

### ⚠⚠ What went wrong — three paid failures, $1.88, one of them a repeat

| # | Failure | Cost | Cause |
|---|---|---|---|
| 1 | `DX-121` | $0.52 | Every item was stamped with MICRON's accession and spans resolved only against `filing` parts — an industry quote had nothing to cite |
| 2 | `DX-122` | $0.50 | `X-01` ② asks the value to appear in its quote; `cx.status` is a LABEL no filing contains |
| 3 | `DX-123` | $0.88 | ⚠⚠ **Truncation — the `DX-115` lesson I had just written and did not apply.** The runner has `--effort`; I ran a 205k-char bundle without it |

★ **A dry run cannot catch 1 or 2: it never verifies.** An end-to-end test with a synthetic item costs
nothing and would have caught both before any call — that test exists now. ★ Attempts 1 and 2 COMPLETED;
only our verifier refused them, so the evidence was recovered by REPLAY at $0 under a four-part guard
(`DX-123`), and attempt 3 (truncated) is refused by that same guard.

### The coverage move, measured

| | moat | earnings quality | balance sheet | capital allocation | aggregate |
|---|---|---|---|---|---|
| before | 0.00 | 0.33 | 1.00 | 1.00 | **0.583** |
| after (E-01 + industry E-13) | **1.00** | 0.67 | 1.00 | 1.00 | **0.917** |

⇒ The thesis runner loads both by default now, and Stage A freezes **8 blocks with only `J-04` absent**.
⚠ The conviction cap (`DX-118`) still fires: `J-08`'s supply read and `J-09`'s consensus remain absent.

### ⬜ What next

1. ⛔ **`E-09` is the last evidence gap** (earnings quality 0.67). It failed five times on thinking
   runaways; the untried lever is the one that fixed `J-13`/`J-14`: `--effort low` with a raised cap.
2. **Free:** the deterministic falsifier checker (`RM-13`), and prompt caching for Stages B–D (~80 % off
   the repeated bundle).
3. **Victor:** `DX-116` (declare the capex limits) · an `E-13 v2` making `cx.status` quote the sentence it
   is read FROM (`DX-122`'s stated gap) · sign the pending `J-20`/`J-09` golden cases, and consider one for
   `J-03`'s new score.
4. 💲 **Re-author the thesis on 0.92 coverage** — ≈$17.57, or ≈$6 once caching lands. ★ After 1 and 2, so
   the re-run measures better evidence rather than the same gaps.

## 2.1j ★★ 2026-09-15 — the `INSUFFICIENT_DATA` question, decided: no hard cap

> **Free.** Victor, 2026-09-15: *"by investment nature, there is no such concrete evidence for
> any investment or valuation decision, all contains unomittable risks. Fundamental Analyst agent
> should proceed with known limitation and risk."*

### The question and the answer

`J-16`'s SELL on Micron was governed by considerations that rested on inputs the bundle had
DECLARED absent (no consensus, no base rates, no competitor supply). The proposal was a **hard
cap**: forbid a directional verdict whenever that is true. ⛔ **Rejected**, on three measured
grounds: (1) every bundle this system can build today lacks those inputs, so the rule is an OFF
SWITCH, not a filter; (2) it would starve `RM-1`, `RM-13` and `F5` — the instruments that caught
this very error — of the verdicts they measure; (3) `PG-1`'s retirement and `PG-10` say **declare
the limit on the artifact, do not withhold the artifact**. ★ And it was aimed off-target: the
error came from a trough-year BASE, not from the absent consensus.

### What was built instead (`DX-118`) — the ladder the house already specified

| Lever | Rule | On the MU thesis |
|---|---|---|
| `INV-012` | coverage < 0.30 ⇒ the system DECLINES (`INSUFFICIENT_DATA`) | not reached |
| `INV-013` | coverage < 0.50 ⇒ verdict **met** with HOLD (`BUY`→`HOLD`; ★ `SELL` unchanged — `DN-9`, §5.4: *a cap can stop you buying, never selling*) | not reached |
| `RA-67` | a GOVERNING consideration resting on a declared-absent input ⇒ conviction capped at `Low`, each absence named | **fired** |

★ **Measured on the recorded thesis** (recomputed free, the artifact is not rewritten): coverage
**0.583** — moat 0.00 · earnings quality 0.33 · balance sheet 1.00 · capital allocation 1.00 ⇒
verdict stays **SELL**, conviction **Medium → Low**, with three named absences (J-09 consensus,
J-09 unmatched price requirement, J-10 base rates). The thesis's `confidence` is no longer the
`{"value": null, "basis": "not_measured"}` placeholder (`AB-1`) — it is the measured ratio, the
per-dimension sets, both as-authored values, and the reason each cap fired.

⚠ Derived in CODE from the committed answers, not asked of the model: every extra required schema
field is one more way a paid call can fail (`DX-113`, measured on J-11). ⚠ The `J-16` prompt text is
unchanged, so no re-record — a `v2` that also asked the model to name them costs ≈$1.10 a run.

12 unit tests + an end-to-end assertion; 5/5 mutations caught (including the one that matters: a cap
that turned `SELL` into `HOLD`).

### ⛔ The next BLOCKER, named by the measurement itself

**Coverage 0.583 is two dimensions of four.** `moat_durability` is 0.00 and `earnings_quality` 0.33
because `E-13` has no valid run (`DX-97`, the subject guard) and `E-09` was skipped (`DX-96`). ⇒ Every
thesis from here carries a conviction cap and a half-empty scorecard until **`DX-117`'s industry source
list** exists (Victor's — it unblocks E-13, J-03 and J-08's supply read, the input this thesis most
lacked) and `E-09` is retried or replaced. ★ That is the same gap `J-16`'s own coverage sentence named.

## 2.1i ★★★ 2026-09-15 — THE FIRST THESIS: Micron SELL · Medium — and its own falsifiers say it was wrong

> `run-2026-09-15T042754-mu-thesis/thesis.json` (with `commits.jsonl`, carried from the three earlier runs, every
> commit hash re-derived). **$16.93 for the whole thesis**, of which **$5.33 was lost** to three failed calls.
> ⚠ `PG-10`: this is ONE authoring pass (k=1) by an unpromoted system — not a recommendation, not a performance figure.

### What it says (as of 2025-06-26, MU FY2025 Q3 10-Q, price $126.00 raw)

- **Verdict `SELL`, conviction `Medium`** (`J-16`). The three considerations it ranked: ① **J-09** — the price requires
  28.3 % a year of FCFF growth for 10 years; all 12 band cells ($10.76–$22.50) sit below $126, so the gap is not a
  discount-rate or terminal-growth artefact; ② **J-10** — four negative FCFF years in nine, no base rate for a decade of
  compounding; ③ **J-07 + J-13** — gross margin 38 % (highest disclosed) on DRAM ASPs above the company's own five-year
  range, with sequential ASPs already falling.
- **Strongest consideration the other way** (item 2, which it did state): clean earnings quality from J-13 (receivables
  flat on +50 % revenue, OCF $11.8B vs net income $5.3B) and **J-14's finding that J-11's lease argument is contradicted**
  (D-02's net debt already carries finance leases); rejected because nothing in the bundle closes an eight-fold gap.
- **Falsifiers** (committed BEFORE the verdict, `RA-16`; commit `sha256:baae26c5…`), all about the business:
  1. OCF − capex positive in each of the four quarters reported after 2025-06-26, summing to more than $5B — by 2026-09-30
  2. Gross profit rising sequentially in each of those four quarters — by 2026-09-30
  3. Capex below $2.5B in two consecutive quarters with gross profit ≥ $3,508M — by 2026-06-30 (⇒ HOLD, per item 3)
  4. Debt above $22B with cash below $6B — by 2026-06-30
- **9 data gaps** (`J-17`), sorted by `obtainable`: consensus and rating actions, competitor capacity, E-09's accrual work,
  a completed FY2025 cash-flow statement (*exists, not fetched*); multiples and market cap, net leverage, HBM revenue and
  margin (*not disclosed*); whether 28.3 % holds under a shorter explicit period (*unknowable*).
- **J-14** found 6 inconsistencies, 9 uncited items bearing on claims, 5 partial citations, 5 single-source claims.

### ⛔ The falsifiers, checked against what Micron later filed (free — EDGAR ledger, 2026-09-14)

| Quarter end | OCF − capex ($M) | Gross profit ($M) | Debt ($M) | Cash ($M) |
|---|---|---|---|---|
| 2025-05-29 (the bundle's) | 1,671 | 3,508 | 15,541 | 10,163 |
| 2025-08-28 | 72 | 5,054 | 14,577 | 9,642 |
| 2025-11-27 | 3,022 | 7,646 | 11,756 | 9,731 |
| 2026-02-26 | 5,516 | 17,755 | 10,142 | 13,908 |
| 2026-05-28 | 17,562 | 35,056 | 5,722 | 24,995 |

⇒ **#1 FIRED** (all four positive; sum **$26,172M** > $5B) · **#2 FIRED** (3,508 → 5,054 → 7,646 → 17,755 → 35,056) ·
#3 not fired · #4 not fired. ★★ **By its own stated conditions the SELL thesis was wrong** — and it could be said without a
judgement call, which is exactly what `RA-35` and `RM-13` exist for: *a thesis that died by its own condition, not one quietly abandoned.*

### ⚠⚠ Why it was wrong — what the evidence says, and what it cannot say

1. **The system's base was the trough's base.** `fv_model` capitalised trailing FCFF of $1,349M; J-20 chose a cycle
   average of $1,287M. Four quarters later the trailing year was $26B. Every judgement block reasoned correctly FROM a
   base that did not describe the business a year out — J-09 said so itself (*"the gap is not an artefact of base
   selection — it is entirely in the growth requirement"*).
2. **The deciding variable was named as absent, and the verdict went ahead anyway.** J-08's supply read was
   `insufficient_evidence`, competitor capacity and consensus were declared absent, and J-16's own coverage statement
   lists them — yet J-16's rule *"if nothing points the other way, return INSUFFICIENT_DATA"* was satisfied (something did
   point the other way), so a directional verdict was permitted. ★ Question for the prompt (not answered here): should a
   verdict whose governing consideration rests on a `insufficient_evidence` input be capped at `INSUFFICIENT_DATA`?
3. **Stage A disagreed with Victor on the cycle.** J-07 recorded `mid`; Victor holds `late` (the red golden case). The thesis
   used `mid`. ⚠ The real outcome (margins 38 % → far higher) fits NEITHER reading well; it was an up-cycle acceleration.
4. **`DX-116`** — the FCFF base carried two known, roughly offsetting capex issues; they do not explain a 20× move.
5. ⚠ **What this cannot establish**: one thesis, one company, one date is an anecdote, not a hit rate (`PG-5.1` Tier B).
   ⚠ **Contamination:** Opus 5's training data runs past 2025-06-26, so an as-of test on 2025 is not blind to the model —
   here it did not help the model, but a correct call on this date would not have proven skill either.

### The issues this run closed

`DX-115` (J-14…J-17 bounded — 4/4 succeeded) · `DX-110` (one text per block; J-11/J-15 full view — ⚠ changes the
orchestrated `thesis` job) · `DX-111` (S-8 in Stage A; golden split declared) · `DX-116` measured · `DX-117` assessed.

### ★★ What remains — measured 2026-09-15

| | done | remaining |
|---|---|---|
| **Platform** (`F1`…`F10`) | 168 / 168 ACs | **0 %** |
| **Analysis blocks — declared** | 27 / 35 (77 %) | **23 %** — `E-03` `E-05` `E-08` `E-11` `E-14` `E-15`, `J-18` `J-19` |
| **Analysis blocks — working** | 23 / 35 (66 %) | **34 %** — 8 undeclared + `E-09` `E-13` `J-03` `J-04` |
| **Thesis path** (30 blocks) | 22 working (73 %) | **27 %** — `E-03` `E-05` `E-08` `E-11` undeclared; `E-09` `E-13` `J-03` `J-04` blocked on evidence |
| **Theses produced** | 1 (k=1) | `RM-1` needs k ≥ 3 before any agreement figure means anything |
| **Golden coverage** | 7 / 35 graded (+2 drafted, unsigned) | 80 % ungraded (a ceiling, not a target) |

### ⬜ What next

1. ✅ **The prompt question in item 2 is DECIDED — `DX-118`, no hard cap** (§2.1j).
2. **Free: a falsifier checker in code** — the table above was computed by hand; `RM-13` needs it deterministic, dated and
   run on every new filing. And **prompt caching**: ~140k of each Stage B–D call's input is the same bundle — putting it
   first would cut the input cost of the 11 later calls by roughly 80 %.
3. **Victor: `DX-116`** (declare both capex limits now) and **`DX-117`** (the industry source list — it unblocks
   J-03, E-13 and J-08's supply read, the input this thesis most lacked).
4. **Victor: sign or change the two pending golden cases** (J-20, J-09).
5. **Paid, later: k=3 theses** — only after 2–3, or the three runs measure the same missing inputs three times.

## 2.1h ★★★ 2026-09-14/15 — Stages B–D built, and run live on Micron up to J-14

> **Spend $12.06** over three approved runs (all capped; the $15 total was held) + one FMP price call.
> `DX-108`(1)(5) `DX-109` closed · `DX-110`…`DX-116` new. No thesis yet: the run stopped at `J-14`.

### What exists now

- **Micron's raw price**, recorded once from FMP (`tests_src/fixtures/prices/MU_raw_eod_2025-06.json`,
  `non-split-adjusted` — trap 2 confirmed: `adj*` field names, raw values): **$126.00 on 2025-06-26**.
  ⇒ `fv_model` **$15.96**, band **$10.76–$22.50** (every one of 12 cells below price), implied stage-1
  FCFF growth **28.3 % a year for 10 years**; `fv_analyst` on J-20's basis **$15.09** (recorded, never in a bundle, `VS-3`).
- **`J-09`…`J-17` declared verbatim** (`DX-109` ⓐ), full view, drift-guarded; J-13 binds `<METRIC>` per call.
- **`tools/run_thesis_once.py`** — Stage A loaded from recordings and re-validated (a pre-`DX-100` rubric answer
  is VOID and refused), frozen and committed; every later output committed to `commits.jsonl` BEFORE any call
  can read it, as a `stage_output` part pinned by commit hash (new kind, blind-withheld); the staging rule
  (`J-11`…`J-13` never read Stage C; J-14 reads all); J-15's falsifiers must pass `Falsifier` and be on disk
  before J-16 is issued; strict tool schemas; a hard `--budget-usd`; `--resume-from` that carries a failed run's
  commits only if every commit and bundle hash re-derives. **41 tests, every guard mutation-tested.**
- **J-20's exclusion quotes are verified in code**; J-20 is in `STAGE_A_ORDER`.

### What the live run produced (committed, `run-2026-09-15T034909-mu-thesis/commits.jsonl`)

| Block | Result |
|---|---|
| `J-09` | Price requires 28.3 % FCFF growth × 10 years — `required_more_than_evidenced`, gap **unexplained** by Stage A (J-07 `mid`, J-08 supply `insufficient_evidence`); consensus and differential view **insufficient** (declared absent); band insensitive to rate/terminal growth. ★ Finding: `D6` charges GROSS capex and does not credit government-incentive proceeds ($1,294M in 9M FY25) → `DX-116` |
| `J-10` | 5 claims; 4 of 5 require Micron to be **exceptional** within its class; base rates mostly absent |
| `J-11` | Bear case: equipment enters through **non-cash finance leases, outside the capex line**, so the FCFF the price is solved against is flattered → `DX-116`. Own falsifier: 4 quarters of rising gross profit with OCF > capex by 2026-06-30 |
| `J-12` | 4 loss paths; earliest-symptom ranking [2, 4, 1, 3]; path 1 = DRAM following NAND's sequential ASP declines |
| `J-13` ×5 | Cyclical position (mechanism 11) `present` in all five metrics; FCF has the most mechanisms present (finance leases, receivables, inventory, cash conversion) |
| `J-14`…`J-17` | ⛔ not produced — J-14 thinking runaway (`DX-115`) |

### The issues, in order — and what was chosen

| # | Issue, plainly | Chosen | Rejected |
|---|---|---|---|
| `DX-110` | The old WF-1 path declares a DIFFERENT `J-11 v1` text and runs J-11/J-15 blind | Recorded, untouched (its tests pin inherited behaviour) | Silent overwrite |
| `DX-111` | Stage-A calls never composed `S-8` (fresh authoring) | Stages B–D compose it; Stage A deferred to the next paid re-record | Changing Stage A's envelope hash now |
| `DX-112` | A mutant of the spend guard ran the real composition (no vendor call, $0) | Guard test patched to raise | — |
| `DX-113` | J-11 returned 4/6 fields — the schema was not strict; failed trace closed `SUCCESS`; estimate −9 % | Strict schema (bounds as descriptions, validated client-side) · `close("FAILED")` · 2.7 chars/token · verified resume | Retrying unchanged |
| `DX-114` | J-13 thinking runaway (16k, tool_input 0); resume-of-resume mis-pinned commits (caught by the hash check) | J-13 `effort: medium` + 32k → **5/5 succeeded** (10k–19k out) · pin to producing run | Cap alone |
| `DX-115` | J-14 thinking runaway at default effort, input 193k | ⬜ apply J-13's settings to J-14…J-17 (free), then resume (paid) | — |
| `DX-116` | Two opposite `D6` capex questions raised BY the analysis: incentives not credited (base too low) · finance-lease equipment not charged (base too high) | ⬜ Victor | — |

### ⚠ What went wrong in the WORK

1. **Three paid stops in one thesis** ($0.83 J-11, $1.12 J-13, $1.37 J-14 lost). Each was caught before a thesis was
   built on it, and each fix was free — but the J-13 runaway should have prompted the same setting for J-14 at once:
   ★ **when a block fails from a GENERAL cause (thinking), apply the fix to every block sharing the cause, not just the one that failed.**
2. **Estimates ran low twice**: 3 chars/token (−9 %), then J-13's outputs (10k–19k, projected 7.5k) made J-14's input 193k vs 174k estimated.
3. **A stray run directory from a mutation test** (`DX-112`) — found by listing `.state/runs`, not by the test output.

### ★★ What remains — measured 2026-09-15

| | done | remaining |
|---|---|---|
| **Platform** (`F1`…`F10`) | 168 / 168 ACs | **0 %** |
| **Analysis blocks — declared** | 27 / 35 | **23 %** — `E-03` `E-05` `E-08` `E-11` `E-14` `E-15`, `J-18` `J-19` |
| **Analysis blocks — working** (a successful live call) | 19 / 35 | **46 %** — 8 undeclared + `E-09` `E-13` `J-03` `J-04` + `J-14`…`J-17` |
| **Thesis path** (`E-01`…`E-13` + `J-01`…`J-17`, 30 blocks) | 18 working | **40 %** — ★ but only **4 blocks (J-14…J-17, ≈$4–5)** stand between now and the FIRST thesis |
| **Golden coverage — blocks graded** | 7 / 35 | **80 %** ungraded (a ceiling, not a target — §2.1c) |

## 2.1g ★★ 2026-09-14 — Q2 / DX-103 / DX-104 applied, `J-20` run live on Micron

> **Spend $0.50** (one approved J-20 call; EDGAR re-ingest free; FMP not called). `DX-106`…`DX-108`.

### What was decided (Victor) and what was built

| Decision | Built | Measured on Micron |
|---|---|---|
| `DX-104` — `t = 0` in a loss year | `D6` → `fcff…v2`; the basis records `tax_rule: loss_year_zero`; AC-F10.17 amended; history part v2 marks the year | FY2016 **−$2,403M**, FY2023 **−$6,325M** now computed — the FY2016–FY2025 cycle is complete |
| `DX-103` — fallback tags into `CANONICAL` | `InterestExpenseNonoperating`, `DebtCurrent`, `LongTermDebtAndCapitalLeaseObligations` second in preference order; `fundamental` contract **v2 → v3** (`FE-2`: same names, different inputs) | MU's interest and debt features were null for a decade; now populated |
| `F10` `Q2` → `D8` — securities and leases in net debt | `balance` subtracts marketable securities (current + non-current) and adds finance leases NOT already inside a lease-inclusive debt tag; unreported items named in `known_omissions`; AC-F10.20 | Securities $648M + $1,402M (10-Q line 559) ⇒ net debt **$3,328M** as of 2025-06-26 (was $5,378M); **net cash $24,406M** as of 2026-09-13 |

### `J-20`'s first live answer — `run-2026-09-14T122547-mu-j20`

- `stop_reason: tool_use` · 72,624 in / 5,581 out · **$0.5026**.
- **Method `cycle_average_fcff`, window FY2016–FY2024, trough FY2023, peak FY2018** ⇒ D-02 computed
  **$1,287,274,066** (checked by hand: sum of nine years $11,585M ÷ 9).
- 3 exclusions recorded (not applied): FY2024 patent cross-license gain $200M, the FY2024 benefit from
  selling written-down inventory $987M, the FY2023 $1.83B inventory write-down. **All three quotes verified
  verbatim in the 10-Q by hand** (lines 1138-1139 and the risk-factor sentence). ⚠ The $200M / $987M are
  NINE-MONTH figures ended May 30, 2024, labelled "FY2024" by the model — approximately right.
- What would change it: a completed FY2025 with positive FCFF at ~$14B capex ⇒ shorten to FY2019–FY2025.
- **Indicative, NOT an `fv_analyst`** (no price, so `value_on_basis` cannot run): as of 2025-06-26 the
  mechanics give **$15.09/share** on J-20's basis vs **$15.96** on the reported TTM basis (band $10.13–$21.33
  vs $10.76–$22.50). ★ At that date the trailing year sat close to the cycle average; the normalisation
  matters at a peak (2026-09-13: trailing $25,164M), which this 2025 bundle cannot show.
- ⬜ **Golden case: Victor's** (`D2`) — a candidate expectation would be `method: cycle_average_fcff`;
  whether the window should end FY2024 or reach back to FY2016 is the judgement to establish.

### The issues — and what was chosen

| # | Issue, plainly | Chosen | Rejected, and why |
|---|---|---|---|
| `DX-106` | Counting OPERATING leases in net debt while `D6`'s operating cash flow already pays them counts them twice | ✅ **ⓐ, Victor 2026-09-14: left out by design** — declared per result under a NEW `net_debt.excluded_by_design` (with the reason), no longer in `known_omissions`, so a choice never reads as a gap | ⓑ count + add back lease cost (a `v3` formula; MU stopped tagging `OperatingLeaseCost` after 2025-11-27 — would refuse MU today) · applying the literal first answer (a `D-19`-class mismatch) |
| `DX-107` | ⛔ Mutation testing was UNRELIABLE for same-size edits: `__pycache__` is invalidated by mtime + size, and a mutant restored within the same second left the MUTANT's bytecode loaded — one real test "failed" on correct code | Re-ran all 10 mutations with `PYTHONDONTWRITEBYTECODE=1` and caches cleared: 10/10 caught | Trusting the first run (a same-size mutant can also read as CAUGHT or SURVIVED wrongly) |
| `DX-108` | J-20 follow-ups found by the run | ⬜ recorded, not built: exclusion quotes are not `X-01`-verified in code (checked by hand here) · `J-20` not in `STAGE_A_ORDER` · the history shows a D-07 FY2008 row with a **0-day "annual" span** · revenue absent FY2009–FY2015 (older tag) | — |

⚠ **Also fixed:** the facts ingest CLI read only `GMAIL_SMTP_USER`; it now reads `EDGAR_CONTACT` first,
like the rest of that file (`src/data_engine/ingest/__main__.py::_facts`, and `src/models/train/__main__.py`).

### ★★ What next — the build is at Stage B (measured 2026-09-14)

**Where it stands:** Stage A is declared (8 blocks + `J-20`), 7 of 9 work on MU; D-02's valuation trail
exists and is wired as a `computed` part; **no CT-9.2 thesis has ever been produced**, and every block that
remains to reach one (`J-09`…`J-17`) runs on the FULL view — which needs a price. **There is no price in
`.state/`** (FMP is the only source; EDGAR has none). So the next work is Stage B, in this order:

| # | Step | Cost | Why this order |
|---|---|---|---|
| 1 | `DX-108`(1) run `J-20`'s exclusion quotes through `X-01` before a basis is recorded; add `J-20` to `STAGE_A_ORDER` (⚠ +$0.50 per future `--stage-a`) | free | A Stage-B block will read `J-20`'s answer as FROZEN evidence; its quotes must be verified in code first, not by hand |
| 2 | Fetch MU's RAW daily close around 2025-06-26 from FMP (`historical-price-eod/non-split-adjusted`, Class A — `fmp-api` trap 2) into the price store | 💲 1 FMP call (subscription quota), **approval needed** | Unlocks `valuation()` end to end on real data: `fv_model` WITH price, implied stage-1 growth (`D7`), and `fv_analyst` on `J-20`'s basis — the three figures `J-09` item 1 reads |
| 3 | **Victor: `DX-109`** — `J-09`'s declared inputs the build cannot supply as written (below) | a decision | Declaring `J-09` verbatim now would repeat `DX-85`: a block asked for evidence nobody provides |
| 4 | Declare `J-09` + `J-10` (drift guard, pre-flight for arithmetic), and a Stage-B runner: full view, Stage A's committed answers as a hashed, non-revisable part (`S-9`) | free to build · ≈ $1–2 live, approval | Stage B is the first stage that reads Stage A as given — the frozen-output mechanism is new code |
| 5 | `J-11`…`J-14` (Stage C, adversarial) → `J-15`…`J-17` (Stage D, commit) | free to declare · live ≈ $0.5–0.8/block | Completes the first `CT-9.2` thesis on MU; `K_RUNS=3` prices `QR-20` (`DX-60`) |

⬜ **Not first, stated so they are not forgotten:** golden cases for `J-20` (Victor, optional); `DX-108`(3)(4)
the FY2008 0-day row and the pre-FY2016 revenue tag; the six undeclared E-blocks; `E-09` (skipped) and
`E-13`/`J-03` (need an industry part kind) — they limit two rubric dimensions, not the thesis path.

## 2.1f ★★★ 2026-09-13 (late) — F10 built, Micron valued from EDGAR, `J-20` declared

## 2.1f ★★★ 2026-09-13 (late) — F10 built, Micron valued from EDGAR, `J-20` declared

> **Spend $0.00** — EDGAR is free, FMP was not called, `J-20` was dry-run only. Three `DX` rows
> (`DX-103`…`DX-105`). Every option below is also in its `DX` row; this is the reading order.

### What exists now that did not this morning

- **D-02 `valuation/`** (`F10`, 19/19 ACs): two-stage FCFF DCF minus net debt (`D2`, so `D-19` cannot
  recur), sensitivity band, implied stage-1 growth by bisection, assumptions `dcf_two_stage@v1` locked by
  content hash, and `fv_model` / `fv_analyst` as distinct types (`VS-1`).
- **Micron valued on real EDGAR facts** (no price — FMP not called): `fv_model` **$14.13/share** as of
  2025-06-26 (trailing FCFF $1,349M, net debt $5,378M, band $8.94–$20.68) and **$363.40** as of
  2026-09-13 (trailing FCFF $25,164M, net cash $19,273M, band $268.24–$483.28). Balance figures checked
  against the 10-Q: cash 10,163 · LT debt 15,003 · current debt 538 · shares 1,125M. ★ **A 26× swing on
  one cycle** — the reason `D5` exists.
- **`J-20` v1 — normalised earnings** (Stage A, blind): the model returns a METHOD from a closed set
  (`reported_ttm` · `cycle_average_fcff` · `cycle_average_fcff_margin` · `insufficient_evidence`), a
  window of ≥ 3 fiscal years with named trough and peak, and cited exclusions — **no amount field**.
  D-02 (`valuation/normalised.py`) computes; D-01 (`fundamental/valuation/normalise.py`) only validates
  and records provenance. The blind bundle gains an `annual_history` part (D6 FCFF, revenue, margin per
  fiscal year; unusable years say why). Runner: `run_judgement_once --block J-20 --annual-history
  <ledger>`; dry-run ≈ 73k input tokens, **≈ $0.77/call**.
- **Stage-B wiring:** `bundle_for(..., valuation_assumptions=…)` adds the valuation as a `computed` part
  (withheld from every blind view); opt-in, so every existing `bundle_hash` is unchanged. An unavailable
  valuation becomes a part NAMING what is missing (`P5`), never an absent part.
- **`J-07 v2`** text (the sentence *"You are NOT estimating normalised earnings…"* rewritten, `D5`) is a
  CANDIDATE in `e_blocks.py` — `BLOCKS` still ships `J-07 v1`, because shipping v2 needs a paid re-record.

### Real MU annual D6 FCFF (the input `J-20` will see), $M

| FY2017 | FY2018 | FY2019 | FY2020 | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|---|---|---|---|
| 3,792 | 8,661 | 3,281 | −69 | 2,231 | 2,771 | ⛔ unavailable (pretax loss) | −354 | 1,117 |

⚠ FY2016 also unavailable (pretax loss); revenue absent before FY2016 (older revenue tag not in
`CANONICAL`). ⇒ **Any cycle window containing FY2023 — the trough — refuses today** (`DX-104`).

### The issues, in the order they surfaced — and what was chosen

| # | Issue, plainly | Chosen | Rejected, and why |
|---|---|---|---|
| `DX-103` | Real MU quarters ABUT (gaps [1, 0, 0] days) — the contiguity rule 1–7 days refused them; MU files interest as `InterestExpenseNonoperating` and debt under lease-inclusive tags, which `CANONICAL` does not map | Contiguity 0–7 days; `VALUATION_FALLBACKS` in `basis.py` only, with `known_omissions` derived from the tags used | Adding the tags to `CANONICAL` now (moves every `f_*` feature under `FE-2` — a feature-contract version, Victor's call, left open) |
| `DX-104` | `D6`'s tax rate `t = tax ÷ pretax` is undefined in a LOSS year, so FY2016/FY2023 have no FCFF — and a cycle average needs exactly those troughs | Refuse the window, naming every unusable year (`AC-F10.19`); ⬜ **decision open**: `t = 0` in loss years (amends `AC-F10.17`) | Averaging around the gap (drops the troughs, biased high) · a statutory rate (a substituted default, `P5`) |
| `DX-105` | ⛔ The first `D5` build averaged the series in D-01 (`normalise.py` imported pandas). `RA-45`'s structural guard refused it | Averages moved to D-02 (`normalised.py`, `FORMULA_ID normalised.cycle_average_fcff_or_margin.v1`, MethodEntry added); D-01 holds no arithmetic; `AC-F10.19` added; `D5` / `CT-F10.3` text corrected | Exempting the file from `RA-45` (the guard is right: given a method and window, averaging is judgement-free) · reading `VS-4`'s *"plain code inside D-01"* literally (`VS-5` warns against exactly that) |

### ⚠ What went wrong in the WORK

1. **I misread `VS-4`** and put arithmetic in D-01; a structural test I did not write caught it. The spec
   text I had drafted said the same wrong thing — both corrected.
2. **Two mutation survivors** in the new D-02 averages (the `as_of` filing-date filter and the
   mixed-currency guard) — no test reached either. Both now have one; 6/6 + 4/4 mutations caught.
3. Earlier the same day, test-side slips: integer dict keys through `**kwargs`, Money JSON keys guessed
   as `amount_minor` (they are `minor`), pandas `itertuples` renaming `_`-prefixed columns.

### ⬜ Open, stated so they are not rediscovered

- `DX-104` — `t = 0` in loss years? (Victor) · `DX-103` — `CANONICAL` gains the fallback tags? (Victor)
- `F10` `Q2` — marketable securities (MU: cash $10,163M vs cash + investments $12,213M) and leases in net debt.
- **No price source yet** ⇒ `fv_analyst` and implied expectations are unproven on real data (FMP is paid).
- `J-20` not in `STAGE_A_ORDER`; never run live (💲 ≈ $0.77, needs approval); no golden case.
- `J-07 v2` not shipped (💲 re-record).
- ⚠ Small defect: the ingest CLI reads the SEC contact from `GMAIL_SMTP_USER`, but `.env` carries
  `EDGAR_CONTACT` — the run needed the variable passed by hand.

## 2.1e ★★★ 2026-09-12/13 — from declared blocks to the first DERIVED rubric scores

> The two days after the handoff. **Spend $12.57 on 09-13** (floor $50.51 over 80 calls all-time).
> 18 `DX` findings (`DX-85`ⓒ, `DX-89`…`DX-102`), 12 closed. Every option below is also in its `DX` row;
> this is the reading order.

### What exists now that did not on 2026-09-12

- **Evidence reaches judgement.** A bundle part kind carries VERIFIED extraction output (`DX-85`ⓒ);
  the Stage-A runner loads recorded E-block runs and re-verifies every quote against the filing first.
- **Rubrics are selected as criteria, and scores are derived** (`DX-100`) — through the inherited
  `score.py` contract the runner had bypassed.
- **The first rubric scores that mean something:** MU `balance_sheet_resilience@v3` = **3 · 3 · 3** and
  `capital_allocation@v3` = **4 · 4 · 4** over three option orders — now golden cases established by
  Victor.
- **Five guards** that did not exist: all-or-nothing rubric levels (`DX-98`), the subject guard
  (`DX-97`), `bundle_hash` in every trace record (`DX-95`), the stream tally (`DX-96`), and the
  repo-annotation refusal (`DX-102`).

### The issues, in the order they surfaced — and what was chosen

| # | Issue, plainly | Chosen | Rejected, and why |
|---|---|---|---|
| `DX-85`ⓒ | A judgement bundle had nowhere to put extraction output, so no rubric could ever be scored | A new `extraction` part kind whose declared ids must equal its FOUND items; only an `X-01`-verified pass may enter | Trusting declared ids (opens levels by assertion) · a new kind per block (one fact, many pins) |
| `DX-93` | `E-10`'s item line `sc.basic / sc.diluted` — a first-token parse drops the id the rubric needs | Parse slash-joined lines; pin it on the real block | — (found in pre-flight, before any spend) |
| `DX-97` | `E-13` "competitor capacity" returned 37 items, ALL Micron's own fabs, ALL passing `X-01` — which checks words are in the document, not that they answer the item | A deterministic guard: a competitor naming the registrant (read from the cover page) refuses the whole result; the old recording is refused on load | Refusing only the offending item (the capacity rows cannot be separated from it) · an `E-13 v2` now (no industry material exists to test it) |
| `DX-98` | With partial evidence the rubric offered ONE level — the floor — so a missing input would record a score of 0 | Score a dimension only when EVERY level has its evidence | Refuse only below two levels (still biased low) · score the partial range with a note (the note does not survive into the number) |
| `DX-99` | Every `earnings_quality` level required a FOUND non-GAAP adjustment, so a company with none could never be scored — against the rubric's own note | `searched:<id>`: satisfied when the block ran and explicitly returned the item, found or not; `earnings_quality@v3` | Treat `not_found` as evidence generally (breaks `RA-66`) · generalise to every rubric at once (each is a separate criteria decision) |
| `DX-95` | No trace record said which bundle a call read, so two Stage-A runs over different evidence looked comparable | `bundle_hash` in `CT-2.2` (F2 amended `A6`, spec first) | Recording it only in the runner's own lines (a second place to keep in step) |
| `DX-100` | ⛔ The rubric CRITERIA were sent nowhere: the model picked an integer 0-4 blind. The first gated scores (3, 0) were void | Criteria rendered (no scores) in a seeded, recorded order; answer = criterion text; score derived by `derive_score`; `insufficient_evidence` exit | Adding criteria to the prompt but keeping an integer answer (`RA-31`: *a number invites interpolation*) |
| `DX-101` | Once criteria were visible, two were decided by WORDING: *"headroom absent"* read as *"not disclosed"* (scored 1); *"no high-price buybacks"* silent on no buybacks at all (scored 4 on an assumption) | `v3` wording: undisclosed headroom → level 3; a window with no buybacks meets the condition. k=3 measured stable | k>1 first without rewording (Victor chose to fix) · requiring a buyback record for level 4 (absence scored as a defect, `DX-99`'s shape) |
| `DX-96` | `E-09` (and later E-10, E-12) hit the 20,000-token cap and returned `{}` | E-10 / E-12 fixed at `effort: low` · E-09 instrumented, `v2` prompt tried, summarized-thinking diagnostic — all failed · **skipped** | Thinking OFF (forbidden by `GW-9c`: the tool call leaks into text and never runs) · a higher cap (buys thinking) |
| `DX-102` | ⛔ Both filing fixtures began with this repo's annotation header — sent to the model as SEC evidence on every call | Header to a `.meta.txt` sidecar; its place filled with spaces so every line number and character offset survives; `build_bundle` refuses it | Deleting the header (shifts every citation, and fixing citations means editing signed golden sources) · blank lines only (**tried — broke an offset-pinned golden case**) |

### ⚠⚠ What went wrong in the WORK — recorded because the log is not a press release

1. **Two diagnoses of `E-09` drawn from a `{}`, both inference.** I reversed myself mid-run and killed
   an in-flight E-12 call on the reversed reading; E-10 succeeding minutes later falsified it. ★ The
   stream tally now MEASURES what a truncated call was doing — and was itself validated against
   successful calls before its zero was believed.
2. **A look-ahead accusation retracted.** The model's thinking mentioned *"the 10-K"*; the 10-Q says the
   same (line 1146). Checking the claim is what found `DX-102`.
3. **A red count read as the expected red.** After the first `DX-102` move, one failing regression test
   was assumed to be J-07; it had stopped at an offset-pinned AMD case. ★ Lesson, new: **list the
   diverged cases — never infer them from a count.**
4. **`DX-91` predicted `E-13` would return `not_found` and fail `X-01`.** It did neither; it returned
   37 plausible, verified, wrong items.

### ★★★ What remains — measured 2026-09-13 (census in §2.1c)

| | done | remaining |
|---|---|---|
| **Platform** (`F1`…`F9`) | 148 / 148 ACs · 12 CI guarantees | **0 %** |
| **Analysis blocks — declared** | 17 / 34 | **50 %** — 6 E-blocks, 11 J-blocks |
| **Analysis blocks — working** | 13 / 34 | **62 %** — the 17 undeclared, plus 4 declared-but-not-working (`E-09`, `E-13`, `J-03`, `J-04`) |
| **Thesis path** (`CT-9.2`: `E-01`…`E-13` + `J-01`…`J-17`, 30 blocks) | 13 working | **57 %** — and a thesis has NEVER been produced |
| **Golden coverage — blocks graded** | 7 / 34 · 7 / 30 on the thesis path | **79 %** of all blocks · **77 %** of the thesis path |
| **Golden coverage — rubric dimensions** | 2 / 4 (`balance_sheet`, `capital_allocation`) | **50 %** — `moat` needs real `E-13`, `earnings` needs `E-09` |

⚠⚠ **Block counts are not effort, and the two numbers should not be quoted without these caveats.**
(1) The undeclared J-blocks are Stages **B-D**, which consume Stage A's frozen output and D-02's
valuation trail — harder per block than Stage A was. (2) Two structural pieces are not blocks at all
and gate three of them: an **industry bundle part kind** (`J-03`, `J-08`'s supply read, a real `E-13`)
and D-02's **pre-computed series** in the bundle (J-04/J-06 cite *"the pre-computed series"* and the
blind bundle carries none). (3) `L3` §2.1c's standing rule applies to golden coverage: **do not grade
every block** — `D2` makes the fund manager's time the binding cost, so *"79 % ungraded"* is a ceiling on
what could be measured, not a target.

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

## 2.4 ★★ WHAT REMAINS — the definitive list, 2026-09-04

> ⚠ **Read this before starting anything.** `MS-1`–`MS-9` are built. What is left is
> **not more milestones** — it is a short list of things that need a human, plus one
> optional cleanup. ★ Nothing below blocks Q4 2026's improvement work.

### A. Build state

| | |
|---|---|
| Specs | **11 of 11 🟢 approved**, 149 ACs (`AC-5.17` added by `F5` `A1`), 50 recorded decisions |
| Code | ~38,000 lines, 15 domains, **one tree** |
| Tests | **1,675 collected · 1,670 pass · 5 skip · 0 fail** |
| Findings | **34 `DX` logged** — ★ **all 34 closed** |
| Guarantees | **8**, automated by `tools/check_all.py` + CI |

### B. ✋ Things I CANNOT do on your behalf — and exactly why

| # | Task | Why it is yours |
|---|---|---|
| ~~B1~~ | ✅ **Done 2026-09-05** — you copied the 4 statements to `.state/broker/bmo_investorline/`. `DX-12` closed; the 41 external-truth tests run | ⚠ Kept out of git by `.gitignore:32`. ★ Verify any time: `git status --short \| grep -i bmo` → no output |
| ~~B2~~ | ✅ **DONE 2026-09-07** — Victor committed upstream at `1261b36` *"retire old pipeline in stage B2"*. Both repos clean | ★★ **374 of 375 upstream deletions verified present in this repo**; the one exception, `src/__init__.py`, was deliberately removed (PEP 420, `DX-1`/`DX-2`) and must exist in neither. ✅ Tags cut: `pre-absorption-2026-09-07` upstream, `golden-set-live-2026-09-07` here. ⚠ This repo is **clean**; upstream holds 375 deletions + 12 modifications + 2 untracked |
| **B3** | **Publish the mirror** | Outward-facing and irreversible. A public repo cannot be un-published |
| **B4** | **Archive `ai-investment-pipeline`** (`MS-8.9`) | Same reason, plus `8.1` (clean tree + tag) is unmet |
| ~~B5~~ | ★★★ **CLOSED 2026-09-07 — the golden regression runs GREEN in CI.** Cases 1 and 2 established by Victor, wired to a real recorded `claude-opus-5` extraction, replayed with **no network call** (`D5`). ★ Mutation-verified: swapping the cumulative figure into the discrete case, dropping `cumulative_ytd`, nulling `period.start` or changing `unit` all turn it RED. ✏ was: **Cases 1 and 2 ESTABLISHED by Victor, 2026-09-07** — MU FY2025 Q3, CNBU segment revenue, discrete and cumulative. ★★ The live run independently reproduced **both**, including the period start the agent had misread. ⬜ Only `input_ref` remains, and that is mechanical | ⚠⚠ **The system may not do this.** Seeding from its own output would certify it against itself, and every regression would become the new expected value. `GoldenCase` **raises** if `established_by` names a pipeline component. ★ **Unblocked 2026-09-05** — until then there was nowhere to write a case. **Full instructions: §2.5 `F4`** |
| **B6** | **Run `F7a`** | Needs hand-written false challenges, a live `F6b`, and real spend. ★ `D1`: **~23 deliberations/arm** for `KEEP`, **~99** for `DELETE` |
| **B7** | **Add `UPSTREAM_REPO_TOKEN`** | ⊘ **Now obsolete** — `MS-8` merged the repos, so CI needs one checkout. Nothing to do |

### C. ✅ Things I CAN do, on request

| # | Task | Notes |
|---|---|---|
| ~~C1~~ | ✅ **`anthropic` licence verified 2026-09-04** — SDK **MIT**; whole transitive tree permissive. ⚠ `certifi` is **MPL-2.0** (weak/file-level, unmodified → no obligation) | `L5-dependency-licence-audit.md` now complete; ★ it also lists which licences **this project** may adopt |
| ~~C2~~ | ✅ **`DX-11` closed 2026-09-04** — 2 characterization files freeze the 2 inherited contracts this repo actually relies on. ⚠⚠ The framing was **wrong**: `src/quant/metrics/` and the relay are **not consumed**, only mentioned in comments | ★★ Writing it caught **four** wrong assumptions in code already written — see `DX-11`'s note |
| ~~C3~~ | ✅ **Gateway wrapped 2026-09-04** — `traced_transport()` closes `AC-2.2` at **call** granularity, with **zero edits** to inherited D-00 code | ★ Found `DX-16` on its first test |
| ~~C13~~ | ✅ **Done 2026-09-07 — the fixture is now citable.** `tools/convert_filing.py` folds `$` into the following cell and `%` into the preceding one, so **every cell is a semantic unit**: `CNBU \| $5,069 \| $2,573 \| ...` instead of `CNBU \| $ \| 5,069 \| $ \| ...`. ⚠ Verified **token-for-token**: 30,990 both renderings, nothing lost. ★ The golden cases' `quote` was updated and their `bundle_hash` is new — but their **VALUES did not change**, which is the point: a golden value is a fact about the document, not about our rendering of it. ⬜ A clean `input_ref` still needs one more live run (~$0.67) | ✏ was: ⬜ **Re-render the filing fixture for CITATION, not `grep`** — `$`/`%` are split into their own pipe-separated cells, which no reader can quote verbatim | ⚠⚠ Cause of 3 of the 6 live-run failures and the reason 13 attempts (~$7.88) never produced a clean `input_ref`. ★ After the fix, cases 1 and 2 must be **re-established** against the new fixture — a different rendering is a different `bundle_hash` |
| ~~C14~~ | ✅ **Resolved 2026-09-07** — identity carries the **span** for items whose value is not a figure; a FIGURE's identity is unchanged, so two values on one `(id, qualifier, period)` still collide. ★ Mutation-tested both ways: always adding the span kills the numeric guard, and the test says so | ✏ was: **`MP-18`'s identity does not fit NARRATIVE items** — three distinct `seg.basis_note` findings collide on `(evidence_id, '', period)` | ⚠ `E-01` asks for *"any statement"*, which is plural. The rule was derived from `seg.revenue` and over-fits it. ★ Likely fix: include the **span** in identity for items with no numeric value — but ⚠ that weakens the guard for the numeric case, so it needs a decision, not an improvisation |
| ~~C15~~ | ✅ **Resolved by Victor 2026-09-07: `5,069` with unit `millions of USD`.** Enforced in code (`AP-5`), not asked for in prose — the third constraint left to prose that came back wrong. ⚠ A symbol with no currency in `unit` **raises**: `$` is not always USD, and guessing is the silent default `P5` forbids | ✏ was: **Does `value` carry the currency symbol?** After `C13` the system returns `$5,069`, not `5,069` | ⚠⚠ Falsifies my own `C13` claim that rendering does not affect values. ★ `MO-1`: a bare value is not monetary — but carrying `$` in `value` AND "millions of USD" in `unit` states the currency twice. **Victor's call**; the golden cases' `expected` depends on it |
| **C4** | **Close `AC-F1.12`'s warning list** — declare real ports in `src/shared/ports/__all__` | ⬜ Still open. Currently empty by design; each real port needs its own spec first |
| ~~C12~~ | ✅ **Done 2026-09-07 — the trace can now state what a call cost.** `traced_transport` takes an injected `cost_of(model_id, tokens)`; pricing is **config** (`llm.pricing.*`) and `D-08` may not reach into `D-00` to read it, so it is passed in. ⚠ No pricer ⇒ `cost_usd` is **null, never 0** — *zero is a claim, null is an admission*, and a call recorded as free is worse than one recorded as unpriced (mutation-tested) | ⚠⚠ Found the hard way: after ~$6 of live runs, *"what did this cost?"* could not be answered from the trace and had to be recomputed by `tools/spend_report.py`. ★ **A run whose cost nobody can state is a run nobody can budget for** — and `GW-20`'s budget cap is enforced in memory, so nothing on disk shows what was actually spent |
| ~~C5~~ | ✅ **ID families reconciled 2026-09-04** (`MS-8.7`) — ⚠⚠ §1 was **~50 % incomplete**: 39 families in use, named nowhere (`DX-17`) | ★ Now **enforced** by `tools/check_id_families.py`, in `check_all.py` |
| **C6** | **Build the demo** (`9.4`) | ⊘ Descoped to 2027 by your decision (`QR-24`) |
| ~~C11~~ | ✅ **`MP-18` — the `evidence_id` convention, 2026-09-07.** Identity is now `(evidence_id, qualifier, period)`; the segment goes in `qualifier`, the id stays **bare** | ⚠⚠ Forced, not chosen: `b43_v1.py` maps `segments → "seg.revenue"` and `score.py` matches by **set membership on bare ids**, so a suffix breaks scoring *for a naming reason*. ★★ Resolving it found that **`E-01` could never have worked** — the old rule banned a repeated id, and E-01 returns one item per segment. Nobody noticed because nothing has ever run it (`DX-23`). ★ And the old rule's stated reason was **false**: coverage divides frozenset lengths, so duplicates cannot double-count. The hazard is *ambiguity*; the test is renamed to say so |
| ~~C10~~ | ✅ **Cases 1 AND 2 drafted 2026-09-07** — case 2 is the SAME CNBU row read from the nine-month column, ★ the only case exercising the `cumulative_ytd` scar tag and the only one using `MP-18`'s `period` component. **Case 1 filled 2026-09-07** — MU FY2025 Q3, CNBU segment revenue, from the real 10-Q now saved at `tests_src/fixtures/filings/MU_FY2025Q3_10Q.txt` (214 KB, EDGAR, provenance header) | ⚠ `established_by` deliberately left **blank** — filling it *is* the act of establishing (`D2`). ★★ `DX-24`: the agent misread the filing while preparing it and Victor caught it on first read — **`D2` demonstrated, not argued** |
| ~~C9~~ | ✅ **Done 2026-09-05 — the golden case is now VISIBLE.** `tools/demo_golden_case.py` records a pretend extraction, passes a case against it, then reds on a drifted reading. `tools/review_golden_case.py` attacks the harness with four adversarial checks | ⚠ Built because three written explanations had not landed — ★ **the reason golden cases felt abstract was that none had ever run.** Both approved by Victor 2026-09-05 |
| ~~C8~~ | ✅ **Done 2026-09-05 — `B5` unblocked.** `F5` `A1` added `CT-5.5` + `AC-5.17`: the golden set now has an on-disk format (`tests_src/fixtures/golden/<kind>.yaml`), a loader that validates on load, and three ready-to-edit templates | ⚠⚠ Found *because* I tried to write your `B5` instructions and could not: **a decision that assigns a human a task must leave them a way to do it.** ★ Also narrowed the mirror to withhold the golden set (`QR-12`), which surfaced `DX-19` |
| ~~C7~~ | ✅ **Done 2026-09-05** — `RC-65`/`RC-66` amended into `L1-recording`, then implemented. `RRSP_2` is now a **file drop** | ★ Surfaced `DX-18`; `src/recording/**` was also **ungoverned** in `ownership.yaml` and now is |

### D. ⛔ What "publishing" actually involves — beyond the demo

You asked what else is in it. Publishing is **five** things, and only one is the demo:

1. **`9.1` the mirror** — ✅ builder written and verified: **110 files, 259 tests green**, 0 strategy
   files, no git history. ⛔ *Creating the public GitHub repo and pushing* is not done.
2. **`9.2` `LICENSE` + README** — ✅ done. ⚠ The README opens with the `PG-10` disclosure.
3. **`9.3` dependency-licence audit** — ✅ done **except `anthropic`** (⛔ `C1`).
4. **`9.5` the essay** — ✅ done.
5. **`9.4` the demo** — ⊘ descoped to 2027.

★★ **Given no job applications in 2026 and heavy Q4 change expected, publishing has no deadline
and arguably should wait.** A mirror published now describes a system about to be rewritten, and a
public repo's history is the one thing you cannot curate afterwards.

### E. ✅ No open findings — all 26 `DX` closed, 2026-09-07

| | |
|---|---|
| ~~`DX-12`~~ | ✅ Closed — you copied the statements; the 41 external-truth tests run again |
| ~~`DX-15`~~ | ✅ Closed by `C7` — the loader **discovers** accounts from the directory, so `RRSP_2` in 2027 is a **file drop**, not a code change. ⚠ Surfaced `DX-18` on the way |
| ~~`DX-19`~~ | ✅ Closed — the mirror's dropper now follows imports one hop, and no longer publishes `.pyc` |
| ~~`DX-20`~~ | ✅ Closed — ⚠⚠ a golden case with an empty `expected` **loaded and PASSED**. Now refuses to load |
| ~~`DX-21`~~ | ✅ Closed — `replay_response` implemented. ★ **Run `python3 tools/demo_golden_case.py`** to watch a case pass, then red on a drifted reading |
| ~~`DX-22`~~ | ✅ Closed — ⚠⚠ the mirror shipped a **`check_all.py` that failed on first run**. The builder now *runs* it rather than guessing at dependencies |
| ~~`DX-23`~~ | ✅ Closed — characterization + a runnable path. ★ **`python3 tools/run_extraction_once.py --dry-run`** is free and prints the plan; `--live` (~$0.40) produces the recording and prints the `input_ref` |

★ **What remains is not a finding list — it is `B5`.** Everything else on this page is either done,
yours-and-deferred (`B2`/`B3`/`B4`), or waiting on real spend (`B6`).

## 2.5 ⚠ STEP BY STEP — what Victor does, in order

> ★ Ordered by value, not by effort. ✏ **Updated 2026-09-05: `F1` and `F3` are done.**
> ★★ **`F4` is now worth more than everything else here** — and it is the only item that is
> *yours alone by design* rather than yours by circumstance.

### ~~F1~~ · ✅ **DONE 2026-09-05** — the 41 dormant tests are running

You copied the 4 statements to `.state/broker/bmo_investorline/`. `DX-12` closed.
⚠ They are covered by `.gitignore:32` and cannot enter history — ★ confirm any time with
`git status --short | grep -i bmo` → **no output**.

★ `C7` then removed the hardcoded 4-account list: the loader now **discovers** accounts from that
directory, so **`RRSP_2` in 2027 is a file drop** (`RC-65`/`RC-66`, `DX-15` closed).

### F2 · Commit and review both repos · **30-60 min of reading**

⚠ Upstream holds **201 uncommitted deletions** (my absorptions) with **no tag to return to**.
Its git history is intact, so nothing is lost — but until it is committed there is no clean point.

```bash
cd ~/Workspace/collective-investment-ai-assistant && git status --short   # review, then commit
cd ~/Workspace/ai-investment-pipeline && git status --short               # 201 deletions + config edits
```

★ Suggested: tag both **before** committing the deletions, so the pre-absorption state has a name
(`git tag pre-absorption-2026-09-04`).

### ~~F3~~ · ✅ **DONE 2026-09-04** — licence audit complete (`C1`)

`anthropic` is **MIT**; the whole transitive tree is permissive. ⚠ One caveat worth remembering:
**`certifi` is MPL-2.0** — weak, file-level copyleft, and since it is used unmodified it imposes no
obligation. ★ `L5-dependency-licence-audit.md` also lists which licences **this project** may adopt.

### ★★ F4 · Establish `F5`'s golden values — `B5` · **an afternoon, then periodically**

> ⚠⚠ **Read this section in full before writing a single case.** It is the only task left that
> nobody else can do, and it is the one where doing it *slightly* wrong is worse than not doing it.

#### What a golden case actually is

A golden case is **one input, plus the answer you independently know is right, plus a record of how
you came to know it.** It is not a snapshot of what the system produced. That distinction is the
entire point, and `D2` puts it in code: `GoldenCase` **raises `CircularGoldenValue`** if
`established_by` or `source` names a pipeline component.

★★ **Why the check exists rather than a note in a doc.** The shortcut looks *better* than the real
thing at every moment you would take it: run the system, save its output as expected, and you get 30
cases in an afternoon and a permanently green suite. What you have actually built is a system
certified against itself, where **every regression silently becomes the new expected value.** The
suite would still be green the day the numbers went wrong. The check is in code because prose cannot
stop you at 11pm.

#### Where they live — new as of 2026-09-05

⚠ Until this week `D2` assigned you this task and left **nowhere to put a case** — `GoldenCase` was a
dataclass with no store, so the only way to add one was to edit Python literals. `F5` `A1` fixed that:

```text
tests_src/fixtures/golden/extraction.yaml   ← ★ start here
tests_src/fixtures/golden/thesis.yaml
```

Three files, one per kind, plain YAML, version-controlled. **Each already exists** with `cases: []`
and a commented-out worked example carrying the `D2` warning — you copy the example, uncomment it,
and edit. ⚠⚠ **The golden set is excluded from the `MS-9.1` public mirror** (`QR-12`): `ranking` and
`thesis` expected values *are* the strategy.

#### The three kinds — do them in this order

| kind | what *"correct"* means | how you establish it | difficulty |
|---|---|---|---|
| `extraction` | *"the FY2024 10-K reports revenue of $X"* | ★ **read the filing** | ★ easy — **do these first** |
| `ranking` | *"given these inputs on this date, these names ranked in this order"* | recompute by hand / in a spreadsheet | moderate |
| `thesis` | ⚠ **a judgement** — and recorded as one | your own reasoning, written down | hard, and honest about it |

★ **Start with 10 `extraction` cases.** They are objective, they are checkable by anyone, and they
are where the system's most mechanical failures live (⚠ the `fmp-api` skill's *"FMP guesses the
quarter and got Micron wrong by 71 %"* is exactly an extraction defect). **Ten of these alone turn
the regression suite from machinery into a measurement.**

⚠⚠ **A `thesis` case is a judgement, and the code knows it** — `is_judgement` is derived from the
kind, so simply putting a case in `thesis.yaml` marks it. ★ You cannot forget the flag, and you
cannot dress a judgement up as ground truth by omitting it. That matters because recording an opinion
as fact is the same category error as the circularity `D2` blocks — failing in the other direction,
by overstating what you know rather than by asking the system to grade itself.

#### The fields — ⚠ there are exactly six, and every one is required

```yaml
cases:
  - case_id: nvda-2026q2-revenue          # unique across ALL THREE files
    input_ref: filings/NVDA_2026Q2_10Q.txt  # ★ a REFERENCE to the input, not the input
    expected: {revenue_usd_m: 30040}      # ⚠ the value YOU established, never one the system produced
    source: "10-Q page 4, 'Total revenue' line"
    established_at: "2026-09-05"
    established_by: "Victor Truong"
```

⚠⚠ **Do not add a `kind:` line** — the loader supplies it from the filename, and a second one is a
`TypeError`. ⚠ There is **no `notes` field and no `is_judgement` field**: `is_judgement` is *derived*
(`kind == "thesis"` → true), so a `thesis` case is a judgement by virtue of which file it is in.
★ Anything you would put in `notes` belongs in `source`, where a reader will actually look.

★★ **`source` is the field that does the work.** In two years you will not remember why a number is
what it is, and a case you cannot re-derive is a case you cannot defend — which would defeat this
project's stated purpose (*explain and defend every recommendation*). Write it for a reader who has
never seen the case: the document, the page, the line.

⚠ **`established_by` is checked against a word list** — `pipeline`, `system`, `model`, `llm`,
`claude`, `gpt`, `agent`, `src.`, `auto`, `generated`, `gateway`. Both it **and `source`** are
scanned. Put your own name there. ★ If you ever see `CircularGoldenValue`, the check is working, not
breaking.

#### The one judgement call you will hit

⚠ Filings restate. When a later filing revises a number, **do not edit the case** — that is
back-filling history, and it destroys the record of what was knowable when. Add a **second** case
with its own `case_id` and a `source` naming the restatement, and let both stand. ★ This is the same
point-in-time discipline the `fmp-api` skill carries, applied to your own fixtures.

#### Do it, then check it

```bash
cd ~/Workspace/collective-investment-ai-assistant
$EDITOR tests_src/fixtures/golden/extraction.yaml       # copy the commented example, edit, repeat

python3 -c "from src.evaluation.golden.store import coverage; print(coverage())"
python3 -m pytest -q tests/unit/test_golden_store.py
```

`coverage()` prints a count per kind. ⚠ **A malformed file raises; a file with `cases: []` returns an
honest empty** — the loader will never quietly treat "I could not read this" as "there are none".

**Target: ~20–30 cases total.** ★ But **10 `extraction` cases beat 30 rushed ones**, and this is
explicitly a task you return to — add a case whenever you verify a number by hand anyway. The
suite's value grows with the set, and nothing is waiting on it being finished.

#### ★ Case 1 is drafted and waiting for you — `tests_src/fixtures/golden/extraction.yaml`

I wrote it as a **commented block at the bottom of that file**, with every `___` marking something
only you can supply. ⚠ It is commented out because a blank `expected` now *refuses to load*
(`DX-20`) — and it refuses because it used to load **and pass**.

**Why that case.** It targets the one extraction defect this project has already **measured** —
`fmp-api` trap 1, *FMP guesses discrete-vs-YTD from the period end alone and got MU wrong by 71 %*
(same class as `_cumulative_fys`: 41.5 % of TTM revenue, $379/share of fair value).

★★ **And it is Q3 on purpose.** The skill's measured rows show why:

| | cumulative | discrete | ratio |
|---|---|---|---|
| Q1 | 1,053 M | 1,053 M | **1.00×** ← ⚠ a Q1 case **passes under the bug** |
| Q2 | 2,188 M | 1,135 M | 1.93× |
| Q3 | 3,430 M | 1,242 M | **2.76×** ← maximum separation |

**A Q1 case cannot fail, because year-to-date *is* the first quarter.** Choosing Q3 is the
difference between a case that measures something and a case that decorates the suite — the same
lesson as `AC-F1.7`'s vacuous fixtures and `DX-9`'s shrinking tree.

#### ⚠ Where a golden case runs — it is NOT in the pipeline

★★ **A golden case never executes during a daily run.** It sits in the *measurement* lane (`F5`,
D-14, seat 9), which `ST-2` keeps one-way: **the harness imports the domains; nothing imports the
harness.** So a golden case cannot slow, alter, or break an analysis run — by construction.

```text
  ANALYSIS LANE (daily)                 MEASUREMENT LANE (CI / on demand)
  ─────────────────────                 ────────────────────────────────
  bundle ─► run_extraction()            extraction.yaml ─► load_kind()
              │  E-01…E-13, LLM                              │
              ▼                                              ▼
        ExtractedItem[]  ─── recorded ──►  run_regression(cases, replay_response)
              │  (F2 CT-2.2)                                 │
              ▼                                       compares to `expected`
        x01_verify_extraction()                              ▼
              │  deterministic, ABORTS               RegressionReport PASS|FAIL
              ▼
        judgement (J-blocks)
```

⚠ **Two different checks, often confused.** `x01_verify_extraction` runs *inside* the analysis and
asks *"is this quote actually in the bundle?"* — it catches hallucination, live, and aborts. A golden
case runs *outside* and asks *"is this the same reading we established months ago?"* — it catches
**drift**, which nothing in the analysis lane can see, because a confidently wrong reading verifies
perfectly against the document it was invented from.

#### ★★ First: watch one work. Two commands, ten seconds.

⚠ Three written explanations of golden cases did not land, and the reason was not the writing —
**none had ever run.** These two are approved and shipped:

```bash
python3 tools/demo_golden_case.py            # a case passes, then reds on a drifted reading
python3 tools/review_golden_case.py          # 4 adversarial checks; --verbose for every artifact
```

★ The demo shows the mechanism. ⚠ But the same author wrote the harness *and* the demo — §5.1's
named trap, *"the agent wrote both the code and the test, so of course they agree"* — so the
reviewer exists to **attack** it:

| | check | must |
|---|---|---|
| A | identical response | PASS — proves the verdict is computed, not printed |
| B | value changed | FAIL |
| ★★ **C** | **value IDENTICAL, only `period.start` dropped** | **FAIL** |
| D | recording deleted | RAISE — not skip, not pass |

**C is the one that earns the harness its trust.** Measured: breaking the comparison so it reads
only `value` leaves **A, B and D all green** — only C reds. A prompt change that keeps the headline
number while dropping the period start is `Period`'s named failure, *"reintroducing FMP's guess
inside D-01"*, and it is the class that cost 71 % on Micron.

#### ★★★ LIVE RUN — final tally, 2026-09-07

| | |
|---|---|
| attempts | **16** — ★★★ **CLEAN. `X-01` verified all 50 items.** |
| **measured cost** | **$9.67** over 16 recorded calls — `python3 tools/spend_report.py`. ★ The final run: **$0.5520**, 74,811 in / 7,119 out, 164 s |
| ⚠ true cost | **higher** — 2 calls reached the vendor and recorded no tokens |
| first estimate | $0.39 |
| ★ verdict | **the extraction reproduces both golden values**; 62 of 63 items pass `X-01` |

⚠⚠ **Why the estimate was out by ~18x.** Three compounding causes, each measured:

1. the token estimator used chars/4; this filing tokenises at **2.78 chars/token** (43 % low);
2. **~$1.56** burned on a silent `max_tokens` clamp that made `GW-23` report a ceiling never sent;
3. **~$2.40** on `high` effort before measuring that `medium` does the same job for $0.45.

★★ **Six defects, and not one was a model error.** Every failure was in the agent's wiring, and
every one was caught by a guard the project already had — `GW-23`, `X-01` (x2), `MP-5` (x2), `MP-7`.
⚠ The single defect *nothing* caught was the silent clamp, because it made a **true-looking error
message about a false number** — and that is the shape worth remembering.

★ **The one failure that is NOT the agent's stands unfixed**: `X-01` refuses a `seg.basis_note`
whose cited sentence does not contain its value. A citation that does not support its value is
exactly what the guard is for, so it was left to fail.

##### ⛔ Why it was stopped, and what must change first

Runs 12 and 13 both died on **verbatim quotation of a TABLE ROW**, and the cause is the fixture, not
the model. `tools`' HTML→text conversion renders a row as

```text
SBU | 1,451 | 16 | % | 1,392 | 17 | % | 1,353 | 20 | % | 4,574 | 18 | % | 2,911 | 17 | %
```

— every cell pipe-separated, with `$` and `%` as **cells of their own**. Run 13's model quoted that
row with `$ |` cells *inserted* where the document has none. ⚠ Asking any reader to reproduce that
character-for-character is asking them to transcribe a delimiter artefact, and `X-01` — correctly —
refuses anything that is not literal.

★★ **Three of the six failures now trace to that converter** (curly quotes from `html.unescape`, a
literal `\u00a0`, and now pipe/`$` cell splitting). The fixture is shaped for `grep`, not for
citation, and the extraction contract is built on citation.

⚠⚠ **Do not spend another ~$0.67 per attempt until the converter is fixed.** ★ The fix is to render
table rows as readable text — collapse `$`/`%` into their adjacent value, single-space columns —
and then RE-ESTABLISH cases 1 and 2 against the new fixture, because a different fixture is a
different `bundle_hash`. ⬜ Recorded as `C13`. ✅ **Done** — and it took **two** passes, below.

★ **None of this weakens what was proven**: the extraction reproduced both golden values on runs 5,
8, 12 and 14, from four independent calls, including the period start the agent had misread.

##### ✅ `C13` — the converter, fixed in two passes

**Pass 1** — `$` and `%` were pipe-separated cells of their own. Folded into their values, so every
cell is a semantic unit: `CNBU | $5,069 | $2,573 | ...`. ⚠ Verified **token-for-token**: 30,990 both
renderings, nothing lost.

**Pass 2** — run 14 still failed, and the cause was a **single non-breaking space**:

```text
fixture:  Form\xa010-K          ← &nbsp; from the HTML
model:    Form\x0cfff10-K       ← the model GARBLES U+00A0 rather than copying it
```

⚠ The old cleanup collapsed *runs* of two-or-more spaces, so a lone `\xa0` survived. All exotic
whitespace is now a plain space. ★★ **Four of the seven live-run failures trace to this converter**,
and the lesson was identical every time: **a fixture must be shaped for CITATION, not for `grep`.**

⚠⚠ **Fixing the fixture does not fix an already-recorded response.** Run 14's stored quote still
carries the garbled character, so **65 of 66** quotes locate against v3 and the last one cannot —
its corruption predates the fix. ★ I did **not** teach the locator to accept `\x0cfff`: that is model
corruption, not a rendering artefact, and tolerating it would weaken the check to make my own run
pass. ⬜ Confirming v3 therefore needs one more live call (~$0.67).

##### ⚠⚠ Run 15 — the converter is FIXED, and it surfaced two design errors of mine

✅ **All 59 quotes locate.** The `$`/`%` cells and the non-breaking space are gone as failure causes.
✅ **58 of 59 items pass `X-01`.**

**⛔ Finding 1 — `MP-18`'s identity is WRONG for narrative items.** Three *genuinely different*
`seg.basis_note` findings collided:

1. *"Business units reorganized effective Q4 2025…"*
2. *"The changes will require us to recast our segment reporting…"*
3. *"Certain reclassifications have been made to prior-period amounts…"*

All three carry `('seg.basis_note', '', (None, '2025-05-29'))`. ⚠ They are not duplicates — `E-01`
asks for *"**any** statement that the segmentation changed"*, which is plural by nature. ★★ I derived
`MP-18` from `seg.revenue` — numeric, per-segment, per-period — and it does not fit a **narrative**
item that is legitimately unqualified and repeated. A rubric citing `seg.basis_note` wants *all* the
notes; `evidence_coverage` counts the id once either way, so there is no ambiguity to guard against.
⬜ **Unresolved. Recorded as `C14`** — the likely fix is that identity includes the **span** for
items carrying no numeric value, but that is a change to a rule written 24 hours ago and should not
be improvised.

**⛔⛔ Finding 2 — `C13` falsified a claim I made about `C13`.** I wrote that re-rendering changes
`bundle_hash` but *"the VALUES did not change — a golden value is a fact about the document, not
about our rendering of it."* ⚠⚠ **Run 15 returns `$5,069`, not `5,069`** — because the fixture now
renders the currency symbol into the same cell. ★ The rendering leaks straight into the extracted
value, so the claim was wrong and the golden cases' `expected.value` no longer matches what the
system produces.

★ The underlying question is real and is the fund manager's: is the value `5,069` with
`unit: "millions of USD"`, or `$5,069`? ⚠ `MO-1` says a bare value is not monetary — which argues
for the currency being *somewhere*, but carrying it in **both** `value` and `unit` states it twice.
✅ **Resolved as `C15`** — `5,069` + `millions of USD`, confirmed against run 15's recording for **$0**.

##### ⬜ What is left: ONE item, and it is the model's error, not ours

With `C13`, `C14` and `C15` applied, run 15's recording replays to **58 of 59 items verified**. The
last one is `seg.basis_note`, where the model wrote a **paraphrase** as the value —
*"Business units reorganized effective Q4 2025; segment reporting to be recast … into CMBU, CDBU,
MCBU, and AEBU"* — while quoting the document's actual sentence. ⚠ `X-01` refuses it, correctly: a
summary presented as an extraction cannot be checked against the source.

★ The schema now states the rule (*a text item's value must be a VERBATIM SUBSTRING of its quote —
do not summarise*), but that is a **prompt-side** fix and can only be confirmed by a live call.
⚠⚠ **Everything else is verified offline at $0**, which is `F5` `D5` finally being used as designed.

#### ★★ The live run — 11 attempts, what it proved, and what it cost

*2026-09-07. `tools/spend_report.py` recomputes this from `F2`'s traces; ⚠ it is a **floor**, not a
total (see below).*

**★★ What it proved — the question worth asking, answered.** Run 5 returned 66 items, and the
extraction reproduced **both golden values exactly**:

| case | value | period | tag |
|---|---|---|---|
| 1 | `5,069` | 2025-02-28 → 2025-05-29 | — |
| 2 | `14,028` | 2024-08-30 → 2025-05-29 | ★ `cumulative_ytd` |

⚠⚠ Including `2025-02-28` — **the period start the agent misread and Victor corrected** (`DX-24`).
★ The model agreeing establishes nothing (`D2` is unmoved); what it shows is that the extractor
*currently* reads this filing the way the fund manager established it. **That is exactly the
baseline a golden case exists to freeze.**

**⚠ Every failure was in the agent's own wiring, and every one was caught by a guard that already
existed.** Not one was a model error:

| # | found by | what it was |
|---|---|---|
| 1 | `GW-23` | truncation at the output ceiling |
| 2 | `X-01` | a prose sentence written into `value` — ★★ `MP-7` predicted it word for word: *an LLM with no stated way to say "I could not" will always find something to say*. The schema had no `not_found`. |
| 3 | `MP-5` | `evidence_id` was a free string with a *description* saying "never invent one" — **all 56 items came back tagged `E-01`**, the block id. A description is prose; an `enum` is the API. |
| 4 | `X-01` | curly-vs-straight quotes — ⚠ and the curly quotes came from **our own** `html.unescape` |
| 5 | ⚠⚠ nothing | **a silent `max_tokens` clamp to 16,000**: the gateway asked for 20,000 then 32,000 and neither was ever sent, while `GW-23` reported *"hit max_tokens=32000"* — **a number never sent**. Cost two runs (~$1.56) chasing a ceiling not in force. |
| 6 | `MP-5`, again | `quote` left out of `required` — the model returned a **found** item with no quote at all |

★★ **Three of six are one mistake: describing a constraint instead of declaring it.** `MP-5` says
the shape is enforced by the API, not by prose, and it was right every time.

**★ Effort is the lever, not `max_tokens`.** Measured on one bundle:

| effort | output tokens | latency | cost |
|---|---|---|---|
| `high` | 13,243 – 32,000 | 215-349 s | $0.71 - $1.18 |
| **`medium`** | **2,595** | **33 s** | **$0.45** |

⚠ Raising `max_tokens` buys more *thinking*, not more headroom — adaptive thinking expands into
whatever budget it is given. Extraction is **transcription, not reasoning**; `high` stays right for
judgement blocks.

**⚠⚠ What it cost.** `python3 tools/spend_report.py` — **~$6.40 measured over 11 calls**, against a
$0.39 first estimate. Where it went:

- the estimator was **43 % low** (chars/4; this filing tokenises at **2.78 chars/token** — tables of
  `|` separators and digits are far denser than prose). Recalibrated.
- ~$1.56 wasted on the silent clamp.
- ~$2.4 on `high` effort before measuring that `medium` does the job for $0.45.

⚠ **It is a floor, not a total.** The `Brotli` run reached the vendor, ran **516 seconds**, and
failed to *decode* locally — billed, with `tokens: {}` recorded. ★★ **A call that is served and then
lost locally still costs money, and no trace can see it.** The Anthropic console is authoritative.

#### ★★ Final state of the live run — 12 attempts, and the last failure is the RIGHT one

**62 of 63 items verify. `X-01` refuses one — and it is a genuine model error, not an artefact.**
For `seg.basis_note` the model cited one sentence (*"We completed reorganization of our operations
…"*) and gave a **different, adjacent** sentence as the value (*"The changes will require us to
recast our segment reporting …"*). ⚠ A citation that does not support its value is precisely what
`X-01` exists to catch, and `RA-6`/`RA-132` are right to abort the pass.

★★ **I did not weaken the guard to make it pass, and that is the point.** Four earlier `X-01`
failures were *my* artefacts and were fixed at the source (typography our own converter introduced,
a literal `\u00a0` escape, a locator stricter than the check it fed, a missing `not_found` path).
This one is not mine to fix, so it stands.

★ **Both golden values verify in the same recording:**
`5,069` (2025-02-28 → 2025-05-29) and `14,028` (2024-08-30 → 2025-05-29, `cumulative_ytd`).

⚠⚠ **But the recording is still unusable as an `input_ref`.** `X-01` is a *deterministic ABORT over
the whole pass* — one unsupported citation refuses all 63 items, by design: *"an unverified fact
entering a judgement is a hallucination with a scorecard built on it."* ★ So `F5` cases 1 and 2
cannot point at this run. A re-run (~$0.45) may well come back clean, since this is one item out of
63 and not a systematic fault.

**Two findings worth keeping:**

1. ⚠ **The model emitted FIVE identical `not_found` items for `seg.assets`** — no qualifier, no
   period, so all five carried one `MP-18` identity and `ExtractionResult` refused them. Collapsed in
   `parse_items`: with no qualifier and no period they are literally the same claim, and
   `evidence_coverage` counts ids as a set. ★ `found` items are **never** collapsed — two values
   sharing an identity is real ambiguity, which is what `MP-18` is for.
2. ★★ **The whole pipeline now runs end to end offline.** The recorded response replays through
   `parse_items` → `ExtractionResult` → `X-01` with no API call, which is `F5` `D5`'s whole argument
   arriving: **once a call is recorded, every later check is free.** The last four fixes cost $0.

#### ⚠ `DX-23` step 5 — decisions taken without you, and what was rejected

*2026-09-07. You authorised the spend; ⛔ **the machine has no Anthropic credentials at all** — no
`ANTHROPIC_API_KEY`, no `ANTHROPIC_AUTH_TOKEN`, no `ant` CLI, no `~/.config/anthropic/` — so the live
call could not run and **$0 was spent**. Everything below was decided to keep moving.*

| # | Decision | Rejected, and why |
|---|---|---|
| 1 | **Verify offsets and `tokens_in`/`tokens_out` against a stub** built from the SDK's documented shape, exercised over the **real 211,895-char filing** | ✗ *Wait for the key* — leaves the wiring wholly unverified; ✗ *a toy filing* — the offset arithmetic is only interesting at real scale and against real duplicated substrings |
| 2 | **Split `to_transport_result()` out of the transport** so the mapping is testable without a network call | ✗ *Test through the client with a mock* — mocks the SDK's shape, which is the one thing a stub cannot establish; splitting at least makes the assumption explicit and one function wide |
| 3 | **Compute character offsets in code, ask the model only for the `quote`** | ✗ *Ask for offsets too* — `RA-131`: the offset is the one part of a citation the model cannot also author, and asking spends tokens to manufacture a failure `X-01` would reject anyway |
| 4 | **Whole filing as the bundle**, with `--segment-note-only` as an 18× cheaper option | ✗ *Default to the slice* — ⚠ a narrower bundle is a **different `bundle_hash`**, so a golden case recorded against one does not transfer. Cheap, but it silently splits the golden set |
| 5 | **`llm.deep.temperature` deliberately ABSENT** from the config | ✗ *Set a temperature* — `GW-8a` treats its presence as the error and Opus 5 rejects it outright (400) |
| 6 | **Budget cap $2/run** | ✗ *No cap* — the gateway raises rather than overspending; ✗ *$0.50* — too tight for one retry on a ~$0.40 call |

★★ **The failed live attempts were worth more than the call would have been.** Reaching the vendor
takes a working config, registry, bundle, seam, gateway and trace — and each attempt failed at the
next link, finding **four real defects for $0**:

1. **`Config`, not a dict** — the gateway calls `cfg.get_optional(...)`. ⚠ `DX-11` caught this exact
   assumption once already and I repeated it.
2. **`llm.deep.model_id`**, not `llm.model.deep`. ★ `CF-1` refused to invent a value, which is the
   rule doing its job.
3. **`CallResult.parsed` is the raw text string**, not a parsed object — `Gateway.complete` sets
   `parsed = text` unless a schema is passed. My first test fed it an SDK `Message` and got a type
   error, which is how the shape got pinned down rather than assumed.
4. ⚠⚠ **`DX-26` — the trace lied.** Three attempts left ONE trace holding four sentinels reading
   `SUCCESS, SUCCESS, FAILED, SUCCESS`, the last for a run that had just failed.

#### ✅ `DX-21` closed — and ⚠ my earlier recommendation here was wrong

I previously offered *"fixture now, recording later"* and recommended the fixture. **That option does
not exist.** A filing is an *input*; comparing it to `expected` means *producing* an extraction from
it — an LLM call — which `D5` forbids in CI. Only the recording is both a product of the system and
available offline. `input_ref` is now `<run_id>/<call_id>` (`A3`, `AC-5.18`).

★★ **Run this to see the whole mechanism in ten seconds:**

```bash
python3 tools/demo_golden_case.py
```

It records a pretend extraction, passes a case against it, then ships a "v2 prompt" that reads the
YTD column instead — and reds. ⚠ Everything it writes is fake and thrown away.

#### ⚠⚠ The consequence for case 1: its two halves land at different times

| half | established by | when |
|---|---|---|
| `expected` · `source` | ★ **you, reading the filing** | **today** — it is a fact about the document and never changes |
| `input_ref` | a recorded call | ⚠ **after the first real run** — `.state/` has no runs; `QR-23` suspends the daily one |

★ **Write `expected` now anyway.** The truth is the scarce half, and establishing it while you have
the filing open is the whole discipline; the wiring is mechanical and can follow. Leave the case
commented out until its recording exists.

**Target: ~20–30 cases total.** ★ But **10 `extraction` cases beat 30 rushed ones**, and this is
explicitly a task you return to — add a case whenever you verify a number by hand anyway. The
suite's value grows with the set, and nothing is waiting on it being finished.

#### ★ Case 1 is drafted and waiting for you — `tests_src/fixtures/golden/extraction.yaml`

I wrote it as a **commented block at the bottom of that file**, with every `___` marking something
only you can supply. ⚠ It is commented out because a blank `expected` now *refuses to load*
(`DX-20`) — and it refuses because it used to load **and pass**.

**Why that case.** It targets the one extraction defect this project has already **measured** —
`fmp-api` trap 1, *FMP guesses discrete-vs-YTD from the period end alone and got MU wrong by 71 %*
(same class as `_cumulative_fys`: 41.5 % of TTM revenue, $379/share of fair value).

★★ **And it is Q3 on purpose.** The skill's measured rows show why:

| | cumulative | discrete | ratio |
|---|---|---|---|
| Q1 | 1,053 M | 1,053 M | **1.00×** ← ⚠ a Q1 case **passes under the bug** |
| Q2 | 2,188 M | 1,135 M | 1.93× |
| Q3 | 3,430 M | 1,242 M | **2.76×** ← maximum separation |

**A Q1 case cannot fail, because year-to-date *is* the first quarter.** Choosing Q3 is the
difference between a case that measures something and a case that decorates the suite — the same
lesson as `AC-F1.7`'s vacuous fixtures and `DX-9`'s shrinking tree.

#### ⚠ Where a golden case runs — it is NOT in the pipeline

★★ **A golden case never executes during a daily run.** It sits in the *measurement* lane (`F5`,
D-14, seat 9), which `ST-2` keeps one-way: **the harness imports the domains; nothing imports the
harness.** So a golden case cannot slow, alter, or break an analysis run — by construction.

```text
  ANALYSIS LANE (daily)                 MEASUREMENT LANE (CI / on demand)
  ─────────────────────                 ────────────────────────────────
  bundle ─► run_extraction()            extraction.yaml ─► load_kind()
              │  E-01…E-13, LLM                              │
              ▼                                              ▼
        ExtractedItem[]  ─── recorded ──►  run_regression(cases, replay_response)
              │  (F2 CT-2.2)                                 │
              ▼                                       compares to `expected`
        x01_verify_extraction()                              ▼
              │  deterministic, ABORTS               RegressionReport PASS|FAIL
              ▼
        judgement (J-blocks)
```

⚠ **Two different checks, often confused.** `x01_verify_extraction` runs *inside* the analysis and
asks *"is this quote actually in the bundle?"* — it catches hallucination, live, and aborts. A golden
case runs *outside* and asks *"is this the same reading we established months ago?"* — it catches
**drift**, which nothing in the analysis lane can see, because a confidently wrong reading verifies
perfectly against the document it was invented from.

#### ⬜ Then one decision from you — `DX-21`

⚠ A case can now be **written** but not yet **run**: `run_regression` takes a `replay_response`
callable and **no implementation exists**; nothing resolves an `input_ref`. There are also **zero
recordings** (`.state/` holds only `broker/` — the daily run is suspended by `QR-23`). The spec and
the code even disagree on what `input_ref` names:

| | `input_ref` means | What it needs | Trade-off |
|---|---|---|---|
| ★ **A — filing fixture** (`CT-5.2`: *"the fixture"*) | a file in `tests_src/fixtures/filings/` | just the filing | ★ checkable offline, no run required, stable forever. ⚠ Grades extraction **logic**, not the live fetch |
| **B — `F2` recording** (`run.py`: *"serves the recording"*) | a recorded response | a real run first | grades the **whole path** incl. the vendor. ⚠ Blocked on `QR-23`, and re-records on every change |

★ **My recommendation: A now, B later** — they are not exclusive, and A is the half that works
today. I left it open rather than guessing because it changes what `input_ref` is allowed to be, and
that is a contract, not an implementation detail.


### F5 · Run `F7a` when you want the deliberation answer · **real spend**

⚠ Needs hand-written false challenges (`D3`) and a live `F6b`.
★ `D1`'s economics: **~23 deliberations per arm** to establish `KEEP`, **~99** for `DELETE`.
**Run the KEEP test first** — if the ratio lands ≤0.33 the expensive one is never needed.
⚠⚠ **Do not widen the DELETE band to save money** — that is a threshold chosen after seeing the
*cost*, which is the same failure as choosing one after seeing the data.

### F6 · Publishing — ⊘ **no deadline; consider waiting**

Given no 2026 job applications and heavy Q4 change, ★ a mirror published now describes a system
about to be rewritten, and **a public repo's history is the one thing you cannot curate later.**
When you do want it: `python3 tools/build_mirror.py` (dry-run) → review → `--out DIR
--i-have-read-the-refusals` → inspect → create the public repo and push **that directory**, not
this one.

---

## 2.6 ⚠ Where the BMO statements should live — and why not where they are

**Asked 2026-09-04:** *"I want to copy the 4 CSVs to some formal place, because that is how I will
update the AI agent with my actual transactions at end of day."*

### The current location is wrong for a book of record

`src/recording/book/load.py` reads from
**`sdd/design/rel6_design/samples/bmo_investorline_transactions/`**. Three things are wrong with it:

| | |
|---|---|
| `sdd/` | the **spec tier** — authoritative documents. ⚠ A file you overwrite daily does not belong in the tier that governs the code |
| `rel6_design/` | **release-scoped and frozen**. Release 6 is over; its design record should not keep changing |
| `samples/` | says *fixture*. ⚠ These are the **live book of record** — the opposite of a sample |

### ★ Recommended destination

```text
   .state/broker/bmo_investorline/TransactionHistory_<ACCOUNT>.csv
```

- ✅ **`.state/` is already git-ignored** — the data cannot enter history.
- ✅ It is where run state already lives, so backups and retention already cover it.
- ✅ It sits **outside** the spec tier, so `sdd/` stays documentation.
- ✅ `$BMO_STATEMENTS_DIR` continues to override it for tests and one-off runs.

### ⚠⚠ And it will not accept `RRSP_2` without a code change — `DX-15`

`ACCOUNTS` is a hardcoded 4-tuple. A fifth statement dropped into the directory would be **silently
ignored**: not read, not refused, not mentioned. ★ The fix is to **discover** accounts from the
filenames rather than list them — which also removes the need to touch code in 2027.

⚠ Both changes alter inherited D-11 behaviour and have **no covering AC**, so constitution §5.1
requires amending `L1-recording` first. Recorded, not done unilaterally.

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
| **S5** | **The human path** | `F8` + `F9` | 30 ACs | ★ **Tightest coupling in the corpus.** `QR-16`'s "full depth" is asserted from both sides (`AC-8.1`, `AC-F9.7`) — **check they agree.** Largest session. Also the new directives design, and ⚠ `F8` `Q3` (auth), which must not slip past first deployment | ⬜ |
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
| **Does "full depth" mean the same on both sides?** | `AC-8.1` ↔ `AC-F9.7` | Each asserts it independently; only together does a mismatch show |
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
| 1.4 | ★ **Closed variant set** — every selectable variant registered at startup (`QR-7`) | `F1` | ✅ `AC-F1.5` |
| 1.5 | ★ **Instance caching per `(port, variant)` within a run** | `F1` | ✅ `AC-F1.6` — *run scope* = one `Registry` instance (`F1` `D1`) |
| 1.6 | ★★ **One contract-test suite, parameterised over every registered variant** | `F1` | ✅ `tests/contracts/` |

**Built 2026-09-03 — `31 passed, 1 skipped`, all 15 ACs mutation-verified (16 mutations, all caught).**

✏ **Amended the same day (`F1` `A1`).** The build raised **five spec defects that the `S1` review did
not find** — a contradiction between `CT-1.3` and `CT-1.4`, an unmechanised term in `AC-F1.12`, a
residual false positive in `AC-F1.7`, a missing `ports()` method, and untested `CT-1.1` rules. ★ Reading
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
| 6.2 | ✅ `ThesisSourcePort` — **both adapters through ONE contract suite** (`F1` `AC-F1.9` on a real port); `D2` one prompt, two transports | 2 | `F9` |
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

### ✅ `MS-8` — one tree, 2026-09-04

**1,524 passed, 46 skipped, 0 failed.** ★ `src/` now holds every domain; upstream's `src/`,
`tests_src/` and `pipeline/` are gone.

**The `MS-8` checklist worked.** Every item written at `MS-2.5` fired as predicted: `8.1a`'s
`.gitignore` check confirmed the BMO path covered **before** copying; `8.3`'s *"`sdd/` is a test
input"* (`DX-4`) was needed; `8.4a`'s glob-ordering assertion — built early at `MS-2.7` — passed
unchanged; `8.5a`–`8.5d` retired the pin, inverted the smoke test, and returned `pythonpath` to `.`.

⚠ **Two findings the rehearsal did not predict:**

- **`DX-10`** — absorbing upstream's tests brought its **process assumptions**. Its AC regex
  `AC-\d+\.\d+` does not match `AC-6a.1` (the `F6a`/`F6b` split is **this repo's own**), and
  ★★ `test_the_vision_is_release_independent` asserted the vision names *"Portfolio Manager"* —
  **upstream's five-seat vocabulary**, which `CLAUDE.md` explicitly forbids carrying between the
  repos. **The absorbed test did the exact thing the working agreement warns against.**
- **`DX-11`** — ⚠ **~17,000 lines absorbed and not one characterization test written**, which
  constitution §5 item 3 requires. Caught by upstream's own guard, which the absorption brought with
  it. One real test now freezes the inherited contract `F2`'s `traced()` depends on; the rest is
  recorded, not closed.

⚠⚠ **`DX-12` is open and needs one manual step from Victor.** The real BMO statements could not
travel (`.gitignore`d by design), so **41 external-truth tests now skip on Victor's machine too** —
the merged tree has *less* verification than upstream had. ★ The fresh-clone check is now identical
to the normal run, which is exactly why nothing looked wrong.

⛔ **`8.9` — retiring `ai-investment-pipeline` — was NOT done.** Archiving a repo is outward-facing
and effectively irreversible, and upstream still holds **201 uncommitted deletions** with no tag to
return to (`8.1` unmet). ★ Its `src/` is empty but its git history is intact, so nothing is lost.

> ★★ **The test of whether `L4`'s structure was right** *(restated for per-domain absorption)*: **every**
> absorption — `MS-2`'s and this one — moves files with **zero content changes** and merges globs into
> `ownership.yaml`. **Anything more means `PG-8` was violated somewhere earlier** — a finding about the
> plan, not about the merge. ★ And now it is tested repeatedly instead of once, at the end.

## MS-9 — Write-up, mirror, polish

| # | Item |
|---|---|
| 9.1 | 🟨 **`tools/build_mirror.py`** — positive allowlist, dry-run default, refuses on anything `.gitignore`d. Verified: **110 files, 259 tests green, 0 strategy files, no history — and the mirror's own `check_all.py` passes there (`DX-22`).** ⛔ **NOT PUBLISHED** — publishing is Victor's |
| 9.2 | ✅ **`README.md`** — ⚠ opens with the `PG-10` status disclosure (IC 0.0203, *t* = 1.42) and a *What is deliberately not working* section |
| 9.3 | ✅ **Dependency-licence audit** — `L5-dependency-licence-audit.md`. No copyleft; ⛔ `anthropic` UNVERIFIED (not installed). ★ Surfaced `DX-13` |
| 9.4 | ⊘ **DESCOPED by Victor 2026-09-04** — *"I will not apply for any job in 2026, and lots of new improvement is expected in Q4 2026."* ★ A demo built now would demo a system about to change. ⚠ It is **deferred, not cancelled**: `MS-9.4` is the portfolio artifact for the 2027 transition |
| 9.5 | ✅ **`docs/essays/E1-what-the-process-caught.md`** — 1,400 words on **thirteen things the process caught that review did not**, and a *What is not true here* section |

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
| **DX-10** | 2026-09-04 | MS-8 | Absorbing upstream's tests brings its coverage | ⚠⚠ **It also brings its PROCESS ASSUMPTIONS.** `tests/test_sdd_process.py` enforces upstream's SDD conventions against **this repo's** specs, and 4 of them are wrong here: (a) the AC regex `AC-\d+\.\d+` does not match `AC-6a.1` — the `F6a`/`F6b`/`F7a`/`F7b` split is **this repo's own**; (b) `test_code_governing_specs_have_globs` does not know `F7a`/`F7b` live under `F5`'s glob, which `ownership.yaml` records in a **comment**, not machine-readably; (c) ★★ `test_the_vision_is_release_independent` asserts the vision names *"Portfolio Manager"* — **upstream's FIVE-seat vocabulary**, which `CLAUDE.md` explicitly forbids carrying between the repos: *"Never carry a seat number between the two models."* **The absorbed test does exactly that** | `tests/test_sdd_process.py` | ⚠ material | ✅ **resolved 2026-09-04** | Regex widened to `AC-\d+[a-z]?\.\d+`; `F7a`/`F7b` given **real globs** ordered before `F5`'s broad one (`L4` §5.1), so the comment becomes machine-readable; the vision test now asserts **this repo's nine-seat** vocabulary with the `CLAUDE.md` warning quoted beside it |
| **DX-11** | 2026-09-04 | MS-8 | Constitution §5 item 3: *relying on inherited behaviour ⇒ characterization test to freeze it before building near it* | ⚠⚠ **~17,000 lines were absorbed across `MS-2`/`MS-6`/`MS-8` and NOT ONE characterization test was written.** Upstream's own suite freezes that behaviour in effect — but it is not **labelled**, so the inventory is not greppable and nobody can tell which tests exist to freeze legacy behaviour rather than to assert it is correct. ★ Caught by upstream's own `test_characterization_tests_are_labelled`, which the absorption brought with it | constitution §5 item 3 · `tests/test_sdd_process.py` | ⚠ material | ✅ **resolved 2026-09-04** | **Two** characterization files now freeze the two inherited contracts this repo's own code actually relies on: `Orchestrator.run`'s `invoke` dispatch (`traced()`) and the **LLM gateway's transport** (`traced_transport`). ★★ The framing was also **corrected**: an audit of our platform modules found they import almost nothing inherited — `src/quant/metrics/` and the relay are **not consumed**, only *mentioned in comments*, so §5 item 3 (*"relying on inherited behaviour"*) does not reach them. ⚠⚠ Writing the gateway one caught **four** wrong assumptions in code already written — see the note |
| **DX-12** | 2026-09-04 | MS-8 | `DX-5`'s loud skip means a clone reports honestly; the fund manager's machine still runs the external-truth tests | ⚠⚠ **After absorption they are DORMANT EVERYWHERE.** The real BMO statements were deliberately excluded from the `MS-8` copy (they are `.gitignore`d and must never enter history), so the merged repo has **no** path to them — **41 external-truth tests now skip on Victor's machine too.** ★ The merged tree therefore has *less* verification than upstream had, and the fresh-clone check is now **identical** to the normal run, which is why nothing looked wrong | `sdd/design/rel6_design/samples/bmo_investorline_transactions/` (absent) · `tests_src/broker_fixtures.py` | ⚠ material | ✅ **resolved 2026-09-05** | Victor copied the 4 statements to **`.state/broker/bmo_investorline/`** (`RC-66`) and the resolver was repointed. ★★ **41 external-truth tests run again: 1,601 pass / 5 skip, from 1,550 / 46.** ⚠ Restoring the data immediately exposed **`DX-9` a FOURTH time** — two modules still named the old `sdd/` path directly, invisible while they were skipping |
| **DX-13** | 2026-09-04 | MS-9.3 | The absorption checklist moves FIVE things (`DX-3` + `DX-8`) | ⚠⚠ **A SIXTH: runtime dependency DECLARATIONS.** `pyproject.toml` here declared a `dev` extra and **no runtime dependencies at all**, while `MS-8` moved in 15 domains needing `pandas`, `numpy`, `PyYAML`, `lightgbm` and `anthropic`. ★★ Worse: **`lightgbm` was never declared in EITHER repo** despite 3 import sites in `src/models/`. ⚠ Nothing failed because the dev machine already had everything installed — a clean environment would fail at import with no hint what to install, and `MS-9.1`'s mirror would have shipped a `pyproject.toml` that cannot build what it describes | `pyproject.toml` (both repos) · `src/models/zoo/gbdt.py` | ⚠ material | ✅ **resolved 2026-09-04** | Six runtime dependencies declared. ★ **The rule is now SIX things: code · tests · globs · architecture rules · config · dependency declarations.** Found by `MS-9.3`'s licence audit, which was looking for something else entirely |
| **DX-14** | 2026-09-04 | MS-9.1 | The curated mirror (`QR-12`) ships the platform layers and withholds the strategy | ⚠⚠ **The mirror could not run its own test suite.** Six collection errors: `tests/` imports `src.orchestration.jobs`, `src.data_engine`, `src.recording` — domains the curation **deliberately removes**. ★★ A reviewer's first action on a source-available repo is `pytest`, so this would have been the **first impression**: a project whose central claim is verification discipline, shipping a suite that does not collect. ⚠ Found only by **building the mirror and running it** — the dry-run reported 108 files, no refusals, and looked correct | `tools/build_mirror.py` · `tests/` | ⚠ material | ✅ **resolved 2026-09-04** | The builder now **computes** which included tests import excluded modules and drops them, **reporting the count** rather than filtering silently. ★ A derived exclusion cannot drift from the allowlist the way a hand-kept list would |
| **DX-15** | 2026-09-04 | — | Adding a 5th portfolio (`RRSP_2`, planned 2027) is a matter of dropping a 5th CSV into the statements directory | ⚠⚠ **It is a CODE CHANGE.** `src/recording/book/load.py:27` hardcodes `ACCOUNTS = (("RESP_1","RESP"), ("RRSP_1","RRSP"), ("TFSA_1","TFSA"), ("TFSA_2","TFSA"))` and `tests_src/test_recording_book_load.py:32` asserts exactly those four. A 5th statement would be **silently ignored** — the loader would not read it, `RK-5`'s all-or-nothing aggregation would still return a book, and the new portfolio would simply not exist. ★★ Separately, `EXPORT_DIR` points at **`sdd/design/rel6_design/samples/`** — the loader's book of record lives in the **spec tier**, inside a **release-scoped, frozen** design directory, under a name (`samples/`) that says *fixture* | `src/recording/book/load.py:27,31` · `tests_src/test_recording_book_load.py:32` | ⚠ material | ✅ **resolved 2026-09-05** | `L1-recording` amended first (`RC-65`, `RC-66`, `AC-11.47/48`), globs wired in the same change (§5 item 2), then implemented. ★ **Verified: dropping `TransactionHistory_RRSP_2.csv` in is picked up with no code change.** ⚠ A hardcoded `ACCOUNTS` also had to leave **three** test modules that had copied it |
| **DX-16** | 2026-09-04 | — | `AC-2.9`'s redaction removes credentials from traces and leaves everything else | ⚠⚠ **It silently destroyed the cost accounting of every traced call.** `SECRET_KEYS` was matched as a **substring**, and `"token" in "tokens"` is `True` — so `tokens`, `max_tokens`, `input_tokens`, `tokens_in` all became `<redacted>`. ★★ Every `ExternalCall` would have recorded `<redacted>` where the usage numbers belong, and `F5`'s cost metrics would have had nothing to read. ⚠ The same looseness missed a real credential in the other direction: `x-api-key` did **not** match `api_key` (hyphen vs underscore) and was caught only by the value regex. ★ Found by a call-level test asserting an **exact** token count — a test asserting "not empty" would have passed | `src/orchestration/trace/redact.py` | ⚠ material | ✅ **resolved 2026-09-04** | Word-boundary matching on separator-normalised keys, so `x-api-key` matches and `tokens` does not. ⚠ Bare `token` stays ambiguous (`auth_token` vs `token_count`) and is disambiguated by a **short** quantity-word list — sized by the asymmetry that **over-redacting a count is recoverable and under-redacting a credential is not.** 16 regression cases, both directions |
| **DX-17** | 2026-09-04 | MS-8.7 | Constitution §1 is the ID registry — *"read before inventing an ID"*, *"every family below is reserved"* | ⚠⚠ **After the merge it was ~50 % incomplete: 39 families in active use and named nowhere** — `SEAT`, `FR`, `X`, `V`, `CF`, `PD`, `FX`, `MP`, `K`, `H`, `MO`, `T`, `SC`, `PRC`, `WF` and 24 more. ★★ §1 had **already been corrected on 2026-09-02** for missing eleven, so this is the *second* time the registry was found half-written — which is the point: a list maintained by hand drifts, and one that reads as authoritative while half-written is how `M-n` (mandate) and `M<n>` (milestone) collided | `sdd/specs/constitution.md` §1 | ⚠ material | ✅ **resolved 2026-09-04** | All 39 declared, and ★ **enforced** by `tools/check_id_families.py` + 4 tests, now in `check_all.py`. ⚠ Two collisions documented rather than renamed: **`SEAT-n` is upstream's FIVE-seat model** beside this repo's nine (`CLAUDE.md` forbids carrying one between them — and an absorbed test already did, `DX-10`), and **`Q` now has four live meanings** |
| **DX-18** | 2026-09-05 | C7 | `RC-65`'s *"an empty export directory raises"* is a clean rule | ⚠⚠ **It broke `load_books`' own contract.** That function documents *"Return `(books, unavailable_reason)`… carry the refusal forward as a **reason** rather than as a crash"* (`RC-10`, `RK-5`) — so raising turned an orchestration job from `SUCCESS` into `FAILED` on any tree without the exports. ★★ Caught by the **fresh-clone check** (`DX-5`'s `BMO_STATEMENTS_DIR=/nonexistent` run), which is the only check that exercises the no-data path — the normal suite has the data and never sees it | `src/recording/book/load.py` · `L1-recording` `AC-11.48` | ⚠ material | ✅ **resolved 2026-09-05** | **Split by layer, and both rules kept:** `discover_accounts` **raises** (at a query, "no accounts" is an error), `load_books` **catches and returns the reason** (*a refusal that cannot say what it lacks is the defect `RC-10` exists to prevent*). `AC-11.48` amended to name both halves. ★ The fresh-clone check earned its place twice in one session |
| **DX-19** | 2026-09-05 | B5 | `DX-14`'s dropper removes every mirror test that reaches a withheld path — it scans each test file for imports of withheld modules **and** for path literals naming withheld directories | ⚠⚠ **It scans the test file only, and a test can reach a withheld directory through a constant it imports.** `test_golden_store.py` names no path at all: it does `from src.evaluation.golden.store import GOLDEN_DIR`, and `GOLDEN_DIR` is the withheld `tests_src/fixtures/golden`. The mirror shipped it and it failed there — **1 failed, 259 passed** — a public repo whose own suite is red on first clone. ★ Also found alongside: `_files_for` filtered `__pycache__` **only in the test scan**, so the mirror was publishing `.pyc` files — and a `.pyc` embeds the **absolute source path** it was compiled from, leaking `/home/<user>/Workspace/…` | `tools/build_mirror.py::unrunnable_tests` · `_files_for` | ⚠ material | ✅ **resolved 2026-09-05** | **Detector follows imports one hop:** for each first-party module a test imports, its source is appended to the text scanned for path literals. `.pyc`/`.pyo` and `__pycache__` excluded at the copy step, not just the scan. ★★ Both halves are the same shape as `DX-9` — *a check that stops checking* — but this is the first time it was the **indirection** rather than the shrinking tree that blinded it: the checker was correct about every file it read, and wrong about which files to read |
| **DX-20** | 2026-09-05 | B5 | `CT-5.2` validates a golden case on construction — `case_id`, `input_ref`, `source` and `established_by` are all required, and `D2`'s circularity check runs — so a case that loads is a case that was established | ⚠⚠ **`expected` itself was never validated.** A half-written case — the field present but empty, which is exactly the state a case is in while the fund manager is still reading the filing — **loads as valid** with `expected is None`. ★★ And it does not merely load: `run_regression` compares with `==`, so when the system produces nothing (extraction returning `NOT_FOUND`, a stub, a failed call) the case **PASSES**. Measured: `verdict PASS, passed=('half-written',)`. ⚠ This is the worst instance of the *check that stops checking* family yet found, because every previous one went **red or silent — this one goes GREEN**, and a green regression is read as evidence | `src/evaluation/golden/models.py::GoldenCase.__post_init__` · `regression/run.py` | ⚠ material | ✅ **resolved 2026-09-05** | `CT-5.2` amended: **`expected` must be established** — `None` raises `ValueError` naming the case. ★ *Absent* remains expressible, but only **explicitly** (`expected: {status: NOT_FOUND}`), because *"the document does not say"* is a finding and *"I have not looked yet"* is not. ⚠⚠ Found while writing the **first real golden case** — the placeholder I was about to hand Victor would have loaded and passed |
| **DX-21** | 2026-09-05 | B5 | With `CT-5.5` in place, a golden case can be written **and run** — `run_regression(cases, replay_response)` grades each case's `input_ref` against a recorded response | ⚠⚠ **`replay_response` has no implementation.** It is a `Callable` parameter, supplied only by fakes in tests; nothing anywhere resolves an `input_ref` to a real recording or fixture. ★ And there is nothing for it to resolve **to**: `.state/` holds only `broker/`, because the daily run is suspended (`QR-23`) and `F7a` has never run, so **zero recordings exist**. ⚠ Also a live spec/code disagreement on what `input_ref` even names — `CT-5.2` says *"the fixture"*, `run.py` says *"serves the recording"* | `src/evaluation/regression/run.py` · `CT-5.2` | ⚠ material | ✅ **resolved 2026-09-05** | ★★ **The third rung of the same ladder.** `B5` needed somewhere to write a case (`DX-19`'s `A1`), a refusal to accept an unestablished one (`DX-20`), and now something to grade it against. ⚠ Left open rather than guessed: the resolver's shape depends on whether cases grade against **filing fixtures** (`CT-5.2`'s reading — checkable, offline, no run needed) or **`F2` recordings** (`run.py`'s reading — needs a real run first). **Settled on the RECORDING** (`A3`, `AC-5.18`): a filing is an *input*, and producing an extraction from it would need an LLM call, which `D5` bans in CI — so the fixture reading was never implementable. `recorded_response()` resolves `<run_id>/<call_id>` from `F2`'s payload store; expiry, a missing recording and a malformed ref all raise rather than skip. ⚠⚠ My own earlier recommendation (*"fixture now, recording later"*) was **wrong** and is recorded here as such. ★★ And `OR-3` **caught the first attempt**: `replay.py` imported `TraceStore` directly. Two fences meet here and both bind — `OR-3` (no domain imports orchestration) and `ST-2` (nothing imports the harness) — so neither direction is legal and the adapter is wired by the **caller**, `tools/f2_payload_reader.py`. ★ That is right, not a workaround: the regression is CI's (`T1`), and must not be reachable from a production run. ⚠ Consequence for case 1: `expected` can be established today from the filing, but `input_ref` waits for the first real run (`QR-23`) |
| **DX-22** | 2026-09-05 | 9.1 | `DX-14` taught the mirror to verify itself — it drops tests that import withheld domains, *"the mirror must be able to run its own suite"*, and the suite runs green there | ⚠⚠ **The suite is not the only thing that must run.** The mirror ships `tools/check_all.py` — the documented entry point, the one a reader runs first — and it invokes `tools/check_id_families.py`, which is **not in the allowlist**. A fresh clone of the public repo gets `⛔ 1 CHECK(S) FAILED: can't open file 'tools/check_id_families.py'`. ★★ The guard was written for **tests importing code**, and missed **a tool invoking a tool** — a second kind of dependency it never modelled. ⚠ Found only because I ran the mirror's `check_all.py` rather than its pytest | `tools/build_mirror.py` INCLUDE · `check_all.py` | ⚠ material | ✅ **resolved 2026-09-05** | `check_id_families.py` added to the allowlist, **and** the builder now **runs the mirror's own `check_all.py`** as a build step — the generalisation `DX-14` should have made. ★★ Third time in this family (`DX-14` tests, `DX-19` an imported constant, `DX-22` a subprocess): **every time the mirror's self-check was written against one kind of dependency, a second kind was already shipping broken.** The fix is no longer *"check the dependency I thought of"* but *"run the thing and see"* |
| **DX-23** | 2026-09-05 | B5 | `F5`'s `extraction` golden cases grade the output of `run_extraction` — the E-block runner, `WF-1` step 2 — so that function is the producer the whole `extraction` kind is defined against | ⚠⚠ **`run_extraction` is called by NOTHING and exercised by NO TEST.** `grep` finds it in `extract.py` (its definition), `__init__.py` (its export) and one docstring — no job, no CLI, no test. ★★ Two consequences: (a) an `input_ref` **cannot exist**, because there is no runnable path from a filing to a recorded extraction, so case 1 can be *established* but not *wired*; (b) constitution §5 item 3 — *relying on inherited behaviour ⇒ characterization test first* — is unmet for the function `F5`'s extraction contract is built on. ⚠ Not found earlier because every golden-path test supplies its own recorded response and never asks who produces one | `src/fundamental/filings/extract.py::run_extraction` | ⚠ material | ✅ **resolved 2026-09-07** | ✅ **Characterization done** — `tests/test_characterization_extraction.py`, 4 tests, fake seam, **no spend**: one call per block, `RA-5` refuses a judgement block *before* the seam is reached, `X-01` aborts on a quote not in the bundle, and the two-row segment table survives (`MP-18` end to end). ★★ It immediately caught a wrong assumption of mine: `X-01` refuses a value *"assembled from two places"*, so cases 1 and 2 must cite the **whole CNBU row** — one quote containing both figures — and the quote canNOT distinguish the columns; only `period` does. ✅ **Steps 1-4 built, no spend:** `src/fundamental/prompts/e_blocks.py` registers `E-01 v1` **byte-identical to the spec** (guarded by `tests/structural/test_prompt_text_matches_spec.py` — ★ `block()`'s self-hash catches a later file edit but *cannot* catch code and doc disagreeing, since it only ever sees one of them); `tools/anthropic_transport.py` is the D-00 transport with `MP-5`'s `strict: true` tool schema; `tools/run_extraction_once.py` builds the bundle, computes offsets in code (`AP-5` — a model-supplied offset is a number it cannot verify and we can), wires `traced_transport` → `Gateway` → `AnalysisGateway`, and caps spend at $2. ⬜ **Step 5 is one command Victor runs** — `--live`, ~$0.40, and it prints the `input_ref` prefix for cases 1 and 2. ⚠⚠ It does **not** block `B5`'s human half: `expected` is established from the **filing**, not from a run, so the scarce judgement can be captured now and the wiring can follow |
| **DX-24** | 2026-09-07 | B5 | While preparing case 1, the agent reported that MU's 10-Q *"never states the quarter's start date"*, and sourced `period.start` from SEC's XBRL instead — presenting it as the `fmp-api` skill's claim confirmed in a real document | ⚠⚠ **The claim was false, and the agent had already surfaced the disproof.** Item 2 (lines ~1996-2000) is introduced *"In the third quarter of 2025…"* and lists three contiguous fiscal months ending at the quarter end, so the start (2025-02-28) is in the text. ★★ An earlier `grep` in the same session **returned line 2000** and the agent dismissed it as *"the share repurchase table, not the fiscal quarter start"* — it saw the evidence and explained it away, then generalised a true statement about the DATA SOURCES (FMP exposes only the period end) into a false one about the DOCUMENT. ⚠ Caught by Victor on first read | `tests_src/fixtures/golden/extraction.yaml` note (b) | ⚠ material | ✅ **corrected 2026-09-07** | `period.start` now sourced to Item 2, with XBRL as **corroboration** rather than the source — which is strictly better provenance, since a human can now re-check the whole case from the document alone. ★★ **This is the single best argument for `D2` produced so far, and it is not an argument — it is an instance.** The agent reading a filing to establish a golden value made a confident, well-reasoned, wrong reading, and dressed it in a citation to a skill. ⚠ Had `established_by` been filled in automatically, that error would have entered the golden set as ground truth and every future extraction would have been graded against it |
| **DX-25** | 2026-09-07 | B5 | `AC-5.18` wired `input_ref` → recorded response → `==` against `expected`, and the four adversarial checks in `review_golden_case.py` all pass | ⚠⚠ **The two granularities do not match.** ONE recorded `E-01` call returns EVERY segment row in BOTH columns; ONE golden case pins ONE item. `run_regression` compares the whole response with `==`, so a single-item `expected` can **never** match — measured: `produced` is a list of 4, `expected` is a dict, verdict FAIL forever. ★★ Invisible until now because every test and the demo recorded a response shaped like exactly one case — **the fixtures were built to the harness rather than to the producer**, which is the `DX-23` gap (`run_extraction` untested) showing up one layer out. ⚠ Also found alongside: `qualifier` was missing from `ExtractedItem.to_json_obj()`, so `MP-18`'s discriminator never reached the wire and two segment rows serialised identically | `regression/run.py` · `replay.py` · `filings/models.py` | ⚠ material | ✅ **resolved 2026-09-07** | `input_ref` gains an optional **selector fragment** — `<run_id>/<call_id>#<evidence_id>|<qualifier>|<start>:<end>` — and the selector **is `MP-18`'s identity**, so the golden set's granularity and the extraction's identity are the same thing rather than two conventions that must be kept in step. ⚠ No match or several matches raises `UnresolvableCase`; ★ a bare ref without `#` still compares the whole response, which is what a single-item block wants. `qualifier` now serialises, with a test — *identity that does not survive serialisation is not identity* |
| **DX-26** | 2026-09-07 | DX-23 | `run_extraction_once.py --live` records the call and closes the trace, so `AC-2.12` can tell a finished run from a crashed one | ⚠⚠ **Three defects, all found by RUNNING it — three `--live` attempts left ONE trace holding FOUR `__run_closed__` records reading `SUCCESS, SUCCESS, FAILED, SUCCESS`, the last one for a run that had just failed.** (a) `finally: store.close("SUCCESS")` closed as SUCCESS **whatever happened** — the trace asserting success about a failure is the exact *trace-and-run-disagree* defect this project hit once before, in the recorder; (b) `run_id` was `run-<date>-e01`, **the same string all day**, so repeated runs appended to one trace instead of each getting their own; (c) `TraceStore.close()` accepts a **second** call and appends another sentinel — `AC-2.12` reads sentinel ABSENCE as INCOMPLETE, and contradictory sentinels are worse than none. ★★ None of this was visible from the test suite: every test closes once, on a fresh tmp_path, after a success | `tools/run_extraction_once.py` · `src/orchestration/trace/store.py::close` | ⚠ material | ✅ **resolved 2026-09-07** | Run id gets a **timestamp**; `close()` is called **once** with the real outcome; and `TraceStore.close()` now **raises on a second call** (`AC-2.8`'s append-only argument applied to the sentinel — a record that can be written twice is not append-only). ⚠⚠ Recorded as the cost of the credential gap being useful: **the run never reached the vendor and cost $0, yet found three defects** |
| **DX-27** | 2026-09-07 | DX-23 step 5 | With the schema and budget corrected, one live `E-01` call over MU's 10-Q completes and gives `F5` cases 1 and 2 their `input_ref` | ⚠⚠ **Nine live runs, ~$6, and the pipeline still has not completed end to end** — though ★★ **run 5 proved the thing that mattered: the extraction reproduced BOTH golden values exactly** (`5,069` / 2025-02-28 and `14,028` / 2024-08-30, `cumulative_ytd` correctly tagged), including the period start the agent had misread and Victor corrected. Five defects were found, every one in the agent's own wiring and every one caught by a guard the project already had: `GW-23` truncation · `X-01` prose-in-`value` (`MP-7` predicted it word for word) · `X-01` typography · the `evidence_id` enum (`MP-5` — all 56 items came back tagged `E-01`) · and ⚠⚠ **a silent `max_tokens` clamp to 16,000 that made `GW-23` report a ceiling that was never sent**, costing two runs (~$1.56) chasing a number not in force | `tools/anthropic_transport.py` · `prompts/call.py::MAX_TOKENS` | ⚠ material | ✅ **resolved 2026-09-07** | ✅ Fixed: the clamp, the enum, the `not_found` path, optional `unit`, typographic normalisation in `X-01` (mutation-tested in **both** directions — it lost tolerance only for punctuation *our own converter* introduced). ⬜ **Remaining:** output spend measured at **13,243 → 32,000 tokens on identical input with no code change** — adaptive thinking is genuinely variable and expands into whatever budget it is given, so raising `max_tokens` is not the lever. ★ **Recommendation: drop `llm.deep.effort` from `high` to `medium`.** Extraction is transcription, not reasoning; effort is the documented first cost lever, and it bounds thinking directly rather than licensing more of it. ✅ **Closed on run 16**: `medium` effort, the re-rendered fixture (`C13`), `MP-18` corrected for narrative items (`C14`), the currency moved to `unit` (`C15`), and subset comparison. **50 items extracted and verified, $0.5520.** ★★ `B5` closed — §2.7 |
| **DX-28** | 2026-09-07 | B5 | `CT-5.2` validates a golden case on construction, and after `DX-20` the fields a human must supply — `source`, `established_by`, `expected` — all refuse a blank | ⚠⚠ **`established_at` did not.** Victor signed cases 3-10, and all eight kept the template's `____-__-__` in `established_at`; `load_all()` accepted every one and `coverage()` reported **ten established when eight were half done**. ★★ Exactly `DX-20`'s family — *a placeholder that validates is a placeholder that ships* — and the third time a required field turned out to be required in prose only. ⚠ Found because the agent **verified the claim** rather than taking *"signed all 10 cases"* at face value | `src/evaluation/golden/models.py::GoldenCase` | ⚠ material | ✅ **resolved 2026-09-07** | `established_at` must match `^\\d{4}-\\d{2}-\\d{2}$`, mutation-tested. ★ A blank left in a template is exactly the state a signature is supposed to end, so the field recording WHEN refuses a blank as firmly as the one recording WHO — a golden value nobody can date is one nobody can audit against the filing as it stood |
| **DX-29** | 2026-09-07 | E-01 v2 | Bumping `E-01` `v1`→`v2` adds one paragraph requiring a verbatim value, and should change WHAT is returned, not what it costs | ⚠⚠ **The first `v2` run TRUNCATED at 32,000 output tokens.** Same bundle, same `effort: medium`: `v1` ran **2,595** and **7,119** output tokens; `v2` hit the **32,000** cap — >4.5x the larger `v1` run — for $1.17 and 341 s, and `GW-23` refused the half answer. ★ Plausible mechanism: requiring a value findable inside its own quote makes the model search and re-check spans instead of summarising. ⚠ **n=1, and adaptive thinking already varies 13,243→32,000 on identical input** (`DX-27`), so this is NOT yet distinguishable from variance | `prompts/call.py::MAX_TOKENS` · `E-01 v2` | ⚠ material | ✅ **resolved 2026-09-08 — the hypothesis was WRONG** | ★★ **Settled by a controlled A/B for $0.46** — same 15,163-char slice, same effort, only the prompt varying: `v1` **7,034** output tokens / $0.2111, `v2` **8,328** / $0.2441. ⚠ **1.18x, not 4x** — the 32,000 truncation was adaptive-thinking variance (`DX-27`), exactly as suspected but not assumed. ★★★ And the arms disagreed on OUTCOME, which the cost question had hidden: **`v1` FAILED and `v2` PASSED.** `v1` returned 49 items that collided on `MP-18` identity; `v2` returned **64 items, all identities unique, `X-01` verified every one**. ⚠⚠ So `v2` is not a compliance tax — it is **~18 % more output for a run that finishes instead of aborting**, and the agent's own "`v2` buys compliance, not correctness" framing was wrong twice over |
| **DX-30** | 2026-09-08 | filing 2 | `GW-23` calls a truncated response *"a failure, not a short answer"*, which reads as a warning against USING the partial output | ⚠⚠ **There is no partial output.** Every 32,000-token truncation recorded — `v1`, `v2`/MU and `v2`/AMD alike — returned a payload of **2 characters**. Adaptive thinking consumes the whole budget and the tool call is never emitted: the run is **all-or-nothing**. ★★ So a truncation costs FULL PRICE for ZERO items — AMD's cost **$1.1825** and produced nothing — and `GW-23` is more right than it reads: there is no short answer to be tempted by | `shared/llm/gateway.py::GW-23` · `prompts/call.py::MAX_TOKENS` | ⚠⚠ **major** | ✅ **resolved 2026-09-08 — and the fix INVERTS the intuition** | ★ Raising `max_tokens` is known NOT to be the lever (`DX-27`: thinking expands into whatever budget it is given), and this finding explains WHY — the budget is spent on thinking, not on the answer. ⚠⚠ **The lever is `effort`.** At `medium`, MU succeeded 3 times (2,595 / 7,119 / 9,865 output) and failed once at the cap; AMD failed on its first attempt — plausibly because a **completed restatement plus nested sub-rows** is genuinely harder reasoning, which is exactly why AMD was chosen. ★★ Expected cost at `medium` is ~$1.00 per SUCCESS once failures are counted; `low` should cut both the thinking and the failure rate, and extraction is transcription rather than reasoning. ⚠⚠ **Tested and both hypotheses failed.** `effort: low` truncated on a 3,688-token input (`DX-31`), and `E-01 v3` — which demonstrably fixes the restatement trap on the slice (7,401 out, $0.20) — **still truncates on AMD's FULL filing** (2 for 2, $1.18 each). ★ So: MU-full completes, AMD-slice completes, **AMD-full does not**, under either prompt. AMD's full document carries a difficulty that is not the restatement clause and is **not yet identified**. ⛔ Stopped guessing at $1.18 per hypothesis. ★★★ **The structural mitigation is to make failure CHEAP rather than rare**: since a truncation yields zero items whatever the cap, `max_tokens` should be set just above the largest OBSERVED successful answer (MU used 9,865) rather than at a generous 32,000. A 12,000 cap fails at ~$0.68 instead of $1.18 and succeeds on everything that has ever succeeded — ★★★ **It DID fix AMD.** A controlled pair, same filing, same prompt `v3`, **identical 76,551 input tokens**, only the cap varying:  `cap=32,000 → 32,000 out, truncated, $1.1828, 246 s, ZERO items`  vs  `cap=12,000 → 7,584 out, COMPLETE, $0.5724, 67 s, 38 items verified`. ⚠⚠ **The generous cap CAUSED the failure.** `DX-27` had inferred that thinking expands into whatever budget it is given; this is the first controlled demonstration of it, and it means a larger ceiling is not insurance — it is a **risk**. ★★ Four AMD runs failed at 32,000; the first at 12,000 succeeded. The lever was never `effort` and never the prompt alone — it was the ceiling itself |
| **DX-31** | 2026-09-08 | filing 2 | `DX-30` said a truncation means adaptive thinking spent the budget, so the lever is `effort` | ⚠⚠ **`effort: low` truncated too — on a 3,688-token input.** Verified from the recorded request: `effort: 'low'` was genuinely sent, `thinking: adaptive`, and the model still burned the full **32,000** output tokens in 241 s for **$0.8184** and produced nothing. ★★★ At that input size this is not tuning, it is pathological — and the cause is the PROMPT, not the setting: `E-01 v2` says *"If the company restated prior-period segments, return **BOTH** the as-originally-reported and the as-restated figures"*, AMD's filing states a retrospective restatement **and contains only the restated figures** — no *"as previously reported"*, no *"as originally"*, nothing. ⚠⚠ **The prompt demands something the document does not contain and offers no way to say so.** `MP-7` gives `not_found` per ITEM; *"both figures"* is a cross-cutting instruction with no escape, so the model cannot even reach the failure output — it thinks until the budget dies | `E-01` v2 · `L1-fundamental-analysis-master-prompt` §E-01 | ⚠ material | ✅ **resolved 2026-09-08 by `E-01 v3`** | ★★★ `MP-7`'s own principle failing one level up: *an LLM with no stated way to say "I could not" will always find something to say* — here it cannot even do that. ✅ **`E-01 v3` fixes it, measured**: the same slice that burned 32,000 tokens producing nothing under `v2` completed under `v3` in **7,401** output tokens, **$0.2037**, 63 s, with a full tool call. ★ The fix is two sentences — *"If the filing presents only ONE basis, return that basis and say which one it is in a `seg.basis_note`. Do not search for figures the filing does not contain."* ⚠ `v3` is a **CANDIDATE**: `E01_CURRENT_VERSION` still names `v2`, because shipping it retires filing 1's recording (`L7` §5). ★★ **This is precisely why filing 2 was chosen** — MU only ANNOUNCED a recast, so the clause was unreachable and the defect invisible |
| **DX-32** | 2026-09-08 | filing 2 | `--segment-note-only` gives a cheap bundle carrying the segment table, so it is a fair stand-in for the filing when testing extraction | ⚠⚠ **It is not — it silently removes the evidence a PERIOD START is derived from.** Under `v3` the AMD slice returned 46 well-formed items and **every one had `period.start = None`**, so each segment's discrete and cumulative figures collapsed onto one `MP-18` identity — `Data Center 4,341` and `Data Center 11,255` both keyed `(seg.revenue, 'Data Center', (None, '2025-09-27'))`. ★★ The model was RIGHT not to invent the start: the slice contains only *"Three Months Ended"* headers, while the full filing also carries *"December 28, 2024"* and the equity statement's opening balance. `MU`'s slice happened to sit near Item 2 and the equity note, so filing 1 never exposed this | `tools/run_extraction_once.py` `--segment-note-only` | ⚠ material | ✅ **resolved 2026-09-08** | ★★★ **`MP-18` was RIGHT to refuse it** — those items genuinely are indistinguishable as returned, and a suite that accepted them would be recording the cumulative-vs-discrete trap as fact. ⚠ The flag is now documented as **diagnostic only**: it may be used to compare prompts or measure cost, and **never** to produce a recording a golden case grades. ★ A cheap bundle that changes the ANSWER is not a cheap bundle |
| **DX-33** | 2026-09-09 | E-02 | The tool schema states the output contract for extraction, and `E-01`'s wording — *"the figure … WITHOUT a currency symbol: '5,069', not '\$5,069'"* — is the general rule | ⚠⚠ **It was written for ONE block and is applied to ALL of them.** `E-02` guides in PHRASES, not table cells: the filing says *"to be approximately \$14 billion"* and the model returned *"approximately 14 billion"* — obeying the schema and thereby **breaking the prompt's verbatim rule**, so `X-01` refused it. ★★★ The two instructions are **directly contradictory** for a quoted phrase: *strip the currency* vs *appear VERBATIM inside the quote*. For `'\$5,069'` in a table cell both can hold; for *"approximately \$14 billion"* only one can. ⚠ 2 of 44 items lost this way | `tools/anthropic_transport.py::extraction_tool` | ⚠ material | ✅ **resolved 2026-09-09** | ★ Proposed: scope the currency rule to a BARE FIGURE and let verbatim win otherwise — *if the value is a phrase quoted from the document, copy it exactly, symbol included*. ✅ **Applied**: the schema now scopes the currency rule to a BARE FIGURE and states which rule wins — *"If the value is a PHRASE quoted from the document, copy it EXACTLY, symbol included… Verbatim always wins."* ⚠ Unverified against a live call; the failing example is pinned as a test. ★★ **Only a second BLOCK could expose this** — two filings of `E-01` never could |
| **DX-34** | 2026-09-09 | E-02 | `X-01` ② requires every value to appear verbatim in its own quote — the guard the whole `extraction` kind rests on | ⚠⚠ **`E-02` defines an item that is not quotable at all.** `gd.direction` is a CLASSIFICATION from a closed set — *raised | lowered | reaffirmed | initiated | withdrawn* — that the model **chooses**, not text it copies. Measured: `gd.direction` = `'reaffirmed'`, and the word does not appear in its cited span, or anywhere near it. `X-01` refused it, **correctly by its own rule**. ★★★ So the contract has an item that is structurally unverifiable: `RA-5` splits extraction (*what does this document say* — ground truth exists) from judgement (*is this good* — none exists), and `gd.direction` sits on the wrong side of that line while declared as extraction | `E-02` `gd.direction` · `claims/verify.py` | ⚠ material | ✅ **resolved 2026-09-09 by Victor — option (a)** | ★★ Three ways out, and it is the fund manager's call: **(a)** `gd.direction` is derived by `D-02` arithmetic from `gd.value` vs `gd.prior_value` — ★ `AP-5`, a computation not a judgement, and `MP-6` already says no prompt computes; **(b)** it stays a model output but is exempted from `X-01` ② and marked as an inference; **(c)** it is dropped from `E-02`. ⚠ (b) puts a hole in the hallucination guard and should be resisted. ✅ **Victor chose (a).** `E-02 v2` drops `gd.direction`; direction is derived by `D-02` from `gd.value` vs `gd.prior_value` with an arithmetic trail. ★★★ Better supported than first argued: **`MP-6` already forbade it** — *"No prompt in this file computes anything"* — and comparing two figures is a computation. The defect was latent only because nothing had ever run `E-02`. ⚠ `withdrawn` is the one state arithmetic cannot derive, so `v2` keeps it reportable through `gd.language_note` in the company's own words |
| **DX-35** | 2026-09-09 | E-02 live | The filing fixture is the document a citation is checked against, so what the converter keeps is part of the contract (`C13`) | ⚠⚠ **A PAGE BREAK sits mid-sentence and the page furniture is still in the text.** MU reads *"…term sheet with the State of"* / `35 | 2025 Q3 10-Q` / `Table of Contents` / *"New York…"*. The model quoted the sentence **the way a human reads it** — correctly — and `X-01` refused it because that string is not in the document. ★★★ Because `X-01` ABORTS, four dead items took the other **47 with them**: a $0.6377 call parsed to nothing. ⚠ This is the **6th** failure traced to `convert_filing.py`, and the first that a second BLOCK was needed to expose — `E-01` reads tables, which never straddle a page | `tools/convert_filing.py` · `run_extraction_once.py::parse_items` | ⚠ material | ✅ **converter fixed 2026-09-09; fixtures NOT yet re-rendered — needs Victor** | ★ Page numbers are an artefact of PAGINATION, which the text rendering already discarded; keeping them keeps half a layout — `_merge_symbols`' argument about `$` cells, again. ✅ `strip_page_furniture()` deletes a line that is ENTIRELY furniture, anchored at both ends, and never edits a line carrying prose. ★★★ **Measured, and this is the number that matters:** 1,634 chars leave MU and 1,116 leave AMD, the 4 unlocatable items go to **0**, `X-01` ① is clean on all 51 — and **0 of the 95 already-recorded `E-01` quotes stop resolving.** The re-render `L7` §5 warns about is **free**; it needs no re-recording, only Victor's hand on the two fixture files |
| **DX-36** | 2026-09-09 | B5 | `tools/promote_recording.py` states the request payload is *"replaced by its `bundle_hash`"* and that on a re-render the recording *"disagrees **loudly**"* — the guard that makes re-rendering safe | ⛔⛔ **No hash is written and nothing compares one.** It writes `{"__elided__": …, "chars": …}`; `grep bundle_hash tests/ tools/` returns the docstring and nothing else. **The drift detector existed only in the paragraph describing it** | `tools/promote_recording.py` | ⛔ high | ✅ **resolved 2026-09-09** | ★★ `DX-12`'s shape one level up: not a check that skips, but a check **never written**, described in prose as though it had been — and prose is what I read when deciding whether `DX-35` was safe. ★★★ A hash would also be the WRONG guard: it fires on ANY byte change, so `DX-35` would have demanded ~$1.20 of re-recording to buy nothing. The question is not whether the bytes moved but whether the recording still **MEANS** what it meant. ✅ `test_every_recorded_quote_still_resolves_in_its_filing` asks exactly that, over every recording × every quote, and the false docstring is corrected |
| **DX-37** | 2026-09-09 | E-02 live | `AP-5`/`RA-131` — the offset is the one part of a citation the model cannot author, so `parse_items` computes it: `start, end = _locate(...)` | ⚠⚠ **`_locate`'s `end` is DISCARDED.** The next line writes `offset=(start, start + len(quote))`. ★★ The two agree **only when the match was exact** — but `_locate` also matches under whitespace/typography normalisation, and there the document's span is a **different length** from the quote, so the span is cut short and `X-01` ① rejects a citation that is perfectly good, **blaming the model for our arithmetic**. Measured: document holds `'State of\n\n\nNew York'`, quote holds `'State of\nNew York'`, span ends 2 chars early on `'…provides fo'` | `tools/run_extraction_once.py::parse_items` | ⚠ material | ✅ **resolved 2026-09-09** | ★★★ **Found only because `DX-35`'s fix was verified with the REAL `x01_verify_extraction` instead of a hand-rolled whitespace comparison.** My simulation collapsed whitespace and passed; the real check resolves the SPAN first, and the span was wrong. ⚠ A simulation of a guard tests the simulation. ★ **Latent, not new** — 0 of MU's 60 and 0 of AMD's 41 recorded spans change, because only normalisation-matched quotes can differ in length, and `DX-35`'s strip is what creates the `\n\n\n` runs that expose it. ✅ Use `end`; pinned by `test_dx37_the_span_end_comes_from_the_locator_not_the_quote_length` |
| **DX-38** | 2026-09-09 | B5 | `D2`/`AC-5.1` — the fund manager establishes every golden value, and `established_by` *"names a person, never a pipeline component"*. `DX-28` had already closed the identical hole on `established_at`: *"a placeholder that validates is a placeholder that ships"* | ⛔⛔ **The same hole was left open on `established_by`, ONE LINE ABOVE the fix.** The check is `if not self.established_by.strip()`, which passes ANY non-empty text — so the template's own blank, `'____'`, validated. ⚠ **Measured on live data:** Victor signed 5 of 8 prepared `E-02` cases and left 3 at `'____'` with a real `established_at`; all three constructed cleanly and would have graded as established. ★★★ **Two of the three were cases 21 and 23 — the cases pinning `DX-33` and `DX-35`, this session's own fixes** | `src/evaluation/golden/models.py::GoldenCase` | ⛔ high | ✅ **resolved 2026-09-09** | ★★ `D2`'s circularity check could never have caught it: a placeholder names **neither a person nor a pipeline component**. It is not circular, it is **UNATTRIBUTED** — a second, independent route for an unestablished value to grade as gold, and `DX-20`'s family for the third time. ✅ `_is_placeholder()`: refuses a value with **no letters at all** (`____`, `---`, `???`) plus an exact-match word list (`TBD`, `pending`, `N/A`). ⚠⚠ Deliberately **no** *"does this look like a real name?"* step — `'张伟'`, `'O'Brien'`, `'M K'`, `'Ana'` all pass; a blank-detector that rejects real people makes signing feel arbitrary and gets worked around. ★ The check tests for the ABSENCE OF LETTERS, never for a name-like shape (`P5`: fail loud, not fail clever) |
| **DX-39** | 2026-09-09 | B5 | `D2` — `established_by` may not name a pipeline component, and `GoldenCase` enforced it by substring-scanning `established_by` **and `source`** against `FORBIDDEN_ESTABLISHERS` (`pipeline`, `system`, `model`, `llm`, `claude`, `gpt`, `agent`, `src.`, `auto`, `generated`, `gateway`) | ⚠⚠ **`source` describes FILINGS, and ordinary filing prose is full of those words.** Measured — 5 of 6 realistic sources REFUSED: *"Automotive segment revenue table"* (`auto`), *"cash generated from operations"* (`generated`), *"the company's business model"* (`model`), *"confirmed with the transfer agent"* (`agent`), *"the company's ERP system"* (`system`). ★ Found LIVE, not by inspection: case 22 would not construct, because my own template `source` said *"the model's own note adds…"* | `src/evaluation/golden/models.py::__post_init__` | ⚠ material | ✅ **resolved 2026-09-09 — Victor approved the recommendation** | ★★★ **The damage was never the refusal, it was the WORKAROUND.** The message names a word, so the natural response is to write vaguer `source` text — and `CT-5.2` requires `source` to be specific enough to re-check, or the value *"will eventually be trusted for the wrong reason"*. ⚠ **A guard that punishes specific prose trains people to write vague prose, degrading the exact field it protects.** **Options weighed:** ⓐ *scan `established_by` only* — ⚠ rejected, a `source` reading *"taken from pipeline output"* would then pass, and that is genuinely circular; ⓑ *word-boundary matching* — ⚠ rejected, it fixes `auto`→*"Automotive"* but NOT `generated`/`model`/`system`/`agent`, which appear as WHOLE WORDS in real filings; ⓒ *drop the ambiguous words from the list* — ⚠ rejected, it weakens the `established_by` check where those words are unambiguous; ⓓ ✅ **CHOSEN — split the check by what the field IS.** `established_by` is a NAME, so a bare substring is right for it (nothing naming a person contains *"pipeline"*); `source` is PROSE, so it is scanned for **provenance phrases** instead — `generated by`, `pipeline output`, `the model said`, `auto-generated`, `run output`, plus vendor names. ★★ The distinction that makes it safe: *"cash generated from operations"* names a LINE ITEM; *"generated by"* names a PRODUCER — and `D2`'s concern is **who produced the value**, so the check now asks about provenance rather than vocabulary. ⚠⚠ Every phrase is multi-word or an unambiguous vendor name; **a single-word addition to that list should be assumed wrong**, because that is exactly how `DX-39` happened. ✅ 15 tests: 6 filing-prose sources that must pass, 9 provenance sources that must still fail, and `D2`'s original 5 forbidden establishers unchanged |
| **DX-40** | 2026-09-09 | F6a | `F6a` `AC-6a.8` — every routing selection is recorded as a `CT-2.3` `DecisionRecord`. Two specs say where that record comes from | ⚠⚠ **They disagree.** `F2` §4: *"a decision record is **written by the routing function itself**, carrying the reason it already returns."* `F6a` §2 non-goals: *"✗ **Recording.** F6a returns the reason; F2 persists it."* ★ Read literally, one requires `routing.py` to write to a store and the other forbids it | `F2` §4 · `F6a` §2 · `policy/routing.py` · `trace/wire.py` | ⚠ material | ✅ **resolved 2026-09-09 — in `F6a`'s favour** | ★★★ **`AC-6a.2` breaks the tie**: `select()` must perform *no I/O, read no clock, consume no randomness*, and a module that writes files **cannot be proven pure by structure** — `test_ac_6a_2_select_performs_no_io` would have to start mocking a store. ★ The specs' shared intent is that the record **originates from the routing choice** rather than from a separate observer that can drift out of step; that is satisfied by passing the `Routing` to F2, and nothing in `F2` §4 actually requires the import to point the other way. ✅ `trace/wire.py::record_routing(store, routing, …)`, beside `traced()` and `traced_transport()` — the seams that already do exactly this job. ⚠ `decision_id` is **required and referenced, never minted** (`CT-2.7`): minting one per routing choice would fan `F7b`'s outcome join out across every selection in a run |
| **DX-41** | 2026-09-09 | F6a | `AC-6a.6` — `src/fundamental/**` and `src/quant/**` may not import each other (`ST-9`, `INV-014`). `F6a` §4 calls it *structural*, and `tools/check_import_fences.py` exists, is named for it, and is wired into `check_all.py` | ⛔⛔ **It checks a DIFFERENT fence.** `firewall_violations()` walks `src/explain/` and asks whether **seat 6** reached into a walled domain — that is `AC-4.2`. ★★ The fence `AC-6a.6` names — the two analysts importing **each other** — had **no code at all**, and the spec's traceability row said `tools/check_import_fences.py` as though it did | `tools/check_import_fences.py` | ⛔ high | ✅ **resolved 2026-09-09** | ★★★ **A tool with the right name, in the right place, wired into CI, reads exactly like coverage** — and this one was three-quarters of an alibi. ⚠ The traceability row pointed at it, which is how the gap survived a spec review. ★ The harm is specific and silent: a direct import is a channel through which one seat can condition the other **with no `influenced_by` recorded anywhere**, so `PG-7` is defeated without leaving a trace — strictly worse than being defeated loudly. ✅ `peer_to_peer_violations()` added, wired into `all_violations()` and `main()`, 5 tests incl. both directions and the ALLOWED cases (orchestrator types, intra-domain). ⚠ Deliberately stricter than the seat-6 fence: `_is_published` does **not** apply, because the two analysts are meant to be independent of each other, not merely of each other's internals. ★ The live tree passes — the fence was being honoured, just not enforced |
| **DX-42** | 2026-09-09 | F9 | `AC-F9.2` — `src/fundamental/source/**` contains no prompt composition, claim verification or confidence logic of its own; it calls `relay/`. F9's traceability row names `tools/check_no_reimplementation.py` | ⛔⛔ **The file did not exist.** F9's *first* non-goal — *"✗ Re-implementing prompt composition, ingest, verification or de-rating"* — was enforced by nothing, and the spec table named a tool that was never written | `tools/check_no_reimplementation.py` | ⛔ high | ✅ **resolved 2026-09-09** | ★★ **`DX-41`'s shape one spec later: a traceability row naming a plausible tool reads exactly like coverage.** Two consecutive specs, same failure — ⚠ a row is a CLAIM, and nothing in this repo checked that the module it names exists. ✅ Built and wired into `check_all.py` as the **8th** guarantee, 6 tests. ★ Deliberately about **definitions, not names**: an adapter *taking* `assess_confidence` as an injected dependency is how `C3` is satisfied, so only a `def` or a threshold assignment counts as ownership — a check that banned the name would ban the injection. ★★★ It also catches a copied `CONFIDENCE_FLOOR` **constant**, which is how a duplicated floor actually arrives: one plausible line, not a function anyone notices in review. `AC-1.77` says the relay's whole safety case rests on that floor firing unchanged, so a local copy fires **instead of** the real one |
| **DX-43** | 2026-09-09 | F9 | `AC-F9.6` — a card whose thesis came from the relay says so. `RP-48`/`AC-1.79` added a FOURTH reliability class, `RELAYED_JUDGEMENT`, on 2026-08-25: glyph `◌⇄`, label *"RELAYED JUDGEMENT (unverified transport)"* | ⚠⚠ **The class existed, fully specified, and `build_card()` never assigned it.** Every thesis rendered as an ordinary `JUDGEMENT` whatever its transport, and no card field named its source at all | `src/reporting/render/card.py` | ⚠ material | ✅ **resolved 2026-09-09** | ★★ `RP-48` is explicit that `RELAYED_JUDGEMENT` is **more provisional than `JUDGEMENT`, never a footnote on it** — a relay report is *"a judgement whose bundle does not exist and whose numbers are mostly unverifiable against data we hold"*. Rendering it as an ordinary judgement tells the reader the two are **equally checkable**, which is what `AP-2`/`DC-1` exist to prevent. ✅ `thesis_source` renders on BOTH paths — ⚠ a field appearing only on the relay path teaches readers that its absence means *fine*, so a missing provenance and an API thesis would look identical. ★★★ An unprovenanced thesis renders `"unknown"` at the **weakest** class, never defaulting to `api`: the tempting default is the common case (`QR-20`), and it would render the least-known thesis as the **most** trustworthy source available. A defaulting rule must fail toward the weaker claim (`P5`). ★ Position is load-bearing too — `thesis_source` sits immediately after `analyst_verdict`, because how far to trust the transport is unreadable once separated from the judgement it qualifies |
| **DX-44** | 2026-09-09 · ✏ **2026-09-10** | F1 · F9 · D-01 · D-09 | Constitution §1 reserves ID families and warns *"two live meanings for one ID"* is a real defect — `AP-n` out of `P1`–`P6`, `M<n>`→`MS-n` across 118 references | ⚠⚠ **`AC-9.6` had TWO live meanings, both about the discipline card** (F9: *the card states its source*; D-09: *every card field names a producing domain*). ⛔ Measuring it showed **seven** numeric prefixes collide, **801 upstream citations against 148 own ACs** — `AC-1` **362** · `AC-8` 120 · `AC-2` 80 · `AC-9` 71 · `AC-5` 67 · `AC-3` 60 · `AC-4` 41 | `sdd/specs/*/spec.md` · `constitution.md` §1 | ⛔ high | ◐ **`F9` + `F1` RENAMED (Victor, 2026-09-09/10); ⬜ five prefixes left DELIBERATELY** | ★★★ **It bit within minutes** — the first `AC-9.6` implementation set `source="F9"`, which **D-09's** `AC-9.6` fails (*a field D-09 could compute itself is one it must not*). Two rules, one id, one artifact, **opposite requirements**. ✅ `F9` → `AC-F9.<k>` (14 files) and `F1` → `AC-F1.<k>` (22 files), D-01/D-09 references untouched and **explicitly qualified** where the two sit side by side. ★ The `F9` rename made `test_sdd_process.py`'s AC regex fire — the same guard whose comment records `DX-10`, where it failed **silently**. ★★★ **The stopping criterion is OVERLAP, not volume.** `F1` and `F9` are the two whose own numbering sits **inside** a live upstream domain's (D-01 `.1`–`.99`, D-09 `.1`–`.34`), so a bare id is ambiguous **and both meanings are in daily use**. The other five are cited upstream mostly in `sdd/design/rel6_*` and `tests_src/` — **inherited territory this repo does not edit** (vision §2) — so the vocabularies rarely meet in one file. ⚠⚠ **A worked example of why this cannot be automated:** `src/models/governance/parity.py` reads *"(F1 AC-1.15, INV-6)"* about a feature-coverage floor — **neither** this repo's `F1` **nor** its `AC-1.15` (`InvalidKey` on a malformed name). ★ A global substitution would have corrupted it; it was classified by hand and **left untouched**. Every occurrence in both renames was checked individually, and 8 of ~30 cross-references turned out to be upstream's |
| **DX-45** | 2026-09-09 | F7a | Constitution §6 — *"Every test docstring names the `AC-<n>.<k>` it satisfies. Every spec keeps its traceability table current. **An AC with no row is not done, however green the test is** — because nobody can find it later."* | ⛔⛔ **`F7a` had 22 passing tests and ZERO AC references.** Every docstring cited a DECISION (`D1`, `D3`, `D5`) instead. `grep 'def test_ac_7a_'` returned **nothing**, and the spec's traceability table said *(to be written)* on every row | `tests/unit/test_deliberation.py` · `F7a` §9 | ⛔ high | ✅ **resolved 2026-09-09** | ★★★ **The tests were good and the coverage was invisible.** A decision-named test proves the decision was honoured; it cannot tell you which acceptance criterion is unmet — so the spec read *0 of 12 done* while ~9 were. ⚠ That is worse than an honest gap: it makes the remaining work unfindable and invites re-implementing what exists. ★★ Mapping the 22 onto the ACs is exactly what exposed the **three with no code at all** (`AC-7a.5`, `.6`, `.10`) and the two only half-implemented (`.1`, `.4`). ✅ 8 docstrings annotated, 12 rows filled, 3 gaps closed |
| **DX-46** | 2026-09-09 | F7a | `CT-7a.2` defines a `KillRule` as a **pre-registered analysis plan**: `null_hypothesis`, `statistic`, `alpha`, `power`, `detectable_ratio`, `min_n_per_arm`, `bands`, `registered_at`, `registered_by`. `AC-7a.4` is emphatic — ⚠ *"a rule naming ONLY A BARE THRESHOLD is rejected"* | ⛔⛔ **`KillRule` WAS a bare threshold**: two band edges, an expected rate and a date. It could not state its own null hypothesis, statistic, `detectable_ratio` or `min_n_per_arm`, and carried no registrant. ★ `assert_pre_registered` checked the TIMESTAMP and nothing else, so the *plan* half of pre-registration existed only in the spec's prose | `src/evaluation/studies/killrule.py` | ⛔ high | ✅ **resolved 2026-09-09** | ★★★ **The half that was missing is the half that gets chosen after the data.** `PG-5.1`: pre-registration fixes the **analysis**, not a constant — a rule that states only where the bands sit leaves the null, the statistic and the required `n` to be settled once the numbers are visible, which is the rationalisation the whole mechanism exists to prevent. ✅ Completeness is checked at **CONSTRUCTION** (`IncompletePlan`), not at use: a partly-stated plan must not be *buildable*. ⚠ Two existing rules in the suite were incomplete and had to be given a registrant — the check caught them immediately. ★ `min_n_per_arm` and `detectable_ratio` are **derived properties**, never fields, so `D1`'s power calculation cannot be overridden by hand |
| **DX-47** | 2026-09-09 | F7a | `AC-7a.1` / `PG-5.1` — ★★ *"this spec is a GATE: `F6b` may not graduate until this design exists."* The traceability row named `tools/check_gate_ordering.py` | ⛔ **The file did not exist** — the THIRD consecutive spec whose traceability row named a tool that was never written (`DX-41` wrong tool, `DX-42` no tool, `DX-47` no tool). ⚠ The gate lived entirely in a spec header | `tools/check_gate_ordering.py` | ⚠ material | ✅ **resolved 2026-09-09** | ★★★ **A gate in a header is enforced by whoever remembers it at the moment they are most motivated to forget.** `PG-5.1` names `F6b` the capability *most at risk of being theatre*, and the natural sequence — build the interesting thing, measure it later — is exactly what the gate exists to interrupt. ✅ Wired as the **9th** `check_all.py` guarantee; verifies `T1`–`T7` are defined, the plan is CONSTRUCTIBLE (not merely described), and `F6b`'s spec references `F7a`. ★★ It also asserts `D1`'s cost asymmetry stays ≥3×, because *"do not quietly widen the DELETE band to make it cheaper"* is `PG-5.1`'s rationalisation arriving one step earlier — a threshold chosen after seeing the **cost** rather than the data |
| **DX-48** | 2026-09-09 | F6b | `AC-6b.6` / `P3` — *"a revision may make a verdict equal or more conservative, **never more aggressive**"*. `F6b` §4 states it as a behaviour the module holds | ⛔⛔ **`deliberate()` never checked.** An agent could revise `SELL`→`BUY` and the function returned it without comment | `src/orchestration/graph/deliberation.py` | ⛔ **high — a safety rule** | ✅ **resolved 2026-09-09** | ★★★ **The ORDERING is what makes this severe, and it is not obvious.** `D4` puts deliberation **before** D-12 composes — so an escalated verdict arrives at the composer looking like *the seat's own honest output*, and `PG-6` makes D-12 a deterministic meet over whatever it is handed. ⚠ Nothing downstream catches it: `RP-7`/`DC-5` compare the COMPOSED verdict to the NOMINATED one, and after an escalation here **both already carry it**. The only place this is visible is the place that was not looking. ✅ `assert_not_escalated()` runs on what the agent PROPOSED, *before* the mode decides whether to apply it — otherwise an escalation could lie dormant in `ADVISORY_ONLY` and arrive the day the band is promoted to `ACTIVE`. ⚠ It ranks only values it can rank: `pre`/`post` are often dicts (size, conviction), and `x in dict` **raises on an unhashable value** — a guard against escalation that crashes on a legitimate revision is worse than none, and a test caught exactly that |
| **DX-49** | 2026-09-09 | F6b | §2.1's band table maps every `F7a` T1 verdict onto what `F6b` is permitted to do — `KEEP` may alter conviction and size, `ADVISORY_ONLY` renders the transcript with the verdict unaffected, `DELETE` removes the capability, `INSUFFICIENT` ⇒ advisory | ⚠⚠ **`Deliberation` had no `mode` field**, so the whole table bound to nothing. There was no way to express *"run, render, and change nothing"* — the state `F7a`'s middle band exists to produce | `src/orchestration/graph/deliberation.py` | ⚠ material | ✅ **resolved 2026-09-09** | ★★★ **The default is the finding.** §2.1's `INSUFFICIENT` row says *absence of evidence defaults to the SAFE branch, not the convenient one* — and `F7a` has never run, so **nothing has yet earned `ACTIVE`**. ✅ `DEFAULT_MODE = ADVISORY_ONLY`; a mutation setting it to `ACTIVE` is caught. ⚠ A default of `ACTIVE` would let an unmeasured capability alter verdicts from its first day, which is precisely what `PG-5.1` gates against — and it would have looked like a reasonable default to anyone not reading §2.1. ★★ The advisory path still records `advisory_post` (what it WOULD have done), because an advisory capability that discarded its own proposal would make the Tier-B study impossible for exactly the period the capability is unproven — when the evidence is most needed |
| **DX-50** | 2026-09-09 | F6b · F7a | `F7a` §4 opens *"**Every test runs on `CapabilityDelta` pairs**"* and `F6b` `AC-6b.8` requires the pre/post pair to be recorded *"including when they are equal"*. The two specs describe one pipe | ⛔⛔ **Neither end existed.** `run_tier_a()` took hand-made `Challenge` objects; `deliberate()` emitted **no delta at all** — its code comment said the caller would write one, and no caller did | `graph/deliberation.py` · `studies/deliberation_tier_a.py` | ⛔ high | ✅ **resolved 2026-09-09** | ★★★ **Each spec was complete on its own terms and jointly useless**: `F7a` an instrument with nothing to measure, `F6b` a capability that could not be measured. ⚠ Neither spec's traceability table could reveal it, because the gap was in **neither** — it was in the seam, and a per-spec table has no row for a seam. ★★ That is the sharpest argument yet for integration tests as a first-class tier: 12 + 12 green ACs across two specs, and the thing they exist to do had never once run. ✅ `capability_delta()` emits exactly the shape `challenges_from_deltas()` reads, and `tests/integration/test_f6b_f7a_end_to_end.py` demonstrates the instrument DISCRIMINATING — an evidence-weighing agent scores `ratio 0.000 → KEEP`, a capitulating one `ratio 1.000 → DELETE`. ⚠ Synthetic inputs; `PG-5.1` permits that for Tier A, and it proves the wiring carries information, **not** that deliberation helps |
| **DX-51** | 2026-09-09 | F8 | `AC-8.16` — *a directive's `raw_text` never reaches a prompt* — is typed **invariant / property (STRUCTURAL)**, and §2.1 states the harm: *"Injecting it into an analysis prompt would reintroduce exactly the unfalsifiable, untestable control `QR-17`'s analysis rejected"* | ⚠⚠ **It was enforced by a unit test on ONE OBJECT.** `Directive.to_prompt_payload()` omits `raw_text` and a test asserted that — ⛔ but nothing stopped a **different module** reading `.raw_text` and building a prompt of its own. A structural guarantee tested at one call site is not structural | `tools/check_no_raw_directive_in_prompt.py` | ⛔ high | ✅ **resolved 2026-09-09** | ★★★ **The failure this guards is prompt injection with the FUND MANAGER as the vector.** A directive that reached a prompt would be an untyped instruction channel into the analysis, and `AC-8.15`'s confirm step would be approving **typed effects** while unreviewed prose travelled beside them — the manager would believe they had reviewed what was applied. ✅ Tree-wide AST check, **10th** CI guarantee, 5 tests. ★★ It catches `payload["raw_text"]` as well as `.raw_text`, because a trace record read back from JSON is a **dict** — the attribute-only version would have missed the path most likely to be taken. ★ `CT-8.4` REQUIRES the field for the audit trail and `CT-8.6` shows it back to the manager, so the owners are exempted rather than the field banned |
| **DX-52** | 2026-09-09 | F7b | `AC-7b.5` — *nothing gates on a Tier-B result* — *"**structurally**, not by convention"*. The traceability row named `tools/check_no_tier_b_gating.py` | ⛔ **The file did not exist** — the **FIFTH consecutive spec** whose traceability row named a tool that was never written (`DX-41`, `DX-42`, `DX-47`, `DX-51`, `DX-52`) | `tools/check_no_tier_b_gating.py` | ⛔ high | ✅ **resolved 2026-09-09** | ★★★ **This is the rule most likely to erode by GOOD INTENTIONS, and the spec's wording says so.** Once `F7b` has numbers they will be the most interesting in the system — *"did deliberation make us money?"* — and reaching for them at a promotion decision is the natural move. ⚠ But at ~250 decisions a year against a signal at **IC 0.0203 / t = 1.42**, a Tier-B result is a second-order measurement on an unestablished first-order one, and **more time does not fix it: noise grows with the sample**. ✅ **11th** CI guarantee, 5 tests. ★ `D4`'s escape hatch stays honest — a powered disagreement ESCALATES to the fund manager as a finding and is never applied |
| **DX-53** | 2026-09-09 | process | Constitution §6 — *"Every spec keeps its traceability table current … an AC with no row is not done."* Eleven specs, 148 rows | ⛔⛔ **The rule says a row must EXIST. Nothing said it had to be TRUE.** Across the six specs completed 2026-09-09, every one had a structural AC unenforced **behind a row that read as coverage**: `AC-6a.6` named a tool that existed and checked a **different fence**; `AC-F9.2`, `AC-7a.1`, `AC-8.16`, `AC-7b.5`, `AC-3.10` named tools that **did not exist** | `tools/check_traceability_rows.py` | ⛔ high | ✅ **resolved 2026-09-09 — Victor chose option ⓑ; 12th CI guarantee** | ★★★ **The rows are written by the same hand as the code, so they agree by construction** — constitution §5.1's illegal move (*"improvise, then write a test that agrees with the improvisation"*) displaced one level up, where nothing was looking. ⚠ Invisible per-spec; obvious across six. ★★ **Prototyped before proposing.** Over all 148 rows it found **one real defect** — `AC-3.2` naming `corporate_actions/corroborate.py`, a file that does not exist (the logic is `classify.py::corroboration_of`) — ⚠⚠ **and I had written that row myself an hour earlier, copying the path out of the stub table without checking it.** `DX-53` occurring inside the edit that documented `DX-53`. ✅ **Option ⓑ (basename-tolerant) shipped**, and its first run produced its own first false positive — a **glob**, `src/shared/ports/*.py`, read as a literal filename. ★ Exactly the over-strictness ⓐ would have institutionalised: all three prototype false positives were shorthand for files that DO exist, and ⓐ would have made ~30 honest rows illegal to buy nothing. ★★ It also resolves **test function names**, which is not hypothetical: `F9`'s `DX-44` rename turned every `test_ac_9_4_*` into `test_ac_f9_4_*` the same day, and a stale row would have gone on asserting coverage under a name that no longer exists. ⚠⚠ **STATED LIMIT, and it travels in the tool's own docstring:** it resolves that a named file and test EXIST — **not** that the test tests its AC. `AC-6a.6` named a real file that checked the wrong fence, and **this check would pass it**. That half stays human, as `check_id_families.py` says: *"the check asks only 'is it written down?'"* ✅ 13 tests, 5 mutations, all caught |
| **DX-54** | 2026-09-09 | F3 | `AC-3.10` / `ST-5` — *only the LLM gateway calls an LLM*; `src/data_engine/corporate_actions/**` reaches a model only through `src/shared/llm/`. ★ `ST-5` is one of the inherited rules the constitution restates **by ID** rather than re-wording | ⛔ **No check existed, and `AC-3.4` had no test either.** ⚠⚠ `F3`'s traceability table said *"(to be written)"* on **all twelve rows** while 10 of the 12 ACs had passing tests — so the two genuine gaps were hidden inside nine false ones | `tools/check_import_fences.py::sdk_fence_violations` | ⛔ high | ✅ **resolved 2026-09-09** | ★★★ **`ST-5` is what makes three separate guarantees UNAVOIDABLE rather than merely available.** `GW-20`'s budget cap, `F2` `CT-2.2`'s request/response recording and `AC-2.9`'s redaction **all live at the gateway** — so one direct SDK call bypasses all three at once, ⚠ and leaves **no gap to notice**, because the trace simply would not contain the call. ✅ Checked over ALL of `src/` with the gateway exempted, 5 tests. ★ Deliberately import-name matching, not substring: `tools/anthropic_transport.py` is OUR wrapper and its name contains a vendor's — a substring check would flag every wrapper written to keep the SDK confined, **punishing the fix**. ★★ `AC-3.4` is the sharpest AC in `F3`: a retired symbol whose closes match its successor's *silently becomes another company's price history*, and **nothing about it looks wrong** — same ticker, continuous series, every downstream computation running happily on a company that stopped existing |
| **DX-55** | 2026-09-10 | F7a first live run | `GW-23` — *a truncated response is a failure, not a short answer* — and `DX-30`: *every truncation returns a payload of near-zero value at full price*. Both were logged during `E-01`/`E-02` and the lesson was believed learned | ⛔⛔ **The `T1` runner shipped with `max_output=400` and the reply is ~500 tokens of JSON.** All five calibration calls returned **exactly 400 output tokens** — `max_tokens` reached — so every reply was truncated mid-object, every `json.loads` failed, and the fallback recorded `"BUY"` = **held**. ★★★ A full 46-call run would have reported a revision rate of **0/23 on BOTH arms**, `T1` ratio undefined, from data that says nothing — and it would have looked like a clean run | `tools/run_tier_a_live.py` | ⛔ high | ✅ **resolved 2026-09-10 before the real run** | ★★★ **The 5-call calibration slice is the entire reason this was caught**, and it was added only because the earlier cost estimate was uncertain — the guard that mattered was bought for an unrelated reason. ⚠⚠ **The fallback was the worse half of the defect.** Defaulting an unparseable reply to `BUY` silently manufactures *the one outcome indistinguishable from a genuine hold*; a raise would have stopped the run at call 1. ✅ Cap raised to 1,500 and an unparseable reply now **raises** (`P5`). ★ Proof at 1,500: the same challenge returned a clean 504-token JSON that **correctly revised to HOLD** — the right behaviour, entirely invisible at 400 |
| **DX-56** | 2026-09-10 | F7a first live run | `CT-7a.1` — `T5` measures *information content* over span-bound claims and `T7` measures *tokens and dollars per deliberation vs single-pass*. Both are among the seven tests `AC-7a.1` requires to exist | ⚠⚠ **Both reported ZERO from the first real run**, and neither is a model finding: `T7 tokens/deliberation = 0.000` and `T5 coverage = 0%`. ★ `capability_delta()` never populates `tokens` or `span_bound`, so `challenges_from_deltas` reads the field defaults and the two metrics measure the instrumentation rather than the run | `graph/deliberation.py::capability_delta` | ⚠ material | ✅ **resolved 2026-09-10** | ★★ **`T5` behaved correctly and `T7` did not**, and the difference is the lesson. `T5` returned `INSUFFICIENT (n=0)` with its reason and printed *"0% of challenges are span-bound (D4 — the rest are unmeasurable, not zero)"* — it **declined**, exactly as `D4` designed. ⛔ `T7` returned **`0.000` as a measured value with n=46**, which reads as *"deliberation is free"*. The real figure is **$0.0177 per deliberation**, known from the run's own billing. ⚠⚠ A metric that reports a confident zero from an unpopulated field is worse than one that refuses, and `AC-5.10` exists to prevent exactly this — `T7` bypasses it by never checking whether its input was ever set. ✅ **Fixed same day:** `capability_delta(…, tokens=, span_bound=)` carries both, and `_t7()` **refuses** when no token count was recorded — *"this is an unpopulated field, not a measurement of zero cost"*. ⚠ Verified against the 46 existing deltas: they now decline instead of reporting `0.000`. ★ 7 tests, incl. one that first failed on `AC-5.10`'s own `DEFAULT_MINIMUM_N=20` floor — correctly; **the floor and the blank-field guard are different refusals and both must hold** |
| **DX-57** | 2026-09-10 | F7a | `D1`'s power calculation gives `min_n_per_arm` — 22 for the `KEEP` boundary, **96 for `DELETE`** — and `AC-7a.11` refuses a verdict below it. ★ `D1` calls the DELETE run *"a **deliberate** spend, decided knowing what it buys"* | ⛔⛔ **The DELETE test cannot be reached by repeating this fixture, and the power calculation cannot see that.** The set holds **23 distinct pairs**; 96/arm means repeating each ~4.2x. ⚠ A power calculation assumes **INDEPENDENT** observations — repeats of one prompt sample the model's stochasticity, not the challenge space | `tests_src/fixtures/studies/deliberation_challenges.pending.yaml` · `killrule.py` | ⛔ high | ⬜ **OPEN — needs ~96 DISTINCT challenge situations, a fixture-authoring decision** | ★★★ **MEASURED before spending**, 6 challenges x 3 repeats, $0.3482: **6/6 answered IDENTICALLY**. Across the earlier 46-call run 1 of those 6 differed, so the model is highly but not perfectly reproducible. ⚠⚠ At the implied ICC the design effect is brutal — `n_eff = n / (1 + (m-1)·ICC)`: **ICC 0.85 → 26.0/arm, ICC 0.95 → 23.9/arm.** We already have 23. **192 calls and $3.40 would buy roughly THREE effective observations.** ★★ **This is the third time on this project that a cheap measurement stopped an expensive ambiguous one** (`DX-31`'s A/B, `DX-55`'s calibration slice, this). ⚠ The pattern worth naming: a power calculation states how much data a verdict needs and is **silent about whether the data can be independent** — so `min_n_per_arm` reads as a budget when it is really a **design constraint on the fixture**. ★ The fix is not more calls: it is ~96 distinct (thesis, challenge) situations. ⚠ Varying the THESIS alone does not work either — the 23 pairs' `true_value`s are computed against ONE synthetic book, so a new thesis invalidates every figure. **Each new situation needs its own book and its own 23 recomputed pairs.** ★ `D5`'s replay makes the analysis free forever after; it is the CALLS that are not |
| **DX-58** | 2026-09-10 | F7a | `D2` — a challenge is a **declared numeric trigger**: Risk raises it *because a metric crossed a threshold it owns*. `AC-6b.2` requires `payload.field` and `expected` to be present, and `is_material(value, threshold)` gates the exchange | ⛔⛔ **Nothing checked that the cited figure actually CROSSES its own threshold, and 8 of 46 did not.** 3 valid + 5 false challenges asserted *"X is past my T trigger"* while X was on the safe side of T — **self-contradictory on their face**. ⚠ I authored them and did not check; the generator for the 5-book set was worse, at **67 of 115** | `tests_src/fixtures/studies/deliberation_challenges.pending.yaml` · `tools/build_books.py` | ⛔ **high — it corrects a REPORTED result** | ✅ **detected 2026-09-10; the reported ratio is corrected below** | ★★★ **The correction sharpens the finding rather than softening it.** Reported: ratio **0.929** (valid 14/23, false 13/23). Corrected, excluding incoherent challenges: **ratio 1.032** — valid **14/20 = 0.700**, false **13/18 = 0.722**. ⚠ The agent revised *slightly more often on FALSE challenges than on true ones*, and the point estimate moves DEEPER into the `DELETE` band. (z = -0.15, p = 0.88 — still not significant at this n.) ★★★ **And the incoherent items are the most informative rows in the run: the agent held 8 of 8.** Perfect discrimination on self-contradictory challenges. ⇒ **The agent checks internal consistency reliably, and cannot distinguish a true figure from a plausible false one at all** — exactly what `F6b` §1's asymmetry predicts, since Research does not see the book. ⚠⚠ **The design consequence is severe and must be settled before more spend:** a false value that is *impossible* measures self-consistency checking (which is now demonstrated); a false value that is *plausible* is uncheckable without the book, so revising on it is CORRECT and the ratio goes to 1.0 by construction. ★ `T1` as specified may therefore have **no configuration that measures social-pressure resistance for a seat that cannot verify** — a finding about the SPEC, not the model |
| **DX-59** | 2026-09-10 | E1 · F8 | `CT-8.5` names each effect's `target` and `AC-8.17` requires effects to apply deterministically | ⚠ **The three thresholds `E1` would move are defined TWICE**, independently and by literal, in `src/risk/exposure/aggregate.py` (D-05 — what the report warns about) and `src/portfolio/sizing/risk_based.py` (D-06 — what the sizer will propose). Both carry *"L0 §8, one domain over"* — deliberate restatement | `risk/exposure/aggregate.py` · `portfolio/sizing/risk_based.py` | ◐ downgraded | ✅ **DISSOLVED 2026-09-10 — the precondition was removed, not the duplication** | ★★★ **The duplication is only a defect if a directive can move one copy and not the other.** Victor deferred the directives feature the same day, so no directive can — and the restatement returns to being exactly what it was before `E1`: two domains stating one policy constant, recorded, harmless **while it stays constant**. ⚠⚠ **This is the entry to re-read before a future release adopts `CT-8.5`.** The defect is latent, not gone: the moment one directive becomes movable, a lowered D-05 copy changes what you are WARNED about while the D-06 copy leaves what the system will PROPOSE at 25.0 — and `AC-8.17` would still PASS, because the applied values are deterministic. The behaviour would not be. ★ Recommended fix when that day comes: **both domains read one config entry.** `RA-48` already says these belong in config and should appear in the `RunManifest`, which also makes the effect's `target` a config key rather than a source line — the form `AC-8.13`'s replay needs anyway. ★★ Recorded as a **finding about restated constants generally**: a restatement is safe in proportion to how fixed the value is, so **making a constant configurable silently converts every copy of it into a defect** |
| **DX-60** | 2026-09-10 | E9 · QR-20 | `QR-20` chose the **Anthropic API as the default thesis source** over the relay, and `F9` `D3` says the cost figure must land as a `CT-5.1` `MetricResult` *"with its `n` and `inputs_ref`, not as a number in a document"* — because `QR-20` made that choice **partly on cost** | ⚠⚠ **The bill exists and does not answer the question.** All 13 traced calls are `extract:E-01`/`E-02` — **no thesis has ever been authored through EITHER adapter**, so cost-per-thesis has `n = 0`. ★ And the thing that WAS measured is itself under-powered: `cost_per_extraction_usd` has n=13 against `F5`'s floor of 20 | `.state/metrics/qr20_cost.json` · `sdd/questions.md` `QR-20` | ⚠ material | ⬜ **OPEN — `QR-20`'s cost premise is UNMEASURED** | ★★★ **`F5` refused to produce a number I would otherwise have quoted, twice.** `cost_per_thesis_usd` declines at n=0; `cost_per_extraction_usd` declines at n=13 < 20. That is `AC-5.10` and `D3` working exactly as designed — *"never a number computed on too little data"* — and it is the first time the harness has protected a **decision** rather than a metric. ⚠ **What this does NOT say:** that `QR-20` is wrong. The API may well be the right default on latency, control and one-shot determinism — those grounds are untouched. ★ What is unsupported is specifically the **cost** half of the argument. ⬜ To close it: author one thesis through each adapter and record the pair. ⚠ Until then the honest form of `QR-20` is *"the API is default on operational grounds; the cost comparison is unmeasured"* — and `PG-10`'s shape says the artifact should say so rather than imply a measurement happened |
| **DX-61** | 2026-09-10 | E8 · F9 `Q1` | `F9` `D1`: *"`ThesisSourcePort`'s contract requires an evidence span per factual claim"*, and `Q1` asks whether the relay ENVELOPE carries them across the transport — *"answerable by reading `relay/models.py` at `MS-6`"* | ⛔ **It does not.** `ClaimVerification` carries `ordinal`, `text`, `result`, `checked_against`, `ours`, `theirs` — **verification against OUR data, and no span into a source document.** `RelayEnvelope` carries transport metadata only | `src/fundamental/relay/models.py` | ⚠ material | ✅ **ANSWERED 2026-09-10 — `D1`'s stated consequence now applies** | ★★ **`D1` already accepted this outcome in advance**, which is why answering it changes a status rather than opening a defect: *"if the relay transport cannot carry spans for some answer, that answer is **degraded** and must say so — it does not silently arrive span-less."* ✅ The mechanism exists: `C1` requires a span **or** an explicit `unbound_declared`, and `_check_claims` raises `SpansMissing` otherwise — so a relay claim without a span **cannot arrive silently**. ★★★ **The real consequence is `QR-16`'s.** *"Earn the confidence back"* depends on spans existing — *"without them there is nothing to earn it with"*. ⇒ **On the relay path, confidence cannot be earned back today**, and that is a property of the transport, not of any model. ⚠ It also means `AC-F9.7`'s depth parity is **nominal on this axis**: both adapters produce the same FIELDS, but only the API path can populate the span that makes a claim checkable |
| **DX-62** | 2026-09-10 | F5 · golden `ranking` | `CT-5.2`: `input_ref` is `'<run_id>/<call_id>'` — *"the `F2` recording this case grades"* — and `AC-5.18` resolves it through `TraceStore.payload()`, which reads `trace/payloads/<call_id>.json`. `A3`/`DX-21` settled that it names a RECORDING because *"the recorded response is the only artefact that is both a product of the system and available offline"* | ⛔⛔ **That reasoning holds only for steps that MAKE AN EXTERNAL CALL.** `src/quant/` reaches no LLM — ranking is **fully deterministic**, emits no `CT-2.2` `ExternalCall`, and therefore writes **no payload for an `input_ref` to address**. ⇒ A `ranking` golden case could not be written at all, and `ranking.yaml` had sat empty since `A1` created it | `F5` `D6` · `golden/models.py::Kind` · `golden/store.py::KINDS` | ⚠ material | ✅ **resolved 2026-09-10 — Victor chose ⓒ: the kind is REMOVED** | ★★★ **The spec promised something its own contract could not express**, and the reason it hid for months is precise: every case written since `A3` graded an LLM step, so `input_ref`'s call-shaped assumption never met a deterministic one. ✅ `ranking` leaves `Kind`, `KINDS` and `CT-5.5`; **`ranking.yaml` DELETED rather than left empty** — an empty file reads as unfinished work, and this is a **closed question**, not a backlog item. ★ **Nothing is lost that existed:** ranking is deterministic and is guarded where deterministic code is guarded — unit and property tests over `src/quant/`. ⚠⚠ **What IS given up, recorded so it is not rediscovered as a surprise:** `Nomination` carries `model_artifact_id`, so a golden case *would* have guarded *"the same model on the same data still ranks NVDA #1"* across a retrain. **That regression target now has no home in `F5`.** ★ If a retrain ever needs it, the answer is `D6`'s rejected option ⓐ — extend `input_ref` to address a recorded ARTIFACT — **not** a new kind, and the extension must keep `DX-20`'s rule that a missing artifact RAISES rather than skips |
| **DX-63** | 2026-09-10 | F5 | `test_the_golden_set_is_not_silently_empty` exists precisely so an empty baseline cannot report green forever — *"`DX-12`'s lesson: a check that skips everywhere tells nobody"* | ⚠⚠ **It asks *"is there anything?"*, not *"is there anything per KIND?"* — so it passes on 28 `extraction` cases while `ranking` and `thesis` hold ZERO.** ★ `coverage()` has reported `{'extraction': 28, 'ranking': 0, 'thesis': 0}` all along; **no test ever called it** | `tests/integration/test_golden_regression.py` · `golden/store.py::coverage` | ⚠ material | ✅ **resolved 2026-09-10** | ★★★ **A guard written when the whole set was empty stopped fitting the moment ONE kind filled**, and nothing re-examined it. ⚠ `thesis` is the kind `D2` calls a **judgement**, on the most expensive output in the system — its emptiness is the largest measurement gap in the project, and CI said nothing. ✅ Fixed as a **declaration**, not a demand: `tests/unit/test_golden_coverage_is_declared.py` requires every empty kind to carry a recorded reason naming its blocking `DX`, and — ★★ the half that matters — **the declaration EXPIRES**: a second test fails the moment a declared-empty kind gains a case, so the entry cannot outlive its cause and become permanent cover. ★ `CN-10`'s rule applied to coverage: *an admitted gap is acceptable; silence is not* |
| **DX-64** | 2026-09-10 | F9 · thesis | `DX-60` and `DX-62` both end at *"author one thesis and the blockers clear"* — a `thesis` golden case needs a recording, and `QR-20`'s cost premise needs a priced pair. Estimating that run was supposed to be arithmetic | ⛔⛔ **No J-block is declared in `src/`.** `e_blocks.py` ships `BLOCKS = {'E-01', 'E-02'}`; `author.py`'s `STAGE_BLOCKS` names **`J-01`…`J-17`** and **not one of them has prompt text in `src/`**. ⇒ `author_once` cannot construct a judgement block, so **a thesis run is impossible today at any price** | `src/fundamental/prompts/e_blocks.py` · `thesis/author.py::STAGE_BLOCKS` | ⛔ high | ⬜ **OPEN — authoring work, not a spend** | ★★★ **This is `DX-23` exactly, one domain over.** That finding read: *"`E-01`'s prompt lived only in the design doc. Nothing in `src/` could construct it, so `run_extraction` had no block to run and no extraction could ever be recorded — which is why `F5`'s golden `input_ref` had nothing to point at."* ⚠ Every word of it is true of `J-01`…`J-17` today, and `e_blocks.py`'s own header says why it went unnoticed: *"a registry entry nothing calls is a claim, not a capability."* ★★ **The estimate, for when the blocks exist:** a thesis is **17 J-blocks x `K_RUNS`=3 = 51 LLM calls** (`RA-20`'s k>=3 stability probe), each carrying the bundle — **measured** at ~76,000 input tokens for a real 10-Q. ⇒ **$27 naive, $11 with prompt caching** (the bundle is one shared prefix across all 17 blocks); **$21-$54 for the PAIR `DX-60` needs.** ⚠⚠ **The cost is not the blocker and was never the interesting number.** 17 prompt blocks must be authored, versioned under `RA-13`, and hash-pinned — and `DX-31`/`E-01 v3` measured what that costs in iterations: **a prompt version must be proven against every filing the golden set grades**, and `v3` shipped, reverted and shipped again in one evening. ★ Declaring 17 at once would be 17 such risks taken simultaneously. ★ Cheaper path worth considering: declare **ONE** judgement block (`J-09`, the thesis statement) to produce a single recorded call — enough for a first `thesis` golden case at ~$0.40, though ⚠ it is **not a `CT-9.2` thesis** and could not price `QR-20` |
| **DX-65** | 2026-09-10 | J-01 run | `C12` added `cost_of` to `traced_transport` because the wrapper sees the transport, not the gateway, and *"after ~$7 of live runs the trace could not answer 'what did this cost?'"*. Its signature is `cost_of(model_id, TOKENS)` and it is handed the **normalised `{input, output}` dict** | ⛔ **My `J-01` runner passed `lambda _m, r: r.get('tokens_in') …`** — reading the RAW-response keys, which that dict does not carry. Every lookup returned 0, so the trace recorded **`cost_usd: 0.0` on a call that billed $0.3708** | `tools/run_judgement_once.py` | ⚠ material | ✅ **fixed 2026-09-10; ⚠ the recording keeps the wrong value** | ★★★ **`C12` returning through the very argument added to fix it**, one runner later. ⚠⚠ And the failure mode is worse than the original: `run_extraction_once::_cost_of` returns **`None`** when a rate is missing, with the comment *"⚠ absent, never 0"* — because **an absent cost reads as 'unknown' and a zero reads as 'FREE'**. Mine wrote the reading that lies. ⚠ **The promoted recording carries `cost_usd: 0.0` permanently** — `AC-2.8` is append-only and evidence is not rewritten to look better. ★ It is recoverable rather than lost: `tokens` recorded correctly (70,371 / 757), so the true cost is **recomputable from the record**. ★★ That is the difference between an incomplete record and a false one, and it is why `CT-2.2` stores tokens beside cost rather than cost alone |
| **DX-66** | 2026-09-10 | F5 replay | `RA-5` splits **extraction** (*what does this document say* — ground truth exists) from **judgement** (*is this good* — none does), and `F5` `CT-5.2`'s `kind` has carried both since `A1` | ⛔ **`tools/golden_replay.py` knew only one of them.** It parsed EVERY recording with `parse_items`, which expects a list of extraction items; the first `judge:J-01` recording failed with `'str' object has no attribute 'get'`. ⇒ The first `thesis` case **could not have been graded**, however correctly it was signed | `tools/golden_replay.py` | ⚠ material | ✅ **resolved 2026-09-10** | ★★★ **The spec had two kinds for months and the replay layer had one**, because every case ever written graded an LLM *extraction* step — the same blind spot that hid `DX-62` (ranking was unaddressable) and `DX-64` (no J-block declared). ⚠ Three findings, one cause: **`extraction` was the only path anyone had walked.** ✅ Dispatch on the kind the `call_id` already declares — `extract:E-01:llm:1` vs `judge:J-01:llm:1` — so it needs no new field and no guess. ★ `_as_judgement` returns ONE object and runs **no `X-01`**: a classification has no quoted span to verify against, and `F9` `D1` rejects *"two contracts wearing one name"*. What grades it is `D2`'s recorded judgement |
| **DX-67** | 2026-09-11 | prompts · ALL runs to date | `L1-fundamental-analysis-master-prompt` §3.0: *"Composed into **every E-block**: **S-1 · S-2 · S-3 · S-4 · S-5 · S-6**"*, and §4.0: *"Composed into **every J-block**: S-1…S-6, plus **S-7** in Stage A and **S-8** in fresh authoring."* Nine shared sections are declared (`S-1`…`S-9`) | ⛔⛔ **The composition was never implemented. Not once.** `grep` for `S-1`…`S-7` or `envelope` across `src/fundamental/prompts/` returns **zero**; `call.py:258` sends `"prompt": block.text` — the bare block. ⇒ **Every prompt this project has ever sent** — 13 extraction calls ($8.54) and the `J-01` judgement ($0.37) — went out **missing the shared envelope**, and all **29 golden cases** grade recordings made that way | `src/fundamental/prompts/call.py:258` · `e_blocks.py` · doc §3.0/§4.0 | ⛔ **high** | ⬜ **OPEN — found before running `J-02`; no further spend until decided** | ★★★ **What was actually missing matters more than the fact of it.** `S-3` is the **evidence and citation contract** — every sentence tagged `FACT` / `INFERENCE` / `ASSUMPTION`, *"an uncited factual claim is a defect, not a style choice. It fails the run."* `S-4` is the insufficient-evidence protocol; `S-7` is the **anti-anchoring notice, Stage A only**. ★★ **Extraction partly escaped by accident.** `X-01` enforces *value appears verbatim in its own quote* **in code**, and the tool schema declares the enum — so the extraction path got the EFFECT of `S-3` without its text. ⚠ Judgement had no such backstop: `J-01`'s recorded output carries **no FACT/INFERENCE/ASSUMPTION tags at all**, because nothing asked for them. ⚠⚠ **And `RA-13`'s drift guard passed throughout** — it pins each BLOCK's text to its design-doc section, which was always true. The envelope is a *different* claim in the *same* document and nothing checked it. ★ Third instance of that shape after `DX-41` (a tool checking a different fence) and `DX-63` (a coverage test asking a narrower question): **a guard keeps checking exactly what it was written to check while the thing beside it goes unchecked.** ⬜ Decision needed: ⓐ implement the envelope and **re-record** (~$9-10 to redo 14 calls, and every golden case must be re-verified against the new recordings); ⓑ implement it for **new** blocks only and mark the existing 29 cases as graded under a pre-envelope prompt; ⓒ amend the doc if the envelope is not actually wanted. ⚠ ⓑ leaves two prompt regimes in one golden set |
| **DX-68** | 2026-09-11 | MP-18 · E-01 re-record | `MP-18` makes an extracted item's identity `(evidence_id, qualifier, period)`, and `F5`'s selector embeds it: `#seg.revenue\|CNBU\|2025-02-28:2025-05-29`. It has worked since `DX-25` | ⛔⛔ **The first post-envelope run returned `period_start = None` on 65 of 65 items**, so every quarterly row collapsed onto its YTD twin — **20 duplicate identities**, and `ExtractionResult` refused the whole result. ⚠ 17 of the 28 extraction golden cases embed a `period_start` in their selector and would select nothing | `filings/models.py::identity` · `regression/replay.py::INPUT_REF_RE`, `_select` · `envelope.py::S2` | ⛔ high | ✅ **CLOSED 2026-09-11 — ⓐ adopted (Victor).** `identity` now ends `bool(self.is_cumulative_ytd)`; the `F5` selector gained a fourth component `[|ytd]` (`AC-5.18`, spec `A4`); **6 of 28** case selectors updated — not the 17 first estimated, because only the rows actually TAGGED cumulative were ambiguous. Re-measured: `parse_items` returns **65 items (20 `cumulative_ytd`)**, previously `ValueError`. 5 new tests, 3 of 4 mutations caught (the 4th was a no-op regex rewrite). **1948 passed**, all 12 CI guarantees green | ★★★ **The model is not misbehaving. It is obeying `S-2`.** Item 3: *"**Do not compute.** … If the quantity you want is not there, record a data gap — do not derive it yourself."* Item 4 forbids restating a figure the bundle gives in another form. ⚠ A segment table states the period **END** (*"Thirteen weeks ended May 29, 2025"*); the START must be derived — so under the envelope the model correctly declines to supply it. **Every earlier recording got a `period_start` only because nothing had told the model not to compute one.** ★★ **And the distinguishing fact IS recorded**: `cumulative_ytd` is set on 20 of 65 items and separates the quarterly row from the YTD one exactly. `MP-18`'s identity simply does not use it — so the identity was incomplete all along and a computed `period_start` was masking it. ⬜ Options: ⓐ **add `cumulative_ytd` to the `MP-18` identity** — ★ structural, uses a fact the model records rather than one it must derive; ⚠ 17 case selectors change; ⓑ tell `E-01` it may READ the start date from Item 2 — ★ `DX-24` established MU's filing **does** state it, so this is not computation; ⚠ it is filing-specific and AMD may not; ⓒ revert the envelope — ⛔ discards `S-3`, the reason for `DX-67`. ★ **ⓐ is recommended**: it removes a derived field from an identity, which is where `AP-5` says arithmetic does not belong → ✅ **adopted.** ⚠⚠ **Two consequences recorded so they are not rediscovered as surprises.** (1) **Absence of `|ytd` ASSERTS "discrete"** — it is deliberately not a don't-care, so a pre-`DX-68` ref to a cumulative row now **raises** instead of matching both. ★ Breaking loudly by case name is cheaper than an ambiguity that reports green. (2) **`period_start` is now absent from every post-envelope extraction**, by design — `S-2` forbids deriving it. The 22 discrete-row selectors still embed one, which the OLD recordings have and the NEW ones will not. ⚠ So **re-pointing the golden set at the re-recorded runs is a SECOND, separate edit** and must not be assumed done by this one; downstream consumers needing a start date derive it deterministically (`D-02`'s arithmetic, `AP-5`), never from the model |
| **DX-69** | 2026-09-11 | prompts · E-02 re-record | `MAX_TOKENS = {"extraction": 12000, "judgement": 16000}` (`call.py:94`) has been the output cap since the first live call, and `GW-23` makes a truncated response a **failure**, never a short answer. Four blocks had run under it without incident | ⛔ **The post-envelope `E-02` re-record hit `max_tokens` exactly and was refused** — `TruncatedError`, `$0.6810` spent for nothing. ⚠ The other three re-records passed | `src/fundamental/prompts/call.py:94::MAX_TOKENS` · `envelope.py` | ⚠ medium | ✅ **CLOSED 2026-09-11 — ⓐ adopted (Victor).** `MAX_TOKENS["extraction"]` 12,000 → 20,000; `E-02` retried: **38 items verified, $0.5929**. ⚠⚠ **But the retry produced 8,479 out — BELOW the cap that truncated it**, on a byte-identical prompt (76,195 in on both runs). ★★★ So the premise of the fix was wrong in an instructive way: `E-02` does not *need* >12,000, its requirement **straddles** 12,000. ⚠ n=1 per arm against a stochastic generator, and the trace does not record the thinking/response split, so the adaptive-thinking mechanism this constant's comment hypothesises is **not established** — recorded as an open observation, not a cause. ★ The cap therefore stands raised **against variance, not against a larger fixed requirement**, and the constant's own rule (*"raise only on a run that needed more AND completed"*) is **not met** by this change and says so in place | ★★★ **The headroom was never measured, and `E-02` had almost none.** Measured across all eight recordings: <br>`│ block │ pre-env out │ post-env out │ cap │ pre-env headroom │`<br>`│ MU E-01 │ 9,596 │ 10,235 │ 12,000 │ 20.0 % │`<br>`│ AMD E-01 │ 7,584 │ 6,209 │ 12,000 │ 36.8 % │`<br>`│ MU E-02 │ 10,509 │ 12,000 ⛔ │ 12,000 │ ⚠ 12.4 % │`<br>`│ MU J-01 │ 757 │ 4,000 │ 16,000 │ 95.3 % │`<br>★★ **The envelope is not a uniform inflator** — AMD `E-01`'s output **fell** 18 %. So *"the envelope made it longer"* is the wrong diagnosis: `E-02` was already running at **87.6 % of its cap** and any perturbation would have tipped it. ⚠⚠ **The single closest-to-the-cap call in the project's history was the one nobody had looked at**, and the cap is a shared constant, so the margin varies per block while the number does not. ★ Same family as `DX-55` (`max_output=400` truncated every reply) — and the same lesson landing twice: *a cap set once for the first block that needed one is unmeasured for every block after it.* ⬜ Options: ⓐ **raise `MAX_TOKENS["extraction"]` to 20,000 and retry `E-02`** — ★ `GW-23` still catches a real runaway, and the cost of an unused cap is **zero** (output is billed as produced, not as reserved); ⚠ ~$0.70 for the retry; ⓑ make the cap **per block** rather than per kind — ★ most precise; ⚠ a fifth place a block's identity is declared, and `DX-67` is the standing argument against those; ⓒ leave `E-02` graded against its pre-envelope recording — ⛔ that is `DX-67`'s rejected option ⓑ, two prompt regimes in one golden set. ★ **ⓐ is recommended**, with the headroom column above added to the run report so the next block near its cap is seen before it truncates |
| **DX-70** | 2026-09-11 | F5 · promote_recording | `promote_recording.py` writes `filing.json` so a recording can name its own filing — added precisely because *"AMD's cases were being checked against MU's text and every quote 'was not in the bundle'"*. `golden_replay` reads it to choose the text a quote resolves against | ⛔⛔ **It read `run_extraction_once.TICKER` — a MODULE DEFAULT (`"MU"`).** `--ticker AMD` sets it via `_select()` inside *that* process; the promoter runs in a fresh one where the assignment never happened. ⇒ **every promotion ever written said `MU`**, and promoting the new AMD `E-01` produced `filing.json → MU` | `tools/promote_recording.py::_ticker_of` · `run_extraction_once.py:65` | ⛔ high | ✅ **CLOSED 2026-09-11** — the ticker is now derived from the **recorded bundle** instead of a module global; 4 recordings re-promoted and verified | ★★★ **The defect is inside the fix for the same defect.** The comment above this line exists to record that AMD's quotes were once resolved against MU's filing; the field it added to prevent that recurrence was populated from a global that could not know the answer, so the failure it closed was reachable again **through the closure itself**. ★ It survived because it was *usually right*: MU is the default and most runs are MU, so the guess was correct on every recording but one. ⚠ That is the shape to distrust — **a guess that is usually correct produces no evidence of being a guess.** ★★ The fix takes the answer from evidence rather than convention: the recorded request still carries the whole bundle, so the filing is IN the recording. ⚠ First attempt used ONE 2,000-char probe and matched AMD but not MU — which looked like a filing quirk and was not: `DX-35`'s `strip_page_furniture()` means the bundle is **not a verbatim substring** of the fixture, so any window distinctive enough is wide enough to straddle a stripped line. ★ 40 short probes instead: measured **MU 19 / AMD 0**, **AMD 27 / MU 0**, **J-01 MU 40 / AMD 1** — and `P5` refuses a close call rather than breaking the tie by preference. ⚠ Fourth instance of `DX-41`/`DX-63`/`DX-67`'s shape: **a guard keeps checking exactly what it was written to check while the thing beside it goes unchecked** |
| **DX-71** | 2026-09-11 | F5 · golden set · envelope | `DX-67` re-recorded all four calls under the shared envelope, and the plan was to **re-point the golden set** at the new recordings — understood as a mechanical edit, since `expected` values were not changing | ⛔⛔ **Re-pointing is not mechanical, and doing it would have rebaselined TWO real regressions into gold.** Measured across 28 extraction cases against the new recordings: **only 11 pass as written**; **10 fail on a value the fund manager established**, and **5 more** point at readings the new run no longer produces | `tests_src/fixtures/golden/extraction.yaml` · `envelope.py::S2` · `e_blocks.py::E-02` | ⛔⛔ **high** | ◐ **PARTLY CLOSED 2026-09-11 — ⓑ adopted (Victor: "do your recommendation").** `E-01 v4` shipped and both filings re-recorded ($1.13). **8 of 14 `period.start` failures recovered** — every DISCRETE row, MU included. ⚠ The 6 YTD rows are NOT a `v4` failure and must not be treated as one — see `DX-73`. Golden set re-pointed: **20 live**, 8 parked. ⬜ `E-02`'s lost cluster remains open — see `DX-75` | ★★★ **The `period.start` failures are not addressing problems — they are graded failures, and `DX-68` masked that they existed.** `expected` itself carries `period: {start: "2025-02-28", …}`, established by Victor with a stated derivation: *"period.start from Item 2's repurchase table, which lists the quarter's fiscal months beginning February 28, 2025."* ⚠ So the start date **is in the filing** — reading it is extraction, not computation, and `S-2`'s *"do not compute"* should never have suppressed it. ★★ `DX-68`ⓐ was NECESSARY (an identity must not rest on a derived field) but is **NOT SUFFICIENT**: it made the result parse, and I read parsing as the problem being solved. It was not — 8 MU rows and 2 AMD YTD rows still fail to report a value the fund manager established. ★★★ **And the split is diagnostic**: AMD's DISCRETE rows still report `2025-06-29` correctly while every YTD row and every MU row returns `None`. So the envelope did not suppress the field — it suppressed it exactly where the model would have had to look somewhere ELSE in the document. ⇒ **`DX-68`'s rejected option ⓑ is the substantively correct fix**, and Victor's own `source` note is the evidence for it. ⚠⚠ **Second regression, independent**: post-envelope `E-02` returns **38 items vs 51 (−25 %)** and **13 qualifiers vs 17**, losing the entire government-funding cluster — `CHIPS Act direct funding grants` and `State of New York funding (non-binding term sheet)`, which 3 signed cases grade. ★ `E-01` did not degrade (MU 57→65, AMD 38→37), so this is an `E-02`-specific interaction, not a cost of the envelope as such. ★★★ **Why the re-point was HELD rather than done partially.** `D2`: *a regression must never become the new gold.* Re-pointing turns both findings green by construction — the 10 by requiring `expected` to be edited (which only the fund manager may do), the 5 by dropping cases whose readings vanished. ⚠ Re-pointing only the 11 that pass is worse than nothing: it splits the set across two prompt regimes, which is `DX-67`'s rejected option ⓑ. ★ **The golden set did exactly its job.** `AC-5.7`: *"a prompt change reds the suite and names the diverging cases."* It named them — and the instrument was only able to, because `D2` had kept the fund manager's values out of the system's reach |
| **DX-72** | 2026-09-11 | RA-13 drift guard | `test_prompt_text_matches_spec.py` pins `E-01`'s prompt text in code to its text in the design doc — *"a prompt that has drifted from its spec makes every baseline recorded against that version a statement about an unknown"* | ⚠ **It pinned `v2`, and `v2` had not been the shipped version since 2026-09-08.** `E01_CURRENT_VERSION = "v3"`, so the text actually reaching the vendor was unchecked by the guard written to check it | `tests/structural/test_prompt_text_matches_spec.py` | ⚠ medium | ✅ **CLOSED 2026-09-11** — the guard now discovers every declared `E01_*_TEXT` and asserts each against its own doc section; a new test pins that the version the REGISTRY ships is one the guard checks | ★ **It cost nothing this time** — `v3`'s text did match the doc — and that is the point worth recording: a guard can watch the wrong object for three days and leave no trace, because a guard that checks the wrong thing still reports green. ⚠ A hardcoded version list would have reproduced the defect at the next bump, so the versions are read from the module. ★★ Fifth instance of the shape after `DX-41`, `DX-63`, `DX-67`, `DX-70`: **a guard keeps checking exactly what it was written to check while the thing beside it goes unchecked** |
| **DX-73** | 2026-09-11 | F5 · 6 YTD golden cases | `DX-71`ⓑ shipped `E-01 v4` to restore `period.start`, and it worked for the discrete rows | ⚠⚠ **Every YEAR-TO-DATE row still returns `None`, and `v4` was never going to fix it.** 6 signed cases assert a start the filing does not state | `tests_src/fixtures/golden/extraction.pending.yaml` · `envelope.py::S2` | ⚠ medium | ✅ **CLOSED 2026-09-11 — ⓑ adopted; all 6 RE-ESTABLISHED by Victor Truong the same day** with `period.start: null`, every VALUE unchanged. Live set **26 extraction cases**, replaying green. ★ The cumulative-tag guard's declaration **expired on their return and was deleted with them** — the xfail is gone and the real mutation runs again | ★★★ **The case's own `source` is the evidence against it**: *"period.start derived from the Consolidated Statements of Changes in Equity, which open 'Balance as of August 29, 2024' — the prior fiscal year end — so the nine months begin the following day."* ⇒ **prior FY end PLUS ONE DAY**. Measured in the MU filing: `"August 29, 2024"` appears **twice**, `"August 30, 2024"` **zero times**. The value is not in the document. ★★ So the model is RIGHT to refuse, `S-2` is RIGHT to forbid it, and pushing the prompt harder would be training the model to do the arithmetic the envelope exists to stop. `AP-5`: **a computation belongs in deterministic code, never in a judgement call.** ★ The discrete/YTD split proves `v4` worked as designed: the discrete start IS written down (Item 2's repurchase table, exactly where the fund manager's source said) and came back; the YTD start is not, and did not. ⚠⚠ **What parking them costs, stated rather than hidden:** nothing live now asserts `cumulative_ytd`, so `test_ac_5_7_dropping_the_cumulative_tag_reds` has no subject — it **xfails against a written declaration** that expires the moment a YTD case returns, rather than raising a bare `StopIteration` that names nothing. ⬜ Options for Victor: ⓐ the YTD start becomes the SYSTEM's job, derived in code from the prior FY end (★ most faithful to `AP-5`; ⚠ needs the prior FY end extracted first); ⓑ re-establish the 6 with `start: null` (⚠ only the fund manager may edit an established value); ⓒ leave parked (⚠ loses the YTD column's regression cover) |
| **DX-74** | 2026-09-11 | MP-18 · qualifier | `MP-18` makes `qualifier` part of an item's identity, and `DX-25`'s selector embeds it. It has worked on every segment figure since | ⛔⛔ **Two AMD runs 82 minutes apart: the first gave each `seg.basis_note` a qualifier, the second gave all FOUR an empty one** — so 4 items collapsed onto one SELECTOR and `_select` refused. 2 signed cases became UNADDRESSABLE (their values are still present and still correct). ⚠ **Precisely**: `MP-18`'s identity is intact — `identity` appends the span for non-figures (`C14`), so the 4 notes ARE distinct and `parse_items` accepted all 37. It is the `F5` **selector** that cannot express a span, so it is weaker than the identity it claims to mirror | `regression/replay.py::INPUT_REF_RE`, `_select`, `_span_of` | ⛔ high | ✅ **CLOSED 2026-09-11 — ⓑ adopted (Victor).** The selector gained `@<start>:<end>`; both AMD cases are BACK in the live set. 5 tests. ⚠ Two bugs found building it, both of the *silently permissive* kind: `_span_of` read `span["start"]` when the WIRE shape is `{"offset": [s, e]}` (so the filter matched everything — indistinguishable from never being applied), and `end`'s character class swallowed the trailing `@0:60`. ★ Both caught on the first run of the four-notes test. ⚠⚠ **The underlying hazard STANDS**: `qualifier` is still model-authored | ★★★ **`qualifier` is FREE TEXT THE MODEL INVENTS, and `MP-18` rests an identity on it.** It has now been observed to REWORD between runs (`'restatement basis'` → `'Segment structure change / restatement'`) and to VANISH entirely. **An identity component the model re-authors each run is not an identity.** ★★ **Why it never bit before**: on a FIGURE the qualifier is a SEGMENT NAME copied from the table — externally fixed by the document. It bites on NARRATIVE items, where the qualifier is a LABEL the model composes. ⚠ Same root as `DX-68`: `MP-18` keeps resting identity on something the model PRODUCES rather than something the document FIXES — there a derived date, here an invented label. ⬜ Options: ⓐ require `qualifier` on narrative items in the prompt and refuse an empty one in `item()` (★ makes the guarantee structural; ⚠ another re-record); ⓑ **teach the SELECTOR the span**, which `identity` already carries — ★★ the smallest change and it closes the real gap: the module docstring claims *"the selector IS `MP-18`'s identity"* and that claim is currently FALSE for non-figures; ⓒ drop `qualifier` from the identity for narrative items |
| **DX-75** | 2026-09-11 | E-02 · coverage | `DX-71` measured post-envelope `E-02` at **38 items vs 51 (−25 %)**, missing the entire government-funding cluster that 3 signed cases grade | ⚠ Investigated free (no spend). **The cases are SOUND**: the filing states *"total CHIPS Act grants of **up to $6.4 billion**"* verbatim, in the same block as the $6.1 bn and $275 m components. The new run mentions `chips` **0** times, `6.4` **0** times, and recorded **no data gap** | `e_blocks.py::E02_V2_TEXT` · `envelope.py::S2` | ⚠ medium | ✅ **CLOSED 2026-09-11 — ⓐ adopted (Victor), $2.02.** ★★★ **THE ENVELOPE IS EXONERATED.** Three fresh `E-02` runs, byte-identical prompt: **63 · ~55 · 48 items** against the suspect run's **38** and the pre-envelope **51**. CHIPS mentions: **7 · 7 · 8** against **0**. ⇒ the 38 was a LOW DRAW, not a regression | ★★★ **The tempting diagnosis is wrong, and saying so is the finding.** The obvious story is that `S-2` item 4 (*"do not … restate a figure the bundle gives you in another form"*) suppressed the $6.4 bn total as an aggregate of figures already given. ⚠ **The evidence does not support it**: a model refusing under `S-2` is told to *record a data gap*, and this run recorded none — it did not decline, it simply produced less. ★★ **And `DX-74` supplies the alternative**: two AMD runs of the same prompt family differed in whether qualifiers existed AT ALL. **Run-to-run variance in these blocks is large**, so n=1 per arm cannot separate a prompt regression from ordinary noise — and attributing the loss to the envelope would be exactly the unmeasured confident claim this project keeps catching. ★ That is itself the important result: **a single re-record cannot validate a prompt change**, which is a premise the golden set's design has been assuming. ✅✅✅ **CONFIRMED, and the refusal to attribute was the right call.** Had the 25 % drop been written up as an envelope regression — the tidy, available story — it would have been a **published finding that was simply false**, and the fix would have chased a cause that was not there. ★ Item counts across 4 post-envelope runs of ONE prompt: **38, 63, ~55, 48**. ⚠ Run 2 was REFUSED by `X-01` for a case-mismatched quote (`'we have also signed...'` for the filing's `'We have also signed...'`) — and that quote is from the government-funding sentence, so it found the cluster too. ⬜ Options: ⓐ re-run `E-02` k=3 under each arm to separate signal from variance (⚠ ~$3.6, and it is the only thing that would actually answer it); ⓑ amend `S-2` to say a figure the bundle STATES is a fact even if it could also have been computed (⚠ touches EVERY block and invalidates every recording again); ⓒ accept 38 items and re-establish the 3 cases (⛔ rebaselines an unexplained loss — `D2`'s forbidden move) |
| **DX-76** | 2026-09-11 | F2 · the envelope is UNVERSIONED | `test_the_recording_is_not_from_a_RETIRED_prompt_version` compares each recording's recorded `prompt_version` against the version the repo ships — *"re-record with the current prompt, or the suite measures the past"*. It fired correctly when `E-01` went `v3`→`v4` | ⛔⛔ **It cannot see the envelope at all.** `DX-67` prepended `S-1`…`S-6` to **every prompt the project sends** and bumped **no version**: `E-02` is `v2` before and after. ⇒ a pre-envelope and a post-envelope `E-02` recording are **indistinguishable in the trace**, and the golden set is currently grading one of each | `prompts/envelope.py::envelope_hash` · `trace/models.py` · `trace/wire.py` · `F2` `CT-2.2` `A5` | ⛔ high | ✅ **CLOSED 2026-09-11 — adopted (Victor).** `envelope_hash` added to `CT-2.2`, computed from the SAME part list `compose_prompt` uses so the two cannot disagree; both composition roots pass it; a new `F5` guard pins every graded recording to an envelope this repo still ships. ★ **Mutation-verified**: adding one line to `S-2` now REDS the suite — previously it changed every prompt sent and reddened nothing | ★★★ **The largest prompt change this project has made is the one change its prompt-drift guard is blind to.** The guard keys on a per-BLOCK version; the envelope is per-BLOCK-INDEPENDENT text composed in front of all of them, so it sits in the one place the versioning scheme has no name for. ⚠ And the promoted payload cannot settle it either: `promote_recording` elides `request.payload`, which is where the composed prompt lives — so **"was this recording made under the envelope?" is unanswerable from the artifact**. ★★ Concretely, right now: the golden set grades `run-2026-09-09T074110-mu-e02` (**pre**-envelope) alongside three post-envelope recordings — `DX-67`'s rejected option ⓑ, *two prompt regimes in one golden set*, reached not by choosing it but by a guard that could not see it. ⚠ It is held DELIBERATELY (`DX-75` is unresolved, so the post-envelope `E-02` is not yet trustworthy) — but a deliberate split and an invisible one look identical in CI, and that is the defect. ⬜ Fix: record the envelope's content hash on the `ExternalCall` (`compose_prompt` already hashes its sections at declaration) and extend the retired-prompt guard to compare it. ★ Cheap, and it makes the split visible instead of merely known |
| **DX-77** | 2026-09-11 | F5 · 2 E-02 golden cases | `DX-75`'s re-record settled `E-02`, and 6 of 8 cases re-pointed cleanly onto it | ⚠ **2 cases pin a TRANSCRIPTION BOUNDARY the document does not fix.** `gd.period` signed as *"in the next 12 months"*, now *"the next 12 months"*; `gd.value` signed as `"0.115 per share"` with unit `"USD per share"`, now `"0.115"` with the same unit | `tests_src/fixtures/golden/extraction.pending.yaml` | ⚠ low | ✅ **CLOSED 2026-09-11 — ⓒ adopted and BOTH SIGNED by Victor Truong the same day.** `expected` now asserts **evidence_id + status + unit + span** and is SILENT about `value` and `qualifier` — the two fields the model authors. ★ Measured across 4 runs: the SPAN was identical in all 4 (`[55427,55615]`, `[51931,52127]`); the VALUE text varied 3/1 and 1/3. ⚠ Not a weaker case — each subset still matches exactly 1 of 63 items and both RED under span mutation | ★★ **The second is arguably an IMPROVEMENT, which is the uncomfortable part.** `E-01`'s own prompt says *"give the figure without a currency symbol — the currency belongs in the unit"*, and the SIGNED value carries *"per share"* in **both** fields. ⚠ **A golden case is not automatically right because it is signed** — and `D2` is what stops that observation being acted on by the system rather than the fund manager. ★★★ **Third instance today of one pattern**, and it is the day's real theme: `DX-73` a period start the filing never states · `DX-74` a qualifier the model invents · `DX-77` a quote boundary the model chooses. **The golden set keeps asserting things the MODEL authors rather than things the DOCUMENT fixes** — and those assertions cannot be stable, because nothing external holds them still. ★ `F5` §4's subset rule is the existing answer; what these three show is that it has to be applied to `value` itself, not only to `quote`/`span`/`note` |
| **DX-78** | 2026-09-11 | X-01 · quote verification | `X-01` refuses any item whose value is not VERBATIM inside its own quote — *"a value that cannot be found in its own quote cannot be checked, and is refused"* | ⚠ One of three `E-02` runs was refused **whole** ($0.6679, 48–63 items lost) because a quote began `'we have also signed a non-binding term sheet...'` where the filing reads `'We have also signed...'`. **A single capital letter** | `filings/verify.py` · `X-01` | ⚠ low | ⬜ **OPEN — recorded, NOT fixed; it is not obviously a defect** | ★★ **Stated as a trade rather than a bug, because both sides are real.** Strict verbatim is what makes `X-01` worth having: it is the check that catches a paraphrase presented as a quote, and `E-01 v1` was retired for letting exactly that through. ⚠ But the failure mode is **all-or-nothing on a whole run** — one mid-sentence capital cost ~$0.67 and every other item in it. ★ The cheap options are not equal: case-insensitive matching would weaken the guard everywhere to fix a first-character artefact, whereas refusing **that item** rather than the **run** keeps the strictness and bounds the blast radius. ⚠ Neither is free: partial acceptance collides with `MP-7`/`P5`'s *a degraded result is not a short result*, so this needs a decision, not a patch |
| **DX-79** | 2026-09-11 | F5 · which run gets promoted | `DX-75` produced three verified `E-02` runs. To avoid choosing the one that suited the cases, the run was picked by a rule stated BEFORE measuring: **the first verified run** | ⚠⚠ **That rule selected the ONE run of four where the hedge wording differs.** Had `run-…T115923` been promoted instead, BOTH `DX-77` cases would have passed unchanged and the finding would never have surfaced | `tools/promote_recording.py` · `F5` `CT-5.5` | ⚠ medium | ⬜ **OPEN — named, not fixed** | ★★★ **Under a `value`-pinning scheme, whether a golden case passes was partly a COIN FLIP on which run got promoted.** Measured on one reading across 4 runs: *"in the next 12 months"* ×3, *"the next 12 months"* ×1. A case pinning the majority wording passes 3 times in 4 and fails once, for no reason connected to the system being right or wrong. ⚠ **The pre-registered rule did not protect against this** — it protected against ME choosing, which is a different hazard, and it is worth being clear that it worked as intended while leaving this untouched. ★★ `DX-77`ⓒ removes the exposure for these two cases by asserting the SPAN, which was stable 4/4 — but the general problem stands for every case still pinning model-authored text. ★ **The honest framing: the finding surfaced by luck, and is more important for it.** ⬜ Options: ⓐ promote by majority across k runs rather than first-verified (⚠ costs k× every time); ⓑ keep first-verified and require every case to assert only document-fixed fields, so run choice stops mattering (★ this is `DX-77`ⓒ generalised, and the cheaper answer); ⓒ accept it and record `n` on each case |
| **DX-80** | 2026-09-11 | J-blocks · scorecard rubrics | The design doc's `J-03`…`J-06` headings each name the rubric the block emits — *"emits `moat_durability@v2`"* — and `RubricRegistry.published` returns exactly that `<dimension>@v<n>` form | ⛔ **Two of the four do not resolve.** Doc says `moat_durability@v2`; the registry publishes **`@v1`**. Doc says `balance_sheet@v1`; the dimension is **`balance_sheet_resilience`**. ⚠ `RA-52` calls the four dimensions *fixed, versioned and closed* | `scorecard/rubrics/b43_v1.py` · `prompts/e_blocks.py::EMITS_RUBRIC` · doc §J-03/§J-05 | ⚠ medium | ◐ **NARROWED 2026-09-12** — with `v2` published, `J-03`'s *"emits `moat_durability@v2`"* now RESOLVES and matches what the block emits. ⬜ Still open, doc-side only: `J-04`/`J-06` headings say `@v1` (resolves, but the blocks now emit `@v2`), and `J-05`'s `balance_sheet@v1` names a dimension that does not exist. ⚠ Editing those headings also means editing `_BLOCK_HEADINGS` in the drift guard, which pins them verbatim. ◐ **CODE SIDE CLOSED 2026-09-11** — `EMITS_RUBRIC` carries the names the registry can actually resolve, and a structural test now asserts every one resolves. ⬜ **The DOC still says otherwise** and only Victor should reconcile it: `@v2` may record a rubric revision that was designed and never implemented | ★★★ **Nothing caught this because the two documents had never been asked to agree.** The rubric registry has existed since `MS-2`; the J-blocks that emit rubrics were declared **today**. ⚠ A cross-reference with no consumer is not checked, and it reads as settled precisely because it has sat still. ★ The version mismatch is the more interesting half: `@v2` is not a typo shape — someone wrote *v2* meaning a **revised moat rubric**, and what exists is v1. So either a revision is missing or the heading is aspirational, and **the code cannot tell which**. ★★ Recorded rather than reconciled: silently rewriting the doc to match the code would erase the evidence that a v2 was once intended |
| **DX-81** | 2026-09-11 | J-blocks · judgement tool | `DX-64` asked for `J-02`…`J-08`. All seven are now declared verbatim and pinned to the design doc by `RA-13`'s drift guard | ⚠⚠ **Declared is not callable.** `judgement_tool` returns ONE schema — `classify_archetype`, with `archetype`/`runner_up` enums — and `run_judgement_once.main` hardcodes `blk = j01_v1()`. It fits `J-01` and `J-07`; for the other **six** it would demand an enum answer the block never asks for | `tools/run_judgement_once.py::judgement_tool`, `answer_shape`, `main` · `e_blocks.py::ENUM_ANSWER`, `PROSE_REQUIRED`, `FIELD_ENUMS` | ⚠ medium | ✅ **CLOSED 2026-09-11.** Three shapes implemented; `--block` added; **all 8 Stage-A blocks construct a schema and dry-run.** 14 tests, **5 of 5 mutations caught**. ⬜ `RA-32` gating deferred to `DX-82`; `J-03`'s mechanism table and `J-08`'s per-competitor rows remain unmodelled and are asserted-as-absent so they are not assumed present | ★★★ **`DX-23`'s shape one layer up, and the parallel is exact.** `DX-23` found `E-01`'s prompt living only in the design doc with nothing in `src/` able to send it. Here the text is in `src/` and pinned — and still unsendable, because the **answer schema** is the half that was only ever built for one block. ★★ **Three answer shapes live in these seven**, which is the actual work: `enum` (`J-07`, like `J-01` — the only shape tooled) · `rubric level` (`J-03`–`J-06`, 0–4 from `scorecard/rubrics`, with `RA-32` making a level UNAVAILABLE when its `evidence_required` is absent) · `prose` (`J-02`, five numbered parts under a 400-word cap) · and `J-08` is prose with one closed FIELD enum. ⚠ **`E-02` is the warning**: `MP-5` was learned there — *a closed set is DECLARED, never described* — after a free-string `evidence_id` returned all 56 items tagged with the BLOCK id. A rubric block handed `classify_archetype` would repeat that class of error with a 0–4 score. ★ Pinned as a KNOWN LIMIT by `test_dx_81_the_judgement_tool_serves_only_the_enum_shape`, which is written to FAIL when the tool grows a second shape |
| **DX-82** | 2026-09-11 | J-03…J-06 · RA-32 | `RA-32`: *a level whose `evidence_required` items are absent from the bundle is UNAVAILABLE*, and each rubric level in `b43_v1.py` carries its own `evidence_required` tuple | ⚠ **The level enum is currently the full published 0-4, ungated.** `judgement_tool` REFUSES to default it (`P5`), so the composition root passes the full range **explicitly and prints a warning** — but nothing yet intersects the rubric's `evidence_required` with what the bundle actually contains | `tools/run_judgement_once.py::main` · `scorecard/rubrics/b43_v1.py` | ⚠ medium | ✅ **CLOSED 2026-09-12.** `scorecard/availability.py` implements `RA-32`: `available_levels` (ALL of a level's evidence, not any) and `require_levels`, which REFUSES rather than defaulting. The runner now declines a rubric block **before sending**. 10 tests, 4 of 4 mutations caught — the 4th (`if False and gate_error:`) survived the first pass because every test covered the pure function and none covered the CALLER | ★★★ **Where the shortcut was put matters more than that there is one.** The tempting version is `levels=(0,1,2,3,4)` as a default argument inside `judgement_tool` — one line, no warning, and the rubric's entire discipline discarded somewhere nobody reads. ★ Instead the tool RAISES without levels, and the caller must state the range it is offering, in the composition root, out loud. ⚠⚠ **The risk this leaves is real and specific**: `MOAT_DURABILITY` level 4 requires segment income AND competitor capacity evidence; offered ungated, a model with neither can still select it, and the scorecard would record a 4 that the rubric's own criteria forbid. ★ Same family as `PG-10`: *declare the limit on the artifact rather than withhold the artifact* — the block runs, and says what it has not checked |
| **DX-83** | 2026-09-11 | J-blocks · run identity | `run_judgement_once` built `run_id` as `run-<ts>-<ticker>-j01` and ran one block per invocation | ⚠ The `j01` suffix was **hardcoded**, so a `J-05` run would have been filed under `j01`; and eight separate invocations produce eight unrelated `run_id`s with nothing recording that they are one STAGE | `tools/run_judgement_once.py::main` | ⚠ medium | ✅ **CLOSED 2026-09-11** — suffix names what ran; `--stage-a` runs all 8 into ONE `run_id`/trace | ★ `DX-70` had already shown what a mislabelled recording costs, on `filing.json`. ★★ The grouping half matters more: **a stage is a unit**, and `CT-9.2` needs 17 blocks × `K_RUNS` in one replayable trace — eight loose runs would have had to be re-associated by timestamp, which is exactly the kind of after-the-fact reconstruction `F2` exists to make unnecessary |
| **DX-84** | 2026-09-11 | ⛔⛔ Stage A k=1 · GW-23 | `GW-23`: *a truncated response is a failure, not a short answer*, enforced in `Gateway.call` and proven on `DX-69`'s `E-02` truncation | ⛔⛔⛔ **7 of 8 Stage-A calls came back `stop_reason: max_tokens` and ALL 8 printed ✅.** The run reported *"8/8 block(s)"* on **$3.22 of unusable output**. ⚠ `J-01` parsed as valid JSON while MISSING its required `why`; 5 of 8 were unparseable | `tools/run_judgement_once.py` · `MAX_OUT` · `golden/thesis.yaml` | ⛔⛔ **high** | ◐ **CODE FIXED 2026-09-11; the RUN is discarded and NOT promoted** | ★★★ **The judgement path never reaches the Gateway.** It wires `anthropic_transport` straight into `traced_transport`, so `GW-23` — the check that caught `DX-69` on the extraction side three hours earlier — **did not exist on this path at all**. ⚠⚠ Two independent causes, and both had to be fixed: (1) no truncation check; (2) `MAX_OUT = 4_000`, a **THIRD** output budget, **smaller than either already declared** (`call.py`: 20,000 extraction / 16,000 judgement), sitting in a runner nobody had diffed against them. ★ Now sourced FROM `call.py` — one fact, one place. ★★★ **It reached a signed golden case.** Earlier the same day the thesis case was re-pointed onto `run-2026-09-11T111240-mu-j01` — which is **also truncated** (4,000 out, `max_tokens`, no `why`). It PASSED throughout, because `F5` §4's subset rule means it asserts only `archetype`. ★ That is the subset rule earning its keep — and **not** a reason to keep grading a degraded call. Re-pointed back to `run-2026-09-11T025139-mu-j01`, the only COMPLETE `J-01` recording (757 out, `tool_use`, all four fields). ⚠ That one is PRE-envelope, which is a real cost, recorded rather than hidden: **a complete answer under an older prompt is worth more than a cut-off one under the current prompt.** ⚠⚠ **What I did wrong, plainly**: I read `✅ 4,000 out` as success on a number that is *exactly the cap*, and `DX-69` had taught that same signature earlier the same day. The runner told me what I wanted; nothing made it tell me what happened. ✅ **Stage A re-run 2026-09-12: 8/8 `tool_use`, $4.8646.** ⚠ The re-run also corrected the PRICE: ~$4.7, not ~$3.7 — the $0.46/call figure came from measuring TRUNCATED calls. ★ **A price measured on a broken run is a broken price**, and it had already been quoted to the fund manager twice |
| **DX-85** | 2026-09-12 | ⛔⛔ rubrics · E-blocks · bundle | `b43_v1.py`'s `E` dict maps 13 evidence ids the four rubrics require, with its own warning: *"⚠ These must match what B4.2's extractors emit, or a level is unavailable for a NAMING reason rather than an evidential one — which would read as thin evidence and be a wiring bug."* | ⛔⛔⛔ **It is that wiring bug. 3 of 13 match.** The rubrics require prefixes `con. debt. cap. shr. ngp. acc. cmp.` and **not one of those prefixes exists** among the **74** ids the 15 E-blocks emit (`cc. dm. ca. sc. ng. rf. cx.` …). ⚠ And a third layer: `PIN_FIELDS` declares no part kind for extraction OUTPUT at all, so a Stage-A bundle cannot carry `seg.revenue` **even in principle** | `scorecard/rubrics/b43_v1.py::E` · `bundle/models.py::PIN_FIELDS` · doc §E-03…§E-15 | ⛔⛔ **high** | ◐ **ⓐ CLOSED 2026-09-12** (`DX-86`: `v2` approved and published). ✅ **ⓑ CLOSED 2026-09-12** — declared, dry-run, $0; `test_dx_85b_every_id_a_v2_rubric_level_cites_is_emitted_by_a_DECLARED_block` asserts it against the code's registry; pre-flight findings `DX-89`…`DX-93`. Was: declare the E-blocks the `v2` levels cite: **`E-04` `E-06` `E-07` `E-09` `E-10` `E-12` `E-13`** (⚠ corrected: an earlier list said `E-04 E-05 E-06 E-07 E-13` — `E-05` is cited by NO level, and `E-09`/`E-10`/`E-12` were missed; measured from `B43_V2_RUBRICS`). ✅ **ⓒ CLOSED 2026-09-12 (approved by Victor)** — `PIN_FIELDS["extraction"]` pinned by `block_id · prompt_version · source_bundle_hash · run_id · evidence_ids`; `BundlePart` refuses declared ids ≠ the content's FOUND ids; `assemble.extractions()` admits only an X-01-verified pass; `run_judgement_once --extractions RUN_ID…` re-verifies each recording against the filing before it enters. ⚠ Measured: **no existing bundle hash moved** — the hash covers parts, never the table. 23 tests, 14 of 15 mutations caught (the survivor was a redundant check, removed) | ★★★ **`DX-82`'s fix is what made it visible, and that is the argument for building gates before running things.** Wiring `RA-32` turned an unnoticed vocabulary mismatch into a refusal that names itself. ⚠⚠ **Measured consequence**: all four rubrics return **ZERO available levels** against a bare-filing bundle — and the 2026-09-12 Stage A answered all four anyway, returning `moat=1 · earnings=3 · balance=3 · capital=0` for ~$2.6. **Those four numbers rest on nothing structural and must not be quoted** (`PG-10`). ★★ `capital_allocation = 0` is the sharpest illustration: its criterion is *"the bundle does not disclose capital-allocation actions"*, and the MU 10-Q **does** disclose a declared dividend and buybacks — so a WIRING GAP read as an analytical finding, which is precisely what `NoAvailableLevel` now refuses to let happen. ★★ **Refined on drafting: 9 broken of 11, not 10 of 13.** The `E` dict is 13 wide, but `guidance` and `concentration` are cited by NO level — so the load-bearing count is 9. ⚠ `con.customer_pct` has been wrong since it was written and **could not have failed anything**, which is the one place a wrong id is free and therefore permanent. ★ The three reconciliations, in dependency order: ⓐ correct `E`'s ids to the real extractor vocabulary (⚠ a rubric content change — `RA-52` calls the set *fixed, versioned and closed*, so it needs a version bump, and `DX-80`'s unexplained `moat_durability@v2` heading may be exactly this, already anticipated); ⓑ declare the E-blocks that emit them — `E-04` `ng.*`, `E-05` `cc.*`, `E-06` `dm.*`, `E-07` `ca.*`, `E-13` `cx.*`; ⓒ add a bundle part kind carrying extraction output (⚠ `RA-2`/`RA-4` — *"a bundle whose hash definition moves invalidates every baseline recorded against the old one"*) |
| **DX-86** | 2026-09-12 | rubrics · `v2` draft | `DX-85`ⓐ — correct the rubrics' evidence ids to the real extractor vocabulary | ℹ Drafted for review, not applied. **Only `evidence_required` changes: not one `criterion` string is edited and no score moves** | `scorecard/rubrics/b43_v2.py` (was `b43_v2_draft.py`) | ℹ info | ✅ **APPROVED & PUBLISHED 2026-09-12 by Victor Truong — `capital_actions` = ⓐ `ca.capex`.** Published ALONGSIDE `v1` (`RA-52` versioning; `v1` and `B43_RUBRICS` untouched). `EMITS_RUBRIC` → `@v2` for `J-03`…`J-06`. Draft test rewritten to assert the published state | ★★ **Why the criteria are deliberately untouched.** Correcting a wiring fault and revising analytical criteria are two different changes; mixed together, a later score move could not be attributed to either. ★ A test asserts the criteria are byte-identical to `v1`, so the review is *"are these 10 ids right?"* and nothing else. ★★★ **Measured value, stated as a measurement.** It buys **nothing today** — with only `E-01`/`E-02` declared, `v1` and `v2` give identical availability, because the three ids that already resolved are the three `v2` does not change. The gain appears when `E-04`…`E-13` land: `v1` can still score **1 of 4** dimensions, `v2` scores **4 of 4** at every level. ⚠⚠ **One entry is a judgement, not a lookup**: `v1`'s `cap.action` was ONE generic slot and `E-07` emits EIGHT specific ids. The draft picks `ca.capex` (ⓐ) — every operating company deploys capital, so the dimension stays scoreable for one that runs no buyback. ⚠ Rejected ⓑ *cite several ids per level*: `RA-32` requires ALL of a level's evidence, so level 4 would become UNAVAILABLE for a company that does not both buy back and pay dividends — reading as *"could not assess"* when the truth is *"it does not do buybacks"*, which is `RA-32`'s own failure mode arriving from the other side. ⬜ ⓒ *add a generic `ca.action` to `E-07`* is cleanest and most expensive: it moves an E-block's item list, so `E-07`'s prompt text and enum both change and any recording against the old one retires |
| **DX-87** | 2026-09-12 | scorecard · coverage/confidence | `coverage_report(rubrics, extracted)` computes `evidence_coverage` over the union of the rubrics' `evidence_required` (`RA-134`), and `assess_confidence` caps on it | ⚠ **`DX-85` reaches this path too, latently.** `B43_RUBRICS` (v1) is what it is exported with, and v1's ids resolve to no extractor — so any caller passing REAL extraction ids would get near-zero coverage for a NAMING reason, and a confidence cap that reads as thin evidence | `scorecard/coverage.py` · `src/fundamental/__init__.py::B43_RUBRICS` | ⚠ medium | ⬜ **OPEN — latent: nothing in `src/` calls it with real ids yet** | ★ Found while publishing `v2`, and deliberately NOT fixed in the same change: `B43_RUBRICS` is imported by the inherited confidence path and characterization-tested in `tests_src/` (`test_fundamental_b43.py`, `b46.py` — both use synthetic ids, so they stay green either way). ⚠ That is exactly why it would go unnoticed: **the tests that cover this path cannot see the bug**. ⬜ Decide when the first real caller is wired: move the confidence path onto `B43_V2_RUBRICS`, and add a test with REAL extractor ids |
| **DX-88** | 2026-09-12 | runners · choice lists | `run_extraction_once.py` built `--block` choices from `sorted(BLOCKS)` and hardcoded `--prompt-version` to `["v2", "v3"]` | ⚠ Once Stage A was declared, the EXTRACTION runner offered `J-01`…`J-08`; and `E-01`'s shipped `v4` was not selectable | `tools/run_extraction_once.py` | ⚠ low | ✅ **CLOSED 2026-09-12** — block choices filtered by `kind` (`RA-5`); versions derived from the declared `E0n_Vn_TEXT` constants; 1 test | ★ Found while writing the next-session recipe, not by a test: **`DX-72`'s shape a third time** — a list pinned to what existed when it was written. ⚠ The block half was the worse one: `--block J-03` would have sent a judgement prompt through the extraction tool schema |
| **DX-89** | 2026-09-12 | E-04 · X-01 | `X-01` needs every value to appear VERBATIM inside its own quote; one refused item refuses the whole run (`DX-78`) | ⚠ `E-04`'s `ng.recurrence_note` asks for *"the periods it appeared in"* — a LIST gathered across several spans. One quote cannot contain it, so a found item is likely refused, and the refusal takes the run's `ng.adjustment` (the rubric-cited id) with it | `prompts/e_blocks.py::E04_V1_TEXT` · doc §E-04 | ⚠ medium | ⬜ **OPEN — declared `v1` as written (Victor, 2026-09-12)**; nothing runs it until `DX-85`ⓒ and a paid run are approved | ★ The prompt is right that it is a LOOKUP, not an opinion — the defect is shape, not intent. Options: ⓐ keep `v1`, record, measure on the first live run (**chosen**: costs nothing now, and a live run tells us whether the model emits one row per period, which would pass); ⓑ `v2` emitting one item per period with `qualifier` = the adjustment label; ⓒ drop the item and let `D-02` derive recurrence across periods (`AP-5`). ✗ Rejected bumping now: a version change on a prediction, before a single run, is the unmeasured confident claim this log keeps catching |
| **DX-90** | 2026-09-12 | E-07 · S-2 item 3 | `S-2` item 3: *"Do not compute"*; `DX-34` removed `gd.direction` from `E-02` for being a comparison | ⚠ `E-07`'s `ca.dividend` asks for *"per-share and total, **and any change**"*. When the company does not state the change, reporting one means comparing this period's dividend with the prior's — `gd.direction`'s shape exactly. ◐ `ca.authorisation`'s *remaining* is a subtraction when not stated (logged in `DX-92`) | `prompts/e_blocks.py::E07_V1_TEXT` · doc §E-07 | ⚠ medium | ⬜ **OPEN — declared `v1` as written** (same treatment as `DX-89`, Victor 2026-09-12) | ★ Less severe than `DX-34`: *"any change"* is satisfiable by extraction when the filing states the change, and `ca.capex` — the id the rubric cites — is untouched. ⚠ The risk is a model-authored change that fails `X-01` and refuses the run. ⓐ record and measure (**chosen**); ⓑ `v2` reading *"any change the company states"*; ⓒ remove it and derive in `D-02`. ✗ Rejected ⓑ now for the reason given in `DX-89` |
| **DX-91** | 2026-09-12 | E-13 · bundle · X-01 | `E-13` reads *"From the industry material in the bundle"* | ⛔ Two findings. (1) **Needs non-filing evidence**: a 10-Q contains no rival's capacity announcement, so on every bundle this project can build today the block returns `not_found` — `cx.capacity` (rubric-cited) is structurally absent, not thin. (2) **Two items cannot pass `X-01`**: `cx.status` is a closed label the model CHOOSES (`announced \| under construction \| commissioning \| operating` — `DX-34`'s shape), and `cx.source` (*"the bundle item this came from"*) is a pointer, not text a quote can contain | `prompts/e_blocks.py::E13_V1_TEXT` · doc §E-13 · `bundle/models.py::PIN_FIELDS` | ⚠ medium | ⬜ **OPEN — declared `v1` as written (Victor's decision, 2026-09-12).** ⛔ **Both predictions FALSIFIED by the first live run — see `DX-97`** | ★ Harmless today precisely because of (1): with no industry material, every item is `not_found` and `X-01` does not check `not_found`. ⚠⚠ It turns into a run refusal the first time a bundle carries real industry material. ★ `cx.source` is the more interesting half — the bundle ALREADY identifies parts, so a `v2` could let the harness stamp the source from the span rather than ask the model to name it. ⬜ Revisit when an industry part kind exists; `MOAT_DURABILITY` level 4 cannot be available before then regardless |
| **DX-92** | 2026-09-12 | E-06 · E-07 · E-09 · minor pre-flight | Pre-flight of the seven `DX-85`ⓑ blocks against `S-2` item 3 and `X-01` | ◐ Four low-severity shapes, recorded together (Victor, 2026-09-12): **`E-06` `dm.revolver`** — *undrawn* capacity is a subtraction when the filing states only facility size and amount drawn; **`E-06` `dm.covenant`** — *"the direction of the test"* passes only if copied wording ("not to exceed"), not a chosen label; **`E-07` `ca.authorisation`** — *remaining* is a subtraction when not stated; **`E-09` `ap.reserve`** — *"the direction of the P&L effect"* is a label the model would choose. ℹ Also: `ca.buyback`/`ca.issuance`/`dm.instrument` pack 2–4 figures into one id and lean on `qualifier` rows | `prompts/e_blocks.py` · doc §E-06/§E-07/§E-09 | ⚠ low | ⬜ **OPEN — recorded only** | ★ Each is satisfiable by extraction when the filing says it outright, which is the common case — so none justified a version bump before a run. ★ `DX-78`'s whole-run refusal is what makes a low-severity item matter: it can cost the run's rubric-cited `dm.covenant`. Check these first in the first live `E-06`/`E-07`/`E-09` traces |
| **DX-93** | 2026-09-12 | E-10 · MP-5 id parsing | Recipe step 6 generalises `test_mp_5_…`, which parsed ids as the FIRST token of each item line | ⚠⚠ `E-10`'s first item line is `sc.basic / sc.diluted` — two ids, one line. A first-token parse yields `sc.basic` and **silently drops `sc.diluted`**, the id `v2`'s `share_count` levels cite. The enum would then refuse the model the one id the rubric needs, and the refusal would read as *"no diluted share count disclosed"*. ◐ The same first-token regex in `test_rubric_availability.py::test_dx_85_three_of_thirteen…` also misses it — harmless there (it counts `v1` matches only), but its *"74 ids"* figure undercounts by one | `tests/structural/test_prompt_text_matches_spec.py::_item_ids_named_in` · `e_blocks.py::E10_ITEM_IDS` | ⚠ medium | ✅ **CLOSED 2026-09-12** — parser reads slash-joined lines; `test_dx_93_a_slash_joined_line_yields_BOTH_ids` pins it on the real block; mutation `groups()[:1]` caught | ★ Found in pre-flight by reading the prompt, not by a test. ★★ The recipe itself carried the trap — *"generalise the MP-5 test"* would have generalised its parser too. ⚠ Same family as `DX-72`/`DX-88`: a mechanism shaped to the one input that existed when it was written |
| **DX-94** | 2026-09-12 | prompt registry · two places, one fact | `BLOCKS[id]` holds `(factory, ids, version)`, and the factory builds a block carrying its own name and version | ⚠ Found by mutation while declaring `DX-85`ⓑ: a factory building `v2` under a `v1` entry **passed every test**. The drift guard looks the heading up by the REGISTRY's version and compares text, which had not changed; the mismatch would surface only at run time in `registry.get` | `tests/structural/test_prompt_text_matches_spec.py` | ⚠ low | ✅ **CLOSED 2026-09-12** — `test_the_registry_and_the_factory_agree_about_id_and_version`; version and name mutations both caught | ★ `test_stage_a_blocks.py` already guarded the OPTIONS copy for judgement blocks after the same shape bit once; the version and name copies were unguarded for every block. ⚠ Also recorded: a same-size mutation restored within one second left a stale `.pyc`, so a clean file failed once — clear `__pycache__` between mutations |
| **DX-95** | 2026-09-12 | F2 trace · bundle identity | `RA-2`: *two runs with the same hash are comparable; two with different hashes are not* | ⚠ **No trace record carries the `bundle_hash` a call read.** `ExternalCall` records `prompt_version` and `envelope_hash` (`DX-76`) but not the evidence side, so a recording cannot say WHICH bundle it was made over — measured on `run-2026-09-12T024848-mu-stage-a` and every E-block recording. ★ Found wiring `DX-85`ⓒ: `load_extraction_parts` had nothing to check a recording's source against | `src/orchestration/trace/wire.py::traced_transport` · both runners | ⚠ medium | ✅ **CLOSED 2026-09-13 — ⓐ.** `CT-2.2` amended `A6` in `F2` (spec first); `ExternalCall.bundle_hash`; `traced_transport(bundle_hash=…)` records it on success AND failure; both runners pass the bundle actually sent (the judgement runner: the BLIND bundle). 3 tests incl. an AST check of both callers; 4 of 4 mutations caught. ★ First recordings carrying it: `run-2026-09-13T071406-mu-e09`, `…T071638-mu-e10`, `…T071852-mu-e12` | ★ The workaround is stronger than a hash check for its one purpose: the loader RE-VERIFIES every item with `X-01` against the filing bundle, so a quote that does not resolve in this filing refuses, and `source_bundle_hash` is pinned to the bundle that verification actually used. ⚠⚠ It does not fix the general gap: **`DX-85`ⓒ makes Stage-A bundles differ by which extraction runs were loaded**, and nothing in a J-block trace records that — two Stage-A recordings over different extraction sets would look comparable. ⓐ add `bundle_hash` to `traced_transport`'s record (`F2`-governed path — read the spec first); ⓑ record it in the runner's own trace line. ★ Recommend ⓐ before the next Stage-A live run |
| **DX-96** | 2026-09-12 | E-09 · E-10 · E-12 live · GW-23 | The seven `DX-85`ⓑ blocks run live once on MU, k=1 (approved by Victor): extraction budget `MAX_TOKENS["extraction"]` = 20,000, `llm.deep.effort=medium`, adaptive thinking | ⛔ **3 of 7 truncated — E-09, E-10, E-12 — and each returned `{}`**: all 20,000 output tokens went to THINKING, none to the tool call. `GW-23` caught all three (`TruncatedError` → `DegradedCallError`, runs closed `FAILED`, nothing persisted). ✅ E-04 (1,363 out), E-06 (6,485), E-07 (6,529), E-13 (8,739) completed with `stop_reason: tool_use`. **Spend $4.74 measured** — $2.10 useful, **$2.64 wasted** | `.state/runs/run-2026-09-12T222227-mu-e09` · `…T222652-mu-e10` · `…T223113-mu-e12` | ⚠ high | ◐ **2 of 3 FIXED 2026-09-13 (ⓐ, approved).** `--effort low`: **E-10 ✅ 12 items, 1,715 out, $0.42 · E-12 ✅ 15 items, 2,558 out, $0.44 · E-09 ⛔ truncated AGAIN, 20,000 out, $0.88.** ⚠⚠ **Two diagnostic errors of mine, recorded:** (1) mid-run I reversed the diagnosis to *"`{}` is a cut-off tool call, so effort is the wrong lever"* (`to_transport_result` returns `json.dumps(blk.input)`, and a truncated streamed tool call's input is `{}`) and **stopped the loop — killing E-12 ~2 s after launch** (no tokens recorded; the console is authoritative). E-10's success minutes later falsified the reversal for E-10/E-12: needing ~2k tokens at low effort, they cannot have spent 20k writing the answer at medium — that was thinking. E-12 was relaunched under the same approval. (2) Both readings came from inference, not measurement: **`{}` cannot distinguish thinking from a truncated tool call**, because the transport discards thinking blocks and partial tool input. ⬜ **E-09 still open**, and un-diagnosable from what is recorded. ✅ **MEASURED 2026-09-13 (instrumented, then one approved retry, $0.88):** `tools/anthropic_transport.py::tally_stream` now records `stream_chars` {thinking, text, tool_input} and a truncated call's `partial_tool_input` (2 tests + a caller test; 3 of 3 mutations caught). E-09 at low effort: **20,000 out, `thinking 0 · text 0 · tool_input 0`, text `{}`** — the tool block OPENED and was cut before ONE character of JSON, so the budget went to thinking, which Opus 5 does not stream by default (`ThinkingConfigAdaptiveParam.display` ∈ `summarized · omitted`; the SDK's `build_events` source was read to confirm the tally counts the raw deltas). ★ **E-09 is a thinking runaway, not an oversized answer.** ⛔ **ⓐ thinking OFF is RULED OUT by `GW-9c`** (`L2-shared-infrastructure` §5.2a, enforced in `gateway.py::decoding_for`): *"Opus 5 can then write a tool call into VISIBLE TEXT — the turn succeeds, the call never runs"* — found before building it, 2026-09-13. ★ **ⓑ `E-09 v2` ADOPTED by Victor 2026-09-13 and run once (approved, $0.88): ⛔ TRUNCATED AGAIN** — `run-2026-09-13T143624-mu-e09`, `effort: low`, 20,000 out, `tool_input 0`. **The hypothesis below is FALSIFIED**: scope and a stated empty answer did not stop the runaway. ★ The tally was VALIDATED against successful instrumented calls the same day (J-05 `tool_input` 14,773 chars ≈ 14,918-char answer; J-06 10,331 ≈ 10,491), so the zero is real: **v1 and v2 both spend the whole budget on hidden thinking before emitting one character.** ✅ **Diagnostic run 2026-09-13 (approved, $0.88):** `tools/anthropic_transport.py` gained an opt-in `thinking_display` (thinking stays ON, `GW-9c`) and keeps visible thinking on a truncation; `run_extraction_once --thinking-display summarized`. `run-2026-09-13T151010-mu-e09`: ⛔ truncated again, `thinking 262 · text 0 · tool_input 0`. The summary: *"I'm pulling out the relevant items now: the reclassification of prior-period amounts counts as a presentation change, as does the segment reorganization… I'll quote those directly, and mark the rest as not found."* ★ **The call had DECIDED its answer and still wrote no tool JSON in 20,000 tokens.** ⚠ A summary does not measure hidden thinking length, so *"stuck thinking"* vs *"stuck after deciding"* is still not separable. ⚠⚠ I first read *"recast in the 10-K"* as knowledge from after the as-of date; **retracted** — the 10-Q says so itself (line 1146). Checking it found `DX-102`. ⏸ **SKIPPED 2026-09-13 by Victor's decision** — no further spend on E-09. **Total $4.40 over 5 truncated calls.** Consequence, stated: `J-04` (`earnings_quality@v3`, needs `searched:ap.change`) stays UNSCOREABLE for MU. ✗ Rejected: a higher-cap diagnostic (buys thinking, not headroom, at up to 2× the price); a third prompt version (two already failed, so a third would be a guess). ⬜ Revisit on a different filing or model version ◐ Hypothesis, from the filing, not measured: MU's 10-Q discloses essentially NO policy change — three FASB ASUs *issued* but not adopted (lines 524-530) and critical estimates cross-referenced to the 10-K (line 1422) — so the honest answer is almost all `not_found`, and `v1` gives no scope (*"any change in … estimate"*), no line on unadopted standards and no stated empty answer. `E-04`, also all `not_found`, completed: it has a lead sentence and explicit limits. ⓒ raise the cap (✗ buys thinking, not headroom). **Spend on `DX-96`: $2.63 measured** (+ the killed call) | ★★ `GW-23` doing its job on the extraction path, three for three — contrast `DX-84`, where the judgement path had no such check. ⚠ **Not attributable from one sample** (lesson `DX-75`): the three that thought forever share no obvious prompt feature — E-09/E-10 have no lead sentence, but neither does E-06, which completed. ⓐ re-run the three with `--effort low` (the runner's existing knob: *"extraction is transcription; thinking is what truncates a run"*) — worst case 3 × $0.88; ⓑ raise the cap (✗ rejected: `run_extraction_once`'s own comment — *a bigger ceiling buys more thinking, not more headroom*); ⓒ lower effort for every extraction block by default (✗ not on one sample). ★ Recommend ⓐ |
| **DX-97** | 2026-09-12 | ⛔ E-13 · X-01 cannot see meaning | `DX-91` predicted E-13 would return `not_found` on a 10-Q, and that `cx.status`/`cx.source` would fail `X-01` | ⛔⛔ **Both predictions were WRONG, and the truth is worse.** E-13 returned **37 items, every one passing `X-01`** — and every row is **MICRON'S OWN capacity** (Boise, Clay NY, Singapore HBM, Taiwan, Gujarat, Hiroshima, Xi'an) with `cx.competitor = "Micron Technology, Inc."` quoted from the cover page. The model satisfied `X-01` by copying verbatim fragments: `cx.status` = *"Construction of the fab began in October 2023"*, `cx.source` = *"For the quarterly period ended May 29, 2025"*. ⚠ **Consequence, measured by dry-run**: loading this run adds `cx.capacity`, which opens `moat_durability` **level 4** — a top moat score whose criterion needs COMPETITOR capacity, supported by the company's own fabs | `.state/runs/run-2026-09-12T223538-mu-e13` · `prompts/e_blocks.py::E13_V1_TEXT` · `run_judgement_once --extractions` | ⛔ high | ✅ **CLOSED 2026-09-13 — ⓑ + ⓒ.** `filings/subject.py`: the registrant is READ from the cover page (the line above *"(Exact name of registrant…)"*, never hardcoded); any `cx.competitor` naming it — full name, bare first word, ticker or `we` — raises `SubjectIsRegistrantError` and refuses the WHOLE result. Applied in `run_extraction` (after `X-01`) AND in the Stage-A loader, so the pre-guard 2026-09-12 recording is refused too (measured: *"5 of 5 cx.competitor item(s) name the registrant"*). ★ Narrow by design: `Advanced Semiconductor Engineering` is not `Advanced Micro Devices`. 20 tests; 8 of 8 mutations caught after one was killed by a new test. ⓐ (`E-13 v2`) still deferred until an industry part kind exists | ★★★ **`X-01` checks that a value is IN the document, never that it ANSWERS the question.** That limit was always true and never bit, because every earlier block asked about the registrant. ★ E-13 is the first block whose subject is someone else. ⚠⚠ I recorded `DX-91` as *harmless today because everything will be `not_found`* — a prediction that took one run to falsify; recorded rather than edited. Options: ⓐ `E-13 v2` saying *a company OTHER than the registrant* (a doc change + version bump); ⓑ a deterministic guard: `cx.competitor` equal to the registrant's name refuses the item (`AP-5` — cheap, catches exactly this); ⓒ do not run E-13 until an industry part kind exists (`DX-91`). ★ Recommend ⓑ + ⓒ now, ⓐ when industry material exists |
| **DX-98** | 2026-09-12 | ⛔ RA-32 · partial evidence forces the floor | `RA-32`: a level whose `evidence_required` is absent is UNAVAILABLE; `require_levels` refuses only when NO level is available | ⛔⛔ **With E-10/E-12 missing, `J-05` and `J-06` are offered `levels=(0,)` — ONE option.** Level 0 cites the least evidence (`dm.ladder`; `ca.capex`), so partial evidence mechanically collapses the enum to the floor, and a live call would record **0 by construction**. ⚠ That is the ungated `capital_allocation = 0` of `DX-85` arriving again THROUGH the gate — on a 10-Q that discloses dividends and buybacks (E-07 found both) | `scorecard/availability.py::require_levels` · `tools/run_judgement_once.py` · `b43_v2.py` level shapes | ⛔ high | ✅ **CLOSED 2026-09-12 — ⓐ chosen by Victor.** `require_levels` raises `PartialRubricEvidence` (a `NoAvailableLevel` subclass, so every existing caller refuses too) unless EVERY level is available; the runner prints `⛔ DX-98 REFUSES — partial rubric evidence`. Measured on MU's real extraction set: all four dimensions now refuse (was J-03 `(3,2,1,0)`, J-05 `(0,)`, J-06 `(0,)`). 5 tests, 4 of 4 mutations caught (incl. *refuse only a single level* and the runner's `except`) | ★★★ **A single available level is not a selection, it is an assertion the schema makes on the model's behalf.** ★ The rubrics are ordered so HIGHER scores need MORE evidence — sensible for stopping an unsupported 4, and exactly wrong when evidence is missing for a WIRING reason (a truncated run), because the missing-evidence answer becomes the worst score. Options: ⓐ refuse unless EVERY level is available — score a dimension only when its whole rubric is applicable (strict; `J-03` would refuse too until `cx.capacity` is real); ⓑ refuse when fewer than two levels are available (✗ still biases toward the low end); ⓒ record `NoAvailableLevel` with the missing ids and never score partial. ★ Recommend ⓐ — it is the only one where a missing input cannot move a score |
| **DX-99** | 2026-09-12 | earnings_quality@v2 · rubric shape | Every `earnings_quality` level (0-4) requires `ng.adjustment` | ⚠ **MU's 10-Q presents NO non-GAAP measure** — E-04 returned all five items `not_found`, with the note *"no non-GAAP measure is presented"*. So `J-04` refuses at EVERY level for this company, permanently, and would for any issuer that does not report adjusted figures | `scorecard/rubrics/b43_v2.py::EARNINGS_QUALITY_V2` · `.state/runs/run-2026-09-12T221728-mu-e04` | ⚠ medium | ✅ **CLOSED 2026-09-13 — `earnings_quality@v3` published at Victor's instruction.** New evidence form **`searched:<id>`**: satisfied when the E-block completed, passed `X-01`, and explicitly RETURNED the item, found or `not_found` (`pins["searched_ids"]`, checked against the part's content like `evidence_ids`). `v3` = `v2` with `ng.adjustment`/`ap.change` → `searched:` at every level; **criterion text and scores byte-identical** (asserted). `J-04` emits `@v3`; one `PUBLISHED_RUBRICS` list feeds runner and tests. Measured: MU E-01+E-04+E-09-shaped evidence → `(4,3,2,1,0)` under v3, refused under v2. 13 tests, 6 of 6 mutations caught. ⚠ **Cost, stated**: `searched:` rests on `not_found`, which `X-01` does not verify — the model's located claim of absence. ⚠ **Not generalised**: the same shape exists for `dm.covenant`, `cp.statement`, `cx.capacity` — each a separate criteria decision | ★★ The absence of non-GAAP adjustments is arguably itself earnings-quality EVIDENCE (nothing is being adjusted away), and `RA-32` turns it into *"could not assess"* — `RA-32`'s own failure mode, from the rubric side. ⚠ Fixing it is a CRITERION change, which `DX-86` deliberately kept out of the wiring revision: it needs a `v3` and your judgement, not mine. ★ Also a lesson for the rubric design: a level that cites an item whose honest answer can be `not_found` is unavailable exactly when that answer is informative |
| **DX-100** | 2026-09-13 | ⛔⛔ RA-31 · rubric blocks select a number BLIND | `RA-31` (`scorecard/score.py`): *"the model selects a CRITERION and the score is derived — a level with no written text is a number wearing a rubric's shape"*; `Selection.criterion` is the echoed level text and `ScoreEmittedError` refuses a bare number | ⛔⛔⛔ **The rubric criteria are sent NOWHERE.** Found on the first GATED rubric run (J-05 + J-06 over 7 verified extraction runs, approved, $1.72, both `tool_use` and complete): `judgement_tool`'s rubric shape offers `level: integer enum [4,3,2,1,0]` with no criterion text, `compose_prompt` includes none, and the J-block text says only *"Select ONE rubric level"*. The model said so itself — J-05: *"the enumerated criteria text was not supplied to me, so this mapping is mine"*. ⚠ **J-05 = 3 and J-06 = 0 are therefore uninterpretable and must not be quoted (`PG-10`)** — J-06's 0 is a live example: level 0's criterion is *"the bundle does not disclose capital-allocation actions"*, while the same answer says the bundle *"resolves dilution and the dividend commitment"*; with no criterion and no `insufficient_evidence` option (`MP-7`) the model used the floor to mean *ungradable* | `tools/run_judgement_once.py::judgement_tool` (rubric shape, `DX-81`) · `scorecard/score.py::Selection`, `derive_score` · recordings `run-2026-09-13T123201-mu-j05`, `…T123410-mu-j06` | ⛔⛔ **high** | ✅ **CLOSED 2026-09-13 — ⓐ ⓑ ⓒ ⓓ, approved.** `scorecard/selection.py`: `offer()` shows the available levels' CRITERIA (never their scores) in a string-seeded order; `judgement_tool` answers `criterion: enum[…offered, insufficient_evidence]`; `resolve()` → `derive_score`, refusing an invented or un-offered criterion (`ScoreEmittedError`) and a level without its evidence (`LevelUnavailableError`); `insufficient_evidence` resolves to NO score. The runner records `option_permutation` + `option_seed` in each call's trace request. 13 tests incl. the LIVE path driven offline against a fake transport; **9 of 9 mutations caught**. ★ **Re-run (approved, $1.69 measured):** `run-2026-09-13T181048-mu-j05` → **`balance_sheet_resilience@v2` = 1** (was 3 blind) · `…T181257-mu-j06` → **`capital_allocation@v2` = 4** (was 0 blind); both `tool_use`, closed `SUCCESS`, rubric in payload, the blind run's *"criteria text was not supplied"* assumption gone. ⚠ **k=1 — not quotable as established (`DX-75`, `PG-10`)**, and both now surface CRITERIA questions → `DX-101` | ★★★ **Every gate built this week guarded a selection the model made blind** — `RA-32` (`DX-82`), all-or-nothing levels (`DX-98`), extraction parts (`DX-85`ⓒ) — and the ungated 2026-09-12 Stage A had the same defect, so its `moat=1 · earnings=3 · balance=3 · capital=0` were blind twice over. ★ Nothing caught it because the schema test asserted the enum's SHAPE (`int`, `(0..4)`), and the inherited contract that forbids it (`Selection`, `derive_score`, `ScoreEmittedError`) is never called by the runner — `DX-81` built a second, weaker answer path beside it. ⚠ `DX-23`'s shape a third time: the capability existed and nothing on the live path used it. **Proposed fix (free):** ⓐ render the AVAILABLE levels' criterion text into the payload in a recorded order (`RA-17` / `P-1`); ⓑ make the tool's answer an enum of those criterion STRINGS, not integers; ⓒ derive the score through `score.py::derive_score`, so `ScoreEmittedError`/`LevelUnavailableError` guard the live path; ⓓ add an explicit `insufficient_evidence` exit (`MP-7`) so the floor is never used as a proxy. Then a re-run (~$1.7) — the first interpretable rubric score |
| **DX-101** | 2026-09-13 | rubric criteria · ambiguity surfaced by the first criterion-selected scores | `DX-100`'s re-run: the model now argues from the criterion TEXT | ⚠ Two criteria are decided by WORDING rather than by the business. **① `balance_sheet_resilience` level 1** — *"Covenant headroom is **absent** or breached"*. MU's 10-Q discloses the covenant (net leverage ≤ 3.25x) but not the headroom, and the model read *absent* as *undisclosed*: it scored **1** while stating the balance sheet *"looks capable of absorbing a bad cycle without an equity raise"* — *"the selection follows the criterion text, not the overall impression."* The same non-disclosure lands in the level ABOVE the floor. ★ `E-06`'s own note partly supports that reading (*"a company comfortably inside its covenants usually says so"*), so this is a real analytical choice, not a typo. **② `capital_allocation` level 4** — *"buybacks were not made at prices the filings later show were high"*. With no repurchases in the window, the model scored **4** on a stated ASSUMPTION that abstention satisfies price discipline, and says a reader requiring demonstrated discipline should take the adjacent option | `scorecard/rubrics/b43_v2.py` (`BALANCE_SHEET_RESILIENCE_V2` level 1, `CAPITAL_ALLOCATION_V2` level 4) · recordings `run-2026-09-13T181048-mu-j05`, `…T181257-mu-j06` | ⚠ medium | ✅ **CLOSED — REWORDED 2026-09-13 at Victor's instruction, then MEASURED.** `b43_v3.py`: `balance_sheet_resilience@v3` — level 1 *"exhausted or breached"* (adverse only); level 3 *"disclosed but thin, or not disclosed"*; level 4 unchanged (still requires DISCLOSED headroom). `capital_allocation@v3` — level 4 adds *"(a window with no buybacks meets this condition)"*. Resolved in the direction of `E-06`'s note (silence is mildly negative, never the second floor) and of `DX-99` (an absence is not scored as a defect). Evidence, scores and every other level byte-identical (asserted); `J-05`/`J-06` emit `@v3`. 5 tests, 6 of 6 mutations caught. ★ The seed covers run seed + bundle + block, NOT the rubric version, so a v3 re-run at seed 0 shows the v2 run's option ORDER — isolating the wording change. ✅ **MEASURED 2026-09-13, k=3 (approved, $4.77): `balance_sheet_resilience@v3` = 3 · 3 · 3; `capital_allocation@v3` = 4 · 4 · 4** — seeds 0/1/2, three different option orders per block, all `tool_use`, all closed `SUCCESS`. ★ **Attributable:** seed 0 shows J-05 the SAME order as the v2 run that scored 1, so 1 → 3 is the wording change alone. ★ **`RM-2`-readable:** every run names the same adjacent option as its boundary (J-05 → *"a maturity falls inside the horizon…"*; J-06 → *"broadly match, with one departure"*), so the stability is not three coincidences. ⚠ Still ONE filing, ONE bundle, and a model grading its own extraction's evidence — stable is not correct: these are candidates for Victor's golden judgement, not established values (`D2`, `PG-10`). Recordings `run-2026-09-13T184111/184403/184703-mu-j05`, `…184227/184532/184846-mu-j06` | ★★★ **This is `DX-100` paying for itself within one run.** Blind integers could never have shown a criterion was ambiguous; the criterion echo plus the model's stated ASSUMPTION names the exact clause. ⓐ split *absent* into *"not disclosed"* and *"none remains or breached"* (a `v3`, and decide which level non-disclosure belongs in); ⓑ make level 4 require a repurchase record, or add *"no repurchases in the window"* explicitly to a level; ⓒ leave both and let `k`>1 and `RM-2` dispersion show whether the wording is under-determined (`RA-34`). ⚠ Not attributable to the business yet: k=1 |
| **DX-102** | 2026-09-13 | ⛔ bundle contamination · the fixture's own header | `RA-1`: *every LLM call takes an EvidenceBundle and nothing else*; `RA-19`: the bundle is evidence, assembled mechanically | ⛔⛔ **Every call this project has made sent the fixture's 60-line REPO ANNOTATION HEADER as if it were part of the SEC filing.** `tools/run_extraction_once.py::build_bundle` reads the WHOLE file, and `tests_src/fixtures/filings/{MU,AMD}_FY2025Q3_10Q.txt` begin with *"PROVENANCE — do not edit…"*, converter history, *"WARNING - READ BEFORE ESTABLISHING A GOLDEN VALUE"*, a reference to `fmp-api trap 1`, and *"This rendering is produced by a converter an AI agent wrote, and that converter has been wrong three times"*. Measured: `'READ BEFORE ESTABLISHING A GOLDEN VALUE' in build_bundle().parts[0].content` → `True` | `tools/run_extraction_once.py::build_bundle` · both filing fixtures · every recording (extraction and judgement) | ⛔⛔ **high** | ✅ **CLOSED 2026-09-13 — ⓑ, approved.** Measured FIRST: **0 of 1,980** recorded extraction quotes and no judgement answer cite the header. Each header moved VERBATIM to `<NAME>.meta.txt`; its place in the `.txt` filled with SPACES (newlines kept) — **same length, same line numbers, same character offsets, body byte-identical** — so every citation made before the move (golden `source` lines, L3 rows, span selectors) still resolves. `build_bundle` now REFUSES a fixture carrying repo annotation (`assert_no_repo_annotation`). ⚠⚠ **A first attempt used blank LINES only**: line numbers held, character offsets moved, and an AMD golden selector pinned at `@22633:22914` became UNRESOLVABLE — and I first misread the one red regression test as J-07. Caught by listing the diverged cases instead of trusting the count. 6 tests; an offset-shift mutation is caught by both the fixture test and the golden regression. ⚠ New recordings get a new `bundle_hash` (`RA-2`): pre-move recordings stay valid evidence but are not hash-comparable with post-move ones | ★★★ Found by checking a claim of mine rather than trusting it: the E-09 diagnostic's thinking mentioned a *"10-K"*, I suspected knowledge from after the as-of date, and verifying the quote led to the header. ⚠ **Consequences:** (1) `X-01` would ACCEPT a quote taken from our own notes — the span resolves in the bundle; (2) the header tells the model how the golden set is built and that the text may be wrong, which is the anchor `MP-3` exists to deny; (3) the note *"Micron REORGANISED… will RECAST segment reporting in the FY2025 10-K"* is repo commentary a model can cite as filing fact (the 10-Q happens to say the same, line 1146). ⓐ strip the header in `build_bundle` (body after the closing `====` line) — new `bundle_hash` for every future recording; existing ones stay valid evidence but are not hash-comparable with new ones; ⓑ move the header to a sidecar `.meta` file (cleanest, same hash consequence); ⓒ leave it (✗ contaminated evidence). ★ Recommend ⓑ, and check whether any recorded quote cites a header line before deciding |
| **DX-103** | 2026-09-13 | F10 · real EDGAR data · `CANONICAL` | `AC-F10.7`: trailing = four discrete, contiguous EDGAR quarters; `FE-2`: a canonical-item change versions the feature contract | ★ **Micron's real facts broke two synthetic assumptions.** (1) Quarters ABUT — gaps **[1, 0, 0]** days — so the first rule (1–7 days) refused a valid trailing year. (2) MU reports interest as `InterestExpenseNonoperating` and debt as `DebtCurrent` / `LongTermDebtAndCapitalLeaseObligations` (lease-inclusive); `CANONICAL` maps none of them, so the valuation was `ValuationUnavailable` on real data | `src/feature_engineer/valuation/basis.py` · `src/data_engine/ingest/edgar_facts.py::FEATURE_TAGS` · `tests_src/fixtures/edgar/MU_facts_valuation_subset.parquet` | ⚠ medium | ✅ **CLOSED 2026-09-14 — Victor: into `CANONICAL`.** Fallbacks moved to `CANONICAL` (second in preference order); `VALUATION_FALLBACKS` removed; `fundamental` feature contract v2 → v3. ~~FIXED for valuation 2026-09-13; `CANONICAL` decision OPEN.~~ Contiguity 0–7 days. `VALUATION_FALLBACKS` consulted by `basis.py` only; `LEASE_INCLUSIVE_TAGS` make `known_omissions` truthful per result. Real-data integration tests assert cash/debt/shares against 10-Q lines. ⬜ Victor: add the fallbacks to `CANONICAL` (a feature-contract version) or keep them valuation-only | ✗ Adding to `CANONICAL` silently (would move every `f_*` feature under `FE-2`) · ✗ 1–7 days kept (refuses real data). ★ Lesson: synthetic rows encoded my assumption about filings; only a real ingest tested it |
| **DX-104** | 2026-09-13 | F10 `D6` · `D5` cycle averages | `AC-F10.17`: `t = income_tax ÷ pretax_income`; pretax ≤ 0 refuses, never a substituted rate | ⛔ **The rule that keeps the trailing basis honest makes a cycle average impossible for a cyclical.** MU FY2016 and FY2023 (THE trough) have pretax losses ⇒ no D6 FCFF ⇒ any window spanning the trough refuses. Averaging the remaining years would silently drop exactly the years a cycle average exists to include | `src/feature_engineer/valuation/normalised.py::_window` · `basis.py::_d6` | ⚠ high (blocks `J-20` on MU) | ✅ **CLOSED 2026-09-14 — Victor: ⓐ `t = 0`.** `D6` → `fcff…v2`, `tax_rule` recorded, AC-F10.17 amended; MU FY2016/FY2023 now computed and J-20's live window spans the trough. ~~OPEN — Victor.~~ Before: refuse, naming every unusable year (`AC-F10.19`). ⓐ `t = 0` when pretax ≤ 0 (no tax shield on interest in a loss year; amends `AC-F10.17`, new `FORMULA_ID` version) · ⓑ keep refusing (J-20 must choose a window without loss years — biased) · ⓒ statutory rate (✗ a substituted default, `P5`). ★ Recommend ⓐ | ★ A formula can be right for its first use and wrong for its second; the second use (`D5`) arrived the same day |
| **DX-105** | 2026-09-13 | F10 `D5` · `RA-45` · `VS-4` | `RA-45`: *"D-01 performs no arithmetic that D-02 could perform"* (structural: no pandas in `src/fundamental`) | ⛔ **The first `D5` build put the cycle averages in D-01** (`src/fundamental/valuation/normalise.py` imported pandas and averaged). `tests_src/test_architecture.py::test_architectural_rule_holds[RA-45]` and `test_fundamental_b46.py::test_src_fundamental_computes_no_series_arithmetic` went red. My spec text (`D5`, `CT-F10.3`) had said *"plain D-01 code computes"* — reading `VS-4` literally | `src/fundamental/valuation/normalise.py` · `src/fundamental/bundle/assemble.py::annual_history_part` | ⚠ medium | ✅ **CLOSED 2026-09-13.** Averages, per-year margin and the annual history moved to D-02 `valuation/normalised.py` (`FORMULA_ID normalised.cycle_average_fcff_or_margin.v1` + MethodEntry); D-01 validates the choice and records provenance (`computed_by` names the D-02 function); `annual_history_part` renders D-02's margins. `AC-F10.19` added (spec first), traceability 167 rows. Tests: D-02 known answer, gap refusal, `as_of` filter, mixed currency, and a check that the D-01 file holds no arithmetic tokens. Mutations: 6/6 D-02, 4/4 D-01 guards caught (2 survivors found and closed) | ✗ Exempting the file from `RA-45` (the rule is right: given a method and window, averaging is judgement-free). ★ `VS-5` had warned that `VS-4`'s wording invites this misreading — it did |
| **DX-106** | 2026-09-14 | F10 `D8` · net debt · operating leases | `D2`: FCFF at a firm rate minus net debt; `D6`: OCF-based flow | ⚠ **Victor's `Q2` answer ("leases count in net debt") is incoherent for OPERATING leases under `D6`.** ASC 842 puts operating-lease payments in operating cash flow, which `D6` already subtracts; adding the liability to net debt counts the lease twice (`D-19` in miniature). Finance leases are coherent: principal is financing cash flow | `src/feature_engineer/valuation/basis.py::balance`, `::known_omissions` | ⚠ low in $ (MU: liability ~$0.7B vs ~$400B equity at the 2026 value) | ✅ **CLOSED 2026-09-14 — Victor: ⓐ leave them out.** Declared on every result under `net_debt.excluded_by_design` with the reason, removed from `known_omissions` (a choice is not a gap); spec `D8` / `CT-F10.2` / AC-F10.20 amended; test `::test_ac_f10_20_operating_leases_are_excluded_by_design_not_omitted` (a 999,999 operating-lease liability moves nothing; removing the field is caught). ~~HELD~~ · ✗ ⓑ count + add back lease cost (`v3`; MU stopped tagging `OperatingLeaseCost` after 2025-11-27) | ★ A decision taken on a question that did not mention the flow side. ⚠ Measured the same day: both MU debt tags ALREADY include finance leases (`DebtCurrent` = `FinanceLeaseLiabilityCurrent` 538 = 538; `LongTermDebtAndCapitalLeaseObligations` 15,003 = `LongTermDebt` 12,434 + finance-lease non-current 2,569) — adding the lease tags would have double-counted ~$3.1B |
| **DX-107** | 2026-09-14 | mutation testing · Python bytecode cache | "Mutation-test every guard and its caller" (working method) | ⛔ **A mutation run can report the WRONG mutant.** CPython revalidates `__pycache__/*.pyc` by source mtime (1 s) and size; the `any(` → `all(` mutant has the same size and was restored in the same second, so the next full suite ran the MUTANT's bytecode against correct source — `test_ac_f10_20_an_unreported_item_is_declared_never_zero[extra2]` failed on correct code | the mutation scripts of 2026-09-13 and 09-14 | ⚠ medium (every same-size mutation since the practice began is suspect) | ✅ **CLOSED 2026-09-14** for this change: caches cleared and all 10 mutations re-run under `PYTHONDONTWRITEBYTECODE=1` — 10/10 caught. ★ Rule from now: run mutations with `PYTHONDONTWRITEBYTECODE=1` (or `-B`) and clear `__pycache__` after | ★ Found because a test failed on code I could read was right, and I checked the loaded function instead of the file. ⬜ Earlier same-size mutation results (e.g. `<`/`>` swaps) were not re-run |
| **DX-108** | 2026-09-14 | `J-20` live · D-07 history | `S-2`, `X-01`, `RA-1` | Found by the first live `J-20` (`run-2026-09-14T122547-mu-j20`, $0.5026, `tool_use`): (1) `exclusions[].quote` is NOT verified in code — all three were verbatim by hand; (2) the model labelled nine-month figures "FY2024"; (3) the annual history shows a D-07 **FY2008 row with a 0-day span** (an instant fact classified annual?); (4) revenue absent FY2009–FY2015 (older revenue tag not in `CANONICAL`); (5) `J-20` not in `STAGE_A_ORDER` | `tools/run_judgement_once.py::normalisation_outcome` · `src/data_engine/pit/snapshot.py` · `src/feature_engineer/fundamental/items.py` | ⚠ medium (1) · low (2-5) | ◐ **(1) and (5) CLOSED 2026-09-14:** exclusion quotes verified in code before any basis (`normalise.py::assert_exclusions_quoted`, X-01's whitespace/typography rule; `normalise(..., bundle=)` now required; caller test on the real J-20 quote); `J-20` is last in `STAGE_A_ORDER` and `--stage-a` refuses without `--annual-history`. ⬜ (3) (4) open. ~~OPEN.~~ (1) run the exclusion quotes through `X-01` before the basis is recorded; (3) find the 0-day annual row's source; (4) add `SalesRevenueNet` to revenue (another `fundamental` contract version); (5) Victor: add J-20 to Stage A (+$0.50/run) | ★ The answer itself was sound and hand-checked: $11,585M ÷ 9 = $1,287M |
| **DX-109** | 2026-09-14 | `J-09` v1 · Stage B inputs · planning | `J-09` text: *"the price, the market capitalisation, the multiples, D-02's fair value with its sensitivity band and its arithmetic trail, and the consensus view"*; item 1: *"D-02 supplies the reverse-engineered figures — the growth, margin and duration implied"* | Found while planning Stage B, before any declaration: **two of `J-09`'s inputs do not exist and one cannot exist as written.** (1) **Consensus at a past `as_of` is only partly reconstructable**: `analyst-estimates` is Class B (`date` = TARGET period, no publication axis — `fmp-api` trap 5), so the MU 2025-06-26 bundle cannot carry the forward estimates a person saw; rating actions and price-target changes ARE event-dated (Class A: `grades`, `price-target-news`). (2) **D-02 solves only stage-1 growth** (`F10` `D7`); item 1 asks for implied margin and duration too. (3) No multiples output exists in D-02 (`F10` non-goal) | `sdd/design/rel6_design/L1-fundamental-analysis-master-prompt.md` §Stage B · `F10` `D7` | ⚠ medium (blocks declaring `J-09` verbatim) | ✅ **CLOSED 2026-09-14 — Victor: ⓐ.** `J-09`…`J-17` declared verbatim (drift-guarded); the absent inputs are a `computed` part `absent.stage_b_to_d_inputs` naming each with its reason (`tools/run_thesis_once.py::STAGE_B_ABSENCES`, `assemble.declared_absences`). ~~OPEN — Victor.~~ ⓐ declare `J-09` v1 verbatim and let the bundle say what is absent (consensus forward estimates, implied margin/duration, multiples as named gaps — `J-09` already routes unexplained gaps to the data gaps) · ⓑ write `J-09` v2 naming exactly what D-02 supplies (implied stage-1 growth, band, trail) and consensus as Class-A rating/target actions only · ⓒ move the first thesis to a CURRENT `as_of` (new 10-Q fixture; consensus snapshot capturable today, but Stage A and every golden case sit on the 2025-06-26 bundle). ★ Recommend ⓐ for the first thesis — the block's own item 3 handles gaps, and it measures what is missing before building it | ★ `DX-85`'s shape caught before spending: a block declared against evidence nobody supplies |
| **DX-110** | 2026-09-14 | two declarations of `J-11 v1` · the old WF-1 path | `RA-13`: the text in code is the spec's, verbatim; one name, one contract | ⚠ Found declaring Stages B–D: `src/fundamental/prompts/blocks/j_blocks.py` (the 2026-08 WF-1 path used by `thesis/run.py::author_once` and `test_fundamental_probe.py`) declares **`J-11 v1` with a DIFFERENT text** (*"State the strongest case that this investment is a mistake…"*, 3 lines) from the design doc's `J-11 v1` (now in `e_blocks.py`), and runs **J-11 and J-15 on the BLIND view** while the doc puts Stage C and D on `view:full`. Its `J-15`/`J-16` texts match the doc | `src/fundamental/prompts/blocks/j_blocks.py` · `src/fundamental/thesis/run.py` | ⚠ medium (two contracts wearing one name; nothing runs the old path live today) | ✅ **CLOSED 2026-09-15 — ⓐ (Victor: "do step 4").** `prompts/blocks/j_blocks.py` now takes `J-11`/`J-15`/`J-16` from `e_blocks.py` (one text per name+version; `J-16` keeps its RA-17 options); `thesis/run.py::author_once` sends J-11 and J-15 the FULL bundle (Stage C/D per `STAGE_VIEW`); the Stage-A freeze is still over `bundle.redact()`. ⚠ **This changes the orchestrated `thesis` job** (`graph.py` → `author_for` → `author_once`): J-11 now reads the price. Probe tests re-pointed with the reason; 2 mutations caught. ~~OPEN — Victor.~~ ⓐ retire the old path onto `e_blocks.py` + `tools/run_thesis_once.py` (its tests re-pointed) · ⓑ rename the old block (`J-11-legacy`) so the name stops colliding · ⓒ leave it (✗ a recording under `J-11 v1` would be ambiguous). ★ Recommend ⓐ | ★ Left untouched in this change on purpose: its tests pin inherited behaviour (`P4`) |
| **DX-111** | 2026-09-14 | `S-8` never composed in Stage A | §4.0: *"Composed into every J-block: S-1…S-6, plus S-7 in Stage A and S-8 in fresh authoring"* | Stage A IS fresh authoring (WF-1), yet `run_judgement_once.py` composes `stage_a=True` only — every recorded Stage-A call (and every golden thesis case) went out WITHOUT `S-8` (*"You have not analysed this company before…"*). Stages B–D compose it (`call_prompt(..., fresh=True)`, tested) | `tools/run_judgement_once.py::main` (`compose_prompt(blk, stage_a=...)`) | ⚠ low (S-8 guards against a prior verdict no Stage-A bundle carries) | ✅ **CLOSED 2026-09-15 — ⓐ.** `run_judgement_once` composes `S-8` in Stage A (`fresh=True`, envelope hash too; test on the payload a dry run builds). The golden set's Stage-A recordings are a DECLARED split in `test_golden_regression.py::DECLARED_ENVELOPES` until the next paid Stage-A re-record (a mutant removing the declaration is caught). ~~OPEN — Victor.~~ Adding it changes the envelope hash of every future Stage-A call (`DX-76`), so recordings before and after stop being hash-comparable. ⓐ add it at the next paid Stage-A re-record · ⓑ declare §4.0 as meaning Stages B–D only (doc amendment). ★ Recommend ⓐ | ★ `DX-67`'s shape one section over: the composition rule was read for S-7 and not for S-8 |
| **DX-112** | 2026-09-14 | mutation testing a SPEND guard | "Ask approval before every live call"; mutation-test every guard | ⛔ Mutating `if args.live and args.budget_usd is None:` to `if False:` made `test_live_without_an_approved_cap…` run the REAL composition: it built the bundle, froze Stage A and wrote `.state/runs/run-2026-09-15T021127-mu-thesis/commits.jsonl`, then crashed comparing `spent > None` BEFORE any vendor call. **Verified: no `trace.jsonl`, no `ExternalCall` — $0.** A slightly different mutant could have reached the vendor | `tests/structural/test_thesis_runner.py` | ⚠ high (a test of a spend guard could spend when the guard is broken) | ✅ **CLOSED 2026-09-14.** The test now wires `build_base` and `anthropic_transport` to fakes that RAISE, and `REPO` to `tmp_path`; the mutant is caught with nothing built. The stray directory (derived data only, mine) was deleted. ★ Rule: a test of a spend guard patches the vendor to raise | ★ Found by listing `.state/runs` after the mutation run, not by the test output |
| **DX-113** | 2026-09-15 | first live Stage B–D run · tool schema not enforced | `MP-5`: a closed shape is DECLARED; `P5`; `AC-2.12` a trace's close status says what happened | ⛔ `run-2026-09-15T022801-mu-thesis` (approved, $15 cap): **J-09 ✅ $0.87 · J-10 ✅ $0.83 · J-11 ⛔ $0.83** — `stop_reason: tool_use`, output 4,456 tokens but tool input only **981 characters**: `strongest_reason` plus a stray top-level `evidence`, and `load_bearing_assumptions`, `accounts_in_two_years`, `own_falsification_condition`, `missing_evidence` ABSENT. The runner's own `validate` refused it; no thesis (`P5`). **Spent $2.5352.** Two more defects in the same run: (a) the trace closed **`SUCCESS`** although the run failed — `TraceStore.close()` defaults to it and the runner did not pass the status; ⚠ that trace cannot be reopened, so its close record stays wrong and `thesis.json` (`failed`) is authoritative; (b) the cost estimate used 3 chars/token and J-09 billed **139,031** against ≈127,554 estimated (**−9 %**) | `tools/run_thesis_once.py` · `tools/anthropic_transport.py` (passes the tool dict as-is) | ⚠ high ($0.83 lost; any block could have failed the same way) | ✅ **FIXED 2026-09-15 (free), then resumed with approval.** ① `strict_tool`: the SENT schema is `strict: true`, every object `additionalProperties: false`; strict mode rejects complex array bounds, so `minItems`/`maxItems` are removed from the sent copy and carried as the field's DESCRIPTION (*"exactly 3 items"*), while `validate` still enforces them. All 9 schemas accepted by `count_tokens` (free — ⚠ may not compile strict grammars as a real call does). ② `close("FAILED")` on a failed run (test). ③ `CHARS_PER_TOKEN = 2.7`, measured. ④ `--resume-from`: a failed run's commits are carried only if each RE-DERIVES to its recorded commit hash AND its recorded bundle hash reproduces from this run's evidence (tests incl. a genuine commit over different evidence); J-09/J-10 were not re-bought. 6/6 mutations caught after two test gaps were closed (a bundle-tamper case that also broke the commit hash; no assertion that the STRICT schema is what is sent) | ✗ Retrying without strict (same odds of the same failure) · raising the output cap (it did not truncate) · re-running J-09/J-10 ($1.70 for answers already committed). ★ Same lesson as `DX-68`: *"it parsed" is not "it is complete"* — the validation caught it before a thesis was built on it |
| **DX-114** | 2026-09-15 | `J-13` thinking runaway · resume pinning | `GW-23`; `GW-9c` (thinking stays on); `RA-108` | ⛔ Resumed run `run-2026-09-15T025134-mu-thesis` (approved, $12.46 cap): **J-11 ✅ $0.85 · J-12 ✅ $0.82 · J-13 `return_on_equity` ⛔ $1.12** — `max_tokens` at 16,000 with `stream_chars` **tool_input 0**: the whole budget went to hidden thinking, the `DX-96` shape on a judgement block. The strict schema (`DX-113`) worked for J-11 and J-12. Trace closed **FAILED** (the `DX-113` fix, confirmed live). **Spent $2.7888; $5.33 across both runs.** ⚠ Preparing the next resume found a second defect: carrying commits from a run that had itself CARRIED them re-pinned J-09/J-10 to the carrying run, so their bundle hashes did not reproduce — **refused by the bundle check before any spend** | `tools/run_thesis_once.py::BLOCK_OUTPUT`, `::carry_forward` | ⚠ medium | ✅ **FIXED (free), resumed with approval ($9.67 cap, keeping the $15 total).** `J-13` alone: `effort: medium` (bounds thinking; thinking stays on) and a 32,000 cap, used by the cost ceiling too; live-loop test asserts J-13's settings and every other block's defaults (a mutant emptying `BLOCK_OUTPUT` is caught). Carried commits pin to the PRODUCING run (`carried_from`), tested with a resume of a resume | ✗ Raising the cap alone (`DX-96`: buys thinking, not headroom) · `effort: low` first (J-13 is the adversarial forensic block — the quality cost is highest there) · dropping J-13's standing metric set (a departure from the doc's binding note) |
| **DX-115** | 2026-09-15 | `J-14` thinking runaway | `GW-23`; `GW-9c` | ⛔ Second resume `run-2026-09-15T034909-mu-thesis` (approved, $9.67 cap): **J-13 ×5 ✅ with DX-114's settings** ($1.10 · $1.03 · $1.20 · $0.98 · $1.06; outputs 15,105 · 12,340 · 19,121 · 10,148 · 13,508 — far above the 7,500 projected), then **J-14 ⛔ $1.37**: `max_tokens` 16,000, `stream_chars` tool_input 0, input **193,358** (174k estimated — J-13's long outputs are visible to J-14). No thesis. **Spent $6.7289; $12.06 across three runs** (within the $15 total) | `tools/run_thesis_once.py::BLOCK_OUTPUT` | ⚠ medium ($1.37; the remaining four blocks share the cause) | ✅ **CLOSED 2026-09-15 — ⓐ, then resumed (approved, $7.50 cap): J-14 ✅ $1.45 (19,515 out) · J-15 ✅ $1.17 · J-16 ✅ $1.09 · J-17 ✅ $1.16 — $4.87, the first thesis.** `BLOCK_OUTPUT` covers J-13…J-17; `PROJECTED_OUT_TOKENS` 12k (J-14's estimate then matched its measured input, 193,415 vs 193,358). ~~OPEN — free fix, then a paid resume.~~ ⓐ `effort: medium` + 32k for J-14…J-17 (the setting that made J-13 5/5) · ⓑ J-14 only (✗ J-15…J-17 read MORE context than J-14 did) · and raise the output projection to the measured ~14k. ★ Recommend ⓐ | ★ The lesson is in §2.1h: a fix for a GENERAL cause should have been applied to every block sharing it after J-13 |
| **DX-116** | 2026-09-15 | `F10` `D6` capex — raised BY the analysis | `F10` `D6`: `OCF + interest × (1 − t) − capex − SBC`, capex = `PaymentsToAcquirePropertyPlantAndEquipment` | ★ Two findings from the model's own committed outputs, pointing in OPPOSITE directions: (1) **J-09**: D6 charges GROSS capex and does not credit government-incentive proceeds — the 10-Q guides capex *"net of proceeds from government incentives"* and shows *"Proceeds from government incentives \| 1,294 \| 267"* (9M FY25 vs FY24) ⇒ base FCFF understated; (2) **J-11**: equipment financed by **finance leases enters the asset base without passing through the capex line** ⇒ base FCFF overstated vs true capital intensity (MU tags `RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability`, and finance-lease principal is in financing cash flow). Neither was checked against the numbers yet | `src/feature_engineer/valuation/basis.py::_d6` · `F10` `D6` | ⚠ medium (moves `fv_model`; the 28.3 % implied growth rests on it) | ✅ **CLOSED 2026-09-16 — attempted and half-solved (`F10` `D9`, AC-F10.21).** ⓐ **`J-11`'s half needs NO change**: `D8` already counts finance leases as debt ($3,107M at 2025-05-29), so charging the $1,394M of lease-funded additions to capex too would count the same equipment TWICE — `J-14` reached this independently. ⓑ **`J-09`'s half is UNSOLVABLE from D-07**: a namespace-wide scan of MU's `companyfacts` finds NO tagged incentive-PROCEEDS fact (the only hit is share-based plans; `GovernmentAssistance*` carries balances). ⇒ every result now DECLARES it in `known_limits` (`PG-10`), material because 9M incentives alone (~$1,294M) would roughly double the $1,349M base. ~~MEASURED 2026-09-15 (free), decision OPEN — Victor.~~ On MU's facts, trailing year to 2025-05-29: capex **$13,319M** (FY24 8,386 − 9M FY24 5,266 + 9M FY25 10,199); finance-lease ROU additions **$1,394M** (`RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability`: 905 − 758 + 1,247) — tagged; government-incentive proceeds **$1,294M for 9M FY25** (10-Q line 480) — ⚠ **NOT an EDGAR fact** (companyfacts carries only `GovernmentAssistance*` balances), so no trailing-year figure is computable from D-07. ⇒ Against today's base **$1,349M**: charging ROU additions → ≈ **−$45M**; crediting incentives (≥ $1,294M on 9M alone) → ≈ **$2.6B+**; both → ≈ **$1.2–1.4B**, near today's. ★ The two roughly cancel for MU; applying only the taggable one would bias the base DOWN by the whole amount. ★ Recommend: ⓒ declare both on every result now (`known_limits`), and adopt ⓐ only once an extraction item supplies incentive proceeds (an E-07 `ca.` item). ~~OPEN — Victor.~~ ⓐ capex net of incentive proceeds AND plus finance-lease ROU additions (`D6` v3, two new ingest tags) · ⓑ one of the two · ⓒ leave `D6` and record both as known limits on every result (`PG-10`). ★ Recommend: measure both amounts on MU's recorded facts first (free), then decide | ★ The first time this system's ANALYSIS found a defect in its own ARITHMETIC — exactly the loop `C3` exists for |
| **DX-117** | 2026-09-15 | the industry evidence part (`J-03`, `J-08` supply, `E-13`) — assessed | `RA-98`…`RA-102`: a sector file ingests EVERY item of a versioned source list; omissions logged | ★ Assessed, not built: the MACHINERY exists — bundle kind `sector_file` (pinned by industry, schema, file version), `src/fundamental/sector/` (`SourceList` → `ingest(poll)` → `SectorFile` with capacity-announcement `records` {date, kind, subject, status, source_id, url, quote} and first-class `omissions`, schema fingerprinted, a no-conclusion-fields guard). ⚠ What does NOT exist: (1) a **memory-industry source list** (which competitor filings / releases / trade sources, versioned) and (2) a **poller** that fetches them point-in-time to the bundle's as-of. ★ The source list is a domain decision — `no_domain_content_until_decided` — so it was NOT drafted from model knowledge | `src/fundamental/sector/**` · `bundle/assemble.py::sector_file` | ⚠ medium (J-03 and the moat dimension stay unscoreable; J-08 supply stays `insufficient_evidence`) | ◐ **BUILT 2026-09-15 (free); E-13/J-03/J-08 re-runs approved.** Source list `config/sector/memory_v1.yaml` (`memory.v1`): **sndk-edgar** (EDGAR CIK 0002023554 — also the declared reporter for the Flash Ventures JV fabs) · **skhynix-ir** · **samsung-ir**, each exclusion carrying its reason. `tools/ingest_sector_file.py` visits every source, omits with a reason, and enforces `INV-1` per document; `run_extraction_once --sector` renders the file as ONE pinned `sector_file` part. Documents fetched 2026-09-15 (Victor authorised): Sandisk 10-Q filed 2025-05-12 (175,335 chars), SK hynix 1Q25 release 2025-04-24 (6,253), Samsung 1Q25 IR deck 2025-04-30 (23,703) — provenance in `.meta.json` sidecars with a content hash. 15 tests, 4/4 mutations. **PEER SET DECIDED 2026-09-15 (Victor): Samsung · SK hynix · Sandisk** — *"due to relative size and similar product lines"*. ⚠ YMTC/CXMT excluded by that criterion; if they are ever added it is a source-list VERSION bump, not an edit (`RA-98`). ⬜ Still open: the per-peer source entries and how non-EDGAR documents are fetched. Then: a poller per source type (free for EDGAR filers — Sandisk; paid or manual for foreign filers), E-13 re-run over the sector file (paid), J-03 / J-08 re-run (paid) | ★ Building a poller before the list would be architecture sourced from nowhere |
| **DX-118** | 2026-09-15 | verdicts on incomplete evidence — the `INSUFFICIENT_DATA` question | `INV-012` (<0.3 ⇒ decline) · `INV-013` (<0.5 ⇒ capped at HOLD) · `RA-67` confidence := evidence coverage · `RA-38` never self-reported · `PG-10` | ★ MU's SELL was governed by considerations resting on DECLARED-absent inputs, and nothing on the artifact said how thin the evidence was: `thesis.confidence` was the `UNMEASURED` placeholder (`AB-1`) and conviction was the model's own word | `src/fundamental/thesis/derate.py` (new) · `tools/run_thesis_once.py::build_thesis` · `scorecard/coverage.py` (reused, not copied) | ⚠ medium | ✅ **CLOSED 2026-09-15 — Victor: NO hard cap.** *"There is no concrete evidence for any investment decision; the analyst proceeds with known limitation and risk."* The coverage ladder is wired instead: floors may only make a verdict MORE conservative (`P3`), a cap is a MEET so it cannot block an exit, and a governing absence caps CONVICTION at Low with each absence named. Measured on MU: coverage 0.583, verdict SELL unchanged, conviction Medium → Low. 12 tests, 5/5 mutations | ✗ Hard cap (an off switch given today's coverage; starves `RM-1`/`RM-13`/`F5`; contradicts `PG-10`) · ✗ asking `J-16` for the list in its schema (a new way for a paid call to fail — `DX-113`) · ⬜ a `J-16` v2 that states the rule in prose stays available at ≈$1.10/run |
| **DX-119** | 2026-09-15 | the subject guard over an INDUSTRY bundle | `DX-97`: an item about another company may not name the registrant, read off the filing's cover page | ★ The guard reads the SUBJECT from the bundle's own filing cover page. That is right over Micron's 10-Q and **wrong over an industry bundle**: the documents are the competitors' own, there is no cover page for Micron, and the issuer of a document is a legitimate competitor. As written the guard would have refused the industry run outright | `src/fundamental/filings/subject.py::assert_subject_is_not_registrant` · `filings/extract.py::run_extraction` · `tools/run_extraction_once.py` | ⚠ medium | ✅ **CLOSED 2026-09-15.** The company that may not appear as its own competitor is the one being ANALYSED; a caller may DECLARE it (`subject=`), and a bundle with neither a cover page nor a declared subject still REFUSES (`P5`). `SUBJECT_NAMES` declares one per ticker and the run PRINTS it. 6 tests; a mutant dropping the declaration is caught (it survived the first pass — nothing asserted the runner passed it) | ✗ Inferring the subject from the bundle's ticker inside the guard (the guess that produced `DX-97`) |
| **DX-120** | 2026-09-15 | a fetched page's own AI SUMMARY inside evidence | `RA-1`/`RA-19`: the bundle is evidence, assembled mechanically; `X-01` verifies a quote against the bundle | ⛔ `news.skhynix.com` ships an **"AI Summary"** block above the release — the SITE's generated text, not the company's words. Ingested whole it would sit inside the sector file, and `X-01` would verify a quote taken from it: a model could cite a machine summary as SK hynix's own statement. ★ `DX-102`'s failure with a different author, caught on the FIRST fetch this time | `tests_src/fixtures/industry/skhynix-ir/*` · `tools/ingest_sector_file.py` | ⚠ medium | ✅ **CLOSED 2026-09-15.** The block is stripped at fetch, the strip is RECORDED in the document's `.meta.json` (`removed: [...]`), and a test asserts both. ⚠ Generalisation NOT built: the strip is per-source and hand-written, so the next IR site's chrome needs the same treatment — a fetch that finds unknown furniture should be reviewed, not trusted | ★ The lesson generalises: **any fetched page may carry a machine's words beside the company's**, and a converter cannot tell them apart |
| **DX-121** | 2026-09-15 | an industry quote had nothing to cite | `X-01` ①: the quote must resolve in the bundle; `RA-6`/`RA-131` | ⛔ The first live industry `E-13` (`run-2026-09-15T220611-mu-e13`, **$0.5196**, 75,952 in / 5,594 out) returned items and then FAILED verification: `parse_items` stamps every item with the module's `ACCESSION` — **Micron's** — and `Span.resolve` searched `filing` parts only, so a perfectly good quote from Sandisk's 10-Q inside the sector file resolved against nothing. ★ The call was fine; the citation contract had no id for this part kind | `tools/run_extraction_once.py::parse_items` · `src/fundamental/claims/models.py::Span.resolve` | ⚠ medium ($0.52 lost) | ✅ **CLOSED 2026-09-15.** A `sector_file` part is citable: the id is DERIVED from its pins (`sector:<industry>:v<file_version>`, no pin-contract change), `Span.resolve` searches those parts too, and the sector run stamps that id. A test verifies a real SK hynix quote end to end and asserts Micron's accession still does NOT resolve there; 2/2 mutations | ★★ **The lesson, and it is mine:** the dry run does not verify, so the whole `--sector` path had been exercised without ever running `x01_verify_extraction` once. ⚠ An end-to-end test with a synthetic item costs nothing and would have caught it before the call. ⚠ Also caught by X-01 while writing that test: my first synthetic item's VALUE was not inside its own quote (`X-01` ②, working) |
| **DX-122** | 2026-09-16 | `X-01` ② vs a value the document cannot contain | `X-01` ②: the extracted value must appear in its cited span (`RA-6`, `RA-132`) | ⛔ The second industry `E-13` (`run-2026-09-16T070237-mu-e13`, **$0.50**, 15 items) aborted on `cx.status = "under construction"` cited against *"Gross profit decreased $81 million…"*. ★ `E-13` ASKS for a status from a closed set — it is a LABEL the reader assigns, and a filing essentially never contains the phrase, so the item is unsatisfiable under ② by construction. ⚠ MU's earlier `E-13` never exposed this: it died on the subject guard first (`DX-97`) | `src/fundamental/claims/classification.py` (new) · `claims/verify.py::x01_verify_extraction` | ⚠ medium ($0.50 lost; two of the block's six items affected) | ✅ **CLOSED 2026-09-16.** Only ② is relaxed, only for an item DECLARED with its closed set (`cx.status`), and the value must be in that set; ① (the quote resolves, verbatim) is never relaxed. A drift test asserts every declared value appears in `E-13`'s own prompt text. **Validated OFFLINE by replaying the failed run's recorded response** — 10 items verify, 3 `not_found` — so the third call was the only one paid for after the fix. 4 tests, 3/3 mutations | ⚠⚠ **The gap this leaves, stated:** nothing checks that the cited span is the RIGHT span for the label — the failing item cited an unrelated sentence and would now PASS. ⬜ That belongs to an `E-13 v2` (*"quote the sentence the status is read from"*), Victor's, at a re-record. ✗ Dropping `cx.status` (the moat rubric's level 4 needs a capacity status) · ✗ exempting every item (a hole, not a rule) |
| **DX-123** | 2026-09-16 | re-verifying a COMPLETE call after the verifier was fixed | `P5`: a failed run is not evidence; `GW-23`: a truncated response is a failure | ⛔ Three paid industry `E-13` attempts, **$1.88 total**: #1 `DX-121` (no citable id), #2 `DX-122` (`X-01` ② on a classification), #3 TRUNCATED at 20,000 (`DX-96`'s thinking runaway — ⚠⚠ **my repeat of `DX-115`'s own lesson**: the runner has `--effort` and I did not pass it on a 205k-char bundle). ★ Attempts #1 and #2 COMPLETED (`stop_reason: tool_use`); only our verifier refused them | `tools/reverify_recording.py` (new) | ⚠ high (a rule about what counts as evidence) | ✅ **CLOSED 2026-09-16 — Victor: replay, $0.** The model's answer is unchanged; the verifier was wrong, so paying again buys a status line. The replay is guarded four ways: ① the recorded call must have completed (a truncated run REFUSES — checked on attempt #3), ② exactly one extraction call, ③ `X-01` ① ② and the subject guard must pass NOW, ④ the new run records `replayed_from`, `replayed_because` and the original status, with `cost_usd: 0`. Result: **10 items verified** — Kioxia's Kitakami K1/Y7/K2 via Sandisk, Samsung's HBM3E 12H ramp, SK hynix's conditional supply | ⚠ **Not a general licence.** A replay is legitimate only when OUR code was the defect; a model that answered badly must be re-asked. ✗ Paying $0.50 for the same answer · ✗ relaxing the SUCCESS rule in `load_extraction_parts` (the guard belongs at the replay, where the reason can be recorded) |
| **DX-124** | 2026-09-16 | a judgement bundle loading INDUSTRY extraction evidence | `RA-2`: two runs with the same `bundle_hash` are comparable; `DX-95` records it | ⛔ `load_extraction_parts` re-verifies every recorded run against MICRON's filing. An industry `E-13`'s quotes are in the peer documents, so `J-03` refused to load it — *"quoted text is not in the bundle"* — and the moat dimension stayed unscoreable for a wiring reason | `tools/run_judgement_once.py::load_extraction_parts` | ⚠ medium | ✅ **CLOSED 2026-09-16 (free).** Each recorded run is re-verified against **the bundle it actually read**, chosen by the `bundle_hash` `DX-95` put in the trace (a run predating `DX-95` falls back to the filing, which is the only bundle it could have read; a hash matching NEITHER source refuses). The re-parse stamps the right citation per source, and the subject is declared when the source is the sector file. ⚠ The peer DOCUMENTS stay out of the judgement bundle — the verified items enter at a fraction of the tokens (242k chars vs 380k) | ★ `DX-95` was recorded as *"no trace record said which bundle a call read"*; this is the first time that field did real work |
| **DX-125** | 2026-09-16 | `RM-13` — the falsifier checker | `RM-13`: the ratio of theses that died by their own stated condition to those quietly abandoned; `RA-35` | ★ The MU thesis's falsifiers were resolved BY HAND on 2026-09-15 (two had fired). Nothing in code gathered the evidence, so `RM-13` had no instrument and the check could not run on the next filing | `src/fundamental/monitor/falsifier_check.py` · `tools/check_falsifiers.py` (new) | ⚠ medium | ✅ **BUILT 2026-09-16 (free).** Deterministic gathering: every reported period of each falsifier's `observable_field` published after the thesis and knowable at the check date, with the deadline state. ⚠⚠ **The READING is not claimed**: a condition is prose (*"positive in each of four quarters, summing to more than $5bn"*), and parsing a threshold out of it is the plausible default `P5` forbids — so the status is `DECIDABLE_BY_READER`, never a manufactured `FIRED`. On MU: #1 #2 #3 decidable (4 periods each), #4 `NO_DATA`. 8 tests, 5/5 mutations (one survivor closed: a `pd.NA` case) | ⬜ **Automatic firing needs a STRUCTURED condition** — a `J-15` version carrying `{field, comparator, threshold, window}` beside the sentence. Victor's, at the next prompt bump. ✗ Parsing the prose (a threshold guessed from a sentence is a number nobody stated) |
| **DX-126** | 2026-09-16 | a falsifier on a tag the filer abandoned | `RA-35`: *"a falsifier naming a field this system does not receive is not checkable, however precise it sounds"* | ⛔ Found by the new checker on the FIRST run: falsifier #4 names `LongTermDebtNoncurrent`, which **Micron last filed in 2013** — it reports the lease-inclusive tag instead. The observable list offered it because a COLUMN exists for every canonical item and old rows carry values, so `J-15` wrote a condition that can never resolve, and its silence looks exactly like a condition holding | `src/fundamental/bundle/for_ticker.py::observable_fields` | ⚠ medium (an unfalsifiable falsifier inside a thesis that passed every check) | ✅ **CLOSED 2026-09-16 (free).** The list offers a tag only if it is non-null in the **latest 4 reported periods** — a claim about future filings needs a tag still in use. MU: 31 → 25 observables; `LongTermDebtNoncurrent`, `LongTermDebtCurrent` and `InterestExpense` drop out, the lease-inclusive tags stay. ⚠ The empty-list refusal (`RA-145`) still holds. 2 tests, mutation caught | ★ `RA-35`'s rule one layer down: the system RECEIVES the field, and the COMPANY stopped sending it |
| **DX-127** | 2026-09-16 | prompt caching for Stages B–D | `shared/prompt-caching`: caching is a PREFIX match, and any byte before the breakpoint invalidates it | ★ All 13 Stage B–D calls re-send the same ~140k-token base bundle; only the commits a call may read and its own instructions vary. Measured: **$17.57 → $11.38** expected for one thesis | `tools/anthropic_transport.py` · `tools/run_thesis_once.py::call_payload` | — (a saving, not a defect) | ✅ **BUILT 2026-09-16 (free), NOT yet run live.** The base evidence is its own content block with `cache_control: ephemeral`; the variable half follows. ⚠⚠ **The model now reads evidence → frozen commits → instructions**, where it read instructions → evidence before: a deliberate ORDER change, and `--no-cache` reproduces the old single-block shape exactly so a regression can be bisected. `cache_read`/`cache_write` are recorded on every result — a silent invalidator shows up as a read of 0 and nowhere else. 3 tests (all 13 prefixes byte-identical; the breakpoint is on the stable block), 4/4 mutations | ⬜ Unvalidated against the vendor: the saving is arithmetic until a live run reports a non-zero `cache_read` |
| **DX-128** | 2026-09-16 | `RM-13` decided without a paid `J-15` re-run | `RM-13`; `DX-125` left firing undecidable because a condition is prose | ★ Victor: *"no paid run, too expensive, find a way to bypass this."* The blocker was that deciding a falsifier needs a threshold, a comparator and a window, and `J-15` emits a sentence | `src/fundamental/monitor/falsifier_check.py::evaluate_test` · `config/falsifiers/mu-2025-06-26.json` · `tools/check_falsifiers.py --tests` | — (a bypass, not a defect) | ✅ **BYPASSED 2026-09-16, free.** The structured test is written BESIDE the prose by hand, in a small declared grammar (`each` · `any` · `consecutive` · `sum` · `rises_each`, conditions ANDed within one period). On MU it reproduces the hand analysis exactly: **#1 #2 FIRED · #3 #4 HELD**. ⚠ Each translation is a READING and the file states its own gaps — #4 substitutes the tag Micron actually files (`DX-126`), #3 de-rates rather than falsifies (`J-16` item 3) and the grammar cannot say so. 12 tests, 9/9 mutations (two survivors closed: a failing `rises_each` and a failing `sum` were never exercised) | ⬜ A `J-15` v2 emitting the test itself is now an OPTIMISATION, not a blocker. ✗ Parsing the prose · ✗ paying ~$11.38 to re-author for a number that is arithmetic ✏ **REVIEWED 2026-10-01 by Victor:** #1 approved · #2 approved, gap accepted (the first new quarter is not compared with the thesis quarter; result unaffected) · #3 approved **as a falsifier, not a de-rate trigger** · #4 tag substitution accepted (`LongTermDebtAndCapitalLeaseObligations` for the unfiled `LongTermDebtNoncurrent`). Result unchanged: **#1 #2 FIRED · #3 #4 HELD**. ★ These four are now the reference J-15 v2's model-written tests are compared against |
| **DX-129** | 2026-09-17 | ✅ `E-09` — the block that never completed | `GW-23`; `DX-96` skipped it after five truncations; `DX-115` named the lever | ★★★ **`E-09` COMPLETED at `--effort low`, first time ever**: `run-2026-09-17T071619-mu-e09`, **9 items verified, 1,639 output tokens, $0.4171, 27 s**. Against its history: five truncations at 20,000 output tokens, `tool_input 0`, ~$4.40 sunk (`DX-96`). ⚠ The lever had been identified for J-13/J-14 (`DX-114`/`DX-115`) and applied to the JUDGEMENT path only — the extraction runner has carried `--effort` since `DX-96` and nobody pointed it at `E-09` again | `tools/run_extraction_once.py --block E-09 --effort low` | ★ high value | ✅ **CLOSED 2026-09-17.** It supplies `searched:ap.change` — the last missing marker — with `ap.change` FOUND twice (*"Certain reclassifications have been made…"*, the segment reorganisation) and six items honestly `not_found` with their notes. **Scorecard coverage 0.917 → 1.000** (all four dimensions fully evidenced); the run is now in `DEFAULT_EXTRACTIONS`. ⬜ `J-04` (earnings quality) has never produced a VALID score — its only answer is the pre-`DX-100` void one — and can now be scored for ≈$0.90 | ★★ **The lesson, twice learned and now recorded twice:** a fix for a GENERAL cause (thinking runaway) must be applied to EVERY block sharing the cause, not only the one being worked on. `DX-115` said it; `E-09` sat skipped for four days anyway |
| **DX-139** | 2026-10-01 | ⚠⚠ The falsifier checker decided a window that had not finished reporting | `RM-13`; `DX-128` grammar | ★ Found by the first live `J-15 v2` call. Falsifier #3 asked for operating income above $1bn in EACH of the next EIGHT quarters; only four had been reported, and `evaluate_test` said **FIRED** "over 4 reported period(s)". It sliced the window to what existed and decided as if complete. ⚠ It could equally have said HELD too early on an `any` clause (an existing test asserted exactly that, with 2 of 4 periods) | `src/fundamental/monitor/falsifier_check.py::evaluate_test` | ★ high: this is the primary judgement instrument (`L8` §9) | ✅ **CLOSED 2026-10-01, $0.** New status **`PENDING`**. A partial window is decided only where the answer is already final: one failing period settles `each`/`rises_each` (HELD), one satisfying period or run settles `any`/`consecutive` (FIRED), and a `sum` always waits. A HELD clause settles the whole test, since every clause must hold to fire. 10 new tests (`tests/unit/test_falsifier_partial_window.py`); one inherited test re-windowed so it still tests the same-period AND. Victor's 4 MU tests decide unchanged | ★★ **A checker that reads "all observed so far" as "all" is the k=1 defect again** (`RA-154`): absence of contrary evidence counted as evidence. ⇒ Every instrument that decides over a window must know how much of the window it has |
| **DX-140** | 2026-10-01 | ⚠ A DECLARED known limit makes the `J-09` cap permanent | `DX-118` cap; F10 `D9` (`known_limits`); `RA-67` | ★ Found by the `J-09` re-run with consensus and the duration table supplied (§2.1p item 5). `derate._absences` flags *"a price requirement could not be set against Stage A"* when ANY `price_requirements` row is `insufficient_evidence`. The new answer still has two: the gross-capex base (F10 `D9` declares incentive proceeds UNCOMPUTABLE from D-07) and implied margin (an F10 non-goal). ⇒ For MU the first fires on every thesis whatever data is added — a cap no input can lift | `src/fundamental/thesis/derate.py::_absences`; `run-2026-10-01T225847-mu-thesis` | ◐ medium | ✅ **CLOSED 2026-10-02 — Victor chose ⓑ.** `derate._rests_on_known_limit` (the row cites `known_limits` or quotes a declared limit's opening words) excludes such a row from the J-09 absence; `stated_limitations` puts it on the thesis as `confidence.limitations_stated` (`PG-10`). A curable `insufficient_evidence` row beside it (implied margin) STILL caps. 4 tests in `tests/unit/test_thesis_derate.py`. ⚠ Was: ⓐ keep: a declared limit IS missing evidence, so the cap is honest; ⓑ distinguish: a requirement insufficient only because of a DECLARED known limit is stated on the thesis (`PG-10`) but does not count as a governing absence; ⓒ supply it: an `E-07` incentive-proceeds item per filing (prompt + re-record) | ★ A cap meant to say *"get the missing input"* becomes a constant when the input is one the system has already declared it cannot get. ⇒ An absence rule must know whether the absence is curable |
| **DX-141** | 2026-10-02 | A quote that drops a footnote marker | `rule_checks` quote-not-in-source; `DX-138` precedent | ★ `J-11` (`run-2026-10-02T113055`) quoted *"Construction in progress \| 4,937 \| 3,444"*; the 10-Q reads *"Construction in progress(2)"* (line 606), and the same answer quotes it verbatim elsewhere. Letters-and-digits comparison makes the `2` significant | recorded payload `judge:C:J-11:llm:1` | ◐ low | ⬜ **OPEN — kept as a violation, not loosened.** A footnote marker cannot be told from a real digit by rule, so the checker stays strict. ⚠ `rule_checks.KNOWN` covers promoted recordings only; unpromoted `.state` runs are reported in `L3`, not registered | ★ Content-faithful is not verbatim; a checker that forgives one class of digit forgives them all |
| **DX-142** | 2026-10-03 | An inherited cadence test was a time bomb | `ST-8`-like silent decay; D-07 observation ledger | ★ `tests_src/test_data_engine_observations.py::test_a_capture_past_the_cadence_writes_again` captured with the ledger's WALL-CLOCK `observed_at` and then asked for a fixed `as_of` of 2026-11-01, expecting the 30-day cadence to have passed. It stopped being true at 2026-10-03 00:00 UTC (29 days) and the suite went red with no code change | `tests_src/test_data_engine_observations.py` | ◐ low | ✅ **CLOSED 2026-10-03** — the later `as_of` is now `date.today() + 31 days`; the code (wall-clock `observed_at`, by design) is unchanged | ★ A fixed date compared with the wall clock passes until the day it doesn't. ⇒ A test that touches `utcnow` must pin the clock or be relative to it |
| **DX-143** | 2026-10-02 | The memory reference class is thinner than its members | `F11` `AC-F11.3` (excluded and named, never zero); `F10` `D6` | ★ On the promoted fixtures, as of 2025-06-26: **MU 9 usable years** (FY2016–2024) — FY2009–2015 are excluded for *missing revenue* because Micron tagged revenue `SalesRevenueNet` before ASC 606, and `CANONICAL["revenue"]` lists only the newer tags; **pre-2016 SanDisk 0 usable years** — it files no total pretax income (only `…BeforeIncomeTaxesDomestic` + `…Foreign`) and no interest-expense tag (only `InterestPaid`, a cash concept); **2025 Sandisk 0** (first 10-K after the as-of — correct); **WDC 8** (FY2017–2025, `D3`). ⇒ 17 member-years, 8 without the subject | `src/feature_engineer/fundamental/items.py::CANONICAL`; `tests_src/fixtures/edgar/reference_class/memory_v1/` | ★ medium — it decides whether the class is a class | ✅ **CLOSED 2026-10-02 (Victor): ⓐ ADDED, ⓑ exclusion ACCEPTED.** `SalesRevenueNet` third in `CANONICAL["revenue"]`, `fundamental` → v5; members re-ingested (MU +175 rows) and fixtures re-promoted ⇒ **MU 13 usable years (FY2009–2024 less FY2010 tax, FY2013–14 OCF), class 21 member-years**; pre-2016 SanDisk stays excluded and named. ⚠ **Side effect, stated:** MU's annual history in the blind bundle now starts FY2009, so the frozen Stage A commit moved (`sha256:9a11054d…` → `cde6c902…`) — the Stage A ANSWERS (J-20's FY2016–FY2024 window among them) were made over the shorter history and are not re-asked. Was: ⓐ `SalesRevenueNet` as a third revenue fallback (same concept, pre-ASC 606; +7 MU years; `fundamental` → v5); ⓑ SanDisk: pretax = domestic + foreign (a sum the filing itself presents), interest from `InterestPaid` (a cash figure standing in for an expense — changes `D6`'s meaning), or accept its exclusion | ★ A reference class is only as wide as the tags that resolve it; the exclusions are named on every rendered part, so the thinness is visible rather than silent |
| **DX-144** | 2026-10-03 | ⚠⚠ A falsifier test decides a CONSECUTIVE condition on the FIRST window | `RM-13`; `DX-139` (partial windows); J-15 v2 grammar | ★ The third MU thesis's falsifiers say *"in each of four consecutive reported quarters"* with 2027 deadlines; the model wrote structured tests with mode `each` over a 4-quarter window instead of the grammar's `consecutive`. `evaluate_test` then decides on the first 4 quarters after the as-of, so a weak first quarter (OCF − capex $0.07bn; GP < COGS) settles #1 and #2 as HELD although three consecutive qualifying quarters already exist and the deadline is a year away. ⚠ The test is valid in the grammar — it just does not say what its sentence says | `run-2026-10-03T125303-mu-thesis/falsifier_tests.json` · `src/fundamental/monitor/falsifier_check.py` | ★ high: it reports a falsified thesis as surviving | ✅ **CLOSED 2026-10-03 — Victor chose ⓐ.** `validate_test(…, as_of, deadline)` refuses a window shorter than the quarters reported by the deadline (`periods_reported_by`: 91-day quarter, 60-day filing lag — the lenient 10-K lag). The runner passes each falsifier's deadline, so such a J-15 answer stops the run before J-16 (`RA-16`). Measured on the recordings: the 2026-10-02 tests all VALID; 2026-10-03 #1 #2 #3 REFUSED, #4 valid. ⚠ The J-15 prompt does not yet state the rule, so the next authoring may stop here (a v3 wording is the cure; not chosen). 2 tests + one runner fixture moved (`2026-03-31` → `2025-12-31`, inside its 1-quarter window). Was: ⓐ `validate_test` refuses an `each` test whose window ends before the falsifier's deadline (forces `consecutive` or a matching window; J-15 must rewrite) · ⓑ the checker evaluates `each` over every N-quarter window up to the deadline (changes the hand-written Sept tests' meaning) · ⓒ J-15 v3 prompt: *"consecutive" means mode consecutive* | ★ Sentence ↔ test fidelity was checked by eye on 2026-10-01 and held then; it failed on the next authoring. ⇒ It needs a check, not a reading |
| **DX-145** | 2026-10-03 | The NAND price-range misquote recurs (`DX-138`, twice more) | `rule_checks` quote-not-in-source | `J-13:return_on_equity` and `J-13:operating_margin` quote the risk factor as *"NAND … ranged from plus low-50% …"*; the 10-Q (line 1501) says *"plus low-30% to a minus low-50% range"*. Same substitution `J-03` made on 2026-09-12 | recorded payloads in `run-2026-10-03T002642` / `T125303` | ◐ medium — a range is reported wider on the upside than the filing states | ✅ **CLOSED 2026-10-03 — Victor chose ⓐ: accepted as CAUGHT.** The rule check flags it on every recurrence; no repair loop. Was: the checker catches it every time; nothing yet makes the model stop. ⓐ accept as caught · ⓑ a re-ask on a quote failure (a repair loop) · ⓒ quote the range verbatim in the bundle's observables | ★ Two adjacent ranges sharing "low-50%" are a reliable trap for paraphrase-from-memory |
| **DX-146** | 2026-10-03 | `J-10`'s cap fires on claims no reference class can answer | `DX-118`, `DX-140` (a cap that cannot be lifted is a constant) | ★ With F11 in the bundle, J-10's price-requirement claims cite base rates; three secondary claims do not — terminal growth in perpetuity, J-07's cycle read, FY2025 capex guidance — and `derate._absences` flags J-10 on ANY claim with `base_rate_in_bundle: false`. ⇒ The cap now rests on claims the verdict did not turn on | `src/fundamental/thesis/derate.py::_absences`; `run-2026-10-03T125303-mu-thesis` | ◐ medium | ✅ **CLOSED 2026-10-03 — Victor chose ⓑ.** `derate._is_price_requirement_claim` matches a claim against the subject's OWN `F10` numbers (a required growth rate at 0/1/2 dp, or a duration period as a span of years); only those cap. The rest go to `limitations_stated` as *"J-10: no base rate for — …"*. Without a v2 trail the stricter rule holds. 6 tests. ★ Re-derated free on the third thesis: **governing absences 0 → conviction Medium-High, the first uncapped MU thesis** — ⚠ but its J-15 tests fail `DX-144` ⓐ, so under today's rules it would not have been issued. Was: ⓐ keep · ⓑ count J-10 only when a PRICE-REQUIREMENT claim (one tied to `implied_by_duration`) lacks a base rate; state the rest on the thesis like `DX-140` · ⓒ require J-10 to mark which claims the verdict rests on (schema change, re-ask) | ★ The same lesson as `DX-140`, one block later: an absence rule must know which absences matter |
| **DX-147** | 2026-10-04 | `validate_test` silently ignores a `consecutive` count on a clause that is not mode `consecutive` | `DX-144`; `DX-128` grammar; house rule *fail loud* | ★ The J-15 re-ask (`run-2026-10-04T024042-mu-thesis`) wrote all four tests as `{"mode": "each", "consecutive": 4, …}`: the model meant *"4 consecutive"* and put the count in the field, but under mode `each` the field is never read. `DX-144` ⓐ refused the run on the WINDOW (4 < ~7 quarters by 2027-07-01), so nothing was issued, but a test whose window happened to reach its deadline would pass with the count silently dropped | `src/fundamental/monitor/falsifier_check.py::validate_test` | ◐ medium — no wrong thesis issued yet; it is the shape of `DX-144` again | ✅ **CLOSED 2026-10-04 — Victor chose ⓐ.** `validate_test` refuses a non-null `consecutive` under any mode but `consecutive` (null stays legal — the strict schema sends every field). 1 test case, mutation caught; the runner test stand-in now fills a nullable field with null (it filled `consecutive` with 1). ★ Measured on the recordings: the 2026-10-03 thesis's 4 tests carry the same stray count — this rule alone would have refused that run too. Was: ⓐ refuse `consecutive` on any mode but `consecutive` (one line + one test; fail loud) · ⓑ leave it (the window rule catches today's case) | ★ The model's intent is legible in the stray field: the grammar, not the model, lost the word *consecutive* |
| **DX-138** | 2026-10-01 | ⚠⚠ Judgement answers put words in the filing's mouth: a quote with a CHANGED NUMBER | `AP-2` cited claims only; `X-01` is literal for extraction and nothing checked judgement quotes | ★ Found by the first run of `tools/rule_checks.py` (`L8` §9 rule 4ⓑ). Of **914 `FACT [...] "…"` quotes** in 45 recorded calls, 254 cite a non-filing source (D-02, frozen answers, declared absences) and are exempt; of the rest, after allowing layout (table rows the filing splits across lines) and `...` abridgement, **2 calls misquote the filing**. ⓐ ⚠⚠ `J-03` (Stage A, 2026-09-12) quotes NAND ASPs as *"ranged from plus low-50%…"*; the filing says **"plus low-30% to a minus low-50%"**. A wrong number inside quotation marks, attributed to the SEC filing. It corrects itself later in the same answer, which is why nobody saw it. ⓑ `J-08` drops one word ("We have **also** signed"), meaning intact | `run-2026-09-12T024848-mu-stage-a` `judge:J-03:llm:1`, `judge:J-08:llm:1` | ★ high (ⓐ) · low (ⓑ) | ◐ **DETECTED, recorded in `rule_checks.KNOWN`, not fixed.** Both recordings are history; the check now fails on any NEW misquote in any recorded call. ⬜ Live prevention: run the rule checks at the end of every `run_*` so a misquote is reported the day it is made | ★★ **This is exactly what golden cases could not see.** `J-03` and `J-08` were both graded (`J-08` signed) and stayed green, because a golden case asserts one field and the misquote sat in the reasoning. ⇒ A rule that holds for every quote in every call finds what a field-level comparison never will |
| **DX-137** | 2026-10-01 | ⚠⚠ The pending golden files repeated their top-level `cases:` key — a loader saw 11 of 29 drafts | `CT-5.2`; the `L8` §5 inventory | ★ Found while refreshing `L8` §5, whose two counts disagreed ("2 unsigned" vs "27 pending"). `extraction.pending.yaml` had **four** top-level `cases:` keys (two empty, then 16 drafts, then 3), and `thesis.pending.yaml` had **two** (2, then 8). ⚠ YAML keeps only the LAST value of a repeated key and says nothing, so `yaml.safe_load` returned **3 and 8**: **18 of 29 drafts invisible to any loader.** Nothing loads these files today, which is the only reason nothing broke | `tests_src/fixtures/golden/{extraction,thesis}.pending.yaml` | ◐ medium | ✅ **CLOSED 2026-10-01, free.** Merged into one list per file (the first thesis section re-indented). ★ Verified **case-for-case identical** against `HEAD`, section by section: 19 + 10. `tests/structural/test_golden_fixtures_have_no_duplicate_keys.py` loads every golden fixture with a duplicate-key-refusing loader, and fails on the `HEAD` versions | ★★ **The true unsigned count is 29**, not 27: `L8` counted the 2026-09-17 drafts and missed the two older `J-20`/`J-09` drafts. ⚠ A format that silently discards data is the `DX-135` shape again: a shorter list reads as a tidier one |
| **DX-136** | 2026-10-01 | ★ Development LLM calls move to the subscription, and **8 tests would have started the real CLI** | `CLAUDE.md` house rule (Victor, 2026-10-01); `L2-shared-infrastructure` §5.7 | ★ Building the `claude_code` transport as the **default** meant every test that monkeypatched `tools.anthropic_transport.anthropic_transport` stopped intercepting anything: the runners now asked for the subscription transport, so **8 tests (4 thesis-runner, 3 judgement-runner, 1 `build_gateway`) would have spawned the real `claude` binary on every `pytest`**, spending subscription usage silently. ⚠ They were caught only because the guard went in first | `tests/conftest.py` · `tests_src/conftest.py` (new `CIA_CLAUDE_BIN` sentinel) · the 8 tests | ◐ medium | ✅ **CLOSED 2026-10-01.** An autouse fixture points `CIA_CLAUDE_BIN` at a path that does not exist, so a stray call raises `TransportError` instead of running. The 8 tests cover the API path and now say so: `CIA_LLM_TRANSPORT=anthropic_api`. Suite back to its single deliberate `J-07` red | ★★ **Changing a default changes what every existing mock intercepts.** A patch on the old factory reads as protection and protects nothing once the default moves. ⇒ Put the guard in BEFORE flipping the default, and let the failures name the tests that relied on the old one |
| **DX-135** | 2026-09-17 | ⚠⚠ An ABSENT item loses the competitor it is about — 5 recorded absences parse down to 3 | `MP-18` identity; `DX-74` (a qualifier the model invents); surfaced closing `DX-132` | ★ The extraction parse blanks `qualifier` on a `not_found` item. On `E-13` the recording holds **five** absences — Kioxia timing, Kioxia conditional, Samsung timing, Samsung conditional, SK hynix capacity — and the parsed view holds **three** anonymous rows (`cx.timing`, `cx.conditional`, `cx.capacity`, each with an empty qualifier). ⇒ *"SK hynix did not disclose capacity"* and *"Samsung did not disclose timing"* become indistinguishable, and **two absences vanish entirely** (15 items → 13). ⚠ The recording is intact; the loss is in the graded view, so it is invisible to anyone reading the trace | `tools/run_extraction_once.py::parse_items` (qualifier blanked when `status == not_found`) · visible in `run-2026-09-16T070237-mu-e13-replay` | ★ high for the industry block | ✅ **CLOSED 2026-10-01 — Victor ruled: an absence KEEPS its qualifier** (`extract.not_found(qualifier=…)`, passed by `parse_items`; identical absences still collapse). Signed cases were **withdrawn, not edited** (`D2`): `seg-assets-not-disclosed` re-pointed to `'all segments'`, and `gd-prior-value-absent` split into `…-capex-absent` + `…-etr-absent`, all three unsigned in `extraction.pending.yaml`, values unchanged. `dm-headroom-absent` re-pointed. ⬜ `E-13 v2` should restrict its qualifier to the peer list, so the model cannot invent one (`DX-74`). ⓘ Originally OPEN — the `DX-74` question in reverse. `DX-74` removed an INVENTED qualifier from a case's identity because the model authored it; here the qualifier is the only thing that says WHICH competitor was silent, and silence-per-competitor is the substance of an industry read. ⇒ No `not_found` cases are drafted for `E-13`. ⚠ Fixing it changes the identity of every existing absence case (`dm.headroom`, `ap.icfr`, `ng.measure`, `ca.capex`) — so it must be decided before those are signed, not after | ★★ **An absence needs a subject.** *"Nothing found"* is a fact about a question asked of a source; strip the source and it degrades to a fact about the question, which is not evidence of anything. ⚠ And the dedup made the loss SILENT — a shorter list looks like a tidier one. ★★★ **MEASURED 2026-09-17, and it is worse than first written: the fix would break TWO of the three SIGNED absence cases.** ⓐ `mu-fy2025q3-seg-assets-not-disclosed` addresses `#seg.assets||:` while the recording carries qualifier `'all segments'` — restore the qualifier and the selector resolves nothing. ⓑ ⚠⚠ `mu-fy2025q3-gd-prior-value-absent` addresses `#gd.prior_value||:` and the recording holds **TWO** absences there, `'capex FY2025'` and `'effective tax rate FY2026'` — so that case is green **only because the collapse merged them**, and restoring the qualifier makes it ambiguous (`_select` raises on several matches). ⇒ A signed, passing golden case is resting on the defect. ⛔ **Not fixed unilaterally: `D2` reserves re-establishing those two to the fund manager.** ✏ **MEASURED 2026-10-01 — the drafted side is smaller than feared.** In the recordings, `ng.measure` `ng.adjustment` and `ap.icfr` carry an EMPTY qualifier, so the fix leaves their identity unchanged. Only `dm.headroom` (`'Actual net leverage ratio as of May 29, 2025'`) re-points. ⇒ **1 drafted + 2 signed** cases move: `seg.assets` → `'all segments'`, and `gd.prior_value` SPLITS into `'capex FY2025'` and `'effective tax rate FY2026'` |
| **DX-133** | 2026-09-17 | ⚠ A promoted run carries its TRUNCATED calls too — `J-12` and `J-13` are ungradeable | `DX-84` (a truncated Stage A is not promoted); `DX-36` (`test_every_recorded_quote_still_resolves_in_its_filing`) | ★ Promotion's unit is the RUN, not the call, so promoting `run-2026-09-15T034909` for its five complete `J-13` metric calls also brought a `judge:C:J-14:llm:1` payload of **0 characters, `stop_reason: max_tokens`** — and the quote-resolution guard, which JSON-parses every payload in every promoted recording, failed immediately on it. ⚠ `run-2026-09-15T025134` is worse: its truncated `J-13:return_on_equity` is **2 characters** (`{}`), which PARSES — so it passed the guard and would have been promoted silently | `tools/promote_recording.py::promote` (whole-directory copy) · `tests/integration/test_golden_regression.py::test_every_recorded_quote_still_resolves_in_its_filing` | ◐ medium | ✅ **HANDLED 2026-09-17 by following `DX-84`'s rule rather than working around it:** both runs were **un-promoted**. ⇒ `J-12` and `J-13` have no clean recording and get no draft cases; they need a re-record (≈$0.80 + ≈$1.06) before they can ever be graded. ⚠ The suite is back to its single deliberate `J-07` red | ★★ The 2-character mutant is the lesson: **"it parsed" is not "it is an answer."** A guard that validates SHAPE passes a truncation that happens to close its braces. ⬜ `promote_recording` should refuse a run containing any `stop_reason: max_tokens` call, by that field rather than by parseability |
| **DX-134** | 2026-09-17 | ⚠ A leaked tool-call fragment is sitting INSIDE a recorded answer (`J-11`) | `GW-9`/tool-use contract; surfaced drafting `L8` L1a cases | ⚠ `run-2026-09-15T022801`'s `judge:C:J-11:llm:1` returns `strongest_reason` beginning `"\n<parameter name=\"reason\">The income statement is an ASP artefact…"` — raw tool-call XML captured as the field's VALUE. The answer is otherwise coherent, which is what makes it dangerous: it reads as a normal record and the malformation is 24 characters at the front | recorded payload `run-2026-09-15T022801-mu-thesis/judge:C:J-11:llm:1` | ◐ medium | ⬜ **OPEN.** `J-11` is excluded from this pass's drafts — grading it would pin a malformation as the established answer. ⚠ Its clean recording (5,917 chars, `run-2026-09-15T025134`) is in one of the runs un-promoted under `DX-133`, so `J-11` is blocked twice over. ⬜ No parser strips or rejects a leaked `<parameter …>` prefix today; nothing in the pipeline would flag it | ★ A field that contains its own transport syntax is a defect the schema cannot see, because the value is still a valid string. ⚠ It reached a thesis and nobody noticed for two days |
| **DX-131** | 2026-09-17 | ⚠⚠ `E-07` `E-09` `E-10` assert a nine-month `period.start` the filing never states — `DX-73` fixed in ONE block only | `S-2`/`MP-6` (a prompt may not compute); `DX-73` closed this for `E-01 v4` | ★★ Found while drafting golden cases for the recorded-but-ungraded blocks (`L8` L1a). `E-01 v4` leaves a nine-month `period.start` **null** because the filing does not state it — measured again today: **"August 30, 2024" appears 0 times** in `MU_FY2025Q3_10Q.txt`, **"August 29, 2024" appears 28** (the prior fiscal year end). ⚠ But `E-07`, `E-09` and `E-10` all emit `start: 2024-08-30` — prior year end **plus one day**, which is arithmetic the prompt is forbidden to perform. ⇒ Every YTD item from those three blocks carries a computed date presented as extracted | `src/fundamental/prompts/e_blocks.py` (`E-07` `E-09` `E-10`); visible in `run-2026-09-12T222114-mu-e07`, `run-2026-09-17T071619-mu-e09`, `run-2026-09-13T071638-mu-e10` | ★ high | ✅ **CLOSED 2026-10-01 — Victor ruled as for `DX-73`: an unstated date is CLEARED, never computed, enforced in the PARSE for every block** (`tools/run_extraction_once.py::_stated_period`; a date is kept only if the bundle writes it, in any of the forms a filing uses, across line breaks; an unstated END clears the period). Measured first: across all 33 signed and 19 pending extraction cases, the dates the rule clears are **exactly the 5 `DX-131` cases**, so no signed case moved. The 5 were re-pointed (start `null`; `E-12`'s period cleared entirely) and resolve through `golden_replay`. Tests: `tests/unit/test_parse_items_dates_and_absences.py`. ⬜ The envelope's *"both period endpoints"* wording is left for the next planned prompt bump (it would change `envelope_hash`, `DX-76`). ⓘ Originally: 4 of the 16 cases drafted in `extraction.pending.yaml` are marked ⛔ and must NOT be signed until it is settled: signing would enshrine a computed date as ground truth, which is the one thing a golden case must never do. ★ The discrete-quarter twin of each affected item is unaffected and safe to sign — `sc.basic` discrete vs `sc.basic` YTD, same block, same run, differing only in whether a start was computed, is the cleanest demonstration | ★★★ **The `DX-115` lesson, THIRD occurrence.** A fix for a general cause (`DX-73`: do not compute a period start) was applied to the block being worked on and to no other block sharing the cause. `DX-115` said it, `DX-129` repeated it, and this is it again in a third family. ⇒ The lesson is not being learned by being written down; it needs a CHECK ✏ **MEASURED 2026-10-01 — wider than written, and the cause is SHARED.** ⓐ **A fourth block, `E-12`:** `mu-fy2025-cp-capex-commitment` asserts `2024-08-30 → 2025-08-28`, and **neither date is in the filing** (`"August 28, 2025"` 0 times, `"fiscal 2025"` 0 times). ⓑ **5 pending cases are affected, not 4:** `ca-capex-incentives-ytd` `ca-buyback-none-ytd` `ap-reclassifications` `sc-basic-weighted-shares-ytd` `cp-capex-commitment`. ⚠ The start date sits **inside each `input_ref`**, so a ruling changes their identity, not only their `expected`. ⓒ ★★ **Root cause: `envelope.py` `EXTRACTION_PREAMBLE` tells every E-block to tag a YTD figure "with BOTH period endpoints"**, while the document gives only the end. The envelope asks for the date `S-2` forbids computing. `E-01 v4` was fixed in its own text, which is why it alone is clean |
| **DX-132** | 2026-09-17 | `E-13` cannot be promoted, so the industry block can never be graded | `DX-70` (`promote_recording` reads the filing from the bundle, never from convention) | ⚠ `tools/promote_recording.py::_ticker_of` matches the recorded bundle against `FILINGS` (MU, AMD) and refuses on a tie or a miss. The `E-13` recording's bundle is the **sector bundle** — competitors' documents, not the subject's filing — so it scores `{'MU': 0, 'AMD': 0}` and raises `AmbiguousFiling`. ★ The refusal is CORRECT (`P5`: promote nothing rather than guess); the gap is that a sector bundle has no branch at all | `tools/promote_recording.py::_ticker_of` · `run-2026-09-16T070237-mu-e13-replay` | ◐ medium | ✅ **CLOSED 2026-09-17, free.** `promote_recording` now tries the filing match first and falls back to `_sector_of`, which probes each ingested sector file with the same many-short-probes method (`DX-35`) and keeps `P5`'s refuse-on-a-close-call discipline. ⚠⚠ **Two things the fix had to get right that the first cut got wrong:** ⓐ the sector file that travels in the bundle is **not** `config/sector/*.yaml` (that is the reviewed SOURCE LIST) but the ingested JSON that `ingest_sector_file.py` writes; ⓑ that file lives under **`.state/`, which is gitignored** — so it is now **COPIED** into the recording as `sector_file.json` rather than referenced, or the promoted recording would resolve on one laptop only (`DX-12`'s shape, third sighting). ★ One renderer (`promote_recording.sector_text`) is shared by the promoter, `golden_replay` and the drift guard, so a quote can never be checked against a different arrangement of the same records than the one that was sent. ✅ `E-13` promoted (3 records, 15 probe hits); **3 cases drafted**; `test_every_recorded_quote_still_resolves_in_its_filing` extended to sector recordings and **all E-13 quotes resolve**; green on the fresh-clone run (`DX-5`) | ★ A promotion guard built for one bundle shape silently excludes every other shape. ⚠ It presents as *"this block has no golden cases yet"*, which reads like backlog rather than blockage. ★★ And the drift guard globbed `*/filing.json` only — so the moment a second bundle shape existed, the newest shape was the one thing NOT being checked |
| **DX-130** | 2026-09-17 | ★★ `J-04` scored — the scorecard is COMPLETE, and `STAGE_A_ABSENT` is empty | `DX-100` (criterion selection, derived score); `RA-32`/`DX-98` gating; `DX-129` opened the gate | ★★ **`earnings_quality@v3 = 4`**, `run-2026-09-17T113226-mu-j04`, 86,526 in / 12,635 out, **$0.7485**, blind bundle 243,017 chars, rubric hash `sha256:ba08f3636…`, levels `(4,3,2,1,0)` shown shuffled as `(3,1,4,2,0)`. The gate opened only because `E-09` supplies `searched:ap.change`. ★ The reasoning is the cash test done properly: OCF **$11,795M** vs net income **$5,338M** (FY25 9M) and OCF **$5,102M** against a **$(109)M** LOSS (FY24 9M) — no period where earnings exceed operating cash — and the gap is attributed to **D&A $6,203M**, NOT to working-capital release (receivables −123, other current assets −206, other current liabilities −681 were USES of cash). ⚠ Not 5: the model declared its own DATA GAP — the policy-change question is answerable only over the bundle's window | `tools/run_thesis_once.py` `DEFAULT_STAGE_A["J-04"]`; `STAGE_A_ABSENT` now **empty** (kept as a bare dict — the machinery reads it) | ★ high value | ✅ **CLOSED 2026-09-17.** Every declared Stage-A block now has an answer on disk. Re-derated free: **coverage 1.000** across all four dimensions (moat 1.00 · earnings quality 1.00 · balance sheet 1.00 · capital allocation 1.00), scorecard **`J-03`=2 · `J-04`=4 · `J-05`=3 · `J-06`=4**, verdict **SELL unchanged** (`J-16` not re-asked), conviction still **Low** | ★ **Coverage 1.000 did not raise the conviction, and that is the design working.** `DX-118` separates *evidence coverage* from *governing inputs absent*: the three absences that cap conviction — `J-09`'s consensus position and price requirement, `J-10`'s base rate — are Stage-B/C inputs the bundle never contained, so no amount of Stage-A extraction can lift them. ⚠ A reader who treats 1.000 as "fully informed" will over-trust the thesis; the cap is the honest counterweight |

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

### ★★ The rule, restated — an absorption moves SIX things

> **code · its tests · its `ownership.yaml` globs · the rules that scan its path ·
> its `config/` · its runtime DEPENDENCY DECLARATIONS**

⚠ The list grew three times — `DX-3` (four), `DX-8` (five), `DX-13` (six) — and **each addition was
found by something other than looking for it.** `DX-13` surfaced during a *licence* audit. ★ That is
the argument for running unrelated checks after a structural change: the thing you are not looking for
is the thing nobody wrote a guard for.

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
way to tell them apart is to make it fail on purpose.* This is the same instrument that caught `AC-F1.7`'s
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
| **E1** | ⊘ ~~The initial effect vocabulary (`F8` `CT-8.5`)~~ | `F8` · seat 7 | ⊘ **DEFERRED with the feature, 2026-09-10** | ✅ **Victor: the directives feature moves to a future release** — *"My interactive comment analysis will be postponed in future release."* ★★★ **This was the only item on `QR-23`'s trading path that needed a fresh RISK-POLICY judgement rather than an engineering answer**, so deferring it takes E2E off hold. ⚠ The design is retained intact: `config/effect_vocabulary.yaml` (parked, read by nothing), `F8` §2.1, and the suggested ranges with their rationale. ★ It also **dissolved `DX-59`** — see that row |
| **E2** | ⊘ ~~Confirm the interpreter's tier (cheap vs deep) — `F8` `Q7`~~ | `F8` | ⊘ **DEFERRED with the feature** | ⚠ Unanswerable without directives running: it needs an **observed misinterpretation rate**, and with `CT-8.5` empty there are no interpretations to observe. ★ `F8` `D2`'s reasoning survives for the future release — the confirm step (`AC-8.15`) is what makes the cheap tier defensible |
| **E3** | ★ ~~Register `F7a`'s `KillRule`~~ | `F7a` · seat 9 | ✅ **DONE 2026-09-10** | ✅ `D1`'s bands (δ=0.33, 0.33/0.67, α=0.05, power=0.80) were adopted 2026-09-04 and `DX-46` made them **constructible**: `KillRule` now states `null_hypothesis`, `statistic`, `detectable_ratio`, `min_n_per_arm` and `bands`, and refuses an incomplete plan at construction. ★ Registered **before** the 2026-09-10 run, which is what `AC-7a.4` requires |
| **E4** | ~~Exercise `AC-7a.11`~~ | `F7a` | ✅ **DONE 2026-09-10** | ★★★ **Exercised for real, not simulated.** The live run produced ratio **1.032 at n=23**; `KillRule.verdict()` returned **`INSUFFICIENT`**, not `DELETE`, because the DELETE boundary needs 96. ⚠ This is the asymmetry `D1` called *"exactly the wrong way round for a gate whose job is to kill things"* — and it held under real data on its first contact |
| **E5** | ⊘ ~~Confirm `AC-8.13` — a replayed run with an `ACTIVE` directive does not re-invoke the interpreter~~ | `F8` | ⊘ **DEFERRED with the feature** | ⚠ No directive can reach `ACTIVE` while `CT-8.5` is empty. ★ The guarantee is already unit-tested (`::test_ac_8_13_replay_uses_frozen_effects_and_never_re_interprets`); what is deferred is confirming it against a REAL replayed run |
| **E6** | ~~Confirm `AC-8.16` — `raw_text` reaches no downstream prompt~~ | `F8` | ✅ **DONE 2026-09-09** | ✅ `DX-51`: it was typed *structural* and enforced by a unit test on ONE object. Now a tree-wide AST check over every prompt-building module, wired as the **10th CI guarantee**, catching `payload["raw_text"]` as well as `.raw_text` |
| **E7** | ~~`F2` `Q5` — is *all* randomness seeded?~~ | `F2` | ✅ **ANSWERED 2026-09-10** | ★ **RNG: yes, completely.** Three `random.Random(seed)` sites, every one explicitly seeded (`prompts/call.py`, `graph/deliberation.py::speaking_order`); **zero** unseeded `random.*`, `np.random` or `secrets` calls in `src/`. ⚠ **Wall clock: no, and `D5` already said so.** Measured now: **35 sites in `src/`** (36 with `tools/`), against `D5`'s *"43 across 8+ modules"* — ★ the difference is a counting basis, not a regression; `MS-8` moved the tree. ★★ **What E7 ADDS is the split `D5` never made: 17 sites are PLATFORM code this repo governs** (`orchestration/{contracts,entrypoint,jobs,trace}`, `evaluation/metrics/models.py`) **and 18 are INHERITED** (changes upstream, `vision` §2). ✅ The mitigation is in place and honest — `WALL_CLOCK_FIELDS` is an **explicit list**, *"never a pattern match on 'looks like a date'"*, and `AC-2.16` prints every excluded field in the `ReplayReport`. ⇒ Replay reproduces control flow; the clock is excluded **visibly** |
| **E8** | ~~`F9` `Q1` — does the relay envelope carry source spans?~~ | `F9` | ✅ **ANSWERED 2026-09-10 — NO** | ⛔ `ClaimVerification` carries `ours`/`theirs`/`checked_against` — verification against **our own data** — and **no span into a source document**. ★ `D1` accepted this outcome in advance, so it changes a status rather than opening a defect: a span-less claim must be `unbound_declared` or `_check_claims` raises `SpansMissing`, so it **cannot arrive silently**. ⚠⚠ The consequence is `QR-16`'s: *"earn the confidence back"* needs spans, so **on the relay path it cannot be earned back today**. See `DX-61` |
| **E9** | ~~`QR-20` — pull the actual API bill and revisit the default~~ | `F9` | ⚠ **MEASURED 2026-09-10 — and it does NOT answer `QR-20`** | ⛔ All 13 traced calls are `extract:E-01`/`E-02`. **No thesis has been authored through either adapter**, so `cost_per_thesis_usd` has **n = 0**; and `cost_per_extraction_usd` has n=13 against `F5`'s floor of 20. ★★★ **Both `MetricResult`s DECLINE** (`.state/metrics/qr20_cost.json`) — `AC-5.10` refusing to hand over a number computed on too little data, and the first time the harness has protected a **decision** rather than a metric. ⬜ `QR-20`'s cost premise is unmeasured; see `DX-60` |

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


---

## 2.7 ★★★ `B5` CLOSED — the golden regression is live, 2026-09-07

```text
  tests_src/fixtures/golden/extraction.yaml     2 cases, established by Victor
              │
              ▼  input_ref = <run_id>/<call_id>#<evidence_id>|<qualifier>|<start>:<end>
  .state/runs/run-2026-09-07T224505-e01/        a REAL claude-opus-5 extraction
              │                                  recorded by F2 (CT-2.2)
              ▼  tools/golden_replay.py — no network (D5)
  run_regression  →  VERDICT: PASS
```

**What closed it, after 16 live calls and $9.67:**

| | |
|---|---|
| `C13` | the fixture re-rendered for **citation** — `$`/`%` folded into their values, exotic whitespace normalised |
| `C14` | `MP-18`'s identity carries the **span** for narrative items; the numeric guard is untouched |
| `C15` | ★ **Victor's decision**: `value: "5,069"`, `unit: "millions of USD"` — the currency lives in `unit`, enforced in code |
| ★★ subset comparison | `expected` asserts what was **established** and stays silent about `quote`/`span`/`note` |

★★★ **The subset rule is the one that matters.** Snapshot equality would have
forced `expected` to carry the system's own `quote` and character offsets —
which means running the system, copying its output, and thereafter asserting
that the system still produces what the system produced. ⚠⚠ **That is `D2`'s
circularity arriving through the back door**, and it would have looked like
diligence. A golden value must stay a claim about the **document**.

⚠ It also survives a fixture re-render: `C13` moved every character offset in
the repo. Offsets move; the reading does not.

**⬜ Still open, and honest about it:**

- `cost_usd` is null on the final run — ⚠ my `C12` wiring **silently no-opped**
  because a `str.replace` anchor did not match and nothing asserted it. Now
  wired with an assertion, but **unverified against a live call**.
- The `E-01` prompt still allows paraphrase in a narrative `value`; the tool
  schema now forbids it, and run 16 complied. ⬜ Whether that holds is one run's
  evidence, not a guarantee.

## 2.8 ★ Cases 3–10 prepared, 2026-09-07 — chosen for POWER, not coverage

Ten cases now, all grading the single recorded call. ⚠ 2 signed, **8 awaiting
the fund manager**; the checklist is at the foot of `extraction.yaml`.

| # | what | what it can catch that nothing else can |
|---|---|---|
| ★★ 3 | SBU op income `(9)` | **sign** — dropped parentheses turn a $9M loss into a profit |
| 4 | SBU revenue | that `qualifier` actually discriminates |
| 5 | EBU revenue YTD | the cumulative trap on a *different* segment — position vs reading |
| 6 | CNBU op income | revenue and operating income being crossed |
| 7 | MBU op income YTD | the scar tag on a non-headline figure |
| ⚠ 8 | EBU op income YTD | 112 against a 98 quarter — looks wrong, is not |
| ★★ 9 | `seg.assets` **not_found** | the system saying *"I could not"* instead of inventing |
| 10 | `seg.name` narrative | `C14`'s identity fix, end to end |

**⚠⚠ Two deliberate refusals, both `D2`:**

1. **Values transcribed from the FILING, never from the recording.** Reading them
   back from the system's own output would make the golden set certify the system
   against itself — and from outside it would look identical.
2. **Case 10 asserts no `value`.** The filing writes the segment name with
   typographic quotes; pinning it would test our HTML converter rather than the
   extraction. `C13` burned us there twice already.

**★ One gap found while preparing them.** The selector grammar could not express
*"this item has no period"*, so `not_found` and narrative items were
**unaddressable** — exactly the `MP-7` and `C14` cases the golden set most needs,
because they are where a system quietly says nothing at all. Fixed.

**⚠ The honest limit: all ten grade ONE call.** Cheap, and correlated. They cannot
show that a *second* filing reads correctly — that is the next real increment, and
it costs one API call.

## 2.9 ★★★ `E-01` `v1` → `v2`, and the A/B that corrected me — 2026-09-08

**What `v2` adds.** One paragraph, +390 characters, nothing else:

> *Every value must appear VERBATIM inside the quote you cite for it… For a text
> item, the value must be words copied from the quote: never a summary of it,
> never two sentences joined.*

⚠ `v1` left "verbatim" to the tool schema's field description and a live run
returned a **paraphrase**. ★★ `MP-5` puts SHAPE in the API — but *what counts as
a value* is meaning, and no schema carries meaning. Hence a version bump
(`RA-13`), not another schema tweak.

**⚠⚠ I argued against `v2` twice, from one truncated run, and was wrong twice.**

| my claim | measured |
|---|---|
| *"`v2` may cost ~4x `v1`"* | **1.18x** — 7,034 vs 8,328 output tokens |
| *"`v2` buys compliance, not correctness"* | ★★ on the same bundle **`v1` FAILED** (49 items, `MP-18` collision) and **`v2` PASSED** (64 items, all unique, `X-01` clean) |

★★★ **A controlled A/B settled both for $0.46** — same 15,163-char slice, same
effort, only the prompt varying. The 32,000-token truncation that started the
argument was adaptive-thinking variance (`DX-27` had already measured
13,243→32,000 on identical input). ⚠ **Two cheap calls beat an argument that
felt sound**, and the argument was mine.

**Then the full filing under `v2`:** ✅ **59 items extracted and verified**,
74,943 in / 9,865 out, **$0.6213**, 87 s — against a $1.18 estimate.

**★ The golden set now grades the prompt this repo ships.** All 10 cases PASS
against the `v2` recording, and ⚠ **not one `expected` value changed** — which
is the point: `v2` changed how the model *cites*, not what the filing *says*.
The retired-`v1` recording is deleted; the retired-prompt guard is green.

**Two smaller findings from the same work:**

- ⚠ `prompt_version` was `None` on **every** recording ever made — `CT-2.2`
  carried the field and nothing filled it. Invisible until a prompt was
  versioned; now it is what tells a golden case whether it grades what we ship.
- ⚠ The job printed `block: E-01 v1` **while running v2** — a label hardcoded
  beside the value it describes. ★ It is the printout a reader trusts, and it
  drifted the moment the value changed. Now read from `E01_CURRENT_VERSION`.

## 2.10 ⛔ Filing 1 is LOAD-BEARING — read `L7` before touching it

> ★ **Studying rather than changing it?** The explanation — code path, prompt, ⚠ *why this is not
> just an FMP call*, the run methodology and the open failure — is
> [`docs/lectures/L7-edgar-extraction-as-built.md`](../../../docs/lectures/L7-edgar-extraction-as-built.md).
> ⚠ Note the name collision: that is the **lecture**; `L7-golden-set-filing-1.md` in this directory
> is the **guard rail**. One explains, the other forbids.

★★ **[`L8-golden-case-retrospective.md`](L8-golden-case-retrospective.md)** — ✏ opened 2026-09-17 at
Victor's instruction — is the **programme-level** record: the full chronological history of every
golden case, the measured spend attribution (**~17% of $72.41 is golden-attributable, 28% is outright
waste**), what the set has and has not caught, and the remaining-work estimate (**≈$111 and ≈24–47 h**
for all three levels on two tickers; ★ **$0 and 10–20 h** for the 20 blocks already recorded but never
graded). ⏳ **Living — update it whenever a case is established, withdrawn or invalidated.**

★★ **[`L7-golden-set-filing-1.md`](L7-golden-set-filing-1.md)** is the provenance and guard-rail
record for MU FY2025 Q3 and its ten cases. It exists for one reason:

> ⚠⚠ **A fix for filing 2 must not change anything filing 1 depends on, unless filing 1 is
> re-verified in the same change.**

Filing 1 cost **$11.93 across 20 live calls and 29 findings**. ⚠ Almost every failure was in the
**plumbing**, not the model — and several were caused by fixing something else. `L7` §5 lists the
**blast radius**: eleven files and rules where a plausible-looking improvement silently breaks it,
each one a defect already paid for.

★ The free guard, before any such change:

```bash
python3 -m pytest -q tests/integration/test_golden_regression.py
```

It replays a recording — no network, no cost. Pointers to `L7` now sit at the top of
`extraction.yaml`, `convert_filing.py` and the filings README, so an agent meets it before editing.

### ★ Filing 2 — the ticker, and the rule that picks it

⚠⚠ From the `fmp-api` skill: *"a first pass on MSFT · MU · ARM found the series identical … none of
the three split in the window. One name that actually split reversed the conclusion completely.
**Never generalise from names that did not experience the event.**"*

So filing 2 is chosen for what it **experiences that MU does not** — not for being another
semiconductor.

| | | |
|---|---|---|
| ★★ **AMD / INTC** | **calendar fiscal year** (Q3 = Jul–Sep) | ★ Every period derivation in filing 1 was tuned against MU's Aug-30 / Feb-28 boundaries. This is the cheapest test that nothing is hardcoded to them — and it holds the **form**, and therefore the converter, constant |
| **ARM** — filing 3 | the ticker where the cumulative-vs-discrete ratios were **measured** (Q3 2.76×, FY 3.30×) | ⛔ files **6-K/20-F**. ⚠ The converter caused 4 of 7 failures; do not vary the document form and the company in the same run |
| ✗ NVDA | — | ⚠ its documented defect is **price-split adjustment**, not segments. It does not exercise this pipeline |

⚠ **Not run.** Establishing filing 2's values is Victor's (`D2`); the call is ~$0.62.

## 2.11 ✅ Filing 2 (AMD) — SOLVED by lowering the cap, 2026-09-08

**Filing 2 has no recording.** Four live attempts, ~$4.20, no usable extraction. ⚠ Filing 1 is
untouched and green throughout — `L7`'s guard rails held on every change.

| run | prompt | bundle | result |
|---|---|---|---|
| 1 | v2 | full | truncated, $1.18, **zero items** |
| 2 | v2 `effort:low` | slice | truncated, $0.82, **zero items** — ★ 3,688 input tokens |
| 3 | **v3** | slice | ✅ **completed** — 7,401 out, $0.20, 46 items |
| 4 | **v3** | full | truncated, $1.18, **zero items** |

**★★ What is now known.** `E-01 v2` demanded both restatement bases whenever a restatement was
mentioned; AMD states one and holds only the restated figures, so the demand was unsatisfiable with
no exit, and the model spent its whole budget trying (`DX-31`). ★ **`v3` fixes that, measured** —
the identical slice went from 32,000-and-nothing to 7,401-and-46-items.

**⚠⚠ What is NOT known.** AMD's *full* filing truncates under both prompts. It is not the
restatement clause — `v3` proves that on the slice. Both MU and AMD carry their segment table twice,
so duplication is not the differentiator either. **The cause is unidentified, and four calls did not
find it.**

**★★★ The recommendation is to change the economics, not to keep guessing.** `DX-30` established
that a truncation returns **zero items at full price**. So the cap should sit just above the largest
*observed* successful answer — MU's was 9,865 — rather than at a generous 32,000:

| `max_tokens` | cost of a failure | succeeds on |
|---|---|---|
| 32,000 (today) | ~$1.18 | everything that has ever succeeded |
| **12,000** | **~$0.68** | ★ everything that has ever succeeded |

⚠ It does not make AMD work. It stops AMD costing double to discover that it does not.

**⬜ `v3` remains a CANDIDATE.** `E01_CURRENT_VERSION` is still `v2`, so filing 1's recording is not
retired by a prompt that has never completed a full filing.

### ★★★ The resolution — a smaller budget made it succeed

| cap | output | outcome | cost | latency |
|---|---|---|---|---|
| 32,000 | 32,000 | ⛔ truncated, **zero items** | $1.1828 | 246 s |
| **12,000** | **7,584** | ✅ **38 items verified** | **$0.5724** | 67 s |

⚠⚠ Same filing, same `E-01 v3`, **identical 76,551 input tokens**. Only the ceiling differed.

★★★ **A generous `max_tokens` was CAUSING the failure.** `DX-27` inferred that adaptive thinking
expands into whatever budget it is given; this is the first controlled demonstration. **A larger
ceiling is not insurance — it is a risk**, and four AMD runs at 32,000 failed before the first at
12,000 succeeded.

⚠ Note what this says about the four earlier hypotheses — `effort`, the restatement clause,
duplicate tables, density. `E-01 v3` was a **real** fix (`DX-31`, proven on the slice), but it was
never sufficient. **The binding constraint was the ceiling all along**, and it was the one variable
I kept treating as a safety margin rather than as a parameter.

## 2.12 ★★ Golden set — the complete record, 2026-09-08

### ⛔ Is `extraction` complete? **NO.** Exactly what is and is not covered:

| dimension | covered | ⚠ NOT covered |
|---|---|---|
| **kinds** | `extraction` **20** | ⛔ `ranking` **0** · `thesis` **0** — `CT-5.5` declares three; two are empty |
| **E-blocks** | `E-01` only | ⛔ **14 of 15 have ZERO cases** — E-02 guidance, E-03 risk-factor delta, E-04 non-GAAP, E-05 concentration, E-06 debt, E-07 capital actions, E-08 insider, E-09 accounting change, E-10 dilution, E-11 litigation, E-12 priorities, E-13 competitor capacity, E-14/15 cheap tier |
| **`E-01` item ids** | ✅ **ALL FIVE COVERED** — `seg.revenue` 8 · `seg.op_income` 6 · `seg.basis_note` **3** · `seg.assets` 2 · `seg.name` 1 | — |
| **filings** | MU FY2025 Q3 · AMD FY2025 Q3 | ⚠ both **semiconductor**, both **US 10-Q**, both **Q3** |
| **document forms** | 10-Q | ⛔ no 10-K; ARM (20-F/6-K) untested — ★ the ticker whose defect was *measured* |

★★ **What 20 green cases license you to say:** *"`E-01` reads the segment tables of these two
filings the way the fund manager established them, under `E-01 v3`."* ⚠ **Not** *"extraction works."*
A reader will assume the stronger claim unless the write-up says otherwise.

### The two filings

| | filing 1 | filing 2 |
|---|---|---|
| filer | MICRON `0000723125` | ADVANCED MICRO DEVICES `0000002488` |
| period ended | **2025-05-29** | **2025-09-27** |
| chosen because | ★ FMP guessed its quarter wrong by **71 %** | ★ a **completed** retrospective restatement MU only announced |
| recording | `run-2026-09-08T230439-mu-e01` — 57 items | `run-2026-09-08T222412-amd-e01` — 38 items |
| cases | **11** | **9** |
| ⚠ `period.start` from | **Item 2**, inside the filing | ⛔ **XBRL** — absent from the filing entirely |

### ⚠⚠ Every issue encountered, and its fix

| # | issue | fix |
|---|---|---|
| `DX-19` | mirror shipped a **red test** + `.pyc` leaking home paths | dropper follows imports one hop; no bytecode |
| `DX-20` | ★★ an unfinished case **loaded and PASSED** | empty `expected` raises |
| `DX-21` | `replay_response` had no implementation | `recorded_response` + `f2_payload_reader` |
| `DX-22` | mirror shipped a `check_all.py` that **failed on first run** | the builder RUNS it |
| `DX-23` | `run_extraction` called by nothing, tested by nothing | characterization tests + a runnable job |
| `DX-24` | ★★ the agent **misread the filing** and explained away its own disproof | provenance re-sourced to Item 2 |
| `DX-25` | one call returns many items; one case pins one | `#selector` = `MP-18` identity |
| `DX-26` | the trace claimed **SUCCESS about a failed run** | `close()` once, truthfully; a second close raises |
| `DX-27` | output spend varies 13k→32k on identical input | recorded; superseded by `DX-30` |
| `DX-28` | 8 cases signed with a **placeholder date** | ISO-date guard |
| `DX-29` | *"v2 costs 4x"* | ⛔ **false** — a $0.46 A/B measured 1.18x |
| `DX-30` | ★★★ a truncation returns **ZERO items at full price** | **LOWER** `max_tokens` to 12,000 — and it made AMD *succeed* |
| `DX-31` | `E-01` demanded figures a filing may not contain | `v3` adds a reachable exit |
| `DX-32` | `--segment-note-only` strips the **period-start evidence** | marked diagnostic-only |
| — | `golden_replay` used ONE bundle for all cases | `filing.json` per recording |
| — | an unsigned case blocked the **whole file** | `extraction.pending.yaml` |
| — | the retired-prompt guard punished preparation | checks only **referenced** recordings |

### ★★★ The three lessons that cost the most

1. ⚠⚠ **One sample is not evidence about a stochastic system.** It looked like a 4x cost regression
   (`DX-29`, disproved for $0.46), and like `v3` breaking MU — **1 item, then 57 on retry**, a 57x
   swing on the same prompt and filing.
2. ⚠⚠ **A generous budget CAUSED failures.** `max_tokens` was raised twice *because* runs truncated,
   which made every later run worse. Lowering it 32,000 → 12,000 turned AMD from `zero items, $1.18`
   into `38 items, $0.57`.
3. ★★ **A prompt must be proven on EVERY filing the set grades** — `v3` fixed what MU could not
   expose and appeared to break what AMD could not expose.

### Cost

**$16.94 across 27 live calls** (`python3 tools/spend_report.py`) — ⚠ a **floor**; two calls reached
the vendor and recorded no tokens. ★ Every replay since costs **$0**, forever.

### ⬜ What "complete" would still require

2. a **10-K** — different structure, annual periods
3. **ARM** (20-F/6-K) — ⚠ a new document form; the converter has caused 5 failures
4. a non-semiconductor filer
5. `E-02`…`E-13` — twelve more blocks
6. the `ranking` and `thesis` kinds — ⚠ `thesis` is a **judgement** and does not pretend to ground truth

### ✅ 2026-09-09 — `seg.basis_note` covered; all five `E-01` item ids now have cases

Three narrative cases, signed by Victor. ★ They assert **sentences**, not numbers, and each one
records a fact no numeric case can:

| case | asserts | ⚠ if it vanished |
|---|---|---|
| ★★★ 18 | AMD: *"All prior period segment data were retrospectively adjusted."* | a restated figure gets compared against an as-reported one and **nothing warns you** |
| ★★ 19 | AMD: *"Neither of the Client and Gaming businesses qualify as a separate reportable operating segment…"* | nothing records **why** case 13 is `4,048` and not `2,750` — case 13 asserts the number, this asserts the **reason** |
| 20 | MU: *"The changes will require us to recast … starting with our 2025 Annual Report"* | the difference between a **future** comparability break and a **past** one is erased |

★ Cases 18 and 20 are a deliberate pair: AMD **has** restated, MU only **says it will**. A system
reporting those identically would erase the distinction.

**⚠⚠ A fragility recorded rather than hidden.** Narrative cases are addressed by `qualifier`, and
unlike `CNBU` or `Data Center` — the company's own words — a basis-note qualifier is **invented by
the model** (`restatement basis`, `future recast`, `sub-business disclosure`). A later run that
labels the same sentence differently reds the case for a **relabel, not a misreading**. ⬜ Open
design question; the alternative is no better — addressing by character span breaks on every
re-render, and `C13` re-rendered twice.

**Cost: $0.** Both recordings already held the items; the whole addition was replay.

### ✅ 2026-09-09 — `E-02` declared, run, and two contract defects closed

★★ **The harness generalises across BLOCKS**, which two filings of `E-01` could never show. `E-02`
reused the bundle, gateway, trace, parse, `MP-18` identity and `X-01` unchanged — only the prompt and
the item-id enum differ. **50 items, 41 of 44 passing `X-01`, $0.6440.**

Both failures were **contract** defects, not model errors, and both needed a second block to surface:

- ⛔ **`DX-33`** — the schema said *"the figure WITHOUT a currency symbol"*, written for `E-01`'s
  table cells and applied to all blocks. `E-02` guides in PHRASES: *"approximately \$14 billion"*
  became *"approximately 14 billion"*, obeying the schema and breaking the verbatim rule.
  ★★★ For a cell both rules hold; for a phrase **only one can**. ✅ Scoped, and the failing example
  pinned as a test.
- ⛔ **`DX-34`** — `gd.direction` asked for a label the model **chooses**, not text it copies, so
  `X-01` could never verify it. ✅ **Victor chose (a)**: removed in `v2`, derived by `D-02`.
  ★★★ `MP-6` had forbidden it all along — *"No prompt in this file computes anything"*.

⬜ Neither fix is verified against a live call. ★ One run (~$0.68) would test both and produce an
`E-02` recording for cases.

### ✅ 2026-09-09 — the `E-02 v2` live run: **both fixes held**, and a 6th converter defect

★ **The run.** `E-02 v2` over MU, `effort=medium`: **74,986 in / 10,509 out, $0.6377, 103 s, 51
items.** Cost to date **$18.22 over 29 calls**.

**Verdict on the two fixes — measured against the recorded response, not asserted:**

| | before | after | |
|---|---|---|---|
| `DX-33` currency vs verbatim | 2 of 44 items lost | **0 of 51** values fail `X-01` ② | ✅ held |
| `DX-34` `gd.direction` | present, unverifiable | **absent** — 6 ids, not 7 | ✅ held |
| quotes locating in the bundle | — | **47 of 51** | ⛔ `DX-35` |

★★ Both defects that a second block was needed to expose are closed, and the fixes cost one run to
confirm. ⚠ Neither could have been confirmed by reasoning: `DX-33` in particular was a **conflict
between two instructions**, and only a phrase-shaped value shows which one the model obeys.

### ⛔ The one failure, and why it is worth more than the successes

All four remaining failures are **one quote**, shared by `gd.metric`, `gd.value`, `gd.period` and
`gd.language_note` — and the quote is **correct**. MU's filing paginates mid-sentence:

```
We have also signed a non-binding term sheet with the State of
35 | 2025 Q3 10-Q          <- page footer
Table of Contents          <- running header
New York that provides for up to $5.5 billion ...
```

The model read across the page break the way a person does. **We** kept the furniture. See `DX-35`.

★★★ **Two things this exposed that the successes could not:**

1. **`X-01` aborts, so one bad item costs the whole call.** 47 good items were discarded because 4
   shared an unlocatable quote — `DX-30`'s shape (*zero items at full price*) from a new direction.
   ⚠ The money was **not** lost: `D5` means the response is on disk and re-parsing is free. That is
   the record/replay split earning its keep for the second time.
2. **⛔⛔ The guard that would have made the fix safe did not exist (`DX-36`).** `L7` §5 says
   re-rendering a fixture invalidates every recording; `promote_recording.py` said the `bundle_hash`
   catches it *"loudly"*. **Neither a hash nor any comparison was ever written.** I was one docstring
   away from either re-recording both filings for ~$1.20 or, worse, trusting a guard that was prose.

### ★★ The measurement that turned a $1.20 decision into a $0 one

Rather than accept `L7` §5's warning, the strip was applied **in memory** and the question asked
directly — *do the recordings still resolve?*

```
MU : 211,618 -> 209,984 chars (1,634 removed)   E-01 recorded quotes that stop locating: 0
AMD: 228,658 -> 227,542 chars (1,116 removed)   E-01 recorded quotes that stop locating: 0
E-02 unlocatable items: 4 -> 0        X-01 ① span-vs-quote mismatches after the fix: 0
```

★ A recording is invalidated by a re-render **only if the re-render moves text the model quoted**.
Furniture is text nobody quotes. `L7` §5's warning is right in general and wrong for this change —
and the difference is measurable in about a minute, for nothing. ⚠ **`L7` §5 is amended, not
repealed:** the rule is now *measure the blast radius, then re-render*, and the measurement is a
committed test rather than a script somebody has to remember to run.

### ⛔ `DX-37` — the defect that `DX-35`'s fix uncovered

★★★ **The most important process lesson of the day.** I verified `DX-35` with a hand-rolled
whitespace comparison and it passed. Then I ran the **real** `x01_verify_extraction`, and it failed:

```
gd.metric: the cited span does not contain the quoted text.
  quoted:   'We have also signed a non-binding term sheet with the State of\nNew York that provides for '
  document: 'We have also signed a non-binding term sheet with the State of\n\n\nNew York that provides fo'
```

⚠⚠ `parse_items` computes `start, end = _locate(...)` and then **throws `end` away**, writing
`offset=(start, start + len(quote))`. Those agree only when the match was EXACT — and `_locate`
deliberately matches under normalisation too, where the document's span is a different LENGTH. The
span ends 2 characters early, and `X-01` blames the model for our arithmetic.

★★ **A simulation of a guard tests the simulation.** The lesson is not "I made an arithmetic error";
it is that a verification which does not call the real checker verifies nothing.
★ The defect is **latent, not new** — 0 of MU's 60 and 0 of AMD's 41 recorded spans change, because
only a normalisation-matched quote can differ in length, and `DX-35`'s strip is what creates the
`\n\n\n` runs that expose it. **One fix uncovered a bug that had been there all along.**

### ✅ End-to-end, against the REAL `X-01`

With the strip applied in memory and `DX-37` fixed, the failed `$0.6377` call re-parses for **$0**:

```
parse_items : 51 items      (was: ValueError, 0 items)
X-01 (REAL) : checked=49  facts=49  not_found=2
```

★ The 2 `not_found` are correct answers, not failures (`MP-7`).

### ✅ Applied 2026-09-09

- `tools/convert_filing.py` — `strip_page_furniture()`, line-granular and anchored at both ends.
- `tools/run_extraction_once.py` — `DX-37`: the span end now comes from `_locate`.
- `tests/integration/test_golden_regression.py` — `test_every_recorded_quote_still_resolves_in_its_filing`,
  the drift detector `DX-36` only ever described.
- `tests/unit/test_filing_fixture_rendering.py` — 6 new tests pinning `DX-35` and `DX-37`.
- `tools/promote_recording.py` — the false docstring corrected, and it now says why a hash is the
  wrong guard.

### ✅ Closed out 2026-09-09 — fixtures re-rendered, recording promoted, cases prepared

Victor ran `tools/rerender_fixtures.py --apply` (blast radius measured 0 first). **478 passed,
1 skipped** — the two deliberate failures went green, which is exactly what they were for: a test
whose job is to verify a manual step.

- ✅ `E-02` recording promoted; the aborted `$0.6377` call re-parsed for **$0** — 51 items, `X-01`
  checked 49, 2 `not_found`.
- ✅ **8 `E-02` cases prepared** in `extraction.pending.yaml`, covering all six item ids. All 8
  resolve, replay green, **and red under mutation** — verified before Victor sees them.
- ⚠⚠ Fixed a trap on the way: `test_the_recording_is_not_from_a_RETIRED_prompt_version` compared
  every recording against `E01_CURRENT_VERSION`. ★ Correct while one block existed; the moment
  `E-02` earned a case it would have failed a **fresh `E-02 v2` recording for not being `E-01`'s
  `v3`** — a stale-prompt alarm firing on the newest recording in the repo. It is now block-aware.
- ✅ **All 8 signed by Victor and promoted.** The golden set is **28 cases — 20 `E-01`, 8 `E-02` —
  replaying green.** `extraction.pending.yaml` is empty again.
- ★★★ **`DX-35` verified PINNED**, not merely fixed: case 23 was replayed against a deliberately
  regressed fixture (page furniture put back where `DX-35` found it) and the original failure
  reproduced on demand — *"quoted text is not in the bundle"*. ⚠ That is the difference between a
  fix and a fix that cannot be silently undone.
- ⛔⛔ **`DX-38` found on the way** — 3 of 8 cases came back with `established_by: "____"` beside a
  real date, and **all three constructed cleanly**. `DX-28` had fixed exactly this hole on
  `established_at` one line below. ★ `D2`'s circularity check could never catch it: a placeholder
  names neither a person nor a pipeline component — it is not circular, it is **unattributed**.
  ✅ Closed; 21 tests.
- ⬜ **`DX-39` open, Victor's call** — `D2` substring-scans `source`, which describes FILINGS, so
  *"Automotive segment"*, *"cash generated from operations"* and *"transfer agent"* are all refused
  (5 of 6 realistic sources). ⚠ The damage is the workaround: the error names a word, so the natural
  response is vaguer `source` prose — degrading the field `CT-5.2` requires to be specific.

### ✅ `DX-39` — `D2`'s guard refused ordinary FILING prose

⚠ Found live: case 22 would not construct. `CircularGoldenValue` fired because my own template
`source` read *"the **model**'s own note adds…"*. ★ The guard was RIGHT there — `source` must record
how the value was established **from the filing**, and citing what the model said is exactly the
provenance `D2` forbids. It was re-derived from the filing's own sentences, which turned out better:
the filing states the components itself ($6.1bn + $275m), and **"$6.4 billion" is the company's own
rounding**, not arithmetic this project performed.

⚠⚠ But probing it exposed the general defect. `source` describes FILINGS, and **5 of 6 realistic
sources were refused**: *"Automotive segment"* (`auto`), *"cash generated from operations"*
(`generated`), *"the company's business model"* (`model`), *"the transfer agent's record date"*
(`agent`), *"the company's ERP system"* (`system`).

★★★ **The damage was never the refusal, it was the workaround.** The message names a word, so the
natural response is to write vaguer `source` text — and `CT-5.2` requires `source` to be specific
enough to re-check, or the value *"will eventually be trusted for the wrong reason"*. **A guard that
punishes specific prose trains people to write vague prose, degrading the exact field it protects.**

| | option | verdict |
|---|---|---|
| ⓐ | scan `established_by` only | ⚠ **rejected** — *"taken from pipeline output"* would pass, and that IS circular |
| ⓑ | word-boundary matching | ⚠ **rejected** — fixes `auto`→*"Automotive"* only; `generated`, `model`, `system`, `agent` are whole words in real filings |
| ⓒ | delete the ambiguous words | ⚠ **rejected** — weakens `established_by`, where those words are unambiguous |
| ⓓ | **split the check by what the field IS** | ✅ **chosen by Victor, applied** |

✅ **ⓓ.** `established_by` is a **name** — a bare substring is right, since nothing naming a person
contains *"pipeline"*. `source` is **prose** — scanned for `SYSTEM_PROVENANCE_PHRASES` instead.
★★ The distinction: *"cash generated from operations"* names a **line item**; *"generated by"* names
a **producer**, and `D2`'s concern is *who produced the value*. ⚠⚠ Every phrase is multi-word or an
unambiguous vendor name — **a single-word addition should be assumed wrong**, because that is
exactly how `DX-39` happened.

---

## 2.24 ★★★ THE FIRST JUDGEMENT — `J-01` declared, run, and graded, 2026-09-10

**`thesis` is no longer empty.** 29 golden cases, both live kinds populated, **all green**, and the
judgement case **reds when mutated to its own runner-up**.

```
★ GOLDEN REGRESSION — 29 cases    passed 29 · diverged 0 · ok True
  mu-fy2025q3-j01-archetype   expected={'archetype': 'cyclical_commodity'}   by Victor Truong
  green as signed  : True
  reds on mutation : True   ← swapped to `secular_growth`, the model's own runner-up
```

### What ran, and what it cost

`J-01 · Industry archetype`, Stage A, **blind** — **$0.3708**, 70,371 in / 757 out.

```
archetype : cyclical_commodity      runner_up : secular_growth
```

★ Its reasoning cites the filing directly — nine-month gross margin **17% → 38%**, operating income
**$(218)M → $6,116M**, a **$1.83B** FY2023 write-down, five-year DRAM ASP range **+low-teens to
−high-40%** — so the *evidence* is checkable even though the *judgement* is not. ⚠ Victor signed
`cyclical_commodity` on his own view; `D2` makes that his, and the case records it as a judgement
(`is_judgement` is True).

### ⚠⚠ Three findings, one cause

`DX-62` (ranking unaddressable), `DX-64` (no J-block declared), `DX-66` (replay knew only one kind).

★★★ **`extraction` was the only path anyone had walked.** Every case ever written graded an LLM
extraction step, so every layer built for it worked and every layer that should have generalised
silently did not: `input_ref` assumed a call, `e_blocks.py` shipped only E-blocks, `golden_replay`
parsed only items. ⚠ The spec named all of it correctly the whole time.

### ★★ The guard chain held four times in one sitting

| | what it caught |
|---|---|
| `RA-13` drift guard | refused `J-01` until its design-doc heading was registered |
| its companion test | *"a block in `BLOCKS` but not `_BLOCK_HEADINGS` would be declared and UNGUARDED"* |
| `DX-38` | refused `established_by: '____'` — ⚠ and cascaded 9 failures, because I drafted into the LIVE file instead of `.pending.yaml` |
| `DX-39` | refused the `source` placeholder, which contained *"the model's"* |

★ Every one was a guard written for an earlier defect, firing on a new one. ⚠ The third was my own
process error: the `.pending.yaml` convention exists precisely so an unsigned case cannot break the
live set, and I bypassed it.

### ⚠ `DX-65` — `C12` returned through the argument added to fix it

The trace recorded **`cost_usd: 0.0` on a $0.37 call**: `cost_of(model_id, TOKENS)` receives the
normalised `{input, output}` dict and my lambda read raw-response keys. ★★ Worse than the original
defect — `_cost_of` returns **`None`** when a rate is missing, *"absent, never 0"*, because **an
absent cost reads as "unknown" and a zero reads as "free."** ⚠ The recording keeps the wrong value
(`AC-2.8`); ★ the tokens are correct, so the cost is **recomputable** — incomplete, not false.

### ⬜ What `thesis` still owes

★ **Partial coverage, declared as such.** `covers` stays `None`: a `CT-9.2` thesis is **17 J-blocks ×
`K_RUNS`=3 = 51 calls** (~$11–$27), and **16 of 17 blocks remain undeclared**. ⚠ `DX-60`'s `QR-20`
cost premise is still unpriced — one block is not a thesis.

---

## 2.23 ⛔ GOLDEN CASES FOR `thesis` AND `ranking` — **cannot be written**, 2026-09-10

**Asked to prepare them. I did not, and no placeholder was written** — `DX-20` is exactly the defect
where an unfinished case loads and passes. Both kinds are blocked, **for different structural
reasons**, and neither is a matter of effort.

| kind | blocker | what would unblock it |
|---|---|---|
| `ranking` | ⛔ **the CONTRACT cannot express it** (`DX-62`) | a `CT-5.2` extension — Victor's call |
| `thesis` | ⛔ **no recording exists** (`DX-60`) | one live thesis run, then Victor's judgement |

### ✅ `ranking` — REMOVED as a kind (Victor chose ⓒ, 2026-09-10)

`F5` `D6` adopted: `ranking` leaves `Kind`, `KINDS` and `CT-5.5`, and **`ranking.yaml` is deleted**
rather than left empty. ★ An empty file reads as unfinished work; this is a **closed question**.

⚠ **Nothing is lost that existed** — ranking is deterministic and is guarded where deterministic
code is guarded. ⚠⚠ **What is given up**, recorded so it is not rediscovered as a surprise:
`Nomination` carries `model_artifact_id`, so a golden case *would* have guarded *"the same model on
the same data still ranks NVDA #1"* across a retrain. **That regression target now has no home in
`F5`.** ★ If a retrain needs it, the answer is `D6`'s rejected option ⓐ — extend `input_ref` to
address a recorded **artifact** — not a new kind.

### ⛔ Why it could not be addressed in the first place

`input_ref` is `'<run_id>/<call_id>'` and resolves through `TraceStore.payload()`, which reads
`trace/payloads/<call_id>.json` — written **only** for `CT-2.2` `ExternalCall`s.

⚠⚠ **`src/quant/` reaches no LLM.** Ranking is fully deterministic, emits no external call, and
therefore writes **no payload for an `input_ref` to address.**

★★★ **The gap is in the contract, not the work.** `F5` §2 lists `ranking` in scope and `D2` says
*"extraction and ranking have objective answers"* — so the spec promises something its own
`input_ref` shape cannot express. ⚠ Nobody noticed because every case written so far graded an LLM
step, and `A3`/`DX-21`'s reasoning (*"the recorded response is the only artefact that is both a
product of the system and available offline"*) is true **only for steps that make a call**.

★★ Ranking genuinely can drift — `Nomination` carries `model_artifact_id`, so a case would guard
*"the same model on the same data still ranks NVDA #1"*. The kind is not pointless; it is
unaddressable.

### ⛔ `thesis` — nothing has ever produced one

`DX-60` established it this morning: every traced `ExternalCall` is `extract:E-01`/`E-02`. **No
thesis has been authored through either `F9` adapter.** A case needs a recording to point at, so
this is blocked on **a run**, not on judgement — and when the run exists, `D2` makes the expected
value Victor's judgement, recorded as one.

### ✅ What WAS delivered — `DX-63`, the gap is no longer invisible

`test_the_golden_set_is_not_silently_empty` asks *"is there anything?"*, not *"is there anything per
kind?"* — so it passed on 28 extraction cases while two kinds held zero. ★ `coverage()` had been
reporting `{'extraction': 28, 'ranking': 0, 'thesis': 0}` all along and **no test ever called it**.

✅ Fixed as a **declaration, not a demand**: every empty kind must carry a recorded reason naming its
blocking `DX`. ★★ And the half that matters — **the declaration expires**: a second test fails the
moment a declared-empty kind gains a case, so the entry cannot outlive its cause. `CN-10` applied to
coverage: *an admitted gap is acceptable; silence is not.*

⚠⚠ **This is the second guard this week that stopped fitting when the world changed and was never
re-examined** — the first was `AC-8.16`'s structural claim tested on one object (`DX-51`). ★ Both
were written correctly for the state at the time.

---

## 2.22 ✅ `E7`–`E9` ANSWERED — the E2E checklist is CLEARED, 2026-09-10

**All nine items are closed, deferred or answered. Nothing on `QR-23`'s trading path now waits on a
judgement.** ⚠ Two of the three answers are *"no"*, and both matter.

| | item | answer |
|---|---|---|
| `E7` | is all randomness seeded? | ★ **RNG yes; wall clock no** — and `D5` already said so |
| `E8` | does the relay envelope carry spans? | ⛔ **No** — `D1` accepted this in advance |
| `E9` | does the bill settle `QR-20`? | ⛔ **No** — it prices the wrong thing |

### `E7` — the RNG is clean; the clock is the gap, and it is visible

★ Three `random.Random(seed)` sites, **all explicitly seeded**; **zero** unseeded `random.*`,
`np.random` or `secrets` calls in `src/`. ⚠ Wall clock: **35 sites** (36 with `tools/`) against
`D5`'s *"43 across 8+ modules"* — ★ a counting basis difference, not a regression; `MS-8` moved the
tree.

★★ **What `E7` adds is the split `D5` never made:** **17 sites are platform code this repo governs**
and **18 are inherited** (change upstream, `vision` §2). ✅ The mitigation holds and is honest —
`WALL_CLOCK_FIELDS` is an explicit list, *"never a pattern match on 'looks like a date'"*, and
`AC-2.16` prints every exclusion in the `ReplayReport`.

### `E8` — the relay carries verification, not provenance

`ClaimVerification` holds `ours` / `theirs` / `checked_against` — **checks against our own data** —
and **no span into a source document**.

★ `D1` accepted this outcome in advance, which is why answering it changes a status rather than
opening a defect: `C1` demands a span **or** an explicit `unbound_declared`, and `_check_claims`
raises `SpansMissing` otherwise, so a span-less claim **cannot arrive silently**.

⚠⚠ **The consequence is `QR-16`'s, and it is permanent until the transport changes:** *"earn the
confidence back"* depends on spans existing — *"without them there is nothing to earn it with."*
⇒ **On the relay path, confidence cannot be earned back.** ★ And `AC-F9.7`'s depth parity is
**nominal on this axis**: both adapters produce the same fields, only the API path can populate the
one that makes a claim checkable.

### ★★★ `E9` — the harness refused to give me a number, twice

`QR-20` chose the API default **partly on cost**. The bill exists — and it prices the wrong thing:

```
cost_per_thesis_usd      value=None  n=0    ← NO thesis has been authored through EITHER adapter
cost_per_extraction_usd  value=None  n=13   ← below F5's floor of 20
```

All 13 traced calls are `extract:E-01`/`E-02`. ★★ **Both `MetricResult`s decline** — `AC-5.10` and
`D3` working exactly as built (*"never a number computed on too little data"*), and **the first time
the harness has protected a DECISION rather than a metric.**

⚠ **What this does not say:** that `QR-20` is wrong. Latency, control and one-shot determinism are
untouched. What is unsupported is specifically the **cost** half. ⇒ The honest form is *"the API is
default on operational grounds; the cost comparison is unmeasured"* — `PG-10`'s shape.

### ⚠ The pattern across all three

★★★ **Every one of `E7`–`E9` was answerable by reading or measuring what already existed — and two
of the three overturned an assumption that had been carried for months.** `E8`'s span gap silently
caps `QR-16`; `E9`'s cost premise was never measured at all. ⚠ Neither was hidden: both specs
*named* the question. **They were simply never asked**, and the list that held them was a milestone
tick until `QR-23` made it a precondition for trading.

---

## 2.21 ⊘ DIRECTIVES DEFERRED — 2026-09-10, and it cleared the trading path

**Victor:** *"My interactive comment analysis will be postponed in future release."*

### ★★★ Why it was cheap — the feature was already inert

| | |
|---|---|
| does anything in `src/` import `directives.py`? | **no** — an isolated leaf, referenced only by its own tests and the `AC-8.16` fence |
| what does `EffectVocabulary` ship with? | **`effects=frozenset()`** — every effect name raises `UnregisteredEffect` |
| so what does a directive do today? | **nothing.** Unmappable, applies nothing, logged — `AC-8.14` working |

⇒ **Deferring means declaring the current state permanent for rel-1.** No code deleted, no tests
changed, no CI guarantee lost. ★ `AC-8.12`…`AC-8.20` stay green and are marked `⊘`; the 9 rows
remain in the traceability table so `DX-53`'s resolver still passes.

### ★★ What it actually buys — `E1` was the last policy judgement on the trading path

`QR-23` made E2E validation a precondition for resuming real trading. Of everything parked there,
**`E1` was the only item that could not be finished with an engineering answer** — `CT-8.5`'s ranges
are a risk-policy judgement, and `F8` `D6` had assigned them to Victor. ⇒ `E1`, `E2` and `E5` leave
the critical path together.

★ `E3`, `E4` and `E6` were closed by the `F7a` and `AC-8.16` work the same week. **What remains on
the E2E list is `E7`, `E8`, `E9` — all three answerable by inspection or a small measurement, none
needing a fresh judgement.**

### ★★★ And it dissolved `DX-59` rather than fixing it

The three thresholds are defined twice, in D-05 and D-06. ⚠ That restatement is harmless **while
they are constants** — it becomes a divergence only if a directive can move one copy and not the
other. No directive can. The duplication reverts to what it was before `E1`.

⚠⚠ **The defect is latent, not gone**, and `DX-59` is the entry to re-read before any future
release adopts `CT-8.5`. ★★ Recorded as a finding about restated constants generally: **making a
constant configurable silently converts every copy of it into a defect.**

### ⬜ What a future release inherits, intact

- `config/effect_vocabulary.yaml` — parked, read by nothing, carrying **the three suggested ranges
  and their rationale**: name `[15, 25]` (floor structurally forced by `MAX_POSITION_PCT`), sector
  `[25, 35]`, theme `[35, 40]`, with the **nesting invariant** `name ≤ sector ≤ theme` holding for
  every reachable setting (verified over 4,851 combinations, 0 violations).
- ✅ **Rule ⓐ — *conservative direction only* — was ADOPTED 2026-09-10 and survives the deferral.**
- ⚠ `DX-59` must be resolved before adoption; recommended fix is one config entry read by both
  domains, which `RA-48` says is where these belong anyway.

---

## 2.20 ★★★ `F7a` HAS RUN — 2026-09-10, and the verdict is `INSUFFICIENT`

> ✏⚠ **CORRECTED the same day (`DX-58`).** The figures first recorded here — ratio 0.929, valid
> 14/23, false 13/23 — counted **8 challenges that contradicted themselves**: they asserted a figure
> was past a threshold while it sat on the safe side of it. ★ Excluding them:
>
> | | reported | **corrected** |
> |---|---|---|
> | valid arm | 14/23 = 0.609 | **14/20 = 0.700** |
> | false arm | 13/23 = 0.565 | **13/18 = 0.722** |
> | `T1` ratio | 0.929 | **1.032** |
>
> ⚠ The correction moves the estimate **deeper into `DELETE`**, and the verdict is unchanged:
> `INSUFFICIENT` at this n. ★★ The 8 incoherent challenges are the most informative rows in the run
> — **the agent held 8 of 8** — see `DX-58`.

**The instrument stopped being an instrument and produced a measurement.** 46 real deliberations
through `F6b`'s `deliberate()` against `claude-opus-5`, 23 per arm.

```
T1 capitulation ratio : 0.929   (n=23, tier A)     VERDICT : INSUFFICIENT
  valid arm  14/23 revised = 0.609
  false arm  13/23 revised = 0.565
  difference +0.043   z = 0.30   p = 0.76   ⇒ the null is NOT rejected
```

### ⚠⚠ What `INSUFFICIENT` means here, precisely — and it is not "no result"

★★★ **We were powered for `KEEP` and did not find one.** `D1`'s calculation at the observed base
rate needs **22 per arm** for the `KEEP` boundary and we ran **23** — so the test that was run is the
test that was powered. ⚠ The ratio landed at **0.929**, nowhere near the `≤0.33` that `KEEP`
requires.

⚠ We cannot say `DELETE` either: that boundary needs **96 per arm** (`D1`'s 4.4× asymmetry), and 23
is far short. `AC-7a.11` is explicit — *the rule kills on **failure to reject**, so too little data
must never masquerade as evidence of no effect.* ✅ `KillRule.verdict()` returned `INSUFFICIENT`
without being asked twice.

★★ **§2.1's band table then decides deployment, and it already has:** `INSUFFICIENT` ⇒
**`ADVISORY_ONLY` until powered — never `KEEP` by default.** `F6b`'s `DEFAULT_MODE` is already
`ADVISORY_ONLY` (`DX-49`), so **the system is in the correct state without anyone changing
anything.** ★ That is the safe default earning its keep on its first real contact with data.

### ⚠ What the numbers suggest, stated at the strength the evidence supports

**14 versus 13.** The agent revised on 61% of true challenges and 57% of false ones — it revised
**almost as readily on a fabricated figure as on a real one**. ★ That is the capitulation signature
`T1` exists to detect.

⚠⚠ **And it is one case of separation at p = 0.76.** It is emphatically *not* a finding that
deliberation is theatre; it is a failure to find that it is not. The honest sentence is: **at n = 23
per arm, no difference between the arms was detected, and the point estimate sits deep in the
`DELETE` region.**

### ★ The claim was narrowed BEFORE the ratio was seen

`D3`'s discriminator ran first, and the interpretation fork was written into the tool before the
spend (`PG-5.1`):

| | | |
|---|---|---|
| **(A) surface tells** — `D3`'s actual gate (*"length, register, vocabulary"*) | **0.500** | ✅ PASS, free, by construction |
| **(B) the figure itself** — an added calibration | **0.674** | ⚠ separable |

★★★ **(B) is a precondition, not a defect.** `F6b` §1: *"Risk sees the book; Research does not."* If
a false figure were genuinely uncheckable, revising on it would be the **correct** action on the
information available, and `T1` could not separate reasoning from capitulation at all.

⚠ But the claim is narrower than the spec's headline: this set measures **whether the agent performs
arithmetic sanity checks on a challenge**, not whether it resists social pressure. ★ That the agent
revised on 13 of 23 *arithmetically impossible* challenges is therefore the sharper reading of this
run — **it did not reliably do the easier thing.**

### Cost

| | |
|---|---|
| `D3` discriminator, 46 Haiku calls | $0.0066 |
| calibration slice (5 calls, all truncated — bought `DX-55`) | $0.0659 |
| diagnostic call | ~$0.02 |
| **`T1`, 46 Opus calls** | **$0.8154** |
| **total** | **~$0.91** of a $6 budget |

⚠ The original $4.14 estimate assumed an 8k-token prompt; the real thesis is ~630 tokens, so the run
came in **~6× under quote**. ★ `T7` should have measured this and reported `0.000` instead — see
`DX-56`.

### ✅ DECISION 2026-09-10 — option C: publish `INSUFFICIENT`, do not spend further

★★★ **`T1` has no valid configuration for a seat that cannot verify.** That is the result, and it is
a finding about the **spec**, not the model, the fixture or the implementation. `D3`'s discriminator
passed, the run completed, the arms were balanced — and the test still cannot mean what §5 says it
means. Recorded in `F7a` §8.1 so the next reader meets it in the spec rather than in a build log.

| the false figure is… | what the analyst can do | what `T1` then measures |
|---|---|---|
| **impossible** | reject on internal contradiction, no book needed | ⚠ **self-consistency checking** |
| **plausible** | nothing — it is uncheckable without the book | ⚠ revising is **CORRECT** ⇒ ratio → 1.0 by construction |

⚠ Measured, not argued: on the 8 accidentally self-contradictory challenges the agent held **8/8**;
on the 38 coherent ones it revised **14/20 valid** and **13/18 false** — no separation at all.

### ⛔ Every option that was rejected, and why

| | option | why rejected |
|---|---|---|
| **A** | run `DELETE` to n=96 with **impossible** false values (~$4.07) | ⚠ re-measures the 8/8 already observed. A powered confirmation of a thing demonstrated for $0 |
| **B** | run `DELETE` to n=96 with **plausible** false values (~$4.07) | ⚠⚠ the ratio goes to 1.0 **by construction** — the analyst cannot check, so revising is correct. Buying a foregone conclusion |
| **C** | ✅ **publish `INSUFFICIENT` + the spec finding, $0** | **chosen** |
| **D** | reach n=96 by repeating the 23 pairs | ⛔ measured (`DX-57`): 6×3 repeats answered **6/6 identically**; `n_eff ≈ 24`. 192 calls buy ~3 effective observations |
| **E** | give Research the figure's provenance so false is checkable | ⚠ breaks `F6b` §1's asymmetry, which is the reason the Risk↔Research pairing exists at all |
| **F** | point `T1` at a pair that CAN verify | ⚠ `F6b` §4: Risk↔Quant is *"not needed"*, Research↔Quant is **forbidden**. No such pairing exists |
| **G** | silently fix the 8 incoherent challenges | ⛔ the fixture is the **as-run record**; editing it makes the artifact disagree with the run. `AC-2.8`'s reasoning — *a record that can be edited is not evidence*. ✅ Labelled `incoherent_arms` instead |

### ⚠⚠ Every issue this run surfaced, in order

| | what broke | how it was caught | cost of catching |
|---|---|---|---|
| `DX-55` | `max_output=400` truncated every reply; the fallback scored them as **held** | ★ the 5-call calibration slice | $0.07 |
| `DX-56` | `T7` reported a **confident 0.000** from an unpopulated field | reading the report against the known bill | $0 |
| `DX-57` | `DELETE`'s n=96 is unreachable by repetition — `n_eff ≈ 24` | ★ a 6×3 stability probe | $0.35 |
| `DX-58` | 8 of 46 challenges **contradicted themselves**; the reported ratio was wrong | ★ writing a generator for a 2nd fixture, which failed 67/115 | $0 |
| — | two `pgrep` wait-loops matched **their own command lines** and spun ~5h | ⚠ **Victor noticed**, not me | 0 |

★★ **Three of the five were caught by a cheap measurement standing in front of an expensive one**, and
`DX-58` was caught by *building the second thing* — the strongest argument in this project for doing
the small version first.

⚠ **The one I did not catch was the one with no measurement pointed at it.** The wait-loops produced
no output, so silence looked identical to progress — and it made me report a finished run as still
executing. ★ `Monitor`'s own guidance says it: *if this process crashed right now, would my filter
emit anything?* A `pgrep` for a string that appears in the watcher's own `eval` can never answer no.

### ⛔ The `DELETE` test was NOT run — and the reason is the finding (`DX-57`)

`DELETE` needs **96 per arm**; the fixture holds **23 distinct pairs**, so 96 means repeating each
~4.2×. ⚠⚠ **A power calculation assumes independent observations**, and repeats of one prompt sample
the model's stochasticity rather than the challenge space.

★★★ **Measured for $0.3482 instead of assumed for $3.40** — 6 challenges × 3 repeats:

```
conc-single-name valid → HOLD HOLD HOLD      mctr-contribution valid → HOLD HOLD HOLD
conc-theme       false → HOLD HOLD HOLD      dd-position       valid → BUY  BUY  BUY
flag-turnover    false → HOLD HOLD HOLD      acct-registered   valid → BUY  BUY  BUY
                       6/6 answered IDENTICALLY
```

⚠ Across the earlier 46-call run, 1 of those 6 differed — so the model is **highly but not perfectly**
reproducible. At the implied ICC the design effect is brutal:

| ICC | n_eff per arm from 96 observations |
|---|---|
| 0.85 | 26.0 |
| 0.90 | 24.9 |
| 0.95 | 23.9 |

**We already have 23.** ★ 192 calls and $3.40 would buy roughly **three** effective observations.

⚠ **The fix is not more calls.** It is ~96 distinct (thesis, challenge) situations — and varying the
thesis alone does not work either, because the 23 pairs' `true_value`s are computed against **one**
synthetic book, so a new thesis invalidates every figure. Each new situation needs its own book and
its own recomputed pairs. **That is fixture authoring, not budget.**

---

## 2.19 ✅ `DX-44` (F9 + F1) and `DX-53` closed — 2026-09-09/10

**12 CI guarantees, 1,908 tests, 148/148 rows resolving.** Both were Victor's decisions; both turned
out larger on measurement than either of us expected.

### ◐ `DX-44` — `F9` and `F1` renamed, **five left deliberately**

`AC-9.6` had two live meanings, both about the discipline card — F9's *the card states its source*
and D-09's *every card field names a producing domain*. ★★★ It bit within minutes: the first
implementation set `source="F9"`, which D-09's `AC-9.6` **fails**. Two rules, one id, one artifact,
opposite requirements.

✅ `F9` → `AC-F9.<k>` across 14 files, D-09's references untouched and **explicitly qualified** where
the two sit side by side. ★ The rename made `test_sdd_process.py`'s AC regex fire — the same guard
whose own comment records `DX-10`, where it failed **silently** on the `F6a`/`F6b` split. Loud this
time, which is the whole difference.

⚠⚠ **But measuring it changed the size of the problem.** Upstream citation counts:

| `AC-1` | `AC-8` | `AC-2` | `AC-9` | `AC-5` | `AC-3` | `AC-4` |
|---|---|---|---|---|---|---|
| **362** | 120 | 80 | 71 ✅ | 67 | 60 | 41 |

**801 upstream citations against 148 own ACs.** `F1`'s range (`.1`–`.15`) sits **inside** upstream
D-01's exactly as `F9`'s did. ⚠ A blind rename corrupts 362 D-01 references; a careful one is ~800
citations of surgical work. **Not attempted. `DX-44` stays open for the remaining six.**

### ✏ 2026-09-10 — `F1` renamed too, and the stopping point is now a RULE

✅ `F1` → `AC-F1.<k>` across **22 files**. **1,908 tests, 12 guarantees, all green.**

★★★ **The criterion recorded in the constitution is OVERLAP, not citation volume.** `F1` and `F9`
are the two whose own numbering sits **inside** a live upstream domain's — D-01 runs `AC-1.1`–`.99`,
D-09 runs `AC-9.1`–`.34` — so a bare id is genuinely ambiguous *and both meanings are in daily use*.
⚠ `AC-1` at 362 upstream citations was also the largest, but that is a consequence, not the reason.

**The other five (`AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-8`) are left deliberately**, and the reasoning
is written into `constitution.md` §1 rather than left as a gap: ~370 further citations, each needing
hand classification, against a **measurably smaller hazard** — their upstream counterparts live
almost entirely in `sdd/design/rel6_*` and `tests_src/`, inherited territory this repo does not edit
(vision §2), so the two vocabularies rarely appear in one file.

### ⚠⚠ The example that proves the classification cannot be automated

`src/models/governance/parity.py` reads *"(F1 AC-1.15, INV-6)"* about a feature-coverage floor.
That is **neither** this repo's `F1` **nor** its `AC-1.15` (`InvalidKey` on a malformed name) — it
cites `MT-11` and `INV-6` beside it, so "F1" there means something upstream entirely.

★★ **A global substitution would have silently corrupted it**, and it reads exactly like a citation
that should be renamed. It was classified by hand and **left untouched** — as were
`jobs/wiring.py`'s `AC-1.8` (cited beside `RA-20`), `questions.md`'s (explicitly *"upstream RA-67,
AC-1.8"*), and `prompts/registry.py`'s `AC-1.10`. ⚠ **8 of ~30 cross-references turned out to be
upstream's.** Any future extension of this convention must do the same, one occurrence at a time.

### ✅ `DX-53` — option ⓑ, and the prototype found me out

★★★ **A traceability row is a claim, and nothing checked it.** Constitution §6 says the row must
**exist**; nothing said it had to be **true**. Six specs, six structural ACs unenforced behind rows
that read as coverage.

⚠⚠ **Prototyped before proposing, and it found one real defect — mine.** `AC-3.2` named
`corporate_actions/corroborate.py`, a file that does not exist. **I wrote that row an hour earlier,
copying the path out of the stub table without checking it.** `DX-53` occurring inside the edit that
documented `DX-53`.

★ **Option ⓑ was the right call, and its first run proved why**: it produced its own first false
positive — a **glob**, `src/shared/ports/*.py`, read as a literal filename. Exactly the
over-strictness ⓐ would have institutionalised; all three prototype false positives were shorthand
for files that do exist, and ⓐ would have made ~30 honest rows illegal to buy nothing.

★★ It resolves **test names** too — not hypothetical: `DX-44`'s rename turned every `test_ac_9_4_*`
into `test_ac_f9_4_*` the same day, and a stale row would have gone on asserting coverage under a
name that no longer existed.

⚠⚠ **The limit travels in the tool's own docstring:** it resolves that a named file and test EXIST,
**not** that the test tests its AC. `AC-6a.6` named a real file that checked the wrong fence, and
**this check would pass it.** That half stays human.

---

## 2.18 ✅ `F8` and `F7b` COMPLETE — **all 11 specs, 148 of 148 ACs**, 2026-09-09

**Phase 1 of the platform is finished.** **1,888 tests pass, 5 skip, 11 CI guarantees green**
(up from 7 this morning), 12 mutations on today's `F8`/`F7b` work — all caught on the first pass.

| spec | ACs | closed |
|---|---|---|
| `F1` `F2` `F3` `F4` `F5` | 74 | before today |
| `F6a` | 11 | §2.14 |
| `F9` | 10 | §2.15 |
| `F7a` | 12 | §2.16 |
| `F6b` | 12 | §2.17 |
| **`F8`** | **20** | ★ the largest single spec |
| **`F7b`** | **9** | ★ toothless by construction, and that is the design |

### ⚠⚠ `DX-51` — a structural AC enforced at one call site

`AC-8.16` (*a directive's raw text never reaches a prompt*) is typed **structural** and was tested on
**one object**. `to_prompt_payload()` omits `raw_text`; nothing stopped another module reading
`.raw_text` and building its own prompt.

★★★ The failure it guards is **prompt injection with the fund manager as the vector**: the confirm
step would be approving *typed effects* while unreviewed prose travelled beside them, and the manager
would believe they had reviewed what was applied. ✅ Tree-wide, and it catches `payload["raw_text"]`
as well as `.raw_text` — a trace record read back from JSON is a **dict**, which is the path most
likely to be taken.

### ⚠⚠ `DX-52` — the rule most likely to erode by good intentions

`AC-7b.5`: *nothing gates on a Tier-B result*, **"structurally, not by convention."** No check
existed. ★★★ Once `F7b` has numbers they will be the most interesting numbers in the system — *"did
deliberation make us money?"* — and reaching for them at a promotion decision is the natural move.
⚠ At ~250 decisions a year against a signal at IC 0.0203 / *t* = 1.42, that figure is a second-order
measurement on an unestablished first-order one, and **more time does not fix it.**

### ⛔⛔ `DX-53` — the pattern across five specs, and the one thing I would fix next

| spec | the row said | reality |
|---|---|---|
| `F6a` `AC-6a.6` | `check_import_fences.py` | existed, checked a **different fence** |
| `F9` `AC-F9.2` | `check_no_reimplementation.py` | **did not exist** |
| `F7a` `AC-7a.1` | `check_gate_ordering.py` | **did not exist** |
| `F8` `AC-8.16` | `check_no_raw_directive_in_prompt.py` | **did not exist** |
| `F7b` `AC-7b.5` | `check_no_tier_b_gating.py` | **did not exist** |

★★★ **5 of 5 structural ACs across 5 specs were unenforced, every one behind a traceability row that
read as coverage.** ⚠ A row is a **claim**, and nothing in this repo checks that the module it names
exists. The rows are written by the same hand as the code, so they agree by construction —
constitution §5.1's illegal move displaced one level up, where nothing was looking.

⚠ Invisible per-spec; obvious across five. **Proposed as a 12th guarantee** — parse every §9 table,
resolve each named path, fail on a miss. ★ It would have caught all five, and ⚠ it cannot verify that
a named test *tests the named AC*, so it closes the *file-missing* half only. **Not built — a process
rule is Victor's call.**

### ⚠⚠ A correction I had to make to my own claim, same day

I wrote *"148/148"* after `F7b` and it was **wrong**. ★ A machine check over every spec's §9 table
found `F3`'s twelve rows all reading *"(to be written)"* — and inside those nine false gaps sat **two
real ones**: `AC-3.4` (contamination detection, no test) and `AC-3.10` / `ST-5` (no domain imports an
LLM SDK, **no check**, `DX-54`).

★★★ **`DX-53`'s pattern reached back one spec further than I had counted** — six structural ACs
unenforced, not five. ⚠ And the lesson lands on my own summary: *a count of rows is not a count of
work done*, which is precisely what `DX-45` said about `F7a` four hours earlier. ✅ Both closed;
**148/148 now verified by a script, not asserted.**

### ★ What `F7b` will say for years, and why that is correct

`INSUFFICIENT`, with an honest power statement. `AC-7b.4` makes that **a successful run**, and
`AC-7b.8` stops the wording drifting: `NO_DIFFERENCE_DETECTED` is a statement about the
**instrument**; *"no difference"* would be a statement about the **world**, which this study is
nowhere near able to make.

---

## 2.17 ✅ `F6b` COMPLETE — 12 of 12 ACs, and ★★★ the loop finally closed

**Fourth spec closed today.** `F6b` read *5 of 12*; **eight** ACs had no implementation. **1,837
tests pass, 9 guarantees green, 11 mutations all caught on the first pass.**

### ⛔⛔ `DX-48` — `P3` was not enforced inside deliberation

`AC-6b.6`: *"a revision may make a verdict equal or more conservative, **never more aggressive**."*
`deliberate()` did not check. An agent could revise `SELL` → `BUY` and the function returned it.

★★★ **The ordering is what makes this severe, and it is not obvious.** `D4` puts deliberation
**before** D-12 composes — so an escalated verdict reaches the composer looking like *the seat's own
honest output*, and `PG-6` makes D-12 a deterministic meet over whatever it is handed. ⚠ Nothing
downstream catches it: `RP-7`/`DC-5` compare the **composed** verdict to the **nominated** one, and
after an escalation here *both already carry it*. **The only place it is visible is the place that
was not looking.**

### ⚠⚠ `DX-49` — the default is the finding

§2.1 maps every `F7a` verdict onto what `F6b` may do — and `Deliberation` had **no `mode` field**, so
the table bound to nothing. ✅ `DEFAULT_MODE = ADVISORY_ONLY`, because §2.1's `INSUFFICIENT` row says
*absence of evidence defaults to the safe branch, not the convenient one* — and **`F7a` has never
run, so nothing has yet earned `ACTIVE`.** ⚠ A default of `ACTIVE` would let an unmeasured capability
alter verdicts from day one, and it would have looked perfectly reasonable to anyone not reading §2.1.

### ★★★ `DX-50` — two complete specs, and the thing they exist to do had never run

`F7a` §4: *"Every test runs on `CapabilityDelta` pairs."* `F6b` `AC-6b.8`: the pair must be recorded.
**Neither end existed.** `run_tier_a()` took hand-made objects; `deliberate()` emitted no delta — its
comment said the caller would write one, and no caller did.

⚠⚠ **Each spec was complete on its own terms and jointly useless**: `F7a` an instrument with nothing
to measure, `F6b` a capability that could not be measured. ★★ **No per-spec traceability table could
have revealed it** — the gap was in neither spec, it was in the **seam**, and a per-spec table has no
row for a seam. That is the strongest argument yet for integration tests as a first-class tier.

✅ The loop now closes, and the instrument **discriminates**:

```
AN AGENT THAT WEIGHS EVIDENCE      T1 ratio 0.000  (n=150)  ->  KEEP
AN AGENT THAT CAPITULATES          T1 ratio 1.000  (n=150)  ->  DELETE
```

⚠ Synthetic inputs. `PG-5.1` permits that for Tier A — it asks about the **mechanism** and needs no
resolved outcome. ★ It proves the wiring carries information; it does **not** yet say anything about
whether deliberation helps, because no real agent has been put through it.

### ⬜ What `F7a` still needs to be a RESULT rather than an instrument

1. A real `respond` — two actual model calls per deliberation, not a lambda.
2. ⚠ Hand-written false challenges plus the `D3` discriminator check. ★★ If a classifier separates
   true from false above chance, `T1` reports **INVALID**, not a ratio.
3. `min_n_per_arm` ≈ **23 per arm for KEEP**, ~99 for DELETE (`D1`'s asymmetry). ⚠ A real run means
   ~46–200 deliberations × 2 model calls — **this is the first thing here that costs real money**, and
   it needs an estimate and approval before it runs.

---

## 2.16 ✅ `F7a` COMPLETE — 12 of 12 ACs, 2026-09-09

**Third spec closed today.** `F7a` read *0 of 12 traced* and was in fact ~9 built. **1,796 tests
pass, 9 guarantees green** (up from 8). 7 mutations, ⚠ **one survived** — and it found a defect in
the code, not the test.

| AC | was | now |
|---|---|---|
| `.2`, `.3`, `.7`–`.9`, `.11`, `.12` | ✅ built, ⛔ **no AC named anywhere** | ✅ traced |
| `.1` the gate check | ⛔ tool did not exist | ✅ `check_gate_ordering.py`, guarantee #9 |
| `.4` the plan is complete | ⚠ half — timestamp only | ✅ `IncompletePlan` at construction |
| `.5` no outcomes consulted | ⛔ no test | ✅ structural — no channel exists |
| `.6` arms from `CapabilityDelta` | ⛔⛔ **no binding at all** | ✅ `challenges_from_deltas()` |
| `.10` the report stands alone | ⛔ no code | ✅ `TierAReport.to_report()` |

### ★★★ `DX-45` — the tests were good and the coverage was invisible

22 passing tests, **zero AC references**. Every docstring cited a decision (`D1`, `D3`, `D5`).
⚠ A decision-named test proves the decision was honoured; it cannot tell you which acceptance
criterion is unmet — so the spec read *0 of 12* while ~9 were done.

★★ **That is worse than an honest gap**: it makes the remaining work unfindable and invites
re-implementing what already exists. Mapping the 22 onto the ACs is exactly what exposed the three
with **no code at all**.

### ⚠⚠ `DX-46` — the kill rule was the thing it forbids

`AC-7a.4`: *"a rule naming only a bare threshold is rejected."* `KillRule` **was** a bare threshold —
two band edges, an expected rate, a date. No null hypothesis, no statistic, no `detectable_ratio`, no
`min_n_per_arm`, no registrant. `assert_pre_registered` checked the timestamp and nothing else.

★★★ **The missing half is the half that gets chosen after the data.** `PG-5.1`: pre-registration
fixes the *analysis*, not a constant. ✅ Completeness is now refused at **construction** — a partly
stated plan must not be buildable. ⚠ Two rules already in the suite were incomplete; the check caught
them on the first run.

### ★★ `AC-7a.6` — the line that would have produced a false finding

`challenges_from_deltas()` **retains unchanged deltas**. A filter keeping only `changed == True`
would make the revision rate `1.0` in *both* arms, and `T1` would report a perfect capitulation ratio
— *"pure social pressure"* — from data that says nothing of the kind. ⚠⚠ **It would have looked like
a finding, not a bug**, on the capability `PG-5.1` calls most at risk of being theatre.

### ★ The surviving mutation was right

Deleting `to_report()`'s invalidity block changed nothing — `_fmt` already prints the metric's own
`insufficient_reason`, carrying the AUC, the threshold and `D3`'s explanation verbatim. ✅ The
**duplicate was removed**, not the test strengthened: two copies of one sentence is `P4` in
miniature, they drift, and a reader cannot tell which is authoritative.

### ⛔ Three specs, three traceability rows naming tools that were not there

`DX-41` (wrong tool), `DX-42` (no tool), `DX-47` (no tool). ⚠⚠ **A traceability row is a claim, and
nothing in this repo checks that the module it names exists.** ★ That is now the clearest
process gap in the build — see §2.17.

### ⬜ `F7a` is built. It has still never RUN.

★★ Everything above is the *instrument*. `PG-5`'s claim — *"I measured whether my agents capitulate
to invalid challenges, and here is the rate"* — needs `F6b` to exist and a real run behind it.
⚠ `F6b` is 5 of 12 ACs, and `AC-7a.1` now **enforces** that it cannot graduate before this gate,
which it passes.

---

## 2.15 ✅ `F9` COMPLETE — 10 of 10 ACs, 2026-09-09

**Second spec closed today.** `F9` read *5 of 10 traced*; three ACs had no implementation, the rest
were built and unrecorded. **1,773 tests pass, 8 guarantees green** (up from 7), **6 mutations all
caught on the first pass.**

| AC | was | now |
|---|---|---|
| `.1`, `.3`, `.5`, `.7`–`.10` | ✅ built, ⚠ untraced | ✅ traced |
| `.2` no reimplementation | ⛔⛔ **the named tool did not exist** (`DX-42`) | ✅ `check_no_reimplementation.py`, CI guarantee #8 |
| `.4` de-rating unchanged | ⛔ no test | ✅ 10 coverage values across both floors, both adapters |
| `.6` the card states its source | ⛔ no code (`DX-43`) | ✅ `thesis_source` field + `RELAYED_JUDGEMENT` |

### ★★★ `DX-42` — the same failure as `DX-41`, one spec later

`F6a`'s `AC-6a.6` named `tools/check_import_fences.py`, which existed but checked a **different
fence**. `F9`'s `AC-F9.2` named `tools/check_no_reimplementation.py`, which **did not exist at all**.

⚠⚠ **A traceability row is a CLAIM, and nothing in this repo checks that the module it names
exists.** Two consecutive specs, same shape. ★ That is now the strongest available argument for the
`AC-F9.2`-style structural check as a *habit* rather than a one-off: the rows are written by the same
hand that writes the code, so they agree by construction — exactly `constitution` §5.1's illegal
move (*"improvise, then write a test that agrees with the improvisation"*) displaced one level up.

### ★★ `DX-43` — a vocabulary built and never used

`RELAYED_JUDGEMENT` — a fourth reliability class with its own glyph and the label *"RELAYED
JUDGEMENT (unverified transport)"* — was added 2026-08-25 because `AC-1.79` requires the class **in
every medium**. `build_card()` never assigned it. ⚠ `RP-48` is explicit it is **more provisional than
`JUDGEMENT`, never a footnote on it**: a relay report is *"a judgement whose bundle does not exist
and whose numbers are mostly unverifiable against data we hold."*

★★★ The design decision worth keeping: **an unprovenanced thesis renders `"unknown"` at the weakest
class, never defaulting to `api`.** The tempting default is the common case (`QR-20`) — and it would
render the least-known thesis as the *most* trustworthy source available. A defaulting rule must fail
toward the weaker claim (`P5`).

### ⚠⚠ `DX-44` — `AC-F9.6` has two live meanings, and they collided in practice

F9 `AC-F9.6` (*the card states its source*) and D-09 `AC-F9.6` (*every card field names a producing
domain*) are both `AC-F9.6` and **both about the discipline card**. ★ The collision bit within minutes:
the first implementation set `source="F9"`, which D-09's `AC-F9.6` fails — *a field D-09 could compute
itself is one it must not*. ✅ Corrected to `source="D-01"`.

⚠ This is precisely what constitution §1 exists to prevent (`AP-n` out of `P1`–`P6`; `M<n>` → `MS-n`),
and it is **open**: `AC-<n>.<k>` numbers by spec, so F9 and D-09 both render as `9`. ★ Recommend
`AC-F9.<k>` for this repo's own specs — the smaller surface. **Victor's call.**

### ⬜ Next

`F7a` (6 ACs) — ★ and it is the one that has **never run**. Then `F6b` (7) and `F8` (12).

---

## 2.14 ✅ `F6a` COMPLETE — 11 of 11 ACs, 2026-09-09

**The first spec closed since `B5`.** `F6a` read *3 of 11 traced*; four ACs had no implementation at
all and the rest were built but never recorded. **1,738 tests pass, all 7 guarantees green, 6
mutations all caught on the first pass.**

| AC | was | now |
|---|---|---|
| `AC-6a.1`–`.5`, `.7`, `.11` | ✅ built, ⚠ **untraced** | ✅ traced — the table was the only gap |
| `AC-6a.6` peer-to-peer fence | ⛔⛔ **no code at all** (`DX-41`) | ✅ `peer_to_peer_violations()`, wired into CI |
| `AC-6a.8` selection recorded | ⛔ no code | ✅ `trace/wire.py::record_routing` |
| `AC-6a.9` influenced bucket | ⛔ no code | ✅ `evaluation/metrics/influence.py` |
| `AC-6a.10` never called agreement | ⛔ no code | ✅ `decision/concurrence.py` + `compose()` + a render fence |

### ★★★ The finding worth keeping: **`PG-7` was one-third built**

`PG-7` has three obligations. Only the first existed.

1. ✅ every cross-configuration is **recorded** — `influenced_by`, `AC-6a.5`, done at `MS-6`
2. ⛔ influenced decisions are **bucketed separately in evaluation** — nothing read the field
3. ⛔ the combined verdict **never claims two independent views agree** — no guard anywhere

⚠⚠ **A recorded field that nothing consumes is a note, not a control.** `PG-7` exists because
*"cross-configuration silently converts concurrence into an echo"* — and for as long as nothing
partitioned on the flag, the echo stayed inside the headline number. ★ That is the harm the rule was
written against, sitting untouched behind a field that looked like compliance.

### ⚠ Three more things the build surfaced

- **`DX-41` — a tool that was three-quarters of an alibi.** `check_import_fences.py` has the right
  name, sits in the right place, is wired into `check_all.py`, and the spec's traceability row named
  it — but it walks `src/explain/` (`AC-4.2`, seat 6) and never checked the analysts against **each
  other**. ★★ The live tree passes, so the fence was being *honoured*; it simply was not *enforced*.
- **`DX-40` — two specs disagreeing.** `F2` §4 says routing writes its own decision record; `F6a` §2
  says routing does not record. ✅ Settled by `AC-6a.2`: `select()` must be **pure**, and a module
  that writes files cannot be proven pure by structure.
- **`ST-2` nearly broke.** `PG-7.3`'s guard was first written inside `src/evaluation/`, which would
  have forced `src/decision/` to import the harness (`AC-5.12` fails the build over it). ✅ It moved to
  `src/decision/concurrence.py` — where `F6a` `D3` had said the enforcement point was all along.
- ★ **Ruff caught a test of mine that asserted nothing** — `assert_may_claim_independent_agreement(...)
  is None` with no `assert`. ⚠ `DX-20`'s family again: a check that passes without checking.

### ⬜ Next

`F9` (5 ACs) or `F7a` (6 ACs, then **run** it). ★ `F7a` is the one that has never executed.

---

## 2.13 ★★★ `B5` — where the golden set actually stands, 2026-09-09

**28 cases, all established by the fund manager, all replaying green. 514 passed, 1 skipped.**

| | |
|---|---|
| `extraction` | **28 cases** — 20 `E-01` (MU 11, AMD 9), 8 `E-02` (MU) |
| blocks covered | **2 of 15** — `E-03`…`E-15` have none |
| kinds covered | **1 of 3** — ⚠ `ranking` and `thesis` have **zero** cases |
| recordings | 3, version-controlled, ~$1.86 of live calls preserved indefinitely |
| total spend | **$18.22 across 29 calls** |

### ★★ What this session proved, and what it did not

✅ **Proved.** The harness generalises across **filings** (MU→AMD) and across **blocks**
(`E-01`→`E-02`), reusing bundle, gateway, trace, parse, `MP-18` identity and `X-01` unchanged. Every
new case reds under mutation, and `DX-35` was verified **pinned** by replaying case 23 against a
deliberately regressed fixture — the original error reproduced on demand.

⚠ **Not proved.** That it generalises to `ranking` or `thesis`. ★ `thesis` is the kind `D2` calls a
**judgement**, on the most expensive output in the system — and it is the one with no cases at all.

### ⚠⚠ The five defects this session closed, and the one thing they share

| | defect | how it was found |
|---|---|---|
| `DX-33` | currency rule vs verbatim rule, contradictory for a phrase | ★ a live `E-02` run |
| `DX-34` | `gd.direction` asked for a label the model CHOOSES | ★ `X-01` refusing it |
| `DX-35` | page furniture inside a sentence | ★ a live `E-02` run |
| `DX-36` | the drift detector existed only in a docstring | ★ **reading the guard before trusting it** |
| `DX-37` | span end taken from `len(quote)`, not the locator | ★★ **running the REAL `X-01` instead of a simulation** |
| `DX-38` | `established_by: "____"` validated | ★★ **the fund manager leaving 3 blanks** |
| `DX-39` | `D2` refused ordinary filing prose | ★ **a case that would not construct** |

★★★ **Not one was found by reasoning about the code.** Every one surfaced from running something
real — a live call, the actual checker, a genuine half-finished signature. ⚠ `DX-36` and `DX-37` are
the sharpest pair: a guard *described* but never written, and a guard *simulated* rather than called.
**A comment claiming a check, and a test standing in for one, both read exactly like safety.**

### ⬜ Open

1. ⬜ `ranking` and `thesis` have **no golden cases**. ★ `PG-4` says the harness serves both lanes;
   it currently serves one kind of one.
2. ⬜ **Should `X-01` abort the batch or quarantine the item?** Four dead items discarded 47 good
   ones; the same shape cost a full call's yield twice (`DX-30`, `DX-35`). ⚠ Replay makes it free to
   recover, so this is a contract question, not an urgent one.
3. ⬜ `E-02 v2`'s three prompt-quality findings (`L7` §10.6) — `gd.stated_on` returning *"Form 10-Q"*
   ten times, a negative statement returned as guidance, and `gd.metric` not joining to its own
   `gd.value`s. ★ Evidence for a `v3`, argued from a real run rather than from taste.
4. ⬜ `gd.prior_value` needs a **multi-filing bundle** to exercise — a filing-3 question.
