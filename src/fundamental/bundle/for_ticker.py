"""★★ `ticker + as_of` → `EvidenceBundle`. The assembler §5 always implied.

Every part constructor in `assemble.py` existed; **nothing built the parts from
real data.** The first live authoring run (MU, 2026-08-25) composed its bundle by
hand in a scratch script, which is why `RunContext.probed_thesis` stayed `None`
in every unattended run and DN-39 kept the card informational.

★ **RA-19 shapes this module exactly as it shapes `assemble`: the bundle is not
curated by the layer that judges.** Nothing here takes a hint, a preference or a
relevance score — the ticker and the `as_of` decide the whole content.

⚠ **DE-1 — everything through D-07.** This module never touches an API. It takes
a `DataEngine` and a D-02 panel and reads them; §3 lists both as D-01's
dependencies, and an external call here would be the ambient retrieval RA-1
forbids.
"""

from __future__ import annotations

from datetime import date

from src.fundamental.bundle.assemble import (
    assemble,
    computed,
    filing,
    observables,
    profile,
)
from src.fundamental.bundle.models import BundlePart
from src.fundamental.errors import BundleInconsistentError

#: ★ D-01's Class-B consumer identity (DE-6.9). ⚠ **Not a PIT consumer.**
#: `PIT_CONSUMERS` is `{training, backtest, inference}`, and `profile` is a
#: Class-B field set — so authoring under any of those names raises
#: `LiveReadDeniedError` and **no thesis could ever be written**. The rule is
#: written per-consumer because *"live consensus is genuinely useful on a report
#: today and genuinely poison in a training row"*: a thesis is the former. It is
#: a judgement made today about today, and it never becomes a training row.
D01_CONSUMER = "thesis"

#: ★★ **The profile fields a bundle may carry — an ALLOWLIST, never a denylist.**
#:
#: ⚠ **RA-14 is structural only if the anchors never enter a non-withheld part.**
#: `BLIND_WITHHELD_KINDS` strips `computed` and nothing else, so a `profile` part
#: reaches J-11 and J-15 — *exactly* the qualitative passes that are supposed to
#: run "with price, market cap and any valuation withheld". FMP's `profile`
#: response leads with `price`, `marketCap`, `beta`, `range`, `change` and
#: `lastDividend`: dumping it whole would defeat RA-14 while every test still
#: passed, because nothing checks a part's *content* against the rule.
#:
#: ★ An allowlist because **a denylist leaks whatever the vendor adds next.** A
#: new `impliedVolatility` key would arrive silently on the blind view; an
#: unknown key here is simply not carried.
PROFILE_FIELDS = (
    "companyName", "symbol", "sector", "industry", "country",
    "exchangeFullName", "currency", "ipoDate", "isEtf", "isFund",
    "isAdr", "fullTimeEmployees", "description", "ceo", "website",
)

#: ⚠ Present in the vendor payload and deliberately refused (RA-14). Named so
#: that a reader can see the strip was a decision, not an oversight — and so the
#: guard test has something to assert against.
PROFILE_ANCHORS_STRIPPED = (
    "price", "marketCap", "beta", "range", "change", "changePercentage",
    "lastDividend", "volume", "averageVolume", "dcf", "dcfDiff",
)

#: ★★ **Operating ratios a blind pass may see — an ALLOWLIST, and the default
#: is WITHHELD.**
#:
#: ⚠ **26 of `ratios-ttm`'s 62 keys are price-derived.** Handing the set over
#: whole would leak the anchor through `priceToEarningsRatioTTM` alone — a
#: reader with EPS and a P/E has the price, and **RA-14 is defeated without a
#: single price field appearing.**
#:
#: ★ The default must be *withheld*, not *shown*: wrongly withholding a quality
#: metric costs a slightly thinner bundle; wrongly exposing a multiple costs
#: RA-14. ⚠ And a keyword rule is not good enough — a substring probe for `ev`
#: classified `financialLeverageRatioTTM` as enterprise-value-derived. **Names
#: are enumerated because a heuristic over vendor field names silently
#: misclassifies in both directions.**
OPERATING_RATIOS = (
    "grossProfitMarginTTM", "operatingProfitMarginTTM", "netProfitMarginTTM",
    "ebitMarginTTM", "ebitdaMarginTTM", "pretaxProfitMarginTTM",
    "returnOnEquityTTM", "returnOnAssetsTTM", "returnOnCapitalEmployedTTM",
    "returnOnInvestedCapitalTTM",
    "currentRatioTTM", "quickRatioTTM", "cashRatioTTM",
    "debtToEquityRatioTTM", "debtToAssetsRatioTTM", "debtToCapitalRatioTTM",
    "interestCoverageRatioTTM", "debtServiceCoverageRatioTTM",
    "assetTurnoverTTM", "inventoryTurnoverTTM", "receivablesTurnoverTTM",
    "fixedAssetTurnoverTTM", "effectiveTaxRateTTM", "dividendPayoutRatioTTM",
    "researchAndDevelopementToRevenueTTM",
)

