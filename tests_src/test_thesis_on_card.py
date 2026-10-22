"""F13 `D13` — the daily card reads the nominee's thesis (AC-F13.15 … AC-F13.18).

★ D-01 finds it (`on_demand/lookup.py`), D-08's `thesis_gate` grades it (§11.2), D-12 carries
it (DN-42), D-09 shows it — or shows "no thesis — no peer set" / "— not yet written" (RP-56).
"""
import json
import pathlib
import shutil
from datetime import date

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests_src/fixtures/theses/MU_2025-06-26_thesis.json"
RUN = "run-2026-10-04T031717-mu-thesis"
CONFIG = {"subjects": {"MU": {"name": "Micron Technology, Inc.", "cik": "0000723125",
                              "sector_list": "memory_v1"}}}


def _state(tmp_path, *, thesis_as_of="2025-06-26", fired=0, done=True):
    runs, root = tmp_path / "runs", tmp_path / "thesis_for"
    (runs / RUN).mkdir(parents=True)
    shutil.copy(FIXTURE, runs / RUN / "thesis.json")
    chain = root / f"MU_{thesis_as_of}" / "chain.json"
    chain.parent.mkdir(parents=True)
    chain.write_text(json.dumps({
        "ticker": "MU", "as_of": thesis_as_of, "transport": "claude_code",
        "thesis_run_id": RUN if done else None,
        "steps": [{"step": "thesis", "run_id": RUN, "status": "done" if done else "failed"}],
        "checks": {"thesis_run_id": RUN, "falsifiers": {"falsifiers": 4, "FIRED": fired}}}))
    return root, runs


def _look(tmp_path, ticker="MU", as_of=date(2025, 7, 1), **kw):
    from src.fundamental.on_demand.lookup import thesis_for_card

    root, runs = _state(tmp_path, **kw)
    return thesis_for_card(ticker, as_of, root=root, runs_root=runs, config=CONFIG)


# ── AC-F13.15 — the lookup ───────────────────────────────────────────────────

def test_ac_f13_15_the_newest_completed_thesis_at_or_before_as_of_is_found(tmp_path):
    found = _look(tmp_path)
    assert found.status == "found" and found.run_id == RUN
    assert found.thesis.verdict == "SELL" and not found.stale and not found.falsifier_fired
    assert found.ref["verdict"] == "SELL" and found.ref["run_id"] == RUN
    assert found.ref["provenance"]["variant"] == "claude_code"
    assert "Cash after capital expenditure" in found.ref["falsifier"]


def test_ac_f13_15_a_thesis_after_as_of_is_not_seen(tmp_path):
    assert _look(tmp_path, as_of=date(2025, 6, 25)).status == "not_written"


def test_ac_f13_15_stale_after_120_days_and_a_fired_falsifier_is_carried(tmp_path):
    found = _look(tmp_path, as_of=date(2025, 10, 25), fired=2)
    assert found.stale and found.falsifier_fired


def test_ac_f13_15_a_failed_chain_is_not_a_thesis(tmp_path):
    assert _look(tmp_path, done=False).status == "not_written"


def test_ac_f13_15_no_peer_set_and_not_written_name_themselves(tmp_path):
    none = _look(tmp_path, ticker="MRNA")
    assert none.status == "no_peer_set" and none.reason.startswith("no thesis — no peer set")
    assert none.thesis is None and none.ref is None


# ── AC-F13.16 — the daily thesis_gate ────────────────────────────────────────

class _Ctx:
    def __init__(self, ticker, as_of, root, runs):
        from types import SimpleNamespace

        self.as_of, self.thesis_root, self.thesis_runs_root = as_of, str(root), str(runs)
        self.thesis_config = CONFIG
        self.probed_thesis, self.card_thesis = None, None
        self.thesis_stale = self.falsifier_fired = False
        self._rank = SimpleNamespace(top=SimpleNamespace(ticker=ticker))

    def require(self, job):
        assert job == "rank"
        return self._rank


