# F4 — Explainability contract

> **Spec-ID:** F4 · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** lecture §3 · [`../../questions.md`](../../questions.md) `QR-10` ·
> upstream `AB-1`, `AB-2`
> **Milestone:** `MS-5` · **Governs:** inherits `AP-1`, `AP-2`, `AP-3`, `P5`, `INV-014`/`ST-9`,
> upstream `RA-6`, `RA-9`, `RA-67`.
> **Capability:** `C3` · **Domain:** **D-13** `src/explain/`, seat 6.
>
> ✅ **Approved 2026-09-04.** `Q1`–`Q5` adopted as `D1`–`D5` (§7) — ★ **read `D1` first: it moves two of
> this spec's own ACs out of `MS-5`.**
> ⚠⚠ **`AC-4.4` and `AC-4.6` are ⏸ BLOCKED on upstream R7** (`AB-1`/`AB-2`), which Victor deferred as
> *"needs mathematics, not plumbing"*. §1's *"wire it"* framing was wrong and is corrected below.

---

## 1. Goal & why

**Every recommendation carries a faithful account of what produced it, and what would change it.**

★ **The distinction the whole spec turns on:**

```text
   PLAUSIBLE   the explanation reads well and satisfies a human
   FAITHFUL    the explanation describes the computation that actually ran

   ⚠ THESE ARE INDEPENDENT. A plausible-but-unfaithful explanation is
     WORSE THAN NONE — it manufactures confidence while conveying nothing.
```

**Much of this is already built and simply not called.** The honest scope:

| Piece | State | F4's job |
|---|---|---|
| `src/fundamental/claims/` — *"the citation spine: `Claim`, `EvidenceSpan`"* (`RA-9`, `INV-004`) | ✅ built, tested, exported | ⏸ **⬆ upstream R7** (`D1`) — `AB-2`: `Thesis.claims: tuple = ()` on every authored thesis |
| `src/fundamental/scorecard/coverage.py` | ✅ built | ⏸ **⬆ upstream R7** (`D1`) — `AB-1`: coverage is never computed, so confidence declares itself unmeasured |
| `src/decision/attribute/binding.py` — *"which gates bound, and why"* (`DN-13`, `DN-14`) | ✅ built | ★ **consume it** — D-12 already explains the verdict at gate level |
| Feature attribution, counterfactuals, calibration measurement | ✗ absent | **build** |

> ⚠ **`AB-2` matters enormously**: if the model writes *"NAND margins expanded on HBM demand"*,
> **nothing currently checks it against the filing** — while a reader who sees a thesis pass every test
> will reasonably conclude its prose was verified. Only its falsifiers were.
>
> ✏ **Corrected 2026-09-04 (`D1`).** ⚠ This section previously called `AB-2` *"the highest
> value-per-unit-work item"* and said *"wire it"* — i.e. treated it as plumbing. **Upstream records
> Victor's decision that it is not**: *"needs mathematical consideration, logic/algorithm
> reconsideration and experiment"*, **deferred to R7**. The value is undiminished; **the cost estimate
> was wrong**, and the work is upstream's. F4 owns the contract that consumes the result.

## 2. Scope / non-goals

**In scope** — the explanation contract; per-domain **attribution obligations**; cross-view explanation
at seat 6; counterfactuals in observables; wiring `AB-1` and `AB-2`; the attribution-stability
diagnostic.

**Non-goals**
- ✗ **Computing another domain's attribution.** ★ `QR-10`: only the module that performed a computation
  can attribute it — SHAP needs the fitted model, claim-binding needs the extraction pipeline.
  **Each analytical seat attributes its own output through its own contract.**
- ✗ **Re-deriving gate binding.** `decision/attribute/binding.py` owns it.
- ✗ ⚠ **Asking a model to explain itself.** See §4 — self-reported reasoning is not evidence.
- ✗ **Measuring faithfulness.** `F5` owns deletion/insertion curves; F4 produces the artifact they test.
- ✗ **Choosing the model.** The EBM challenger is a `MS-5` experiment under seat 9, not a spec commitment.

## 3. Users & triggers

