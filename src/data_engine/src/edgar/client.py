"""SEC EDGAR access — throttled, identified, and never logged (DE-8, DE-9, AC-7.21/22).

★ **The User-Agent is not politeness, it is access.** SEC requires a contactable
identifier and blocks clients without one, so being blocked is a self-inflicted
outage. The rate limit is likewise theirs, not ours: 10 requests/second, and the
throttle is in-process because there is one process.

⚠ **DE-8 covers the EDGAR User-Agent email as well as the API keys.** The email
is a real person's address; it may not appear in a log, an artifact or an error
message. It is wrapped in a `Secret` for the same reason the FMP key is — so the
protection is structural rather than a habit at each raise site.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from src.data_engine.errors import SourceUnavailableError
from src.shared.secrets import Secret

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:0>10}.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:0>10}.json"
#: DE-83 — the only place `document()` may read from.
ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/"

#: SEC's published fair-access limit, checked 2026-08-23 (CN-2).
RATE_LIMIT_PER_SEC = 10


class EdgarClient:
    """Throttled EDGAR client. The contact email is a Secret, not a string."""

    def __init__(self, contact_email: Secret, transport=None, *, timeout: float = 30.0,
                 sleep=time.sleep, clock=time.monotonic) -> None:
        if not isinstance(contact_email, Secret):
            raise TypeError(
                "contact_email must be a Secret — DE-8 puts the EDGAR User-Agent email "
                "in the same class as an API key, and a bare string reaches the first "
                "error message that formats its arguments"
            )
        self._contact = contact_email
        self._transport = transport or _UrllibTransport()
        self._timeout = timeout
        self._sleep = sleep
        self._clock = clock
        self._calls: list[float] = []

    @property
    def user_agent(self) -> str:
        """Built on demand, never stored. `Secret.reveal()` is the one exit point."""
        return f"ai-investment-pipeline (contact: {self._contact.reveal()})"

    def submissions(self, cik: str) -> dict:
        """The filing index for one CIK — form types, accessions, dates."""
        return self._get(SUBMISSIONS_URL.format(cik=str(cik).lstrip("0")))

    def companyfacts(self, cik: str) -> dict:
        """XBRL companyfacts — every tag, every period, every filing that reported it."""
        return self._get(COMPANYFACTS_URL.format(cik=str(cik).lstrip("0")))

    def document(self, url: str) -> str:
        """DE-83 — one filing document as TEXT, through the same throttle and User-Agent.

        ⚠ Archive URLs only: anything else is not a filing, and this client is not a
        general fetcher.
        """
        if not url.startswith(ARCHIVES_URL):
            raise ValueError(f"{url} is not in the EDGAR archive ({ARCHIVES_URL}) — DE-83")
        self._throttle()
        status, body = self._transport.get(
            url, {}, {"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
            self._timeout,
        )
        if status == 200:
            return body
        raise SourceUnavailableError(_endpoint_of(url), f"HTTP {status}")

    def _get(self, url: str) -> dict:
        self._throttle()
        status, body = self._transport.get(
            url, {}, {"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
            self._timeout,
        )
        if status == 200:
            return json.loads(body)
        # The URL carries a CIK, not a secret; the User-Agent does and is not
        # included. DE-8 holds because of what is NOT interpolated here.
        raise SourceUnavailableError(_endpoint_of(url), f"HTTP {status}")

    def _throttle(self) -> None:
        now = self._clock()
        self._calls = [t for t in self._calls if now - t < 1.0]
        if len(self._calls) >= RATE_LIMIT_PER_SEC:
            self._sleep(1.0 - (now - self._calls[0]))
            self._calls = []
        self._calls.append(self._clock())


class _UrllibTransport:
    """★★ ⚠ **`_get` asks for gzip, so this must be able to un-gzip.**

    *Found 2026-08-26 on the first real EDGAR call ever made:* `_get` sends
    `Accept-Encoding: gzip, deflate`, `urllib` does **not** decompress
    transparently, and this read `.decode("utf-8")` straight off the wire —
    so every companyfacts fetch died on `0x8b`, the second byte of the gzip
    magic number.

    ★ **Nothing caught it because every test injects a fake transport.** The one
    class that talks to the network was the one class with no coverage, and
    EDGAR is the *preferred* source for TTM line items (CLAUDE.md: *"EDGAR
    wins"*) — so the preferred path had never once run.
    """

    def get(self, url: str, params: dict, headers: dict, timeout: float):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, _decode(resp.read(), resp.headers)
        except urllib.error.HTTPError as exc:
            return exc.code, _decode(exc.read(), exc.headers, errors="replace")


def _decode(raw: bytes, headers, *, errors: str = "strict") -> str:
    """Undo whatever `Content-Encoding` the server actually applied.

    ⚠ Keyed on the RESPONSE header, never on what was requested: a server is
    free to ignore `Accept-Encoding`, and decompressing an identity body is the
    same defect in the other direction.
    """
    import gzip
    import zlib

    encoding = (headers.get("Content-Encoding") or "").lower()
    if "gzip" in encoding:
        raw = gzip.decompress(raw)
    elif "deflate" in encoding:
        raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    return raw.decode("utf-8", errors=errors) if errors != "strict" \
        else raw.decode("utf-8")


def _endpoint_of(url: str) -> str:
    return url.split("/api/")[-1] if "/api/" in url else url.rsplit("/", 1)[-1]
