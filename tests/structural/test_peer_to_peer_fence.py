"""`F6a` `AC-6a.6` — ★★ the two analysts may not import each other.

⚠⚠ **This was the one `F6a` AC with no enforcement at all.**
`tools/check_import_fences.py::firewall_violations` walks `src/explain/` only —
that is `AC-4.2`, seat 6 reaching into a walled domain. Nothing checked the
fence `AC-6a.6` actually names: `src/fundamental/**` and `src/quant/**` not
importing **each other**.

★ Why it matters structurally, not stylistically (`F6a` §4):

> *"Mediated, never peer-to-peer. The fundamental agent never calls the quant
> agent. Both import only the orchestrator's types. ⚠ A direct call would breach
> `ST-9` structurally and turn *n* agents into *n²* dependencies."*

⚠ And `INV-014`: the firewall's value is that concurrence between the two views
is *informative*. A direct import is a channel through which one can condition
the other **without any `influenced_by` being recorded** — so it defeats `PG-7`
silently, which is worse than defeating it loudly.
"""

from __future__ import annotations

import pathlib

from tools.check_import_fences import peer_to_peer_violations

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_ac_6a_6_the_two_analysts_do_not_import_each_other():
    """The live tree. ⚠ No skip, no tolerance list."""
    assert peer_to_peer_violations() == []


def test_ac_6a_6_a_fundamental_import_of_quant_is_caught(tmp_path):
    """⚠ The check must be able to FAIL, or it is decoration."""
    src = tmp_path / "src"
    (src / "fundamental").mkdir(parents=True)
    (src / "quant").mkdir(parents=True)
    (src / "fundamental" / "thesis.py").write_text(
        "from src.quant.rank.service import rank\n")
    (src / "quant" / "ok.py").write_text("import json\n")
    hits = peer_to_peer_violations(src)
    assert len(hits) == 1 and "src.quant.rank" in hits[0]


def test_ac_6a_6_a_quant_import_of_fundamental_is_caught(tmp_path):
    """★ Symmetric — the fence has no favoured direction. ⚠ `D1`'s phase order
    (`quant → fundamental`) says which may INFLUENCE which through the
    orchestrator; it never licenses an import either way."""
    src = tmp_path / "src"
    (src / "fundamental").mkdir(parents=True)
    (src / "quant").mkdir(parents=True)
    (src / "quant" / "rank.py").write_text(
        "from src.fundamental.thesis.models import Thesis\n")
    hits = peer_to_peer_violations(src)
    assert len(hits) == 1 and "src.fundamental.thesis" in hits[0]


def test_ac_6a_6_importing_the_orchestrators_types_is_ALLOWED(tmp_path):
    """★★ The rule is *mediated, never peer-to-peer* — not *isolated*.

    ⚠ A fence that also banned the mediator would make `F6a` unimplementable:
    routing exists precisely so both seats can depend on one shared vocabulary
    instead of on each other.
    """
    src = tmp_path / "src"
    (src / "fundamental").mkdir(parents=True)
    (src / "quant").mkdir(parents=True)
    (src / "fundamental" / "a.py").write_text(
        "from src.orchestration.policy.routing import Routing\n"
        "from src.shared.money import Money\n")
    assert peer_to_peer_violations(src) == []


def test_ac_6a_6_a_self_import_within_one_domain_is_ALLOWED(tmp_path):
    """⚠ The fence is BETWEEN the analysts, not inside either."""
    src = tmp_path / "src"
    (src / "fundamental" / "sub").mkdir(parents=True)
    (src / "quant").mkdir(parents=True)
    (src / "fundamental" / "a.py").write_text(
        "from src.fundamental.sub.b import thing\n")
    assert peer_to_peer_violations(src) == []