| ID | Trigger | Input | Entry point |
|---|---|---|---|
| T1 | A recommendation is assembled | both analyst views, published | `src/explain/service.py::explain` |
| T2 | The manager asks *"why this and not that?"* | two names | `src/explain/comparative.py` |
| T3 | The manager asks *"what would change this?"* | verdict | `src/explain/counterfactual.py` |
| T4 | A thesis is authored | narrative | `src/fundamental/claims/verify.py` *(wired, not new)* |

## 4. Behaviour & reuse (the lean "how")

- ★★ **Attribution lives in-domain; explanation lives at seat 6.** D-13 **composes already-published
  attributions**; it never recomputes them and never sees in-progress analysis — which is what keeps it
  on the legal side of `INV-014`/`ST-9`.
- ⚠ **Do not ask the LLM why.** Chain-of-thought is demonstrably unfaithful: models shift answers under
  biasing cues while their stated reasoning never mentions the cue. **So the LLM half is explained by
  constraint and verification, not introspection** — every factual claim binds to a span and is checked
  **deterministically** (`RA-6`: present in, or arithmetically derivable from, the cited span).
- **Counterfactuals are stated in observables**, never in feature space. *"Gross margin holds above
  42 % for two more quarters"* is monitorable; `f_gross_margin_z + 0.4σ` is not. ⚠ And a **rank**
  counterfactual is conditional on the peer set, so it is stated **as of a date and universe**.
- ★ **Attribution stability is a diagnostic, not a display concern.** If drivers churn while the
  prediction barely moves, the explanation describes noise — and that is a finding about the model.
- ⚠ **An explanation carries its subject's status.** The ranker is currently unpromoted (walk-forward
  IC 0.0203, *t* = 1.42). An explanation of it must not lend borrowed authority (`PG-2`).
- **Coverage and calibration never share a field** (`F5` `AC-5.5`).

## 5. Contracts (inline)

**CT-4.1 — `Attribution`** (a field on **each analytical domain's own output contract**, not D-13's):
```json
{ "domain": "str", "method": "str — e.g. 'treeshap', 'gate_binding', 'claim_binding'",
  "drivers": [{"name": "str — observable name, not feature id",
               "contribution": "float", "direction": "up|down"}],
  "baseline": "float | null",
  "stability": "float | null — agreement across perturbation; null if not computed",
  "subject_status": "promoted | unpromoted | experimental" }
```

