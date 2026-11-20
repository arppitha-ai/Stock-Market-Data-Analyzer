# GitHub Upload Steps

**Repo name:** `Stock-Market-Data-Analyzer`
**Description:** Python tool that analyses stock prices - returns, moving averages, volatility, RSI/MACD, SMA backtest, charts, reports and a Streamlit dashboard. Educational, not financial advice.
**Topics/tags:** `python` `pandas` `numpy` `matplotlib` `yfinance` `streamlit` `stock-market` `data-analysis` `finance` `fintech` `backtesting` `technical-analysis` `data-visualization` `portfolio-project`

```bash
cd Stock-Market-Data-Analyzer
git init
git add .
git commit -m "feat: initial project structure and data loader"
git branch -M main
# create an EMPTY repo on github.com first (no README/.gitignore), then:
git remote add origin https://github.com/arppitha-ai/Stock-Market-Data-Analyzer.git
git push -u origin main
```
Later updates: `git add . && git commit -m "message" && git push`

If GitHub asks for a password, use a **Personal Access Token** (Settings → Developer settings → Tokens) or SSH keys.

**Before pushing, run with a real ticker** (`python main.py --ticker AAPL`) and commit the real charts from `images/` and the report from `reports/`. Outputs in `outputs/` are git-ignored on purpose.

## Good commit messages
`chore: set up venv and requirements` · `feat: add yfinance loader with CSV fallback` · `feat: data cleaning` · `feat: returns, SMA, volatility` · `feat: RSI, MACD, Bollinger` · `feat: SMA crossover backtest` · `feat: charts and report` · `feat: streamlit dashboard` · `test: unit tests` · `docs: README and screenshots`
