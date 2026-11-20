# 6-Day Proof-Building Plan

| Day | Do | Commit message | Screenshot |
|---|---|---|---|
| 1 | Setup venv, folders, requirements, `.gitignore`, `config.py` | `chore: project setup` | Folder tree in VS Code, terminal with `pip list` |
| 2 | `data_loader.py` - yfinance, CSV fallback, sample data | `feat: data loader with fallback` | Dataset preview (`df.head()`) |
| 3 | `cleaning.py` + EDA notebook in `notebooks/` | `feat: cleaning and EDA` | Cleaning log, `df.describe()` |
| 4 | `indicators.py`, `analysis.py`, `backtest.py` | `feat: indicators, risk summary, backtest` | Terminal risk summary |
| 5 | `visualize.py`, run `main.py` on a real ticker | `feat: charts` | Closing price, moving average, returns, volatility charts |
| 6 | `report.py`, `app.py`, tests, README | `docs: README, report, dashboard` | Final report, Streamlit dashboard, GitHub repo page |

## Screenshot checklist
Project folder · dataset preview · terminal output · closing price chart · moving average chart · daily returns chart · volatility/risk summary · final report · backtest chart · Streamlit dashboard · GitHub repo preview (README rendered).

## How to explain the simulation
Data arrives (Yahoo or CSV) → cleaned → daily returns show performance → moving averages show trend (price/fast above slow = uptrend) → volatility shows risk → backtest shows what a simple rule would have done after costs → insights are generated from the numbers.
