"""Who `thesis_for` may write about — `config/thesis_for.yaml` (AC-F13.5)."""

from __future__ import annotations

from dataclasses import dataclass


class NoPeerSetError(ValueError):
    """A ticker whose industry has no source list — refused, never defaulted (`T2`)."""


@dataclass(frozen=True)
class Subject:
    ticker: str
    name: str
    cik: str
    sector_list: str


def load_subject(ticker: str, config: dict) -> Subject:
    """The subject's declared name, CIK and industry source list.

    ⚠ A ticker absent from the config is REFUSED: its peer set is Victor's to choose
    first, and a thesis over no industry evidence would read the company in a vacuum.
    """
    entry = (config.get("subjects") or {}).get(ticker.upper())
    if not entry:
        raise NoPeerSetError(
            f"{ticker.upper()} has no industry source list in config/thesis_for.yaml. The "
            f"peer set is Victor's to choose first (T2; F13 D2) — nothing is defaulted")
    return Subject(ticker=ticker.upper(), name=entry["name"], cik=str(entry["cik"]),
                   sector_list=entry["sector_list"])
