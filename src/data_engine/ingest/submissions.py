"""Classes 4, 7 and 11 from ONE EDGAR submissions pass.

★★ **Three classes, one fetch.** `restatement_amended` (4),
`filing_mid_window` (7) and `material_event_8k` (11) are all answered by the
same `submissions` document, so fetching it three times would triple EDGAR's
throttled cost for nothing. ⚠ The caller says which classes it wants; the
default is class 4 alone, so an existing caller sees no change.

★ **From EDGAR, because FMP does not carry it.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  MEASURED 2026-08-28.  FMP's filing index HAS NO 10-K/A AT ALL.  ║
║                                                                  ║
║    sec-filings-search/form-type  10-K/A  2024-01-01..2024-12-31   ║
║      -> 0 rows.  Same for 2025 H1 and 2026 YTD.                  ║
║      -> 10-Q/A over the SAME windows fills a 100-row page.       ║
║    Per-symbol search: 6 known amenders, 2 683 filings scanned    ║
║      across 5 mega-caps -> NOT ONE 10-K/A.                       ║
║                                                                  ║
║  ★ EDGAR carries them: TSLA's submissions hold FIVE 10-K/A.      ║
║                                                                  ║
║  ⚠⚠ ZERO ANNUAL AMENDMENTS ACROSS ALL US FILERS IN A YEAR IS     ║
║     NOT RARITY, IT IS A VENDOR GAP — and this is a BLOCK class.  ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **The same precedence that already governs TTM**: *EDGAR wins, because it
carries the fact explicitly where FMP infers or omits it.*

⚠⚠ **The spec said `formType ~ /A`, and that test is wrong.** Measured on five
mega-caps, the `/A` suffix matches **63 `SC 13G/A`, 7 `4/A`, 5 `13F-HR/A`** and
similar — *ownership and holdings amendments, which restate nobody's financial
statements*. A suffix test would file Apple as having restated 63 times. ★ So
this module uses an **explicit whitelist of financial-statement forms**, and the
ownership forms are excluded by construction rather than by filtering.
"""

from __future__ import annotations

from datetime import date

#: ★ Amendments to **financial statements**. ⚠ Deliberately a whitelist: the
#: `/A` suffix is shared with ownership forms that restate nothing (DE-35).
AMENDED_FORMS = frozenset({"10-K/A", "10-Q/A", "20-F/A", "40-F/A", "6-K/A"})

#: ★★ **8-K Item 4.02 — "Non-Reliance on Previously Issued Financial
#: Statements".** ⚠ This is the *announcement* of a restatement and usually
#: **precedes the amended filing by weeks**, so a class that waits for the
#: amendment learns last. EDGAR's `items` field carries it; FMP exposes no
#: item numbers at all.
NON_RELIANCE_ITEM = "4.02"

#: ⚠ Late-filing notices. ★ NOT restatements — kept separate on purpose: a
#: company may file NT 10-K for reasons that never become an amendment.
LATE_FORMS = frozenset({"NT 10-K", "NT 10-Q"})

#: Class 7 — ★ **the periodic financial reports themselves.** A 10-K accepted
#: *inside* an analysis window means what was knowable CHANGED partway through
#: it, which is why the class is a FLAG rather than noise.
#: ⚠ Amendments are deliberately absent: they are class 4, and a filing must
#: not arrive twice under two classes.
PERIODIC_FORMS = frozenset({"10-K", "10-Q", "20-F", "40-F"})

#: ★ Every class this module can answer from one submissions document.
SUBMISSION_CLASSES = ("restatement_amended", "filing_mid_window",
                      "material_event_8k")


