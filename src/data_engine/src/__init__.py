"""Source adapters — EDGAR and FMP (L4 §1.1, `data_engine/src/{edgar,fmp}`).

★ **D-07 is the only domain permitted to reach an external data API** (ST-3,
L0 §4.3). Any other domain doing so is a defect, not an optimisation — and this
package is the only place in `src/` that holds a URL or an API key.
"""
