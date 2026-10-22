# `cv.purge_embargo.derived.v1` — purge and embargo from the horizon set

## Statement

    purge_days   = max( trading_days ) over every horizon in the set
    embargo_days = configured, applied AFTER the test block only

Training rows within `purge_days` **on either side** of a test block are
removed; a further `embargo_days` is removed after it.

★ Both are counted in **trading days** — positions in the sorted date list —
because the horizons are defined in trading days. ✏ *Amended 2026-10-20 (F12
`D17`, `DX-161`):* the purge was a calendar-day `timedelta`, so 63 removed only
≈ 43 trading days; safe for the 21-day selection label, ~20 days short for a
63-day one.

## Symbols

`h_i` = each horizon's trading days · `purge` = the removed band ·
`embargo` = the additional forward band.

## Reference

López de Prado, *Advances in Financial Machine Learning*, ch. 7 (purging and
embargoing). `L1-quantitative-analysis.md` **QA-18** requires the derivation
rather than independent configuration.

## Assumptions

- ⚠ **The purge uses the LONGEST horizon in the set, not the one being
  evaluated.** A fold purged for 21 days while a 63-day label is in the set
  leaks 42 days of overlap into every boundary.
- Purging is applied on **both sides**. ★ A training row *after* the test block
  whose label window reaches back into it is exactly as leaky as one before —
  the overlap has no preferred direction, and purging only the past is the
  common half-implementation.
- The embargo is forward-only, because it models information propagation
  (serial correlation in features), not label overlap.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **Configuring purge independently** | QA-18: it will be wrong the first time someone changes the horizon set and forgets |
| **Purging only before the test block** | Halves the protection for no stated reason; the overlap is symmetric |
| **Calendar days (the v1 code until 2026-10-20)** | The horizon is in trading days; a calendar purge is ~30 % short (`DX-161`) |

## Known-answer test

HorizonSet v1 (`h1w 5`, `h1m 21`, `h1q 63`) ⇒ `purge_days = 63`, matching
`CT-3.1`'s declared value.
`tests_src/test_quant_evaluation.py::test_purge_is_derived_from_the_longest_horizon`
· the trading-day count: `tests_src/test_quant_walk_forward.py::test_ac_f12_38_the_k_fold_purge_before_the_block_is_in_trading_days`
