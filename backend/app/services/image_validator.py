"""Upload validation: size limits, extension allowlist and magic-byte checks.

Content-Type headers are client-controlled, so real file contents are
verified via magic bytes before anything is decoded.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.core.exceptions import (
    FileTooLargeError,
    InvalidImageError,
    UnsupportedFileTypeError,
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

_MAGIC_CHECKS: list[tuple[bytes, int, str]] = [
    (b"\xff\xd8\xff", 3, "JPEG"),
    (b"\x89PNG\r\n\x1a\n", 8, "PNG"),
]
_WEBP_MAGIC = b"WEBP"


def validate_upload(data: bytes, filename: str | None, max_bytes: int) -> None:
    if not data:
        raise InvalidImageError("The uploaded file is empty.")

    if len(data) > max_bytes:
        raise FileTooLargeError(
            f"The uploaded file is too large. Maximum allowed size is {max_bytes // (1024 * 1024)} MB."
        )

    if len(data) < 64:
        raise InvalidImageError("The uploaded file is too small to be a valid image.")

    if filename:
        extension = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
        if extension not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError()

    kind = _detect_format(data)
    if kind is None:
        raise UnsupportedFileTypeError(
            "File contents do not look like a supported image (JPG, PNG or WEBP)."
        )

    # contents claim to be an image — make sure OpenCV can actually decode it
    if cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR) is None:
        raise InvalidImageError("Could not decode the uploaded file as an image.")


def _detect_format(data: bytes) -> str | None:
    for magic, length, kind in _MAGIC_CHECKS:
        if data[:length] == magic:
            return kind
    if data[:4] == b"RIFF" and data[8:12] == _WEBP_MAGIC:
        return "WEBP"
    return None