#: Field sets whose whole content is valuation. ⚠ These never reach a blind
#: pass — they go in as `computed`, which `BLIND_WITHHELD_KINDS` strips.
VALUATION_FIELD_SETS = ("key_metrics_ttm", "financial_scores")

#: Columns of CT-7.2 that are provenance rather than line items.
_PANEL_META = (
    "ticker", "period_start", "period_end", "period_type", "source",
    "accession_id", "filing_date", "ingested_at", "pit_guarantee",
    "restated", "quality_flags", "shares_outstanding",
)


def bundle_for(ticker: str, *, as_of: date, engine, panel=None, contract=None,
               periods: int = 4, consumer: str = D01_CONSUMER,
               valuation_assumptions=None):
    """The bundle for one `(ticker, as_of)` — ★ **deterministic (RA-4)**.

    `engine` is D-07's `DataEngine`; `panel` and `contract` are D-02's feature
    panel and the `FeatureContract` it was built under.

    ⚠ **Every read is PIT-filtered by `as_of` inside D-07**, so INV-1 is D-07's
    guarantee here rather than a filter this module reimplements — and
    `assemble` re-checks the assembled set for RA-3 regardless.
    """
    parts = [_filing_part(engine, ticker, as_of, periods=periods)]

    company = _profile_part(engine, ticker, as_of, consumer=consumer)
    if company is not None:
        parts.append(company)

    operating = _ratios_part(engine, ticker, as_of, consumer=consumer)
    if operating is not None:
        parts.append(operating)

    numbers = _computed_part(panel, ticker, as_of, contract,
                             engine=engine, consumer=consumer)
    if numbers is not None:
        parts.append(numbers)

    parts.append(observables(observable_fields(engine, ticker, as_of, contract)))

    # ★★ `F10` — Stage B's evidence. Opt-in: `None` keeps every existing bundle,
    #   and therefore every recorded `bundle_hash`, exactly as it was (`RA-2`).
    if valuation_assumptions is not None:
        from src.fundamental.bundle.assemble import valuation_part
        parts.append(valuation_part(ticker, as_of, engine=engine,
                                    assumptions=valuation_assumptions))
    return assemble(ticker=ticker, as_of=as_of, parts=parts)


def _filing_part(engine, ticker: str, as_of: date, *, periods: int):
    """The newest PIT-visible reported periods, rendered as line items.

    ★ Pinned by `accession_id` — the filing is immutable once published (CT-7.4),
    which is the whole reason §5 chose that pin over a date.

    ⚠ **An FMP-routed row carries `accession_id = None`** (CT-7.2), and a filing
    part that cannot be pinned cannot be hashed into a comparable bundle. That
    raises rather than substituting a date: *two runs with the same `bundle_hash`
    are comparable; two with different hashes are not* (RA-2), and a pin that can
    silently be `None` makes the hash claim untrue for an unknowable subset.
    """
    rows = engine.get_fundamentals(ticker, as_of=as_of)
    if rows is None or not len(rows):
        raise BundleInconsistentError(
            f"{ticker}: D-07 has no fundamentals visible at {as_of}. ★ A thesis "
            f"authored on an empty evidence set is the failure P5 exists for — "
            f"it would read as a judgement about a company rather than as the "
            f"absence of one (RA-1)")

    # ★★ **By `period_end`, not `filing_date`.** ⚠ *Found 2026-08-26 reading the
    #   first real bundle:* one EDGAR filing reports its own quarter **and the
    #   prior-year comparative**, so the most-recently-FILED rows included NVDA's
    #   quarter ending 2025-04-27 — a year stale — while the actual latest
    #   quarter sorted earlier. A model handed that reads a comparative as the
    #   current period, and every ratio it computes is a year out.
    #   `get_fundamentals` has already PIT-filtered on `filing_date`, so ordering
    #   by period costs no look-ahead protection (INV-1 stays D-07's).
    rows = rows.sort_values(["period_end", "filing_date"], kind="mergesort")
    rows = _drop_empty_periods(rows).tail(periods)
    if not len(rows):
        raise BundleInconsistentError(
            f"{ticker}: every PIT-visible period at {as_of} is empty of line "
            f"items. ★ An evidence part with no evidence in it reads to the "
            f"model as a company that reported nothing (RA-1, P5)")
    accession = rows["accession_id"].iloc[-1]
    if accession is None or str(accession) in ("", "nan", "None"):
        raise BundleInconsistentError(
            f"{ticker}: the newest PIT row has no accession_id — it is "
            f"FMP-routed (CT-7.2). ★ RA-2 says two runs with the same "
            f"bundle_hash are comparable; a pin that is None for an unknowable "
            f"subset makes that claim untrue, so this refuses rather than "
            f"substituting filing_date (DE-5.1, CLAUDE.md: EDGAR wins)")

    return filing(str(accession), _render_periods(rows))


