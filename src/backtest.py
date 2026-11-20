"""Step 7 - Vectorised backtest of a long-only SMA crossover strategy.

Rule: be invested (1) when SMA_fast > SMA_slow, otherwise stay in cash (0).
The signal is shifted one day so we trade on *tomorrow's* return - this avoids
"look-ahead bias", the classic beginner backtesting mistake.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def run_sma_backtest(df, fast=config.SMA_FAST, slow=config.SMA_SLOW, fee_bps=config.FEE_BPS) -> dict:
    d = df.dropna(subset=[f"sma_{fast}", f"sma_{slow}"]).reset_index(drop=True)
    if len(d) < 30:
        raise ValueError("Not enough data after SMA warm-up to run a backtest.")

    signal = (d[f"sma_{fast}"] > d[f"sma_{slow}"]).astype(int)
    position = signal.shift(1).fillna(0)                      # act the NEXT day
    ret = d["adj_close"].pct_change().fillna(0.0)
    turns = position.diff().abs().fillna(position.abs())      # 1 when we enter/exit
    cost = turns * (fee_bps / 10_000)
    strat = position * ret - cost

    out = pd.DataFrame({
        "date": d["date"],
        "position": position,
        "strategy_return": strat,
        "buyhold_return": ret,
    })
    out["strategy_equity"] = (1 + out["strategy_return"]).cumprod()
    out["buyhold_equity"] = (1 + out["buyhold_return"]).cumprod()

    # Per-trade results: each run of consecutive position==1 days is one trade
    trade_id = (position.diff().fillna(position) == 1).cumsum().where(position == 1)
    trade_returns = (1 + strat[position == 1]).groupby(trade_id[position == 1]).prod() - 1
    n_trades = int(len(trade_returns))

    def stats(equity: pd.Series, rets: pd.Series) -> dict:
        years = max(len(rets) / config.TRADING_DAYS, 1e-9)
        total = equity.iloc[-1] - 1
        vol = rets.std() * np.sqrt(config.TRADING_DAYS)
        ann = equity.iloc[-1] ** (1 / years) - 1
        return {
            "total_return": float(total),
            "annualized_return": float(ann),
            "annualized_volatility": float(vol),
            "sharpe_ratio": float(ann / vol) if vol > 0 else float("nan"),
            "max_drawdown": float((equity / equity.cummax() - 1).min()),
        }

    s_stats = stats(out["strategy_equity"], out["strategy_return"])
    s_stats.update({
        "trades": n_trades,
        "win_rate": float((trade_returns > 0).mean()) if n_trades else 0.0,
        "time_in_market": float(position.mean()),
    })
    return {
        "curve": out,
        "strategy": s_stats,
        "buy_and_hold": stats(out["buyhold_equity"], out["buyhold_return"]),
        "params": {"fast": fast, "slow": slow, "fee_bps": fee_bps},
    }
