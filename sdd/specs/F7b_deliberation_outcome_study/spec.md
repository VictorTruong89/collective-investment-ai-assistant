# F7b — Deliberation outcome study (Tier B)

> **Spec-ID:** F7b · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** [`../../questions.md`](../../questions.md) `QR-3` §I
> **Milestone:** `MS-7` onward — ★ **and then for years** · **Governs:** enforces `PG-5.1`, `PG-5.2`.
> **Capability:** `C6` · **Domain:** D-14, seat 9.
>
> ★★ **This study accrues from day one and NEVER GATES.** That is not a weakness of the design; it is
> the design (`PG-5.1`).
>
> ✅ **Approved 2026-09-04.** Open questions adopted as decisions in §7 — ★ **read §7 before changing
> §5 or §6**.

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
  `decision_id` (`F2` `CT-2.7` — ★ the join this whole study rests on).
  → *data contract.* (`PG-5.2`, `F2` `CT-2.6`)
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

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **ADOPTED 2026-09-04.**
> ⚠⚠ **`D2` is the one that changes what this study can claim.** It should be read before `D1`.

**`D1` — The outcome is FORWARD RETURN at the model's own horizon, not realised P&L.**
*(Resolves `Q1`.)*

- **Decision:** forward return from the `decision_anchor`, over the horizon the ranker was fit for,
  currency-explicit (`INV-5`).
- ⚠ **Realised P&L is confounded by things deliberation did not touch**: position sizing (D-06),
  execution timing, and the manager's own overrides. A study of *deliberation* that measures P&L is
  measuring four things and attributing them to one.
- ★ Horizon comes from the **model**, not from the study — otherwise the horizon becomes a free
  parameter chosen after seeing outcomes, which is `PG-5.1`'s rationalisation failure.
- **Rejected — realised P&L.** Confounded, as above.
- **Rejected — "was the stop hit?".** A binary on a path-dependent quantity; discards magnitude, and
  the stop is `D-05`'s policy rather than a property of the recommendation.

**`D2` — ⚠⚠ Both arms are scored as PAPER outcomes, and `F7b` says so on every figure.**
*(Resolves `Q2`.)*

★★ **`Q2` names a genuine impossibility, and the honest response is a stated limit, not a clever fix.**
The `pre` verdict was **never acted on**, so its realised outcome does not exist and cannot be
recovered.

- **Decision:** score **both** arms identically as *paper* forward returns — what each arm's
  recommendation would have returned — **regardless of which was acted on.** Symmetric treatment is
  what makes the comparison valid.
- ⚠⚠ **The consequence must travel with every figure:** `F7b` measures whether deliberation improved
  **the recommendation**, ★ *not* whether it improved **the portfolio**. Those are different claims,
  and the second is the one a reader will assume. `PG-10` requires the artifact to say which it is.
- ★ `F5` `CT-5.1` already carries the machinery — the figure goes out with its `n` and an explicit
  scope, exactly as `F2` `D3` made replay's verdict carry `scope`.
- **Rejected — compare the `post` arm's realised outcome with the `pre` arm's paper outcome.**
  ⚠⚠ **Asymmetric**, and the asymmetry flatters deliberation: the acted arm carries execution and
  sizing effects the paper arm cannot. This is the most dangerous option because it looks like using
  the best available data.
- **Rejected — restrict the study to decisions where deliberation changed nothing.** Then the study
  can never observe the effect it exists to measure.
- **Rejected — model the counterfactual.** Adds an unvalidated model between the data and the claim,
  on a question already short of power.

**`D3` — Report ANNUALLY until `F5`'s floor is met, then quarterly — and always publish `n`.**
*(Resolves `Q3`.)*

- ⚠ `Q3` is right that *"reporting `INSUFFICIENT` monthly for three years is noise"*. But suppressing
  the report entirely hides the **accrual**, and at ~250 decisions a year the accrual **is** the
  information: how far off sufficiency are we, and is that distance shrinking?
- **Decision:** annual while insufficient, quarterly once `F5`'s per-metric floor (`F5` `D3`) is met.
  ★ Every report carries `n` and the floor, so *"not yet"* is a measured statement rather than a
  recurring shrug.
- **Rejected — monthly.** Noise, as `Q3` says.
- **Rejected — publish nothing until sufficient.** ⚠ Makes it impossible to notice that the study will
  **never** reach power — which, given `PG-5.1`'s arithmetic, is a live possibility and itself a finding.

