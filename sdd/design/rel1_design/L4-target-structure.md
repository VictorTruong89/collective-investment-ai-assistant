# L4 — Target repository structure

> **SDD role: `design/` tier — NON-AUTHORITATIVE.** Rationale and layout reasoning.
> **Binds nothing.** What binds is [`../../specs/constitution.md`](../../specs/constitution.md)
> `PG-8` (*the tree is a superset, always*) and `ownership.yaml`.
> **Status:** DRAFT · **Opened:** 2026-08-28 · **Source:** rel1 S1, Q1
> **Companion to:** [`../rel1_brainstorm.md`](../rel1_brainstorm.md) §G

---

# 1. The constraint this document exists to satisfy

**Decision (rel1 S1, Q1):** build the platform here, import `ai-investment-pipeline` in the
interim, **copy its `src/**` tree in once stable, then retire the old repo.**

```text
╔══════════════════════════════════════════════════════════════════════╗
║  THE ABSORPTION MUST BE A MERGE, NOT A RESTRUCTURING.                ║
║                                                                      ║
║  ★ Every inherited domain keeps its upstream path, verbatim.        ║
║    src/fundamental/  stays  src/fundamental/                         ║
║    src/quant/        stays  src/quant/                               ║
║                                                                      ║
║  ⚠ WHY THIS IS NON-NEGOTIABLE (PG-8):                               ║
║    ~34,700 LOC across 294 files import each other by absolute path   ║
║    (`from src.shared.money import Money`). Renaming ANY domain at    ║
║    absorption time rewrites imports across the whole tree, in the    ║
║    same commit as a move — and L4's migration classes forbid         ║
║    exactly that, because git records a rewrite and the review        ║
║    becomes impossible.                                               ║
║                                                                      ║
║  ★ A move commit changes ZERO bytes. That is the whole design.      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

# 2. The target tree

`★ NEW` = built in this repo · `⇐ INHERITED` = arrives at absorption, untouched.

```text
collective-investment-ai-assistant/
│
├── CLAUDE.md                       ★ working agreement
├── pyproject.toml                  ★ packaging; adds the pipeline as a dep until absorption
├── .claude/
│   ├── settings.json               ★ hooks wiring
│   ├── hooks/sdd_gate.py           ★ the PreToolUse spec gate
│   └── skills/                     ★ sdd-implement, + agent/xAI skills as they earn one
│
├── sdd/                            ★ this repo's SDD tiers (specs · design · blueprints · archive)
│
├── config/                         ⇐ INHERITED  settings.yaml, universe, tuning
├── tools/                          ⇐ INHERITED  sdd_audit.py and friends
│
├── tests/                          ⇐ INHERITED  the 1,192-test suite
├── tests_src/                      ⇐ INHERITED
│
└── src/
    │
    ├── shared/                     ⇐ INHERITED  D-00
    │   ├── money.py                ⇐ INV-5, integer minor units
    │   ├── llm/                    ⇐ the sole LLM call site (ST-5)
    │   │   └── tiers.py            ★ NEW  Opus/Sonnet/Haiku selection (pluggability L1)
    │   └── agents/                 ★★ NEW  F1 — the agent protocol layer
    │       ├── ports.py            ★ AgentPort — pure typing, no implementation (CA-3)
    │       ├── messages.py         ★ typed inter-agent message schemas (F6)
    │       ├── capability.py       ★ seat, domain, version, supported message types
    │       ├── registry.py         ★ (seat, variant) → implementation
    │       └── errors.py           ★
    │
    ├── data_engine/                ⇐ INHERITED  D-07 · 8,511 LOC
    │   ├── calendar/ contracts/ ingest/ observation/ pit/ store/
    │   ├── symbology/ universe/ validation/
    │   └── corporate_actions/      ★★ NEW  F3 — the earned agent (PG-3)
    │
    ├── feature_engineer/           ⇐ INHERITED  D-02 · neutral ground
    ├── fundamental/                ⇐ INHERITED  D-01 · 8,527 LOC
    │   ├── claims/                 ⚠ built, tested, exported — AND NEVER CALLED (AB-2)
    │   └── scorecard/              ⚠ same shape (AB-1)
    ├── quant/                      ⇐ INHERITED  D-03
    ├── models/                     ⇐ INHERITED  D-04
    ├── risk/                       ⇐ INHERITED  D-05
    ├── portfolio/                  ⇐ INHERITED  D-06
    ├── recording/                  ⇐ INHERITED  D-11
    ├── reporting/                  ⇐ INHERITED  D-09
    ├── decision/                   ⇐ INHERITED  D-12 · the meet-semilattice (PG-6)
    ├── experiments/                ⇐ INHERITED  D-10 · P7-exempt, ST-2 one-way
    │
    ├── orchestration/              ⇐ INHERITED  D-08
    │   ├── contracts/ jobs/ policy/ schedule/ state/
    │   ├── graph/                  ★★ NEW  F2/F6 — LangGraph lives HERE and nowhere else
    │   │   ├── pipeline_graph.py   ★ nodes + edges
    │   │   ├── routing.py          ★ conditional edges (variant / horizon / tier)
    │   │   ├── deliberation.py     ★ F6 — max_turns=1 is Option B, N is Option C
    │   │   └── checkpoints.py      ★ checkpoint adapter (local JSON)
    │   └── trace/                  ★★ NEW  F2 — the observability substrate
    │       ├── models.py           ★ TraceRecord, AgentTurn, GraphSnapshot
    │       ├── record.py           ★
    │       └── replay.py           ★
    │
    ├── explain/                    ★★ NEW  D-13 — F4
    │   │                           ⚠ DOWNSTREAM of the analyst firewall. See §3.
    │   ├── contracts/              ★ the explanation shape
    │   ├── attribution/            ★ reads per-domain attributions; does not compute them
    │   ├── binding/                ★ claim → evidence span (wires up AB-2)
    │   └── counterfactual/         ★ "what would have to change to flip this"
    │
    └── evaluation/                 ★★ NEW  D-14 — F5/F7
        │                           ★ the ST-2 shape: imports anything, imported by nothing
        ├── golden/                 ★ known-correct fixtures
        ├── metrics/                ★ citation rate, calibration, faithfulness
        ├── regression/             ★ fails when a PROMPT changes behaviour
        └── studies/                ★ F7 — the deliberation A/B
