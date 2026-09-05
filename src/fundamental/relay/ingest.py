"""D-01 §4B — ingesting a pasted response. RA-117, RA-118, RA-125, RA-143.

★ The response is an **external artifact** and is validated before anything
builds on it, exactly as an FMP figure is. ⚠ *A number does not become
trustworthy because a human carried it — EDGAR beats FMP for TTM because of what
the source can prove, not because of who fetched it.*
"""

from __future__ import annotations

from datetime import date

from src.fundamental.errors import (
    RelayContradictedError, RelayNotFreshError, RelayPartialError,
)
from src.fundamental.relay.compose import assert_prompt_attributed
from src.fundamental.relay.models import (
    CONTRADICTED, SESSION_FRESH, UNVERIFIABLE, VERIFIED, ClaimVerification,
    RelayEnvelope, RelayReport, VerificationResult,
)

#: Markers of a response that stopped early or declined. ⚠ **There is no
#: `partial`** (RA-64/GW-22): each of these is a failed relay, not a short one.
TRUNCATION_MARKERS = (
    "[continued]", "...(truncated)", "shall i continue", "would you like me to continue",
    "i'll continue in the next message", "message limit",
)
REFUSAL_MARKERS = ("i can't help with that", "i cannot provide", "i'm unable to")


def verify_claim(claim, *, ours, ordinal: int, checked_against: str,
                 tolerance: float = 0.0) -> ClaimVerification:
    """RA-118 — re-verify one relayed number against D-02/D-07.

    `ours` is `None` where we hold no counterpart, which is `unverifiable` — the
    honest majority case, and the one RA-114 prices.
    """
    theirs = claim.get("value")
    if ours is None or theirs is None:
        return ClaimVerification(ordinal=ordinal, text=claim.get("text", ""),
                                 result=UNVERIFIABLE,
                                 theirs="" if theirs is None else str(theirs))
    agree = _agree(ours, theirs, tolerance)
    return ClaimVerification(
        ordinal=ordinal, text=claim.get("text", ""),
        result=VERIFIED if agree else CONTRADICTED,
        checked_against=checked_against, ours=str(ours), theirs=str(theirs))


def _agree(ours, theirs, tolerance: float) -> bool:
    try:
        a, b = float(ours), float(theirs)
    except (TypeError, ValueError):
        return str(ours).strip().casefold() == str(theirs).strip().casefold()
    if a == b:
        return True
    scale = max(abs(a), abs(b)) or 1.0
    return abs(a - b) / scale <= tolerance


def assert_fresh(ticker: str, envelope: RelayEnvelope) -> None:
    """RA-117 / AC-1.80 — one prompt, one response, one fresh session."""
    if envelope.session != SESSION_FRESH:
        raise RelayNotFreshError(ticker, envelope.session)


def assert_whole(ticker: str, text: str) -> None:
    """RA-125 / AC-1.80 — never partially ingested, never topped up."""
    low = (text or "").casefold()
    if not low.strip():
        raise RelayPartialError(ticker, "an empty response")
    for marker in TRUNCATION_MARKERS:
        if marker in low:
            raise RelayPartialError(ticker, f"a truncated response ({marker!r})")
    for marker in REFUSAL_MARKERS:
        if marker in low:
            raise RelayPartialError(ticker, f"a refused response ({marker!r})")


def ingest(*, ticker: str, as_of: date, envelope: RelayEnvelope, text: str,
           verifications, prompt=None, verdict: str = "", conviction: str = "",
           checked_against=()) -> RelayReport:
    """The whole ingest, in the order the guards have to run in.

    ★ Freshness and wholeness come **before** verification: there is no point
    re-verifying half a response, and RA-125 says a partial one is not topped up
    but re-run. Attribution comes before both, because an unattributable prompt
    means we do not know what question was asked.
    """
    if prompt is not None:
        assert_prompt_attributed(ticker, prompt, envelope)     # RA-122
    assert_fresh(ticker, envelope)                             # RA-117
    assert_whole(ticker, text)                                 # RA-125

    result = VerificationResult(claims=tuple(verifications),
                                checked_against=tuple(checked_against))
    # ⚠ RA-118 — `contradicted` fails the ingest, and RA-143 lets it say which.
    if result.contradicted:
        raise RelayContradictedError(ticker, result.contradictions)

    return RelayReport(ticker=ticker, as_of=as_of, relay=envelope,
                       verification=result, verdict=verdict,
                       conviction=conviction, narrative=text)


def confidence_of(report: RelayReport):
    """RA-114 / RA-144 / AC-1.77 — ★★ the floors fire on it **unchanged**.

    ⚠ *No relay-specific rule anywhere.* `assess_confidence` reads an
    `aggregate`, and `VerificationResult` exposes one — so the relay and the
    scorecard share **one implementation of INV-012/INV-013** while keeping the
    different denominators each is entitled to.
    """
    from src.fundamental.scorecard.coverage import assess_confidence

    return assess_confidence(report.verification)
