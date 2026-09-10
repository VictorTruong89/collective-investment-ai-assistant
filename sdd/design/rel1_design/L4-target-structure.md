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
║  ★ Every inherited domain keeps its upstream path, verbatim.         ║
║    src/fundamental/  stays  src/fundamental/                         ║
║    src/quant/        stays  src/quant/                               ║
║                                                                      ║
║  ⚠ WHY THIS IS NON-NEGOTIABLE (PG-8):                                ║
║    ~34,700 LOC across 294 files import each other by absolute path   ║
║    (`from src.shared.money import Money`). Renaming ANY domain at    ║
║    absorption time rewrites imports across the whole tree, in the    ║
║    same commit as a move — and L4's migration classes forbid         ║
║    exactly that, because git records a rewrite and the review        ║
║    becomes impossible.                                               ║
║                                                                      ║
║  ★ A move commit changes ZERO bytes. That is the whole design.       ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 1.1 ★ Architecture considerations — and where each was actually decided

> **For a reader arriving here first.** This section states the four shape decisions behind the tree
> and **points to where each was argued**. ⚠ It deliberately does **not** restate those arguments —
> a second copy would drift, and `../../README.md` forbids exactly that.

| # | Question | Decision | ★ Where it was argued |
|---|---|---|---|
| **1** | **Vertical slices, or horizontal layers?** Folders by *domain* (`quant/`, `risk/`) or by *layer* (`models/`, `services/`)? | ★ **Vertical, by domain.** Layers live *inside* each module | ⬆ upstream `L0` §4.4 — *"the adoption is of the **Dependency Rule**, not the folder taxonomy"*. Inherited, and `PG-8` makes it non-negotiable |
| **2** | **Where does an alternative implementation live?** Beside its port, or in a central `adapters/` tree? | ★ **Beside its port**, in `<module>/adapters/` | ⬆ upstream `L4-coding-standards` §18.3 already fixes the module layout: `ports.py` · `service.py` · `store.py` · `adapters/`. **Inherited convention, not invention** — see §2.1 |
| **3** | **Registry, or pure dependency injection?** | **A registry**, resolved only at a composition root | 📘 **Lecture 1 §1.5** — including the honest cost: *a registry is a Service Locator*, trading a compile-time error for a runtime one. `validate_coverage()` at boot is the mitigation |
| **4** | **`Protocol` or `ABC` for the port?** | ★ **`Protocol`** — structural typing | 📘 **Lecture 1 §1.4.** ⚠ Decisive here: structural typing lets an **inherited or third-party class satisfy a port without inheriting from it**, which matters at absorption (`PG-8`) |

### The discussion already exists — three places, none of them this file

| Where | What it covers |
|---|---|
| 📘 **`docs/lectures/L1-3-ports-debate-evidence.html`, Lecture 1** | ★ **The full treatment** — the real vocabulary (Strategy, DIP, ports & adapters, SPI, variability management), interface-vs-contract and the LSP argument, `Protocol` vs `ABC`, the registry and its Service-Locator cost, contract tests, when *not* to build a port, and the anti-patterns |
| **`specs/vision.md` §5** | The binding principles `A1`–`A8` — dependency direction, semantic contracts, earned abstraction, confined frameworks |
| **`questions.md` `QR-7`, `QR-8`** | The two decisions that fixed the shape: **closed variant set** (no hot reload, no lazy discovery) and **module-scoped, not agent-scoped** |

