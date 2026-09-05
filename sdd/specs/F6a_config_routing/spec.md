# F6a — Config-influence routing

> **Spec-ID:** F6a · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §H.2 · lecture §2.4 ·
> [`../../questions.md`](../../questions.md) `QR-9`
> **Milestone:** `MS-6` · **Governs:** enforces **`PG-7`**, **`PG-9`**; inherits `AP-5`, `ST-9`/`INV-014`.
> **Capability:** `C2`(a) · `C5` — the machine-side half of the control plane.
>
> ✅ **Approved 2026-09-04.** Open questions adopted as decisions in §7 — ★ **read §7 before changing
> §5 or §6**; the rejected options are recorded there.

---

## 1. Goal & why

**One agent's output selects another's variant, model or horizon — as a pure function, mediated by the
orchestrator, with the influence recorded.**

This is the deterministic half of "interactive agents" (`QR-9`). The other half — agents *arguing* —
is `F6b`, gated on `F7a`. They were split because their failure modes are disjoint: **cycles** here,
**sycophancy** there.

★ **It is a routing function, not a plugin loader:** `(features, peer output) → variant name + reason`.
It decides *which*; `F1`'s registry decides *how to build it*. Keeping those separate is what lets
routing be unit-tested exhaustively without constructing a single model.

**What it reuses:** `src/orchestration/policy/` already holds `budget.py` and `retry.py` — D-08's
existing policy layer. F6a lands beside them; it does not create a parallel one.

## 2. Scope / non-goals

**In scope** — the routing function; the `Routing` contract; the mediation rule; cycle prevention;
`PG-7`'s three obligations.

**Non-goals**
- ✗ **Building the variant.** `F1` resolves; F6a only names.
- ✗ **Any message between agents.** That is `F6b`.
- ✗ **Recording.** F6a *returns* the reason; `F2` persists it.
- ✗ **LLM-driven routing.** ⚠ Explicitly out of scope — `PG-9`, and the reversal conditions are
  written down in the lecture §2.8.

## 3. Users & triggers

| ID | Trigger | Input | Entry point |
|---|---|---|---|
| T1 | Orchestrator needs a variant for a seat | features + optional peer view | `src/orchestration/policy/routing.py::select` |
| T2 | Evaluation partitions decisions by influence | `influenced_by` | `F5` consumes `F2`'s records |

## 4. Behaviour & reuse (the lean "how")

- **Pure function.** No I/O, no clock, no randomness. Same inputs ⇒ same `Routing`, always (`PG-9`).
- **Returns a reason, not just a name.** The predicate that fired is part of the return value, so
  *"why did this run use the one-week model?"* is answerable from the record rather than from memory.
- ★ **Mediated, never peer-to-peer.** The fundamental agent never calls the quant agent. Both import
  only the orchestrator's types. ⚠ A direct call would breach `ST-9` structurally and turn *n* agents
  into *n²* dependencies.
- ★★ **Phase-ordered, therefore acyclic.** Influence flows one way through a fixed phase order.
  ⚠ Mutual influence is a fixed-point computation and fixed points do not terminate for free; making
  the graph acyclic makes termination **structural** rather than hoped-for.
- **`influenced_by` is set whenever a peer's output shaped the choice** — the field `PG-7` turns on.
- ⚠ **Influence costs independence, and the cost is recorded rather than hidden.** Conditioning B's
  configuration on A's output means their agreement is partly an echo. `PG-7` requires that decisions
  be bucketed separately in evaluation and that the combined verdict never claim *"two independent
  views agree"* when one configured the other.

## 5. Contracts (inline)

**CT-6a.1 — `Routing`** (returned by `select`, consumed by `F1` and `F2`):
```json
{ "port": "str", "variant": "str",
  "reason": "str — the predicate that fired, e.g. 'realised_vol_60d > 0.45'",
  "influenced_by": "str | null — the seat whose output shaped this, PG-7",
  "candidates": ["str"] }
```
Rules: `reason` non-empty always; `variant` ∈ `candidates`; `candidates` = the registered variants for
that port at the time of the call (`F1` `AC-1.5`, closed set).

