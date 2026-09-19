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


#: ⚠⚠ `RA-5` splits EXTRACTION (*what does this document say* — ground truth
#: exists) from JUDGEMENT (*is this good* — none does), and the two have
#: different output shapes. ★ The replay layer did not know the difference: it
#: parsed every recording with `parse_items`, so the first `judge:J-01`
#: recording failed with `'str' object has no attribute 'get'` (`DX-66`).
#:
#: ★★ The call_id carries the kind — `extract:E-01:llm:1` vs `judge:J-01:llm:1`
#: — so dispatch needs no new field and no guess.
JUDGEMENT_PREFIX = "judge:"


def _as_judgement(response: object) -> dict:
    """A judgement returns ONE object, not a list of items.

    ⚠ There is no `X-01` here and there must not be: a classification has no
    quoted span to verify against, and `F9` `D1` rejects *"two contracts
    wearing one name"*. ★ What grades it is `D2`'s recorded judgement —
    `is_judgement` is True for `thesis`.
    """
    import json as _json
    body = response
    if isinstance(body, dict) and "text" in body:
        body = body["text"]
    if not isinstance(body, str):
        body = _json.dumps(body)
    return _json.loads(body[body.index("{"):body.rindex("}") + 1])


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
            # ★★ `DX-132` — a recording states its own bundle shape. `sector.json`
            #   means the industry evidence: the competitors' documents, rendered in
            #   the sector file's one permitted order (`RA-99`), which is the text
            #   `X-01` verified those quotes against when the call was made.
            #   ⚠ Checked BEFORE `filing.json` because a sector recording has no
            #   filing, and falling through to the default would resolve industry
            #   quotes against Micron's 10-Q — `DX-70`'s defect in a new shape.
            sector = root / run_id / "sector.json"
            if sector.exists():
                from tools.promote_recording import sector_text
                manifest = json.loads(sector.read_text())
                # ★ The COPY that travels with the recording, never `.state/`.
                cache[run_id] = sector_text(sector.parent / manifest["sector_file"])
            else:
                manifest = root / run_id / "filing.json"
                fixture = (json.loads(manifest.read_text())["fixture"]
                           if manifest.exists() else str(FILING))
                cache[run_id] = (REPO / fixture).read_text(encoding="utf-8")
        return cache[run_id]

    reader = f2_payload_reader(root)

    def replay(input_ref: str):
        run_id, _, rest = input_ref.partition("/")
        call_id = rest.split("#", 1)[0]
        # ★ `RA-5` — dispatch on the kind the call_id already declares.
        parse = (_as_judgement if call_id.startswith(JUDGEMENT_PREFIX)
                 else _as_recorded_items(_text_for(run_id)))
        return recorded_response(reader, parse=parse)(input_ref)

    return replay
