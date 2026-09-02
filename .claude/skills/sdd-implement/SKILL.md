---
name: sdd-implement
description: >
  Implement or change code in this repo under its spec-driven development (SDD)
  process. Use this BEFORE writing or editing anything under a spec-governed path
  — it loads the constitution and the governing spec, finds the acceptance
  criteria, and drives the spec -> failing test -> code -> traceability loop.
  Also use when a change has no covering AC (the spec must be amended first), or
  when code and spec disagree. Triggers: "implement", "add a feature", "follow
  the specs", "SDD".
---

# Implementing under SDD

The specs are the source of truth; code is downstream. Your job is to make the
code satisfy a *named* acceptance criterion — not to write something that looks
plausible. A `PreToolUse` hook enforces step 1 and will deny your edit otherwise.

## 1. Load the governing spec (required)

Read, with the Read tool — Grep and `cat` do not satisfy the gate:

- `sdd/specs/constitution.md` — always.
- The spec that owns the path you are touching. The mapping is
  `sdd/specs/ownership.yaml`; `sdd/specs/README.md` indexes all specs.
- `sdd/specs/vision.md` when the task is to *propose* or *scope* rather than
  implement a named AC.

Do not skim. The constitution's invariants and the spec's contracts are the
things you are most likely to violate by accident.

## 2. Find the acceptance criterion

Locate the `AC-<n>.<k>` your change satisfies and quote it in your plan.

**If no AC covers the change, stop and amend the spec first** (constitution
§5). Say so plainly and propose the AC text. Writing un-specified behaviour is
the failure mode this whole process exists to prevent — an AC you invent in
your head is exactly the hallucination the gate is trying to catch. Amending
the spec is a legitimate deliverable, not a detour.

If the spec and the existing code disagree, surface it as a defect and ask
which is wrong. Do not silently conform the code to the spec or the spec to
the code.

## 3. Write the failing test first

Every AC maps to a test tier (constitution §4) — data contract,
invariant/property, golden/characterization, API contract, metric gate, unit,
or integration. Pick the tier the AC names.

- Name the AC in the test docstring so the traceability table stays honest.
- Run it and confirm it fails **for the reason you expect**. A test that
  passes immediately, or fails on an import error, has told you nothing.

## 4. Implement the smallest thing that passes

Reuse before rebuild — check whether an existing module already does this
before adding a new one. No frameworks or abstractions for hypothetical future
callers.

## 5. Verify and close the loop

Run the whole test suite, not just the new test — the suite is the regression
net, and a green new test beside newly-red old ones is a net loss. Then update
the spec's traceability table: acceptance criterion → test → code module.

Report honestly: which ACs are now green, which remain unbuilt, and anything
you left out and why. Do not report "done" for an AC whose test you did not
run.

## Never

- Never `git commit` without review.
- Never hardcode a credential; read from the environment.
- Never mark an AC green on the strength of code you wrote but did not execute.
