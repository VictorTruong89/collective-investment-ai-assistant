"""★ The consensus part reaches the Stage B–D bundle, and only its absence is lifted.

`L3` §2.1p item 5 (Victor, 2026-10-01). Built from the real MU fixtures.
"""

from __future__ import annotations

import json
import pathlib
from datetime import date

REPO = pathlib.Path(__file__).resolve().parents[2]
AS_OF = date(2025, 6, 26)


def test_mu_has_a_consensus_part_built_from_its_fixtures():
    from tools.run_thesis_once import consensus_for

    part = consensus_for("MU", AS_OF)
    assert part is not None and part.kind == "computed"
    assert part.pins["contract_name"] == "consensus.as_of"
    assert "CONSENSUS AS OF 2025-06-26" in part.content


def test_the_real_mu_part_matches_the_previewed_numbers():
    """The 2026-10-01 preview, now from the version-controlled fixtures: 23 firms rated
    MU in the 12 months before, the 2025-06-25 report beat at $1.91 vs $1.60, and every
    price target in the window sits above the $126.00 raw close."""
    from src.fundamental.bundle.consensus import consensus_as_of

    root = REPO / "tests_src/fixtures/consensus"
    load = lambda n: json.loads((root / f"MU_{n}.json").read_text())  # noqa: E731
    s = consensus_as_of(grades=load("grades"), targets=load("price_target_news"),
                        earnings=load("earnings"), as_of=AS_OF)
    assert len(s["ratings"]["latest_by_firm"]) == 23 and not s["ratings"]["unmapped"]
    assert s["ratings"]["by_bucket"]["buy"] > s["ratings"]["by_bucket"]["sell"]
    last = s["earnings"]["reports"][-1]
    assert (last["date"], last["eps_estimated"], last["eps_actual"]) == ("2025-06-25", 1.6, 1.91)
    assert s["price_targets"]["n"] >= 3 and s["price_targets"]["low"] > 126.0


def test_a_ticker_without_fixtures_keeps_the_absence_declared(tmp_path):
    from tools.run_thesis_once import CONSENSUS_FILLS, consensus_for, stage_b_absences

    assert consensus_for("ZZZZ", AS_OF, fixtures=tmp_path) is None
    assert CONSENSUS_FILLS in stage_b_absences(has_consensus=False)


def test_only_the_ratings_absence_is_lifted_forward_estimates_stay_absent():
    from tools.run_thesis_once import CONSENSUS_FILLS, stage_b_absences

    supplied = stage_b_absences(has_consensus=True)
    assert CONSENSUS_FILLS not in supplied
    assert "consensus_forward_estimates" in supplied


def test_the_meta_sidecar_states_provenance_and_hazards():
    meta = json.loads((REPO / "tests_src/fixtures/consensus/MU.meta.json").read_text())
    assert meta["fetched_at"] and meta["rows"]["grades"] > 0
    assert any("lastUpdated" in h for h in meta["hazards"])
