# Machine Learning Pipeline

This document details the Machine Learning pipeline, dataset preparation, feature engineering, and model training workflow for **LeafGuard AI**.

---

## 🌿 Dataset Overview

LeafGuard AI utilizes the **PlantVillage (color)** dataset focused on Solanaceae crops (Potatoes and Tomatoes):

- **Total Classes**: 9 disease and healthy categories:
  - `Potato___Early_blight`
  - `Potato___Late_blight`
  - `Potato___healthy`
  - `Tomato___Bacterial_spot`
  - `Tomato___Early_blight`
  - `Tomato___Late_blight`
  - `Tomato___Leaf_Mold`
  - `Tomato___Septoria_leaf_spot`
  - `Tomato___healthy`
- **Split Distribution**:
  - **Training**: 70% (~1,898 images)
  - **Validation**: 15% (~407 images)
  - **Testing**: 15% (~407 images)

---

## 🔬 Feature Engineering & Computer Vision

Rather than heavy neural networks requiring GPUs in production, LeafGuard AI uses lightweight, interpretable, deterministic computer vision features extracted using **OpenCV**:

1. **Color Spaces**:
   - Extraction of color histograms across RGB, HSV, and Lab color spaces to capture discoloration and chlorosis.
2. **Texture Analysis**:
   - Haralick texture features computed from Gray-Level Co-occurrence Matrices (GLCM) detecting surface roughness and lesion patterns.
3. **Shape & Contour Descriptors**:
   - Hu Moments capturing geometric contour deformations in diseased spots.
4. **Segmentation & Denoising**:
   - Bilateral filtering and Otsu thresholding to segment leaf tissue from background artifacts.

---

## 🤖 Candidate Models & Selection

Three classical machine learning architectures are trained and benchmarked:

| Model | Characteristic | Hyperparameters |
|---|---|---|
| **Random Forest** | Non-linear ensemble, robust to outliers | `n_estimators=100`, `max_depth=None`, `class_weight='balanced'` |
| **RBF SVM** | High-dimensional margin maximization | `kernel='rbf'`, `C=10.0`, `gamma='scale'` |
| **Logistic Regression** | Baseline linear model | `C=1.0`, `max_iter=1000`, `solver='lbfgs'` |

The best model is selected based on validation macro F1-score, refitted on the combined training and validation sets, and evaluated once on the holdout test set.

---

## 📦 Artifact Packaging

The final production bundle is exported as a serialized joblib archive:

```
backend/app/ml/artifacts/leafguard_model.joblib
```

The bundle contains:
- `model`: Trained scikit-learn classifier pipeline
- `feature_extractor`: Parameterized OpenCV feature extraction pipeline
- `label_encoder`: Mapping between numerical prediction indices and human-readable disease classes
- `metadata`: Training timestamp, dataset hash, and validation metrics

---

## 🔁 Reproducing the Training Pipeline

To download the dataset and execute the training pipeline locally:

```bash
# 1. Download and preprocess images
python ml/scripts/download_dataset.py
python ml/scripts/prepare_dataset.py

# 2. Run model training and evaluation
python ml/training/train.py

# Optional: Run in fast mode for testing pipeline integrity
python ml/training/train.py --fast
```
