# Blueprint — D-06 Portfolio Strategy *(B5)*

> **Governing spec:** [`../design/rel6_design/L1-portfolio-strategy.md`](../design/rel6_design/L1-portfolio-strategy.md)
> **Seat:** SEAT-4, forward-looking half · **Path:** `src/portfolio/`

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-25 *(B5)* | ★★ **`target_positions` is required per-account configuration with no default** | **PS-43**, closing **QS-7**. **PS-27 divides the risk budget by `n_reserve = target_positions − current_positions`** and the number was declared nowhere — *a number that DIVIDES the risk budget cannot have an invented default* — while PS-27's own *"never derived from free cash"* rules out the tempting inference (*deriving it from cash is circular*). ⚠ **`n_reserve ≤ 0` yields `unavailable`, not a floor**: there is no open slot, and a budget computed anyway sizes a position the policy says does not exist | *Defaulting to the book's observed 6–11 names* — it invents a policy and then divides real money by it |
| 2026-08-25 *(B5)* | ★ **A MethodEntry lives in its own domain's `methods/entries/`** | **PS-44.** **AC-6.9k** requires every applied risk-budget factor to resolve to a MethodEntry and the register is **D-03's** — so satisfying it would file SEAT-4's work in SEAT-3's tree, or create a `src/portfolio → src/quant` import edge **the graph cannot distinguish from consuming a nomination** (FE-21's shape, one seat over). ★ The register's check is a **filesystem scan, not an import**, so widening it satisfies QA-20 verbatim and creates no dependency | *Importing `src.quant.methods`* — one import, and the seat boundary is no longer checkable |
| 2026-08-25 *(B5)* | ★ **Every factor is bounded in `(0, 1]` at construction** | This is what makes **INV-022 structural**: the product can never exceed `r_ceiling`, so *"the system's own recommendation may never exceed MAX_POSITION_PCT"* holds **by construction rather than by a clamp bolted on afterwards** | *Clamping the product at the end* — the same number, and it stops being a property of the design |
| 2026-08-25 *(B5)* | ★ **`unapplied` and `unmeasured` are different statuses** | *We measured and it did not differentiate* (PS-35, `E` inside its MDE) and *we could not measure* (PS-34, `C` until RM-1) are different findings. ⚠ Collapsing them would hide the one PS-35 exists to surface: **the framework reporting that it cannot differentiate** | *One `unavailable` status* — it makes an honest null result look like missing plumbing |
| 2026-08-25 *(B5)* | **The human's size is never capped, and the contract refuses to mark it capped** | PS-10 with INV-026: *INV-022 caps only what the SYSTEM proposes.* Capping the human's own size would be D-06 overruling the seat that holds the P&L | *A single `capped` flag for both paths* — one boolean, two meanings, and the wrong one is a mandate violation |

# 1. What this domain does, in one paragraph

D-06 answers **"if I did this, what would it cost me and what would it do to the book?"** It sizes a
candidate against a stop, decomposes the risk budget into named factors, reports which constraint
binds, computes the book after a hypothetical, and raises M-3's scale-in check **together with its
forgotten half — the hold alternative.** ★ **It computes consequences; it does not propose.**

# 2. The objects and how they flow

```text
   D-11 capital_base ─┐
   D-05 P · D  ───────┼──► risk_budget()  r_ceiling × E × C × P × D
   D-03 edge · MDE ───┘         │  each factor ∈ (0,1] — INV-022 structural
                                ▼
   entry · stop ──► implied_k ──► size_for_stop ──► CT-6.1 SizingAnswer
                                       │              arithmetic · assumptions
                                       │              consequences · thresholds
                                       ▼              binding constraint
                              INV-022 cap (system only, labelled)

   implied_risk()   ← the human's share count in, the implied budget out (PS-9)
   scenario()       ← the book after a hypothetical; is_proposal is a constant
   hold_alternative() ← what holding preserves, beside what trimming realises
```

# 3. The sequence — what actually executes

`size_for_stop` runs: stop present (PS-5) → FX available (PS-4) → `n_reserve` (PS-27/PS-43) →
account risk state (PS-30) → per-trade budget = `remaining / n_reserve` → stop distance and implied
`k` (PS-6/PS-7) → shares → **INV-022 cap, labelled** (PS-10) → binding constraint (PS-28) →
consequences and threshold crossings (§5.4).

# 4. ★ The mathematics

```
   risk_capital  = risk_remaining / n_reserve          (PS-27)
   d             = entry − stop                        (PS-7 reports implied k)
   shares        = risk_capital / d
   notional      = shares × entry
   committed     = Σ max(0, entry − stop) × shares     (PS-29)
```

★ **`max(0, …)` is the whole of PS-29**: a position whose stop has trailed above entry **releases
its budget without being sold.** ⚠ The mark-to-market alternative *would keep a winner charged
forever and quietly penalise holding* — the exact behaviour M-3 asks us to encourage.

⚠ **§5.1a, restated because it is the most confused idea in position sizing.** The risk budget is
what you can **lose**, not what you deploy; the two are related by `entry / d` and nothing else. At
a constant 2 % risk, a −2.2 % stop is a **90 %-of-account position** and a −13.3 % stop is 15 %.

# 5. The logic decisions

| Decision | Rule |
|---|---|
| `E` applies only outside its MDE | PS-35 — ★ *manufacturing differentiation from noise* is the failure at IC ≈ 0.03 |
| Factor validation lives in `Factor.__post_init__` | An unapplied factor with a value ≠ 1.0 is *an estimate wearing a disclaimer* |
| `ThresholdCrossing` raises on any `effect` but `reported_only` | INV-026 — the contract states that no other value exists |
| `Scenario.is_proposal` and `ParityComparison.is_target` refuse `True` | PS-12/PS-32 — ★ *reporting the number is a disclosure; optimising toward it is the target allocation PS-12 forbids* |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Changing it affects |
|---|---|---|---|
| `MAX_POSITION_PCT` | `src/portfolio/contracts/sizing.py` | `15.0` | INV-022's cap on **system-proposed** size only |
| `DEFAULT_K` | `src/portfolio/sizing/stop_distance.py` | `1.5` | Stop width, hence position size. ★ PS-6 requires it **stated on every answer**, and it is |
| `DEFAULT_HORIZON_DAYS` | same | `21` | HorizonSet v1's holding horizon |
| `r_ceiling` | ⚠ **caller argument** | — | The maximum, not the target. Should be config once D-08 supplies a manifest |
| `target_positions` | ⚠ **required caller argument, no default** | — | ★ **PS-43** — it divides the risk budget, so it is stated per account and reported on the answer |
| `CONCENTRATION_THRESHOLD_PCT` · `SECTOR_MAX_PCT` · `THEME_REPORT_THRESHOLD_PCT` | `src/portfolio/sizing/risk_based.py` | 25 · 35 · 40 | ⚠ **Duplicated from D-05's aggregate.** Two copies of L0 §8 — see §10.3 |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | `capital_base` | D-11 (RC-19) | point-in-time; never configured |
| in | `P`, `D` | D-05 | either may be `unmeasured` ⇒ the factor is 1.0 and says so |
| in | the human's share count | SEAT-1 | ★ never substituted (PS-9), never capped (PS-10) |
| out | `CT-6.1 SizingAnswer` | D-09, SEAT-1 | a consequence of stated assumptions |
| out | `CT-6.2 Scenario` · `CT-6.3 HoldAlternative` | D-09 | `is_proposal` / `tax_event` are constants |

# 8. Failure behaviour

No stop ⇒ `NoStopError` (**undefined, not conservative**). No FX rate ⇒ `UnavailableInputError`. No
`target_positions`, or a full account ⇒ `ReserveUnavailableError`. A target-allocation request ⇒
`TargetAllocationError`. ★ **Nothing here degrades to a default**, because every default would be a
number about a book nobody holds.

# 9. What this domain deliberately does NOT do

| Not done | Why |
|---|---|
| Propose a size | PS-8 — ⚠ **§5.3's collision**: `shares ∝ 1/σ` pushes the book away from M-2's deliberate concentration, so applied as a *recommendation* it would implement the diversification pressure M-2 rejects, **one trade at a time, with arithmetic as the alibi** |
| Rank or sort by distance from risk parity | PS-32 |
| Compute a target allocation or drift | PS-12, L0 §4.3 |
| Reason about tax lots | ★ PS-21 — **all four accounts are registered, so the "tax cost of trimming" term is identically zero. That is a finding, not an omission**, and it strengthens M-3's *trim rather than exit* |
| Write anything | PS-26 — it computes on demand and returns; the book is D-11's |

# 10. ⚠ Known-wrong, approximations, and open defects

| # | What | Severity | Detail | ID |
|---|---|---|---|---|
| 10.1 | **`C_confidence` is always `unmeasured`** | ⚠ **expected** | ★ *`C_i` is where D-01's k-run stability stops being a hope and becomes arithmetic* (§5.1d) — and **nothing wires RM-1 to sizing**. The budget is visibly incomplete, which is PS-34 working | PS-34 |
| 10.2 | **`E_edge` needs an MDE D-03 does not publish** | ⚠ expected | The formula is in `L1-quantitative-analysis` §… but **no contract carries it**, so `edge_factor(None, None)` is the real path today | PS-35 |
| 10.3 | **L0 §8's thresholds are declared twice** | ⚠ **medium** | `src/risk/exposure/aggregate.py` and `src/portfolio/sizing/risk_based.py` each define 25/35/40. ★ **FE-4's defect shape** — two copies of one config, and nothing fails if they diverge. They belong in `src/shared/`, which is a B6 change | RK-2, INV-026 |
| 10.4 | **`src.portfolio.scenario` resolves to the FUNCTION, not the subpackage** | low | §4's tree names `scenario/` and §11's API names `scenario()`, so **the collision is the spec's.** `import src.portfolio.scenario.whatif` fails after `src.portfolio` is imported; `importlib.import_module` is exact and the test uses it | §4, §11 |
| 10.5 | **The multiplicative form assumes independent factors** | ⚠ stated, not fixed | A deep drawdown and low confidence **co-occur**, so the product is *more* conservative than either alone. Recorded in the MethodEntry's assumptions rather than corrected — the safe direction | PS-33 |
| 10.6 | **No `Money` type is used** | ⚠ medium | CT-6.1 shows `{"minor": …, "currency": …}` and **PS-4 requires every output to be a `Money` with explicit currency (INV-001)**. This slice computes in floats with a `currency` string beside them. ★ The FX *guard* is real (PS-4's second half); the representation is not | PS-4, INV-001 |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_portfolio_b5.py` — 32 cases, each docstring naming its `AC-6.n` |
| 2 | ★ **Break it and confirm red** | **(a)** In `src/portfolio/contracts/sizing.py`, drop the `0 < value <= 1` check in `Factor`. `test_ac_6_9i_the_product_never_exceeds_r_ceiling` must fail — ★ **INV-022 stops being structural and becomes a clamp somebody has to remember.** **(b)** In `src/portfolio/sizing/risk_based.py::committed_risk`, drop the `max(0, …)`. `test_ac_6_9a_a_stop_above_entry_releases_the_whole_allocation` must fail — **a winner stays charged forever, and holding is quietly penalised.** **(c)** In `n_reserve`, return `1` instead of raising when `target_positions is None`. `test_ac_6_9l_...` must fail — ★ **a number that divides the risk budget acquires an invented default** |
| 3 | The worked example (§4) reproduces | The `stop_distance_vol_v1` known-answer test: entry 100, σ 0.02, h 21, k 1.5 ⇒ d = 13.7477, 145.4786 shares at a 2,000 risk capital |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **No.** The arithmetic reproduces §5.1a's published table to the dollar, which checks it against **the spec**, not against a broker. **No order has ever been sized from a real book**, and 10.6 means the money representation would have to change first |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-portfolio-strategy.md` | §5.1a the risk-budget confusion, §5.1b/§5.1d, **§5.3 the collision**, §7 M-3; **PS-43/PS-44** |
| `sdd/design/rel6_design/L1-risk-management.md` | **§8** — the `P` and `D` factors this domain multiplies |
| `sdd/design/rel6_design/L1-quantitative-analysis.md` | **QA-20** — the MethodEntry standard, whose storage PS-44 distributes |
| `sdd/design/rel6_design/L3-build-sequence.md` | **BS-15** — D-05 then D-06 |
