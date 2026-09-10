"""Wire `F5`'s golden regression to `F2`'s recordings — the CI composition root.

    from tools.golden_replay import golden_replay
    report = run_regression(load_all(), golden_replay(".state/runs"))

⚠⚠ **Why this file exists.** `AC-5.18`'s selector matches an item by its
`MP-18` identity — `(evidence_id, qualifier, period)` — but what `F2` records is
the **raw model output**, whose keys are flat (`period_start`, `period_end`) and
which is wrapped in `{"items": [...]}`. Pointing the selector straight at that
gets *"the recorded response is dict, not a list of items"*, and even unwrapped
it could never match on `period`.

★ `recorded_response(..., parse=...)` exists for exactly this, and it was simply
never wired. The parse converts the recording into the shape a golden case's
`expected` is written in — `ExtractedItem.to_json_obj()` — **before** the
selector runs.

★★ It lives outside `src/` for the same reason as `f2_payload_reader.py`:
`OR-3` forbids `src/evaluation/` from importing orchestration and `ST-2` forbids
anything importing the harness, so the two halves are joined by their caller.
"""

from __future__ import annotations

import json
import pathlib
from collections.abc import Callable

from src.evaluation.regression.replay import recorded_response
from tools.f2_payload_reader import f2_payload_reader
from tools.run_extraction_once import FILING, parse_items

#: ⚠ The VERSION-CONTROLLED recordings, not `.state/runs/` — that is gitignored,
#: so a golden case pointed at it runs on exactly one laptop (`DX-12`'s shape).
REPO = pathlib.Path(__file__).resolve().parent.parent
RECORDINGS = REPO / "tests_src/fixtures/recordings"


def _as_recorded_items(bundle_text: str) -> Callable[[object], list]:
    """Recording → `ExtractedItem.to_json_obj()` list, the shape cases use."""

    class _Call:
        def __init__(self, text):
            self.text = self.parsed = text

    def parse(response: object) -> list:
        payload = response
        if isinstance(payload, dict) and "text" in payload:
            payload = payload["text"]
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        return [it.to_json_obj() for it in parse_items(_Call(payload), bundle_text)]

    return parse


def golden_replay(root: str | pathlib.Path | None = None,
                  bundle_text: str | None = None) -> Callable[[str], object]:
    """The `replay_response` a golden case's `input_ref` resolves through.

    ⚠ `bundle_text` must be the SAME text the call was recorded against —
    offsets and quotes are checked against it. Defaults to the filing fixture,
    which is what `run_extraction_once.py` sends.
    """
    if root is None:
        root = RECORDINGS
    root = pathlib.Path(root)

    if bundle_text is not None:          # ★ explicit override, used by tests
        return recorded_response(f2_payload_reader(root),
                                 parse=_as_recorded_items(bundle_text))

    # ⚠⚠ One bundle for every case was wrong the moment a SECOND filing joined
    # the golden set: AMD's cases were parsed against MU's text and every quote
    # "was not in the bundle". ★ Each recording states its own filing.
    cache: dict[str, str] = {}

    def _text_for(run_id: str) -> str:
        if run_id not in cache:
            manifest = root / run_id / "filing.json"
            fixture = (json.loads(manifest.read_text())["fixture"]
                       if manifest.exists() else str(FILING))
            cache[run_id] = (REPO / fixture).read_text(encoding="utf-8")
        return cache[run_id]

    reader = f2_payload_reader(root)

    def replay(input_ref: str):
        run_id = input_ref.split("/", 1)[0]
        return recorded_response(
            reader, parse=_as_recorded_items(_text_for(run_id)))(input_ref)

    return replay
