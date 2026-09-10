# F1 — Module protocol & registry (SPI)

> **Spec-ID:** F1 · **Status:** 🟢 **approved** · **Adopted:** 2026-09-03
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §D.5 · §H.1 ·
> [`../../questions.md`](../../questions.md) `QR-7`, `QR-8`
> **Milestone:** `MS-1` — [`../../design/rel1_design/L3-build-sequence.md`](../../design/rel1_design/L3-build-sequence.md)
> **Governs:** `constitution.md` — enforces `PG-8`, `PG-9`; inherits `P5`, `CA-3`, `AP-6`.
> **Capability:** `C1` (plugin architecture / SPI), and the substrate `C8` (governance) stands on.
>
> ✏ **Amended 2026-09-03 (`A1`), same day, from findings raised by the `MS-1` build.** Five defects the
> spec review could not have found because they only surface when code is written against it — a
> contradiction between `CT-1.3` and `CT-1.4`, an unmechanised term in `AC-F1.12`, a residual
> false-positive in `AC-F1.7`, a missing method, and an untested contract. See §7 `A1`.
>
> ✅ **Approved 2026-09-03** after review `S1`. Its ACs are now binding: code in the governed paths
> must satisfy a named `AC-1.<k>`, and changes go through constitution §5.
> ⚠ Open questions `Q1`–`Q3` were resolved as `D1`–`D3` (§7) — **read §7 before changing §5 or §6**,
> because the rejected options are recorded there and should not be re-argued from scratch.

---

## 1. Goal & why

**One registry, keyed by `(port, variant)`, through which every swappable implementation in the system
is registered and resolved.** A port declares a contract; adapters implement it; the registry maps a
name to a way of building one; and a single contract-test suite proves every adapter is actually
substitutable.

This is the mechanism behind capability `C1` and behind the **vertical scalability axis**
(`vision.md` §6): a module is improved or replaced behind an unchanged contract without its callers
knowing. It is also what makes `C8` possible — an output can name *which implementation version*
produced it.

★ **It is deliberately first.** `MS-1` is the only platform milestone with no pipeline dependency: a
registry and a protocol can be built and fully contract-tested in isolation, so this spec is writable
and approvable while `MS-0` is still in flight.

> ⚠ **The interface is the easy half.** A satisfied type signature does **not** make an implementation
> substitutable — the upstream `MU`-71 % incident is a case where two adapters shared a signature and
> differed in a guarantee nobody had written down. §5's ports must state guarantees, and §6's `AC-F1.9`
> is what makes them checkable.

## 2. Scope / non-goals

**In scope**
- The registry: registration, resolution, coverage validation, versioning, experimental tagging.
- The **closed variant set** rule and its consequences (`QR-7`).
- Per-run instance caching.
- `AgentPort` — declared here as **one registered port among several**, not as the registry's purpose.
- The contract-test *harness pattern* every port must use.

**Non-goals (this spec)**
- ✗ **Hot reload / code swap without restart** — cut by `QR-7`, and a durable non-goal (`vision.md` §7).
- ✗ **Lazy or dynamic variant discovery** — excluded by the closed-set rule; see `AC-F1.5`.
- ✗ **A dependency-injection container.** Resolution happens at a composition root and the resolved
  object is passed downward. This spec does not introduce framework-wide injection.
- ✗ **The semantics of any particular port.** `PricePort`, `RankingModelPort`, `ThesisSourcePort` (`F9`)
  and the rest each define their own contract in their own spec. F1 defines only the *mechanism* and
  the *obligations a port declaration must meet*.
- ✗ **Routing** — choosing *which* variant is `F6a`. F1 only resolves the name it is given.
- ✗ **Tracing** — recording the resolution is `F2`. F1 must *expose* the provenance record (`CT-1.4`);
  it does not persist it.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | Process start — every variant is registered | module import / explicit wiring call | `src/shared/registry/wiring.py::register_all` |
| T2 | Process start — coverage is validated before work begins | list of required ports, from config | `Registry.validate_coverage` |
| T3 | Composition root resolves an implementation | `(port, variant)`; variant from config (`T3a`) or from a routing function (`T3b`, `F6a`) | `Registry.resolve` |
| T4 | Test suite enumerates variants to run a contract suite against | `port` | `Registry.variants` |

