"""Optional Streamlit dashboard.   Run:  streamlit run app.py
Educational project - NOT financial advice."""
import datetime as dt

import pandas as pd
import streamlit as st

from src import config
from src.analysis import find_crossovers, generate_insights, risk_label, summarize
from src.backtest import run_sma_backtest
from src.cleaning import clean_data
from src.data_loader import load_data
from src.indicators import add_all_indicators
from src import visualize as viz

st.set_page_config(page_title="Stock Market Data Analyzer", page_icon="📈", layout="wide")
st.title("📈 Stock Market Data Analyzer")
st.caption(config.DISCLAIMER)

with st.sidebar:
    st.header("Inputs")
    ticker = st.text_input("Ticker symbol", config.DEFAULT_TICKER).upper().strip()
    start = st.date_input("Start date", dt.date(2020, 1, 1))
    end = st.date_input("End date", dt.date.today())
    source = st.selectbox("Data source", ["auto", "yahoo", "csv", "sample"])
    fast = st.number_input("Fast SMA", 5, 100, config.SMA_FAST)
    slow = st.number_input("Slow SMA", 10, 300, config.SMA_SLOW)
    fee = st.number_input("Fee (bps per trade)", 0.0, 100.0, float(config.FEE_BPS))
    go = st.button("Analyze", type="primary")


@st.cache_data(show_spinner=False)
def pipeline(ticker, start, end, source, fast, slow, fee):
    raw, src = load_data(ticker, str(start), str(end), source)
    df, log = clean_data(raw, str(start), str(end))
    df = add_all_indicators(df, fast, slow)
    return df, log, src, summarize(df, fast, slow), find_crossovers(df, fast, slow), run_sma_backtest(df, fast, slow, fee)


if go or "ran" in st.session_state:
    st.session_state["ran"] = True
    if fast >= slow:
        st.error("Fast SMA must be smaller than slow SMA."); st.stop()
    try:
        df, log, src, s, cross, bt = pipeline(ticker, start, end, source, int(fast), int(slow), fee)
    except Exception as exc:
        st.error(f"Could not analyze {ticker}: {exc}"); st.stop()

    st.success(f"Data source: {src} · {log['rows_clean']} trading days")
    c = st.columns(5)
    c[0].metric("Total return", f"{s['total_return']:+.1%}")
    c[1].metric("Annualised return", f"{s['annualized_return']:+.1%}")
    c[2].metric("Volatility", f"{s['annualized_volatility']:.1%}", risk_label(s["annualized_volatility"]), delta_color="off")
    c[3].metric("Max drawdown", f"{s['max_drawdown']:.1%}")
    c[4].metric("Trend", s["current_trend"])

    tabs = st.tabs(["Price", "Moving averages", "Returns", "Risk", "Indicators", "Backtest", "Insights", "Data"])
    with tabs[0]: st.pyplot(viz.plot_price(df, ticker))
    with tabs[1]:
        st.pyplot(viz.plot_moving_averages(df, ticker, int(fast), int(slow)))
        st.subheader("Recent crossovers"); st.dataframe(cross.tail(10), use_container_width=True)
    with tabs[2]: st.pyplot(viz.plot_returns(df, ticker))
    with tabs[3]:
        st.pyplot(viz.plot_volatility(df, ticker)); st.pyplot(viz.plot_drawdown(df, ticker))
    with tabs[4]:
        st.pyplot(viz.plot_rsi_macd(df, ticker)); st.pyplot(viz.plot_bollinger(df, ticker))
    with tabs[5]:
        st.pyplot(viz.plot_backtest(bt, ticker))
        st.dataframe(pd.DataFrame({"Strategy": bt["strategy"], "Buy & hold": bt["buy_and_hold"]}))
    with tabs[6]:
        for line in generate_insights(s, ticker): st.markdown(f"- {line}")
    with tabs[7]:
        st.dataframe(df.tail(200), use_container_width=True)
        st.download_button("Download processed CSV", df.to_csv(index=False), f"{ticker}_processed.csv")
else:
    st.info("Choose a ticker in the sidebar and click **Analyze**. No internet? Pick source = sample.")
