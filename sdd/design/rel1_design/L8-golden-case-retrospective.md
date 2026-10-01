# L8 — The golden case programme: full history, retrospective, and what remains

> **Status:** ✅ **CLOSED 2026-10-01 by a recorded decision of the fund manager — see §9.** No new golden
> cases are developed. The 53 live cases stay live and are maintained, never deleted.
> ⓘ Was: ⏳ LIVING RECORD — keep updating until the golden set is complete.
> Opened 2026-09-17 at Victor's instruction, after a session that asked whether the programme
> should be stopped entirely.
> **Purpose:** so that a future planning decision about golden cases is made against the *measured*
> history of what they cost and what they caught — not against anyone's memory of it.
> **Audience:** Victor, and any session asked *"should we keep doing golden cases?"* or
> *"how much is left?"*
>
> ★ **Companion documents.** `L7-golden-set-filing-1.md` is the *mechanics* of filing 1 — what must
> not be changed to make another filing pass. This file is the *programme*: history, money, and plan.
> `L3-build-sequence.md` holds the authoritative `DX` findings table; this file cites it, never
> duplicates it.

---

# 0. ⚠⚠ The update rule

**Every time a golden case is established, withdrawn, re-pointed or invalidated, add a row to §7 and
re-measure §5.** A retrospective that stops being updated becomes a story about the past instead of a
record of it, and the whole reason this file exists is that *nobody could answer "what have golden
cases actually cost us" from memory* when the question was asked on 2026-09-17.

The file is complete — and may be closed — when §5's "Level 1" inventory reaches every declared
block, or when the programme is formally abandoned by a recorded decision.

---

# 1. What a golden case is, and the distinction that matters most

A golden case is a **recorded, replayable claim that a named human believes a specific pipeline output
is correct.** `F5` `CT-5.2` gives it five parts: an `input_ref` pointing at an `F2` recording, an
`expected` value, a `source`, an `established_by` naming a *person*, and a `kind`.

★★ **The programme bundles three separable activities, and conflating them is what made it look
more expensive than it is.**

| | Activity | What it costs | Who does it |
|---|---|---|---|
| **A** | **Recording** — every live call persisted to `.state/runs/<run_id>/trace.jsonl` | **$0** — automatic, already built, happens whether or not a case is ever written | the machine |
| **B** | **Establishing** — a human reads the output and signs a value | **time** — the true bottleneck | ⚠ Victor **only** (`D2`) |
| **C** | **Replaying / gating** — CI re-grades the set on every change | ~0 (no network) | the machine |

⚠ **A is what makes B possible later.** A golden case is established *from a recording*. As long as
recording continues, establishment can be deferred to any future date **at zero API cost**, because
the calls are already bought and on disk. If recording ever stops, deferral means re-buying them.

★ This is the single most important planning fact in this document.

---

# 2. Why the programme exists — the three defects it was built to catch

Not theory. Each had already happened in the predecessor repo or in this one.

1. **`_cumulative_fys`** — understated Micron's TTM revenue by **41.5%** and moved fair value by
   **$379/share**. It survived review because a docstring asserting the wrong rule had a *passing test
   built on real production numbers*. ⇒ A test can be green and wrong; a golden case anchored to a
   filing's actual words cannot be green and wrong in the same way.
2. **FMP's quarter guessing** — off by **71%** on MU, because FMP exposes only period *end* and must
   infer discrete-vs-cumulative. Detectable only against ground truth.
3. **Silent prompt drift** — the reason the set is anchored to recordings rather than to live calls.
   A prompt edit changes output in ways that still *look* plausible. Nothing else in the repo detects
   this: the type checker cannot, the unit tests cannot, and a human reading one output cannot.

⇒ **The golden set is the only instrument in the repo that answers *"did this change make the answer
worse?"*** That is its whole claim to budget, and it should be judged on it.

---

# 3. Full chronological history

All costs measured from traces by `tools/spend_report.py`, not estimated.

## Phase 1 — the harness exists but nothing can be graded (2026-09-05 → 09-07)

