# F2 — Execution trace & replay

> **Spec-ID:** F2 · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §D.1 · lecture §2.7 ·
> [`../../questions.md`](../../questions.md) `QR-14`
> **Milestone:** `MS-3` — [`../../design/rel1_design/L3-build-sequence.md`](../../design/rel1_design/L3-build-sequence.md)
> **Governs:** `constitution.md` — enforces **`PG-5.2`**, **`PG-9`**, `PG-7`; inherits `P5`, `AP-6`,
> and upstream **`OR-13` / `INV-005` / `INV-006`** (manifest immutability).
> **Capability:** `C7` observability — the substrate `C2`, `C4`, `C5`, `C6` and `C8` all stand on.
>
> ✅ **Approved 2026-09-04.** `Q1`–`Q6` adopted as `D1`–`D6` (§7) — ★ **read §7 before changing §5 or
> §6**; the rejected options are recorded there and should not be re-argued.
> ⚠ `D5` found that `RunManifest.seed` does **not** cover all randomness — **43 wall-clock call sites**
> do not, which is why `AC-2.3` names what it cannot reproduce.

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
- ★★ **`decision_id` is minted once per `(run_id, ticker, attempt)`, at the START of that ticker's
  analysis** — before any routing, analysis or verdict exists. It is a **correlation id**, and minting
  it early is what makes it available to every record that must reference it (`CT-2.7`).
- **`propensity` is `1.0` while the control plane is deterministic** (`PG-9`). The field exists now so
  off-policy evaluation is possible later; ⚠ it is not a placeholder to be added when needed, because
  by then the history is gone.
- **Fail loud on incompleteness.** A run whose trace is partial is marked `INCOMPLETE`; ⚠ a partial
  trace that looks complete is worse than none (`P5`).
- ★★ **A trace is EVIDENCE, not output** (`D6` note). Upstream `AnalysisRunLog` states
  *"RECORD THAT IT FAILED; NEVER RECORD WHAT IT PRODUCED"* (`RA-111`/`AC-1.27`) — that rule stops a
  **degraded LLM output being persisted and later rendered as if sound**. ⚠ It is not a ban on
  recording payloads for evidence. **A trace record may never be a source from which a narrative is
  rendered**; it exists to be read by a human or a replay. `AC-2.9` and `D4`'s export filter are what
  keep it out of the output path. Without this sentence the two rules read as contradictory.
- **Replay substitutes, never re-calls.** The engine re-executes the graph with every external call
  served from the recording. A replay that reaches the network has failed.

## 5. Contracts (inline)

**CT-2.1 — `StepRecord`** (one per step, beneath an existing `JobRun`):
```json
{ "run_id": "str — FK to the existing RunManifest",
  "job_id": "str — FK to the existing JobRun",
  "step_id": "str — unique within the run",
  "parent_step_id": "str | null",
  "decision_id": "str | null — CT-2.7; null for run-scoped steps not about one ticker",
  "node": "str — graph node / function name",
  "seat": "int | null — 1..9; ⚠ NULL for cross-cutting D-00 work, which vision §3
           says has no seat (the registry itself is the first such step)",
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
  "envelope_hash": "str | null — ★ DX-76, which SHARED ENVELOPE was composed in front",
  "tokens": {"input": "int", "output": "int"}, "cost_usd": "float | null",
  "latency_ms": "int", "error": "str | null" }
```

