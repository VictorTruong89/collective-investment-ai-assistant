# Specs — source of truth (lean SDD)

> **This folder is authoritative.** Production code is built from the files here, not
> from brainstorm docs. For the tiers and the release-close procedure see
> [`../README.md`](../README.md).

## What lives where

| Path | Role | Authority |
|---|---|---|
| [`vision.md`](vision.md) | **WHAT we are building** — dual purpose, the nine seats, capabilities `C1`–`C9`, the two scalability axes, the spec registry | **Highest, alongside the constitution** |
| [`constitution.md`](constitution.md) | **HOW we build** — `PG-2`…`PG-9` (`PG-1` retired), inherited rules, test tiers, change process | **Highest** — a spec may add constraints, never contradict it |
| `F<n>_<slug>/spec.md` | One feature = one spec. **★ **ALL 11 specs exist — `F1` `F2` `F5` 🟢 approved, 8 🟡 draft** — `F1` `F2` `F3` `F4` `F5` `F6a` `F6b` `F7a` `F7b` `F8` `F9`** — IDs are claimed in `vision.md` §4.1 | Authoritative once created |
| [`ownership.yaml`](ownership.yaml) | spec → code globs. The `PreToolUse` gate reads this; a spec with no globs is unenforced. ★ **Live since 2026-09-01** — 9 governed globs across 11 drafted specs | Authoritative (machine-read) |
| [`_templates/spec.md`](_templates/spec.md) | Skeleton for new specs — copy it to start a feature | — |
| `../design/rel<N>_brainstorm.md` | Brainstorm / rationale / decision log. Ideas live here until they graduate into a spec | **Non-authoritative** |
| `../design/releases/` | One-page close-out per release (+ its template) | Non-authoritative, historical |
| [`../archive/`](../archive/README.md) | Superseded specs, frozen as-is | Historical |

**Nothing in this folder is release-scoped.** A spec describes code that is *running
now*, so it is amended in place and retired only when its code is deleted.

## The SDD loop

1. **Diverge** — brainstorm freely in `../design/rel1_brainstorm.md`.
2. **Converge** — record the decision in that log's Decisions section.
3. **Graduate** — copy [`_templates/spec.md`](_templates/spec.md) → `F<n>_<slug>/spec.md`
   and fill it in. A feature is ready to graduate only when its acceptance criteria
   can be written.
4. **Approve** — review the spec (status 🟡 draft → 🟢 approved). The ACs are now the
   definition of done.
5. **Implement** — write code and tests where each test satisfies a specific `AC-n.k`,
   filling the spec's traceability table.

## Test tiers (constitution §4 — every AC maps to one)

data-contract · invariant/property · golden/characterization · API-contract ·
metric-gate · unit · integration.

## Spec index

> IDs are claimed in [`vision.md`](vision.md) §4 and **never renumbered**.
> ⚠ **Nothing is approved yet.** `PG-1` (which blocked implementation) was **retired 2026-09-02** —
> verification moved to the fund manager. Implementation is now gated only by **spec approval
> 🟡→🟢** and by the `PreToolUse` gate, which is unaffected and still requires the governing spec
> to be read before any edit.

> ★ **Reviewing?** The order to read them in — and which to read **together** — is
> [`../design/rel1_design/L3-build-sequence.md`](../design/rel1_design/L3-build-sequence.md) §2.3,
> with a review-status column to track progress.

