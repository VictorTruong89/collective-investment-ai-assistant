"""The LIVE reality probe — AC-7.54, 7.55, 7.56 (§6A.4, F3 Tier 1).

Tier: integration, against reality (constitution §4; F3 §4a Tier 1).

```
A CALENDAR CHECK BUILT AND TESTED ONLY AGAINST RECORDED FIXTURES IS A
MACHINE FOR CONFIRMING ITS AUTHOR'S ASSUMPTIONS.
```

⚠ **Only ONE test here reaches the network, and it is marked `live`.** The rest
verify the properties DE-40 attaches to the SKIP path — because "the probe was
skipped" is the state that has to be impossible to confuse with "the probe
passed", and that is checkable without a key.

    pytest -m live tests_src/test_data_engine_probe.py    # DE-40, separately invocable
"""

from __future__ import annotations

import os

import pytest

from src.data_engine.calendar.probe import (
    FAIL, HIGH_VALUE, KNOWN_ANSWERS, PASS, ProbeResult, SKIP, run_probe,
)
from src.data_engine.src.fmp.client import FMPClient
from src.shared.secrets import Secret


def test_ac_7_55_the_probe_asserts_against_the_k1_to_k10_known_answer_set():
    """AC-7.55 — DE-38. A probe that only checks "something came back" verifies nothing.

    ★ K-2 and K-8 are the two most valuable rows, because each **contradicts
    something this spec previously asserted**. A known-answer set earns its keep
    by containing the cases that already caught us out.
    """
    ids = [k.id for k in KNOWN_ANSWERS]
    assert ids == [f"K-{n}" for n in range(1, 11)]
    assert set(HIGH_VALUE) <= set(ids)
    for known in KNOWN_ANSWERS:
        assert known.established_by, f"{known.id} must name what established it (F3 §4c)"
        assert known.probes, f"{known.id} must name what it probes"


def test_ac_7_56_a_skipped_probe_is_reported_as_skipped_and_never_as_a_pass():
    """AC-7.56 — DE-40.

    ⚠ A live probe that silently skips when `FMP_API_KEY` is unset is **worse
    than no probe**: it reports green while verifying nothing.
    """
    result = run_probe(None)
    assert result.outcome == SKIP
    assert result.outcome != PASS
    payload = result.to_json_obj()
    assert payload["code"] == "DATA.PROBE.SKIPPED"
    assert "FMP_API_KEY" in payload["skipped_reason"]


def test_an_empty_probe_is_a_skip_not_a_pass():
    """DE-40's corollary — zero checks is not success, it is nothing happening."""
    assert ProbeResult().outcome == SKIP


def test_a_single_failed_check_fails_the_whole_probe():
    """DE-39 — every intermediate is compared, so any one of them can fail it."""
    result = ProbeResult()
    result.record("K-2", PASS, 120890, 120890)
    result.record("K-3", FAIL, 41238600, 412386000, "vendor volume, x10")
    assert result.outcome == FAIL


@pytest.mark.live
def test_ac_7_54_the_probe_fetches_from_fmp_over_the_network(request):
    """AC-7.54 / AC-7.55 — DE-37, DE-38, DE-39.

    Fetches over the network and digests through the **real code path** — no
    fixture, no mock, no cassette. It builds the panel through
    `build_price_panel` rather than reading the vendor's adjusted series, because
    the intermediate that matters is **our derived factor**: a probe that
    compared FMP against FMP would confirm the vendor and verify nothing about
    this code.
    """
    key = os.environ.get("FMP_API_KEY")
    if not key:
        # DE-40: the skip is LOUD. pytest reports it in the run summary with this
        # reason attached, which is the "reported as skipped" the rule demands.
        pytest.skip(
            "DATA.PROBE.SKIPPED — FMP_API_KEY is unset, so the live reality probe "
            "did NOT run. This is a gap in verification, not a pass (DE-40)"
        )

    result = run_probe(FMPClient(Secret("FMP_API_KEY", key)))
    failures = [c for c in result.checks if c["outcome"] == FAIL]
    assert result.outcome == PASS, (
        "the live probe disagrees with §6A.5's known-answer set. ⚠ F3 §4c applies: "
        "NEITHER is assumed right until it is established which is wrong. "
        f"Failures: {failures}"
    )
    assert {c["id"] for c in result.checks} >= {"K-1", "K-2", "K-3", "K-4", "K-5"}


# --------------------------------------------------------------------------- #
# DE-47 — the day-T opening print. AC-7.63, AC-7.64
# --------------------------------------------------------------------------- #

