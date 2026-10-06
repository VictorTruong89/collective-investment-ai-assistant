"""`DX-53` — ★★ a traceability row is a CLAIM, and this resolves it.

⚠⚠ Constitution §6 says a row must **exist**. Nothing said it had to be **true**.

★★★ Measured 2026-09-09: six specs were completed that day and in every one a
structural AC was unenforced **behind a row that read as coverage** — five named
a tool that did not exist, one named a tool that existed and checked a different
fence. ⚠ The rows are written by the same hand as the code, so they agree by
construction: constitution §5.1's illegal move displaced one level up.

★★ **The limit travels with the check.** It resolves that a named file and test
EXIST. It cannot verify the named test *tests the named AC* — `AC-6a.6` named a
real file that checked the wrong thing, and no file-resolver finds that.
"""

from __future__ import annotations

import pathlib

import pytest

from tools.check_traceability_rows import _file_exists, check

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_dx53_every_traceability_row_resolves():
    """The live tree, all 148 rows. ⚠ No skip, no tolerance list."""
    assert check() == []


def test_dx53_the_check_covers_every_spec_and_every_row():
    """⚠ A resolver pointed at the wrong section passes forever."""
    from tools.check_traceability_rows import _iter_rows
    rows = list(_iter_rows())
    specs = {s.parent.name for s, _ in rows}
    # ✏ 2026-09-13 — `F10` (17 ACs) joined. ⚠ Still pinned on purpose: a spec that
    #   loses its table must turn this red, and a count that silently grew would too.
    # ✏ 2026-10-05 — `F12` (30 ACs, 🟡 draft) joined.
    assert len(rows) == 210, "148 + F10's 23 + F11's 9 + F12's 30 ACs, one row each (F12 drafted 2026-10-05)"
    assert len(specs) == 14, "all fourteen specs carry a table (F12 joined 2026-10-05)"


# ── ⓑ basename fallback — the decision that made this shippable ───────────
def test_dx53_an_exact_repo_relative_path_resolves():
    assert _file_exists("tools/check_all.py", set())


def test_dx53_a_BASENAME_resolves_even_when_the_path_is_shorthand():
    """★★ Option ⓑ (Victor, 2026-09-09). Rows legitimately abbreviate —
    `.../corroborate.py`, a bare `check_import_fences.py`.

    ⚠ Option ⓐ (strict repo-relative paths) would have made ~30 honest rows
    illegal to buy nothing: all three of the prototype's false positives were
    shorthand for files that **do** exist.
    """
    assert _file_exists("anything/at/all/check_all.py", {"check_all.py"})


def test_dx53_a_GLOB_resolves_to_its_directory():
    """⚠ `src/shared/ports/*.py` — an AC satisfied by a directory, not a module.
    ★ This was the check's FIRST false positive, on its first run: treating a
    glob as a literal filename is exactly the over-strictness ⓑ avoids."""
    assert _file_exists("src/shared/ports/*.py", set())
    assert not _file_exists("src/shared/ports/*.rs", set())


def test_dx53_a_genuinely_missing_file_does_NOT_resolve():
    """⚠ The check must be able to FAIL, or it is decoration."""
    assert not _file_exists("src/data_engine/corporate_actions/corroborate.py",
                            {"classify.py", "models.py"})


# ── the six real historical failures, replayed ────────────────────────────
@pytest.mark.parametrize("named", [
    "tools/check_no_reimplementation.py",       # F9  AC-F9.2
    "tools/check_gate_ordering.py",             # F7a AC-7a.1
    "tools/check_no_raw_directive_in_prompt.py",  # F8  AC-8.16
    "tools/check_no_tier_b_gating.py",          # F7b AC-7b.5
])
def test_dx53_the_tools_that_were_MISSING_now_exist(named):
    """★★ Four of the six failures were *"the row names a tool that does not
    exist"*. ⚠ This asserts the fix stays fixed — deleting any of these would
    now red the suite instead of quietly un-enforcing an AC."""
    assert (REPO / named).exists(), f"{named} is named by a traceability row"


def test_dx53_the_check_would_have_caught_a_missing_tool(tmp_path, monkeypatch):
    """★ The counterfactual, proven rather than asserted."""
    import tools.check_traceability_rows as mod

    spec_dir = tmp_path / "sdd" / "specs" / "F99_probe"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# F99\n\n## 9. Traceability\n\n| AC | Test | Code |\n|---|---|---|\n"
        "| AC-99.1 | `tests/test_nope.py::test_x` | `tools/never_written.py` |\n")
    monkeypatch.setattr(mod, "SPECS", tmp_path / "sdd" / "specs")
    monkeypatch.setattr(mod, "REPO", tmp_path)
    hits = mod.check()
    assert any("never_written.py" in h for h in hits)


def test_dx53_a_renamed_test_leaves_the_row_STALE_and_is_caught(tmp_path, monkeypatch):
    """★★ The second half, and it is not hypothetical: `F9`'s rename turned
    every `test_ac_9_4_*` into `test_ac_f9_4_*` on 2026-09-09. ⚠ A table still
    naming the old function would assert coverage that no longer exists under
    that name."""
    import tools.check_traceability_rows as mod

    spec_dir = tmp_path / "sdd" / "specs" / "F99_probe"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# F99\n\n## 9. Traceability\n\n| AC | Test | Code |\n|---|---|---|\n"
        "| AC-99.1 | `tools/check_all.py::test_this_was_renamed_away` | `tools/check_all.py` |\n")
    monkeypatch.setattr(mod, "SPECS", tmp_path / "sdd" / "specs")
    monkeypatch.setattr(mod, "REPO", REPO)
    assert any("renamed or deleted" in h for h in mod.check())


def test_dx53_the_stated_limit_is_in_the_module_docstring():
    """⚠⚠ `PG-10`'s shape — a claim carries its subject's status.

    ★ The check CANNOT verify that a named test tests its AC. `AC-6a.6` named a
    real file that checked the wrong fence, and this would have passed it. That
    limit is stated where a reader of the tool will meet it, not only here.
    """
    import tools.check_traceability_rows as mod
    # ⚠ Whitespace-normalised: the phrase is line-wrapped in the docstring, and
    #   a raw substring test failed on its own first run — asserting against
    #   prose formatting rather than against what the prose SAYS.
    doc = " ".join((mod.__doc__ or "").split())
    assert "It cannot verify that the named test" in doc
    assert "no file-resolver finds that" in doc
