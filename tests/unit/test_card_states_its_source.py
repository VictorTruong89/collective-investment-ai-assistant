"""`F9` `AC-9.6` — ★ the discipline card states which source produced its thesis.

⚠⚠ **The vocabulary existed and nothing used it.** `RELAYED_JUDGEMENT` — a
fourth reliability class with its own glyph `◌⇄` and the label *"RELAYED
JUDGEMENT (unverified transport)"* — has been in `render/classes.py` since
2026-08-25, added because `AC-1.79` requires the class **in every medium**.
`build_card()` never assigned it (`DX-43`).

★★ `RP-48` is emphatic about why it is not a footnote on `JUDGEMENT`: a relay
report is *"a judgement whose bundle does not exist and whose numbers are mostly
unverifiable against data we hold."* ⚠ Rendering it as an ordinary judgement
tells the reader the two are equally checkable, which is the specific thing
`AP-2` and `DC-1` exist to prevent.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from src.decision import compose
from src.fundamental import GateVerdict, Grade
from src.quant import Candidate, Nomination
from src.reporting.render.card import build_card
from src.reporting.render.classes import JUDGEMENT, LABEL, RELAYED_JUDGEMENT
from src.risk import AlertSet, unchecked

AS_OF = date(2026, 9, 9)
_SENTINEL = object()


def _rec(variant="api", *, thesis_ref=_SENTINEL):
    """A REAL `CT-12.1` through `compose()` — the card re-derives nothing
    (`RP-43`), so a stand-in would test the stand-in."""
    if thesis_ref is _SENTINEL:
        thesis_ref = {"falsifier": "gross margin below 20%",
                      "provenance": {"port": "thesis_source", "variant": variant}}
    nom = Nomination(as_of=AS_OF, run_id="r", decision_anchor="open",
                     horizon_set=("production", 1), nominating_horizon="h1m",
                     universe_n=1, model_artifact_id="sha256:abc",
                     candidates=(Candidate("NVDA", 1, 0.1115, 0.425),))
    # ★ A gate carrying a graded verdict, so `analyst_verdict` renders — that
    #   is the unit whose reliability CLASS `AC-9.6` changes.
    gate = GateVerdict("thesis", "NVDA", AS_OF, "PASS", "graded for test",
                       Grade(verdict="BUY"))
    rec = compose(
        nomination=nom, gate_verdicts=[gate],
        alert_set=AlertSet((), unchecked("no book (RK-29)")),
        run_id="r", as_of=AS_OF, gate_roster_declared=("thesis",),
        manifest_anchor="open", actionable=False, not_actionable_reason="test",
        stubs=({"domain": "D-01", "job": "thesis", "behaviour": "constant PASS",
                "replaced_at": "B4.4", "rule": "L3 BS-11"},),
    )
    return replace(rec, thesis_ref=thesis_ref)


def test_ac_9_6_a_relayed_thesis_is_named_on_the_card():
    """⚠ `AC-9.6` — *"when its thesis came from the relay, the card says so."*"""
    card = build_card(_rec("relay"), as_of=AS_OF)
    unit = card.field("thesis_source")
    assert unit.value == "relay"
    assert card.to_json_obj()["fields"]["thesis_source"]["value"] == "relay"


def test_ac_9_6_an_api_thesis_is_named_too():
    """★ The field is present on BOTH paths.

    ⚠ A provenance field that appears only on the relay path teaches readers
    that its absence means "fine" — and then a missing provenance and an API
    thesis look identical. `AP-2`: transparency over confidence.
    """
    assert build_card(_rec("api"), as_of=AS_OF).field("thesis_source").value == "api"


def test_ac_9_6_a_relayed_analyst_verdict_renders_as_RELAYED_JUDGEMENT():
    """★★ `RP-48` / `AC-1.79` — the CLASS changes, not just a label somewhere.

    ⚠ `RELAYED_JUDGEMENT` is **more provisional than `JUDGEMENT`**, never a
    footnote on it: the bundle does not exist and the numbers are mostly
    unverifiable against data we hold.
    """
    card = build_card(_rec("relay"), as_of=AS_OF)
    assert card.field("analyst_verdict").reliability == RELAYED_JUDGEMENT
    assert card.field("thesis_source").reliability == RELAYED_JUDGEMENT


def test_ac_9_6_an_api_analyst_verdict_stays_an_ordinary_JUDGEMENT():
    """⚠ The class must not be applied indiscriminately — if everything is
    relayed, the distinction carries no information."""
    card = build_card(_rec("api"), as_of=AS_OF)
    assert card.field("analyst_verdict").reliability == JUDGEMENT


def test_ac_9_6_the_label_says_unverified_transport_in_words():
    """★★ `RP-1` residual (`QP-1`): class is **never signalled by colour
    alone** — and a machine-readable enum is this medium's 'colour'. The words
    are what a reader takes away."""
    card = build_card(_rec("relay"), as_of=AS_OF)
    label = LABEL[card.field("thesis_source").reliability]
    assert "RELAYED" in label and "unverified transport" in label


def test_ac_9_6_a_thesis_with_no_provenance_is_LOUD_not_assumed_api():
    """⚠⚠ `P5` — fail loud, never silent.

    ★ The tempting default is `api`, because it is the common case (`QR-20`).
    That would render an unprovenanced thesis as the **most** trustworthy
    source available, which is the wrong direction for a defaulting rule.
    """
    card = build_card(_rec(variant=None), as_of=AS_OF)
    unit = card.field("thesis_source")
    assert unit.value == "unknown"
    assert unit.reliability == RELAYED_JUDGEMENT, (
        "an unprovenanced thesis must render at the WEAKEST class, never the "
        "strongest (P5, AP-2)")


def test_ac_9_6_a_card_with_no_thesis_at_all_omits_the_field():
    """★ A walking-skeleton card states no thesis; a `thesis_source` on it
    would name a source for something that does not exist."""
    card = build_card(_rec(thesis_ref=None), as_of=AS_OF)
    assert "thesis_source" not in card.field_names
    with pytest.raises(KeyError):
        card.field("thesis_source")
