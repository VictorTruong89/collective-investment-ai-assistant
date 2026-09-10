"""F9 `AC-F9.1` — ★ ONE contract suite, both adapters. `MS-6.2`.

★★ This is `F1` `AC-1.9` doing its job on a real port: the suite is
parameterised over the registered variants, so `api` and `relay` face **exactly**
the same guarantees. ⚠ The `MU`-71 % lesson — two adapters shared a signature and
differed in a guarantee nobody had written down.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.fundamental.source.adapters import (
    PROMPT_SPEC,
    ApiAdapter,
    RelayAdapter,
)
from src.fundamental.source.errors import (
    ClaimContradictsData,
    SpansMissing,
    UnresolvableTicker,
)
from src.shared.registry import Registry


@dataclass(frozen=True)
class Claim:
    text: str
    is_factual: bool = True
    evidence_ref: str | None = "10-K p42"
    unbound_declared: bool = False


def _raw(claims=None, **kw):
    return {"claims": claims if claims is not None else [Claim("revenue rose 12%")],
            "provenance": {"model_id": "claude-opus-5"}, **kw}


def _shared_confidence(raw):
    """C3 — the SHARED assess_confidence. Neither adapter supplies its own."""
    return {"basis": "evidence_coverage", "value": 0.8}


def _adapter(cls, author_fn=None, contradiction=lambda _c: None):
    return cls(author_fn=author_fn or (lambda t, a, c: _raw()),
               assess_confidence=_shared_confidence,
               contradiction_check=contradiction)


#: `AC-F9.1` — the suite runs against BOTH.
ADAPTERS = [ApiAdapter, RelayAdapter]


@pytest.fixture(params=ADAPTERS, ids=lambda c: c.variant)
def adapter_cls(request):
    return request.param


# --------------------------------------------------------------------------- #
# the five contract clauses, on every variant
# --------------------------------------------------------------------------- #
def test_ac_f9_1_c1_an_unbound_factual_claim_is_refused(adapter_cls):
    """C1 / `D1` — spans required from BOTH adapters.

    ⚠ A port whose two adapters make different guarantees is not one port.
    """
    a = _adapter(adapter_cls,
                 lambda t, s, c: _raw([Claim("margins expanded", evidence_ref=None)]))
    with pytest.raises(SpansMissing):
        a.author("NVDA", "2026-09-04", {})


def test_ac_f9_1_c1_an_explicitly_unbound_claim_is_allowed(adapter_cls):
    a = _adapter(adapter_cls, lambda t, s, c: _raw(
        [Claim("margins expanded", evidence_ref=None, unbound_declared=True)]))
    assert a.author("NVDA", "2026-09-04", {}).claims


def test_ac_f9_3_c2_a_contradicting_claim_RAISES_and_is_never_de_rated(adapter_cls):
    """★★ AC-F9.3 — verification survives the wrapper.

    ⚠ RA-118: a claim contradicting our own data is WRONG, not low-confidence.
    A wrapper that caught this and de-rated would convert a refusal into a
    discount — silently.
    """
    a = _adapter(adapter_cls, contradiction=lambda c: "revenue was 11%, not 12%")
    with pytest.raises(ClaimContradictsData, match="never returned de-rated"):
        a.author("NVDA", "2026-09-04", {})


def test_ac_f9_1_c3_the_adapter_may_not_score_its_own_output(adapter_cls):
    """C3 / RA-67 — ⚠ an adapter scoring its own output grades its own homework."""
    a = adapter_cls(author_fn=lambda t, s, c: _raw(),
                    assess_confidence=lambda raw: {"basis": "adapter", "value": 0.99})
    with pytest.raises(ValueError, match="never\n *from the adapter|from the adapter"):
        a.author("NVDA", "2026-09-04", {})


def test_ac_f9_5_c4_provenance_is_on_every_thesis(adapter_cls):
    t = _adapter(adapter_cls).author("NVDA", "2026-09-04", {})
    assert t.provenance["port"] == "thesis_source"
    assert t.provenance["variant"] == adapter_cls.variant


def test_ac_f9_9_c5_an_unresolvable_ticker_raises(adapter_cls):
    """⚠ An empty thesis reads downstream as 'analysed, nothing to say'."""
    a = _adapter(adapter_cls, lambda t, s, c: {})
    with pytest.raises(UnresolvableTicker, match="nothing to say"):
        a.author("ZZZZ", "2026-09-04", {})


# --------------------------------------------------------------------------- #
# D2 / AC-F9.7 — one prompt, two transports
# --------------------------------------------------------------------------- #
def test_d2_both_adapters_name_the_same_prompt_spec(adapter_cls):
    """⚠ Two prompts would confound every measured difference between them:
    F5 and F7b partition by variant, and no experiment could then separate
    transport from instruction."""
    assert _adapter(adapter_cls).author("NVDA", "2026-09-04", {}).prompt_spec == PROMPT_SPEC


def test_ac_f9_7_depth_parity_the_two_produce_the_same_shape():
    api = _adapter(ApiAdapter).author("NVDA", "2026-09-04", {})
    relay = _adapter(RelayAdapter).author("NVDA", "2026-09-04", {})
    from dataclasses import fields
    assert {f.name for f in fields(api)} == {f.name for f in fields(relay)}
    assert api.prompt_spec == relay.prompt_spec
    assert api.source_variant != relay.source_variant


# --------------------------------------------------------------------------- #
# AC-F9.8 / AC-F9.10 — registry default and identical tracing
# --------------------------------------------------------------------------- #
def test_ac_f9_8_the_api_is_the_registry_default():
    """QR-20 — the API is the default variant for `thesis_source`."""
    r = Registry()
    r.register("thesis_source", "api", lambda: _adapter(ApiAdapter), version="1.0.0")
    r.register("thesis_source", "relay", lambda: _adapter(RelayAdapter), version="1.0.0")
    assert r.variants("thesis_source")[0] == "api", "sorted first AND the default"
    assert r.provenance("thesis_source", "api").variant == "api"


def test_ac_f9_10_both_are_traced_identically():
    """A consumer must not be able to tell which answered, except by provenance."""
    r = Registry()
    for v, cls in (("api", ApiAdapter), ("relay", RelayAdapter)):
        r.register("thesis_source", v, lambda cls=cls: _adapter(cls), version="1.0.0")
    provs = [r.provenance("thesis_source", v) for v in ("api", "relay")]
    assert {p.port for p in provs} == {"thesis_source"}
    assert [p.variant for p in provs] == ["api", "relay"]
    assert all(p.experimental is False for p in provs)


# ═══════════════════════════════════════════════════════════════════════════
# AC-F9.4 — ★★ de-rating is UNCHANGED through the wrapper.
#
# ⚠⚠ `AC-1.77` records that the relay's whole safety case rests on `RA-67`'s
# coverage de-rating firing **unchanged**. F9 §2 puts it in the non-goals:
# *"✗ Changing the confidence rules."* ★ A wrapper is exactly the place a
# de-rating quietly stops applying — and it would look like nothing at all.
# ═══════════════════════════════════════════════════════════════════════════

from src.fundamental.scorecard.coverage import (  # noqa: E402
    CONFIDENCE_FLOOR,
    CONFIDENCE_HOLD_CAP,
    assess_confidence,
)


@pytest.mark.parametrize("coverage", [
    0.0, 0.05,
    CONFIDENCE_FLOOR - 0.001, CONFIDENCE_FLOOR, CONFIDENCE_FLOOR + 0.001,
    CONFIDENCE_HOLD_CAP - 0.001, CONFIDENCE_HOLD_CAP, CONFIDENCE_HOLD_CAP + 0.001,
    0.9, 1.0,
])
def test_ac_f9_4_de_rating_through_the_adapter_equals_calling_it_directly(
        adapter_cls, coverage):
    """`AC-F9.4` — the characterization that pins `RA-67` across the wrapper.

    ★ Both boundary values are exercised on BOTH sides of the threshold, because
    a de-rating defect shows up at the boundary or nowhere: an adapter that
    rounded, clamped or defaulted would agree everywhere in the middle.
    """
    direct = assess_confidence(coverage)
    # ★ The adapter is handed the SHARED function, exactly as production wires it.
    wired = adapter_cls(author_fn=lambda t, a, c: _raw(),
                        assess_confidence=lambda raw: assess_confidence(
                            coverage).to_json_obj())
    thesis = wired.author("MU", "2026-09-09", {})
    assert thesis.confidence == direct.to_json_obj()
    assert thesis.confidence["cap"] == direct.cap
    assert thesis.confidence["basis"] == "evidence_coverage"


def test_ac_f9_4_the_two_adapters_de_rate_identically(monkeypatch):
    """⚠⚠ `D1` — *"a port whose two adapters make different guarantees is not
    one port."* ★ If the relay path de-rated differently from the API path, the
    caller would have to know which answered, which is precisely what `F1`
    `AC-1.9`'s substitution contract forbids.
    """
    results = {}
    for cls in ADAPTERS:
        wired = cls(author_fn=lambda t, a, c: _raw(),
                    assess_confidence=lambda raw: assess_confidence(0.42).to_json_obj())
        results[cls.variant] = wired.author("MU", "2026-09-09", {}).confidence
    assert results["api"] == results["relay"]


def test_ac_f9_4_an_adapter_may_not_substitute_its_own_floor():
    """⚠ `C3` / `RA-67` — an adapter that scores its own output is grading its
    own homework. ★ `SourcedThesis` refuses a confidence whose `basis` says the
    adapter produced it."""
    wired = ApiAdapter(author_fn=lambda t, a, c: _raw(),
                       assess_confidence=lambda raw: {"basis": "adapter",
                                                      "value": 0.99})
    with pytest.raises(ValueError, match="assess_confidence"):
        wired.author("MU", "2026-09-09", {})
