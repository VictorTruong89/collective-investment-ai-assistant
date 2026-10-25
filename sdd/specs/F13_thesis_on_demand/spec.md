# F13 — Thesis on demand (`thesis_for TICKER --as-of DATE`)

> **Spec-ID:** F13 · **Status:** 🟢 **approved 2026-10-20** (Victor: *"approve F13 as recommended"*; `Q1`–`Q4` → `D5`–`D8`) · ✅ **22/22 ACs green 2026-10-22** (✏ AC-F13.19 added 2026-10-21, `DX-183`; AC-F13.20 2026-10-22, `D14`; AC-F13.21–22 2026-10-22, `D15`) · **Drafted:** 2026-10-20
> **Source discussion:** `_TEMP_handover_2026-10-11.md` §4.1 · `sdd/design/rel1_design/L9-go-live-checklist.md` §13.2
> (`T1`…`T4`) · Victor, 2026-10-11: *D-01 next, linked to D-04's nomination* · Victor, 2026-10-20: *"step-1 is the full
> one-command thesis_for TICKER --as-of DATE … take run IDs as arguments. start with MU."*
> ✏ **Supersedes `T1`** (2026-10-06, *"keep the MANUAL chain"*).
> **Home:** D-01 `src/fundamental/` · seat 2 (this repo's nine-seat model, vision §3) · capabilities C7 · C8.
> **Governs:** `constitution.md` — `P5` fail loud · `AP-5` deterministic where computable · `INV-1` no look-ahead ·
> `PG-2` · `PG-10`. Design-tier sources, cited by id and never re-worded: `L1-fundamental-analysis.md` (`RA-1`, `RA-2`,
> `RA-14`, `RA-15`, `RA-16`, `RA-98`, `RA-108`), `L1-fundamental-analysis-master-prompt.md` (`X-01`, `MP-3`).

---

## 1. Goal & why

Today a thesis can be written for **one ticker at one date** — Micron as of 2025-06-26 — because
`tools/run_thesis_once.py` holds its inputs as **run-id constants** (`DEFAULT_STAGE_A`, `DEFAULT_EXTRACTIONS`), and
`tools/run_extraction_once.py` holds the filing as a constant (`FILINGS`). Any other date is a hand-run chain of seven
tools and an edit to the code (`L9` §13.2). F13 makes it **one command** that chains the existing steps, passes every
run id as an argument, and records the chain so it can be resumed, audited and replayed.

★ **Nothing analytical is new.** Every prompt block, every check and every commit rule is the one already built and
verified live (32/35 blocks). F13 is the plumbing between them.

## 2. Scope / non-goals

**In scope:**
- One command: `python tools/thesis_for.py TICKER --as-of DATE [--dry-run]`.
- The inputs for that date, resolved and checked before any model call: the periodic filing, the documents the
  multi-document blocks read, the industry sector file, the consensus fixtures, the price, the fundamentals ledger.
- The chain: filing → the E-block extractions → Stage A (`J-01`…`J-08`, `J-20`) → Stages B–D (`J-09`…`J-17`) →
  falsifier check and rule checks — each step a recorded run, its id written to a **chain manifest**.
- Resume: a re-run continues from the first step not completed; a completed step is never re-sent.
- **MU first.** The subject's industry must have a sector source list (today only `memory_v1`).
  ✏ *2026-10-22 (`D15`):* **SNDK** on `memory_v2` and **MRNA** on `vaccines_v1` join MU.

**Non-goals (this spec):**
- ⊘ **The nomination as default ticker** (hand-over §4.1 step 2). ✏ Step 3 — the thesis replacing the card's
  placeholder gate — was brought IN on 2026-10-21 (`D13`).
- ⊘ **Any other industry.** A peer set is Victor's to choose first (`T2`; memory rule *no domain content until
  decided*). `thesis_for` refuses a ticker whose industry has no source list.