**CT-6a.2 — `select(port, features, peer=None) -> Routing`** — total: every input yields a `Routing`,
falling back to the declared default with `reason == "default"`.

## 6. Acceptance criteria

- **AC-6a.1** *(deterministic)* — **Given** identical inputs, **when** `select` runs any number of
  times, **then** it returns an equal `Routing`. → *invariant / property.* (`PG-9`)
- **AC-6a.2** *(no side effects)* — **Given** any call, **when** it runs, **then** it performs no I/O,
  reads no clock and consumes no randomness. → *invariant / property (structural).* (`PG-9`, `AP-5`)
- **AC-6a.3** *(the reason is always present and specific)* — **Given** any `Routing`, **when** read,
  **then** `reason` is non-empty; and where a threshold fired, it names the quantity and the bound.
  → *data contract.*
- **AC-6a.4** *(the chosen variant is registered)* — **Given** a `Routing`, **when** `F1` resolves it,
  **then** the variant is in the registry — ⚠ routing can never name a variant that does not exist.
  → *unit.* (`F1` `AC-1.5`)
- **AC-6a.5** *(★ `influenced_by` records cross-configuration)* — **Given** a selection that consumed a
  peer seat's output, **when** the `Routing` is read, **then** `influenced_by` names that seat; and
  **given** one that did not, **then** it is null. → *data contract.* (`PG-7.1`)
- **AC-6a.6** *(★★ no peer-to-peer import)* — **Given** the source tree, **when** CI runs, **then**
  `src/fundamental/**` and `src/quant/**` do not import each other, and neither imports the other's
  agent module. → *invariant / property (structural).* (`ST-9`, `INV-014`)
- **AC-6a.7** *(★★ influence is acyclic)* — **Given** the declared phase order, **when** the influence
  graph is built, **then** it is a DAG — ⚠ **a cycle fails the build**, not the run. → *invariant /
  property (structural).*
- **AC-6a.8** *(every selection is recorded)* — **Given** any `select` call in a run, **when** the
  trace is read, **then** a `DecisionRecord` exists with `state`, `candidates`, `action`, `reason`,
  `propensity == 1.0`, and the **`decision_id` of the ticker analysis it ran inside** — ⚠ *referenced,
  not minted here* (`F2` `CT-2.7`). → *data contract.* (`F2` `AC-2.5`, `PG-9`)
- **AC-6a.9** *(★ influenced decisions are separable)* — **Given** a set of decisions, **when**
  evaluation partitions them, **then** those with non-null `influenced_by` form a distinct bucket
  reportable on its own. → *data contract.* (`PG-7.2`)
- **AC-6a.10** *(⚠ never called agreement)* — **Given** a combined verdict whose inputs include a
  cross-configured seat, **when** it is rendered, **then** it does not assert that two independent
  views agree. → *invariant / property.* (`PG-7.3`)
- **AC-6a.11** *(total function)* — **Given** any features, including degenerate or missing ones,
  **when** `select` runs, **then** it returns a `Routing` — falling back to the default with
  `reason == "default"` rather than raising. → *unit.*

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **`D1`–`D3` ADOPTED 2026-09-04.**

**`D1` — The phase order is `quant → fundamental → risk`, and it is DERIVED, not chosen.**
*(Resolves `Q1`.)*

★★ **Already settled upstream, on economic grounds — this is not a free choice.**
`L0-system-vision` records the answer from `L2-signal-combination`:

> *"The combination is **quant ranks → thesis gates → risk alerts**, derived from **coverage
> economics** rather than from the `P3` ordering that was withdrawn: D-01's coverage is `O(1)/day`
> and **conditioned on D-03's output**, so it carries **zero cross-sectional ranking information**, and
> dense coverage costs **6.3–19 % of NAV per year**."*