**CT-4.2 — `Explanation`** (D-13's output; assembled, never recomputed):
```json
{ "subject_id": "str", "as_of": "date", "universe_id": "str",
  "attributions": ["Attribution — one per contributing seat, as published"],
  "gate_binding": "object — consumed from decision/attribute/binding.py",
  "counterfactual": "Counterfactual | null",
  "grounding": {"claims_total": "int", "claims_bound": "int", "unbound": ["str"]},
  "confidence": "object — from assess_confidence; ⚠ coverage, not calibration" }
```

**CT-4.3 — `Counterfactual`:**
```json
{ "statement": "str — in OBSERVABLES",
  "changes": [{"observable": "str", "from": "number|str", "to": "number|str"}],
  "flips_to": "str — the verdict it would produce",
  "as_of": "date", "universe_id": "str — ⚠ a rank counterfactual is peer-conditional",
  "sparsity": "int — number of changed observables" }
```

## 6. Acceptance criteria

- **AC-4.1** *(★ each seat attributes its own output)* — **Given** any analytical seat's published
  output, **when** read, **then** it carries an `Attribution` produced by that domain. → *data
  contract.* (`QR-10`)
- **AC-4.2** *(★★ D-13 never crosses the firewall)* — **Given** the source tree, **when** CI runs,
  **then** `src/explain/**` imports neither `src/fundamental/**` nor `src/quant/**` internals — only
  published contract types. → *invariant / property (structural).* (`INV-014`, `ST-9`)
- **AC-4.3** *(D-13 composes, never recomputes)* — **Given** an `Explanation`, **when** its
  attributions are compared with the domains' published ones, **then** they are identical. → *data
  contract.*
- ⏸ **AC-4.4** *(★★ claim binding runs on the narrative — closes `AB-2`)* — **⬆ BLOCKED ON UPSTREAM R7
  (`D1`).** Not `MS-5` work. — **Given** an authored thesis,
  **when** it is emitted, **then** every factual claim in the **judgement narrative** is bound to a
  verified span or listed in `unbound` — ⚠ `Thesis.claims` is never empty on a thesis containing
  factual claims. → *invariant / property.* (`RA-9`, `AP-2`)
- **AC-4.5** *(verification is deterministic)* — **Given** a claim and its span, **when** verified,
  **then** the check is `in`/arithmetic — ⚠ **no model is consulted**. → *unit.* (`RA-6`, `AP-5`)
- ⏸ **AC-4.6** *(coverage is computed — closes `AB-1`)* — **⬆ BLOCKED ON UPSTREAM R7 (`D1`).**
  ⚠⚠ **`PG-2` sign-off travels with it** (`D5`): when this lands, the change in scored names must be
  measured and put to Victor **before it ships**. Deferring a decision is fine; losing it is not. — **Given** a scored thesis, **when** confidence
  is read, **then** it is derived from measured `evidence_coverage`, not `not_measured`. → *unit.*
  ⚠ **Expect `CONFIDENCE_FLOOR` to become reachable and start firing — that is the mechanism working.**
- **AC-4.7** *(gate binding is consumed, not rebuilt)* — **Given** the source tree, **when** CI runs,
  **then** `src/explain/**` contains no gate-binding logic; it reads `decision/attribute/binding.py`.
  → *invariant / property (structural).* (`P4`)
- **AC-4.8** *(counterfactuals are observable and actionable)* — **Given** a `Counterfactual`, **when**
  read, **then** every `changes[].observable` names a monitorable quantity — ⚠ **never a raw feature
  id or a z-score**. → *data contract.*
- **AC-4.9** *(a rank counterfactual is peer-scoped)* — **Given** a counterfactual about rank, **when**
  read, **then** `as_of` and `universe_id` are present. → *data contract.*
- **AC-4.10** *(⚠ no self-explanation)* — **Given** any `Explanation`, **when** read, **then** it
  contains no model-generated account of the model's own reasoning presented as fact. → *invariant /
  property.*
- **AC-4.11** *(stability is reported or explicitly absent — `D3`)* — **Given** an `Attribution`,
  **when** read, **then** `stability` is a number or explicitly `null` — ⚠ absence is never implied
  agreement, and **never `0`**, which reads as *measured and unstable*. → *data contract.* (`P5`)
  > ★ `D3`: sampled per run, not computed for every name — which is what makes explicit absence
  > affordable rather than aspirational.
- **AC-4.14** *(★ a counterfactual is the SPARSEST flip, or an honest refusal — `D4`)* — **Given** a
  verdict and a domain's declared observable set, **when** a counterfactual is searched, **then** the
  result changes the fewest observables that flip it; **and when nothing in the set flips it**, the
  output says so explicitly rather than returning empty. → *unit.*
- **AC-4.15** *(the attribution method is always named — `D2`)* — **Given** any `Attribution`, **when**
  read, **then** `method` is non-empty. → *data contract.*
  > ★ F4 commits to **no** method: if the EBM challenger wins, attribution becomes intrinsic and only
  > the recorded name changes.
- **AC-4.12** *(★ status travels with the explanation)* — **Given** an explanation of an unpromoted
  model, **when** rendered, **then** `subject_status` is stated on the artifact. → *data contract.*
  (`PG-2`)
- **AC-4.13** *(comparative explanation answers "why not that one")* — **Given** two names on one date,
  **when** compared, **then** the output names the drivers of the gap using each name's **published**
  attribution. → *unit.* (`QR-16`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **`D1`–`D5` ADOPTED 2026-09-04.** The ACs they touch were amended in the same change.

**`D1` — ⚠⚠ `AB-1`/`AB-2` are upstream R7 work that Victor has ALREADY DEFERRED. This spec's
premise about them is wrong.** *(Resolves `Q1`.)*

★★ **Measured, and it contradicts §1 of this spec.** Upstream `L3-build-sequence.md` records:

> *"⏸ **AB-1/AB-2 postponed by decision** (confidence and claim-binding: **'needs mathematical
> consideration, logic/algorithm reconsideration and experiment'**)"*
> and, in the carry-forward table: *"**Victor deferred to R7** — **needs mathematics, not plumbing**."*

⚠ **§1 of this spec calls `AB-2` *"the highest value-per-unit-work item in the project"* and says
"⚠ **wire it**".** That framing treats it as plumbing. **Victor's own upstream decision says it is
not**, and that decision is more recent and better informed than this spec's assumption.

- **Decision: `AC-4.4` and `AC-4.6` are NOT `MS-5` work.** They are upstream R7. **F4 owns the contract
  that consumes the result** — `CT-4.2.grounding` and `CT-4.2.confidence` — and those are buildable now
  against an empty/`not_measured` input, exactly as they will behave until R7 lands.
- ★ **This is a real gain, not a retreat.** `Thesis.claims: tuple = ()` is the current reality; a
  contract that handles it *honestly today* is what makes the R7 work droppable in later.
- **Rejected — build the wiring here anyway.** ⚠ It would (a) edit inherited D-01, which `vision.md` §2
  reserves to upstream, and (b) **re-open a question Victor closed** on grounds this spec never
  addressed. If the maths is the hard part, wiring it early produces a number nobody can defend.
- **Rejected — drop `AC-4.4`/`AC-4.6` from F4.** ✗ They are the right ACs; only their *milestone* was
  wrong. Marked ⏸ **blocked on upstream R7** so the obligation survives.

**`D2` — The attribution method is a recorded FIELD, not a spec commitment.** *(Resolves `Q2`.)*

- `CT-4.1.method` already carries it (`treeshap`, `gate_binding`, `claim_binding`, `ebm_intrinsic`).
  ★ So the contract is **already indifferent** to how the EBM challenger turns out — which is why `Q2`
  can stay open without blocking anything.
- **Decision: F4 commits to no method.** It requires only that the method be **named on every
  attribution**, so a later comparison can partition by it.
- **Rejected — commit to TreeSHAP now.** ⚠ If the EBM wins, attribution becomes *intrinsic* and the
  field would be a lie inherited from a superseded choice.

**`D3` — `stability` is SAMPLED, and `null` is a first-class answer.** *(Resolves `Q3`.)*

- Perturbation re-runs cost a model evaluation each. **Decision: compute stability on a sampled subset
  per run (default: the top-ranked names plus a random tail), and write `null` — never `0`, never a
  stale value — for the rest.**
- ★ `AC-4.11` already says absence must be explicit; this makes it affordable rather than aspirational.
- **Rejected — every name every run.** ⚠ Cost scales with universe size, and the first thing dropped
  under time pressure would be the diagnostic — silently.
- **Rejected — never compute it.** ✗ *"If drivers churn while the prediction barely moves, the
  explanation describes noise"* — that is a finding about the model, and it is the reason the field
  exists.

**`D4` — Counterfactuals: exhaustive over a small DECLARED observable set.** *(Resolves `Q4`.)*

- **Decision:** each domain declares a short list of **actionable observables** (gross margin, revenue
  growth, rank, a gate input). The search is exhaustive over that list at declared step sizes, and
  returns the **sparsest** flip. ⚠ If nothing in the set flips the verdict, that is reported as
  *"no single-observable change flips this"* — **not** an empty result.
- ★ **Sparsity is the property that makes it useful.** *"Gross margin holds above 42 % for two more
  quarters"* is monitorable; a six-way simultaneous move is not, however optimal.
- **Rejected — gradient/optimisation search in feature space.** ⚠ Produces exactly what `AC-4.8`
  forbids — `f_gross_margin_z + 0.4σ` — and needs a differentiable model, which a GBDT is not.
- **Rejected — LLM-proposed counterfactuals.** ✗ Unverifiable, and §4 already bans self-explanation.

**`D5` — `Q5` is DISSOLVED by `D1`.** *(Resolves `Q5`.)*

- `Q5` asks whether `AC-4.6` materially changes existing outputs — *"once the floor fires, some names
  become `INSUFFICIENT_DATA` that previously scored"* — and rightly demands Victor's sign-off first.
- ★ **Under `D1` the floor cannot fire yet**, because `AB-1` is upstream R7 work that has not run. There
  is nothing to sign off **at `MS-5`**.
- ⚠ **The obligation does not disappear — it MOVES.** It is recorded as a **precondition on the R7
  work**: when `AB-1` is implemented upstream, the change in scored names must be measured and put to
  Victor **before it ships** (`PG-2`). ★ Deferring a decision is fine; **losing** it is not.

## 8. Open questions (must resolve before/at implementation)

> ✅ **All five are resolved** — `D1`–`D5` in §7, adopted 2026-09-04. **No open questions remain.**

- ~~**Q1**~~ → `D1` (⬆ upstream R7; F4 owns the consuming contract)
- ~~**Q2**~~ → `D2` (method is a recorded field, not a commitment)
- ~~**Q3**~~ → `D3` (stability sampled; `null` is a first-class answer)
- ~~**Q4**~~ → `D4` (exhaustive over a declared observable set; sparsest flip)
- ~~**Q5**~~ → `D5` (dissolved by `D1`; ⚠ the `PG-2` sign-off **moves to R7**, it does not vanish)

- **Q1 — ⬆ `AB-1` and `AB-2` are upstream.** `AC-4.4` and `AC-4.6` wire inherited D-01 machinery, which
  `vision.md` §2 says changes upstream until absorption. ⚠ **Are these F4's work or `MS-0`'s?**
  *Leaning: the wiring is upstream (D-01 owns it); F4 owns the contract that consumes the result.*
- **Q2 — What is the attribution method per domain?** SHAP for the GBDT is the default; ⚠ if the EBM
  challenger wins, attribution becomes intrinsic and `CT-4.1.method` changes. Deliberately left open.
- **Q3 — Is `stability` computed every run or sampled?** Perturbation re-runs are not free.
- **Q4 — How is a counterfactual searched?** Exhaustive over a small observable set, or optimisation?
  Sparsity and actionability constraints make this non-trivial.
- **Q5 — Does `AC-4.6` change existing outputs materially?** ⚠ Once the floor fires, some names become
  `INSUFFICIENT_DATA` that previously scored. **This is a `PG-2` change and needs Victor's sign-off
  before it ships**, not after.

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test | Code module |
|---|---|---|
| AC-4.1 | `tests/unit/test_explain.py::test_ac_4_1_an_explanation_without_attribution_explains_nothing` | `src/explain/models.py::Explanation` |
| AC-4.2 | `tests/structural/test_explain_firewall.py::test_ac_4_2_*` (4 groups, 3+3 parametrised) | `tools/check_import_fences.py::firewall_violations` |
| AC-4.3 | `tests/unit/test_explain.py::test_ac_4_3_attributions_are_used_exactly_as_published` | `src/explain/service.py::explain` |
| ⏸ AC-4.4 | ⬆ **upstream R7** (`D1`) | ⬆ `src/fundamental/claims/` |
| AC-4.5 | ⬆ **upstream** — deterministic verification already exists (`x01_verify_extraction`) | ⬆ `src/fundamental/claims/verify.py` |
| ⏸ AC-4.6 | ⬆ **upstream R7** (`D1`) ⚠ **`PG-2` sign-off attached** (`D5`) | ⬆ `src/fundamental/scorecard/coverage.py` |
| AC-4.7 | `tests/structural/test_explain_firewall.py::test_ac_4_7_*` (2) | `tools/check_import_fences.py::gate_binding_violations` |
| AC-4.8 | `tests/unit/test_explain.py::test_ac_4_8_every_change_names_an_observable_not_a_feature_id` | `src/explain/counterfactual.py` |
| AC-4.9 | `::test_ac_4_9_*` (2) | `src/explain/models.py::Counterfactual` |
| AC-4.10 | `::test_ac_4_10_*` (3, incl. 5 parametrised keys) | `src/explain/service.py::_reject_self_report` |
| AC-4.11 | `::test_ac_4_11_*` (3) | `src/explain/models.py::Attribution.stability` |
| AC-4.12 | `::test_ac_4_12_*` (2) | `src/explain/models.py::Explanation.subject_status` |
| AC-4.13 | `::test_ac_4_13_*` (3) | `src/explain/comparative.py::compare` |
| AC-4.14 | `::test_ac_4_14_*` (4) | `src/explain/counterfactual.py::search` |
| AC-4.15 | `::test_ac_4_15_*` (2) | `src/explain/models.py::Attribution.method` |

✅ **13 of 15 ACs green, 2026-09-04** — 16 mutations, all caught (one mis-designed mutation was
re-run properly rather than counted).

⏸ **`AC-4.4` and `AC-4.6` are ⬆ upstream R7 by `D1`**, and `AC-4.5`'s deterministic verification
already exists upstream. ⚠ **They are not "not done" — they are not this repo's.** The `PG-2` sign-off
`D5` attaches to `AC-4.6` is recorded in the **upstream** R7 row, because that is where it will be read.
