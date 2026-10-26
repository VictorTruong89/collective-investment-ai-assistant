# F14 — Position sizing on demand (`size_for TICKER --account ACCT --entry P [--stop S]`)

> **Spec-ID:** F14 · **Status:** 🟢 **approved 2026-10-25** (Victor: *"approve as drafted"*; `D7`–`D10` confirmed, `Q1` → `D11`) · ✅ **19/19 ACs green 2026-10-25** (✏ AC-F14.19 added 2026-10-25, `D12` — `DX-191` fixed) · **Drafted:** 2026-10-25
> **Source discussion:** `_TEMP_handover_2026-10-25.md` part 2 · `sdd/design/rel1_design/L9-go-live-checklist.md` §7.4
> option ⓑ · Victor's rulings 2026-10-25 (this session; `D2`–`D6`).
> ✏ **Supersedes `L9` §7 ⓐ** (Victor 2026-10-06, *"leave D-06 a library for rel-1"*) — `D1`.
> **Home:** D-06 `src/portfolio/` · seat 5, Portfolio Strategy (this repo's nine-seat model, vision §3; ✏ corrected 2026-10-25 from "seat 4", which is Risk).
> **Governs:** `constitution.md` — `P5` fail loud · `AP-5` / `PG-3` deterministic (*"position sizing from a stop"* is
> PG-3's own example of what is NOT an agent's job) · `PG-2` · `PG-10`. Design-tier sources, cited by id and never
> re-worded: `L1-portfolio-strategy.md` (`PS-2…PS-10`, `PS-19…PS-30`, `PS-33…PS-36`, `PS-41`, `PS-43`, `CT-6.1`,
> `AC-6.18…6.21`), `L1-recording.md` (`RC-4`, `RC-70…RC-78`).

---

## 1. Goal & why

D-06 is a tested library that nothing calls (`L9` §7.1): risk-based sizing given a stop, the volatility stop, the
factor-decomposed risk budget, the 15 % cap — 32 green tests, no entry point. It could not have one, because it had
**no capital base**: every account held a CAD/CDR line FMP cannot price (`R1`, `RC-58`). D-11's holdings export
(`RC-70…RC-78`, built 2026-10-25) now supplies BMO's own reported balance for `RESP_1` and `TFSA_2`. F14 is the
command that sizes one trade in one account against that balance — **a consequence of stated inputs, never a
proposal** (`PS-8`) — and labels every input with where it came from and how old it is.

★ **Nothing about the sizing rule is new.** `shares = risk_capital / (entry − stop)` (`PS-2`), the volatility stop
(`PS-6`), the factor budget (`PS-33`), the cap (`PS-10`) are the library's. F14 is the composition, its inputs and
its refusals.

## 2. Scope / non-goals

**In scope:**
- One command: `python tools/size_for.py TICKER --account ACCT --entry P [--stop S] [--currency CAD|USD]
  [--held-stop SYM=PRICE …] [--sigma X] [--dry-run] [--json]`.
- Accounts with a holdings export (`RESP_1`, `TFSA_2` today). Any other account is **refused by name** (`RC-77`).
- The answer (`CT-F14.1`): whole shares; which constraint binds — risk, cash or the 15 % cap — with all three numbers
  (`PS-28`, `PS-10`); committed / remaining risk for the account (`PS-30`); the factor-decomposed budget (`PS-33`);
  every input with its source and as-of date; the consequences (weight in the account, thresholds as reports); a
  pyramid flag when the ticker is already held (`PS-15`).

**Non-goals (this spec):**
- ⊘ **The daily run** — `L9` `P1`: nothing is actionable while `R1` stands, so there is nothing for the run to size.
- ⊘ **The D-12 seam** (`PS-37…PS-41`): F14 reads no recommendation, no grade, no scorecard. It sizes what Victor names.
- ⊘ **Any target allocation, recommended book or drift from target** (`PS-12`).
- ⊘ **A measured risk-budget factor.** `E`, `C`, `P`, `D` ship `unmeasured` (`D3`); each needs a MethodEntry first
  (`PS-36`).
- ⊘ **Book-wide sizing or exposure** while `TFSA_1` / `RRSP_1` have no holdings export — stated `UNCHECKED` (`AC-F14.11`).
- ⊘ **Any write.** No journal, no artifact, no cache (`PS-26`, `AC-6.21`).
- ⊘ **Any LLM** (`PS-25`, `AC-6.20`). $0 API; FMP for realised volatility is standing-approved.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | Victor, by hand | `TICKER`, `--account`, `--entry`, optional `--stop` | `tools/size_for.py` (composition root, `CA-9`) |
| T2 | Victor, by hand — the free preview | the same, `--dry-run` | the same; **no network** — the inputs resolved and what is missing |

## 4. Behaviour & reuse (the lean "how")

```text
size_for TICKER --account A --entry P [--stop S]
  1  CAPITAL      load_holdings(A)  → balance (CAD), cash, positions, footer rate, as-of      RC-70…RC-77
                  ✗ no Holdings_A.csv → refused by name; never a derived or stated capital
  2  POLICY       config/portfolio_policy.yaml[A] → r_total, r_ceiling, target_positions      PS-43, D6
                  ✗ no entry / a missing key → refused by name; no default exists
  3  BUDGET       risk_budget(r_ceiling) — E, C, P, D all 1.0, `unmeasured`                   PS-33, PS-34, D3
  4  COMMITTED    Σ max(0, avg_cost − held_stop) × qty over the holdings                       PS-29, D4
                  every holding stated → measured · any missing → `unmeasured`, names them
  5  σ            realised 21-session sd of daily log returns, FMP, US listing only            PS-23, D8
                  or --sigma (stated) · ✗ CAD listing / CDR with no --sigma → σ unavailable
  6  STOP         --stop S → implied k (needs σ; else `unavailable`)                           PS-7
                  no --stop → entry − k·σ·√21·entry, k = 1.5 `default (QS-2 open)`             PS-6, D5
                  ✗ no stop and no σ → refused (PS-5)
  7  FX           entry in USD for a CAD capital base → the holdings footer rate, labelled       PS-4, FX-3
  8  SIZE         risk_capital = min(capital·r_ceiling·∏factors,
                                     (capital·r_total − committed) / n_reserve  if measured)    PS-27, D4
                  notional_risk = risk_capital / d · entry
                  notional_cash = the account's reported cash (CAD, at the footer rate)          PS-28, D9
                  notional_cap  = capital · 15 %                                                PS-10
                  deploy = min(the three) → whole shares, floored                               D7
  9  REPORT       CT-F14.1, every input with source + as-of; book-wide UNCHECKED; RESP stated
```

- **Reuse.** `load_holdings` / `HoldingsStatement.to_book_state` (D-11 §8a); `risk_budget`, `n_reserve`,
  `committed_risk`, `_consequences` (`src/portfolio/sizing/risk_based.py`); `implied_k`, `stop_distance`, `DEFAULT_K`
  (`sizing/stop_distance.py`); `MAX_POSITION_PCT`, `Factor`, `RiskBudget`, `SizingAnswer` (`contracts/sizing.py`);
  `pyramid_check` (`pyramid/scale.py`); FMP daily prices (`src/data_engine/src/fmp/prices.py`).
- ✏ *(2026-10-25, `D12`: superseded — both now call `sizing/trade.py::size_trade`.)* ⚠ **Not reused: `size_for_stop`.** It derives the account allowance from the per-trade rate (no `r_total`), and when
  cash binds it reports `binds: cash` **without reducing the shares** to the cash — the `PS-28` table's *"Deploy
  $40,000"* row is not what it returns. Recorded as `DX-191` (`D7`); the library function and its 32 tests are left
  as they are. F14 composes the same primitives into the §5.1b arithmetic as written.

## 5. Contracts (inline)

**CT-F14.1 — the sizing answer** (printed; `--json` prints the object; never written):
```json
{
  "ticker": "DELL", "account_id": "TFSA_2", "as_of": "2026-10-25",
  "inputs": {                                         // every one: value · source · as_of
    "capital_base":     {"value": 76805.55, "currency": "CAD", "source": "holdings_export", "as_of": "2026-10-25"},
    "cash_available":   {"value": 105.24, "currency": "CAD", "source": "holdings_export", "as_of": "2026-10-25"},
    "entry":            {"value": 450.0, "currency": "USD", "source": "stated"},
    "stop":             {"value": 410.0, "currency": "USD", "source": "stated | volatility_stop"},
    "sigma":            {"value": 0.021, "source": "realised · FMP · 21 sessions to 2026-10-23 | stated | unavailable"},
    "k":                {"value": 1.5, "source": "default (QS-2 open) | implied by the stated stop"},
    "fx_usd_cad":       {"value": 1.3999, "source": "holdings_export", "as_of": "2026-10-25"},
    "r_total":          {"value": "<policy>", "source": "config/portfolio_policy.yaml"},
    "r_ceiling":        {"value": "<policy>", "source": "config/portfolio_policy.yaml"},
    "target_positions": {"value": "<policy>", "source": "config/portfolio_policy.yaml"},
    "held_stops":       {"value": {"ENB": 60.0}, "source": "stated", "missing": ["ARM", "…"]}
  },
  "risk_budget_factors": {"r_ceiling": "…", "E_edge": {"status": "unmeasured"}, "…": "…", "effective": "…"},
  "account_risk": {"allowance": "…", "committed": "… | null", "committed_status": "measured | unmeasured",
                   "remaining": "… | null", "n_reserve": 3, "currency": "CAD"},
  "risk_capital": {"value": "…", "binds": "r_ceiling | risk_remaining / n_reserve"},
  "notional": {"risk": "…", "cash": "…", "cap_15pct": "…", "currency": "USD"},
  "binding_constraint": "risk | cash | cap_15pct",
  "shares": 3, "shares_exact": 3.7, "deploy_notional": "…",
  "consequences": {"weight_account_pct": "…", "weight_fund_pct": "… | excluded (RC-4)"},
  "thresholds_crossed": [{"name": "…", "effect": "reported_only"}],
  "pyramid": null,
  "book_wide": "UNCHECKED — no holdings export for RRSP_1, TFSA_1 (RC-77)",
  "unavailable": ["implied_k: σ unavailable for a CAD listing"],
  "statement": "a consequence of the stated inputs, not a recommendation (PS-8)"
}
```
Rules: every money value carries its currency (`PS-4`); `committed` and `remaining` are `null` — never 0 — when any held
stop is missing (`PS-34`'s shape); `binding_constraint` is exactly one of three; `unavailable` names every input that
was not there (`PS-24`).

**CT-F14.2 — `config/portfolio_policy.yaml`** (Victor's; no value ships with the code):
```yaml
accounts:
  TFSA_2: {r_total: <fraction>, r_ceiling: <fraction>, target_positions: <int>}
```
Rules: `0 < r_ceiling ≤ r_total ≤ 1`; `target_positions ≥ 1`. A missing account, key, or out-of-range value **raises
naming it** (`PS-43`).

## 6. Acceptance criteria (Given / When / Then → test tier)

- **AC-F14.1** *(capital is reported)* — **Given** an account with a holdings export, **when** sized, **then**
  `capital_base` is its reported balance, labelled `holdings_export` with the file's as-of date; **and given** an
  account with none, **then** the command refuses naming it and prints no size — no derived, older or stated capital.
  → *unit.* (`PS-3`, `PS-41`, `RC-77`, `D2`)
- **AC-F14.2** *(policy, no defaults)* — **Given** the policy file lacks the account, a key, or a value is out of range,
  **then** it raises naming what is missing; **and** the values used are reported with their source. → *unit.*
  (`PS-43`, `D6`)
- **AC-F14.3** *(budget = ceiling, visibly)* — every answer shows all four factors `unmeasured` at 1.0 and
  `effective == r_ceiling`, and says so in words. → *unit.* (`PS-33`, `PS-34`, `D3`)
- **AC-F14.4** *(committed risk)* — **Given** a held stop for every holding, **then** `committed = Σ max(0, avg_cost −
  stop) × qty` from the reported average cost, and a stop above average cost commits 0 (`PS-29`); **given** any
  holding without one, **then** `committed` and `remaining` are `null`, `committed_status = unmeasured`, the missing
  holdings are named, and only `r_ceiling` binds — stated. A `--held-stop` for a symbol not held raises. → *unit.* (`D4`)
- **AC-F14.5** *(the per-trade risk)* — `risk_capital = min(capital·r_ceiling·∏factors, remaining / n_reserve)` when
  committed is measured, naming which term bound; `n_reserve = target_positions − held lines`, and `n_reserve ≤ 0`
  refuses (`PS-27`, `PS-43`). → *unit, known answer.*
- **AC-F14.6** *(which constraint binds)* — `deploy = min(notional_risk, notional_cash, notional_cap)`; shares are
  whole, floored; `binding_constraint` names the minimum and all three notionals are reported. Three known answers:
  one where each binds. → *unit.* (`PS-28`, `PS-10`, `D7`)
- **AC-F14.7** *(the stop)* — a stated stop yields the implied `k` (`PS-7`), or `implied_k: unavailable` when σ is; no
  stop → the volatility stop at `k = 1.5` labelled `default (QS-2 open)`; no stop **and** no σ → refused; a stop at or
  above entry → refused. → *unit.* (`PS-5`, `PS-6`, `D5`)
- **AC-F14.8** *(σ, labelled)* — for a US listing σ is the realised 21-session sd of daily log closes from FMP, labelled
  `realised` with its window end (`PS-23`); a CAD listing or a CDR is **never fetched by its bare ticker** (`RC-53`) —
  σ is `unavailable` unless `--sigma` is given, then labelled `stated`; fewer than 22 closes → `unavailable`, never a
  shorter window. → *unit (fake fetch).* (`D8`)
- **AC-F14.9** *(currency)* — a USD entry against a CAD capital base converts at the holdings footer rate, labelled;
  an account file with no footer rate makes a USD sizing **unavailable** (`FX-3`, `PS-4`). → *unit.*
- **AC-F14.10** *(cash)* — `cash_available` is the account's reported total cash in CAD, converted to the entry
  currency at the footer rate, labelled `holdings_export`; the answer states that it assumes BMO's auto-FX. → *unit.*
  (`D9`)
- **AC-F14.11** *(per account; book-wide stated — `AC-6.18`)* — the answer is per account; its `book_wide` field says
  `UNCHECKED` and names every discovered account without a holdings export (`RC-77`, `RK-5`); no book-wide figure is
  computed over a subset. → *unit.* (`PS-19`)
- **AC-F14.12** *(RESP stated — `AC-6.19`)* — sizing `RESP_1` answers per account and states on the answer that the
  RESP is excluded from the fund (`weight_fund_pct: excluded (RC-4)`). → *unit.* (`PS-20`, `D10`)
- **AC-F14.13** *(no LLM, no D-01 — `AC-6.20`)* — `src/portfolio/**` and `tools/size_for.py` import no LLM gateway
  (`src.shared.llm`), no `src.fundamental`, no `anthropic`. → *invariant (import graph).* (`PS-25`, `ST-5`)
- **AC-F14.14** *(writes nothing — `AC-6.21`)* — a full run and a `--dry-run` create, modify or delete no file under
  the repo or `.state/`. → *integration (hermetic).* (`PS-26`)
- **AC-F14.15** *(every input labelled)* — every key of `inputs` carries a `source`; every holdings-derived input
  carries `as_of`; the printed answer shows the holdings' age in days. → *data contract.* (`RC-74`)
- **AC-F14.16** *(held ticker — M-3)* — sizing a ticker the account already holds reports the pyramid check from the
  reported average cost (flag, never block) and counts no new slot. → *unit.* (`PS-15`, `PS-16`)
- **AC-F14.17** *(dry run)* — `--dry-run` makes no network call, prints the resolved inputs and names each missing
  one, and exits 0 when sizing could proceed, 1 when an input would refuse. → *integration (hermetic).*
- **AC-F14.18** *(real files)* — on Victor's `.state/` files (**skipped when absent**), a `--dry-run` for `TFSA_2`
  reports capital 76,805.55 CAD as of 2026-10-25 and footer rate 1.3999, and `TFSA_1` is refused by name. → *reality
  probe.*
- **AC-F14.19** *(one sizing path — `DX-191`, `D12`)* — `size_for_stop` and `size_on_demand` both compute through one pure function, `size_trade`; on the same inputs they return the same whole shares, the same binding constraint and the same risk capital. Known answers from the design's own tables: **PS-28** (risk capital 4,000, entry 90, d = 6, cash 40,000 → **cash binds, 444 shares**, risk notional 60,000 still reported; d = 18 → **risk binds, 222 shares**) and **§5.1b** (capital 100,000, `r_ceiling` 1 %, `r_total` 6 %, `n_reserve` 4: nothing committed → **1,000, `r_ceiling` binds**; 3,000 committed → **750, `risk_remaining / n_reserve` binds**). When the 15 % cap binds, the uncapped risk notional is still reported beside it. → *unit, known answer.* (`PS-27`, `PS-28`, `PS-10`)

## 7. Decisions (resolved questions — kept with their rejected options)

- **D1 — ⓑ supersedes ⓐ** (Victor, 2026-10-25, the hand-over this spec answers). `L9` §7.4 ⓐ *"leave D-06 a library for
  rel-1"* (2026-10-06) is superseded by ⓑ, an on-demand tool. ⓒ (the daily run) stays rejected while `R1` stands.
- **D2 — capital from the holdings export** (Victor, 2026-10-25). `PS-3` holds unamended. *Rejected:* a capital stated
  per run, labelled `stated` — it would amend `PS-3` and reintroduce an un-checkable number.
- **D3 — budget = `r_ceiling × E × C × P × D` with all four `unmeasured`** (Victor, 2026-10-25). The answer reads
  *"budget = ceiling, because E, C, P, D are not measured yet"*. *Rejected now:* shipping a factor — `D` needs NAV
  history (several holdings exports apart), `P` needs D-05 on a valued book, `C` needs k ≥ 3 theses, `E` is unproven
  (`PS-35`); each needs a MethodEntry (`PS-36`).
- **D4 — held stops optional per run, else `unmeasured`** (Victor, 2026-10-25). BMO exports no open orders, so
  `PS-29`'s committed risk has no source. *Rejected:* assuming a volatility stop per holding (invents a stop Victor
  did not set); never measuring (wastes a stop he can state).
- **D5 — `k = 1.5`, labelled `default (QS-2 open)`** (Victor, 2026-10-25). *Rejected:* `--k` required with no default.
  The implied `k` of a stated stop is always shown (`PS-7`).
- **D6 — policy in `config/portfolio_policy.yaml`, per account** (Victor, 2026-10-25). Victor gave no values on
  2026-10-25: the file ships **with no account in it**, so every sizing refuses by name until he fills it in
  (`PS-43`). *Rejected:* required command-line flags each run.
- **D7 — compose the §5.1b arithmetic; do not call `size_for_stop`; whole shares, floored.** `DX-191`: `size_for_stop`
  has no `r_total` and does not reduce shares when cash binds. Floored, because BMO fills whole shares and flooring
  keeps the risk at or under the budget. *(Proposed by Claude; ✅ confirmed by Victor 2026-10-25.)*
- **D8 — σ: realised 21 sessions, US listings only; anything else `unavailable` unless stated.** `RC-53`: a bare TSX
  ticker returns the NYSE listing in USD. *(✅ confirmed by Victor 2026-10-25; `Q1` → `D11`.)*
- **D9 — cash = the account's total reported cash in CAD**, converted at the footer rate, with BMO's auto-FX stated as
  the assumption. *Rejected:* cash in the entry currency only — TFSA_2 holds USD 19.92, which would make cash bind
  on every US trade for a reason that is a conversion, not a constraint. *(✅ confirmed by Victor 2026-10-25.)*
- **D11 — a CDR's σ is NOT taken from its US underlying** (Victor, 2026-10-25, was `Q1`). A CDR or TSX name needs
  `--sigma`, labelled `stated`; otherwise σ is `unavailable`. *Rejected:* the underlying's realised σ labelled
  `realised · US underlying` — defensible under `RC-52`'s hedged-return argument, but it substitutes another
  instrument's behaviour for the CDR's own (`RC-58`: *"a CDR is a separate stock"*).
- **D12 — `DX-191` resolved by ONE sizing path** (Victor, 2026-10-25: *"fix DX-191 with option B"*). The §5.1b arithmetic moves into a pure `size_trade` (`src/portfolio/sizing/trade.py`) that reads no file; `size_for_stop` becomes a thin wrapper over it (gaining optional `r_total` and `open_positions`), and F14's `size_on_demand` calls the same function. *Rejected:* (A) fixing `size_for_stop` in place — two correct implementations of one formula drift, which is how `DX-191` arose; (C) leaving it documented — the obviously named function is what a future daily run (`L9` ⓒ) would wire. ⚠ Behaviour change in the library, deliberate: shares are now whole (floored, as `D7`); with no `r_total` stated only `r_ceiling` binds (the ceiling is no longer divided by `n_reserve`); when cash binds the shares ARE reduced.
- **D10 — the RESP is sized when asked by name**, and its exclusion from the fund is stated on the answer (`RC-4`,
  `PS-20`). *(✅ confirmed by Victor 2026-10-25.)*

## 8. Open questions (must resolve before/at implementation)

- **Q2 — the policy values** for `RESP_1` and `TFSA_2` (`r_total`, `r_ceiling`, `target_positions`). Blocks every real
  answer (`D6`), not the build.

## 9. Traceability (spec → test → code)

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-F14.1 | `tests_src/test_portfolio_size_for.py::test_ac_f14_1_capital_is_the_reported_balance_with_its_date` · `::test_ac_f14_1_an_account_with_no_holdings_export_is_refused_by_name` | `src/portfolio/on_demand/size_for.py`, `tools/size_for.py` |
| AC-F14.2 | `tests_src/test_portfolio_size_for.py::test_ac_f14_2_a_missing_or_out_of_range_policy_raises_naming_it` (×4) · `::test_ac_f14_2_the_policy_used_is_reported_with_its_source` · `::test_ac_f14_2_the_shipped_policy_file_holds_no_invented_values` | `src/portfolio/on_demand/size_for.py`, `config/portfolio_policy.yaml` |
| AC-F14.3 | `tests_src/test_portfolio_size_for.py::test_ac_f14_3_every_factor_is_unmeasured_and_the_budget_equals_the_ceiling` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.4 | `tests_src/test_portfolio_size_for.py::test_ac_f14_4_committed_risk_from_stated_held_stops` · `::test_ac_f14_4_a_missing_held_stop_makes_committed_unmeasured_and_named` · `::test_ac_f14_4_a_stop_for_a_symbol_not_held_raises` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.5 | `tests_src/test_portfolio_size_for.py::test_ac_f14_5_the_reserve_term_binds_when_it_is_smaller` · `::test_ac_f14_5_the_ceiling_binds_when_it_is_smaller` · `::test_ac_f14_5_a_full_account_refuses` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.6 | `tests_src/test_portfolio_size_for.py::test_ac_f14_6_risk_binds` · `::test_ac_f14_6_cash_binds` · `::test_ac_f14_6_the_15pct_cap_binds` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.7 | `tests_src/test_portfolio_size_for.py::test_ac_f14_7_a_stated_stop_reports_its_implied_k` · `::…_with_no_sigma_has_k_unavailable` · `::test_ac_f14_7_no_stop_uses_the_volatility_stop_at_the_default_k` · `::test_ac_f14_7_no_stop_and_no_sigma_refuses` · `::test_ac_f14_7_a_stop_at_or_above_entry_refuses` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.8 | `tests_src/test_portfolio_size_for.py::test_ac_f14_8_realised_sigma_is_the_21_session_sd_of_log_closes` · `::test_ac_f14_8_too_few_closes_is_unavailable_never_a_shorter_window` · `::test_ac_f14_8_a_cad_listing_is_never_fetched_by_its_bare_ticker` | `src/portfolio/on_demand/size_for.py`, `tools/size_for.py` |
| AC-F14.9 | `tests_src/test_portfolio_size_for.py::test_ac_f14_9_a_usd_entry_converts_at_the_footer_rate` · `::test_ac_f14_9_no_footer_rate_makes_a_usd_sizing_unavailable` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.10 | `tests_src/test_portfolio_size_for.py::test_ac_f14_10_cash_is_the_reported_total_and_states_auto_fx` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.11 | `tests_src/test_portfolio_size_for.py::test_ac_f14_11_book_wide_is_unchecked_and_names_the_accounts_without_an_export` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.12 | `tests_src/test_portfolio_size_for.py::test_ac_f14_12_the_resp_is_sized_and_its_exclusion_is_stated` | `src/portfolio/on_demand/size_for.py` |
| AC-F14.13 | `tests_src/test_portfolio_size_for.py::test_ac_f14_13_portfolio_and_the_tool_import_no_llm_and_no_d01` | `src/portfolio/`, `tools/size_for.py` |
| AC-F14.14 | `tests_src/test_portfolio_size_for.py::test_ac_f14_14_a_full_run_and_a_dry_run_write_nothing` | `tools/size_for.py` |
| AC-F14.15 | `tests_src/test_portfolio_size_for.py::test_ac_f14_15_every_input_carries_a_source_and_holdings_inputs_an_as_of` (×4) | `src/portfolio/on_demand/size_for.py` |
| AC-F14.16 | `tests_src/test_portfolio_size_for.py::test_ac_f14_16_a_held_ticker_reports_the_pyramid_check_and_takes_no_new_slot` | `src/portfolio/on_demand/size_for.py`, `src/portfolio/pyramid/scale.py` |
| AC-F14.17 | `tests_src/test_portfolio_size_for.py::test_ac_f14_17_the_dry_run_names_what_is_missing_and_exits_1` | `tools/size_for.py` |
| AC-F14.18 | `tests_src/test_portfolio_size_for_real.py::test_ac_f14_18_tfsa_2_reads_the_reported_capital_and_rate` · `::test_ac_f14_18_tfsa_1_is_refused_by_name` | `tools/size_for.py` |
| AC-F14.19 | `tests_src/test_portfolio_size_trade.py::test_ac_f14_19_ps28_tight_stop_cash_binds_and_the_shares_are_reduced` · `::test_ac_f14_19_ps28_wide_stop_risk_binds` · `::test_ac_f14_19_5_1b_nothing_committed_the_ceiling_binds` · `::test_ac_f14_19_5_1b_committed_risk_makes_the_reserve_term_bind` · `::test_ac_f14_19_with_committed_unmeasured_only_the_ceiling_binds` · `::test_ac_f14_19_the_uncapped_risk_notional_survives_the_cap` · `::test_ac_f14_19_size_for_stop_and_size_on_demand_agree` (×3) | `src/portfolio/sizing/trade.py`, `src/portfolio/sizing/risk_based.py`, `src/portfolio/on_demand/size_for.py` |
