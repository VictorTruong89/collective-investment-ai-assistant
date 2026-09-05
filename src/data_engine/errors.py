"""D-07 error family — the §10 catalog made raisable (L4 §5.3, EH-10, EH-13).

Every ERROR-severity row of `L1-data-engine.md` §10 is a class here; every
WARNING-severity row is a code in :data:`WARNING_CODES`. The split is not
cosmetic:

    ERROR   → the caller asked for something the system should have been able
              to do. It raises (EH-1, EH-9).
    WARNING → a reportable state. It is recorded and travels with the artifact
              — never raised, and never silently dropped either.

★ WHY THE CODE LIVES ON THE EXCEPTION AND NOT ONLY IN THE MESSAGE (EH-13).
A message is for a human reading a traceback; a code is for the run record,
which is the only thing that survives to be counted. `DATA.PROBE.SKIPPED`
appearing zero times in a month of run records is a fact about the probe
(DE-40); the same words inside a log line are not.

⚠ `PointInTimeError` is deliberately its own branch and `LiveReadDeniedError`
deliberately sits under it (EH-12). INV-1 is invisible in every metric this
system computes, so a look-ahead must not be catchable by accident inside a
broad ``except DataError``. Serving a Class-B field live to a training consumer
(DE-6.9) *is* a look-ahead — it just arrives through a different door.
"""

from __future__ import annotations

from src.shared.errors import PipelineError


class DataError(PipelineError):
    """Base for D-07. Code: ``DATA.*``.

    `retryable` is a class attribute rather than a constructor argument so the
    default is a property of the *class* (EH-15: an untagged class is not
    retryable). D-08 reads it; D-07 never acts on it.
    """

    code = "DATA.UNSPECIFIED"
    retryable = False


# --------------------------------------------------------------------------- #
# DATA.SOURCE.* — acquisition
# --------------------------------------------------------------------------- #

class SourceError(DataError):
    """Base for acquisition failures."""

    code = "DATA.SOURCE.UNSPECIFIED"


class NoCikError(SourceError):
    """DATA.SOURCE.NO_CIK — a universe ticker has no CIK (DE-13).

    ⚠ Inherited from a real incident: a LEFT JOIN silently dropped 7 of the 13
    watchlist tickers from the training panel, and they were scored with all 47
    fundamental features NaN. Nothing said so. That is why this raises rather
    than returning an empty row.
    """

    code = "DATA.SOURCE.NO_CIK"

    def __init__(self, ticker: str) -> None:
        super().__init__(
            f"universe ticker {ticker!r} resolves to no CIK — the run fails rather "
            f"than dropping it, because a dropped ticker becomes a row of NaNs that "
            f"still gets scored (DE-13)"
        )
        self.ticker = ticker


class NoFundamentalSourceError(SourceError):
    """DATA.SOURCE.NO_FUNDAMENTALS — neither EDGAR nor FMP has the ticker (§5.1 case C)."""

    code = "DATA.SOURCE.NO_FUNDAMENTALS"

    def __init__(self, ticker: str, tried) -> None:
        super().__init__(
            f"no fundamental source for {ticker!r} — tried {sorted(tried)}. "
            f"§5.1 case C is fail-loud: a universe ticker with no source is an error, "
            f"never a silent NaN row"
        )
        self.ticker = ticker


class SourceUnavailableError(SourceError):
    """DATA.SOURCE.UNAVAILABLE — the source is unreachable after retries.

    Retryable: this is the transport failure D-08's policy exists for (EH-15).
    """

    code = "DATA.SOURCE.UNAVAILABLE"
    retryable = True

    def __init__(self, endpoint: str, detail: str) -> None:
        super().__init__(f"source unreachable: {endpoint} — {detail}")
        self.endpoint = endpoint


