"""F13 — a thesis on demand: `thesis_for TICKER --as-of DATE`.

★ Plumbing only. Every prompt block, check and commit rule is the one already built and
verified live; this package resolves the inputs for a date, records the chain, and hands
each existing runner the run ids it reads as arguments (`D1`). The runners themselves are
wired in the composition root, `tools/thesis_for.py` (`CA-9`).
"""
