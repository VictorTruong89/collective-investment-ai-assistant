# `stop_distance_vol_v1` — the volatility-scaled stop

Code: src/portfolio/sizing/stop_distance.py @ sha256:4eb25feee76a29cb
*(QA-25 / F12 AC-F12.22 — pinned 2026-10-05 as the baseline; re-pin only after re-reading this entry against the changed code.)*

## Statement

    stop_distance = k · σ̂ · √h · entry      ⇒      shares ∝ 1 / σ̂

## Symbols

| Symbol | Meaning |
|---|---|
| `k` | how many forecast standard deviations the stop sits away — **configuration, stated on every answer** (PS-6) |
| `σ̂` | the volatility forecast (D-04); **realised vol as a labelled stand-in until it exists** (PS-23) |
| `h` | holding horizon in days — 21, HorizonSet v1 |

## Reference

Standard volatility-scaled position sizing. `L1-quantitative-analysis.md` §9.5
argues the **volatility** forecast, not the return forecast, is the most
decision-relevant ML output this system could produce.

## Assumptions

- Returns scale as `√h` — ⚠ true under i.i.d. increments, and **false around a
  scheduled event**, which is exactly when a stop matters most.
- ⚠ **Realised volatility understates exactly when it matters** — before an
  earnings gap — which is why PS-23 forbids calling it a forecast.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **An eyeballed stop** | *A stop picked by eye is an unstated volatility assumption* — and, through `entry/d`, an unstated **position-size** decision |
| **A fixed percentage stop** | Same width on a 15 %-vol name and a 60 %-vol one: it is a volatility bet nobody chose |

## Known-answer test

`entry = 100`, `σ̂ = 0.02/day`, `h = 21`, `k = 1.5` ⇒
`d = 1.5 × 0.02 × √21 × 100 = 13.7477…`; at `risk_capital = 2000` ⇒ **145.4786 shares**.
`tests_src/test_portfolio_b5.py::test_ac_6_5_every_answer_states_sigma_its_source_and_its_class`
