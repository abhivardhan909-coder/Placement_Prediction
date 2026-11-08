import json
import os
from pathlib import Path

import mlflow
import yaml
from mlflow.tracking import MlflowClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def generate_registry_report() -> Path:
    config_path = PROJECT_ROOT / "config.yaml"
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI") or config["mlflow"].get("tracking_uri")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    model_name = config["registry"]["model_name"]
    client = MlflowClient()
    versions = client.search_model_versions(f"name='{model_name}'")
    production_models = [version for version in versions if version.current_stage == "Production"]
    if len(production_models) != 1:
        raise RuntimeError(
            f"Expected exactly one Production model named {model_name}; found {len(production_models)}."
        )

    champion = production_models[0]
    run = client.get_run(champion.run_id)
    report = {
        "registry_status": "READY_FOR_DEPLOYMENT",
        "model_lineage": {
            "registered_name": model_name,
            "version": int(champion.version),
            "current_stage": champion.current_stage,
            "run_id": champion.run_id,
            "artifact_uri": champion.source,
        },
        "performance_metrics": run.data.metrics,
        "hyperparameters": run.data.params,
        "preprocessing_dependency": "deployment/preprocessor.pkl",
        "target_column": config["data"]["target_column"],
        "positive_class": "Placed",
    }

    report_path = PROJECT_ROOT / "artifacts" / "production_model_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
    print(f"[SUCCESS] Placement registry report saved to {report_path}.")
    return report_path


if __name__ == "__main__":
    generate_registry_report()
