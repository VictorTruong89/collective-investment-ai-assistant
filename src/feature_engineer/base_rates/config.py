"""`CT-F11.1` / `CT-F11.3` — the declared class and the published table (`AC-F11.1`, `AC-F11.7`).

★ Both are config, never code: the members are Victor's choice (`D1`, `D3`), and the
published figures are transcribed from the document (`D5`) — a loader is the only thing
here, and it refuses what it cannot trust.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass

import yaml

from src.feature_engineer.errors import AssumptionsMutatedError

REPO = pathlib.Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO / "config/reference_class"

_HASHED = ("name", "version", "decided_by", "members", "excluded")


def content_hash(doc: dict) -> str:
    payload = json.dumps({k: doc[k] for k in _HASHED}, sort_keys=True,
                         separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Member:
    label: str
    name: str
    cik: str
    role: str
    year_from: int | None
    year_to: int | None
    why: str


@dataclass(frozen=True, slots=True)
class ReferenceClass:
    name: str
    version: int
    content_hash: str
    decided_by: str
    members: tuple[Member, ...]
    excluded: tuple[dict, ...]

    def cite(self) -> dict:
        return {"name": self.name, "version": self.version, "content_hash": self.content_hash}

    def ranges(self) -> dict[str, tuple[int | None, int | None]]:
        return {m.label: (m.year_from, m.year_to) for m in self.members}


def load_class(path) -> ReferenceClass:
    """Refuses a value changed under an unchanged version, and any entry without `why`."""
    doc = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    expected = content_hash(doc)
    if doc.get("content_hash") != expected:
        raise AssumptionsMutatedError(
            f"{path}: {doc.get('name')}@v{doc.get('version')} content hash "
            f"{doc.get('content_hash')!r} does not match its values ({expected}) — a value "
            f"changed without a version change (F11 AC-F11.1)")
    for entry in [*doc["members"], *doc.get("excluded", [])]:
        if not str(entry.get("why") or "").strip():
            raise ValueError(f"{path}: {entry.get('name')!r} carries no `why` (F11 CT-F11.1)")
    members = tuple(Member(m["label"], m["name"], str(m["cik"]), m["role"],
                           m["years"]["from"], m["years"]["to"], m["why"])
                    for m in doc["members"])
    return ReferenceClass(doc["name"], int(doc["version"]), expected, doc["decided_by"],
                          members, tuple(doc.get("excluded", [])))


def load_published_class(name: str, version: int) -> ReferenceClass:
    return load_class(CONFIG_DIR / f"{name}_v{version}.yaml")


@dataclass(frozen=True, slots=True)
class PublishedTable:
    source: dict
    measure: str
    reference_class: str
    horizons: tuple[dict, ...]


def load_published_table(slug: str, *, root=CONFIG_DIR) -> PublishedTable:
    """`AC-F11.7` — every horizon carries both pages, and its bins sum to its total."""
    path = pathlib.Path(root) / f"published_{slug}.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    for h in doc["horizons"]:
        for key in ("page", "rates_page"):
            page = h.get(key) or {}
            if not (page.get("printed") and page.get("pdf")):
                raise ValueError(f"{path}: {h.get('years')}-year horizon has no {key} — a "
                                 f"published figure is cited to its page or not used (P5)")
        counted = sum(int(b["observations"]) for b in h["bins"])
        if counted != int(h["total"]):
            raise ValueError(f"{path}: {h['years']}-year bins sum to {counted}, not the "
                             f"printed total {h['total']} — a transcription error")
    return PublishedTable(doc["source"], doc["measure"], doc["reference_class"],
                          tuple(doc["horizons"]))