def _gate(tmp_path, ticker, as_of=date(2025, 7, 1)):
    from src.orchestration.jobs.wiring import _thesis_gate

    root, runs = _state(tmp_path)
    ctx = _Ctx(ticker, as_of, root, runs)
    return _thesis_gate(None, None, ctx), ctx


def test_ac_f13_16_a_found_thesis_is_graded_by_the_table_not_the_stub(tmp_path):
    verdict, ctx = _gate(tmp_path, "MU")
    assert verdict.produced_by_stub is None
    assert verdict.status == "VETO" and "SELL" in verdict.reason      # §11.2: SELL ⇒ VETO
    assert ctx.card_thesis.status == "found"


@pytest.mark.parametrize("ticker,as_of,why", [("MRNA", date(2025, 7, 1), "no peer set"),
                                              ("MU", date(2025, 6, 1), "not yet written")])
def test_ac_f13_16_no_thesis_is_NO_THESIS_never_PASS(tmp_path, ticker, as_of, why):
    verdict, _ = _gate(tmp_path, ticker, as_of)
    assert verdict.status == "NO_THESIS" and why in verdict.reason
    assert verdict.produced_by_stub is None


# ── AC-F13.17 — D-12 carries the reference ───────────────────────────────────

def test_ac_f13_17_compose_carries_the_thesis_ref_verbatim():
    from tests_src.test_decision_b3 import composed, gate

    ref = {"run_id": RUN, "verdict": "SELL", "falsifier": "x"}
    rec = composed(gate_verdicts=[gate("VETO")], thesis_ref=ref, actionable=False,
                   top_thesis_stability=None)
    assert rec.thesis_ref == ref and rec.to_json_obj()["thesis_ref"] == ref
    assert rec.actionable is False


# ── AC-F13.18 — the card ─────────────────────────────────────────────────────

def _card(gate_verdict, *, thesis_ref=None):
    from src.decision import compose
    from src.reporting import build_card
    from src.risk import AlertSet, unchecked
    from tests_src.test_card_refused_ranker import _refused_nomination
    from tests_src.test_decision_b3 import AS_OF

    rec = compose(nomination=_refused_nomination(), gate_verdicts=[gate_verdict],
                  alert_set=AlertSet((), unchecked("no book (RK-29)")), run_id="run-1",
                  as_of=AS_OF, gate_roster_declared=("thesis",), manifest_anchor="open",
                  actionable=False, not_actionable_reason="ranked by a refused model",
                  top_thesis_stability=None, thesis_ref=thesis_ref)
    return rec, build_card(rec, as_of=AS_OF)


@pytest.mark.parametrize("why", ["no peer set", "not yet written"])
def test_ac_f13_18_no_thesis_reads_as_absence_not_as_a_hold(why):
    from src.fundamental.contracts.gate import GateVerdict
    from tests_src.test_decision_b3 import AS_OF

    reason = f"no thesis — {why}: because"
    rec, card = _card(GateVerdict("thesis", "NVDA", AS_OF, "NO_THESIS", reason))
    assert rec.verdict_final == "HOLD"                       # the composed record is untouched
    line = card.field("verdict").value
    assert line == f"no verdict — ranked #1 by a refused model; no thesis — {why}"
    assert why in card.falsifier and any(why in g for g in card.data_gaps)


def test_ac_f13_18_a_found_thesis_shows_its_own_verdict_and_falsifiers():
    from src.fundamental.contracts.gate import GateVerdict, Grade
    from tests_src.test_decision_b3 import AS_OF

    ref = json.loads(FIXTURE.read_text())
    from src.fundamental.on_demand.lookup import thesis_ref
    from src.fundamental.thesis.models import Thesis

    th = Thesis.from_json_obj(ref["thesis"])
    gv = GateVerdict("thesis", "NVDA", AS_OF, "VETO", "the thesis verdict is SELL",
                     Grade(verdict="SELL"))
    _rec, card = _card(gv, thesis_ref=thesis_ref(th, RUN, transport="claude_code"))
    assert card.field("analyst_verdict").value == "SELL"
    assert "Cash after capital expenditure" in card.falsifier
    source = card.field("thesis_source")
    assert source.value == "thesis_for (claude_code)" and "full evidence bundle" in source.note
