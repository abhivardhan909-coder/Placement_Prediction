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
model = client.get_registered_model(model_name)
print(f"MODEL: {model.name}")
print("VERSIONS:")
for version in client.search_model_versions(f"name='{model_name}'"):
    print(
        f"version={version.version} "
        f"stage={version.current_stage} "
        f"run_id={version.run_id}"
    )
