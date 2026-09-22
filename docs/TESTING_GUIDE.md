# Testing Guide

This guide provides instructions for running and writing tests for both the backend and frontend components of **LeafGuard AI**.

---

## 🐍 Backend Testing (`pytest`)

The backend test suite is built on **pytest** and uses FastAPI's `TestClient` and `httpx` for testing endpoints asynchronously and synchronously.

### Running Backend Tests

Navigate to the `backend/` directory:

```bash
cd backend

# Install development and test dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run a specific test module
python -m pytest tests/test_predictions.py

# Run tests matching a keyword
python -m pytest -k "test_health"
```

### Backend Test Layout

```
backend/tests/
├── conftest.py              # Shared fixtures (mock DB, test client, sample images)
├── fixtures/                # Synthetic test images and fixtures
├── test_health.py           # /health endpoint and DB fallback checks
├── test_predictions.py      # /api/predict validation, inference, and error handling
├── test_repositories.py     # MongoDB vs In-Memory repository tests
└── test_validation.py       # Payload and image format validation tests
```

---

## ⚛️ Frontend Testing (`Vitest`)

The frontend uses **Vitest** with **React Testing Library** and **jsdom** for fast component and utility testing.

### Running Frontend Tests

Navigate to the `frontend/` directory:

```bash
cd frontend

# Install dependencies
npm ci

# Run tests once (CI mode)
npm test

# Run tests in interactive watch mode
npm run test:watch
```

### Frontend Test Layout

```
frontend/src/__tests__/
├── client.test.js           # API client configuration and interceptor tests
├── format.test.js           # Formatting and display utility tests
├── PredictionResult.test.jsx# Results card rendering and severity badge tests
└── UploadZone.test.jsx      # Drag-and-drop file upload component tests
```

---

## 🔄 Continuous Integration (CI)

Every pull request and push to the `main` branch automatically triggers `.github/workflows/ci.yml`. The workflow executes:

1. **Backend Job**:
   - Sets up Python 3.12
   - Installs dependencies from `requirements-dev.txt`
   - Executes `python -m pytest`
   - Verifies API application initializes without import errors
2. **Frontend Job**:
   - Sets up Node 20
   - Runs `npm ci`
   - Executes `npm test`
   - Executes `npm run build`
