"""F9 failure modes. Every one is loud (`P5`)."""

from __future__ import annotations


class ThesisSourceError(Exception):
    """Base."""


class UnresolvableTicker(ThesisSourceError):
    """`C5` / `AC-F9.9` — ⚠ an empty thesis is never returned.

    A thesis-shaped object with nothing in it reads downstream as *"analysed and
    found nothing to say"*, which is a different claim from *"could not analyse"*.
    """

    def __init__(self, ticker: str, why: str) -> None:
        super().__init__(f"cannot author a thesis for {ticker!r}: {why} (C5, P5)")


class ClaimContradictsData(ThesisSourceError):
    """`C2` / `AC-F9.3` — ⚠⚠ verification must survive the wrapper.

    ★ The relay already *"re-verifies claims and raises on contradiction"*
    (`QR-20`). A wrapper that caught this and de-rated instead would convert a
    **refusal** into a **discount** — and the whole point of `RA-118` is that a
    claim contradicting our own data is not a low-confidence claim, it is a
    wrong one.
    """


class SpansMissing(ThesisSourceError):
    """`D1` — the transport could not carry evidence spans.

    ⚠ Degraded, and it SAYS so. `QR-16`'s *"earn the confidence back"* depends on
    the spans existing; arriving span-less in silence removes the thing that
    would have earned it.
    """
