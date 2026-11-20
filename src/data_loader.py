"""Step 1 - Data collection.

Order of attempts when source="auto":
    1. Yahoo Finance via yfinance (needs internet)
    2. A CSV file (data/<TICKER>.csv or --csv path)
    3. Synthetic demo data (random-walk) so the project ALWAYS runs offline

The returned DataFrame is *raw*; cleaning happens in cleaning.py.
"""
from __future__ import annotations

import datetime as dt
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from . import config


def fetch_yfinance(ticker: str, start: str, end: str | None = None) -> pd.DataFrame:
    """Download daily OHLCV data from Yahoo Finance."""
    import yfinance as yf  # imported here so the project works even if yfinance is missing

    end = end or dt.date.today().isoformat()
    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise ValueError(f"Yahoo Finance returned no data for '{ticker}'.")
    # Newer yfinance versions return MultiIndex columns like ('Close', 'AAPL') -> flatten
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.reset_index()


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV that has at least Date and Close columns."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    return pd.read_csv(path)


def generate_sample_data(
    ticker: str = "DEMO",
    start: str = "2020-01-01",
    end: str | None = None,
    seed: int | None = None,
    start_price: float = 100.0,
) -> pd.DataFrame:
    """Create realistic-looking *synthetic* OHLCV data (geometric random walk).

    Used as an offline fallback and for unit tests. It is NOT real market data.
    """
    end = end or dt.date.today().isoformat()
    rng = np.random.default_rng(seed if seed is not None else zlib.crc32(ticker.encode()))
    dates = pd.bdate_range(start=start, end=end)
    n = len(dates)
    daily_drift, daily_vol = 0.0004, 0.015
    log_ret = rng.normal(daily_drift, daily_vol, n)
    close = start_price * np.exp(np.cumsum(log_ret))
    open_ = np.concatenate([[start_price], close[:-1]]) * (1 + rng.normal(0, 0.003, n))
    spread = np.abs(rng.normal(0, 0.008, n))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    volume = rng.integers(5_000_000, 60_000_000, n)
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": open_.round(2),
            "High": high.round(2),
            "Low": low.round(2),
            "Close": close.round(2),
            "Adj Close": close.round(2),
            "Volume": volume,
        }
    )


def load_data(
    ticker: str = config.DEFAULT_TICKER,
    start: str = config.DEFAULT_START,
    end: str | None = config.DEFAULT_END,
    source: str = "auto",
    csv_path: str | None = None,
) -> tuple[pd.DataFrame, str]:
    """Return (raw_dataframe, description_of_source_used).

    source: "auto" | "yahoo" | "csv" | "sample"
    """
    ticker = ticker.upper().strip()
    default_csv = config.DATA_DIR / f"{ticker}.csv"
    errors: list[str] = []

    if source in ("auto", "yahoo"):
        try:
            return fetch_yfinance(ticker, start, end), "Yahoo Finance (yfinance)"
        except Exception as exc:  # network down, bad ticker, package missing ...
            errors.append(f"Yahoo Finance failed: {exc}")
            if source == "yahoo":
                raise

    if source in ("auto", "csv"):
        path = Path(csv_path) if csv_path else default_csv
        try:
            return load_csv(path), f"CSV file ({path.name})"
        except Exception as exc:
            errors.append(f"CSV failed: {exc}")
            if source == "csv":
                raise

    # Final fallback: synthetic demo data
    for e in errors:
        print(f"[info] {e}")
    print("[info] Using synthetic demo data (random walk) - not real market prices.")
    return generate_sample_data(ticker, start, end), "Synthetic demo data (offline fallback)"
