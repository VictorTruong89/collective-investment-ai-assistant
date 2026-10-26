"""F14 — position sizing on demand. AC-F14.1…AC-F14.17.

★ The capital base is D-11's REPORTED balance (`RC-70…RC-77`), read here from the tracked
SYNTHETIC holdings fixtures (`tests_src/fixtures/broker_statements/holdings/`, every value
invented). ⚠ The policy numbers below (`r_total`, `r_ceiling`, `target_positions`) are
**test values, invented for the arithmetic** — they are not a proposal and appear in no
config (`PS-43`, F14 `D6`).

Tier: unit unless named (constitution §4).
"""

from __future__ import annotations

import ast
import json
import math
import os
import pathlib
import shutil
import statistics
import subprocess
import sys
from dataclasses import replace
from datetime import date, timedelta

import pytest

from src.portfolio.errors import NoStopError, PolicyMissingError, UnavailableInputError
from src.portfolio.on_demand.size_for import (
    Policy, Sigma, load_policy, realised_sigma, size_on_demand,
)
from src.portfolio.errors import ReserveUnavailableError
from src.recording.book.holdings import parse_holdings
from tests_src.broker_fixtures import SYNTHETIC

REPO = pathlib.Path(__file__).resolve().parents[1]
HOLDINGS = SYNTHETIC / "holdings"
TOOL = REPO / "tools" / "size_for.py"

#: ⚠ Invented for the arithmetic. Not policy.
POLICY = Policy(account_id="TFSA_8", r_total=0.10, r_ceiling=0.01, target_positions=5,
                source="test")
NO_SIGMA = Sigma(None, "unavailable: test")


def stmt(fixture="HLD_1", account_id="TFSA_8"):
    return parse_holdings(HOLDINGS / f"Holdings_{fixture}.csv", account_id=account_id)


def size(**kw):
    args = dict(ticker="NEWCO", account_id="TFSA_8", entry=10.0, currency="CAD", stop=8.0,
                statement=stmt(), policy=POLICY, sigma=NO_SIGMA, held_stops={},
                discovered_accounts=("TFSA_8",))
    args.update(kw)
    return size_on_demand(**args)


# --------------------------------------------------------------------------- #
# AC-F14.1 — capital is the reported balance
# --------------------------------------------------------------------------- #
def test_ac_f14_1_capital_is_the_reported_balance_with_its_date():
    """AC-F14.1 (PS-3, PS-41, RC-77, D2)."""
    obj = size().to_json_obj()
    cap = obj["inputs"]["capital_base"]
    assert cap == {"value": 1750.25, "currency": "CAD", "source": "holdings_export",
                   "as_of": "2026-06-12"}


def test_ac_f14_1_an_account_with_no_holdings_export_is_refused_by_name(tmp_path):
    """AC-F14.1 — through the command: no derived, older or stated capital."""
    shutil.copy(HOLDINGS / "TransactionHistory_HLD_1.csv", tmp_path)
    out = _run(tmp_path, "NEWCO", "--account", "HLD_1", "--entry", "10", "--stop", "8",
               "--currency", "CAD")
    assert out.returncode == 1
    assert "no holdings export for HLD_1" in out.stdout + out.stderr
    assert "shares" not in out.stdout.lower()


# --------------------------------------------------------------------------- #
# AC-F14.2 — policy, no defaults
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("text, missing", [
    ("accounts: {}\n", "TFSA_8"),
    ("accounts:\n  TFSA_8: {r_total: 0.1, target_positions: 5}\n", "r_ceiling"),
    ("accounts:\n  TFSA_8: {r_total: 0.1, r_ceiling: 0.2, target_positions: 5}\n", "r_ceiling"),
    ("accounts:\n  TFSA_8: {r_total: 0.1, r_ceiling: 0.01, target_positions: 0}\n", "target_positions"),
])
def test_ac_f14_2_a_missing_or_out_of_range_policy_raises_naming_it(tmp_path, text, missing):
    """AC-F14.2 (PS-43, D6)."""
    path = tmp_path / "policy.yaml"
    path.write_text(text)
    with pytest.raises(PolicyMissingError, match=missing):
        load_policy("TFSA_8", path)


