"""★ B3's done-when, as a test — the whole walking skeleton (L3 B3, BS-10…BS-12).

```
D-07 --> D-02 (features) --> D-03 (a rank) --> D-12 (compose) --> D-09 (a card)
                                  ^                    ^
                          D-01 (a stub gate)     D-05 (a stub alert)
```

**Done when:** *a card produced entirely by `src/` reaches your inbox for one
ticker, carrying a `RunManifest` (OR-9) and a verdict traceable to an input
verdict (DN-1)* — and ⚠ **the card is `actionable: false`** (BS-33).

Tier: **integration** (constitution §4). Hermetic: the only fake is the SMTP
transport, and the live variant is marked `live` and skipped loudly.
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import pandas as pd
import pytest

from src.orchestration.jobs.b3_run import (
    B3_TICKER, NOT_ACTIONABLE_REASON, run_skeleton,
)
from tests_src.data_engine_fixtures import split

START = date(2024, 4, 1)


def synthetic_prices(n=90, ticker=B3_TICKER):
    """A pre-split ramp, the 10:1 on 2024-06-10, then a post-split ramp.

    Built rather than fetched so the hermetic test exercises the same code path
    the live one does — and so the split is *in* the window, which is the point
    of QY-2's choice of NVDA (it is the only way QA-84/91 get exercised).
    """
    rows, day, px = [], START, 100_000
    while len(rows) < n:
        if day.weekday() < 5:
            if day == date(2024, 6, 10):
                px //= 10
            px = int(px * 1.004)
            rows.append((day, px, px + 200, px - 200, px + 50, 40_000_000 + len(rows)))
        day += timedelta(days=1)
    return pd.DataFrame([{
        "ticker": ticker, "date": d, "open_minor": o, "high_minor": h,
        "low_minor": lo, "close_minor": c, "volume": v, "currency": "USD",
        "source": "fmp",
    } for d, o, h, lo, c, v in rows])


@pytest.fixture
def skeleton(tmp_path):
    raw = synthetic_prices()
    as_of = max(raw["date"])
    return run_skeleton(
        as_of=as_of, adj_as_of=as_of, raw_prices=raw,
        events=[split(ticker=B3_TICKER)],
        event_store_root=tmp_path / "events", manifest_root=tmp_path / "runs",
    )


def test_the_skeleton_completes_every_domain_boundary(skeleton):
    """★ BS-10 — *B3 exercises every domain boundary and nothing deep.*"""
    assert skeleton.outcome.status == "SUCCESS"
    ran = [j.job_id for j in skeleton.outcome.jobs]
    assert ran == ["calendar_check", "prices", "features", "rank", "gate", "risk",
                   "compose", "render", "deliver"]
    assert all(j.status == "SUCCESS" for j in skeleton.outcome.jobs)


def test_the_run_carries_a_runmanifest(skeleton):
    """B3's done-when, first half — OR-9, and it is written BEFORE any work."""
    m = skeleton.manifest
    assert m.run_id and m.git_sha and m.decision_anchor == "open"
    assert m.config_hash.startswith("sha256:")
    assert m.data_as_of == skeleton.card.as_of


def test_bs_27_the_stub_fact_is_in_the_manifest_and_on_the_card(skeleton):
    """★ BS-27/OR-43 — *rather than being silently true.*

    ⚠ *A stub that is indistinguishable from a real gate in the record is how a
    placeholder survives into production.* So the record and the artifact must
    say the same thing, and this asserts they do.
    """
    manifest_stubs = {s.domain: s for s in skeleton.manifest.stubs}
    assert set(manifest_stubs) == {"D-01", "D-05"}
    card_stubs = {s["domain"] for s in skeleton.card.stubs}
    assert "D-01" in card_stubs
    # ✏ 2026-10-06 (RP-53): the data gap says "placeholder", and names today's cause.
    assert any("placeholder" in g for g in skeleton.card.data_gaps)


def test_dn_1_the_verdict_is_traceable_to_an_input_verdict(skeleton):
    """B3's done-when, second half — DN-1. D-12 originates nothing."""
    rec = skeleton.recommendation
    inputs = {rec.verdict_nominated, *(g.verdict_after for g in rec.gates)}
    assert rec.verdict_final in inputs


def test_bs_33_the_card_is_informational_and_says_why(skeleton):
    """★★ BS-33 — the resolution of BS-11 against BS-28/RP-13.

    A B3 stub has no stability, and *a verdict rendered without its stability
    figure is D-15 with better plumbing.* INV-6/DN-22 already permit output
    "explicitly marked non-actionable", so the skeleton walks without claiming
    to be a recommendation.
    """
    assert skeleton.recommendation.actionable is False
    assert skeleton.card.actionable is False
    assert skeleton.card.not_actionable_reason == NOT_ACTIONABLE_REASON
    # ⚠ This used to assert `"B4.5" in ...` — a promise that **B4.5 came and
    #   went without keeping**: the gate and the stability probe both landed and
    #   the card is still informational, now for a data reason (RC-58). The
    #   durable assertion is that the reason names DN-39's two inputs.
    assert "stability" in NOT_ACTIONABLE_REASON
    assert "COMPLETE risk pass" in NOT_ACTIONABLE_REASON


def test_bs_34_no_graded_field_is_fabricated(skeleton):
    """★ BS-34 — *absence reported as absence.*

    ⚠ The tempting alternative is `k=1, distribution={PASS: 1},
    stability_fraction=1.0` — literally true and completely misleading.
    """
    grade = skeleton.recommendation.grade
    assert grade["k"] is None and grade["verdict_distribution"] is None
    assert grade["confidence"] is None and grade["stability_fraction"] is None
    assert skeleton.card.field("stability").value == "not applicable — no model was run"


