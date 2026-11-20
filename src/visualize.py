"""Step 8 - Charts. Every plot_* function RETURNS a matplotlib Figure so the same
code works for saved PNGs (main.py) and the Streamlit dashboard (app.py)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display needed (works on servers / WSL)
import matplotlib.pyplot as plt
import numpy as np

from . import config

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})


def plot_price(df, ticker):
    fig, (ax, axv) = plt.subplots(2, 1, figsize=(11, 6), sharex=True,
                                  gridspec_kw={"height_ratios": [3, 1]})
    ax.plot(df["date"], df["close"], color="#1f77b4", lw=1.4, label="Close")
    hi, lo = df["close"].idxmax(), df["close"].idxmin()
    ax.scatter(df.loc[hi, "date"], df.loc[hi, "close"], color="green", zorder=5, label="Highest close")
    ax.scatter(df.loc[lo, "date"], df.loc[lo, "close"], color="red", zorder=5, label="Lowest close")
    ax.set_title(f"{ticker} - Closing Price"); ax.set_ylabel("Price"); ax.legend()
    if "volume" in df.columns:
        axv.bar(df["date"], df["volume"], color="#999999", width=1.0)
        axv.set_ylabel("Volume")
    fig.tight_layout()
    return fig


def plot_moving_averages(df, ticker, fast=config.SMA_FAST, slow=config.SMA_SLOW):
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["date"], df["close"], color="#bbbbbb", lw=1, label="Close")
    ax.plot(df["date"], df[f"sma_{fast}"], color="#ff7f0e", lw=1.5, label=f"SMA {fast}")
    ax.plot(df["date"], df[f"sma_{slow}"], color="#2ca02c", lw=1.5, label=f"SMA {slow}")
    ax.set_title(f"{ticker} - Moving Averages (trend)"); ax.set_ylabel("Price"); ax.legend()
    fig.tight_layout()
    return fig


def plot_returns(df, ticker):
    r = df["daily_return"].dropna() * 100
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.5))
    a1.plot(df["date"], df["daily_return"] * 100, color="#555555", lw=0.7)
    a1.axhline(0, color="black", lw=0.8)
    a1.set_title("Daily Returns (%)"); a1.set_ylabel("%")
    a2.hist(r, bins=50, color="#1f77b4", alpha=0.8, edgecolor="white")
    a2.axvline(r.mean(), color="red", ls="--", label=f"Mean {r.mean():.2f}%")
    a2.axvline(np.percentile(r, 5), color="orange", ls="--", label=f"5th pct {np.percentile(r, 5):.2f}%")
    a2.set_title("Return Distribution"); a2.set_xlabel("Daily return (%)"); a2.legend()
    fig.suptitle(f"{ticker} - Return Analysis"); fig.tight_layout()
    return fig


def plot_volatility(df, ticker):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(df["date"], df["rolling_volatility"] * 100, color="#d62728", lw=1.3)
    ax.set_title(f"{ticker} - Rolling {config.VOL_WINDOW}-day Annualised Volatility (risk)")
    ax.set_ylabel("Volatility (%)")
    fig.tight_layout()
    return fig


def plot_drawdown(df, ticker):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.fill_between(df["date"], df["drawdown"] * 100, 0, color="#d62728", alpha=0.4)
    ax.set_title(f"{ticker} - Drawdown from Peak"); ax.set_ylabel("%")
    fig.tight_layout()
    return fig


def plot_rsi_macd(df, ticker):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    a1.plot(df["date"], df["rsi"], color="#9467bd", lw=1.2)
    a1.axhline(70, color="red", ls="--", lw=0.8); a1.axhline(30, color="green", ls="--", lw=0.8)
    a1.set_ylim(0, 100); a1.set_title(f"{ticker} - RSI (14)")
    colors = np.where(df["macd_hist"] >= 0, "#2ca02c", "#d62728")
    a2.bar(df["date"], df["macd_hist"], color=colors, width=1.0, alpha=0.6)
    a2.plot(df["date"], df["macd"], color="#1f77b4", lw=1.1, label="MACD")
    a2.plot(df["date"], df["macd_signal"], color="#ff7f0e", lw=1.1, label="Signal")
    a2.set_title("MACD"); a2.legend()
    fig.tight_layout()
    return fig


def plot_bollinger(df, ticker):
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["date"], df["close"], color="#1f77b4", lw=1.2, label="Close")
    ax.plot(df["date"], df["bb_mid"], color="#ff7f0e", lw=1, label="SMA 20")
    ax.fill_between(df["date"], df["bb_lower"], df["bb_upper"], color="#ff7f0e", alpha=0.15, label="Bollinger band")
    ax.set_title(f"{ticker} - Bollinger Bands"); ax.legend()
    fig.tight_layout()
    return fig


def plot_backtest(bt, ticker):
    c = bt["curve"]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(c["date"], c["buyhold_equity"], color="#888888", lw=1.4, label="Buy & hold")
    ax.plot(c["date"], c["strategy_equity"], color="#2ca02c", lw=1.6,
            label=f"SMA {bt['params']['fast']}/{bt['params']['slow']} strategy")
    ax.set_title(f"{ticker} - Backtest: growth of 1.00 invested (educational)")
    ax.set_ylabel("Equity"); ax.legend()
    fig.tight_layout()
    return fig


def save_all_charts(df, bt, ticker, out_dir: Path = config.IMAGES_DIR) -> list[Path]:
    """Save every chart as a PNG and return the file paths."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    charts = {
        "01_closing_price": plot_price(df, ticker),
        "02_moving_averages": plot_moving_averages(df, ticker),
        "03_daily_returns": plot_returns(df, ticker),
        "04_volatility": plot_volatility(df, ticker),
        "05_drawdown": plot_drawdown(df, ticker),
        "06_rsi_macd": plot_rsi_macd(df, ticker),
        "07_bollinger_bands": plot_bollinger(df, ticker),
    }
    if bt is not None:
        charts["08_backtest"] = plot_backtest(bt, ticker)
    paths = []
    for name, fig in charts.items():
        p = out_dir / f"{ticker}_{name}.png"
        fig.savefig(p, bbox_inches="tight"); plt.close(fig); paths.append(p)
    return paths
