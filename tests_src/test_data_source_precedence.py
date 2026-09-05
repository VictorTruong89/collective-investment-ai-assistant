"""Data-source precedence — EDGAR + FMP only, never yfinance.

★ **Migrated from `tests/test_data_source_precedence.py` at B7** (G-7, BS-18):
the original pinned the rule against `pipeline/**`, whose modules moved to
`backups/` on 2026-08-25. **The rule outlived the tree it was written against**,
which is exactly why G-7 requires the ACs to migrate *before* retirement.

> *"For fundamental data sources, do not follow yfinance because of many known
> errors and corrupted data."*

⚠ **The pin is on the STRING, not just the import.** *A stale comment is how the
`DataValidator` mislabel survived a whole release*: yfinance had been removed
from the fundamentals path while the validator's WARN lines still said
"yfinance", so a real FMP-vs-EDGAR disagreement was reported as a yfinance
problem.

Tier: unit (constitution §4).
"""

from __future__ import annotations

from pathlib import Path

from tests_src.architecture import SRC_ROOTS

BANNED_CALLS = ("import yfinance", "from yfinance", "yf.Ticker",
                "yfinance.download", "yfinance.Ticker")

#: ★ The new tree, and the config that drives it. `backups/**` is deliberately
#: NOT scanned — it is frozen legacy held for review, not code that runs.
#: ⚠⚠ MULTI-ROOT (DX-9). These scans resolve the FILESYSTEM, not imports, so
#: DX-3's fix to the import graph did not cover them. When a domain is absorbed
#: into the sibling repo, a scan pinned to `Path("src")` silently stops covering
#: it — and because these tests assert ABSENCE (`offenders == []`), a smaller
#: tree passes trivially. ★ The yfinance ban stopped covering two whole domains
#: and stayed green; the sibling test below failed only because it happened to
#: assert PRESENCE. Same bug, one loud instance and one silent one.
SCANNED = tuple(r for root in SRC_ROOTS for r in (root, root.parent / "tools")
                if r.is_dir())


def test_no_live_yfinance_call_anywhere_in_the_new_tree():
    """The rule CLAUDE.md pins: *yfinance is gone from the code base and must
    not return.*"""
    offenders = []
    for root in SCANNED:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for banned in BANNED_CALLS:
                if banned in text:
                    offenders.append(f"{path} ({banned})")
    assert offenders == [], f"yfinance called in: {offenders}"


#: ★ A mention that SAYS it was removed is a record, not drift — the same
#: tombstone principle the `spec pointers resolve` audit check uses. ⚠ The
#: defect the `DataValidator` incident actually caused was a **live label**
#: claiming yfinance was the source; a line stating its removal is the cure.
_REMOVAL_WORDS = ("removed", "gone", "never", "must not", "no longer", "banned")


def test_a_yfinance_mention_must_say_it_was_removed():
    """⚠ **The string, not just the import.** *A stale comment is how the
    `DataValidator` mislabel survived a whole release* — so a module may name
    yfinance only on a line that records its removal.

    ★ Anything else is a mention with no stated reason, which is
    indistinguishable from drift creeping back.
    """
    offenders = []
    for root in SCANNED:
        for path in root.rglob("*.py"):
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                low = line.lower()
                if "yfinance" not in low:
                    continue
                if not any(w in low for w in _REMOVAL_WORDS):
                    offenders.append(f"{path}:{n}")
    assert offenders == [], (
        f"yfinance named without recording its removal: {offenders}")


def test_the_config_names_no_yfinance_source():
    """The legacy `market_data.source` knob may not resurrect it."""
    offenders = []
    for path in Path("config").glob("*.yaml"):
        if "yfinance" in path.read_text(encoding="utf-8").lower():
            offenders.append(str(path))
    assert offenders == [], f"yfinance named in config: {offenders}"


def test_edgar_beats_fmp_for_ttm_and_the_code_says_why():
    """★ **EDGAR wins for TTM line items** — *its facts carry explicit period
    start AND end, so a discrete quarter is distinguishable from a cumulative
    YTD one by arithmetic*, whereas FMP exposes only the period end and must
    guess. ⚠ **It guessed wrong on MU by 71 %** (and `_cumulative_fys` by
    41.5 % — see `sdd/design/rel6_design/L5-inherited-defects.md` §3 D-4).
    """
    # ⚠ DX-9 — resolve the directory across BOTH roots; it moved at MS-6.
    edgar = [d for root in SRC_ROOTS
             if (d := root / "data_engine" / "src" / "edgar").is_dir()]
    assert edgar, ("src/data_engine/src/edgar was not found under any root — if "
                   "the domain moved again, add its root (DX-9)")
    seen = " ".join(p.read_text(encoding="utf-8")
                    for d in edgar for p in d.rglob("*.py"))
    assert "period" in seen, "the EDGAR path must reason about periods at all"
    spec = Path("sdd/design/rel6_design/L1-data-engine.md").read_text(
        encoding="utf-8")
    assert "EDGAR" in spec and "period_type" in spec
