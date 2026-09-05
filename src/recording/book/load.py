"""D-11 — load the four BMO InvestorLine exports into `CT-11.4` book states.

★ This is the seam D-05 has been waiting on. `build_book` already refuses a
book with any unpriceable position (RC-10, FX-3), so this module's only job is
to hand it the exports and the prices and to **carry the refusal forward as a
reason** rather than as a crash.

⏸ **RC-58 — Victor, 2026-08-25.** Canadian listings and CDRs are not valued
until the rest of the code is complete, and the FMP plan covers US listings
only (measured 2026-08-26: `MDA.TO` → 402, `MRV.NE` → 402, `NVDA` → 200).
⚠ Every one of the four accounts holds at least one such position, so **today
this loader always returns `(), <reason>`** — and that reason is what keeps
D-05's pass `UNCHECKED` and D-12's card informational, honestly and by name.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from src.recording.book.from_activity import build_book
from src.recording.errors import RecordingError
from src.recording.orders.group import group_orders
from src.recording.reconcile.ingest import parse_export

#: The four registered accounts (RC-25) and their statement types.
ACCOUNTS = (("RESP_1", "RESP"), ("RRSP_1", "RRSP"),
            ("TFSA_1", "TFSA"), ("TFSA_2", "TFSA"))

EXPORT_DIR = "sdd/design/rel6_design/samples/bmo_investorline_transactions"


def export_path(root, account_id: str) -> Path:
    return Path(root) / f"TransactionHistory_{account_id}.csv"


def load_books(*, as_of: date, prices=None, fetch=None, reported_nav=None,
               sectors=None, root: str = EXPORT_DIR) -> tuple[tuple, str]:
    """Return `(books, unavailable_reason)`. ★ **Never a partial tuple.**

    ⚠ *A book-wide aggregate computed over the accounts that happened to price
    is not a partial answer, it is a wrong one* — so one unpriceable account
    withholds all four (RK-5's aggregation rule, one level up). The reason names
    the instruments, because a refusal that cannot say what it lacks is the
    defect RC-10 exists to prevent.
    """
    prices = dict(prices or {})
    if fetch is not None:
        # ★ **D-11 decides WHAT to price; the caller only knows HOW.** ⚠ The
        #   inversion matters: orchestration asking the book what it holds would
        #   put holdings knowledge in the shim (OR-2), and pricing only the
        #   trading universe made `DELL` — an ordinary US common stock — report
        #   as unpriceable beside `MDA.TO`, which is a different fact entirely.
        prices.update(quote_holdings(fetch, root=root))

    books, refusals = [], []
    for account_id, account_type in ACCOUNTS:
        path = export_path(root, account_id)
        if not path.exists():
            refusals.append(f"{account_id}: no export at {path}")
            continue
        activities = parse_export(path, account_id=account_id)
        orders = group_orders(activities)
        try:
            state, _status = build_book(
                account_id=account_id, as_of=as_of, activities=activities,
                orders=orders, prices=prices, account_type=account_type,
                reported_nav=(reported_nav or {}).get(account_id),
                sectors=sectors)
        except RecordingError as exc:
            refusals.append(str(exc))
            continue
        books.append(state)

    if refusals:
        return (), (
            "; ".join(refusals) + " — ⏸ RC-58: Canadian listings and CDRs are "
            "not valued yet (FMP covers US listings only, .TO/.NE are 402). "
            "★ One unpriceable account withholds all four, because a book-wide "
            "figure computed over the rest would be wrong, not partial")
    return tuple(books), ""


def held_instruments(*, root: str = EXPORT_DIR) -> tuple[str, ...]:
    """Every instrument_id with a non-zero position, across all four accounts.

    ★ **The book is priced from what it HOLDS, not from the trading universe.**
    ⚠ Relying on the overlap made `DELL` — an ordinary US common stock — report
    as unpriceable beside `MDA.TO`, which is a genuinely different fact. A
    reason that conflates *"we did not fetch it"* with *"the plan will not sell
    it to us"* sends the reader to the wrong fix (DE-49, RC-10).
    """
    held: set[str] = set()
    for account_id, _type in ACCOUNTS:
        path = export_path(root, account_id)
        if not path.exists():
            continue
        activities = parse_export(path, account_id=account_id)
        from src.recording.book.from_activity import derive_quantities

        quantities = derive_quantities(activities, group_orders(activities))
        held.update(i for i, q in quantities.items() if q)
    return tuple(sorted(held))


def quote_holdings(fetch, *, root: str = EXPORT_DIR) -> dict:
    """`{instrument_id: (price, currency)}` for the US common stock held.

    ⏸ **RC-58 — CDRs and CAD listings are deliberately not attempted.** They are
    a declared pause, and firing a request per name would turn it into a string
    of 402s that reads like a fault (DE-49).
    """
    prices = {}
    for instrument_id in held_instruments(root=root):
        symbol, wrapper, venue_currency = instrument_id.split("|")
        if wrapper != "COMMON" or venue_currency != "USD":
            continue
        quote = fetch(symbol)
        if quote is not None:
            prices[instrument_id] = quote
    return prices
