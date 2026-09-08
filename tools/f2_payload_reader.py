"""The `F2` adapter for `F5`'s golden regression — wired here, outside `src/`.

⚠⚠ **Why this file is not in `src/`.** Two import fences meet at the golden
regression and both bind:

    OR-3  no domain imports orchestration   → src/evaluation/ ↛ src/orchestration/
    ST-2  nothing imports the harness       → src/orchestration/ ↛ src/evaluation/

Neither direction is legal, so the two halves are joined by their **caller**.
★ That caller is CI, which is exactly `F5` `T1`: *"CI, every build"*. The
regression is not part of a production run and must not be reachable from one.

★ `OR-3` caught this on the first attempt, when `replay.py` imported
`TraceStore` directly (`DX-21`).
"""

from __future__ import annotations

import pathlib

from src.evaluation.regression.replay import UnresolvableCase
from src.orchestration.trace.errors import IncompleteTrace, PayloadsExpired
from src.orchestration.trace.store import TraceStore


def f2_payload_reader(root: str | pathlib.Path):
    """A `PayloadReader` over `F2`'s on-disk payloads (`CT-2.8`).

    ⚠ Every failure is translated to `UnresolvableCase` and **raised**. The
    tempting alternative — returning nothing so the case is skipped — turns a
    broken baseline into a *smaller* baseline that still reports green.
    """
    root = pathlib.Path(root)

    def read_payload(run_id: str, call_id: str) -> dict:
        try:
            return TraceStore(root, run_id).payload(call_id)
        except PayloadsExpired as exc:
            # ⚠ `F2` `D2` expires raw payloads while keeping decisions forever.
            # ★ A case whose evidence expired is UNREPLAYABLE — a different fact
            #   from "the reading changed". Reporting it as either a pass or a
            #   failure would state something untrue.
            raise UnresolvableCase(
                f"{run_id}/{call_id}: payloads expired ({exc}) — the recording "
                "this case grades no longer exists (F2 D2 retention). ⚠ Re-record "
                "or retire the case; do not silently drop it"
            ) from None
        except IncompleteTrace as exc:
            raise UnresolvableCase(f"{run_id}/{call_id}: {exc}") from None

    return read_payload
