"""Seed the warehouse from bundled sample parquet files on first boot.

Runs offline (no Yahoo Finance call) so a freshly deployed instance shows
data immediately. Skipped if the warehouse already has rows.
"""
from __future__ import annotations

from app.db import query_df
from app.settings import SAMPLES_DIR, SEED_ON_STARTUP
from orchestration.pipeline import process_file
from utils.logger import logger


def warehouse_is_empty() -> bool:
    try:
        n = int(query_df("SELECT COUNT(*) AS n FROM stock_analytics")["n"].iloc[0])
        return n == 0
    except Exception:  # noqa: BLE001 - table may not exist yet
        return True


def seed_if_empty() -> None:
    if not SEED_ON_STARTUP:
        return
    if not warehouse_is_empty():
        return
    if not SAMPLES_DIR.exists():
        return

    logger.info("Warehouse empty — seeding from bundled samples")
    for f in sorted(SAMPLES_DIR.glob("*.parquet")):
        try:
            process_file(str(f))
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to seed {f.name}: {exc}")
    logger.success("Seeding complete")
