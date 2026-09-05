"""WF-R5 alert emission — the B3 slice, which is a refusal (RK-29, RK-30, RK-36).

★ **The B3 "stub alert" is a real D-05 that correctly declines to run**, and
that is not a shortcut. `L3` **BS-11** says a stub is a real implementation of
the contract; the contract here (**RK-0**) takes a `CT-11.4 BookState` with
`reconciled: "ok"`, and **D-11's book is not built until a later milestone**.

```
Step 0 of WF-R1 is RECONCILED?, and it ABORTS.

A risk number computed on an unreconciled book is worse than no risk number
— it is a confident statement about a book that is not the book, and it
would be INDISTINGUISHABLE from a correct one on the card.
```

So B3 emits **no alerts and an `UNCHECKED` status**, D-12 transports the status
(**DN-38**), and D-09 renders it (**RP-47**). The seam is exercised end to end;
nothing is claimed.
"""

from __future__ import annotations

from datetime import date

from src.risk.contracts.alerts import COMPLETE, Alert, AlertSet, unchecked
from src.risk.errors import BlockAttemptedError, NoBookError, SuppressionAttemptedError

NO_BOOK_REASON = (
    "D-11's reconciled book does not exist yet (L3: the book lands with D-11, "
    "after B3), so WF-R1 aborts at step 0 and no exposure, drawdown or flag was "
    "computed — RK-29"
)


def daily_pass(*, as_of: date, book=None, why: str = "") -> AlertSet:
    """WF-R1 -> WF-R5. Returns the alert set **with its status** (DN-38).

    `book` is a `CT-11.4 BookState` or `None`. `None` is not an empty book — it
    is the absence of one, and the difference is the whole of RK-29.
    """
    if book is None:
        # ★ `why` lets the caller say WHICH absence this is. ⚠ Without it every
        #   unavailable book reported the B3 skeleton's reason, which stopped
        #   being true the moment D-11 landed — a stale reason is worse than a
        #   vague one, because it names a cause that has already been fixed.
        return AlertSet(alerts=(), status=unchecked(why or NO_BOOK_REASON))
    if getattr(book, "reconciled", None) != "ok":
        # ⚠ Refuses rather than falling back to the last good book. The fallback
        # produces a correct-looking report about YESTERDAY (RK-29).
        raise NoBookError(as_of, f"book state is {getattr(book, 'reconciled', '?')!r}")

    # The real WF-R1 ladder lands with the book. Reaching here in B3 means a book
    # arrived from somewhere it should not have.
    raise NotImplementedError(
        "WF-R1's exposure/metrics/flags ladder is not built in the B3 slice. It "
        "arrives with D-11's book — see the blueprint §9"
    )


def emit(alerts, *, complete: bool, reason: str = "") -> AlertSet:
    """Package an alert set, enforcing RK-30 at the one place alerts are published."""
    return AlertSet(tuple(alerts), COMPLETE if complete else unchecked(reason))


def refuse_to_block(caller: str) -> None:
    """RK-34 / AC-5.22 — the method that exists in order to raise.

    ⚠ A domain with no `block()` is silently satisfied by a caller who assumes
    one. One that raises names the rule at the moment someone reaches for it —
    the same reasoning as D-11's `revise()`.
    """
    raise BlockAttemptedError(caller)


def suppress(flag_id: str) -> None:
    """AC-5.17 / RK-18 — likewise. There is no suppression path, and saying so costs less
    than discovering its absence by assuming it exists."""
    raise SuppressionAttemptedError(
        f"suppression of flag {flag_id!r} was attempted. No component may suppress, "
        f"downgrade, filter or defer a flag — not D-09's renderer, not a config flag, "
        f"not a severity threshold that quietly drops the tail (INV-021, RK-18)"
    )
