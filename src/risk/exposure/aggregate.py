"""D-05 §5 — exposure on five dimensions. RK-1…RK-7, RK-37.

★ **RK-1: name · sector · theme · currency · account.** *Any one alone
understates a concentrated book.*

⚠ **RK-2: every threshold in L0 §8 is a REPORTING threshold.** Crossing one
emits a LEVEL 2 ALERT and **changes nothing else** (INV-023, INV-026) — the
existing code already says it in words: *"tracked, not blocked — concentration
is intentional"*.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.risk.contracts.theme import UNCLASSIFIED, ThemeTaxonomy
from src.risk.errors import FxUnavailableError, NoTaxonomyError, NotAggregatedError

#: L0 §8 — reporting thresholds, every one of them (RK-2).
CONCENTRATION_THRESHOLD_PCT = 25.0
SECTOR_MAX_PCT = 35.0
THEME_REPORT_THRESHOLD_PCT = 40.0

#: ⚠ There is no other value. `effect` is on the contract so that CT-5.1 states
#: no other exists (INV-026).
REPORTED_ONLY = "reported_only"
ALERT_LEVEL_2 = 2

#: RK-36 / DE-35 — ★ **`UNCHECKED` is a first-class result, distinct from "no
#: risk found".** An exposure that could not be computed must never render as
#: zero: **zero theme exposure and unmeasured theme exposure are opposite
#: findings and would look identical.**
UNCHECKED = "UNCHECKED"

DIMENSIONS = ("by_name", "by_sector", "by_theme", "by_currency", "by_account")


@dataclass(frozen=True, slots=True)
class ThresholdCrossing:
    name: str
    limit: float
    value: float
    subject: str = ""
    effect: str = REPORTED_ONLY
    alert_level: int = ALERT_LEVEL_2

    def __post_init__(self) -> None:
        if self.effect != REPORTED_ONLY:
            from src.risk.errors import BlockAttemptedError
            raise BlockAttemptedError(
                f"threshold {self.name!r} with effect={self.effect!r} — every "
                f"threshold in L0 §8 is a REPORTING threshold (RK-2, INV-026)")

    def to_json_obj(self) -> dict:
        return {"name": self.name, "limit": self.limit, "value": self.value,
                "subject": self.subject, "effect": self.effect,
                "alert_level": self.alert_level}


@dataclass(frozen=True, slots=True)
class ExposureView:
    """The five dimensions, in base currency, with the RESP exclusion stated."""

    as_of: date
    base_currency: str
    by_name: dict
    by_sector: dict
    by_theme: dict
    by_currency: dict
    by_account: dict
    total_base: float
    #: ★ RC-4 / AC-5.5 — **stated, not assumed.**
    resp_excluded: bool = True
    excluded_accounts: tuple[str, ...] = ()
    taxonomy_version: str = ""

    def to_json_obj(self) -> dict:
        return {"as_of": self.as_of.isoformat(),
                "base_currency": self.base_currency,
                "by_name": dict(self.by_name), "by_sector": dict(self.by_sector),
                "by_theme": dict(self.by_theme),
                "by_currency": dict(self.by_currency),
                "by_account": dict(self.by_account),
                "total_base": self.total_base,
                "resp_excluded": self.resp_excluded,
                "excluded_accounts": list(self.excluded_accounts),
                "taxonomy_version": self.taxonomy_version}


def _to_base(position, book, base_currency: str) -> float:
    if position.currency == base_currency:
        return float(position.market_value)
    rate = book.fx_rate_used.get(position.currency)
    if rate is None:
        # ★ RK-3/FX-3 — unavailable, never estimated.
        raise FxUnavailableError(book.account_id, position.currency)
    return float(position.market_value) * float(rate)


def exposure(books, *, as_of: date, taxonomy: ThemeTaxonomy,
             base_currency: str = "CAD") -> ExposureView:
    """RK-1…RK-7 — the aggregation, over the fund's books only.

    ⚠ **RK-5 is applied here, not left to the caller**: positions are keyed on
    `analysis_symbol`, so a CDR and its underlying land on one line by
    construction rather than by a caller remembering to merge them.
    """
    if taxonomy is None:
        raise NoTaxonomyError(
            "exposure was asked for a theme breakdown with no taxonomy")

    by_name, by_sector, by_theme, by_currency, by_account = {}, {}, {}, {}, {}
    instruments_by_symbol: dict = {}
    excluded, total = [], 0.0

    for book in books:
        if not book.in_fund:                       # RC-4 — stated below
            excluded.append(book.account_id)
            continue
        for position in book.positions:
            value = _to_base(position, book, base_currency)
            total += value
            symbol = position.analysis_symbol
            instruments_by_symbol.setdefault(symbol, set()).add(
                position.instrument_id)
            by_name[symbol] = by_name.get(symbol, 0.0) + value
            by_sector[position.sector or "unclassified"] = (
                by_sector.get(position.sector or "unclassified", 0.0) + value)
            theme = taxonomy.resolve(symbol=symbol, sector=position.sector)
            by_theme[theme] = by_theme.get(theme, 0.0) + value
            by_currency[position.currency] = (
                by_currency.get(position.currency, 0.0) + value)
            by_account[book.account_id] = (
                by_account.get(book.account_id, 0.0) + value)

    pct = (lambda d: {k: round(100.0 * v / total, 4) for k, v in sorted(d.items())}
           if total else (lambda d: {k: 0.0 for k in sorted(d)}))
    return ExposureView(
        as_of=as_of, base_currency=base_currency,
        by_name=pct(by_name), by_sector=pct(by_sector), by_theme=pct(by_theme),
        by_currency=pct(by_currency), by_account=pct(by_account),
        total_base=total, resp_excluded=True,
        excluded_accounts=tuple(sorted(excluded)),
        taxonomy_version=taxonomy.taxonomy_version)


def assert_aggregated(view: ExposureView, books) -> None:
    """RK-5 / AC-5.3 — one line per company, however many lots hold it."""
    seen: dict = {}
    for book in books:
        for position in book.positions:
            seen.setdefault(position.analysis_symbol, set()).add(
                position.instrument_id)
    for symbol, instruments in seen.items():
        if len(instruments) > 1 and symbol not in view.by_name:
            raise NotAggregatedError(symbol, instruments)


def thresholds_crossed(view: ExposureView) -> tuple[ThresholdCrossing, ...]:
    """RK-2 — crossing one emits a LEVEL 2 ALERT and **changes nothing else**."""
    crossings = []
    for name, weight in view.by_name.items():
        if weight > CONCENTRATION_THRESHOLD_PCT:
            crossings.append(ThresholdCrossing(
                "CONCENTRATION_THRESHOLD_PCT", CONCENTRATION_THRESHOLD_PCT,
                weight, subject=name))
    for sector, weight in view.by_sector.items():
        if weight > SECTOR_MAX_PCT:
            crossings.append(ThresholdCrossing(
                "SECTOR_MAX_PCT", SECTOR_MAX_PCT, weight, subject=sector))
    for theme, weight in view.by_theme.items():
        if theme == UNCLASSIFIED:
            continue          # RK-7 — reported in the residual, not thresholded
        if weight > THEME_REPORT_THRESHOLD_PCT:
            crossings.append(ThresholdCrossing(
                "THEME_REPORT_THRESHOLD_PCT", THEME_REPORT_THRESHOLD_PCT,
                weight, subject=theme))
    return tuple(crossings)
