"""Health and root endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_settings_dep
from app.schemas.prediction import ApiInfo, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    model = request.app.state.model
    return HealthResponse(
        status="ok" if model is not None else "degraded",
        model_loaded=model is not None,
        model_name=model.model_name if model else None,
        database=request.app.state.repository.name,
        version=request.app.state.settings.app_version,
    )


@router.get("/", response_model=ApiInfo)
def root(settings=Depends(get_settings_dep)) -> ApiInfo:
    return ApiInfo(
        name=settings.app_name,
        version=settings.app_version,
        description="Plant disease detection & classification platform API.",
        docs_url="/docs",
    )
