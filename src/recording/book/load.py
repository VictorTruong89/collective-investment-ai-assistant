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

import os
import re
from datetime import date
from pathlib import Path

from src.recording.book.from_activity import build_book
from src.recording.errors import RecordingError
from src.recording.orders.group import group_orders
from src.recording.reconcile.ingest import parse_export

#: ★ RC-66 — the exports live OUTSIDE the spec tier.
#:
#: ⚠ This previously pointed at `sdd/design/rel6_design/samples/`: the **book of
#: record** sat inside the tier that governs the code, in a **release-scoped,
#: frozen** design directory, under a name that says *fixture*. `.state/` is
#: already git-ignored, so real broker statements cannot enter history (DX-5).
EXPORT_DIR = ".state/broker/bmo_investorline"

#: ⚠ Read only if `EXPORT_DIR` is absent, so an unmigrated checkout degrades to
#: WORKING rather than to an empty book.
LEGACY_EXPORT_DIR = "sdd/design/rel6_design/samples/bmo_investorline_transactions"

#: `H-5` — *registered status is not a field; the naming convention carries it.*
_EXPORT_RE = re.compile(r"^TransactionHistory_(?P<account>[A-Z]+_\d+)\.csv$")


def export_path(root, account_id: str) -> Path:
    return Path(root) / f"TransactionHistory_{account_id}.csv"


def discover_accounts(root) -> tuple[tuple[str, str], ...]:
    """★★ RC-65 — the account set comes from the DIRECTORY, never from a list.

    ⚠ `ACCOUNTS` used to be a hardcoded 4-tuple. A fifth statement dropped into
    the directory was **silently ignored**: not read, not refused, not
    mentioned — the new portfolio simply did not exist, while `RK-5`'s
    all-or-nothing aggregation still returned a book that looked healthy.
    ★ `RRSP_2` (planned 2027) is now a file drop, not a code edit.

    `H-5` already established that the filename carries the account, and the
    registered TYPE is its prefix — so the directory is a sufficient source and a
    second list in code could only disagree with it.

    ⚠ Raises on an empty directory (`AC-11.48`): *"no accounts found"* and
    *"this book holds nothing"* are different facts, and deriving the second from
    the first would read as a healthy refusal rather than a missing input.
    """
    path = Path(root)
    found = []
    if path.is_dir():
        for entry in sorted(path.iterdir()):
            m = _EXPORT_RE.match(entry.name)
            if m:
                account_id = m.group("account")
                found.append((account_id, account_id.rsplit("_", 1)[0]))
    if not found:
        raise RecordingError(
            f"no broker exports found in {path} — expected files named "
            "`TransactionHistory_<ACCOUNT>.csv` (RC-65, AC-11.48). ⚠ An empty "
            "book is not the same answer as a missing input.")
    return tuple(found)                       # sorted → INV-2 determinism


def resolve_export_dir(root: str | None = None) -> str:
    """`RC-66` — `$BMO_STATEMENTS_DIR`, then `.state/`, then the legacy path."""
    if root is not None:
        return root
    override = os.environ.get("BMO_STATEMENTS_DIR")
    if override:
        return override
    if Path(EXPORT_DIR).is_dir():
        return EXPORT_DIR
    return LEGACY_EXPORT_DIR if Path(LEGACY_EXPORT_DIR).is_dir() else EXPORT_DIR


def load_books(*, as_of: date, prices=None, fetch=None, reported_nav=None,
               sectors=None, root: str | None = None) -> tuple[tuple, str]:
    """Return `(books, unavailable_reason)`. ★ **Never a partial tuple.**

    ⚠ *A book-wide aggregate computed over the accounts that happened to price
    is not a partial answer, it is a wrong one* — so one unpriceable account
    withholds all four (RK-5's aggregation rule, one level up). The reason names
    the instruments, because a refusal that cannot say what it lacks is the
    defect RC-10 exists to prevent.
    """
    root = resolve_export_dir(root)
    # ⚠⚠ RC-65 vs RC-10, and BOTH are right — they belong at different layers.
    # `discover_accounts` RAISES: at that level "no accounts" is an error, and
    # returning () would let an empty book look derived (AC-11.48).
    # `load_books` must NOT crash: its contract is "carry the refusal forward as
    # a REASON" (RC-10, RK-5) — *a refusal that cannot say what it lacks is the
    # defect RC-10 exists to prevent*. So it catches and names it.
    # ★ Found by the fresh-clone check (DX-5): with no exports present, an
    # orchestration job went SUCCESS -> FAILED.
    try:
        accounts = discover_accounts(root)
    except RecordingError as exc:
        return (), str(exc)
    prices = dict(prices or {})
    if fetch is not None:
        # ★ **D-11 decides WHAT to price; the caller only knows HOW.** ⚠ The
        #   inversion matters: orchestration asking the book what it holds would
        #   put holdings knowledge in the shim (OR-2), and pricing only the
        #   trading universe made `DELL` — an ordinary US common stock — report
        #   as unpriceable beside `MDA.TO`, which is a different fact entirely.
        prices.update(quote_holdings(fetch, root=root))

    books, refusals = [], []
    for account_id, account_type in accounts:
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


def held_instruments(*, root: str | None = None) -> tuple[str, ...]:
    """Every instrument_id with a non-zero position, across EVERY account present.

    ✏ *"all four accounts"* until `RC-65` — the count is now whatever the export
    directory holds.

    ★ **The book is priced from what it HOLDS, not from the trading universe.**
    ⚠ Relying on the overlap made `DELL` — an ordinary US common stock — report
    as unpriceable beside `MDA.TO`, which is a genuinely different fact. A
    reason that conflates *"we did not fetch it"* with *"the plan will not sell
    it to us"* sends the reader to the wrong fix (DE-49, RC-10).
    """
    root = resolve_export_dir(root)
    held: set[str] = set()
    for account_id, _type in discover_accounts(root):
        path = export_path(root, account_id)
        if not path.exists():
            continue
        activities = parse_export(path, account_id=account_id)
        from src.recording.book.from_activity import derive_quantities

        quantities = derive_quantities(activities, group_orders(activities))
        held.update(i for i, q in quantities.items() if q)
    return tuple(sorted(held))


def quote_holdings(fetch, *, root: str | None = None) -> dict:
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
