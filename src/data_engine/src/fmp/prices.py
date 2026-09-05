"""FMP prices — the RAW series is the system of record (DE-27, AC-7.43).

★ `non-split-adjusted` is the only raw feed, and it matters more than the name
suggests. Everything else — `full`, `light`, `dividend-adjusted` — is
retro-adjusted for every split since. Measured on NVDA's 10:1:

    non-split-adjusted  1150.00   raw — what a person actually saw
    full                 115.00   split-adjusted (/10)
    light                115.00   identical to full
    dividend-adjusted    114.80   split- AND dividend-adjusted

**Volume is retro-adjusted in the opposite direction**: `full` reports
438,392,000 shares against a true 43,839,200.

⚠ A caution about how this was nearly missed: the first pass (MSFT · MU · ARM)
found `full` and `non-split-adjusted` identical to 4dp and concluded split
adjustment was not the hazard. **None of those three split in the window** — the
two series agreed because there was nothing to disagree about.
"""

from __future__ import annotations

from src.shared.money import Money

from datetime import date, datetime
from decimal import Decimal

import pandas as pd

from src.data_engine.errors import ContractViolationError
from src.data_engine.pit.models import CorporateEvent
from src.shared.money import SUPPORTED_CURRENCIES, Money

#: The only endpoint that returns what a person actually saw.
RAW_ENDPOINT = "historical-price-eod/non-split-adjusted"
#: Kept only so DE-43 can compare a reconstruction against the vendor's own.
VENDOR_ADJUSTED_ENDPOINT = "historical-price-eod/full"


def raw_prices(client, ticker: str, start: date, end: date, *,
               currency: str = "USD") -> pd.DataFrame:
    """The raw OHLCV series, canonicalised at the boundary (DE-2, DE-3, DE-7)."""
    payload = client.get(RAW_ENDPOINT, symbol=ticker.upper(),
                         **{"from": start.isoformat(), "to": end.isoformat()})
    rows = _rows(payload)
    if not rows:
        raise ContractViolationError(
            RAW_ENDPOINT,
            f"{ticker}: no raw price rows for {start}..{end}. An empty price series "
            f"is not a zero-row panel — it is a source failure (DE-14, P5)",
        )
    out = pd.DataFrame([{
        "ticker": ticker.upper(),
        "date": pd.Timestamp(r["date"]),
        "open_minor": _minor(_field(r, "open"), currency),
        "high_minor": _minor(_field(r, "high"), currency),
        "low_minor": _minor(_field(r, "low"), currency),
        "close_minor": _minor(_field(r, "close"), currency),
        "volume": int(r["volume"]),
        "currency": currency,
        "source": "fmp",
    } for r in rows])
    return out.sort_values("date", kind="mergesort").reset_index(drop=True)


def vendor_adjusted(client, ticker: str, start: date, end: date, *,
                    currency: str = "USD") -> pd.DataFrame:
    """`full` — used ONLY as DE-43's external check, never ingested as primary."""
    payload = client.get(VENDOR_ADJUSTED_ENDPOINT, symbol=ticker.upper(),
                         **{"from": start.isoformat(), "to": end.isoformat()})
    return pd.DataFrame([{
        "ticker": ticker.upper(),
        "date": pd.Timestamp(r["date"]),
        "adj_open_minor": _minor(_field(r, "open"), currency),
        "adj_close_minor": _minor(_field(r, "close"), currency),
    } for r in _rows(payload)]).sort_values("date", kind="mergesort").reset_index(drop=True)


def splits(client, ticker: str) -> list[CorporateEvent]:
    """Split events. `date` is the EFFECTIVE date; the announcement is in an 8-K.

    ⚠ `knowable_at` is set to the effective date here and that is deliberately
    **conservative, not correct**: the true knowability date is the 8-K
    acceptance, which is earlier. Using the effective date can only *omit* a
    split from a report keyed on knowability (DE-34), never invent one — and
    §6A.2 class 2 says the announcement lives in a different feed, so joining
    the two is the 8-K router's job (B4.6), not this function's.
    """
    payload = client.get("splits", symbol=ticker.upper())
    out = []
    for r in _rows(payload):
        effective = _as_date(r["date"])
        out.append(CorporateEvent(
            ticker.upper(), "split", effective, effective,
            {"numerator": float(r["numerator"]), "denominator": float(r["denominator"])},
            "fmp:splits",
        ))
    return sorted(out, key=lambda e: e.event_date)


