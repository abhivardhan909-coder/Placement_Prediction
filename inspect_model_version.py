import os
from pathlib import Path

import mlflow
import yaml
from mlflow import MlflowClient


PROJECT_ROOT = Path(__file__).resolve().parent
with (PROJECT_ROOT / "config.yaml").open("r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

tracking_uri = os.getenv("MLFLOW_TRACKING_URI") or config["mlflow"].get("tracking_uri")
if tracking_uri:
    mlflow.set_tracking_uri(tracking_uri)

model_name = config["registry"]["model_name"]
client = MlflowClient()
versions = client.search_model_versions(f"name='{model_name}'")
production = [version for version in versions if version.current_stage == "Production"]
if len(production) != 1:
    raise RuntimeError(f"Expected one Production version for {model_name}, found {len(production)}.")

model_version = production[0]
print("MODEL NAME:", model_version.name)
print("VERSION:", model_version.version)
print("STAGE:", model_version.current_stage)
print("RUN ID:", model_version.run_id)
print("SOURCE:", model_version.source)
print("STATUS:", model_version.status)
print("CREATION TIMESTAMP:", model_version.creation_timestamp)
