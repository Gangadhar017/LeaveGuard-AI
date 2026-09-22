"""Thread-safe in-memory prediction repository (dev fallback).

Used when MongoDB is unreachable so the whole product still works end to end.
Data lives only for the lifetime of the process — a warning is logged at
startup when this backend is selected.
"""

from __future__ import annotations

import re
import threading
import uuid

from app.core.exceptions import NotFoundError
from app.models.prediction import PredictionRecord
from app.repositories.base import PredictionRepository

_SORTS = {
    "newest": lambda r: r.created_at,
    "oldest": lambda r: r.created_at,
    "confidence": lambda r: r.confidence,
}


class InMemoryPredictionRepository(PredictionRepository):
    name = "in-memory"

    def __init__(self) -> None:
        self._records: list[PredictionRecord] = []
        self._lock = threading.Lock()

    def add(self, record: PredictionRecord) -> PredictionRecord:
        record.id = str(uuid.uuid4())
        with self._lock:
            self._records.append(record)
        return record

    def get(self, record_id: str) -> PredictionRecord:
        with self._lock:
            for record in self._records:
                if record.id == record_id:
                    return record
        raise NotFoundError(f"Prediction '{record_id}' was not found.")

    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        plant: str | None = None,
        status: str | None = None,
        sort: str = "newest",
    ) -> tuple[list[PredictionRecord], int]:
        with self._lock:
            records = list(self._records)

        if search:
            needle = search.lower()
            records = [r for r in records if needle in r.disease.lower() or needle in r.plant.lower()]
        if plant:
            records = [r for r in records if r.plant.lower() == plant.lower()]
        if status in {"healthy", "diseased"}:
            records = [r for r in records if r.is_healthy == (status == "healthy")]

        key = _SORTS.get(sort, _SORTS["newest"])
        records.sort(key=key, reverse=(sort != "oldest"))

        total = len(records)
        start = (page - 1) * page_size
        return records[start: start + page_size], total

    def delete(self, record_id: str) -> None:
        with self._lock:
            for i, record in enumerate(self._records):
                if record.id == record_id:
                    del self._records[i]
                    return
        raise NotFoundError(f"Prediction '{record_id}' was not found.")

    def stats(self) -> dict:
        with self._lock:
            records = list(self._records)
        return _compute_stats(records)


def _compute_stats(records: list[PredictionRecord]) -> dict:
    total = len(records)
    healthy = sum(1 for r in records if r.is_healthy)
    avg_conf = round(sum(r.confidence for r in records) / total, 2) if total else None

    disease_counts: dict[str, int] = {}
    plant_counts: dict[str, int] = {}
    for r in records:
        plant_counts[r.plant] = plant_counts.get(r.plant, 0) + 1
        if not r.is_healthy:
            disease_counts[r.disease] = disease_counts.get(r.disease, 0) + 1

    top = sorted(disease_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    plants = sorted(plant_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "total_predictions": total,
        "healthy_count": healthy,
        "diseased_count": total - healthy,
        "average_confidence": avg_conf,
        "most_detected_disease": {"disease": top[0][0], "count": top[0][1]} if top else None,
        "by_plant": [{"name": n, "count": c} for n, c in plants],
        "top_diseases": [{"name": n, "count": c} for n, c in top[:8]],
    }