| Date | Event | `DX` |
|---|---|---|
| 09-05 | `CT-5.5` gives the golden set **a place to live**; `run_regression(cases, replay_response)` can grade an `input_ref` against a recording | `DX-21` |
| 09-05 | `F5`'s `extraction` kind is pointed at the E-block runner's output — fixing *which producer* the set grades | `DX-23` |
| 09-07 | `AC-5.18` wires `input_ref` → recorded response → `==` against `expected`; the four adversarial checks in `review_golden_case.py` pass | `DX-25` |
| 09-07 | ⚠ `CT-5.2` validation lands: `source`, `established_by` and `expected` all **refuse a blank**. Correct — but it means one unsigned draft in the live file stops **every** case loading | `DX-28` |

★ `DX-28` is the origin of the `*.pending.yaml` convention: a case in preparation lives in the pending
file and is **moved** — never copied — into the live file when signed.

## Phase 2 — filing 1 goes green (2026-09-07 → 09-08)

**Filing 1 (Micron FY2025 Q3 10-Q) cost $11.93 across 20 live calls and produced 29 recorded
findings.** ⚠ **Almost every finding was a defect in the *plumbing*, not in the model** — and several
were *caused by fixing something else*. Full mechanics in `L7-golden-set-filing-1.md`.

| Date | Spend | Calls | What it bought |
|---|---|---|---|
| 09-07 | **$10.85** | 17 | filing 1's `E-01` runs and the ten cases that first went green |
| 09-08 | **$5.63** | 8 | ★ **filing 2 (AMD)** — a second filing's cases, the first generalisation test |

★ Adding AMD immediately justified itself: `DX-70` exists because *"AMD's cases were being checked
against Micron's filing"* — a whole class of defect that a single-ticker set could never have shown.

## Phase 3 — a second BLOCK, and the establishment guards bite (2026-09-09)

| Date | Spend | Event | `DX` |
|---|---|---|---|
| 09-09 | **$1.28** (2 calls) | `E-02` runs live — the first cases for a second block; everything before graded `E-01` only | `DX-33`…`DX-37` |
| 09-09 | — | ⚠⚠ A case drafted straight into `thesis.yaml` with `established_by: '____'` cascaded into **9 failures and 3 errors**. ★ The guard was right; the file was wrong | `DX-38` |
| 09-09 | — | `D2` hardened: `established_by` may not name a pipeline component, enforced by substring scan of both `established_by` *and* `source` | `DX-39` |

## Phase 4 — ★★ the re-record, and the most expensive lesson (2026-09-10 → 09-11)

| Date | Spend | Event | `DX` |
|---|---|---|---|
| 09-10 | — | ⛔ The `ranking` golden kind is **REMOVED**: deterministic code emits no `ExternalCall` payload, so an `input_ref` has nothing to resolve to. A retrain-regression target has no home in `F5` | `DX-62` |
| 09-10 | — | `test_the_golden_set_is_not_silently_empty` added — an empty baseline must not report green forever | `DX-63` |
| 09-10 | — | ⚠ **No thesis case could exist at all**: `e_blocks.py` shipped `E-01`/`E-02` while `STAGE_BLOCKS` named `J-01`…`J-17`, none with prompt text. `author_once` could construct nothing | `DX-64` |
| 09-11 | **$6.44** | 12 | ★★ **The re-record day.** All four graded calls re-run under the shared envelope (`DX-67`), `E-01 v4` to restore `period.start` (`DX-68`, `DX-73`), `E-02` re-recorded (`DX-69`, `DX-77`) | |
| 09-11 | — | ⚠⚠ **`DX-76` — the envelope is UNVERSIONED.** A recording from a retired prompt version is not detectable from the recording itself. **Eight cases were withdrawn and re-established** rather than rebaselined | `DX-71`, `DX-76` |

★★★ **This is the retrospective's central finding, and it should drive the plan.** Establishing cases
against prompts that are still changing means paying for them **twice** — once to record, once to
re-record — and re-establishing by hand each time. The $6.44 and the eight withdrawn cases are the
measured price of signing too early.

## Phase 5 — the analysis layer swallows the budget (2026-09-12 → 09-17)

⚠ **From here on, almost nothing is golden-case cost.** The money goes to making the prompt blocks
*work at all* — truncations, thinking runaways, schema failures.

