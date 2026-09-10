# F6b — Inter-agent messaging & deliberation

> **Spec-ID:** F6b · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** lecture §2.5–§2.6 · [`../../questions.md`](../../questions.md) `QR-3`, `QR-9`
> **Milestone:** `MS-7` · **Governs:** enforces `PG-5.1`, `PG-5.2`, `PG-3`; inherits `P3`, `P5`,
> `INV-014`/`ST-9`, `AP-3`.
> **Capability:** `C2`(b).
>
> ★★ **Graduation gate satisfied:** `PG-5.1` requires `F7a`'s Tier-A design to exist before this spec
> may graduate. [`F7a`](../F7a_deliberation_process_tests/spec.md) exists as of 2026-09-01.
> ⚠ **Deployment status is a separate matter** — see §2.1.
>
> ✅ **Approved 2026-09-04.** Open questions adopted as decisions in §7 — ★ **read §7 before changing
> §5 or §6**.

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

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **ADOPTED 2026-09-04.**
> ★ **Two are settled by the constitution rather than by preference** — `D3` by `P4`, `D4` by `PG-6`.

**`D1` — `turn_budget = 2`: one challenge, one response.** *(Resolves `Q1`.)*

- **Decision:** the minimum that permits an actual exchange. ⚠ `max_turns = 1` is request–response and
  cannot show revision at all; `N` unbounded makes `T7`'s cost unbounded and gives `PG-3`'s
  *deliberation theatre* room to accumulate transcript without changing a position.
- ★ **`T6` is what raises it, not intuition.** It measures convergence rate and turns-vs-budget: if
  deliberations routinely hit the budget without converging, that is measured evidence for 3 — and
  `F2` records the turn count from day one, so the evidence accrues before the question is asked.
- **Rejected — unbounded turns.** ⚠ Cost scales with the one failure mode we most expect.
- **Rejected — 1 turn.** Not deliberation; there is nothing for `T1` to measure.

**`D2` — "Material" is a DECLARED THRESHOLD on the challenger's own metric, recorded as the reason.**
*(Resolves `Q2`.)*

- **Decision:** the challenging seat declares a numeric trigger on a metric **it owns** (e.g. risk
  contribution above a stated level), and that predicate is written into the `DecisionRecord.reason`
  — exactly as `F6a` routing does.
- ⚠ **Not a model judgement of materiality.** `PG-9`'s *"why did this happen?"* must have an answer
  better than *"the model thought it mattered"*; and a model deciding when to object is a model
  deciding how often it speaks.
- **Rejected — an LLM decides materiality.** ⚠ Makes the objection *rate* itself unexplainable, and
  `T2`'s effect size becomes uninterpretable: a change in rate could be the world or the model.
- **Rejected — always challenge.** Guarantees `PG-3`'s theatre and maximises `T7`'s cost.

**`D3` — ⛔ No `BLOCK` at `MS-7`.** *(Resolves `Q3`.)*

- ★★ **`P4` decides it: D-12's gate algebra already blocks.** A challenge that forces rework would be a
  **second gating mechanism**, and two gates that can disagree is precisely the defect the *"one
  answer"* rule exists to prevent.
- **Decision:** a challenge produces a **recorded objection** which D-12's existing algebra consumes.
  ⚠ If the objection should stop a recommendation, that is a **gate**, and gates live in D-12.
- **Rejected — reinstate `BLOCK`.** ⚠ It would let a deliberating agent halt a decision — an agent that
  *acts* rather than advises, which is the same line `F3` `D4` holds for corporate actions.

**`D4` — Deliberation runs BEFORE D-12 composes. It shapes inputs; it never touches the verdict.**
*(Resolves `Q4`.)*

- ★★ **`PG-6` decides it, and leaves no room:** the verdict algebra is *"a bounded meet-semilattice…
  a **structural** guarantee, not a runtime check"*, and any agent-assisted combination is
  *"**advisory alongside, never replacing**"*.
- ⚠ **Running after composition would mean revising a composed verdict**, which is exactly the
  replacement `PG-6` forbids — *"an unfalsifiable combination rule at the point where output becomes
  action is the most expensive mistake available in this design."*
- ★ Before-composition also makes `PG-5.2`'s two arms clean: `pre` is the seat's own output, `post` is
  its output after deliberation, and **D-12 composes deterministically from whichever it is given** —
  so the counterfactual is a property of the *input*, not of a re-run of the decision.
- **Rejected — after composition.** Forbidden by `PG-6`, and it would make the `pre`/`post` arms
  differ by a re-composition rather than by deliberation, confounding `F7b`.

**`D5` — Only Risk initiates at `MS-7`. ⚠ The FIREWALL decides this, not preference.**
*(Resolves `Q5`.)*

- ★★ **`INV-014`/`ST-9`: D-01 and D-03 must not see each other's in-progress work.** Risk (D-05)
  consumes both analysts' **published** outputs, so a Risk challenge crosses nothing. **A Research
  challenge to Quant would be a firewall crossing** — and `PG-7` says the same thing from the other
  side: once one seat shapes the other, their agreement stops being independent evidence.
- ★ §4's asymmetry argument survives too: Risk's objections are checkable against arithmetic the
  pipeline already computes, so `T5`'s *"cites a checkable fact"* has something to bind to.
