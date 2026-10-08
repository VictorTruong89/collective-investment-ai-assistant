# `cv.walk_forward.expanding.v1` — expanding-window walk-forward folds

## Statement

    dates sorted, cut into n_folds contiguous blocks B_0 … B_{n-1} (the same blocks as cv.purge_embargo.derived.v1)
    for k = 1 … n-1:
        test_k  = B_k
        train_k = every date at position < first_position(B_k) − purge_days
    B_0 is never tested; a block whose train_k is empty is dropped

## Symbols

`n_folds` = number of blocks · `purge_days` = `cv.purge_embargo.derived.v1`'s purge, counted in **trading days**
(positions in the date list) · `B_k` = the k-th test block.

## Reference

López de Prado, *Advances in Financial Machine Learning* (Wiley, 2018), ch. 7 and ch. 11–12 (walk-forward as the
historical simulation of a strategy, and its single-path limitation). F12 `D11` (`DX-162`) records why it is
measured here beside the purged k-fold.

## Assumptions

- ⚠ **One historical path.** Each test block is scored by exactly one model, trained on everything before it;
  the estimate has fewer test dates than the k-fold (block 0 is lost) and so a wider standard error.
- ★ **Trading-day purge.** The horizon is defined in trading days; a calendar-day purge of 63 is ~43 trading
  days, too short for a 63-trading-day label (`DX-161`, open for the k-fold).
- No embargo is needed: nothing after a test block is ever trained on.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **Rolling (fixed-length) window** | Discards early history the expanding window keeps; a choice of window length is one more tuned parameter |
| **Replacing the purged k-fold** | The k-fold uses every block and is the record so far; `D11` measures both |

## Known-answer test

500 business days, 5 folds, purge 63 ⇒ folds 1–4 only; every training date precedes every test date; the gap
between the last training date and the first test date is exactly 64 positions.
`tests_src/test_quant_walk_forward.py::test_ac_f12_33_the_purge_is_in_trading_days_not_calendar_days`
