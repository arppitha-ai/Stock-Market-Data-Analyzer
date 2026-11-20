"""Run:  python -m unittest discover -s tests -v   (or: pytest)"""
import sys, unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis import find_crossovers, summarize
from src.backtest import run_sma_backtest
from src.cleaning import clean_data
from src.data_loader import generate_sample_data
from src.indicators import add_all_indicators, add_returns, add_rsi


def make_df(n_start="2021-01-01", n_end="2023-12-31", seed=1):
    raw = generate_sample_data("T", n_start, n_end, seed=seed)
    df, _ = clean_data(raw)
    return df


class TestCleaning(unittest.TestCase):
    def test_removes_duplicates_and_bad_prices(self):
        raw = generate_sample_data("T", "2021-01-01", "2021-12-31", seed=1)
        raw = pd.concat([raw, raw.iloc[[5]]])                 # duplicate day
        raw.loc[raw.index[10], "Close"] = np.nan              # missing value
        raw.loc[raw.index[20], "Close"] = -5                  # impossible price
        df, log = clean_data(raw)
        self.assertEqual(log["duplicates_removed"], 1)
        self.assertTrue((df["close"] > 0).all())
        self.assertTrue(df["date"].is_monotonic_increasing)
        self.assertFalse(df["close"].isna().any())

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            clean_data(pd.DataFrame({"foo": [1, 2, 3]}))


class TestIndicators(unittest.TestCase):
    def test_daily_return_formula(self):
        df = add_returns(make_df())
        expected = df["adj_close"].iloc[1] / df["adj_close"].iloc[0] - 1
        self.assertAlmostEqual(df["daily_return"].iloc[1], expected)

    def test_sma_matches_manual_mean(self):
        df = add_all_indicators(make_df())
        manual = df["close"].iloc[:20].mean()
        self.assertAlmostEqual(df["sma_20"].iloc[19], manual)

    def test_rsi_bounds(self):
        rsi = add_rsi(make_df())["rsi"].dropna()
        self.assertTrue(((rsi >= 0) & (rsi <= 100)).all())

    def test_bollinger_order(self):
        d = add_all_indicators(make_df()).dropna()
        self.assertTrue((d["bb_upper"] >= d["bb_mid"]).all() and (d["bb_mid"] >= d["bb_lower"]).all())

    def test_drawdown_never_positive(self):
        self.assertLessEqual(add_all_indicators(make_df())["drawdown"].max(), 0)


class TestAnalysisAndBacktest(unittest.TestCase):
    def setUp(self):
        self.df = add_all_indicators(make_df())

    def test_summary_keys_and_consistency(self):
        s = summarize(self.df)
        self.assertGreaterEqual(s["highest_close"], s["lowest_close"])
        self.assertLessEqual(s["max_drawdown"], 0)
        self.assertGreater(s["annualized_volatility"], 0)

    def test_crossovers_alternate(self):
        ev = find_crossovers(self.df)
        if len(ev) > 1:
            self.assertTrue((ev["signal"] != ev["signal"].shift()).iloc[1:].all())

    def test_backtest_no_lookahead_and_valid_stats(self):
        bt = run_sma_backtest(self.df)
        c = bt["curve"]
        # first day can never hold a position (signal is shifted by one day)
        self.assertEqual(c["position"].iloc[0], 0)
        self.assertTrue(set(c["position"].unique()) <= {0.0, 1.0})
        self.assertTrue(0 <= bt["strategy"]["win_rate"] <= 1)
        self.assertLessEqual(bt["strategy"]["max_drawdown"], 0)

    def test_zero_fee_beats_high_fee(self):
        lo = run_sma_backtest(self.df, fee_bps=0)["strategy"]["total_return"]
        hi = run_sma_backtest(self.df, fee_bps=100)["strategy"]["total_return"]
        self.assertGreaterEqual(lo, hi)


if __name__ == "__main__":
    unittest.main()