- **Rejected — any seat may challenge any other.** ⚠ Breaks the firewall, and `PG-7.3` would then have
  to be enforced on every pair rather than on one edge.
- **Rejected — the mediator (seat 6) initiates.** It composes; an initiator that also composes is the
  `D3`/`P4` problem again in a different place.

## 8. Open questions

> ✅ **All five are resolved** — adopted 2026-09-04. **No open questions remain.** ★ `D3` and `D4` are settled by `P4` and
> `PG-6` — they are not free choices. (must resolve before/at implementation)

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

## 9. Traceability (spec → test → code)

✅ **All 12 ACs green, 2026-09-09** — every one mutation-verified (11 mutations, **all caught on the
first pass**).

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-6b.1 | ★ `tests/unit/test_deliberation_safety.py::test_ac_6b_1_every_input_terminates_within_budget` (8 cases) | `graph/deliberation.py::deliberate` |
| AC-6b.2 | `tests/unit/test_deliberation.py::test_d2_a_challenge_without_a_declared_threshold_is_refused` | `deliberation.py::Message.__post_init__` |
| AC-6b.3 | ★ `tests/structural/test_peer_to_peer_fence.py::test_ac_6b_3_*` (4) | `tools/check_import_fences.py::prose_branch_violations` |
| AC-6b.4 | `tests/unit/test_deliberation.py::test_d5_only_risk_may_initiate_and_the_firewall_is_why` | `deliberation.py::FirewallCrossing` |
| AC-6b.5 | ★ `tests/structural/test_peer_to_peer_fence.py::test_ac_6b_5_*` (2) | `check_import_fences.py::agent_cross_import_violations` |
| AC-6b.6 | ★★ `tests/unit/test_deliberation_safety.py::test_ac_6b_6_*` (8) | `deliberation.py::assert_not_escalated` · `VerdictEscalated` |
| AC-6b.7 | ★ `::test_ac_6b_7_escalation_is_recorded_not_averaged` · `tests/unit/test_deliberation.py::test_escalation_is_a_first_class_outcome` | `deliberation.py::deliberate` |
| AC-6b.8 | ★ `::test_ac_6b_8_*` (3) | `deliberation.py::capability_delta` |
| AC-6b.9 | ★ `::test_ac_6b_9_*` (2) | `deliberation.py::speaking_order` |
| AC-6b.10 | ★★ `::test_ac_6b_10_*` (4) | `deliberation.py::ACTIVE` · `ADVISORY_ONLY` · `DEFAULT_MODE` |
| AC-6b.11 | `::test_ac_6b_11_a_sent_message_is_immutable` | `deliberation.py::Message` (frozen) |
| AC-6b.12 | ★ `::test_ac_6b_12_*` (3) | `deliberation.py::deliberate` · `Deliberation.incomplete_reason` |
| — | ★★★ `tests/integration/test_f6b_f7a_end_to_end.py` (5) | **the `F6b`→`F7a` loop, closed** |

### ⚠⚠ What completing this spec exposed — three findings, 2026-09-09

1. **⛔⛔ `P3` was not enforced inside deliberation (`DX-48`).** `AC-6b.6` says *"a revision may make a
   verdict equal or more conservative, **never more aggressive**"* — and `deliberate()` did not check.
   ★★★ The ordering is what makes this severe: deliberation runs **before** D-12 (`D4`), so an
   escalated verdict reaches the composer looking like the seat's own honest output, and D-12 composes
   deterministically from whatever it is handed. ⚠ Nothing downstream catches it — `RP-7`/`DC-5`
   compare the *composed* verdict to the *nominated* one, and after an escalation here **both already
   carry it**. ✅ `assert_not_escalated()` runs on what the agent PROPOSED, before the mode decides
   whether to apply it, so an escalation cannot lie dormant in `ADVISORY_ONLY` and arrive the day the
   band is promoted.
2. **`ADVISORY_ONLY` could not be expressed (`DX-49`).** §2.1's band table maps every `F7a` verdict onto
   what `F6b` may do — and `Deliberation` had **no `mode` field**, so the table bound to nothing.
   ⚠ Including its `INSUFFICIENT` row, which exists precisely so *absence of evidence defaults to the
   safe branch, not the convenient one*. ✅ `DEFAULT_MODE = ADVISORY_ONLY`: `F7a` has never run, so
   nothing has yet earned `ACTIVE`. ★★ The advisory path still records `advisory_post` — what it
   *would* have done — because an advisory capability that discarded its own proposal would make the
   Tier-B study impossible for exactly the period the capability is unproven.
3. **★★★ The `F6b`→`F7a` loop had never closed (`DX-50`).** `F7a` §4 opens *"every test runs on
   `CapabilityDelta` pairs"*; `AC-6b.8` requires the pair to be recorded. **Neither side existed**:
   `run_tier_a` took hand-made objects and `deliberate()` emitted no delta. ⚠ So `F7a` was an
   instrument with nothing to measure and `F6b` a capability that could not be measured — **each
   complete on its own terms, and jointly useless.** ✅ `capability_delta()` emits exactly the shape
   `challenges_from_deltas()` reads, and the end-to-end test demonstrates the instrument
   discriminating: an evidence-weighing agent scores `ratio 0.000 → KEEP`, a capitulating one
   `ratio 1.000 → DELETE`.