- ⊘ **The daily run.** Theses stay on Victor's manual command only (2026-10-05).
- ⊘ **The paid API.** It stays off (2026-10-05); see `AC-F13.2`.
- ⊘ **New prompt blocks or prompt changes**, and the deferred `E-14`, `J-18`, `J-19`.
- ⊘ **New golden cases** (`L8` §9 — closed).

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | Victor, by hand | `TICKER`, `--as-of DATE` | `tools/thesis_for.py` (composition root, `CA-9`) |
| T2 | Victor, by hand — the free preview | the same, `--dry-run` | the same; no model call |

## 4. Behaviour & reuse (the lean "how")

```text
thesis_for MU --as-of D
  0  RESOLVE (free, no model)   periodic filing ≤ D (the filing index) · sector documents (D8 defers E-03/E-08's)
                                · sector file at D (ingest_sector_file over memory_v1) · consensus fixtures
                                (fetch_consensus) · raw price at D (FMP) · facts ledger (EDGAR)
                                → any input missing ⇒ STOP before step 1, naming it (P5)
  1  CONVERT                    convert_filing.py → a filing fixture + provenance sidecar
  2  EXTRACT                    run_extraction_once.py, one run per E-block, --filing <fixture>
  3  STAGE A                    run_judgement_once.py --stage-a --extractions <runs> --sector <file>
  4  STAGES B–D                 run_thesis_once.py --stage-a <map> --extractions <runs> --sector --price --as-of
  5  CHECK (free)               check_falsifiers.py · rule_checks.py over the new run
  every step → .state/thesis_for/<TICKER>_<D>/chain.json  (step, run id, status, input hashes)
```

**Reuse, not rebuild:** each step calls the existing runner's functions. The runners' constants become **defaults
of new arguments** — the MU 2025-06-26 values stay the defaults, so every existing command, golden replay and test
behaves exactly as before (characterization tests first, constitution §5 item 3).

**Inputs and where they live** (`D6`, `D9`–`D11`):

| Input | Found when | Supplied by |
|---|---|---|
| anchor filing | the newest row of `tests_src/fixtures/filings/index.json` for the ticker, form 10-Q or 10-K, filed ≤ `as_of`, and not older than 120 days | `--fetch-inputs` (EDGAR → `convert_filing` → fixture + `.meta.txt` + index row) |
| sector documents | every source on the industry's list has a document published ≤ `as_of` and not older than 120 days | EDGAR sources: `--fetch-inputs`. Company-IR sources: **by hand** (`D11`) |
| sector file | `.state/sector/<list>_<as_of>.json` — ✏ `<list>_<as_of>_<TICKER>.json` when the subject's own source was left out (`AC-F13.21`) | free chain step (`ingest_sector_file.py --as-of`) |
| consensus | the earliest fixture set fetched on or after `as_of` (`tests_src/fixtures/consensus/` or `…/consensus/<date>/`) | `--fetch-inputs` (FMP, into `consensus/<as_of>/`) |
| raw price | a `tests_src/fixtures/prices/<T>_raw_eod_*.json` whose window holds `as_of` and a session within 5 days before it | `--fetch-inputs` (FMP `non-split-adjusted`) |
| facts | `.state/facts/<T>.parquet` holds the anchor filing's accession | `--fetch-inputs` (EDGAR companyfacts, this ticker only) |

## 5. Contracts (inline)

**CT-F13.1 — chain manifest** (`.state/thesis_for/<TICKER>_<as_of>/chain.json`, rewritten atomically after each
step): `ticker`, `as_of`, `transport`, `created_at`, `inputs` (each with path, source, sha256, and for documents
`knowable_at`), `steps[]` — each `{step, block?, run_id, status ∈ {pending, done, failed}, started_at, ended_at,
error?}` — and `thesis_run_id` once step 4 is done.

## 6. Acceptance criteria

- **AC-F13.1** — **Given** a ticker and a date, **when** `thesis_for --dry-run` runs, **then** it makes no model
  call and prints every step, every input with found/missing, and the number of calls the live run would make. →
  integration (no network: recorded inputs).
