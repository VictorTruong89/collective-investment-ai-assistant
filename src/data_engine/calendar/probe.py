"""The LIVE FMP reality probe — §6A.4, DE-37…DE-41 (AC-7.54, 7.55, 7.56).

```
A CALENDAR CHECK BUILT AND TESTED ONLY AGAINST RECORDED FIXTURES IS A
MACHINE FOR CONFIRMING ITS AUTHOR'S ASSUMPTIONS.

Every wrong belief in this spec's history was of exactly that shape: the
`_cumulative_fys` docstring asserted the wrong rule and had a PASSING TEST
built on real production numbers; the 2026-08-15 split conclusion was drawn
from three names that could not have shown the effect.

FIXTURES FREEZE WHAT WE ALREADY BELIEVE.
```

Four rules shape this module and each rejects an easier design:

  **DE-37** fetch over the network and digest through the **real code path** —
  not a fixture, not a mock, not a recorded cassette.
  **DE-38** assert against a **known-answer set** established independently
  (§6A.5). A probe that only checks "something came back" verifies nothing.
  **DE-39** compare **every intermediate**, not just the final report — the
  lesson of FMP's TTM being wrong while the DCF still produced a plausible
  number.
  **DE-40** ⚠ **a skipped probe is LOUD.** A live probe that silently skips when
  `FMP_API_KEY` is unset is worse than no probe: it reports green while
  verifying nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.data_engine.errors import WARNING_CODES
from src.data_engine.pit.adjustment import build_price_panel
from src.data_engine.pit.models import utcnow
from src.data_engine.src.edgar.submissions import filer_class
from src.data_engine.src.fmp import prices as fmp_prices

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


@dataclass(frozen=True, slots=True)
class KnownAnswer:
    """One row of §6A.5. `established_by` is not decoration.

    ⚠ **F3 §4c applies when a probe and this table disagree: neither is assumed
    right until it is established which is wrong.** So the provenance of the
    expected value has to travel with it — otherwise the tie is broken by
    whichever side is easier to change.
    """

    id: str
    claim: str
    established_by: str
    probes: str


KNOWN_ANSWERS = (
    KnownAnswer("K-1", "NVDA split 10:1 effective 2024-06-10 (also 4:1 2021-07-20, "
                       "3:2 2007-09-11, 2:1 2006-04-07)",
                "fmp:splits + SEC 8-K", "split detection, adjustment factors"),
    KnownAnswer("K-2", "NVDA 2024-06-07: full close 120.89, non-split-adjusted 1208.90, "
                       "ratio exactly 10", "dump, §5C.7", "which series is raw"),
    KnownAnswer("K-3", "NVDA volume 2024-06-07: raw 41,238,600, full 412,386,000",
                "dump", "volume is adjusted in the OPPOSITE direction"),
    KnownAnswer("K-4", "MSFT declares dividends a median ~72 days before ex-date; "
                       "declarationDate populated on 90/90 rows",
                "dump", "knowability keyed on declaration, not ex-date"),
    KnownAnswer("K-5", "ARM files 20-F and 6-K; no 10-K, no 10-Q",
                "fmp:sec-filings-search, EDGAR", "source routing (§5.1 case B)"),
    KnownAnswer("K-6", "MU statement filing lag: min 20, median 28, max 57 days",
                "dump, §5C.1", "mid-window filing detection (class 7)"),
    KnownAnswer("K-7", "MSFT amendments 2024-2026: 8-K/A, 4/A, 3/A, SC 13G/A; no 10-K/A",
                "fmp:sec-filings-search", "restatement detection finds these, invents none"),
    KnownAnswer("K-8", "news/stock returns ~92 days regardless of paging",
                "dump, §5C.4", "news reports UNCHECKED beyond the window"),
    KnownAnswer("K-9", "408 of 437 MSFT filings accepted at/after 16:00 ET",
                "dump, §5C.5", "next-session knowability"),
    KnownAnswer("K-10", "MU quarterly revenue is discrete: quarters sum exactly to annual",
                "dump, §5A.3a", "the _cumulative_fys class stays absent"),
)

#: K-2 and K-8 are the two most valuable rows, because each CONTRADICTS
#: something this spec previously asserted. A known-answer set earns its keep by
#: containing the cases that already caught us out.
HIGH_VALUE = ("K-2", "K-8")


@dataclass
class ProbeResult:
    """DE-39 — every intermediate, not only the verdict."""

    checks: list = field(default_factory=list)
    skipped_reason: str | None = None

    def record(self, answer_id: str, outcome: str, expected, actual, note: str = "") -> None:
        self.checks.append({"id": answer_id, "outcome": outcome,
                            "expected": expected, "actual": actual, "note": note})

    @property
    def outcome(self) -> str:
        if self.skipped_reason:
            return SKIP
        if any(c["outcome"] == FAIL for c in self.checks):
            return FAIL
        return PASS if self.checks else SKIP

    def to_json_obj(self) -> dict:
        obj = {"outcome": self.outcome, "checks": self.checks,
               "ran_at": utcnow().isoformat()}
        if self.skipped_reason:
            # DE-40 / AC-7.56: a skip is reported AS a skip and never counted as
            # a pass. The warning code is what makes its absence countable in the
            # run record rather than only readable in a log.
            obj["skipped_reason"] = self.skipped_reason
            obj["code"] = WARNING_CODES["probe_skipped"]
        return obj


def run_probe(client) -> ProbeResult:
    """Fetch live and digest through the real code path (DE-37).

    `client` is a real :class:`FMPClient` over a real transport. Passing a fake
    here does not make the probe cheaper — it makes it a fixture test wearing the
    probe's name, which is the exact failure DE-37 exists to prevent.
    """
    result = ProbeResult()
    if client is None:
        result.skipped_reason = (
            "no FMP client — FMP_API_KEY unset or network unavailable. Reported as "
            "SKIPPED, never as a pass: a probe that silently skips is worse than no "
            "probe because it reports green while verifying nothing (DE-40)"
        )
        return result

    _probe_split(client, result)          # K-1, K-2, K-3
    _probe_dividends(client, result)      # K-4
    _probe_filer_class(client, result)    # K-5
    return result


def _probe_split(client, result: ProbeResult) -> None:
    """K-1/K-2/K-3 — and it goes through `build_price_panel`, not past it.

    ★ DE-39's requirement is why the panel is built rather than the raw JSON
    inspected: the intermediate that matters is the **derived adjustment
    factor**, and a probe that read `full` and `non-split-adjusted` straight from
    the response would confirm the vendor and verify nothing about our code.
    """
    on, ticker = date(2024, 6, 7), "NVDA"
    splits = fmp_prices.splits(client, ticker)
    ten_to_one = [s for s in splits
                  if s.event_date == date(2024, 6, 10)
                  and s.detail["numerator"] == 10 and s.detail["denominator"] == 1]
    result.record("K-1", PASS if ten_to_one else FAIL,
                  "10:1 effective 2024-06-10",
                  [f"{s.detail['numerator']}:{s.detail['denominator']} {s.event_date}"
                   for s in splits[-4:]])

    raw = fmp_prices.raw_prices(client, ticker, on, on)
    vendor = fmp_prices.vendor_adjusted(client, ticker, on, on)
    raw_close = int(raw.iloc[0]["close_minor"])
    vendor_close = int(vendor.iloc[0]["adj_close_minor"])
    result.record("K-2", PASS if raw_close == 120890 else FAIL, 120890, raw_close,
                  "non-split-adjusted close, minor units")
    result.record("K-2b", PASS if abs(raw_close / max(vendor_close, 1) - 10) < 0.01 else FAIL,
                  10.0, round(raw_close / max(vendor_close, 1), 4),
                  "raw/full ratio must be exactly the split factor")
    result.record("K-3", PASS if int(raw.iloc[0]["volume"]) == 41238600 else FAIL,
                  41238600, int(raw.iloc[0]["volume"]), "raw volume, NOT the x10 full volume")

    panel = build_price_panel(raw, splits, date(2024, 8, 1))
    ours = int(panel.iloc[0]["adj_close_minor"])
    result.record("K-2c", PASS if abs(ours - vendor_close) <= 1 else FAIL,
                  vendor_close, ours,
                  "★ our reconstruction against the vendor's own adjusted close (DE-43)")

    unadjusted = build_price_panel(raw, splits, date(2024, 6, 1))
    result.record("K-1b",
                  PASS if int(unadjusted.iloc[0]["adj_close_minor"]) == raw_close else FAIL,
                  raw_close, int(unadjusted.iloc[0]["adj_close_minor"]),
                  "adj_as_of BEFORE the split leaves the price alone (DE-28, INV-2)")


def _probe_dividends(client, result: ProbeResult) -> None:
    """K-4 — declarationDate populated, and a median lead of roughly 72 days."""
    divs = fmp_prices.dividends(client, "MSFT")
    recent = [d for d in divs if d.event_date >= date(2018, 1, 1)]
    if not recent:
        result.record("K-4", FAIL, "dividend rows", 0, "no MSFT dividends returned")
        return
    leads = sorted((d.event_date - d.knowable_at).days for d in recent)
    median = leads[len(leads) // 2]
    populated = sum(1 for d in recent if d.knowable_at != d.event_date)
    result.record("K-4", PASS if 40 <= median <= 110 else FAIL, "~72 days", median,
                  f"declarationDate lead; populated on {populated}/{len(recent)} rows")


def _probe_filer_class(client, result: ProbeResult) -> None:
    """K-5 — ARM is 20-F/6-K, and the router must say case B."""
    filings = client.get("sec-filings-search/symbol", symbol="ARM",
                         **{"from": "2024-01-01", "to": "2026-08-15"})
    forms = sorted({str(f.get("formType", "")) for f in (filings or [])})
    case = filer_class(forms)
    result.record("K-5", PASS if case == "20-F/6-K" else FAIL, "20-F/6-K", case,
                  f"forms seen: {forms[:8]}")
