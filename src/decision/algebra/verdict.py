"""★ The verdict algebra — a bounded meet-semilattice (§5, DN-5…DN-9).

```
        c(BUY) = 0   <   c(HOLD) = 1   <   c(SELL) = 2
                    increasingly conservative  --->

        v* = meet_i(v_i) = argmax_i c(v_i)      the LEAST aggressive input wins
```

★ **Why a meet, and the decisive argument is statistical, not order-theoretic.**

```
THE MEET IS A ZERO-PARAMETER COMBINATION RULE.

It estimates nothing. No weight, no covariance, no threshold — so nothing in
it can be fitted to noise. At n ~ 60 decisions/year that is not a safety
compromise. It is the OUT-OF-SAMPLE OPTIMUM.
```

This is the **forecast combination puzzle** (Smith & Wallis 2009; Claeskens et
al. 2016): once weights must be *estimated*, the combination acquires a bias
even with unbiased components and its variance exceeds the fixed-weight case —
so the penalty for fitting is **active harm, not merely no gain**. Its twin is
DeMiguel, Garlappi & Uppal (2009): naive `1/N` beats mean-variance out of sample.

```
P3 IS NOT ENFORCED HERE. IT IS IMPLIED.

    v* = meet_i(v_i)   ==>   v* <= v_j   for every j

The meet is a lower bound BY DEFINITION, so the composition cannot be more
aggressive than any input. There is no branch to forget, no assertion to
omit, no code path where an upgrade is expressible.
```
"""

from __future__ import annotations

BUY, HOLD, SELL = "BUY", "HOLD", "SELL"

#: The conservatism index. A chain, so `V` is totally ordered and the meet is
#: simply the maximum index.
CONSERVATISM = {BUY: 0, HOLD: 1, SELL: 2}

#: Identity (top) and absorbing (bottom) elements of the bounded semilattice.
IDENTITY, ABSORBING = BUY, SELL

#: Gate severities — also a chain (§5.3).
PASS, FLAG, VETO = "PASS", "FLAG", "VETO"
SEVERITY = {PASS: 0, FLAG: 1, VETO: 2}


def conservatism(verdict: str) -> int:
    try:
        return CONSERVATISM[verdict]
    except KeyError:
        raise ValueError(
            f"{verdict!r} is not a verdict. V = {sorted(CONSERVATISM)} — and it is "
            f"deliberately small: |V| = 3 makes every law exhaustively testable "
            f"(DN-6)"
        ) from None


def meet(*verdicts: str) -> str:
    """★ `v* = the least aggressive input`. The ONLY place composition happens (DN-5).

    ⚠ **The empty meet is the identity, and calling it is almost always the
    DN-10 bug.** `meet()` with no arguments returns BUY — mathematically correct
    for a bounded semilattice, and in this system it means every gate went
    missing. So it raises instead: §5.5's rule is that the identity must not be
    reachable by omission, and an empty argument list is the purest form of
    omission there is.
    """
    if not verdicts:
        raise ValueError(
            "meet() with no verdicts would return the identity (BUY), which is "
            "exactly the ungated recommendation §5.5 forbids. A run with no gate "
            "inputs is a failure, not a pass (DN-10)"
        )
    return max(verdicts, key=conservatism)


def apply_gate(verdict: str, status: str) -> str:
    """`phi(v, s)` — the monotone map from a gate status to a verdict (§5.3, DN-7).

    ```
        phi(v, PASS) = v                   identity
        phi(v, FLAG) = v                   ★ verdict unchanged — DN-8
        phi(v, VETO) = v meet HOLD         refuse to act; do not instruct
    ```

    ★ **`VETO` maps to HOLD, never to SELL** (DN-9). A veto is *"do not act on
    this"*, not *"take the opposite side"* — mapping a vetoed BUY to SELL would
    have the discipline layer originating a trade instruction, which is DN-1's
    exact prohibition.

    ⚠ **DN-8: FLAG does not move the verdict, and must therefore change the
    ARTIFACT.** A severity level that alters nothing anywhere trains the reader
    to skip it, which is worse than not having it. FLAG's obligation is to D-09.
    """
    conservatism(verdict)                 # validates
    if status not in SEVERITY:
        raise ValueError(
            f"{status!r} is not a gate status. S = {sorted(SEVERITY)}; anything else "
            f"is an unmapped state, and D-01 RA-49 makes that a defect rather than a "
            f"default to PASS"
        )
    if status == VETO:
        return meet(verdict, HOLD)
    return verdict


def is_no_more_aggressive_than(composed: str, other: str) -> bool:
    """P3, as a predicate. `composed ⊑ other` iff it is at least as conservative."""
    return conservatism(composed) >= conservatism(other)
