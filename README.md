# Collective Investment AI Assistant

A single-machine investment analysis system that can **explain and defend every
recommendation it makes — and measure whether any part of it actually helps.**

> ## ⚠⚠ Status disclosure — read this first
>
> **The ranking model behind this system sits at walk-forward IC 0.0203,
> *t* = 1.42, and is refused by its own significance gate.** Nothing here is a
> claim that the strategy works.
>
> The **daily run is suspended** until end-to-end validation is complete.
>
> ★ This disclosure is required by the project's own constitution (`PG-10`):
> *no output may present a recommendation as actionable, or publish a performance
> figure, unless the model behind it has passed its own promotion gates — or the
> output states plainly that it has not.*

---

## What this is

| | |
|---|---|
| **Specs** | 11 feature specs, **148 acceptance criteria**, all 🟢 approved |
| **Code** | ~38,000 lines across 15 domains |
| **Tests** | **1,570**, of which 41 are dormant by design (see below) |
| **Decisions** | **50** recorded with the options that were **rejected**, and why |
| **Findings** | **13** discrepancies logged before being fixed |

It is **spec-driven**: `sdd/specs/` is the source of truth and the code is
downstream of it. A `PreToolUse` hook refuses an edit to a governed path until the
governing spec has been read in that session — per session, because context does
not carry over and neither should the permission.

## Start here

| If you want to | Read |
|---|---|
| ★ **Judge the engineering** | [`docs/essays/E1-what-the-process-caught.md`](docs/essays/E1-what-the-process-caught.md) — thirteen things the process caught that review did not |
| Understand the goal | [`sdd/specs/vision.md`](sdd/specs/vision.md) |
| Understand the rules | [`sdd/specs/constitution.md`](sdd/specs/constitution.md) |
| See *why* a decision went the way it did | [`sdd/questions.md`](sdd/questions.md) — 23 questions, answers, and rejected options |
| See what went wrong and when | `sdd/design/rel1_design/L3-build-sequence.md` §6 |

## Running it

```bash
pip install -e ".[dev]"
python tools/check_all.py      # every guarantee, one command
```

⚠ **`src` is an implicit namespace package.** Do not add `src/__init__.py` — a
regular package ends the import scan, and the layout depends on it.

## ⚠ What is deliberately not working

Stated because a project that lists only its successes is not evidence of
judgement.

- **41 external-truth tests skip everywhere.** They verify derived cash against
  real broker statements, which are correctly excluded from version control. They
  are dormant, not passing.
- **The deliberation experiment (`F7a`) has never run.** The instrument and its
  pre-registered kill rule exist; the measurement does not.
- **The evaluation harness has no golden set.** Establishing expected values is a
  human judgement and is deliberately not automated — seeding them from the
  system's own output would certify the system against itself.
- **~38,000 inherited lines carry one characterization test.**

## Licence

**Source-available. All rights reserved.** See [`LICENSE`](LICENSE).

⚠ This is **not open source**: the code is readable, and no rights to use, modify
or distribute are granted. Calling it open source would be a category error a
technical reviewer would notice.

Dependency licences are audited in
[`sdd/design/rel1_design/L5-dependency-licence-audit.md`](sdd/design/rel1_design/L5-dependency-licence-audit.md)
— no copyleft in the dependency set. ⛔ One entry (`anthropic`) is **unverified**
and must be confirmed before any publication.
