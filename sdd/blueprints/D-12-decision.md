# Blueprint — D-12 Decision

> **Code:** `src/decision/` · **Spec:** `sdd/design/rel6_design/L1-decision.md` · **Seat:** SEAT-5 · **LEVEL 1**
> **Status:** written 2026-08-23 at **B3** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ★ **Nearly complete.** The algebra, composition, attribution and grade transport are all here.
> The counterfactual store (DN-19…DN-21) lives in D-11 and was built at B1; `ρ` (DN-27) and the
> deferral tracker (DN-29) need history that does not exist yet — §9.

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-23 | `meet()` with **no arguments raises** | Mathematically the empty meet is the identity (BUY). In this system it means *every gate went missing*, which is §5.5's exact defect — **the identity reached by omission** | Returning BUY — correct order theory and the precise shape of both real incidents in this repo |
| 2026-08-23 | `NO_THESIS` **composes as VETO** and keeps its own name | DN-10 honoured rather than bypassed: absence must MOVE the verdict. Keeping the name lets a reader tell *"the analyst said no"* from *"there was no analyst"* | Mapping it to PASS (identity by omission) or inventing a fourth verdict (breaks §5's chain) |
| 2026-08-23 | The upgrade check runs **even though the meet makes it impossible** | ★ **A check that can never fire is the only evidence the meet was actually used.** `DEC.VERDICT.UPGRADE` firing means someone bypassed `meet()` | Omitting it as dead code — then a future refactor to an `if`-chain would be silent |
| 2026-08-23 | `NOMINATED_VERDICT = BUY` is a **named module constant** | D-03 emits no verdict (QA-29); *"a rank-1 nomination means BUY"* is a translation, and it belongs in one visible place rather than implied at a call site | A literal at the call site — the translation would be invisible and un-greppable |
| 2026-08-23 | `alerts_status` is **on the Recommendation**, not inside `alerts[]` | It is a property of the **pass**, not of any alert. Putting it on an element would make an empty list unable to carry it — which is the whole defect DN-38 fixes | A sentinel alert saying "unchecked" — an alert that is not an alert, and RP-46 says alerts may never be filtered |

---

# 1. What this domain does, in one paragraph

D-12 takes D-03's nomination, D-01's gate and D-05's alerts and produces exactly one artifact-ready
`Recommendation` with a complete audit trail. ★ **It originates nothing**: every verdict it emits was
emitted by someone else first, and its only freedom is to make one *more conservative*. That is not
a safety rule bolted on — it is the algebraic structure of the composition itself.

# 2. The objects and how they flow

```text
   CT-3.4 Nomination ──┐
   CT-1.4 GateVerdict ─┤
   AlertSet (D-05) ────┤
                       ▼
              compose() ──► meet(BUY, phi(BUY, status), ...)
                       │              │
                       │              └──► attribute() ──► Attribution
                       ▼
              CT-12.1 Recommendation ──► D-09 renders · D-11 records
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| verdict chain | `src/decision/algebra/verdict.py::CONSERVATISM` | module constant | everything | forever |
| `GateOutcome` | `src/decision/contracts/recommendation.py::GateOutcome` | `src/decision/compose/service.py::compose` | attribution, D-09 | one run |
| `Recommendation` | `src/decision/contracts/recommendation.py::Recommendation` | `compose` | D-09, D-11 | one run |

★ **The object that surprised me: `grade`.** It is a `dict` deliberately — a **superset** of the
producer's keys (DN-32), so adding a field upstream must not require a schema change here. A typed
mirror would silently drop the new field, which is the exact defect DN-32 was written for.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | roster check | `src/decision/compose/service.py::compose` | ★ **DN-11 before anything.** Inferring the roster from responders makes a silently-absent gate structurally undetectable | `AbsentTreatedAsPassError` / `GateMissingError` |
| 1 | anchor check | same | DN-23/OR-35. A model trained on one anchor and deployed on another is a full session of drift, **invisible in backtest** | `AnchorMismatchError` |
| 2 | apply φ per gate | `src/decision/algebra/verdict.py::apply_gate` | statuses become verdicts before any meet — the two are different types | `ValueError` on an unmapped status |
| 3 | meet | `src/decision/algebra/verdict.py::meet` | ★ the one place composition happens (DN-5) | — |
| 4 | traceability + upgrade checks | `compose` | **after** the meet, because they are assertions *about* it | `VerdictOriginatedError`, `VerdictUpgradeError` |
| 5 | attribute | `src/decision/attribute/binding.py::attribute` | needs every outcome, since several gates can bind at once | `AttributionIncompleteError` |
| 6 | transport the grade | `src/decision/compose/service.py::_transport_grade` | last, so nothing recomputes it in flight (DN-26) | — |

⚠ **Step 0 before step 2 is the ordering that matters.** Checking the roster *after* composing means
the meet has already run over a short list and produced a plausible verdict.

# 4. ★ The mathematics

### The meet

| | |
|---|---|
| **Implemented in** | `src/decision/algebra/verdict.py::meet` |
| **Formula** | ```python\nreturn max(verdicts, key=conservatism)\n``` over `c(BUY)=0 < c(HOLD)=1 < c(SELL)=2` |
| **Units** | none — an ordinal on a 3-element chain |
| **Domain / range** | `V = {BUY, HOLD, SELL}`; ⚠ **the empty argument list raises** rather than returning the identity |
| **Why this form** | ★ **The decisive argument is statistical, not order-theoretic.** The meet is a **zero-parameter** rule: it estimates nothing, so nothing in it can be fitted to noise. At n≈60 decisions/year that is the out-of-sample optimum, not a safety compromise (Smith & Wallis 2009; Claeskens et al. 2016; DeMiguel et al. 2009 — *fitted weights do active harm, not merely no good*) |
| **Alternatives rejected** | A fitted linear blend of D-01 and D-03 — **§6.7 prices what that forgoes: up to 1.41× IR uplift if `ρ≈0`** — and rejects it because the uplift is *unverifiable at this breadth* while the literature says fitting it makes things worse. An imperative `max()` over a severity dict (today's `backups/pipeline/discipline/gate.py`) gives the same answer today and a weaker guarantee tomorrow |
| **Sensitivity** | None — it is a total order. **That is the point** |
| **★ Worked example** | `meet(BUY, HOLD) = HOLD`; `meet(SELL, BUY) = SELL`; `φ(SELL, VETO) = SELL ⊓ HOLD = SELL` — ★ **the veto is inert on a SELL**, so the discipline layer can stop you buying and cannot stop you selling |
| **Known-wrong** | ⚠ **§5.4a's precondition.** `c(BUY) < c(HOLD) < c(SELL)` orders correctly **only for a held name**. On an unheld name a SELL is a short — an escalation — and the chain inverts. Guaranteed unreachable here (all four accounts registered; CRA prohibits shorting), and guarded by `SellNotHeldError` anyway |

### The gate map φ

| | |
|---|---|
| **Implemented in** | `src/decision/algebra/verdict.py::apply_gate` |
| **Formula** | ```python\nif status == VETO:\n    return meet(verdict, HOLD)\nreturn verdict\n``` |
| **Why this form** | ★ **VETO maps to HOLD, never SELL** (DN-9). A veto is *"do not act on this"*, not *"take the opposite side"* — mapping a vetoed BUY to SELL would have the discipline layer **originating a trade instruction**, which DN-1 forbids outright |
| **Alternatives rejected** | Per-gate configurable severity (QN-2) — a gate wanting `⊓ SELL` is asking to originate an instruction. FLAG moving the verdict — DN-8 puts FLAG's obligation on the *artifact*, because a level that alters nothing trains the reader to skip it |
| **★ Worked example** | All nine `(v, s)` pairs are enumerated exhaustively in `test_ac_12_3_phi_is_monotone_in_both_arguments`. The one worth reading: `φ(SELL, VETO) = SELL` |
| **Known-wrong** | none known |

# 5. The logic decisions

| Decision | Where | Why this way | What it would take to change it |
|---|---|---|---|
| Gates are iterated **sorted by id** | `compose` | Determinism (INV-2). DN-6's commutativity means the *result* cannot depend on order — this makes the *record* not depend on it either | one sort key |
| Attribution reports **binding gates only** | `attribute` | DN-13. Reporting all gates would bury the binding ones; reporting one would hide the rest | — |
| A binding level with no claimant **raises** | `attribute` | The alternative is an attribution that silently omits what actually bound | — |
| `veto_rate([])` **raises** | `src/decision/compose/service.py::veto_rate` | ★ A rate of zero means the gate never fired; **no data means nobody looked**. Returning 0.0 conflates them (DE-35's shape) | — |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Who reads it | Changing it affects |
|---|---|---|---|---|
| the gate roster | ⚠ **passed in by the caller** | `("thesis",)` at B3 | `compose` | **QN-3 is open** — DN-11 needs a source of truth, and config is the obvious home, which makes it RunManifest-recorded (CN-5) |
| `NOMINATED_VERDICT` | `src/decision/compose/service.py` | `BUY` | `compose` | a world-model constant, not a tunable |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | **CT-3.4** Nomination | D-03 | `NominationContractError` at its own construction |
| in | **CT-1.4** GateVerdict | D-01 | invalid status ⇒ `ValueError`; missing ⇒ `AbsentTreatedAsPassError` |
| in | `AlertSet` + status | D-05 | `ValueError` if alerts came from an incomplete pass (RK-30) |
| out | **CT-12.1** Recommendation | D-09, D-11 | — |
| out | **CT-12.2** VetoedCandidate | ⚠ **D-11 owns it** and built it at B1; D-12 does not write it yet (§9) |

# 8. Failure behaviour

| Failure | Detected where | Behaviour |
|---|---|---|
| a declared gate did not report | `compose` | `AbsentTreatedAsPassError` — ★ never composed as PASS |
| `meet()` with no verdicts | `meet` | raises |
| anchor ≠ manifest | `compose` | `AnchorMismatchError` |
| composed verdict in no input | `compose` | `VerdictOriginatedError` |
| composed verdict more aggressive | `compose` | `VerdictUpgradeError` — *firing means the meet was bypassed* |
| SELL on an unheld name | `compose` | `SellNotHeldError` |
| more than one actionable | `src/decision/compose/service.py::enforce_inv6` | `MultipleActionableError` |

# 9. What this domain deliberately does NOT do

| Not here | Owner / when |
|---|---|
| produce a ranking, author a thesis, compute risk, size a position | D-03 / D-01 / D-05 / D-06 |
| **derive** a gate status | ★ **D-01** (DN-31). Deriving one would be originating a verdict and would need analytical policy D-12 has no standing to hold |
| render or deliver | D-09 |
| ★ **write the counterfactual record** | D-11 owns CT-12.2 and built it at B1; the D-12 → D-11 write lands when D-12 produces real vetoes (B4) |
| report `ρ` (DN-27) | needs D-01 coverage spanning the rank distribution — ⚠ **DN-28: at n=1 every covered name has rank 1 and `ρ` is not estimable at all** |
| track deferrals (DN-29) | needs run history |
| feed anything back to D-01 or D-03 | ✗ **never** (DN-3) — grep-checked as ST-10 |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — the roster is a caller argument, not config** | ⚠ medium | DN-11 is satisfied *procedurally*: the caller declares it. A caller that declares only what it has is back to inferring | **QN-3** |
| **10.2 — `deferral` is always `None`** | low | DN-29's liveness monitor needs run history. ⚠ *Safety is handled by the lattice; **liveness never will be*** | DN-29 |
| **10.3 — no vetoed candidate is written** | ⚠ expected | The B3 gate never vetoes. When it can (B4.4), the D-12 → D-11 write must land **with it**, or §6's whole measurement programme starts late | DN-19, L3 BS-1 |
| **10.5 — no account can produce a COMPLETE risk pass today** | ⚠ **expected, and it is why the live card is informational** | DN-39 needs a complete pass; a complete pass needs book-wide exposure; that needs every held name priced. All four accounts hold at least one CAD-venue or CDR position and those symbols are **402 on the current FMP plan** (measured 2026-08-26). ★ The code path is finished and pinned by `tests_src/test_b3_actionable_e2e.py` — **only the data is missing** | **RC-58**, DE-49 |
| **10.4 — `_transport_grade` matches `gate_id == "thesis"`** | ⚠ medium | A second graded gate would not have its grade transported. **Silent, and exactly DN-32's defect shape** — a field dropped in transport looks like one never emitted | new — no ID |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_decision_b3.py` — 24 cases; the algebra is **exhaustive over `V³`** |
| 1b | ★ **DN-39, both halves** | `tests_src/test_decision_actionable.py` (5 cases) and `tests_src/test_b3_actionable_e2e.py` (4) — the second builds a **fully priced, reconciled book**, gets a `COMPLETE` pass out of D-05's real WF-R1 ladder, and shows the card go actionable. That is the proof the wiring is complete and the blocker is data |
| 2 | ★ **Break it and confirm red** | In `src/decision/algebra/verdict.py::apply_gate`, change `meet(verdict, HOLD)` to `SELL`. `test_ac_12_5_a_veto_on_a_sell_is_inert` must fail — **that line is DN-9, and getting it wrong makes the discipline layer originate a trade instruction** |
| 3 | The worked example (§4) reproduces | `python -c "from src.decision import *; print(meet('BUY','HOLD'), apply_gate('SELL','VETO'))"` → `HOLD SELL` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **No, and it never can be directly.** §6.3: the gate's P&L effect needs **3.5–11× more data than three years supplies**. What *is* checkable is the algebra, and it is checked exhaustively — which is the whole argument for choosing an algebraic structure here |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-decision.md` | DN-1…DN-39, CT-12.1/12.2, §5 the algebra, §6 the measurement |
| `sdd/design/rel6_design/L1-fundamental-analysis.md` | **CT-1.4** and §11.1 — why D-01 owns the status mapping |
| `sdd/design/rel6_design/L1-risk-management.md` | RK-29/RK-30/RK-36 — why `alerts_status` exists; **RK-30 is DN-39's whole argument** |
| `sdd/design/rel6_design/L1-recording.md` | **RC-58** — the CAD/CDR postponement that keeps every book unpriceable |
| `sdd/design/rel6_design/L2-signal-combination.md` | the architecture D-12 implements; QB-1/QB-2/QB-5 |
| `sdd/specs/constitution.md` | **P3** as amended, P2, P5, INV-2, INV-6 |
