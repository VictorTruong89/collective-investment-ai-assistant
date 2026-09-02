# F6b — Inter-agent messaging & deliberation

> **Spec-ID:** F6b · **Status:** 🟡 draft · **Adopted:** —
> **Source discussion:** lecture §2.5–§2.6 · [`../../questions.md`](../../questions.md) `QR-3`, `QR-9`
> **Milestone:** `M7` · **Governs:** enforces `PG-5.1`, `PG-5.2`, `PG-3`; inherits `P3`, `P5`,
> `INV-014`/`ST-9`, `AP-3`.
> **Capability:** `C2`(b).
>
> ★★ **Graduation gate satisfied:** `PG-5.1` requires `F7a`'s Tier-A design to exist before this spec
> may graduate. [`F7a`](../F7a_deliberation_process_tests/spec.md) exists as of 2026-09-01.
> ⚠ **Deployment status is a separate matter** — see §2.1.
>
> ⚠ **`PG-1` blocks implementation.** Spec only.

---

## 1. Goal & why

**Two agents exchange typed messages about one recommendation, under a turn budget, and the exchange
terminates in a settled position or an escalation to the human.**

★ **The design problem is not making agents talk — it is making the talk carry information.** Three
documented failure modes make LLM debate produce motion without evidence, and **all three are silent**:

| Failure | What it looks like |
|---|---|
| ⚠⚠ **Sycophancy** | the challenged agent revises because it was challenged, not because the challenge was right |
| **Correlated errors** | two instances of one base model share blind spots; the second opinion adds confidence, not accuracy |
| **Position bias** | whoever speaks first frames the exchange; the outcome tracks order |

Every one produces a convincing transcript either way. **That is why `F7a` gates this spec** and why
§4's constraints are about *asymmetry* rather than about protocol richness.

★ **Where debate genuinely helps: asymmetry.** Risk sees the book; Research does not. Risk's challenge
carries **facts Research lacked** and cites a number that can be **checked deterministically**. That
condition describes the Risk↔Research pairing and describes no pairing of two general-purpose LLMs
discussing a thesis — which is the whole design brief.

## 2. Scope / non-goals

**In scope** — the message contract; the deliberation state machine and its termination guarantee; the
turn budget; escalation; the `PG-5.2` pre/post record; the firewall constraint on who may address whom.

**Non-goals**
- ✗ **Routing or configuration influence.** That is `F6a`, and it is deterministic.
- ✗ ⚠ **Wrapping arithmetic in messages.** `PG-3`: risk exposure and concentration are computed by
  `src/risk/`. A CHALLENGE that merely restates a number the other side could compute is theatre.
- ✗ **Deciding.** D-12 composes the verdict; deliberation may inform its inputs, never replace it
  (`PG-6`).
- ✗ **Measuring itself.** `F7a` does.
- ✗ **Free-form conversation.** Messages carry structured payloads (`CT-6b.1`).

## 2.1 ⚠ Deployment status is governed by `F7a`, not by this spec

Graduating is not shipping. `F7a`'s pre-registered bands decide what this capability is permitted to do:

| `F7a` T1 verdict | What `F6b` may do |
|---|---|
| **KEEP** (ratio ≤ 0.33) | deliberation may alter conviction and size, subject to `P3` |
| **ADVISORY_ONLY** (0.33 – 0.67) | ⚠ transcript is rendered; **the verdict is unaffected** |
| **DELETE** (> 0.67) | ⛔ the capability is removed |
| **INSUFFICIENT** (n < `min_n_per_arm`) | ⚠ **ADVISORY_ONLY** until powered — never KEEP by default |

★ The `INSUFFICIENT` row matters: absence of evidence defaults to the *safe* branch, not the
convenient one.

## 3. Users & triggers

| ID | Trigger | Input | Entry point |
|---|---|---|---|
| T1 | A recommendation is formed and the risk seat has a material objection | verdict, book state | `src/orchestration/graph/deliberation.py::deliberate` |
| T2 | The turn budget is exhausted | turn count | same — terminates |
| T3 | Positions do not converge | state | escalate to seat 1 |

