"""D-11 §8a — the BMO holdings export, parsed and checked. RC-70…RC-78.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE HOLDINGS EXPORT IS THE BOOK'S OUTSIDE FIGURE.               ║
║                                                                  ║
║  RC-51: a transaction export carries no balance, so a derived    ║
║  book reconciles by construction and checks nothing.             ║
║  RC-58: FMP has no Canadian prices, so CDR and TSX lines cannot  ║
║  be valued — and every account holds one.                        ║
║                                                                  ║
║  BMO's holdings export carries its own price and market value    ║
║  for every line, cash per currency and the account balance.      ║
║  Read as REPORTED FACT as of its own date — never re-priced.     ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **Two FX rates (RC-72).** Market value uses the footer's CURRENT rate; the per-line
`FX rate` column is the rate AT PURCHASE and enters cost only. Mixing them mis-values
every US line, plausibly.

⚠⚠ **Line 1 carries the REAL account number (RC-78).** It is checked to be present and
discarded on the spot — it is in no object, no error message, no log. The account id is
the file name's.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from src.recording.book.from_activity import derive_cash, derive_quantities
from src.recording.book.load import discover_accounts, resolve_export_dir
from src.recording.book.models import OK, BookState, Position
from src.recording.errors import (
    HoldingsMissingError, HoldingsSelfCheckError, HoldingsUnrecognisedError,
    RecordingError,
)
from src.recording.reconcile.ingest import is_cdr_description

SOURCE = "holdings_export"

_HOLDINGS_RE = re.compile(r"^Holdings_(?P<account>[A-Z]+_\d+)\.csv$")
_COUNT_RE = re.compile(r"\(\s*(\d+)\s+holdings?\s*\)")
_RATE_RE = re.compile(r"^1 USD = ([0-9.]+) CAD$")
_MONTHS = {m: i for i, m in enumerate(
    ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}

#: RC-70 — the cash lines BMO prints, by description. Anything else raises.
CASH_DESCRIPTIONS = {"Canadian $ Cash": "CAD", "U.S. $ Cash": "USD"}
EQUITIES, CASH_BALANCES = "Equities", "Cash balances"

#: RC-73 — a cent, the printing precision of every money column.
CENT = 0.01
#: RC-73 (f) — half the last printed digit of a 4-dp rate: the most a correctly
#: rounded rate can move `quantity × price`. Derived from the format, not fitted.
RATE_HALF_DIGIT = 0.00005


@dataclass(frozen=True, slots=True)
class CashLine:
    currency: str
    amount: float          # native
    rate: float            # BMO's current rate for this currency (1.0 for CAD)
    value_cad: float

    def to_json_obj(self) -> dict:
        return {"currency": self.currency, "amount": self.amount, "rate": self.rate,
                "value_cad": self.value_cad}


@dataclass(frozen=True, slots=True)
class HoldingLine:
    """One equity line, as reported. ★ Identity from description + currency (RC-71)."""

    instrument_id: str
    symbol: str            # as printed (`ARM:US`)
    analysis_symbol: str   # `:US` dropped (RC-28)
    description: str
    sector: str            # BMO's label — not D-02's sector taxonomy
    quantity: float
    average_cost: float | None
    total_cost: float | None
    cost_currency: str
    price: float
    price_currency: str
    market_value_cad: float
    fx_at_cost: float | None   # ⚠ RC-72 — cost only, never value

    def to_json_obj(self) -> dict:
        return {k: getattr(self, k) for k in self.__slots__}


@dataclass(frozen=True, slots=True)
class HoldingsStatement:
    """One `Holdings_<ACCOUNT>.csv`, self-checked (RC-73). ⚠ No account number (RC-78)."""

    account_id: str
    as_of: date
    cash_total: float
    securities: float
    balance: float
    usd_cad: float | None
    cash: tuple[CashLine, ...]
    lines: tuple[HoldingLine, ...]
    source_file: str

    @property
    def account_type(self) -> str:
        return self.account_id.rsplit("_", 1)[0]

    def to_book_state(self, *, account_type: str | None = None) -> BookState:
        """RC-75 — `CT-11.4` from REPORTED figures only; capital base = the balance."""
        positions = tuple(Position(
            instrument_id=line.instrument_id, analysis_symbol=line.analysis_symbol,
            quantity=line.quantity, market_value=round(line.quantity * line.price, 2),
            currency=line.price_currency, account_id=self.account_id,
            average_cost=line.average_cost) for line in self.lines)
        cash = {c.currency: c.amount for c in self.cash}
        nav: dict = {}
        for p in positions:
            nav[p.currency] = nav.get(p.currency, 0.0) + p.market_value
        for currency, amount in cash.items():
            nav[currency] = nav.get(currency, 0.0) + amount
        return BookState(
            account_id=self.account_id, date=self.as_of, positions=positions,
            cash_by_currency=cash, nav_by_currency={k: round(v, 2) for k, v in nav.items()},
            base_currency="CAD", nav_base=self.balance,
            fx_rate_used={"USD": self.usd_cad} if self.usd_cad else {},
            capital_base=self.balance, reconciled=OK,
            account_type=account_type or self.account_type, source=SOURCE)

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "as_of": self.as_of.isoformat(),
                "cash_total": self.cash_total, "securities": self.securities,
                "balance": self.balance, "usd_cad": self.usd_cad,
                "cash": [c.to_json_obj() for c in self.cash],
                "lines": [line.to_json_obj() for line in self.lines],
                "source_file": self.source_file, "source": SOURCE}


def _num(text, where):
    text = (text or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        raise HoldingsUnrecognisedError(where, f"{text!r} is not a number (RC-70)") from None


def _as_of(text, where) -> date:
    """RC-74 — `dd-Mon-yyyy`, parsed without the locale."""
    m = re.fullmatch(r"(\d{1,2})-([A-Z][a-z]{2})-(\d{4})", (text or "").strip())
    if not m or m.group(2) not in _MONTHS:
        raise HoldingsUnrecognisedError(
            where, "no readable `as of date` — an undated balance is not a balance (RC-74)")
    return date(int(m.group(3)), _MONTHS[m.group(2)], int(m.group(1)))


def parse_holdings(path, *, account_id: str) -> HoldingsStatement:
    """RC-70…RC-74 — read, classify, self-check. Raises on anything it does not know."""
    path = Path(path)
    name = path.name
    rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
    rows = [[c.strip() for c in r] for r in rows]
    rows = [r for r in rows if any(r)]

    # ⚠⚠ RC-78 — line 1 is how a holdings export is recognised; its value is never kept.
    if not rows or rows[0][0] != "Account:" or len(rows[0]) < 2 or not rows[0][1]:
        raise HoldingsUnrecognisedError(name, "line 1 is not `Account:,<number>` — "
                                              "not a BMO holdings export (RC-70)")
    rows = rows[1:]
    if not rows or rows[0][0] != "as of date:":
        raise HoldingsUnrecognisedError(name, "no `as of date` line (RC-74)")
    as_of = _as_of(rows[0][1] if len(rows[0]) > 1 else "", name)

    totals = header = None
    cash_rows, equity_rows = [], []
    cash_total_row = portfolio_row = None
    usd_cad = None
    pending_rate = False
    for n, row in enumerate(rows[1:], start=3):
        where = f"{name}:{n}"
        first = row[0]
        if pending_rate:
            m = _RATE_RE.match(first)
            if not m:
                raise HoldingsUnrecognisedError(where, "`Exchange Rate:` not followed by "
                                                       "`1 USD = r CAD` (RC-72)")
            usd_cad = float(m.group(1))
            pending_rate = False
        elif first == "" and len(row) > 5 and row[1] == "Cash" and row[3] == "Value of securities":
            continue                                   # the totals' own header
        elif first == "Total":
            if row[2] != "CAD" or row[4] != "CAD" or row[6] != "CAD":
                raise HoldingsUnrecognisedError(where, "account totals not in CAD (RC-70)")
            totals = (_num(row[1], where), _num(row[3], where), _num(row[5], where))
        elif first == CASH_BALANCES and not any(row[1:]):
            continue                                   # the one-cell heading row
        elif first == "Asset class":
            header = row
        elif first == CASH_BALANCES:
            cash_rows.append((where, row, header))
        elif first == EQUITIES:
            equity_rows.append((where, row, header))
        elif first == "Total cash balances":
            cash_total_row = (where, row, header)
        elif first.startswith("Total portfolio value"):
            portfolio_row = (where, row, header)
        elif first == "Exchange Rate:":
            pending_rate = True
        else:
            raise HoldingsUnrecognisedError(
                where, f"unrecognised line {first!r} — only `{EQUITIES}` and "
                       f"`{CASH_BALANCES}` are known asset classes (RC-70)")
    if totals is None or header is None:
        raise HoldingsUnrecognisedError(name, "no `Total` line or no column header (RC-70)")
    if pending_rate:
        raise HoldingsUnrecognisedError(name, "`Exchange Rate:` with no rate after it (RC-72)")

    cash = tuple(_cash_line(w, r, h) for w, r, h in cash_rows)
    lines = tuple(_equity_line(w, r, h) for w, r, h in equity_rows)
    needs_rate = [c.currency for c in cash if c.currency == "USD"] + [
        line.symbol for line in lines if line.price_currency == "USD"]
    if needs_rate and usd_cad is None:
        raise HoldingsUnrecognisedError(
            name, f"{needs_rate} are in USD and the file carries no `1 USD = r CAD` footer — "
                  f"no rate, no number (RC-72, FX-3)")

    statement = HoldingsStatement(
        account_id=account_id, as_of=as_of, cash_total=totals[0], securities=totals[1],
        balance=totals[2], usd_cad=usd_cad, cash=cash, lines=lines, source_file=name)
    _self_check(statement, cash_total_row, portfolio_row)
    return statement


def _col(header, label, where):
    try:
        return header.index(label)
    except ValueError:
        raise HoldingsUnrecognisedError(where, f"column {label!r} missing (RC-70)") from None


def _cell(row, i):
    return row[i] if i < len(row) else ""


def _cash_line(where, row, header) -> CashLine:
    description = _cell(row, _col(header, "Description", where))
    currency = CASH_DESCRIPTIONS.get(description)
    if currency is None:
        raise HoldingsUnrecognisedError(
            where, f"cash line {description!r} is not one of {sorted(CASH_DESCRIPTIONS)} (RC-70)")
    cost = _col(header, "Total cost", where)
    if _cell(row, cost + 1) != currency:
        raise HoldingsUnrecognisedError(
            where, f"{description!r} is booked in {_cell(row, cost + 1)!r} (RC-70)")
    mv = _col(header, "Market value", where)
    return CashLine(currency=currency, amount=_num(_cell(row, _col(header, "Quantity", where)), where),
                    rate=_num(_cell(row, _col(header, "Current price", where)), where),
                    value_cad=_num(_cell(row, mv), where))


def _equity_line(where, row, header) -> HoldingLine:
    description = _cell(row, _col(header, "Description", where))
    symbol = _cell(row, _col(header, "Symbol", where)).upper()
    price_at = _col(header, "Current price", where)
    cost_at = _col(header, "Total cost", where)
    avg_at = _col(header, "Average cost", where)
    mv_at = _col(header, "Market value", where)
    price_currency = _cell(row, price_at + 1)
    if price_currency not in ("CAD", "USD"):
        raise HoldingsUnrecognisedError(where, f"{symbol}: price currency {price_currency!r} (RC-70)")
    if _cell(row, mv_at + 1) != "CAD":
        raise HoldingsUnrecognisedError(where, f"{symbol}: market value not in CAD (RC-70)")
    # ★★ RC-71 — the `:US` suffix and the currency must agree; neither is assumed right.
    us = symbol.endswith(":US")
    if us != (price_currency == "USD"):
        raise HoldingsUnrecognisedError(
            where, f"{symbol} is priced in {price_currency}: a `:US` suffix must go with USD "
                   f"and USD with `:US` — the two disagree (RC-71)")
    bare = symbol[:-3] if us else symbol
    wrapper = "CDR" if is_cdr_description(description) else "COMMON"
    fx_at = header.index("FX rate") if "FX rate" in header else None
    return HoldingLine(
        instrument_id=f"{bare}|{wrapper}|{price_currency}", symbol=symbol,
        analysis_symbol=bare, description=description,
        sector=_cell(row, _col(header, "PROD Type/IND. Sector", where)),
        quantity=_num(_cell(row, _col(header, "Quantity", where)), where),
        average_cost=_num(_cell(row, avg_at), where), total_cost=_num(_cell(row, cost_at), where),
        cost_currency=_cell(row, cost_at + 1), price=_num(_cell(row, price_at), where),
        price_currency=price_currency, market_value_cad=_num(_cell(row, mv_at), where),
        fx_at_cost=_num(_cell(row, fx_at), where) if fx_at is not None else None)


def _self_check(s: HoldingsStatement, cash_total_row, portfolio_row) -> None:
    """★★ RC-73 — (a)…(g), every failure listed and named."""
    failures = []

    def off(a, b, tol=CENT):
        return a is None or b is None or abs(a - b) > tol + 1e-9

    cash_sum = round(sum(c.value_cad for c in s.cash), 2)
    if off(cash_sum, s.cash_total):
        failures.append(f"(a) Σ cash lines {cash_sum:.2f} ≠ cash total {s.cash_total:.2f}")
    mv_sum = round(sum(line.market_value_cad for line in s.lines), 2)
    if off(mv_sum, s.securities):
        failures.append(f"(b) Σ market values {mv_sum:.2f} ≠ value of securities {s.securities:.2f}")
    if off(round(s.cash_total + s.securities, 2), s.balance):
        failures.append(f"(c) cash {s.cash_total:.2f} + securities {s.securities:.2f} "
                        f"≠ account balance {s.balance:.2f}")
    if portfolio_row is None:
        failures.append("(d) no `Total portfolio value` line")
    else:
        where, row, header = portfolio_row
        reported = _num(_cell(row, header.index("Market value")), where)
        m = _COUNT_RE.search(row[0])
        if off(reported, s.balance):
            failures.append(f"(d) total portfolio value {reported} ≠ account balance {s.balance:.2f}")
        if not m or int(m.group(1)) != len(s.lines):
            failures.append(f"(d) the file says {row[0]!r} and carries {len(s.lines)} equity line(s)")
    if cash_total_row is None:
        failures.append("(e) no `Total cash balances` line")
    else:
        where, row, header = cash_total_row
        reported = _num(_cell(row, header.index("Market value")), where)
        if off(reported, s.cash_total):
            failures.append(f"(e) total cash balances {reported} ≠ cash total {s.cash_total:.2f}")
    for c in s.cash:
        rate = s.usd_cad if c.currency == "USD" else 1.0
        if off(round(c.amount * rate, 2), c.value_cad,
               CENT + (c.amount * RATE_HALF_DIGIT if c.currency == "USD" else 0)):
            failures.append(f"(f) {c.currency} cash {c.amount} × {rate} ≠ {c.value_cad}")
        if c.currency == "USD" and off(c.rate, s.usd_cad, 1e-9):
            failures.append(f"(g) the USD cash line's rate {c.rate} ≠ the footer's {s.usd_cad}")
    for line in s.lines:
        usd = line.price_currency == "USD"
        native = line.quantity * line.price
        expect = round(native * (s.usd_cad if usd else 1.0), 2)
        if off(expect, line.market_value_cad, CENT + (native * RATE_HALF_DIGIT if usd else 0)):
            failures.append(f"(f) {line.symbol}: {line.quantity:g} × {line.price} "
                            + (f"× {s.usd_cad} " if usd else "")
                            + f"= {expect:.2f} ≠ market value {line.market_value_cad:.2f}")
    if failures:
        raise HoldingsSelfCheckError(s.source_file, failures)


# --------------------------------------------------------------------------- #
# RC-77 — where the files are, and refusing by name
# --------------------------------------------------------------------------- #
def holdings_path(root, account_id: str) -> Path:
    return Path(root) / f"Holdings_{account_id}.csv"


def discover_holdings(root) -> tuple[str, ...]:
    path = Path(root)
    if not path.is_dir():
        return ()
    return tuple(sorted(m.group("account") for e in path.iterdir()
                        if (m := _HOLDINGS_RE.match(e.name))))


def load_holdings(account_id: str, *, root: str | None = None) -> HoldingsStatement:
    """RC-77 — one account's statement, or a refusal naming it. Never a fallback."""
    root = resolve_export_dir(root)
    path = holdings_path(root, account_id)
    if not path.exists():
        raise HoldingsMissingError((account_id,), root)
    return parse_holdings(path, account_id=account_id)