> ✏ **Amended `A5` 2026-09-11 (`DX-76`) — `envelope_hash` added.** ⚠⚠ `prompt_version` names the
> **block's** version and nothing else. `DX-67` composed the shared sections `S-1`…`S-6` in front of
> **every call this project makes** and bumped **no version** — `E-02` is `v2` before and after — so a
> pre-envelope and a post-envelope recording were **indistinguishable in the trace**.
>
> ★★★ The consequence was not theoretical: `F5`'s `test_the_recording_is_not_from_a_RETIRED_prompt_
> version` exists precisely to stop the golden set grading a prompt the repo no longer ships, and it
> was **structurally blind to the largest prompt change the project has made** — because the envelope
> is per-block-INDEPENDENT text and the version is per-block, so it sat in the one place the
> versioning scheme had no name for.
>
> ⚠ `promote_recording` elides `request.payload`, where the composed prompt lives, so the question
> could not be answered from the artefact either. ★ The hash is computed from the same part list
> `compose_prompt` uses — a hash of a parallel list would be a hash of bytes the vendor never saw,
> which is worse than none because it reads as evidence.
>
> ⚠ `null` means **unknown** (a recording made before this field existed), never *"an empty
> envelope"* — that case is the string `"none"`. The distinction matters: four recordings promoted
> before 2026-09-11 carry `null` and **cannot be classified retroactively**.
Rules: `request` **and** `response` are both required — a request without its response cannot be
replayed. `model_id` records what actually served the call, so provider aliasing is visible.

**CT-2.3 — `DecisionRecord`** (⭐ `PG-9`):
```json
{ "run_id": "str", "step_id": "str",
  "decision_id": "str — ⚠ REFERENCE to CT-2.7, not owned here. This record's own
                  identity is step_id; a routing choice is part of a decision",
  "state": "object — the inputs the policy actually saw",
  "candidates": ["str"], "action": "str — the variant chosen",
  "reason": "str — the predicate that fired, e.g. 'realised_vol_60d > 0.45'",
  "propensity": "float — probability the policy assigned; 1.0 while deterministic",
  "influenced_by": "str | null — PG-7; the seat whose output shaped this choice" }
```

**CT-2.4 — `CapabilityDelta`** (⭐ `PG-5.2`):
```json
{ "run_id": "str",
  "decision_id": "str — reference to CT-2.7; ★ REQUIRED, and the reason CT-2.7 exists —
                  deliberation and explanation alter an output without any routing
                  decision to hang off",
  "capability": "str — e.g. 'deliberation', 'config_influence', 'explanation'",
  "pre":  "object — the value BEFORE the capability ran",
  "post": "object — the value AFTER",
  "changed": "bool" }
```
Rules: written **whenever the capability runs**, including when `changed` is `false` — ⚠ the
no-change cases are half the comparison and dropping them biases the study.

**CT-2.7 — `decision_id`** ⭐ *the join key every other record references* — added 2026-09-03 (`S1-1`):
```json
{ "decision_id": "str — mint format: '{run_id}:{ticker}:{attempt}'",
  "run_id": "str", "ticker": "str",
  "attempt": "int — 1 for the scheduled analysis; 2+ for a drill-down (QR-16),
              which is a SEPARATE analysis of the same ticker and mints its own",
  "minted_at": "iso8601 — at the START of the ticker's analysis" }
```

★★ **It identifies *the system's decision about one ticker in one run* — not a routing choice.**
Routing choices already have their own identity (`step_id`); they **reference** `decision_id`, they do
not own it.

⚠ **Why it is minted early rather than when the verdict forms.** Routing (`F6a`) runs *before* D-12
composes a verdict — so an id minted at verdict time could not be referenced by the records that
precede it. Minting at the start of the ticker's analysis removes the ordering problem entirely.

**Who references it:**

| Record | Relationship | Why it needs the *recommendation*, not the routing choice |
|---|---|---|
| `CT-2.1` `StepRecord` | references, **nullable** | ⚠ null for run-scoped steps that are not about one ticker (price ingest, calendar check) |
| `CT-2.3` `DecisionRecord` | references | a routing choice is *part of* a decision, not the decision |
| `CT-2.4` `CapabilityDelta` | references | *"what was the verdict before/after deliberation"* is about the recommendation |
| `CT-2.6` outcome link | joins on it | outcomes attach to recommendations |
| `F7b` `AC-7b.1` | joins on it | ★ the whole Tier-B study rests on this |

**CT-2.8 — on-disk layout** (`D1`) — beside the existing run record, never replacing it:
```text
.state/runs/<run_id>/
    manifest.json  outcome.json  ...   ← EXISTS (OR-13). F2 never writes here.
    trace.jsonl                        ← one JSON object per line; `type` discriminates
    trace/payloads/<call_id>.json      ← CT-2.2's request/response bodies
    trace/EXPIRED                      ← ⚠ written when payloads are removed (D2)
