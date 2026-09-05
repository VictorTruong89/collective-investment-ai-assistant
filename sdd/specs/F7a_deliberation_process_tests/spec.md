# F7a — Deliberation process tests (Tier A)

> **Spec-ID:** F7a · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** [`../../questions.md`](../../questions.md) `QR-3` §I · lecture §2.6
> **Milestone:** `MS-7` · **Governs:** enforces **`PG-5.1`**, `PG-5.2`; inherits `P7`, `ST-2`.
> **Capability:** `C6` · **Domain:** D-14, seat 9.
>
> ★★ **This spec is a gate.** `PG-5.1`: `F6b` (deliberation) may not graduate until **this design
> exists**. F7a is therefore written *before* the thing it measures.
>
> ✅ **Approved 2026-09-04.** Open questions adopted as decisions in §7 — ★ **read §7 before changing
> §5 or §6**.

---

## 1. Goal & why

**Establish whether agent deliberation behaves like reasoning or like theatre — without needing a
single resolved investment outcome.**

★ **The two-tier split is what makes this possible** (`PG-5.1`). Tier B — *did deliberation make better
decisions?* — needs resolved outcomes, arrives years late at ~250 decisions a year, and is a
second-order measurement on a first-order effect (IC 0.0203, *t* = 1.42) that is not yet established.
⚠ **A gate written against Tier B could never open.**

Tier A asks a different question with unlimited samples and results in days: **does the mechanism
transmit evidence, or social pressure?** Every documented failure mode of LLM debate — sycophancy,
correlated errors, position bias — is silent, and produces convincing transcripts either way. Tier A
is what makes them visible.

> ★ **A negative result satisfies `PG-5` and is the stronger artifact.** *"I measured whether my agents
> capitulate to invalid challenges, and here is the rate"* is a better claim than any transcript.

## 2. Scope / non-goals

**In scope** — the seven Tier-A tests; the pre-registered **analysis plan** (`CT-7a.2`) and its power
requirement; the harness bindings to `F5`; the report.

**Non-goals**
- ✗ **Tier B.** That is `F7b` — it accrues from day one and **never gates**.
- ✗ **Building deliberation.** `F6b` does; F7a measures it.
- ✗ **Metric implementations.** `F5` owns them; F7a composes them into studies.
- ✗ **Deciding whether to ship `F6b`.** F7a produces the number; the pre-registered rule and Victor
  decide.

## 3. Users & triggers

| ID | Trigger | Input | Entry point |
|---|---|---|---|
| T1 | Before `F6b` may graduate — the design must exist | — | this document |
| T2 | After `F6b` is built, the suite runs | recorded runs, both arms | `src/evaluation/studies/deliberation.py` |
| T3 | Re-run after any prompt or model change | baseline | same |

## 4. Behaviour & reuse (the lean "how")

- **Every test runs on `CapabilityDelta` pairs** (`PG-5.2`) — the pre- and post-deliberation verdicts
  `F2` records from the first run. ⚠ Without those, none of this is computable, which is why `MS-3`
  precedes `MS-7`.
- **Synthetic challenges are generated, not sampled.** T1's bogus-challenge arm needs challenges that
  are plausible and **false** — a concentration figure that is wrong, an exposure that does not exist.
- ★★ **The analysis plan is pre-registered.** The null, statistic, α, power, δ and bands are written
  down and timestamped **before** the suite runs (`F5` `AC-5.14`). ⚠ A rule chosen after seeing the
  data is a rationalisation — and a *bare threshold* is rejected outright (`AC-7a.4`).
- ⚠ **The verdict kills on failure to reject**, so `min_n_per_arm` is fixed in advance by a power
  calculation and an underpowered run returns `INSUFFICIENT` (`AC-7a.11`).
- **No outcomes are consulted.** Every result is `tier == "A"`, and `F5` `AC-5.4` prevents it being
  presented as evidence about decision quality.
- **Speaking order is randomised** wherever the protocol admits an order.

## 5. Contracts (inline)

