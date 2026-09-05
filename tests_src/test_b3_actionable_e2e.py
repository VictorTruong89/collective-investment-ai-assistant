"""B3 end-to-end — the card goes actionable when both DN-39 inputs exist.

★ These tests are the **proof that the wiring is complete**. The live pipeline
still emits an informational card, and the reason is data, not code: every one of
Victor's four accounts holds at least one CAD-venue or CDR position, and those
symbols are plan-gated on the current FMP subscription (measured 2026-08-26:
`/stable/quote-short?symbol=MDA.TO` -> **402**, DE-49). An unpriceable sleeve
means no book-wide exposure, so **RK-30** keeps the pass `UNCHECKED` and DN-39
keeps the card informational. Supply prices and the same code path turns
actionable with no further change — which is what these tests pin.
"""
from datetime import date

import pytest

from src.decision.compose.service import assert_actionable_inputs
from src.decision.errors import DecisionError
from src.recording.book.models import BookState, Position
from src.risk.alerts.daily import daily_book_pass
from src.risk.contracts.theme import Theme, ThemeTaxonomy

AS_OF = date(2026, 8, 25)
STABLE = {"k": 3, "modal": "BUY", "agreement": 1.0}


def _priced_book():
    """A fully priced, reconciled account — ★ what RC-58 currently prevents."""
    pos = (
        Position(instrument_id="NVDA|COMMON|USD", analysis_symbol="NVDA",
                 quantity=44.0, market_value=9374.20, currency="USD",
                 account_id="TFSA_2", sector="Information Technology"),
        Position(instrument_id="ARM|COMMON|USD", analysis_symbol="ARM",
                 quantity=35.0, market_value=4900.00, currency="USD",
                 account_id="TFSA_2", sector="Information Technology"),
    )
    return BookState(
        account_id="TFSA_2", date=AS_OF, positions=pos,
        cash_by_currency={"USD": 151.22}, nav_by_currency={"USD": 14425.42},
        base_currency="USD", nav_base=14425.42, capital_base=14425.42,
    )


def _taxonomy():
    return ThemeTaxonomy(
        taxonomy_version="test-v1",
        membership_rule="declared GICS sector, one theme per sector (RK-6)",
        themes=(Theme(theme_id="semis", sectors=("Information Technology",),
                      included=("NVDA", "ARM")),),
    )


def test_priced_reconciled_book_yields_a_complete_pass():
    """AC-12.29 — ★ the precondition DN-39 turns on. A pass over a book with no
    unpriceable sleeve is COMPLETE, so its silence is a real all-clear (RK-30)."""
    _report, alerts = daily_book_pass(
        as_of=AS_OF, books=[_priced_book()], taxonomy=_taxonomy(),
        history=[_priced_book()], base_currency="USD")
    assert str(alerts.status).startswith("COMPLETE"), alerts.status


def test_complete_pass_plus_stability_makes_the_card_actionable():
    """AC-12.29 (DN-39) — ★ **the positive path, end to end.** Both inputs
    present, so D-12 permits the single actionable recommendation (INV-6)."""
    _report, alerts = daily_book_pass(
        as_of=AS_OF, books=[_priced_book()], taxonomy=_taxonomy(),
        history=[_priced_book()], base_currency="USD")
    assert_actionable_inputs(alerts, STABLE)      # does not raise


def test_same_book_unreconciled_never_reaches_actionable():
    """AC-12.29 / RK-29 — ⚠ the fallback that produces a correct-looking report
    about YESTERDAY is refused at step 0, and the card cannot go actionable."""
    from src.risk.errors import NoBookError

    import dataclasses

    from src.recording.book.models import Break

    bad = dataclasses.replace(
        _priced_book(), reconciled="break",
        breaks=(Break(account_id="TFSA_2", currency="USD",
                      computed=151.22, reported=140.00),))
    with pytest.raises(NoBookError):
        daily_book_pass(as_of=AS_OF, books=[bad], taxonomy=_taxonomy(),
                        history=[bad], base_currency="USD")


def test_unpriceable_sleeve_is_todays_actual_blocker():
    """AC-12.29 — ★ pins the *reason* the live card is informational, so that
    when RC-58 is lifted this test is the one that has to change."""
    with pytest.raises(DecisionError, match="never ran"):
        assert_actionable_inputs(
            type("A", (), {"status": "UNCHECKED: CAD sleeve unpriceable (RC-58)"})(),
            STABLE)
