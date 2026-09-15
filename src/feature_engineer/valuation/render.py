"""`CT-F10.4` / `T4` — a valuation as an evidence-bundle part (`AC-F10.15`).

★ **Returns the part's `kind`, `pins` and `content`, not a `BundlePart`.** The
bundle type lives in D-01, and `AC-F10.14` forbids this module importing it; the
bundle builder wraps the three fields. The KIND is what matters: `computed` is
the kind the blind view already withholds (`BLIND_WITHHELD_KINDS`, `RA-14`), so
Stage A — including the normalised-earnings judgement (`D1`) — never sees a
price, a value or a band it could anchor to.

⚠ Only `fv_model` renders (`require_fv_model`): an `AnalystValuation` is a
conclusion and does not travel as neutral evidence (`VS-1`, `VS-3`).
"""

from __future__ import annotations

import json

from src.feature_engineer.valuation.types import require_fv_model

KIND = "computed"


def as_bundle_part(result) -> dict:
    result = require_fv_model(result)
    a = result.assumptions_obj
    obj = json.loads(result.to_json())
    lines = [
        f"D-02 VALUATION TRAIL — fv_model (judgement-free), {obj['ticker']} as of {obj['as_of']}",
        f"assumptions: {a.name}@v{a.version} {a.content_hash}",
        "Every figure below is labelled; recompute any of them from the others.",
        "",
        json.dumps(obj, indent=1, sort_keys=True),
    ]
    return {"kind": KIND,
            "pins": {"contract_name": f"valuation.{a.name}", "contract_version": a.version},
            "content": "\n".join(lines)}
