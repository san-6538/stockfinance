import pandas as pd

from app.db import upsert_analytics
from utils.logger import logger


def load(df: pd.DataFrame) -> int:
    """Idempotently load a feature dataframe into the warehouse."""
    logger.info("Loading data into warehouse")
    written = upsert_analytics(df)
    logger.success(f"Warehouse load complete ({written} rows)")
    return written