class PlanGatedError(SourceError):
    """DATA.SOURCE.PLAN_GATED — a persistent 402 (DE-15, DE-46, AC-7.32).

    ★ The parameters are half of what was refused, and the attempt count is the
    evidence that this is cause 1 or 2 rather than cause 3 (§5A.2). Both are on
    the exception because both have to reach the run record — that is how DE-46
    answers EH-14 rather than waiving it.

    ⚠ It is NEVER converted into an empty result. Had ingest done that, D-02
    would have lost every key metric and every ratio for the whole universe and
    the frame downstream would have looked like a clean empty result.
    """

    code = "DATA.SOURCE.PLAN_GATED"

    def __init__(self, endpoint: str, params: dict, attempts: int) -> None:
        super().__init__(
            f"402 from {endpoint} with params {params!r} after {attempts} attempt(s) "
            f"— the parameter is half of what was refused (DE-15). A 402 is never "
            f"read as 'no data': §5A.2 gives it three causes and the status code "
            f"does not say which"
        )
        self.endpoint, self.params, self.attempts = endpoint, params, attempts


class PlanGateRejected(SourceError):
    """DE-16 / AC-7.33 — a known-gated parameter combination, refused before sending.

    Not a transport failure at all: the call is rejected at the client boundary,
    so it never leaves the process. Sending it and handling the 402 would work
    and would also burn a request against the rate cap for an answer already
    known.
    """

    code = "DATA.SOURCE.PLAN_GATED"

    def __init__(self, endpoint: str, params: dict, reason: str) -> None:
        super().__init__(
            f"{endpoint} with {params!r} is plan-gated on Starter ({reason}) and is "
            f"rejected at the client boundary rather than sent and failed (DE-16)"
        )
        self.endpoint, self.params = endpoint, params


# --------------------------------------------------------------------------- #
# DATA.CONTRACT.* — shape
# --------------------------------------------------------------------------- #

class ContractViolationError(DataError):
    """DATA.CONTRACT.* — schema, dtype or units.

    Never retryable (EH-15): re-sending an identical request cannot change the
    shape of the answer.
    """

    code = "DATA.CONTRACT.VIOLATION"

    def __init__(self, contract: str, detail: str) -> None:
        super().__init__(f"{contract}: {detail}")
        self.contract = contract


class MissingCurrencyError(ContractViolationError):
    """DATA.CONTRACT.MISSING_CURRENCY — a `*_minor` with no `*_currency` sibling."""

    code = "DATA.CONTRACT.MISSING_CURRENCY"

    def __init__(self, contract: str, field: str) -> None:
        super().__init__(
            contract,
            f"{field}_minor has no {field}_currency sibling. A minor amount with no "
            f"currency is the untagged number INV-001 exists to forbid (CT-M.1)",
        )


# --------------------------------------------------------------------------- #
# DATA.PIT.* — the domain's reason to exist
# --------------------------------------------------------------------------- #

class PointInTimeError(DataError):
    """DATA.PIT.* — ★ INV-1. A look-ahead was detected or made possible.

    ⚠ EH-12: its own class precisely so a broad ``except DataError`` around an
    ingest cannot swallow it. INV-1 is invisible in every metric the system
    computes — the numbers look right and the model looks good.
    """

    code = "DATA.PIT.VIOLATION"


class NoFilingDateError(PointInTimeError):
    """DATA.PIT.NO_FILING_DATE — a Fact rejected at ingest (DE-6.3, AC-7.9)."""

    code = "DATA.PIT.NO_FILING_DATE"

    def __init__(self, ticker: str, tag: str, period_end) -> None:
        super().__init__(
            f"Fact {ticker}/{tag}/{period_end} has no filing_date and is rejected at "
            f"ingest. It cannot be placed in time, so it could never be safely served "
            f"— the as-of filter runs on this axis (DE-6.3)"
        )


class AsOfRequiredError(PointInTimeError):
    """DATA.PIT.AS_OF_REQUIRED — as_of omitted on a PIT path (DE-6.4, AC-7.10).

    ★ The rule most likely to be eroded. ``as_of=None → today`` is convenient at
    every call site and silently correct in production, where today *is* the
    as-of. It is silently wrong in every backtest and every training run.
    """

    code = "DATA.PIT.AS_OF_REQUIRED"

    def __init__(self, method: str) -> None:
        super().__init__(
            f"{method} requires an explicit as_of. A defaulted as_of is look-ahead "
            f"with a convenient signature (DE-6.4) — it is right in production and "
            f"wrong in every backtest, and the failure is invisible either way"
        )


