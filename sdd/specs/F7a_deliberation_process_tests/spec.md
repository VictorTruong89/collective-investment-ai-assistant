# F7a — Deliberation process tests (Tier A)

> **Spec-ID:** F7a · **Status:** 🟡 draft · **Adopted:** —
> **Source discussion:** [`../../questions.md`](../../questions.md) `QR-3` §I · lecture §2.6
> **Milestone:** `M7` · **Governs:** enforces **`PG-5.1`**, `PG-5.2`; inherits `P7`, `ST-2`.
> **Capability:** `C6` · **Domain:** D-14, seat 9.
>
> ★★ **This spec is a gate.** `PG-5.1`: `F6b` (deliberation) may not graduate until **this design
> exists**. F7a is therefore written *before* the thing it measures.
>
> ⚠ **`PG-1` blocks implementation.** Spec only.

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
  `F2` records from the first run. ⚠ Without those, none of this is computable, which is why `M3`
  precedes `M7`.
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

## 7. Open questions

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

## 8. Traceability

⚠ **Empty by design** — `PG-1`, and `F6b` does not yet exist to measure.

| AC | Test | Code module |
|---|---|---|
| AC-7a.1 | *(process check)* | `tools/check_gate_ordering.py` |
| AC-7a.2 … AC-7a.3 | *(to be written — Q1, Q3)* | `src/evaluation/studies/deliberation.py` |
| AC-7a.4 … AC-7a.6 | *(to be written)* | `src/evaluation/studies/` |
| AC-7a.7 … AC-7a.9 | *(to be written — Q2)* | `src/evaluation/studies/deliberation.py` |
| AC-7a.11, AC-7a.12 | *(to be written)* | `src/evaluation/studies/killrule.py` |
| AC-7a.10 | *(to be written)* | `src/evaluation/studies/report.py` |