## 4. Behaviour & reuse (the lean "how")

- **Ports are pure typing.** A port is a `typing.Protocol` in a module containing declarations only —
  no implementation, no I/O, no SDK import. Inherits `CA-3`. ★ Structural typing is chosen over `ABC`
  so a third-party or upstream class can satisfy a port without inheriting from it, which matters at
  absorption (`PG-8`).
- **The registry stores factories, not instances.** Registering a live object would force construction
  at import time and couple registration order to configuration.
- **Registration is fail-loud.** A duplicate `(port, variant)` raises. ⚠ Silent overwrite makes import
  order load-bearing — inherits `P5`.
- **The variant set is closed.** Everything selectable is registered at startup; resolution never
  discovers, imports or loads a variant that was not (`QR-7`). ★ This is what makes the hot-reload
  non-goal *structural* rather than merely stated.
- **Coverage is validated once, at startup.** ⚠ The registry is a *service locator*: it trades a
  compile-time error for a runtime one. `validate_coverage()` is the mitigation that turns a 3 a.m.
  `KeyError` into a boot failure.
- **Resolution caches per `(port, variant)` within a run scope.** A model load is expensive and
  per-ticker selection may resolve the same variant hundreds of times.
- **Every entry carries a version**, and every resolution yields a provenance record, so an output can
  answer *"which implementation produced this?"* (`AP-6`, `C8`).
- **Experimental variants are tagged and the tag propagates.** Seat 9 swaps an experimental variant in,
  runs the pipeline, swaps it back; ⚠ nothing it produces may be mistakable for production output
  (`PG-2`).
- **One contract suite per port, parameterised over every registered variant.** ★ This — not the
  registry — is what makes substitution *safe*.

## 5. Contracts (inline)

