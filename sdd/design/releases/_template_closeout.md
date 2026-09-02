# Release <N> — Close-out

> **SDD role: `design/` tier — NON-AUTHORITATIVE, historical.** One page. What
> shipped, what the acceptance-criteria scoreboard said on the day, what was
> deferred and to where.
> **Status:** CLOSED · **Opened:** YYYY-MM-DD · **Closed:** YYYY-MM-DD

<!--
HOW TO USE THIS TEMPLATE (delete this comment block in the real file):
- Copy to  sdd/design/releases/rel<N>_closeout.md  when the release closes.
- Keep it to ONE PAGE. This is not an as-built document — the specs and their
  traceability tables are the as-built record, continuously. A second narrative
  copy only drifts.
- Work the checklist at the bottom before marking the release closed.
-->

---

## What shipped

| Spec | Feature | ACs green / total | Code |
|---|---|---|---|
| F<n> | <name> | k / m | `<path>` |

**Test suite at close:** <N> passing.

## What did not ship, and where it went

| Item | Why deferred | Now tracked in |
|---|---|---|
| <AC or feature> | <reason> | `rel<N+1>_brainstorm.md` / spec §7 open question / vision §<s> |

## Decisions promoted out of the brainstorm

> Anything from the rel<N> decision log that still binds, and where it now lives.
> Everything **not** listed here freezes with the brainstorm and stops being
> authoritative.

| Decision | Promoted to |
|---|---|
| <decision> | `../../specs/constitution.md` / `F<n>` §<s> / `vision.md` §<s> |

## What we learned (worth carrying forward)

<Bugs that only real data found, assumptions that proved wrong, process that
worked or didn't. This is the section a future session actually benefits from —
be specific, name the incident.>

---

## Close-out checklist

- [ ] Binding decisions promoted out of the brainstorm (table above)
- [ ] Spec traceability tables current; no row claims ✅ for a test that does not exist
- [ ] `../../specs/README.md` spec index refreshed (counts match the suite)
- [ ] `../../specs/ownership.yaml` globs cover every path this release made spec-governed
- [ ] Session references in specs written as `rel<N> S<k>`, not bare `Session <k>`
- [ ] `rel<N>_brainstorm.md` header marked **FROZEN**
- [ ] `rel<N+1>_brainstorm.md` opened from `../_templates/brainstorm.md`
- [ ] Full suite green
