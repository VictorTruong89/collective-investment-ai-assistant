#!/usr/bin/env python3
"""Re-apply the current renderer to the committed filing fixtures (`DX-35`).

    python3 tools/rerender_fixtures.py --dry-run   # ★ free, shows the diff size
    python3 tools/rerender_fixtures.py --apply     # ⚠ rewrites the fixtures

⚠⚠ **This rewrites version-controlled evidence.** `L7` §5 calls a re-render
load-bearing, and it is — but ★ §10.3 amends the rule from *never* to **measure
the blast radius first**, because a re-render invalidates a recording only if it
moves text the model actually QUOTED.

★★ `--dry-run` performs that measurement: for every recording it re-locates
every recorded quote against the NEW text and reports how many stop resolving.
**If that number is not 0, do not apply.** The same question is asked
permanently by `test_every_recorded_quote_still_resolves_in_its_filing`
(`DX-36`, the drift detector that used to exist only in a docstring).
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.convert_filing import strip_page_furniture  # noqa: E402

FIXTURES = REPO / "tests_src/fixtures/filings"
RECORDINGS = REPO / "tests_src/fixtures/recordings"

#: ★ The renderer steps that are safe to re-apply to already-converted TEXT.
#: ⚠ The HTML stages are not: the source `.htm` is not kept in the repo.
RERENDER = strip_page_furniture


def _quotes_for(fixture_rel: str):
    """Every recorded quote made against this fixture, with its recording."""
    for manifest in sorted(RECORDINGS.glob("*/filing.json")):
        if json.loads(manifest.read_text())["fixture"] != fixture_rel:
            continue
        for pf in sorted((manifest.parent / "trace/payloads").glob("*.json")):
            resp = json.loads(pf.read_text()).get("response")
            body = resp.get("text") if isinstance(resp, dict) else resp
            if not isinstance(body, str):
                body = json.dumps(body)
            for row in json.loads(body).get("items", []):
                if row.get("quote"):
                    yield manifest.parent.name, row["evidence_id"], row["quote"]


def main() -> int:
    apply = "--apply" in sys.argv
    if not apply and "--dry-run" not in sys.argv:
        print(__doc__.splitlines()[2].strip())
        return 2

    from tools.run_extraction_once import _locate

    broken_total = 0
    for path in sorted(FIXTURES.glob("*.txt")):
        rel = str(path.relative_to(REPO))
        old = path.read_text(encoding="utf-8")
        new = RERENDER(old)
        broken = [(r, e, q) for r, e, q in _quotes_for(rel)
                  if _locate(new, q)[0] < 0]
        broken_total += len(broken)
        flag = "✅" if not broken else "⛔"
        print(f"  {flag} {path.name}: {len(old):,} -> {len(new):,} chars "
              f"({len(old) - len(new):,} removed); "
              f"recorded quotes that stop resolving: {len(broken)}")
        for r, e, q in broken[:5]:
            print(f"       ⛔ {r} {e} {q[:60]!r}")
        if apply and not broken and new != old:
            path.write_text(new, encoding="utf-8")
            print(f"       ✍ rewritten")

    if broken_total:
        print("\n  ⛔ NOT applied to at least one fixture — a re-render that moves "
              "quoted text invalidates its recording (L7 §5). Re-record, or "
              "narrow the renderer change.")
        return 1
    print("\n  ✅ blast radius = 0." + ("" if apply else
          "  Re-run with --apply to rewrite."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
