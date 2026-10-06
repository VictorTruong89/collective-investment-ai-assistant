# Constitution — Collective Investment AI Assistant

> **Status:** Living. Adopted 2026-08-28 (`../design/rel1_brainstorm.md`, rel1 S1).
> **Purpose:** the non-negotiable, project-wide rules every spec and every code change must
> respect. A spec may *add* constraints; it may not *contradict* this file. If a change needs
> to break a rule here, **amend this file first**, in its own change, with the rationale.
> **Scope — this file is *how* we build.** *What* is being built is
> [`vision.md`](vision.md). Neither overrides the other.
> **Audience:** the AI agent implementing code, and any reviewer.

---

# 1. ⚠⚠ ID families — read before inventing an ID

This repo will **absorb `ai-investment-pipeline` and retire it** (vision §3). That repo carries a
large, live ID space, and **every family below is reserved.** ⚠ The upstream L0 §5.2 records a real
defect caused by *"two live meanings for one ID"* — `AP-n` had to be renamed out of `P1`–`P6` for
exactly this.

> ⚠ **Corrected 2026-09-02.** The earlier version of this list named 20 families and **missed eleven**
> that are in live use upstream — `OR`, `RM`, `RK`, `RP`, `PS`, `GW`, `XP`, `QQ`, `CN`, `J`/`E`/`S`.
> `OR-n` alone has **76 definitions and ~600 citations.** The list below was rebuilt by extraction, not
> recollection, and each family is assigned to the document that actually *defines* it (by density).
>
> ⚠⚠ **The rebuild immediately caught a live collision of our own making.** This repo's build
> milestones were `M0`…`M9`, and §1.1 shows `M-n` is already the **mandate** family in `L0`. Two
> meanings for one letter is the exact defect this section exists to prevent, so the milestones were
> **renamed `M<n>` → `MS-n`** the same day, across 118 references. ★ *That is the section doing its
> job on its first real use.*

## 1.1 Inherited families — reserved, do not reuse

### Cross-cutting rules

| Family | Meaning | Defined in |
|---|---|---|
| **`P1`–`P7`** | **Constitution principles** — spec-before-code · AI only for qualitative work · ★ verdicts gate, never upgrade · reuse before rebuild · ★ fail loud, never silent · self-contained delivery · research is exempt | upstream `constitution.md` |
| **`INV-1`…`INV-9`** | **Constitution invariants** — no look-ahead · determinism · feature ranges · train/inference parity · currency explicit · ★ one actionable rec per day · positions round-trip · model tiering · prompt alignment | upstream `constitution.md` |
| ⚠ **`INV-0nn`** | **A DIFFERENT family sharing the prefix** — L0's system invariants (`INV-004` claim binding, `INV-005/006` manifest immutability, `INV-012/013` confidence, ★ `INV-014` the analyst firewall, `INV-017` survivorship, `INV-021`/`INV-026` risk reports-never-blocks) | `L0-system-vision` |
| **`AP-1`…`AP-7`** | **Agent principles** — transparency over confidence · cited claims only · adversarial thinking · graceful degradation · ★ `AP-5` deterministic when possible · versioned and reproducible | `L0-system-vision` §5.2 |
| **`M-n`** | **Mandate rules** — the investment posture (no penny stocks, no derivatives, concentration policy, registered-account constraints, base currency) | `L0-system-vision` |
| **`G-n`** | **Governance gates** — tier promotion, spec graduation | `L0-system-vision` §17 |
| **`DC-n`** | **Discipline Card rules** — what the card may and may not originate | `L0` §5.1a · `L1-reporting` |

### Structural rules (`L4-coding-standards`)

| Family | Meaning |
|---|---|
| **`ST-n`** | ★ **Horizontal import fences** *between* domains — `ST-2` nothing imports experiments · `ST-5` only the gateway calls an LLM · `ST-8` a stale glob fails the gate OPEN · `ST-9` the analyst firewall · `ST-10` neither analyst imports decision |
| **`CA-n`** | ★ **Vertical Clean-Architecture rules** *within* a module — `models.py` pure · `service.py` no SDK · `ports.py` typing only · `CA-9` the composition root |
| **`CN-n`** | Coding conventions — naming, structure, style |
| **`EH-n`** | Error-handling rules — e.g. `EH-14`, *only orchestration retries* |

