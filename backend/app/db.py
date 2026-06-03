"""Single-connection DuckDB access guarded by a process-wide lock.

DuckDB is single-writer and its connection object is not safe for concurrent
use, so every read and write goes through one connection behind an RLock. This
is plenty for this app's scale and removes any chance of two requests
corrupting the database file.
"""
from __future__ import annotations

import threading

import duckdb
import pandas as pd

from app.settings import DB_PATH, SCHEMA_PATH, ensure_dirs

_lock = threading.RLock()
_con: duckdb.DuckDBPyConnection | None = None

# Columns the warehouse table expects, in order.
_COLUMNS = ["date", "ticker", "close", "returns", "ma_20", "ma_50", "volatility"]


def _connect() -> duckdb.DuckDBPyConnection:
    global _con
    if _con is None:
        ensure_dirs()
        _con = duckdb.connect(str(DB_PATH))
        _con.execute(SCHEMA_PATH.read_text())
    return _con


def init_db() -> None:
    """Create the database file and schema if they don't exist yet."""
    with _lock:
        _connect()


def query_df(sql: str, params: list | None = None) -> pd.DataFrame:
    with _lock:
        return _connect().execute(sql, params or []).df()


def upsert_analytics(df: pd.DataFrame) -> int:
    """Insert rows, replacing any existing (date, ticker) pairs.

    Returns the number of rows written. Idempotent: re-running the pipeline
    for the same dates updates instead of duplicating (the original bug).
    """
    if df is None or df.empty:
        return 0

    # yfinance/feature columns are capitalized (Date, Close); DuckDB
    # identifiers are case-insensitive so the names line up with the schema.
    with _lock:
        con = _connect()
        con.register("incoming", df)
        try:
            con.execute(
                """
                DELETE FROM stock_analytics
                WHERE EXISTS (
                    SELECT 1 FROM incoming i
                    WHERE i.Date = stock_analytics.date
                      AND i.ticker = stock_analytics.ticker
                )
                """
            )
            con.execute(
                """
                INSERT INTO stock_analytics
                SELECT Date, ticker, Close, returns, ma_20, ma_50, volatility
                FROM incoming
                """
            )
        finally:
            con.unregister("incoming")
    return len(df)