## 4. Behaviour & reuse (the lean "how")

- **A state machine, not a chat.** `PROPOSED → CHALLENGED → REVISED → SETTLED | ESCALATED`. The only
  cycle is re-challenge, and it **decrements a budget**, so the machine halts by construction.
- ★ **Challenges cite checkable facts.** A `CHALLENGE` names the field it disputes and the value it
  expected. ⚠ If the payload is prose, only another model can consume it and the branch becomes
  undecidable.
- ★★ **The firewall shapes who may address whom** (`INV-014`/`ST-9`):

  | Pair | Allowed | Why |
  |---|---|---|
  | Risk ↔ Research | ✅ | asymmetric information — Risk sees the book |
  | Risk ↔ Quant | ◐ not needed | a rank score is a number; there is nothing to debate |
  | ⛔ **Research ↔ Quant** | ✗ **forbidden** | their independence is the point |

- **Mediated by the orchestrator.** Agents exchange messages *through* D-08 and never import each
  other — the same rule `F6a` follows.
- ⚠ **Escalation is a first-class outcome, not a failure.** Forcing convergence means silently
  averaging a genuine disagreement, which is exactly the information most worth seeing.
- **`P3` holds inside deliberation.** A revision may make a verdict equal or more conservative, never
  more aggressive.
- ★ **Speaking order is randomised** so `F7a`'s T4 can measure whether it mattered.
- **Pre/post is recorded from the first run** (`PG-5.2`) — including when nothing changed.

## 5. Contracts (inline)

**CT-6b.1 — `AgentMessage`:**
```json
{ "correlation_id": "str — one deliberation", "turn": "int",
  "sender": "str — seat", "receiver": "str — seat",
  "type": "REQUEST|RESPONSE|CHALLENGE|REVISION|ACKNOWLEDGE|BLOCK|ERROR|ESCALATE",
  "payload": {"field": "str — the disputed quantity",
              "expected": "number|str|null",
              "observed": "number|str|null",
              "note": "str — ⚠ human-readable ONLY; never branched on"},
  "sent_at": "iso8601" }
```
Rules: immutable once sent; `CHALLENGE` requires `payload.field`; `note` is never consumed by control
flow.

**CT-6b.2 — `Deliberation`:**
```json
{ "correlation_id": "str", "subject_id": "str",
  "state": "PROPOSED|CHALLENGED|REVISED|SETTLED|ESCALATED",
  "messages": ["AgentMessage"],
  "turns_used": "int", "turn_budget": "int",
  "speaking_order": ["str"], "order_seed": "int",
  "pre_verdict": "object", "post_verdict": "object",
  "mode": "ACTIVE|ADVISORY_ONLY — from F7a's band" }
```

## 6. Acceptance criteria

- **AC-6b.1** *(★★ termination is guaranteed)* — **Given** any deliberation, **when** it runs, **then**
  it reaches `SETTLED` or `ESCALATED` within `turn_budget` — ⚠ **no input produces an unbounded
  exchange**. → *invariant / property.*
- **AC-6b.2** *(challenges are checkable)* — **Given** a `CHALLENGE`, **when** read, **then**
  `payload.field` names a quantity the receiver can verify, and `expected` is present. → *data
  contract.*
- **AC-6b.3** *(⚠ control flow never branches on prose)* — **Given** the source tree, **when** CI runs,
  **then** no branch reads `payload.note`. → *invariant / property (structural).*
- **AC-6b.4** *(★★ the firewall holds)* — **Given** any deliberation, **when** its messages are read,
  **then** no message has Research as sender and Quant as receiver, or the reverse. → *invariant /
  property.* (`INV-014`, `ST-9`)
