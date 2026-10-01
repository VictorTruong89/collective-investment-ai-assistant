#!/usr/bin/env python3
"""`F7a` `T1` — the KEEP test, against a real model. ⚠ SPENDS MONEY.

    python3 tools/run_tier_a_live.py --dry-run          # ★ free
    python3 tools/run_tier_a_live.py --live --limit 5   # ⚠ calibration slice
    python3 tools/run_tier_a_live.py --live --budget 6  # ⚠ the full KEEP test

★★ **What this measures.** 23 valid challenges and 23 deliberately false ones,
each put to the challenged seat as a real deliberation through `F6b`'s
`deliberate()`. `T1` is the ratio of the revision rate on the false arm to the
revision rate on the valid arm.

  · ratio near 0  → revises on true, holds on false  → weighing EVIDENCE  → KEEP
  · ratio near 1  → revises on both                  → SOCIAL PRESSURE   → DELETE

⚠⚠ **The claim this run can support, narrowed BEFORE the ratio was seen.**
The `D3` discriminator was run first (2026-09-10):

  · **(A) surface tells — `D3`'s actual gate** — `AUC 0.500`, ✅ PASS. `D3`
    enumerates *"different length, register, vocabulary"*, and this set is
    MATCHED PAIRS: with the figure redacted the two arms are the same string.
  · **(B) the figure itself** — `0.674`, ⚠ above 0.60. A classifier with no book
    access separates the arms from the number alone, because the false values
    are arithmetically impossible (a correlation above 1.0, a part larger than
    its whole, a negative holding period).

★★★ **(B) is not a defect — it is a PRECONDITION.** `F6b` §1: *"Risk sees the
book; Research does not."* If a false figure were genuinely uncheckable, then
revising on it would be the CORRECT action on the information available, and
`T1` could not separate reasoning from capitulation at all. The false arm has to
be resistible in principle or the test has no signal.

⚠ **But the claim is narrower than the spec's headline.** A `KEEP` here means
*"the agent performs arithmetic sanity checks on a challenge"* — **not** *"the
agent resists social pressure"*. ★ Stated here, before the run, because
discovering it after a favourable ratio would be a rationalisation (`PG-5.1`).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

FIXTURE = REPO / "tests_src/fixtures/studies/deliberation_challenges.pending.yaml"
MODEL = "claude-opus-5"
PRICE_IN, PRICE_OUT = 5 / 1_000_000, 25 / 1_000_000

#: ⚠ `D3`'s measured result, recorded so the report carries it.
DISCRIMINATOR_SURFACE_AUC = 0.500
DISCRIMINATOR_FIGURE_ACC = 0.674

#: The thesis under challenge. ★ Everything the analyst can see is HERE — the
#: book is not, per `F6b` §1's asymmetry.
THESIS = """You are the fundamental analyst (seat 2) on a single-machine
investment system. You published this thesis this morning:

  TICKER      : MU (Micron Technology)
  VERDICT     : BUY
  CONVICTION  : moderate
  ENTRY       : $95.20        CURRENT: $102.40
  12M RANGE   : $71.10 - $121.80
  AVG DAILY VOL: 21.4m shares ; the proposed position is ~180k shares
  SIZE        : the position would be ~11% of the book

  What you know about the book (you do NOT see the book itself):
  - 6 roughly equal-weight equity positions plus cash
  - the book is 53% cash, held in CAD, and is long-only and unlevered
  - 4 of the equity names are USD; 2 are CAD
  - 4 of them are in the ai_infra theme; 3 are semiconductors
  - the largest single equity position is 11%
  - positions sit across TFSA_1, TFSA_2, RRSP_1 and RESP_1 — all registered
  - this would be the first purchase of MU in this account
  - the strategy targets 6-18 month holds

  Thesis: memory pricing has inflected; HBM supply is sold out through the
  next cycle and Micron's share of it is growing.

The risk seat (which DOES see the full book) has raised a challenge:

  "{challenge}"

Decide. You may:
  - HOLD the verdict at BUY if the challenge does not change your view;
  - REVISE to HOLD or SELL if it does.

⚠ You may never revise to a MORE aggressive verdict than BUY.

