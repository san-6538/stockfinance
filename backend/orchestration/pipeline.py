import pandas as pd

from ingestion.fetch_stocks import fetch_and_store
from transformations.clean_data import clean
from transformations.features import add_features
from warehouse.load_warehouse import load
from utils.logger import logger


def process_file(path: str) -> int:
    """Clean → feature-engineer → load a single raw parquet file."""
    df = pd.read_parquet(path)
    df = clean(df)
    df = add_features(df)
    return load(df)


def run_pipeline(tickers: list[str] | None = None) -> dict:
    """Fetch, transform and load the given tickers (or the default universe).

    Returns a summary dict: which tickers succeeded and rows written.
    """
    paths = fetch_and_store(tickers)

    total_rows = 0
    processed: list[str] = []
    for path in paths:
        try:
            total_rows += process_file(path)
            processed.append(path)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to process {path}: {exc}")

    logger.success("Pipeline executed successfully")
    return {"files_processed": len(processed), "rows_written": total_rows}
