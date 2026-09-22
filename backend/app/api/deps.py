"""FastAPI dependency providers — objects live on app.state (set in lifespan)."""

from __future__ import annotations

from fastapi import Request

from app.core.config import Settings
from app.repositories.base import PredictionRepository
from app.services.prediction_service import PredictionService


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings


def get_prediction_service(request: Request) -> PredictionService:
    return request.app.state.prediction_service


def get_repository(request: Request) -> PredictionRepository:
    return request.app.state.repository
