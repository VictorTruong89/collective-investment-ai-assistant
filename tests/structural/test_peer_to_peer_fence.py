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


# ═══════════════════════════════════════════════════════════════════════════
# `F6b` AC-6b.3 · AC-6b.5 — the two structural fences deliberation needs.
# ═══════════════════════════════════════════════════════════════════════════
from tools.check_import_fences import (  # noqa: E402
    agent_cross_import_violations,
    prose_branch_violations,
)


def test_ac_6b_3_no_control_flow_branches_on_prose():
    """The live tree. ⚠ No skip, no tolerance list."""
    assert prose_branch_violations() == []


def test_ac_6b_3_a_branch_on_a_note_is_caught(tmp_path):
    """⚠⚠ `CT-6b.1` marks `note` *human-readable ONLY; never branched on*.

    ★★ `F6b` §4 says why: *"If the payload is prose, only another model can
    consume it and the branch becomes undecidable."* ★ The deeper reason is
    `PG-9` — a branch on free text has no answer to *"why did this happen?"*
    better than *"the wording tripped it"*, so changing a prompt would silently
    change decisions with nothing in the trace to show it.
    """
    src = tmp_path / "src" / "orchestration" / "graph"
    src.mkdir(parents=True)
    (src / "d.py").write_text(
        "def go(msg):\n"
        "    if 'concentration' in msg.note:\n"
        "        return 'REVISE'\n"
        "    return 'HOLD'\n")
    hits = prose_branch_violations(tmp_path / "src")
    assert len(hits) == 1 and "AC-6b.3" in hits[0]


def test_ac_6b_3_RECORDING_or_RENDERING_prose_is_allowed(tmp_path):
    """★★ The distinction the fence rests on: **reading is fine, branching is
    not.** ⚠ A check that banned the field outright would forbid putting the
    challenge into the transcript, which is the whole point of carrying it."""
    src = tmp_path / "src" / "orchestration" / "graph"
    src.mkdir(parents=True)
    (src / "d.py").write_text(
        "def record(msg, store):\n"
        "    store.append({'note': msg.note, 'text': msg.text})\n"
        "    return f'{msg.note}'\n")
    assert prose_branch_violations(tmp_path / "src") == []


def test_ac_6b_3_a_branch_on_a_CHECKABLE_field_is_allowed(tmp_path):
    """★ `AC-6b.2` — a challenge names the field it disputes and the value it
    expected, and branching on THAT is exactly what makes the exchange
    decidable without a model."""
    src = tmp_path / "src" / "orchestration" / "graph"
    src.mkdir(parents=True)
    (src / "d.py").write_text(
        "def go(msg):\n"
        "    if msg.metric_value > msg.threshold:\n"
        "        return 'CHALLENGE'\n"
        "    return None\n")
    assert prose_branch_violations(tmp_path / "src") == []


def test_ac_6b_5_no_agent_imports_another():
    assert agent_cross_import_violations() == []


def test_ac_6b_5_an_agent_importing_a_peer_is_caught(tmp_path):
    """⚠ `F6b` §4 — *agents exchange through D-08 and never import each
    other*. ★ A direct import is a path along which one seat's in-progress work
    reaches another **with no message recorded**."""
    src = tmp_path / "src" / "shared" / "agents"
    src.mkdir(parents=True)
    (src / "risk_agent.py").write_text(
        "from src.shared.agents.research_agent import view\n")
    (src / "research_agent.py").write_text("view = 1\n")
    hits = agent_cross_import_violations(tmp_path / "src")
    assert len(hits) == 1 and "AC-6b.5" in hits[0]


# ═══════════════════════════════════════════════════════════════════════════
# `F3` AC-3.10 / `ST-5` — only the LLM gateway calls an LLM. ⚠ The 6th
# structural AC found unenforced (`DX-53`'s pattern, one spec further back).
# ═══════════════════════════════════════════════════════════════════════════
from tools.check_import_fences import sdk_fence_violations  # noqa: E402


def test_ac_3_10_no_domain_imports_an_llm_sdk_directly():
    """The live tree. ⚠ No skip, no tolerance list."""
    assert sdk_fence_violations() == []


def test_ac_3_10_a_direct_sdk_import_is_caught(tmp_path):
    """⚠⚠ `ST-5` is what makes three separate guarantees UNAVOIDABLE.

    ★★★ `GW-20`'s budget cap, `F2` `CT-2.2`'s request/response recording and
    `AC-2.9`'s redaction all live at the gateway — so a single direct SDK call
    bypasses **all three at once**, and nothing downstream would show a gap:
    the trace simply would not contain the call.
    """
    src = tmp_path / "src" / "data_engine" / "corporate_actions"
    src.mkdir(parents=True)
    (src / "classify.py").write_text("import anthropic\n")
    hits = sdk_fence_violations(tmp_path / "src")
    assert len(hits) == 1 and "ST-5" in hits[0]


def test_ac_3_10_the_gateway_itself_may_import_it(tmp_path):
    """★ Otherwise the gateway could not exist. ⚠ The rule is *only* the
    gateway, not *nobody*."""
    gw = tmp_path / "src" / "shared" / "llm"
    gw.mkdir(parents=True)
    (gw / "gateway.py").write_text("import anthropic\n")
    assert sdk_fence_violations(tmp_path / "src") == []


def test_ac_3_10_a_submodule_import_is_caught_too(tmp_path):
    """⚠ `from anthropic.types import Message` is the same breach."""
    src = tmp_path / "src" / "fundamental"
    src.mkdir(parents=True)
    (src / "x.py").write_text("from anthropic.types import Message\n")
    assert sdk_fence_violations(tmp_path / "src")


def test_ac_3_10_a_name_that_merely_CONTAINS_a_vendor_is_not_caught(tmp_path):
    """★ `tools/anthropic_transport.py` is OUR module and its name contains a
    vendor's. ⚠ A substring check would flag every wrapper written to keep the
    SDK confined — punishing the fix."""
    src = tmp_path / "src" / "fundamental"
    src.mkdir(parents=True)
    (src / "x.py").write_text("from src.shared.llm.anthropic_gateway import send\n")
    assert sdk_fence_violations(tmp_path / "src") == []
