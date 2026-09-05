# What the process caught

> **Architecture essay — `MS-9.5`.** Not SDD material; governs nothing.
> **Audience:** a reviewer deciding whether the engineering judgement here is real.
>
> ⚠⚠ **Status disclosure, first because `PG-10` requires it:** the ranking model
> behind this system sits at **walk-forward IC 0.0203, *t* = 1.42**, and is
> **refused by its own significance gate**. Nothing in this document is a claim
> that the strategy works. It is a claim about how the *system* was built, and the
> most interesting evidence is a list of things that were wrong.

---

## 1. The thesis

Most write-ups describe a finished architecture as if it were designed that way.
This one describes **thirteen occasions on which the design was wrong**, how each
was found, and what it cost — because the recurring shape of those errors is the
actual finding, and it is more transferable than the architecture.

The system is a single-machine investment platform: eleven feature specs, 148
acceptance criteria, ~38,000 lines across 15 domains, 1,570 tests. It was built
spec-first under a lean SDD process with a `PreToolUse` hook that refuses an edit
to a governed path until the governing spec has been read in the session.

★ **The claim is narrow and I want it to stay narrow:** the process caught
defects that review did not, repeatedly, and the *kind* of defect it caught was
consistent enough to name.

---

## 2. The shape that recurred: a check that stops checking

Nine of the thirteen findings are the same failure. A rule exists, it passes, and
it has silently stopped examining anything.

| | What went quiet | How it was found |
|---|---|---|
| `DX-3` | An architecture rule (`SI-1`) scanned a directory that had moved. **It examined 0 files and reported `14 passed`.** | Planting a violation |
| `DX-9` | A filesystem-scanning ban asserted **absence**, so a shrinking tree satisfied it trivially. Two whole domains stopped being covered. | Its sibling test happened to assert *presence* and failed loudly |
| `DX-10` | An absorbed test enforced upstream's **five-seat** vocabulary on a repo with **nine** seats — the exact thing the working agreement forbids | A merged test run |
| `AC-1.7` | A contract suite passed vacuously because every fixture was stateless | Mutation testing |
| `AC-2.9` | Two code paths, one test. A credential in the un-tested path would have been written verbatim | Mutation testing |

> ★★ **An assertion that something is ABSENT gets easier to satisfy as the thing
> it scans gets smaller.** That sentence explains most of the list. A rule scoped
> to a directory is a rule with an expiry date nobody set.

**The instrument that found several of them was the same one:** deliberately
break the behaviour and check that the named test goes red. Well over a hundred
such mutations were run across the build. **Five survived**, and each was a real
coverage hole — a vacuous contract suite, a redaction path with no test, a
recorder that could swallow the exception it was recording, an outcome lookup
that ignored the key it looked up by, and a clause that only a
leaks-on-first-call fixture could expose.

⚠ **A green suite written by the same author as the code is evidence of
agreement, not of correctness.** That is the whole argument for the technique.

---

## 3. The second shape: a list that was complete when written

An absorption — moving a domain between repositories — was supposed to move
**one** thing. It moves six, and the list grew three times:

```text
   DX-3   code · tests · ownership globs · the rules that scan the path
   DX-8   + config/                    (a FileNotFoundError, loud)
   DX-13  + dependency declarations    (silent: the dev machine had them)
```

★ **Each addition was found by something that was not looking for it.** `DX-13`
surfaced during a *licence* audit: `lightgbm` had three import sites and had
**never been declared in either repository**. Nothing failed, because every
machine that ran the code already had it installed.

> ⚠ The generalisable point is not "write better checklists". It is that a
> checklist is a hypothesis about what a change touches, and the honest way to
> test it is to run **unrelated** checks afterwards.

---

## 4. The third shape: the cheap answer and the expensive one

Two decisions turned out to have economics that pushed the wrong way.

**`F7a` — the kill rule.** The gate that decides whether an agent-deliberation
feature survives compares its revision rate on *true* versus deliberately *false*
challenges. Computing the required sample size gave:

| verdict | n per arm |
|---|---|
| `KEEP` (ratio ≤ 0.33) | **~23** |
| `DELETE` (ratio ≥ 0.67) | **~99** |

⚠⚠ **The cheap verdict is the one that preserves the feature.** For a gate whose
purpose is to kill things, budget pressure points at exactly the wrong answer.
The response was to pre-register both bands and run the cheap test first, and to
write down that widening the expensive band to save money is *"a threshold chosen
after seeing the cost"* — the same failure as choosing one after seeing the data,
one step earlier.

**`F5` `D2` — who establishes a golden value.** The tempting option was to seed
the evaluation harness's expected answers from the system's own best output. It
gives more cases and a permanently green suite, and it **certifies the system
against itself**: any regression silently becomes the new expected value. It is
refused in code, not in a comment, because it is the option that looks better.

---

## 5. What was decided against the grain

Three decisions cost something and were taken anyway.

**Replay's verdict is named `REPRODUCED`, not `IDENTICAL`.** Replay substitutes
recorded model responses; it establishes control flow, not that a model would
answer the same way again. A field named *identical* travels into reports and
over-claims. The verdict now carries a literal `scope` string so the limit moves
with the value.

**The outcome study measures the recommendation, not the portfolio.** A
deliberation's *pre* arm was never acted on, so its realised outcome does not
exist. Both arms are scored as paper returns — symmetric and weaker — rather than
comparing an acted arm's realised outcome against an unacted arm's paper one.
⚠ The asymmetric version *flatters the feature*, and it looks like using the best
available data.

**Two acceptance criteria were moved out of a milestone rather than built.** The
explainability spec called claim-binding *"the highest value-per-unit-work item
in the project"* and said to wire it. The upstream record said the fund manager
had already deferred it: *"needs mathematics, not plumbing."* Building it would
have produced a grounding number nobody could defend, underneath an explanation
layer whose entire purpose is faithfulness.

---

## 6. What is not true here

⚠ Stated plainly, because a write-up that only lists successes is not evidence of
judgement.

- **The signal is unestablished.** IC 0.0203, *t* = 1.42, refused by its own gate.
- **`F7a` has never run.** The instrument exists; the experiment does not. So there
  is no measurement of whether deliberation helps — only a pre-registered plan for
  making one.
- **The evaluation harness has no golden set.** Its machinery is tested and its
  expectations are empty, because establishing them is a human judgement.
- **41 external-truth tests are dormant.** They check derived cash against real
  broker statements, correctly absent from version control — so after the merge
  they skip *everywhere*, including on the machine that holds the data. ⚠ The
  fresh-clone check consequently became identical to the normal run, which is
  exactly why nothing looked wrong.
- **~38,000 inherited lines carry one characterization test.** The rest of that
  behaviour is frozen only by tests that were written to assert it is *correct*,
  which is a different claim.

---

## 7. What I would keep

1. **Mutation-test anything you and the tests both wrote.** Six real holes, and
   every one looked green.
2. **Prefer the ten-line experiment to the paragraph of reasoning.** A plan
   asserting that an import works is a hypothesis until something imports.
3. **Make the rule refuse the tempting option in code.** A comment saying "do not
   seed golden values from the system" is advice; a `CircularGoldenValue`
   exception is a constraint.
4. **Record the rejected options, not just the decision.** Fifty decisions carry
   theirs. Twice a later decision was reversed by re-reading why the earlier one
   had gone the other way.
5. ★ **Let a derived rule contradict you.** The phase order derived from coverage
   economics rejected a worked example in its own spec, because that example had
   a later phase configuring an earlier one. The rule was right.
