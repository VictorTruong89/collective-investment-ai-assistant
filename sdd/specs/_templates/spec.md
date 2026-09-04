# F<n> — <Feature name>

> **Spec-ID:** F<n> · **Status:** 🔵 idea | 🟡 draft | 🟢 approved · **Adopted:** YYYY-MM-DD
> **Source discussion:** `sdd/design/rel<N>_brainstorm.md` <section / session refs>
> **Governs:** `constitution.md` (enforces P…, INV-…, DC-…). Lean SDD: acceptance
> criteria + inline contracts, no separate plan/tasks.

<!--
HOW TO USE THIS TEMPLATE (delete this comment block in the real spec):
- Copy this file to  sdd/specs/F<n>_<slug>/spec.md.
- A feature is ready to leave the brainstorm (design/) and become a spec ONLY when
  you can write its acceptance criteria (§6). If you can't, it's not clarified yet —
  keep it in design/rel<N>_brainstorm.md.
- Every acceptance criterion (AC-n.k) must map to exactly one test tier (constitution
  §4) and appear in the Traceability table (§8). A task is "done" only when its AC
  has a passing test in the right tier.
- Contracts (CT-n.k) are the concrete data/API/schema shapes. Reference constitution
  invariants/contracts by ID instead of restating them.
- Status: 🔵 idea → 🟡 draft (has ACs) → 🟢 approved (reviewed; coding may start).
-->

---

## 1. Goal & why

<One paragraph: WHAT this feature does and WHY it matters.>

## 2. Scope / non-goals

**In scope:** <the specific slices this spec commits to.>
**Non-goals (this spec):** <what is explicitly deferred / owned by another spec —
name it.>

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | <when/how invoked> | <user-supplied? system-chosen?> | `<module::function or endpoint>` |

## 4. Behaviour & reuse (the lean "how")

- **<Step / concern>:** <what happens; which EXISTING asset it reuses (reuse before
  rebuild); which invariant it enforces.>

## 5. Contracts (inline)

**CT-<n>.1 — <name>** (<where persisted / returned>):
```json
{ "field": "type / enum / rule" }
```
Rules: <required keys, enums, nullability, ranges. Reference DC-* where a global
data contract already covers it.>

**CT-<n>.2 — <API / structure contract>:**
- `<METHOD /route>` → <status + body shape>; <error status + reason on failure>.

## 6. Acceptance criteria (Given / When / Then → test tier)

> Each AC is one testable behaviour. Tag the test tier (data-contract ·
> invariant/property · golden/characterization · API-contract · metric-gate · unit ·
> integration) and the constitution/spec IDs it enforces.

- **AC-<n>.1** *(<short label>)* — **Given** <precondition>, **when** <action>,
  **then** <observable outcome>. → *<test tier>.* (<INV/DC/P refs>)
- <mark any AC blocked on an open question, e.g. "(blocked — Q1)">

## 7. Decisions (resolved questions — kept with their rejected options)

> Move a question here once decided, rather than deleting it. Record **the options that were
> rejected and why** — a later reader must be able to reconstruct the argument without the
> conversation that produced it. Give each a `D<n>` and cite it from the ACs it changed.
> ⚠ Keep this heading even when empty (write *None yet*) — section numbers stay stable
> across all specs, so `§9` always means traceability.

## 8. Open questions (must resolve before/at implementation)

- **Q1 — <question>:** <context; which AC it blocks.>

## 9. Traceability (spec → test → code)

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-<n>.1 | *(to be written)* | `<module>` |
