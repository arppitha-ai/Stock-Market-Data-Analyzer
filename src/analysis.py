"""Step 6 - Performance & risk summary + plain-English insights."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def summarize(df: pd.DataFrame, fast=config.SMA_FAST, slow=config.SMA_SLOW) -> dict:
    """Compute headline statistics from an indicator-enriched DataFrame."""
    r = df["daily_return"].dropna()
    years = max((df["date"].iloc[-1] - df["date"].iloc[0]).days / 365.25, 1e-9)
    first, last = df["adj_close"].iloc[0], df["adj_close"].iloc[-1]
    total_return = last / first - 1
    ann_return = (last / first) ** (1 / years) - 1
    ann_vol = r.std() * np.sqrt(config.TRADING_DAYS)
    sharpe = (ann_return - config.RISK_FREE_RATE) / ann_vol if ann_vol > 0 else float("nan")
    hi_i, lo_i = df["close"].idxmax(), df["close"].idxmin()
    best_i, worst_i = df["daily_return"].idxmax(), df["daily_return"].idxmin()
    latest = df.iloc[-1]

    return {
        "start_date": df["date"].iloc[0].date().isoformat(),
        "end_date": df["date"].iloc[-1].date().isoformat(),
        "trading_days": int(len(df)),
        "start_price": float(first),
        "end_price": float(last),
        "total_return": float(total_return),
        "annualized_return": float(ann_return),
        "annualized_volatility": float(ann_vol),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(df["drawdown"].min()),
        "var_95_daily": float(np.percentile(r, 5)),        # worst day in 20 (historical)
        "positive_days_pct": float((r > 0).mean()),
        "highest_close": float(df.loc[hi_i, "close"]),
        "highest_close_date": df.loc[hi_i, "date"].date().isoformat(),
        "lowest_close": float(df.loc[lo_i, "close"]),
        "lowest_close_date": df.loc[lo_i, "date"].date().isoformat(),
        "best_day_return": float(df.loc[best_i, "daily_return"]),
        "best_day_date": df.loc[best_i, "date"].date().isoformat(),
        "worst_day_return": float(df.loc[worst_i, "daily_return"]),
        "worst_day_date": df.loc[worst_i, "date"].date().isoformat(),
        "current_trend": str(latest["trend"]),
        "latest_rsi": None if pd.isna(latest["rsi"]) else float(latest["rsi"]),
        "latest_volatility": None if pd.isna(latest["rolling_volatility"]) else float(latest["rolling_volatility"]),
    }


def risk_label(ann_vol: float) -> str:
    """Rough, beginner-friendly risk bucket based on annualised volatility."""
    if ann_vol < 0.20:
        return "Low"
    if ann_vol < 0.35:
        return "Moderate"
    return "High"


def find_crossovers(df, fast=config.SMA_FAST, slow=config.SMA_SLOW) -> pd.DataFrame:
    """Dates where the fast SMA crosses the slow SMA (golden / death cross style)."""
    f, s = df[f"sma_{fast}"], df[f"sma_{slow}"]
    above = (f > s).astype(int)
    valid = f.notna() & s.notna()
    change = above.diff().where(valid & valid.shift(1, fill_value=False))
    events = df.loc[change.abs() == 1, ["date", "close"]].copy()
    events["signal"] = np.where(change[events.index] == 1, "BUY (bullish cross)", "SELL (bearish cross)")
    return events.reset_index(drop=True)


def generate_insights(summary: dict, ticker: str) -> list[str]:
    """Turn the numbers into plain-English bullet points."""
    s = summary
    out = [
        f"{ticker} moved from {s['start_price']:.2f} to {s['end_price']:.2f} "
        f"({s['total_return']:+.1%}) between {s['start_date']} and {s['end_date']}, "
        f"about {s['annualized_return']:+.1%} per year.",
        f"Annualised volatility is {s['annualized_volatility']:.1%}, a "
        f"{risk_label(s['annualized_volatility']).lower()}-risk profile by this project's simple scale.",
        f"The deepest peak-to-trough fall (max drawdown) was {s['max_drawdown']:.1%}.",
        f"On a typical bad day (historical 95% VaR) the stock fell about {abs(s['var_95_daily']):.1%} or more "
        f"on roughly 1 day in 20.",
        f"Best day: {s['best_day_return']:+.1%} on {s['best_day_date']}; "
        f"worst day: {s['worst_day_return']:+.1%} on {s['worst_day_date']}.",
        f"Highest close {s['highest_close']:.2f} ({s['highest_close_date']}); "
        f"lowest close {s['lowest_close']:.2f} ({s['lowest_close_date']}).",
        f"Current trend by the SMA rules: {s['current_trend']}.",
    ]
    rsi = s["latest_rsi"]
    if rsi is not None:
        zone = "overbought (>70)" if rsi > 70 else "oversold (<30)" if rsi < 30 else "neutral (30-70)"
        out.append(f"Latest RSI is {rsi:.1f}, which is {zone}.")
    return out
