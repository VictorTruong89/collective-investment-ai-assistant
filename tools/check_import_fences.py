#!/usr/bin/env python3
"""F4 `AC-4.2` / `AC-4.7` — the analyst firewall, at seat 6.

★★ **`INV-014` / `ST-9`: D-01 and D-03 must not see each other's in-progress
work.** The firewall's whole value is that when the fundamental and quant views
*agree*, the agreement is informative — two independent reads reaching the same
place. ⚠ If seat 6 reached into either domain's internals it would become a path
between them, and concurrence would quietly become an echo (`PG-7` says the same
thing about cross-configuration).

So `src/explain/**` may import **published contract types only** — a domain's
`contracts`/`models` surface — and never its analysis internals.

`AC-4.7`: it also may not contain gate-binding logic. `decision/attribute/binding.py`
already answers *"which gates bound, and why"*; a second implementation would be a
second answer (`P4`).

⚠ **AST, not grep** — a docstring naming a module is not an import.
"""

from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
EXPLAIN = "src/explain"

#: Domains whose INTERNALS seat 6 may not reach into (`INV-014`, `ST-9`).
WALLED_DOMAINS = ("src.fundamental", "src.quant")

#: The only sub-modules of a walled domain that are published surface.
PUBLISHED_SUFFIXES = (".contracts", ".models", ".contracts.", ".models.")

#: `AC-4.7` — gate binding is consumed, never re-implemented here.
GATE_BINDING_MARKERS = ("def bind_gates", "def gate_binding", "def which_gates_bound",
                        "def _bind(", "def compute_binding")


def _imports(source: str, filename: str) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(ast.parse(source, filename=filename)):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            out.add(node.module)
    return out


def _py(root: pathlib.Path):
    for p in sorted(root.rglob("*.py")):
        if "__pycache__" not in p.parts:
            yield p


def _is_published(mod: str) -> bool:
    return any(s in mod for s in PUBLISHED_SUFFIXES) or mod in WALLED_DOMAINS


def firewall_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-4.2` — seat 6 reaching into a walled domain's internals."""
    src_root = src_root or REPO / "src"
    explain_dir = src_root / "explain"
    if not explain_dir.is_dir():
        return []
    out = []
    for path in _py(explain_dir):
        rel = path.relative_to(src_root.parent).as_posix()
        for mod in _imports(path.read_text(encoding="utf-8"), rel):
            if mod.startswith(WALLED_DOMAINS) and not _is_published(mod):
                out.append(
                    f"{rel} imports {mod} — ⚠ INV-014/ST-9: seat 6 may read a "
                    "domain's PUBLISHED contracts, never its analysis internals. "
                    "Reaching inside makes D-13 a path between the two analysts, "
                    "and their agreement stops being independent.")
    return out


def peer_to_peer_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`F6a` `AC-6a.6` — ★★ the two analysts may not import EACH OTHER.

    ⚠⚠ **This is a different fence from `firewall_violations` above**, and the
    difference is why `AC-6a.6` went unenforced: that one walks `src/explain/`
    and asks whether **seat 6** reached into a walled domain (`AC-4.2`). This
    one asks whether the walled domains reached into **one another**.

    `F6a` §4: *"Mediated, never peer-to-peer. The fundamental agent never calls
    the quant agent. Both import only the orchestrator's types. ⚠ A direct call
    would breach `ST-9` structurally and turn n agents into n² dependencies."*

    ★ The subtle harm is not coupling, it is **silence**: a direct import is a
    channel through which one seat can condition the other with **no
    `influenced_by` recorded anywhere**. `PG-7` is defeated without leaving a
    trace, which is strictly worse than being defeated loudly.

    ⚠ Unlike the seat-6 fence, `_is_published` does NOT apply. Seat 6 is a
    *reader* of both domains and may read their published contracts; the two
    analysts are supposed to be independent of each other, so even a contract
    import is a dependency `INV-014` does not want. Mediation goes through the
    orchestrator's types, which this deliberately still allows.
    """
    src_root = src_root or REPO / "src"
    out = []
    for domain in WALLED_DOMAINS:                      # "src.fundamental", "src.quant"
        peers = tuple(d for d in WALLED_DOMAINS if d != domain)
        domain_dir = src_root / domain.split(".", 1)[1]
        if not domain_dir.is_dir():
            continue
        for path in _py(domain_dir):
            rel = path.relative_to(src_root.parent).as_posix()
            for mod in _imports(path.read_text(encoding="utf-8"), rel):
                if mod.startswith(peers):
                    out.append(
                        f"{rel} imports {mod} — ⚠ AC-6a.6 / ST-9 / INV-014: the "
                        "two analysts are MEDIATED, never peer-to-peer. A direct "
                        "import lets one seat condition the other with no "
                        "influenced_by recorded, defeating PG-7 silently. Route "
                        "it through the orchestrator's types instead.")
    return out


def gate_binding_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-4.7` — gate binding rebuilt here instead of consumed."""
    src_root = src_root or REPO / "src"
    explain_dir = src_root / "explain"
    if not explain_dir.is_dir():
        return []
    out = []
    for path in _py(explain_dir):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(src_root.parent).as_posix()
        for marker in GATE_BINDING_MARKERS:
            if marker in text:
                out.append(f"{rel} defines {marker!r} — read "
                           "decision/attribute/binding.py instead (AC-4.7, P4)")
    return out


#: `F6b` `AC-6b.3` — the fields that are HUMAN-READABLE ONLY. `CT-6b.1`:
#: *"note: str — ⚠ human-readable ONLY; never branched on"*.
PROSE_FIELDS = ("note", "text")

#: Where deliberation control flow lives.
DELIBERATION_ROOTS = ("orchestration/graph", "shared/agents")


def prose_branch_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-6b.3` — ⚠⚠ control flow may NEVER branch on prose.

    `CT-6b.1` marks `payload.note` *"human-readable ONLY; never branched on"*,
    and `F6b` §4 says why: *"If the payload is prose, only another model can
    consume it and the branch becomes **undecidable**."*

    ★★ The deeper reason is `PG-9`. A branch on free text has no answer to
    *"why did this happen?"* better than *"the wording tripped it"* — and a
    deliberation whose control flow depends on phrasing is one where changing a
    prompt silently changes decisions, with nothing in the trace to show it.

    ⚠ Reading prose to RECORD or RENDER it is fine; only a branch is refused.
    """
    import ast

    src_root = src_root or REPO / "src"
    out = []
    for rel_root in DELIBERATION_ROOTS:
        root = src_root / rel_root
        if not root.is_dir():
            continue
        for path in _py(root):
            rel = path.relative_to(src_root.parent).as_posix()
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
            except SyntaxError:                            # pragma: no cover
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.If, ast.While, ast.IfExp)):
                    continue
                for sub in ast.walk(node.test):
                    if (isinstance(sub, ast.Attribute)
                            and sub.attr in PROSE_FIELDS):
                        out.append(
                            f"{rel}:{node.lineno}: control flow branches on "
                            f".{sub.attr} — ⚠ AC-6b.3 / CT-6b.1: that field is "
                            "HUMAN-READABLE ONLY. A branch on prose is "
                            "undecidable to anything but another model, and "
                            "PG-9 has no answer for it better than 'the "
                            "wording tripped it'.")
    return out