### Per-domain rules — one family per domain

| Family | Domain | Defined in | Scale |
|---|---|---|---|
| **`RA-nn`** | D-01 Fundamental Analysis | `L1-fundamental-analysis` | **293 defs** — the largest |
| **`QA-nn`** | D-03 Quantitative Analysis | `L1-quantitative-analysis` | 263 |
| **`DE-nn`** | D-07 Data Engine | `L1-data-engine` | 131 |
| **`RC-nn`** | D-11 Recording | `L1-recording` | 110 |
| **`OR-nn`** | D-08 Orchestration | `L1-orchestration` | 76 ⚠ *was missing* |
| **`PS-nn`** | D-06 Portfolio Strategy | `L1-portfolio-strategy` | 69 ⚠ *was missing* |
| **`MT-nn`** | D-04 Model Training | `L1-model-training` | 67 |
| **`RP-nn`** | D-09 Reporting | `L1-reporting` | 64 ⚠ *was missing* |
| **`RK-nn`** | D-05 Risk Management | `L1-risk-management` | 62 ⚠ *was missing* |
| **`FE-nn`** | D-02 Feature Engineering | `L1-feature-engineering` | 54 |
| **`DN-nn`** | D-12 Decision | `L1-decision` | 51 |
| **`GW-nn`** | D-00 the LLM gateway | `L2-shared-infrastructure` | 37 ⚠ *was missing* |
| **`RM-nn`** | D-01 relay / monitoring | `L1-fundamental-analysis` | 22 ⚠ *was missing* |
| **`CB-nn`** | signal combination | `L2-signal-combination` | 52 |
| **`XP-nn`** | D-10 Experiments | `L1-experiments-intent` | 78 ⚠ *was missing* |

### Prompt-internal families (`L1-fundamental-analysis-master-prompt`)

⚠ **Short prefixes, high collision risk.** `J-nn` judgement steps · `E-nn` event/macro blocks ·
`S-n` prompt sections · `P-n` *(a third meaning of `P`)*.

### Process & record families

| Family | Meaning | Defined in |
|---|---|---|
| **`BS-nn`** | Build-sequence rules | `L3-build-sequence` |
| **`AB-nn`** | ★ **As-built remaining** — open defects and postponed decisions | `L6-as-built-remaining` |
| **`QD-nn`** | Open data questions | `L1-data-engine` |
| **`QQ-nn`** | Open quant questions | `L1-quantitative-analysis` |
| **`DR-n`** | Blueprint-tier rules | `blueprints/README.md` |

### ⚠⚠ `AC-F<n>.<k>` — this repo's spec ACs carry their spec id (`DX-44`, 2026-09-09)

**A bare `AC-9.6` had two live meanings**, and both were about the discipline card:

| | means |
|---|---|
| `F9` (this repo) | *the card states which source produced its thesis* |
| `D-09` (upstream reporting) | *every card field names a producing domain* |

★★★ **It bit within minutes of being noticed.** The first `F9` `AC-9.6` implementation set
`source="F9"` on a new card field — which D-09's `AC-9.6` **fails**, since it asserts every field's
source starts with `D-`. ⚠ Two rules, one id, the same artifact, opposite requirements.

★ **The rule:** where this repo's `F<n>` spec number collides with an upstream domain's, its ACs are
written **`AC-F<n>.<k>`**. ✅ **`F9` and `F1` are renamed.** `F6b`, `F7a`, `F7b` need no change —
their letters are already unique, which is the argument for the convention generally.

### ⚠⚠ Why `F1` and `F9` were renamed and the other five were NOT — a deliberate stopping point

Measured 2026-09-09 by upstream citation count:

| | `AC-1` | `AC-9` | `AC-8` | `AC-2` | `AC-5` | `AC-3` | `AC-4` |
|---|---|---|---|---|---|---|---|
| upstream citations | **362** | 71 | 120 | 80 | 67 | 60 | 41 |
| own AC range | `.1`–`.15` | `.1`–`.10` | `.1`–`.20` | `.1`–`.16` | `.1`–`.18` | `.1`–`.12` | `.1`–`.13` |
| renamed | ✅ | ✅ | ✗ | ✗ | ✗ | ✗ | ✗ |

