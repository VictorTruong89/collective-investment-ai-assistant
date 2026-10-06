"""`tools/spend_report.py` — subscription calls are never spend (CLAUDE.md house rule, GW-27).

⚠ Found 2026-10-05 preparing go-live: since the trace line stopped carrying the
`response`, the report looked for `transport` where it no longer was and priced
every subscription call at list rate as API spend — a $137 "floor" that was not.
"""
import json

from tools.spend_report import tally


def _run(root, name, *, transport, tin=6_000, tout=1_000, inline=False):
    run = root / name
    (run / "trace" / "payloads").mkdir(parents=True)
    rec = {"type": "ExternalCall", "call_id": "c:1", "payload_ref": "c:1",
           "tokens": {"input": tin, "output": tout}, "error": None,
           "latency_ms": 1000}
    response = {"transport": transport, "notional_usd": 0.12}
    if inline:
        rec["response"] = response
    (run / "trace" / "payloads" / "c:1.json").write_text(
        json.dumps({"request": {}, "response": response}))
    (run / "trace.jsonl").write_text(
        json.dumps(rec) + "\n" + json.dumps({"type": "__run_closed__",
                                             "status": "SUCCESS"}) + "\n")


def test_a_subscription_call_found_only_in_its_payload_is_not_spend(tmp_path):
    _run(tmp_path, "run-a", transport="claude_code")
    result = tally(tmp_path)
    assert result["subscription"] == 1 and result["floor"] == 0.0
    assert result["notional"] == 0.12


def test_an_api_call_is_still_priced(tmp_path):
    _run(tmp_path, "run-b", transport="anthropic_api", tin=1_000_000, tout=0)
    assert tally(tmp_path)["floor"] == 5.00


def test_the_older_inline_response_still_counts(tmp_path):
    _run(tmp_path, "run-c", transport="claude_code", inline=True)
    assert tally(tmp_path)["subscription"] == 1
