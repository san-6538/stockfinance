# 📈 Financial Market Data Platform

End-to-end platform for ingesting, processing, analyzing, and **visualizing** stock
market time-series — now with a web frontend and one-command deployment anywhere.

```
 Yahoo Finance ──▶ Ingest ──▶ Clean ──▶ Feature engineer ──▶ DuckDB warehouse
                                                                   │
                            React dashboard ◀── FastAPI REST API ◀─┘
```

## What it does

- **Ingest** stock data from Yahoo Finance (any ticker, e.g. `AAPL`, `TSLA`, `SBIN.NS`)
- **Transform** — clean, then engineer features: returns, MA-20, MA-50, 20-day volatility
- **Warehouse** — idempotent loads into DuckDB (re-running updates instead of duplicating)
- **Serve** — a FastAPI REST API
- **Search** — find a stock by **company name** ("Apple", "Reliance", "Tata") → resolves to
  the right ticker via Yahoo's lookup, then fetches & charts it
- **Visualize** — a React dashboard: price + moving averages, volatility, daily returns,
  a data table, CSV export, and a button to fetch/refresh any ticker on demand

## Repository layout

```
finance-data-platform/
├── backend/                 # FastAPI + the data pipeline
│   ├── app/                 # API: main, routes, db, schemas, settings, seed
│   ├── ingestion/ transformations/ warehouse/ orchestration/ utils/
│   ├── samples/             # bundled parquet used to seed on first boot
│   ├── Dockerfile · fly.toml · requirements.txt
├── frontend/                # React + Vite + TypeScript dashboard
│   ├── src/                 # App, api, components/ (charts, table, cards)
│   ├── Dockerfile · nginx.conf.template
├── docker-compose.yml       # run the whole stack with one command
├── render.yaml              # Render Blueprint (one-click deploy)
└── DEPLOY.md                # deployment guide (Render / Railway / Fly / any host)
```

## Quickstart — run the whole thing (Docker)

```bash
docker compose up --build
```

- **App:** http://localhost:8090
- **API docs (Swagger):** http://localhost:8000/docs

The warehouse self-seeds from bundled samples, so there's data on first load.
Type any ticker in the UI and click **Analyze** to fetch it live.

## Local development (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv && .venv/Scripts/activate    # Windows
# source .venv/bin/activate                        # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend** (proxies `/api` to `localhost:8000` in dev)
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

**Batch run only** (no API — populate the warehouse from the CLI):
```bash
cd backend && python main.py
```

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET`  | `/api/health` | liveness |
| `GET`  | `/api/search?q=apple` | resolve a company name to tickers |
| `GET`  | `/api/stocks` | list tickers + whether they have data |
| `GET`  | `/api/stocks/{ticker}/analytics?range=1Y` | time-series for charts |
| `GET`  | `/api/stocks/{ticker}/summary` | latest price, change, volatility |
| `GET`  | `/api/stocks/{ticker}/export.csv` | download as CSV |
| `POST` | `/api/pipeline/run` | fetch/refresh tickers (`{"tickers":["AAPL"]}`) |

Ranges: `1M, 3M, 6M, 1Y, 3Y, 5Y, MAX`.

## Deploying
live at : https://stockfinance.onrender.com
See **[DEPLOY.md](DEPLOY.md)** for Render, Railway, Fly.io, and single-host instructions.
The same Docker images run unchanged on any host. Configuration is via environment
variables (`DATA_DIR`, `DB_PATH`, `CORS_ORIGINS`, `VITE_API_URL`, …).

## Production notes

- Swap the DuckDB file for Postgres/Snowflake by replacing `app/db.py`.
- Swap the local data lake for S3/GCS in `ingestion/`.
- Orchestrate scheduled refreshes with Airflow/cron by calling `python main.py`
  or `POST /api/pipeline/run`.
