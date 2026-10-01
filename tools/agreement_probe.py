#!/usr/bin/env python3
"""Did a prompt change MOVE an answer, or is it noise? — `L3` §2.1p item 4.

    # does J-15 v2 answer differently from v1 on the same recorded call?
    python3 tools/agreement_probe.py <payload.json> --block J-15 --from v1 --to v2 --k 3 --live
    # how much does one prompt disagree with ITSELF? (the noise floor)
    python3 tools/agreement_probe.py <payload.json> --block J-16 --noise-floor --k 3 --live

`L8` §9 rule 4ⓑ (2026-10-01): judgement is measured by rule checks and by
agreement across runs, not by golden cases. ★ One re-run after a prompt edit
cannot separate a moved answer from a different draw: two runs of one prompt 82
minutes apart differed in whether a field existed (`DX-74`).

**What it does.** Re-sends ONE recorded call k times per arm. Arm A is the prompt
as recorded (the recorded answer counts as one of its k); arm B swaps the block's
old text for its new text, exactly once, and changes NOTHING else: same bundle,
model, effort and max_tokens. It then compares the DECISION fields only (enums,
booleans, numbers, and list lengths), never prose.

★★ **The rule, fixed before any run** (PG-5.1: a threshold chosen after seeing the
data is a rationalisation):

| Result | When |
|---|---|
| `SAME` | both arms' modal answer is the same |
| `MOVED` | ★ each arm is UNANIMOUS and the two differ, the only result k=3 can call a move |
| `UNCLEAR` | anything else, including an arm with fewer than k usable answers |

Single arm (`--noise-floor`): `STABLE` (unanimous) · `SPLIT` · `UNCLEAR` (< k usable).

⚠ **Sampling, not perturbation.** `RA-61` prefers perturbing the input for RM-1's
stability question; this probe answers a different question (*did the prompt
change move it?*), for which the arms must differ ONLY in the prompt.
⚠ **Scope:** Stage B–D blocks (`J-09`…`J-17`), whose answer schema is rebuilt by
`thesis_tool`. A Stage-A block's schema depends on the criteria it was offered.
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys
from collections import Counter
from collections.abc import Callable
from datetime import datetime

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SAME, MOVED, UNCLEAR, STABLE, SPLIT = "SAME", "MOVED", "UNCLEAR", "STABLE", "SPLIT"
#: RM-1's floor: fewer usable runs than this cannot show agreement.
K_MIN = 3


# ── the decision fields ─────────────────────────────────────────────────────

def decision_fields(schema: dict, answer, prefix: str = "") -> dict:
    """Every CLOSED answer in `answer`, keyed by its path in `schema`.

    Enums, booleans and numbers are decisions; free strings are prose and are skipped.
    An array of objects contributes each closed sub-field as a SORTED tuple (its order
    is presentation) plus its length as `name[]#`; an array of scalars keeps its order.
    """
    out: dict = {}
    if not isinstance(answer, dict):
        return out
    for name, sub in (schema.get("properties") or {}).items():
        if name not in answer:
            continue
        path, value = f"{prefix}{name}", answer[name]
        kinds = sub.get("type")
        kinds = kinds if isinstance(kinds, list) else [kinds]
        if "enum" in sub or {"boolean", "integer", "number"} & set(kinds):
            out[path] = value
        elif "object" in kinds:
            out.update(decision_fields(sub, value, f"{path}."))
        elif "array" in kinds and isinstance(value, list):
            items = sub.get("items") or {}
            item_kinds = items.get("type")
            if items.get("properties"):
                rows = [decision_fields(items, v) for v in value]
                for key in sorted({k for r in rows for k in r}):
                    out[f"{path}[].{key}"] = tuple(sorted((r.get(key) for r in rows), key=repr))
                out[f"{path}[]#"] = len(value)
            elif "enum" in items or item_kinds in ("boolean", "integer", "number"):
                out[path] = tuple(value)
    return out


def _modal(values: list):
    if not values:
        return None, 0.0
    counts = Counter(values).most_common()
    if len(counts) > 1 and counts[0][1] == counts[1][1]:
        return None, counts[0][1] / len(values)            # a tie has no modal answer
    return counts[0][0], counts[0][1] / len(values)


def _distribution(values: list) -> dict:
    return dict(sorted(Counter(str(v) for v in values).items()))


def compare(a: list, b: list | None = None) -> dict:
    """The pre-registered rule (module docstring), applied to one field."""
    modal_a, agree_a = _modal(a)
    if b is None:
        result = (UNCLEAR if len(a) < K_MIN else STABLE if agree_a == 1.0 else SPLIT)
        return {"result": result, "agreement": (agree_a,), "modal": (modal_a,),
                "distribution": [_distribution(a)]}
    modal_b, agree_b = _modal(b)
    if len(a) < K_MIN or len(b) < K_MIN or modal_a is None or modal_b is None:
        result = UNCLEAR
    elif modal_a == modal_b:
        result = SAME
    elif agree_a == 1.0 and agree_b == 1.0:
        result = MOVED
    else:
        result = UNCLEAR
    return {"result": result, "agreement": (agree_a, agree_b), "modal": (modal_a, modal_b),
            "distribution": [_distribution(a), _distribution(b)]}


# ── the probe ───────────────────────────────────────────────────────────────

def _answer_of(response: dict | None):
    if not response or (response.get("stop_reason") or "").lower() == "max_tokens":
        return None
    text = response.get("text") or ""
    try:
        return json.loads(text[text.index("{"):text.rindex("}") + 1])
    except ValueError:
        return None


def probe(recorded: pathlib.Path, *, old_text: str, new_text: str | None, schema: dict,
          k: int = 3, transport: Callable | dict) -> dict:
    """Run the arms and apply the rule. `transport` may be one callable or `{"A":…, "B":…}`
    (J-15's two versions answer through different schemas)."""
    if k < K_MIN:
        raise ValueError(f"k={k} is below {K_MIN}: fewer runs cannot show agreement (RM-1)")
    record = json.loads(pathlib.Path(recorded).read_text(encoding="utf-8"))
    request = record["request"]
    if str(request.get("payload", "")).count(old_text) != 1:
        raise ValueError("the block's old text must appear in the recorded payload exactly once "
                         "— otherwise the arms would not differ only in the prompt")
    send = transport if isinstance(transport, dict) else {"A": transport, "B": transport}

    arms: dict = {"A": {"answers": [], "calls": 0, "failed": 0}}
    recorded_answer = _answer_of(record.get("response"))
    if recorded_answer is not None:
        arms["A"]["answers"].append(recorded_answer)        # ★ the recording is one of k
    plan = [("A", request, k - len(arms["A"]["answers"]))]
    if new_text is not None:
        arms["B"] = {"answers": [], "calls": 0, "failed": 0}
        swapped = copy.deepcopy(request)
        swapped["payload"] = request["payload"].replace(old_text, new_text)
        plan.append(("B", swapped, k))
    for arm, req, n in plan:
        for _ in range(n):
            arms[arm]["calls"] += 1
            try:
                answer = _answer_of(send[arm](copy.deepcopy(req)))
            except Exception as exc:                          # noqa: BLE001 — reported, not hidden
                answer = None
                arms[arm].setdefault("errors", []).append(f"{type(exc).__name__}: {exc}"[:200])
            if answer is None:
                arms[arm]["failed"] += 1
            else:
                arms[arm]["answers"].append(answer)

    per_arm = {arm: [decision_fields(schema, a) for a in v["answers"]] for arm, v in arms.items()}
    paths = sorted({p for rows in per_arm.values() for row in rows for p in row})
    fields = {}
    for path in paths:
        a = [row[path] for row in per_arm["A"] if path in row]
        b = [row[path] for row in per_arm["B"] if path in row] if "B" in per_arm else None
        fields[path] = compare(a, b)
    for v in arms.values():
        v["usable"] = len(v.pop("answers"))
    return {"recorded": str(recorded), "k": k, "arms": arms, "fields": fields,
            "rule": "SAME = modal answers agree; MOVED = both arms unanimous and different; "
                    "else UNCLEAR (incl. < k usable). Single arm: STABLE / SPLIT / UNCLEAR."}


# ── the command line ────────────────────────────────────────────────────────

def _block_text(block_id: str, version: str) -> str:
    import src.fundamental.prompts.e_blocks as eb
    factory = getattr(eb, f"{block_id.lower().replace('-', '')}_{version}", None)
    if factory is None:
        raise ValueError(f"no factory for {block_id} {version} in e_blocks.py")
    return factory().text


def main(argv=None) -> int:
    import argparse
    import re

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("payload", help="a recorded call: .state/runs/<run>/trace/payloads/<call>.json")
    ap.add_argument("--block", required=True, help="J-09 … J-17")
    ap.add_argument("--from", dest="old", default="v1", help="the version recorded")
    ap.add_argument("--to", dest="new", default=None, help="the version to compare against")
    ap.add_argument("--noise-floor", action="store_true", help="arm A only")
    ap.add_argument("--k", type=int, default=K_MIN)
    ap.add_argument("--live", action="store_true", help="⚠ send calls (subscription by default)")
    args = ap.parse_args(argv)
    if bool(args.new) == bool(args.noise_floor):
        ap.error("give exactly one of --to VERSION or --noise-floor")

    from src.orchestration.trace.store import TraceStore
    from src.orchestration.trace.wire import traced_transport
    from tools.llm_transport import dev_transport, transport_label
    from tools.run_thesis_once import strict_tool, thesis_tool

    record = json.loads(pathlib.Path(args.payload).read_text(encoding="utf-8"))
    payload = str(record["request"]["payload"])
    m = re.search(r"AVAILABLE OBSERVABLES — a falsifier may name only these fields:\n(.+)\n",
                  payload)
    observables = tuple(x.strip() for x in m[1].split(",")) if m else ()
    schema_b = thesis_tool(args.block, observables=observables)["input_schema"]
    tool_a = thesis_tool(args.block, observables=observables, j15_version=args.old)
    tool_b = thesis_tool(args.block, observables=observables,
                         j15_version=args.new or args.old)
    new_calls = (args.k - 1) + (0 if args.noise_floor else args.k)
    print(f"── AGREEMENT PROBE · {args.block} {args.old}"
          f"{' → ' + args.new if args.new else ' (noise floor)'} · k={args.k} ──")
    print(f"  transport  : {transport_label()}")
    print(f"  new calls  : {new_calls} of ~{len(payload) // 3:,} input tokens each")
    if not args.live:
        print("  ⓘ dry run — nothing sent. Add --live to send.")
        return 0

    run_id = f"run-{datetime.now():%Y-%m-%dT%H%M%S}-agreement-{args.block.lower().replace('-', '')}"
    store = TraceStore(REPO / ".state/runs", run_id)
    max_out = int(record["request"].get("max_tokens") or 32000)
    send = {arm: traced_transport(dev_transport(tool=strict_tool(t), max_output=max_out), store,
                                  step_id=f"agreement:{args.block}:{arm}", kind="llm",
                                  prompt_version=v, cost_of=lambda _m, _t: 0.0)
            for arm, t, v in (("A", tool_a, args.old), ("B", tool_b, args.new or args.old))}
    report = probe(pathlib.Path(args.payload), old_text=_block_text(args.block, args.old),
                   new_text=_block_text(args.block, args.new) if args.new else None,
                   schema=schema_b, k=args.k, transport=send)
    store.close("SUCCESS")
    out = REPO / ".state/runs" / run_id / "agreement.json"
    out.write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    print(f"  arms       : {json.dumps(report['arms'])}")
    for path, f in report["fields"].items():
        print(f"  {f['result']:8} {path:40} {f['distribution']}")
    print(f"  → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
