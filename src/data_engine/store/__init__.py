"""Parquet + JSON read/write, atomic (L4 §1.3 — `store.py`, not `repository.py`)."""

from src.data_engine.store.atomic import read_json, read_parquet, write_json, write_parquet

__all__ = ["read_json", "read_parquet", "write_json", "write_parquet"]
