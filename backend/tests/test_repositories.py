"""In-memory repository behaviour (mirrors the MongoDB contract)."""

import pytest

from app.core.exceptions import NotFoundError
from app.models.prediction import PredictionRecord
from app.repositories.memory import InMemoryPredictionRepository


def make_record(disease="Tomato Early Blight", plant="Tomato", healthy=False, confidence=90.0):
    return PredictionRecord(
        plant=plant,
        disease=disease,
        is_healthy=healthy,
        confidence=confidence,
        image_name="leaf.jpg",
        processing_time=0.1,
        model_name="stub",
    )


def test_add_assigns_id_and_get_roundtrip():
    repo = InMemoryPredictionRepository()
    record = repo.add(make_record())
    assert record.id
    assert repo.get(record.id).disease == "Tomato Early Blight"


def test_get_unknown_id_raises():
    repo = InMemoryPredictionRepository()
    with pytest.raises(NotFoundError):
        repo.get("does-not-exist")


def test_list_pagination_and_sort():
    repo = InMemoryPredictionRepository()
    repo.add(make_record(confidence=50.0))
    repo.add(make_record(confidence=99.0))
    repo.add(make_record(confidence=75.0))

    page1, total = repo.list(page=1, page_size=2, sort="confidence")
    assert total == 3
    assert [r.confidence for r in page1] == [99.0, 75.0]

    page2, _ = repo.list(page=2, page_size=2, sort="confidence")
    assert [r.confidence for r in page2] == [50.0]


def test_search_and_status_filters():
    repo = InMemoryPredictionRepository()
    repo.add(make_record())
    repo.add(make_record(disease="Tomato Healthy", healthy=True))

    diseased, _ = repo.list(status="diseased")
    assert len(diseased) == 1

    found, total = repo.list(search="healthy")
    assert total == 1
    assert found[0].is_healthy is True


def test_delete_removes_record():
    repo = InMemoryPredictionRepository()
    record = repo.add(make_record())
    repo.delete(record.id)
    with pytest.raises(NotFoundError):
        repo.get(record.id)


def test_stats_aggregation():
    repo = InMemoryPredictionRepository()
    repo.add(make_record())
    repo.add(make_record())
    repo.add(make_record(disease="Potato Late Blight", plant="Potato"))
    repo.add(make_record(disease="Tomato Healthy", healthy=True))

    stats = repo.stats()
    assert stats["total_predictions"] == 4
    assert stats["healthy_count"] == 1
    assert stats["diseased_count"] == 3
    assert stats["most_detected_disease"]["disease"] == "Tomato Early Blight"
    assert stats["most_detected_disease"]["count"] == 2
    assert {"name": "Tomato", "count": 3} in stats["by_plant"]
    assert stats["top_diseases"][0]["name"] == "Tomato Early Blight"
