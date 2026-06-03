# Single-service image: build the React frontend, then serve it from FastAPI.
# One container, one URL, same-origin API — nothing to cross-wire.

# ---- Stage 1: build the frontend ----
FROM node:20-alpine AS frontend
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Empty => the app uses same-origin /api (served by this very backend).
ENV VITE_API_URL=""
RUN npm run build

# ---- Stage 2: backend + bundled static UI ----
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./
COPY --from=frontend /fe/dist ./static

ENV DATA_DIR=/data \
    DB_PATH=/data/analytics/warehouse.duckdb \
    STATIC_DIR=/app/static \
    PORT=8000
VOLUME ["/data"]
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