- **AC-F13.2** — **Given** `CIA_LLM_TRANSPORT=anthropic_api`, **when** `thesis_for` runs live, **then** it refuses
  before any call (`PG-2`, Victor 2026-10-05: the paid API stays off). It prints which transport is live. → unit.
- **AC-F13.3** — **Given** any required input missing at `as_of` (filing, sector file, consensus, price, facts),
  **when** `thesis_for` runs, **then** it stops before the first model call and names each missing input and the
  command that supplies it — never a partial thesis (`P5`). → unit.
- **AC-F13.4** — **Given** a document knowable only after `as_of` (a filing, a sector document, a consensus row, a
  price bar), **when** inputs are resolved, **then** it is not used (`INV-1`). → invariant/property.
- **AC-F13.5** — **Given** a ticker with no industry sector source list, **when** `thesis_for` runs, **then** it
  refuses and says the peer set is Victor's to choose (`T2`). → unit.
- **AC-F13.6** — **Given** a step completes, **when** the next starts, **then** the chain manifest already records the
  completed step's run id and status (`CT-F13.1`), and each later step receives the run ids it reads **as
  arguments** — no constant is edited. → integration.
- **AC-F13.7** — **Given** a chain that stopped at step *k* (a failure, a session limit), **when** `thesis_for` is run
  again with the same ticker and date, **then** steps before *k* are carried (their runs re-verified, `X-01` /
  `RA-108`), nothing completed is re-sent, and the chain continues from *k*. → integration.
- **AC-F13.8** — ★ **Known answer.** **Given** MU as of 2025-06-26 and the recorded runs, **when** the chain is
  resolved from them, **then** the Stage-A map and the extraction list it passes to step 4 equal today's
  `DEFAULT_STAGE_A` and `DEFAULT_EXTRACTIONS`, and the bundle it builds for `J-09` has the same `bundle_hash` as the
  recorded fourth MU thesis's. → golden/characterization.
- **AC-F13.9** — **Given** the runners' constants become argument defaults, **when** each runner is invoked as before
  (no new argument), **then** its output is unchanged — the existing golden replays and runner tests pass untouched.
  → golden/characterization.
- **AC-F13.10** — **Given** a thesis produced by `thesis_for`, **when** step 5 runs, **then** the falsifier check and
  the rule checks run over it and their results are recorded in the chain manifest beside the thesis run id. →
  integration.
- **AC-F13.11** — **Given** `--fetch-inputs`, **when** it runs, **then** it fetches only from EDGAR and FMP (free /
  standing-approved), writes a NEW fixture and never overwrites one, and leaves a company-IR document missing with the
  manual steps named (`D11`). → unit (fake clients).
- **AC-F13.12** — **Given** a quarterly source (or the anchor filing) whose newest document is older than 120 days at
  `as_of`, **when** inputs are resolved, **then** it counts as MISSING, not found — a stale peer document is the
  look-alike of evidence (`P5`). → unit.
- **AC-F13.13** — ✏ *2026-10-21 (`DX-174`).* **Given** a Stage-A run in which some blocks answered and some failed,
  **when** it closes, **then** its trace says `PARTIAL` (none answered: `FAILED`; all: `SUCCESS`), never `SUCCESS`; and
  a `PARTIAL` run's answered blocks still load, each re-validated on its own call record (`D12`). → unit.
- **AC-F13.14** — ✏ *2026-10-21.* **Given** a step stopped by the subscription's usage limit, **when** the chain
  reports it, **then** it says so in words — *session limit, resets <time>* — and that nothing was lost and the same
  command resumes; a bare exception name is not a report (`P5`). → unit.
