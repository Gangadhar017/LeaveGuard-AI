"""Repository interface for prediction storage.

The API layer depends only on this abstraction; concrete implementations are
the MongoDB repository (production / docker-compose) and an in-memory
repository (dev fallback when MongoDB is unreachable).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.prediction import PredictionRecord


class PredictionRepository(ABC):
    name: str = "abstract"

    @abstractmethod
    def add(self, record: PredictionRecord) -> PredictionRecord: ...

    @abstractmethod
    def get(self, record_id: str) -> PredictionRecord: ...

    @abstractmethod
    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        plant: str | None = None,
        status: str | None = None,
        sort: str = "newest",
    ) -> tuple[list[PredictionRecord], int]: ...

    @abstractmethod
    def delete(self, record_id: str) -> None: ...

    @abstractmethod
    def stats(self) -> dict: ...
