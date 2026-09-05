# L3: Build Sequence — turning sixteen documents into running code

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** §17 (G-1…G-7)
> **Closes:** L0 **§17.6**'s *"the migration's phase ordering"* · [`L4-coding-standards.md`](L4-coding-standards.md) **Q-3**
> **Consumes:** L1 ×11 (what each domain is) · L2 ×3 (cross-cutting) · L4 (how files move, §1.4–1.6)
> **Binding:** **ST-1…ST-10**, **CA-0…CA-9**, **G-6/G-7** · **P1** (spec before code) · **P7**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.23.0 | 2026-08-28 | Victor | ★★★ **All 18 event classes accounted for — 5 → 15 CHECKED** (AB-14 ingest CLOSED). Built classes 7, 11, 13, 14, 15, 16 + **DE-72 cadence**; classes **4/7/11 share one EDGAR pass**; class 1 needed **no build** (derived at check time). ⚠⚠ `grades` **ignores `limit`** and `economic-calendar` truncates **non-monotonically** — both caught by probing first (AB-22's rule). ⏸ **New AB-25**: the **four decisions are POSTPONED by Victor** with what each costs recorded — ⚠ *an E2E run that goes green while all four stand proves the plumbing, not the judgement.* |
| 0.22.0 | 2026-08-28 | Victor | ★★ **Classes 9 & 10 ingested — 9 CHECKED + 1 built-but-uncoverable of 18.** ⚠⚠ **AB-24**: `earnings-calendar` **truncates silently at 4 000 rows keeping the LATEST** and reaches **exactly 365 days** — the third distinct way a declared feed has fallen short without saying so. ★ Chunk-and-verify built; an uncovered chunk records no refresh and names its cause. ⚠ **AB-3 now stands for a second independent reason**: earnings cannot backfill a multi-year backtest either. *Live: 2 540 findings, 70 chunks, none truncated.* |
| 0.21.0 | 2026-08-28 | Victor | ★★ **Class 5 `restatement_silent` built — 7 CHECKED + 1 built-but-uncoverable of 18** (AB-23). ⚠⚠ It reports **UNCHECKED and says why**: DE-24 can only detect a silent revision by diffing a dated prior, and **0 of 510 names have one**. ★ DE-24's diff had had no production caller since the B era. ⚠ A second limit is **structural**: no field set carries a period key, so a changed TTM value cannot be told from a new quarter — the finding is flagged `ambiguous` rather than claimed. |
| 0.20.0 | 2026-08-28 | Victor | ★★★ **Event coverage 5 → 7 of 18** — `ma_announcement` (class 12) and `restatement_amended` (class 4). ⚠⚠ **AB-22 — the declared source for class 4 does not carry the data**: FMP's index has **zero `10-K/A`**; rebuilt on EDGAR, which found **48** plus **5 non-reliance 8-Ks** (`ADM` among them). ⚠ Class 12's pair is **S-4 filer/subject, not acquirer/target** — 4 of 6 universe matches were split-offs or divestitures, so every hit is a **candidate** (DE-35). ★★ Two of three classes built against declared sources have not behaved as declared; **the other 10 carry the same assumption**. |
| 0.19.0 | 2026-08-28 | Victor | ★★★ **§6B decisions ruled and class 12 ingested.** `EQR` is a **merger of equals** — established by **search**, not data — and the CIK diff shows a merger of equals and a rebrand as the **same shape**, so it reported one event where **two** names left the universe (DE-68). ⚠⚠ **`AVB` prints `VMRK`'s series from 2026-08-18** and the contamination check now runs in `ingest symbols`. ★ `ma_announcement` ingested — ⚠ but its pair is **S-4 filer/subject, not acquirer/target**: 4 of 6 universe matches were split-offs or divestitures, so every hit is a **candidate** (DE-35). ★ Skill `ticker-went-silent` rewritten **search-first**. |
| 0.18.0 | 2026-08-28 | Victor | ★★★ **§6B IDENTITY built** (row 14). A ticker is a label with a validity interval, not an instrument: **CIK is the anchor**, renames come from a **dated SEC snapshot diff** (free, no vendor), retrieval uses the **current symbol** and ⚠⚠ **never splices** — the overlapping bars agree on OHLC and **disagree on volume**. ⚠ The first detector produced **79 false renames out of 507** because a CIK is a registrant, not a security (**QD-17, fatal on first run**); membership-testing took it to 3. ★ `XOM` proved DE-62: its CIK vanished from SEC's file while Exxon priced normally. |
| 0.17.0 | 2026-08-28 | Victor | ★★ **§0A rows 14-15.** AB-18 diagnosed: **`BK`→`BNY` and `SATS`→`ECHO` are rebrands that STILL TRADE** — concluding *delisted* from silence would have deleted two live names, and ⚠ *the 3-day-stale name was the rename while the 5-month one was the delisting*. New skill `ticker-went-silent`; **D-07 still has no `ticker_change` class**. **Row 15 CLOSED**: 44 phantom run records pruned and a conftest guard added — suite **223 s → 16 s**. |
| 0.16.0 | 2026-08-27 | Victor | ★★ **§0A updated — rows 4 and 13 CLOSED as one amendment.** Delivery is wired behind `--deliver` and **a real send is verified**; the run record now names the model, the universe and the barred names. ⚠⚠ Both defects were the same shape as the register's others: `deliver` **reported SUCCESS in 0.000278 s having sent nothing**, and `inputs_fresh` **reported `true` over zero inputs**. ★ **New row 14 (AB-18)**: five S&P 500 names stopped printing at the vendor, one for **five months**, silently absent from every cross-section until QA-125's guard named them. **New row 15 (AB-19)**: a unit test had become a live daily run writing into the real `.state/runs`. |
| 0.15.0 | 2026-08-27 | Victor | ★ **The S&P 500 sweep ran** — 51 822 findings, 510-name coverage on all four sourceable classes. ⚠⚠ **New row 12 — AB-15**: the `delisting` class is now ingested and **the gate still cannot use it**, because a three-week feed cannot cover a 200-day window; `AVB`/`EQR` are excluded only because they print no bar on the as-of date. *The guard is a side effect.* |
| 0.15.0 | 2026-08-27 | Victor | ★★ **§0A updated — row 12 CLOSED.** The untradeable-name check moved into **D-03** on Victor's decision (**QA-125/126, AC-3.32**, `quant/signals/tradeable.py`): a delisted or stale name is barred **by a check**, not by the side effect of printing no bar. ⚠⚠ **New row 13 — AB-16**: `excluded[]` is recorded on the `Nomination` and **the nomination is never written to disk**, so the barred names survive exactly one process — CT-11.7 declares no such artifact, and the amendment comes first. ★ Also **AB-17**: 110 duplicated lines in `entrypoint.py` (seven helpers defined twice) removed. |
| 0.14.0 | 2026-08-27 | Victor | ★ **§0A updated.** The `delisting` class is ingested — it found **AVB and EQR** in the live universe and the gate **HALTs** on them (**DE-59**: a price adjustment was 'handling' a name that had stopped trading). ⚠ **New row 11 — DE-60**: `delisted-companies` reaches ~3 weeks, so **survivorship cannot be corrected from these sources at all**; that is a gap waiting on a data source, not on code. |
| 0.13.0 | 2026-08-27 | Victor | ★ **§0A updated.** Rows 1, 6 and 7 closed — the breadth gate, train/inference population parity (**OR-49**) and the training calendar check (**AB-9**). Four capabilities added to the *built after the plan* table. ⚠ **New row 10 — AB-14**: the corporate-action sweep is runnable and **unscheduled**, and only **3 of 17** event classes are swept. ★ The first model is promoted, with the three reasons a PASS is not a finding stated beside it. |
| 0.12.0 | 2026-08-27 | Victor | ★★ **New §0A — where the build actually stands**, placed *before* the milestone plan because the plan says what was intended and §0A says what exists. ★ **B0-B7 are all built**; seven capabilities were added *after* the plan and appear nowhere in the milestone table — the **61 features**, the **ledger writes**, the **run record**, D-01's **assembler**, the **training run**, the **artifact store**, the **portfolio simulation**. ⚠ **Nine items are left undone** and each names its owner and blocker; six of them are open questions or Victor's decisions rather than code. |
| 0.11.0 | 2026-08-27 | Victor | ★ **BS-40 — `L6-as-built-remaining.md` created.** Release 6's own carry-forward register (`AB-1…AB-8`), distinct from L5's pre-SDD one. ⏸ **AB-1/AB-2 postponed by decision** (confidence and claim-binding: *"needs mathematical consideration, logic/algorithm reconsideration and experiment"*). |
| 0.10.0 | 2026-08-25 | Victor | ⚠⚠ **B7 opened; the deletion half is deferred to Victor (BS-35).** ★ **BS-18's migration performed**: `F0`'s defect log — deleted 2026-08-20 with **nothing carried over** — is recovered from git into **`L5-inherited-defects.md`**, preserving the two OPEN defects (**D-19** enterprise-value-per-share, **D-16** `rsi_14`). ⚠ **BS-36**: a new `spec pointers resolve` check finds **29 dangling citations to the six deleted F-specs across 11 live L-specs** — G-7 requires migration first, and only F0's happened. **BS-35** records B7's unmet preconditions with measurements. |
| 0.9.0 | 2026-08-25 | Victor | ⚠⚠ **`CT-11.4 BookState` was assigned to NO milestone.** B1 built *"enough of D-11 to hold"* the journal, calibration and counterfactual store — **the book was not among them** — and **BS-9's amendment binds the SOURCE rather than a milestone**, saying only that the book lands *"before B4"*, so nobody owned it and **B4 shipped without it**. D-05's step 0 is `RECONCILED?` against that contract, so **B5 could not start**. **BS-15b** opens B5 with the book. §3A's heading corrected to B4.1…B4.8. |
| 0.8.0 | 2026-08-23 | Victor | ⚠ **§3A.2 assigned AC-1.59 TWICE, with contradictory dispositions.** B4.6's range *1.41–1.61* swept it in while the *(deferred)* row names it explicitly as **blocked on D-02** publishing a change decomposition (BS-30). An implementer following the range would build a D-02-blocked AC. ★ **B4.6's range is now enumerated** — `1.41–1.58, 1.60, 1.61` — because **1.60 (vintages) and 1.61 (D-01 assembles no peer set) need no peer set to exist**, while 1.59 does. |
| 0.7.0 | 2026-08-23 | Victor | ⚠ **B3 readiness — BS-11 and BS-28 collide, and four contracts could not express what B3 needs.** ★★ **BS-33**: the walking skeleton's card is **informational, `actionable: false`**. BS-11 blesses a constant-`PASS` stub; BS-28 and `L1-reporting` **RP-13** forbid a verdict reaching a human with no stability — and a stub has none. **INV-6/DN-22 already allow explicitly non-actionable output**, so the skeleton walks without claiming to be a recommendation. ★ **BS-34**: a stub reports absence as absence and never fabricates `k` or confidence. Cascaded: **OR-43** (`stubs[]` — BS-27 had no manifest field), **DN-38** (`alerts_status` — D-05 must refuse with no book, RK-29), **CT-7.7 `report_id`** (D-02's `calendar_check_id` referenced nothing), **QA-121** (a pre-model ranker is still hashed). |
| 0.6.0 | 2026-08-23 | Victor | ⚠ **BS-9 amended — the capital base does NOT land at B2.** It read *"read from D-11 **at B2**"* while **B2's own build list and done-when name D-07 only**; the capital base is **D-11's** (`L1-recording.md` **RC-19**, `src/recording/capital/`), it reads `book_state.nav_base` from a **reconciled book B1 did not build**, and its first consumer is **D-03's backtest at B4** (QA-107). ★ **The rule binds the SOURCE, not the milestone** — that distinction is what the original wording lost, and B2 was being scoped to build most of another domain on the strength of one clause. §4's B2 row corrected to match. |
| 0.5.0 | 2026-08-23 | Victor | ⚠ **BS-3 superseded — arrival capture is NOT built.** It made the capture *first among the three* while `L1-recording.md` §7 had closed **QC-5** as *"won't do"* **on the same day**; neither document cited the other, and the contradiction surfaced only when B1 was scoped for implementation. **BS-3a**: two clocks, not three — and what retired it was **structure, not cost** (RC-38: split tranches fill within seconds at an identical price, so there is no gap to measure). ★ **BS-3b**: the **journal** is the clock that can start today — `CT-11.6` allows `thesis_version: null`, so decisions are recordable before D-01 exists and become RA-59's calibration sample. B1's build list and done-when updated. |
| 0.4.0 | 2026-08-22 | Victor | ⚠ **Consistency pass — five gaps closed.** ★ **BS-23 amended: SPECIFYING and BUILDING D-10 now have different triggers.** L3 read as though both happened at B3; Victor deferred *implementation* until the pipeline runs stably, which is **post-B6** — a thin walking skeleton with a stub gate is not a stable pipeline, and the two dates were being read as one. **BS-23a** points at the intent capture that partly discharges the specifying half. ★ **New B4.8 — the relay.** §3A's slice table stopped at AC-1.71 while D-01 now carries ACs to **1.85**; the relay's thirteen were in no slice. **BS-30a**: it is the only D-01 slice that *reduces* running cost rather than adding capability. ★ **BS-15a**: D-05 now has a stated sequence (§4A) — build B5 against it, not against the list of measures. ★★ **BS-31/BS-32 — a domain is not done until it has a blueprint**, enforced by three new `sdd_audit.py` checks. |
| 0.3.0 | 2026-08-21 | Victor | ★ **New §3A — the D-01 build slice (B4.1…B4.7).** ⚠ **B4 said *"D-01 (the real gate)"* in one line, and D-01 now carries 104 rules, 72 ACs and four companion documents — one line is no longer an instruction.** Six slices plus the sector file, each ending in ACs that pass together. ★ **BS-26 is the ordering that is not obvious**: extraction ships **before** the scorecard, because rubric `evidence_required` lists cite extraction IDs — build rubrics first and they name *documents*, which is exactly the RA-66 defect. ★ **BS-28**: a verdict may not reach a human before RA-20/RA-21's fields exist, so B4.5 gates B4.4's output rather than following it. |
| 0.2.0 | 2026-08-18 | Victor | ⚠ **Milestones renamed `M0`…`M7` → `B0`…`B7`** — `M-1`…`M-5` are L0's **mandate rules** and a reader tripped on exactly that collision; the mandate owns the letter. **QY-1 closed: fresh start on `src/`.** ★ And the resolution carries a finding — **arrival capture needs neither tree** (it records a quote at order submission), so **BS-3's clock starts today** rather than after B0. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft. **§2 is the argument**: the build order is decided by two constraints, and the second — **the measurement clocks** — inverts the usual instinct, because three obligations produce nothing for years and must therefore be built *first*. §4 defines the **walking skeleton**; §7 closes **L4 Q-3**, which turns out to be a non-question. |