def agent_cross_import_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-6b.5` — no agent module imports another; all exchange is via D-08.

    ★ Same rule `F6a` follows, one layer up: `F6b` §4 — *"Mediated by the
    orchestrator. Agents exchange messages **through** D-08 and never import
    each other."* ⚠ A direct import turns n agents into n² dependencies and,
    worse, creates a path along which one seat's in-progress work reaches
    another without any message being recorded.
    """
    src_root = src_root or REPO / "src"
    agents = src_root / "shared/agents"
    if not agents.is_dir():
        return []
    out = []
    for path in _py(agents):
        rel = path.relative_to(src_root.parent).as_posix()
        own = path.stem
        for mod in _imports(path.read_text(encoding="utf-8"), rel):
            if mod.startswith("src.shared.agents") and not mod.endswith(own):
                out.append(
                    f"{rel} imports {mod} — ⚠ AC-6b.5: agents exchange through "
                    "D-08 and never import each other.")
    return out


#: `ST-5` — **only the LLM gateway calls an LLM.** ⚠ Vendor SDKs, by import name.
LLM_SDKS = ("anthropic", "openai", "google.generativeai", "cohere",
            "mistralai", "litellm", "langchain")

#: ★ The one place permitted to import them.
GATEWAY_PREFIX = "src/shared/llm"


def sdk_fence_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`F3` `AC-3.10` / `ST-5` — ⚠ no domain reaches a model directly.

    ★★ `ST-5` is one of the inherited rules the constitution restates by ID:
    *only the LLM gateway calls an LLM*. It is what makes `GW-20`'s budget cap,
    `F2`'s `CT-2.2` recording and `AC-2.9`'s redaction **unavoidable** rather
    than merely available — every one of them lives at the gateway, so a direct
    SDK call bypasses all three at once.

    ⚠ `AC-3.10` names `src/data_engine/corporate_actions/**`, and the same rule
    binds every domain, so the fence is checked over all of `src/` with the
    gateway exempted (`DX-54`).
    """
    src_root = src_root or REPO / "src"
    out = []
    for path in _py(src_root):
        rel = path.relative_to(src_root.parent).as_posix()
        if rel.startswith(GATEWAY_PREFIX):
            continue
        for mod in _imports(path.read_text(encoding="utf-8"), rel):
            if any(mod == s or mod.startswith(f"{s}.") for s in LLM_SDKS):
                out.append(
                    f"{rel} imports {mod} — ⚠ ST-5 / AC-3.10: only "
                    "src/shared/llm/ calls an LLM. A direct SDK call bypasses "
                    "the budget cap (GW-20), the CT-2.2 recording and AC-2.9's "
                    "redaction in one step, because all three live at the "
                    "gateway.")
    return out


def all_violations(src_root: pathlib.Path | None = None) -> list[str]:
    # ⚠ `peer_to_peer_violations` was added 2026-09-09 (`AC-6a.6`). It had a
    # tool-shaped home here and was never wired in, so the fence `F6a` §4 calls
    # *structural* was enforced by nothing — see `DX-41`.
    return (firewall_violations(src_root)
            + gate_binding_violations(src_root)
            + peer_to_peer_violations(src_root)
            + prose_branch_violations(src_root)
            + agent_cross_import_violations(src_root)
            + sdk_fence_violations(src_root))


def main() -> int:
    bad = all_violations()
    if bad:
        print("⛔ import-fence violations:", file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    print("✅ AC-4.2 / AC-4.7 — the analyst firewall holds at seat 6")
    print("✅ AC-6a.6 — the two analysts are mediated, never peer-to-peer")
    print("✅ AC-6b.3 / AC-6b.5 — no branch on prose; no agent imports another")
    print("✅ AC-3.10 / ST-5 — only src/shared/llm/ imports an LLM SDK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