class DerivedNoFilingDateError(PointInTimeError):
    """DATA.PIT.NO_FILING_DATE_DERIVED — a derived periodic with nothing to inherit (DE-22)."""

    code = "DATA.PIT.NO_FILING_DATE_DERIVED"

    def __init__(self, ticker: str, period_end, period_type: str, kind: str) -> None:
        super().__init__(
            f"derived periodic {kind} for {ticker}/{period_end}/{period_type} has no "
            f"filing date and no statement row to inherit acceptedDate from, so it "
            f"cannot be placed in time and is not served PIT (DE-22)"
        )


class LiveReadDeniedError(PointInTimeError):
    """DATA.OBSERVATION.LIVE_READ_DENIED — Class-B served live to D-04 (DE-6.9, AC-7.26).

    ⚠ A PointInTimeError by inheritance and on purpose. `analyst-estimates` has
    a `date` field; it is the FORECAST target period, not the publication date.
    Joining it to a 2024 training row gives the model a 2026 opinion about 2027
    and calls it a 2024 feature. That is INV-1 arriving through a different door.
    """

    code = "DATA.OBSERVATION.LIVE_READ_DENIED"

    def __init__(self, field_set: str, consumer: str) -> None:
        super().__init__(
            f"Class-B field_set {field_set!r} may not be read live by a {consumer!r} "
            f"consumer — it has no publication axis of its own, so the only legal path "
            f"is the CT-7.6 observation ledger at an as_of (DE-6.9)"
        )
        self.field_set, self.consumer = field_set, consumer


# --------------------------------------------------------------------------- #
# DATA.PRICE.* — adjustment is restatement (§5C.7)
# --------------------------------------------------------------------------- #

class AdjAsOfRequiredError(DataError):
    """DATA.PRICE.ADJ_AS_OF_REQUIRED — an adjusted panel with no adj_as_of (DE-28, DE-45).

    ★ The same defect shape as AsOfRequiredError, one axis over. A backtest run
    on 2024-06-01 saw NVDA at $1,150; the same backtest re-run today sees $115.
    Same code, same config, same dates — the input changed underneath, on a
    vendor's schedule, for dates already past. That is constitution INV-2.
    """

    code = "DATA.PRICE.ADJ_AS_OF_REQUIRED"

    def __init__(self, method: str) -> None:
        super().__init__(
            f"{method} requires an explicit adj_as_of; pass None to mean the RAW "
            f"series (DE-45). A default adjustment is DE-6.4's defaulted as_of "
            f"wearing a different name, and it breaks INV-2 rather than INV-1"
        )


class RawRequiredError(DataError):
    """DATA.PRICE.RAW_REQUIRED — a non-scale-invariant consumer read the adjusted panel (DE-29).

    ⚠ **M-1 is a mandate rule, so this is a compliance defect and not only a
    modelling one.** Applied to an adjusted history, a *reverse* split makes a
    stock that traded at $0.50 look like $10 retroactively — so a penny-stock
    filter run over adjusted prices silently admits names that were penny stocks
    at the time.
    """

    code = "DATA.PRICE.RAW_REQUIRED"

    def __init__(self, use: str) -> None:
        super().__init__(
            f"{use} is not scale-invariant and must be computed on the RAW series "
            f"(DE-29). Absolute price and volume thresholds, share counts and the M-1 "
            f"penny-stock screen all shift by the split factor on an adjusted panel"
        )
        self.use = use


# --------------------------------------------------------------------------- #
# DATA.CALENDAR.* — the pre-run gate (§6A)
# --------------------------------------------------------------------------- #

class CalendarError(DataError):
    code = "DATA.CALENDAR.ERROR"


class UnhandledBlockError(CalendarError):
    """DATA.CALENDAR.UNHANDLED_BLOCK — halts the run, names tickers AND events (DE-32).

    ⚠ A blocking ticker is never silently dropped. Dropping is the D-17 defect,
    where 7 of 13 watchlist names were scored on NaNs and nothing said so.
    """

    code = "DATA.CALENDAR.UNHANDLED_BLOCK"

    def __init__(self, findings) -> None:
        listing = "; ".join(
            f"{f.ticker} {f.event_class} {f.event_date} ({f.detail})" for f in findings
        )
        super().__init__(
            f"{len(findings)} unhandled BLOCK-severity corporate action(s) inside the "
            f"window — the run halts (DE-32): {listing}"
        )
        self.findings = tuple(findings)
        self.blocked_tickers = tuple(sorted({f.ticker for f in findings}))


