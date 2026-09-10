"""
F3 — the SDD process itself is checkable.

A process spec that nothing enforces is a wish. These tests assert the mechanical parts of
`sdd/specs/F3_sdd_adoption/spec.md`: that specs have the required shape, that the
ownership map actually wires them to code, that traceability tables cite real files, that
the PreToolUse gate is live, and that research stays exempt (P7).

What these tests deliberately do NOT check: whether a spec is *good*. No test can tell you
that a spec describes the right behaviour — that is what F3 §4c (verify against external
truth) is for, and it is a human judgement.

Deterministic: filesystem and YAML reads only. No network, no imports of pipeline code.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

SDD = Path("sdd")
SPECS = SDD / "specs"
OWNERSHIP = SPECS / "ownership.yaml"
TEMPLATE = SPECS / "_templates" / "spec.md"
VISION = SPECS / "vision.md"

# F0 is descriptive: it maps the system and governs no code path. F3 is a process spec:
# it governs procedure, not files. Both legitimately have no ownership globs.
DESCRIPTIVE_SPECS = {"F0_code_map", "F3_sdd_adoption"}


def _spec_files() -> list[Path]:
    return sorted(p for p in SPECS.glob("*/spec.md") if p.parent.name != "_templates")


@pytest.fixture(scope="module")
def ownership() -> dict:
    return yaml.safe_load(OWNERSHIP.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# AC-3.1 — spec structure (CT-3.4)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("spec", _spec_files(), ids=lambda p: p.parent.name)
def test_every_spec_has_the_required_shape(spec: Path):
    """Numbered sections, at least one AC, and a traceability table (constitution §6)."""
    text = spec.read_text(encoding="utf-8")

    assert re.search(r"^## \d+", text, re.M), f"{spec} has no numbered sections"
    # ⚠ DX-10 — `[a-z]?` matters: this repo splits F6/F7 into `F6a`/`F6b`/
    # `F7a`/`F7b`, so its ACs read `AC-6a.1`. Upstream's regex predates that split
    # and silently reported four real specs as declaring NO acceptance criteria.
    # ⚠⚠ `F?` — DX-44, 2026-09-09. F9's ACs are `AC-F9.1` because a bare
    # `AC-9.6` had TWO live meanings: F9's (*the card states its source*) and
    # D-09's (*every card field names a producing domain*), both about the
    # discipline card. ★ This assertion fired the moment the rename landed —
    # which is the same guard doing its job LOUDLY that `DX-10` recorded it
    # doing SILENTLY the first time.
    assert re.search(r"\*\*AC-F?\d+[a-z]?\.\d+\*\*", text), \
        f"{spec} declares no acceptance criteria — it cannot be 'done' (constitution §4)"
    assert "Traceability" in text, f"{spec} has no traceability table"


@pytest.mark.parametrize("spec", _spec_files(), ids=lambda p: p.parent.name)
def test_every_spec_declares_a_status(spec: Path):
    """🔵 idea → 🟡 draft → 🟢 approved. A spec with no status invites coding against an idea."""
    head = spec.read_text(encoding="utf-8")[:1200]
    assert "Status:" in head, f"{spec} does not declare a status"


# --------------------------------------------------------------------------- #
# AC-3.2 — ownership is wired (CT-3.3)
# --------------------------------------------------------------------------- #
def test_ownership_map_resolves(ownership):
    """Every spec the gate points at must exist, or the gate silently under-protects."""
    missing = [e["spec"] for e in ownership.get("map", [])
               if not Path(e["spec"]).is_file()]
    assert not missing, f"ownership.yaml points at specs that do not exist: {missing}"


def test_ownership_always_list_resolves(ownership):
    always = ownership.get("always", [])
    assert always, "ownership.yaml has no `always` list — nothing would ever be required"
    missing = [p for p in always if not Path(p).is_file()]
    assert not missing, f"`always` names missing files: {missing}"


def test_code_governing_specs_have_globs(ownership):
    """A spec with no globs is UNENFORCED: the gate falls back to `always` (constitution
    only), which is weaker than the author almost certainly intended. F3 CT-3.3."""
    mapped = {e["spec"] for e in ownership.get("map", [])}
    for spec in _spec_files():
        if spec.parent.name in DESCRIPTIVE_SPECS:
            continue
        assert str(spec) in mapped, (
            f"{spec} governs code but has no globs in ownership.yaml — add them in the "
            f"same change, or declare the spec descriptive")


def test_every_mapped_entry_has_globs_and_a_reason(ownership):
    for e in ownership.get("map", []):
        assert e.get("globs"), f"ownership entry for {e.get('spec')} has no globs"
        assert e.get("why"), f"ownership entry for {e.get('spec')} has no `why`"


# --------------------------------------------------------------------------- #
# AC-3.3 — traceability cites real files (constitution §6)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("spec", _spec_files(), ids=lambda p: p.parent.name)
def test_traceability_tables_cite_real_test_files(spec: Path):
    """A row claiming ✅ green must cite a test that exists — otherwise the scoreboard
    overstates coverage, which is how a spec starts lying about itself.

    Rows marked ⬜ not-built MAY name a test file that does not exist yet: that is the
    planned filename, and pinning it is useful. The distinction is deliberate — "cites a
    test that vanished" is drift, "names the test it will write" is planning.
    """
    unresolved = []
    for line in spec.read_text(encoding="utf-8").splitlines():
        if "✅" not in line:
            continue
        for cited in re.findall(r"(tests/test_[a-z0-9_]+\.py)", line):
            if not Path(cited).is_file():
                unresolved.append(f"{cited}  (row: {line.strip()[:70]})")
    assert not unresolved, (
        f"{spec} marks rows green whose tests do not exist:\n  " + "\n  ".join(unresolved))


@pytest.mark.parametrize("spec", _spec_files(), ids=lambda p: p.parent.name)
def test_not_built_rows_are_marked_not_green(spec: Path):
    """The converse guard: a row citing a missing test must be honestly marked, so an
    unbuilt AC can never read as done."""
    for line in spec.read_text(encoding="utf-8").splitlines():
        cited = re.findall(r"(tests/test_[a-z0-9_]+\.py)", line)
        if not cited or all(Path(c).is_file() for c in cited):
            continue
        assert "✅" not in line, f"{spec}: row cites a missing test but claims green: {line.strip()[:90]}"


# --------------------------------------------------------------------------- #
# AC-3.4 — characterization tests are labelled (CT-3.1)
# --------------------------------------------------------------------------- #
def test_characterization_tests_are_labelled():
    """Constitution §5.2 makes characterization tests the instrument for legacy code, so
    the inventory must be greppable. The token also forces the author to confront that the
    test freezes behaviour WITHOUT claiming it is correct."""
    # Exclude THIS file: it names the token to define the convention, and counting it
    # would make the assertion self-satisfying — a test that can never go red.
    # ★ B7 (2026-08-25): the legacy tier moved to `backups/`, and the
    #   characterization tests moved WITH the code they freeze. §5.2 makes them
    #   the instrument *for legacy code* — so the guard follows them there and
    #   stays meaningful until Victor deletes the tier at end of release.
    labelled = [p for root in ("tests", "backups/tests")
                for p in Path(root).glob("test_*.py")
                if p.name != "test_sdd_process.py"
                and "CHARACTERIZATION" in p.read_text(encoding="utf-8")]
    assert labelled, (
        "no characterization tests found. Legacy behaviour relied upon must be frozen "
        "with one (constitution §5.2, F3 CT-3.1)")


def test_characterization_tests_disclaim_correctness():
    """The distinction between 'unchanged' and 'correct' is the entire point. A frozen
    bug is still a bug — `_cumulative_fys` had a passing test for two weeks."""
    for p in [q for root in ("tests", "backups/tests")
              for q in Path(root).glob("test_*.py")]:
        text = p.read_text(encoding="utf-8")
        if "CHARACTERIZATION" not in text:
            continue
        lowered = text.lower()
        assert any(s in lowered for s in ("does not claim", "not claim", "never claims",
                                          "freeze", "frozen")), (
            f"{p} labels a characterization test but never states that it freezes "
            f"behaviour rather than endorsing it (F3 CT-3.1)")


# --------------------------------------------------------------------------- #
# AC-3.5 — the gate is live (P1)
# --------------------------------------------------------------------------- #
def test_the_sdd_gate_is_wired():
    """CLAUDE.md and skills only persuade; the hook is the only thing that enforces."""
    gate = Path(".claude/hooks/sdd_gate.py")
    assert gate.is_file(), "the SDD gate script is gone — P1 is unenforced"

    settings = json.loads(Path(".claude/settings.json").read_text(encoding="utf-8"))
    hooks = settings.get("hooks", {})
    for event in ("SessionStart", "PostToolUse", "PreToolUse"):
        assert event in hooks, f"{event} hook missing — the gate is not wired"

    flat = json.dumps(hooks)
    assert "sdd_gate.py" in flat
    matchers = {h.get("matcher") for h in hooks["PreToolUse"]}
    assert "Edit|Write" in matchers, \
        "PreToolUse does not match Edit|Write — writes are not gated"


def test_the_gate_is_project_scoped_so_new_agents_inherit_it():
    """In settings.local.json it would not survive a fresh clone or reach a teammate."""
    assert Path(".claude/settings.json").is_file(), \
        "the gate must live in project settings, not settings.local.json"


# --------------------------------------------------------------------------- #
# AC-3.6 — research stays exempt (P7)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("research_path", [
    "pipeline/ohlcv/experiments/experiment_runner.py",
    "pipeline/buffett/backtest/runner.py",
])
def test_research_paths_are_never_gated(ownership, research_path):
    """P7: exploratory work is exempt from spec rigor. Gating it would tax the one place
    the constitution deliberately leaves free."""
    import fnmatch

    mapped = any(fnmatch.fnmatch(research_path, g)
                 for e in ownership.get("map", []) for g in e.get("globs", []))
    assert not mapped, f"{research_path} is research (P7) but is spec-governed"


# --------------------------------------------------------------------------- #
# AC-3.7 — no retro-spec sprawl (§1)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("spec", _spec_files(), ids=lambda p: p.parent.name)
def test_no_spec_governs_nothing_without_saying_so(spec: Path):
    """F3 §1: a spec written for code nobody intends to change is the failure mode this
    process exists to prevent. Either govern something, or declare yourself descriptive."""
    if spec.parent.name in DESCRIPTIVE_SPECS:
        text = spec.read_text(encoding="utf-8").lower()
        assert "descriptive" in text or "governs nothing" in text or "not a feature spec" in text, (
            f"{spec} governs no code path but never says so — a reader will assume it is "
            f"prescriptive")


def test_the_template_still_exists_for_new_specs():
    assert TEMPLATE.is_file(), "the spec template is gone — new specs will drift in shape"


# --------------------------------------------------------------------------- #
# AC-3.8 — the tier layout survives a release boundary (CT-3.5)
# --------------------------------------------------------------------------- #
def test_the_sdd_tiers_exist():
    """CT-3.5 — specs (authoritative, permanent) / design (release-scoped) / archive (frozen).
    The whole layout exists so that opening rel7 moves only the design tier."""
    for path in (SDD / "README.md", SPECS / "constitution.md", OWNERSHIP,
                 SPECS / "README.md", TEMPLATE, SDD / "design", SDD / "archive"):
        assert path.exists(), f"{path} is missing — the SDD tier layout is incomplete (CT-3.5)"


def test_the_vision_is_release_independent():
    """CT-3.5 — the project's goal must not live under a `rel<N>`-scoped filename.

    It did until 2026-08-08: the fund-desk roles model, the mandate, and the guiding vision sat in
    `design/rel6_brainstorm.md` — a file whose own header says NON-AUTHORITATIVE, do not code from
    this. At the rel7 boundary that content is copied (and drifts) or orphaned. This asserts the
    fix stays fixed.
    """
    assert VISION.is_file(), (
        "sdd/specs/vision.md is missing — an agent reading only the constitution learns the rules "
        "but never what the project is for (CT-3.5)")
    assert "rel" not in VISION.parent.name.lower(), \
        f"the vision lives under a release-scoped path ({VISION.parent}) — it must outlive releases"

    text = VISION.read_text(encoding="utf-8")
    # ⚠⚠ DX-10 — this list was upstream's FIVE-seat vocabulary. `CLAUDE.md`:
    # *"The seat model is this repo's own — nine seats, numbered 1-9. Upstream L0
    # §1.5 numbers five. Never carry a seat number between the two repos."*
    # ★ The absorbed test did exactly that. These are THIS repo's nine-seat terms.
    for token in ("Fund PM", "Analyst", "Back Office", "Orchestrator", "Experiments"):
        assert token.lower() in text.lower(), \
            f"vision.md does not mention '{token}' — the nine-seat model is the load-bearing part"
    assert re.search(r"\|\s*\*?\*?F5", text), \
        "vision.md has no reserved-F<n> desk registry — future desks have nowhere to be recorded"


def test_the_design_tier_has_templates_for_the_next_release():
    """A release boundary is the moment the process is most likely to be improvised. CT-3.5."""
    assert (SDD / "design" / "_templates" / "brainstorm.md").is_file(), \
        "no brainstorm template — rel<N+1> will be opened ad hoc"
    closeout = SDD / "design" / "releases" / "_template_closeout.md"
    assert closeout.is_file(), "no close-out template — binding decisions freeze with the brainstorm"
    text = closeout.read_text(encoding="utf-8")
    assert "Decisions promoted" in text, \
        "the close-out template does not force decisions out of the brainstorm before it freezes"


@pytest.mark.parametrize("archived", sorted(p for p in (Path("sdd/archive")).glob("*")
                                            if p.is_file() and p.name != "README.md"),
                         ids=lambda p: p.name)
def test_every_archived_file_disclaims_authority(archived: Path):
    """CT-3.5 — a banner in the file, not only in a sibling README.

    `rel3_todo_agent_tasks.md` opens with "This file is intended for an AI agent to implement" and
    `rel5_document.md` calls itself "The single source of truth". Both were true in their release.
    An agent that opens one directly, without the directory README, has no way to know otherwise.
    """
    head = archived.read_text(encoding="utf-8", errors="replace")[:1200].upper()
    assert "ARCHIVED" in head and "DO NOT CODE FROM" in head, (
        f"{archived} carries no archive banner — it reads as live instruction (CT-3.5)")
