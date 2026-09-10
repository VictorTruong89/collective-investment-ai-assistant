# Brainstorm template patch

> **Destination:** `sdd/design/_templates/brainstorm.md` — append both sections below.
> **Blocked on:** `PG-11` landing first. Without it this is a suggestion, not a rule.
> **Drafted:** 2026-09-09.

## Patch 1 — add to the `### Feature <n>` block

Insert directly beneath the existing `**Target spec:**` line:

```markdown
**Methods this feature turns on** — `PG-11` applies to every row.

| Method | Primary source (DOI) | Regime established in | Limiting / dissenting work | Venue tier |
|---|---|---|---|---|
| <name> | <doi> | <market · period · universe · cost assumption> | <doi, or "no dissent found"> | 1 / 2 / 3 |

> ⚠ **"No dissent found"** means a search was run and returned nothing. It is not a synonym
> for "undisputed", and it may not be written unless the search actually happened.
```

## Patch 2 — add as a new top-level section, before `## Decisions log`

```markdown
## References

> `PG-11`. Primary sources only — a survey that cites the result is not the result.
> Venue tiers per `.claude/skills/lit-search/references/venues.md`.
> ⚠ This section stays in the design tier. **The spec that graduates from this file carries
> no bibliography** — it states what must be true; the argument lives here.

- <Author>, *<Title>* (<Venue> <Year>) — DOI: <doi> — **Tier <n>**
```

---

## Note for the reviewer

Patch 1 is a table rather than prose deliberately. Prose lets a method claim be made without
its regime; a table with an empty cell is **visibly** incomplete, which is the whole mechanism.
The venue-tier column exists so `PG-11` req. 4 is discharged at the point of writing rather
than reconstructed at review.

★ Neither patch is enforceable by a hook — see `PG-11`'s *Enforcement* paragraph. They make the
obligation visible at the moment of writing, which is the most a template can do.
