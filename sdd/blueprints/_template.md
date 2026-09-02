# Blueprint — <Domain Name>

> **Code:** `<path>/` · **Spec:** `sdd/specs/<spec-file>` (or `sdd/design/...` if not yet promoted)
> **Status:** written <date> against commit `<sha>` · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠ **This describes the CODE, not the spec.** A sentence here that would still be
> true if the code were rewritten differently belongs in the spec (DR-1).

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| | | | |

---

# 1. What this domain does, in one paragraph

Plain language. What goes in, what comes out, what it is responsible for being
right about.

# 2. The objects and how they flow

```text
   <ASCII: the real call path — the objects as they are NAMED IN THE CODE,
    not as the spec describes them. Where the names differ, say so and why.>
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| | `file.py::Class` | | | |

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | | `file.py::fn` | ★ what forces this position — a rule ID, a data dependency, or a decision | |

# 4. ★ The mathematics

**One entry per formula. QUOTE from the code — never re-type it (DR-3).**

### <name of the quantity>

| | |
|---|---|
| **Implemented in** | `file.py::function`, lines n–m |
| **Formula** | ```python\n<verbatim from source>\n``` |
| **Units** | inputs and output |
| **Domain / range** | what inputs are valid; what happens outside |
| **Why this form** | ★ DR-4. Not "because the spec says" |
| **Alternatives rejected** | ★ DR-5 — and why. If none were considered, **say that** |
| **Sensitivity** | which input moves the output most, and roughly how hard |
| **★ Worked example** | DR-6 — real input → **every intermediate** → output |
| **Known-wrong** | DR-7 — or "none known" |

# 5. The logic decisions

For each branch, threshold or ordering that could reasonably have gone another way:

| Decision | Where | What it does | Why this way | What it would take to change it |
|---|---|---|---|---|

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Range | Who reads it | Changing it affects |
|---|---|---|---|---|---|

# 7. Inputs and outputs

| Direction | Contract | Shape | Producer / consumer | What happens if malformed |
|---|---|---|---|---|

# 8. Failure behaviour

| Failure | Detected where | Behaviour | Visible to whom |
|---|---|---|---|

# 9. What this domain deliberately does NOT do

★ Boundaries, with the module/domain that owns each.

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|

★ **"None known" must be written explicitly if true.**

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | spec traceability table |
| 2 | ★ Break it and confirm red | which line to break, which test should fail |
| 3 | The worked example (§4) reproduces | how to run it |
| 4 | ★ Checked against external truth? | which reality probe, or **"none — self-consistency only"** |

# 12. Cross-references

| Document | Relevance |
|---|---|
