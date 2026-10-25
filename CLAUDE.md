# Collective Investment AI Assistant — working agreement

This repo is **spec-driven (lean SDD)**. The specs are the source of truth; the code
is downstream of them. If code and spec ever disagree, one of them is a bug — say so
rather than quietly picking a side.

All SDD material lives in **`sdd/`**: `sdd/specs/` is authoritative and permanent,
`sdd/design/` is the release-scoped brainstorm tier, `sdd/blueprints/` records what
the code does and why (per domain, once code exists), `sdd/archive/` is frozen
historical record. Map: `sdd/README.md`.

## Read before you write

- `sdd/specs/vision.md` — what this project is building. Read it before proposing or
  designing anything.
- `sdd/specs/constitution.md` — the non-negotiable rules every spec and every change
  must respect: principles, invariants, data contracts, test tiers, change process.
- The spec that governs the file you are about to touch — the mapping lives in
  `sdd/specs/ownership.yaml`.

## What this project is

A single-machine investment analysis system that can **explain and defend every
recommendation it makes — and measure whether any part of it actually helps.** Two
purposes, in a deliberate order: (1) a real investment tool the fund manager acts on
with his own capital; (2) a career portfolio piece for an AI-engineering role
transition around May–June 2027. `PG-2`: where they conflict on a number someone
would trade on, purpose 1 wins.

⚠ **This repo will absorb `../ai-investment-pipeline` and retire it** (vision §3).
Until then, that repo stays authoritative for its own domains — inherited analytical
logic is changed *there*, not here. This repo owns the platform layers only, and its
tree must stay a **superset** of the pipeline's so the absorption is a merge and not
a restructuring (`PG-8`).

**The seat model is this repo's own** — nine seats, numbered 1–9 (vision §3). Upstream
`L0` §1.5 numbers five. Never carry a seat number between the two repos without saying
which model it belongs to.

**Current state (2026-10-20):** **15 specs 🟢 approved — 199/199 ACs green, plus `F12` quant core
at 35/38 (3 vacuous)**, with 19 governed path groups in `ownership.yaml`. The pipeline is absorbed: `src/` is one tree of 15 domains (~370
modules), and the suite stands at 2,785 pass with 1 deliberate red (`J-07`). ★ **D-04 is CLOSED as *functionally
complete, skill unproven*** (Victor, 2026-10-11 — F12 `D16`, MT-68): the gates stay measurements, no threshold moves;
fit 4 (`sha256:8200ada7…`, walk-forward t 2.51) is refused and **designated** to rank the card, labelled (MT-67); the
shadow trial runs frozen on it (next `record`/`score` on or after 2026-11-06); no more fits on 2016–2026 unless Victor
asks. Operator's page: `src/models/README.md`. ✅ **The card ran live with the model on 2026-10-20** (`…-c04583`: 508 names, #1 MRNA, not actionable) after four defects found by that run were fixed (`DX-170`…`DX-173`); PSKY and WBD left the universe (delisted). **D-01 in progress — `F13` 🟢 built 2026-10-20 (18/18; ✏ 2026-10-21 `D13`: the daily card READS the nominee's thesis, or says "no thesis — no peer set"):**
`python tools/thesis_for.py TICKER --as-of DATE [--dry-run|--fetch-inputs]` chains extraction → Stage A → B–D → checks, run ids as
arguments, resumable (`.state/thesis_for/`); MU only. The $0 replay of 2025-06-26 passed; ★ **MU as of 2026-10-20 → SELL · Medium** (2026-10-22, `run-2026-10-22T004557-mu-thesis`, 4 falsifiers NO_DATA until Q1 FY2027) — but it cost ≈4.1M input tokens and two subscription session-limit stops (`DX-181`…`DX-183`). **Next (hand-over `_TEMP_handover_2026-10-21.md`): ① cut a thesis's cost · ② D-05 risk on the card (blocked on Victor: R3/`RK-30`, fresh BMO exports) · ③ more peer sets.** The analysis layer has 32/35
prompt blocks declared, every one run live and verified (`E-14` `J-18` `J-19` deferred by decision), and four
MU theses produced (k=1 each; SELL → HOLD → SELL → SELL, all falsified or on course to be). ⊘ AMD thesis
skipped; falsifier improvement waits for real runs. Go-live prepared in `sdd/design/rel1_design/L9-go-live-checklist.md` — Victor 2026-10-05: **card only, theses on demand by his manual command; paid Anthropic API stays OFF; no budget yet** (the old 3-call daily `thesis` path was removed 2026-10-05, `DX-153` — restore patch in `sdd/archive/`). ⊘ **The golden-case programme is CLOSED**
(`L8` §9, 2026-10-01): 53 live cases kept and maintained, **no new golden cases**. Judgement quality is
measured by falsifiers and rule checks. **Live progress is `sdd/design/rel1_design/L3-build-sequence.md`
§2.1**; the golden-case programme is `L8-golden-case-retrospective.md`.

