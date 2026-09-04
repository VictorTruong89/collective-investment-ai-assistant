# F4 — Explainability contract

> **Spec-ID:** F4 · **Status:** 🟡 draft · **Adopted:** —
> **Source discussion:** lecture §3 · [`../../questions.md`](../../questions.md) `QR-10` ·
> upstream `AB-1`, `AB-2`
> **Milestone:** `MS-5` · **Governs:** inherits `AP-1`, `AP-2`, `AP-3`, `P5`, `INV-014`/`ST-9`,
> upstream `RA-6`, `RA-9`, `RA-67`.
> **Capability:** `C3` · **Domain:** **D-13** `src/explain/`, seat 6.
>
> ⚠ **No code exists yet** — `src/` is empty and this spec is unapproved. *(`PG-1`, which
> formerly blocked implementation, was retired 2026-09-02; verification is now manual.)*

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
| `src/fundamental/claims/` — *"the citation spine: `Claim`, `EvidenceSpan`"* (`RA-9`, `INV-004`) | ✅ built, tested, exported | ⚠ **wire it** — `AB-2`: `Thesis.claims` is empty on every authored thesis |
| `src/fundamental/scorecard/coverage.py` | ✅ built | ⚠ **wire it** — `AB-1`: coverage is never computed, so confidence declares itself unmeasured |
| `src/decision/attribute/binding.py` — *"which gates bound, and why"* (`DN-13`, `DN-14`) | ✅ built | ★ **consume it** — D-12 already explains the verdict at gate level |
| Feature attribution, counterfactuals, calibration measurement | ✗ absent | **build** |

> ⚠ **`AB-2` is the highest value-per-unit-work item in the project.** If the model writes *"NAND
> margins expanded on HBM demand"*, **nothing currently checks it against the filing** — while a reader
> who sees a thesis pass every test will reasonably conclude its prose was verified. Only its
> falsifiers were.

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
- **AC-4.4** *(★★ claim binding runs on the narrative — closes `AB-2`)* — **Given** an authored thesis,
  **when** it is emitted, **then** every factual claim in the **judgement narrative** is bound to a
  verified span or listed in `unbound` — ⚠ `Thesis.claims` is never empty on a thesis containing
  factual claims. → *invariant / property.* (`RA-9`, `AP-2`)
- **AC-4.5** *(verification is deterministic)* — **Given** a claim and its span, **when** verified,
  **then** the check is `in`/arithmetic — ⚠ **no model is consulted**. → *unit.* (`RA-6`, `AP-5`)
- **AC-4.6** *(coverage is computed — closes `AB-1`)* — **Given** a scored thesis, **when** confidence
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
- **AC-4.11** *(stability is reported or explicitly absent)* — **Given** an `Attribution`, **when**
  read, **then** `stability` is a number or explicitly `null` — ⚠ absence is never implied agreement.
  → *data contract.* (`P5`)
- **AC-4.12** *(★ status travels with the explanation)* — **Given** an explanation of an unpromoted
  model, **when** rendered, **then** `subject_status` is stated on the artifact. → *data contract.*
  (`PG-2`)
- **AC-4.13** *(comparative explanation answers "why not that one")* — **Given** two names on one date,
  **when** compared, **then** the output names the drivers of the gap using each name's **published**
  attribution. → *unit.* (`QR-16`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **None yet.** When a question in §8 is decided, move it here with a `D<n>`, and keep the
> **options that were rejected and why** — a later reader must be able to reconstruct the
> argument without the conversation that produced it. Cite the `D<n>` from every AC it changed.

## 8. Open questions (must resolve before/at implementation)

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
| AC-4.1, AC-4.3, AC-4.11, AC-4.12 | *(to be written)* | `src/explain/models.py` |
| AC-4.2, AC-4.7 | *(to be written)* | `tools/check_import_fences.py` |
| AC-4.4 … AC-4.6 | *(to be written — blocked Q1, Q5)* | ⬆ `src/fundamental/{claims,scorecard}/` |
| AC-4.8 … AC-4.9 | *(to be written — Q4)* | `src/explain/counterfactual.py` |
| AC-4.10, AC-4.13 | *(to be written)* | `src/explain/service.py` |
