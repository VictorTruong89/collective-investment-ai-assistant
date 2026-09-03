# F2 — Execution trace & replay

> **Spec-ID:** F2 · **Status:** 🟡 draft *(has ACs; not yet approved)* · **Adopted:** —
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §D.1 · lecture §2.7 ·
> [`../../questions.md`](../../questions.md) `QR-14`
> **Milestone:** `MS-3` — [`../../design/rel1_design/L3-build-sequence.md`](../../design/rel1_design/L3-build-sequence.md)
> **Governs:** `constitution.md` — enforces **`PG-5.2`**, **`PG-9`**, `PG-7`; inherits `P5`, `AP-6`,
> and upstream **`OR-13` / `INV-005` / `INV-006`** (manifest immutability).
> **Capability:** `C7` observability — the substrate `C2`, `C4`, `C5`, `C6` and `C8` all stand on.
>
> ⚠ **No code exists yet** — `src/` is empty and this spec is unapproved. *(`PG-1`, which
> formerly blocked implementation, was retired 2026-09-02; verification is now manual.)*

---

## 1. Goal & why

**Record enough about a run that it can be replayed, and that every decision inside it can be
explained, without re-running anything.**

★ **This spec's most important sentence is about what it does NOT build.** The upstream pipeline
already records runs: `RunManifest` (`src/orchestration/contracts/manifest.py`) carries `run_id`,
`git_sha`, `dirty`, `config_hash`, `data_as_of`, `decision_anchor`, **`seed`**, `inputs`, `budgets`,
`preconditions` and `stubs`; `RunOutcome` carries per-job status, attempts, elapsed time and error
codes; and `manifest_store.py` already enforces **append-only immutability** (`OR-13`), raising
`ManifestImmutableError` because *"editing it would let a run's recorded inputs be adjusted to match
its outputs."*

**That layer is done and F2 does not touch it.** What is missing is everything *below* job
granularity:

| Question a reader will ask | Answerable today? |
|---|---|
| Which jobs ran, how long, did they fail? | ✅ `RunOutcome` |
| What was the code, config and data as-of? | ✅ `RunManifest` |
| ⚠ **What did the LLM actually receive and return?** | ✗ |
| ⚠ **Why did routing pick this variant?** | ✗ |
| ⚠ **What would the verdict have been without this capability?** | ✗ |
| ⚠ **Can this run be re-executed and checked?** | ✗ |

> ★★ **F2 extends the existing run record downward from job granularity to decision granularity, and
> adds replay.** It is one new sub-package, `src/orchestration/trace/`, joined to the existing record
> by `run_id`.

**Why it comes before every capability:** `PG-5.2` and `PG-9` require fields that are **near-free
today and impossible to backfill**. A capability shipped before the recorder exists destroys its own
counterfactual arm permanently.

## 2. Scope / non-goals

**In scope**
- Step-level records beneath each existing `JobRun`, joined by `run_id` + `job_id`.
- **Every external call** — LLM and tool — with request *and* response. The replay substrate.
- **`PG-9` decision records**: state seen, action, reason, candidate set, propensity.
- **`PG-5.2` capability deltas**: the pre-capability value beside the post.
- `F1` `Provenance` attached to every resolution.
- A **stable decision id** that survives to the outcome store as a join key.
- The **replay engine** and its divergence report.
- ⚠ The **CI grep** confining any orchestration framework to `src/orchestration/graph/` (`QR-14`).

**Non-goals (this spec)**
- ✗ **Re-implementing `RunManifest`, `RunOutcome`, `manifest_store` or the locks.** They exist, they
  are immutable, and duplicating them would create a second run-level record that can disagree with
  the first (`P4`; ⚠ and `PG-8` — the paths must survive absorption unchanged).
- ✗ **Bit-for-bit determinism of LLM output.** See `Q3` — replay substitutes recorded responses; it
  does not assert a model would answer identically twice.
- ✗ **Deciding anything.** F2 records; `F6a` routes, `D-12` decides.
- ✗ **The decision journal** (D-11) — a human-facing record of what the fund manager did. F2 records
  what the *system* did. They join on `decision_id` and are not the same artifact.
- ✗ **Metrics over traces** — that is `F5`. F2 produces the substrate; it computes nothing.
- ✗ **A dashboard.** Reading traces is `MS-9` polish.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | Any job step begins/ends during a run | ambient run context | `src/orchestration/trace/record.py::step` |
| T2 | Any external call is made (LLM, tool, HTTP) | request payload | `trace/record.py::external_call` |
| T3 | A control-plane decision is taken (`F6a`) | state, chosen action, candidate set | `trace/record.py::decision` |
| T4 | A capability alters an output | pre value, post value | `trace/record.py::delta` |
| T5 | A past run is replayed | `run_id` | `trace/replay.py::replay` |
| T6 | An outcome resolves, weeks later | `decision_id`, realised outcome | `trace/outcomes.py::link` |

## 4. Behaviour & reuse (the lean "how")

- **Join, do not duplicate.** Every F2 record carries the existing `run_id`. F2 writes no second
  run-level record and never rewrites a manifest.
