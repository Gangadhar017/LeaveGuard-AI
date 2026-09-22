"""Model service abstraction.

The API only depends on `BaseDiseaseModel`. The current implementation is the
classical OpenCV + scikit-learn bundle produced by ml/training/train.py; a
future CNN implementation only needs to return the same `ModelPrediction`,
so the API contract never changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

import joblib

from app.core.exceptions import ModelNotLoadedError
from app.core.logging_config import get_logger
from app.ml import preprocessing as prep

logger = get_logger(__name__)


@dataclass
class ModelPrediction:
    label: str
    confidence: float  # percentage 0-100
    model_name: str
    top_predictions: list[dict] = field(default_factory=list)


class BaseDiseaseModel(ABC):
    model_name: str = "abstract"

    @abstractmethod
    def predict(self, image_bytes: bytes) -> ModelPrediction: ...


class ClassicalModelService(BaseDiseaseModel):
    """Serving wrapper around the trained joblib bundle.

    The bundle contains the fitted sklearn Pipeline, class labels and the
    feature configuration used during training — inference reuses the exact
    same preprocessing code path from app.ml.preprocessing.
    """

    def __init__(self, model_path: Path | str):
        path = Path(model_path)
        if not path.is_file():
            raise ModelNotLoadedError(f"Model artifact not found at '{path}'.")
        try:
            bundle = joblib.load(path)
        except Exception as exc:  # corrupt/unpicklable artifact
            raise ModelNotLoadedError("Model artifact could not be loaded.") from exc

        required = {"pipeline", "classes", "feature_config", "metadata"}
        if not required.issubset(bundle):
            raise ModelNotLoadedError("Model bundle is missing required keys.")

        self.pipeline = bundle["pipeline"]
        self.classes: list[str] = bundle["classes"]
        self.feature_config: dict = bundle["feature_config"]
        self.metadata: dict = bundle["metadata"]
        self.model_name = self.metadata.get("model_name", "unknown")
        self.source_path = str(path)

        if not hasattr(self.pipeline, "predict_proba"):
            raise ModelNotLoadedError("Loaded pipeline does not support probability estimates.")
        logger.info("Model loaded: %s (%s) from %s", self.model_name, self.metadata.get("trained_at"), path)

    def predict(self, image_bytes: bytes) -> ModelPrediction:
        features = prep.extract_features_from_bytes(
            image_bytes,
            use_segmentation=self.feature_config.get("use_segmentation", True),
            use_denoise=self.feature_config.get("use_denoise", True),
        ).reshape(1, -1)

        proba = self.pipeline.predict_proba(features)[0]
        order = proba.argsort()[::-1][:3]
        top = [
            {"label": self.pipeline.classes_[i], "confidence": round(float(proba[i]) * 100, 2)}
            for i in order
        ]
        return ModelPrediction(
            label=top[0]["label"],
            confidence=top[0]["confidence"],
            model_name=self.model_name,
            top_predictions=top,
        )
