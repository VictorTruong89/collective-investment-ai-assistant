"""The FMP client — the only place an FMP URL exists (DE-1, DE-2, DE-8, CA-3).

Three behaviours carry the weight, and each was bought with measured evidence:

  **DE-15/DE-46 — a 402 is retried before it is reported.** §5A.2 gives `402`
  three indistinguishable causes, one of which is transient under burst:
  `key-metrics` and `ratios` came back 402 for all three tickers in a 595-call
  run and returned 40 periods each on retry with identical parameters.

  ```
  A 402 IS NOT EVIDENCE OF A PLAN GATE UNTIL IT HAS BEEN RETRIED.

  Had ingest treated 402 as "no data", D-02 would have lost every key metric
  and every ratio for the whole universe — and the downstream frame would
  have looked like a clean empty result, not a failure.
  ```

  **DE-16 — a known-gated parameter combination is refused before sending.**

  **DE-8 — the key never appears in a log, an artifact or an error message.**
  Enforced by the `Secret` wrapper's `__repr__`, not by care at each raise site.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

from src.data_engine.errors import (
    PlanGateRejected, PlanGatedError, SourceUnavailableError, WARNING_CODES,
)
from src.data_engine.src.fmp.gates import (
    ABSENT_ENDPOINTS, FORBIDDEN_ENDPOINT_PREFIXES, GATED_ENDPOINTS, parameter_gate,
)
from src.shared.secrets import Secret

BASE_URL = "https://financialmodelingprep.com/stable"

#: FMP Starter rate cap, checked 2026-08-15 (CN-2 — a world fact carries its
#: source and check date, or nobody can tell a stale fact from a current one).
RATE_LIMIT_PER_MIN = 300

#: DE-15's backoff. Three attempts because cause 3 recovered on the FIRST retry
#: in every measured case; a fourth would only lengthen a failure that is
#: already decided. Not a measurement — an admitted judgement (CN-10).
RETRY_DELAYS_S = (1.0, 4.0)


class UrllibTransport:
    """The real HTTP boundary. Injected, so the client itself stays testable."""

    def get(self, url: str, params: dict, headers: dict, timeout: float):
        query = urllib.parse.urlencode({k: v for k, v in params.items()
                                        if v is not None and not k.startswith("_")})
        req = urllib.request.Request(f"{url}?{query}", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace")


class FMPClient:
    """Throttled, gate-aware, fail-loud."""

    def __init__(self, api_key: Secret, transport=None, *, timeout: float = 30.0,
                 sleep=time.sleep, clock=time.monotonic) -> None:
        if not isinstance(api_key, Secret):
            raise TypeError(
                "api_key must be a Secret, not a bare string — DE-8 keeps the key out "
                "of logs and errors through the wrapper's __repr__, not through care "
                "at each raise site"
            )
        self._key = api_key
        self._transport = transport or UrllibTransport()
        self._timeout = timeout
        self._sleep = sleep
        self._clock = clock
        self._calls: list[float] = []
        self.warnings: list[str] = []

    # -- the one request path ----------------------------------------------- #

    def get(self, endpoint: str, **params):
        """Fetch and decode one endpoint. Raises rather than returning empty (P5)."""
        self._refuse_forbidden(endpoint)
        self._refuse_absent(endpoint)
        self._refuse_gated(endpoint, params)

        attempts = 0
        last_body = ""
        for delay in (0.0, *RETRY_DELAYS_S):
            if delay:
                self.warnings.append(WARNING_CODES["throttled"])
                self._sleep(delay)
            self._throttle()
            attempts += 1
            status, body = self._transport.get(
                f"{BASE_URL}/{endpoint}", dict(params, apikey=self._key.reveal()),
                {"User-Agent": "ai-investment-pipeline/D-07"}, self._timeout,
            )
            if status == 200:
                return json.loads(body) if body.strip() else []
            last_body = body
            if status == 402:
                continue                    # DE-15/DE-46 — classify, do not conclude
            if status == 404:
                # §5A.3: an absence, not a gate. Retrying is pointless.
                raise SourceUnavailableError(
                    endpoint,
                    f"404 — the endpoint does not exist. That is a different fact from "
                    f"402 and must never be handled alike (§5A.3)",
                )
            if status in (429, 500, 502, 503, 504):
                continue
            raise SourceUnavailableError(endpoint, f"HTTP {status}: {body[:200]}")

        if status == 402:
            raise PlanGatedError(endpoint, _redacted(params), attempts)
        raise SourceUnavailableError(
            endpoint, f"HTTP {status} after {attempts} attempt(s): {last_body[:200]}"
        )

    # -- refusals ------------------------------------------------------------ #

    def _refuse_forbidden(self, endpoint: str) -> None:
        """AC-7.31 — the vendor's indicators are never ingested, at any tier."""
        if endpoint.startswith(FORBIDDEN_ENDPOINT_PREFIXES):
            raise PlanGateRejected(
                endpoint, {},
                "D-02 computes indicators from D-07 prices. A vendor RSI is a SECOND "
                "definition of a feature we own, silently different from ours — F0 §12 "
                "D-16 is this exact defect, self-inflicted once already (AC-7.31)",
            )

    def _refuse_absent(self, endpoint: str) -> None:
        if endpoint in ABSENT_ENDPOINTS:
            raise SourceUnavailableError(
                endpoint, f"404 by measurement — {ABSENT_ENDPOINTS[endpoint]} (§5A.3)"
            )

    def _refuse_gated(self, endpoint: str, params: dict) -> None:
        """DE-16 / AC-7.33 — rejected at the boundary, not sent and failed."""
        if endpoint in GATED_ENDPOINTS:
            raise PlanGateRejected(endpoint, _redacted(params), GATED_ENDPOINTS[endpoint])
        why = parameter_gate(endpoint, params)
        if why:
            raise PlanGateRejected(endpoint, _redacted(params), why)

    # -- throttle ------------------------------------------------------------ #

    def _throttle(self) -> None:
        """In-process rate limiting. DE-9's sibling for FMP.

        Being rate-limited is a self-inflicted outage, and the 300/min cap is
        exactly what §6A.6 says a live per-run calendar sweep would blow through.
        """
        now = self._clock()
        self._calls = [t for t in self._calls if now - t < 60.0]
        if len(self._calls) >= RATE_LIMIT_PER_MIN:
            self.warnings.append(WARNING_CODES["throttled"])
            self._sleep(60.0 - (now - self._calls[0]))
            self._calls = []
        self._calls.append(self._clock())


def _redacted(params: dict) -> dict:
    """DE-8 — the parameters go into the error; the key never does."""
    return {k: v for k, v in sorted(params.items())
            if k not in ("apikey",) and not k.startswith("_")}
