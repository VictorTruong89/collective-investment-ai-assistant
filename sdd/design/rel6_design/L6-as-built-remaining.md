# L6: As-Built Remaining — what Release 6 hands to Release 7

> **Tier:** `sdd/design/rel6_design/` — design tier.
> **Distinct from [`L5-inherited-defects.md`](L5-inherited-defects.md):** L5 records what the
> **pre-SDD `pipeline/` tree** left behind. This file records what **Release 6 itself** leaves
> behind — things built, measured, understood, and deliberately not finished.
> **Family:** `AB-n`.

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-08-27 | Victor | ★ Created. **AB-1/AB-2 postponed by decision** — *"Solving this needs certain mathematical consideration, logic/algorithm reconsideration and experiment"* (Victor, 2026-08-27). ⚠ **`CONFIDENCE_FLOOR` deliberately NOT set to `-1`** — the proposal was raised and withdrawn on evidence: the constant is **live in the relay path** and `-1` would disable the relay's only safety mechanism silently. AB-3…AB-8 registered from the same session's findings. |
| 0.15.0 | 2026-08-28 | Victor | ★★★ **Every event class is now accounted for — 5 → 15 CHECKED of 18** (AB-14 ingest CLOSED; the cron period stays Victor's, and **DE-72 cadence** makes that choice non-blocking). Built: classes 7, 11, 13, 14, 15, 16. ★★ **Classes 4, 7 and 11 share ONE EDGAR pass.** ⚠⚠ *Measured:* **`grades` ignores `limit` entirely** — ~900 000 rows across the universe from one NOTE class, so the window is client-side; `economic-calendar` truncates **non-monotonically** (a wider request returned fewer rows). ★ **Class 1 needed no build** — derived at check time; the status line gained a **⊙ derived** mark. ⚠ A macro release is stored **once**, not 510 times. ⏸ **New AB-25 — the four decisions are POSTPONED by Victor**, with what each one costs stated. |
| 0.14.0 | 2026-08-28 | Victor | ★★ **Classes 9 & 10 (`earnings_reported`/`earnings_scheduled`) ingested — coverage 7 → 9 of 18.** ⚠⚠ **New AB-24**: three feeds now have three *different* silent shortfalls — a 402, a zero-row answer, and now **truncation at 4 000 rows that keeps the LATEST**. Asking `earnings-calendar` for 2026 returns November onward, HTTP 200, no flag. ★ Built chunk-and-verify: a response **at** the cap is treated as truncated and halved; an uncovered chunk records **no refresh** and **names its cause** — the first run said *'at the row cap'* for what was a **402**, and that is now separated. ⚠ **The feed reaches exactly 365 days**, so `earnings_reported` cannot backfill a multi-year backtest — **AB-3 stands for a second independent reason**. ★★ Knowability differs by class: a scheduled date is knowable **as of when we looked** and **moves** (DE-71). |
| 0.13.0 | 2026-08-28 | Victor | ★★ **Class 5 `restatement_silent` built (new AB-23) — and it correctly reports UNCHECKED.** DE-24's diff had **no production caller** since the B era; it has one now, plus the append-only observation ledger as substrate. ⚠⚠ *Measured:* **0 of 510 names have a prior snapshot**, so nothing is recorded and the class stays UNCHECKED **with its reason** — one snapshot cannot be diffed, and *'no restatements found'* would be DE-35's conflation. ⚠ A second limit **does not go away with time**: no field set carries a period key, so a changed TTM value is **ambiguous by construction**. ★ Forced a third mark into `ingest status` — **◐ built but not yet coverable** — because *'no ingest built'* understated it. |
| 0.12.0 | 2026-08-28 | Victor | ★★★ **Class 4 `restatement_amended` ingested — and the DECLARED SOURCE DID NOT CARRY THE DATA** (new **AB-22**). ⚠⚠ FMP's index returns **zero `10-K/A` across all filers** in three windows; EDGAR holds 5 for TSLA alone and the live sweep found **48 across the S&P 500** — all of which the declared source would have missed **silently on a BLOCK class**. ⚠ The declared *test* was wrong too: `formType ~ /A` matches `SC 13G/A` and `4/A`, **63 for AAPL alone**. ★ Rebuilt on EDGAR with an explicit whitelist **plus 8-K item 4.02**, the *announcement*, which FMP cannot express at all — **5 found**: `CPAY`, `ADM`, `AES`, `AXON`, `MPWR`. ★★ **Two of three classes built against declared sources have not behaved as declared** — the other 11 carry the same unverified assumption. Also **class 12 `ma_announcement`** ingested; coverage **5 → 7 of 18**. |
| 0.11.0 | 2026-08-28 | Victor | ★★ **The contamination check is WIRED and RAN** — `ingest symbols` now reports it, and on live data it printed **`⚠⚠ AVB prints VMRK's series from 2026-08-18`** with no search involved. ★★ `contaminated_by()` is **the detector the CIK diff can never be**: `AVB` is invisible to identity data (its CIK never changed ticker) and visible to *arithmetic*. ⚠ The check calls the vendor — reported separately, kept to `delisted × successors` (2 × 3 here), and it **degrades to a note** rather than failing the sweep. ★ Compares `close_minor` (integers, CT-7.1) so equality is exact rather than float-rounded. ⏸ Only `AVB`'s `delisting` record remains, and it **needs Victor's source URLs** — the writer refuses without them. |
| 0.10.0 | 2026-08-28 | Victor | ★★ **AC-7.85 BUILT** — a combination now emits **two** findings and the retired symbol is checked for successor-price contamination. ⚠⚠ **The live check caught my first cut being wrong**: it flagged the `BK`→`BNY` rebrand, because a rebrand *is* one series through two symbols — ★ contamination is **diverge-then-converge**, and a fixture alone would never have shown it. ⚠ The cause is **refused without source URLs** (DE-68). ⏸ Still open: **nothing calls it on a daily run**, and `AVB` has no `delisting` at the merger date. |
| 0.9.0 | 2026-08-28 | Victor | ★★★ **`EQR` was a MERGER OF EQUALS with AvalonBay — established by SEARCH, and it broke the detector's premise.** ⚠ A CIK diff shows a merger of equals and a rebrand as **the same shape**, so it reported *one* event where **two** names left the universe; **`AVB` is invisible to it by construction**. ⚠⚠ *Measured:* the vendor **back-fills the retired symbol with the successor's prices** — `AVB` 2026-08-17 = 65.90 (its own), 2026-08-18 = 64.03 = `EQR` = `VMRK` — so a dead ticker keeps printing and carries **a fabricated −2.8 % return**, DE-61's welding hazard with no ticker reuse involved. ★ The survivor is clean (**VMRK = EQR 59/59**). **AB-20 rewritten** — my earlier *"AVB prints nothing"* was inferred from the store, not measured, and was wrong. New **DE-68 + AC-7.85** (specified, unbuilt). ★ Skill `ticker-went-silent` rewritten **search-first**. |
| 0.8.0 | 2026-08-28 | Victor | ★★★ **Both AB-18 decisions RULED.** **(1) `EQR` is NOT a delisting** — the registrant index beats the feed, on the same reasoning that makes EDGAR beat FMP for TTM; built as **DE-67 + AC-7.84**, and ⚠⚠ the delisting is **superseded, never deleted** while the `ticker_change` BLOCK still stands, so the name is un-barred rather than declared fine (QD-15). **(2) `HOLX`/`CTRA`/`EA` STAY until the next retrain** — removing them moves `universe_n` off the 510 the model was fitted at, and the cross-section is what defines every rank and `*_sector_z` feature (DE-36); ⚠ the cost is that breadth reads **three names optimistic** meanwhile. ★ Deciding `EQR` **split a pair that had always travelled together**: **new AB-20** — `AVB` is still listed at SEC, prints nothing, and fits no class the model has. **New AB-21** — the QD-17 membership fix is scheduled for end-of-release revalidation, because *79 → 3 was right on one snapshot on one day*. |
| 0.7.0 | 2026-08-28 | Victor | ★★★ **§6B IDENTITY built — DE-61…66, CT-7.8, event class 18.** CIK is the anchor (CRSP's PERMNO idea, from a source already fetched); renames are detected by **diffing dated SEC snapshots**, verified to recover `BK`→`BNY` and `SATS`→`ECHO` from this repo's own universe with **no vendor call**. ⚠⚠ **The first detector produced 79 false renames out of 507** — a CIK is a *registrant* and 1 443 of 8 004 list several securities; fixed by testing membership, 79→3. ★ **Live proof of DE-62**: `XOM`'s CIK vanished from SEC's file while Exxon priced normally — a vanished CIK is never a delisting. ⏸ Two decisions: **`EQR`→`VMRK`** (FMP says delisted, SEC says renamed — RC-54, neither assumed right) and removing the three genuine delistings from the universe. |
| 0.6.0 | 2026-08-28 | Victor | ★★★ **AB-18 diagnosed — and two of the five silent names WERE NEVER DELISTED.** `BK` → **`BNY`** and `SATS` → **`ECHO`** are **rebrands, still trading**; `HOLX`/`CTRA`/`EA` are real delistings (Blackstone-TPG, Devon merger, a $55bn LBO). ⚠⚠ Concluding *"delisted"* from silence — the obvious reading — **would have deleted two live names**, and ★ the silence length is no guide: *SATS was 3 days stale and HOLX 5 months, and the 3-day one was the rename.* New skill **`ticker-went-silent`** encodes the procedure. ⏸ Still open: **D-07 has no `ticker_change` class**, and the universe still holds the dead symbols. **AB-19 CLOSED**: 44 phantom records pruned (archived), `conftest.py` makes the class of mistake impossible, suite **223 s → 16 s**. |
| 0.5.0 | 2026-08-27 | Victor | ★★★ **AB-6 and AB-16 both CLOSED as one amendment** (Victor's decisions, 2026-08-27). ⚠⚠ Investigating AB-16 found the larger defect: **the run record could not name the model that produced the pick**, `manifest.json` carried `git_sha: ""`/`config_hash: ""`/`inputs: []`, and **`inputs_fresh` reported `true` over ZERO inputs** — DE-56's shape inside the orchestrator's own guards. AB-6's `deliver` job was **reporting SUCCESS in 0.000278 s having sent nothing**, falsifying P6 in the record. ★ A real send is verified. **New AB-18**: five S&P 500 names stopped printing at the vendor — one for **five months** — and were silently absent from every cross-section until QA-125's guard named them. **New AB-19**: a unit test had become a live daily run writing into the real `.state/runs`. |
| 0.4.0 | 2026-08-27 | Victor | ★ **AB-15 ANSWERED** — Victor moved the untradeable-name check into **D-03** (QA-125/126, AC-3.32). ⚠⚠ Recorded with it: **the first cut of the guard reproduced the silent drop it was written to prevent** — it filtered `candidates`, and the barred names were *absent from the cross-section*, so `excluded[]` came back empty. Fixed by making the **barred set the authority**. ★ **New AB-16**: the nomination — and therefore `excluded[]` — is **never persisted**; CT-11.7 declares no such artifact. **AB-17**: 110 duplicated lines in `entrypoint.py`, removed. |
| 0.3.0 | 2026-08-27 | Victor | ★ **Interim verification of this register.** Four discrepancies fixed: **AB-9…AB-12 were filed under \"BUILT BUT INERT\"**, where none of them belonged; **AB-10 was closed and still listed as open**; **AB-4 said \"the universe is 130 names\"**, untrue since training moved to 510 — and correcting it surfaced **a new finding: a model fitted on 510 names is applied to a 130-name cross-section, and rank features are defined by their population** (INV-4). Sections regrouped so **§3 is now OPEN QUESTIONS**, per the standing instruction that open questions be highlighted for consolidation. |
| 0.2.0 | 2026-08-27 | Victor | ★★ **The first fit ever performed** — `fit()` existed since B6 and had never been called. §5 records the measured figures: **in-sample IC 0.757 against a walk-forward 0.069 (t = 1.28)**, and the gap between them is the whole reason the purged evaluation exists. **AB-9** (the training run asserts a calendar check it never performed) and **AB-10** (no artifact is persisted, nothing is promoted) registered. |

---

# 1. Why this document exists

A release that ends with *"everything passes"* has either finished or stopped looking. This one
finished a build sequence (B0→B7) and **kept a list**, because several things are known-incomplete
in ways that are invisible from the test suite: the tests pin the behaviour that exists, and every
item below is behaviour that does **not**.

⚠ **Each entry states what a reader would wrongly conclude if they did not know.** That is the
purpose — an as-built register whose entries only say *"not done yet"* is a backlog, and a backlog
does not stop anyone drawing a false conclusion from a green run.

---

---

# 2. ⏸ POSTPONED BY DECISION

## AB-1 — Confidence is declared unmeasured, because coverage is never computed

**Status:** ⏸ postponed by Victor, 2026-08-27. **Owner:** D-01. **Rules:** RA-38, RA-67, INV-012/013.

`author_once` performs three LLM calls — J-11 bear case, J-15 falsifiers, J-16 verdict — and then
writes `scorecard={}` and a confidence that **declares itself unmeasured**.

★ **What is actually missing.** RA-67 says `confidence := evidence_coverage`, and coverage is meant
to be earned mechanically:

```text
rubric names what is needed  →  extraction pulls figures with character-range
citations  →  scorecard checks which rubric items got real evidence  →
coverage = the fraction  →  confidence := coverage
```

`src/fundamental/scorecard/`, `src/fundamental/claims/` and `src/fundamental/filings/` are **built,
tested and exported**, and the authoring path calls **none of them**. It is the same
*built-but-never-called* shape as the fact ledger, the observation ledger and both run stores — the
difference is that this one **cannot be fixed by adding a caller**, which is why it is postponed
rather than done: *the mathematics, the algorithm and the experiment all need reconsideration.*

⚠ **What was fixed anyway, because it was a different defect.** The field previously read
`{"value": 0.0, "basis": "evidence_coverage"}` — which says *coverage was measured and came out
zero*. ★ **That is a lie by shape**, and it makes a company with genuinely no evidence
indistinguishable from a pipeline that never looked. It now reads
`{"value": null, "basis": "not_measured", "reason": …}` and the card renders
*"not measured — …"*. RA-30 already gave a monitor the vocabulary to decline, and **RA-136 added
`not_measurable` for exactly this shape**.

### ★★ Why `CONFIDENCE_FLOOR` is NOT set to `-1`

The proposal was to neutralise the floor by setting it negative. ⚠ **It would have silently
disabled a live safety mechanism**, and the evidence is direct:

| | |
|---|---|
| **`CONFIDENCE_FLOOR` is not dormant** | `src/fundamental/relay/ingest.py:116` calls `assess_confidence` in production |
| **The relay depends on it** | **AC-1.77 / RA-114 / RA-144**: *"the floors fire on it **unchanged**"* |
| **It is the relay's whole safety case** | A pasted chat report is *"largely unverifiable"*, and **coverage de-rating is what stops it becoming the actionable pick** (RA-67, AC-1.8) |
| **The failure mode** | One line, no error, no failing test — and the relay guard gone |

★ **No change was needed at all.** RA-38 computes the floor **from** coverage. With no coverage the
floor is **unreachable, not disabled** — so the constant stays at `0.3`, RA-38 needs no amendment
*(which was the stated concern)*, and the relay keeps working.

⚠ **Release 7 must re-read this before wiring coverage in:** the moment `evidence_coverage` becomes
a real number, the floor becomes reachable **and will start firing** — at `0.3` it forces
`INSUFFICIENT_DATA`, and at `0.5` it caps the verdict at HOLD. That is the intended behaviour and it
will look like a regression on the first run that hits it.

## AB-2 — Claim-binding does not run on the judgement narrative

**Status:** ⏸ postponed with AB-1 (same root). **Owner:** D-01. **Rules:** RA-9, INV-004, AP-2.

`Thesis.claims` is `()` on every authored thesis. **RA-9**: *"Every claim binds to an evidence span
… an unbound factual claim is a defect."*

★ **This is the hallucination guard for the *prose*.** §7's argument is that hallucination is a
*detectable class*: a fabricated number in **extraction** is caught by RA-6's source check, and a
fabricated number in a **judgement narrative** is caught by claim-binding. ⚠ **The first half runs;
the second does not** — so if the model writes *"NAND margins expanded on HBM demand"*, nothing
checks it against the filing.

⚠ **What a reader would wrongly conclude:** that a thesis passing every test has had its narrative
verified. It has had its **falsifiers** verified (each names a real observable field) and its
**verdict** constrained. Its prose is unchecked.

## AB-3 — Canadian listings and CDRs are not valued (RC-58)

**Status:** ⏸ Victor, 2026-08-25. **Owner:** D-11/D-07.

★ **This is the single thing keeping the daily card non-actionable.** DN-39 requires a `COMPLETE`
risk pass; a complete pass needs book-wide exposure; that needs every held name priced. **All four
accounts hold at least one CAD-venue or CDR position**, and those symbols are `402` on the current
FMP plan — measured 2026-08-26: `MDA.TO` → 402, `MRV.NE` → 402, against an `NVDA` control at 200.

⚠ It is a **subscription boundary, not a bug** (DE-49). The fix is a plan upgrade or a second price
source, and it is Victor's commercial decision.

## ⚠⚠ And survivorship cannot be corrected either — measured, not assumed

**DE-60, 2026-08-27.** `delisted-companies` is INV-017's declared source. It
returns **100 rows on page 0 and `402` on every page after**, spanning about
**three weeks**. ★ So it answers *"who is delisting now"* — which is what the
§6A gate needs, and it is now ingested — and **cannot** answer *"who delisted in
2019"*, which is what survivorship correction needs.

⚠ Every backtest therefore stays stamped `survivorship_handled=False`, and
**QA-14 says such a result is reported as BIASED, not as a result.** That is not
a gap waiting on code; it is a gap waiting on a data source.

## AB-5 — D-10 Experiments is unspecified and unbuilt

**Status:** ⏸ by design. **Rule:** BS-23, L0 §4.2.

The **specifying** trigger has fired (*"the first full E2E run is complete"*); the **building**
trigger is Victor's — *"I do not plan to implement D-10 code until the full pipeline runs stably."*
Held safe by **ST-2's one-way import rule** rather than by a spec.

---

# 3. ⚠⚠ OPEN QUESTIONS — these need a decision, not a build

> ★ **Read this section first.** Every entry below changes what other work
> *means*, not merely when it happens. An answer here is worth more than a
> feature.

## AB-12 — ★★★ The IC gate's standard error is the NULL one, and QA-4 promises otherwise

**Status:** ⚠ **OPEN — found 2026-08-27 wiring promotion. Needs Victor's call.**
**Owner:** D-03. **Rules:** QA-4, QA-17, §5.3b.

⚠⚠ **This is the gate promotion turns on, and two defensible statistics disagree
about the same run by 3.5×.**

Measured on the full 500-name, ten-year fit — `mean IC = 0.0203`:

| Standard error | Value | t | Verdict |
|---|---|---|---|
| **`corrected_se`** — `√(h/((n−1)·T))` | 0.00411 | **4.94** | ★ **PASS** |
| **Realised** — `sd(per-date IC)/√(T/h)`, `sd = 0.156` | 0.01433 | **1.42** | ⚠ fail |

★ **`corrected_se` is the NULL standard error.** It assumes per-date rank IC has
variance `1/(n−1)`, which is true *under the null of no skill*. The **observed**
dispersion is **3.49× larger**, because real cross-sectional IC varies across
regimes — 2016-18 and 2024-26 scored ~0.034 while 2018-20 and 2022-24 scored
~0.009.

⚠ **QA-4 says every reported statistic carries "an autocorrelation-corrected
standard error." `corrected_se` contains no autocorrelation correction at all** —
it is the null variance with an overlap divisor. The name and the rule both
promise something the formula does not do.

★ **Both readings have a defence, which is why this is a question and not a bug
fix:**

* **For the null SE** — under `H₀: IC = 0` the per-date variance *is* `1/(n−1)`;
  the excess dispersion is time-varying *true* skill, not noise, so charging the
  test for it is conservative to the point of being wrong.
* **For the realised SE** — the quantity being tested is *"will this signal earn
  its keep going forward"*, and its forward variability is what was observed, not
  what the null assumes. Standard quant practice (Newey-West) uses the realised
  series for exactly this reason.

⚠⚠ **The consequence is not academic.** `ic_significance` **PASSED** on this run.
The model was still refused — `cost_survival` and `breadth` are `NOT_EVALUATED`
(**AB-10**) — so nothing was promoted. ★ **But the moment those two land, this
gate promotes a model whose realised t is 1.42.**

★ §5.3b calls its own table an **MDE** — *"the bar, not a prediction"*, *"computable
before anything is measured"*. That is a **power** calculation. `ic_significance_gate`
uses it as an **acceptance** test (`passed = |IC| >= mde`). Those are different
questions, and the gate currently answers the planning one.

**Not changed unilaterally:** the formula is D-03's contract, `mde()` and the
§5.3b table are built on it, and switching the denominator would move every
published bar. Registered as an open **QA-** question for Victor.

## ~~AB-13 — The daily run scores 130 names with a model fitted on 497~~ — ✅ **CLOSED 2026-08-27**

**Status:** ⚠ **OPEN — the guard exists, the mismatch does not.** **Owner:** D-03/D-04.

★ **Wired 2026-08-27**: `_rank` now scores with the promoted artifact and
`assert_population_parity` runs **before** it. ⚠ The promoted model predates the
`training_names` field, so the check reports
**`UNCHECKED: … cannot be compared to the one it was fitted on`** on every run
rather than passing silently — *"could not check" must not read like "checked and
fine"*.

⚠⚠ **The mismatch is real and currently unguarded**: training used **497**
names, the daily run uses **130**, and `rank_ret_5d`, `rank_vol_20d` and every
`*_sector_z` are **defined by the population they are computed in**. The next fit
records `training_names` and the check will then **raise** at a ratio of 0.26.

✅ **Closed by alignment, not by a check** (**OR-49**). `--universe` now defaults
to `sp500` — the same list `src.models.train` declares, read through **one**
call so the two cannot drift. `watchlist` stays reachable for comparison.

★ **Measured 2026-08-27**: 130 names 57 s · **510 names 3 m 44 s**. ⚠ And the
ranking below #1 changed — **`COHR` and `TTD` entered the top three** and are not
in the 130-name list at all, so the narrow universe was hiding names the model
scores above `ARM` and `INTC`.

⚠ **DE-36 is why this costs nothing in mandate terms**: the universe is what
*normalises* the cross-section; the watchlist is what may be *bought*. INV-6
still permits exactly one actionable pick.

## ~~AB-16 — `excluded[]` is recorded on the nomination, and the nomination is never persisted~~ — ✅ **CLOSED 2026-08-27**

**Status:** ✅ **Built.** **Owner:** D-11. **Rules:** RC-62…64. **AC:** 11.44…11.46.

⚠⚠ **Investigating it found something larger than the exclusions.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  $ grep -rl "85b75744" .state/runs/<run_id>/                      ║
║  NOT FOUND — the run could not name the model that produced it.   ║
║                                                                  ║
║  manifest.json:  "inputs": [],  "code": {"git_sha": ""}           ║
║                  "config_hash": ""                               ║
║                  "preconditions": {"inputs_fresh": true, …}      ║
╚══════════════════════════════════════════════════════════════════╝
```

★ So the filed defect — *the exclusions are invisible* — was one missing field
in a record that **could not reproduce the run at all**, which QA-121 requires
and INV-2 rests on.

**Fixed, as one amendment (Victor's instruction):**

* **RC-62** — D-03's `Nomination` is folded into `recommendation.json`: the full
  slate, `excluded[]` with reasons, `universe_n`, `model_artifact_id`.
  ★ **Victor chose the single file**; D-11 composes it at write time so **D-12's
  `Recommendation` class gains no dependency on D-03's contract** — one file for
  the reader, two independent contracts for the code.
* **RC-63** — `delivery.json`, and ⚠ **absence means not-delivered, never
  unknown** (DE-35): a run that did not deliver writes no file at all.
* **RC-64** — `universe_n`, `excluded_n`, `model_artifact_id`, `delivery_status`
  in the index. ⚠ `excluded_n` is `None` with no nomination and `0` when nothing
  was barred: *we did not rank* and *we barred nobody* are different facts.
* **OR-51** — the provenance is supplied. `git_state()` **existed and the daily
  path never called it**, so OR-11's *"a dirty tree is permitted and marked"* was
  recording neither the sha nor the dirt.
* **OR-52** — ★★ **`inputs_fresh` was returning `true` over ZERO inputs.** It
  asserted freshness having checked nothing — **DE-56's shape inside the
  orchestrator's own preconditions**. It now reports `null` (NOT EVALUATED).

★ **Verified live:** `model_artifact_id sha256:85b75744…`, `universe_n 510`,
`candidates 503`, `excluded 7`, `git_sha 10251e5 (dirty: True)`,
`inputs_fresh: None`.

## AB-18 — ⚠⚠ Five names went silent, and **two of them still trade** — ✅ **BUILT 2026-08-28**

**Status:** ✅ **§6B built.** ⏸ **Two decisions left.** **Owner:** D-07. **Rules:** DE-61…66, CT-7.8, class 18.

| Ticker | Last bar | What actually happened | Class |
|---|---|---|---|
| `HOLX` | 2026-04-07 | acquired by **Blackstone / TPG** | delisting |
| `CTRA` | 2026-05-07 | merged into **Devon Energy** | delisting |
| `EA` | 2026-08-05 | **$55bn leveraged buyout** | delisting |
| `BK` | 2026-06-29 | ★★ **rebrand** — `BK` → **`BNY`**, still trades | ticker_change |
| `SATS` | 2026-08-24 | ★★ **rebrand** — `SATS` → **`ECHO`**, still trades | ticker_change |

★ From the price feed a rename and a delisting are **identical**; the silence
length is no guide either — *`SATS` was 3 days stale and `HOLX` 5 months, and
the 3-day one was the rename.*

### ✅ What was built — CIK as the anchor, a snapshot diff as the detector

★ The canonical solution is CRSP's **PERMNO**, a permanent id surviving ticker,
name, CUSIP and exchange changes. **CIK** is the same idea from a source this
repo already fetches, free.

* **Detection** — diff dated SEC `company_tickers.json` snapshots on CIK.
  ★ **Verified against this repo's own stored universe**: it recovered `BK`→`BNY`
  and `SATS`→`ECHO` exactly, **no vendor call, no web search**.
* **Retrieval** — fetch under the **current** symbol. *Measured:* `BNY` returns
  **164 bars covering the whole `BK` period**; `BK` returns **122** and stops at
  the changeover.
* **⚠⚠ Never splice** — the overlapping bars agree on OHLC and **disagree on
  volume** (`BK` 2 790 284 vs `BNY` 2 790 283; `ECHO` rounded to hundreds). A
  splice puts a step into `volume.split_adjusted_zscore.v1`.
* **Point-in-time** — `resolve(ticker, as_of)`. ⚠ `S` was **Sears**, then
  **Sprint** (2005), then **SentinelOne** (2021): a ticker-keyed join welds three
  companies into one series and no range check detects it.

### ⚠⚠ The bug this shipped with first — QD-17 is not a future concern

The first detector keyed `{cik: ticker}` and produced **79 false renames out of
507 names**: `WFC` "became" `WFC-PA`, `BRK-B` "became" `BRK-A`, `GOOGL` "became"
`GOOGM`.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A CIK IS A REGISTRANT, NOT A SECURITY.                          ║
║  1 443 of the 8 004 CIKs in the live file list MORE THAN ONE      ║
║  ticker — preferred, warrants, notes, share classes — so a dict   ║
║  keyed on CIK keeps whichever row came last.                     ║
║                                                                  ║
║  ★ Fixed by testing MEMBERSHIP, not equality.  79 → 3.           ║
╚══════════════════════════════════════════════════════════════════╝
```

★ SEC lists the common stock **first**, so the successor is SEC's own ordering
rather than our guess — and the whole candidate set travels with the finding so
⚠ **an ambiguous case is visible rather than decided** (`BK` → `['BNY','BNY-PK']`).

### ✅ Decision 1 — `EQR` is **NOT** a delisting (Victor, 2026-08-28)

The sweep found a **third** rename nobody was looking for:

```text
  EQR -> VMRK   cik 0000906107
  ⚠ FMP's delisted-companies feed called EQR a DELISTING on 2026-08-18.
  ⚠ SEC says CIK 906107 now lists VMRK.
  ★ Measured: EQR stops 2026-08-24; VMRK prices 41 bars through 2026-08-27.
```

**RC-54 said neither source is assumed right.** ★ Victor's ruling settles it in
favour of the **registrant index**, and the reasoning generalises — it is the
same precedence that already makes **EDGAR beat FMP for TTM**: *the source
carrying the explicit fact beats the source inferring one.* The feed sees a
symbol go dark; it cannot tell a rebrand from an exit.

★ **Built as `DE-67` + `AC-7.84`** — a knowable `ticker_change` **supersedes** a
vendor `delisting` for the same ticker.

⚠⚠ **Un-barred is not "declared fine."** The delisting row is **superseded, never
deleted** (the ledger is append-only), and the `ticker_change` is still a
**BLOCK** demanding DE-66's explicit handling. Clearing the bar *and* the BLOCK
would be exactly the severity downgrade QD-15 forbids.

### ⚠ And it split a pair that had travelled together — `AVB` is now on its own

`AVB` and `EQR` are named as a couple in `tradeable.py`, `gate.py` and DE-62,
because the feed delisted them on consecutive days. ★ **They have now diverged**,
and `AVB` is the harder of the two:

| | `EQR` | `AVB` |
|---|---|---|
| FMP feed | delisted 2026-08-18 | delisted 2026-08-17 |
| SEC file | CIK 906107 → **`VMRK`** | ⚠ **still lists `AVB`**, own CIK, open-ended |
| Prices | `VMRK` prints normally | ⚠ **nothing prints** |
| Verdict | ✅ rename (DE-67) | ⏸ **unresolved** |

⚠ **DE-67 deliberately does not cover it** — no `ticker_change`, so the delisting
stands and `AVB` stays barred. That is the conservative direction and it is the
right default, but *"SEC still lists it and it prints no bar"* is a **third
state** the model has no name for: not a rename, not confirmed dead. It may be a
registrant that has not yet filed its Form 15. **Registered as AB-20.**

### ✅ Decision 2 — the three dead symbols **stay until the next retrain** (Victor, 2026-08-28)

`HOLX`, `CTRA` and `EA` are **genuine delistings**; `BK`/`SATS`/`EQR` now resolve
automatically. ★ Victor's ruling: **leave them in the universe and remove them at
the next retrain.**

★ **Why that is the right order, not the lazy one.** Removing three names moves
`universe_n` off 510 — and `universe_n` is *what the cross-section normalises
over*. `rank_ret_5d`, `rank_vol_20d` and every `*_sector_z` are **defined by the
population they are computed in** (DE-36): a percentile among 510 is not a
percentile among 507. ⚠ The promoted model was **fitted at 510**, so dropping
them now would put the live cross-section and the fitted population out of step —
a fresh instance of **AB-4**, which is already open for exactly this reason.
Retrain is the moment both move together.

⚠ **What this costs in the meantime, stated plainly:** three names sit in the
universe that can never be nominated. They are barred by `untradeable()` and
appear in `excluded[]` **with their reason** (QA-125), so they are *visible*, not
silent — but `universe_n` counts them, so the breadth figure is **three names
optimistic** until the retrain.

### ★ And a live proof that DE-62's caution was right

`XOM`'s CIK is **absent from SEC's ticker file**, and **Exxon Mobil priced
normally that same day — 41 bars through 2026-08-27.** ⚠ Had a vanished CIK been
treated as a delisting, the sweep would have dropped the largest US oil company
on its first run.

## AB-20 — ⚠⚠ `EQR`/`AVB` was a **merger of equals**, and the retired symbol is **printing the successor's prices**

**Status:** ⚠ OPEN — cause established 2026-08-28, **the data defect is not fixed**.
**Owner:** D-07. **Rules:** DE-61, DE-68, DE-64.

★ **Established by search, not by data** (Victor, 2026-08-28): Equity Residential
and AvalonBay Communities combined in a **merger of equals** forming `VMRK`.
`EQR`'s CIK `0000906107` survived; `AVB`'s side was retired.

⚠ **My earlier entry said `AVB` "prints nothing". That was wrong** — I inferred
it from the event store instead of measuring the feed. `AVB` prints through
2026-08-24, and *what* it prints is the problem:

```text
  2026-08-17   EQR 63.66   AVB 65.90   VMRK 63.66   ← still two companies
  2026-08-18   EQR 64.03   AVB 64.03   VMRK 64.03   ← AVB now prints VMRK
  2026-08-19   EQR 64.35   AVB 64.35   VMRK 64.35
  2026-08-24   EQR 68.14   AVB 68.14   VMRK 68.14

  ★ VMRK's pre-merger closes equal EQR's 59/59 — the SURVIVOR is clean.
  ⚠⚠ AVB's closes equal EQR's from 2026-08-18 — the RETIRED SIDE IS NOT.
```

⚠⚠ **`AVB` carries a fabricated −2.8 % return on 2026-08-18** (65.90 → 64.03).
It is not a price move; it is the series changing companies mid-stream. ★ This is
**DE-61's welding hazard** — *"a ticker-keyed join welds unrelated companies into
one series and no range check detects it"* — arriving not through ticker reuse
but through **a vendor back-filling a retired symbol**. Nothing in the stack
flags it: the bars are present, monotonic, and in range.

### ⚠ What this exposed about the detector — DE-68

★ The CIK diff shows **a merger of equals and a rebrand as the same shape**: one
CIK, new ticker. So it reported **one** event where **two** names left the
universe, and ⚠ **the retired side is invisible to it by construction** — `AVB`
never appears in the diff, because its CIK was not the one that changed ticker.

⚠⚠ **The detector is therefore not a classifier**, and DE-68 now says so: the
cause must come from a **search**, and a combination is recorded as **two**
findings — a `ticker_change` for the survivor and a `delisting` for the retired
side.

### ⏸ What is still not done

| | |
|---|---|
| ⚠ `AVB` still in the universe | its bars from 2026-08-18 are `VMRK`'s |
| ⚠ no `delisting` recorded for `AVB` at the merger date | the feed's 2026-08-17 date is the *announcement*, not the retirement of the series |
| ✅ contamination detection | **AC-7.85 BUILT** — `contaminated_from()`, verified live: `AVB`/`VMRK` → 2026-08-18, and `EQR`/`VMRK`, `BK`/`BNY`, `SATS`/`ECHO` → `None` |
| ✅ the sweep runs it | `ingest symbols` now reports it — ★ **live output 2026-08-28**: `⚠⚠ AVB prints VMRK's series from 2026-08-18` |
| ⏸ `AVB`'s `delisting` record | **DEFERRED by Victor, 2026-08-28** — *"ignore it, revisit after all codes and as-built validation"*. ★ Nothing is blocked: `AVB` is barred by the existing FMP delisting **and** by staleness, so only the stated *reason* is wrong, not the outcome |
| ★ `EQR`→`VMRK` itself | ✅ correct — survivor verified 59/59 |

### ⏸ DEFERRED — and the one thing that must not be lost with it

⚠ **Victor deferred the `AVB` record on 2026-08-28** to keep the build moving:
*"ignore it, add a note to revisit after completing all codes and as-built
validation."* ★ Recorded rather than actioned, because the writer **refuses a
cause without source URLs** and fabricating one to unblock myself would put a
guess in the store next to corroborated findings — the exact failure DE-68
exists to prevent.

⚠⚠ **What the deferral does NOT make safe.** `AVB` being barred protects the
**nomination**; it does not protect the **panel**. `AVB` is one of the 510
training names, and its bars from 2026-08-18 are `VMRK`'s — so any feature or
fit computed over a window spanning the changeover consumes **a return that
never happened**. ★ The bar is a D-03 guard (QA-125); the contamination is a
D-07 data fact, and the two are not the same protection.

**On revisit, the check is:** does the training panel include `AVB` bars on or
after 2026-08-18, and if so, what did the fit see?

⚠ **`AVB` is currently barred anyway** — by staleness, for the wrong reason
(QA-125 says *"stopped printing"*, and it did not). ★ That is luck, not a guard:
the bar is two sessions of lag, and a contaminated symbol that kept printing to
the as-of date would rank normally.

## AB-21 — ⏸ Revalidate the QD-17 membership fix at end of release

**Status:** ⏸ scheduled by Victor, 2026-08-28 — *"revalidate after coding
complete, at end of release."* **Owner:** D-07. **Rules:** QD-17, DE-62.

★★ **Why this earned a scheduled recheck rather than a green tick.** The first
detector keyed `{cik: ticker}` and produced **79 false renames out of 507** —
`WFC` "became" `WFC-PA`, `BRK-B` "became" `BRK-A`. The fix (test **membership**,
not equality) took it to **3**, and 3 is the number that matched reality *on one
snapshot, on one day*.

⚠ **A count that came out right once is evidence, not proof.** The failure mode
is structural: **1 443 of the 8 004 CIKs list more than one security**, SEC's
ordering is what picks the successor, and neither the multi-security population
nor the ordering is a contract SEC owes us. ★ The regression test pins the
*shape* (a registrant's other securities are not renames); it cannot pin that
tomorrow's file still behaves.

**What the end-of-release check must do:**

* ★ Re-run the sweep against a **fresh** SEC snapshot and confirm the finding
  count is still ~3 and every one is a **real** rename.
* ⚠ Confirm no S&P 500 name has acquired a second listed security that reads as
  a rename — the `BK` → `['BNY','BNY-PK']` shape, which is already flagged
  `ambiguous` rather than decided.
* ★ Confirm the `ambiguous` flag is still *surfacing* rather than being consumed
  silently — the whole candidate set travels with the finding for this reason.

⚠ **A rename accepted wrongly is not a cosmetic error**: it repoints a name's
price fetch at a different security, and DE-64 forbids splicing precisely
because the join is invisible once made.

## AB-25 — ⏸ **Four decisions POSTPONED by Victor, 2026-08-28**

**Status:** ⏸ deferred **deliberately**, to keep the build moving.
**Owner:** Victor. **Revisit:** with the as-built and design review, before E2E sign-off.

★ Victor's instruction: *"try to postpone (if possible) the 4 decisions, which
need careful review of as-built and design and other consideration."* ⚠ Recorded
**here as one entry** so they cannot be lost individually in a changelog.

| # | Decision | Registered as | ⚠ What it blocks |
|---|---|---|---|
| 1 | **CAD/CDR valuation** | AB-3 | ★ the *only* thing keeping the card non-actionable — no account can produce a `COMPLETE` risk pass |
| 2 | **The IC gate's standard error** | AB-12 | ⚠⚠ the same run gives **t = 4.94 (PASS)** and **t = 1.42 (fail)**; a promotion decision rests on which is used |
| 3 | **Universe breadth** | AB-4 · QQ-11 · QQ-14 | ⚠ the `breadth` gate reports `NOT_EVALUATED` because QA-43's residual measurement **does not exist** |
| 4 | **Confidence + claim-binding** | AB-1 · AB-2 | ⏸ already deferred to **R7** — *"needs mathematics, not plumbing"* |

⚠⚠ **None of the four is blocked on code.** Each needs a judgement or a
measurement that does not exist yet, which is precisely why postponing them was
the right call and why **postponing them does not make them smaller**.

★ **What the postponement costs, stated plainly** — so the E2E run is read
correctly rather than optimistically:

* the daily card remains **non-actionable** (decision 1);
* a promoted model's IC gate **may be passing on the null standard error**
  (decision 2) — see AB-12;
* the `breadth` gate is **not a gate**, it reports `NOT_EVALUATED` (decision 3);
* `confidence` reads **`not_measured`**, honestly, and stays that way (decision 4).

⚠ An E2E run that goes green while all four stand is a run that proves the
**plumbing**, not the **judgement**. That distinction belongs in whatever
sign-off follows.

## AB-24 — ⚠⚠ Three feeds, three different silent shortfalls

**Status:** ⚠ **registered 2026-08-28.** **Owner:** D-07. **Rules:** DE-58, DE-60, DE-70.

★ **AB-22 said a declared source is an assumption until measured.** Class 9/10
made the point a third time, in a *new* way — so the pattern is now worth naming
as a class of defect rather than three incidents.

| Feed | What it does when it cannot answer | ⚠ How it LOOKS |
|---|---|---|
| `delisted-companies` | **402** on page 1+ | a complete 3-week feed (DE-60) |
| `sec-filings-search` | returns **0 rows** for `10-K/A` | *"no amendments exist"* (DE-69) |
| `earnings-calendar` | **truncates at 4 000 rows, keeping the LATEST** | a complete answer for the range asked (DE-70) |

⚠⚠ **Not one of the three raises, and not one says a word.** Asking
`earnings-calendar` for 2026 returns `2026-11-05..` — ten months missing, HTTP
200, no flag. ★ A sweep that recorded the window it *requested* would mark the
class `CHECKED` over names it never saw, which is DE-56/DE-58's defect for the
third and fourth time in one release.

### ★ What was built in response

* **Chunk, then verify** — a response **at** the cap is treated as truncated
  (it is indistinguishable from one that was) and the window is **halved and
  refetched** until it fits.
* **Record only what was reached** — an uncovered chunk records **no refresh**,
  so the class stays `UNCHECKED`.
* **Name the cause** — ⚠ `capped` and `refused` are different problems needing
  different fixes; the first run conflated them and reported *"at the row cap"*
  for what was actually a **402**. Corrected.

### ⚠ And a hard limit this exposes for INV-017

**`earnings-calendar` reaches exactly 365 days** — a window opening 2025-08-29
answers, 2025-08-27 is `402`. ★ So `earnings_reported` **cannot backfill a
multi-year backtest**, precisely as `delisted-companies` cannot (DE-60). ⚠ Two
of the classes a long backtest would want are now known to be **structurally
unavailable at this plan**, and **AB-3 stands** for a second, independent reason.

## AB-23 — ◐ Class 5 is built and **cannot be checked yet** — a third state

**Status:** ◐ **built 2026-08-28, UNCHECKED by construction.** **Owner:** D-07.
**Rules:** DE-24, DE-35, DE-58, AC-7.39.

★ **DE-24's diff had existed for a long time with no production caller** —
`pit/restatement.py::diff_against_stored`, exported and unit-tested, called by
nothing. The same *built-but-never-called* shape as the fact ledger, both run
stores and `fit()`. ★ It now has a caller **and a substrate**: the observation
ledger is append-only and content-hashed, so dated priors accumulate.

⚠⚠ **And it finds nothing, which is the finding:**

```text
  observation ledger, 2026-08-28
    financial_scores   47 rows / 47 tickers / 0 with a prior
    key_metrics_ttm    48 rows / 48 tickers / 0 with a prior
    profile            48 rows / 48 tickers / 0 with a prior
    ratios_ttm         48 rows / 48 tickers / 0 with a prior

  -> 0 of 510 names comparable.  NOTHING is recorded as refreshed.
```

★ **FMP serves one answer: today's.** A silent revision is detectable *only* by
having kept a dated earlier value, so **one snapshot cannot be diffed** — and
reporting *"no restatements found"* from it would be exactly the conflation
DE-35 exists to stop. The class becomes checkable **after a second dated
ingest**, and not before.

### ⚠ A second limit, and this one does not go away with time

**No field set carries a period key.** All four are TTM or current-state, so a
changed value is **ambiguous by construction**: a new quarter rolling into a
trailing window is indistinguishable from a revision of an already-reported one.
★ The finding carries `ambiguous: true` and says why, rather than claiming a
restatement it cannot establish. ⏸ Making class 5 *unambiguous* needs a
**period-keyed** field set in the ledger — registered here, not silently
assumed away.

### ★ It also forced a third state into the status line

⚠ `ingest status` had two marks for *not-swept* — *"sourceable, never swept"*
and *"declared source, no ingest built"* — and class 5 is **neither**. Reporting
it as *"no ingest built"* understates the work; reporting it swept would
overstate the coverage. ★ New mark **◐ built but not yet coverable**, with the
reason inline.

## AB-22 — ⚠⚠ A declared source that does not carry the data — and it was a BLOCK class

**Status:** ✅ **fixed 2026-08-28**, kept because ★ **the shape recurs.**
**Owner:** D-07. **Rules:** DE-69, DE-35, AC-7.86.

`L1-data-engine` declared class 4 `restatement_amended` as
`fmp:sec-filings-search/symbol (formType ~ /A)`. ⚠ **Both halves were wrong**, and
neither would have failed loudly.

### ⚠⚠ Half one — the source does not have it

```text
  FMP  sec-filings-search/form-type  10-K/A
       2024-01-01..2024-12-31  ->  0 rows
       2025-01-01..2025-06-30  ->  0 rows
       2026-01-01..2026-08-28  ->  0 rows
  ⚠ 10-Q/A over the SAME windows fills a 100-row page every time.
  ⚠ Per-symbol search: 2 683 filings across 5 mega-caps -> NOT ONE.

  ★ EDGAR holds FIVE 10-K/A for TSLA alone.
  ★ The live sweep found 48 across the S&P 500.
```

⚠ **Zero annual amendments across every US filer in a year is not rarity, it is
a vendor gap** — and a class built on it would have reported `CHECKED` while
missing all 48, **silently, on a BLOCK class**. ★ Rebuilt on **EDGAR**: the same
precedence that already governs TTM — *the source carrying the fact explicitly
beats the one that omits or infers it.*

### ⚠ Half two — the TEST was wrong too

`formType ~ /A` matches, on those same five names: **63 `SC 13G/A`, 7 `4/A`,
5 `13F-HR/A`, 5 `SC 13D/A`** — ownership and holdings amendments that **restate
no financial statements**. ★ It would have filed Apple as having restated 63
times. Replaced by an explicit **whitelist** of financial-statement forms.

### ★ And the signal that arrives first

**8-K item 4.02 — *"Non-Reliance on Previously Issued Financial Statements"*** —
is the *announcement*, and it lands **weeks before** the amended filing. EDGAR's
`items` field carries it; ⚠ **FMP exposes no item numbers at all**, so no FMP-based
class could ever have had it. *Live: 5 in the S&P 500 over 3 years —* `CPAY`,
**`ADM`** *(the 2024 accounting investigation),* `AES`, `AXON`, `MPWR`.

### ★★ Why this is kept after being fixed

⚠ **A spec's declared source is an assumption until something measures it.**
Three classes have now been built against declared sources and **two of the three
did not behave as declared** — DE-60's three-week wall, and this. ★ The
**remaining 11 unbuilt classes carry the same unverified assumption**, and
AB-14 should be read with that in mind.

## AB-4 — ⚠ Two universes now, and only one of them was widened

**Status:** open, registered as **QQ-11**. **Owner:** D-03.
**Amended 2026-08-27** — the original entry said *"the universe is 130 names"*, which stopped being
true when the training run moved to the full index.

| Where | Names | Source |
|---|---|---|
| **Training** (`src.models.train`) | **510** | `config/sp500_tickers.yaml` — ★ widened 2026-08-27 |
| **Daily ranking** (`src.orchestration.entrypoint`) | **130** | `config/settings.yaml` → `pipeline.tickers` |

⚠⚠ **A model fitted on 510 names and applied to a 130-name cross-section is a
mismatch nothing currently checks.** Rank features (`rank_ret_5d`,
`rank_vol_20d`) and every `*_sector_z` are **defined by the cross-section they
are computed in** — a percentile among 510 is not a percentile among 130. ★ That
is INV-4 train/inference parity, and it is not the parity check D-04 already runs
(`governance/parity.py` compares the feature *contract*, not the *population*).

**L1-quantitative-analysis §5.3b**: *"On the history already held, **~330 names reaches t = 3 at
1q**. That is a data task — an ETL re-run."* ★ Training now clears that count.

⚠ **Count is still not breadth.** QQ-11 asks *"how far should the universe widen, and toward which
sectors"* and answers *"by added breadth, not count (QA-44) — needs QA-43's residual-correlation
measurement to choose."* **That measurement does not exist**, which is why the `breadth` gate reports
`NOT_EVALUATED` (**AB-10**).

⚠ **A second, independent problem in the same area:** `lambdarank_truncation_level = 30` means the
ranking objective **ignores roughly 100 of the 130 names** during training (v0.6.0 finding (ii)).

★ **Universe breadth and book concentration are different things** (L0 §12) — widening the universe
does not dilute the book, and M-2 constrains only the second.

---

# 4. ⚠ BUILT BUT INERT — wired, and doing nothing

## AB-14 — Nothing schedules the corporate-action sweep — ✅ **ingest complete 2026-08-28**

**Status:** ✅ **every class is accounted for; ⏸ the cron period is still Victor's.**
★ *Ingest* built for all sourceable classes (**5 → 15 CHECKED of 18**); `price_adjustment_state` is
**derived at check time** and needed none; `restatement_silent` is built and awaits a second snapshot
(**AB-23**); `index_membership` has no source at any price. ★ **DE-72 cadence** now answers *"what is
stale RIGHT NOW"* by severity — **BLOCK 1 day, FLAG 7, NOTE 30** — which is the question a scheduler of
any period needs, so choosing the period no longer blocks the build.

**Original entry —** ⚠ found 2026-08-27. **Owner:** D-07/D-08. **Rules:** DE-56, QD-16, FE-10.

★★ **DE-56 fixed a gate that reported `CHECKED` having fetched nothing.** With
the store populated it now **HALTs on NVDA's real 2024-06-10 10:1 split**, where
the same window previously found **zero**.

★ **Runnable since 2026-08-27**: `python -m src.data_engine.ingest events`
sweeps, `… facts` refreshes EDGAR, and `… status` prints what each store holds
**and what it does not**. ⚠ **Nothing schedules it** — QD-16 rules out a per-run
sweep (*"510 tickers × 8 classes is thousands of calls per run against a 300/min
cap"*), so cadence is a decision about API budget, not something to assume.

⚠⚠ **A second defect surfaced building this — DE-58.** `record_refresh` stored
*when* a class was fetched but not *which names*, so a **12-name sweep marked
`split` refreshed and a 510-name gate read `CHECKED` — 498 never fetched.**
Coverage now travels with the refresh, and the unfetched names are **named**.

★ Current state, from `ingest status`: **4 of 17 classes swept** (`split`,
`reverse_split`, `dividend`, `delisting`); 12 have declared sources in §5A.5 with
**no ingest built**; one (`index_membership`) is **UNCHECKED permanently**.

⚠⚠ **The `delisting` ingest found two real ones and the gate now HALTs on them**
— `AVB` 2026-08-17 and `EQR` 2026-08-18, both in the S&P 500 universe the model
trains and scores on. ★ It also exposed **DE-59**: the handling cleared *every*
BLOCK, so a price adjustment was "handling" a name that had stopped trading.

★ **The daily run therefore reports `split: UNCHECKED`, which is the truth** —
and is **weaker than FE-10's guarantee sounds**. ⚠ *What a reader would wrongly
conclude*: that a green run means no unhandled corporate action in the window. It
means **nobody looked**, and the report says so.

⚠ **Note for whoever schedules it**: the sweep must cover the **whole universe**
or record no refresh at all. A partial pass leaves the rest unchecked, and DE-36
says an unhandled split on an excluded name *contaminates every other name's
rank*.

## ~~AB-15 — The `delisting` class can be ingested and the gate still cannot use it~~ — ✅ **ANSWERED 2026-08-27**

**Status:** ✅ **Victor's decision: the check moves to D-03.**
**Owner:** D-03. **Built:** `src/quant/signals/tradeable.py`, QA-125/126, AC-3.32.

★ The sweep ran over the whole index: **51 822 findings across 510 names**, all
four sourceable classes at **510-name coverage**, and the two real delistings
(`AVB`, `EQR`) are in the store.

⚠⚠ **And the daily run still does not see them.** The class reports:

```text
UNCHECKED: store covers 2026-08-06..2026-12-30,
           window needs   2026-02-07..2026-08-26
```

★ **That is correct behaviour** — DE-60's three-week feed honestly declining a
200-day window rather than claiming it. ⚠ **But the consequence is that the
`delisting` class can essentially NEVER be CHECKED**, because every real
panel-building window is longer than the feed reaches. An `UNCHECKED` class
contributes no findings, so the BLOCKs never reach the gate.

## ★ And the practical exclusion happens by accident

⚠ Measured: `AVB` and `EQR` **still return prices**, last bar **2026-08-24** —
two sessions before `NVDA`'s 2026-08-26. `rank_by_model` selects
`panel[date == as_of]`, so they are absent from the day's cross-section and are
not ranked.

★★ **They are excluded because they have no bar today, not because anything
detected the delisting.** A name that delisted *today* and still printed a bar
would rank normally. **The guard is a side effect, and side effects are what
this register exists to name.**

## ✅ The answer — the check lives where the ranking is made

*"Has any name in my universe stopped trading?"* is a **current-state** question,
not a window question — and §6A's gate is window-scoped by construction. ★ Victor
decided it belongs in **D-03**: the domain that owns the ranking owns the rule
that a ranked name must be tradeable.

**What was built** (`src/quant/signals/tradeable.py`):

* `untradeable(panel, as_of, delisted)` — two independent grounds. **Delisted**
  (⚠ *supplied* by the orchestrator from D-07's store, never fetched — QA-126,
  so D-03 does not become a data client) and **stale** (last bar more than
  `STALE_SESSIONS = 2` behind ★ *the panel's own* latest date, never a calendar —
  a market holiday moves every name together and must not bar the universe).
* `apply_exclusions` — the survivors, renumbered, plus `excluded[]` with reasons.
* `assert_something_tradeable` — ⚠ P5: an empty slate raises rather than reaching
  D-12 as *"no opportunity today"*, which is a judgement nobody made.
* `delisted_names()` in `calendar/gate.py` — a **current-state** read deliberately
  outside `check_window`, still filtered by knowability (DE-34).

### ⚠⚠ The bug the first cut shipped with — recorded because the shape recurs

The first implementation filtered `candidates` by the barred set. *Measured:*

```text
barred  : {'AVB': 'delisted 2026-08-17'}
kept    : ['NVDA']
excluded: []          ⚠ AVB barred, and NEVER RECORDED
```

★★ `AVB` and `EQR` **are absent from the day's cross-section** — that is the very
accident this rule replaces — so filtering the candidate list matched nothing and
recorded nothing. **The guard reproduced the silent drop it was written to
prevent.** Fixed by making the **barred set the authority**: `excluded[]` now
carries every barred name whether or not it reached `candidates`. Verified live —
the 2026-08-27 run bars `AVB` and `EQR` by name and reason.

★ *The lesson generalises:* a guard that filters a derived list inherits whatever
the derivation already dropped.

## ~~AB-6 — Delivery never sends~~ — ✅ **WIRED 2026-08-27**

**Status:** ✅ **Victor's decision, and a real send verified.** **Owner:** D-08/D-09. **Rules:** RP-50…52, OR-50.

⚠⚠ **The defect was worse than "never sends".** The `deliver` job reported:

```text
{'job_id': 'deliver', 'status': 'SUCCESS', 'elapsed_s': 0.000278}
artifacts: []
```

★★ **A job asserting SUCCESS for doing nothing** — and what it was asserting was
that the artifact had reached the human, which is **P6**, a constitutional
claim. A silent failure would have been better: it would not have lied in the
record.

**What was built and what Victor chose:**

| | Decision |
|---|---|
| Recipient | `REPORT_RECIPIENT` in the gitignored `.env` — ⚠ read from the environment, **never hardcoded**, and a missing one **raises** rather than falling back to the SMTP user (RP-51) |
| Enablement | behind **`--deliver`**, default OFF — sending is outward-facing |
| Cadence | **every trading day**, actionable or not (RP-52) — ★ silence would otherwise be ambiguous between *nothing to do* and *the run did not happen*, which is what DN-29's liveness monitor exists to remove |
| Failure | **fails the run** (OR-50). ★ The CT-11.7 record is already on disk because `record` precedes `deliver` — *a record written after a successful send is missing exactly when the send failed* |
| Record | `delivery.json` in the run directory (RC-63) |

★ **Verified live 2026-08-27**, run `…03:49:00Z-…-b7130b`: `outcome: "SENT"`,
`delivery_id e5a5f4a52020ece5`, both renderings archived under
`.state/deliveries/` and digest-matched (RP-24). ⚠ The recipient is stored
**hashed** (`recipient_hash`), never in plaintext.

⚠ **The concern in the previous entry stands and is now Victor's to watch**: a
card that lands every morning saying `not measured` (AB-1) and `NOT ACTIONABLE`
(AB-3/RC-58) *trains its reader to ignore it*, which is the failure mode the two
incidents in `CLAUDE.md` describe. ★ It is behind a flag, so the exposure is
chosen rather than inherited.

## ~~AB-9 — The training run asserts a calendar check it never performed~~ — ✅ **CLOSED 2026-08-27**

**Owner:** D-04/D-07. **Rule:** FE-10, CT-7.7.

✅ The stub is gone. The training run calls **D-07's `check_window`** — the same
gate the daily run uses (FE-4) — over its own window.

⚠ **And the run says how much was actually checked**, because `PROCEED` alone
reads as *"checked and clear"* when an `UNCHECKED` class is not a blocker:

```text
  unswept : PROCEED · 0/17 classes CHECKED []          + a warning
  swept   : PROCEED_WITH_FLAGS · 3/17 CHECKED          from 1 081 findings
            ['dividend', 'reverse_split', 'split']
```

★ `--refresh-events` performs the sweep. ⚠ The remaining 14 classes stay
`UNCHECKED` with their reasons — see **AB-14**.

---

# 5. Housekeeping

## AB-7 — `backups/**` awaits review and deletion

176 modules and 59 test files moved there at B7 (BS-37) rather than deleted. ⚠ **Never delete it
without Victor's review.** Deleting it will break
`tests/test_sdd_process.py::test_characterization_tests_are_labelled`, which scans `backups/tests/`.

## AB-17 — ✅ 110 duplicated lines in `entrypoint.py`, removed

**Status:** ✅ **FIXED 2026-08-27.** **Owner:** D-08.

Seven helpers — `_sp500_universe`, `_fundamentals_for`, `_sectors_for`,
`_delisted_for`, `_contract_for`, `_observation_ledger`, `_fmp_client` — were
each **defined twice**, an entire 110-line block duplicated by an editing slip
during the QA-125 wiring. ⚠ Python keeps the **last** definition, so the file
ran correctly and no test could see it.

★ The two copies differed in exactly one place (`_fmp_client`'s early return vs
a conditional, functionally identical), which is why it went unnoticed — and is
also the shape that turns into a real defect the moment someone edits the copy
that does not bind. The **first** block was deleted, so the surviving code is
byte-identical to what was already executing.

## ~~AB-19 — A unit test had become a live daily run~~ — ✅ **CLOSED 2026-08-28**

**Status:** ✅ **Test fixed, store pruned, recurrence made impossible.** **Owner:** D-08.

`test_the_entrypoint_blocks_rather_than_inventing_a_day_t_open` asserted:

```python
assert main(["--as-of", "2026-08-25"]) == 0
```

on the stated premise that *"`_day_bar` returns `None` while D-07's open feed is
unwired"*. ⚠ **The feed was wired since**, so the test had quietly become a
**full live daily run inside the unit suite** — real vendor calls, and a real
CT-11.7 directory written into `.state/runs` on **every `make check`**.

★★ **And the assertion could never notice**, because `EXIT_OK` and
`EXIT_BLOCKED` are **both `0`** (OR-42: blocked is INFO, not failure). *The
assertion held while the behaviour it named had gone* — the same shape as the
`deliver` job reporting `SUCCESS` for doing nothing.

**Three fixes, in increasing order of how much they matter:**

1. **The test** — the condition is forced (`_day_bar → None`), and it now
   asserts the *named* outcome: `OPEN_UNCONFIRMED` on stderr and **no run
   directory written**.
2. **The store** — ★ **44 phantom directories removed** (archived first to
   `.state/runs-pruned-2026-08-28.tar.gz`). They were identified by
   `data_as_of == 2026-08-25`, ⚠ **git-verified as the only literal that test
   ever used**, so the classification is evidence and not a guess. **23 records
   remain: 19 `SUCCESS` and 4 `INCOMPLETE`.**
   ★ The four `INCOMPLETE` runs were **deliberately kept** — RC-59: *a failed
   run is a record, not an absence*, and an index of successes only would make
   every base rate measure the wrong population.
3. **`tests_src/conftest.py`** — ⚠⚠ an autouse fixture points `PIPELINE_STATE`
   at a per-test directory. ★ **The failure was not that one test; it was that a
   test COULD reach production state at all.** A test that genuinely wants the
   real tree must now set the variable and say why, which makes it a visible
   decision instead of an accident.

★ **Measured side effect:** the whole suite went from **223 s to ~16 s**. That
one test was ~200 seconds of live network calls on every check.

## AB-8 — 29 dangling citations to five deleted F-specs

**Rule:** BS-36. Tombstoned, warn-tier in `tools/sdd_audit.py`, and **their ACs were never
migrated** — which is precisely what G-7 forbids and what L5 exists to remedy for the sixth spec.

---

# 6. ✅ RESOLVED — kept, because the shape recurs

## ~~AB-10 — No artifact is persisted and nothing is promoted~~ — ✅ **WIRED 2026-08-27**

**Owner:** D-04. **Rules:** MT-17, MT-19, MT-50.

`.state/models/<artifact_id>/` now holds `manifest.json`, `features.json`,
`estimator.pkl` and `evaluation.json`; `promotion.json` is written **only** when
every required gate passes, and **its absence is the refusal**.
`_incumbent_model()` reads `promoted()`, never the mere presence of a model —
*treating a fitted artifact as licence to score with it is exactly what MT-17
prevents*.

⚠ **The concern this entry was originally raised on still stands, and is now
carried on the record rather than in a chat log.** `evaluation.json` embeds the
INV-017 survivorship note, so a future reader of a *passing* artifact sees what
it passed on.

★ **What still refuses, and correctly:**

| Gate | Verdict | Why |
|---|---|---|
| `ic_significance` | **FAIL** | measured IC below the corrected-SE bar — see §5 |
| `cost_survival` | **NOT_EVALUATED** | ⚠ needs a D-03 **backtest**; **MT-19: D-04 does not evaluate itself**, and scoring it PASS here would be D-04 marking its own homework |
| `breadth` | **NOT_EVALUATED** | ⚠ needs QA-43's **residual-correlation** measure, which is **QQ-11** — *500 correlated names are not 500 bets* |

★★ **So the remaining work is D-03's, not D-04's**: a backtest that produces
gross and net returns after QA-123's 9.95 commission, and an effective-breadth
measure. Until both exist, **no artifact can be promoted by construction** — and
that is the rule working, not a gap.

## AB-11 — `walk_forward_ic` rolled its own IC before it was corrected

**Status:** ✅ fixed 2026-08-27, recorded because the shape recurs.

The first version computed its own mean, its own overlap correction and its own
t-statistic. ⚠ **`quant.metrics.ic.rank_ic` already returned a `CT-3.x ICResult`
carrying `effective_n` and an autocorrelation-corrected SE — and
`ic_significance_gate` reads exactly that**, so the hand-rolled number could not
reach the gate at all. ★ Two implementations of one statistic, and the one
promotion turns on. Recorded because it is **FE-4's defect committed by the
author who had spent the day flagging it in inherited code**.

---

# 7. ★ Measured — the training run, 2026-08-27

The first fit ever performed. Two configurations, and the second is the one that counts.

| | smoke (12 names, 3y) | ★ **full (500 names, 10y)** |
|---|---|---|
| Panel rows · dates | 9 024 · 752 | **1 248 173 · 2 512** |
| Evaluated rows · dates *(after the label join)* | 8 772 · 731 | **1 237 463 · 2 491** |
| Features declared / effective | 59 / 58 | 59 / 58 |
| Mean feature coverage | 0.855 | 0.749 |
| **In-sample** rank IC | 0.757 (t = 25.4) | 0.112 (t = 7.8) |
| **Walk-forward** IC — 5 folds, purge 63d, embargo 5d | 0.069 | **0.0203** |
| — `t` on D-03's `corrected_se` (null) | 1.36 | **4.94 → `ic_significance` PASS** |
| — `t` on the realised dispersion | 1.28 | **1.42 → fail** |
| Per-fold IC | −0.024 · 0.060 · 0.091 · 0.051 · 0.167 | 0.033 · 0.010 · 0.016 · 0.009 · 0.034 |
| Wall clock | 14 s | 754 s |
| **Promoted?** | ⚠ no — all three gates refused | ⚠ **no** — `cost_survival` + `breadth` `NOT_EVALUATED` |

⚠⚠ **The two `t` rows are the same run measured two ways, and they disagree by
3.5×.** See **AB-12** — it is the gate promotion turns on.

⚠ **The two row counts differ by exactly one horizon.** A 21-day forward label
does not exist for the last 21 trading days, so the evaluated set is smaller than
the panel — `2 512 − 2 491 = 21`. ★ Recorded because a single "rows" figure would
have made a **21-day look-ahead and a correctly truncated label set look the
same**; this discrepancy was found by the 2026-08-27 interim verification, not by
a test.

## What the numbers say

★★ **The gap between in-sample and walk-forward is the entire reason the purged
evaluation exists.** 0.757 against 0.069 on the smoke run; 0.112 against 0.020 on
the full one. *An in-sample IC is not a weak result — it is not a result.*

★ **All five folds are positive** on the full run, spanning 2016-2026 — including
the 2020 and 2022 regimes. The smoke run had a negative fold; breadth removed it.

⚠⚠ **And it still fails the gate, for a reason worth understanding.** §5.3b's
minimum detectable IC at `n = 500, T = 2491, h = 21` is **0.0123 at t > 3**, and
the measured **0.0203 is above it** — yet the realised `t` is **1.42**. The
resolution is dispersion: the *observed* per-date IC has `sd = 0.156` against a
null `sd = 1/√(n−1) = 0.045`, i.e. **3.5× the null**. ★ **The MDE is a bar
computed under the null, not a prediction of the realised standard error** — real
cross-sectional IC varies across regimes far more than sampling alone, and that
variance is what the t-statistic pays for.

⚠ **`ic_significance_gate` therefore refuses this artifact, and that is correct.**

## ★ The portfolio simulation — 500 names, 10 years, $100k

| | |
|---|---|
| Strategy, annualised gross · net | **24.91 %** · 24.72 % |
| **Equal-weight universe (benchmark)** | **14.56 %** |
| **Excess, annualised** | **+10.35 %** |
| Trades · fees · drag | 1 408 · $14 010 · **14.01 % of capital over 9.92y** (≈1.4 %/yr) |
| Gates | `ic_significance` **PASS** · `cost_survival` **PASS** · `breadth` **NOT_EVALUATED** |
| Promoted? | ⚠ **no — refused on `breadth` alone** |

★ The measured cost drag (~1.4 %/yr at 1m on $100 k) sits close to §7.1's own
figure of **1.20 %/yr**, which is a check on the cost model rather than a result.

⚠⚠ **A +10.35 % annualised excess should be read with suspicion, not
satisfaction.** Three reasons it is probably overstated, none of them measured:

1. ★★ **Survivorship is asymmetric between the arms.** Today's index has the
   losers removed, and a **ranking** strategy is spared exactly the picks it
   would have got wrong — while the equal-weight benchmark merely holds what is
   left. So the excess is biased **upward**, not neutral (INV-017).
2. ⚠ **Ten names is a concentrated book.** One favourable decade in a top-decile
   momentum-and-quality basket is not a distribution.
3. ⚠ **Costs are commission only.** `proportional_bps = 0.0` and §5.6a's ground
   (b) flips sign at **3-12 bps** — the true drag is larger by an unmeasured
   amount (QA-49).

## What the numbers do NOT say

⚠ The sample is **survivorship flattered** (**AB-3**, INV-017): today's index over
ten years. A signal that *fails* here would fail harder on an honest sample — so
this result is informative in the direction it points. **A signal that passed
would not have been shown to work.**

⚠ `f_market_to_book` is **100 % null** (no market caps wired) and
`f_rd_to_revenue` under 25 % — so 58 features carried information, not 59, and
**FE-37's sector-shaped null pattern is inside the fitted model**.

# 8. Cross-references

| Document | Relevance |
|---|---|
| [`L5-inherited-defects.md`](L5-inherited-defects.md) | the **pre-SDD** register — `pipeline/`'s leftovers, not this release's |
| [`L1-fundamental-analysis.md`](L1-fundamental-analysis.md) | RA-9, RA-30, RA-38, RA-67, RA-136 — AB-1 and AB-2 |
| [`L1-quantitative-analysis.md`](L1-quantitative-analysis.md) | §5.3b breadth arithmetic, QQ-11 — AB-4 |
| [`L1-recording.md`](L1-recording.md) | RC-58 (AB-3), RC-59 and CT-11.7 (AB-6's persistence half) |
| [`L3-build-sequence.md`](L3-build-sequence.md) | BS-23 (AB-5), BS-36 (AB-8), BS-37 (AB-7) |
| `sdd/specs/constitution.md` | **P6** — AB-6; **INV-012/INV-013** — AB-1; **P7** — the training run is research |
| `sdd/design/rel6_design/L1-model-training.md` | MT-30 (the SELECTION horizon), MT-50 — AB-10 |
