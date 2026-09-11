"""`F8` `CT-8.5` / `E1` — the effect vocabulary is CLOSED, and stays closed.

⚠⚠ **An empty vocabulary is not a stub.** `F8` `D6` parked it deliberately:
until effects exist, every directive is unmappable, applies nothing, and is
logged — which is `AC-8.14` working, not a gap. ★ `QR-23` then made E2E a
precondition for resuming trading, so filling it sits on that critical path.

★★ This file guards the shape, never the contents. **Which effects exist and
what their ranges are is the fund manager's judgement** (`D6`), exactly as `D2`
makes golden values his — an agent that chose them would be writing risk policy.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
VOCAB = REPO / "config/effect_vocabulary.yaml"

#: `CT-8.5` — every field an effect must declare.
REQUIRED = ("effect", "target", "operations", "domain", "owning_spec")

#: ⛔ Parameters a directive may NEVER move, and the rule that forbids each.
FORBIDDEN_TARGETS = {
    "CONFIDENCE_FLOOR": "INV-012 / RA-67 — F9 §2: '✗ Changing the confidence rules'",
    "CONFIDENCE_HOLD_CAP": "INV-013 / AC-1.77 — the relay's safety case rests on it",
}


def _doc():
    if not VOCAB.exists():                     # pragma: no cover
        pytest.skip("vocabulary not present")
    return yaml.safe_load(VOCAB.read_text(encoding="utf-8"))


def test_ct_8_5_the_draft_is_not_adopted_until_a_human_says_so():
    """⚠⚠ `D6` — the vocabulary is the fund manager's, and a DRAFT must not
    take effect by existing. ★ Same shape as `D2`'s `established_by`: an agent
    that adopted its own proposal would be writing risk policy."""
    doc = _doc()
    if doc.get("adopted"):
        assert str(doc.get("adopted_by", "")).strip() not in ("", "____"), (
            "an adopted vocabulary must name who adopted it (D6, D2's shape)")
    else:
        assert str(doc.get("adopted_by", "____")) == "____"


def test_ct_8_5_nothing_reads_an_unadopted_vocabulary():
    """★ The draft is inert. ⚠ `AC-8.12` lets the interpreter emit only
    REGISTERED effects, and a draft registers none."""
    from src.orchestration.control.directives import EffectVocabulary, UnregisteredEffect

    doc = _doc()
    live = EffectVocabulary(version=doc["version"],
                            effects=frozenset() if not doc.get("adopted")
                            else frozenset(e["effect"] for e in doc["effects"]))
    if not doc.get("adopted"):
        with pytest.raises(UnregisteredEffect):
            live.check("concentration_report_threshold")


@pytest.mark.parametrize("field", REQUIRED)
def test_ct_8_5_every_effect_declares_every_required_field(field):
    """`CT-8.5` — ⚠ `owning_spec` is *'the spec that authorises this effect to
    exist'*. An effect without one is an effect nobody approved."""
    missing = [e["effect"] for e in _doc()["effects"] if field not in e]
    assert not missing, f"{field!r} missing from: {missing}"


def test_ct_8_5_an_ADOPTED_effect_may_not_have_a_blank_owning_spec():
    """⚠⚠ The draft is allowed blanks; an adopted vocabulary is not.

    ★ `data_staleness_tolerance` has no owning spec today — `STALE_SESSIONS`
    lives in inherited D-03 code no `F<n>` governs. It must gain an owner or be
    dropped before adoption, and this is what stops it slipping through.
    """
    doc = _doc()
    if not doc.get("adopted"):
        pytest.skip("draft — blanks are expected until adoption")
    blank = [e["effect"] for e in doc["effects"]
             if str(e.get("owning_spec", "")).startswith("____")]
    assert not blank, f"adopted effects with no authorising spec: {blank}"


