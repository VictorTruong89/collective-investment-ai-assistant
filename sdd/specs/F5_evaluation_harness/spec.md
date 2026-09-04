# F5 — Evaluation harness

> **Spec-ID:** F5 · **Status:** 🟡 draft *(has ACs; not yet approved)* · **Adopted:** —
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §B.4 · lecture §3.6 ·
> [`../../questions.md`](../../questions.md) `QR-13`, `QR-19`
> **Milestone:** `MS-4` — [`../../design/rel1_design/L3-build-sequence.md`](../../design/rel1_design/L3-build-sequence.md)
> **Governs:** `constitution.md` — enforces **`PG-4`**, **`PG-5`/`PG-5.1`**; inherits `P5`, `ST-2`, `P7`.
> **Capability:** `C6` — ★ **without it, `C1`–`C5` are demonstrations rather than results.**
> **Domain:** D-14 `src/evaluation/`, seat 9.
>
> ⚠ **No code exists yet** — `src/` is empty and this spec is unapproved. *(`PG-1`, which
> formerly blocked implementation, was retired 2026-09-02; verification is now manual.)*

---

## 1. Goal & why

**One harness that measures whether anything in this system actually works — built once, shared by
both portfolio lanes (`PG-4`).**

★ **This is the spec that makes the project's central claim checkable.** `vision.md` §1.1 promises a
system that *"can explain and defend every recommendation — and measure whether any of it helps."*
Everything else produces the recommendations and the explanations; F5 produces the evidence.

**Why it is spec-governed rather than research-exempt** (`QR-13`): D-14 inherits D-10's *structural*
rule — imports anything, imported by nothing (`ST-2`) — but **not** its spec exemption. The exemption
protects exploration; this is not exploration. It is an **instrument other decisions depend on**:
`F7a`'s output gates `F6b`, and its calibration numbers back the portfolio thesis.

> ⚠ **A measurement instrument nobody verified is how you get confidently wrong numbers** — and under
> `PG-4` an error here is wrong in *both* lanes, silently.

**What it must not duplicate.** `src/quant/metrics/` already computes `ic.py` and `breadth.py`, and the
IC standard error is `QR-5`'s upstream change to `src/quant/gates/metric_gate.py`. ⚠ **F5 consumes
those; it does not re-implement them.** A second IC implementation that disagrees with the first is
precisely the failure this spec exists to prevent.

## 2. Scope / non-goals

