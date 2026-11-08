import json
from pathlib import Path

import mlflow
from mlflow import MlflowClient


PROJECT_ROOT = Path(__file__).resolve().parent
METADATA_PATH = PROJECT_ROOT / "deployment" / "model_metadata.json"


def get_deployed_run_id():
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Deployment metadata not found: {METADATA_PATH}. "
            "Prepare a deployment bundle first."
        )

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    run_id = metadata.get("run_id")
    if not run_id:
        raise ValueError(f"No run_id found in {METADATA_PATH}.")

    return run_id


client = MlflowClient()

run_id = get_deployed_run_id()

run = client.get_run(run_id)

print("RUN ID:", run.info.run_id)
print("STATUS:", run.info.status)
print("ARTIFACT URI:", run.info.artifact_uri)

print("\nARTIFACTS:")

artifacts = client.list_artifacts(run_id)

for artifact in artifacts:
    print(f"{artifact.path} | is_dir={artifact.is_dir}")

    if artifact.is_dir:
        children = client.list_artifacts(run_id, artifact.path)

        for child in children:
            print(f"  `- {child.path} | is_dir={child.is_dir}")