def dividends(client, ticker: str, *, currency: str = "USD") -> list[CorporateEvent]:
    """Dividend events keyed on `declarationDate` for knowability (DE-18, K-4).

    ★ **`declarationDate` matters more than it looks.** MSFT's dividends declare
    a median ~72 days before the ex-date (90/90 rows populated). A "dividend
    coming up" feature keyed on `date` fires far too late to be the signal it
    claims to be; keyed on `declarationDate` it is both earlier and honestly PIT.

    `date` remains the EX-date, which is what the DE-44 adjustment needs — the
    two dates answer different questions and the entity carries both.
    """
    payload = client.get("dividends", symbol=ticker.upper())
    out = []
    for r in _rows(payload):
        ex = _as_date(r["date"])
        declared = _as_date(r["declarationDate"]) if r.get("declarationDate") else ex
        # `dividend`, not `adjDividend`: the latter is retro-adjusted by the same
        # split machinery and needs the same adj_as_of (§5C.5, QD-13).
        cash_minor, cash_exact = _dividend_amount(r["dividend"], currency, ticker, ex)
        out.append(CorporateEvent(
            ticker.upper(), "dividend", ex, declared,
            {"cash_minor": cash_minor, "cash_exact": cash_exact, "currency": currency},
            "fmp:dividends",
        ))
    return sorted(out, key=lambda e: e.event_date)


#: ⚠ **THE FIELD NAMES ON THE RAW ENDPOINT ARE `adjOpen`/`adjClose`.**
#: Measured live 2026-08-23 against `historical-price-eod/non-split-adjusted`:
#:
#:     non-split-adjusted  {"adjOpen": 1197.7, ..., "adjClose": 1208.9,
#:                          "volume": 41238600}     <- RAW values
#:     full                {"open": 119.77, ..., "close": 120.89,
#:                          "volume": 412386000}    <- ADJUSTED values
#:
#: ★ The endpoint whose fields are called `adj*` is the one that is NOT adjusted,
#: and the endpoint with plain names is the one that is. Reading by field name
#: alone gets it exactly backwards, and both shapes parse without error — which
#: is why this mapping is explicit and named rather than a `.get()` chain. The
#: live probe (§6A.4) is what caught it; a fixture written from this file's own
#: assumptions never would have.
_FIELD_ALIASES = {
    "open": ("open", "adjOpen"),
    "high": ("high", "adjHigh"),
    "low": ("low", "adjLow"),
    "close": ("close", "adjClose"),
}


def _field(row: dict, name: str):
    for key in _FIELD_ALIASES[name]:
        if key in row:
            return row[key]
    raise ContractViolationError(
        RAW_ENDPOINT,
        f"row has neither {' nor '.join(_FIELD_ALIASES[name])}; FMP changed the price "
        f"payload shape. Keys present: {sorted(row)}",
    )


def _rows(payload):
    if isinstance(payload, dict):
        return payload.get("historical", []) or []
    return payload or []


def _dividend_amount(value, currency: str, ticker: str, ex: date) -> tuple[int, str]:
    """★ **Dividends are quoted to SUB-CENT precision, and `Money` refuses to guess.**

    ⚠ Found 2026-08-23 running the B3 skeleton on live data: NVDA's pre-split
    dividends are `0.0100`, `0.115` and similar, and `Money.from_float` raised
    `PrecisionLossError` — **correctly**. A per-share dividend is not a cash
    amount in an account; it is a rate, and USD's two decimal places do not bound
    it.

    ★ **So both are kept.** `cash_minor` is the quantized amount, rounded ONCE and
    explicitly (MO-5, AC-M.16), for anything that is actually money. `cash_exact`
    is the vendor's decimal string, kept because **the DE-44 adjustment factor is
    a RATIO** — `1 − d/close` — and quantizing `d` to a cent before dividing
    throws away precision the factor can use. Discarding it would be DE-14's
    lesson inverted: not a missing value stored as zero, but a known value
    stored coarser than it was known.
    """
    exact = Decimal(str(value))
    if exact < 0:
        raise ContractViolationError(
            "fmp:dividends", f"{ticker} {ex}: negative dividend {value!r}"
        )
    # `cash_exact` is returned in MINOR units, like `cash_minor`, so the two are
    # the same quantity at two precisions rather than two quantities in two
    # units. Scaling by the currency's own exponent rather than a literal 100
    # keeps that true for a zero-decimal currency (CN-8 — a number carries its
    # unit, and here the unit is in the name of both fields).
    # ⚠ `from_minor_decimal` takes MINOR units — it quantizes a Decimal that is
    # already scaled. Passing major units silently yields 0 for any dividend
    # under a dollar, which is most of them. Found running the B3 skeleton:
    # NVDA's $0.01 came back as 0 minor units.
    scale = Decimal(10) ** SUPPORTED_CURRENCIES[currency]
    minor_exact = exact * scale
    return Money.from_minor_decimal(minor_exact, currency).amount_minor, str(minor_exact)