> ⚠ **Milestones are `B0`…`B7`, renamed from `M0`…`M7` on 2026-08-18.** `M-1`…`M-5` are **L0's
> mandate rules** ("deliberately takes extra risk — no penny stocks, no derivatives"), and a reader
> asked what *"B1 for the mandate M-1"* meant. **Two ID families one hyphen apart is a collision**,
> and the mandate owns the letter (L0 §16.1). `B` matches this document's `BS-` rule prefix.

## Why L3

The scheme runs **L0** vision → **L1** domain → **L2** cross-cutting module → **L4** standards.
**L3 was never used.** This document sits exactly there: it *consumes* L1/L2 (what to build) and L4
(how files move) and produces neither — it is the **execution order**, and it is the last thing
between sixteen finished documents and someone typing code.

> ⚠ **If Victor prefers this as L0 §18 or a fourth L4, renaming is trivial and the content stands.**
> The tier claim is an argument from position, not authority (G-1).

---

---

# 0A. ★★ WHERE THE BUILD ACTUALLY STANDS — *2026-08-27*

> ⚠ **This section is the one to read first**, and it is deliberately placed
> before the milestone plan. The plan below says what was *intended*; this says
> what **exists, runs, and is measured**. Where they differ, this section wins
> and the divergence is named.

## B0-B7 — the declared sequence