**In scope**
- **Golden sets** — known-correct fixtures with their provenance.
- **Grounding metrics** — citation rate, unbound-claim count, span precision.
- **Calibration** — reliability curve, ECE, Brier and its decomposition.
- **Faithfulness** — deletion / insertion curves, attribution stability.
- **Regression** — a suite that reds when a *prompt* changes behaviour.
- The **Tier-A / Tier-B split** (`PG-5.1`) as a structural property of the harness.
- ★ **Sample size and selection count on every published figure** (`QR-19`'s lesson, generalised).

**Non-goals (this spec)**
- ✗ **Re-implementing IC, breadth, or the IC standard error.** Consumed from `src/quant/metrics/` and
  `metric_gate.py`. The `QR-5`/`QR-19` change is upstream work (`MS-0.2`).
- ✗ **The deliberation study itself** — that is `F7a` (Tier A) and `F7b` (Tier B). F5 supplies the
  machinery they run on.
- ✗ **Deciding promotion.** `metric_gate.py` gates models upstream; F5 measures and reports.
- ✗ **Producing explanations.** `F4` produces them; F5 tests whether they are faithful.
- ✗ **Collecting outcomes.** `F2`'s `CT-2.6` links `decision_id` to a realised outcome; F5 reads that
  join.
- ✗ **One-off exploratory studies** — see `Q1`; the metric/study boundary is the open question `QR-13`
  flagged.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | CI, every build | golden set | `src/evaluation/regression/run.py` |
| T2 | After a run, on its outputs | `run_id` | `src/evaluation/metrics/grounding.py` |
| T3 | Periodically, over resolved outcomes | date range | `src/evaluation/metrics/calibration.py` |
| T4 | A Tier-A study asks for a comparison | two arms of `CapabilityDelta` | `src/evaluation/studies/compare.py` |
| T5 | A prompt or model id changes | previous baseline | `src/evaluation/regression/run.py` |

## 4. Behaviour & reuse (the lean "how")

- **Consume, never re-derive.** IC and breadth come from `src/quant/metrics/`; outcomes come from
  `F2`'s join; provenance comes from `F1`. F5 owns only what nothing else computes.
- **Tier A needs no outcomes; Tier B does** (`PG-5.1`). ⚠ The harness keeps them **structurally
  separate**, so a Tier-A result can never be presented as evidence about decision quality.
- ★ **Every published figure carries `n` and, where a model or variant was selected from candidates,
  the selection count.** `QR-19` established that a significance figure with an unstated selection
  count is not interpretable; F5 generalises that to every metric it emits.
- **Coverage is not calibration.** ⚠ Upstream `AB-1` defines `confidence := evidence_coverage` — a
  measure of *how much the system looked at*, not *how often it is right*. F5 computes both and **they
  never share a field name**.
- **A metric is checked against a known answer.** Every metric implementation has a fixture whose
  correct value is derived independently — ★ this is the "who checks the checker" obligation that
  `QR-13` turned into a spec.
- **The harness imports domains; nothing imports the harness** (`ST-2`, inherited from D-10's shape).
- **Fail loud on insufficiency.** ⚠ A metric asked for on too small a sample returns an explicit
  insufficiency, never a number (`P5`).

## 5. Contracts (inline)

**CT-5.1 — `MetricResult`** (every figure the harness emits):
```json
{ "metric": "str — e.g. 'grounding_rate', 'ece', 'brier'",
  "value": "float | null — null when insufficient",
  "n": "int — ★ sample size, always present",
  "selection_count": "int | null — candidates the subject was chosen from (QR-19)",
  "tier": "A | B — PG-5.1",
  "insufficient_reason": "str | null",
  "computed_at": "iso8601",
  "inputs_ref": "str — golden set id or run_id range" }
```
Rules: `value` and `insufficient_reason` are mutually exclusive and one is always present.
⚠ `n` is **never optional** — a figure without its sample size is not publishable.

**CT-5.2 — `GoldenCase`:**
```json
{ "case_id": "str", "kind": "extraction | thesis | ranking",
  "input_ref": "str — the fixture", "expected": "object",
  "source": "str — how the expected value was established",
  "established_at": "iso8601", "established_by": "str" }
```
⚠ `source` is required: a golden value whose derivation is unrecorded cannot be re-checked, and will
eventually be trusted for the wrong reason.

**CT-5.3 — `CalibrationResult`** (extends `CT-5.1`):
```json
{ "bins": [{"lower": "float", "upper": "float",
            "n": "int", "mean_confidence": "float", "observed_rate": "float"}],
  "ece": "float", "brier": "float",
  "brier_decomposition": {"reliability": "float", "resolution": "float",
                          "uncertainty": "float"} }
```

**CT-5.4 — `ComparisonResult`** (Tier-A arms, consumed by `F7a`):
```json
{ "arm_a": "str", "arm_b": "str", "metric": "str",
  "value_a": "float", "value_b": "float", "n_a": "int", "n_b": "int",
  "pre_registered_rule": "str — ★ stated BEFORE the run (PG-5.1)",
  "verdict": "PASS | FAIL | INSUFFICIENT" }
```

## 6. Acceptance criteria (Given / When / Then → test tier)

- **AC-5.1** *(★ every metric is checked against a known answer)* — **Given** any metric
  implementation, **when** run on its fixture, **then** it returns the independently-derived expected
  value within tolerance. → *golden / characterization, one per metric.* (`QR-13`)
- **AC-5.2** *(★ `n` is never absent)* — **Given** any `MetricResult`, **when** emitted, **then** `n`
  is present and > 0, or `value` is null with an `insufficient_reason`. → *data contract.*
- **AC-5.3** *(selection count travels with the figure)* — **Given** a subject chosen from `k > 1`
  candidates, **when** a metric about it is emitted, **then** `selection_count == k`. → *data
  contract.* (`QR-19`)
- **AC-5.4** *(★★ tiers do not mix)* — **Given** a Tier-A result, **when** any report is assembled,
  **then** it is never presented as evidence about decision quality; a Tier-B claim requires
  `tier == "B"` inputs. → *invariant / property.* (`PG-5.1`)
- **AC-5.5** *(coverage ≠ calibration)* — **Given** both are computed, **when** either is emitted,
  **then** they carry distinct metric names and neither is derived from the other. → *data contract.*
  (upstream `AB-1`)
- **AC-5.6** *(grounding rate is real)* — **Given** a thesis with bound and unbound claims, **when**
  grounding is computed, **then** the rate equals verified-claims ÷ factual-claims, and
  `unbound_claim_count` is reported alongside. → *unit.* (`AP-2`)
- **AC-5.7** *(a prompt change reds the suite)* — **Given** a green regression baseline, **when** a
  prompt's text changes such that behaviour changes on the golden set, **then** the suite fails and
  names the diverging cases. → *integration.*
- **AC-5.8** *(calibration joins on `decision_id`)* — **Given** resolved outcomes linked by `F2`
  `CT-2.6`, **when** calibration is computed, **then** every bin's `observed_rate` derives from that
  join and no outcome is counted twice. → *data contract.*
- **AC-5.9** *(deletion curve detects a useless attribution)* — **Given** an attribution that is pure
  noise, **when** the deletion curve is computed, **then** removing top-`k` attributed features
  degrades performance no faster than removing random features, and the result is reported as
  unfaithful. → *unit.*
- **AC-5.10** *(insufficient is loud)* — **Given** a metric requested on a sample below its stated
  minimum, **when** computed, **then** `value` is null and `insufficient_reason` names the shortfall —
  ⚠ **never a number computed on too little data**. → *unit.* (`P5`)
- **AC-5.11** *(no re-implementation of upstream metrics)* — **Given** the source tree, **when** CI
  runs, **then** `src/evaluation/**` contains no independent computation of IC, breadth or the IC
  standard error; it imports them. → *invariant / property (structural).* (`P4`)
- **AC-5.12** *(one-way import)* — **Given** the source tree, **when** CI runs, **then** no module
  outside `src/evaluation/**` imports from it. → *invariant / property (structural).* (`ST-2`)
- **AC-5.13** *(experimental provenance propagates)* — **Given** inputs produced by a variant with
  `experimental == true`, **when** a metric is emitted, **then** the result is labelled experimental
  and cannot be reported as production. → *data contract.* (`F1` `AC-1.11`, `PG-2`)
- **AC-5.14** *(pre-registration is recorded, not retrofitted)* — **Given** a `ComparisonResult`,
  **when** it is written, **then** `pre_registered_rule` is non-empty and its recorded timestamp
  precedes the comparison's `computed_at`. → *data contract.* (`PG-5.1`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **None yet.** When a question in §8 is decided, move it here with a `D<n>`, and keep the
> **options that were rejected and why** — a later reader must be able to reconstruct the
> argument without the conversation that produced it. Cite the `D<n>` from every AC it changed.

## 8. Open questions (must resolve before/at implementation)

- **Q1 — ⚠ Where is the metric / study boundary?** `QR-13` flagged it and deferred it here. Metric
  implementations are spec-governed; **one-off exploratory studies arguably stay `P7`-exempt like
  D-10**. The boundary needs a rule, not a case-by-case judgement — otherwise everything drifts into
  the exempt side. *Proposal to react to: anything another decision consumes is a metric; anything
  read once by a human is a study.*
- **Q2 — Who establishes a golden value, and how is it maintained?** `CT-5.2` requires a `source`, but
  for a thesis fixture the "correct" answer is a judgement. ⚠ A golden set the system's own output
  seeded is circular. Blocks `AC-5.1` for the `thesis` kind.
- **Q3 — Minimum sample sizes.** `AC-5.10` needs a stated minimum per metric. ECE with 5 bins on 40
  cases is not meaningful; where is the floor, and is it per-metric or global?
- **Q4 — Storage and retention.** `MetricResult` history is what makes a regression *trend* visible
  rather than a point check. Same tiering question as `F2`'s `Q2`, and it should get the same answer.
- **Q5 — Does F5 run in CI, or after a run, or both?** `T1` and `T2` imply both, on different cadences.
  ⚠ CI cannot call an LLM cheaply; the golden-set regression may need recorded responses from `F2`
  rather than live calls.

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-5.1 | *(to be written — blocked Q2 for `thesis`)* | `src/evaluation/metrics/**` |
| AC-5.2 | *(to be written)* | `src/evaluation/metrics/models.py` |
| AC-5.3 | *(to be written)* | `src/evaluation/metrics/models.py` |
| AC-5.4 | *(to be written)* | `src/evaluation/metrics/models.py` |
| AC-5.5 | *(to be written)* | `src/evaluation/metrics/calibration.py` |
| AC-5.6 | *(to be written)* | `src/evaluation/metrics/grounding.py` |
| AC-5.7 | *(to be written — blocked Q5)* | `src/evaluation/regression/run.py` |
| AC-5.8 | *(to be written)* | `src/evaluation/metrics/calibration.py` |
| AC-5.9 | *(to be written)* | `src/evaluation/metrics/faithfulness.py` |
| AC-5.10 | *(to be written — blocked Q3)* | `src/evaluation/metrics/models.py` |
| AC-5.11 | *(to be written)* | `tools/check_no_metric_duplication.py` |
| AC-5.12 | *(to be written)* | `tools/check_oneway_imports.py` |
| AC-5.13 | *(to be written)* | `src/evaluation/metrics/models.py` |
| AC-5.14 | *(to be written)* | `src/evaluation/studies/compare.py` |
