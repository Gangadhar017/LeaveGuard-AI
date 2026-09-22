# 🚀 Deploying LeafGuard AI (free tier)

This stack runs publicly for **$0/month**:

| Piece | Service | Free tier notes |
|---|---|---|
| Database | [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) M0 | 512 MB, no card required |
| Backend API | [Render](https://render.com) web service (Docker) | Sleeps after ~15 min idle; cold start ≈ 50 s |
| Frontend | [Vercel](https://vercel.com) (Vite preset) | Recieves all traffic; instant |

Total time: **~30 minutes**, mostly waiting for the first Docker build on Render.

---

## 1. MongoDB Atlas (database)

1. Create a free account at <https://www.mongodb.com/cloud/atlas> → **Build a Database** → choose **M0 FREE**.
2. Pick any region close to you → **Create**.
3. **Database Access** (left sidebar) → *Add New Database User* →
   - username: `leafguard`, password: generate one and **save it** (no special characters avoids URL-escaping pain)
   - role: *Read and write to any database*
4. **Network Access** → *Add IP Address* → **Allow access from anywhere** (`0.0.0.0/0`) — required because Render's egress IPs are dynamic.
5. **Database → Connect → Drivers** → copy the connection string, e.g.
   ```
   mongodb+srv://leafguard:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   Replace `<password>` with the real password.

## 2. Render (backend API)

1. Sign in at <https://dashboard.render.com> **with GitHub** and authorize access to the `LifeGuard-AI` repository.
2. **New +** → **Blueprint** → select the `Gangadhar017/LifeGuard-AI` repo → **Apply**.
   Render reads the [`render.yaml`](render.yaml) blueprint and creates a Docker web service from `backend/`.
3. When prompted for the two `sync: false` variables, fill them in:
   - `MONGODB_URI` → the Atlas connection string from step 1
   - `FRONTEND_URL` → temporarily `https://localhost:5173` (you will update it after Vercel gives you a URL)
4. **Create Resources**. The first build takes ~10 minutes (installs OpenCV + scikit-learn into the image).
5. When it goes live, verify: open `https://leafguard-api-XXXX.onrender.com/health` →
   ```json
   {"status":"ok","model_loaded":true,"database":"mongodb",...}
   ```
   **Note your backend URL** — you need it in step 3.

## 3. Vercel (frontend)

1. Sign in at <https://vercel.com> **with GitHub** → **Add New… → Project** → import `LifeGuard-AI`.
2. Configure:
   - **Framework Preset:** Vite (auto-detected)
   - **Root Directory:** `frontend`  ← important, the React app lives in a subfolder
   - **Environment Variables:** none required — `frontend/vercel.json` already proxies
     `/api`, `/health` and `/docs` to the Render backend in **same-origin mode**
     (update the rewrite destination there if your Render URL differs), and the
     client treats an empty `VITE_API_URL` as same-origin.
3. **Deploy** — done in ~1 minute. Note your frontend URL, e.g. `https://life-guard-ai.vercel.app`.

## 4. Wire the last screw (CORS)

1. Back in **Render → your service → Environment**:
   - `FRONTEND_URL` = `https://life-guard-ai.vercel.app` (your Vercel URL)
2. **Save & Deploy** (takes ~2 min — it reuses the build cache).

## 5. Verify the deployed product

1. Open your Vercel URL → **Predict** → upload a leaf photo → you should get a prediction with confidence.
2. Check **History** and **Dashboard** show the stored prediction (Atlas-backed).
3. API docs are at `https://<render-url>/docs`.

---

## Notes & gotchas

- **Cold starts**: Render's free tier spins the API down after ~15 min idle. The first request after
  that takes ~50 s (the browser will look stuck on "Analyzing…") — it wakes up on its own.
  Upgrade to Render Starter ($7/mo) if you want it always-on.
- **CORS**: the backend only allows origins listed in `FRONTEND_URL` (comma-separated), so the
  Vercel URL must match exactly (no trailing slash).
- **Alternate setups**: anything that runs Docker works for the backend (Fly.io, Railway, Koyeb,
  AWS App Runner, Cloud Run). For the frontend, Netlify is a drop-in Vercel replacement.
  For same-origin proxying instead of CORS, add a rewrite rule (`/api/*` → backend) on the
  frontend host and set `VITE_API_URL` to an empty string — the client supports that mode.
- **Local vs cloud**: `docker compose up` still runs the whole stack locally with the same images.
