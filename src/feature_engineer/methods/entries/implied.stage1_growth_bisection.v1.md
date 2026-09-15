# `implied.stage1_growth_bisection.v1` — the stage-1 growth the price requires

## Statement

Find `g₁` such that `value_per_share(g₁) = price`, holding every other
assumption fixed, by bisection over the declared bracket `[low, high]` for a fixed
number of iterations (`F10` `D7`):

    f(g) = value_per_share(g) − price
    if sign f(low) = sign f(high): NO_ROOT_IN_BRACKET  (value = null)
    else: halve the bracket `iterations` times; g₁ = midpoint

## Symbols

| Symbol | Meaning |
|---|---|
| `price` | the raw close on the last trading day ≤ `as_of` |
| `[low, high]` | the declared growth bracket (`D4`: −20 % to +40 %) |
| `iterations` | fixed count (`D4`: 60) — so the answer is deterministic |

## Reference

Reverse DCF / expectations investing (Rappaport & Mauboussin, *Expectations
Investing*): read what the price implies rather than asserting a growth rate.
Bisection is the standard bracketed root-finder (Press et al., *Numerical Recipes*,
§9.1).

## Assumptions

- `value_per_share` is monotone in `g₁` across the bracket. ⚠ **Yes, violated if
  the basis is negative** — growth then lowers value; bisection still finds a root
  when the bracket ends straddle the price, because it tests signs, not direction.
- ⚠ A price the bracket cannot reach returns `NO_ROOT_IN_BRACKET` and a null value —
  never the bracket end, which would read as a real, extreme expectation.
- Value per share is an integer number of minor units, so the residual at the
  solution is within about one minor unit, not zero.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| **Newton's method** | Needs a derivative of a rounded, piecewise function, and can diverge — non-determinism in iteration count |
| **Solve for implied terminal growth** | Hides the question in the least knowable number |
| **Solve for an implied cash-flow level** | Harder for a reader to judge than a growth rate |

## Known-answer test

Valuing at the solved growth reproduces the price within one minor unit per share;
a price of $10¹⁰ per share returns `NO_ROOT_IN_BRACKET`.
`tests/unit/test_valuation_f10.py::test_ac_f10_10_implied_growth_round_trips_to_the_price`
