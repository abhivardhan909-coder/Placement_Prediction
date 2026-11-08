import os
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def configure_mlflow(config):
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI") or config["mlflow"].get("tracking_uri")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)


def train_and_register_model():
    print("[INFO] --- Starting MLflow Run with Model Registry ---")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    configure_mlflow(config)
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    processed_dir = PROJECT_ROOT / config["data"]["processed_dir"]

    try:
        X_train = np.load(processed_dir / "X_train_final.npy")
        X_test = np.load(processed_dir / "X_test_final.npy")
        y_train = np.load(processed_dir / "y_train.npy")
        y_test = np.load(processed_dir / "y_test.npy")
    except FileNotFoundError:
        print("[ERROR] Processed data not found. Please run 03_preprocessing.py first.")
        return False

    model_cfg = config["model"]

    params = {
        "n_estimators": model_cfg["n_estimators"],
        "max_depth": model_cfg["max_depth"],
        "random_state": model_cfg["random_state"],
        "class_weight": model_cfg["class_weight"],
    }

    with mlflow.start_run(run_name="RandomForest") as run:
        mlflow.log_params(params)
        mlflow.log_param("model_family", "RandomForest")
        mlflow.log_param("lab", "ML Pipeline")

        if os.getenv("GITHUB_RUN_ID"):
            mlflow.log_param("github_run_id", os.getenv("GITHUB_RUN_ID"))
        if os.getenv("GITHUB_SHA"):
            mlflow.log_param("github_commit", os.getenv("GITHUB_SHA"))

        print("[INFO] Training RandomForest model...")
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        print("[INFO] Evaluating model on the held-out test set...")
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }

        mlflow.log_metrics(metrics)

        model_path = PROJECT_ROOT / config["paths"]["model"]
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)

        preprocessor_path = PROJECT_ROOT / config["paths"]["preprocessor"]
        if preprocessor_path.exists():
            mlflow.log_artifact(str(preprocessor_path), artifact_path="preprocessing_pipeline")

        print("[INFO] Pushing model to MLflow Registry...")
        mlflow.sklearn.log_model(
            sk_model=model,
            name="random_forest_model",
            registered_model_name=config["registry"]["model_name"],
            # This stage creates the RandomForest itself, so its internal
            # scikit-learn tree storage is a reviewed, trusted type.
            skops_trusted_types=["sklearn.tree._tree.Tree"],
        )

        print(
            f"[SUCCESS] Accuracy={metrics['accuracy']:.4f} | "
            f"Recall={metrics['recall']:.4f} | "
            f"F1={metrics['f1_score']:.4f} | "
            f"ROC-AUC={metrics['roc_auc']:.4f}"
        )
        print(f"[SUCCESS] Model saved to {model_path}")
        print(f"[SUCCESS] Model registered as '{config['registry']['model_name']}'")
        print(f"[INFO] MLflow Run ID: {run.info.run_id}")

    return True


if __name__ == "__main__":
    passed = train_and_register_model()
    sys.exit(0 if passed else 1)
