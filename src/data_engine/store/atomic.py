"""Atomic file store — DE-10, DE-11 (AC-7.19, AC-7.20).

★ WHY THIS MODULE EXISTS AT ALL.
L0 §6.2 says no database, so parquet and JSON on local disk are the whole
persistence layer. **Atomicity is the one property a database gave for free**,
and losing it is not theoretical: a killed write leaves a truncated parquet
whose footer is missing, and the next read fails somewhere unrelated — or
worse, a partially-written JSON parses.

The mechanism is write-temp-then-rename. `os.replace` is atomic within a
filesystem, so a reader sees either the old file or the new one and never a
half-written one. The temp file is created in the SAME directory as the target
precisely so the rename cannot cross a filesystem boundary and silently degrade
into copy-then-delete.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pandas as pd

from src.data_engine.errors import StoreWriteError


def write_parquet(df: pd.DataFrame, path: str | Path) -> Path:
    """Write `df` atomically. Overwrites — DE-11 (except the append-only ledgers).

    ``index=False`` is deliberate and not a default worth trusting: a written
    index becomes a phantom column on read, and CT-7.x declares no index.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".parquet.tmp")
        os.close(fd)
        df.to_parquet(tmp, index=False)
        os.replace(tmp, path)
        tmp = None
        return path
    except Exception as exc:
        raise StoreWriteError(
            f"atomic parquet write to {path} failed: {type(exc).__name__}: {exc}. "
            f"No partial file remains (DE-10)"
        ) from exc
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def write_json(obj, path: str | Path) -> Path:
    """Write `obj` as JSON atomically.

    `sort_keys=True` is what makes DE-11 checkable: two ingests of the same data
    must produce identical BYTES, and dict ordering is otherwise an insertion
    artifact that would differ between runs while the data did not (INV-2).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".json.tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        tmp = None
        return path
    except Exception as exc:
        raise StoreWriteError(
            f"atomic JSON write to {path} failed: {type(exc).__name__}: {exc}"
        ) from exc
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def read_parquet(path: str | Path) -> pd.DataFrame:
    return pd.read_parquet(Path(path))


def read_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
