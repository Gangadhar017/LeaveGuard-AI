"""Leaf image preprocessing and feature extraction.

This module is the single source of truth for image preprocessing. It is used
by BOTH the training pipeline (ml/training) and the inference API
(backend/app/services) so that the features a model was trained on are exactly
the features computed at serving time (no train/serve skew).

Pipeline (classical ML, no deep learning required):
    bytes -> decode -> resize 256x256 -> Gaussian denoise -> HSV leaf mask
          -> segmentation -> [color histograms | channel stats | lesion stats
             | LBP texture | HOG gradients] -> 1-D float32 feature vector
"""

from __future__ import annotations

import cv2
import numpy as np

TARGET_SIZE = (256, 256)

# HSV ranges (OpenCV: H in [0,179], S/V in [0,255])
_LEAF_HUE = (25, 95)          # green foliage
_LEAF_SAT = 40
_LEAF_VAL = 40
_LESION_HUE = (0, 38)         # brown / necrotic tissue
_YELLOW_HUE = (20, 38)        # chlorosis
_MIN_SAT = 50

# LBP (uniform, P=8, R=1) -> P+2 histogram bins
_LBP_P = 8
_LBP_BINS = _LBP_P + 2

# HOG computed on a 64x64 grayscale patch: 8x8 px cells, 9 unsigned gradient
# bins, 16x16 px blocks with 8 px stride and L2-Hys normalization.
# Blocks: 7x7 x (2x2 cells x 9 bins) = 1764 dims.
_HOG_SIZE = 64
_HOG_CELL = 8
_HOG_BINS = 9
_HOG_BIN_WIDTH = 180.0 / _HOG_BINS

FEATURE_VERSION = "v1-hist46-stats16-lbp10-hog1764"


class InvalidImageError(ValueError):
    """Raised when bytes cannot be decoded as a usable image."""


# --------------------------------------------------------------------------- #
# Preprocessing steps
# --------------------------------------------------------------------------- #
def load_image_from_bytes(data: bytes) -> np.ndarray:
    """Decode raw bytes into a BGR image. Raises InvalidImageError on failure."""
    if not data:
        raise InvalidImageError("Image file is empty.")
    array = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise InvalidImageError("Could not decode the uploaded file as an image.")
    return image


def resize_image(image: np.ndarray, size: tuple[int, int] = TARGET_SIZE) -> np.ndarray:
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def reduce_noise(image: np.ndarray) -> np.ndarray:
    """5x5 Gaussian blur suppresses JPEG/sensor noise before gradients."""
    return cv2.GaussianBlur(image, (5, 5), 0)


def to_hsv(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


def leaf_mask(hsv: np.ndarray) -> np.ndarray:
    """Binary mask of leaf pixels.

    Primary rule: green-hued, reasonably saturated pixels. Fallback for
    non-green leaves / odd lighting: any saturated non-gray region. As a last
    resort the whole frame is kept so features degrade gracefully instead of
    crashing. Morphological opening/closing removes speckle, and only the
    largest connected component is kept (drops stray background blobs).
    """
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    mask = (
        (h >= _LEAF_HUE[0]) & (h <= _LEAF_HUE[1])
        & (s >= _LEAF_SAT) & (v >= _LEAF_VAL)
    ).astype(np.uint8) * 255

    if cv2.countNonZero(mask) < 0.05 * mask.size:
        mask = ((s >= 60) & (v >= 60)).astype(np.uint8) * 255
    if cv2.countNonZero(mask) < 0.02 * mask.size:
        return np.full_like(mask, 255)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [largest], -1, 255, thickness=cv2.FILLED)
    return mask


