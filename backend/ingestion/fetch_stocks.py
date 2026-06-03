import yfinance as yf
import pandas as pd

from app.settings import DEFAULT_STOCKS, START_DATE, DATA_LAKE_RAW
from utils.logger import logger


def fetch_one(ticker: str, start: str = START_DATE) -> str:
    """Fetch a single ticker from Yahoo Finance and store it as parquet.

    Returns the path to the stored file. Raises ValueError if no data.
    """
    DATA_LAKE_RAW.mkdir(parents=True, exist_ok=True)

    logger.info(f"Fetching data for {ticker}")
    df = yf.download(ticker, start=start, progress=False, auto_adjust=True)

    if df is None or df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")

    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.reset_index(inplace=True)
    df["ticker"] = ticker

    path = str(DATA_LAKE_RAW / f"{ticker}.parquet")
    df.to_parquet(path, index=False)
    logger.success(f"Stored raw data → {path}")
    return path


def fetch_and_store(tickers: list[str] | None = None) -> list[str]:
    """Fetch a list of tickers (defaults to the configured universe)."""
    tickers = tickers or list(DEFAULT_STOCKS.keys())
    paths: list[str] = []
    for ticker in tickers:
        try:
            paths.append(fetch_one(ticker))
        except Exception as exc:  # noqa: BLE001 - log and continue with others
            logger.error(f"Failed to fetch {ticker}: {exc}")
    return paths
