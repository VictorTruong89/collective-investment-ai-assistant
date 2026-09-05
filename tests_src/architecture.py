"""Import-graph scanner for the architectural rules (L3 BS-4).

WHY AST AND NOT GREP
--------------------
`L4-coding-standards.md` §10.1 specifies each rule as a grep, e.g. ST-5 as::

    grep -rn "llm" src/ | grep -v "^src/fundamental/\\|^src/shared/llm/"

That matches the *string* `llm` anywhere — a docstring in `src/reporting/` that
mentions the LLM gateway would fail the build. The rules are about IMPORTS
("the gateway is imported only by src/fundamental/"), so parsing imports
enforces the stated rule; grepping text enforces a proxy for it.

This module implements the rule. The greps stay in L4 as the human-readable
statement of intent.

Shared by:
  test_architecture.py            — the rules hold on the real tree
  test_architecture_violates.py   — each rule FIRES on a planted violation (BS-5)
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: ⚠⚠ MULTI-ROOT — the rules span BOTH trees during the absorption period.
#:
#: `src/shared/` was absorbed into ../collective-investment-ai-assistant on
#: 2026-09-04 (that repo's QR-22: absorption is PER-DOMAIN, and the two trees
#: never both hold one domain). `src` is an implicit namespace package spanning
#: both, so an import edge can now CROSS the repo boundary.
#:
#: ⚠ Scoping these rules to one repo is not merely incomplete, it is SILENT:
#: SI-1 (`importer_prefixes=("src/shared/",)`) went from policing a directory to
#: scanning ZERO files the moment that directory moved, and reported `14 passed`.
#: Nothing failed. See that repo's L3 DX-3 — and `test_the_graph_is_not_vacuous`
#: below, which exists so that cannot recur unnoticed.
#: ✏ MS-8: emptied. Every domain now lives in one tree.
#: ⚠ The MECHANISM stays — SRC_ROOTS, source_path() and the vacuity guard
#: cost nothing and are what made DX-3/DX-9 findable. Deleting them would
#: remove the instrument along with the situation it was built for.
_SIBLING_REPOS: tuple[str, ...] = ()


def _src_roots() -> tuple[Path, ...]:
    """Every `src/` tree the rules apply to: this repo's, plus absorbed siblings.

    Override with ARCHITECTURE_SRC_ROOTS (os.pathsep-separated, absolute or
    sibling-relative) — used by CI where the checkout layout differs.
    """
    roots = [REPO / "src"]
    override = os.environ.get("ARCHITECTURE_SRC_ROOTS")
    names = override.split(os.pathsep) if override else _SIBLING_REPOS
    for name in names:
        if not name:
            continue
        base = Path(name) if os.path.isabs(name) else REPO.parent / name
        src = base / "src"
        if src.is_dir() and src.resolve() != (REPO / "src").resolve():
            roots.append(src)
    return tuple(roots)


SRC_ROOTS = _src_roots()

#: This repo's own tree. ⚠ Prefer SRC_ROOTS — a rule written against SRC alone
#: stops seeing a domain the day it is absorbed.
SRC = REPO / "src"


def source_path(rel: str) -> Path:
    """Resolve a repo-root-relative path across EVERY root — `DX-9`.

    ⚠⚠ **Why this exists.** Tests that scan the FILESYSTEM (rather than the
    import graph) break or, worse, go **silent** when a domain is absorbed into
    the sibling repo:

    * a test that stays while its target moves → `FileNotFoundError`, or an
      empty scan that **passes** if it asserts absence;
    * a test that moves while its target stays → the same, mirrored.

    ★ Both were seen at `MS-6` within minutes of each other. Use this instead of
    `Path("src/...")` in any test that reads a file by path, and the question
    "which repo owns that domain today?" stops being the test's problem.

    Raises rather than returning a non-existent path: a silent miss is the
    failure mode this whole helper exists to remove (`P5`).
    """
    rel = rel.lstrip("/")
    tried = []
    for root in SRC_ROOTS:
        candidate = root.parent / rel
        tried.append(candidate)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"{rel!r} was not found under any root (DX-9). Tried: "
        + ", ".join(str(t) for t in tried)
        + ". If the domain moved again, add its repo to _SIBLING_REPOS or set "
          "ARCHITECTURE_SRC_ROOTS.")


def imports_of(source: str, filename: str = "<memory>") -> set[str]:
    """Every dotted module name imported by a Python source string.

    Relative imports are returned with a leading dot count intact so a caller
    can tell them apart; no rule below concerns them today, but silently
    flattening them would hide a future violation.
    """
    found: set[str] = set()
    tree = ast.parse(source, filename=filename)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * (node.level or 0)
            found.add(prefix + (node.module or ""))
    return found


def scan(roots=None) -> dict[str, set[str]]:
    """Map every .py file under every root in `roots` to the modules it imports.

    Keys are POSIX-style `src/<domain>/...` paths, taken relative to EACH root's
    own parent — not to this repo — so a file absorbed into a sibling repo keys
    identically to one here and every existing prefix rule keeps working
    unchanged.

    ⚠ A key appearing under two roots means one domain exists in both trees,
    which is exactly what per-domain absorption forbids (QR-22). That raises
    rather than silently letting one shadow the other.
    """
    if roots is None:
        roots = SRC_ROOTS
    elif isinstance(roots, (str, Path)):
        roots = (Path(roots),)

    out: dict[str, set[str]] = {}
    origin: dict[str, Path] = {}
    for root in roots:
        for path in sorted(Path(root).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = path.relative_to(Path(root).parent).as_posix()
            if rel in out:
                raise RuntimeError(
                    f"{rel} exists in TWO trees: {origin[rel]} and {path}. "
                    "Per-domain absorption (QR-22) requires exactly one owner; "
                    "two copies mean imports resolve to whichever root is first "
                    "on sys.path, silently."
                )
            origin[rel] = path
            out[rel] = imports_of(path.read_text(encoding="utf-8"), rel)
    return out


def _hits(graph, *, importer_prefixes, target_prefixes, exempt_prefixes=()):
    """Files under `importer_prefixes` importing anything under `target_prefixes`.

    Prefixes are path-style (`src/quant/`) for importers and module-style
    (`src.decision`) for targets, because that is how each is written in the
    specs — translating once here beats translating at every call site.
    """
    bad = []
    for file, mods in graph.items():
        if importer_prefixes and not any(file.startswith(p) for p in importer_prefixes):
            continue
        if any(file.startswith(p) for p in exempt_prefixes):
            continue
        for mod in mods:
            if any(mod == t or mod.startswith(t + ".") for t in target_prefixes):
                bad.append(f"{file} imports {mod}")
    return bad


# --------------------------------------------------------------------------- #
# The rules. Each returns a list of violations — empty means the rule holds.
# One function per rule ID so a failure names the rule the reader must go read.
# --------------------------------------------------------------------------- #

def st_1(graph):
    """ST-1 — src/ must not import pipeline/, ever, including temporarily.

    The legacy tree depends on the new one via shims; the reverse makes
    pipeline/ undeletable and the parallel build a permanent fork (L3 BS-20).
    """
    return _hits(graph, importer_prefixes=("src/",), target_prefixes=("pipeline",))


def st_2(graph):
    """ST-2 — no domain imports src/experiments/ (D-10).

    P7 exempts experiments from spec rigor; this one-way rule is what stops the
    exemption leaking into production by import rather than by decision. It is
    load-bearing precisely because D-10 has no spec (L0 §4.2).
    """
    return _hits(graph, importer_prefixes=("src/",), target_prefixes=("src.experiments",),
                 exempt_prefixes=("src/experiments/",))


def st_5(graph):
    """ST-5 — the LLM gateway is imported only by src/fundamental/ (D-01)."""
    return _hits(graph, importer_prefixes=("src/",), target_prefixes=("src.shared.llm",),
                 exempt_prefixes=("src/fundamental/", "src/shared/llm/"))


def st_9(graph):
    """ST-9 — src/recording/ (D-11) must not import src/reporting/ (D-09).

    Recording is LEVEL 0 custody of fact; Reporting is LEVEL 1 advice. The
    forbidden direction puts a renderer upstream of the book.
    """
    return _hits(graph, importer_prefixes=("src/recording/",), target_prefixes=("src.reporting",))


def st_10(graph):
    """ST-10 — neither analyst seat imports src/decision/ (D-12).

    A composed verdict returning to an analyst seat is INV-014 laundered
    through a third party and a time lag (L1-decision DN-3).
    """
    return _hits(graph, importer_prefixes=("src/fundamental/", "src/quant/"),
                 target_prefixes=("src.decision",))


def or_3(graph):
    """OR-3 — no domain imports src/orchestration/ (D-08).

    Invocation is one-way. A domain that imports the scheduler becomes
    schedule-aware and untestable standalone.
    """
    return _hits(graph, importer_prefixes=("src/",), target_prefixes=("src.orchestration",),
                 exempt_prefixes=("src/orchestration/",))


def si_1(graph):
    """SI-1 — src/shared/ imports no src/<domain>/.

    A shared module that knows about a domain is that domain's module in the
    wrong folder.
    """
    domains = tuple(
        f"src.{d}" for d in (
            "data_engine", "feature_engineer", "fundamental", "quant", "models",
            "risk", "portfolio", "decision", "orchestration", "reporting",
            "recording", "experiments",
        )
    )
    return _hits(graph, importer_prefixes=("src/shared/",), target_prefixes=domains)


#: The analytical domains D-02 must not consume (FE-21, INV-014).
_ANALYTICAL = ("src.fundamental", "src.quant", "src.models", "src.risk",
               "src.portfolio", "src.decision")


def fe_21(graph):
    """FE-21 / AC-2.24 — src/feature_engineer/ imports no analytical domain.

    ★ D-02 is NEUTRAL GROUND, and that is the property keeping INV-014 intact:
    neither analyst seat consumes the other's output BECAUSE the layer upstream
    of both consumes neither.

    ⚠ Including a deterministic transform of one. `MoatScorer._llm_score` never
    calls a model and reads three fields an LLM authored — **the determinism is
    in the transport, not the source.**
    """
    return _hits(graph, importer_prefixes=("src/feature_engineer/",),
                 target_prefixes=_ANALYTICAL)


def qa_21(graph):
    """AC-3.21 — src/quant/ imports neither src/models/ (D-04) nor src/fundamental/.

    QA-28: D-03 is **stateless** — no module holds fitted parameters. Importing
    D-04 is how a ranker acquires one; importing D-01 is how seat 3 starts
    reading seat 2 (INV-014).
    """
    return _hits(graph, importer_prefixes=("src/quant/",),
                 target_prefixes=("src.models", "src.fundamental"))


def rp_30(graph):
    """RP-30 / AC-9.28 — src/reporting/ writes to nothing it renders.

    ⚠ Structural, not stylistic: **a renderer that can mutate the book can
    rewrite history to match what it printed.** ST-9 states the D-11 direction;
    this is its generalisation to every producing domain D-09 reads.
    """
    return _hits(graph, importer_prefixes=("src/reporting/",),
                 target_prefixes=("src.recording", "src.data_engine"))


def ra_45(graph):
    """RA-45 / AC-1.49 — src/fundamental/ computes no series arithmetic.

    ★ **D-01 never detects a price move** (RA-78). It receives a *decomposed*
    move as an input with its arithmetic trail, exactly as it receives a fair
    value — and the decomposition comes from **D-02**, not D-03, because D-02 is
    neutral ground (L0 §4.2), so consuming it is not consuming SEAT-3's output.

    ⚠ Structural because the alternative is unenforceable by review: a prompt
    that reads a price series and concludes it moved a lot is **arithmetic in a
    prompt** (P2), and it looks like prose. A domain with no array library
    cannot compute a return, a volatility or a decomposition by accident.
    """
    return _hits(graph, importer_prefixes=("src/fundamental/",),
                 target_prefixes=("pandas", "numpy", "scipy", "sklearn"))


#: Vendor SDKs and I/O surfaces the inner layers may not reach for (CA-1, CA-2).
_IO_AND_VENDOR = (
    "anthropic", "requests", "httpx", "urllib", "urllib3", "boto3",
    "sqlite3", "psycopg2", "pyarrow", "smtplib", "socket", "os.path",
)


def ca_1(graph):
    """CA-1 — models.py imports no I/O, no vendor SDK, no config, no logger.

    The innermost circle, and the first to be quietly polluted by "just one"
    config read.
    """
    targets = _IO_AND_VENDOR + ("logging", "src.shared.config", "src.shared.logging")
    files = {f: m for f, m in graph.items() if Path(f).name == "models.py"}
    return _hits(files, importer_prefixes=(), target_prefixes=targets)


def ca_2(graph):
    """CA-2 — service.py imports no transport, no filesystem path, no vendor SDK.

    It receives what it needs. A service.py holding a URL, a key lookup, an
    open() or a requests import has inverted the rule.
    """
    targets = _IO_AND_VENDOR + ("pathlib",)
    files = {f: m for f, m in graph.items() if Path(f).name == "service.py"}
    return _hits(files, importer_prefixes=(), target_prefixes=targets)


#: (rule id, spec that defines it, checker). Extending this is how a new
#: structural rule enters CI — and BS-5 requires a violating test with it.
RULES = [
    ("ST-1", "L4 §10.1", st_1),
    ("ST-2", "L4 §10.1", st_2),
    ("ST-5", "L4 §10.1 · L2-shared-infrastructure GW-1", st_5),
    ("ST-9", "L4 §10.1", st_9),
    ("ST-10", "L4 §10.1", st_10),
    ("OR-3", "L1-orchestration OR-3", or_3),
    ("SI-1", "L2-shared-infrastructure SI-1", si_1),
    ("CA-1", "L4 §18", ca_1),
    ("CA-2", "L4 §18", ca_2),
    ("FE-21", "L1-feature-engineering FE-21 · INV-014", fe_21),
    ("QA-21", "L1-quantitative-analysis AC-3.21 · QA-28", qa_21),
    ("RP-30", "L1-reporting RP-30 · ST-9", rp_30),
    ("RA-45", "L1-fundamental-analysis RA-45/RA-78 · AC-1.49", ra_45),
]