| Milestone | State | ⚠ What is NOT what the plan assumed |
|---|---|---|
| **B0** Foundations | ✅ | — |
| **B1** Start the clocks | ✅ | — |
| **B2** Data spine | ✅ | ⚠ **DE-50/54/55 found later**: EDGAR had **never successfully fetched** (gzip), sub-penny prices dropped whole tickers, and the **YTD→discrete conversion EDGAR was chosen for had never run** |
| **B3** Walking skeleton | ✅ | ★ The card now runs end-to-end daily, `daily_inference@v7`, **13 jobs** |
| **B4.1-4.8** Depth (D-01) | ✅ built | ⏸ **AB-1/AB-2**: B4.2's extraction and B4.3's scorecard are **built, tested, and not called by authoring** — confidence is `not_measured` and **claim-binding does not run on the narrative** |
| **B5** Risk & sizing | ✅ built | ⏸ **AB-3**: no account can produce a `COMPLETE` risk pass — every one holds a CAD/CDR position that is `402` |
| **B6** Orchestration | ✅ | ★ 13 jobs; **`book`, `observe`, `thesis`, `record`** added after the plan |
| **B7** Cutover | ⚠ half | ★ the move happened (BS-37); ⏸ **AB-7** the deletion awaits Victor |

## Built after the plan — ★ none of this is in the milestone table below

| What | Where | State |
|---|---|---|
| **The 61 features** §5.3 declares | `price_ohlcv@v1` (14) + `fundamental@v1` (47) | ✅ **61/61**, D-02 published **two** before this |
| **The ledger writes** | `data_engine/ingest/` | ✅ facts + Class-B; `DataEngine` read ledgers **nothing wrote** |
| **The run record** CT-11.7 | `recording/artifacts/` | ✅ **P6 was unmet** — every run evaporated at exit |
| **D-01's assembler + WF-1** | `bundle/for_ticker.py`, `thesis/author_for.py` | ✅ live, k=3 |
| **The training run** | `src.models.train` | ✅ **`fit()` had never been called** |
| **Artifact store + promotion** | `models/artifact/store.py` | ✅ append-only; **promotion refuses** |
| **The portfolio simulation** | `quant/backtest/portfolio.py` | ✅ **`cost_survival` could not be reached before it** |
| **Effective breadth** QA-43 | `quant/metrics/breadth.py` | ✅ the last `NOT_EVALUATED` gate |
| **Model-driven ranking** | `models/infer/rank.py` | ✅ **a model was promoted and the card still used a formula** |
| **The store sweeps** | `data_engine/ingest/__main__.py` | ✅ §6A's maintenance, which nothing could invoke |
| **The §6A gate, shared** | `data_engine/calendar/gate.py` | ✅ one implementation; the training run's was **a stub** |
| **Delisting detection** | `data_engine/ingest/events.py` | ✅ found **AVB and EQR** live; the gate HALTs on them |
| **The tradeability guard** | `quant/signals/tradeable.py` | ✅ **the exclusion had been a side effect**; now barred by name, with a reason |
| **Delivery, wired** | `_deliver` + `deliver/email.py` | ✅ a **real send verified**; the job used to report SUCCESS having sent nothing |
| **The run record, traceable** | `recording/artifacts/store.py` | ✅ names the model, the universe and the barred names — it named **none** of them before |
| **`ticker-went-silent` skill** | `.claude/skills/` | ✅ why a name stopped printing — ⚠ **a rename is not a delisting** |
| **§6B identity / security master** | `data_engine/symbology/` | ✅ CIK anchor, CT-7.8 symbol history, class 18 — ⚠ **the first detector gave 79 false renames** |

## ⏳ What is left undone — and who owns each

