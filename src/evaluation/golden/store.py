"""F5 `CT-5.5` / `AC-5.17` — where golden cases live, and how they load.

⚠⚠ **Why this module exists.** `D2` made establishing golden values the fund
manager's work — and then left nowhere to put one. `GoldenCase` was a dataclass
with no store, so adding a case meant editing Python. ★ **A decision that
assigns a human a task must leave them a way to do it**, or the task silently
does not happen; the golden set stayed empty for exactly that reason.

★ One YAML file per `kind`, version-controlled: a golden set that is not
versioned cannot show drift, and drift is the only thing a regression measures.

⚠ Every case is constructed through `CT-5.2`'s validation, so `D2`'s
circularity check runs on **file contents** — not only on values a programmer
typed into a test.
"""

from __future__ import annotations

import pathlib

import yaml

from src.evaluation.golden.models import GoldenCase

#: ⚠ NOT published. `expected` values for `thesis` are the fund's
#: judgement — the strategy `QR-12` withholds. The mirror ships the machinery
#: without the answers (`tools/build_mirror.py`).
GOLDEN_DIR = "tests_src/fixtures/golden"

#: ⊘ `ranking` removed 2026-09-10 — `F5` `D6` / `DX-62`.
KINDS = ("extraction", "thesis")


class GoldenSetError(Exception):
    """⚠ Loud, per `P5`. A golden set that loads partially is not a baseline."""


def load_kind(kind: str, root: str | pathlib.Path = GOLDEN_DIR) -> tuple[GoldenCase, ...]:
    """Load one kind's file. ★ Absent file → empty tuple, which is not an error.

    ⚠ An **empty** golden set is a real and honest state (`F5` `D2` — Victor has
    not written them yet). A *malformed* one is not, and raises.
    """
    path = pathlib.Path(root) / f"{kind}.yaml"
    if not path.exists():
        return ()
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise GoldenSetError(f"{path} is not valid YAML: {exc}") from None
    rows = doc.get("cases") or []
    cases = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise GoldenSetError(f"{path}: case {i} is not a mapping")
        try:
            cases.append(GoldenCase(kind=kind, **row))
        except TypeError as exc:
            raise GoldenSetError(
                f"{path}: case {row.get('case_id', i)!r} — {exc}. Every field of "
                "CT-5.2 is required: case_id, input_ref, expected, source, "
                "established_at, established_by"
            ) from None
        except ValueError as exc:
            # ⚠ `CT-5.2`'s own field rules (empty `source`, empty `expected` —
            # `DX-20`). Re-raised naming the FILE: a validation message that
            # cannot say which case it rejected sends the reader to grep.
            # ★ `CircularGoldenValue` is deliberately NOT caught here — it does
            #   not derive from `ValueError`, and `D2`'s refusal must reach the
            #   caller wearing its own name.
            raise GoldenSetError(f"{path}: {exc}") from None
    return tuple(cases)


def load_all(root: str | pathlib.Path = GOLDEN_DIR) -> tuple[GoldenCase, ...]:
    """Every kind. ⚠ A duplicate `case_id` across files raises (`AC-5.17`)."""
    out: list[GoldenCase] = []
    seen: dict[str, str] = {}
    for kind in KINDS:
        for case in load_kind(kind, root):
            if case.case_id in seen:
                raise GoldenSetError(
                    f"duplicate case_id {case.case_id!r} in {kind}.yaml and "
                    f"{seen[case.case_id]}.yaml — ⚠ ids must be unique across the "
                    "whole set, or a regression report names a case ambiguously"
                )
            seen[case.case_id] = kind
            out.append(case)
    return tuple(out)


def coverage(root: str | pathlib.Path = GOLDEN_DIR) -> dict[str, int]:
    """How many cases per kind. ★ Reported so *empty* is visible, not assumed."""
    return {k: len(load_kind(k, root)) for k in KINDS}
