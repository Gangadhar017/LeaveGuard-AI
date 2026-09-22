"""Prediction endpoints: analyze a leaf image and manage history."""

from __future__ import annotations

import dataclasses

from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.api.deps import get_prediction_service, get_repository, get_settings_dep
from app.core.config import Settings
from app.core.exceptions import (
    FileTooLargeError,
    InvalidImageError,
)
from app.models.prediction import PredictionRecord
from app.repositories.base import PredictionRepository
from app.schemas.prediction import (
    DeleteResponse,
    PredictResponse,
    PredictionOut,
    PredictionsListResponse,
    Pagination,
)
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["predictions"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    file: UploadFile = File(..., description="Leaf image (JPG/PNG/WEBP)"),
    service: PredictionService = Depends(get_prediction_service),
    settings: Settings = Depends(get_settings_dep),
) -> PredictResponse:
    data = file.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise FileTooLargeError(
            f"The uploaded file is too large. Maximum allowed size is {settings.max_upload_size_mb} MB."
        )
    if not data:
        raise InvalidImageError("The uploaded file is empty.")

    return service.analyze(data, file.filename)


@router.get("/predictions", response_model=PredictionsListResponse)
def list_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, max_length=100, description="Matches plant or disease"),
    plant: str | None = Query(None, max_length=50),
    status: str | None = Query(None, pattern="^(healthy|diseased)$"),
    sort: str = Query("newest", pattern="^(newest|oldest|confidence)$"),
    repository: PredictionRepository = Depends(get_repository),
) -> PredictionsListResponse:
    items, total = repository.list(
        page=page, page_size=page_size, search=search, plant=plant, status=status, sort=sort
    )
    return PredictionsListResponse(
        success=True,
        items=[PredictionOut(**dataclasses.asdict(record)) for record in items],
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=max(1, -(-total // page_size)),
        ),
    )


@router.get("/predictions/{prediction_id}", response_model=PredictionOut)
def get_prediction(
    prediction_id: str,
    repository: PredictionRepository = Depends(get_repository),
) -> PredictionOut:
    return PredictionOut(**dataclasses.asdict(repository.get(prediction_id)))


@router.delete("/predictions/{prediction_id}", response_model=DeleteResponse)
def delete_prediction(
    prediction_id: str,
    repository: PredictionRepository = Depends(get_repository),
) -> DeleteResponse:
    repository.delete(prediction_id)
    return DeleteResponse(success=True, message=f"Prediction '{prediction_id}' deleted.")