def test_ac_f14_2_the_policy_used_is_reported_with_its_source(tmp_path):
    """AC-F14.2."""
    path = tmp_path / "policy.yaml"
    path.write_text("accounts:\n  TFSA_8: {r_total: 0.1, r_ceiling: 0.01, target_positions: 5}\n")
    policy = load_policy("TFSA_8", path)
    assert (policy.r_total, policy.r_ceiling, policy.target_positions) == (0.1, 0.01, 5)
    inputs = size(policy=policy).to_json_obj()["inputs"]
    assert inputs["r_ceiling"] == {"value": 0.01, "source": str(path)}
    assert inputs["target_positions"]["source"] == str(path)


def test_ac_f14_2_the_shipped_policy_file_holds_no_invented_values():
    """AC-F14.2 / D6 — Victor gave no values: the shipped file names no account."""
    import yaml

    shipped = yaml.safe_load((REPO / "config" / "portfolio_policy.yaml").read_text())
    assert shipped["accounts"] in ({}, None)


# --------------------------------------------------------------------------- #
# AC-F14.3 — the budget is the ceiling, visibly
# --------------------------------------------------------------------------- #
def test_ac_f14_3_every_factor_is_unmeasured_and_the_budget_equals_the_ceiling():
    """AC-F14.3 (PS-33, PS-34, D3)."""
    answer = size()
    factors = answer.to_json_obj()["risk_budget_factors"]
    for name in ("E_edge", "C_confidence", "P_portfolio", "D_drawdown"):
        assert factors[name]["status"] == "unmeasured" and factors[name]["value"] == 1.0
    assert factors["effective"] == pytest.approx(0.01)
    assert "budget = ceiling, because E, C, P, D are not measured yet" in answer.render()


# --------------------------------------------------------------------------- #
# AC-F14.4 — committed risk
# --------------------------------------------------------------------------- #
def test_ac_f14_4_committed_risk_from_stated_held_stops():
    """AC-F14.4 (PS-29) — FRC.B 100 @ 10.0995 stop 9.0995 → 100.00; FTC stop above cost → 0."""
    risk = size(held_stops={"FRC.B": 9.0995, "FTC": 9.0}).to_json_obj()["account_risk"]
    assert risk["committed_status"] == "measured"
    assert risk["committed"] == pytest.approx(100.00)
    assert risk["allowance"] == pytest.approx(175.025)
    assert risk["remaining"] == pytest.approx(75.025)


def test_ac_f14_4_a_missing_held_stop_makes_committed_unmeasured_and_named():
    """AC-F14.4 (D4) — null, never 0; only r_ceiling binds, stated."""
    obj = size(held_stops={"FRC.B": 9.0}).to_json_obj()
    risk = obj["account_risk"]
    assert risk["committed"] is None and risk["remaining"] is None
    assert risk["committed_status"] == "unmeasured"
    assert obj["inputs"]["held_stops"]["missing"] == ["FTC"]
    assert obj["risk_capital"]["binds"] == "r_ceiling"


def test_ac_f14_4_a_stop_for_a_symbol_not_held_raises():
    """AC-F14.4."""
    with pytest.raises(UnavailableInputError, match="ZZZ"):
        size(held_stops={"ZZZ": 1.0})


# --------------------------------------------------------------------------- #
# AC-F14.5 — the per-trade risk
# --------------------------------------------------------------------------- #
def test_ac_f14_5_the_reserve_term_binds_when_it_is_smaller():
    """AC-F14.5 (PS-27) — remaining 75.025 / n_reserve 3 = 25.008 < ceiling 2 % = 35.005."""
    policy = replace(POLICY, r_ceiling=0.02)
    obj = size(policy=policy, held_stops={"FRC.B": 9.0995, "FTC": 9.0}).to_json_obj()
    assert obj["account_risk"]["n_reserve"] == 3
    assert obj["risk_capital"]["value"] == pytest.approx(75.025 / 3)
    assert obj["risk_capital"]["binds"] == "risk_remaining / n_reserve"


def test_ac_f14_5_the_ceiling_binds_when_it_is_smaller():
    """AC-F14.5 — ceiling 1 % = 17.5025 < 25.008."""
    obj = size(held_stops={"FRC.B": 9.0995, "FTC": 9.0}).to_json_obj()
    assert obj["risk_capital"]["value"] == pytest.approx(17.5025)
    assert obj["risk_capital"]["binds"] == "r_ceiling"


def test_ac_f14_5_a_full_account_refuses():
    """AC-F14.5 (PS-43) — 2 lines held, target 2 → no open slot."""
    with pytest.raises(ReserveUnavailableError):
        size(policy=replace(POLICY, target_positions=2))