def test_the_split_is_handled_and_the_handling_is_recorded(tmp_path):
    """QD-15 — *a BLOCK may only be cleared by an explicit, recorded handling.*

    NVDA's 10:1 is inside the window and is a BLOCK-severity event (§6A.2 class
    2). The only handling QD-15 defines is re-deriving the panel at the run's
    `adj_as_of`, and the run must record that it did so rather than assume it.
    """
    from src.data_engine import UnhandledBlockError

    raw = synthetic_prices()
    as_of = max(raw["date"])
    result = run_skeleton(as_of=as_of, adj_as_of=as_of, raw_prices=raw,
                          events=[split(ticker=B3_TICKER)],
                          event_store_root=tmp_path / "e", manifest_root=tmp_path / "r")
    assert result.outcome.status == "SUCCESS"

    # And the gate really can halt: with the handling withheld it raises.
    from src.data_engine import calendar_check
    from src.data_engine.calendar import CachedEventFeed, EventStore
    store = EventStore(tmp_path / "e")
    with pytest.raises(UnhandledBlockError, match="NVDA"):
        calendar_check(tickers=[B3_TICKER], start=START, end=as_of, as_of=as_of,
                       adj_as_of=as_of, feed=CachedEventFeed(store), run_id="r2",
                       handled=None)


def test_dn_38_the_risk_channel_says_nobody_looked(skeleton):
    """★ DN-38/RP-47 — D-05 refused (RK-29), and the card says so."""
    assert skeleton.recommendation.alerts == ()
    assert skeleton.recommendation.alerts_status.startswith("UNCHECKED: ")
    assert "RK-29" in skeleton.card.alerts_status


def test_both_renderings_agree_and_the_html_fetches_nothing(skeleton):
    """RP-31/RP-32/RP-34 — content-equivalent, self-contained, script-free."""
    from src.reporting import assert_content_equivalent, assert_self_contained

    html = skeleton.renderings[f"{B3_TICKER}_{skeleton.card.as_of}.html"].decode()
    md = skeleton.renderings[f"{B3_TICKER}_{skeleton.card.as_of}.md"].decode()
    assert_self_contained(html)
    assert_content_equivalent(html, md)


def test_the_whole_run_is_deterministic(tmp_path):
    """INV-2 at the pipeline level — OR-10's claim, checked end to end.

    ⚠ `run_id` and timings differ by construction; everything the card shows
    must not.
    """
    raw = synthetic_prices()
    as_of = max(raw["date"])
    kw = dict(as_of=as_of, adj_as_of=as_of, raw_prices=raw,
              events=[split(ticker=B3_TICKER)])
    a = run_skeleton(**kw, event_store_root=tmp_path / "e1", manifest_root=tmp_path / "r1")
    b = run_skeleton(**kw, event_store_root=tmp_path / "e2", manifest_root=tmp_path / "r2")

    def scrub(card_obj):
        return {k: v for k, v in card_obj.items() if k != "run_id"}

    assert scrub(a.card.to_json_obj()) == scrub(b.card.to_json_obj())
    assert a.nomination.candidates == b.nomination.candidates
    assert a.manifest.config_hash == b.manifest.config_hash


def test_the_card_reaches_an_inbox(skeleton, tmp_path):
    """B3's done-when, third half — *reaches your inbox*, with the SMTP faked.

    RP-35: the body is a NOTIFICATION and the attachments are the artifact.
    """
    from src.reporting import deliver
    from src.shared.secrets import Secret

    class Capture:
        def __init__(self): self.sent = []
        def send_message(self, msg): self.sent.append(msg)

    transport = Capture()
    record = deliver(
        skeleton.card, skeleton.renderings, sender="fund@example.com",
        recipient="victor@example.com",
        user=Secret("GMAIL_SMTP_USER", "fund@example.com"),
        password=Secret("GMAIL_APP_PASSWORD", "app-password"),
        archive_root=tmp_path / "archive", transport=transport,
    )
    assert record.outcome == "SENT" and len(transport.sent) == 1
    msg = transport.sent[0]
    assert "NOT ACTIONABLE" in msg["Subject"]
    attached = sorted(p.get_filename() for p in msg.iter_attachments())
    assert attached == sorted(skeleton.renderings)
    for name, payload in skeleton.renderings.items():
        assert record.artifact_digests[name].startswith("sha256:")
        assert (tmp_path / "archive" / record.delivery_id / name).read_bytes() == payload


@pytest.mark.live
def test_the_skeleton_runs_on_live_fmp_data(tmp_path):
    """★ The same code path, against the real vendor (DE-37's argument).

    ⚠ Skipped LOUDLY without a key: a skeleton that only ever runs on synthetic
    prices has not been shown to survive contact with the data.
    """
    key = os.environ.get("FMP_API_KEY")
    if not key:
        pytest.skip(
            "FMP_API_KEY is unset, so the B3 skeleton did NOT run against live "
            "data. That is a gap in verification, not a pass (DE-40's argument)"
        )
    from src.data_engine.src.fmp import prices as fp
    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret

    client = FMPClient(Secret("FMP_API_KEY", key))
    start, end = date(2024, 4, 1), date(2024, 8, 30)
    raw = fp.raw_prices(client, B3_TICKER, start, end)
    events = fp.splits(client, B3_TICKER) + fp.dividends(client, B3_TICKER)

    result = run_skeleton(as_of=end, adj_as_of=end, raw_prices=raw, events=events,
                          event_store_root=tmp_path / "e", manifest_root=tmp_path / "r")
    assert result.outcome.status == "SUCCESS"
    assert result.nomination.top.ticker == B3_TICKER
    assert result.card.actionable is False
    assert result.coverage[B3_TICKER]["coverage_fraction"] == 1.0
