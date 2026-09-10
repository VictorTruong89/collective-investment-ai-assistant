#!/usr/bin/env python3
"""Promote an `F2` run recording into a version-controlled golden fixture.

    python3 tools/promote_recording.py <run_id>

⚠⚠ **Why this exists.** `F5`'s golden cases grade a recorded call, and the
recording lived under `.state/runs/` — which `.gitignore:32` excludes. So the
golden regression **ran only on the machine that made the call**; on a fresh
clone or in CI its three replay tests skipped, silently.

★★ That is `DX-12` exactly — *"41 external-truth tests that skip everywhere and
tell nobody"* — and it was reintroduced in the very file that carries a comment
warning about it. **A measurement that exists on one laptop is not a
measurement.**

**What is copied, and what is not.** The `response` is copied verbatim: it is
the evidence. ⚠ The request's `payload` — the whole 209 KB filing — is
**elided**, because the filing is already in the repo and a second copy is a
second thing to keep in step. `filing.json` records WHICH filing, so the
recording is never unmoored.

⚠⚠ **`DX-36` — this docstring used to lie.** It claimed the payload was
*"replaced by its `bundle_hash`"* and that on a re-render the recording would
*"disagree **loudly**"*. No hash was ever written here, and nothing in the repo
compared one: the drift detector existed only in this paragraph.

★★★ It is also not the guard to want. A hash fires on ANY byte change, so
`DX-35`'s furniture strip — measured to break none of the 95 recorded quotes —
would have demanded ~$1.20 of re-recording to buy nothing. The real question is
not whether the bytes moved but whether the recording still MEANS what it
meant. `test_every_recorded_quote_still_resolves_in_its_filing` asks that one,
and it is a real test rather than a sentence.
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
# ⚠ Runs as a script, so `tools` is not importable without this.
sys.path.insert(0, str(REPO))
SRC = REPO / ".state/runs"
DST = REPO / "tests_src/fixtures/recordings"


def promote(run_id: str) -> int:
    src = SRC / run_id
    if not src.exists():
        print(f"  ⛔ no recording at {src.relative_to(REPO)}")
        return 1

    out = DST / run_id
    (out / "trace/payloads").mkdir(parents=True, exist_ok=True)
    (out / "trace.jsonl").write_text((src / "trace.jsonl").read_text(encoding="utf-8"),
                                     encoding="utf-8")

    for pf in sorted((src / "trace/payloads").glob("*.json")):
        payload = json.loads(pf.read_text(encoding="utf-8"))
        request = payload.get("request") or {}
        body = str(request.get("payload", ""))
        if len(body) > 4096:
            # ⚠ Replaced, not dropped: a reader must be able to tell WHICH
            # document this was recorded against, or the recording is unmoored.
            request["payload"] = {
                "__elided__": "the bundle is the filing fixture, not duplicated here",
                "chars": len(body),
                "see": "tests_src/fixtures/filings/",
            }
            payload["request"] = request
        (out / "trace/payloads" / pf.name).write_text(
            json.dumps(payload, indent=2), encoding="utf-8")
        print(f"  ✅ {pf.name} — response kept verbatim, {len(body):,}-char bundle elided")

    # ⚠⚠ A recording must say WHICH filing it was made against. The golden set
    # now spans two filings, and `golden_replay` was resolving every case
    # against ONE bundle — so AMD's cases were being checked against MU's text
    # and every quote "was not in the bundle". ★ The recording knows; nothing
    # else reliably does.
    from tools.run_extraction_once import FILINGS, TICKER
    (out / "filing.json").write_text(json.dumps(
        {"ticker": TICKER, "fixture": FILINGS[TICKER]["path"]}, indent=2),
        encoding="utf-8")
    print(f"  ✅ filing.json → {TICKER}")

    print(f"  ✅ {out.relative_to(REPO)}")
    print("  ⚠ Review it before committing: it is a real model response and it "
          "is about to become public repo history.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.splitlines()[2].strip())
        raise SystemExit(2)
    raise SystemExit(promote(sys.argv[1]))
