"""D-07 — Class-B capture into the ObservationLedger. DE-6.8/6.9/6.10."""
from datetime import date, datetime, timezone

from src.data_engine.ingest.observations import (
    THESIS_FIELD_SETS, capture, is_due,
)
from src.data_engine.observation.ledger import ObservationLedger


class _Client:
    def __init__(self, payload=None, fail=()):
        self.payload = payload if payload is not None else [{"symbol": "NVDA", "beta": 2.2}]
        self.fail = set(fail)
        self.asked = []

    def get(self, endpoint, **params):
        self.asked.append(endpoint)
        if endpoint in self.fail:
            raise RuntimeError("endpoint unavailable")
        return self.payload


def test_a_first_capture_writes_every_thesis_field_set(tmp_path):
    """★★ `snapshot()` existed and **nothing ever called it** — the same shape as
    the fact ledger and the two run stores: a correct writer with no caller."""
    ledger = ObservationLedger(tmp_path)
    written = capture(_Client(), ledger, ticker="NVDA", as_of=date(2026, 8, 26))
    assert set(written) == set(THESIS_FIELD_SETS)
    assert all(written.values())


def test_a_second_capture_inside_the_cadence_writes_nothing(tmp_path):
    """⚠ `DEFAULT_SCHEDULE`'s intervals are *admitted guesses* (CN-10) and are
    used as declared, not replaced with better-sounding ones."""
    ledger = ObservationLedger(tmp_path)
    capture(_Client(), ledger, ticker="NVDA", as_of=date(2026, 8, 26))
    again = capture(_Client(), ledger, ticker="NVDA", as_of=date(2026, 8, 26))
    assert not any(again.values())


def test_a_capture_past_the_cadence_writes_again(tmp_path):
    """★ `profile` is on a 30-day cadence — near-static, not frozen."""
    ledger = ObservationLedger(tmp_path)
    capture(_Client(), ledger, ticker="NVDA", as_of=date(2026, 8, 26))
    later = capture(_Client([{"symbol": "NVDA", "beta": 9.9}]), ledger,
                    ticker="NVDA", as_of=date(2026, 11, 1))
    assert later["profile"] is True


def test_one_failed_endpoint_does_not_cost_the_others(tmp_path):
    """P5 — the failure is visible as `False`; ★ it does not abort the sweep."""
    ledger = ObservationLedger(tmp_path)
    written = capture(_Client(fail={"ratios-ttm"}), ledger, ticker="NVDA",
                      as_of=date(2026, 8, 26))
    assert written["ratios_ttm"] is False
    assert written["profile"] is True


def test_a_one_element_list_is_unwrapped(tmp_path):
    """⚠ FMP answers these as a ONE-ELEMENT LIST. Storing the list makes every
    consumer index into it, and a day the vendor returns two elements silently
    changes meaning."""
    ledger = ObservationLedger(tmp_path)
    capture(_Client(), ledger, ticker="NVDA", as_of=date(2026, 8, 26))
    got = ledger.get(ticker="NVDA", field_set="profile", consumer="display")
    assert isinstance(got["payload"], dict) and got["payload"]["beta"] == 2.2


def test_the_scheduler_reads_as_display_not_as_a_pit_consumer(tmp_path):
    """★★ DE-6.9 denies a Class-B live read to a PIT consumer. ⚠ Asking *"when
    did we last look?"* is scheduling, not a PIT read — a PIT consumer name here
    makes the scheduler raise on exactly the field sets it exists to schedule."""
    ledger = ObservationLedger(tmp_path)
    assert is_due(ledger, ticker="NVDA", field_set="profile",
                  as_of=date(2026, 8, 26), cadence_days=30) is True


def test_consensus_field_sets_are_deliberately_not_captured():
    """★ RA-12/RA-19 — a thesis that reads the consensus before forming a view
    is measuring agreement, not the business."""
    for opinion in ("analyst_estimates", "price_target_consensus",
                    "grades_consensus"):
        assert opinion not in THESIS_FIELD_SETS


# --------------------------------------------------------------------------- #
# DE-53 — the PIT cutoff is an ET trading day, not a UTC one
# --------------------------------------------------------------------------- #

def test_ac_7_70_an_evening_capture_is_visible_to_that_days_run(tmp_path):
    """★★ DE-53 — ⚠ *the failure was silent and self-inflicted*: a run captured a
    profile at 22:50 ET, wrote it, read back `None`, and assembled the bundle
    without it. **"Nothing was captured" and "it was captured four hours ago"
    were indistinguishable.**"""
    ledger = ObservationLedger(tmp_path)
    evening_et = datetime(2026, 8, 27, 2, 50, tzinfo=timezone.utc)   # 22:50 ET
    ledger.snapshot(ticker="NVDA", field_set="profile", payload={"a": 1},
                    source_endpoint="fmp:profile", observed_at=evening_et)
    assert ledger.get(ticker="NVDA", field_set="profile",
                      as_of=date(2026, 8, 26), consumer="display") is not None


def test_ac_7_70_the_next_days_capture_is_still_invisible(tmp_path):
    """⚠ INV-1 — widening the cutoff to the ET close must not widen it past
    the close. A capture on T+1 is future evidence for a run dated T."""
    ledger = ObservationLedger(tmp_path)
    next_day = datetime(2026, 8, 27, 14, 0, tzinfo=timezone.utc)     # 10:00 ET T+1
    ledger.snapshot(ticker="NVDA", field_set="profile", payload={"a": 1},
                    source_endpoint="fmp:profile", observed_at=next_day)
    assert ledger.get(ticker="NVDA", field_set="profile",
                      as_of=date(2026, 8, 26), consumer="display") is None


def test_ac_7_70_the_cutoff_is_the_market_close_not_utc_midnight():
    """★ `MARKET_TZ` already existed in `observation/day_open.py` and
    `orchestration/schedule/cadence.py`; the ledger simply did not use it."""
    from src.data_engine.observation.ledger import end_of_day_utc

    cutoff = end_of_day_utc(date(2026, 8, 26))
    assert cutoff.isoformat().startswith("2026-08-27T04:00")
