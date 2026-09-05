#!/usr/bin/env python3
"""
debug_inspect_data.py

Standalone debugging script to inspect:
    - Raw price data
    - Feature-engineered data
    - Latest available dates
    - Missing tickers
    - Feature completeness
    - MODEL_FEATURES alignment

Run:
    python debug_inspect_data.py
"""

from pathlib import Path
import pandas as pd
import sys
import yaml

# Ensure pipeline is importable
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.ohlcv.dataset import DataLoader, OhlcvFeatureEngineer, MODEL_FEATURES
from pipeline.utils.logger import *
from pipeline.utils.utils import *


def main():
    print("\n=== DEBUG: Inspecting Input Data ===\n")

    config = load_config()

    # ------------------------------------------------------------
    # 1. Load raw price data
    # ------------------------------------------------------------
    loader = DataLoader(config)
    df_prices = loader.load_price_data()

    print("Raw price data:")
    print(df_prices.head())
    print(df_prices.tail())
    print("\nRaw price date range:", df_prices["date"].min(), "→", df_prices["date"].max())
    print("Tickers:", sorted(df_prices["ticker"].unique()))
    print("Rows:", len(df_prices))

    # ------------------------------------------------------------
    # 2. Build features
    # ------------------------------------------------------------
    fe = OhlcvFeatureEngineer(config)
    df_features = fe.ohlcv_build_features(df_prices)

    print("\nFeature-engineered data:")
    print(df_features.head())
    print(df_features.tail())
    print("\nFeature date range:", df_features["date"].min(), "→", df_features["date"].max())
    print("Rows:", len(df_features))

    # ------------------------------------------------------------
    # 3. Check for missing MODEL_FEATURES
    # ------------------------------------------------------------
    missing = [f for f in MODEL_FEATURES if f not in df_features.columns]
    if missing:
        print("\n❌ Missing MODEL_FEATURES:", missing)
    else:
        print("\n✅ All MODEL_FEATURES present.")

    # ------------------------------------------------------------
    # 4. Inspect the latest date
    # ------------------------------------------------------------
    latest_date = df_features["date"].max()
    df_today = df_features[df_features["date"] == latest_date]

    print("\nLatest feature date:", latest_date)
    print("Rows for latest date:", len(df_today))
    print(df_today[["ticker"] + MODEL_FEATURES].head())

    # ------------------------------------------------------------
    # 5. Check for NaNs in latest date
    # ------------------------------------------------------------
    nan_counts = df_today[MODEL_FEATURES].isna().sum()
    print("\nNaN counts in MODEL_FEATURES for latest date:")
    print(nan_counts[nan_counts > 0])

    print("\n=== DEBUG COMPLETE ===\n")


if __name__ == "__main__":
    main()
