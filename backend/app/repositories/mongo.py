"""MongoDB prediction repository (pymongo, sync — routes run in threadpool)."""

from __future__ import annotations

from datetime import timezone

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

from app.core.exceptions import NotFoundError, RepositoryError
from app.models.prediction import PredictionRecord
from app.repositories.base import PredictionRepository
from app.repositories.memory import _compute_stats

_SORTS = {"newest": ("created_at", DESCENDING), "oldest": ("created_at", ASCENDING),
          "confidence": ("confidence", DESCENDING)}


def _to_record(doc: dict) -> PredictionRecord:
    return PredictionRecord(
        id=str(doc["_id"]),
        plant=doc["plant"],
        disease=doc["disease"],
        is_healthy=doc["is_healthy"],
        confidence=doc["confidence"],
        image_name=doc["image_name"],
        processing_time=doc["processing_time"],
        model_name=doc["model_name"],
        top_predictions=doc.get("top_predictions", []),
        thumbnail=doc.get("thumbnail"),
        created_at=doc["created_at"].astimezone(timezone.utc),
    )


class MongoPredictionRepository(PredictionRepository):
    name = "mongodb"

    def __init__(self, uri: str, database: str, server_selection_timeout_ms: int = 3000):
        self._client = MongoClient(
            uri,
            serverSelectionTimeoutMS=server_selection_timeout_ms,
            appname="leafguard-ai",
        )
        self._collection = self._client[database]["predictions"]

    def ensure_ready(self) -> None:
        """Fail fast if the server is unreachable, and create indexes."""
        self._client.admin.command("ping")
        self._collection.create_index([("created_at", DESCENDING)])
        self._collection.create_index([("plant", ASCENDING)])
        self._collection.create_index([("disease", ASCENDING)])

    def add(self, record: PredictionRecord) -> PredictionRecord:
        try:
            doc = record.__dict__.copy()
            doc.pop("id")
            result = self._collection.insert_one(doc)
            record.id = str(result.inserted_id)
            return record
        except PyMongoError as exc:
            raise RepositoryError(f"Could not store prediction: {exc.code}") from exc

    def get(self, record_id: str) -> PredictionRecord:
        try:
            doc = self._collection.find_one({"_id": ObjectId(record_id)})
        except InvalidId as exc:
            raise NotFoundError(f"Prediction '{record_id}' was not found.") from exc
        except PyMongoError as exc:
            raise RepositoryError("Could not read prediction storage.") from exc
        if doc is None:
            raise NotFoundError(f"Prediction '{record_id}' was not found.")
        return _to_record(doc)

    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        plant: str | None = None,
        status: str | None = None,
        sort: str = "newest",
    ) -> tuple[list[PredictionRecord], int]:
        query: dict = {}
        if search:
            query["$or"] = [
                {"disease": {"$regex": _escape(search), "$options": "i"}},
                {"plant": {"$regex": _escape(search), "$options": "i"}},
            ]
        if plant:
            query["plant"] = {"$regex": f"^{_escape(plant)}$", "$options": "i"}
        if status in {"healthy", "diseased"}:
            query["is_healthy"] = status == "healthy"

        sort_field, sort_dir = _SORTS.get(sort, _SORTS["newest"])
        try:
            total = self._collection.count_documents(query)
            cursor = (
                self._collection.find(query)
                .sort(sort_field, sort_dir)
                .skip((page - 1) * page_size)
                .limit(page_size)
            )
            return [_to_record(doc) for doc in cursor], total
        except PyMongoError as exc:
            raise RepositoryError("Could not read prediction storage.") from exc

    def delete(self, record_id: str) -> None:
        try:
            result = self._collection.delete_one({"_id": ObjectId(record_id)})
        except InvalidId as exc:
            raise NotFoundError(f"Prediction '{record_id}' was not found.") from exc
        except PyMongoError as exc:
            raise RepositoryError("Could not delete prediction.") from exc
        if result.deleted_count == 0:
            raise NotFoundError(f"Prediction '{record_id}' was not found.")

    def stats(self) -> dict:
        try:
            docs = list(self._collection.find({}, {
                "is_healthy": 1, "confidence": 1, "plant": 1, "disease": 1,
            }))
        except PyMongoError as exc:
            raise RepositoryError("Could not compute statistics.") from exc
        records = [
            PredictionRecord(
                plant=d["plant"], disease=d["disease"], is_healthy=d["is_healthy"],
                confidence=d["confidence"], image_name="", processing_time=0, model_name="",
            )
            for d in docs
        ]
        return _compute_stats(records)


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\")