class CheckMissingError(CalendarError):
    """DATA.CALENDAR.CHECK_MISSING — feature-building reached without a check (DE-31)."""

    code = "DATA.CALENDAR.CHECK_MISSING"

    def __init__(self, what: str) -> None:
        super().__init__(
            f"{what} was attempted with no calendar check for its window. Every "
            f"training, backtest and inference run calls it for the entire universe "
            f"before the first feature is built — not per-ticker, not lazily (DE-31)"
        )


# --------------------------------------------------------------------------- #
# DATA.STORE.*
# --------------------------------------------------------------------------- #

class StoreWriteError(DataError):
    """DATA.STORE.WRITE_FAILED — atomic write failed; no partial file remains (DE-10)."""

    code = "DATA.STORE.WRITE_FAILED"


class AppendOnlyError(DataError):
    """DE-6.2 / DE-6.7 — an attempt to overwrite an append-only ledger.

    ⚠ Deleting a Fact destroys the ability to reproduce a past decision, and a
    restatement that overwrites is indistinguishable from one that never
    happened.
    """

    code = "DATA.STORE.APPEND_ONLY"

    def __init__(self, ledger: str, key: object) -> None:
        super().__init__(
            f"{ledger} is append-only; {key!r} already exists and may not be "
            f"rewritten. A restatement APPENDS — overwriting destroys the only "
            f"information that makes look-ahead detectable (DE-6.2)"
        )


# --------------------------------------------------------------------------- #
# WARNING-severity codes — recorded, never raised (§10)
# --------------------------------------------------------------------------- #

#: Reportable states. Each is attached to an artifact or a run record; none of
#: them stops a run, and none of them is allowed to vanish either. Keyed by a
#: short name so a call site reads ``warn(WARNING_CODES["empty_as_of"], ...)``
#: rather than repeating a dotted string that a typo would silently change.
WARNING_CODES = {
    "throttled":        "DATA.SOURCE.THROTTLED",
    "empty_as_of":      "DATA.PIT.EMPTY_AS_OF",
    "weak_guarantee":   "DATA.PIT.WEAK_GUARANTEE",
    "validation_reject": "DATA.VALIDATION.REJECTED",
    "fx_unavailable":   "DATA.FX.UNAVAILABLE",
    "value_changed":    "DATA.RESTATEMENT.VALUE_CHANGED",
    "class_unchecked":  "DATA.CALENDAR.CLASS_UNCHECKED",
    "probe_skipped":    "DATA.PROBE.SKIPPED",
}


class UniverseIncompleteError(DataError):
    """DE-13 — ★ **a universe ticker that resolves to no source fails the run.**

    ⚠ *It is not dropped, and it does not become a row of NaNs.*

    > Inherited from a real incident: a LEFT JOIN silently dropped **7 of the 13
    > watchlist names** — the majority of the actionable path — and each kept
    > its row with every fundamental column present and entirely `NaN`.

    ★ Every failure is listed, not just the first: a 130-name universe with
    three problems should take one run to diagnose, not three.
    """

    code = "DATA.UNIVERSE.INCOMPLETE"

    def __init__(self, failures, requested: int) -> None:
        by_reason: dict = {}
        for failure in failures:
            by_reason.setdefault(failure.reason, []).append(failure.ticker)
        summary = "; ".join(f"{reason}: {sorted(names)}"
                            for reason, names in sorted(by_reason.items()))
        super().__init__(
            f"{len(failures)} of {requested} universe tickers did not resolve — "
            f"{summary}. ⚠ A missing name is not dropped and does not become a "
            f"row of NaNs (DE-13, P5). ★ `plan_gated` is a DECLARATION problem, "
            f"not a data one: the name does not belong in the universe while "
            f"the plan does not cover it (DE-49)")
