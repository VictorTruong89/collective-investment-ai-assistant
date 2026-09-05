# MethodEntry — `volatility.realised_open_to_open_std.v1`

## Statement

```
sigma_hat(i, t) = sd( log( adj_open(i, s) / adj_open(i, s-1) ) )  for s in (t-20 .. t)
```

Sample standard deviation (`ddof=1`) of the last 21 daily open-to-open log
returns. **Daily** units — the caller annualises or scales to a horizon.

## Symbols

| Symbol | Meaning | Units |
|---|---|---|
| `adj_open(i, s)` | adjusted opening price, `CT-7.1.adj_open_minor` | minor units |
| `sigma_hat` | realised daily volatility | **dimensionless per day** (a log-return sd) |
| `21` | window, in trading sessions | sessions |

## Reference

The close-to-close realised-volatility estimator, e.g. Andersen & Bollerslev
(1998), *Answering the Skeptics*, International Economic Review 39(4).
⚠ **HOUSE VARIANT in one respect (QA-22): it is open-to-open, not close-to-close.**
That is deliberate — D-08 §5A decides at the open and QA-71 anchors the label
there, so the volatility of the quantity actually being predicted is the
open-to-open one. **Measured on 130 tickers × 371,840 rows the two sds differ by
a ratio of 1.0006** (D-03 §5.9.1c), so the substitution is empirically near-free.

## Assumptions

| Assumption | Does this system violate it? |
|---|---|
| Returns are iid within the window | ⚠ **Yes, mildly.** Volatility clusters; a 21-day sd lags a regime change by roughly half its window |
| 21 observations estimate an sd usefully | ⚠ Borderline. `SE(sd) ≈ sd/sqrt(2(n−1)) ≈ 16 %` at n=21. **Stated rather than hidden**: this is a noisy estimate and the ranking inherits that noise |
| No split inside the window | Holds only at a fixed `adj_as_of` (DE-28). A raw-series window across a split would show a fake −90 % day |

## Alternatives rejected

| Alternative | Why not |
|---|---|
| Yang-Zhang | ★ **The right answer, and it is QA-35's** — it uses the full OHLC and is far more efficient. Deferred to B4 because it needs `adj_high`/`adj_low`, which **CT-7.1 does not carry** (only `adj_open` and `adj_close`). Recorded so the deferral is visible rather than looking like a choice |
| EWMA / GARCH | A forecast, not a realised measure. **That is D-04's**, and B3 has no D-04 |
| Close-to-close | Wrong anchor for an open-anchored decision (see Reference) |

## Known-answer test

`tests_src/test_quant_b3.py::test_method_known_answer_vol_21`

A constant-growth series has identical log returns every day, so its sd is
**exactly 0.0** — and 0.0 here is a *measured* zero, not a missing one. With
fewer than 22 rows the value is `NaN`, never 0.0 (`min_periods`, PD-9).