- **Immutability is inherited, not reinvented.** Trace records are append-only under the same rule as
  `OR-13`. ⚠ A trace that can be edited is not evidence.
- **Record at the boundary, not inside the logic.** External calls are captured where the process
  leaves the system — so coverage is a property of the boundary, not of each caller remembering.
- **A decision record is written by the routing function itself**, carrying the reason it already
  returns (`F6a`'s `Routing(variant, reason, influenced_by)`), so `PG-7`'s cross-configuration flag
  and `PG-9`'s reason are the *same* field, recorded once.
- **`propensity` is `1.0` while the control plane is deterministic** (`PG-9`). The field exists now so
  off-policy evaluation is possible later; ⚠ it is not a placeholder to be added when needed, because
  by then the history is gone.
- **Fail loud on incompleteness.** A run whose trace is partial is marked `INCOMPLETE`; ⚠ a partial
  trace that looks complete is worse than none (`P5`).
- **Replay substitutes, never re-calls.** The engine re-executes the graph with every external call
  served from the recording. A replay that reaches the network has failed.

## 5. Contracts (inline)

**CT-2.1 — `StepRecord`** (one per step, beneath an existing `JobRun`):
```json
{ "run_id": "str — FK to the existing RunManifest",
  "job_id": "str — FK to the existing JobRun",
  "step_id": "str — unique within the run",
  "parent_step_id": "str | null",
  "node": "str — graph node / function name",
  "seat": "int — 1..9",
  "started_at": "iso8601", "ended_at": "iso8601",
  "provenance": "Provenance | null — F1 CT-1.4, when the step resolved a variant",
  "status": "SUCCESS | FAILED | INCOMPLETE" }
```

**CT-2.2 — `ExternalCall`** (⭐ the replay substrate):
```json
{ "run_id": "str", "step_id": "str", "call_id": "str",
  "kind": "llm | tool | http",
  "request": "object — the full payload as sent, after redaction (AC-2.9)",
  "response": "object — the full payload as received",
  "model_id": "str | null — exact id, never an alias",
  "prompt_version": "str | null",
  "tokens": {"input": "int", "output": "int"}, "cost_usd": "float | null",
  "latency_ms": "int", "error": "str | null" }
```
Rules: `request` **and** `response` are both required — a request without its response cannot be
replayed. `model_id` records what actually served the call, so provider aliasing is visible.

**CT-2.3 — `DecisionRecord`** (⭐ `PG-9`):
```json
{ "run_id": "str", "step_id": "str",
  "decision_id": "str — ★ stable, and the join key to the outcome store",
  "state": "object — the inputs the policy actually saw",
  "candidates": ["str"], "action": "str — the variant chosen",
  "reason": "str — the predicate that fired, e.g. 'realised_vol_60d > 0.45'",
  "propensity": "float — probability the policy assigned; 1.0 while deterministic",
  "influenced_by": "str | null — PG-7; the seat whose output shaped this choice" }
```

**CT-2.4 — `CapabilityDelta`** (⭐ `PG-5.2`):
```json
{ "run_id": "str", "decision_id": "str",
  "capability": "str — e.g. 'deliberation', 'config_influence', 'explanation'",
  "pre":  "object — the value BEFORE the capability ran",
  "post": "object — the value AFTER",
  "changed": "bool" }
```
Rules: written **whenever the capability runs**, including when `changed` is `false` — ⚠ the
no-change cases are half the comparison and dropping them biases the study.

**CT-2.5 — `ReplayReport`:**
```json
{ "run_id": "str", "verdict": "IDENTICAL | DIVERGED | UNREPLAYABLE",
  "first_divergence": {"step_id": "str", "field": "str",
                       "recorded": "object", "replayed": "object"} }
```
- `UNREPLAYABLE` when the trace is `INCOMPLETE` or an external call lacks its response.

**CT-2.6 — outcome link** (written weeks later, `T6`): `{ "decision_id": "str", "resolved_at":
"iso8601", "outcome": "object" }` — append-only; ★ this is what makes a Tier-B study (`F7b`) possible
years after the decision.

## 6. Acceptance criteria (Given / When / Then → test tier)

- **AC-2.1** *(★ extends, never duplicates)* — **Given** a completed run, **when** its trace is read,
  **then** every record carries the `run_id` of the existing `RunManifest`, and **no second
  run-level record exists**. → *data contract.* (`P4`, `PG-8`)
- **AC-2.2** *(every external call is captured, both halves)* — **Given** a run that makes LLM or tool
  calls, **when** the trace is read, **then** each call has a record with a non-null `request` **and**
  `response`, or an explicit `error`. → *invariant / property over call sites.*
- **AC-2.3** *(★★ replay reproduces)* — **Given** a completed run's trace, **when** it is replayed,
  **then** the run's deterministic outputs are reproduced and the verdict is `IDENTICAL` — **and no
  network call is made**. → *integration.*
- **AC-2.4** *(divergence is located, not just detected)* — **Given** a trace whose code has since
  changed, **when** replayed, **then** the verdict is `DIVERGED` and `first_divergence` names the
  **first** diverging step and field. → *integration.*
- **AC-2.5** *(★★ `PG-9` completeness)* — **Given** any control-plane decision, **when** its record is
  read, **then** `state`, `candidates`, `action`, `reason` and `propensity` are all present and
  non-null. → *data contract.* (`PG-9`)
- **AC-2.6** *(★★ `PG-5.2` both arms)* — **Given** any capability that can alter an output, **when** it
  runs, **then** a `CapabilityDelta` records `pre` and `post` — **including when `changed` is false**.
  → *invariant / property.* (`PG-5.2`)
- **AC-2.7** *(the join key survives)* — **Given** a `decision_id` from a past run, **when** an outcome
  resolves later, **then** it links to that decision without re-deriving the id from run contents.
  → *data contract.* (enables `F7b`)
- **AC-2.8** *(append-only)* — **Given** a written trace record, **when** a write to the same id is
  attempted, **then** it raises and the original is unchanged. → *invariant / property.*
  (`OR-13`, `INV-005/006`)
- **AC-2.9** *(⚠ no secret ever enters a trace)* — **Given** a run whose config or environment holds
  credentials, **when** any trace record is written, **then** no API key, token or password appears in
  it. → *invariant / property (security).*
- **AC-2.10** *(`QR-14` framework confinement)* — **Given** the source tree, **when** CI runs, **then**
  any orchestration framework is imported **only** by `src/orchestration/graph/**`, and an import
  elsewhere fails the build. → *invariant / property (structural).* (`A8`, `QR-14`)
- **AC-2.11** *(provenance on every resolution)* — **Given** a step that resolved a variant via `F1`,
  **when** its record is read, **then** it carries `Provenance` with `port`, `variant`, `version` and
  `experimental`. → *data contract.* (`F1` `CT-1.4`, `AP-6`)
- **AC-2.12** *(incomplete is loud)* — **Given** a run that fails mid-way, **when** its trace is read,
  **then** its status is `INCOMPLETE` and replay returns `UNREPLAYABLE` — ⚠ **never a silently partial
  trace that reads as whole**. → *unit.* (`P5`)

## 7. Open questions (must resolve before/at implementation)

- **Q1 — Storage location, format and size.** Alongside `manifest.json` in
  `.state/runs/<run_id>/`? One file per record type, or one append-only log? ⚠ **A trace containing
  full filing text plus every LLM request could be tens of MB per run** — the manifests are kilobytes.
  Blocks `CT-2.1`'s persistence and `Q2`.
- **Q2 — Retention.** Traces are needed for `F7b` *years* later, but full-payload traces will not fit
  indefinitely. Tiering (keep decisions and deltas forever, expire raw payloads after N months) is the
  obvious answer, ⚠ **but expiring payloads makes those runs unreplayable** — so the boundary is a
  real decision, not a cleanup detail.
- **Q3 — ★ What does replay actually prove?** Substituting recorded responses verifies the **control
  flow and the deterministic computation**. It does **not** verify that a model would answer the same
  way again — that is unknowable and not what replay is for. ⚠ The wording of `AC-2.3` must not
  over-claim, and the divergence report must not imply otherwise.
- **Q4 — Redaction boundary.** `AC-2.9` covers credentials, which is unambiguous. ⚠ Book positions,
  P&L and holdings are *sensitive but not secret* — and `QR-12`'s public mirror makes this concrete.
  Are they redacted, excluded, or simply never published? Blocks `AC-2.9`'s scope.
- **Q5 — Does the existing `seed` cover all randomness?** `RunManifest.seed` exists, which is
  promising. ⚠ Confirm there is no unseeded RNG, clock read or dict-ordering dependence before
  `AC-2.3` can pass. **This is a question about the inherited code and is answerable at `MS-2`.**
- **Q6 — Does F2 trace the inherited pipeline's jobs, or only platform code?** Tracing D-01/D-03
  internals means touching inherited domains, which `vision.md` §2 says change upstream. **Boundary
  proposal:** F2 records at *job* and *external-call* boundaries, which are already D-08's territory,
  and does not reach inside an inherited domain's logic.

## 8. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-2.1 | *(to be written)* | `src/orchestration/trace/models.py` |
| AC-2.2 | *(to be written)* | `src/orchestration/trace/record.py` |
| AC-2.3 | *(to be written — blocked Q3, Q5)* | `src/orchestration/trace/replay.py` |
| AC-2.4 | *(to be written)* | `src/orchestration/trace/replay.py` |
| AC-2.5 | *(to be written)* | `src/orchestration/trace/record.py` |
| AC-2.6 | *(to be written)* | `src/orchestration/trace/record.py` |
| AC-2.7 | *(to be written)* | `src/orchestration/trace/outcomes.py` |
| AC-2.8 | *(to be written)* | `src/orchestration/trace/store.py` |
| AC-2.9 | *(to be written — blocked Q4)* | `src/orchestration/trace/redact.py` |
| AC-2.10 | *(to be written)* | `tools/check_framework_confinement.py` |
| AC-2.11 | *(to be written)* | `src/orchestration/trace/models.py` |
| AC-2.12 | *(to be written)* | `src/orchestration/trace/store.py` |
