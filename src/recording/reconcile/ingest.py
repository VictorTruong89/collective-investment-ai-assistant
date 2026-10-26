"""D-11 §8 — the BMO InvestorLine export, parsed. RC-9…RC-18, RC-36, RC-37.

★ **The broker is BMO InvestorLine.** ⚠ **"CIBC" in this data is the CDR issuer
and belongs to the INSTRUMENT, never to the account** (RC-36, §5.3 H-0):
`MICRON TECHNOLOGY CIBC CDN DEP`, `BROADCOM CDR CIBC CDN DEPOSITA`.

★ **RC-9: the book is DERIVED from activity and reconciled against the export,
never read from it.** No cash balance is supplied, so every position and every
cash line here is computed from the transactions and then checked (RC-10).
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

#: The 10-column layout (TFSA_1, RRSP_1, RESP_1) and the 13-column layout
#: (TFSA_2) differ by three inserted columns. ★ **RC-41**: the header is READ,
#: never assumed — a positional parser reads `Account name` as
#: `Activity Description` on the wider file and silently mis-books every row.
CANONICAL = {
    "transaction date": "trade_date",
    "settlement date": "settlement_date",
    "activity description": "activity",
    "description": "instrument_name",
    "symbol": "symbol",
    "quantity": "quantity",
    "price": "price",
    "price currency": "price_currency",
    "total amount": "total_amount",
    "total currency": "total_currency",
    "account name": "account_name",
    "account type": "account_type",
    "account number": "account_number",
}

#: RC-13 — ★ **an unclassifiable activity RAISES.** *No neutral default, no
#: silent drop.* Every value BMO emits must appear here or the run stops.
#: ★★ RC-55 — **the layout can change WITHIN one file.** Measured 2026-08-25:
#: `TransactionHistory_TFSA_2.csv` carries **75 ten-column rows and 74
#: thirteen-column rows**, interleaved, because newer activity was appended
#: from a differently-shaped export. ⚠ Reading the header once and applying it
#: to every row puts `Quantity` where `Activity Description` belongs — the very
#: first symptom was an activity called `'1000'`.
NARROW_FIELDS = ("transaction date", "settlement date", "activity description",
                 "description", "symbol", "quantity", "price", "price currency",
                 "total amount", "total currency")

#: ⚠ RC-56 — **a blank `Activity Description` is not an absence.** Measured:
#: three RESP rows carry `BENE: 01 … GRANT REC` with **no activity type and
#: $500 of real cash each**. Skipping them silently lost **exactly $1,500** and
#: the account missed its stated balance by that amount. ★ The mapping is
#: DECLARED DATA keyed on the description — not an inference — so a reader can
#: see which rows it claims and disagree.
BLANK_ACTIVITY_BY_DESCRIPTION = (
    ("GRANT REC", "Grant"),
)

BUY, SELL, DIVIDEND, CONTRIBUTION, NR_TAX, FX, INTEREST = (
    "Buy", "Sell", "Dividend", "Contribution", "Non resident tax",
    "Foreign Exchange", "Interest")
#: Found only once the exports were re-pulled from account inception (2022).
#: ★ Five types that four years of history contain and eight months did not —
#: which is RC-13's argument made twice over.
HST, ADMIN_FEE, WITHDRAWAL, DISBURSEMENT, ONLINE_BANKING, GRANT = (
    "Harmonized sales tax", "Admin fee charged", "Withdrawal", "Disbursement",
    "Online banking", "Grant")
#: ★ Enumerated from the four real exports (2026-01-01 → 2026-08-18), not
#: imagined. ⚠ `Interest` appears **once** in 216 rows and was missed by a
#: positional survey of the files — because the 13-column TFSA_2 layout puts
#: `Account name` where the 10-column layout puts `Activity Description`.
#: **RC-13 caught it on the first real parse**, which is the whole argument for
#: failing loud on an unknown activity rather than defaulting.
KNOWN_ACTIVITIES = frozenset({BUY, SELL, DIVIDEND, CONTRIBUTION, NR_TAX, FX,
                              INTEREST, HST, ADMIN_FEE, WITHDRAWAL,
                              DISBURSEMENT, ONLINE_BANKING, GRANT})

#: Activities that move cash without touching a position (RC-9's cash side).
CASH_ONLY = frozenset({DIVIDEND, CONTRIBUTION, NR_TAX, INTEREST, FX, HST,
                       ADMIN_FEE, WITHDRAWAL, ONLINE_BANKING, GRANT})

#: ★★ Activities that move SHARES without a price — **a corporate action wearing
#: BMO's `Disbursement` label**, not cash leaving the account.
#:
#: ⚠ Measured, `RESP_1 · PLTR CDR`:
#:
#: ```
#:   buys 2025-11-12 :  30 + 100        = +130
#:   Disbursement    :                    +390
#:   sells 2026-01-15: -500 + -20       = -520      130 x 4 = 520
#: ```
#:
#: ★ **It is a 4:1 ratio change** — CIBC adjusts CDR ratios to pass through
#: hedge costs and dividends, and BMO books the extra shares under this label.
#: ⚠ **It cannot be dropped**: without it the position is `-390`, which is
#: impossible. The SIGN is taken from the file, never inferred — and the book
#: reconciles to exactly zero on that reading and on no other.
POSITION_MOVING_NON_TRADE = frozenset({DISBURSEMENT})

#: What such a row actually is, for anything that renders or records it.
CORPORATE_ACTION_ADJUSTMENT = "corporate_action_share_adjustment"

TRADES = frozenset({BUY, SELL})


def is_cdr_description(name: str) -> bool:
    """RC-36 — ★ the CDR marker lives in the INSTRUMENT name, not the account.

    ★ Shared with the holdings parser (RC-71), so both exports derive the same
    `instrument_id` and can be reconciled line by line (RC-76).
    """
    upper = (name or "").upper()
    return "CIBC" in upper or " CDR" in upper or "CDN DEP" in upper


@dataclass(frozen=True, slots=True)
class Activity:
    """One export row, canonicalised. ⚠ **RC-12: missing is `None`, never zero.**

    *A zero `Total Amount` is a **tranche** (H-1), not an absence* — collapsing
    the two is how a real leg of a split order disappears from the book.
    """

    account_id: str
    trade_date: date
    settlement_date: date | None
    activity: str
    instrument_name: str
    symbol: str
    quantity: float | None
    price: float | None
    price_currency: str | None
    total_amount: float | None
    total_currency: str | None
    source_file: str = ""
    row_number: int = 0

    @property
    def is_trade(self) -> bool:
        return self.activity in TRADES

    @property
    def is_corporate_action(self) -> bool:
        """RC-49 — ★ a share adjustment, **not** cash leaving the account."""
        return (self.activity in POSITION_MOVING_NON_TRADE
                and bool(self.symbol) and not self.total_amount)

    @property
    def moves_position(self) -> bool:
        """★ Trades **and** the corporate-action share adjustments (RC-49)."""
        if self.is_trade:
            return True
        return (self.activity in POSITION_MOVING_NON_TRADE
                and bool(self.symbol) and bool(self.quantity))

    @property
    def is_cdr(self) -> bool:
        """RC-36 — ★ the CDR marker lives in the INSTRUMENT name, not the account."""
        return is_cdr_description(self.instrument_name)

    @property
    def instrument_id(self) -> str:
        """RC-16 — identity in the BOOK is `(symbol, wrapper, venue_currency)`."""
        wrapper = "CDR" if self.is_cdr else "COMMON"
        # ⚠ `|`, not `.` — **`BBD.B` is a real holding in this book** and a
        #   dotted id (`BBD.B.COMMON.CAD`) cannot be split back into its three
        #   parts by any consumer. The separator has to be one a ticker cannot
        #   contain (RC-16).
        return f"{self.symbol}|{wrapper}|{self.price_currency or self.total_currency}"

    @property
    def analysis_symbol(self) -> str:
        """RC-28 — ★ what D-02/D-03/D-04 see: **the underlying US ticker.**

        ⚠ *A CDR and its underlying are the same COMPANY and different LOTS*,
        which is why D-05 **RK-5** aggregates them into one exposure.
        """
        return self.symbol.upper()

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id,
                "trade_date": self.trade_date.isoformat(),
                "activity": self.activity, "symbol": self.symbol,
                "instrument_id": self.instrument_id,
                "analysis_symbol": self.analysis_symbol,
                "quantity": self.quantity, "price": self.price,
                "price_currency": self.price_currency,
                "total_amount": self.total_amount,
                "total_currency": self.total_currency,
                "is_cdr": self.is_cdr, "source_file": self.source_file,
                "row_number": self.row_number}


def file_hash(path) -> str:
    """RC-11 — ★ re-ingesting the same export is **idempotent**, keyed on content.

    ⚠ *A changed hash for a covered window is a **restatement**, recorded not
    overwritten* (DE-24's shape).
    """
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _header_index(rows) -> tuple[int, list[str]]:
    """RC-37 — find the header row and map it, rather than counting columns."""
    for i, row in enumerate(rows[:8]):
        lowered = [c.strip().lower().lstrip("﻿") for c in row]
        if "transaction date" in lowered and "symbol" in lowered:
            return i, lowered
    from src.recording.errors import UnclassifiableActivityError

    raise UnclassifiableActivityError(
        "<header>", "no header row containing 'Transaction Date' and 'Symbol' "
                    "in the first 8 lines — this is not a BMO export (RC-41)")


def _num(text):
    text = (text or "").strip()
    if not text:
        return None                    # ⚠ RC-12 — missing is None, never zero
    return float(text.replace(",", "").replace("$", ""))


def _dt(text):
    text = (text or "").strip()
    return date.fromisoformat(text) if text else None


def parse_export(path, *, account_id: str,
                 strict_accounts: bool = True) -> tuple[Activity, ...]:
    """RC-1/RC-13/RC-18 — every row attributed, every activity classified.

    ⚠ **RC-18: account type is CONFIGURATION**, never inferred from a
    `Contribution` description that may fall outside the window — so
    `account_id` is supplied by the caller and never read from the file.
    """
    from src.recording.errors import UnclassifiableActivityError

    raw = list(csv.reader(Path(path).read_text(encoding="utf-8-sig").splitlines()))
    start, header = _header_index(raw)
    fields = [CANONICAL.get(name, name) for name in header]

    out, name, foreign = [], Path(path).name, []
    # The account this file is *about*: the modal account number, where the
    # layout carries one at all.
    numbers = [r[fields.index("account_number")].strip()
               for r in raw[start + 1:]
               if "account_number" in fields and len(r) > fields.index("account_number")]
    numbers = [x for x in numbers if x and set(x) != {"-"}]
    declared_account = max(set(numbers), key=numbers.count) if numbers else ""
    for n, row in enumerate(raw[start + 1:], start=start + 2):
        if not any(cell.strip() for cell in row):
            continue
        if set("".join(row).strip()) <= {"-"}:          # the ---- rule line
            continue
        # ★ RC-55 — map THIS row, by its own width. A narrow row inside a wide
        #   file is not corrupt; it is a differently-shaped export appended.
        row_fields = fields
        if len(row) != len(fields):
            row_fields = ([CANONICAL[n] for n in NARROW_FIELDS]
                          if len(row) == len(NARROW_FIELDS) else fields)
        record = dict(zip(row_fields, row))
        activity = (record.get("activity") or "").strip()
        if not activity:
            # ⚠ RC-56 — a blank activity carrying CASH is not an absence.
            description = (record.get("instrument_name") or "").upper()
            for marker, mapped in BLANK_ACTIVITY_BY_DESCRIPTION:
                if marker in description:
                    activity = mapped
                    break
            else:
                if _num(record.get("total_amount")):
                    raise UnclassifiableActivityError(
                        f"{name}:{n}",
                        f"a blank activity carrying "
                        f"{record.get('total_amount')} "
                        f"{record.get('total_currency')} — description "
                        f"{(record.get('instrument_name') or '').strip()!r}. "
                        f"Skipping it silently loses real cash (RC-56)")
                continue
        if activity not in KNOWN_ACTIVITIES:
            # ★ RC-13 — P5. A new BMO activity type stops the run rather than
            #   being silently dropped from a book that must balance.
            raise UnclassifiableActivityError(
                f"{name}:{n}",
                f"activity {activity!r} is not one of {sorted(KNOWN_ACTIVITIES)}")
        # ★★ RC-48 — where the export carries account columns, a row belonging
        #   to a DIFFERENT account is refused, never absorbed. ⚠ Measured:
        #   `TransactionHistory_TFSA_2.csv` contains one `Joint` row
        #   (account <Joint account no., redacted>) among 146 TFSA rows (<TFSA_2 account no., redacted>). Booking it into
        #   the TFSA would attribute another account's cash to this one — small
        #   here ($0.50), and the principle is RC-1's.
        row_account = (record.get("account_number") or "").strip()
        if row_account and declared_account and row_account != declared_account:
            foreign.append((n, row_account,
                            (record.get("account_type") or "").strip()))
            continue

        out.append(Activity(
            account_id=account_id,
            trade_date=_dt(record.get("trade_date")),
            settlement_date=_dt(record.get("settlement_date")),
            activity=activity,
            instrument_name=(record.get("instrument_name") or "").strip(),
            symbol=(record.get("symbol") or "").strip().upper(),
            quantity=_num(record.get("quantity")),
            price=_num(record.get("price")),
            price_currency=(record.get("price_currency") or "").strip() or None,
            total_amount=_num(record.get("total_amount")),
            total_currency=(record.get("total_currency") or "").strip() or None,
            source_file=name, row_number=n))

    if foreign and strict_accounts:
        from src.recording.errors import ForeignAccountRowError

        raise ForeignAccountRowError(name, declared_account, foreign)
    return tuple(out)