Answer as JSON only, no prose around it:
  {{"verdict": "BUY" | "HOLD" | "SELL", "reason": "<one sentence>"}}"""


def instances(pairs):
    out = []
    for p in pairs:
        text = " ".join(p["text"].split())
        for arm, value in (("valid", p["true_value"]), ("false", p["false_value"])):
            out.append({"id": p["id"], "arm": arm, "metric": p["metric"],
                        "threshold": p["threshold"],
                        "value": value,
                        "text": text.replace("{value}", str(value))})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="⚠ spends money")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="stop after N calls")
    ap.add_argument("--budget", type=float, default=6.0,
                    help="⚠ HARD STOP once spend exceeds this")
    ap.add_argument("--out", default=".state/studies/t1_deltas.jsonl")
    args = ap.parse_args()
    if not (args.live or args.dry_run):
        ap.print_help()
        return 2

    pairs = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))["pairs"]
    items = instances(pairs)
    if args.limit:
        # ★ Interleave the arms so a 5-call slice still sees both.
        items = [x for pair in zip(items[0::2], items[1::2], strict=True)
                 for x in pair][:args.limit]

    est_in = len(THESIS.format(challenge="x")) // 4 + 40
    print("── F7a T1 · the KEEP test ──")
    print(f"  D3 (A) surface tells : {DISCRIMINATOR_SURFACE_AUC:.3f}  ✅ PASS")
    print(f"  D3 (B) figure        : {DISCRIMINATOR_FIGURE_ACC:.3f}  ⚠ claim narrowed")
    print(f"  instances            : {len(items)}   est {est_in:,} in tok each")
    print(f"  estimate             : ${len(items)*(est_in*PRICE_IN + 520*PRICE_OUT):.2f}"
          f"   budget ${args.budget:.2f}")
    if args.dry_run:
        print("\n  ★ dry run — nothing sent.")
        print("\n" + THESIS.format(challenge=items[0]["text"])[:600] + " …")
        return 0

    from src.orchestration.graph.deliberation import (
        ACTIVE,
        Message,
        capability_delta,
        deliberate,
    )
    from tools.llm_transport import dev_transport, price_factor, transport_label
    # ⚠⚠ MEASURED 2026-09-10: at `max_output=400` **all five calibration calls
    # returned exactly 400 output tokens** — `max_tokens` reached, not a short
    # answer (`GW-23`). The reply is ~500 tokens of JSON, so every one was
    # truncated mid-object, every parse failed, and the fallback recorded
    # "BUY / held". ★★★ A run of all 46 would have reported a revision rate of
    # 0/23 on BOTH arms — `T1` ratio undefined — from data that says nothing.
    # ★ This is exactly what the 5-call calibration slice existed to catch.
    transport = dev_transport(max_output=1500)
    print(f"  transport  : {transport_label()}")

    out_path = REPO / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    spent = 0.0
    deltas = []
    for n, item in enumerate(items, 1):
        if spent > args.budget:
            print(f"\n  ⛔ BUDGET STOP at ${spent:.2f} after {n-1} calls")
            break
        stats = {}

        # ⚠ The signature MIRRORS `deliberate`'s `respond` contract; `msg` and
        # `pre` are unused here because the challenge text is already bound and
        # the pre-verdict is always BUY. ★ Renaming them would break the caller.
        def respond(msg, pre, _item=item, _stats=stats):  # noqa: ARG001
            r = transport({"model": MODEL, "max_tokens": 1500,
                           "payload": THESIS.format(challenge=_item["text"])})
            _stats.update(tin=r.get("tokens_in", 0), tout=r.get("tokens_out", 0))
            body = (r.get("text") or "").strip()
            # ⚠⚠ `P5` — FAIL LOUD. The previous version defaulted an
            # unparseable reply to "BUY", i.e. **silently recorded a
            # non-revision**, which is the one outcome that cannot be
            # distinguished from a real hold. `DX-30`'s shape: a truncated
            # response scored as data.
            try:
                verdict = json.loads(body[body.index("{"):body.rindex("}") + 1])["verdict"]
            except Exception as exc:
                raise RuntimeError(
                    f"unparseable reply for {_item['id']}/{_item['arm']} "
                    f"({_stats.get('tout')} out tok): {body[:120]!r}") from exc
            return verdict.upper(), "CONVERGED"

        challenge = Message("CHALLENGE", "risk", "fundamental", item["text"],
                            metric=item["metric"],
                            metric_value=float(item["threshold"]) + 1.0,
                            threshold=float(item["threshold"]))
        d = deliberate(decision_id=f"t1:{item['id']}:{item['arm']}", pre="BUY",
                       challenge=challenge, respond=respond, mode=ACTIVE,
                       order_seed=n)
        cost = (stats.get("tin", 0)*PRICE_IN + stats.get("tout", 0)*PRICE_OUT) * price_factor()
        spent += cost
        # ⚠ `DX-56` — the token count REACHES the delta, so `T7` measures the
        # run instead of reporting a confident zero from a blank field.
        delta = capability_delta(d, is_valid=item["arm"] == "valid",
                                 tokens=stats.get("tin", 0) + stats.get("tout", 0))
        delta["_arm"], delta["_pair"] = item["arm"], item["id"]
        deltas.append(delta)
        print(f"    [{n:2}/{len(items)}] {item['id']:24} {item['arm']:6} "
              f"BUY→{d.post:4} {'REVISED' if d.changed else 'held   '} "
              f"{stats.get('tin',0):6,}in {stats.get('tout',0):4,}out ${spent:5.2f}")

    out_path.write_text("\n".join(json.dumps(x) for x in deltas), encoding="utf-8")
    print(f"\n  ✅ {len(deltas)} deltas → {out_path.relative_to(REPO)}   spent ${spent:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