| # | What | Owner | ⚠ Blocked on |
|---|---|---|---|
| 1 | ~~`breadth` gate~~ ✅ **built** — and it **diverges from QA-43 deliberately** | D-03 | ⚠ **QQ-14** — QA-43's residual measure is `−1/(n−1)` and carries no information |
| 2 | **Confidence + claim-binding** (AB-1/AB-2) | D-01 | ⏸ **Victor deferred to R7** — needs mathematics, not plumbing. ⚠⚠ **PRECONDITION ADDED 2026-09-04** (platform repo `F4` `D5`): when this ships, `CONFIDENCE_FLOOR` starts firing and **some names that previously scored will become `INSUFFICIENT_DATA`**. That is a `PG-2` change — **measure how many and put it to Victor BEFORE it ships**, not after. ★ Recorded here because R7 is where it will be read |
| 3 | **CAD/CDR valuation** (AB-3) | D-11/D-07 | ⏸ **Victor's commercial decision** — the *only* thing keeping the card non-actionable |
| 4 | ~~Delivery~~ ✅ **WIRED** — behind `--deliver`, sent and verified (AB-6) | — | ★ `REPORT_RECIPIENT` from the env; every trading day, actionable or not; a failed send fails the run. ⚠ The job used to report **SUCCESS in 0.000278 s having sent nothing** |
| 5 | **The IC gate's standard error** (AB-12) | D-03 | ⚠⚠ **open question** — the same run gives **t = 4.94 (PASS)** and **t = 1.42 (fail)** |
| 6 | ~~Train/inference population parity~~ ✅ **closed** — one universe on both sides (**OR-49**) | — | — |
| 7 | ~~Calendar check over the training window~~ ✅ **closed** (AB-9) | — | ⚠ but see row 10 |
| 10 | ~~**Schedule the corporate-action sweep**~~ ✅ **INGEST COMPLETE** (AB-14) | D-07/D-08 | ★ **15 of 18 CHECKED**; `price_adjustment_state` **derived at check time** (no ingest needed), `restatement_silent` built and awaiting a 2nd snapshot (**AB-23**), `index_membership` has no source at any price. ★ **DE-72 cadence** answers *what is stale now* by severity, so ⏸ the **cron period** — still Victor's — no longer blocks. ⚠⚠ **AB-22/AB-24**: of the sources probed, **five did not behave as declared** |
| 11 | ⚠⚠ **Survivorship cannot be corrected from these sources** (AB-3, DE-60, **DE-70**) | — | `delisted-companies` reaches **~3 weeks** — pages 1+ are `402`. Every backtest stays `survivorship_handled=False`, and **QA-14 reports that as BIASED** |
| 12 | ~~A delisted name is excluded by SIDE EFFECT~~ ✅ **closed** — the check moved to **D-03** (QA-125/126, AC-3.32) | — | ★ Victor's decision: the domain that owns the ranking owns *"a ranked name must be tradeable"*. `untradeable()` bars on **delisting** (supplied) and **staleness**; `excluded[]` carries the reason |
| 13 | ~~The nomination is never persisted~~ ✅ **CLOSED** — and it was hiding a bigger one (AB-16) | — | ★ **The run record could not name the model that produced the pick.** RC-62…64 + OR-51/52: the nomination folds into `recommendation.json`, `delivery.json` is written, the index gains four columns, the manifest carries real provenance, and **`inputs_fresh` no longer reports `true` over zero inputs** |
| 14 | ~~Two of the five silent names were never delisted~~ ✅ **§6B BUILT** (AB-18) | D-07 | ★ **CIK anchor + SEC snapshot diff** — recovered `BK`→`BNY`, `SATS`→`ECHO` with **no vendor call**; fetch resolves to the current symbol; ⚠⚠ **never splices** (volume disagrees). ✅ **Both decisions RULED 2026-08-28**: `EQR` is a **merger of equals** with AvalonBay (DE-67/DE-68), and the 3 delistings **stay until the next retrain**. ⚠⚠ Ruling it exposed a live defect — **`AVB` prints `VMRK`'s series from 2026-08-18**, a fabricated −2.8 % return under a retired symbol (AB-20) |
| 15 | ~~Phantom run records in `.state/runs`~~ ✅ **CLOSED** (AB-19) | — | **44 pruned** (archived first), 23 kept — ★ the 4 `INCOMPLETE` deliberately, per RC-59. `conftest.py` now isolates `PIPELINE_STATE` so a test **cannot** reach production state. ⚠ Suite **223 s → 16 s** |
| 8 | **D-10 Experiments** (AB-5) | D-10 | ⏸ Victor's trigger |
| 9 | **`backups/` deletion** (AB-7) · **29 dangling citations** (AB-8) | — | ⏸ housekeeping |

## ★ The first model is promoted — and what that does *not* mean

`sha256:85b75744…` · 497 names · 10 years · 61 features · all three gates PASS.
⚠ **Three registered items say why a PASS is not a finding**: **AB-12** (the IC
gate passes on the *null* standard error; on the realised one `t = 1.42` and it
fails), **AB-3/INV-017** (the backtest is stamped `survivorship_handled=False`,
and **QA-14 says such a result is reported as BIASED**), and **QQ-14**.

★★ **Every one of the items above is registered in
[`L6-as-built-remaining.md`](L6-as-built-remaining.md) with its evidence.** ⚠ The
suite passes at **1000+ tests and none of these is a failing test** — they are
behaviour that does not exist, which is exactly why the register is kept.

# 1. WHAT THIS DOCUMENT DECIDES

| | |
|---|---|
| ✅ **In scope** | the order domains are built · what "done" means at each step · when the two trees cut over · **which obligations must start before they are useful** |
| ✗ Out of scope | what each domain *is* (L1) · file-by-file disposition (L4 §1.5) · what to *spend* on (`L2-signal-combination.md` §7B — a spending order, not a build order) |

---

# 2. ★ THE TWO CONSTRAINTS — and the second is the surprising one

## 2.1 Constraint 1 — the dependency graph (obvious)

```text
   D-00 shared ──► everything
   D-07 data   ──► everything analytical
        └─► D-02 features ──► D-03 quant · D-04 models · D-01 research
   D-11 record ──► D-05 risk ──► D-06 sizing
   D-01 + D-03 + D-05 ──► D-12 decision ──► D-09 reporting
   D-08 orchestration ──► invokes all of the above (never computes — OR-1)
```

A topological sort gives `D-00 → D-07 → {D-02, D-11} → {D-03, D-04, D-01, D-05} → {D-06, D-12} →
D-09 → D-08`. **That order is correct and it is not sufficient**, because it says nothing about when
the things with *clocks* get built.

## 2.2 ★ Constraint 2 — the clocks, which run backwards

Three obligations across three specs share a property nothing else in the design has: **they produce
no usable output for months or years, and their clock starts only when the recording starts.**

| Obligation | Spec | Produces value after | Cost |
|---|---|---|---|
| **Calibrate closed theses** | D-01 **RA-59** | ★ **years** — ~250 decisions/yr | **$0** |
| **Record vetoed candidates** | D-12 **DN-19/20** | ★ **~7.8 years** to detect a 5 bps gate effect | ~$0 |
| ~~Capture the arrival quote~~ | ~~D-03 QA-69/70~~ | ⚠ **RETIRED 2026-08-23 — see BS-3** | — |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE NORMAL INSTINCT — BUILD THE VALUABLE THING FIRST — IS       ║
║  EXACTLY WRONG FOR THESE THREE.                                  ║
║                                                                  ║
║  They are worthless on the day they ship and irreplaceable four  ║
║  years later, and NOTHING can recover the interval. A thesis     ║
║  that closed unscored is evidence destroyed; a vetoed name whose ║
║  outcome went unrecorded is a counterfactual that cannot be      ║
║  reconstructed; and V-30 already proved the arrival price is     ║
║  NOT retrospectively recoverable at all — the broker export      ║
║  carries a DATE, not a timestamp.                                ║
║                                                                  ║
║  ★ EVERY MONTH THEY ARE NOT RUNNING IS A MONTH DELETED FROM      ║
║  THE SAMPLE THAT DECIDES WHETHER THIS SYSTEM WORKS.              ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **BS-1** | ★★ **The three clock-bearing obligations are built in B1 — before any analytical domain, before anything renders, and before they are useful.** Their value is a function of *elapsed* time, not of build effort, and it is the only quantity in this project that cannot be bought back later |
| **BS-2** | ★ **A clock-bearing obligation may run against the LEGACY tree.** It records; it does not analyse. Waiting for `src/` to be ready before scoring theses trades years of sample for architectural tidiness — **and G-6 permits it, since `pipeline/**` is still governed and still running** |
| ~~**BS-3**~~ | ⚠ **SUPERSEDED → BS-3a** (2026-08-23). It made arrival capture *first among the three*, on the ground that it is the only one **impossible** to reconstruct. ★ **The premise was right and the conclusion was wrong**, because `L1-recording.md` §7 had already closed **QC-5** as *"won't do"* on the same day — **this document made first what that one had cancelled**, and neither cited the other |
| **BS-3a** | ★★ **There are TWO clocks, not three. Arrival capture is not built** (QC-5 stands; Victor reconfirmed 2026-08-23). ⚠ **BS-1's argument is unaffected for the two that remain** — their value is still a function of elapsed time and still cannot be bought back. ★ **What retired BS-3 was not cost but STRUCTURE**: `L1-recording.md` **RC-38** records the account holder's confirmation that split tranches fill *within seconds at an identical price*, so **there is no intra-order gap to measure** and a capture built for one would record a constant |
| **BS-3b** | ★ **The journal is the clock that can start TODAY**, and it is the one B1 should be judged on. `CT-11.6 JournalEntry` allows `thesis_version: null`, so decisions can be recorded **before D-01 exists** — and those entries become **RA-59's calibration sample** later. ⚠ The other two arms (closed theses, vetoed candidates) need D-01 and D-12, so B1 builds their **stores** and the clock starts when those domains produce records |

