"""LeafGuard AI — FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000   (from the backend/ directory)
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, predictions, stats
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging, get_logger
from app.ml.model_service import ClassicalModelService
from app.repositories.memory import InMemoryPredictionRepository
from app.repositories.mongo import MongoPredictionRepository
from app.services.prediction_service import PredictionService

logger = get_logger(__name__)


def _build_repository(settings):
    """Prefer MongoDB; fall back to in-memory storage when unavailable."""
    try:
        repository = MongoPredictionRepository(settings.mongodb_uri, settings.database_name)
        repository.ensure_ready()
        logger.info("MongoDB connected: %s (db=%s)", settings.mongodb_uri, settings.database_name)
        return repository
    except Exception as exc:
        logger.warning(
            "MongoDB unavailable (%s) — falling back to IN-MEMORY storage. "
            "Prediction history will be lost on restart.",
            type(exc).__name__,
        )
        return InMemoryPredictionRepository()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    app.state.settings = settings
    try:
        app.state.model = ClassicalModelService(settings.model_path)
    except Exception as exc:
        logger.error("Model could not be loaded: %s", exc)
        app.state.model = None

    app.state.repository = _build_repository(settings)
    app.state.prediction_service = PredictionService(
        model=app.state.model,
        repository=app.state.repository,
        max_upload_bytes=settings.max_upload_bytes,
    )
    logger.info("%s v%s ready", settings.app_name, settings.app_version)
    yield
    logger.info("Shutting down LeafGuard AI backend")


def create_app() -> FastAPI:
    app = FastAPI(
        title="LeafGuard AI API",
        version=get_settings().app_version,
        description="REST API for plant disease detection & classification from leaf images.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        if request.url.path != "/health":
            logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
        return response

    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(predictions.router, prefix="/api/v1")
    app.include_router(stats.router, prefix="/api/v1")
    return app


app = create_app()
