"""Dashboard statistics endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.repositories.base import PredictionRepository
from app.api.deps import get_repository
from app.schemas.prediction import DiseaseCount, MostDetected, StatsResponse

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
def stats(repository: PredictionRepository = Depends(get_repository)) -> StatsResponse:
    raw = repository.stats()
    return StatsResponse(
        total_predictions=raw["total_predictions"],
        healthy_count=raw["healthy_count"],
        diseased_count=raw["diseased_count"],
        average_confidence=raw["average_confidence"],
        most_detected_disease=(
            MostDetected(**raw["most_detected_disease"]) if raw["most_detected_disease"] else None
        ),
        by_plant=[DiseaseCount(**item) for item in raw["by_plant"]],
        top_diseases=[DiseaseCount(**item) for item in raw["top_diseases"]],
    )
