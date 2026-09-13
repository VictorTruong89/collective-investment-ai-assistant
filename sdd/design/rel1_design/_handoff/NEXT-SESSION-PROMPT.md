# ⏳ Paste-ready prompt for the next Claude session

> Copy everything inside the fence below into a **fresh** Claude Code session started in
> `~/Workspace/collective-investment-ai-assistant`. Temporary — delete with the rest of `_handoff/`.

```text
You are continuing work on collective-investment-ai-assistant, a spec-driven (lean SDD) repo. A long
previous session ended at a clean breakout point. Do NOT re-derive its history — it is summarised.

STEP 1 — read, in this order, before doing anything else:
  1. sdd/design/rel1_design/_handoff/HANDOFF-2026-09-12.md   (state, constraints, next task, traps)
  2. CLAUDE.md
  3. sdd/specs/constitution.md                               (use the Read tool — the SDD gate only
                                                              credits a full Read)
  4. sdd/design/rel1_design/L3-build-sequence.md §2.1 (the headline box) and §6 rows DX-80…DX-88
     only. Do not read the whole L3 file; it is very large.

STEP 2 — verify the handoff is still true (free, no network):
  - git status --short         (expect ~25 uncommitted paths + 3 deletions I must NOT touch)
  - python3 -m pytest -q        (expect 2,006 passed, 6 skipped)
  - PYTHONPATH=. python3 tools/check_all.py   (expect ALL CHECKS PASSED)
  If any of these differ, STOP and tell me what differs before building anything.

STEP 3 — the task: declare the seven E-blocks whose evidence the v2 rubric levels cite:
  E-04 · E-06 · E-07 · E-09 · E-10 · E-12 · E-13
  Follow HANDOFF §3 exactly: its recipe, and its per-block PRE-FLIGHT (does an item ask the model to
  COMPUTE? does it need non-filing evidence? is every id X-01-checkable?). Do the pre-flight for ALL
  seven first and report the results to me BEFORE declaring any — if a block asks the model to
  compute, I decide whether to change its prompt text.

Rules that bind this session (verbatim from me; also in HANDOFF §1):
  - Never git commit or git add. I commit manually.
  - Ask my approval before EVERY action that spends money (every live API call). Dry-runs are free.
  - Brief and concise answer first, detail after.
  - sdd_staging/ is isolated — leave it untouched. Do not restore the 3 working-tree deletions.
  - D2: never establish, edit or rebaseline a golden value; prepare cases unsigned in *.pending.yaml.
  - Never hardcode a credential. The API key is in .env: `set -a; . ./.env; set +a` before --live.

Working method that has paid off repeatedly: measure before specifying; mutation-test every new guard
AND its caller; record a DX row in L3 §6 (finding, options, chosen, rejected, why) before or with
the fix; never treat an output-token count equal to the cap as success — check stop_reason.

When the seven are declared, tested and green: update L3 (§2.1 box, block census in §2.1c, DX rows),
tell me what changed, what it cost (should be $0), and what needs my decision next.
```