---

# 3. THE MILESTONES

```text
   B0  Foundations         no investment logic at all
   B1  ★ Start the clocks  no user-visible value — and it goes first anyway
   B2  Data spine          D-07
   B3  ★ Walking skeleton  thin end-to-end: a real card from src/
   B4  Depth               D-04, D-03's evaluation protocol, D-01
   B5  Risk & sizing       D-05, D-06
   B6  Orchestration       D-08 replaces the B3 thin runner
   B7  Cutover             ownership.yaml moves, pipeline/ dies
       └─► D-10 SPEC unblocks at B3; ⚠ D-10 CODE waits for a stable
           daily cadence — post-B6 (BS-23, decided 2026-08-22)
```

## B0 — Foundations

**Build:** `src/` skeleton · **D-00** ([`L2-shared-infrastructure.md`](L2-shared-infrastructure.md) +
[`L2-shared-money.md`](L2-shared-money.md)) · CI.

| ID | Rule |
|---|---|
| **BS-4** | ★ **The checked import edges go in CI at B0, not later** — ST-1/2/5/9/10, OR-3, SI-1, CA-1/CA-2. **They are cheap on an empty tree and expensive on a full one**, and their whole purpose is to prevent an architecture that has already been built wrong |
| **BS-5** | ★ **Each check ships with a test that deliberately violates it and asserts the check fires** (L4 **IM-3**). A structural rule that cannot fail is worse than none — it reports safety it never verified |

**Done when:** `src/` exists; `Money` and the gateway are usable; **a deliberate import violation
fails the build**; the SDD consistency audit runs green in CI.

## B1 — ★ Start the clocks

**Build:** ~~arrival-quote capture~~ *(retired — BS-3a)* · the **decision journal** (**CT-11.6**,
startable today — BS-3b) · thesis calibration scoring (**RA-59**) · the counterfactual store
(**DN-19/21**) · enough of **D-11** to hold them.

| ID | Rule |
|---|---|
| **BS-6** | ★ **B1 ships with no user-visible change and that is expected.** A milestone justified by a clock rather than an output is the one most likely to be skipped, and skipping it is unrecoverable (§2.2) |
| **BS-7** | **The counterfactual store is append-only from day one** (DN-21, INV-006). A rejected-name history that can be edited is the most tempting record in the system to edit |

**Done when:** a decision can be journalled today and is append-only (**AC-11.15**); the
counterfactual store accepts a `CT-12.2 VetoedCandidate` and refuses a revision (**DN-21**, BS-7);
and outcome marking runs on the **same horizon and open anchor** for both arms (**DN-20**).

⚠ **Two of those three cannot be exercised end-to-end until D-01 and D-12 exist.** B1 builds the
receptacles and the marking machinery; **BS-3b** is why that is still worth doing now, and the
journal is the part that starts accruing immediately.

## B2 — Data spine

**Build:** **D-07** ([`L1-data-engine.md`](L1-data-engine.md)) — EDGAR/FMP routing, PIT, the
calendar check (§6A), `adj_open` (**QA-84**) and its ex-dividend check (**QA-91**).

| ID | Rule |
|---|---|
| **BS-8** | ★ **`adj_open` is built at B2, not when the anchor migration needs it.** `price_data.parquet` has **no adjusted open** (D-03 §5.9.1d), so QA-71's whole label change is blocked on a column that does not exist — and it is D-07's to produce |
| **BS-9** | **The capital base is read from D-11 — never from a literal** (**QA-107**), so no percentage figure downstream is ever computed against one. ⚠ **Amended 2026-08-23: it does NOT land at B2.** This rule said *"at B2"* while B2's build list and done-when name **D-07 only**; the capital base is **D-11's** (`L1-recording.md` **RC-19**), it reads `book_state.nav_base` from a **reconciled book B1 did not build**, and its first consumer is **D-03's backtest at B4**. ★ **The rule binds the SOURCE, not the milestone** — it lands with D-11's book, before B4 |

**Done when:** the calendar check runs against live FMP; the panel validates against its contract;
`adj_close/close` and `adj_open/open` agree on every ex-dividend date.

## B3 — ★ The walking skeleton

**The most important milestone, and the one to keep thin.** One ticker, one feature, one horizon,
a trivial composition, a real card.

```text
   D-07 ─► D-02 (ONE feature) ─► D-03 (a rank) ─► D-12 (compose) ─► D-09 (a card)
                                       ▲                 ▲
                                D-01 (a stub gate)   D-05 (a stub alert)
```

| ID | Rule |
|---|---|
| **BS-10** | ★★ **B3 exercises every domain boundary and nothing deep.** The purpose is to find the seams that are wrong while they are cheap to move. **A build that produces nothing readable for months drifts, and this design has twelve boundaries to get wrong** |
| **BS-11** | ★ **The stubs are real implementations of the contracts, not mocks.** A D-01 gate that always returns `PASS` is a legitimate B3 stub; one that returns `None` and is special-cased downstream has already broken **DN-10** — *the identity must not be reachable by omission* |
| **BS-33** | ★★ **B3's card is INFORMATIONAL — `actionable: false` — and that is what reconciles BS-11 with BS-28.** ⚠ **The two rules collide as written.** BS-11 blesses a constant-`PASS` D-01 stub; **BS-28** forbids a verdict reaching a human before RA-20/RA-21's fields exist, and `L1-reporting.md` **RP-13** / `RPT.STABILITY.MISSING` makes *a verdict on the actionable path with no stability* an ERROR. A B3 stub has no stability — it never ran a model. ★ **The tempting fix is the dangerous one**: have the stub emit `k: 1`, `verdict_distribution: {BUY: 1}`, `stability_fraction: 1.0` — *literally true and completely misleading*, **D-15's exact shape, a plausible value manufactured by a placeholder**. ★★ **The resolution costs nothing**: `INV-6` / **DN-22** already permit informational output *"explicitly marked non-actionable"*, and RP-13's error is scoped to *the actionable path*. So B3 delivers a real card, through the real renderer, over the real boundaries — and it does not claim to be a recommendation. **The first actionable card is B4.5's**, which is exactly where BS-28 put it |
| **BS-34** | ★ **A stub never fabricates a graded field.** The B3 gate emits a real `CT-1.4` with `status: PASS`, and its `grade` block reports **absence as absence** — no invented `k`, no invented confidence. ⚠ Paired with **OR-43**: the stub is declared in the RunManifest (BS-27), so the record and the artifact say the same thing. **A stub is legitimate; a stub that reads like a result is the defect** |
| **BS-12** | ★ **B3 runs on a thin orchestration shim, not D-08.** Building D-08 properly before there is anything to orchestrate inverts the dependency — and OR-1 makes the shim trivially replaceable, since orchestration invokes and never computes |

