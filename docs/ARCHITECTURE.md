# Architecture

```
 INPUT                    PROCESSING                                   OUTPUT
┌──────────────┐   ┌────────────────────────────────────────┐   ┌──────────────────────┐
│ ticker       │   │ data_loader.py  fetch / CSV / sample   │   │ images/*.png charts  │
│ date range   │──▶│ cleaning.py     validate + fix         │──▶│ reports/*_report.md  │
│ source/CSV   │   │ indicators.py   returns, SMA, RSI...   │   │ outputs/*.csv, .json │
│ SMA, fee     │   │ analysis.py     risk summary, insights │   │ terminal summary     │
└──────────────┘   │ backtest.py     SMA cross vs buy&hold  │   │ Streamlit dashboard  │
                   └────────────────────────────────────────┘   └──────────────────────┘
```

## Data flow
1. **Collect** - `load_data()` tries Yahoo Finance, then a CSV, then synthetic data.
2. **Clean** - lowercase columns, parse/sort dates, drop duplicates, coerce numbers, forward-fill gaps, drop non-positive prices, fix OHLC.
3. **Features** - daily/log returns → SMA/EMA → rolling volatility → RSI → MACD → Bollinger → drawdown → trend label.
4. **Analyse** - total/annualised return, volatility, Sharpe, max drawdown, VaR, extremes, crossovers.
5. **Backtest** - signal = SMA fast > SMA slow; position shifted one day; fees on every entry/exit.
6. **Report** - PNG charts, Markdown report, JSON summary, CSVs.

## Key formulas
- Daily return = P_t / P_(t-1) − 1
- Annualised volatility = std(daily returns) × √252
- Sharpe = annualised return / annualised volatility (risk-free = 0)
- Max drawdown = min(price / running peak − 1)
- RSI = 100 − 100 / (1 + avg gain / avg loss), Wilder smoothing, 14 days
