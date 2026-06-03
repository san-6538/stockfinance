FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install deps first for better layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Data lives on a mounted volume in production.
ENV DATA_DIR=/data \
    DB_PATH=/data/analytics/warehouse.duckdb \
    PORT=8000
VOLUME ["/data"]
EXPOSE 8000

# Honor $PORT (Render/Railway/Fly inject it).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
