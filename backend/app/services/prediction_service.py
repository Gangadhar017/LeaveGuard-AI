"""Orchestrates the full prediction flow:

validate upload -> model inference -> disease knowledge base lookup ->
thumbnail generation -> persistence -> API response.

`processing_time` measures model-side work (decode + features + inference),
which is the metric users care about; storage time is excluded on purpose.
"""

from __future__ import annotations

import time

from app.core.exceptions import ModelNotLoadedError
from app.core.logging_config import get_logger
from app.ml.disease_info import get_disease_info
from app.ml.labels import split_label
from app.ml.model_service import BaseDiseaseModel
from app.models.prediction import PredictionRecord
from app.repositories.base import PredictionRepository
from app.services.image_validator import validate_upload
from app.utils.images import make_thumbnail

logger = get_logger(__name__)


class PredictionService:
    def __init__(
        self,
        model: BaseDiseaseModel,
        repository: PredictionRepository,
        max_upload_bytes: int,
    ):
        self.model = model
        self.repository = repository
        self.max_upload_bytes = max_upload_bytes

    def analyze(self, data: bytes, filename: str | None) -> dict:
        validate_upload(data, filename, self.max_upload_bytes)
        if self.model is None:
            raise ModelNotLoadedError()

        start = time.perf_counter()
        result = self.model.predict(data)
        processing_time = time.perf_counter() - start

        # API contract: `plant` is the crop, `disease` is the full class label
        # (e.g. plant="Tomato", disease="Tomato Early Blight")
        plant, _, is_healthy = split_label(result.label)
        info = get_disease_info(result.label)

        record = self.repository.add(PredictionRecord(
            plant=plant,
            disease=result.label,
            is_healthy=is_healthy,
            confidence=result.confidence,
            image_name=filename or "upload",
            processing_time=round(processing_time, 3),
            model_name=result.model_name,
            top_predictions=result.top_predictions,
            thumbnail=make_thumbnail(data),
        ))

        logger.info(
            "Prediction #%s: %s (%.2f%%) in %.3fs via %s",
            record.id, result.label, result.confidence, processing_time, self.repository.name,
        )
        return self._response(record, info)

    def _response(self, record: PredictionRecord, info: dict) -> dict:
        return {
            "success": True,
            "prediction": {
                "id": record.id,
                "plant": record.plant,
                "disease": record.disease,
                "is_healthy": record.is_healthy,
                "confidence": record.confidence,
                "image_name": record.image_name,
                "thumbnail": record.thumbnail,
                "processing_time": record.processing_time,
                "model_name": record.model_name,
                "top_predictions": record.top_predictions,
                "created_at": record.created_at,
            },
            "recommendation": {
                "description": info["description"],
                "symptoms": info["symptoms"],
                "prevention": info["prevention"],
                "treatment": info["treatment"],
                "severity": info["severity"],
            },
        }
