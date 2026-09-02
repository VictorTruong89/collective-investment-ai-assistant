# `blueprints/` — what the code actually does, and why it does it that way

> **Tier:** permanent, **per domain**, lifetime = the code's lifetime.
> **Written:** when a domain's code is complete, and amended when its logic changes.
> **Audience:** whoever is reviewing, debugging, or returning after time away — and
> the next agent that has to change something without breaking a decision it
> cannot see.

---

# 1. Why this tier exists

A spec is a **constraint set**, and it deliberately underdetermines the code — many
implementations satisfy it. The blueprint records which one was built and why that
one. That content exists nowhere else.

⚠ **The collision with `sdd/README.md`, stated openly.** `sdd/README.md` forbids a
release-scoped "as-built" document, because it restates the specs and drifts
against them. A blueprint is different: it is **per domain**, describes **what the
code does** (not what the system does), and drifts against the **code**, not the
specs — which is mechanically checkable.

> ⚠ **The rule that keeps them apart (DR-1): a sentence that would still be true if
> the code were rewritten differently belongs in the spec, not here.**

---

# 2. The rules

| ID | Rule |
|---|---|
| **DR-1** | ★★ **Describe the code, never the spec.** The test: would it still be true if the code were rewritten to satisfy the same spec? If yes, it belongs upstream. |
| **DR-2** | ★★ **Every claim carries a pointer** — `file.py::function`, a config key, a contract ID. A blueprint sentence without a pointer cannot be checked and will rot silently. |
| **DR-3** | ★★ **A formula appears ONCE, in the code, and is QUOTED here with its pointer — never re-typed.** A re-typed formula is a second implementation that can disagree with the first. |
| **DR-4** | ★★ **"Why" is mandatory, and *"because the spec says so"* is not a why.** This explains why this construction among the several that would have satisfied the spec. |
| **DR-5** | ★★ **Record what was CONSIDERED AND REJECTED, with the reason.** Often the most valuable line — the only way a later reader tells a *choice* from a *default nobody examined*. |
| **DR-6** | ★ **One worked numerical example, traced end to end** — real input, every intermediate value, the output. |
| **DR-7** | ★ **Known-wrong is a mandatory section.** An empty section must say "none known" explicitly — a missing section reads as "nothing to report", and those are different claims. |
| **DR-8** | ★ **The "why" is APPEND-ONLY; the "what" is regenerated.** Pointers, formulas and configs are refreshed and checked; every decision entry is dated and never edited. |
| **DR-9** | **Where a number came from a measurement, name the measurement and its sample.** A setting and a decision look identical unless you write down where the number came from. |

---

# 3. How this tier is kept honest

A `PreToolUse` hook cannot enforce this — "the domain's code is complete" is not a
moment a hook can observe. The enforceable point is CI, if/when this project adds
a structural audit tool: existence (every domain with code has a blueprint),
pointer validity (every named `file.py::function` exists), freshness (flagged, not
failed, when older than the last logic-bearing commit).

---

# 4. Layout

```text
   sdd/blueprints/
   ├── README.md          this file — the tier and its rules
   ├── _template.md       copy this to start one
   └── <domain>.md        one per domain that has code
```

★ **One per domain, not one per release.** The domain is the unit that has an
owner, a spec, a directory and a set of invariants — and it is the unit you will
be debugging.