```
Rules: `trace.jsonl` is **append-only** (`AC-2.8`); a `CT-2.2` record stores a `payload_ref`, not the
body. ⚠ **Payloads are separate so `D2`'s expiry is a directory deletion** — inline bodies would make
expiry a log rewrite, which append-only forbids.

**CT-2.5 — `ReplayReport`:**
```json
{ "run_id": "str", "verdict": "REPRODUCED | DIVERGED | UNREPLAYABLE",
  "scope": "str — ALWAYS 'control flow and deterministic computation, given
            recorded external responses'. ★ D3: the verdict travels into reports,
            so its limit travels with it (PG-10's shape)",
  "excluded_fields": ["str"],
  "//excluded_fields": "D5 — wall-clock fields NOT compared. ⚠ PRINTED, never
                        silently skipped: an invisible exclusion is a lie",
  "first_divergence": "object | null — ⚠ NULL when verdict is REPRODUCED",
  "//first_divergence": {"step_id": "str", "field": "str",
                         "recorded": "object", "replayed": "object"} }
```
- `UNREPLAYABLE` when the trace is `INCOMPLETE`, an external call lacks its response, **or payloads
  have expired** (`D2`) — ⚠ in which case the reason names the expiry date.
- ⚠ **`IDENTICAL` was renamed `REPRODUCED` by `D3`.** A field named *identical* over-claims exactly
  where `PG-10` says a claim must carry its subject's status.

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
- **AC-2.3** *(★★ replay reproduces CONTROL FLOW — `D3`, `D5`)* — **Given** a completed run's trace,
  **when** it is replayed, **then** every output that does **not** depend on the wall clock is
  reproduced, the verdict is `REPRODUCED`, `scope` states what that covers, `excluded_fields` lists
  every wall-clock field not compared — **and no network call is made**. → *integration.*
  > ⚠ **The old wording over-claimed.** *"The run's deterministic outputs are reproduced"* did not say
  > which outputs are not deterministic — and `D5` measured **43 wall-clock call sites** across 8+
  > modules that `RunManifest.seed` does not cover. An AC that cannot be satisfied honestly is worse
  > than one that is merely narrow.
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
- **AC-2.13** *(★★ `decision_id` is minted once and referenced, never re-derived)* — **Given** a
  ticker's analysis in a run, **when** any `StepRecord`, `DecisionRecord` or `CapabilityDelta` for it
  is written, **then** all carry the **same** `decision_id`, minted once at the start of that
  analysis; and a drill-down of the same ticker carries a **different** one. → *data contract.*
  (`CT-2.7`, `PG-5.2`; enables `F7b`)
- **AC-2.8** *(append-only)* — **Given** a written trace record, **when** a write to the same id is
  attempted, **then** it raises and the original is unchanged. → *invariant / property.*
  (`OR-13`, `INV-005/006`)
- **AC-2.9** *(⚠ no secret ever enters a trace)* — **Given** a run whose config or environment holds
  credentials, **when** any trace record is written, **then** no API key, token or password appears in
  it. → *invariant / property (security).*
- **AC-2.14** *(★ positions are recorded in full, and filtered at EXPORT — `D4`)* — **Given** a trace
  containing book positions or P&L, **when** it is written, **then** the values are present unredacted;
  **when** it is exported for publication, **then** they are removed by the export filter.
  → *invariant / property.* (`QR-12`)
  > ★★ Redacting at write time would **break replay**, because positions are *inputs* to the decisions
  > being replayed. Same shape as `DX-5`: keep the artifact complete, control its **distribution**.
- **AC-2.15** *(★ expiry is recorded, never silent — `D2`)* — **Given** a run whose payloads have been
  expired, **when** it is replayed, **then** the verdict is `UNREPLAYABLE` and the reason names the
  expiry date. → *unit.* (`P5`)
  > ⚠ A run that cannot be replayed *because we deleted something* must say so. Silence reads as
  > corruption.
- **AC-2.16** *(★ an excluded field is visible — `D5`)* — **Given** a replay that skips wall-clock
  fields, **when** the `ReplayReport` is read, **then** every skipped field is listed in
  `excluded_fields`. → *data contract.*
  > ⚠ Never a blanket "ignore all datetimes": a decision timestamped in the wrong **order** is a real
  > bug, and a blanket rule would swallow it.
- **AC-2.10** *(`QR-14` framework confinement)* — **Given** the source tree, **when** CI runs, **then**
  any orchestration framework is imported **only** by `src/orchestration/graph/**`, and an import
  elsewhere fails the build. → *invariant / property (structural).* (`A8`, `QR-14`)
- **AC-2.11** *(provenance on every resolution)* — **Given** a step that resolved a variant via `F1`,
  **when** its record is read, **then** it carries `Provenance` with `port`, `variant`, `version` and
  `experimental`. → *data contract.* (`F1` `CT-1.4`, `AP-6`)
- **AC-2.12** *(incomplete is loud)* — **Given** a run that fails mid-way, **when** its trace is read,
  **then** its status is `INCOMPLETE` and replay returns `UNREPLAYABLE` — ⚠ **never a silently partial
  trace that reads as whole**. → *unit.* (`P5`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **`D1`–`D6` ADOPTED 2026-09-04.** The ACs they touch were amended in the same change.
>
> ★ **Several were settled by measuring the inherited code rather than by reasoning** — `MS-2`'s
> lesson, applied deliberately. Where that happened, the measurement is quoted.

**`D1` — Storage: an append-only `trace.jsonl` per run, with payloads in a sibling directory.**
*(Resolves `Q1`.)*

```text
   .state/runs/<run_id>/            ← EXISTS: manifest.json, outcome.json, thesis.json (~25 KB)
       trace.jsonl                  ← NEW: one JSON object per line, `type` discriminates
       trace/payloads/<call_id>.json ← NEW: the bulky halves of CT-2.2, by reference
```

- **Measured:** a run directory today is **~25 KB** (`manifest.json` 857 B–4 KB). `.state/` totals
  **20 MB** for ~3 months. ⚠ A trace carrying full filing text and every LLM request is **orders of
  magnitude larger than everything else in the directory combined** — so the layout has to survive that,
  not merely accommodate it.
- ★★ **The decisive argument is not size, it is `Q2`.** If payloads sit **inline** in the log, expiring
  them later means **rewriting the log** — which `AC-2.8` (append-only) forbids. **Inline payloads make
  tiered retention impossible without breaking immutability.** Separating them turns expiry into
  deleting a directory, which append-only permits without qualification.
- **Rejected — one JSON file per record type.** Matches the existing directory convention, but a
  crashed run leaves a half-written array that does not parse; JSONL's last line is either whole or
  visibly truncated, which `AC-2.12`'s `INCOMPLETE` needs.
- **Rejected — Parquet** (upstream already uses it for `.state/events/events.parquet`, 3.2 MB). ★ Right
  for *analytics across thousands of runs*, wrong for *appending during* one — it needs batching, and a
  crash loses the batch. ⚠ Do not build it yet: `F5`/`F7b` can derive a Parquet projection when they
  have a query. Building the analytics store before the query exists is the `P4` mistake.
- **Rejected — SQLite.** Queryable and transactional, but introduces a schema migration story for a
  record that is append-only and never updated. The cost lands before the benefit.

**`D2` — Retention: records forever, payloads expire — and expiry is RECORDED.**
*(Resolves `Q2`.)*

- **Measured:** there is **no retention code upstream**. What exists is
  `.state/runs-pruned-2026-08-28.tar.gz` — a **hand-made tarball**, done once. So this is a policy
  being written, not inherited.
- **The split follows what each is FOR.** Replay verifies a change *soon after* it is made; `F7b` joins
  decisions to outcomes *years* later. So `DecisionRecord`, `CapabilityDelta` and the outcome link are
  **permanent**; raw request/response payloads expire on a configured horizon (**default 12 months**).
- ★★ **Expiry must be recorded, not merely happen.** When payloads are removed, a marker is written so
  a later replay reports `UNREPLAYABLE: payloads expired <date>` instead of the file simply being
  missing. ⚠ *A run that cannot be replayed because we deleted something must say so;* silence here
  reads as corruption (`P5`).
- **Rejected — keep everything forever.** ⚠ `.state/` is already 20 MB for three months of ~25 KB runs;
  full payloads change the growth rate by orders of magnitude, and "we will deal with it later" is how
  a disk fills at the worst moment.
- **Rejected — tar.gz old runs** (what was done by hand). ◐ Preserves everything, but replay would need
  to extract an archive, and the practice is manual — which is why it happened **once**.

**`D3` — Replay proves control flow, and the verdict says so in its own name.**
*(Resolves `Q3`.)*

- **What replay establishes:** given the **recorded external responses**, the control flow and the
  deterministic computation reproduce. **What it does not establish:** that a model would answer the
  same way again. ⚠ That is unknowable and is not what replay is for.
- ★ **Rename the verdict `IDENTICAL` → `REPRODUCED`**, and add a literal `scope` field to `CT-2.5`
  carrying *"control flow and deterministic computation, given recorded external responses"*, so any
  consumer that renders the verdict renders its limit with it.
- ★★ **This is `PG-10`'s shape applied to replay** — *a claim carries its subject's status*. A field
  named `IDENTICAL` invites precisely the over-claim `PG-10` exists to prevent, and it would be quoted
  in the `MS-9` write-up, which is the highest-stakes place for it to mislead.
- **Rejected — keep `IDENTICAL` and add a caveat in prose.** The caveat lives in the spec; the field
  travels into reports. ⚠ **The name is what gets copied**, and a caveat that does not travel with the
  value it qualifies is decoration.

**`D4` — The trace is complete and LOCAL; redaction happens at export, never at write.**
*(Resolves `Q4`.)*

- Credentials are **never written at all** (`AC-2.9`, unchanged). Book positions, P&L and holdings are
  **sensitive but not secret**: they are written in full, and `.state/` is git-ignored.
- ★★ **Redacting positions at write time would break replay**, because positions are *inputs* to the
  decisions being replayed. A trace redacted at the source is not evidence of the run that happened.
- Publication is a **separate act**: `MS-9`'s mirror (`QR-12`, source-available) exports through a
  documented filter. ⚠ Nothing publishes a trace by default.
- ★ **Same shape as `DX-5`'s answer**: do not cripple the real artifact to make it safe to share —
  keep it complete, and control its **distribution**. That parallel is deliberate.
- **Rejected — redact at write.** Breaks replay, as above, and irreversibly: the unredacted value is
  gone.
- **Rejected — exclude positions from the trace.** Then `CapabilityDelta`'s `pre`/`post` cannot carry a
  verdict that references a position, and `PG-5.2`'s counterfactual arm is hollow.

**`D5` — ⚠ `seed` does NOT cover all randomness. The clock is the gap.**
*(Resolves `Q5`.)*

| Source | Measured | Verdict |
|---|---|---|
| `random.Random(seed)` in `src/fundamental/prompts/call.py` | **explicitly seeded**, seed threaded in | ✅ covered |
| `uuid.uuid4()` in `contracts/manifest.py:155` | only to make `run_id` unique — and `run_id` is **recorded** | ✅ harmless |
| ⚠ `datetime.now` / `utcnow` / `time.time()` | **43 call sites across 8+ modules** | ⛔ **NOT covered** |

★ **So the honest answer to `Q5` is no**, and the gap is not the RNG everyone worries about — it is the
wall clock, which nobody had counted.

- **Proposal:** record the run's clock origin in the trace and inject it where platform code allows;
  for inherited call sites, **exclude known wall-clock fields from the divergence comparison via an
  explicit allowlist that is itself printed in the `ReplayReport`.** ⚠ An excluded field must be
  **visible**, never silently skipped.
- ⚠ **`AC-2.3` currently over-claims** — *"the run's deterministic outputs are reproduced"* — without
  saying which outputs are not deterministic. It needs amending alongside this.
- **Rejected — a `Clock` port every module must use.** Correct, and a refactor of **43 sites across
  inherited domains** that `vision.md` §2 says change upstream. ★ Revisit per-domain as each is
  absorbed (`QR-22`) — not as a precondition for `MS-3`.
- **Rejected — ignore all datetime fields when comparing.** ⚠ Hides real divergences: a decision
  timestamped in the wrong *order* is a genuine bug, and a blanket rule would swallow it.

**`D6` — F2 records at job and external-call boundaries only.**
*(Resolves `Q6`.)*

- ★ **`QR-22` has already made this cheaper than when the question was written.** `src/orchestration/`
  is absorbed **before** `MS-3` starts, so instrumenting D-08's job boundaries is an **intra-repo
  change**, not an edit to a repo `vision.md` §2 says we do not touch.
- **Rejected — instrument inherited domain internals.** ✗ Reaches inside D-01/D-03 logic that changes
  upstream, and every such edit becomes a merge conflict at each absorption.
- **Rejected — platform code only.** ⚠ Too little: the LLM calls that most need recording happen
  *inside* D-01, and a trace that omits them cannot replay a run.
- ★ **Extension point, not an obligation:** a decorator inherited domains *may* adopt for deeper steps
  once absorbed. Offered, never required.

### ⚠⚠ A conflict `Q1`–`Q6` did not name — found while measuring

Upstream `src/fundamental/contracts/analysis_run.py::AnalysisRunLog` states its rule in a banner:

```text
RECORD THAT IT FAILED; NEVER RECORD WHAT IT PRODUCED.
```

It deliberately persists **call metadata only** — `call_id`, `step`, `tokens`, `attempts`, `outcome` —
and explicitly **not** the payload, because `RA-111`/`AC-1.27` exist to stop a *degraded* LLM output
being persisted and later rendered as if it were sound.

⚠ **`CT-2.2` requires the full `request` and `response`.** Read side by side, the two rules appear to
contradict. They do not — **a trace is evidence, not output** — but that distinction is currently
nowhere in writing, and the next reader will have to re-derive it or will "fix" one of them.

★ **Adopted — `F2` §4 states the distinction explicitly** — *a trace record may never be a source from
which a narrative is rendered; it exists to be read by a human or a replay, and `AC-2.9`'s redaction
plus `D4`'s export filter are what keep it out of the output path.* ⚠ This should be settled **before**
`MS-3` writes record #1, not after.

## 8. Open questions (must resolve before/at implementation)

> ✅ **All six are resolved** — `D1`–`D6` in §7, adopted 2026-09-04. ★ `Q5` was answered by
> **measuring the inherited code**, not by opinion: see `D5`'s table. **No open questions remain.**

- ~~**Q1 — Storage location, format and size.** Alongside `manifest.json` in
  `.state/runs/<run_id>/`? One file per record type, or one append-only log? ⚠ **A trace containing
  full filing text plus every LLM request could be tens of MB per run** — the manifests are kilobytes.
  Blocks `CT-2.1`'s persistence and `Q2`.
- ~~**Q2 — Retention.** Traces are needed for `F7b` *years* later, but full-payload traces will not fit
  indefinitely. Tiering (keep decisions and deltas forever, expire raw payloads after N months) is the
  obvious answer, ⚠ **but expiring payloads makes those runs unreplayable** — so the boundary is a
  real decision, not a cleanup detail.
- ~~**Q3 — ★ What does replay actually prove?** Substituting recorded responses verifies the **control
  flow and the deterministic computation**. It does **not** verify that a model would answer the same
  way again — that is unknowable and not what replay is for. ⚠ The wording of `AC-2.3` must not
  over-claim, and the divergence report must not imply otherwise.
- ~~**Q4 — Redaction boundary.** `AC-2.9` covers credentials, which is unambiguous. ⚠ Book positions,
  P&L and holdings are *sensitive but not secret* — and `QR-12`'s public mirror makes this concrete.
  Are they redacted, excluded, or simply never published? Blocks `AC-2.9`'s scope.
- ~~**Q5 — Does the existing `seed` cover all randomness?** `RunManifest.seed` exists, which is
  promising. ⚠ Confirm there is no unseeded RNG, clock read or dict-ordering dependence before
  `AC-2.3` can pass. **This is a question about the inherited code and is answerable at `MS-2`.**
- ~~**Q6 — Does F2 trace the inherited pipeline's jobs, or only platform code?** Tracing D-01/D-03
  internals means touching inherited domains, which `vision.md` §2 says change upstream. **Boundary
  proposal:** F2 records at *job* and *external-call* boundaries, which are already D-08's territory,
  and does not reach inside an inherited domain's logic.

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-2.1 | `tests/unit/test_trace.py::test_ac_2_1_every_record_carries_the_run_id_and_no_second_run_record` · `::test_ac_2_1_rejects_a_record_from_another_run` · `::test_ac_2_1_a_run_scoped_step_may_carry_no_decision_id` | `trace/models.py`, `trace/store.py` |
| AC-2.2 | `tests/unit/test_trace.py::test_ac_2_2_*` (3) · ★ **call granularity**: `tests/integration/test_trace_replay.py::test_ac_2_2_a_gateway_transport_call_is_recorded_with_both_halves` · `::test_ac_2_2_a_failing_transport_is_recorded_AND_re_raised` | `trace/models.py::ExternalCall`, `trace/wire.py::traced_transport` |
| AC-2.3 | `tests/integration/test_trace_replay.py::test_ac_2_3_*` (4) | `trace/replay.py::replay` |
| AC-2.4 | `tests/integration/test_trace_replay.py::test_ac_2_4_divergence_names_the_first_step_and_field` | `trace/replay.py` |
| AC-2.5 | `tests/unit/test_trace.py::test_ac_2_5_a_decision_record_is_complete` · `::test_ac_2_5_an_incomplete_decision_is_refused` (5 cases) | `trace/models.py::DecisionRecord` |
| AC-2.6 | `tests/unit/test_trace.py::test_ac_2_6_a_delta_is_written_even_when_nothing_changed` | `trace/models.py::CapabilityDelta` |
| AC-2.7 | `tests/integration/test_ms3_traced_run.py::test_ac_2_7_an_outcome_links_to_a_past_decision_without_re_deriving_the_id` · `::test_ac_2_7_an_outcome_may_not_be_silently_revised` | `trace/outcomes.py::OutcomeStore` |
| AC-2.8 | `tests/unit/test_trace.py::test_ac_2_8_rewriting_a_record_id_raises_and_leaves_the_original` | `trace/store.py`, `trace/errors.py::TraceImmutableError` |
| AC-2.9 | `tests/integration/test_trace_replay.py::test_ac_2_9_*` (5 groups, 16 parametrised) — ⚠ incl. `::test_ac_2_9_usage_fields_are_NOT_redacted`, the `DX-16` regression | `trace/redact.py::redact_secrets`, `::_key_is_secret` |
| AC-2.10 | `tests/structural/test_framework_confinement.py` (13, incl. one per framework) | `tools/check_framework_confinement.py` |
| AC-2.11 | `tests/integration/test_ms3_traced_run.py::test_ac_2_11_a_step_that_resolved_a_variant_carries_provenance` | `trace/models.py::StepRecord.provenance` |
| AC-2.12 | `tests/unit/test_trace.py::test_ac_2_12_an_unclosed_run_reads_as_incomplete` · `::test_ac_2_12_a_truncated_log_line_is_detected` · `tests/integration/…::test_ac_2_12_an_unclosed_run_is_unreplayable` | `trace/store.py::status` |
| AC-2.13 | `tests/unit/test_trace.py::test_ac_2_13_*` (2) | `trace/models.py::mint_decision_id` |
| AC-2.14 | `tests/integration/test_trace_replay.py::test_ac_2_14_*` (2) | `trace/redact.py::export_for_publication` |
| AC-2.15 | `tests/integration/test_trace_replay.py::test_ac_2_15_*` (2) | `trace/store.py::expire_payloads` |
| AC-2.16 | `tests/integration/test_trace_replay.py::test_ac_2_16_excluded_wall_clock_fields_are_listed` | `trace/replay.py` |

| — | `tests/integration/test_ms3_traced_run.py::test_ms3_*` (6) | **`MS-3`'s done-when**: the real 13-job `DAILY_INFERENCE` graph, traced and replayed |

✅ **All 16 ACs green, 2026-09-04**, every one mutation-verified (19 mutations; **4 survived on the
first pass and were closed**).

> ✏ **`AC-2.7` was wrongly deferred to `MS-4`.** Re-reading this spec settled it: `T6` names
> `trace/outcomes.py::link` and `CT-2.6` defines the record — the outcome **link** is F2's, and only
> the *metrics over* outcomes are `F5`'s (§2 non-goals). ★ The spec had the answer; the deferral came
> from reading the milestone plan instead of the spec.