**CT-1.1 — `Key`** (in-memory; the registry's key):
```json
{ "port":    "str — stable port name, e.g. 'price', 'ranking_model', 'agent.fundamental'",
  "variant": "str — stable variant name, e.g. 'edgar', 'lightgbm', 'scorecard'" }
```
Rules: both non-empty; `[a-z0-9_.]+`; the pair is unique across the registry; **neither is ever
renumbered or reused for a different implementation** — they appear in provenance records that outlive
the code.

**CT-1.2 — `Entry`** (in-memory; what a registration stores):
```json
{ "factory":      "Callable[..., object] — builds the implementation; NOT the instance",
  "version":      "str — semver of the IMPLEMENTATION, not of the port",
  "experimental": "bool — default false. Real code being TRIALLED",
  "fixture":      "bool — default false. ⚠ A STAND-IN, not an implementation: a test
                   double, null object or stub. Added by A1 — AC-F1.12 said 'two real
                   (non-fixture) variants' with no way to tell one from the other,
                   so the count was silently wrong. Distinct from `experimental`:
                   an experimental variant is real code on trial; a fixture is not
                   an implementation at all",
  "port_type":    "type — the Protocol this entry claims to satisfy. ★ Its JOB is to map
                   port → contract suite (AC-F1.9); it is not a runtime type assertion,
                   because @runtime_checkable only verifies method NAMES, not signatures
                   or semantics" }
```

**CT-1.3 — Registry API surface** — ★ **methods on a `Registry` class, not module-level functions**
(`D1`). Consumers receive a registry by **constructor injection**; there is no importable singleton.
- `Registry()` → a fresh, empty registry. ★★ **Its lifetime IS the run scope** (`D1`, `AC-F1.6`).
- `register(port, variant, factory, version, experimental=False, fixture=False) -> None`
  → raises `DuplicateRegistration` if `(port, variant)` exists.
- `resolve(port, variant) -> object`
  → raises `UnknownVariant(port, variant, available)` — ⚠ **`available` is required**, so a typo
  diagnoses itself.
  ★ **No runtime arguments.** Variant configuration happens at *registration*, beside `version` and
  `experimental`. ⚠ Runtime kwargs would break two things at once: the `(port, variant)` cache key
  (`AC-F1.6`) would silently return an instance built with a different call's arguments, and `AC-F1.8`'s
  *"provenance is fully determined by the registry entry"* would become false — two resolutions
  behaving differently while reporting identical provenance.
- `variants(port) -> tuple[str, ...]` → registered variant names, sorted. Used by T4.
- `validate_coverage(required_ports=None) -> CoverageReport` → raises `IncompleteRegistry(missing)`.
  ⚠ **`required_ports` defaults to `src.shared.ports.__all__`** minus entries marked optional (`D2`).
  Passing an explicit list is for **tests only** — production never passes one, because the point of
  `D2` is that there is no second list to keep current.
  Returns `CoverageReport` for `AC-F1.12`'s warnings (a *raise* still wins over a *report*).
- `resolve_with_provenance(port, variant) -> tuple[object, Provenance]` — the instance and its record
  together. ⚠ **Added by `A1`** to settle a contradiction: `CT-1.3` typed `resolve` as returning the
  object while `CT-1.4` said Provenance is *"returned by `resolve`"*. **`resolve` returns the object**;
  a caller that needs both asks for both. ★ Keeping `resolve`'s return type narrow is what lets `F6a`
  route and `F2` trace without either depending on the other's payload.
- `provenance(port, variant) -> Provenance` → `CT-1.4` without constructing the implementation.
- `ports() -> tuple[str, ...]` → every port with at least one registered variant, sorted.
  ⚠ **Added by `A1`.** `AC-F1.9`'s meta-test cannot check *"a variant registered without being added to
  the suite causes a failure"* without enumerating what is registered — the AC was unimplementable
  without it.

**CT-1.4 — `Provenance`** (returned by `provenance()` and by `resolve_with_provenance()`; ⚠ **not** by
`resolve()` — corrected by `A1`; consumed by `F2`):
```json
{ "port": "str", "variant": "str", "version": "str", "experimental": "bool" }
```
Rules: immutable; **fully determined by the registry entry**, never by the resolved object.

**CT-1.5 — `AgentPort`** (one registered port among several):
```json
{ "capability": "property -> AgentCapability — seat, domain, version, supported message types",
  "analyze":    "(ticker: str, context: Mapping) -> Mapping — this seat's view of one ticker" }
```
⚠ Message handling (`respond_to_message`) is **not** in F1 — it belongs to `F6b` and is added there if
and when `F6b` graduates (gated on `F7a`, `PG-5.1`).

## 6. Acceptance criteria (Given / When / Then → test tier)

- **AC-F1.1** *(duplicate registration is loud)* — **Given** `(port, variant)` is registered, **when**
  the same pair is registered again, **then** `DuplicateRegistration` is raised and the first entry is
  unchanged. → *unit.* (`P5`)
- **AC-F1.2** *(unknown variant names the alternatives)* — **Given** a registry with variants of `port`,
  **when** an unregistered variant of that port is resolved, **then** `UnknownVariant` is raised **and
  its message lists the registered variants for that port**. → *unit.* (`P5`)
- **AC-F1.3** *(factories, not instances)* — **Given** a registered factory, **when** registration
  occurs, **then** the factory is **not** invoked; **when** `resolve` is first called, **then** it is.
  → *unit.*
- **AC-F1.4** *(coverage fails at boot)* — **Given** a port declared in **`src/shared/ports/__all__`**
  and not marked optional (`D2`), **when** `validate_coverage` runs with no variant registered for it,
  **then** `IncompleteRegistry` is raised naming every missing port. → *unit.*
- **AC-F1.13** *(★★ declaring a port IS requiring it — `D2`)* — **Given** a new `Protocol` added to
  `src/shared/ports/__all__` with no variant and no optional marker, **when** `validate_coverage` runs,
  **then** it fails. → *invariant / property (structural).*
  > ★ This is the whole point of `D2`: the drift that a hand-kept list permits — *add a port, forget the
  > entry, coverage silently stops checking it* — becomes impossible rather than merely discouraged.
  > "This port is optional" must be **stated**, never achieved by omission.
- **AC-F1.5** *(★ the variant set is closed)* — **Given** any variant name not registered **at registry
  construction** (`D1` — a real moment, where *"startup"* was a vague one),
  **when** it is resolved, **then** `UnknownVariant` is raised — **and no import, module load or
  filesystem lookup is attempted**. → *invariant / property.* (`QR-7`; makes `vision.md` §7's
  hot-reload non-goal structural)
  > ⚠ `D2` reads `ports.__all__` **at construction**, which is a plain list lookup, not a scan. This AC
  > constrains **resolve** time and is untouched by it.
- **AC-F1.6** *(per-registry caching — ★ the `Registry` instance IS the run scope, `D1`)* — **Given** a
  registered factory, **when** the same `(port, variant)` is resolved `n > 1` times **on one `Registry`
  instance**, **then** the factory is invoked **exactly once** and every call returns the same object;
  **and** a second `Registry` built from the same registrations invokes the factory again and returns a
  **different** object. → *unit.*
  > ★ The second clause is the one that matters. It is what makes *"run scope"* checkable instead of
  > interpretive, and what stops a long-lived `F8` process serving day 2 from day 1's cache.
- **AC-F1.7** *(⚠ no state leaks between calls — the obligation caching depends on)* — **Given** any
  registered variant **with its external dependencies held fixed** (`A1`), **when** **the port's primary
  method, as named in its own contract**, is called with input `A` and then input `B` on the same
  instance, **then** `B`'s result equals the result of calling `B` on a **fresh** instance.
  → *invariant / property, run against every registered variant.*
  > ⚠ **`A1` — the clause `S1-4` missed.** The A-then-B form compares *outputs*, so an adapter reading a
  > world that moves **between the two calls** fails it — reintroducing, by another route, exactly the
  > false positive `S1-4` removed from the idempotence form. A `PricePort` against a live vendor fails a
  > correct implementation unless the vendor is stubbed. **A contract suite that cannot hold its port's
  > external world fixed cannot run this AC**, and must say so rather than report a pass.
  > ⚠ **This is deliberately NOT an idempotence test.** *"Same input twice → same output"* would
  > **fail a correct adapter**: a `PricePort` hitting a live vendor legitimately returns different
  > results if the data moved. What `AC-F1.6`'s instance caching actually requires is that **no
  > caller-visible state carries from one call to the next** — which is what the A-then-B form tests.
- **AC-F1.8** *(provenance is complete and entry-derived)* — **Given** a resolution, **when**
  `Provenance` is read, **then** it carries `port`, `variant`, `version` and `experimental`, and its
  values equal the registry entry's — **not** anything reported by the resolved object.
  → *data contract.* (`AP-6`, `C8`)
- **AC-F1.9** *(★★ every variant faces the same contract suite)* — **Given** a port with a contract
  suite, **when** the suite runs, **then** it executes once per name in `registry.variants(port)` —
  the suite being selected by the entry's **`port_type`** — and **a variant registered without being
  added to the suite causes a failure**. → *invariant / property (meta-test over the
  parameterisation).* (`A3` — the rule that makes substitution safe)
- **AC-F1.10** *(ports carry no implementation)* — **Given** any module declaring a port, **when** it is
  inspected, **then** it contains only `Protocol` declarations, type aliases, `__all__`-style literal
  bindings, and imports **from `typing`/stdlib typing modules** — ⚠ **no module-scope call, no I/O, no
  vendor SDK import, and no control flow at module scope**.
  → *invariant / property (structural).* (`CA-3`, `A2`)
  > ✏ `A1`: *"no executable statement"* was literally false — a binding like `__all__ = ()` is an
  > executable statement, and `D2` **requires** one. The ban is on **calls and side effects**; a literal
  > binding is a declaration. Written down because the implementer otherwise decides it privately.
- **AC-F1.11** *(experimental output is never mistakable for production)* — **Given** a variant
  registered with `experimental=True`, **when** it is resolved, **then** `Provenance.experimental` is
  `True`; and **when** any artifact is produced from it, **then** that artifact carries the flag.
  → *data contract.* (`PG-2`)
- **AC-F1.12** *(★ earned abstraction is reported, not enforced)* — **Given** the registry at
  construction, **when** coverage is validated, **then** every port **in the same `D2` list** with fewer
  than **two variants registered with `fixture=False`** is **listed as a warning** — ⚠ **and the build
  does not fail**. → *unit.* (`A4`)
  > ✏ `A1`: *"real (non-fixture)"* previously named a distinction `CT-1.2` could not express, so the
  > count included stand-ins and the warning was quietly wrong in the one direction that matters —
  > **under**-reporting. `fixture` makes it checkable.
  > ★ **Why a warning and not a gate.** *"Abstraction is earned"* is a judgement. A hard test on it is
  > either **vacuous** — the earlier wording let a test double count, so every port passed — or it
  > **blocks legitimate work**: `AgentPort` has one real implementation on day one and would fail the
  > build. A warning list gives visibility without false precision, and `AgentPort` simply sits on it
  > until a second implementation exists, which is *true and useful*.

- **AC-F1.15** *(`CT-1.1`'s key rules are enforced, not merely stated — `A1`)* — **Given** a port or
  variant name that is empty or does not match `[a-z0-9_.]+`, **when** it is registered, **then**
  `InvalidKey` is raised naming the offending field. → *unit.* (`P5`)
  > ✏ `A1`: `CT-1.1` stated these rules and **no AC tested them**, so the implementation enforced them
  > on its own authority — an improvisation the constitution §5.1 table lists as the illegal move.
  > ★ They matter because a key *"appears in provenance records that outlive the code"*: a mixed-case
  > or whitespace-bearing name is unfixable once written to a trace.
- **AC-F1.14** *(⚠ single-threaded, and it says so out loud — `D3`)* — **Given** a `Registry`
  constructed on thread `T`, **when** `resolve` is called from any other thread, **then**
  `ConcurrentRegistryAccess` is raised naming both threads. → *unit.*
  > ★ Fails **loud**, per the house rule. `INV-2` (reproducibility) is a property of the whole
  > invocation, and upstream's `models/zoo/gbdt.py` already requires single-threading to hold it. The
  > alternative — a lock around the cache — would guard the *dict* while leaving the *shared instance*
  > exactly as exposed, i.e. it would look like a fix and not be one.

## 7. Decisions (resolved questions — kept with their rejected options)

> ⚠ **Recorded so they can be re-explained, not just obeyed.** Each entry keeps the options that were
> rejected and why — a later reader (human or agent) should be able to reconstruct the argument
> without this conversation.

**`D1` — "Run scope" means: the lifetime of one `Registry` instance.** One registry is constructed per
run; consumers take it by constructor injection. *(Resolves `Q1`; rewords `AC-F1.5`, `AC-F1.6`, `CT-1.3`.)*

- ⚠ **The fact that decided it:** a run is **already not a process**. `F8` §4 states a run may pause and
  resume *"possibly after a process restart"* (`AC-8.7` tests it), so process-lifetime is false the day
  suspend/resume lands — not merely inelegant.
- **Rejected — process-lifetime cache (module-level dict).** Free, and wrong: a long-lived `F8` process
  serves day 2 with an instance built from day 1's config, **silently**.
- **Rejected — an explicit `RunScope` threaded through `resolve()`.** Correct, but re-opens the
  signature `S1-6` had just closed: `resolve` grows a third parameter at every call site.
- **Rejected — cache keyed `(port, variant, run_id)`.** `run_id` arrives either as a parameter (= the
  option above) or as an ambient global (= a hidden dependency). No third way.
- **Cost accepted:** no importable singleton, which is the conventional Python shape. Bought back as
  the dependency inversion `A2` wants anyway, plus **test isolation for free** — a fresh registry per
  test instead of order-dependent global state, the classic flake source for this pattern.
- ⚠ A restart mid-run rebuilds the cache. That is **correct**: the cache is a performance device, and
  `AC-F1.7` guarantees the instances are stateless, so rebuilding costs time and nothing else.

**`D2` — `required_ports` is derived from `src/shared/ports/__init__.py`'s `__all__`**, minus entries
carrying an explicit optional marker. Declaring a port *is* requiring it. *(Resolves `Q2`; feeds
`AC-F1.4`, `AC-F1.9`, `AC-F1.12`, `AC-F1.13`.)*

- ⚠ **The asymmetry that decided it:** a hand-kept list that names a *deleted* port fails loudly at boot
  (harmless). One that *omits a new* port silently stops checking it (harmful). Only derivation removes
  the harmful direction.
- **Rejected — a YAML config list.** Permits exactly that silent omission.
- **Rejected — a hand-maintained manifest module.** The same failure, relocated from YAML to Python.
- **Why `__all__` and not a filesystem scan:** it is a plain list, no import magic — and `L4` `ST-3`
  already holds that `src/<domain>/__init__.py` **is** the domain's public API surface. This makes that
  claim load-bearing rather than decorative.
- ★ One list, four consumers: coverage (`AC-F1.4`), contract-suite mapping (`AC-F1.9`), the earned-
  abstraction warning (`AC-F1.12`), and the drift guard (`AC-F1.13`).

**`D3` — The registry is single-threaded, asserted rather than assumed.** *(Resolves `Q3`; adds
`AC-F1.14`.)*

- **Evidence, not preference:** upstream `src/models/zoo/gbdt.py` — *"Determinism is not LightGBM's
  default… single-threading [is] required, or repeated fits differ in the low bits — and **`INV-2` is a
  property of the whole invocation**."* Concurrency is excluded upstream **on purpose**. Upstream
  `orchestration/state/locks.py` `OR-24` is *in-process* mutual exclusion between **runs**, not threads.
- **Rejected — add a lock around the cache now.** Licenses concurrency `INV-2` does not want, and guards
  the wrong object: the hazard is two threads sharing one resolved instance, not the dict.
- **Rejected — defer and record only.** Leaves the answer discoverable solely through a
  non-reproducible diff. The assertion converts that into an immediate, named failure.
- ⚠ **Where this gets reopened deliberately:** `F6b`. LLM latency dominates deliberation and the agent
  calls are independent, so parallelism will be tempting. `AC-F1.14` guarantees that attempt announces
  itself instead of quietly costing reproducibility.

**`A1` — Amendment 2026-09-03, from the `MS-1` build.** ★ Five defects found by *writing code against
the spec*, which is a different instrument from reviewing it. Recorded together because the pattern
matters more than any one of them: **each was a place the spec read fluently and could not be
implemented as written.**

| # | Defect | Fix | Class |
|---|---|---|---|
| 1 | `CT-1.3` typed `resolve -> object`; `CT-1.4` said Provenance is *"returned by `resolve`"* | `resolve` returns the object; added `resolve_with_provenance()` | ⚠ **contradiction** — two contracts, no possible implementation |
| 2 | `AC-F1.12` counted *"real (non-fixture)"* variants; `CT-1.2` had no way to tell | added `fixture: bool` to `CT-1.2` and `register()` | **unmechanised term** — the count was silently under-reporting |
| 3 | `AC-F1.7` compares outputs, so an adapter reading a moving world fails it | added *"with its external dependencies held fixed"* | ⚠ **residual false positive** — `S1-4` closed the idempotence route, not this one |
| 4 | `CT-1.1`'s key rules had no AC | added `AC-F1.15` (`InvalidKey`) | **untested contract** — enforced on the implementer's authority |
| 5 | `AC-F1.10` banned *"executable statements"*, but `D2` requires `__all__ = ()` | ban module-scope **calls**; a literal binding is a declaration | **literally false as written** |

> ★★ **What this says about the process.** `S1` was a careful review that found eight issues, and it
> found **none of these five** — because reading a spec checks whether it is *coherent*, while
> implementing it checks whether it is *executable*. ⚠ The two failure modes that recur here are
> **a term with no mechanism** (#2) and **two contracts that cannot both hold** (#1). Both read fine.
> The lesson is not "review harder"; it is that **the first implementation is part of the review**, and
> a spec should not be considered settled until something has been built against it.

## 8. Open questions (must resolve before/at implementation)

> ✅ **None blocking.** `Q1`–`Q3` are resolved above as `D1`–`D3`; `Q4` dissolved at `S1-5`.
> Their rejected options are kept in §7 — do not re-litigate them without reading it first.

- ~~**Q4 — Does `AC-F1.12` hold for `AgentPort` on day one?**~~ ✅ **Dissolved 2026-09-03 (S1-5).**
  `AC-F1.12` now **warns rather than fails**, so a port with one real implementation is *reported*, not
  a build break. `AgentPort` sits on the warning list until a second implementation exists.

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet, and no test may be marked green before it has been run.

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-F1.1 | `tests/unit/test_registry.py::test_ac_f1_1_duplicate_registration_is_loud` | `src/shared/registry/registry.py::Registry.register` |
| AC-F1.2 | `tests/unit/test_registry.py::test_ac_f1_2_unknown_variant_names_the_alternatives` | `src/shared/registry/errors.py::UnknownVariant` |
| AC-F1.3 | `tests/unit/test_registry.py::test_ac_f1_3_factories_not_instances` | `src/shared/registry/registry.py::Registry.register` |
| AC-F1.4 | `tests/unit/test_registry.py::test_ac_f1_4_coverage_fails_at_boot_naming_every_missing_port` | `Registry.validate_coverage` |
| AC-F1.5 | `tests/unit/test_registry.py::test_ac_f1_5_closed_variant_set_attempts_no_import` | `Registry._entry` |
| AC-F1.6 | `tests/unit/test_registry.py::test_ac_f1_6_caching_is_scoped_to_the_registry_instance` | `Registry.resolve` |
| AC-F1.7 | `tests/contracts/harness.py::assert_no_state_leak`, run per variant by `PortContractSuite` — ⚠ **skipped, loudly, for any suite with `external_world_held_fixed = False`** (`A1`); ★ power proven by `test_port_contracts.py::test_ac_f1_7_the_suite_actually_catches_a_leaky_adapter` and `::test_ac_f1_7_the_fresh_instance_clause_is_load_bearing` | every registered variant |
| AC-F1.8 | `tests/unit/test_registry.py::test_ac_f1_8_provenance_is_entry_derived_not_object_reported` | `src/shared/registry/provenance.py::Provenance` |
| AC-F1.9 | `tests/contracts/conftest.py::pytest_generate_tests` + `test_port_contracts.py::test_ac_f1_9_every_port_with_variants_has_a_contract_suite` | `tests/contracts/harness.py` |
| AC-F1.10 | `tests/structural/test_ports_purity.py::test_ac_f1_10_port_modules_carry_no_implementation` | `src/shared/ports/*.py` (AST scan) |
| AC-F1.11 | `tests/unit/test_registry.py::test_ac_f1_11_experimental_flag_propagates` | `Registry.provenance` |
| AC-F1.12 | `tests/unit/test_registry.py::test_ac_f1_12_thin_ports_are_warned_not_failed` · `::test_ac_f1_12_a_fixture_variant_does_not_count_as_earned_abstraction` · `::test_ac_f1_12_an_experimental_variant_DOES_count` | `Registry.real_variants` → `CoverageReport.thin_ports` |
| AC-F1.13 | `tests/structural/test_ports_purity.py::test_ac_f1_13_default_required_ports_comes_from_all_not_a_second_list` · `::test_ac_f1_13_a_declared_port_with_no_variant_is_caught` (⏳ `::test_ac_f1_13_declaring_a_port_is_requiring_it` **skips** while `__all__` is empty) | `src/shared/ports/__init__.py` + `Registry.validate_coverage` |
| AC-F1.14 | `tests/unit/test_registry.py::test_ac_f1_14_resolve_from_another_thread_is_refused` | `Registry._assert_owner_thread` |
| AC-F1.15 | `tests/unit/test_registry.py::test_ac_f1_15_invalid_keys_are_refused` (6 cases) · `::test_ac_f1_15_names_the_offending_field` | `Registry._check_key` → `errors.InvalidKey` |

★ **Verified by mutation, 2026-09-03** (re-run after amendment `A1`; **16 mutations, all caught**). Every row above was checked by breaking the behaviour and
confirming the named test goes red — a suite written alongside its own implementation proves nothing
otherwise (constitution §5.1: *"the illegal move produces green tests"*). ⚠ Two mutations initially
**survived** against `AC-F1.7`, whose suite passed vacuously because every fixture adapter is stateless;
`WarmupGreeter` (leaks on the first call only) and `LeakyGreeter` were added until the check had power.

⚠ **`src/shared/ports/__all__` is empty**, so `AC-F1.4`/`AC-F1.12`/`AC-F1.13` are exercised against
explicit lists and fixtures rather than real ports. F1 §2 makes port *semantics* a non-goal — real
ports arrive with their own specs, and `AC-F1.13`'s skipped test turns itself on when the first one lands.