def test_ct_8_5_the_forbidden_parameters_are_not_in_the_vocabulary():
    """⛔⛔ The rules that decide this are not mine and not negotiable.

    ★★ `CONFIDENCE_FLOOR`/`CONFIDENCE_HOLD_CAP` gate what may be **proposed**
    on a tradeable number. `F9` §2 lists changing them as a non-goal and
    `AC-1.77` records that the relay's entire safety case rests on them firing
    unchanged — so a directive reaching them would launder the one guarantee
    the relay path depends on.
    """
    targets = " ".join(str(e.get("target", "")) for e in _doc()["effects"])
    for banned, why in FORBIDDEN_TARGETS.items():
        assert banned not in targets, f"{banned} may never be directive-movable — {why}"


def test_ct_8_5_no_effect_touches_the_verdict_algebra_or_a_promotion_gate():
    """⛔ `PG-6` — the algebra is a **structural** guarantee, not a runtime
    check. ⛔ `PG-10` — a directive loosening `src/quant/gates/` would present an
    unpromoted model as actionable."""
    targets = " ".join(str(e.get("target", "")) for e in _doc()["effects"])
    assert "decision/algebra" not in targets, "PG-6: the verdict algebra is not a knob"
    assert "quant/gates" not in targets, "PG-10: a promotion gate is not a knob"


# ═══════════════════════════════════════════════════════════════════════════
# ★★★ THE NESTING INVARIANT — why the three ranges are safe TOGETHER
# ═══════════════════════════════════════════════════════════════════════════

def _domain(effect: str) -> tuple[float, float]:
    e = next(x for x in _doc()["effects"] if x["effect"] == effect)
    lo, hi = str(e["domain"]).split("-")
    return float(lo), float(hi)


def test_e1_rule_a_no_effect_may_be_loosened_above_its_current_value():
    """✅ Rule ⓐ, adopted 2026-09-10 — **conservative direction only.**

    ★ `P3`'s shape applied to the control surface: a directive may make the
    system report earlier, never later. ⚠ The accepted cost is that *"markets
    are calm, let some noise through"* is unexpressible and needs a spec change.
    """
    for e in _doc()["effects"]:
        lo, hi = _domain(e["effect"])
        assert hi <= e["current"], (
            f"{e['effect']} may be set to {hi} > its current {e['current']} — "
            "that LOOSENS a risk report, which rule ⓐ forbids")
        assert lo < hi, f"{e['effect']} has an empty range"


def test_e1_name_sector_theme_nest_for_EVERY_reachable_setting():
    """⚠⚠ A name sits inside a sector sits inside a theme.

    ★★★ If the sector threshold could be set below the name threshold, the
    system could warn about a sector while staying silent about a single
    position larger than the whole sector limit — an incoherent state no reader
    could interpret.

    ★ Each floor is the NEXT-NARROWER dimension's current value, so the ranges
    meet end-to-end and never overlap: the invariant holds **by construction**,
    not by a runtime check. This asserts the construction, exhaustively.
    """
    name, sector, theme = (_domain("concentration_report_threshold"),
                           _domain("sector_report_threshold"),
                           _domain("theme_report_threshold"))
    # the worst case is each dimension at its own extreme
    assert name[1] <= sector[0], (
        f"name may reach {name[1]} while sector may sit at {sector[0]} — "
        "a single position could exceed its own sector's limit")
    assert sector[1] <= theme[0], (
        f"sector may reach {sector[1]} while theme may sit at {theme[0]}")


def test_e1_the_name_floor_is_the_cap_on_what_the_system_PROPOSES():
    """★★★ The one floor that is structurally forced rather than chosen.

    `MAX_POSITION_PCT = 15.0` (`portfolio/contracts/sizing.py`, `INV-022`) caps
    what the sizer will ever propose. ⚠ A concentration alert set below it
    would fire on a position the system itself called normal — and `RP-46`/
    `RP-47` forbid suppressing alerts, so that noise would be permanent.
    """
    from src.portfolio.contracts.sizing import MAX_POSITION_PCT
    assert _domain("concentration_report_threshold")[0] == MAX_POSITION_PCT
