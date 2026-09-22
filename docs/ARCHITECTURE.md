# LeafGuard AI — Architecture Deep Dive

This document explains the internal architecture of LeafGuard AI in detail, covering every
layer from the browser to the ML artifact on disk.

---

## System Overview

```
Browser (React SPA)
    │  multipart/form-data upload + REST JSON
    ▼
FastAPI Backend  (:8000)
    ├── Image Validator   — magic-byte · size · OpenCV decode check
    ├── Prediction Service — orchestrates validation → model → knowledge-base lookup → persist
    ├── Model Service       — scikit-learn pipeline loaded from joblib bundle
    ├── Knowledge Base      — Python dict of disease metadata (symptoms, treatment, prevention)
    └── Repository Layer    — MongoDB (Atlas / local) with in-memory fallback
             │
             ▼
        MongoDB  (predictions collection + thumbnail binary)
```

---

## Frontend — React SPA

| Concern            | Implementation |
|--------------------|----------------|
| Build tooling      | Vite 5 |
| Routing            | React Router v6 |
| Styling            | Tailwind CSS |
| HTTP client        | Axios with custom error mapping |
| Charts             | Recharts |
| Icons              | Lucide React |
| Testing            | Vitest + Testing Library |

### Key pages
- `/` — Landing page (hero, features, how-it-works).
- `/analyse` — Upload zone + prediction result card.
- `/history` — Paginated history with search / filter.
- `/dashboard` — Live statistics charts.
- `/about` — Metrics, model info, team.

### Data-fetching pattern
Custom hooks (`useHistory`, `useStats`) wrap Axios calls and return `{ data, loading, error }`
triples. Components remain pure display layers.

---

## Backend — FastAPI

### Request lifecycle

```
POST /api/v1/predictions
    1. Middleware: CORS headers, structured request logging
    2. Route handler receives UploadFile
    3. ImageValidator:
         a. Check MIME type allowlist
         b. Check file size ≤ 10 MB
         c. Read first 12 bytes → magic-byte check (JPEG / PNG)
         d. Decode full image with OpenCV — reject if corrupt
    4. PredictionService.predict(image_bytes)
         a. ModelService.predict(image_bytes) → class, confidence, top-3
         b. KnowledgeBase.lookup(class) → disease metadata
         c. ThumbnailHelper.generate(image_bytes) → JPEG thumbnail bytes
         d. Repository.save(PredictionRecord) → MongoDB insert
    5. Return PredictionResponse JSON
```

### Repository abstraction

`BaseRepository` defines the CRUD + stats interface.  
`MongoRepository` implements it against MongoDB.  
`InMemoryRepository` is the automatic fallback when MongoDB is unreachable — useful for
development without a running database.

### Model-service abstraction

`BaseDiseaseModel` is an abstract base class with a single `predict(image_bytes)` method.
`SklearnDiseaseModel` wraps the joblib bundle.  
To swap in a CNN: subclass `BaseDiseaseModel`, point the DI binding at the new class, done —
no API changes required.

---

## ML Pipeline — scikit-learn

### Feature extraction (`preprocessor.py`)

Each image goes through:
1. Resize to **128 × 128** px.
2. Convert to **HSV** colour space.
3. Compute histogram per channel (32 bins) → 96 features.
4. Extract **ORB** keypoint descriptors → bag-of-words (50-word vocabulary) → 50 features.
5. Compute **LBP** texture histogram → 26 features.
6. Flatten and concatenate → **1 836-dimensional** feature vector.

### Training pipeline (`train.py`)

1. Stratified 80 / 10 / 10 split (train / val / test).
2. Grid-search over Random Forest (`n_estimators`, `max_depth`, `min_samples_split`) and a
   baseline SVM.
3. Best model evaluated on held-out test set → metrics written to `ml/evaluation/metrics.json`.
4. Pipeline (scaler → model) serialised with `joblib` → `ml/artifacts/model_bundle.joblib`.

### Disease classes (9 total)

| Index | Class |
|-------|-------|
| 0 | Potato — Early Blight |
| 1 | Potato — Late Blight |
| 2 | Potato — Healthy |
| 3 | Tomato — Early Blight |
| 4 | Tomato — Late Blight |
| 5 | Tomato — Leaf Mold |
| 6 | Tomato — Septoria Leaf Spot |
| 7 | Tomato — Target Spot |
| 8 | Tomato — Healthy |

---

## Data Storage — MongoDB

Single collection: `predictions`.

```json
{
  "_id":            "ObjectId",
  "predicted_class":"string",
  "confidence":     "float",
  "top_predictions":"array",
  "disease_info":   "object",
  "thumbnail":      "Binary (JPEG bytes)",
  "created_at":     "ISODate"
}
```

Indexes:
- `created_at` descending — fast history pagination.
- `predicted_class` — fast per-disease filtering.

---

## CI/CD

- **GitHub Actions** — runs backend pytest + frontend Vite build on every push to `main`.
- **Render** — backend auto-deploys from `render.yaml` blueprint.
- **Vercel** — frontend auto-deploys; `vercel.json` rewrites `/api/*` to the Render backend.
- **Docker Compose** — local full-stack: `docker compose up --build`.
