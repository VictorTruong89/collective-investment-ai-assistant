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

This repo will **absorb `ai-investment-pipeline` and retire it** (vision §3). That repo carries
a large, live ID space:

```text
   P1–P7 · INV-1..9 · INV-0nn · AP-n · ST-n · CA-n · DR-n · G-n
   DE-nn · RA-nn · QA-nn · RC-nn · MT-nn · FE-nn · DN-nn · CB-nn
   BS-nn · AB-nn · QD-nn · DC-n
```

⚠ **Every one of those is reserved.** The upstream L0 §5.2 records a real defect caused by
*"two live meanings for one ID"* — `AP-n` had to be renamed out of `P1`–`P6` for exactly this.

★ **This repo therefore opens one fresh family for its own process rules: `PG-n` (Platform
Governance).** Do not invent any other new family without amending this section.

| Family | Meaning | Owned by |
|---|---|---|
| **`PG-n`** | **Platform governance** — this repo's own process and structural rules | ★ **this file** |
| **`QR-n`** | **Question register** — one ID per design question, answered or open | [`../questions.md`](../questions.md) |
| **`M<n>`** | **Build milestone** | [`../design/rel1_design/L3-build-sequence.md`](../design/rel1_design/L3-build-sequence.md) |
| **`DX-n`** | **Absorption discrepancy** — found while merging the pipeline in | `L3-build-sequence.md` §6 |
| `F<n>` | Feature spec ID | [`vision.md`](vision.md) §4 |
| everything above | inherited, reserved, unchanged | the pipeline repo, until absorption |

★ **`QR-n` records the *why*; `PG-n` and the specs record the *what*.** A `QR` entry always names where
its decision binds, and never restates the rule.

---

# 2. Platform governance rules

## ★★ PG-1 — Phase 0 gates everything

**No platform code — agent layer, explainability, evaluation harness — is written until the
inherited pipeline completes a verified end-to-end run.**

*Rationale (rel1 S1, Q4):* mirrors the fund manager's own precedent for D-10 (upstream AB-5:
*"I do not plan to implement D-10 code until the full pipeline runs stably"*). ⚠ The failure this
prevents is arriving at May 2027 with an elaborate demo built over an unproven signal — the
system's own gates currently refuse to promote its model (upstream L6 §7).

**Done when:** a full daily run completes end-to-end on real data and delivers its report,
without manual intervention.

> ⚠ **PG-1 does not block spec-writing.** Specs, design docs and this constitution are Phase-0
> work. It blocks *implementation*.

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
dual pitch degenerates into split focus — which is the stated risk of the Q2 decision and the
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
**destroys `F7`'s ability to attribute an outcome difference to deliberation.**

★ **The reversal conditions are written down** (lecture §2.8): a learned policy becomes viable only
where a fast, cheap, unconfounded reward signal exists — which is true of cost and of backtest results,
and is not true of investment return. ⚠ Any proposal to adopt one must first show which of those
conditions has changed.

> **Preparation is required even though adoption is not.** The trace (`F2`) records the state the
> policy saw, the action taken, a propensity field, and a stable id linking to the realised outcome.
> All four are near-free today and **cannot be backfilled** onto history that was never recorded.

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
