# Collective Investment AI Assistant — working agreement

This repo is **spec-driven (lean SDD)**. The specs are the source of truth; the code
is downstream of them. If code and spec ever disagree, one of them is a bug — say so
rather than quietly picking a side.

All SDD material lives in **`sdd/`**: `sdd/specs/` is authoritative and permanent,
`sdd/design/` is the release-scoped brainstorm tier, `sdd/blueprints/` records what
the code does and why (per domain, once code exists), `sdd/archive/` is frozen
historical record. Map: `sdd/README.md`.

## Read before you write

- `sdd/specs/vision.md` — what this project is building. Read it before proposing or
  designing anything.
- `sdd/specs/constitution.md` — the non-negotiable rules every spec and every change
  must respect: principles, invariants, data contracts, test tiers, change process.
- The spec that governs the file you are about to touch — the mapping lives in
  `sdd/specs/ownership.yaml`.

## What this project is

A single-machine investment analysis system that can **explain and defend every
recommendation it makes — and measure whether any part of it actually helps.** Two
purposes, in a deliberate order: (1) a real investment tool the fund manager acts on
with his own capital; (2) a career portfolio piece for an AI-engineering role
transition around May–June 2027. `PG-2`: where they conflict on a number someone
would trade on, purpose 1 wins.

⚠ **This repo will absorb `../ai-investment-pipeline` and retire it** (vision §3).
Until then, that repo stays authoritative for its own domains — inherited analytical
logic is changed *there*, not here. This repo owns the platform layers only, and its
tree must stay a **superset** of the pipeline's so the absorption is a merge and not
a restructuring (`PG-8`).

**The seat model is this repo's own** — nine seats, numbered 1–9 (vision §3). Upstream
`L0` §1.5 numbers five. Never carry a seat number between the two repos without saying
which model it belongs to.

**Current state:** `vision.md` and `constitution.md` are written. No `F<n>` spec has
graduated yet, `ownership.yaml` is still empty, and `src/` does not exist —
**`PG-1` blocks all implementation** until the inherited pipeline completes a verified
end-to-end run. Spec-writing is not blocked.

## Enforcement

A `PreToolUse` hook (`.claude/hooks/sdd_gate.py`) denies `Edit`/`Write` to any path
`sdd/specs/ownership.yaml` marks as governed, until this session has actually **Read**
the specs that govern it. The ledger is per-session — a new conversation must read
them again, because context does not carry over and neither should the permission.
It fails open (allows the edit) if it errors, and prints a loud warning when it does.

## The loop

1. **Diverge** — brainstorm in `sdd/design/rel<N>_brainstorm.md`.
2. **Converge** — record the decision in that file's Decisions log.
3. **Graduate** — copy `sdd/specs/_templates/spec.md` → `sdd/specs/F<n>_<slug>/spec.md`
   once its acceptance criteria can be written.
4. **Wire** — add the spec's globs to `sdd/specs/ownership.yaml` in the same change.
   A spec with no globs is unenforced.
5. **Implement** — failing test per `AC-<n>.<k>` first, then the smallest code that
   passes. Fill the spec's traceability table.
6. **Verify** — run the whole test suite, not just the new test.

A task is done only when its AC has a passing test in the right tier (constitution §4).

## House rules

- Never `git commit` without review.
- Never hardcode a credential; read from the environment.
- Fail loud, never silent — a degraded input should raise, not emit a
  plausible-looking default.

These are starting defaults, not settled decisions — revise this file freely as the
project's actual working agreement takes shape.
