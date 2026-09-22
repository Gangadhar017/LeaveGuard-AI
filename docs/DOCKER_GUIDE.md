# Docker & Containerization Guide

This guide describes how to run, build, and troubleshoot **LeafGuard AI** using Docker and Docker Compose.

---

## 🏗 Architecture Overview

The containerized stack consists of three services managed by `docker-compose.yml`:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│  React Frontend │ ────> │ FastAPI Backend │ ────> │  MongoDB Server │
│ (Nginx :3000)   │       │ (Uvicorn :8000) │       │ (Mongo 7 :27017)│
│                 │       │                 │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   │
                                   ▼
                            Local Model Bundle
                        (joblib / sklearn pipeline)
```

1. **`mongodb`**: Official MongoDB 7 image with healthcheck probing `mongosh` ping. Data is persisted in the `mongo_data` named volume.
2. **`backend`**: Python 3.12 slim image with OpenCV headless dependencies and FastAPI/Uvicorn runtime.
3. **`frontend`**: Multi-stage build (Node 20 build stage compiles Vite assets, Nginx Alpine stage serves static files and routes SPAs).

---

## 🚀 Quickstart

### 1. Build and Start All Containers

```bash
docker compose up -d --build
```

### 2. Verify Services

- **Frontend App**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/health>

### 3. View Logs

```bash
# Stream logs for all services
docker compose logs -f

# Stream logs for backend only
docker compose logs -f backend
```

### 4. Stop All Services

```bash
docker compose down
```

To also remove persisted database volumes:
```bash
docker compose down -v
```

---

## 🔍 Individual Image Builds

### Backend Container

Build and run standalone:

```bash
docker build -t leafguard-backend ./backend
docker run -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017 \
  -e FRONTEND_URL=http://localhost:3000 \
  leafguard-backend
```

### Frontend Container

Build and run standalone:

```bash
docker build -t leafguard-frontend ./frontend
docker run -p 3000:80 leafguard-frontend
```

---

## 🛠 Useful Troubleshooting Commands

| Command | Purpose |
|---|---|
| `docker compose ps` | Check running container status and health states |
| `docker compose top` | Inspect processes running inside each container |
| `docker compose exec backend bash` | Open an interactive terminal in the backend container |
| `docker compose exec mongodb mongosh` | Inspect database documents and collections directly |
| `docker system prune -f` | Free disk space by cleaning unused builder caches |