# --------------------------------------------------------------------------- #
# AC-F14.6 — which constraint binds: three known answers
# --------------------------------------------------------------------------- #
def test_ac_f14_6_risk_binds():
    """AC-F14.6 — 17.5025 / 2 = 8.75 sh → 87.51 < cash 150.25 < cap 262.54 → 8 shares."""
    obj = size(entry=10.0, stop=8.0).to_json_obj()
    assert obj["binding_constraint"] == "risk"
    assert obj["notional"]["risk"] == pytest.approx(87.5125)
    assert obj["notional"]["cash"] == pytest.approx(150.25)
    assert obj["notional"]["cap_15pct"] == pytest.approx(262.5375)
    assert (obj["shares"], obj["shares_exact"]) == (8, pytest.approx(8.75125))


def test_ac_f14_6_cash_binds():
    """AC-F14.6 — d = 0.5 → 350.05 of risk capacity; cash 150.25 binds → 15 shares."""
    obj = size(entry=10.0, stop=9.5).to_json_obj()
    assert obj["binding_constraint"] == "cash"
    assert obj["shares"] == 15
    assert obj["deploy_notional"] == pytest.approx(150.25)


def test_ac_f14_6_the_15pct_cap_binds():
    """AC-F14.6 (PS-10) — with cash 1,000 the cap 262.54 binds → 26 shares."""
    obj = size(entry=10.0, stop=9.5, statement=replace(stmt(), cash_total=1000.0)).to_json_obj()
    assert obj["binding_constraint"] == "cap_15pct"
    assert obj["shares"] == 26


# --------------------------------------------------------------------------- #
# AC-F14.7 — the stop
# --------------------------------------------------------------------------- #
def test_ac_f14_7_a_stated_stop_reports_its_implied_k():
    """AC-F14.7 (PS-7)."""
    obj = size(stop=8.0, sigma=Sigma(0.02, "stated")).to_json_obj()
    assert obj["inputs"]["k"]["source"] == "implied by the stated stop"
    assert obj["inputs"]["k"]["value"] == pytest.approx(2.0 / (0.02 * math.sqrt(21) * 10.0))


def test_ac_f14_7_a_stated_stop_with_no_sigma_has_k_unavailable():
    """AC-F14.7."""
    obj = size(stop=8.0).to_json_obj()
    assert obj["inputs"]["k"]["value"] is None
    assert any(u.startswith("implied_k") for u in obj["unavailable"])


def test_ac_f14_7_no_stop_uses_the_volatility_stop_at_the_default_k():
    """AC-F14.7 (PS-6, D5)."""
    obj = size(stop=None, sigma=Sigma(0.02, "stated")).to_json_obj()
    expected = 10.0 - 1.5 * 0.02 * math.sqrt(21) * 10.0
    assert obj["inputs"]["stop"]["value"] == pytest.approx(expected)
    assert obj["inputs"]["stop"]["source"] == "volatility_stop"
    assert obj["inputs"]["k"] == {"value": 1.5, "source": "default (QS-2 open)"}


def test_ac_f14_7_no_stop_and_no_sigma_refuses():
    """AC-F14.7 (PS-5)."""
    with pytest.raises(NoStopError):
        size(stop=None)


def test_ac_f14_7_a_stop_at_or_above_entry_refuses():
    """AC-F14.7."""
    with pytest.raises(NoStopError):
        size(stop=10.0)


# --------------------------------------------------------------------------- #
# AC-F14.8 — σ, labelled
# --------------------------------------------------------------------------- #
def _closes(n, start=100.0):
    d0 = date(2026, 9, 1)
    return [(d0 + timedelta(days=i), start * (1.01 if i % 2 else 0.995) ** (i % 3))
            for i in range(n)]


def test_ac_f14_8_realised_sigma_is_the_21_session_sd_of_log_closes():
    """AC-F14.8 (PS-23)."""
    closes = _closes(30)
    window = closes[-22:]
    rets = [math.log(b[1] / a[1]) for a, b in zip(window, window[1:])]
    sigma = realised_sigma(closes, source="FMP")
    assert sigma.value == pytest.approx(statistics.stdev(rets))
    assert sigma.source.startswith("realised") and closes[-1][0].isoformat() in sigma.source


def test_ac_f14_8_too_few_closes_is_unavailable_never_a_shorter_window():
    """AC-F14.8."""
    sigma = realised_sigma(_closes(21), source="FMP")
    assert sigma.value is None and sigma.source.startswith("unavailable")


