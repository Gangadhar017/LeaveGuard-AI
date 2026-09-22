"""Upload validation: file type, size and content checks."""

BAD_TEXT = b"this is definitely not an image " * 10
PNG_HEADER = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def test_unsupported_extension_rejected(client, sample_leaf_bytes):
    response = client.post(
        "/api/v1/predict",
        files={"file": ("notes.txt", sample_leaf_bytes, "text/plain")},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_fake_extension_with_wrong_content_rejected(client):
    response = client.post(
        "/api/v1/predict",
        files={"file": ("evil.jpg", BAD_TEXT, "image/jpeg")},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_corrupt_image_bytes_rejected(client):
    response = client.post(
        "/api/v1/predict",
        files={"file": ("corrupt.png", PNG_HEADER, "image/png")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_IMAGE"


def test_empty_file_rejected(client):
    response = client.post(
        "/api/v1/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_IMAGE"


def test_oversized_file_rejected(client, sample_leaf_bytes):
    big = sample_leaf_bytes + b"\x00" * (3 * 1024 * 1024)  # > 2 MB test limit
    response = client.post(
        "/api/v1/predict",
        files={"file": ("big.jpg", big, "image/jpeg")},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_webp_magic_is_accepted_by_validator(client):
    from app.services.image_validator import _detect_format

    assert _detect_format(b"RIFF\x00\x00\x00\x00WEBPVP8 ") == "WEBP"
    assert _detect_format(b"\xff\xd8\xff\xe0" + b"\x00" * 20) == "JPEG"
    assert _detect_format(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20) == "PNG"
    assert _detect_format(BAD_TEXT) is None