def _missing(value) -> bool:
    """Null, NaN or pandas `NA` — ★ **without importing pandas** (RA-45).

    ⚠ `value != value` is the usual NaN idiom and it **raises** on pandas' `NA`
    ("boolean value of NA is ambiguous"), which is exactly what CT-7.2's
    nullable columns hand out. ★ D-01 may not import pandas at all: **arithmetic
    is D-02's** (RA-132), and the rule is structural so that it cannot be argued
    case by case — *"I only wanted `isna`"* is how it erodes.
    """
    if value is None:
        return True
    try:
        return bool(value != value)
    except TypeError:                     # pandas NA — an ambiguous truth IS missing
        return True


def _day(value) -> str:
    """A date, without the midnight timestamp pandas carries on `date32`."""
    return str(value)[:10]


def _line_item_columns(rows) -> list:
    return [c for c in rows.columns
            if c.endswith("_minor") and c not in _PANEL_META]


def _drop_empty_periods(rows):
    """Rows whose every line item is null carry nothing but a date.

    ★ **Not curation** (RA-19). Curation is choosing between things the model
    could have reasoned about; a period with no reported figure offers nothing to
    reason about, and spending four of the bundle's periods on them would push
    the ones that do carry figures out of the window entirely.
    """
    items = _line_item_columns(rows)
    if not items:
        return rows
    keep = [any(not _missing(row[c]) for c in items)
            for _index, row in rows.iterrows()]
    return rows[keep]