def test_ac_f14_8_a_cad_listing_is_never_fetched_by_its_bare_ticker():
    """AC-F14.8 (RC-53, D8, D11) — the command asks for no FMP prices for a CAD entry."""
    from tools.size_for import resolve_sigma

    calls = []
    sigma = resolve_sigma("BMO", currency="CAD", stated=None, as_of=date(2026, 10, 25),
                          fetch_closes=lambda *a: calls.append(a) or [])
    assert calls == [] and sigma.value is None
    assert "CAD listing or CDR" in sigma.source
    stated = resolve_sigma("BMO", currency="CAD", stated=0.015, as_of=date(2026, 10, 25),
                           fetch_closes=lambda *a: calls.append(a) or [])
    assert (stated.value, stated.source) == (0.015, "stated")


# --------------------------------------------------------------------------- #
# AC-F14.9 / AC-F14.10 — currency and cash
# --------------------------------------------------------------------------- #
def test_ac_f14_9_a_usd_entry_converts_at_the_footer_rate():
    """AC-F14.9 (PS-4) — HLD_2: footer 1.40; cash 54.00 CAD → 38.57 USD."""
    obj = size(statement=stmt("HLD_2"), currency="USD", entry=100.0, stop=90.0).to_json_obj()
    assert obj["inputs"]["fx_usd_cad"] == {"value": 1.4, "source": "holdings_export",
                                           "as_of": "2026-10-25"}
    assert obj["notional"]["currency"] == "USD"
    assert obj["notional"]["cash"] == pytest.approx(54.00 / 1.4)
    # risk 60.47 CAD over (10 USD × 1.40) per share = 4.319 sh
    assert obj["shares_exact"] == pytest.approx(54.00 / 1.4 / 100.0)   # cash binds


def test_ac_f14_9_no_footer_rate_makes_a_usd_sizing_unavailable():
    """AC-F14.9 (FX-3) — HLD_1 has no USD and so no rate."""
    with pytest.raises(UnavailableInputError, match="FX-3"):
        size(currency="USD")


def test_ac_f14_10_cash_is_the_reported_total_and_states_auto_fx():
    """AC-F14.10 (D9)."""
    answer = size(statement=stmt("HLD_2"), currency="USD", entry=100.0, stop=90.0)
    cash = answer.to_json_obj()["inputs"]["cash_available"]
    assert cash == {"value": 54.0, "currency": "CAD", "source": "holdings_export",
                    "as_of": "2026-10-25"}
    assert "auto-FX" in answer.render()


# --------------------------------------------------------------------------- #
# AC-F14.11 / AC-F14.12 — per account, book-wide stated, RESP stated
# --------------------------------------------------------------------------- #
def test_ac_f14_11_book_wide_is_unchecked_and_names_the_accounts_without_an_export():
    """AC-F14.11 (AC-6.18, PS-19, RC-77)."""
    obj = size(discovered_accounts=("RRSP_7", "TFSA_8", "TFSA_9"),
               accounts_with_holdings=("TFSA_8",)).to_json_obj()
    assert obj["book_wide"].startswith("UNCHECKED")
    assert "RRSP_7" in obj["book_wide"] and "TFSA_9" in obj["book_wide"]
    assert obj["consequences"]["weight_fund_pct"].startswith("UNCHECKED")


def test_ac_f14_12_the_resp_is_sized_and_its_exclusion_is_stated():
    """AC-F14.12 (AC-6.19, PS-20, RC-4, D10)."""
    obj = size(account_id="RESP_9", statement=stmt(account_id="RESP_9")).to_json_obj()
    assert obj["consequences"]["weight_fund_pct"] == "excluded (RC-4)"
    assert obj["shares"] == 8


# --------------------------------------------------------------------------- #
# AC-F14.13 — no LLM, no D-01 (AC-6.20)
# --------------------------------------------------------------------------- #
FORBIDDEN = ("src.shared.llm", "src.fundamental", "anthropic")


def test_ac_f14_13_portfolio_and_the_tool_import_no_llm_and_no_d01():
    """AC-F14.13 (PS-25, ST-5) — invariant over every module in the tree."""
    files = [*(REPO / "src" / "portfolio").rglob("*.py"), TOOL]
    for path in files:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            for name in names:
                assert not name.startswith(FORBIDDEN), f"{path}: imports {name}"


