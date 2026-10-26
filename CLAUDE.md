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

**Current state (2026-10-25):** **16 specs 🟢 approved** (`F14` 19/19, `F13` 22/22, `F10` 25/25, `F12` quant core 35/38
with 3 vacuous; 261 traceability rows), 20 governed path groups in `ownership.yaml`. `src/` is one tree of 15 domains (the
pipeline is absorbed); suite **2,954 pass, 1 deliberate red (`J-07`)**. Live progress: `sdd/design/rel1_design/L3-build-sequence.md`
§2.1; go-live state per domain: `L9-go-live-checklist.md`.
- ★ **D-04 (ranker) CLOSED — *functionally complete, skill unproven*** (F12 `D16`, MT-68): fit 4 (`sha256:8200ada7…`) is
  refused but **designated** to rank the card, labelled; the shadow trial runs frozen on it — next `record`/`score` on or
  after **2026-11-06** (Victor's); no retrain or new fit unless Victor asks. Operator's page: `src/models/README.md`.
- ★ **D-01 (thesis) CLOSED for now — *functionally complete, accuracy & reliability unproven*** (F13 `D16`, Victor
  2026-10-25). `python tools/thesis_for.py TICKER --as-of DATE [--dry-run|--fetch-inputs]` runs the whole chain
  (8 extractions → 9 Stage-A → 13 B–D → checks), resumable, on the subscription only. Subjects: MU (`memory_v1`), SNDK
  (`memory_v2`), MRNA (`vaccines_v1`, ⛔ blocked — `DX-190`: no path for a pre-profit / single-segment / debt-free
  company). Theses: MU ×5, **SNDK 2026-10-20 → SELL · Medium-High** (≈ $33.9 notional, against MU's ≈ $58.5 before the
  cache fix). All `k = 1`, so no card is actionable on one. The revisit list is in F13 `D16`.
- **The daily card** (D-08 → D-09) is run by hand (no timer, O1); it ran live 2026-10-20. It reads the nominee's thesis
  or says "no thesis — no peer set / not yet written", and shows D-05's behavioural flags (`RK-40`) beside an exposure
  pass that stays `UNCHECKED` (R1: CAD/CDR positions cannot be priced on the FMP plan). Paid Anthropic API **OFF**; no budget.
- ⊘ **Golden-case programme CLOSED** (`L8` §9): 53 cases kept, no new ones; judgement quality is measured by falsifiers
  and rule checks.
- ★ **D-11 reads BMO's holdings export** (`L1-recording` §8a, RC-70…RC-78, 2026-10-25): `Holdings_<ACCOUNT>.csv` in
  `.state/broker/bmo_investorline/` gives BMO's reported price, market value, cash and balance — self-checked, reconciled
  against the transaction history (RC-76). ⚠ Line 1 is the REAL account number: never kept (RC-78). Valued: `RESP_1`
  13,703.62 CAD, `TFSA_2` 76,805.55 CAD (as of 2026-10-25). `TFSA_1`/`RRSP_1` have no export for 1–2 months → refused by
  name, and the book-wide figure stays `UNCHECKED` (RC-77). Not wired into the daily card's `load_books` yet.
- ★ **D-06 sizing on demand** (`F14`, 2026-10-25): `python tools/size_for.py TICKER --account ACCT --entry P [--stop S]
  [--currency CAD|USD] [--held-stop SYM=P …] [--sigma X] [--dry-run|--json]`. Capital = the reported balance; budget =
  `r_ceiling` (E·C·P·D `unmeasured`); k 1.5 labelled; σ from FMP for US listings only. ⚠ `config/portfolio_policy.yaml`
  is EMPTY: every real sizing refuses until Victor states `r_total`, `r_ceiling` and `target_positions` per account (PS-43).
  One sizing path: `src/portfolio/sizing/trade.py::size_trade` (`DX-191` fixed, F14 `D12`). Theory: `docs/lectures/L9-position-sizing-and-risk.html`.

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