def refresh_restatements(client, store, *, tickers, cik_map, as_of: date,
                         since: date | None = None, on_error=None,
                         classes=("restatement_amended",)) -> dict:
    """EDGAR submissions into the store, for the `classes` requested.

    ★ Default is class 4 alone (**BLOCK**). Pass `SUBMISSION_CLASSES` to get
    `filing_mid_window` (7) and `material_event_8k` (11) from the same pass.

    `client` is an `EdgarClient`; `cik_map` is `{ticker: cik}` — ★ **supplied,
    not looked up**, so this module never becomes a second owner of the mapping.

    ⚠ **`acceptanceDateTime` is the knowability date** (DE-34), not
    `filingDate`: a filing accepted after the close is not knowable that day,
    and a restatement is precisely the event a run must not act on early.

    ⚠⚠ **A name that fails is NOT silently skipped.** The refresh is recorded
    only for the names actually reached — DE-58's rule, because a class marked
    `CHECKED` over a universe it did not cover is the defect §6A exists to stop.
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding

    wanted_classes = tuple(classes)
    severities = {name: BY_NAME[name].severity for name in wanted_classes}
    findings, reached, failed = [], [], {}

    for ticker in tickers:
        cik = cik_map.get(ticker)
        if not cik:
            failed[ticker] = "no CIK in the map"
            continue
        try:
            recent = (client.submissions(cik).get("filings") or {}).get("recent") or {}
        except Exception as exc:                   # noqa: BLE001 — named
            failed[ticker] = str(exc)[:140]
            if on_error is not None:
                on_error(ticker, exc)
            continue
        reached.append(ticker)
        findings.extend(_findings_for(ticker, recent, severities,
                                      as_of=as_of, since=since))

    store.upsert(findings)
    if not reached:
        return {"findings": 0, "refreshed": [], "reached": [], "failed": failed,
                "why": "EDGAR returned nothing for any name — nothing is CHECKED"}

    window_from = since or date(1993, 1, 1)     # ★ EDGAR's own earliest filings
    if not failed:
        for name in wanted_classes:
            store.record_refresh(name, window_from, as_of,
                                 covers_tickers=tuple(reached))
        recorded = list(wanted_classes)
        why = ""
    else:
        # ⚠ NOT recorded. A partial sweep that marks the class CHECKED claims a
        #   coverage it does not have, and the gate would inherit the claim.
        recorded = []
        why = (f"{len(failed)} of {len(tickers)} names failed, so the class is "
               f"NOT recorded as refreshed — {sorted(failed)[:5]}")

    counts = {}
    for finding in findings:
        counts[finding.event_class] = counts.get(finding.event_class, 0) + 1
    amended = sum(1 for f in findings
                  if f.detail.get("signal") == "amended_filing")
    return {"findings": len(findings), "refreshed": recorded,
            "reached": tuple(reached), "failed": failed,
            "amended": amended, "by_class": counts,
            "non_reliance": sum(1 for f in findings
                                if f.detail.get("signal") == "non_reliance_8k"),
            "why": why or (
                "★ EDGAR, not FMP: measured 2026-08-28, FMP's index carries "
                "ZERO 10-K/A across all filers while EDGAR holds them. ⚠ The "
                "`/A` suffix is NOT the test — it matches SC 13G/A and 4/A, "
                "which restate no financial statements")}


def _findings_for(ticker: str, recent: dict, severities: dict, *,
                  as_of: date, since: date | None):
    """One name's filings, classified. ★ **One pass, up to three classes.**

    ⚠ A filing is emitted under **exactly one** class. An amendment is class 4
    and must not also arrive as class 7, or a consumer counting periodic filings
    would double-count every restatement.
    """
    from src.data_engine.contracts import Finding

    forms = recent.get("form") or []
    filed = recent.get("filingDate") or []
    accepted = recent.get("acceptanceDateTime") or []
    items = recent.get("items") or []
    reports = recent.get("reportDate") or []
    accession = recent.get("accessionNumber") or []

    out = []
    for index, form in enumerate(forms):
        item = items[index] if index < len(items) else ""
        classified = _classify(form, item)
        if classified is None:
            continue
        event_class, signal = classified
        severity = severities.get(event_class)
        if severity is None:
            continue                       # ★ the caller did not ask for it

        when = _date_of(filed[index] if index < len(filed) else None)
        knowable = _date_of(accepted[index] if index < len(accepted) else None) or when
        if when is None or knowable is None:
            continue
        if knowable > as_of:
            continue                       # ⚠ DE-34 — not knowable to this run
        if since is not None and when < since:
            continue

        out.append(Finding(
            ticker, event_class, severity, when, knowable,
            {"signal": signal, "form": form,
             # ★ The PERIOD the filing speaks to, which is the field a consumer
             #   needs: an amendment filed today can restate a quarter three
             #   years back, and class 7 asks whether the period lands INSIDE
             #   the analysis window.
             "period": _text(reports[index] if index < len(reports) else ""),
             "items": item or "",
             "accession": _text(accession[index] if index < len(accession) else "")},
            "edgar:submissions"))
    return out


def _classify(form: str, item: str):
    """`(event_class, signal)` or `None`. ⚠ **Order matters — first match wins.**

    ★ The amendment test runs BEFORE the periodic test, so `10-K/A` is a
    restatement and never a mid-window filing. ⚠ Reversing them would file every
    amendment twice.
    """
    if form in AMENDED_FORMS:
        return ("restatement_amended", "amended_filing")
    # ★★ 8-K item 4.02 is a RESTATEMENT announcement, not an ordinary material
    #    event — it outranks class 11 and lands weeks before the amendment.
    if form.startswith("8-K") and NON_RELIANCE_ITEM in (item or ""):
        return ("restatement_amended", "non_reliance_8k")
    if form in PERIODIC_FORMS:
        return ("filing_mid_window", "periodic_filing")
    if form.startswith("8-K"):
        return ("material_event_8k", "material_event")
    return None


def _date_of(value):
    from datetime import date as _date

    try:
        return _date.fromisoformat(str(value)[:10]) if value else None
    except (TypeError, ValueError):
        return None


def _text(value) -> str:
    return "" if value is None else str(value)
