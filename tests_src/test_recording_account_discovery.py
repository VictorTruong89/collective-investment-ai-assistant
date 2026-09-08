"""D-11 `RC-65`/`RC-66` — the account set is discovered, not listed. `AC-11.47/48`.

⚠⚠ **Why this exists.** `ACCOUNTS` was a hardcoded 4-tuple, so a fifth statement
dropped into the export directory was **silently ignored**: not read, not
refused, not mentioned. ★ The new portfolio would simply not exist, and
`RK-5`'s all-or-nothing aggregation would still return a book — looking healthy.

★ `RRSP_2` is planned for 2027. This makes it a **file drop**, not a code edit.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.recording.book.load import (
    EXPORT_DIR, discover_accounts, export_path, load_books,
)
from src.recording.errors import RecordingError

HEADER = ("Transaction Date,Settlement Date,Activity Description,Description,"
          "Symbol,Quantity,Price,Price Currency,Total Amount,Total Currency")
ROW = "2026-01-05,2026-01-07,Contribution,CONTRIBUTION,,0,0,CAD,1000.00,CAD"


def _dir(tmp_path, accounts):
    d = tmp_path / "exports"
    d.mkdir()
    for a in accounts:
        (d / f"TransactionHistory_{a}.csv").write_text(f"{HEADER}\n{ROW}\n")
    return d


# --------------------------------------------------------------------------- #
# AC-11.47 — n accounts, whatever n is
# --------------------------------------------------------------------------- #
def test_ac_11_47_the_four_real_accounts_are_discovered(tmp_path):
    d = _dir(tmp_path, ("RESP_1", "RRSP_1", "TFSA_1", "TFSA_2"))
    assert discover_accounts(d) == (("RESP_1", "RESP"), ("RRSP_1", "RRSP"),
                                    ("TFSA_1", "TFSA"), ("TFSA_2", "TFSA"))


def test_ac_11_47_a_FIFTH_account_needs_no_code_change(tmp_path):
    """★★ The whole point — `RRSP_2` in 2027 is a file drop."""
    d = _dir(tmp_path, ("RESP_1", "RRSP_1", "RRSP_2", "TFSA_1", "TFSA_2"))
    found = discover_accounts(d)
    assert len(found) == 5
    assert ("RRSP_2", "RRSP") in found, "the type comes from the id's prefix (H-5)"


def test_ac_11_47_the_registered_type_comes_from_the_filename(tmp_path):
    """`H-5` — *registered status is not a field; the naming convention carries it.*"""
    d = _dir(tmp_path, ("RESP_9", "RRSP_3", "TFSA_7"))
    assert dict(discover_accounts(d)) == {"RESP_9": "RESP", "RRSP_3": "RRSP",
                                          "TFSA_7": "TFSA"}


def test_ac_11_47_discovery_is_sorted_so_the_book_is_deterministic(tmp_path):
    """⚠ `INV-2` — two runs on the same directory must derive the same book."""
    d = _dir(tmp_path, ("TFSA_2", "RESP_1", "RRSP_1"))
    assert discover_accounts(d) == tuple(sorted(discover_accounts(d)))


def test_ac_11_47_an_unrelated_file_is_ignored(tmp_path):
    d = _dir(tmp_path, ("TFSA_1",))
    (d / "README.md").write_text("notes")
    (d / "balances.csv").write_text("not a transaction history")
    assert discover_accounts(d) == (("TFSA_1", "TFSA"),)


# --------------------------------------------------------------------------- #
# AC-11.48 — empty RAISES; it never derives an empty book
# --------------------------------------------------------------------------- #
def test_ac_11_48_an_empty_directory_raises_and_names_it(tmp_path):
    """⚠⚠ *'No accounts found' and 'this book holds nothing' are different facts.*

    `RK-5` withholds a book-wide figure when one account cannot price — so an
    empty derivation would read as a healthy refusal rather than a missing input.
    """
    empty = tmp_path / "nothing"
    empty.mkdir()
    with pytest.raises(RecordingError, match="no broker exports"):
        discover_accounts(empty)


def test_ac_11_48_a_missing_directory_raises_too(tmp_path):
    with pytest.raises(RecordingError, match="no broker exports"):
        discover_accounts(tmp_path / "does_not_exist")


def test_ac_11_48_load_books_returns_a_REASON_and_never_crashes(tmp_path):
    """⚠⚠ The other half — and the two are not in tension.

    `discover_accounts` raises because at that layer *"no accounts"* is an error.
    `load_books` must **not**: its contract is `RC-10`/`RK-5` — *carry the
    refusal forward as a reason*, because *a refusal that cannot say what it
    lacks is the defect RC-10 exists to prevent*.

    ★ Found by the fresh-clone check: raising here turned an orchestration job
    from `SUCCESS` into `FAILED`.
    """
    books, reason = load_books(as_of=date(2026, 9, 4),
                               root=str(tmp_path / "missing"))
    assert books == ()
    assert "no broker exports" in reason, "the reason must NAME what is missing"


# --------------------------------------------------------------------------- #
# RC-66 — the exports live outside the spec tier
# --------------------------------------------------------------------------- #
def test_rc_66_the_default_export_dir_is_state_not_the_spec_tier():
    """⚠ The book of record must not live in `sdd/` — the tier that governs code."""
    assert EXPORT_DIR.startswith(".state/broker/")
    assert "sdd/" not in EXPORT_DIR


def test_rc_66_export_path_still_builds_the_documented_filename(tmp_path):
    assert export_path(tmp_path, "RRSP_2").name == "TransactionHistory_RRSP_2.csv"
