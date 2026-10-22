# F10 — Valuation trail (D-02 `valuation`, `fv_model`, the sensitivity band, implied expectations)

> **Spec-ID:** F10 · **Status:** 🟢 **approved 2026-09-13** (Victor Truong) · **Drafted:** 2026-09-13
> ✅ **Approved with `Q1`, `Q3`, `Q5` answered as suggested → `D4`, `D5`, `D6`; `Q4` adopted with the
> contract → `D7`.** ✅ `Q2` answered 2026-09-14 (Victor): marketable securities
> and finance leases count in net debt → `D8`; operating leases stay OUT (`DX-106`, Victor, same day). `DX-103`, `DX-104` decided
> the same day (`D6` amended).
> ✏ **Amended 2026-10-01 (Victor): `D10`** — implied growth by duration (5 / 7 / 10 / 15 years) and market
> capitalisation, published as `dcf_two_stage@v2`; `AC-F10.22`. `v1` is unchanged.
> ✏ **Amended 2026-10-02 (Victor): `D11`** — each duration row also states the FCFF the price requires in its
> final explicit year and that figure as a share of trailing revenue (*at flat revenue*); `AC-F10.23`.
> ✏ **Amended 2026-10-21 (Victor, "go DX-176"): `D12`** — after a 10-K, the balance items of the latest quarter are
> read from the annual row of the SAME period end and the SAME filing; `AC-F10.24`.
> **Source discussion:** `sdd/design/rel1_brainstorm.md` Decisions log 2026-09-13 · `sdd/questions.md`
> `QR-25` · `L3` §2.1e *What remains* · design tier `sdd/design/rel6_design/L1-feature-engineering.md`
> §1.3, §6.2, §8.1, §10 · `L0-system-vision.md` §4.2 D-01 valuation split, **VS-1…VS-5**
> **Home:** D-02 `src/feature_engineer/valuation/` · seat 8 (Back Office, neutral ground) · capability
> vision §4 — serves `C3` (every number carries its trail) and the `CT-9.2` thesis path.
> **Governs:** `constitution.md` — `P5` fail loud · `AP-5` deterministic where a computation applies ·
> `INV-1` no look-ahead · `INV-2` determinism · `INV-014`/`ST-9` the analyst firewall · `ST-5` no LLM
> outside the gateway · `MO-1` money is never a bare number · `PG-10`. Design-tier rules it enforces:
> `FE-7` `FE-9` `FE-14` `FE-16` `FE-21` `FE-23` `FE-24` `FE-25`, `VS-1`…`VS-4`.

---

## 1. Goal & why

**Compute a company's fair value deterministically, with every assumption, input and intermediate on
the record — and say what the current price requires to be true.**

★ **Why now, measured 2026-09-13.** Stage B's first block, `J-09` (expectations reconciliation), is
written against evidence that does not exist: *"D-02 supplies [what the current price requires]"*,
*"D-02's fair-value trail"*, *"the sensitivity band"*. `J-10` and `J-11` consume `J-09`, and `J-16` (the
verdict) consumes all of them — so **no `CT-9.2` thesis can be produced until this spec's outputs
exist.** The design has specified `valuation(ticker, as_of)` since 2026-08-16 (`L1-feature-engineering`
§6.2); `src/` has no fair value, no reverse valuation and no band anywhere.

★★ **Why a trail and not a number** (`L1-feature-engineering` §6.2, `AP-2`): *"A thesis that says ROIC
of 24% comfortably exceeds cost of capital must be able to name the NOPAT and the invested capital it
came from. A bare float cannot support a citation."* The same holds for a fair value — and for the
failure this spec must not repeat: the inherited DCF (`D-19`, §8.1) returned **an enterprise value per
share with no net-debt subtraction**, measured at **455 % of market cap on CHTR**. A trail is what
would have made that visible.

## 2. Scope / non-goals

**In scope**
- **The mechanics** — a pure two-stage discounted-cash-flow function over a declared cash-flow basis,
  returning enterprise value, equity value and value per share **with every intermediate** (`CT-F10.2`).
- **`fv_model`** — `valuation(ticker, as_of, …)`: the mechanics applied to a **judgement-free** basis
  built from D-07 data (reported trailing cash flow), per `VS-2` consumable by both analyst seats.
- **The sensitivity band** — the value over a declared grid of discount rate × terminal growth.
- **Implied expectations** — the reverse valuation: the growth rate the current price requires.
  ✏ `D10`: also **by duration** — the same solve repeated at each declared explicit period.
- **Market capitalisation** — the raw price × diluted shares, on the trail (`D10`).
- **A declared, versioned assumption set** (`CT-F10.1`) — no assumption is a literal in code.
- **The basis contract** (`CT-F10.3`) through which a **judgement block's normalised earnings feed the
  same mechanics** — producing a result that is **`fv_analyst`, never `fv_model`** (§7 `D1`).
- **Rendering** a valuation into the evidence bundle as a `computed` part (`CT-F10.4`).

**Non-goals (this spec)**
- ✗ **Normalising earnings.** Which earnings to capitalise is a JUDGEMENT (`VS` table, `D1`). The block
  that makes it is a D-01 prompt, specified separately (§8 `Q3`). F10 defines only the input it
  supplies.
- ✗ **`fv_analyst` itself** — the reconciled fair-value OPINION is D-01's (`VS-1`, `VS-4`). F10 guarantees
  the arithmetic it uses is the same arithmetic, and that the two can never share a name.
- ✗ **Multiples-based valuation, peer context, `quality()`, `moat()`** — separate `§6.2` outputs; later
  specs.
- ✗ **Entering the D-03/D-04 panel.** No valuation output becomes a `FeatureSpec` (`QF-1` stays closed:
  the valuation is not historically reconstructable point-in-time).
- ✗ **Porting the inherited DCF.** It was never absorbed (§7 `D3`); `FE-18`'s *"moves VERBATIM"* is moot.
- ✗ **Choosing the assumption VALUES** — policy, `§8` `Q1`. F10 makes them declared and versioned.
- ✗ **Adding canonical line items** (marketable investments, leases, tax) — D-07's definitional work
  (`§8` `Q2`); F10 states what it needs and refuses when it is absent.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | A Stage-B bundle is assembled for a ticker | `ticker`, `as_of`, assumption set | `src/feature_engineer/valuation/service.py::valuation` |
| T2 | A normalised-earnings judgement has been committed (Stage A, blind) | `CT-F10.3` basis + the same inputs | `src/feature_engineer/valuation/service.py::value_on_basis` |
| T3 | Any caller needs the pure arithmetic | a fully-specified `CashFlowBasis` + assumptions | `src/feature_engineer/valuation/dcf.py::discount` |
| T4 | The bundle builder renders the result | a `ValuationResult` | `src/feature_engineer/valuation/render.py::as_bundle_part` |