★★★ **The criterion is not citation volume — it is whether the two ranges OVERLAP.**
`F1` and `F9` are the two whose own numbering sits **inside** a live upstream domain's (D-01's
`AC-1.1`–`AC-1.99`, D-09's `AC-9.1`–`AC-9.34`), so a bare id is genuinely ambiguous *and both
meanings are in daily use*. ⚠ `AC-9.6` proved that is not theoretical: two rules, one id, the same
artifact, **opposite requirements**.

⚠⚠ **The remaining five are left deliberately, and the reason is cost against a smaller risk.**
Renaming them means ~370 further surgical citations, and every one must be classified by hand
because a global substitution would corrupt upstream references. ★ The measured hazard is lower:
their upstream counterparts are cited mostly in `sdd/design/rel6_*` and `tests_src/`, which are
**inherited territory this repo does not edit** (vision §2), so the two vocabularies rarely meet in
one file.

★★ **A worked example of why the classification cannot be automated.** `src/models/governance/
parity.py` reads *"(F1 AC-1.15, INV-6)"* about a feature-coverage floor — which is **neither** this
repo's `F1` nor its `AC-1.15` (`InvalidKey` on a malformed name). A naive rename would have
corrupted it. **It was left untouched.** ⚠ Any future extension of this convention must classify
every occurrence individually, exactly as `F1` and `F9` were.

⬜ `DX-44` remains **partially open** for `AC-2`/`AC-3`/`AC-4`/`AC-5`/`AC-8`.

### Spec-internal (every spec, both repos)

| Family | Meaning |
|---|---|
| **`AC-<n>.<k>`** | Acceptance criterion — the unit of done |
| ★ **`AC-F<n>.<k>`** | ⚠ **This repo's own spec ACs, where a bare number would collide** — see below |
| **`CT-<n>.<k>`** | Contract — a concrete data/API shape |
| **`D-nn`** | Domain identifier (`D-00`…`D-14`) |


### ⚠⚠ Absorbed at `MS-8` — found by `tools/check_id_families.py`, 2026-09-04

★★ **`MS-8` merged two ID spaces into one tree, and this section was ~50 % incomplete.**
**39 families were in active use and named nowhere here** — after §1 had *already* been corrected on
2026-09-02 for missing eleven. ⚠ A registry that reads as authoritative while being half the story is
how `M-n` (mandate) and `M<n>` (milestone) came to collide in the first place.

★ It is now **enforced**: `tools/check_id_families.py` fails when a family with ≥20 uses is not
declared below. ⚠ The check asks only *"is it written down?"* — meaning stays a human's job.

