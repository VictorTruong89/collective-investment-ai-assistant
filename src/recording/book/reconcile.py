"""D-11 §8 — RC-10, the one check the whole book rests on.

★ `sum(positions) + cash == NAV` **per currency, per account, every day**
(INV-025). ⚠ **A break raises; it is never absorbed** — and D-05 refuses to
compute on the result either way (RK-29), because *a risk number computed on an
unreconciled book is a confident statement about a book that is not the book.*
"""

from __future__ import annotations

from datetime import date

from src.recording.book.models import (
    BREAK, OK, RECONCILE_TOLERANCE, BookState, Break, Position,
)


def compute_breaks(positions, cash_by_currency, nav_by_currency, *,
                   account_id: str, tolerance: float = RECONCILE_TOLERANCE):
    """RC-10 — one `Break` per currency that does not balance.

    ⚠ **Every currency present in ANY of the three inputs is checked.** A
    currency holding positions but absent from `nav_by_currency` is a break, not
    a currency to skip — the tempting `for ccy in nav_by_currency` loop would
    silently pass a book missing a whole leg.
    """
    currencies = (set(cash_by_currency) | set(nav_by_currency)
                  | {p.currency for p in positions})
    found = []
    for currency in sorted(currencies):
        held = sum(p.market_value for p in positions if p.currency == currency)
        computed = held + float(cash_by_currency.get(currency, 0.0))
        reported = float(nav_by_currency.get(currency, 0.0))
        if abs(computed - reported) > tolerance:
            found.append(Break(account_id=account_id, currency=currency,
                               computed=computed, reported=reported))
    return tuple(found)


def build_book(*, account_id: str, as_of: date, positions, cash_by_currency,
               nav_by_currency, account_type: str = "TFSA",
               base_currency: str = "CAD", fx_rate_used=None,
               capital_base: float | None = None,
               tolerance: float = RECONCILE_TOLERANCE) -> BookState:
    """Derive the book and reconcile it (RC-9, RC-10).

    ★ The returned state carries `reconciled` and its breaks; it does **not**
    raise. RC-10's *"a break raises"* is enforced at the point of USE —
    `assert_reconciled` — because a break must be *recordable* to be reported,
    and a constructor that refuses to build one leaves nothing to look at.
    """
    positions = tuple(positions)
    breaks = compute_breaks(positions, cash_by_currency, nav_by_currency,
                            account_id=account_id, tolerance=tolerance)
    fx = dict(fx_rate_used or {})
    nav_base = _nav_base(nav_by_currency, fx, base_currency)
    return BookState(
        account_id=account_id, date=as_of, positions=positions,
        cash_by_currency=dict(cash_by_currency),
        nav_by_currency=dict(nav_by_currency), base_currency=base_currency,
        nav_base=nav_base, fx_rate_used=fx,
        capital_base=capital_base if capital_base is not None else nav_base,
        reconciled=BREAK if breaks else OK, breaks=breaks,
        account_type=account_type)


def _nav_base(nav_by_currency, fx_rate_used, base_currency: str):
    """FX-3 — ⚠ **`nav_base` is `null` when no rate is available, never a guess.**

    ★ A single missing rate makes the whole aggregate unavailable: a partial sum
    across currencies is not a smaller NAV, it is a wrong one.
    """
    total = 0.0
    for currency, amount in nav_by_currency.items():
        if currency == base_currency:
            total += float(amount)
            continue
        rate = fx_rate_used.get(currency)
        if rate is None:
            return None
        total += float(amount) * float(rate)
    return total


def assert_reconciled(book: BookState) -> BookState:
    """RC-10 / RK-0 — ★ **a `BookState` in `break` is not a risk input.**"""
    from src.recording.errors import BookBreakError

    if book.reconciled != OK:
        raise BookBreakError(book.account_id, book.date, book.breaks)
    return book


def capital_base(book: BookState) -> float:
    """RC-19 — ★ **read from the book, never configured, never hard-coded.**

    ⚠ *Every percentage cost figure in this repository is a function of a number
    that is currently the literal `20000.0` at `backtester.py:107`.*
    """
    from src.recording.errors import BookBreakError, CapitalBaseUnavailableError

    assert_reconciled(book)
    if book.capital_base is None:
        raise CapitalBaseUnavailableError(book.account_id, book.date)
    return book.capital_base
