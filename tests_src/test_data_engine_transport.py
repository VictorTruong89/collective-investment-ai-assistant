"""D-07 §5A — the EDGAR transport. ★ The class every other test fakes away."""
import gzip
import json
import zlib

from src.data_engine.src.edgar.client import _decode


class _Headers(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


def test_ac_7_44_a_gzip_response_is_decompressed():
    """★★ DE-50 — ⚠ *the first real EDGAR call this project ever made died here.*
    `_get` asks for gzip and `urllib` does not decompress transparently."""
    payload = json.dumps({"facts": {}}).encode()
    body = _decode(gzip.compress(payload), _Headers({"Content-Encoding": "gzip"}))
    assert json.loads(body) == {"facts": {}}


def test_ac_7_44_a_deflate_response_is_decompressed():
    """DE-50 — the header names both encodings, so both must round-trip."""
    payload = json.dumps({"ok": 1}).encode()
    raw = zlib.compressobj(wbits=-zlib.MAX_WBITS)
    compressed = raw.compress(payload) + raw.flush()
    body = _decode(compressed, _Headers({"Content-Encoding": "deflate"}))
    assert json.loads(body) == {"ok": 1}


def test_ac_7_44_an_identity_response_is_not_decompressed():
    """⚠ Keyed on the RESPONSE header, never the request: a server may ignore
    `Accept-Encoding`, and decompressing an identity body is the same defect in
    the other direction."""
    body = _decode(b'{"ok": 2}', _Headers())
    assert json.loads(body) == {"ok": 2}


def test_ac_7_44_raw_gzip_bytes_never_reach_json_loads():
    """★ The regression itself: decoding gzip as UTF-8 raises on byte 0x8b."""
    payload = gzip.compress(json.dumps({"facts": {}}).encode())
    assert payload[:2] == b"\x1f\x8b"
    body = _decode(payload, _Headers({"Content-Encoding": "gzip"}))
    assert body.startswith("{")


def test_de_54_a_sub_penny_vendor_price_rounds_rather_than_dropping_the_ticker():
    """★★ DE-54 — ⚠ *measured 2026-08-27*: `AAPL` returned `310.245` and
    `SNDK` `1454.445`, `Money.from_float` raised, and **the whole ticker was
    reported as `no_source`** — which reads as *the vendor has nothing*.

    ★ It was invisible at inference and fatal at training: the daily run's
    200-day window sat in front of the sub-penny prints.
    """
    from src.data_engine.src.fmp.prices import _minor

    assert _minor(310.245, "USD") == 31025      # HALF_UP, stated once
    assert _minor(1454.445, "USD") == 145445
    assert _minor(211.02, "USD") == 21102       # ordinary prices unchanged
