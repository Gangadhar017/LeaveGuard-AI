"""Shared pytest fixtures.

Tests run against the real app factory with a stubbed model and the
in-memory repository so they are fast and hermetic. One integration test
(test_predictions.py::test_predict_with_trained_artifact) uses the real
trained model when the artifact exists.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

os.environ["LOG_LEVEL"] = "WARNING"
os.environ["MAX_UPLOAD_SIZE_MB"] = "2"
os.environ["MONGODB_URI"] = "mongodb://127.0.0.1:1/leafguard_test"  # force fallback path
os.environ["MODEL_PATH"] = str(BACKEND_DIR / "app" / "ml" / "artifacts" / "leafguard_model.joblib")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import create_app  # noqa: E402
from app.ml.model_service import BaseDiseaseModel, ModelPrediction  # noqa: E402
from app.repositories.memory import InMemoryPredictionRepository  # noqa: E402
from app.services.prediction_service import PredictionService  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


class StubModel(BaseDiseaseModel):
    model_name = "stub-svm"

    def predict(self, image_bytes: bytes) -> ModelPrediction:
        return ModelPrediction(
            label="Tomato Early Blight",
            confidence=91.5,
            model_name=self.model_name,
            top_predictions=[
                {"label": "Tomato Early Blight", "confidence": 91.5},
                {"label": "Tomato Late Blight", "confidence": 5.1},
            ],
        )


def build_client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


@pytest.fixture()
def client():
    test_client = build_client()
    with test_client:
        # lifespan already ran on this app; swap in deterministic stubs
        app = test_client.app
        app.state.model = StubModel()
        app.state.repository = InMemoryPredictionRepository()
        app.state.prediction_service = PredictionService(
            model=app.state.model,
            repository=app.state.repository,
            max_upload_bytes=app.state.settings.max_upload_bytes,
        )
        yield test_client


@pytest.fixture()
def sample_leaf_bytes() -> bytes:
    return (FIXTURES / "sample_leaf.jpg").read_bytes()
