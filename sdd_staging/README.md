# `sdd_staging/` — prepared SDD material, NOT yet merged

> ⚠ **Nothing in this directory is live.** It is drafted here because the constitution,
> the specs and `CLAUDE.md` are being edited in **another session** and must not be
> touched from this one. Every file below is written so it can be **pasted into its
> destination** once the main codebase settles.
>
> **Opened:** 2026-09-09 · **Owner decision required before any merge.**
> **Nothing here governs anything.** The `PreToolUse` gate does not see this directory,
> and that is correct — these are drafts awaiting the fund manager's approval.

---

## The merge manifest

Work top to bottom. Each row is one paste.

| # | Staging file | Destination | Kind | Blocked on |
|---|---|---|---|---|
| 1 | [`PG-11_citation_discipline.md`](PG-11_citation_discipline.md) | `sdd/specs/constitution.md` → new §2 entry after `PG-10` | **Constitution amendment** | ★ Fund-manager approval (§5.4: amend in its own change, with rationale) |
| 2 | [`venue_policy.md`](venue_policy.md) | `.claude/skills/lit-search/references/venues.md` | Skill reference — ★ **34 venues across the 5 target fields, the ranking methodology, and the ML-in-finance trap** | Nothing — but `PG-11` cites it, so merge together |
| 3 | [`brainstorm_template_addendum.md`](brainstorm_template_addendum.md) | `sdd/design/_templates/brainstorm.md` → append the two sections | Template patch | `PG-11` landing first |
| 4 | [`decisions.md`](decisions.md) | `sdd/design/rel<N>_brainstorm.md` → Decisions log | Decisions-log entries | The open release being known |
| 5 | [`source_evaluation.md`](source_evaluation.md) | `docs/lectures/` — folds into `L4-6` §6.3 | Study material / evidence | Nothing. Merge any time |
| 6 | *(not yet written)* `skill_lit_search/` | `.claude/skills/lit-search/` | Skill (markdown only) | Step 1–2; and a Tier-0 run to know what it should say |

⚠ **`ownership.yaml` needs no change.** Nothing here governs a path under `src/`.
That is the point — see `L4-6` §6.8.

---

## The build plan

Restated from `L4-6` §6.10, now with the staging step made explicit.

| Phase | Action | Code? | Status |
|---|---|---|---|
| **A** | Draft `PG-11` + venue policy + template patch | none | ✅ **done, staged here** |
| **B** | Fund manager reviews `PG-11`; approve, amend or reject | none | ⏸ **awaiting review** |
| **C** | Merge rows 1–5 into the live tree once the other session lands | none | ⏸ blocked on B and on the codebase settling |
| **D** | Write the `lit-search` skill from what Phase E actually needed | none | ⏸ |
| **E** | ★ Run **Tier 0** on one real question from the next release | none | ⏸ **can start now — needs nothing above** |
| **F** | Decide on `tools/litsearch.py` — only if a named Tier-0 search failed | ~200 lines | ⛔ gated by the §6.6 stop rule |

★ **Phase E is not blocked by anything in this directory.** The staging work is about making
the *rule* binding; the *search* can be run today.

## The five target fields

Fixed 2026-09-09, and the venue policy is scoped to exactly these:

**quant · finance · macroeconomics · applied mathematics (in finance only) · applied AI/ML (in finance only)**

⚠ The parenthetical *"in finance only"* on the last two is load-bearing. General applied
mathematics and general machine learning are out of scope — they are enormous fields whose
top venues would swamp the list and whose results mostly do not transfer.

★ **Sizing:** ~34 venues on the *filter* list (what a topical search may return), of which
only **5–6** are on the *scan* list (what gets browsed). See `venue_policy.md` §3 for why
those are two different numbers.

## Code forecast

**Phases A–E are entirely markdown.** The only code ever contemplated is one file,
`tools/litsearch.py`, doing cross-source DOI dedup and a result cache — and only after a
named Tier-0 search has actually failed without it. `tools/` is not in `ownership.yaml`,
so it stays ungoverned, alongside the existing `convert_filing.py` / `golden_replay.py`.

## Merge checklist

- `[]` Other session's work on `sdd/` and `src/` is committed and settled
- `[]` `PG-11` approved by the fund manager (or amended, and this file updated to match)
- `[]` Confirm `PG-11` is the next free `PG` number — ⚠ re-check against the live
      constitution at merge time; the other session may have claimed it
- `[]` Rows 1–5 pasted; this directory deleted in the same change
- `[]` `docs/lectures/README.md` updated if `source_evaluation.md` lands as its own file
