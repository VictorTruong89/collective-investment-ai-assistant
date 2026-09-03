# F7b — Deliberation outcome study (Tier B)

> **Spec-ID:** F7b · **Status:** 🟡 draft · **Adopted:** —
> **Source discussion:** [`../../questions.md`](../../questions.md) `QR-3` §I
> **Milestone:** `MS-7` onward — ★ **and then for years** · **Governs:** enforces `PG-5.1`, `PG-5.2`.
> **Capability:** `C6` · **Domain:** D-14, seat 9.
>
> ★★ **This study accrues from day one and NEVER GATES.** That is not a weakness of the design; it is
> the design (`PG-5.1`).
>
> ⚠ **No code exists yet** — `src/` is empty and this spec is unapproved. *(`PG-1`, which
> formerly blocked implementation, was retired 2026-09-02; verification is now manual.)*

---

## 1. Goal & why

**Answer, eventually, whether deliberation produced better decisions — and report honestly that it
cannot answer yet.**

★ **Why this is a separate spec from `F7a`, and why it is toothless by construction.** Tier B needs
resolved investment outcomes, and the arithmetic is unkind:

```text
   ~250 decisions per year
   × the subset deliberation actually CHANGED  (F7a's T2 measures this)
   ÷ noise from an underlying signal at IC 0.0203, t = 1.42
   ──────────────────────────────────────────────────────────
   ⚠ a SECOND-order measurement on a FIRST-order effect that is
     not yet established. More time does not fix it — the noise
     grows with the sample.
```

**A gate written against this could never open.** `QR-3` therefore put the gate on Tier A and left
Tier B to accrue. F7b exists so that the data is *collected correctly from the first run*, and so that
in three or five years the question is answerable rather than merely unanswered.

> ★ **Its most valuable output for most of its life is `INSUFFICIENT` with an honest power statement.**
> A study that says *"I cannot yet distinguish this"* and shows why is a result. One that reports a
> number at n = 40 is not.

## 2. Scope / non-goals

**In scope** — the outcome join; the paired comparison over `CapabilityDelta` arms; power reporting;
the accrual record that makes a future answer possible.

**Non-goals**
- ✗ **Gating anything.** ⚠ Structurally, not by convention — `AC-7b.5`.
- ✗ **Tier-A questions.** `F7a` owns process behaviour.
- ✗ **Collecting outcomes.** `F2` `CT-2.6` owns the join; F7b reads it.
- ✗ **Metric implementations.** `F5` owns calibration, Brier and the rest.
- ✗ **Deciding what an outcome *is*.** See `Q1` — that is an investment judgement.

## 3. Users & triggers

| ID | Trigger | Input | Entry point |
|---|---|---|---|
| T1 | An outcome resolves | `decision_id`, realised outcome | `F2` `trace/outcomes.py::link` |
| T2 | Periodic accrual report | date range | `src/evaluation/studies/deliberation_outcome.py` |
| T3 | Someone asks *"has it helped yet?"* | — | same — ★ usually answers `INSUFFICIENT` |

## 4. Behaviour & reuse (the lean "how")

- ★★ **The comparison is paired, and both arms come from `PG-5.2`.** Every deliberation recorded a
  `pre_verdict` and a `post_verdict`; the study compares the realised outcome against **what would have
  happened under the pre-deliberation verdict**. ⚠ **This is only possible because the counterfactual
  arm was logged from the first run** — it cannot be reconstructed later.
- **Only decisions where deliberation *changed* something carry signal**, but ⚠ the unchanged ones are
  retained: they set the base rate and their exclusion would bias the comparison.
- ★ **Power is reported before the result, every time.** The report leads with achieved *n* and the
  detectable effect at that *n*, so a reader cannot mistake a null for a negative.
- **Bucketed separately where influence occurred** (`PG-7.2`) — decisions where one seat configured
  another are a distinct population and are reported as such.
- **Never gates.** No promotion, graduation or deployment decision reads F7b's verdict (`AC-7b.5`).

## 5. Contracts (inline)

