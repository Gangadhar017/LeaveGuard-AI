"""Tests for OpenCV preprocessing and feature extraction."""

import cv2
import numpy as np
import pytest

from app.ml import preprocessing as prep


@pytest.fixture()
def green_leaf_image():
    """A synthetic 'leaf': green ellipse with dark brown lesion spots on white bg."""
    image = np.full((160, 200, 3), (255, 255, 255), dtype=np.uint8)
    cv2.ellipse(image, (100, 80), (85, 60), 20, 0, 360, (40, 160, 60), -1)
    for x, y in ((70, 70), (130, 95)):
        cv2.circle(image, (x, y), 9, (30, 40, 90), -1)
    return image


def test_load_image_from_bytes_roundtrip(green_leaf_image):
    ok, buffer = cv2.imencode(".jpg", green_leaf_image)
    assert ok
    decoded = prep.load_image_from_bytes(buffer.tobytes())
    assert decoded is not None
    assert decoded.shape[:2] == (160, 200)


def test_load_image_rejects_garbage():
    with pytest.raises(prep.InvalidImageError):
        prep.load_image_from_bytes(b"definitely not an image" * 5)
    with pytest.raises(prep.InvalidImageError):
        prep.load_image_from_bytes(b"")


def test_resize_and_denoise_shapes(green_leaf_image):
    resized = prep.resize_image(green_leaf_image)
    assert resized.shape[:2] == prep.TARGET_SIZE
    denoised = prep.reduce_noise(resized)
    assert denoised.shape == resized.shape


def test_leaf_mask_covers_leaf_not_background(green_leaf_image):
    _, hsv, mask = prep.preprocess(green_leaf_image)
    coverage = cv2.countNonZero(mask) / mask.size
    assert 0.3 < coverage < 1.0  # leaf found, white background mostly excluded


def test_feature_vector_shape_and_determinism(green_leaf_image):
    features_a = prep.extract_features(green_leaf_image)
    features_b = prep.extract_features(green_leaf_image)
    assert features_a.dtype == np.float32
    assert features_a.shape == (prep.feature_dim(),)
    assert features_a.shape[0] == 1836  # 46 hist + 16 stats + 10 lbp + 1764 hog
    np.testing.assert_array_equal(features_a, features_b)


def test_baseline_vs_preprocessed_features_differ(green_leaf_image):
    full = prep.extract_features(green_leaf_image, use_segmentation=True, use_denoise=True)
    baseline = prep.extract_features(green_leaf_image, use_segmentation=False, use_denoise=False)
    assert full.shape == baseline.shape
    assert not np.array_equal(full, baseline)


def test_feature_dim_matches_probe():
    assert prep.feature_dim() == 1836
