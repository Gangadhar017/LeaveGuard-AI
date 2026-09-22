# LeafGuard AI — Troubleshooting & FAQ

This guide helps resolve common issues encountered during local development, deployment, or testing.

---

## 1. Backend Issues

### MongoDB Connection Failed
**Symptom:**
```
pymongo.errors.ServerSelectionTimeoutError: No servers found yet
```
**Solution:**
- Ensure MongoDB service is running locally (`mongod` or Docker container).
- Check `MONGO_URI` in `.env`.
- If using MongoDB Atlas, verify your IP address is whitelisted in Atlas Network Access settings and that `dnspython` is installed (`pip install dnspython`).
- If MongoDB is unavailable, the backend automatically falls back to `InMemoryRepository` for transient local testing.

### Import Error / Missing Module
**Symptom:**
```
ModuleNotFoundError: No module named 'cv2'
```
**Solution:**
- Make sure virtual environment is activated.
- Run `pip install -r requirements.txt`.
- For OpenCV on Linux headless environments, ensure `opencv-python-headless` is used instead of `opencv-python`.

---

## 2. Frontend Issues

### CORS / API Network Errors
**Symptom:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/predictions' from origin 'http://localhost:5173' has been blocked by CORS policy.
```
**Solution:**
- Ensure backend `CORS_ORIGINS` in environment variables includes `http://localhost:5173`.
- If using Vite proxy or Vercel rewrites, ensure request path starts with `/api/v1`.

### Build Failures with Tailwind CSS
**Symptom:**
```
[vite:css] Unexpected token / missing utility class
```
**Solution:**
- Clear Vite cache: `rm -rf node_modules/.vite`.
- Reinstall dependencies: `npm ci`.

---

## 3. Docker Compose Issues

### Port Already in Use
**Symptom:**
```
Error response from daemon: driver failed programming external connectivity on endpoint: Bind for 0.0.0.0:8000 failed: port is already allocated
```
**Solution:**
- Check running services on port 8000 (`lsof -i :8000` or `netstat -ano | findstr 8000`).
- Stop conflicting process or change port binding in `docker-compose.yml`.

---

## 4. ML Pipeline Issues

### Missing Model Artifact
**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ml/artifacts/model_bundle.joblib'
```
**Solution:**
- Run training script to generate the joblib model bundle:
  ```bash
  cd ml
  python training/train.py
  ```
- Alternatively, check out `ml/artifacts/` where pre-trained outputs are committed.