- **AC-6b.5** *(no direct import)* — **Given** the source tree, **when** CI runs, **then** no agent
  module imports another agent module; all exchange is via D-08. → *invariant / property
  (structural).*
- **AC-6b.6** *(`P3` holds through revision)* — **Given** a `REVISION`, **when** the verdict is
  compared with the pre-deliberation one, **then** it is equal or more conservative — ⚠ **never more
  aggressive**. → *invariant / property.* (`P3`)
- **AC-6b.7** *(★ escalation is reachable and recorded)* — **Given** a deliberation that exhausts its
  budget without convergence, **when** it ends, **then** the state is `ESCALATED` and the disagreement
  is surfaced to seat 1 — ⚠ **never silently averaged**. → *unit.*
- **AC-6b.8** *(★★ pre/post recorded always)* — **Given** any deliberation, **when** it ends, **then** a
  `CapabilityDelta` records `pre_verdict` and `post_verdict`, **including when they are equal**.
  → *data contract.* (`PG-5.2`, `F7a` `AC-7a.6`)
- **AC-6b.9** *(order is randomised and recorded)* — **Given** a deliberation, **when** it starts,
  **then** `speaking_order` is drawn from a recorded `order_seed`. → *data contract.* (enables `F7a` T4)
- **AC-6b.10** *(★ advisory mode cannot alter the verdict)* — **Given** `mode == "ADVISORY_ONLY"`,
  **when** the deliberation ends, **then** `post_verdict == pre_verdict` and the transcript is still
  rendered. → *invariant / property.* (§2.1)
- **AC-6b.11** *(messages are immutable and traced)* — **Given** a sent message, **when** a write to it
  is attempted, **then** it raises; and every message appears in the run trace. → *invariant /
  property.* (`F2` `AC-2.8`)
- **AC-6b.12** *(an agent error degrades, not crashes)* — **Given** an agent that fails mid-exchange,
  **when** it emits `ERROR`, **then** the deliberation terminates with a partial result **marked
  incomplete** — ⚠ never a silently shortened exchange presented as settled. → *unit.* (`AP-4`, `P5`)

## 7. Open questions

- **Q1 — What is `turn_budget`?** Lecture §2.5: `max_turns=1` is request-response; `N` is full
  deliberation. ⚠ Cost scales with turns (`F7a` T7) and so does sycophancy exposure. *Leaning: start
  at 1 and raise only if T5 shows information content justifying it.*
- **Q2 — What makes an objection "material" enough to trigger T1?** A threshold on the risk metric, or
  the risk agent's judgement? ⚠ If the latter, that judgement needs its own record.
- **Q3 — Does `BLOCK` exist?** The earlier taxonomy included it — a challenge that forces rework before
  the pipeline proceeds. ⚠ It adds a state and a deadlock risk. *Leaning: omit until a case needs it
  (`A4`).*
- **Q4 — Does deliberation run before or after D-12 composes?** Before means it shapes inputs; after
  means it can only annotate. ⚠ `PG-6` says D-12 composes and originates nothing, which argues for
  *before*.
- **Q5 — Which seat may initiate?** §4 gives Risk the challenge role on asymmetry grounds. Can Research
  challenge Risk? Symmetry is tempting but the information asymmetry runs one way.

## 8. Traceability

⚠ **Empty by design** — `PG-1`, and deployment mode awaits `F7a`'s verdict.

| AC | Test | Code module |
|---|---|---|
| AC-6b.1, AC-6b.7, AC-6b.12 | *(to be written — Q1)* | `src/orchestration/graph/deliberation.py` |
| AC-6b.2, AC-6b.3 | *(to be written)* | `src/shared/agents/messages.py` |
| AC-6b.4, AC-6b.5 | *(to be written)* | `tools/check_import_fences.py` |
| AC-6b.6, AC-6b.10 | *(to be written)* | `src/orchestration/graph/deliberation.py` |
| AC-6b.8, AC-6b.9, AC-6b.11 | *(to be written)* | `src/orchestration/trace/` |
