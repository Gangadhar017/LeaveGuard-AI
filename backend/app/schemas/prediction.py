"""Pydantic response models — the public API contract."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TopPrediction(BaseModel):
    label: str
    confidence: float


class PredictionOut(BaseModel):
    id: str
    plant: str
    disease: str
    is_healthy: bool
    confidence: float = Field(description="Confidence percentage, 0-100")
    image_name: str
    thumbnail: str | None = None
    processing_time: float
    model_name: str
    top_predictions: list[TopPrediction] = []
    created_at: datetime


class Recommendation(BaseModel):
    description: str
    symptoms: list[str]
    prevention: list[str]
    treatment: list[str]
    severity: str


class PredictResponse(BaseModel):
    success: bool
    prediction: PredictionOut
    recommendation: Recommendation


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class PredictionsListResponse(BaseModel):
    success: bool
    items: list[PredictionOut]
    pagination: Pagination


class DeleteResponse(BaseModel):
    success: bool
    message: str


class DiseaseCount(BaseModel):
    name: str
    count: int


class MostDetected(BaseModel):
    disease: str
    count: int


class StatsResponse(BaseModel):
    total_predictions: int
    healthy_count: int
    diseased_count: int
    average_confidence: float | None
    most_detected_disease: MostDetected | None
    by_plant: list[DiseaseCount]
    top_diseases: list[DiseaseCount]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None
    database: str
    version: str


class ApiInfo(BaseModel):
    name: str
    version: str
    description: str
    docs_url: str
