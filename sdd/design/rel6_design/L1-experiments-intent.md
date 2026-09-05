# L1 Intent Capture: Experiments (D-10)

> **Tier:** `sdd/design/rel6_design/` — **design tier, non-authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-10 · **Seat:** SEAT-5
> **Status:** ⚠ **INTENT CAPTURE — this is NOT the L1 spec.**
>
> **L0 §4.2 and `L3-build-sequence.md` BS-23 both hold: D-10 gets no L1 spec until the first full
> E2E run is complete and evaluated.** That decision stands and this file does not overturn it.
> What is captured here is **stated intent plus a feasibility audit**, so that when the trigger
> fires the spec is written from a recorded position rather than from memory. ★ **The distinction
> matters** — L0's argument is that *what belongs in an experiment* is unknowable before B3. That is
> still true. *What the experiment machinery must be able to do* is knowable now, and is what
> follows.

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.5.0 | 2026-08-22 | Victor | ✅ **QX-4 closed — D-01 prompts ARE variants** (§7A). ★ **The seam already exists**: MP-2 makes a prompt *composed, not written*, so a variant substitutes **one declared block**, and **INV-9's alignment checker becomes the admission test** — it already refuses an unversioned prompt change, which is XP-13 enforced for free. ⚠ **Two real collisions surfaced and are resolved, not waved through.** **XP-30 (a variant must reproduce itself) cannot be met literally** — LLM output is stochastic and `temperature` is unsettable on Opus 5; reproducibility transfers from the *output* to the *measurement* (XP-45), which costs `k×`. ★★ **And D-01 §7.5 already warns against exactly what this decision makes easy** — *"tuning prompts until the base rate looks healthy optimises the metric, not the analysis."* **XP-47 splits the bundle sets** (regression / selection / confirmation), because one set cannot both tune and judge. |
| 0.4.0 | 2026-08-22 | Victor | ★ **New §5A — what a "variant" actually is**, because the word was load-bearing in twelve rules and defined in half a sentence. Definition, anatomy, the **may/may-not** table, ★ **the contrast set** (a variant is not a feature flag, not a branch, not a plugin, not a config override — each of those is a different thing that would behave differently), lifecycle, and two worked examples at the extremes. **XP-41: one variant changes ONE thing**, or a better score is unattributable — which is what `blend_attribution.py` already exists to untangle. **XP-42: a variant is inert by default.** **XP-43: it names its seam.** |
| 0.3.0 | 2026-08-22 | Victor | ✅ **QX-6 and QX-7 closed.** **§9B — experiments are MANUAL-ONLY**: nothing scheduled, no daily-path step, D-08 never invokes D-10. ★ **That answers QX-6 structurally** — a variant cannot become permanent by neglect because **no unattended process ever runs one**; the neglect risk moves to *"the baseline changed and nobody recorded it"*, which XP-24/XP-28 already cover. ★★ **XP-35 draws a boundary that would otherwise be crossed by accident**: the same runner serves *regression* (fixed set, automated, gates a release — AC-1.9/RM-4) and *sweeps* (variants, manual, never gates). **The test is whether anything varies.** ★ **QX-7: `buffett/backtest/**` is HARVESTED, not moved** (§9C) — reclassified **EXCLUDE → REBUILD**. ⚠ **Correction: it has ZERO tests**, verified — so "transfer its tests" is not available; what transfers is the *designs*. ★ **`iv_replay.py` is the find** — a point-in-time fundamental backtest, which is precisely the Fundamental-surface protocol XP-11d said was missing. |
| 0.2.0 | 2026-08-22 | Victor | ✅ **QX-5 CLOSED — reuse the rel5 harness** (§2a), and the BS-22-vs-P4 tension it flagged **dissolves**: `L4` §1.5's disposition vocabulary already had the answer. ★★ **XP-14 REVERSED by §9A's audit.** Variants were to live under `src/<domain>/variants/` for locality; that placement breaks **two** things — the domain glob is *governed* so the hook would demand spec-reading for P7-exempt work, and **ST-2's CI grep is blind to it**, so production could import a variant as an ordinary intra-domain import. ⚠ **Locality would have opened a leak path the one-way rule cannot see.** Variants now live under `src/experiments/variants/<domain>/`, and the inheritance XP-14 wanted becomes an **explicit check (XP-32)** instead of a location effect. ★ **§9A also found a live staleness bug**: `L4` §1.2 still had **D-10 at SEAT-3** after L0 v0.22.0 moved it to SEAT-5 — fixed. |
| 0.1.0 | 2026-08-21 | Victor | Intent recorded (§1). Feasibility audit against the **1,978 LOC of experiment harness already in `pipeline/ohlcv/experiments/`** (§2). Verdict §3: the baseline+variant pattern is **proven in this codebase**; the *"entire codebase adaptive configurable"* half is the one item recommended against, and §4 gives the alternative. Vocabulary §5, architecture §6, the four surfaces §7, ★ the promotion gate §8 — *the part that actually needs a spec*. |

---

# 1. THE INTENT, AS STATED

Recorded as given, before evaluation. **These are `XP-` intent items, not rules** — nothing here
binds until the L1 spec is written.

| ID | Stated intent |
|---|---|
| **XP-1** | Experiments target **all analyst seats plus D-12 Decision** — Fundamental (D-01), Quantitative (D-03/D-04), Risk Management (D-05), and the composition layer (D-12) |
| **XP-2** | The **most frequent** experiment is ML model selection and hyperparameter tuning |
| **XP-3** | Experiments also cover **different approaches** for Fundamental and Risk: formulas, optimisation, deterministic algorithms, weights |
| **XP-4** | An experiment is **not merely a set of configs** — it is new mathematics, new algorithms, new Python code, new ML libraries, new model architectures |
| **XP-5** | The codebase should be an **adaptive configurable base**, so an experiment is a **portable module that plugs in and out easily** |
| **XP-6** | An experiment attempt = **Python code** (model, algorithm, logic) **+ config files** (YAML/JSON: hyperparameters, fixed values) that adapt to the main codebase |
| **XP-7** | The main configuration/algorithms/logic used for daily production work is the **"golden config"** *(a better name was invited — see §5)* |
| **XP-8** | Enabling this may require an **adaptor and an interface for every domain** |
| **XP-9** | For simplicity, possibly **four separate Experiments domains**, one under each of Quant, Fundamental, Risk and Decision |
| **XP-10** | ★ The purpose of all of the above is to **minimise bugs and discrepancies when experimenting** |

> ★ **XP-10 is the requirement; XP-5 through XP-9 are a proposed solution to it.** They are separated
> here on purpose, because §3 accepts the requirement and disagrees with part of the solution.

---