# --------------------------------------------------------------------------- #
# AC-F14.14 / AC-F14.17 — writes nothing; the dry run
# --------------------------------------------------------------------------- #
def _tree(*roots):
    seen = {}
    for root in roots:
        for p in pathlib.Path(root).rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                seen[str(p)] = p.stat().st_mtime_ns
    return seen


def _run(root, *args, policy=None):
    env = dict(os.environ, BMO_STATEMENTS_DIR=str(root), PYTHONDONTWRITEBYTECODE="1")
    env.pop("FMP_API_KEY", None)
    extra = ["--policy", str(policy)] if policy else []
    return subprocess.run([sys.executable, str(TOOL), *args, *extra], cwd=REPO, env=env,
                          capture_output=True, text=True, timeout=60)


@pytest.fixture
def drop(tmp_path):
    root = tmp_path / "broker"
    root.mkdir()
    for name in ("Holdings_HLD_1.csv", "TransactionHistory_HLD_1.csv"):
        shutil.copy(HOLDINGS / name, root / name.replace("HLD_1", "TFSA_8"))
    policy = tmp_path / "policy.yaml"
    policy.write_text("accounts:\n  TFSA_8: {r_total: 0.1, r_ceiling: 0.01, target_positions: 5}\n")
    return root, policy


def test_ac_f14_14_a_full_run_and_a_dry_run_write_nothing(drop, tmp_path):
    """AC-F14.14 (AC-6.21, PS-26) — integration, hermetic."""
    root, policy = drop
    before = _tree(tmp_path, REPO / ".state", REPO / "config")
    full = _run(root, "NEWCO", "--account", "TFSA_8", "--entry", "10", "--stop", "8",
                "--currency", "CAD", "--json", policy=policy)
    dry = _run(root, "NEWCO", "--account", "TFSA_8", "--entry", "10", "--stop", "8",
               "--currency", "CAD", "--dry-run", policy=policy)
    assert full.returncode == 0, full.stderr
    assert dry.returncode == 0, dry.stderr
    assert json.loads(full.stdout)["shares"] == 8
    assert _tree(tmp_path, REPO / ".state", REPO / "config") == before


def test_ac_f14_17_the_dry_run_names_what_is_missing_and_exits_1(drop):
    """AC-F14.17 — USD with no stated σ: FMP would be called, so the dry run says so; a CAD
    entry with no stop and no σ would refuse → exit 1, named."""
    root, policy = drop
    out = _run(root, "NEWCO", "--account", "TFSA_8", "--entry", "10", "--currency", "CAD",
               "--dry-run", policy=policy)
    assert out.returncode == 1
    assert "σ" in out.stdout and "unavailable" in out.stdout
    assert "1750.25" in out.stdout.replace(",", "")


# --------------------------------------------------------------------------- #
# AC-F14.16 — a held ticker: the pyramid check, no new slot
# --------------------------------------------------------------------------- #
def test_ac_f14_16_a_held_ticker_reports_the_pyramid_check_and_takes_no_new_slot():
    """AC-F14.16 (PS-15, PS-16) — FRC.B held 100 @ 10.0995; buying at 12 raises the average."""
    obj = size(ticker="FRC.B", entry=12.0, stop=11.0,
               held_stops={"FRC.B": 9.0995, "FTC": 9.0}).to_json_obj()
    assert obj["pyramid"]["is_scale_in"] is True and obj["pyramid"]["blocks"] is False
    assert obj["account_risk"]["n_reserve"] == 4        # 5 − (2 held − this one)


# --------------------------------------------------------------------------- #
# AC-F14.15 — every input labelled
# --------------------------------------------------------------------------- #
HOLDINGS_DERIVED = ("capital_base", "cash_available", "fx_usd_cad")


@pytest.mark.parametrize("kw", [
    {}, {"stop": None, "sigma": Sigma(0.02, "stated")},
    {"statement": stmt("HLD_2"), "currency": "USD", "entry": 100.0, "stop": 90.0},
    {"held_stops": {"FRC.B": 9.0995, "FTC": 9.0}},
])
def test_ac_f14_15_every_input_carries_a_source_and_holdings_inputs_an_as_of(kw):
    """AC-F14.15 (RC-74) — data contract over several answers."""
    answer = size(**kw)
    inputs = answer.to_json_obj()["inputs"]
    for name, item in inputs.items():
        assert item.get("source"), name
    for name in HOLDINGS_DERIVED:
        if name in inputs and inputs[name]["value"] is not None:
            assert inputs[name]["as_of"], name
    assert "days old" in answer.render()
