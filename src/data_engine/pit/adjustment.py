"""Price adjustment as restatement — DE-27…DE-30, DE-42…DE-45 (§5C.7).

```
THE SAME QUERY, FOR THE SAME PAST DATES, RETURNS DIFFERENT NUMBERS
DEPENDING ON WHEN YOU ASK.

A backtest run on 2024-06-01 saw NVDA at $1,150. The same backtest, same
code, same config, same date range, re-run today sees $115. The config did
not change. The code did not change. THE INPUT DATA CHANGED UNDERNEATH,
silently, on a vendor's schedule, for dates already in the past.
```

★ **The hazard is constitution INV-2 determinism, not classical look-ahead**, and
the obvious reading gets this backwards. Split adjustment is *necessary* —
returns on the raw series would show a fake −90 % on 2024-06-10 — and most quant
features are scale-invariant, so adjusted is correct for them and nothing leaks.
What breaks is reproducibility.

The fix is the pattern §6 already uses: keep the **raw** series plus the
**events** as the system of record, and derive the adjusted panel **at an
`adj_as_of`** (DE-27, DE-28). Immutable observations plus the events that
transform them — the Fact ledger, applied to prices.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from src.data_engine.contracts.panels import validate_price_panel
from src.data_engine.contracts.schema import as_date32, as_utc_timestamp
from src.data_engine.errors import AdjAsOfRequiredError, ContractViolationError
from src.data_engine.pit.models import utcnow

#: Sentinel distinguishing "adj_as_of was not passed" from "adj_as_of is None,
#: meaning RAW". DE-45: `None` is the explicit raw value; omission raises.
UNSET = object()

#: DE-42's factor is a float. Rounding minor units half-up (rather than numpy's
#: banker's default) keeps 0.5 deterministic in one direction, which is what
#: INV-2 needs — the direction itself is arbitrary, the consistency is not.
def _round_half_up(values: np.ndarray) -> np.ndarray:
    return np.floor(np.asarray(values, dtype="float64") + 0.5).astype("int64")


def split_multiplier(numerator: float, denominator: float) -> float:
    """The factor a split contributes to dates BEFORE its effective date.

    NVDA 10:1 -> numerator=10, denominator=1 -> 0.1: every pre-split price is
    divided by ten. A *reverse* split (denominator > numerator) gives a
    multiplier above one, which is the case that makes a $0.50 stock look like
    $10 retroactively — an M-1 mandate-compliance hazard, not merely a modelling
    one (DE-29).
    """
    if numerator <= 0 or denominator <= 0:
        raise ContractViolationError(
            "split event", f"numerator={numerator}, denominator={denominator} — a "
            f"non-positive split ratio cannot produce a usable factor"
        )
    return float(denominator) / float(numerator)


def dividend_multiplier(cash, prior_close_minor: int) -> float:
    """The factor a cash dividend contributes to dates BEFORE its ex-date.

    ⚠ **DE-44.** The reference close is the session BEFORE the ex-date, and the
    factor applies to dates strictly before the ex-date. That is the whole
    content of the rule: the ex-date *open already reflects the drop* in the raw
    price, so including the dividend in the ex-date's own factor double-counts
    it. DE-43's monotonicity test passes either convention, which is why this
    needs its own assertion (AC-7.59).
    """
    if prior_close_minor <= 0:
        raise ContractViolationError(
            "dividend event",
            f"prior close {prior_close_minor} is not positive, so the dividend "
            f"factor cannot be computed — it is not 1.0 and it is not 0 (DE-14)",
        )
    # `cash` is MINOR units either way: an int (cent-quantized) or a decimal
    # string carrying the vendor's sub-cent precision. One quantity, two
    # precisions — never two units (CN-8).
    minor = float(cash)
    if minor < 0:
        raise ContractViolationError("dividend event", f"negative dividend {cash!r}")
    return 1.0 - (minor / float(prior_close_minor))


def adjustment_factors(
    dates: pd.Series, events: list, adj_as_of: date, prior_close, ticker: str,
) -> np.ndarray:
    """DE-28 / DE-42 — the cumulative factor in effect at `adj_as_of`, per date.

    Only events with ``event_date <= adj_as_of`` contribute, and each contributes
    to dates ``< event_date``. A backtest as of 2024-06-01 therefore sees $1,150
    and re-running it next year still sees $1,150.

    Events are applied in a fixed ascending order. Float multiplication is not
    associative, so an arbitrary order would make the factor depend on the order
    the vendor happened to return events in — INV-2 lost to something nobody
    would ever look for (PD-20).
    """
    factors = np.ones(len(dates), dtype="float64")
    day = pd.to_datetime(dates).to_numpy()

    usable = sorted(
        (e for e in events if e.event_date <= adj_as_of),
        key=lambda e: (e.event_date, e.event_type, str(e.detail)),
    )
    first = day.min() if len(day) else None
    for event in usable:
        cut = np.datetime64(pd.Timestamp(event.event_date))
        # An event at or before the panel's first row adjusts no row in it, so
        # its factor is never applied. ⚠ Skipping it BEFORE pricing it matters:
        # a dividend from 2012 has no prior close inside a 2024 window, and
        # computing one would raise for an event that changes nothing.
        if first is not None and cut <= first:
            continue
        if event.event_type == "split":
            m = split_multiplier(event.detail["numerator"], event.detail["denominator"])
        elif event.event_type == "dividend":
            ref = prior_close(ticker, event.event_date)
            if ref is None:
                # DE-14: unknown is not 1.0. Without the prior close there is no
                # honest factor, and a silent 1.0 would understate every price
                # before the ex-date by exactly the dividend.
                raise ContractViolationError(
                    "dividend event",
                    f"{ticker}: no raw close before ex-date {event.event_date}, so the "
                    f"DE-44 factor is uncomputable. It is not 1.0",
                )
            # ★ Prefer the vendor's exact decimal over the cent-quantized
            # amount: the factor is a ratio, so sub-cent precision survives the
            # division and is thrown away by rounding first. See
            # `src/fmp/prices.py::_dividend_amount`.
            m = dividend_multiplier(
                event.detail.get("cash_exact", event.detail["cash_minor"]), ref)
        else:
            continue
        factors[day < cut] *= m
    return factors


def price_event_conflicts(raw: pd.DataFrame, events, adj_as_of) -> dict:
    """DE-79 / AC-7.97 — `{ticker: reason}` where the events contradict the prices.

    ★ A dividend at or above the prior close gives a factor ≤ 0 — impossible —
    and a dividend with no prior close inside the window has no honest factor.
    Both mean the vendor's events and its prices are in different units or
    histories. ⚠ Named so the consumer can refuse the NAME; never repaired by a
    guessed factor or a dropped event. *Found 2026-10-08:* KDP — FMP prices the
    pre-merger history in post-merger units (≈ $19.91) while its 2018-07-10
    special dividend is in pre-merger units ($103.75).
    """
    out = {}
    if raw is None or not len(raw):
        return out
    frame = raw.copy()
    frame["ticker"] = frame["ticker"].str.upper()
    frame["date"] = pd.to_datetime(frame["date"])
    by_ticker = {t: g.sort_values("date") for t, g in frame.groupby("ticker", sort=True)}
    for event in events:
        if event.event_type != "dividend" or event.event_date > adj_as_of:
            continue
        grp = by_ticker.get(event.ticker.upper())
        if grp is None or not len(grp):
            continue
        cut = pd.Timestamp(event.event_date)
        if cut <= grp["date"].iloc[0]:
            continue                                   # adjusts no row in the window
        before = grp[grp["date"] < cut]
        cash = float(event.detail.get("cash_exact", event.detail["cash_minor"]))
        if not len(before):
            out.setdefault(event.ticker.upper(),
                           f"dividend {cash / 100:.2f} on {event.event_date} has no prior close")
            continue
        ref = float(before["close_minor"].iloc[-1])
        if cash >= ref:
            out.setdefault(event.ticker.upper(),
                           f"dividend {cash / 100:.2f} on {event.event_date} ≥ prior close "
                           f"{ref / 100:.2f} — the events and the prices are in different "
                           f"units or histories (DE-79)")
    return out


def build_price_panel(raw: pd.DataFrame, events, adj_as_of=UNSET) -> pd.DataFrame:
    """CT-7.1 from the raw series plus the events (DE-27, DE-45, AC-7.43/44/46).

    `adj_as_of=None` returns the RAW panel: ``adj_factor = 1.0``,
    ``is_adjusted = False``, ``adj_as_of = NaT``, and the ``adj_*`` columns equal
    their raw counterparts. That is not a degenerate case to be tolerated — it is
    the series DE-29's non-scale-invariant consumers are required to use, so it
    has to be a first-class result rather than a flag someone forgets.

    ⚠ `volume` is **always raw, in both modes**, and CT-7.1 declares no
    `adj_volume`. Dollar volume is therefore ``close_minor x volume`` (raw x raw)
    and never ``adj_close x volume``, which would be wrong by the split factor.
    Recorded here because the contract's silence is the kind a reader fills in
    with the wrong guess.
    """
    if adj_as_of is UNSET:
        raise AdjAsOfRequiredError("build_price_panel")

    required = {"ticker", "date", "open_minor", "high_minor", "low_minor",
                "close_minor", "volume", "currency", "source"}
    missing = sorted(required - set(raw.columns))
    if missing:
        raise ContractViolationError("raw price series", f"missing {missing}")

    df = raw.copy()                                    # PD-14 — never mutate the caller's
    df["ticker"] = df["ticker"].str.upper()            # DE-7
    df["date"] = as_date32(df["date"])
    df = df.sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)

    closes = {(t, d.date()): int(c) for t, d, c
              in zip(df["ticker"], df["date"], df["close_minor"])}
    sessions_by_ticker = {t: sorted(d.date() for d in g["date"])
                          for t, g in df.groupby("ticker", sort=True)}

    def prior_close(ticker: str, on: date):
        earlier = [s for s in sessions_by_ticker.get(ticker, []) if s < on]
        return closes[(ticker, earlier[-1])] if earlier else None

    # Assigned by positional index per group rather than by concatenating in
    # groupby order: the two happen to agree today because the frame is sorted
    # by (ticker, date), and a future sort change would misalign every factor
    # silently. PD-12 — never rely on positional alignment across objects.
    df["adj_factor"] = np.ones(len(df), dtype="float64")
    for ticker, grp in df.groupby("ticker", sort=True):
        if adj_as_of is None:
            continue
        evs = [e for e in events if e.ticker.upper() == ticker]
        df.loc[grp.index, "adj_factor"] = adjustment_factors(
            grp["date"], evs, adj_as_of, prior_close, ticker
        )

    # DE-42: every adjusted field is raw x adj_factor, from the SAME factor.
    df["adj_close_minor"] = _round_half_up(df["close_minor"] * df["adj_factor"])
    df["adj_open_minor"] = _round_half_up(df["open_minor"] * df["adj_factor"])

    currency = df.pop("currency")
    for base in ("open", "high", "low", "close", "adj_close", "adj_open"):
        df[f"{base}_currency"] = currency

    df["is_adjusted"] = adj_as_of is not None
    df["adj_as_of"] = as_date32(
        pd.Series([adj_as_of] * len(df), index=df.index, dtype="object")
    )
    if "fetched_at" not in df.columns:
        df["fetched_at"] = utcnow()
    df["fetched_at"] = as_utc_timestamp(df["fetched_at"])
    df["volume"] = df["volume"].astype("int64")

    from src.data_engine.contracts.panels import PRICE_PANEL
    return validate_price_panel(df[list(PRICE_PANEL.names)].reset_index(drop=True))


# --------------------------------------------------------------------------- #
# The three assertions — DE-43, DE-44 (AC-7.58, AC-7.59)
# --------------------------------------------------------------------------- #

def assert_factor_discipline(panel: pd.DataFrame, event_dates) -> None:
    """DE-43 / QA-85 — strictly positive, and changing only on flagged dates.

    ⚠ **`adj_close/close == adj_open/open` is a TAUTOLOGY against a
    reconstruction** and tests nothing about it (QA-85), because both sides are
    built from the same materialised factor. That is precisely why the real
    check is this one: the factor may change only on a date the calendar check
    flagged (§6A), so an adjustment appearing on an ordinary Tuesday is a defect
    the tautology would never see.
    """
    if (panel["adj_factor"] <= 0).any():
        raise ContractViolationError("CT-7.1", "adj_factor must be strictly positive (DE-43)")

    flagged = {pd.Timestamp(d) for d in event_dates}
    for ticker, grp in panel.groupby("ticker", sort=True):
        g = grp.sort_values("date", kind="mergesort")
        changed = g["adj_factor"].ne(g["adj_factor"].shift())
        changed.iloc[0] = False                       # the first row starts, it does not change
        stray = [d for d, ch in zip(g["date"], changed) if ch and d not in flagged]
        if stray:
            raise ContractViolationError(
                "CT-7.1",
                f"{ticker}: adj_factor changes on {[str(d.date()) for d in stray[:5]]}, "
                f"which the calendar check did not flag. An adjustment with no "
                f"corporate action behind it is a vendor artifact, not a factor "
                f"(DE-43, QA-85)",
            )


def assert_ex_dividend_convention(panel: pd.DataFrame, dividends) -> None:
    """DE-44 / QA-91 / AC-7.59 — the ex-date must NOT carry its own dividend factor.

    ★ THE FAILURE THIS CATCHES, IN ONE LINE: the ex-date open already reflects
    the drop, so a close-derived factor applied to the ex-date itself subtracts
    the dividend twice.

    The check compares the factor on the ex-date with the factor on the session
    before it. Their ratio must be exactly the dividend multiplier — meaning the
    step happened *between* those two sessions and not after.
    """
    for div in dividends:
        ticker = div.ticker.upper()
        grp = panel[panel["ticker"] == ticker].sort_values("date", kind="mergesort")
        if not len(grp):
            continue
        ex = pd.Timestamp(div.event_date)
        on_or_after = grp[grp["date"] >= ex]
        before = grp[grp["date"] < ex]
        if not len(on_or_after) or not len(before):
            continue
        f_ex = float(on_or_after.iloc[0]["adj_factor"])
        prev = before.iloc[-1]
        f_prev = float(prev["adj_factor"])
        expected = dividend_multiplier(div.detail["cash_minor"], int(prev["close_minor"]))
        if not np.isclose(f_prev, f_ex * expected, rtol=1e-9, atol=0.0):
            raise ContractViolationError(
                "CT-7.1",
                f"{ticker} ex-date {div.event_date}: factor steps from {f_prev} to "
                f"{f_ex}, expected ratio {expected}. A close-derived factor applied "
                f"to the ex-date itself double-counts the drop already present in "
                f"the raw open (DE-44, QA-91)",
            )


def assert_matches_vendor(
    panel: pd.DataFrame, vendor: pd.DataFrame, *, column: str = "adj_open_minor",
    tolerance_minor: int = 1,
) -> None:
    """DE-43's other half — compare the reconstruction against the vendor's own.

    Where FMP supplies an adjusted open, this is the only check that is not
    self-referential. `tolerance_minor` defaults to one cent: the vendor rounds
    its own way, and demanding bit-equality would fail on rounding rather than
    on adjustment.
    """
    merged = panel.merge(vendor, on=["ticker", "date"], how="inner",
                         suffixes=("", "_vendor"), validate="one_to_one")
    if not len(merged):
        raise ContractViolationError(
            "CT-7.1", "no overlapping (ticker, date) rows to compare against the vendor"
        )
    delta = (merged[column] - merged[f"{column}_vendor"]).abs()
    bad = merged[delta > tolerance_minor]
    if len(bad):
        row = bad.iloc[0]
        raise ContractViolationError(
            "CT-7.1",
            f"{len(bad)} row(s) disagree with the vendor beyond {tolerance_minor} "
            f"minor unit(s); first {row['ticker']} {row['date'].date()}: "
            f"ours {row[column]} vs vendor {row[f'{column}_vendor']} (DE-43)",
        )
