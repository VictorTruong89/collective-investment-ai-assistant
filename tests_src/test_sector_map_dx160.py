"""DX-160 — the sector map reaches training and the daily run; unknown sectors are null.

DE-77 / AC-7.95 · FE-41 / AC-2.48 · MT-55 / AC-4.37 · OR-56 / AC-8.44.
✏ Written 2026-10-07 (Victor: *"supply the sector map to training, fix DX-160"*).

⚠ Found writing lecture L8: training passed no sectors, `sector_z` grouped the `None`s together,
and the five `*_sector_z` features were MARKET-wide z-scores under sector-relative names.
"""

from __future__ import annotations

import inspect

import pandas as pd

# ── AC-7.95 · DE-77 — one sector map ─────────────────────────────────────────

def test_ac_7_95_the_configured_map_covers_the_universe():
    from src.data_engine.ingest.edgar_facts import load_cik_map, load_sector_map

    sectors = load_sector_map()
    assert set(load_cik_map()) <= set(sectors), "every routed name has a sector"
    assert sectors["AAPL"] == "Information Technology"
    assert sectors["ADM"] == "Consumer Staples"
    assert all(k == k.upper() for k in sectors)


def test_ac_7_95_an_absent_name_is_absent_never_defaulted(tmp_path):
    from src.data_engine.ingest.edgar_facts import load_sector_map

    path = tmp_path / "u.yaml"
    path.write_text("sector_map:\n  aapl: Information Technology\n  XOM: ''\n", encoding="utf-8")
    assert load_sector_map(str(path)) == {"AAPL": "Information Technology"}


# ── AC-2.48 · FE-41 — unknown sector is null, never a bucket ─────────────────

def _panel(n=4):
    return pd.DataFrame({"ticker": [f"T{i}" for i in range(n)],
                         "date": pd.to_datetime(["2024-01-02"] * n)})


def test_ac_2_48_no_map_at_all_gives_null():
    from src.feature_engineer.fundamental.build import _aligned
    from src.feature_engineer.fundamental.growth import sector_z

    panel = _panel()
    out = sector_z(panel, pd.Series([1.0, 2.0, 3.0, 4.0]), _aligned(panel, None, default=None))
    assert out.isna().all(), "the DX-160 shape: a market-wide z under a sector name"


def test_ac_2_48_a_name_with_no_sector_is_null_and_others_are_scored_within_sector():
    from src.feature_engineer.fundamental.growth import sector_z

    panel = _panel(7)
    sectors = pd.Series(["Tech", "Tech", "Tech", "Energy", "Energy", "Energy", None])
    out = sector_z(panel, pd.Series([1.0, 2.0, 3.0, 10.0, 20.0, 30.0, 5.0]), sectors)
    assert pd.isna(out.iloc[6])
    assert out.iloc[:3].round(6).tolist() == out.iloc[3:6].round(6).tolist() == [-1.0, 0.0, 1.0]


def test_ac_2_48_the_block_is_null_without_sectors_and_filled_with_them():
    import numpy as np

    from src.feature_engineer.fundamental.build import build

    rows = []
    for t, margin in zip(["A", "B", "C", "D"], [0.1, 0.2, 0.3, 0.4], strict=True):
        rows.append({"ticker": t, "period_end": pd.Timestamp("2023-12-31"),
                     "period_type": "quarterly",
                     "filing_date": pd.Timestamp("2024-02-01").as_unit("ns"),
                     "accession_id": f"{t}-1", "Revenues_minor": 100_000,
                     "NetIncomeLoss_minor": int(100_000 * margin)})
    by_ticker = {r["ticker"]: pd.DataFrame([r]) for r in rows}
    panel = pd.DataFrame({"ticker": ["A", "B", "C", "D"],
                          "date": pd.to_datetime(["2024-03-01"] * 4).astype("datetime64[ns]")})
    bare = build(panel, rows_by_ticker=by_ticker)
    assert bare["f_net_margin_sector_z"].isna().all()
    filled = build(panel, rows_by_ticker=by_ticker,
                   sectors=dict.fromkeys(["A", "B", "C", "D"], "Tech"))
    assert np.isfinite(filled["f_net_margin_sector_z"].astype(float)).all()


# ── AC-4.37 · MT-55 and AC-8.44 · OR-56 — both paths read the one map ────────

def test_ac_4_37_training_builds_the_panel_with_the_sector_map():
    from src.models.train import __main__ as train

    body = inspect.getsource(train._train)
    assert "load_sector_map()" in body and "sectors=" in body


def test_ac_8_44_the_daily_run_reads_the_same_map(monkeypatch):
    from src.orchestration import entrypoint

    monkeypatch.setattr("src.data_engine.ingest.edgar_facts.load_sector_map",
                        lambda *a, **k: {"AAPL": "Information Technology", "XOM": "Energy"})
    assert entrypoint._sectors_for(None, ("AAPL", "ZZZZ"), None) == {
        "AAPL": "Information Technology"}
