# Release <N> — Feature Design & Brainstorm

> **SDD role: `design/` tier — NON-AUTHORITATIVE.** This is the brainstorm /
> rationale / decision log, not a contract. **Do not code from this file.** The
> source of truth for implementation is `../specs/vision.md` (what we're building)
> + `../specs/constitution.md` (global rules) + the per-feature
> `../specs/F<n>_<slug>/spec.md`. Ideas here *graduate* into a spec once their
> acceptance criteria can be written; if this doc and a spec ever disagree,
> **the spec wins.**
>
> **Status:** OPEN · **Opened:** YYYY-MM-DD · **Previous release:** `rel<N-1>_brainstorm.md` (FROZEN)
> This is a *living* doc — each brainstorm session appends to it.

<!--
HOW TO USE THIS TEMPLATE (delete this comment block in the real file):
- Copy to  sdd/design/rel<N>_brainstorm.md  when the release opens.
- Session numbering restarts at 1 each release. When citing a session from a spec
  or the constitution, write it as `rel<N> S<k>` (e.g. "rel1 S3") — a bare
  "Session 3" becomes ambiguous the moment a second release exists.
- A feature leaves this file and becomes a spec ONLY when you can write its
  acceptance criteria.
-->

---

## Release goal

<One paragraph. What does this release advance, and why now?>

## Carried over from rel<N-1>

<Anything the previous close-out listed as deferred.>

## Intended features (living list)

> Canonical, continuously-clarified list of what this release will build.
> Status: 🔵 idea · 🟡 partially specified · 🟢 clarified (ready to graduate into a spec).

### Feature <n> — <name> <status>

**One-line goal.**

**Target spec:** `../specs/F<n>_<slug>/spec.md` (or "not yet allocated")

<Detail written to be implementation-ready: concrete data flow, file paths, reuse
targets.>

---

## Discussion log

### YYYY-MM-DD — Session 1: <topic>

**Trigger:** <what prompted this session>

<Findings, options weighed, what was rejected and why. Rejections are worth as much
as decisions — they stop the next session re-proposing them.>

---

## Candidate backlog

<Ideas not scheduled. Fine to leave here indefinitely; that is what this tier is for.>

## Open questions (to revisit)

- <question — and which decision it blocks, if any>

## Decisions log

> Append-only. Each entry: date, session, decision, and the reasoning that makes it
> re-checkable later. **At release close, anything here that still binds must be
> promoted** into a spec, a constitution amendment, or `../specs/vision.md` —
> otherwise it freezes with this file and is lost.

- YYYY-MM-DD (S1): <decision> — <rationale>
