"""Consistent API error responses.

Every error returned by the API has the same shape:

    {"success": false, "error": {"code": "INVALID_IMAGE", "message": "..."}}

Internal details (stack traces, driver errors) are logged but never leaked.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    code = "APP_ERROR"
    status = 500
    message = "An unexpected error occurred."

    def __init__(self, message: str | None = None, *, code: str | None = None, status: int | None = None):
        self.message = message or self.message
        self.code = code or self.code
        self.status = status or self.status
        super().__init__(self.message)


class InvalidImageError(AppError):
    code = "INVALID_IMAGE"
    status = 422
    message = "Please upload a valid leaf image."


class UnsupportedFileTypeError(AppError):
    code = "UNSUPPORTED_FILE_TYPE"
    status = 415
    message = "Unsupported file type. Allowed: JPG, JPEG, PNG, WEBP."


class FileTooLargeError(AppError):
    code = "FILE_TOO_LARGE"
    status = 413
    message = "The uploaded file is too large."


class ModelNotLoadedError(AppError):
    code = "MODEL_NOT_LOADED"
    status = 503
    message = "The ML model is not available. Please try again later."


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status = 404
    message = "The requested resource was not found."


class RepositoryError(AppError):
    code = "REPOSITORY_ERROR"
    status = 500
    message = "Failed to access the prediction storage."


def _error_response(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"success": False, "error": {"code": code, "message": message}})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        logger.warning("%s: %s", exc.code, exc.message)
        return _error_response(exc.code, exc.message, exc.status)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(p) for p in first.get("loc", []) if p != "body")
        message = f"Invalid request: {field or 'payload'} — {first.get('msg', 'validation failed')}"
        return _error_response("VALIDATION_ERROR", message, 422)

    @app.exception_handler(ValidationError)
    async def pydantic_handler(_: Request, exc: ValidationError) -> JSONResponse:
        logger.error("Response validation failed: %s", exc)
        return _error_response("RESPONSE_VALIDATION_ERROR", "The server produced an invalid response.", 500)

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return _error_response("INTERNAL_SERVER_ERROR", "An unexpected error occurred.", 500)
