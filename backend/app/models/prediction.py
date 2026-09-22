"""Domain model for a stored prediction (independent of API and DB shapes)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class PredictionRecord:
    plant: str
    disease: str
    is_healthy: bool
    confidence: float
    image_name: str
    processing_time: float
    model_name: str
    top_predictions: list[dict] = field(default_factory=list)
    thumbnail: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    id: str | None = None
