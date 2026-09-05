"""F9 `AC-9.1` — ★ ONE contract suite, both adapters. `MS-6.2`.

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


#: `AC-9.1` — the suite runs against BOTH.
ADAPTERS = [ApiAdapter, RelayAdapter]


@pytest.fixture(params=ADAPTERS, ids=lambda c: c.variant)
def adapter_cls(request):
    return request.param


# --------------------------------------------------------------------------- #
# the five contract clauses, on every variant
# --------------------------------------------------------------------------- #
def test_ac_9_1_c1_an_unbound_factual_claim_is_refused(adapter_cls):
    """C1 / `D1` — spans required from BOTH adapters.

    ⚠ A port whose two adapters make different guarantees is not one port.
    """
    a = _adapter(adapter_cls,
                 lambda t, s, c: _raw([Claim("margins expanded", evidence_ref=None)]))
    with pytest.raises(SpansMissing):
        a.author("NVDA", "2026-09-04", {})


def test_ac_9_1_c1_an_explicitly_unbound_claim_is_allowed(adapter_cls):
    a = _adapter(adapter_cls, lambda t, s, c: _raw(
        [Claim("margins expanded", evidence_ref=None, unbound_declared=True)]))
    assert a.author("NVDA", "2026-09-04", {}).claims


def test_ac_9_3_c2_a_contradicting_claim_RAISES_and_is_never_de_rated(adapter_cls):
    """★★ AC-9.3 — verification survives the wrapper.

    ⚠ RA-118: a claim contradicting our own data is WRONG, not low-confidence.
    A wrapper that caught this and de-rated would convert a refusal into a
    discount — silently.
    """
    a = _adapter(adapter_cls, contradiction=lambda c: "revenue was 11%, not 12%")
    with pytest.raises(ClaimContradictsData, match="never returned de-rated"):
        a.author("NVDA", "2026-09-04", {})


def test_ac_9_1_c3_the_adapter_may_not_score_its_own_output(adapter_cls):
    """C3 / RA-67 — ⚠ an adapter scoring its own output grades its own homework."""
    a = adapter_cls(author_fn=lambda t, s, c: _raw(),
                    assess_confidence=lambda raw: {"basis": "adapter", "value": 0.99})
    with pytest.raises(ValueError, match="never\n *from the adapter|from the adapter"):
        a.author("NVDA", "2026-09-04", {})


def test_ac_9_5_c4_provenance_is_on_every_thesis(adapter_cls):
    t = _adapter(adapter_cls).author("NVDA", "2026-09-04", {})
    assert t.provenance["port"] == "thesis_source"
    assert t.provenance["variant"] == adapter_cls.variant


def test_ac_9_9_c5_an_unresolvable_ticker_raises(adapter_cls):
    """⚠ An empty thesis reads downstream as 'analysed, nothing to say'."""
    a = _adapter(adapter_cls, lambda t, s, c: {})
    with pytest.raises(UnresolvableTicker, match="nothing to say"):
        a.author("ZZZZ", "2026-09-04", {})


# --------------------------------------------------------------------------- #
# D2 / AC-9.7 — one prompt, two transports
# --------------------------------------------------------------------------- #
def test_d2_both_adapters_name_the_same_prompt_spec(adapter_cls):
    """⚠ Two prompts would confound every measured difference between them:
    F5 and F7b partition by variant, and no experiment could then separate
    transport from instruction."""
    assert _adapter(adapter_cls).author("NVDA", "2026-09-04", {}).prompt_spec == PROMPT_SPEC


def test_ac_9_7_depth_parity_the_two_produce_the_same_shape():
    api = _adapter(ApiAdapter).author("NVDA", "2026-09-04", {})
    relay = _adapter(RelayAdapter).author("NVDA", "2026-09-04", {})
    from dataclasses import fields
    assert {f.name for f in fields(api)} == {f.name for f in fields(relay)}
    assert api.prompt_spec == relay.prompt_spec
    assert api.source_variant != relay.source_variant


# --------------------------------------------------------------------------- #
# AC-9.8 / AC-9.10 — registry default and identical tracing
# --------------------------------------------------------------------------- #
def test_ac_9_8_the_api_is_the_registry_default():
    """QR-20 — the API is the default variant for `thesis_source`."""
    r = Registry()
    r.register("thesis_source", "api", lambda: _adapter(ApiAdapter), version="1.0.0")
    r.register("thesis_source", "relay", lambda: _adapter(RelayAdapter), version="1.0.0")
    assert r.variants("thesis_source")[0] == "api", "sorted first AND the default"
    assert r.provenance("thesis_source", "api").variant == "api"


def test_ac_9_10_both_are_traced_identically():
    """A consumer must not be able to tell which answered, except by provenance."""
    r = Registry()
    for v, cls in (("api", ApiAdapter), ("relay", RelayAdapter)):
        r.register("thesis_source", v, lambda cls=cls: _adapter(cls), version="1.0.0")
    provs = [r.provenance("thesis_source", v) for v in ("api", "relay")]
    assert {p.port for p in provs} == {"thesis_source"}
    assert [p.variant for p in provs] == ["api", "relay"]
    assert all(p.experimental is False for p in provs)