# 2. WHAT ALREADY EXISTS — audited, not assumed

⚠ **`pipeline/ohlcv/experiments/` is 1,978 LOC of working experiment harness**, built in rel5 for
the Feature 3-c hyperparameter work. **The architecture XP-5…XP-7 describes is already implemented
for the quant seat**, and the naming Victor reached for independently is the naming already in the
code.

| Module | LOC | What it already does |
|---|---|---|
| `experiment_runner.py` | 539 | The sweep loop; walk-forward **and** CPCV variants; per-variant seeding |
| `tuning_report.py` | 382 | Result reporting |
| `blend_attribution.py` | 196 | Which component moved the metric |
| `cpcv.py` | 180 | Combinatorial purged cross-validation |
| `leaderboard.py` | 168 | Cross-variant comparison on a common footing |
| `policy_tuner.py` | 147 | Policy-level sweeps |
| `experiment_config.py` | 142 | `VariantSpec` · `ExperimentConfig` · `load_experiment_config()` |
| `grid_gen.py` | 89 | Grid / random search generation |

★ **Three findings from reading it, each of which changes the feasibility answer:**

**① The baseline-plus-overlay pattern is already built and named.**
`ExperimentRunner._deep_merge(base, override)` merges `ExperimentConfig.config_overrides` into the
global `settings.yaml` before a sweep runs. **That *is* XP-7's "golden config + experiment overlay",
implemented and exercised over a 25-variant sweep.**

**② Code substitution already exists — but only from a closed set.**
`VariantSpec.backend` is `str | Dict[str, str]` — a **named registry key** (`sklearn_rf`, `linear`,
…), optionally per model role. So swapping an implementation by name is solved. ⚠ **What is not
solved is XP-4: registering *arbitrary new* code**, which is the gap between "choose a backend" and
"try a new architecture."

**③ Determinism is already handled at the variant level.** `_with_seed(spec, seed)` and
`ExperimentConfig.seed` exist. ⚠ **But the seed pins the *run*, not the *code*** — see §9.

| ID | Consequence |
|---|---|
| **XP-11** | ★ **Constitution P4 applies: reuse before rebuild.** D-10's harness is not a green field. The runner, the CPCV evaluator, the leaderboard and the grid generator are prior art to be **carried across and generalised**, not reinvented — and `L3` **BS-22**'s *"the legacy tree is replaced, not repaired"* does **not** exempt this from being read first |

## 2a. ✅ QX-5 CLOSED — the rel5 harness is REUSED

