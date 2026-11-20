"""Step 9 - Save processed data, JSON summary and a Markdown report."""
from __future__ import annotations

import json
from pathlib import Path

from . import config
from .analysis import generate_insights, risk_label


def _pct(x): return f"{x:.2%}"


def build_report(ticker, summary, bt, crossovers, source, clean_log, image_names) -> str:
    s = summary
    lines = [
        f"# Stock Analysis Report - {ticker}", "",
        f"> {config.DISCLAIMER}", "",
        f"- **Data source:** {source}",
        f"- **Period:** {s['start_date']} to {s['end_date']} ({s['trading_days']} trading days)",
        f"- **Rows cleaned:** {clean_log['rows_raw']} raw -> {clean_log['rows_clean']} clean "
        f"({clean_log['duplicates_removed']} duplicates removed)", "",
        "## Key Insights", "",
    ]
    lines += [f"- {t}" for t in generate_insights(s, ticker)]
    lines += [
        "", "## Performance & Risk Summary", "",
        "| Metric | Value |", "|---|---|",
        f"| Total return | {_pct(s['total_return'])} |",
        f"| Annualised return | {_pct(s['annualized_return'])} |",
        f"| Annualised volatility | {_pct(s['annualized_volatility'])} ({risk_label(s['annualized_volatility'])} risk) |",
        f"| Sharpe ratio (rf = 0) | {s['sharpe_ratio']:.2f} |",
        f"| Max drawdown | {_pct(s['max_drawdown'])} |",
        f"| 1-day 95% VaR (historical) | {_pct(s['var_95_daily'])} |",
        f"| Positive days | {_pct(s['positive_days_pct'])} |",
        f"| Highest close | {s['highest_close']:.2f} on {s['highest_close_date']} |",
        f"| Lowest close | {s['lowest_close']:.2f} on {s['lowest_close_date']} |",
    ]
    if bt:
        p, st, bh = bt["params"], bt["strategy"], bt["buy_and_hold"]
        lines += [
            "", f"## Backtest: SMA {p['fast']}/{p['slow']} Crossover (long-only, {p['fee_bps']} bps fee)", "",
            "| Metric | Strategy | Buy & Hold |", "|---|---|---|",
            f"| Total return | {_pct(st['total_return'])} | {_pct(bh['total_return'])} |",
            f"| Annualised return | {_pct(st['annualized_return'])} | {_pct(bh['annualized_return'])} |",
            f"| Annualised volatility | {_pct(st['annualized_volatility'])} | {_pct(bh['annualized_volatility'])} |",
            f"| Sharpe ratio | {st['sharpe_ratio']:.2f} | {bh['sharpe_ratio']:.2f} |",
            f"| Max drawdown | {_pct(st['max_drawdown'])} | {_pct(bh['max_drawdown'])} |",
            f"| Trades | {st['trades']} | - |",
            f"| Win rate (per trade) | {_pct(st['win_rate'])} | - |",
            f"| Time in market | {_pct(st['time_in_market'])} | 100% |",
        ]
    if crossovers is not None and len(crossovers):
        lines += ["", "## Latest SMA Crossovers", "", "| Date | Close | Signal |", "|---|---|---|"]
        for _, r in crossovers.tail(5).iterrows():
            lines.append(f"| {r['date'].date()} | {r['close']:.2f} | {r['signal']} |")
    if image_names:
        lines += ["", "## Charts", ""]
        lines += [f"![{n}](../images/{n})" for n in image_names]
    lines += ["", "---", f"*{config.DISCLAIMER}*", ""]
    return "\n".join(lines)


def save_outputs(ticker, df, summary, bt, report_md,
                 out_dir: Path = config.OUTPUT_DIR, report_dir: Path = config.REPORTS_DIR) -> dict:
    out_dir, report_dir = Path(out_dir), Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True); report_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "processed_csv": out_dir / f"{ticker}_processed.csv",
        "summary_json": out_dir / f"{ticker}_summary.json",
        "report_md": report_dir / f"{ticker}_report.md",
    }
    df.to_csv(paths["processed_csv"], index=False)
    payload = {"summary": summary}
    if bt:
        payload["backtest"] = {"params": bt["params"], "strategy": bt["strategy"], "buy_and_hold": bt["buy_and_hold"]}
    paths["summary_json"].write_text(json.dumps(payload, indent=2))
    paths["report_md"].write_text(report_md, encoding="utf-8")
    if bt:
        paths["backtest_csv"] = out_dir / f"{ticker}_backtest.csv"
        bt["curve"].to_csv(paths["backtest_csv"], index=False)
    return paths