**Done when:** ★ **a card produced entirely by `src/` reaches your inbox for one ticker**, carrying
a `RunManifest` (**OR-9**) and a verdict traceable to an input verdict (**DN-1**).
⚠ **The card is `actionable: false`** — **BS-33**. It exercises every boundary and claims nothing;
the first *actionable* card is B4.5's, per **BS-28**.

## B4 — Depth

**Build:** **D-04** (training, parity, promotion) · **D-03**'s evaluation protocol (§7) and
HorizonSet v1 · **D-01** (the real gate, `k_cov = 3`, both sampling policies).

| ID | Rule |
|---|---|
| **BS-12a** | ★ **D-01's own slicing is §3A (B4.1…B4.8)** — this line used to read *"D-01 (the real gate)"* and that is no longer an instruction |
| **BS-13** | ★ **`τ` is measured here, and three decisions are waiting on it** — `δ` (**QA-110**, provisional at 2.19), §5.8.5b's superseded consistency claim, and **QA-112**'s headroom check that `δ < E[max z]`. **Measure `τ` before tuning anything that depends on it** |
| **BS-14** | ★ **The anchor migration runs BOTH label sets for one evaluation cycle** (**QA-82**), converting an unmeasurable *"not comparable"* into a measured translation factor for every pre-migration result |

## B5 — Risk & sizing · B6 — Orchestration · B7 — Cutover

| ID | Rule |
|---|---|
| **BS-15** | **D-05 then D-06** — D-06 consumes D-05's `P` and `D` factors, and **`D` (drawdown) is computable from D-11's book alone** (**RK-21**), so it lands early and cheaply |
| **BS-15b** | ★★ **B5 opens by building `CT-11.4 BookState` and its reconciliation, because no milestone ever claimed it.** ⚠ *Added 2026-08-25 opening B5.* **B1's build list** names the journal, calibration scoring, the counterfactual store and *"enough of D-11 to hold them"* — **not the book**. B2–B4 name other domains. **BS-9 says the capital base "lands with D-11's book, before B4"** — ★ **and B4 shipped without it**, because BS-9 binds a *source* rather than a milestone and no milestone picked the book up. **D-05's step 0 is `RECONCILED?` against `CT-11.4`** (RK-0, RK-29), so B5 cannot begin without it. ★ Placed here rather than retro-fitted into B1: **it is B5's blocker and nothing earlier needed it**, which is also why nobody noticed |
| **BS-15a** | ★ **D-05 now has a stated runtime sequence** — `L1-risk-management.md` **§4A**, added 2026-08-22 because it did not exist and an agent would have invented one. ⚠ **Build B5 against it, not against §5–§9's list of measures**: the two load-bearing rules are **RK-29** (never compute on an unreconciled book — the *last good book* fallback produces a correct-looking report about yesterday) and **RK-30** (alerts emit only from a complete pass, because silence from a risk desk is a claim) |
| **BS-16** | **D-08 replaces the B3 shim** — full manifest, retry classification, budgets, the 10:00 ET cadence (§5A) |
| **BS-17** | ★ **Cutover is per domain, not big-bang.** `ownership.yaml`'s glob moves **in the same commit** as the code (**ST-8**) — *"the highest-risk step in the whole migration"*, because a stale glob matches nothing and the `sdd_gate` hook **fails open silently** |
| **BS-18** | ★ **An F-spec is retired only when the code it governs is deleted, and its ACs migrate into the receiving L-spec first** (**G-7**, L0 §17.5). ⚠ **`F0`'s defect log — including the open `D-19` net-debt defect — must be carried over, not left to die with `pipeline/`**. ✅ **Carried over 2026-08-25 into [`L5-inherited-defects.md`](L5-inherited-defects.md)** — ⚠ *recovered from git, because **F0 was deleted on 2026-08-20 (`e053786`) before anything migrated it**, leaving 26 files pointing at a spec that does not exist and the two OPEN defects (**D-19** net debt, **D-16** `rsi_14`) recorded nowhere authoritative* |

---

# 3A. ★ THE D-01 BUILD SLICE — B4.1 … B4.8

> ⚠ **Why this section exists.** B4 above says *"**D-01** (the real gate, `k_cov = 3`, both sampling
> policies)"* — one line, written when D-01 was a short spec. It now carries **104 rules, 72
> acceptance criteria, 12 error codes and four companion documents**. *"Build D-01"* is a scope, not
> an instruction, and the same staleness this document warns about elsewhere had reached it.

## 3A.1 What lands before B4

