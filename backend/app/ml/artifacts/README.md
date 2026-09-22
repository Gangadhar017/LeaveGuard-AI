# ML Model Artifacts

`leafguard_model.joblib` is produced by the training pipeline and **is committed**
(~4.5 MB) so the backend and Docker stack run out of the box — no training step
required.

To retrain from scratch (and regenerate every metric and chart):

```bash
python ml/scripts/download_dataset.py
python ml/scripts/prepare_dataset.py
python ml/training/train.py
```

If the artifact is missing, the API starts in a degraded state:
`GET /health` reports `model_loaded: false` and `/api/v1/predict` returns
`503 MODEL_NOT_LOADED`.
