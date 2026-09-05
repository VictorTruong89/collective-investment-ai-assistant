# MethodEntry — `rank.denormalised_within_ticker_z.v1`

> ⚠ **B3 only.** B4 replaces `z_hat` with a fitted model's cross-sectional
> standardised prediction. The *denormalisation* survives that change; the
> standardisation does not.

## Statement

```
z_hat(i, t)           = ( s(i,t) − mean_21(s(i,·)) ) / sd_21(s(i,·))     within ticker i
ranked_quantity(i, t) = z_hat(i, t) * sigma_hat(i, t) * sqrt(h)
```

with `s = mom_21`, `sigma_hat = vol_21` (daily), `h = 21` sessions.

## Symbols

| Symbol | Meaning | Units |
|---|---|---|
| `s(i,t)` | the signal, `mom_21` | dimensionless return |
| `z_hat` | trailing within-ticker standardisation of `s` | dimensionless (sd units) |
| `sigma_hat` | `vol_21`, realised daily volatility | per day |
| `sqrt(h)` | square-root-of-time scaling to the 21-session horizon | sqrt(sessions) |
| `ranked_quantity` | ★ an **expected 21-session return**, in return units | dimensionless |

## Reference

The denormalisation is **D-03 QA-58**: rank on `z_hat * sigma_hat * sqrt(h)`, not
on `z_hat`. ★ **HOUSE VARIANT (QA-22)** in its standardisation: the literature
and QA-58 both intend a **cross-sectional** `z_hat`; this uses a **time-series**
one, because at `n = 1` the cross-sectional sd is undefined. Square-root-of-time
scaling is standard under iid returns (Hull, *Options, Futures and Other
Derivatives*, ch. 15).

## Assumptions

| Assumption | Does this system violate it? |
|---|---|
| `sqrt(h)` scaling — returns are iid | ⚠ **Yes, mildly.** Momentum is by definition autocorrelated, so `sqrt(h)` understates a trending name's horizon vol |
| A time-series `z` substitutes for a cross-sectional one | ⚠ **They are different quantities.** Cross-sectional `z` asks *"rich relative to peers today"*; this asks *"rich relative to its own recent history"*. **At n = 1 they coincide trivially — there is nobody to compare to** |
| 21 observations estimate a mean and an sd | Same noise as `vol_21`: `SE(sd) ≈ 16 %` |

## Alternatives rejected

| Alternative | Why not |
|---|---|
| Rank on `z_hat` alone | ⚠ **The defect QA-58 exists to remove** — a systematic tilt toward low-volatility names, because `z` divides out exactly the quantity the position will be sized against |
| Rank on the raw signal | Not comparable across names once `n > 1`; would have to be replaced at B4 rather than extended |
| `fillna(0)` for short-history names | ★ **PD-1.** A z-score of 0.0 says *"exactly average"*; a name with missing data is **unknown**, and filling it lets a data-poor name compete for the slot |
| Cross-sectional `z` with a fallback at n=1 | An implicit branch that changes the meaning of the output without changing its name. The variant is in the `formula_id` instead, so it reaches the hash and the record |

## Known-answer test

`tests_src/test_quant_b3.py::test_method_known_answer_ranked_quantity`

```
z_hat = 2.0, sigma_hat = 0.02/day, h = 21
ranked_quantity = 2.0 * 0.02 * sqrt(21) = 0.183303...
```

And the ordering property: with two candidates of equal `z`, **the
higher-volatility name ranks first** — which is the tilt QA-58 restores and the
observable difference from ranking on `z`.