def load_book_wide(*, root: str | None = None) -> tuple[HoldingsStatement, ...]:
    """RC-77, RC-3, RK-5 — every account or a refusal naming each one missing.

    ★ The account set is every account with EITHER export (RC-65): a transaction
    history with no holdings beside it is an account that exists and is unvalued.
    """
    root = resolve_export_dir(root)
    try:
        accounts = {a for a, _type in discover_accounts(root)}
    except RecordingError:
        accounts = set()
    have = set(discover_holdings(root))
    accounts |= have
    missing = sorted(accounts - have)
    if missing or not accounts:
        raise HoldingsMissingError(missing or ("<any account>",), root)
    return tuple(load_holdings(a, root=root) for a in sorted(accounts))


# --------------------------------------------------------------------------- #
# RC-76 — derived vs reported
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class HoldingsBreak:
    """One RC-76 disagreement. ⚠ Reported with both windows; neither side is adjusted."""

    account_id: str
    item: str                    # an instrument id, or `cash <CCY>`
    derived: float
    reported: float
    transactions_end: date | None
    holdings_as_of: date

    def __str__(self) -> str:
        end = self.transactions_end.isoformat() if self.transactions_end else "—"
        return (f"{self.account_id} {self.item}: derived {self.derived:g} vs reported "
                f"{self.reported:g} — transactions end {end}, holdings as of "
                f"{self.holdings_as_of.isoformat()}; activity in the gap is the commonest "
                f"honest cause, and neither side is adjusted (RC-76)")

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "item": self.item, "derived": self.derived,
                "reported": self.reported, "holdings_as_of": self.holdings_as_of.isoformat(),
                "transactions_end": (self.transactions_end.isoformat()
                                     if self.transactions_end else None)}


def reconcile_with_activity(statement: HoldingsStatement, activities, orders
                            ) -> tuple[HoldingsBreak, ...]:
    """★★ RC-76 — RC-10 against something that can be wrong. Both directions, to the cent."""
    activities = tuple(activities)
    end = max((a.trade_date for a in activities), default=None)
    derived_q = derive_quantities(activities, orders)
    reported_q = {line.instrument_id: line.quantity for line in statement.lines}
    derived_c = derive_cash(activities)
    reported_c = {c.currency: c.amount for c in statement.cash}

    found = []
    for item in sorted(set(derived_q) | set(reported_q)):
        d, r = derived_q.get(item, 0.0), reported_q.get(item, 0.0)
        if abs(d - r) > 1e-6:
            found.append(HoldingsBreak(statement.account_id, item, d, r, end, statement.as_of))
    for currency in sorted(set(derived_c) | set(reported_c)):
        d, r = derived_c.get(currency, 0.0), reported_c.get(currency, 0.0)
        if abs(d - r) > CENT / 2:
            found.append(HoldingsBreak(statement.account_id, f"cash {currency}", d, r, end,
                                       statement.as_of))
    return tuple(found)
