# Deployment Guide

The app is two services that run anywhere via Docker:

- **backend** — FastAPI + DuckDB (the pipeline as an API)
- **frontend** — React/Vite dashboard, served by nginx which proxies `/api` to the backend

There are two deployment shapes:

| Shape | When | How users reach it |
|---|---|---|
| **Single host** (docker-compose) | one VM, a laptop, any Docker host | one URL — nginx serves the UI and proxies `/api` |
| **Split** (backend + static frontend) | managed PaaS (Render/Railway/Fly) | frontend URL calls the backend URL directly (CORS) |

---

## 1. Local / any Docker host — one command

```bash
docker compose up --build
```

- UI:   http://localhost:8090
- API:  http://localhost:8000/docs
- The DuckDB warehouse persists in the named volume `warehouse-data`.
- On first boot the warehouse self-seeds from `backend/samples/` so there's data immediately.

This same `docker compose` works on any cloud VM (EC2, GCE, DigitalOcean droplet, etc.).

---

## 2. Render (Blueprint) — push & deploy

A [`render.yaml`](render.yaml) blueprint is included.

1. Push this repo to GitHub.
2. Render → **New → Blueprint** → select the repo.
3. Render creates the **fdp-backend** (Docker web service) and **fdp-frontend** (static site).
4. If the backend URL differs from `https://fdp-backend.onrender.com`, update the
   frontend's `VITE_API_URL` env var and redeploy it.

> Free instances have no persistent disk, so the warehouse re-seeds on cold start.
> To persist, upgrade the backend plan and uncomment the `disk:` block in `render.yaml`.

---

## 3. Railway

Railway auto-detects the Dockerfiles.

- **Backend service:** root directory `backend/`. Set env: `DATA_DIR=/data`,
  `DB_PATH=/data/analytics/warehouse.duckdb`, `CORS_ORIGINS=*`. Add a **Volume**
  mounted at `/data` for persistence. Railway injects `$PORT` (the image honors it).
- **Frontend service:** root directory `frontend/`. Set build arg / env
  `VITE_API_URL=https://<your-backend>.up.railway.app`.

---

## 4. Fly.io

Backend config is in [`backend/fly.toml`](backend/fly.toml):

```bash
cd backend
fly launch --no-deploy
fly volumes create warehouse --size 1 --region <region>
fly deploy
```

Deploy the frontend to any static host (or `fly launch` in `frontend/`) and set
`VITE_API_URL=https://fdp-backend.fly.dev`.

---

## Environment variables (backend)

| Var | Default | Purpose |
|---|---|---|
| `DATA_DIR` | `backend/data_lake` | Root of the data lake (point at a volume in prod) |
| `DB_PATH` | `$DATA_DIR/analytics/warehouse.duckdb` | DuckDB file location |
| `START_DATE` | `2023-01-01` | Earliest date to fetch |
| `CORS_ORIGINS` | `*` | Comma-separated allowed frontend origins |
| `SEED_ON_STARTUP` | `true` | Seed warehouse from bundled samples when empty |
| `PORT` | `8000` | Port uvicorn binds (PaaS platforms inject this) |

## Environment variables (frontend, build-time)

| Var | Default | Purpose |
|---|---|---|
| `VITE_API_URL` | `""` (same-origin) | Absolute backend URL for split deploys |