| Spec-ID | Feature | Status | Acceptance criteria | Tests exist? |
|---|---|---|---|---|
| **F1** | [Module protocol & registry (SPI)](F1_module_registry/spec.md) | 🟢 **approved 2026-09-03** — 14 ACs, **0 blocked** (`Q1`–`Q3` → `D1`–`D3`) | AC-F1.1 … AC-F1.14 | 🔨 `MS-1` in progress |
| **F2** | [Execution trace & replay](F2_trace_replay/spec.md) | 🟢 **approved 2026-09-04** — 16 ACs, **0 blocked** (`Q1`–`Q6` → `D1`–`D6`) | AC-2.1 … AC-2.16 | ⛔ none — unapproved |
| **F3** | [Corporate-action resolution agent](F3_corporate_actions/spec.md) | 🟡 **draft** — 12 ACs, ⚠ 1 blocked (Q1) | AC-3.1 … AC-3.12 | ⛔ none — `PG-1` |
| **F4** | [Explainability contract](F4_explainability/spec.md) | 🟡 **draft** — 13 ACs, ⚠ 3 blocked (Q1, Q4, Q5) | AC-4.1 … AC-4.13 | ⛔ none |
| **F5** | [Evaluation harness](F5_evaluation_harness/spec.md) | 🟢 **approved 2026-09-04** — 16 ACs, **0 blocked** (`Q1`–`Q5` → `D1`–`D5`) | AC-5.1 … AC-5.16 | 🔨 `MS-4` |
| **F6a** | [Config-influence routing](F6a_config_routing/spec.md) | 🟡 **draft** — 11 ACs | AC-6a.1 … AC-6a.11 | ⛔ none |
| **F6b** | [Inter-agent messaging & deliberation](F6b_deliberation/spec.md) | 🟡 **draft** — 12 ACs; ✅ gate satisfied, ⚠ deployment mode set by `F7a` | AC-6b.1 … AC-6b.12 | ⛔ none |
| **F7a** | [Deliberation process tests (Tier A)](F7a_deliberation_process_tests/spec.md) — **gates F6b** | 🟡 **draft** — 12 ACs; ✅ blocker resolved | AC-7a.1 … AC-7a.12 | ⛔ none |
| **F7b** | [Deliberation outcome study (Tier B)](F7b_deliberation_outcome_study/spec.md) — never gates | 🟡 **draft** — 9 ACs, ⚠ 2 blocked (Q1, Q2) | AC-7b.1 … AC-7b.9 | ⛔ none |
| **F8** | [Human control surface](F8_control_surface/spec.md) | 🟡 **draft** — 20 ACs incl. directives; ⏳ vocabulary at E2E | AC-8.1 … AC-8.20 | ⛔ none |
| **F9** | [Thesis source port](F9_thesis_source_port/spec.md) | 🟡 **draft** — 10 ACs, ⚠ 2 blocked (Q1) | AC-F9.1 … AC-F9.10 | ⛔ none |
| **F10** | [Valuation trail (D-02)](F10_valuation_trail/spec.md) — ★ gates Stage B | 🟢 **approved 2026-09-13** — ✏ amended `D10` (2026-10-01) · `D11` (2026-10-02) | AC-F10.1 … AC-F10.23 | ✅ **23/23 green** |
| **F11** | [Reference-class base rates (D-02)](F11_reference_class_base_rates/spec.md) — the `J-10` input | 🟢 **approved 2026-10-02** — `D1`–`D6` | AC-F11.1 … AC-F11.9 | ✅ **9/9 green** · ⚠ `DX-143` (thin real data) |
| **F12** | [Quant core (D-03)](F12_quant_core/spec.md) — governs `src/quant/**` | 🟢 **approved 2026-10-05** — `D1`–`D8` (Victor) | AC-F12.1 … AC-F12.30 | ✅ **27/30 green** · ⊘ 3 vacuous |
| **F13** | [Thesis on demand (D-01)](F13_thesis_on_demand/spec.md) — `thesis_for TICKER --as-of DATE` | 🟢 **approved 2026-10-20** | AC-F13.1 … AC-F13.18 | ✅ 18/18 |

★ **F1 + F2 + F3 is a coherent release on its own** — and would still interview well if
nothing after it landed.

## Adding a new spec (checklist)

1. Claim the next free `F<n>` — never renumber an existing spec.
2. `cp _templates/spec.md F<n>_<slug>/spec.md`
3. Fill in the sections; give every behaviour an `AC-n.k` tagged with a test tier.
4. **Add its globs to [`ownership.yaml`](ownership.yaml) in the same change** — a
   spec with no globs is unenforced.
5. Add a row to the Spec index above.
6. On approval, set status 🟢 and begin implementation; keep the traceability table
   current as tests land.
7. Breaking a constitution rule? Amend `constitution.md` first, in its own change.
