# L9 — Go-live checklist (`MS-0`, L3 §2.1p row 10)

> **SDD role: `design/` tier — NON-AUTHORITATIVE.** A preparation list, not a plan of record.
> **Status:** DRAFT · **Opened:** 2026-10-05 · **Source:** `_TEMP_handover_2026-10-05.md` Task 3, L3 §2.1s.
> ⚠ **Every step below is Victor's.** Nothing here was spent, switched or enabled while writing it. Costs are
> list-price estimates from measured traces (`tools/spend_report.py`, fixed 2026-10-05), priced at
> `claude-opus-5` $5 / $25 per million input / output tokens.

## 0. Where it stands (measured 2026-10-05)

| | |
|---|---|
| API spend to date | **$72.41 over 105 calls**, none since 2026-09-17. 89 later calls ran on the subscription ($99.36 notional, **not** spend). ⚠ Until today the report counted those as spend ($137.18) — fixed, with a test |
| Daily run | ⛔ **not scheduled.** The only user timer is `snapshot-analyst-estimates` (weekdays 18:30 NY). `Linger=no`, so user timers run only while Victor is logged in |
| Ranker | ⛔ **no promoted model** (`.state/models` absent) → the card ranks on the deterministic rule `z(mom_21)·vol_21·√21`, informational (`PG-10`, DN-39). Last fit: walk-forward IC 0.0203, *t* = 1.42 — refused |
| Thesis in the daily graph | ⚠⚠ **NOT the thesis that was built** — see G1 |
| Commission | **$0** since 2026-10-05 (F12 `D8`) |

## 1. ⚠⚠ G1 — the daily graph authors the OLD thesis

`src/orchestration/jobs/graph.py` → `thesis` job → `src.fundamental.thesis.author_for` → `run.author_once`:
**three calls** — `J-11@v1`, `J-15@v1`, `J-16@v1` — with `scorecard={}` and confidence `UNMEASURED`. No Stage A
extraction, no J-01…J-10, no F10 valuation, no F11 base rates, no consensus, and the falsifier prompt is `v1`,
not the `J-15 v3` the fourth MU thesis needed. The **32-block `CT-9.2` thesis** built and verified since
September runs **only** through `tools/run_thesis_once.py`, over hand-built MU fixtures (filings, sector file,
consensus). `entrypoint.py`'s `THESIS_ASSEMBLER_MISSING` comment is itself stale (`bundle_for` exists).

| option | what it means | effort | cost |
|---|---|---|---|
| ⓐ wire the 32-block runner into the daily graph | generalise `run_thesis_once` past MU: EDGAR filing fetch + conversion per ticker, a sector file per industry (today: memory only), consensus from the snapshot | ⚠ several sessions; needs a spec amendment (D-01 / F9) | per thesis, §3 |
| ⓑ go live quant-only; thesis on demand | the card stays informational; Victor runs `run_thesis_once` by hand for a name he is considering | none | per run, §3 |
| ⓒ go live with the old 3-call path | cheapest, but it is not the analysis the project measured, and its falsifiers predate DX-139/144/147 | none | ~3 calls/name |

★ Recommendation: **ⓑ now, ⓐ as the next build** — ⓒ would put an unmeasured analysis on a card.

## 2. The steps

| # | step | what Victor decides / does | cost | depends on |
|---|---|---|---|---|
| 1 | **G1** | ⓐ / ⓑ / ⓒ above | — | — |
| 2 | **API spot-check of signed golden cases** (CLAUDE.md house rule) | approve a sample, per call. All 53 cases come from **15 distinct recorded calls**; re-running all 15 ≈ **$8.60**. Proposed sample: 5 calls covering 31 cases — E-01 MU (11 cases), E-01 AMD (9), E-02 MU (9), J-01, J-05 ≈ **$3.10** | $3–9 | — |
| 3 | **Budget `QI-2`** (`L2-shared-infrastructure`, GW-20) | a number and a period. ⚠ D-01 §7.4a's *$624/yr at `k_cov=3`* predates the 32-block thesis and no longer holds — see §3 | — | 1, 5 |
| 4 | **Transport switch** | set `CIA_LLM_TRANSPORT=anthropic_api` **for the daily run only**, with `ANTHROPIC_API_KEY` in its environment; dev stays on the subscription. Every runner prints the live transport | per §3 | 2, 3 |
| 5 | **Thesis cadence** | which names, how often, which `k`. The cost driver by far (§3) | — | 1 |
| 6 | **Daily timer** | a thin systemd user timer at 10:00 America/New_York (OR-30, OR-40); and `loginctl enable-linger` if it must run while logged out (also fixes the snapshot timer) | $0 | 1 |
| 7 | **Delivery** | SMTP credentials in the environment for `--deliver` (RP-50); a failed send fails the run (OR-50) | $0 | 6 |
| 8 | **Sector file v2** | switch `DEFAULT_SECTOR` to `memory_v1_2025-06-26_e15_v2.json` (Victor 2026-10-05: *at go-live*). Re-hashes every downstream bundle | $0 | 1ⓐ/ⓑ |
| 9 | **`E-14` news + a news snapshot** | FMP news is standing-approved but only **~92 days deep** — a snapshot like `snapshots/analyst-estimates/` must run for months before `E-14` has history. ★ Starting the snapshot now costs nothing and cannot be backfilled later | $0 (FMP) | — |
| 10 | **`J-18` event briefs** | needs the event workflow designed first (deferred by Victor) | spec first | — |
| 11 | **Model retrain under F12** | `D6` (drift weights) and `D8` ($0 fee) change every backtest, so the last refusal no longer describes the current simulator. A retrain + gate run is local CPU (no API). `cost_survival` can no longer fail on commission; `ic_significance` still decides | $0 | — |
| 12 | **Retire `../ai-investment-pipeline`** (`MS-8.9`) | archive read-only, **do not delete**; `MS-8.1` (clean tree + tag) is still unmet. Repo stays private | $0 | — |
| 13 | **`DX-152`** | D-11's merged-order detection loses its fee evidence at $0 — ⓐ date-switch · ⓑ accept and state · ⓒ measure the first free export | $0 | — |
| 14 | **Open findings** | `DX-57 60 61 78 79 87 89–92 134`, partial `DX-44 71 80` — none blocks go-live by itself; review which must close first | — | — |

## 3. What a daily run would cost (estimates, stated assumptions)

Measured per-call inputs: an extraction over one 10-Q ≈ 76 k in / 2–12 k out ≈ **$0.42–0.69**; a Stage B–D
judgement over the full bundle ≈ 240–490 k in ≈ **$1.29–2.71** uncached. Whole theses: **$16.93** (first MU, 4 runs)
and an estimated **$11.38** with prompt caching (DX-127, never validated live).

| scenario (per year, ~252 trading days) | assumption | ≈ cost |
|---|---|---|
| quant-only card (G1 ⓑ) | no LLM call | **$0** |
| on-demand theses | 2 per month × k=1 × $11–17 | **$260–410** |
| per-filing re-author, top-3 | 3 names × 4 filings × k=3 × $11–17, plus ~1 new name/month × k=3 | **$800–1,200** |
| ⚠ daily re-author, top-3 | 3 × k=3 × $11 every trading day | **~$25,000** — not a real option |

★ The cadence (step 5) moves the bill by two orders of magnitude; the transport switch (step 4) only decides
whether it is paid at all.

## 4. What is free and could start before go-live

Steps 6 (timer), 9 (news snapshot), 11 (retrain), 12 (archive) and 13 (DX-152) spend nothing. ⚠ Step 9 is the
only one with a clock on it: every day without a snapshot is a day of news history `E-14` will never have.
