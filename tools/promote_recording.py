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


class AmbiguousFiling(Exception):
    """⚠ The recorded bundle matches no filing fixture, or more than one."""


def _ticker_of(bundles: list[str]) -> str:
    """★★ `DX-70` — which filing was this recorded against? **Ask the bundle.**

    ⚠⚠ This used to read `run_extraction_once.TICKER`, which is a **module
    default** (`"MU"`). `--ticker AMD` sets it by calling `_select()` inside
    *that* process; the promoter runs in a fresh one, where the assignment never
    happened. ⇒ **Every promotion wrote `MU`, whatever it was promoting.**

    ★ It went unnoticed because MU is the default and most runs are MU, so the
    answer was accidentally right nearly every time — the shape that makes a
    guess survive: *it is a guess that is usually correct.*

    ⚠⚠ And the damage lands one layer away, silently: `golden_replay` reads
    `filing.json` to choose the text a quote is resolved against, so a wrong
    ticker checks AMD's quotes against MU's filing — which is the exact defect
    the comment above this function was written to close, reintroduced through
    the field that comment added.

    ★ The fix takes the answer from **evidence rather than convention**: the
    recorded request still carries the whole bundle, so the filing it was built
    from is *in the recording*. `P5` — exactly one fixture must match.
    """
    from tools.run_extraction_once import FILINGS
    joined = "\n".join(bundles)
    scores = {}
    for ticker, meta in FILINGS.items():
        text = (REPO / meta["path"]).read_text(encoding="utf-8")
        # ⚠⚠ MANY SHORT probes, not one long one. A single 2,000-char slice
        # failed on MU and passed on AMD, which looked like a filing-specific
        # quirk and is not: `DX-35`'s `strip_page_furniture()` removes lines
        # from the bundle, so the bundle is **not a verbatim substring** of the
        # fixture. Any window wide enough to be distinctive is wide enough to
        # straddle a stripped line. ★ Short probes spread across the document
        # survive that — some land on furniture and fail, and the rest still
        # carry the signal.
        probes = [text[i:i + 200]
                  for i in range(0, max(len(text) - 200, 1), max(len(text) // 40, 1))]
        scores[ticker] = sum(1 for pr in probes if pr.strip() and pr in joined)
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    (best, hi), (_, lo) = ranked[0], (ranked[1] if len(ranked) > 1 else ("", 0))
    # ★ Two different companies' 10-Qs share boilerplate but not content, so a
    # real match is decisive. ⚠ `P5` — refuse a close call rather than break
    # the tie by preference.
    if hi < 8 or hi < 3 * max(lo, 1):
        raise AmbiguousFiling(
            f"the recorded bundle does not decisively match any filing fixture "
            f"(probe hits: {scores}) — a recording that cannot name its own "
            f"filing is unmoored, and `golden_replay` would resolve its quotes "
            f"against the wrong text (DX-70). ⚠ Promote nothing rather than guess."
        )
    return best


def promote(run_id: str) -> int:
    src = SRC / run_id
    if not src.exists():
        print(f"  ⛔ no recording at {src.relative_to(REPO)}")
        return 1

    out = DST / run_id
    bundles: list[str] = []
    (out / "trace/payloads").mkdir(parents=True, exist_ok=True)
    (out / "trace.jsonl").write_text((src / "trace.jsonl").read_text(encoding="utf-8"),
                                     encoding="utf-8")

    for pf in sorted((src / "trace/payloads").glob("*.json")):
        payload = json.loads(pf.read_text(encoding="utf-8"))
        request = payload.get("request") or {}
        body = str(request.get("payload", ""))
        if len(body) > 4096:
            bundles.append(body)
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
    ticker = _ticker_of(bundles)
    from tools.run_extraction_once import FILINGS
    (out / "filing.json").write_text(json.dumps(
        {"ticker": ticker, "fixture": FILINGS[ticker]["path"]}, indent=2),
        encoding="utf-8")
    print(f"  ✅ filing.json → {ticker}  (matched against the recorded bundle)")

    print(f"  ✅ {out.relative_to(REPO)}")
    print("  ⚠ Review it before committing: it is a real model response and it "
          "is about to become public repo history.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.splitlines()[2].strip())
        raise SystemExit(2)
    raise SystemExit(promote(sys.argv[1]))