| Date | Spend | Calls | What it was |
|---|---|---|---|
| 09-12 | **$13.29** | 23 | seven E-block runs + Stage A (⚠ `DX-84`'s truncated Stage A: **$3.68** wasted) |
| 09-13 | **$12.57** | 16 | `J-05`/`J-06` rubric work, `DX-96`'s `E-09` truncations (**$4.39**), a VOID blind-criteria run |
| 09-14 | **$0.50** | 1 | `J-20` |
| 09-15 | **$17.45** | 17 | ★ the first complete thesis (**$5.33 lost** to three failed calls) |
| 09-16 | **$2.79** | 5 | industry evidence (**$1.88 lost** to three failed `E-13` attempts) |
| 09-17 | **$1.17** | 2 | `E-09` solved at `--effort low` ($0.42) · `J-04` scored ($0.75) ⇒ coverage **1.000** |

## ★ Spend attribution — the question that prompted this file

| Category | Amount | Share |
|---|---|---|
| **Purely golden-attributable** (filing 2's cases 09-08; the re-record day 09-11) | **~$12.07** | **17%** |
| **Mixed** (filing 1 and `E-02` — first runs of blocks that had to work regardless, which also produced the cases) | ~$13.21 | 18% |
| **Block development** (09-12 → 09-17: truncations, runaways, the thesis) | ~$47.13 | 65% |
| **Total measured** | **$72.41** over 105 calls | |

⚠ **Correction to a claim made in conversation on 2026-09-17.** I first said stopping golden cases
would save *"roughly $0"*. The measured figure is **~17%, not 0%** — real, and worth naming. The
substantive point survives: the majority of spend was prompt engineering that would have been paid
with no golden set in existence. ★ But *"roughly $0"* was an overstatement and is corrected here.

⚠ Also note: **~$20 of the $72 (28%) was outright waste** — truncations and failed calls, each
recorded as its own `DX` row. That is the largest single cost category in the project and it is not
golden cases.

---

# 4. What the programme has actually caught

The honest ledger, because a programme should be judged on its catches.

| Caught | How |
|---|---|
| **`DX-70`** — AMD's cases were graded against **Micron's filing** | only visible with a second ticker in the set |
| **`DX-68`** — `E-01` lost `period.start`, making discrete-vs-cumulative undecidable (the `_cumulative_fys` defect class, live again) | a case whose selector embeds `MP-18` identity stopped resolving |
| **`DX-76`** — recordings carry no prompt version, so a retired prompt is undetectable | cases silently grading a stale recording |
| **`DX-62`** — deterministic outputs have **no home in `F5`** at all | attempting to write a `ranking` case |
| **`DX-64`** — no thesis could ever be recorded; `STAGE_BLOCKS` named blocks with no prompt text | attempting to write a `thesis` case |
| **`J-07`** — the model says `mid` cycle position, Victor says `late` | ⛔ **red on purpose since 2026-09-13** — a measured disagreement between model and fund manager, which is exactly what the instrument is for |

★★ Four of these six are defects **in the harness and the pipeline**, found only because someone tried
to write a case. ⚠ **None of them is a model-quality finding.** After 33 cases the set has caught many
plumbing defects and exactly **one** substantive disagreement with the model (`J-07`).

⇒ **The fair verdict: so far the golden programme has been an excellent *integration* test and an
unproven *quality* instrument.** It has not yet been used for the thing it was built for — detecting
regression across a prompt or model change — because no prompt or model change has yet been graded
through it. That is not evidence it fails at that job; it is evidence the job has not started.

---

# 5. ⏳ Current inventory — measured 2026-10-01

## Cases on disk

| File | Live cases | Note |
|---|---|---|
| `tests_src/fixtures/golden/extraction.yaml` | **48** | `E-01` `E-02` + ✏ 2026-10-01: `E-04` `E-06` `E-07` `E-09` `E-10` `E-12` `E-13` (22 signed) |
| `tests_src/fixtures/golden/thesis.yaml` | **5** | `J-01` archetype · `J-05` · `J-06` · `J-07` ⛔red · `J-08` |
| `tests_src/fixtures/golden/extraction.pending.yaml` | **0** | ✅ all 22 signed and moved 2026-10-01 |
| `tests_src/fixtures/golden/thesis.pending.yaml` | **10 unsigned** | 2 older (`J-20` method, `J-09` widest gap) + 8 L1a (`J-03` `J-04` `J-09` `J-10` `J-14` `J-16` `J-17` `J-20`) |
| **Total live** | **53** | 52 pass · 1 red (`J-07`, deliberate) |
| **Total drafted, unsigned** | **10** | thesis only; each needs the fund manager's `expected` |

✅ **What the two rulings moved, 2026-10-01:**

| Ruling | Pending cases re-pointed | Signed cases moved |
|---|---|---|
| **`DX-131`**: an unstated period date is cleared in the parse | **5**: `ca-capex-incentives-ytd` `ca-buyback-none-ytd` `ap-reclassifications` `sc-basic-weighted-shares-ytd` (start → null) · `cp-capex-commitment` (period → null) | none |
| **`DX-135`**: an absence keeps its qualifier | **1**: `dm-headroom-absent` | **2, withdrawn to pending**: `seg-assets-not-disclosed` (re-pointed) · `gd-prior-value-absent` → split into `…-capex-absent` + `…-etr-absent` |

## Block coverage — the real measure

**35 prompt blocks exist** (15 `E` + 20 `J`). Of these:

| State | Count | Blocks |
|---|---|---|
| ✅ **Graded** (≥1 signed golden case) | **7 (20%)** | `E-01` `E-02` `J-01` `J-05` `J-06` `J-07` `J-08` |
| ★ **Recorded but ungraded** — *a case costs $0 in API* | **20** | `E-04` `E-06` `E-07` `E-09` `E-10` `E-12` `E-13` · `J-02` `J-03` `J-04` `J-09` `J-10` `J-11` `J-12` `J-13` `J-14` `J-15` `J-16` `J-17` `J-20` |
| ⬜ **Undeclared and never run** | **8** | `E-03` `E-05` `E-08` `E-11` `E-14` `E-15` · `J-18` `J-19` |

★★ **20 blocks already have a complete recording on disk.** Establishing cases for them requires
**no API spend at all** — only Victor's reading and signature. This is the cheapest available
progress in the entire programme and it has never been harvested.

## Ticker coverage

| Ticker | Blocks graded | Recordings |
|---|---|---|
| MU | 7 | 27 blocks |
| AMD | 1 (`E-01` only) | 1 block |

⚠ **Generalisation is essentially untested.** `DX-70` was caught the moment a second ticker appeared;
with 1 of 35 blocks graded on AMD, that class of defect is wide open on the other 34.

## Structural gaps that no amount of signing will close

- **`DX-62`** — deterministic outputs (the ranker, the valuation arithmetic) have **no golden kind**.
  `input_ref` requires an `ExternalCall` payload and code emits none. ⇒ The quant seat cannot be
  golden-tested in the current `F5` design at all. **Unresolved.**
- **`CT-9.2` k=3 is unmet.** `K_RUNS = 3` in `author_for.py`; every thesis so far is **k=1**.
  ⚠⚠ Consequence beyond the golden set: `thesis/gate.py::_agreement` returns `None` at k=1, and the
  gate reads `if agreement is None or agreement >= FLAG_FLOOR: PASS` — so **the stability check is
  silently skipped in the daily run**, not failed. A k=1 thesis passes the gate by absence of
  evidence.
- **`DX-76`** — the envelope is still unversioned; a prompt bump can invalidate cases again.

---

# 6. ⊘ What remained, and what it would have cost — SUPERSEDED by §9

> ⊘ **Kept for the record, no longer a plan.** §9 closes the programme. The estimates below are what
> was turned down, and they are why the decision was cheap to make.

## The three levels of "complete"

| Level | Definition | Why you would want it |
|---|---|---|
| **L1 — block coverage** | every declared block has ≥1 case on MU | regression detection across prompt edits |
| **L2 — generalisation** | every block also graded on AMD | catches the `DX-70` class; proves the module is not Micron-shaped |
| **L3 — reproducibility** | a k=3 thesis, so `CT-9.2` is met and `_agreement` is computable | un-blinds the thesis gate in the daily run |

## Money — measured rates, not guesses

> ✏ **2026-10-01 — development calls now run on the subscription** (`L3` §2.1o, `GW-24`…`GW-29`). Every
> "API cost" below is now **subscription usage at $0 API**, and the binding constraint becomes the
> **Pro plan's usage limits**, not dollars. ⚠ One cost is new: before the daily runs go live, a sample
> of signed cases must be re-run through the API, because a `claude_code` recording grades the prompt,
> not the production transport.

Observed unit costs: extraction block **~$0.42–0.88** (mean ≈ $0.60) · judgement block **~$0.61–0.88**
(mean ≈ $0.75) · full Stage B–D thesis **$11.38 with caching** (measured $16.93 uncached).
⚠ **Apply a 40% margin**: 28% of all spend to date was failed calls, and every new block is a fresh
chance at a truncation.

| Item | API cost | Victor's time |
|---|---|---|
| **L1a** — sign the **20 recorded-but-ungraded** blocks (~2–3 cases each ⇒ 40–60 cases) | **$0** | **10–20 h** |
| **L1b** — declare + run the **8 remaining blocks** (8 × ~$0.70) | ~$5.60 → **~$8 with margin** | +2–4 h signing |
| **L2** — AMD: fact-ledger ingest (EDGAR, free) · 9 extraction runs (~$5.40) · 8 Stage-A runs (~$6.40) · one Stage B–D thesis ($11.38) | ~$23.20 → **~$32 with margin** | 8–15 h |
| **L3** — k=3: two extra Stage B–D passes per ticker (2 × $11.38 × 2 tickers) | ~$45.50 → **~$64 with margin** | 2–4 h |
| **Contingency** — one forced re-record if a prompt version bumps mid-programme (`DX-76` precedent: $6.44 + 8 cases withdrawn) | ~$7 | 2–4 h |
| **TOTAL, all three levels, two tickers** | **≈ $111** | **≈ 24–47 h** |

## ✏ 2026-09-17 — L1a ran, and the estimate above needs two corrections

**24 cases drafted, $0 spent, 10 recordings promoted.** But drafting them found four defects, and two
of them make the L1 estimate **worse**, not better:

| Finding | Effect on the plan |
|---|---|
| **`DX-131`** — `E-07` `E-09` `E-10` emit a nine-month `period.start` of `2024-08-30`, a date the filing never states (`DX-73`'s fix was applied to `E-01` only) | ⛔ **4 of the 16 extraction drafts cannot be signed** until it is ruled on. A prompt fix plus a re-record of those three blocks is ≈**$1.50** |
| **`DX-133`** — promotion's unit is the RUN, so promoting for `J-13` also dragged in a truncated `J-14`; both affected runs were un-promoted | ⛔ **`J-12` and `J-13` are ungradeable** — they need a clean re-record, ≈**$1.86** |
| **`DX-134`** — the only promotable `J-11` recording contains a leaked `<parameter name="reason">` fragment inside its answer | ⛔ **`J-11` excluded**; blocked twice over, since its clean recording is in an un-promoted run |
| **`DX-132`** — `promote_recording` cannot promote a sector-bundle recording | ✅ **FIXED same day, free.** `E-13` promoted, 3 cases drafted |
| **`DX-135`** (found closing `DX-132`) — the parse blanks `qualifier` on an ABSENT item, so `E-13`'s five recorded absences collapse to three anonymous rows and two vanish | ⛔ **No `not_found` cases for `E-13`**, and ⚠ it must be ruled on **before** the four absence cases already drafted (`dm.headroom` `ap.icfr` `ng.measure` `ca.capex`) are signed — a fix changes their identity |

⇒ ★ **L1a is not "20 blocks for $0" — it is 15 blocks for $0 and 5 blocks for ≈$3.40 plus one code
fix.** The revised L1a line: **$0 API for the 27 drafted cases**, then ≈**$3.40** and ~1 h of
engineering to unblock `J-11` `J-12` `J-13` and the four `DX-131` cases. (`E-13` left that list the
same afternoon — `DX-132` was a 40-line change, and it is now the 15th block drafted.)

★★ **A ruling you owe before signing anything, not after.** `DX-135` asks whether an ABSENT item
keeps the qualifier that says what it is absent *about*. Answering it changes the identity — and so
the `input_ref` — of the four absence cases already drafted (`dm.headroom`, `ap.icfr`, `ng.measure`,
`ca.capex`). ⚠ Signing them first and fixing afterwards is the `DX-76` re-record cycle in miniature,
which §8 lesson 1 exists to stop.

★★ **And this is the programme justifying itself in a way §4 said it had not yet.** Four defects in
one afternoon, at zero API cost, none of which any test would have caught — `DX-131` in particular is
the *third* recurrence of "a general fix applied to one block only" (`DX-115`, `DX-129`, now this).
⚠ They remain **plumbing** catches, not model-quality catches; §4's verdict stands, but the
integration-test value is now measured rather than asserted.

### ★ The cheap subset, if the budget is the constraint

**L1a alone — $0 API, 10–20 hours — takes block coverage from 20% to 77%.** It needs no approval, no
spending decision and no new code. It is, by a wide margin, the best value in the programme, and it is
available today.

## ⚠⚠ The sequencing rule this history argues for

**Do not bulk-establish until the prompts stop changing.** The measured precedent is `DX-76`: eight
cases withdrawn and $6.44 re-spent because signing happened while the envelope was still moving.
Eight blocks are still undeclared and `E-13 v2` / `J-15 v2` are both known-wanted revisions — so the
prompt surface is *not* stable today.

⇒ ★ **The evidence in this file supports deferring bulk establishment until the block set is
declared and frozen** — which is materially the same conclusion Victor reached independently on
2026-09-17 for schedule reasons. **The two arguments agree.** The one thing that must not be deferred
with it is **recording (activity A)**, which costs nothing and is what keeps the option alive.

---

# 7. ⏳ Update log

| Date | Change | Live cases | Block coverage | Golden-attributable spend |
|---|---|---|---|---|
| 2026-09-08 | filing 1 green (10 cases); filing 2 (AMD) added | 10 → ~18 | `E-01` | $5.63 |
| 2026-09-09 | `E-02` cases; `DX-38`/`DX-39` establishment guards | ~18 → 26 | `E-01` `E-02` | $1.28 (mixed) |
| 2026-09-11 | ⚠ re-record; **8 cases withdrawn and re-established** under the shared envelope | 26 → 28 | unchanged | $6.44 |
| 2026-09-12 | `J-01` thesis case moved onto the complete Stage-A recording | 28 → 29 | + `J-01` | $0 |
| 2026-09-13 | `J-05` `J-06` `J-08` established; ⛔ `J-07` **re-established by Victor against the recording** — red on purpose | 29 → 33 | + `J-05` `J-06` `J-07` `J-08` | $0 |
| 2026-09-17 | L8 opened. Inventory measured: 33 live · 7/35 blocks graded · **20 blocks recorded but ungraded** | 33 | 7/35 (20%) | cumulative ~$12.07 |
| 2026-09-17 | ✅ **`DX-133` FIXED, $0 spent** — promotion is now PER-CALL: it refuses a run containing a `stop_reason: max_tokens` call, and `--skip-truncated` promotes the complete calls beside it while naming the omissions in `excluded.json`. ⇒ **`J-11` `J-12` `J-13` unblocked without a re-record** (their clean recordings were already paid for). ⛔ `DX-135` investigated and NOT fixed: it would break 2 of the 3 signed absence cases | 33 live + 27 pending | 7/35 signed · **25/35 addressable (71%)** | **$0** |
| 2026-09-17 | ✅ **`DX-132` FIXED, $0 spent** — `promote_recording` gained a sector branch, `E-13` promoted at last, **3 more cases drafted**. ⚠ Found `DX-135` on the way: absent items lose their competitor, so no `not_found` case is draftable for the industry block | 33 live + **27 pending** | 7/35 signed · **22/35 drafted or signed (63%)** | **$0** |
| 2026-09-17 | ★★ **L1a started, $0 spent.** 10 recordings promoted to version-controlled fixtures; **24 cases drafted unsigned** (16 extraction across `E-04` `E-06` `E-07` `E-09` `E-10` `E-12`; 8 judgement across `J-03` `J-04` `J-09` `J-10` `J-14` `J-16` `J-17` `J-20`). All 24 resolve through `golden_replay`, each selector matches exactly one item, and all 16 extraction cases go red under mutation. ⚠ 4 surfaced findings — `DX-131`…`DX-134` | 33 live + **24 pending** | 7/35 signed · **21/35 drafted or signed (60%)** | **$0** |
| 2026-10-01 | ✏ **Inventory re-measured, $0.** `DX-137`: both pending files repeated their top-level `cases:` key, so a loader saw 11 of 29 drafts. Merged, verified identical to `HEAD`, guarded by a test. True unsigned count **29**. `DX-131` measured wider (5 cases, a 4th block `E-12`, root cause in the shared envelope); `DX-135` measured narrower (1 drafted + 2 signed cases move). ★ Dev calls move to the subscription (`L3` §2.1o) | 33 live + **29 pending** (23 signable now) | 7/35 signed · 22/35 drafted or signed | **$0** |
| 2026-10-01 | ✅ **`DX-131` + `DX-135` ruled (Victor) and built, $0.** Unstated period dates cleared in the parse; absences keep their qualifier. 5 + 1 drafts re-pointed; 2 signed cases **withdrawn** to pending, one split in two. All 48 extraction cases resolve and match | **31 live + 32 pending, all signable** | 7/35 signed (unchanged: `E-01` `E-02` keep other signed cases) | **$0** |
| 2026-10-01 | ★★ **22 extraction cases SIGNED by Victor Truong and moved live** (16 L1a + 3 `E-13` + 3 `DX-135` re-signs). Every one verified against its recording before the move; no `expected` changed. Live set replays 52/53 (`J-07` red on purpose) | **53 live + 10 pending (thesis)** | **14/35 (40%)**: + `E-04` `E-06` `E-07` `E-09` `E-10` `E-12` `E-13` | **$0** |
| 2026-10-01 | ✅ **PROGRAMME CLOSED by decision (§9).** No new golden cases. Extraction finished at 48; thesis frozen at 5 signed + 10 unsigned drafts kept; judgement moves to falsifiers and rule checks. Nothing deleted | **53 live (final)** | **14/35 (final)** | **$0** |
| 2026-10-01 | ⊘ **Frozen per company (§9 rule 6):** MU 39 extraction + 5 thesis live, 10 drafts frozen; AMD 9 extraction live. ★ The replacement's first instrument is built: `tools/rule_checks.py` over all 45 recorded calls, 4 known violations (`DX-84` `DX-134` `DX-138` ×2), wired into `check_all.py` (`L3` §2.1p) | 53 live (final) | 14/35 (final) | $0 |

---

# 8. Retrospective — what to do differently

1. ★★ **Sign late, record always.** Establishment is free to defer and expensive to redo; recording is
   free to keep and expensive to recreate. The programme paid $6.44 and lost eight cases learning this.
2. ★ **Harvest existing recordings before buying new ones.** 20 blocks sat recorded-and-ungraded while
   new live calls were being bought. Nobody checked the inventory.
3. **A second ticker earns its cost immediately.** `DX-70` was invisible until AMD existed. One
   filing's cases cannot tell you whether the code is about the filing or about the company.
4. ⚠ **Distinguish plumbing catches from quality catches when reporting value.** 4 of 6 catches were
   harness defects. Reporting them as *"the golden set caught six defects"* overstates the instrument's
   proven value at its actual job.
5. **Version the envelope.** `DX-76` is still open and is the live re-record risk on every future
   prompt edit.
6. ★★ **Drafting a case is the cheapest defect detector this project has.** Measured 2026-09-17:
   **five findings** (`DX-131`…`DX-135`) in one afternoon at **$0**, none of which any existing test
   would have caught, three of them (`DX-132`, `DX-133`, `DX-135`) invisible until someone tried to
   *address* a recording rather than read it. ⇒ Where a block is cheap to draft against, draft it —
   the case is a by-product; the interrogation is the value.
7. ⚠⚠ **`DX-12`'s shape has now appeared four times** — a check that skips, a check never written, a
   recording under `.state/`, and an ingested sector file under `.state/`. Each time the symptom is
   *"it works here"*. ⇒ Anything a golden case resolves through must be version-controlled, and that
   should be asserted by a test rather than remembered.
8. ⚠ **`k=1` is not just an unmet spec line** — it silently disables the thesis gate's stability check
   in production. A spec gap that degrades a *runtime* guard should be tracked as a defect, not as
   scope.
   ✅ *Fixed 2026-10-01 (`RA-154`, `L3` §2.1p item 2): an unmeasured verdict now FLAGS at the gate.*

---

# 9. ✅ DECISION 2026-10-01 — the programme is CLOSED

> **Decided by:** Victor Truong (fund manager), 2026-10-01. **Recorded by:** Claude, at his instruction.
> This is the *"formally abandoned by a recorded decision"* exit that §0 names.

## The decision

| # | Rule |
|---|---|
| **1** | ★ **No golden case is developed from today.** No new drafts, no new recordings made in order to draft one, no signing sessions. This covers extraction and thesis alike |
| **2** | ★ **Extraction is finished at what is signed: 48 live cases over 9 of 15 E-blocks** (`E-01` `E-02` `E-04` `E-06` `E-07` `E-09` `E-10` `E-12` `E-13`). Blocks without cases (`E-03` `E-05` `E-08` `E-11` `E-14` `E-15`) are covered by the rule checks in rule 4, not by golden cases |
| **3** | ★ **Thesis cases are frozen**: the 5 signed cases (`J-01` `J-05` `J-06` `J-07` `J-08`) stay live, and the 10 drafts in `thesis.pending.yaml` stay **unsigned and unused**, kept as a record |
| **4** | ★★ **Judgement quality moves to two instruments:** ⓐ **falsifiers**, meaning a thesis's own stated conditions checked against later filings (`RM-13`, `tools/check_falsifiers.py`), the only check that has ever shown a thesis to be wrong; ⓑ **rule checks**, meaning properties every recorded call must satisfy whatever its answer: refuse on a declared-absent input, cite only what resolves, carry no computed date, no leaked tool syntax, agree with itself across k runs |
| **5** | ★ **Nothing is deleted.** The 53 live cases keep running in `test_golden_regression.py` and are **maintained**: when code changes their identity (as `DX-131`/`DX-135` did), they are re-pointed, and a value change goes to the fund manager. The harness (`F5`), the recordings and every pending file stay |
| **6** | ★ **Frozen for BOTH companies** (Victor, 2026-10-01). **Micron:** 39 extraction + 5 thesis live, 10 thesis drafts frozen. **AMD:** 9 extraction live (`E-01` only), no thesis cases. ⚠ AMD stays at `E-01`: the second-ticker work in `L3` §2.1p item 8 is judged by rule checks and falsifiers, and adds no golden cases |

## Why — measured, not felt

1. **The replay grades STORED answers.** `golden_replay` re-reads `tests_src/fixtures/recordings/` and
   never asks the model, so a golden case catches changes in our CODE (parse, dates, qualifiers) and
   **cannot judge a prompt change** without a re-record and a fresh human reading. ⇒ It is a parser
   regression net, which the 48 extraction cases already are.
2. **k=1 noise.** Two runs of one prompt 82 minutes apart differed in whether a field existed
   (`DX-74`), and every thesis is k=1. A red judgement case cannot separate a worse prompt from a
   different draw.
3. **A judgement case measures agreement with one reader, not correctness.** `J-07` has been red since
   2026-09-13 because the fund manager holds `late` and the model `mid`; neither has been shown right.
4. **It does not see the failure that mattered.** The first MU thesis was wrong by its own falsifiers
   (#1 and #2 FIRED, `DX-128`). Every golden case would have stayed green.
5. **Its catches were plumbing.** §4: 4 of the first 6 catches were harness defects, and the
   2026-09-17 finds (`DX-131`…`DX-135`) were the same kind. Those are worth having, and the 48 cases keep
   catching them. Rule checks catch the same class across *every* block without a signature.

## What the decision does NOT change

- ⚠ **`J-07` stays red, on purpose.** Freezing keeps it live, so `test_ac_5_7_the_golden_set_replays_green`
  and `check_all.py` keep reporting one failure. ⬜ The fund manager may later re-establish it or move
  it to `thesis.pending.yaml`. Either is a `D2` act, not a cleanup.
- `F5`'s acceptance criteria stay met. They specify the harness, not a coverage target.
- The pre-launch **API spot-check** (`CLAUDE.md`) now applies to the 53 live cases only.

## Remaining work under this decision

| Item | Golden-case work left | Was (§6) |
|---|---|---|
| Golden programme | **none** | ≈24–47 h of the fund manager's time, ≈$111 (now subscription) |
| Maintenance | re-point live cases when a parser change moves their identity; ~0–1 h per event | — |
| Replacement instruments | built under `L3` §2.1p, not here | — |