def _render_periods(rows) -> str:
    """CT-7.2 rows as text. ⚠ **`restated` is rendered, never smoothed** (DE-6.5).

    ★ A restated period that reads like an original is the defect AC-7.13 exists
    to surface — and a model told "revenue was X" for a figure that has since
    been revised is being lied to by its own evidence.
    """
    items = _line_item_columns(rows)
    lines = []
    for _index, row in rows.iterrows():
        flag = " [RESTATED]" if bool(row.get("restated")) else ""
        lines.append(
            f"{row['period_type']} ending {_day(row['period_end'])} "
            f"(filed {_day(row['filing_date'])}, {row['source']}){flag}")
        for column in sorted(items):
            value = row.get(column)
            # ⚠ `value != value` is the usual NaN idiom and it **raises** on
            #   pandas' `NA` — "boolean value of NA is ambiguous". CT-7.2's
            #   nullable columns hand out `NA`, not `float('nan')`.
            if _missing(value):
                continue
            currency = row.get(f"{column[:-len('_minor')]}_currency", "")
            lines.append(f"    {column[:-len('_minor')]}: "
                         f"{int(value) / 100:,.2f} {currency}".rstrip())
        shares = row.get("shares_outstanding")
        if not _missing(shares):
            lines.append(f"    shares_outstanding: {int(shares):,}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _profile_part(engine, ticker: str, as_of: date, *, consumer: str):
    """Identity and business description — ★ **anchors stripped** (RA-14).

    Returns `None` when D-07 has no observation, because a profile is context
    rather than evidence: its absence weakens a thesis, it does not invalidate
    one. ⚠ Contrast `_filing_part`, whose absence does.
    """
    try:
        observation = engine.get_observation(ticker, "profile", as_of=as_of,
                                             consumer=consumer)
    except Exception:                          # noqa: BLE001 — see the docstring
        return None
    fields = _observation_fields(observation)
    if not fields:
        return None

    kept = {k: v for k, v in fields.items()
            if k in PROFILE_FIELDS and v not in (None, "", 0)}
    if not kept:
        return None
    body = "\n".join(f"{k}: {v}" for k, v in sorted(kept.items()))
    return profile(as_of, body)


def _observation_fields(observation) -> dict:
    """The vendor payload, unwrapped.

    ⚠ `ObservationLedger.get()` returns an ENVELOPE — `{ticker, field_set,
    observed_at, source_endpoint, payload, content_hash}` — and the fields are
    nested under `payload`. ★ Reading the envelope as the payload finds no
    allowlisted key and returns `None`, so the part vanishes **exactly as it
    would if nothing had been captured**: a silent miss with data on disk.
    """
    if isinstance(observation, dict):
        inner = observation.get("payload")
        return inner if isinstance(inner, dict) else observation
    for attribute in ("fields", "values", "payload", "data"):
        value = getattr(observation, attribute, None)
        if isinstance(value, dict):
            return value
    return {}


def _ratios_part(engine, ticker: str, as_of: date, *, consumer: str):
    """Operating ratios — ★ **margins, returns, leverage and turnover only.**

    These carry no price, so a blind pass may reason over them: *"is this a good
    business?"* is exactly the question a margin answers and a multiple does
    not. ⚠ Everything price-derived is routed to `_computed_part` instead, where
    RA-14's withholding applies.
    """
    fields = _class_b(engine, ticker, as_of, "ratios_ttm", consumer)
    kept = {k: v for k, v in fields.items()
            if k in OPERATING_RATIOS and v is not None}
    if not kept:
        return None
    body = "\n".join(f"{k[:-3] if k.endswith('TTM') else k}: {v:.4g}"
                      if isinstance(v, (int, float)) else f"{k}: {v}"
                      for k, v in sorted(kept.items()))
    return BundlePart("operating_ratios",
                      {"contract_name": "ratios_ttm", "contract_version": 1},
                      "TRAILING TWELVE MONTH OPERATING RATIOS\n" + body)


def _class_b(engine, ticker: str, as_of: date, field_set: str, consumer: str):
    """One Class-B observation's payload, or `{}`. ⚠ Never raises — an absent
    observation is *legitimately absent* (EH-2), not a failure."""
    try:
        observation = engine.get_observation(ticker, field_set, as_of=as_of,
                                             consumer=consumer)
    except Exception:                          # noqa: BLE001 — see the docstring
        return {}
    return _observation_fields(observation) if observation else {}


def _computed_part(panel, ticker: str, as_of: date, contract,
                   *, engine=None, consumer: str = D01_CONSUMER):
    """D-02's numbers, pinned by the **contract** rather than by the values.

    ⚠ Withheld from the blind passes wholesale (`BLIND_WITHHELD_KINDS`), which
    is why the observable *vocabulary* had to become its own kind — RA-146.
    """
    # ★ Valuation goes here **because this kind is the one RA-14 strips.**
    #   `BLIND_WITHHELD_KINDS = ("computed",)`, so a multiple placed here is
    #   invisible to J-11 and J-15 and revealed only at reconciliation.
    valuation = []
    for field_set in VALUATION_FIELD_SETS:
        for key, value in sorted(_class_b(engine, ticker, as_of, field_set,
                                          consumer).items()):
            if isinstance(value, (int, float)) and key != "symbol":
                valuation.append(f"{key}={value:.6g}")

    if panel is None or contract is None or not len(panel):
        if valuation:
            return computed("class_b_valuation", 1, " ".join(valuation))
        return None
    rows = panel[(panel["ticker"] == ticker.upper())]
    if "date" in rows.columns:
        # ★ ISO strings compare in date order, so this needs no pandas dtype
        #   knowledge and no `Timestamp` (RA-45).
        cutoff = as_of.isoformat()
        rows = rows[[str(d)[:10] <= cutoff for d in rows["date"]]]
    if not len(rows):
        return None
    row = rows.iloc[-1]
    named = [f.name for f in contract.features]
    body = " ".join(f"{name}={row[name]:.6g}" for name in named
                    if name in row.index and not _missing(row[name]))
    if valuation:
        body = (body + " " if body else "") + " ".join(valuation)
    if not body:
        return None
    return computed(contract.name, contract.version, body)


def observable_fields(engine, ticker: str, as_of: date, contract) -> tuple:
    """★★ **The vocabulary a falsifier may name** (RA-35, RA-145, J-15).

    Two sources, and the second is why this is a function rather than a list:

    1. **D-02's contract features** — `mom_21`, `vol_21` today.
    2. **The PIT fundamental tags D-07 can re-read** — `revenue`, `grossProfit`
       and the rest of CT-7.2's line items.

    ⚠ **Without (2) a *fundamental* thesis could only be falsified by momentum
    and volatility**, because `b3_minimal` is the only contract D-02 publishes
    and it carries no ratios at all. ★ A statement tag qualifies under RA-35 on
    the same ground a feature does: it is re-readable at a future `as_of`, which
    is the entire test. *A falsifier the system cannot check is a sentence, not
    a condition.*
    """
    fields = set()
    if contract is not None:
        fields.update(f.name for f in contract.features)
    try:
        rows = engine.get_fundamentals(ticker, as_of=as_of)
    except Exception:                          # noqa: BLE001 — vocabulary only
        rows = None
    if rows is not None and len(rows):
        fields.update(c[: -len("_minor")] for c in rows.columns
                      if c.endswith("_minor") and c not in _PANEL_META)
    if not fields:
        raise BundleInconsistentError(
            f"{ticker}: no observable fields at {as_of}. ★ J-15 would be told to "
            f"choose from a supplied list and handed an empty one — the exact "
            f"defect RA-145 was written for, where four well-formed falsifiers "
            f"named no field and the thesis raised NoFalsifierError")
    return tuple(sorted(fields))
