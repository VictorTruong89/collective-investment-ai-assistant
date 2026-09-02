#!/usr/bin/env python3
"""
SDD gate — makes "spec before code" enforceable rather than aspirational.

CLAUDE.md and skills *persuade* a model; only a hook *enforces*. This script runs
in three modes, wired to three hook events in .claude/settings.json:

  record   PostToolUse  on Read        — ledger which specs this session has read
  gate     PreToolUse   on Edit|Write  — deny writes to governed code until they are
  brief    SessionStart                — tell a fresh session the specs exist

The ledger is per-session (keyed by session_id), so a NEW conversation or a NEW
agent starts with an empty ledger and must read the specs again. That is the point:
context does not survive across sessions, so neither should the permission.

FAIL-OPEN BY DESIGN: if this script raises, the edit is ALLOWED and a loud warning
is printed. A buggy gate that bricks every edit is worse than a gate that misses
one. Tighten to fail-closed only once you trust it.

Reads stdin JSON: {"session_id": ..., "tool_name": ..., "tool_input": {...}}
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OWNERSHIP = REPO / "sdd" / "specs" / "ownership.yaml"
LEDGER_DIR = Path(os.environ.get("TMPDIR", "/tmp")) / "claude-sdd-ledger"


# --------------------------------------------------------------------------- #
# ownership.yaml
# --------------------------------------------------------------------------- #
def load_ownership() -> dict:
    """Parse ownership.yaml. Uses PyYAML when importable, else a tiny fallback
    parser so the gate keeps working in an interpreter without the dependency."""
    text = OWNERSHIP.read_text(encoding="utf-8")
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except Exception:
        return _mini_parse(text)


def _mini_parse(text: str) -> dict:
    """Handles exactly the shape of ownership.yaml — nothing more."""
    out: dict = {"always": [], "map": [], "exempt": []}
    section, entry, sub = None, None, None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        s = line.strip()
        if indent == 0 and s.endswith(":"):
            section, entry, sub = s[:-1], None, None
            continue
        if section == "map":
            if s.startswith("- globs:"):
                entry = {"globs": [], "spec": "", "why": ""}
                out["map"].append(entry)
                sub = "globs"
            elif entry is not None and s.startswith("spec:"):
                entry["spec"] = s.split(":", 1)[1].strip().strip('"')
                sub = None
            elif entry is not None and s.startswith("why:"):
                entry["why"] = s.split(":", 1)[1].strip().strip('"')
                sub = None
            elif entry is not None and sub == "globs" and s.startswith("- "):
                entry["globs"].append(s[2:].strip().strip('"'))
        elif section in ("always", "exempt") and s.startswith("- "):
            out[section].append(s[2:].strip().strip('"'))
    return out


# --------------------------------------------------------------------------- #
# ledger
# --------------------------------------------------------------------------- #
def ledger_path(session_id: str) -> Path:
    safe = "".join(c for c in (session_id or "unknown") if c.isalnum() or c in "-_")
    return LEDGER_DIR / f"{safe}.json"


def read_ledger(session_id: str) -> set:
    p = ledger_path(session_id)
    if not p.is_file():
        return set()
    try:
        return set(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return set()


def add_to_ledger(session_id: str, spec_rel: str) -> None:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    seen = read_ledger(session_id)
    seen.add(spec_rel)
    ledger_path(session_id).write_text(json.dumps(sorted(seen)), encoding="utf-8")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def rel(path_str: str) -> str | None:
    if not path_str:
        return None
    try:
        return str(Path(path_str).resolve().relative_to(REPO))
    except Exception:
        return None


def matches(rel_path: str, globs) -> bool:
    return any(fnmatch.fnmatch(rel_path, g) for g in (globs or []))


def required_specs(rel_path: str, own: dict):
    """Return (specs_required, why) for a path, or (None, None) if exempt."""
    if matches(rel_path, own.get("exempt")):
        return None, None
    required = list(own.get("always") or [])
    why = ""
    for entry in own.get("map") or []:
        if matches(rel_path, entry.get("globs")):
            if entry.get("spec"):
                required.append(entry["spec"])
            why = entry.get("why", "")
            break
    return required, why


# --------------------------------------------------------------------------- #
# modes
# --------------------------------------------------------------------------- #
def known_specs(own: dict) -> set:
    """Every path ownership.yaml can require: `always` plus each map entry's spec.

    Derived from ownership.yaml rather than hard-coded, so a future move of the
    specs tree carries the recorder with it automatically instead of silently
    leaving the gate unsatisfiable.
    """
    specs = set(own.get("always") or [])
    for entry in own.get("map") or []:
        if entry.get("spec"):
            specs.add(entry["spec"])
    return specs


def mode_record(payload: dict) -> None:
    """PostToolUse on Read — if a spec was read, remember it for this session."""
    r = rel((payload.get("tool_input") or {}).get("file_path", ""))
    if r and r in known_specs(load_ownership()):
        add_to_ledger(payload.get("session_id", ""), r)


def mode_gate(payload: dict) -> None:
    """PreToolUse on Edit|Write — deny until the governing specs are read."""
    r = rel((payload.get("tool_input") or {}).get("file_path", ""))
    if not r:
        return
    own = load_ownership()
    required, why = required_specs(r, own)
    if not required:
        return

    seen = read_ledger(payload.get("session_id", ""))
    missing = [s for s in required if s not in seen]
    if not missing:
        return

    bullets = "\n".join(f"  - {m}" for m in missing)
    reason = (
        f"SDD gate (spec before code): {r} is spec-governed, but "
        f"this session has not read:\n{bullets}\n"
    )
    if why:
        reason += f"\nThat spec covers: {why}\n"
    reason += (
        "\nRead those files with the Read tool, then retry this edit. Reading them "
        "is what stops an implementation from drifting off its acceptance criteria.\n"
        "Grep/Bash(cat) do not count: the gate only credits a full Read."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def mode_brief(payload: dict) -> None:
    """SessionStart — a fresh conversation should know the specs exist."""
    own = load_ownership()
    lines = [
        "This repo is spec-driven (lean SDD); all SDD material lives in sdd/. Before "
        "editing spec-governed code you MUST read the constitution and the governing "
        "spec — a PreToolUse hook enforces this and will deny the edit otherwise.",
        "",
        "  vision       : sdd/specs/vision.md",
        "  constitution : sdd/specs/constitution.md",
        "  spec index   : sdd/specs/README.md",
        "  tier map     : sdd/README.md               (specs / design / blueprints / archive)",
        "",
        "Governed paths:",
    ]
    governed = own.get("map") or []
    if governed:
        for entry in governed:
            lines.append(f"  {', '.join(entry.get('globs', [])):46} -> {entry.get('spec','')}")
    else:
        lines.append("  (none yet — ownership.yaml is still empty)")
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }))


MODES = {"record": mode_record, "gate": mode_gate, "brief": mode_brief}


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in MODES:
        print(f"usage: sdd_gate.py {{{'|'.join(MODES)}}}", file=sys.stderr)
        return 2
    try:
        raw = sys.stdin.read() or "{}"
        MODES[mode](json.loads(raw))
    except Exception as exc:                                   # fail OPEN, loudly
        print(json.dumps({
            "systemMessage": f"SDD gate ({mode}) errored and was skipped: "
                             f"{type(exc).__name__}: {exc}"
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