| ID | Rule |
|---|---|
| **XP-11a** | ✅ **`pipeline/ohlcv/experiments/**` (1,978 LOC) is MOVED into `src/experiments/`, then generalised — never rewritten from scratch.** It is classed **REVIEW** in `L4` §1.5, whose definition is exactly this: *"moves, then is deliberately rewritten against a written AC — `git mv` first, rewrite in a later commit. **Never both at once.**"* |
| **XP-11b** | ★ **The move commit changes no behaviour.** A move that also "tidies" is a rewrite with the diff hidden, and the whole value of moving 1,978 exercised lines is that they already work. ⚠ `L3` **BS-21** applies: the suite is green at every commit |
| **XP-11c** | ★ **Three pieces carry across essentially unchanged and are the load-bearing ones**: `_deep_merge(base, override)` (the baseline+variant overlay — XP-7), `VariantSpec.backend` (the named registry — XP-4's foundation), and `cpcv.py` (the honest-selection evaluator XP-26 depends on) |
| **XP-11d** | ⚠ **What must be generalised afterwards, in its own commit:** the runner is **quant-shaped** — it assumes a panel, folds, a training loop and a metric over predictions. **A Fundamental or Risk variant has none of those.** The generalisation is to make *evaluation protocol* a per-surface plug (§7), not to make the runner more configurable |

**Target mapping** *(`L4` §1.5 D-10 table, updated)*:

```text
   ohlcv/experiments/experiment_runner.py   →  experiments/sweeps/
   ohlcv/experiments/grid_gen.py            →  experiments/tuning/
   ohlcv/experiments/cpcv.py                →  experiments/evaluate/
   ohlcv/experiments/leaderboard.py         →  experiments/leaderboard/
   ohlcv/experiments/experiment_config.py   →  experiments/registry/   ★ VariantSpec
   ohlcv/experiments/{tuning_report,
                      blend_attribution}.py →  experiments/leaderboard/
   ohlcv/experiments/policy_tuner.py        →  experiments/variants/quant/
   ohlcv/experiments/run_feature3c.py       →  ⚠ a rel5 entry point — EXCLUDE, not moved
```

---

# 3. FEASIBILITY — item by item

| Intent | Verdict | Note |
|---|---|---|
| **XP-1** all four domains | ✅ **Feasible** | §7 |
| **XP-2** ML selection + HP tuning | ✅ **Already built** | §2 — proven over a 25-variant sweep |
| **XP-3** formulas, optimisation, weights | ✅ **Feasible** | Cheaper than XP-2: mostly pure functions with no training loop |
| **XP-4** new code, not just config | ⚠ **Feasible, needs design** | The registry must open (§6); the variant hash must cover code (§9) |
| **XP-5** *"entire codebase adaptive configurable"* | ✗ **Recommend against** | ★ **§4 — this is the one item that would make XP-10 worse, not better** |
| **XP-6** code + config per attempt | ✅ **Feasible** | Already the shape of `VariantSpec` + `experiments.yaml` |
| **XP-7** "golden config" | ✅ Feasible, ⚠ **rename** | §5 — the word is taken, and the project already has a better one |
| **XP-8** adaptor + interface per domain | ◐ **Mostly already exists** | §6 — the interfaces are the `CT-n.k` contracts and the §12 API surfaces |
| **XP-9** four separate Experiments domains | ◐ **Half right** | §6 — one harness, four surfaces |
| **XP-10** minimise bugs and discrepancies | ✅ **The right requirement** | And §4 argues XP-5 is the wrong instrument for it |

---

# 4. ✗ THE ONE RECOMMENDATION AGAINST — and what to do instead

```text
╔══════════════════════════════════════════════════════════════════╗
║  WHAT PREVENTS A DISCREPANCY IS NOT PLUGGABILITY.                ║
║  IT IS RUNNING THE SAME CODE PATH.                               ║
║                                                                  ║
║  INV-4 already says exactly this for train vs inference:         ║
║  parity is achieved by the SAME code path, not by two paths      ║
║  that are configured to agree.                                   ║
║                                                                  ║
║  A plug point is, by construction, a place where TWO             ║
║  implementations exist and must be shown to agree. Making the    ║
║  whole codebase pluggable multiplies the number of places        ║
║  where production and experiment can silently differ —           ║
║  which is precisely the bug class XP-10 exists to eliminate.     ║
║                                                                  ║
║  ★ "Adaptive configurable base" is speculative generality. It    ║
║    also fights P1: a spec cannot say what the code does if the   ║
║    code is whatever the config loaded.                           ║
╚══════════════════════════════════════════════════════════════════╝
```

**The alternative, which gets XP-10 without the cost:**

| ID | Proposed rule |
|---|---|
| **XP-12** | ★★ **Plug only at seams that ALREADY exist and are ALREADY tested.** Every domain publishes a §12 Public API Surface and `CT-n.k` contracts. **A variant substitutes an implementation *behind an existing contract*; it never introduces a new seam.** ⚠ You do not need new interfaces — you need the existing contracts to be **constructible with a different implementation**. That is dependency injection at ~12 named seams, not a plugin framework |
| **XP-13** | ★★ **A variant is admissible only if the BASELINE's own contract tests pass against it, unchanged.** This one rule does most of the work: a variant may change **values**, never **shapes**. A variant that needs the contract test edited is not a variant — it is a **contract change**, and contract changes go through the spec (P1) |
| ~~**XP-14**~~ | ⚠ **REVERSED 2026-08-22 by §9A's audit.** It read: *"a variant inherits the import restrictions of the domain it plugs into, by LOCATION."* ★ **The locality it depended on is unsafe** — see §9A.2. **SUPERSEDED → XP-32** |
| **XP-32** | ★★ **All variant code lives under `src/experiments/variants/<domain>/`, and its seat restrictions are enforced by an EXPLICIT CHECK rather than by location.** A variant under `src/experiments/` can import anything, so **INV-014 has to be asserted, not inherited**: a `variants/fundamental/` module may not import `src/quant/`, `src/models/` or their outputs, and vice versa. ⚠ **This is a new CI check that does not exist today** — `ST-2`'s grep only catches production importing D-10, not a variant reaching across seats |
| **XP-15** | **The number of plug points is a declared, finite list — not "wherever someone needs one."** Adding one is a spec change. ⚠ An unbounded set of seams is XP-5 arriving through the back door |

> ★ **The instinct behind XP-5 is right and the scope is wrong.** Victor is correct that ad-hoc
> experimentation is where discrepancies come from. The fix is **fewer, named, tested seams** — not
> more of them.

---

# 5. VOCABULARY — "golden config" is a collision, and the project already has the words

| Proposed | Use instead | Why |
|---|---|---|
| "golden config" | ★ **`baseline`** | ⚠ **"Golden" is already taken and means something else here**: constitution §4's *Golden / characterization* test tier means **frozen expected output**. Overloading it would repeat the collision `L3` already had to fix once (`M0…M7` → `B0…B7`, because `M-1…M-5` were the mandate). ★ **And `baseline` is already this project's word for exactly this concept** — D-01 §7.4: *"a rubric edit invalidates every baseline"*, RM-4/RM-5 |
| "experiment attempt" | ★ **`variant`** | Already the name in the code: `VariantSpec` |
| "adaptor" | **`adapter`** *(if needed at all)* | §6 argues most of these already exist as contracts |

| ID | Proposed rule |
|---|---|
| **XP-16** | ★ **`baseline` = the code and config production runs today. `variant` = one candidate substitution against it. `sweep` = a set of variants evaluated together.** Both load-bearing words are already in use — in the constitution and in `experiment_config.py` respectively — so **this is adopting existing vocabulary, not coining any** |

---

# 5A. ★ WHAT A "VARIANT" IS — the definition in full

> The word carries twelve rules in this file and was defined in half a sentence (XP-16). It is also
> **overloaded in software**, and every neighbouring meaning would behave differently — §5A.5.

## 5A.1 The definition

```text
╔══════════════════════════════════════════════════════════════════╗
║  A VARIANT IS ONE CANDIDATE SUBSTITUTION AGAINST THE BASELINE,   ║
║  AT A DECLARED SEAM, WITH AN IDENTITY AND A HASH, THAT CHANGES   ║
║  VALUES AND NEVER SHAPES.                                        ║
║                                                                  ║
║  ★ Or, shorter: A VARIANT IS A HYPOTHESIS WITH AN ADDRESS.       ║
║                                                                  ║
║  It is the smallest thing you can swap in and still ask          ║
║  "did THAT change the answer?" — and the identity, the hash      ║
║  and the registry all exist so that question has a defensible    ║
║  answer rather than an anecdote.                                 ║
╚══════════════════════════════════════════════════════════════════╝
```

## 5A.2 Three words, deliberately kept apart

| Word | Is | Example |
|---|---|---|
| **experiment** | ★ the **question** | *"would weighting the moat rubric's outcome tests more heavily discriminate better?"* |
| **variant** | ★ one **candidate answer**, as runnable code + config | `moat_durability@v3-outcome-weighted` |
| **sweep** | ★ one **run** that evaluates a set of variants against the baseline | the twelve rubric variants, run over the pinned bundle set |

⚠ **These get used interchangeably in conversation and must not be in the registry.** A sweep has a
date and a cost; a variant has a hash and a result; an experiment has neither and is just what you
were trying to find out.

## 5A.3 Anatomy — what a variant is made of

| Part | What it is | Prior art in `experiment_config.py` |
|---|---|---|
| **id** | A stable, human-readable name that survives into the leaderboard and the promotion record | `VariantSpec.id` |
| **seam** | ★ **Which declared plug point it substitutes at** (XP-12, XP-15). A variant that does not name one is not admissible | — ⚠ **new** (rel5 had one implicit seam: the model backend) |
| **substitution** | The code — a model class, a formula, an algorithm, a rubric, a prompt block. **May be new code** (XP-4) | `VariantSpec.backend` — *by registry name, from a closed set* |
| **configuration** | Hyperparameters, thresholds, fixed values — YAML/JSON overlaid on the baseline | `VariantSpec.hyperparameters` + `ExperimentConfig.config_overrides` |
| **baseline ref** | ★ **Which baseline version it overlays.** A variant is meaningless without it — it is a *difference*, not a thing | ⚠ implicit in rel5 (`settings.yaml` at run time) — **must become explicit** (XP-28) |
| **variant_hash** | Content hash over code + config + baseline + data snapshot + seed + library versions (XP-29) | ⚠ **new** — rel5 hashed nothing; it seeded the run |
| **protocol** | Which evaluation applies — CPCV, walk-forward, pinned-bundle regression, deterministic replay (§7) | `ExperimentConfig.validation` |
| **status** | `registered · enabled · swept · promoted · discarded` | `VariantSpec.enabled` (a two-state subset) |

★ **Five of eight already exist.** The three that do not — **seam**, **baseline ref**, **hash** — are
exactly what turns rel5's quant-only sweep tool into something four domains can share.

## 5A.4 What a variant may and may not change

| ✅ May change | ✗ May not change |
|---|---|
| A **value**: a threshold, a weight, a hyperparameter, a horizon | A **shape**: a contract field, a JSON key, a return type (XP-13) |
| An **implementation** behind an existing contract | The **contract** itself — that is a spec change (P1) |
| A **formula, algorithm or model architecture** (XP-4) | The **seam list** — plug points are finite and declared (XP-15) |
| A **rubric's criteria** or a **prompt block** | Whether an alert can be **suppressed** (XP-21, INV-026) |
| Which library computes something | The **import rules** its seat obeys (XP-32, INV-014) |

> ★ **XP-13 is the whole test, restated: a variant is admissible only if the baseline's own contract
> tests pass against it, unchanged.** If a test needs editing, what you have is not a variant — it is
> a contract change wearing one, and it goes through the spec.

## 5A.5 ★ What a variant is NOT — and why each neighbour would behave differently

⚠ Every row below is a real thing this word gets confused with, and each would break a different rule.

| Not a… | Difference | What breaks if confused |
|---|---|---|
| **feature flag** | A flag varies **production** behaviour at run time, for real users | ★ A variant **never runs in production** (XP-34). A flag that selects a variant *is* a promotion, made silently |
| **branch** | A branch is **unmerged** code, invisible to the registry | A variant is **merged, registered and inert** — comparable and reproducible. Branches cannot appear on a leaderboard |
| **config override alone** | An override changes values only | XP-4: a variant may be **new code, new mathematics, a new library**. Treating it as config-only is what makes rel5's tool quant-only |
| **plugin** | A plugin implies **open extensibility** — anyone adds a seam | XP-15: the seam list is **finite and declared**. Unbounded seams are XP-5 returning through the back door (§4) |
| **fork of the domain** | A fork duplicates the domain and diverges | A variant plugs **behind an existing contract** (XP-12). A fork is two code paths that must be shown to agree — the bug class XP-10 exists to remove |
| **A/B test** | An A/B test splits **live traffic** and measures on real outcomes | There is no live traffic and one decision per day (INV-6). Evaluation is **historical and replayed** (§7) |
| **the baseline** | The baseline is what production runs **today** | ★ Confusing them is how *"enabled"* comes to mean *"live"*. **`enabled` = included in the next sweep I launch** (XP-34) |

## 5A.6 Lifecycle

```text
   written ──► registered ──► enabled ──► swept ──► ┬─► PROMOTED  → becomes the baseline (§8)
               (has id,       (in the     (has a    │              — an explicit, recorded act
                seam, hash)    next        result)  ├─► DISCARDED → result kept, code may go
                               sweep)               └─► INERT     → registered, never enabled;
                                                                    costs nothing, breaks nothing
```

★ **Only the PROMOTED branch touches production, and only through §8's gate.** Every other state is
invisible to the daily pipeline — which is XP-33/XP-34 restated in terms of a variant's own life.

| ID | Rule |
|---|---|
| **XP-41** | ★★ **One variant changes ONE thing.** ⚠ A variant that changes the model architecture *and* the feature set produces a score nobody can attribute — and a sweep of such variants is a list of anecdotes. **Where a combination genuinely must be tested, it is declared as a composite that names its constituent variants**, so the leaderboard can still separate them. *(This is what `blend_attribution.py` already exists to untangle after the fact; declaring it up front is cheaper.)* |
| **XP-42** | ★ **A variant is INERT by default.** Registering it changes nothing; enabling it changes only what the next manually-launched sweep includes (XP-33). ⚠ **There is no state in which a variant affects a production run without a promotion** |
| **XP-43** | ★ **A variant names its seam, and a seam it does not name is not admissible.** Without it, "what did this substitute?" is answerable only by reading the diff — and a leaderboard row whose meaning requires reading code is not a comparison |

## 5A.7 Two worked examples, at the extremes

> ⚠ Illustrative — neither has been run.

**A Fundamental variant (no training loop, minutes, ~$ tokens):**

```yaml
id: moat_v3_outcome_weighted
seam: fundamental.scorecard.rubric        # a declared plug point
substitutes: variants/fundamental/moat_durability_v3.py
baseline: baseline@2026-08-22
config:
  rubric_version: moat_durability@v3
protocol: pinned_bundle_regression        # RM-4's, reused — §7
changes: ONE — the moat rubric's criteria text          # XP-41
```

**A Quant/Models variant (full sweep, hours, GPU):**

```yaml
id: ranker_lgbm_depth8
seam: models.ranker.backend               # rel5's one implicit seam, now declared
substitutes: variants/models/lgbm_ranker.py
baseline: baseline@2026-08-22
config:
  hyperparameters: {max_depth: 8, num_leaves: 64}
protocol: cpcv                            # ← cpcv.py, reused
changes: ONE — the ranker backend                       # XP-41
```

★ **Same eight fields, same registry, same leaderboard — and one needs a GPU while the other needs a
prompt budget.** That symmetry is the argument for one harness (XP-17) stated as an artifact rather
than as a claim.

---

# 6. ARCHITECTURE — one harness, four surfaces

★ **XP-9's instinct (locality) is right; splitting the *harness* is the costly half.**

```text
   src/experiments/               ← ONE harness · SEAT-5 · neutral ground
   ├── registry.py                   variant registration + resolution
   ├── runner.py                     the sweep loop  (from experiment_runner.py)
   ├── evaluate/                     CPCV, walk-forward, purging  (from cpcv.py)
   ├── store.py                      run records, hashes, results
   ├── leaderboard.py                ★ cross-variant, cross-DOMAIN comparison
   └── promote.py                    ★ §8 — the gate

   └── variants/                  ★ ALL variant code lives HERE (XP-32) —
       ├── fundamental/             NOT under the domain it varies. §9A.2
       ├── quant/                   explains why locality was unsafe.
       ├── models/
       ├── risk/
       └── decision/
```

| ID | Proposed rule |
|---|---|
| **XP-17** | ★★ **The harness is shared; the variants are local.** Four separate harnesses would give **four incompatible result stores**, and *"did the new rubric or the new feature move the number?"* becomes unanswerable — ⚠ **which is the single most valuable question an experiment system answers.** A shared comparison footing is the product; the runner is just plumbing |
| **XP-18** | **D-10 stays SEAT-5 (L0 v0.22.0).** A harness owned by one analyst seat cannot be used by the others without borrowing their domain — the same argument that placed **D-02** and **D-12** |
| **XP-19** | ⚠ **D-12 experiments have nowhere else to live.** Composition spans three seats by construction, so a per-seat experiment domain has no home for it. **XP-9's four-domain split cannot express its own fourth case** |
| **XP-20** | ★ **The "interface" XP-8 asks for is the `CT-n.k` contract that already exists.** What is missing is not an interface but **injection**: the domain must be constructible with a non-default implementation. That is a constructor argument, not an architecture |

---

# 7. THE FOUR SURFACES — what actually varies, per domain

| Surface | What a variant substitutes | Evaluation protocol | Status |
|---|---|---|---|
| **Quant / Models** (D-03/D-04) | Model architecture, backend, hyperparameters, feature set, label horizon, blend weights | ★ **CPCV / walk-forward — already built** (`cpcv.py`), metric gate per constitution §4 | ✅ proven |
| **Fundamental** (D-01) | Rubric criteria and versions, prompt blocks, the scorecard dimension set, `evidence_coverage` definition, extraction strategies | ★ **Already specified: RM-4's pinned-bundle regression run** — a prompt or rubric edit re-runs a fixed bundle set and diffs the verdict distribution | ✅ protocol exists, harness does not |
| **Risk** (D-05) | Risk formulas, exposure definitions, limit arithmetic, scenario construction | Deterministic replay over a historical book from D-11 — ⚠ **no protocol specified yet** | ⚠ gap |
| **Decision** (D-12) | Composition rule, thresholds (`VETO_FLOOR`, `FLAG_FLOOR`), attribution | ⚠ **needs the counterfactual store** (DN-19/20) — and see XP-22 | ⚠ gap + caution |

| ID | Proposed rule |
|---|---|
| **XP-21** | ⚠ **A Risk variant may change thresholds and formulas; it may never change whether an alert can be suppressed.** **INV-026** gives D-05 zero authority and **RP-46** forbids suppressing an alert. ★ An experiment that made a flag suppressible would be an authority change wearing a configuration change |
| **XP-22** | ⚠ **A D-12 variant that FITS weights runs straight into `L2-signal-combination.md` §5.0**, which argues the meet is chosen *because it is a zero-parameter rule* (DeMiguel et al. — `1/N` beats fitted weights out of sample). ★ **The domain's own spec argues against the experiment you would most want to run**, and L2 §5.0's own review notes the argument **weakens only once `ρ` and both `IC`s are measured** — so this surface is **blocked on measurement, not on the harness** |
| **XP-23** | ★ **D-01's surface is the cheapest to build and the least obvious.** Its evaluation protocol is already written (RM-4, and the pinned bundle set `L1-fundamental-analysis-master-prompt.md` **MP-14** specifies) — **what is missing is only the runner.** A rubric variant needs no training loop and no GPU |

---

# 7A. ✅ QX-4 — D-01 PROMPTS ARE VARIANTS

> ✅ **Decided 2026-08-22 (Victor).** A prompt is not a separate lane. It registers, sweeps, promotes
> and is compared on the same leaderboard as a model backend or a risk formula.

## 7A.1 ★ The seam already exists — and INV-9 is the admission test

`L1-fundamental-analysis-master-prompt.md` **MP-2** already makes a prompt **composed, not written**:
every call is *shared blocks + exactly one task block*, each block individually hashed (**MP-11**),
with the call site declaring its composition (**MP-12**). ★ **That composition is the seam.** A
prompt variant substitutes **one declared block**, exactly as a model variant substitutes one
backend.

| ID | Rule |
|---|---|
| **XP-44** | ★★ **A prompt variant is a NEW, VERSIONED BLOCK — never an edit to an existing one.** `J-03@v2-outcome-weighted`, not a changed `J-03@v1`. ★ **INV-9's alignment checker then becomes the admission test for free**: it already refuses a call whose prompt has drifted from its declared composition, so a variant that tried to mutate a block in place **fails before it runs**. ⚠ *XP-13 — "a variant may change values, never shapes" — is enforced for prompts by a mechanism that already exists and was built for a different reason* |
| **XP-45** | ⚠ **A SHARED block (`S-1…S-9`) variant is a whole-system variant.** MP-13: a change to `S-5` reds *every* call that declares it. ★ **It does not violate XP-41 but it cannot pretend to be a one-call change** — it must be declared as system-wide and its sweep must cover **every call type**, not just the one that motivated it |

## 7A.2 ⚠ The collision: XP-30 cannot be met literally

**XP-30 says a variant that cannot reproduce itself cannot be promoted.** A prompt variant is
evaluated by an LLM. `L1-fundamental-analysis.md` §7.1 establishes that its output is **not**
reproducible — and **QP-1** records that `temperature` is **rejected outright on `claude-opus-5`**,
so the usual escape is not available either.

```text
╔══════════════════════════════════════════════════════════════════╗
║  REPRODUCIBILITY TRANSFERS FROM THE OUTPUT TO THE MEASUREMENT.   ║
║                                                                  ║
║  A config variant:  run once, compare to baseline once.          ║
║  A prompt variant:  the BASELINE ITSELF HAS VARIANCE, so         ║
║                     comparing one draw to one draw is noise.     ║
║                                                                  ║
║  ★ What must be reproducible is the variant_hash and the         ║
║    PROTOCOL — not the answer. The comparison is made on the      ║
║    DISTRIBUTION over k runs, exactly as RM-1/RA-62 already do    ║
║    for the production verdict.                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **XP-46** | ★★ **For an LLM-evaluated variant, XP-30's determinism requirement binds the `variant_hash` and the evaluation protocol — not the output.** The comparison is distributional: **the baseline is re-run under the same protocol in the same sweep**, never quoted from a previous run. ⚠ **A prompt sweep that compares `k` fresh variant runs against one remembered baseline number is measuring the wrong difference** |
| **XP-47** | ★ **The perturbation form is the right one here too** (RA-61/62). A prompt variant that wins only under one option ordering has not won |

## 7A.3 ★★ The risk this decision creates — and D-01 already named it

⚠ **`L1-fundamental-analysis.md` §7.5 warns against exactly what making prompts variants makes
easy:**

> *"The monitors are gameable. Tuning prompts until RM-6's base rate looks healthy optimises the
> metric, not the analysis. The metrics are diagnostics for a human, not objectives for a search —
> and the moment one becomes a target it stops measuring (Goodhart)."*

★ **A prompt sweep is, definitionally, a search over prompts against a metric.** The decision is
still right — the alternative is tuning prompts by hand against the same metrics with no record —
but it converts a warning into an operational hazard, and needs the mitigation stated.

| ID | Rule |
|---|---|
| **XP-48** | ★★ **`MP-14`'s pinned bundle set has ONE role today (regression) and now needs THREE.** A single set cannot both tune and judge — **XP-26**: *selection on the same data that justified the search is not evidence.* <br>★ **`regression`** — fixed, gates a release (AC-1.9), never used to choose a variant.<br>★ **`selection`** — what a sweep iterates against.<br>★ **`confirmation`** — held out, touched **once**, at promotion. <br>⚠ **Without the split, every promoted prompt is promoted on the set it was fitted to** |
| **XP-49** | ⚠ **A prompt variant may not be selected on RM-6 (verdict base rate) or RM-7 (score dispersion).** ★ **Those are the diagnostics §7.5 says become meaningless once targeted.** A prompt variant is judged on whether its *claims survive checking* — citation validity (RM-10), bear-case substance (RM-11), perturbation stability (RA-62), evidence coverage (RA-65) — **and, once N suffices, on calibration (RM-12)**, which is the only metric that cannot be gamed by writing more confidently |

## 7A.4 What it costs — and it is not the shape you would guess

| | Config variant | ★ **Prompt variant** |
|---|---|---|
| Compute | GPU-hours | **none** |
| Spend | electricity | ★ **deep-tier tokens** — Opus 5 |
| Runs needed | 1 per variant | ★ **`k` per variant, PLUS `k` for the baseline** (XP-46) |
| Wall clock | hours | minutes |

⚠ **Prompt caching does not rescue this the way it rescues RM-1.** The evidence bundle is the stable
cacheable prefix, but a prompt block lives **ahead of it** in the rendered order — so **substituting
a block invalidates the cached prefix for every bundle in the set.** A prompt sweep therefore pays
close to full input price per `(variant × bundle × k)`, where a same-prompt stability probe pays
almost none.

★ **The mitigation is already implied by XP-33:** a manual sweep is not latency-sensitive, so it is
**batch-eligible at half price**. ★ **Manual-only turns out to be a cost decision as well as a safety
one** — an automated sweep could not have used the batch path.

---

# 8. ★ THE PROMOTION GATE — the part that actually needs a spec

★ **The spec D-10 eventually needs is not "how to run an experiment." Running experiments is
solved (§2). It is "what must be true before a variant becomes the baseline."** That is the boundary
constitution **P7** draws — *research is exempt; promotion requires a spec* — and **today nothing
implements it.**

| ID | Proposed rule |
|---|---|
| **XP-24** | ★★ **Promotion is an explicit, recorded act with a named decider — never a config edit.** A variant that becomes the baseline by someone changing `settings.yaml` has been promoted without anyone deciding to |
| **XP-25** | ★ **A promoted variant carries its evidence:** the sweep it won, the sample it won on, the metric and its uncertainty, and **what it was compared against**. ⚠ **A winner with no runner-up recorded is a selection nobody can audit** |
| **XP-26** | ★★ **Selection on the same data that justified the search is not evidence.** This project has already paid for that lesson — `L1-quantitative-analysis.md` records CPCV existing precisely because walk-forward screening overstates a winner. **The promotion gate names which evaluation the promotion rests on, and it is not the screening one** |
| **XP-27** | **Promotion into a governed path requires the receiving domain's ACs to pass, plus a spec amendment if any contract changed** (P1, XP-13) |
| **XP-28** | ★ **The baseline is versioned and every production run records which baseline version produced it** (AP-6). ⚠ Without it, *"the numbers changed last Tuesday"* has no answer — and a promoted variant is indistinguishable from a bug |

---

# 9. DETERMINISM WHEN CODE VARIES

⚠ **The existing harness seeds the run. It does not pin the code**, because in rel5 the code was a
closed backend set. XP-4 breaks that assumption.

| ID | Proposed rule |
|---|---|
| **XP-29** | ★★ **A `variant_hash` covers the CODE as well as the config** — a content hash over the variant module, its config, the baseline version it overlays, the data snapshot, the seed and the library versions. ★ **This is `RA-2`'s `bundle_hash` argument applied to experiments**: two runs with different hashes are not comparable, and a comparison across them is meaningless |
| **XP-30** | **Constitution INV-2 applies to a variant exactly as to production**: same input + same config ⇒ byte-identical output. ⚠ **A variant that cannot reproduce itself cannot be promoted**, regardless of its score |
| **XP-31** | ★ **Library versions are part of the hash.** XP-4 explicitly includes *"new ML libraries"*, and an unpinned dependency is a silent variant nobody registered |

---

# 9A. ★ CONSEQUENCES FOR THE CODE DESIGN — the audit Victor asked for

> Checked 2026-08-22 against `L4-coding-standards.md` §1.1/§1.2/§1.5, `sdd/specs/ownership.yaml`,
> `ST-2`'s CI grep, and `L3-build-sequence.md` §B0. **Four findings; one of them reverses a rule in
> this very file and one is a live staleness bug.**

## 9A.1 ⚠ Live bug — `L4` had D-10 at the wrong seat

`L4` §1.2's domain→path map read **`D-10 | Experiments | SEAT-3`**. L0 **v0.22.0** moved D-10 to
**SEAT-5** so it could serve all three analyst seats, and the mechanical seat permutation renumbered
*seat 2 → seat 3* without applying the *move*. ✅ **Fixed** — but note the shape: **a rename pass
cannot see a reassignment**, and the two arrived in the same commit.

## 9A.2 ★★ The finding that reverses XP-14 — where variants may live

XP-14 put variant code under `src/<domain>/variants/`, reasoning that locality makes a variant
inherit its domain's import rules for free. **Two independent problems, either of which is fatal:**

```text
╔══════════════════════════════════════════════════════════════════╗
║  ① THE GLOB IS GOVERNED.                                         ║
║     ownership.yaml maps  src/fundamental/**  →  the D-01 spec.   ║
║     A variant there is spec-governed, so the sdd_gate hook       ║
║     demands the spec be read before editing it — for work        ║
║     constitution P7 explicitly EXEMPTS from spec rigor.          ║
║                                                                  ║
║  ② ★ ST-2'S CI CHECK IS BLIND TO IT.                             ║
║     The check is:                                                ║
║       grep -rn "experiments" src/ | grep -v "^src/experiments/"  ║
║     It greps for the NAME. A variant at                          ║
║     src/fundamental/variants/ contains no such name, so          ║
║     production importing it is an ordinary intra-domain          ║
║     import — invisible to the one rule that holds D-10.          ║
║                                                                  ║
║  ⚠ LOCALITY WOULD HAVE OPENED THE EXACT LEAK PATH ST-2 EXISTS    ║
║  TO CLOSE, IN A PLACE ST-2 CANNOT LOOK.                          ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **`ownership.yaml` already anticipated this** — `src/experiments/**` is listed among the
deliberately **ungoverned** paths, *"held by ST-2's one-way rule."* Putting variants anywhere else
would have needed a new exclusion; putting them under `src/experiments/variants/` needs **no
ownership change at all**. **The existing configuration was already telling us where they go.**

⚠ **The cost of the fix, stated:** a variant under `src/experiments/` can import anything, so the
seat independence XP-14 got free must now be **asserted** — **XP-32**. `ST-2` catches production
importing D-10; **nothing today catches a `variants/fundamental/` module importing `src/quant/`**,
which would be INV-014 breached inside the research lane.

## 9A.3 File-structure changes — applied to `L4` §1.1

```text
   src/experiments/            D-10 · P7-EXEMPT · SEAT-5
   ├── sweeps/        ← ohlcv/experiments/experiment_runner.py   (reuse)
   ├── tuning/        ← grid_gen.py                              (reuse)
   ├── evaluate/      ← cpcv.py                                  (reuse)
   ├── leaderboard/   ← leaderboard.py, tuning_report.py,
   │                    blend_attribution.py                     (reuse)
   ├── registry/   ★  ← experiment_config.py (VariantSpec)       (reuse)
   ├── store/      ★    run records · variant hashes · results   NEW
   ├── promote/    ★★   the P7 promotion gate                    NEW — §8
   └── variants/   ★★   fundamental · quant · models · risk ·    NEW
                        decision                                  (XP-32)
```

★ **Only three of the eight are new**, and `promote/` is the only one with no prior art at all —
which is the same conclusion §8 reached from the other direction: **the promotion gate is the part
that actually needs specifying.**

## 9A.4 What does NOT change — checked, so it is not re-litigated later

| Asked | Verdict |
|---|---|
| `ownership.yaml` | ✅ **No change.** `src/experiments/**` is already in the ungoverned list, and 9A.2 shows that is the right answer rather than a gap |
| **ST-2** itself | ✅ **No change.** Its grep works as written once variants live under `src/experiments/` — ⚠ **it was only ever going to fail under the placement XP-14 proposed** |
| The eleven governed globs | ✅ **No change.** No variant lands inside one |
| Each domain's §4 Module Decomposition | ✅ **No `variants/` entry** — variant code is not domain code |
| Each domain's §12 Public API Surface | ⚠ **Will change at B4, not now.** XP-20's injection means a domain must be *constructible with a non-default implementation*. That is a constructor argument per plug point, and **XP-15 requires the plug-point list to be finite and declared** — so it is a spec change per domain, deferred with the surfaces |
| `L3` §B0's CI import checks | ⚠ **One addition wanted**: XP-32's cross-seat check for variants. **B0 is the moment it is cheap** (BS-4: *"cheap on an empty tree and expensive on a full one"*), and **BS-5** applies — it ships with a test that deliberately violates it |

## 9A.5 ⚠ The one thing this audit could not settle

**`buffett/backtest/**` — 2,030 LOC, zero tests, disposition `EXCLUDE`, target "undecided"
(`L4` §1.5, open as **Q-9**).** It is the largest untested package in the repo and the obvious
place a Fundamental or Risk *evaluation protocol* would come from (XP-11d says the reused runner is
quant-shaped and has none). ★ **So D-10's Risk and Decision surfaces have a plausible dependency on
a package nobody has decided to keep** — Q-9 stops being a tidy-up question and becomes a blocker
for two of the four surfaces.

---

# 9B. ✅ MANUAL-ONLY — the isolation is temporal as well as structural

> ✅ **Decided 2026-08-22 (Victor):** *"variants and experiments live entirely under D-10, and are
> triggered manually. Daily normal pipeline tasks carry on normally; experiments run on my command
> only. I do not foresee any experiment related to automation."*

★ **This is a stronger guarantee than ST-2 alone gives.** ST-2 stops an experiment leaking into
production **by import**. Manual-only stops it leaking **by execution** — and those are different
failure modes: an import leak is a code defect, a schedule leak is an operational one, and nothing
before this decision addressed the second.

| ID | Rule |
|---|---|
| **XP-33** | ★★ **No experiment is ever scheduled.** No cron, no daily-path step, no D-08 trigger, no "run the sweep after the pipeline" hook. **D-08 never invokes D-10** — already implied by ST-2 (a scheduler that invoked D-10 would import it) and now stated where a reader will find it, in `L1-orchestration.md` §1.6 |
| **XP-34** | ★ **The daily pipeline is unaffected by the existence of a variant.** A registered, enabled, even winning variant changes **nothing** about production until a promotion changes the baseline (XP-24). ⚠ *"Enabled"* in `experiments.yaml` means *"included in the next sweep I launch"*, never *"live"* |
| **XP-36** | ✅ **QX-6 is closed by construction.** A variant cannot become permanent by neglect because no unattended process ever runs one. ★ **The residual risk is a different one and is already covered**: the baseline changing without a recorded decision — XP-24 (promotion is an explicit act) and XP-28 (every production run records its baseline version) |
| **XP-37** | ★ **Manual-only makes the promotion gate cheaper to build.** XP-24 wanted *"an explicit, recorded act with a named decider"*. With no automation to design around, `promote/` is a CLI that writes a record — not a workflow engine |

## 9B.1 ★★ The boundary that would otherwise be crossed by accident

⚠ **The same runner has two callers, and only one of them is an experiment.**

| | **Regression** | **Sweep** |
|---|---|---|
| What varies | ★ **nothing** — a fixed pinned set | ★ **the variant** |
| Purpose | *has production changed behaviour?* | *is this candidate better?* |
| Cadence | **automated** — runs in CI | **manual only** (XP-33) |
| Gates a release? | ✅ **yes** — AC-1.9, RM-4, RM-5 | ✗ **never** |
| Domain | production QC — belongs to the domain it checks | **D-10** |

| ID | Rule |
|---|---|
| **XP-35** | ★★ **A run in which nothing varies is a REGRESSION, not an experiment** — and regressions are automated and may gate a release. **A run in which a variant varies is an experiment, and is manual and never gates anything.** ⚠ **Without this line someone wires the sweep into CI "because it is the same runner", and D-10 becomes a scheduled dependency of the release** — which is XP-33 defeated by convenience |

> ★ **D-01's RM-4 is the live example.** *"A prompt change without an RM-4 regression run blocks
> release"* (AC-1.9) is **automated and correct** — it re-runs a **fixed** bundle set and diffs the
> verdict distribution. Nothing varies except the thing under test. **It is not an experiment**, and
> it belongs to D-01, not D-10, even though it will share the evaluate/ code.

---

# 9C. ✅ QX-7 / Q-9 — `buffett/backtest/**` is HARVESTED, not copied

> ✅ **Decided 2026-08-22 (Victor):** *"transfer the tests, patterns and designs into D-10 — but not
> a blind copy of the entire folder."*

⚠ **One correction to the premise, verified against the repo: the package has ZERO tests.** Only
`tests/test_sdd_process.py` mentions it, and that is the SDD meta-test counting coverage, not
exercising the code. **So there are no tests to transfer.** What is worth taking is the **designs**,
and — from the rel4 archive — the **measured results** those designs produced.

| ID | Rule |
|---|---|
| **XP-38** | ★ **Class changes `EXCLUDE` → `REBUILD`** (`L4` §1.5): *written fresh in `src/`, no history to preserve*. ⚠ **REBUILD does not mean "start from a blank page"** — §9C.1 is a **required reading list**, and rebuilding without reading it discards the only measured evidence this project has about which evaluation methods work |
| **XP-39** | ⚠ **Nothing is `git mv`-ed.** A move would carry 2,030 untested lines into `src/` and `L3` **BS-21** (green at every commit) would be satisfied only because nothing tests them. **Untested code that moves becomes untested code that ships** |

## 9C.1 The harvest list — what to read, and what it is for

| Source | What it gives D-10 |
|---|---|
| ★★ **`iv_replay.py`** | **A point-in-time FUNDAMENTAL backtest.** Builds a (ticker, quarter-end) observation grid, uses only the filings knowable at `as_of`, computes IV and margin of safety, and **documents why each non-PIT path is deliberately skipped** (TTM is enricher-filled; the validator phones FMP with today's values; FMP profile gives current shares). ★ **This is the Fundamental-surface evaluation protocol XP-11d said was missing** — it already exists and is already PIT-aware |
| **`pit_data.py`** | The point-in-time observation-grid pattern that `iv_replay` stands on. Also relevant to D-07 |
| **`method1_forward_returns.py`** | Forward-return evaluation — ★ **and rel4 recorded it PASSING** (+31.6 %/yr Q1−Q5 spread, t = 5.38). A method with a measured result is worth more than one without |
| **`method5_mean_reversion.py`** | ★ **Recorded FAILING** in rel4. ⚠ **Keep the record of the failure** — a method known not to work is evidence, and rebuilding it unknowingly is how a dead end gets re-walked |
| **`method2_long_short.py`** | Long/short spread construction — ⚠ **out of mandate (M-1: long-only, no shorts)**, so it is a *pattern* reference only, never a surface |
| **`runner.py`, `report.py`** | Superseded by `experiments/sweeps/` and `experiments/leaderboard/` (XP-11a). **Read for shape, do not carry** |

| ID | Rule |
|---|---|
| **XP-40** | ★ **A harvested method carries its recorded RESULT, not only its code.** Method 1 passed and Method 5 failed on measured evidence in rel4. ⚠ **Rebuilding a method while dropping the record of whether it worked is the most expensive kind of tidy-up** — it costs the measurement, which is the part that took years of data to earn |

---

# 10. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QX-1** | Does this file's existence violate L0 §4.2 / BS-23? | ★ **No — deliberately.** It captures intent and audits feasibility; it declares no ACs and governs no path. **The L1 spec still waits for B3.** But the boundary is thin and worth watching |
| **QX-2** | Do the four surfaces land at **B4** with their domains, or later as one milestone? | Leaning: the **harness** at B4 with D-04 (it is already needed there), the **Fundamental surface** next because it is cheapest (XP-23), Risk and Decision after their protocols exist |
| **QX-3** | Where do variant **results** live — D-11 Recording, or D-10's own store? | D-11 has custody of *the fact* about the book. An experiment result is not a fact about the book. ★ Leaning D-10's own store, with D-11 recording only **promotions** |
| ~~**QX-4**~~ | ~~Is a **prompt** a variant, or a separate lane?~~ | ✅ **CLOSED 2026-08-22 — a prompt IS a variant** (Victor). §7A. ★ It costs `k×` runs and a second bundle set; it buys one comparison surface and reuses INV-9 as the admission test |
| ~~**QX-5**~~ | ~~How much of `pipeline/ohlcv/experiments/` migrates vs is rewritten?~~ | ✅ **CLOSED 2026-08-22 — REUSE** (Victor). See §2a. ★ **The tension was apparent, not real**: `L4` §1.5 classes `ohlcv/experiments/**` as **REVIEW**, which already means *move first, rewrite against a written AC in a later commit — never both at once*. **BS-22 governs the DELETE/EXCLUDE class** (`backtester.py`'s hard-coded capital); **P4 governs the REVIEW class.** Both rules stand and they were never addressing the same files |
| ~~**QX-7**~~ | ~~Does `buffett/backtest/**` (Q-9) become D-10's evaluation substrate, or is it dropped?~~ | ✅ **CLOSED 2026-08-22 — HARVESTED, not moved** (Victor). §9C. `L4` Q-9 closes with it; the row moves **EXCLUDE → REBUILD** |
| ~~**QX-6**~~ | ~~What stops a variant becoming permanent by neglect?~~ | ✅ **CLOSED 2026-08-22 — nothing unattended ever runs a variant** (§9B, XP-33). ★ The question assumed a scheduled experiment; there is none. **The residual risk is different and already covered**: not *"a variant ran for a year"* but *"the baseline changed and nobody recorded it"* — XP-24, XP-28 |

---

# 11. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §1.2, §4.2 **D-10**, §4.1 | the research-lane requirement; D-10's seat-5 placement and its "no spec before B3" decision |
| `L3-build-sequence.md` **BS-22**, **BS-23**, §3A | what is not built, and when D-10 unblocks |
| `sdd/specs/constitution.md` **P1**, **P4**, **P7**, **INV-2**, **INV-4**, §4 | spec before code · reuse before rebuild · the research exemption and its promotion boundary · determinism · parity · the metric-gate tier |
| `L2-signal-combination.md` **§5.0** | ⚠ why a D-12 weight-fitting experiment is contested by the receiving domain's own spec |
| `L1-fundamental-analysis.md` **RM-4**, **RA-33**, §7.4 · master-prompt **MP-14** | D-01's evaluation protocol and its pinned bundle set — the Fundamental surface's protocol, already written |
| `L1-risk-management.md` **INV-026**, `L1-reporting.md` **RP-46** | why a Risk variant may change thresholds and never suppressibility |
| `L1-decision.md` **DN-19/20/21** | the counterfactual store a D-12 surface would evaluate against |
| `L4-coding-standards.md` **ST-2**, **ST-5** | the one-way import rule that keeps an unspecified D-10 safe, and the gateway restriction a variant inherits by location |
| `pipeline/ohlcv/experiments/**` | ★ **1,978 LOC of prior art — read before designing** (P4) |
