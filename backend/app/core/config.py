"""Application settings loaded from environment variables / .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "LeafGuard AI"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "leafguard"

    model_path: Path = BACKEND_DIR / "app" / "ml" / "artifacts" / "leafguard_model.joblib"

    frontend_url: str = "http://localhost:5173,http://localhost:3000"
    max_upload_size_mb: int = 10

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
