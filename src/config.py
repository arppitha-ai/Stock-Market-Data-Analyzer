"""Central settings so numbers are not scattered ("magic numbers") across the code."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "outputs"
IMAGES_DIR = ROOT_DIR / "images"
REPORTS_DIR = ROOT_DIR / "reports"

DEFAULT_TICKER = "AAPL"
DEFAULT_START = "2020-01-01"
DEFAULT_END = None            # None = today

TRADING_DAYS = 252            # trading days in a year (used to annualise)
SMA_FAST = 20
SMA_SLOW = 50
RSI_WINDOW = 14
BB_WINDOW = 20
VOL_WINDOW = 21               # ~1 trading month
RISK_FREE_RATE = 0.0          # keep 0 for simplicity; change if you want
FEE_BPS = 5                   # 5 basis points = 0.05% per position change

DISCLAIMER = (
    "Educational project only. Historical data and backtests do not predict future "
    "results. This is NOT financial advice."
)
