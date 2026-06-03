from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.routes import router
from app.seed import seed_if_empty
from app.settings import CORS_ORIGINS, STATIC_DIR
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up: initializing warehouse")
    init_db()
    seed_if_empty()
    yield


app = FastAPI(
    title="Financial Data Platform API",
    version="1.0.0",
    description="Ingest, transform and serve stock analytics.",
    lifespan=lifespan,
)

allow_all = "*" in CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else CORS_ORIGINS,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve the built frontend from the API itself (single-service deploy).
# Mounted last so /api/* and /docs match first; "/" serves the SPA.
if STATIC_DIR and STATIC_DIR.exists():
    logger.info(f"Serving frontend from {STATIC_DIR}")
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:

    @app.get("/")
    def root() -> dict:
        return {
            "service": "financial-data-platform",
            "docs": "/docs",
            "health": "/api/health",
        }
