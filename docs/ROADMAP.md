# Product & Technical Roadmap

This roadmap outlines key milestones and anticipated feature improvements for **LeafGuard AI**.

---

## 🎯 Current Milestone: v1.0.0 (Foundation) ✅

- [x] Dual-stack deployment on Render (Docker backend) and Vercel (React frontend)
- [x] Classical computer vision + ML classifier with 9 PlantVillage classes
- [x] MongoDB Atlas database with automatic fallback to in-memory store
- [x] Real-time inference endpoint (`/api/predict`) with latency metrics
- [x] Historical prediction logging and searchable dashboard
- [x] Responsive web interface with drag-and-drop file upload

---

## 🚀 Near-Term Milestone: v1.1.0 (Q4 2026)

### 🌾 Extended Crop Support
- Expand disease detection support to additional commercial crops:
  - Apple (`Apple Scab`, `Black Rot`, `Cedar Apple Rust`)
  - Grape (`Black Rot`, `Esca`, `Leaf Blight`)
  - Corn/Maize (`Common Rust`, `Northern Leaf Blight`, `Gray Leaf Spot`)

### 📱 Progressive Web App (PWA) & Offline Mode
- Service worker caching for application shell
- Local offline queuing of captured photos for automatic sync once network connectivity resumes
- Mobile camera capture enhancements (guides, brightness normalization)

### 📊 Enhanced Analytics Dashboard
- Crop health trends over time with geographical grouping
- Export analysis reports in PDF and CSV formats
- Batch image upload for field inspections

---

## 🔮 Long-Term Milestone: v2.0.0 (2027)

### 🧠 Edge AI & On-Device Inference
- Quantized ONNX / TensorFlow Lite model export for in-browser client-side inference via WebAssembly/WebGPU
- Sub-50ms inference without cloud round-trip
- Hybrid edge-cloud validation for high-confidence confirmations

### 🔔 Alerting & Proactive Advisory
- Weather API integration to correlate localized humidity/rainfall with blight outbreak risks
- Push notifications for proactive treatment windows
- Multi-lingual UI localization (Hindi, Spanish, French, Swahili)