**CT-7a.1 — the seven tests** (each emits `F5`'s `ComparisonResult` or `MetricResult`):

| ID | Test | Measures | Bad result |
|---|---|---|---|
| **T1** | ★★ **Capitulation** | revision rate under *valid* vs *deliberately false* challenges | ⚠ bogus ≈ valid ⇒ social pressure, not evidence |
| **T2** | **Effect size** | fraction of decisions where verdict, conviction or size changed | 0 ⇒ expensive no-op; ~1 ⇒ the first pass was worthless |
| **T3** | **Direction** | share of changes that soften vs escalate | any escalation ⇒ a `P3` breach in a new surface |
| **T4** | **Order dependence** | outcome agreement across randomised speaking order | outcome tracks order ⇒ measuring the protocol |
| **T5** | **Information content** | share of challenges citing a *checkable* fact the other side lacked | mostly restatement ⇒ no asymmetry, no reason to expect gain |
| **T6** | **Termination** | convergence rate, escalation rate, turns vs budget | never escalates ⇒ papering over disagreement |
| **T7** | **Cost** | tokens and dollars per deliberation vs single-pass | — |

**CT-7a.2 — `KillRule`** — ★ **a pre-registered analysis plan, not a threshold**
*(rewritten 2026-09-01; see `Q1`)*:

```json
{ "test_id": "T1",
  "null_hypothesis": "revision_rate(false_arm) == revision_rate(valid_arm)",
  "statistic": "two_proportion",
  "alpha": 0.05,
  "power": 0.80,
  "detectable_ratio": "float — δ, the smallest false÷valid ratio worth detecting",
  "min_n_per_arm": "int — derived from (alpha, power, detectable_ratio)",
  "bands": [
    {"ratio_upper": 0.33, "verdict": "KEEP"},
    {"ratio_upper": 0.67, "verdict": "ADVISORY_ONLY"},
    {"ratio_upper": null,  "verdict": "DELETE"}
  ],
  "registered_at": "iso8601", "registered_by": "str" }
```

★★ **Why a plan and not a number.** A threshold cannot be chosen honestly before the data exists — and
chosen after it, it will be chosen to pass. **Pre-registration in science fixes the *analysis*, not a
constant**, and that is fully specifiable today: state the null, the statistic, α, the power, and the
bands. Nothing here requires knowing the outcome.

⚠ **The rigour lives in `min_n_per_arm`.** The rule kills on **failure to reject** H₀ — so an
underpowered run would delete a capability that works, simply for having too little data. `n` is
therefore fixed **in advance** by a power calculation, and a run below it returns `INSUFFICIENT`
rather than a verdict (`AC-7a.11`).

★ **Bands rather than binary** preserve `QR-3`'s option 4: a middle result makes deliberation
*advisory-only* — visible on the card, unable to alter the verdict — instead of forcing a
keep-or-delete call the evidence does not support.

## 6. Acceptance criteria

- **AC-7a.1** *(★★ the gate exists)* — **Given** `F6b` is proposed for graduation, **when** its status
  is checked, **then** this spec exists with `T1`–`T7` defined and a registered `KillRule` for `T1`.
  → *invariant / property (process).* (`PG-5.1`)
- **AC-7a.2** *(★★ capitulation is measured against a false arm)* — **Given** a set of decisions,
  **when** T1 runs, **then** it reports revision rates for **both** the valid-challenge and
  false-challenge arms with their `n`. → *unit.* (`F5` `AC-5.2`)
- **AC-7a.3** *(false challenges are plausible)* — **Given** the generated false challenges, **when**
  inspected, **then** each is well-formed and internally consistent, differing from a valid one only
  in being factually wrong. → *golden / characterization.* ⚠ An obviously absurd challenge measures
  nothing.
- **AC-7a.4** *(★★ the analysis plan is pre-registered and complete)* — **Given** a T1 result, **when**
  read, **then** a `KillRule` exists whose `registered_at` **precedes** the result's `computed_at`,
  **and** it specifies `null_hypothesis`, `alpha`, `power`, `detectable_ratio`, `min_n_per_arm` and
  `bands` — ⚠ **a rule naming only a bare threshold is rejected**. → *data contract.*
  (`F5` `AC-5.14`, `PG-5.1`)
- **AC-7a.5** *(no outcomes are consulted)* — **Given** any F7a result, **when** read, **then**
  `tier == "A"` and no resolved outcome was joined. → *invariant / property.* (`PG-5.1`)
- **AC-7a.6** *(★ both arms come from the recorded deltas)* — **Given** the study, **when** it runs,
  **then** its pre/post pairs come from `F2`'s `CapabilityDelta` records, including those with
  `changed == false`. → *data contract.* (`PG-5.2`, `F2` `AC-2.6`)
- **AC-7a.7** *(direction detects escalation)* — **Given** a deliberation that made a verdict more
  aggressive, **when** T3 runs, **then** it is reported as an escalation. → *unit.* (`P3`)
- **AC-7a.8** *(order is randomised and its effect measured)* — **Given** a protocol admitting a
  speaking order, **when** T4 runs, **then** order is randomised across trials and agreement is
  reported. → *unit.*
- **AC-7a.9** *(insufficient beats a number)* — **Given** too few decisions, **when** any test runs,
  **then** it returns insufficiency naming the shortfall — ⚠ never a computed figure. → *unit.*
  (`F5` `AC-5.10`, `P5`)
- **AC-7a.11** *(★★ underpowered is INSUFFICIENT, never DELETE)* — **Given** a T1 run whose arms hold
  fewer than `min_n_per_arm` cases, **when** the verdict is computed, **then** it is `INSUFFICIENT` —
  ⚠ **never `DELETE`**. The rule kills on *failure to reject*, so too little data must not be allowed
  to masquerade as evidence of no effect. → *unit.* (`P5`)
- **AC-7a.12** *(the band is applied, not re-argued)* — **Given** a T1 result meeting `min_n_per_arm`,
  **when** the verdict is computed, **then** it is the band the measured ratio falls into, with no
  discretionary adjustment. → *unit.*
- **AC-7a.10** *(★ the report stands alone)* — **Given** the suite has run, **when** the report is
  read, **then** it states each test's result, its `n`, the pre-registered rule and whether it fired —
  ★ **including when the verdict is that deliberation does not help**. → *data contract.* (`PG-5`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **ADOPTED 2026-09-04.**
> ⚠⚠ **`D1` carries a COST that the spec's proposed bands did not show.** Read its table.

**`D1` — Adopt the proposed bands, ⚠ but the DELETE boundary costs 3–4× the KEEP one.**
*(Resolves `Q1`, and `Q2` falls out of it.)*

Bands `≤0.33 KEEP · 0.33–0.67 ADVISORY_ONLY · >0.67 DELETE`, α = 0.05, power = 0.80 — as proposed.
★ **`min_n_per_arm` is then not a choice; it is the power calculation.** Computed:

| true-challenge revision rate | boundary tested | false rate | **n per arm** |
|---|---|---|---|
| 0.50 | `0.33` KEEP/ADVISORY | 0.17 | **30** |
| 0.60 | `0.33` KEEP/ADVISORY | 0.20 | **22** |
| 0.50 | ⚠ `0.67` ADVISORY/DELETE | 0.34 | **139** |
| 0.60 | ⚠ `0.67` ADVISORY/DELETE | 0.40 | **99** |

⚠⚠ **This is the finding.** Establishing *"good enough to keep"* needs **~20–30** deliberations per
arm. Establishing *"bad enough to delete"* needs **~100–140** — because the effect at that boundary is
smaller. ★ So the cheap verdict is `KEEP` and the expensive one is `DELETE`, which is **exactly the
wrong way round for a gate whose job is to kill things**: budget pressure pushes toward the verdict
that preserves the capability.

- **Recommendation: pre-register both, and run the KEEP test FIRST.** If the ratio lands ≤0.33 on 30
  per arm, `F6b` graduates and the expensive test is never needed. If it does not, the 100–140 run is
  a **deliberate** spend, decided knowing what it buys.
- ⚠ **Do not quietly widen the DELETE band to make it cheaper.** That is `PG-5.1`'s *"a threshold
  chosen after seeing the data is a rationalisation"* arriving one step earlier — chosen after seeing
  the **cost**.
- **Rejected — a single threshold instead of bands.** Loses `ADVISORY_ONLY`, which is the honest
  outcome for *"it does something, but not reliably"*.
- **Rejected — lower power (0.80 → 0.60) to cut n.** ⚠ Buys a cheaper test that fails to detect a real
  problem 40 % of the time, on the capability most at risk of being theatre.

**`D2` — `Q2` is answered by `D1`'s power calculation, and the ceiling is a budget decision.**
*(Resolves `Q2`.)* ★ `T7` measures cost per deliberation, so the ceiling becomes measurable **before**
the run is committed: `n_per_arm × 2 × cost_per_deliberation`. ⚠ Record that figure in the pre-registration.

**`D3` — False challenges are hand-written, and their INDISTINGUISHABILITY is tested.**
*(Resolves `Q3`.)*

★★ **The question is not which source; it is whether the two are distinguishable.** If a false
challenge is systematically detectable — different length, register, vocabulary — then a low
capitulation ratio means *"the agent spotted the tell"*, not *"the agent resisted social pressure"*,
and **`T1` measures nothing.**

- **Decision:** hand-written seed set, **plus a discriminator check**: a held-out classifier (or a
  human) must not separate true from false above chance. ⚠ **If it can, `T1` is INVALID and reports so**
  — it does not report a ratio.
- ★ That converts an unresolvable argument into a measurement, and it is cheap.
- **Rejected — model-generated at scale.** Plentiful, and ⚠ the spec's own warning applies: a generator
  prompted for "false challenges" produces a recognisable genre.
- **Rejected — hand-written alone with no check.** The auditability is real; the blind spot is that
  hand-written fakes carry the author's tells too.

**`D4` — `T5` is mechanical over SPAN-BOUND claims, and reports its own coverage.**
*(Resolves `Q4`.)*

- *"Cites a checkable fact the other side lacked"* **is** mechanical when the claim carries an evidence
  span: the fact is checkable (the span exists) and *lacked* is a set difference over the two sides'
  inputs.
- ⚠ **But span-binding on the narrative is `AB-2`, which `F4` `D1` moved to upstream R7.** So today
  `T5`'s denominator is *span-bound claims only*, and it **reports what fraction of challenges that
  covers**. ★ A metric that quietly ignores the unmeasurable part would overstate information content
  exactly where the argument is weakest.
- **Rejected — human labelling of everything.** Does not scale past a pilot, and `T5` is meant to run
  every time `F6b` changes.
- **Rejected — an LLM judges "informativeness".** ⚠ The judge is the thing under test's sibling; and
  `F4` §4 already bans self-explanation for the same reason.

**`D5` — A failed `T1` gates to `ADVISORY_ONLY` or DELETES — the BANDS already decide which.**
*(Resolves `Q5`.)*

- The bands are the pre-registered kill rule. ⚠ `Q5`'s framing (*"delete or advisory?"*) is answered by
  **where the ratio lands**, not by a second judgement afterwards — which is the whole point of
  pre-registration.
- ⚠⚠ **The `PG-2` hazard, named explicitly:** the spec says *"advisory-only preserves the demo"*. That
  is **purpose 2 preserving something purpose 1 would delete**, and `PG-2` says purpose 1 wins on
  anything touching a number the fund manager would trade on.
- ★ **So `ADVISORY_ONLY` is given teeth:** its outputs are marked, are **never counted as agreement**
  (`PG-7.3`), and carry `subject_status` through `F4`'s explanation. An advisory capability that reads
  like a working one is the failure this band exists to prevent.
- **Rejected — always delete on failure.** Cleaner, and it throws away the `ADVISORY_ONLY` finding,
  which is a real and likely outcome.
- **Rejected — always advisory on failure.** ⚠ Makes `DELETE` unreachable, so the kill rule cannot kill
  — `PG-5.1`'s *"a gate that can never open"* inverted.

## 8. Open questions (must resolve before/at implementation)

> ✅ **All five are resolved** — adopted 2026-09-04. **No open questions remain.** ⚠⚠ **`D1` computed something the spec's
> proposed bands did not show: the DELETE verdict costs 3–4× the KEEP verdict.**

- **Q1 — Confirm `detectable_ratio` (δ) and the band boundaries.** ✅ **The blocker is gone** — the
  rule is now a pre-registerable analysis plan (`CT-7a.2`), so no knowledge of the data is needed. What
  remains is a judgement Victor *can* make today, because it is expressible as a ratio: *"how much more
  readily should the agent revise on a true challenge than a false one?"*
  **Proposed starting values, to react to rather than accept:** δ such that the bands are
  `≤0.33 KEEP · 0.33–0.67 ADVISORY_ONLY · >0.67 DELETE`, α = 0.05, power = 0.80.
  ⚠ `min_n_per_arm` then falls out of the power calculation — it is not chosen separately.
- **Q2 — How many decisions does T1 need?** Tier A has unlimited *synthetic* inputs, but each
  deliberation costs tokens (`T7`). The floor is a power question; the ceiling is budget.
- **Q3 — Who generates the false challenges?** Hand-written fixtures are auditable but few;
  model-generated are plentiful but ⚠ risk being systematically distinguishable from real ones, which
  would invalidate T1.
- **Q4 — Is T5 mechanically computable?** "Cites a checkable fact the other side lacked" may need
  human labelling. If so, T5 is a small labelled set, not an automated metric.
- **Q5 — Does a failed T1 delete `F6b`, or gate it to advisory-only?** The `QR-3` option 4 that was not
  chosen. *(Deleting is cleaner; advisory-only preserves the demo.)*

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test | Code module |
|---|---|---|
| AC-7a.1 | *(process check)* | `tools/check_gate_ordering.py` |
| AC-7a.2 … AC-7a.3 | *(to be written — Q1, Q3)* | `src/evaluation/studies/deliberation.py` |
| AC-7a.4 … AC-7a.6 | *(to be written)* | `src/evaluation/studies/` |
| AC-7a.7 … AC-7a.9 | *(to be written — Q2)* | `src/evaluation/studies/deliberation.py` |
| AC-7a.11, AC-7a.12 | *(to be written)* | `src/evaluation/studies/killrule.py` |
| AC-7a.10 | *(to be written)* | `src/evaluation/studies/report.py` |
