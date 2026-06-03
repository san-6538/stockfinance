"""CLI entry point: run the batch pipeline once (e.g. for cron/Airflow).

The web API lives in app/main.py and is served with uvicorn.
"""
from orchestration.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()
