# F11 — Reference-class base rates (D-02 `base_rates`, the `J-10` input)

> **Spec-ID:** F11 · **Status:** 🟢 **approved 2026-10-02** (Victor Truong) · **Drafted:** 2026-10-02
> ✅ Approved with `Q1`–`Q4` answered as suggested → `D3`–`D6`.
> **Source discussion:** `sdd/design/rel1_design/L3-build-sequence.md` §2.1q decision 1 (Victor,
> 2026-10-02): reference class = **memory makers from EDGAR — Micron, SanDisk (pre-2016 and the 2025
> spin-off), Western Digital** — used **beside a published all-company table**.
> **Home:** D-02 `src/feature_engineer/base_rates/` · seat 8 (neutral ground) · serves `CT-9.2` via `J-10`.
> **Governs:** `constitution.md` — `P5` fail loud · `AP-5` deterministic · `INV-1` no look-ahead ·
> `INV-2` determinism · `INV-014`/`FE-21` the analyst firewall · `MO-1` money · `PG-10` claims carry their
> limits. Reuses `F10` `D6` (`annual_basis`) so a member's FCFF is the subject's formula, exactly.

---

## 1. Goal & why

**Say how often companies like the subject have done what its price requires — computed, with its
sample size on every number.**

★ **Why now, measured 2026-10-02.** `J-10` (base rates) answered both MU theses with
`INSUFFICIENT_EVIDENCE`: *"a cross-company base rate for decade-long ~28 % FCFF compounding among
capital-intensive semiconductor manufacturers"* — because the bundle declares `reference_class_base_rates`
absent (*"the bundle is single-company; no reference-class dataset exists"*). `F10` `D10`/`D11` now state
what the price requires in three forms — a growth rate per period, a run of years, and a final-year FCFF
as a share of revenue — so each can be set against the same quantity measured on a reference class.

⚠⚠ **The sample is small, and that is the finding to keep in view.** On EDGAR's XBRL era the class is
Micron (~15 usable fiscal years), SanDisk (~4 pre-2016, ~2 post-2025) and Western Digital (~17, mostly
hard-drive economics). Samsung, SK hynix and Kioxia do not file on EDGAR. ⇒ Every rate states `n` and
which members contributed, and the published all-company table is shown beside it so a reader can weigh a
memory-specific rate on a small `n` against a large-sample rate on a broad class.

## 2. Scope / non-goals

**In scope**
- A **declared, versioned reference class** (`CT-F11.1`): members, CIKs, the years each contributes, and
  why — the same discipline as `config/sector/memory_v1.yaml`.
- **Member annual rows from D-07** (EDGAR companyfacts), point in time, through `F10`'s `annual_basis`
  (`D6`), so a member's FCFF and FCFF margin use the subject's formula.
- **Three statistics** (`CT-F11.2`), each matched to a form of the price requirement `F10` already states.
- **A published table** (`CT-F11.3`) entered by hand from the source, each value with its page.
- **Rendering** as a `computed` bundle part, withheld from the blind view (`RA-14`).

