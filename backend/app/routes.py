from __future__ import annotations

import io
import re

import numpy as np
import pandas as pd
import requests
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app import db
from app.schemas import (
    AnalyticsPoint,
    PipelineRunRequest,
    PipelineRunResult,
    SearchResult,
    StockInfo,
    StockSummary,
)
from app.settings import DEFAULT_STOCKS
from orchestration.pipeline import run_pipeline
from utils.logger import logger

router = APIRouter(prefix="/api")

# Allow letters/digits plus the symbols Yahoo Finance uses:
#   . (e.g. SBIN.NS)   - (e.g. BTC-USD)   ^ (indices, ^NSEI)   = (futures, ES=F)
TICKER_RE = re.compile(r"^[A-Za-z0-9.^=\-]{1,20}$")

# Range label -> number of days back from the latest available date. None = all.
RANGES: dict[str, int | None] = {
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "3Y": 1095,
    "5Y": 1825,
    "MAX": None,
}


def _validate_ticker(ticker: str) -> str:
    ticker = ticker.strip().upper()
    if not TICKER_RE.match(ticker):
        raise HTTPException(status_code=400, detail=f"Invalid ticker: {ticker!r}")
    return ticker


def _records(df: pd.DataFrame) -> list[dict]:
    """Convert a dataframe to JSON-safe records (NaN/NaT → None)."""
    df = df.replace({np.nan: None})
    return df.to_dict(orient="records")


def _name_for(ticker: str) -> str:
    return DEFAULT_STOCKS.get(ticker, ticker)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
# Quote types worth surfacing in search (skip news, options, etc.).
_SEARCHABLE_TYPES = {"EQUITY", "ETF", "INDEX", "CRYPTOCURRENCY", "CURRENCY", "MUTUALFUND"}


@router.get("/search", response_model=list[SearchResult])
def search(q: str = Query(..., min_length=1, description="Company name or symbol")) -> list[SearchResult]:
    """Resolve a company name (or partial symbol) to tradable tickers."""
    query = q.strip()
    if not query:
        return []
    try:
        resp = requests.get(
            YAHOO_SEARCH_URL,
            params={"q": query, "quotesCount": 10, "newsCount": 0},
            headers={"User-Agent": "Mozilla/5.0 (financial-data-platform)"},
            timeout=10,
        )
        resp.raise_for_status()
        quotes = resp.json().get("quotes", [])
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Search failed for {query!r}: {exc}")
        raise HTTPException(status_code=502, detail="Search provider unavailable")

    results: list[SearchResult] = []
    for item in quotes:
        symbol = item.get("symbol")
        qtype = (item.get("quoteType") or "").upper()
        if not symbol or (qtype and qtype not in _SEARCHABLE_TYPES):
            continue
        name = item.get("shortname") or item.get("longname") or symbol
        results.append(
            SearchResult(
                symbol=symbol,
                name=name,
                exchange=item.get("exchDisp") or item.get("exchange") or "",
                type=qtype,
            )
        )
    return results


@router.get("/stocks", response_model=list[StockInfo])
def list_stocks() -> list[StockInfo]:
    present = db.query_df("SELECT DISTINCT ticker FROM stock_analytics")
    present_set = set(present["ticker"].tolist()) if not present.empty else set()

    # Union of the configured universe and anything already in the warehouse.
    tickers = list(DEFAULT_STOCKS.keys()) + [
        t for t in present_set if t not in DEFAULT_STOCKS
    ]
    return [
        StockInfo(ticker=t, name=_name_for(t), has_data=t in present_set)
        for t in tickers
    ]


@router.get("/stocks/{ticker}/analytics", response_model=list[AnalyticsPoint])
def analytics(
    ticker: str,
    range: str = Query("1Y", description="One of " + ", ".join(RANGES)),
) -> list[AnalyticsPoint]:
    ticker = _validate_ticker(ticker)
    if range not in RANGES:
        raise HTTPException(status_code=400, detail=f"Invalid range: {range!r}")

    days = RANGES[range]
    if days is None:
        df = db.query_df(
            """
            SELECT date, close, returns, ma_20, ma_50, volatility
            FROM stock_analytics WHERE ticker = ? ORDER BY date
            """,
            [ticker],
        )
    else:
        df = db.query_df(
            """
            SELECT date, close, returns, ma_20, ma_50, volatility
            FROM stock_analytics
            WHERE ticker = ?
              AND date >= (
                  SELECT max(date) FROM stock_analytics WHERE ticker = ?
              ) - CAST(? AS INTEGER)
            ORDER BY date
            """,
            [ticker, ticker, days],
        )

    if df.empty:
        return []

    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return [AnalyticsPoint(**r) for r in _records(df)]


@router.get("/stocks/{ticker}/summary", response_model=StockSummary)
def summary(ticker: str) -> StockSummary:
    ticker = _validate_ticker(ticker)
    df = db.query_df(
        """
        SELECT date, close, volatility
        FROM stock_analytics WHERE ticker = ? ORDER BY date
        """,
        [ticker],
    )
    if df.empty:
        return StockSummary(ticker=ticker, name=_name_for(ticker), points=0)

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    latest_close = float(latest["close"])
    prev_close = float(prev["close"])
    change = latest_close - prev_close
    change_pct = (change / prev_close * 100) if prev_close else None
    vol = latest["volatility"]

    return StockSummary(
        ticker=ticker,
        name=_name_for(ticker),
        points=len(df),
        as_of=pd.to_datetime(latest["date"]).strftime("%Y-%m-%d"),
        latest_close=latest_close,
        prev_close=prev_close,
        change=change,
        change_pct=change_pct,
        volatility=None if pd.isna(vol) else float(vol),
    )


@router.get("/stocks/{ticker}/export.csv")
def export_csv(ticker: str) -> StreamingResponse:
    ticker = _validate_ticker(ticker)
    df = db.query_df(
        """
        SELECT date, ticker, close, returns, ma_20, ma_50, volatility
        FROM stock_analytics WHERE ticker = ? ORDER BY date
        """,
        [ticker],
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {ticker}")

    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{ticker}.csv"'},
    )


@router.post("/pipeline/run", response_model=PipelineRunResult)
def pipeline_run(req: PipelineRunRequest) -> PipelineRunResult:
    tickers = req.tickers
    if tickers:
        tickers = [_validate_ticker(t) for t in tickers]
    else:
        tickers = list(DEFAULT_STOCKS.keys())

    logger.info(f"Pipeline run requested for {tickers}")
    result = run_pipeline(tickers)
    return PipelineRunResult(
        status="ok",
        files_processed=result["files_processed"],
        rows_written=result["rows_written"],
        tickers=tickers,
    )