**`D4` — ⛔ Tier B NEVER supersedes Tier A. A disagreement is a finding, not an override.**
*(Resolves `Q4`.)*

- ★★ **`PG-5.1` is explicit: *"Tier B accrues from day one and never gates."*** A thing that never gates
  cannot supersede a thing that does.
- ⚠ **`PG-5.1`'s reason still holds even if Tier B reaches power:** at ~250 decisions a year against an
  underlying signal at **IC 0.0203, *t* = 1.42**, a Tier-B result is *"a second-order measurement on an
  unestablished first-order one"* — and **more time does not fix it, because noise grows with the
  sample.**
- **Decision:** if Tier B reaches power **and** contradicts Tier A, that contradiction is escalated to
  Victor as a **finding requiring a decision** — with both figures, both `n`s, and both scopes. ★ It
  never silently overrides, and it is never silently discarded either.
- **Rejected — Tier B wins once powered.** ⚠ Would let a weak outcome study revoke a process result,
  reversing `PG-5.1` by accident.
- **Rejected — ignore the disagreement.** Discards the most interesting thing the study could produce.

## 8. Open questions

> ✅ **All four are resolved** — adopted 2026-09-04. **No open questions remain.**
> ⚠⚠ **`D2` changes what this study may CLAIM** — read it before `D1`. (must resolve before/at implementation)

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

## 9. Traceability (spec → test → code)

✅ **All 9 ACs green, 2026-09-09** — mutation-verified (5 mutations, all caught on the first pass).

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-7b.1 | ★ `tests/unit/test_tier_b_gaps.py::test_ac_7b_1_*` (2) | `studies/deliberation_tier_b.py::pairs_from_deltas` |
| AC-7b.2 | `::test_ac_7b_2_unchanged_pairs_are_retained_in_the_base_rate` · `tests/unit/test_deliberation.py::test_ac_7b_2_*` | `deliberation_tier_b.py::study` |
| AC-7b.3 | ★★ `::test_ac_7b_3_*` (2) | `deliberation_tier_b.py::TierBReport.to_report` · `achieved_power` · `detectable_effect_at_n` |
| AC-7b.4 | ★ `::test_ac_7b_4_an_empty_window_is_INSUFFICIENT_and_is_a_SUCCESSFUL_run` | `TierBReport.verdict` |
| AC-7b.5 | ★★ `tests/structural/test_no_tier_b_gating.py` (5) · `::test_ac_7b_5_calling_gate_is_always_an_error` | `tools/check_no_tier_b_gating.py` · `TierBCannotGate` |
| AC-7b.6 | `::test_ac_7b_6_the_tier_is_declared_B` | `TierBReport.tier` |
| AC-7b.7 | ★ `::test_ac_7b_7_*` (2) | `TierBReport.influenced_bucket` |
| AC-7b.8 | ★★ `::test_ac_7b_8_*` (3, incl. 6 forbidden phrases × 4 report shapes) | `deliberation_tier_b.py::VERDICTS` · `OVERCLAIMS` |
| AC-7b.9 | `tests/unit/test_trace.py` (outcome link, append-only + idempotent) | `orchestration/trace/outcomes.py::OutcomeStore.link` |

### ⚠⚠ What completing this spec exposed — two findings, 2026-09-09

1. **`AC-7b.5` had no check (`DX-52`) — the 5th consecutive spec naming a tool that did not exist.**
   ⚠ The AC says *"structurally, not by convention"*, and that wording is chosen: this is the rule most
   likely to erode **by good intentions**. ★★★ Once `F7b` finally has numbers they will be the most
   interesting numbers in the system — *"did deliberation make us money?"* — and reaching for them at a
   promotion decision is the natural move. ✅ Now the **11th** CI guarantee.
2. **`AC-7b.8`'s wording had no enforcement.** `CT-7b.1` is emphatic — *"`NO_DIFFERENCE_DETECTED` is
   **not** `NO_DIFFERENCE`"* — and nothing produced a verdict at all. ★★★ A null on an underpowered
   study is a statement about the **instrument**; *"no difference"* is a statement about the **world**,
   and this study is nowhere near able to make it. ✅ `VERDICTS` is a closed set and `OVERCLAIMS` is
   asserted against the rendered text of every report shape — not left to a reviewer to notice.
   ★ `AC-7b.3`'s ordering is likewise enforced on the **rendered string**: power appears before the
   result, because a reader who meets the difference first has already formed a view.
