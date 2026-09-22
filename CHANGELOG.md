# Changelog

All notable changes to **LeafGuard AI** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `CONTRIBUTING.md` — developer setup, code style and commit conventions.
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1.
- `SECURITY.md` — vulnerability reporting policy.
- `CHANGELOG.md` — this file.

---

## [1.0.0] — 2025-07-01

### Added
- 🖼️ Drag-and-drop image upload with client-side and server-side validation (file type, size,
  magic-byte check, decodability).
- 🧠 Disease prediction across **9 classes** (tomato & potato diseases + healthy) with confidence
  score and top-3 alternate predictions.
- 📋 Curated agronomic knowledge base per disease: description, symptoms, prevention and
  treatment guidance.
- 🕓 Prediction history page with search, filtering by plant/disease, sorting and pagination.
- 📊 Live statistics dashboard: totals, healthy vs diseased ratio, top diseases, per-plant counts.
- 🐳 One-command Docker Compose stack (frontend + FastAPI backend + MongoDB).
- 🔁 Model-service abstraction (`BaseDiseaseModel` ABC) — swap in a CNN without touching the API.
- 🧪 40 automated tests across backend, ML pipeline and frontend.
- 🚀 Free-tier cloud deployment guide (MongoDB Atlas + Render + Vercel).
- ⚙️ GitHub Actions CI for backend tests and frontend build on every push.
- 📐 Render blueprint (`render.yaml`) for one-click backend deployment.

### Changed
- N/A — initial release.

### Fixed
- Confidence score display on mobile history cards.
- Vercel rewrite rules to proxy API calls through the same origin.
- `dnspython` added to requirements to support `mongodb+srv://` Atlas connection strings.
- Docker image respects `PORT` environment variable injected by PaaS providers.

---

[Unreleased]: https://github.com/Gangadhar017/LeaveGuard-AI/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Gangadhar017/LeaveGuard-AI/releases/tag/v1.0.0