**Non-goals (this spec)**
- ✗ **Choosing members or thresholds by judgement in code.** Members are config (Victor's); thresholds
  come from the subject's own `F10` trail, never from a literal.
- ✗ **Non-EDGAR companies** (Samsung, SK hynix, Kioxia) — no point-in-time source this repo holds.
- ✗ **Pre-XBRL years** (HTML filing parsing) — a separate ingest decision.
- ✗ **Any statistic recalled rather than computed or transcribed** (`P5`).

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | A Stage-B bundle is assembled | `ticker`, `as_of`, the reference class, the subject's `F10` result | `src/feature_engineer/base_rates/service.py::base_rates` |
| T2 | The bundle builder renders it | a `BaseRates` result | `src/feature_engineer/base_rates/render.py::as_bundle_part` |
| T3 | Ingest of member facts | the class config | `tools/ingest_reference_class.py` (D-07 `ingest/edgar_facts.py`) |

## 4. Behaviour & reuse

- **Members' facts come only through D-07** (`FE-23`), ingested from EDGAR companyfacts like the subject's.
  ⚠ A recorded subset is promoted to `tests_src/fixtures/` — `.state/` is gitignored (`DX-12`).
- **Point in time** (`INV-1`): a member-year counts only if its 10-K was filed on or before `as_of`.
- **One formula** (`FE-25`): each member-year goes through `F10` `annual_basis`; a year it cannot resolve
  is **excluded and named** with its reason, never zero (`FE-14`).
- **The subject is in its own class, and the rates are also shown without it** — otherwise Micron is most
  of its own base rate and the reader cannot see it.
- **Thresholds come from the subject's trail** (`F10` `D10`/`D11`): the required growth per period, the
  periods themselves, and the required final-year share of revenue. ⇒ The rates answer exactly the
  questions `J-09`/`J-10` ask, and no number in this module is a policy literal.

## 5. Contracts (inline)

**CT-F11.1 — `ReferenceClass`** (`config/reference_class/<name>_v<version>.yaml`, content-hashed like `CT-F10.1`):
```json
{ "name": "memory", "version": 1, "content_hash": "sha256:…",
  "decided_by": "Victor Truong, 2026-10-02",
  "members": [{"name": "str", "cik": "str", "role": "memory | memory_and_storage",
               "years": {"from": "int | null", "to": "int | null"}, "why": "str"}],
  "excluded": [{"name": "str", "why": "str"}] }
```

**CT-F11.2 — `BaseRates`** (returned and rendered; never stored in a panel):
```json
{ "class": {"name": "str", "version": "int", "content_hash": "str"}, "as_of": "date",
  "member_years": [{"member": "str", "fiscal_year": "int", "fcff": "Money", "revenue": "Money",
                    "fcff_margin": "decimal", "filing_date": "date"}],
  "excluded_years": [{"member": "str", "fiscal_year": "int", "reason": "str"}],
  "margin_reach": [{"threshold": "decimal", "periods": "int — the F10 row it came from",
                    "all": {"hits": "int", "n": "int"}, "excluding_subject": {"hits": "int", "n": "int"}}],
  "positive_runs": [{"at_least_years": "int", "all": {"hits": "int", "n": "int"},
                     "excluding_subject": {"hits": "int", "n": "int"}}],
  "revenue_cagr_reach": [{"periods": "int", "required_growth": "decimal",
                          "all": {"hits": "int", "n": "int"}, "excluding_subject": {"hits": "int", "n": "int"},
                          "windows": "overlapping"}],
  "published": "CT-F11.3 | null" }
```
Rules: every rate is `hits` and `n`, never a bare percentage; `n = 0` renders as *"no observations"*,
never 0 %. `margin_reach` counts member-years with `fcff_margin ≥ threshold`; `positive_runs` counts
maximal runs of consecutive positive-FCFF years of length ≥ `at_least_years`; `revenue_cagr_reach`
counts `periods`-year windows whose revenue CAGR ≥ `required_growth`.

**CT-F11.3 — `PublishedTable`** (`config/reference_class/published_<slug>.yaml`):
```json
{ "source": {"title": "str", "authors": "str", "publisher": "str", "date": "date", "copy": "str — where the transcribed copy came from"},
  "measure": "str — e.g. 'sales CAGR, inflation-adjusted (2015 $)'",
  "reference_class": "str — e.g. 'starting sales > $25,000 Mn'",
  "horizons": [{"years": "int", "total": "int", "page": {"printed": "int", "pdf": "int"},
                "bins": [{"label": "str", "low": "decimal | null", "high": "decimal | null",
                          "observations": "int", "rate_as_printed": "str"}]}] }
```
Rules: every horizon carries the pages of BOTH its rates and its observation counts; ⚠ **values are
transcribed from the document, never recalled** — a loader refuses a horizon without pages, and refuses
one whose bin counts do not sum to its `total`. ✏ *Refined at approval (`D5`): counts, not only
percentages, so the published line is `hits/n` like every other rate (`AC-F11.6`).* Because the book bins
growth in 5-point bands, a required rate inside a bin is reported as a **bracket**: at least the count at
or above the bin's upper edge, at most the count at or above its lower edge — never interpolated.

## 6. Acceptance criteria

- **AC-F11.1** *(declared class)* — **Given** a class config, **when** loaded, **then** a value changed
  without a version change refuses on the content hash, and every member and exclusion carries `why`.
  → *data contract.* (`CT-F11.1`, `FE-2`'s rule)
- **AC-F11.2** *(point in time)* — **Given** member filings dated after `as_of`, **when** base rates are
  computed, **then** no member-year with `filing_date > as_of` is used. → *invariant / property.* (`INV-1`)
- **AC-F11.3** *(one formula)* — **Given** a member annual row, **when** its FCFF is computed, **then** it
  equals `F10` `annual_basis` on that row; **and** a year that cannot resolve is in `excluded_years` with
  its reason, never counted as zero. → *unit.* (`FE-25`, `FE-14`, `P5`)
- **AC-F11.4** *(the three statistics, known answer)* — **Given** hand-worked member-years, **when**
  computed, **then** `margin_reach`, `positive_runs` and `revenue_cagr_reach` equal the hand counts, with and
  without the subject. → *unit.*
- **AC-F11.5** *(thresholds from the trail)* — **Given** a `v2` `F10` result, **when** base rates are
  built, **then** every threshold is a value from that result's `implied_by_duration`, and no threshold is
  a literal in `base_rates/` code. → *invariant / property (structural).*
- **AC-F11.6** *(n everywhere)* — **Given** any result, **when** rendered, **then** every rate shows
  `hits/n` and its members, and `n = 0` reads *"no observations"*. → *data contract.* (`PG-10`)
- **AC-F11.7** *(published table)* — **Given** a published-table file, **when** loaded, **then** a row
  without `page` refuses, and the rendered part names the source, edition and page beside each value. →
  *data contract.* (`P5`)
- **AC-F11.8** *(staging and isolation)* — **Given** a bundle with the part, **when** its blind view is
  built, **then** the part is absent; **and** `base_rates/` imports nothing from `src/fundamental/`, no
  LLM gateway and no vendor SDK. → *integration* + *structural.* (`RA-14`, `FE-21`, `ST-5`)
- **AC-F11.9** *(real data)* — **Given** the recorded fixture for the `memory@v1` members, **when** base
  rates are computed for MU as of 2025-06-26, **then** every member-year's revenue and FCFF trace to an
  accession id, and the result reproduces from the fixture alone. → *integration.* (`AP-2`)

## 7. Decisions

- **`D1` — Members (Victor, 2026-10-02):** Micron, SanDisk (CIK 1000180, pre-2016; CIK 2023554, 2025
  spin-off), Western Digital (CIK 106040, role `memory_and_storage`). ✗ Rejected: module makers (Netlist,
  SMART/Penguin — no fabs, so no capex cycle); niche memory (Everspin, Cypress — tiny or mixed); Spansion,
  ISSI, SST (0–1 usable XBRL years).
- **`D2` — Use (Victor, 2026-10-02):** the class AND a published all-company table, side by side.
- **`D3` — Western Digital counts FY2017–FY2025 only (was `Q1`; Victor, 2026-10-02):** the years it owned
  SanDisk's flash fabs, so a hard-drive company is not counted as a memory maker. ✗ Rejected: all XBRL
  years (FY2010–2026) — 7 more years of hard-drive economics.
- **`D4` — Capex falls back to `PaymentsToAcquireProductiveAssets` (was `Q2`; Victor, 2026-10-02):** the
  tag pre-2016 SanDisk files. Second in `CANONICAL["capex"]`, so a filer of the PP&E tag is unchanged;
  `fundamental` feature contract → `v4` (`FE-2`, as `DX-103` did).
- **`D5` — The published table is *The Base Rate Book* (was `Q3`; Victor, 2026-10-02):** Mauboussin,
  Callahan & Majd, Credit Suisse, 26 September 2016, Exhibit 4 (rates, printed p. 24) and its appendix
  (observations, printed p. 31), sales CAGR by starting size, class **starting sales > $25,000 Mn**
  (MU's trailing revenue was $33.8bn). ⚠ Two caveats travel with every rendered rate: the figures are
  **inflation-adjusted (2015 dollars)** while the price requirement is nominal, and they measure **sales**
  growth while the requirement is FCFF growth (equal only at a constant margin).
- **`D6` — Revenue-growth windows overlap (was `Q4`; Victor, 2026-10-02):** every N-year window is used,
  and every such rate is labelled *"overlapping windows — observations are correlated"*.

## 8. Open questions (must resolve before implementation)

✅ All four answered at approval → `D3`–`D6`. Kept below for the argument that preceded each.

- **Q1 — Western Digital's years.** All XBRL years (FY2010–2026, hard-drive economics until the 2016
  SanDisk acquisition), or only the flash-owning years (FY2017–FY2025)? ★ Suggested: **FY2017–FY2025**,
  so a hard-drive company is not counted as a memory maker; the cost is 7 fewer years.
- **Q2 — SanDisk (pre-2016) capex tag.** Its companyfacts carry no `PaymentsToAcquirePropertyPlantAndEquipment`;
  the capex line is under another tag. Adding the fallback is D-07 definitional work (as `F10` `D8` did).
  Without it, its years are excluded and named.
- **Q3 — The published table.** Which source and table: suggested Mauboussin & Callahan, *The Base Rate
  Book* (Credit Suisse, 2016), sales-growth CAGR by starting size. ⚠ Its values must be transcribed from
  the document with pages; if no copy can be obtained, the published line is declared absent.
- **Q4 — Overlapping windows.** `revenue_cagr_reach` over overlapping N-year windows inflates `n` with
  correlated observations; non-overlapping windows leave ~1–2 per member. Suggested: overlapping, labelled
  as such on every rate.

## 9. Traceability (spec → test → code)

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-F11.1 | `tests/unit/test_base_rates_f11.py::test_ac_f11_1_*` (3) | `src/feature_engineer/base_rates/config.py::load_class`, `config/reference_class/memory_v1.yaml` |
| AC-F11.2 | `tests/unit/test_base_rates_f11.py::test_ac_f11_2_a_year_filed_after_as_of_is_not_used` · `tests/integration/test_base_rates_real_memory.py::test_ac_f11_9_every_member_year_traces_to_an_accession_and_none_is_late` | `src/feature_engineer/base_rates/service.py::member_years` (+ `F10` `annual_history`) |
| AC-F11.3 | `tests/unit/test_base_rates_f11.py::test_ac_f11_3_*` (3) | `src/feature_engineer/base_rates/service.py::member_years`, `::history_from_rows` |
| AC-F11.4 | `tests/unit/test_base_rates_f11.py::test_ac_f11_4_*` (3) | `src/feature_engineer/base_rates/stats.py::margin_reach`, `::positive_runs`, `::revenue_cagr_reach` |
| AC-F11.5 | `tests/unit/test_base_rates_f11.py::test_ac_f11_5_*` (3) | `src/feature_engineer/base_rates/service.py::thresholds_from` |
| AC-F11.6 | `tests/unit/test_base_rates_f11.py::test_ac_f11_6_*` (2) | `src/feature_engineer/base_rates/render.py::rate`, `::as_bundle_part` |
| AC-F11.7 | `tests/unit/test_base_rates_f11.py::test_ac_f11_7_*` (3) | `src/feature_engineer/base_rates/config.py::load_published_table`, `src/feature_engineer/base_rates/stats.py::published_bracket`, `config/reference_class/published_base_rate_book_2016.yaml` |
| AC-F11.8 | `tests/unit/test_base_rates_f11.py::test_ac_f11_8_*` (2) · `tests/structural/test_consensus_in_the_bundle.py::test_f11_base_rates_fill_their_absence_only_for_a_class_member` | `src/feature_engineer/base_rates/render.py::KIND`, `tools/run_thesis_once.py::base_rates_for` |
| AC-F11.9 | `tests/integration/test_base_rates_real_memory.py::test_ac_f11_9_*` (3) | `tools/ingest_reference_class.py`, `tests_src/fixtures/edgar/reference_class/memory_v1/` |

✅ **9 of 9 ACs** have passing tests (2026-10-02); **9 of 9 mutations caught**. ⚠ On real data the class is
thinner than the members suggest (`L3` `DX-143`, closed 2026-10-02): `SalesRevenueNet` added as a revenue
fallback (MU 9 → 13 usable years); pre-2016 SanDisk excluded by decision (no total pretax income, no
interest-expense tag). Class: 21 member-years as of 2025-06-26, 8 without the subject.
