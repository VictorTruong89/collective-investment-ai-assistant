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


#: The `Omission` reason for a subject's own source (AC-F13.21) — it leads with the rule.
SUBJECT_ITSELF = ("the subject itself — its own filing is the extractions' evidence, not its "
                  "industry's (F13 D15)")


def own_sources(subject: Subject, sources: list[dict], edgar_sources: dict) -> dict[str, str]:
    """AC-F13.21 — `{source_id: reason}` for each listed EDGAR source that IS the subject.

    ★ Matched by CIK, never by name: a company-IR source has no CIK and is always kept.
    """
    return {s["source_id"]: SUBJECT_ITSELF for s in sources
            if str((edgar_sources.get(s["source_id"]) or {}).get("cik", "")) == subject.cik}