★ **The mechanism itself is specified in [`F1`](../../specs/F1_module_registry/spec.md)** — 12 ACs
covering registration, resolution, the closed set, per-run caching, provenance and the contract suite.
**This document places F1's output in the tree; it does not re-specify it.**

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
    │   ├── registry/               ★★ NEW  F1 — the SPI. MODULE-scoped (QR-8)
    │   │   ├── registry.py         ★ (port, variant) → factory · closed set (QR-7)
    │   │   ├── provenance.py       ★ CT-1.4 — travels with every resolved output
    │   │   ├── wiring.py           ★ ⚠ THE COMPOSITION ROOT — the one place that
    │   │   │                          imports every adapter (CA-9)
    │   │   └── errors.py           ★ DuplicateRegistration · UnknownVariant
    │   ├── agents/                 ★ NEW  AgentPort — ONE registered port among several
    │   │   ├── ports.py            ★ pure typing, no implementation (CA-3)
    │   │   └── messages.py         ★ typed inter-agent messages (F6b)
    │   └── upstream.py             ★ NEW  the interim shim — ⚠ DELETED at MS-8 (§4)
    │
    ├── data_engine/                ⇐ INHERITED  D-07 · 8,511 LOC
    │   ├── calendar/ contracts/ ingest/ observation/ pit/ store/
    │   ├── symbology/ universe/ validation/
    │   └── corporate_actions/      ★★ NEW  F3 — the earned agent (PG-3)
    │
    ├── feature_engineer/           ⇐ INHERITED  D-02 · neutral ground
    ├── fundamental/                ⇐ INHERITED  D-01 · 8,527 LOC
    │   ├── claims/                 ⚠ built, tested, exported — AND NEVER CALLED (AB-2)
    │   ├── scorecard/              ⚠ same shape (AB-1)
    │   ├── relay/                  ⇐ D-01 §4B — compose · ingest · confidence_of
    │   └── source/                 ★★ NEW  F9 — ★ THE WORKED EXAMPLE OF §2.1
    │       ├── ports.py            ★ ThesisSourcePort + its C1–C5 guarantees
    │       └── adapters/           ★ ── the variants live HERE ──
    │           ├── api.py          ★ ApiAdapter    (default — QR-20)
    │           └── relay.py        ★ RelayAdapter  ⚠ WRAPS relay/, rebuilds nothing
    │
    ├── quant/                      ⇐ INHERITED  D-03
    │   └── metrics/                ⇐ ic.py · breadth.py — ⚠ F5 CONSUMES, never re-derives
    ├── models/                     ⇐ INHERITED  D-04 — a future RankingModelPort's
    │                                  adapters/ would hold lightgbm.py · ebm.py
    ├── risk/                       ⇐ INHERITED  D-05
    ├── portfolio/                  ⇐ INHERITED  D-06
    ├── recording/                  ⇐ INHERITED  D-11
    ├── reporting/                  ⇐ INHERITED  D-09
    ├── decision/                   ⇐ INHERITED  D-12 · the meet-semilattice (PG-6)
    │   └── attribute/binding.py    ⇐ "which gates bound, and why" — F4 CONSUMES this
    ├── experiments/                ⇐ INHERITED  D-10 · P7-exempt, ST-2 one-way
    │                                  ★ experimental variants live here (§2.1)
    │
    ├── orchestration/              ⇐ INHERITED  D-08
    │   ├── contracts/ jobs/ schedule/ state/
    │   ├── policy/                 ⇐ budget.py · retry.py
    │   │   └── routing.py          ★★ NEW  F6a — pure function, no I/O (PG-9)
    │   ├── graph/                  ★★ NEW  F2/F6b — ⛔ the ONLY directory permitted
    │   │   │                          to import an orchestration framework (QR-14)
    │   │   ├── pipeline_graph.py   ★ nodes + edges
    │   │   ├── deliberation.py     ★ F6b — the state machine + turn budget
    │   │   └── checkpoints.py      ★ checkpoint adapter (local JSON)
    │   ├── trace/                  ★★ NEW  F2 — the observability substrate
    │   │   ├── models.py           ★ StepRecord · ExternalCall · DecisionRecord
    │   │   │                          · CapabilityDelta  ⚠ PG-5.2 + PG-9 fields
    │   │   ├── record.py  store.py  replay.py  redact.py  outcomes.py   ★
    │   └── control/                ★★ NEW  F8 — the inbound human channel
    │       ├── analysis.py         ★ full-depth drill-down (QR-16)
    │       ├── resume.py           ★ suspend / resume
    │       └── directives/         ★ interpret.py · store.py — closed effect vocab
    │
    ├── explain/                    ★★ NEW  D-13 — F4
    │   │                           ⚠ DOWNSTREAM of the analyst firewall. See §3.
    │   ├── contracts/              ★ the explanation shape
    │   ├── comparative.py          ★ "why this one and not that one"
    │   └── counterfactual.py       ★ "what would have to change to flip this"
    │
    └── evaluation/                 ★★ NEW  D-14 — F5 / F7a / F7b
        │                           ★ the ST-2 shape: imports anything, imported by nothing
        ├── golden/                 ★ known-correct fixtures
        ├── metrics/                ★ grounding · calibration · faithfulness
        ├── regression/             ★ fails when a PROMPT changes behaviour
        └── studies/                ★ deliberation.py · killrule.py · report.py
```

## 2.1 ★★ Where a new pluggable alternative goes

**Four locations, and only four.** A variant that does not fit one of them is a sign the port is in
the wrong place.

```text
   src/fundamental/source/           ← the module that OWNS the capability
   ├── ports.py                        the CONTRACT   — pure typing (CA-3)
   ├── service.py                      the USE CASE   — imports ports, never an SDK
   └── adapters/                     ★ THE VARIANTS LIVE HERE
       ├── api.py                      ApiAdapter     ← default
       └── relay.py                    RelayAdapter   ← alternative
                    ▲
                    │  registered once, at the composition root
                    │
   src/shared/registry/wiring.py     ← ("thesis_source", "api")   → ApiAdapter
                                       ("thesis_source", "relay") → RelayAdapter
