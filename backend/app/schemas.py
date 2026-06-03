from __future__ import annotations

from pydantic import BaseModel, Field


class StockInfo(BaseModel):
    ticker: str
    name: str
    has_data: bool


class AnalyticsPoint(BaseModel):
    date: str
    close: float | None = None
    returns: float | None = None
    ma_20: float | None = None
    ma_50: float | None = None
    volatility: float | None = None


class StockSummary(BaseModel):
    ticker: str
    name: str
    points: int
    as_of: str | None = None
    latest_close: float | None = None
    prev_close: float | None = None
    change: float | None = None
    change_pct: float | None = None
    volatility: float | None = None


class SearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str = ""
    type: str = ""


class PipelineRunRequest(BaseModel):
    tickers: list[str] | None = Field(
        default=None,
        description="Tickers to (re)fetch. Defaults to the configured universe.",
    )


class PipelineRunResult(BaseModel):
    status: str
    files_processed: int
    rows_written: int
    tickers: list[str]
