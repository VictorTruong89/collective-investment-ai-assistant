"""F13 `D13` — the nominee's thesis, as the daily card reads it (AC-F13.15).

★ The daily run still WRITES no thesis (Victor 2026-10-05, DX-153). It READS the newest one
`thesis_for` completed, through the chain manifests (`CT-F13.1`), and nothing else.

Three outcomes, each a statement the card can print:
  · **found** — the newest COMPLETED thesis with thesis `as_of` ≤ the run's (`INV-1`);
    stale after `STALE_DAYS` (`D9`), falsifier-fired when its recorded check counted one;
  · **no peer set** — the ticker is not a `thesis_for` subject (`D2`, `T2`);
  · **not yet written** — it is, and no completed thesis exists; the command is named.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from datetime import date

from src.fundamental.on_demand.inputs import STALE_DAYS

FOUND, NO_PEER_SET, NOT_WRITTEN = "found", "no_peer_set", "not_written"


@dataclass(frozen=True)
class CardThesis:
    status: str
    reason: str
    thesis: object = None
    run_id: str | None = None
    stale: bool = False
    falsifier_fired: bool = False
    ref: dict | None = None


def thesis_ref(thesis, run_id: str, *, transport: str, stale: bool = False,
               fired: int = 0) -> dict:
    """DN-42 — what D-12 carries and D-09 shows. ★ Copied from the thesis, never computed."""
    falsifier = " ".join(f"{f.ordinal}) {f.condition} [{f.observable_field}, by {f.deadline}]"
                         for f in thesis.falsifiers)
    return {"run_id": run_id, "as_of": thesis.as_of.isoformat(), "verdict": thesis.verdict,
            "conviction": thesis.conviction, "falsifier": falsifier,
            "stale": stale, "falsifiers_fired": fired,
            "provenance": {"variant": transport, "authored_by": "tools/thesis_for.py",
                           "bundle_hash": thesis.bundle_hash}}


def thesis_for_card(ticker: str, as_of: date, *, root, runs_root, config: dict) -> CardThesis:
    """The card's thesis for `ticker` at `as_of` — found, no peer set, or not yet written."""
    from src.fundamental.thesis.models import Thesis

    ticker = ticker.upper()
    if ticker not in (config.get("subjects") or {}):
        return CardThesis(NO_PEER_SET, (
            f"no thesis — no peer set: {ticker}'s industry has no source list, and "
            f"thesis_for writes theses only for an industry Victor has given a peer set "
            f"(F13 D2, D13)"))
    candidates = []
    for chain in pathlib.Path(root).glob(f"{ticker}_*/chain.json"):
        doc = json.loads(chain.read_text(encoding="utf-8"))
        written = date.fromisoformat(doc["as_of"])
        done = any(s.get("step") == "thesis" and s.get("status") == "done"
                   for s in doc.get("steps") or ())
        if doc.get("thesis_run_id") and done and written <= as_of:             # INV-1
            candidates.append((written, doc))
    if not candidates:
        return CardThesis(NOT_WRITTEN, (
            f"no thesis — not yet written: none completed for {ticker} on or before "
            f"{as_of}; write one with `python tools/thesis_for.py {ticker} --as-of {as_of}`"))
    written, doc = max(candidates, key=lambda c: c[0])
    run_id = doc["thesis_run_id"]
    summary = json.loads((pathlib.Path(runs_root) / run_id / "thesis.json")
                         .read_text(encoding="utf-8"))
    thesis = Thesis.from_json_obj(summary["thesis"])
    fired = int(((doc.get("checks") or {}).get("falsifiers") or {}).get("FIRED", 0))
    stale = (as_of - written).days > STALE_DAYS
    return CardThesis(
        FOUND, f"thesis {run_id} as of {written}" + (" — STALE (D9)" if stale else ""),
        thesis=thesis, run_id=run_id, stale=stale, falsifier_fired=fired > 0,
        ref=thesis_ref(thesis, run_id, transport=doc.get("transport", "unknown"),
                       stale=stale, fired=fired))
