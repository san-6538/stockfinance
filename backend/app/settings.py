"""Centralized, environment-driven configuration.

Every path and tunable lives here so the same image runs locally and in the
cloud (pointing at a mounted volume) just by changing env vars.
"""
from __future__ import annotations

import os
from pathlib import Path

# Resolve paths relative to the backend/ directory so cwd doesn't matter.
BACKEND_DIR = Path(__file__).resolve().parent.parent


def _path(env_var: str, default: Path) -> Path:
    raw = os.getenv(env_var)
    return Path(raw) if raw else default


# Where the runtime data lake lives. Override DATA_DIR in production to point
# at a persistent volume, e.g. DATA_DIR=/data.
DATA_DIR: Path = _path("DATA_DIR", BACKEND_DIR / "data_lake")
DATA_LAKE_RAW: Path = DATA_DIR / "raw" / "stocks"
DB_PATH: Path = _path("DB_PATH", DATA_DIR / "analytics" / "warehouse.duckdb")

# Bundled sample parquet files used to seed the warehouse on first boot
# (avoids hitting Yahoo Finance before the user does anything).
SAMPLES_DIR: Path = BACKEND_DIR / "samples" / "stocks"

SCHEMA_PATH: Path = BACKEND_DIR / "warehouse" / "schema.sql"

# Optional directory of built frontend assets to serve from the API itself
# (single-service deploys). When set and present, the SPA is served at "/".
STATIC_DIR: Path = _path("STATIC_DIR", BACKEND_DIR / "static")

# Default universe shown in the UI. Users can analyze any valid ticker on top.
DEFAULT_STOCKS: dict[str, str] = {
    "SBIN.NS": "State Bank of India",
    "SHRIRAMFIN.NS": "Shriram Finance",
    "ADANIPOWER.NS": "Adani Power",
}

START_DATE: str = os.getenv("START_DATE", "2023-01-01")

# CORS: comma-separated list of allowed frontend origins. "*" allows all.
CORS_ORIGINS: list[str] = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()
]

# If true, seed the warehouse from bundled samples on startup when it's empty.
SEED_ON_STARTUP: bool = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"


def ensure_dirs() -> None:
    DATA_LAKE_RAW.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
