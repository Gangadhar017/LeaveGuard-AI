"""Tests for the serving-side model service (uses real artifact if present)."""

import pytest

from app.ml.model_service import ClassicalModelService, ModelPrediction
from app.core.exceptions import ModelNotLoadedError

ARTIFACT = (
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "backend" / "app" / "ml" / "artifacts" / "leafguard_model.joblib"
)

KNOWN_LABELS = {
    "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight",
    "Tomato Leaf Mold", "Tomato Septoria Leaf Spot", "Tomato Healthy",
    "Potato Early Blight", "Potato Late Blight", "Potato Healthy",
}


@pytest.fixture(scope="module")
def model_service():
    if not ARTIFACT.is_file():
        pytest.skip("Trained model artifact not found — run ml/training/train.py first.")
    return ClassicalModelService(ARTIFACT)


def test_missing_artifact_raises_model_not_loaded(tmp_path):
    with pytest.raises(ModelNotLoadedError):
        ClassicalModelService(tmp_path / "missing.joblib")


def test_service_exposes_metadata(model_service):
    assert model_service.model_name
    assert len(model_service.classes) == 9
    assert set(model_service.classes) == KNOWN_LABELS
    assert model_service.feature_config["use_segmentation"] is True


def test_predict_returns_valid_probabilities(model_service, tmp_path):
    import cv2
    import numpy as np

    # green 'leaf' on dark background — in-distribution-ish synthetic input
    image = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.ellipse(image, (100, 100), (90, 65), 15, 0, 360, (40, 150, 70), -1)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    result = model_service.predict(encoded.tobytes())
    assert isinstance(result, ModelPrediction)
    assert result.label in KNOWN_LABELS
    assert 0 <= result.confidence <= 100
    assert len(result.top_predictions) == 3
    total = sum(tp["confidence"] for tp in result.top_predictions)
    assert 0 < total <= 100.01
