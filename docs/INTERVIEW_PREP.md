# Interview Preparation

**1. Explain your project.**
I built a Python Stock Market Data Analyzer. It loads daily price data from Yahoo Finance (or a CSV if offline), cleans it, and calculates daily returns, moving averages, volatility, RSI, MACD and Bollinger Bands. It summarises return and risk (volatility, Sharpe ratio, max drawdown), backtests a 20/50-day moving-average crossover strategy against buy-and-hold including trading costs, and generates charts, a Markdown report and a Streamlit dashboard. It is modular, tested, and on GitHub.

**2. What problem does it solve?**
It replaces manual price checking with a repeatable pipeline that shows trend, risk and historical performance quickly and consistently.

**3. Why did you use moving averages?**
They smooth daily noise. When the 20-day average is above the 50-day average and price is above both, the trend is up; the reverse is a downtrend. Crossovers also give simple, testable rules.

**4. What is volatility and how did you calculate it?**
Volatility is how much returns fluctuate - a proxy for risk. I took the standard deviation of daily returns and multiplied by √252 to annualise it.

**5. What is the difference between price, return and cumulative return?**
Price is the level. Return is the percentage change between days. Cumulative return compounds daily returns to show total growth since the start.

**6. What is max drawdown?**
The largest fall from a previous peak to a later low. It shows the worst loss an investor would have experienced.

**7. How did you avoid look-ahead bias in the backtest?**
The signal is computed from today's close but the position is shifted by one day, so the strategy only earns tomorrow's return. Without that shift, results look unrealistically good.

**8. How did you handle missing or bad data?**
I standardised column names, removed duplicate dates, coerced values to numeric, forward-filled small gaps, dropped rows with no close or non-positive prices, and fixed inconsistent high/low values. A cleaning log reports what changed.

**9. What are the limitations?**
It uses only price data, daily candles, one stock at a time and a very simple strategy. Backtests ignore slippage, taxes and liquidity, and past performance does not predict the future. The bundled sample CSV is synthetic, so real conclusions need real data.

**10. How would you improve it?**
Store data in SQLite/Parquet, add a FastAPI layer, multi-stock and portfolio analysis, walk-forward validation, risk controls like stop-losses, and RSI/Bollinger alerts.

## HR explanation (30 seconds)
"I wanted proof that I can work with real-world financial data, so I built a tool that downloads stock prices, finds trends, measures risk and tests a simple trading rule, then presents everything in charts and a dashboard. It taught me data cleaning, analysis, testing and clear communication of results."

## Non-technical explanation
"It studies past stock prices and shows, in simple charts, whether a stock has been rising or falling, how bumpy the ride was, and how a basic buy/sell rule would have done."

## Technical one-liner
"Modular pandas pipeline: yfinance/CSV ingestion → validation/cleaning → vectorised indicators → risk metrics → cost-aware, look-ahead-safe SMA backtest → Matplotlib/Streamlit reporting, with unit tests."