def _minor(value, currency: str) -> int:
    """DE-3 — Money is built at the boundary, and the rounding is stated here.

    FMP returns JSON floats. QM-2 permits `from_float` at a provider boundary
    precisely so the conversion is greppable: every place a float becomes money
    is one of these call sites and nowhere else.

    ⚠⚠ **`Money.from_float` alone refuses these rows.** *Measured 2026-08-27:*
    `AAPL` returns a close of **`310.245`** and `SNDK` one of **`1454.445`** in
    the historical series — more precision than USD supports — and `Money`
    raises rather than round silently. ★★ **The refusal cost the whole ticker**:
    `assert_complete` reported `AAPL` as `no_source`, which reads as *"the vendor
    has no data"* when the truth is *"the vendor has data we declined to round"*.

    ⚠ It went unseen because the daily run fetches **200 days** and the
    sub-penny prints sat further back — so the defect is invisible at inference
    and fatal at **training**, which is the one that needs years.

    ★ Rounded HALF_UP, the same decision `day_open_row` states for the same
    reason: *a bar price is a price you could transact at, and USD transacts in
    cents.* The raw endpoint returns traded prices, so this never sees a
    split-adjusted fraction of a cent — that arithmetic happens downstream on
    minor units.
    """
    from decimal import ROUND_HALF_UP, Decimal

    from src.shared.money import SUPPORTED_CURRENCIES

    # ★ The exponent comes from Money's own TABLE, never the literal 2 — *"a
    #   zero-decimal currency (JPY) or three-decimal one (KWD) would otherwise be
    #   silently wrong by a factor of 100 the day one is added."*
    places = Decimal(1).scaleb(-SUPPORTED_CURRENCIES[currency])
    rounded = Decimal(str(value)).quantize(places, rounding=ROUND_HALF_UP)
    return Money.from_decimal_str(str(rounded), currency).amount_minor


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def open_row(client, ticker: str, as_of) -> dict | None:
    """DE-47 — the day-T row, reduced to the **opening print alone**.

    ⚠ **MEASURED 2026-08-25 14:42 ET, NVDA, mid-session:** this endpoint
    returned `open 211.025 · high 214.7291 · low 210.11 · close 212.855` — a
    plausible, **non-collapsed** bar whose `close` is simply the running price,
    with nothing in the payload saying so. ★ So the other three fields are
    dropped here rather than downstream: **collapse-detection is necessary and
    not sufficient**, and the only field that is final at 10:00 is the open.
    """
    payload = client.get(RAW_ENDPOINT, symbol=ticker.upper(),
                         **{"from": str(as_of), "to": str(as_of)})
    rows = _rows(payload)
    if not rows:
        return None
    raw = _field(rows[0], "open")
    if raw is None:
        return None
    # ★ DE-3 — Money is constructed at the BOUNDARY. ⚠ **FMP reports sub-penny
    #   opens** (measured: NVDA 2026-08-25 open = 211.025), and `Money` refuses
    #   more precision than the currency supports rather than rounding silently.
    #   ★ So the rounding is stated here, once, where it can be read: the
    #   decision anchor is a price you could transact at, and USD transacts in
    #   cents. HALF_UP is the convention every exchange quote already uses.
    from decimal import ROUND_HALF_UP, Decimal

    exact = Decimal(str(raw))
    cents = exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    money = Money.from_decimal_str(str(cents), "USD")
    return {"open_minor": money.amount_minor, "currency": money.currency,
            # ⚠ Kept beside the rounded value, never instead of it: the ratio
            #   arithmetic that needs full precision (DE-44's shape) must not
            #   silently pick up a quantized number.
            "open_exact": str(exact)}