- **AC-F13.15** — ✏ *2026-10-21 (`D13`).* **Given** the chain manifests under `.state/thesis_for/`, **when** the daily run
  asks for the nominated ticker's thesis at `as_of`, **then** it gets the newest COMPLETED thesis with thesis `as_of` ≤
  the run's (`INV-1`), marked **stale** when more than 120 days older (`D9`) and **falsifier-fired** when its recorded
  check counted a FIRED falsifier; else **no peer set** (the ticker is not in `config/thesis_for.yaml`) or **not yet
  written** (it is, and no thesis exists — the command that writes one is named). → unit.
- **AC-F13.16** — **Given** a found thesis, **when** the daily `thesis_gate` runs, **then** it is §11.2's table over THAT
  thesis (`evaluate`), never the placeholder; **given** no peer set or none written, **then** the gate is `NO_THESIS`
  with that reason — never `PASS` (DN-10). → integration.
- **AC-F13.17** — **Given** a found thesis, **when** D-12 composes, **then** the recommendation carries a `thesis_ref`
  (run id, as of, verdict, conviction, its falsifiers, provenance `thesis_for`/transport) passed through VERBATIM — D-12
  derives nothing from it (DN-1) — and DN-39 is unchanged: a k=1 thesis has no stability figure, so the card stays
  informational. → unit.
- **AC-F13.18** — **Given** a `NO_THESIS` gate, **when** the card renders, **then** its verdict line reads *"no verdict —
  ranked #1 by … ; no thesis — no peer set"* (or *"— not yet written"*), its falsifier block and data gaps say why, and no
  composed HOLD is shown as if someone had judged it; **given** a found thesis, **then** the card shows the thesis's own
  verdict beside the composed one (RP-8), its falsifiers, and its source as `thesis_for` over the full bundle. → unit.
- **AC-F13.19** — ✏ *2026-10-21 (`DX-183`).* **Given** a Stages B–D plan, **when** its cost is printed before sending,
  **then** the ceiling prices every call as **two turns that both miss the cache** (the CLI's schema-repair turn,
  `DX-182`), each at the live transport's cache-write rate (`claude_code` 2.0× — its 1-hour cache, measured
  2026-10-21; API 1.25×) and its output cap; and the expected figure assumes the shared prefix is written once and
  read after (GW-30/31). ★ Known answer: over the measured calls of `run-2026-10-22T004557-mu-thesis`, the ceiling
  from each call's measured input is ≥ its notional cost, where the old formula's was not. → unit.
- **AC-F13.20** — ✏ *2026-10-22 (`D14`).* **Given** `--cache-evidence` (which `thesis_for` passes to every extraction and
  Stage-A step it sends), **when** a call is sent, **then** its evidence is the request's `cache_prefix` — the same bytes
  the call sent before, moved ahead of the instructions, byte-identical for every call over one bundle — and each call
  hands the transport ONE schema family for its runner (every E-block of `D8`; every Stage-A block of the run), keyed by
  block (GW-31). **Given** no flag, every runner sends exactly what it sent before (AC-F13.9). → unit + structural.
- **AC-F13.21** — ✏ *2026-10-22 (`D15`).* **Given** a subject whose own CIK is an EDGAR source on its industry's list,
  **when** inputs are resolved and the sector file is built, **then** that source is left out of both — not counted
  missing, not fetched — and the sector file records it as an `Omission` saying it is the subject itself (`RA-98`: the
  absence is declared); that subject's sector file is `<list>_<as_of>_<TICKER>.json`. **Given** a subject not on its
  list, nothing changes (MU on `memory_v1` keeps `memory_v1_<as_of>.json`, AC-F13.9). → unit.
- **AC-F13.22** — ✏ *2026-10-22 (`D15`).* **Given** a sector-file extraction (`E-13`) for a subject declared in
  `config/thesis_for.yaml`, **when** it runs, **then** the subject it declares (`DX-119`) is that config's name; a
  ticker declared nowhere is refused, never inferred. → unit.

## 7. Decisions

- **`D1` — one command chaining the existing steps; run ids as arguments** *(Victor, 2026-10-20)*. Supersedes `T1`
  (2026-10-06, keep the manual chain). Rejected: keep the manual chain (seven tools and a code edit per thesis).
