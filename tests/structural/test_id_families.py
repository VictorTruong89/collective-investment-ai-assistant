"""`MS-8.7` — the ID-family registry is complete and enforced."""

from __future__ import annotations

import pathlib

from tools.check_id_families import (
    MIN_USES,
    declared_families,
    families_in_use,
    undeclared,
)


def test_ms_8_7_every_family_in_use_is_declared_in_the_constitution():
    """⚠⚠ §1 says *'every family below is reserved'* — only true if complete.

    At `MS-8` it was ~50% incomplete: **39 families in active use, named
    nowhere** — after §1 had already been corrected once for missing eleven.
    """
    assert undeclared() == {}


def test_ms_8_7_the_registry_covers_both_repos_id_spaces():
    """★ The merge put ~40 families in one tree; the check must see them all."""
    fams = families_in_use()
    for expected in ("RA", "QA", "OR", "DE", "RC", "PG", "QR", "MS", "DX", "AC"):
        assert fams[expected] >= MIN_USES, f"{expected} should be in heavy use"
    assert len(declared_families()) >= 40


def test_ms_8_7_an_undeclared_family_is_caught(tmp_path):
    """⚠ BS-5 — the rule needs a case that fails it.

    ★ Simulated with a scratch tree so the real registry is not disturbed.
    """
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.py").write_text(
        "\n".join(f"# ZZ-{i} a family nobody declared" for i in range(MIN_USES + 5)))
    for d in ("sdd", "tests", "tests_src", "tools"):
        (tmp_path / d).mkdir()
    (tmp_path / "sdd" / "specs").mkdir(parents=True)
    assert "ZZ" in undeclared(tmp_path)


def test_ms_8_7_the_seat_collision_is_documented():
    """⚠⚠ `SEAT-n` is upstream's FIVE-seat model; this repo has NINE.

    ★ `CLAUDE.md`: *"Never carry a seat number between the two repos."* Now that
    both ID spaces live in one tree that is easier to violate — an absorbed test
    already did (`DX-10`).
    """
    con = pathlib.Path("sdd/specs/constitution.md").read_text(encoding="utf-8")
    sec1 = con[con.index("# 1."):con.index("# 2.")]
    assert "SEAT-n" in sec1
    assert "five-seat" in sec1.lower() and "nine" in sec1.lower()