- ★ **The running graph already implements it.** `DAILY_INFERENCE`'s order is
  `… features → rank → risk → observe → thesis → thesis_gate → decide …`: quant ranks first, the
  thesis gates, and the decision composes. `AC-6a.7`'s declared order is therefore a *statement of
  what runs*, not a new rule — which is the only kind that stays true.
- ⚠ **Do not resurrect the withdrawn `P3` ordering as the justification.** Constitution `P3` was
  narrowed to *"verdicts gate, never upgrade"* in Aug 2026 and the ordering mandate was deliberately
  removed. Citing it would re-assert a rule Victor retired.
- **Rejected — fundamental → quant.** ⚠ Inverts the dependency: D-01's coverage is *conditioned on*
  D-03's output, so running it first means analysing names the ranker would never surface — at
  6.3–19 % of NAV.
- **Rejected — leave the order undeclared.** `AC-6a.7` becomes untestable, and a phase order that is
  merely emergent changes silently when the graph is edited.

**`D2` — Exactly ONE predicate at `MS-6`: the volatility→horizon rule.** *(Resolves `Q2`.)*

- **Decision:** ship the worked example alone. ⚠ `PG-9` requires every routing choice to record the
  predicate that fired; a predicate set nobody has evaluated is a set of untested branches, and
  `F7b` can only attribute an outcome difference to a rule that actually varied.
- ★ **`AC-1.12`'s logic applied to predicates**: abstraction is earned. A second predicate arrives when
  a measured need for it does — and `F2`'s `DecisionRecord.state` is already recording what the policy
  saw, so the evidence for the next one accrues from day one.
- **Rejected — a fuller predicate library at `MS-6`.** ⚠ Every unexercised branch is a path through
  the control plane that `PG-9`'s replay has never covered.

**`D3` — `AC-6a.10` binds BOTH, and the enforcement point is composition (D-12).**
*(Resolves `Q3`.)*

- **Decision:** the rule — *a combined verdict may never claim two independent views agree when one
  configured the other* — is enforced **where the claim is constructed** (D-12 composition) and
  **checked again** where it is rendered (D-09).
- ★ **Why composition is the enforcement point:** if the claim is never *built*, no renderer can emit
  it. Guarding only D-09 leaves a true-looking `agreement=True` sitting in the decision record for
  `F5`, `F7b` and any future consumer to read.
- ⚠ **Why D-09 still checks:** rendering is where a human sees it, and `PG-7.3` is about what the
  reader is told. A single guard at composition would be correct and would still let a *report
  template* phrase concurrence into existence.
- **Rejected — rendering only.** Leaves the false claim in the data.
- **Rejected — composition only.** ★ Cheaper, and it fails the one place the harm actually lands.

## 8. Open questions

> ✅ **All three are resolved** — adopted 2026-09-04. **No open questions remain.**
> measured economics** — the running job graph implements it today.

 (must resolve before/at implementation)

- **Q1 — What is the declared phase order?** `AC-6a.7` needs one. Fundamental → quant, or the reverse,
  or a richer order? ⚠ The choice determines which seat can influence which, and it is an analytical
  decision, not an engineering one.
- **Q2 — Which routing predicates exist at `MS-6`?** The volatility→horizon rule is the worked example.
  A full predicate list is `MS-6` scoping, not spec content — but `AC-6a.3`'s test needs at least one.
- **Q3 — Does `AC-6a.10` bind rendering (D-09) or composition (D-12)?** Probably both, but the
  enforcement point should be named once.

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test | Code module |
|---|---|---|
| AC-6a.1 … AC-6a.5, AC-6a.11 | *(to be written)* | `src/orchestration/policy/routing.py` |
| AC-6a.6, AC-6a.7 | *(to be written)* | `tools/check_import_fences.py` |
| AC-6a.8 … AC-6a.10 | *(to be written)* | `src/orchestration/trace/` · `src/decision/` |
