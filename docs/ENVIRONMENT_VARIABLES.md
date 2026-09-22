# Environment Variables Reference

This document details all configuration variables used across the **LeafGuard AI** application for both the FastAPI backend service and Vite React frontend client.

---

## 🛠 Backend Configuration

The backend reads configuration through Pydantic `BaseSettings` defined in `backend/app/core/config.py`. Values can be supplied via a `.env` file in the project root or through standard environment variables.

| Variable | Type | Default | Description | Required in Production |
|---|---|---|---|:---:|
| `MONGODB_URI` | `string` | `mongodb://localhost:27017` | MongoDB connection URI. Connects to Atlas in cloud or MongoDB container locally. Falls back to in-memory store if unreachable. | Yes |
| `DATABASE_NAME` | `string` | `leafguard` | Name of the database for predictions, metrics, and health logs. | No |
| `MODEL_PATH` | `string` | `./app/ml/artifacts/leafguard_model.joblib` | Filesystem path to the trained ML model bundle and label encoder. | No |
| `FRONTEND_URL` | `string` | `http://localhost:5173,http://localhost:3000` | Comma-separated list of allowed CORS origins. Do not include trailing slashes. | Yes |
| `MAX_UPLOAD_SIZE_MB` | `integer` | `10` | Maximum allowable image upload payload size in megabytes. | No |
| `LOG_LEVEL` | `string` | `INFO` | Application logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | No |
| `BACKEND_PORT` | `integer` | `8000` | Port listened to by Uvicorn server in Docker and local execution. | No |

### Production Backend Notes (Render / Cloud)
- **CORS Configuration**: Render requires setting `FRONTEND_URL` to the exact deployed Vercel domain (e.g., `https://leafguard-ai.vercel.app`) without any trailing slash.
- **Resilience**: If `MONGODB_URI` is absent or the database cluster is temporarily unreachable during startup, the application seamlessly switches to an ephemeral in-memory storage driver to prevent 502/boot failures.

---

## 💻 Frontend Configuration

The React frontend utilizes Vite environment variables prefixed with `VITE_`.

| Variable | Type | Default | Description | Required in Production |
|---|---|---|---|:---:|
| `VITE_API_URL` | `string` | `http://localhost:8000` | Base URL of the backend REST API. If empty (`""`), requests use same-origin relative paths. | No |

### Frontend Proxy Mode (Vercel / Rewrites)
When deployed on Vercel with rewrite rules (see `frontend/vercel.json`), setting `VITE_API_URL` to an empty string or leaving it undefined causes API calls to `/api/*` to be proxied automatically to the backend, avoiding cross-site origin and cookie restrictions.

---

## 🔒 Security Best Practices

1. **Never commit `.env` files**: All `.env` and `.env.local` files are ignored by git.
2. **MongoDB Atlas Credentials**: Use dedicated database users with least-privilege access rather than administrative root users.
3. **CORS Origins**: Avoid using `*` wildcard origins in production environments. Explicitly list verified frontend hostnames.
