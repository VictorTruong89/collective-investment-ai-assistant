# MethodEntry — `momentum.open_to_open_ratio.v1`

> **CT-3.3.** One per `formula_id`. A `formula_id` referenced anywhere in `src/`
> with no MethodEntry **fails the build** (QA-20, AC-3.14).

## Statement

```
mom_21(i, t) = adj_open(i, t) / adj_open(i, t − 21) − 1
```

The simple 21-session price return of instrument `i`, measured open-to-open on
the split- and dividend-adjusted series at a stated `adj_as_of`.

## Symbols

| Symbol | Meaning | Units |
|---|---|---|
| `adj_open(i, t)` | adjusted opening price, `CT-7.1.adj_open_minor` | minor currency units (integer) |
| `21` | lookback in **trading sessions**, not calendar days | sessions |
| `mom_21` | the return | **dimensionless** — a same-currency ratio leaves the Money type (FE-32, MO-8) |

## Reference

Jegadeesh & Titman (1993), *Returns to Buying Winners and Selling Losers*,
Journal of Finance 48(1) — the cross-sectional momentum result. ⚠ Their formation
window is 3–12 months; **21 sessions is the short end and is chosen to match
HorizonSet v1's `h1m`, not to replicate their result.** Not a HOUSE VARIANT
(QA-22) — a plain price return is standard — but the *window* is ours.

## Assumptions

| Assumption | Does this system violate it? |
|---|---|
| Prices are comparable across `t` and `t−21` | ★ **Only at a fixed `adj_as_of`.** A split between the two dates rescales one end. DE-28 is what makes it hold; a panel built without `adj_as_of` violates it silently (§5C.7) |
| The opening print is settled at decision time | ⚠ **Enforced upstream, not here** — OR-32/OR-33 block the run on an unconfirmed open rather than substituting the previous close |
| Both ends share a currency | Checked, not assumed — the function raises (FE-32) |

## Alternatives rejected

| Alternative | Why not |
|---|---|
| `close(t)/close(t−21)` | ⚠ **Close-anchored, while the decision is taken at the open** (D-08 §5A). One full session of drift on every prediction, invisible in backtest because the backtest shares the anchor |
| `adj_close(t)/adj_open(t−21)` | Mixed anchors carry a systematic intraday drift the model will fit (QA-71's argument) |
| Log return | Equivalent for ranking (monotone), and the simple return is what `ranked_quantity`'s denormalisation expects (QA-58) |
| Volatility-scaled at source | That is the *ranker's* job (QA-58), not the feature's. Scaling here would put the same operation in two places (FE-4) |

## Known-answer test

`tests_src/test_feature_engineer_b3.py::test_method_known_answer_mom_21`

```
adj_open(t−21) = 10000  (minor units, $100.00)
adj_open(t)    = 11000  (minor units, $110.00)
mom_21         = 11000/10000 − 1 = 0.10   exactly
```

And the boundary: with fewer than 22 rows the value is `NaN`, **never 0.0** —
a name with insufficient history is unknown, not flat (FE-14, PD-1).
