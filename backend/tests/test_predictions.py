"""Tests for the prediction lifecycle: analyze, history CRUD, schema shape."""

from pathlib import Path

import pytest

REQUIRED_PREDICTION_FIELDS = {
    "id", "plant", "disease", "is_healthy", "confidence", "image_name",
    "processing_time", "model_name", "top_predictions", "created_at",
}
REQUIRED_RECOMMENDATION_FIELDS = {"description", "symptoms", "prevention", "treatment", "severity"}

KNOWN_LABELS = {
    "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight",
    "Tomato Leaf Mold", "Tomato Septoria Leaf Spot", "Tomato Healthy",
    "Potato Early Blight", "Potato Late Blight", "Potato Healthy",
}


def _analyze(client, sample_leaf_bytes, name="leaf.jpg"):
    return client.post(
        "/api/v1/predict",
        files={"file": (name, sample_leaf_bytes, "image/jpeg")},
    )


def test_predict_returns_full_schema(client, sample_leaf_bytes):
    response = _analyze(client, sample_leaf_bytes)
    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert REQUIRED_PREDICTION_FIELDS.issubset(body["prediction"])
    assert REQUIRED_RECOMMENDATION_FIELDS.issubset(body["recommendation"])

    prediction = body["prediction"]
    assert prediction["plant"] == "Tomato"
    assert prediction["disease"] == "Tomato Early Blight"
    assert prediction["is_healthy"] is False
    assert 0 <= prediction["confidence"] <= 100
    assert prediction["processing_time"] >= 0
    assert len(prediction["top_predictions"]) == 2


def test_prediction_is_stored_and_retrievable(client, sample_leaf_bytes):
    created = _analyze(client, sample_leaf_bytes).json()["prediction"]

    single = client.get(f"/api/v1/predictions/{created['id']}")
    assert single.status_code == 200
    assert single.json()["disease"] == "Tomato Early Blight"

    listing = client.get("/api/v1/predictions")
    assert listing.status_code == 200
    assert listing.json()["pagination"]["total"] >= 1
    assert any(item["id"] == created["id"] for item in listing.json()["items"])


def test_delete_then_404(client, sample_leaf_bytes):
    created = _analyze(client, sample_leaf_bytes).json()["prediction"]

    deleted = client.delete(f"/api/v1/predictions/{created['id']}")
    assert deleted.status_code == 200
    assert deleted.json()["success"] is True

    missing = client.get(f"/api/v1/predictions/{created['id']}")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "NOT_FOUND"


def test_history_filters_and_sorting(client, sample_leaf_bytes):
    _analyze(client, sample_leaf_bytes)
    _analyze(client, sample_leaf_bytes, name="second.png")

    filtered = client.get("/api/v1/predictions", params={"status": "diseased", "plant": "tomato"})
    assert filtered.status_code == 200
    assert all(item["plant"] == "Tomato" for item in filtered.json()["items"])

    searched = client.get("/api/v1/predictions", params={"search": "early"})
    assert searched.status_code == 200
    assert searched.json()["pagination"]["total"] >= 1

    sorted_desc = client.get("/api/v1/predictions", params={"sort": "confidence"})
    assert sorted_desc.status_code == 200

    invalid_status = client.get("/api/v1/predictions", params={"status": "bogus"})
    assert invalid_status.status_code == 422


def test_predict_without_model_returns_503(client, sample_leaf_bytes):
    client.app.state.prediction_service.model = None
    response = _analyze(client, sample_leaf_bytes)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "MODEL_NOT_LOADED"


@pytest.mark.integration
def test_predict_with_trained_artifact(sample_leaf_bytes):
    """End-to-end test with the real trained model (skipped if not trained yet)."""
    artifact = (
        Path(__file__).resolve().parents[1] / "app" / "ml" / "artifacts" / "leafguard_model.joblib"
    )
    if not artifact.is_file():
        pytest.skip("Trained model artifact not found — run ml/training/train.py first.")

    from app.ml.model_service import ClassicalModelService

    model = ClassicalModelService(artifact)
    result = model.predict(sample_leaf_bytes)
    assert result.label in KNOWN_LABELS
    assert 0 <= result.confidence <= 100