| Family | Uses | Defined in | Meaning |
|---|---|---|---|
| **`SEAT-n`** | 216 | `L0-system-vision` | ⚠ Upstream's **five**-seat desk model. **NOT this repo's nine seats** — see the warning below |
| **`FR-n`** | 168 | *(cross-cutting)* | Functional requirement |
| **`X-nn`** | 108 | `L1-fundamental-analysis-master-prompt` | Extraction steps (`X-01` …) |
| **`V-nn`** | 106 | `L1-fundamental-analysis-event-and-macro` | Event/macro validation rules |
| **`CF-n`** | 98 | `L2-shared-infrastructure` | Config rules — `CF-4` immutability |
| **`PD-n`** | 78 | `L2-signal-combination` | Prediction/combination rules |
| **`FX-n`** | 78 | `L1-recording` | FX conversion rules — `FX-3` *no rate, no number* |
| **`MP-nn`** | 76 | `L1-experiments-intent` | Master-prompt rules |
| **`K-nn`** | 75 | `L1-data-engine` | Known-answer / calibration cases |
| **`H-n`** | 73 | `L1-recording` · `L5-inherited-defects` | Hypotheses about the data — `H-0` *the broker is BMO* |
| **`MO-n`** | 68 | `L2-shared-money` | Money rules — `MO-1` a bare value is not monetary |
| **`T-n`** | 68 | `L0-system-vision` | Trigger/entry-point ids |
| **`SC-n`** | 64 | `L2-shared-infrastructure` | Secrets/credential rules |
| **`PRC-n`** | 64 | *(cross-cutting)* | Pricing rules |
| **`WF-n`** | 55 | `L1-fundamental-analysis` | Workflow steps |
| **`Q-n`** | 50 | `L0-system-vision` | ⚠ Open questions — **a fourth meaning of `Q`**; see below |
| **`QP`/`QS`/`QK`/`QO`/`QC`/`QB`/`QX`/`QI`-nn** | 20-44 | per-domain L1s · `QI` = `L2-shared-infrastructure` | Domain open-question families (portfolio, strategy, knowledge, ops, recording, combination, experiments, shared infrastructure — ✏ `QI` declared 2026-10-05 when the go-live notes took it past 20 uses) |
| **`DQ-nn`** | 39 | `L0-system-vision` | Data-quality questions |
| **`VS-n`** | 33 | `L0-system-vision` §4.2 | ★ **Valuation split** — D-02 arithmetic vs D-01 judgement (`VS-1` `fv_model` ≠ `fv_analyst` · `VS-4` judgement-parameterised arithmetic is D-01's). *Declared 2026-09-13 when `F10` took its use count past the threshold* |
| **`IM-n`** | 38 | `L3-build-sequence` | Implementation-method rules |
| **`LG-n`** | 37 | `L2-shared-infrastructure` | Logging rules |
| **`SI-n`** | 36 | `L2-shared-infrastructure` | Shared-infrastructure rules — ★ `SI-1` is `DX-3`'s vacuous fence |
| **`CI`/`VR`/`OB`/`ANO`/`VOL`/`OQ`/`DF`/`PE`/`BT`/`CAL`/`PA`/`DV`-n** | 20-30 | various | Smaller per-domain families; ⚠ reserved, do not reuse |

> ⚠⚠ **`SEAT-n` is the sharpest entry on this page.** It is upstream's **five-seat** model.
> `vision.md` §3 defines **nine** seats and `CLAUDE.md` says: *"Never carry a seat number between the
> two repos."* ★ Now that both live in **one tree**, that warning is easier to violate and harder to
> notice — an absorbed test asserted upstream's seat vocabulary against this repo's vision and had to
> be corrected (`DX-10`).

> ⚠ **`Q` now has four live meanings**: `Q-n` (upstream open questions), `QR-n` (this repo's register),
> the per-domain `QQ`/`QD`/`QP`/`QS`/`QK`/`QO`/`QC`/`QB`/`QX` families, and a bare `Qn` inside a spec's
> own §8. ★ They are distinguishable only by prefix length and context — **do not add a fifth.**

## 1.2 This repo's own families

★ **Against that space, this repo opens only fresh, non-colliding families.** Do not invent any other
without amending this section — and ⚠ **check §1.1 first**, because the space is fuller than it looks.

| Family | Meaning | Owned by |
|---|---|---|
| **`PG-n`** | **Platform governance** — this repo's own process and structural rules. ⚠ `PG-1` is **retired**; the ID is not reused | ★ **this file** |
| **`QR-n`** | **Question register** — one ID per design question, answered or open | [`../questions.md`](../questions.md) |
| **`MS-n`** | **Build milestone** ⚠ *renamed from `M<n>` on 2026-09-02 — it collided with inherited `M-n` mandate rules* | [`../design/rel1_design/L3-build-sequence.md`](../design/rel1_design/L3-build-sequence.md) |
| **`DX-n`** | **Absorption discrepancy** — found while merging the pipeline in | `L3-build-sequence.md` §6 |
| `F<n>` | Feature spec ID | [`vision.md`](vision.md) §4 |
| everything above | inherited, reserved, unchanged | the pipeline repo, until absorption |

★ **`QR-n` records the *why*; `PG-n` and the specs record the *what*.** A `QR` entry always names where
its decision binds, and never restates the rule.

---

# 2. Platform governance rules

## ⊘ ~~PG-1~~ — RETIRED 2026-09-02

> ~~`MS-0` gates everything~~ — **struck.** ⚠ **The ID is retired and never reused** (§1).

**What it said.** No platform code — agent layer, explainability, evaluation harness — until the
inherited pipeline completed a verified end-to-end run.

**Why it was cancelled** *(Victor, 2026-09-02)*: **verification moves to the fund manager**, performed
manually and in depth against real run outcomes. A rule that blocked **137 acceptance criteria across
11 specs** on a condition that was never defined operationally — and that the running pipeline had
arguably already met — cost more than it bought.

### ⚠ What the review found before it was struck

`PG-1` carried **three different bars that did not agree**:

| | Bar | Status |
|---|---|---|
| the rule body | *"a **verified** end-to-end run"* | undefined — "verified" was never operationalised |
| the done-when | *"completes… and delivers its report, unattended"* | ★ **arguably already met** — two runs on 2026-08-28 were `SUCCESS`, 13/13 jobs, with a rendered report |
| the rationale | *"not… a demo built over an **unproven signal**"* | ⚠ **a different question entirely** — about the model, not the run |

★ **And it blocked `F5`, the evaluation harness — the very instrument that would answer the concern
the rationale was built on.** A gate that blocks its own key is not doing its job.

### ⚠⚠ The gap this leaves — unresolved, and named on purpose

Manual verification answers the *operational* bar. It does **not** answer the third one. **No rule now
prevents a performance figure or an actionable card being presented from an unpromoted model** (the
ranker sits at walk-forward IC 0.0203, *t* = 1.42, refused by its own gate).

`PG-2` does not cover it — that is about conflicts between the two purposes. `PG-5` does not cover it —
that is about capabilities *this platform adds*, not the inherited signal's status.

> ✅ **Replaced by [`PG-10`](#-pg-10--a-claim-carries-its-subjects-status), adopted 2026-09-02.**
> `PG-1` blocked 137 acceptance criteria to guard this concern; `PG-10` guards it by requiring one
> sentence on the output — and blocks nothing.

## ★ PG-2 — Purpose 1 wins on numbers

Where the investment purpose and the portfolio purpose conflict **on anything that touches a
number the fund manager would trade on**, the investment purpose wins. A feature that improves
the demo and degrades the analysis is a **defect**, not a trade-off.

## ★★ PG-3 — An agent must earn its place

> **An agent is justified only where the task requires open-ended, tool-using interaction with
> an unbounded external world. Where the inputs are known and the computation is definable,
> write the code.**

*This is `AP-5` applied to agency itself.* ⚠ The failure it guards against is **deliberation
theatre**: wrapping arithmetic that `src/risk/` already computes in a typed CHALLENGE message
and an LLM-authored rebuttal, which lengthens the transcript without improving the position.

| Justified | ✗ Not justified |
|---|---|
| corporate-action resolution (the answer is on the internet, not in the data) | risk arithmetic, exposure, concentration |
| filing interpretation, claim extraction | position sizing from a stop |
| news materiality | verdict combination (see `PG-6`) |

## ★★ PG-4 — One evaluation harness, built once, shared

Both portfolio lanes (vision §1.1) depend on measurement. **The evaluation harness (F5) is built
once, early, and serves both.** ⚠ If each lane grows its own ad-hoc measurement code, the
dual pitch degenerates into split focus — which is the stated risk of the `QR-2` decision and the
thing this rule exists to prevent.

## ★ PG-5 — A demonstration must be measured, not merely shown

Any capability presented as a portfolio result must carry a measurement of whether it helped.

> ★★ **A negative result, published, satisfies this rule and is worth more than a polished
> transcript.** It demonstrates the evaluation instinct that is the scarce skill.

### PG-5.1 — Two tiers, and only one of them gates

*(Added 2026-08-30, rel1 S3 — `QR-3`. "Measured" was ambiguous, and the ambiguity mattered.)*

| Tier | Question | Needs outcomes | Power |
|---|---|---|---|
| ★ **A — process** | *Does it behave like reasoning, or like theatre?* | ✗ no | ★ adequate, unlimited samples |
| **B — outcome** | *Did it make better decisions?* | yes, resolved | ⚠ weak; years to accrue |

**A capability graduates when its Tier-A design exists. Tier B accrues from day one and never gates.**

⚠ **Why Tier B may not gate:** at ~250 decisions a year, against an underlying signal at IC 0.0203
(*t* = 1.42), a Tier-B result is a second-order measurement on an unestablished first-order one. **More
time does not fix it — noise grows with the sample.** A gate written against Tier B is not rigour; it
is a gate that can never open, and it would cancel a capability by procedural accident rather than by
decision.

★ **Pre-register the kill rule.** Before running a Tier-A test, state the result that would cause the
capability to be deleted. A threshold chosen after seeing the data is a rationalisation, not a
measurement.

### ★★ PG-5.2 — Log both arms, from the first run

**When a capability alters an output, the pre-capability value is persisted alongside the
post-capability value.**

The pre-deliberation verdict, the pre-influence routing choice, the pre-explanation decision — each is
already in memory at the moment the capability runs. Writing it costs one field.

⚠ **Omitting it destroys the counterfactual arm permanently**, and Tier B becomes impossible *even
once the samples accumulate*. This is the same shape as `PG-9`'s propensity requirement: **near-free
today, impossible to backfill.** It binds whether or not the Tier-B study has been scheduled.

## ✗ PG-6 — D-12 stays deterministic

The verdict algebra is a **bounded meet-semilattice**: *"verdicts gate, never upgrade"* is a
**structural** guarantee, not a runtime check. It may not be replaced by a learned or
LLM-assisted combiner.

★ An `AgentPort` may be implemented on the decision node to preserve the option, but any
agent-assisted combination is **advisory alongside**, never replacing. ⚠ An unfalsifiable
combination rule at the point where output becomes action is the most expensive mistake
available in this design.

*(✅ **Confirmed 2026-08-30** for this release — rel1 S3, `QR-6`. No longer provisional. Revisiting it
is a constitution amendment under §5 item 4, not a design choice.)*

## ★ PG-7 — Cross-configuration is recorded, and never called agreement

If `INV-014b` is adopted (agents may request configuration variants from each other through the
orchestrator), then:

1. every cross-configuration request is **recorded on the nomination**; and
2. any decision where one seat configured the other is **bucketed separately in evaluation**; and
3. ⚠ **the combined verdict may never claim "two independent views agree"** when one configured
   the other.

*Rationale:* choosing a model horizon **is** an analytical choice. The firewall's value is that
concurrence between independent views is *informative*; cross-configuration silently converts
concurrence into an echo.

## PG-8 — The tree is a superset, always

Every inherited domain keeps its upstream path (`src/fundamental/`, `src/quant/`, …) so the
eventual absorption is a **merge, not a restructuring** (vision §3). ⚠ A new module that would
force an upstream import to be rewritten at absorption time is a defect.

## ★ PG-9 — The control plane stays deterministic

**Routing, scheduling and orchestration decisions are made by pure functions, are replayable, and
record the reason for every choice.** A learned or LLM-driven control policy is out of scope.

*Rationale:* three independent grounds. **(a)** *"Why did this run use the one-week model?"* must have
an answer better than *"the model chose it"* — otherwise the explainability claim in `vision.md` §1.1
is false. **(b)** `AP-5` — routing on a definable quantity is a computation, not a judgement.
**(c)** ⚠ A stochastic control plane makes two runs on identical data take different paths, which
**destroys `F7a`/`F7b`'s ability to attribute an outcome difference to deliberation.**

★ **The reversal conditions are written down** (lecture §2.8): a learned policy becomes viable only
where a fast, cheap, unconfounded reward signal exists — which is true of cost and of backtest results,
and is not true of investment return. ⚠ Any proposal to adopt one must first show which of those
conditions has changed.

> **Preparation is required even though adoption is not.** The trace (`F2`) records the state the
> policy saw, the action taken, a propensity field, and a stable id linking to the realised outcome.
> All four are near-free today and **cannot be backfilled** onto history that was never recorded.

## ★ PG-10 — A claim carries its subject's status

**No output may present a recommendation as *actionable*, or publish a *performance figure*, unless
the model behind it has passed its own promotion gates — or the output states plainly that it has
not.**

*Adopted 2026-09-02 (`QR-4`).* It replaces the half of the retired `PG-1` that was never about
blocking code.

**Why it is needed once `PG-1` is gone.** Manual verification answers whether the pipeline *ran*. It
does not answer whether the *signal* is established — and those are different questions. ⚠ The risk is
live, not hypothetical: the ranker sits at **walk-forward IC 0.0203, *t* = 1.42**, refused by its own
`ic_significance` gate.

**Scope** — the discipline card, any report, the demo, and the `MS-9` write-up.

> ★★ **It blocks nothing in the build.** It constrains only what may be *claimed*, which is where the
> risk actually was. `PG-1` blocked 137 acceptance criteria to guard this; `PG-10` guards it by
> requiring one sentence on the output.

★ **The same shape as `QR-21`'s coverage statement: declare the limit on the artifact, rather than
withholding the artifact.** A stated caveat is worth more than a blocked page, because a blocked page
teaches nobody what the limitation was.

---

# 3. Inherited principles that still bind

Until absorption, the pipeline's constitution and L0 govern its own domains. These carry over
into platform work and are **restated by ID only** — never re-worded, because a second wording
drifts:

| ID | Where it lives | Why it matters here |
|---|---|---|
| **`AP-5`** | upstream L0 §5.2 | deterministic code where computation applies — the parent of `PG-3` |
| **`P5`** | upstream constitution | fail loud, never silent — a degraded input raises, never emits a plausible default |
| **`AP-1`, `AP-2`, `AP-3`** | upstream L0 §5.2 | transparency, cited claims, adversarial thinking — ★ these are *already* explainability rules; F4 completes them |
| **`INV-014` / `ST-9`** | upstream L0 · L4 | the analyst firewall — D-01 ↛ D-03. Shapes where D-13 may sit (vision §4.1) |
| **`ST-2`** | upstream L4 | the one-way import rule — D-14 inherits it |
| **`ST-5`** | upstream L4 | only the LLM gateway calls an LLM |
| **`P7`** | upstream constitution | research is spec-exempt |

⚠ **Amending any inherited rule is an upstream change**, made in the pipeline repo, not here.

---

# 4. Testing tiers

Every acceptance criterion maps to exactly one:

| Tier | Enforces | Example |
|---|---|---|
| Data contract | a declared shape | message schema, trace record |
| Invariant / property | a rule that holds for **all** inputs | no agent bypasses the registry |
| Golden / characterization | unintended output change | a frozen explanation on a fixture |
| API contract | request/response + status | the `AgentPort` surface |
| **Metric gate** | ★ statistical regression | calibration ≥ threshold, citation rate |
| Unit | one function | variant resolution |
| Integration | multi-component flow | a full graph run with trace |

⚠ **Getting the tier wrong is the most common quiet failure.** An invariant AC given a single
example test *looks* green and proves almost nothing.

**Rule:** a task is "done" only when its acceptance criterion has a passing test in the right tier.

---

# 5. Change process

1. New capability ⇒ add `specs/F<n>_<slug>/spec.md` with acceptance criteria **first**.
2. Add its globs to `ownership.yaml` **in the same change** — a spec with no globs is unenforced.
3. Relying on inherited behaviour ⇒ **characterization test** to freeze it before building near it.
4. Breaking a `PG-n` rule ⇒ amend this file first, in its own change, with rationale.
5. Research/experiment ⇒ no spec required (`P7`); promoting its output to production ⇒ spec required.

## 5.1 When the spec is silent

| Situation | Move |
|---|---|
| No AC covers the change | ★ **Amend the spec first.** A real deliverable, not overhead |
| Building next to inherited untested code | **Characterization test first** — freeze what it does before touching it |
| The choice is genuinely the fund manager's | **Stop and ask** |
| — | ✗ **Improvise, then write a test that agrees with the improvisation** |

⚠ **The illegal move is dangerous precisely because it produces green tests.** The agent wrote
both the code and the test, so of course they agree.

---

# 6. Traceability

Every test docstring names the `AC-<n>.<k>` it satisfies. Every spec keeps its traceability
table current: acceptance criterion → test → code module. **An AC with no row is not done,
however green the test is** — because nobody can find it later.