| **BS-35** | ★★ **B7's preconditions are NOT met as of 2026-08-25, and the deletion of `pipeline/` is Victor's call, not an implementer's.** ⚠ *Added opening B7.* Measured, not asserted: **59 of 60 files under `tests/` import `pipeline`** — deleting the tree deletes the suite that currently proves anything works; **`src/` declares zero entrypoints** (`grep -rl 'if __name__' src/` → 0), so nothing runs in its place; **`src/models/` holds one file** (D-04 is unbuilt), so the B6 graph cannot reach a trained model; and **B6.1** records that nothing dispatches `invoke`, so the real graph has never driven the domains. ★ **The migration half of B7 is separable from the deletion half and was done first**: F0's defect log is carried over (BS-18), and a new `spec pointers resolve` audit check reports the rest |
| **BS-37** | ★ **B7's cutover was performed as a MOVE, not a delete** (Victor, 2026-08-25): `pipeline/**`'s 176 modules → `backups/pipeline/**`, its 59 test files → `backups/tests/**`, **structure preserved**, restorable with one `mv`. ⚠ **183 MB of non-Python artifacts remain under `pipeline/`** (parquet, models, reports) — they were not part of the move and are Victor's to dispose of. ★ **`tests_src/` was untouched by the move — 739 passing before and after** — which is the first direct evidence that the new tree carries **no dependency on the old one**. ★ **BS-18's migration ran first**: the yfinance ban (CLAUDE.md's pinned rule) moved to `tests_src/test_data_source_precedence.py` rewritten against `src/`, because **the rule outlived the tree it was written against** |
| **BS-39** | ✅✅ **THE PIPELINE RUNS END TO END ON LIVE DATA, 2026-08-26.** `python -m src.orchestration.entrypoint --as-of <date>` fetches **130 declared universe names** from FMP, assembles one `CT-7.1` panel, and drives **all nine jobs of the B6 graph** — D-07 calendar check → D-07 prices → D-02 features → D-03 rank → {D-01 gate, D-05 alerts} → D-12 compose → D-09 render → deliver — to a `DisciplineCard` in **37 seconds**. ⚠ **`actionable: false`** (BS-33): D-01's gate is still the declared stub and the card claims no action. ★ The run is **blocked, not degraded**, by every precondition on the way — trading day, settled day-T open, model anchor, cadence window — and a single unresolvable ticker **fails it** (DE-13) |
| **BS-40** | ★ **What B0–B7 did NOT finish is a register, not a memory.** [`L6-as-built-remaining.md`](L6-as-built-remaining.md) records Release 6's own carry-forward (`AB-n`), distinct from **L5**, which records what the pre-SDD `pipeline/` tree left behind. ⚠ *A release that ends with "everything passes" has either finished or stopped looking* — the suite pins the behaviour that exists, and every `AB-n` entry is behaviour that does not, so **each states what a reader would wrongly conclude from a green run** |
| **BS-36** | ⚠ **The F-tier deletion left 29 dangling citations across 11 live L-specs**, to all six deleted F-specs. **G-7 requires the ACs to migrate BEFORE retirement** and only F0's have. ★ The check is deliberately **`warn`, not `fail`**: it is a *pre-existing* debt that B7 exists to clear, and a red build would punish every unrelated change until it is. ⚠ A citation that says on its line that its target is deleted counts as a **tombstone**, not a dangling pointer — the defect this check exists for is the **silent** one |
| **BS-38** | ✅ **BS-36 CLEARED 2026-08-25.** All six retired F-specs are tombstoned in `L5-inherited-defects.md` §6 with what each governed and where its content went, and **29 citations across 12 live documents now say on their own line that the target is retired** (**DF-4**). ★ **Four were not prior art**: `CT-3.2` — the reality-probe record D-07 §6A.4's live FMP probe is built on — plus F3's three test tiers and `CT-3.3`, all carried into L5 §5. ⚠ *Recoverability is not migration*: a citation that resolves only through `git show` is one a reader cannot follow |
| Where | D-01's contribution | Why there |
|---|---|---|
| **B1** | ★ **RA-59 calibration scoring** — every closed thesis scored against its realised outcome | **BS-1.** It is clock-bearing, costs `$0`, and its value is a function of *elapsed* time. **BS-2** permits it against the legacy tree |
| **B3** | ★ **A stub gate** — a real `CT-1.4 GateVerdict` emitter that always returns `PASS` | **BS-11.** A real implementation of the contract, never a mock. It exercises the D-01 → D-12 seam while it is still cheap to move |

## 3A.2 The slices

| Slice | Builds | ACs that must pass together | Blocked on |
|---|---|---|---|
| **B4.1** | ★ **The bundle and the seam** — `bundle/`, content hashing, determinism, the gateway import boundary, `CT-1.2 AnalysisRun`, degraded handling | AC-1.1, 1.2, 1.7, 1.10, 1.11, 1.27, 1.38, 1.39, 1.40 | D-07 (B2), D-00 (B0) |
| **B4.2** | ★ **Extraction and the citation spine** — `filings/`, `claims/`, the E-blocks, RA-6 source checks, evidence spans, the **deterministic** X-01/X-02 | AC-1.3, 1.4, 1.5 | B4.1 |
| **B4.3** | **The scorecard** — `scorecard/rubrics/`, criterion selection, `evidence_coverage`, the confidence floors | AC-1.29, 1.30, 1.31, 1.34 | ★ **B4.2** (BS-26) |
| **B4.4** | ★ **Authoring and the real gate** — staged bundle views, Stage A→D, falsifier-before-verdict, bear case, the `CT-1.4` mapping. **Replaces the B3 stub** | AC-1.6, 1.12, 1.13, 1.14, 1.15, 1.18, 1.32, 1.33 | B4.3 |
| **B4.5** | ★ **Monitors and the card fields** — `monitor/`, the perturbation probe, `not_yet_calibrated`, forecast-voice lint, length caps, monitor-report completeness | AC-1.8, 1.9, 1.16, 1.17, 1.19–1.26, 1.28, 1.72 | B4.4 — but ★ **gates it** (BS-28) |
| **B4.6** | **Invalidation, calendar and events** — `invalidation/`, `calendar/`, `events/`, the 8-K router, the move review, the weekly sweep | AC-1.35–1.37, 1.41–1.58, 1.60, 1.61, 1.65 | B4.4; D-07's 8-K feed |
| **B4.7** | ★ **The sector evidence file** — `sector/`, the four-way guard | AC-1.66–1.71 | ★ **B4.5** (BS-29) |
| **B4.8** | ★ **The relay** (§4B) — prompt composition, the queue, the ingest and its verification | AC-1.73–1.85 | B4.3 (coverage) + B4.4 (archetype, gate mapping) |
| *(deferred)* | **Fundamental attribution** §10B.5 | AC-1.59, 1.62, 1.63, 1.64 | ⚠ **D-02** must publish a *change* decomposition on `peer_context` — not a D-01 slice at all (BS-30) |

## 3A.3 The four ordering rules — and only one is obvious

| ID | Rule |
|---|---|
| **BS-25** | ★ **B4.1 ships the whole reproducibility apparatus before the first judgement exists** — hash, run record, decoding parameters, prompt version, degraded handling. It produces **no analysis at all**, which is what makes it look skippable. ⚠ **Without it, §7's entire measurement programme has nothing to key on**, and every judgement built before it is unattributable after the fact |
| **BS-26** | ★★ **Extraction ships BEFORE the scorecard, and this is the ordering that is not obvious.** A rubric level names its `evidence_required` (RA-32) and `evidence_coverage` counts **successfully extracted items** (RA-65/66). **Build rubrics against a system with no extraction and their `evidence_required` lists will name *documents*** — which is precisely RA-66's defect: *"a 10-K that is present but from which the required number could not be pulled is not evidence."* ★ **The build order is what makes the rule enforceable rather than aspirational** |
| **BS-27** | **The B3 stub is replaced in B4.4 and not before.** Until then D-12 receives a constant `PASS`, and **that fact is written into the `RunManifest`** rather than being silently true. ⚠ A stub that is indistinguishable from a real gate in the record is how a placeholder survives into production |
| **BS-28** | ★★ **A verdict may not reach a human before RA-20/RA-21's fields exist.** B4.5 is listed after B4.4 in dependency order and **gates it in shipping order**: a verdict rendered without its stability figure and with a bare confidence number is `D-15` with better plumbing. **B4.4 may be merged; its output may not be delivered until B4.5 lands** |
| **BS-29** | ★ **The sector file (B4.7) lands after the monitors, not before.** It is a **shared prior by construction** (RA-102) — one input feeding every thesis in the industry — so a defect in it is a correlated defect. **RM-16 is the instrument that would see that, and it ships in B4.5** |
| **BS-30a** | ★★ **B4.8 is the only D-01 slice that REDUCES running cost instead of adding capability.** The relay moves the expensive deep-tier authoring onto a flat-rate subscription, so **it makes B4.4's API path optional for most names.** ⚠ It still depends on B4.4 — it needs the archetype classifier (RA-123) and the `CT-1.4` mapping — but **once it lands, the cost of covering a name falls sharply**, which is worth knowing when sequencing what comes after |
| **BS-30** | **A slice blocked on D-02 waits for D-02.** ⚠ It is never worked around inside D-01: a ratio computed in a prompt is a defect twice over (RA-45, MP-6, AP-5). §10B.5 is the live example — it needs a *change* decomposition D-02 does not publish yet |

## 3A.4 What "done" looks like per slice

| Slice | Done when |
|---|---|
| **B4.1** | The same `(ticker, as_of)` yields a byte-identical `bundle_hash` twice; a call attempted without one raises; a deliberately degraded response is neither persisted nor rendered |
| **B4.2** | An extracted value absent from its cited span raises **without an LLM being asked**; every factual claim carries a resolvable span |
| **B4.3** | A rubric level whose required evidence was not *extracted* is unavailable to the model; `evidence_coverage` falls when an extraction fails |
| **B4.4** | ★ **D-12 receives a `GateVerdict` that varies with the thesis** — the B3 constant is gone, and every reachable thesis state maps to exactly one status (RA-49) |
| **B4.5** | The monitor report contains **every** `RM-n` as a value or an explicit `not_yet_calibrated`; a verdict cannot render without its stability figure |
| **B4.6** | An 8-K item 4.02 drives `evidence_coverage` to zero for the affected periods; a move trigger without a residual raises; the weekly sweep emits a report on a week when nothing happened |
| **B4.7** | A source-list item missing with no logged reason raises; a schema change without a version bump raises |

---

# 4. WHAT EACH MILESTONE UNBLOCKS

| Milestone | Unblocks |
|---|---|
| B1 | ★ the calibration clock (**CB-10**, the hard blocker on any Bayesian merge) · the gate's falsifiability |
| B2 | `adj_open` ⇒ the anchor migration (QA-71) · the Fact ledger and the calendar check ⇒ every analytical domain. ⚠ **not the capital base** — BS-9 as amended |
| B3 | ★ **D-10's SPEC-WRITING trigger** — *"the first full E2E run is complete and its results evaluated"* (L0 §4.2). ⚠ **Not its build trigger** — see BS-23 |
| B4 | `τ` ⇒ `δ` ⇒ QQ-21's architecture · `IC₀₃` becomes measurable **once `n = 500`** (**CB-21**) |
| B5–B6 | the dynamic risk budget (**QS-1**) · the production cadence |
| B7 | `pipeline/` deleted; F-specs retired per G-7 |

---

# 5. THE PARALLEL BUILD

| ID | Rule |
|---|---|
| **BS-19** | ★ **`pipeline/` keeps running and keeps being governed by its F-spec throughout** (**G-6**). The daily report does not stop while `src/` is built |
| **BS-20** | ★ **`src/` MUST NOT import `pipeline/`** (**ST-1**) — *ever, including temporarily*. The legacy tree depends on the new one via shims; the reverse makes `pipeline/` undeletable and the parallel build a permanent fork |
| **BS-21** | **The test suite is green at every commit** (**ST-7**). A move commit that reddens it means the shim is wrong — which is exactly what the shim exists to reveal |
| **BS-31** | ★★ **A domain is not done until it has a blueprint** — [`sdd/blueprints/`](../../blueprints/README.md), one per domain, recording **what the code does and why THIS construction** among the several its spec would have allowed. ⚠ **This is not an as-built doc** (the carve-out is in `sdd/README.md`): a spec deliberately underdetermines its code, and the blueprint is the layer that omission leaves empty. ★ **Enforced by `tools/sdd_audit.py`** — `blueprint exists per built domain` fails when `src/<domain>/` has code that no blueprint names, `blueprint pointers resolve` fails on a `file.py::symbol` that does not exist, and `blueprint freshness` **warns** when code was committed after its blueprint |
| **BS-32** | ★ **The reason this is a milestone obligation and not a nicety:** this system's failures are **plausible numbers**, not crashes. `_cumulative_fys` had a confident docstring, a passing test and a **41.5 % error**; `D-19` has been emitting an enterprise value per share the whole time. ⚠ **Neither would have been caught by more tests** — both were caught by someone reading what the code was *supposed* to do. **A domain whose reasoning was never written down cannot be audited that way** |

---

# 6. WHAT IS *NOT* BUILT

| ID | Rule |
|---|---|
| **BS-22** | ★ **`backtester.py`'s hard-coded `initial_capital` is not patched** (**QA-114**). The legacy tree is replaced, not repaired |
| **BS-23** | ★ **D-10 is not specified until B3 completes** — the E2E-run trigger, held by ST-2's one-way import rule rather than by a spec (L0 §4.2). ⚠ **Amended 2026-08-22: SPECIFYING and BUILDING now have different triggers.** *"I do not plan to implement D-10 code until the full pipeline runs stably"* (Victor) — which is **post-B6**, once D-08 has replaced the B3 shim and the daily cadence is running, **not B3**. ★ B3 is a *thin* skeleton with a stub gate; a walking skeleton is not a stable pipeline, and the two were being read as one date |
| **BS-23a** | ★ **The specifying half is partly discharged already.** [`L1-experiments-intent.md`](L1-experiments-intent.md) records the intent, audits it against the **1,978 LOC of harness already in `pipeline/ohlcv/experiments/`** (reused per QX-5), and closes six of its own questions. ⚠ **It declares no ACs and governs no path** — the L1 spec still waits for B3 |
| **BS-24** | **L4 §§2–4, 6–9, 11–13, 15–16, 19–25 are not written.** Five sections were chosen because each makes an invariant mechanical; the rest is style `ruff` and `black` settle |

---

# 7. ✅ L4 Q-3 CLOSED — and it was a non-question

> *"Does D-10 move first (shrinking the problem by ~2,000 LOC) or last?"*

**Neither.** D-10 does not move on this schedule at all. Its content is **unknowable before B3**
(L0 §4.2), and **ST-2's one-way import rule means nothing can be blocked by it** — no domain may
import D-10, so its position in the order is unconstrained by every other domain.

★ **The question presupposed that D-10 was on the critical path. The one-way rule is precisely what
takes it off.** *(Same shape as `L1-decision.md` §5.7: the algebra dissolved QB-2 rather than
answering it.)*

---

# 8. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| ~~**QY-1**~~ | ~~Does B1 run against `pipeline/` or wait for `src/`?~~ | ✅ **CLOSED — fresh start on `src/`** (Victor, 2026-08-18). ★ **But arrival capture needs NEITHER tree**: it records a quote at order submission — a ~20-line append-only writer — so **BS-3's clock can start today** without touching `pipeline/` or waiting for B0. The other two clocks (calibration, counterfactuals) wait for `src/`, and B0 is small enough that the delay is weeks |
| **QY-2** | Which **single ticker** is B3's skeleton? | Wants a name with a long clean history, an EDGAR filer class, and a split in-window to exercise **QA-84/91**. **NVDA fits all three** (10:1 in 2024) |
| **QY-3** | Does `n = 500` land at B2 or B4? | **CB-21** says universe expansion is what makes `IC₀₃` measurable — but it also multiplies B2's ETL. Later is cheaper; earlier starts the measurement |
| **QY-4** | Is there a **calendar date** attached to any milestone? | This document deliberately gives none. ⚠ **But §2.2's clocks are measured in years, so "eventually" is a decision with a cost** |
| **QY-5** | `tests_src/` merged at cutover, or kept split? | Inherited from **L4 Q-4**, unchanged |

---

# 9. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` **§17** G-1…G-7, **§17.5** F→D landing table, §17.6, §4.2 D-10 | governance; what this closes |
| `L4-coding-standards.md` **§1.4–1.6**, **ST-1…ST-10**, **§10.1**, CA-0 | migration classes and the file-by-file table this sequences |
| `L1-recording.md`, `L1-decision.md` **DN-19/20/21**, `L1-quantitative-analysis.md` **QA-69/70** | ★ the three clocks §2.2 puts first |
| `L2-signal-combination.md` **§7B** | the **spending** order — distinct from this build order, and dependent on it |
| `L1-data-engine.md` §6A, **QA-84/91** | B2's deliverables |
| `sdd/specs/constitution.md` **P1**, P7 | spec before code; why D-10 is exempt |