def test_ac_7_63_a_collapsed_row_is_refused_never_returned():
    """AC-7.63 / DE-47 — ★★ *the running price wearing a bar's shape.*

    ⚠ This is `main_inference.py:250` verbatim: it set all five OHLC fields to
    one spot quote, making the day-T **intraday range identically zero** on the
    one bar that drives the decision, while every training bar has a real range.
    """
    from datetime import date, datetime, timezone

    import pytest

    from src.data_engine.errors import DataError
    from src.data_engine.observation.day_open import day_open

    flat = {"open": 12050, "high": 12050, "low": 12050, "close": 12050}
    with pytest.raises(DataError, match="running price wearing a bar's shape"):
        day_open(ticker="NVDA", as_of=date(2026, 8, 25), row=flat,
                 now=datetime(2026, 8, 25, 14, 0, tzinfo=timezone.utc))


def test_ac_7_64_an_unsettled_open_is_never_backfilled():
    """AC-7.64 / DE-47, OR-33 — ★ *never substituted with the previous close:
    that substitution is silent and makes the decision a day stale while looking
    current.*"""
    from datetime import date, datetime, timezone

    from src.data_engine.observation.day_open import day_open

    # 09:00 ET — before the bell.
    early = day_open(ticker="NVDA", as_of=date(2026, 8, 25), row=None,
                     now=datetime(2026, 8, 25, 13, 0, tzinfo=timezone.utc))
    assert early.settled is False and early.open_minor is None
    assert "has not settled" in early.why
    assert early.as_precondition_bar() is None      # ⇒ D-08 blocks


def test_the_print_carries_the_open_and_states_the_absence_of_the_rest():
    """DE-47 / OR-47 — ★ `high`/`low`/`close` are **the absence of a settled
    value, stated** — not missing fields, and not fabricated ones."""
    from datetime import date, datetime, timezone

    from src.data_engine.observation.day_open import day_open

    row = {"open": 11977, "high": 12100, "low": 11900, "close": 12050,
           "currency": "USD"}
    settled = day_open(ticker="NVDA", as_of=date(2026, 8, 25), row=row,
                       now=datetime(2026, 8, 25, 14, 0, tzinfo=timezone.utc))
    bar = settled.as_precondition_bar()
    assert bar["open"] == 11977 and bar["settled"] is True
    assert bar["high"] is None and bar["low"] is None and bar["close"] is None

    # ★ and D-08 accepts it — OR-47.
    from src.orchestration.schedule.preconditions import assert_open_confirmed

    assert assert_open_confirmed(bar, as_of=date(2026, 8, 25)).ok


@pytest.mark.live
def test_de47_the_vendor_intraday_bar_is_not_collapsed_and_that_is_the_point():
    """★★ **CT-3.2 reality probe** — the record F3 §4b requires.

    | Field | Value |
    |---|---|
    | **entry point** | `historical-price-eod/full`, NVDA, `from=to=today` |
    | **ground truth** | FMP live, measured 2026-08-25 14:42 ET, mid-session |
    | **intermediate** | `open 211.025 · high 214.7291 · low 210.11 · close 212.855` |
    | **verdict** | ⚠ **a plausible, NON-collapsed bar whose `close` is the running price** |

    ★ So **collapse-detection is necessary and not sufficient.** The legacy
    defect was detectable because it wrote one spot quote into five fields; the
    vendor's own in-progress row is not detectable that way at all — which is
    why DE-47 keys on *has the session closed* and takes **the open alone**.
    """
    import os
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    import src.data_engine.src.fmp.prices as prices
    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret

    key = os.environ.get("FMP_API_KEY")
    if not key:
        pytest.skip("FMP_API_KEY not set")

    et = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
    client = FMPClient(Secret("FMP_API_KEY", key))
    payload = client.get(prices.VENDOR_ADJUSTED_ENDPOINT, symbol="NVDA",
                         **{"from": str(et.date()), "to": str(et.date())})
    rows = prices._rows(payload)
    if not rows:
        pytest.skip(f"no NVDA row for {et.date()} — not a trading day")

    row = rows[0]
    fields = [row.get(f) for f in ("open", "high", "low", "close")]
    if all(f is not None for f in fields):
        # ⚠ The finding: the vendor does NOT collapse the bar, so a guard that
        #   only looks for equality would pass an in-progress row unchallenged.
        assert len(set(fields)) > 1, (
            "if FMP ever DOES collapse the bar, DE-47's reasoning changes and "
            "this test is the place that will say so")
