"""Small image helpers shared by services."""

from __future__ import annotations

import base64

import cv2
import numpy as np

THUMBNAIL_HEIGHT = 96
THUMBNAIL_JPEG_QUALITY = 70


def make_thumbnail(data: bytes, height: int = THUMBNAIL_HEIGHT) -> str | None:
    """Decode bytes and return a small base64 JPEG data URL (~2-4 KB) for
    history/dashboard cards, or None when the image cannot be processed."""
    try:
        array = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            return None
        scale = height / image.shape[0]
        image = cv2.resize(image, (max(1, int(image.shape[1] * scale)), height))
        ok, buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), THUMBNAIL_JPEG_QUALITY])
        if not ok:
            return None
        return "data:image/jpeg;base64," + base64.b64encode(buffer.tobytes()).decode("ascii")
    except Exception:
        return None
