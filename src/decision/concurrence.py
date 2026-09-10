"""`PG-7.3` at its enforcement point — D-12 composition (`F6a` `AC-6a.10`, `D3`).

⚠⚠ **A combined verdict may never claim two independent views agree when one
seat configured the other.** `PG-7`'s rationale: choosing a model horizon *is*
an analytical choice, so conditioning B's configuration on A's output means
their agreement is partly an **echo** of a decision we made, not evidence about
the world.

★★ **Why here and not in `src/evaluation/`.** `F6a` `D3` names **composition**
as the enforcement point — *"if the claim is never built, no renderer can emit
it"* — and `ST-2`/`AC-5.12` forbid any module outside `src/evaluation/**` from
importing the harness. So the rule lives with the code that constructs the
claim, and the harness imports **this**, never the reverse.

★ `D3` also keeps a second check at rendering (D-09): a single guard at
composition is correct and would still let a *report template* phrase
concurrence into existence.
"""

from __future__ import annotations

from collections.abc import Sequence


class IndependenceClaimError(Exception):
    """`AC-6a.10` — a claim of independent agreement that is not true.

    ⚠ Raised at composition, so the claim is never built. Guarding only the
    renderer would leave a true-looking `agreement=True` in the decision record
    for `F5`, `F7b` and every future consumer to read.
    """


def assert_may_claim_independent_agreement(*, influenced_by: Sequence[str]) -> None:
    """Refuse to BUILD a false independence claim (`PG-7.3`).

    ⚠⚠ The rule is not *"add a caveat"* — it is that the claim **may never be
    made**. ★ The firewall's whole value is that concurrence between
    *independent* views is informative; cross-configuration silently converts
    that concurrence into an echo.
    """
    configured = [s for s in influenced_by if s]
    if configured:
        raise IndependenceClaimError(
            "cannot claim two INDEPENDENT views agree: "
            f"{', '.join(sorted(set(configured)))} configured another seat "
            "(PG-7.3, AC-6a.10). ★ The concurrence is partly an echo of our own "
            "configuration choice, so it is not evidence of agreement."
        )


def concurrence_label(influenced_by: Sequence[str]) -> str:
    """The word a reader actually takes away — `"independent"` or
    `"cross-configured"`.

    ★★ `PG-10`'s shape, and `F2` `D3`'s: **a claim carries its subject's status,
    in the field itself.** `D3` renamed `IDENTICAL` → `REPRODUCED` because
    *"the name is what gets copied"* — a caveat that does not travel beside the
    value it qualifies is decoration.
    """
    return "cross-configured" if any(influenced_by) else "independent"
