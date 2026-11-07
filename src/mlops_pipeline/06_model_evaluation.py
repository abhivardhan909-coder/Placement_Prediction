import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np
import yaml
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def run_evaluation():
    print("[INFO] Starting ML Pipeline Model Evaluation...")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    model_path = PROJECT_ROOT / config["paths"]["model"]
    processed_dir = PROJECT_ROOT / config["data"]["processed_dir"]

    if not model_path.exists():
        print(f"[ERROR] Model not found at {model_path}. Run 05_train_registry_mlops.py first.")
        return False

    try:
        X_test = np.load(processed_dir / "X_test_final.npy")
        y_test = np.load(processed_dir / "y_test.npy")
    except FileNotFoundError:
        print("[ERROR] Test data not found. Run 03_preprocessing_mlops.py first.")
        return False

    model = joblib.load(model_path)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }

    print("\n--- ML Pipeline: Model Evaluation ---")
    for name, value in metrics.items():
        print(f"{name.replace('_', ' ').title():10}: {value:.4f}")
    print(f"Confusion Matrix:\n{cm}")
    print("--------------------------------\n")

    report = {
        "stage": "ML Pipeline - Model Evaluation",
        "evaluated_on": "held-out test split",
        "test_rows": int(len(y_test)),
        "metrics": {name: round(float(value), 4) for name, value in metrics.items()},
        "confusion_matrix": cm.tolist(),
    }

    report_path = PROJECT_ROOT / config["paths"]["evaluation_report"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(f"[SUCCESS] Evaluation report saved to {report_path}")
    return True


if __name__ == "__main__":
    passed = run_evaluation()
    sys.exit(0 if passed else 1)
