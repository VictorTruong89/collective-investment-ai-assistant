# Blueprint — D-01 Fundamental Analysis *(B4.1 … B4.8 — the D-01 slice complete)*

> **Code:** `src/fundamental/` · **Spec:** `sdd/design/rel6_design/L1-fundamental-analysis.md` · **Seat:** SEAT-2
> **Status:** written 2026-08-23 at **B3** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠⚠ **THIS IS A STUB SLICE, AND ALMOST NOTHING OF D-01 IS HERE.** B3 builds `CT-1.4` and a gate
> that always PASSes. The evidence bundle, extraction, the scorecard, thesis authoring, the bear
> case, invalidation monitoring, the sector file and the relay are **B4** (L3 §3A) — §9.

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-26 | ★★ **The assembler — `ticker + as_of` → `EvidenceBundle`** | Every part constructor existed and **nothing built the parts from real data**; the first live run composed its bundle in a scratch script, which is why `probed_thesis` was `None` in every unattended run. `src/fundamental/bundle/for_ticker.py` reads D-07 and D-02; `src/fundamental/thesis/author_for.py` is WF-1's single entry point. ⚠ Four defects surfaced only by running it: **RA-147** (FMP's profile leads with `price`/`marketCap` and `profile` is NOT blind-withheld — dumping it defeats RA-14 with every test green), **RA-148** (D-01's Class-B consumer cannot be a PIT consumer or no thesis can ever be written), **RA-149** (one filing carries the prior-year comparative, so `filing_date` ordering fed a year-stale period as current), **RA-150** (`b3_minimal` has no ratios, so falsifiers needed D-07's statement tags) | *Dumping the vendor profile* — the anchors reach the blind passes and nothing checks a part's content |
| 2026-08-25 *(B4.8)* | ★★ **The INV-012/013 floors take a coverage VALUE, not a `CoverageReport`** | **RA-144.** AC-1.77 says the floors fire on a relay report *"unchanged"* — but the floor function required a **rubric-dimension object a relay cannot build**, because a relay has claims, not extracted rubric evidence. The only readings were *fake the container* or *write a second copy of the floors*, and the second is **FE-4's defect** — the one RA-137 had just removed from the wordlist. ⚠ **The denominators stay different and must**: `required_union` vs `claims_total`. *What is shared is the threshold, not the arithmetic that reaches it* | *A `CoverageReport` adapter on the relay side* — it dresses claims as rubric dimensions, and the fake denominator then flows into every downstream reader of the object |
| 2026-08-25 *(B4.8)* | ★★ **Verification is recorded per CLAIM; the counts are a projection** | **RA-143.** RA-118 says *"the result is recorded per claim"* and `CT-1.5` stored **three integers**. Two readers need the detail and neither can get it from a count: ★ **the ingest failure must name WHICH claim contradicted** — *"contradicted: 1"* is not an error anyone can act on — and a **HOLD-capped report must name which claims were unverifiable**, since that set is exactly what the cap is about | *Keeping the counts and adding a separate claims list* — two stores for one idea is **RA-133's** shape, and they diverge |
| 2026-08-25 *(B4.8)* | ⚠ **§11.2's stale row named the CLOCK, and B4.6 had moved staleness to EVENTS** | A thesis stale because results landed unread, but inside the 48-hour floor, **matched no row and therefore PASSed** — the exact case **AC-1.84** requires to FLAG for an unrun relay. ★ **The code was already right** (the gate takes a `stale` bool, so RA-71's answer flows straight in); **the spec row was the stale artifact**, and it would have been the thing a future reader trusted | *Leaving the row and relying on the caller* — it makes the gate's meaning depend on who computes its input |
| 2026-08-25 *(B4.8)* | ★ **`times_skipped` is recorded and is absent from every ordering** | **RA-127.** *No re-prioritising a name because it was skipped.* ⚠ **Skipping is a decision SEAT-1 is entitled to make**, and D-01's obligation is the override obligation — make it visible and let it stand. A queue that pesters is a system asserting authority it does not hold | *Ageing skipped names up the queue* — it converts a legitimate override into a penalty, quietly |
| 2026-08-25 *(B4.7)* | ★★ **The sector file's unit is the dated RECORD, not the row** | **RA-141.** RA-99 requires a *fixed* date sort and RA-101 gives a capacity row **four** dates. Sorting rows by announcement buries a transition that happened yesterday beside its 2019 announcement; sorting by latest transition makes the **sort key mutate**, so the file reorders without its content changing. ★ With the record as the unit, RA-101's *"the transition history is the finding"* falls out of the storage model instead of resting on a convention | *A `sort_key` field on the row* — it puts the ordering decision back in an author's hands, which is the channel RA-99 exists to close |
| 2026-08-25 *(B4.7)* | ★★ **`schema_fingerprint` — drift is caught by arithmetic** | **RA-140.** RA-100 demands a *"fixed, versioned schema"* and **no schema was ever declared**, so AC-1.69 had nothing to compare against. ⚠ RA-100's own argument is that **a schema change looks like maintenance** — a guard that depends on someone noticing is the guard it says will fail. The fingerprint covers field **order** too, because a reader reads columns in order | *Comparing against the previous file's fields* — it makes the check relative, so a schema that drifts one column per version never trips it |
| 2026-08-25 *(B4.7)* | ★ **A thesis DECLARES the sector-file version, not only hashes it** | **RA-142.** RA-102's *"declared on every artifact that consumed it"* was implemented as a pin inside `bundle_hash` — **verifiable, not readable**. A reader asking *which sector file did this thesis rest on?* could not answer it from the thesis. ★ Derived from the bundle inside `author()`, never a parameter: a caller supplying its own list is the curation RA-19 forbids | *A `sector_files=` argument on `author()`* — it would let an artifact declare a version it never read |
| 2026-08-25 *(B4.7)* | ⚠ **A failing poll becomes a LOGGED OMISSION, not a raised exception** | RA-98 requires every source to produce a record **or** a logged reason. Raising would end the run and leave twelve good sources unpolled, and the next run would face the same source. ★ This is P5 honoured, not bent: **the failure is loud in the artifact**, carries its reason, and `assert_complete` still fails if it is absent | *Raising on the first bad poll* — it makes the file's completeness depend on the order the sources happen to sit in |
| 2026-08-25 *(B4.7)* | **`CONCLUSION_FIELDS` is wider than RA-97's five** | The rule names `outlook`, `view`, `implication`, `summary`, `assessment`. ⚠ **The defect is a conclusion, not a spelling** — renaming `outlook` to `takeaway` is the cheapest possible evasion, and a guard matching only the rule's five words invites exactly that | *Matching the five verbatim* — it turns the most visible of the four guards into the easiest to walk around |
| 2026-08-25 *(B4.6)* | ★★ **Extraction withdrawal is keyed on `(evidence_id, period)`** | **RA-138.** RA-83 says a 4.02 drives `evidence_coverage` to zero *for the affected periods* — but **RA-65's `extracted` set is a set of ids with no period axis**, so the rule had only two implementations, both wrong: withdraw everything, or withdraw nothing. ★ The item already carried its `period`; **the coverage projection dropped it.** Filtering the extraction set by period means coverage recomputes naturally and RA-83 needs no special case in the arithmetic | *A `withdrawn` flag on `DimensionCoverage`* — it would put restatement logic inside the coverage sum, where every future reader has to know it is there |
| 2026-08-25 *(B4.6)* | ⚠ **An extracted item with NO period is withdrawn by any 4.02** | An undated fact **cannot be shown to lie outside** the affected range, and RA-83's entire point is that the evidence was withdrawn. Erring toward keeping it would leave the scorecard resting on a fact nobody can date | *Keeping undated items* — it makes the withdrawal quietly incomplete, which is the failure mode RA-83 exists to prevent |
| 2026-08-25 *(B4.6)* | ★ **`PRE_EVENT_WINDOW_DAYS = 10` calendar days** | **RA-139.** RA-72 marks a **rendered card field** against a window no spec declared. Ten is sized from both ends: it must cover RA-72's own case — *"conviction High, written four days before results"* — with margin, and stay small against a ~91-day reporting cycle, because ★ **a window wide enough to be always-on marks nothing** | *Trading days* — the reader's question is *how close to the number was this written*, and a weekend does not make a verdict less provisional |
| 2026-08-25 *(B4.6)* | ★ **`RA-45` became an architecture rule: `src/fundamental/` imports no array library** | **AC-1.49** asks that D-01 compute no return, volatility or decomposition. That is unenforceable by review — *a prompt that reads a price series and concludes it moved a lot is arithmetic in a prompt* (P2), **and it looks like prose**. A domain with no `pandas`/`numpy` cannot compute one by accident | *A code-review convention* — the same class of rule ST-5 and FE-21 already make structural |
| 2026-08-25 *(B4.6)* | **`depended_classes` never narrows below `earnings`** | RA-71 needs *"a class it depends on"* and no spec derives it. A thesis with any **business** falsifier is read by a quarterly result — that is what a business falsifier *is*. Macro classes are never inferred: a thesis depends on CPI only if a falsifier names it | *Inferring macro dependence from sector* — it would mark every semiconductor thesis stale on every CPI print |
| 2026-08-23 *(B4.5)* | ★★ **`not_measurable` is a third monitor status, distinct from `not_yet_calibrated`** | **RA-136.** RA-30 gave a monitor one way to decline, and it **promises the number is coming**. ⚠ **RM-1's sampling half can NEVER be computed on this tier** — `claude-opus-5` rejects `temperature` (GW-8a), so *the sampling probe was never measuring a property anyone controlled* (GW-10). Reporting it as `not_yet_calibrated (N=0)` tells a reader to wait forever | Using `not_yet_calibrated` — indistinguishable, and it makes an impossibility look like a backlog |
| 2026-08-23 *(B4.5)* | ★★ **The forecast-voice wordlist moved to D-01; D-09 imports it** | **RA-137.** RA-26/RA-27 are **D-01's** rules and `L1-reporting` §8 says so — *"D-01's to satisfy in CONTENT and D-09's to satisfy in RENDERING"* — but neither spec said where the list lives, and B3 had put it in D-09. ⚠ **Two copies is FE-4's defect in another domain**, and the enforcement points differ in consequence: X-03 **fails the run**, RP-18 **blocks the render** | Two lists with a test asserting they match — it detects drift instead of preventing it, and the assertion is the thing most likely to be relaxed |
| 2026-08-23 *(B4.5)* | RM-1 is the **perturbation** probe, and `k` stays at **3** | **RA-61.** *Resampling the same distribution measures the decoder; perturbing the INPUT measures robustness to things that should not matter.* ★ On this tier it is not merely better — **it is the only probe available** | `k_stab = 5` — RA-61 rejects it by name: same k× cost, and it buys a property of the sampler |
| 2026-08-23 *(B4.5)* | **RM-5 watches the whole `decoding` record, not just the tier** | ★★ **GW-9b/RA-60a — the amendment's most consequential clause.** RM-5 keys on an INV-8 *tier* change and `high → xhigh` is not one, so *an effort edit would move every deep-tier output with nothing firing* — **worse than the unset temperature GW-9 was written to fix** | Watching `model_id` alone — matches the letter of RM-5 and misses the live control |
| 2026-08-23 *(B4.5)* | **RM-8 warns at BOTH ends** | ★ *Healthy disagreement is evidence the independence is real.* ⚠ A near-zero disagreement rate is **leakage or shared bias**, and near-total is an inverted seat. Neither is "good" | Warning on high disagreement only — it would read agreement as success, which inverts INV-014's health check |
| 2026-08-23 *(B4.5)* | `_pearson` returns **`None`** for a constant series | ⚠ A constant error series has **undefined** correlation; reporting `0.0` would claim independence that was never measured | Returning 0.0 — RM-16's whole argument turns on ρ, and a fabricated zero is the most flattering possible answer |
| 2026-08-23 *(B4.4)* | ★★ **The falsifiers are PERSISTED in a separate call before the verdict** | **RA-16 amended.** It read *"and is part of the same structured output"* — the exact failure §4A.2 step 8 names: *held in memory, the ordering is nominal and **a single call could produce both***. ★ One call emitting `{falsifiers, verdict}` satisfies the old wording and buys nothing: **the falsifiers get fitted to a verdict already reached** | Keeping the single-output form — it type-checks, reads as compliant, and removes the de-biasing entirely |
| 2026-08-23 *(B4.4)* | **`Thesis` REQUIRES `falsifier_commit_hash`** | ★ The ordering is enforced by the **type**, not by the call sequence: a caller who skipped J-15's write **cannot construct a thesis at all** | Asserting the order in the workflow — then any other caller reproduces the bug |
| 2026-08-23 *(B4.4)* | ★★ **§11.2's status is the MOST CONSERVATIVE matching row** | **RA-135.** The rows **overlap** — a stable, confident BUY that is also stale matches `PASS` *and* `FLAG` — so RA-49's *"exactly one status"* was unachievable. ★ The meet is already the system's rule (D-12 §5.1), so this is **P3 applied inside D-01** | ⚠ **First match wins** — makes the answer depend on the order the rows happen to be written in, which is invisible and untestable |
| 2026-08-23 *(B4.4)* | **The other matches are reported in the reason** | A `FLAG` that says only *"stale"* hides that the thesis was otherwise a `PASS` — and DN-13's *report every binding gate* is the same argument one layer down | Reporting only the binding row — shorter, and it loses why the gate did not veto |
| 2026-08-23 *(B4.4)* | **`GateInputs` does NOT take the nominated verdict** | The gate answers *"does the thesis support acting on this?"* and the answer must not depend on which name D-03 picked. ⚠ Passing it would let the gate tune itself to the nomination — INV-014 by the back door | Passing it "for context" — the most natural-looking way to break seat independence |
| 2026-08-23 *(B4.4)* | Bear-case separateness is checked on the **call id** | RA-15. ⚠ Prose cannot show which call produced it, and *a bear case written in the same breath is a rhetorical concession, not an analysis* | Checking the text — unmeasurable, and it is the thing being defended against |
| 2026-08-23 *(B4.4)* | `author()` **derives** the blind bundle and accepts none | **RA-19** — *if the judging layer could choose its evidence, confirmation bias would have a supply chain.* A caller supplying its own "blind" view **is** that curation | A `blind_bundle` parameter — convenient, and it hands the guard to the thing being guarded |
| 2026-08-23 *(B4.3)* | ★★ **`evidence_coverage`'s denominator is the rubric's UNION, not the selected level's list** | **RA-65 was degenerate.** RA-32 makes a level whose evidence is absent **unavailable**, so every *selectable* level has all its evidence by construction — coverage was **identically 1.0**, or `0/0` for a level declaring none. ★★ **RA-38's 0.3/0.5 floors could never fire and RA-67's `confidence := evidence_coverage` was a constant.** Spec amended (**RA-65**, **RA-134**) before the code | Keeping the selected-level denominator — then *dropping to a low-demand level RAISES coverage*, which is RA-66's manufacturing arriving through the denominator |
| 2026-08-23 *(B4.3)* | **A level declaring no `evidence_required` is refused** | It would be *unconditionally available* (RA-32) **and** shrink coverage's union denominator (RA-134). ★ §8's own example had exactly such a level, and the spec's example was amended too | Allowing it — a level nothing can fail to support is a floor with a hole in it |
| 2026-08-23 *(B4.3)* | The selection echoes the **criterion text**, not a score | **RA-31.** ⚠ A response carrying `score: 3` alone is indistinguishable from an interpolation; **the echo is what ties the answer to a written level**, and a criterion matching none is an invented level rather than a rounding question | Accepting a level index — cheaper to parse, and it removes the only evidence that a *selection* happened |
| 2026-08-23 *(B4.3)* | `ScorecardResult` has **no total, and no `score` field at all** | ★★ **RA-53.** *A weighted sum would be a second verdict competing with the first, produced by weights nobody fitted* — and `L2` §5.0's argument against fitted weights applies with more force here, where `n` is smaller still. A test asserts the absence by name | A composite — every reader will want one, and it is the thing this rubric must not produce |
| 2026-08-23 *(B4.3)* | Coverage carries the **sets**, not just the ratio | RA-25's data-gap block has to say *which* half was missing, and `0.5` cannot | The bare float — smaller, and it makes the gap block unwritable |
| 2026-08-23 *(B4.2)* | ★★ **X-01 resolves the OFFSET before it looks for the value** | **RA-131.** The envelope emits a `quote` *and* an `offset`, and nothing said to resolve the offset. ★ **Checking only value-in-quote verifies the model against itself** — a model that fabricates both consistently passes, and the citation is fiction with a character range attached. **The offset is the only part of a citation the model cannot also author** | Trusting the quote — cheaper, and it makes X-01 a check the thing being checked can satisfy by lying twice |
| 2026-08-23 *(B4.2)* | ★ **"Arithmetically derivable" = reformat ONE figure, never combine two** | **RA-132.** RA-6's phrase covered both readings. `"1,234"` → `1234` is the same figure in another format; `1234 − 1100 = 134` is **D-02's arithmetic** and is the `_cumulative_fys` scar (ARM 2.76×, MU 71 %) | An open "is it derivable?" test — ⚠ read that way, **X-01 accepts anything a determined reader can construct, which is no check at all** |
| 2026-08-23 *(B4.2)* | **No rescaling in X-01** | The envelope returns the value *"in the document's own units"* with a separate `unit` field. Rescaling would let a value disagree with its own declared unit and still pass | Normalising "thousands" — it looks helpful and it silently widens what passes |
| 2026-08-23 *(B4.2)* | ★★ **`Claim.kind` admits `assumption`** | **RA-9 amended.** The enum held two kinds while **S-3 tells the model there are exactly three**. ⚠ The prompt asked for a shape the contract could not hold, so an ingest had to reject valid output or coerce an assumption into an inference — *which S-3 defines as resting on stated facts, and an assumption rests on none* | Coercing to `inference` — it would type-check and quietly relabel a supplied belief as a derived one |
| 2026-08-23 *(B4.2)* | **`assumptions[]` is a PROJECTION of `kind == assumption`** | **RA-133.** Two stores for one idea is how the same prose ends up under two contracts (DN-33's shape). ★ The projection keeps the **ordinal**, which the bare string list destroyed — and S-3's inferences cite ordinals | A parallel list — then an inference cannot point at the assumption it rests on |
| 2026-08-23 *(B4.2)* | Whitespace is the **only** thing normalised in the span comparison | A filing arrives through PDF/HTML extraction, so a run of spaces is a transport artifact. **A changed digit, word or punctuation mark is a real disagreement** | Case-folding or punctuation-stripping — each widens the gap a fabricated quote can hide in |
| 2026-08-23 *(B4.1)* | ★★ **`CT-1.2.decoding` is CT-0.1's OBJECT, transported whole** | The contract carried a **flat `temperature`** — the shape CT-0.1 was reshaped away from (GW-9: a flat `null` cannot distinguish *not settable* from *forgotten*) — **and no `effort` at all**, while §6 puts both call kinds on the deep tier where `effort` is the only knob. **RA-11's *"a parameter that is not recorded cannot be held responsible"* was unsatisfiable.** Spec amended (**RA-129**) before the code | Recording `effort` as a sixth flat field — it would work and would leave the *next* control to be discovered the same way |
| 2026-08-23 *(B4.1)* | ★★ **A failed call's `AnalysisRun` is persisted; the failed analysis is not** | **RA-130.** AC-1.27 (*never persisted*) and RA-111 (*distinguish "did not run" from "ran and failed"*) read together tell an implementer to suppress the record — destroying exactly what RA-111 exists for. **They are two different artifacts** | Suppressing the record — then a flaky provider and a name nobody analysed look identical in the run history |
| 2026-08-23 *(B4.1)* | **A view is a NEW bundle with its own hash and a recorded parent** | RA-14. ⚠ A `blind: bool` would let **one hash stand for two different things the model saw**, and RM-1's whole premise is that a hash identifies *what was read* | A flag on the bundle — cheaper, and it silently breaks the only comparability guarantee §7 has |
| 2026-08-23 *(B4.1)* | The blind/full **view is checked on the PAIR**, both ways | A blind prompt handed the full bundle has lost the anchor-stripping; a full-view prompt handed a redacted one reasons about a valuation it cannot see **and would say so confidently** | Checking only that a blind prompt got a blind bundle — half the failure |
| 2026-08-23 *(B4.1)* | `extra_context` **exists in order to be refused** | RA-12. ⚠ A seam with no such parameter is silently satisfied by a caller who concatenates history into the payload instead; one that names and rejects it puts the rule where someone reaches for it | Omitting it — same reasoning as D-05's `refuse_to_block` and D-11's `revise` |
| 2026-08-23 *(B4.1)* | Alignment hashing **does not normalise whitespace** | *"It was only formatting"* is precisely the edit that slips a method change past a version bump | Normalising — it would make the check agree with the intuition that is wrong |
| 2026-08-23 *(B4.1)* | ⚠ The **inherited 358-LOC `PromptAlignmentChecker` is NOT moved here** | `L4` §1.5 classes it **VERBATIM**, and a verbatim move is a pure `git mv` in its own commit (ST-6) — **it cannot be done by writing a file.** The *gate* AC-1.10 needs is built; the checker composes behind `AlignmentCheck` at cutover | Rewriting it — that would launder a VERBATIM file into new code and destroy its blame |
| 2026-08-23 | The stub returns **`PASS`**, not `NO_THESIS` | §11.2 maps *"no thesis at all"* to `NO_THESIS`, which is the honest status if D-01 **looked and had nothing**. ★ **B3 is a different situation: D-01 has not been built.** `PASS` + `produced_by_stub` says *the gate is not yet real*, which is the true statement | `NO_THESIS` — says the analyst looked, which would be a false claim about a domain that does not exist. Returning `None` — breaks DN-10 outright (BS-11's own example) |
| 2026-08-23 | ★★ **The `grade` block stays entirely `None`** | **BS-34.** Emitting `k: 1, verdict_distribution: {PASS: 1}, stability_fraction: 1.0` is *literally true and completely misleading* — **D-15's exact shape, a plausible value manufactured by a placeholder** | Populating it "so the card renders" — the card renders absence instead, which is the whole of BS-33 |
| 2026-08-23 | `produced_by_stub` carries the **replacing milestone**, not a boolean | A boolean says *this is fake*; a milestone says *and here is when it stops being fake*. The manifest sources its `replaced_at` from this same constant, so record and artifact cannot drift | `is_stub: True` — no less true and much less useful |
| 2026-08-23 | Every `Grade` field is **nullable** | ★ It is the type-level form of BS-34: a schema that *required* `k` would force a stub to invent one | Required fields with sentinel values — sentinels are how a placeholder becomes indistinguishable from a result |

---

# 1. What this domain does, in one paragraph

D-01 is the qualitative seat: it reads filings and news and produces a **thesis**, its falsifiers,
its bear case and a bounded scorecard. **None of that judgement is built.** What exists is the
*apparatus around it*: **B3**'s adapter (`CT-1.4`, the decision-ready projection D-12 consumes, plus
a stub emitter that exercises the D-01 → D-12 seam), and **B4.1**'s reproducibility layer — a pinned,
content-hashed evidence bundle, a run record, an alignment gate, and the single file in `src/` that
may call a model.

# 2. The objects and how they flow

```text
   B4.1  D-07 filings/news ─┐
         D-02 computed ─────┼──► assemble(ticker, as_of) ──► EvidenceBundle
         D-07 profile ──────┘                                  │  bundle_hash
                                                    ┌──────────┴──────────┐
                                        .redact() ──┤                     │
                                        blind view  ▼                     ▼
                                     PromptRegistry.check()   AnalysisGateway.call()
                                     (INV-9, before ANY call)      │
                                                                   ├─ ok ──► CallResult
                                                                   └─ fail ► DegradedCallError
                                                                              │
                                              AnalysisRunLog ◄────────────────┘
                                              (RA-130: the FAILURE is recorded,
                                               the analysis is not)

   B4.2  E-01…E-13 (deep, view:full) ──► ExtractedItem[]  evidence_id · value ·
                                          unit · period · quote · span
                                                │
                       ★ X-01 (DETERMINISTIC, no LLM)
                          ① quote == document[start:end]      ◄── RA-131
                          ② value in quote (reformat only)    ◄── RA-132
                                                │
                       ★ X-02 (DETERMINISTIC, no LLM)
                          every kind=fact carries a RESOLVABLE span
                                                ▼
                                          evidence_ids
                                                │
   B4.3            ┌────────────────────────────┴───────────────┐
                   ▼                                            ▼
        Rubric.available_levels(extracted)        dimension_coverage(rubric, extracted)
        ★ per LEVEL — RA-32                       ★ per RUBRIC (union) — RA-65/RA-134
                   │                                            │
        Selection (criterion echoed)                     CoverageReport
                   ▼                                            ▼
        derive_score ──► DimensionScore ×4          assess_confidence ──► floors
                   └───────────────┬────────────────────────────┘
                                   ▼
                        ScorecardResult — ★ NO TOTAL (RA-53)

   B4.4  bundle.redact() ──► STAGE A (J-01…J-08, view:blind)
                                    │
                        ★ FREEZE — persist + hash        ◄── RA-14 / RA-108
                                    │
                        STAGE B (J-09/J-10, view:full) ──► STAGE C (J-11…J-14)
                                    │
                        STAGE D:  J-15 ──► ★ COMMIT ──► J-16 ──► J-17
                                              │             ◄── RA-16
                                              ▼
                                     Thesis (CT-1.1)
                                              │
                            §11.2 mapping, meet over matching rows (RA-135)
                                              ▼
                                CT-1.4 GateVerdict ──► D-12
                                PASS | FLAG | VETO | NO_THESIS

   B4.5  k=3 authoring passes, INPUT PERTURBED ──► rm1_perturbation_probe
         (option order · evidence order · paraphrase)          │
                                                    StabilityResult
                                        "⚠ unstable: 3 BUY / 2 HOLD"
                                                               │
                       ┌───────────────────────────────────────┤
                       ▼                                       ▼
              Thesis.verdict_stability            CT-1.3 MonitorReport
                       │                          ★ ALL 16 RM-n appear
                       ▼                          ok | warn | fail |
              CT-1.4.grade ──► D-12 ──► D-09      not_yet_calibrated |
              ★ RP-13 can now render it           ★ not_measurable

   B3    stub_gate_verdict(...) ──► constant PASS      ⚠ SUPERSEDED by B4.4
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| `BundlePart` | `src/fundamental/bundle/models.py::BundlePart` | `src/fundamental/bundle/assemble.py` helpers | the bundle | one analysis |
| `EvidenceBundle` | `src/fundamental/bundle/models.py::EvidenceBundle` | `src/fundamental/bundle/assemble.py::assemble` | every call; **RM-1 keys on its hash** | one analysis |
| `PromptBlock` | `src/fundamental/prompts/registry.py::PromptBlock` | `src/fundamental/prompts/registry.py::block` | the alignment gate | the method's lifetime |
| `AnalysisRun` | `src/fundamental/contracts/analysis_run.py::AnalysisRun` | `src/fundamental/prompts/call.py::AnalysisGateway` | RM-1…RM-5, the RunManifest | forever |
| `EvidenceSpan` | `src/fundamental/claims/models.py::EvidenceSpan` | the extractor / the author | X-01, X-02 | the analysis |
| `ExtractedItem` | `src/fundamental/filings/models.py::ExtractedItem` | `src/fundamental/filings/extract.py::run_extraction` | X-01, then the scorecard (B4.3) | the analysis |
| `Claim` | `src/fundamental/claims/models.py::Claim` | the judgement blocks (B4.4) | X-02, D-09's `kind` rendering | the thesis |
| `Rubric` | `src/fundamental/scorecard/models.py::Rubric` | `src/fundamental/scorecard/rubrics/b43_v1.py` | selection, coverage | versioned, immutable |
| `Selection` | `src/fundamental/scorecard/score.py::Selection` | a J-block (B4.4) | `derive_score` | one analysis |
| `ScorecardResult` | `src/fundamental/scorecard/score.py::ScorecardResult` | `build_scorecard` | `CT-1.4.grade.scorecard` | one analysis |
| `StageCommit` | `src/fundamental/thesis/author.py::StageCommit` | `AuthoringRun.freeze_stage_a`, `commit_falsifiers` | later stages **read** it | forever — append-only |
| `Falsifier` | `src/fundamental/thesis/models.py::Falsifier` | J-15 | invalidation (B4.6) | the thesis version |
| `Thesis` | `src/fundamental/thesis/models.py::Thesis` | `AuthoringRun.author` | the gate; D-09 via `thesis_ref` | versioned, superseded never edited |
| `StabilityResult` | `src/fundamental/monitor/variance.py::StabilityResult` | `rm1_perturbation_probe` | the card, **verbatim** (RA-20) | one analysis |
| `MonitorResult` | `src/fundamental/monitor/registry.py::MonitorResult` | each `rm*` function | `MonitorReport` | one run |
| `MonitorReport` | `src/fundamental/monitor/registry.py::MonitorReport` | the run | the monitor page | one run |
| `Grade` | `src/fundamental/contracts/gate.py::Grade` | the gate | D-12 transports it; D-09 renders it | one run |
| `GateVerdict` | `src/fundamental/contracts/gate.py::GateVerdict` | `src/fundamental/thesis/stub_gate.py::stub_gate_verdict` | D-12 | one run |

★ **The object that surprised me: `Grade` with every field `None`.** It looks like an empty object
and it is a *claim* — the claim that nothing was measured. Reading it as "no data yet, fill it in"
is exactly the mistake BS-34 exists to prevent.

★★ **The one B4.5 added: a `MonitorResult` with `status="not_measurable"` is a PERMANENT answer.**
Every other decline in this system means *ask again later*; this one means *never*, and a reader who
treats the two alike waits for a number that cannot arrive. ⚠ It is the only status carrying a
**mandatory** reason, for exactly that reason.

★★ **The one B4.4 added: `falsifier_commit_hash` is a REQUIRED field on `Thesis`.** It reads like
provenance and it is a **precondition**: a caller who never persisted J-15's output cannot construct
a thesis at all. ⚠ The ordering RA-16 is about lives in the type, not in the workflow — because any
other caller would otherwise reproduce the bug.

★★ **The one B4.3 added: `Rubric.required_union` is a DIFFERENT set from any level's
`evidence_required`.** A reader will assume coverage is measured against what the chosen level
needed; it is measured against **what a complete assessment of the dimension would need**. ⚠ That
distinction is the whole of RA-134, and getting it backwards makes the metric constant.

★★ **The one B4.2 added: `evidence_ids` counts EXTRACTED items, never documents.** A `not_found`
item is deliberately absent from the set. ⚠ *A 10-K that is present but from which the required
number could not be pulled is not evidence* (RA-66) — and **that is BS-26's whole argument for
building this before the scorecard**: build rubrics against a system with no extraction and their
`evidence_required` lists will name documents.

★★ **And the one B4.1 added: `bundle_hash` is a HASH OF WHAT WAS READ, not of what was asked.** It
covers the ticker, the `as_of`, the *view*, and every part's pins **and content** — and deliberately
**not** the assembly timestamp, which would make every bundle unique and RM-1 unmeasurable. ⚠ A
reader who assumes it identifies "the NVDA bundle" will be surprised that the blind view has a
different one; that is the point (RA-14).

# 2a. ★ As-built — the assembler and WF-1 *(2026-08-26)*

⚠ Every bundle-part constructor existed and **nothing built the parts from real
data**; the first live run composed its bundle in a scratch script.

| Module | What it is | ⚠ Open / known-limited |
|---|---|---|
| `src/fundamental/bundle/for_ticker.py` | `ticker + as_of` → `EvidenceBundle` from D-07/D-02 | ★★ **RA-147**: `profile` is **not** blind-withheld, so dumping FMP's payload puts `price`/`marketCap` in front of J-11 and J-15 — **RA-14 defeated with every test green.** Allowlisted |
| `src/fundamental/thesis/author_for.py` | WF-1 — assemble → author k=3 → probe | ⚠ **AB-1**: `scorecard={}` and confidence **declared unmeasured**; B4.2/B4.3 are built and this path calls neither |

## ⚠⚠ Open questions carried to `L6-as-built-remaining.md`

★★ **AB-1 / AB-2.** Confidence is `not_measured` and **claim-binding (RA-9) does
not run on the narrative** — the hallucination guard for the *prose*. ⚠ A reader
would wrongly conclude a passing thesis has had its narrative verified; it has
had its **falsifiers** verified and its **verdict** constrained, not its text.

⚠ **`CONFIDENCE_FLOOR` stays at 0.3.** RA-38 computes the floor *from* coverage,
so with no coverage it is **unreachable, not disabled** — and it is **live in the
relay path** (AC-1.77), where the floors are the only thing de-rating a pasted
chat report.

# 3. The sequence — what actually executes

**B4.1 — one call, four guards, in this order** (`src/fundamental/prompts/call.py::AnalysisGateway.call`):

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | assemble & pin | `src/fundamental/bundle/assemble.py::assemble` | RA-3/RA-4 — one `as_of`, nothing knowing the future, deterministic order | `BundleInconsistentError` |
| 1 | **is it pinned?** | `AnalysisGateway._require_pinned_and_aligned` | ⚠ **Before alignment.** An unpinned call that failed on alignment would look like a drift problem and the reader would fix the prompt | `BundleNotPinnedError` |
| 2 | **is the prompt aligned?** | `src/fundamental/prompts/registry.py::PromptRegistry.check` | ★ **INV-9, §4A.2 step 0.** *Checking alignment after the calls checks nothing — the calls already ran* | `PromptDriftError` |
| 3 | **is there ambient state?** | `AnalysisGateway._refuse_ambient` | RA-12. The parameter exists **in order to be refused** | `ConversationalStateError` |
| 4 | **do the views match?** | `AnalysisGateway._require_matching_view` | RA-14, checked **both ways** | `BundleNotPinnedError` |
| 5 | permute options | `AnalysisGateway._permute` | RA-17 — ⚠ **per call, not per stage**: a stage-level permutation would correlate the position bias across the very dimensions RM-2 compares |  — |
| 6 | send | `src/shared/llm/gateway.py::Gateway.call` | D-00 owns transport, retry, budget, decoding | any `LLMError` |
| 7 | record | `src/fundamental/contracts/analysis_run.py::AnalysisRunLog.append` | ★ **RA-111 — before the next step begins.** On failure this still runs (RA-130) | — |

**B4.2 — extraction, then verification** (§4A.2 steps 2 and 3, and they are one call):

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 2 | run the E-blocks | `src/fundamental/filings/extract.py::run_extraction` | **RA-5** — extraction is its own call with its own prompt. Checked on the declared `kind`, not the id | `ExtractionKindError` |
| 3a | ★ resolve the offset | `src/fundamental/claims/verify.py::_assert_quote_matches_document` | ★★ **RA-131.** Without it X-01 checks the model against itself | `SpanMismatchError`, `SpanUnresolvableError` |
| 3b | value in quote | `src/fundamental/claims/verify.py::_assert_value_in_quote` | RA-6, bounded by **RA-132** | `ValueNotInSpanError` |
| — | claims | `src/fundamental/claims/verify.py::x02_verify_claims` | X-02, a deterministic **schema** check | `UncitedClaimError` |

⚠ **Step 3 is inside step 2's call, not after it.** *An unverified fact entering a judgement is a
hallucination with a scorecard built on it* — so verification is not a later stage a caller might
skip.

**B4.3 — the scorecard pass** (`src/fundamental/scorecard/score.py::build_scorecard`):

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | filter the levels | `src/fundamental/scorecard/models.py::Rubric.available_levels` | ★ **RA-32, before the model chooses.** *If the evidence for an option's stated requirements is missing, that option is unavailable to you no matter how well it describes the company* | — |
| 1 | derive the score | `src/fundamental/scorecard/score.py::derive_score` | RA-31 — the criterion resolves to a level, and **availability is re-checked** on the way through | `ScoreEmittedError`, `LevelUnavailableError` |
| 2 | measure coverage | `src/fundamental/scorecard/coverage.py::coverage_report` | ⚠ **Over the RUBRICS, not the selections** (RA-134). Keyed on the selections it is identically 1.0 | `ValueError` on a partial dimension set |
| 3 | apply the floors | `src/fundamental/scorecard/coverage.py::assess_confidence` | **After** coverage, because RA-67 makes confidence *be* coverage until calibration lands | — |

⚠ **Step 2 must not be keyed on step 1's output**, and that is the whole finding: it reads like the
natural dependency and it makes the metric constant.

**B4.4 — WF-1, and the two writes are the whole module** (`src/fundamental/thesis/author.py`):

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 4 | Stage A on a **blind** bundle | `AuthoringRun.author` → `EvidenceBundle.redact` | ★ **RA-14/MP-3** — the staging is physical. *"Do not consider valuation" is a request; an absent field is a guarantee* | `PriorVerdictLeakError` on a view mismatch |
| 5 | ★★ **FREEZE** | `src/fundamental/thesis/author.py::AuthoringRun.freeze_stage_a` | *Staging without a persisted commit lets Stage B silently revise Stage A once it has seen the price — **and the anchor-stripping bought nothing*** | re-commit raises |
| 7 | bear case, separate call | `src/fundamental/thesis/author.py::assert_bear_case_separate` | RA-15, checked on the **call id** | `BearCaseNotSeparateError` |
| 8a | ★★ **COMMIT the falsifiers** | `src/fundamental/thesis/author.py::commit_falsifiers` | **RA-16.** Returns a *hash*, and `Thesis` requires it — so the order is enforced by the type | `UncommittedFalsifiersError` |
| 8b | the verdict | `Thesis.__post_init__` | RA-8's enums, RA-35's falsifier bounds, RA-38's basis | `VerdictNotEnumError`, `NoFalsifierError` |
| 10 | ★ **the gate** | `src/fundamental/thesis/gate.py::evaluate` | §11.2, **meet over matching rows** (RA-135) | `GateMappingError` on an unmapped state |

⚠ **Step 5 before step 6, and step 8a before 8b, are the two orderings a rewrite would collapse** —
both look like bookkeeping and both are the de-biasing.

**B3 — the stub gate (superseded by B4.4):**

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | build the verdict | `src/fundamental/thesis/stub_gate.py::stub_gate_verdict` | the only step | — |
| 1 | validate status | `src/fundamental/contracts/gate.py::GateVerdict.__post_init__` | RA-49: an invented status **is** an unmapped state, and a state with no row is a defect rather than a default to PASS | `ValueError` |
| 2 | validate the grade | `src/fundamental/contracts/gate.py::Grade.__post_init__` | RA-51a: `k` and `verdict_distribution` must agree, or RA-20 renders a distribution that does not sum to its own `k` | `ValueError` |

# 4. ★ The mathematics

★ **No investment arithmetic — RA-45 forbids it, and `test_ac_1_40…` checks it structurally.** But
B4.1 adds one computation that is load-bearing, so the section is no longer empty.

### The bundle hash

| | |
|---|---|
| **Implemented in** | `src/fundamental/bundle/models.py::EvidenceBundle.bundle_hash` |
| **Formula** | ```python\npayload = json.dumps({"ticker":…, "as_of":…, "view":…, "withheld":…,\n                      "parts": [p.to_json_obj() for p in self.parts]},\n                     sort_keys=True, separators=(",", ":"), default=str)\nreturn "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()\n``` |
| **Units** | none — an identifier |
| **Domain / range** | any non-empty part set; an empty bundle raises |
| **Why this form** | ★ **What is IN it and what is OUT of it are both deliberate.** In: ticker, `as_of`, **view**, and each part's pins *and* content. Out: the assembly timestamp — **including it would make every bundle unique and RM-1 unmeasurable**, which is the whole reason the hash exists |
| **Alternatives rejected** | Hashing pins only — two filings with the same accession and different text would collide, and a silent upstream change would look like model variance, which is the exact confusion §5 opens by naming. Hashing content only — then a re-pinned part looks unchanged. **Sorting by arrival order** — RA-4 fails the moment D-07 answers in a different order |
| **Sensitivity** | Total and intended: one changed byte anywhere ⇒ a different hash ⇒ **RA-2 says the two runs are not comparable** |
| **★ Worked example** | Four parts (filing · news · computed · profile) for `NVDA` at `2026-08-23` → `sha256:c6159707…`. **The same four supplied in reverse order → the identical hash** (`sort_key` orders by kind, pins, content-digest). `.redact()` drops the `computed` part → a *different* hash, with `derived_from` set to the first |
| **Known-wrong** | ⚠ `default=str` in the dump means an unexpected pin type is stringified rather than rejected. Today every pin is a `str`/`int`/ISO date, so nothing exercises it — but a `datetime` pin would hash differently from the `date` a reader would assume (§10.6) |

### Number normalisation — RA-132's entire permitted set

| | |
|---|---|
| **Implemented in** | `src/fundamental/claims/verify.py::_as_number` |
| **Formula** | ```python\ncleaned = text.strip().translate(_FORMAT_CHARS)\nnegative = cleaned.startswith("(") and cleaned.endswith(")")\ncleaned = cleaned.strip("()")\nvalue = Decimal(cleaned)\nreturn -value if negative else value\n``` |
| **Units** | **none — and that is the rule.** The value stays in the document's own units; `unit` travels beside it |
| **Domain / range** | anything `Decimal` parses after stripping `, _ $ € £ ¥ %` and space; otherwise `None`, which means *not a number*, not *zero* |
| **Why this form** | ★ **RA-132.** Reformatting one stated figure passes; combining two does not. `Decimal`, not `float`, because a filing's `1234.10` must compare exactly and binary floating point does not |
| **Alternatives rejected** | **Scale words** (`"thousand"` → ×1000) — ⚠ the envelope returns the value *in the document's own units*, so rescaling would let a value disagree with its declared unit and still pass. **Tolerance matching** (`abs(a−b) < ε`) — an extraction is a quotation, not a measurement; "close" is a fabrication that happens to be near |
| **Sensitivity** | None — exact equality after formatting is stripped. **That is deliberate**: every loosening is a gap a fabricated value can hide in |
| **★ Worked example** | `"1,234"` → `1234`; `"(500)"` → `-500`; `"12.5%"` → `12.5`; `"$1,234.50"` → `1234.50`; `"abc"` → `None`. And the one that must fail: a span reading `"$1,234 … against $1,100"` with an extracted `134` — **arithmetically derivable and refused**, because that subtraction is the `_cumulative_fys` scar |
| **Known-wrong** | ⚠ A document writing a negative as `−500` (U+2212 minus) rather than `-500` parses as `None` and the item fails X-01 — a **false rejection**, which is the safe direction but is a real limitation (§10.11) |

### RM-16's `ρ̂` and the effective breadth it implies

| | |
|---|---|
| **Implemented in** | `src/fundamental/monitor/calibration.py::rm16_thesis_error_correlation` |
| **Formula** | ```python\nrho = fmean(pairs)                       # mean pairwise Pearson\neffective_breadth = n / (1 + (n - 1) * rho)\n``` |
| **Units** | `ρ` dimensionless in `[-1, 1]`; breadth in **independent opinions** |
| **Domain / range** | ≥2 names, ≥3 aligned periods, and each series must vary — otherwise `not_yet_calibrated` |
| **Why this form** | ★★ **The asymmetry is the whole point.** Writing a thesis score as `f_i = μ_i + c + u_i`: for a **LEVEL** decision the error variance is `σ²` and breadth collapses to `n/(1+(n−1)ρ)`; for a **RANK** decision the shared error `c` **cancels exactly** and the residual `2(1−ρ)σ²` is *smaller* than independent errors would give. **So a shared bias is dangerous exactly where D-01 GATES, and benign-to-helpful where L2 re-ranks** |
| **Alternatives rejected** | A fitted factor model — five observations, and `L2` §5.0's argument against fitted parameters applies with more force here. Reporting `ρ = 0` when a series is constant — **claims independence that was never measured** |
| **Sensitivity** | ★ Brutal, and that is the finding: at `n = 13`, `ρ = 0.6` gives breadth **1.6, not 13**. A modest correlation removes almost all the apparent coverage |
| **★ Worked example** | Three names whose errors move together (`ρ̂ ≈ 0.99`) → `3/(1+2×0.99) = 1.005` — **three names, barely more than one independent opinion**. Rank decisions over the same three are unharmed |
| **Known-wrong** | ⚠ **Exact only for EQUICORRELATED errors.** Sub-clusters — two rubrics, two sub-themes — leave common structure *inside* each cluster that a single mean `ρ̂` averages away |

### `evidence_coverage` — the number RA-38's floors act on

| | |
|---|---|
| **Implemented in** | `src/fundamental/scorecard/coverage.py::DimensionCoverage.coverage`, aggregated by `CoverageReport.aggregate` |
| **Formula** | ```python\nreturn len(self.matched) / len(self.required)   # matched = required & extracted\n``` with `required = Rubric.required_union` and the aggregate `fmean` over the four dimensions |
| **Units** | dimensionless, `[0, 1]` |
| **Domain / range** | `required` non-empty — enforced by `RubricLevel` refusing an evidence-free level, and this **raises** rather than returning a plausible `1.0` if one ever slips through |
| **Why this form** | ★★ **RA-134.** The denominator is *what a complete assessment of this dimension would need*, so thin evidence both **restricts the levels available** (RA-32) and **lowers the confidence** (RA-38). Keyed on the selected level the two collapse into one and the second stops working |
| **Alternatives rejected** | **The selected level's list** — RA-65 as originally written; ⚠ **identically 1.0**, because RA-32 already removed every level whose evidence is absent. **The highest level's list** — then a dimension with an unreachable top level reports permanent low coverage regardless of what was read. **Counting documents** — RA-66: *a 10-K that is present but from which the required number could not be pulled is not evidence* |
| **Sensitivity** | One missing evidence id moves a 3-item dimension by **0.333**, and the aggregate by **0.083**. ⚠ With four dimensions and 3–4 items each, **a single extraction failure can cross the 0.5 HOLD cap** — which is intended, and is worth knowing before someone reads a cap as a modelling opinion |
| **★ Worked example** | Moat requires `{seg.revenue, seg.op_income, cmp.capacity_announcement}`. All three extracted → `3/3 = 1.0`. Competitor capacity missing → `2/3 = 0.667`, **and level 4 becomes unavailable**. Only `seg.revenue` → `1/3 = 0.333`, levels `[2, 1, 0]`. Nothing → `0.0`.<br>★ A scorecard where **every** dimension took its lowest level scores `(1/3 + 1/3 + 1/3 + 1/4)/4 = 0.3125` — above the `0.3` floor, inside the `0.5` HOLD cap |
| **Known-wrong** | ⚠ **Unweighted.** A dimension needing four items counts the same as one needing three, so `capital_allocation` is harder to cover and pulls the mean down. **Not a measured choice** — see §10.13 |

### `Grade`'s consistency check — the one *near*-arithmetic rule

```python
total = sum(self.verdict_distribution.values())
if total != self.k:
```

⚠ It exists because **RA-51a's failure is a rendering failure that looks like data**:
`stability_fraction: 0.6` is equally 3/5, 6/10 or 12/20, so RA-20's *"BUY 3 / HOLD 2"* is not
recoverable from the ratio. Carrying `k` and the distribution **and letting them disagree** would be
worse than carrying the ratio alone.

# 5. The logic decisions

| Decision | Where | Why this way | What it would take to change it |
|---|---|---|---|
| The gate reports **all** matched rows, binds on the strictest | `src/fundamental/thesis/gate.py::evaluate` | RA-135, and DN-13's *report every binding gate* one layer down | — |
| `_agreement` returns **`None`**, never `1.0` | `src/fundamental/thesis/gate.py::_agreement` | ★ *A thesis with no stability result is not stable; it is **unmeasured***. Fabricating 1.0 is BS-34's shape, and RP-13 is what catches it downstream | B4.5's probe supplies the real number |
| A BUY with **no** stability still PASSes | same | ⚠ Deliberate and load-bearing: the gate cannot demand a measurement B4.5 has not built, so **BS-28 holds the line at DELIVERY instead** — `actionable: false` | B4.5 |
| `not_found` requires a **note** | `src/fundamental/filings/models.py::ExtractedItem` | MP-7. ⚠ *A bare `not_found` is indistinguishable from a step that never ran* | — |
| `VerificationReport` has **no `passed` flag** | `src/fundamental/claims/verify.py` | The checks **raise**; reaching the report *is* the pass. ⚠ A `passed: False` would let a caller forget one `if`, which is the return-value failure mode L4 §5.1 rejects outright | — |
| X-02's `bundle` argument is **optional and named** | `src/fundamental/claims/verify.py::x02_verify_claims` | Supplied, spans are *resolved*; omitted, only *presence* is checked. ⚠ The done-when says **resolvable**, so the weaker call must be visible at the call site rather than inferred | make it required — and every caller that only has claims would then need a bundle it does not hold |
| Pin fields are a **table**, not per-part code | `src/fundamental/bundle/models.py::PIN_FIELDS` | ★ *A part with no stated pin can change without the hash noticing.* A table makes an unpinnable kind impossible to add by accident | one dict entry — and `sector_file` is already declared for **B4.7**, so the hash contract will not move when it lands |
| `TIER` is a module constant | `src/fundamental/prompts/call.py` | **GW-4: the tier is a property of the CALL SITE, declared statically — never chosen at runtime from data.** §6 puts *both* call kinds on deep | — |
| `MAX_TOKENS` is per call kind | same | GW-7a. ⚠ *A single global value either starves the cheap calls or truncates the deep ones, and only the second is fatal* | one dict; values reused from `settings.yaml` (QI-4, closed) |
| The RNG is **seeded** | `AnalysisGateway.__init__` | A run is reproducible (INV-2) while the permutation still varies **across calls within it** (RA-17) | the `seed` argument |
| `SCORECARD_DIMENSIONS` is a closed 4-tuple | `src/fundamental/contracts/gate.py` | RA-52: fixed, versioned, closed. **Adding one invalidates every §7.4 baseline** | a version bump, not an edit |
| An empty `reason` raises | `GateVerdict.__post_init__` | A status with no reason cannot be attributed on the card (DN-13) | — |
| `NO_THESIS` is in `STATUSES` | same | It is a real status D-12 must handle, not an error condition — DN-10 | — |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Changing it affects |
|---|---|---|---|
| `REPLACED_AT` | `src/fundamental/thesis/stub_gate.py` | `"B4.4"` | the manifest's `stubs[].replaced_at` and the card's data-gap line — **one source, two readers** |
| `llm.deep.effort` | config, read by D-00 | `high` | ⚠ **QI-4 is open: *"what effort level do deep-tier calls run at, and was it chosen or defaulted?"*** GW-9a forces it to be **set**; it does not say to what. `high` is the provider default and the obvious first choice, and **nothing has measured it** |
| `MAX_TOKENS` | `src/fundamental/prompts/call.py` | 8000 / 16000 | truncation frequency. ⚠ **GW-7b: with adaptive thinking the response budget is the ceiling minus unknowable thinking, so truncation is *caught, not predicted*** |
| `seed` | `AnalysisGateway` ctor | 0 | the option permutation sequence — a policy choice in code today (CN-3) |
| `CONFIDENCE_FLOOR` | `src/fundamental/scorecard/coverage.py` | `0.3` | INV-012. ⚠ **RA-48 says both thresholds are declared config and appear in the RunManifest** — they are module constants today because B4.3 has no manifest to read them from (§10.12) |
| `CONFIDENCE_HOLD_CAP` | same | `0.5` | INV-013, same gap |
| `VETO_FLOOR` / `FLAG_FLOOR` | `src/fundamental/thesis/gate.py` | `0.5` / `0.8` | ⚠ **RA-48 says both are declared config appearing in the RunManifest** — module constants today, same gap as B4.3's floors (§10.12). ★ And both are **admitted guesses**: no k-run distribution has been observed |
| `K_STAB` | `src/fundamental/monitor/variance.py` | `3` | RM-1's cost. ★ **RA-61 rejects 5 by name** — *same k× cost, and it buys a property of the sampler* |
| `UNSTABLE_BELOW` / `SEVERELY_UNSTABLE_BELOW` | same | `0.8` / `0.5` | the monitor row's colour only. ⚠ **ADMITTED GUESSES** — RA-20 publishes the fraction verbatim and names no threshold |
| `VERDICT_FLIP_CEILING` | `src/fundamental/monitor/regression.py` | `0.30` | RM-4's release block. ★ **The spec's own illustration promoted to a threshold** — *"a wording change that flips 30 % of verdicts is a change of policy"* — never measured |
| `MIN_N` / `MIN_CLOSED_THESES` | `src/fundamental/monitor/base_rates.py` / `src/fundamental/monitor/calibration.py` | `20` | when a weekly or monthly monitor stops declining. ⚠ **ADMITTED GUESSES**, and §6.3's power arithmetic suggests the real numbers are far larger (§10.20) |
| `FORECAST_VOICE` / `LENGTH_CAPS` | `src/fundamental/monitor/lint.py` | RA-26's list | ★★ **RA-137 — declared here, executed by D-09.** One object, imported, not copied |
| `BEAR_OVERLAP_CAP` | `src/fundamental/thesis/author.py` | `0.6` | ⚠ **RM-11 says *"shares > X %"* and never declares X.** 0.6 is a level at which two texts are plainly one argument; never measured (CN-10) |
| `ARCHETYPE_BLOCKS` | `src/fundamental/relay/compose.py` | 6 archetypes | ★ **RA-123's sentence made executable** — which blocks each archetype's prompt carries. ⚠ **Not config**: a seventh archetype is a master-prompt change (J-01), not a relay one |
| `TRUNCATION_MARKERS` / `REFUSAL_MARKERS` | `src/fundamental/relay/ingest.py` | 6 + 3 phrases | RA-125's gate. ⚠ **ADMITTED GUESSES** (CN-10) — the rule names the failure, not the strings a chat UI emits when it hits one |
| `overdue_after_days` | `src/fundamental/relay/queue.py` | `7` | Only the `overdue` **count** on the D-09 block. ★ It changes **nothing** about staleness — RA-126 routes that through RA-71, and the queue never absorbs the consequence |
| `CHASING_VOICE` | `src/reporting/render/relay_queue.py` | 8 phrases | RP-49/RA-127's lint. ⚠ ADMITTED GUESSES, same shape as `FORECAST_VOICE` |
| `SCHEMAS` | `src/fundamental/sector/schema.py` | `sector.v1` | ★ **Not config** — a schema is a versioned artifact like a rubric (RA-33/RA-100). Adding a version is how a column arrives; **editing one in place is the defect** |
| `CONCLUSION_FIELDS` | `src/fundamental/sector/models.py` | 16 words | RA-97's gate. ⚠ **ADMITTED GUESSES beyond the rule's five** (CN-10) — the extra eleven are near-synonyms, not a measured list |
| `CAPACITY_STATUSES` | same | 5 states | RA-101 / L0 INV-006. ★ `cancelled` is ours: **a project that stalls or dies is precisely the history the rule protects**, so the lifecycle is not one-way |
| `PRE_EVENT_WINDOW_DAYS` | `src/fundamental/calendar/staleness.py` | `10` | ★ **RA-139**, mirrored from L0 §config. Which theses render `pre_event` on the card — the pyramiding context RA-72 exists to surface |
| `STALENESS_FILINGS_HOURS` | same | `48` | RA-43's **floor**, no longer the primary test. Only reached for names with no depended event in the window (RA-71) |
| `ITEM_ROUTES` | `src/fundamental/events/router.py` | §10B.3's table | ★ **Not config** — the table *is* the spec section. Adding a row is a spec change, and RA-82 is the reason: the SEC assigned the code, so this is a lookup |
| `ALFRED_COVERED` | `src/fundamental/events/vintage.py` | 11 series | Which comparisons may be graded `revised_series` at all. ⚠ **RA-93 forbids adding to it casually** — recording a free check as unavailable *permanently downgrades* it |
| `PREDICTION_MARKERS` | `src/fundamental/calendar/pre_event.py` | 12 phrases | RA-74's second gate, beside `FORECAST_VOICE`. ⚠ **ADMITTED GUESSES** (CN-10) — RA-74 names the defect and no wordlist |
| `IDENTITY_TOLERANCE` | `src/fundamental/events/moves.py` | `1e-6` | How exactly `market+sector+fx+residual` must equal the total. Float slack only — not a modelling knob |
| the four rubrics | `src/fundamental/scorecard/rubrics/b43_v1.py` | `@v1` | every scorecard. ⚠ **Not config** — a rubric is a versioned artifact (RA-33), and an edit invalidates every §7.4 baseline |
| `VETO_FLOOR` / `FLAG_FLOOR` (RA-48) | ⚠ **not built** | — | B4. They are declared config and appear in the RunManifest when the real gate lands |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | D-07 filings, news, profile at `as_of` | D-07 | `BundleInconsistentError` if any part post-dates the `as_of` |
| in | D-02 computed values + contract version | D-02 | pinned by **contract**, not by value — that is what makes "D-02 changed a formula" distinguishable from model variance |
| in | **CT-0.1** LLMCall | D-00's gateway | `decoding` transported whole into `CT-1.2` (RA-129) |
| out | **CT-1.2** AnalysisRun | RM-1…RM-5, the RunManifest | `ValueError` on a flat `decoding` or an invented outcome |
| in | *(the B3 stub takes a ticker and a date)* | — | — |
| out | **CT-1.4** GateVerdict | D-12 | `ValueError` at construction |
| out | **CT-1.1** Thesis | ⚠ **not produced.** RA-47 requires both to be published; B3 publishes only the projection **because there is no thesis to project** |

# 8. Failure behaviour

| Failure | Detected where | Behaviour |
|---|---|---|
| a part with no stated pin | `BundlePart.__post_init__` | `ValueError` — it could change without the hash noticing |
| a part post-dating the `as_of` | `assemble._assert_internally_consistent` | `BundleInconsistentError` — INV-1 on the input set |
| a call with no hashed bundle | `AnalysisGateway._require_pinned_and_aligned` | `BundleNotPinnedError` |
| a drifted prompt | `PromptRegistry.check` | `PromptDriftError` — ★ **and the transport is never reached** |
| ambient context supplied | `AnalysisGateway._refuse_ambient` | `ConversationalStateError` |
| a blind/full view mismatch | `AnalysisGateway._require_matching_view` | `BundleNotPinnedError` |
| a truncated, refused or unparseable response | the gateway → the seam | `DegradedCallError` — ★ **never returned as analysis**, and the `AnalysisRun` IS written (RA-130) |
| an invented status | `GateVerdict.__post_init__` | `ValueError` naming RA-49 |
| `k` disagreeing with the distribution | `Grade.__post_init__` | `ValueError` naming RA-20 |
| an undeclared scorecard dimension | `Grade.__post_init__` | `ValueError` naming RA-52 |
| an unmapped thesis state (B4) | `src/fundamental/errors.py::GateMappingError` | raises — ★ **never a default to PASS** |

# 9. What this domain deliberately does NOT do — and what B3 leaves unbuilt

| Not in the B3 slice | When |
|---|---|
| ~~the evidence bundle, content hashing, determinism, `CT-1.2 AnalysisRun`~~ | ✅ **B4.1 — built** |
| ~~extraction, the citation spine, evidence spans, X-01/X-02~~ | ✅ **B4.2 — built** |
| **X-06** bear-case substance and **X-07** claim–span semantic agreement | **B4.5** — the two of seven verification steps that *are* prompts, *"where the question is genuinely semantic"* |
| ~~the scorecard, rubrics, `evidence_coverage`, the confidence floors~~ | ✅ **B4.3 — built** |
| ★ **RM-7 dispersion-checking the rubrics** | **B4.5** — ⚠ *a rubric whose scores do not disperse across the universe is a defect in the rubric* (RA-34), and **none of the four has been checked** (§10.14) |
| ~~thesis authoring, the bear case, the real gate~~ | ✅ **B4.4 — built** |
| ~~RM-1's probe, the monitor set, `CT-1.3`, the lint declaration~~ | ✅ **B4.5 — built.** ★ BS-28's boundary lifts |
| ★ **X-06 and X-07** — the two verification steps that ARE prompts | still unbuilt: *"reach for them only where the question is genuinely semantic"* (§10.21) |
| **RUNNING** the k passes RM-1 measures | ⚠ B4.5 measures the spread; **WF-1 runs the passes**, and the J-block prompts are still unregistered (§10.16) |
| the J-block PROMPTS themselves (J-01…J-17) | **B4.4's prompt registry entries** — ⚠ the *machinery* is built and the **prompt text is not** (§10.16) |
| `InvalidationEvent`, the 8-K router, staleness computation | **B4.6** — the gate *consumes* `stale` and `falsifier_fired`; nothing computes them yet (§10.17) |
| ★ **the staged Stage A→D views and the step-5 FREEZE** | **B4.4** — `redact()` is the mechanism; **the staging is not built** (§10.5) |
| the scorecard, rubrics, `evidence_coverage`, confidence floors | **B4.3** |
| thesis authoring, the bear case, falsifiers, ★ **the real gate** | **B4.4** |
| monitors (RM-1…RM-15), the perturbation probe, `not_yet_calibrated` | **B4.5** — and ★ **BS-28: B4.4's output may not be delivered until this lands** |
| invalidation, the calendar, the 8-K router, the weekly sweep | **B4.6** |
| the sector evidence file | **B4.7** |
| the relay | **B4.8** |
| ★ **calling the LLM gateway** | B4. D-01 is the **only** domain permitted to (ST-5), and this slice has no judgement to make |
| deriving its own gate status inside D-12 | ✗ never — DN-31, and §11.1 is the argument |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — the gate is a constant** | ⚠ **expected and declared** | D-12 receives `PASS` regardless of the name. Recorded in the RunManifest (OR-43) and on the card, so it is visible rather than silently true | **BS-27** |
| **10.2 — RA-47 is half-satisfied** | ⚠ expected | *"Both are published — the projection never replaces the thesis."* B3 publishes only the projection **because no thesis exists**; at B4.4 both must appear together or the falsifiers become unreachable | RA-47 |
| **10.3 — §11.2's mapping table is not implemented** | ⚠ expected | Nine thesis states map to four statuses and **none of that code exists**. `GateMappingError` is defined and unreached — a signpost, not an implementation | RA-49 |
| **10.4 — `EvidenceBundle.contains` is superseded and still present** | ⚠ medium | B4.1 shipped it as a crude substring test; **X-01 is now the real check** and nothing in `src/` calls `contains` any more. ⚠ It remains on the public bundle type, where a future caller could still mistake it for RA-6 | new — no ID; delete it or rename it `_looks_present` |
| **10.9 — X-01 verifies FILING spans only** | ⚠ **medium** | `EvidenceSpan.resolve` searches `bundle.of_kind("filing")`. A claim citing a **news** item or a **computed** metric has no resolvable span and would raise `SpanUnresolvableError`. ★ S-3 anticipates this — *"or the exact metric name for a computed number"* — and **that path is not built** | new — no ID; needed by B4.4's claim binding |
| **10.10 — nothing enforces that a judgement consumed extraction OUTPUT** | ⚠ **medium** | **RA-7**: *judgement calls consume extraction outputs, never raw documents.* B4.2 verifies extraction and B4.4 will author judgement, but **no code yet stops a J-block being handed the raw bundle** — the ordering is in §4A.2 and not in a type | **RA-7**, B4.4 |
| **10.20 — every monitor threshold is an admitted guess** | ⚠ **medium, and uniformly so** | `MIN_N = 20`, `VERDICT_FLIP_CEILING = 0.30`, `UNSTABLE_BELOW = 0.8`, `ABANDONMENT_CEILING = 0.5`, `BUY_BASE_RATE_CEILING = 0.6` — **not one was measured.** ★ CN-10 says an admitted guess is an acceptable answer and silence is not, so each is named at its declaration; but a reader should not mistake the set for a calibrated instrument | CN-10 |
| **10.21 — X-06 and X-07 are not built** | ⚠ medium | §1.4's two *semantic* verification calls: *does the bear case name a falsifiable condition* and *does the span actually support the sentence*. B4.4's `BearCase` checks the **presence** of a falsification condition; **nothing checks it is about anything** | §1.4, RM-10, RM-11 |
| **10.22 — RM-1 measures a spread it does not produce** | ⚠ **medium, and it is the honest limit** | `rm1_perturbation_probe` takes the `k` verdicts as an argument. **Running the k perturbed authoring passes is WF-1's job and is not wired** — so the probe is correct and currently un-fed, exactly as §10.16 leaves the J-blocks unregistered | new — no ID |
| **10.23 — `MonitorReport` is assembled by the caller** | low | Nothing forces a run to *build* one; `MonitorReport` only refuses an incomplete one once you do. ⚠ A run that never assembles a report satisfies AC-1.28 vacuously — which is DE-35's shape one level out | new — no ID |
| **10.16 — the J-block prompt TEXT is not registered** | ⚠ **medium, and it is the honest limit of this slice** | B4.4 builds the staging, the commits, the contracts and the mapping. **The seventeen judgement prompts live in `L1-fundamental-analysis-master-prompt.md` and are not in the `PromptRegistry`** — so the machinery has nothing to run yet. ★ That is *why* every test here constructs a `Thesis` directly rather than authoring one through the seam | new — no ID |
| **10.17 — `stale` and `falsifier_fired` are INPUTS nobody computes** | ⚠ medium | `GateInputs` takes them as booleans and B4.6 owns both (RA-71's event-relative staleness, RA-41's fired falsifier). ⚠ **A caller passing `False` for both gets a gate that never flags for staleness** — which is correct today and silently wrong the moment B4.6 lands without wiring | RA-71, RA-41 |
| **10.18 — `CommitLog` is in-memory** | ⚠ medium | RA-108 says the freeze is **persisted**; this persists it for the life of one `AuthoringRun`. ★ The *hash* survives on the `Thesis`, so a later reader can verify a commit happened — but **the payload does not**, and RA-109's resume-by-stage needs it on disk | RA-109 |
| **10.19 — `UncommittedFalsifiersError` is reused for a re-commit** | low | `CommitLog.commit` raises it when a stage is already committed, which is a *different* fault from a missing commit. The message is right; **the class name is not** | new — no ID |
| **10.12 — the confidence thresholds are module constants** | ⚠ medium | **RA-48**: *both thresholds are declared config and appear in the RunManifest.* They are `0.3`/`0.5` in code, so **a run cannot record which floors it applied** — and a threshold nobody can read from the manifest is one that can move silently | RA-48, CN-5 |
| **10.13 — coverage is unweighted across dimensions** | ⚠ medium | A dimension requiring four evidence items is harder to cover than one requiring three, so `capital_allocation` pulls the aggregate down for a structural reason rather than an evidential one. **Not a measured choice** — an admitted default (CN-10) | new — no ID |
| **10.14 — no rubric has been dispersion-checked** | ⚠ **medium, and it is RA-34's whole point** | *A rubric whose scores do not disperse across the universe (RM-7) is a defect in the rubric, and it is fixed by rewriting criteria — never by asking the model to "use the full range".* These four are **first drafts**, and RM-7 needs a universe of scored names | RA-34, RM-7, B4.5 |
| **10.15 — `evidence_ids` are declared in two places** | ⚠ medium | `src/fundamental/scorecard/rubrics/b43_v1.py`'s `E` table names the ids the rubrics require; B4.2's extractors will emit them. **Nothing checks the two agree** — a typo makes a level permanently unavailable, which reads as thin evidence rather than as a wiring bug | new — no ID; needs a cross-check once the E-blocks emit |
| **10.11 — a Unicode minus fails to parse** | low | `"−500"` (U+2212) → `None` → X-01 rejects the item. A **false rejection**, which is the safe direction, but it would look like a model error rather than an encoding one | new — no ID |
| **10.5 — the Stage-A freeze is not built** | ⚠ expected | `redact()` produces a blind bundle; **nothing persists and content-hashes the Stage-A output** (RA-108). ★ *Staging without a persisted commit lets Stage B silently revise Stage A once it has seen the price — and the anchor-stripping bought nothing* | **B4.4**, §4A.2 step 5 |
| **10.6 — `default=str` in the hash payload** | low | An unexpected pin type is stringified rather than rejected. Nothing exercises it today (all pins are `str`/`int`/ISO date), but a `datetime` pin would hash differently from the `date` a reader would assume | new — no ID |
| **10.7 — alignment cannot catch a co-ordinated edit** | ⚠ **medium, and unfixable here** | The hash catches a file touched *after* declaration. **It cannot catch an author who edits the text and bumps the version together** — and nothing mechanical can. That is **RM-4**'s prompt-change regression run, and it is B4.5's | RM-4, AC-1.9 |
| **10.8 — `_model_id()` reaches into the gateway's private config** | low | Only on the failure path, to record a model id the failed call never returned. ⚠ It couples the seam to a `_cfg` attribute; a public accessor on the gateway would be cleaner | new — no ID |

| **10.15 — `STATUSES` was defined three times with three different tuples** | ⚠ **found and fixed, 2026-08-25** | `contracts/gate` (PASS/FLAG/VETO/NO_THESIS), `filings/models` (found/not_found) and `monitor/registry` (OK/WARN/FAIL/…) each define `STATUSES`, and the package re-exported one of them **flat**. Nothing read the wrong one, so nothing was broken — ★ but `from src.fundamental import STATUSES` while working on extraction silently returned the *gate's* tuple. Now exported as **`GATE_STATUSES`**, and `test_no_two_d01_modules_export_the_same_name_with_different_values` fails if it recurs | new — no ID |
| **10.19 — no relay prompt blocks are written** | ⚠ **expected** | `compose` is real and `ARCHETYPE_BLOCKS` selects, but the **`RLY-*` block texts do not exist** in the registry — the tests register stubs. ★ Writing them is master-prompt work (MP-12/RA-123), and **an empty registry raises at composition** rather than producing a short prompt, which is the right failure | RA-122 |
| **10.20 — `verify_claim` is handed `ours`; nothing fetches it** | ⚠ **expected** | RA-118 says *re-verify against D-02/D-07 where a counterpart exists*, and the **lookup does not exist** — the caller supplies `ours`. ⚠ **This is the load-bearing half of the relay's safety case**: `coverage` prices the report, and until something actually resolves counterparts, every claim is `unverifiable` and **every relay is INSUFFICIENT_DATA**. ★ Conservative in the safe direction, and it makes the relay useless until wired | RA-118, RA-114 |
| **10.21 — `RelayReport` does not become a `Thesis`** | ⚠ **expected, and deliberate for now** | Nothing converts an ingested relay into `CT-1.1`, so it cannot yet reach D-12's gate. ★ The conversion is where RA-114's cap and RA-115's `verdict_stability: null` must survive translation, and **B4.8's ACs do not specify it** — building it unspecified is how the cap would get lost | new — no ID |
| **10.16 — nothing polls a real source** | ⚠ **expected** | `ingest` takes `poll` as a callable and the **adapters do not exist** — no IR scraper, no filing watcher, no trade-press feed. ★ The completeness machinery, the omission logging and the four guards are all real and tested; **the file is empty until WF-7 has something to poll**, which is a D-07 feed question | RA-98, WF-7 |
| **10.17 — the source list has no published instance** | ⚠ **expected** | `CT-1.7` and `SourceList` exist; **no `srcs.v1` for semiconductors is committed anywhere.** ⚠ That artifact is the one RA-98 says gets *reviewed* — the code cannot supply it, because choosing the sources **is** the analytical act the rule isolates | RA-98 |
| **10.18 — `assert_complete` is a tautology on a file `ingest` built** | low | By construction every source yields a record or an omission, so the check can only fail on a file assembled some other way. ★ That is the intent — it is a **contract check for external files**, not a self-test — but it means the ingest path gets no coverage from it | RA-98 |
| **10.12 — `depended_classes` is a house derivation, not a spec rule** | ⚠ medium | RA-71 says *"a class it depends on"* and **no spec says how to derive it**. Today: any business falsifier ⇒ `earnings`, plus any macro class a falsifier's `observable_field` names by prefix. ★ A thesis whose real dependency is a **supplier's** earnings is not covered, and would go stale only on the clock floor | new — no ID |
| **10.13 — the sweep's findings are supplied, not detected** | ⚠ **expected** | `weekly_sweep` assembles and guarantees the report (RA-86/RA-87); **the detectors that produce `Accumulation`s do not exist** — a residual drip needs D-02's decomposition per session, `guidance_not_repeated` needs the post-event read. ★ The container is built and its invariants hold; the contents arrive with B4.7/B5 | RA-85 |
| **10.14 — `PREDICTION_MARKERS` is a wordlist against a semantic rule** | low | RA-74 forbids *an expected result*; a phrase list catches the stated forms and misses a paraphrase. ★ Mitigated structurally: `OutcomeMapping.falsifier_state` has **three** values and no *"confirms"*, so a brief cannot express a prediction through the mapping — only through prose | RA-74 |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_fundamental_b41.py` (31), `tests_src/test_fundamental_b42.py` (25), `tests_src/test_fundamental_b43.py` (24), `tests_src/test_fundamental_b44.py` (29) and `tests_src/test_fundamental_b45.py` (28) and `tests_src/test_fundamental_b46.py` (48) and `tests_src/test_fundamental_b47.py` (29) and `tests_src/test_fundamental_b48.py` (32), each docstring naming its `AC-1.n` |
| 2 | ★ **Break it and confirm red** | **(a)** In `src/fundamental/prompts/call.py`, move the `self._registry.check(...)` line to *after* the gateway call. `test_ac_1_10_prompt_drift_raises_before_any_call_is_made` must fail — **it asserts the transport was never reached, not merely that an error was raised.** **(b)** Delete the `self.log.append(_failed_run(...))` line. `test_ac_1_27a_but_the_failure_IS_recorded` must fail — that line is RA-130, and without it a flaky provider and a name nobody analysed look identical. **(c)** In `src/fundamental/claims/verify.py::x01_verify_extraction`, drop the `_assert_quote_matches_document` call. `test_ac_1_3a_x01_resolves_the_offset_before_looking_for_the_value` must fail — ★ **that one line is the difference between checking a citation and asking the model to confirm itself.** **(d)** In `src/fundamental/scorecard/models.py::Rubric.required_union`, return the *top* level's `evidence_required` instead of the union. `test_ac_1_34a_coverage_falls_when_an_extraction_fails` must fail — **that one word is the difference between a floor and a constant.** **(e)** In `src/fundamental/thesis/gate.py::evaluate`, replace `max(matches, key=…)` with `matches[0]`. `test_ac_1_6a_the_most_conservative_matching_row_wins` must fail — ★ **first-match-wins makes a stale thesis PASS, and the difference is invisible in any single case.** **(f)** In `src/fundamental/monitor/variance.py::rm1_sampling_probe`, return `not_yet_calibrated("RM-1")` instead. `test_ac_1_28a_not_measurable_is_distinct_from_not_yet_calibrated` must fail — ★★ **that swap turns an impossibility into a backlog**. **(g)** In `src/fundamental/events/router.py::_overlaps`, return `False` when `period is None`. `test_ac_1_52a_withdrawal_is_by_period_and_an_undated_item_goes_too` must fail — ★ **an undated fact would survive a restatement**, and the scorecard would keep resting on it. **(h)** In `src/fundamental/events/moves.py::review_move`, delete the `trigger.basis != BASIS_RESIDUAL` check. `test_ac_1_56_a_move_trigger_without_a_residual_raises` must fail — ★★ **that check is RA-88**, and without it every trigger measures the sector on the days the whole theme repriced. **(i)** In `src/fundamental/sector/schema.py`, drop `record_fields` from the fingerprint payload. `test_ac_1_69a_a_changed_field_set_fingerprints_differently` must fail — ★★ **that leaves the schema versioned in name only**, and RA-100 is the guard that looks like engineering. **(j)** In `src/fundamental/thesis/author.py`, delete the `sector_files=` line in the `Thesis(...)` call. `test_ac_1_71a_the_thesis_declares_the_version_it_consumed` must fail — the version stays *hashed* and stops being *readable*, which is the whole distinction RA-142 draws. **(k)** In `src/fundamental/scorecard/coverage.py::assess_confidence`, restore the `report.aggregate` attribute access. `test_ac_1_77a_the_floors_are_one_implementation_not_two` must fail — ★★ **that is RA-144**, and the alternative is two copies of INV-012/013. **(l)** In `src/fundamental/relay/queue.py::_rotation_key`, add `-entry.times_skipped` to the tuple. `test_ac_1_85_nothing_is_re_prioritised_for_having_been_skipped` must fail — ★ **it converts SEAT-1's legitimate override into a penalty, quietly** |
| 3 | The worked example (§4) reproduces | Same four parts in reverse order hash identically; `.redact()` differs and records its parent — `test_ac_1_2_the_hash_is_independent_of_part_arrival_order`, `test_ra_14_a_blind_view_is_a_new_bundle_with_a_recorded_parent` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **No.** B4.1 verifies *reproducibility*; B4.2 verifies a citation against the document it cites — which is external to the model but internal to the bundle; B4.3 and B4.4 verify *structure*. **Nothing yet checks whether a verdict was right.** ★ The first such check is **RM-1's k-run probe** (B4.5) — and even that measures *stability*, not correctness. RA-59's calibration, whose clock started at B1, is the only thing that ever will |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-fundamental-analysis.md` §4B | RA-114…RA-128, **RA-143**, **RA-144**; **CT-1.5** RelayReport; §4B.5a's decision; §11.2's amended stale row |
| `sdd/design/rel6_design/L1-fundamental-analysis.md` §10C | RA-97…RA-102, **RA-140**, **RA-141**, **RA-142**; **CT-1.6** the file, **CT-1.7** the source list |
| `sdd/design/rel6_design/L1-fundamental-analysis.md` §10A/§10B | RA-69…RA-96a, **RA-138**, **RA-139**; §10B.3's 8-K table; §10B.4's cadence table |
| `sdd/design/rel6_design/L1-fundamental-analysis.md` | **§5** the bundle (RA-1…RA-4), §6 the two call kinds (RA-5…RA-7), §7.1 (RA-11…RA-13, RA-17), **§4A.2** the eleven steps, **CT-1.2** + RA-129/RA-130, **CT-1.4**, §11.1/§11.2, RA-47…RA-54 |
| `sdd/design/rel6_design/L2-shared-infrastructure.md` | **CT-0.1**, GW-1…GW-23 — the transport this seam wraps, and **GW-9**'s `decoding` object |
| `sdd/design/rel6_design/L1-decision.md` | DN-10, DN-25, DN-31, DN-32 — what D-12 does with this |
| `sdd/design/rel6_design/L3-build-sequence.md` | **BS-11**, **BS-27**, **BS-28**, **BS-33**, **BS-34**; §3A's B4 slices |
| `sdd/design/rel6_design/L5-inherited-defects.md` **D-15** | the incident BS-34 exists to prevent |
