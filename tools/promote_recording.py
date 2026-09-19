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


#: ★ `DX-132` — where the INGESTED sector files live. A SECTOR recording's bundle is
#: the competitors' documents, not the subject's filing, so `_ticker_of` scores it
#: `{'MU': 0, 'AMD': 0}` and refuses. The refusal is right (`P5`); the gap was that
#: there was no second thing to try.
#:
#: ⚠⚠ Note WHICH file this is. `config/sector/*.yaml` is the reviewed SOURCE LIST;
#: what actually travels in the bundle is the ingested sector file that
#: `tools/ingest_sector_file.py` writes here. ★ And `.state/` is gitignored — so,
#: exactly as with the recordings themselves (`DX-12`), the ingested file must be
#: COPIED into the fixture or the promoted recording resolves on one laptop only.
SECTORS = REPO / ".state/sector"


def _probe_hits(text: str, joined: str) -> int:
    """★ How much of `text` appears in the recorded bundle — the same many-short-
    probes method `_ticker_of` uses, and for the same reason (`DX-35`: the bundle
    is not a verbatim substring of any source, because page furniture is stripped).
    """
    probes = [text[i:i + 200]
              for i in range(0, max(len(text) - 200, 1), max(len(text) // 40, 1))]
    return sum(1 for pr in probes if pr.strip() and pr in joined)


def sector_text(sector_file_json: pathlib.Path) -> str:
    """The sector file rendered exactly as the bundle carries it (`RA-99` order).

    ★★ ONE renderer, used by BOTH the promoter and `golden_replay`, so a quote can
    never be verified against a different arrangement of the same records than the
    one that was sent. ⚠ Two renderers here would be `DX-70`'s defect with extra
    steps: the mismatch would present as *"the quote is not in the bundle"*.
    """
    from tools.run_extraction_once import sector_bundle
    return "\n".join(p.content for p in sector_bundle(sector_file_json, ticker="MU").parts)


def _sector_of(bundles: list[str]) -> tuple[pathlib.Path, int] | None:
    """★★ `DX-132` — was this recorded against a SECTOR file, and which one?

    Returns `(ingested_file, hits)` for a decisive match, or `None` when no sector
    file is in the bundle. ⚠ Same `P5` discipline as `_ticker_of`: a close call
    between two sector files refuses rather than picking one.
    """
    if not SECTORS.is_dir():
        return None
    joined = "\n".join(bundles)
    scores = {}
    for p in sorted(SECTORS.glob("*.json")):
        try:
            scores[p] = _probe_hits(sector_text(p), joined)
        except Exception:
            continue          # ⚠ an unreadable candidate is not a match, not a crash
    if not scores:
        return None
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    (best, hi), (_, lo) = ranked[0], (ranked[1] if len(ranked) > 1 else (None, 0))
    if hi < 8 or hi < 3 * max(lo, 1):
        return None
    return best, hi


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


#: ★★ `DX-133` — a call that hit the output cap is NOT an answer, and promoting
#: one poisons the whole recording: `test_every_recorded_quote_still_resolves_in_
#: its_filing` JSON-parses every payload, and a 0-char body fails it outright.
#:
#: ⚠⚠ **Detect it by the FIELD, never by parseability.** `run-2026-09-15T025134`'s
#: truncated `J-13` is the two characters `{}` — which parses perfectly, passes a
#: shape check, and means nothing. *"It parsed"* is not *"it is an answer."*
TRUNCATED = "max_tokens"


def _is_truncated(payload: dict) -> bool:
    resp = payload.get("response")
    return isinstance(resp, dict) and resp.get("stop_reason") == TRUNCATED


def _write_exclusions(out: pathlib.Path, excluded: list[dict]) -> None:
    """★ `DX-133` — a promoted subset must SAY it is a subset.

    ⚠ An omission nobody wrote down is indistinguishable from a call that never
    happened. `excluded.json` is what makes this a declared curation rather than a
    quiet one, and it is why leaving a truncated call out is not editing the record.
    """
    target = out / "excluded.json"
    if not excluded:
        target.unlink(missing_ok=True)
        return
    target.write_text(json.dumps(
        {"note": ("calls present in .state/runs/ and deliberately NOT promoted — "
                  "the full run is unchanged there (DX-133)"),
         "excluded": excluded}, indent=2), encoding="utf-8")
    print(f"  ✅ excluded.json — {len(excluded)} call(s) named as left out")


def promote(run_id: str, *, skip_truncated: bool = False) -> int:
    """Copy a recording into the version-controlled fixtures.

    ★★ `DX-133` — promotion's unit WAS the whole run, so one truncated call made
    every complete call beside it unusable: `J-11`, `J-12` and `J-13` each had a
    clean, paid-for recording blocked by a truncated sibling. With
    `--skip-truncated` the incomplete calls are LEFT OUT and **named in
    `excluded.json`**, so the fixture is a declared subset rather than a quiet one.

    ⚠ This is not editing the record. The full run stays in `.state/runs/`
    untouched; what changes is which calls the golden set may address, and that
    choice is written down beside them.
    """
    src = SRC / run_id
    if not src.exists():
        print(f"  ⛔ no recording at {src.relative_to(REPO)}")
        return 1

    out = DST / run_id
    bundles: list[str] = []
    excluded: list[dict] = []
    (out / "trace/payloads").mkdir(parents=True, exist_ok=True)
    (out / "trace.jsonl").write_text((src / "trace.jsonl").read_text(encoding="utf-8"),
                                     encoding="utf-8")

    for pf in sorted((src / "trace/payloads").glob("*.json")):
        payload = json.loads(pf.read_text(encoding="utf-8"))
        if _is_truncated(payload):
            body_len = len((payload.get("response") or {}).get("text") or "")
            if not skip_truncated:
                print(f"  ⛔ {pf.name} — stop_reason={TRUNCATED}, {body_len} chars. "
                      "A truncated call is not an answer; re-run --skip-truncated "
                      "to promote the complete calls beside it (DX-133).")
                return 1
            excluded.append({"call": pf.stem, "reason": f"stop_reason={TRUNCATED}",
                             "chars": body_len})
            print(f"  ⏭ {pf.name} — EXCLUDED ({body_len} chars, {TRUNCATED})")
            continue
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
    # ★★ `DX-132` — TWO bundle shapes, tried in order. A subject filing is the
    #   common case; a sector file is what `E-13` is recorded against, and before
    #   this branch existed the industry block could never be promoted and so
    #   could never be graded at all.
    try:
        ticker = _ticker_of(bundles)
    except AmbiguousFiling:
        found = _sector_of(bundles)
        if found is None:
            raise            # ⚠ neither shape matched — promote nothing (P5)
        ingested, hits = found
        doc = json.loads(ingested.read_text(encoding="utf-8"))
        # ⚠⚠ COPY the sector file in, do not reference `.state/`. It is gitignored,
        #   so a reference would make this recording resolve on one laptop and fail
        #   everywhere else — `DX-12`'s shape, which is the whole reason the
        #   recordings themselves were moved under version control.
        (out / "sector_file.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
        (out / "sector.json").write_text(json.dumps(
            {"kind": "sector", "sector_file": "sector_file.json",
             "industry": doc["industry"], "file_version": int(doc["file_version"]),
             # ⚠ Pinned so a re-ingest that changes any record is VISIBLE here
             #   rather than silently re-pointing this recording at new text.
             "source_list_version": doc.get("source_list_version", ""),
             "as_of": doc.get("as_of", ""), "records": len(doc.get("records", ())),
             "ingested_from": str(ingested.relative_to(REPO)),
             "probe_hits": hits}, indent=2), encoding="utf-8")
        print(f"  ✅ sector.json → {doc['industry']} v{doc['file_version']}  "
              f"({len(doc.get('records', ()))} records, {hits} probe hits)")
        print("  ✅ sector_file.json — the ingested file COPIED in "
              "(.state/ is gitignored; a reference would not survive a clone)")
        _write_exclusions(out, excluded)
        print(f"  ✅ {out.relative_to(REPO)}")
        print("  ⚠ Review it before committing: it is a real model response and it "
              "is about to become public repo history.")
        return 0

    from tools.run_extraction_once import FILINGS
    (out / "filing.json").write_text(json.dumps(
        {"ticker": ticker, "fixture": FILINGS[ticker]["path"]}, indent=2),
        encoding="utf-8")
    print(f"  ✅ filing.json → {ticker}  (matched against the recorded bundle)")

    _write_exclusions(out, excluded)
    print(f"  ✅ {out.relative_to(REPO)}")
    print("  ⚠ Review it before committing: it is a real model response and it "
          "is about to become public repo history.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) != 1 or flags - {"--skip-truncated"}:
        print("usage: promote_recording.py <run_id> [--skip-truncated]")
        raise SystemExit(2)
    raise SystemExit(promote(args[0], skip_truncated="--skip-truncated" in flags))
