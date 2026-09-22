"""Train and evaluate LeafGuard AI models on the processed dataset.

Trains three classical candidates (Logistic Regression, RBF-SVM, Random
Forest) on OpenCV-extracted features, compares them on the validation split,
refits the winner on train+validation and evaluates it ONCE on the test split.
Also runs a preprocessing ablation (same model without denoising/segmentation)
so the README can report measured — not invented — impact.

Outputs:
  backend/app/ml/artifacts/leafguard_model.joblib   (serving bundle)
  ml/models/leafguard_model.joblib                  (backup copy)
  ml/evaluation/metrics.json                        (all real numbers)
  ml/evaluation/classification_report.txt
  ml/evaluation/confusion_matrix.png
  ml/evaluation/model_comparison.png
  ml/evaluation/class_distribution.png

Usage:
    python ml/training/train.py [--fast]
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
import time
from pathlib import Path

import cv2
import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.ml import preprocessing as prep  # noqa: E402  (shared with serving)
from app.ml.labels import display_name  # noqa: E402

SEED = 42
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def load_split(data_dir: Path, split: str) -> tuple[list[Path], list[str]]:
    paths, labels = [], []
    for class_dir in sorted((data_dir / split).iterdir()):
        if not class_dir.is_dir():
            continue
        for image in sorted(class_dir.iterdir()):
            if image.suffix.lower() in IMAGE_EXTS:
                paths.append(image)
                labels.append(display_name(class_dir.name))
    return paths, labels


def featurize(paths: list[Path], use_segmentation: bool, use_denoise: bool) -> np.ndarray:
    features = []
    started = time.perf_counter()
    for i, path in enumerate(paths, 1):
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"Unreadable image skipped list check: {path}")
        features.append(prep.extract_features(image, use_segmentation, use_denoise))
        if i % 250 == 0 or i == len(paths):
            rate = i / max(time.perf_counter() - started, 1e-9)
            print(f"  features {i}/{len(paths)} ({rate:.0f} img/s)", flush=True)
    return np.vstack(features).astype(np.float32)


def build_candidates(fast: bool) -> list[tuple[str, Pipeline, dict]]:
    cv_folds = 2 if fast else 3
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=SEED)

    pca_svm = Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=0.95, random_state=SEED)),
        ("clf", SVC(kernel="rbf", probability=True, random_state=SEED)),
    ])
    svm_grid = (
        {"clf__C": [10], "clf__gamma": ["scale"]} if fast
        else {"clf__C": [10, 100], "clf__gamma": ["scale", 0.001]}
    )

    lr_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=0.95, random_state=SEED)),
        ("clf", LogisticRegression(max_iter=3000, random_state=SEED)),
    ])
    lr_grid = {"clf__C": [1]} if fast else {"clf__C": [0.1, 1, 10]}

    rf_pipe = Pipeline([("scaler", StandardScaler()), ("clf", RandomForestClassifier(random_state=SEED))])
    rf_grid = (
        {"clf__n_estimators": [200], "clf__max_depth": [None]} if fast
        else {"clf__n_estimators": [300], "clf__max_depth": [None, 30], "clf__min_samples_leaf": [1, 3]}
    )

    return [
        ("Logistic Regression", lr_pipe, lr_grid),
        ("SVM (RBF)", pca_svm, svm_grid),
        ("Random Forest", rf_pipe, rf_grid),
    ], cv


def fit_candidate(name: str, pipe: Pipeline, grid: dict, cv, X_train, y_train) -> GridSearchCV:
    search = GridSearchCV(pipe, grid, scoring="f1_macro", cv=cv, n_jobs=-1, refit=True)
    started = time.perf_counter()
    search.fit(X_train, y_train)
    print(f"  {name}: best CV f1_macro={search.best_score_:.4f} "
          f"params={search.best_params_} ({time.perf_counter() - started:.1f}s)", flush=True)
    return search


def evaluate(model, X, y) -> dict:
    y_pred = model.predict(X)
    return {
        "accuracy": round(float(accuracy_score(y, y_pred)), 4),
        "precision_macro": round(float(precision_score(y, y_pred, average="macro", zero_division=0)), 4),
        "recall_macro": round(float(recall_score(y, y_pred, average="macro", zero_division=0)), 4),
        "f1_macro": round(float(f1_score(y, y_pred, average="macro", zero_division=0)), 4),
        "f1_weighted": round(float(f1_score(y, y_pred, average="weighted", zero_division=0)), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "ml" / "dataset" / "processed")
    parser.add_argument("--artifacts", type=Path, default=REPO_ROOT / "backend" / "app" / "ml" / "artifacts")
    parser.add_argument("--reports", type=Path, default=REPO_ROOT / "ml" / "evaluation")
    parser.add_argument("--models", type=Path, default=REPO_ROOT / "ml" / "models")
    parser.add_argument("--fast", action="store_true", help="reduced grids for smoke-testing")
    args = parser.parse_args()

    np.random.seed(SEED)
    for folder in (args.artifacts, args.reports, args.models):
        folder.mkdir(parents=True, exist_ok=True)

    report_path = args.data_dir / "dataset_report.json"
    dataset_report = json.loads(report_path.read_text()) if report_path.exists() else {}

    print("== Loading splits ==", flush=True)
    train_paths, y_train = load_split(args.data_dir, "train")
    val_paths, y_val = load_split(args.data_dir, "validation")
    test_paths, y_test = load_split(args.data_dir, "test")
    print(f"train={len(train_paths)} val={len(val_paths)} test={len(test_paths)}", flush=True)

    print("== Extracting features (full preprocessing) ==", flush=True)
    t0 = time.perf_counter()
    X_train = featurize(train_paths, True, True)
    X_val = featurize(val_paths, True, True)
    X_test = featurize(test_paths, True, True)
    feature_seconds = round(time.perf_counter() - t0, 1)

    print("== Training candidates ==", flush=True)
    candidates, cv = build_candidates(args.fast)
    searches = {}
    val_results = []
    for name, pipe, grid in candidates:
        searches[name] = fit_candidate(name, pipe, grid, cv, X_train, y_train)
        val_metrics = evaluate(searches[name].best_estimator_, X_val, y_val)
        val_results.append({"model": name, "params": searches[name].best_params_,
                            "cv_f1_macro": round(float(searches[name].best_score_), 4), **val_metrics})
        print(f"  {name} validation: {val_metrics}", flush=True)

    best_name = max(val_results, key=lambda r: r["f1_macro"])["model"]
    print(f"== Best model: {best_name} — refitting on train+validation ==", flush=True)
    best_model = copy.deepcopy(searches[best_name].best_estimator_)
    X_trainval = np.vstack([X_train, X_val])
    y_trainval = y_train + y_val
    best_model.fit(X_trainval, y_trainval)

    test_metrics = evaluate(best_model, X_test, y_test)
    y_pred_test = best_model.predict(X_test)
    class_names = sorted(set(y_test))
    report_text = classification_report(y_test, y_pred_test, zero_division=0)
    print(f"== Test metrics ({best_name}): {test_metrics}", flush=True)

    print("== Preprocessing ablation (no denoise / no segmentation) ==", flush=True)
    base_pipe = copy.deepcopy(searches[best_name].best_estimator_)
    base_pipe.fit(
        np.vstack([featurize(train_paths, False, False), featurize(val_paths, False, False)]),
        y_trainval,
    )
    baseline_metrics = evaluate(base_pipe, featurize(test_paths, False, False), y_test)
    print(f"  baseline: {baseline_metrics}", flush=True)

    print("== Latency benchmark (30 images, bytes -> prediction) ==", flush=True)
    rng = np.random.RandomState(SEED)
    sample_idx = rng.choice(len(test_paths), size=min(30, len(test_paths)), replace=False)
    latencies = []
    for idx in sample_idx:
        data = test_paths[int(idx)].read_bytes()
        start = time.perf_counter()
        features = prep.extract_features_from_bytes(data).reshape(1, -1)
        best_model.predict_proba(features)
        latencies.append((time.perf_counter() - start) * 1000)
    latency = {
        "mean_ms": round(float(np.mean(latencies)), 1),
        "p50_ms": round(float(np.percentile(latencies, 50)), 1),
        "p95_ms": round(float(np.percentile(latencies, 95)), 1),
    }
    print(f"  {latency}", flush=True)

    print("== Saving artifacts ==", flush=True)
    bundle = {
        "pipeline": best_model,
        "classes": best_model.classes_.tolist(),
        "feature_config": {
            "version": prep.FEATURE_VERSION,
            "target_size": list(prep.TARGET_SIZE),
            "use_segmentation": True,
            "use_denoise": True,
        },
        "metadata": {
            "model_name": best_name,
            "model_params": {k: str(v) for k, v in searches[best_name].best_params_.items()},
            "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "seed": SEED,
            "dataset": dataset_report,
            "test_metrics": test_metrics,
        },
    }
    artifact_path = args.artifacts / "leafguard_model.joblib"
    joblib.dump(bundle, artifact_path, compress=3)
    shutil.copy2(artifact_path, args.models / "leafguard_model.joblib")
    model_size_mb = round(artifact_path.stat().st_size / (1024 * 1024), 2)

    metrics = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "dataset": {
            "source": "PlantVillage (color) — https://github.com/spMohanty/PlantVillage-Dataset",
            "num_classes": len(set(y_train)),
            "class_names": sorted(set(y_train)),
            "train": len(train_paths), "validation": len(val_paths), "test": len(test_paths),
            "per_class": dataset_report.get("per_class", {}),
        },
        "features": {
            "version": prep.FEATURE_VERSION,
            "dim": int(X_train.shape[1]),
            "extraction_seconds_all_splits": feature_seconds,
        },
        "validation_results": val_results,
        "best_model": best_name,
        "test_metrics": test_metrics,
        "ablation": {
            "full_preprocessing": test_metrics,
            "no_denoise_no_segmentation": baseline_metrics,
            "accuracy_delta": round(test_metrics["accuracy"] - baseline_metrics["accuracy"], 4),
            "f1_macro_delta": round(test_metrics["f1_macro"] - baseline_metrics["f1_macro"], 4),
        },
        "latency": latency,
        "model_size_mb": model_size_mb,
    }
    (args.reports / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (args.reports / "classification_report.txt").write_text(
        f"Model: {best_name}\nTrained on: train+validation, evaluated once on test\n\n{report_text}"
    )

    # ---- Charts ----
    sns.set_theme(style="whitegrid")
    cm = confusion_matrix(y_test, y_pred_test, labels=class_names)
    fig, ax = plt.subplots(figsize=(11, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Greens", xticklabels=class_names,
                yticklabels=class_names, ax=ax)
    ax.set_title(f"Confusion Matrix — {best_name} (test split)")
    ax.set_ylabel("True label")
    ax.set_xlabel("Predicted label")
    plt.xticks(rotation=35, ha="right")
    plt.yticks(rotation=0)
    fig.tight_layout()
    fig.savefig(args.reports / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    vdf = pd.DataFrame(val_results).set_index("model")[["accuracy", "f1_macro"]]
    ax = vdf.plot(kind="bar", figsize=(9, 5.5), rot=0, color=["#34d399", "#059669"])
    ax.set_title("Model comparison (validation split)")
    ax.set_ylim(0, 1)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=9)
    fig = ax.figure
    fig.tight_layout()
    fig.savefig(args.reports / "model_comparison.png", dpi=150)
    plt.close(fig)

    if dataset_report.get("per_class"):
        pdf = pd.DataFrame(dataset_report["per_class"]).T[["train", "validation", "test"]]
        pdf.index = [display_name(i) for i in pdf.index]
        ax = pdf.plot(kind="bar", stacked=True, figsize=(11, 5.5),
                      color=["#059669", "#34d399", "#a7f3d0"])
        ax.set_title("Class distribution after stratified split")
        ax.set_ylabel("images")
        plt.xticks(rotation=35, ha="right")
        fig = ax.figure
        fig.tight_layout()
        fig.savefig(args.reports / "class_distribution.png", dpi=150)
        plt.close(fig)

    print("== TRAINING COMPLETE ==")
    print(json.dumps({
        "best_model": best_name,
        "test_metrics": test_metrics,
        "ablation_accuracy_delta": metrics["ablation"]["accuracy_delta"],
        "latency": latency,
        "model_size_mb": model_size_mb,
        "artifact": str(artifact_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