**CT-7b.1 — `OutcomeStudyResult`** (extends `F5`'s `MetricResult`):
```json
{ "window": {"from": "date", "to": "date"},
  "n_changed": "int — decisions deliberation altered",
  "n_unchanged": "int — retained for the base rate",
  "outcome_metric": "str — see Q1",
  "arm_pre": "float | null", "arm_post": "float | null",
  "difference": "float | null", "ci": ["float", "float"] ,
  "achieved_power": "float",
  "detectable_effect_at_n": "float — ★ the honest headline",
  "verdict": "INSUFFICIENT | NO_DIFFERENCE_DETECTED | IMPROVED | DEGRADED",
  "influenced_bucket": "bool — PG-7.2" }
```
⚠ `verdict == "NO_DIFFERENCE_DETECTED"` is **not** `"NO_DIFFERENCE"`. The wording is load-bearing.

## 6. Acceptance criteria

- **AC-7b.1** *(★ the paired arms come from recorded deltas)* — **Given** the study, **when** it runs,
  **then** each pair is a `CapabilityDelta`'s `pre`/`post`, joined to a realised outcome by
  `decision_id`. → *data contract.* (`PG-5.2`, `F2` `CT-2.6`)
- **AC-7b.2** *(unchanged decisions are retained)* — **Given** deliberations that changed nothing,
  **when** the study runs, **then** they appear in `n_unchanged` and are not silently dropped.
  → *unit.*
- **AC-7b.3** *(★★ power precedes the result)* — **Given** any `OutcomeStudyResult`, **when** rendered,
  **then** `achieved_power` and `detectable_effect_at_n` appear **before** any difference. → *data
  contract.*
- **AC-7b.4** *(★ insufficient is the default, not an error)* — **Given** a window with too few
  resolved paired outcomes, **when** the study runs, **then** `verdict == "INSUFFICIENT"` with the
  shortfall named — ⚠ **and this is a successful run**. → *unit.* (`P5`, `F5` `AC-5.10`)
- **AC-7b.5** *(★★ nothing gates on it)* — **Given** the source tree, **when** CI runs, **then** no
  promotion, graduation or deployment path reads an `OutcomeStudyResult`. → *invariant / property
  (structural).* (`PG-5.1`)
- **AC-7b.6** *(tier is declared)* — **Given** any result, **when** read, **then** `tier == "B"`, and
  `F5` `AC-5.4` prevents it being presented as a Tier-A claim or the reverse. → *data contract.*
- **AC-7b.7** *(influenced decisions are a separate bucket)* — **Given** decisions where one seat
  configured another, **when** the study runs, **then** they are reported separately and never pooled
  with independent ones. → *data contract.* (`PG-7.2`)
- **AC-7b.8** *(⚠ wording cannot overclaim)* — **Given** a null result, **when** rendered, **then** it
  reads `NO_DIFFERENCE_DETECTED` — ⚠ never "no difference", "no effect", or "deliberation does not
  help". → *unit.*
- **AC-7b.9** *(accrual is continuous and idempotent)* — **Given** outcomes arriving over months,
  **when** each is linked, **then** the record grows append-only and re-linking the same outcome is a
  no-op. → *invariant / property.*

## 7. Open questions

- **Q1 — ⚠ What is "the outcome"?** Forward return at the horizon? Realised P&L? Whether the stop was
  hit? Whether the thesis was falsified? **This is an investment judgement, not an engineering one, and
  it determines what the study can ever conclude.** Blocks `CT-7b.1.outcome_metric`.
- **Q2 — Counterfactual outcome for the `pre` arm.** The realised outcome is known for the action
  *taken*; the pre-deliberation verdict was **not acted on**. ⚠ Comparing them requires simulating what
  the un-deliberated verdict would have produced — which reintroduces backtest assumptions.
  ★ **This may be the hardest problem in the spec and it deserves a decision before any code.**
- **Q3 — Minimum window before the first report.** Reporting `INSUFFICIENT` monthly for three years is
  honest but noisy. Annual?
- **Q4 — Does `F7b` ever supersede `F7a`?** If Tier B eventually reaches power and disagrees with Tier
  A, which governs? *Leaning: Tier B informs, Tier A still gates — `PG-5.1` is unconditional.*

## 8. Traceability

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test | Code module |
|---|---|---|
| AC-7b.1, AC-7b.2, AC-7b.7 | *(to be written — blocked Q1, Q2)* | `src/evaluation/studies/deliberation_outcome.py` |
| AC-7b.3, AC-7b.4, AC-7b.8 | *(to be written)* | `src/evaluation/studies/report.py` |
| AC-7b.5 | *(to be written)* | `tools/check_no_tier_b_gating.py` |
| AC-7b.6 | *(to be written)* | `src/evaluation/metrics/models.py` |
| AC-7b.9 | *(to be written)* | `src/orchestration/trace/outcomes.py` |