## 4. Behaviour & reuse (the lean "how")

- **One coherent design, chosen once (`D2`).** Free cash flow **to the firm** discounted at a **firm**
  rate gives enterprise value; **equity value = enterprise value − net debt**; per share = equity value ÷
  diluted shares. ⚠ `D-19` mixed the halves of two coherent designs; F10 implements exactly one and a
  property test asserts the net-debt step (`AC-F10.2`).
- **Two stages.** Years `1…N` grow at `g₁`; the terminal value is Gordon growth at `g_T` on year `N+1`.
  `wacc ≤ g_T` refuses — the formula has no finite answer there, and a clamp would be a fabricated one.
- **Inputs come only through D-07's public API** (`FE-23`): `get_fundamentals` / `get_facts` for line
  items, `get_prices` for the price. ★ **Trailing figures are four DISCRETE EDGAR quarters**, classified
  by span, never by label — the `fmp-api` skill's trap 1 (*FMP guessed MU's quarter wrong by 71 %*); an
  FMP-sourced TTM is refused where EDGAR has the quarters. **Per-share comparisons read the RAW price
  series** (`FE-9`; trap 2 — the field names on the adjusted endpoint are inverted).
- **The trail is the result, not a log of it.** Every assumption (with its set name, version and content
  hash), every input (with `source`, `accession_id`, `period_start`/`period_end`, `filing_date`), and every
  intermediate (each year's flow, discount factor, present value, terminal value, EV, net debt, equity)
  is a field of `CT-F10.2`. ★ **Recomputing from the trail alone reproduces the value exactly**
  (`AC-F10.4`) — which is the test that the trail is complete.
- **Money everywhere** (`FE-24`, `MO-1`): monetary fields are `Money` in integer minor units with a
  currency; a ratio of same-currency money is dimensionless (`FE-32`); **cross-currency arithmetic
  refuses**.
- **Missing is not zero** (`FE-14`, `P5`). An absent input yields `ValuationUnavailable` naming exactly
  what was missing — never a value computed around the gap, never a default.
- **The band and the reverse valuation reuse the mechanics.** The band evaluates `discount` over the
  declared grid; implied expectations solves `value_per_share(g₁) = price` by bisection over a declared
  bracket, deterministic in iteration count, and **refuses when no root exists in the bracket** rather
  than returning the nearest end.
- **The analyst basis (`D1`, `VS-4`).** `value_on_basis` runs the SAME `discount` on a basis a judgement
  supplied, and returns an `AnalystValuation` whose `kind` is `fv_analyst` and which carries the basis's
  provenance (block, prompt version, run id, commit hash). ★ **It is a different type from
  `ValuationResult`**: nothing that accepts `fv_model` accepts it, `valuation()` can never return it, and
  no D-02 artifact stores it (`VS-1`, `VS-3`, `FE-21`).
- **Rendering respects staging.** A valuation renders as a `computed` bundle part — the kind the blind
  view already withholds (`BLIND_WITHHELD_KINDS`, `RA-14`) — so Stage A never sees a price, a value or a
  band, and a normalised-earnings judgement made in Stage A cannot back-solve to the price.
- **Isolation.** `src/feature_engineer/valuation/` imports nothing from `src/fundamental/`, no LLM
  gateway, no vendor SDK (`ST-5`, `FE-21`, `A2`). FMP's own DCF may be fetched by D-07 as a **cross-check
  field** and is never `fv_model` (`fmp-api`: *"a cross-check, never a published fair value"*).

## 5. Contracts (inline)

**CT-F10.1 — `ValuationAssumptions`** (versioned, declared in config; immutable once published):
```json
{ "name": "str — e.g. 'dcf_two_stage'",
  "version": "int — changing ANY value below produces a new version (FE-2's rule, applied here)",
  "content_hash": "sha256 over the fields below — the identity a trail cites",
  "discount_rate": {"method": "declared_constant | capm", "value": "decimal | null",
                    "risk_free": "decimal | null", "equity_risk_premium": "decimal | null",
                    "note": "why — Q1"},
  "explicit_years": "int ≥ 1",
  "stage1_growth": "decimal — the fv_model basis growth; implied expectations solves for it",
  "terminal_growth": "decimal — must be < discount rate",
  "band": {"discount_rate_steps": ["decimal"], "terminal_growth_steps": ["decimal"]},
  "implied_bracket": {"low": "decimal", "high": "decimal", "iterations": "int"},
  "duration_table": {"explicit_years": ["int ≥ 1"]} }
```
Rules: every field required; no field has a code default; `terminal_growth < discount_rate` for every
grid point, checked at load. ✏ **`duration_table` (`D10`) is the one field a set may omit** — `v1`
predates it and is immutable, so its absence means *"this set declares no duration table"*, never a
default table; when present it is hashed like every other field, and its periods must be distinct.

**CT-F10.2 — `ValuationResult`** (`kind = "fv_model"`; returned, rendered, never stored in a panel):
```json
{ "kind": "fv_model", "ticker": "str", "as_of": "date",
  "assumptions": {"name": "str", "version": "int", "content_hash": "str"},
  "basis": {"label": "reported_ttm_fcff",
            "formula_id": "fcff.ocf_plus_after_tax_interest_minus_capex_minus_sbc.v2 (D6)",
            "tax_rate": {"value": "decimal", "income_tax": "Money", "pretax_income": "Money"},
            "inputs": [{"item": "str", "value": "Money|int", "source": "edgar|fmp",
                        "accession_id": "str|null", "period_start": "date", "period_end": "date",
                        "filing_date": "date"}]},
  "flows": [{"year": "int", "fcff": "Money", "discount_factor": "decimal", "present_value": "Money"}],
  "terminal": {"fcff_n_plus_1": "Money", "value": "Money", "present_value": "Money"},
  "enterprise_value": "Money",
  "net_debt": {"value": "Money", "components": ["…input refs, each with its tag"],
               "known_omissions": ["subset of: marketable_securities, finance_leases"],
               "excluded_by_design": {"operating_leases": "str — why (D8)"}},
  "equity_value": "Money", "diluted_shares": "int", "value_per_share": "Money",
  "known_limits": ["str — a figure this valuation CANNOT compute, and why (D9)"],
  "price": {"value": "Money", "date": "date", "series": "raw"},
  "band": {"grid": [{"discount_rate": "decimal", "terminal_growth": "decimal",
                     "value_per_share": "Money"}], "low": "Money", "high": "Money"},
  "implied": {"solves_for": "stage1_growth", "value": "decimal | null",
              "status": "SOLVED | NO_ROOT_IN_BRACKET", "residual": "Money | null"},
  "market_capitalisation": "Money — price.value × diluted_shares (D10)",
  "implied_by_duration": [{"explicit_years": "int", "solves_for": "stage1_growth",
                           "value": "decimal | null", "status": "SOLVED | NO_ROOT_IN_BRACKET",
                           "residual": "Money | null",
                           "required_final_year_fcff": "Money | null — D11",
                           "share_of_trailing_revenue": "decimal | null — D11, at FLAT revenue"}],
  "trailing_revenue": {"value": "Money", "item": "revenue", "periods": "the four D6 quarters"} }
```
✏ `implied_by_duration` is present exactly when the assumption set declares a `duration_table`, one row
per declared period in the declared order (`D10`). ✏ `D11`: `required_final_year_fcff` is the year-`N`
flow of the SAME `discount` trail at the solved growth (one rounding, `MO-5`), and
`share_of_trailing_revenue` is it ÷ `trailing_revenue`, both null exactly when the row is
`NO_ROOT_IN_BRACKET`; `trailing_revenue` is present exactly when the table is.
Rules: every monetary field one currency; `value_per_share ∈ [band.low, band.high]`; `implied.value` is
null exactly when `status = NO_ROOT_IN_BRACKET`. ★ **Net debt (`D8`)** = debt + finance leases not already
inside a debt tag − cash − marketable securities (current and non-current). ★ **Rounding (`MO-5`):** each present value is rounded
to minor units ONCE, and `enterprise_value` is the exact sum of the rounded fields — so the trail adds
up to the cent. ⚠ `net_debt.known_omissions` names every net-debt item NOT counted in this result (`PG-10`): one the
filer does not report. Never a fixed list. `net_debt.excluded_by_design` names what is left out ON PURPOSE —
operating leases, which `D6`'s operating cash flow already pays (`D8`) — so a reader never mistakes a choice
for a gap, or a gap for a choice.

**CT-F10.3 — `CashFlowBasis`** (the one input shape the mechanics accept):
```json
{ "label": "str", "base_fcff": "Money", "origin": "reported | judgement",
  "provenance": "for 'reported': the CT-F10.2 inputs · for 'judgement': {block, prompt_version, run_id,
                 stage_commit_hash, bundle_hash, method, window: {start, end}, exclusions: [{item,
                 evidence_id, quote}], computed_by}" }
```
Rules: `origin = judgement` ⇒ provenance complete, and the result is an `AnalystValuation`
(`kind = "fv_analyst"`) — **never** a `ValuationResult`. ★ **`D5`: the judgement supplies `method`,
`window` and `exclusions`; it never supplies `base_fcff`.** `base_fcff` is computed from that choice by
D-02 functions (`AC-F10.19`, `RA-45`), named in `computed_by` — so no figure in a basis was produced
inside a prompt (`S-2` item 3, `MP-6`), and no series arithmetic lives in D-01.

**CT-F10.4 — bundle rendering:** `BundlePart(kind="computed", pins={"contract_name": "valuation.<name>",
"contract_version": <assumptions.version>}, content=<CT-F10.2 as text, every figure labelled>)`.
Withheld from every `blind` view by the existing `BLIND_WITHHELD_KINDS`.

**CT-F10.5 — `ValuationUnavailable`** (`P5`): `{ticker, as_of, missing: [item], reason}` — raised, never
returned as a value.

## 6. Acceptance criteria (Given / When / Then → test tier)

> ⚠ IDs are **`AC-F10.k`** (constitution §1.1 — a bare `AC-10.k` would sit beside upstream families).

- **AC-F10.1** *(the mechanics, known answer)* — **Given** a basis, discount rate, explicit years and
  both growth rates whose result is worked by hand, **when** `discount` runs, **then** every flow,
  discount factor, present value, terminal value and the enterprise value equal the hand-worked figures.
  → *unit.* (`AP-5`)
- **AC-F10.2** *(★ `D-19` cannot recur)* — **Given** any basis and a company with non-zero net debt,
  **when** value per share is computed, **then** it equals `(enterprise_value − net_debt) ÷
  diluted_shares`, and differs from `enterprise_value ÷ diluted_shares` by `net_debt ÷ diluted_shares`
  to within one minor unit (the single rounding of a per-share division, `MO-5`). → *invariant /
  property.* (`L1-FE` §8.1) ✏ *amended at approval: "exactly" cannot hold across integer minor units.*
- **AC-F10.3** *(no finite answer refuses)* — **Given** `discount_rate ≤ terminal_growth`, or diluted
  shares ≤ 0, **when** valuing, **then** it raises; no clamp, no substitute. → *unit.* (`P5`)
- **AC-F10.4** *(the trail is complete)* — **Given** any `ValuationResult`, **when** the value is
  recomputed from the trail's fields alone, **then** it reproduces `value_per_share`, the band and the
  implied figure exactly. → *invariant / property.* (`AP-2`, §6.2)
- **AC-F10.5** *(money)* — **Given** a valuation, **when** its fields are read, **then** every monetary
  field is `Money` with a currency; **and given** inputs in two currencies, **then** it raises. → *data
  contract.* (`MO-1`, `FE-24`, `FE-32`)
- **AC-F10.6** *(point in time)* — **Given** `valuation` is called, **when** `as_of` is omitted, **then**
  it raises; **and** no input carries a `filing_date` or price date after `as_of`; **and** the price is the
  raw series. → *invariant / property.* (`INV-1`, `FE-7`, `FE-9`)
- **AC-F10.7** *(★ trailing = four discrete quarters)* — **Given** filings that carry cumulative
  year-to-date values, **when** the trailing basis is built, **then** it is the sum of four spans each
  80–100 days long, a cumulative value never enters as a quarter, and an FMP-sourced trailing figure is
  refused where EDGAR quarters exist. → *integration* (on a recorded fixture). (`fmp-api` trap 1)
- **AC-F10.8** *(missing is not zero)* — **Given** any required input absent, **when** valuing, **then**
  `ValuationUnavailable` names exactly the missing items and no value is produced. → *unit.* (`FE-14`,
  `P5`)
- **AC-F10.9** *(the band)* — **Given** declared grid steps, **when** the band is computed, **then** it
  holds one value per grid point, the point estimate lies within `[low, high]`, and value is
  non-increasing in the discount rate at fixed terminal growth. → *invariant / property.*
- **AC-F10.10** *(implied expectations round-trip)* — **Given** a price inside the bracket's value
  range, **when** implied growth is solved, **then** valuing at that growth reproduces the price within
  one minor unit per share; **and given** a price outside it, **then** `status = NO_ROOT_IN_BRACKET` and
  the value is null — never the bracket end. → *invariant / property.* (`P5`)
- **AC-F10.11** *(determinism)* — **Given** identical inputs and assumptions, **when** valued twice,
  **then** the serialised results are byte-identical. → *invariant / property.* (`INV-2`, `FE-16`)
- **AC-F10.12** *(assumptions are declared and versioned)* — **Given** a published assumption set,
  **when** any value changes without a version change, **then** loading refuses on the content hash;
  **and** no assumption value is a literal in `valuation/` code. → *data contract.* (`FE-2`'s rule)
- **AC-F10.13** *(★★ `fv_model` and `fv_analyst` never share a name)* — **Given** a `CashFlowBasis`
  with `origin = judgement`, **when** it is valued, **then** the result is an `AnalystValuation` with
  `kind = fv_analyst` and complete provenance; `valuation()` can never return one; and passing one where
  a `ValuationResult` is required raises. → *invariant / property.* (`VS-1`, `VS-3`, `INV-014`)
- **AC-F10.14** *(isolation)* — **Given** the source tree, **when** CI runs, **then**
  `src/feature_engineer/valuation/` imports nothing from `src/fundamental/`, no LLM gateway and no
  vendor SDK, and no `FeatureSpec` lists a valuation output as an input. → *invariant / property
  (structural).* (`ST-5`, `FE-21`, `A2`)
- **AC-F10.15** *(★ staging)* — **Given** a bundle containing a rendered valuation, **when** its blind
  view is built, **then** the valuation part is absent; and it is present in the full view. →
  *integration.* (`RA-14`, `MP-3`)
- **AC-F10.16** *(a vendor DCF is a cross-check only)* — **Given** D-07 supplies a vendor DCF field,
  **when** a valuation is produced, **then** that field appears, if at all, only under a cross-check key
  and never as `value_per_share`. → *invariant / property (structural).* (`fmp-api`)

- **AC-F10.17** *(★ the `D6` cash-flow formula)* — **Given** trailing operating cash flow, interest
  expense, income tax, pretax income, capex and stock-based compensation worked by hand, **when** the
  reported basis is built, **then** `base_fcff = OCF + interest × (1 − t) − capex − SBC` with
  `t = income_tax ÷ pretax_income`; **and given** pretax income ≤ 0, **then** `t = 0` and the basis
  records that the loss rule applied; **and given** positive pretax income with `t` outside `[0, 1]`,
  **then** it raises `ValuationUnavailable` naming the tax rate — never a substituted statutory rate.
  → *unit.* (`D6`, `P5`) ✏ *amended 2026-09-14 (`DX-104`): a loss year was a refusal.*

- **AC-F10.18** *(★ one formula, any span — for `D5`'s normaliser)* — **Given** one ANNUAL row (a
  350–380-day span), **when** `annual_basis` runs, **then** it applies exactly `D6`'s formula to that
  year (same function as the trailing basis, `FE-25`) and returns FCFF and revenue; a non-annual span
  refuses; **and** `trailing_total` sums one canonical item over the same four trailing quarters
  `reported_basis` uses. → *unit.* (`D6`, `D5`, `FE-25`) ✏ *added 2026-09-13 with the `J-20` build.*

- **AC-F10.19** *(★ the cycle averages are D-02's — `RA-45`)* — **Given** annual rows and a window of
  fiscal years, **when** `cycle_average_fcff` / `cycle_average_fcff_margin` run, **then** they return the
  mean annual `D6` FCFF (or the mean FCFF margin × trailing revenue) with the years used; **and given** a
  window with an absent or unusable year, **then** they raise naming every such year — never an average
  around the gap; **and** `src/fundamental/` holds no series arithmetic for it. → *unit.* (`RA-45`, `D5`,
  `P5`) ✏ *added 2026-09-13: the first `D5` build put the averaging in D-01 and `RA-45`'s structural
  guard refused it (L3 `DX-105`).*

- **AC-F10.24** *(★ a 10-K's balance sheet — `D12`)* — **Given** a latest quarterly row DERIVED from a 10-K (flows,
  no balance items) and an annual row with the same `period_end` and `accession_id` carrying cash, debt and
  securities, **when** net debt is computed, **then** it uses the annual row's values, each component citing
  that accession and date, and the diluted share count when the quarter has none; **and given** an annual row from a DIFFERENT accession, or none, **then** it raises
  `ValuationUnavailable` naming the items — never a stale quarter's figure. → *unit* + *integration* (MU's
  FY2026 10-K). ✏ *added 2026-10-21 (`DX-176`).*

- **AC-F10.21** *(★ a result declares what it cannot compute — `D9`)* — **Given** any valuation,
  **when** its trail is read, **then** `known_limits` names every figure `D6`/`D8` cannot compute from
  D-07's facts — today: government-incentive proceeds are not credited against capex — each with its
  reason; **and** a limit that IS computable (lease-funded equipment, which `D8` already counts as debt)
  does not appear. → *data contract.* (`PG-10`, `DX-116`) ✏ *added 2026-09-16.*

- **AC-F10.20** *(★ net debt counts securities and finance leases — `D8`)* — **Given** a latest quarter
  reporting marketable securities (current and/or non-current) and finance-lease liabilities, **when**
  net debt is computed, **then** it subtracts the securities and adds each finance-lease side whose debt
  tag does not already include leases, every counted amount a component with its tag; **and given** an
  item the filer does not report, **then** it is named in `known_omissions`, never counted as zero;
  **and** operating leases are never counted and are declared under `excluded_by_design`, not
  `known_omissions`. → *unit* +
  *integration* (Micron's recorded facts against the 10-Q). ✏ *added 2026-09-14.*

- **AC-F10.22** *(★ the price requirement by duration — `D10`)* — **Given** an assumption set with a
  `duration_table`, **when** a valuation is produced, **then** `implied_by_duration` holds one row per
  declared period, each the `D7` solve with only `explicit_years` replaced, so the row for the set's own
  `explicit_years` equals `implied`; each row round-trips to the price within one minor unit per share
  or is `NO_ROOT_IN_BRACKET` with a null value; **and** `market_capitalisation = price × diluted_shares`
  exactly; **and given** a set with no table (`v1`), **then** the result carries no `implied_by_duration`
  key; **and** a `v2` trail recomputes every row from its own fields (`AC-F10.4`). → *invariant /
  property.* (`D10`, `P5`, `AP-2`) ✏ *added 2026-10-01.*

- **AC-F10.23** *(★ the required cash flow, in revenue terms — `D11`)* — **Given** a `v2` valuation,
  **when** its duration table is read, **then** each SOLVED row's `required_final_year_fcff` equals the
  final explicit-year flow of `discount` at that row's growth and period, and `share_of_trailing_revenue`
  equals it ÷ the trailing four-quarter revenue (the quarters `D6` uses); a `NO_ROOT_IN_BRACKET` row has
  both null; **and given** trailing revenue absent, **then** it raises `ValuationUnavailable` naming
  `revenue` — never a share over a substituted denominator; **and** a `v1` result carries neither field.
  → *invariant / property.* (`D11`, `P5`, `AP-2`) ✏ *added 2026-10-02.*

## 7. Decisions (resolved questions — kept with their rejected options)

**`D1` — Normalised earnings are owned by a judgement block that feeds D-02's mechanics.** *(Victor
Truong, 2026-09-13; register `QR-25`.)* The judgement chooses **which earnings to capitalise** —
normalising for the cycle, one-offs and non-GAAP adjustments, exactly the row `L0`'s valuation split
already puts on D-01's side. D-02 owns the arithmetic applied to it.
- ★ **How this keeps `FE-21` and `INV-014` intact.** `VS-4`: *"arithmetic that a judgement
  parameterises … is plain code inside D-01. The LLM chooses the inputs; it never does the
  multiplication."* The judgement's basis runs through the SAME pure function, but the result is
  `fv_analyst` — a distinct type, owned by D-01, never stored by D-02 and never in the panel. D-02's own
  `fv_model` stays judgement-free and consumable by both seats (`VS-2`).
- ★ **Why the judgement block must run blind (Stage A).** A normaliser that can see the price can
  back-solve earnings to justify it. `CT-F10.4` renders valuations as `computed`, which the blind view
  withholds, so the block cannot see what it would be anchoring to.
- ✗ **Rejected — D-02 normalises by rule** (e.g. a trailing-cycle average margin). For a cyclical the
  choice of window and method IS the valuation, and two reasonable analysts disagree about it — which
  is `L1-FE` §1.3's own test for *"belongs in D-01, not D-02"*.
- ✗ **Rejected — D-02 accepts the judgement's basis and publishes the result as its own output.** One
  name for arithmetic and for a conclusion is precisely what `VS-1` forbids, and it would put seat 2's
  judgement into a seat-8 artifact seat 3 may read (`FE-21`, `VS-3`).
- ⚠ **Consequence recorded, not applied:** `J-07`'s prompt currently says *"You are NOT estimating
  normalised earnings. That is arithmetic and belongs to D-02"*. `D1` contradicts that sentence; the
  prompt revision is `Q3`.

**`D2` — FCFF at a firm discount rate, minus net debt.** *(Adopted with the spec's approval, 2026-09-13.)* One of the two coherent designs `L1-FE` §8.1 names. ✗ **Rejected — owner earnings /
FCFE at the cost of equity:** equally coherent, but FCFE needs net borrowing per period, which the
canonical items do not carry, and a cost of equity needs a beta the vendor serves only as a Class-B
snapshot with no history (`fmp-api` trap 5). ⚠ The design `D-19` shipped mixed the halves of both.

**`D3` — A new build, not a port.** The inherited `DCFCalculator` exists only in the retired pipeline's
`backups/`; nothing in `src/` carries it. `FE-18`'s *"moves VERBATIM"* and `AC-2.26` therefore have no
subject. ✗ Rejected — porting it to fix afterwards: it would import `D-19` knowingly to remove it.

**`D4` — The assumption values (was `Q1`).** *(Victor Truong, 2026-09-13, as suggested.)* Published as
`dcf_two_stage@v1` in `config/valuation/dcf_two_stage_v1.yaml`:

| Value | Adopted | Why |
|---|---|---|
| discount rate | **9 % declared constant** | transparent and stable; a change is a deliberate version bump |
| terminal growth | **2.5 %** | about long-run nominal economic growth |
| explicit years | **10** | long enough to contain a full memory cycle |
| stage-1 growth (`fv_model`) | **2.5 % — equal to terminal** | keeps `fv_model` judgement-free; the growth question moves to implied expectations |
| band | discount **8 / 9 / 10 / 11 %** × terminal **1.5 / 2.5 / 3.5 %** | 12 points, wide enough to show fragility |
| implied bracket | stage-1 growth **−20 % to +40 %**, **60** bisection iterations | wide enough for cyclical prices |

✗ Rejected — **CAPM**: a cyclical's beta swings with the window chosen, the vendor serves beta only as a
Class-B snapshot, and D-02's own beta output is unbuilt; three more levers for no gain in transparency.
Revisit as a new version.

**`D5` — The normalised-earnings block chooses; code calculates (was `Q3`).** *(Victor Truong,
2026-09-13, option ⓐ.)* A NEW Stage-A, blind judgement block returns `method` (closed set, including
`insufficient_evidence`), `window` and cited `exclusions`; plain D-01 code computes `base_fcff` from that
choice. `J-07`'s sentence *"You are NOT estimating normalised earnings…"* is to be rewritten.
✏ **Corrected 2026-09-13 (`DX-105`): the arithmetic is D-02's, not "plain D-01 code".** Given a method and
a window, averaging a series is judgement-free — `RA-45` (*"D-01 performs no arithmetic that D-02 could
perform"*) is enforced structurally and refused the first build. D-01's normaliser validates the choice
and records provenance; D-02 (`valuation/normalised.py`, `AC-F10.19`) computes. `VS-5` had warned that
`VS-4`'s wording invites exactly this misreading. ✗ Rejected —
ⓑ extending `J-07` (two judgements in one answer, and its golden case would move); ⓒ no block
(`fv_model` alone misvalues a cyclical). ⚠ **Out of F10's code**: the block is a prompt plus D-01 code,
built separately; F10 fixes the contract it feeds (`CT-F10.3`). It needs a multi-year line-item history
in the blind bundle, which is permitted (`operating_ratios`-style, not an anchor).

**`D6` — The cash-flow formula (was `Q5`).** *(Victor Truong, 2026-09-13, option A, with SBC
subtracted.)* `base_fcff = OCF + interest × (1 − t) − capex − SBC`, `t = income_tax ÷ pretax_income`,
all trailing four discrete quarters. ✏ **Amended 2026-09-14 (`DX-104`, Victor): `t = 0` when pretax income
≤ 0** — a loss year pays no tax to shield, and refusing it made every cycle window through a trough
impossible (MU FY2016, FY2023). `FORMULA_ID` → `…v2`. ★ Adding back after-tax interest makes the flow pre-financing,
matching `D2`'s firm rate; subtracting SBC treats pay in shares as a cost owners bear. ⚠ Needs three
facts D-07 does not yet ingest — `IncomeTaxExpenseBenefit`, pretax income, `ShareBasedCompensation` —
an ingest-tag extension (`src/data_engine/ingest/edgar_facts.py`), definitional, same change. ✗ Rejected
— B `EBIT × (1 − t) + D&A − capex − ΔNWC` (more items, more places to err); leaving SBC in (overstates
the owners' cash).

**`D8` — Net debt counts marketable securities and leases (was `Q2`).** *(Victor Truong, 2026-09-14.)*
Net debt = debt + finance leases not already inside a lease-inclusive debt tag − cash − marketable
securities (current and non-current; MU: $648M + $1,402M, 10-Q line 559). A finance lease's principal is
paid in FINANCING cash flow, so it is debt `D6`'s flow does not bear. ★ **Operating leases are OUT —
ⓐ, Victor, 2026-09-14 (`DX-106`):** under ASC 842 an operating lease's payments run through OPERATING
cash flow, which `D6` already subtracts, so the flow bears them; adding the liability to net debt would
count the lease twice, `D-19`'s mistake in miniature. Every result declares it under
`net_debt.excluded_by_design`. ✗ Rejected — ⓑ count the liability AND add back operating lease cost in `D6`
(a `v3` formula, more items; ⚠ MU stopped tagging `OperatingLeaseCost` after 2025-11-27, so ⓑ would refuse
MU today). **`DX-103` (same day):** `CANONICAL` gained the fallback tags
(`InterestExpenseNonoperating`, `DebtCurrent`, `LongTermDebtAndCapitalLeaseObligations`) — `fundamental`
feature contract → `v3` (`FE-2`).

**`D9` — The two capex questions the analysis raised, answered (`DX-116`).** *(2026-09-16.)*
`J-09` and `J-11` each found a way `D6`'s capex term could misstate the base. Measured on Micron:

| Raised by | Claim | Answer |
|---|---|---|
| `J-11` | Equipment arrives through finance leases, OUTSIDE the capex line, so FCFF is flattered | ✅ **No change — `D6` is already coherent.** `D8` counts finance leases IN NET DEBT ($3,107M at 2025-05-29). Charging the $1,394M of lease-funded additions to capex as well would count the same equipment TWICE — once as debt subtracted from equity value, once as investment reducing the flow. ★ `J-14` reached this independently when it contradicted `J-11` |
| `J-09` | Capex is charged GROSS; the 10-Q guides it *"net of proceeds from government incentives"* ($1,294M in 9M FY25) | ⚠ **Cannot be computed, and is DECLARED.** No tagged fact for incentive PROCEEDS exists anywhere in Micron's `companyfacts` (`GovernmentAssistance*` carries balances, not the cash line); the figure lives only in filing prose. A TTM figure would need an extraction item per filing, which is `E-07`'s territory, not D-02's |

★ **So the rule is: state the limit on the result** (`PG-10`, `CT-F10.2` `known_limits`) rather than
silently valuing as if it did not exist. ⚠ It is material — crediting 9M incentives alone would roughly
double MU's $1,349M trailing base. ✗ Rejected: applying only the computable half (it biases the base
DOWN by the whole lease amount); a statutory or estimated incentive rate (a fabricated input, `P5`).

**`D7` — Implied expectations solves for stage-1 growth (was `Q4`).** *(Adopted with the contract at
approval.)* It reads as *"the price requires X % a year for N years"* — the sentence `J-09` reasons
about. ✗ Rejected: an implied cash-flow level (harder to judge); implied terminal growth (hides the
question in the least-knowable number).

**`D10` — The price requirement by duration, and market capitalisation.** *(Victor Truong, 2026-10-01.)*
`J-09`'s first live answer could not set its third requirement — *"28.3 % for 10 years, then 2.5 %"* —
against Stage A, because the 10 years is a declared assumption and `implied_duration` was declared
absent. ★ **Adopted: re-run `D7`'s solve at each period of a declared table, 5 / 7 / 10 / 15 years,
in a new set `dcf_two_stage@v2`** (every other value identical to `v1`). The rows read as *"the price
requires X % for 5 years … Y % for 15"*, so a reader can compare a required run of growth with the
company's own history without the system choosing one horizon for them. Market capitalisation (raw
price × diluted shares) joins the trail, so `J-09` never multiplies it in a prompt. ✗ Rejected —
ⓐ **solving for the number of years at a fixed growth**: one number, but the fixed growth is a judgement
the system would have to supply; ⓑ **valuation multiples** (EV/FCFF, P/FCF): still a non-goal (§2);
ⓒ **adding the table to `v1`**: `v1` is published and immutable (`AC-F10.12`).

**`D11` — The required cash flow, stated in revenue terms.** *(Victor Truong, 2026-10-02.)* `J-09`'s
second live answer still had one curable `insufficient_evidence` row — *"implied operating margin: not
derivable"* — and it capped conviction (`DX-140` counts curable absences). ★ **Adopted: for each
duration row, the FCFF the price requires in the final explicit year, and that figure as a share of
trailing revenue, labelled *at flat revenue*.** Pure arithmetic on numbers the trail already holds, so a
reader can set it beside the company's own FCFF margin history (MU: the price needs ≈48 % at flat
revenue at 10 years; its best year FY2016–FY2024 was 28.5 %). ★ **Reconciling with `D7`:** `D7` rejected
an implied cash-flow level as the thing to SOLVE FOR; `D11` changes no solve — it restates the solved
answer in a second unit. ✗ Rejected — ⓐ accepting the cap (a curable gap left open on every thesis);
ⓒ solving for margin at an assumed revenue growth (the growth is a judgement the system would supply,
which `D7` avoided). ⚠ It is an FCFF share of revenue, **not** an operating margin; the label says so.

**`D12` — After a 10-K, the latest quarter's balance sheet is the annual row's (`DX-176`).** *(Victor, 2026-10-21.)*
A 10-K reports no fourth quarter: D-07 DERIVES Q4's flows as the year minus nine months, and a derived row
has no balance items — the year-end balance sheet (cash, debt, securities, leases) is an INSTANT on the
ANNUAL row. `CT-F10.2` reads net debt "from the latest trailing quarter", so every 10-K-anchored valuation
refused (`ValuationUnavailable … missing ['cash', 'long_term_debt', 'current_debt']`), found on the first
live `thesis_for` (F13 `D7`). ★ **Adopted:** an instant item absent on the latest quarterly row is read from
the annual row with the SAME `period_end` AND the SAME `accession_id` — the same balance sheet on the same
date in the same filing, so nothing is substituted; the component still cites that accession and date. ✏ **The diluted share count too (`DX-177`, same day):** a 10-K
tags it only for the YEAR, and DE-84 now refuses to derive a Q4 average by subtraction (it produced 1,000,000 for
MU); so the year's weighted-average diluted count from that same annual row is used — MU FY2026 1,143M against
Q3's 1,145M — and is the one balance input that is a year's average rather than a point.
✗ Rejected — ⓐ the previous quarter's balance sheet (a stale figure, three months before the price it is set
against); ⓑ any annual row with that end date (a later amendment could supply a different filing's figure);
ⓒ deriving Q4 balance items in D-07 (an instant is not a flow; there is nothing to difference).

## 8. Open questions (must resolve before/at implementation)

- ~~**Q1**~~ → `D4`. ~~**Q3**~~ → `D5`. ~~**Q4**~~ → `D7`. ~~**Q5**~~ → `D6`. *(Kept below, struck, for the
  argument that preceded each decision.)*
- ~~**Q1 — The assumption VALUES.**~~ Discount rate: a declared constant, or CAPM (risk-free + beta × ERP) —
  and if CAPM, whose beta (D-02's own from our prices, `§6.4`, not the vendor snapshot)? Terminal growth,
  explicit years, band steps, implied bracket. ★ **Policy, the fund manager's.** Blocks the NUMBERS of
  `fv_model`, not the mechanics or any AC except the published set in `AC-F10.12`.
- ~~**Q2 — Net debt's definition.**~~ → `D8` (operating leases out by design, `DX-106`). The canonical items (`src/feature_engineer/fundamental/items.py`) carry
  `cash`, `long_term_debt`, `current_debt` — **not marketable investments, finance leases or operating
  leases.** ⚠ Measured on MU: cash $10,163M vs cash + investments **$12,213M** (10-Q line 559) — a $2B
  swing in equity value. Adding canonical items is D-07 definitional work. Blocks `AC-F10.2`'s
  real-data use (the property test runs on synthetic inputs regardless).
- ~~**Q3 — The normalised-earnings judgement block.**~~ A new J-block (or a revised `J-07`), Stage A, blind,
  emitting a `CT-F10.3` basis with a closed method field and an `insufficient_evidence` exit; `J-07`'s
  sentence rewritten. A prompt-doc change and a version bump — Victor's. Blocks `T2` in practice, not
  `AC-F10.13` (tested with a synthetic basis).
- ~~**Q4 — What implied expectations solves for.**~~ Stage-1 growth (recommended — it reads as *"the price
  requires X % a year for N years"*), an implied cash-flow level, or implied terminal growth.
- ~~**Q5 — The FCFF formula.**~~ Under US GAAP operating cash flow is AFTER interest paid, so
  `OCF − capex` is not FCFF. Coherent options: `OCF + interest × (1 − t) − capex` (needs a tax rate the
  canonical items lack) or `EBIT × (1 − t) + D&A − capex − ΔNWC` (needs D&A and working capital). ⚠ This
  is `D-19`'s question in miniature — choosing a formula that mismatches `D2`'s discount rate would
  reintroduce it. Blocks `CT-F10.2.basis.formula_id`.

## 9. Traceability (spec → test → code)

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-F10.1 | `tests/unit/test_valuation_f10.py::test_ac_f10_1_the_mechanics_match_a_hand_worked_two_stage_dcf` | `src/feature_engineer/valuation/dcf.py::discount` |
| AC-F10.2 | `tests/unit/test_valuation_f10.py::test_ac_f10_2_value_per_share_subtracts_net_debt` (3 cases) | `src/feature_engineer/valuation/dcf.py::per_share` |
| AC-F10.3 | `tests/unit/test_valuation_f10.py::test_ac_f10_3_discount_rate_not_above_terminal_growth_refuses` · `::test_ac_f10_3_non_positive_shares_refuses` | `src/feature_engineer/valuation/dcf.py` |
| AC-F10.4 | `tests/unit/test_valuation_f10.py::test_ac_f10_4_recomputing_from_the_trail_alone_reproduces_everything` | `src/feature_engineer/valuation/types.py::ValuationResult.to_json` |
| AC-F10.5 | `tests/unit/test_valuation_f10.py::test_ac_f10_5_every_monetary_field_carries_one_currency` · `::test_ac_f10_5_a_second_currency_refuses` | `src/feature_engineer/valuation/types.py`, `src/shared/money.py` |
| AC-F10.6 | `tests/unit/test_valuation_f10.py::test_ac_f10_6_as_of_is_required` · `::test_ac_f10_6_nothing_after_as_of_and_the_price_is_the_RAW_series` · `::test_ac_f10_6_a_filing_after_as_of_is_not_used` | `src/feature_engineer/valuation/service.py` |
| AC-F10.7 | `tests/unit/test_valuation_f10.py::test_ac_f10_7_*` (5) — ⚠ on synthetic CT-7.2 rows; the RECORDED-fixture half is ⬜ pending (§9 note) | `src/feature_engineer/valuation/basis.py::trailing_quarters` |
| AC-F10.8 | `tests/unit/test_valuation_f10.py::test_ac_f10_8_*` (3 groups, 8 cases) | `src/feature_engineer/valuation/basis.py`, `src/feature_engineer/valuation/service.py` |
| AC-F10.9 | `tests/unit/test_valuation_f10.py::test_ac_f10_9_the_band` | `src/feature_engineer/valuation/band.py::band` |
| AC-F10.10 | `tests/unit/test_valuation_f10.py::test_ac_f10_10_implied_growth_round_trips_to_the_price` · `::test_ac_f10_10_a_price_outside_the_bracket_is_NO_ROOT_never_the_bracket_end` | `src/feature_engineer/valuation/implied.py::solve_implied` |
| AC-F10.11 | `tests/unit/test_valuation_f10.py::test_ac_f10_11_identical_inputs_serialise_byte_identically` | `src/feature_engineer/valuation/types.py` |
| AC-F10.12 | `tests/unit/test_valuation_f10.py::test_ac_f10_12_*` (4) | `src/feature_engineer/valuation/assumptions.py::load`, `config/valuation/dcf_two_stage_v1.yaml` |
| AC-F10.13 | `tests/unit/test_valuation_f10.py::test_ac_f10_13_*` (4 tests, 7 cases) | `src/feature_engineer/valuation/types.py::require_fv_model`, `src/feature_engineer/valuation/service.py::value_on_basis` |
| AC-F10.14 | `tests/structural/test_valuation_isolation.py::test_ac_f10_14_valuation_imports_no_analyst_domain_no_llm_no_vendor_sdk` · `::test_ac_f10_14_no_feature_spec_lists_a_valuation_output_as_an_input` | `src/feature_engineer/valuation/` |
| AC-F10.15 | `tests/unit/test_valuation_f10.py::test_ac_f10_15_the_valuation_part_is_withheld_from_the_blind_view` | `src/feature_engineer/valuation/render.py::as_bundle_part` |
| AC-F10.16 | `tests/structural/test_valuation_isolation.py::test_ac_f10_16_a_vendor_dcf_is_never_read_as_fv_model` | `src/feature_engineer/valuation/service.py` |
| AC-F10.17 | `tests/unit/test_valuation_f10.py::test_ac_f10_17_the_reported_basis_is_ocf_plus_after_tax_interest_minus_capex_minus_sbc` · `::test_ac_f10_17_a_loss_year_uses_a_zero_tax_rate` (2) · `::test_ac_f10_17_an_out_of_range_rate_on_a_profit_refuses_and_names_it` (2) | `src/feature_engineer/valuation/basis.py::reported_basis` |
| AC-F10.18 | `tests/unit/test_valuation_f10.py::test_ac_f10_18_annual_basis_applies_D6_to_one_fiscal_year` · `::test_ac_f10_18_a_non_annual_span_refuses` (3) · `::test_ac_f10_18_trailing_total_sums_the_same_four_quarters` | `src/feature_engineer/valuation/basis.py::annual_basis`, `::trailing_total`, `::_d6` |
| AC-F10.21 | `tests/unit/test_valuation_f10.py::test_ac_f10_21_the_result_declares_what_it_cannot_compute` | `src/feature_engineer/valuation/basis.py::KNOWN_LIMITS`, `src/feature_engineer/valuation/types.py` |
| AC-F10.20 | `tests/unit/test_valuation_f10.py::test_ac_f10_20_net_debt_counts_securities_and_finance_leases` · `::test_ac_f10_20_a_lease_inclusive_debt_tag_is_not_counted_twice` · `::test_ac_f10_20_an_unreported_item_is_declared_never_zero` · `::test_ac_f10_20_operating_leases_are_excluded_by_design_not_omitted` · `tests/integration/test_valuation_real_mu.py::test_ac_f10_20_real_net_debt_matches_the_10q` | `src/feature_engineer/valuation/basis.py::balance`, `::known_omissions` |
| AC-F10.19 | `tests/unit/test_normalise_d5.py::test_ac_f10_19_the_averages_are_D02_functions_and_D01_holds_no_series_arithmetic` · `::test_ac_f10_19_a_year_filed_after_as_of_is_absent_and_a_mixed_currency_window_refuses` · `tests_src/test_architecture.py::test_architectural_rule_holds` (RA-45) | `src/feature_engineer/valuation/normalised.py::cycle_average_fcff`, `::cycle_average_fcff_margin`, `::annual_history` |

| AC-F10.22 | `tests/unit/test_valuation_f10.py::test_ac_f10_22_*` (8 tests, 10 cases; 5 of 5 mutations caught) | `src/feature_engineer/valuation/implied.py::implied_by_duration`, `src/feature_engineer/valuation/assumptions.py` (`duration_table`), `src/feature_engineer/valuation/service.py::_assemble` (`market_capitalisation`), `config/valuation/dcf_two_stage_v2.yaml` |

| AC-F10.24 | `tests/unit/test_valuation_f10.py::test_ac_f10_24_*` (4: the annual balance sheet · another filing's row refused · the year's share count · end to end through `valuation()`) | `src/feature_engineer/valuation/basis.py::_with_year_end_balance`, `src/feature_engineer/valuation/service.py::_assemble` |

| AC-F10.23 | `tests/unit/test_valuation_f10.py::test_ac_f10_23_*` (4 tests; 4 of 4 mutations caught) | `src/feature_engineer/valuation/implied.py::implied_by_duration`, `src/feature_engineer/valuation/types.py::DurationRow`, `src/feature_engineer/valuation/service.py::_assemble` (`trailing_revenue`) |

✅ **24 of 24 ACs** have passing tests (AC-F10.24 added 2026-10-21 with `D12`; AC-F10.23 added 2026-10-02 with `D11`; AC-F10.22 2026-10-01 with `D10`). Previously: **21 of 21 ACs** have passing tests (AC-F10.19 added with `J-20`, `DX-105`; AC-F10.20 with `D8`). Earlier count: **18 of 18 ACs have passing tests, 2026-09-13** — 60 unit + 3 real-data integration tests; **16 of 16 mutations caught** after two
weak tests were strengthened (a contiguity test that tripped the COUNT check first, and a refusal test
that passed through the second guard instead of the first). Also required by `D-03`'s `AC-3.14`: three
MethodEntries under `src/feature_engineer/methods/entries/` — the FCFF formula, the DCF mechanics and
the implied-growth solve.

⚠ **Honest limits, stated on the table they qualify:**
- ✅ **`AC-F10.7`'s recorded-fixture half — CLOSED 2026-09-13.** Micron's EDGAR facts were ingested and a
  valuation-tag subset promoted to `tests_src/fixtures/edgar/MU_facts_valuation_subset.parquet`;
  `tests/integration/test_valuation_real_mu.py` asserts cash, debt and shares against the 10-Q's own
  lines. ⚠ It found what synthetic rows could not: real quarters abut with gaps **[1, 0, 0]** days, and
  Micron files `InterestExpenseNonoperating` and lease-inclusive debt tags (L3 `DX-103`).
- ✅ **A real company has been valued** (without a price — FMP not called): MU `fv_model` **$14.13/share**
  as of 2025-06-26 (trailing FCFF $1,349M) and **$363.40** as of 2026-09-13 (trailing FCFF $25,164M, net
  cash $19,273M). ★ The 26× swing on one cycle is `D5`'s reason to exist. ✏ **2026-09-14, after `D8` and
  `D6` v2:** net debt $3,328M ⇒ **$15.96** (2025-06-26); net cash $24,406M ⇒ **$367.89** (2026-09-13).
- ✅ **`J-20` ran live on MU** (`run-2026-09-14T122547-mu-j20`): `cycle_average_fcff` FY2016–FY2024 ⇒ basis
  **$1,287M** ⇒ **$15.09/share** by the same mechanics — ⚠ indicative only; no price, so no `AnalystValuation`.
- ✅ **`CT-F10.4` wired** — `bundle_for(..., valuation_assumptions=…)` adds the part (opt-in, so every
  existing `bundle_hash` is unchanged); an unavailable valuation becomes a part naming what is missing.
  ⬜ No Stage-B runner calls it yet (`J-09` is undeclared).
