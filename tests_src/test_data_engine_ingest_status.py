"""D-07 — DE-73 / AC-7.91: `ingest status` tells the truth about which sweep covers which class.

✏ Written 2026-10-06 (`DX-157`). `status` decided "built or not" from `events.SOURCED` (four
classes), so eleven classes `ingest events` DOES record were labelled "no ingest built".
Hermetic: an empty event store in a tmp directory; no network.
"""

from __future__ import annotations


def test_ac_7_91_every_class_is_swept_derived_or_permanently_unchecked():
    """★ No class may fall through to "no ingest built" while a sweep records it — and
    every class must have SOME account of how it is covered."""
    from src.data_engine.calendar.classes import EVENT_CLASSES
    from src.data_engine.ingest.__main__ import DERIVED_AT_CHECK, SWEPT_BY

    swept = {c for classes in SWEPT_BY.values() for c in classes}
    names = {c.name for c in EVENT_CLASSES}
    permanent = {c.name for c in EVENT_CLASSES if c.permanently_unchecked}
    assert swept <= names, f"SWEPT_BY names unknown classes: {swept - names}"
    unaccounted = names - swept - set(DERIVED_AT_CHECK) - permanent
    assert unaccounted == set(), f"no sweep, derivation or flag covers {unaccounted}"


def test_ac_7_91_swept_by_is_composed_from_the_modules_own_constants():
    """Drift guard — the map is built from what each ingest module declares, so adding a
    class to one of them reaches `status` with no second edit."""
    from src.data_engine.ingest.__main__ import SWEPT_BY
    from src.data_engine.ingest.events import SOURCED
    from src.data_engine.ingest.submissions import SUBMISSION_CLASSES

    assert set(SOURCED) | set(SUBMISSION_CLASSES) <= set(SWEPT_BY["events"])
    assert "ticker_change" in SWEPT_BY["symbols"]


def test_ac_7_91_status_names_the_sweep_and_never_says_no_ingest_for_a_swept_class(
        tmp_path, monkeypatch, capsys):
    """On an empty store every sweepable class reads "never swept — run `ingest events`"
    (or `symbols`), not "no ingest built"."""
    from src.data_engine.ingest.__main__ import main

    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path / "state"))
    assert main(["status"]) == 0
    out = capsys.readouterr().out
    lines = {ln.split()[1]: ln for ln in out.splitlines()
             if ln.startswith("    ") and len(ln.split()) > 1}
    for name in ("earnings_reported", "ma_announcement", "material_event_8k", "news"):
        assert "no ingest built" not in lines[name], lines[name]
        assert "ingest events" in lines[name], lines[name]
    assert "ingest symbols" in lines["ticker_change"]
    assert "no ingest built" not in out
