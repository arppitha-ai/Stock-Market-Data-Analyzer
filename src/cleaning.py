"""Step 2 - Data cleaning: make raw data safe for analysis."""
from __future__ import annotations

import pandas as pd

REQUIRED = ["date", "close"]
PRICE_COLS = ["open", "high", "low", "close", "adj_close"]


def clean_data(raw: pd.DataFrame, start: str | None = None, end: str | None = None):
    """Clean raw OHLCV data. Returns (clean_df, log_dict)."""
    df = raw.copy()
    log = {"rows_raw": len(df)}

    # 1. Standardise column names: "Adj Close" -> "adj_close"
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    if "datetime" in df.columns and "date" not in df.columns:
        df = df.rename(columns={"datetime": "date"})
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Data must contain columns {REQUIRED}; missing {missing}")
    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]

    # 2. Parse dates, sort, drop duplicate days
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    before = len(df)
    df = df.drop_duplicates(subset="date", keep="last")
    log["duplicates_removed"] = before - len(df)

    # 3. Force numeric types (bad text becomes NaN instead of crashing)
    for col in PRICE_COLS + ["volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Optional date window (useful when a CSV holds more history than requested)
    if start:
        df = df[df["date"] >= pd.to_datetime(start)]
    if end:
        df = df[df["date"] <= pd.to_datetime(end)]

    # 5. Missing values: forward-fill small gaps, drop rows with no close at all
    log["missing_cells_before"] = int(df.isna().sum().sum())
    df[PRICE_COLS] = df[[c for c in PRICE_COLS if c in df.columns]].ffill()
    df = df.dropna(subset=["close"])

    # 6. Remove impossible prices (<= 0)
    bad = (df["close"] <= 0)
    log["non_positive_prices_removed"] = int(bad.sum())
    df = df[~bad]

    # 7. Fix inconsistent candles (high must be the highest, low the lowest)
    if {"open", "high", "low"}.issubset(df.columns):
        hi = df[["open", "high", "low", "close"]].max(axis=1)
        lo = df[["open", "high", "low", "close"]].min(axis=1)
        log["candles_fixed"] = int(((df["high"] < hi) | (df["low"] > lo)).sum())
        df["high"], df["low"] = hi, lo

    df = df.reset_index(drop=True)
    log["rows_clean"] = len(df)
    if len(df) < 60:
        raise ValueError(f"Only {len(df)} usable rows - need at least 60 for indicators.")
    return df, log
