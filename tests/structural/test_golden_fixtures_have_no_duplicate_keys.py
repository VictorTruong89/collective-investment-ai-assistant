"""`DX-137` — a golden fixture may not repeat a mapping key.

⚠⚠ YAML keeps only the LAST value of a repeated key, and says nothing.
`extraction.pending.yaml` carried four top-level `cases:` keys, so a loader saw
the last 3 cases and silently dropped the 16 above them; `thesis.pending.yaml`
dropped 2 of 10 the same way. ★ A signed case lost like that would vanish from
the golden set with the suite still green.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = sorted((REPO / "tests_src/fixtures/golden").glob("*.yaml"))


class _StrictLoader(yaml.SafeLoader):
    pass


def _no_duplicates(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key {key!r}", key_node.start_mark)
        seen.add(key)
    return loader.construct_mapping(node, deep)


_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def test_there_are_golden_fixtures_to_check():
    assert len(FIXTURES) >= 4


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_dx_137_no_golden_fixture_repeats_a_key(path):
    """DX-137 — a repeated key silently discards every value but the last."""
    yaml.load(path.read_text(encoding="utf-8"), Loader=_StrictLoader)  # noqa: S506
