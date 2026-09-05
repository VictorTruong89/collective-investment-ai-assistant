# Release 6 — Close-out

> **PLACEHOLDER — Release 6 is still OPEN.** Created 2026-08-08 during the `notebooks/` → `sdd/`
> restructure so the close-out slot exists and the convention is visible. Fill it in from
> `_template_closeout.md` when rel6 actually closes; until then this file records nothing binding.
>
> **SDD role: `design/` tier — NON-AUTHORITATIVE.**
> **Status:** ⬜ NOT CLOSED · **Opened:** 2026-06-28 (constitution adopted, rel6 S5)

---

## What shipped (interim — refresh at close)

| Spec | Feature | ACs green / total | Code |
|---|---|---|---|
| F0 | Code map | 9 / 9 | *(descriptive — `tests/test_code_map.py`)* |
| F1 | Disciplinary Trading Report | 11 / 14 | `pipeline/report/` |
| F2 | Portfolio context, journal & delivery | 8 / 8 | `pipeline/discipline/`, `pipeline/delivery/` |
| F3 | SDD adoption | 7 / 7 | *(process — `tests/test_sdd_process.py`)* |
| F4 | Portfolio & market data plane | 8 / 8 | `pipeline/portfolio/` |

**Test suite:** 810 passing (2026-08-08).

## Known open at time of writing

- **F1 AC-1.1 / AC-1.2** — the API surface and the 409 prompt-alignment surface. Not built.
- **F1 AC-1.8** — T3 live pricing; re-scoped to a characterization test after rel6 Q1 resolved to spot.
- **P2 characterization tests** — freezing `OhlcvFeatureEngineer` output and the online-API contract.
  Called "the highest-leverage next step" since rel6 S6 (2026-07-11); still outstanding.
- **INV-1…4 have no owning spec** — see `../../specs/vision.md` §4, "Known structural gap".

## To fill in at close

Sections from `_template_closeout.md`: *What did not ship and where it went* · *Decisions promoted out of
the brainstorm* · *What we learned* · the close-out checklist.