def segment_leaf(image_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Return the leaf with the background zeroed out."""
    return cv2.bitwise_and(image_bgr, image_bgr, mask=mask)


def preprocess(image_bgr: np.ndarray, use_denoise: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Resize (+ denoise) and return (bgr, hsv, leaf_mask)."""
    img = resize_image(image_bgr)
    if use_denoise:
        img = reduce_noise(img)
    hsv = to_hsv(img)
    return img, hsv, leaf_mask(hsv)


# --------------------------------------------------------------------------- #
# Feature extraction
# --------------------------------------------------------------------------- #
def _lbp_lookup_table() -> np.ndarray:
    """Map each 8-bit LBP pattern to its 'uniform' label (0..P, else P+1)."""
    table = np.zeros(1 << _LBP_P, dtype=np.int32)
    for value in range(1 << _LBP_P):
        ones = bin(value).count("1")
        transitions = sum(
            ((value >> i) & 1) != ((value >> ((i + 1) % _LBP_P)) & 1)
            for i in range(_LBP_P)
        )
        table[value] = ones if transitions <= 2 else _LBP_P + 1
    return table


_LBP_TABLE = _lbp_lookup_table()


def color_histograms(hsv: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Normalized H/S/V histograms over leaf pixels (distribution of leaf and
    lesion coloration is the strongest classical signal for leaf disease)."""
    h_hist = cv2.calcHist([hsv], [0], mask, [18], [0, 180])
    s_hist = cv2.calcHist([hsv], [1], mask, [16], [0, 256])
    v_hist = cv2.calcHist([hsv], [2], mask, [12], [0, 256])
    hist = np.concatenate([h_hist, s_hist, v_hist]).ravel()
    total = hist.sum()
    return hist / total if total > 0 else hist


def channel_statistics(bgr: np.ndarray, hsv: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Mean/std of each channel over the leaf + domain ratios
    (leaf coverage, necrotic ratio, chlorotic ratio, edge density)."""
    b, g, r = cv2.split(bgr)
    h, s, v = cv2.split(hsv)
    m = mask > 0
    count = int(m.sum())

    def mean_std(plane: np.ndarray) -> list[float]:
        if count == 0:
            return [0.0, 0.0]
        pixels = plane[m].astype(np.float32)
        return [float(pixels.mean()), float(pixels.std())]

    stats: list[float] = []
    for plane in (b, g, r, h, s, v):
        stats.extend(mean_std(plane))

    stats.append(count / mask.size)  # leaf coverage

    lesion = (
        (h >= _LESION_HUE[0]) & (h <= _LESION_HUE[1])
        & (s >= _MIN_SAT) & (v <= 210) & m
    )
    yellow = (
        (h >= _YELLOW_HUE[0]) & (h <= _YELLOW_HUE[1]) & (s >= 60) & m
    )
    stats.append(float(lesion.sum()) / count if count else 0.0)
    stats.append(float(yellow.sum()) / count if count else 0.0)

    edges = cv2.Canny(bgr, 100, 200)
    stats.append(float((edges > 0)[m].mean()) if count else 0.0)

    return np.array(stats, dtype=np.float32)


def lbp_texture(gray: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Uniform LBP histogram — captures lesion texture independent of color."""
    g = gray.astype(np.int16)
    centers = g[1:-1, 1:-1]
    pattern = np.zeros(centers.shape, np.uint8)
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for i, (dy, dx) in enumerate(offsets):
        neighbor = g[1 + dy: g.shape[0] - 1 + dy, 1 + dx: g.shape[1] - 1 + dx]
        pattern |= ((neighbor >= centers).astype(np.uint8) << i)

    labels = _LBP_TABLE[pattern.ravel()].reshape(centers.shape)
    center_mask = mask[1:-1, 1:-1] > 0
    if not center_mask.any():
        return np.zeros(_LBP_BINS, dtype=np.float32)
    hist = np.bincount(labels[center_mask], minlength=_LBP_BINS).astype(np.float32)
    return hist / hist.sum()


def hog_gradients(seg_bgr: np.ndarray) -> np.ndarray:
    """HOG on the segmented leaf at 64x64 (numpy implementation — OpenCV 5
    removed HOGDescriptor). Reacts to spots, rings and lesion edges."""
    gray = cv2.cvtColor(seg_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (_HOG_SIZE, _HOG_SIZE), interpolation=cv2.INTER_AREA)
    gray = gray.astype(np.float32)

    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = np.sqrt(gx * gx + gy * gy)
    angle = np.rad2deg(np.arctan2(gy, gx)) % 180.0
    bins = np.minimum((angle // _HOG_BIN_WIDTH).astype(np.int32), _HOG_BINS - 1)

    # accumulate weighted votes into 8x8 cells
    cell_ids = (np.arange(_HOG_SIZE) // _HOG_CELL)[:, None] * (_HOG_SIZE // _HOG_CELL) + (
        np.arange(_HOG_SIZE) // _HOG_CELL
    )[None, :]
    cell_hist = np.bincount(
        (cell_ids.ravel() * _HOG_BINS + bins.ravel()),
        weights=magnitude.ravel(),
        minlength=(_HOG_SIZE // _HOG_CELL) ** 2 * _HOG_BINS,
    ).reshape(_HOG_SIZE // _HOG_CELL, _HOG_SIZE // _HOG_CELL, _HOG_BINS)

    # 2x2-cell blocks with stride 1 cell, L2-Hys normalization
    n_blocks = _HOG_SIZE // _HOG_CELL - 1
    blocks = np.empty((n_blocks * n_blocks, 4 * _HOG_BINS), dtype=np.float32)
    for by in range(n_blocks):
        for bx in range(n_blocks):
            block = cell_hist[by:by + 2, bx:bx + 2].ravel()
            block /= np.sqrt((block * block).sum()) + 1e-6
            np.clip(block, 0, 0.2, out=block)
            block /= np.sqrt((block * block).sum()) + 1e-6
            blocks[by * n_blocks + bx] = block
    return blocks.ravel()


def extract_features(
    image_bgr: np.ndarray,
    use_segmentation: bool = True,
    use_denoise: bool = True,
) -> np.ndarray:
    """Full feature vector for one BGR image (any resolution)."""
    img, hsv, mask = preprocess(image_bgr, use_denoise=use_denoise)
    if use_segmentation:
        seg = segment_leaf(img, mask)
    else:
        seg = img

    return np.concatenate([
        color_histograms(hsv, mask),
        channel_statistics(img, hsv, mask),
        lbp_texture(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), mask),
        hog_gradients(seg),
    ]).astype(np.float32)


def extract_features_from_bytes(
    data: bytes,
    use_segmentation: bool = True,
    use_denoise: bool = True,
) -> np.ndarray:
    return extract_features(
        load_image_from_bytes(data),
        use_segmentation=use_segmentation,
        use_denoise=use_denoise,
    )


def feature_dim() -> int:
    probe = np.zeros((32, 32, 3), dtype=np.uint8)
    probe[:] = (60, 140, 60)
    return int(extract_features(probe).shape[0])