- **`D2` — MU first** *(Victor, 2026-10-20)*; other industries wait on a peer set Victor chooses (`T2`).
- **`D3` — the card wording stays "REFUSED"** *(Victor, 2026-10-20)*; F12 `D15`, DN-41, RP-55 unchanged. Recorded here
  because it was asked with this spec; it binds there.
- **`D4` — subscription transport only** *(Victor's 2026-10-05 ruling, applied)* → `AC-F13.2`.
- **`D5` — first runs: a $0 replay of MU 2025-06-26 from its recorded runs, then MU as of today** *(Victor, 2026-10-20,
  was `Q1`)*. The replay carries every step from `config/thesis_for/MU_2025-06-26.json` and sends nothing (`AC-F13.8`).
- **`D6` — new filing fixtures are versioned in `tests_src/fixtures/filings/`** *(Victor, 2026-10-20, was `Q2`)*, each
  with a `.meta.txt` provenance sidecar (`DX-102`) and a row in `index.json`.
- **`D7` — a 10-K may anchor a thesis** *(Victor, 2026-10-20, was `Q3`)*; the form is recorded in the chain manifest and
  the first 10-K run is a new observation (all 32 blocks were verified on a 10-Q).
- **`D8` — the 8 E-blocks the thesis reads** *(Victor, 2026-10-20, was `Q4`)*: E-01 E-04 E-06 E-07 E-09 E-10 E-12 over
  the filing, E-13 over the sector file. `E-09` runs at `--effort low` (`DX-130`). E-03 E-05 E-08 E-11 E-15 later.
- **`D9` — staleness is absence** → `AC-F13.12`. 120 days covers one quarterly cadence and a reporting lag.
- **`D10` — consensus fixtures are dated sets**: a later fetch goes to `consensus/<as_of>/`, never over the set an
  earlier thesis read, so the replay's `bundle_hash` stays reproducible.
- **`D11` — company-IR documents are saved by hand**: they are not on EDGAR, and a scraper would choose what to keep —
  the selection `RA-98` forbids.
  ✏ *2026-10-20 (Victor): Claude may do the manual steps on request* — the 2Q26 SK hynix release and Samsung deck
  were saved that way, whole and verbatim (only the site's "AI Summary" removed, as for 1Q25), each date taken from the
  company's own dateline or notice. Still never automated in `--fetch-inputs`.

- **`D12` — a partial Stage-A run closes `PARTIAL`, and its answered blocks remain evidence** *(2026-10-21, Victor:
  "fix DX-174")*. The run status says what happened (`DX-26`: a trace that disagrees with its run is worse than none);
  the per-call checks (one error-free, untruncated, complete answer per block) are what make a block usable. Rejected:
  `FAILED` for any failure — it would discard eight good answers because a ninth hit a session limit.

- **`D13` — the daily card reads the nominee's thesis; "no thesis — no peer set" for the rest** *(Victor, 2026-10-21:
  "connect the thesis to the daily card (D-01 → D-12 → D-09) … show 'no thesis — no peer set' on the card for the
  rest")*. Was a non-goal of this spec (hand-over §4.1 step 3). ★ The daily run still WRITES no thesis (Victor
  2026-10-05, DX-153): it READS the newest one `thesis_for` wrote. The placeholder gate's own docstring named
  `NO_THESIS` as the honest status *once D-01 exists*; it does. ✗ Rejected — writing a thesis inside the daily run (the
  paid-API path stays off and theses stay on Victor's command); keeping the PASS stub (it says "not built", which is no
  longer true).

- **`D14` — evidence first in the extraction and Stage-A calls too** *(Victor, 2026-10-22: "as recommended")*. `DX-127`
  moved B–D's evidence ahead of the instructions so it could be cached; the same move for the 7 filing extractions (one
  bundle, `255a6a46…` on 2026-10-20) and the 9 Stage-A calls (one blind bundle, `a3c36d65…`) is what takes a thesis from
  ≈ $51 to ≈ $31 notional (L3, 2026-10-21). ★ The model reads the same text: evidence, then instructions (and, in Stage
  A, the rubric between them stays with the instructions). Opt-in by flag, so every recorded replay and golden case is
  untouched. ✗ Rejected: changing the runners' default (it would silently change what every old command sends).