```

---

# 3. ⚠⚠ Why `explain/` is a peer of `decision/`, not a cross-cutting utility

The obvious design — one explainability module that reads the thesis *and* the rank_score —
is **structurally illegal**:

```text
   src/explain/  →  imports src/fundamental/   (D-01)
   src/explain/  →  imports src/quant/         (D-03)

   ⚠⚠ INV-014 / ST-9 forbid D-01 and D-03 meeting in one module.
      The firewall is the reason concurrence between the two views
      is INFORMATIVE. A module that reads both is the breach.
```

★ **Resolution — two halves, on opposite sides of the fence:**

| Half | Lives | Sees |
|---|---|---|
| **Per-domain attribution** — *"what moved MY score"* | ⇐ inside each domain, exposed via its own output contract | only itself |
| **Cross-view explanation** — *"why this recommendation"* | ★ `src/explain/`, downstream | both views, **as already-published outputs** — the same position `D-12` and `D-09` occupy |

> ★ `D-09`'s `DC-4` already renders seat-2 and seat-3 views side by side. `src/explain/` sits at
> that same altitude. **It reads published outputs, never in-progress analysis** — which is
> precisely what `INV-014a` protects.

⚠ **The import fences caught this before a line of code existed.** Keep the incident for the
Phase-4 write-up — it is a concrete, checkable example of architecture doing work.

---

# 4. Interim: how imports work before absorption

`PG-1` blocks implementation until Phase 0 completes, so this is a **Phase-1 concern**, recorded
now so the decision is not re-litigated later.

| Option | Mechanism | Verdict |
|---|---|---|
| **A — editable install** | `pip install -e ../ai-investment-pipeline`; import `src.quant…` | ⚠ **collides.** Both repos root their packages at `src`, so two `src` packages fight |
| ★ **B — path-scoped namespace** | keep the upstream repo importable under its own distribution name; this repo's own code lives under `src/` and reaches the pipeline through **one adapter module** | ★★ **recommended** |
| **C — vendor early** | copy `src/**` in now | ✗ **premature.** The pipeline is still changing daily; a copy forks maintenance before the absorption is ready |

★ **Option B, concretely:** every reach into the pipeline goes through a single
`src/shared/upstream.py` shim. ⚠ **One file to delete at absorption time** — at which point the
imports it wraps become plain intra-repo imports, and nothing else changes.

> ★★ **That is the test of whether this structure is right:** absorption should delete one shim,
> move ~294 files with zero content changes, and merge `ownership.yaml`. Nothing else.

---

# 5. What `ownership.yaml` looks like after absorption

Inherited globs arrive pointing at inherited specs; new globs are added as each `F<n>` graduates.

```yaml
always:
  - sdd/specs/constitution.md

map:
  # ★ NEW — this repo's platform layers
  - globs: ["src/shared/agents/**"]
    spec: sdd/specs/F1_agent_protocol/spec.md
  - globs: ["src/orchestration/trace/**", "src/orchestration/graph/**"]
    spec: sdd/specs/F2_trace_replay/spec.md
  - globs: ["src/data_engine/corporate_actions/**"]
    spec: sdd/specs/F3_corporate_actions/spec.md
  - globs: ["src/explain/**"]
    spec: sdd/specs/F4_explainability/spec.md

  # ⇐ INHERITED — arrive with the absorption, repointed at their L-specs
  - globs: ["src/fundamental/**"]
    spec: sdd/design/rel6_design/L1-fundamental-analysis.md
  # … etc

exempt:
  - "*.md"
  - "sdd/**"
  - ".claude/**"
  - "src/evaluation/**"    # ★ D-14 — the ST-2 shape, like D-10
  - "src/experiments/**"   # ⇐ D-10 — P7-exempt
```

⚠ **`ST-8` applies at absorption:** a glob that matches nothing makes the gate **fail open,
silently**. Every glob moves in the **same commit** as the code it governs.

---

# 6. Open

| # | Question | Blocks |
|---|---|---|
| **S-1** | Does `src/evaluation/` stay gate-exempt (D-10 shape), or does F5 get a spec because the *harness itself* must be trustworthy? ★ **Leaning: spec it.** A measurement instrument nobody verified is how you get confidently wrong numbers | F5 |
| **S-2** | Confirm LangGraph is confined to `orchestration/graph/` and never imported by a domain — enforceable as a CI grep, like `ST-5` | F2, F6 |
| **S-3** | Does `config/` merge cleanly, or do platform settings need their own namespace? | absorption |