⚠ `PG-1`, which blocked all implementation, was **retired 2026-09-02**: verification moved to the
fund manager, done manually against real run outcomes. **Implementation is gated by spec
approval 🟡→🟢** — and by the `PreToolUse` gate, which is unaffected and still refuses an edit to a
governed path until this session has read the governing spec.

## Skills

- **`fmp-api`** — what Financial Modeling Prep can and cannot serve, **measured** against the
  real Starter key (156 `/stable/` endpoints probed 2026-08-15), not read from FMP's docs.
  Carries the full endpoint catalog, the plan gates (`402` vs `404`), the point-in-time
  hazard classes, and the five traps that have already caused measured defects — including
  ⚠ **FMP guesses the quarter and got Micron wrong by 71 %**. Load it before designing or
  coding any data fetch.
- **`sdd-implement`** — the spec → failing test → code → traceability loop.

## Enforcement

A `PreToolUse` hook (`.claude/hooks/sdd_gate.py`) denies `Edit`/`Write` to any path
`sdd/specs/ownership.yaml` marks as governed, until this session has actually **Read**
the specs that govern it. The ledger is per-session — a new conversation must read
them again, because context does not carry over and neither should the permission.
It fails open (allows the edit) if it errors, and prints a loud warning when it does.

## The loop

1. **Diverge** — brainstorm in `sdd/design/rel<N>_brainstorm.md`.
2. **Converge** — record the decision in that file's Decisions log.
3. **Graduate** — copy `sdd/specs/_templates/spec.md` → `sdd/specs/F<n>_<slug>/spec.md`
   once its acceptance criteria can be written.
4. **Wire** — add the spec's globs to `sdd/specs/ownership.yaml` in the same change.
   A spec with no globs is unenforced.
5. **Implement** — failing test per `AC-<n>.<k>` first, then the smallest code that
   passes. Fill the spec's traceability table.
6. **Verify** — run the whole test suite, not just the new test.

A task is done only when its AC has a passing test in the right tier (constitution §4).

## House rules

- Never `git commit` without review.
- Never hardcode a credential; read from the environment.
- Fail loud, never silent — a degraded input should raise, not emit a
  plausible-looking default.
- **LLM calls during development go through headless Claude Code on the subscription, not the
  Anthropic API** (Victor, 2026-10-01). That covers golden-case building, test runs, live debugging,
  re-records — everything. The **API key is reserved for the real daily runs** of the finished
  pipeline. Consequences that must be kept:
  - Every recording made this way says so — `transport: claude_code` in its trace — and its cost is
    **notional**, never added to the spend figures. Spend means API dollars only.
  - It is the same model behind a different envelope (Claude Code's framing, no `temperature` /
    `max_tokens` control, `--effort` in place of the thinking budget, `--json-schema` in place of
    strict tool schemas). A golden case signed on a `claude_code` recording therefore grades the
    prompt, **not the production transport**. Before daily runs go live, an API spot-check of a
    sample of signed cases is required (paid, approved per call).
  - Built 2026-10-01: `src/shared/llm/claude_code_transport.py` (spec: `L2-shared-infrastructure`
    §5.7, GW-24…29). It is the **default**; `CIA_LLM_TRANSPORT=anthropic_api` selects the paid path,
    and that still needs per-call approval. Every runner prints which transport is live.

These are starting defaults, not settled decisions — revise this file freely as the
project's actual working agreement takes shape.