- **`D15` — two more subjects: SNDK on `memory_v2`, MRNA on `vaccines_v1`** *(Victor, 2026-10-22: "go with SNDK on
  memory_v1, then [MRNA] as recommended"; then "memory_v2, skip subject" and "MRNA, EDGAR peers only")*. The two were
  nominated #3 and #1 on the 2026-10-20 card. `memory_v1` is Micron's list: it holds Sandisk and not Micron, so a
  Sandisk thesis on it would read its own 10-K as industry evidence. `memory_v2` = Micron · SK hynix · Samsung ·
  Sandisk, and a thesis leaves out its own subject's source by CIK (`AC-F13.21`); MU stays on `memory_v1`, so its
  replays are unchanged. `vaccines_v1` = Pfizer · Novavax, both on EDGAR. BioNTech, GSK and Sanofi report their quarters
  on 6-K, which `--fetch-inputs` does not fetch, so they wait for a version bump. ⚠ `E-13` reads *competitor capacity
  announcements*; in vaccines that is mostly not what a peer's filing reports, so a thin `E-13` there is expected, not a
  defect. ✗ Rejected: `memory_v1` as it is (the subject as its own peer, no Micron); one list per subject (an industry's
  list would fork with every new subject).

## 8. Open questions — Victor (✅ all answered 2026-10-20 → `D5`–`D8`; kept as asked)

- **`Q1` — the first live date.** *(a)* **MU as of today** — the latest periodic filing (MU's FY2026 10-K, if filed
  by then), ~25 subscription calls, and newer **SK hynix / Samsung** documents saved by hand with their `.meta.json`
  (they are company IR pages, not on EDGAR); *(b)* a replay of **2025-06-26** first, at $0 and no calls, to prove the
  wiring (`AC-F13.8`), then *(a)*. ★ Recommended: *(b)* then *(a)*.
- **`Q2` — where new filing fixtures live.** *(a)* versioned, beside today's (`tests_src/fixtures/filings/`) — a thesis
  then reproduces on any clone (`DX-12`'s lesson; the repo is private); *(b)* `.state/` — not versioned. Recommended *(a)*.
- **`Q3` — a 10-K as the anchor filing.** All 32 blocks were verified on a **10-Q**. A 10-K's layout differs (annual
  segment note, Item 7). Allowed, and its first run treated as a new observation? Or 10-Q-anchored only (the latest
  10-Q ≤ `as_of`)? Recommended: allow both; report the form in the chain manifest.
- **`Q4` — which E-blocks.** The thesis reads the 8 in `DEFAULT_EXTRACTIONS` (E-01 E-04 E-06 E-07 E-09 E-10 E-12 E-13).
  `E-03` `E-05` `E-08` `E-11` `E-15` are declared and run live but not read by the thesis. Recommended: the 8 now
  (reproduces the record); the others in a later amendment.

## 9. Traceability (spec → test → code)

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-F13.1 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_1_*` | `src/fundamental/on_demand/chain.py::run_chain` |
| AC-F13.2 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_2_*` | `chain.py::run_chain` · `tools/thesis_for.py` (prints the transport) |
| AC-F13.3 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_3_*` | `on_demand/inputs.py::resolve_inputs` · `chain.py` |
| AC-F13.4 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_4_*` | `on_demand/inputs.py` |
| AC-F13.5 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_5_*` | `on_demand/subjects.py::load_subject` · `config/thesis_for.yaml` |
| AC-F13.6 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_6_*` | `chain.py` · `on_demand/manifest.py` (CT-F13.1) |
| AC-F13.7 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_7_*` | `chain.py` · `manifest.py` |
| AC-F13.8 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_8_*` (the bundle check skips without `.state/`) | `chain.py::thesis_inputs` · `config/thesis_for/MU_2025-06-26.json` · `tools/run_thesis_once.py::base_for` |
| AC-F13.9 ✅ | `tests_src/test_thesis_for_characterization.py::test_ac_f13_9_*` (written first) · `tests_src/test_thesis_for.py::test_ac_f13_9_*` | `tools/run_extraction_once.py` (`add_filing_args`) · `run_judgement_once.py` · `run_thesis_once.py` (`parser`) |
| AC-F13.10 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_10_*` | `chain.py` · `tools/thesis_for.py::ToolRunners.checks` |
| AC-F13.11 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_11_*` · `tests_src/test_thesis_for_subjects.py::test_ac_f13_11_*` (`DX-186`) | `on_demand/fetch.py` · `EdgarClient.document` (DE-83) |
| AC-F13.12 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_12_*` | `on_demand/inputs.py` (`STALE_DAYS`) |
| AC-F13.13 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_13_*` | `tools/run_judgement_once.py::closing_status` · `tools/run_thesis_once.py::_recorded_call` |
| AC-F13.15 ✅ | `tests_src/test_thesis_on_card.py::test_ac_f13_15_*` | `src/fundamental/on_demand/lookup.py::thesis_for_card` |
| AC-F13.16 ✅ | `tests_src/test_thesis_on_card.py::test_ac_f13_16_*` | `src/orchestration/jobs/wiring.py::_thesis_gate` (OR-62) · `src/fundamental/thesis/gate.py::_by_dimension` (DX-178) |
| AC-F13.17 ✅ | `tests_src/test_thesis_on_card.py::test_ac_f13_17_*` | `src/decision/compose/service.py::compose` (`thesis_ref`, DN-42) |
| AC-F13.18 ✅ | `tests_src/test_thesis_on_card.py::test_ac_f13_18_*` | `src/reporting/render/card.py` (RP-56) |
| AC-F13.14 ✅ | `tests_src/test_thesis_for.py::test_ac_f13_14_*` | `on_demand/chain.py::describe_stop` · `tools/thesis_for.py::ToolRunners.stage_a_block_error` |
| AC-F13.20 ✅ | `tests/structural/test_evidence_first.py::test_ac_f13_20_*` | `tools/llm_transport.py::split_evidence` · `evidence_first` · `tools/run_extraction_once.py` · `tools/run_judgement_once.py` (`--cache-evidence`) · `on_demand/chain.py` |
| AC-F13.19 ✅ | `tests/structural/test_thesis_runner.py::test_ac_f13_19_*` | `tools/run_thesis_once.py::call_ceiling` · `plan_cost` |
| AC-F13.21 ✅ | `tests_src/test_thesis_for_subjects.py::test_ac_f13_21_*` | `on_demand/subjects.py::own_sources` · `tools/thesis_for.py` (`_context`, `ToolRunners`) · `config/sector/memory_v2.yaml` |
| AC-F13.22 ✅ | `tests_src/test_thesis_for_subjects.py::test_ac_f13_22_*` | `tools/run_extraction_once.py::subject_name` (read by `run_judgement_once` · `reverify_recording`) · `config/thesis_for.yaml` |

**As built (2026-10-20).** The $0 replay ran: `thesis_for MU --as-of 2025-06-26 --runs config/thesis_for/MU_2025-06-26.json`
carried all 8 extractions, 9 Stage-A blocks and the fourth thesis, re-verified them (base bundle `sha256:ed40721f…`), and
recorded the checks (falsifiers 2 FIRED · 2 PENDING; rule checks 0 violations over 3 calls). `--fetch-inputs` for
2026-10-20 wrote MU's FY2026 10-K (`0000723125-26-000023`, filed 2026-10-09 — the first 10-K anchor, `D7`), Sandisk's
FY2026 10-K, the MU facts, a price fixture and a consensus set; SK hynix and Samsung remain by hand (`D11`).