```

| Where | What goes there | Rule |
|---|---|---|
| **`<module>/ports.py`** | the contract — a `Protocol` and its written guarantees | ⚠ pure typing, no implementation (`CA-3`) |
| ★ **`<module>/adapters/<variant>.py`** | **every alternative implementation** | Inherited convention (upstream `L4` §18.3). Adapters may import an SDK; the module above them may not (`A2`) |
| **`src/shared/registry/wiring.py`** | the **only** place that imports adapters, and registers them | ⚠ The composition root (`CA-9`). Everything selectable is registered **here, at startup** — the closed set (`QR-7`, `F1` `AC-F1.5`) |
| **`src/experiments/`** | ★ **experimental** variants | The `ST-2` carve-out: nothing imports D-10 **except the wiring**, so an experiment can be swapped in, run, and swapped out without any domain depending on it. Registered with `experimental=True`, which propagates to every output (`F1` `AC-F1.11`, `PG-2`) |

### Why a variant does **not** live anywhere else

- ✗ **Not in a central `src/adapters/` tree.** It would sit outside the domain whose contract it
  satisfies, and a reader of `fundamental/` would not find the implementations of `fundamental/`'s own
  port. It also breaks the vertical-slice rule (§1.1 #1).
- ✗ **Not discovered from the filesystem at runtime.** The variant set is **closed** (`QR-7`): a
  variant that was never registered cannot be resolved, and no import or filesystem lookup is
  attempted (`F1` `AC-F1.5`). ★ **That is what makes the no-hot-reload non-goal structural rather than
  merely stated.**
- ✗ **Not registered by the module itself on import.** Registration order would become semantics.
  One composition root, called once.

### The three variant axes already in the tree

| Axis | Port | Variants today | Where |
|---|---|---|---|
| **Thesis source** (`F9`) | `ThesisSourcePort` | `api` ★default · `relay` | `fundamental/source/adapters/` |
| **LLM tier** (pluggability L1) | the gateway | Opus · Sonnet · Haiku | `shared/llm/tiers.py` |
| **Ranking model** *(not yet built)* | `RankingModelPort` | LightGBM · EBM challenger | `models/…/adapters/` when `A4` is satisfied |

⚠ **`A4` — abstraction is earned.** A port with one implementation is a guess about the future written
in code. `RankingModelPort` appears above as an *illustration*, not a commitment: it earns its
existence when the EBM challenger is real (`F4` `Q2`), and `F1` `AC-F1.12` tests exactly that.

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
`MS-9` write-up — it is a concrete, checkable example of architecture doing work.

---

# 4. Interim: how imports work before absorption

This is an **`MS-2` concern**, recorded
now so the decision is not re-litigated later.

| Option | Mechanism | Verdict |
|---|---|---|
| **A — editable install** | `pip install -e ../ai-investment-pipeline`; import `src.quant…` | ⚠ **collides.** Both repos root their packages at `src`, so two `src` packages fight |
| ~~★ **B — path-scoped namespace**~~ | ~~keep the upstream repo importable under its own distribution name~~ | ⛔ **DISPROVEN 2026-09-04, measured.** The clash is on the **import** name, not the distribution name — a distribution name changes nothing. Partially fixed at the root (`L3` `DX-1` ✅); ⚠ **recurs at every shared subdirectory** (`L3` `DX-2`, open) |
| **C — vendor early** | copy `src/**` in now | ✗ **premature** *(and still is — B is per-DOMAIN, not wholesale)* |
| ★★ **PER-DOMAIN ABSORPTION** *(no letter — it is `L3` §6.1's **option B**; ⚠ do not call it "D", which is `L3`'s process-boundary option)* | a domain moves here the moment this repo needs to add to it; the two trees never both hold one domain | ★★ **CHOSEN 2026-09-04** — `questions.md` `QR-22`, `L3` §6.2 |

⚠ ~~**Option B, concretely:** every reach into the pipeline goes through a single
`src/shared/upstream.py` shim.~~ **Struck 2026-09-04.** The shim presumes both trees are importable at
once, which `QR-22` measured to be impossible for any domain both repos populate.

⚠⚠ **The rule, stated once — it recurred three times before it was written down.**
**EVERY top-level directory both repos populate must be a namespace package** (no `__init__.py` in
either): `src/` (`DX-1`), `src/shared/` and the domains (`DX-2`), `tools/` (`DX-7`). A *regular*
package found anywhere on `sys.path` **ends the import scan**, so one stray `__init__.py` makes the
other repo's contents invisible — with a `ModuleNotFoundError` naming the submodule and no hint of the
cause. ★ `DX-7`'s file was **untracked**, so `git status` could not show it either.

★ **Option D, concretely:** there is **no shim for an absorbed domain** — its imports are plain
intra-repo imports from the day it arrives, because upstream's copy is gone. A shim survives only for
reaching a domain this repo has **not** absorbed and does not intend to yet.

> ★★ **That is the test of whether this structure is right:** absorption should delete one shim,
> move ~294 files with zero content changes, and merge `ownership.yaml`. Nothing else.

---

# 5. What `ownership.yaml` looks like after absorption

## ⚠⚠ 5.1 The ordering rule — specific before broad

**`ownership.yaml` is first-match-wins.** At absorption the inherited domains arrive as broad globs,
and several of them *contain* a path this repo already governs:

```text
   ⛔ WRONG — the inherited glob swallows F9
      - globs: ["src/fundamental/**"]        → L1-fundamental-analysis
      - globs: ["src/fundamental/source/**"] → F9      ← NEVER REACHED

   ✅ RIGHT — specific first
      - globs: ["src/fundamental/source/**"] → F9
      - globs: ["src/fundamental/**"]        → L1-fundamental-analysis
```

★ **THE RULE: every platform glob is written ABOVE the inherited glob that contains it.**

⚠ **The failure is silent.** Editing `src/fundamental/source/` would credit a read of the *upstream*
L-spec and never require `F9` — the gate still fires, so nothing looks broken, and the wrong spec
governs. This is `ST-8`'s hazard with the sign flipped: not a glob that matches nothing, but a glob
that matches *too much*.

**Four platform paths sit inside an inherited domain and must precede it at `MS-8`:**

| Platform glob | Contained by | Spec |
|---|---|---|
| `src/fundamental/source/**` | `src/fundamental/**` | `F9` |
| `src/data_engine/corporate_actions/**` | `src/data_engine/**` | `F3` |
| `src/orchestration/{trace,graph,control}/**` · `policy/routing.py` | `src/orchestration/**` | `F2` `F6b` `F8` `F6a` |
| `src/shared/{registry,agents}/**` | `src/shared/**` | `F1` |

★ **`MS-8.4` should assert this mechanically** — for every pair of globs where one is a prefix of the
other, the more specific must appear first.

## 5.2 The shape after absorption

```yaml
always:
  - sdd/specs/constitution.md

map:
  # ── ★ PLATFORM FIRST — each precedes the inherited glob that contains it ──
  - globs: ["src/shared/registry/**", "src/shared/agents/**"]
    spec: sdd/specs/F1_module_registry/spec.md
  - globs: ["src/orchestration/trace/**"]
    spec: sdd/specs/F2_trace_replay/spec.md
  - globs: ["src/orchestration/graph/**"]
    spec: sdd/specs/F6b_deliberation/spec.md
  - globs: ["src/orchestration/control/**"]
    spec: sdd/specs/F8_control_surface/spec.md
  - globs: ["src/orchestration/policy/routing.py"]
    spec: sdd/specs/F6a_config_routing/spec.md
  - globs: ["src/data_engine/corporate_actions/**"]
    spec: sdd/specs/F3_corporate_actions/spec.md
  - globs: ["src/fundamental/source/**"]
    spec: sdd/specs/F9_thesis_source_port/spec.md
  - globs: ["src/explain/**"]
    spec: sdd/specs/F4_explainability/spec.md
  - globs: ["src/evaluation/**"]
    spec: sdd/specs/F5_evaluation_harness/spec.md

  # ── ⇐ INHERITED — arrive at MS-8, repointed at their L-specs, BELOW the above ──
  - globs: ["src/fundamental/**"]
    spec: sdd/design/rel6_design/L1-fundamental-analysis.md
  - globs: ["src/orchestration/**"]
    spec: sdd/design/rel6_design/L1-orchestration.md
  - globs: ["src/data_engine/**"]
    spec: sdd/design/rel6_design/L1-data-engine.md
  - globs: ["src/shared/**"]
    spec: sdd/design/rel6_design/L2-shared-infrastructure.md
  # … quant, models, risk, portfolio, decision, recording, reporting, feature_engineer

exempt:
  - "*.md"
  - "sdd/**"
  - "docs/**"
  - ".claude/**"
  - "config/**"
  - "tests/**"
  - "tests_src/**"
  - "src/experiments/**"   # D-10 — P7-exempt, held by ST-2
```

⚠ **`ST-8` still applies in the other direction:** a glob matching nothing makes the gate **fail open,
silently**. Every glob moves in the **same commit** as the code it governs.

# 6. Open

| # | Question | Blocks |
|---|---|---|
| **S-1** | Does `src/evaluation/` stay gate-exempt (D-10 shape), or does F5 get a spec because the *harness itself* must be trustworthy? ★ **Leaning: spec it.** A measurement instrument nobody verified is how you get confidently wrong numbers | F5 |
| **S-2** | Confirm LangGraph is confined to `orchestration/graph/` and never imported by a domain — enforceable as a CI grep, like `ST-5` | F2, F6 |
| **S-3** | Does `config/` merge cleanly, or do platform settings need their own namespace? | absorption |
