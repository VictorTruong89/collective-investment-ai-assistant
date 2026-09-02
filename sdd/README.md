# `sdd/` — Spec-Driven Development

This project is built spec-first. **The specs are the source of truth; the code is
downstream of them.** If code and spec disagree, one of them is a bug — say so
rather than quietly picking a side.

## The tiers

| Tier | Path | Authority | Lifetime |
|---|---|---|---|
| **Specs** | `specs/` | **Authoritative.** Code is built from here. | **Permanent** — amended in place, never archived while the code runs |
| **Design** | `design/` | **Non-authoritative.** Brainstorm, rationale, decision log. Never code from it. | **Release-scoped** — freezes when the release closes |
| **Blueprints** | `blueprints/` | **Permanent, per domain.** What the code actually does and why THIS construction among the several the spec would have allowed. | Amended with the code |
| **Archive** | `archive/` | **Historical.** Superseded, read-only. | Frozen forever |
| ★ **Questions** | [`questions.md`](questions.md) | **The register** — why each decision was made, and what was rejected. ⚠ Records reasoning, never rules. | Permanent, cross-cutting |

The rule that decides where something belongs:

> **Specs are release-independent. Designs are release-scoped.**
> A spec describes code that is *running now*. A brainstorm describes a decision
> process that *ended*. A blueprint describes code that *exists*, and the reasoning
> a spec deliberately leaves out.

## Layout

```
sdd/
├── README.md                       this file — the tier map
├── questions.md                    ★ the QUESTION REGISTER — every design question,
│                                     answered and open, by module, with the options
│                                     rejected and where each answer binds
├── specs/                          AUTHORITATIVE · permanent
│   ├── vision.md                   WHAT we are building              ← read first
│   ├── constitution.md             HOW we build: principles, invariants, data
│   │                                contracts, test tiers, change process
│   ├── ownership.yaml              spec → code globs. The PreToolUse gate reads this.
│   ├── README.md                   spec index
│   ├── _templates/spec.md          skeleton for a new feature spec
│   └── F<n>_<slug>/spec.md         one feature = one spec
├── design/                         NON-AUTHORITATIVE · release-scoped
│   ├── rel<N>_brainstorm.md        the live release's brainstorm + decision log
│   ├── rel<N>_design/
│   │   ├── L3-build-sequence.md    ★ the BUILD PLAN — M0..M9, the link step (M2),
│   │   │                             and the DX absorption-discrepancy log
│   │   └── L4-target-structure.md  the target tree the absorption merges into
│   ├── _templates/brainstorm.md    skeleton for the next release
│   └── releases/
│       ├── _template_closeout.md   skeleton for a release close-out
│       └── rel<N>_closeout.md      1 page: what shipped, AC status, what deferred
├── blueprints/                     PERMANENT · per domain
│   ├── README.md                   the tier and its rules
│   ├── _template.md                skeleton for a new blueprint
│   └── <domain>.md                 one per domain that has code
└── archive/                        HISTORICAL · frozen
    ├── README.md                   what is in here and why none of it binds
    └── rel<N>_*.md                 superseded release docs, kept as an immutable record
```

## The loop

1. **Diverge** — brainstorm freely in `design/rel<N>_brainstorm.md`.
2. **Converge** — record the decision in that file's Decisions log.
3. **Graduate** — copy `specs/_templates/spec.md` → `specs/F<n>_<slug>/spec.md`. A
   feature graduates **only when its acceptance criteria can be written.** If you
   can't write the ACs, it isn't clarified yet.
4. **Wire** — add the spec's globs to `specs/ownership.yaml` **in the same change**.
   A spec with no globs is unenforced.
5. **Implement** — failing test per `AC-<n>.<k>` first, then the smallest code that
   passes. Fill the traceability table.
6. **Verify** — run the whole test suite.

A task is done only when its AC has a passing test in the right tier (constitution §4).

## Enforcement

`CLAUDE.md` and skills *persuade*; only a hook *enforces*. `.claude/hooks/sdd_gate.py`
denies `Edit`/`Write` to a spec-governed path until the current session has actually
**Read** the constitution and the governing spec. The ledger is per-session — a new
conversation must read them again, because context does not carry over and neither
should the permission.

## Closing a release

When rel-`N` closes (see `design/releases/_template_closeout.md` for the checklist):

1. Extract anything still binding out of the brainstorm into the tier that binds it —
   a spec amendment, a constitution amendment, or `specs/vision.md`.
2. Mark `design/rel<N>_brainstorm.md` **FROZEN**. It stays in `design/`.
3. Write `design/releases/rel<N>_closeout.md` — one page.
4. Open `design/rel<N+1>_brainstorm.md` from the template.

**Nothing in `specs/` moves.** Archiving a live spec would silently un-govern live
code and disable the gate for those paths. **Do not write a `rel<N>_document.md`
as-built doc** — the specs plus their traceability tables *are* the as-built record,
continuously. A second one only drifts. `blueprints/` is not that document either —
it is per-domain, records what the code does and why, and drifts against the
*code*, not the specs.

## Current state

`specs/vision.md` and `specs/constitution.md` are written; `questions.md` tracks every
decision and the one still open. **No `F<n>` spec has graduated yet**, `ownership.yaml`
is still empty, and `src/` does not exist.

⚠ **`PG-1` blocks all implementation** until the inherited `ai-investment-pipeline`
completes a verified end-to-end run — milestone `M0` in
[`design/rel1_design/L3-build-sequence.md`](design/rel1_design/L3-build-sequence.md).
**Spec-writing is not blocked.**
