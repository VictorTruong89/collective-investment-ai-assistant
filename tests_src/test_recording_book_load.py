"""D-11 §5 — loading the four BMO InvestorLine exports into book states.

⏸ **RC-58.** Every assertion about *today's* outcome here is an assertion about
a postponement, not about the code: Canadian listings and CDRs are unvalued
until the rest of the release is complete.
"""
from datetime import date

from src.recording.book.load import (
    discover_accounts, held_instruments, load_books, quote_holdings,
    resolve_export_dir,
)
from tests_src.broker_fixtures import requires_real_statements

# ⚠⚠ DX-5 — every test below reads the REAL BMO exports, which are NOT in git.
# They check derived numbers against EXTERNAL TRUTH (CT-3.2) — which is exactly
# what makes them worth having, and exactly why they cannot be synthesised: a
# synthetic external-truth check asserts a property of invented data while
# LOOKING like validation. So they skip loudly instead.
#
# ★ Structural parsing — column layouts, zero totals, dotted tickers, unknown
#   activities, foreign rows, CDR-vs-common — IS covered on any clone by
#   tests_src/test_recording_ingest_synthetic.py against tracked fixtures.
pytestmark = requires_real_statements



AS_OF = date(2026, 8, 25)


def test_every_registered_account_present_is_loaded():
    """RC-25 — ★ M-4 has no exempt population, so the loader has no short list.

    ✏ **Rewritten 2026-09-04 (`RC-65`).** ⚠⚠ This test asserted
    `[a for a, _ in ACCOUNTS] == ["RESP_1", "RRSP_1", "TFSA_1", "TFSA_2"]` —
    **a short list** — while its own docstring argued that *the loader has no
    short list*. ★ The docstring was right and the assertion contradicted it:
    a hardcoded four made a fifth statement **silently invisible**, which is the
    opposite of "no exempt population".

    It now asserts what it always claimed: **whatever accounts are present are
    loaded, and every one of them is registered.**
    """
    found = discover_accounts(resolve_export_dir())
    assert found, "at least one export must be present for this test to mean anything"
    # RC-25 — all account types in this book are REGISTERED. That is the real claim.
    assert {t for _, t in found} <= {"RESP", "RRSP", "TFSA"}
    # ⚠ and the four real ones are here today — stated as an observation of the
    # data, NOT as a constraint on how many accounts may exist (RC-65).
    assert {a for a, _ in found} >= {"RESP_1", "RRSP_1", "TFSA_1", "TFSA_2"}


def test_held_instruments_spans_every_account():
    """RC-9 — the holdings are derived from activity, across all four books."""
    held = held_instruments()
    assert "MDA|COMMON|CAD" in held        # TFSA_1
    assert "MRV|CDR|CAD" in held           # RESP_1
    assert "DELL|COMMON|USD" in held       # ★ US common, outside the universe


def test_quote_holdings_never_attempts_a_postponed_symbol():
    """⏸ RC-58 / DE-49 — ⚠ firing a request per CAD name would turn a declared
    pause into a string of 402s that reads like a fault."""
    asked = []

    def fetch(symbol):
        asked.append(symbol)
        return 100.0, "USD"

    quote_holdings(fetch)
    assert asked, "it must price the US common stock it holds"
    assert not [s for s in asked if s.endswith((".TO", ".NE"))]
    assert "MDA" not in asked and "MRV" not in asked


def test_one_unpriceable_account_withholds_all_four():
    """★★ RK-5's aggregation rule, one level up. ⚠ *A book-wide figure computed
    over the accounts that happened to price is not a partial answer, it is a
    wrong one* — which is why this returns `()`, never the three that worked."""
    books, why = load_books(as_of=AS_OF, prices={})
    assert books == ()
    assert "RC-58" in why and "402" in why


def test_the_refusal_names_the_instruments_it_lacks():
    """RC-10 — ⚠ a refusal that cannot say what it lacks has absorbed itself."""
    _books, why = load_books(as_of=AS_OF, prices={})
    for instrument in ("MRV|CDR|CAD", "MDA|COMMON|CAD", "BBD.B|COMMON|CAD"):
        assert instrument in why


def test_a_fetch_closure_prices_us_common_without_the_caller_knowing_holdings():
    """★ OR-2 / OR-48 — **D-11 decides WHAT to price; the caller only knows
    HOW.** The caller passes a closure and never learns the holdings."""
    _books, why = load_books(as_of=AS_OF, fetch=lambda s: (100.0, "USD"))
    # ⏸ Still refused — but no longer for DELL, which the closure priced.
    assert "DELL" not in why
    assert "MDA|COMMON|CAD" in why
