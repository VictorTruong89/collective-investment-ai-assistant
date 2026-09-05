"""DE-62 — ticker changes from a snapshot diff on CIK. ★ No vendor, no search.

```text
╔══════════════════════════════════════════════════════════════════╗
║  VERIFIED 2026-08-28 against this repo's own stored universe:     ║
║                                                                  ║
║    config/sp500_tickers.yaml   SEC company_tickers.json today     ║
║      BK   -> 0001390777   vs     BNY  -> 1390777                  ║
║      SATS -> 0001415404   vs     ECHO -> 1415404                  ║
║                                                                  ║
║  Both rebrands recovered EXACTLY, with no vendor call and no      ║
║  web search — because the CIK never moved.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠⚠ **A CIK that DISAPPEARS is not a delisting.** Measured the same day: `AVB`
is delisted at FMP (2026-08-17) and **still present in SEC's ticker file**. The
file lags deregistration, so a vanished CIK is a *candidate for investigation*
(`.claude/skills/ticker-went-silent/`) and never a conclusion — DE-35's
distinction, in the identity layer.
"""

from __future__ import annotations

from datetime import date

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

def sec_snapshot(contact=None, *, url: str = SEC_TICKERS_URL, opener=None) -> dict:
    """`{cik: ticker}` from SEC's current-state file.

    ★ **The User-Agent is access, not politeness** — SEC answers a generic one
    with `403`, measured 2026-08-28. `contact` is the **same `Secret`
    `EdgarClient` takes** (`EDGAR_CONTACT`): ⚠ **DE-8 puts that address in the
    same class as an API key**, so it is wrapped rather than passed as a string
    and `reveal()` is the one exit point.

    ⚠ **Decompressed explicitly.** DE-50: this repo requested gzip from EDGAR
    for months and never decompressed it, so *EDGAR had never successfully
    fetched*. Making the same mistake twice would be inexcusable.
    """
    import gzip
    import json
    import urllib.request

    from src.data_engine.errors import SourceUnavailableError
    from src.shared.secrets import Secret

    if opener is None:
        if not isinstance(contact, Secret):
            raise TypeError(
                "contact must be a Secret — DE-8 puts the SEC User-Agent email in "
                "the same class as an API key, and a bare string reaches the first "
                "error message that formats its arguments")
        agent = f"ai-investment-pipeline (contact: {contact.reveal()})"

        def opener(target):
            request = urllib.request.Request(
                target, headers={"User-Agent": agent,
                                 "Accept-Encoding": "gzip, deflate"})
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = response.read()
                    if response.headers.get("Content-Encoding") in ("gzip", "deflate"):
                        payload = gzip.decompress(payload)
                    return payload.decode("utf-8")
            except Exception as exc:                   # noqa: BLE001
                # ⚠ The UA carries the address, so the exception must not.
                raise SourceUnavailableError(
                    f"sec:company_tickers.json is unavailable: "
                    f"{type(exc).__name__}") from None

    rows = json.loads(opener(url))
    values = rows.values() if isinstance(rows, dict) else rows

    # ★★ `{cik: [tickers]}` — a LIST, and the order is SEC's own.
    #
    # ⚠⚠ The first cut of this returned `{cik: ticker}` and produced **79
    #    false renames out of 507 names**: `WFC` "became" `WFC-PA`, `BRK-B`
    #    "became" `BRK-A`, `GOOGL` "became" `GOOGM`. ★ A CIK is a REGISTRANT
    #    and 1 443 of the 8 004 in this file carry more than one security —
    #    preferred (`-P*`), warrants (`-WT`), notes, share classes — so a dict
    #    keyed on CIK keeps whichever row came last. **That is QD-17, and it is
    #    not a future concern; it is fatal on the first run.**
    #
    # ★ SEC lists the COMMON STOCK FIRST: ['BNY', 'BNY-PK'],
    #   ['GOOGL', 'GOOG', 'GOOGN', 'GOOGM'], ['WFC', 'WFC-PY', ...].
    out: dict = {}
    for value in values:
        if not value.get("ticker"):
            continue
        out.setdefault(_cik(value["cik_str"]), []).append(str(value["ticker"]).upper())
    return out


def detect_changes(previous: dict, current: dict, *, knowable_at: date):
    """`(findings, vanished)` — ★ **two results, deliberately separated.**

    `previous` is `{cik: ticker}` (what we hold); `current` is
    `{cik: [tickers]}` from `sec_snapshot`. A single ticker is accepted for
    `current` too, so a caller may pass either shape.

    ★★ **The test is MEMBERSHIP, not equality.** A registrant lists every
    security it has — common, preferred, warrants, share classes — so *"our
    ticker is not the one SEC lists first"* is nothing. Only *"our ticker is not
    listed at all, and the registrant is still here"* is a rename.

    ⚠ **A CIK that left `current` is returned separately as a candidate, never
    as a finding**: the SEC file lags deregistration — `AVB` was delisted at FMP
    on 2026-08-17 and still present here on the 28th (DE-62, DE-35).
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding

    findings = []
    for cik, was in sorted(previous.items()):
        listed = _listed(current.get(_cik(cik)))
        if listed is None:
            continue                       # ⚠ vanished — handled below, not here
        was = str(was).upper()
        if was in listed:
            continue                       # ★ still listed: NOT a rename
        findings.append(Finding(
            was, "ticker_change", BY_NAME["ticker_change"].severity,
            knowable_at, knowable_at,
            # ★ The successor travels WITH the finding — a rename that does not
            #   name what it became is half an answer. `candidates` carries the
            #   whole set so ⚠ an AMBIGUOUS case is visible rather than decided:
            #   the primary is SEC's own first listing, not our guess.
            {"cik": _cik(cik), "from": was, "to": listed[0],
             "candidates": list(listed), "ambiguous": len(listed) > 1},
            "derived:sec:company_tickers.json"))

    vanished = {_cik(c): str(t).upper() for c, t in previous.items()
                if _cik(c) not in current}
    return findings, vanished


def _listed(value):
    """Accept `[tickers]` or a bare `ticker`; `None` when the CIK is absent."""
    if value is None:
        return None
    if isinstance(value, str):
        return [value.upper()]
    return [str(v).upper() for v in value]


def mappings_from(snapshot: dict, *, knowable_at: date, valid_from=None):
    """CT-7.8 rows for a whole snapshot — the append payload."""
    from src.data_engine.symbology.master import SEC_SOURCE

    return [{"cik": _cik(cik), "ticker": ticker,
             "valid_from": valid_from or knowable_at, "valid_to": None,
             "knowable_at": knowable_at, "source": SEC_SOURCE}
            for cik, listed in sorted(snapshot.items())
            for ticker in (_listed(listed) or ())]


def close_out(history, findings, *, on: date) -> int:
    """Stamp `valid_to` on the retired symbols named by `findings`.

    ⚠ **Appends a closing row rather than editing** (CT-7.8): the store is
    append-only, and `resolve` reads the most recent applicable row.
    """
    rows = []
    for finding in findings:
        detail = finding.detail or {}
        rows.append({"cik": _cik(detail.get("cik", "")),
                     "ticker": str(detail.get("from", "")).upper(),
                     "valid_from": None, "valid_to": on,
                     "knowable_at": on, "source": "derived:ticker_change"})
    return history.append(rows)


def _cik(value) -> str:
    return str(value).strip().zfill(10)
