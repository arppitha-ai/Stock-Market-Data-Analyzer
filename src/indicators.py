"""Steps 4-5 - Returns, moving averages, volatility and technical indicators.

Everything is written in plain pandas/NumPy (no extra TA library) so you can
explain every formula in an interview.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Daily % return, log return, cumulative return."""
    out = df.copy()
    out["daily_return"] = out["adj_close"].pct_change()
    out["log_return"] = np.log(out["adj_close"] / out["adj_close"].shift(1))
    out["cumulative_return"] = (1 + out["daily_return"].fillna(0)).cumprod() - 1
    return out


def add_moving_averages(df, fast=config.SMA_FAST, slow=config.SMA_SLOW) -> pd.DataFrame:
    """Simple (SMA) and exponential (EMA) moving averages of the close."""
    out = df.copy()
    out[f"sma_{fast}"] = out["close"].rolling(fast).mean()
    out[f"sma_{slow}"] = out["close"].rolling(slow).mean()
    out[f"ema_{fast}"] = out["close"].ewm(span=fast, adjust=False).mean()
    return out


def add_volatility(df, window=config.VOL_WINDOW) -> pd.DataFrame:
    """Rolling annualised volatility = std(daily returns) * sqrt(252)."""
    out = df.copy()
    out["rolling_volatility"] = out["daily_return"].rolling(window).std() * np.sqrt(config.TRADING_DAYS)
    return out


def add_rsi(df, window=config.RSI_WINDOW) -> pd.DataFrame:
    """Relative Strength Index (Wilder smoothing). >70 overbought, <30 oversold."""
    out = df.copy()
    delta = out["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out["rsi"] = (100 - 100 / (1 + rs)).fillna(100.0).where(avg_gain.notna())
    return out


def add_macd(df, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """MACD = EMA12 - EMA26; signal = EMA9 of MACD; histogram = MACD - signal."""
    out = df.copy()
    ema_fast = out["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = out["close"].ewm(span=slow, adjust=False).mean()
    out["macd"] = ema_fast - ema_slow
    out["macd_signal"] = out["macd"].ewm(span=signal, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]
    return out


def add_bollinger(df, window=config.BB_WINDOW, n_std=2) -> pd.DataFrame:
    """Bollinger Bands = SMA(20) +/- 2 standard deviations."""
    out = df.copy()
    mid = out["close"].rolling(window).mean()
    std = out["close"].rolling(window).std()
    out["bb_mid"], out["bb_upper"], out["bb_lower"] = mid, mid + n_std * std, mid - n_std * std
    return out


def add_drawdown(df) -> pd.DataFrame:
    """Drawdown = how far price is below its previous all-time peak."""
    out = df.copy()
    peak = out["adj_close"].cummax()
    out["drawdown"] = out["adj_close"] / peak - 1
    return out


def add_trend(df, fast=config.SMA_FAST, slow=config.SMA_SLOW) -> pd.DataFrame:
    """Label each day Uptrend / Downtrend / Sideways using price and the two SMAs."""
    out = df.copy()
    f, s = out[f"sma_{fast}"], out[f"sma_{slow}"]
    up = (out["close"] > s) & (f > s)
    down = (out["close"] < s) & (f < s)
    out["trend"] = np.select([up, down], ["Uptrend", "Downtrend"], default="Sideways")
    out.loc[s.isna(), "trend"] = "n/a"
    return out


def add_all_indicators(df, fast=config.SMA_FAST, slow=config.SMA_SLOW) -> pd.DataFrame:
    """Run every indicator step in the right order."""
    out = add_returns(df)
    out = add_moving_averages(out, fast, slow)
    out = add_volatility(out)
    out = add_rsi(out)
    out = add_macd(out)
    out = add_bollinger(out)
    out = add_drawdown(out)
    out = add_trend(out, fast, slow)
    return out
