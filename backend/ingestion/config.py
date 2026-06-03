"""Backwards-compatible config shim.

Real configuration now lives in :mod:`app.settings` so it can be driven by
environment variables. These names are kept for existing imports.
"""
from app.settings import DATA_LAKE_RAW, DEFAULT_STOCKS as STOCKS, START_DATE

__all__ = ["STOCKS", "START_DATE", "DATA_LAKE_RAW"]
