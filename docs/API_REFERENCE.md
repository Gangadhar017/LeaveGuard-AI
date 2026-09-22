# LeafGuard AI — API Reference

Base URL (local): `http://localhost:8000/api/v1`  
Base URL (production): Set by `VITE_API_URL` / `API_BASE_URL` environment variable.

All requests and responses use `application/json` unless a multipart upload is indicated.

---

## Health

### `GET /health`

Returns the service liveness status.

**Response `200 OK`**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Predictions

### `POST /predictions`

Upload a leaf image for disease prediction.

**Request** — `multipart/form-data`

| Field  | Type | Required | Description                          |
|--------|------|----------|--------------------------------------|
| `file` | File | ✅       | JPEG or PNG leaf image (max 10 MB).  |

**Response `200 OK`**
```json
{
  "id": "64f1a2b3c4d5e6f7a8b9c0d1",
  "predicted_class": "Tomato___Early_blight",
  "confidence": 0.8731,
  "top_predictions": [
    { "class": "Tomato___Early_blight",  "confidence": 0.8731 },
    { "class": "Tomato___Late_blight",   "confidence": 0.0814 },
    { "class": "Tomato___healthy",       "confidence": 0.0211 }
  ],
  "disease_info": {
    "display_name": "Early Blight",
    "plant": "Tomato",
    "description": "Fungal disease caused by Alternaria solani ...",
    "symptoms": ["Dark concentric-ring lesions", "Yellowing around spots"],
    "prevention": ["Crop rotation", "Resistant varieties"],
    "treatment": ["Apply copper-based fungicide", "Remove infected leaves"]
  },
  "thumbnail_url": "/api/v1/predictions/64f1a2b3c4d5e6f7a8b9c0d1/thumbnail",
  "created_at": "2025-07-01T10:23:45.123Z"
}
```

**Error responses**

| Status | Reason |
|--------|--------|
| `400`  | Invalid file type, size exceeds limit, or image cannot be decoded. |
| `422`  | Validation error (missing field). |
| `500`  | Internal server error during prediction. |

---

### `GET /predictions`

Retrieve paginated prediction history.

**Query parameters**

| Parameter  | Type    | Default | Description                                |
|------------|---------|---------|--------------------------------------------|
| `page`     | integer | `1`     | Page number (1-indexed).                   |
| `page_size`| integer | `20`    | Items per page (max 100).                  |
| `plant`    | string  | —       | Filter by plant name (e.g. `Tomato`).      |
| `disease`  | string  | —       | Filter by disease class substring.         |
| `sort`     | string  | `desc`  | Sort by `created_at`: `asc` or `desc`.     |

**Response `200 OK`**
```json
{
  "items": [ { /* prediction object (see above) */ } ],
  "total": 142,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

---

### `GET /predictions/{id}`

Retrieve a single prediction by ID.

**Path parameters**

| Parameter | Type   | Description         |
|-----------|--------|---------------------|
| `id`      | string | MongoDB ObjectId.   |

**Response `200 OK`** — single prediction object.  
**Response `404 Not Found`** — prediction does not exist.

---

### `DELETE /predictions/{id}`

Delete a prediction record.

**Response `204 No Content`** — successfully deleted.  
**Response `404 Not Found`** — prediction does not exist.

---

### `GET /predictions/{id}/thumbnail`

Returns the stored thumbnail image for a prediction.

**Response `200 OK`** — `image/jpeg` binary stream.  
**Response `404 Not Found`** — thumbnail not available.

---

## Statistics

### `GET /stats`

Returns aggregated statistics for the dashboard.

**Response `200 OK`**
```json
{
  "total_predictions": 142,
  "healthy_count": 43,
  "diseased_count": 99,
  "top_diseases": [
    { "class": "Tomato___Early_blight", "count": 31 },
    { "class": "Potato___Late_blight",  "count": 24 }
  ],
  "by_plant": {
    "Tomato": 89,
    "Potato": 53
  }
}
```

---

## Error Response Schema

All error responses share the same envelope:

```json
{
  "detail": "Human-readable error message"
}
```
