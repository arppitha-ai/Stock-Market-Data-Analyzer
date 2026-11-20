"""Stock Market Data Analyzer - command-line entry point.

Examples
--------
python main.py                              # AAPL, Yahoo -> CSV -> demo-data fallback
python main.py --ticker TCS.NS --start 2021-01-01
python main.py --source csv --csv data/sample_stock.csv --ticker DEMO
python main.py --source sample              # always offline

Educational project - NOT financial advice.
"""
from __future__ import annotations

import argparse

from src import config
from src.analysis import find_crossovers, generate_insights, risk_label, summarize
from src.backtest import run_sma_backtest
from src.cleaning import clean_data
from src.data_loader import load_data
from src.indicators import add_all_indicators
from src.report import build_report, save_outputs
from src.visualize import save_all_charts


def parse_args():
    p = argparse.ArgumentParser(description="Stock Market Data Analyzer (educational)")
    p.add_argument("--ticker", default=config.DEFAULT_TICKER, help="e.g. AAPL, MSFT, TCS.NS, RELIANCE.NS")
    p.add_argument("--start", default=config.DEFAULT_START, help="YYYY-MM-DD")
    p.add_argument("--end", default=config.DEFAULT_END, help="YYYY-MM-DD (default: today)")
    p.add_argument("--source", choices=["auto", "yahoo", "csv", "sample"], default="auto")
    p.add_argument("--csv", default=None, help="path to a CSV with Date + Close (+OHLCV) columns")
    p.add_argument("--fast", type=int, default=config.SMA_FAST)
    p.add_argument("--slow", type=int, default=config.SMA_SLOW)
    p.add_argument("--fee-bps", type=float, default=config.FEE_BPS)
    p.add_argument("--no-charts", action="store_true")
    return p.parse_args()


def run(args) -> None:
    ticker = args.ticker.upper()
    print("=" * 62)
    print(f" STOCK MARKET DATA ANALYZER  |  {ticker}")
    print("=" * 62)

    raw, source = load_data(ticker, args.start, args.end, args.source, args.csv)
    print(f"[1/6] Data loaded from: {source}  ({len(raw)} rows)")

    df, log = clean_data(raw, args.start, args.end)
    print(f"[2/6] Cleaned: {log['rows_raw']} -> {log['rows_clean']} rows "
          f"(duplicates removed: {log['duplicates_removed']}, candles fixed: {log.get('candles_fixed', 0)})")
    print("\nDataset preview:")
    print(df[["date", "open", "high", "low", "close", "volume"]].head().to_string(index=False))

    df = add_all_indicators(df, args.fast, args.slow)
    print(f"\n[3/6] Indicators added: returns, SMA {args.fast}/{args.slow}, EMA, RSI, MACD, Bollinger, volatility, drawdown")

    summary = summarize(df, args.fast, args.slow)
    crossovers = find_crossovers(df, args.fast, args.slow)
    print("[4/6] Summary computed")

    bt = run_sma_backtest(df, args.fast, args.slow, args.fee_bps)
    print("[5/6] Backtest finished")

    image_names = []
    if not args.no_charts:
        paths = save_all_charts(df, bt, ticker)
        image_names = [p.name for p in paths]
        print(f"[6/6] {len(paths)} charts saved to images/")

    report_md = build_report(ticker, summary, bt, crossovers, source, log, image_names)
    paths = save_outputs(ticker, df, summary, bt, report_md)

    s = summary
    print("\n" + "-" * 62)
    print(" RISK & RETURN SUMMARY")
    print("-" * 62)
    print(f" Period               : {s['start_date']} -> {s['end_date']}")
    print(f" Total return         : {s['total_return']:+.2%}")
    print(f" Annualised return    : {s['annualized_return']:+.2%}")
    print(f" Annualised volatility: {s['annualized_volatility']:.2%}  ({risk_label(s['annualized_volatility'])} risk)")
    print(f" Sharpe ratio         : {s['sharpe_ratio']:.2f}")
    print(f" Max drawdown         : {s['max_drawdown']:.2%}")
    print(f" Highest close        : {s['highest_close']:.2f} on {s['highest_close_date']}")
    print(f" Lowest close         : {s['lowest_close']:.2f} on {s['lowest_close_date']}")
    print(f" Current trend        : {s['current_trend']}")
    st, bh = bt["strategy"], bt["buy_and_hold"]
    print(f"\n SMA {args.fast}/{args.slow} backtest vs buy & hold")
    print(f"   Strategy : {st['total_return']:+.2%}  | trades {st['trades']} | win rate {st['win_rate']:.0%}")
    print(f"   Buy&Hold : {bh['total_return']:+.2%}")
    print("\n INSIGHTS")
    for line in generate_insights(s, ticker):
        print(f"  * {line}")
    print("\n Files created:")
    for k, v in paths.items():
        print(f"   {k:14s} -> {v.relative_to(config.ROOT_DIR)}")
    print(f"\n {config.DISCLAIMER}")


if __name__ == "__main__":
    run(parse_args())
