# L1: Domain Specification — Fundamental Analysis (D-01)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-01 · **Seat:** SEAT-2
> **Path:** `src/fundamental/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Depends on:** [`L1-data-engine.md`](L1-data-engine.md) (D-07) ·
> [`L1-feature-engineering.md`](L1-feature-engineering.md) (D-02) · `src/shared/llm/` (D-00)
> **Prior art:** `pipeline/buffett/synthesis/**` (incl. `prompt_alignment.py`, `prompt_stock_analysis.md`),
> `pipeline/buffett/analysis/{news_analyst,llm_filing_parser}.py`,
> `constitution.md` P2/P3/P5, INV-4/INV-8/INV-9, `F0` §12 **D-15**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.26.0 | 2026-10-01 | Victor | ⚠⚠ **§11.2 had no row for an UNMEASURED verdict, and the code defaulted it to PASS**, the exact thing RA-49 forbids (*"a state with no row is a defect, not a default to PASS"*). The PASS row requires a **stable** verdict; a thesis authored once (k=1) has `verdict_stability = null` and is not stable, only unmeasured. **RA-154 added: an unmeasured BUY FLAGS.** It does not VETO, because nothing shows it unstable, and it cannot PASS, because nothing shows it stable. Surfaced by `L8` §8 lesson 8 and `L3` §2.1p item 2. ⓘ The downstream backstop (`assert_actionable_inputs`, RP-13) already refused such a verdict on the actionable path; the defect was that the gate's own record said PASS. |
| 0.25.0 | 2026-08-26 | Victor | ★★ **Class-B evidence reaches the bundle — and RA-14 nearly lost.** **RA-151/152**: `ratios-ttm` mixes 36 operating ratios with **26 price-derived ones**, so the payload is split — `operating_ratios` (visible) vs `computed` (withheld). ⚠ *A reader with EPS and a P/E has the price*: RA-14 can be defeated **without a single price field appearing**. ★ Allowlisted and **enumerated, not inferred** — a substring probe misclassified `financialLeverageRatioTTM`. **RA-153**: the consensus is deliberately not in the bundle. AC-1.97…1.99. |
| 0.24.0 | 2026-08-26 | Victor | ★★ **The assembler §5 always implied — `ticker + as_of` → `EvidenceBundle` — and building it against real EDGAR data found four defects.** **RA-147**: `profile` is not blind-withheld, so dumping FMP's payload would have put `price` and `marketCap` in front of J-11 and J-15 and **defeated RA-14 with every test green** — stripped by allowlist, because a denylist leaks the vendor's next field. **RA-148**: D-01's Class-B consumer is `thesis`; any PIT consumer name makes the profile read raise and **no thesis could ever be written**. **RA-149**: one filing carries its own quarter *and the prior-year comparative*, so `filing_date` ordering fed a **year-stale** period as current. **RA-150**: without D-07's statement tags a fundamental thesis could be falsified only by `mom_21` and `vol_21`. |
| 0.24.0 | 2026-08-25 | Victor | ⚠⚠ **B4.8 readiness — three defects, and one was a gate that silently PASSes.** ★★ **§11.2's stale row named the CLOCK only** (`STALENESS_FILINGS_HOURS`), and B4.6's **RA-71** made staleness **event-relative first** — so a thesis stale because results landed unread, but inside the 48-hour floor, **matched no row and PASSed**, which is exactly the case **AC-1.84** requires to FLAG. Row amended. ★★ **RA-144**: AC-1.77 says the INV-012/013 floors fire *"unchanged"* on a relay, but the floor function took a `CoverageReport` — **a rubric-dimension object a relay cannot produce**. The only readings were to fake one or to write **a second copy of the floors** (FE-4's defect, the one RA-137 had just removed). The floors take a **coverage value**; ⚠ the denominators stay different and must. ★ **RA-143**: RA-118 requires the verification result *"per claim"* and `CT-1.5` stored **three integers** — so a failed ingest could not name which claim contradicted, and a HOLD-capped report could not name what was unverifiable. AC-1.76a/1.77a added. |
| 0.23.0 | 2026-08-25 | Victor | ⚠⚠ **B4.7 readiness — §10C's four guards, and three of them had nothing to check against.** ★★ **RA-140**: RA-100 requires a *"fixed, versioned schema"* and **no schema was ever declared**, so AC-1.69 could not detect drift — the hardest of the four guards was the one with no instrument. **CT-1.6** declares it and `schema_fingerprint` makes drift arithmetic. ★★ **RA-141**: RA-99 says *"ordered by date"* while RA-101 gives a capacity row **several** dates — announcement order buries yesterday's transition, latest-transition order **mutates the sort key**. The file's unit is now the dated **record**, and the row is its projection. ★ **RA-142**: RA-102's *"declared on every artifact that consumed it"* was implemented as a **pin inside `bundle_hash`** — verifiable, not readable. `CT-1.1.sector_files[]` added, the same seam defect as CT-7.7's `report_id`. **CT-1.7** declares the source list RA-98 measures completeness against. AC-1.68a/1.69a/1.71a added. |
| 0.23.0 | 2026-08-26 | Victor | ★★ **RM-1's k-run probe wired to REAL authoring, and the live run found two defects nothing else could.** **RA-145**: J-15 tells the model to choose a field *"from the supplied list of available observables"* and **nothing supplied one** — four well-formed falsifiers named no field, all failed RA-35, and the thesis raised. ★ *The model diagnosed it: "this bundle carries filing line items and disclosure text only."* **RA-146**: the list then had to become **its own part kind**, because `BLIND_WITHHELD_KINDS` strips `computed` wholesale and **J-11 and J-15 are exactly the blind calls** — ⚠ RA-14 withholds **anchors, not vocabulary**. |
| 0.22.0 | 2026-08-25 | Victor | ⚠ **RA-72 marked a card field against an undeclared threshold.** *"A thesis authored inside **the window** before a scheduled event…"* — no spec, L0's config block included, said how wide the window is, so `pre_event` could not be computed without inventing a number. **RA-139** declares `PRE_EVENT_WINDOW_DAYS = 10` calendar days, sized from RA-72's own four-days-before-results case at the low end and the ~91-day reporting cycle at the high end — ★ *a window wide enough to be always-on marks nothing*. |
| 0.21.0 | 2026-08-23 | Victor | ⚠⚠ **B4.6 readiness — RA-83 was not computable against RA-65.** *"Item 4.02 drives `evidence_coverage` for the **affected periods** to zero"* — but **RA-65's `extracted` set is a set of `evidence_id`s with no period axis**, so a non-reliance filing naming FY2024 could invalidate **everything** or **nothing**, with no third option. ★ The extracted item already carries its `period`; **the coverage projection dropped it**. **RA-138**: withdrawal is by `(evidence_id, period)`, so coverage recomputes naturally and RA-83 needs no special case — and ⚠ **an item with no period is withdrawn by any 4.02**, because an undated fact cannot be shown to lie outside the affected range. AC-1.52a added. |
| 0.20.0 | 2026-08-23 | Victor | ⚠ **B4.5 readiness — two defects.** ★★ **RA-136**: RA-30 gives a monitor **one** way to decline, *"not yet calibrated (N=…)"*, **which promises the number is coming** — but **RM-1's sampling half can never be computed on this tier** (`claude-opus-5` rejects `temperature`; GW-8a/GW-10), so reporting it that way tells a reader to wait for a number that will never arrive. **`not_measurable` added**, with its reason, and `CT-1.1.verdict_stability` now names **which probe** produced it — RA-62 asks for two figures and the contract carried one. ★★ **RA-137**: **RA-26/RA-27 are D-01's rules** and the wordlist was implemented only in D-09 — two deterministic copies of one list is **FE-4's defect in another domain**, and the two enforcement points differ in consequence (X-03 fails the run; RP-18 blocks the render). AC-1.25a/1.28a added. |
| 0.19.0 | 2026-08-23 | Victor | ⚠ **B4.4 readiness — two defects, and both are about ORDER.** ★★ **RA-16 said the falsifier and the verdict are *"part of the same structured output"*** — which is the exact failure **§4A.2 step 8** names (*held in memory, the ordering is nominal and a single call could produce both*) and which the master prompt's **J-15 → persist → J-16** split has contradicted since v0.12.0. **One call emitting both satisfies the old wording and buys nothing**: the falsifiers get fitted to a verdict already reached. RA-16 and AC-1.14 amended. ★★ **RA-135 — §11.2's rows OVERLAP**: a stale, confident BUY matches both `PASS` and `FLAG`, so RA-49's *"exactly one status"* was unachievable and *first match wins* would make the answer depend on row order. **The most conservative match wins** — P3 applied inside D-01. AC-1.6a added. |
| 0.18.0 | 2026-08-23 | Victor | ⚠⚠ **B4.3 readiness — `evidence_coverage` was DEGENERATE and the confidence floors could never fire.** RA-65's denominator was *the `evidence_required` list of the level **being selected***, and **RA-32 makes a level whose evidence is absent unavailable** — so every selectable level has full coverage by construction: **the metric was identically 1.0**, or `0/0` for a level declaring no evidence. ★★ **RA-38's 0.3/0.5 floors could therefore never fire, and RA-67's `confidence := evidence_coverage` was a constant** — the whole un-gameable-floor argument rested on a number that could not vary. **RA-65 amended to the UNION over the rubric's levels**; **RA-134** states why: *availability is per level, coverage is per rubric.* §8's example also lost a stale `dimension: pricing_power` field that contradicted §8.1's closed four. AC-1.34a added. |
| 0.17.0 | 2026-08-23 | Victor | ⚠ **B4.2 readiness — three defects, and one of them made X-01 self-referential.** ★★ **RA-131**: the extraction envelope emits a `quote` **and** an `offset`, and **nothing said to resolve the offset** — checking only *value-in-quote* verifies the model against itself, because a model that fabricates both consistently passes. **The offset is the only part of a citation the model cannot also author.** ★ **RA-132**: *"arithmetically derivable"* covered both *reformat one figure* and *combine two*, and the second is D-02's and is the `_cumulative_fys` scar. ★★ **RA-9 amended — the enum admitted two kinds while S-3 instructs the model that there are exactly three**, so the prompt asked for a shape the contract could not hold; **RA-133** makes `assumptions[]` a projection with ordinals intact. AC-1.3a/1.3b/1.5a added. |
| 0.16.0 | 2026-08-23 | Victor | ⚠ **B4.1 readiness — `CT-1.2` could not record D-01's only decoding control.** It carried a **flat `temperature`**, which is the shape `CT-0.1` was reshaped away from (GW-9: a flat `null` cannot distinguish *not settable* from *forgotten*), and **no `effort` field at all** — while §6 puts both of D-01's call kinds on the **deep tier**, where `temperature` is rejected with a 400 and `effort` is the only knob. **RA-11's *"a parameter that is not recorded cannot be held responsible"* was unsatisfiable.** ★ **RA-129**: `decoding` transports whole, byte-identical. ★★ **RA-130** resolves a second reading hazard — **AC-1.27** (*never persisted*) against **RA-111** (*the record must distinguish did-not-run from ran-and-failed*): **record that it failed; never record what it produced.** |
| 0.15.0 | 2026-08-23 | Victor | ⚠ **RA-60 corrected — its premise was wrong for this domain.** It required setting `temperature`; **`claude-opus-5` rejects the parameter with a 400 and D-01 is the deep tier**, so there was never a knob to set. ★ **GW-10's conclusion survives and is now over-determined**: the sampling probe is retired not because temperature 0 removes the variance but because **the setting does not exist** — RA-61's perturbation form is the *only* stability probe available here. ★★ **New RA-60a: `effort` is a live decoding control RM-5 does not watch** (`high → xhigh` is not a tier change), which is worse than an unset knob because an unset knob is visibly unset. **§7.4b's box corrected.** |
| 0.14.0 | 2026-08-22 | Victor | ✅ **§4B.5a — overdue relays go STALE** (Victor: *"my responsibility to remember"*). ★ **No new mechanism**: **RA-126** lets **RA-71**'s event-relative staleness do it, and §11.2 already maps a stale thesis to **FLAG** — so an unrun relay annotates the name at the gate without anyone adding a rule. ★ **RA-127: the system reports, it does not chase** — skipping is a decision SEAT-1 is entitled to make, and D-01's obligation is the override obligation: **make it visible and let it stand.** **RA-128:** `overdue` and `stale` are separate counts, because *not yet run* and *no longer trusted* are different states. |
| 0.13.0 | 2026-08-22 | Victor | ★★ **New §4B — THE RELAY**: D-01 composes a complete prompt, Victor runs it manually on a flat-rate Claude Pro / ChatGPT Plus subscription, and pastes the result back. **WF-8/WF-9 added; neither makes an LLM call.** ★ **The framing that settles it: the relay is an EXTERNAL PROVIDER WITH A HUMAN TRANSPORT** — the request is D-01's, the response is an ingested external artifact validated before use. ⚠ **Five guarantees do not survive a chat paste** (RA-1/2 pinning, AP-6 reproducibility, RA-12 no conversational state, RA-14 anchor-strip, RA-6/9 span checks) — each accepted and **labelled**, none waved through. ★★ **The safety case needed NO new rule**: `confidence := evidence_coverage` (RA-67) de-rates it automatically because relayed claims are largely unverifiable, and **AC-1.8 already makes it impossible for a relay report to be the actionable pick** — a single chat response has no distribution. **RA-114…RA-125, CT-1.5, 5 error codes, AC-1.73…AC-1.82.** Prompts in [`L1-fundamental-analysis-relay-prompt.md`](L1-fundamental-analysis-relay-prompt.md). |
| 0.12.0 | 2026-08-21 | Victor | ★★ **New §4A — the runtime workflow, which did not exist.** §4 said what the code *is*, §12 listed methods in no order, and §§5–10C stated rules without saying when any fired: **a reader could implement every rule here and not know what to call first.** ★ **There are SEVEN workflows, not one** (WF-1…WF-7), with distinct entry points and preconditions — **RA-106**: a single `analyse(mode=…)` is how the blind bundle eventually gets handed the full one. ★ **§4A.2's eleven steps carry the rule that forces each position**, and the load-bearing one is **step 5, the Stage-A freeze**: staging without a persisted commit lets Stage B silently revise Stage A after seeing the price, and the anchor-stripping bought nothing. ★ **RA-107: RA-12 already bought intra-stage parallelism** — "no conversational state" makes every call in a stage independent by construction. **RA-110**: a failed step emits `NO_THESIS`, never a partial, never the prior one, never nothing. |
| 0.11.0 | 2026-08-20 | Victor | ⚠ **§1.2 was STALE and is corrected — it showed D-01 reaching SEAT-1 "via D-09" with no D-12 at all.** D-12 Decision arrived in L0 v0.17.0 and **this spec's own v0.2.0 added `CT-1.4 GateVerdict`, "the adapter D-12 consumes"** — the diagram and §3's *depended on by* were never updated, so a reader of §1 saw an architecture the rest of the file contradicts. ★ **New §1.2a states the two paths**: ① `CT-1.4` → **D-12 composes** → `CT-12.1` → D-09 renders (**RA-103** — a direct D-01→D-09 verdict edge would make the renderer the composer, `L1-decision.md` §1.2's *"dangerous one"*); ② the narrative reaches D-09 by **resolving `thesis_ref`** back to `CT-1.1`, referenced never copied (**RA-104**, DN-33, RP-43a), with the analyst's verdict rendered **beside** the composed one, never instead of it. §3 also de-duplicated a `D-07` line introduced in v0.8.0. |
| 0.10.0 | 2026-08-20 | Victor | ✅ **Sector evidence file adopted — §10C, the one funded capability (RA-97…RA-102), with a FOUR-way guard**: a view hides in the prose, the **sampling**, the **ordering** and the **schema**, and they get harder to see in that order — ★ *schema drift looks like maintenance.* ★★ **New RM-16 — thesis-error correlation `ρ̂`**, with the asymmetry that decides what coverage is worth: **`ρ` collapses breadth for LEVEL decisions (13 → 1.6) and cancels exactly for RANK decisions**, where residual noise is `2(1−ρ)σ²` — *smaller* than independent errors would give. Third appearance of QA-93's structure, and **L2's CB-19 re-ranking case is strengthened, not merely spared**. ★ **RA-93 corrected — vintages ARE obtainable**: ALFRED covers CPI/PCE/IP/treasuries free; FMP is the vendor that cannot, not the world (**RA-93a**: capex guidance needs no vintage service at all). ★ **RA-95: one capability, TWO estimators** — the fundamental form is a *difference*, never a fitted `β` on five observations. ★ **RA-96/96a: the peer set has the same vintage problem**, and MU's August fiscal year-end makes a date-aligned peer median wrong on a live watchlist name. |
| 0.9.0 | 2026-08-20 | Victor | ★ **Independent review folded in — attribution is now a GATE, not a refinement (RA-88…RA-94).** ★★ **RA-88: the residual is computed BEFORE the move trigger fires.** A trigger on the raw return measures the sector, and **RA-91 names the consequence** — exiting a sound position because its sector repriced is an allocation call, i.e. **SEAT-1's authority exercised by accident**; the macro view this domain refuses to form re-enters as a *false invalidation*. ★ **RA-89 the clustering diagnostic** costs nothing and needs no factor model. ★★ **New §10B.5 — the same error on the ACCOUNTS (RA-92)**: a scorecard that cannot separate the cycle from the company is wrong on every cyclical name in the same direction, and reports 5/5 stability while doing it. ★ **RA-93 the vintage rule** — compare against the print that existed on the date; where no vintage exists (FMP `economic-indicators`) the result is UNCHECKED-grade, never silently used. |
| 0.8.0 | 2026-08-20 | Victor | ★ **Two new sections — §10A the scheduled calendar, §10B unscheduled events and sudden moves (RA-69…RA-87).** ⚠ **`L1-data-engine.md` §5A.4b already states its calendar is *"consumed by D-01 as thesis-invalidation triggers"*, and §10 contained no reference to a calendar at all** — the gap was one sentence wide. ★ **RA-71 replaces the staleness *timer* with an event predicate**: a thesis is not stale because 168 hours elapsed, it is stale because a scheduled event it depends on happened and was not read. ★ **RA-83**: an 8-K item 4.02 withdraws the *evidence*, not merely the conclusion — `evidence_coverage` for the affected periods goes to zero and RA-38's floor fires. ★ **RA-79: an unexplained move is reported unexplained** — a plausible reason attached to one is strictly worse than the honest gap. Rationale, and the macro half, in [`L1-fundamental-analysis-event-and-macro.md`](L1-fundamental-analysis-event-and-macro.md). |
| 0.7.0 | 2026-08-18 | Victor | ✅ **QR-6 closed — `evidence_coverage` defined (RA-65…68).** It is the fraction of a rubric level's `evidence_required` items that were **successfully extracted**, per dimension. ★ **RA-66 is the load-bearing half: presence in the bundle is not extraction** — counting documents rather than pulled facts reports 100 % coverage on a bundle nothing could be read from. ★ **RA-67**: until calibration exists `confidence := evidence_coverage`, so there is **no model-produced number to launder** and RA-38 becomes structural; **RA-68** splits them again afterwards, because *how much we read* and *how often we were right* are different questions. |
| 0.6.0 | 2026-08-18 | Victor | ⚠ **Seam audit: D-01 is the only domain permitted to call the gateway and never named the record it emits.** **RA-64** names **CT-0.1 LLMCall** as the source of `CT-1.2 AnalysisRun`'s token, model and temperature fields — and carries forward **GW-22**: `outcome` has no `partial` value, because both card incidents came from treating one as a success. |
| 0.5.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit: `CT-1.4`'s grade was lossy against RA-20.** It carried `stability_fraction` but not `verdict_distribution`, and **a ratio cannot reproduce *"BUY 4 / HOLD 1"*** — 0.6 is equally 3/5 or 12/20. Added, with **RA-51a**: the grade carries what the artifact must *render*, not a summary of it. |
| 0.4.0 | 2026-08-18 | Victor | **RA-60 now has an owner.** `L2-shared-infrastructure.md` **GW-8** sets production calls to `temperature = 0`, which resolves the contradiction between RA-60 (set it) and RM-1 (measure variance that only exists if it is not 0): **the sampling probe is retired and RA-61's perturbation probe replaces it** (GW-10). |
| 0.3.0 | 2026-08-18 | Victor | ✅ **§7.4a — two sampling policies decided.** **Decision coverage `k_cov = 3`** (RA-55, crosses the gate/rank boundary at 0.44 % NAV for +20 % on the pick), **planned `k_cov = 10`** (RA-56 — held back not for cost but because the gain is uninterpretable until `IC₀₃` is measured). ★★ **Measurement coverage is STRATIFIED across rank deciles** (RA-57) — the single highest-value change here and it costs nothing, because covering only the top-`k` makes `ρ` *undefined*. **Calibration starts now** (RA-59, $0). ★★ **§7.4b — RM-1 measures the LANGUAGE MODEL, not the analysis.** No `temperature` is set anywhere, so it runs at the API default and RM-1 spends k× tokens measuring **self-inflicted** variance that would vanish at temperature 0. **`k_stab = 5` is the wrong purchase** (RA-61): keep k=3 and **perturb the input** (option order, evidence order, paraphrase) instead of resampling the decoder — same cost, and it measures a property of the analysis. RA-60…RA-63. |
| 0.2.0 | 2026-08-18 | Victor | ★ **CT-1.4 GateVerdict added — the adapter D-12 consumes, which existed in neither spec.** `PASS/FLAG/VETO` appeared nowhere here while `L1-decision.md` CT-12.1 showed a thesis gate status with no source. §11.1 argues **D-01 owns the mapping** (it is a judgement about the thesis's own reliability, and D-12 deriving it would be origination — DN-1). §11.2 is the total mapping and **closes QR-2**: unstable FLAGs above `VETO_FLOOR` and VETOes below. **§8.1 fixes the four scorecard dimensions**, so D-12's contract stops carrying an invented example. RA-47…RA-54. |
| 0.1.0 | 2026-08-16 | Victor | Initial draft. §7 — the three failure modes of an LLM analyst (inconsistency, bias, induced overconfidence) with a reduce/monitor pair for each — is the substance of this spec; everything else supports it. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

D-01 answers one question, and it is the only question in this system that arithmetic cannot:

> **"Is this a good business, is the story still true, and what would prove me wrong?"**

Every other domain computes. D-01 **judges** — and judgement is exactly the thing that cannot be
tested by asserting an expected value. That asymmetry is the whole design problem, and §7 is the
answer to it.

## 1.2 Position

> ⚠ **Corrected 2026-08-20 (v0.11.0). The previous diagram showed D-01 reaching SEAT-1 directly
> "via D-09" and was stale** — it predated **D-12 Decision** (L0 v0.17.0), which this spec's own
> v0.2.0 already acknowledged by adding `CT-1.4 GateVerdict`, *"the adapter D-12 consumes"*. **D-01
> does not send a verdict to the reader. It sends a gate to a composer.**

```text
                     ┌──────────────────────────┐
                     │  SEAT 1 — PM & Trader    │   reads · decides
                     └────────────▲─────────────┘
                                  │  ONE artifact
                     ┌────────────┴─────────────┐
                     │  D-09 REPORTING  SEAT-5  │   renders CT-12.1;
                     └────────────▲─────────────┘   never originates (DC-1)
                                  │  Recommendation CT-12.1
        ┌─────────────────────────┴──────────────────────────┐
        │  D-12 DECISION   SEAT-5                            │
        │  composes · attributes · ★ ORIGINATES NOTHING      │
        │  P3-monotone by construction (DN-1)                │
        └──▲───────────────────▲───────────────────▲─────────┘
           │                   │                   │
    Nomination CT-3.4   ★ GateVerdict CT-1.4     alerts
       (D-03)                  │                  (D-05)
                     ┌─────────┴────────────────┐
                     │  D-01 FUNDAMENTAL ANALYSIS  │   SEAT-2  ← this spec
                     │  thesis · verdict ·      │
                     │  falsifier · invalidation│
                     │  ★ the ONLY LLM-bearing  │
                     │    domain                │
                     └───▲──────────────────▲───┘
                         │                  │
         ┌───────────────┴──┐        ┌──────┴────────────┐
         │  D-02 Feature Eng│        │  D-07 Data Engine │
         │  fair value,     │        │  filings, news,   │
         │  quality, moat,  │        │  events, calendar │
         │  ratios (§6.2)   │        │  — all at as_of   │
         └──────────────────┘        └───────────────────┘

   ✗ D-03 / D-04 rank_score — FORBIDDEN INPUT to D-01 (INV-014)
   ✗ D-12's output never flows back to D-01 or D-03 (L0 §4.3) — a composed
     verdict fed back would launder one seat's view into the other's input
```

## 1.2a ★ Two things leave D-01, and only one of them is a decision

The diagram has one arrow out of D-01 because only one thing D-01 emits participates in the
decision. **The narrative reaches the page by a different route, and confusing the two is what the
old diagram did.**

```text
   ① THE DECISION PATH
      GateVerdict CT-1.4  ──►  D-12 composes  ──►  CT-12.1  ──►  D-09 renders
      PASS / FLAG / VETO       against D-03's       the one        the card
                               nomination and       artifact
                               D-05's alerts

   ② THE NARRATIVE PATH  — a LOOKUP, not a second decision
      CT-12.1 carries `thesis_ref` = (ticker, thesis_version, as_of, bundle_hash)
      D-09 RESOLVES that key back to D-01 CT-1.1 to render the thesis text,
      bear case, falsifiers and claims.
      ★ Referenced, never copied (D-12 DN-33) — the same prose under two
        contracts renders whichever was written last.
      ★ Resolving a reference is permitted; re-deriving a computation is not
        (D-09 RP-43a).
```

| ID | Rule |
|---|---|
| **RA-103** | ★★ **D-01's verdict reaches SEAT-1 only through D-12.** There is no path from a `Thesis.verdict` to the artifact's verdict field. ⚠ A direct D-01 → D-09 verdict edge would make **D-09 the composer**, which `L1-decision.md` §1.2 names as *"the dangerous one — how a renderer starts deciding"* (DC-5) |
| **RA-104** | ★ **The narrative reaches D-09 by resolvable reference, never by copy** (DN-33), and **the analyst's own verdict renders BESIDE the composed one, never instead of it** (`CT-12.1.grade.verdict`, D-09 §8Z, DC-4). ★ That is what keeps the disagreement between a thesis and a composed decision visible rather than resolved in layout |

## 1.3 Boundary

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-01 INTERPRETS NUMBERS. IT NEVER COMPUTES THEM.                ║
║                                                                  ║
║  "Fair value is $412.80"                        → D-02           ║
║  "…which is 34% above the price, and the gap    → D-01           ║
║   is justified because the moat is widening"                     ║
║                                                                  ║
║  D-01 owns: thesis, verdict, conviction, falsification           ║
║             condition, bear case, invalidation monitoring,       ║
║             the reading of a filing, the materiality of news.    ║
║                                                                  ║
║  D-01 does NOT own: any arithmetic (P2, AP-5), the ranking       ║
║             (SEAT-3), the rendering (D-09, DC-1), the decision   ║
║             (SEAT-1).                                            ║
║                                                                  ║
║  A number that appears in a D-01 output and nowhere in its       ║
║  evidence bundle is a HALLUCINATION, not an insight (RA-9).      ║
╚══════════════════════════════════════════════════════════════════╝
```

**Authority: RECOMMEND (L0 §3.1).** D-01 proposes; it never decides and never gates. Under P3 a
verdict may be made *more* conservative downstream and never more aggressive.

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **EvidenceBundle** | one analysis | `bundle_hash` | **the pinned, hashed input set** — §5 |
| **Thesis** | ticker × version | `(ticker, thesis_version)` | the structured rationale |
| **Falsifier** | thesis × condition | `(thesis_version, ordinal)` | observable, dated, checkable |
| **ScorecardResult** | ticker × rubric × as_of | `(ticker, rubric_id, as_of)` | bounded judgement — §8 |
| **Claim** | one assertion | `(analysis_id, ordinal)` | text + **evidence span** + kind (fact \| inference \| assumption — RA-9, S-3) |
| **Verdict** | ticker × as_of | `(ticker, as_of)` | enum + conviction + stability — §7.1 |
| **InvalidationEvent** | thesis × trigger | `(thesis_version, event_id)` | a falsifier that fired |
| **AnalysisRun** | one execution | `run_id` | prompt version, model id, params, bundle hash (AP-6) |
| **PreEventBrief** | thesis × scheduled event | `(thesis_version, event_id)` | ★ written **before** the event, immutable after — §10A |
| **MoveReview** | ticker × date | `(ticker, date)` | the read on an abnormal move; may conclude **unexplained** — §10B |
| *`CalendarEntry`* | *(D-07's entity — DE-19)* | — | **consumed, never owned.** A revisable *claim about the future*, never a fact |

> **`AnalysisRun` is not bookkeeping.** It is what makes an output reproducible-in-principle and
> comparable across runs. Without it the variance measurement in §7.1 has nothing to key on.

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── D-07 Data Engine    filings, news text, profile, events — at as_of
  │                       ★ AND the event calendar (DE-18…DE-20, §5A.4b) and
  │                       the 8-K feed — §10A / §10B
  ├── D-02 Feature Eng.   fair value, quality, moat, ratios, peer context
  │                       WITH the arithmetic trail (its §6.2)
  │                       ★ AND the return decomposition §10B consumes (RA-78)
  └── D-00 shared/llm     the gateway — the ONLY domain permitted to import it (ST-5)

DEPENDED ON BY
  ├── D-12 Decision       ★ consumes CT-1.4 GateVerdict — THE decision path.
  │                       Statuses are consumed, never derived (DN-31), and
  │                       D-12 originates nothing (DN-1). RA-103
  ├── D-09 Reporting      resolves `thesis_ref` back to CT-1.1 to render the
  │                       narrative; may not alter it (DC-1, DC-5, RP-43a).
  │                       ★ NOT a second verdict path — RA-104
  └── D-11 Recording      the decision journal records what was argued

DOES NOT DEPEND ON
  ✗ D-03 / D-04 — rank_score, signals, model output (INV-014)
        ★ including the abnormal-move decomposition. It is arithmetic, and it
          is sourced from D-02 — neutral ground — precisely so consuming it is
          not consuming SEAT-3's output (RA-78)
  ✗ D-05 / D-06 — risk and sizing are downstream of a verdict, not inputs to it
  ✗ an external API — everything through D-07 (DE-1)
  ✗ its own prior verdict, when authoring afresh — §7.2 (RA-12)
```

---

# 4. MODULE DECOMPOSITION

```text
src/fundamental/
├── bundle/             # ★ evidence assembly, pinning, hashing — §5
├── scorecard/          # ★ bounded rubric-driven judgement — §8
│   ├── rubrics/        #   versioned YAML: dimensions, levels, criteria
│   └── score.py
├── prompts/            #   versioned; alignment-checked (INV-9)
│   ├── master.md       #   the single-source registry of every prompt
│   └── alignment.py    #   PromptAlignmentChecker — inherited VERBATIM
├── thesis/             #   authoring + falsification conditions — §9
├── invalidation/       #   monitoring against new filings & news — §10
│   └── news.py
├── calendar/           # ★ scheduled-event awareness — §10A
│   ├── staleness.py    #   event-relative staleness (RA-71/72)
│   └── pre_event.py    #   the pre-event brief (RA-73…RA-75)
├── events/             # ★ unscheduled events & abnormal moves — §10B
│   ├── router.py       #   ★ the 8-K item-code TABLE — deterministic (RA-82)
│   ├── moves.py        #   the unexplained-residual read (RA-79/80)
│   └── sweep.py        #   the weekly accumulation sweep (RA-85/86)
├── filings/            #   filing interpretation (extraction — §6)
├── claims/             #   claim extraction, evidence-span binding, citation check
└── monitor/            # ★ the RM-n measurements — §7.4
    ├── variance.py     #   the k-run probe
    ├── base_rates.py
    └── calibration.py
```

---

# 4A. ★ THE RUNTIME WORKFLOW — what runs, in what order, on what trigger

> ⚠ **Added v0.12.0 to close a real hole.** §4 says what the code *is*; §12 lists methods in no
> order; §§5–10C state rules without saying when any of them fires. **Nothing said how a run
> proceeds.** A reader could implement every rule in this spec and still not know what to call first.

## 4A.0 Who decides the timing, and who decides the order

```text
   D-08 ORCHESTRATION            D-01 FUNDAMENTAL ANALYSIS
   ─────────────────────         ──────────────────────
   decides WHEN                  decides IN WHAT ORDER
   10:00 ET, preconditions,      the ladder below
   locks, retries (OR-5)
        │                                 ▲
        └──── invokes an entry point ─────┘
              never reaches inside (OR-1)
```

D-08 **invokes and never computes** (OR-1), and **no domain may import orchestration** (OR-3). So the
sequencing below is D-01's own and must run standalone — which is also what makes it testable
without a scheduler.

| ID | Rule |
|---|---|
| **RA-105** | ★ **D-01 sequences its own work. A caller may invoke an entry point; it may not reorder, skip or re-enter a step.** ⚠ A caller able to skip Stage A has removed RA-14, and a caller able to re-run Stage D has removed RA-16 — **the anti-bias guarantees live in the order, so exposing the steps individually exports the ability to break them** |
| **RA-106** | ★ **The seven workflows below are distinct entry points with distinct preconditions — not modes of one function.** ⚠ A single `analyse(ticker, mode=…)` is how the blind bundle eventually gets handed the full one: the flag is easy to pass wrongly and impossible to type-check |

## 4A.1 There is not one workflow — there are nine

| ID | Workflow | Trigger | Cadence | Tier | Emits |
|---|---|---|---|---|---|
| **WF-1** | **Fresh authoring** | no live thesis, or the thesis was superseded | per selected name (`k_cov = 3`) | deep | `Thesis` · `GateVerdict` · `MonitorReport` |
| **WF-2** | **The daily watch** | the 10:00 ET run (D-08 §5A) | daily | ★ cheap→deep, gated | `InvalidationEvent[]` · `MoveReview[]` |
| **WF-3** | **Pre-event brief** | calendar: `T−3` before a depended-on event | per event | deep | `PreEventBrief` |
| **WF-4** | **Post-event read** | calendar: the event occurred | per event | cheap→deep | `InvalidationEvent[]` |
| **WF-5** | **The weekly sweep** | weekly | weekly | mixed | `SweepReport` · monitor page |
| **WF-6** | **Calibration scoring** | a thesis closed | on close (reported monthly) | ★ **none — deterministic** | calibration curve · `ρ̂` |
| **WF-7** | **Sector file update** | source-list poll | daily ingest, weekly report | cheap | new `SectorFile` version |
| **WF-8** | ★ **Relay request** | the relay queue (§4B) | **daily, a few tickers, 5 days/week** | ★ **none — composition only** | `RelayRequest` — a prompt to copy |
| **WF-9** | ★ **Relay ingest** | Victor pastes a response back | on return | ★ **cheap — verification, not authoring** | `RelayReport` · `Thesis` · `GateVerdict` |

★ **WF-6 has no LLM in it at all**, and it is the one whose clock starts first (`L3` **BS-1**, RA-59).
★★ **WF-8 has no LLM either** — it *composes* a prompt and never sends one. **The expensive call is
made by a human on a flat-rate subscription, which is the entire point** (§4B).

---

## 4A.2 WF-1 — fresh authoring, the eleven steps

```text
  0  ALIGN      prompt-alignment check              deterministic   ABORT
  1  ASSEMBLE   build_bundle → bundle_hash          deterministic   ABORT
                                    │
  2  EXTRACT    E-01 … E-13   ┌─────┴─────┐  ║ PARALLEL ║  deep
                              ▼ ▼ ▼ ▼ ▼ ▼ ▼
  3  VERIFY     X-01 · X-02 (value-in-span, span-present)
                                    │        deterministic   ABORT
                                    ▼
  4  STAGE A    J-01 … J-08   ┌─────┴─────┐  ║ PARALLEL ║  deep
     view:blind               ▼ ▼ ▼ ▼ ▼ ▼ ▼   no price, no
                                    │          market cap, no
                                    ▼          valuation
  5  ★ FREEZE   hash + persist Stage A output   ◄── irreversible
                                    │
                                    ▼
  6  STAGE B    J-09 ──► J-10                  ║ SEQUENTIAL ║  deep
     view:full                      │
                                    ▼
  7  STAGE C    J-11 · J-12 · J-13 · J-14      ║ PARALLEL ║  deep
                                    │           separate prompts,
                                    ▼           separate calls
  8  STAGE D    J-15 ──► persist ──► J-16 ──► J-17
                ★ STRICTLY SEQUENTIAL, with a write between 15 and 16
                                    │
                                    ▼
  9  VERIFY     X-03…X-07 · RM-1/2/3 · RM-10/11/15
                                    │        non-zero ⇒ FAIL the run
                                    ▼
 10  PROJECT    Thesis ──► GateVerdict (CT-1.4, §11.2 mapping)
                                    │
                                    ▼
 11  EMIT       Thesis · GateVerdict · MonitorReport · AnalysisRun[]
```

### What forces each position — the column that matters

| Step | Forced there by | What breaks if it moves |
|---|---|---|
| **0** before everything | **INV-9**, RA-13 | A drifted prompt is an unversioned change to the method. Checking alignment *after* the calls checks nothing — the calls already ran |
| **2** before **4** | **RA-7** | Judgement consumes *extraction outputs*, never raw documents. Reversed, the verifiable half becomes unverifiable (RA-5) |
| **3** before **4** | **RA-6** | An unverified fact entering a judgement is a hallucination with a scorecard built on it |
| **5** between **4** and **6** | ★★ **RA-14** | **The freeze is what makes staging real.** Staging without a persisted commit lets Stage B silently revise Stage A once it has seen the price — and the anchor-stripping bought nothing |
| **8** internal order | ★ **RA-16** | The falsifier is written **before** the verdict. ⚠ **With a persisted write between them** — held in memory, the ordering is nominal and a single call could produce both |
| **9** before **10** | **RA-29**, P5, DC-3 | A degraded or failed run must never project into a gate. This is the D-15 boundary |
| **10** owned here | **§11.1**, DN-31 | D-12 deriving the status would be **origination** (DN-1) and would need analytical policy D-12 may not hold |

## 4A.3 Parallel or sequential — and the rule that already decided it

| ID | Rule |
|---|---|
| **RA-107** | ★ **Calls within a stage may run in any order or concurrently; stages never overlap.** ★ **This needs no new rule — RA-12 already guarantees it.** "No conversational state; each call starts from a fresh context containing the bundle and nothing else" means every call in a stage is independent by construction. **RA-12 was written as a bias guard and it buys parallelism for free** |
| **RA-108** | ★ **The Stage-A freeze is a persisted, content-hashed commit — not a variable held across steps.** Later stages *read* it. Nothing rewrites it, including a re-run of a later stage |
| **RA-111** | ★ **Each step's `AnalysisRun` is written before the next step begins.** ⚠ Records written at the end of a run cannot distinguish *"did not run"* from *"ran and failed"* — and that distinction is the whole of P5 |

> ⚠ **One thing deliberately absent: option-order randomisation is per call, not per stage** (RA-17).
> Two J-blocks in the same parallel batch get *different* permutations, and both are recorded. A
> stage-level permutation would correlate the position bias across the very dimensions RM-2 compares.

## 4A.4 WF-2 — the daily watch, ordered cheapest-first

★ **Every step is a gate on the next.** Deep-tier work runs only on what survived triage, which is
what keeps a daily loop over the whole book affordable.

```text
   1  CALENDAR GATE      D-07 §6A pre-run check      ⛔ HALT on unhandled action
   2  8-K ROUTING        deterministic item table    RA-82 — no LLM
        └─ item 4.02 ─► ⛔ evidence withdrawn (RA-83), coverage → 0
   3  MOVE DECOMPOSITION residual from D-02          RA-88 — before any trigger
        └─ ≥2 names tripping ─► ⚠ common-factor suspected (RA-89)
   4  TRIAGE             E-14 / V-01 / V-03          cheap tier, escalations only
   5  ESCALATION         V-02                        deep tier, flagged only
   6  STALENESS          event-relative + pre_event  RA-71 / RA-72 — deterministic
   7  AUTHORING          WF-1 for the k_cov names    deep tier
```

| ID | Rule |
|---|---|
| **RA-112** | ★ **The daily loop is ordered cheapest-first and every step gates the next.** ⚠ **Steps 1–3 and 6 contain no LLM call at all** — a deterministic majority is what makes daily coverage of the whole book cost almost nothing, and inverting the order would spend deep-tier tokens deciding what to look at |
| **RA-113** | ★ **A `HALT` at step 1 stops the run; it does not proceed with a partial universe.** D-07 **DE-35**'s `UNCHECKED` is a first-class result, and a calendar check that could not complete is not a calendar check that found nothing |

## 4A.5 WF-5, WF-6 — the slow loops

| Workflow | Runs | Contains |
|---|---|---|
| **WF-5 weekly** | accumulation sweep (RA-85/86) · RM-6 · RM-7 · RM-8 · RM-9 · sector-file report | ★ emits a report **even when nothing accumulated** |
| **WF-6 on close** | score the closed thesis against its outcome (RA-59) · falsifier-fired vs quiet-abandonment (RM-13) · `ρ̂` (RM-16) | ★ **no LLM.** Its clock started at `L3` **B1** |

## 4A.6 Failure, abort and resumption

| ID | Rule |
|---|---|
| **RA-109** | ★ **Resumption is by STAGE, keyed on `bundle_hash`.** A run resumes from the last persisted stage; **a resumed run whose `bundle_hash` differs is a NEW run, not a resumption**, and must not inherit any earlier stage. ⚠ *Contrast the legacy `[TICKER]_progress.json`, which resumed inside a conversation — RA-12 forbids exactly that* |
| **RA-110** | ★★ **A failed step aborts its workflow and emits nothing partial.** There is no `partial` outcome (RA-64, GW-22). Downstream receives **`NO_THESIS`** — never a half thesis, never the previous one, never a plausible default (RA-29, DN-10, P5) |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE THREE THINGS A FAILED RUN MUST NOT DO — ALL THREE HAPPENED  ║
║                                                                  ║
║   ✗ emit a partial Thesis        a verdict with no stop and no   ║
║                                   targets IS D-15                ║
║   ✗ fall back to the prior one   the reader cannot tell they are ║
║                                   reading last Tuesday's view    ║
║   ✗ vanish from the slate        a name that disappears looks    ║
║                                   like one that was considered   ║
║                                   and passed over — CT-9.2       ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 4B. ★ THE RELAY — human-mediated research on a flat-rate subscription

> **Intent (Victor, 2026-08-22):** running the whole fundamental report through the Anthropic API is
> expensive per token. A **Claude Pro** and a **ChatGPT Plus** subscription can do equivalent work at
> a flat rate, run **manually**. So: D-01 composes a complete prompt, Victor pastes it into a chat,
> pastes the response back, and the system caches it. D-01 then does only the cheap half — check
> freshness, re-verify, update when stale.

## 4B.1 ★★ The framing that makes everything else fall out

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE RELAY IS AN EXTERNAL PROVIDER WITH A HUMAN AS ITS           ║
║  TRANSPORT.                                                      ║
║                                                                  ║
║  It is not "D-01 running somewhere else". The request is         ║
║  D-01's — it composes it. The RESPONSE is an external            ║
║  artifact that arrives from outside the system and must be       ║
║  ingested and validated before anything builds on it —           ║
║  exactly as an FMP figure is.                                    ║
║                                                                  ║
║  ⚠ A number does not become trustworthy because a human          ║
║  carried it. EDGAR beats FMP for TTM because of what the         ║
║  source can prove, not because of who fetched it.                ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **Under that framing the relay needs almost no new machinery** — it needs an ingest, a validator,
and a provenance label. What it does *not* get is the assumption that a `Thesis` is a `Thesis`
regardless of where it came from.

## 4B.2 ⚠ What the relay breaks — stated before what it buys

Five of D-01's guarantees do not survive a chat-window paste. **None of them is a reason not to do
this; all of them are reasons to label the output honestly.**

| Broken | Why | Disposition |
|---|---|---|
| **RA-1 / RA-2** bundle pinning + hash | ★ **A chat session with web search is ambient retrieval by definition** — the model fetches what it likes. There is no `bundle_hash` because there is no bundle | ⚠ **Accepted and labelled.** A relay report is a distinct provenance class (RA-115) |
| **RA-11 / AP-6 / CT-1.2** reproducibility | A chat UI reports no model id, no decoding parameters, no token counts | Record what is knowable — date, *stated* model, prompt version, who relayed it. Everything else `unknown`, ★ **never fabricated** |
| **RA-12** no conversational state | ★ **A chat box IS conversational state.** A follow-up question makes the analysis path-dependent — which RA-12 forbids because it turns a stochastic answer into a *stubborn* one | **RA-117** — one prompt, one response, fresh session |
| **RA-14** anchor stripping + the §4A step-5 freeze | One paste cannot be staged and hashed between stages. The model sees price from the first token | **RA-119** — ordering inside the prompt, which is weaker, and **said to be weaker** |
| **RA-6 / RA-9 / X-01** span verification | Offsets into documents *we do not hold* map to nothing | **RA-118** — re-verify numerically against D-02/D-07 where possible; mark the rest unverified |

## 4B.3 ★★ The two mechanisms that de-rate a relay report WITHOUT a new rule

This is the part worth reading twice. **The existing spec already handles the risk**, and adding a
special case would have been worse than using what is there.

| ID | Rule |
|---|---|
| **RA-114** | ★★ **`confidence := evidence_coverage` (RA-67) de-rates the relay automatically.** Coverage counts items **successfully extracted and checked** (RA-66) — and a relay report's claims are largely *unverifiable against data we hold*. So its coverage is low, **INV-012/INV-013's floors fire on their own**, and the verdict is capped at HOLD or forced to `INSUFFICIENT_DATA` **with no relay-specific rule anywhere.** ★ *A mechanism built to stop a model inflating its own confidence turns out to price an untrusted transport correctly too* |
| **RA-115** | ★★ **A relay report can never be the actionable pick.** **AC-1.8** requires the actionable pick to carry a `k ≥ 3` stability result, and **a single chat response has no distribution** — `verdict_stability` is structurally absent. ⚠ **So the relay can inform, gate and populate the card; it cannot be the one thing INV-6 lets you trade on** unless an API-side probe is run over the same name. ★ **Again: no new rule — an existing acceptance criterion already draws the line in the right place** |

> ★ **Those two together are the safety case.** A relay report is cheap, useful, visibly
> lower-assurance, incapable of becoming the daily actionable recommendation on its own, and
> automatically capped by a floor nobody had to remember to apply.

## 4B.4 The rules the relay does need

| ID | Rule |
|---|---|
| **RA-116** | **`RelayReport` is a first-class provenance class carried on every artifact that consumes it** (D-09 RP-1's reliability classes gain a fourth: `fact · computation · judgement · ★ relayed judgement`). ⚠ A reader must never have to remember which reports came from a chat window |
| **RA-117** | ★ **One prompt, one response, one fresh session.** Follow-ups are permitted for Victor's own understanding and **may not be pasted back** — a conversation is not the artifact the prompt version describes (RA-12) |
| **RA-118** | ★ **Every number in a relay response is re-verified against D-02/D-07 where a counterpart exists**, and the result is recorded per claim: `verified · contradicted · unverifiable`. ⚠ **`contradicted` fails the ingest** — a relayed report that disagrees with our own data about a *fact* is not a difference of opinion |
| **RA-119** | ⚠ **Staging inside a single prompt is ordering, not a freeze, and the spec says so.** RA-14's guarantee was structural (the field was absent); here it is an instruction the model can ignore. ★ **The two-pass form (§4B.6) restores it at the cost of a second paste** and is the higher-assurance option |
| **RA-120** | **Relay staleness is event-relative** (RA-71/72, §10A) — a relay report is stale when a scheduled event it depends on has occurred, not when a timer expires. ★ **This is the half Victor described as *"D-01 just needs to search, re-evaluate and update if the report is too old"* — and it already exists** |
| **RA-121** | ★ **The queue mechanics are deterministic; the priority is D-01's judgement.** Rotation, coverage and overdue tracking are arithmetic. **What makes a ticker urgent is a judgement** — and that split is why this feature is D-01's rather than SEAT-5's, exactly as Victor argued |
| **RA-122** | ★ **The relay prompt is COMPOSED from the registry, never hand-written**, and the composition is recorded on the `RelayReport` (MP-12 extended to the relay). ⚠ A hand-edited prompt makes the artifact unattributable and silently breaks INV-9's alignment for that name |
| **RA-123** | ★ **Sector and archetype adaptation is J-01 driving block selection.** A `cyclical_commodity` gets the cycle and supply-side blocks; a `financial` gets book-value framing instead of EPS. **This is the "intelligence" that places the feature in D-01** |
| **RA-124** | ⚠ **The relay stays manual. No automation of a chat interface, ever** — no browser driving, no scripted paste. It is a flat-rate personal subscription used personally; automating it would be both a terms problem and the exact "leak by execution" XP-33 refused |
| **RA-125** | ★ **A relay report is never partially ingested.** A truncated or refused chat response is a failed relay (RA-64/GW-22 — there is no `partial`), and **it must not be topped up by a follow-up** (RA-117). Re-run the whole prompt in a fresh session |
| **RA-143** | ★★ **`verification.claims[]` — the result is recorded PER CLAIM, because RA-118 says so and the contract did not.** ⚠ *Added 2026-08-25 building B4.8: **RA-118 requires "the result is recorded per claim: `verified · contradicted · unverifiable`" and `CT-1.5.verification` stored three INTEGERS.*** ★ Two readers need the detail and neither can get it from a count: **the ingest failure must name WHICH claim contradicted** — *"contradicted: 1"* is not an error message anyone can act on — and **a reader of a HOLD-capped relay report needs to know which claims were unverifiable**, since that set is precisely what the cap is about. Same argument as **RA-133**: a projection that drops the ordinal destroys the thing the rule was for |
| **RA-144** | ★★ **The INV-012/013 floors take a COVERAGE VALUE, so RA-114's *"unchanged"* is literally one implementation.** ⚠ *Added 2026-08-25 building B4.8: **AC-1.77 says the floors "fire on it unchanged"**, and the floor function's input was `CoverageReport` — **a rubric-dimension object a relay report cannot produce**, because a relay has claims, not extracted rubric evidence. The only ways to satisfy the AC as written were to fake a `CoverageReport` or to write **a second copy of the floors** — which is **FE-4's defect** and the one **RA-137** had just finished removing from the wordlist.* ★ **The floors are a function of one number**; taking that number instead of one particular container is what makes RA-114's claim true rather than aspirational. ⚠ **The two denominators stay different and must** — RA-65's is the rubric's `required_union`, the relay's is `claims_total` — *what is shared is the threshold, not the arithmetic that reaches it* |

## 4B.5 The schedule (WF-8)

| | |
|---|---|
| Cadence | **5 days/week**, a few tickers per day |
| Default order | Rotation over names with a live thesis, oldest-first, so coverage is even by construction |
| ★ Priority overrides | **D-01's judgement** — an event just landed (§10A), a falsifier is `approaching`, an unexplained residual (RA-80), an 8-K routed for escalation (§10B.3), the sector file moved (§10C) |
| Reschedule | ★ **The queue is re-derived every run, not consumed.** A ticker that becomes urgent overtakes; nothing is "already scheduled" in a way that resists new evidence |
| Notification | ★ **D-09 renders today's queue in the daily report** — the ask's second requirement. Wants a `RELAY QUEUE` block: today's names, what came back, what is overdue, what went stale |

## 4B.5a ✅ What happens when a queued name is not run — DECIDED 2026-08-22

> ✅ **Victor:** *"Overdue names go stale. It is my responsibility to remember and run it later."*

★ **This is the right answer and it needs no new mechanism** — it is **RA-120** (event-relative
staleness) already doing its job, with the queue kept honest about the consequence.

| ID | Rule |
|---|---|
| **RA-126** | ★★ **An overdue relay is not a backlog item — it is a thesis going stale.** A queued name that is not run ages until its thesis crosses **RA-71**'s staleness test (event-relative first, the clock as a floor), at which point the thesis is **marked stale on the card** exactly as any other stale thesis is. ⚠ **The queue never absorbs the consequence on the thesis's behalf** — a name sitting in a queue is not a name that has been analysed |
| **RA-127** | ★ **The system reports; it does not chase.** No nagging, no auto-escalation, no re-prioritising a name *because it was skipped*. ★ **Skipping is a decision SEAT-1 is entitled to make**, and D-01's obligation is the same one it has for every override — **make it visible and let it stand** (`vision.md` §2). ⚠ A queue that pesters is a system asserting authority it does not hold |
| **RA-128** | **An overdue entry ages in place and is never silently dropped to make room.** It stays on the queue with its age, and the daily report carries `overdue` and `stale` as **separate counts** — *not yet run* and *no longer trusted* are different states, and collapsing them hides the moment one became the other |

> ★ **The consequence is already wired and worth stating explicitly: a stale thesis FLAGs at the
> gate.** §11.2 maps *"thesis stale past `STALENESS_FILINGS_HOURS`"* → **FLAG**, so an unrun relay
> eventually annotates that name in D-12 without anyone adding a rule for it. **The cost of not
> running one is paid in visible confidence, not in a hidden gap** — which is what makes
> *"my responsibility to remember"* a workable arrangement rather than a hope.

## 4B.6 One paste or two

| | **One paste** *(recommended to start)* | **Two pastes** *(higher assurance)* |
|---|---|---|
| Manual load | 1 chat per ticker | 2 chats per ticker |
| RA-14 anchor strip | ⚠ **instruction only** (RA-119) | ✅ **structural — Pass A never receives the price** |
| Realistic at 3 tickers/day | 3 sessions | 6 sessions |
| ★ Recommendation | **Start here.** The binding constraint is Victor's time, and a protocol that is not run has zero assurance | **Escalate to this for a name about to be sized up** — the moment RA-14's bias actually costs money |

---

# 5. THE EVIDENCE BUNDLE — pin the inputs before blaming the model

Nothing in §7 is measurable if the inputs move. An analysis that differs from yesterday's may
differ because the model is stochastic, or because a filing landed, or because a price moved, or
because D-02 changed a formula. **Those must be distinguishable, and only pinning makes them so.**

An **EvidenceBundle** is the complete, ordered, hashed set of what the model is allowed to see:

| Part | Source | Pinned by |
|---|---|---|
| Filing text & extracts | D-07 at `as_of` | `accession_id` |
| News items | D-07 at `as_of` | `(source, external_id)` + `published_date` |
| Computed numbers | D-02 at `(as_of, adj_as_of)` | contract name + version |
| Company profile & sector | D-07 | `as_of` |
| Prior thesis *(invalidation only)* | D-01 | `thesis_version` |

| ID | Rule |
|---|---|
| **RA-1** | Every LLM call takes an **EvidenceBundle and nothing else**. No ambient retrieval, no live fetch mid-prompt, no tool that reaches outside the bundle |
| **RA-2** | The bundle is **content-hashed** and the hash is recorded on the `AnalysisRun`. Two runs with the same `bundle_hash` are comparable; two with different hashes are not, and any variance measurement across them is meaningless |
| **RA-3** | The bundle is assembled at a single `as_of` and is **internally consistent** — no mixing a fresh price with a stale filing |
| **RA-4** | Bundle assembly is **deterministic**: same `as_of` ⇒ same bundle ⇒ same hash (INV-2 applied to inputs) |
| **RA-147** | ★★ **The `profile` part carries identity and business description ONLY — price, market cap and every valuation field are stripped at assembly, by an ALLOWLIST.** ⚠ *Added 2026-08-26 building the assembler.* **RA-14 is structural only if the anchors never enter a non-withheld part.** `BLIND_WITHHELD_KINDS` strips `computed` and nothing else, so a `profile` part reaches **J-11 and J-15 — exactly the qualitative passes RA-14 protects**. FMP's `profile` response leads with `price`, `marketCap`, `beta`, `range` and `lastDividend`: dumping it whole defeats RA-14 while every test still passes, because **nothing checks a part's CONTENT against the rule**. ★ An allowlist, not a denylist — *a denylist leaks whatever the vendor adds next*, silently, onto the blind view |
| **RA-148** | ★ **D-01's Class-B consumer is `thesis`, and it is deliberately NOT a PIT consumer.** ⚠ *`profile` is a Class-B field set and `PIT_CONSUMERS` is `{training, backtest, inference}` — authoring under any of those raises `LiveReadDeniedError`, so **no thesis could ever be written**.* DE-6.9 is written per-consumer precisely because *live data is useful on a report today and poison in a training row*: **a thesis is the former.** It is a judgement made today about today and it never becomes a training row |
| **RA-149** | ★★ **A filing part selects the newest PERIODS, never the newest FILED ROWS.** ⚠ *Found 2026-08-26 reading the first real bundle:* one EDGAR filing reports its own quarter **and the prior-year comparative**, so ordering by `filing_date` put NVDA's quarter ending **2025-04-27 — a year stale —** last in the window while the actual latest quarter sorted earlier. ★ **A model handed that reads a comparative as the current period, and every ratio it computes is a year out.** `get_fundamentals` has already PIT-filtered on `filing_date`, so ordering by period costs no look-ahead protection — INV-1 stays D-07's |
| **RA-150** | ★ **The observable vocabulary is D-02's contract fields PLUS D-07's PIT fundamental tags.** ⚠ **`b3_minimal` is the only contract D-02 publishes and it carries `mom_21` and `vol_21` — no ratios at all**, so a *fundamental* thesis restricted to contract fields could be falsified **only by momentum and volatility**. A statement tag qualifies under RA-35 on the same ground a feature does: **it is re-readable at a future `as_of`**, which is the entire test |
| **RA-151** | ★★ **A ratio with price in it is an ANCHOR, and the bundle splits the vendor's payload accordingly.** ⚠ *Added 2026-08-26 capturing Class-B observations:* **26 of `ratios-ttm`'s 62 keys are price-derived.** Handing the set to a blind pass whole leaks the anchor through `priceToEarningsRatioTTM` alone — **a reader with EPS and a P/E has the price, and RA-14 is defeated without a single price field appearing.** ★ Margins, returns, leverage and turnover go in as **`operating_ratios`** (visible: *"is this a good business?"* is the question a margin answers and a multiple does not); every price-derived key goes to **`computed`**, which `BLIND_WITHHELD_KINDS` strips |
| **RA-152** | ★ **The ratio list is an ALLOWLIST and the default is WITHHELD.** ⚠ *Wrongly withholding a quality metric costs a slightly thinner bundle; wrongly exposing a multiple costs RA-14* — the asymmetry decides the default. ★★ **And it is enumerated, never inferred:** a substring probe for `ev` classified **`financialLeverageRatioTTM`** as enterprise-value-derived. A heuristic over vendor field names **misclassifies in both directions**, and one of those directions is silent |
| **RA-153** | ★ **A thesis bundle does not carry the consensus.** `analyst_estimates`, `price_target_consensus` and `grades_consensus` are captured by D-07 for D-09's display and are **deliberately absent from the bundle** — *a thesis that reads the consensus before forming a view is measuring agreement, not the business* (RA-12, RA-19) |

---

# 6. TWO KINDS OF LLM CALL — and they get different guards

Treating "the LLM call" as one thing is the root of most of the difficulty. There are two, and only
one of them is irreducibly uncertain.

| | **Extraction** | **Judgement** |
|---|---|---|
| Question | *what does this document say?* | *is this a good business?* |
| Example | "what was the stated FY guidance?" | "is the moat widening?" |
| Ground truth | **exists** — in the document | **does not exist** |
| Verifiable | **yes** — the answer is in the bundle | no |
| Right guard | **assert against the source** | measure variance, bound the output, disclose |
| Right tier (INV-8) | deep tier — quality-critical, low-frequency, filing-cached | deep tier |
| Failure mode | hallucination — a fact not in the source | inconsistency, bias, false confidence |

| ID | Rule |
|---|---|
| **RA-5** | Extraction and judgement are **separate calls with separate prompts**. A prompt that asks "summarise the filing and tell me if it's a good business" makes the verifiable half unverifiable |
| **RA-6** | Every extraction output is **checked against the bundle**: each extracted value must appear in, or be arithmetically derivable from, the cited span. A failed check raises (P5) |
| **RA-131** | ★★ **X-01 has TWO halves, and only the second is usually implemented.** ⚠ *Added 2026-08-23 building B4.2.* The extraction envelope emits **both** a `quote` and an `offset [start, end]` into the cited document, and **the offset exists in order to be resolved**: ① the `quote` must equal the document's own text at those offsets, ② the `value` must appear in the `quote`. ★★ **Checking only ② verifies the model against itself** — a model that fabricates a quote *and* a value consistently passes, and the citation is fiction with a character range attached. **The offset is the only part of a citation the model cannot also author** |
| **RA-132** | ★ **"Arithmetically derivable" in RA-6 means NORMALISING ONE STATED FIGURE — never combining two.** ⚠ *Added 2026-08-23: RA-6's phrase covers both readings and the spec never separated them.* `"1,234"` → `1234` and `"(500)"` → `-500` are the **same figure in another format** and pass. `revenue 100` + `cogs 40` ⇒ `gross_profit 60` is **arithmetic, and it is D-02's** (RA-45, MP-6) — as is subtracting a prior year-to-date to reach a discrete quarter, which is *the single most expensive extraction error this project has actually made* (ARM 2.76×, MU 71 %). ★ **Read the other way, X-01 accepts anything a determined reader can construct, which is no check at all** |
| **RA-7** | Judgement calls consume **extraction outputs**, never raw documents. The judgement layer reasons over a clean, checked set of facts |

> **This split is what makes hallucination a *detectable* class rather than a general anxiety.**
> A hallucinated number in extraction is caught by RA-6 automatically. A hallucinated number in a
> judgement narrative is caught by claim-binding (RA-9). Neither relies on a human noticing.

---

# 7. THE THREE FAILURE MODES OF AN LLM ANALYST

> **This section is the reason this spec exists.** D-01 is the only domain where correctness cannot
> be asserted, so its guarantees have to be of a different kind: not *"this output is right"* but
> *"the ways this output can be wrong are bounded, measured, and visible to the reader."*
>
> The three modes are genuinely distinct. They have different causes, different mitigations, and —
> critically — **different observers**. Inconsistency is invisible to the reader and visible to the
> machine. Bias is invisible to both without aggregation. Overconfidence is invisible to the machine
> and lives entirely in the reader's head.

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   THE GOAL IS NOT A RELIABLE ANALYST.                            ║
║   THE GOAL IS AN ANALYST WHOSE UNRELIABILITY IS MEASURED         ║
║   AND SHOWN.                                                     ║
║                                                                  ║
║   A model that is wrong 30% of the time and says so is usable.   ║
║   A model that is wrong 20% of the time and reads as certain     ║
║   is more dangerous, because the reader sizes the position       ║
║   off the tone.                                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 7.1 Failure mode 1 — INCONSISTENCY

**Same evidence, same prompt, same model, different answer.**

This is not a defect to be eliminated. It is a property of the tool. Constitution **INV-8** puts
deep-tier work on Opus 5, which **runs adaptive thinking by default**, and the constitution
explicitly warns against disabling it. Temperature 0 does not buy determinism under those
conditions. So the target is not zero variance — **it is *known* variance**.

The danger is not that the model is unstable. It is that **a single run looks exactly like a stable
one.** The reader sees "BUY, conviction High" and cannot tell whether that answer would survive
being asked again.

### Reduce

| ID | Rule |
|---|---|
| **RA-8** | **Bounded outputs for anything that gates a decision.** Verdict, conviction and every scorecard dimension are **enums with written criteria**, never free-form numbers or prose. *(Already true of `verdict`/`conviction` in `report_writer.py`'s JSON schema — this generalises it.)* Free prose is permitted only where nothing downstream branches on it |
| **RA-9** | **Every claim binds to an evidence span.** A claim carries `kind ∈ {fact, inference, assumption}` and, for a fact, the bundle span supporting it. An unbound factual claim is a defect (INV-004, AP-2). ⚠ **Amended 2026-08-23: `assumption` added.** The enum read `{fact, inference}` while the shared citation block **S-3** (`L1-fundamental-analysis-master-prompt.md` §2) instructs the model that *"every sentence you write is one of exactly **three** kinds"* and names ASSUMPTION as the third. ★★ **The prompt asked for a shape the contract could not hold**, so an ingest had two bad options: reject output the prompt requested, or coerce it to `inference` — which S-3 defines as *resting on stated facts*, and an assumption rests on none. See **RA-133** |
| **RA-133** | ★ **`CT-1.1.assumptions[]` is the PROJECTION of `kind == assumption` claims, not a parallel list.** ⚠ Two stores for one idea is how the same prose ends up under two contracts (DN-33's shape). ★ **The projection keeps each assumption's ordinal**, which the bare string list destroyed — and S-3's inferences cite *ordinals*, so an assumption without one cannot be pointed at by the inference that rests on it. *Permitted, and must be listed as an assumption so the reader can reject it independently of everything else* |
| **RA-10** | **Decompose.** Many narrow calls beat one omnibus call. Variance scales with the degrees of freedom in a single response, so a prompt that asks for twelve judgements at once is twelve times less stable than twelve prompts |
| **RA-11** | **Fixed, recorded decoding parameters.** Model id, temperature, top-p, thinking mode and prompt version go on the `AnalysisRun` (AP-6). A parameter that is not recorded cannot be held responsible |
| **RA-12** | **No conversational state.** Each call starts from a fresh context containing the bundle and nothing else. Multi-turn accumulates path dependence, which converts a stochastic answer into a *stubborn* one — worse, because it looks stable |
| **RA-13** | **Prompt alignment is enforced before any call** (INV-9). A drifted prompt is an unversioned change to the analytical method, and it invalidates every baseline in §7.4 |

### Monitor

| ID | Measurement | How |
|---|---|---|
| **RM-1** | **Verdict stability — the k-run probe** | Re-run the *same* `bundle_hash` **k ≥ 3** times. Record the modal verdict and the agreement fraction. **Published on the card** (§7.3) |
| **RM-2** | **Scorecard dispersion** | Per dimension, the spread across the k runs. A dimension that moves ≥ 2 levels between identical runs is not measuring anything |
| **RM-3** | **Numeric spread** | Coefficient of variation of stop and targets across the k runs. Wide spread ⇒ the numbers are decoration |
| **RM-4** | **Prompt-change regression** | On any prompt edit, re-run a **pinned bundle set** and diff the verdict distribution against the previous version. A wording change that flips 30% of verdicts is a change of policy |
| **RM-5** | **Model-change re-baseline** | Any INV-8 tier change invalidates every baseline here. All of RM-1…RM-4 re-measured before the new model is used in production |

> **RM-1 is the highest-leverage measurement in this spec**, and it costs k× the tokens on whatever
> sample it runs over. It does not need to run on every ticker every day — a rotating sample, plus
> **always** on the actionable pick (INV-6), buys most of the value. **The actionable pick is never
> exempt**, because it is the only output anyone trades on.

## 7.2 Failure mode 2 — BIAS

**Not random error — systematic error in a direction.** Repeat-runs will never find it: a
consistently biased analyst is perfectly consistent.

The biases that actually apply here:

| Bias | How it shows up |
|---|---|
| **Anchoring** | Sees the price first, and the qualitative view drifts toward justifying it |
| **Agreeableness / positive skew** | Assistant-trained models rate things well. Shows as too many BUYs and scores clustered high |
| **Confirmation** | Given a bullish frame, retrieves bullish evidence from the same bundle |
| **Recency** | The newest headline dominates a five-year thesis |
| **Position bias** | In an enumerated rubric, option order affects selection |
| **Theme contamination** | Unconscious enthusiasm for the AI/semi theme. **M-2 makes concentration the PM's deliberate choice — it does not license the analyst to add to it unconsciously** |
| **Inherited conclusion** | Seeing `rank_score` and rationalising it — structurally blocked by INV-014 |

### Reduce

| ID | Rule |
|---|---|
| **RA-14** | **Anchor stripping, staged.** The qualitative passes — business understanding, moat, quality — run on a bundle **with price, market cap and any valuation withheld**. Valuation is revealed only at the reconciliation stage, after the qualitative view is committed and hashed. You cannot un-see a price |
| **RA-15** | **The bear case is a separate call with a different prompt**, run against the same bundle, **not** a paragraph appended to the bull case. A bear case written in the same breath is a rhetorical concession, not an analysis (AP-3, INV-011) |
| **RA-16** | **The falsifier is written before the verdict, in a SEPARATE CALL, with a PERSISTED WRITE between them** (J-15 → persist → J-16). Committing to what would break the thesis *before* stating the thesis is the cheapest available de-biasing device. ⚠ **Amended 2026-08-23: it read *"and is part of the same structured output"*, which is the failure §4A.2 step 8 names** — *held in memory, the ordering is nominal and **a single call could produce both***. ★ **One call emitting `{falsifiers, verdict}` satisfies the old wording exactly and buys nothing**: a model choosing both in one forward pass can fit the falsifiers to the verdict it has already reached, which is the anchoring RA-16 exists to prevent. §4A.2 and the master prompt's J-15/J-16 split had both said so since v0.12.0 |
| **RA-17** | **Enumerated options are order-randomised per call**, with the permutation recorded on the `AnalysisRun` |
| **RA-18** | **Fresh authoring never sees the prior verdict.** *(Invalidation checking is the exception and must see it — §10. The distinction is deliberate: re-deciding and re-checking are different tasks.)* |
| **RA-19** | **The evidence bundle is not curated by the same layer that judges.** Bundle assembly (§5) is mechanical and as-of-driven; if the judging layer could choose its evidence, confirmation bias would have a supply chain |

### Monitor

| ID | Measurement | Interpretation |
|---|---|---|
| **RM-6** | **Verdict base rate** over trailing N — fraction BUY / HOLD / SELL | An analyst that says BUY most of the time is not discriminating. Publish the distribution beside the verdict |
| **RM-7** | **Per-dimension score distribution** across the universe | Degeneracy check. If moat clusters at 7–8 for everything, the rubric has no resolving power and the score is noise wearing a number |
| **RM-8** | **Seat-disagreement rate with D-03/D-04** | ★ INV-014 makes the two seats independent, so **healthy disagreement is evidence the independence is real**. Agreement drifting toward 100% means either leakage or a shared bias — both worth knowing. This diagnostic exists *because of* the architecture |
| **RM-9** | **Theme skew** — verdict distribution conditional on sector/theme vs universe base rate | Separates the PM's deliberate concentration (M-2, fine) from the analyst's unconscious enthusiasm (not fine) |
| **RM-10** | **Citation validity rate** | Sample claims; for numeric claims this is **deterministic** — does the cited value appear in the cited span? Uncited-claim rate should be 0 (INV-004) |
| **RM-11** | **Bear-case substance** | A bear case that names no falsifiable condition, or shares > X% of its tokens with the bull case, is null. Measurable without judgement |

## 7.3 Failure mode 3 — INDUCED OVERCONFIDENCE IN THE READER

**The model is not the failure here. The interface is.**

Prose quality is uncorrelated with analytical quality and strongly correlated with *perceived*
reliability. A well-written report about a coin flip reads as insight. And unlike the other two
modes, this one **cannot be measured inside the system** — it lives in the reader's head, and the
only evidence is what the reader subsequently does.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE HEURISTICS A HUMAN READER APPLIES, AND WHY EACH IS WRONG    ║
║  HERE:                                                           ║
║                                                                  ║
║   fluent    → well-reasoned     ✗ fluency is free                ║
║   long      → thorough          ✗ length is free                 ║
║   precise   → researched        ✗ $412.83 is arithmetic, not     ║
║                                    knowledge                     ║
║   no doubt  → no uncertainty    ✗ absence of hedging is a        ║
║                shown               style, not a finding          ║
║   one answer→ a stable answer   ✗ the reader never sees the      ║
║                                    four other runs               ║
║                                                                  ║
║  D-15 IS THE INCIDENT: a FAILED LLM call rendered as             ║
║  "Verdict: HOLD | Conviction: Medium" with no stop and no        ║
║  targets, cached and emailed as a genuine recommendation.        ║
║  Nothing about the artifact looked wrong.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

### Reduce

| ID | Rule |
|---|---|
| **RA-20** | ★ **Publish the variance on the artifact.** The card carries RM-1's result verbatim — *"verdict stable 5/5"* or *"⚠ unstable: BUY 3 / HOLD 2"*. **This is the single most effective anti-overconfidence device available**, because it is quantitative, honest, and impossible to skim past. A reader who sees 3/5 sizes the position differently, and should |
| **RA-21** | **Confidence is displayed only with an empirical referent, or not at all.** Not `confidence: 0.8` — *"High conviction; of 14 prior High-conviction theses, 9 reached target before stop."* Until N is large enough, the artifact says **"not yet calibrated (N=3)"**. A confidence number with nothing behind it is a fabricated precision, and the reader cannot tell the difference |
| **RA-22** | **Fact and inference are typographically distinct** in the rendered output. A number lifted from a 10-K and a judgement about that number must not look the same on the page (D-09 renders it; D-01 supplies `Claim.kind`) |
| **RA-23** | **The falsifier renders ABOVE the verdict.** What would prove this wrong, before what we think. Ordering is an argument |
| **RA-24** | **Fair value renders as a band, never a point.** The point estimate is an artifact of the arithmetic and reads as knowledge. D-02 supplies the sensitivity range; D-09 shows it |
| **RA-25** | **The data-gap block is mandatory and non-collapsible** (AP-1). What the analyst wanted and did not have is part of the finding, not a footnote |
| **RA-26** | **Forecast-voice is linted out.** "will", "is set to", "poised to", "clearly", "undoubtedly" → flagged before render. Deterministic, cheap, and it removes the cheapest source of unearned certainty |
| **RA-27** | **Narrative sections are length-capped.** Length is a free confidence signal; capping removes it and costs nothing analytical |
| **RA-28** | **Both seats' views render side by side, attributed, and divergence is never resolved in layout** (DC-4). Disagreement between an independent quant rank and a thesis is *information*, and hiding it manufactures certainty |
| **RA-29** | **A degraded or failed call never renders as analysis** (P5, DC-3). Inherited from D-15's three-layer fix: refuse to persist, banner the report, refuse to build on a degraded cache |

### Monitor

| ID | Measurement | Note |
|---|---|---|
| **RM-12** | **Calibration curve** — conviction bucket vs realized outcome (target reached / stopped / falsifier fired) | The only real test of whether conviction carries information. Needs D-11's journal and **time** |
| **RM-13** | **Falsifier trigger rate vs quiet-abandonment rate** | ★ How many theses died by their own stated condition versus were quietly dropped. **A high abandonment rate means the falsifiers were decorative** — unfalsifiable in practice, which is the failure AP-3 exists to prevent |
| **RM-14** | **Action correlation** | Does Victor act more on high-conviction reports, and do those do better? If not, conviction is noise the reader is nonetheless responding to |
| **RM-15** | **Lint violations** (RA-26) and **uncited-claim count** (RA-9) | Should be zero. Non-zero is a regression, not a style question |
| **RM-16** | ★★ **Thesis-error correlation `ρ̂` across names** — the correlation of realised thesis errors between covered names, once outcomes accrue | An **RM-9 extension**, not new machinery. ⚠ **`ρ` is currently an assumed parameter on both sides of an argument** and it is measurable. See the box — it decides what the analyst seat's nominal coverage is actually worth |

```text
╔══════════════════════════════════════════════════════════════════╗
║  ρ COLLAPSES BREADTH FOR *LEVEL* DECISIONS AND CANCELS FOR       ║
║  *RANK* DECISIONS. THE ASYMMETRY IS THE WHOLE POINT.             ║
║                                                                  ║
║  Write a thesis score as  f_i = μ_i + c + u_i, where c is the    ║
║  error shared across names (one rubric set, one analyst, one     ║
║  theme):  Var(c) = ρσ²,  Var(u_i) = (1−ρ)σ².                     ║
║                                                                  ║
║  LEVEL  ("is this a BUY?")   error variance σ²; across n names   ║
║         effective breadth is n/(1+(n−1)ρ) — at n=13, ρ=0.6       ║
║         that is 1.6, NOT 13.                                     ║
║                                                                  ║
║  RANK   ("is i better than j?")  the difference is u_i − u_j.    ║
║         ★ c CANCELS EXACTLY, and the residual noise is           ║
║         2(1−ρ)σ² — SMALLER than the 2σ² that independent         ║
║         errors of the same size would give. Correlated error     ║
║         does not merely leave ranking unharmed; it makes         ║
║         ranking cheaper.                                         ║
║                                                                  ║
║  So a shared analytical bias is dangerous exactly where D-01     ║
║  acts as a GATE, and benign-to-helpful where L2 re-ranks         ║
║  (CB-19, k_cov ≥ 2) — which STRENGTHENS the coverage case        ║
║  rather than merely sparing it. Third appearance of the same     ║
║  structure: see `L1-quantitative-analysis.md` QA-93, where a     ║
║  within-date sort cancels the market factor a pooled statistic   ║
║  drowns in.                                                      ║
║                                                                  ║
║  ⚠ Exact for EQUICORRELATED errors. Sub-clusters (two rubrics,   ║
║  two sub-themes) leave common structure inside each cluster.     ║
╚══════════════════════════════════════════════════════════════════╝
```

## 7.4 The monitor set — what runs, when, and where it surfaces

| ID | Cadence | Sample | Published to |
|---|---|---|---|
| RM-1 · RM-2 · RM-3 | every run | **always the actionable pick**; rotating sample otherwise | **the card** (RA-20) |
| RM-4 | on every prompt change | pinned bundle set | change record; blocks release |
| RM-5 | on every model-tier change | pinned bundle set | change record; blocks release |
| RM-6 · RM-7 · RM-9 | weekly | trailing N verdicts | monitor page |
| RM-8 | weekly | all scored names | monitor page — the INV-014 health check |
| RM-10 · RM-15 | every run | all claims | run summary; non-zero fails the run |
| RM-11 | every run | the bear case | run summary |
| RM-12 · RM-13 · RM-14 | monthly | all closed theses | monitor page; **"not yet calibrated"** until N suffices |

| ID | Rule |
|---|---|
| **RA-30** | A monitor that cannot yet be computed reports **"not yet calibrated (N=…)"**, never a placeholder value and never silence. This is `L1-data-engine.md` **DE-35** applied to metrics: absence of evidence is not evidence of absence |
| **RA-136** | ★★ **`not_measurable` is a THIRD status, distinct from `not_yet_calibrated`.** ⚠ *Added 2026-08-23 building B4.5.* RA-30 gives a monitor one way to decline — *"not yet calibrated (N=…)"* — which **promises the number is coming**. ★★ **RM-1's sampling half can NEVER be computed on this tier**: `claude-opus-5` rejects `temperature` (GW-8a), so *the sampling probe was never measuring a property anyone controlled* (GW-10, RA-60) and **RA-61's perturbation form is the only probe available**. Reporting that as `not_yet_calibrated (N=0)` tells a reader to wait for a number that will never arrive. ★ `not_measurable` carries **why**, and `CT-1.3`'s status enum admits it |
| **RA-137** | ★★ **The forecast-voice wordlist and the length caps are D-01's declaration; D-09 EXECUTES them and does not restate them.** ⚠ *Added 2026-08-23: **RA-26/RA-27 are D-01's rules** and `L1-reporting.md` §8 says so explicitly — those obligations are "D-01's to satisfy in CONTENT and D-09's to satisfy in RENDERING". But **neither spec said where the list lives**, and it was implemented only in D-09.* ★ **Two deterministic implementations of one wordlist is D-02 **FE-4**'s defect in another domain** — *the second definition is always the one nobody tests* — and here the two enforcement points disagree in consequence: X-03 **fails the run**, RP-18 **blocks the render**. A list that drifts between them makes which one fires depend on which copy was edited |

## 7.4a ✅ THE TWO SAMPLING POLICIES — **DECIDED 2026-08-18**

D-01 had one notion of *which names get analysed*. It needs **two**, because they buy different
things and were being priced as one (`L2` **CB-29**).

| | **Decision coverage** | **Measurement coverage** |
|---|---|---|
| Which names | ★ **D-03's top `k_cov`** | ★ **stratified across ALL rank deciles** |
| Size | **`k_cov = 3` now → 10 later** | **~20 names/month** |
| Cadence | every run | rotating |
| Buys | the ability to **re-rank** (`L2` CB-19/20) | ★ **`ρ`, `IC₀₁`, and calibration** |
| Cost @ `k_stab=3` | **$624/yr** → $2,079/yr | ~$198/yr |
| ⚠ Does **not** buy | `ρ` — the top-3 span `sd(z) ≈ 0.20` | a better daily pick |

| ID | Rule |
|---|---|
| **RA-55** | ✅ **`k_cov = 3` — decision coverage is D-03's top three.** This crosses the gate/rank boundary (`L2` CB-19: it is at `k = 2`, not `k = n`) at **0.44 % of NAV**, and buys **+20 %** on the expected pick |
| **RA-56** | ★ **PLANNED: `k_cov = 10`.** ★ **Not deferred for cost — $2,079/yr is affordable — but because the value is currently unverifiable.** `k=10` buys **+32 %** (vs +20 % at k=3) and takes `ρ`'s corrected SE from 0.179 to 0.066. **Both gains are only interpretable once `IC₀₃` and `IC₀₁` are measured**, so it follows universe expansion rather than preceding it. **Trigger: `n = 500` live and `ρ` estimated once.** *(Full curve: k=5 → +26 %, k=25 → +37 %; the returns flatten because D-03's top names differ by ~12 bps of alpha against 866 bps of noise)* |
| **RA-57** | ★★ **Measurement coverage is STRATIFIED ACROSS RANK DECILES and is not a by-product of decision coverage.** Covering only the top-`k` makes `ρ` **undefined, not merely imprecise** — every covered name has nearly the same quant rank (**DN-28**, `L2` CB-3). ★ **This is the single highest-value change in this spec and it costs nothing extra** — it changes *which* names the existing rotating sample picks, not how many |
| **RA-58** | Range restriction is **corrected for (Thorndike Case II) and the correction is reported**, or `ρ̂` is published as `unmeasured` (D-12 **DN-28**) |
| **RA-59** | ✅ **Calibration starts now.** Every closed thesis is scored against its realised outcome, using D-11's journal, which already records what is needed. **Cost: $0.** ★ It is the **single hard blocker** on any Bayesian merge (`L2` CB-10) and the strongest anti-overconfidence device this spec has (RA-20/21) — **and its clock does not start until the scoring does** |

## 7.4b ★★ WHAT RM-1 ACTUALLY MEASURES — and why `k_stab = 5` is the wrong purchase

> ★ **A sharp question deserves a sharp answer: does re-running the same prompt on the same data
> measure our investment analysis, or the language model?** **It measures the language model.**

RM-1 re-runs an identical `bundle_hash` with an identical prompt and rubric. Nothing about the
company, the data, or the analysis changes between runs. What varies is **the decoder's sampling**.

```text
╔══════════════════════════════════════════════════════════════════╗
║  RM-1 MEASURES SELF-INFLICTED VARIANCE.                          ║
║                                                                  ║
║  ⚠ CORRECTED 2026-08-23: written when we believed temperature    ║
║  was settable and merely unset. It is NOT SETTABLE ON THE DEEP   ║
║  TIER — claude-opus-5 rejects it with a 400 (L2 §5.2a).          ║
║                                                                  ║
║  ★ The conclusion is unchanged and now STRONGER. RM-1 was said   ║
║  to measure "a property of a setting nobody set". It measures a  ║
║  property of a setting NOBODY CAN SET — so it was never a        ║
║  measurement of the analysis, and no configuration change could  ║
║  ever have made it one.                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

**What it is genuinely good for**, and this survives:

1. ★ **Detecting an under-determined rubric.** If the criteria were tight (RA-31/32), identical input
   would force an identical *selection*. Dispersion means the criteria admit more than one reading —
   which is **RA-34's defect, and actionable.**
2. **Proximity to a decision boundary.** A 3/5 verdict sits near a threshold. That is real
   information and it is what RA-20 publishes.

**What it is not**, and the question is right:

- It says **nothing about whether the thesis is correct.** §7.2 already records that *consistent
  bias survives every consistency check* — a model can be 5/5 stable and 5/5 wrong.
- It is **not a domain measurement.** It would change if the model, the temperature, or the decoding
  settings changed, with the investment analysis untouched (RM-5 half-recognises this).

| ID | Rule |
|---|---|
| **RA-60** | ⚠ **CORRECTED 2026-08-23 — the premise was wrong for THIS domain.** It read *"set `temperature` explicitly and record it… GW-8 sets production calls to `temperature = 0`."* ★★ **`claude-opus-5` rejects `temperature` with a 400, and D-01 is the deep tier**, so there was never a knob here to set. ✅ **Now owned by [`L2-shared-infrastructure.md`](L2-shared-infrastructure.md) §5.2a: the deep-tier control is `output_config.effort`** (GW-8a, GW-9a). ★ **GW-10's conclusion survives and is now over-determined** — the sampling probe is retired not because temperature 0 removes the variance, but because **the setting does not exist**, so it was never measuring a property anyone controlled. **RA-61's perturbation form is the only stability probe available to this domain** |
| **RA-60a** | ★★ **`effort` is the parameter RM-5 must watch, and today it does not.** RM-5 re-baselines on an INV-8 *tier* change; **`high → xhigh` is not one**, and it would move every deep-tier output with nothing firing. ⚠ **That is worse than the unset temperature RA-60 was written about** — an unset knob is at least visibly unset. Closed by `L2-shared-infrastructure.md` **GW-9b**; **RM-5's scope in §7.1 reads as *"any decoding-control change"*, not *"any tier change"*** |
| **RA-64** | ★ **Every gateway call emits `L2-shared-infrastructure.md` **CT-0.1 LLMCall**, and it is what populates `CT-1.2 AnalysisRun`.** ⚠ *Added by seam audit: D-01 is the **only** domain permitted to import the gateway (AP-5, ST-5) and had never named the record it produces.* ★ **`outcome` has no `partial` value** (GW-22) — a truncated or refused response is a failure, and **both real incidents in this repo came from treating one as a success** |
| **RA-61** | ★★ **DO NOT raise `k_stab` to 5. Change what varies between runs instead.** Resampling the same distribution measures the decoder. ★ **Perturbing the INPUT measures robustness to things that should not matter** — option order (CT-1.2 already records `option_permutation`), evidence-item order, a paraphrased prompt at a fixed version. **Same k× cost, a property of the analysis rather than of the sampler** |
| **RA-62** | ★ **Report the two separately: `sampling_stability` (same input, resampled) and `perturbation_stability` (equivalent input, restructured).** They fail for different reasons and a single "5/5" conflates them. ★ **`perturbation_stability` is the one that belongs on the card** (RA-20) — a verdict that flips when the options are reordered is fragile in a way a reader must see |
| **RA-63** | ⚠ **`k_stab = 5` is reconsidered only if a Bayesian merge becomes reachable** (`L2` CB-10), because `Ω` consumes run-to-run variance. ★ **Even then the perturbation form is the better input**, since `Ω` should express *"how much do we believe this view"*, not *"how randomly did we decode it"* |

## 7.5 What none of this fixes — stated so it is not assumed

Honesty about the limits is part of the design, not a caveat on it.

- **None of it makes the analysis correct.** It makes the analysis's unreliability *visible*. A
  well-monitored wrong answer is still wrong.
- **Consistent bias survives every consistency check.** RM-1 will happily report 5/5 agreement on a
  verdict that is systematically too bullish. Only RM-6…RM-9 and, eventually, RM-12 can see it —
  and those need aggregate data and time.
- **Calibration needs N, and N accrues slowly.** With one actionable recommendation per day
  (INV-6), a usable calibration curve is a multi-year artifact. RA-21's "not yet calibrated" is
  therefore the *normal* state for a long while, and must not be quietly replaced by a plausible
  number.
- **The monitors are gameable.** Tuning prompts until RM-6's base rate looks healthy optimises the
  metric, not the analysis. The metrics are diagnostics for a human, not objectives for a
  search — and the moment one becomes a target it stops measuring (Goodhart).
- **Overconfidence is measured only through the reader's behaviour**, which means RM-12/RM-14
  depend on the decision journal being honest about what was actually done and why.

---

# 8. THE SCORECARD — bounded judgement

The mechanism RA-8 depends on. A scorecard converts an open-ended judgement into a **selection from
written criteria**, which is what makes it repeatable enough to measure.

```yaml
rubric: moat_durability          # ★ §8.1's dimension id — the set is CLOSED (RA-52)
version: 2
levels:
  - score: 4
    criterion: "Raised prices above input-cost inflation in ≥3 of the last 5 years
                with no volume loss disclosed in the filings."
    evidence_required: [income_statement_5y, md_and_a]
  - score: 3
    criterion: "Raised prices with input costs, margins stable."
    evidence_required: [income_statement_5y]
  # …
```

> ⚠ **The `dimension:` line was removed 2026-08-23.** It read `pricing_power`, a name appearing
> nowhere else, while **§8.1 fixes the dimension set to four** and CT-1.4's `scorecard` keys on them.
> A reader of the schema alone would have built a free-text `dimension` field (RA-52).
>
> ★ **And every level now names its `evidence_required`, including the lower ones.** Under **RA-134**
> the union of those lists is `evidence_coverage`'s denominator, so **a level declaring none would
> silently shrink the denominator** — the exact manufacturing RA-134 forbids.

| ID | Rule |
|---|---|
| **RA-31** | The model selects **a criterion**, and the score is *derived* from the selection. It never emits a number directly — a number invites interpolation, and interpolation is where dispersion enters |
| **RA-32** | Every level names the **evidence required**. A level selected without that evidence present in the bundle is a failed selection, not a low-confidence one |
| **RA-33** | Rubrics are **versioned and immutable once published**, exactly like a D-02 feature contract (FE-2). A rubric edit invalidates every baseline in §7.4 (RM-4) |
| **RA-34** | A rubric whose scores **do not disperse** across the universe (RM-7) is a defect in the rubric, and it is fixed by rewriting criteria — never by asking the model to "use the full range" |

---

# 9. THESIS & FALSIFICATION

| ID | Rule |
|---|---|
| **RA-35** | A thesis is **not valid without at least one falsifier** that is *observable*, *dated*, and *checkable without a further judgement call*. "Competition intensifies" is not a falsifier; "gross margin below 55% in any two consecutive quarters" is |
| **RA-36** | Falsifiers are written **at authoring time**, versioned with the thesis, and **never edited** — only superseded by a new thesis version. Editing a falsifier after the fact is how a thesis becomes unfalsifiable |
| **RA-37** | A thesis carries its **bear case**, its **data gaps**, and its **assumptions** as first-class fields, not prose (AP-1, AP-3) |
| **RA-38** | Confidence below `CONFIDENCE_FLOOR` forces `INSUFFICIENT_DATA`; below `CONFIDENCE_HOLD_CAP` caps the verdict at HOLD (INV-012, INV-013). **These are floors on what may be *proposed*, and they are computed from data completeness and evidence coverage — never self-reported by the model**, which would let the model raise its own ceiling |
| **RA-65** | ★ **`evidence_coverage(dimension) = |extracted ∩ required| / |required|`**, where `required` is the **UNION of `evidence_required` across every level of the rubric** and the aggregate is the mean over the four dimensions scored (**RA-52**). ★ **It derives entirely from data the model does not control**, which is what makes RA-38's floor un-gameable. ⚠⚠ **AMENDED 2026-08-23 — as written the metric was DEGENERATE.** `required` read *"the `evidence_required` list of the rubric level **being selected**"*, and **RA-32 makes a level whose evidence is absent UNAVAILABLE** — so every selectable level has all its evidence by construction and coverage is **identically 1.0**; a level declaring no evidence gives **0/0**. ★★ **The metric could never take a value in (0, 1), so RA-38's 0.3/0.5 floors could never fire and RA-67's `confidence := evidence_coverage` was a constant.** See **RA-134** |
| **RA-134** | ★★ **AVAILABILITY is per LEVEL; COVERAGE is per RUBRIC. They answer different questions and RA-65 had conflated them.** ⚠ *Which levels may the model choose from?* is RA-32's, and it is a filter over levels. *How much of what this dimension needed did we actually pull?* is RA-65's, and its denominator must be **what a complete assessment would require** — otherwise **selecting a low-demand level manufactures perfect coverage**, which is RA-66's defect arriving through the numerator instead of the denominator. ★ Under the union denominator the two compose correctly: thin evidence both *restricts the levels available* and *lowers the confidence*, which is the behaviour RA-38 was written to buy |
| **RA-66** | ★★ **An item counts as EXTRACTED only if RA-6's check passed — not merely because the document is in the bundle.** ⚠ **A 10-K that is present but from which the required number could not be pulled is not evidence**, and counting presence rather than extraction is how a coverage metric reports 100 % on a bundle nothing could be read from |
| **RA-67** | ★ **Until calibration exists, `confidence := evidence_coverage`.** There is then **no model-produced confidence to launder**, so RA-38's *"never self-reported"* becomes structural rather than a rule someone enforces. INV-012/INV-013's thresholds (0.3 → `INSUFFICIENT_DATA`, 0.3–0.5 → cap at HOLD) apply to it unchanged |
| **RA-68** | ★ **After calibration lands (RA-59), `confidence` becomes the calibrated estimate and `evidence_coverage` stays as a SEPARATE reported field.** They answer different questions — *how much did we read* versus *how often were we right* — and collapsing them again would hide a well-evidenced thesis that is reliably wrong |

> **RA-38's second clause matters.** AP-1 asks the agent for a confidence score. A model asked to
> gate itself will not gate itself. Completeness and coverage are measurable from the bundle
> (how many required evidence items were present), so the floor is computed from facts the model
> does not control.

---

# 10. INVALIDATION MONITORING

The half of D-01 that is not authoring: watching an existing thesis for the condition that would
break it.

| ID | Rule |
|---|---|
| **RA-39** | Invalidation checking **sees the prior thesis and its falsifiers** — the deliberate exception to RA-18. Re-checking is a different task from re-deciding |
| **RA-40** | The check runs against **new evidence only** — filings and news with a knowability date after the thesis version's `as_of`. Re-reading old evidence produces drift, not information |
| **RA-41** | A fired falsifier produces an **`InvalidationEvent`, not a new verdict.** D-01 reports that the stated condition occurred; whether that changes the position is SEAT-1's (L0 §3.1) |
| **RA-42** | Invalidation is a **cheap-tier, high-frequency** call (INV-8, Haiku 4.5) — materiality triage is shallow and runs daily. Escalation to deep tier happens only when triage flags something |
| **RA-43** | **A thesis with no invalidation check in `STALENESS_FILINGS_HOURS` is reported stale on the card**, not silently trusted |

---

# 10A. THE SCHEDULED CALENDAR — events we know are coming

★ **§10 treats all new evidence as if it arrived unannounced.** Much of it does not. Earnings
reports, FOMC decisions and macro releases are on a published schedule, and a thesis that is about
to be tested by one is a different object from a thesis that is not.

> ⚠ **`L1-data-engine.md` §5A.4b already states its calendar is "consumed by D-01 as
> thesis-invalidation triggers and event-risk context."** D-07 specifies `CalendarEntry` as an
> entity distinct from `CorporateEvent` (**DE-19**), the two-date knowability rule (**DE-18**), the
> pre-run gate (**§6A**) and the feeds. **Nothing on this side consumed any of it.**

## 10A.1 The look-ahead trap, inherited

D-07 measured it: **34.6 % of `earnings-calendar` rows are future-dated**, and a scheduled date is a
*revisable claim*, not a fact.

| ID | Rule |
|---|---|
| **RA-69** | ★ **A scheduled event is evidence about the future and never enters an EvidenceBundle as a fact.** It travels in a dedicated `calendar` block carrying its `knowable_at`, and **no `Claim` may cite it as support for a business fact** (RA-9). *"Earnings are on the 24th"* is not a reason for anything |
| **RA-70** | **A confirmed date and a vendor-estimated date are different fields and render differently.** ⚠ Most vendor earnings dates are estimates until the company announces; an estimated date presented as confirmed produces a pre-event brief written for the wrong week |

## 10A.2 ★ Staleness becomes event-relative

**RA-43 is a timer, and a timer is the wrong instrument.** A thesis is not stale because
`STALENESS_FILINGS_HOURS` elapsed. It is stale because **a scheduled event bearing on it has
occurred and has not been read.**

| ID | Rule |
|---|---|
| **RA-71** | ★ **Staleness is event-relative first, clock-relative second.** A thesis is `stale` if any calendar event of a class it depends on has **occurred** since its `as_of` with no invalidation check against it. RA-43's clock threshold survives as a **floor** for names with no events in the window — it is no longer the primary test |
| **RA-72** | ★ **A thesis authored inside the window before a scheduled event it depends on is marked `pre_event`, with the date, on the card.** Not stale — **provisional**. ⚠ The reader must not have to remember for themselves that a verdict was written four days before results |
| **RA-145** | ★★ **The list J-15 tells the model to choose from must BE IN THE BUNDLE, and the blind view must not withhold it.** ⚠ *Found 2026-08-26 on the first live authoring run.* J-15 says *"name the specific metric or field the check reads, **choosing from the supplied list of available observables**"* — and **nothing supplied a list.** The model wrote four well-formed falsifiers naming no field, every one failed **RA-35**'s observable test, and the thesis raised `NoFalsifierError`. ★ **The model diagnosed it itself**: *"this bundle carries filing line items and disclosure text only. No price or volume series is supplied, so price-level falsifiers would not be checkable by this system and are omitted deliberately."* ⚠ It reasoned correctly about an input that was never complete |
| **RA-146** | ★★ **`observables` is its own bundle part kind, and RA-14 does NOT withhold it.** ⚠ The list began as a `computed` part — and **`BLIND_WITHHELD_KINDS` strips `computed` wholesale**, so J-11 and J-15, which run blind, were the two calls that could not see it. ★ **RA-14 withholds ANCHORS, not vocabulary**: `f_gross_margin` tells the model *what is checkable*, never *what it is worth*, and no price leaks through a field name. ⚠ A blind view that hides the vocabulary makes its own instruction impossible to obey, which is worse than showing an anchor — it produces a failure that looks like the model's |
| **RA-139** | ★ **The window is `PRE_EVENT_WINDOW_DAYS = 10` calendar days** (L0 §config, beside the `STALENESS_*` family). ⚠ *Added 2026-08-25 building B4.6: **RA-72 marks a rendered card field and no spec declared the threshold**, so the marking was unimplementable without inventing one — the same class of defect as `adj_as_of` (DE-45).* ★ **Ten days is chosen from both ends**: it must cover RA-72's own motivating case — *"conviction High, written four days before results"* — with margin, and it must stay small against the ~91-day reporting cycle (≈11 %), because **a window wide enough to be always-on marks nothing**. The window is measured in calendar days to the event, **not trading days** — the reader's question is *how close to the number was this written*, and a weekend does not make a verdict less provisional |

> ★ **RA-72 is the cheapest rule in this section and possibly the most valuable.** The mandate's
> stated behavioural problem is **pyramiding-up** (vision §3) — adding at ever-higher average cost —
> and *"conviction High, written four days pre-earnings"* is exactly the context that makes an add
> look better than it is. The card cannot currently tell the two apart.

## 10A.3 The pre-event brief — pre-commitment, dated

★ **J-15's falsifier machinery aimed at a known date.** Written before the event, it converts a
scheduled release into a test the thesis can fail.

| ID | Rule |
|---|---|
| **RA-73** | ★ **The brief is written and hashed BEFORE the event and is immutable after it** (RA-36's rule, applied to a different artifact). A brief editable post-event is a memory of what we would have said, and its entire value is the possibility of being wrong in public |
| **RA-74** | ★ **The brief predicts nothing.** It maps *outcomes to falsifier states* — what result fires a condition, what clears it, what leaves it undetermined. **A brief containing an expected result is a defect**: a forecast wearing a process's clothing, and it re-anchors the post-event read it was supposed to discipline |
| **RA-75** | ★ **"What this event will NOT tell you" is a mandatory field.** A quarterly result is over-read by default, and the only moment at which naming the limit is free is before the number exists |
| **RA-76** | **Briefs are written for names with a LIVE THESIS, never for the universe** (a brief nobody will read is cost with no reader). This is what keeps the calendar's cost near zero |
| **RA-77** | **A macro or FOMC brief is written once at BOOK level, never per ticker.** ⚠ Thirteen near-identical CPI briefs is not merely waste — it is one macro narrative given thirteen independent chances to leak into thirteen theses |

## 10A.4 The post-event read

The comparison (actual vs guided vs consensus) is D-02's arithmetic. D-01 answers only *did the
stated condition occur?* — which is **V-01/V-02 unchanged**, triggered by the calendar rather than
by a crawler. ★ **No new prompt is required, and that is the correct outcome**: a scheduled event is
not a new kind of question, only a predictable arrival of the existing one.

---

# 10B. UNSCHEDULED EVENTS & SUDDEN MOVES — the surprises

> ⚠ `L1-data-engine.md` §5A.5 ranks the 8-K feed **#3 by value ÷ effort**, noting: *"→ CT-7.4 cache
> invalidation and D-01 invalidation monitoring. **Both already specified, neither has a trigger.**"*
> **That sentence is this section.**

## 10B.1 D-01 does not detect

| Question | Owner |
|---|---|
| Did the price move abnormally? | **D-03** — return against trailing volatility |
| How much was market, sector, idiosyncratic? | ★ **D-02** — a decomposition, on neutral ground |
| Was there an 8-K, and of what item type? | **D-07** — a feed with structured item codes |
| Is the news material? | **D-01**, cheap tier (RA-42) |
| **Does any of it bear on the thesis?** | ★ **D-01** — the only judgement in the chain |

| ID | Rule |
|---|---|
| **RA-88** | ★★ **The residual is computed BEFORE the trigger fires, not after it.** ⚠ A trigger keyed on the **raw** return is measuring the sector, not the company. For semiconductor names a market-plus-sector model explains a large share of return variance, so a raw-return trigger fires on days the whole theme repriced — and those are exactly the days it fires on **every name at once** |
| **RA-89** | ★★ **The clustering diagnostic.** If **two or more** book names trip the move trigger in the same session, that is *prima facie* a common-factor event and **every one of those triggers is suspect until its residual says otherwise.** Deterministic, free, and it needs no factor model to run — ★ a system that fires thirteen invalidation triggers in one day has already diagnosed itself, and should say so rather than escalate thirteen times. ⚠ **It is a PARTIAL detector and may never displace RA-88.** It catches a sector dropping 5 % in a day; it is blind to one drifting 1 %/day for a fortnight — names trip on different sessions, no clustering signature, each looks idiosyncratic. ★ **That slow form is RA-85's weekly accumulation sweep**, so the answer is three layers: RA-89 for the fast common-factor event, RA-85 for the slow one, and **RA-88's decomposition as the only complete one** |
| **RA-90** | ★ **FX is a NAMED TERM in the decomposition, not an entry on an observable list.** A CAD book holding USD names carries an identical currency exposure on **every** position, so it does not diversify away the way name-specific error does. ⚠ It is a systematic contributor **no thesis is about and no analysis will ever explain**, and leaving it inside the residual attributes it to the company (INV-5, L0 INV-001) |
| **RA-91** | ★★ **Acting on an undecomposed move is a top-down decision taken by accident.** ⚠ Exiting a sound position because its sector repriced is an allocation call — **SEAT-1's authority, exercised without the seat and without anyone choosing to.** This is *why* RA-88 is a gate and not a refinement: the macro view this domain refuses to form re-enters as a **false invalidation**, unlabelled |
| **RA-78** | ★ **D-01 never detects a price move.** It receives a **decomposed** move as an input with its arithmetic trail, exactly as it receives a fair value. ★ **The decomposition is sourced from D-02, not D-03** — not because D-03 could not compute it, but because D-02 is neutral ground (L0 §4.2), so consuming it is not consuming SEAT-3's output. A prompt that reads a price series and concludes it moved a lot is arithmetic in a prompt (RA-45, P2) |

## 10B.2 ★ The unexplained residual is the finding

```text
   move  =  market  +  sector  +  idiosyncratic residual
                                   └────────┬────────┘
                                            │  only this needs explaining
                ┌───────────────────────────┴─────────────────┐
                ▼                                             ▼
   the bundle explains it                    NOTHING in the bundle explains it
   (8-K, news, guidance)                                      │
                │                                             ▼
                ▼                          ★ THAT IS THE FINDING, NOT A FAILURE
   route to V-01: does it fire                "the market repriced this name by
   a stated condition?                         3.1σ and our evidence does not
                                               say why" — an information gap
                                               with a direction
```

| ID | Rule |
|---|---|
| **RA-79** | ★ **An idiosyncratic move the evidence does not explain is reported as UNEXPLAINED, never rationalised.** ⚠ An LLM asked *"why did this stock fall"* will always produce a reason. **A plausible reason attached to an unexplained move is strictly worse than the honest gap** — it closes an open question with a fabrication, and nothing downstream can tell the two apart |
| **RA-80** | ★ **An unexplained residual is a `data_gap` with `obtainable: fetchable`**, not a narrative. It is a research instruction — *go find out* — which is S-4's `would_change` applied to price action |
| **RA-81** | **Direction is reported; causation is not inferred from it.** "Fell on the news" requires the news timestamp to precede the move, and D-07 supplies both |

## 10B.3 The 8-K item-code router — deterministic

★ **8-K item numbers are semantically typed by the SEC**, so this is a lookup, not a classification.

| Item | Meaning | Route |
|---|---|---|
| **4.02** | ★ **Non-reliance on previously issued financial statements** | ⛔ **highest severity in this system** — see RA-83 |
| **4.01** | Change in certifying accountant | ⛔ escalate deep tier; pair with E-09 `ap.auditor` |
| **2.02** | Results of operations | → the post-event read (§10A.4) |
| **1.01 / 1.02** | Entry into / termination of a material agreement | escalate if a falsifier names that counterparty or contract |
| **2.01 / 2.05 / 2.06** | Acquisition or disposition · exit costs · **impairment** | ★ escalate — an impairment is management scoring its own capital allocation |
| **3.01** | Delisting notice / listing-rule failure | ⛔ escalate |
| **5.02** | Departure or appointment of directors and officers | escalate where `capital_allocation` rests on a named individual's record |
| **1.05** | Material cybersecurity incident | escalate |
| **7.01 / 8.01** | Regulation FD · other events | ★ cheap-tier triage — where the genuinely unexpected lands, unstructured by design |

| ID | Rule |
|---|---|
| **RA-82** | ★ **8-K routing is a deterministic table keyed on item number, never an LLM classification.** The SEC has already assigned the code; asking a model to classify what the form declares is the reverse of AP-5 |
| **RA-83** | ★★ **Item 4.02 invalidates the EXTRACTIONS, not merely the thesis.** A non-reliance filing withdraws the *facts* the analysis was built from. `evidence_coverage` for the affected periods goes to **zero** (RA-65/66), RA-38's floor fires, and the verdict becomes **`INSUFFICIENT_DATA`** — never "HOLD pending review." ⚠ Every `ScorecardResult` whose selected level cited an affected period is unsupported and must be re-derived, not adjusted |
| **RA-84** | **Only `7.01`/`8.01` and news reach the cheap-tier LLM.** Everything else is routed by the table |
| **RA-138** | ★★ **An extraction is withdrawn by `(evidence_id, PERIOD)`, so RA-83's *"for the affected periods"* is computable.** ⚠ *Added 2026-08-23 building B4.6: **RA-65's `extracted` set has no period axis** — it is a set of `evidence_id`s (RA-66/MP-4) — while **RA-83 requires coverage to fall for the affected periods only**. The two contracts did not compose: a 4.02 naming FY2024 could invalidate **everything** (too broad) or **nothing** (wrong), and there was no third option.* ★ **The item already carries its `period`** (the extraction envelope, §3.0) — what was missing is that the coverage projection **drops it**. A withdrawal filters the extraction set by period and coverage recomputes naturally, so RA-83 needs no special case in the coverage arithmetic. ⚠ **An item with no period is withdrawn by ANY non-reliance filing** — an undated fact cannot be shown to be outside the affected range, and RA-83's whole point is that the evidence was withdrawn |

> ★ **RA-83 is the strongest rule in this section.** A restatement is the one event that reaches
> backwards through everything already concluded. Treating it as "news to consider" rather than
> "the evidence has been withdrawn" is how an analysis outlives the invalidation of its own inputs —
> and it would do so wearing an unchanged `evidence_coverage` figure.

## 10B.4 Cadence — daily and weekly, for different reasons

★ **"Weekly" is right for the sweep and wrong for the trigger.**

| Layer | Cadence | Why |
|---|---|---|
| Residual detection · 8-K routing | **daily**, deterministic, ~free | ⚠ A 4.02 filed Monday cannot wait until Friday |
| Cheap-tier triage of escalations | **daily**, Haiku, escalations only | RA-42 |
| Deep-tier confirmation | **on escalation only** | V-02 |
| ★ **The accumulation sweep** | **weekly** | What no single day trips: a **drip of small residuals** none of which breaches the daily threshold, guidance quietly not repeated, a risk factor added, competitor capacity moving `announced → operating`, a falsifier approaching slowly |

| ID | Rule |
|---|---|
| **RA-85** | ★ **The weekly sweep's subject is ACCUMULATION, not events.** Events are handled daily. The sweep exists for the slow kind of change — which is invisible at daily resolution and is how a thesis usually actually dies |
| **RA-86** | **The sweep runs whether or not anything happened and reports "nothing accumulated" explicitly** (RA-30, DE-35). ★ A sweep that appears only when it has something to say is indistinguishable from a sweep that did not run |
| **RA-87** | ⚠ **The sweep produces no verdict and no recommendation.** It reports state changes and routes them. **INV-6 is untouched** — a weekly monitor that began proposing trades would be a second decision channel, and the constitution permits exactly one |

## 10B.5 ★ ONE DECOMPOSITION, TWO DATA TYPES — fundamental attribution

★ **§10B.2 guards the price side only, and this is a fundamental desk.** The identical mistake is
available on the fundamentals and is currently unguarded:

```text
   Δ margin(company)  =  Δ margin(industry)  +  Δ margin(idiosyncratic)
                         └──── the cycle ────┘   └── about the company ──┘

   "gross margin fell 400bp"          is not a finding
   "gross margin fell 400bp while     is not a finding either — it is the cycle
    the peer set fell 450bp"
   "gross margin fell 400bp while     ★ THAT is the finding
    the peer set fell 120bp"
```

| ID | Rule |
|---|---|
| **RA-92** | ★★ **A scorecard dimension may not be marked down for a movement the peer set shows is industry-wide, without the comparison being stated.** ⚠ `earnings_quality` falling because DRAM ASPs fell across the industry is **J-07's cycle finding, not J-04's quality finding** — a rubric that scores it as quality is measuring the cycle with the wrong instrument, which is RA-34's defect arriving from outside |
| **RA-93** | ★★ **A comparison against a released series uses the print that existed on the date, never the current revised value.** ⚠ Comparing a dated assumption against a revised figure is a look-ahead of exactly the class this project keeps finding (`_cumulative_fys` 41.5 %, FMP TTM 71 %, `historical-market-capitalization` ~28 days). ★ **Vintages are OBTAINABLE for the series that matter, and the rule must say so**: [ALFRED](https://fred.stlouisfed.org/docs/api/fred/alfred.html) publishes as-first-released values via `realtime_start`/`realtime_end` for CPI, PCE, industrial production and treasury series, free, over the FRED API — **FMP's `economic-indicators` is the vendor that cannot, not the world.** So: **vintage-checked where ALFRED covers the series; `revised_series` and UNCHECKED-grade only where it does not** (DE-35). ⚠ Recording it as universally unavailable would permanently downgrade a check that is free for exactly the series that matter |
| **RA-93a** | ★ **The primary macro variable needs no external vintage service at all.** Hyperscaler capex guidance is **company disclosure**, so its vintage is its filing date and D-07's `knowable_at` already carries it (DE-18); treasury rates are market prices and are not revised. **The ALFRED dependency is narrow — CPI, PCE, industrial production — and must not be allowed to gate the capex work that does not need it** |
| **RA-94** | **The industry term comes from D-02's `peer_context` at matching periods, with its arithmetic trail** (RA-45, D-02 §6.2). D-01 does not assemble a peer set and does not choose one — ★ a chosen peer set is a conclusion wearing a denominator |
| **RA-95** | ★★ **The price and fundamental forms are ONE capability on one D-02 surface — and TWO estimators.** Both subtract a common component and keep the residual, so they share the routing, the neutral-ground argument and the vintage rules. ⚠ **They do not share an estimator.** The return form *fits* sensitivities (`β_m, β_s, β_fx`) over hundreds of daily observations; the fundamental form uses **unit sensitivity to the peer median — a difference, not a regression** — because ~5 annual observations cannot support a fitted `β`. ★ **Specifying them as one thing without this clause is how someone regresses on five data points** |
| **RA-96** | ★★ **The peer set has the same vintage problem as a macro series, one data type over.** Companies report across a ~6-week window, so on the day a thesis is written **the peer set is partially reported**. The comparison must declare *which peers had reported as of the date*; a partially-reported peer median is **UNCHECKED-grade** — RA-93's ruling applied verbatim |
| **RA-96a** | ★ **Peer comparison is PERIOD-aligned, never date-aligned.** ⚠ **MU's fiscal year ends in late August while its peers run calendar quarters** — a date-aligned median compares MU's Jun–Aug quarter against peers' Apr–Jun. **MU is on the practice watchlist, so this is not hypothetical**; where periods cannot be aligned the comparison says so rather than aligning on the nearest date |

> ★ **Why this outranks the price version for a fundamental desk.** A false invalidation costs one
> position. **A scorecard that cannot separate the cycle from the company is wrong on every
> cyclical name, in the same direction, for as long as the cycle lasts** — and it will look
> perfectly stable while doing it (RM-1 reports 5/5), because a consistent bias survives every
> consistency check (§7.5).

---

# 10C. ★ THE SECTOR EVIDENCE FILE — the one funded capability

> ✅ **Decision taken 2026-08-20: build it.** With 13 watchlist names largely in one theme, J-08 and
> E-13 currently do the same industry work **thirteen times over the same industry**. That is waste
> today and leverage tomorrow: **one sector file serves nearly the whole book.** ★ The mandate that
> creates the correlated-error exposure (RM-16) also creates the cheapest research leverage
> available — the same fact, cutting both ways.

⚠ **It is also a shared prior by construction** — §7.2's correlated-error channel wearing a data
structure. The guard is not one rule but **four, because a view can hide in four places**:

```text
   ┌──────────────────────────────────────────────────────────────┐
   │  WHERE A VIEW HIDES IN A FILE THAT CONTAINS NO VIEW          │
   │                                                              │
   │   the PROSE      ── an "outlook" field         → RA-97       │
   │   the SAMPLING   ── which items got ingested   → RA-98       │
   │   the ORDERING   ── what sits at the top       → RA-99       │
   │   the SCHEMA     ── what got a column at all   → RA-100      │
   │                                                              │
   │  ★ They get harder to see in that order, and the last one    │
   │    looks like engineering.                                   │
   └──────────────────────────────────────────────────────────────┘
```

| ID | Rule |
|---|---|
| **RA-97** | **Evidence only — no conclusion field of any kind.** No `outlook`, `view`, `implication`, `summary` or `assessment`. ★ If one appears, the rejected macro-narrative option has returned under another name |
| **RA-98** | ★★ **Completeness: the file ingests EVERY item from a defined, versioned source list, and omissions are logged with a reason.** ⚠ **Selection of evidence is itself a conclusion** — a file accumulating the capacity announcements someone found interesting has a view, with no opinion field anywhere in it. **Curation is where the view hides** |
| **RA-99** | ★★ **Fixed date sort — ordered by date and by nothing else.** A file sorted by importance carries an author's view **in the sort key**, and the reader reads the top of it |
| **RA-100** | ★★ **Fixed, versioned schema, immutable within a version** — exactly like a rubric (RA-33). ⚠ **A file whose fields evolve encodes a view in what it decided was worth a column, and this is the hardest of the four to see, because a schema change looks like maintenance.** A new column is an analytical change and takes a version bump |
| **RA-101** | **Capacity rows are append-only with dated status transitions** (`announced → under construction → commissioning → operating`; L0 INV-006). A row is never overwritten — ★ the *transition history* is the finding, and an announcement that quietly never became capacity is invisible once the row is mutated |
| **RA-102** | ★ **The file enters theses as a BUNDLE INPUT and is hashed into `bundle_hash`** (RA-2), with its version declared on every artifact that consumed it. It is shared across every thesis in the industry, so **a defect in it is a correlated defect by construction** — and RM-16 is the instrument that would see it |
| **RA-140** | ★★ **The schema RA-100 versions is `CT-1.6`, and drift is detected by ARITHMETIC.** ⚠ *Added 2026-08-25 building B4.7: **RA-100 requires a "fixed, versioned schema, immutable within a version" and no schema was ever declared** — so AC-1.69's *"a schema change without a version bump raises"* had nothing to compare against, and the hardest of the four guards was the one with no instrument.* ★ **`schema_fingerprint` is derived from the declared field set** (names, types, order) and stored with the version; a file whose fingerprint differs from its declared version's raises. **This is the whole point**: RA-100's own argument is that *a schema change looks like maintenance*, and a check that depends on someone noticing is the check it says will fail |
| **RA-141** | ★★ **RA-99's sort key is the RECORD's date, and a capacity transition IS a record.** ⚠ *RA-99 says "ordered by date"; RA-101 gives a capacity row **several** dates — announced, under construction, commissioning, operating. Sorting rows by announcement buries a transition that happened yesterday next to its 2019 announcement; sorting by latest transition makes the sort key **mutate**, and a file whose order changes without its content changing is not a fixed sort.* ★ **So the file's unit is the dated record, not the row**: each transition is appended as its own record with its own date, the file sorts over records, and the capacity row is the **projection** of its transitions. RA-101's *"the transition history is the finding"* then falls out of the storage model rather than resting on a convention |
| **RA-142** | ★ **`CT-1.1.sector_files[]` — the consumed version is DECLARED, not merely hashed.** ⚠ *RA-102 says the version is "declared on every artifact that consumed it", and the pin (`PIN_FIELDS["sector_file"]`) makes it **hashed into `bundle_hash`** — which is verifiable only by someone still holding the bundle. A reader asking "which sector file did this thesis rest on?" could not answer it from the thesis.* ★ Same seam-defect class as **CT-7.7's missing `report_id`**: the consumer references a version the producer never surfaced. **Hashing proves it did not change; declaring says what it was** — RA-102 needs both |

> ★ **Why four guards rather than the usual one.** *"Evidence, not conclusions"* is necessary and not
> sufficient. Each of RA-98/99/100 closes a channel that survives it, and the ordering matters:
> prose is caught on sight, sampling needs a source list to check against, ordering needs someone to
> ask why it is sorted that way, and **schema drift is indistinguishable from ordinary maintenance
> unless the schema is versioned.**

---

# 11. CONTRACTS

> **ID-collision notice.** `AC-1.k` / `CT-1.k` here key `n` on **D-01**.
> **`sdd/specs/F1_disciplinary_report/spec.md` already issues `AC-1.1`…`AC-1.15` against live code.** *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))*
> Per L0 §16.4 this is knowingly accepted; unlike D-07/F7 it is **live, not latent** — the second
> such case (see `L1-feature-engineering.md` §9). Always qualify: "D-01 AC-1.3" or "F1 AC-1.3".

## CT-1.1 — Thesis (JSON)

```json
{
  "ticker": "MU", "thesis_version": 4, "as_of": "2026-08-16",
  "bundle_hash": "sha256:…", "run_id": "…",
  "verdict": "BUY", "conviction": "Medium-High",
  "verdict_stability": {"k": 5, "modal": "BUY", "agreement": 0.8,
                        "distribution": {"BUY": 4, "HOLD": 1},
                        "probe": "perturbation"},   // ★ RA-62/RA-136 — WHICH probe
  "falsifiers": [
    {"ordinal": 1, "condition": "gross margin < 55% in two consecutive quarters",
     "observable": "f_gross_margin", "source": "D-02", "checkable": true}
  ],
  "bear_case": {"text": "…", "prompt_version": "bear.v3", "run_id": "…"},
  "claims": [{"ordinal": 1, "kind": "fact", "text": "…",
              "evidence_span": {"accession_id": "…", "offset": [1204, 1288]}}],
  "data_gaps": ["no segment detail for the memory business"],
  "assumptions": [{"ordinal": 7, "text": "cycle trough passed in FY2025"}],  // ★ RA-133 — a PROJECTION of kind==assumption claims, ordinals intact
  "sector_files": [{"industry": "semiconductors", "schema_version": "sector.v1",
                    "file_version": 17}],   // ★ RA-142 — declared, not merely hashed
  "confidence": {"value": 0.62, "basis": "evidence_coverage",
                 "calibration": {"n": 3, "status": "not_yet_calibrated"}}
}
```

| Field | Rule |
|---|---|
| `verdict_stability` | **required** — RM-1's output travels with the verdict (RA-20). ★ `probe` names which form produced it (**RA-62**), and on this tier it is always `"perturbation"`: ⚠ **RA-62 asks for `sampling_stability` and `perturbation_stability` reported separately, and the sampling one is `not_measurable` here** — the knob does not exist (GW-8a, GW-10, **RA-136**). A single un-labelled figure conflates them |
| `falsifiers` | ≥ 1, each `checkable: true` (RA-35) |
| `claims[].evidence_span` | required where `kind == "fact"` (RA-9) |
| `sector_files[]` | ★ **RA-142** — every sector file the bundle pinned, by version. ⚠ Hashing proves it did not change; **declaring says what it was**, and RA-102 asks for both |
| `confidence.basis` | never `"self_reported"` (RA-38) |
| `confidence.calibration` | `not_yet_calibrated` until N suffices (RA-21, RA-30) |

## CT-1.4 — ★ GateVerdict (JSON) — the adapter D-12 consumes

> ★ **Added v0.2.0 to close a real hole.** `PASS / FLAG / VETO` appeared **nowhere** in this spec,
> while `L1-decision.md` CT-12.1 shows `{"gate_id": "thesis", "status": "VETO"}` with **no stated
> source**. A `Thesis` is not a gate verdict, and nothing translated one into the other.

```json
{
  "gate_id": "thesis", "ticker": "MU", "as_of": "2026-08-18",
  "status": "VETO",
  "reason": "thesis verdict HOLD does not support the nominated BUY",
  "thesis_version": 4, "thesis_as_of": "2026-08-16",
  "grade": {                                    // transported, not consumed (D-12 DN-25)
    "verdict": "HOLD", "conviction": "Medium-High",
    "stability_fraction": 0.8, "k": 5,
    "verdict_distribution": {"BUY": 4, "HOLD": 1},        // ★ RA-20 renders "BUY 4 / HOLD 1"
    "scorecard": {"moat_durability": 3, "earnings_quality": 4,
                  "balance_sheet_resilience": 3, "capital_allocation": 2},
    "confidence": {"value": 0.62, "basis": "evidence_coverage"}
  }
}
```

### 11.1 ★ Why D-01 owns this mapping and D-12 does not

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE GATE STATUS IS A JUDGEMENT ABOUT THE THESIS'S OWN           ║
║  RELIABILITY — WHICH IS D-01'S KNOWLEDGE, NOT D-12'S.            ║
║                                                                  ║
║  If D-12 derived the status it would need to know what agreement ║
║  fraction counts as unstable and what evidence coverage counts   ║
║  as thin. That is ANALYTICAL POLICY, and D-12 is deterministic   ║
║  composition with no judgement (DN-2). Deriving it there would   ║
║  also be D-12 ORIGINATING a verdict, which DN-1 forbids.         ║
║                                                                  ║
║  So D-01 emits the status. D-12 composes statuses it was given.  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 11.2 The mapping — and it answers QR-2

The gate answers one question: **D-03 nominated a BUY; does the thesis support acting on it?**

| Thesis state | status | why |
|---|---|---|
| verdict **BUY**, stable, confidence above floor | **PASS** | independent agreement |
| verdict **BUY**, `agreement` in `[VETO_FLOOR, FLAG_FLOOR)` | **FLAG** | ★ annotate — QR-2's middle |
| verdict **BUY**, stability **unmeasured**: no RM-1 result, or `k` below `K_STAB` (**RA-154**) | **FLAG** | ★ not shown unstable, so not a VETO; not shown stable, so never a PASS |
| verdict **BUY**, `agreement < VETO_FLOOR` | **VETO** | the model does not reproduce its own answer |
| verdict **HOLD** | **VETO** | the thesis does not support a buy |
| verdict **SELL** | **VETO** | ⚠ and **only** to HOLD — D-12 **DN-9** forbids a gate originating a sell |
| **INSUFFICIENT_DATA** (RA-38 floor) | **VETO** | absence of a thesis, not a weak one |
| thesis **stale** on **RA-71**'s test — an event of a depended class occurred unread, *or* the `STALENESS_FILINGS_HOURS` floor elapsed (RA-43) | **FLAG** | reported, not silently trusted. ⚠ *Amended 2026-08-25: this row named the **clock only**, and B4.6's **RA-71** made staleness **event-relative first**. A thesis stale because results landed unread, but inside the 48-hour floor, **matched no row and therefore PASSed** — and **AC-1.84** requires exactly that case to FLAG for an unrun relay.* |
| a **falsifier has fired** (RA-41) | **VETO** | the stated breaking condition occurred |
| no thesis at all | ★ **`NO_THESIS`**, never PASS | D-12 **DN-10** — the identity must not be reachable by omission |

| ID | Rule |
|---|---|
| **RA-47** | ★ **D-01 emits a `GateVerdict` (CT-1.4) alongside the `Thesis`.** The `Thesis` is the analytical product; the `GateVerdict` is its decision-ready projection. **Both are published — the projection never replaces the thesis**, or the falsifiers and bear case become unreachable |
| **RA-48** | ★ **QR-2 CLOSED: an unstable verdict FLAGS above `VETO_FLOOR` and VETOES below it.** The question presupposed a binary; a two-threshold split gives the reader the 3/5 signal RA-20 wants **and** stops the pipeline acting on a verdict the model cannot reproduce. **Both thresholds are declared config** (L4 CN-1) and appear in the RunManifest |
| **RA-49** | ★ **The mapping is total and deterministic** — every reachable `Thesis` state maps to exactly one status, and identical theses map identically (INV-2). A state with no row is a defect, not a default to PASS |
| **RA-154** | ★★ **An UNMEASURED verdict FLAGS; it never PASSes.** ⚠ *Added 2026-10-01: §11.2 had no row for it, and the code mapped `agreement is None` to PASS, the default RA-49 forbids.* Unmeasured means `verdict_stability` is null **or** carries `k < K_STAB` (a single run's 1.0 agreement is a measurement of nothing; `variance.py`). ★ FLAG, not VETO: RA-48 reserves VETO for a verdict the model is SHOWN not to reproduce, and an unmeasured one has shown nothing either way |
| **RA-135** | ★★ **§11.2's rows OVERLAP, so the status is the MOST CONSERVATIVE match — `VETO ⊐ FLAG ⊐ PASS`.** ⚠ *Added 2026-08-23 building B4.4: RA-49 demands "exactly one status" and **the table is a list of conditions, not a total function**.* A stable, confident **BUY** that is also **stale** matches row 1 (`PASS`) and row 7 (`FLAG`); a `HOLD` whose falsifier fired matches rows 4 and 8. **Without a stated precedence the mapping is neither total nor unique**, and the tempting default — first match wins — makes the status depend on the order the rows happen to be written in. ★ **The meet is already the system's rule** (D-12 §5.1), so this is P3 applied inside D-01 rather than a new mechanism: a gate may only become more conservative as more conditions match. ⚠ **`NO_THESIS` is not on the chain** — it is a distinct state (DN-10) and short-circuits the whole mapping |
| **RA-50** | ★ **`VETO` on a SELL thesis is inert by construction** (D-12 §5.4). D-01 must not expect a SELL thesis to *cause* a sell; it withholds support for a buy. **A thesis that wants an exit says so through an `InvalidationEvent` to SEAT-1** (RA-41), never through the gate |
| **RA-51a** | ★ **The `grade` block carries everything the artifact must RENDER, not a summary of it.** ⚠ **`stability_fraction: 0.6` alone cannot produce RA-20's *"BUY 3 / HOLD 2"*** — 0.6 is equally 3/5, 6/10 or 12/20, and the distribution is not recoverable from a ratio. **`k` and `verdict_distribution` are therefore required**, and `confidence` travels with its calibration status so **RA-21** can refuse to print a bare number |
| **RA-51** | The `grade` block is **byte-identical to the Thesis fields it mirrors** (D-12 DN-26). It is a transport copy, not a recomputation |

## 8.1 ★ The scorecard dimensions — fixed, so D-12's contract is not illustrative

§8 gave a rubric *schema* and one example. The **dimension set itself** was never enumerated, so
`L1-decision.md` CT-12.1 was carrying an invented `{moat, quality, value}`.

| dimension | rubric | asks |
|---|---|---|
| `moat_durability` | `moat_durability@v2` | can it defend pricing and share? |
| `earnings_quality` | `earnings_quality@v1` | do reported earnings convert to cash? |
| `balance_sheet_resilience` | `balance_sheet@v1` | does it survive a bad cycle without dilution? |
| `capital_allocation` | `capital_allocation@v1` | does management reinvest or destroy? |

| ID | Rule |
|---|---|
| **RA-52** | ★ **The dimension set is fixed, versioned and closed.** Four dimensions, each `0–4` by written criteria (RA-31). **Adding one invalidates every §7.4 baseline** (RM-4), exactly as a rubric edit does |
| **RA-53** | ★ **The scorecard is transported, never summed.** There is no composite score. A weighted sum would be a *second* verdict competing with the first, produced by weights nobody fitted — and `L2-signal-combination.md` §5.0's argument against fitted weights applies with more force here, where `n` is smaller still |
| **RA-54** | Each dimension is **independently dispersed-checked** (RM-2). A dimension that does not move across the universe is a defect in its rubric |

## CT-1.5 — ★ RelayReport (JSON) — a relayed analysis and what could be checked

```jsonc
{
  "ticker": "MU", "as_of": "2026-08-22",
  "relay": {
    "assistant": "claude_pro",            // claude_pro | chatgpt_plus | other
    "model_stated": "Claude Opus 4.5",    // ★ SELF-REPORTED by the relayer — never a fact
    "session": "fresh",                   // RA-117 — must be "fresh"
    "relayed_by": "victor",
    "pasted_at": "2026-08-22T19:40:00Z",
    "prompt_blocks": ["RLY-0@v1","RLY-A@v1","RLY-B@v1"],   // RA-122
    "archetype_applied": "cyclical_commodity",             // RA-123 (J-01)
    "passes": 1                            // 1 or 2 — §4B.6
  },
  "verification": {                        // ★ RA-118 — the ingest's own work
    "claims_total": 41,
    "verified": 12, "contradicted": 0, "unverifiable": 29,
    "claims": [{"ordinal": 1, "text": "…", "result": "verified",
                "checked_against": "D-07 f_gross_margin",
                "ours": "55.4", "theirs": "55.4"}],   // ★ RA-143 — PER CLAIM
    "coverage": 0.2927,                    // → RA-114 floors fire on this
    "checked_against": ["D-02 ratios", "D-07 filings", "D-02 peer_context"]
  },
  "verdict_stability": null,               // ★ RA-115 — structurally absent
  "provenance_class": "relayed_judgement", // RA-116 — travels to D-09
  "degraded": false
}
```

| Field | Rule |
|---|---|
| `relay.model_stated` | ★ **self-reported.** Renders as *"stated: …"*, never as a recorded model id |
| `relay.session` | must be `"fresh"` — a continued session fails ingest (RA-117) |
| `verification.claims[]` | ★ **RA-143** — one row per claim with its `result` and what it was checked against. ⚠ The counts are a **projection** of this array, never a parallel store (RA-133's shape) |
| `verification.contradicted` | ★ **non-zero fails the ingest** (RA-118). It is therefore **0 on every persisted report** — the field exists so the *failure* can carry its count, and `claims[]` names which |
| `verification.coverage` | feeds `confidence` unchanged — **this is what caps the verdict** (RA-114) |
| `verdict_stability` | ★ **always `null`.** A single chat response has no distribution (RA-115) |

## CT-1.2 — AnalysisRun (JSON)

`(run_id, ticker, as_of, bundle_hash, prompt_name, prompt_version, model_id, ★ decoding{},
option_permutation, started_at, tokens_in, tokens_out, attempts, outcome)` — AP-6.

> ⚠ **Amended 2026-08-23 (v0.16.0). It read `…model_id, temperature, thinking_mode, …`.**
> **RA-64** makes `CT-0.1 LLMCall` the thing that *populates* this record, and CT-0.1's `decoding`
> is **an object precisely because a flat `temperature: null` cannot distinguish *"this model has no
> such parameter"* from *"nobody set it"*** (GW-9). Flattening it here **reintroduced one contract
> downstream exactly the defect CT-0.1 was reshaped to remove.**
>
> ★★ **And the worse half: `effort` was absent entirely.** §6 puts **both** of D-01's call kinds on
> the **deep tier**, `claude-opus-5` **rejects `temperature` with a 400** (GW-8a), so **`effort` is
> the only decoding control D-01 actually has** — and the record could not hold it. **RA-11**: *"a
> parameter that is not recorded cannot be held responsible"*, and **RA-60a** already warns that
> `effort` is a live control RM-5 does not watch. An `AnalysisRun` that cannot say what effort a run
> used makes RA-60a's hazard permanently un-diagnosable.

| ID | Rule |
|---|---|
| **RA-129** | ★★ **`AnalysisRun.decoding` is `CT-0.1.decoding` transported WHOLE — the object, never a flattened field.** ⚠ *Added 2026-08-23 building B4.1.* The transported block is **byte-identical to its source** and is never recomputed or reshaped in transit (the rule D-12 **DN-26** states for its own grade block, applied here). ★ **A field flattened in transport is indistinguishable downstream from one the producer never emitted** (DN-32's shape): `temperature: null` on a deep-tier record is *"not settable"*, and a reader of a flat field cannot tell that from *"forgotten"* |
| **RA-130** | ★★ **A FAILED call's `AnalysisRun` IS persisted; the failed ANALYSIS is not.** ⚠ *Added 2026-08-23: `AC-1.27` says a degraded call is "never persisted", and **RA-111** requires the run record so *"did not run"* and *"ran and failed"* stay distinguishable — read together, an implementer suppresses the record and destroys exactly what RA-111 exists for.* ★ **They are two different artifacts.** D-15 persisted a **`Narrative`** carrying dataclass defaults to `{TICKER}_synthesis.json` and rendered it; **CT-0.1's `outcome` enum exists to record the failure** (`transport_failed`, `refused`, `truncated`, `unparseable`, `drift_blocked`) — and there is deliberately **no `partial`** (GW-22). ★ The rule in one line: **record that it failed; never record what it produced** |


## CT-1.3 — Monitor report (JSON)

One per run: every `RM-n` with `value`, `n`, and a status.
`status ∈ {ok, warn, fail, not_yet_calibrated, ★ not_measurable}` (**RA-136**).
**Every RM appears** — a missing one is a defect, not a pass (RA-30, cf. `L1-data-engine.md` CT-7.7).

---

## CT-1.6 — ★ SectorFile (JSON) — §10C's four-way guard, as a schema

★ **The object RA-100 versions.** Declared here so `schema_fingerprint` has
something to be a fingerprint *of* (**RA-140**).

```json
{
  "industry": "semiconductors",
  "schema_version": "sector.v1",
  "schema_fingerprint": "sha256:…",   // ★ RA-140 — derived from the field set
  "file_version": 17,                 // RA-102 — the CONTENT version
  "as_of": "2026-08-25",
  "source_list_version": "srcs.v3",   // RA-98 — what completeness is measured against
  "records": [
    {"record_id": "…", "date": "2026-07-14", "kind": "capacity_transition",
     "subject": "TSMC AZ P2", "status": "commissioning",
     "prior_status": "under construction",
     "source_id": "src-tsmc-ir", "url": "…", "quote": "…"}
  ],
  "omissions": [
    {"source_id": "src-samsung-ir", "reason": "IR page returned 503 on three polls",
     "observed_at": "2026-08-25T06:04:00Z"}
  ]
}
```

| Field | Rule |
|---|---|
| *(any conclusion-shaped field)* | ⛔ **forbidden** — no `outlook`, `view`, `implication`, `summary`, `assessment` (**RA-97**) |
| `records[]` | ★ **the file's unit is the dated RECORD, not the row** (**RA-141**). Sorted by `date`, ascending, and **no other sort is exposed** (RA-99) |
| `records[].status` / `prior_status` | RA-101's transitions. A record is **appended**, never overwritten — the capacity row is the *projection* of its records |
| `omissions[]` | **required, and may be empty** — RA-98. ⚠ An omission with no reason is the defect; an empty list is a claim that the source list was fully ingested |
| `schema_fingerprint` | RA-140. Differs from the declared `schema_version`'s fingerprint ⇒ raise. ★ **A new column is an analytical change and takes a version bump** |
| `file_version` | RA-102 — what `CT-1.1.sector_files[]` declares |

## CT-1.7 — ★ SourceList (JSON) — what RA-98 measures completeness against

★ **Versioned, because completeness is only meaningful against a fixed list.**
⚠ *Selection of evidence is itself a conclusion*, so the list is the artifact
that gets reviewed — not the file that results from it.

```json
{
  "source_list_version": "srcs.v3", "industry": "semiconductors",
  "sources": [{"source_id": "src-tsmc-ir", "name": "TSMC investor relations",
               "kind": "company_ir", "cadence": "daily"}]
}
```

| Field | Rule |
|---|---|
| `source_list_version` | bumped on **any** membership change — adding a source is an analytical change (RA-98, and RA-100's argument one level up) |
| `sources[].source_id` | the key `records[].source_id` and `omissions[].source_id` both refer to. ★ **Every source appears in exactly one of the two** — that is the completeness check |

---

# 12. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `build_bundle(ticker, as_of)` | `EvidenceBundle` | deterministic, hashed (RA-4) |
| `extract(bundle, extractor)` | `ExtractionResult` | checked against the bundle (RA-6) |
| `score(bundle, rubric, version)` | `ScorecardResult` | bounded selection (§8) |
| `author_thesis(bundle, k=1)` | `Thesis` | `k>1` runs the stability probe (RM-1) |
| `bear_case(bundle)` | `BearCase` | separate prompt, separate call (RA-15) |
| `check_invalidation(thesis, bundle)` | `list[InvalidationEvent]` | new evidence only (RA-40) |
| `monitors(window)` | `MonitorReport` | the RM-n set (§7.4) |
| `staleness(thesis, as_of)` | `StalenessState` | ★ event-relative, clock as floor (RA-71/72) |
| `pre_event_brief(thesis, event)` | `PreEventBrief` | ★ written **before**, immutable after (RA-73) |
| `route_filing(filing)` | `Routing` | ★ **deterministic** 8-K item table — no LLM (RA-82) |
| `review_move(ticker, date, decomposition)` | `MoveReview` | ★ residual-first; may conclude `unexplained` (RA-88, RA-79) |
| `attribute_change(ticker, metric, periods)` | `ChangeAttribution` | ★ industry vs idiosyncratic; **a difference, not a regression** (RA-95) |
| `sector_file(industry, as_of)` | `SectorFile` | ★ date-sorted, versioned schema, hashed into the bundle (RA-99…RA-102) |
| `weekly_sweep(as_of)` | `SweepReport` | ★ accumulation, never events; always emitted (RA-85/86) |

---

# 13. BUSINESS RULES

| ID | Rule |
|---|---|
| **RA-1…RA-4** | The evidence bundle — §5 |
| **RA-5…RA-7** | Extraction vs judgement — §6 |
| **RA-8…RA-13** | Consistency — §7.1 |
| **RA-14…RA-19** | Bias — §7.2 |
| **RA-20…RA-30** | Reader overconfidence — §7.3 |
| **RA-31…RA-34** | Scorecard — §8 |
| **RA-35…RA-38** | Thesis & falsification — §9 |
| **RA-39…RA-43** | Invalidation — §10 |
| **RA-69…RA-77** | ★ The scheduled calendar — §10A |
| **RA-78…RA-91** | ★ Unscheduled events & sudden moves — §10B |
| **RA-92…RA-96a** | ★ One decomposition, two data types — §10B.5 |
| **RA-97…RA-102** | ★ The sector evidence file — §10C |
| **RA-103…RA-104** | ★ The two paths out of D-01 — §1.2a |
| **RA-105…RA-113** | ★ The runtime workflow — §4A |
| **RA-114…RA-125** | ★ The relay — §4B |
| **RA-44** | D-01 is the **only** domain that imports the LLM gateway (ST-5), and it imports it **only** from `src/shared/llm/` (D-00) |
| **RA-45** | D-01 performs **no arithmetic that D-02 could perform** (P2, AP-5). A ratio computed in a prompt is a defect twice over — undeterministic and duplicated |
| **RA-46** | D-01 never reads `rank_score` or any D-03/D-04 output (INV-014), and this is grep-checkable |

---

# 14. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `RES.BUNDLE.NOT_PINNED` | ERROR | an LLM call was made without a hashed bundle (RA-1, RA-2) |
| `RES.EXTRACT.UNVERIFIED` | ERROR | an extracted value is not present in its cited span (RA-6) |
| `RES.CLAIM.UNCITED` | ERROR | a factual claim with no evidence span (RA-9, INV-004) |
| `RES.CLAIM.SPAN_MISMATCH` | ERROR | the cited span does not contain the asserted value (RM-10) |
| `RES.THESIS.NO_FALSIFIER` | ERROR | thesis with zero checkable falsifiers (RA-35) |
| `RES.THESIS.FALSIFIER_EDITED` | ERROR | an existing falsifier was mutated rather than superseded (RA-36) |
| `RES.VERDICT.NO_STABILITY` | ERROR | a verdict published without RM-1 on the actionable path (RA-20) |
| `RES.CONFIDENCE.SELF_REPORTED` | ERROR | confidence basis is the model's own claim (RA-38) |
| `RES.PROMPT.DRIFT` | ERROR | prompt alignment failed (INV-9) — **surfaced to the caller, never swallowed** |
| `RES.LLM.DEGRADED` | ERROR | the call failed or returned a degraded narrative — **never persisted, never rendered** (P5, DC-3, D-15) |
| `RES.LINT.FORECAST_VOICE` | WARNING | unearned-certainty language in rendered text (RA-26) |
| `RES.MONITOR.INCOMPLETE` | WARNING | an RM-n is absent from the monitor report (RA-30) |
| `RES.CALENDAR.CITED_AS_FACT` | ERROR | a `Claim` cites a scheduled event as evidence for a business fact (RA-69) |
| `RES.BRIEF.MUTATED` | ERROR | a `PreEventBrief` was edited after its event occurred (RA-73) |
| `RES.BRIEF.PREDICTS` | ERROR | a brief states an expected result rather than mapping outcomes to falsifier states (RA-74) |
| `RES.EVIDENCE.WITHDRAWN` | ERROR | ★ an 8-K item 4.02 covers a period a selected rubric level cited — coverage → 0, verdict → `INSUFFICIENT_DATA` (RA-83) |
| `RES.MOVE.RATIONALISED` | ERROR | an unexplained residual was returned with a narrative cause (RA-79) |
| `RES.SWEEP.SILENT` | WARNING | a weekly sweep produced no report at all rather than "nothing accumulated" (RA-86) |
| `RES.MOVE.UNDECOMPOSED` | ERROR | ★ a move trigger fired on a raw return with no residual (RA-88) |
| `RES.MOVE.CLUSTERED` | WARNING | ★ ≥2 book names tripped the same session — common-factor event suspected (RA-89) |
| `RES.SERIES.REVISED` | WARNING | ★ a comparison used a series with no vintage available; the result is UNCHECKED-grade (RA-93) |
| `RES.SCORE.CYCLE_AS_QUALITY` | ERROR | a dimension was marked down for an industry-wide movement with no peer comparison stated (RA-92) |
| `RES.PEER.PARTIAL` | WARNING | ★ the peer set was partially reported at the comparison date — UNCHECKED-grade (RA-96) |
| `RES.PEER.PERIOD_MISALIGNED` | ERROR | a peer comparison aligned on date rather than fiscal period (RA-96a) |
| `RES.SECTOR.CONCLUSION_FIELD` | ERROR | ★ the sector file carries an outlook/view/assessment field (RA-97) |
| `RES.SECTOR.INCOMPLETE` | ERROR | a source-list item was skipped with no logged reason (RA-98) |
| `RES.SECTOR.SCHEMA_DRIFT` | ERROR | the sector-file schema changed without a version bump (RA-100) |
| `RES.SECTOR.ROW_MUTATED` | ERROR | ★ a capacity row was overwritten rather than appended to (RA-101, INV-006) — *the transition history IS the finding, and an announcement that quietly never became capacity is invisible once the row is mutated* |
| `RES.RELAY.CONTRADICTED` | ERROR | ★ a relayed number disagrees with our own data about a fact (RA-118) |
| `RES.RELAY.NOT_FRESH` | ERROR | the response came from a continued session (RA-117) |
| `RES.RELAY.PARTIAL` | ERROR | a truncated or refused chat response — re-run whole, never top up (RA-125) |
| `RES.RELAY.PROMPT_UNATTRIBUTED` | ERROR | the prompt was hand-edited; composition not recorded (RA-122) |
| `RES.RELAY.STABILITY_CLAIMED` | ERROR | ★ a relay report carrying a `verdict_stability` — impossible by construction (RA-115) |

---

# 15. ACCEPTANCE CRITERIA

```text
EVIDENCE & EXTRACTION
□ AC-1.1   An LLM call without a hashed EvidenceBundle raises (RA-1, RA-2)
□ AC-1.2   Same ticker + same as_of => same bundle_hash (RA-4)
□ AC-1.3   An extracted value absent from its cited span raises (RA-6)
□ AC-1.4   Extraction and judgement use separate prompts and separate calls (RA-5)
□ AC-1.5   A factual claim with no evidence span raises (RA-9, INV-004)
□ AC-1.5a  ★ An assumption is a claim with kind=assumption and an ordinal, not
           a bare string; CT-1.1.assumptions[] projects them (RA-133, S-3)
□ AC-1.3a  ★ X-01 resolves the OFFSET: the quote must match the document at
           those offsets before the value is sought in the quote (RA-131)
□ AC-1.3b  A value combined from two figures fails X-01; a reformatted single
           figure passes (RA-132, RA-45)

CONSISTENCY  (§7.1)
□ AC-1.6   Verdict and conviction are enums; a free-form value is rejected (RA-8)
□ AC-1.6a  ★ Where §11.2's rows overlap the MOST CONSERVATIVE wins; a stale
           PASS-eligible thesis FLAGs, and first-match-wins is a defect
           (RA-135, RA-49)
□ AC-1.7   Every AnalysisRun records prompt version, model id, decoding params,
           thinking mode and option permutation (RA-11, RA-17, AP-6)
□ AC-1.8   The actionable pick always carries a k>=3 stability result (RM-1, RA-20)
□ AC-1.9   A prompt change without an RM-4 regression run blocks release
□ AC-1.10  Prompt-alignment drift raises before any call is made (RA-13, INV-9)
□ AC-1.11  No call carries conversational state from a previous call (RA-12)

BIAS  (§7.2)
□ AC-1.12  Qualitative passes receive a bundle with price and valuation withheld (RA-14)
□ AC-1.13  The bear case is produced by a different prompt in a separate call (RA-15)
□ AC-1.14  ★ The falsifier is authored in a SEPARATE call and PERSISTED before
           the verdict call begins; one call emitting both raises (RA-16)
□ AC-1.15  Fresh authoring receives no prior verdict; invalidation does (RA-18, RA-39)
□ AC-1.16  Verdict base rate, per-dimension dispersion and theme skew are computed
           and published weekly (RM-6, RM-7, RM-9)
□ AC-1.17  Seat-disagreement rate with D-03/D-04 is measured (RM-8)
□ AC-1.18  A bear case naming no falsifiable condition fails the run (RM-11)

READER OVERCONFIDENCE  (§7.3)
□ AC-1.19  The card shows verdict stability verbatim, including when unstable (RA-20)
□ AC-1.20  Confidence renders with an empirical referent or as
           "not yet calibrated (N=..)" — never a bare number (RA-21, RA-30)
□ AC-1.21  Claims carry kind=fact|inference|assumption and render distinguishably
           (RA-22, RA-9, S-3)
□ AC-1.22  The falsifier renders above the verdict (RA-23)
□ AC-1.23  Fair value renders as a band, never a point (RA-24)
□ AC-1.24  The data-gap block is present and non-empty-by-construction (RA-25)
□ AC-1.25  Forecast-voice lint violations are zero in rendered output (RA-26)
□ AC-1.26  Narrative sections respect their length caps (RA-27)
□ AC-1.27  A degraded or failed call is never persisted and never rendered
           as analysis (RA-29, P5, DC-3 — the D-15 regression)
□ AC-1.27a ★ ...but its AnalysisRun IS persisted, with the failing outcome, so
           "did not run" and "ran and failed" stay distinguishable (RA-130, RA-111)
□ AC-1.7a  ★ AnalysisRun.decoding is CT-0.1's OBJECT, transported whole and
           byte-identical; a deep-tier run records its effort (RA-129, GW-9)
□ AC-1.28  Every RM-n appears in the monitor report as a value or an explicit
           not_yet_calibrated (RA-30)
□ AC-1.28a ★ A monitor that can NEVER be computed reports not_measurable with
           its reason, never not_yet_calibrated — which promises a number
           that will not arrive (RA-136, GW-10)
□ AC-1.25a ★ The forecast-voice wordlist and length caps are declared ONCE, in
           D-01, and D-09 executes that declaration (RA-137, FE-4)

SCORECARD, THESIS, INVALIDATION
□ AC-1.29  The model selects a criterion; the score is derived, not emitted (RA-31)
□ AC-1.30  A level selected without its required evidence fails (RA-32)
□ AC-1.31  Republishing a rubric version with changed content raises (RA-33)
□ AC-1.32  A thesis with zero checkable falsifiers raises (RA-35)
□ AC-1.33  Editing an existing falsifier raises; superseding is the only path (RA-36)
□ AC-1.34a ★ evidence_coverage's denominator is the UNION over the rubric's
           levels, not the selected level's list — it must be able to take a
           value strictly between 0 and 1 (RA-65, RA-134)
□ AC-1.34  Confidence below the floor forces INSUFFICIENT_DATA; below the cap
           forces HOLD, computed from coverage not self-report (RA-38, INV-012/013)
□ AC-1.35  Invalidation reads only evidence knowable after the thesis as_of (RA-40)
□ AC-1.36  A fired falsifier emits an InvalidationEvent, not a new verdict (RA-41)
□ AC-1.37  A thesis past the staleness threshold is marked stale on the card (RA-43)

SCHEDULED CALENDAR  (§10A)
□ AC-1.41  A Claim citing a CalendarEntry as support for a business fact raises (RA-69)
□ AC-1.42  A vendor-estimated date and a confirmed date are distinguishable in the
           contract and render differently (RA-70)
□ AC-1.43  A thesis with an occurred, unread event of a class it depends on is stale
           even when inside the clock threshold (RA-71)
□ AC-1.44  A thesis authored inside the pre-event window is marked pre_event with
           the date on the card (RA-72)
□ AC-1.45  Editing a PreEventBrief after its event raises (RA-73)
□ AC-1.46  A brief containing an expected result fails the run (RA-74)
□ AC-1.47  "What this event will not tell you" is present and non-empty (RA-75)
□ AC-1.48  Briefs are produced only for names with a live thesis (RA-76); macro and
           FOMC briefs are emitted once at book level, not per ticker (RA-77)

UNSCHEDULED EVENTS & MOVES  (§10B)
□ AC-1.49  src/fundamental computes no return, volatility or move decomposition;
           the decomposition arrives from D-02 with its trail (RA-78, RA-45)
□ AC-1.50  An unexplained residual is returned as unexplained, with no cause, and
           appears as a data_gap with obtainable=fetchable (RA-79, RA-80)
□ AC-1.51  8-K routing is a pure table on item number with no LLM call (RA-82)
□ AC-1.52  An 8-K item 4.02 drives evidence_coverage for the affected periods to
           zero, fires RA-38's floor and yields INSUFFICIENT_DATA (RA-83)
□ AC-1.52a ★ Withdrawal is by (evidence_id, period); an item OUTSIDE the affected
           range survives, and an item with NO period is withdrawn (RA-138)
□ AC-1.53  Only 7.01/8.01 items and news reach the cheap tier (RA-84)
□ AC-1.54  The weekly sweep emits a report every week, including
           "nothing accumulated" (RA-86)
□ AC-1.55  The sweep emits no verdict and no recommendation; INV-6's count of
           actionable recommendations is unchanged by it (RA-87)
□ AC-1.56  A move trigger firing without a residual raises (RA-88)
□ AC-1.57  Two or more book names tripping the same session are reported as a
           suspected common-factor event, not escalated independently (RA-89)
□ AC-1.58  FX appears as a named term in the decomposition, never inside the
           residual (RA-90, INV-5)

FUNDAMENTAL ATTRIBUTION  (§10B.5)
□ AC-1.59  A dimension marked down for a movement the peer set shows is
           industry-wide, with no comparison stated, raises (RA-92)
□ AC-1.60  A comparison against a series with no available vintage is reported
           revised_series and is UNCHECKED-grade, never silently used (RA-93)
□ AC-1.61  The industry term is D-02's peer_context with its trail; src/fundamental
           assembles no peer set (RA-94, RA-45)
□ AC-1.62  The fundamental form uses a difference against the peer median, never a
           fitted sensitivity (RA-95)
□ AC-1.63  A comparison against a partially-reported peer set declares which peers
           had reported and is UNCHECKED-grade (RA-96)
□ AC-1.64  Peer comparison is period-aligned; a date-aligned median raises (RA-96a)
□ AC-1.65  Vintage-checked where ALFRED covers the series; revised_series only where
           it does not (RA-93)

THE SECTOR EVIDENCE FILE  (§10C)
□ AC-1.66  A sector file containing any conclusion-shaped field raises (RA-97)
□ AC-1.67  A source-list item absent from the file with no logged reason raises (RA-98)
□ AC-1.68  The file is returned in date order and exposes no other sort (RA-99)
□ AC-1.69  A schema change without a version bump raises (RA-100)
□ AC-1.70  Capacity rows are append-only; a mutated row raises (RA-101, INV-006)
□ AC-1.69a ★ A file whose schema_fingerprint differs from its declared version's
           raises — drift is caught by arithmetic, not by review (RA-140)
□ AC-1.68a ★ Records sort by record date; a capacity transition is its own dated
           record, and the row is the projection of its records (RA-141, RA-101)
□ AC-1.71  The sector-file version is hashed into bundle_hash and declared on every
           artifact that consumed it (RA-102, RA-2)
□ AC-1.71a ★ CT-1.1.sector_files[] carries the consumed file_version and
           schema_version — declared, not merely hashed (RA-142)
□ AC-1.72  Thesis-error correlation is computed once outcomes accrue and reported as
           not_yet_calibrated until then (RM-16, RA-30)

THE RELAY  (§4B)
□ AC-1.73  WF-8 composes a prompt and makes no LLM call (§4B, RA-122)
□ AC-1.74  A relay prompt is composed from the registry; a hand-edited prompt
           fails ingest (RA-122)
□ AC-1.75  Archetype drives block selection in the composed prompt (RA-123, J-01)
□ AC-1.76  A relayed number contradicting our own data fails the ingest (RA-118)
□ AC-1.77  A relay report's confidence is its verification coverage, and the
           INV-012/013 floors fire on it unchanged (RA-114)
□ AC-1.77a ★ The floors are ONE implementation shared with the scorecard path —
           same thresholds, different denominators, no second copy (RA-144)
□ AC-1.76a ★ A failed ingest names WHICH claim contradicted, and a HOLD-capped
           report names which claims were unverifiable (RA-143, RA-118)
□ AC-1.78  A relay report can never be the actionable pick: verdict_stability is
           null and AC-1.8 therefore cannot be satisfied (RA-115)
□ AC-1.79  A relay report renders with provenance_class=relayed_judgement in
           every medium (RA-116, RP-1)
□ AC-1.80  A continued-session or truncated response fails ingest (RA-117, RA-125)
□ AC-1.81  Relay staleness is event-relative, not clock-relative (RA-120, RA-71)
□ AC-1.82  The daily report renders today's relay queue, returns, and overdue
           and stale as SEPARATE counts (RA-128, D-09)
□ AC-1.83  An unrun queued name's thesis goes stale on RA-71's test; the queue
           does not absorb the consequence (RA-126)
□ AC-1.84  A stale relay-sourced thesis FLAGs at the gate, not PASSes
           (RA-126, §11.2)
□ AC-1.85  No queue entry is re-prioritised for having been skipped, and none is
           dropped to make room (RA-127, RA-128)

INDEPENDENCE & BOUNDARY
□ AC-1.38  No module outside src/fundamental imports the LLM gateway (ST-5, RA-44)
□ AC-1.39  src/fundamental imports nothing from D-03/D-04 (INV-014, RA-46)
□ AC-1.40  No arithmetic in D-01 that D-02 exposes (P2, AP-5, RA-45)
□ AC-1.94 ★ the profile part carries no price/market-cap anchor; the
           allowlist drops unknown vendor fields (RA-147, RA-14)
□ AC-1.95 ★ the filing part selects newest periods, not newest filed
           rows — the prior-year comparative never reads as current (RA-149)
□ AC-1.96 ★ observables span D-02 contract fields AND D-07 statement
           tags; an unpinnable filing refuses (RA-150, RA-2)
□ AC-1.97 ★ no price-derived ratio reaches the blind view, and an
           unknown vendor key defaults to withheld (RA-151, RA-152)
□ AC-1.98 ★ the operating-ratio list is enumerated — no entry matches a
           price/enterprise-value name (RA-152)
□ AC-1.99 ★ consensus field sets are absent from the bundle (RA-153)
```

---

# 16. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QR-1** | What is `k` for RM-1, and what sample? | k=3 is the cheapest signal; k=5 distinguishes 60% from 80% agreement. Cost scales linearly on the deep tier. **The actionable pick is never exempt** — the open part is the rest |
| **QR-2** | ~~Does an unstable verdict block or annotate?~~ | ✅ **CLOSED — both, at two thresholds.** FLAG above `VETO_FLOOR`, VETO below (§11.2, **RA-48**). The question presupposed a binary |
| **QR-3** | Where does the monitor page live — D-09 renders it, but who owns the thresholds? | Thresholds are analytical policy. Leaning D-01 owns them, D-09 renders |
| **QR-4** | Can RM-8 (seat disagreement) be computed before the combine point is decided? | It needs both outputs side by side, which DC-4 already requires on the card. So yes — and it does **not** require L0 §1.6 to be resolved |
| **QR-5** | Does anchor stripping (RA-14) survive contact with the existing master prompt? | `prompt_stock_analysis.md` is one document covering Sections 0–N including valuation. Staging it means splitting the master prompt, which INV-9's alignment manifest tracks section by section — a real but bounded change |
| ~~**QR-6**~~ | ~~How is `evidence_coverage` defined?~~ | ✅ **CLOSED 2026-08-18 — RA-65…RA-68** (recommended, adopted). It is the **fraction of REQUIRED evidence items that were successfully EXTRACTED**, per dimension, aggregated over the dimensions scored |
| **QR-8** | ★ **What is the pre-event window for RA-72?** T−3 trading days is the working default and is unmeasured. It should probably vary by event class — an FOMC repricing and an earnings report have different lead times |
| **QR-9** | ★ **Which event classes does a thesis "depend on" for RA-71?** Declared per thesis at authoring (explicit, more work, checkable), or derived from the falsifiers' `observable` fields (automatic, and quietly wrong when a falsifier names a metric with no event)? *(Leaning: derived from falsifiers, with an explicit override)* |
| **QR-10** | **D-05 also consumes D-07's earnings calendar for event risk.** Does D-05's use and D-01's pre-event brief share one calendar consumer or two? A seam question this spec cannot settle alone |
| **QR-11** | ★ **The macro half of the 2026-08-20 addition is NOT in this spec.** §3 of [`L1-fundamental-analysis-event-and-macro.md`](L1-fundamental-analysis-event-and-macro.md) records the decided methodology — **track thesis assumptions, never forecast the economy**; the deterministic layer lives in **D-02 (neutral ground)** so SEAT-3 can consume it without breaching INV-014; **hyperscaler capex guidance is the primary "macro" variable for this book**. Folding it in requires an `assumptions[]` contract change here and a new D-02 surface |
| **QR-7** | Retention: how many `AnalysisRun` records and bundles are kept? | RM-4/RM-5 need historical bundles to re-run against. Bundles are large (filing text). Probably: hashes forever, payloads windowed |

---

# 17. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §1.6, §5.2 **AP-1…AP-6**, §5.1a **DC-1…DC-5**, INV-004/011/012/013/014 | the agent principles §7 operationalises, and the card rules RA-20…RA-29 feed |
| `L1-feature-engineering.md` §6.2 | the shape D-02 publishes to this domain — numbers **with the arithmetic trail**, which is what makes AP-2 citation possible |
| `L1-data-engine.md` §5A.4b **DE-18…DE-20**, §5A.5 | ★ the event calendar D-01 consumes (§10A) and the 8-K feed §10B triggers — *"both already specified, neither has a trigger"* |
| [`L1-fundamental-analysis-master-prompt.md`](L1-fundamental-analysis-master-prompt.md) | every prompt this domain issues, composed and versioned (INV-9) |
| [`L1-fundamental-analysis-output-template.md`](L1-fundamental-analysis-output-template.md) | the rubric criteria, the wording contract, and the rendered form of `CT-1.1` |
| [`L1-fundamental-analysis-event-and-macro.md`](L1-fundamental-analysis-event-and-macro.md) | ★ the rationale behind §10A/§10B, and **the macro methodology that is not yet folded in** (QR-11) |
| `L1-data-engine.md` §5A.4a, §6A, **DE-35** | the evidence side of the bundle; the calendar check; and the "UNCHECKED, never none" rule RA-30 mirrors |
| `L4-coding-standards.md` §1.2, **ST-5**, §1.5 | path, the LLM-gateway import rule, and the ~3,000 LOC inbound |
| `sdd/specs/constitution.md` P2, P3, P5, **INV-8**, **INV-9** | deterministic-math boundary, verdict monotonicity, fail-loud, model tiering, prompt alignment |
| `sdd/specs/F0_code_map/spec.md` §12 **D-15** | the incident RA-29 exists to prevent — a failed call rendered as a genuine recommendation *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| [`L1-decision.md`](L1-decision.md) **DN-1**, **DN-31**, **DN-33**, §1.2, §1.3 | ★ the composer `CT-1.4` feeds; why no other domain could own composition; narrative-by-reference |
| [`L1-reporting.md`](L1-reporting.md) **§8Z**, **RP-43a**, **RP-44** | ★ what D-09 actually renders — `CT-12.1`, with `thesis_ref` resolved back to `CT-1.1` |
| [`L3-build-sequence.md`](L3-build-sequence.md) **B3**, **B4**, **BS-11** | ★ when this domain is built: a *real-contract* stub gate at B3, the real gate at B4 |
| `sdd/specs/F1_disciplinary_report/spec.md` | the card this domain's output lands on; **AC-1.k collision — always qualify** *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `pipeline/buffett/synthesis/prompt_alignment.py` | INV-9 enforcement, inherited **VERBATIM** |
